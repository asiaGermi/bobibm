# watsonx.governance Integration

Questo modulo fornisce l'integrazione completa con IBM watsonx.governance per il sistema Financial Risk Management.

## 📋 Componenti

### 1. ModelRegistry (`model_registry.py`)
Gestisce la registrazione e il tracking dei modelli AI nel catalogo di governance.

**Funzionalità:**
- Registrazione automatica dei modelli
- Aggiornamento metadata modelli
- Linking modelli a AI Use Cases
- Query informazioni modelli

**Esempio d'uso:**
```python
from src.governance import ModelRegistry

registry = ModelRegistry()

# Registra il modello Granite
result = registry.register_model(
    model_id="ibm/granite-4-h-small",
    model_name="Financial Risk - Granite Explanation Model",
    model_type="foundation_model",
    provider="IBM",
    use_case_id="your-use-case-id"
)
```

### 2. FactsheetManager (`factsheet_manager.py`)
Gestisce gli AI Factsheets per trasparenza e compliance.

**Funzionalità:**
- Creazione AI Factsheets
- Aggiornamento metriche di performance
- Valutazioni di fairness
- Informazioni di compliance

**Esempio d'uso:**
```python
from src.governance import FactsheetManager

manager = FactsheetManager()

# Crea factsheet per Granite
result = manager.create_granite_factsheet()

# Aggiungi metriche di performance
manager.add_performance_metrics(
    factsheet_id=result['factsheet_id'],
    metrics={
        "accuracy": 0.95,
        "response_time": 1.2
    }
)
```

### 3. GovernanceMonitor (`monitoring.py`)
Monitora l'uso dei modelli e logga le predizioni per audit e compliance.

**Funzionalità:**
- Logging predizioni per audit trail
- Tracking metriche modelli
- Rilevamento model drift
- Generazione report di compliance

**Esempio d'uso:**
```python
from src.governance import GovernanceMonitor

monitor = GovernanceMonitor()

# Logga una predizione
monitor.log_explanation(
    model_id="ibm/granite-4-h-small",
    account_id="ACC-12345",
    risk_score=0.73,
    risk_level="high",
    explanation="Account shows high risk...",
    tokens_used=150,
    execution_time=1.5
)

# Ottieni metriche del modello
metrics = monitor.get_model_metrics("ibm/granite-4-h-small")

# Genera report di compliance
report = monitor.generate_compliance_report(
    model_id="ibm/granite-4-h-small",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## 🔧 Configurazione

### Variabili d'Ambiente

Aggiungi queste variabili al tuo file `.env`:

```bash
# watsonx.governance Settings
WATSONX_GOVERNANCE_URL=https://api.dataplatform.cloud.ibm.com
WATSONX_GOVERNANCE_INSTANCE_ID=gov-675000bo4y
WATSONX_GOVERNANCE_API_KEY=your-api-key
WATSONX_GOVERNANCE_CATALOG_ID=itz-saas-290
WATSONX_GOVERNANCE_USECASE_ID=your-usecase-id
ENABLE_GOVERNANCE_TRACKING=true
```

### Installazione Dipendenze

```bash
pip install -r requirements.txt
```

Le dipendenze necessarie sono:
- `ibm-aigov-facts-client>=1.0.0` - Per AI Factsheets
- `ibm-watson-openscale>=3.0.0` - Per model monitoring

## 🚀 Integrazione con ExplanationAgent

L'`ExplanationAgent` è già integrato con la governance. Quando abilitato:

1. **Registrazione Automatica**: Il modello Granite viene registrato automaticamente al primo avvio
2. **Factsheet Creation**: Viene creato un AI Factsheet completo
3. **Prediction Logging**: Ogni spiegazione generata viene loggata per audit

```python
from src.agents import ExplanationAgent

# L'agent si inizializza automaticamente con governance
agent = ExplanationAgent(
    api_key=os.getenv("WATSONX_API_KEY"),
    url=os.getenv("WATSONX_URL"),
    project_id=os.getenv("WATSONX_PROJECT_ID"),
    enable_governance=True  # Default: True se ENABLE_GOVERNANCE_TRACKING=true
)

# Ogni chiamata viene automaticamente loggata
result = agent.run({
    "account_id": "ACC-12345",
    "risk_score": 0.73,
    "risk_level": "high"
})

# Il metadata include info sulla governance
print(result['metadata']['governance_logged'])  # True
```

## 📊 Monitoring e Compliance

### Visualizzare i Log

```python
from src.governance import GovernanceMonitor

monitor = GovernanceMonitor()

# Ottieni gli ultimi 100 log
logs = monitor.get_prediction_logs(
    model_id="ibm/granite-4-h-small",
    limit=100
)

# Filtra per periodo
logs = monitor.get_prediction_logs(
    model_id="ibm/granite-4-h-small",
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-12-31T23:59:59Z"
)
```

### Esportare Log per Audit

```python
# Esporta tutti i log in JSON
result = monitor.export_logs(
    filepath="audit_logs_2024.json",
    model_id="ibm/granite-4-h-small"
)
```

### Generare Report di Compliance

```python
# Report mensile
report = monitor.generate_compliance_report(
    model_id="ibm/granite-4-h-small",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(f"Total predictions: {report['summary']['total_predictions']}")
print(f"Compliance status: {report['compliance_status']}")
```

## 🔒 Compliance e Regolamentazione

Questa integrazione supporta:

- **EU AI Act**: Classificazione High Risk, human oversight, audit trail
- **GDPR**: Data retention, right to explanation, transparency
- **AML Regulations**: Complete audit trail, model monitoring, compliance reporting

### Audit Trail

Ogni predizione viene loggata con:
- Timestamp
- Input data (account_id, risk_score, risk_level)
- Output (explanation, tokens_used)
- Metadata (execution_time, model_version)

### Model Monitoring

Il sistema monitora automaticamente:
- Performance metrics (execution time, token usage)
- Model drift indicators
- Fairness metrics (quando disponibili)

## 🛠️ Troubleshooting

### Governance Disabilitato

Se vedi `"governance_logged": false` nei metadata:

1. Verifica che `ENABLE_GOVERNANCE_TRACKING=true` nel `.env`
2. Controlla che le dipendenze siano installate: `pip install ibm-aigov-facts-client ibm-watson-openscale`
3. Verifica le credenziali di governance nel `.env`

### Mock Mode

Se i moduli girano in "mock mode":

- I log vengono salvati localmente ma non inviati a governance
- Le operazioni continuano a funzionare per sviluppo/test
- Nessun errore viene generato

### Errori di Connessione

Se ci sono errori di connessione a governance:

1. Verifica l'`INSTANCE_ID` e `CATALOG_ID`
2. Controlla che l'API key abbia i permessi corretti
3. Verifica la connettività alla region corretta (eu-de, us-south, etc.)

## 📚 Risorse

- [watsonx.governance Documentation](https://www.ibm.com/docs/en/watsonx/saas?topic=governance)
- [AI Factsheets Guide](https://www.ibm.com/docs/en/watsonx/saas?topic=governance-ai-factsheets)
- [Model Monitoring](https://www.ibm.com/docs/en/watsonx/saas?topic=governance-monitoring-models)

## 🤝 Supporto

Per problemi o domande sull'integrazione governance, contatta il team di compliance o apri un issue nel repository.

---

**Made with Bob** 🤖