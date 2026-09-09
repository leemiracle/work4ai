"""用真实 LLM (智谱 GLM) 对全量文章做高质量知识抽取。

对每篇全文：调用 glm-4-flash 产出 抽象式摘要 + 语义三元组(非模板) + 规范化概念。
并发执行；产出 data/processed/knowledge_llm.jsonl，替换/升级 knowledge_all 的模板层。
"""
from __future__ import annotations
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config as C
from .nlp import clean_text
from . import llm

_tls = threading.local()

PROMPT = """你是技术知识抽取引擎。阅读下面文章，输出**严格的 JSON**（不要任何额外文字、不要 markdown 围栏）：
{{
  "summary": "2-3句中文抽象式摘要（概括核心观点/做法/结论，不要罗列细节）",
  "concepts": ["核心概念1","核心概念2",...],  // 5个规范化术语
  "triples": [["主体","关系","客体"], ...]  // 3-5条**语义**三元组
}}
关系必须是有意义的语义关系，从这些里选：属于领域/实现/解决/优化/依赖/包含/适用于/导致/优于/对比/替代/定义/支持/基于/演进为。禁止用"涉及"这种无信息关系。
文章标题：{title}
文章正文（节选）：
{text}"""


def _call(a):
    aid = a["aid"]
    title = a["title"]
    text = clean_text(a["markdown"])[:1300]
    if len(text) < 80:
        return None
    msgs = [{"role": "user", "content": PROMPT.format(title=title[:80], text=text)}]
    try:
        out = llm.chat_json(msgs, model="glm-5.1", temperature=0.2,
                            max_tokens=4000, timeout=110)
        return {
            "id": f"llm_{aid}", "source": f"InfoQ topic={a['topic_id']}",
            "title": title, "aid": aid, "topic_id": a["topic_id"],
            "summary": out.get("summary", ""),
            "concepts": out.get("concepts", [])[:12],
            "triples": [list(t) for t in out.get("triples", [])[:12]
                        if isinstance(t, (list, tuple)) and len(t) == 3],
            "llm": True,
        }
    except Exception as e:
        return {"id": f"llm_{aid}", "source": f"InfoQ topic={a['topic_id']}",
                "title": title, "aid": aid, "topic_id": a["topic_id"],
                "summary": "", "concepts": [], "triples": [],
                "llm": True, "error": str(e)[:80]}


def iter_articles(limit=None):
    n = 0
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
        yield {"aid": str(rec.get("aid")),
               "title": det.get("title") or meta.get("article_title", ""),
               "topic_id": meta.get("_topic_crawl_id"), "markdown": md}
        n += 1
        if limit and n >= limit:
            break


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    arts = list(iter_articles(limit=limit))
    print(f"[kb_llm] 处理 {len(arts)} 篇, workers={workers}")
    out_path = C.PROCESSED / "knowledge_llm.jsonl"
    t0 = time.time()
    ok = err = 0
    f = out_path.open("w", encoding="utf-8")
    lock = threading.Lock()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_call, a): a for a in arts}
        for fut in as_completed(futs):
            r = fut.result()
            with lock:
                if r:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    if r.get("error") or not r.get("triples"):
                        err += 1
                    else:
                        ok += 1
                done += 1
                if done % 25 == 0 or done == len(arts):
                    print(f"  {done}/{len(arts)} ok={ok} err={err} "
                          f"elapsed={time.time()-t0:.0f}s", flush=True)
    f.close()
    print(f"\n[kb_llm] 完成: ok={ok} err={err} 耗时 {time.time()-t0:.0f}s -> {out_path.name}")


if __name__ == "__main__":
    main()
