# Spec-Driven Development (SDD)
# Financial Risk Management Agentic System
# IBM Open Agentic Builders - Track A

**Version**: 1.0  
**Date**: 2026-06-19  
**Project**: IBM Cloud Challenge - Financial Risk Management  
**Team**: BOB Challenge Team

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Agent Definitions](#3-agent-definitions)
4. [Tool Definitions](#4-tool-definitions)
5. [API Contract](#5-api-contract)
6. [Data Flow](#6-data-flow)
7. [Implementation Phases](#7-implementation-phases)
8. [Verification Criteria](#8-verification-criteria)
9. [Appendices](#9-appendices)

---

## 1. System Overview

### 1.1 Purpose

The Financial Risk Management Agentic System is a containerized, AI-powered application designed to analyze financial transactions, assess money laundering risks, detect fraud patterns, and generate actionable recommendations for compliance teams in the banking industry.

### 1.2 Scope

The system processes transactions from the IBM Synthetic Data Set (HI-Small_Trans.csv) and provides:
- Real-time transaction analysis
- Risk scoring and assessment
- Fraud detection and pattern recognition
- Automated action recommendations
- Compliance reporting

### 1.3 Key Requirements (IBM Mandate)

- **Deployment**: Containerized on IBM Cloud Code Engine
- **Orchestration**: watsonx Orchestrate ADK for agent workflow management
- **LLM**: IBM Granite 3 8B for reasoning and analysis
- **API**: REST API endpoints for integration with financial systems
- **Data Source**: IBM Synthetic Data Sets (HI-Small_Trans.csv)
- **Agents**: 4 specialized agents working collaboratively

### 1.4 Technology Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | IBM Bob + watsonx Orchestrate ADK |
| LLM | IBM Granite 3 8B |
| API Framework | FastAPI (Python 3.11+) |
| Container Platform | IBM Cloud Code Engine |
| Data Processing | Pandas, NumPy (in-memory cache) |
| Monitoring | IBM Cloud Monitoring |
| Logging | IBM Cloud Logging |

---

## 2. Architecture

### 2.1 High-Level Architecture (Textual Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SYSTEMS                             │
│                  (Financial Applications)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│                        (FastAPI)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ POST /analyze│  │ GET /health  │  │ POST /batch  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              WATSONX ORCHESTRATE LAYER                           │
│                  (Workflow Orchestrator)                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Orchestration Workflow                       │  │
│  │  1. Validate Input → 2. Route to Agents → 3. Aggregate   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬────────────────┐
        ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Transaction  │ │ Risk         │ │ Fraud        │ │ Action       │
│ Analysis     │ │ Evaluation   │ │ Detection    │ │ Recommend.   │
│ Agent        │ │ Agent        │ │ Agent        │ │ Agent        │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Loader  │  │ Risk Scorer  │  │ Pattern      │          │
│  │              │  │              │  │ Detector     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              HI-Small_Trans.csv                           │  │
│  │         (with in-memory pandas cache)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   IBM GRANITE 3 8B LLM                           │
│              (Reasoning & Natural Language)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **API Gateway** | Request validation, authentication, rate limiting, response formatting |
| **watsonx Orchestrate** | Agent coordination, workflow management, error handling, result aggregation |
| **Agents** | Specialized analysis tasks (transaction, risk, fraud, recommendations) |
| **Tools** | Reusable utilities for data access, calculations, pattern detection |
| **Data Layer** | Transaction data loading from CSV, in-memory caching with pandas |
| **LLM** | Natural language reasoning, explanation generation, insight synthesis |

### 2.3 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IBM CLOUD CODE ENGINE                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Container: API Service                     │ │
│  │  - FastAPI Application                                      │ │
│  │  - Health Checks                                            │ │
│  │  - Auto-scaling: 1-10 instances                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Container: Agent Service                       │ │
│  │  - 4 Specialized Agents                                     │ │
│  │  - watsonx Orchestrate Integration                          │ │
│  │  - IBM Granite 3 8B Connection                              │ │
│  │  - Auto-scaling: 2-20 instances                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                IBM Cloud Services                           │ │
│  │  - Object Storage (Dataset)                                 │ │
│  │  - Monitoring & Logging                                     │ │
│  │  - Secrets Manager                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent Definitions

### 3.1 Transaction Analysis Agent

**Name**: `TransactionAnalysisAgent`

**Role**: Analyze individual transactions and identify patterns, anomalies, and behavioral characteristics.

**Input Schema**:
```python
{
    "transaction_key": Optional[dict],  # {"timestamp": str, "from_account": str}
    "account_id": Optional[str],
    "transaction_data": Optional[dict],
    "analysis_depth": str,  # "basic" | "detailed" | "comprehensive"
    "include_context": bool
}
```

**Note**: Transaction identifier is composite: `Timestamp + Account (From)` from HI-Small_Trans.csv

**Output Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "analysis_timestamp": str,
    "patterns_detected": List[dict],
    "anomalies": List[dict],
    "behavioral_insights": List[str],
    "context_summary": dict
}
```

**Tools Used**:
- `load_transaction_data`
- `calculate_transaction_statistics`
- `detect_temporal_anomalies`
- `analyze_amount_patterns`
- `get_account_history`

**LLM Integration**: Uses IBM Granite 3 8B for natural language insight generation

---

### 3.2 Risk Evaluation Agent

**Name**: `RiskEvaluationAgent`

**Role**: Assess the risk level of transactions based on multiple factors and generate comprehensive risk scores.

**Input Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "transaction_data": dict,
    "analysis_results": dict,
    "risk_factors": Optional[List[str]],
    "threshold_config": Optional[dict]
}
```

**Output Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "risk_assessment_timestamp": str,
    "overall_risk_score": float,  # 0.0 to 1.0
    "risk_level": str,  # "low" | "medium" | "high" | "critical"
    "risk_factors": List[dict],
    "compliance_flags": List[dict],
    "risk_indicators": dict,
    "confidence_level": float
}
```

**Tools Used**:
- `calculate_risk_score`
- `evaluate_aml_indicators`
- `check_compliance_rules`
- `assess_geographic_risk`
- `analyze_velocity_patterns`

**LLM Integration**: Uses IBM Granite 3 8B for risk explanation generation

---

### 3.3 Fraud Detection Agent

**Name**: `FraudDetectionAgent`

**Role**: Identify potential fraud patterns, money laundering schemes, and suspicious activities.

**Input Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "transaction_data": dict,
    "risk_assessment": dict,
    "detection_mode": str,  # "real-time" | "batch" | "deep-analysis"
    "fraud_types": Optional[List[str]]
}
```

**Output Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "fraud_detection_timestamp": str,
    "is_fraudulent": bool,
    "fraud_probability": float,
    "fraud_types_detected": List[dict],
    "laundering_indicators": dict,
    "suspicious_patterns": List[dict],
    "red_flags": List[dict]
}
```

**Tools Used**:
- `detect_laundering_patterns`
- `identify_structuring`
- `analyze_transaction_network`
- `check_known_fraud_patterns`
- `calculate_fraud_score`

**LLM Integration**: Uses IBM Granite 3 8B for fraud pattern explanation

---

### 3.4 Action Recommendation Agent

**Name**: `ActionRecommendationAgent`

**Role**: Generate actionable recommendations based on analysis, risk assessment, and fraud detection results.

**Input Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "transaction_analysis": dict,
    "risk_assessment": dict,
    "fraud_detection": dict,
    "business_context": Optional[dict],
    "recommendation_mode": str  # "conservative" | "balanced" | "aggressive"
}
```

**Output Schema**:
```python
{
    "transaction_key": dict,  # {"timestamp": str, "from_account": str}
    "recommendation_timestamp": str,
    "primary_action": dict,
    "recommended_actions": List[dict],
    "compliance_actions": List[dict],
    "investigation_steps": List[dict],
    "notification_requirements": dict,
    "documentation_requirements": List[str],
    "escalation_path": List[str]
}
```

**Tools Used**:
- `generate_recommendations`
- `prioritize_actions`
- `check_regulatory_requirements`
- `format_compliance_report`
- `create_investigation_plan`

**LLM Integration**: Uses IBM Granite 3 8B for recommendation explanation and justification

---

## 4. Tool Definitions

### 4.1 Data Access Tools

#### load_transaction_data
**Function**: Load transaction data from HI-Small_Trans.csv dataset
**Parameters**: `{transaction_key: {timestamp, from_account}, account_id, date_range, limit}`
**Return Type**: `Union[dict, List[dict]]`
**Note**: Transaction identifier is composite: Timestamp + Account (From)

#### get_account_history
**Function**: Retrieve historical transaction data for an account  
**Parameters**: `{account_id, days_back, include_statistics}`  
**Return Type**: `{account_id, transactions, statistics}`

### 4.2 Analysis Tools

#### calculate_transaction_statistics
**Function**: Calculate statistical metrics for transactions  
**Parameters**: `{transactions, metrics}`  
**Return Type**: `{count, mean_amount, median_amount, std_deviation, percentiles}`

#### detect_temporal_anomalies
**Function**: Identify time-based anomalies in transaction patterns  
**Parameters**: `{transaction, historical_data, sensitivity}`  
**Return Type**: `{is_anomalous, anomaly_score, anomaly_type, details}`

#### analyze_amount_patterns
**Function**: Analyze transaction amounts for suspicious patterns  
**Parameters**: `{transaction, account_history, thresholds}`  
**Return Type**: `{is_unusual, deviation_score, pattern_type, explanation}`

### 4.3 Risk Assessment Tools

#### calculate_risk_score
**Function**: Calculate composite risk score based on multiple factors  
**Parameters**: `{transaction, risk_factors, weights, model_version}`  
**Return Type**: `{overall_score, risk_level, factor_contributions, confidence}`

#### evaluate_aml_indicators
**Function**: Evaluate Anti-Money Laundering indicators  
**Parameters**: `{transaction, account_profile, regulatory_rules}`  
**Return Type**: `{aml_score, triggered_rules, compliance_status, required_actions}`

#### check_compliance_rules
**Function**: Check transaction against compliance rules  
**Parameters**: `{transaction, jurisdiction, rule_set}`  
**Return Type**: `{compliant, violations, warnings, required_documentation}`

### 4.4 Fraud Detection Tools

#### detect_laundering_patterns
**Function**: Detect money laundering patterns in transaction data  
**Parameters**: `{transaction, network_data, pattern_types}`  
**Return Type**: `{patterns_found, confidence_scores, network_analysis, is_laundering}`

#### identify_structuring
**Function**: Identify structuring (smurfing) patterns  
**Parameters**: `{transactions, time_window, threshold}`  
**Return Type**: `{is_structuring, total_amount, transaction_count, pattern_description}`

#### analyze_transaction_network
**Function**: Analyze network of related transactions
**Parameters**: `{transaction_key: {timestamp, from_account}, depth, include_accounts}`
**Return Type**: `{network_graph, suspicious_clusters, central_nodes, network_metrics}`

### 4.5 Recommendation Tools

#### generate_recommendations
**Function**: Generate action recommendations based on analysis results  
**Parameters**: `{analysis_results, risk_level, fraud_indicators, business_rules}`  
**Return Type**: `{recommendations, priority_order, estimated_impacts}`

#### prioritize_actions
**Function**: Prioritize recommended actions  
**Parameters**: `{actions, criteria, constraints}`  
**Return Type**: `{prioritized_actions, priority_scores, execution_order}`

#### format_compliance_report
**Function**: Format results into compliance report  
**Parameters**: `{transaction_data, analysis_results, recommendations, report_format}`  
**Return Type**: `{report_id, report_content, metadata}`

---

## 5. API Contract

### 5.1 Base Configuration

**Base URL**: `https://financial-risk-api.ibmcloud.com/api/v1`
**Authentication**: API Key via `X-API-Key` header (or no auth for MVP)
**Content-Type**: `application/json`

**Note**: Authentication is simplified for MVP. Production systems should implement proper JWT-based authentication.

### 5.2 Endpoint: POST /analyze

**Description**: Analyze a transaction or account for risk, fraud, and generate recommendations

**Request Example**:
```json
{
    "transaction_key": {
        "timestamp": "2025-08-11T14:32:17.6Z",
        "from_account": "3020009543"
    },
    "options": {
        "analysis_depth": "comprehensive",
        "include_recommendations": true,
        "include_explanation": true
    }
}
```

**Note**: Transaction identifier is composite: `Timestamp + Account (From)` from HI-Small_Trans.csv

**Response Example (200 OK)**:
```json
{
    "request_id": "req_20260619_001",
    "transaction_key": {
        "timestamp": "2025-08-11T14:32:17.6Z",
        "from_account": "3020009543"
    },
    "risk_assessment": {
        "overall_risk_score": 0.78,
        "risk_level": "high"
    },
    "fraud_detection": {
        "fraud_probability": 0.35,
        "is_laundering": false
    },
    "recommendations": {
        "primary_action": {
            "action_type": "review",
            "priority": "high"
        }
    },
    "explanation": {
        "summary": "High-risk transaction requiring manual review..."
    }
}
```

### 5.3 Endpoint: GET /health

**Response (200 OK)**:
```json
{
    "status": "healthy",
    "services": {
        "api": "healthy",
        "agents": "healthy",
        "llm": "healthy"
    }
}
```

### 5.4 Endpoint: POST /batch

**Description**: Batch process multiple transactions

**Request Example**:
```json
{
    "transactions": [
        {"timestamp": "2025-08-11T14:32:17.6Z", "from_account": "3020009543"},
        {"timestamp": "2025-08-11T15:20:10.2Z", "from_account": "1409286471"}
    ],
    "options": {
        "parallel_processing": true
    }
}
```

**Response (202 Accepted)**:
```json
{
    "batch_id": "batch_20260619_001",
    "status": "processing",
    "total_transactions": 2
}
```

---

## 6. Data Flow

### 6.1 Single Transaction Analysis Flow

```
Client Request
    ↓
API Gateway (Validation)
    ↓
watsonx Orchestrate (Workflow Init)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Transaction │ Risk        │ Fraud       │  ← parallel
│ Analysis    │ Evaluation  │ Detection   │
└──────┬──────┴──────┬──────┴──────┬──────┘
       └─────────────┼─────────────┘
                     ▼
             ┌──────────────┐
             │ Action       │  ← sequential (depends on above)
             │ Recommend.   │
             └──────────────┘
    ↓
Result Aggregation
    ↓
LLM Explanation (IBM Granite 3 8B)
    ↓
Response Formatting
    ↓
Client Response
```

### 6.2 Agent Interaction Sequence

1. **API receives request** with transaction_key (timestamp + from_account)
2. **Data loading** from HI-Small_Trans.csv
3. **watsonx Orchestrate** initiates workflow
4. **First 3 agents execute in parallel**:
   - Transaction Analysis Agent analyzes patterns
   - Risk Evaluation Agent calculates risk score
   - Fraud Detection Agent identifies fraud indicators
5. **Action Recommendation Agent** receives outputs of steps above and generates actions
6. **Results aggregation** by watsonx Orchestrate
6. **LLM generates** natural language explanation
7. **Response returned** to client

---

## 7. Implementation Phases

**Contest Deadline**: July 1, 2026 (13 days from June 19, 2026)

### Phase 1: Foundation Setup (Day 1-2)

**Duration**: 2 days
**Objectives**: Set up infrastructure and development environment

**Deliverables**:
- IBM Cloud Code Engine configured
- watsonx Orchestrate instance provisioned
- IBM Granite 3 8B access configured
- GitHub repository with basic CI/CD
- Base Docker containers

**Tasks**:
- Create IBM Cloud project
- Set up Code Engine application
- Configure Object Storage for dataset
- Set up watsonx Orchestrate workspace
- Create GitHub repository
- Configure secrets management

---

### Phase 2: Data Layer (Day 3)

**Duration**: 1 day
**Objectives**: Implement data loading and validation

**Deliverables**:
- Data loading module
- CSV parser for HI-Small_Trans.csv
- Data validation layer
- In-memory caching with pandas

**Tasks**:
- Implement `load_transaction_data` tool
- Create data validation functions
- Implement pandas-based in-memory cache
- Implement error handling

---

### Phase 3: Agent Development (Day 4-8)

**Duration**: 5 days
**Objectives**: Develop all 4 specialized agents

**Deliverables**:
- Transaction Analysis Agent
- Risk Evaluation Agent
- Fraud Detection Agent
- Action Recommendation Agent

**Tasks**:
- Implement agent base classes (Day 4)
- Develop Transaction Analysis Agent (Day 5)
- Develop Risk Evaluation Agent (Day 6)
- Develop Fraud Detection Agent (Day 7)
- Develop Action Recommendation Agent (Day 8)
- Integrate with IBM Granite 3 8B
- Create agent tools
- Unit test each agent

---

### Phase 4: Orchestration (Day 9-10)

**Duration**: 2 days
**Objectives**: Integrate agents with watsonx Orchestrate

**Deliverables**:
- watsonx Orchestrate workflow
- Agent coordination logic
- Error handling
- Result aggregation

**Tasks**:
- Define watsonx skills for each agent (Day 9)
- Create orchestration workflow (Day 9)
- Implement error recovery (Day 10)
- Test end-to-end flow (Day 10)

---

### Phase 5: API Development (Day 11)

**Duration**: 1 day
**Objectives**: Build REST API layer

**Deliverables**:
- FastAPI application
- API endpoints
- Basic API key authentication (optional)
- OpenAPI documentation

**Tasks**:
- Implement POST /analyze endpoint
- Implement GET /health endpoint
- Implement POST /batch endpoint
- Add simple API key authentication (optional)
- Generate OpenAPI documentation

---

### Phase 6: Testing & Deployment (Day 12-13)

**Duration**: 2 days
**Objectives**: Test and deploy to production

**Deliverables**:
- Core test suite
- Basic performance benchmarks
- Production deployment
- Basic monitoring

**Tasks**:
- Unit testing (Day 12)
- Integration testing (Day 12)
- Basic load testing (Day 12)
- Deploy to IBM Cloud Code Engine (Day 13)
- Configure basic monitoring (Day 13)
- Final verification and documentation (Day 13)

---

## 8. Verification Criteria

### 8.1 Phase 1 Verification

**Criteria**:
- [ ] IBM Cloud Code Engine project accessible
- [ ] watsonx Orchestrate instance responding
- [ ] IBM Granite 3 8B endpoint reachable
- [ ] CI/CD pipeline executing successfully
- [ ] Docker containers building without errors

**Acceptance Test**: Deploy "Hello World" container to Code Engine

---

### 8.2 Phase 2 Verification

**Criteria**:
- [ ] HI-Small_Trans.csv successfully loaded
- [ ] Data validation catching malformed records
- [ ] Cache improving load times by >50%
- [ ] All dataset columns correctly parsed

**Acceptance Test**: Load 1000 transactions in <2 seconds

---

### 8.3 Phase 3 Verification

**Criteria**:
- [ ] Each agent processes test transaction successfully
- [ ] Agent outputs match expected schema
- [ ] IBM Granite 3 8B generating coherent explanations
- [ ] Unit test coverage >80%

**Acceptance Test**: Each agent analyzes sample transaction and produces valid output

---

### 8.4 Phase 4 Verification

**Criteria**:
- [ ] watsonx Orchestrate coordinating all 4 agents
- [ ] Workflow completing end-to-end
- [ ] Error handling recovering from agent failures
- [ ] Results properly aggregated

**Acceptance Test**: Complete workflow execution with all agents in <5 seconds

---

### 8.5 Phase 5 Verification

**Criteria**:
- [ ] POST /analyze returning valid responses
- [ ] API response time <2 seconds (p95)
- [ ] API key authentication working (if implemented)
- [ ] OpenAPI documentation complete

**Acceptance Test**: 100 concurrent API requests with <5% error rate

---

### 8.6 Phase 6 Verification

**Criteria**:
- [ ] All tests passing
- [ ] Load test: 1000 req/min sustained
- [ ] Production deployment successful
- [ ] Monitoring dashboards showing metrics
- [ ] Zero critical security vulnerabilities

**Acceptance Test**: Production system handling real transactions with 99.9% uptime

---

## 9. Appendices

### 9.1 Dataset Schema (HI-Small_Trans.csv)

| Column | Type | Description |
|--------|------|-------------|
| Timestamp | datetime | Transaction timestamp (part of composite key) |
| From Bank | string | Originating bank |
| Account | string | From account number (part of composite key) |
| To Bank | string | Destination bank |
| Account | string | To account number |
| Amount Received | float | Amount received |
| Receiving Currency | string | Currency code |
| Amount Paid | float | Amount paid |
| Payment Currency | string | Currency code |
| Payment Format | string | Payment method |
| Is Laundering | int | 0=No, 1=Yes |

**Note**: Transaction unique identifier is the composite key: `Timestamp + Account (From)`

### 9.2 Technology References

- **IBM Bob**: https://ibm.github.io/bob
- **watsonx Orchestrate**: https://www.ibm.com/watsonx/orchestrate
- **IBM Granite 3 8B**: https://www.ibm.com/granite
- **FastAPI**: https://fastapi.tiangolo.com
- **IBM Cloud Code Engine**: https://cloud.ibm.com/codeengine

### 9.3 Success Metrics

| Metric | Target |
|--------|--------|
| API Response Time (p95) | <2 seconds |
| Fraud Detection Accuracy | >90% |
| System Uptime | >99.9% |
| Concurrent Users | >100 |
| Transactions/Minute | >1000 |

---

**End of Specification**

*This document serves as the complete specification for the Financial Risk Management Agentic System implementation.*