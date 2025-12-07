#!/usr/bin/env python3
"""
Script principal para extraer correos electrónicos de la web de la UPM
"""
import sys
from pathlib import Path
from datetime import datetime
import yaml

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.scraper import EmailScraper
from src.logger import setup_logger


def load_config(config_file: str = 'config/config.yaml') -> dict:
    """
    Carga la configuración desde un archivo YAML.
    
    Args:
        config_file: Ruta al archivo de configuración
        
    Returns:
        Diccionario con la configuración
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Configuración por defecto
        return {
            'url': 'https://www.fi.upm.es/?id=estructura/departamentos',
            'output_dir': 'output'
        }


def main():
    """Función principal"""
    logger = setup_logger()
    
    # Cargar configuración
    config = load_config()
    url = config.get('url', 'https://www.fi.upm.es/?id=estructura/departamentos')
    output_dir = Path(config.get('output_dir', 'output'))
    
    # Crear directorio de salida si no existe
    output_dir.mkdir(exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"contactos_upm_{timestamp}.csv"
    
    logger.info(f"URL objetivo: {url}")
    logger.info(f"Archivo de salida: {output_file}")
    
    # Ejecutar scraping
    scraper = EmailScraper(url)
    scraper.run(str(output_file))


if __name__ == '__main__':
    main()
