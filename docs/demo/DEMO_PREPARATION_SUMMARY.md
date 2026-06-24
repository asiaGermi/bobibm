# Demo Preparation Summary — 24 Giugno 2026

## ✅ Stato Attuale: PRONTO PER DEMO

### Sistema in produzione
**URL:** `https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud`  
**Dashboard:** `/dashboard`  
**API Docs:** `/api/v1/docs`

---

## 🏗️ Architettura Attuale

```
IBM Cloud Infrastructure
├── IBM Code Engine (eu-de)
│   ├── FastAPI Application (10 endpoint REST)
│   ├── 5 Agenti Specializzati (Risk, Fraud, Recommend, Explanation, Orchestrator)
│   └── Dashboard web 4-tab (static/index.html)
├── IBM Container Registry (eu-de)
│   └── private.de.icr.io/financial-risk/financial-risk-management:latest
├── IBM watsonx.ai (eu-de)
│   └── ibm/granite-4-h-small — spiegazioni linguaggio naturale
└── IBM Watson OpenScale / watsonx.governance (eu-de)
    ├── Data Mart: bc2c304b-0513-4bad-832c-6ecf916274af
    ├── Subscription: 019ef96a-44d2-7ebf-85e4-c9c53923009e
    └── Payload Dataset: 019ef96a-4884-7ded-8911-4b3219e64327
```

---

## 📊 Dashboard — 4 Tab

### Tab 1: 📊 Analisi Rischio
**Flusso automatico 2-step:**
1. Inserisci Account ID → click "Analizza Rischio"
2. Step 1: `POST /assess/risk` → calcola score da CSV → mostra metriche + AML patterns
3. Step 2: `POST /explain` → IBM Granite genera spiegazione → mostra testo AI

**Account di test consigliati:**
- `100428660` → Risk 34.2% LOW, 2 pattern (fan-out + smurfing)
- `8000EBD30` → Risk ~0% LOW, 0 pattern

### Tab 2: 🔍 Strumenti
3 API esposte con form interattivi:
- **Analisi Transazione** → `POST /analyze/transaction`
- **Raccomandazioni** → `POST /recommend/actions` (BLOCK, ALERT, REVIEW, MONITOR)
- **Fraud Detection** → `POST /detect/fraud`

### Tab 3: 🛡️ Governance
Monitoring IBM watsonx.governance in tempo reale:
- Metriche aggregate (totale analisi, score medio, status cloud)
- Log sessione corrente
- Record permanenti da IBM Watson OpenScale cloud

### Tab 4: 📋 Audit Trail
Risponde alle domande delle autorità: *"Quando? Quale sistema? Con quali dati?"*
- Ricerca per Account ID
- Tabella con timestamp, score, level, modello AI, ID univoco analisi
- Export CSV per reportistica esterna

---

## 🔌 Endpoint API Completi

| # | Endpoint | Metodo | Esposto in GUI |
|---|---|---|---|
| 1 | `/api/v1/assess/risk` | POST | ✅ Tab Analisi |
| 2 | `/api/v1/explain` | POST | ✅ Tab Analisi (auto) |
| 3 | `/api/v1/analyze/transaction` | POST | ✅ Tab Strumenti |
| 4 | `/api/v1/recommend/actions` | POST | ✅ Tab Strumenti |
| 5 | `/api/v1/detect/fraud` | POST | ✅ Tab Strumenti |
| 6 | `/api/v1/governance/metrics` | GET | ✅ Tab Governance |
| 7 | `/api/v1/governance/logs` | GET | ✅ Tab Governance |
| 8 | `/api/v1/governance/cloud-records` | GET | ✅ Tab Governance |
| 9 | `/api/v1/governance/audit` | GET | ✅ Tab Audit Trail |
| 10 | `/api/v1/governance/audit/export` | GET | ✅ Tab Audit Trail (CSV) |

---

## 🎯 Workflow Demo Consigliato (10 minuti)

### 1. Apertura (1 min)
- Apri `https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/dashboard`
- Mostra il badge "Powered by IBM watsonx.ai" e il design IBM-style

### 2. Analisi Rischio — Conto Sospetto (3 min)
- Tab "Analisi Rischio"
- Account ID: `100428660`, Periodo: 30 giorni
- Click "Analizza Rischio"
- Mostra: loading a 2 step → metriche → **pattern fan-out + smurfing** → spiegazione Granite
- *"Il sistema ha rilevato 122 destinatari diversi e 9 transazioni strutturate sotto $10k"*

### 3. Strumenti — Raccomandazioni (2 min)
- Tab "Strumenti" → sezione Raccomandazioni
- Stesso account `100428660`
- Mostra: azioni ALERT/REVIEW con motivazione per compliance

### 4. Governance (2 min)
- Tab "Governance" → click "Aggiorna"
- Mostra: metriche aggregate, log sessione, connessione IBM OpenScale cloud attiva

### 5. Audit Trail (2 min)
- Tab "Audit Trail" → click "Cerca" (senza filtro = tutti)
- Mostra tabella con timestamp, modello AI usato (`ibm/granite-4-h-small`), ID univoco
- Click "Export CSV" → download file per autorità
- *"Se un ispettore chiede 'quando avete fatto questa analisi?', rispondo qui"*

---

## 📊 Dati Tecnici

- **Dataset:** IBM HI-Small_Trans_sample.csv (~15k transazioni, 1.4MB)
- **Risk Score:** formula su 5 fattori ponderati
- **AML Patterns:** fan-out, fan-in, circular, smurfing
- **AI Model:** `ibm/granite-4-h-small` via IBM watsonx.ai API (eu-de)
- **Governance:** IBM Watson OpenScale, payload logging su cloud IBM
- **Deploy:** IBM Code Engine buildpacks da GitHub (auto-build)

---

## ✅ Checklist Pre-Demo

- [x] Dashboard 4-tab live su IBM Code Engine
- [x] IBM Granite funzionante (verificato 24/06/2026)
- [x] IBM Watson OpenScale governance attivo (cloud enabled: true)
- [x] Audit Trail con export CSV
- [x] Tutti e 10 gli endpoint esposti nella GUI
- [x] Account di test verificati (`100428660` → fan-out + smurfing)
- [ ] Verifica che il pod sia attivo prima della demo (health check)

### Health Check Pre-Demo
```bash
curl https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health
```

---

## 🐛 Troubleshooting

| Problema | Causa | Soluzione |
|---|---|---|
| Dashboard non risponde | Pod Code Engine in cold start | Attendere 10-30 sec dopo il primo accesso |
| AI Explanation "fallback" | Rate limit watsonx.ai free tier | Riprovare dopo 30 sec |
| Audit Trail vuoto | Pod riavviato (log in-memory persi) | Esegui almeno 1 analisi, poi cerca |
| Export CSV vuoto | Nessun record di tipo risk_assessment | Esegui analisi dalla tab Analisi Rischio |

---

## 📅 Scadenze Contest

- **1 Luglio 2026** — Demo Day
- **8 Luglio 2026** — Finale

---

**Preparato da:** Claude Sonnet 4.6 + IBM Bob  
**Data aggiornamento:** 24 Giugno 2026  
**Versione:** 3.0
