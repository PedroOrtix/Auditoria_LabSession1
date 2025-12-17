#!/bin/bash
# Script para ejecutar el email scraper

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Email Scraper UPM ===${NC}"
echo ""

# Verificar si conda está disponible
if command -v conda &> /dev/null; then
    echo -e "${YELLOW}Activando entorno conda...${NC}"
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate email_scraper 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Entorno no encontrado. Creándolo...${NC}"
        conda env create -f config/environment.yml
        conda activate email_scraper
    fi
fi

# Ejecutar el script
echo -e "${GREEN}Ejecutando scraper...${NC}"
python main.py

echo ""
echo -e "${GREEN}=== Proceso completado ===${NC}"
