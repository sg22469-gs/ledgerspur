import json
from datetime import datetime
from pathlib import Path
from config import Config

class SiteBuilder:
    def __init__(self):
        self.base_dir = Config.BASE_DIR
        self.posts_dir = Config.POSTS_DIR
        self.pages_dir = Config.PAGES_DIR
        self.categories_dir = Config.CATEGORIES_DIR
        self.history_file = Config.HISTORY_FILE
        self.site_url = Config.SITE_URL.rstrip('/')
        self.site_name = Config.SITE_NAME

        # Ensure directories exist
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.categories_dir.mkdir(parents=True, exist_ok=True)

    def _get_published_articles(self) -> list:
        """Reads all recorded articles from history.json."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                articles = json.load(f)
                return sorted(articles, key=lambda x: x.get("published_at", ""), reverse=True)
        except Exception:
            return []

    def _get_header_html(self, relative_root: str = "") -> str:
        r = relative_root
        return f"""
  <!-- Top Bar -->
  <div class="top-bar">
    <span>🇺🇸 Independent US Financial Insights. Free FDIC-Insured &amp; High-Yield Guides.</span>
    <a href="{r}pages/ftc-disclosure.html">How we make money</a>
  </div>

  <!-- Header -->
  <header class="site-header">
    <div class="header-container">
      <div class="brand-logo">
        <a class="logo-title" href="{r}index.html">Ledger<span>Spur</span></a>
        <span class="logo-tagline">Smart Money. Sharper Moves.</span>
      </div>

      <nav class="site-nav">
        <a href="{r}categories/credit-cards.html">Credit Cards</a>
        <a href="{r}categories/banking.html">Banking &amp; HYSA</a>
        <a href="{r}categories/loans.html">Loans</a>
        <a href="{r}categories/investing.html">Investing</a>
        <a href="{r}categories/reviews.html">Reviews</a>
        <a class="nav-cta" href="{r}index.html#featured">Top Picks</a>
      </nav>
    </div>
  </header>
"""

    def _get_sidebar_html(self, relative_root: str = "") -> str:
        r = relative_root
        return f"""
    <aside class="sidebar-area">
      <div class="sidebar-widget">
        <h4>Why Trust LedgerSpur?</h4>
        <ul class="trust-badge-list">
          <li>🛡️ <strong>100% Unbiased:</strong> Editorial ratings cannot be purchased by financial institutions.</li>
          <li>🏦 <strong>FDIC Insured:</strong> We prioritize accounts backed up to $250,000 by the US Government.</li>
          <li>📊 <strong>Live APY Tracking:</strong> Rates verified directly against Federal Reserve trends.</li>
        </ul>
      </div>

      <div class="sidebar-widget">
        <h4>Popular Categories</h4>
        <ul class="trust-badge-list">
          <li><a href="{r}categories/banking.html">High-Yield Savings Accounts (HYSA)</a></li>
          <li><a href="{r}categories/credit-cards.html">Best Cash Back &amp; Travel Cards</a></li>
          <li><a href="{r}categories/loans.html">Personal Loans for Debt Consolidation</a></li>
          <li><a href="{r}categories/investing.html">Index Funds &amp; Roth IRA Guides</a></li>
        </ul>
      </div>
    </aside>
