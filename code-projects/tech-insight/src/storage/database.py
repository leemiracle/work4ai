"""SQLite 数据库操作层"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator, Optional

from ..config import Config
from .models import Article

_LOCAL = threading.local()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_name TEXT,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    author TEXT,
    author_id TEXT,
    summary TEXT,
    content TEXT,
    category TEXT,
    tags TEXT,
    published_at TEXT,
    collected_at TEXT,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    cover_image TEXT,
    uuid TEXT,
    language TEXT DEFAULT 'zh-CN',
    analyzed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    mentions INTEGER DEFAULT 1,
    source_articles TEXT,
    properties TEXT,
    created_at TEXT,
    UNIQUE(name, entity_type)
);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    evidence TEXT,
    source_articles TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category TEXT,
    current_count INTEGER,
    previous_count INTEGER,
    growth_rate REAL,
    first_seen TEXT,
    last_seen TEXT,
    related_entities TEXT,
    recorded_at TEXT,
    UNIQUE(keyword, recorded_at)
);

CREATE TABLE IF NOT EXISTS analysis_cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity);
"""


def _get_db_path() -> str:
    settings = Config.settings()
    db_path = Config.base_dir() / settings["storage"]["sqlite_path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)


def _get_conn() -> sqlite3.Connection:
    if not hasattr(_LOCAL, "conn") or _LOCAL.conn is None:
        _LOCAL.conn = sqlite3.connect(_get_db_path(), check_same_thread=False)
        _LOCAL.conn.row_factory = sqlite3.Row
        _LOCAL.conn.execute("PRAGMA journal_mode=WAL")
    return _LOCAL.conn


def init_db():
    conn = _get_conn()
    conn.executescript(_SCHEMA)
    conn.commit()


def _gen_id(source: str, url: str) -> str:
    raw = f"{source}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()


@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    conn = _get_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def save_article(article: Article) -> bool:
    init_db()
    article.id = article.id or _gen_id(article.source, article.url)
    data = article.to_dict()
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT OR REPLACE INTO articles
            (id, source, source_name, title, url, author, author_id, summary,
             content, category, tags, published_at, collected_at, view_count,
             like_count, comment_count, bookmark_count, cover_image, uuid, language, analyzed)
            VALUES
            (:id, :source, :source_name, :title, :url, :author, :author_id, :summary,
             :content, :category, :tags, :published_at, :collected_at, :view_count,
             :like_count, :comment_count, :bookmark_count, :cover_image, :uuid, :language,
             COALESCE((SELECT analyzed FROM articles WHERE id=:id), 0))
            """,
            data,
        )
    return True


def article_exists(source: str, url: str) -> bool:
    aid = _gen_id(source, url)
    with get_cursor() as cur:
        cur.execute("SELECT 1 FROM articles WHERE id=?", (aid,))
        return cur.fetchone() is not None


def get_unanalyzed_articles(limit: int = 50) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT * FROM articles WHERE analyzed=0 AND content != ''
            ORDER BY published_at DESC LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]


def mark_analyzed(article_ids: list[str]):
    if not article_ids:
        return
    placeholders = ",".join("?" * len(article_ids))
    with get_cursor() as cur:
        cur.execute(
            f"UPDATE articles SET analyzed=1 WHERE id IN ({placeholders})",
            article_ids,
        )


def get_all_articles(limit: int = 1000, source: Optional[str] = None,
                     days: Optional[int] = None) -> list[dict]:
    query = "SELECT * FROM articles WHERE content != ''"
    params: list[Any] = []
    if source:
        query += " AND source=?"
        params.append(source)
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        query += " AND collected_at >= ?"
        params.append(cutoff)
    query += " ORDER BY published_at DESC LIMIT ?"
    params.append(limit)
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def get_stats() -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM articles")
        total = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM articles WHERE analyzed=1")
        analyzed = cur.fetchone()["c"]
        cur.execute(
            "SELECT source, COUNT(*) as c FROM articles GROUP BY source ORDER BY c DESC"
        )
        by_source = {r["source"]: r["c"] for r in cur.fetchall()}
        cur.execute("SELECT COUNT(*) as c FROM entities")
        entities = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM relations")
        relations = cur.fetchone()["c"]
    return {
        "total_articles": total,
        "analyzed_articles": analyzed,
        "by_source": by_source,
        "entities": entities,
        "relations": relations,
    }


def save_analysis_cache(key: str, value: Any):
    now = datetime.now().isoformat()
    with get_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO analysis_cache (key, value, created_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, ensure_ascii=False), now),
        )


def get_analysis_cache(key: str) -> Optional[Any]:
    with get_cursor() as cur:
        cur.execute("SELECT value FROM analysis_cache WHERE key=?", (key,))
        row = cur.fetchone()
        if row:
            return json.loads(row["value"])
    return None
