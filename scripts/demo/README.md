# Demo Scripts - Financial Risk Management System

Questi script dimostrano il workflow end-to-end del sistema di gestione del rischio finanziario.

## 📋 Script Disponibili

### 1. Python Demo Script (`demo.py`)
Script Python completo con output colorato e formattato.

**Requisiti:**
```bash
pip install requests
```

**Esecuzione:**
```bash
# Da directory root del progetto
python scripts/demo.py

# Oppure rendi eseguibile (Linux/Mac)
chmod +x scripts/demo.py
./scripts/demo.py
```

### 2. PowerShell Demo Script (`demo.ps1`)
Script PowerShell per Windows con output colorato.

**Esecuzione:**
```powershell
# Da directory root del progetto
.\scripts\demo.ps1

# Se hai problemi con execution policy
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\demo.ps1
```

## 🎬 Cosa Fa la Demo

La demo esegue un workflow completo di analisi rischio in 6 step:

### Step 1: Health Check
Verifica che l'API sia online e funzionante.

**Endpoint:** `GET /health`

**Output:**
- Status del sistema
- Stato data layer
- Numero totale transazioni disponibili

### Step 2: Risk Assessment
Calcola il risk score per l'account demo.

**Endpoint:** `POST /api/v1/assess/risk`

**Output:**
- Risk score (0.0-1.0)
- Risk level (LOW/MEDIUM/HIGH)
- Breakdown fattori di rischio
- Lista high-risk accounts

### Step 3: Fraud Detection
Rileva segnali di frode e anomalie.

**Endpoint:** `POST /api/v1/detect/fraud`

**Output:**
- Fraud signals (temporal anomalies, laundering history)
- Account profile (statistiche transazionali)
- Suspicious patterns count

### Step 4: Transaction Analysis
Analizza pattern AML (Anti-Money Laundering).

**Endpoint:** `POST /api/v1/analyze/transaction`

**Output:**
- Pattern AML rilevati (fan-out, fan-in, circular, smurfing)
- Statistiche transazionali
- Account history

### Step 5: Recommendation Generation
Genera raccomandazioni basate sull'analisi.

**Endpoint:** `POST /api/v1/recommend/actions`

**Output:**
- Azioni raccomandate (ALERT, REVIEW, BLOCK, MONITOR)
- Priority per ogni azione
- Reasoning dettagliato

### Step 6: Explanation (IBM watsonx.ai Granite)
Genera spiegazione in linguaggio naturale usando LLM.

**Endpoint:** `POST /api/v1/explain`

**Output:**
- Spiegazione human-readable
- Model utilizzato (ibm/granite-4-h-small)
- Fallback status

### Consolidated Report
Alla fine, genera un report consolidato con tutti i risultati.

## 🔧 Configurazione

### Account Demo
Gli script usano l'account demo predefinito:
```
DEMO_ACCOUNT_ID = "ACC-12345"
```

Per testare con un account diverso, modifica la variabile negli script.

### API Endpoint
```
API_BASE_URL = "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
```

## 📊 Output Esempio

