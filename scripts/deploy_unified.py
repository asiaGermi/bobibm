#!/usr/bin/env python3
"""
Script Unificato per Deployment su IBM Cloud Code Engine
e Registrazione Skills su Watson X Orchestrate

Usage:
    python deploy_unified.py --environment production --image-tag v1.2.0
"""

import os
import sys
import json
import time
import argparse
import requests
import subprocess
from typing import Dict, Optional, List
from datetime import datetime


class IBMCloudDeployer:
    """Gestisce deployment su IBM Cloud Code Engine tramite API"""
    
    def __init__(self, api_key: str, region: str = "eu-de"):
        self.api_key = api_key
        self.region = region
        self.base_url = f"https://api.{region}.codeengine.cloud.ibm.com/v2"
        self.token = None
        self.token_expiry = None
        
    def get_iam_token(self) -> str:
        """Ottiene IAM token per autenticazione IBM Cloud"""
        print("🔐 Ottenendo IAM token...")
        
        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Errore ottenimento token: {response.text}")
        
        data = response.json()
        self.token = data['access_token']
        self.token_expiry = time.time() + data['expires_in']
        
        print("✅ Token ottenuto con successo")
        return self.token
    
    def _ensure_token(self):
        """Assicura che il token sia valido"""
        if not self.token or (self.token_expiry and time.time() >= self.token_expiry - 60):
            self.get_iam_token()
    
    def update_app(self, project_id: str, app_name: str, config: Dict) -> Dict:
        """Aggiorna applicazione Code Engine"""
        self._ensure_token()
        
        print(f"📦 Aggiornando app {app_name}...")
        
        url = f"{self.base_url}/projects/{project_id}/apps/{app_name}"
        response = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=config
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"Errore update app: {response.status_code} - {response.text}")
        
        print("✅ App aggiornata con successo")
        return response.json()
    
    def get_app_status(self, project_id: str, app_name: str) -> Dict:
        """Ottiene status applicazione"""
        self._ensure_token()
        
        url = f"{self.base_url}/projects/{project_id}/apps/{app_name}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Errore get status: {response.status_code} - {response.text}")
        
        return response.json()
    
    def wait_for_ready(self, project_id: str, app_name: str, timeout: int = 300) -> bool:
        """Attende che l'app sia ready"""
        print(f"⏳ Attendendo che {app_name} sia ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_app_status(project_id, app_name)
                
                current_status = status.get('status', 'unknown')
                print(f"   Status: {current_status}")
                
                if current_status == 'ready':
                    print(f"✅ App {app_name} is ready!")
                    return True
                
                if current_status == 'failed':
                    raise Exception(f"App deployment failed: {status.get('status_details', {})}")
                
            except Exception as e:
                print(f"   Errore verifica status: {e}")
            
            time.sleep(10)
        
        raise TimeoutError(f"App {app_name} not ready after {timeout}s")
    
    def create_secret(self, project_id: str, secret_name: str, data: Dict) -> Dict:
        """Crea o aggiorna un secret"""
        self._ensure_token()
        
        print(f"🔒 Creando secret {secret_name}...")
        
        # Encode data in base64
        import base64
        encoded_data = {
            key: base64.b64encode(value.encode()).decode()
            for key, value in data.items()
        }
        
        url = f"{self.base_url}/projects/{project_id}/secrets"
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={
                "name": secret_name,
                "format": "generic",
                "data": encoded_data
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Secret {secret_name} creato")
            return response.json()
        elif response.status_code == 409:
            print(f"ℹ️  Secret {secret_name} già esistente")
            return {"name": secret_name, "status": "exists"}
        else:
            raise Exception(f"Errore creazione secret: {response.status_code} - {response.text}")


class WatsonXIntegrator:
    """Gestisce integrazione con Watson X Orchestrate"""
    
    def __init__(self, instance_url: str, api_key: str):
        self.instance_url = instance_url.rstrip('/')
        self.api_key = api_key
        self.token = None
        self.token_expiry = None
    
    def get_token(self) -> str:
        """Ottiene token Watson X"""
        print("🔐 Ottenendo Watson X token...")
        
        # Nota: L'endpoint esatto dipende dalla tua istanza Watson X
        # Potrebbe essere necessario usare IBM Cloud IAM invece
        try:
            response = requests.post(
                f"{self.instance_url}/api/v1/auth/token",
                json={"apikey": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.token_expiry = time.time() + data.get('expires_in', 3600)
                print("✅ Watson X token ottenuto")
                return self.token
        except Exception as e:
            print(f"⚠️  Errore ottenimento token Watson X: {e}")
            print("   Usando API key direttamente...")
        
        # Fallback: usa API key direttamente
        self.token = self.api_key
        return self.token
    
    def _ensure_token(self):
        """Assicura che il token sia valido"""
        if not self.token or (self.token_expiry and time.time() >= self.token_expiry - 60):
            self.get_token()
    
    def register_skill(self, skill: Dict) -> Optional[Dict]:
        """Registra una skill"""
        self._ensure_token()
        
        print(f"📝 Registrando skill: {skill['name']}...")
        
        try:
            response = requests.post(
                f"{self.instance_url}/api/v1/skills",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=skill,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Skill {skill['name']} registrata (ID: {result.get('id', 'N/A')})")
                return result
            elif response.status_code == 409:
                print(f"ℹ️  Skill {skill['name']} già esistente")
                return {"name": skill['name'], "status": "exists"}
            else:
                print(f"⚠️  Errore registrazione skill: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"⚠️  Errore registrazione skill {skill['name']}: {e}")
            return None
    
    def create_workflow(self, workflow: Dict) -> Optional[Dict]:
        """Crea workflow orchestrato"""
        self._ensure_token()
        
        print(f"🔄 Creando workflow: {workflow['name']}...")
        
        try:
            response = requests.post(
                f"{self.instance_url}/api/v1/workflows",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=workflow,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Workflow creato (ID: {result.get('id', 'N/A')})")
                return result
            else:
                print(f"⚠️  Errore creazione workflow: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"⚠️  Errore creazione workflow: {e}")
            return None


def build_and_push_image(registry_url: str, image_tag: str, skip_build: bool = False):
    """Build e push Docker image"""
    
    if skip_build:
        print("⏭️  Skipping Docker build (--skip-build)")
        return
    
    full_image = f"{registry_url}:{image_tag}"
    
    print(f"🐳 Building Docker image: {full_image}")
    
    try:
        subprocess.run(
            ["docker", "build", "-t", full_image, "."],
            check=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        print("✅ Image built successfully")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Docker build failed: {e}")
    
    print(f"📤 Pushing image to registry...")
    
    try:
        # Login to IBM Container Registry
        subprocess.run(["ibmcloud", "cr", "login"], check=True)
        
        # Push image
        subprocess.run(["docker", "push", full_image], check=True)
        print("✅ Image pushed successfully")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Docker push failed: {e}")


def health_check(app_url: str, max_retries: int = 5) -> bool:
    """Verifica health dell'applicazione"""
    print(f"🏥 Health check: {app_url}/health")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{app_url}/health", timeout=10)
            
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Health check passed!")
                print(f"   Status: {health.get('status')}")
                print(f"   Data layer: {health.get('data_layer_status')}")
                print(f"   Transactions: {health.get('total_transactions', 0):,}")
                return True
            else:
                print(f"   Attempt {attempt + 1}/{max_retries}: Status {response.status_code}")
        except Exception as e:
            print(f"   Attempt {attempt + 1}/{max_retries}: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(5)
    
    print("⚠️  Health check failed")
    return False


def main():
    parser = argparse.ArgumentParser(description="Deploy bobibm to IBM Cloud")
    parser.add_argument("--environment", default="staging", choices=["dev", "staging", "production"])
    parser.add_argument("--image-tag", default="latest", help="Docker image tag")
    parser.add_argument("--skip-build", action="store_true", help="Skip Docker build")
    parser.add_argument("--skip-watsonx", action="store_true", help="Skip Watson X integration")
    parser.add_argument("--project-id", help="Code Engine project ID")
    parser.add_argument("--app-name", default="financial-risk-api", help="App name")
    
    args = parser.parse_args()
    
    # Configurazione da environment variables
    IBM_CLOUD_API_KEY = os.getenv('IBM_CLOUD_API_KEY')
    WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
    WATSONX_INSTANCE_URL = os.getenv('WATSONX_INSTANCE_URL')
    
    if not IBM_CLOUD_API_KEY:
        print("❌ IBM_CLOUD_API_KEY non impostata")
        sys.exit(1)
    
    # Configurazione deployment
    PROJECT_ID = args.project_id or os.getenv('CODE_ENGINE_PROJECT_ID', 'ce-675000bo4y')
    APP_NAME = args.app_name
    REGION = os.getenv('IBM_CLOUD_REGION', 'eu-de')
    REGISTRY_NAMESPACE = os.getenv('REGISTRY_NAMESPACE', 'financial-risk')
    
    REGISTRY_URL = f"{REGION}.icr.io/{REGISTRY_NAMESPACE}/{APP_NAME}"
    
    print("=" * 70)
    print("🚀 Deployment Unificato - IBM Cloud & Watson X")
    print("=" * 70)
    print(f"Environment: {args.environment}")
    print(f"Image Tag: {args.image_tag}")
    print(f"Project ID: {PROJECT_ID}")
    print(f"App Name: {APP_NAME}")
    print(f"Region: {REGION}")
    print("=" * 70)
    
    try:
        # Step 1: Build e Push Image
        if not args.skip_build:
            print("\n[1/5] 🐳 Build e Push Docker Image")
            build_and_push_image(REGISTRY_URL, args.image_tag, args.skip_build)
        else:
            print("\n[1/5] ⏭️  Skipping Docker build")
        
        # Step 2: Deploy su Code Engine
        print("\n[2/5] 📦 Deploy su IBM Cloud Code Engine")
        deployer = IBMCloudDeployer(IBM_CLOUD_API_KEY, REGION)
        
        # Configurazione app basata su environment
        scale_config = {
            "dev": {"min": 1, "max": 2},
            "staging": {"min": 2, "max": 5},
            "production": {"min": 3, "max": 10}
        }
        
        scale = scale_config[args.environment]
        
        app_config = {
            "image_reference": f"{REGISTRY_URL}:{args.image_tag}",
            "scale_min_instances": scale["min"],
            "scale_max_instances": scale["max"],
            "scale_cpu_limit": "1",
            "scale_memory_limit": "2G",
            "run_env_variables": [
                {"type": "literal", "name": "ENVIRONMENT", "value": args.environment},
                {"type": "literal", "name": "LOG_LEVEL", "value": "INFO" if args.environment == "production" else "DEBUG"},
                {"type": "literal", "name": "PORT", "value": "8000"}
            ]
        }
        
        result = deployer.update_app(PROJECT_ID, APP_NAME, app_config)
        
        # Step 3: Attendi ready
        print("\n[3/5] ⏳ Verifica Deployment")
        deployer.wait_for_ready(PROJECT_ID, APP_NAME)
        
        # Ottieni URL
        app_status = deployer.get_app_status(PROJECT_ID, APP_NAME)
        app_url = f"https://{app_status['endpoint']}"
        print(f"\n📍 App URL: {app_url}")
        
        # Step 4: Health Check
        print("\n[4/5] 🏥 Health Check")
        health_ok = health_check(app_url)
        
        if not health_ok:
            print("⚠️  Warning: Health check failed, ma deployment completato")
        
        # Step 5: Watson X Integration
        if not args.skip_watsonx and WATSONX_API_KEY and WATSONX_INSTANCE_URL:
            print("\n[5/5] 🤖 Integrazione Watson X Orchestrate")
            wxo = WatsonXIntegrator(WATSONX_INSTANCE_URL, WATSONX_API_KEY)
            
            skills = [
                {
                    "name": "transaction-analysis",
                    "display_name": "Analisi Transazioni",
                    "description": "Analizza pattern transazionali e rileva anomalie AML",
                    "endpoint": {
                        "url": f"{app_url}/api/v1/analyze/transaction",
                        "method": "POST"
                    }
                },
                {
                    "name": "risk-assessment",
                    "display_name": "Valutazione Rischio",
                    "description": "Calcola risk score per account",
                    "endpoint": {
                        "url": f"{app_url}/api/v1/assess/risk",
                        "method": "POST"
                    }
                },
                {
                    "name": "fraud-detection",
                    "display_name": "Rilevamento Frodi",
                    "description": "Rileva attività fraudolente",
                    "endpoint": {
                        "url": f"{app_url}/api/v1/detect/fraud",
                        "method": "POST"
                    }
                },
                {
                    "name": "recommendation",
                    "display_name": "Raccomandazioni",
                    "description": "Genera azioni raccomandate",
                    "endpoint": {
                        "url": f"{app_url}/api/v1/recommend/actions",
                        "method": "POST"
                    }
                }
            ]
            
            for skill in skills:
                wxo.register_skill(skill)
        else:
            print("\n[5/5] ⏭️  Skipping Watson X integration")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ Deployment completato con successo!")
        print("=" * 70)
        print(f"\n📍 App URL: {app_url}")
        print(f"📚 API Docs: {app_url}/docs")
        print(f"🏥 Health: {app_url}/health")
        print(f"\n🔗 Endpoints:")
        print(f"   • Transaction Analysis: {app_url}/api/v1/analyze/transaction")
        print(f"   • Risk Assessment: {app_url}/api/v1/assess/risk")
        print(f"   • Fraud Detection: {app_url}/api/v1/detect/fraud")
        print(f"   • Recommendations: {app_url}/api/v1/recommend/actions")
        
        # Save deployment info
        deployment_info = {
            "timestamp": datetime.now().isoformat(),
            "environment": args.environment,
            "image_tag": args.image_tag,
            "app_url": app_url,
            "project_id": PROJECT_ID,
            "app_name": APP_NAME,
            "region": REGION
        }
        
        with open("deployment-info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n💾 Deployment info salvato in: deployment-info.json")
        
    except Exception as e:
        print(f"\n❌ Errore durante deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
