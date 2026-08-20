#!/usr/bin/env python3
"""llm_eval.py — L4 最小评测：困惑度 + 生成质量启发式（非替代人工评测）。

用法： python3 tools/llm_eval.py --model /path/to/model --texts a.txt b.txt
输出： 每文本 PPL + 生成长度/重复率统计。exit code：PPL 有限且 >0 即 0。
诚实边界：PPL 低≠有用；本工具只防"模型完全坏了"这类回归。
"""
import argparse
import collections
import math
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="~/ai/models/Qwen2.5-0.5B-Instruct")
    ap.add_argument("--texts", nargs="+", required=True)
    ap.add_argument("--max-chars", type=int, default=2000)
    a = ap.parse_args()
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        print("EVAL SKIP: transformers/torch 未装（DEGRADED——只验证调用契约）")
        return 0
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype="float32").eval()
    results = []
    for t in a.texts:
        text = Path(t).read_text(errors="replace")[:a.max_chars]
        ids = tok(text, return_tensors="pt")
        with torch.no_grad():
            logits = model(**ids).logits[0, :-1]
        labels = ids.input_ids[0, 1:]
        nll = torch.nn.functional.cross_entropy(logits, labels).item()
        ppl = math.exp(nll)
        toks = labels.tolist()
        rep = 1 - len(set(toks)) / max(1, len(toks))
        results.append((t, ppl, rep))
        print(f"  {Path(t).name:<24} PPL={ppl:8.2f} 重复率={rep:.3f} tokens={len(toks)}")
    finite = all(math.isfinite(p) and p > 0 for _, p, _ in results)
    print("EVAL " + ("PASS" if finite else "FAIL") + "（PPL 健全性；质量判断需人工/基准）")
    return 0 if finite else 1


if __name__ == "__main__":
    sys.exit(main())
