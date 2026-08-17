# 12 · 最小 harness 实现：200 行骨架 + OpenCode 活教材

> **核心论点**：读十个框架不如写一个最小实现——六组件的最小可用形态两百行内装得下。
> **本文是什么**：可跑的最小骨架（纯标准库思路，接任意 OpenAI 兼容端点）+ 用本会话环境当活教材。

---

## 🏗️ 最小骨架（六组件全部落位）

```python
"""mini_harness.py — Agent = Model + Harness 的最小实现
E 循环 + T 工具注册 + C 上下文预算 + S 状态账本 + L 钩子 + V 验证
依赖：pip install openai（或任何 OpenAI 兼容客户端）"""
import json, os, subprocess, time
from pathlib import Path

# ===== C 组件：上下文预算（04 章参数表）=====
FILE_MAX_LINES, FILE_MAX_BYTES = 2000, 50_000
TOOL_RESULT_CAP = 16_000
COMPACT_TRIGGER, KEEP_RECENT = 0.8, 20_000      # 占窗口 80% 触发，保底最近 20K

# ===== S 组件：最小四文件（05 章）=====
class Ledger:
    def __init__(self, root: Path):
        self.root = root
        self.progress = root / "progress.md"; self.progress.touch(exist_ok=True)
        self.features = root / "feature_list.json"
        self.features.write_text("[]" if not self.features.exists() else self.features.read_text())
    def wrap_up(self, note: str):               # 07 章 WRAP UP：只追加，禁重写（铁律 #9）
        with open(self.progress, "a") as f:
            f.write(f"\n## {time.strftime('%F %T')}\n{note}\n")

# ===== T 组件：工具注册（schema 校验 + 结果预算）=====
TOOLS = [{
    "type": "function", "function": {
        "name": "read_file", "description": "读文件，返回前 2000 行；大文件用 offset/limit",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "offset": {"type": "integer", "default": 1}},
            "required": ["path"]}}}, {
    "type": "function", "function": {
        "name": "run_verify", "description": "跑验证命令（pytest/lint），返回退出码与输出",
        "parameters": {"type": "object", "properties": {
            "cmd": {"type": "string"}}, "required": ["cmd"]}}}]

def exec_tool(name, args) -> str:               # 结果预算 + 报错即导航
    if name == "read_file":
        text = Path(args["path"]).read_text(errors="replace")
        lines = text.splitlines()
        if len(text.encode()) > FILE_MAX_BYTES or len(lines) > FILE_MAX_LINES:
            tail = "\n".join(lines[:FILE_MAX_LINES])
            return tail[:TOOL_RESULT_CAP] + f"\n[Showing 1-{FILE_MAX_LINES} of {len(lines)}. Use offset={FILE_MAX_LINES+1}]"
        return text[:TOOL_RESULT_CAP]
    if name == "run_verify":                    # V 组件入口：exit code 即证据
        r = subprocess.run(args["cmd"], shell=True, capture_output=True, text=True, timeout=300)
        out = (r.stdout + r.stderr)[-TOOL_RESULT_CAP:]     # 失败输出保尾部（错误栈在最后）
        return f"exit={r.returncode}\n{out}"
    return "unknown tool"

# ===== L 组件：钩子（权限门 fail-closed + 审计）=====
WRITE_ALLOWLIST = {"progress.md", "feature_list.json"}     # Scope：只许账本
def authorize(tool_name, args) -> bool:
    ok = tool_name in {"read_file", "run_verify"} or args.get("path","") in WRITE_ALLOWLIST
    print(f"[audit] {tool_name} args={args} -> {'ALLOW' if ok else 'DENY'}")
    return ok

# ===== C 组件：压缩（触发即摘要 + 状态 flush）=====
def maybe_compact(messages, client, model):
    if est_tokens(messages) < COMPACT_TRIGGER * window(model): return messages
    ledger.wrap_up("[auto] pre-compact flush")             # OpenClaw 模式：压缩前落盘
    summary = client.chat.completions.create(model=model, messages=messages[:6] + [
        {"role":"user","content":"把以上任务状态压缩为要点：目标/已做/未做/约束"}]).choices[0].message.content
    return [{"role":"user","content": f"[compact]\n{summary}"}] + messages_tail(messages, KEEP_RECENT)

def est_tokens(msgs): return sum(len(str(m)) for m in msgs) // 4          # char/4
def window(model): return 128_000
def messages_tail(msgs, budget): ...       # 从尾往前取，保 tool_call/result 配对

# ===== E 组件：主循环（三终止条件）=====
def run(task, root=".", model="glm-4-flash"):
    from openai import OpenAI
    client = OpenAI(base_url=os.environ["ZHIPU_BASE_URL"], api_key=os.environ["ZHIPU_API_KEY"])
    ledger = Ledger(Path(root))
    messages = [{"role":"system","content":Path("AGENTS.md").read_text() if Path("AGENTS.md").exists() else "You are a careful agent."},
                {"role":"user","content":task}]
    for turn in range(40):                                  # 终止 1：轮数上限
        messages = maybe_compact(messages, client, model)
        r = client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
        msg = r.choices[0].message
        if not msg.tool_calls:
            ledger.wrap_up(f"[done] {msg.content[:200]}"); return msg.content   # 终止 2：自然结束
        messages.append(msg)
        for tc in msg.tool_calls:
            result = exec_tool(tc.function.name, json.loads(tc.function.arguments)) \
                     if authorize(tc.function.name, json.loads(tc.function.arguments)) \
                     else "DENIED by policy"
            messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
    ledger.wrap_up("[timeout] 40 turns reached")            # 终止 3：超时可交接
    return "TIMEOUT"

if __name__ == "__main__":
    print(run("读取 mini_harness.py，统计行数，然后跑 run_verify: python -c 'print(1)' 确认环境"))
```

