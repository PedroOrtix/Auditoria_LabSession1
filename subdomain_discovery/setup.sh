#!/bin/bash
# Setup script for subdomain discovery tool

echo "======================================"
echo "Subdomain Discovery Tool - Setup"
echo "======================================"
echo ""

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed"
    echo "Install with: sudo dnf install -y golang"
    exit 1
fi

echo "✓ Go is installed: $(go version)"

# Add Go bin to PATH if not already there
GOPATH_BIN=$(go env GOPATH)/bin
if [[ ":$PATH:" != *":$GOPATH_BIN:"* ]]; then
    echo ""
    echo "Adding Go bin to PATH..."
    echo "export PATH=\$PATH:$GOPATH_BIN" >> ~/.zshrc
    echo "✓ Added to ~/.zshrc"
    echo ""
    echo "⚠️  Run: source ~/.zshrc"
    echo "   Or restart your terminal"
fi

export PATH=$PATH:$GOPATH_BIN

# Check if subfinder is installed
if ! command -v subfinder &> /dev/null; then
    echo ""
    echo "❌ subfinder is not installed"
    echo "Installing subfinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    echo "✓ subfinder installed"
else
    echo "✓ subfinder is installed"
fi

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import requests, yaml, bs4, dns.resolver, colorama" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All Python dependencies installed"
else
    echo "Installing Python dependencies..."
    pip install -r config/requirements.txt
fi

echo ""
echo "======================================"
echo "✓ Setup complete!"
echo "======================================"
echo ""
echo "Usage examples:"
echo "  ./run.sh analyze upm.es          # Full analysis"
echo "  python test_quick.py upm.es 50   # Quick test (50 subdomains)"
echo "  python main.py discover upm.es   # Discovery only"
echo "  python main.py verify -i file.txt # Verify from file"
echo ""
