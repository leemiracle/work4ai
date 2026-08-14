#!/usr/bin/env python3
"""
mini_agent.py — 一个 ~150 行的最小 Agentic 代码生成回路 (Act / ReAct 范式)
==========================================================================
这是"第三幕:最小代码生成回路"的可运行示范。
工具(环境): read_file / list_dir / write_file / run_shell
大脑(策略): 可插拔 — MockBrain(确定性, 无需 API) 或 LLMBrain(OpenAI 兼容, 含本地 vLLM/SGLang/GLM)
循环: 感知 -> 思考(产出 action JSON) -> 行动(执行 tool) -> 观察结果 -> ... 直到 done 或步数耗尽

用法:
  python3 mini_agent.py --mock                 # 用 MockBrain 跑确定性演示 (验证回路本身)
  python3 mini_agent.py --task "你的任务"       # 用真实 LLM (需 OPENAI_API_KEY / OPENAI_BASE_URL)
"""
import argparse, json, os, subprocess, sys, textwrap, traceback

MAX_STEPS = 12
ROOT = os.path.dirname(os.path.abspath(__file__))          # .../codegen/scripts/

# ─────────────────────────────────────────────────────────────────────────────
# 1. 工具层 (Environment) — agent 与真实文件系统 / shell 交互的唯一接口
# ─────────────────────────────────────────────────────────────────────────────
def _safe(path):
    """沙箱化: 只允许在 ROOT 目录树内操作, 防止 agent 越界改坏宿主工程。"""
    p = os.path.normpath(os.path.join(ROOT, path))
    if not (p == ROOT or p.startswith(ROOT + os.sep)):
        raise PermissionError(f"path outside sandbox: {path}")
    return p

def tool_read_file(path):
    p = _safe(path)
    if not os.path.isfile(p):
        return f"[error] not a file: {path}"
    return open(p, encoding="utf-8").read()[:8000]

def tool_list_dir(path):
    p = _safe(path)
    if not os.path.isdir(p):
        return f"[error] not a dir: {path}"
    return "\n".join(sorted(os.listdir(p)))

def tool_write_file(path, content):
    p = _safe(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)
    return f"[ok] wrote {len(content)} chars -> {path}"

def tool_run_shell(cmd):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
        return f"[exit {r.returncode}]\n{(r.stdout + r.stderr)[:4000]}"
    except Exception as e:
        return f"[error] {e}"

TOOLS = {
    "read_file": tool_read_file,
    "list_dir":  tool_list_dir,
    "write_file": tool_write_file,
    "run_shell": tool_run_shell,
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. 大脑层 (Brain) — 把「任务 + 历史」映射成下一个 action
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM = textwrap.dedent("""\
    你是一个最小编程 agent。每一步输出且仅输出一个 JSON action:
      {"tool": "read_file"|"list_dir"|"write_file"|"run_shell"|"done", "args": {...}}
    读文件: {"tool":"read_file","args":{"path":"demo/calc.py"}}
    写文件: {"tool":"write_file","args":{"path":"demo/calc.py","content":"..."}}
    跑命令: {"tool":"run_shell","args":{"cmd":"python3 -m pytest demo/test_calc.py -q"}}
    完成时: {"tool":"done","args":{"summary":"一句话总结"}}
    """)

class MockBrain:
    """确定性大脑: 硬编码一条修复 demo/calc.py 的轨迹, 用来验证回路本身能跑通。"""
    def __init__(self, task):
        self.plan = [
            {"tool": "list_dir",  "args": {"path": "."}},
            {"tool": "read_file", "args": {"path": "demo/calc.py"}},
            {"tool": "read_file", "args": {"path": "demo/test_calc.py"}},
            {"tool": "write_file", "args": {"path": "demo/calc.py",
                "content": "def add(a, b):\n    return a + b\n\n"
                           "def sub(a, b):\n    return a - b\n"}},
            {"tool": "run_shell", "args": {"cmd": "python3 -m pytest demo/test_calc.py -q"}},
            {"tool": "done", "args": {"summary": "calc.add 原为 a-b(应为 a+b), 修复后测试通过"}},
        ]
        self.i = 0

    def next_action(self, history):
        if self.i < len(self.plan):
            a = self.plan[self.i]; self.i += 1; return a
        return {"tool": "done", "args": {"summary": "mock plan exhausted"}}

class LLMBrain:
    """真实大脑: 调用任意 OpenAI 兼容接口 (云模型 / 本地 vLLM、SGLang、GLM)。"""
    def __init__(self, task):
        from openai import OpenAI
        self.client = OpenAI()                       # 读 OPENAI_API_KEY / OPENAI_BASE_URL
        self.model = os.environ.get("CODEGEN_MODEL", "gpt-4o-mini")
        self.history = [{"role": "system", "content": SYSTEM},
                        {"role": "user", "content": "任务: " + task}]

    def next_action(self, _):
        resp = self.client.chat.completions.create(
            model=self.model, messages=self.history, temperature=0.2,
            response_format={"type": "json_object"})
        msg = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": msg})
        return _parse_json(msg)

def _parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        a, b = s.find("{"), s.rfind("}")
        return json.loads(s[a:b+1]) if a >= 0 else {"tool": "done", "args": {"summary": s}}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Agent 主循环 — observe -> think -> act -> observe ... (Act 范式)
# ─────────────────────────────────────────────────────────────────────────────
def run(task, brain, max_steps=MAX_STEPS, verbose=True):
    history = []
    for step in range(1, max_steps + 1):
        action = brain.next_action(history)
        tool, args = action.get("tool"), action.get("args", {})
        if verbose:
            print(f"\n— step {step} — {tool} " + json.dumps(args, ensure_ascii=False)[:160])
        if tool == "done":
            print(f"\n✅ DONE: {args.get('summary', '')}"); return 0
        fn = TOOLS.get(tool)
        if not fn:
            obs = f"[error] unknown tool: {tool}"
        else:
            try:
                obs = fn(**args)
            except TypeError as e:
                obs = f"[error] bad args: {e}"
            except Exception as e:
                obs = f"[error] {e}\n{traceback.format_exc()[:500]}"
        history.append({"step": step, "action": action, "observation": obs})
        if verbose:
            print(_clip(obs, 600))
    print("\n⏹ reached max steps"); return 1

def _clip(s, n):
    return s if len(s) <= n else s[:n] + " …[truncated]"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="最小 agentic 代码生成回路")
    ap.add_argument("--mock", action="store_true", help="用确定性 MockBrain 演示回路")
    ap.add_argument("--task", default=None, help="任务描述(配合真实 LLM 使用)")
    a = ap.parse_args()
    task = a.task or "修复 demo/calc.py 中的 add 函数, 使 demo/test_calc.py 全部通过"
    brain = MockBrain(task) if a.mock else LLMBrain(task)
    sys.exit(run(task, brain))