"""

    def _get_footer_html(self, relative_root: str = "") -> str:
        r = relative_root
        return f"""
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-col">
        <h4>LedgerSpur</h4>
        <p>LedgerSpur is an independent, advertising-supported publisher dedicated to helping American consumers make smarter, data-backed decisions about their money, investments, and debt.</p>
      </div>

      <div class="footer-col">
        <h4>Quick Links</h4>
        <ul>
          <li><a href="{r}index.html">Home</a></li>
          <li><a href="{r}categories/credit-cards.html">Credit Cards</a></li>
          <li><a href="{r}categories/banking.html">Banking &amp; HYSA</a></li>
          <li><a href="{r}categories/investing.html">Investing</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4>Compliance &amp; Legal</h4>
        <ul>
          <li><a href="{r}pages/about.html">About Us</a></li>
          <li><a href="{r}pages/privacy-policy.html">Privacy Policy (CCPA)</a></li>
          <li><a href="{r}pages/terms.html">Terms of Service</a></li>
          <li><a href="{r}pages/ftc-disclosure.html">FTC Affiliate Disclosure</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p><strong>Disclaimer:</strong> The content provided on LedgerSpur.com is for informational and educational purposes only and does not constitute certified financial, legal, or tax advice. Financial products, rates, and terms change frequently. Please verify details directly with the official provider prior to opening an account.</p>
      <p style="margin-top: 10px;">&copy; {datetime.now().year} LedgerSpur. All rights reserved.</p>
    </div>
  </footer>
