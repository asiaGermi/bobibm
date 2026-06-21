# TODO — IBM Open Agentic Builders · Track A: Financial Risk Management

**Demo**: 1 luglio 2026 · **Finale**: 8 luglio 2026 · **Oggi**: 21 giugno 2026 · **Giorni rimasti**: 10  
**Aggiornato**: 21 giugno 2026

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

### Common
- ✅ `src/agents/__init__.py` — export tutti e 4 gli agenti

---

## FASE 5 · API REST ✅ COMPLETATA

- ✅ `src/api/models.py` — modelli Pydantic request/response (+ `FraudDetectionResponse`)
- ✅ `src/api/main.py` — app FastAPI con CORS e OpenAPI
  - ✅ `POST /api/v1/analyze/transaction`
  - ✅ `POST /api/v1/assess/risk`
  - ✅ `POST /api/v1/recommend/actions`
  - ✅ `POST /api/v1/detect/fraud`
  - ✅ `GET  /api/v1/health`
- ✅ `src/api/orchestrator.py` — coordina le chiamate agli agenti con fallback graceful
- ✅ `src/api/__init__.py`
- ✅ `run_api.py` — entry point locale (`uvicorn src.api.main:app --reload`)
- ⏳ Rate limiting
- ⏳ JWT authentication (Step 2+)

---

## FASE 6 · Orchestrazione watsonx Orchestrate ✅ COMPLETATA (definizioni)

- ✅ `agents/transaction_analysis_agent.yaml` — skill wxO → `/api/v1/analyze/transaction`
- ✅ `agents/risk_assessment_agent.yaml` — skill wxO → `/api/v1/assess/risk`
- ✅ `agents/recommendation_agent.yaml` — skill wxO → `/api/v1/recommend/actions`
- ✅ `agents/fraud_detection_agent.yaml` — skill wxO → `/api/v1/detect/fraud`
- ✅ `agents/financial_risk_orchestrator.yaml` — orchestratore wxO sequenziale
- ❌ Deploy skills su istanza watsonx Orchestrate
- ❌ Test workflow wxO end-to-end

---

## FASE 7 · Containerizzazione ✅ COMPLETATA (file)

- ✅ `Dockerfile` — multi-stage build Python 3.11-slim, non-root user, healthcheck
- ✅ `docker-compose.yml` — volume ./data read-only, env vars, network dedicata
- ✅ `.env.example` — template completo (JWT e wxO commentati per Step 2)
- ✅ `DOCKER.md` — guida operativa con curl di test per tutti e 4 gli endpoint
- ❌ Build e test locale container (`docker-compose up -d`)
- ⏳ Push immagine su IBM Cloud Container Registry

---

## FASE 8 · Deploy IBM Cloud

- ⏳ Provisioning IBM Cloud Code Engine (environment + project)
- ⏳ Push immagine Docker su IBM Cloud Container Registry
- ⏳ Deploy applicazione su Code Engine
- ⏳ Configurazione variabili ambiente su Code Engine
- ⏳ Esposizione endpoint pubblico HTTPS
- ⏳ Test endpoint pubblico con curl/Postman

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
| 4 · Agenti | ✅ Completo | 100% |
| 5 · API REST | ✅ Completo | 100% |
| 6 · Orchestrazione wxO | 🔄 Definizioni ok, deploy mancante | 60% |
| 7 · Containerizzazione | ✅ File pronti, build da testare | 80% |
| 8 · Deploy IBM Cloud | ❌ Non iniziato | 0% |
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
| 22-24 giu | Build + test container locale, poi deploy IBM Cloud Code Engine | ❌ PROSSIMO |
| 24-25 giu | Deploy skills su wxO + test workflow | ❌ |
| 25-28 giu | Test end-to-end su endpoint pubblico | ❌ |
| 28-30 giu | Video demo + slide architettura | ❌ |
