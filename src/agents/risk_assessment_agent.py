"""
Risk Assessment Agent for Financial Risk Management System
Phase 4: Agent Layer Implementation

This agent calculates risk scores and identifies high-risk accounts.
No LLM calls - purely data-driven risk assessment.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..data.analyzer import (
    calculate_risk_score,
    get_high_risk_accounts,
    AnalyzerError
)
from ..data.loader import DataLoaderError


class RiskAssessmentAgent:
    """
    Agent specialized in risk assessment and scoring.
    
    Uses data layer functions to:
    - Calculate comprehensive risk scores (0.0-1.0)
    - Identify high-risk accounts
    - Classify risk levels
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the Risk Assessment Agent.
        
        Args:
            data_path: Optional path to the data file
        """
        self.data_path = data_path
        self.agent_name = "RiskAssessmentAgent"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run risk assessment for an account or identify high-risk accounts.
        
        Args:
            input_data: Dictionary containing either:
                For single account assessment:
                - account_id (str, required): Account ID to assess
                - lookback_days (int, optional): Days to look back (default: 90)
                
                For high-risk account identification:
                - mode (str): "high_risk_scan"
                - threshold (float, optional): Risk threshold (default: 0.7)
                - lookback_days (int, optional): Days to look back (default: 90)
                - limit (int, optional): Max accounts to return (default: None)
                
        Returns:
            Dictionary with:
                - status (str): "success" or "error"
                - result (dict): Risk assessment results if successful
                - metadata (dict): Agent execution metadata
                
        Example:
            >>> agent = RiskAssessmentAgent()
            >>> result = agent.run({"account_id": "8000EBD30", "lookback_days": 90})
            >>> print(result['result']['risk_score'])
            0.73
        """
        start_time = datetime.utcnow()
        
        try:
            # Check if this is a high-risk scan mode
            mode = input_data.get('mode', 'single_account')
            
            if mode == 'high_risk_scan':
                return self._run_high_risk_scan(input_data, start_time)
            else:
                return self._run_single_assessment(input_data, start_time)
                
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
    
    def _run_single_assessment(
        self,
        input_data: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Run risk assessment for a single account."""
        
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
        
        # Calculate risk score
        risk_score = calculate_risk_score(
            account_id=account_id,
            lookback_days=lookback_days,
            data_path=self.data_path
        )
        
        # Determine risk level and classification
        risk_classification = self._classify_risk(risk_score)
        
        # Build result
        result = {
            'account_id': account_id,
            'risk_score': round(risk_score, 4),
            'risk_level': risk_classification['level'],
            'risk_category': risk_classification['category'],
            'risk_description': risk_classification['description'],
            'analysis_period_days': lookback_days,
            'requires_action': risk_classification['requires_action'],
            'priority': risk_classification['priority']
        }
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'status': 'success',
            'result': result,
            'metadata': {
                'agent': self.agent_name,
                'mode': 'single_account',
                'execution_time_seconds': round(execution_time, 3),
                'timestamp': end_time.isoformat()
            }
        }
    
    def _run_high_risk_scan(
        self,
        input_data: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Scan for high-risk accounts across the dataset."""
        
        threshold = input_data.get('threshold', 0.7)
        lookback_days = input_data.get('lookback_days', 90)
        limit = input_data.get('limit', None)
        
        # Validate threshold
        if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': 'threshold must be between 0.0 and 1.0',
                    'timestamp': start_time.isoformat()
                }
            }
        
        # Get high-risk accounts
        high_risk_df = get_high_risk_accounts(
            threshold=threshold,
            lookback_days=lookback_days,
            limit=limit,
            data_path=self.data_path
        )
        
        # Convert DataFrame to list of dicts
        high_risk_accounts = high_risk_df.to_dict('records') if len(high_risk_df) > 0 else []
        
        # Add risk classifications
        for account in high_risk_accounts:
            classification = self._classify_risk(account['risk_score'])
            account['risk_category'] = classification['category']
            account['risk_description'] = classification['description']
            account['requires_action'] = classification['requires_action']
            account['priority'] = classification['priority']
        
        # Calculate summary statistics
        summary_stats = {
            'total_high_risk_accounts': len(high_risk_accounts),
            'threshold_used': threshold,
            'analysis_period_days': lookback_days
        }
        
        if high_risk_accounts:
            risk_scores = [acc['risk_score'] for acc in high_risk_accounts]
            summary_stats.update({
                'avg_risk_score': round(sum(risk_scores) / len(risk_scores), 4),
                'max_risk_score': round(max(risk_scores), 4),
                'min_risk_score': round(min(risk_scores), 4),
                'critical_count': sum(1 for acc in high_risk_accounts if acc['risk_level'] == 'critical'),
                'high_count': sum(1 for acc in high_risk_accounts if acc['risk_level'] == 'high'),
                'medium_count': sum(1 for acc in high_risk_accounts if acc['risk_level'] == 'medium')
            })
        
        result = {
            'high_risk_accounts': high_risk_accounts,
            'summary': summary_stats
        }
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'status': 'success',
            'result': result,
            'metadata': {
                'agent': self.agent_name,
                'mode': 'high_risk_scan',
                'execution_time_seconds': round(execution_time, 3),
                'timestamp': end_time.isoformat(),
                'accounts_analyzed': len(high_risk_accounts)
            }
        }
    
    def _classify_risk(self, risk_score: float) -> Dict[str, Any]:
        """
        Classify risk score into categories with descriptions.
        
        Args:
            risk_score: Risk score between 0.0 and 1.0
            
        Returns:
            Dictionary with risk classification details
        """
        if risk_score >= 0.8:
            return {
                'level': 'critical',
                'category': 'CRITICAL_RISK',
                'description': 'Immediate action required - high probability of illicit activity',
                'requires_action': True,
                'priority': 'immediate'
            }
        elif risk_score >= 0.6:
            return {
                'level': 'high',
                'category': 'HIGH_RISK',
                'description': 'Enhanced monitoring required - significant risk indicators present',
                'requires_action': True,
                'priority': 'high'
            }
        elif risk_score >= 0.4:
            return {
                'level': 'medium',
                'category': 'MEDIUM_RISK',
                'description': 'Increased monitoring recommended - some risk indicators present',
                'requires_action': True,
                'priority': 'medium'
            }
        elif risk_score >= 0.2:
            return {
                'level': 'low',
                'category': 'LOW_RISK',
                'description': 'Standard monitoring sufficient - minimal risk indicators',
                'requires_action': False,
                'priority': 'low'
            }
        else:
            return {
                'level': 'minimal',
                'category': 'MINIMAL_RISK',
                'description': 'Normal activity - no significant risk indicators',
                'requires_action': False,
                'priority': 'routine'
            }


# Made with Bob