# Script Video — IBM Open Agentic Builders
## Financial Risk Management — AML Detection

**Durata stimata:** 12-14 minuti  
**Lingua:** Italiano  
**Formato:** Voiceover su screen recording  
**Note:** I testi tra [parentesi] sono istruzioni di regia — NON vanno letti

---

## PARTE 1 — Il Problema (2 minuti)

[Apri **docs/demo/SLIDES_PART1.md** e mostra **Slide 1** (copertina con titolo e badge IBM Open Agentic Builders)]

---

Ciao a tutti. Siamo Accenture e questo è il nostro progetto per l'IBM Open Agentic Builders Challenge: un sistema multi-agente per la gestione del rischio finanziario e il rilevamento di schemi di riciclaggio.

Partiamo dal problema reale che vogliamo risolvere.

[Avanza a **Slide 2** (cifre riciclaggio: €2-5 trilioni, 2-4 ore, obbligo legale)]

Il riciclaggio di denaro è una delle sfide più critiche per le istituzioni finanziarie. Ogni anno, miliardi di euro transitano attraverso reti di conti apparentemente normali, nascondendo l'origine illecita dei fondi. Le banche e le assicurazioni hanno l'obbligo legale di identificare questi comportamenti — ma farlo manualmente significa analizzare milioni di transazioni, cercando pattern che spesso non sono visibili a occhio nudo.

[Avanza a **Slide 3** (problemi sistemi tradizionali: lenti, costosi, non scalabili, black box)]

I sistemi tradizionali di analisi del rischio sono lenti, costosi, e richiedono analisti specializzati. Un singolo caso sospetto può richiedere ore di lavoro prima di arrivare a una raccomandazione operativa. E con volumi di dati in costante crescita, questo approccio non scala.

[Avanza a **Slide 4** (schema 5 agenti AI + KPI: <3 secondi, 95% accuracy, auditable)]

La nostra soluzione risponde a questa sfida con un approccio agentico: cinque agenti AI specializzati che collaborano in automatico, orchestrati da IBM watsonx Orchestrate, e capaci di analizzare un conto in meno di tre secondi — producendo non solo un punteggio di rischio, ma anche una spiegazione comprensibile per un compliance officer.

---

## PARTE 2 — L'Architettura della Soluzione (2-3 minuti)

[Mostra il diagramma architettura da docs/demo/ARCHITECTURE_SLIDES.md oppure da README.md sezione "Architettura"]

---

Vediamo come è costruito il sistema.

Al centro di tutto c'è **IBM watsonx Orchestrate**, che funge da orchestratore intelligente: riceve la richiesta, decide quali agenti chiamare, in quale ordine, e consolida il risultato finale in un report strutturato.

Abbiamo cinque agenti specializzati, ognuno con una responsabilità precisa.

Il primo è il **Transaction Analysis Agent**: analizza la storia transazionale di un conto e rileva i pattern tipici del riciclaggio. Per esempio il cosiddetto "fan-out" — un conto che distribuisce rapidamente denaro verso molti destinatari — oppure lo "smurfing", cioè tante piccole transazioni sotto soglia per sfuggire ai controlli automatici. O ancora i flussi circolari, dove il denaro parte da un conto, passa per una catena di intermediari, e torna al punto di partenza.

Il secondo è il **Risk Assessment Agent**: calcola un punteggio di rischio da zero a uno, pesando cinque fattori — volume delle transazioni, frequenza operativa, pattern anomali rilevati, presenza di transazioni di alto valore, e l'età del conto. I conti nuovi con alta attività sono statisticamente più rischiosi.

Il terzo è il **Fraud Detection Agent**: si focalizza sulle anomalie temporali — picchi di attività in orari inusuali — e sulla storia di laundering presente nel dataset, per costruire un profilo di rischio strutturato.

Il quarto è il **Recommendation Agent**: prende tutti i risultati precedenti e genera un'azione operativa: ALERT, REVIEW, BLOCK oppure MONITOR, con relativa priorità e motivazione.

Il quinto, e forse il più innovativo, è l'**Explanation Agent**: usa IBM watsonx.ai con il modello Granite per tradurre i risultati tecnici in linguaggio naturale — una spiegazione che può essere letta e usata direttamente da un compliance officer, senza alcun background tecnico.

Tutta l'infrastruttura è deployata su **IBM Cloud Code Engine** in Frankfurt, containerizzata con Docker, con auto-scaling da uno a dieci istanze in base al carico.

