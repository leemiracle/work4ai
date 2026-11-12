# WebLLM 新人上手指南（ONBOARDING）

> 基于知识图谱（395 节点 / 574 边 / 11 层 / 15 步导览，commit 56d318c）与源码精读生成。
> 配套：`../deepwiki/`（25 页官方文档镜像）、`../explain/`（5 篇核心文件精讲）。

## 1. 项目总览

WebLLM（`@mlc-ai/web-llm`，当前 0.2.84）回答一个问题：**大语言模型能不能不依赖服务器，直接跑在用户的浏览器里？** 答案是能——它是一个完全运行在浏览器内的 LLM 推理引擎，基于 WebGPU 硬件加速与 Apache TVM 的 MLC 技术栈，把模型编译成 WebAssembly + WebGPU kernel 在本地执行。

它解决三个痛点：

1. **免服务器本地推理**：模型权重从 Hugging Face 拉取后缓存在浏览器 Cache API（或 IndexedDB/OPFS）里，第二次加载零下载；推理全部发生在用户 GPU 上，开发者不需要付推理账单。
2. **隐私**：对话内容不出本机——数据流終点是用户自己的 WebGPU 设备，不是云端。
3. **零成本可扩展**：API 表面完全兼容 OpenAI（chat completions / legacy completions / embeddings 三组），已有 OpenAI 应用几乎零改动迁移。

代价是**环境约束**：需要浏览器支持 WebGPU（Chrome/Edge 113+），部分模型还需要 `shader-f16` 特性；显存上限受 `maxStorageBufferBindingSize` 限制（默认阈值 1GB）。模型必须先用 MLC-LLM 工具链预编译成 wasm 库 + 量化权重，本库自带 167 个预编译模型的目录（`prebuiltAppConfig`）。

技术栈定位：TypeScript 实现，唯一运行时依赖 `loglevel`；推理内核来自 `@mlc-ai/web-runtime`（tvmjs），分词来自 `@mlc-ai/web-tokenizers`，结构化输出约束来自 `@mlc-ai/web-xgrammar`。

一次典型使用的完整心智模型：页面加载后调用 `CreateWebWorkerMLCEngine(worker, "Llama-3.2-1B-Instruct-q4f16_1-MLC")`，引擎从远端拉取 mlc-chat-config.json、wasm 模型库与量化权重（首次约数百 MB 到数 GB，之后走缓存秒开），期间通过 initProgressCallback 持续上报进度；加载完成后，用户每发一条消息，就是一次 OpenAI 风格请求——引擎判定是否为多轮对话（决定 KV Cache 复用与否）、渲染对话模板、分块 prefill、逐 token decode 与采样，流式地把增量文本推回 UI。理解了这条链路，后面所有模块都能对号入座。

## 2. 架构分层说明

知识图谱将全仓划分为 11 层，自上而下如下（ASCII 图中的编号对应层名）：

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⑩文档官网层  README/docs(Sphinx)/site(Jekyll)                        │
│ ⑨示例应用层  examples/ 25 组可运行示例 + chrome-extension ×2          │
├─────────────────────────────────────────────────────────────────────┤
│ ⑦Worker通信层  web_worker.ts / service_worker.ts /                   │
│                extension_service_worker.ts / message.ts(19种请求)    │
├─────────────────────────────────────────────────────────────────────┤
│ ①核心推理引擎层                                                     │
│   MLCEngine(engine.ts) ──门面──▶ LLMChatPipeline(llm_chat.ts)       │
│        │                            EmbeddingPipeline(embedding.ts) │
│        │                            Conversation(conversation.ts)    │
│   OpenAI协议层(②) chat/completion/embedding 三组类型+校验            │
├─────────────────────────────────────────────────────────────────────┤
│ ③配置基础层  config.ts(模型目录2607行) / error.ts(69个错误类)         │
│ ⑤缓存完整性层 cache_util.ts(三类CacheScope) / integrity.ts(SRI)      │
│ ⑥工具函数层  support.ts(CustomLock/分块prefill) / utils.ts(深比较)   │
├─────────────────────────────────────────────────────────────────────┤
│ ④测试层(Jest×18)          ⑪构建CI层(rollup+5条workflow)             │
└─────────────────────────────────────────────────────────────────────┘
                    ▼ 底层（不在本仓库，npm 依赖）
        tvmjs WebGPU 虚拟机 / web-tokenizers / web-xgrammar
