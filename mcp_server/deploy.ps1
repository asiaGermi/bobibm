# PowerShell deployment script for MCP Server to IBM Cloud Code Engine

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "MCP Server Deployment to IBM Cloud" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_NAME = "financial-risk"
$APP_NAME = "financial-risk-mcp"
$REGION = "eu-de"
$REGISTRY = "us.icr.io"
$NAMESPACE = "financial-risk"
$IMAGE_NAME = "mcp-server"
$IMAGE_TAG = "latest"
$FULL_IMAGE = "${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"

# Step 1: Login to IBM Cloud
Write-Host "Step 1: Logging in to IBM Cloud..." -ForegroundColor Yellow
if (-not $env:IBM_CLOUD_API_KEY) {
    Write-Host "Error: IBM_CLOUD_API_KEY environment variable not set" -ForegroundColor Red
    exit 1
}
ibmcloud login --apikey $env:IBM_CLOUD_API_KEY -r $REGION

# Step 2: Target Code Engine project
Write-Host ""
Write-Host "Step 2: Targeting Code Engine project..." -ForegroundColor Yellow
ibmcloud ce project select --name $PROJECT_NAME

# Step 3: Login to Container Registry
Write-Host ""
Write-Host "Step 3: Logging in to IBM Container Registry..." -ForegroundColor Yellow
ibmcloud cr login

# Step 4: Build Docker image
Write-Host ""
Write-Host "Step 4: Building Docker image..." -ForegroundColor Yellow
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f mcp_server/Dockerfile .

# Step 5: Tag image
Write-Host ""
Write-Host "Step 5: Tagging image..." -ForegroundColor Yellow
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" $FULL_IMAGE

# Step 6: Push to registry
Write-Host ""
Write-Host "Step 6: Pushing image to registry..." -ForegroundColor Yellow
docker push $FULL_IMAGE

# Step 7: Deploy to Code Engine
Write-Host ""
Write-Host "Step 7: Deploying to Code Engine..." -ForegroundColor Yellow

# Check if app exists
$appExists = $false
try {
    ibmcloud ce app get --name $APP_NAME 2>$null
    $appExists = $true
} catch {
    $appExists = $false
}

if ($appExists) {
    Write-Host "Updating existing application..." -ForegroundColor Green
    ibmcloud ce app update `
        --name $APP_NAME `
        --image $FULL_IMAGE `
        --port 8080 `
        --min-scale 1 `
        --max-scale 5 `
        --cpu 0.5 `
        --memory 1G `
        --wait
} else {
    Write-Host "Creating new application..." -ForegroundColor Green
    ibmcloud ce app create `
        --name $APP_NAME `
        --image $FULL_IMAGE `
        --port 8080 `
        --min-scale 1 `
        --max-scale 5 `
        --cpu 0.5 `
        --memory 1G `
        --wait
}

# Step 8: Get application URL
Write-Host ""
Write-Host "Step 8: Getting application URL..." -ForegroundColor Yellow
$appInfo = ibmcloud ce app get --name $APP_NAME --output json | ConvertFrom-Json
$APP_URL = $appInfo.status.url

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "MCP Server URL: $APP_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Register MCP server in watsonx Orchestrate:"
Write-Host "   orchestrate mcp-servers add \"
Write-Host "     --name $APP_NAME \"
Write-Host "     --url $APP_URL \"
Write-Host "     --transport sse"
Write-Host ""
Write-Host "2. Test the tools:"
Write-Host "   orchestrate tools list"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

# Made with Bob
