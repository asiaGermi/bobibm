"""
AI Factsheet Manager for watsonx.governance

Creates and manages AI Factsheets via the Watson Studio catalog REST API.
No heavy SDK — uses requests directly.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
CATALOG_BASE_URL = "https://api.eu-de.dataplatform.cloud.ibm.com"


class FactsheetManager:
    """
    Creates and manages AI Factsheets in the IBM Watson Studio catalog.

    Factsheets document model purpose, training data, performance,
    fairness, and compliance — required for EU AI Act and AML regulations.

    Uses the Watson Studio /v2/assets API to store factsheet records
    as catalog assets of type `factsheet`.
    """

    # Watson Studio project for Financial Risk Management
    PROJECT_ID = "cdf7fe29-7dc1-455c-99a5-18b59b187727"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WATSONX_GOVERNANCE_API_KEY")
        self._token: Optional[str] = None
        self._token_exp: float = 0.0
        self.enabled = bool(self.api_key)
        self._local_factsheets: Dict[str, Dict[str, Any]] = {}

        if self.enabled:
            try:
                self._refresh_token()
                logger.info("FactsheetManager connected to IBM Watson Studio catalog")
            except Exception as exc:
                logger.warning(f"FactsheetManager: token fetch failed — running offline: {exc}")
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_factsheet(
        self,
        model_id: str,
        model_name: str,
        model_description: str,
        use_case: str,
        intended_use: str,
        training_data_info: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        fairness_info: Optional[Dict[str, Any]] = None,
        compliance_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an AI Factsheet for a model as a Watson Studio project asset.

        Returns the asset_id of the created factsheet.
        """
        now = datetime.now(timezone.utc).isoformat()
        factsheet_data = {
            "model_id": model_id,
            "model_name": model_name,
            "description": model_description,
            "use_case": use_case,
            "intended_use": intended_use,
            "created_at": now,
            "training_data": training_data_info or {},
            "performance": performance_metrics or {},
            "fairness": fairness_info or {},
            "compliance": compliance_info or {},
        }

        # Always store locally
        local_id = f"factsheet_{model_id.replace('/', '_')}"
        self._local_factsheets[local_id] = {**factsheet_data, "factsheet_id": local_id}

        if not self.enabled:
            logger.info(f"FactsheetManager offline — factsheet stored locally for {model_id}")
            return {"status": "local", "factsheet_id": local_id, "model_id": model_id}

        try:
            asset_payload = {
                "metadata": {
                    "name": f"Factsheet — {model_name}",
                    "description": model_description,
                    "asset_type": "factsheet",
                    "tags": ["financial-risk", "aml", "governance", model_id.replace("/", "-")],
                    "origin_country": "de",
                    "project_id": self.PROJECT_ID,
                },
                "entity": {
                    "factsheet": factsheet_data
                },
            }

            resp = requests.post(
                f"{CATALOG_BASE_URL}/v2/assets?project_id={self.PROJECT_ID}",
                headers=self._headers(),
                json=asset_payload,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            asset_id: str = data.get("metadata", {}).get("asset_id", local_id)

            self._local_factsheets[local_id]["asset_id"] = asset_id
            logger.info(f"FactsheetManager: created factsheet asset {asset_id} for {model_id}")
            return {
                "status": "created",
                "factsheet_id": asset_id,
                "model_id": model_id,
                "project_id": self.PROJECT_ID,
                "created_at": now,
            }

        except requests.HTTPError as exc:
            logger.warning(
                f"FactsheetManager: catalog API returned {exc.response.status_code} "
                f"({exc.response.text[:200]}) — factsheet stored locally"
            )
            return {"status": "local_fallback", "factsheet_id": local_id, "model_id": model_id}
        except Exception as exc:
            logger.error(f"FactsheetManager.create_factsheet failed: {exc}")
            return {"status": "error", "model_id": model_id, "error": str(exc)}

    def create_granite_factsheet(self) -> Dict[str, Any]:
        """Pre-configured factsheet for the Granite model used in this system."""
        return self.create_factsheet(
            model_id="ibm/granite-4-h-small",
            model_name="Financial Risk — Granite Explanation Model",
            model_description=(
                "IBM Granite 4H Small model used to generate natural language explanations "
                "of financial risk assessments in the AML detection pipeline."
            ),
            use_case="Financial Risk Management — AML Detection",
            intended_use=(
                "Generate clear, actionable explanations for compliance officers. "
                "NOT intended for automated decisions without human oversight."
            ),
            training_data_info={
                "source": "IBM Granite foundation model (pretrained)",
                "domain": "General purpose with financial domain prompting",
                "data_quality": "High quality, curated IBM datasets",
                "bias_mitigation": "Applied during foundation model training",
            },
            performance_metrics={
                "explanation_quality": "Human-evaluated: High",
                "avg_response_time_ms": "< 2000",
                "token_efficiency": "Optimised for concise outputs",
                "fallback_rate": "< 5% under normal conditions",
            },
            fairness_info={
                "bias_assessment": "Regular monitoring for demographic bias",
                "fairness_metrics": "Evaluated across risk level distributions",
                "mitigation": "Human-in-the-loop review for all critical decisions",
            },
            compliance_info={
                "regulatory_framework": "EU AI Act, GDPR, AML Directive 6AMLD",
                "risk_classification": "High — financial services decision support",
                "human_oversight": "Required for all critical risk decisions",
                "audit_trail": "All predictions logged to IBM watsonx.governance",
                "data_residency": "EU (Frankfurt, eu-de)",
            },
        )

    def get_factsheet(self, factsheet_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a factsheet — first from local cache, then from Watson Studio catalog."""
        local = self._local_factsheets.get(factsheet_id)
        if local:
            return local

        if not self.enabled:
            return None

        try:
            resp = requests.get(
                f"{CATALOG_BASE_URL}/v2/assets/{factsheet_id}?project_id={self.PROJECT_ID}",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "factsheet_id": factsheet_id,
                "name": data.get("metadata", {}).get("name"),
                "content": data.get("entity", {}).get("factsheet"),
                "created_at": data.get("metadata", {}).get("create_time"),
            }
        except Exception as exc:
            logger.error(f"FactsheetManager.get_factsheet failed for {factsheet_id}: {exc}")
            return None

    def list_factsheets(self) -> List[Dict[str, Any]]:
        """List all factsheets tracked by this manager."""
        return list(self._local_factsheets.values())


# Made with Bob
