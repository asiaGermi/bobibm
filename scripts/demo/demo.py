#!/usr/bin/env python3
"""
Financial Risk Management - Demo Script
Demonstrates end-to-end workflow with live API calls
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime
import sys

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
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_json(data: Dict[Any, Any], indent: int = 2):
    """Print formatted JSON"""
    print(f"{Colors.OKBLUE}{json.dumps(data, indent=indent)}{Colors.ENDC}")

def make_api_call(endpoint: str, method: str = "GET", data: Dict | None = None) -> Dict:
    """Make API call and return response"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print_error(f"API call failed: {e}")
        return {"error": str(e)}

def demo_health_check():
    """Demo: Health check"""
    print_step(1, "Health Check - Verifying API Status")
    print(f"   Endpoint: GET {API_BASE_URL}/health\n")
    
    result = make_api_call("/health")
    
    if "error" not in result:
        print_success("API is healthy!")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Data Layer: {result.get('data_layer_status', 'unknown')}")
        print(f"   Total Transactions: {result.get('total_transactions', 0):,}")
        print(f"   Timestamp: {result.get('timestamp', 'unknown')}")
    else:
        print_error("Health check failed!")
    
    return result

def demo_risk_assessment(account_id: str):
    """Demo: Risk assessment"""
    print_step(2, f"Risk Assessment - Analyzing Account {account_id}")
    print(f"   Endpoint: POST {API_BASE_URL}/api/v1/assess/risk\n")
    
    payload = {"account_id": account_id}
    print("   Request:")
    print_json(payload)
    print()
    
    result = make_api_call("/api/v1/assess/risk", method="POST", data=payload)
    
    if "error" not in result:
        print_success("Risk assessment completed!")
        print(f"   Risk Score: {result.get('risk_score', 0):.2f}")
        print(f"   Risk Level: {result.get('risk_level', 'unknown')}")
        
        if 'risk_factors' in result:
            print(f"   Risk Factors:")
            for factor, value in result['risk_factors'].items():
                print(f"      - {factor}: {value}")
        
        if 'high_risk_accounts' in result and result['high_risk_accounts']:
            print(f"   High Risk Accounts: {len(result['high_risk_accounts'])}")
    else:
        print_error("Risk assessment failed!")
    
    return result

def demo_fraud_detection(account_id: str):
    """Demo: Fraud detection"""
    print_step(3, f"Fraud Detection - Scanning Account {account_id}")
    print(f"   Endpoint: POST {API_BASE_URL}/api/v1/detect/fraud\n")
    
    payload = {"account_id": account_id, "mode": "account_profile"}
    print("   Request:")
    print_json(payload)
    print()
    
    result = make_api_call("/api/v1/detect/fraud", method="POST", data=payload)
    
    if "error" not in result:
        print_success("Fraud detection completed!")
        
        if 'fraud_signals' in result:
            signals = result['fraud_signals']
            print(f"   Fraud Signals:")
            print(f"      - Temporal Anomalies: {signals.get('temporal_anomalies', 0)}")
            print(f"      - Laundering History: {signals.get('laundering_history', False)}")
            print(f"      - Suspicious Patterns: {signals.get('suspicious_patterns', 0)}")
        
        if 'account_profile' in result:
            profile = result['account_profile']
            print(f"   Account Profile:")
            print(f"      - Total Transactions: {profile.get('total_transactions', 0)}")
            print(f"      - Total Amount: ${profile.get('total_amount', 0):,.2f}")
            print(f"      - Average Transaction: ${profile.get('avg_transaction', 0):,.2f}")
    else:
        print_error("Fraud detection failed!")
    
    return result

def demo_transaction_analysis(account_id: str):
    """Demo: Transaction analysis"""
    print_step(4, f"Transaction Analysis - Detecting AML Patterns for {account_id}")
    print(f"   Endpoint: POST {API_BASE_URL}/api/v1/analyze/transaction\n")
    
    payload = {"account_id": account_id}
    print("   Request:")
    print_json(payload)
    print()
    
    result = make_api_call("/api/v1/analyze/transaction", method="POST", data=payload)
    
    if "error" not in result:
        print_success("Transaction analysis completed!")
        
        if 'patterns_detected' in result:
            patterns = result['patterns_detected']
            print(f"   AML Patterns Detected:")
            for pattern_type, detected in patterns.items():
                status = "✓ DETECTED" if detected else "✗ Not detected"
                color = Colors.WARNING if detected else Colors.OKGREEN
                print(f"      - {pattern_type}: {color}{status}{Colors.ENDC}")
        
        if 'transaction_stats' in result:
            stats = result['transaction_stats']
            print(f"   Transaction Statistics:")
            print(f"      - Total Transactions: {stats.get('total_transactions', 0)}")
            print(f"      - Total Amount: ${stats.get('total_amount', 0):,.2f}")
            print(f"      - Average Amount: ${stats.get('avg_amount', 0):,.2f}")
    else:
        print_error("Transaction analysis failed!")
    
    return result

