# 01 — Python CLI 入口与命令树（`mem0-cli`）

> `mem0-cli` 是 Mem0 的命令行工具,基于 Typer + Rich。**默认走 Platform API**,可选 OSS 模式（`pip install mem0-cli[oss]`）。

---

## 1. 安装与入口

```bash
pip install mem0-cli
# 安装后:`mem0` 命令可用

# 装上 OSS 支持
pip install mem0-cli[oss]
```

```toml
# cli/python/pyproject.toml
[project]
name = "mem0-cli"
version = "0.2.11"
requires-python = ">=3.10"

[project.scripts]
mem0 = "mem0_cli.app:main"   # ← 命令入口

[project.optional-dependencies]
oss = ["mem0ai>=0.1.0"]
```

---

## 2. 文件结构

```
cli/python/src/mem0_cli/
├── __init__.py            # __version__
├── __main__.py            # python -m mem0_cli 入口
├── app.py                 # ⭐ 主 Typer app + 命令注册（1416 行）
├── branding.py            # Rich 颜色 + ASCII art（178 行）
├── output.py              # Rich table/json 输出（394 行）
├── config.py              # 配置文件 load/save（244 行）
├── state.py               # 全局 state（agent mode 等）
├── telemetry.py           # PostHog 遥测（155 行）
├── telemetry_sender.py    # 异步发送（119 行）
├── agent_detect.py        # 检测是否在 AI agent 环境
├── plugin_sync.py         # 编辑器插件同步（119 行）
├── backend/
│   ├── base.py            # Backend ABC
│   ├── platform.py        # HTTP backend（默认）
│   └── __init__.py        # get_backend factory
└── commands/
    ├── init_cmd.py        # mem0 init
    ├── memory.py          # mem0 add/search/get/getAll/update/delete
    ├── entities.py        # mem0 entity ...
    ├── events_cmd.py      # mem0 event ...
    ├── config_cmd.py      # mem0 config ...
    ├── whoami_cmd.py      # mem0 whoami
    ├── identify_cmd.py    # mem0 identify
    ├── agent_mode_cmd.py  # mem0 agent-mode on/off
    ├── agent_rush_cmd.py  # mem0 agent-rush（批量）
    └── utils.py
```

---

## 3. ⭐ `app.py` 顶层结构

```python
import typer
from rich.console import Console

console = Console()
err_console = Console(stderr=True)

# 主 app
app = typer.Typer(
    name="mem0",
    help=f"◆ Mem0 CLI v{__version__} · Python SDK\n\n   The Memory Layer for AI Agents",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
    add_completion=False,
)

# 子命令组
config_app = typer.Typer(name="config", help="Manage mem0 configuration.")
entity_app = typer.Typer(name="entity", help="Manage entities.")
event_app = typer.Typer(name="event", help="Inspect background processing events.")

# 命令注册（在文件后段）
# app.command("init")(init_cmd)
# app.command("add")(memory.add_cmd)
# ...
```

### `pretty_exceptions_enable=False`

禁用 Rich 异常美化——防止 traceback 在 AI agent 环境下显得乱（agent 解析 stack trace 时 Rich 颜色码会干扰）。

---

## 4. ⭐ 命令清单

| 命令 | 用途 |
|------|------|
| `mem0 init` | 初始化（创建账号 / 登录 / 设 API key） |
| `mem0 init --agent --agent-caller claude-code` | Agent sign up（README 推荐流程） |
| `mem0 add <text>` | 添加 memory |
| `mem0 add <text> --user-id alice` | 带 scope |
| `mem0 search <query> --user-id alice` | 搜索 |
| `mem0 get <id>` | 取单条 |
| `mem0 get-all --user-id alice` | 列出 |
| `mem0 update <id> --text "..."` | 更新 |
| `mem0 delete <id>` | 删除 |
| `mem0 delete-all --user-id alice` | 批量删 |
| `mem0 history <id>` | 变更历史 |
| `mem0 entity list/add/delete ...` | 实体管理 |
| `mem0 event list/status ...` | 后台事件 |
| `mem0 config get/set/show` | 配置 |
| `mem0 whoami` | 当前账号 |
| `mem0 identify` | 检测环境 |
| `mem0 agent-mode on/off` | Agent 模式开关 |
| `mem0 agent-rush ...` | 批量任务 |

---

## 5. ⭐ Backend 抽象

