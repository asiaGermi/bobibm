"""
Recommendation Agent for Financial Risk Management System
Phase 4: Agent Layer Implementation

This agent generates structured action recommendations based on risk scores and detected patterns.
No LLM calls - purely rule-based recommendation engine.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from ..data.analyzer import (
    calculate_risk_score,
    detect_aml_patterns,
    get_account_summary,
    AnalyzerError
)
from ..data.loader import DataLoaderError


class RecommendationAgent:
    """
    Agent specialized in generating action recommendations.
    
    Generates structured recommendations with actions:
    - ALERT: Notify compliance team
    - REVIEW: Manual review required
    - BLOCK: Block account transactions
    - MONITOR: Enhanced monitoring
    
    Based on risk scores and detected AML patterns.
    """
    
    # Action types
    ACTION_ALERT = "ALERT"
    ACTION_REVIEW = "REVIEW"
    ACTION_BLOCK = "BLOCK"
    ACTION_MONITOR = "MONITOR"
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the Recommendation Agent.
        
        Args:
            data_path: Optional path to the data file
        """
        self.data_path = data_path
        self.agent_name = "RecommendationAgent"
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate action recommendations for an account.
        
        Args:
            input_data: Dictionary containing:
                - account_id (str, required): Account ID to analyze
                - risk_score (float, optional): Pre-calculated risk score
                - lookback_days (int, optional): Days to look back (default: 90)
                - include_evidence (bool, optional): Include detailed evidence (default: True)
                
        Returns:
            Dictionary with:
                - status (str): "success" or "error"
                - result (dict): Recommendations if successful
                - metadata (dict): Agent execution metadata
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
            include_evidence = input_data.get('include_evidence', True)
            
            # Get or calculate risk score
            if 'risk_score' in input_data and input_data['risk_score'] is not None:
                risk_score = float(input_data['risk_score'])
            else:
                risk_score = calculate_risk_score(
                    account_id=account_id,
                    lookback_days=lookback_days,
                    data_path=self.data_path
                )
            
            # Detect AML patterns
            aml_patterns = detect_aml_patterns(
                account_id=account_id,
                lookback_days=lookback_days,
                data_path=self.data_path
            )
            
            # Get account summary
            summary = get_account_summary(
                account_id=account_id,
                lookback_days=lookback_days,
                data_path=self.data_path
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_score, aml_patterns, summary, include_evidence
            )
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            result = {
                'account_id': account_id,
                'risk_score': round(risk_score, 4),
                'risk_level': risk_level,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations)
            }
            
            end_time = datetime.utcnow()
            
            return {
                'status': 'success',
                'result': result,
                'metadata': {
                    'agent': self.agent_name,
                    'execution_time_seconds': round((end_time - start_time).total_seconds(), 3),
                    'timestamp': end_time.isoformat()
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def _generate_recommendations(
        self, risk_score: float, aml_patterns: List[Dict],
        summary: Dict, include_evidence: bool
    ) -> List[Dict[str, Any]]:
        """Generate structured recommendations."""
        recommendations = []
        
        # Critical risk
        if risk_score >= 0.8:
            recommendations.append({
                'action': self.ACTION_BLOCK,
                'priority': 'critical',
                'reason': f'Critical risk score of {risk_score:.2f}',
                'description': 'Freeze account transactions immediately'
            })
        
        # High risk
        elif risk_score >= 0.6:
            recommendations.append({
                'action': self.ACTION_REVIEW,
                'priority': 'high',
                'reason': f'High risk score of {risk_score:.2f}',
                'description': 'Enhanced due diligence required'
            })
        
        # Pattern-specific recommendations
        for pattern in aml_patterns:
            if pattern['pattern_type'] == 'smurfing':
                recommendations.append({
                    'action': self.ACTION_REVIEW,
                    'priority': pattern['severity'],
                    'reason': pattern['description'],
                    'description': 'Investigate structuring activity'
                })
        
        return recommendations


# Made with Bob