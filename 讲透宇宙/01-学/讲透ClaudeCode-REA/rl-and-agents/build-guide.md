# 手搓指南：从零实现一个简化版 Claude Code

> 配套实现：[mini_claude.py](mini_claude.py)（v2=551 行，纯标准库；v1 405 行跑通三工具链+429 退避，v2 增 file-state/8 段式 autocompact/遥测三元组并逐项实测，见 §9.1）。
> 本指南按 Claude Code 逆向出的架构（v2.1.261）逐层展开：每一层先讲原型怎么做，
> 再讲 Claude Code 的真实做法（[S]=源码实证），最后给扩展练习。
> 读完你可以把 mini-claude 逐步升级成一个趁手的自用 agent。

## 0. 分层总图

```
┌─ CLI/REPL 层──── 参数解析、交互循环、-p 非交互模式          ← claude 的 304 行 --help
├─ 会话层──────── transcript 持久化(JSONL)、resume、--continue
├─ Agent Loop──── 主循环：LLM→tool_calls→执行→回填→再循环      ← 核心中的核心
├─ 上下文管理──── token 估算、autocompact、file-state 跟踪
├─ 工具层──────── 7~50 个工具：schema+执行+权限+输出整形
├─ 权限层──────── allowlist/denylist/ask 弹窗/bypass 模式
├─ API 客户端──── 端点、重试、流式、thinking、cache
└─ 增强件──────── hooks、MCP、子代理、skills、sandbox          ← 可全部后加
```

mini-claude 实现 1/2/3/4/5/6 的最小版；第 7 层砍掉。**这个顺序就是构建顺序**。

## 1. API 客户端（先让模型说话）

```python
def chat(messages, tools):
    body = {"model": MODEL, "messages": messages, "tools": tools, ...}
    # POST {BASE_URL}/chat/completions  (OpenAI 兼容格式)
    msg = response["choices"][0]["message"]
    return msg.get("content") or "", msg.get("tool_calls") or []
```

三个不可省的细节：
1. **重试**：429/5xx 指数退避（2s→4s→8s→16s，4 次封顶）。
2. **超时**：reasoning 模型单请求可以 3-5 分钟，别用默认 30s。
3. **工具结果格式**：OpenAI 格式是 `{"role":"tool","tool_call_id":...,"content":...}`，
   必须紧贴在带 `tool_calls` 的 assistant 消息之后，一 一对应。

Claude Code 的真实做法 [S]：原生走 Anthropic `/v1/messages`（SSE 流式、
`content_block` 增量、`tool_use` 块、`tool_result` 回填），支持 Bedrock/Vertex 双云、
429 优先读 `retry-after` 头。**流式不是必须的**——mini-claude 非流式一样能干活，
流式只是 UX（更快的首 token 反馈）。

## 2. 工具层（agent 的手）

每个工具 = 三件套：**JSON schema（给模型看）+ 执行函数（给系统跑）+ 输出整形（给上下文省 token）**。

```python
{"type":"function","function":{
  "name":"read",
  "description":"Read a file with line numbers...",
  "parameters":{"type":"object","properties":{"path":...},"required":["path"]}}}
```

七个工具就够覆盖 90% 编码任务：`bash / read / write / edit / glob / grep / todo`。
Claude Code 有 49 个工具 [S]（sdk-tools.d.ts），但高频核心同样是这 7 个。

**输出整形是隐藏的重点**：
- `read` → `cat -n` 行号格式（edit 定位用）
- `bash` → `[exit N]` 前缀 + 截断保留尾部（错误信息在尾部）
- `grep` → `path:line:text`（模型可以直接引用）
- `edit` 失败 → 语义化错误（"old_string 出现 3 次"→ 模型自纠）

Claude Code 的对应物 [S]：Edit 强制 old_string 唯一性检查；Read 默认 2000 行；
Bash 后台任务体系（run_in_background + BashOutput 轮询 + KillShell）；
file-state 跟踪（"no need to Read it back" 提示，防重复读浪费 token）。

