# 🦅 LedgerSpur.com - Standalone US Finance Publishing Platform

> **"Smart Money. Sharper Moves."**  
> 100% Independent Static Publishing Architecture (Zero Blogger, Zero Database, Zero Hosting Cost).  
> Designed for **GitHub Pages / Cloudflare Pages** with automated Gemini AI publishing.

---

## 📁 Project Architecture

```text
C:\Users\HP\Projects\ledgerspur/
├── .github/
│   └── workflows/
│       └── daily_blog.yml         # GitHub Actions 24/7 automated publisher (08:00 UTC)
├── .venv/                         # Isolated Python 3.12 virtual environment
├── assets/
│   └── css/
│       └── style.css              # Custom Wall Street & Fintech stylesheet (Navy & Emerald)
├── categories/                    # Category archive pages
│   ├── banking.html               # High-Yield Savings & CDs
│   ├── credit-cards.html          # Cash Back, Travel & 0% APR Cards
│   ├── investing.html             # Roth IRA, 401(k) & Index Funds
│   ├── loans.html                 # Debt Consolidation & Personal Loans
│   └── reviews.html               # In-depth fintech app reviews
├── pages/                         # Legal & E-E-A-T compliance pages
│   ├── about.html                 # Editorial standards & CFP research methodology
│   ├── ftc-disclosure.html        # US FTC advertising & affiliate disclosure
│   ├── privacy-policy.html        # California Consumer Privacy Act (CCPA) compliant
│   └── terms.html                 # Financial educational disclaimer & terms
├── posts/                         # Generated standalone financial guides
│   ├── the-7-best-high-yield-savings-accounts-in-the-us-for-2026.html
│   └── best-0-intro-apr-credit-cards-for-balance-transfers-to-crush-debt.html
├── modules/
│   ├── content_generator.py       # Gemini AI engine (US English, CFP-style, E-E-A-T)
│   ├── site_builder.py            # Static site generator (Builds index, posts, sitemap)
│   └── state_manager.py           # Tracks published topics & prevents duplicates
├── .env                           # Local environment credentials (GEMINI_API_KEY)
├── .env.example                   # Configuration blueprint
├── .gitignore                     # Git tracking exclusions
├── CNAME                          # GitHub Pages custom domain (ledgerspur.com)
├── config.py                      # Centralized configuration & design tokens
├── index.html                     # Live homepage (Hero + Latest Guides Grid)
├── main.py                        # CLI orchestrator (--run-once, --seed N, --rebuild)
├── requirements.txt               # Locked dependencies
├── sitemap.xml                    # Auto-generated XML sitemap for Google Search Console
└── topics.json                    # Curated high-RPM US finance topics database
```

---

## 🎨 Design Tokens

* **Primary Trust:** `#0F172A` (Deep Slate Navy)
* **Background:** `#FFFFFF` (Pure White) & `#F8FAFC` (Ghost Slate)
* **Conversion / Money CTA:** `#059669` (Emerald Green)
* **Star / Badges:** `#D97706` (Amber Gold)
* **Typography:** `Plus Jakarta Sans` (Headings) + `Inter` (Body Text, 18px / 1.7 line height)

---

## 🚀 How to Launch on GitHub Pages (100% Free Hosting)

### 1. Push Code to GitHub
1. Create a new repository on GitHub (e.g. `ledgerspur` or `ledgerspur.github.io`).
2. Push this folder to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial launch of LedgerSpur"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ledgerspur.git
   git push -u origin main
   ```

### 2. Enable GitHub Pages
1. Go to repository **Settings** -> **Pages**.
2. Under **Build and deployment**, select:
   * Source: **Deploy from a branch**
   * Branch: **main** / folder: **/ (root)**
3. Save. Your website is instantly live on the global internet with free SSL!

### 3. Connect Custom Domain (`LedgerSpur.com`)
1. On the same GitHub Pages settings page, enter **`ledgerspur.com`** in **Custom domain**.
2. Check **Enforce HTTPS**.
3. At your domain registrar (Namecheap / Cloudflare / GoDaddy), add:
   * **4 A Records:**
     * `185.199.108.153`
     * `185.199.109.153`
     * `185.199.110.153`
     * `185.199.111.153`
   * **1 CNAME Record:**
     * Host: `www` -> Points to `YOUR_USERNAME.github.io`

---

## ⚙️ Automated Publishing (GitHub Actions)

1. In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Add a secret named `GEMINI_API_KEY` with your free Google AI Studio key.
3. The `.github/workflows/daily_blog.yml` action will run **every day automatically**:
   - Picks the next pending topic from `topics.json`.
   - Generates the in-depth article.
   - Updates `index.html`, `sitemap.xml`, and categories.
   - Pushes to `main`, which automatically updates the live website!

---

## 💻 Local Commands

* **Generate next article:**
  ```powershell
  .venv\Scripts\python.exe main.py --run-once
  ```
* **Rebuild all pages & sitemap:**
  ```powershell
  .venv\Scripts\python.exe main.py --rebuild
  ```
* **Check pending topics:**
  ```powershell
  .venv\Scripts\python.exe main.py --list
  ```
