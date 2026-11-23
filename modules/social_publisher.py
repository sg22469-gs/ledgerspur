import json
import os
import re
import time
from datetime import datetime
from email.utils import formatdate
from pathlib import Path
from config import Config

class SocialPublisher:
    """
    Autonomous Social Media Distribution & Trailer Engine for LedgerSpur.
    Generates platform-specific teaser trailers (X/Twitter, LinkedIn, Reddit, Pinterest)
    for every published article, maintains a version-controlled social outbox,
    and supports multi-channel webhook/RSS dispatching.
    """

    def __init__(self):
        self.site_url = Config.SITE_URL.rstrip('/')
        self.site_name = Config.SITE_NAME
        self.outbox_file = getattr(Config, "SOCIAL_OUTBOX_FILE", Config.BASE_DIR / "social_outbox.json")
        self.feed_file = getattr(Config, "FEED_FILE", Config.BASE_DIR / "feed.xml")
        self.social_feed_file = getattr(Config, "SOCIAL_FEED_FILE", Config.BASE_DIR / "social_feed.json")

        self.webhook_url = getattr(Config, "SOCIAL_WEBHOOK_URL", os.getenv("SOCIAL_WEBHOOK_URL", ""))
        self.discord_webhook = getattr(Config, "DISCORD_WEBHOOK_URL", os.getenv("DISCORD_WEBHOOK_URL", ""))
        self.telegram_token = getattr(Config, "TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
        self.telegram_chat = getattr(Config, "TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_CHAT_ID", ""))

    def _get_og_image_url(self, category: str) -> str:
        cat_lower = (category or "").lower()
        if "card" in cat_lower:
            fn = "og-credit-cards.png"
        elif "bank" in cat_lower or "hysa" in cat_lower or "saving" in cat_lower or "cd" in cat_lower or "checking" in cat_lower:
            fn = "og-banking.png"
        elif "invest" in cat_lower or "roth" in cat_lower or "401" in cat_lower or "stock" in cat_lower or "fund" in cat_lower or "ira" in cat_lower:
            fn = "og-investing.png"
        elif "loan" in cat_lower or "debt" in cat_lower or "mortgage" in cat_lower:
            fn = "og-loans.png"
        elif "review" in cat_lower or "app" in cat_lower or "vs" in cat_lower:
            fn = "og-reviews.png"
        else:
            fn = "og-default.png"
        return f"{self.site_url}/assets/images/{fn}"

    def _get_category_hashtags(self, category: str) -> list:
        cat_lower = (category or "").lower()
        if "card" in cat_lower:
            return ["#CreditCards", "#CashBack", "#TravelHacks", "#PersonalFinance"]
        elif "bank" in cat_lower or "saving" in cat_lower or "hysa" in cat_lower:
            return ["#HYSA", "#Savings", "#SmartMoney", "#PersonalFinance", "#Banking"]
        elif "invest" in cat_lower or "roth" in cat_lower or "401" in cat_lower:
            return ["#Investing", "#RothIRA", "#WealthBuilding", "#FinancialFreedom"]
        elif "loan" in cat_lower or "debt" in cat_lower:
            return ["#DebtFree", "#MortgageRates", "#DebtPayoff", "#MoneyManagement"]
        elif "review" in cat_lower or "app" in cat_lower:
            return ["#Fintech", "#Budgeting", "#MoneyApps", "#AppReview"]
        return ["#PersonalFinance", "#SmartMoney", "#Wealth", "#MoneyTips"]

    def generate_social_trailers(self, article: dict) -> dict:
        """
        Creates platform-specific teasers designed for high-converting click-throughs:
        - Twitter / X Teaser (curiosity hook + data points + link)
        - LinkedIn Executive Teaser (high-income wealth strategy angle)
        - Reddit Discussion Starter (community-focused question + breakdown)
        - Pinterest Pin Teaser (rich search keyword description)
        """
        title = article.get("title", article.get("topic", "")).strip()
        slug = article.get("slug", "")
        category = article.get("category", "Banking")
        meta_desc = article.get("meta_description", "").strip()
        post_url = f"{self.site_url}/posts/{slug}.html"
        image_url = self._get_og_image_url(category)
        hashtags = self._get_category_hashtags(category)
        tag_str = " ".join(hashtags[:3])

        # 1. Twitter / X Trailer (Hook + Proof + CTA)
        clean_desc = meta_desc if len(meta_desc) < 130 else meta_desc[:127] + "..."
        twitter_copy = f"""🚨 {title}

💡 {clean_desc}

📊 Full CFP-reviewed breakdown, rates comparison & interactive calculator:
🔗 {post_url}

{tag_str}"""

        # 2. LinkedIn Executive Teaser
        linkedin_copy = f"""Are you maximizing your capital efficiency in 2026?

We just published an in-depth financial evaluation:
👉 "{title}"

Key Takeaways for High Earners & Investors:
• Why outdated traditional banking/credit assumptions cost you thousands in lost yield
• Direct feature-by-feature benchmark based on empirical FDIC & IRS regulations
• Interactive calculator to model your exact return

Read the complete guide on LedgerSpur:
{post_url}

#WealthManagement #PersonalFinance #FinancialStrategy #Investing"""

        # 3. Reddit Discussion Starter (r/personalfinance, r/CreditCards, r/financialindependence)
        reddit_title = f"Deep Dive Analysis: {title} - Here is what the numbers prove"
        reddit_body = f"""Hey everyone,

With rates and rules shifting, there's been a lot of debate around this topic. We ran a full empirical comparison analyzing the math, fee structures, and fine print:

**Summary of findings:**
{meta_desc}

For those interested in the full side-by-side comparison tables, interactive calculator, and CFP notes:
{post_url}

Would love to hear how others are handling this in their own portfolios right now."""

        # 4. Pinterest Pin Copy
        pin_title = f"{title} | LedgerSpur Financial Guide"
        pin_description = f"{meta_desc} Discover the best financial moves for Americans in 2026. Click through to read the full guide, rate comparisons, and free interactive calculator on LedgerSpur. {tag_str}"

        return {
            "slug": slug,
            "title": title,
            "category": category,
            "url": post_url,
            "image_url": image_url,
            "twitter": {
                "text": twitter_copy,
                "character_count": len(twitter_copy),
                "hashtags": hashtags[:4]
            },
            "linkedin": {
                "text": linkedin_copy
            },
            "reddit": {
                "title": reddit_title,
                "body": reddit_body
            },
            "pinterest": {
                "title": pin_title,
                "description": pin_description
            }
        }

    def _read_outbox(self) -> list:
        if not self.outbox_file.exists():
            return []
        try:
            with open(self.outbox_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_outbox(self, items: list):
        with open(self.outbox_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    def queue_trailer(self, article: dict) -> dict:
        """Queues a social trailer for the given article if not already present."""
        slug = article.get("slug", "")
        if not slug:
            return {}

        outbox = self._read_outbox()
        existing = next((x for x in outbox if x.get("slug") == slug), None)
        if existing:
            return existing

        trailers = self.generate_social_trailers(article)
        entry = {
            "id": f"soc_{slug[:25]}_{int(time.time())}",
            "slug": slug,
            "title": trailers["title"],
            "category": trailers["category"],
            "url": trailers["url"],
            "image_url": trailers["image_url"],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "queued",
            "dispatched_at": None,
            "trailers": {
                "twitter": trailers["twitter"],
                "linkedin": trailers["linkedin"],
                "reddit": trailers["reddit"],
                "pinterest": trailers["pinterest"]
            }
        }

        outbox.insert(0, entry) # Most recent first
        self._write_outbox(outbox)
        print(f"[+] Social trailer queued in outbox for '{trailers['title']}'")
        return entry

    def dispatch_trailers(self, max_items: int = 3) -> dict:
        """
        Dispatches queued trailers via available webhooks (Discord, Telegram, Zapier/Make).
        If no webhooks are configured, maintains queued state safely without failing.
        """
        outbox = self._read_outbox()
        queued = [x for x in outbox if x.get("status") == "queued"]

        results = {
            "total_queued": len(queued),
            "dispatched_count": 0,
            "channels_used": [],
            "skipped_no_webhook": False
        }

        if not queued:
            print("[*] No pending social trailers to dispatch.")
            return results

        has_any_channel = bool(self.webhook_url or self.discord_webhook or (self.telegram_token and self.telegram_chat))
        if not has_any_channel:
            results["skipped_no_webhook"] = True
            print("[i] Social trailers ready in social_outbox.json (No external webhooks configured yet in .env).")
            return results

        import requests

        to_process = queued[:max_items]
        for item in to_process:
            dispatched = False
            title = item["title"]
            url = item["url"]
            img = item["image_url"]
            desc = item["trailers"]["twitter"]["text"]

            # 1. Discord Webhook
            if self.discord_webhook:
                try:
                    payload = {
                        "username": "LedgerSpur Publisher",
                        "avatar_url": f"{self.site_url}/assets/images/logo.png",
                        "embeds": [
                            {
                                "title": f"🚀 New Post: {title}",
                                "url": url,
                                "description": desc,
                                "color": 1095961, # Emerald #10B981
                                "image": {"url": img},
                                "footer": {"text": "LedgerSpur • Smart Money. Sharper Moves."}
                            }
                        ]
                    }
                    resp = requests.post(self.discord_webhook, json=payload, timeout=8)
                    if resp.status_code in (200, 204):
                        dispatched = True
                        if "Discord" not in results["channels_used"]:
                            results["channels_used"].append("Discord")
                except Exception as e:
                    print(f"[!] Discord dispatch error: {e}")

            # 2. Generic Social Automation Webhook (Make / Zapier / Buffer)
            if self.webhook_url:
                try:
                    resp = requests.post(self.webhook_url, json=item, timeout=8)
                    if resp.status_code in (200, 201, 204):
                        dispatched = True
                        if "Generic Webhook" not in results["channels_used"]:
                            results["channels_used"].append("Generic Webhook")
                except Exception as e:
                    print(f"[!] Webhook dispatch error: {e}")

            # 3. Telegram Channel Broadcast
            if self.telegram_token and self.telegram_chat:
                try:
                    tg_api = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
                    caption = f"<b>{title}</b>\n\n{item['trailers']['twitter']['text']}"
                    tg_payload = {
                        "chat_id": self.telegram_chat,
                        "photo": img,
                        "caption": caption[:1024],
                        "parse_mode": "HTML"
                    }
                    resp = requests.post(tg_api, json=tg_payload, timeout=8)
                    if resp.status_code == 200:
                        dispatched = True
                        if "Telegram" not in results["channels_used"]:
                            results["channels_used"].append("Telegram")
                except Exception as e:
                    print(f"[!] Telegram dispatch error: {e}")

            if dispatched:
                item["status"] = "dispatched"
                item["dispatched_at"] = datetime.utcnow().isoformat() + "Z"
                results["dispatched_count"] += 1

        self._write_outbox(outbox)
        print(f"[✓] Dispatched {results['dispatched_count']} social trailer(s) to {', '.join(results['channels_used'])}.")
        return results

    def generate_feeds(self, articles: list):
        """
        Generates production-grade RSS 2.0 (feed.xml) and JSON Feed 1.1 (social_feed.json)
        with media enclosures so social schedulers (Buffer, Hootsuite, IFTTT, Zapier)
        can auto-syndicate articles with zero custom code.
        """
        now_rfc822 = formatdate(time.time(), usegmt=True)

        # 1. RSS 2.0 Feed with Media Enclosures
        rss_items = []
        for art in articles[:30]:
            slug = art.get("slug", "")
            title = art.get("title", art.get("topic", "")).strip()
            desc = art.get("meta_description", "").strip()
            cat = art.get("category", "Banking")
            url = f"{self.site_url}/posts/{slug}.html"
            img_url = self._get_og_image_url(cat)
            pub_date = formatdate(time.time(), usegmt=True)

            rss_items.append(f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <description><![CDATA[{desc}]]></description>
      <category>{cat}</category>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{img_url}" length="45000" type="image/png" />
    </item>""")

        rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{self.site_name} - Smart Money. Sharper Moves.</title>
    <link>{self.site_url}</link>
    <description>Unbiased US personal finance guides, high-yield savings reviews, and wealth-building strategies.</description>
    <language>en-US</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
    <atom:link href="{self.site_url}/feed.xml" rel="self" type="application/rss+xml" />
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
        with open(self.feed_file, "w", encoding="utf-8") as f:
            f.write(rss_xml)

        # 2. JSON Feed 1.1 for No-Code Automations
        json_items = []
        for art in articles[:30]:
            slug = art.get("slug", "")
            title = art.get("title", art.get("topic", "")).strip()
            desc = art.get("meta_description", "").strip()
            cat = art.get("category", "Banking")
            url = f"{self.site_url}/posts/{slug}.html"
            img_url = self._get_og_image_url(cat)

            json_items.append({
                "id": url,
                "url": url,
                "title": title,
                "summary": desc,
                "image": img_url,
                "tags": [cat, "Finance", "LedgerSpur"],
                "date_published": datetime.utcnow().isoformat() + "Z"
            })

        json_feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"{self.site_name} - Social Distribution Feed",
            "home_page_url": self.site_url,
            "feed_url": f"{self.site_url}/social_feed.json",
            "description": "Automated trailer feed for social media syndication.",
            "icon": f"{self.site_url}/assets/images/logo.png",
            "favicon": f"{self.site_url}/assets/images/logo.png",
            "items": json_items
        }

        with open(self.social_feed_file, "w", encoding="utf-8") as f:
            json.dump(json_feed, f, indent=2, ensure_ascii=False)

        print(f"[+] Successfully generated RSS Feed ({self.feed_file.name}) and JSON Feed ({self.social_feed_file.name}).")
