"""
FastAPI Application for Financial Risk Management System
Phase 3: REST API Layer Implementation

This module provides REST API endpoints for financial risk analysis,
AML pattern detection, and risk assessment using the data layer functions.
"""

from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
import os

# Import data layer functions
from ..data.loader import (
    get_transaction_by_key,
    get_dataset_info,
    DataLoaderError,
    DataNotFoundError,
    InvalidTransactionKeyError
)
from ..data.analyzer import (
    calculate_risk_score,
    detect_aml_patterns,
    detect_temporal_anomalies,
    get_account_history,
    AnalyzerError
)

# Import orchestrator
from .orchestrator import AgentOrchestrator

# Import governance monitor
from ..governance.monitoring import GovernanceMonitor

# Import API models
from .models import (
    TransactionAnalysisRequest,
    TransactionAnalysisResponse,
    TransactionDetail,
    AnomalyDetail,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    RiskMetrics,
    TransactionStatistics,
    AMLPattern,
    RecommendActionsRequest,
    RecommendActionsResponse,
    ActionRecommendation,
    FraudDetectionResponse,
    HealthCheckResponse,
    ErrorResponse,
    ExplainRequest,
    ExplainResponse
)


# ============================================================================
# Configuration
# ============================================================================

class Settings(BaseSettings):
    """Application settings using pydantic-settings."""
    
    app_name: str = "Financial Risk Management API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Data settings
    data_path: Optional[str] = None
    
    # watsonx.ai settings (read from environment without FRM_ prefix)
    watsonx_api_key: Optional[str] = None
    watsonx_url: str = "https://eu-de.ml.cloud.ibm.com"
    watsonx_project_id: Optional[str] = None
    
    class Config:
        env_prefix = "FRM_"
        case_sensitive = False
        # Allow reading WATSONX_* variables without FRM_ prefix
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Read WATSONX_* variables from environment if not set via FRM_ prefix
        import os
        if not self.watsonx_api_key:
            self.watsonx_api_key = os.getenv('WATSONX_API_KEY')
        if self.watsonx_url == "https://us-south.ml.cloud.ibm.com":
            self.watsonx_url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
        if not self.watsonx_project_id:
            self.watsonx_project_id = os.getenv('WATSONX_PROJECT_ID')


settings = Settings()


# ============================================================================
# Application Lifecycle
# ============================================================================

# Global instances
orchestrator = None
governance_monitor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator, governance_monitor

    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        info = get_dataset_info(settings.data_path)
        print(f"✓ Data layer connected: {info['total_transactions']} transactions loaded")

        orchestrator = AgentOrchestrator(settings.data_path)
        print(f"✓ Agent orchestrator initialized")

        if settings.watsonx_api_key and settings.watsonx_project_id:
            print(f"✓ watsonx.ai configured: {settings.watsonx_url}")
            print(f"  - Project ID: {settings.watsonx_project_id[:8]}...")
        else:
            print(f"⚠ watsonx.ai not configured (ExplanationAgent will use fallback mode)")

        governance_api_key = os.getenv("WATSONX_GOVERNANCE_API_KEY")
        governance_monitor = GovernanceMonitor(api_key=governance_api_key)
        if governance_monitor.enabled:
            print(f"✓ watsonx.governance connected (instance: {GovernanceMonitor.INSTANCE_ID[:8]}...)")
        else:
            print(f"⚠ watsonx.governance running in local-only mode (set WATSONX_GOVERNANCE_API_KEY)")

    except Exception as e:
        print(f"⚠ Warning during startup: {str(e)}")

    yield

    print(f"Shutting down {settings.app_name}")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    REST API for Financial Risk Management and AML Detection.
    
    This API provides endpoints for:
    - Transaction analysis and anomaly detection
    - Risk assessment and scoring
    - AML pattern detection
    - Action recommendations
    
    Built on top of IBM Synthetic Financial Data Sets.
    """,
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json"
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ============================================================================
# Static Files
# ============================================================================

# Mount static files directory if it exists
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(DataNotFoundError)
async def data_not_found_handler(request, exc: DataNotFoundError):
    """Handle data not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="DataNotFound",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(InvalidTransactionKeyError)
