import argparse
import sys
from modules.content_generator import ContentGenerator
from modules.site_builder import SiteBuilder
from modules.state_manager import StateManager
from config import Config

def run_single_pipeline(topic_data: dict = None):
    state_mgr = StateManager()
    site_builder = SiteBuilder()

    if not topic_data:
        topic_data = state_mgr.get_next_pending_topic()

    if not topic_data:
        print("[*] No pending topics found in topics.json!")
        return

    print(f"\n[+] Processing Topic #{topic_data.get('id')}: '{topic_data.get('topic')}'")
    print(f"[+] Category: {topic_data.get('category')} | Target Keyword: {topic_data.get('target_keyword')}")

    # 1. Generate Article
    print("[+] Invoking Gemini AI Content Engine for LedgerSpur...")
    generator = ContentGenerator()
    article = generator.generate_article(topic_data)
    print(f"[+] Article generated successfully: {len(article['html_content'])} characters.")

    # 2. Build Standalone Post Page
    post_file = site_builder.build_post_page(article)
    print(f"[+] Standalone post generated: {post_file}")

    # 3. Update State
    post_url = f"{Config.SITE_URL}/posts/{article['slug']}.html"
    state_mgr.mark_topic_completed(topic_data.get("id"), post_url=post_url, article_data=article)
    print(f"[+] Topic #{topic_data.get('id')} recorded in state manager.")

    # 4. Rebuild Index, Categories & Sitemap
    print("[+] Rebuilding homepage, category pages, legal pages and sitemap...")
    site_builder.build_index_page()
    site_builder.build_category_pages()
    site_builder.build_legal_pages()
    site_builder.build_sitemap_and_feed()
    print("[+] Site successfully updated!")

def rebuild_all():
    print("[+] Rebuilding all static site pages from current history...")
    builder = SiteBuilder()
    builder.build_index_page()
    builder.build_category_pages()
    builder.build_legal_pages()
    builder.build_sitemap_and_feed()
    print("[+] Complete site build finished!")

def main():
    parser = argparse.ArgumentParser(description="LedgerSpur Standalone Static Site Engine")
    parser.add_argument("--run-once", action="store_true", help="Generate next pending article and update site")
    parser.add_argument("--seed", type=int, default=0, help="Generate N flagship seed articles")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild homepage, categories, legal pages & sitemap")
    parser.add_argument("--list", action="store_true", help="List all pending topics")

    args = parser.parse_args()

    if args.list:
        state_mgr = StateManager()
        import json
        with open(state_mgr.topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        for t in topics:
            status_symbol = "[✓]" if t.get("status") == "published" else "[ ]"
            print(f"{status_symbol} #{t['id']} [{t['category']}] {t['topic']}")
        return

    if args.rebuild:
        rebuild_all()
        return

    if args.seed > 0:
        print(f"[*] Generating {args.seed} flagship seed articles for LedgerSpur...")
        state_mgr = StateManager()
        for i in range(args.seed):
            topic = state_mgr.get_next_pending_topic()
            if not topic:
                break
            run_single_pipeline(topic)
        print("\n[*] Seed generation complete! Full website is ready.")
        return

    # Default: Run once
    run_single_pipeline()

if __name__ == "__main__":
    main()