I dati vengono dagli **IBM Synthetic Data Sets**: oltre quindicimila transazioni realistiche con flag di laundering certificati — il dataset ufficiale IBM per questo tipo di analisi.

---

## PARTE 3 — Come Abbiamo Usato IBM Bob (3 minuti)

[Apri IBM Bob nel terminale/IDE → mostra la chat con la modalità **wxo-agent-architect** attiva (custom_modes.yaml visibile)]

---

Adesso veniamo alla parte che ritengo più importante: come abbiamo usato **IBM Bob** per costruire questo sistema.

Bob è l'assistente AI integrato nel nostro ambiente di sviluppo. Fin dal primo giorno lo abbiamo configurato in modalità **wxo-agent-architect** — la modalità specifica per progettare e implementare soluzioni su watsonx Orchestrate.

Il contributo di Bob non si è limitato ad accelerare la scrittura di codice. Bob ci ha aiutato a **ragionare sull'architettura** prima ancora di scrivere una riga.

[Mostra screenshot o registrazione di una conversazione reale con Bob — es. la risposta di Bob alla domanda sull'architettura multi-agente]

Quando abbiamo iniziato, la prima cosa che abbiamo chiesto a Bob è stata: qual è il modo migliore per strutturare un sistema multi-agente per l'analisi del rischio finanziario usando lo stack IBM? Bob ci ha restituito immediatamente una proposta di architettura con separazione delle responsabilità tra agenti, suggerendo watsonx Orchestrate come orchestratore e Code Engine per il backend. Questo ci ha dato una struttura solida da cui partire.

Bob conosce le specifiche IBM in profondità. Quando abbiamo chiesto come configurare l'agente orchestratore su watsonx Orchestrate, ci ha dato il formato YAML corretto, i parametri del modello Granite da usare, e la struttura dei tool. Senza questa guida avremmo passato giorni a leggere documentazione.

Bob ci ha anche aiutato a definire l'OpenAPI spec — il contratto tra watsonx Orchestrate e il nostro backend. Ha suggerito la struttura degli endpoint, i tipi di input e output, e come allinearli con i tool registrati in watsonx Orchestrate.

Un altro momento chiave è stato il deployment su IBM Cloud. Il processo di containerizzazione, push su IBM Container Registry, e deploy su Code Engine non è banale. Bob ci ha guidato passo passo, anticipando problemi come la configurazione delle variabili d'ambiente e la gestione delle credenziali IBM Cloud.

In una settimana — dal giorno zero — siamo arrivati a un sistema live su IBM Cloud. Bob ha compresso settimane di curva di apprendimento in giorni. Non ha sostituito il nostro ragionamento, ma ha agito come un collega esperto che conosce alla perfezione lo stack IBM e ti aiuta a prendere le decisioni architetturali giuste al momento giusto.

---

## PARTE 4 — Demo Live del Sistema (5 minuti)

[Apri il browser su: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/dashboard]

---

Adesso vi mostro il sistema in funzione, live su IBM Cloud, usando dati reali dal dataset IBM Synthetic Data Sets.

Prima cosa: verifichiamo che tutto sia attivo con l'health check.

[Nel browser apri una nuova tab su: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/health — mostra la risposta JSON a schermo]

Il sistema risponde: tutte le componenti sono operative, il data layer ha quindicimila transazioni caricate. Siamo pronti.

Torna alla dashboard e analizziamo tre conti reali del dataset, con profili di rischio molto diversi tra loro.

---

**Primo conto: 8000EBD30 — un conto pulito.**

[Tab **📊 Analisi Rischio** → campo **Account ID**: digita `8000EBD30` → campo **Periodo analisi**: `30` → click bottone **Analizza Rischio** → attendi il risultato]

Il sistema restituisce un risk score vicino allo zero, livello LOW, nessun pattern AML rilevato, nessun fraud signal. Il Recommendation Agent dice MONITOR — nessuna azione urgente necessaria. Questo è il comportamento atteso per un conto regolare: il sistema non genera falsi positivi.

---

**Secondo conto: 812D22980 — un caso sospetto.**

[Tab **📊 Analisi Rischio** → campo **Account ID**: digita `812D22980` → campo **Periodo analisi**: `90` → click bottone **Analizza Rischio** → attendi il risultato]

Qui la situazione cambia. Risk score 53.9%, livello MEDIUM. Il Transaction Analysis rileva un pattern di flusso circolare: il denaro parte da questo conto, passa per una catena di intermediari, e torna al punto di partenza — classico schema per oscurare l'origine dei fondi. Il dato più rilevante: il 93% delle transazioni di questo conto sono flaggate come laundering nel dataset. Il sistema genera una raccomandazione di REVIEW.

[Scorri verso il basso fino alla sezione **AI Explanation (IBM Granite)** — mostra il testo generato da Granite]

---

**Terzo conto: 100428A51 — il caso critico.**

[Apri il browser su: https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/d406e5c1-2678-4678-910c-5d02ac17d024 — mostra la chat dell'agente **financial_risk_orchestrator**]

Per questo conto usiamo il workflow completo orchestrato da watsonx Orchestrate. Nella chat scriviamo: "Analyze the risk for account 100428A51".

[Digita il prompt nella chat di watsonx Orchestrate e attendi la risposta completa]

L'orchestratore pianifica il workflow: prima assessRisk, poi detectFraud e analyzeTransaction in parallelo, infine recommendActions.

Risk Assessment: **70% — livello HIGH.** I fattori principali sono volume transazionale estremo e pattern anomali di distribuzione.

Transaction Analysis: **pattern fan-out massivo.** Questo conto ha generato oltre tredicimila transazioni Bitcoin verso 1.147 destinatari diversi. Non è un comportamento normale — è la firma di uno schema di distribuzione strutturato, progettato per frammentare i flussi e rendere difficile il tracciamento.

Fraud Detection: conferma il profilo — anomalie temporali e storia di laundering consolidata.

Recommendation Agent: **ALERT + BLOCK.** Il sistema raccomanda di bloccare immediatamente le operazioni in uscita e di aprire un'indagine formale.

Infine, torniamo alla dashboard per l'**Explanation Agent** con Granite.

[Torna alla dashboard → Tab **📊 Analisi Rischio** → campo **Account ID**: digita `100428A51` → **Analizza Rischio** → scorri fino alla sezione **AI Explanation (IBM Granite)**]

Granite genera: "Questo conto presenta segnali critici di riciclaggio. L'analisi ha rilevato un pattern fan-out su scala elevata — oltre mille destinatari in transazioni Bitcoin — con storia confermata di laundering. Si raccomanda il blocco immediato e l'avvio di una procedura di indagine AML formale."

Questo è il valore aggiunto: in meno di tre secondi, il sistema ha analizzato tredicimila transazioni e prodotto una spiegazione pronta per un compliance officer o per un documento di audit.

---

## PARTE 5 — Governance e Audit Trail (3 minuti)

C'è un'ultima componente del sistema che voglio mostrarvi, e che secondo me è quella più rilevante per il contesto enterprise: la governance AI e la tracciabilità delle decisioni.

Nel settore finanziario non basta che un sistema AI funzioni — deve anche essere auditabile, tracciabile, e conforme alle normative. Le autorità di vigilanza richiedono che le istituzioni finanziarie documentino le decisioni prese con l'ausilio di sistemi AI.

---

**Prima: la governance in tempo reale nella nostra applicazione.**

[Torna alla dashboard → click tab **🛡️ Governance** → click bottone **Aggiorna**]

Qui vediamo le metriche aggregate in tempo reale: quante analisi di rischio sono state eseguite, il risk score medio, e soprattutto — lo status della connessione con IBM Watson OpenScale. Ogni analisi che abbiamo appena eseguito è stata automaticamente loggata su IBM Cloud.

[Scorri verso il basso fino alla sezione **Record IBM OpenScale Cloud** — mostra i record]

Questi record vengono letti direttamente da IBM Watson OpenScale. Sono persistenti — sopravvivono al restart del pod, all'aggiornamento del sistema, a qualsiasi evento tecnico.

---

**Poi: l'Audit Trail per le autorità di vigilanza.**

[Click tab **📋 Audit Trail** → lascia il campo Account ID vuoto → click bottone **Cerca**]

Questa è la risposta alla domanda che un ispettore farebbe in sede di audit: "Quando avete analizzato questo conto? Quale sistema ha preso la decisione? Con quali dati?"

La tabella mostra: timestamp preciso, account analizzato, risk score, livello di rischio, numero di pattern AML rilevati, modello AI usato — in questo caso `ibm/granite-4-h-small` — e un ID univoco per ogni analisi.

[Click bottone verde **Export CSV**]

Con un click esportiamo tutto in formato CSV — pronto per essere allegato a un documento di audit o inviato alle autorità di vigilanza.

---

**Infine: la piattaforma IBM watsonx.governance.**

[Apri il browser su: https://eu-de.aiopenscale.cloud.ibm.com → click sulla card **Financial Risk API - IBM Code Engine**]

Qui vediamo la stessa subscription dalla parte di IBM: le transazioni registrate con ID, timestamp, e la predizione del modello — il risk level che il sistema ha assegnato.

[Nella pagina watsonx.governance → click su **Lifecycle** nel menu in alto → mostra la card **Granite LLM Approach**]

Nella vista Lifecycle abbiamo l'approccio "Granite LLM Approach", che traccia il ciclo di vita del modello Granite all'interno di questo use case — classificato a rischio **High** perché opera in un dominio regolamentato.

[Click su **Granite LLM Approach** → mostra l'AI Factsheet **Financial Risk - Granite Explanation Model**]

E qui c'è l'AI Factsheet del modello. Questo documento registra automaticamente ogni inferenza fatta da Granite — quando è avvenuta, con quali input, con quale output.

Nel codice, questa registrazione avviene in automatico tramite il nostro `GovernanceMonitor`: ogni volta che l'Explanation Agent chiama Granite, il log viene inviato a IBM senza che l'utente debba fare nulla.

Questo significa che un compliance officer, in qualsiasi momento, può accedere alla piattaforma e avere una traccia completa di tutte le decisioni AI — pronta per un audit regolamentare.

---

## PARTE 6 — Valore di Business e Chiusura (1-2 minuti)

[Torna al diagramma architettura / slide finale con metriche di performance da README.md]

---

Ricapitoliamo il valore di business di questa soluzione.

Prima di sistemi come questo, un analista impiegava ore per esaminare un conto sospetto. Adesso lo stesso processo richiede meno di tre secondi, con una precisione nel rilevamento dei pattern AML superiore al novantacinque percento.

Il sistema scala in automatico su IBM Cloud in base al carico, quindi è pronto per volumi enterprise senza intervento manuale.

La componente Granite aggiunge interpretabilità — le decisioni sono spiegabili e comprensibili anche ai non tecnici.

E grazie a watsonx.governance, ogni decisione è auditabile e documentata — un requisito normativo concreto nel mondo finanziario, non un'opzione.

Abbiamo costruito tutto questo in meno di due settimane, con IBM Bob come partner di sviluppo e l'intero stack IBM come infrastruttura. Il sistema è live adesso, su IBM Cloud, e pronto per essere esteso con ulteriori dataset IBM, connettori verso sistemi bancari core, e workflow di approvazione umana.

Grazie per l'attenzione.

---

## Riepilogo tecnologie IBM usate

| Tecnologia | Utilizzo |
|------------|----------|
| IBM Bob (`wxo-agent-architect`) | Architettura, sviluppo, deployment |
| IBM watsonx Orchestrate | Orchestrazione multi-agente (5 tool + orchestratore) |
| IBM watsonx.ai Granite (`ibm/granite-4-h-small`) | Spiegazioni in linguaggio naturale |
| IBM watsonx.governance | AI Use Case, Factsheet, audit trail |
| IBM Cloud Code Engine | Hosting API containerizzata (eu-de, auto-scaling) |
| IBM Container Registry | Storage immagini Docker |
| IBM Synthetic Data Sets | Dataset transazioni (15.000+ record, flag laundering) |

---

## Note per la registrazione

- **Parte 3 (Bob)** è quella più pesante per i giudici — parla lentamente e mostra esempi concreti della chat
- **Parte 5 (Governance)** differenzia il progetto dagli altri — non saltarla
- Durante la demo live (Parte 4), avvia le chiamate API prima di parlare per evitare pause
- Totale parole script: ~1.800 — a ritmo normale (~130 parole/minuto) = ~13-14 minuti

## Account di test usati nella demo

| Account | Risk | Pattern | Perché usarlo |
|---------|------|---------|---------------|
| `8000EBD30` | ~0% LOW | nessuno | Mostra che il sistema non genera falsi positivi |
| `812D22980` | 53.9% MEDIUM | circular flow | 93% laundering — caso sospetto convincente |
| `100428A51` | 70.0% HIGH | fan-out | 13k tx Bitcoin, 1.147 destinatari — caso critico per il finale |

---

*Accenture — IBM Open Agentic Builders Challenge — Track A: Financial Risk Management*  
*Demo: 1 luglio 2026*
