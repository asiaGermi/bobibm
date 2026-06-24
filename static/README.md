# 🏦 Financial Risk Dashboard

Dashboard interattiva per l'analisi del rischio finanziario AML (Anti-Money Laundering), powered by IBM watsonx.ai e IBM watsonx.governance.

**URL Produzione:** `https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/dashboard`

---

## 📋 Struttura: 4 Tab

### 📊 Tab 1 — Analisi Rischio
Flusso automatico in 2 step per analizzare un conto bancario.

**Input:**
- Account ID (es. `100428660`)
- Periodo analisi in giorni (default: 30)

**Step 1 — `/api/v1/assess/risk`:**
Calcola il risk score con formula ponderata su 5 fattori dal CSV:
1. Frequenza transazioni (anomalie volume)
2. Importi anomali (deviazioni statistiche)
3. Valute ad alto rischio (non-USD)
4. Storia laundering (flag `Is Laundering = 1`)
5. Complessità rete (numero controparti)

**Step 2 — `/api/v1/explain` (automatico):**
Invia il risultato a IBM watsonx.ai (`ibm/granite-4-h-small`) → genera spiegazione in linguaggio naturale per compliance officer. Fallback rule-based se Granite non disponibile.

**Output visualizzato:**
- Risk Score (%) + Risk Level (LOW/MEDIUM/HIGH/CRITICAL) — derivato automaticamente dallo score
- Pattern AML rilevati (fan-out, smurfing, fan-in, circular) con confidenza
- AI Explanation (IBM Granite) con testo generato
- Grafici: Risk Score Distribution (donut) + Risk Level Breakdown (bar)
- Statistiche transazioni: totali, volume, media, massimo

---

### 🔍 Tab 2 — Strumenti
Tre API esposte singolarmente per analisi avanzate.

**Analisi Singola Transazione — `POST /api/v1/analyze/transaction`**
- Input: Account ID + Timestamp + Periodo
- Output: dettaglio transazione, anomalie, risk info

**Raccomandazioni Azioni — `POST /api/v1/recommend/actions`**
- Input: Account ID + Periodo
- Output: lista azioni prioritizzate (BLOCK, ALERT, REVIEW, MONITOR) con motivazione

**Fraud Detection — `POST /api/v1/detect/fraud`**
- Input: Account ID + Timestamp + Periodo
- Output: fraud risk level, anomaly score, segnali di frode rilevati

---

### 🛡️ Tab 3 — Governance
Monitoraggio IBM watsonx.governance in tempo reale.

**Metriche aggregate:**
- Totale analisi rischio eseguite
- Totale spiegazioni AI generate
- Risk score medio su tutte le analisi
- Status connessione IBM Watson OpenScale cloud

**Log locali recenti:**
Ultimi record dalla sessione corrente (in-memory).

**Record IBM OpenScale Cloud:**
Record permanenti salvati su IBM Watson OpenScale — persistenti anche dopo restart del pod.

> Ogni analisi eseguita viene automaticamente loggata su IBM Watson OpenScale cloud (subscription ID: `019ef96a-44d2-7ebf-85e4-c9c53923009e`).

---

### 📋 Tab 4 — Audit Trail
Registro di tutte le analisi per compliance e tracciabilità.

**Ricerca:** filtra per Account ID (opzionale — lascia vuoto per vedere tutto)

**Tabella risultati:**
| Campo | Descrizione |
|---|---|
| Data / Ora | Timestamp preciso dell'analisi |
| Account ID | Conto analizzato |
| Risk Score | Score calcolato (%) |
| Risk Level | Livello derivato automaticamente |
| Pattern AML | Numero schemi rilevati |
| Transazioni | Transazioni analizzate |
| Periodo | Giorni di lookback |
| Modello AI | Granite o fallback |
| ID Analisi | UUID univoco per tracciabilità |

**Export CSV:** scarica il registro come file CSV per reportistica esterna.

> Risponde alla domanda delle autorità: *"Quando? Quale sistema? Con quali dati?"*

---

## 🔧 API Endpoint Completi

| Endpoint | Metodo | Tab | Descrizione |
|---|---|---|---|
| `/api/v1/assess/risk` | POST | Analisi Rischio | Risk score + pattern AML dal CSV |
| `/api/v1/explain` | POST | Analisi Rischio | Spiegazione AI via IBM Granite |
| `/api/v1/analyze/transaction` | POST | Strumenti | Analisi singola transazione |
| `/api/v1/recommend/actions` | POST | Strumenti | Azioni raccomandate |
| `/api/v1/detect/fraud` | POST | Strumenti | Fraud detection |
| `/api/v1/governance/metrics` | GET | Governance | Metriche aggregate |
| `/api/v1/governance/logs` | GET | Governance | Log sessione corrente |
| `/api/v1/governance/cloud-records` | GET | Governance | Record IBM OpenScale |
| `/api/v1/governance/audit` | GET | Audit Trail | Query audit (filtro account) |
| `/api/v1/governance/audit/export` | GET | Audit Trail | Export CSV |

Swagger UI: `/api/v1/docs`

---

## 🎨 Design

- **Font:** IBM Plex Sans
- **Colori:** gradient IBM (`#667eea` → `#764ba2`), IBM Blue (`#0f62fe`)
- **Risk colors:** LOW `#28a745` · MEDIUM `#ffc107` · HIGH `#dc3545` · CRITICAL `#6f42c1`
- **Responsive:** Desktop / Tablet / Mobile

---

## 📊 Fonte Dati

- **CSV runtime:** `data/raw/HI-Small_Trans_sample.csv` (~1.4MB, ~15k transazioni)
- **Dataset originale:** IBM HI-Small_Trans.csv (453MB, escluso dall'immagine Docker)
- **Schema:** `Timestamp, From Bank, Account, To Bank, Account, Amount Received, Receiving Currency, Amount Paid, Payment Currency, Payment Format, Is Laundering`

---

## 🚀 Account di Test

| Account ID | Caratteristiche |
|---|---|
| `100428660` | Fan-out (122 account) + Smurfing (9 tx sotto $10k) → Risk 34% LOW |
| `8000EBD30` | Transazioni normali → Risk ~0% LOW |

---

## 🔐 Tecnologie IBM

- **IBM Code Engine** — deploy containerizzato (buildpacks da GitHub)
- **IBM Container Registry** — immagine Docker privata
- **IBM watsonx.ai** — IBM Granite `ibm/granite-4-h-small` per spiegazioni
- **IBM Watson OpenScale** — governance, payload logging, audit trail cloud

---

**Repository:** https://github.com/asiaGermi/bobibm  
**API Docs:** https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/docs
