<h1 align="center">Agent Gateway</h1>

<p align="center">
  <strong>所有客户端到 Agent 的统一网关：多频道接入、请求路由与调度</strong>
</p>

<p align="center">
  <a href="README.zh.md">中文</a>
  ·
  <a href="README.md">English</a>
  ·
  <a href="docs/zh/how-to/local-validation.md">本地验证</a>
  ·
  <a href="https://gitcode.com/openJiuwen/agent-gateway">代码仓</a>
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-Apache--2.0-green.svg" alt="License" />
  </a>
  <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/os-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="OS Support" />
</p>

**Agent Gateway** 是（Gateway + AgentServer）分离部署中的网关进程。它位于用户侧频道与 AgentServer 之间：接收来自 Web UI、TUI、ACP 客户端与 IM 平台的连接，把请求经单条 WebSocket（E2A 协议）路由给 AgentServer，并承载跨会话的公共服务——定时任务、心跳、健康检查与多实例隔离。

Gateway 以独立 Python 包 `agent-gateway` 构建和运行，提供两个入口：`agent-gateway`（Gateway + 频道）与 `agent-gateway-acp`（ACP 桥接）。

## 核心特性

| 能力 | 价值 |
| --- | --- |
| 多频道接入 | 一个进程同时服务 Web UI、TUI、ACP 客户端与 IM 平台（小艺、飞书、钉钉、企业微信、个人微信、Telegram、Discord、Slack、WhatsApp），各频道按配置惰性加载 |
| 请求路由 | 客户端请求统一归一化后经一条 E2A WebSocket 转发给 AgentServer，响应与流式分片按 request id 多路复用回收 |
| 会话与项目路由 | Gateway 维护路由状态（会话、项目、工作模式、频道绑定），客户端重连或切换时不丢上下文 |
| 定时任务 | cron 存储、调度器与命令回执在 Gateway；任务由 AgentServer 执行；系统自有的 `proactive.tick` 任务禁止手动创建或修改 |
| 媒体与文件转发 | IM 平台文件经 AgentServer 落盘，Gateway 不直接写入用户工程目录 |
| 安全防护 | WebSocket Origin 校验、user_id 白名单、显式剔除客户端伪造的认证键，凭据只从已认证频道转发 |
| 协议桥接 | ACP、A2A、SSH relay 与 web proxy 频道复用同一套路由层 |
| 健康检查与心跳 | 周期性健康检查与心跳让 Gateway / AgentServer 状态可观测，便于守护进程拉起异常的一半 |
| 多实例隔离 | `JIUWENSWARM_HOME` / `JIUWENSWARM_DATA_DIR` 隔离工作区，工作区锁避免两个 Gateway 服务同一实例 |

## 相关文档

