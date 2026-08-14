# MCP 工程手册

> 版本：2026-08 精简版 · 中文为主，术语英文 · 代码可跑（Python SDK / FastMCP）
> 一句话：MCP 把"LLM 怎么连外部世界"从各家私有插件，收敛成**一个开放协议**。

---

## 1. 是什么 + 为什么

### 是什么

**MCP（Model Context Protocol）** 是 Anthropic 于 2024-11 开源发布的应用层协议，采用 **client–server** 架构 + **JSON-RPC 2.0** 消息格式，让任意 LLM Host（Claude Desktop / Cursor / VS Code / 自建 Agent）以**统一方式**连接外部工具、数据源、提示词。

类比：**MCP 之于 AI 工具 ≈ USB 之于硬件 / LSP 之于编辑器**。前者是"即插即用"的硬件总线，LSP 让一个语言服务喂所有编辑器，MCP 让**一个 server 喂所有 host**。

```
┌─────────┐   JSON-RPC   ┌───────────┐
│  Host   │◄────────────►│ MCP Server│──► 文件系统 / DB / API / Git …
│ (LLM)   │              │ (你写的)  │
└─────────┘              └───────────┘
```

### 为什么（解决了什么痛）

| 痛点（Pre-MCP） | MCP 方案 |
|---|---|
| 每家平台一套插件 SDK，N 个 host × M 个工具 = N×M 适配 | **写一次 server，所有 host 通用**（N+M） |
| 工具调用全靠 prompt 里硬塞 schema，脆弱 | server 自描述 schema，host 自动发现 |
| 工具/数据/Prompt 杂糅，无法分类治理 | 显式三分：**Resources / Tools / Prompts** |
| 本地敏感数据只能靠复制粘贴进对话框 | server 本地运行，数据**不离开本机**即可被引用 |

---

## 2. 听说读写 4 能力（自我评估框架）

评价你对 MCP 的掌握，看这四档：

