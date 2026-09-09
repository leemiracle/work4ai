"""自动化知识抽取（全量 833 篇）：用 NLP + 实体词典产出结构化
（摘要 + 三元组 + 概念），与手工精抽合并成完整知识库。

模板三元组：
  (文章, 属于领域, category)
  (文章, 涉及技术, term)
  (term_A, 共现于, term_B)   同篇 Top 实体间
产出 data/processed/knowledge_auto.jsonl，并合并为 knowledge_all.jsonl。
"""
from __future__ import annotations
import json
import time
from . import config as C
from .nlp import extract_entities, keyphrases, summarize, clean_text


def iter_articles():
    for p in sorted(C.RAW_ARTICLES.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        md = rec.get("markdown", "")
        if not md or len(md) < 200 or md.startswith("[content"):
            continue
        meta = rec.get("meta", {})
        det = rec.get("detail", {})
        yield {
            "aid": str(rec.get("aid")),
            "title": det.get("title") or meta.get("article_title", ""),
            "topic_id": meta.get("_topic_crawl_id"),
            "markdown": md,
        }


def extract_one(a: dict) -> dict:
    text = clean_text(a["markdown"])
    ents = extract_entities(text)
    summ = summarize(text, n=2, max_len=200)
    kps = [k for k, _ in keyphrases(text, topk=8)]
    # 三元组
    triples = []
    title = a["title"][:40] or a["aid"]
    flat_ents = []
    for cat, m in ents.items():
        triples.append((title, "属于领域", cat))
        for term, c in m.items():
            triples.append((title, f"涉及{cat}", term))
            flat_ents.append(term)
    # 共现（Top 实体两两）
    top = list(dict.fromkeys(flat_ents))[:8]
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            triples.append((top[i], "共现于", top[j]))
    concepts = list(dict.fromkeys(flat_ents))[:15] + kps[:8]
    return {
        "id": f"auto_{a['aid']}",
        "source": f"InfoQ topic={a['topic_id']}",
        "title": a["title"],
        "summary": " ".join(summ),
        "concepts": list(dict.fromkeys(concepts))[:18],
        "triples": triples[:40],
        "auto": True,
    }


def main():
    t0 = time.time()
    out_path = C.PROCESSED / "knowledge_auto.jsonl"
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for a in iter_articles():
            e = extract_one(a)
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
            n += 1
            if n % 100 == 0:
                print(f"  已处理 {n} ({time.time()-t0:.0f}s)", flush=True)
    # 合并：手工精抽(前) + 自动
    curated = (C.PROCESSED / "knowledge.jsonl").read_text(encoding="utf-8") \
        if (C.PROCESSED / "knowledge.jsonl").exists() else ""
    auto = out_path.read_text(encoding="utf-8")
    (C.PROCESSED / "knowledge_all.jsonl").write_text(curated + auto, encoding="utf-8")
    print(f"[kb_auto] 自动抽取 {n} 篇 ({time.time()-t0:.0f}s) -> knowledge_auto.jsonl")
    print(f"[kb_auto] 合并知识库 -> knowledge_all.jsonl "
          f"({(curated.count(chr(10))+n)} 条)")


if __name__ == "__main__":
    main()
