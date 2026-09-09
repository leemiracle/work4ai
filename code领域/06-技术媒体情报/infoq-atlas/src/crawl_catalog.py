"""全量文章目录爬取（元数据层）。

按 top-level topic 并发爬取 getList，游标分页 + 去重，增量落盘到
data/raw/lists/{tid}.jsonl，并写状态文件 data/raw/lists/{tid}.state.json 以便断点续爬。

用法:
    python -m src.crawl_catalog                      # 默认爬所有顶层 topic, max_pages=200
    python -m src.crawl_catalog --topics 8,1174 --max-pages 500
    python -m src.crawl_catalog --resume              # 跳过已完成的 topic
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import InfoQClient, crawl_topic_articles
from . import config as C

# 每个 worker 独立 client（urllib 非线程安全要求低，但分开更稳）
_tls = threading.local()


def _client() -> InfoQClient:
    c = getattr(_tls, "c", None)
    if c is None:
        c = InfoQClient()
        _tls.c = c
    return c


def crawl_one_topic(tid: int, name: str, max_pages: int,
                    page_size: int = C.LIST_PAGE_SIZE,
                    verbose: bool = True) -> dict:
    """爬单个 topic 的目录。增量写 jsonl，状态写 state 文件。支持续爬。"""
    out_jsonl = C.RAW_LISTS / f"{tid}.jsonl"
    state_path = C.RAW_LISTS / f"{tid}.state.json"

    # 恢复状态
    seen: set[str] = set()
    last_score: int | None = None
    pages_done = 0
    total_written = 0
    if out_jsonl.exists():
        with out_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                seen.add(str(rec.get("aid") or rec.get("aidint") or rec.get("uuid")))
                total_written += 1
                pts = rec.get("_score")
                if pts:
                    last_score = pts
        pages_done = (total_written // page_size) or 0
        if verbose:
            print(f"[{tid} {name}] 续爬: 已有 {total_written} 条, 估计 {pages_done} 页")

    client = _client()
    f = out_jsonl.open("a", encoding="utf-8")
    try:
        consecutive_empty = 0
        while pages_done < max_pages:
            page = client.get_article_list(tid, size=page_size, score=last_score)
            pages_done += 1
            if not page:
                if verbose:
                    print(f"[{tid} {name}] page {pages_done} 空 -> 完成")
                break
            new_count = 0
            for a in page:
                aid = str(a.get("aid") or a.get("aidint") or a.get("uuid"))
                if not aid or aid in seen:
                    continue
                seen.add(aid)
                a["aid"] = aid
                a["_score"] = int(a.get("score") or a.get("publish_time") or 0)
                a["_topic_crawl_id"] = tid
                a["_topic_crawl_name"] = name
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
                new_count += 1
            f.flush()
            total_written += new_count
            last = page[-1]
            last_score = int(last.get("score") or last.get("publish_time") or 0)
            consecutive_empty = 0 if new_count else consecutive_empty + 1
            if consecutive_empty >= 3:
                if verbose:
                    print(f"[{tid} {name}] 连续 3 页无新文章 -> 认为到尽头 "
                          f"(共 {total_written} 条)")
                break
            if verbose and (pages_done % 25 == 0 or pages_done <= 2):
                print(f"[{tid} {name}] page {pages_done}/{max_pages} "
                      f"new {new_count} total {total_written}")
    finally:
        f.close()
        state = {"tid": tid, "name": name, "pages": pages_done,
                 "total": total_written, "last_score": last_score,
                 "finished_at": int(time.time())}
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    return {"tid": tid, "name": name, "total": total_written,
            "pages": pages_done}


def load_topic_tree() -> dict:
    return json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))


def top_topic_ids() -> list[tuple[int, str]]:
    tree = load_topic_tree()
    out = []
    for key in tree["top_level"]:
        t = tree["all_topics"][key]
        out.append((t["id"], t["name"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", default="", help="逗号分隔 topic id，留空=全部顶层")
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--resume", action="store_true", help="跳过已达到页数上限的 topic")
    args = ap.parse_args()

    if args.topics:
        ids = [int(x) for x in args.topics.split(",") if x.strip()]
        tree = load_topic_tree()
        targets = [(i, tree["all_topics"].get(str(i), {}).get("name", str(i)))
                   for i in ids]
    else:
        targets = top_topic_ids()

    print(f"[catalog] 目标 {len(targets)} 个 topic, max_pages={args.max_pages}, "
          f"workers={args.workers}")
    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {}
        for tid, name in targets:
            if args.resume:
                st = C.RAW_LISTS / f"{tid}.state.json"
                if st.exists():
                    s = json.loads(st.read_text(encoding="utf-8"))
                    if s.get("pages", 0) >= args.max_pages:
                        print(f"[catalog] 跳过 [{tid} {name}] 已达上限")
                        results.append(s)
                        continue
            futures[ex.submit(crawl_one_topic, tid, name, args.max_pages)] = (tid, name)
        for fut in as_completed(futures):
            tid, name = futures[fut]
            try:
                r = fut.result()
                results.append(r)
                print(f"[catalog] 完成 [{tid} {name}] -> {r['total']} 条, "
                      f"{r['pages']} 页")
            except Exception as e:
                print(f"[catalog] 失败 [{tid} {name}] -> {e}", file=sys.stderr)

    total = sum(r.get("total", 0) for r in results)
    print(f"\n[catalog] 全部完成: {total} 条目录, 耗时 {time.time()-t0:.0f}s")
    # 汇总
    summary_path = C.RAW_LISTS / "_summary.json"
    summary_path.write_text(json.dumps({
        "finished_at": int(time.time()),
        "max_pages": args.max_pages,
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[catalog] -> {summary_path}")


if __name__ == "__main__":
    main()
