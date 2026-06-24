# MCP Server for Financial Risk Management

MCP (Model Context Protocol) server che espone i 5 endpoint dell'API Financial Risk Management come MCP tools per watsonx Orchestrate.

## 🎯 Overview

Questo MCP server wrappa l'API REST esistente su IBM Cloud Code Engine, permettendo a watsonx Orchestrate di utilizzare i tools tramite il protocollo MCP invece che tramite OpenAPI.

**API Base URL:** `https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud`

## 🔧 Tools Disponibili

### 1. analyzeTransaction
Analizza transazioni e rileva pattern AML.

**Input:**
- `account_id` (required): Account identifier
- `timestamp` (required): Transaction timestamp (YYYY/MM/DD HH:MM)
- `lookback_days` (optional): Days to look back (default: 30)

### 2. assessRisk
Valuta il rischio complessivo di un account.

**Input:**
- `account_id` (required): Account identifier
- `lookback_days` (optional): Days to look back (default: 90)

### 3. detectFraud
Rileva segnali di frode.

**Input:**
- `account_id` (required): Account identifier
- `timestamp` (required): Transaction timestamp (YYYY/MM/DD HH:MM)
- `lookback_days` (optional): Days to look back (default: 30)

### 4. recommendActions
Genera raccomandazioni basate sull'analisi.

**Input:**
- `account_id` (required): Account identifier
- `risk_score` (optional): Pre-calculated risk score (0.0-1.0)
- `lookback_days` (optional): Days to look back (default: 90)

### 5. explainRisk
Genera spiegazioni in linguaggio naturale usando IBM watsonx.ai Granite.

**Input:**
- `account_id` (required): Account identifier
- `risk_score` (required): Risk score (0.0-1.0)
- `risk_level` (required): Risk level (minimal/low/medium/high/critical)
- `aml_patterns` (optional): List of AML patterns
- `recommendations` (optional): List of recommendations

## 🚀 Setup Locale

### 1. Installa dipendenze
```bash
cd mcp_server
pip install -r requirements.txt
```

### 2. Test locale (stdio)
```bash
python server.py
```

Il server comunica via stdin/stdout seguendo il protocollo MCP.

## 🐳 Docker Build

```bash
# Build image
docker build -t financial-risk-mcp:latest -f mcp_server/Dockerfile .

# Run container (per test locale)
docker run -p 8080:8080 financial-risk-mcp:latest
```

## ☁️ Deploy su IBM Cloud Code Engine

### 1. Build e push image
```bash
# Login to IBM Container Registry
ibmcloud cr login

# Tag image
docker tag financial-risk-mcp:latest us.icr.io/financial-risk/mcp-server:latest

# Push image
docker push us.icr.io/financial-risk/mcp-server:latest
```

### 2. Deploy su Code Engine
```bash
# Create application
ibmcloud ce application create \
  --name financial-risk-mcp \
  --image us.icr.io/financial-risk/mcp-server:latest \
  --port 8080 \
  --min-scale 1 \
  --max-scale 5 \
  --cpu 0.5 \
  --memory 1G \
  --region eu-de
```

### 3. Get URL
```bash
ibmcloud ce application get --name financial-risk-mcp
```

## 🔗 Registrazione in watsonx Orchestrate

### Via UI
1. Vai su watsonx Orchestrate → Tools → Add MCP Server
2. Seleziona "Remote (SSE)"
3. Inserisci l'URL del server MCP deployato
4. Salva e testa

### Via CLI
```bash
orchestrate mcp-servers add \
  --name financial-risk-mcp \
  --url https://[your-mcp-server-url] \
  --transport sse
```

## 🧪 Testing

### Test singolo tool
```bash
# Via orchestrate CLI (dopo registrazione)
orchestrate tools test assessRisk \
  --input '{"account_id": "ACC-12345", "lookback_days": 90}'
```

### Test in watsonx Orchestrate UI
Prompt di esempio:
```
Analyze the risk for account ACC-12345
```

L'orchestrator agent dovrebbe utilizzare i tools MCP invece degli OpenAPI tools.

## 📊 Architettura

```
┌─────────────────────────────────────────┐
│   watsonx Orchestrate (eu-de)           │
│   - Financial Risk Orchestrator Agent   │
└──────────────┬──────────────────────────┘
               │ MCP Protocol (SSE)
               ▼
┌─────────────────────────────────────────┐
│   MCP Server (Code Engine, eu-de)       │
│   - Port 8080                           │
│   - 5 MCP Tools                         │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────────┐
│   FastAPI (Code Engine, eu-de)          │
│   - 5 REST Endpoints                    │
│   - 5 Specialized Agents                │
└─────────────────────────────────────────┘
```

## 🔍 Differenze vs OpenAPI Tools

| Aspetto | OpenAPI Tools | MCP Tools |
|---------|---------------|-----------|
| Protocollo | REST/HTTP | MCP (stdio/SSE) |
| Registrazione | Import OpenAPI spec | Add MCP server |
| Formato Response | JSON | Formatted text |
| Streaming | No | Possibile |
| Context | Stateless | Può mantenere stato |

## 📝 Note

- Il server MCP fa da proxy all'API REST esistente
- Non modifica la logica di business
- Aggiunge formattazione user-friendly delle risposte
- Timeout configurato a 30 secondi per chiamata
- Supporta sia stdio (locale) che SSE (remoto)

## 🆘 Troubleshooting

### Server non risponde
```bash
# Check logs
ibmcloud ce application logs --name financial-risk-mcp
```

### Tool non trovato in wxO
- Verifica che il server MCP sia registrato
- Controlla che l'URL sia raggiungibile
- Testa con `orchestrate mcp-servers list`

### Errori API
- Verifica che l'API REST sia online: `curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health`
- Controlla i parametri richiesti per ogni tool

## 📚 Riferimenti

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [watsonx Orchestrate MCP Integration](https://www.ibm.com/docs/en/watsonx/orchestrate)