#!/bin/bash
# Phase 1 - Step 1: Install Prerequisites
# Run this script to install Azure CLI and Python dependencies

set -e

echo "=========================================="
echo "BOE OCR MVP - Prerequisites Installation"
echo "=========================================="

# Check OS
OS=$(uname -s)
echo "Detected OS: $OS"

# Install Azure CLI
echo ""
echo "Step 1: Installing Azure CLI..."
if command -v az &> /dev/null; then
    echo "Azure CLI already installed: $(az --version | head -1)"
else
    if [ "$OS" = "Darwin" ]; then
        # macOS
        echo "Installing via Homebrew..."
        brew update && brew install azure-cli
    elif [ "$OS" = "Linux" ]; then
        # Linux
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    else
        echo "Please install Azure CLI manually: https://docs.microsoft.com/cli/azure/install-azure-cli"
        exit 1
    fi
fi

# Verify Azure CLI installation
echo ""
echo "Verifying Azure CLI installation..."
az --version | head -3

# Create Python virtual environment
echo ""
echo "Step 2: Setting up Python virtual environment..."
cd /Users/shubh/boe

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created at /Users/shubh/boe/venv"
else
    echo "Virtual environment already exists"
fi

# Activate and install dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Prerequisites installed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: az login"
echo "3. Run: ./scripts/02_setup_azure_resources.sh"