| 能力 | 定义 | 检验标准 |
|---|---|---|
| **听 Listen** | 能看懂一个陌生 MCP server 提供什么 | 给你一份 server 配置，能说出它有哪些 tool/resource/prompt 及用途 |
| **说 Speak** | 能在对话中正确指挥 host 调用 MCP | 知道何时让模型用 tool、何时用 resource、如何描述需求 |
| **读 Read** | 能读懂 MCP spec / SDK 源码 | 读过 [modelcontextprotocol/specification](https://github.com/modelcontextprotocol/specification)，理解 lifecycle、sampling、roots |
| **写 Write** | 能从零实现并发布一个 MCP server | 写的 server 能在 Claude Desktop / Cursor 双端跑通，过 `mcp inspector` 校验 |

> 经验：90% 的人卡在"听→说"（会用），但真正的杠杆在**"写"**——写一个适配自己工作流的 server，是你和别人的护城河。

---

## 3. SRCPT 解析框架

拿到任何 MCP server，用这 5 个字母快速拆解：

| 字母 | 全称 | 是什么 | 例子 |
|---|---|---|---|
| **S** | **Server** | 协议端点，承载下列三类能力 | `@modelcontextprotocol/server-filesystem` |
| **R** | **Resources** | **被动**数据，模型按需读取（只读） | `file:///report.md`、`postgres://table/users` |
| **C** | *(Capability)* | server 还可声明 `sampling`（反向请求 LLM）、`roots`（工作目录边界）等能力 | — |
| **P** | **Prompts** | 可复用的提示词模板（带参数） | `/summarize-pr-diff?repo=x&pr=42` |
| **T** | **Tools** | **主动**动作，模型决定调用并执行（可能有副作用） | `run_sql(query)`、`create_issue(...)` |

> ⚠️ **T（Tools）= 写（可能改世界）；R（Resources）= 读（只读）**。新手最常混淆：把"查询数据库"做成 Resource 还是 Tool？纯 SELECT 且无副作用→Resource；带写或重计算→Tool。

- **Resources**：URI 寻址，`@mcp.resource("file://{path}")`，模型用 `read_resource` 拉。
- **Tools**：JSON Schema 描述入参，`@mcp.tool()`，模型用 `call_tool` 调，server 执行后回结果。
- **Prompts**：`@mcp.prompt()`，把高频用法固化成模板，用户在 host 里像命令一样选。

---

## 4. 6 维度评价（给 server 打分）

评审一个 MCP server（自己的或他人的），逐项打 0–2 分：

| 维度 | 问题 | 2 分（好） | 0 分（差） |
|---|---|---|---|
| **准确性** | 工具返回的数据对吗？ | 结果可验证、有来源 | 幻觉字段、编造数据 |
| **触发精度** | schema/描述能让模型在对的时机调用吗？ | 名称动词化、描述含触发条件 | 名词命名、描述含糊、误触发 |
| **资源质量** | Resources 是否该读的都暴露、不该读的都屏蔽？ | 白名单粒度细、大文件分页 | 暴露全盘、塞爆上下文 |
| **协作性** | 多个 server 能并存、不抢名词吗？ | 工具名带前缀、幂等 | 同名冲突、副作用叠加 |
| **维护性** | 升级 SDK / 换 host 会不会崩？ | 类型完整、有测试、错误优雅 | 无类型、异常裸抛 |
| **安全性** | 敏感操作有没有护栏？ | 危险工具要确认、最小权限 | 任意路径读写、SQL 注入 |

> 合格线 ≥ 9/12。**安全性**若为 0 直接否决，无论其他多高。

---

## 5. 工具栈 2026

### 官方 / 主流 SDK

| SDK | 仓库 | 推荐场景 | 备注 |
|---|---|---|---|
| **Python** | `modelcontextprotocol/python-sdk` | 快速原型、AI 工程师首选 | 内置 `FastMCP`（装饰器风格，类似 FastAPI） |
| **TypeScript** | `modelcontextprotocol/typescript-sdk` | 前端/Node 生态、与 web 工具集成 | 官方 reference servers 多用 TS |
| **Rust** | 社区 `mcp-rust-sdk` 等 | 高性能、嵌入式 | 生态尚早期 |
| **C++** | 社区实验性 | 极致性能/边缘 | 非主流，谨慎选 |
| **Go / C# / Java** | 各社区分支 | 企业栈对齐 | 选活跃维护者 |

### Host（客户端）清单

| Host | MCP 支持 | 备注 |
|---|---|---|
| **Claude Desktop** | ✅ 首发、最全 | 配置在 `claude_desktop_config.json` |
| **Cursor** | ✅ | Settings → MCP，支持 stdio + HTTP |
| **VS Code** | ✅（Copilot Chat） | 2025 起原生支持，`.vscode/mcp.json` |
| **Claude Code / opencode** | ✅ | CLI agent，配置 `mcp` server |
| **OpenAI（ChatGPT/Agents SDK）** | ✅ | 2025-03 起官方接入 MCP |

### 已知高质量 MCP Servers（`modelcontextprotocol/servers` 及社区）

| 名称 | 能力 |
|---|---|
| `filesystem` | 受限目录读写 |
| `git` / `github` | 仓库操作 / Issue·PR |
| `postgres` / `sqlite` | 数据库查询 |
| `puppeteer` / `playwright` | 浏览器自动化 |
| `fetch` | 抓取 URL |
| `memory` | 跨会话知识图谱 |
| `sequential-thinking` | 多步推理脚手架 |
| `brave-search` / `tavily` | 网络搜索 |
| `slack` / `google-drive` / `google-maps` | SaaS 集成 |

> ⚠️ 版本号随时间变化快，落地前以各自 GitHub Release 为准（2026-08 查询），勿凭记忆锁定。

### 开发利器

- **`@modelcontextprotocol/inspector`**（`mcp inspector`）：官方调试 UI，可视化看 tool/resource、模拟调用。**发版前必过。**

---

## 6. 跨平台差异

| 维度 | Claude Desktop | Cursor | VS Code (Copilot) | OpenAI |
|---|---|---|---|---|
| Transport | stdio（主）、HTTP/SSE | stdio + HTTP | stdio + HTTP | HTTP（云）/ stdio |
| 配置位置 | `claude_desktop_config.json` | `.cursor/mcp.json` | `.vscode/mcp.json` | Agents SDK 配置 |
| Resources 支持 | ✅ | ✅ | ✅ | ✅ |
| Prompts 支持 | ✅ | △（部分） | △ | △ |
| Sampling（server→LLM） | ✅ | △ | ❌/△ | △ |
| Roots（工作目录） | ✅ | ✅ | ✅ | △ |
| 权限确认 UI | ✅（敏感操作弹窗） | ✅ | ✅ | ✅ |

> 实操建议：**优先用 stdio + 官方 SDK 默认写法**，兼容性最广；HTTP server 给远程/多用户场景。写完在 ≥2 个 host 实测，别只测一家。

---

## 7. 实战案例

### 7.1 文件系统 MCP Server（Python / FastMCP）

```python
# fs_server.py —— 最小可跑：受限目录的读/写/列目录
from pathlib import Path
from mcp.server.fastmcp import FastMCP

ALLOWED = Path("~/ai/work4ai").resolve()  # ⚠️ 锁定根目录

mcp = FastMCP("safe-fs")

def _safe(path: str) -> Path:
    """防止目录穿越：解析后必须在 ALLOWED 内"""
    p = (ALLOWED / path).resolve()
    if ALLOWED not in p.parents and p != ALLOWED:
        raise PermissionError(f"越界: {p}")
    return p

@mcp.tool()
def list_dir(rel: str = "") -> list[str]:
    """列出指定子目录下的文件名（仅限白名单根目录）"""
    return [f.name for f in _safe(rel).iterdir()]

@mcp.tool()
def read_file(rel: str) -> str:
    """读取文本文件内容"""
    return _safe(rel).read_text(encoding="utf-8")

@mcp.tool()
def write_file(rel: str, content: str) -> str:
    """写入文本文件（覆盖）"""
    p = _safe(rel); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"已写入 {len(content)} 字符 -> {rel}"

@mcp.resource("file://{rel}")
def get_file(rel: str) -> str:
    """以 resource 形式暴露文件（只读，模型可按需拉取）"""
    return read_file(rel)

if __name__ == "__main__":
    mcp.run()  # 默认 stdio transport
```

配置进 Claude Desktop（`~/Library/Application Support/Claude/claude_desktop_config.json`，Linux/WSL 路径不同）：

```json
{
  "mcpServers": {
    "safe-fs": {
      "command": "python",
      "args": ["/abs/path/fs_server.py"]
    }
  }
}
```

### 7.2 数据库 MCP Server（SQLite，只读 Tool + Schema Resource）

```python
# db_server.py —— 安全只读查询 + 暴露 schema
import sqlite3, json
from mcp.server.fastmcp import FastMCP

DB = "~/ai/work4ai/demo.db"
mcp = FastMCP("readonly-sqlite")

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

@mcp.tool()
def query(sql: str, limit: int = 100) -> str:
    """执行【只读】SQL 查询，返回 JSON。自动加 LIMIT 防爆。"""
    s = sql.strip().rstrip(";")
    if not s.lower().startswith("select"):
        raise ValueError("仅允许 SELECT")          # 硬护栏：禁止写
    if "limit" not in s.lower():
        s += f" LIMIT {min(limit, 1000)}"
    rows = [dict(r) for r in _conn().execute(s)]
    return json.dumps(rows[:limit], ensure_ascii=False)

@mcp.resource("schema://tables")
def schema() -> str:
    """暴露所有表结构，帮模型写出正确 SQL"""
    cur = _conn().execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table'")
    return json.dumps([dict(r) for r in cur], ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
```

> 两个 server 合并打分（§4）：准确性 2 / 触发精度 2（动词命名）/ 资源质量 2（schema 即文档）/ 协作性 1 / 维护性 1 / 安全性 2（白名单 + 只读 + LIMIT）= **10/12，合格**。

---

## 8. 反模式 10 条

| # | 反模式 | 后果 | 正解 |
|---|---|---|---|
| 1 | **Tool 用名词命名**（`database`） | 模型不知道何时调 | 用动词：`query_users` |
| 2 | **一个 tool 干所有事**（`do_anything`） | 触发精度崩、模型乱调 | 按职责拆细，schema 明确 |
| 3 | **Resource 暴露全盘文件/全表** | 上下文爆炸、泄密 | 白名单 + 分页 + URI 精确寻址 |
| 4 | **危险操作无确认**（删文件、DROP） | 误删不可逆 | tool 内要求 `confirm=true`，host 弹窗 |
| 5 | **SQL/路径直接拼接用户输入** | 注入 / 目录穿越 | 参数化查询 + `resolve()` 越界检查 |
| 6 | **裸抛异常不 try** | host 拿到 traceback，模型困惑 | 捕获并返回结构化错误信息 |
| 7 | **Resource 和 Tool 重名重叠** | 模型随机选一个，行为不确定 | 职责正交：Resource 只读 / Tool 可写 |
| 8 | **stdio server 里 print 调试** | 污染 JSON-RPC 管道，协议崩 | 日志写文件，stdout 只走协议 |
| 9 | **把密钥写进 server 代码/配置** | 泄密 | 走环境变量 / secret manager |
| 10 | **只测一个 host 就发布** | 换平台即崩 | 至少 Claude Desktop + Cursor 双测，过 inspector |

---

## 9. 下一步

1. **跑通**：装 `pip install mcp`，复制 §7 代码，本地起 server，`mcp inspector` 连上看 tool/resource 列表。
2. **接入 host**：写 `claude_desktop_config.json`，在对话框里让模型"列出 work4ai 目录""查 demo.db 的表"。
3. **套用 SRCPT**：挑一个官方 server（如 `github`），用 §3 拆它的 S/R/P/T，用 §4 打分。
4. **造轮子**：为自己的高频工作流写一个 server（例：查公司内部 wiki / 跑实验脚本 / 管 Anki 卡片）。
5. **进 spec**：读 [specification](https://modelcontextprotocol.io/specification) 的 lifecycle / sampling / roots / elicitation，补齐"读"档。
6. **反模式体检**：拿 §4 + §8 给自己的 server 做一次评审，安全项必须 2 分。

> **判断你毕业的标志**：能写出第 7 类（§7）那样的 server，且在 ≥2 个 host 里零配置改动跑通——你就同时跨过了"听说读写"四档。

---

*本手册遵循三层原则：直觉（§1–3 类比）→ 实操（§5–7 表格+可跑代码）→ 批判（§4 评分 / §8 反模式）。代码用 Python 官方 SDK + FastMCP，bash `python xxx.py` 即可起 stdio server。*
