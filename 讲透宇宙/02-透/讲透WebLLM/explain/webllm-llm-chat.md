# webllm-llm-chat.md — src/llm_chat.ts 精讲：LLMChatPipeline 推理管线

## 角色定位

`llm_chat.ts`（2298 行，全库最重单文件）定义 `LLMChatPipeline`——WebGPU 上的**对话推理心脏**。MLCEngine 的每次 chat/completion 请求最终都落到这里的 `prefillStep()`/`decodeStep()` 循环。它负责：从 tvmjs 虚拟机动态发现可用 kernel 并解析模型 ABI；管理 KV Cache / RNN 状态；执行"grammar 掩码 → logit 处理 → 采样"的完整 token 生产链；处理多模态图像输入与 xgrammar 结构化输出；以及全套逐 token 统计。它与 UI 层完全解耦——不认识 OpenAI 请求对象（那层拆解在 engine.ts），只吃 token 数组与图像 URL。

## 内部结构

**ABI 解析（构造器前半）**：`loadVMFunctionRegistry` 用 try-catch 逐个查询 14 个候选 VM 函数（prefill/batch_prefill/decode/batch_decode/create_tir_paged_kv_cache/create_rnn_state/embed/image_embed/采样五件套等），得到可用性表；再从 `_metadata()` 读出 `kv_state_kind`（kv_cache / rnn_state / hybrid / none）与参数名单、`prefill_chunk_size`。`resolveModelABI` 静态方法把两者组合成 `ResolvedModelABI`：hybrid 强制要求 batch kernel 对 + 两种状态创建函数；kv_cache 与 rnn_state 则在 single/batch kernel 对里择一。这样新模型只要导出对应函数就能被同一套 TS 代码驱动，无需改库。

**状态创建（构造器后半）**：需要 KVCache 时以 `create_tir_paged_kv_cache(maxNumSequence=1, maxTotalSeqLen, prefillChunkSize, pageSize=16, slidingWindow标志)` 建 PagedKVCache；需要 RNN 时以 `create_rnnState(1, maxHistorySize)` 建状态（`max_history_size` 未显式配置时浏览器保守默认 1，防 hybrid 模型过度预分配）。窗口配置互斥校验：`context_window_size` 与 `sliding_window_size` 必须二选一（都设抛 `WindowSizeConfigurationError`，都不设抛 `WindowSizeSpecificationError`）；滑窗还需 `attention_sink_size ≥ 0`。PagedKVCache 的五个形状参数全部用 `makeShapeTuple` 打包传入而非散参，是 TVM PackedFunc 调用的典型风格——初学者容易在这类"一切皆 ShapeTuple/Scalar"的边界上犯类型错误。

**prefillStep 主干**：清逐轮状态（outputIds、频表、统计、LatencyBreakdown 六数组）→ 若 response_format 有 grammar，启动 GrammarMatcher 初始化 **Promise（与 prefill 并行重叠隐藏耗时**；同 schema 命中 `responseFormatCacheKey` 则只 reset 复用）→ conversation 追加消息（`enable_thinking=false` 时预灌空思考块 token）→ `getInputData` 把 prompt 数组 tokenize（图像 URL 原样保留、按配置插 BOI/EOI token）→ `getChunkedPrefillInputData` 按 `prefill_chunk_size` 分块 → 逐块 `embedAndForward` → `device.sync` 后 await grammar Promise → 采样首 token → `processNextToken`。

**decodeStep**：取 outputIds 最后一个 token 单步前向再采样。**processNextToken 四停止条件**：stop token 命中 / stop 字符串出现（`lastIndexOf` 截断输出）/ 超 `max_tokens` / KVCache 写满上下文窗口（finish_reason 分别为 stop/length）。

**embedAndForward（统一前向）**：文本走 `getTokensEmbeddings`（embed kernel），图像走 `getImageEmbeddings`（image_embed kernel，phi3_v 按 336 网格算 resize/crop，Gemma3V 用 `mm_tokens_per_image` 固定值）→ `concatEmbeddings` 拼接 → 对每个活跃状态 `begin_forward` → inputLen>1 调 prefill kernel 否则 decode kernel → `end_forward` → `filledKVCacheLength` 递增校验。