```python
# cli/python/src/mem0_cli/backend/base.py（推断）
class Backend(ABC):
    @abstractmethod
    def ping(self, timeout=None) -> dict: ...

    @abstractmethod
    def add(self, messages, **kwargs) -> dict: ...

    @abstractmethod
    def search(self, query, **kwargs) -> dict: ...

    # ... get_all/update/delete/delete_all/history

# cli/python/src/mem0_cli/backend/platform.py
class PlatformBackend(Backend):
    """HTTP backend → api.mem0.ai 或自托管 server"""
    def __init__(self, api_key, base_url): ...
    def ping(self, timeout=None):
        return self._client.get("/v1/ping/", timeout=timeout).json()
    # ...

# cli/python/src/mem0_cli/backend/__init__.py
def get_backend(config) -> Backend:
    if config.platform.api_key:
        return PlatformBackend(config.platform.api_key, config.platform.base_url)
    elif config.oss.enabled:
        from mem0_cli.backend.oss import OSSBackend   # 仅 [oss] extra 时可 import
        return OSSBackend(config.oss)
    else:
        raise ValueError("No backend configured")
```

> Backend 抽象让同一套命令支持 **Platform / 自托管 Server / OSS Library** 三种模式。

---

## 6. ⭐ `init` 流程（README 推荐的 4 步）

```bash
# 1. Install
npm install -g @mem0/cli      # or: pip install mem0-cli

# 2. Sign up as an agent
mem0 init --agent --agent-caller claude-code

# 3. Add a memory
mem0 add "I am using mem0"

# 4. Search
mem0 search "am I using mem0"
```

### `mem0 init` 内部

```python
# commands/init_cmd.py（推断）
@app.command("init")
def init(
    agent: bool = False,
    agent_caller: str = None,
    email: str = None,
    api_key: str = None,
):
    if agent:
        # Agent signup：用 agent_detect 拿 caller,创建临时 API key
        ...
    elif email:
        # Email signup
        ...
    elif api_key:
        # 直接配 API key
        config.platform.api_key = api_key
        save_config(config)
    else:
        # Interactive prompt
        ...
```

---

## 7. ⭐ Agent 模式（特别设计）

`mem0 agent-mode on` 让 CLI 切到"AI agent 友好"输出模式：
- 全部输出 JSON（agent 易解析）
- 禁用 Rich 颜色
- 禁用交互 prompt
- 启用 stdin pipe 支持

```python
# state.py
def is_agent_mode() -> bool:
    return _agent_mode_flag or os.environ.get("MEM0_AGENT_MODE") == "1"
```

`agent_detect.py` 自动检测环境：
- `CLAUDE_CODE=true` env → Claude Code
- `CURSOR_TRACE_ID` → Cursor
- 等等

> AI agent 跑 CLI 时,自动切 agent mode,避免 Rich 颜色码污染输出。

---

## 8. ⭐ 配置文件

```
~/.mem0/config.json
```

```json
{
  "user_id": "uuid-...",
  "telemetry": {"enabled": true},
  "platform": {
    "api_key": "m0sk_..." or "Mem0 platform key",
    "base_url": "https://api.mem0.ai",
    "user_email": "alice@example.com"
  },
  "oss": {
    "enabled": false,
    "config": {}
  }
}
```

> 通过 `mem0 config get/set <key> <value>` 管理。

---

## 9. Telemetry

跟 SDK 一样用 PostHog,但事件名前缀 `cli.`（如 `cli.init` / `cli.add`）：

```python
def _fire_telemetry(command_name: str, extra: dict | None = None) -> None:
    """非阻塞、永不出错。"""
    try:
        from mem0_cli.telemetry import capture_event
        props = {"command": command_name}
        if extra:
            props.update(extra)
        capture_event(f"cli.{command_name}", props, pre_resolved_email=_validated_user_email)
    except Exception:
        pass
```

> 关闭：`mem0 config set telemetry.enabled false` 或环境变量 `MEM0_TELEMETRY=False`。

---

## 10. ⭐ 输出系统（`output.py`）

`output.py` 394 行,管所有输出格式：

```python
# 自动判断 agent 模式 / 普通 terminal
def render_memory(memory: dict, format: str = "auto"):
    if format == "json" or is_agent_mode():
        print(json.dumps(memory))
    else:
        # Rich 表格
        table = Table(show_header=False)
        table.add_row("ID", memory["id"])
        table.add_row("Memory", memory["memory"])
        # ...
        console.print(table)
```

---

## 11. 与 SDK 关系

| 场景 | 用 |
|------|---|
| 想在 shell 用 mem0 | CLI |
| 想在 Python 代码用 | SDK（`from mem0 import Memory`） |
| 想在 TS/JS 代码用 | TS SDK |
| AI agent 自动管理 memory | CLI（agent mode） |

> CLI **不**是 SDK 的替代品,是补充——shell 场景 / AI agent 集成。

---

## 12. 接下来

| 想看 | 去哪 |
|------|------|
| Node CLI 对比 | [`../07-cli-node/01-entry-and-commands.md`](../07-cli-node/01-entry-and-commands.md) |
| Hosted client API | [`../03-py-sdk-client/01-client.md`](../03-py-sdk-client/01-client.md) |
| 编辑器集成 | [`../08-integrations/01-mem0-plugin.md`](../08-integrations/01-mem0-plugin.md) |

---

📌 **下一步** → [`../07-cli-node/`](../07-cli-node/) Node CLI。