```
================================================================================
        FINANCIAL RISK MANAGEMENT SYSTEM - LIVE DEMO
================================================================================

IBM Open Agentic Builders - Track A: Financial Risk Management
Demo Date: 2026-06-23 10:00:00
API Endpoint: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
Demo Account: ACC-12345

Press Enter to start the demo...

[STEP 1] Health Check - Verifying API Status
   Endpoint: GET .../health

✓ API is healthy!
   Status: healthy
   Data Layer: connected
   Total Transactions: 15,000
   Timestamp: 2026-06-23T08:00:00Z

[STEP 2] Risk Assessment - Analyzing Account ACC-12345
   Endpoint: POST .../api/v1/assess/risk

✓ Risk assessment completed!
   Risk Score: 0.78
   Risk Level: HIGH
   Risk Factors:
      - transaction_volume: 0.85
      - transaction_frequency: 0.72
      - unusual_patterns: 0.90
      - high_value_transactions: 0.65
      - account_age: 0.45

[STEP 3] Fraud Detection - Scanning Account ACC-12345
   Endpoint: POST .../api/v1/detect/fraud

✓ Fraud detection completed!
   Fraud Signals:
      - Temporal Anomalies: 3
      - Laundering History: True
      - Suspicious Patterns: 5

[STEP 4] Transaction Analysis - Detecting AML Patterns for ACC-12345
   Endpoint: POST .../api/v1/analyze/transaction

✓ Transaction analysis completed!
   AML Patterns Detected:
      - fan_out: ✓ DETECTED
      - fan_in: ✗ Not detected
      - circular: ✓ DETECTED
      - smurfing: ✗ Not detected

[STEP 5] Recommendation Generation - Creating Action Plan
   Endpoint: POST .../api/v1/recommend/actions

✓ Recommendations generated!
   Recommended Actions (3):
      1. ALERT (Priority: high)
         Reasoning: High risk score and multiple AML patterns detected
      2. REVIEW (Priority: medium)
         Reasoning: Laundering history requires manual review
      3. MONITOR (Priority: low)
         Reasoning: Continue monitoring for additional suspicious activity

[STEP 6] Explanation Generation - IBM watsonx.ai Granite LLM
   Endpoint: POST .../api/v1/explain

✓ Explanation generated!
   Model Used: ibm/granite-4-h-small
   Fallback Used: False

   Explanation:
   This account shows high risk due to unusual transaction patterns including
   fan-out and circular flows, combined with a confirmed laundering history.
   The risk score of 0.78 indicates immediate attention is required...

================================================================================
        CONSOLIDATED FINANCIAL RISK ANALYSIS REPORT
================================================================================

Report Generated: 2026-06-23 10:00:15
Account ID: ACC-12345
API Endpoint: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud

1. SYSTEM STATUS
   Status: healthy
   Data Layer: connected
   Total Transactions Available: 15,000

2. RISK ASSESSMENT
   Risk Score: 0.78
   Risk Level: HIGH
   Risk Factors:
      - transaction_volume: 0.85
      - transaction_frequency: 0.72
      - unusual_patterns: 0.90
      - high_value_transactions: 0.65
      - account_age: 0.45

3. FRAUD DETECTION
   Temporal Anomalies: 3
   Laundering History: True
   Suspicious Patterns: 5

4. TRANSACTION ANALYSIS
   AML Patterns Detected:
      - fan_out
      - circular
   Transaction Statistics:
      - Total: 1,234
      - Total Amount: $1,234,567.89
      - Average: $1,000.54

5. RECOMMENDED ACTIONS
   1. ALERT (Priority: high)
   2. REVIEW (Priority: medium)
   3. MONITOR (Priority: low)

6. EXPLANATION (IBM watsonx.ai Granite)
   This account shows high risk due to unusual transaction patterns...
   
   Model: ibm/granite-4-h-small

================================================================================

✓ Demo completed successfully!

Next Steps:
   1. Review the consolidated report above
   2. Test with different account IDs
   3. Explore watsonx Orchestrate UI for agent orchestration
   4. Check API documentation at .../docs
```

## 🎯 Use Cases

### 1. Demo per Stakeholder
Esegui lo script durante presentazioni per mostrare il sistema in azione.

### 2. Testing End-to-End
Usa lo script per verificare che tutti gli endpoint funzionino correttamente.

### 3. Performance Baseline
Misura i tempi di risposta per ogni step del workflow.

### 4. Integration Testing
Verifica l'integrazione tra agenti, API e watsonx Orchestrate.

## 🔍 Troubleshooting

### Errore: "Connection refused"
**Causa:** API non raggiungibile
**Soluzione:** Verifica che l'API sia online con:
```bash
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health
```

### Errore: "Account not found"
**Causa:** Account ID non esiste nel dataset
**Soluzione:** Usa un account ID valido dal dataset o usa l'account demo predefinito.

### Errore: "Timeout"
**Causa:** API lenta o sovraccarica
**Soluzione:** Aumenta il timeout negli script o riprova più tardi.

### Output senza colori (Windows)
**Causa:** Terminal non supporta ANSI colors
**Soluzione:** Usa Windows Terminal o PowerShell 7+

## 📝 Personalizzazione

### Cambiare Account Demo
Modifica la variabile negli script:

**Python:**
```python
DEMO_ACCOUNT_ID = "ACC-67890"
```

**PowerShell:**
```powershell
$DEMO_ACCOUNT_ID = "ACC-67890"
```

### Aggiungere Delay tra Step
Modifica i `time.sleep()` (Python) o `Start-Sleep` (PowerShell):

**Python:**
```python
time.sleep(2)  # 2 secondi invece di 1
```

**PowerShell:**
```powershell
Start-Sleep -Seconds 2
```

### Disabilitare Colori
**Python:** Rimuovi le classi `Colors`
**PowerShell:** Rimuovi i parametri `-ForegroundColor`

## 🚀 Next Steps

Dopo aver eseguito la demo:

1. **Esplora watsonx Orchestrate UI**
   - URL: https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024
   - Cerca: `financial_risk_orchestrator`
   - Testa: "Analyze the risk for account ACC-12345"

2. **Testa con Account Diversi**
   - Modifica `DEMO_ACCOUNT_ID` negli script
   - Confronta risultati per account diversi

3. **Integra nel Frontend**
   - Usa gli script come riferimento per chiamate API
   - Implementa UI che chiama gli stessi endpoint

4. **Crea Video Demo**
   - Registra l'esecuzione dello script
   - Aggiungi narrazione per spiegare ogni step

## 📞 Support

Per problemi o domande:
- Controlla i log dell'API su IBM Cloud Code Engine
- Verifica la documentazione OpenAPI: `/docs`
- Consulta `DEPLOYMENT_GUIDE.md` per troubleshooting deployment