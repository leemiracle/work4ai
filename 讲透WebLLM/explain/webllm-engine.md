# webllm-engine.md — src/engine.ts 精讲：MLCEngine 门面

## 角色定位

`engine.ts`（1432 行）是 WebLLM 的**门面层**：`MLCEngine` 类实现 `MLCEngineInterface`（types.ts 定义），把库的全部能力收敛成三个 OpenAI 风格命名空间——`chat`（`engine.chat.completions.create()`）、`completions`（旧版文本补全）、`embeddings`（句向量）——加上模型生命周期管理（reload/unload）、进度回调、logit processor 注册与生成中断。它是全库扇出最高的枢纽（依赖 15 个模块），但自己不做任何张量计算：真正干活的是它路由到的 `LLMChatPipeline` / `EmbeddingPipeline`。文件同时导出异步工厂 `CreateMLCEngine(modelId, engineConfig?, chatOpts?)`——`new MLCEngine()` 再 `await engine.reload(...)` 的等价 sugar，是绝大多数使用者的入口。

## 内部结构

**三组 API 实例**（构造器里 `new API.Chat(this)` 等）：Chat/Completions/Embeddings 门面类来自 openai_api_protocols，只做转发。

**四个状态 Map**（多模型服务的核心数据结构）：
- `loadedModelIdToPipeline: Map<string, LLMChatPipeline | EmbeddingPipeline>`——每个已加载模型的管线；
- `loadedModelIdToChatConfig` / `loadedModelIdToModelType`——配套配置与类型；
- `loadedModelIdToLock: Map<string, CustomLock>`——每模型一把异步互斥锁，保证同一模型串行处理请求（不同模型可并行）。

**信号与标志**：`interruptSignal`（中断生成）、`deviceLostIsError`（区分"reload 引起的设备销毁"与"真 OOM"）、`reloadController: AbortController`（可中断的模型加载）。

**reload 语义**：`reload()` 是"全换"而非"增量"——先 `unload()` 清空全部，再把输入数组化、校验唯一性（重复 model_id 抛 `ReloadModelIdNotUniqueError`）、逐个顺序加载，单个 AbortController 让一次 abort 能停掉整批。这个设计有意牺牲了灵活性换取状态简单：多模型并存时每个模型占着数百 MB 显存，"往已满的引擎里再加一个"的失败模式远比"全换"复杂，把显存决策留给调用方反而更可控。加载中途调用 `unload()` 会触发 AbortError，被 catch 成警告而非崩溃。

**reloadInternal 十步链**（模型加载主流程）：①`findModelRecord` 查目录 → ②configCache 拉 `mlc-chat-config.json`（可 SRI 校验）→ ③三层合并 `{...configJson, ...modelRecord.overrides, ...chatOpts}` → ④拉 wasm 模型库（localhost 不缓存）→ ⑤`tvmjs.instantiate` + polyfill WASI → ⑥`detectGPUDevice`（无 WebGPU 抛错；`required_features` 如 shader-f16 逐一检查）→ ⑦挂 `device.lost` 监听（OOM 自动 unload）→ ⑧`asyncLoadTokenizer` + `fetchTensorCache` 拉权重 → ⑨按 `model_type` 实例化 LLMChatPipeline 或 EmbeddingPipeline，`asyncLoadWebGPUPipelines` 装载 WebGPU shader → ⑩注册进 Map，进度回调报到 1。

**生成主干**：`_generate()` = prefill 一次 + `while (!pipeline.stopped()) decode()`；`asyncGenerate()` 是它的 async generator 版，供流式请求复用。

## 外部连接

- 依赖：`config.ts`（模型目录/校验）、`llm_chat.ts` 与 `embedding.ts`（管线）、`openai_api_protocols`（类型与请求校验 `API.postInitAndCheckFieldsXxx`）、`conversation.ts`（多轮对话比较）、`support.ts`（CustomLock/getModelIdToUse/getToolCallFromOutputMessage）、`cache_util.ts`、`integrity.ts`、`error.ts`（12 个错误类）。
- 被依赖：`web_worker.ts` 的 Handler 在 worker 线程内 `new MLCEngine()` 包装它；`index.ts` 导出它；`tests/engine_integration.test.ts` 端到端守护。它对 tvmjs 的依赖全部经由两个 Pipeline 间接发生，engine.ts 自己 import tvmjs 只为两处 GPU 探测（`detectGPUDevice`）——这让它能专注编排而不过问张量细节。

## 数据流

以一次非流式 `chatCompletion(request)` 为例：`getLLMStates()`（按 request.model 或唯一已加载模型选出三元组，类型不符抛 `IncorrectPipelineLoadedError`）→ 协议校验 → 组装 `GenerationConfig` → `lock.acquire()`（排队等前序请求）→ 循环 n 次 `_generate`（每次 prefill+decode 到停止）→ 组装 choices（function calling 时用 `getToolCallFromOutputMessage` 解析 tool_calls）→ 统计 usage（`usage.extra` 附 prefill/decode tokens per sec、time_to_first_token 等性能指标）→ `finally lock.release()`。流式路径返回 `asyncGenerate` 生成器：每个 decode 步 yield 一个 chunk，尾随 U+FFFD 字符数非 4 的倍数时推迟输出（等完整 emoji），最后一个 chunk 带 finish_reason，`stream_options.include_usage` 时再补一个 usage chunk。

## 设计决策

1. **API 无状态、内部有优化**：每次请求都完整传入 messages，但 prefill 前用 `compareConversationObject` 深比较新旧对话——一致即复用 KV Cache 只灌新 tokens。用户拿到无状态语义，性能却接近有状态。
2. **锁的粒度是模型而非引擎**：多模型各自串行、彼此并行；`asyncGenerate` 里细粒度 try-catch 保证异常路径也释放锁。
3. **device.lost 用标志位消歧**：`unload()` 主动销毁设备时置 `deviceLostIsError=false`，避免误报 OOM；`reloadInternal` 结束时若曾在加载中丢设备，同步抛 `DeviceLostError`（把异步错误变成可捕获的同步点）。多数设备丢失发生在 reload 阶段——因为权重与 KVCache 的显存在那时一次性分配——所以源码注释明确说这个标志主要用于让 reload 的错误处理同步化。
4. **seed 请求级隔离**：请求结束后 `setSeed(Date.now())` 重置，避免影响后续请求。
5. **中断是协作式**：`interruptGenerate()` 只置 flag，由生成循环在每步检查触发 `triggerStop()`（finish_reason 记为 abort）。

## 新人提示

读这个文件先抓两条线：reload 生命周期（reload→reloadInternal→unload）与一次请求的生命周期（chatCompletion→lock→_generate/asyncGenerate→prefill/decode）。四个 Map 是理解多模型行为的钥匙。`runtimeStatsText()` 已标记废弃——统计请走 `ChatCompletion.usage`。设备丢失多半是显存不够，官方建议是换小模型或缩短上下文重试。配套精读：`webllm-llm-chat.md`（它路由到的管线）与 `webllm-web-worker.md`（它最常见的外壳）。改引擎逻辑后先跑 engine_integration 与 web_worker_handler 两个测试文件，它们覆盖了本文件绝大多数分支的行为回归。
