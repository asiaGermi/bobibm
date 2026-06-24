"""
Test script for MCP Server
Tests all 5 tools locally before deployment
"""

import asyncio
import json
from datetime import datetime


async def test_mcp_tools():
    """Test all MCP tools with sample data."""
    
    print("=" * 80)
    print("MCP Server Test Suite")
    print("=" * 80)
    print()
    
    # Import after printing header to show any import errors clearly
    try:
        from server import call_tool
        print("✓ MCP server module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MCP server: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return
    
    print()
    
    # Test data
    test_account = "ACC-12345"
    test_timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
    
    tests = [
        {
            "name": "assessRisk",
            "description": "Risk Assessment",
            "arguments": {
                "account_id": test_account,
                "lookback_days": 90
            }
        },
        {
            "name": "detectFraud",
            "description": "Fraud Detection",
            "arguments": {
                "account_id": test_account,
                "timestamp": test_timestamp,
                "lookback_days": 30
            }
        },
        {
            "name": "analyzeTransaction",
            "description": "Transaction Analysis",
            "arguments": {
                "account_id": test_account,
                "timestamp": test_timestamp,
                "lookback_days": 30
            }
        },
        {
            "name": "recommendActions",
            "description": "Action Recommendations",
            "arguments": {
                "account_id": test_account,
                "risk_score": 0.75,
                "lookback_days": 90
            }
        },
        {
            "name": "explainRisk",
            "description": "Risk Explanation",
            "arguments": {
                "account_id": test_account,
                "risk_score": 0.75,
                "risk_level": "high",
                "aml_patterns": ["fan-out", "high-velocity"],
                "recommendations": ["ALERT", "REVIEW"]
            }
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"Test {i}/{len(tests)}: {test['description']}")
        print("-" * 80)
        print(f"Tool: {test['name']}")
        print(f"Arguments: {json.dumps(test['arguments'], indent=2)}")
        print()
        
        try:
            # Call the tool
            result = await call_tool(test['name'], test['arguments'])
            
            # Extract text from result
            if result and len(result) > 0:
                text = result[0].text
                print("Response:")
                print(text)
                print()
                
                # Check for errors in response
                if "Error" in text or "error" in text.lower():
                    results.append({
                        "test": test['name'],
                        "status": "⚠️  WARNING",
                        "message": "Response contains error message"
                    })
                else:
                    results.append({
                        "test": test['name'],
                        "status": "✓ PASS",
                        "message": "Tool executed successfully"
                    })
            else:
                results.append({
                    "test": test['name'],
                    "status": "✗ FAIL",
                    "message": "Empty response"
                })
                print("✗ Empty response")
                print()
                
        except Exception as e:
            results.append({
                "test": test['name'],
                "status": "✗ FAIL",
                "message": str(e)
            })
            print(f"✗ Error: {e}")
            print()
        
        print("=" * 80)
        print()
    
    # Summary
    print("\nTest Summary")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['status'] == "✓ PASS")
    warnings = sum(1 for r in results if r['status'] == "⚠️  WARNING")
    failed = sum(1 for r in results if r['status'] == "✗ FAIL")
    
    for result in results:
        print(f"{result['status']} {result['test']}: {result['message']}")
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0 and warnings == 0:
        print("✓ All tests passed! MCP server is ready for deployment.")
    elif failed == 0:
        print("⚠️  All tests completed with warnings. Review responses before deployment.")
    else:
        print("✗ Some tests failed. Please fix issues before deployment.")
    
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting MCP Server Tests...")
    print("This will test all 5 tools against the live API.")
    print()
    
    try:
        asyncio.run(test_mcp_tools())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
