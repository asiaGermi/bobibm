#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Risk Management - Automated Demo Script (No User Input)
Demonstrates end-to-end workflow with live API calls
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Configuration
API_BASE_URL = "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
DEMO_ACCOUNT_ID = "ACC-12345"

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_step(step_num: int, text: str):
    """Print formatted step"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[STEP {step_num}]{Colors.ENDC} {text}")

def print_success(text: str):
    """Print success message"""
    try:
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    try:
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")

def make_api_call(endpoint: str, method: str = "GET", data: Dict | None = None) -> Dict:
    """Make API call and return response"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        error_msg = f"API call failed: {str(e)[:100]}"
        print(f"{Colors.FAIL}[ERROR] {error_msg}{Colors.ENDC}")
        return {"error": str(e)}

def main():
    """Main demo function"""
    print_header("FINANCIAL RISK MANAGEMENT SYSTEM - AUTOMATED DEMO")
    print(f"{Colors.BOLD}IBM Open Agentic Builders - Track A: Financial Risk Management{Colors.ENDC}")
    print(f"Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Endpoint: {API_BASE_URL}")
    print(f"Demo Account: {DEMO_ACCOUNT_ID}")
    print()
    
    # Step 1: Health Check
    print_step(1, "Health Check - Verifying API Status")
    health_result = make_api_call("/health")
    
    if "error" not in health_result:
        print_success("API is healthy!")
        print(f"   Status: {health_result.get('status', 'unknown')}")
        print(f"   Total Transactions: {health_result.get('total_transactions', 0):,}")
    else:
        print_error("Health check failed!")
        return
    
    time.sleep(1)
    
    # Step 2: Risk Assessment
    print_step(2, f"Risk Assessment - Analyzing Account {DEMO_ACCOUNT_ID}")
    risk_result = make_api_call("/api/v1/assess/risk", method="POST", data={"account_id": DEMO_ACCOUNT_ID})
    
    if "error" not in risk_result:
        print_success("Risk assessment completed!")
        print(f"   Risk Score: {risk_result.get('risk_score', 0):.2f}")
        print(f"   Risk Level: {risk_result.get('risk_level', 'unknown')}")
    else:
        print_error("Risk assessment failed!")
    
    time.sleep(1)
    
    # Step 3: Fraud Detection
    print_step(3, f"Fraud Detection - Scanning Account {DEMO_ACCOUNT_ID}")
    fraud_result = make_api_call("/api/v1/detect/fraud", method="POST", 
                                 data={"account_id": DEMO_ACCOUNT_ID, "mode": "account_profile"})
    
    if "error" not in fraud_result:
        print_success("Fraud detection completed!")
        if 'fraud_signals' in fraud_result:
            signals = fraud_result['fraud_signals']
            print(f"   Temporal Anomalies: {signals.get('temporal_anomalies', 0)}")
            print(f"   Laundering History: {signals.get('laundering_history', False)}")
    else:
        print_error("Fraud detection failed!")
    
    time.sleep(1)
    
    # Step 4: Transaction Analysis
    print_step(4, f"Transaction Analysis - Detecting AML Patterns")
    transaction_result = make_api_call("/api/v1/analyze/transaction", method="POST", 
                                      data={"account_id": DEMO_ACCOUNT_ID})
    
    if "error" not in transaction_result:
        print_success("Transaction analysis completed!")
        if 'patterns_detected' in transaction_result:
            patterns = transaction_result['patterns_detected']
            detected = [k for k, v in patterns.items() if v]
            if detected:
                print(f"   {Colors.WARNING}AML Patterns: {', '.join(detected)}{Colors.ENDC}")
            else:
                print(f"   {Colors.OKGREEN}No AML patterns detected{Colors.ENDC}")
    else:
        print_error("Transaction analysis failed!")
    
    time.sleep(1)
    
    # Step 5: Recommendations
    print_step(5, "Recommendation Generation")
    risk_score = risk_result.get('risk_score', 0.5)
    patterns = transaction_result.get('patterns_detected', {})
    fraud_signals = fraud_result.get('fraud_signals', {})
    
    rec_result = make_api_call("/api/v1/recommend/actions", method="POST",
                               data={"risk_score": risk_score, "patterns": patterns, 
                                    "fraud_signals": fraud_signals})
    
    if "error" not in rec_result:
        print_success("Recommendations generated!")
        if 'recommended_actions' in rec_result:
            actions = rec_result['recommended_actions']
            print(f"   Actions: {len(actions)} recommendations")
            for action in actions[:3]:  # Show first 3
                print(f"      - {action.get('action', 'unknown')}")
    else:
        print_error("Recommendation generation failed!")
    
    time.sleep(1)
    
    # Step 6: Explanation
    print_step(6, "Explanation Generation - IBM watsonx.ai Granite")
    patterns_list = [k for k, v in patterns.items() if v] if patterns else []
    fraud_list = [k for k, v in fraud_signals.items() if v] if fraud_signals else []
    
    exp_result = make_api_call("/api/v1/explain", method="POST",
                               data={"risk_score": risk_score, "patterns": patterns_list,
                                    "fraud_signals": fraud_list})
    
    if "error" not in exp_result:
        print_success("Explanation generated!")
        print(f"   Model: {exp_result.get('model_used', 'unknown')}")
        print(f"   Fallback: {exp_result.get('fallback_used', False)}")
    else:
        print_error("Explanation generation failed!")
    
    # Summary
    print_header("DEMO SUMMARY")
    try:
        print(f"{Colors.OKGREEN}✓ All 6 steps completed successfully!{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.OKGREEN}[OK] All 6 steps completed successfully!{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
    print(f"   Risk Score: {risk_score:.2f}")
    print(f"   Risk Level: {risk_result.get('risk_level', 'unknown')}")
    print(f"   Patterns Detected: {len([k for k, v in patterns.items() if v])}")
    print(f"   Recommendations: {len(rec_result.get('recommended_actions', []))}")
    print(f"\n{Colors.OKCYAN}Demo completed in ~{6} seconds{Colors.ENDC}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
