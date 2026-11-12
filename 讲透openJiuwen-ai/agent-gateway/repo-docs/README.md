<h1 align="center">Agent Gateway</h1>

<p align="center">
  <strong>One gateway from every client to the agent — multi-channel access, routing, scheduling</strong>
</p>

<p align="center">
  <a href="README.md">English</a>
  ·
  <a href="README.zh.md">Chinese</a>
  ·
  <a href="docs/en/how-to/local-validation.md">Local Validation</a>
  ·
  <a href="https://gitcode.com/openJiuwen/agent-gateway">Repository</a>
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-Apache--2.0-green.svg" alt="License" />
  </a>
  <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/os-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="OS Support" />
</p>

**Agent Gateway** is the gateway process of the split deployment (Gateway + AgentServer). It sits between user-facing channels and the AgentServer: it accepts connections from the Web UI, TUI, ACP clients and IM platforms, routes requests to the AgentServer over a single WebSocket (E2A protocol), and owns the cross-session services — scheduled tasks, heartbeat, health checks and multi-instance isolation.

The gateway builds and runs as its own Python package `agent-gateway` with two entry points: `agent-gateway` (gateway + channels) and `agent-gateway-acp` (ACP bridge).

## Core Features

| Capability                     | Value                                                                                                                                                                                          |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Multi-channel access           | One process serves the Web UI, TUI, ACP clients and IM platforms (Xiaoyi, Feishu, DingTalk, WeCom, Personal WeChat, Telegram, Discord, Slack, WhatsApp) with per-channel lazy loading          |
| Request routing                | Every client request is normalized and forwarded to the AgentServer over one E2A WebSocket; responses and stream chunks are demultiplexed by request id                                         |
| Session & project routing      | Gateway keeps routing state (session, project, work mode, channel binding) so clients can reconnect or switch without losing the conversation                                                  |
| Scheduled tasks                | Cron store, scheduler and command acknowledgement live in the gateway; jobs are executed by the AgentServer; system-owned `proactive.tick` jobs cannot be created or edited manually          |
| Media & file forwarding        | Files from IM platforms are persisted through the AgentServer — the gateway never writes into the user's project directory                                                                     |
| Security                       | WebSocket origin checks, user-id whitelist, explicit stripping of client-forged auth keys, and credentials forwarded only from authenticated channels                                            |
| Protocol bridges               | ACP, A2A, SSH relay and web proxy channels share the same routing layer                                                                                                                        |
| Health & heartbeat             | Periodic health checks and heartbeat keep the gateway/AgentServer pair observable and let the supervisor restart a stuck half                                                                   |
| Multi-instance isolation       | `JIUWENSWARM_HOME` / `JIUWENSWARM_DATA_DIR` isolate workspaces, and a workspace lock prevents two gateways from serving the same instance                                                        |

## Related Documents

