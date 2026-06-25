"""
MCP Server for Financial Risk Management API
FastMCP with streamable-http transport for IBM watsonx Orchestrate integration.

Tools:
- analyzeTransaction: anomaly detection + AML pattern analysis
- assessRisk: risk score (0-1) + level + patterns
- detectFraud: fraud signals + anomaly score
- recommendActions: ALERT/BLOCK/REVIEW/MONITOR
- explainRisk: natural language explanation via IBM Granite
"""
import os
import uvicorn
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request

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


async def handle_health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "financial-risk-mcp", "tools": 5})


if __name__ == "__main__":
    # streamable_http_app() returns a Starlette app with the MCP endpoint at /mcp
    mcp_asgi = mcp.streamable_http_app()

    app = Starlette(routes=[
        Route("/health", handle_health),
        Mount("/", app=mcp_asgi),
    ])

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

# Made with Bob
