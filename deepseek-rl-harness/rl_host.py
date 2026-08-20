#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rl_host.py — 宿主：DeepSeek 引擎 + 六组件骨架 + rl-dev 插件装载

与 rust/kernel 版同骨架（engines/hooks/governance 完全复用），换 RL 领域工具表：
验证金字塔 L1 lint → L2 单测 → L3 训练冒烟（reward 方向性）→ L4 复现（seed 一致性）。

零依赖自检: python3 rl_host.py --self-test
真实运行:   python3 rl_host.py --task "..." （需 pip install openai + KH_API_KEY）
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from hooks.authorize import authorize  # noqa: E402

FILE_MAX_LINES, TOOL_RESULT_CAP = 2000, 16_000
COMPACT_TRIGGER, KEEP_RECENT = 0.8, 20_000
WINDOW = 128_000
MAX_TURNS_DEFAULT = 40
VERIFY_TIMEOUT = 600          # RL 训练比编译慢，放宽

from engines.dialects import (api_key, base_url, loop_model, thinker_model,  # noqa: E402
                              resolve_dialect)


def _tool(name, desc, props, required):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": required}}}


TOOLS = [
    _tool("read_file", "读文件（限 RL_PROJECT/插件目录）",
          {"path": {"type": "string"}, "offset": {"type": "integer", "default": 1}}, ["path"]),
    _tool("grep_tree", "RL_PROJECT 内 grep -rn（找算法实现/超参/seed 用法）",
          {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."},
           "glob": {"type": "string", "default": "*.py"}}, ["pattern"]),
    _tool("run_verify", "跑命令。exit code 即证据。pip install / wandb 上传会被拦",
          {"cmd": {"type": "string"}}, ["cmd"]),
    _tool("write_file", "写文件（白名单：RL_PROJECT + state/）",
          {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"]),
    _tool("rl_lint", "L1: py_compile 全部 .py + ruff（若装了）",
          {"target": {"type": "string", "description": "文件或目录"}}, []),
    _tool("rl_test", "L2: pytest（缺则 unittest discover）。测试不过=没完成",
          {"target": {"type": "string", "description": "测试路径/节点，缺省全跑"}}, []),
    _tool("rl_smoke", "L3: toy 训练冒烟——纯标准库 bandit+Q-learning，断言 reward 改善方向（防'训练循环空转'）",
          {}, []),
    _tool("rl_repro", "L4: 复现检查——同 seed 两跑输出 diff 必须为空（改代码前先证明基线可复现）",
          {"cmd": {"type": "string", "description": "要复现的实验命令（须自带 --seed）"}}, ["cmd"]),
    _tool("graph_guard", "graph 三查①反Goodhart: reward hacking 扫描（reward 写文件伪造/环境改语义/eval 泄漏）",
          {"base": {"type": "string", "default": "HEAD~1"}}, []),
    _tool("graph_conflict", "graph 三查②盲区: 影响面（环境版本/gym API/超参文件/CUDA 版本）+补验清单",
          {"base": {"type": "string", "default": "HEAD~1"}}, []),
    _tool("patch_queue", "graph 三查③冲突: 补丁队列（实验目录与结果文件是共享热点）",
          {"action": {"type": "string", "enum": ["status", "claim", "release", "precheck"]},
           "series": {"type": "string"}, "files": {"type": "array", "items": {"type": "string"}},
           "patch": {"type": "string"}}, ["action"]),
    _tool("deep_plan", "重量级规划/审查 → thinker 模型（手册08章 cascade）。循环内 ≤2 次",
          {"question": {"type": "string"}}, ["question"]),
]
TOOL_NAMES = {t["function"]["name"] for t in TOOLS}


class Ledger:
    def __init__(self, root=ROOT / "state"):
        self.progress = root / "progress.md"
        self.progress.touch(exist_ok=True)

    def wrap_up(self, note):
        with open(self.progress, "a") as f:
            f.write(f"\n## {time.strftime('%F %T')}\n{note}\n")
        print(f"[ledger] {note[:120]}")


def _cap(text, cap=TOOL_RESULT_CAP):
    text = text or ""
    return text if len(text) <= cap else text[-cap:] + f"\n[...truncated, kept tail {cap}B]"


def _sh(cmd, timeout=VERIFY_TIMEOUT):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout,
                           cwd=str(ROOT))
        return f"exit={r.returncode}\n{_cap((r.stdout or '') + (r.stderr or ''))}"
    except subprocess.TimeoutExpired:
        return f"exit=124\nTIMEOUT {timeout}s —— 缩小规模（步数/环境数）或分层跑"


def exec_tool(name, args):
    rp = os.environ.get("RL_PROJECT", "")

    def resolve(path):
        p = Path(path)
        return p if p.is_absolute() or not rp else (Path(rp) / p)

    if name == "read_file":
        p = resolve(args["path"])
        try:
            lines = p.read_text(errors="replace").splitlines()
        except OSError as e:
            return f"ERROR: {e}"
        off = int(args.get("offset", 1))
        return _cap(f"[{p}:{off}-{off+len(lines[off-1:off-1+FILE_MAX_LINES])} of {len(lines)}]\n"
                    + "\n".join(lines[off-1:off-1+FILE_MAX_LINES]))
    if name == "grep_tree":
        base = rp or "."
        return _sh(f'grep -rn --include="{args.get("glob", "*.py")}" -e "{args["pattern"]}" '
                   f'{args.get("path", ".")} 2>/dev/null | head -80')
    if name == "run_verify":
        return _sh(args["cmd"])
    if name == "write_file":
        p = resolve(args["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(args["content"])
        return f"wrote {len(args['content'])}B to {p}"
    if name == "rl_lint":
        return _sh(f"bash tools/rl_lint.sh {args.get('target', rp or '.')}")
    if name == "rl_test":
        return _sh(f"bash tools/rl_test.sh {args.get('target', '')}")
    if name == "rl_smoke":
        return _sh("python3 tools/rl_smoke.py")
    if name == "rl_repro":
        return _sh(f"bash tools/rl_repro.sh {args['cmd']}")
    if name == "graph_guard":
        return _sh(f'python3 governance/goodhart_guards.py --base {args.get("base", "HEAD~1")} '
                   f'--repo "{rp or "."}" --json')
    if name == "graph_conflict":
        return _sh(f'python3 governance/global_conflicts.py --base {args.get("base", "HEAD~1")} '
                   f'--repo "{rp or "."}" --json')
    if name == "patch_queue":
        a = args["action"]
        cmds = {"status": "status", "claim": f'claim {args.get("series", "S?")} '
                 + " ".join(args.get("files", [])),
                "release": f'release {args.get("series", "S?")}',
                "precheck": f'precheck {args.get("patch", "")}'}
        return _sh(f"python3 governance/patch_queue.py {cmds[a]}")
    if name == "deep_plan":
        return deep_plan(args["question"])
    return "unknown tool"


def deep_plan(question):
    try:
        from openai import OpenAI
    except ImportError:
        return "openai 未装——降级：循环内规划"
    if not api_key():
        return "API key 未配置——降级"
    client = OpenAI(base_url=base_url(), api_key=api_key())
    sys_p = (Path(ROOT / "AGENTS.md").read_text()[:6000]
             + "\n\n你是 RL 研究审查员。给出：改动文件/验证层级/风险点（seed?环境版本?reward 定义?）。不写代码。")
    d = resolve_dialect()
    try:
        r = client.chat.completions.create(
            model=thinker_model(),
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": question}],
            **d["thinker_kwargs"])
        return _cap(r.choices[0].message.content or "(thinker 无 content)")
    except Exception as e:
        return f"thinker 失败（{e}）——降级回 loop"


def est_tokens(msgs):
    return sum(len(str(m.get("content", ""))) for m in msgs) // 4


def maybe_compact(messages, ledger):
    if est_tokens(messages) < COMPACT_TRIGGER * WINDOW:
        return messages
    ledger.wrap_up("[auto] pre-compact flush")
    head = "\n".join(str(m.get("content", ""))[:400] for m in messages[:4])
    compacted = [{"role": "user",
                  "content": f"[compact] 前情摘要（原文已压缩，详情查 state/progress.md）:\n{head}"}]
    tail_chars, tail = KEEP_RECENT, []
    for m in reversed(messages):
        if tail_chars <= 0:
            break
        tail.insert(0, m)
        tail_chars -= len(str(m.get("content", "")))
    return compacted + tail


def run(task, max_turns=MAX_TURNS_DEFAULT):
    from openai import OpenAI
    client = OpenAI(base_url=base_url(), api_key=api_key())
    dialect = resolve_dialect()
    ledger = Ledger()
    agents_md = (ROOT / "AGENTS.md").read_text() if (ROOT / "AGENTS.md").exists() else "You are an RL research agent."
    messages = [{"role": "system", "content": agents_md},
                {"role": "user", "content": f"[断点续传]\n{ledger.progress.read_text()[-2000:]}\n\n[TASK]\n{task}"}]
    for turn in range(max_turns):
        messages = maybe_compact(messages, ledger)
        r = client.chat.completions.create(model=loop_model(), messages=messages,
                                           tools=TOOLS, **dialect["loop_kwargs"])
        msg = r.choices[0].message
        if not msg.tool_calls:
            ledger.wrap_up(f"[done] {msg.content[:200]}")
            return msg.content
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            ok, why = authorize(tc.function.name, args)
            print(f"[audit] {tc.function.name} -> {'ALLOW' if ok else 'DENY ' + why}")
            result = exec_tool(tc.function.name, args) if ok else f"DENIED: {why}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    ledger.wrap_up(f"[timeout] {max_turns} turns —— 交接：按 progress.md 续跑")
    return "TIMEOUT（已交接）"


def self_test():
    print("== rl_host self-test ==")
    ok = True

    def check(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'✓' if cond else '✗'}] {name}")

    check("plugin.json 解析", bool(json.loads((ROOT / "plugin.json").read_text())))
    check(f"工具注册 {len(TOOLS)} 个", len(TOOLS) >= 12 and len(TOOL_NAMES) == len(TOOLS))
    check("authorize 拦 pip install", authorize("run_verify", {"cmd": "pip install torch"})[0] is False)
    check("authorize 拒未知工具", authorize("qq", {})[0] is False)
    for shf in sorted((ROOT / "tools").glob("*.sh")):
        rc = subprocess.run(f"bash -n {shf}", shell=True).returncode
        check(f"bash -n {shf.name}", rc == 0)
    # L3 冒烟真实跑（纯标准库，秒级）
    rc = subprocess.run("python3 tools/rl_smoke.py", shell=True, cwd=str(ROOT),
                        capture_output=True, text=True, timeout=120)
    check("rl_smoke.py 训练冒烟", rc.returncode == 0)
    print("    └ " + (rc.stdout.strip().splitlines()[-1] if rc.stdout.strip() else rc.stderr[-100:]))
    for py in ["goodhart_guards.py", "global_conflicts.py", "patch_queue.py"]:
        rc2 = subprocess.run(f"python3 governance/{py} --self-test", shell=True,
                             cwd=str(ROOT), capture_output=True, text=True)
        check(f"{py} --self-test", rc2.returncode == 0)
    led = Ledger()
    n0 = len(led.progress.read_text())
    led.wrap_up("[self-test] 账本写入验证")
    check("progress.md 只追加", len(led.progress.read_text()) > n0)
    from engines.dialects import DIALECTS
    check(f"方言注册表 {len(DIALECTS)} 引擎", all(
        "loop_kwargs" in v and "thinker_kwargs" in v for v in DIALECTS.values()))
    d = resolve_dialect()
    print(f"  [i] 引擎={d['name']} loop={loop_model()} thinker={thinker_model()}")
    print("self-test:", "ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--task")
    ap.add_argument("--max-turns", type=int, default=MAX_TURNS_DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.task:
        ap.error("给 --task 或 --self-test")
        return 2
    if not api_key():
        print("缺 API key（export KH_API_KEY=...）")
        return 2
    print(run(args.task, args.max_turns))


if __name__ == "__main__":
    sys.exit(main())
