# 快速开始

> 目标：在本地 15 分钟内跑通 Agent Gateway——用一个 Mock AgentServer 模拟下游，启动 Gateway，再通过 `/tui` 路由发一条 `chat.send`，看到下游回显。
>
> English: [../../en/tutorial/01-quick-start.md](../../en/tutorial/01-quick-start.md)

## 1. 前置条件

| 依赖 | 要求 |
| --- | --- |
| 操作系统 | Linux / macOS / Windows |
| Python | 3.11 ~ 3.13 |
| uv | 已安装，可访问 `gitcode.com`（依赖含 git 源） |
| 端口 | `19500`、`19501`、`19502` 未被占用 |

## 2. 安装

```bash
git clone https://gitcode.com/openJiuwen/agent-gateway.git
cd agent-gateway
uv sync
uv run agent-gateway --help
```

若 `uv sync` 因网络失败，可先配置镜像：

```bash
export UV_DEFAULT_INDEX=https://pypi.org/simple
uv sync
```

## 3. 启动 Mock AgentServer（终端 A）

示例脚本位于 [examples/mock-agent-server/mock_agent_server.py](../../../examples/mock-agent-server/mock_agent_server.py)。它会在连接建立后立即返回 `connection.ack`，并对收到的请求回 Echo。

```bash
uv run python examples/mock-agent-server/mock_agent_server.py 19501
```

看到下面的输出即就绪：

```text
MOCK_READY ws://127.0.0.1:19501
```

## 4. 启动 Gateway（终端 B）

```bash
export JIUWENSWARM_HOME="$PWD/.local-home"
export AGENT_SERVER_HOST=127.0.0.1
export AGENT_SERVER_PORT=19501
export WEB_HOST=127.0.0.1
export WEB_PORT=19500
export GATEWAY_HOST=127.0.0.1
export GATEWAY_PORT=19502

uv run agent-gateway --port 19500
```

日志中出现以下内容，说明 Gateway 已完成启动：

- `[ExtensionManager] 加载 ...`：扩展加载完成
- `Uvicorn running on http://127.0.0.1:19500`：WebChannel 就绪
- `[Cron] loaded N job(s) from ...` / `background_cleanup: started ...`：定时任务与后台清理启动

如果出现 `[App] Another Gateway is already serving this workspace`，说明同一工作区已有 Gateway 在运行，请停止旧进程或更换 `JIUWENSWARM_HOME`。

## 5. 发送第一条请求（终端 C）

示例客户端位于 [examples/mock-agent-server/gw_client.py](../../../examples/mock-agent-server/gw_client.py)。

```bash
uv run python examples/mock-agent-server/gw_client.py ws://127.0.0.1:19502/tui
```

预期依次看到：

1. `connection.ack`：Gateway 对上游的握手确认
2. `{"type":"res","id":"req-chat","ok":true,"payload":{"accepted":true,"session_id":"sess_test"}}`
3. `chat.processing_status`（`is_processing=true`）
4. 3 条 `chat.final`，内容为 `流式-1`、`流式-2`、`流式-3(完)`
5. `chat.processing_status`（`is_complete=true`）

同时终端 A 会出现 `MOCK_RECV chat.send {...}`，说明「上游客户端 → Gateway → 下游 AgentServer」链路已打通。

## 6. 停止并清理

- 在终端 A、B 中按 `Ctrl+C`
- 删除本地工作区：`rm -rf .local-home`

## 下一步

- 完整验证步骤与排错：[本地功能验证](../how-to/local-validation.md)
- 接入 IM 频道：[配置频道](../how-to/configure-channels.md)
- 运行多个实例：[单机多实例](../how-to/run-multiple-instances.md)
- 命令行与环境变量：[参考文档](../reference/cli-and-environment.md)
- 架构与设计：[架构说明](../explanation/architecture.md)
