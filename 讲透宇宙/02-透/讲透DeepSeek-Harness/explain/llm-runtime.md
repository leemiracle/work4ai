# llm/src/index.ts — LlmRuntime：模型调用的服务端与拦截总线

> 原文件：[`packages/llm/llm/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/llm/llm/src/index.ts)（1092 行）

## 角色定位

`LlmRuntime` 是 LLM 能力的服务端：适配器注册表、路由冻结、模型发现，以及一条 **waterfall 可拦截的流式调用 API**。所有 provider（当前是 DeepSeek，经 `llm-deepseek` 包的适配器）从这里进出；agent-loop 的每一次模型请求都经过它的拦截链。它同时是 `dsh-llm` 的包入口，汇出 `BlockAssembler` 等公开面。

把它理解为"模型调用的海关+装配线"最贴切：海关决定请求走哪个适配器（路由），装配线把流式碎片组装成完整消息（BlockAssembler），而 waterfall 拦截链是海关前的检查带——计费、脱敏、重试策略等横切关注点都挂在这里，不侵入主干。

## 内部结构

包入口聚合九个内部模块，各自承担一块可独立测试的关注点：

- **adapter 注册表与抽象 `LlmAdapter`**：provider 实现的接口契约。注册后路由表建立，运行中**路由冻结**——避免调用进行中被新注册扰动。
- **`BlockAssembler`（assembler.ts）**：流式组装的核心。provider 产出流式 chunk， assembler 按**块索引**把它们组装为最终 assistant 消息——累积 partials、闭合块、汇总用量与 replay 状态。这是整个流式路径的正确性关键。
- **`retry-policy.ts` 的 `resolveRetryPolicy`**：把配置解析为重试策略，可重试错误类别由 adapter 失败分类（`adapter-failure.ts`）驱动。
- **`message.ts` 的 `freezeMessage`**：消息冻结——进入历史的东西不可再改，防下游篡改。
- **`api-key.ts` 的 `normalizeApiKey`** 与 `brand.ts` 的品牌化 id：密钥规范化与跨边界 id 纪律。
- **`content.ts` 的 `contentHasImage`/`projectImagesForTextModel`**：图像内容检测与"纯文本模型的图像投影"——图像请求发给文本模型的降级路径显式化。
- **`call-config.ts` 的 `callConfigEquals`**：调用配置相等性，供缓存与重用判断。
- **`error.ts` 的 `HarnessError`**：统一错误层级。

调用 API 是 waterfall 形态：拦截器链上每个监听器**必须调用 `next()`** 委派，不调用即短路整链——这是仓库明文的 Cordis waterfall 语义，文档有专门章节。

## 外部连接

下游实现：`llm-deepseek` 的 `DeepSeekAdapter` 实现 `LlmAdapter` 并注册进来（见下一篇）。上游消费者：agent-loop（每次请求经拦截链调用，`markAgentLoopRequest` 标记来源）；session-controller 的 `modelCatalog`（模型发现投影出可选模型目录）；计费/遥测类插件挂拦截链。图谱确认包入口直接 import 九个内部模块，assembler 又依赖 brand/message/types 三件套——层次干净，无环。

模型发现的下游形状值得一看：session-controller 的 `buildModelCatalog` 把注册表按 provider 分组、附上部署默认值，并把单个 provider 的失败隔离呈现——一个 provider 掉线不会让整个目录变空。`adapter-failure.ts` 的失败分类则是重试策略的输入：可重试类别（如瞬时传输错误）与不可重试类别（如配额超限）在这里分家，`resolveRetryPolicy` 只对前者计数。

## 数据流

调用主线：请求（消息序列+调用配置）→ waterfall 拦截链逐层过（每层可观察、改写、或决定不调 `next()` 而终止）→ 路由到适配器 → provider 流式返回 → `BlockAssembler` 按块索引累积（partials 到齐后闭块）→ 冻结的 assistant 消息 + 用量汇总产出 → 交回调用方。失败路径：adapter 归类失败 → `resolveRetryPolicy` 判定可否重试 → 重试或上抛 `HarnessError`。模型发现路径：各 adapter 报告能力 → 目录构建 → `modelCatalog` 投影。

## 设计决策

**waterfall 而非事件钩子**：拦截器既可观察又可改写还可终止，且顺序明确。计费、脱敏、限流这类"必须挡在调用前面"的关注点，用事件模型表达不了，waterfall 是最小充分结构。强制 `next()` 的纪律换来的是链上行为的可预测性。

**适配器模式 + 路由冻结**：多 provider 扩展点清晰；冻结期保证一次调用内的路由决策不被并发注册改变——避免"同一次请求前后见到不同 provider 视图"的诡异状态。

**消息冻结**：`freezeMessage` 把"历史不可变"从约定升级为机制。会话重放的正确性依赖没有人偷偷改过已落账的消息。

**组装器独立成模块**：流式组装是正确性热点（块乱序、partial 到不齐、用量汇总），单独成模块使其可以被穷举测试，而不必拉起整个 runtime。

**图像投影显式化**：文本模型遇到图像不是隐式丢弃，而是走显式投影函数——降级行为可测试、可审计。

**品牌化 id 与密钥规范化**：模型 id、消息 id 等跨边界标识一律品牌化（`brand.ts`），密钥经 `normalizeApiKey` 统一形态后才进入比较与缓存——两件小事共同保证"相等"这个判断在边界两侧是同一个意思，缓存与去重因此才可靠。

## 新人提示

理解这个包的钥匙是 `BlockAssembler` 的**块索引模型**：先搞清 provider 的 chunk 里块如何编号、partial 如何累积、闭合条件是什么，流式路径的一切怪象（丢块、重复尾部、用量不对）都能对号入座。写拦截器时把"必须 `next()`"贴在显示器上——忘记调用不会报错，只会让整条链静默短路，这是最难排查的一类 bug；仓库文档对此有专门语义说明。加新 provider 的路径是：实现 `LlmAdapter` → 在自己的注册插件里校验配置与凭据 → 注册进 runtime；不要在 runtime 里加 provider 特有分支。判断"该不该在拦截链里做"的标准很简单：如果你需要看到或改写请求/响应，挂链；如果只是听个响，用事件。最后一条心法：消息一旦冻结就不要试图解冻改写——需要新内容就发起新消息，所有"改历史"的冲动都应该被翻译成"追加事件"。
