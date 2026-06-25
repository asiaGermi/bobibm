"""
Data Analyzer Module for Financial Risk Management System
Phase 2: Data Layer Implementation - Analysis Functions

This module provides advanced analysis functions for risk scoring, AML pattern detection,
and anomaly identification in transaction data.

Functions:
- calculate_risk_score: Calculate risk score for an account (0.0-1.0)
- detect_aml_patterns: Detect anti-money laundering patterns
- get_account_summary: Get comprehensive account statistics
- detect_temporal_anomalies: Detect time-based anomalies
- get_high_risk_accounts: Identify high-risk accounts
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import pandas as pd
import numpy as np

from .loader import (
    load_dataset,
    get_transactions_by_account,
    get_account_history,
    DataLoaderError
)


# Risk scoring weights and thresholds
RISK_WEIGHTS = {
    'transaction_frequency': 0.20,
    'amount_anomaly': 0.25,
    'high_risk_currency': 0.15,
    'laundering_history': 0.30,
    'network_complexity': 0.10
}

HIGH_RISK_CURRENCIES = {'Bitcoin', 'Cryptocurrency', 'Offshore Currency'}
STRUCTURING_THRESHOLD = 10000.0  # Typical threshold for structuring detection
ANOMALY_STD_MULTIPLIER = 2.5  # Standard deviations for anomaly detection


class AnalyzerError(Exception):
    """Base exception for analyzer errors"""
    pass


def calculate_risk_score(
    account_id: str,
    lookback_days: int = 90,
    data_path: Optional[str] = None
) -> float:
    """
    Calculate comprehensive risk score for an account (0.0-1.0).
    
    Risk factors considered:
    - Transaction frequency (unusual activity patterns)
    - Amount anomalies (transactions significantly above/below normal)
    - High-risk currencies usage
    - Historical laundering flags (Is_Laundering field)
    - Network complexity (number of unique counterparties)
    
    Args:
        account_id: The account ID to analyze
        lookback_days: Number of days to analyze (default: 90)
        data_path: Optional path to the CSV file
        
    Returns:
        float: Risk score between 0.0 (low risk) and 1.0 (high risk)
        
    Raises:
        AnalyzerError: If there's an error calculating risk score
        
    Example:
        >>> risk = calculate_risk_score("8000EBD30")
        >>> print(f"Risk score: {risk:.2f}")
        Risk score: 0.73
    """
    try:
        # Get account history
        history = get_account_history(account_id, days_back=lookback_days, data_path=data_path)
        stats = history['statistics']
        transactions = history['transactions']
        
        if stats['total_transactions'] == 0:
            return 0.0  # No transactions = no risk data
        
        # Factor 1: Transaction frequency risk (normalized)
        # High frequency can indicate suspicious activity
        daily_avg = stats['total_transactions'] / lookback_days
        frequency_risk = min(daily_avg / 100.0, 1.0)  # Cap at 100 transactions/day
        
        # Factor 2: Amount anomaly risk
        # Check for unusual transaction amounts
        amount_risk = 0.0
        if stats['std_transaction_amount'] > 0:
            # Calculate coefficient of variation (CV)
            cv = stats['std_transaction_amount'] / stats['avg_transaction_amount']
            amount_risk = min(cv / 2.0, 1.0)  # High variance = higher risk
        
        # Factor 3: High-risk currency usage
        currency_risk = 0.0
        df = load_dataset(data_path)
        account_txs = df[
            (df['from_account'] == str(account_id)) | 
            (df['to_account'] == str(account_id))
        ]
        if len(account_txs) > 0:
            high_risk_count = account_txs[
                account_txs['payment_currency'].isin(HIGH_RISK_CURRENCIES)
            ].shape[0]
            currency_risk = high_risk_count / len(account_txs)
        
        # Factor 4: Historical laundering flags (most important)
        laundering_risk = stats['laundering_percentage'] / 100.0

        # Factor 5: Network complexity risk
        # Many unique counterparties can indicate layering
        network_risk = min(stats['unique_counterparties'] / 50.0, 1.0)

        # Bonus: 100% high-risk currency + extreme fan-out is a strong
        # laundering signal even without explicit dataset flags (e.g. Bitcoin
        # dispersed to 1000+ recipients). Capped at 0.15 additional points.
        crypto_fanout_bonus = 0.0
        if currency_risk == 1.0 and stats['unique_counterparties'] > 200:
            crypto_fanout_bonus = min((stats['unique_counterparties'] - 200) / 1000.0, 0.15)

        # Calculate weighted risk score
        risk_score = (
            RISK_WEIGHTS['transaction_frequency'] * frequency_risk +
            RISK_WEIGHTS['amount_anomaly'] * amount_risk +
            RISK_WEIGHTS['high_risk_currency'] * currency_risk +
            RISK_WEIGHTS['laundering_history'] * laundering_risk +
            RISK_WEIGHTS['network_complexity'] * network_risk +
            crypto_fanout_bonus
        )

        return min(max(risk_score, 0.0), 1.0)  # Ensure 0.0-1.0 range
        
    except Exception as e:
        raise AnalyzerError(f"Error calculating risk score for account {account_id}: {str(e)}")


def detect_aml_patterns(
    account_id: str,
    lookback_days: int = 90,
    data_path: Optional[str] = None
) -> List[Dict]:
    """
    Detect Anti-Money Laundering patterns in account transactions.
    
    Patterns detected:
    - Fan-out: One account sending to many accounts (placement)
    - Fan-in: Many accounts sending to one account (integration)
    - Circular transactions: Money flowing back to source
    - Smurfing/Structuring: Multiple transactions just below reporting threshold
    
    Args:
        account_id: The account ID to analyze
        lookback_days: Number of days to analyze (default: 90)
        data_path: Optional path to the CSV file
        
    Returns:
        List[dict]: List of detected patterns with details:
            - pattern_type: Type of pattern detected
            - severity: "low", "medium", "high", "critical"
            - confidence: Confidence score (0.0-1.0)
            - description: Human-readable description
            - evidence: Supporting data
            
    Example:
        >>> patterns = detect_aml_patterns("8000EBD30")
        >>> for p in patterns:
        ...     print(f"{p['pattern_type']}: {p['severity']}")
    """
    patterns = []
    
    try:
        df = load_dataset(data_path)
        
        # Get account transactions within lookback period
        max_date = df['timestamp'].max()
        start_date = max_date - timedelta(days=lookback_days)
        
        account_txs = df[
            ((df['from_account'] == str(account_id)) | (df['to_account'] == str(account_id))) &
            (df['timestamp'] >= start_date)
        ].copy()
        
        if len(account_txs) == 0:
            return patterns
        
        # Pattern 1: Fan-out detection (placement phase)
        outgoing = account_txs[account_txs['from_account'] == str(account_id)]
        if len(outgoing) > 0:
            unique_recipients = outgoing['to_account'].nunique()
            if unique_recipients >= 10:
                severity = "high" if unique_recipients >= 20 else "medium"
                patterns.append({
                    'pattern_type': 'fan-out',
                    'severity': severity,
                    'confidence': min(unique_recipients / 30.0, 1.0),
                    'description': f'Account sent funds to {unique_recipients} different accounts',
                    'evidence': {
                        'unique_recipients': unique_recipients,
                        'total_outgoing': len(outgoing),
                        'total_amount': float(outgoing['amount_paid'].sum())
                    }
                })
        
        # Pattern 2: Fan-in detection (integration phase)
        incoming = account_txs[account_txs['to_account'] == str(account_id)]
        if len(incoming) > 0:
            unique_senders = incoming['from_account'].nunique()
            if unique_senders >= 10:
                severity = "high" if unique_senders >= 20 else "medium"
                patterns.append({
                    'pattern_type': 'fan-in',
                    'severity': severity,
                    'confidence': min(unique_senders / 30.0, 1.0),
                    'description': f'Account received funds from {unique_senders} different accounts',
                    'evidence': {
                        'unique_senders': unique_senders,
                        'total_incoming': len(incoming),
                        'total_amount': float(incoming['amount_received'].sum())
                    }
                })
        
        # Pattern 3: Circular transactions
        if len(outgoing) > 0 and len(incoming) > 0:
            # Check if any recipient also sent money back
            recipients = set(outgoing['to_account'].unique())
            senders = set(incoming['from_account'].unique())
            circular_accounts = recipients & senders
            
            if len(circular_accounts) > 0:
                severity = "critical" if len(circular_accounts) >= 5 else "high"
                patterns.append({
                    'pattern_type': 'circular',
                    'severity': severity,
                    'confidence': min(len(circular_accounts) / 10.0, 1.0),
                    'description': f'Detected circular money flow with {len(circular_accounts)} accounts',
                    'evidence': {
                        'circular_accounts': len(circular_accounts),
                        'accounts': list(circular_accounts)[:10]  # Limit to 10 for brevity
                    }
                })
        
        # Pattern 4: Smurfing/Structuring detection
        # Multiple transactions just below threshold
        if len(outgoing) > 0:
            # Transactions between 90% and 99% of threshold
            near_threshold = outgoing[
                (outgoing['amount_paid'] >= STRUCTURING_THRESHOLD * 0.90) &
                (outgoing['amount_paid'] < STRUCTURING_THRESHOLD)
            ]
            
            if len(near_threshold) >= 3:
                # Group by day to detect same-day structuring
                near_threshold['date'] = near_threshold['timestamp'].dt.date
                daily_counts = near_threshold.groupby('date').size()
                max_daily = daily_counts.max() if len(daily_counts) > 0 else 0
                
                if max_daily >= 2:
                    severity = "critical" if max_daily >= 5 else "high"
                    patterns.append({
                        'pattern_type': 'smurfing',
                        'severity': severity,
                        'confidence': min(len(near_threshold) / 10.0, 1.0),
                        'description': f'Detected {len(near_threshold)} transactions just below ${STRUCTURING_THRESHOLD:,.0f} threshold',
                        'evidence': {
                            'suspicious_transactions': len(near_threshold),
                            'max_same_day': int(max_daily),
                            'threshold': STRUCTURING_THRESHOLD,
                            'avg_amount': float(near_threshold['amount_paid'].mean())
                        }
                    })
        
        return patterns
        
    except Exception as e:
        raise AnalyzerError(f"Error detecting AML patterns for account {account_id}: {str(e)}")


def get_account_summary(
    account_id: str,
    lookback_days: int = 90,
    data_path: Optional[str] = None
) -> Dict:
    """
    Get comprehensive account summary with aggregated statistics.
    
    Args:
        account_id: The account ID to summarize
        lookback_days: Number of days to analyze (default: 90)
        data_path: Optional path to the CSV file
        
    Returns:
        dict: Comprehensive account summary including:
            - basic_info: Account ID and analysis period
            - transaction_stats: Transaction counts and amounts
            - risk_metrics: Risk score and AML patterns
            - behavioral_profile: Transaction patterns and preferences
            - network_analysis: Counterparty information
            
    Example:
        >>> summary = get_account_summary("8000EBD30")
        >>> print(f"Risk level: {summary['risk_metrics']['risk_level']}")
    """
    try:
        # Get base history
        history = get_account_history(account_id, days_back=lookback_days, data_path=data_path)
        
        # Calculate risk score
        risk_score = calculate_risk_score(account_id, lookback_days, data_path)
        
        # Detect AML patterns
        aml_patterns = detect_aml_patterns(account_id, lookback_days, data_path)
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Build comprehensive summary
        summary = {
            'basic_info': {
                'account_id': account_id,
                'analysis_period_days': lookback_days,
                'date_range': history['date_range']
            },
            'transaction_stats': history['statistics'],
            'risk_metrics': {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'aml_patterns_detected': len(aml_patterns),
                'aml_patterns': aml_patterns
            },
            'behavioral_profile': {
                'primary_payment_format': max(
                    history['statistics']['payment_formats'].items(),
                    key=lambda x: x[1]
                )[0] if history['statistics']['payment_formats'] else None,
                'transaction_frequency': history['statistics']['total_transactions'] / lookback_days,
                'avg_transaction_size': history['statistics']['avg_transaction_amount'],
                'transaction_volatility': history['statistics']['std_transaction_amount']
            },
            'network_analysis': {
                'unique_counterparties': history['statistics']['unique_counterparties'],
                'network_density': min(
                    history['statistics']['unique_counterparties'] / 
                    max(history['statistics']['total_transactions'], 1),
                    1.0
                )
            }
        }
        
        return summary
        
    except Exception as e:
        raise AnalyzerError(f"Error generating account summary for {account_id}: {str(e)}")


def detect_temporal_anomalies(
    account_id: str,
    timestamp: str,
    lookback_days: int = 30,
    data_path: Optional[str] = None
) -> Dict:
    """
    Detect temporal anomalies for a specific transaction.
    
    Analyzes if a transaction at a given timestamp is anomalous compared to
    the account's historical behavior patterns.
    
    Args:
        account_id: The account ID to analyze
        timestamp: Transaction timestamp to check (ISO format or 'YYYY/MM/DD HH:MM')
        lookback_days: Days of history to use for baseline (default: 30)
        data_path: Optional path to the CSV file
        
    Returns:
        dict: Anomaly detection results:
            - is_anomalous: Boolean indicating if anomaly detected
            - anomaly_score: Score from 0.0 (normal) to 1.0 (highly anomalous)
            - anomaly_types: List of detected anomaly types
            - details: Detailed analysis
            
    Example:
        >>> result = detect_temporal_anomalies("8000EBD30", "2022/09/15 14:30")
        >>> if result['is_anomalous']:
        ...     print(f"Anomaly detected: {result['anomaly_types']}")
    """
    try:
        df = load_dataset(data_path)
        
        # Parse target timestamp
        if 'T' in timestamp:
            target_ts = pd.to_datetime(timestamp)
        else:
            target_ts = pd.to_datetime(timestamp, format='%Y/%m/%d %H:%M')
        
        # Get historical transactions (before target timestamp)
        historical = df[
            ((df['from_account'] == str(account_id)) | (df['to_account'] == str(account_id))) &
            (df['timestamp'] < target_ts) &
            (df['timestamp'] >= target_ts - timedelta(days=lookback_days))
        ].copy()
        
        # Get target transaction
        target_tx = df[
            ((df['from_account'] == str(account_id)) | (df['to_account'] == str(account_id))) &
            (df['timestamp'] == target_ts)
        ]
        
        if len(target_tx) == 0:
            return {
                'is_anomalous': False,
                'anomaly_score': 0.0,
                'anomaly_types': [],
                'details': {'error': 'Transaction not found at specified timestamp'}
            }
        
        if len(historical) < 5:
            return {
                'is_anomalous': False,
                'anomaly_score': 0.0,
                'anomaly_types': [],
                'details': {'warning': 'Insufficient historical data for anomaly detection'}
            }
        
        target_tx = target_tx.iloc[0]
        anomaly_types = []
        anomaly_scores = []
        
        # Anomaly 1: Amount anomaly
        is_outgoing = target_tx['from_account'] == str(account_id)
        target_amount = target_tx['amount_paid'] if is_outgoing else target_tx['amount_received']
        
        hist_amounts = pd.concat([
            historical[historical['from_account'] == str(account_id)]['amount_paid'],
            historical[historical['to_account'] == str(account_id)]['amount_received']
        ])
        
        if len(hist_amounts) > 0:
            mean_amount = hist_amounts.mean()
            std_amount = hist_amounts.std()
            
            if std_amount > 0:
                z_score = abs((target_amount - mean_amount) / std_amount)
                if z_score > ANOMALY_STD_MULTIPLIER:
                    anomaly_types.append('amount_anomaly')
                    anomaly_scores.append(min(z_score / 5.0, 1.0))
        
        # Anomaly 2: Time-of-day anomaly
        target_hour = target_ts.hour
        hist_hours = historical['timestamp'].dt.hour
        hour_counts = hist_hours.value_counts()
        
        if target_hour not in hour_counts.index or hour_counts[target_hour] < len(historical) * 0.05:
            anomaly_types.append('unusual_time')
            anomaly_scores.append(0.6)
        
        # Anomaly 3: Frequency anomaly (burst detection)
        # Check transactions in 1-hour window
        window_start = target_ts - timedelta(hours=1)
        window_txs = historical[
            (historical['timestamp'] >= window_start) &
            (historical['timestamp'] <= target_ts)
        ]
        
        if len(window_txs) > 10:  # More than 10 transactions in 1 hour
            anomaly_types.append('high_frequency_burst')
            anomaly_scores.append(min(len(window_txs) / 20.0, 1.0))
        
        # Calculate overall anomaly score
        overall_score = max(anomaly_scores) if anomaly_scores else 0.0
        is_anomalous = overall_score > 0.5
        
        return {
            'is_anomalous': is_anomalous,
            'anomaly_score': overall_score,
            'anomaly_types': anomaly_types,
            'details': {
                'target_timestamp': target_ts.isoformat(),
                'target_amount': float(target_amount),
                'historical_mean_amount': float(mean_amount) if len(hist_amounts) > 0 else 0.0,
                'historical_std_amount': float(std_amount) if len(hist_amounts) > 0 else 0.0,
                'target_hour': target_hour,
                'transactions_in_hour_window': len(window_txs),
                'historical_transactions': len(historical)
            }
        }
        
    except Exception as e:
        raise AnalyzerError(f"Error detecting temporal anomalies: {str(e)}")


def get_high_risk_accounts(
    threshold: float = 0.7,
    lookback_days: int = 90,
    limit: Optional[int] = None,
    data_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Identify high-risk accounts based on risk score threshold.
    
    Args:
        threshold: Minimum risk score to be considered high-risk (default: 0.7)
        lookback_days: Days of history to analyze (default: 90)
        limit: Maximum number of accounts to return (default: None = all)
        data_path: Optional path to the CSV file
        
    Returns:
        pd.DataFrame: High-risk accounts with columns:
            - account_id: Account identifier
            - risk_score: Calculated risk score
            - risk_level: Risk classification
            - total_transactions: Number of transactions
            - laundering_count: Number of flagged transactions
            - aml_patterns: Number of AML patterns detected
            
    Example:
        >>> high_risk = get_high_risk_accounts(threshold=0.7)
        >>> print(f"Found {len(high_risk)} high-risk accounts")
    """
    try:
        df = load_dataset(data_path)
        
        # Get all unique accounts
        all_accounts = set(df['from_account'].unique()) | set(df['to_account'].unique())
        
        high_risk_data = []
        
        for account_id in all_accounts:
            try:
                # Calculate risk score
                risk_score = calculate_risk_score(account_id, lookback_days, data_path)
                
                if risk_score >= threshold:
                    # Get additional details
                    history = get_account_history(account_id, days_back=lookback_days, data_path=data_path)
                    aml_patterns = detect_aml_patterns(account_id, lookback_days, data_path)
                    
                    # Determine risk level
                    if risk_score >= 0.8:
                        risk_level = "critical"
                    elif risk_score >= 0.6:
                        risk_level = "high"
                    else:
                        risk_level = "medium"
                    
                    high_risk_data.append({
                        'account_id': account_id,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'total_transactions': history['statistics']['total_transactions'],
                        'laundering_count': history['statistics']['laundering_count'],
                        'laundering_percentage': history['statistics']['laundering_percentage'],
                        'aml_patterns': len(aml_patterns),
                        'unique_counterparties': history['statistics']['unique_counterparties'],
                        'total_volume': history['statistics']['total_sent'] + history['statistics']['total_received']
                    })
            except Exception:
                # Skip accounts that cause errors
                continue
        
        # Convert to DataFrame
        result_df = pd.DataFrame(high_risk_data)
        
        if len(result_df) > 0:
            # Sort by risk score descending
            result_df = result_df.sort_values('risk_score', ascending=False)
            
            # Apply limit if specified
            if limit is not None:
                result_df = result_df.head(limit)
        
        return result_df
        
    except Exception as e:
        raise AnalyzerError(f"Error identifying high-risk accounts: {str(e)}")

# Made with Bob
