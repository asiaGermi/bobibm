# PowerShell script to add and activate a watsonx Orchestrate SaaS environment
# Usage: .\setup-wxo-env.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "watsonx Orchestrate Environment Setup" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Prompt for environment name
$envName = Read-Host "Enter environment name (e.g., 'production', 'dev')"
if ([string]::IsNullOrWhiteSpace($envName)) {
    Write-Host "Error: Environment name cannot be empty" -ForegroundColor Red
    exit 1
}

# Prompt for service instance URL
$serviceUrl = Read-Host "Enter service instance URL"
if ([string]::IsNullOrWhiteSpace($serviceUrl)) {
    Write-Host "Error: Service URL cannot be empty" -ForegroundColor Red
    exit 1
}

# Prompt for API key (secure)
$apiKeySecure = Read-Host "Enter API key" -AsSecureString
$apiKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKeySecure))
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "Error: API key cannot be empty" -ForegroundColor Red
    exit 1
}

# Detect environment type from URL
$envType = ""
if ($serviceUrl -like "*cloud.ibm.com*") {
    $envType = "ibm_iam"
    Write-Host "Detected IBM Cloud environment" -ForegroundColor Yellow
} elseif ($serviceUrl -like "*aws*" -or $serviceUrl -like "*saas*") {
    $envType = "mcsp"
    Write-Host "Detected AWS/MCSP environment" -ForegroundColor Yellow
} else {
    Write-Host "Could not auto-detect environment type" -ForegroundColor Yellow
    Write-Host "Please select environment type:"
    Write-Host "1) IBM Cloud (ibm_iam)"
    Write-Host "2) AWS/SaaS (mcsp)"
    Write-Host "3) On-premises (cpd)"
    $typeChoice = Read-Host "Enter choice (1-3)"
    switch ($typeChoice) {
        "1" { $envType = "ibm_iam" }
        "2" { $envType = "mcsp" }
        "3" { $envType = "cpd" }
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "Adding environment '$envName'..." -ForegroundColor Blue

# Add the environment
try {
    if ($envType) {
        & orchestrate env add -n $envName -u $serviceUrl --type $envType
    } else {
        & orchestrate env add -n $envName -u $serviceUrl
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to add environment"
    }
    Write-Host "✓ Environment added successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to add environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Activating environment '$envName'..." -ForegroundColor Blue

# Activate the environment with API key
try {
    & orchestrate env activate $envName --api-key $apiKey
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate environment"
    }
} catch {
    Write-Host "Failed to activate environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Environment '$envName' is now active and ready to use." -ForegroundColor White
Write-Host ""
Write-Host "Note: " -ForegroundColor Yellow -NoNewline
Write-Host "Authentication expires every 2 hours."
Write-Host "To re-activate, run: " -NoNewline
Write-Host "orchestrate env activate $envName" -ForegroundColor Blue
Write-Host ""
Write-Host "Next steps:"
Write-Host "  • List agents: " -NoNewline
Write-Host "orchestrate agents list" -ForegroundColor Blue
Write-Host "  • List tools: " -NoNewline
Write-Host "orchestrate tools list" -ForegroundColor Blue
Write-Host "  • Start chat: " -NoNewline
Write-Host "orchestrate chat start" -ForegroundColor Blue
Write-Host ""

# Clear sensitive data
$apiKey = $null
$apiKeySecure = $null

# Made with Bob
