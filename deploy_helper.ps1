# ==============================================================================
# LedgerSpur.com - One-Click Launcher & Deployment Helper
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🦅 LedgerSpur.com - US Personal Finance Platform       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "1. Preview Website Locally (Opens in Browser at http://localhost:8080)"
Write-Host "2. Generate Next Article Manually"
Write-Host "3. Rebuild All Pages, Categories & Sitemap"
Write-Host "4. Check Live Domain & DNS Activation Status (Step 1)"
Write-Host "5. Exit"
Write-Host "----------------------------------------------------------"

$choice = Read-Host "Select an option (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n[+] Starting Local Web Server at http://localhost:8080..." -ForegroundColor Green
        Start-Process "http://localhost:8080"
        .venv\Scripts\python.exe -m http.server 8080
    }
    "2" {
        Write-Host "`n[+] Generating next pending article from topics.json..." -ForegroundColor Green
        .venv\Scripts\python.exe main.py --run-once
    }
    "3" {
        Write-Host "`n[+] Rebuilding all static pages..." -ForegroundColor Green
        .venv\Scripts\python.exe main.py --rebuild
    }
    "4" {
        Write-Host "`n[+] Checking Live DNS & Connectivity for ledgerspur.com..." -ForegroundColor Green
        .venv\Scripts\python.exe check_dns.py
    }
    "5" {
        Write-Host "Exiting."
    }
    Default {
        Write-Host "Invalid option."
    }
}
