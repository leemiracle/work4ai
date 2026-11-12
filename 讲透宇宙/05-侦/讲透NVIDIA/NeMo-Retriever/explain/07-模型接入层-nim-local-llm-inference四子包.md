# 07 模型接入层：models/ 四子包（nim 18 + local 15 + llm 11 + inference 6）

## 角色定位

`nemo_retriever/src/nemo_retriever/models/` 是 Retriever 的"模型方言层"：上层 operator（OCR/embed/rerank/caption/generation）只面对统一接口，不关心模型跑在哪里。全层 50 个 py 文件分四子包：**nim/**（18 文件）远程 NIM 端点客户端（HTTP+Triton gRPC 双协议）；**local/**（15 文件）本地 GPU 进程内模型；**llm/**（11 文件）文本生成抽象（Protocol+litellm+任务层）；**inference/**（6 文件）embedding 批处理引擎。形态权威定义在 `model.py:14`：`ModelRunMode = Literal["local", "NIM", "build-endpoint"]`——名义双形态，实际三值。

## 内部结构

**nim/ 双客户端**。`nim/nim.py:270` 的 `NIMClient` 是有状态 HTTP 客户端：构造时建 `ThreadPoolExecutor(max_workers=24)`（`nim.py:277-279`）供 Ray actor 整个生命周期复用。`invoke_image_inference_batches`（`nim.py:283`）按 `max_batch_size=8` 切片，future 按 `invoke_urls[idx % len(invoke_urls)]` 轮询分发（`nim.py:342`）——`invoke_url` 支持逗号分隔多端点（`nim.py:93-98`），是最朴素的客户端负载均衡。`_normalize_batch_response`（`nim.py:101-128`）兼容 `data`/`output`/`predictions` 三种形状并强校验条数；重试 `_post_with_retries`（`nim.py:131`）：429 独立预算（`nim.py:184-197`），5xx 走 `max_retries=5`（`nim.py:199-213`），4xx 不重试（`nim.py:215-219`）。MIME 靠 base64 魔法字节判定（`nim.py:258-262`）。

第二套是 `nim/primitives/nim_client.py:131` 的 `NimClient`（大小写区分两个类）：`protocol: "grpc"|"http"`（`nim_client.py:136-148`），gRPC 客户端惰性导入 tritonclient（`nim_client.py:114-118`）。`infer()`（`nim_client.py:312`）双路径：offline batching 用临时线程池（`nim_client.py:390`）；dynamic batching 把每图包成 `InferenceRequest` namedtuple（`nim_client.py:128`）入队，守护线程 `_batcher_loop`（`nim_client.py:680`）在 0.1s 窗口攒批，闸门=批满/trace context 不同切批（`nim_client.py:711`）/内存预算（`nim_model_interface.py:113-126`）；批尺寸从 Triton `get_model_config` 拉取并加锁缓存（`nim_client.py:225-249`）。

模型侧协议由 `ModelInterface` 基类定义（`nim_model_interface.py:15`）：format_input/parse_output 等钩子，加 dynamic batching 专属 `coalesce_requests_to_batch`（`nim_model_interface.py:86-111`，未实现即显式不支持动态批）。实现按 NIM 类型分文件在 `primitives/model_interface/`（yolox/vlm/parakeet/nemotron_parse/text_embedding），共享预处理在 helpers.py（PaddleOCR gRPC 输入需 32 倍数 padding+HWC→CHW，`helpers.py:25`）。端点健康由 `probe_endpoint`（`probe.py:37`）fail-fast：GET `/v1/health/ready`，云端无该路径时空 body POST 骗出 401/403 让 actor `__init__` 直接失败（`probe.py:44-51`）。

**local/**。`agent_llm.py:113` 的 `VLLMAgentChatLLM` 是进程内 vLLM 适配器，刻意白名单：只认 Nemotron Nano-8B 与 Super-49B 两族（`agent_llm.py:32-51`），别名表归一化到 HF ID（`agent_llm.py:55-66`）——"V1 只支持测过本地 tool-call 行为的模型"。Nemotron JSON 工具调用靠 chat template kwarg `tools_in_user_message: True`（`agent_llm.py:79`）。嵌入侧 `llama_nemotron_embed_1b_v2_embedder.py:48-49` 定义 `query: `/`passage: ` 指令前缀。

**llm/**。`litellm.py:48` 的 `LiteLLMClient` 借模型名前缀路由一家打多家：`nvidia_nim/`、`openai/`+api_base（vLLM/Ollama）、`huggingface/`（`litellm.py:51-55`），默认模型 `nemotron-3.5-lightning-30b-a3b`（`litellm.py:72`）。配置拆 transport/sampling 两个正交 Pydantic 对象（`litellm.py:62-67`）。`import litellm` 在函数体内（`litellm.py:143`）。文本契约极严：恰好一个 choice、拒绝 tool_calls/refusal/audio（`litellm.py:185-202`）。任务层 `TextGenerationTask` ABC（`tasks/base.py:42`）+ `RagAnswerTask`（`rag_answer.py:115`）；类型全 Protocol（`types.py:44`）——结构化鸭子类型。

**inference/**。`main_text_embed.py:632` 的 `create_text_embeddings_for_df` 是 DataFrame 嵌入主引擎：可重试码 `{408,429,500,502,503,504}`（`main_text_embed.py:64`），退避封顶 30s，429 尊重 `Retry-After` 头（`main_text_embed.py:421`）。`runtime.py:28` 的 `_embed_group` 是双形态分派枢纽：endpoint 为 None 走本地 embedder——query 侧 `embed_queries`、passage 侧手动拼 `"passage: "` 前缀（`runtime.py:59`）；图像模态批尺寸远程压 4、本地压 8（`runtime.py:66-73`）。`vllm.py:85` 的 `nvlink_is_available` 用 NVML 实测且"未知即视为有"防误降级。

## 外部连接

上游消费方覆盖全部 operator 层：`operators/extract/ocr/gpu_ocr.py`、`operators/extract/parse/nemotron_parse.py`、`operators/embed/gpu_operator.py`、`operators/generation/base.py`、`operators/graph_ops/react_agent_operator.py`、`graph/retriever.py`、`common/modality/ocr/shared.py`、`harness/portal/app.py`。依赖 requests/httpx、tritonclient[grpc]（可选）、vllm+pynvml、litellm。

## 数据流

PDF 页图 OCR：operator 拿 base64 → `NimClient.infer`：解码 → format_input 打包（HTTP 为 `{"input":[{"type":"image_url",...}]}`，`nim.py:315-322`）→ 线程池并发推理 → parse_output → process_inference_results 用 batch_data 缓存形状反变换坐标。LLM 流：`LiteLLMClient.generate` → `RagAnswerTask.execute` → litellm → 契约校验 → `GenerationResult`。嵌入流：`embed_text_main_text_embed`（`runtime.py:109`）按模态分组 → `_embed_group` 二选一 → 向量写回 `df.metadata["embedding"]`（`main_text_embed.py:11`）。

## 设计决策

1. **双客户端而非一个**：`nim.py:NIMClient`（纯 HTTP、chat/image 端点、多 URL 轮询）与 `primitives/nim_client.py:NimClient`（gRPC+HTTP、Triton 模型、动态批）服务两类后端，ModelInterface 吸收模型差异。
2. **429 与 5xx 分账**：限流是"用户太多"、5xx 是"服务坏了"，前者独立预算——两处实现（`nim.py:184`、`nim_client.py:543`）口径一致。
3. **fail-fast 探活**：401/403 前移到 actor 启动期（`probe.py:51`）。
4. **白名单式本地 LLM**：未测过 tool-call 的本地模型一律拒绝（`agent_llm.py:128-133`）。
5. **攒批 trace 一致性**：dynamic batcher 拒绝跨 trace context 攒批（`nim_client.py:711`）——OTel span 不能混批，可观测性优先于批效率。

## 新人提示

- 两个 NimClient 各一套重试循环，默认值（5/3 与 10/5）不同，调参需两处同步。
- litellm/tritonclient/vllm 全惰性导入，模块顶层 import 安全；但 `helpers.py` 顶层的 `cv2.setNumThreads(1)` 全局生效。
- 嵌入前缀是正确性问题：忘加 `query: `/`passage: ` 会显著掉召回，`runtime.py:59` 的手动拼接分支最容易漏。
- 自定义 NIM 聚合响应先过 `_normalize_batch_response` 的条数强校验（`nim.py:126-127`）。
- `nim.py:530` 起的自由函数是向后兼容包装（每次调用建临时线程池），新代码直接用 `NIMClient` 类（`nim.py:560` docstring 自己也这么劝）。
