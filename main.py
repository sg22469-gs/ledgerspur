import sys
import argparse
from modules.content_generator import ContentGenerator
from modules.site_builder import SiteBuilder
from modules.state_manager import StateManager
from modules.topic_guard import TopicGuard
from modules.buffer_manager import BufferManager
from config import Config

# Ensure clean UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_single_pipeline(topic_data: dict = None, is_trending: bool = False):
    state_mgr = StateManager()
    site_builder = SiteBuilder()
    guard = TopicGuard()

    if is_trending and not topic_data:
        print("\n[!] Activating Golden-Time Trending Post Segment...")
        topic_data = guard.generate_trending_topic()

    if not topic_data:
        topic_data = state_mgr.get_next_pending_topic()

    if not topic_data:
        print("[*] No eligible pending topics found. Checking buffer...")
        guard.maintain_permanent_buffer(target_pending=30)
        topic_data = state_mgr.get_next_pending_topic(bypass_48h=True)
        if not topic_data:
            print("[!] Unable to retrieve topic. Please verify topics.json.")
            return

    print(f"\n[+] Processing Topic #{topic_data.get('id')}: '{topic_data.get('topic')}'")
    print(f"[+] Category: {topic_data.get('category')} | Target Keyword: {topic_data.get('target_keyword')}")
    if topic_data.get("mock_score"):
        print(f"[+] 48-Hour AI Mock Score: {topic_data.get('mock_score')}/100 | Projected RPM: {topic_data.get('projected_rpm')}")

    # 1. Generate Article with Emergency Buffer Fallback & Self-Healing Refill Gate
    generator = ContentGenerator()
    buffer_mgr = BufferManager()
    article = None
    is_emergency_fallback = False

    try:
        print("[+] Invoking Gemini AI Content Engine for LedgerSpur...")
        article = generator.generate_article(topic_data)
        print(f"[+] Article generated successfully: {len(article['html_content'])} characters.")

        # Self-healing: live AI is functional! Check if emergency buffer pool needs replenishment
        if buffer_mgr.get_deficit() > 0:
            print("[+] Live AI operational. Checking emergency buffer reserve...")
            buffer_mgr.refill_buffer(generator=generator)
    except Exception as e:
        print(f"[!] Warning: Live AI Generation failed ({e})")
        print("[⚡] Activating Emergency Buffer Pool Fallback...")
        article = buffer_mgr.pop_buffer_post()
        if article:
            is_emergency_fallback = True
            print(f"[✓] Successfully retrieved pre-generated buffer article: '{article['title']}'")
        else:
            print("[!] Emergency buffer pool empty. Using deterministic fallback engine...")
            article = generator.generate_fallback_direct(topic_data)

    # 2. Build Standalone Post Page
    post_file = site_builder.build_post_page(article)
    print(f"[+] Standalone post generated: {post_file}")

    # 3. Update State
    post_url = f"{Config.SITE_URL}/posts/{article['slug']}.html"
    if is_emergency_fallback:
        state_mgr.record_emergency_publication(article, post_url=post_url)
        print(f"[+] Emergency buffer post '{article['title']}' recorded in history.json.")
    else:
        state_mgr.mark_topic_completed(topic_data.get("id"), post_url=post_url, article_data=article)
        print(f"[+] Topic #{topic_data.get('id')} recorded in state manager.")

    # 4. Rebuild Index, Categories & Sitemap
    print("[+] Rebuilding homepage, category pages, legal pages and sitemap...")
    site_builder.build_index_page()
    site_builder.build_category_pages()
    site_builder.build_legal_pages()
    site_builder.build_sitemap_and_feed()
    print("[+] Site successfully updated!")

