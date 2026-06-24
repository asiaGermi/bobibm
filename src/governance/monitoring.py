"""
Governance Monitoring for watsonx.governance (IBM OpenScale)

Logs predictions to IBM watsonx.governance for audit, compliance, and model monitoring.
Uses direct REST API calls — no heavy SDK required.
"""

import os
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
GOVERNANCE_BASE_URL = "https://eu-de.aiopenscale.cloud.ibm.com"


class GovernanceMonitor:
    """
    Logs AI model predictions to IBM watsonx.governance for compliance and audit.

    On init it obtains an IAM token from the personal API key and caches it.
    Each log_* call sends a payload record to the governance data set.
    Falls back to local in-memory logging if governance is unreachable.
    """

    INSTANCE_ID = "bc2c304b-0513-4bad-832c-6ecf916274af"
    SUBSCRIPTION_ID = "019ef96a-44d2-7ebf-85e4-c9c53923009e"
    DATASET_ID = "019ef96a-4884-7ded-8911-4b3219e64327"
    DEPLOYMENT_ID = "frm-deployment-v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WATSONX_GOVERNANCE_API_KEY")
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self.enabled = bool(self.api_key)
        self._local_log: List[Dict[str, Any]] = []

        if self.enabled:
            try:
                self._refresh_token()
                logger.info("GovernanceMonitor connected to IBM watsonx.governance")
            except Exception as exc:
                logger.warning(f"GovernanceMonitor: token fetch failed, falling back to local log: {exc}")
                self.enabled = False
        else:
            logger.info("GovernanceMonitor: no API key — running in local-only mode")

    # ------------------------------------------------------------------
    # Token management
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
        import time
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 120
        return token

    def _get_token(self) -> str:
        import time
        if not self._token or time.time() >= self._token_expires_at:
            return self._refresh_token()
        return self._token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Core payload logging
    # ------------------------------------------------------------------

    def _log_to_governance(self, record: Dict[str, Any]) -> bool:
        """Send one record to the watsonx.governance payload dataset."""
        url = (
            f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}"
            f"/v2/data_sets/{self.DATASET_ID}/records?header=true"
        )
        try:
            resp = requests.post(url, headers=self._headers(), json=[record], timeout=10)
            resp.raise_for_status()
            return True
        except requests.HTTPError as exc:
            logger.error(f"Governance payload log failed {exc.response.status_code}: {exc.response.text[:200]}")
            return False
        except Exception as exc:
            logger.error(f"Governance payload log error: {exc}")
            return False

    def _store_local(self, record: Dict[str, Any]) -> None:
        self._local_log.append(record)
        if len(self._local_log) > 5000:
            self._local_log = self._local_log[-5000:]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_risk_assessment(
        self,
        account_id: str,
        lookback_days: int,
        risk_score: float,
        risk_level: str,
        aml_patterns_count: int,
        tx_count: int = 0,
    ) -> Dict[str, Any]:
        """Log a /assess/risk call to watsonx.governance."""
        scoring_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        record = {
            "request": {
                "fields": ["account_id", "lookback_days"],
                "values": [[account_id, lookback_days]],
            },
            "response": {
                # prediction + prediction_probability required by OpenScale UI
                "fields": ["prediction", "prediction_probability", "risk_score", "risk_level", "aml_patterns_count", "transaction_count"],
                "values": [[risk_level, risk_score, risk_score, risk_level, aml_patterns_count, tx_count]],
            },
            "scoring_timestamp": ts,
            "deployment_id": self.DEPLOYMENT_ID,
        }

        local_entry = {
            "scoring_id": scoring_id,
            "timestamp": ts,
            "type": "risk_assessment",
            "account_id": account_id,
            "lookback_days": lookback_days,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "aml_patterns_count": aml_patterns_count,
            "transaction_count": tx_count,
        }
        self._store_local(local_entry)

        sent_to_cloud = False
        if self.enabled:
            sent_to_cloud = self._log_to_governance(record)

        return {
            "status": "logged",
            "scoring_id": scoring_id,
            "sent_to_governance": sent_to_cloud,
            "timestamp": ts,
        }

    def log_explanation(
        self,
        account_id: str,
        risk_score: float,
        risk_level: str,
        model_used: str,
        fallback_used: bool,
        execution_time_ms: float = 0.0,
    ) -> Dict[str, Any]:
        """Log a /explain call to watsonx.governance."""
        scoring_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        record = {
            "request": {
                "fields": ["account_id", "risk_score", "risk_level"],
                "values": [[account_id, risk_score, risk_level]],
            },
            "response": {
                "fields": ["model_used", "fallback_used", "execution_time_ms"],
                "values": [[model_used, fallback_used, execution_time_ms]],
            },
            "scoring_timestamp": ts,
            "deployment_id": self.DEPLOYMENT_ID,
        }

        local_entry = {
            "scoring_id": scoring_id,
            "timestamp": ts,
            "type": "explanation",
            "account_id": account_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "model_used": model_used,
            "fallback_used": fallback_used,
            "execution_time_ms": execution_time_ms,
        }
        self._store_local(local_entry)

        sent_to_cloud = False
        if self.enabled:
            sent_to_cloud = self._log_to_governance(record)

        return {
            "status": "logged",
            "scoring_id": scoring_id,
            "sent_to_governance": sent_to_cloud,
            "timestamp": ts,
        }

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_recent_logs(self, limit: int = 50, log_type: Optional[str] = None, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return recent local logs (optionally filtered by type and/or account_id)."""
        logs = self._local_log
        if log_type:
            logs = [l for l in logs if l.get("type") == log_type]
        if account_id:
            logs = [l for l in logs if l.get("account_id") == account_id]
        return logs[-limit:][::-1]

    def get_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics from local log."""
        all_logs = self._local_log
        risk_logs = [l for l in all_logs if l.get("type") == "risk_assessment"]
        expl_logs = [l for l in all_logs if l.get("type") == "explanation"]

        risk_scores = [l.get("risk_score", 0) for l in risk_logs]

        level_dist: Dict[str, int] = {}
        for l in risk_logs:
            level = l.get("risk_level", "unknown")
            level_dist[level] = level_dist.get(level, 0) + 1

        fallback_count = sum(1 for l in expl_logs if l.get("fallback_used"))

        return {
            "total_risk_assessments": len(risk_logs),
            "total_explanations": len(expl_logs),
            "avg_risk_score": round(sum(risk_scores) / len(risk_scores), 4) if risk_scores else None,
            "max_risk_score": round(max(risk_scores), 4) if risk_scores else None,
            "min_risk_score": round(min(risk_scores), 4) if risk_scores else None,
            "risk_level_distribution": level_dist,
            "explanation_fallback_rate": round(fallback_count / len(expl_logs), 4) if expl_logs else None,
            "governance_cloud_enabled": self.enabled,
            "governance_instance_id": self.INSTANCE_ID,
            "governance_subscription_id": self.SUBSCRIPTION_ID,
        }

    def get_cloud_records(self, limit: int = 20) -> Dict[str, Any]:
        """Fetch recent records directly from watsonx.governance cloud."""
        if not self.enabled:
            return {"error": "governance_disabled", "records": []}
        url = (
            f"{GOVERNANCE_BASE_URL}/openscale/{self.INSTANCE_ID}"
            f"/v2/data_sets/{self.DATASET_ID}/records?limit={limit}"
        )
        try:
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error(f"Failed to fetch cloud records: {exc}")
            return {"error": str(exc), "records": []}

    def get_audit_entries(self, limit: int = 100, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return audit entries: local records merged with valid cloud records."""
        entries = []
        seen_ids: set = set()

        # Local entries always included (source of truth for current session)
        local_entries = self.get_recent_logs(limit=limit, log_type="risk_assessment")
        for e in local_entries:
            e = dict(e)
            e["source"] = "local"
            sid = e.get("scoring_id", "")
            if sid:
                seen_ids.add(sid)
            entries.append(e)

        # Cloud entries supplement local (records from previous pod instances)
        if self.enabled:
            raw = self.get_cloud_records(limit=limit)
            records = raw.get("records", [])
            for r in records:
                entity = r.get("entity", r)
                meta = r.get("metadata", {})

                # IBM OpenScale stores fields as flat entity.values dict
                values = entity.get("values", {})
                # Fallback: try nested request/response format
                if not values:
                    req = entity.get("request", {})
                    resp = entity.get("response", {})
                    req_fields = req.get("fields", [])
                    req_values = req.get("values", [[]])[0] if req.get("values") else []
                    resp_fields = resp.get("fields", [])
                    resp_values = resp.get("values", [[]])[0] if resp.get("values") else []
                    values = dict(zip(req_fields, req_values))
                    values.update(dict(zip(resp_fields, resp_values)))

                cloud_account_id = values.get("account_id", "")
                # Skip records without account_id (not a risk_assessment, or malformed)
                if not cloud_account_id:
                    continue

                cloud_id = meta.get("id", values.get("scoring_id", entity.get("scoring_id", "")))
                if cloud_id in seen_ids:
                    continue

                entry = {
                    "scoring_id": cloud_id,
                    "timestamp": values.get("scoring_timestamp", entity.get("scoring_timestamp", meta.get("created_at", ""))),
                    "type": "risk_assessment",
                    "account_id": cloud_account_id,
                    "lookback_days": values.get("lookback_days", 30),
                    "risk_score": values.get("risk_score", 0),
                    "risk_level": values.get("risk_level", ""),
                    "aml_patterns_count": values.get("aml_patterns_count", 0),
                    "transaction_count": values.get("transaction_count", 0),
                    "source": "cloud",
                }
                entries.append(entry)

        if account_id:
            entries = [e for e in entries if e.get("account_id") == account_id]

        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return entries[:limit]


# Made with Bob
