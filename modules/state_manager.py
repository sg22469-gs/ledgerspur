import json
from datetime import datetime
from pathlib import Path
from config import Config
from modules.topic_guard import TopicGuard

class StateManager:
    def __init__(self):
        self.topics_file = Config.TOPICS_FILE
        self.history_file = Config.HISTORY_FILE
        self.guard = TopicGuard()

    def get_next_pending_topic(self, bypass_48h: bool = False) -> dict | None:
        """Returns the next pending topic that satisfies 48h AI evaluation."""
        return self.guard.get_next_publishable_topic(bypass_48h=bypass_48h)

    def mark_topic_completed(self, topic_id: int, post_url: str = "", article_data: dict = None):
        """Marks a topic as completed and records timestamp and metadata."""
        if not self.topics_file.exists():
            return
        with open(self.topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        
        target = None
        for t in topics:
            if t.get("id") == topic_id:
                t["status"] = "published"
                t["published_at"] = datetime.now().isoformat()
                t["url"] = post_url
                if article_data:
                    t["slug"] = article_data.get("slug")
                    t["meta_description"] = article_data.get("meta_description")
                    t["title"] = article_data.get("title")
                target = t
                break

        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(topics, f, indent=2)

        # Log in history
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        if target:
            # Avoid duplicate in history
            history = [h for h in history if h.get("id") != topic_id]
            history.append(target)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)

        # Autonomously maintain permanent 30-topic buffer
        try:
            self.guard.maintain_permanent_buffer(target_pending=30)
        except Exception as e:
            print(f"[!] Topic buffer check: {e}")

    def record_emergency_publication(self, article_data: dict, post_url: str) -> dict:
        """Records an emergency buffer publication in history.json."""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        max_id = max([h.get("id", 0) for h in history]) if history else 0
        entry = {
            "id": max_id + 1,
            "topic": article_data.get("title"),
            "category": article_data.get("category", "Banking"),
            "tags": article_data.get("tags", ["Finance", "Emergency Buffer"]),
            "target_keyword": article_data.get("slug", "").replace("-", " "),
            "intent": "commercial",
            "affiliate_focus": "Top US Providers",
            "status": "published",
            "published_at": datetime.now().isoformat(),
            "url": post_url,
            "slug": article_data.get("slug"),
            "meta_description": article_data.get("meta_description"),
            "title": article_data.get("title"),
            "is_emergency_buffer": True
        }
        history.append(entry)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return entry
