"""
Crt.sh scraper module for subdomain discovery
"""
import requests
from bs4 import BeautifulSoup
from typing import Set, List
import time
import json
import re
from logger import setup_logger

logger = setup_logger()


class CrtShScraper:
    """Scraper for crt.sh certificate transparency logs"""
    
    def __init__(self, base_url: str = "https://crt.sh/", timeout: int = 30, user_agent: str = None):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL for crt.sh
            timeout: Request timeout in seconds
            user_agent: Custom User-Agent header
        """
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_subdomains(self, query: str, use_json_api: bool = True) -> Set[str]:
        """
        Search for subdomains using crt.sh
        
        Args:
            query: Search query (e.g., "%.upm.es" or "moodle.upm.es")
            use_json_api: If True, use JSON API (faster), else scrape HTML
            
        Returns:
            Set of discovered subdomains
        """
        logger.info(f"Buscando subdominios para: {query}")
        
        if use_json_api:
            return self._search_with_json_api(query)
        else:
            return self._search_with_html_scraping(query)
    
    def _search_with_json_api(self, query: str) -> Set[str]:
        """
        Search using crt.sh JSON API (more efficient)
        
        Args:
            query: Search query
            
        Returns:
            Set of discovered subdomains
        """
        params = {'q': query, 'output': 'json'}
        subdomains = set()
        
        try:
            logger.debug(f"Consultando API JSON de crt.sh...")
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            certificates = response.json()
            logger.info(f"Certificados encontrados: {len(certificates)}")
            
            # Extract subdomains from certificates
            for cert in certificates:
                # El campo 'name_value' contiene los dominios (pueden ser múltiples)
                name_value = cert.get('name_value', '')
                
                # Los dominios pueden estar separados por saltos de línea
                domains = name_value.split('\n')
                
                for domain in domains:
                    domain = domain.strip()
                    
                    # Limpiar wildcards y caracteres especiales
                    if domain.startswith('*.'):
                        domain = domain[2:]
                    
                    # Validar que es un dominio válido
                    if self._is_valid_domain(domain):
                        subdomains.add(domain.lower())
            
            logger.info(f"Subdominios únicos extraídos: {len(subdomains)}")
            return subdomains
            
        except requests.Timeout:
            logger.error(f"Timeout al consultar crt.sh - La búsqueda '{query}' puede ser demasiado amplia")
            logger.info("Sugerencia: Prueba con un query más específico (ej: 'subdomain.domain.com' en vez de '%.domain.com')")
            return subdomains
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            logger.info("Intentando con scraping HTML como alternativa...")
            return self._search_with_html_scraping(query)
        except requests.RequestException as e:
            logger.error(f"Error al consultar crt.sh: {e}")
            return subdomains
    
    def _search_with_html_scraping(self, query: str) -> Set[str]:
        """
        Search by scraping HTML (fallback method)
        
        Args:
            query: Search query
            
        Returns:
            Set of discovered subdomains
        """
        params = {'q': query}
        subdomains = set()
        
        try:
            logger.debug(f"Consultando crt.sh con scraping HTML...")
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer subdominios de la tabla
            subdomains = self.extract_subdomains_from_table(soup)
            
            logger.info(f"Subdominios extraídos del HTML: {len(subdomains)}")
            return subdomains
            
        except requests.RequestException as e:
            logger.error(f"Error al hacer scraping HTML: {e}")
            return subdomains
    
    def extract_subdomains_from_table(self, soup: BeautifulSoup) -> Set[str]:
        """
        Extract subdomains from HTML table
        
        Args:
            soup: BeautifulSoup object with parsed HTML
            
        Returns:
            Set of subdomain names
        """
        subdomains = set()
        
        # Buscar todas las tablas
        tables = soup.find_all('table')
        
        if not tables:
            logger.warning("No se encontraron tablas en el HTML")
            return subdomains
        
        logger.debug(f"Encontradas {len(tables)} tablas en el HTML")
        
        # La tabla principal suele ser la primera o segunda
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                # Buscar celdas que contengan dominios
                for cell in cells:
                    text = cell.get_text(strip=True)
                    
                    # Intentar extraer dominios del texto
                    if self._is_valid_domain(text):
                        if text.startswith('*.'):
                            text = text[2:]
                        subdomains.add(text.lower())
        
        return subdomains
    
    def _is_valid_domain(self, domain: str) -> bool:
        """
        Validate if a string is a valid domain name
        
        Args:
            domain: String to validate
            
        Returns:
            True if valid domain, False otherwise
        """
        if not domain or len(domain) > 253:
            return False
        
        # Patrón básico para validar dominios
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        
        return bool(re.match(pattern, domain))
