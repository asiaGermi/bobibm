"""
Agent Orchestrator for Financial Risk Management API
Phase 4: Agent Integration Layer

This module coordinates agent calls and handles errors gracefully.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from ..agents import (
    TransactionAnalysisAgent,
    RiskAssessmentAgent,
    RecommendationAgent,
    FraudDetectionAgent,
    ExplanationAgent
)


class AgentOrchestrator:
    """
    Orchestrates multiple agent calls and handles errors gracefully.
    
    Ensures that if one agent fails, others can still execute and
    partial results are returned to the API caller.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the orchestrator with all agents.
        
        Args:
            data_path: Optional path to the data file
        """
        self.data_path = data_path
        self.transaction_agent = TransactionAnalysisAgent(data_path)
        self.risk_agent = RiskAssessmentAgent(data_path)
        self.recommendation_agent = RecommendationAgent(data_path)
        self.fraud_agent = FraudDetectionAgent(data_path)
    
    def analyze_transaction(
        self,
        account_id: str,
        timestamp: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Orchestrate transaction analysis using TransactionAnalysisAgent.
        
        Args:
            account_id: Account ID to analyze
            timestamp: Transaction timestamp
            lookback_days: Days to look back for analysis
            
        Returns:
            Dictionary with analysis results and any errors
        """
        result = {
            'account_id': account_id,
            'timestamp': timestamp,
            'analysis': None,
            'errors': []
        }
        
        # Run transaction analysis agent
        try:
            agent_result = self.transaction_agent.run({
                'account_id': account_id,
                'lookback_days': lookback_days
            })
            
            if agent_result['status'] == 'success':
                result['analysis'] = agent_result['result']
            else:
                result['errors'].append({
                    'agent': 'TransactionAnalysisAgent',
                    'error': agent_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'TransactionAnalysisAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        return result
    
    def assess_risk_with_fraud(
        self,
        account_id: str,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Orchestrate risk assessment combining RiskAssessmentAgent and FraudDetectionAgent.
        
        Args:
            account_id: Account ID to assess
            lookback_days: Days to look back for analysis
            
        Returns:
            Dictionary with combined risk and fraud assessment results
        """
        result = {
            'account_id': account_id,
            'risk_assessment': None,
            'fraud_detection': None,
            'combined_score': None,
            'combined_level': None,
            'errors': []
        }
        
        # Run risk assessment agent
        risk_score = None
        try:
            risk_result = self.risk_agent.run({
                'account_id': account_id,
                'lookback_days': lookback_days
            })
            
            if risk_result['status'] == 'success':
                result['risk_assessment'] = risk_result['result']
                risk_score = risk_result['result']['risk_score']
            else:
                result['errors'].append({
                    'agent': 'RiskAssessmentAgent',
                    'error': risk_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'RiskAssessmentAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        # Run fraud detection agent (account profile mode)
        fraud_score = None
        try:
            fraud_result = self.fraud_agent.run({
                'account_id': account_id,
                'mode': 'account_profile',
                'lookback_days': lookback_days
            })
            
            if fraud_result['status'] == 'success':
                result['fraud_detection'] = fraud_result['result']
                fraud_score = fraud_result['result']['fraud_risk_score']
            else:
                result['errors'].append({
                    'agent': 'FraudDetectionAgent',
                    'error': fraud_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'FraudDetectionAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        # Combine scores if both are available
        if risk_score is not None and fraud_score is not None:
            # Weighted average: 60% risk score, 40% fraud score
            combined_score = (risk_score * 0.6) + (fraud_score * 0.4)
            result['combined_score'] = round(combined_score, 4)
            
            # Determine combined level
            if combined_score >= 0.8:
                result['combined_level'] = 'critical'
            elif combined_score >= 0.6:
                result['combined_level'] = 'high'
            elif combined_score >= 0.4:
                result['combined_level'] = 'medium'
            else:
                result['combined_level'] = 'low'
        elif risk_score is not None:
            # Use risk score only
            result['combined_score'] = risk_score
            result['combined_level'] = result['risk_assessment']['risk_level']
        elif fraud_score is not None:
            # Use fraud score only
            result['combined_score'] = fraud_score
            result['combined_level'] = result['fraud_detection']['fraud_risk_level']
        
        return result
    
    def generate_recommendations(
        self,
        account_id: str,
        risk_score: Optional[float] = None,
        lookback_days: int = 90,
        include_evidence: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate recommendation generation using RecommendationAgent.
        
        Args:
            account_id: Account ID for recommendations
            risk_score: Pre-calculated risk score (optional)
            lookback_days: Days to look back for analysis
            include_evidence: Whether to include detailed evidence
            
        Returns:
            Dictionary with recommendations and any errors
        """
        result = {
            'account_id': account_id,
            'recommendations': None,
            'errors': []
        }
        
        # Run recommendation agent
        try:
            agent_input = {
                'account_id': account_id,
                'lookback_days': lookback_days,
                'include_evidence': include_evidence
            }
            
            if risk_score is not None:
                agent_input['risk_score'] = risk_score
            
            rec_result = self.recommendation_agent.run(agent_input)
            
            if rec_result['status'] == 'success':
                result['recommendations'] = rec_result['result']
            else:
                result['errors'].append({
                    'agent': 'RecommendationAgent',
                    'error': rec_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'RecommendationAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        return result
    
    def detect_transaction_fraud(
        self,
        account_id: str,
        timestamp: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Orchestrate fraud detection for a specific transaction.
        
        Args:
            account_id: Account ID
            timestamp: Transaction timestamp
            lookback_days: Days to look back for baseline
            
        Returns:
            Dictionary with fraud detection results and any errors
        """
        result = {
            'account_id': account_id,
            'timestamp': timestamp,
            'fraud_analysis': None,
            'errors': []
        }
        
        # Run fraud detection agent (transaction mode)
        try:
            fraud_result = self.fraud_agent.run({
                'account_id': account_id,
                'timestamp': timestamp,
                'lookback_days': lookback_days
            })
            
            if fraud_result['status'] == 'success':
                result['fraud_analysis'] = fraud_result['result']
            else:
                result['errors'].append({
                    'agent': 'FraudDetectionAgent',
                    'error': fraud_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'FraudDetectionAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        return result
    
    def generate_explanation(
        self,
        account_id: str,
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate explanation generation using ExplanationAgent with IBM watsonx.ai.
        
        Args:
            account_id: Account ID
            risk_data: Dictionary containing:
                - risk_score (float): Risk score from 0.0 to 1.0
                - risk_level (str): Risk level (critical/high/medium/low/minimal)
                - aml_patterns (list, optional): List of AML pattern dicts
                - recommendations (list, optional): List of recommendation dicts
                
        Returns:
            Dictionary with explanation results and any errors
        """
        result = {
            'account_id': account_id,
            'explanation': None,
            'errors': []
        }
        
        # Get watsonx.ai credentials from environment
        api_key = os.getenv('WATSONX_API_KEY')
        url = os.getenv('WATSONX_URL', 'https://eu-de.ml.cloud.ibm.com')
        project_id = os.getenv('WATSONX_PROJECT_ID')
        
        # Initialize ExplanationAgent with credentials
        try:
            explanation_agent = ExplanationAgent(
                api_key=api_key,
                url=url,
                project_id=project_id
            )
            
            # Prepare input data for the agent
            agent_input = {
                'account_id': account_id,
                'risk_score': risk_data.get('risk_score'),
                'risk_level': risk_data.get('risk_level'),
                'aml_patterns': risk_data.get('aml_patterns', []),
                'recommendations': risk_data.get('recommendations', [])
            }
            
            # Run the explanation agent
            explanation_result = explanation_agent.run(agent_input)
            
            if explanation_result['status'] == 'success':
                result['explanation'] = explanation_result['result']
            else:
                result['errors'].append({
                    'agent': 'ExplanationAgent',
                    'error': explanation_result['metadata'].get('error', 'Unknown error')
                })
        except Exception as e:
            result['errors'].append({
                'agent': 'ExplanationAgent',
                'error': f"Unexpected error: {str(e)}"
            })
        
        return result


# Made with Bob