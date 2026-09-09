"""把知识抽取扩到全量 25,801 篇目录（标题+摘要层）—— 批量高效版。

每次 API 调用处理一个 BATCH（15篇），返回 JSON 数组，调用数降 15x。
833 全文已用 GLM-5.1，跳过；其余用 glm-4-flash。
产出 data/processed/knowledge_catalog.jsonl。
用法: python -m src.kb_llm_catalog [batch=15] [workers=12] [model=glm-4-flash]
"""
from __future__ import annotations
import json
import os
import sys
import time
import threading
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import config as C
from . import llm

_done_aids: set[str] = set()


def load_done():
    p = C.PROCESSED / "knowledge_llm.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    e = json.loads(line)
                    if e.get("aid"):
                        _done_aids.add(str(e["aid"]))
                except json.JSONDecodeError:
                    continue


def iter_catalog():
    conn = sqlite3.connect(C.DB_PATH)
    rows = conn.execute("SELECT aid,title,summary FROM articles").fetchall()
    conn.close()
    for aid, title, summary in rows:
        if str(aid) in _done_aids or not (title or summary):
            continue
        yield {"aid": str(aid), "title": title or "", "summary": summary or ""}


def _batch_call(batch, model):
    """一次处理多篇。返回 [{...}, ...]"""
    items = [{"i": i, "title": a["title"][:70], "summary": a["summary"][:180]}
             for i, a in enumerate(batch)]
    prompt = ("你是技术知识抽取引擎。对下面每篇文章(i)，基于其标题与摘要输出**一个JSON数组**"
              "（无额外文字/无markdown围栏），每个元素形如 "
              '{"i":序号,"summary":"1句中文摘要","concepts":["c1","c2","c3"],'
              '"triples":[["主体","关系","客体"]]}。'
              "关系从 属于领域/实现/解决/依赖/包含/适用于/导致/优于/替代/基于/支持 里选，每篇2-3条。\n"
              f"文章列表：\n{json.dumps(items, ensure_ascii=False)}")
    try:
        out = llm.chat_json([{"role": "user", "content": prompt}],
                            model=model, temperature=0.2, max_tokens=4000, timeout=60)
        # out 可能是 list 或 dict
        arr = out if isinstance(out, list) else out.get("data", out.get("items",
                out.get("results", [])))
        if isinstance(arr, dict):
            arr = []
        by_i = {it.get("i"): it for it in arr if isinstance(it, dict)}
        results = []
        for idx, a in enumerate(batch):
            it = by_i.get(idx, {})
            results.append({
                "id": f"cat_{a['aid']}", "source": "InfoQ-catalog",
                "aid": a["aid"], "title": a["title"],
                "summary": it.get("summary", ""),
                "concepts": it.get("concepts", [])[:6],
                "triples": [list(t) for t in it.get("triples", [])[:5]
                            if isinstance(t, (list, tuple)) and len(t) == 3],
                "catalog": True,
            })
        return results
    except Exception as e:
        return [{"id": f"cat_{a['aid']}", "source": "InfoQ-catalog",
                 "aid": a["aid"], "title": a["title"], "summary": "",
                 "concepts": [], "triples": [], "catalog": True,
                 "error": str(e)[:50]} for a in batch]


def main():
    batch_sz = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    model = sys.argv[3] if len(sys.argv) > 3 else "glm-4-flash"
    load_done()
    arts = list(iter_catalog())
    batches = [arts[i:i + batch_sz] for i in range(0, len(arts), batch_sz)]
    print(f"[kb_catalog] {len(arts)} 篇 / {len(batches)} 批(×{batch_sz}) "
          f"model={model} workers={workers}", flush=True)
    out_path = C.PROCESSED / "knowledge_catalog.jsonl"
    t0 = time.time()
    ok = err = 0
    lock = threading.Lock()
    f = out_path.open("w", encoding="utf-8")
    n = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_batch_call, b, model): b for b in batches}
        for fut in as_completed(futs):
            for r in fut.result():
                with lock:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    if r.get("error") or not r.get("triples"):
                        err += 1
                    else:
                        ok += 1
                    n += 1
            if n and n % 300 == 0:
                f.flush()
                el = time.time() - t0
                print(f"  {n}/{len(arts)} ok={ok} err={err} {el:.0f}s "
                      f"速率={n/el:.1f}/s ETA={(len(arts)-n)/(n/el):.0f}s", flush=True)
    f.close()
    print(f"\n[kb_catalog] 完成 ok={ok} err={err} 耗时{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
