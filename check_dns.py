#!/usr/bin/env python3
"""
LedgerSpur.com DNS & GitHub Pages Live Status Checker
Verifies:
1. DNS A Records (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153)
2. CNAME Record for www.ledgerspur.com
3. HTTP / HTTPS Live Connectivity & SSL Status
"""

import sys
import socket
import urllib.request
import ssl

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

EXPECTED_IPS = {
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153"
}

def check_domain_dns(domain: str) -> dict:
    result = {"domain": domain, "resolved": False, "ips": [], "matches_github": False, "error": None}
    try:
        _, _, ips = socket.gethostbyname_ex(domain)
        result["resolved"] = True
        result["ips"] = ips
        matched = set(ips).intersection(EXPECTED_IPS)
        result["matches_github"] = len(matched) > 0
    except Exception as e:
        result["error"] = str(e)
    return result

def check_http_status(url: str) -> dict:
    result = {"url": url, "reachable": False, "status_code": None, "error": None}
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LedgerSpur-DNS-Verifier/1.0"}
    )
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=context, timeout=8) as resp:
            result["reachable"] = True
            result["status_code"] = resp.getcode()
    except urllib.error.HTTPError as e:
        result["reachable"] = True
        result["status_code"] = e.code
    except Exception as e:
        result["error"] = str(e)
    return result

def main():
    print("=" * 65)
    print("   [LedgerSpur.com] DNS & Connectivity Verifier")
    print("=" * 65)
    
    apex_dns = check_domain_dns("ledgerspur.com")
    www_dns = check_domain_dns("www.ledgerspur.com")

    print("\n[1] APEX DOMAIN (ledgerspur.com):")
    if apex_dns["resolved"]:
        print(f"    [OK] Resolved IPs: {', '.join(apex_dns['ips'])}")
        if apex_dns["matches_github"]:
            print("    [OK] GitHub Pages IP detected correctly!")
        else:
            print("    [WARN] IPs do NOT match GitHub Pages IP ranges.")
            print(f"           Expected: {', '.join(sorted(EXPECTED_IPS))}")
    else:
        print(f"    [X] Not resolving yet (Error: {apex_dns['error']})")
        print("    --> Please add the 4 GitHub Pages A-Records at your registrar.")

    print("\n[2] WWW SUBDOMAIN (www.ledgerspur.com):")
    if www_dns["resolved"]:
        print(f"    [OK] Resolved IPs: {', '.join(www_dns['ips'])}")
    else:
        print(f"    [WARN] Not resolving yet (Error: {www_dns['error']})")
        print("    --> Add CNAME record: Host 'www' pointing to your GitHub Pages URL.")

    print("\n[3] LIVE HTTP / HTTPS CONNECTIVITY:")
    for protocol in ["https://", "http://"]:
        url = f"{protocol}ledgerspur.com"
        http_res = check_http_status(url)
        if http_res["reachable"]:
            print(f"    [OK] {url} -> HTTP {http_res['status_code']}")
        else:
            print(f"    [..] {url} -> Unreachable ({http_res['error']})")

    print("\n" + "=" * 65)
    if apex_dns["matches_github"]:
        print("STATUS: [ACTIVE] DNS ACTIVATED! LedgerSpur is pointing to GitHub Pages.")
    else:
        print("STATUS: [PENDING] PENDING REGISTRAR DNS UPDATE. See instructions below.")
    print("=" * 65)

if __name__ == "__main__":
    main()
