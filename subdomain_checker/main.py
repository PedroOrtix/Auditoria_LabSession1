#!/usr/bin/env python3
"""
Subdomain Checker - Main script
Automated subdomain discovery and verification tool
"""
import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict
import warnings

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

from logger import setup_logger
from crtsh_scraper import CrtShScraper
from subdomain_verifier import SubdomainVerifier


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error al parsear el archivo de configuración: {e}")
        sys.exit(1)


def save_results(live_urls: list, output_file: str):
    """
    Save live subdomain URLs to a file
    
    Args:
        live_urls: List of live subdomain URLs
        output_file: Output file path
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Subdominios Activos (HTTP 200)\n")
            f.write(f"# Total encontrados: {len(live_urls)}\n\n")
            for url in sorted(live_urls):
                f.write(f"{url}\n")
        print(f"\n✓ Resultados guardados en: {output_file}")
    except IOError as e:
        print(f"Error al guardar resultados: {e}")


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description='Subdomain Checker - Descubre y verifica subdominios activos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s                                # Usar configuración por defecto
  %(prog)s -q "%%.google.com"             # Buscar subdominios de google.com
  %(prog)s -q "%%.upm.es" -o results.txt  # Especificar archivo de salida
  %(prog)s -c mi_config.yaml              # Usar archivo de configuración personalizado
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        help='Query de búsqueda (ej: %%.upm.es)',
        type=str
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Archivo de configuración (default: config/config.yaml)',
        default='config/config.yaml',
        type=str
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Archivo de salida para resultados',
        type=str
    )
    
    parser.add_argument(
        '--no-verify',
        help='Solo descubrir subdominios, sin verificar si están activos',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.query:
        config['search_query'] = args.query
    if args.output:
        config['output_file'] = args.output
    
    # Setup logger
    log_level = getattr(__import__('logging'), config.get('log_level', 'INFO'))
    logger = setup_logger(level=log_level)
    
    logger.info("="*60)
    logger.info("Subdomain Checker - Iniciando...")
    logger.info("="*60)
    logger.info(f"Query de búsqueda: {config['search_query']}")
    
    # Step 1: Discover subdomains from crt.sh
    scraper = CrtShScraper(
        base_url=config['crt_sh_url'],
        timeout=config['request_timeout'],
        user_agent=config['user_agent']
    )
    
    use_json_api = config.get('use_json_api', True)
    subdomains = scraper.search_subdomains(config['search_query'], use_json_api=use_json_api)
    
    if not subdomains:
        logger.warning("No se encontraron subdominios.")
        if config['search_query'].startswith('%.'):
            logger.info("\n⚠️  NOTA: Las búsquedas con '%.' pueden ser demasiado amplias y fallar.")
            logger.info("    Intenta con un subdominio más específico, por ejemplo:")
            domain = config['search_query'].replace('%.', '')
            logger.info(f"      - moodle.{domain}")
            logger.info(f"      - www.{domain}")
            logger.info(f"      - %.moodle.{domain}")
        return
    
    logger.info(f"Subdominios descubiertos: {len(subdomains)}")
    
    # Step 2: Verify which subdomains are live (if not disabled)
    if args.no_verify:
        logger.info("Verificación desactivada. Mostrando solo subdominios descubiertos:")
        for subdomain in sorted(subdomains):
            print(f"  - {subdomain}")
        return
    
    verifier = SubdomainVerifier(
        timeout=config['verification_timeout'],
        protocols=config['protocols'],
        max_workers=config.get('max_workers', 10)
    )
    
    results = verifier.verify_subdomains(subdomains)
    live_urls = verifier.get_live_subdomains(results)
    
    # Display results
    logger.info("="*60)
    logger.info("RESULTADOS")
    logger.info("="*60)
    logger.info(f"Total subdominios descubiertos: {len(subdomains)}")
    logger.info(f"Total subdominios activos (HTTP 200): {len(live_urls)}")
    
    if live_urls:
        logger.info("\nSubdominios activos:")
        for url in sorted(live_urls):
            print(f"  ✓ {url}")
        
        # Save results
        save_results(live_urls, config['output_file'])
    else:
        logger.warning("No se encontraron subdominios activos.")
    
    logger.info("\n✓ Proceso completado")


if __name__ == "__main__":
    main()