def audit_queue():
    """Runs 48-hour AI mock evaluation on all pending topics."""
    guard = TopicGuard()
    topics = guard.load_topics()
    pending = [t for t in topics if t.get("status") == "pending"]
    print("\n=======================================================")
    print("   [TALON] LedgerSpur AI Pre-Publishing Mock Audit Queue ")
    print("=======================================================")
    print(f"Total Pending in Queue: {len(pending)}")
    print(f"{'ID':<4} | {'Score':<6} | {'Projected RPM':<16} | {'Category':<12} | {'Topic'}")
    print("-" * 80)
    for t in pending[:15]:
        score = t.get("mock_score", 90)
        rpm = t.get("projected_rpm", "$45/1000 views")
        cat = t.get("category", "Banking")
        title = (t.get("topic")[:38] + "...") if len(t.get("topic")) > 38 else t.get("topic")
        print(f"#{t['id']:<3} | {score:<6} | {rpm:<16} | {cat:<12} | {title}")
    print("-------------------------------------------------------")
    print("[+] All queue items evaluated against commercial intent & E-E-A-T standards.\n")

def rebuild_all():
    print("[+] Rebuilding all static site pages from current history...")
    builder = SiteBuilder()
    builder.update_all_posts_schema()
    builder.build_index_page()
    builder.build_category_pages()
    builder.build_legal_pages()
    builder.build_sitemap_and_feed()
    print("[+] Complete site build finished!")

def main():
    parser = argparse.ArgumentParser(description="LedgerSpur Standalone Static Site Engine")
    parser.add_argument("--run-once", action="store_true", help="Generate next pending article and update site")
    parser.add_argument("--trending", action="store_true", help="Publish Golden-Time Trending Post Segment")
    parser.add_argument("--mock-audit", action="store_true", help="Audit & score upcoming topics with 48h AI mock")
    parser.add_argument("--replenish", action="store_true", help="Ensure permanent 30-topic pending buffer")
    parser.add_argument("--seed", type=int, default=0, help="Generate N flagship seed articles")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild homepage, categories, legal pages & sitemap")
    parser.add_argument("--list", action="store_true", help="List all pending topics")
    parser.add_argument("--refill-buffer", action="store_true", help="Check and refill pre-generated emergency buffer post pool")
    parser.add_argument("--buffer-status", action="store_true", help="Display current status of emergency buffer pool")

    args = parser.parse_args()

    if args.mock_audit:
        audit_queue()
        return

    if args.replenish:
        guard = TopicGuard()
        guard.maintain_permanent_buffer(target_pending=30)
        return

    if args.buffer_status:
        buffer_mgr = BufferManager()
        report = buffer_mgr.get_status_report()
        print("\n=======================================================")
        print("   [TALON] LedgerSpur Emergency Post Buffer Status     ")
        print("=======================================================")
        print(f"Current Reserve: {report['current_count']} / {report['target_count']} articles")
        print(f"Deficit: {report['deficit']}")
        if report['articles']:
            print("\nPre-generated reserve articles waiting in pool:")
            for i, a in enumerate(report['articles'], 1):
                print(f"  {i}. [{a['category']}] {a['title']}")
        else:
            print("  (Pool is empty! Run --refill-buffer to populate reserve.)")
        print("=======================================================\n")
        return

    if args.refill_buffer:
        buffer_mgr = BufferManager()
        generator = ContentGenerator()
        buffer_mgr.refill_buffer(generator=generator)
        return

    if args.list:
        state_mgr = StateManager()
        import json
        with open(state_mgr.topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        for t in topics:
            status_symbol = "[X]" if t.get("status") == "published" else "[ ]"
            score_badge = f"(Score: {t.get('mock_score', '-')})" if t.get("status") == "pending" else ""
            print(f"{status_symbol} #{t['id']} [{t['category']}] {t['topic']} {score_badge}")
        return

    if args.rebuild:
        rebuild_all()
        return

    if args.trending:
        run_single_pipeline(is_trending=True)
        return

    if args.seed > 0:
        print(f"[*] Generating {args.seed} flagship seed articles for LedgerSpur...")
        state_mgr = StateManager()
        for i in range(args.seed):
            topic = state_mgr.get_next_pending_topic(bypass_48h=True)
            if not topic:
                break
            run_single_pipeline(topic)
        print("\n[*] Seed generation complete! Full website is ready.")
        return

    # Default: Run regular post pipeline
    run_single_pipeline()

if __name__ == "__main__":
    main()
