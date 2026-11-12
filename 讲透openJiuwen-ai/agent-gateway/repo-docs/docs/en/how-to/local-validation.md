# Local Validation Guide

Validate `agent-gateway` locally with a mock AgentServer: startup, downstream connection, and the upstream WebSocket round trip.

- **Downstream (South)**: AgentServer WebSocket; this guide uses a mock service instead of a real AgentServer.
- **Upstream (North)**: the gateway's built-in `/tui` WebSocket route (same frame format as real clients).

> For the shortest first-run path, see [Quick Start](../tutorial/01-quick-start.md). This document focuses on complete validation steps and troubleshooting.

## 0. Prerequisites

- Python 3.11 ~ 3.13
- [uv](https://docs.astral.sh/uv/)
- `gitcode.com` reachable (dependencies include git sources)

## 1. Install

```bash
cd agent-gateway
uv sync
uv run agent-gateway --help
```

All third-party dependencies are declared in `pyproject.toml`; the package does not depend on `workswarm` and can be installed standalone.

If `uv sync` fails because of network issues, configure a mirror first:

```bash
export UV_DEFAULT_INDEX=https://pypi.org/simple
uv sync
```

## 2. Configuration

### 2.1 Workspace isolation (recommended)

```bash
export JIUWENSWARM_HOME="$PWD/.local-home"
```

- The workspace is `$JIUWENSWARM_HOME/.jiuwenswarm` and is initialized on first start (default skills, cron files, and so on); no manual setup is required.
- Default config path: `$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`.
- Use `JIUWENSWARM_DATA_DIR` for data isolation between instances (this is what `--name` uses on the deployment side).

### 2.2 Ports and downstream address

| Variable | Default | Description |
|---|---|---|
| `AGENT_SERVER_URL` | derived from HOST/PORT | Downstream AgentServer WebSocket URL, highest priority |
| `AGENT_SERVER_HOST` / `AGENT_SERVER_PORT` | `127.0.0.1` / `18092` | Used to build `ws://host:port` when the URL is unset |
| `WEB_HOST` / `WEB_PORT` / `WEB_PATH` | `127.0.0.1` / `19000` / `/ws` | WebChannel (uvicorn) listen address |
| `GATEWAY_PORT` | `19001` | `/tui` route listen port |
| `AGENT_CONNECT_RETRY` / `AGENT_CONNECT_RETRY_INTERVAL` | `20` / `3` | Downstream connect retries / interval in seconds |

The CLI options `--agent-server-url` / `--host` / `--port` / `--web-path` override the corresponding environment variables.

### 2.3 config.yaml (optional)

When the file is missing, the gateway warns and uses defaults, so it is not required for a minimal validation. To explicitly disable all IM channels:

```yaml
channels: {}
health_check:
  every: 60
  target: web
```

A channel (feishu / dingtalk / telegram / discord / slack / wecom, and so on) is loaded lazily only when its entry exists under `channels`.

## 3. Start the mock AgentServer

The example ships with the repository: [examples/mock-agent-server/mock_agent_server.py](../../../examples/mock-agent-server/mock_agent_server.py). It replies with `connection.ack` on connect, echoes requests, and supports streamed chunks.

Start it (terminal A):

```bash
uv run python examples/mock-agent-server/mock_agent_server.py 19501
# Output: MOCK_READY ws://127.0.0.1:19501
```

## 4. Start the gateway

Terminal B:

```bash
export JIUWENSWARM_HOME="$PWD/.local-home"
export AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=19501
export WEB_HOST=127.0.0.1 WEB_PORT=19500 GATEWAY_HOST=127.0.0.1 GATEWAY_PORT=19502

uv run agent-gateway --port 19500
```

Ready markers in the log:

- No `[App] Another Gateway is already serving this workspace`: workspace singleton lock acquired
- `[ExtensionManager] 加载 ...`: extensions loaded
- `Uvicorn running on http://127.0.0.1:19500`: WebChannel is up
- `[Cron] loaded N job(s) from ...` / `background_cleanup: started ...`: cron and background cleanup started

## 5. Verify the upstream path

The example client ships with the repository: [examples/mock-agent-server/gw_client.py](../../../examples/mock-agent-server/gw_client.py). It sends `chat.send` through the `/tui` route and prints events pushed back by the gateway.

```bash
uv run python examples/mock-agent-server/gw_client.py ws://127.0.0.1:19502/tui
```

Expected output, in order:

1. `connection.ack` (gateway handshake confirmation to the client)
2. `{"type":"res","id":"req-chat","ok":true,"payload":{"accepted":true,"session_id":"sess_test"}}`
3. `chat.processing_status` (`is_processing=true`)
4. Three `chat.final` frames carrying `流式-1 / 流式-2 / 流式-3(完)`
5. `chat.processing_status` (`is_complete=true`)

Terminal A should also print `MOCK_RECV chat.send {...}`, proving the client → gateway → AgentServer path works.

Then verify a downstream RPC (`session.list`):

```bash
uv run python - <<'EOF'
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:19502/tui") as ws:
        await ws.send(json.dumps({"type": "req", "id": "req-list", "method": "session.list", "params": {}}))
        while True:
            frame = json.loads(await ws.recv())
            if frame.get("type") == "res" and frame.get("id") == "req-list":
                print(json.dumps(frame, ensure_ascii=False)); break

asyncio.run(main())
EOF
```

Expected: `{"type":"res","id":"req-list","ok":true,"payload":{"sessions":[],"current_branch":"HEAD"}}`, and the mock side prints `MOCK_RECV session.list {}`.

## 6. Stop and clean up

- Press `Ctrl+C` in both terminals
- Remove the local workspace: `rm -rf .local-home`

## 7. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'agent_gateway'` | Dependencies are incomplete; run `uv sync` again, or check that you are not bypassing the project venv |
| Startup reports "Another Gateway is already serving this workspace" | Another gateway is running with the same `JIUWENSWARM_HOME` (`.gateway.lock`); use another directory or stop the old process |
| Log shows `等待 connection.ack 超时` | The mock did not send `connection.ack`, so `server_ready` stays false and some proxy entries are unavailable |
| Port already in use | Change `WEB_PORT` / `GATEWAY_PORT` / the mock port |
| IM channels not started | Expected: only channels explicitly enabled under `channels` are started |
| `uv sync` is slow or times out | The first run pulls git sources such as openjiuwen; make sure gitcode is reachable or configure `UV_DEFAULT_INDEX` |

## Appendix A: Run with an existing venv

If a venv with the gateway's dependencies already exists, reuse it instead of creating a new one:

```bash
JIUWENSWARM_HOME=/tmp/gw-home \
AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=19501 \
WEB_PORT=19500 GATEWAY_PORT=19502 \
PYTHONPATH=/path/to/agent-gateway \
/path/to/venv/bin/python -m agent_gateway.app_gateway --port 19500
```

The venv must already have the gateway's dependencies.

---

## Navigation

- [Documentation home](../../README.md)
- [Quick Start](../tutorial/01-quick-start.md)
- [CLI and environment reference](../reference/cli-and-environment.md)
