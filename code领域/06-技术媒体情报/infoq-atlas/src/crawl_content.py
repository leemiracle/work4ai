"""Tier 2：高信号文章全文爬取（detail + 正文 markdown）。

从已爬目录中，按 topic 选取代表性文章（默认：views Top N + 最近 N），抓取
detail 元数据与 content_url 正文，转 markdown，落到 data/raw/articles/{aid}.json。
全局按 aid 去重，已存在则跳过（幂等）。

用法:
    python -m src.crawl_content --per-topic 150 --recent 30
    python -m src.crawl_content --topics 8,31 --per-topic 300 --workers 6
"""
from __future__ import annotations
import argparse
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import InfoQClient
from .prosemirror import to_markdown
from . import config as C

_tls = threading.local()


def _client() -> InfoQClient:
    c = getattr(_tls, "c", None)
    if c is None:
        c = InfoQClient()
        _tls.c = c
    return c


def load_catalog_by_topic() -> dict[int, list[dict]]:
    """读全部 lists jsonl，按 _topic_crawl_id 分组。"""
    by_topic: dict[int, list[dict]] = {}
    for p in sorted(C.RAW_LISTS.glob("*.jsonl")):
        if p.name.startswith("_"):
            continue
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                tid = rec.get("_topic_crawl_id")
                if tid is None:
                    tid = int(p.stem)
                by_topic.setdefault(int(tid), []).append(rec)
    return by_topic


def select_sample(items: list[dict], top_views: int, recent: int) -> list[dict]:
    """选样：views Top N + 最近 N（按 publish_time），合并去重。"""
    def view_key(a):
        v = a.get("views") or 0
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    def time_key(a):
        try:
            return int(a.get("publish_time") or 0)
        except (TypeError, ValueError):
            return 0

    chosen: dict[str, dict] = {}
    for a in sorted(items, key=view_key, reverse=True)[:top_views]:
        chosen[str(a.get("aid") or a.get("uuid"))] = a
    for a in sorted(items, key=time_key, reverse=True)[:recent]:
        chosen[str(a.get("aid") or a.get("uuid"))] = a
    return list(chosen.values())


def fetch_one(a_meta: dict) -> dict | None:
    """抓单篇 detail + content，返回统一记录。"""
    aid = str(a_meta.get("aid") or a_meta.get("aidint") or a_meta.get("uuid"))
    out_path = C.RAW_ARTICLES / f"{aid}.json"
    if out_path.exists():
        return {"aid": aid, "status": "cached"}
    uuid = a_meta.get("uuid")
    if not uuid:
        return None
    client = _client()
    try:
        # 优先 SSR（detail API 常被 451 限流），失败回退 detail API
        try:
            ssr = client.get_article_via_ssr(uuid)
            content_url = ssr.get("content_url")
            extra = ssr
        except Exception:
            detail = client.get_article_detail(uuid)
            content_url = detail.get("content_url")
            extra = detail
        if not content_url:
            return {"aid": aid, "status": "no_content_url"}
    except Exception as e:
        return {"aid": aid, "status": "detail_error", "error": str(e)}
    markdown = ""
    try:
        doc = client.get_article_content(content_url)
        markdown = to_markdown(doc)
    except Exception as e:
        markdown = f"[content fetch error: {e}]"
    rec = {
        "aid": aid,
        "uuid": uuid,
        "fetched_at": int(time.time()),
        "meta": a_meta,
        "detail": {
            "title": extra.get("article_title") or a_meta.get("article_title"),
            "summary": extra.get("article_summary") or a_meta.get("article_summary"),
            "publish_time": extra.get("publish_time") or a_meta.get("publish_time"),
            "views": a_meta.get("views"),
            "word_count": extra.get("word_count"),
            "comment_count": a_meta.get("comment_count"),
            "no_author": a_meta.get("no_author"),
            "topics": a_meta.get("topic"),
            "labels": a_meta.get("label"),
            "content_url": content_url,
        },
        "markdown": markdown,
    }
    out_path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return {"aid": aid, "status": "ok", "len": len(markdown)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", default="", help="逗号分隔 topic id")
    ap.add_argument("--per-topic", type=int, default=150, help="views Top N")
    ap.add_argument("--recent", type=int, default=30, help="最近 N")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    by_topic = load_catalog_by_topic()
    if args.topics:
        want = {int(x) for x in args.topics.split(",") if x.strip()}
        by_topic = {k: v for k, v in by_topic.items() if k in want}

    # 选题 + 全局去重
    seen: set[str] = set()
    todo: list[dict] = []
    per_topic_plan: dict[int, int] = {}
    for tid, items in sorted(by_topic.items()):
        sample = select_sample(items, args.per_topic, args.recent)
        n = 0
        for a in sample:
            aid = str(a.get("aid") or a.get("uuid"))
            if aid in seen:
                continue
            seen.add(aid)
            todo.append(a)
            n += 1
        per_topic_plan[tid] = n

    print(f"[content] 计划抓取 {len(todo)} 篇 (跨 {len(per_topic_plan)} topic)")
    for tid, n in list(per_topic_plan.items())[:20]:
        print(f"    topic {tid}: {n}")

    t0 = time.time()
    done = ok = err = cached = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, a): a for a in todo}
        for fut in as_completed(futs):
            done += 1
            try:
                r = fut.result() or {}
                st = r.get("status")
                if st == "ok":
                    ok += 1
                elif st == "cached":
                    cached += 1
                else:
                    err += 1
            except Exception as e:
                err += 1
            if done % 25 == 0 or done == len(todo):
                print(f"[content] {done}/{len(todo)} ok={ok} cached={cached} "
                      f"err={err} elapsed={time.time()-t0:.0f}s")
    print(f"\n[content] 完成: ok={ok} cached={cached} err={err} 耗时 {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
