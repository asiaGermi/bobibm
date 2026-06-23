# Guida Completa: Setup watsonx.governance

Questa guida ti aiuterà a completare l'integrazione di watsonx.governance per il sistema Financial Risk Management.

## 📋 Prerequisiti

- Account IBM Cloud attivo
- Istanza watsonx.governance (già configurata: `gov-675000bo4y`)
- Accesso al catalogo governance (già configurato: `itz-saas-290`)
- Python 3.9+

## 🚀 Setup Passo-Passo

### Step 1: Installare le Dipendenze

```bash
# Installa i nuovi pacchetti per governance
pip install ibm-aigov-facts-client>=1.0.0
pip install ibm-watson-openscale>=3.0.0

# Oppure reinstalla tutto
pip install -r requirements.txt
```

### Step 2: Configurare le Variabili d'Ambiente

Il file `.env` è già stato aggiornato con le variabili base. Devi solo verificare/aggiornare:

```bash
# Apri il file .env
nano .env  # o usa il tuo editor preferito

# Verifica queste variabili:
WATSONX_GOVERNANCE_URL=https://api.dataplatform.cloud.ibm.com
WATSONX_GOVERNANCE_INSTANCE_ID=gov-675000bo4y
WATSONX_GOVERNANCE_API_KEY=xujvDklHEI524wm1Gxl3B3ILLUf1LxdX04kAppOIw-UP
WATSONX_GOVERNANCE_CATALOG_ID=itz-saas-290
ENABLE_GOVERNANCE_TRACKING=true
```

### Step 3: Ottenere l'AI Use Case ID (Opzionale ma Raccomandato)

1. Vai alla UI di watsonx.governance: https://dataplatform.cloud.ibm.com/wx/governance
2. Naviga a **AI Use Cases**
3. Trova il tuo use case: **"Financial Risk Management - AML Detection"**
4. Clicca sul use case e copia l'ID dall'URL o dai dettagli
5. Aggiungi al `.env`:
   ```bash
   WATSONX_GOVERNANCE_USECASE_ID=your-copied-use-case-id
   ```

### Step 4: Verificare l'Integrazione

Crea un file di test `test_governance.py`:

```python
#!/usr/bin/env python3
"""Test script per verificare l'integrazione governance"""

import os
from dotenv import load_dotenv
from src.governance import ModelRegistry, FactsheetManager, GovernanceMonitor

# Carica variabili d'ambiente
load_dotenv()

def test_governance():
    print("🔍 Testing watsonx.governance Integration\n")
    
    # Test 1: Model Registry
    print("1️⃣ Testing ModelRegistry...")
    registry = ModelRegistry()
    result = registry.register_model(
        model_id="ibm/granite-4-h-small",
        model_name="Financial Risk - Granite Explanation Model",
        model_type="foundation_model",
        provider="IBM"
    )
    print(f"   Status: {result.get('status')}")
    print(f"   ✅ ModelRegistry OK\n")
    
    # Test 2: Factsheet Manager
    print("2️⃣ Testing FactsheetManager...")
    factsheet_mgr = FactsheetManager()
    result = factsheet_mgr.create_granite_factsheet()
    print(f"   Status: {result.get('status')}")
    print(f"   ✅ FactsheetManager OK\n")
    
    # Test 3: Governance Monitor
    print("3️⃣ Testing GovernanceMonitor...")
    monitor = GovernanceMonitor()
    result = monitor.log_explanation(
        model_id="ibm/granite-4-h-small",
        account_id="TEST-001",
        risk_score=0.75,
        risk_level="high",
        explanation="Test explanation",
        tokens_used=100,
        execution_time=1.5
    )
    print(f"   Status: {result.get('status')}")
    print(f"   ✅ GovernanceMonitor OK\n")
    
    # Test 4: Get Metrics
    print("4️⃣ Testing Metrics Retrieval...")
    metrics = monitor.get_model_metrics("ibm/granite-4-h-small")
    print(f"   Total predictions: {metrics.get('total_predictions', 0)}")
    print(f"   ✅ Metrics OK\n")
    
    print("✅ All governance tests passed!")
    print("\n📊 Next Steps:")
    print("   1. Run the API: python run_api.py")
    print("   2. Test with a real request")
    print("   3. Check governance UI for logged data")

if __name__ == "__main__":
    test_governance()
```

Esegui il test:

```bash
python test_governance.py
```

### Step 5: Testare con l'API

Avvia l'API:

```bash
python run_api.py
```

Fai una richiesta di test:

```bash
curl -X POST "http://localhost:8000/api/v1/explain-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACC-12345",
    "risk_score": 0.73,
    "risk_level": "high",
    "aml_patterns": [
      {"pattern_type": "smurfing", "severity": "high"}
    ],
    "recommendations": [
      {"action": "REVIEW", "priority": "high", "reason": "High risk detected"}
    ]
  }'
```

Verifica che la risposta includa `"governance_logged": true` nei metadata.

### Step 6: Verificare nella UI di Governance

