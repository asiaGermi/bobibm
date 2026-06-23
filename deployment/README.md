# Deployment Scripts

Scripts e configurazioni per il deployment del sistema su IBM Cloud e watsonx Orchestrate.

## 📁 Contenuto

### Script Principali

- **`deploy_to_wxo.py`** - Deploy tools e agent su watsonx Orchestrate
- **`deploy.ps1`** - Script PowerShell per deploy rapido
- **`setup-wxo-env.ps1`** - Setup environment Windows
- **`setup-wxo-env.sh`** - Setup environment Linux/Mac

## 🚀 Quick Start

### Deploy su watsonx Orchestrate

**PowerShell:**
```powershell
.\deployment\deploy.ps1
```

**Python:**
```bash
python deployment/deploy_to_wxo.py
```

### Setup Environment

**Windows:**
```powershell
.\deployment\setup-wxo-env.ps1
```

**Linux/Mac:**
```bash
chmod +x deployment/setup-wxo-env.sh
./deployment/setup-wxo-env.sh
```

## 📖 Guide Dettagliate

Per guide complete sul deployment, consulta:
- [`docs/guides/DEPLOYMENT_GUIDE.md`](../docs/guides/DEPLOYMENT_GUIDE.md)
- [`docs/guides/GUIDA_DEPLOY_PRATICA.md`](../docs/guides/GUIDA_DEPLOY_PRATICA.md)
- [`docs/deployment/QUICK-START.md`](../docs/deployment/QUICK-START.md)

## 🔧 Prerequisiti

- Python 3.11+
- IBM Cloud account
- watsonx Orchestrate instance
- Credenziali configurate in `.env`

## 📝 Configurazione

1. Copia `.env.example` in `.env`
2. Configura le credenziali:
   ```
   WXO_URL=https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/...
   WXO_APIKEY=your-api-key
   ```

## 🎯 Workflow

1. **Setup** - Configura environment
2. **Build** - Build Docker image (opzionale)
3. **Deploy API** - Deploy su IBM Cloud Code Engine
4. **Deploy Skills** - Deploy tools su watsonx Orchestrate
5. **Deploy Agent** - Deploy orchestrator agent
6. **Verify** - Test deployment

## 🔗 Link Utili

- [Main README](../README.md)
- [Deployment Guides](../docs/guides/)
- [API Documentation](../docs/deployment/)