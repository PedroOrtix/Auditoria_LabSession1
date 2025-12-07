#!/usr/bin/env python3
"""
Quick test script for subdomain discovery - limits to first 50 subdomains for testing
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import SubdomainDiscoveryTool

def quick_test(domain: str, limit: int = 50):
    """
    Quick test with limited subdomain count.
    
    Args:
        domain: Target domain
        limit: Maximum number of subdomains to verify
    """
    tool = SubdomainDiscoveryTool()
    
    print(f"[Quick Test Mode] Limiting to first {limit} subdomains\n")
    
    # Run subfinder
    subdomains = tool.run_subfinder(domain)
    
    if not subdomains:
        print("No subdomains discovered.")
        return
    
    print(f"\nTotal discovered: {len(subdomains)}")
    print(f"Will verify: {min(limit, len(subdomains))}\n")
    
    # Limit subdomains
    subdomains = subdomains[:limit]
    
    # Verify
    results = tool.verify_subdomains(subdomains)
    
    # Analyze
    analysis = tool.analyze_results(results, len(subdomains))
    
    # Save
    tool.save_results(domain, subdomains, results, analysis)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_quick.py <domain> [limit]")
        print("Example: python test_quick.py upm.es 50")
        sys.exit(1)
    
    domain = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    quick_test(domain, limit)