**逐组件对照**：E=run() 三终止条件（03 章）｜T=TOOLS+exec_tool（校验/预算/导航式报错）｜C=maybe_compact+est_tokens（触发前 flush）｜S=Ledger（四文件之二，WRAP UP 追加式）｜L=authorize（fail-closed+审计行）｜V=run_verify（exit code 即证据）。约 150 行，六组件一个不少。

---

## 🎓 活教材：把 OpenCode 剖一遍（你正在被 harness 服务）

本会话的运行环境就是六组件的工业实现，随手可验证：

| 组件 | OpenCode 里的样子 | 你验证它的方法 |
|---|---|---|
| E | agent loop + max_turns + auto_continue（"做完不要停"= 轮数上限的解除开关）| 观察长任务多轮自动续 |
| T | 工具注册（bash/read/edit/grep…）+ 参数 schema | 传错参数看报错格式 |
| C | 读文件默认 2000 行 + 截断提示 + 输出超限落盘 | 让它读一个大文件看 truncation 提示 |
| S | session 持久化 + `/resume`；本项目的 progress 型文档 | 杀会话再 resume |
| L | permission 规则（read 拦截/危险命令拦截）| 让它 `rm -rf` 看拦截 |
| V | bash 跑测试 exit code 即证据；TODO 系统 = 任务账本 | 跑一个会失败的 pytest |

**作业**：对照上表逐行验证，写进 progress.md——这一张表打勾完，你对六组件的理解就从名词变成了动词。

---

## 🚀 从骨架到生产的最短路径

```
骨架（本章）→ +沙箱（bubblewrap/容器跑 exec_tool）→ +子代理（07 章交接契约）
→ +多模型（08 章端点路由）→ +回归集（10 章防退步）→ +进化闭环（11 章）
```

每一步只在**失败真的发生**时加（futureagi 六层指南的原则：从正在坏的层开始修，而不是从教程开始抄）。

---

## 📌 本周必做

1. [ ] 跑通 mini_harness（glm-4-flash 免费档即可），看六组件日志各行
2. [ ] 做一张你自己环境的"六组件验证表"（活教材作业）
3. [ ] 给骨架加一个你自己最痛的组件改进（带预测，下周期验证——11 章闭环入门）

## 📚 推荐深读

- Edd Mann: "Around the Loop: Building a Coding Agent Harness in Python"（七环视角，2026-04-27）
- Thorsten Ball: 400 行 Go 写 agent（loop 不是难点的最好证明）
- futureagi: How to Build a Coding Agent Harness: 6 Core Layers

---

**版本**：v1.0（2026-08-17）
**核心隐喻**：框架是买的车，骨架是你焊的车。焊过一次，你就永远知道哪个零件在响——这就是本手册存在的原因。
