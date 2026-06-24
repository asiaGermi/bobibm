"""
MCP Server for Financial Risk Management API
Exposes 5 API endpoints as MCP tools for watsonx Orchestrate integration.

This server wraps the existing REST API endpoints:
- analyzeTransaction
- assessRisk
- detectFraud
- recommendActions
- explainRisk

Each tool makes HTTP calls to the live API on IBM Cloud Code Engine.
"""

import asyncio
import httpx
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# API Configuration
API_BASE_URL = "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
API_TIMEOUT = 30.0

# Initialize MCP Server
app = Server("financial-risk-mcp")

# HTTP Client
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=API_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
    return http_client


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="analyzeTransaction",
            description="Analyzes transaction details, performs anomaly detection, and identifies AML patterns",
            inputSchema={
                "type": "object",
                "required": ["account_id", "timestamp"],
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier to analyze"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Transaction timestamp in format YYYY/MM/DD HH:MM"
                    },
                    "lookback_days": {
                        "type": "integer",
                        "default": 30,
                        "description": "Number of days to look back for analysis"
                    }
                }
            }
        ),
        Tool(
            name="assessRisk",
            description="Assesses overall risk for an account including risk score, level, AML patterns, and transaction statistics",
            inputSchema={
                "type": "object",
                "required": ["account_id"],
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier to assess"
                    },
                    "lookback_days": {
                        "type": "integer",
                        "default": 90,
                        "description": "Number of days to look back for risk assessment"
                    }
                }
            }
        ),
        Tool(
            name="detectFraud",
            description="Detects potential fraud by analyzing fraud risk level, anomaly scores, and fraud signals",
            inputSchema={
                "type": "object",
                "required": ["account_id", "timestamp"],
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier to check for fraud"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Transaction timestamp in format YYYY/MM/DD HH:MM"
                    },
                    "lookback_days": {
                        "type": "integer",
                        "default": 30,
                        "description": "Number of days to look back for fraud detection"
                    }
                }
            }
        ),
        Tool(
            name="recommendActions",
            description="Provides actionable recommendations based on risk assessment and fraud detection",
            inputSchema={
                "type": "object",
                "required": ["account_id"],
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier for recommendations"
                    },
                    "risk_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Optional risk score from previous assessment"
                    },
                    "lookback_days": {
                        "type": "integer",
                        "default": 90,
                        "description": "Number of days to look back for recommendations"
                    }
                }
            }
        ),
        Tool(
            name="explainRisk",
            description="Generate natural language explanation of risk assessment using IBM watsonx.ai Granite model",
            inputSchema={
                "type": "object",
                "required": ["account_id", "risk_score", "risk_level"],
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to explain"
                    },
                    "risk_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Risk score from risk assessment"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Risk level: minimal, low, medium, high, critical"
                    },
                    "aml_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of detected AML pattern types"
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recommended actions"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute a tool by calling the corresponding API endpoint."""
    
    client = await get_http_client()
    
    try:
        # Map tool names to API endpoints
        endpoint_map = {
            "analyzeTransaction": "/api/v1/analyze/transaction",
            "assessRisk": "/api/v1/assess/risk",
            "detectFraud": "/api/v1/detect/fraud",
            "recommendActions": "/api/v1/recommend/actions",
            "explainRisk": "/api/v1/explain"
        }
        
        if name not in endpoint_map:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        
        endpoint = endpoint_map[name]
        
        # Make API call
        response = await client.post(endpoint, json=arguments)
        response.raise_for_status()
        
        result = response.json()
        
        # Format response based on tool type
        if name == "analyzeTransaction":
            text = format_transaction_analysis(result)
        elif name == "assessRisk":
            text = format_risk_assessment(result)
        elif name == "detectFraud":
            text = format_fraud_detection(result)
        elif name == "recommendActions":
            text = format_recommendations(result)
        elif name == "explainRisk":
            text = format_explanation(result)
        else:
            text = str(result)
        
        return [TextContent(type="text", text=text)]
        
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else str(e)
        return [TextContent(
            type="text",
            text=f"API Error ({e.response.status_code}): {error_detail}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error calling {name}: {str(e)}"
        )]


