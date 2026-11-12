#!/usr/bin/env python3
"""mini-claude v2：可运行的简化版 Claude Code（file-state + autocompact + 遥测）。

逆向自 Claude Code v2.1.261（详见 ../02-agent-loop.md 等分册），v2 落地三个
逆向实证的核心机制：

  1. file-state 跟踪（../03-tools.md §5）：Read 成功记 {mtime, lines}；
     Edit/Write 前置校验"读过且未变更"（ec=6 not-read / ec=7 stale，
     文案与 Claude Code 同款）；同参重读 mtime 未变 → file_unchanged 去重。
  2. autocompact 真摘要（../02-agent-loop.md §3）：超阈值用另一次 LLM 调用
     生成 8 段式摘要（Primary Request/Key Concepts/Files/Errors/...），
     失败回退骨架版；连续 3 次失败熔断（本会话不再自动 compact）。
  3. 遥测三元组（../13-telemetry.md §6）：(state, action, outcome) JSONL
     落盘 .mini-claude/telemetry/<sid>.jsonl——tool_use/turn_end/compact/
     file_read_dedup 四组事件，对齐 Claude Code 的 tengu_* 设计。

agent loop 骨架不变（单层 while + 工具结果回填再循环）。v2 起工具结果
回填后直接续轮（不再注入 "(continue)" 占位）。

依赖：仅 Python 标准库。端点：智谱 coding plan（OpenAI 兼容）：
  ZHIPU_CODING_BASE_URL（默认 https://open.bigmodel.cn/api/coding/paas/v4）
  ZHIPU_CODING_API_KEY
用法：
  python3 mini_claude.py                 # 交互 REPL
  python3 mini_claude.py -p "任务描述"    # 非交互单任务
  python3 mini_claude.py --model glm-5.3-flash --max-turns 40
  MINI_AUTOCOMPACT_THRESHOLD=3000 …      # 调低阈值观察 compact（调试用）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# ─────────────────────────── 配置 ───────────────────────────

MODEL = os.environ.get("MINI_CLAUDE_MODEL", "glm-5.3")
BASE_URL = (os.environ.get("ZHIPU_CODING_BASE_URL")
            or "https://open.bigmodel.cn/api/coding/paas/v4").rstrip("/")
API_KEY = os.environ.get("ZHIPU_CODING_API_KEY", "")
MAX_TOKENS = 8192
TEMPERATURE = 0.3
REQUEST_TIMEOUT = 300          # 单次 API 请求超时（reasoning 模型要放宽）
RETRY_MAX = 4                  # 429/5xx 指数退避
CONTEXT_BUDGET = 100_000       # token 粗估上限，超过触发压缩
AUTOCOMPACT_THRESHOLD = int(os.environ.get("MINI_AUTOCOMPACT_THRESHOLD")
                            or CONTEXT_BUDGET)          # compact 阈值（可调低测试）
TOOL_OUTPUT_LIMIT = 20_000     # 单个工具输出字符截断
BASH_TIMEOUT = 120             # 秒
COMPACT_FAIL_CAP = 3           # 连续 compact 失败熔断（对齐 Claude Code iQn=3）

SESSION_ID = uuid.uuid4().hex[:12]
TELEMETRY_DIR = Path.cwd() / ".mini-claude" / "telemetry"

# Bash 黑名单：先于白名单判断（对应 Claude Code 的 permission deny 规则）
BASH_DENY = [
    r"\brm\s+-rf\s+/(?:\s|$)", r"\bmkfs\b", r"\bdd\s+if=.*of=/dev/",
    r":\(\)\s*\{\s*:\|:\s*&\s*\};:",      # fork bomb
    r"\bshutdown\b", r"\breboot\b", r">\s*/dev/sda",
]
# 需要确认的命令（交互模式下询问；非交互模式下默认拒绝）
BASH_ASK = [r"\bgit\s+push\b", r"\bnpm\s+publish\b", r"\bpip\s+install\b",
            r"\bcurl\b.*\|\s*(ba)?sh", r"\bwget\b.*&&\s*sh"]


# ─────────────────────────── 遥测三元组（对应 13 册 §6 数据飞轮）───────────
# (state, action, outcome)：tool_use/turn_end/compact/file_read_dedup 四组事件，
# 关联键 session_id（贯穿）+ turn（回合）+ tool_call_id（工具调用）。

def emit(kind: str, **fields) -> None:
    """追加一条 JSONL 遥测事件（发不出去也不影响主流程）。"""
    try:
        TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind,
               "session_id": SESSION_ID, **fields}
        with open(TELEMETRY_DIR / f"{SESSION_ID}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ─────────────────────────── file-state 系统（对应 03 册 §5）───────────
# Read 成功 → 记 {mtime, lines}；Edit/Write 前置校验；同参重读去重。
# 一个机制三个功能：免重读 + stale 检测 + 冗余拦截。

READ_STATE: dict[str, dict] = {}   # path → {mtime, lines, offset, limit}


def _check_write_premise(p: Path) -> str | None:
    """Edit/Write 的读前置校验（ec=6/7，文案对齐 Claude Code）。新文件免校验。"""
    if not p.exists():
        return None                                  # CreateFile 不需先读
    st = READ_STATE.get(str(p))
    if st is None:
        return ("File has not been read yet. Read it first before writing to it. "
                f"(hint: Read {p} then retry)")
    if p.stat().st_mtime > st["mtime"]:
        return ("File has been modified since read, either by the user or by another "
                "process. Read it again before writing.")
    return None


def _record_read(p: Path, lines: list[str], offset: int, limit: int) -> None:
    READ_STATE[str(p)] = {"mtime": p.stat().st_mtime, "lines": len(lines),
                          "offset": offset, "limit": limit}


FILE_STATE_SUFFIX = " (file state is current in your context — no need to Read it back)"

SYSTEM_PROMPT = """You are mini-claude, a minimal agentic coding assistant \
(reverse-engineered from Claude Code's architecture).

You accomplish tasks through an agentic loop: think → call one tool → observe \
the result → continue, until the task is done. Rules:

1. Prefer tools over guessing: read files before editing, run commands to \
verify, never fabricate file contents or command output.
2. One step at a time: issue tool calls, wait for results, then decide. \
Do not assume a tool succeeded without seeing its output.
3. Keep going autonomously until the task is DONE, then summarize: what was \
changed, which files, what was verified (tests/commands run and their results).
4. If a step fails twice with the same approach, change strategy instead of \
repeating it. Report honestly what failed.
5. Be surgical: minimal edits, match existing code style.

Available tools: bash, read, write, edit, glob, grep, todo.

Current working directory: {cwd}"""

# ─────────────────────────── 工具定义（OpenAI function calling schema）──────────

TOOLS = [
    {"type": "function", "function": {
        "name": "bash",
        "description": "Run a shell command in the workspace. Returns stdout+stderr "
                       f"(truncated to {TOOL_OUTPUT_LIMIT} chars). Timeout {BASH_TIMEOUT}s.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "The shell command to run"}},
            "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "read",
        "description": "Read a file with line numbers (like `cat -n`). Default whole file, "
                       "max 2000 lines; use offset/limit for long files.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "offset": {"type": "integer", "description": "1-based start line"},
            "limit": {"type": "integer", "description": "max lines to read"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write",
        "description": "Create or overwrite a file with full content.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "edit",
        "description": "Replace exact old_string with new_string in a file. "
                       "old_string must be unique; include surrounding lines to disambiguate.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "old_string": {"type": "string"}, "new_string": {"type": "string"}},
            "required": ["path", "old_string", "new_string"]}}},
    {"type": "function", "function": {
        "name": "glob",
        "description": "Find files by glob pattern (e.g. '**/*.py'), newest first.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "grep",
        "description": "Regex search across files. Returns matches as path:line:text (capped).",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"},
            "path": {"type": "string", "description": "file or dir, default '.'"}},
            "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "todo",
        "description": "Create/replace the task list. Use for multi-step tasks: one item per step, "
                       "mark in_progress before starting, completed when done.",
        "parameters": {"type": "object", "properties": {
            "todos": {"type": "array", "items": {"type": "object", "properties": {
                "content": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}},
                "required": ["content", "status"]}}},
            "required": ["todos"]}}},
]

# ─────────────────────────── 工具实现 ───────────────────────────

def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    return p if p.is_absolute() else (Path.cwd() / p)


def _guard_write(p: Path) -> str | None:
    """写操作限制在工作区（含上级引用拦截）。"""
    wd = Path.cwd().resolve()
    rp = p.resolve() if p.exists() else (p.parent.resolve() / p.name)
    if not str(rp).startswith(str(wd)):
        return f"REFUSED: {rp} is outside workspace {wd}"
    return None


def tool_bash(command: str) -> str:
    cmd = command
    for pat in BASH_DENY:
        if re.search(pat, cmd):
            return f"REFUSED: command matches deny rule {pat!r}"
    for pat in BASH_ASK:
        if re.search(pat, cmd):
            if not sys.stdin.isatty():
                return "REFUSED: interactive-confirm command in non-interactive mode"
            ans = input(f"  ⚠ allow? {cmd} [y/N] ").strip().lower()
            if ans != "y":
                return "REFUSED by user"
    try:
        r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                           timeout=BASH_TIMEOUT, cwd=str(Path.cwd()))
        out = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr.strip() else "")
        head = f"[exit {r.returncode}] "
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {BASH_TIMEOUT}s"
    out = head + (out or "(no output)")
    return out if len(out) <= TOOL_OUTPUT_LIMIT else out[:TOOL_OUTPUT_LIMIT] + f"\n…[truncated, {len(out)} chars total]"


def tool_read(path: str, offset: int = 1, limit: int = 2000) -> str:
    p = _resolve(path)
    if not p.is_file():
        return f"ERROR: not a file: {p}"
    # 去重：同 offset/limit 且 mtime 未变 → 拒绝重读（对齐 file_unchanged）
    st = READ_STATE.get(str(p))
    if st and st["offset"] == (offset or 1) and st["limit"] == (limit or 2000) \
            and p.stat().st_mtime <= st["mtime"]:
        emit("file_read_dedup", path=str(p), source="mtime_hit")
        return ("File unchanged since last read. The content from the earlier Read "
                "tool result in this conversation is still current — refer to that "
                "instead of re-reading.")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    off = max(1, offset or 1)
    sel = lines[off - 1: off - 1 + (limit or 2000)]
    if not sel:
        return f"(empty range: file has {len(lines)} lines)"
    _record_read(p, lines, off, limit or 2000)
    body = "\n".join(f"{n:>6}\t{l}" for n, l in enumerate(sel, off))
    return body + f"\n(showing lines {off}-{off + len(sel) - 1} of {len(lines)})"


def tool_write(path: str, content: str) -> str:
    p = _resolve(path)
    if err := _guard_write(p):
        return err
    if err := _check_write_premise(p):
        return f"ERROR: {err}"
    p.parent.mkdir(parents=True, exist_ok=True)
    existed = p.exists()
    p.write_text(content, encoding="utf-8")
    _record_read(p, content.splitlines(), 1, 2000)   # 写后 state 即最新
    return f"{'Overwrote' if existed else 'Created'} {p} ({len(content)} chars)" + FILE_STATE_SUFFIX


def tool_edit(path: str, old_string: str, new_string: str) -> str:
    p = _resolve(path)
    if not p.is_file():
        return f"ERROR: not a file: {p}"
    if err := _check_write_premise(p):
        return f"ERROR: {err}"
    t = p.read_text(encoding="utf-8", errors="replace")
    n = t.count(old_string)
    if n == 0:
        return ("ERROR: String to replace not found in file. "
                "Read the file again — it may have changed.")
    if n > 1:
        return (f"ERROR: Found {n} matches of the string to replace. "
                "Add surrounding context lines to make it unique.")
    p.write_text(t.replace(old_string, new_string, 1), encoding="utf-8")
    _record_read(p, t.replace(old_string, new_string, 1).splitlines(), 1, 2000)
    return (f"Edited {p}: replaced {len(old_string)} chars with {len(new_string)}"
            + FILE_STATE_SUFFIX)


def tool_glob(pattern: str) -> str:
    hits = [str(p) for p in Path.cwd().glob(pattern) if ".git/" not in str(p)]
    hits.sort(key=lambda p: -os.path.getmtime(p) if os.path.exists(p) else 0)
    if not hits:
        return "(no matches)"
    return "\n".join(hits[:200]) + (f"\n…[{len(hits)} total]" if len(hits) > 200 else "")


def tool_grep(pattern: str, path: str = ".") -> str:
    rx = re.compile(pattern)
    root = _resolve(path)
    files = [root] if root.is_file() else [p for p in root.rglob("*")
                                           if p.is_file() and ".git/" not in str(p)]
    out, cap = [], 200
    for p in files[:2000]:
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if rx.search(line):
                    out.append(f"{p}:{i}:{line.strip()[:200]}")
                    if len(out) >= cap:
                        return "\n".join(out) + f"\n…[capped at {cap} matches]"
        except OSError:
            continue
    return "\n".join(out) if out else "(no matches)"


def tool_todo(todos: list[dict]) -> str:
    icons = {"pending": "○", "in_progress": "◐", "completed": "●"}
    rows = [f"  {icons.get(str(t.get('status')), '?')} {t.get('content', '')}" for t in todos]
    print("\n📋 todo list:\n" + "\n".join(rows) + "\n", flush=True)
    return "todo list updated and shown to user"


TOOL_IMPL = {"bash": tool_bash, "read": tool_read, "write": tool_write,
             "edit": tool_edit, "glob": tool_glob, "grep": tool_grep,
             "todo": tool_todo}

# ─────────────────────────── API 客户端（重试+流式可选）──────────

def chat(messages: list, tools: list[dict] | None = None,
         stream: bool = False) -> tuple[str, list[dict]]:
    """调 /chat/completions，返回 (content, tool_calls)。"""
    if not API_KEY:
        sys.exit("缺少 ZHIPU_CODING_API_KEY 环境变量")
    body = {"model": MODEL, "messages": messages, "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE, "stream": stream}
    if tools:
        body["tools"] = tools
    delay = 2.0
    for attempt in range(RETRY_MAX + 1):
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions", method="POST",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {API_KEY}"})
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                data = json.loads(r.read())
            msg = data["choices"][0]["message"]
            return msg.get("content") or "", msg.get("tool_calls") or []
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < RETRY_MAX:
                print(f"  ⚠ HTTP {e.code}, retry in {delay:.0f}s…", flush=True)
                time.sleep(delay); delay *= 2; continue
            detail = e.read()[:300].decode("utf-8", "replace")
            raise RuntimeError(f"API HTTP {e.code}: {detail}") from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < RETRY_MAX:
                print(f"  ⚠ {type(e).__name__}, retry in {delay:.0f}s…", flush=True)
                time.sleep(delay); delay *= 2; continue
            raise
    raise RuntimeError("unreachable")


# ─────────────────────────── 上下文管理（压缩）──────────

def est_tokens(messages: list[dict]) -> int:
    """粗估：英文 ~4 chars/token，中文 ~1.5 字/token → 统一 chars/2.8。"""
    return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages) // 3


def compact_skeleton(messages: list[dict], keep_recent: int = 6) -> list[dict]:
    """骨架版压缩（回退路径）：老轮次只留轮次骨架，丢工具输出详情。"""
    if len(messages) <= keep_recent + 1:
        return messages
    head = messages[0] if messages[0]["role"] == "system" else None
    old = messages[:-keep_recent]
    recent = messages[-keep_recent:]
    skel = []
    for m in old[:200]:
        r = m.get("role", "?")
        c = m.get("content")
        if isinstance(c, str):
            skel.append(f"{r}: {c[:120]}")
        elif isinstance(c, list):
            for blk in c:
                if blk.get("type") == "function":
                    skel.append(f"assistant→tool {blk.get('name', '?')}")
        elif m.get("tool_calls"):
            names = ",".join(tc["function"]["name"] for tc in m["tool_calls"])
            skel.append(f"assistant tools: {names}")
        elif m.get("role") == "tool":
            skel.append("tool result: (elided)")
    summary = ("[context compacted] Earlier turns summarized. Skeleton:\n"
               + "\n".join(skel[-80:]))
    return ([head] if head else []) + [{"role": "user", "content": summary}] + recent


# 8 段式摘要模板（对齐 Claude Code 实证模板：02 册 §3.3，querySource="compact"）
SUMMARY_SYSTEM = "You are a helpful AI assistant tasked with summarizing conversations."
COMPACT_PROMPT = """Summarize our conversation so far in exactly this structure:

1. Primary Request and Intent:
   The user's main request and any additional details such as ask/assume/answer.
2. Key Technical Concepts:
   Files, functions, APIs, algorithms and domain knowledge central to the task.
3. Files and Code Sections:
   Each file read or edited, with the purpose of key sections.
4. Errors and fixes:
   Errors encountered and how they were fixed (or remain open).
5. Problem Solving:
   Approaches tried, what worked and what did not.
6. All user messages:
   The complete list of the user's non-tool-result messages, numbered, near-verbatim.
7. Pending Tasks:
   Anything not yet finished (with the exact next step).
8. Current Work / Next Step:
   Where the conversation stands right now and the immediate next action.

Be specific and terse; the summary replaces the full history in context."""


def compact(messages: list[dict], keep_recent: int = 6,
            failure_count: int = 0) -> tuple[list[dict], str]:
    """autocompact v2：LLM 8 段式真摘要，失败回退骨架版。

    返回 (新消息列表, method: "llm"|"skeleton"|"noop")。对齐 Claude Code：
    独立摘要调用（不同 system）+ 连续失败熔断在调用方计数。
    """
    if len(messages) <= keep_recent + 1:
        return messages, "noop"
    head = messages[0] if messages[0]["role"] == "system" else None
    old = messages[:-keep_recent] if head else messages[:-keep_recent]
    recent = messages[-keep_recent:]
    if failure_count >= COMPACT_FAIL_CAP:            # 熔断：直接骨架版
        return compact_skeleton(messages, keep_recent), "skeleton"
    try:
        digest = json.dumps(
            [{"role": m.get("role"),
              "content": (m.get("content") if isinstance(m.get("content"), str)
                          else json.dumps(m.get("content") or m.get("tool_calls") or "",
                                          ensure_ascii=False)[:400])}
             for m in old], ensure_ascii=False)
        text, _ = chat([{"role": "system", "content": SUMMARY_SYSTEM},
                        {"role": "user", "content": COMPACT_PROMPT + "\n\nConversation:\n" + digest}],
                       tools=None)
        lead = ("This session is being continued from a previous conversation that "
                "ran out of context. The summary of that conversation is:\n\n")
        return ([head] if head else []) + [{"role": "user", "content": lead + text}] + recent, "llm"
    except Exception as e:                            # noqa: BLE001 — 摘要失败不致命
        print(f"  ⚠ compact LLM summary failed ({e}); falling back to skeleton", flush=True)
        return compact_skeleton(messages, keep_recent), "skeleton"


# ─────────────────────────── Agent 主循环 ───────────────────────────

def load_project_context() -> str:
    """对应 Claude Code 的 CLAUDE.md 注入：项目说明进 system prompt。"""
    for name in ("CLAUDE.md", "AGENTS.md"):
        p = Path.cwd() / name
        if p.is_file():
            return f"\n\n# Project context ({name})\n{p.read_text(encoding='utf-8', errors='replace')[:8000]}"
    return ""


def run_agent(task: str, max_turns: int = 30) -> str:
    system = SYSTEM_PROMPT.format(cwd=Path.cwd()) + load_project_context()
    messages: list = [{"role": "system", "content": system}]
    turns = 0
    content = ""
    compact_fails = 0
    emit("session_start", model=MODEL, cwd=str(Path.cwd()), task=task[:200])
    while True:
        turns += 1
        if turns > max_turns:
            print(f"\n⏹ max turns ({max_turns}) reached")
            emit("turn_end", turns=turns - 1, outcome="max_turns")
            break
        # ── autocompact（02 册：每 turn 先压缩再发请求）──
        if est_tokens(messages) > AUTOCOMPACT_THRESHOLD:
            before = est_tokens(messages)
            print("  🗜 autocompact triggered", flush=True)
            messages, method = compact(messages, failure_count=compact_fails)
            ok = method == "llm"
            compact_fails = 0 if ok else compact_fails + 1
            emit("compact", trigger="auto", before_tokens=before,
                 after_tokens=est_tokens(messages), method=method,
                 boundary=turns, consecutive_failures=compact_fails)
            if compact_fails >= COMPACT_FAIL_CAP:
                print("  ⚠ compact circuit breaker open (skeleton mode)", flush=True)
        if turns == 1:
            messages.append({"role": "user", "content": task})
        content, tool_calls = chat(messages, TOOLS)
        if content:
            print(f"\n🤖 {content}", flush=True)
        if not tool_calls:
            emit("turn_end", turns=turns, outcome="completed")   # episode 终局信号
            return content                       # 终止：模型不再调工具
        # 记录 assistant 轮（含 tool_calls），然后逐个执行工具
        messages.append({"role": "assistant", "content": content,
                         "tool_calls": tool_calls})
        for tc in tool_calls:
            fn, args = tc["function"]["name"], tc["function"]["arguments"]
            t0 = time.time()
            try:
                parsed = json.loads(args or "{}")
            except json.JSONDecodeError:
                result = f"ERROR: invalid JSON args: {args[:200]}"
            else:
                print(f"  🔧 {fn}({json.dumps(parsed, ensure_ascii=False)[:160]})", flush=True)
                impl = TOOL_IMPL.get(fn)
                result = impl(**parsed) if impl else f"ERROR: unknown tool {fn}"
            # (state→action→outcome) 三元组的 action+outcome 落盘
            emit("tool_use", turn=turns, tool_call_id=tc.get("id"), name=fn,
                 args_head=(args or "")[:200], outcome=str(result)[:80],
                 is_error=str(result).startswith(("ERROR", "REFUSED", "TIMEOUT")),
                 duration_ms=int((time.time() - t0) * 1000))
            messages.append({"role": "tool", "tool_call_id": tc["id"],
                             "content": str(result)})
        # v2：工具结果已回填，直接续轮（OpenAI 协议允许 tool 结尾，无需占位）
    return content


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    global MODEL
    ap = argparse.ArgumentParser(description="mini-claude: 最小可运行 coding agent")
    ap.add_argument("prompt", nargs="*", help="任务描述；省略则进入交互 REPL")
    ap.add_argument("-p", "--print", action="store_true", help="非交互模式")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-turns", type=int, default=30)
    args = ap.parse_args()
    MODEL = args.model

    task = " ".join(args.prompt).strip()
    if task:
        run_agent(task, max_turns=args.max_turns)
        return
    if not sys.stdin.isatty():
        sys.exit("非交互环境请用: mini_claude.py -p '任务' 或传入 prompt 参数")
    print(f"mini-claude · {MODEL} · workspace {Path.cwd()} · exit/quit 退出")
    while True:
        try:
            line = input("\n❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if line in ("exit", "quit", ""):
            break
        run_agent(line, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
