# agentfield 深读卡 —— "Kubernetes for AI Agents"：Go 控制平面 + 三语言 SDK 的多 Agent 运行时

> **定位**：自主 AI Agent 的后端基础设施——无状态 Go 控制平面编排 Python/TypeScript/Go 三语言 agent 节点（agent-as-microservice），内建分层记忆、W3C DID/VC 密码学审计与 Harness 外部编码代理编排。README 自称 "Kubernetes for AI Agents"；v0.1.x 早期活跃项目，无论文背书。⚠️ 注意：它**不是**基准评测场（wiki 87 页无任何 benchmark/多环境任务评测内容）。
> **本地**：`repos/agentfield`（Agent-Field/agentfield）｜**深读**：deepwiki 87 子页归档 `deepwiki/agentfield/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| CLI / Desktop | 项目脚手架、secrets 加密管理、健康监控 GUI | `af` binary（`cmd/af`）、Electron 桌面应用 |
| Control Plane（Go） | 无状态编排枢纽：注册/发现/路由执行/工作流 DAG/VC 签发 | `cmd/agentfield-server`、`/api/v1/execute/{node}.{capability}` |
| Agent Node SDK | 三语言**同语义** Agent 运行时，节点=微服务 | `agentfield.Agent`（Py）/ `@agentfield/sdk.Agent`（TS）/ Go `agent.New()` |
| 能力层 | 非确定性推理与确定性工具强制分离 + 能力分组 | `@app.reasoner()` / `@app.skill()` / `AgentRouter` |
| Harness 层 | 把长任务委派给外部编码代理（子进程编排） | `HarnessRunner` + OpenCode/Claude Code/Codex/Gemini providers |
| AI 层 | 多 provider 文本/嵌入/多模态 + 限流重试熔断 | `app.ai()`、litellm（Py）/ ai-sdk（TS） |
| Memory 层 | KV + 向量存储、4 级 scope 分层回退（免外部数据库起步） | `MemoryInterface`、SQLite+BoltDB / PostgreSQL+pgvector |
| Identity 层 | 每节点 W3C DID + 执行 VC 链（防篡改审计） | `did_auth.py`、`vc_service.go` |

## 二、核心机制

1. **Reasoner/Skill 语言级强制分离**（Core Concepts; Defining Reasoners/Skills）：`@app.reasoner()` 只放 LLM 决策逻辑、`@app.skill()` 只放确定性工具（禁 LLM），决策与执行在**部署拓扑**层面分开，Reasoner 自动在 dashboard 记为可追踪"推理步骤"——同类框架把 planning 和 tool 混在一个 ReAct 循环里，这里拆成一等公民双原语。
2. **Memory 四级 scope 分层回退**（Memory Scopes; Context Propagation）：`workflow→session→actor→global` 逐级查找，scope 由 HTTP header（`X-Workflow-ID`/`X-Session-ID`）随 `app.call()` 自动跨 agent 传播——跨 Agent 共享状态零手工 key 管理；且记忆不在 SDK 内部而在**控制平面集中服务**，后端自动切换 SQLite+BoltDB/pgvector。
3. **DID + VC 执行链审计**（Identity & Trust; Verifiable Credentials; Audit Trail Export）：每节点有 `did:agentfield:node:*` 身份，每次执行生成含 input/output hash 的签名 Verifiable Credential，串成可导出、可独立验证的防篡改工作流链——non-repudiation 内建，同类框架几乎没有。
4. **Harness 子进程编排自主编码代理**（Harness Concepts & Architecture; Harness Providers; Schema Extraction & Repair）：`app.harness()` 把多轮自主任务委派给 Claude Code（原生 SDK）/Codex/OpenCode/Gemini（CLI 子进程）——空闲看门狗（默认 300s 杀进程组）、全局信号量限并发、litellm 半闭连接死锁强制恢复、JSON schema 提取 + AI 修复回路——把外部 coding agent 统一抽象成"工具"。

## 三、与讲透系列的对位

| AgentField 概念 | 讲透系列对应概念 |
|---|---|
| Reasoner（LLM 决策）/ Skill（确定性工具） | 讲透Agent：ReAct 循环中"思考"与"行动"的强制拆分 |
| `app.call()` 经控制平面路由 + 自动 Workflow DAG | 讲透多Agent协作：中心化编排（Hub-and-Spoke vs P2P） |
| Memory 4-scope 分层回退 | 讲透Agent/讲透学习型Agent：记忆机制分层（工作记忆→长期记忆） |
| Harness 子进程 + 看门狗 + permission_mode | 安全沙盒：外部编码代理的进程级隔离与权限矩阵 |
| `X-Workflow-ID` 等 header 传播 | 上下文工程：跨调用元数据传递与追踪 |

## 四、关键入口

```
control-plane/cmd/agentfield-server/main.go       # 控制平面服务入口（无状态编排枢纽）
control-plane/cmd/af/main.go                      # af CLI：init/server/secrets/agent 管理
sdk/python/agentfield/agent.py                    # Python Agent：注册/心跳/执行/memory scope 回退
sdk/python/agentfield/harness/_runner.py          # HarnessRunner 生命周期：看门狗+schema 修复
sdk/python/agentfield/harness/providers/claude.py # Claude Code 原生 SDK provider（permission_mode 映射）
sdk/typescript/src/agent/Agent.ts                 # TypeScript 同语义 Agent
sdk/go/agent/agent.go                             # Go SDK Agent（New() 构造 + lease/心跳注册）
control-plane/internal/storage/storage.go         # StorageProvider 接口：SQLite/Postgres 双实现
```

## 五、深读子页地图（87 页精选 6）

1. **Core Concepts** — 全系统术语一次性定义（Reasoner/Skill/Memory Scope/DID/ExecutionContext），87 页的"词典页"
2. **Memory Scopes** — 4 级回退顺序与 header→scope 映射的实现细节
3. **Harness Concepts & Architecture** — 子进程看门狗、静默死锁恢复、provider 差异矩阵（最独特的一章）
4. **Verifiable Credentials / Audit Trail Export** — VC 数据模型、验证序列与审计链导出
5. **Cross-Agent Calls** — target 解析（`{node}.{capability}`）、本地/远程调用决策、上下文透传
6. **Documentation Chatbot 五连页（61-65）** — 官方旗舰 RAG 范例：ingestion→query planning→parallel retrieval→self-aware synthesis 全流程

## 六、与"我们"的关系（一句话）

把"Agent 当微服务部署"这条路线（注册/发现/路由/身份/记忆/DAG 观测）做全的最完整开源样本——学 Agent 的**基础设施视角**（比又一层 prompt 循环稀缺得多），也是 Harness 编排外部编码代理的参考实现。

---
生成：2026-08-21 · deepwiki 87 页全归档（注：定位以 wiki Overview 为准——是 Agent 控制平面基础设施，非评测场）
