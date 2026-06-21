"""
Agents Module for Financial Risk Management System
Phase 4: Agent Layer Implementation

This module provides specialized agents for financial risk analysis:
- TransactionAnalysisAgent: Analyzes transaction patterns
- RiskAssessmentAgent: Calculates risk scores and identifies high-risk accounts
- RecommendationAgent: Generates structured action recommendations
- FraudDetectionAgent: Detects fraud signals and anomalies

All agents are data-driven with no LLM calls.
"""

from .transaction_analysis_agent import TransactionAnalysisAgent
from .risk_assessment_agent import RiskAssessmentAgent
from .recommendation_agent import RecommendationAgent
from .fraud_detection_agent import FraudDetectionAgent

__all__ = [
    'TransactionAnalysisAgent',
    'RiskAssessmentAgent',
    'RecommendationAgent',
    'FraudDetectionAgent'
]

# Made with Bob