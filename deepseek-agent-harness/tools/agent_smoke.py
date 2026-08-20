#!/usr/bin/env python3
"""agent_smoke.py — L3 最小 agent 循环冒烟：不依赖 LLM API。

模拟一个三事件循环（user→assistant(tool_call)→tool(result)→assistant(done)），
写出轨迹并用 agent_trace_check.py 校验——验证"循环+轨迹+校验"链路在位。
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def run():
    events = [
        {"role": "system", "content": "smoke agent"},
        {"role": "user", "content": "echo 任务"},
        {"role": "assistant", "content": "",
         "tool_calls": [{"id": "c1", "function": {"name": "run_verify",
                                                  "arguments": json.dumps({"cmd": "echo hi"})}}]},
        {"role": "tool", "tool_call_id": "c1", "content": "exit=0\nhi"},
        {"role": "assistant", "content": "完成：输出 hi"},
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        path = f.name
    r = subprocess.run([sys.executable, str(HERE / "agent_trace_check.py"), path],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    Path(path).unlink()
    return r.returncode


if __name__ == "__main__":
    rc = run()
    print("SMOKE " + ("PASS" if rc == 0 else "FAIL") + "（循环→轨迹→校验 链路完整）")
    sys.exit(rc)
