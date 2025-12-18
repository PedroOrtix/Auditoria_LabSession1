# Unified DNS Enumeration Tool

This directory contains the `unified_scanner.py` tool, which is designed to perform comprehensive DNS enumeration on a target domain. It orchestrates a two-step process: discovering subdomains and then resolving their Name Server (NS) records.

## Files

- **`unified_scanner.py`**: The main entry point script. It runs the subdomain discovery process and then triggers the DNS analysis.
- **`dns_scanner.py`**: A helper module used by `unified_scanner.py` to resolve NS records and IPs for the discovered subdomains.
- **`upm.es_full_results.json`**: (Example) Output file showing the results of a scan against `upm.es`.

## Prerequisites

### Dependencies
This tool requires Python 3 and the following Python packages:
- `dnspython`

You can install it via pip:
```bash
pip install dnspython
```

### Directory Structure
This tool depends on the `subdomain_checker` tool located in a sibling directory. Ensure your project structure looks like this:

```
project_root/
├── dns_lab_tool/
│   ├── unified_scanner.py
│   └── dns_scanner.py
└── subdomain_checker/
    └── main.py
```

## Usage

To run a scan against a domain (e.g., `upm.es`), navigate to this directory and run:

```bash
python3 unified_scanner.py upm.es
```

### How it Works
1. **Subdomain Discovery**: Calls `../subdomain_checker/main.py` to scrape subdomains (e.g., from crt.sh) and identify their IP addresses.
2. **DNS Resolution**: Processes the list of discovered subdomains using `dns_scanner.py`. For each subdomain, it:
   - Resolves its Name Server (NS) records.
   - Resolves the IP addresses of those Name Servers.
3. **Output**:  Saves the combined results to a JSON file named `<domain>_full_results.json`.

## Output Format

The output is a JSON file containing a list of results. Each entry includes:
- `domain`: The subdomain discovered.
- `ip_addresses`: List of IP addresses for that subdomain.
- `nameservers`: List of nameservers, where each entry contains:
  - `name`: The hostname of the nameserver.
  - `ip`: The resolved IP address of the nameserver.

**Example:**
```json
{
    "results": [
        {
            "domain": "www.upm.es",
            "ip_addresses": ["138.100.10.10"],
            "nameservers": [
                {
                    "name": "dns1.upm.es",
                    "ip": "138.100.200.1"
                }
            ]
        }
    ]
}
```