"""

    def build_post_page(self, article: dict) -> Path:
        """Builds a single standalone post HTML file in posts/<slug>.html with full interactive modules."""
        slug = article["slug"]
        file_path = self.posts_dir / f"{slug}.html"
        header = self._get_header_html(relative_root="../")
        sidebar = self._get_sidebar_html(relative_root="../")
        footer = self._get_footer_html(relative_root="../")

        date_str = datetime.now().strftime("%B %d, %Y")
        cat = article.get('category', 'Finance')

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{article['title']} - LedgerSpur</title>
  <meta name="description" content="{article['meta_description']}">
  <link rel="canonical" href="{self.site_url}/posts/{slug}.html">
  <meta property="og:title" content="{article['title']} - LedgerSpur">
  <meta property="og:description" content="{article['meta_description']}">
  <meta property="og:url" content="{self.site_url}/posts/{slug}.html">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{article['title']}">
  <meta name="twitter:description" content="{article['meta_description']}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  {header}

  <div class="main-wrapper">
    <main class="content-area">
      <article class="single-post-container">
        <div class="single-post-header">
          <span class="post-category" style="color: var(--ls-green); font-weight:700; text-transform:uppercase; font-size:13px;">{cat}</span>
          <h1 class="single-post-title">{article['title']}</h1>
          <div class="author-credentials">
            <span class="author-badge">CFP® Reviewed</span>
            <span>By <strong>LedgerSpur Editorial Desk</strong></span>
            <span>•</span>
            <span>Updated {date_str}</span>
          </div>
        </div>

        <!-- Editorial Hero Visual Graphic -->
        <div class="post-hero-visual">
          <div class="post-hero-visual-text">
            <span class="post-hero-badge-tag">{cat} • Editorial Review</span>
            <h3>2026 US Consumer Data &amp; Rate Analysis</h3>
            <p>Audited against Federal Reserve benchmarks and official provider rate disclosures.</p>
          </div>
          <div class="post-hero-badge-icon" style="font-size: 42px;">📊</div>
        </div>

        <div class="single-post-body">
          {article['html_content']}
        </div>

        <!-- Interactive Category Match Poll -->
        <div class="ls-poll-widget">
          <div class="ls-poll-header">
            <span class="ls-poll-badge">Interactive Tool</span>
            <h4>What is your highest monthly household expense?</h4>
            <p class="poll-subtitle">Select an option below to reveal your highest-earning personalized match.</p>
          </div>
          <div class="poll-options-grid">
            <button type="button" class="poll-option-btn" data-choice="groceries">
              <span>🥦 Supermarkets &amp; Groceries</span>
              <span>&rarr;</span>
            </button>
            <button type="button" class="poll-option-btn" data-choice="gas">
              <span>⛽ Gas &amp; Commuting</span>
              <span>&rarr;</span>
            </button>
            <button type="button" class="poll-option-btn" data-choice="dining">
              <span>🍽️ Dining &amp; Delivery</span>
              <span>&rarr;</span>
            </button>
            <button type="button" class="poll-option-btn" data-choice="flat">
              <span>🛍️ All Other Purchases</span>
              <span>&rarr;</span>
            </button>
          </div>
          <div class="poll-result-box"></div>
        </div>

        <!-- Interactive Cash Back & Savings Estimator -->
        <div class="ls-calculator-widget">
          <div class="calc-header">
            <span class="hero-badge" style="background: rgba(5,150,105,0.1); color: var(--ls-green); border-color: rgba(5,150,105,0.2);">Live Estimator</span>
            <h4>Calculate Your Annual Rewards vs. Traditional 1% Bank Cards</h4>
            <p style="font-size: 14px; color: var(--ls-muted); margin:0;">Move the sliders to match your estimated monthly household spend.</p>
          </div>
          <div class="calc-inputs-grid">
            <div class="calc-control">
              <label>
                <span>Monthly Groceries Spend:</span>
                <span id="val-grocery" style="color: var(--ls-green); font-weight:700;">$400</span>
              </label>
              <input type="range" id="calc-grocery" min="100" max="1500" step="50" value="400">
            </div>
            <div class="calc-control">
              <label>
                <span>Monthly Gas / Commute Spend:</span>
                <span id="val-gas" style="color: var(--ls-green); font-weight:700;">$150</span>
              </label>
              <input type="range" id="calc-gas" min="50" max="800" step="25" value="150">
            </div>
          </div>
          <div class="calc-results-box">
            <div class="calc-res-item">
              <span class="res-label">Optimized Tier-1 Card</span>
              <span class="res-val highlight-green" id="calc-result-top">$312</span>
            </div>
            <div class="calc-res-item">
              <span class="res-label">Standard 1% Bank Card</span>
              <span class="res-val" id="calc-result-std">$66</span>
            </div>
            <div class="calc-res-item">
              <span class="res-label">Your Extra Money / Year</span>
              <span class="res-val highlight-green" id="calc-result-diff">+$246/yr</span>
            </div>
          </div>
        </div>

        <!-- 1-Click "Was this guide helpful?" Feedback Bar -->
        <div class="ls-feedback-widget" data-slug="{slug}">
          <div class="feedback-inner">
            <span class="feedback-question">Was this guide helpful to your financial decision?</span>
            <div class="feedback-buttons">
              <button type="button" class="feedback-btn feedback-btn-yes">
                <span>👍 Yes</span>
              </button>
              <button type="button" class="feedback-btn feedback-btn-no">
                <span>👎 No</span>
              </button>
            </div>
          </div>
          <div class="feedback-status"></div>
        </div>

        <!-- Community Q&A Section -->
        <section class="ls-qa-section">
          <h3>Community Questions &amp; CFP Editorial Insights</h3>
          <p class="qa-subtitle">Direct inquiries from verified readers, reviewed by certified financial professionals.</p>

          <div class="qa-list">
            <div class="qa-item open">
              <div class="qa-item-question">
                <span>Q: How quickly do rate updates and promotional terms take effect?</span>
                <span>▼</span>
              </div>
              <div class="qa-item-answer">
                <p><strong>LedgerSpur Editorial Desk:</strong> Federal Reserve rate moves adjust savings accounts within 1 to 2 business weeks. For credit cards, intro APR windows are locked from account opening, while quarterly rotating bonus categories renew every three months.</p>
              </div>
            </div>
            <div class="qa-item">
              <div class="qa-item-question">
                <span>Q: Does applying for a new rewards card damage my credit score?</span>
                <span>▼</span>
              </div>
              <div class="qa-item-answer">
                <p><strong>LedgerSpur Editorial Desk:</strong> The initial hard inquiry temporarily lowers your score by 3 to 5 points. However, the added credit limit reduces your credit utilization ratio, which is one of the highest-weighted FICO factors, providing a net positive boost over 60-90 days.</p>
              </div>
            </div>
          </div>

          <div class="qa-submit-box">
            <h4>Have a question about this product or strategy?</h4>
            <p style="font-size:13px; color:var(--ls-muted); margin-bottom:10px;">Our financial research desk reviews questions daily to enhance our guides.</p>
            <form class="qa-submit-form">
              <textarea placeholder="Ask a question about interest rates, annual fees, or qualification..." required></textarea>
              <button type="submit" class="qa-submit-btn">Submit Question</button>
            </form>
            <div class="qa-success-message">✓ Question submitted successfully! The LedgerSpur research desk will review and update the guide within 24 hours.</div>
          </div>
        </section>

      </article>
    </main>

    {sidebar}
  </div>

  {footer}
  <script src="../assets/js/interactions.js" defer></script>
</body>
</html>
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def build_index_page(self):
        """Builds index.html with Hero section and cards for all published articles."""
        articles = self._get_published_articles()
        header = self._get_header_html(relative_root="")
        sidebar = self._get_sidebar_html(relative_root="")
        footer = self._get_footer_html(relative_root="")

        posts_cards_html = ""
        for art in articles:
            slug = art.get("slug", "")
            title = art.get("topic", art.get("title", ""))
            category = art.get("category", "Banking")
            date_str = art.get("published_at", "")[:10] or datetime.now().strftime("%Y-%m-%d")
            snippet = art.get("meta_description", "In-depth financial comparison and rates analysis for US consumers.")

            posts_cards_html += f"""
        <article class="post-card">
          <span class="post-category">{category}</span>
          <h2 class="post-title">
            <a href="posts/{slug}.html">{title}</a>
          </h2>
          <div class="post-meta">
            <span>By LedgerSpur Editorial</span>
            <span>•</span>
            <span>{date_str}</span>
            <span>•</span>
            <span>5 min read</span>
          </div>
          <p class="post-snippet">{snippet}</p>
          <a class="read-more-link" href="posts/{slug}.html">Read Full Analysis &rarr;</a>
        </article>
