import json
from datetime import datetime
from pathlib import Path
from config import Config

class BufferManager:
    """
    Manages an Emergency Pre-Generated Post Buffer Pool (buffer_pool.json).
    Guarantees zero publishing interruptions when third-party AI APIs experience outages,
    rate-limits, or network failures, and autonomously refills the pool once AI recovers.
    """

    TARGET_BUFFER_SIZE = 5

    EMERGENCY_CATALOG = [
        {
            "topic": "High-Yield Checking Accounts vs High-Yield Savings in 2026: Where Does Your Cash Earn More?",
            "category": "Banking",
            "tags": ["Banking", "Checking", "HYSA", "Savings", "Best Picks"],
            "target_keyword": "high yield checking vs high yield savings 2026",
            "intent": "commercial",
            "affiliate_focus": "SoFi Checking and Savings, Ally Bank, Discover Bank, Capital One 360",
            "projected_rpm": "$55/1000 views"
        },
        {
            "topic": "The Best Business Credit Cards for LLCs & Side Hustles: No Personal Guarantee Options in 2026",
            "category": "Credit Cards",
            "tags": ["Credit Cards", "Business", "Side Hustle", "LLC", "Best Picks"],
            "target_keyword": "best business credit cards no personal guarantee 2026",
            "intent": "commercial",
            "affiliate_focus": "Chase Ink Business Unlimited, Amex Blue Business Plus, Capital One Spark",
            "projected_rpm": "$68/1000 views"
        },
        {
            "topic": "Dollar-Cost Averaging (DCA) vs Lump-Sum Investing: What the Math Proves for 2026",
            "category": "Investing",
            "tags": ["Investing", "Index Funds", "DCA", "Wealth Building", "Guides"],
            "target_keyword": "dca vs lump sum investing math",
            "intent": "informational",
            "affiliate_focus": "Vanguard VTI, Fidelity Investments, Charles Schwab",
            "projected_rpm": "$48/1000 views"
        },
        {
            "topic": "401(k) Loan vs Personal Loan: Which Borrowing Route Protects Your Retirement Wealth?",
            "category": "Loans",
            "tags": ["Loans", "401k", "Personal Loans", "Debt", "Guides"],
            "target_keyword": "401k loan vs personal loan for debt",
            "intent": "informational",
            "affiliate_focus": "SoFi Personal Loans, Upgrade, LightStream",
            "projected_rpm": "$52/1000 views"
        },
        {
            "topic": "Copilot Money vs Monarch Money vs YNAB: The Ultimate 2026 Personal Finance App Showdown",
            "category": "Reviews",
            "tags": ["Reviews", "Budgeting", "Apps", "YNAB", "Monarch Money", "Copilot"],
            "target_keyword": "copilot money vs monarch money vs ynab 2026",
            "intent": "commercial",
            "affiliate_focus": "Monarch Money, YNAB, Empower Personal Dashboard",
            "projected_rpm": "$60/1000 views"
        },
        {
            "topic": "Treasury Bills vs High-Yield CDs in 2026: How to Avoid State Income Tax on Cash Reserves",
            "category": "Banking",
            "tags": ["Banking", "Treasury Bills", "CDs", "Taxes", "Savings"],
            "target_keyword": "treasury bills vs cds state income tax exempt",
            "intent": "commercial",
            "affiliate_focus": "Public.com Treasury, Vanguard, Marcus by Goldman Sachs",
            "projected_rpm": "$58/1000 views"
        },
        {
            "topic": "Flat 2% Cash Back Cards vs Rotating 5% Categories: Which Wallet Strategy Maximizes Returns?",
            "category": "Credit Cards",
            "tags": ["Credit Cards", "Cash Back", "Budgeting", "Best Picks"],
            "target_keyword": "flat 2 percent cash back vs rotating categories",
            "intent": "commercial",
            "affiliate_focus": "Citi Double Cash, Discover it, Chase Freedom Flex, Wells Fargo Active Cash",
            "projected_rpm": "$54/1000 views"
        },
        {
            "topic": "Dividend Aristocrats for Passive Income in 2026: 5 Recession-Resilient Stocks for Beginners",
            "category": "Investing",
            "tags": ["Investing", "Dividends", "Passive Income", "Stocks"],
            "target_keyword": "best dividend aristocrats passive income 2026",
            "intent": "informational",
            "affiliate_focus": "Robinhood, Fidelity, M1 Finance",
            "projected_rpm": "$50/1000 views"
        }
    ]

    def __init__(self):
        self.buffer_file = Config.BASE_DIR / "buffer_pool.json"
        self.history_file = Config.HISTORY_FILE

    def load_buffer(self) -> list:
        if not self.buffer_file.exists():
            return []
        try:
            with open(self.buffer_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_buffer(self, buffer_list: list):
        with open(self.buffer_file, "w", encoding="utf-8") as f:
            json.dump(buffer_list, f, indent=2, ensure_ascii=False)

    def get_count(self) -> int:
        return len(self.load_buffer())

    def get_deficit(self) -> int:
        count = self.get_count()
        return max(0, self.TARGET_BUFFER_SIZE - count)

    def pop_buffer_post(self) -> dict | None:
        """
        Pops and returns an emergency pre-generated article from the buffer pool.
        Atomically updates buffer_pool.json.
        """
        pool = self.load_buffer()
        if not pool:
            return None
        article = pool.pop(0)
        self.save_buffer(pool)
        return article

    def refill_buffer(self, generator=None) -> int:
        """
        Refills the buffer pool back to TARGET_BUFFER_SIZE using the operational AI engine.
        Returns the count of new articles generated and stored.
        """
        deficit = self.get_deficit()
        if deficit <= 0:
            print(f"[*] Emergency buffer pool is full: {self.get_count()}/{self.TARGET_BUFFER_SIZE} articles ready.")
            return 0

        print(f"[+] Emergency buffer replenishment triggered: Deficit of {deficit} article(s).")
        
        # Avoid topics that are already published or currently in buffer
        published_slugs = set()
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for h in history:
                        published_slugs.add(h.get("slug"))
            except Exception:
                pass

        current_pool = self.load_buffer()
        for art in current_pool:
            published_slugs.add(art.get("slug"))

        if generator is None:
            from modules.content_generator import ContentGenerator
            generator = ContentGenerator()

        added = 0
        for item in self.EMERGENCY_CATALOG:
            if added >= deficit:
                break
            
            # Simple slug check
            import re
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', item["topic"].lower()).strip('-')
            if slug in published_slugs:
                continue

            try:
                print(f"[+] Pre-generating emergency buffer article: '{item['topic']}'...")
                article = generator.generate_article(item)
                article["is_emergency_buffer"] = True
                article["buffered_at"] = datetime.now().isoformat()
                current_pool.append(article)
                published_slugs.add(article["slug"])
                added += 1
                print(f"[✓] Added to emergency buffer pool ({len(current_pool)}/{self.TARGET_BUFFER_SIZE})")
            except Exception as e:
                print(f"[!] Warning: Failed to generate buffer article ({e})")
                continue

        self.save_buffer(current_pool)
        print(f"[+] Buffer replenishment finished. Active reserve: {len(current_pool)}/{self.TARGET_BUFFER_SIZE} articles.")
        return added

    def get_status_report(self) -> dict:
        pool = self.load_buffer()
        return {
            "current_count": len(pool),
            "target_count": self.TARGET_BUFFER_SIZE,
            "deficit": self.get_deficit(),
            "articles": [
                {
                    "title": a.get("title"),
                    "category": a.get("category"),
                    "slug": a.get("slug"),
                    "buffered_at": a.get("buffered_at")
                }
                for a in pool
            ]
        }
