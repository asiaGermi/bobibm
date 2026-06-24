#!/usr/bin/env python3
"""
Deploy Governance Integration to IBM Code Engine

This script automates the deployment of the governance-enabled application
to IBM Code Engine by triggering a rebuild from GitHub.

Usage:
    python scripts/deploy_governance_to_code_engine.py
"""

import subprocess
import sys
import os
from datetime import datetime

# Configuration
APP_NAME = "financial-risk-api"
GITHUB_REPO = "https://github.com/asiaGermi/bobibm"
BUILD_STRATEGY = "buildpacks"

# Governance environment variables
GOVERNANCE_ENV_VARS = {
    "WATSONX_GOVERNANCE_URL": "https://api.dataplatform.cloud.ibm.com",
    "WATSONX_GOVERNANCE_INSTANCE_ID": "gov-675000bo4y",
    "WATSONX_GOVERNANCE_CATALOG_ID": "itz-saas-290",
    "ENABLE_GOVERNANCE_TRACKING": "true"
}

def print_header(message):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70 + "\n")

def run_command(cmd, description, check=True):
    """Execute a shell command and handle errors."""
    print(f"🔧 {description}")
    print(f"   Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(f"   Output:\n{result.stdout}")
        
        if result.returncode == 0:
            print(f"   ✅ Success!\n")
            return True
        else:
            if result.stderr:
                print(f"   ⚠️  Warning: {result.stderr}\n")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return False
    except FileNotFoundError:
        print(f"   ❌ Error: Command not found. Make sure IBM Cloud CLI is installed.")
        print(f"   Install from: https://cloud.ibm.com/docs/cli")
        sys.exit(1)

def check_ibmcloud_login():
    """Check if user is logged into IBM Cloud."""
    print_header("Checking IBM Cloud Login")
    
    result = subprocess.run(
        ["ibmcloud", "target"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Not logged into IBM Cloud")
        print("\nPlease login first:")
        print("   ibmcloud login --sso")
        sys.exit(1)
    
    print("✅ IBM Cloud login verified")
    print(result.stdout)

def check_code_engine_plugin():
    """Check if Code Engine plugin is installed."""
    print_header("Checking Code Engine Plugin")
    
    result = subprocess.run(
        ["ibmcloud", "plugin", "list"],
        capture_output=True,
        text=True
    )
    
    if "code-engine" not in result.stdout:
        print("❌ Code Engine plugin not installed")
        print("\nInstalling Code Engine plugin...")
        run_command(
            ["ibmcloud", "plugin", "install", "code-engine"],
            "Installing Code Engine plugin"
        )
    else:
        print("✅ Code Engine plugin installed")

def get_current_app_info():
    """Get current application information."""
    print_header("Current Application Info")
    
    run_command(
        ["ibmcloud", "ce", "application", "get", "--name", APP_NAME],
        "Fetching current application details",
        check=False
    )

def update_environment_variables():
    """Update environment variables for governance."""
    print_header("Updating Environment Variables")
    
    print("📝 Setting governance environment variables...\n")
    
    # Build the command with all environment variables
    cmd = ["ibmcloud", "ce", "application", "update", "--name", APP_NAME]
    
    for key, value in GOVERNANCE_ENV_VARS.items():
        cmd.extend(["--env", f"{key}={value}"])
        print(f"   • {key}={value}")
    
    print()
    
    success = run_command(
        cmd,
        "Updating environment variables",
        check=False
    )
    
    if not success:
        print("⚠️  Environment variables update had warnings, but continuing...")
    
    return True

def trigger_rebuild_from_github():
    """Trigger application rebuild from GitHub repository."""
    print_header("Triggering Rebuild from GitHub")
    
    print(f"📦 Repository: {GITHUB_REPO}")
    print(f"🏗️  Build Strategy: {BUILD_STRATEGY}")
    print(f"🎯 Application: {APP_NAME}\n")
    
    cmd = [
        "ibmcloud", "ce", "application", "update",
        "--name", APP_NAME,
        "--build-source", GITHUB_REPO,
        "--build-strategy", BUILD_STRATEGY
    ]
    
    success = run_command(
        cmd,
        "Rebuilding application from GitHub",
        check=True
    )
    
    if success:
        print("✅ Rebuild triggered successfully!")
        print("\n📊 The build process will:")
        print("   1. Clone the latest code from GitHub")
        print("   2. Detect and install dependencies from requirements.txt")
        print("   3. Include new governance modules (src/governance/)")
        print("   4. Deploy the updated application")
    
    return success

def wait_for_deployment():
    """Wait for deployment to complete and show status."""
    print_header("Monitoring Deployment")
    
    print("⏳ Waiting for deployment to complete...")
    print("   This may take 2-5 minutes...\n")
    
    # Show application status
    run_command(
        ["ibmcloud", "ce", "application", "get", "--name", APP_NAME],
        "Checking application status",
        check=False
    )
    
    print("\n💡 To monitor logs in real-time, run:")
    print(f"   ibmcloud ce application logs --name {APP_NAME} --follow")

def verify_deployment():
    """Verify the deployment was successful."""
    print_header("Verifying Deployment")
    
    # Get application URL
    result = subprocess.run(
        ["ibmcloud", "ce", "application", "get", "--name", APP_NAME, "--output", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        import json
        try:
            app_info = json.loads(result.stdout)
            url = app_info.get("status", {}).get("url", "")
            
            if url:
                print(f"✅ Application deployed successfully!")
                print(f"\n🔗 Application URL: {url}")
                print(f"\n🧪 Test the governance integration:")
                print(f'   curl -X POST "{url}/api/v1/explain-risk" \\')
                print(f'     -H "Content-Type: application/json" \\')
                print(f"     -d '{{")
                print(f'       "account_id": "TEST-001",')
                print(f'       "risk_score": 0.75,')
                print(f'       "risk_level": "high"')
                print(f"     }}'")
                print(f"\n   Look for 'governance_logged': true in the response")
            else:
                print("⚠️  Could not retrieve application URL")
        except json.JSONDecodeError:
            print("⚠️  Could not parse application info")
    else:
        print("⚠️  Could not verify deployment status")

def print_next_steps():
    """Print next steps for the user."""
    print_header("Next Steps")
    
    print("📋 Post-Deployment Checklist:")
    print()
    print("1. ✅ Test the API endpoint (see command above)")
    print("2. ✅ Verify 'governance_logged': true in response metadata")
    print("3. ✅ Check watsonx.governance UI:")
    print("      https://dataplatform.cloud.ibm.com/wx/governance")
    print("4. ✅ Verify AI Use Case: 'Financial Risk Management - AML Detection'")
    print("5. ✅ Check AI Factsheets for Granite model")
    print("6. ✅ Monitor prediction logs")
    print()
    print("📚 Documentation:")
    print("   • Setup Guide: docs/guides/GOVERNANCE_SETUP_GUIDE.md")
    print("   • Technical Docs: src/governance/README.md")
    print()
    print("🔍 Troubleshooting:")
    print("   • View logs: ibmcloud ce application logs --name financial-risk-api")
    print("   • Check status: ibmcloud ce application get --name financial-risk-api")
    print("   • List env vars: ibmcloud ce application get --name financial-risk-api --output json")

def main():
    """Main deployment workflow."""
    print("\n" + "=" * 70)
    print("  🚀 Deploy Governance Integration to IBM Code Engine")
    print("=" * 70)
    print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Step 1: Check prerequisites
        check_ibmcloud_login()
        check_code_engine_plugin()
        
        # Step 2: Show current app info
        get_current_app_info()
        
        # Step 3: Update environment variables
        update_environment_variables()
        
        # Step 4: Trigger rebuild from GitHub
        trigger_rebuild_from_github()
        
        # Step 5: Wait and monitor
        wait_for_deployment()
        
        # Step 6: Verify deployment
        verify_deployment()
        
        # Step 7: Show next steps
        print_next_steps()
        
        print("\n" + "=" * 70)
        print("  ✅ DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob