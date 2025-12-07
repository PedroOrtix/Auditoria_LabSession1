"""
Asset Analyzer Module
Analyzes discovered live assets to identify high-value targets and calculate metrics.
"""

from typing import List, Dict, Set
import re


class AssetAnalyzer:
    """Analyzes discovered assets for prioritization and metrics."""
    
    def __init__(self, high_value_keywords: List[str], interesting_status_codes: List[int]):
        """
        Initialize the analyzer with configuration.
        
        Args:
            high_value_keywords: Keywords that indicate high-value targets
            interesting_status_codes: HTTP status codes of interest
        """
        self.high_value_keywords = [kw.lower() for kw in high_value_keywords]
        self.interesting_status_codes = interesting_status_codes
    
    def is_high_value_target(self, subdomain: str) -> tuple[bool, List[str]]:
        """
        Check if a subdomain contains high-value keywords.
        
        Args:
            subdomain: The subdomain to check
            
        Returns:
            Tuple of (is_high_value, matching_keywords)
        """
        subdomain_lower = subdomain.lower()
        matching_keywords = []
        
        for keyword in self.high_value_keywords:
            if keyword in subdomain_lower:
                matching_keywords.append(keyword)
        
        return len(matching_keywords) > 0, matching_keywords
    
    def categorize_by_status(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize live assets by HTTP status code.
        
        Args:
            results: List of verification results
            
        Returns:
            Dictionary mapping status codes to lists of assets
        """
        categorized = {
            'active_200': [],        # Fully active servers
            'forbidden_403': [],     # Restricted access (high interest)
            'unauthorized_401': [],  # Requires authentication
            'redirects': [],         # 301, 302 redirects
            'other_live': [],        # Other successful responses
            'unreachable': []        # DNS resolves but HTTP fails
        }
        
        for result in results:
            if not result.get('is_live'):
                if result.get('dns_resolves'):
                    categorized['unreachable'].append(result)
                continue
            
            http_info = result.get('http_info', {})
            status_code = http_info.get('status_code')
            
            if status_code == 200:
                categorized['active_200'].append(result)
            elif status_code == 403:
                categorized['forbidden_403'].append(result)
            elif status_code == 401:
                categorized['unauthorized_401'].append(result)
            elif status_code in [301, 302, 303, 307, 308]:
                categorized['redirects'].append(result)
            elif status_code:
                categorized['other_live'].append(result)
        
        return categorized
    
    def identify_high_value_assets(self, results: List[Dict]) -> List[Dict]:
        """
        Identify high-value assets from verification results.
        
        Args:
            results: List of verification results
            
        Returns:
            List of high-value assets with priority scores
        """
        high_value_assets = []
        
        for result in results:
            if not result.get('is_live'):
                continue
            
            subdomain = result['subdomain']
            is_high_value, keywords = self.is_high_value_target(subdomain)
            
            if not is_high_value:
                continue
            
            http_info = result.get('http_info', {})
            status_code = http_info.get('status_code')
            
            # Calculate priority score
            priority_score = 0
            priority_reasons = []
            
            # Keywords add base value
            priority_score += len(keywords) * 10
            priority_reasons.extend([f"Keyword: {kw}" for kw in keywords])
            
            # 403 is especially interesting (restricted internal asset)
            if status_code == 403:
                priority_score += 20
                priority_reasons.append("403 Forbidden - Restricted access")
            elif status_code == 401:
                priority_score += 15
                priority_reasons.append("401 Unauthorized - Auth required")
            elif status_code == 200:
                priority_score += 10
                priority_reasons.append("200 OK - Fully accessible")
            
            high_value_assets.append({
                'subdomain': subdomain,
                'keywords': keywords,
                'status_code': status_code,
                'protocol': http_info.get('protocol'),
                'title': http_info.get('title'),
                'priority_score': priority_score,
                'priority_reasons': priority_reasons,
                'http_info': http_info
            })
        
        # Sort by priority score (highest first)
        high_value_assets.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return high_value_assets
    
    def calculate_efficiency_metrics(self, total_candidates: int, 
                                     results: List[Dict]) -> Dict[str, any]:
        """
        Calculate reconnaissance efficiency metrics.
        
        Args:
            total_candidates: Total number of subdomains discovered
            results: List of verification results
            
        Returns:
            Dictionary with efficiency metrics
        """
        live_assets = [r for r in results if r.get('is_live')]
        dns_resolved = [r for r in results if r.get('dns_resolves')]
        
        metrics = {
            'total_candidates': total_candidates,
            'dns_resolved': len(dns_resolved),
            'live_assets': len(live_assets),
            'dead_domains': total_candidates - len(dns_resolved),
            'dns_resolution_rate': (len(dns_resolved) / total_candidates * 100) if total_candidates > 0 else 0,
            'live_asset_rate': (len(live_assets) / total_candidates * 100) if total_candidates > 0 else 0,
            'noise_filtered': total_candidates - len(live_assets),
            'noise_percentage': ((total_candidates - len(live_assets)) / total_candidates * 100) if total_candidates > 0 else 0
        }
        
        # Calculate status code distribution
        status_distribution = {}
        for result in live_assets:
            status = result.get('http_info', {}).get('status_code', 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        metrics['status_distribution'] = status_distribution
        
        return metrics
    
    def generate_report(self, metrics: Dict, categorized: Dict, 
                       high_value_assets: List[Dict]) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            metrics: Efficiency metrics
            categorized: Categorized assets by status
            high_value_assets: High-value assets with priorities
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("SUBDOMAIN DISCOVERY AND ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Efficiency Metrics
        report_lines.append("1. RECONNAISSANCE EFFICIENCY METRICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Candidates (subfinder output): {metrics['total_candidates']}")
        report_lines.append(f"DNS Resolved: {metrics['dns_resolved']} ({metrics['dns_resolution_rate']:.2f}%)")
        report_lines.append(f"Live Assets (validated hosts): {metrics['live_assets']} ({metrics['live_asset_rate']:.2f}%)")
        report_lines.append(f"Noise Filtered: {metrics['noise_filtered']} ({metrics['noise_percentage']:.2f}%)")
        report_lines.append("")
        report_lines.append(f"Signal-to-Noise Ratio: {metrics['live_asset_rate']:.2f}%")
        report_lines.append(f"Discovery Efficiency: {metrics['live_assets']}/{metrics['total_candidates']} live assets found")
        report_lines.append("")
        
        # Status Code Distribution
        report_lines.append("2. HTTP STATUS CODE DISTRIBUTION")
        report_lines.append("-" * 80)
        for status, count in sorted(metrics['status_distribution'].items()):
            report_lines.append(f"HTTP {status}: {count} assets")
        report_lines.append("")
        
        # Categorized Assets
        report_lines.append("3. ASSET CATEGORIZATION")
        report_lines.append("-" * 80)
        report_lines.append(f"Fully Active (200 OK): {len(categorized['active_200'])} assets")
        report_lines.append(f"Restricted Access (403 Forbidden): {len(categorized['forbidden_403'])} assets ⚠️ HIGH INTEREST")
        report_lines.append(f"Authentication Required (401): {len(categorized['unauthorized_401'])} assets")
        report_lines.append(f"Redirects (3xx): {len(categorized['redirects'])} assets")
        report_lines.append(f"Other Live: {len(categorized['other_live'])} assets")
        report_lines.append(f"DNS Resolved but Unreachable: {len(categorized['unreachable'])} assets")
        report_lines.append("")
        
        # High-Value Targets
        report_lines.append("4. HIGH-VALUE TARGETS (Prioritized)")
        report_lines.append("-" * 80)
        if high_value_assets:
            report_lines.append(f"Found {len(high_value_assets)} high-value targets:")
            report_lines.append("")
            
            for i, asset in enumerate(high_value_assets[:20], 1):  # Top 20
                report_lines.append(f"{i}. {asset['subdomain']} [Priority Score: {asset['priority_score']}]")
                report_lines.append(f"   Status: HTTP {asset['status_code']} ({asset['protocol'].upper()})")
                report_lines.append(f"   Keywords: {', '.join(asset['keywords'])}")
                if asset['title']:
                    report_lines.append(f"   Title: {asset['title'][:60]}...")
                report_lines.append(f"   Reasons: {', '.join(asset['priority_reasons'])}")
                report_lines.append("")
        else:
            report_lines.append("No high-value targets identified based on keywords.")
            report_lines.append("")
        
        # Detailed 403 Forbidden Assets (High Interest)
        if categorized['forbidden_403']:
            report_lines.append("5. DETAILED 403 FORBIDDEN ASSETS (Restricted Internal Assets)")
            report_lines.append("-" * 80)
            for result in categorized['forbidden_403'][:10]:  # Top 10
                subdomain = result['subdomain']
                http_info = result['http_info']
                report_lines.append(f"• {subdomain}")
                report_lines.append(f"  Protocol: {http_info['protocol'].upper()}")
                if http_info.get('title'):
                    report_lines.append(f"  Title: {http_info['title'][:60]}")
                report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
