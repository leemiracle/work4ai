# llm-deepseek/src/adapter.ts — DeepSeekAdapter：刻意"只管运输"的传输层

> 原文件：[`packages/llm/llm-deepseek/src/adapter.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/llm/llm-deepseek/src/adapter.ts)（707 行）

## 角色定位

`DeepSeekAdapter` 是 `dsh-llm` 抽象 `LlmAdapter` 的 DeepSeek 实现：用 `fetch` + SSE 对接 DeepSeek（OpenAI 兼容的 chat-completions 端点），把请求翻译过去、把流式响应翻译回 Harness 的 `StreamChunk`。它对自己的定位写在文件注释里并且被严格执行——**transport-only（只管运输）**：连接校验、配置分层、凭据策略全部归属注册插件（`index.ts`），适配器只认"给我什么我运什么"。

这个自我克制是本文件最值得学习的设计：707 行里没有一行策略判断，因此可以脱离 Cordis 上下文独立测试，也可以被任何未来的注册方复用。

## 内部结构

**连接事实的 thunk 注入**：base URL、端点等连接事实不作为构造期常量，而是经一个 **thunk 在每次操作内解析一次**——同一操作的全程看到一致的连接事实，操作之间又能感知变化（配置热更新不需要重建适配器）。

**bearer token 的逐请求解析器**：API 密钥经 per-request resolver 取得，每次请求都可能拿到不同的 token——密钥轮换、多凭据切换对适配器透明。

**请求序列化**（`serialize.ts`）：`serializeRequest` / `serializeRequestWithImages` 把 Harness 请求翻成线格式；图像请求有专门路径，配合**图像卸载**（`offloadRequestImagesWithPolicy`）：图像数据按策略转移到附件存储，请求里只留引用——大负载不撑爆请求体。

**SSE 与翻译**（`sse.ts` / `translate.ts`）：SSE 流解析（处理分块边界、半行拼接）与 chunk 语义翻译（DeepSeek/OpenAI 的 delta 语义 → Harness `StreamChunk`）。

**错误码公民**：`QUOTA_EXCEEDED_CODE`（配额超限）与 `CONTEXT_WINDOW_EXCEEDED_CODE`（上下文窗口超限）是显式常量——上游的重试策略与用户提示据此分流，而不是字符串匹配错误消息。

**时间治理**：`deadline`（总时限）、`idleWatchdog`（流卡死看门狗）、`timeoutOf` 的解析——三种超时各管一段。

**其他**：`attributionHeaders`（归因头）；`file-id.ts`/`file-store.ts` 的文件侧设施；`request-pricing.ts` 的请求计价（与本文件互相引用，图谱可见）。

## 外部连接

上游：实现并注册进 `LlmRuntime`（注册方是本包 `index.ts` 插件——它持有 Config 校验、连接测试与凭据策略）。包内依赖：`file-id.ts`、`file-store.ts`、`request-pricing.ts`、`serialize.ts`、`sse.ts`、`translate.ts`、`types.ts` 七个模块；`index.ts` 与 `request-pricing.ts` 反向引用本文件。语义出口：产出的 `StreamChunk` 流交给 `BlockAssembler` 组装。环境约定：e2e 测试读 `DEEPSEEK_API_KEY` 与可选 `DEEPSEEK_BASE_URL`，无密钥自动跳过——适配器本身不读环境，环境是注册方的事。

计价是包内的另一半：`request-pricing.ts` 基于请求内容算出计价事实（与本文件互相引用），归因头（`attributionHeaders`）让服务器端能识别调用来源，两者配合支撑用量与账单的对账。`file-id.ts`/`file-store.ts` 提供文件侧设施——图像卸载路径引用的附件、以及文件接口涉及的 id 映射都在这里落账。e2e 测试（`test:e2e`）没有 `DEEPSEEK_API_KEY` 时自动跳过，有密钥则打真实端点，适配器的传输正确性靠这条通道持续验证。

## 数据流

请求侧：Harness 消息序列 → `serializeRequest(WithImages)` → 图像按策略卸载进附件存储、请求留引用 → 附 attributionHeaders 与当次解析的 bearer token → `fetch` 发起 SSE 请求。响应侧：SSE 字节流 → `sse.ts` 切分事件 → `translate.ts` 翻成 `StreamChunk` 序列 →（经 idleWatchdog 监视活性）持续产出 → 组装器闭块。失败侧：HTTP/流错误分类 → 配额/上下文窗口超限打专属错误码 → 其余按可重试性归类的 `adapter-failure` 通道上抛 → `resolveRetryPolicy` 决定重试或终止。

## 设计决策

**transport-only 的边界纪律**：适配器不知道"这个密钥该不该用"、"这个 base URL 是否合规"。好处有三：可独立测试（不 mock Cordis）；策略集中在注册插件（一处审查）；换注册方（比如测试环境用自己的凭据层）不动运输代码。

**thunk 每操作一解析**：在"构造期固化"（热更新失灵）与"每次调用重读"（同一操作内不一致）之间取了操作粒度——一次操作一个事实快照，恰好覆盖两种担忧。

**token 逐请求解析**：密钥轮换零成本。这是把"凭据是策略不是配置"落实为 API 形状。

**图像卸载**：多模态请求的体积问题在运输层解决（引用化），上层协议保持干净。

**错误码一等公民**：配额与上下文超限从"错误消息里的字符串"升级为可编程分支——上游重试策略、用户提示、计费归因都挂在常量上。

**三段超时**：总 deadline 防久等、idle watchdog 防流卡死、逐段 timeout 可配——流式调用的三类时间病各有一味药。

## 新人提示

读这个文件前先立一条心法：**别在这里加策略**。如果你想加"密钥校验"、"模型白名单"、"价格上限"，它们的家在注册插件（`index.ts`）或拦截链（`llm-runtime`），硬塞进适配器会破坏它可独立测试的属性。调试顺序建议：先开 e2e（有 `DEEPSEEK_API_KEY` 就能跑真流），观察 SSE 半行拼接与块翻译的边界情况——那是运输层最容易出错的两处。排查"图像没到模型"时查卸载策略与准入两侧，适配器只负责搬。密钥轮换相关的行为测试直接看 per-request resolver 的调用次数。最后，`QUOTA_EXCEEDED_CODE` 与 `CONTEXT_WINDOW_EXCEEDED_CODE` 是你写重试/提示逻辑时唯一应该依赖的标识，永远不要匹配错误文本。补充一个时间治理的读法：deadline 管单次操作的总时长，idleWatchdog 盯流式响应的间隔——两者独立生效，长回答不该撞死看门狗，但挂死的流必须被咬断；调试超时问题先分清是哪一段在叫。
