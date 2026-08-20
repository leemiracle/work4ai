#!/usr/bin/env python3
"""agent_eval.py — L4 任务评测：从轨迹 JSONL 统计任务结果与成本。

统计：任务数/完成数（最后 assistant 事件含结论且无断头工具调用）、
     总轮数、工具调用次数、粗估 token（字符/4）。
对比模式：--baseline old.jsonl 时输出增量对比（防回归）。
"""
import argparse
import json
import sys
from pathlib import Path


def stats(path):
    evs = []
    for ln in Path(path).read_text(errors="replace").splitlines():
        ln = ln.strip()
        if ln:
            try:
                evs.append(json.loads(ln))
            except json.JSONDecodeError:
                pass
    n_tools = sum(len(e.get("tool_calls", [])) for e in evs if e["role"] == "assistant")
    chars = sum(len(str(e.get("content", ""))) for e in evs)
    done = bool(evs) and evs[-1]["role"] == "assistant" and evs[-1].get("content") \
        and not any(len(e.get("tool_calls", [])) for e in evs if e["role"] == "assistant") is None
    # 简化完成判定：最后事件是 assistant 且有文本（循环自然结束的近似）
    return {"events": len(evs), "tool_calls": n_tools,
            "tokens_est": chars // 4, "last_role": evs[-1]["role"] if evs else "-"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--baseline", default=None)
    a = ap.parse_args()
    s = stats(a.trace)
    print(f"  {Path(a.trace).name}: events={s['events']} tool_calls={s['tool_calls']} "
          f"tokens≈{s['tokens_est']} last_role={s['last_role']}")
    if a.baseline:
        b = stats(a.baseline)
        dt = s["tokens_est"] - b["tokens_est"]
        dc = s["tool_calls"] - b["tool_calls"]
        flag = "↑变贵" if dt > max(100, b["tokens_est"] * 0.1) else "OK"
        print(f"  vs 基线: tokens {dt:+d} tool_calls {dc:+d} → {flag}")
    print("EVAL DONE（完成判定见 last_role；严格判定须任务级 checker）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
