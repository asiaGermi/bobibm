# Implementation Guide - Git Setup and Codebase Structure

## Overview
This guide provides step-by-step instructions for setting up the git repository inside the `20-codebase/` directory and creating the complete codebase structure for the BOB Challenge project.

## Important Note
**The git repository will be initialized inside `20-codebase/` directory, NOT in the project root.**

Project structure:
```
BOB_CHALLENGE_20260616/          # Project root (NO git here)
├── .bob/                        # Bob configuration
├── 00-input/                    # Input documents
├── 10-strategy/                 # Strategy documents
└── 20-codebase/                 # Git repository root (git init HERE)
    ├── .git/                    # Git repository
    ├── .gitignore              # Git ignore file
    └── [all code here]
```

## Prerequisites
- Git installed on the system
- Appropriate permissions to create files and directories

## Step 1: Create 20-codebase Directory

First, create the main codebase directory:

```bash
# Create the codebase directory
mkdir 20-codebase
cd 20-codebase
```

## Step 2: Create .gitignore File

Create a file named `.gitignore` inside `20-codebase/` with the following content:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# Virtual Environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# OS Files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Logs
*.log
logs/
*.log.*

# Environment Variables and Secrets
.env
.env.local
.env.*.local
*.env
secrets/
credentials/
*.key
*.pem
*.crt
*.p12

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/

# Jupyter Notebooks
.ipynb_checkpoints
*.ipynb

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.dockerignore

# Kubernetes
*.kubeconfig

# Temporary Files
*.tmp
*.temp
*.bak
*.swp
*~

# Build Artifacts
*.tar.gz
*.zip
*.war
*.jar

# Node (if using any JS tools)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IBM Cloud
.bluemix/
manifest.yml.bak

# Redis
dump.rdb

# Terraform (if used for infrastructure)
.terraform/
*.tfstate
*.tfstate.backup

# Local development
local/
scratch/
```

## Step 2: Initialize Git Repository

Execute the following commands in the project root:

```bash
# Navigate to project root
cd c:/Users/mattia.conti/Projects/BOB_CHALLENGE_20260616

# Initialize git repository
git init

# Configure git user (if not already configured globally)
git config user.name "Mattia Conti"
git config user.email "mattia.conti@example.com"

# Verify git initialization
git status
```

## Step 3: Create 20-codebase Directory Structure

Create the following directory structure:

```
20-codebase/
├── agents/
│   ├── transaction-analysis/
│   │   ├── src/
│   │   ├── tests/
│   │   └── README.md
│   ├── risk-assessment/
│   │   ├── src/
│   │   ├── tests/
│   │   └── README.md
│   └── recommendation/
│       ├── src/
│       ├── tests/
│       └── README.md
├── api/
│   ├── src/
│   ├── tests/
│   └── README.md
├── orchestration/
│   ├── workflows/
│   ├── configs/
│   └── README.md
├── data/
│   ├── ingestion/
│   ├── validation/
│   ├── transformation/
│   └── README.md
├── tests/
│   ├── integration/
│   ├── e2e/
│   ├── load/
│   └── README.md
├── deployment/
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── configmaps/
│   │   └── secrets/
│   ├── docker-compose/
│   └── README.md
├── scripts/
│   └── README.md
└── README.md
```

### Commands to Create Structure

```bash
# Create main codebase directory
mkdir 20-codebase

# Create agent directories
mkdir -p 20-codebase/agents/transaction-analysis/src
mkdir -p 20-codebase/agents/transaction-analysis/tests
mkdir -p 20-codebase/agents/risk-assessment/src
mkdir -p 20-codebase/agents/risk-assessment/tests
mkdir -p 20-codebase/agents/recommendation/src
mkdir -p 20-codebase/agents/recommendation/tests

# Create API directory
mkdir -p 20-codebase/api/src
mkdir -p 20-codebase/api/tests

# Create orchestration directory
mkdir -p 20-codebase/orchestration/workflows
mkdir -p 20-codebase/orchestration/configs

# Create data directory
mkdir -p 20-codebase/data/ingestion
mkdir -p 20-codebase/data/validation
mkdir -p 20-codebase/data/transformation

# Create tests directory
mkdir -p 20-codebase/tests/integration
mkdir -p 20-codebase/tests/e2e
mkdir -p 20-codebase/tests/load

# Create deployment directory
mkdir -p 20-codebase/deployment/kubernetes/deployments
mkdir -p 20-codebase/deployment/kubernetes/services
mkdir -p 20-codebase/deployment/kubernetes/configmaps
mkdir -p 20-codebase/deployment/kubernetes/secrets
mkdir -p 20-codebase/deployment/docker-compose

# Create scripts directory
mkdir -p 20-codebase/scripts
```

## Step 4: Create README Files

Create placeholder README.md files in each major directory to document their purpose.

### 20-codebase/README.md
```markdown
# Codebase - IBM Cloud Agentic Application

This directory contains all implementation code for the containerized agentic application.

