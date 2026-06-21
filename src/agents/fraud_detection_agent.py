"""
Fraud Detection Agent for Financial Risk Management System
Phase 4: Agent Layer Implementation

This agent detects fraud signals using temporal anomalies and laundering history.
No LLM calls - purely data-driven fraud detection.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from ..data.analyzer import detect_temporal_anomalies, AnalyzerError
from ..data.loader import (
    get_transactions_by_account,
    get_account_history,
    DataLoaderError
)


class FraudDetectionAgent:
    """
    Agent specialized in fraud detection.
    
    Uses data layer functions to:
    - Detect temporal anomalies in transactions
    - Analyze laundering history from dataset
    - Identify fraud signals and patterns
    - Generate fraud risk assessments
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the Fraud Detection Agent.
        
        Args:
            data_path: Optional path to the data file
        """
        self.data_path = data_path
        self.agent_name = "FraudDetectionAgent"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run fraud detection analysis for an account or transaction.
        
        Args:
            input_data: Dictionary containing either:
                For transaction analysis:
                - account_id (str, required): Account ID
                - timestamp (str, required): Transaction timestamp
                - lookback_days (int, optional): Days for baseline (default: 30)
                
                For account fraud profile:
                - account_id (str, required): Account ID
                - mode (str): "account_profile"
                - lookback_days (int, optional): Days to analyze (default: 90)
                
        Returns:
            Dictionary with:
                - status (str): "success" or "error"
                - result (dict): Fraud detection results if successful
                - metadata (dict): Agent execution metadata
                
        Example:
            >>> agent = FraudDetectionAgent()
            >>> result = agent.run({
            ...     "account_id": "8000EBD30",
            ...     "timestamp": "2022/09/15 14:30"
            ... })
            >>> print(result['result']['fraud_risk_level'])
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not input_data or 'account_id' not in input_data:
                return {
                    'status': 'error',
                    'result': None,
                    'metadata': {
                        'agent': self.agent_name,
                        'error': 'Missing required field: account_id',
                        'timestamp': start_time.isoformat()
                    }
                }
            
            mode = input_data.get('mode', 'transaction')
            
            if mode == 'account_profile':
                return self._run_account_profile(input_data, start_time)
            else:
                return self._run_transaction_analysis(input_data, start_time)
                
        except DataLoaderError as e:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': f"Data loader error: {str(e)}",
                    'error_type': 'DataLoaderError',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except AnalyzerError as e:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': f"Analyzer error: {str(e)}",
                    'error_type': 'AnalyzerError',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': f"Unexpected error: {str(e)}",
                    'error_type': type(e).__name__,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def _run_transaction_analysis(
        self,
        input_data: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Analyze a specific transaction for fraud signals."""
        
        # Validate required fields
        if 'timestamp' not in input_data:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': 'Missing required field: timestamp',
                    'timestamp': start_time.isoformat()
                }
            }
        
        account_id = input_data['account_id']
        timestamp = input_data['timestamp']
        lookback_days = input_data.get('lookback_days', 30)
        
        # Detect temporal anomalies
        anomaly_result = detect_temporal_anomalies(
            account_id=account_id,
            timestamp=timestamp,
            lookback_days=lookback_days,
            data_path=self.data_path
        )
        
        # Determine fraud risk level based on anomaly score
        anomaly_score = anomaly_result['anomaly_score']
        fraud_risk_level = self._calculate_fraud_risk_level(anomaly_score)
        
        # Build fraud signals list
        fraud_signals = []
        
        if anomaly_result['is_anomalous']:
            for anomaly_type in anomaly_result['anomaly_types']:
                fraud_signals.append({
                    'signal_type': anomaly_type,
                    'severity': self._map_anomaly_to_severity(anomaly_type, anomaly_score),
                    'description': self._get_anomaly_description(anomaly_type)
                })
        
        # Check for laundering history in the transaction
        details = anomaly_result.get('details', {})
        
        result = {
            'account_id': account_id,
            'timestamp': timestamp,
            'fraud_risk_level': fraud_risk_level,
            'anomaly_score': round(anomaly_score, 4),
            'is_anomalous': anomaly_result['is_anomalous'],
            'fraud_signals': fraud_signals,
            'anomaly_details': details,
            'recommendation': self._get_fraud_recommendation(fraud_risk_level, fraud_signals)
        }
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'status': 'success',
            'result': result,
            'metadata': {
                'agent': self.agent_name,
                'mode': 'transaction',
                'execution_time_seconds': round(execution_time, 3),
                'timestamp': end_time.isoformat()
            }
        }
    
    def _run_account_profile(
        self,
        input_data: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate fraud profile for an account."""
        
        account_id = input_data['account_id']
        lookback_days = input_data.get('lookback_days', 90)
        
        # Get account history
        history = get_account_history(
            account_id=account_id,
            days_back=lookback_days,
            data_path=self.data_path
        )
        
        stats = history['statistics']
        
        # Analyze laundering history
        laundering_analysis = self._analyze_laundering_history(stats)
        
        # Calculate fraud indicators
        fraud_indicators = self._calculate_fraud_indicators(stats, history)
        
        # Determine overall fraud risk
        fraud_risk_score = self._calculate_account_fraud_score(
            laundering_analysis,
            fraud_indicators
        )
        
        fraud_risk_level = self._calculate_fraud_risk_level(fraud_risk_score)
        
        result = {
            'account_id': account_id,
            'analysis_period_days': lookback_days,
            'fraud_risk_score': round(fraud_risk_score, 4),
            'fraud_risk_level': fraud_risk_level,
            'laundering_analysis': laundering_analysis,
            'fraud_indicators': fraud_indicators,
            'transaction_summary': {
                'total_transactions': stats['total_transactions'],
                'laundering_count': stats['laundering_count'],
                'laundering_percentage': round(stats['laundering_percentage'], 2)
            },
            'recommendation': self._get_fraud_recommendation(fraud_risk_level, [])
        }
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'status': 'success',
            'result': result,
            'metadata': {
                'agent': self.agent_name,
                'mode': 'account_profile',
                'execution_time_seconds': round(execution_time, 3),
                'timestamp': end_time.isoformat()
            }
        }
    
    def _analyze_laundering_history(self, stats: Dict) -> Dict[str, Any]:
        """Analyze laundering history from dataset."""
        
        laundering_count = stats['laundering_count']
        total_transactions = stats['total_transactions']
        laundering_percentage = stats['laundering_percentage']
        
        # Classify laundering severity
        if laundering_percentage >= 50:
            severity = "critical"
            assessment = "Majority of transactions flagged as laundering"
        elif laundering_percentage >= 20:
            severity = "high"
            assessment = "Significant laundering activity detected"
        elif laundering_percentage >= 5:
            severity = "medium"
            assessment = "Some laundering activity detected"
        elif laundering_percentage > 0:
            severity = "low"
            assessment = "Minimal laundering activity detected"
        else:
            severity = "none"
            assessment = "No laundering activity detected"
        
        return {
            'laundering_count': laundering_count,
            'total_transactions': total_transactions,
            'laundering_percentage': round(laundering_percentage, 2),
            'severity': severity,
            'assessment': assessment
        }
    
    def _calculate_fraud_indicators(
        self,
        stats: Dict,
        history: Dict
    ) -> List[Dict[str, Any]]:
        """Calculate fraud indicators from transaction data."""
        
        indicators = []
        
        # Indicator 1: High transaction volatility
        if stats['std_transaction_amount'] > 0:
            cv = stats['std_transaction_amount'] / stats['avg_transaction_amount']
            if cv > 1.5:
                indicators.append({
                    'indicator': 'high_volatility',
                    'severity': 'medium',
                    'description': f'High transaction amount volatility (CV: {cv:.2f})',
                    'value': round(cv, 2)
                })
        
        # Indicator 2: Unusual network complexity
        if stats['unique_counterparties'] > 30:
            indicators.append({
                'indicator': 'complex_network',
                'severity': 'medium',
                'description': f'Large number of counterparties ({stats["unique_counterparties"]})',
                'value': stats['unique_counterparties']
            })
        
        # Indicator 3: Extreme net flow
        if abs(stats['net_flow']) > stats['total_received'] * 0.8:
            indicators.append({
                'indicator': 'extreme_net_flow',
                'severity': 'low',
                'description': f'Extreme net cash flow: ${stats["net_flow"]:,.2f}',
                'value': round(stats['net_flow'], 2)
            })
        
        return indicators
    
    def _calculate_account_fraud_score(
        self,
        laundering_analysis: Dict,
        fraud_indicators: List[Dict]
    ) -> float:
        """Calculate overall fraud score for account."""
        
        # Base score from laundering percentage (0.0-0.7 weight)
        laundering_score = (laundering_analysis['laundering_percentage'] / 100.0) * 0.7
        
        # Additional score from fraud indicators (0.0-0.3 weight)
        indicator_score = 0.0
        if fraud_indicators:
            severity_weights = {'low': 0.1, 'medium': 0.15, 'high': 0.2, 'critical': 0.3}
            for indicator in fraud_indicators:
                indicator_score += severity_weights.get(indicator['severity'], 0.1)
        
        indicator_score = min(indicator_score, 0.3)
        
        return min(laundering_score + indicator_score, 1.0)
    
    def _calculate_fraud_risk_level(self, score: float) -> str:
        """Map fraud score to risk level."""
        
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    def _map_anomaly_to_severity(self, anomaly_type: str, score: float) -> str:
        """Map anomaly type and score to severity."""
        
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_anomaly_description(self, anomaly_type: str) -> str:
        """Get human-readable description for anomaly type."""
        
        descriptions = {
            'amount_anomaly': 'Transaction amount significantly deviates from historical pattern',
            'unusual_time': 'Transaction occurred at unusual time of day',
            'high_frequency_burst': 'Unusually high transaction frequency detected'
        }
        
        return descriptions.get(anomaly_type, f'Anomaly detected: {anomaly_type}')
    
    def _get_fraud_recommendation(
        self,
        risk_level: str,
        fraud_signals: List[Dict]
    ) -> str:
        """Generate fraud-specific recommendation."""
        
        if risk_level == "critical":
            return "IMMEDIATE ACTION: Freeze account and initiate fraud investigation"
        elif risk_level == "high":
            return "HIGH PRIORITY: Manual review required within 24 hours"
        elif risk_level == "medium":
            return "MEDIUM PRIORITY: Enhanced monitoring and review within 72 hours"
        elif risk_level == "low":
            return "LOW PRIORITY: Continue standard monitoring"
        else:
            return "ROUTINE: No immediate action required"


# Made with Bob