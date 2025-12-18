#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import tempfile
import json
from pathlib import Path

# Import the logic from our existing scanner
# Assuming this script is in dns_lab_tool/, and dns_scanner.py is also there.
try:
    from dns_scanner import process_results
except ImportError:
    # If run from elsewhere, try to adjust path or fail
    sys.path.append(str(Path(__file__).parent))
    from dns_scanner import process_results

def run_unified_scan(domain):
    print(f"[*] Starting unified scan for: {domain}")
    
    # Define paths
    base_dir = Path(__file__).parent.resolve()
    # subdomain_checker is one level up and then in subdomain_checker/
    checker_dir = base_dir.parent / "subdomain_checker"
    checker_script = checker_dir / "main.py"
    
    if not checker_script.exists():
        print(f"[!] Error: Could not find subdomain_checker at {checker_script}")
        sys.exit(1)

    # 1. Run subdomain_checker
    # We'll use a temporary file for the intermediate JSON
    # Named explicitly so we can easily find it if needed, or just temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json', prefix=f'subdomains_{domain}_')
    os.close(temp_fd) # Close file descriptor, we just need the path

    print(f"[*] Step 1: Discovering subdomains (using subdomain_checker)...")
    cmd = [
        "python3",
        str(checker_script),
        "-q", f"%.{domain}",
        "-o", temp_path
    ]
    
    # We want to capture output or let it stream? 
    # Let's let it stream to stdout so user sees progress
    try:
        subprocess.run(cmd, cwd=str(checker_dir), check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Subdomain discovery failed with exit code {e.returncode}")
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        sys.exit(1)

    # 2. Run dns_scanner process_results
    final_output = base_dir / f"{domain}_full_results.json"
    print(f"\n[*] Step 2: resolving Name Servers and formatting results...")
    
    try:
        process_results(temp_path, str(final_output))
        print(f"\n[+] Unified scan completed successfully!")
        print(f"[+] Final results saved to: {final_output}")
    except Exception as e:
        print(f"[!] Error during processing: {e}")
    finally:
        # Cleanup intermediate file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified DNS Enumeration Tool")
    parser.add_argument("domain", help="Target domain (e.g., upm.es)")
    args = parser.parse_args()

    run_unified_scan(args.domain)
