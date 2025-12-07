#!/bin/bash
# Aquatone runner con configuración optimizada para evitar errores de screenshot

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Aquatone Visual Reconnaissance Runner              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que se pasó un archivo
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No input file specified${NC}"
    echo ""
    echo "Usage: $0 <subdomains_file.txt> [output_directory]"
    echo ""
    echo "Examples:"
    echo "  $0 iberiaexpress_live.txt"
    echo "  $0 iberiaexpress_live.txt custom_output"
    echo ""
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_DIR="${2:-aquatone_output}"

# Verificar que el archivo existe
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error: File not found: $INPUT_FILE${NC}"
    exit 1
fi

# Contar subdominios
NUM_TARGETS=$(wc -l < "$INPUT_FILE")
echo -e "${YELLOW}Input file:${NC} $INPUT_FILE"
echo -e "${YELLOW}Targets:${NC} $NUM_TARGETS subdominios"
echo -e "${YELLOW}Output directory:${NC} $OUTPUT_DIR"
echo ""

# Detectar navegador disponible
if command -v chromium &> /dev/null; then
    BROWSER="chromium"
    BROWSER_PATH=$(which chromium)
    echo -e "${GREEN}✓ Using Chromium:${NC} $BROWSER_PATH"
elif command -v chromium-browser &> /dev/null; then
    BROWSER="chromium-browser"
    BROWSER_PATH=$(which chromium-browser)
    echo -e "${GREEN}✓ Using Chromium:${NC} $BROWSER_PATH"
elif command -v google-chrome &> /dev/null; then
    BROWSER="google-chrome"
    BROWSER_PATH=$(which google-chrome)
    echo -e "${YELLOW}⚠ Using Google Chrome:${NC} $BROWSER_PATH (puede ser menos confiable)"
else
    echo -e "${RED}✗ Error: No Chrome/Chromium found${NC}"
    echo ""
    echo "Install with: sudo dnf install chromium"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting Aquatone...${NC}"
echo ""

# Ejecutar Aquatone con configuración optimizada
cat "$INPUT_FILE" | aquatone \
    -chrome-path "$BROWSER_PATH" \
    -threads 3 \
    -scan-timeout 300 \
    -screenshot-timeout 10000 \
    -http-timeout 8000 \
    -out "$OUTPUT_DIR"

# Verificar si se generó el reporte
if [ -f "$OUTPUT_DIR/aquatone_report.html" ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    SUCCESS!                                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✓ Report generated:${NC} $OUTPUT_DIR/aquatone_report.html"
    echo ""
    echo "Open with:"
    echo "  firefox $OUTPUT_DIR/aquatone_report.html"
    echo "  google-chrome $OUTPUT_DIR/aquatone_report.html"
    echo ""
    
    # Mostrar estadísticas
    if [ -f "$OUTPUT_DIR/aquatone_session.json" ]; then
        SCREENSHOTS=$(find "$OUTPUT_DIR/screenshots" -name "*.png" 2>/dev/null | wc -l)
        echo -e "${YELLOW}Screenshots captured:${NC} $SCREENSHOTS"
        echo ""
    fi
else
    echo -e "${RED}✗ Error: Report not generated${NC}"
    exit 1
fi
