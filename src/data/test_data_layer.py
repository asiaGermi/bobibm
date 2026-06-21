"""
Test script for data layer implementation
Tests loader.py and analyzer.py functions
"""

import sys
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.loader import (
    load_dataset,
    get_transactions_by_account,
    get_transactions_by_bank,
    get_transaction_by_key,
    get_account_history,
    get_transaction_sample,
    get_dataset_info
)

from data.analyzer import (
    calculate_risk_score,
    detect_aml_patterns,
    get_account_summary,
    detect_temporal_anomalies,
    get_high_risk_accounts
)


def test_loader_functions():
    """Test all loader.py functions"""
    print("=" * 60)
    print("TESTING LOADER FUNCTIONS")
    print("=" * 60)
    
    # Test 1: Load dataset
    print("\n1. Testing load_dataset()...")
    try:
        df = load_dataset()
        print(f"   ✓ Dataset loaded: {len(df)} transactions")
        print(f"   ✓ Columns: {list(df.columns)}")
        print(f"   ✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Get dataset info
    print("\n2. Testing get_dataset_info()...")
    try:
        info = get_dataset_info()
        print(f"   ✓ Total transactions: {info['total_transactions']}")
        print(f"   ✓ Unique accounts: {info['unique_accounts']}")
        print(f"   ✓ Unique banks: {info['unique_banks']}")
        print(f"   ✓ Laundering %: {info['laundering_percentage']:.2f}%")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Get transactions by account
    print("\n3. Testing get_transactions_by_account()...")
    try:
        # Use first account from dataset
        test_account = df['from_account'].iloc[0]
        account_txs = get_transactions_by_account(test_account)
        print(f"   ✓ Account {test_account}: {len(account_txs)} transactions")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Get transactions by bank
    print("\n4. Testing get_transactions_by_bank()...")
    try:
        test_bank = df['from_bank'].iloc[0]
        bank_txs = get_transactions_by_bank(test_bank)
        print(f"   ✓ Bank {test_bank}: {len(bank_txs)} transactions")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Get transaction by key
    print("\n5. Testing get_transaction_by_key()...")
    try:
        test_ts = df['timestamp'].iloc[0]
        test_account = df['from_account'].iloc[0]
        tx = get_transaction_by_key(test_ts.strftime('%Y/%m/%d %H:%M'), test_account)
        if tx:
            print(f"   ✓ Transaction found: ${tx['amount_paid']:.2f}")
        else:
            print(f"   ✗ Transaction not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 6: Get account history
    print("\n6. Testing get_account_history()...")
    try:
        test_account = df['from_account'].iloc[0]
        history = get_account_history(test_account, days_back=30)
        stats = history['statistics']
        print(f"   ✓ Account {test_account}:")
        print(f"      - Total transactions: {stats['total_transactions']}")
        print(f"      - Total sent: ${stats['total_sent']:.2f}")
        print(f"      - Total received: ${stats['total_received']:.2f}")
        print(f"      - Net flow: ${stats['net_flow']:.2f}")
        print(f"      - Unique counterparties: {stats['unique_counterparties']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 7: Get transaction sample
    print("\n7. Testing get_transaction_sample()...")
    try:
        sample = get_transaction_sample(n=10)
        print(f"   ✓ Sample of {len(sample)} transactions retrieved")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return True


def test_analyzer_functions():
    """Test all analyzer.py functions"""
    print("\n" + "=" * 60)
    print("TESTING ANALYZER FUNCTIONS")
    print("=" * 60)
    
    # Get a test account
    df = load_dataset()
    test_account = df['from_account'].iloc[0]
    
    # Test 1: Calculate risk score
    print("\n1. Testing calculate_risk_score()...")
    try:
        risk_score = calculate_risk_score(test_account, lookback_days=30)
        print(f"   ✓ Account {test_account} risk score: {risk_score:.3f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Detect AML patterns
    print("\n2. Testing detect_aml_patterns()...")
    try:
        patterns = detect_aml_patterns(test_account, lookback_days=30)
        print(f"   ✓ Detected {len(patterns)} AML patterns")
        for pattern in patterns:
            print(f"      - {pattern['pattern_type']}: {pattern['severity']} severity")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Get account summary
    print("\n3. Testing get_account_summary()...")
    try:
        summary = get_account_summary(test_account, lookback_days=30)
        print(f"   ✓ Account summary generated:")
        print(f"      - Risk level: {summary['risk_metrics']['risk_level']}")
        print(f"      - Risk score: {summary['risk_metrics']['risk_score']:.3f}")
        print(f"      - AML patterns: {summary['risk_metrics']['aml_patterns_detected']}")
        print(f"      - Transaction frequency: {summary['behavioral_profile']['transaction_frequency']:.2f}/day")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Detect temporal anomalies
    print("\n4. Testing detect_temporal_anomalies()...")
    try:
        test_ts = df['timestamp'].iloc[0]
        test_account = df['from_account'].iloc[0]
        anomalies = detect_temporal_anomalies(
            test_account,
            test_ts.strftime('%Y/%m/%d %H:%M'),
            lookback_days=30
        )
        print(f"   ✓ Anomaly detection completed:")
        print(f"      - Is anomalous: {anomalies['is_anomalous']}")
        print(f"      - Anomaly score: {anomalies['anomaly_score']:.3f}")
        if anomalies['anomaly_types']:
            print(f"      - Anomaly types: {', '.join(anomalies['anomaly_types'])}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Get high risk accounts
    print("\n5. Testing get_high_risk_accounts()...")
    try:
        high_risk = get_high_risk_accounts(threshold=0.5, lookback_days=30, limit=5)
        print(f"   ✓ Found {len(high_risk)} high-risk accounts (showing top 5):")
        if len(high_risk) > 0:
            for idx, row in high_risk.iterrows():
                print(f"      - {row['account_id']}: risk={row['risk_score']:.3f}, "
                      f"level={row['risk_level']}, patterns={row['aml_patterns']}")
        else:
            print(f"      (No accounts above threshold)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DATA LAYER IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    try:
        # Test loader functions
        loader_success = test_loader_functions()
        
        # Test analyzer functions
        analyzer_success = test_analyzer_functions()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Loader functions: {'✓ PASSED' if loader_success else '✗ FAILED'}")
        print(f"Analyzer functions: {'✓ PASSED' if analyzer_success else '✗ FAILED'}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob
