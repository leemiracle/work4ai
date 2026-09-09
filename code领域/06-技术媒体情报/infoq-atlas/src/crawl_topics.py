"""拉取完整 topic 树并落地。

InfoQ topic/getList 返回顶层 topic，部分内嵌 child_list（含 id/name/alias/type）。
我们把顶层与子节点都登记为「可爬取的 topic id」，并保留父子关系。
"""
from __future__ import annotations
import json
import time
from .client import InfoQClient
from . import config as C


def build_topic_tree() -> dict:
    client = InfoQClient()
    raw = client.get_topics()
    tree = {
        "fetched_at": int(time.time()),
        "top_level": [],
        "all_topics": {},   # id(str) -> topic node（扁平化，含 parent_id）
    }

    def register(node: dict, parent_id: int | None):
        tid = node.get("id")
        if tid is None:
            return
        key = str(tid)
        rec = {
            "id": tid,
            "name": node.get("name", ""),
            "alias": node.get("alias", ""),
            "desc": node.get("desc", ""),
            "cover": node.get("cover", ""),
            "type": node.get("type"),
            "pid": parent_id,
            "article_count": node.get("article_count", 0),
            "total_count": node.get("total_count", 0),
            "ebook_count": node.get("ebook_count", 0),
            "score": node.get("score"),
            "is_leaf_subtopic": parent_id is not None and not node.get("child_list"),
        }
        tree["all_topics"][key] = rec
        for child in (node.get("child_list") or []):
            register(child, tid)

    for top in raw:
        register(top, None)
        tree["top_level"].append(str(top.get("id")))

    return tree


def main():
    tree = build_topic_tree()
    out = C.RAW_TOPICS / "topic_tree.json"
    out.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(tree["all_topics"])
    total_articles = sum(t["article_count"] for t in tree["all_topics"].values())
    print(f"[topics] 顶层 {len(tree['top_level'])} 个，全部 topic 节点 {n} 个")
    print(f"[topics] 报告文章数总和（含跨 topic 重复）：{total_articles}")
    print(f"[topics] -> {out}")

    # 打印概览
    for key in tree["top_level"]:
        t = tree["all_topics"][key]
        nsub = sum(1 for x in tree["all_topics"].values() if x["pid"] == t["id"])
        print(f"  [{t['id']:>4}] {t['name']:<10} articles={t['article_count']:>6} "
              f"subs={nsub}")


if __name__ == "__main__":
    main()
