# TODO — IBM Open Agentic Builders · Track A: Financial Risk Management

**Demo**: 1 luglio 2026 · **Finale**: 8 luglio 2026 · **Oggi**: 22 giugno 2026 · **Giorni rimasti**: 9  
**Aggiornato**: 22 giugno 2026 (sera)

---

## Legenda
- ✅ Fatto
- 🔄 In corso
- ❌ Da fare (bloccante per demo)
- ⏳ Da fare (non bloccante per demo)

---

## FASE 1 · Analisi e Design

- ✅ Review requisiti mandate
- ✅ Scelta stack (FastAPI + LangGraph + watsonx Orchestrate + IBM Cloud Code Engine)
- ✅ Definizione responsabilità agenti (Transaction Analysis, Risk Assessment, Recommendation, Fraud Detection)
- ✅ Gap analysis rispetto al mandate ([docs/gap-analysis/gap-analysis.md](docs/gap-analysis/gap-analysis.md))
- ✅ Strategy document con roadmap ([docs/strategy/strategy.md](docs/strategy/strategy.md))
- ✅ Documentazione spec-driven development ([docs/spec-driven-development.md](docs/spec-driven-development.md))
- ✅ Definizione contratti API (OpenAPI auto-generato da FastAPI + Pydantic models)

---

## FASE 2 · Setup Ambiente

- ✅ IBM Bob installato con custom mode `wxo-agent-architect`
- ✅ Repository git creato e struttura directory inizializzata
- ✅ `requirements.txt` con dipendenze core (fastapi, uvicorn, pandas, pydantic)
- ✅ `workspace_config.yaml` watsonx configurato
- ❌ File `.env` con variabili ambiente (IBM Cloud API key, watsonx credentials)
- ❌ Account IBM Cloud configurato con credenziali watsonx Orchestrate
- ⏳ IBM Cloud Code Engine — provisioning environment

---

## FASE 3 · Data Layer

- ✅ Dataset IBM Synthetic Data (HI-Small_Trans.csv) caricato in `data/raw/`
- ✅ `src/data/loader.py` — caricamento dataset con LRU cache, query per account/banca/transazione
- ✅ `src/data/analyzer.py` — risk scoring (0.0-1.0), AML pattern detection (fan-out, fan-in, circular, smurfing), anomaly detection
- ✅ `src/data/test_data_layer.py` — test suite 12 casi (loader + analyzer)
- ❌ Script ETL per gli altri IBM Synthetic Data Sets (Core Banking, Payment Cards)
- ❌ Validazione e pulizia dati (colonne nulle, tipi errati)
- ⏳ Integrazione dati processati in `data/processed/`

---

## FASE 4 · Agenti ✅ COMPLETATA

### Transaction Analysis Agent
- ✅ `src/agents/transaction_analysis_agent.py`
  - ✅ Metodo `run(input: dict) -> dict`
  - ✅ Usa `get_account_history()` e `detect_aml_patterns()` dal data layer
  - ✅ Restituisce pattern rilevati + statistiche transazionali

### Risk Assessment Agent
- ✅ `src/agents/risk_assessment_agent.py`
  - ✅ Metodo `run(input: dict) -> dict`
  - ✅ Usa `calculate_risk_score()` e `get_high_risk_accounts()`
  - ✅ Restituisce score 0.0-1.0 + breakdown fattori di rischio + modalità `high_risk_scan`

### Recommendation Agent
- ✅ `src/agents/recommendation_agent.py`
  - ✅ Metodo `run(input: dict) -> dict`
  - ✅ Genera azioni: ALERT / REVIEW / BLOCK / MONITOR
  - ✅ Input: risk_score + patterns rilevati

### Fraud Detection Agent
- ✅ `src/agents/fraud_detection_agent.py`
  - ✅ Metodo `run(input: dict) -> dict`
  - ✅ Usa `detect_temporal_anomalies()` + laundering history
  - ✅ Restituisce fraud signals strutturati + modalità `account_profile`

### Explanation Agent ✅ NUOVO
- ✅ `src/agents/explanation_agent.py`
  - ✅ Metodo `run(input: dict) -> dict`
  - ✅ Usa IBM watsonx.ai Granite (`ibm/granite-4-h-small`) via ibm-watsonx-ai SDK
  - ✅ Chat API (`/ml/v1/text/chat`) — no deprecated endpoints
  - ✅ Fallback rule-based se LLM non disponibile
  - ✅ Testato live su Cloud Engine — `fallback_used: False`

### Common
- ✅ `src/agents/__init__.py` — export tutti e 5 gli agenti

---

## FASE 5 · API REST ✅ COMPLETATA

- ✅ `src/api/models.py` — modelli Pydantic request/response (+ `ExplainRequest`, `ExplainResponse`)
- ✅ `src/api/main.py` — app FastAPI con CORS e OpenAPI
  - ✅ `POST /api/v1/analyze/transaction`
  - ✅ `POST /api/v1/assess/risk`
  - ✅ `POST /api/v1/recommend/actions`
  - ✅ `POST /api/v1/detect/fraud`
  - ✅ `POST /api/v1/explain` — **NUOVO** LLM Granite explanation
  - ✅ `GET  /api/v1/health`
- ✅ `src/api/orchestrator.py` — coordina le chiamate agli agenti con fallback graceful
- ✅ `src/api/__init__.py`
- ✅ `run_api.py` — entry point locale (`uvicorn src.api.main:app --reload`)
- ⏳ Rate limiting
- ⏳ JWT authentication (Step 2+)

---

## FASE 6 · Orchestrazione watsonx Orchestrate ✅ COMPLETATA