## Structure

- `agents/` - Specialized agent implementations
- `api/` - REST API gateway
- `orchestration/` - watsonx Orchestrate workflows
- `data/` - Data layer components
- `tests/` - Test suites
- `deployment/` - Deployment configurations
- `scripts/` - Utility scripts

## Getting Started

See individual component READMEs for specific setup instructions.
```

### 20-codebase/agents/README.md
```markdown
# Agents

This directory contains the three specialized agents:

1. **Transaction Analysis Agent** - Analyzes financial transactions
2. **Risk Assessment Agent** - Evaluates transaction risks
3. **Recommendation Agent** - Generates actionable recommendations

Each agent is containerized and exposes a REST API.
```

### 20-codebase/api/README.md
```markdown
# API Gateway

REST API layer that exposes agent functionality to external systems.

## Endpoints

- `/api/v1/analyze/transaction` - Transaction analysis
- `/api/v1/assess/risk` - Risk assessment
- `/api/v1/recommend/actions` - Recommendations
- `/api/v1/batch/process` - Batch processing
```

### 20-codebase/orchestration/README.md
```markdown
# Orchestration

watsonx Orchestrate workflow configurations and agent skill definitions.

## Components

- `workflows/` - Workflow definitions
- `configs/` - Configuration files
```

### 20-codebase/data/README.md
```markdown
# Data Layer

Data ingestion, validation, and transformation components for IBM Synthetic Data Sets.

## Components

- `ingestion/` - Data ingestion services
- `validation/` - Data quality checks
- `transformation/` - Data transformation pipelines
```

### 20-codebase/tests/README.md
```markdown
# Tests

Comprehensive test suites for the application.

## Test Types

- `integration/` - Integration tests
- `e2e/` - End-to-end tests
- `load/` - Performance and load tests
```

### 20-codebase/deployment/README.md
```markdown
# Deployment

Deployment configurations for IBM Cloud Kubernetes Service.

## Components

- `kubernetes/` - Kubernetes manifests
- `docker-compose/` - Local development setup
```

### 20-codebase/scripts/README.md
```markdown
# Scripts

Utility scripts for setup, deployment, and testing.
```

## Step 5: Initial Git Commit

After creating all files and directories:

```bash
# Add all files to staging
git add .

# Create initial commit
git commit -m "chore(structure): initialize project with git and codebase structure

- Add .gitignore for Python, Docker, and IDE files
- Create 20-codebase directory structure
- Add README files for documentation
- Include strategy and planning documents"

# Verify commit
git log --oneline
```

## Step 6: Commit Workflow for Future Changes

For each change, follow this workflow:

```bash
# Check current status
git status

# Review changes
git diff

# Add specific files or all changes
git add <file>
# or
git add .

# Commit with descriptive message
git commit -m "type(scope): description"

# View commit history
git log --oneline --graph
```

### Commit Message Examples

```bash
# Feature additions
git commit -m "feat(agents): implement transaction analysis agent"
git commit -m "feat(api): add authentication middleware"

# Bug fixes
git commit -m "fix(agents): correct risk calculation formula"

# Documentation
git commit -m "docs(api): update endpoint documentation"

# Refactoring
git commit -m "refactor(data): optimize data transformation pipeline"

# Tests
git commit -m "test(agents): add unit tests for recommendation agent"

# Chores
git commit -m "chore(deps): update Python dependencies"
```

## Step 7: Verification Checklist

After completing the setup, verify:

- [ ] `.gitignore` file exists in project root
- [ ] Git repository is initialized (`.git/` directory exists)
- [ ] `20-codebase/` directory structure is created
- [ ] All README.md files are in place
- [ ] Initial commit is created
- [ ] `git status` shows clean working directory
- [ ] `git log` shows initial commit

## Next Steps

1. Switch to Code mode to implement the actual setup
2. Begin implementing agents in `20-codebase/agents/`
3. Set up CI/CD pipeline for automated testing
4. Configure IBM Cloud services
5. Implement watsonx Orchestrate workflows

## Automation Strategy

### Manual Commits (Current)
- Developer creates commits after each logical change
- Use descriptive commit messages following conventions
- Review changes before committing

### Future Automation
When ready to automate commits:

1. **Git Hooks**: Pre-commit hooks for linting and validation
2. **CI/CD Pipeline**: Automated builds and deployments
3. **Monitoring**: Track commit frequency and patterns

## Troubleshooting

### Issue: Git not initialized
```bash
# Check if .git directory exists
ls -la | grep .git

# If not, initialize
git init
```

### Issue: Permission denied
```bash
# Check directory permissions
ls -la

# Fix permissions if needed (Unix/Linux)
chmod -R u+w .
```

### Issue: Commit failed
```bash
# Check git configuration
git config --list

# Set user if needed
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## References

- [Git Workflow Strategy](./git-workflow.md)
- [Project Strategy](./strategy.md)
- [Todo List](./todo-list.md)
- [Mandate](../00-input/mandate/mandate.md)