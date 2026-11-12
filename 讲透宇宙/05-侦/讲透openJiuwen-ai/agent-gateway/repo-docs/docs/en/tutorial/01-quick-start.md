# Quick Start

> Goal: run Agent Gateway locally in about 15 minutes — use a mock AgentServer as the downstream, start the gateway, send a `chat.send` request through the `/tui` route, and see the echo.
>
> 中文: [../../zh/tutorial/01-quick-start.md](../../zh/tutorial/01-quick-start.md)

## 1. Prerequisites

| Dependency | Requirement |
| --- | --- |
| OS | Linux / macOS / Windows |
| Python | 3.11 ~ 3.13 |
| uv | Installed; `gitcode.com` reachable (dependencies include git sources) |
| Ports | `19500`, `19501`, `19502` are free |

## 2. Install

```bash
git clone https://gitcode.com/openJiuwen/agent-gateway.git
cd agent-gateway
uv sync
uv run agent-gateway --help
```

If `uv sync` fails because of network issues, configure a mirror first:

```bash
export UV_DEFAULT_INDEX=https://pypi.org/simple
uv sync
```

## 3. Start the mock AgentServer (terminal A)

The example lives at [examples/mock-agent-server/mock_agent_server.py](../../../examples/mock-agent-server/mock_agent_server.py). It returns `connection.ack` immediately after the connection is established and echoes every request.

```bash
uv run python examples/mock-agent-server/mock_agent_server.py 19501
```

It is ready when you see:

```text
MOCK_READY ws://127.0.0.1:19501
```

## 4. Start the gateway (terminal B)

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

The gateway is ready when the log shows:

- `[ExtensionManager] 加载 ...`: extensions loaded
- `Uvicorn running on http://127.0.0.1:19500`: WebChannel is up
- `[Cron] loaded N job(s) from ...` / `background_cleanup: started ...`: cron and background cleanup started

If you see `[App] Another Gateway is already serving this workspace`, another gateway holds the workspace lock. Stop it or use a different `JIUWENSWARM_HOME`.

## 5. Send your first request (terminal C)

The example client lives at [examples/mock-agent-server/gw_client.py](../../../examples/mock-agent-server/gw_client.py).

```bash
uv run python examples/mock-agent-server/gw_client.py ws://127.0.0.1:19502/tui
```

Expected output, in order:

1. `connection.ack`: handshake confirmation from the gateway
2. `{"type":"res","id":"req-chat","ok":true,"payload":{"accepted":true,"session_id":"sess_test"}}`
3. `chat.processing_status` (`is_processing=true`)
4. Three `chat.final` frames with `流式-1`, `流式-2`, `流式-3(完)`
5. `chat.processing_status` (`is_complete=true`)

Terminal A should also print `MOCK_RECV chat.send {...}`, proving the client → gateway → AgentServer path works.

## 6. Stop and clean up

- Press `Ctrl+C` in terminals A and B
- Remove the local workspace: `rm -rf .local-home`

## Next steps

- Full validation and troubleshooting: [Local validation](../how-to/local-validation.md)
- Connect IM channels: [Configure channels](../how-to/configure-channels.md)
- Run multiple instances: [Multiple instances](../how-to/run-multiple-instances.md)
- CLI and environment variables: [Reference](../reference/cli-and-environment.md)
- Architecture and design: [Architecture](../explanation/architecture.md)