```

各层职责：

| # | 层 | 节点数 | 职责 |
|---|---|---|---|
| 1 | core-engine 核心推理引擎 | 6 | MLCEngine 门面 + LLMChatPipeline 推理管线 + EmbeddingPipeline + Conversation 模板 + types.ts 契约 + index.ts barrel |
| 2 | openai-protocols OpenAI 兼容协议 | 4 | chat_completion / completion / embedding 三组请求响应类型与字段校验 |
| 3 | config-registry 配置与基础类型 | 2 | config.ts 核心接口 + 2200 行模型目录（全库 fan-in 最高）；error.ts 69 个错误类 |
| 4 | worker-communication Worker 通信 | 4 | 三种运行时形态（Web Worker / Service Worker / MV3 扩展）+ message.ts 消息协议 |
| 5 | cache-integrity 缓存与完整性 | 2 | 三类 CacheScope 缓存管理；Web Crypto SRI 校验 |
| 6 | utility 工具函数 | 2 | 采样辅助 / Hermes function calling / 分块 prefill / CustomLock；深比较 |
| 7 | test 测试 | 22 | 18 个 Jest 文件覆盖每个模块 |
| 8 | chrome-extension 扩展示例 | 18 | MV2/MV3 两组完整扩展示例 |
| 9 | examples 示例应用 | 131 | 25 组特性示例（学习每个特性的最短路径） |
| 10 | documentation 文档官网 | 22 | README/CONTRIBUTING/SECURITY + Sphinx 文档站 + Jekyll 官网 |
| 11 | build-ci 构建工程 | 23 | rollup 构建 + 5 条 GitHub Actions + 部署脚本 |

依赖方向上，`config.ts`、`support.ts`、`error.ts` 是被依赖最多的底座（fan-in 15/15/14）；`engine.ts` 依赖最多（fan-out 15），是枢纽。

## 3. 核心模块

### MLCEngine（src/engine.ts，1432 行）——门面
实现 `MLCEngineInterface`，对外暴露 `chat` / `completions` / `embeddings` 三个 OpenAI 风格命名空间。内部用 4 个 Map 维护多模型状态：`loadedModelIdToPipeline`（模型→管线）、`...ChatConfig`、`...ModelType`、`...Lock`（每模型一把 `CustomLock`，保证同一模型串行处理请求）。`reload()` 语义是"先全部卸载再顺序加载新列表"，`reloadInternal()` 完成从模型目录查记录→拉 config→拉 wasm→探测 GPU→拉权重→实例化管线的完整链路。设备丢失（多为 OOM）通过 `device.lost` Promise 监听并触发自动 unload。

### LLMChatPipeline（src/llm_chat.ts，2298 行）——推理心脏
封装 tvmjs 虚拟机上的自回归循环。构造时动态查询 VM 函数注册表，按模型 metadata 的 `kv_state_kind`（kv_cache / rnn_state / hybrid）与可用 kernel（single/batch）解析出 `ResolvedModelABI`，据此创建 PagedKVCache 或 RNN 状态。`prefillStep`/`decodeStep` 驱动生成，`sampleTokenFromLogits` 实现完整的采样链（grammar bitmask → logitProcessor → logit_bias → penalties → softmax/top-p 采样，除 logitProcessor 外全在 GPU 上）。

### config.ts（2607 行）——模型目录与基础类型
前 330 行定义 `ConvTemplateConfig`/`ChatConfig`/`GenerationConfig`/`ModelRecord`/`AppConfig` 等核心接口与采样参数校验；第 358 行起是 `prebuiltAppConfig`：约 2250 行、167 个 `model_id` 的预编译模型表（Llama-3.2/3.1、DeepSeek-R1-Distill、Hermes、Phi-3.5/4-mini、Mistral、Qwen 等），每条记录含 HF 权重 URL、wasm 库 URL、VRAM 需求、`overrides`、可选 SRI 哈希。它声明了"当前 npm 版本兼容哪些模型库"（`modelVersion = "v0_2_84/base"`），是全库唯一事实来源。

### OpenAI 协议四件套（src/openai_api_protocols/）
`chat_completion.ts`（1228 行）复刻 openai-node 的类型表面并加 188 行 `postInitAndCheckFields` 校验（消息合法性、VLM 图像限制、function calling 模型白名单、response_format 交叉校验、Hermes 硬编码注入）；`completion.ts`（381 行）旧版文本补全；`embedding.ts`（198 行）句向量协议（不支持 dimensions/user/base64）；`index.ts` barrel 统一导出 43 个符号。

### Worker 三态通信（web/service/extension）
`web_worker.ts`（844 行）定义双端：worker 线程内 `WebWorkerMLCEngineHandler` 包装 MLCEngine 并按 19 种消息 kind 分发；主线程 `WebWorkerMLCEngine` 用 uuid + pendingPromise 实现 RPC 代理，接口与 MLCEngine 完全一致。`service_worker.ts` 把引擎搬进 Service Worker 供多标签页共享；`extension_service_worker.ts` 继承后者，用 `chrome.runtime.connect` 端口 + 心跳对抗 MV3 回收。

### 缓存 + SRI
`cache_util.ts` 管理 `webllm/model`（权重+分词器）、`webllm/config`（mlc-chat-config.json）、`webllm/wasm`（模型库）三类 CacheScope，提供级联删除；`integrity.ts` 用 Web Crypto 对下载制品算 SHA-256/384/512 并与 SRI 哈希比对，`onFailure` 可选 error（抛 IntegrityError）或 warn。

## 4. 关键概念（14 个）

1. **WebGPU 设备管理**：`tvmjs.detectGPUDevice()` 探测设备与特性（`shader-f16` 等由 `ModelRecord.required_features` 声明）；`device.lost` Promise 全生命周期监听，OOM 即自动 unload；`maxStorageBufferBindingSize` 决定能跑多大的模型。
2. **prefill / decode 两阶段**：自回归生成的两个阶段。prefill 一次性吃入整段 prompt（分块进行，每块 ≤ `prefill_chunk_size`），产出第一个 token；decode 每步只吃上一个 token、产出一个 token。两者走不同的 VM kernel（`prefill`/`decode` 或 batch 版）。
3. **KVCache 与 PagedKVCache**：注意力缓存，避免每步重算历史。通过 `create_tir_paged_kv_cache` 创建（page_size=16，max_num_sequence=1），`begin_forward`/`end_forward` 包裹每次前向。
4. **RNN 状态与 hybrid ABI**：新式混合架构（如 Mamba 类）用 `kv_state_kind` 声明 `rnn_state` 或 `hybrid`（KV+RNN 双状态），管线构造时按 ABI 解析结果选择 kernel 与状态组合；`max_history_size` 浏览器默认保守取 1。
5. **多轮对话 KV 复用**：`prefill()` 用 `compareConversationObject` 深比较新旧对话，一致则只 prefill 新增 tokens、复用 KV Cache；不一致则 `resetChat()` 全部重来。这是"API 无状态、内部有优化"的关键设计——用户负责维护完整消息历史，库负责识别前缀并省掉重复计算，第二轮起的首 token 延迟因此大幅下降。
6. **worker RPC 模式**：主线程把请求打包成 `{kind, uuid, content}` postMessage 给 worker；worker 处理后回 `{kind: "return"|"throw", uuid, content}`；uuid 关联 pendingPromise 完成异步桥接。流式生成用三段式：`StreamInit`（建 generator）→ N 次 `NextChunk`（每次 next() 一个 chunk）→ 结束返回 void。
7. **深比较参数 reload（reloadIfUnmatched）**：每个请求都携带期望的 `modelId/chatOpts`，handler 用 `areArraysEqual` 与实际状态比对；不匹配（如 service worker 被杀后复活）自动重新 reload，保证前端期望与后端状态最终一致。
8. **CacheScope 三类**：`webllm/model` / `webllm/config` / `webllm/wasm`，后端可选 Cache API（默认、测试最充分）/ IndexedDB / cross-origin / OPFS（`AppConfig.cacheBackend` + `opfsAccessMode`）。
9. **SRI 完整性**：`ModelRecord.integrity` 携带 `sha256-BASE64` 格式哈希，对 config/wasm/tokenizer 逐制品校验，防权重投毒。
10. **采样链**：每 token 的处理顺序为 grammar bitmask（GPU）→ LogitProcessor（CPU 回调，有状态）→ logit_bias（GPU）→ penalties（GPU，依赖 `appearedTokensFreq` 频表）→ softmax+argsort+top-p 采样（GPU）。seed 请求级生效，请求结束重置。
11. **结构化输出（xgrammar）**：`response_format` 支持 `json_object`（可带 schema）/`grammar`（EBNF）/`structural_tag` 四形态；GrammarMatcher 产出 token 位掩码在采样前屏蔽非法 token，matcher 初始化与 prompt prefill 并行重叠以隐藏开销，同 schema 复用只 reset。
12. **logit processor**：用户注册的有状态回调（`processLogits`/`processSampledToken`/`resetState`），在 GPU 采样前于 CPU 侧改写 logits；worker 模式下因无法跨线程传递被忽略。
13. **模型预编译制品（wasm + bc）**：每个模型家族对应一个 wasm 模型库（TVM Relax 虚拟机字节码 + WebGPU shader），权重以量化 NDArray 从 HF 拉取；没有 wasm 库的模型跑不了（`MissingModelWasmError`）。
14. **多模型服务**：一个引擎可同时加载多个模型（reload 传数组，逐个顺序加载，每模型独立管线+锁）；请求时按 `request.model` 或唯一已加载模型路由（`getModelIdToUse`）。

## 5. 推荐学习路径（15 步导览改写）

用法建议：前三步建立全景，第 4-7 步是核心必修（建议配合 `../explain/` 对应精读对照源码），第 8-12 步按需选读，第 13-15 步在动手改代码前过一遍。每步的自检问题答不上来就回到该步文件重读——本表的粒度设计成"一步一个可独立验证的理解点"。

| 步 | 看什么 | 理解什么 | 自检问题 |
|---|---|---|---|
| 1 | `README.md` | 项目定位：WebGPU + TVM/MLC + OpenAI 兼容 API + 浏览器 Cache | WebLLM 的三个卖点是什么？需要什么浏览器条件？ |
| 2 | `src/index.ts` | 库的公共表面：41 个符号 + 协议全量 re-export | 使用者能拿到哪几类东西（引擎/worker/协议/缓存/配置）？ |
| 3 | `src/engine.ts` + `src/types.ts` | MLCEngine 门面：三组 API、4 个状态 Map、reload/unload 语义 | reload 是"增量加模型"还是"全换"？锁的粒度是什么？ |
| 4 | `src/llm_chat.ts` | 推理管线：ABI 解析、prefill/decode 循环、采样链 | kv_state_kind 有哪几种？hybrid 需要哪些函数？ |
| 5 | `src/conversation.ts` + `src/embedding.ts` | 对话模板渲染成 prompt 数组；第二条管线产句向量 | 多模态 prompt 数组长什么样？ |
| 6 | `src/config.ts` + `src/error.ts` | 基础类型底座 + 2200 行模型目录 + 69 个错误类 | ModelRecord 有哪些字段？VRAM/feature 门槛在哪声明？ |
| 7 | `src/openai_api_protocols/` | 协议层：类型从 openai-node 移植 + postInit 校验 | 哪些 OpenAI 字段不支持？Hermes function calling 如何硬编码注入？ |
| 8 | `src/web_worker.ts` + `src/message.ts` | RPC 双端：19 种请求 kind、uuid 桥接、流式三段式 | 流式生成为什么要 StreamInit + NextChunk 两类消息？ |
| 9 | `src/service_worker.ts` | Service Worker 版：多页面共享引擎与心跳 | reloadIfUnmatched 解决什么问题？ |
| 10 | `src/extension_service_worker.ts` | MV3 扩展适配：端口通信 + setInterval 保活 | 为什么 MV3 需要心跳而 Web Worker 不需要？ |
| 11 | `src/cache_util.ts` + `src/integrity.ts` | 三类 CacheScope + SRI 校验链 | 删除一个模型要清几处缓存？ |
| 12 | `src/support.ts` + `src/utils.ts` | 分块 prefill、CustomLock、Hermes schema、深比较 | getChunkedPrefillInputData 为什么需要 getEmbedSize 回调？ |
| 13 | `tests/`（18 个文件） | 每模块的守护网：engine_integration 端到端、协议校验、ABI 测试 | 改了采样逻辑该跑哪些测试？ |
| 14 | `examples/`（25 组） | 特性最短路径：get-started → simple-chat-ts → function-calling/json-schema/vision | 想演示 logit processor 该抄哪个示例？ |
| 15 | `rollup.config.js` + `.github/workflows/` + `scripts/` | 工程链：构建产物清洗（cleanup-index-js.sh）、5 条 CI、站点部署 | 为什么产物要洗掉 Node 专属代码？ |

## 6. 文件地图（按层速查）

**① 核心引擎层**
- `src/engine.ts` — MLCEngine 门面 + CreateMLCEngine 工厂 + _generate/asyncGenerate/prefill/decode
- `src/llm_chat.ts` — LLMChatPipeline：ABI 解析 / prefill / decode / 采样链 / xgrammar / VLM 图像
- `src/embedding.ts` — EmbeddingPipeline：批量 prefill 产句向量 + 统计
- `src/conversation.ts` — Conversation 模板类 + 多轮比较 + 请求转换
- `src/types.ts` — InitProgressReport / LogitProcessor / MLCEngineInterface / LatencyBreakdown
- `src/index.ts` — 公共 API barrel（rollup 入口）

**② OpenAI 协议层**
- `src/openai_api_protocols/chat_completion.ts` — Chat/Completions 门面 + 请求响应类型 + 188 行校验
- `src/openai_api_protocols/completion.ts` — 旧版文本补全协议
- `src/openai_api_protocols/embedding.ts` — 句向量协议 + 不支持字段清单
- `src/openai_api_protocols/index.ts` — 协议 barrel（43 导出）

**③ 配置基础层**
- `src/config.ts` — 核心接口 + 校验函数 + prebuiltAppConfig（167 模型）+ functionCallingModelIds
- `src/error.ts` — 69 个语义化错误类（配置/WebGPU/消息/工具调用/上下文/embedding/完整性）

**④ Worker 通信层**
- `src/web_worker.ts` — Handler（worker 侧）+ Engine（主线程代理）+ 工厂
- `src/service_worker.ts` — Service Worker 双端（clientRegistry 定向回复）
- `src/extension_service_worker.ts` — MV3 扩展适配（继承 web_worker 系）
- `src/message.ts` — 19 种 RequestKind + Params + WorkerResponse 信封

**⑤ 缓存完整性层**
- `src/cache_util.ts` — CacheScope 三类 / 级联删除 / asyncLoadTokenizer
- `src/integrity.ts` — SRI 解析 + verifyIntegrity + isValidSRI

**⑥ 工具函数层**
- `src/support.ts` — getTopProbs / 分块 prefill / CustomLock / Hermes schema / 图像转换
- `src/utils.ts` — 数组/ModelRecord/AppConfig/ChatOptions 深比较

**⑦ 测试层**（`tests/`，18 个文件）
- `engine_integration` 端到端 / `llm_chat_pipeline` + `llm_chat_abi` 内核 / `openai_chat_completion` + `openai_completion` + `openai_embeddings` 协议三件套 / `cache_util` / `integrity` / `web_worker_handler` / `service_worker` / `extension_service_worker` / `function_calling` / `multi_round_chat` / `generation_config` / `conversation` / `embedding_stats` / `util`。命名与 src 模块一一对应，找某模块的用法样例或回归范围，先看同名测试。

**⑨ 示例层**（`examples/`，25 组）
- `get-started` 最小入门 / `simple-chat-ts` 完整 worker 聊天 UI / `function-calling` / `json-schema` / `logit-processor` / `vision-model` / `multi-round-chat` / `nextjs-*` / `chrome-extension` ×2 / `vram-requirements`（`utils/` 下独立工具页）

**⑩⑪ 文档与工程**
- `README.md`（27 节）/ `CONTRIBUTING.md`（14 节）/ `SECURITY.md` / `docs/`（Sphinx）/ `site/`（Jekyll）
- `rollup.config.js` / `cleanup-index-js.sh`（产物去 Node 化）/ `package.json`（唯一运行时依赖 loglevel）/ `tsconfig.json`（@webgpu/types）/ `jest.config.cjs` / `.github/workflows/`（build/linter/tests/security/build-site）/ `scripts/`（站点部署 + prep_deps.sh TVM 依赖准备）

## 7. 复杂度热点

| 文件 | 行数 | 为什么难 | 攻读建议 |
|---|---|---|---|
| `src/llm_chat.ts` | 2298 | 单类承载 ABI 解析、双前向循环、六步采样链、xgrammar 生命周期、VLM 图像几何、全套统计；TVM 对象作用域管理（beginScope/detach）处处是坑 | 先读构造器的 ABI 解析（loadVMFunctionRegistry→resolveModelABI），再读 prefillStep→embedAndForward→sampleTokenFromLogits 主干，统计与 VLM 后置 |
| `src/config.ts` | 2607 | 前 330 行是高密度接口定义，后 2250 行是数据目录，两类内容混在一个文件 | 只精读前 330 行 + modelVersion 附近；目录部分当数据库查 |
| `src/web_worker.ts` | 844 | 双端类 + 流式 generator 跨线程搬移，消息时序容易绕晕 | 对照 message.ts 的 19 种 kind 画一张时序图 |
| `src/engine.ts` | 1432 | reloadInternal 十步链路 + asyncGenerate 的细粒度 try-catch 锁管理 + n>1 多 choice 统计口径 | 先 reload/unload 生命周期，再 chatCompletion 单一路径走通 |
| `src/openai_api_protocols/chat_completion.ts` | 1228 | 类型定义占大头，校验函数 8 组规则有交叉依赖 | 校验逻辑从上往下编号读，Hermes 硬编码注入是最绕的一段 |

## 8. 与生态关系

- **MLC-LLM（上游编译器）**：模型先用 MLC-LLM（基于 Apache TVM 的机器学习编译栈）编译：权重量化为 q4f16_1 等格式、计算图编译成 Relax VM 字节码（即 wasm 模型库）。`scripts/serve_mlc_llm_dist.sh` 支持本地调试自编译模型。WebLLM 是这条工具链的浏览器运行时终端。
- **TVM / tvmjs（`@mlc-ai/web-runtime`）**：推理内核的实际提供者——WebGPU 设备管理、wasm 实例化（polyfill WASI）、PagedKVCache builtin、tensor 作用域、artifact cache 全在 tvmjs。读不懂 `llm_chat.ts` 时往往缺的是 tvmjs 背景。
- **xgrammar（`@mlc-ai/web-xgrammar`）**：结构化输出引擎，GrammarCompiler/GrammarMatcher 把 JSON schema/EBNF 编译成 token 位掩码，与 SGLang/vLLM 生态共用同一技术。
- **vs llama.cpp wasm**：llama.cpp 也能编译到 wasm（llamafile 路线），但主算力路径是 CPU/wasm；WebLLM 从设计之初就以 WebGPU 为第一公民，吞吐显著更高，代价是兼容面窄（WebGPU 浏览器）。
- **vs transformers.js**：后者直接在浏览器跑 transformers 模型（ONNX/wasm 后端为主），胜在模型生态广；WebLLM 胜在有 TVM 编译优化 + 服务级特性（多模型、Service Worker 共享、SRI、xgrammar 结构化输出）。
- **与 openai-node**：协议层类型直接从 openai-node 移植（Apache-2.0），保证 `openai` npm 包用户零学习成本切换。

**选型建议**：想在网页里加个轻量聊天助手、且用户群基本用现代 Chrome/Edge——WebLLM 是当前最完整的选择；要覆盖 Safari/Firefox 等暂无 WebGPU 的环境，只能回退服务端推理或 transformers.js 的 wasm 路线；要在 Node 侧跑同样量化模型，则回到 MLC-LLM 原生运行时。三者在模型制品上同源（都是 MLC 编译产物），迁移成本主要在 API 层而非模型层。

📌 下一步：跑通 `examples/get-started`，再按第 5 节路径精读 `engine.ts` → `llm_chat.ts`；深挖单文件看 `../explain/` 五篇精讲；查官方文档细节看 `../deepwiki/`。
