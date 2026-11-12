# Run Multiple Instances on One Host

Run multiple isolated Gateway + AgentServer pairs on the same machine, each with its own workspace, configuration, ports, and processes.

## Isolation model

The gateway resolves its runtime directory from two environment variables:

| Variable | Effect | Priority |
| --- | --- | --- |
| `JIUWENSWARM_DATA_DIR` | Directly sets the instance root (config, sessions, logs, cron, and so on) | Highest |
| `JIUWENSWARM_HOME` | Sets the user home; the instance root is `.jiuwenswarm` under it | Next |

Each instance root contains a workspace lock (`.gateway.lock`): only one gateway process may serve a given root, which prevents duplicate cron scheduling. Different roots can run in parallel.

## Option 1: Environment isolation (recommended)

Instance A (terminals 1 and 2):

```bash
# Terminal 1: AgentServer
JIUWENSWARM_DATA_DIR=/srv/gw-a \
AGENT_SERVER_PORT=18092 \
uv run jiuwenswarm-agentserver

# Terminal 2: Gateway
JIUWENSWARM_DATA_DIR=/srv/gw-a \
AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=18092 \
WEB_PORT=19000 GATEWAY_PORT=19001 \
uv run agent-gateway
```

Instance B (terminals 3 and 4):

```bash
# Terminal 3: AgentServer
JIUWENSWARM_DATA_DIR=/srv/gw-b \
AGENT_SERVER_PORT=19092 \
uv run jiuwenswarm-agentserver

# Terminal 4: Gateway
JIUWENSWARM_DATA_DIR=/srv/gw-b \
AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=19092 \
WEB_PORT=20000 GATEWAY_PORT=20001 \
uv run agent-gateway
```

Notes:

- `AGENT_SERVER_PORT`, `WEB_PORT`, and `GATEWAY_PORT` must not collide across instances.
- The AgentServer and gateway of the same instance must use the same `JIUWENSWARM_DATA_DIR`.
- For the TUI route, give each instance a different `GATEWAY_PORT`. For A2A ingress, set `A2A_SERVER_ENABLED=1` and assign a different `A2A_SERVER_PORT` per instance.

## Option 2: Named instances with instances.yaml

Register instances in `~/.jiuwenswarm/instances.yaml` (or let `jiuwenswarm-init --name <name>` create them):

```yaml
instances:
  dev:
    workspace: /srv/gw-dev
  prod:
    workspace: /srv/gw-prod
```

Create the workspaces first:

```bash
uv run jiuwenswarm-init --name dev --workspace /srv/gw-dev
uv run jiuwenswarm-init --name prod --workspace /srv/gw-prod
```

Start with `--name`. Ports come from the bootstrap `.env` in each workspace (allocated as base port + instance index × 1000):

```bash
# Instance dev
uv run jiuwenswarm-agentserver --name dev
uv run agent-gateway --name dev

# Instance prod
uv run jiuwenswarm-agentserver --name prod
uv run agent-gateway --name prod
```

## Verify

Open each instance's WebChannel port and confirm that no log contains `Another Gateway is already serving this workspace`. If it appears, two processes point at the same instance root.

---

## Navigation

- [Documentation home](../../README.md)
- [CLI and environment reference](../reference/cli-and-environment.md)
- [Local validation](local-validation.md)
