# Deploy su IBM Code Engine — Financial Risk API
# Uso: .\scripts\deploy_code_engine.ps1 ["messaggio commit opzionale"]

param(
    [string]$CommitMsg = "fix: deploy aggiornamento"
)

$BUILD_NAME = "financial-risk-api-build-ktk8x"
$APP_NAME   = "financial-risk-api"

Write-Host "=== 1. Git push ===" -ForegroundColor Cyan
git add src/ static/ docs/
$hasChanges = (git status --porcelain) -ne ""
if ($hasChanges) {
    git commit -m "$CommitMsg`n`nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
} else {
    Write-Host "(nessuna modifica da committare)"
}
git push origin main

Write-Host ""
Write-Host "=== 2. Build Code Engine ===" -ForegroundColor Cyan
$buildOutput = ibmcloud ce buildrun submit --build $BUILD_NAME 2>&1
$buildOutput | Write-Host

# Estrai nome buildrun dall'output
$BUILD_RUN = ($buildOutput | Select-String "esecuzione della build '([\w\-]+)'").Matches.Groups[1].Value
if (-not $BUILD_RUN) {
    Write-Host "Impossibile ricavare il nome del buildrun. Controlla con: ibmcloud ce buildrun list" -ForegroundColor Red
    exit 1
}
Write-Host "Build avviata: $BUILD_RUN" -ForegroundColor Green

Write-Host ""
Write-Host "=== 3. Attesa completamento build ===" -ForegroundColor Cyan
do {
    Start-Sleep -Seconds 15
    $status = (ibmcloud ce buildrun get -n $BUILD_RUN 2>&1 | Select-String "Stato:").ToString().Trim()
    Write-Host "  $status"
} until ((ibmcloud ce buildrun get -n $BUILD_RUN 2>&1) -match "succeeded|failed")

if ((ibmcloud ce buildrun get -n $BUILD_RUN 2>&1) -match "failed") {
    Write-Host "BUILD FALLITA. Controlla i log:" -ForegroundColor Red
    ibmcloud ce buildrun logs -n $BUILD_RUN
    exit 1
}

Write-Host ""
Write-Host "=== 4. App update ===" -ForegroundColor Cyan
ibmcloud ce app update -n $APP_NAME

Write-Host ""
Write-Host "=== FATTO ===" -ForegroundColor Green
Write-Host "URL: https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
Write-Host "Aspetta 30s poi Ctrl+F5 sul dashboard."
