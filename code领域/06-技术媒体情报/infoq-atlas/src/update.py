"""增量更新：抓取每个 topic 最新一页，把新文章追加进 lists 与 DB 可选。

用法:
    python -m src.update            # 仅刷新最新列表
    python -m src.update --rebuild  # 刷新后重建库与报告
"""
from __future__ import annotations
import argparse
import json
import time

from .client import InfoQClient
from . import config as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--pages", type=int, default=3, help="每 topic 刷新页数")
    args = ap.parse_args()

    tree = json.loads((C.RAW_TOPICS / "topic_tree.json").read_text(encoding="utf-8"))
    client = InfoQClient()
    new_total = 0
    for key in tree["top_level"]:
        t = tree["all_topics"][key]
        tid = t["id"]
        jsonl = C.RAW_LISTS / f"{tid}.jsonl"
        seen: set[str] = set()
        if jsonl.exists():
            with jsonl.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        seen.add(str(json.loads(line).get("aid")))
                    except json.JSONDecodeError:
                        pass
        # 不带 score，从最新开始抓几页
        added = 0
        score = None
        with jsonl.open("a", encoding="utf-8") as f:
            for _ in range(args.pages):
                page = client.get_article_list(tid, size=C.LIST_PAGE_SIZE, score=score)
                if not page:
                    break
                for a in page:
                    aid = str(a.get("aid") or a.get("aidint") or a.get("uuid"))
                    if aid in seen:
                        continue
                    seen.add(aid)
                    a["aid"] = aid
                    a["_score"] = int(a.get("score") or a.get("publish_time") or 0)
                    a["_topic_crawl_id"] = tid
                    a["_topic_crawl_name"] = t["name"]
                    f.write(json.dumps(a, ensure_ascii=False) + "\n")
                    added += 1
                score = int(page[-1].get("score") or page[-1].get("publish_time") or 0)
        if added:
            print(f"  [{tid} {t['name']}] +{added} 新文章")
            new_total += added
    print(f"[update] 共新增 {new_total} 篇, 时间 {time.strftime('%Y-%m-%d %H:%M')}")

    if args.rebuild:
        print("[update] 重建库与报告...")
        from . import normalize, analyze, kg, report_gen, dashboard
        normalize.build()
        analyze.main()
        kg.build()
        report_gen.main()
        dashboard.build()
        print("[update] 全部重建完成")


if __name__ == "__main__":
    main()
