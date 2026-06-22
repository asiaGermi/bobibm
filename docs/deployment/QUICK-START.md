# Quick Start - Deployment bobibm

Guida completa per deployment automatizzato su IBM Cloud con Watson X.

---

## 📋 Cosa Contiene Questo Lavoro

### Script Creato
- **`scripts/deploy_unified.py`** - Deployment automatizzato completo
- **`scripts/README.md`** - Guida dettagliata uso script

### Cosa Fa lo Script
1. ✅ Build Docker image
2. ✅ Push a Container Registry
3. ✅ Deploy Code Engine via API
4. ✅ Registra 4 skills Watson X
5. ✅ Health check automatico

### Cosa Cambia per Te
**PRIMA**: 3+ comandi manuali ogni deploy
**ADESSO**: 1 comando automatico

```bash
# Prima
docker build ...
docker push ...
ibmcloud ce app update ...

# Adesso
python scripts/deploy_unified.py --environment production
```

---

## ⚡ Setup Rapido (5 minuti)

### 1. Prerequisiti

**Opzione A: Usa WSL (Raccomandato se hai già ibmcloud su WSL)**
```bash
# Entra in WSL
wsl

# Vai al progetto
cd /mnt/c/Users/selvana.hosni.badir/OneDrive\ -\ Accenture/Documents/ibm\ corso/bobibm
```

**Opzione B: Windows Nativo**
- Scarica IBM Cloud CLI: https://download.clis.cloud.ibm.com/ibm-cloud-cli/2.23.0/IBM_Cloud_CLI_2.23.0_windows_amd64.msi
- Installa e riavvia PowerShell

**Verifica Setup**:
```bash
python --version  # Deve essere 3.11+
pip install requests
ibmcloud --version  # (opzionale, lo script usa API)
```

### 2. Configura Variabili Ambiente

Crea un file `.env` nella root del progetto:

```bash
# Copia il template
cp .env.example .env

# Edita con i tuoi valori
nano .env
```

**Valori da configurare**:

```bash
# IBM Cloud
IBM_CLOUD_API_KEY=your-ibm-cloud-api-key

# Watson X Orchestrate (già configurato)
WATSONX_INSTANCE_URL=https://api.eu-de.watson-orchestrate.cloud.ibm.com
WATSONX_API_KEY=your-watsonx-api-key

# Code Engine (già configurato)
CODE_ENGINE_PROJECT_ID=ce-675000bo4y
IBM_CLOUD_REGION=eu-de
REGISTRY_NAMESPACE=financial-risk
```

### 3. Carica Variabili Ambiente

```bash
# PowerShell (Windows)
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Bash (Linux/Mac)
export $(cat .env | xargs)
```

### 4. Primo Deploy

```bash
# Deploy su staging (default)
python scripts/deploy_unified.py

# Output atteso:
# 🚀 Deployment Unificato - IBM Cloud & Watson X
# [1/5] 🐳 Build e Push Docker Image
# [2/5] 📦 Deploy su IBM Cloud Code Engine
# [3/5] ⏳ Verifica Deployment
# [4/5] 🏥 Health Check
# [5/5] 🤖 Integrazione Watson X Orchestrate
# ✅ Deployment completato con successo!
```

### 5. Verifica

```bash
# Health check
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health

# API Docs
open https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/docs
```

---

## 🎯 Comandi Utili

### Deploy su Production

```bash
python scripts/deploy_unified.py \
  --environment production \
  --image-tag v1.0.0
```

### Deploy Rapido (Skip Build)

```bash
# Usa immagine già esistente
python scripts/deploy_unified.py --skip-build
```

### Deploy Solo Code Engine (Skip Watson X)

```bash
# Utile per test rapidi
python scripts/deploy_unified.py --skip-watsonx
```

### Verifica Status App

```bash
# Via CLI
ibmcloud ce app get --name financial-risk-api

# Via API
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health
```

### Visualizza Logs

```bash
# Logs in tempo reale
ibmcloud ce app logs --name financial-risk-api --follow

# Ultimi 100 log
ibmcloud ce app logs --name financial-risk-api --tail 100
```

---

## 🧪 Test API Endpoints

### 1. Health Check

```bash
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health
```

