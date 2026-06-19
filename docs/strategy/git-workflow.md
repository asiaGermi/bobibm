# Git Workflow Strategy

## Overview
This document outlines the git workflow strategy for the BOB Challenge project, including repository structure, commit conventions, and automation guidelines.

## Important: Repository Location

**The git repository is initialized inside `20-codebase/` directory, NOT in the project root.**

## Repository Structure

```
BOB_CHALLENGE_20260616/          # Project root (NO git repository here)
├── .bob/                        # Bob configuration
├── 00-input/                    # Input documents and requirements
│   └── mandate/
├── 10-strategy/                 # Strategy and planning documents
├── 20-codebase/                 # Git repository root (git init HERE)
│   ├── .git/                    # Git repository
│   ├── .gitignore              # Git ignore patterns
│   ├── README.md               # Codebase documentation
│   ├── agents/                 # Agent implementations
│   │   ├── transaction-analysis/
│   │   ├── risk-assessment/
│   │   └── recommendation/
│   ├── api/                    # API gateway
│   ├── orchestration/          # Workflow orchestration
│   ├── data/                   # Data layer
│   ├── tests/                  # Test suites
│   ├── deployment/             # Kubernetes manifests, Dockerfiles
│   └── scripts/                # Utility scripts
└── bob-challenge-scenario-1/   # Existing scenario files
```

## Git Initialization

### Step 1: Create and Navigate to Codebase Directory
```bash
# Create the codebase directory (if it doesn't exist)
mkdir 20-codebase

# Navigate to codebase directory
cd 20-codebase
```

### Step 2: Initialize Repository
```bash
# Initialize git inside 20-codebase directory
git init

# Configure user (if not already configured)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Create .gitignore
The `.gitignore` file (inside `20-codebase/`) should exclude:
- Python cache files (`__pycache__/`, `*.pyc`, `*.pyo`)
- Virtual environments (`venv/`, `env/`, `.venv/`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Build artifacts (`dist/`, `build/`, `*.egg-info/`)
- Secrets and credentials (`*.env`, `secrets/`, `credentials/`)
- Logs (`*.log`, `logs/`)
- Temporary files (`*.tmp`, `*.temp`)

### Step 4: Initial Commit
```bash
# Make sure you're in 20-codebase directory
cd 20-codebase

# Add all files
git add .

# Create initial commit
git commit -m "chore(structure): initialize codebase with directory structure"
```

## Commit Strategy

### Commit Frequency
- **After each significant change**: Create a commit after completing a logical unit of work
- **Before switching tasks**: Commit current work before moving to a different task
- **After file creation**: Commit new files immediately after creation
- **After file modification**: Commit changes after completing modifications

### Commit Message Convention
Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `build`: Build system changes
- `ci`: CI/CD changes

**Examples:**
```bash
git commit -m "feat(agents): implement transaction analysis agent"
git commit -m "docs(strategy): update deployment timeline"
git commit -m "chore(structure): create 20-codebase directory"
git commit -m "fix(api): correct authentication middleware"
```

## Automated Commit Workflow

### Manual Commits (Current Approach)
Since we don't have a remote repository yet, all commits will be local.

**IMPORTANT: All git commands must be run from inside `20-codebase/` directory**

```bash
# Navigate to codebase directory
cd 20-codebase

