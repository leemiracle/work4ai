"""为深度综合(LLM 精读)准备素材包：每个 topic 取头部 N 篇全文，
清洗为纯文本，写入 notes/topic_bundle_{tid}.txt 供后续精读综合。

这样把"慢 FS 程序化取数"与"LLM 读+写"分离。
"""
from __future__ import annotations
import json
from . import config as C
from .nlp import clean_text


def load_full_by_topic() -> dict[int, list[dict]]:
    by: dict[int, list[dict]] = {}
    for p in sorted(C.RAW_ARTICLES.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        meta = rec.get("meta", {})
        det = rec.get("detail", {})
        md = rec.get("markdown", "")
        if not md or len(md) < 200 or md.startswith("[content"):
            continue
        tid = meta.get("_topic_crawl_id")
        if tid is None:
            continue
        by.setdefault(int(tid), []).append({
            "aid": str(rec.get("aid")),
            "title": det.get("title") or meta.get("article_title", ""),
            "summary": det.get("summary") or meta.get("article_summary", ""),
            "views": int(meta.get("views") or 0),
            "publish_time": det.get("publish_time") or meta.get("publish_time") or 0,
            "markdown": md,
        })
    return by


def main(top_n: int = 6, max_chars: int = 3200):
    by = load_full_by_topic()
    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text("utf-8"))
    tname = {int(k): v["name"] for k, v in tree["all_topics"].items()}
    for tid, items in by.items():
        items.sort(key=lambda x: x["views"], reverse=True)
        picks = items[:top_n]
        if not picks:
            continue
        name = tname.get(tid, str(tid))
        out = C.NOTES / f"topic_bundle_{tid}.txt"
        parts = [f"# TOPIC: {name} (id={tid})  精读素材 {len(picks)} 篇\n"]
        for i, a in enumerate(picks, 1):
            txt = clean_text(a["markdown"])[:max_chars]
            parts.append(f"\n{'='*70}\n[{i}] {a['title']}\n"
                         f"views={a['views']}  publish={a['publish_time']}\n"
                         f"摘要: {a['summary']}\n\n{txt}\n")
        out.write_text("".join(parts), encoding="utf-8")
        print(f"  [{tid} {name}] {len(picks)} 篇 -> {out.name} "
              f"({out.stat().st_size//1024}KB)")


if __name__ == "__main__":
    main()