**Risposta attesa**:
```json
{
  "status": "healthy",
  "data_layer_status": "connected",
  "total_transactions": 15000,
  "timestamp": "2026-06-22T13:00:00Z"
}
```

### 2. Transaction Analysis

```bash
curl -X POST \
  https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/analyze/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACC001",
    "days": 30
  }'
```

### 3. Risk Assessment

```bash
curl -X POST \
  https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/assess/risk \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACC001",
    "mode": "standard"
  }'
```

### 4. Fraud Detection

```bash
curl -X POST \
  https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/detect/fraud \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACC001",
    "mode": "account_profile"
  }'
```

### 5. Recommendations

```bash
curl -X POST \
  https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/recommend/actions \
  -H "Content-Type: application/json" \
  -d '{
    "risk_score": 0.75,
    "patterns": ["fan_out", "circular"],
    "fraud_signals": []
  }'
```

---

## 🤖 Watson X Orchestrate

### Verifica Skills Registrate

Le seguenti skills vengono registrate automaticamente:

1. **transaction-analysis** - Analisi transazioni
2. **risk-assessment** - Valutazione rischio
3. **fraud-detection** - Rilevamento frodi
4. **recommendation** - Raccomandazioni

### Accedi a Watson X

1. Vai a: https://api.eu-de.watson-orchestrate.cloud.ibm.com
2. Login con le tue credenziali IBM Cloud
3. Verifica che le skills siano visibili nella sezione "Skills"

### Test Skill da Watson X

Puoi testare le skills direttamente dall'interfaccia Watson X:

1. Seleziona una skill (es. "transaction-analysis")
2. Inserisci input di test:
   ```json
   {
     "account_id": "ACC001",
     "days": 30
   }
   ```
3. Esegui e verifica il risultato

---

## 🔧 Troubleshooting

### Errore: "IBM_CLOUD_API_KEY non impostata"

```bash
# Verifica che la variabile sia impostata
echo $IBM_CLOUD_API_KEY  # Linux/Mac
echo $env:IBM_CLOUD_API_KEY  # PowerShell

# Se vuota, ricarica .env
export $(cat .env | xargs)  # Linux/Mac
```

### Errore: "Docker build failed"

```bash
# Verifica Docker
docker ps

# Se non funziona, usa --skip-build
python scripts/deploy_unified.py --skip-build
```

### Errore: "Health check failed"

```bash
# Verifica logs
ibmcloud ce app logs --name financial-risk-api

# Verifica status
ibmcloud ce app get --name financial-risk-api

# Attendi qualche minuto e riprova
```

### Watson X: "Errore registrazione skill"

Lo script prova prima `/api/v1/auth/token`; se fallisce, usa l'API key direttamente come fallback automatico (verrà mostrato un warning ma il deployment continua).

```bash
# Salta Watson X per ora
python scripts/deploy_unified.py --skip-watsonx

# Registra skills manualmente dopo
```

---

## 📊 Monitoring

### Dashboard IBM Cloud

1. Vai a: https://cloud.ibm.com/codeengine/projects
2. Seleziona progetto: `ce-675000bo4y`
3. Visualizza metriche, logs, e status

### Logs in Tempo Reale

```bash
# Segui i logs
ibmcloud ce app logs --name financial-risk-api --follow

# Filtra per errori
ibmcloud ce app logs --name financial-risk-api | grep ERROR
```

### Metriche

```bash
# CPU e Memory usage
ibmcloud ce app get --name financial-risk-api --output json | jq '.status'
```

---

## 🚀 Next Steps

Dopo il primo deployment:

1. ✅ Verifica tutti gli endpoint API
2. ✅ Testa skills Watson X
3. ✅ Crea workflow orchestrato in Watson X
4. ✅ Setup monitoring e alerting
5. ✅ Configura CI/CD con GitHub Actions

---

## 📚 Documentazione Completa

- [API Deployment Strategy](./api-deployment-strategy.md) - Strategia completa
- [Scripts README](../../scripts/README.md) - Guida script

---

**Ultimo aggiornamento**: 22 Giugno 2026  
**App URL**: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud  
**Watson X URL**: https://api.eu-de.watson-orchestrate.cloud.ibm.com