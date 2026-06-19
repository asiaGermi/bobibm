#!/bin/bash
# Deploy AML Compliance Application to IBM Cloud Kubernetes Service
# Usage: ./deploy-to-ibm-cloud.sh [environment]
# Example: ./deploy-to-ibm-cloud.sh production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
CLUSTER_NAME="aml-compliance-cluster"
REGION="us-south"
RESOURCE_GROUP="aml-compliance-rg"
NAMESPACE="aml-compliance"
REGISTRY="icr.io"
REGISTRY_NAMESPACE="aml-namespace"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IBM Cloud Deployment Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}"

# Step 1: Login to IBM Cloud
echo -e "\n${YELLOW}[1/10] Logging in to IBM Cloud...${NC}"
ibmcloud login --apikey ${IBM_CLOUD_API_KEY} -r ${REGION} -g ${RESOURCE_GROUP}

# Step 2: Set kubectl context
echo -e "\n${YELLOW}[2/10] Setting kubectl context...${NC}"
ibmcloud ks cluster config --cluster ${CLUSTER_NAME}

# Step 3: Login to IBM Cloud Container Registry
echo -e "\n${YELLOW}[3/10] Logging in to IBM Cloud Container Registry...${NC}"
ibmcloud cr login

# Step 4: Create namespace if it doesn't exist
echo -e "\n${YELLOW}[4/10] Creating namespace...${NC}"
kubectl apply -f ../kubernetes/namespace.yaml

# Step 5: Create secrets
echo -e "\n${YELLOW}[5/10] Creating secrets...${NC}"
if [ ! -f "../kubernetes/secrets.yaml" ]; then
    echo -e "${RED}ERROR: secrets.yaml not found!${NC}"
    echo -e "${RED}Please create secrets.yaml from secrets.yaml.template${NC}"
    exit 1
fi
kubectl apply -f ../kubernetes/secrets.yaml

# Step 6: Create ConfigMaps
echo -e "\n${YELLOW}[6/10] Creating ConfigMaps...${NC}"
kubectl apply -f ../kubernetes/configmap.yaml

# Step 7: Create PersistentVolumeClaims
echo -e "\n${YELLOW}[7/10] Creating PersistentVolumeClaims...${NC}"
kubectl apply -f ../kubernetes/pvc.yaml

# Step 8: Build and push Docker images
echo -e "\n${YELLOW}[8/10] Building and pushing Docker images...${NC}"

# Build API Gateway image
echo "Building API Gateway image..."
docker build -f ../Dockerfile.api -t ${REGISTRY}/${REGISTRY_NAMESPACE}/aml-api-gateway:${ENVIRONMENT} ../../
docker push ${REGISTRY}/${REGISTRY_NAMESPACE}/aml-api-gateway:${ENVIRONMENT}

# Build Agents image
echo "Building Agents image..."
docker build -f ../Dockerfile.agents -t ${REGISTRY}/${REGISTRY_NAMESPACE}/aml-agents:${ENVIRONMENT} ../../
docker push ${REGISTRY}/${REGISTRY_NAMESPACE}/aml-agents:${ENVIRONMENT}

# Step 9: Deploy applications
echo -e "\n${YELLOW}[9/10] Deploying applications...${NC}"

# Update image tags in deployments
sed -i "s|:latest|:${ENVIRONMENT}|g" ../kubernetes/deployment-api.yaml
sed -i "s|:latest|:${ENVIRONMENT}|g" ../kubernetes/deployment-agents.yaml

# Apply deployments
kubectl apply -f ../kubernetes/deployment-api.yaml
kubectl apply -f ../kubernetes/deployment-agents.yaml

# Apply services
kubectl apply -f ../kubernetes/service-api.yaml

# Apply HPA
kubectl apply -f ../kubernetes/hpa.yaml

# Step 10: Wait for deployments to be ready
echo -e "\n${YELLOW}[10/10] Waiting for deployments to be ready...${NC}"
kubectl rollout status deployment/aml-api-gateway -n ${NAMESPACE} --timeout=5m
kubectl rollout status deployment/aml-agents -n ${NAMESPACE} --timeout=5m

# Get service endpoint
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

EXTERNAL_IP=$(kubectl get service aml-api-gateway -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP=$(kubectl get service aml-api-gateway -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

echo -e "\n${GREEN}API Gateway Endpoint: http://${EXTERNAL_IP}${NC}"
echo -e "${GREEN}API Documentation: http://${EXTERNAL_IP}/docs${NC}"
echo -e "${GREEN}Health Check: http://${EXTERNAL_IP}/health${NC}"

# Show pod status
echo -e "\n${YELLOW}Pod Status:${NC}"
kubectl get pods -n ${NAMESPACE}

echo -e "\n${GREEN}Deployment complete!${NC}"

# Made with Bob
