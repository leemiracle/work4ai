# openagents 深读卡 —— 港大全栈开源 Agent 平台：数据分析 + 插件调用 + 自动浏览网页三站台

> **定位**：OpenAgents 是港大 XLANG 实验室（Tao Yu 组）的"语言 Agent 落地野外（in the wild）"开源平台，用完整 Web UI + Flask 后端 + 三个真实 Agent（Data/Plugins/Web）对标 ChatGPT Plus 的数据分析、插件与浏览能力。差异化在于不做 PoC 框架而是补齐非专家用户可用性与应用层工程；有论文背书（arXiv 2310.10634，引用量极高），是 AutoGPT 之后"平台型 Agent"的代表项目。
> **本地**：`repos/openagents`（xlang-ai/OpenAgents）｜**深读**：deepwiki 30 子页归档 `deepwiki/openagents/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Frontend（Next.js/React/TS） | 聊天 UI、Agent/插件选择器、文件管理、富内容渲染 | `Chat.tsx`、`AgentSelect.tsx`、`home.state.tsx`、`types/agent.ts` |
| Backend（Flask） | REST API、会话管理、流式渲染、LLM 适配、代码执行队列 | `app.py`、`api/chat_*.py`、`display_streaming.py`、`kernel_publisher.py` |
| Real Agents（"一 Agent 一文件夹"） | 三大 Agent 领域逻辑 | `data_agent/`、`plugins_agent/`、`web_agent/` 各自 executors/chains |
| Shared Adapters | Agent↔后端胶水：流解析、数据模型、记忆、callbacks | `adapters/data_model/message.py`、`models/azure_openai.py` |
| Storage | 会话持久化 + 缓存 | MongoDB（用户/对话池）、Redis（缓存） |
| 外部执行面 | 代码沙盒、第三方 API、真实浏览器 | Code Interpreter 容器、200+ plugin API、WeBot Chrome 扩展 |

## 二、核心机制

1. **"Real Agents" 三明治架构**（Architecture 页）：命名即立场——不止包含概念层语言 Agent，还在 `adapters/` 显式填补"Agent 概念"与"生产后端"之间的缝隙（流解析、MessageDataModel/HTMLDataModel、共享记忆、callbacks）。基于 LangChain 二次开发，但把 PoC 框架补成了可部署全栈系统，这是它区别于同类框架的本质。
2. **Web Agent 双模式浏览器操控**（Web Agent 页）：`WebotCallingChain` 先把自然语言意图解析为 `{instruction, start_url}`，`WebBrowsingExecutor` 进入"感知 DOM → 决策 → 执行动作"循环；提供 basic（`WebotChain` 直映射）与 react（`ReActWebotChain` 带 thought/plan/action history）两档推理，动作由 WeBot Chrome 扩展在真实浏览器落地——走的是 ChatGPT 插件之外的"真浏览器"路线。
3. **Auto Plugin Selection**（Plugins Agent 页）：200+ 插件不靠人挑，ToolSelector 对 query + 对话历史做 embedding 相似度检索自动选 top-5 插件，再交给 AgentExecutor（持 `ConversationReActBufferMemory`）ReAct 式决定何时调 PluginExecutor 打外部 API——开源复刻并超越了 ChatGPT Plugins 的选插件体验。
4. **双层记忆 + 池化资源**（Memory Management 页）：UserMemoryManager/ChatMemoryManager/MessageMemoryManager 三层管理器，Redis 缓存 + MongoDB 持久化；Message Pool 与 API Key Pool 把会话上下文和用户插件密钥统一池化管理。

## 三、与讲透系列的对位

| OpenAgents 概念 | 讲透Agent 系列对应概念 |
|---|---|
| `ReActWebotChain`（thought→action 循环） | ReAct 循环（推理与行动交替） |
| ToolSelector embedding 检索 200+ 插件 | 工具调用（工具检索式 tool selection） |
| `ConversationReActBufferMemory` + Redis/MongoDB | 记忆机制（短期缓冲记忆 + 长期持久化记忆） |
| Kernel Publisher + Code Interpreter 容器 | 安全沙盒（代码执行隔离） |
| `display_streaming.py` 流式富内容渲染 | 上下文工程（执行结果→UI 呈现的流式管线） |
| `adapters/` 共享适配层 | 编排模式（平台化 glue layer 解耦 Agent 与宿主） |

## 四、关键入口

```python
backend/api/chat_plugin.py            # Plugins Agent 聊天入口：ToolSelector→AgentExecutor→PluginExecutor 流水线
backend/api/chat_webot.py             # Web Agent 聊天入口（意图→指令→浏览器循环）
backend/api/language_model.py         # LLM 注册表：加新模型只需在此注册（含自托管 FastChat 端点）
backend/memory.py                     # 双层记忆：Redis 缓存 + MongoDB 持久化、Message/API Key Pool
backend/kernel_publisher.py           # Data Agent 代码执行队列（对接 Code Interpreter 沙盒）
backend/display_streaming.py          # 流式响应渲染：文本/图片/表格/JSON 四类富内容解析
real_agents/web_agent/executors/web_browsing_executor.py  # 浏览器 ReAct 执行器（basic/react 双模式）
real_agents/plugins_agent/plugins/plugin_names.py         # 200+ 插件注册表（新插件登记处）
```

## 五、深读子页地图（30 页精选 6）

1. **Architecture**（L246）——组件/数据流/部署三视角全景，理解全栈分层的第一站
2. **Web Agent**（L6646）——双模式浏览器 Agent 的完整机制与 Chrome 扩展集成
3. **Plugins Agent**（L6314）——四组件插件执行流水线 + Auto Plugin Selection 检索式选工具
4. **Memory Management**（L3439）——三层 memory manager 与双存储后端的工程实现
5. **Creating Custom Agents**（L8582）——六步扩出新 Agent 的实操指南（扩展性设计验证）
6. **Docker Deployment**（L7649）——含 GPU/沙盒容器的容器化部署细节

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这个仓库的独特价值是展示"从 ReAct 循环到真实用户可用产品"之间缺的那一层工程——adapters 流解析、流式富内容渲染、池化记忆、插件检索选择，正是 PoC demo 与 ChatGPT 级产品的差距所在。

---
生成：2026-08-21 · deepwiki 30 页全归档
