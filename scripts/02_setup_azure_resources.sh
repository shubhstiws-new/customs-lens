#!/bin/bash
# Phase 1 - Step 2: Setup Azure Resources
# Run this after logging into Azure CLI with: az login

set -e

echo "=========================================="
echo "BOE OCR MVP - Azure Resource Setup"
echo "=========================================="

# Configuration - Free Tier settings
RESOURCE_GROUP="rg-boe-ocr-mvp"
LOCATION="westus"  # San Francisco region
DOC_INTEL_NAME="doc-intel-boe-mvp"
SQL_SERVER_NAME="sql-boe-mvp-$(date +%s)"  # Unique name with timestamp
SQL_DB_NAME="boe"
KEY_VAULT_NAME="kv-boe-mvp-$(date +%s)"  # Unique name with timestamp

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if logged in
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure first: az login"
    exit 1
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${GREEN}Logged in to subscription: $SUBSCRIPTION${NC}"

# Step 1: Create Resource Group
echo ""
echo "Step 1: Creating Resource Group..."
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}Resource group '$RESOURCE_GROUP' already exists${NC}"
else
    az group create --name $RESOURCE_GROUP --location $LOCATION
    echo -e "${GREEN}Resource group '$RESOURCE_GROUP' created${NC}"
fi

# Step 2: Create Document Intelligence (Form Recognizer) - Free Tier
echo ""
echo "Step 2: Creating Document Intelligence resource (Free F0 tier)..."
DOC_INTEL_EXISTS=$(az cognitiveservices account list --resource-group $RESOURCE_GROUP --query "[?name=='$DOC_INTEL_NAME'].name" -o tsv)
if [ -n "$DOC_INTEL_EXISTS" ]; then
    echo -e "${YELLOW}Document Intelligence '$DOC_INTEL_NAME' already exists${NC}"
else
    az cognitiveservices account create \
        --name $DOC_INTEL_NAME \
        --resource-group $RESOURCE_GROUP \
        --kind FormRecognizer \
        --sku F0 \
        --location $LOCATION \
        --yes
    echo -e "${GREEN}Document Intelligence '$DOC_INTEL_NAME' created (F0 Free tier)${NC}"
fi

# Get Document Intelligence endpoint and key
DOC_INTEL_ENDPOINT=$(az cognitiveservices account show \
    --name $DOC_INTEL_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.endpoint" -o tsv)
DOC_INTEL_KEY=$(az cognitiveservices account keys list \
    --name $DOC_INTEL_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "key1" -o tsv)

echo "Document Intelligence Endpoint: $DOC_INTEL_ENDPOINT"

# Step 3: Create Azure SQL Server and Database - Free Tier
echo ""
echo "Step 3: Creating Azure SQL Database (Free tier)..."
echo -e "${YELLOW}Note: Azure SQL free tier offers 100,000 vCore seconds/month${NC}"

# Prompt for SQL admin password
read -sp "Enter SQL admin password (min 8 chars, uppercase, lowercase, number): " SQL_PASSWORD
echo ""

# Create SQL Server
az sql server create \
    --name $SQL_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --admin-user boeadmin \
    --admin-password "$SQL_PASSWORD"

echo -e "${GREEN}SQL Server '$SQL_SERVER_NAME' created${NC}"

# Create SQL Database with free tier
az sql db create \
    --name $SQL_DB_NAME \
    --server $SQL_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --edition GeneralPurpose \
    --compute-model Serverless \
    --family Gen5 \
    --capacity 1 \
    --auto-pause-delay 60 \
    --min-capacity 0.5 \
    --free-limit true \
    --free-limit-exhaustion-behavior AutoPause

echo -e "${GREEN}SQL Database '$SQL_DB_NAME' created (Free tier)${NC}"

# Configure firewall - Allow Azure services
az sql server firewall-rule create \
    --server $SQL_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Get current public IP and add to firewall
MY_IP=$(curl -s ifconfig.me)
az sql server firewall-rule create \
    --server $SQL_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --name AllowMyIP \
    --start-ip-address $MY_IP \
    --end-ip-address $MY_IP

echo "Firewall configured for Azure services and your IP: $MY_IP"

# Step 4: Create Key Vault (Optional but recommended)
echo ""
echo "Step 4: Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard

# Store secrets in Key Vault
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "doc-intel-key" --value "$DOC_INTEL_KEY"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "sql-password" --value "$SQL_PASSWORD"

echo -e "${GREEN}Key Vault '$KEY_VAULT_NAME' created and secrets stored${NC}"

# Step 5: Create .env file with configuration
echo ""
echo "Step 5: Creating configuration file..."
cat > /Users/shubh/boe/config/.env << EOF
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$DOC_INTEL_ENDPOINT
AZURE_DOCUMENT_INTELLIGENCE_KEY=$DOC_INTEL_KEY

# Azure SQL Database
AZURE_SQL_SERVER=$SQL_SERVER_NAME.database.windows.net
AZURE_SQL_DATABASE=$SQL_DB_NAME
AZURE_SQL_USERNAME=boeadmin
AZURE_SQL_PASSWORD=$SQL_PASSWORD

# Azure Key Vault
AZURE_KEY_VAULT_URL=https://$KEY_VAULT_NAME.vault.azure.net/

# Application Settings
OCR_CONFIDENCE_THRESHOLD=0.8
LOG_LEVEL=INFO
BATCH_SIZE=10
EOF

echo -e "${GREEN}Configuration saved to /Users/shubh/boe/config/.env${NC}"

# Summary
echo ""
echo "=========================================="
echo "Azure Resource Setup Complete!"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - Document Intelligence: $DOC_INTEL_NAME (F0 Free tier)"
echo "  - SQL Server: $SQL_SERVER_NAME"
echo "  - SQL Database: $SQL_DB_NAME (Free tier)"
echo "  - Key Vault: $KEY_VAULT_NAME"
echo ""
echo "Configuration saved to: /Users/shubh/boe/config/.env"
echo ""
echo "Free tier limits:"
echo "  - Document Intelligence F0: 500 pages/month free"
echo "  - SQL Database: 100,000 vCore seconds/month free"
echo ""
echo "Next steps:"
echo "  1. Verify resources in Azure Portal"
echo "  2. Run Phase 2: OCR Testing"
