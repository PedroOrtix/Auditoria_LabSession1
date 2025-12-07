"""
Subdomain verifier module
"""
import requests
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from logger import setup_logger

logger = setup_logger()


class SubdomainVerifier:
    """Verifies which subdomains are live and return HTTP 200"""
    
    def __init__(self, timeout: int = 3, max_workers: int = 10, protocols: List[str] = None):
        """
        Initialize the verifier
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent threads
            protocols: List of protocols to check (e.g., ['http', 'https'])
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.protocols = protocols or ['https', 'http']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def check_subdomain(self, subdomain: str, protocol: str = 'https') -> Dict[str, any]:
        """
        Check if a subdomain is live
        
        Args:
            subdomain: The subdomain to check
            protocol: Protocol to use (http or https)
            
        Returns:
            Dictionary with check results
        """
        url = f"{protocol}://{subdomain}"
        result = {
            'subdomain': subdomain,
            'url': url,
            'protocol': protocol,
            'is_live': False,
            'status_code': None,
            'error': None
        }
        
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False  # Ignorar errores SSL para testing
            )
            
            result['status_code'] = response.status_code
            result['is_live'] = (response.status_code == 200)
            
            if result['is_live']:
                logger.info(f"✓ {url} - HTTP {response.status_code}")
            else:
                logger.debug(f"✗ {url} - HTTP {response.status_code}")
                
        except requests.RequestException as e:
            result['error'] = str(e)
            logger.debug(f"✗ {url} - Error: {e}")
        
        return result
    
    def verify_subdomains(self, subdomains: Set[str]) -> List[Dict[str, any]]:
        """
        Verify multiple subdomains concurrently
        
        Args:
            subdomains: Set of subdomains to verify
            
        Returns:
            List of results for all checks
        """
        logger.info(f"Verificando {len(subdomains)} subdominios...")
        
        results = []
        tasks = []
        
        # Create tasks for all subdomain/protocol combinations
        for subdomain in subdomains:
            for protocol in self.protocols:
                tasks.append((subdomain, protocol))
        
        logger.info(f"Total de verificaciones a realizar: {len(tasks)}")
        
        # Execute checks concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.check_subdomain, subdomain, protocol): (subdomain, protocol)
                for subdomain, protocol in tasks
            }
            
            for future in as_completed(future_to_task):
                result = future.result()
                results.append(result)
        
        # Filter only live subdomains
        live_results = [r for r in results if r['is_live']]
        logger.info(f"Subdominios activos encontrados: {len(live_results)}")
        
        return results
    
    def get_live_subdomains(self, results: List[Dict[str, any]]) -> List[str]:
        """
        Extract only live subdomain URLs from results
        
        Args:
            results: List of verification results
            
        Returns:
            List of live subdomain URLs
        """
        return [r['url'] for r in results if r['is_live']]
