"""
Subdomain Verifier Module
Verifies which discovered subdomains are actually live by checking DNS resolution
and HTTP responses with timeout handling.
"""

import requests
import dns.resolver
import socket
from typing import Dict, List, Optional
from urllib.parse import urlparse
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SubdomainVerifier:
    """Verifies if subdomains are live and accessible."""
    
    def __init__(self, http_timeout: int = 3, dns_timeout: int = 2, headers: Optional[Dict] = None):
        """
        Initialize the verifier with timeout settings.
        
        Args:
            http_timeout: Timeout for HTTP requests in seconds
            dns_timeout: Timeout for DNS resolution in seconds
            headers: Custom HTTP headers to use
        """
        self.http_timeout = http_timeout
        self.dns_timeout = dns_timeout
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        
        # Configure DNS resolver
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = dns_timeout
        self.resolver.lifetime = dns_timeout
    
    def check_dns_resolution(self, subdomain: str) -> bool:
        """
        Check if a subdomain resolves via DNS.
        
        Args:
            subdomain: The subdomain to check
            
        Returns:
            True if DNS resolves, False otherwise
        """
        try:
            self.resolver.resolve(subdomain, 'A')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, 
                dns.exception.DNSException):
            return False
    
    def check_http_status(self, subdomain: str) -> Dict[str, any]:
        """
        Check HTTP/HTTPS status of a subdomain.
        
        Args:
            subdomain: The subdomain to check
            
        Returns:
            Dictionary with status information:
            - accessible: bool
            - status_code: int or None
            - protocol: str (http or https)
            - redirect_url: str or None
            - title: str or None
        """
        result = {
            'accessible': False,
            'status_code': None,
            'protocol': None,
            'redirect_url': None,
            'title': None,
            'error': None
        }
        
        # Try HTTPS first, then HTTP
        for protocol in ['https', 'http']:
            url = f"{protocol}://{subdomain}"
            try:
                response = requests.get(
                    url,
                    timeout=self.http_timeout,
                    headers=self.headers,
                    allow_redirects=True,
                    verify=False  # Skip SSL verification to avoid certificate errors
                )
                
                result['accessible'] = True
                result['status_code'] = response.status_code
                result['protocol'] = protocol
                
                # Check if redirected
                if response.history:
                    result['redirect_url'] = response.url
                
                # Try to extract title from HTML
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if soup.title:
                        result['title'] = soup.title.string.strip() if soup.title.string else None
                except Exception:
                    pass
                
                return result
                
            except requests.exceptions.Timeout:
                result['error'] = f'{protocol.upper()} timeout'
                continue
            except requests.exceptions.ConnectionError:
                result['error'] = f'{protocol.upper()} connection error'
                continue
            except requests.exceptions.RequestException as e:
                result['error'] = f'{protocol.upper()} error: {str(e)[:50]}'
                continue
        
        return result
    
    def verify_subdomain(self, subdomain: str, skip_dns: bool = False) -> Dict[str, any]:
        """
        Perform complete verification of a subdomain.
        
        Args:
            subdomain: The subdomain to verify
            skip_dns: Skip DNS check (useful when piping from subfinder)
            
        Returns:
            Dictionary with complete verification results
        """
        subdomain = subdomain.strip()
        
        result = {
            'subdomain': subdomain,
            'dns_resolves': False,
            'is_live': False,
            'http_info': None
        }
        
        # Check DNS resolution
        if not skip_dns:
            result['dns_resolves'] = self.check_dns_resolution(subdomain)
            if not result['dns_resolves']:
                return result
        else:
            result['dns_resolves'] = True  # Assume DNS resolves if skipped
        
        # Check HTTP status
        http_info = self.check_http_status(subdomain)
        result['http_info'] = http_info
        
        # Consider live if accessible via HTTP
        if http_info['accessible']:
            result['is_live'] = True
        
        return result
    
    def verify_batch(self, subdomains: List[str], skip_dns: bool = False) -> List[Dict[str, any]]:
        """
        Verify a batch of subdomains.
        
        Args:
            subdomains: List of subdomains to verify
            skip_dns: Skip DNS check for all subdomains
            
        Returns:
            List of verification results
        """
        results = []
        for subdomain in subdomains:
            result = self.verify_subdomain(subdomain, skip_dns=skip_dns)
            results.append(result)
        return results
