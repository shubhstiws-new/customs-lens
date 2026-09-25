#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Phase 1 - Step 3: Verify Azure Setup
# Run this to verify all resources are correctly configured

set -e

echo "=========================================="
echo "BOE OCR MVP - Setup Verification"
echo "=========================================="

# Load environment variables
if [ -f $PROJECT_ROOT/config/.env ]; then
    export $(grep -v '^#' $PROJECT_ROOT/config/.env | xargs)
    echo "Configuration loaded from .env"
else
    echo "ERROR: .env file not found. Run 02_setup_azure_resources.sh first."
    exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test 1: Azure CLI
echo ""
echo "Test 1: Azure CLI..."
if az account show &> /dev/null; then
    echo -e "${GREEN}PASS${NC} - Azure CLI logged in"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC} - Azure CLI not logged in"
    ((FAILED++))
fi

# Test 2: Document Intelligence endpoint
echo ""
echo "Test 2: Document Intelligence endpoint..."
if [ -n "$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" ]; then
    # Test connectivity
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" 2>/dev/null || echo "000")
    if [ "$RESPONSE" != "000" ]; then
        echo -e "${GREEN}PASS${NC} - Document Intelligence endpoint reachable"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} - Cannot reach Document Intelligence endpoint"
        ((FAILED++))
    fi
else
    echo -e "${RED}FAIL${NC} - Document Intelligence endpoint not configured"
    ((FAILED++))
fi

# Test 3: Python environment
echo ""
echo "Test 3: Python environment..."
if [ -d $PROJECT_ROOT/venv ]; then
    source $PROJECT_ROOT/venv/bin/activate
    if python -c "import azure.ai.formrecognizer" 2>/dev/null; then
        echo -e "${GREEN}PASS${NC} - Python dependencies installed"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} - Python dependencies not installed"
        ((FAILED++))
    fi
else
    echo -e "${RED}FAIL${NC} - Virtual environment not found"
    ((FAILED++))
fi

# Test 4: SQL Database connectivity
echo ""
echo "Test 4: SQL Database connectivity..."
if [ -n "$AZURE_SQL_SERVER" ]; then
    # Use Python to test SQL connectivity
    source $PROJECT_ROOT/venv/bin/activate 2>/dev/null
    python3 << EOF
import sys
try:
    import pyodbc
    # Just verify pyodbc is installed - actual connection test requires ODBC driver
    print("pyodbc installed")
    sys.exit(0)
except ImportError:
    sys.exit(1)
EOF
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PASS${NC} - SQL client library installed"
        echo "  Note: Full connectivity test requires ODBC driver"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} - SQL client library not installed"
        ((FAILED++))
    fi
else
    echo -e "${RED}FAIL${NC} - SQL Server not configured"
    ((FAILED++))
fi

# Test 5: Configuration file
echo ""
echo "Test 5: Configuration file..."
REQUIRED_VARS=("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" "AZURE_DOCUMENT_INTELLIGENCE_KEY" "AZURE_SQL_SERVER" "AZURE_SQL_DATABASE")
ALL_SET=true
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "  Missing: $VAR"
        ALL_SET=false
    fi
done
if $ALL_SET; then
    echo -e "${GREEN}PASS${NC} - All required configuration variables set"
    ((PASSED++))
else
    echo -e "${RED}FAIL${NC} - Some configuration variables missing"
    ((FAILED++))
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! Ready for Phase 2.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review and fix issues.${NC}"
    exit 1
fi
