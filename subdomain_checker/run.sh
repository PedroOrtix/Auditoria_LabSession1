#!/bin/bash
# Script wrapper para facilitar el uso del Subdomain Checker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Banner
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          SUBDOMAIN CHECKER - UPM                   ║${NC}"
echo -e "${GREEN}║    Descubrimiento y Verificación de Subdominios   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    exit 1
fi

# Verificar dependencias
echo -e "${YELLOW}Verificando dependencias...${NC}"
python3 -c "import requests, bs4, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Faltan dependencias. Instalando...${NC}"
    pip install -r config/requirements.txt
fi

echo ""

# Menú interactivo
echo "¿Qué deseas hacer?"
echo ""
echo "  1) Buscar subdominios y verificar cuáles están activos"
echo "  2) Solo buscar subdominios (sin verificar)"
echo "  3) Buscar con consulta personalizada"
echo "  4) Ver ayuda completa"
echo "  5) Salir"
echo ""
read -p "Selecciona una opción (1-5): " option

case $option in
    1)
        echo ""
        read -p "Ingresa el dominio a buscar (ej: %.fi.upm.es): " domain
        if [ -z "$domain" ]; then
            domain="moodle.upm.es"
        fi
        echo -e "\n${GREEN}Buscando y verificando: $domain${NC}\n"
        python3 main.py -q "$domain"
        ;;
    2)
        echo ""
        read -p "Ingresa el dominio a buscar (ej: %.fi.upm.es): " domain
        if [ -z "$domain" ]; then
            domain="moodle.upm.es"
        fi
        echo -e "\n${GREEN}Solo buscando: $domain${NC}\n"
        python3 main.py -q "$domain" --no-verify
        ;;
    3)
        echo ""
        read -p "Ingresa el dominio: " domain
        read -p "Archivo de salida (default: subdominios_activos.txt): " output
        if [ -z "$output" ]; then
            output="subdominios_activos.txt"
        fi
        echo -e "\n${GREEN}Ejecutando búsqueda personalizada...${NC}\n"
        python3 main.py -q "$domain" -o "$output"
        ;;
    4)
        echo ""
        echo -e "${GREEN}Mostrando ayuda completa...${NC}\n"
        python3 main.py --help
        echo ""
        exit 0
        ;;
    5)
        echo -e "\n${GREEN}¡Hasta luego!${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Opción no válida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Proceso completado. Revisa los archivos:         ║${NC}"
echo -e "${GREEN}║  - subdominios_activos.txt (resultados)            ║${NC}"
echo -e "${GREEN}║  - subdomain_checker.log (log detallado)           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
