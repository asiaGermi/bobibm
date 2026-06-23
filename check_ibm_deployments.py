"""
Script per verificare i modelli deployati in IBM Cloud e watsonx.ai
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Fix encoding per Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Carica le variabili d'ambiente
load_dotenv()

WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
WATSONX_URL = os.getenv('WATSONX_URL')
IBM_CLOUD_API_KEY = os.getenv('IBM_CLOUD_API_KEY')

def get_iam_token(api_key):
    """Ottieni un token IAM da IBM Cloud"""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Errore nell'ottenere il token IAM: {e}")
        return None

def check_watsonx_deployments():
    """Verifica i deployment in watsonx.ai"""
    print("\n" + "="*60)
    print("WATSONX.AI - Informazioni Progetto e Modelli")
    print("="*60)
    
    token = get_iam_token(WATSONX_API_KEY)
    if not token:
        print("❌ Impossibile autenticarsi con watsonx.ai")
        return
    
    # Informazioni dal .env
    print(f"\n📋 Configurazione corrente:")
    print(f"   Project ID: {WATSONX_PROJECT_ID}")
    print(f"   URL: {WATSONX_URL}")
    print(f"   Modello configurato: {os.getenv('MODEL_ID', 'Non specificato')}")
    
    # Prova a ottenere informazioni sul progetto
    project_url = f"{WATSONX_URL}/ml/v4/projects/{WATSONX_PROJECT_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
        "version": "2024-01-01"
    }
    
    try:
        response = requests.get(project_url, headers=headers, params=params)
        if response.status_code == 200:
            project_info = response.json()
            print(f"\n✅ Progetto trovato:")
            print(f"   Nome: {project_info.get('entity', {}).get('name', 'N/A')}")
            print(f"   Descrizione: {project_info.get('entity', {}).get('description', 'N/A')}")
        else:
            print(f"\n⚠️  Impossibile ottenere info progetto (Status: {response.status_code})")
    except Exception as e:
        print(f"\n⚠️  Errore nel recuperare info progetto: {e}")
    
    # Verifica deployment
    deployments_url = f"{WATSONX_URL}/ml/v4/deployments"
    params = {
        "version": "2024-01-01",
        "space_id": WATSONX_PROJECT_ID
    }
    
    try:
        response = requests.get(deployments_url, headers=headers, params=params)
        if response.status_code == 200:
            deployments = response.json()
            resources = deployments.get('resources', [])
            
            print(f"\n📦 Deployment trovati: {len(resources)}")
            
            if resources:
                for idx, deployment in enumerate(resources, 1):
                    print(f"\n   Deployment #{idx}:")
                    print(f"   - ID: {deployment.get('metadata', {}).get('id', 'N/A')}")
                    print(f"   - Nome: {deployment.get('entity', {}).get('name', 'N/A')}")
                    print(f"   - Stato: {deployment.get('entity', {}).get('status', {}).get('state', 'N/A')}")
                    print(f"   - Tipo: {deployment.get('entity', {}).get('asset', {}).get('asset_type', 'N/A')}")
            else:
                print("   ℹ️  Nessun deployment trovato in questo progetto")
        else:
            print(f"\n⚠️  Impossibile ottenere deployment (Status: {response.status_code})")
            print(f"   Risposta: {response.text[:200]}")
    except Exception as e:
        print(f"\n⚠️  Errore nel recuperare deployment: {e}")

def check_watson_services():
    """Verifica i servizi Watson disponibili"""
    print("\n" + "="*60)
    print("IBM CLOUD - Servizi Watson")
    print("="*60)
    
    token = get_iam_token(IBM_CLOUD_API_KEY)
    if not token:
        print("❌ Impossibile autenticarsi con IBM Cloud")
        return
    
    # Lista delle istanze di servizio
    url = "https://resource-controller.cloud.ibm.com/v2/resource_instances"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            instances = response.json()
            resources = instances.get('resources', [])
            
            # Filtra per servizi Watson/AI
            watson_services = [r for r in resources if 'watson' in r.get('name', '').lower() 
                             or 'machine-learning' in r.get('name', '').lower()
                             or 'watsonx' in r.get('name', '').lower()]
            
            print(f"\n🔍 Servizi Watson/AI trovati: {len(watson_services)}")
            
            if watson_services:
                for idx, service in enumerate(watson_services, 1):
                    print(f"\n   Servizio #{idx}:")
                    print(f"   - Nome: {service.get('name', 'N/A')}")
                    print(f"   - Tipo: {service.get('resource_id', 'N/A')}")
                    print(f"   - Stato: {service.get('state', 'N/A')}")
                    print(f"   - Regione: {service.get('region_id', 'N/A')}")
                    print(f"   - ID: {service.get('id', 'N/A')}")
            else:
                print("   ℹ️  Nessun servizio Watson trovato")
                print(f"   Totale servizi nel tuo account: {len(resources)}")
        else:
            print(f"\n⚠️  Impossibile ottenere servizi (Status: {response.status_code})")
    except Exception as e:
        print(f"\n⚠️  Errore nel recuperare servizi: {e}")

def main():
    print("\n🔍 Verifica Deployment IBM Cloud e watsonx.ai")
    print("="*60)
    
    if not WATSONX_API_KEY or not IBM_CLOUD_API_KEY:
        print("❌ Errore: API keys non trovate nel file .env")
        return
    
    check_watsonx_deployments()
    check_watson_services()
    
    print("\n" + "="*60)
    print("✅ Verifica completata")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

# Made with Bob
