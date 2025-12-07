#!/usr/bin/env python3
"""
Script de prueba rápida para el Subdomain Checker
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crtsh_scraper import CrtShScraper
from subdomain_verifier import SubdomainVerifier
from logger import setup_logger

# Configurar logger
logger = setup_logger()

print("="*60)
print("PRUEBA RÁPIDA - Subdomain Checker")
print("="*60)

# 1. Descubrir subdominios
query = input("\n¿Qué dominio quieres buscar? (ej: moodle.upm.es): ").strip()
if not query:
    query = "moodle.upm.es"

print(f"\n[1/3] Buscando subdominios para: {query}")
scraper = CrtShScraper()
subdomains = scraper.search_subdomains(query, use_json_api=True)

if not subdomains:
    print("\n❌ No se encontraron subdominios")
    sys.exit(1)

print(f"\n✓ Subdominios encontrados: {len(subdomains)}")
print("\nSubdominios descubiertos:")
for subdomain in sorted(subdomains)[:10]:
    print(f"  - {subdomain}")

if len(subdomains) > 10:
    print(f"  ... y {len(subdomains) - 10} más")

# 2. Preguntar si verificar
verify = input("\n¿Quieres verificar cuáles están activos (HTTP 200)? (s/n): ").strip().lower()

if verify == 's':
    print(f"\n[2/3] Verificando {len(subdomains)} subdominios...")
    verifier = SubdomainVerifier(timeout=3, protocols=['https', 'http'], max_workers=20)
    results = verifier.verify_subdomains(subdomains)
    
    live_urls = verifier.get_live_subdomains(results)
    
    print(f"\n[3/3] Resultados:")
    print("="*60)
    print(f"Total descubiertos: {len(subdomains)}")
    print(f"Total activos (HTTP 200): {len(live_urls)}")
    
    if live_urls:
        print("\n✓ Subdominios activos:")
        for url in sorted(live_urls):
            print(f"  {url}")
    else:
        print("\n❌ No se encontraron subdominios activos")
else:
    print("\n✓ Verificación omitida")

print("\n" + "="*60)
print("Prueba completada")
