# Financial Risk Management - watsonx Orchestrate Deployment

Complete deployment package for Financial Risk Management tools and orchestrator agent to watsonx Orchestrate.

## 🎯 Quick Start

### Prerequisites
```bash
pip install ibm-watsonx-orchestrate
```

### Deploy Everything (Windows PowerShell)
```powershell
.\deploy.ps1
```

### Deploy Everything (Linux/Mac or Python)
```bash
python deploy_to_wxo.py
```

## 📦 What Gets Deployed

### 4 OpenAPI Tools
1. **analyzeTransaction** - Transaction analysis with anomaly detection
2. **assessRisk** - Risk assessment with scoring (0.0-1.0)
3. **detectFraud** - Fraud detection with signals
4. **recommendActions** - Action recommendations (ALERT/REVIEW/BLOCK/MONITOR)

### 1 Orchestrator Agent
- **financial_risk_orchestrator** - Coordinates all tools for comprehensive risk analysis

## 🚀 Deployment Commands

### Option 1: Automated Script (Recommended)
```powershell
# Windows PowerShell
.\deploy.ps1
```

```bash
# Linux/Mac/Python
python deploy_to_wxo.py
```

### Option 2: Manual Commands
```bash
# 1. Login
orchestrate login \
  --url https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024 \
  --apikey xujvDklHEI524wm1Gxl3B3ILLUf1LxdX04kAppOIw-UP

# 2. Import tools (all 4 at once)
orchestrate tools import -k openapi -f openapi_spec.json

# 3. Import agent
orchestrate agents import -f agents/financial_risk_orchestrator.yaml

# 4. Verify
orchestrate tools list
orchestrate agents list
```

## 📁 Files Included

```
.
├── openapi_spec.json                    # OpenAPI spec for all 4 tools
├── agents/
│   └── financial_risk_orchestrator.yaml # Agent definition
├── deploy.ps1                           # PowerShell deployment script
├── deploy_to_wxo.py                     # Python deployment script
├── .env                                 # Environment variables
├── DEPLOYMENT_GUIDE.md                  # Detailed deployment guide
└── README-WXO-DEPLOYMENT.md            # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
WXO_URL=https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024
WXO_APIKEY=xujvDklHEI524wm1Gxl3B3ILLUf1LxdX04kAppOIw-UP
API_BASE_URL=https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
```

## 🧪 Testing

### Test Individual Tools
```bash
# Risk Assessment
orchestrate tools test assessRisk \
  --input '{"account_id": "ACC-12345", "lookback_days": 90}'

# Fraud Detection
orchestrate tools test detectFraud \
  --input '{"account_id": "ACC-12345", "timestamp": "2024/01/15 14:30"}'
```

### Test Orchestrator Agent
Go to watsonx Orchestrate UI and try:
```
Analyze the risk for account ACC-12345
```

## 📊 Agent Workflow

The orchestrator executes tools in this sequence:

1. **assessRisk** → Gets risk_score and risk_level
2. **detectFraud** → Identifies fraud signals
3. **recommendActions** → Provides actionable recommendations
4. **Generates Report** → Consolidates all findings

## 🔍 Verification

After deployment, verify:

```bash
# Check tools
orchestrate tools list
# Should show: analyzeTransaction, assessRisk, detectFraud, recommendActions

# Check agent
orchestrate agents list
# Should show: financial_risk_orchestrator
```

## 🆘 Troubleshooting

### Login Failed
- Verify API key in `.env`
- Check URL is correct
- Ensure network connectivity

### Tools Import Failed
- Verify `openapi_spec.json` exists
- Check API base URL is accessible
- Try importing tools individually

### Agent Import Failed
- Ensure all 4 tools are imported first
- Verify tool names match in agent YAML
- Check agent YAML syntax

## 📚 Documentation

- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide with troubleshooting
- **openapi_spec.json** - Complete API specification
- **agents/financial_risk_orchestrator.yaml** - Agent configuration

## 🎯 Next Steps

1. ✅ Run deployment script
2. ✅ Verify in watsonx Orchestrate UI
3. ✅ Test with sample account IDs
4. ✅ Review generated risk reports
5. ✅ Customize agent instructions as needed

## 🔗 API Endpoints

All tools connect to:
```
https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
```

Endpoints:
- `POST /api/v1/analyze/transaction`
- `POST /api/v1/assess/risk`
- `POST /api/v1/detect/fraud`
- `POST /api/v1/recommend/actions`

## ✅ Success Criteria

Deployment is successful when:
- ✅ All 4 tools appear in `orchestrate tools list`
- ✅ Agent appears in `orchestrate agents list`
- ✅ Agent responds to queries in UI
- ✅ Tools execute without errors
- ✅ Risk reports are generated correctly

## 📞 Support

For issues:
1. Check DEPLOYMENT_GUIDE.md troubleshooting section
2. Verify API endpoint accessibility
3. Review watsonx Orchestrate logs
4. Check ADK documentation

---

**Ready to deploy? Run `.\deploy.ps1` (Windows) or `python deploy_to_wxo.py` (Linux/Mac)** 🚀