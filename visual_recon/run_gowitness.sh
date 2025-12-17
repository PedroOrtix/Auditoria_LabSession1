#!/bin/bash
# Gowitness runner script for subdominios_activos.txt

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Gowitness - Database-Driven Screenshots          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuración
INPUT_FILE="${1:-subdominios_activos.txt}"
SCREENSHOT_DIR="${2:-./gowitness_screens}"
DB_FILE="gowitness.sqlite3"

# Verificar archivo
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}✗ Error: File not found: $INPUT_FILE${NC}"
    echo ""
    echo "Usage: $0 [input_file] [screenshot_dir]"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 subdominios_activos.txt"
    echo "  $0 subdominios_activos.txt custom_screens"
    exit 1
fi

# Contar subdominios
NUM_TARGETS=$(wc -l < "$INPUT_FILE")

echo -e "${YELLOW}Input file:${NC} $INPUT_FILE"
echo -e "${YELLOW}Targets:${NC} $NUM_TARGETS subdominios"
echo -e "${YELLOW}Screenshot dir:${NC} $SCREENSHOT_DIR"
echo -e "${YELLOW}Database:${NC} $DB_FILE"
echo ""

# Verificar si ya existe DB anterior
if [ -f "$DB_FILE" ]; then
    echo -e "${YELLOW}⚠ Database already exists: $DB_FILE${NC}"
    echo -e "${YELLOW}  Previous scans will be preserved.${NC}"
    echo ""
fi

# Verificar Chrome/Chromium
if command -v chromium-browser &> /dev/null; then
    CHROME_PATH=$(which chromium-browser)
    echo -e "${GREEN}✓ Using Chromium:${NC} $CHROME_PATH"
elif command -v google-chrome &> /dev/null; then
    CHROME_PATH=$(which google-chrome)
    echo -e "${GREEN}✓ Using Chrome:${NC} $CHROME_PATH"
else
    echo -e "${RED}✗ Chrome/Chromium not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting Gowitness scan...${NC}"
echo ""

# Ejecutar Gowitness (v3 syntax)
export PATH=$PATH:/home/pedro/go/bin

gowitness scan file \
    -f "$INPUT_FILE" \
    --screenshot-path "$SCREENSHOT_DIR" \
    --chrome-path "$CHROME_PATH" \
    --timeout 10 \
    --threads 5 \
    --write-db \
    --delay 2

# Verificar resultados
if [ -f "$DB_FILE" ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    SCAN COMPLETED!                           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✓ Database created:${NC} $DB_FILE"
    echo -e "${GREEN}✓ Screenshots saved to:${NC} $SCREENSHOT_DIR/"
    echo ""
    
    # Contar screenshots
    if [ -d "$SCREENSHOT_DIR" ]; then
        SCREENSHOT_COUNT=$(find "$SCREENSHOT_DIR" -name "*.png" 2>/dev/null | wc -l)
        echo -e "${YELLOW}Screenshots captured:${NC} $SCREENSHOT_COUNT"
    fi
    
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              LAUNCH WEB SERVER TO VIEW RESULTS               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Run the following command to start the web server:${NC}"
    echo ""
    echo -e "  ${GREEN}gowitness report server${NC}"
    echo ""
    echo -e "Then open in your browser:"
    echo -e "  ${GREEN}http://127.0.0.1:7171${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C in the server terminal to stop it.${NC}"
    echo ""
    
    # Información adicional
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Additional Commands:${NC}"
    echo ""
    echo -e "  View database stats:"
    echo -e "    ${GREEN}sqlite3 $DB_FILE 'SELECT COUNT(*) FROM urls;'${NC}"
    echo ""
    echo -e "  Generate static HTML report:"
    echo -e "    ${GREEN}gowitness report generate${NC}"
    echo ""
    echo -e "  Export to CSV:"
    echo -e "    ${GREEN}gowitness report export${NC}"
    echo ""
else
    echo -e "${RED}✗ Error: Database not created${NC}"
    exit 1
fi