# After making changes
git add <files>
git commit -m "type(scope): description"
```

### Future Automation Options
When ready to automate:

1. **Git Hooks**: Use pre-commit hooks for validation
2. **CI/CD Integration**: Automate commits through pipeline
3. **Watchers**: File system watchers for auto-commits (use with caution)

## Branch Strategy

### Main Branch
- `main`: Production-ready code
- All development happens on `main` for now (single developer)

### Future Branch Strategy (when team grows)
- `develop`: Integration branch
- `feature/*`: Feature branches
- `hotfix/*`: Emergency fixes
- `release/*`: Release preparation

## Codebase Organization

**All code resides inside `20-codebase/` which is the git repository root**

### Directory Structure
```
20-codebase/                     # Git repository root
├── .git/                        # Git repository
├── .gitignore                   # Git ignore file
├── README.md                    # Main documentation
├── agents/
│   ├── transaction-analysis/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── risk-assessment/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── recommendation/
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
├── api/
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── orchestration/
│   ├── workflows/
│   └── configs/
├── data/
│   ├── ingestion/
│   ├── validation/
│   └── transformation/
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── load/
├── deployment/
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── configmaps/
│   │   └── secrets/
│   └── docker-compose/
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── test.sh
└── README.md
```

## Commit Checklist

Before each commit, ensure:
- [ ] Code is tested and working
- [ ] No sensitive data (credentials, API keys) is included
- [ ] Documentation is updated if needed
- [ ] Commit message follows convention
- [ ] Files are properly organized in correct directories

## Git Commands Reference

**IMPORTANT: All commands must be run from inside `20-codebase/` directory**

### Basic Operations
```bash
# Navigate to codebase directory
cd 20-codebase

# Check status
git status

# View changes
git diff

# Add files
git add <file>
git add .

# Commit
git commit -m "message"

# View history
git log --oneline
git log --graph --oneline --all

# Undo changes (before commit)
git checkout -- <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View specific commit
git show <commit-hash>
```

### Advanced Operations
```bash
# Interactive staging
git add -p

# Amend last commit
git commit --amend

# Stash changes
git stash
git stash pop

# Cherry-pick commit
git cherry-pick <commit-hash>

# Rebase (use with caution)
git rebase -i HEAD~n
```

## Best Practices

1. **Commit Often**: Small, focused commits are better than large ones
2. **Write Clear Messages**: Describe what and why, not how
3. **Review Before Commit**: Use `git diff` to review changes
4. **Keep Commits Atomic**: Each commit should represent one logical change
5. **Don't Commit Generated Files**: Use `.gitignore` appropriately
6. **Test Before Commit**: Ensure code works before committing

## Integration with Bob

When Bob makes changes to code in `20-codebase/`:
1. Bob will create/modify files inside `20-codebase/` as needed
2. After successful file operations, navigate to `20-codebase/` and create a commit
3. Use descriptive commit messages based on the task
4. Keep commits focused on specific changes

**Note**: Changes to files outside `20-codebase/` (like strategy documents) are NOT tracked by this git repository

## Remote Repository (Future)

When ready to add a remote repository:

```bash
# Navigate to codebase directory
cd 20-codebase

# Add remote
git remote add origin <repository-url>

# Push to remote
git push -u origin main

# Pull from remote
git pull origin main

# Fetch updates
git fetch origin
```

## Troubleshooting

### Common Issues

**Issue**: Accidentally committed sensitive data
```bash
# Remove from last commit
git reset --soft HEAD~1
git reset HEAD <file>
# Edit .gitignore, then commit again
```

**Issue**: Need to change last commit message
```bash
git commit --amend -m "new message"
```

**Issue**: Committed to wrong branch
```bash
# Create new branch from current commit
git branch <new-branch>
# Reset current branch
git reset --hard HEAD~1
# Switch to new branch
git checkout <new-branch>
```

## Next Steps

1. ✅ Create this documentation
2. ⏳ Create `20-codebase/` directory
3. ⏳ Initialize git repository inside `20-codebase/`
4. ⏳ Create `.gitignore` file inside `20-codebase/`
5. ⏳ Create complete directory structure
6. ⏳ Make initial commit
7. ⏳ Document commit workflow in codebase README

## Key Reminders

- **Git location**: `20-codebase/.git/`
- **Working directory**: Always `cd 20-codebase` before git commands
- **Scope**: Only code inside `20-codebase/` is version controlled
- **Project root**: Strategy documents and other folders are NOT in git

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Semantic Versioning](https://semver.org/)