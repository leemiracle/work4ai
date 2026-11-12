# 单机多实例运行

在同一台机器上运行多个相互隔离的 Gateway + AgentServer 实例，每个实例拥有独立的工作区、配置、端口与进程。

## 隔离原理

Gateway 使用两个环境变量定位运行时目录：

| 变量 | 作用 | 优先级 |
| --- | --- | --- |
| `JIUWENSWARM_DATA_DIR` | 直接指定实例根目录（配置、会话、日志、cron 等） | 最高 |
| `JIUWENSWARM_HOME` | 指定用户主目录，实例根目录为其下的 `.jiuwenswarm` | 次之 |

每个实例根目录下有一把工作区锁（`.gateway.lock`）：同一个实例根目录只允许一个 Gateway 进程运行，避免 cron 重复调度。不同实例使用不同根目录即可并行运行。

## 方式一：环境变量隔离（推荐）

实例 A（终端 1、2）：

```bash
# 终端 1：AgentServer
JIUWENSWARM_DATA_DIR=/srv/gw-a \
AGENT_SERVER_PORT=18092 \
uv run jiuwenswarm-agentserver

# 终端 2：Gateway
JIUWENSWARM_DATA_DIR=/srv/gw-a \
AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=18092 \
WEB_PORT=19000 GATEWAY_PORT=19001 \
uv run agent-gateway
```

实例 B（终端 3、4）：

```bash
# 终端 3：AgentServer
JIUWENSWARM_DATA_DIR=/srv/gw-b \
AGENT_SERVER_PORT=19092 \
uv run jiuwenswarm-agentserver

# 终端 4：Gateway
JIUWENSWARM_DATA_DIR=/srv/gw-b \
AGENT_SERVER_HOST=127.0.0.1 AGENT_SERVER_PORT=19092 \
WEB_PORT=20000 GATEWAY_PORT=20001 \
uv run agent-gateway
```

要点：

- 每个实例的 `AGENT_SERVER_PORT`、`WEB_PORT`、`GATEWAY_PORT` 必须互不冲突。
- 同一实例的 AgentServer 与 Gateway 必须使用相同的 `JIUWENSWARM_DATA_DIR`。
- 如需 TUI 入口，同时为每个实例设置不同的 `GATEWAY_PORT`；如需 A2A 入口，设置 `A2A_SERVER_ENABLED=1` 并为每个实例分配不同的 `A2A_SERVER_PORT`。

## 方式二：instances.yaml 命名实例

先在 `~/.jiuwenswarm/instances.yaml` 中登记实例（也可由 `jiuwenswarm-init --name <name>` 自动创建）：

```yaml
instances:
  dev:
    workspace: /srv/gw-dev
  prod:
    workspace: /srv/gw-prod
```

工作区需要已存在，首次可使用：

```bash
uv run jiuwenswarm-init --name dev --workspace /srv/gw-dev
uv run jiuwenswarm-init --name prod --workspace /srv/gw-prod
```

之后通过 `--name` 启动。实例的端口由工作区下的 bootstrap `.env` 提供（按实例顺序自动分配，基准端口 + 实例索引 × 1000）：

```bash
# 实例 dev
uv run jiuwenswarm-agentserver --name dev
uv run agent-gateway --name dev

# 实例 prod
uv run jiuwenswarm-agentserver --name prod
uv run agent-gateway --name prod
```

## 验证

分别访问每个实例的 WebChannel 端口，并检查日志中不出现 `Another Gateway is already serving this workspace`。若出现，说明两个进程指向了同一实例根目录。

---

## 返回导航

- [返回文档首页](../../README.md)
- [命令行与环境变量参考](../reference/cli-and-environment.md)
- [本地功能验证](local-validation.md)
