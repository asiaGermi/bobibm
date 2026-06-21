"""
Transaction Analysis Agent for Financial Risk Management System
Phase 4: Agent Layer Implementation

This agent analyzes transaction patterns for an account using data layer functions.
No LLM calls - purely data-driven analysis.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..data.loader import get_account_history, DataLoaderError
from ..data.analyzer import detect_aml_patterns, AnalyzerError


class TransactionAnalysisAgent:
    """
    Agent specialized in analyzing transaction patterns for accounts.
    
    Uses data layer functions to:
    - Retrieve account transaction history
    - Detect AML patterns (fan-out, fan-in, circular, smurfing)
    - Analyze transaction statistics
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the Transaction Analysis Agent.
        
        Args:
            data_path: Optional path to the data file
        """
        self.data_path = data_path
        self.agent_name = "TransactionAnalysisAgent"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run transaction analysis for an account.
        
        Args:
            input_data: Dictionary containing:
                - account_id (str, required): Account ID to analyze
                - lookback_days (int, optional): Days to look back (default: 90)
                
        Returns:
            Dictionary with:
                - status (str): "success" or "error"
                - result (dict): Analysis results if successful
                - metadata (dict): Agent execution metadata
                
        Example:
            >>> agent = TransactionAnalysisAgent()
            >>> result = agent.run({"account_id": "8000EBD30", "lookback_days": 90})
            >>> print(result['status'])
            success
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
            
            account_id = input_data['account_id']
            lookback_days = input_data.get('lookback_days', 90)
            
            # Validate lookback_days
            if not isinstance(lookback_days, int) or lookback_days < 1:
                return {
                    'status': 'error',
                    'result': None,
                    'metadata': {
                        'agent': self.agent_name,
                        'error': 'lookback_days must be a positive integer',
                        'timestamp': start_time.isoformat()
                    }
                }
            
            # Get account history
            history = get_account_history(
                account_id=account_id,
                days_back=lookback_days,
                data_path=self.data_path
            )
            
            # Detect AML patterns
            aml_patterns = detect_aml_patterns(
                account_id=account_id,
                lookback_days=lookback_days,
                data_path=self.data_path
            )
            
            # Analyze transaction patterns
            stats = history['statistics']
            
            # Calculate additional insights
            transaction_velocity = stats['total_transactions'] / lookback_days
            
            # Determine transaction behavior
            if stats['sent_count'] > stats['received_count'] * 2:
                behavior = "high_outflow"
            elif stats['received_count'] > stats['sent_count'] * 2:
                behavior = "high_inflow"
            else:
                behavior = "balanced"
            
            # Categorize payment format preferences
            payment_format_analysis = {}
            if stats['payment_formats']:
                total_txs = sum(stats['payment_formats'].values())
                for format_type, count in stats['payment_formats'].items():
                    payment_format_analysis[format_type] = {
                        'count': count,
                        'percentage': (count / total_txs * 100) if total_txs > 0 else 0
                    }
            
            # Build comprehensive result
            result = {
                'account_id': account_id,
                'analysis_period': {
                    'days': lookback_days,
                    'date_range': history['date_range']
                },
                'transaction_summary': {
                    'total_transactions': stats['total_transactions'],
                    'sent_count': stats['sent_count'],
                    'received_count': stats['received_count'],
                    'transaction_velocity': round(transaction_velocity, 2),
                    'behavior_type': behavior
                },
                'financial_summary': {
                    'total_sent': round(stats['total_sent'], 2),
                    'total_received': round(stats['total_received'], 2),
                    'net_flow': round(stats['net_flow'], 2),
                    'avg_transaction': round(stats['avg_transaction_amount'], 2),
                    'median_transaction': round(stats['median_transaction_amount'], 2),
                    'std_transaction': round(stats['std_transaction_amount'], 2),
                    'max_transaction': round(stats['max_transaction'], 2),
                    'min_transaction': round(stats['min_transaction'], 2)
                },
                'risk_indicators': {
                    'laundering_count': stats['laundering_count'],
                    'laundering_percentage': round(stats['laundering_percentage'], 2),
                    'unique_counterparties': stats['unique_counterparties'],
                    'aml_patterns_detected': len(aml_patterns)
                },
                'aml_patterns': aml_patterns,
                'payment_format_analysis': payment_format_analysis
            }
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                'status': 'success',
                'result': result,
                'metadata': {
                    'agent': self.agent_name,
                    'execution_time_seconds': round(execution_time, 3),
                    'timestamp': end_time.isoformat(),
                    'data_points_analyzed': stats['total_transactions']
                }
            }
            
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


# Made with Bob