## 3. Agent Loop（核心 60 行）

```python
def run_agent(task):
    messages = [{"role":"system","content":system_prompt()}]
    while turns < MAX_TURNS:
        content, tool_calls = chat(messages, TOOLS)
        if not tool_calls: return content          # 自然终止
        messages.append(assistant(content, tool_calls))
        for tc in tool_calls:
            messages.append(tool_msg(tc["id"], execute(tc)))
        # 循环：下一轮 LLM 看到工具结果继续决策
```

就这么多。复杂度全在三个地方的取舍：
1. **终止条件**：无 tool_calls / max_turns / 用户 ESC 中断。
   Claude Code 还有 stop_reason 分流（end_turn/max_tokens/ pause_turn 工具）[S]。
2. **并行工具调用**：一轮多个 tool_calls 串行执行 vs 并发。Claude Code 对独立工具
   并发执行、对文件写工具串行 [I]；mini-claude 串行（安全默认）。
3. **错误传染**：工具报错 ≠ 崩溃。错误文本作为观测回填，让模型自纠——
   这是 agent 鲁棒性的来源（也是 token 消耗的来源）。

## 4. System Prompt（策略先验）

```python
SYSTEM_PROMPT = """You are mini-claude... 
1. 先读后改，不猜文件内容
2. 一次一步，看到结果再决定
3. 自主推进直到完成，总结改了什么、验证了什么
4. 同一方法失败两次就换策略
5. 外科手术式修改"""
```

Claude Code 的版本 [S] 是 64KB 级别的体系（三种变体：CLI/SDK/Orchestrator +
工具描述 + system-reminder 模板），但骨架同样是这五条。**先写短版跑通，
再按失败案例逐条加规则**——所有长 system prompt 都是这样长出来的。

CLAUDE.md 的做法：启动时读 `./CLAUDE.md`（项目说明）拼进 system prompt [S]。
mini-claude 的 `load_project_context()` 同构。

## 5. 上下文管理（γ 的实现）

```python
def est_tokens(messages): return len(json.dumps(messages)) // 3   # 粗估即可
def compact(messages):
    # 保住：system + 最老 user + 最近 6 轮；中间轮次压成骨架
```

- **粗估够用**：chars/3 的误差不影响决策（阈值触发式管理不敏感）。
- **压缩策略**是上下文工程的主战场：保 todo 状态 > 保最近轮次 > 保中间细节。
  Claude Code [S]：autocompact 阈值可调（100k-1M）、压缩时用 LLM 生成摘要而非
  骨架、microcompact 只清老工具输出。
- **练习**：把 mini-claude 的 compact 换成"调一次 LLM 生成对话摘要"，对比两条
  20 轮任务的成功率与 token 消耗。

## 6. 权限层（安全网）

```python
BASH_DENY = [r"\brm\s+-rf\s+/", r"\bmkfs\b", ...]     # 先判
BASH_ASK  = [r"\bgit\s+push\b", ...]                   # 交互时问
_guard_write(p)  # 写操作限 workspace 内
```

Claude Code 的体系 [S]：permissions 数组（allow/ask/deny 三态 × 工具名+参数模式
如 `Bash(git *)`）、四种模式（default/acceptEdits/plan/bypassPermissions）、
危险命令 UI 弹窗。**分层原则相同：deny 先于 allow，写操作永远比读操作严**。

## 7. 增强件路线图（按性价比排序）

| 优先级 | 增强件 | 价值 | 最小实现 |
|---|---|---|---|
| ★★★★★ | transcript JSONL | resume/复盘/数据集 | 每轮 append 一行 JSON |
| ★★★★ | 子代理（fan-out） | 隔离上下文、并行探索 | 递归调用 run_agent，新 messages，结果回填 |
| ★★★★ | checkpoint | 失败回滚 | git stash / 文件快照 per turn |
| ★★★ | MCP client | 接外部工具生态 | stdio JSON-RPC 子进程，list_tools→转 schema |
| ★★★ | skills | 领域知识包 | 读 SKILL.md 目录拼 prompt |
| ★★ | hooks | 管控/审计 | 工具调用前后跑 shell 回调 |
| ★★ | sandbox | 命令隔离 | bubblewrap/firejail 包 bash |

