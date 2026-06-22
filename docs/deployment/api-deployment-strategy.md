# Strategia di Deployment Unificato tramite API - IBM Cloud & Watson X

**Progetto**: bobibm - Financial Risk Management  
**Data**: 22 Giugno 2026  
**Focus**: Deployment tramite API, integrazione Watson X, automazione

---

## 🎯 Obiettivo

Studiare e documentare come fare deployment unificato del progetto bobibm su IBM Cloud utilizzando **API-based deployment** e integrare con **Watson X Orchestrate**, considerando che:

1. **Facciamo già deploy tramite API** (IBM Cloud Code Engine)
2. Vogliamo integrare con Watson X Orchestrate
3. Terraform è opzionale - focus su API e automazione

---

## 📊 Situazione Attuale

### Deployment Esistente

Attualmente il progetto usa **IBM Cloud Code Engine** con deployment già funzionante:

```
✅ Code Engine Project: ce-675000bo4y (eu-de)
✅ App URL: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud
✅ Container Registry: private.de.icr.io/financial-risk/financial-risk-management:latest
✅ Deployment: Revisione 00007, porta 8000
✅ Dataset: 15.000 transazioni sample
```

### API Endpoints Disponibili

```python
POST /api/v1/analyze/transaction    # Transaction Analysis Agent
POST /api/v1/assess/risk            # Risk Assessment Agent  
POST /api/v1/detect/fraud           # Fraud Detection Agent
POST /api/v1/recommend/actions      # Recommendation Agent
GET  /health                        # Health check
```

---

## 🔧 IBM Cloud Code Engine - Deployment tramite API

### 1. IBM Cloud Code Engine API

IBM Cloud Code Engine espone API REST per gestire applicazioni:

**Base URL**: `https://api.{region}.codeengine.cloud.ibm.com/v2`

#### Autenticazione

```bash
# Ottieni IAM token
curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  -d "apikey=${IBM_CLOUD_API_KEY}"

# Risposta
{
  "access_token": "eyJhbGc...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### Operazioni Principali

**1. Creare/Aggiornare Applicazione**

```bash
# Update app via API
curl -X PATCH \
  "https://api.eu-de.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps/financial-risk-api" \
  -H "Authorization: Bearer ${IAM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "image_reference": "eu-de.icr.io/financial-risk/financial-risk-api:v1.2.0",
    "scale_min_instances": 3,
    "scale_max_instances": 10,
    "scale_cpu_limit": "1",
    "scale_memory_limit": "2G",
    "run_env_variables": [
      {
        "type": "literal",
        "name": "ENVIRONMENT",
        "value": "production"
      },
      {
        "type": "secret_ref",
        "name": "WATSONX_API_KEY",
        "reference": "watsonx-api-key"
      }
    ]
  }'
```

**2. Ottenere Status Applicazione**

```bash
curl -X GET \
  "https://api.eu-de.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/apps/financial-risk-api" \
  -H "Authorization: Bearer ${IAM_TOKEN}"

# Risposta
{
  "name": "financial-risk-api",
  "status": "ready",
  "endpoint": "financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud",
  "scale_min_instances": 3,
  "scale_max_instances": 10,
  "image_reference": "eu-de.icr.io/financial-risk/financial-risk-api:v1.2.0"
}
```

**3. Gestire Secrets**

```bash
# Creare secret
curl -X POST \
  "https://api.eu-de.codeengine.cloud.ibm.com/v2/projects/${PROJECT_ID}/secrets" \
  -H "Authorization: Bearer ${IAM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "watsonx-api-key",
    "format": "generic",
    "data": {
      "api_key": "base64_encoded_value"
    }
  }'
```

---

## 🤖 Watson X Orchestrate - Integrazione tramite API

### 1. Watson X Orchestrate API

Watson X Orchestrate permette di registrare "skills" (i nostri endpoint API) e creare workflow orchestrati.

**Base URL**: Dipende dall'istanza (es. `https://your-instance.watsonx.ibm.com`)

#### Autenticazione Watson X

```bash
# Con API Key
curl -X POST "https://your-instance.watsonx.ibm.com/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "apikey": "${WATSONX_API_KEY}"
  }'

# Risposta
{
  "access_token": "wxo_token...",
  "expires_in": 7200
}
```

