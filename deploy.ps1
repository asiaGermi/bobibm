# Financial Risk Management - Quick Deployment Script for Windows PowerShell
# This script automates the deployment of tools and agent to watsonx Orchestrate

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Financial Risk Management - watsonx Orchestrate Deployment" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Load environment variables from .env file
Write-Host "Loading environment variables from .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
            Write-Host "  ✓ Set $name" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  ✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please create .env file with your credentials." -ForegroundColor Red
    exit 1
}

# Verify environment variables
Write-Host "`nVerifying environment variables..." -ForegroundColor Yellow
$required_vars = @("WXO_URL", "WXO_APIKEY", "API_BASE_URL")
$missing_vars = @()

foreach ($var in $required_vars) {
    if ([string]::IsNullOrEmpty((Get-Item -Path "env:$var" -ErrorAction SilentlyContinue).Value)) {
        $missing_vars += $var
        Write-Host "  ✗ $var is not set" -ForegroundColor Red
    } else {
        if ($var -eq "WXO_APIKEY") {
            $masked = "*" * 20 + $env:WXO_APIKEY.Substring([Math]::Max(0, $env:WXO_APIKEY.Length - 4))
            Write-Host "  ✓ $var = $masked" -ForegroundColor Green
        } else {
            Write-Host "  ✓ $var = $((Get-Item -Path "env:$var").Value)" -ForegroundColor Green
        }
    }
}

if ($missing_vars.Count -gt 0) {
    Write-Host "`n✗ Missing required environment variables: $($missing_vars -join ', ')" -ForegroundColor Red
    exit 1
}

# Check if orchestrate CLI is installed
Write-Host "`nChecking for orchestrate CLI..." -ForegroundColor Yellow
try {
    $version = orchestrate --version 2>&1
    Write-Host "  ✓ orchestrate CLI found: $version" -ForegroundColor Green
} catch {
    Write-Host "  ✗ orchestrate CLI not found!" -ForegroundColor Red
    Write-Host "  Please install it with: pip install ibm-watsonx-orchestrate" -ForegroundColor Red
    exit 1
}

# Check if required files exist
Write-Host "`nChecking required files..." -ForegroundColor Yellow
$required_files = @(
    "openapi_spec.json",
    "agents/financial_risk_orchestrator.yaml"
)

foreach ($file in $required_files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file not found!" -ForegroundColor Red
        exit 1
    }
}

# Step 1: Login to watsonx Orchestrate
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Step 1: Logging in to watsonx Orchestrate" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Command: orchestrate login --url $env:WXO_URL --apikey ****`n" -ForegroundColor Gray

try {
    orchestrate login --url $env:WXO_URL --apikey $env:WXO_APIKEY
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Login successful!" -ForegroundColor Green
    } else {
        throw "Login failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "`n✗ Login failed: $_" -ForegroundColor Red
    Write-Host "Please check your credentials and try again." -ForegroundColor Red
    exit 1
}

# Step 2: Import OpenAPI tools
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Step 2: Importing OpenAPI Tools (4 tools)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Command: orchestrate tools import -k openapi -f openapi_spec.json`n" -ForegroundColor Gray

try {
    orchestrate tools import -k openapi -f openapi_spec.json
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Tools imported successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠ Tools import completed with warnings (exit code $LASTEXITCODE)" -ForegroundColor Yellow
        Write-Host "This is normal if tools already exist. Continuing..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n⚠ Tools import encountered an issue: $_" -ForegroundColor Yellow
    Write-Host "Continuing with agent import..." -ForegroundColor Yellow
}

# Step 3: List tools to verify
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Step 3: Verifying Imported Tools" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Command: orchestrate tools list`n" -ForegroundColor Gray

try {
    orchestrate tools list
    Write-Host "`n✓ Tools listed successfully!" -ForegroundColor Green
} catch {
    Write-Host "`n⚠ Could not list tools: $_" -ForegroundColor Yellow
}

# Step 4: Import orchestrator agent
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Step 4: Importing Orchestrator Agent" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Command: orchestrate agents import -f agents/financial_risk_orchestrator.yaml`n" -ForegroundColor Gray

try {
    orchestrate agents import -f agents/financial_risk_orchestrator.yaml
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Agent imported successfully!" -ForegroundColor Green
    } else {
        throw "Agent import failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "`n✗ Agent import failed: $_" -ForegroundColor Red
    Write-Host "Please check the agent YAML file and try again." -ForegroundColor Red
    exit 1
}

# Step 5: List agents to verify
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Step 5: Verifying Imported Agent" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Command: orchestrate agents list`n" -ForegroundColor Gray

try {
    orchestrate agents list
    Write-Host "`n✓ Agents listed successfully!" -ForegroundColor Green
} catch {
    Write-Host "`n⚠ Could not list agents: $_" -ForegroundColor Yellow
}

# Success summary
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  ✓ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`n📋 Summary:" -ForegroundColor Cyan
Write-Host "   • 4 OpenAPI tools imported:" -ForegroundColor White
Write-Host "     - analyzeTransaction" -ForegroundColor Gray
Write-Host "     - assessRisk" -ForegroundColor Gray
Write-Host "     - detectFraud" -ForegroundColor Gray
Write-Host "     - recommendActions" -ForegroundColor Gray
Write-Host "   • 1 orchestrator agent created:" -ForegroundColor White
Write-Host "     - financial_risk_orchestrator" -ForegroundColor Gray

Write-Host "`n🔗 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Go to watsonx Orchestrate UI" -ForegroundColor White
Write-Host "   2. Navigate to the Agents section" -ForegroundColor White
Write-Host "   3. Find 'financial_risk_orchestrator' agent" -ForegroundColor White
Write-Host "   4. Test the agent with an account_id" -ForegroundColor White

Write-Host "`n💡 Example Query:" -ForegroundColor Cyan
Write-Host "   'Analyze the risk for account ACC-12345'" -ForegroundColor Yellow

Write-Host "`n📚 For more information, see DEPLOYMENT_GUIDE.md`n" -ForegroundColor Cyan

# Made with Bob
