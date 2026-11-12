# webllm-config.md — src/config.ts 精讲：模型目录与基础类型

## 角色定位

`config.ts`（2607 行）是 WebLLM 的**基础类型底座 + 预编译模型注册表**，全库被引用最多的模块（fan-in 15）。它回答两个问题：①"一个模型/一次生成需要哪些配置参数"——用一组 interface 定义；②"当前 npm 版本能跑哪些模型"——用 `prebuiltAppConfig` 约 2250 行、167 个 `model_id` 的目录回答。`MLCEngineConfig` / `AppConfig` 也在此定义，决定缓存后端与进度回调等引擎级行为。任何模块要理解"配置从哪来、被谁覆盖"，起点都在这里。

## 内部结构

文件天然分三段：**前 330 行接口与校验**、**337-358 行版本常量与白名单**、**358 行起模型目录数据**。

**对话模板 `ConvTemplateConfig`**：system_template/system_message、roles 到模板字符串的映射、seps 分隔符、stop_str/stop_token_ids、可选 system_prefix_token_ids（可直灌 KV 的前缀 token）。配合 `MessagePlaceholders` 枚举（`{user_message}` 等）支撑 conversation.ts 的渲染。

**`ChatConfig`**：模型 `mlc-chat-config.json` 的运行时表示，字段按生效范围分层——影响整场对话的（tokenizer_files/vocab_size/conv_template、KVCache 三参数 context_window_size/sliding_window_size/attention_sink_size、RNN 的 max_history_size）与可被逐请求覆盖的采样参数（repetition_penalty/frequency_penalty/presence_penalty/top_p/temperature）；`model_config` 携带视觉模型的 `mm_tokens_per_image`、BOI/EOI token 等模型特有参数。

**`GenerationConfig`**：单次生成的覆盖项，三类来源标注清晰——MLC 特有（repetition_penalty/ignore_eos）、MLC 与 OpenAI 共有（top_p/temperature）、仅 OpenAI（max_tokens/penalties/stop/n/logit_bias/logprobs/response_format 及 extra_body 的 enable_thinking/enable_latency_breakdown）。`postInitAndCheckGenerationConfigValues` 做后置校验与补默认：范围检查（penalty ±2、top_p (0,1]、logit_bias ±100、top_logprobs 0-5）、frequency 与 presence 只设其一时另一方补 0、logprobs 未配 top_logprobs 时补 0、键必须可解析为整数。

**`ModelRecord`**（目录条目 schema）：`model`（HF 权重 URL，四种合法格式：`{USER}/{MODEL}`、带尾斜杠、`/resolve/{BRANCH}` 两种）、`model_id`（使用者引用名）、`model_lib`（wasm 库 URL）、`overrides`（部分 ChatConfig 覆盖，常用缩 context_window_size 出 1k 版）、`vram_required_MB`（选型硬指标）、`low_resource_required`（移动端可用）、`buffer_size_required_bytes`、`required_features`（如 shader-f16）、`model_type`（LLM/embedding/VLM）、`integrity`（SRI 哈希，接 integrity.ts）。

**`AppConfig`**：`model_list` + `cacheBackend`（cache/indexeddb/cross-origin/opfs 四选一，默认 cache 且测试最充分）+ `opfsAccessMode`（async/sync/auto）。`getCacheBackend` 做安全回退。`MLCEngineConfig` 再包一层运行时选项（appConfig/initProgressCallback/logitProcessorRegistry/logLevel）。

**版本与白名单**：`modelVersion = "v0_2_84/base"` 与 `modelLibURLPrefix`（raw.githubusercontent.com/mlc-ai/binary-mlc-llm-libs/main/web-llm-models/）拼出 wasm 库地址——**这是 npm 版本与模型库兼容性的唯一事实来源**，npm 升级不一定动模型版本。`functionCallingModelIds` 是 function calling 的模型白名单（Hermes-2-Pro/3 系五个），协议层硬校验。

**`prebuiltAppConfig`**：167 条 ModelRecord，覆盖 Llama-3.2（1B/3B 全量化档）、Llama-3.1-8B、DeepSeek-R1-Distill、Hermes 系、Phi-3.5/Phi-4-mini（含 vision）、Mistral、Qwen 等；同名模型提供 q4f16_1/q4f32_1/q0f16/q0f32 多档量化与 `-1k` 短上下文变体。量化命名规则值得记住：`q4f16_1` 表示 4 比特权重、16 位浮点激活、分组量化的组数为 1——档位越低显存越省但精度越损，`-1k` 后缀则是用 `overrides.context_window_size` 把上下文压到 1024 换取更小的 KVCache 预分配，本质是同一份权重的不同运行配置而非重新编译。

## 外部连接

被 engine.ts（reload 查目录、读采样默认值）、llm_chat.ts（ChatConfig 字段）、协议层（functionCallingModelIds/MessagePlaceholders/ModelType）、cache_util.ts、conversation.ts、utils.ts（深比较）、index.ts（公开导出 12 个符号）全员依赖；它自己只依赖 error.ts/integrity.ts/types.ts/openai 协议的 ResponseFormat 类型（注意这点反向依赖是刻意的：ResponseFormat 属生成配置）。

## 数据流

引擎 reload 时：`modelId` → `findModelRecord`（support.ts，先查自定义 appConfig 再抛 `ModelNotFoundError`）→ 取 `model_lib`/`model` URL → 下载 `mlc-chat-config.json` 后与 `modelRecord.overrides`、调用方 `chatOpts` 三层浅合并成运行时 ChatConfig（右侧优先级高）。请求时：OpenAI 请求字段拆进 GenerationConfig，与 ChatConfig 采样默认值在 `sampleTokenFromLogits` 里按"有值才覆盖"合并。

## 设计决策

1. **目录即代码**：模型注册表用 TS 字面量而非 JSON，享受类型检查与 `modelLibURLPrefix` 拼接，代价是文件膨胀到 2607 行（数据占 86%）。
2. **三层配置合并链**：远端 json → 目录 overrides → 用户 chatOpts，逐层收紧，让"同一权重跑不同上下文长度"（-1k 变体）零成本。合并是浅展开（`{...a, ...b, ...c}`），因此嵌套对象（如 conv_config）的覆盖是整体替换而非逐字段合并——自定义深层配置时要完整给出整棵子对象，这是新人最常踩的坑之一。
3. **显式能力声明**：VRAM/feature/buffer 门槛全在条目里，UI 可在加载前预判可行性（配套 utils/vram_requirements 工具页）。
4. **校验集中在后置函数**而非 setter：一次请求只校验一次，错误信息带字段名与合法区间（接 error.ts 的 ConfigValueError 族）。
5. **量化档位命名自解释**：q4f16_1 = 4bit 权重 + f16 激活，目录直接可比 VRAM 差异。

## 新人提示

把 2607 行当两个文件读：前 358 行精读，后面当数据库 grep（`grep -n 'model_id' src/config.ts`）。想加自定义模型：不碰这个文件，构造 `AppConfig.model_list` 传给 `CreateMLCEngine` 即可（含自编译 wasm 库与 SRI）。踩"模型能下载但跑不起来"先查 `required_features` 与 `modelVersion` 是否匹配。选型看 `vram_required_MB` 与 `getMaxStorageBufferBindingSize()` 的关系。配套精读：`webllm-engine.md`（谁消费这些配置）。改本文件后跑 `generation_config.test.ts`（校验函数回归）即可，目录数据无专属测试——所以动目录时对照 `utils/vram_requirements` 工具页人工核对 VRAM 数字的量级。
