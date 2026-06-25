"""
MCP Server for Financial Risk Management API
FastMCP with streamable-http transport + /health endpoint.

Uses a raw ASGI wrapper to combine the FastMCP app (which requires lifespan
initialization for its StreamableHTTPSessionManager) with a /health route.
"""
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

API_BASE_URL = os.environ.get(
    "API_BASE_URL",
    "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
)

mcp = FastMCP("financial-risk-mcp")


async def call_api(endpoint: str, payload: dict) -> str:
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        r = await client.post(endpoint, json=payload)
        r.raise_for_status()
        return r.text


@mcp.tool(name="analyzeTransaction")
async def analyze_transaction(account_id: str, timestamp: str, lookback_days: int = 30) -> str:
    """Analyzes transaction details, detects anomalies, and identifies AML patterns for an account."""
    return await call_api("/api/v1/analyze/transaction", {
        "account_id": account_id, "timestamp": timestamp, "lookback_days": lookback_days
    })


@mcp.tool(name="assessRisk")
async def assess_risk(account_id: str, lookback_days: int = 90) -> str:
    """Assesses AML risk for an account: score (0-1), level (LOW/MEDIUM/HIGH), detected patterns, statistics."""
    return await call_api("/api/v1/assess/risk", {
        "account_id": account_id, "lookback_days": lookback_days
    })


@mcp.tool(name="detectFraud")
async def detect_fraud(account_id: str, timestamp: str, lookback_days: int = 30) -> str:
    """Detects fraud signals for an account at a given timestamp: risk level, anomaly score, fraud indicators."""
    return await call_api("/api/v1/detect/fraud", {
        "account_id": account_id, "timestamp": timestamp, "lookback_days": lookback_days
    })


@mcp.tool(name="recommendActions")
async def recommend_actions(account_id: str, lookback_days: int = 90) -> str:
    """Returns compliance recommendations (ALERT/BLOCK/REVIEW/MONITOR) based on risk and fraud analysis."""
    return await call_api("/api/v1/recommend/actions", {
        "account_id": account_id, "lookback_days": lookback_days
    })


@mcp.tool(name="explainRisk")
async def explain_risk(account_id: str, risk_score: float, risk_level: str) -> str:
    """Generates a natural language explanation of the risk assessment using IBM watsonx.ai Granite."""
    return await call_api("/api/v1/explain", {
        "account_id": account_id, "risk_score": risk_score, "risk_level": risk_level
    })


# --- Raw ASGI wrapper ---

_mcp_asgi = mcp.streamable_http_app()
_health_body = json.dumps({"status": "ok", "service": "financial-risk-mcp", "tools": 5}).encode()


async def _send_health(send):
    await send({"type": "http.response.start", "status": 200, "headers": [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(_health_body)).encode()),
    ]})
    await send({"type": "http.response.body", "body": _health_body})


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        # Delegate lifespan to MCP app so its StreamableHTTPSessionManager initializes
        await _mcp_asgi(scope, receive, send)
    elif scope["type"] == "http" and scope.get("path") == "/health":
        await _send_health(send)
    else:
        await _mcp_asgi(scope, receive, send)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")

# Made with Bob
