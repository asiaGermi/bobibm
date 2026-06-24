# 🏦 Financial Risk Dashboard

Dashboard interattiva per l'analisi del rischio finanziario e il rilevamento AML (Anti-Money Laundering).

## 📋 Panoramica

Questa dashboard fornisce un'interfaccia web moderna e intuitiva per:
- Analizzare il rischio delle transazioni
- Visualizzare metriche di rischio con grafici interattivi
- Ottenere spiegazioni AI generate da IBM Granite
- Monitorare pattern AML in tempo reale

## 🚀 Caratteristiche

### 1. **Input Interattivo**
- Campo Account ID personalizzabile
- Slider per Risk Score (0.0 - 1.0)
- Selezione Risk Level (Low, Medium, High, Critical)
- Configurazione endpoint API dinamica

### 2. **Visualizzazioni Grafiche**
- **Risk Score Distribution**: Grafico a ciambella che mostra la distribuzione del rischio
- **Risk Level Breakdown**: Grafico a barre per confrontare i livelli di rischio
- Grafici interattivi con Chart.js 4.4.0

### 3. **Metriche in Tempo Reale**
- Risk Score percentuale
- Risk Level classificato
- Account ID analizzato
- Timestamp dell'analisi

### 4. **AI Explanation**
- Spiegazioni generate da IBM watsonx.ai Granite
- Linguaggio naturale per compliance officer
- Fallback automatico se LLM non disponibile

## 🛠️ Tecnologie Utilizzate

- **HTML5** + **CSS3**: Interfaccia responsive
- **JavaScript ES6+**: Logica client-side
- **Chart.js 4.4.0**: Visualizzazioni grafiche
- **Fetch API**: Chiamate REST asincrone
- **IBM watsonx.governance**: Backend AI

## 📦 Struttura File

```
static/
├── index.html          # Dashboard principale
└── README.md          # Questa documentazione
```

## 🔧 Configurazione

### Endpoint API

L'endpoint predefinito è configurato per IBM Code Engine:
```
https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/explain
```

Per ambiente locale, modifica l'URL nel campo "API Endpoint":
```
http://localhost:8000/api/v1/explain
```

### Parametri Richiesta

La dashboard invia una richiesta POST con il seguente payload:

```json
{
  "account_id": "ACC-123",
  "risk_score": 0.75,
  "risk_level": "high",
  "aml_patterns": [],
  "recommendations": []
}
```

### Risposta Attesa

```json
{
  "account_id": "ACC-123",
  "explanation": "Spiegazione generata da IBM Granite...",
  "model_used": "ibm/granite-13b-chat-v2",
  "generated_at": "2024-01-15T10:30:00Z",
  "fallback_used": false
}
```

## 🎨 Design

### Palette Colori

- **Primary Gradient**: `#667eea` → `#764ba2`
- **Success (Low Risk)**: `#28a745`
- **Warning (Medium Risk)**: `#ffc107`
- **Danger (High Risk)**: `#dc3545`
- **Critical**: `#6f42c1`
- **IBM Blue**: `#0f62fe`

### Responsive Design

La dashboard è completamente responsive e si adatta a:
- Desktop (>1400px)
- Tablet (768px - 1400px)
- Mobile (<768px)

## 🚀 Utilizzo

### 1. Accesso alla Dashboard

**Produzione (IBM Code Engine):**
```
https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/dashboard
```

**Locale:**
```bash
# Avvia l'API
python run_api.py

# Apri nel browser
http://localhost:8000/dashboard
```

### 2. Analisi Rischio

1. **Inserisci Account ID**: es. `ACC-123`, `ACC-456`
2. **Imposta Risk Score**: valore tra 0.0 (basso) e 1.0 (alto)
3. **Seleziona Risk Level**: Low, Medium, High, Critical
4. **Clicca "Analizza Rischio"**

### 3. Interpretazione Risultati

#### Metriche
- **Risk Score**: Percentuale di rischio (0-100%)
- **Risk Level**: Classificazione categorica
- **Account ID**: Identificativo cliente analizzato
- **Timestamp**: Ora dell'analisi

#### Grafici
- **Risk Score Distribution**: Mostra quanto del rischio totale è presente
- **Risk Level Breakdown**: Confronta il livello attuale con gli altri