- [Documentation](docs/README_EN.md) — tutorial, how-to, reference, and explanation
- [Examples](examples/README.md) — runnable mock AgentServer example
- [Local Validation](docs/en/how-to/local-validation.md) — end-to-end validation walkthrough
- [Release Notes](https://gitcode.com/openJiuwen/agent-gateway/releases)

## Requirements

| Dependency | Requirement |
| --- | --- |
| Operating system | Linux / macOS / Windows |
| Python | 3.11 ~ 3.13 |
| uv | Installed |
| Network | Access to `gitcode.com` (dependencies include git sources) |

## Install

### From Source

```bash
git clone https://gitcode.com/openJiuwen/agent-gateway.git
cd agent-gateway
uv sync
uv run agent-gateway --help
```

All third-party dependencies are declared in `pyproject.toml`; the package does not depend on `workswarm` and can be installed standalone.

If `uv sync` is slow or fails on the git sources, configure an index mirror first:

```bash
export UV_DEFAULT_INDEX=https://pypi.org/simple
uv sync
```

### From Wheel

```bash
bash scripts/build.sh --wheel
pip install dist/agent_gateway-*.whl
```

## Quick Start

Start the downstream AgentServer in one terminal (or use the mock from [examples/mock-agent-server](examples/mock-agent-server/)):

```bash
uv run jiuwenswarm-agentserver --port 18092
```

Then start the gateway in another terminal:

```bash
# Keep the workspace of this instance separate
export JIUWENSWARM_HOME="$PWD/.local-home"

# AgentServer (southbound) and WebChannel (northbound)
export AGENT_SERVER_HOST=127.0.0.1
export AGENT_SERVER_PORT=18092
export WEB_HOST=127.0.0.1
export WEB_PORT=19000

uv run agent-gateway --port 19000
```

Ready markers in the log:

- `[ExtensionManager] 加载 <name>` — an extension has been loaded
- `Uvicorn running on http://127.0.0.1:19000` — WebChannel is up
- `[Cron] loaded N job(s) from ...` / `background_cleanup: started ...` — cron and background cleanup are running

A `[App] Another Gateway is already serving this workspace` error means another gateway holds the workspace lock; stop it or use a different `JIUWENSWARM_HOME`.

For a fully self-contained walkthrough (mock downstream + `chat.send` round trip), see [Quick Start](docs/en/tutorial/01-quick-start.md).

## Architecture

```text
 Web UI / TUI / ACP / IM channels
              │  WebSocket (E2A frames)
              ▼
     Agent Gateway
       ├─ MessageHandler + ChannelManager
       ├─ WebChannel (uvicorn) / TUI route
       ├─ Cron scheduler · heartbeat · health check
       └─ routing / session binding
              │  AgentServer WebSocket (E2A)
              ▼
      jiuwenswarm-agentserver
```

The gateway is stateless with respect to agent execution: everything that touches the workspace, the model credentials or the tool sandbox is executed by the AgentServer. See [Architecture](docs/en/explanation/architecture.md) for details.

## Command-Line Options

| Option                          | Description                                                                                   |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| `-u, --agent-server-url <URL>`  | AgentServer WebSocket URL; overrides `AGENT_SERVER_URL` / `AGENT_SERVER_HOST` + `PORT`        |
| `-H, --host <HOST>`             | WebChannel bind host (default `WEB_HOST` or `127.0.0.1`)                                       |
| `-p, --port <PORT>`             | WebChannel bind port (default `WEB_PORT` or `19000`)                                          |
| `--web-path <PATH>`             | WebChannel WebSocket path (default `WEB_PATH` or `/ws`)                                        |
| `--name <name>`                 | Start a named instance from `instances.yaml`                                                  |
| `--dotenv <path>`               | Load environment variables from a `.env` file at startup                                      |

### Environment Variables

| Variable                                          | Default                     | Description                                                    |
| ------------------------------------------------- | --------------------------- | -------------------------------------------------------------- |
| `JIUWENSWARM_HOME`                                | `~`                         | Workspace root; the instance directory is `.jiuwenswarm`       |
| `JIUWENSWARM_DATA_DIR`                            | unset                       | Data directory for multi-instance isolation                    |
| `AGENT_SERVER_URL`                                | derived                     | AgentServer WebSocket URL (highest priority)                   |
| `AGENT_SERVER_HOST` / `AGENT_SERVER_PORT`         | `127.0.0.1` / `18092`       | Used to build `ws://host:port` when the URL is unset           |
| `WEB_HOST` / `WEB_PORT` / `WEB_PATH`              | `127.0.0.1` / `19000` / `/ws` | WebChannel (uvicorn) listen address                          |
| `GATEWAY_HOST` / `GATEWAY_PORT`                   | `127.0.0.1` / `19001`       | TUI route listen address                                       |
| `AGENT_CONNECT_RETRY` / `AGENT_CONNECT_RETRY_INTERVAL` | `20` / `3`             | Southbound connection retries / interval in seconds            |

### config.yaml

The config file lives at `$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`. It is optional for a first run — the gateway warns and uses defaults when it is missing. To start with every IM channel disabled:

```yaml
channels: {}
health_check:
  every: 60
  target: web
```

Channels (`feishu`, `dingtalk`, `telegram`, `discord`, `slack`, `wecom`, `wechat`, `xiaoyi`, `whatsapp`) are loaded lazily: only the entries present under `channels` are initialized, together with their dependencies.

## Channels

Enable a channel in the Web UI, or in `config.yaml` with `enabled: true` and that platform's credentials.

| Region        | Channels                                                                                                                                                                                                                                                   |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| China         | Xiaoyi, Feishu (Lark), DingTalk, WeCom (WeChat Work), Personal WeChat                                                                                                                                                                                       |
| International | Telegram, Discord, Slack, WhatsApp                                                                                                                                                                                                                          |

Capabilities differ per platform: Xiaoyi and WhatsApp are private chat only; Feishu, WeCom, DingTalk, Telegram, Discord and Slack also work in groups, usually by @mentioning the bot. Feishu and WeCom additionally support the Digital Avatar feature. See [Configure Channels](docs/en/how-to/configure-channels.md).

## Local Validation

A self-contained walkthrough that mocks the AgentServer and drives the gateway through its `/tui` route is in [docs/en/how-to/local-validation.md](docs/en/how-to/local-validation.md). It covers install, workspace isolation, ports, startup markers, an upstream `chat.send` round trip and troubleshooting.

## Build

```bash
bash scripts/build.sh              # clean, then build wheel + sdist
bash scripts/build.sh --wheel      # wheel only
bash scripts/build.sh --sdist      # sdist only
bash scripts/build.sh --no-clean   # keep build/ artifacts
```

Artifacts are written to `dist/`:

- `dist/agent_gateway-<version>-py3-none-any.whl`
- `dist/agent_gateway-<version>.tar.gz`

## Test

```bash
./run_tests.sh              # all tests
./run_tests.sh -u           # unit tests only
./run_tests.sh -c           # tests + HTML coverage report
./run_tests.sh -p           # parallel (requires pytest-xdist)
```

`pytest.ini` enables coverage by default for `agent_gateway`:

- terminal report (`term-missing`)
- `htmlcov/index.html`
- `coverage.xml`

## Contributing

We welcome developers to contribute to Agent Gateway:

- Report bugs, feature requests, or usage issues: [Issues](https://gitcode.com/openJiuwen/agent-gateway/issues)
- Submit code, documentation, or examples: [Pull Requests](https://gitcode.com/openJiuwen/agent-gateway/pulls)

Before contributing, read the [Contributing Guide](CONTRIBUTING.en.md) for the debugging workflow, code style, and commit conventions.

## Community

| Channel          | Purpose                                                      | Link                                                          |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------- |
| Website          | Product info, updates, and ecosystem                         | [Visit Website](https://openjiuwen.com/en/)                   |
| SIG              | Technical roadmap, engineering practices, ecosystem building | [Join SIG](https://openjiuwen.com/en/community/sig-center)    |
| Swarm Skills Hub | Browse, publish, and reuse agent skills                | [Visit Swarm Skills Hub](https://swarmskills.openjiuwen.com/) |

## License

This project is licensed under [Apache License 2.0](LICENSE).

This product serves solely as a workflow orchestration tool and does not embed any AI model capabilities. When users integrate AI models for specific business scenarios, they shall bear full responsibility for compliance obligations under the EU AI Act and other relevant regulatory frameworks.
