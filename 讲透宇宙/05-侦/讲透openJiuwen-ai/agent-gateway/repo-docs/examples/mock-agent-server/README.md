# Mock AgentServer 示例

用两个脚本在本地模拟 Gateway 的上下游，无需真实 AgentServer、模型凭据或 IM 频道：

- `mock_agent_server.py`：下游 AgentServer。连接后立即发送 `connection.ack`，对每个请求回 Echo，并在 `is_stream` 请求时发送 3 条流式分片。
- `gw_client.py`：上游客户端。连接 Gateway 的 `/tui` 路由，发送一条 `chat.send` 并打印回推事件。

## 运行

前置条件：已在仓库根目录执行 `uv sync`。

终端 A（Mock AgentServer）：

```bash
uv run python examples/mock-agent-server/mock_agent_server.py 19501
# 预期输出：MOCK_READY ws://127.0.0.1:19501
```

终端 B（Gateway）：

```bash
export JIUWENSWARM_HOME="$PWD/.local-home"
export AGENT_SERVER_HOST=127.0.0.1
export AGENT_SERVER_PORT=19501
export WEB_PORT=19500
export GATEWAY_PORT=19502

uv run agent-gateway --port 19500
```

终端 C（客户端）：

```bash
uv run python examples/mock-agent-server/gw_client.py ws://127.0.0.1:19502/tui
```

## 预期输出

终端 C 依次打印：

1. `connection.ack`
2. `{"type":"res","id":"req-chat","ok":true,"payload":{"accepted":true,"session_id":"sess_test"}}`
3. `chat.processing_status`（`is_processing=true`）
4. 3 条 `chat.final`，内容为 `流式-1`、`流式-2`、`流式-3(完)`
5. `chat.processing_status`（`is_complete=true`）

终端 A 同时打印 `MOCK_CONNECT` 和 `MOCK_RECV chat.send {...}`。

## 清理

在两个服务终端按 `Ctrl+C`，然后执行 `rm -rf .local-home`。