def format_transaction_analysis(result: Dict[str, Any]) -> str:
    """Format transaction analysis results."""
    lines = [
        f"## Transaction Analysis: {result['account_id']}",
        f"**Timestamp:** {result['timestamp']}",
        f"**Transaction Found:** {'Yes' if result['transaction_found'] else 'No'}",
        ""
    ]
    
    if result.get('transaction'):
        tx = result['transaction']
        lines.extend([
            "### Transaction Details",
            f"- From: {tx['from_bank']} / {tx['from_account']}",
            f"- To: {tx['to_bank']} / {tx['to_account']}",
            f"- Amount: {tx['amount_received']} {tx['receiving_currency']}",
            f"- Payment Format: {tx['payment_format']}",
            f"- Laundering Flag: {'Yes' if tx['is_laundering'] else 'No'}",
            ""
        ])
    
    if result.get('anomaly_detection'):
        anom = result['anomaly_detection']
        lines.extend([
            "### Anomaly Detection",
            f"- Anomalous: {'Yes' if anom['is_anomalous'] else 'No'}",
            f"- Anomaly Score: {anom['anomaly_score']:.3f}",
            f"- Types: {', '.join(anom['anomaly_types']) if anom['anomaly_types'] else 'None'}",
            ""
        ])
    
    return "\n".join(lines)


def format_risk_assessment(result: Dict[str, Any]) -> str:
    """Format risk assessment results."""
    metrics = result['risk_metrics']
    stats = result['transaction_statistics']
    
    lines = [
        f"## Risk Assessment: {result['account_id']}",
        f"**Analysis Period:** {result['analysis_period_days']} days",
        f"**Date Range:** {result['date_range']['start']} to {result['date_range']['end']}",
        "",
        "### Risk Metrics",
        f"- **Risk Score:** {metrics['risk_score']:.3f}",
        f"- **Risk Level:** {metrics['risk_level'].upper()}",
        f"- **AML Patterns Detected:** {metrics['aml_patterns_detected']}",
        ""
    ]
    
    if metrics.get('aml_patterns'):
        lines.append("### AML Patterns")
        for pattern in metrics['aml_patterns']:
            lines.append(f"- **{pattern['pattern_type']}** (Severity: {pattern['severity']}, Confidence: {pattern['confidence']:.2f})")
            lines.append(f"  {pattern['description']}")
        lines.append("")
    
    lines.extend([
        "### Transaction Statistics",
        f"- Total Transactions: {stats['total_transactions']}",
        f"- Sent: {stats['sent_count']} ({stats['total_sent']:.2f})",
        f"- Received: {stats['received_count']} ({stats['total_received']:.2f})",
        f"- Net Flow: {stats['net_flow']:.2f}",
        f"- Laundering: {stats['laundering_count']} ({stats['laundering_percentage']:.1f}%)",
        f"- Unique Counterparties: {stats['unique_counterparties']}",
        ""
    ])
    
    return "\n".join(lines)


def format_fraud_detection(result: Dict[str, Any]) -> str:
    """Format fraud detection results."""
    lines = [
        f"## Fraud Detection: {result['account_id']}",
        f"**Timestamp:** {result['timestamp']}",
        f"**Fraud Risk Level:** {result['fraud_risk_level'].upper()}",
        f"**Anomaly Score:** {result['anomaly_score']:.3f}",
        f"**Anomalous:** {'Yes' if result['is_anomalous'] else 'No'}",
        "",
        "### Fraud Signals"
    ]
    
    if result['fraud_signals']:
        for signal in result['fraud_signals']:
            lines.append(f"- **{signal.get('type', 'Unknown')}** (Severity: {signal.get('severity', 'N/A')})")
            if 'description' in signal:
                lines.append(f"  {signal['description']}")
    else:
        lines.append("- No fraud signals detected")
    
    lines.extend([
        "",
        f"### Recommendation",
        result['recommendation']
    ])
    
    return "\n".join(lines)


def format_recommendations(result: Dict[str, Any]) -> str:
    """Format action recommendations."""
    lines = [
        f"## Action Recommendations: {result['account_id']}",
        f"**Risk Score:** {result['risk_score']:.3f}",
        f"**Risk Level:** {result['risk_level'].upper()}",
        "",
        "### Recommended Actions"
    ]
    
    for rec in result['recommendations']:
        lines.append(f"- **{rec['action']}** (Priority: {rec['priority']})")
        lines.append(f"  Reason: {rec['reason']}")
    
    lines.extend([
        "",
        "### Summary",
        result['summary']
    ])
    
    return "\n".join(lines)


def format_explanation(result: Dict[str, Any]) -> str:
    """Format risk explanation."""
    lines = [
        f"## Risk Explanation: {result['account_id']}",
        f"**Model Used:** {result['model_used']}",
        f"**Generated At:** {result['generated_at']}",
        f"**Fallback Used:** {'Yes' if result['fallback_used'] else 'No'}",
        "",
        "### Explanation",
        result['explanation']
    ]
    
    return "\n".join(lines)


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
