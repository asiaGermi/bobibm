# Scripts di Deployment - bobibm

Questa directory contiene gli script per il deployment automatizzato su IBM Cloud e l'integrazione con Watson X Orchestrate.

---

## 📋 Script Disponibili

### 1. `deploy_unified.py`

Script principale per deployment unificato che gestisce:
- Build e push Docker image
- Deploy su IBM Cloud Code Engine tramite API
- Registrazione skills su Watson X Orchestrate
- Health check e verifica deployment

---

## 🚀 Quick Start

### Prerequisiti

1. **IBM Cloud CLI** installato
   ```bash
   curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
   ```

2. **Docker** installato e configurato

3. **Python 3.11+** con dipendenze:
   ```bash
   pip install requests
   ```

4. **Variabili Ambiente** configurate:
   ```bash
   export IBM_CLOUD_API_KEY="your-ibm-cloud-api-key"
   export WATSONX_API_KEY="your-watsonx-api-key"
   export WATSONX_INSTANCE_URL="https://your-instance.watsonx.ibm.com"
   export CODE_ENGINE_PROJECT_ID="ce-675000bo4y"
   ```

### Deployment Base

```bash
# Deploy su staging (default)
python scripts/deploy_unified.py

# Deploy su production
python scripts/deploy_unified.py --environment production --image-tag v1.2.0
```

---

## 📖 Uso Dettagliato

### Opzioni Disponibili

```bash
python scripts/deploy_unified.py [OPTIONS]

Options:
  --environment {dev,staging,production}
                        Environment di deployment (default: staging)
  
  --image-tag TAG       Tag Docker image (default: latest)
  
  --skip-build          Salta build Docker (usa immagine esistente)
  
  --skip-watsonx        Salta integrazione Watson X
  
  --project-id ID       Code Engine project ID
                        (default: da env CODE_ENGINE_PROJECT_ID)
  
  --app-name NAME       Nome applicazione Code Engine
                        (default: financial-risk-api)
  
  -h, --help           Mostra help
```

### Esempi di Uso

#### 1. Deploy Completo su Production

```bash
# Build, push e deploy con nuovo tag
python scripts/deploy_unified.py \
  --environment production \
  --image-tag v1.2.0
```

#### 2. Deploy Rapido (Skip Build)

```bash
# Usa immagine già esistente, solo update Code Engine
python scripts/deploy_unified.py \
  --environment staging \
  --image-tag latest \
  --skip-build
```

#### 3. Deploy Senza Watson X

```bash
# Deploy solo su Code Engine, senza registrare skills
python scripts/deploy_unified.py \
  --environment dev \
  --skip-watsonx
```

#### 4. Deploy con Project ID Custom

```bash
# Specifica project ID diverso
python scripts/deploy_unified.py \
  --project-id ce-custom-project \
  --app-name my-custom-app
```

---

## 🔧 Configurazione

### Variabili Ambiente Richieste

| Variabile | Descrizione | Richiesta |
|-----------|-------------|-----------|
| `IBM_CLOUD_API_KEY` | API Key IBM Cloud | ✅ Sì |
| `WATSONX_API_KEY` | API Key Watson X | ⚠️ Solo se non usi `--skip-watsonx` |
| `WATSONX_INSTANCE_URL` | URL istanza Watson X | ⚠️ Solo se non usi `--skip-watsonx` |
| `CODE_ENGINE_PROJECT_ID` | Project ID Code Engine | ⚠️ Opzionale (default: ce-675000bo4y) |
| `IBM_CLOUD_REGION` | Regione IBM Cloud | ⚠️ Opzionale (default: eu-de) |
| `REGISTRY_NAMESPACE` | Namespace Container Registry | ⚠️ Opzionale (default: financial-risk) |

### File `.env` (Opzionale)

Puoi creare un file `.env` nella root del progetto:

```bash
# .env
IBM_CLOUD_API_KEY=your-api-key-here
WATSONX_API_KEY=your-watsonx-key-here
WATSONX_INSTANCE_URL=https://your-instance.watsonx.ibm.com
CODE_ENGINE_PROJECT_ID=ce-675000bo4y
IBM_CLOUD_REGION=eu-de
REGISTRY_NAMESPACE=financial-risk
```

Poi caricalo prima di eseguire lo script:

```bash
export $(cat .env | xargs)
python scripts/deploy_unified.py
```

---

## 📊 Output dello Script

Lo script produce output dettagliato per ogni fase:

```
======================================================================
🚀 Deployment Unificato - IBM Cloud & Watson X
======================================================================
Environment: production
Image Tag: v1.2.0
Project ID: ce-675000bo4y
App Name: financial-risk-api
Region: eu-de
======================================================================

[1/5] 🐳 Build e Push Docker Image
🐳 Building Docker image: eu-de.icr.io/financial-risk/financial-risk-api:v1.2.0
✅ Image built successfully
📤 Pushing image to registry...
✅ Image pushed successfully

[2/5] 📦 Deploy su IBM Cloud Code Engine
🔐 Ottenendo IAM token...
✅ Token ottenuto con successo
📦 Aggiornando app financial-risk-api...
✅ App aggiornata con successo

[3/5] ⏳ Verifica Deployment
⏳ Attendendo che financial-risk-api sia ready...
   Status: deploying
   Status: ready
✅ App financial-risk-api is ready!

📍 App URL: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud

[4/5] 🏥 Health Check
🏥 Health check: https://financial-risk-api.../health
✅ Health check passed!
   Status: healthy
   Data layer: connected
   Transactions: 15,000

[5/5] 🤖 Integrazione Watson X Orchestrate
🔐 Ottenendo Watson X token...
✅ Watson X token ottenuto
📝 Registrando skill: transaction-analysis...
✅ Skill transaction-analysis registrata (ID: skill-123)
📝 Registrando skill: risk-assessment...
✅ Skill risk-assessment registrata (ID: skill-124)
📝 Registrando skill: fraud-detection...
✅ Skill fraud-detection registrata (ID: skill-125)
📝 Registrando skill: recommendation...
✅ Skill recommendation registrata (ID: skill-126)

======================================================================
✅ Deployment completato con successo!
======================================================================

📍 App URL: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
📚 API Docs: https://financial-risk-api.../docs
🏥 Health: https://financial-risk-api.../health

🔗 Endpoints:
   • Transaction Analysis: .../api/v1/analyze/transaction
   • Risk Assessment: .../api/v1/assess/risk
   • Fraud Detection: .../api/v1/detect/fraud
   • Recommendations: .../api/v1/recommend/actions

💾 Deployment info salvato in: deployment-info.json
```

### File `deployment-info.json`

Lo script salva informazioni sul deployment in `deployment-info.json`:

```json
{
  "timestamp": "2026-06-22T14:30:00.000000",
  "environment": "production",
  "image_tag": "v1.2.0",
  "app_url": "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud",
  "project_id": "ce-675000bo4y",
  "app_name": "financial-risk-api",
  "region": "eu-de"
}
```

---

## 🔍 Troubleshooting

### Errore: "IBM_CLOUD_API_KEY non impostata"

**Soluzione**: Imposta la variabile ambiente:
```bash
export IBM_CLOUD_API_KEY="your-api-key"
```

### Errore: "Docker build failed"

**Possibili cause**:
- Docker non in esecuzione
- Dockerfile non trovato
- Errori nel codice

**Soluzione**:
```bash
# Verifica Docker
docker ps

# Build manuale per vedere errori
docker build -t test .
```

### Errore: "Docker push failed"

**Soluzione**: Login a IBM Container Registry:
```bash
ibmcloud cr login
```

### Errore: "Errore update app"

**Possibili cause**:
- Token IAM scaduto
- Project ID errato
- Permessi insufficienti

**Soluzione**:
```bash
# Verifica project ID
ibmcloud ce project list

# Verifica permessi
ibmcloud iam user-policies <your-email>
```

### Warning: "Health check failed"

**Possibili cause**:
- App non ancora pronta
- Errori nell'applicazione
- Dataset non caricato

**Soluzione**:
```bash
# Verifica logs
ibmcloud ce app logs --name financial-risk-api

# Verifica manualmente
curl https://your-app-url/health
```

### Errore Watson X: "Errore registrazione skill"

**Possibili cause**:
- URL Watson X errato
- API key non valida
- Endpoint API non disponibile

**Soluzione**: Usa `--skip-watsonx` per ora:
```bash
python scripts/deploy_unified.py --skip-watsonx
```

---

## 🔄 Workflow CI/CD

### GitHub Actions

Esempio di workflow per GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to IBM Cloud

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Setup IBM Cloud CLI
        run: |
          curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
          ibmcloud plugin install code-engine
          ibmcloud plugin install container-registry
      
      - name: Deploy
        env:
          IBM_CLOUD_API_KEY: ${{ secrets.IBM_CLOUD_API_KEY }}
          WATSONX_API_KEY: ${{ secrets.WATSONX_API_KEY }}
          WATSONX_INSTANCE_URL: ${{ secrets.WATSONX_INSTANCE_URL }}
        run: |
          python scripts/deploy_unified.py \
            --environment ${{ github.event.inputs.environment || 'staging' }} \
            --image-tag ${{ github.sha }}
```

---

## 📚 Risorse

- [IBM Cloud Code Engine API](https://cloud.ibm.com/apidocs/codeengine)
- [Watson X Orchestrate Docs](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [IBM Cloud CLI](https://cloud.ibm.com/docs/cli)
- [Docker Documentation](https://docs.docker.com/)

---

## 🆘 Supporto

Per problemi o domande:

1. Verifica i logs: `ibmcloud ce app logs --name financial-risk-api`
2. Controlla lo status: `ibmcloud ce app get --name financial-risk-api`
3. Consulta la documentazione: `bobibm/docs/deployment/`

---

**Ultimo aggiornamento**: 22 Giugno 2026