### 2. Registrare Skills tramite API

Ogni nostro endpoint API diventa una "skill" in Watson X:

```python
# register_watsonx_skills.py
import requests
import os

WATSONX_URL = os.getenv('WATSONX_INSTANCE_URL')
WATSONX_TOKEN = os.getenv('WATSONX_TOKEN')
API_BASE_URL = "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"

skills = [
    {
        "name": "transaction-analysis",
        "display_name": "Analisi Transazioni",
        "description": "Analizza pattern transazionali e rileva anomalie AML",
        "endpoint": {
            "url": f"{API_BASE_URL}/api/v1/analyze/transaction",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            }
        },
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "ID del conto da analizzare"
                },
                "days": {
                    "type": "integer",
                    "description": "Numero di giorni da analizzare",
                    "default": 30
                }
            },
            "required": ["account_id"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "patterns": {"type": "array"},
                "anomalies": {"type": "array"},
                "risk_indicators": {"type": "object"}
            }
        }
    },
    {
        "name": "risk-assessment",
        "display_name": "Valutazione Rischio",
        "description": "Calcola risk score per account",
        "endpoint": {
            "url": f"{API_BASE_URL}/api/v1/assess/risk",
            "method": "POST"
        },
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["standard", "high_risk_scan"],
                    "default": "standard"
                }
            },
            "required": ["account_id"]
        }
    },
    {
        "name": "fraud-detection",
        "display_name": "Rilevamento Frodi",
        "description": "Rileva attività fraudolente",
        "endpoint": {
            "url": f"{API_BASE_URL}/api/v1/detect/fraud",
            "method": "POST"
        }
    },
    {
        "name": "recommendation",
        "display_name": "Raccomandazioni Compliance",
        "description": "Genera azioni raccomandate",
        "endpoint": {
            "url": f"{API_BASE_URL}/api/v1/recommend/actions",
            "method": "POST"
        }
    }
]

def register_skill(skill):
    """Registra una skill su Watson X Orchestrate"""
    response = requests.post(
        f"{WATSONX_URL}/api/v1/skills",
        headers={
            "Authorization": f"Bearer {WATSONX_TOKEN}",
            "Content-Type": "application/json"
        },
        json=skill
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Skill registrata: {skill['name']}")
        return response.json()
    else:
        print(f"❌ Errore: {response.status_code} - {response.text}")
        return None

def main():
    print("🚀 Registrazione skills su Watson X Orchestrate...")
    
    for skill in skills:
        result = register_skill(skill)
        if result:
            print(f"   Skill ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
    
    print("\n✅ Registrazione completata!")

if __name__ == "__main__":
    main()
```

### 3. Creare Workflow Orchestrato

Una volta registrate le skills, creiamo un workflow che le orchestra:

