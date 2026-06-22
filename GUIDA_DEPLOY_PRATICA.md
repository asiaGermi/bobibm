# 🚀 Guida Pratica - Deploy Agenti su watsonx Orchestrate

## ✅ Commit Completato!

Il tuo lavoro è stato committato e pushato su GitHub:
- **Commit**: `f6ff43f`
- **Branch**: `main`
- **Repository**: https://github.com/asiaGermi/bobibm.git

---

## 📋 Cosa Hai Ora

8 nuovi file pronti per il deployment:
1. ✅ `openapi_spec.json` - Specifica OpenAPI per 4 tools
2. ✅ `deploy_to_wxo.py` - Script Python deployment
3. ✅ `deploy.ps1` - Script PowerShell deployment
4. ✅ `agents/financial_risk_orchestrator.yaml` - Orchestrator agent
5. ✅ `DEPLOYMENT_GUIDE.md` - Guida completa
6. ✅ `README-WXO-DEPLOYMENT.md` - Quick reference
7. ✅ `COMPARISON_ANALYSIS.md` - Analisi comparativa
8. ✅ `STRATEGIC_RECOMMENDATION.md` - Raccomandazioni strategiche

---

## 🎯 ADESSO: Deploy su watsonx Orchestrate

### Step 1: Installa ADK (2 minuti)

Apri PowerShell e esegui:

```powershell
# Installa IBM watsonx Orchestrate ADK
pip install ibm-watsonx-orchestrate

# Verifica installazione
orchestrate --version
```

**Output atteso**:
```
orchestrate version X.X.X
```

---

### Step 2: Verifica File .env (1 minuto)

Il file `.env` dovrebbe già esistere con le tue credenziali:

```bash
WXO_URL=https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024
WXO_APIKEY=xujvDklHEI524wm1Gxl3B3ILLUf1LxdX04kAppOIw-UP
API_BASE_URL=https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
```

**Verifica**:
```powershell
cat .env
```

Se non esiste, crealo con questi valori.

---

### Step 3: Esegui Deploy (2 minuti)

**Opzione A: Script PowerShell (Raccomandato per Windows)**

```powershell
# Esegui deployment automatico
.\deploy.ps1
```

**Opzione B: Script Python (Alternativa)**

```powershell
# Carica variabili ambiente
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

# Esegui deployment
python deploy_to_wxo.py
```

**Opzione C: Comandi Manuali (Per capire cosa succede)**

```powershell
# 1. Login
orchestrate login `
  --url https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024 `
  --apikey xujvDklHEI524wm1Gxl3B3ILLUf1LxdX04kAppOIw-UP

# 2. Import tools (tutti e 4 insieme)
orchestrate tools import -k openapi -f openapi_spec.json

# 3. Import agent
orchestrate agents import -f agents/financial_risk_orchestrator.yaml

# 4. Verifica
orchestrate tools list
orchestrate agents list
```

---

### Step 4: Verifica Deployment (2 minuti)

**Nel Terminal**:

```powershell
# Lista tools importati
orchestrate tools list
```

**Output atteso**:
```
analyzeTransaction
assessRisk
detectFraud
recommendActions
```

```powershell
# Lista agents importati
orchestrate agents list
```

**Output atteso**:
```
financial_risk_orchestrator
```

---

### Step 5: Test nel UI (3 minuti)

1. **Apri watsonx Orchestrate UI**:
   ```
   https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024
   ```

2. **Vai alla sezione "Agents"**

3. **Cerca "financial_risk_orchestrator"**

4. **Clicca sull'agent per aprirlo**

5. **Testa con una query**:
   ```
   Analyze the risk for account ACC-12345
   ```

**Comportamento atteso**:
L'agent dovrebbe:
1. ✅ Chiamare `assessRisk` per ottenere risk score
2. ✅ Chiamare `detectFraud` per identificare fraud signals
3. ✅ Chiamare `recommendActions` per ottenere raccomandazioni
4. ✅ Generare un report consolidato

---

## 🧪 Test Avanzati

### Test Singoli Tools

```powershell
# Test Risk Assessment
orchestrate tools test assessRisk --input '{\"account_id\": \"ACC-12345\", \"lookback_days\": 90}'

# Test Fraud Detection
orchestrate tools test detectFraud --input '{\"account_id\": \"ACC-12345\", \"timestamp\": \"2024/01/15 14:30\", \"lookback_days\": 30}'

# Test Transaction Analysis
orchestrate tools test analyzeTransaction --input '{\"account_id\": \"ACC-12345\", \"timestamp\": \"2024/01/15 14:30\", \"lookback_days\": 30}'

# Test Recommendations
orchestrate tools test recommendActions --input '{\"account_id\": \"ACC-12345\", \"risk_score\": 0.75, \"lookback_days\": 90}'
```