def demo_recommendations(risk_score: float, patterns: Dict, fraud_signals: Dict):
    """Demo: Generate recommendations"""
    print_step(5, "Recommendation Generation - Creating Action Plan")
    print(f"   Endpoint: POST {API_BASE_URL}/api/v1/recommend/actions\n")
    
    payload = {
        "risk_score": risk_score,
        "patterns": patterns,
        "fraud_signals": fraud_signals
    }
    print("   Request:")
    print_json(payload)
    print()
    
    result = make_api_call("/api/v1/recommend/actions", method="POST", data=payload)
    
    if "error" not in result:
        print_success("Recommendations generated!")
        
        if 'recommended_actions' in result:
            actions = result['recommended_actions']
            print(f"   Recommended Actions ({len(actions)}):")
            for i, action in enumerate(actions, 1):
                action_type = action.get('action', 'unknown')
                priority = action.get('priority', 'unknown')
                reasoning = action.get('reasoning', 'No reasoning provided')
                
                # Color code by action type
                if action_type == "ALERT":
                    color = Colors.FAIL
                elif action_type == "REVIEW":
                    color = Colors.WARNING
                elif action_type == "BLOCK":
                    color = Colors.FAIL + Colors.BOLD
                else:
                    color = Colors.OKBLUE
                
                print(f"      {i}. {color}{action_type}{Colors.ENDC} (Priority: {priority})")
                print(f"         Reasoning: {reasoning}")
    else:
        print_error("Recommendation generation failed!")
    
    return result

def demo_explanation(risk_score: float, patterns: list, fraud_signals: list):
    """Demo: Generate explanation using Granite LLM"""
    print_step(6, "Explanation Generation - IBM watsonx.ai Granite LLM")
    print(f"   Endpoint: POST {API_BASE_URL}/api/v1/explain\n")
    
    payload = {
        "risk_score": risk_score,
        "patterns": patterns,
        "fraud_signals": fraud_signals
    }
    print("   Request:")
    print_json(payload)
    print()
    
    result = make_api_call("/api/v1/explain", method="POST", data=payload)
    
    if "error" not in result:
        print_success("Explanation generated!")
        print(f"   Model Used: {result.get('model_used', 'unknown')}")
        print(f"   Fallback Used: {result.get('fallback_used', False)}")
        print(f"\n   {Colors.BOLD}Explanation:{Colors.ENDC}")
        print(f"   {result.get('explanation', 'No explanation available')}")
    else:
        print_error("Explanation generation failed!")
    
    return result