```python
# create_watsonx_workflow.py
import requests
import os

WATSONX_URL = os.getenv('WATSONX_INSTANCE_URL')
WATSONX_TOKEN = os.getenv('WATSONX_TOKEN')

workflow = {
    "name": "financial-risk-assessment-workflow",
    "display_name": "Workflow Completo Valutazione Rischio Finanziario",
    "description": "Workflow orchestrato per analisi completa rischio AML",
    "steps": [
        {
            "id": "step1",
            "name": "Analisi Transazioni",
            "skill": "transaction-analysis",
            "input_mapping": {
                "account_id": "{{workflow.input.account_id}}",
                "days": "{{workflow.input.days | default(30)}}"
            },
            "output_mapping": {
                "patterns": "{{step1.output.patterns}}",
                "anomalies": "{{step1.output.anomalies}}"
            }
        },
        {
            "id": "step2",
            "name": "Valutazione Rischio",
            "skill": "risk-assessment",
            "depends_on": ["step1"],
            "input_mapping": {
                "account_id": "{{workflow.input.account_id}}",
                "mode": "{{step1.output.anomalies | length > 0 ? 'high_risk_scan' : 'standard'}}"
            },
            "output_mapping": {
                "risk_score": "{{step2.output.risk_score}}",
                "risk_level": "{{step2.output.risk_level}}"
            }
        },
        {
            "id": "step3",
            "name": "Rilevamento Frodi",
            "skill": "fraud-detection",
            "depends_on": ["step1"],
            "condition": "{{step2.output.risk_score > 0.7}}",
            "input_mapping": {
                "account_id": "{{workflow.input.account_id}}",
                "mode": "account_profile"
            }
        },
        {
            "id": "step4",
            "name": "Generazione Raccomandazioni",
            "skill": "recommendation",
            "depends_on": ["step2", "step3"],
            "input_mapping": {
                "risk_score": "{{step2.output.risk_score}}",
                "patterns": "{{step1.output.patterns}}",
                "fraud_signals": "{{step3.output.fraud_signals | default([])}}"
            }
        }
    ],
    "output_mapping": {
        "account_id": "{{workflow.input.account_id}}",
        "analysis_timestamp": "{{workflow.execution_time}}",
        "patterns_detected": "{{step1.output.patterns}}",
        "risk_assessment": {
            "score": "{{step2.output.risk_score}}",
            "level": "{{step2.output.risk_level}}",
            "factors": "{{step2.output.risk_factors}}"
        },
        "fraud_indicators": "{{step3.output.fraud_signals | default([])}}",
        "recommendations": "{{step4.output.actions}}"
    }
}

def create_workflow():
    """Crea workflow orchestrato su Watson X"""
    response = requests.post(
        f"{WATSONX_URL}/api/v1/workflows",
        headers={
            "Authorization": f"Bearer {WATSONX_TOKEN}",
            "Content-Type": "application/json"
        },
        json=workflow
    )
    
    if response.status_code in [200, 201]:
        print("✅ Workflow creato con successo!")
        result = response.json()
        print(f"   Workflow ID: {result.get('id')}")
        print(f"   Status: {result.get('status')}")
        return result
    else:
        print(f"❌ Errore: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Creazione workflow Watson X Orchestrate...")
    create_workflow()
```

### 4. Eseguire Workflow tramite API

```python
# execute_watsonx_workflow.py
import requests
import os
import time

WATSONX_URL = os.getenv('WATSONX_INSTANCE_URL')
WATSONX_TOKEN = os.getenv('WATSONX_TOKEN')
WORKFLOW_ID = os.getenv('WORKFLOW_ID')

def execute_workflow(account_id, days=30):
    """Esegue il workflow per un account specifico"""
    
    # Avvia esecuzione
    response = requests.post(
        f"{WATSONX_URL}/api/v1/workflows/{WORKFLOW_ID}/executions",
        headers={
            "Authorization": f"Bearer {WATSONX_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "input": {
                "account_id": account_id,
                "days": days
            }
        }
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Errore avvio workflow: {response.text}")
        return None
    
    execution = response.json()
    execution_id = execution['id']
    print(f"✅ Workflow avviato - Execution ID: {execution_id}")
    
    # Polling per status
    while True:
        status_response = requests.get(
            f"{WATSONX_URL}/api/v1/workflows/{WORKFLOW_ID}/executions/{execution_id}",
            headers={"Authorization": f"Bearer {WATSONX_TOKEN}"}
        )
        
        if status_response.status_code != 200:
            print(f"❌ Errore verifica status: {status_response.text}")
            return None
        
        execution_status = status_response.json()
        status = execution_status['status']
        
        print(f"   Status: {status}")
        
        if status == 'completed':
            print("✅ Workflow completato!")
            return execution_status['output']
        elif status == 'failed':
            print(f"❌ Workflow fallito: {execution_status.get('error')}")
            return None
        
        time.sleep(2)

if __name__ == "__main__":
    # Esempio di esecuzione
    result = execute_workflow("ACC001", days=30)
    
    if result:
        print("\n📊 Risultati:")
        print(f"   Risk Score: {result['risk_assessment']['score']}")
        print(f"   Risk Level: {result['risk_assessment']['level']}")
        print(f"   Patterns: {len(result['patterns_detected'])}")
        print(f"   Recommendations: {len(result['recommendations'])}")
```

---

## 🔄 Pipeline di Deployment Unificato

### Script Python Completo per Deployment

