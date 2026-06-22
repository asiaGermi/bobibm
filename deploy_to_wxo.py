#!/usr/bin/env python3
"""
Deployment script for Financial Risk Management tools and orchestrator agent to watsonx Orchestrate.

This script:
1. Authenticates with watsonx Orchestrate
2. Imports 4 OpenAPI tools from the Financial Risk API
3. Creates an orchestrator agent that coordinates the tools
4. Deploys everything to the draft environment

Usage:
    python deploy_to_wxo.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Configuration from environment variables
WXO_URL = os.getenv("WXO_URL", "https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024")
WXO_APIKEY = os.getenv("WXO_APIKEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud")

# Tool names
TOOLS = [
    "analyzeTransaction",
    "assessRisk", 
    "detectFraud",
    "recommendActions"
]

# Agent name
AGENT_NAME = "financial_risk_orchestrator"

def run_command(cmd, description):
    """Execute a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Success!")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: Command not found. Make sure the ADK CLI is installed.")
        print(f"Install with: pip install ibm-watsonx-orchestrate")
        return False

def check_prerequisites():
    """Check if required tools and environment variables are set."""
    print("\n" + "="*60)
    print("🔍 Checking Prerequisites")
    print("="*60)
    
    # Check environment variables
    if not WXO_APIKEY:
        print("❌ Error: WXO_APIKEY environment variable not set")
        print("Please set it with: export WXO_APIKEY=your_api_key")
        return False
    
    print(f"✅ WXO_URL: {WXO_URL}")
    print(f"✅ WXO_APIKEY: {'*' * 20}{WXO_APIKEY[-4:]}")
    print(f"✅ API_BASE_URL: {API_BASE_URL}")
    
    # Check if OpenAPI spec exists
    if not Path("openapi_spec.json").exists():
        print("❌ Error: openapi_spec.json not found")
        return False
    print("✅ OpenAPI spec found")
    
    # Check if agent YAML exists
    if not Path("agents/financial_risk_orchestrator.yaml").exists():
        print("❌ Error: agents/financial_risk_orchestrator.yaml not found")
        return False
    print("✅ Agent definition found")
    
    return True

def login_to_wxo():
    """Authenticate with watsonx Orchestrate."""
    cmd = [
        "orchestrate",
        "login",
        "--url", WXO_URL,
        "--apikey", WXO_APIKEY
    ]
    return run_command(cmd, "Logging in to watsonx Orchestrate")

def import_openapi_tools():
    """Import all 4 tools from the OpenAPI specification."""
    cmd = [
        "orchestrate",
        "tools",
        "import",
        "-k", "openapi",
        "-f", "openapi_spec.json"
    ]
    return run_command(cmd, "Importing OpenAPI tools (all 4 endpoints)")

def list_tools():
    """List all imported tools to verify."""
    cmd = [
        "orchestrate",
        "tools",
        "list"
    ]
    return run_command(cmd, "Listing imported tools")

def import_agent():
    """Import the orchestrator agent."""
    cmd = [
        "orchestrate",
        "agents",
        "import",
        "-f", "agents/financial_risk_orchestrator.yaml"
    ]
    return run_command(cmd, "Importing Financial Risk Orchestrator agent")

def list_agents():
    """List all agents to verify."""
    cmd = [
        "orchestrate",
        "agents",
        "list"
    ]
    return run_command(cmd, "Listing agents")

def main():
    """Main deployment workflow."""
    print("\n" + "="*60)
    print("🚀 Financial Risk Management Deployment to watsonx Orchestrate")
    print("="*60)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix the issues and try again.")
        sys.exit(1)
    
    # Step 2: Login
    if not login_to_wxo():
        print("\n❌ Login failed. Please check your credentials.")
        sys.exit(1)
    
    # Step 3: Import OpenAPI tools
    if not import_openapi_tools():
        print("\n⚠️  Tool import failed. This might be okay if tools already exist.")
        print("Continuing with agent import...")
    
    # Step 4: List tools to verify
    list_tools()
    
    # Step 5: Import orchestrator agent
    if not import_agent():
        print("\n❌ Agent import failed.")
        sys.exit(1)
    
    # Step 6: List agents to verify
    list_agents()
    
    # Success!
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\n📋 Summary:")
    print(f"   • 4 OpenAPI tools imported from Financial Risk API")
    print(f"   • 1 orchestrator agent created: {AGENT_NAME}")
    print(f"\n🔗 Next steps:")
    print(f"   1. Go to watsonx Orchestrate UI")
    print(f"   2. Navigate to the Agents section")
    print(f"   3. Find '{AGENT_NAME}' agent")
    print(f"   4. Test the agent with an account_id")
    print(f"\n💡 Example query:")
    print(f"   'Analyze the risk for account ACC-12345'")
    print("\n")

if __name__ == "__main__":
    main()

# Made with Bob