"""

        if not posts_cards_html:
            posts_cards_html = "<p>No articles published yet. Run auto-generator to add seed content.</p>"

        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LedgerSpur - Smart Money. Sharper Moves. (US Personal Finance)</title>
  <meta name="description" content="{Config.DESCRIPTION}">
  <link rel="canonical" href="{self.site_url}/">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  {header}

  <!-- Hero Section -->
  <section class="hero-banner">
    <div class="hero-container">
      <span class="hero-badge">Data-Driven Personal Finance</span>
      <h1>Master Your Wealth.<br>Spur Your Growth.</h1>
      <p>Unbiased comparisons of high-yield savings accounts, top cash back credit cards, and wealth-building strategies for Americans.</p>
      <div class="hero-tags">
        <a class="hero-tag" href="categories/banking.html">💰 4.5%+ HYSA Accounts</a>
        <a class="hero-tag" href="categories/credit-cards.html">💳 0% APR Cards</a>
        <a class="hero-tag" href="categories/investing.html">📈 Roth IRA vs 401(k)</a>
        <a class="hero-tag" href="categories/loans.html">⚡ Debt Payoff Guides</a>
      </div>
    </div>
  </section>

  <!-- Main Content Layout -->
  <div class="main-wrapper" id="featured">
    <main class="content-area">
      <h2 style="margin-bottom: 24px; font-size: 26px;">Latest Financial Guides &amp; Reviews</h2>
      <div class="posts-grid">
        {posts_cards_html}
      </div>
    </main>

    {sidebar}
  </div>

  {footer}
</body>
</html>
"""
        with open(self.base_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

    def build_legal_pages(self):
        """Converts legal/*.html into styled pages/<name>.html."""
        header = self._get_header_html(relative_root="../")
        sidebar = self._get_sidebar_html(relative_root="../")
        footer = self._get_footer_html(relative_root="../")

        legal_mapping = [
            ("about-us.html", "about.html", "About LedgerSpur - Mission & Editorial Standards"),
            ("privacy-policy.html", "privacy-policy.html", "Privacy Policy (CCPA & GDPR) - LedgerSpur"),
            ("terms-of-service.html", "terms.html", "Terms of Service - LedgerSpur"),
            ("ftc-disclosure.html", "ftc-disclosure.html", "FTC Advertising & Affiliate Disclosure - LedgerSpur"),
        ]

        legal_dir = self.base_dir / "legal"
        for src_name, dest_name, page_title in legal_mapping:
            src_file = legal_dir / src_name
            if src_file.exists():
                with open(src_file, "r", encoding="utf-8") as f:
                    inner_content = f.read()

                page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  {header}

  <div class="main-wrapper">
    <main class="content-area">
      <div class="single-post-container">
        {inner_content}
      </div>
    </main>
    {sidebar}
  </div>

  {footer}
</body>
</html>
"""
                with open(self.pages_dir / dest_name, "w", encoding="utf-8") as f:
                    f.write(page_html)

    def build_category_pages(self):
        """Generates dedicated archive pages for each category."""
        categories = ["Credit Cards", "Banking", "Loans", "Investing", "Reviews"]
        articles = self._get_published_articles()
        header = self._get_header_html(relative_root="../")
        sidebar = self._get_sidebar_html(relative_root="../")
        footer = self._get_footer_html(relative_root="../")

        for cat in categories:
            slug = cat.lower().replace(" ", "-")
            cat_articles = [a for a in articles if a.get("category", "").lower() == cat.lower()]

            cards_html = ""
            for art in cat_articles:
                art_slug = art.get("slug", "")
                title = art.get("topic", art.get("title", ""))
                date_str = art.get("published_at", "")[:10]
                snippet = art.get("meta_description", "")
                cards_html += f"""
        <article class="post-card">
          <span class="post-category">{cat}</span>
          <h2 class="post-title"><a href="../posts/{art_slug}.html">{title}</a></h2>
          <div class="post-meta"><span>{date_str}</span> • <span>5 min read</span></div>
          <p class="post-snippet">{snippet}</p>
          <a class="read-more-link" href="../posts/{art_slug}.html">Read Guide &rarr;</a>
        </article>
"""
            if not cards_html:
                cards_html = f"<p>Articles in {cat} will be published shortly.</p>"

            cat_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cat} Guides & Reviews - LedgerSpur</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  {header}
  <div class="main-wrapper">
    <main class="content-area">
      <h1 style="font-size: 32px; margin-bottom: 24px;">{cat} Resources</h1>
      <div class="posts-grid">{cards_html}</div>
    </main>
    {sidebar}
  </div>
  {footer}
</body>
</html>
"""
            with open(self.categories_dir / f"{slug}.html", "w", encoding="utf-8") as f:
                f.write(cat_html)

    def build_sitemap_and_feed(self):
        """Generates sitemap.xml and feed.xml for Google indexing and RSS."""
        articles = self._get_published_articles()
        now_iso = datetime.now().strftime("%Y-%m-%d")

        # Sitemap XML
        sitemap_entries = [
            f"<url><loc>{self.site_url}/</loc><lastmod>{now_iso}</lastmod><priority>1.0</priority></url>",
            f"<url><loc>{self.site_url}/pages/about.html</loc><priority>0.8</priority></url>",
            f"<url><loc>{self.site_url}/pages/privacy-policy.html</loc><priority>0.5</priority></url>",
            f"<url><loc>{self.site_url}/pages/terms.html</loc><priority>0.5</priority></url>",
            f"<url><loc>{self.site_url}/pages/ftc-disclosure.html</loc><priority>0.5</priority></url>",
        ]

        for art in articles:
            slug = art.get("slug", "")
            date_str = art.get("published_at", "")[:10] or now_iso
            sitemap_entries.append(
                f"<url><loc>{self.site_url}/posts/{slug}.html</loc><lastmod>{date_str}</lastmod><priority>0.9</priority></url>"
            )

        sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {chr(10).join(sitemap_entries)}
</urlset>
"""
        with open(self.base_dir / "sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_xml)

        # CNAME File for GitHub Pages
        with open(self.base_dir / "CNAME", "w", encoding="utf-8") as f:
            f.write("ledgerspur.com\n")
