# MCP Server Integration Guide

Guida completa per l'integrazione del MCP Server nel progetto Financial Risk Management.

## 📋 Indice

1. [Overview](#overview)
2. [Architettura](#architettura)
3. [Setup Locale](#setup-locale)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Integrazione watsonx Orchestrate](#integrazione-watsonx-orchestrate)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Il **MCP (Model Context Protocol) Server** espone i 5 endpoint dell'API Financial Risk Management come MCP tools, permettendo a watsonx Orchestrate di utilizzarli tramite il protocollo MCP invece che tramite OpenAPI REST.

### Vantaggi MCP vs OpenAPI

| Aspetto | OpenAPI Tools | MCP Tools |
|---------|---------------|-----------|
| Protocollo | REST/HTTP | MCP (stdio/SSE) |
| Formato Response | JSON grezzo | Testo formattato |
| Streaming | No | Sì |
| Context Management | Stateless | Può mantenere stato |
| User Experience | Tecnico | User-friendly |

### Tools Disponibili

1. **analyzeTransaction** - Analisi transazioni e pattern AML
2. **assessRisk** - Valutazione rischio complessivo
3. **detectFraud** - Rilevamento segnali di frode
4. **recommendActions** - Generazione raccomandazioni
5. **explainRisk** - Spiegazioni in linguaggio naturale (Granite LLM)

---

## Architettura

```
┌─────────────────────────────────────────────────────────┐
│              watsonx Orchestrate (eu-de)                 │
│         Financial Risk Orchestrator Agent                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ OpenAPI Tools│          │  MCP Tools   │
│  (REST API)  │          │ (MCP Server) │
└──────┬───────┘          └──────┬───────┘
       │                         │
       │    ┌────────────────────┘
       │    │
       ▼    ▼
┌─────────────────────────────────────────────────────────┐
│         FastAPI Application (Code Engine)                │
│              5 Specialized Agents                        │
│         https://financial-risk-api...                    │
└─────────────────────────────────────────────────────────┘
```

### Flusso di Comunicazione

1. **User** → Prompt in watsonx Orchestrate UI
2. **Orchestrator Agent** → Decide quale tool usare (OpenAPI o MCP)
3. **MCP Server** → Riceve richiesta via protocollo MCP
4. **MCP Server** → Chiama API REST su Code Engine
5. **FastAPI** → Esegue logica business con agenti specializzati
6. **MCP Server** → Formatta risposta in testo user-friendly
7. **Orchestrator Agent** → Presenta risultato all'utente

---

## Setup Locale

### Prerequisiti

- Python 3.11+
- pip
- Docker (opzionale, per test containerizzato)

### 1. Installa Dipendenze

```bash
cd mcp_server
pip install -r requirements.txt
```

**Dipendenze:**
- `mcp>=1.0.0` - SDK ufficiale MCP
- `httpx>=0.27.0` - Client HTTP async

### 2. Verifica Installazione

```bash
python -c "import mcp; print('MCP SDK installed successfully')"
```

### 3. Struttura Directory

```
mcp_server/
├── server.py           # MCP server implementation
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container image definition
├── README.md          # Documentation
├── test_mcp.py        # Test suite
├── deploy.sh          # Linux/Mac deployment script
├── deploy.ps1         # Windows deployment script
└── .gitignore         # Git ignore rules
```

---

## Testing

### Test Locale (Stdio Mode)

Il server MCP comunica via stdin/stdout. Per testare:

```bash
cd mcp_server
python test_mcp.py
```

**Output atteso:**
```
================================================================================
MCP Server Test Suite
================================================================================

✓ MCP server module imported successfully

Test 1/5: Risk Assessment
--------------------------------------------------------------------------------
Tool: assessRisk
Arguments: {
  "account_id": "ACC-12345",
  "lookback_days": 90
}

Response:
## Risk Assessment: ACC-12345
**Analysis Period:** 90 days
...

✓ PASS assessRisk: Tool executed successfully
...
```

### Test con Account Reale

Modifica `test_mcp.py` per usare un account ID reale dal dataset:

```python
test_account = "8000EBD30"  # Account dal dataset HI-Small_Trans
```

### Test Singolo Tool

```python
import asyncio
from server import call_tool

async def test_single():
    result = await call_tool("assessRisk", {
        "account_id": "ACC-12345",
        "lookback_days": 90
    })
    print(result[0].text)

asyncio.run(test_single())
```

---

## Deployment

### Opzione 1: Deploy Automatico (Raccomandato)

**Windows (PowerShell):**
```powershell
# Set API key
$env:IBM_CLOUD_API_KEY = "your-api-key"

# Run deployment
.\mcp_server\deploy.ps1
```

**Linux/Mac (Bash):**
```bash
# Set API key
export IBM_CLOUD_API_KEY="your-api-key"

# Make script executable
chmod +x mcp_server/deploy.sh

# Run deployment
./mcp_server/deploy.sh
```

### Opzione 2: Deploy Manuale

#### Step 1: Build Docker Image

```bash
docker build -t financial-risk-mcp:latest -f mcp_server/Dockerfile .
```

#### Step 2: Login to IBM Cloud

```bash
ibmcloud login --apikey YOUR_API_KEY -r eu-de
ibmcloud ce project select --name financial-risk
```

#### Step 3: Push to Container Registry

```bash
# Login to registry
ibmcloud cr login

# Tag image
docker tag financial-risk-mcp:latest us.icr.io/financial-risk/mcp-server:latest

# Push image
docker push us.icr.io/financial-risk/mcp-server:latest
```

#### Step 4: Deploy to Code Engine

```bash
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

#### Step 5: Get Application URL

```bash
ibmcloud ce application get --name financial-risk-mcp
```

**Output:**
```
URL: https://financial-risk-mcp.xxx.eu-de.codeengine.appdomain.cloud
```

---

## Integrazione watsonx Orchestrate

### Registrazione MCP Server

#### Via UI

1. Vai su **watsonx Orchestrate** → **Tools** → **Add MCP Server**
2. Seleziona **Remote (SSE)**
3. Inserisci:
   - **Name:** `financial-risk-mcp`
   - **URL:** `https://financial-risk-mcp.xxx.eu-de.codeengine.appdomain.cloud`
   - **Transport:** `sse`
4. Clicca **Save**
5. Verifica che i 5 tools appaiano nella lista

#### Via CLI

```bash
orchestrate mcp-servers add \
  --name financial-risk-mcp \
  --url https://financial-risk-mcp.xxx.eu-de.codeengine.appdomain.cloud \
  --transport sse
```

### Verifica Registrazione

```bash
# List MCP servers
orchestrate mcp-servers list

# List tools (should show 5 new MCP tools)
orchestrate tools list | grep -E "(analyzeTransaction|assessRisk|detectFraud|recommendActions|explainRisk)"
```

### Test in watsonx Orchestrate UI

Vai su watsonx Orchestrate UI e prova questi prompt:

```
Analyze the risk for account ACC-12345
```

```
Detect fraud for account ACC-12345 at timestamp 2024/01/15 14:30
```

```
Explain the risk assessment for account ACC-12345 with risk score 0.75 and high risk level
```

L'orchestrator agent dovrebbe utilizzare i tools MCP e presentare risposte formattate.

---

## Troubleshooting

### Problema: MCP SDK non installato

**Errore:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Soluzione:**
```bash
pip install mcp httpx
```

### Problema: API non raggiungibile

**Errore:**
```
API Error (503): Service Unavailable
```

**Soluzione:**
1. Verifica che l'API sia online:
   ```bash
   curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health
   ```
2. Se l'API è in sleep mode, risvegliala con una chiamata
3. Attendi 30-60 secondi per il cold start

### Problema: MCP Server non risponde

**Errore:**
```
Connection timeout
```

**Soluzione:**
1. Verifica deployment:
   ```bash
   ibmcloud ce application get --name financial-risk-mcp
   ```
2. Controlla logs:
   ```bash
   ibmcloud ce application logs --name financial-risk-mcp
   ```
3. Verifica che min-scale sia >= 1 (no cold start)

### Problema: Tools non appaiono in wxO

**Soluzione:**
1. Verifica registrazione MCP server:
   ```bash
   orchestrate mcp-servers list
   ```
2. Re-registra se necessario:
   ```bash
   orchestrate mcp-servers remove --name financial-risk-mcp
   orchestrate mcp-servers add --name financial-risk-mcp --url YOUR_URL --transport sse
   ```
3. Refresh della pagina Tools in wxO UI

### Problema: Formato risposta non corretto

**Causa:** Il server MCP formatta le risposte in testo markdown per user-friendliness.

**Verifica:** Controlla le funzioni `format_*` in `server.py` per personalizzare il formato.

---

## Best Practices

### 1. Monitoring

Monitora le metriche del MCP server:

```bash
# View logs
ibmcloud ce application logs --name financial-risk-mcp --follow

# Check metrics
ibmcloud ce application get --name financial-risk-mcp
```

### 2. Scaling

Configura auto-scaling appropriato:

```bash
ibmcloud ce application update \
  --name financial-risk-mcp \
  --min-scale 1 \
  --max-scale 10 \
  --concurrency 100
```

### 3. Error Handling

Il server MCP gestisce automaticamente:
- Timeout API (30s)
- Errori HTTP (4xx, 5xx)
- Errori di parsing JSON
- Connessioni fallite

### 4. Security

- ✅ Non-root user nel container
- ✅ HTTPS per tutte le comunicazioni
- ✅ No credenziali hardcoded
- ✅ Minimal base image (Python slim)

---

## Prossimi Step

1. ✅ **Deploy MCP Server** su IBM Cloud Code Engine
2. ✅ **Registra** in watsonx Orchestrate
3. ✅ **Testa** tutti i 5 tools
4. ⏭️ **Confronta** performance MCP vs OpenAPI
5. ⏭️ **Ottimizza** formattazione risposte
6. ⏭️ **Documenta** best practices per il team

---

## Riferimenti

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [watsonx Orchestrate Docs](https://www.ibm.com/docs/en/watsonx/orchestrate)
- [IBM Cloud Code Engine](https://cloud.ibm.com/docs/codeengine)

---

**Ultimo aggiornamento:** 24 Giugno 2026  
**Autore:** Bob (AI Assistant)  
**Versione:** 1.0.0