- ✅ `agents/transaction_analysis_agent.yaml` — skill wxO → `/api/v1/analyze/transaction`
- ✅ `agents/risk_assessment_agent.yaml` — skill wxO → `/api/v1/assess/risk`
- ✅ `agents/recommendation_agent.yaml` — skill wxO → `/api/v1/recommend/actions`
- ✅ `agents/fraud_detection_agent.yaml` — skill wxO → `/api/v1/detect/fraud`
- ✅ `agents/financial_risk_orchestrator.yaml` — orchestratore wxO sequenziale
- ✅ Deploy 4 tool + agente su istanza `wxo-675000bo4y` (eu-de) via ADK CLI
- ✅ Test workflow wxO end-to-end — Financial Risk Analysis Report generato correttamente

---

## FASE 7 · Containerizzazione ✅ COMPLETATA (file)

- ✅ `Dockerfile` — multi-stage build Python 3.11-slim, non-root user, healthcheck
- ✅ `docker-compose.yml` — volume ./data read-only, env vars, network dedicata
- ✅ `.env.example` — template completo (JWT e wxO commentati per Step 2)
- ✅ `DOCKER.md` — guida operativa con curl di test per tutti e 4 gli endpoint
- ❌ Build e test locale container (Docker bloccato da Accenture)
- ✅ IBM Cloud Container Registry namespace `financial-risk` creato su `de.icr.io`
- ✅ Build immagine su IBM Cloud Code Engine da GitHub (Succeeded)
- ✅ Deploy su Code Engine — revisione 00007 Ready, porta 8000, sample CSV 15k transazioni

---

## FASE 8 · Deploy IBM Cloud ✅ COMPLETATA

- ✅ Provisioning IBM Cloud Code Engine (progetto ce-675000bo4y, eu-de)
- ✅ Push immagine Docker su IBM Cloud Container Registry (`private.de.icr.io/financial-risk/financial-risk-management:latest`)
- ✅ Deploy applicazione su Code Engine (revisione 00016, porta 8000)
- ✅ Dataset sample CSV 15k transazioni nel container
- ✅ Endpoint pubblico HTTPS attivo: `https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud`
- ✅ Test health endpoint: `data_layer_status: connected`, 15.000 transazioni
- ✅ Test `/api/v1/assess/risk`: risk_score, AML patterns, statistiche transazionali
- ✅ **IBM watsonx.ai Granite integrato** — progetto `frm-granite` (us-south), modello `ibm/granite-4-h-small`
- ✅ Test `/api/v1/explain`: `model_used: ibm/granite-4-h-small`, `fallback_used: False`
- ✅ `scripts/deploy_unified.py` — script automatizzato (build → push → deploy CE → health check → registra skills wxO)
- ✅ `scripts/README.md` — guida uso script deploy
- ✅ `docs/deployment/QUICK-START.md` — guida rapida deployment (5 min)
- ✅ `docs/deployment/api-deployment-strategy.md` — strategia completa deploy via IBM Cloud API
- ⏳ Prune immagini ICR (storage >80%)

---

## FASE 9 · Testing

- ✅ Test data layer (`src/data/test_data_layer.py`)
- ❌ Test agenti (mock data layer)
- ❌ Test endpoint API (`pytest` + `httpx`)
- ❌ Test integrazione end-to-end (data → agenti → API)
- ⏳ Test su endpoint pubblico IBM Cloud

---

## FASE 10 · Demo (scadenza 1 luglio)

- ❌ Script demo che mostra il flusso completo: input transazione → analisi → risk score → raccomandazione
- ❌ Registrazione video demo (senza facce, con descrizione architettura MVP)
- ❌ Slide architettura (diagramma componenti: dataset → agenti → wxO → API → IBM Cloud)
- ❌ README aggiornato con istruzioni run locale e link endpoint pubblico

---

## Progresso per fase

| Fase | Stato | % |
|------|-------|---|
| 1 · Analisi e Design | ✅ Completo | 100% |
| 2 · Setup Ambiente | 🔄 Parziale | 50% |
| 3 · Data Layer | ✅ Quasi completo | 80% |
| 4 · Agenti (5 agenti incl. Granite) | ✅ Completo | 100% |
| 5 · API REST (6 endpoint) | ✅ Completo | 100% |
| 6 · Orchestrazione wxO | ✅ Completo — live su wxo-675000bo4y | 100% |
| 7 · Containerizzazione | ✅ Completo | 100% |
| 8 · Deploy IBM Cloud + Granite live | ✅ Completo — endpoint pubblico live | 100% |
| 9 · Testing | 🔄 Parziale | 15% |
| 10 · Demo | ❌ Non iniziato | 0% |

---

## Piano 10 giorni (21 giu → 1 lug)

| Giorni | Task | Stato |
|--------|------|-------|
| 21-23 giu | Bob cmd 1: API REST + modelli Pydantic | ✅ FATTO |
| 21-23 giu | Bob cmd 2: 4 agenti data-driven | ✅ FATTO |
| 21-23 giu | Bob cmd 3: orchestrazione locale | ✅ FATTO |
| 21-23 giu | Bob cmd 4: skill wxO | ✅ FATTO |
| 21-22 giu | Bob cmd 5: Dockerfile + docker-compose | ✅ FATTO |
| 22-24 giu | Deploy IBM Cloud Code Engine | ✅ FATTO |
| 22 giu (sera) | Granite ibm/granite-4-h-small live su CE | ✅ FATTO |
| 22 giu (sera) | Script deploy unificato + docs deployment | ✅ FATTO |
| 22 giu (sera) | Deploy skills + agente su wxO — end-to-end ok | ✅ FATTO |
| 23-24 giu | README + script demo curl | ❌ |
| 25-28 giu | Test end-to-end su endpoint pubblico | ❌ |
| 28-30 giu | Video demo + slide architettura | ❌ |
