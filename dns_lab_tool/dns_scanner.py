#!/usr/bin/env python3
import json
import dns.resolver
import sys
import argparse
from urllib.parse import urlparse

def get_nameservers(domain):
    """
    Get NS records for a domain and their IPs.
    Returns a list of dicts: [{'name': 'ns1.example.com', 'ip': '1.2.3.4'}, ...]
    """
    nameservers = []
    try:
        # Query NS records
        answers = dns.resolver.resolve(domain, 'NS')
        for rdata in answers:
            ns_name = str(rdata.target).rstrip('.')
            ns_entry = {'name': ns_name, 'ip': None}
            
            # Resolve IP for the nameserver
            try:
                # Try A record (IPv4)
                ip_answers = dns.resolver.resolve(ns_name, 'A')
                # Take the first one for simplicity, or list all? Input example showed single string IP in one place, but list in my plan.
                # Let's stringify the first IP for the 'ip' field to keep it simple as per plan example
                if ip_answers:
                     ns_entry['ip'] = str(ip_answers[0])
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                pass
            
            nameservers.append(ns_entry)
            
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.name.EmptyLabel):
        # No NS records found (common for subdomains that are just hosts)
        pass
    except Exception as e:
        # print(f"Error resolving NS for {domain}: {e}", file=sys.stderr)
        pass
        
    return nameservers

def process_results(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}.")
        return

    final_results = []

    # The input is a dict: {"url": ["ip", ...], ...}
    for url, ips in data.items():
        # Extract hostname
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path # Handle cases without scheme if any
        if not hostname:
            continue
            
        print(f"Processing: {hostname}")
        
        entry = {
            "domain": hostname,
            "ip_addresses": ips,
            "nameservers": get_nameservers(hostname)
        }
        final_results.append(entry)

    # Wrap in a "results" key or just list? The plan said:
    # { "results": [ ... ] }
    output_data = {"results": final_results}

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"Finished. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Enumeration Tool - NS Resolver")
    parser.add_argument('input_file', help="Path to input JSON file from subdomain_checker")
    parser.add_argument('output_file', help="Path to output JSON file")
    args = parser.parse_args()

    process_results(args.input_file, args.output_file)
