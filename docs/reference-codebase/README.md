# 🏦 Automated AML Compliance Assistant (Multi-Agent Architecture)

Questo progetto implementa un **Assistente Investigativo e di Compliance per l'Anti-Money Laundering (AML)** basato su un'architettura multi-agente deterministica gestita tramite **LangGraph** e **LangChain**.

Il sistema opera al **100% in locale** per garantire la massima riservatezza dei dati bancari, sfruttando **Mistral** tramite **Ollama** come motore di ragionamento e sintesi.

## 📌 Panoramica del Sistema

Il software supera i limiti dei tradizionali sistemi RAG statici delegando l'analisi a 4 agenti specialistici coordinati da un Orchestratore centrale. Il sistema interroga in tempo reale le fonti istituzionali e confronta i dati con le procedure interne memorizzate in un Vector DB locale.

              ┌───────────────────┐
              │    Analista       │
              └─────────┬─────────┘
                        │ (Quesito)
                        ▼
              ┌───────────────────┐◄────────────────┐
              │   ORCHESTRATORE   │                 │
              └─────────┬─────────┘                 │
                        │                           │
     ┌──────────────────┼──────────────────┐        │ (Ritorno dati)
     ▼                  ▼                  ▼        │

┌─────────────────┐┌─────────────────┐┌─────────────────┐│
│ Agente Locale ││ Agente EU ││ Agente IT ││
│ (Vector DB) ││ (BCE + EBA) ││ (Bankit + UIF) ││
└─────────────────┘└─────────────────┘└─────────────────┘│
│ │ │ │
└──────────────────┼──────────────────┘────────┘
▼
[ Agente GAFI ]
│
▼
┌───────────────────┐
│ Report Finale │
└───────────────────┘

## 🕵️‍♂️ La Squadra degli Agenti

1. **`Orchestrator` (Il Cervello):** Analizza la richiesta dell'analista, pianifica la sequenza di attivazione degli specialisti, raccoglie i sotto-report e redige la relazione investigativa finale divisa per sezioni normative.
2. **`Agente_Locale` (Internal Memory):** Esegue ricerche semantiche tramite un Vector DB locale (FAISS) per estrarre le policy interne della banca, le checklist KYC e le procedure di escalation approvate.
3. **`Agente_EU` (European Context):** Esegue il crawling mirato in tempo reale sui domini della Banca Centrale Europea (`ecb.europa.eu`) e dell'EBA (`eba.europa.eu`) per verificare linee guida di vigilanza macroprudenziale e risk factors.
4. **`Agente_IT` (National Enforcement):** Scansiona i portali di Banca d'Italia (`bancaditalia.it`) e dell'UIF (`uif.bancaditalia.it`) alla ricerca degli schemi di comportamento anomalo e degli indicatori di anomalia ufficiali.
5. **`Agente_GAFI` (Geopolitical Risk):** Interroga il dominio del Financial Action Task Force (`fatf-gafi.org`) per identificare lo stato di giurisdizioni ad alto rischio (Blacklist / Grey-list).

## 🛠️ Requisiti Tecnici e Stack

- **Sistema Operativo:** Windows (consigliato l'uso di WSL2/Ubuntu per la produzione) o Linux.
- **LLM Core:** Ollama con modello `mistral` (7B parametri) in esecuzione locale.
- **Embedding Model:** `intfloat/multilingual-e5-large` (HuggingFace) per la vettorizzazione in lingua italiana e inglese.
- **Orchestrazione & Grafo:** `langgraph`, `langchain-core`, `langchain-community`.
- **Database Vettoriale:** `FAISS` (In-memory / File-based per sviluppo locale).
- **Network & Scraping:** `requests`, `beautifulsoup4`, `duckduckgo-search`.

## Struttura del repository

aml-compliance-agent/
│
├── .gitignore # Ignora venv, indici locali e file di configurazione
├── README.md # La documentazione che abbiamo strutturato
├── requirements.txt # Elenco delle dipendenze Python (pip freeze)
├── run.py # L'entry-point principale per l'esecuzione del sistema
│
├── config/ # Configurazioni globali e costanti di rete
│ ├── **init**.py
│ └── settings.py # URL dei domini, modelli di embedding, porte Ollama
│
├── src/ # Il cuore logico dell'applicazione
│ ├── **init**.py
│ ├── state.py # Definizione dello stato del grafo (AgentState)
│ ├── graph.py # Definizione del workflow LangGraph e dei link condizionali
│ │
│ ├── agents/ # Logica di pensiero e prompt dei singoli agenti
│ │ ├── **init**.py
│ │ ├── orchestrator.py # Logica di routing e sintesi finale
│ │ ├── agent_local.py # Interfaccia con il Vector DB
│ │ ├── agent_eu.py # Prompt specifico per BCE/EBA
│ │ ├── agent_it.py # Prompt specifico per Bankit/UIF
│ │ └── agent_gafi.py # Prompt specifico per FATF
│ │
│ └── tools/ # I motori tecnici (Crawler, Scraper e DB)
│ ├── **init**.py
│ ├── vector_db.py # Caricamento e interrogazione di FAISS/Qdrant
│ └── web_crawler.py # Gestione di BeautifulSoup, DuckDuckGo e Crawl-delay
│
└── scripts/ # Script di utility e manutenzione una tantum
├── **init**.py
└── ingestion_internal_policy.py # Lo script per inizializzare il DB locale

## 🚀 Installazione e Configurazione

### 1. Prerequisiti: Ollama e Mistral

Assicurati che Ollama sia installato sul tuo PC ed esegui il server:

```powershell
# Avvia il demone server
ollama serve

# Scarica ed esegui il modello Mistral (in un altro terminale)
ollama run mistral


```
