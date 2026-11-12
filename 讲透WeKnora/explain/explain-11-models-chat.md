# explain-11 · internal/models/chat/chat.go — 模型接入网关的契约与工厂

```
文件路径: internal/models/chat/chat.go
行数:     204 行
所属层:   模型接入层（layer:model-gateway）
一句话:   定义 Chat 接口、Message/ChatOptions/ChatConfig 三大契约与 NewChat 工厂——27 家模型供应商、本地 Ollama、观测/限流装饰链都在这 204 行里完成分派。
```

## 一、角色定位

RAG 问答、Agent 推理、Wiki 生成、摘要、追问建议——每个 LLM 场景最终都要"把消息发给某家模型供应商"。本文件是 L6 模型接入层的**契约中枢**：不含任何供应商细节，却决定供应商必须长什么样（`Chat` 接口）、消息在线上如何表示（`Message`）、调用方能调什么旋钮（`ChatOptions`），以及实例如何组装（`NewChat` + 三层装饰器）。包内其余 39 个文件（remote_api/anthropic/ollama/sse_reader/prompt_cache 等）与兄弟包 `provider`（27 个供应商适配文件）都是这份契约的实现与元数据。上游入口：`application/service/model.go:619`（生产）与 `handler/initialization.go`（连通性测试）。

## 二、内部结构

**1. 工具调用类型（L15-25、L105-116）**：`Tool`/`FunctionDef`（参数 `json.RawMessage` 原样透传 schema）；`ToolCall`/`FunctionCall`（arguments 为 JSON 字符串），与 OpenAI 函数调用协议一一对应。

**2. `ChatOptions`（L28-52）**：温度/TopP/种子/惩罚/思考开关/工具与并行调用。最讲究的是 L32-35 注释：`MaxTokens` 与 `MaxCompletionTokens` 是同一预算的别名，出站 JSON 按供应商只带其一（gpt-5 系只认新名，见 completion_budget.go）。

**3. `Message`（L79-102）**：四种角色共用；`MultiContent` 支持文本+图片；`ReasoningContent`（L87-91）修真实兼容坑——DeepSeek/MiMo 等 thinking 模式要求多轮回传 assistant 推理内容否则 400，其他供应商忽略未知字段无副作用；`Kind`/`TurnID` 是引擎内部记账（`json:"-"`），`Kind=compaction_summary`（L76）防止压缩摘要被再压缩成"摘要的摘要"。

**4. `Chat` 接口（L119-131）**：仅四方法——`Chat`（非流式）、`ChatStream`（channel）、`GetModelName`/`GetModelID`。

**5. 配置与工厂（L133-204）**：`ChatConfig` 含 `MaxConcurrency`（每模型后台并发帽）、`CustomHeaders`、加密的 `AppID/AppSecret`；`ConfigFromModel`（L154）让生产与测试走**完全相同**的字段映射，避免样板漂移。`NewChat`（L174）按 Source 分流 local→Ollama、remote→Remote，随后 L185-189 依次包装：`wrapChatDebug`（最内）→ `wrapChatLangfuse` → `wrapChatConcurrency`（**最外**，并发槽只圈住真实往返，等待不计入观测计时）。`NewRemoteChat` 里 Anthropic 走独立 Messages 协议单独成类，其余全落 OpenAI 兼容的 `RemoteAPIChat`，差异在构造期由 providerAdapter 解析（L192-194）。

## 三、外部连接

**依赖**：`models/provider`——27 家注册表（`AllProviders()` L71：generic/WeKnoraCloud/阿里/智谱/火山/混元/硅基流动/DeepSeek/MiniMax/Kimi/魔搭/千帆/七牛/OpenAI/Anthropic/Gemini/OpenRouter/LiteLLM/Jina/MiMo/LongCat/LKEAP/GPUStack/NVIDIA/Novita/Azure）；`DetectProvider`（L225）按 BaseURL 域名启发识别，含"litellm 环回保持 generic 因 SSRF 拦截"的细节。**被依赖**：`modelService.GetChatModel` 是全后端唯一实例入口，chat pipeline、Agent 引擎、Wiki 摄取、VLM 都消费 `chat.Chat` 接口而非具体实现。

## 四、数据流：一次非流式模型调用

以 Wiki 摘要为例：① 服务层从 DB 读 `types.Model` → `ConfigFromModel`；② `NewChat`：Provider 名为空则 `DetectProvider(BaseURL)` 兜底 → 非 Anthropic → `NewRemoteAPIChat` 构造期解析该供应商 adapter（thinking 编码、token 字段名）；③ 依次套 debug/langfuse/concurrency 三层壳；④ 调用方执行 `Chat(ctx, messages, opts)`：最外层判断是后台任务则先取每模型信号量（交互聊天不受限），langfuse 记 span，`RemoteAPIChat` 组装 Chat Completions JSON 发 HTTP；⑤ 响应经 debug 壳留档返回 `types.ChatResponse`；流式则由 sse_reader 逐块喂 channel。

## 五、设计决策

- **小接口 + 装饰器链**是精髓：观测、限流、调试全做成实现同一接口的包装器，供应商实现零感知；包装顺序有讲究且写明理由（L187-189），是"顺序即语义"的注释典范。
- **Anthropic 是唯一例外**：Messages 协议与 Chat Completions 不兼容，独立实现而非 adapter 里塞 if——27 家供应商只有 2 个远程实现类，复杂度从供应商数量级降到协议数量级。
- **线上格式与引擎状态分离**：`Kind`/`TurnID`/`PromptCacheKey` 一律 `json:"-"`，注释直说"部分供应商拒绝未知字段"，用序列化标签实现线协议白名单。
- 批判点：`ChatOptions` 已长到 15 个字段；`Message` 同时承载 wire 格式与引擎内部状态，两套变更节奏耦合一个类型。

## 六、新人提示

- **加新供应商不碰本文件**：在 provider 包写适配文件 + Register + DetectProvider 加域名分支即可；只有协议不兼容才值得新建 Chat 实现。
- `Source=local` 只有 Ollama；自部署 vLLM 等走 remote + generic。
- 连通性失败先看包装链：debug 壳默认关、langfuse 未配置时透传，真错误几乎总在最内层 HTTP。
- 多轮报 400 且模型是 thinking 系列，查历史回传是否剥掉了 `ReasoningContent`。
- 延伸：DeepWiki `3.7-event-driven-architecture-and-chat-pipeline.md`（谁在调用它）、`2.4-system-initialization-and-configuration.md`（模型配置）。
