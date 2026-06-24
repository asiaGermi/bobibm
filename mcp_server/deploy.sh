#!/bin/bash
# Deploy script for MCP Server to IBM Cloud Code Engine

set -e

echo "=========================================="
echo "MCP Server Deployment to IBM Cloud"
echo "=========================================="
echo ""

# Configuration
PROJECT_NAME="financial-risk"
APP_NAME="financial-risk-mcp"
REGION="eu-de"
REGISTRY="us.icr.io"
NAMESPACE="financial-risk"
IMAGE_NAME="mcp-server"
IMAGE_TAG="latest"
FULL_IMAGE="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"

# Step 1: Login to IBM Cloud
echo "Step 1: Logging in to IBM Cloud..."
ibmcloud login --apikey "${IBM_CLOUD_API_KEY}" -r "${REGION}"

# Step 2: Target Code Engine project
echo ""
echo "Step 2: Targeting Code Engine project..."
ibmcloud ce project select --name "${PROJECT_NAME}"

# Step 3: Login to Container Registry
echo ""
echo "Step 3: Logging in to IBM Container Registry..."
ibmcloud cr login

# Step 4: Build Docker image
echo ""
echo "Step 4: Building Docker image..."
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f mcp_server/Dockerfile .

# Step 5: Tag image
echo ""
echo "Step 5: Tagging image..."
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE}"

# Step 6: Push to registry
echo ""
echo "Step 6: Pushing image to registry..."
docker push "${FULL_IMAGE}"

# Step 7: Deploy to Code Engine
echo ""
echo "Step 7: Deploying to Code Engine..."

# Check if app exists
if ibmcloud ce app get --name "${APP_NAME}" &>/dev/null; then
    echo "Updating existing application..."
    ibmcloud ce app update \
        --name "${APP_NAME}" \
        --image "${FULL_IMAGE}" \
        --port 8080 \
        --min-scale 1 \
        --max-scale 5 \
        --cpu 0.5 \
        --memory 1G \
        --wait
else
    echo "Creating new application..."
    ibmcloud ce app create \
        --name "${APP_NAME}" \
        --image "${FULL_IMAGE}" \
        --port 8080 \
        --min-scale 1 \
        --max-scale 5 \
        --cpu 0.5 \
        --memory 1G \
        --wait
fi

# Step 8: Get application URL
echo ""
echo "Step 8: Getting application URL..."
APP_URL=$(ibmcloud ce app get --name "${APP_NAME}" --output json | jq -r '.status.url')

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "MCP Server URL: ${APP_URL}"
echo ""
echo "Next steps:"
echo "1. Register MCP server in watsonx Orchestrate:"
echo "   orchestrate mcp-servers add \\"
echo "     --name ${APP_NAME} \\"
echo "     --url ${APP_URL} \\"
echo "     --transport sse"
echo ""
echo "2. Test the tools:"
echo "   orchestrate tools list"
echo ""
echo "=========================================="

# Made with Bob
