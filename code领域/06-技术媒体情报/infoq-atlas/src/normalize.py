"""规范化与建库：把 raw 的 lists + articles 统一成 schema，载入 SQLite（含 FTS5）。

产出 data/processed/infoq.db 与 data/processed/unified.jsonl。
幂等：每次重建（DROP）。
"""
from __future__ import annotations
import json
import re
import sqlite3
import time
from collections import defaultdict

from . import config as C


def _ts_group(ms: int) -> str:
    """毫秒时间戳 -> YYYY-MM。"""
    if not ms:
        return ""
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return ""
    if ms <= 0:
        return ""
    t = time.gmtime(ms / 1000)
    return time.strftime("%Y-%m", t)


def _year(ms: int) -> int | None:
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return None
    if ms <= 0:
        return None
    return time.gmtime(ms / 1000).tm_year


def _clean_text(s) -> str:
    if not s:
        return ""
    s = str(s)
    s = re.sub(r"<[^>]+>", "", s)          # 去 HTML 标签
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_topic_map() -> dict[int, dict]:
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))
    return {int(k): v for k, v in tree["all_topics"].items()}


def iter_catalog():
    """yield 每条目录记录。bulk read 避免逐行 I/O（/mnt/c 慢）。"""
    for p in sorted(C.RAW_LISTS.glob("*.jsonl")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def build(db_path=C.DB_PATH):
    topic_map = load_topic_map()
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    PRAGMA journal_mode=WAL;
    DROP TABLE IF EXISTS topics;
    DROP TABLE IF EXISTS articles;
    DROP TABLE IF EXISTS article_topics;
    DROP TABLE IF EXISTS article_people;
    DROP TABLE IF EXISTS article_labels;
    DROP TABLE IF EXISTS articles_fts;
    CREATE TABLE topics(
        id INTEGER PRIMARY KEY, name TEXT, alias TEXT, desc TEXT,
        pid INTEGER, article_count INTEGER, total_count INTEGER,
        is_leaf_subtopic INTEGER
    );
    CREATE TABLE articles(
        aid TEXT PRIMARY KEY, uuid TEXT, title TEXT, sharetitle TEXT,
        summary TEXT, publish_time INTEGER, year INTEGER, month TEXT,
        views INTEGER, comment_count INTEGER, word_count INTEGER,
        no_author TEXT, source INTEGER, type INTEGER, content_len INTEGER,
        ai_summary TEXT
    );
    CREATE TABLE article_topics(aid TEXT, topic_id INTEGER, topic_name TEXT);
    CREATE TABLE article_people(aid TEXT, name TEXT, role TEXT, uid INTEGER);
    CREATE TABLE article_labels(aid TEXT, label TEXT);
    CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(aid, title, summary, body);
    CREATE INDEX idx_at_aid ON article_topics(aid);
    CREATE INDEX idx_at_tid ON article_topics(topic_id);
    CREATE INDEX idx_art_time ON articles(publish_time);
    CREATE INDEX idx_art_year ON articles(year);
    """)
    cur = conn.cursor()

    # topics
    for tid, t in topic_map.items():
        cur.execute(
            "INSERT INTO topics VALUES(?,?,?,?,?,?,?,?)",
            (tid, t.get("name", ""), t.get("alias", ""), t.get("desc", ""),
             t.get("pid"), t.get("article_count", 0), t.get("total_count", 0),
             int(bool(t.get("is_leaf_subtopic")))))

    # 文章：先收集每篇文章聚合（跨 topic），再合并；优先用已抓全文
    full_by_aid: dict[str, dict] = {}
    for p in sorted(C.RAW_ARTICLES.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        full_by_aid[str(rec.get("aid"))] = rec

    agg: dict[str, dict] = {}
    for c in iter_catalog():
        aid = str(c.get("aid") or c.get("aidint") or c.get("uuid"))
        if not aid:
            continue
        e = agg.setdefault(aid, {
            "aid": aid, "uuid": c.get("uuid"), "title": "",
            "sharetitle": "", "summary": "", "publish_time": 0,
            "views": 0, "comment_count": 0, "word_count": None,
            "no_author": "", "source": None, "type": None,
            "crawl_topics": set(), "tag_topics": [], "labels": [],
            "authors": [], "translators": [], "markdown": "",
        })
        e["uuid"] = e["uuid"] or c.get("uuid")
        e["title"] = e["title"] or c.get("article_title", "")
        e["sharetitle"] = e["sharetitle"] or c.get("article_sharetitle", "")
        e["summary"] = e["summary"] or c.get("article_summary", "")
        pt = c.get("publish_time") or 0
        if pt and (not e["publish_time"] or pt > e["publish_time"]):
            e["publish_time"] = int(pt)
        e["views"] = max(e["views"], int(c.get("views") or 0))
        e["comment_count"] = max(e["comment_count"], int(c.get("comment_count") or 0))
        e["no_author"] = e["no_author"] or c.get("no_author", "")
        ct = c.get("_topic_crawl_id")
        if ct is not None:
            e["crawl_topics"].add(int(ct))
        for tp in (c.get("topic") or []):
            e["tag_topics"].append({"id": tp.get("id"), "name": tp.get("name")})
        for tr in (c.get("translator") or []):
            e["translators"].append({"name": tr.get("nickname"),
                                     "uid": tr.get("uid")})
        for lb in (c.get("label") or []):
            if isinstance(lb, dict):
                e["labels"].append(lb.get("name") or lb.get("text") or str(lb))
            else:
                e["labels"].append(str(lb))

    # 合并全文
    have_full = 0
    for aid, e in agg.items():
        full = full_by_aid.get(aid)
        if full:
            have_full += 1
            d = full.get("detail", {})
            e["title"] = d.get("title") or e["title"]
            e["summary"] = d.get("summary") or e["summary"]
            e["publish_time"] = d.get("publish_time") or e["publish_time"]
            e["views"] = max(int(d.get("views") or 0), e["views"])
            e["word_count"] = d.get("word_count")
            e["no_author"] = d.get("no_author") or e["no_author"]
            e["ai_summary"] = d.get("ai_summary")
            e["markdown"] = full.get("markdown", "")
            e["authors"] = [{"name": (a.get("nickname") if isinstance(a, dict) else str(a)),
                             "uid": (a.get("uid") if isinstance(a, dict) else None)}
                            for a in (d.get("author") or [])]
            e["translators"] = e["translators"] or [
                {"name": (t.get("nickname") if isinstance(t, dict) else str(t)),
                 "uid": (t.get("uid") if isinstance(t, dict) else None)}
                for t in (d.get("translator") or [])]
        else:
            e["ai_summary"] = None

    # 写库
    n_art = 0
    n_topic_links = 0
    unified_path = C.PROCESSED / "unified.jsonl"
    unified_lines: list[str] = []
    print(f"[normalize] 聚合 {len(agg)} 文章，开始入库...", flush=True)
    for aid, e in agg.items():
        if n_art % 10000 == 0 and n_art:
            print(f"[normalize] 已写入 {n_art}...", flush=True)
        pt = int(e["publish_time"] or 0)
        body_text = _clean_text(e["markdown"])
        cur.execute(
            "INSERT OR REPLACE INTO articles VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (aid, e["uuid"], _clean_text(e["title"]), _clean_text(e["sharetitle"]),
             _clean_text(e["summary"]), pt, _year(pt), _ts_group(pt),
             int(e["views"]), int(e["comment_count"]), e["word_count"],
             _clean_text(e["no_author"]), e["source"], e["type"],
             len(e["markdown"]), _clean_text(e.get("ai_summary"))))
        # FTS
        cur.execute("INSERT INTO articles_fts(aid,title,summary,body) VALUES(?,?,?,?)",
                    (aid, _clean_text(e["title"]), _clean_text(e["summary"]),
                     body_text[:60000]))
        # crawl_topics
        for tid in e["crawl_topics"]:
            tn = topic_map.get(tid, {}).get("name", str(tid))
            cur.execute("INSERT INTO article_topics VALUES(?,?,?)",
                        (aid, tid, tn))
            n_topic_links += 1
        # tag_topics（去重）
        seen_tp = set()
        for tp in e["tag_topics"]:
            tpid = tp.get("id")
            if tpid in seen_tp or tpid is None:
                continue
            seen_tp.add(tpid)
            cur.execute("INSERT INTO article_topics VALUES(?,?,?)",
                        (aid, int(tpid), tp.get("name", "")))
            n_topic_links += 1
        # people
        for role, lst in (("author", e["authors"]), ("translator", e["translators"])):
            for p in lst:
                nm = (p.get("name") or "").strip() if isinstance(p, dict) else str(p)
                if nm:
                    uid = p.get("uid") if isinstance(p, dict) else None
                    cur.execute("INSERT INTO article_people VALUES(?,?,?,?)",
                                (aid, nm, role, uid))
        # labels
        for lb in dict.fromkeys(e["labels"]):   # 去重保序
            if lb:
                cur.execute("INSERT INTO article_labels VALUES(?,?)", (aid, str(lb)))
        # unified jsonl（缓冲，循环结束一次性写）
        unified_lines.append(json.dumps({
            "aid": aid, "uuid": e["uuid"], "title": _clean_text(e["title"]),
            "summary": _clean_text(e["summary"]), "publish_time": pt,
            "year": _year(pt), "month": _ts_group(pt), "views": int(e["views"]),
            "topics": sorted(e["crawl_topics"]),
            "has_full": bool(e["markdown"]),
            "content_len": len(e["markdown"]),
        }, ensure_ascii=False))
        n_art += 1
    unified_path.write_text("\n".join(unified_lines) + "\n", encoding="utf-8")
    conn.commit()

    # 统计
    stats = {
        "articles": n_art,
        "with_full_text": have_full,
        "topic_links": n_topic_links,
        "topics": len(topic_map),
        "built_at": int(time.time()),
    }
    (C.PROCESSED / "db_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    conn.close()
    print(f"[normalize] 文章 {n_art}（含全文 {have_full}），topic 链接 {n_topic_links}")
    print(f"[normalize] -> {db_path}")
    print(f"[normalize] -> {unified_path}")
    return stats


if __name__ == "__main__":
    build()