#### AI Explanation
Spiegazione dettagliata generata da IBM Granite che include:
- Motivazione del risk score
- Pattern AML rilevati
- Raccomandazioni per compliance officer

## 🔍 Esempi di Test

### Test 1: Basso Rischio
```
Account ID: ACC-001
Risk Score: 0.25
Risk Level: low
```
**Risultato Atteso**: Grafico verde, spiegazione rassicurante

### Test 2: Rischio Medio
```
Account ID: ACC-002
Risk Score: 0.55
Risk Level: medium
```
**Risultato Atteso**: Grafico giallo, raccomandazione di monitoraggio

### Test 3: Alto Rischio
```
Account ID: ACC-003
Risk Score: 0.85
Risk Level: high
```
**Risultato Atteso**: Grafico rosso, alert e raccomandazioni urgenti

### Test 4: Rischio Critico
```
Account ID: ACC-004
Risk Score: 0.95
Risk Level: critical
```
**Risultato Atteso**: Grafico viola, blocco immediato raccomandato

## 🐛 Troubleshooting

### Errore: "Errore nella chiamata API"

**Causa**: Endpoint API non raggiungibile o non configurato

**Soluzione**:
1. Verifica che l'API sia in esecuzione
2. Controlla l'URL dell'endpoint nel campo "API Endpoint"
3. Verifica la connessione di rete
4. Controlla i log del browser (F12 → Console)

### Errore: "Nessuna spiegazione disponibile"

**Causa**: Backend non ha restituito una spiegazione

**Soluzione**:
1. Verifica che watsonx.ai sia configurato (`.env`)
2. Controlla i log dell'API per errori
3. Verifica che `WATSONX_API_KEY` e `WATSONX_PROJECT_ID` siano impostati

### Grafici non visualizzati

**Causa**: Chart.js non caricato o errore JavaScript

**Soluzione**:
1. Verifica la connessione internet (Chart.js è caricato da CDN)
2. Controlla la console del browser per errori JavaScript
3. Ricarica la pagina (Ctrl+F5)

## 📊 Metriche Performance

- **Tempo di caricamento**: <2 secondi
- **Tempo risposta API**: 2-5 secondi (con Granite)
- **Tempo risposta API**: <1 secondo (fallback)
- **Dimensione pagina**: ~15KB (HTML+CSS+JS)
- **Dipendenze esterne**: Chart.js (CDN)

## 🔐 Sicurezza

### CORS
L'API è configurata con CORS per accettare richieste da qualsiasi origine (`*`).
In produzione, limitare a domini specifici.

### Validazione Input
- Account ID: stringa non vuota
- Risk Score: numero tra 0.0 e 1.0
- Risk Level: enum (low, medium, high, critical)

### HTTPS
In produzione, la dashboard usa HTTPS tramite IBM Code Engine.

## 🎯 Roadmap Future

- [ ] Autenticazione utente (IBM App ID)
- [ ] Storico analisi per account
- [ ] Export PDF dei report
- [ ] Grafici aggiuntivi (trend temporali)
- [ ] Notifiche real-time
- [ ] Integrazione con watsonx.governance UI
- [ ] Multi-lingua (EN, IT, ES, FR)
- [ ] Dark mode

## 📝 Note per Demo IBM

### Cosa Mostrare
1. ✅ Interfaccia moderna e professionale
2. ✅ Grafici interattivi con Chart.js
3. ✅ Chiamata API in tempo reale
4. ✅ Spiegazione AI da IBM Granite
5. ✅ Responsive design (mobile/desktop)

### Scenari Demo
1. **Scenario 1**: Analisi basso rischio → Mostra grafico verde
2. **Scenario 2**: Analisi alto rischio → Mostra alert rosso + spiegazione AI
3. **Scenario 3**: Cambio endpoint → Mostra flessibilità configurazione

### Punti di Forza
- ✅ Zero dipendenze backend (solo HTML+JS)
- ✅ Integrazione seamless con API REST
- ✅ Visualizzazioni professionali
- ✅ AI-powered explanations
- ✅ Production-ready su IBM Cloud

## 📞 Supporto

Per problemi o domande:
- Repository: https://github.com/asiaGermi/bobibm
- API Docs: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud/api/v1/docs

---

**Made with ❤️ for IBM watsonx.governance Demo**