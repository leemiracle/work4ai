"""用 GLM-5.1 对 9 经典站全文做知识抽取，扩展知识库到多站点。

读 data/raw/sites/*.jsonl 中含全文的条目，调用 LLM 抽取摘要+三元组，
产出 data/processed/knowledge_sites.jsonl。
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
from .kb_llm import PROMPT, _call  # 复用 prompt 与调用逻辑

SDIR = C.ROOT / "data" / "raw" / "sites"


def iter_site_articles():
    for p in sorted(SDIR.glob("*.jsonl")):
        src = p.stem
        text = p.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = rec.get("content", "")
            if len(content) < 300:
                continue
            yield {"aid": f"site_{rec.get('id','')[:40]}",
                   "title": rec.get("title", ""),
                   "topic_id": src, "markdown": content,
                   "source_site": src, "url": rec.get("url", "")}


def call_site(a):
    out = _call(a)
    if out:
        out["source"] = f"SITE:{a['source_site']}"
        out["url"] = a["url"]
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    arts = list(iter_site_articles())
    print(f"[kb_llm_sites] 处理 {len(arts)} 篇站点全文, workers={workers}")
    out_path = C.PROCESSED / "knowledge_sites.jsonl"
    t0 = time.time()
    ok = err = 0
    f = out_path.open("w", encoding="utf-8")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(call_site, a): a for a in arts}
        for fut in as_completed(futs):
            r = fut.result()
            if r:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                if r.get("error") or not r.get("triples"):
                    err += 1
                else:
                    ok += 1
            else:
                err += 1
            done = ok + err
            if done % 15 == 0:
                print(f"  {done}/{len(arts)} ok={ok} err={err} "
                      f"elapsed={time.time()-t0:.0f}s", flush=True)
    f.close()
    print(f"\n[kb_llm_sites] 完成 ok={ok} err={err} -> {out_path.name}")


if __name__ == "__main__":
    main()