```python
# deploy_unified.py
"""
Script unificato per deployment su IBM Cloud Code Engine
e registrazione skills su Watson X Orchestrate
"""

import os
import sys
import json
import time
import requests
import subprocess
from typing import Dict, Optional

class IBMCloudDeployer:
    """Gestisce deployment su IBM Cloud Code Engine tramite API"""
    
    def __init__(self, api_key: str, region: str = "eu-de"):
        self.api_key = api_key
        self.region = region
        self.base_url = f"https://api.{region}.codeengine.cloud.ibm.com/v2"
        self.token = None
        
    def get_iam_token(self) -> str:
        """Ottiene IAM token per autenticazione"""
        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
        )
        response.raise_for_status()
        self.token = response.json()['access_token']
        return self.token
    
    def update_app(self, project_id: str, app_name: str, config: Dict) -> Dict:
        """Aggiorna applicazione Code Engine"""
        if not self.token:
            self.get_iam_token()
        
        url = f"{self.base_url}/projects/{project_id}/apps/{app_name}"
        response = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=config
        )
        response.raise_for_status()
        return response.json()
    
    def get_app_status(self, project_id: str, app_name: str) -> Dict:
        """Ottiene status applicazione"""
        if not self.token:
            self.get_iam_token()
        
        url = f"{self.base_url}/projects/{project_id}/apps/{app_name}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_ready(self, project_id: str, app_name: str, timeout: int = 300):
        """Attende che l'app sia ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_app_status(project_id, app_name)
            
            if status['status'] == 'ready':
                print(f"✅ App {app_name} is ready!")
                return True
            
            print(f"   Status: {status['status']} - waiting...")
            time.sleep(10)
        
        raise TimeoutError(f"App {app_name} not ready after {timeout}s")


class WatsonXIntegrator:
    """Gestisce integrazione con Watson X Orchestrate"""
    
    def __init__(self, instance_url: str, api_key: str):
        self.instance_url = instance_url
        self.api_key = api_key
        self.token = None
    
    def get_token(self) -> str:
        """Ottiene token Watson X"""
        response = requests.post(
            f"{self.instance_url}/api/v1/auth/token",
            json={"apikey": self.api_key}
        )
        response.raise_for_status()
        self.token = response.json()['access_token']
        return self.token
    
    def register_skill(self, skill: Dict) -> Dict:
        """Registra una skill"""
        if not self.token:
            self.get_token()
        
        response = requests.post(
            f"{self.instance_url}/api/v1/skills",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=skill
        )
        response.raise_for_status()
        return response.json()
    
    def create_workflow(self, workflow: Dict) -> Dict:
        """Crea workflow orchestrato"""
        if not self.token:
            self.get_token()
        
        response = requests.post(
            f"{self.instance_url}/api/v1/workflows",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=workflow
        )
        response.raise_for_status()
        return response.json()


def build_and_push_image(registry_url: str, image_tag: str):
    """Build e push Docker image"""
    print("🐳 Building Docker image...")
    
    subprocess.run([
        "docker", "build",
        "-t", f"{registry_url}:{image_tag}",
        "."
    ], check=True)
    
    print("📤 Pushing to registry...")
    subprocess.run([
        "docker", "push",
        f"{registry_url}:{image_tag}"
    ], check=True)
    
    print("✅ Image pushed successfully!")


def main():
    # Configurazione
    IBM_CLOUD_API_KEY = os.getenv('IBM_CLOUD_API_KEY')
    WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
    WATSONX_INSTANCE_URL = os.getenv('WATSONX_INSTANCE_URL')
    
    PROJECT_ID = "ce-675000bo4y"
    APP_NAME = "financial-risk-api"
    REGION = "eu-de"
    IMAGE_TAG = os.getenv('IMAGE_TAG', 'latest')
    
    REGISTRY_URL = f"{REGION}.icr.io/financial-risk/financial-risk-api"
    
    print("🚀 Deployment Unificato - IBM Cloud & Watson X")
    print("=" * 60)
    
    # Step 1: Build e Push Image
    print("\n[1/4] Build e Push Docker Image")
    build_and_push_image(REGISTRY_URL, IMAGE_TAG)
    
    # Step 2: Deploy su Code Engine
    print("\n[2/4] Deploy su IBM Cloud Code Engine")
    deployer = IBMCloudDeployer(IBM_CLOUD_API_KEY, REGION)
    
    app_config = {
        "image_reference": f"{REGISTRY_URL}:{IMAGE_TAG}",
        "scale_min_instances": 3,
        "scale_max_instances": 10,
        "scale_cpu_limit": "1",
        "scale_memory_limit": "2G",
        "run_env_variables": [
            {"type": "literal", "name": "ENVIRONMENT", "value": "production"},
            {"type": "literal", "name": "LOG_LEVEL", "value": "INFO"}
        ]
    }
    
    result = deployer.update_app(PROJECT_ID, APP_NAME, app_config)
    print(f"✅ App updated: {result['name']}")
    
    # Attendi che sia ready
    deployer.wait_for_ready(PROJECT_ID, APP_NAME)
    
    # Ottieni URL
    app_status = deployer.get_app_status(PROJECT_ID, APP_NAME)
    app_url = f"https://{app_status['endpoint']}"
    print(f"   App URL: {app_url}")
    
    # Step 3: Registra Skills su Watson X
    print("\n[3/4] Registrazione Skills su Watson X Orchestrate")
    wxo = WatsonXIntegrator(WATSONX_INSTANCE_URL, WATSONX_API_KEY)
    
    skills = [
        {
            "name": "transaction-analysis",
            "endpoint": {"url": f"{app_url}/api/v1/analyze/transaction", "method": "POST"}
        },
        {
            "name": "risk-assessment",
            "endpoint": {"url": f"{app_url}/api/v1/assess/risk", "method": "POST"}
        },
        {
            "name": "fraud-detection",
            "endpoint": {"url": f"{app_url}/api/v1/detect/fraud", "method": "POST"}
        },
        {
            "name": "recommendation",
            "endpoint": {"url": f"{app_url}/api/v1/recommend/actions", "method": "POST"}
        }
    ]
    
    for skill in skills:
        result = wxo.register_skill(skill)
        print(f"✅ Skill registered: {skill['name']} (ID: {result['id']})")
    
    # Step 4: Health Check
    print("\n[4/4] Health Check")
    response = requests.get(f"{app_url}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Health check passed!")
        print(f"   Status: {health['status']}")
        print(f"   Data layer: {health['data_layer_status']}")
    
    print("\n" + "=" * 60)
    print("✅ Deployment completato con successo!")
    print(f"\n📍 App URL: {app_url}")
    print(f"📚 API Docs: {app_url}/docs")


if __name__ == "__main__":
    main()
```

