"""为 #3 大模型知识抽取准备输入：选高价值文章(InfoQ 每 topic 头部 + 各站头部)，
清洗全文打包到 notes/kb_input.txt，供 LLM 产出 摘要+知识三元组。"""
from __future__ import annotations
import json
import sqlite3
from . import config as C
from .nlp import clean_text


def pick_infoq(cur, per_topic: int = 1) -> list[dict]:
    """每顶层 topic 取阅读量最高且有全文的文章（全局去重）。"""
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text("utf-8"))
    top_ids = [int(k) for k in tree["top_level"]]
    out = []
    seen = set()
    for tid in top_ids:
        rows = cur.execute(
            "SELECT a.aid, a.title, a.views, a.year FROM articles a "
            "JOIN article_topics t ON a.aid=t.aid "
            "WHERE t.topic_id=? AND a.content_len>500 "
            "GROUP BY a.aid ORDER BY a.views DESC LIMIT ?",
            (tid, per_topic * 3)).fetchall()
        picked = 0
        for aid, title, views, year in rows:
            aid = str(aid)
            if aid in seen:
                continue
            seen.add(aid)
            out.append({"aid": aid, "title": title, "views": views,
                        "year": year, "topic_id": tid})
            picked += 1
            if picked >= per_topic:
                break
    return out


def pick_sites(per_source: int = 2) -> list[dict]:
    out = []
    for p in sorted((C.ROOT / "data" / "raw" / "sites").glob("*.jsonl")):
        items = []
        text = p.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        items = [x for x in items if len(x.get("content", "")) > 400]
        items.sort(key=lambda x: len(x.get("content", "")), reverse=True)
        for it in items[:per_source]:
            out.append({"source": it["source"], "title": it["title"],
                        "url": it.get("url", ""), "text": it["content"]})
    return out


def main():
    import sys
    per_topic = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 2600
    conn = sqlite3.connect(C.DB_PATH)
    picks = pick_infoq(conn, per_topic=per_topic)
    conn.close()
    # 读全文 markdown
    parts = [f"# KB 抽取输入（InfoQ 每 topic 头部 {per_topic} 篇 + 各站头部）\n"]
    for pk in picks:
        aid = pk["aid"]
        path = C.RAW_ARTICLES / f"{aid}.json"
        if not path.exists():
            continue
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        md = clean_text(rec.get("markdown", ""))[:cap]
        parts.append(f"\n{'='*70}\n[INFOQ topic={pk['topic_id']}] {pk['title']}\n"
                     f"aid={pk['aid']} views={pk['views']} year={pk['year']}\n\n{md}\n")
    # 站点
    sp = pick_sites(per_source=2)
    for s in sp:
        parts.append(f"\n{'='*70}\n[SITE {s['source']}] {s['title']}\nurl={s['url']}\n\n"
                     f"{clean_text(s['text'])[:cap]}\n")
    out = C.NOTES / f"kb_input_p{per_topic}.txt"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"InfoQ picks {len(picks)} + 站点 {len(sp)} -> {out.name} "
          f"({out.stat().st_size//1024}KB)")


if __name__ == "__main__":
    main()
