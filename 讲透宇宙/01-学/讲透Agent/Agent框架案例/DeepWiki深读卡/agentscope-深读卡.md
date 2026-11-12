# AgentScope 深读卡 —— 阿里 ModelScope 出品"为日益 agentic 的 LLM 而生"的双层多 Agent 框架

> **定位**：阿里 ModelScope 开源的多 Agent 平台（Python），设计哲学是**为 increasingly agentic 的 LLM 服务**——不 imposing 固定 workflow，而是靠模型原生推理 + `Toolkit` 中间件动态工具 + 分层记忆；消息机制上与 AgentVerse 同源的 **Msg 协议 + hub-and-spoke pipeline**，v1 转向 developer-first（显式 API、类型化消息、内建 OpenTelemetry）。
> **本地**：`repos/agentscope`（modelscope/agentscope）｜**深读**：deepwiki **58 子页**归档 `deepwiki/agentscope/full.md`（2026-08-21，654KB）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心抽象 | Agent 基类 + 生命周期 | `AgentBase`（reply/observe + hooks）、`AgentMixin`（分布式 mixin）|
| 推理循环 | ReAct Agent 州机 | `ReActAgent`（reasoning→acting 循环，23KB 专页详解）、`Toolkit` + 中间件链 |
| 消息协议 | 结构化消息与内容块 | `Msg`（可扩展 content blocks：text/tool_use/image/audio…）|
| 记忆 | 三层记忆 | 短期（in-memory long-term memory）、长期（`LongTermMemory`Base+持久化后端）、知识库（RAG）|
| 编排 | Pipeline/Hub | `MsgHub`（群聊广播）、sequential/pipeline 原语、`ms_agent` 生态 |
| 分布式 | RPC 双工通信 | `RpcAgent`（netoquest 双向流，v1 重点）、placeholder/状态迁移 |
| 可观测 | 零侵入 tracing | OpenTelemetry 全组件埋点 |
| 工具生态 | 中间件式工具 | `Toolkit.register` + schema 校验中间件 + MCP 支持 |

## 二、核心机制

1. **Model-driven 而非 workflow-driven**（Design Philosophy）：不预设 SOP 式流程图，框架只提供推理循环原语（ReActAgent）+ 动态 Toolkit——把"编排智能"下放给模型本身，与 MetaGPT（SOP 固化）形成范式对照。
2. **Toolkit 中间件链**：工具调用可插入中间件（schema 校验/依赖注入/重试），`register` 时声明参数 Pydantic 模型；对比 LangChain Tool 的"函数+schema"，多了责任链维度。
3. **Msg content blocks**：消息体是可扩展块数组（对齐 Anthropic/OpenAI 的 tool_use 块语义），跨模态（text/image/audio/video）与工具轨迹统一在一个协议里——讲透Agent"消息即数据结构"的工业版。
4. **v1 双形态部署**：单机（直接 python 对象互调）与分布式（`RpcAgent` 双向流 + placeholder 引用 + 状态迁移）共享同一编程模型——教学时可先单机讲清再无缝切分布式。

## 三、与讲透系列的对位

| AgentScope 概念 | 讲透系列对应 |
|---|---|
| `ReActAgent` reasoning/acting 州机 | 讲透Agent/01 §ReAct（+ smolagents 同型对照）|
| `Toolkit` + 中间件 | 讲透Agent/02 §工具调用工程（middleware 是增量点）|
| `MsgHub` 广播 | 讲透多Agent协作/02 §发布订阅 |
| 三层记忆 | 讲透Agent/04 §记忆机制 |
| `RpcAgent` 双向流 | 讲透分布式AI系统（讲分布式 Agent 的活样本）|
| OTel 零侵入 | 讲透Agent/00 §可观测性 |

## 四、关键入口

```
src/agentscope/agent/_agent_base.py      # AgentBase: reply/observe + hooks
src/agentscope/agent/_react_agent.py     # ReActAgent 主循环（wiki 6 号页 23KB 逐行拆）
src/agentscope/agent/_toolkit.py         # Toolkit + 中间件
src/agentscope/message/_message_block.py # Msg content blocks
src/agentscope/memory/                   # 长期记忆 + 持久化
src/agentscope/rpc/                      # 分布式 RpcAgent
```

## 五、深读子页地图（58 页精选 7）

3 Core Concepts｜4-5 Agent System + AgentBase（hooks 生命周期）｜**6 ReActAgent Implementation（23KB，最厚核心页）**｜8 Message Protocol（content blocks）｜Agent Memory 章节｜Rpc/Distributed 章节｜Dashboard/Studio 可视化页。

## 六、与"我们"的关系（一句话）

AgentScope 是"模型驱动 vs SOP 驱动"光谱上与 MetaGPT 相对的锚点，58 页 wiki 已全归档——讲透Agent/01 的三种经典范式对比从此有了两极的一手实现可查。

---
生成：2026-08-21 · deepwiki 58 页全归档
