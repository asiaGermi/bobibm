"""
Pydantic Models for Financial Risk Management API
Phase 3: REST API Layer - Request/Response Models

This module defines all request and response models for the API endpoints.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Request Models
# ============================================================================

class TransactionAnalysisRequest(BaseModel):
    """Request model for analyzing a single transaction."""
    
    account_id: str = Field(
        ...,
        description="Account ID to analyze",
        examples=["8000EBD30"]
    )
    timestamp: str = Field(
        ...,
        description="Transaction timestamp in ISO format or 'YYYY/MM/DD HH:MM'",
        examples=["2022/09/01 00:20", "2022-09-01T00:20:00"]
    )
    lookback_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to look back for historical analysis"
    )
    
    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("account_id cannot be empty")
        return v.strip()


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment."""
    
    account_id: str = Field(
        ...,
        description="Account ID to assess",
        examples=["8000EBD30"]
    )
    lookback_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Number of days to analyze for risk assessment"
    )
    
    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("account_id cannot be empty")
        return v.strip()


class RecommendActionsRequest(BaseModel):
    """Request model for action recommendations."""
    
    account_id: str = Field(
        ...,
        description="Account ID for recommendations",
        examples=["8000EBD30"]
    )
    risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Pre-calculated risk score (if None, will be calculated)"
    )
    lookback_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Number of days to analyze"
    )
    
    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("account_id cannot be empty")
        return v.strip()


# ============================================================================
# Response Models
# ============================================================================

class TransactionDetail(BaseModel):
    """Model for transaction details."""
    
    timestamp: str
    from_bank: str
    from_account: str
    to_bank: str
    to_account: str
    amount_received: float
    receiving_currency: str
    amount_paid: float
    payment_currency: str
    payment_format: str
    is_laundering: int


class AnomalyDetail(BaseModel):
    """Model for anomaly detection details."""
    
    is_anomalous: bool = Field(description="Whether an anomaly was detected")
    anomaly_score: float = Field(ge=0.0, le=1.0, description="Anomaly score from 0.0 to 1.0")
    anomaly_types: List[str] = Field(description="Types of anomalies detected")
    details: Dict[str, Any] = Field(description="Detailed anomaly information")


class TransactionAnalysisResponse(BaseModel):
    """Response model for transaction analysis."""
    
    account_id: str
    timestamp: str
    transaction_found: bool
    transaction: Optional[TransactionDetail] = None
    anomaly_detection: Optional[AnomalyDetail] = None
    message: Optional[str] = None


class AMLPattern(BaseModel):
    """Model for AML pattern detection."""
    
    pattern_type: str = Field(description="Type of AML pattern detected")
    severity: str = Field(description="Severity level: low, medium, high, critical")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    description: str = Field(description="Human-readable description")
    evidence: Dict[str, Any] = Field(description="Supporting evidence")


class RiskMetrics(BaseModel):
    """Model for risk metrics."""
    
    risk_score: float = Field(ge=0.0, le=1.0, description="Overall risk score")
    risk_level: str = Field(description="Risk level: low, medium, high, critical")
    aml_patterns_detected: int = Field(description="Number of AML patterns detected")
    aml_patterns: List[AMLPattern] = Field(description="Detailed AML patterns")


class TransactionStatistics(BaseModel):
    """Model for transaction statistics."""
    
    total_transactions: int
    sent_count: int
    received_count: int
    total_sent: float
    total_received: float
    net_flow: float
    avg_transaction_amount: float
    median_transaction_amount: float
    std_transaction_amount: float
    max_transaction: float
    min_transaction: float
    laundering_count: int
    laundering_percentage: float
    unique_counterparties: int
    payment_formats: Dict[str, int]


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment."""
    
    account_id: str
    analysis_period_days: int
    date_range: Dict[str, str]
    risk_metrics: RiskMetrics
    transaction_statistics: TransactionStatistics


class ActionRecommendation(BaseModel):
    """Model for a single action recommendation."""
    
    action: str = Field(description="Recommended action")
    priority: str = Field(description="Priority level: low, medium, high, critical")
    reason: str = Field(description="Reason for recommendation")
    details: Dict[str, Any] = Field(description="Additional details")


class RecommendActionsResponse(BaseModel):
    """Response model for action recommendations."""
    
    account_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: str
    recommendations: List[ActionRecommendation]
    summary: str


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Current timestamp")
    data_layer_status: str = Field(description="Data layer connectivity status")
    dataset_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dataset information if available"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    timestamp: str = Field(description="Error timestamp")


class FraudDetectionResponse(BaseModel):
    """Response model for fraud detection."""
    
    account_id: str
    timestamp: str
    fraud_risk_level: str = Field(description="Fraud risk level: minimal, low, medium, high, critical")
    anomaly_score: float = Field(ge=0.0, le=1.0, description="Anomaly score from 0.0 to 1.0")
    is_anomalous: bool = Field(description="Whether fraud signals were detected")
    fraud_signals: List[Dict[str, Any]] = Field(description="List of detected fraud signals")
    recommendation: str = Field(description="Fraud-specific recommendation")
    anomaly_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed anomaly information"
    )


# Made with Bob

class ExplainRequest(BaseModel):
    """Request model for generating risk assessment explanations."""
    
    account_id: str = Field(
        ...,
        description="Account ID to explain",
        examples=["8000EBD30"]
    )
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Risk score from risk assessment"
    )
    risk_level: str = Field(
        ...,
        description="Risk level: minimal, low, medium, high, critical",
        examples=["high"]
    )
    aml_patterns: List[str] = Field(
        default_factory=list,
        description="List of detected AML pattern types"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of recommended actions"
    )
    
    @field_validator('account_id')
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("account_id cannot be empty")
        return v.strip()
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        valid_levels = ['minimal', 'low', 'medium', 'high', 'critical']
        if v.lower() not in valid_levels:
            raise ValueError(f"risk_level must be one of: {', '.join(valid_levels)}")
        return v.lower()


class ExplainResponse(BaseModel):
    """Response model for risk assessment explanations."""
    
    account_id: str = Field(description="Account ID")
    explanation: str = Field(description="Natural language explanation of risk assessment")
    model_used: str = Field(description="Model used for generation (e.g., 'ibm/granite-3-8b-instruct' or 'fallback')")
    generated_at: str = Field(description="Timestamp when explanation was generated")
    fallback_used: bool = Field(description="Whether fallback rule-based explanation was used")