async def invalid_transaction_key_handler(request, exc: InvalidTransactionKeyError):
    """Handle invalid transaction key errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="InvalidTransactionKey",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(DataLoaderError)
async def data_loader_error_handler(request, exc: DataLoaderError):
    """Handle data loader errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="DataLoaderError",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(AnalyzerError)
async def analyzer_error_handler(request, exc: AnalyzerError):
    """Handle analyzer errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="AnalyzerError",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    f"{settings.api_prefix}/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check API health and data layer connectivity"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status, version, and data layer connectivity information.
    """
    try:
        # Test data layer
        dataset_info = get_dataset_info(settings.data_path)
        data_status = "connected"
    except Exception as e:
        dataset_info = None
        data_status = f"error: {str(e)}"
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat(),
        data_layer_status=data_status,
        dataset_info=dataset_info
    )


@app.post(
    f"{settings.api_prefix}/analyze/transaction",
    response_model=TransactionAnalysisResponse,
    tags=["Analysis"],
    summary="Analyze Transaction",
    description="Analyze a single transaction for anomalies and risk patterns",
    status_code=status.HTTP_200_OK
)
async def analyze_transaction(request: TransactionAnalysisRequest):
    """
    Analyze a specific transaction by account_id and timestamp using TransactionAnalysisAgent.
    
    This endpoint:
    1. Uses TransactionAnalysisAgent to analyze transaction patterns
    2. Retrieves the transaction details
    3. Performs temporal anomaly detection
    4. Returns transaction data with anomaly analysis
    
    Args:
        request: Transaction analysis request with account_id, timestamp, and lookback_days
        
    Returns:
        TransactionAnalysisResponse with transaction details and anomaly detection results
        
    Raises:
        HTTPException: If transaction not found or analysis fails
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service unavailable: data layer not initialized")
    try:
        # Get transaction by key
        transaction = get_transaction_by_key(
            timestamp=request.timestamp,
            from_account=request.account_id,
            data_path=settings.data_path
        )
        
        if not transaction:
            return TransactionAnalysisResponse(
                account_id=request.account_id,
                timestamp=request.timestamp,
                transaction_found=False,
                message="Transaction not found for the given account_id and timestamp"
            )
        
        # Use orchestrator to analyze transaction and detect anomalies
        analysis_result = orchestrator.analyze_transaction(
            account_id=request.account_id,
            timestamp=request.timestamp,
            lookback_days=request.lookback_days
        )
        
        # Also detect temporal anomalies
        anomaly_result = detect_temporal_anomalies(
            account_id=request.account_id,
            timestamp=request.timestamp,
            lookback_days=request.lookback_days,
            data_path=settings.data_path
        )
        
        # Convert transaction to model
        # Convert timestamp to string for Pydantic model
        transaction['timestamp'] = str(transaction.get('timestamp', ''))
        transaction_detail = TransactionDetail(**transaction)
        
        # Convert anomaly result to model
        anomaly_detail = AnomalyDetail(**anomaly_result)
        
        return TransactionAnalysisResponse(
            account_id=request.account_id,
            timestamp=request.timestamp,
            transaction_found=True,
            transaction=transaction_detail,
            anomaly_detection=anomaly_detail,
            message="Transaction analyzed successfully"
        )
        
    except InvalidTransactionKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing transaction: {str(e)}"
        )


@app.post(
    f"{settings.api_prefix}/assess/risk",
    response_model=RiskAssessmentResponse,
    tags=["Risk Assessment"],
    summary="Assess Account Risk",
    description="Calculate risk score and detect AML patterns for an account",
    status_code=status.HTTP_200_OK
)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Assess risk for a specific account using RiskAssessmentAgent and FraudDetectionAgent.
    
    This endpoint:
    1. Uses RiskAssessmentAgent to calculate comprehensive risk score (0.0-1.0)
    2. Uses FraudDetectionAgent to detect fraud patterns
    3. Combines both assessments for comprehensive risk analysis
    4. Detects AML patterns (fan-out, fan-in, circular, smurfing)
    5. Provides transaction statistics
    6. Returns combined risk level classification
    
    Args:
        request: Risk assessment request with account_id and lookback_days
        
    Returns:
        RiskAssessmentResponse with risk metrics and transaction statistics
        
    Raises:
        HTTPException: If risk assessment fails
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service unavailable: data layer not initialized")
    try:
        # Use orchestrator to assess risk with fraud detection
        combined_result = orchestrator.assess_risk_with_fraud(
            account_id=request.account_id,
            lookback_days=request.lookback_days
        )
        
        # Get account history for statistics
        history = get_account_history(
            account_id=request.account_id,
            days_back=request.lookback_days,
            data_path=settings.data_path
        )
        
        # Use combined score if available, otherwise fall back to risk score
        if combined_result['combined_score'] is not None:
            risk_score = combined_result['combined_score']
            risk_level = combined_result['combined_level']
        elif combined_result['risk_assessment']:
            risk_score = combined_result['risk_assessment']['risk_score']
            risk_level = combined_result['risk_assessment']['risk_level']
        else:
            # Fallback: calculate directly
            risk_score = calculate_risk_score(
                account_id=request.account_id,
                lookback_days=request.lookback_days,
                data_path=settings.data_path
            )
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
        
        # Detect AML patterns
        aml_patterns = detect_aml_patterns(
            account_id=request.account_id,
            lookback_days=request.lookback_days,
            data_path=settings.data_path
        )
        
        # Convert AML patterns to models
        aml_pattern_models = [AMLPattern(**pattern) for pattern in aml_patterns]
        
        # Build risk metrics
        risk_metrics = RiskMetrics(
            risk_score=risk_score,
            risk_level=risk_level,
            aml_patterns_detected=len(aml_patterns),
            aml_patterns=aml_pattern_models
        )
        
        # Build transaction statistics
        transaction_stats = TransactionStatistics(**history['statistics'])
        
        response = RiskAssessmentResponse(
            account_id=request.account_id,
            analysis_period_days=request.lookback_days,
            date_range=history['date_range'],
            risk_metrics=risk_metrics,
            transaction_statistics=transaction_stats
        )

        if governance_monitor:
            governance_monitor.log_risk_assessment(
                account_id=request.account_id,
                lookback_days=request.lookback_days,
                risk_score=risk_score,
                risk_level=risk_level,
                aml_patterns_count=len(aml_patterns),
                tx_count=history['statistics'].get('transaction_count', 0),
            )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing risk: {str(e)}"
        )


@app.post(
    f"{settings.api_prefix}/recommend/actions",
    response_model=RecommendActionsResponse,
    tags=["Recommendations"],
    summary="Recommend Actions",
    description="Get recommended actions based on risk score and detected patterns",
    status_code=status.HTTP_200_OK
)
async def recommend_actions(request: RecommendActionsRequest):
    """
    Generate action recommendations using RecommendationAgent.
    
    This endpoint:
    1. Uses RecommendationAgent to generate structured recommendations
    2. Calculates or uses provided risk score
    3. Detects AML patterns
    4. Generates prioritized action recommendations (ALERT, REVIEW, BLOCK, MONITOR)
    5. Provides actionable insights
    
    Args:
        request: Action recommendation request with account_id, optional risk_score, and lookback_days
        
    Returns:
        RecommendActionsResponse with prioritized recommendations
        
    Raises:
        HTTPException: If recommendation generation fails
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service unavailable: data layer not initialized")
    try:
        # Use orchestrator to generate recommendations
        rec_result = orchestrator.generate_recommendations(
            account_id=request.account_id,
            risk_score=request.risk_score,
            lookback_days=request.lookback_days,
            include_evidence=True
        )
        
        # Check if recommendations were generated successfully
        if rec_result['recommendations']:
            agent_recs = rec_result['recommendations']
            risk_score = agent_recs['risk_score']
            risk_level = agent_recs['risk_level']
            
            # Convert agent recommendations to API models
            recommendations = []
            for rec in agent_recs['recommendations']:
                recommendations.append(ActionRecommendation(
                    action=rec['action'],
                    priority=rec['priority'],
                    reason=rec['reason'],
                    details={"description": rec.get('description', '')}
                ))
            
            # Generate summary
            summary = f"{risk_level.upper()} RISK: {len(recommendations)} recommendations generated."
        else:
            # Fallback: generate recommendations directly
            if request.risk_score is None:
                risk_score = calculate_risk_score(
                    account_id=request.account_id,
                    lookback_days=request.lookback_days,
                    data_path=settings.data_path
                )
            else:
                risk_score = request.risk_score
            
            if risk_score >= 0.8:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            recommendations = [ActionRecommendation(
                action="Manual review required",
                priority=risk_level,
                reason=f"Risk score: {risk_score:.2f}",
                details={"risk_score": risk_score}
            )]
            
            summary = f"{risk_level.upper()} RISK: Manual review recommended."
        
        return RecommendActionsResponse(
            account_id=request.account_id,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.post(
    f"{settings.api_prefix}/detect/fraud",
    response_model=FraudDetectionResponse,
    tags=["Fraud Detection"],
    summary="Detect Fraud",
    description="Detect fraud signals using temporal anomalies and laundering history",
    status_code=status.HTTP_200_OK
)
async def detect_fraud(request: TransactionAnalysisRequest):
    """
    Detect fraud for a specific transaction using FraudDetectionAgent.
    
    This endpoint:
    1. Uses FraudDetectionAgent to detect fraud signals
    2. Analyzes temporal anomalies
    3. Checks laundering history from dataset
    4. Provides fraud-specific recommendations
    
    Args:
        request: Transaction analysis request with account_id, timestamp, and lookback_days
        
    Returns:
        FraudDetectionResponse with fraud risk level and detected signals
        
    Raises:
        HTTPException: If fraud detection fails
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service unavailable: data layer not initialized")
    try:
        # Use orchestrator to detect transaction fraud
        fraud_result = orchestrator.detect_transaction_fraud(
            account_id=request.account_id,
            timestamp=request.timestamp,
            lookback_days=request.lookback_days
        )
        
        # Check if fraud analysis was successful
        if fraud_result['fraud_analysis']:
            fraud_data = fraud_result['fraud_analysis']
            
            fraud_signals = fraud_data.get('fraud_signals', [])
            anomaly_score = fraud_data.get('anomaly_score', 0.0)
            fraud_risk_level = fraud_data.get('fraud_risk_level', 'minimal')
            recommendation = fraud_data.get('recommendation', 'No action required')
            
            return FraudDetectionResponse(
                account_id=request.account_id,
                timestamp=request.timestamp,
                fraud_risk_level=fraud_risk_level,
                anomaly_score=anomaly_score,
                is_anomalous=fraud_data.get('is_anomalous', False),
                fraud_signals=fraud_signals,
                recommendation=recommendation,
                anomaly_details=fraud_data.get('details')
            )
        else:
            # Fallback if fraud analysis failed
            return FraudDetectionResponse(
                account_id=request.account_id,
                timestamp=request.timestamp,
                fraud_risk_level="unknown",
                anomaly_score=0.0,
                is_anomalous=False,
                fraud_signals=[],
                recommendation="Unable to perform fraud analysis",
                anomaly_details={"errors": fraud_result.get('errors', [])}
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting fraud: {str(e)}"
        )


@app.post(
    f"{settings.api_prefix}/explain",
    response_model=ExplainResponse,
    tags=["Explanation"],
    summary="Generate Risk Explanation",
    description="Generate natural language explanation of risk assessment using IBM watsonx.ai",
    status_code=status.HTTP_200_OK
)
async def generate_explanation(request: ExplainRequest):
    """
    Generate natural language explanation of risk assessment results using ExplanationAgent.
    
    This endpoint:
    1. Uses ExplanationAgent with IBM watsonx.ai (Granite model)
    2. Generates clear, professional explanations for compliance officers
    3. Falls back to rule-based explanations if LLM is unavailable
    4. Provides context about risk level, AML patterns, and recommendations
    
    Args:
        request: Explanation request with account_id, risk_score, risk_level,
                 aml_patterns, and recommendations
        
    Returns:
        ExplainResponse with natural language explanation
        
    Raises:
        HTTPException: If explanation generation fails
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service unavailable: data layer not initialized")
    
    try:
        # Prepare risk data for the orchestrator
        risk_data = {
            'risk_score': request.risk_score,
            'risk_level': request.risk_level,
            'aml_patterns': [{'pattern_type': p} for p in request.aml_patterns],
            'recommendations': [{'action': r} for r in request.recommendations]
        }
        
        # Use orchestrator to generate explanation
        explanation_result = orchestrator.generate_explanation(
            account_id=request.account_id,
            risk_data=risk_data
        )
        
        # Check if explanation was generated successfully
        if explanation_result['explanation']:
            explanation_data = explanation_result['explanation']
            
            fallback_used = (explanation_data['model_used'] == 'fallback')

            if governance_monitor:
                governance_monitor.log_explanation(
                    account_id=request.account_id,
                    risk_score=request.risk_score,
                    risk_level=request.risk_level,
                    model_used=explanation_data['model_used'],
                    fallback_used=fallback_used,
                )

            return ExplainResponse(
                account_id=request.account_id,
                explanation=explanation_data['explanation'],
                model_used=explanation_data['model_used'],
                generated_at=datetime.utcnow().isoformat(),
                fallback_used=fallback_used,
            )
        else:
            # If explanation failed, return error details
            errors = explanation_result.get('errors', [])
            error_msg = errors[0]['error'] if errors else "Unknown error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate explanation: {error_msg}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating explanation: {str(e)}"
        )