---

## 🔧 Troubleshooting

### Problema: "orchestrate command not found"

**Soluzione**:
```powershell
pip install ibm-watsonx-orchestrate
# Riavvia PowerShell
```

---

### Problema: "Login failed"

**Soluzione**:
```powershell
# Verifica credenziali
cat .env

# Verifica che WXO_APIKEY sia corretto
# Prova login manuale
orchestrate login --url $env:WXO_URL --apikey $env:WXO_APIKEY
```

---

### Problema: "Tools import failed"

**Soluzione**:
```powershell
# Verifica che openapi_spec.json esista
ls openapi_spec.json

# Verifica che l'API sia raggiungibile
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health

# Prova import manuale
orchestrate tools import -k openapi -f openapi_spec.json
```

---

### Problema: "Agent import failed"

**Soluzione**:
```powershell
# Verifica che i tools siano stati importati prima
orchestrate tools list

# Verifica che il file agent esista
ls agents/financial_risk_orchestrator.yaml

# Prova import manuale
orchestrate agents import -f agents/financial_risk_orchestrator.yaml
```

---

## 📊 Cosa Succede Durante il Deploy

### 1. Login (orchestrate login)
- Autentica con watsonx Orchestrate
- Ottiene token di accesso
- Configura sessione CLI

### 2. Import Tools (orchestrate tools import)
- Legge `openapi_spec.json`
- Crea 4 tools in watsonx Orchestrate:
  - `analyzeTransaction`
  - `assessRisk`
  - `detectFraud`
  - `recommendActions`
- Configura endpoint API per ogni tool

### 3. Import Agent (orchestrate agents import)
- Legge `agents/financial_risk_orchestrator.yaml`
- Crea agent con:
  - Nome: `financial_risk_orchestrator`
  - LLM: `ibm/granite-3-8b-instruct`
  - Tools: tutti e 4 i tools importati
  - Instructions: logica di orchestrazione
- Configura chain-of-thought reasoning

---

## 🎯 Prossimi Passi

### Dopo il Deploy Iniziale

1. **Testa l'agent nel UI** con diversi account_id
2. **Verifica i risultati** dei report generati
3. **Modifica le istruzioni** se necessario
4. **Redeploy** per applicare modifiche

### Modificare l'Agent

```powershell
# 1. Modifica il file
notepad agents/financial_risk_orchestrator.yaml

# 2. Redeploy (30 secondi)
orchestrate agents import -f agents/financial_risk_orchestrator.yaml
```

### Aggiungere Nuovi Tools

```powershell
# 1. Modifica openapi_spec.json
notepad openapi_spec.json

# 2. Redeploy tools (1 minuto)
orchestrate tools import -k openapi -f openapi_spec.json

# 3. Aggiorna agent per usare i nuovi tools
notepad agents/financial_risk_orchestrator.yaml
orchestrate agents import -f agents/financial_risk_orchestrator.yaml
```

---

## 📚 Documentazione di Riferimento

- **DEPLOYMENT_GUIDE.md** - Guida completa con troubleshooting dettagliato
- **README-WXO-DEPLOYMENT.md** - Quick reference per comandi comuni
- **STRATEGIC_RECOMMENDATION.md** - Quando usare questo approccio vs Selvana
- **COMPARISON_ANALYSIS.md** - Confronto dettagliato tra approcci

---

## ✅ Checklist Finale

Prima di considerare il deploy completato:

- [ ] ADK installato e funzionante
- [ ] Login a watsonx Orchestrate riuscito
- [ ] 4 tools importati e visibili in `orchestrate tools list`
- [ ] Agent importato e visibile in `orchestrate agents list`
- [ ] Agent testato nel UI con successo
- [ ] Report generato correttamente
- [ ] Documentazione letta e compresa

---

## 🎉 Successo!

Se hai completato tutti gli step, hai ora:
- ✅ 4 tools operativi su watsonx Orchestrate
- ✅ 1 orchestrator agent funzionante
- ✅ Sistema pronto per analisi di rischio finanziario
- ✅ Deployment automatizzato per future modifiche

**Congratulazioni!** 🚀

---

## 📞 Supporto

Se hai problemi:
1. Controlla la sezione Troubleshooting sopra
2. Leggi DEPLOYMENT_GUIDE.md per dettagli
3. Verifica che l'API backend sia raggiungibile
4. Controlla i log di watsonx Orchestrate nel UI

---

**Pronto per iniziare? Esegui `.\deploy.ps1` ADESSO!** 🚀