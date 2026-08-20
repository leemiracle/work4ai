#!/usr/bin/env python3
"""agent_trace_check.py — L2/L3 轨迹校验：JSONL 轨迹的 schema + 完整性检查。

规则（对应六组件的 V 侧最小契约）：
  1. 每行一个事件 JSON，必含 role（system/user/assistant/tool）
  2. assistant 的 tool_calls 与后续 tool 结果按 id 配对（无孤儿）
  3. 无空轮（assistant 纯文本后跟 user 之前允许——自然结束）
用法： python3 agent_trace_check.py trace.jsonl [--write-sample]
"""
import json
import sys
from pathlib import Path


def check(lines):
    errs, warns = [], []
    events = []
    for i, ln in enumerate(lines, 1):
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError as e:
            errs.append(f"L{i}: 非法 JSON（{e}）")
            continue
        if "role" not in ev:
            errs.append(f"L{i}: 缺 role")
            continue
        events.append((i, ev))
    open_calls = {}
    for i, ev in events:
        role = ev["role"]
        if role == "assistant":
            for tc in ev.get("tool_calls", []):
                tid = tc.get("id") or tc.get("tool_call_id")
                if not tid:
                    errs.append(f"L{i}: tool_call 缺 id")
                else:
                    open_calls[tid] = i
        elif role == "tool":
            tid = ev.get("tool_call_id")
            if tid is None:
                errs.append(f"L{i}: tool 结果缺 tool_call_id")
            elif tid not in open_calls:
                errs.append(f"L{i}: 孤儿工具结果（id={tid} 无对应调用）")
            else:
                open_calls.pop(tid)
        if role not in ("system", "user", "assistant", "tool"):
            warns.append(f"L{i}: 非标准 role={role}")
    for tid, i in open_calls.items():
        errs.append(f"L{i}: 工具调用 {tid} 无结果（循环中断？）")
    return errs, warns, len(events)


def sample():
    return [
        json.dumps({"role": "system", "content": "x"}, ensure_ascii=False),
        json.dumps({"role": "user", "content": "任务"}, ensure_ascii=False),
        json.dumps({"role": "assistant", "content": "",
                    "tool_calls": [{"id": "c1", "function": {"name": "read_file",
                                                             "arguments": "{}"}}]}, ensure_ascii=False),
        json.dumps({"role": "tool", "tool_call_id": "c1", "content": "文件内容"}, ensure_ascii=False),
        json.dumps({"role": "assistant", "content": "完成"}, ensure_ascii=False),
    ]


def main():
    args = sys.argv[1:]
    if "--write-sample" in args:
        Path("sample_trace.jsonl").write_text("\n".join(sample()) + "\n")
        print("sample_trace.jsonl 已生成（合法轨迹样例）")
        return 0
    if not args:
        print("用法: agent_trace_check.py <trace.jsonl> [--write-sample]")
        return 2
    p = Path(args[0])
    if not p.exists():
        print(f"文件不存在: {p}")
        return 2
    errs, warns, n = check(p.read_text(errors="replace").splitlines())
    print(f"事件数: {n}  错误: {len(errs)}  警告: {len(warns)}")
    for e in errs:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ⚠ {w}")
    if errs:
        print("TRACE FAIL")
        return 1
    print("TRACE PASS（配对完整，无孤儿/断头）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
