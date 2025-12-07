#!/bin/bash
# Run script for Subdomain Discovery Tool
# This script ensures the correct Python environment is activated before running

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Subdomain Discovery Tool${NC}"
echo "================================"

# Check if running in conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${YELLOW}Warning: No conda environment detected${NC}"
    echo "Recommended: conda env create -f config/environment.yml"
    echo "            conda activate subdomain_discovery"
    echo ""
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Check if subfinder is installed
if ! command -v subfinder &> /dev/null; then
    echo -e "${YELLOW}Warning: subfinder not found${NC}"
    echo "Install with: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    echo "Make sure \$GOPATH/bin is in your PATH"
    echo ""
fi

# Run the main script
python3 main.py "$@"
