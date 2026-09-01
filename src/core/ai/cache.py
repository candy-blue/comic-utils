import os
import sqlite3
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

class AICacheManager:
    """ SQLite-backed persistent cache for LLM metadata parsing results """

    PROMPT_VERSION = "v1.0"

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            base_dir = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "ComicUtils"
            base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = base_dir / "ai_cache.db"

        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_cache (
                    cache_key TEXT PRIMARY KEY,
                    raw_filename TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def _make_key(self, raw_filename: str, model_name: str) -> str:
        content = f"{raw_filename.strip()}||{model_name.strip()}||{self.PROMPT_VERSION}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, raw_filename: str, model_name: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(raw_filename, model_name)
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT result_json FROM ai_cache WHERE cache_key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
            finally:
                conn.close()
        except Exception:
            pass
        return None

    def put(self, raw_filename: str, model_name: str, result_dict: Dict[str, Any]):
        key = self._make_key(raw_filename, model_name)
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO ai_cache (cache_key, raw_filename, model_name, result_json) VALUES (?, ?, ?, ?)",
                    (key, raw_filename, model_name, json.dumps(result_dict, ensure_ascii=False))
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass
