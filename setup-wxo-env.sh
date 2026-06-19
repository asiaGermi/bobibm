#!/bin/bash
# Script to add and activate a watsonx Orchestrate SaaS environment
# Usage: ./setup-wxo-env.sh

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}watsonx Orchestrate Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Prompt for environment name
read -p "Enter environment name (e.g., 'production', 'dev'): " ENV_NAME
if [ -z "$ENV_NAME" ]; then
    echo -e "${RED}Error: Environment name cannot be empty${NC}"
    exit 1
fi

# Prompt for service instance URL
read -p "Enter service instance URL: " SERVICE_URL
if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Error: Service URL cannot be empty${NC}"
    exit 1
fi

# Prompt for API key
read -sp "Enter API key: " API_KEY
echo ""
if [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: API key cannot be empty${NC}"
    exit 1
fi

# Detect environment type from URL
ENV_TYPE=""
if [[ "$SERVICE_URL" == *"cloud.ibm.com"* ]]; then
    ENV_TYPE="ibm_iam"
    echo -e "${YELLOW}Detected IBM Cloud environment${NC}"
elif [[ "$SERVICE_URL" == *"aws"* ]] || [[ "$SERVICE_URL" == *"saas"* ]]; then
    ENV_TYPE="mcsp"
    echo -e "${YELLOW}Detected AWS/MCSP environment${NC}"
else
    echo -e "${YELLOW}Could not auto-detect environment type${NC}"
    echo "Please select environment type:"
    echo "1) IBM Cloud (ibm_iam)"
    echo "2) AWS/SaaS (mcsp)"
    echo "3) On-premises (cpd)"
    read -p "Enter choice (1-3): " TYPE_CHOICE
    case $TYPE_CHOICE in
        1) ENV_TYPE="ibm_iam" ;;
        2) ENV_TYPE="mcsp" ;;
        3) ENV_TYPE="cpd" ;;
        *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
    esac
fi

echo ""
echo -e "${BLUE}Adding environment '${ENV_NAME}'...${NC}"

# Add the environment
if [ -n "$ENV_TYPE" ]; then
    orchestrate env add -n "$ENV_NAME" -u "$SERVICE_URL" --type "$ENV_TYPE"
else
    orchestrate env add -n "$ENV_NAME" -u "$SERVICE_URL"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to add environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment added successfully${NC}"
echo ""
echo -e "${BLUE}Activating environment '${ENV_NAME}'...${NC}"

# Activate the environment with API key
orchestrate env activate "$ENV_NAME" --api-key "$API_KEY"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate environment${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Environment '${BLUE}${ENV_NAME}${NC}' is now active and ready to use."
echo ""
echo -e "${YELLOW}Note:${NC} Authentication expires every 2 hours."
echo -e "To re-activate, run: ${BLUE}orchestrate env activate ${ENV_NAME}${NC}"
echo ""
echo -e "Next steps:"
echo -e "  • List agents: ${BLUE}orchestrate agents list${NC}"
echo -e "  • List tools: ${BLUE}orchestrate tools list${NC}"
echo -e "  • Start chat: ${BLUE}orchestrate chat start${NC}"
echo ""

# Made with Bob