- [文档导航](docs/README.md) —— 教程、操作指南、参考与架构说明
- [示例](examples/README.md) —— 可运行的 Mock AgentServer 示例
- [本地功能验证](docs/zh/how-to/local-validation.md) —— 端到端验证流程
- [变更记录](https://gitcode.com/openJiuwen/agent-gateway/releases)

## 环境要求

| 依赖 | 要求 |
| --- | --- |
| 操作系统 | Linux / macOS / Windows |
| Python | 3.11 ~ 3.13 |
| uv | 已安装 |
| 网络 | 可访问 `gitcode.com`（依赖含 git 源） |

## 安装

### 从源码安装

```bash
git clone https://gitcode.com/openJiuwen/agent-gateway.git
cd agent-gateway
uv sync
uv run agent-gateway --help
```

三方依赖已在 `pyproject.toml` 中完整声明；本包不依赖 `workswarm`，可独立安装运行。

若 `uv sync` 因网络失败或过慢，可先配置镜像：

```bash
export UV_DEFAULT_INDEX=https://pypi.org/simple
uv sync
```

### 从 wheel 安装

```bash
bash scripts/build.sh --wheel
pip install dist/agent_gateway-*.whl
```

## 快速上手

先在一个终端启动下游 AgentServer（也可使用 [examples/mock-agent-server](examples/mock-agent-server/) 中的 Mock 服务）：

```bash
uv run jiuwenswarm-agentserver --port 18092
```

再在另一个终端启动 Gateway：

```bash
# 为本实例隔离工作区
export JIUWENSWARM_HOME="$PWD/.local-home"

# 下游 AgentServer 与上游 WebChannel
export AGENT_SERVER_HOST=127.0.0.1
export AGENT_SERVER_PORT=18092
export WEB_HOST=127.0.0.1
export WEB_PORT=19000

uv run agent-gateway --port 19000
```

日志中的就绪标志：

- `[ExtensionManager] 加载 <name>` —— 扩展加载
- `Uvicorn running on http://127.0.0.1:19000` —— WebChannel 就绪
- `[Cron] loaded N job(s) from ...` / `background_cleanup: started ...` —— cron 与后台清理启动

若出现 `[App] Another Gateway is already serving this workspace`，说明同一工作区已有 Gateway 在运行，需先停止旧进程或更换 `JIUWENSWARM_HOME`。

完整自包含流程（Mock 下游 + `chat.send` 往返）见[快速开始](docs/zh/tutorial/01-quick-start.md)。

## 架构

```text
 Web UI / TUI / ACP / IM 频道
              │  WebSocket（E2A 帧）
              ▼
     Agent Gateway
       ├─ MessageHandler + ChannelManager
       ├─ WebChannel（uvicorn）/ TUI 路由
       ├─ cron 调度器 · 心跳 · 健康检查
       └─ 路由 / 会话绑定
              │  AgentServer WebSocket（E2A）
              ▼
      jiuwenswarm-agentserver
```

Gateway 不承担 Agent 执行：所有涉及工作区、模型凭据与工具沙箱的操作都由 AgentServer 完成。详见[架构说明](docs/zh/explanation/architecture.md)。

## 命令行参数

| 参数 | 说明 |
| --- | --- |
| `-u, --agent-server-url <URL>` | AgentServer WebSocket URL，优先级高于 `AGENT_SERVER_URL` / `AGENT_SERVER_HOST` + `PORT` |
| `-H, --host <HOST>` | WebChannel 绑定地址（默认取 `WEB_HOST`，否则 `127.0.0.1`） |
| `-p, --port <PORT>` | WebChannel 绑定端口（默认取 `WEB_PORT`，否则 `19000`） |
| `--web-path <PATH>` | WebChannel WebSocket 路径（默认取 `WEB_PATH`，否则 `/ws`） |
| `--name <name>` | 按 `instances.yaml` 启动命名实例 |
| `--dotenv <path>` | 启动时从 `.env` 文件加载环境变量 |

### 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `JIUWENSWARM_HOME` | `~` | 工作区根目录，实例目录为 `.jiuwenswarm` |
| `JIUWENSWARM_DATA_DIR` | 未设置 | 多实例隔离用的数据目录 |
| `AGENT_SERVER_URL` | 自动拼接 | AgentServer WebSocket URL（优先级最高） |
| `AGENT_SERVER_HOST` / `AGENT_SERVER_PORT` | `127.0.0.1` / `18092` | 未设置 URL 时用于拼接 `ws://host:port` |
| `WEB_HOST` / `WEB_PORT` / `WEB_PATH` | `127.0.0.1` / `19000` / `/ws` | WebChannel（uvicorn）监听地址 |
| `GATEWAY_HOST` / `GATEWAY_PORT` | `127.0.0.1` / `19001` | TUI 路由监听地址 |
| `AGENT_CONNECT_RETRY` / `AGENT_CONNECT_RETRY_INTERVAL` | `20` / `3` | 下游连接重试次数 / 间隔（秒） |

### config.yaml

配置文件位于 `$JIUWENSWARM_HOME/.jiuwenswarm/config/config.yaml`。首次运行可以不创建——文件缺失时 Gateway 告警并使用默认值。如需显式关闭所有 IM 频道：

```yaml
channels: {}
health_check:
  every: 60
  target: web
```

频道（`feishu`、`dingtalk`、`telegram`、`discord`、`slack`、`wecom`、`wechat`、`xiaoyi`、`whatsapp`）按需惰性加载：只有 `channels` 中出现的条目才会连同其依赖一起初始化。

## 支持的频道

在 Web UI 中启用频道，或在 `config.yaml` 中以 `enabled: true` 加上该平台凭据启用。

| 区域 | 频道 |
| --- | --- |
| 国内 | 小艺、飞书、钉钉、企业微信、个人微信 |
| 海外 | Telegram、Discord、Slack、WhatsApp |

各平台能力有差异：小艺与 WhatsApp 仅支持私聊；飞书、企业微信、钉钉、Telegram、Discord、Slack 还支持群聊，通常通过 @机器人 使用。飞书与企业微信额外支持数字人功能。详见[配置频道](docs/zh/how-to/configure-channels.md)。

## 本地验证

[本地功能验证指南](docs/zh/how-to/local-validation.md) 提供了一套自包含流程：用 Mock AgentServer 模拟下游，经 Gateway 的 `/tui` 路由走通上游往返，覆盖安装、工作区隔离、端口配置、启动标志、`chat.send` 链路与常见问题排查。

## 构建

```bash
bash scripts/build.sh              # 清理后构建 wheel + sdist
bash scripts/build.sh --wheel      # 只构建 wheel
bash scripts/build.sh --sdist      # 只构建 sdist
bash scripts/build.sh --no-clean   # 保留 build/ 历史产物
```

产物位于 `dist/`：

- `dist/agent_gateway-<version>-py3-none-any.whl`
- `dist/agent_gateway-<version>.tar.gz`

## 测试

```bash
./run_tests.sh              # 运行全部测试
./run_tests.sh -u           # 只跑单元测试
./run_tests.sh -c           # 跑测试并生成 HTML 覆盖率报告
./run_tests.sh -p           # 并行执行（需 pytest-xdist）
```

`pytest.ini` 默认对 `agent_gateway` 开启覆盖率，输出：

- 终端报告（term-missing）
- `htmlcov/index.html`
- `coverage.xml`

## 参与贡献

欢迎开发者参与 Agent Gateway 的建设：

- 提交 Bug、功能建议或使用问题：[Issues](https://gitcode.com/openJiuwen/agent-gateway/issues)
- 提交代码、文档或示例：[Pull Requests](https://gitcode.com/openJiuwen/agent-gateway/pulls)

贡献前请阅读 [贡献指南](CONTRIBUTING.md)，了解调试流程、代码风格和提交规范。

## 加入社区

| 入口 | 用途 | 链接 |
| --- | --- | --- |
| 官网 | 产品介绍、动态与生态建设 | [访问官网](https://openjiuwen.com) |
| SIG | 技术路线、工程实践、生态共建 | [加入 SIG](https://openjiuwen.com/community/sig-center) |
| Swarm Skills Hub | 浏览、发布和复用 Agent Skill | [访问 Swarm Skills Hub](https://swarmskills.openjiuwen.com/) |

## License

本项目基于 [Apache License 2.0](LICENSE) 开源。

本产品仅作为流程编排工具，不包含 AI 模型能力；用户在连接 AI 模型用于特定业务场景时，需自行承担欧盟 AI 法案等相关合规义务。
