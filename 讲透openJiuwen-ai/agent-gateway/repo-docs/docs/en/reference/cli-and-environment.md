# CLI and Environment Reference

This page lists the `agent-gateway` command-line options, environment variables, configuration file, and runtime directories.

## CLI options

Entry points: `agent-gateway` (gateway + channels) and `agent-gateway-acp` (ACP bridge).

| Option | Default | Description |
| --- | --- | --- |
| `-u, --agent-server-url <URL>` | Built from `AGENT_SERVER_URL` or HOST/PORT | Downstream AgentServer WebSocket URL, highest priority |
| `-H, --host <HOST>` | `WEB_HOST` or `127.0.0.1` | WebChannel bind host |
| `-p, --port <PORT>` | `WEB_PORT` or `19000` | WebChannel bind port |
| `--web-path <PATH>` | `WEB_PATH` or `/ws` | WebChannel WebSocket path |
| `--name <name>` | none | Start a named instance from `instances.yaml` |
| `--dotenv <path>` | none | Load environment variables from the given `.env` at startup (startup phase only) |
| `-h, --help` | none | Show help and exit |

## Environment variables

### Downstream AgentServer

| Variable | Default | Description |
| --- | --- | --- |
| `AGENT_SERVER_URL` | unset | Downstream WebSocket URL, highest priority |
| `AGENT_SERVER_HOST` | `127.0.0.1` | Used to build `ws://host:port` when the URL is unset |
| `AGENT_SERVER_PORT` / `AGENT_PORT` | `18092` | Downstream port |
| `AGENT_CONNECT_RETRY` | `20` | Downstream connection retries |
| `AGENT_CONNECT_RETRY_INTERVAL` | `3` | Retry interval in seconds |

### Upstream entry points

| Variable | Default | Description |
| --- | --- | --- |
| `WEB_HOST` | `127.0.0.1` | WebChannel bind host |
| `WEB_PORT` | `19000` | WebChannel port |
| `WEB_PATH` | `/ws` | WebChannel WebSocket path |
| `GATEWAY_HOST` | `127.0.0.1` | TUI route bind host |
| `GATEWAY_PORT` | `19001` | TUI route port |
| `GATEWAY_URL` | unset | Gateway public URL used by some extensions |
| `A2A_SERVER_ENABLED` | disabled | Set to `1` / `true` to enable A2A ingress |
| `A2A_SERVER_HOST` | `127.0.0.1` | A2A bind host |
| `A2A_SERVER_PORT` | `19100` | A2A port |
| `A2A_SERVER_PATH` | `/a2a` | A2A RPC path |
| `A2A_SERVER_CARD_PATH` | `/.well-known/agent-card.json` | Agent Card path |
| `A2A_SERVER_EXTENDED_CARD_PATH` | `/agent/authenticatedExtendedCard` | Extended Agent Card path |
| `A2A_SERVER_PROTOCOL_VERSION` | `1.0.0` | A2A protocol version |

### Workspace and runtime

| Variable | Default | Description |
| --- | --- | --- |
| `JIUWENSWARM_HOME` | user home | User home; the instance root is `.jiuwenswarm` under it |
| `JIUWENSWARM_DATA_DIR` | unset | Directly sets the instance root; takes priority over `JIUWENSWARM_HOME` |
| `JIUWENSWARM_RUNTIME_WORKSPACE_READY` | unset | Internal marker; set by parent processes such as the desktop app to skip duplicate workspace initialization |
| `BROWSER_PROFILE_NAME` | `jiuwenclaw` | Profile name for browser-related features |

### Health check / heartbeat

| Variable | Default | Description |
| --- | --- | --- |
| `HEALTH_CHECK_INTERVAL` / `HEARTBEAT_INTERVAL` | `health_check.every` from `config.yaml`, else `60` | Check interval in seconds |
| `HEALTH_CHECK_TIMEOUT` | unset | Timeout per check in seconds |
| `HEALTH_CHECK_RELAY_CHANNEL_ID` / `HEARTBEAT_RELAY_CHANNEL_ID` | `health_check.target` from `config.yaml`, else `web` | Channel that receives the result |

## Configuration file

Default path: `$JIUWENSWARM_DATA_DIR/config/config.yaml`; when `JIUWENSWARM_DATA_DIR` is unset, `$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`.

If the file is missing or cannot be read, the gateway warns and uses defaults. Common settings:

```yaml
channels: {}          # Only IM channels present here are initialized
health_check:
  every: 60           # Health check interval in seconds
  target: web         # Channel that receives the result
```

## Runtime directories

| Path | Content |
| --- | --- |
| `<root>/config/config.yaml` | Gateway / channel configuration |
| `<root>/agent/sessions/` | Session data (written by the AgentServer) |
| `<root>/agent/.logs/` | Gateway, AgentServer, and combined logs |
| `<root>/.gateway.lock` | Workspace singleton lock |
| `<root>/agent/home/cron_jobs.json` | Cron job store (maintained by the gateway) |

`<root>` is `JIUWENSWARM_DATA_DIR` when set, otherwise `JIUWENSWARM_HOME/.jiuwenswarm`.

## Exit behavior

| Scenario | Behavior |
| --- | --- |
| Workspace lock already held | Prints `[App] Another Gateway is already serving this workspace` and exits non-zero |
| `--name` instance missing or workspace absent | Fails before startup with a non-zero exit |
| `Ctrl+C` | Shuts down WebChannel, channels, and background tasks, then exits |

---

## Navigation

- [Documentation home](../../README.md)
- [Quick Start](../tutorial/01-quick-start.md)
- [Multiple instances](../how-to/run-multiple-instances.md)
