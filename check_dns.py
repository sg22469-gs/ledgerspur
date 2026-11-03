#!/usr/bin/env python3
"""
LedgerSpur.com DNS, Cloudflare & Live Status Checker
Verifies:
1. Active Nameservers (Hostinger Parked vs Cloudflare)
2. Resolved IPs (Cloudflare Anycast vs GitHub Pages)
3. HTTP / HTTPS Connectivity, SSL Certificate & Impact.com Verification Meta Tag
"""

import sys
import socket
import urllib.request
import ssl

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CLOUDFLARE_NS = {"moura.ns.cloudflare.com", "walk.ns.cloudflare.com"}
GITHUB_IPS = {
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153"
}

def check_domain_dns(domain: str) -> dict:
    result = {"domain": domain, "resolved": False, "ips": [], "error": None}
    try:
        _, _, ips = socket.gethostbyname_ex(domain)
        result["resolved"] = True
        result["ips"] = ips
    except Exception as e:
        result["error"] = str(e)
    return result

def check_nameservers(domain: str) -> list:
    """Uses Windows nslookup to inspect active Nameservers."""
    import subprocess
    try:
        res = subprocess.run(
            ["nslookup", "-type=ns", domain],
            capture_output=True, text=True, timeout=5
        )
        ns_list = []
        for line in res.stdout.splitlines():
            line_clean = line.strip().lower()
            if "nameserver" in line_clean or "nameserver =" in line_clean:
                parts = line_clean.split("=")
                if len(parts) > 1:
                    ns_list.append(parts[1].strip().rstrip('.'))
        return ns_list
    except Exception:
        return []

def check_http_status(url: str) -> dict:
    result = {
        "url": url,
        "reachable": False,
        "status_code": None,
        "has_impact_tag": False,
        "is_hostinger_parked": False,
        "title": None,
        "error": None
    }
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LedgerSpur-Cloudflare-Verifier/2.0"}
    )
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=8) as resp:
            result["reachable"] = True
            result["status_code"] = resp.getcode()
            body = resp.read().decode('utf-8', errors='ignore')
            result["has_impact_tag"] = "impact-site-verification" in body
            result["is_hostinger_parked"] = "dns-parking" in body.lower() or "parked domain" in body.lower()
            import re
            title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE)
            if title_match:
                result["title"] = title_match.group(1).strip()
    except urllib.error.HTTPError as e:
        result["reachable"] = True
        result["status_code"] = e.code
    except Exception as e:
        result["error"] = str(e)
    return result

def main():
    print("=" * 65)
    print("   [LedgerSpur.com] Cloudflare & DNS Verifier")
    print("=" * 65)

    # 1. Nameservers
    print("\n[1] NAMESERVERS DELEGATION (Registrar Level):")
    active_ns = check_nameservers("ledgerspur.com")
    if active_ns:
        print(f"    Active NS: {', '.join(active_ns)}")
        is_cloudflare = any("cloudflare.com" in ns for ns in active_ns)
        if is_cloudflare:
            print("    [OK] Domain is delegated to Cloudflare!")
        else:
            print("    [WARN] Domain is STILL on Hostinger Parking Nameservers (dns-parking.com).")
            print("           Action: Replace them with moura.ns.cloudflare.com & walk.ns.cloudflare.com")
    else:
        print("    [..] Querying nameservers via DNS...")

    # 2. Apex Domain IPs
    apex_dns = check_domain_dns("ledgerspur.com")
    print("\n[2] APEX DOMAIN (ledgerspur.com):")
    if apex_dns["resolved"]:
        print(f"    Resolved IPs: {', '.join(apex_dns['ips'])}")
        if "2.57.91.91" in apex_dns["ips"]:
            print("    [ALERT] Pointing to Hostinger Parking IP (2.57.91.91)!")
        else:
            print("    [OK] Pointing away from default parking IP.")
    else:
        print(f"    [X] Error: {apex_dns['error']}")

    # 3. HTTP / HTTPS Status
    print("\n[3] LIVE HTTP / HTTPS CONNECTIVITY:")
    for protocol in ["https://", "http://"]:
        url = f"{protocol}ledgerspur.com"
        http_res = check_http_status(url)
        if http_res["reachable"]:
            print(f"    [OK] {url} -> Status {http_res['status_code']}")
            if http_res["title"]:
                print(f"         Page Title: {http_res['title']}")
            if http_res["is_hostinger_parked"]:
                print("         [!] WARNING: Serving Hostinger Parked Page (Verification will fail)")
            if http_res["has_impact_tag"]:
                print("         [✓] Impact verification tag detected!")
        else:
            print(f"    [..] {url} -> Unreachable ({http_res['error']})")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
