# llocalsearch 深读卡 —— 全本地隐私搜索 Agent：Ollama 小模型 + ReAct + 每会话 RAG

> **定位**：LLocalSearch 是完全本地化运行的搜索 Agent——Go(LangChainGo) 后端把 Ollama 本地小模型包装成 ReAct Agent，配 SearXNG 隐私搜索与 ChromaDB 向量库完成"搜索→抓取→总结"。差异化：零 API key、面向 300€ 消费级 GPU 的小模型工程、每会话向量记忆隔离；本地 AI 搜索方向的早期代表作。
> **本地**：`repos/llocalsearch`（nilsherzig/LLocalSearch）｜**深读**：deepwiki 19 子页归档 `deepwiki/llocalsearch/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端 | SvelteKit 聊天 UI、SSE 流式渲染、历史/设置/暗色模式 | `src/lib/*.svelte`, `custom-server.js` |
| API 层 | SSE stream 端点、模型列表、聊天历史、CORS | `backend/apiServer.go` |
| Agent 编排 | ReAct 循环、会话管理、迭代上限、解析容错 | `backend/agentChain.go`（`startAgentChain`） |
| 工具层 | WebSearch / WebScrape / SearchVectorDB 三工具 | `backend/llm_tools/*.go` |
| 推理后端 | Ollama 客户端工厂、模型存在性检查与拉取、嵌入模型 | `backend/utils/llm_backends.go` |
| 向量存储 | 摄取管线（清洗/切块/元数据）+ 每会话命名空间 | `backend/utils/vector_db_handler.go` |
| 事件桥 | LangChainGo 回调 → SSE JSON 流（过程全透明） | `backend/utils/customHandler.go` |
| 基础设施 | docker-compose 编排 backend/frontend/SearXNG/Chroma | `docker-compose.yaml`, `searxng/` |

## 二、核心机制

1. **每会话向量库命名空间（会话即 RAG 记忆）**【Agent Chain / Tool System / LLM Integration】：WebScrape 不把原始 HTML 塞进上下文，而是 bluemonday 清洗 → TokenSplitter 切块 → Ollama 嵌入 → 写入 ChromaDB 的会话 UUID 命名空间；Agent 再用 SearchVectorDB 以余弦相似度 + `MinResultScore` 阈值 + 结果去重取回片段。整场对话的网络阅读史变成会话私有外部记忆，会话间零串扰——区别于"把搜索结果直接拼进 prompt"的 Perplexity 类实现，是该仓库最值得偷的架构点。
2. **为不可靠小模型兜底的 ReAct 容错**【Agent Chain】：`agents.NewExecutor` 跑 ConversationalAgent（MaxIterations 防死循环）；`WithParserErrorHandler` 捕获小模型的 ReAct 格式错误 → 推送 `StepHandleParseError` 事件 → 用 `ParsingErrorPrompt()` 让模型自我纠正而非崩溃；收尾再以一次独立 `llm.Call` 从聊天历史生成 3 词会话标题。整套设计假设"模型会犯错"，是本地小模型 Agent 的工程范式。
3. **CustomHandler 回调桥：Agent 过程全透明**【Tool System / Agent Chain】：自定义 LangChainGo 回调拦截 `HandleToolStart` / `HandleAgentAction` / `HandleSourceAdded` / 流式 token，打包成 `HttpJsonStreamElement` 经 Go channel 推给 SSE——用户在 UI 实时看到每步思考、动作与来源链接，隐私优先之外叠加"可审计"。
4. **全本地微服务拓扑**【System Architecture / Containerization and Deployment】：docker-compose 编排 Go 后端 + SvelteKit 前端 + SearXNG + ChromaDB 四容器；Ollama 通常跑宿主机经 `host.docker.internal` 接入；全系统唯一出网流量是 SearXNG 发出的匿名搜索请求。

## 三、与讲透系列的对位

| LLocalSearch 概念 | 讲透Agent / 讲透多Agent协作 对应概念 |
|---|---|
| `agents.NewExecutor` ReAct 循环（Thought/Action/Observation） | ReAct 循环（感知-思考-行动核心章） |
| `llm_tools` 三工具（Name/Description/Call 契约） | 工具调用（工具注册与描述工程） |
| ConversationWindowBuffer + ChromaDB 会话命名空间 | 记忆机制（短期窗口记忆 + 外部检索记忆/RAG） |
| CustomHandler → SSE 事件流 | 上下文工程 / Agent 可观测性与流式协议 |
| `startAgentChain` 单编排器（Layer1 判工具 / Layer2 精炼） | 编排模式（单 Agent 循环编排，非多 Agent 协作） |

## 四、关键入口

```go
backend/agentChain.go                        // 核心编排 startAgentChain()：会话/模型/工具/Executor 组装，~180 行读完全部主逻辑
backend/utils/customHandler.go               // 回调桥：LangChainGo 事件 → HttpJsonStreamElement → SSE 前端
backend/llm_tools/simple_websearch.go        // WebSearch：SearXNG GET 查询 + sync.WaitGroup 并行 + 会话级去重
backend/llm_tools/tool_webscrape.go          // WebScrape：下载网页 → 清洗切块 → 写入 ChromaDB 会话命名空间
backend/llm_tools/tool_search_vector_db.go   // SearchVectorDB：查询嵌入 + 余弦检索 + 阈值过滤 + 去重
backend/utils/vector_db_handler.go           // 摄取管线：bluemonday / TokenSplitter / URL 元数据溯源
backend/utils/llm_backends.go                // Ollama 工厂：NewOllama / 嵌入模型(8192 ctx) / CheckIfModelExistsOrPull
backend/apiServer.go                         // SSE stream 端点、模型列表、聊天历史接口（前后端契约）
```

## 五、深读子页地图（19 页精选 5）

1. **Agent Chain**（第 3 页）——ReAct 循环 + 会话管理 + SSE 协议 + 错误恢复，全仓精华所在
2. **Tool System**（第 4 页）——三工具接口与摄取管线，RAG 细节最全的一页
3. **LLM Integration**（第 5 页）——Ollama 嵌入管线/模型拉取 + ChromaDB 命名空间数据流
4. **Containerization and Deployment**（第 12 页）——全本地四容器拓扑与网络配置
5. **Glossary**（第 19 页）——自然语言概念 ↔ 代码实体映射表，速查友好

## 六、与"我们"的关系（一句话）

它是"用最小工程把本地小模型变成能上网的 ReAct Agent"的最佳精读样本——180 行主文件读完即可手写一个本地搜索 Agent，且每会话向量记忆与解析容错两招可直接搬进自己的 Agent 项目。

---
生成：2026-08-21 · deepwiki 19 页全归档
