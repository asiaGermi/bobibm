# Deploy Governance Integration to IBM Code Engine

Questa guida spiega come deployare i moduli di governance in produzione su IBM Code Engine.

> **⚠️ NOTA IMPORTANTE**: Docker locale è bloccato da Accenture. Questa guida usa solo IBM Code Engine con rebuild da GitHub.

## 🚀 Deploy Automatico (Raccomandato)

### Usa lo Script Python

Abbiamo creato uno script che automatizza tutto il processo:

```bash
# Esegui lo script di deploy
python scripts/deploy_governance_to_code_engine.py
```

Lo script esegue automaticamente:
1. ✅ Verifica login IBM Cloud
2. ✅ Controlla plugin Code Engine
3. ✅ Mostra info applicazione corrente
4. ✅ Aggiorna variabili d'ambiente governance
5. ✅ Triggera rebuild da GitHub
6. ✅ Monitora il deployment
7. ✅ Verifica il successo

## 📋 Deploy Manuale

Se preferisci eseguire i comandi manualmente:

### Step 1: Verifica Login IBM Cloud

```bash
# Verifica di essere loggato
ibmcloud target

# Se non sei loggato
ibmcloud login --sso
```

### Step 2: Aggiorna Variabili d'Ambiente

```bash
# Aggiungi le variabili di governance
ibmcloud ce application update --name financial-risk-api \
  --env WATSONX_GOVERNANCE_URL=https://api.dataplatform.cloud.ibm.com \
  --env WATSONX_GOVERNANCE_INSTANCE_ID=gov-675000bo4y \
  --env WATSONX_GOVERNANCE_CATALOG_ID=itz-saas-290 \
  --env ENABLE_GOVERNANCE_TRACKING=true
```

### Step 3: Triggera Rebuild da GitHub

**Questo è il comando corretto che usa il rebuild da GitHub:**

```bash
ibmcloud ce application update \
  --name financial-risk-api \
  --build-source https://github.com/asiaGermi/bobibm \
  --build-strategy buildpacks
```

Questo comando:
- ✅ Clona l'ultimo codice da GitHub
- ✅ Rileva automaticamente le dipendenze da `requirements.txt`
- ✅ Include i nuovi moduli `src/governance/`
- ✅ Rebuilda e deploya l'applicazione

### Step 4: Monitora il Deployment

```bash
# Controlla lo stato dell'applicazione
ibmcloud ce application get --name financial-risk-api

# Monitora i log in tempo reale
ibmcloud ce application logs --name financial-risk-api --follow

# Oppure visualizza gli ultimi log
ibmcloud ce application logs --name financial-risk-api --tail 100
```

### Step 5: Verifica il Deployment

```bash
# Ottieni l'URL dell'applicazione
ibmcloud ce application get --name financial-risk-api --output json | grep url

# Test l'endpoint con governance
curl -X POST "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/explain-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "TEST-001",
    "risk_score": 0.75,
    "risk_level": "high",
    "aml_patterns": [{"pattern_type": "smurfing", "severity": "high"}],
    "recommendations": [{"action": "REVIEW", "priority": "high", "reason": "High risk"}]
  }'

# Verifica che la risposta contenga: "governance_logged": true
```

## 🔍 Verifica Post-Deploy

### Checklist di Verifica

- [ ] ✅ Rebuild triggherato da GitHub
- [ ] ✅ Build completato con successo
- [ ] ✅ Variabili d'ambiente governance configurate
- [ ] ✅ API risponde correttamente
- [ ] ✅ `governance_logged: true` nei metadata della risposta
- [ ] ✅ Modello Granite registrato in watsonx.governance
- [ ] ✅ AI Factsheet creato
- [ ] ✅ Predizioni loggate per audit

### Verifica nella UI di watsonx.governance

1. Vai a: https://dataplatform.cloud.ibm.com/wx/governance
2. Naviga a **AI Use Cases** > **Financial Risk Management - AML Detection**
3. Controlla la tab **Lifecycle** per il tracking del modello Granite
4. Vai a **AI Factsheets** e cerca "Financial Risk - Granite Explanation Model"
5. Verifica che le predizioni vengano loggate

### Comandi di Debug

