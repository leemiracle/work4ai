# 架构说明

本文解释 Agent Gateway 的定位、数据流、模块划分与关键设计决策。

## 定位

系统采用分离部署：**Gateway + AgentServer**。

- **Gateway**：面向客户端与 IM 平台的接入层，负责多频道接入、请求归一化、路由、会话绑定、定时任务调度、心跳与健康检查。
- **AgentServer**：执行层，负责 Agent 循环、模型调用、工作区读写、工具沙箱与文件落盘。

Gateway 对 Agent 执行是无状态的：所有涉及工作区、模型凭据和工具沙箱的操作都由 AgentServer 完成。

## 数据流

```text
 Web UI / TUI / ACP / IM 频道
              │  WebSocket（E2A 帧）
              ▼
     Agent Gateway
       ├─ MessageHandler + ChannelManager
       ├─ WebChannel（uvicorn）/ TUI route
       ├─ Cron scheduler · heartbeat · health check
       └─ routing / session binding
              │  AgentServer WebSocket（E2A）
              ▼
      jiuwenswarm-agentserver
```

一条客户端请求的典型路径：

1. 频道接收原始消息（WebSocket 帧、IM 平台事件等）。
2. Gateway 将消息归一化为统一的 E2A 请求字段（`user_id`、`message_id`、`params`、会话信息等）。
3. `MessageHandler` 解析命令与路由信息，`ChannelManager` 维护频道与会话绑定。
4. `routing` 层通过单条 AgentServer WebSocket 发送请求，并按 request id 多路复用响应与流式分片。
5. Gateway 将响应投影回原频道（WebSocket 事件、IM 消息、ACP/A2A 响应等）。

E2A 的字段定义见[E2A 协议参考](../reference/e2a-protocol.md)。

## 模块划分

| 模块 | 职责 |
| --- | --- |
| `app_gateway.py` | 进程入口：启动编排、AgentServer 连接与重试、频道配置应用、工作区锁、后台任务生命周期 |
| `channel_manager/` | 频道注册、懒加载与消息分发；`web/`、`tui/`、`im_platforms/`、`protocol/`（ACP、A2A、SSH、web proxy） |
| `message_handler/` | 消息归一化、命令解析、会话加入/退出、演进审批等处理逻辑 |
| `routing/` | AgentServer 客户端、E2A 转发、路由绑定、会话映射与多实例路由 |
| `cron/` | 定时任务存储、调度器与命令回执；任务由 AgentServer 执行 |
| `heartbeat/`、`health_check/` | 周期性健康检查与心跳，暴露 Gateway / AgentServer 状态 |
| `im_pipeline/` | IM 入站/出站适配与媒体处理 |
| `extensions/` | 扩展注册、认证等可插拔能力 |
| `embedded/` | 内置运行时适配：agent 预热、附件、会话、HarmonyOS 等 |

## 启动顺序

1. 解析 `--dotenv` / 环境变量，准备工作区（首次启动会初始化默认技能、配置等）。
2. 读取 `config.yaml`，解析 `channels` 与 `health_check`。
3. 建立到 AgentServer 的 WebSocket 连接（失败时按 `AGENT_CONNECT_RETRY` 重试）。
4. 获取工作区单例锁 `.gateway.lock`，防止同一工作区启动多个 Gateway。
5. 启动 cron 调度器、心跳与健康检查、WebChannel 与 TUI 路由。
6. 按 `channels` 中的条目惰性加载 IM 频道及其依赖。

## 关键设计决策

- **单条下游连接 + request id 多路复用**：所有客户端共享一条到 AgentServer 的 WebSocket，避免每个客户端建立独立下游连接；响应与流式分片按 request id 解复用。
- **频道惰性加载**：只有 `channels` 中出现的频道才会初始化，未配置的频道不引入依赖、不占用连接。
- **会话与项目路由状态在 Gateway**：客户端重连或切换频道时，Gateway 保留会话、项目、工作模式与频道绑定。
- **工作区单例锁**：锁由操作系统文件锁持有，进程崩溃会自动释放；同一工作区只允许一个 Gateway，避免 cron 重复调度。
- **安全边界**：WebSocket Origin 校验、`user_id` 白名单、显式剔除客户端伪造的认证键；凭据只从已认证频道转发。
- **系统任务保护**：`proactive.tick` 等系统自有任务禁止手动创建或修改。
- **执行无关性**：Gateway 不直接写用户工程目录，IM 文件经 AgentServer 落盘。

## 非目标

- 不执行 Agent 循环，不调用模型。
- 不读写用户工程目录中的业务文件。
- 不替代 AgentServer 的权限、工具与沙箱控制。

---

## 返回导航

- [返回文档首页](../../README.md)
- [E2A 协议参考](../reference/e2a-protocol.md)
- [命令行与环境变量](../reference/cli-and-environment.md)
