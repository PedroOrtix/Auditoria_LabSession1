#!/usr/bin/env python3
"""
Subdomain Discovery and Verification Tool

This tool combines subfinder for passive subdomain discovery with custom verification
to identify live assets. It mimics a real Bug Bounty workflow: Discovery → Resolution → Filtering.

Usage:
    # Discover and verify in one step
    python main.py discover www.upm.es
    
    # Verify a list from file or stdin
    python main.py verify -i subdomains.txt
    cat subdomains.txt | python main.py verify
    
    # Run full analysis
    python main.py analyze www.upm.es
"""

import sys
import argparse
import yaml
from pathlib import Path
import subprocess
import json
from typing import List, Dict
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.logger import setup_logger
from src.subdomain_verifier import SubdomainVerifier
from src.asset_analyzer import AssetAnalyzer


class SubdomainDiscoveryTool:
    """Main tool orchestrator for subdomain discovery and analysis."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the tool with configuration."""
        self.config_path = Path(config_path)
        self.load_config()
        self.setup_logging()
        
        # Initialize components
        self.verifier = SubdomainVerifier(
            http_timeout=self.config['http_timeout'],
            dns_timeout=self.config['dns_timeout'],
            headers=self.config.get('http_headers', {})
        )
        
        self.analyzer = AssetAnalyzer(
            high_value_keywords=self.config['high_value_keywords'],
            interesting_status_codes=self.config['interesting_status_codes']
        )
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"ERROR: Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML configuration: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration."""
        self.logger = setup_logger(
            log_file=self.config.get('log_file', 'subdomain_discovery.log'),
            log_level=self.config.get('log_level', 'INFO')
        )
    
    def run_subfinder(self, domain: str, output_file: str = None) -> List[str]:
        """
        Run subfinder to discover subdomains.
        
        Args:
            domain: Target domain
            output_file: Optional file to save raw subfinder output
            
        Returns:
            List of discovered subdomains
        """
        self.logger.info(f"Running subfinder for domain: {domain}")
        
        try:
            # Check if subfinder is installed
            result = subprocess.run(
                ['which', 'subfinder'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error("subfinder not found. Please install it first.")
                self.logger.error("Run: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
                return []
            
            # Run subfinder
            cmd = ['subfinder', '-d', domain, '-silent']
            
            self.logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"subfinder failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error: {result.stderr}")
                return []
            
            # Parse output
            subdomains = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            self.logger.info(f"subfinder discovered {len(subdomains)} subdomains")
            
            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write('\n'.join(subdomains))
                self.logger.info(f"Saved raw subfinder output to: {output_file}")
            
            return subdomains
            
        except subprocess.TimeoutExpired:
            self.logger.error("subfinder timed out after 5 minutes")
            return []
        except Exception as e:
            self.logger.error(f"Error running subfinder: {e}")
            return []
    
    def verify_subdomains(self, subdomains: List[str]) -> List[Dict]:
        """
        Verify which subdomains are live.
        
        Args:
            subdomains: List of subdomains to verify
            
        Returns:
            List of verification results
        """
        self.logger.info(f"Verifying {len(subdomains)} subdomains...")
        
        results = []
        total = len(subdomains)
        
        for i, subdomain in enumerate(subdomains, 1):
            if i % 10 == 0 or i == total:
                self.logger.info(f"Progress: {i}/{total} subdomains verified")
            
            result = self.verifier.verify_subdomain(subdomain, skip_dns=False)
            results.append(result)
            
            if result['is_live']:
                status = result['http_info']['status_code']
                protocol = result['http_info']['protocol']
                self.logger.debug(f"✓ {subdomain} - {protocol.upper()} {status}")
        
        live_count = sum(1 for r in results if r['is_live'])
        self.logger.info(f"Verification complete: {live_count}/{total} live assets found")
        
        return results
    
    def analyze_results(self, results: List[Dict], total_candidates: int) -> Dict:
        """
        Analyze verification results and generate report.
        
        Args:
            results: Verification results
            total_candidates: Total number of candidates discovered
            
        Returns:
            Dictionary with analysis data
        """
        self.logger.info("Analyzing results...")
        
        # Calculate metrics
        metrics = self.analyzer.calculate_efficiency_metrics(total_candidates, results)
        
        # Categorize by status
        categorized = self.analyzer.categorize_by_status(results)
        
        # Identify high-value assets
        high_value_assets = self.analyzer.identify_high_value_assets(results)
        
        self.logger.info(f"Found {len(high_value_assets)} high-value targets")
        self.logger.info(f"Live asset rate: {metrics['live_asset_rate']:.2f}%")
        self.logger.info(f"Noise filtered: {metrics['noise_percentage']:.2f}%")
        
        return {
            'metrics': metrics,
            'categorized': categorized,
            'high_value_assets': high_value_assets
        }
    
    def save_results(self, domain: str, subdomains: List[str], 
                    results: List[Dict], analysis: Dict):
        """
        Save all results to output files.
        
        Args:
            domain: Target domain
            subdomains: Original list of discovered subdomains
            results: Verification results
            analysis: Analysis data
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config.get('output_dir', 'output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw subdomains
        raw_file = output_dir / f"{domain}_{timestamp}_raw.txt"
        with open(raw_file, 'w') as f:
            f.write('\n'.join(subdomains))
        self.logger.info(f"Saved raw subdomains to: {raw_file}")
        
        # Save live subdomains
        live_subdomains = [r['subdomain'] for r in results if r['is_live']]
        live_file = output_dir / f"{domain}_{timestamp}_live.txt"
        with open(live_file, 'w') as f:
            f.write('\n'.join(live_subdomains))
        self.logger.info(f"Saved live subdomains to: {live_file}")
        
        # Save detailed results as JSON
        json_file = output_dir / f"{domain}_{timestamp}_results.json"
        with open(json_file, 'w') as f:
            json.dump({
                'domain': domain,
                'timestamp': timestamp,
                'total_discovered': len(subdomains),
                'results': results,
                'analysis': {
                    'metrics': analysis['metrics'],
                    'high_value_assets': analysis['high_value_assets']
                }
            }, f, indent=2)
        self.logger.info(f"Saved detailed results to: {json_file}")
        
        # Generate and save report
        report = self.analyzer.generate_report(
            analysis['metrics'],
            analysis['categorized'],
            analysis['high_value_assets']
        )
        
        report_file = output_dir / f"{domain}_{timestamp}_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        self.logger.info(f"Saved analysis report to: {report_file}")
        
        # Print report to console
        print("\n" + report)
    
    def discover_and_analyze(self, domain: str):
        """
        Complete workflow: discover, verify, and analyze.
        
        Args:
            domain: Target domain
        """
        self.logger.info(f"Starting full discovery and analysis for: {domain}")
        
        # Step 1: Discover subdomains with subfinder
        subdomains = self.run_subfinder(domain)
        if not subdomains:
            self.logger.error("No subdomains discovered. Exiting.")
            return
        
        # Step 2: Verify subdomains
        results = self.verify_subdomains(subdomains)
        
        # Step 3: Analyze results
        analysis = self.analyze_results(results, len(subdomains))
        
        # Step 4: Save results
        self.save_results(domain, subdomains, results, analysis)
        
        self.logger.info("Complete workflow finished successfully!")
    
    def verify_from_file(self, input_file: str):
        """
        Verify subdomains from a file.
        
        Args:
            input_file: Path to file containing subdomains (one per line)
        """
        try:
            with open(input_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"Loaded {len(subdomains)} subdomains from {input_file}")
            
            results = self.verify_subdomains(subdomains)
            analysis = self.analyze_results(results, len(subdomains))
            
            # Extract domain from filename or use generic name
            domain = Path(input_file).stem
            self.save_results(domain, subdomains, results, analysis)
            
        except FileNotFoundError:
            self.logger.error(f"File not found: {input_file}")
            sys.exit(1)
    
    def verify_from_stdin(self):
        """Verify subdomains from stdin (pipe)."""
        self.logger.info("Reading subdomains from stdin...")
        
        subdomains = []
        for line in sys.stdin:
            line = line.strip()
            if line:
                subdomains.append(line)
        
        if not subdomains:
            self.logger.error("No subdomains received from stdin")
            sys.exit(1)
        
        self.logger.info(f"Received {len(subdomains)} subdomains from stdin")
        
        results = self.verify_subdomains(subdomains)
        analysis = self.analyze_results(results, len(subdomains))
        
        self.save_results("stdin", subdomains, results, analysis)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Subdomain Discovery and Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full discovery and analysis
  python main.py analyze www.upm.es
  
  # Just discover subdomains
  python main.py discover www.upm.es
  
  # Verify from file
  python main.py verify -i subdomains.txt
  
  # Pipe subfinder output
  subfinder -d www.upm.es | python main.py verify
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command (full workflow)
    analyze_parser = subparsers.add_parser('analyze', help='Full discovery and analysis')
    analyze_parser.add_argument('domain', help='Target domain (e.g., www.upm.es)')
    analyze_parser.add_argument('-c', '--config', default='config/config.yaml',
                               help='Path to config file')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover subdomains only')
    discover_parser.add_argument('domain', help='Target domain')
    discover_parser.add_argument('-o', '--output', help='Output file for subdomains')
    discover_parser.add_argument('-c', '--config', default='config/config.yaml',
                                help='Path to config file')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify subdomains from file or stdin')
    verify_parser.add_argument('-i', '--input', help='Input file with subdomains')
    verify_parser.add_argument('-c', '--config', default='config/config.yaml',
                              help='Path to config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize tool
    tool = SubdomainDiscoveryTool(config_path=args.config)
    
    # Execute command
    if args.command == 'analyze':
        tool.discover_and_analyze(args.domain)
    
    elif args.command == 'discover':
        subdomains = tool.run_subfinder(args.domain, output_file=args.output)
        print(f"\nDiscovered {len(subdomains)} subdomains")
        if not args.output:
            for subdomain in subdomains:
                print(subdomain)
    
    elif args.command == 'verify':
        if args.input:
            tool.verify_from_file(args.input)
        else:
            # Read from stdin
            if sys.stdin.isatty():
                print("ERROR: No input file specified and no data in stdin")
                print("Usage: python main.py verify -i <file>")
                print("   or: cat subdomains.txt | python main.py verify")
                sys.exit(1)
            tool.verify_from_stdin()


if __name__ == '__main__':
    main()
