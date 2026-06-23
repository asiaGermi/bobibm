# Repository Reorganization Plan

## 🎯 Obiettivo
Riorganizzare il repository per una struttura più pulita e professionale.

## 📁 Nuova Struttura

```
bobibm-1/
├── README.md                          # Main README (già aggiornato)
├── requirements.txt                   # Dependencies
├── run_api.py                        # API entry point
├── Dockerfile                        # Container build
├── docker-compose.yml                # Local development
├── openapi_spec.json                 # API specification
├── workspace_config.yaml             # watsonx config
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
│
├── deployment/                       # 🆕 Deployment scripts & configs
│   ├── README.md                     # Deployment overview
│   ├── deploy_to_wxo.py             # watsonx Orchestrate deploy
│   ├── deploy.ps1                   # PowerShell deploy script
│   ├── setup-wxo-env.ps1            # Setup script Windows
│   ├── setup-wxo-env.sh             # Setup script Linux/Mac
│   └── docker/                      # Docker-related files
│       ├── Dockerfile               # (link or move)
│       └── docker-compose.yml       # (link or move)
│
├── docs/                            # Documentation
│   ├── guides/                      # 🆕 User guides
│   │   ├── DEPLOYMENT_GUIDE.md     # From root
│   │   ├── DOCKER.md               # From root
│   │   ├── GUIDA_DEPLOY_PRATICA.md # From root
│   │   ├── README-setup-scripts.md # From root
│   │   └── README-WXO-DEPLOYMENT.md # From root
│   │
│   ├── analysis/                    # 🆕 Analysis & strategy docs
│   │   ├── COMPARISON_ANALYSIS.md  # From root
│   │   ├── STRATEGIC_RECOMMENDATION.md # From root
│   │   ├── TODO.md                 # From root
│   │   └── gap-analysis/           # Already exists
│   │
│   ├── demo/                        # Demo materials (already exists)
│   │   ├── ARCHITECTURE_SLIDES.md
│   │   └── DEMO_PREPARATION_SUMMARY.md
│   │
│   ├── deployment/                  # Deployment docs (already exists)
│   │   ├── QUICK-START.md
│   │   └── api-deployment-strategy.md
│   │
│   ├── reference-codebase/          # Reference code (already exists)
│   ├── remediations/                # Remediation docs (already exists)
│   ├── strategy/                    # Strategy docs (already exists)
│   ├── mandate.md                   # Project mandate (already exists)
│   └── spec-driven-development.md   # Spec-driven dev (already exists)
│
├── scripts/                         # Utility scripts
│   ├── demo/                        # 🆕 Demo scripts
│   │   ├── README.md               # From scripts/DEMO_README.md
│   │   ├── demo.py                 # From scripts/
│   │   ├── demo.ps1                # From scripts/
│   │   └── demo_auto.py            # From scripts/
│   │
│   ├── deploy_unified.py           # Already exists
│   └── README.md                   # Already exists
│
├── src/                            # Source code (already organized)
│   ├── agents/
│   ├── api/
│   └── data/
│
├── agents/                         # watsonx Orchestrate agents (already exists)
├── data/                          # Data files (already exists)
├── connections/                   # Connections (already exists)
├── knowledge-bases/              # Knowledge bases (already exists)
├── models/                       # Models (already exists)
├── toolkits/                     # Toolkits (already exists)
└── tools/                        # Tools (already exists)
```

## 🔄 Operazioni da Eseguire

### 1. Creare Nuove Directory
- [x] `deployment/`
- [x] `docs/guides/`
- [x] `docs/analysis/`
- [x] `scripts/demo/`

### 2. Spostare File - Deployment
- [ ] `deploy_to_wxo.py` → `deployment/`
- [ ] `deploy.ps1` → `deployment/`
- [ ] `setup-wxo-env.ps1` → `deployment/`
- [ ] `setup-wxo-env.sh` → `deployment/`

### 3. Spostare File - Docs/Guides
- [ ] `DEPLOYMENT_GUIDE.md` → `docs/guides/`
- [ ] `DOCKER.md` → `docs/guides/`
- [ ] `GUIDA_DEPLOY_PRATICA.md` → `docs/guides/`
- [ ] `README-setup-scripts.md` → `docs/guides/`
- [ ] `README-WXO-DEPLOYMENT.md` → `docs/guides/`

### 4. Spostare File - Docs/Analysis
- [ ] `COMPARISON_ANALYSIS.md` → `docs/analysis/`
- [ ] `STRATEGIC_RECOMMENDATION.md` → `docs/analysis/`
- [ ] `TODO.md` → `docs/analysis/`

### 5. Spostare File - Scripts/Demo
- [ ] `scripts/demo.py` → `scripts/demo/`
- [ ] `scripts/demo.ps1` → `scripts/demo/`
- [ ] `scripts/demo_auto.py` → `scripts/demo/`
- [ ] `scripts/DEMO_README.md` → `scripts/demo/README.md`

### 6. Creare README per Nuove Directory
- [ ] `deployment/README.md`
- [ ] `docs/guides/README.md`
- [ ] `docs/analysis/README.md`

### 7. Aggiornare Link nel README Principale
- [ ] Aggiornare tutti i path relativi

## 📝 Note
- Mantenere `.env` nella root (non committare)
- Mantenere file di configurazione nella root (Dockerfile, docker-compose.yml, etc.)
- Non spostare directory già ben organizzate (src/, agents/, data/)