### Esecuzione

```bash
# Imposta variabili ambiente
export IBM_CLOUD_API_KEY="your-ibm-cloud-api-key"
export WATSONX_API_KEY="your-watsonx-api-key"
export WATSONX_INSTANCE_URL="https://your-instance.watsonx.ibm.com"
export IMAGE_TAG="v1.2.0"

# Esegui deployment
python deploy_unified.py
```

---

## 📝 Checklist Deployment

### Pre-requisiti
- [ ] IBM Cloud API Key generata
- [ ] Watson X Orchestrate instance attiva
- [ ] Watson X API Key generata
- [ ] Docker installato e configurato
- [ ] Python 3.11+ con requests installato

### Deployment Steps
- [ ] Build Docker image
- [ ] Push image su IBM Container Registry
- [ ] Update Code Engine app tramite API
- [ ] Verifica app status (ready)
- [ ] Test health endpoint
- [ ] Registra skills su Watson X
- [ ] Crea workflow orchestrato
- [ ] Test workflow end-to-end

### Post-Deployment
- [ ] Verifica logs in LogDNA
- [ ] Verifica metriche in Sysdig
- [ ] Test tutti gli endpoint API
- [ ] Test workflow Watson X
- [ ] Documentazione aggiornata

---

## 🎯 Vantaggi Approccio API-Based

1. **Automazione Completa**: Tutto via API, nessun click manuale
2. **CI/CD Ready**: Facile integrazione in GitHub Actions
3. **Ripetibile**: Stesso processo per dev/staging/production
4. **Veloce**: Deploy in minuti, non ore
5. **Tracciabile**: Ogni operazione loggata e verificabile
6. **Flessibile**: Facile modificare configurazioni

---

## 📚 Risorse

- [IBM Cloud Code Engine API](https://cloud.ibm.com/apidocs/codeengine)
- [Watson X Orchestrate Docs](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [IBM Cloud IAM API](https://cloud.ibm.com/apidocs/iam-identity-token-api)

---

**Status**: ✅ Strategia Definita - Pronto per Implementazione  
**Next**: Implementare script Python e testare deployment