def generate_consolidated_report(health: Dict, risk: Dict, fraud: Dict, 
                                 transaction: Dict, recommendations: Dict, 
                                 explanation: Dict):
    """Generate consolidated report"""
    print_header("CONSOLIDATED FINANCIAL RISK ANALYSIS REPORT")
    
    print(f"{Colors.BOLD}Report Generated:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Account ID:{Colors.ENDC} {DEMO_ACCOUNT_ID}")
    print(f"{Colors.BOLD}API Endpoint:{Colors.ENDC} {API_BASE_URL}")
    print()
    
    # System Status
    print(f"{Colors.BOLD}1. SYSTEM STATUS{Colors.ENDC}")
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Data Layer: {health.get('data_layer_status', 'unknown')}")
    print(f"   Total Transactions Available: {health.get('total_transactions', 0):,}")
    print()
    
    # Risk Assessment
    print(f"{Colors.BOLD}2. RISK ASSESSMENT{Colors.ENDC}")
    risk_score = risk.get('risk_score', 0)
    risk_level = risk.get('risk_level', 'unknown')
    
    # Color code risk level
    if risk_level == "HIGH":
        risk_color = Colors.FAIL
    elif risk_level == "MEDIUM":
        risk_color = Colors.WARNING
    else:
        risk_color = Colors.OKGREEN
    
    print(f"   Risk Score: {risk_color}{risk_score:.2f}{Colors.ENDC}")
    print(f"   Risk Level: {risk_color}{risk_level}{Colors.ENDC}")
    
    if 'risk_factors' in risk:
        print(f"   Risk Factors:")
        for factor, value in risk['risk_factors'].items():
            print(f"      - {factor}: {value}")
    print()
    
    # Fraud Detection
    print(f"{Colors.BOLD}3. FRAUD DETECTION{Colors.ENDC}")
    if 'fraud_signals' in fraud:
        signals = fraud['fraud_signals']
        print(f"   Temporal Anomalies: {signals.get('temporal_anomalies', 0)}")
        print(f"   Laundering History: {signals.get('laundering_history', False)}")
        print(f"   Suspicious Patterns: {signals.get('suspicious_patterns', 0)}")
    print()
    
    # Transaction Analysis
    print(f"{Colors.BOLD}4. TRANSACTION ANALYSIS{Colors.ENDC}")
    if 'patterns_detected' in transaction:
        patterns = transaction['patterns_detected']
        detected_patterns = [k for k, v in patterns.items() if v]
        if detected_patterns:
            print(f"   {Colors.WARNING}AML Patterns Detected:{Colors.ENDC}")
            for pattern in detected_patterns:
                print(f"      - {pattern}")
        else:
            print(f"   {Colors.OKGREEN}No AML patterns detected{Colors.ENDC}")
    
    if 'transaction_stats' in transaction:
        stats = transaction['transaction_stats']
        print(f"   Transaction Statistics:")
        print(f"      - Total: {stats.get('total_transactions', 0)}")
        print(f"      - Total Amount: ${stats.get('total_amount', 0):,.2f}")
        print(f"      - Average: ${stats.get('avg_amount', 0):,.2f}")
    print()
    
    # Recommendations
    print(f"{Colors.BOLD}5. RECOMMENDED ACTIONS{Colors.ENDC}")
    if 'recommended_actions' in recommendations:
        actions = recommendations['recommended_actions']
        for i, action in enumerate(actions, 1):
            action_type = action.get('action', 'unknown')
            priority = action.get('priority', 'unknown')
            
            if action_type == "ALERT":
                color = Colors.FAIL
            elif action_type == "REVIEW":
                color = Colors.WARNING
            elif action_type == "BLOCK":
                color = Colors.FAIL + Colors.BOLD
            else:
                color = Colors.OKBLUE
            
            print(f"   {i}. {color}{action_type}{Colors.ENDC} (Priority: {priority})")
    print()
    
    # Explanation
    print(f"{Colors.BOLD}6. EXPLANATION (IBM watsonx.ai Granite){Colors.ENDC}")
    if 'explanation' in explanation:
        print(f"   {explanation.get('explanation', 'No explanation available')}")
        print(f"\n   Model: {explanation.get('model_used', 'unknown')}")
    print()
    
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")

def main():
    """Main demo function"""
    print_header("FINANCIAL RISK MANAGEMENT SYSTEM - LIVE DEMO")
    print(f"{Colors.BOLD}IBM Open Agentic Builders - Track A: Financial Risk Management{Colors.ENDC}")
    print(f"Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Endpoint: {API_BASE_URL}")
    print(f"Demo Account: {DEMO_ACCOUNT_ID}")
    print()
    
    input(f"{Colors.OKCYAN}Press Enter to start the demo...{Colors.ENDC}")
    
    # Step 1: Health Check
    health_result = demo_health_check()
    time.sleep(1)
    
    # Step 2: Risk Assessment
    risk_result = demo_risk_assessment(DEMO_ACCOUNT_ID)
    time.sleep(1)
    
    # Step 3: Fraud Detection
    fraud_result = demo_fraud_detection(DEMO_ACCOUNT_ID)
    time.sleep(1)
    
    # Step 4: Transaction Analysis
    transaction_result = demo_transaction_analysis(DEMO_ACCOUNT_ID)
    time.sleep(1)
    
    # Step 5: Recommendations
    risk_score = risk_result.get('risk_score', 0.5)
    patterns = transaction_result.get('patterns_detected', {})
    fraud_signals = fraud_result.get('fraud_signals', {})
    
    recommendations_result = demo_recommendations(risk_score, patterns, fraud_signals)
    time.sleep(1)
    
    # Step 6: Explanation
    patterns_list = [k for k, v in patterns.items() if v] if patterns else []
    fraud_list = [k for k, v in fraud_signals.items() if v] if fraud_signals else []
    
    explanation_result = demo_explanation(risk_score, patterns_list, fraud_list)
    time.sleep(1)
    
    # Generate Consolidated Report
    generate_consolidated_report(
        health_result,
        risk_result,
        fraud_result,
        transaction_result,
        recommendations_result,
        explanation_result
    )
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Demo completed successfully!{Colors.ENDC}")
    print(f"\n{Colors.OKCYAN}Next Steps:{Colors.ENDC}")
    print(f"   1. Review the consolidated report above")
    print(f"   2. Test with different account IDs")
    print(f"   3. Explore watsonx Orchestrate UI for agent orchestration")
    print(f"   4. Check API documentation at {API_BASE_URL}/docs")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Demo failed with error: {e}")
        sys.exit(1)

# Made with Bob