**sampleTokenFromLogits（六步采样链）**：①grammar 约束：`getNextTokenBitmask` 产 Int32Array 掩码上传 GPU，`apply_bitmask_inplace` 屏蔽非法 token；②LogitProcessor：logits 拷到 CPU 执行用户回调再拷回；③logit_bias：`apply_logit_bias_inplace`；④penalties：`apply_penalty_inplace`（吃 `appearedTokensFreq` 频表，三个惩罚系数打包）；⑤采样：`softmax_with_temperature` → `argsort_probs` → `sample_with_top_p`（均匀随机数在 tvmjs 侧，seed 可控），全程 GPU；⑥后处理：`logitProcessor.processSampledToken` 更新状态、`grammarMatcher.acceptToken` 推进语法状态（拒绝即抛错）；logprobs 需求时用 CPU 侧概率分布构造 `ChatCompletionTokenLogprob`。

## 外部连接

依赖 tvmjs（设备/VM/Tensor）、web-tokenizers（encode/decode）、web-xgrammar（TokenizerInfo/GrammarCompiler/GrammarMatcher）、conversation.ts（模板）、support.ts（分块/getTopProbs/图像工具）、config.ts（ChatConfig 与错误）。被 engine.ts 实例化与调用；`tests/llm_chat_pipeline.test.ts` 与 `llm_chat_abi.test.ts` 守护。

## 数据流

一次用户消息进入后：字符串 → conversation 渲染成 prompt 数组 → tokenize 成 token 块（可夹图像 embedding）→ 逐块 prefill 填充 KVCache → logits 过六步采样链 → token 追加进 outputIds 并 decode 回文本 → 循环至停止条件 → `getMessage()` 返回全文。统计沿两条时间轴记录：全程累计（resetChat 清）与 curRound 逐轮（prefillStep 清），供 engine 组装 usage——看懂这对时间轴的分界，就明白了为什么多 choice（n>1）请求的统计是各轮相加而 resetChat(keepStats=true) 能保住历史数字。

## 设计决策

1. **运行时 ABI 探测优于编译期配置**：函数注册表 + metadata 双探测，让同一管线服务 Transformer、Mamba 类混合架构与新 batch kernel，代价是构造器逻辑分叉多。
2. **grammar 初始化与 prefill 并行**：编译 schema 可能耗时百毫秒级，用 Promise 重叠进 GPU prefill，只在采样前 await——还挂了空 catch 防 unhandled rejection。
3. **采样尽量留在 GPU**：除 LogitProcessor（需要用户 JS 回调）外整条链不落 CPU，避免 10 万级词表来回拷贝。
4. **TVM 作用域纪律**：beginScope/endScope 包裹临时对象、detachFromCurrentScope 提升长寿命对象，泄漏即显存流失——改代码时必须同步维护。文件里反复出现的模式是"beginScope 内创建 → detach 出作用域 → attach 到上层作用域"，比如 embedAndForward 里对 logits 的处理：先 detach 保证 endScope 不销毁它，再 attach 交给调用方管理。
5. **`forwardTokensAndSample` 低级逃生口**：绕过 conversation 直灌 token，供自定义生成循环（代价：用户自理 KV 状态）。

## 新人提示

不要线性通读 2298 行。推荐顺序：构造器的 ABI 解析段（loadVMFunctionRegistry→resolveModelABI）→ prefillStep/decodeStep/processNextToken 主干 → sampleTokenFromLogits → 最后再看 VLM 几何与统计。调试用 `pipeline.evaluate()` 内置冒烟测试（跑 "The capital of Canada is"）。改采样逻辑后必跑 `llm_chat_pipeline.test.ts`；踩 TVM 对象生命周期问题先怀疑 scope 纪律。前置阅读：`webllm-engine.md`（谁在调用它）。
