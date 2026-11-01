import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    BASE_DIR = BASE_DIR

    # 1. Branding & Site Identity
    SITE_NAME = os.getenv("SITE_NAME", "LedgerSpur")
    SITE_URL = os.getenv("SITE_URL", "https://ledgerspur.com")
    TAGLINE = "Smart Money. Sharper Moves."
    DESCRIPTION = "Unbiased US personal finance guides, high-yield savings reviews, credit card rewards, and wealth-building strategies."
    LOCALE = "en-US"
    NICHE = "US Personal Finance, Credit Cards, High-Yield Banking & Wealth Strategy"

    # 2. Gemini AI Engine
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    # 3. Static Site Directory Layout
    POSTS_DIR = BASE_DIR / "posts"
    CATEGORIES_DIR = BASE_DIR / "categories"
    PAGES_DIR = BASE_DIR / "pages"
    ASSETS_DIR = BASE_DIR / "assets"
    TOPICS_FILE = BASE_DIR / "topics.json"
    HISTORY_FILE = BASE_DIR / "history.json"
