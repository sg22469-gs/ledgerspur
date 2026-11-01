import json
from datetime import datetime
from pathlib import Path
from config import Config

class StateManager:
    def __init__(self):
        self.topics_file = Config.TOPICS_FILE
        self.history_file = Config.HISTORY_FILE

    def get_next_pending_topic(self) -> dict | None:
        """Returns the next pending topic from topics.json."""
        if not self.topics_file.exists():
            return None
        with open(self.topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        for t in topics:
            if t.get("status") == "pending":
                return t
        return None

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
