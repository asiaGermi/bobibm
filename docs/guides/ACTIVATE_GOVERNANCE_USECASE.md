# Attivare AI Use Case in watsonx.governance

Guida rapida per cambiare lo status dell'AI Use Case da **Draft** → **Active**.

## 🎯 Procedura Rapida

### 1. Accedi a watsonx.governance

```
URL: https://dataplatform.cloud.ibm.com/wx/governance
Instance: gov-675000bo4y (Frankfurt eu-de)
Inventory: Default Inventory
```

### 2. Apri l'AI Use Case

1. Menu laterale → **"AI Use Cases"**
2. Cerca: **"Financial Risk Management - AML Detection"**
3. Clicca per aprire

### 3. Attiva l'Use Case

**Opzione A - Pulsante Status:**
1. Trova il dropdown **"Status"** (in alto o nella sezione Overview)
2. Clicca e seleziona **"Active"**
3. Conferma

**Opzione B - Pulsante Activate:**
1. Cerca il pulsante **"Activate"** o **"Move to Active"**
2. Clicca
3. Rivedi il summary
4. Conferma

### 4. Verifica

Controlla che:
- ✅ Status = "Active"
- ✅ Badge "Active" visibile
- ✅ Lifecycle tracking attivo

## 📋 Informazioni Richieste

Se l'attivazione richiede informazioni aggiuntive, compila:

### Business Information
- **Business Purpose**: "Detect and prevent money laundering through AI-powered risk assessment"
- **Business Value**: "Improve AML detection accuracy and regulatory compliance"

### Risk Assessment
- **Risk Level**: High (già impostato)
- **Risk Factors**: Financial impact, Regulatory requirements (EU AI Act, GDPR, AML)

### Governance Controls
- **Human Oversight**: Required for critical decisions
- **Monitoring**: Continuous model monitoring
- **Audit Trail**: All predictions logged
- **Explainability**: AI explanations for all assessments

## 🔄 Ciclo di Vita (Lifecycle)

Per un sistema AML in produzione, usa questo ciclo di vita:

### Fasi del Lifecycle

**1. Development (Sviluppo)**
- Design del modello
- Training e testing
- Validazione iniziale
- **Durata**: 2-3 mesi

**2. Validation (Validazione)**
- Testing su dati reali
- Valutazione fairness e bias
- Review da compliance team
- **Durata**: 1 mese

**3. Production (Produzione)** ← **Fase Attuale**
- Deployment in ambiente live
- Monitoring continuo
- Logging di tutte le predizioni
- **Durata**: Ongoing

**4. Monitoring (Monitoraggio)**
- Performance tracking
- Model drift detection
- Fairness monitoring
- **Frequenza**: Continuo

**5. Review (Revisione)**
- Quarterly review (ogni 3 mesi)
- Compliance check
- Performance assessment
- **Frequenza**: Trimestrale

**6. Update/Retrain (Aggiornamento)**
- Model retraining se necessario
- Bug fixes e miglioramenti
- **Frequenza**: Semestrale o as-needed

### Configurazione Consigliata

Quando configuri il lifecycle in watsonx.governance:

**Current Phase**: Production
**Next Review**: [Data tra 3 mesi]
**Review Frequency**: Quarterly
**Monitoring**: Enabled
**Alerts**: Enabled for drift, fairness, performance

### Milestone Importanti

- ✅ **Development Complete**: [Data completamento sviluppo]
- ✅ **Validation Passed**: [Data validazione]
- ✅ **Production Deployment**: [Data deploy - oggi]
- 📅 **First Review**: [Data tra 3 mesi]
- 📅 **Annual Audit**: [Data tra 12 mesi]

## ✅ Fatto!

Una volta attivato:
- Status: **Active** ✅
- Monitoring: **Enabled** ✅
- Compliance: **Enforced** ✅

---

**Made with Bob** 🤖