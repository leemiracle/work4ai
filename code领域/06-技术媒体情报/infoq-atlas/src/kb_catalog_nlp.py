"""全量目录 NLP 知识抽取（秒级覆盖 25,801 篇）。

对 DB 中所有文章用标题+摘要做实体抽取+模板三元组（833 全文已由 GLM-5.1 处理，跳过）。
与 GLM 层合并得到完整知识库（全 25,801 覆盖）。
产出 data/processed/knowledge_catalog.jsonl。
"""
from __future__ import annotations
import json
import sqlite3
from . import config as C
from .nlp import extract_entities, keyphrases


def load_done():
    done = set()
    p = C.PROCESSED / "knowledge_llm.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if e.get("aid"):
                        done.add(str(e["aid"]))
                except json.JSONDecodeError:
                    continue
    return done


def main():
    done = load_done()
    conn = sqlite3.connect(C.DB_PATH)
    rows = conn.execute("SELECT aid,title,summary FROM articles").fetchall()
    conn.close()
    out_path = C.PROCESSED / "knowledge_catalog.jsonl"
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for aid, title, summary in rows:
            aid = str(aid)
            if aid in done:           # GLM 层已处理
                continue
            text = (title or "") + " " + (summary or "")
            if len(text) < 8:
                continue
            ents = extract_entities(text)
            kps = [k for k, _ in keyphrases(text, topk=5)]
            triples = []
            flat = []
            t = (title or aid)[:30]
            for cat, m in ents.items():
                triples.append((t, "属于领域", cat))
                for term, c in m.items():
                    triples.append((t, f"涉及{cat}", term))
                    flat.append(term)
            # 标题-技术 共现
            top = list(dict.fromkeys(flat))[:5]
            for i in range(len(top)):
                for j in range(i + 1, len(top)):
                    triples.append((top[i], "共现于", top[j]))
            concepts = list(dict.fromkeys(flat + kps))[:10]
            f.write(json.dumps({
                "id": f"cat_{aid}", "source": "InfoQ-catalog",
                "aid": aid, "title": title or "",
                "summary": summary or "",
                "concepts": concepts,
                "triples": triples[:25],
                "catalog_nlp": True,
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"[kb_catalog_nlp] 处理 {n} 篇目录(GMT5.1全文层已跳过) -> {out_path.name}")


if __name__ == "__main__":
    main()