# ============================================================================
# Governance Endpoints
# ============================================================================

@app.get(
    f"{settings.api_prefix}/governance/metrics",
    tags=["Governance"],
    summary="Governance Metrics",
    description="Aggregated metrics from watsonx.governance prediction logs"
)
async def governance_metrics():
    if governance_monitor is None:
        raise HTTPException(status_code=503, detail="Governance monitor not initialized")
    return governance_monitor.get_metrics()


@app.get(
    f"{settings.api_prefix}/governance/logs",
    tags=["Governance"],
    summary="Recent Governance Logs",
    description="Recent prediction logs (local cache)"
)
async def governance_logs(limit: int = 20, log_type: Optional[str] = None):
    if governance_monitor is None:
        raise HTTPException(status_code=503, detail="Governance monitor not initialized")
    return {
        "logs": governance_monitor.get_recent_logs(limit=limit, log_type=log_type),
        "total": len(governance_monitor._local_log),
    }


@app.get(
    f"{settings.api_prefix}/governance/cloud-records",
    tags=["Governance"],
    summary="Cloud Governance Records",
    description="Fetch prediction records directly from IBM watsonx.governance"
)
async def governance_cloud_records(limit: int = 20):
    if governance_monitor is None:
        raise HTTPException(status_code=503, detail="Governance monitor not initialized")
    return governance_monitor.get_cloud_records(limit=limit)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get API information and available endpoints"
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": f"{settings.api_prefix}/docs",
        "health": f"{settings.api_prefix}/health",
        "dashboard": "/dashboard",
        "endpoints": {
            "analyze_transaction": f"{settings.api_prefix}/analyze/transaction",
            "assess_risk": f"{settings.api_prefix}/assess/risk",
            "recommend_actions": f"{settings.api_prefix}/recommend/actions",
            "detect_fraud": f"{settings.api_prefix}/detect/fraud",
            "explain": f"{settings.api_prefix}/explain",
            "governance_metrics": f"{settings.api_prefix}/governance/metrics",
            "governance_logs": f"{settings.api_prefix}/governance/logs",
            "governance_cloud_records": f"{settings.api_prefix}/governance/cloud-records",
        }
    }


@app.get(
    "/dashboard",
    tags=["Dashboard"],
    summary="Risk Dashboard",
    description="Interactive dashboard for risk analysis and visualization"
)
async def dashboard():
    """Serve the interactive risk dashboard."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
    dashboard_path = os.path.join(static_dir, "index.html")
    
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found. Please ensure static/index.html exists."
        )


# Made with Bob