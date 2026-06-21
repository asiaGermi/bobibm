# watsonx Orchestrate Skills for Financial Risk Management

This directory contains watsonx Orchestrate (wxO) skill and agent definitions for the Financial Risk Management system.

## Overview

The system consists of 4 specialized skills and 1 orchestrator agent that coordinates them:

### Skills

1. **Transaction Analysis Agent** (`transaction_analysis_agent.yaml`)
   - Analyzes transaction patterns for a specific account
   - Detects AML patterns (fan-out, fan-in, circular, smurfing)
   - Performs temporal anomaly detection
   - Endpoint: `POST /api/v1/analyze/transaction`

2. **Risk Assessment Agent** (`risk_assessment_agent.yaml`)
   - Calculates comprehensive risk score (0.0-1.0)
   - Combines risk and fraud analysis
   - Provides transaction statistics
   - Detects AML patterns
   - Endpoint: `POST /api/v1/assess/risk`

3. **Recommendation Agent** (`recommendation_agent.yaml`)
   - Generates structured action recommendations
   - Actions: ALERT, REVIEW, BLOCK, MONITOR
   - Prioritizes based on risk level and patterns
   - Endpoint: `POST /api/v1/recommend/actions`

4. **Fraud Detection Agent** (`fraud_detection_agent.yaml`)
   - Detects fraud signals using temporal anomalies
   - Analyzes laundering history from dataset
   - Identifies unusual transaction patterns
   - Endpoint: `POST /api/v1/analyze/transaction`

### Orchestrator

**Financial Risk Orchestrator** (`financial_risk_orchestrator.yaml`)
- Coordinates all 4 skills in sequence
- Workflow: Analyze → Assess → Recommend
- Aggregates results from all skills
- Continues execution even if individual skills fail
- Provides comprehensive risk assessment

## Deployment to watsonx Orchestrate

### Prerequisites

1. watsonx Orchestrate instance
2. API server running and accessible
3. `API_BASE_URL` environment variable configured

### Steps

1. **Configure API Base URL**
   ```bash
   export API_BASE_URL=https://your-api-server.com
   ```

2. **Deploy Individual Skills**
   ```bash
   # Using wxo CLI (if available)
   wxo skill create -f transaction_analysis_agent.yaml
   wxo skill create -f risk_assessment_agent.yaml
   wxo skill create -f recommendation_agent.yaml
   wxo skill create -f fraud_detection_agent.yaml
   ```

3. **Deploy Orchestrator Agent**
   ```bash
   wxo agent create -f financial_risk_orchestrator.yaml
   ```

4. **Verify Deployment**
   ```bash
   wxo skill list
   wxo agent list
   ```

## Usage Examples

### Using Individual Skills

#### Transaction Analysis
```json
{
  "account_id": "8000EBD30",
  "timestamp": "2022/09/15 14:30",
  "lookback_days": 30
}
```

#### Risk Assessment
```json
{
  "account_id": "8000EBD30",
  "lookback_days": 90
}
```

#### Recommendations
```json
{
  "account_id": "8000EBD30",
  "risk_score": 0.75,
  "lookback_days": 90
}
```

### Using the Orchestrator

The orchestrator provides a comprehensive analysis by executing all skills in sequence:

```json
{
  "account_id": "8000EBD30",
  "timestamp": "2022/09/15 14:30",
  "lookback_days_short": 30,
  "lookback_days_long": 90
}
```

**Output includes:**
- Transaction analysis results
- Risk assessment with combined score
- Prioritized recommendations
- Overall assessment summary
- Execution metrics

## Skill Configuration

### Environment Variables

Each skill uses the following environment variable:
- `API_BASE_URL`: Base URL of the REST API server

Example:
```bash
export API_BASE_URL=http://localhost:8000
```

### Authentication

Currently configured for `none` (no authentication).

To enable JWT authentication:
1. Update `spec.endpoint.authentication.type` to `jwt`
2. Add JWT token configuration
3. Update API server to validate JWT tokens

### Error Handling

All skills include:
- Retry policy (max 3 attempts)
- Exponential backoff
- Timeout configuration
- Error logging

The orchestrator uses `continue-on-error` strategy to ensure partial results are returned even if some skills fail.

## Monitoring

The orchestrator includes monitoring configuration:
- Execution time tracking
- Success/error rate metrics
- Skill performance monitoring
- Alerting for high error rates or slow execution

## Integration with watsonx Orchestrate

### Skill Discovery

Skills are automatically discovered by watsonx Orchestrate when deployed. They appear in:
- Skill catalog
- Workflow builder
- Agent configuration

### Workflow Integration

Skills can be used in:
1. **Manual workflows**: Drag-and-drop in workflow builder
2. **Automated workflows**: Triggered by events or schedules
3. **Agent orchestration**: Coordinated by the orchestrator agent
4. **API calls**: Direct invocation via wxO API

### Best Practices

1. **Use the orchestrator** for comprehensive analysis
2. **Use individual skills** for specific tasks
3. **Monitor execution metrics** to optimize performance
4. **Configure alerts** for critical failures
5. **Test with sample data** before production use

## Troubleshooting

### Common Issues

1. **Skill not found**
   - Verify skill is deployed: `wxo skill list`
   - Check skill name matches reference

2. **Connection timeout**
   - Verify API server is running
   - Check `API_BASE_URL` is correct
   - Increase timeout in skill definition

3. **Authentication errors**
   - Verify JWT token is valid
   - Check API server authentication configuration

4. **Invalid input**
   - Validate input against schema
   - Check required fields are provided
   - Verify data types match schema

## Support

For issues or questions:
1. Check API server logs
2. Review wxO execution logs
3. Verify skill configuration
4. Test API endpoints directly

## Version History

- **v1.0.0** (2026-06-21)
  - Initial release
  - 4 specialized skills
  - 1 orchestrator agent
  - Sequential workflow execution
  - Error handling and retry logic

---

Made with Bob