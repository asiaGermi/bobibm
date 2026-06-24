"""
Model Registry for watsonx.governance

Registers and tracks AI models via the Watson OpenScale REST API.
No heavy SDK — uses requests directly.
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
GOVERNANCE_BASE_URL = "https://eu-de.aiopenscale.cloud.ibm.com"


class ModelRegistry:
    """
    Registers and tracks AI models in IBM watsonx.governance.

    Maps model concepts to OpenScale service_providers + subscriptions:
    - register_model()  → ensure service provider + subscription exist
    - get_model_info()  → GET subscription from governance
    - update_model_metadata() → not directly supported by OpenScale;
                                stored locally and logged
    """

    INSTANCE_ID = "bc2c304b-0513-4bad-832c-6ecf916274af"
    SERVICE_PROVIDER_ID = "019ef968-e043-70bd-8fa1-5bfc88a05cb4"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WATSONX_GOVERNANCE_API_KEY")
        self._token: Optional[str] = None
        self._token_exp: float = 0.0
        self.enabled = bool(self.api_key)
        self._model_cache: Dict[str, Dict[str, Any]] = {}

        if self.enabled:
            try:
                self._refresh_token()
                logger.info("ModelRegistry connected to IBM watsonx.governance")
            except Exception as exc:
                logger.warning(f"ModelRegistry: token fetch failed — running offline: {exc}")
                self.enabled = False

    # ------------------------------------------------------------------
    # Token
    # ------------------------------------------------------------------

    def _refresh_token(self) -> str:
        resp = requests.post(
            IAM_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.api_key}",
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        token: str = data["access_token"]
        self._token = token
        self._token_exp = time.time() + data.get("expires_in", 3600) - 120
        return token

    def _get_token(self) -> str:
        if not self._token or time.time() >= self._token_exp:
            return self._refresh_token()
        return self._token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def _base(self) -> str:
        return f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}/v2"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_type: str = "custom",
        provider: str = "IBM",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a model in watsonx.governance.

        Checks if a subscription already exists for this model_id;
        creates one if not. Returns the subscription details.
        """
        if not self.enabled:
            return {"status": "offline", "model_id": model_id}

        try:
            # Check existing subscriptions
            existing = self._find_subscription(model_id)
            if existing:
                logger.info(f"ModelRegistry: model {model_id} already registered as {existing['id']}")
                entry = {
                    "status": "already_registered",
                    "model_id": model_id,
                    "subscription_id": existing["id"],
                    "governance_url": f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}/v2/subscriptions/{existing['id']}",
                }
                self._model_cache[model_id] = entry
                return entry

            # Create new subscription
            asset_id = f"{model_id.replace('/', '-')}-{int(time.time())}"
            payload = {
                "data_mart_id": self.INSTANCE_ID,
                "service_provider_id": self.SERVICE_PROVIDER_ID,
                "asset": {
                    "asset_id": asset_id,
                    "name": model_name,
                    "asset_type": "model",
                    "asset_properties": {
                        "model_type": model_type,
                        "runtime_environment": "Python 3.11",
                        "input_data_type": "structured",
                        "description": description or f"{model_name} — {provider}",
                    },
                },
                "deployment": {
                    "deployment_id": f"{asset_id}-deployment",
                    "name": f"{model_name} deployment",
                    "deployment_type": "online",
                    "url": "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud",
                },
            }
            resp = requests.post(
                f"{self._base()}/subscriptions",
                headers=self._headers(),
                json=payload,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            sub_id: str = data.get("metadata", {}).get("id", "unknown")

            entry = {
                "status": "registered",
                "model_id": model_id,
                "model_name": model_name,
                "provider": provider,
                "subscription_id": sub_id,
                "governance_url": f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}/v2/subscriptions/{sub_id}",
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
            }
            self._model_cache[model_id] = entry
            logger.info(f"ModelRegistry: registered {model_id} → subscription {sub_id}")
            return entry

        except Exception as exc:
            logger.error(f"ModelRegistry.register_model failed for {model_id}: {exc}")
            return {"status": "error", "model_id": model_id, "error": str(exc)}

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve model info from watsonx.governance (subscription details)."""
        if not self.enabled:
            return self._model_cache.get(model_id)

        try:
            sub = self._find_subscription(model_id)
            if not sub:
                return self._model_cache.get(model_id)

            sub_id = sub["id"]
            resp = requests.get(
                f"{self._base()}/subscriptions/{sub_id}",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "model_id": model_id,
                "subscription_id": sub_id,
                "status": data.get("entity", {}).get("status", {}).get("state"),
                "deployment_name": data.get("entity", {}).get("deployment", {}).get("name"),
                "created_at": data.get("metadata", {}).get("created_at"),
                "governance_url": f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}/v2/subscriptions/{sub_id}",
            }
        except Exception as exc:
            logger.error(f"ModelRegistry.get_model_info failed for {model_id}: {exc}")
            return None

    def list_registered_models(self) -> Dict[str, Any]:
        """List all subscriptions in watsonx.governance."""
        if not self.enabled:
            return {"models": list(self._model_cache.values()), "source": "local_cache"}

        try:
            resp = requests.get(
                f"{self._base()}/subscriptions",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            subs = data.get("subscriptions", [])
            return {
                "models": [
                    {
                        "subscription_id": s.get("metadata", {}).get("id"),
                        "asset_name": s.get("entity", {}).get("asset", {}).get("name"),
                        "asset_id": s.get("entity", {}).get("asset", {}).get("asset_id"),
                        "status": s.get("entity", {}).get("status", {}).get("state"),
                        "created_at": s.get("metadata", {}).get("created_at"),
                    }
                    for s in subs
                ],
                "total": len(subs),
                "source": "watsonx_governance",
            }
        except Exception as exc:
            logger.error(f"ModelRegistry.list_registered_models failed: {exc}")
            return {"models": [], "error": str(exc)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_subscription(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Find a subscription whose asset_id or asset_name matches model_id."""
        try:
            resp = requests.get(
                f"{self._base()}/subscriptions",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            for sub in resp.json().get("subscriptions", []):
                asset = sub.get("entity", {}).get("asset", {})
                if asset.get("asset_id", "").startswith(model_id.replace("/", "-")) or \
                   model_id in asset.get("name", ""):
                    return sub.get("metadata", {})
        except Exception as exc:
            logger.warning(f"_find_subscription error: {exc}")
        return None


# Made with Bob