子代理的关键认知（逆向实证 [S]）：**worker 的上下文与主会话完全隔离**，任务书必须
自包含（"Workers can't see your conversation"）；主代理只收结论不收过程——这是上下
文经济学的直接应用。

## 8. 调试与评估

1. **打印轨迹**：mini-claude 的 `🔧` 行 = 最小可观测性。下一步存 JSONL。
2. **固定任务集回归**：10 个代表性任务（读改文件/跑测试/搜索定位/多步验证），
   每次改 prompt 或工具后跑一遍，人工或判据打分。
3. **失败分类学**：记失败原因——工具输出截断 / 上下文溢出 / 幻觉文件内容 /
   中途放弃 / 死循环。每类对应不同的修法（截断→调 limit；死循环→max_turns+prompt 规则）。
4. Claude Code 同款思路 [S]：`plugin eval`（eval 套件 + JSON 报告）、
   `/doctor`、结构化遥测事件。

## 9. 实测记录（本仓）

mini-claude v1（405 行）在智谱 coding plan（glm-5.3）上的冒烟测试 2026-10-16：

```
任务: write hello.txt → read 确认 → bash wc -c
结果: 3 工具调用全部成功，模型自主汇报"22 字节 = 21 字符 + 换行"，与真实一致 ✓
轮次: 3 轮（write / read+bash 并行 / 总结）——注意第 2 轮模型一次发了两个 tool_calls
```

复测 2026-10-16 11:50（glm-5.3-flash，断点续跑会话）：bash(mkdir)→write→read 三工具链成功，
途中真实遇到 HTTP 429 并按退避策略自动重试通过——**限流韧性路径同获实测** ✓

## 9.1 v2 实测记录（2026-10-16 15:2x，逆向机制落地）

mini-claude v2（551 行）把三个逆向实证机制落进实现：

| 机制 | 逆向出处 | 实测 |
|---|---|---|
| **file-state 跟踪** | 03 册 §5 | 7 场景单测全过：ec=6 not-read / ec=7 stale / ec=9 多匹配（文案对齐 Claude Code 原文）/ 同参重读 dedup / 新建免校验 / 写后 state 更新 |
| **autocompact 8 段式** | 02 册 §3 | `MINI_AUTOCOMPACT_THRESHOLD=800` 真触发：`compact method=llm`（独立 LLM 摘要调用+续接前导+骨架回退+熔断计数）；compact 后任务仍正确完成 |
| **遥测三元组** | 13 册 §6 | `.mini-claude/telemetry/<sid>.jsonl`：session_start / tool_use(name,outcome,is_error,duration_ms) / file_read_dedup / compact(before/after,method) / turn_end(outcome) 全事件落盘 |

最有价值的观察：**file-state 语义改变了模型行为**——write 后模型 read 被 dedup 拦截，
它自发改用 `bash cat` 验证（两次端到端均如此）。这正是 Claude Code 用 file-state
省钱省时的弹性机制，40 行 Python 就复刻出来了。

v2 修的一个真 bug：edit 工具 schema 参数名（old_string/new_string）与函数签名（old/new）
不一致——首次端到端即暴露 `TypeError`。**schema 与实现的参数名契约要过端到端才能抓到**。

即：**一个 60 行主循环 + 7 个工具 + 1 页 prompt，就能得到一个能干活的 agent**。
Claude Code 的 8.4MB 是把这个骨架的每一环工业化（安全、UX、并发、生态）。

---
理论对照 → [agent-loop-的-RL-形式化.md](agent-loop-的-RL-形式化.md) · 架构全景 → [../01-总体架构.md](../01-总体架构.md)