```bash
# Verifica lo stato dell'applicazione
ibmcloud ce application get --name financial-risk-api

# Controlla le variabili d'ambiente
ibmcloud ce application get --name financial-risk-api --output json | grep -A 20 env

# Visualizza i log recenti
ibmcloud ce application logs --name financial-risk-api --tail 200

# Monitora i log in tempo reale
ibmcloud ce application logs --name financial-risk-api --follow

# Verifica la build history
ibmcloud ce buildrun list
```

## 📦 Prerequisiti Git

Prima di eseguire il deploy, assicurati che questi file siano committati su GitHub:

```bash
# Verifica lo stato
git status

# File critici da committare:
git add requirements.txt                    # Nuove dipendenze governance
git add .env.example                        # Template variabili governance
git add src/governance/                     # Nuovi moduli governance
git add src/agents/explanation_agent.py     # Agent modificato
git add scripts/deploy_governance_to_code_engine.py  # Script deploy

# Commit e push
git commit -m "feat: Add watsonx.governance integration"
git push origin main
```

**⚠️ IMPORTANTE**: Il rebuild da GitHub usa il codice nel repository, non quello locale!

## 🚨 Troubleshooting

### Problema: Build fallisce

**Causa**: Codice non committato su GitHub o errori nel codice

**Soluzione:**
```bash
# Verifica che tutto sia pushato
git status
git push origin main

# Controlla i log della build
ibmcloud ce buildrun list
ibmcloud ce buildrun logs --name <buildrun-name>
```

### Problema: Moduli governance non trovati

**Causa**: Directory `src/governance/` non presente nel repository GitHub

**Soluzione:**
```bash
# Verifica che la directory sia tracciata da git
git ls-files src/governance/

# Se vuota, aggiungi i file
git add src/governance/
git commit -m "Add governance modules"
git push origin main

# Triggera nuovo rebuild
python scripts/deploy_governance_to_code_engine.py
```

### Problema: Dipendenze mancanti

**Causa**: `requirements.txt` non aggiornato nel repository

**Soluzione:**
```bash
# Verifica requirements.txt locale
cat requirements.txt | grep governance

# Commit e push
git add requirements.txt
git commit -m "Update requirements with governance SDKs"
git push origin main

# Triggera nuovo rebuild
ibmcloud ce application update --name financial-risk-api \
  --build-source https://github.com/asiaGermi/bobibm \
  --build-strategy buildpacks
```

### Problema: Variabili d'ambiente non caricate

**Causa**: Variabili non configurate in Code Engine

**Soluzione:**
```bash
# Lista le variabili correnti
ibmcloud ce application get --name financial-risk-api --output json | grep -A 50 env

# Aggiungi le variabili mancanti
ibmcloud ce application update --name financial-risk-api \
  --env WATSONX_GOVERNANCE_URL=https://api.dataplatform.cloud.ibm.com \
  --env WATSONX_GOVERNANCE_INSTANCE_ID=gov-675000bo4y \
  --env WATSONX_GOVERNANCE_CATALOG_ID=itz-saas-290 \
  --env ENABLE_GOVERNANCE_TRACKING=true
```

### Problema: governance_logged è false

**Causa**: Governance disabilitato o credenziali mancanti

**Soluzione:**
```bash
# Verifica che ENABLE_GOVERNANCE_TRACKING sia true
ibmcloud ce application get --name financial-risk-api --output json | grep ENABLE_GOVERNANCE_TRACKING

# Verifica le credenziali
ibmcloud ce application get --name financial-risk-api --output json | grep WATSONX_GOVERNANCE

# Se mancanti, aggiungile
python scripts/deploy_governance_to_code_engine.py
```

## 📊 Monitoring Post-Deploy

### Verifica Continua

```bash
# Script di monitoring (esegui ogni 5 minuti)
while true; do
  echo "=== $(date) ==="
  curl -s http://localhost:8000/api/v1/health | jq
  sleep 300
done
```

### Log Governance

```bash
# Esporta i log di governance dal container
docker-compose exec api python -c "
from src.governance import GovernanceMonitor
m = GovernanceMonitor()
m.export_logs('/app/governance_logs.json')
"

# Copia i log fuori dal container
docker cp $(docker-compose ps -q api):/app/governance_logs.json ./governance_logs.json
```

## ✅ Completamento

Una volta completati tutti gli step, la tua applicazione in produzione avrà:

- ✅ Moduli governance integrati
- ✅ Logging automatico delle predizioni
- ✅ AI Factsheets attivi
- ✅ Compliance monitoring operativo
- ✅ Audit trail completo

---

**Made with Bob** 🤖