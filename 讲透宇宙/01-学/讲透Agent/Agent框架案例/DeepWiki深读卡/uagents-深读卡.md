# uagents 深读卡 —— Fetch.ai 自主 Agent 框架：链上身份+签名信封+去中心化发现

> **定位**：Fetch.ai 开发的轻量 Python 自主 Agent 框架，每个 Agent 启动即注册到 Fetch.ai 区块链上的 Almanac 智能合约，实现全局发现与互联。核心差异化是"Agent 经济"路线：框架不内置 LLM 循环，专注加密身份、签名消息（Envelope）、mailbox 异步收信与 Agentverse 生态托管，是 Agentverse/ASI 生态的主力框架（配套 LangChain/CrewAI/MCP/A2A 适配层）。
> **本地**：`repos/uagents`（fetchai/uAgents）｜**深读**：deepwiki 34 子页归档 `deepwiki/uagents/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 生态层（Agentverse/ASI） | 云端托管、mailbox 代收、agent 市场 | Agentverse API、`av` CLI |
| 适配层 `uagents-adapter` | 桥接主流 AI 生态 | LangchainRegisterTool、A2ARegisterTool、MCP adapter |
| 高层 `uagents` | Agent 运行时与开发体验 | `Agent`、`Bureau`、`Protocol`、`Context`、`@on_message/@on_interval` |
| 通信层 | 签名信封收发、同步/异步模式 | `Dispenser`、`Dispatcher`、`ASGIServer`、`Envelope` |
| 发现层 | 地址→端点解析 | `GlobalResolver` → AlmanacApiResolver / NameServiceResolver |
| 注册层 | 链上/API 注册与续期 | `RegistrationPolicy` → `AlmanacContract`（Fetch.ai 链） |
| 核心层 `uagents-core` | 身份/信封/协议摘要底座 | `Identity`、`envelope`、protocol digest、`KeyValueStore` |
| 实验层 | 高级特性 | Dialogues、QuotaProtocol、Wallet Messaging、ChatAgent、Mobility |

## 二、核心机制

1. **内外双 Context 分治**（Context System）：`InternalContext` 服务 `on_interval`/`on_startup` 等主动行为；`ExternalContext` 收到消息才创建，自带 `_replies` 合法回复类型表与 `validate_replies()`——"什么消息能回什么"成为框架级约束。创新点：把消息协议的状态校验从应用代码上收到框架层。
2. **schema digest 寻址 + 签名信封**（Communication / Message Envelopes）：消息=Pydantic Model，类型标识=schema digest 哈希；发送时本地 agent 走 `dispatch_local_message` 进程内短路，远端则 resolve→`Envelope`(sender/target/session/schema_digest/payload/signature/expires)→签名→Dispenser 异步队列 HTTP 投递；同步模式用 `x-uagents-connection: sync` 头让响应信封随 HTTP 响应直接返回。创新点：消息类型哈希当路由键、协议 manifest digest 当服务发现键。
3. **Almanac 链上注册 + 多策略 Resolver**（Agent Registration / Address Resolution / Almanac Contract）：agent 地址→endpoint 映射写入 Fetch.ai 链上智能合约并周期重注册（Agentverse v2 API 则一次注册永久生效）；`GlobalResolver` 编排 Almanac API、NameService（按名寻址）等策略。创新点：把多 Agent 服务发现从中心化 registry 换成智能合约。
4. **Mailbox 异步代收**（Mailbox Client / Communication）：NAT/防火墙后的 agent 注册到 Agentverse Mailbox，`MailboxClient` 用 attestation 挑战-响应认证后轮询取信，取回的信交给与 HTTP 入口完全相同的 `_handle_envelope`→dispatch 路径——传输差异对 handler 完全透明。创新点：离线/内网 agent 与公网 agent 共用一套消息语义。

## 三、与讲透系列的对位

| uAgents 概念 | 讲透系列对应概念 |
|---|---|
| Protocol + `@on_message` handler | 讲透Agent：工具调用/事件处理（不内置 ReAct，LLM 循环外置给 AI Engine/ChatAgent） |
| Internal/External 双 Context | 讲透Agent：上下文工程（主动/被动两套执行环境） |
| broadcast(protocol_digest)+Almanac | 讲透多Agent协作：动态组网（按协议 digest 发现对端再群发） |
| Envelope 签名+expires+attestation | 安全沙盒（身份认证+防重放，而非进程隔离） |
| KeyValueStore + EnvelopeHistory | 记忆机制（最简持久记忆+会话历史审计） |

## 四、关键入口

```text
python/src/uagents/agent.py           # Agent/Bureau 主体；_build_context() 产出 InternalContext
python/src/uagents/context.py         # Context→Internal→External 三层；send_raw() 消息主流程
python/src/uagents/protocol.py        # Protocol 与 ProtocolSpecification；manifest/digest 计算
python/src/uagents/communication.py   # Dispenser 出站队列；send_exchange_envelope HTTP 投递
python/src/uagents/dispatch.py        # Dispatcher 入站路由；PendingResponse 支撑同步 query
python/src/uagents/asgi.py            # ASGIServer：/submit 收信、REST 端点、同步回包
python/src/uagents/mailbox.py         # MailboxClient：attestation 认证+轮询取信
python/uagents-core/uagents_core/envelope.py  # Envelope 结构与 sign/verify（uagents-core 底座）
```

## 五、深读子页地图（34 页精选 6）

1. **Context System**（27KB 全库最大页）——双 Context 分治与消息主流程的最权威拆解
2. **Protocol System**——协议规范、digest 计算、角色化实现
3. **Message Envelopes**——信封字段、端点解析与投递状态跟踪
4. **Mailbox Client**——attestation 认证与轮询细节
5. **Almanac Contract**——链上注册的合约侧视图（注册消息结构/批量注册）
6. **A2A Protocol Bridge**——与 Google A2A 的双向桥接（出站/入站+AP2 支付桥）

## 六、与"我们"的关系（一句话）

想看"Agent 当一等网络公民"（链上身份、去中心化发现、离线可收信）如何落成代码，uAgents 是 Agent 经济路线最完整的 Python 参照系，且其"LLM 循环外置"的设计恰好反衬出 Agent 框架该管什么、不该管什么。

---
生成：2026-08-21 · deepwiki 34 页全归档
