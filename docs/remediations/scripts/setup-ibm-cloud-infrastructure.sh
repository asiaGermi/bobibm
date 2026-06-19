#!/bin/bash
# Setup IBM Cloud Infrastructure for AML Compliance Application
# This script provisions all required IBM Cloud resources
# Usage: ./setup-ibm-cloud-infrastructure.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="aml-compliance-cluster"
REGION="us-south"
ZONE="us-south-1"
RESOURCE_GROUP="aml-compliance-rg"
REGISTRY_NAMESPACE="aml-namespace"
MACHINE_TYPE="bx2.4x16"  # 4 vCPUs, 16GB RAM
WORKER_COUNT=3

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IBM Cloud Infrastructure Setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo -e "${RED}ERROR: IBM Cloud CLI is not installed${NC}"
    echo -e "${YELLOW}Install from: https://cloud.ibm.com/docs/cli${NC}"
    exit 1
fi

# Step 1: Login to IBM Cloud
echo -e "\n${YELLOW}[1/12] Logging in to IBM Cloud...${NC}"
if [ -z "$IBM_CLOUD_API_KEY" ]; then
    echo -e "${RED}ERROR: IBM_CLOUD_API_KEY environment variable not set${NC}"
    exit 1
fi
ibmcloud login --apikey ${IBM_CLOUD_API_KEY} -r ${REGION}

# Step 2: Create Resource Group
echo -e "\n${YELLOW}[2/12] Creating Resource Group...${NC}"
ibmcloud resource group-create ${RESOURCE_GROUP} || echo "Resource group already exists"
ibmcloud target -g ${RESOURCE_GROUP}

# Step 3: Install Kubernetes Service plugin
echo -e "\n${YELLOW}[3/12] Installing Kubernetes Service plugin...${NC}"
ibmcloud plugin install kubernetes-service -f

# Step 4: Install Container Registry plugin
echo -e "\n${YELLOW}[4/12] Installing Container Registry plugin...${NC}"
ibmcloud plugin install container-registry -f

# Step 5: Create Kubernetes Cluster
echo -e "\n${YELLOW}[5/12] Creating Kubernetes Cluster (this may take 20-30 minutes)...${NC}"
ibmcloud ks cluster create vpc-gen2 \
    --name ${CLUSTER_NAME} \
    --zone ${ZONE} \
    --flavor ${MACHINE_TYPE} \
    --workers ${WORKER_COUNT} \
    --version latest \
    || echo "Cluster already exists or creation in progress"

# Wait for cluster to be ready
echo -e "\n${YELLOW}Waiting for cluster to be ready...${NC}"
while true; do
    STATE=$(ibmcloud ks cluster get --cluster ${CLUSTER_NAME} --output json | jq -r '.state')
    if [ "$STATE" == "normal" ]; then
        echo -e "${GREEN}Cluster is ready!${NC}"
        break
    fi
    echo "Cluster state: $STATE - waiting..."
    sleep 30
done

# Step 6: Configure kubectl
echo -e "\n${YELLOW}[6/12] Configuring kubectl...${NC}"
ibmcloud ks cluster config --cluster ${CLUSTER_NAME}

# Step 7: Create Container Registry Namespace
echo -e "\n${YELLOW}[7/12] Creating Container Registry Namespace...${NC}"
ibmcloud cr login
ibmcloud cr namespace-add ${REGISTRY_NAMESPACE} || echo "Namespace already exists"

# Step 8: Create IBM Cloud Object Storage instance
echo -e "\n${YELLOW}[8/12] Creating IBM Cloud Object Storage...${NC}"
ibmcloud resource service-instance-create aml-object-storage \
    cloud-object-storage standard global \
    || echo "Object Storage instance already exists"

# Step 9: Create IBM Cloud Databases for Redis
echo -e "\n${YELLOW}[9/12] Creating Redis instance...${NC}"
ibmcloud resource service-instance-create aml-redis \
    databases-for-redis standard ${REGION} \
    -p '{"members_memory_allocation_mb": "1024", "members_disk_allocation_mb": "5120"}' \
    || echo "Redis instance already exists"

# Step 10: Create IBM Cloud Monitoring instance
echo -e "\n${YELLOW}[10/12] Creating Monitoring instance...${NC}"
ibmcloud resource service-instance-create aml-monitoring \
    sysdig-monitor graduated-tier ${REGION} \
    || echo "Monitoring instance already exists"

# Step 11: Create IBM Cloud Logging instance
echo -e "\n${YELLOW}[11/12] Creating Logging instance...${NC}"
ibmcloud resource service-instance-create aml-logging \
    logdna 7-day ${REGION} \
    || echo "Logging instance already exists"

# Step 12: Create Service Credentials
echo -e "\n${YELLOW}[12/12] Creating Service Credentials...${NC}"

# Object Storage credentials
ibmcloud resource service-key-create aml-object-storage-key Manager \
    --instance-name aml-object-storage \
    || echo "Object Storage credentials already exist"

# Redis credentials
ibmcloud resource service-key-create aml-redis-key Administrator \
    --instance-name aml-redis \
    || echo "Redis credentials already exist"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Infrastructure Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}Created Resources:${NC}"
echo -e "  • Resource Group: ${RESOURCE_GROUP}"
echo -e "  • Kubernetes Cluster: ${CLUSTER_NAME}"
echo -e "  • Container Registry Namespace: ${REGISTRY_NAMESPACE}"
echo -e "  • Object Storage: aml-object-storage"
echo -e "  • Redis: aml-redis"
echo -e "  • Monitoring: aml-monitoring"
echo -e "  • Logging: aml-logging"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Configure secrets in kubernetes/secrets.yaml"
echo -e "  2. Upload IBM Synthetic Datasets to Object Storage"
echo -e "  3. Run ./deploy-to-ibm-cloud.sh to deploy the application"

echo -e "\n${BLUE}Cluster Information:${NC}"
ibmcloud ks cluster get --cluster ${CLUSTER_NAME}

echo -e "\n${GREEN}Setup complete!${NC}"

# Made with Bob