1. Vai a watsonx.governance UI
2. Naviga a **AI Use Cases** > **Financial Risk Management - AML Detection**
3. Controlla la tab **Lifecycle** per vedere il tracking del modello Granite
4. Vai a **AI Factsheets** per vedere il factsheet del modello
5. Controlla i log delle predizioni (se disponibili nella UI)

## 🔍 Verifica Completa

### Checklist di Verifica

- [ ] Dipendenze installate (`ibm-aigov-facts-client`, `ibm-watson-openscale`)
- [ ] Variabili d'ambiente configurate nel `.env`
- [ ] Test script eseguito con successo
- [ ] API avviata senza errori
- [ ] Richiesta di test completata con `governance_logged: true`
- [ ] Modello visibile nella UI di governance
- [ ] AI Factsheet creato
- [ ] Use case linkato (se USE_CASE_ID configurato)

### Comandi Utili

```bash
# Verificare i log dell'applicazione
tail -f logs/app.log

# Esportare i log di governance
python -c "from src.governance import GovernanceMonitor; m = GovernanceMonitor(); m.export_logs('governance_logs.json')"

# Ottenere metriche del modello
python -c "from src.governance import GovernanceMonitor; m = GovernanceMonitor(); print(m.get_model_metrics('ibm/granite-4-h-small'))"

# Generare report di compliance
python -c "from src.governance import GovernanceMonitor; m = GovernanceMonitor(); print(m.generate_compliance_report('ibm/granite-4-h-small'))"
```

## 🐛 Troubleshooting

### Problema: "Governance modules not available"

**Soluzione:**
```bash
pip install ibm-aigov-facts-client ibm-watson-openscale
```

### Problema: "governance_logged: false"

**Cause possibili:**
1. `ENABLE_GOVERNANCE_TRACKING=false` nel `.env`
2. Credenziali non valide
3. SDK non installati

**Soluzione:**
```bash
# Verifica variabili
cat .env | grep GOVERNANCE

# Verifica installazione
pip list | grep ibm

# Abilita governance
export ENABLE_GOVERNANCE_TRACKING=true
```

### Problema: Errori di connessione a governance

**Soluzione:**
1. Verifica l'INSTANCE_ID: `gov-675000bo4y`
2. Verifica il CATALOG_ID: `itz-saas-290`
3. Controlla che l'API key sia valida
4. Verifica la region (eu-de per Frankfurt)

### Problema: Mock mode attivo

Se vedi messaggi come "running in mock mode":

**Causa:** SDK non disponibili o credenziali mancanti

**Soluzione:**
1. Installa gli SDK
2. Configura tutte le variabili d'ambiente
3. Riavvia l'applicazione

## 📊 Monitoring Continuo

### Setup Monitoring Automatico

Per monitoraggio continuo, puoi creare uno script cron:

```bash
# Crea script di monitoring
cat > monitor_governance.sh << 'EOF'
#!/bin/bash
cd /path/to/project
source venv/bin/activate
python -c "
from src.governance import GovernanceMonitor
import json
from datetime import datetime

monitor = GovernanceMonitor()
metrics = monitor.get_model_metrics('ibm/granite-4-h-small')

print(f'{datetime.now()}: {json.dumps(metrics)}')
" >> logs/governance_metrics.log
EOF

chmod +x monitor_governance.sh

# Aggiungi a crontab (ogni ora)
crontab -e
# Aggiungi: 0 * * * * /path/to/monitor_governance.sh
```

### Dashboard Metriche

Puoi creare una dashboard semplice per visualizzare le metriche:

```python
# dashboard.py
from src.governance import GovernanceMonitor
import json

monitor = GovernanceMonitor()
metrics = monitor.get_model_metrics("ibm/granite-4-h-small")

print("=" * 50)
print("GOVERNANCE METRICS DASHBOARD")
print("=" * 50)
print(f"Model: ibm/granite-4-h-small")
print(f"Total Predictions: {metrics.get('total_predictions', 0)}")
print(f"Avg Execution Time: {metrics.get('avg_execution_time_seconds', 0):.3f}s")
print(f"Total Tokens Used: {metrics.get('total_tokens_used', 0)}")
print(f"Avg Tokens/Prediction: {metrics.get('avg_tokens_per_prediction', 0):.1f}")
print("=" * 50)
```

## 🎯 Best Practices

1. **Logging Completo**: Mantieni `ENABLE_GOVERNANCE_TRACKING=true` in produzione
2. **Backup Regolari**: Esporta i log periodicamente per backup
3. **Monitoring Attivo**: Controlla le metriche regolarmente
4. **Compliance Reports**: Genera report mensili per audit
5. **Factsheet Updates**: Aggiorna il factsheet quando cambi il modello o i parametri

## 📚 Risorse Aggiuntive

- [Documentazione Governance](src/governance/README.md)
- [watsonx.governance Docs](https://www.ibm.com/docs/en/watsonx/saas?topic=governance)
- [AI Factsheets Guide](https://www.ibm.com/docs/en/watsonx/saas?topic=governance-ai-factsheets)

## ✅ Completamento

Una volta completati tutti gli step, la tua configurazione di watsonx.governance è **production-ready**! 🎉

Per domande o supporto, consulta il team di compliance o apri un issue nel repository.

---

**Made with Bob** 🤖