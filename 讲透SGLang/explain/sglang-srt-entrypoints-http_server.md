# 深度解析：`python/sglang/srt/entrypoints/http_server.py`

> 源码: python/sglang/srt/entrypoints/http_server.py @ commit ec075d8bc

`http_server.py` 是 SGLang Runtime（SRT）推理服务的 HTTP 入口，全文件约 2381 行，把 FastAPI 应用、全部 REST 路由、服务启动编排（`launch_server`）和预热（warmup）逻辑收拢在一个文件里。
在 SGLang 的多进程架构中，本模块运行在**主进程**：HTTP server（uvicorn/Granian）、`Engine` 与 `TokenizerManager` 同属主进程，而 `Scheduler`（调度+推理）和 `DetokenizerManager`（反 tokenize）是子进程，彼此通过 ZMQ IPC 通信（见 L2343-2357 的 launch_server docstring）。
本文件自身不做任何 tokenize 或推理，它只做三件事：把 HTTP 请求规范化后交给 `TokenizerManager.generate_request()`，把 `TokenizerManager` 的能力（权重更新、LoRA、profile、cache 管理等）暴露成管理端点，以及在 `launch_server()` 中完成"起子进程 → 装 app → 起 uvicorn"的整个编排。
事件循环统一用 uvloop（L181 `asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())`），保证前端高并发下的低开销；序列化统一走 orjson（`SGLangORJSONResponse`/`dumps_json`/`orjson_response`）。

## 多进程架构中的位置

```
            主进程（本文件所在）
┌──────────────────────────────────────────────┐
│  uvicorn/Granian → FastAPI app (http_server) │
│       │ lifespan 时构造                       │
│  TokenizerManager ── TemplateManager         │
│       │ ZMQ PUSH                ▲ ZMQ PULL   │
└───────┼─────────────────────────┼────────────┘
        ▼                         │
┌──────────────┐   ZMQ   ┌────────────────────┐
│ Scheduler(s) │ ──────► │ DetokenizerManager │ (均为子进程)
│  TP/DP/PP    │         │   (反 tokenize)     │
└──────────────┘         └────────────────────┘
```

- `launch_server()`（L2335）负责 spawn 子进程并启动 HTTP 服务，是 `python -m sglang.launch_server` CLI 的最终落点。
- 文件内 80+ 个端点分为六组：Native API、OpenAI 兼容、Ollama 兼容、Anthropic 兼容、SageMaker、Vertex AI。

## 核心类与函数

### 1. 全局状态：`_GlobalState`（L189-205）

```python
@dataclasses.dataclass
class _GlobalState:
    tokenizer_manager: Union[TokenizerManager, MultiTokenizerRouter, TokenizerWorker]
    template_manager: TemplateManager
    scheduler_info: Dict
```

- 模块级单例 `_global_state`（L196），经 `set_global_state()`/`get_global_state()`（L199-205）存取。
- 三种 tokenizer_manager 形态对应三种进程拓扑：
  - `TokenizerManager`：单 tokenizer 模式（默认），与 HTTP server 同进程；
  - `TokenizerWorker`：多 tokenizer 模式（`--tokenizer-worker-num > 1`）下每个 uvicorn worker 进程各自持有；
  - `MultiTokenizerRouter`：`TokenizerWorker` 的路由包装（定义在 `multi_tokenizer_mixin.py`）。
- 所有路由处理函数都通过 `_global_state.tokenizer_manager.xxx` 触达引擎能力——这是"HTTP 层与引擎层解耦"的唯一桥梁。

### 2. `_init_granian_worker()`（L208-231）与 `init_multi_tokenizer()`（L234-282）

两个"工作进程自举"函数，都从**共享内存**读启动参数：

- `read_from_shared_memory(f"multi_tokenizer_args_{main_pid}")` 拿到 `(port_args, server_args, scheduler_info)` 三元组——主进程用 `write_data_for_multi_tokenizer` 写入（见 L2227-2229）。
- `init_multi_tokenizer()` 是多 tokenizer worker 的 lifespan 初始化：
  - 为当前进程**新建独立 ZMQ ipc 名**（`ipc://{tempfile.NamedTemporaryFile(delete=False).name}`，L254-256），使 detokenizer 的回包能路由到正确的 worker；
  - L249-251 断言多 tokenizer 模式不支持 API key 认证（每个 worker 独立鉴权会导致语义不一致）；
  - 构造 `TokenizerWorker` + `TemplateManager`，`initialize_templates` 后 `set_global_state`；
  - 日志打印本 worker 的 pid 与 ipc_name（L257-260）。
- `_init_granian_worker()` 结构相同，但直接构造 `TokenizerManager`（Granian worker 数为 1，无需路由层）。

### 3. `lifespan()`（L285-401）——FastAPI 生命周期钩子

uvicorn 启动 app 时执行，是所有 serving handler 的真正诞生地：

1. **三分支确定 server_args 来源**（L287-299）：
   - `app.is_single_tokenizer_mode=True`：直接读 `app.server_args` 属性（由 `_setup_and_run_http_server` 预先塞入，L2196-2198）；
   - `SGLANG_GRANIAN_PARENT_PID` 环境变量存在：Granian worker，走 `_init_granian_worker()`；
   - 否则：多 tokenizer worker，走 `init_multi_tokenizer()`，线程标签带 worker_id。
2. **可观测性**（L302-313）：
   - `enable_metrics` 时挂 `add_prometheus_middleware(app)` + `enable_func_timer()`；
   - `enable_trace` 时 `process_tracing_init(otlp_endpoint, "sglang")`，且 PD disaggregation 模式下给线程标签加 "Prefill"/"Decode" 前缀（L309-312），便于按角色过滤 trace。
3. **构造 serving handler 家族**（L316-352），全部存到 `fast_api_app.state`：
   - `OpenAIServingCompletion`（completions）
   - `openai_serving_chat`：经 `_global_state.tokenizer_manager.serving_chat_class(...)` 构造——**property 钩子允许 TokenizerManager 子类换 chat 实现**（tokenizer_manager.py L226-234）
   - `OpenAIServingEmbedding` / `OpenAIServingClassify` / `OpenAIServingScore` / `OpenAIServingRerank`
   - `OpenAIServingTokenize` / `OpenAIServingDetokenize`
   - `OpenAIServingTranscription`
   - `OllamaServing`（Ollama 兼容层）
   - `AnthropicServing(openai_serving_chat)`——包装 OpenAI chat serving，即 Anthropic→OpenAI 协议适配器
   - `OpenAIServingResponses` 在 try/except 中初始化（L366-379），失败只 warning 不阻断启动
4. **tool server**（L354-364）：`--tool-server demo` → `DemoToolServer()`；给 MCP 地址 → `MCPToolServer().add_tool_server(...)`。供 Responses API 的 function calling 使用。
5. **warmup**（L381-401）：
   - 先跑用户自定义 `server_args.warmups`（逗号分隔，`execute_warmups`）；
   - 再起后台线程 `_wait_and_warmup`；
   - `yield` 之后（服务关闭时）`warmup_thread.join()`。

### 4. FastAPI app 与异常处理（L405-501）

- `app = FastAPI(lifespan=lifespan, openapi_url=...)`（L405-408）：`DISABLE_OPENAPI_DOC` 环境变量可关掉 `/openapi.json`。
- CORS 全放开（L409-415：`allow_origins=["*"]` 等）。
- L418-420 include `v1_loads` router（提供 `GET /v1/loads`）。
- **两个自定义异常处理器**是 API 契约的关键：
  - `HTTPException` handler（L423-448）：普通端点返回平铺 `ErrorResponse`；`/v1/responses` 前缀返回 OpenAI 风格的**嵌套** error envelope：
    ```json
    {"error": {"message": "...", "type": "...", "param": null, "code": 400}}
    ```
  - `RequestValidationError` handler（L452-485）：把 FastAPI 默认的 422 改成 **400**，`/v1/responses` 同样特判为嵌套格式。
- `validate_json_request`（L488-501）：作为 OpenAI 端点的 `Depends` 依赖，强制 `Content-Type: application/json`，违规抛 `RequestValidationError`（进而变成 400）。注意解析细节：`content_type.split(";", maxsplit=1)[0]` 容忍 `; charset=utf-8` 后缀。

### 5. health check：`health_generate()`（L507-579）

`/health` 与 `/health_generate` 共用同一 handler（双装饰器 L507-508），是全文件最精巧的端点：

**短路分支**（L517-528）：
- `gracefully_exit`（正在关停）→ 503；
- `server_status == ServerStatus.Starting` → 503；
- `/health` 且未开 `SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION` → 直接 200（纯 liveness，不触引擎）。

**真实生成探测**（L530-555）：
- 构造 `max_new_tokens=1, temperature=0.0` 的最小请求，rid 用 `HEALTH_CHECK_RID_PREFIX`（值为 `"HEALTH_CHECK"`，constants.py L12）+ 时间戳；
- generation 模型用 `GenerateReqInput(input_ids=[0])`，embedding 模型用 `EmbeddingReqInput`；
- **PD disaggregation 模式下注入 `FAKE_BOOTSTRAP_HOST`/`bootstrap_room=0`**（L540-545），避免健康检查走真实 KV 传输 bootstrap；
- 请求 `log_metrics=False`，不污染指标。

**判活逻辑**（L557-578）：
- 不看生成结果，只轮询 `last_receive_tstamp`——`TokenizerManager.handle_loop` 每收到任何 ZMQ 消息就刷新该时间戳；
- 只要该通道在 `HEALTH_CHECK_TIMEOUT`（环境变量 `SGLANG_HEALTH_CHECK_TIMEOUT`，默认 20s）内有心跳 → cancel 任务、清 rid、置 `ServerStatus.Up`、返回 200；
- 超时 → cancel、pop rid、置 `UnHealthy`、打详细日志（含起始时间与最后心跳时间）、返回 503。
- 这解释了 docstring 里"忙时零开销"：探测请求进了 scheduler 队列但没人处理它也没关系，忙时本来就有别的消息在刷时间戳。

### 6. 信息类端点（L582-679）

- `/model_info`（L592-609）：`model_path`/`tokenizer_path`/`is_generation`/`preferred_sampling_params`/`weight_version`/`has_image_understanding`/`has_audio_understanding`/`model_type`/`architectures`。`/get_model_info`（L582-589）是废弃 shim，打 deprecation 警告后转调。
- `/server_info`（L632-652）：`dataclasses.asdict(server_args)` + `scheduler_info` + `get_internal_state()`（每个 DP rank 的内部状态）+ `__version__` + `describe_kv_events_publisher()`（供 KV-aware router 订阅 KV 事件的结构化描述符）。
- `/get_load`（L655-679）：废弃端点，内部调新 `get_loads(include=["core"])` 再把 `GetLoadsReqOutput` 投影成历史字段形状（`dp_rank/num_reqs/num_waiting_reqs/num_tokens/num_pending_tokens/ts_tic`），保证老客户端不断。

### 7. 管理端点群（L684-1486）

按功能分组（绝大多数带 `@auth_level(AuthLevel.ADMIN_OPTIONAL)` 鉴权，详见完整路由表）：

**内部状态与调试**
- `/set_internal_state`（L684-688）：POST/PUT，运行时改 scheduler 参数（如 `pp_max_micro_batch_size`），示例 curl 在 L683 注释。
- `/dumper/{method}`（L694-704）：仅当 `DUMPER_SERVER_PORT=reuse` 时注册——**条件路由**，避免硬依赖 dumper 模块。
- `/slow_down`（L1314-1325）：人为拖慢系统，注释给出使用场景——PD 大规模测试时节点不够，用慢 D 攒够 batch 再放开。

**cache 与语料管理**
- `/flush_cache`（L769-784）：带 `timeout` query 参数（ge=0）；有运行中/排队请求时操作不会执行，返回提示。
- `/add_external_corpus` / `/remove_external_corpus` / `/list_external_corpora`（L787-842）：服务 ngram 投机解码的外部语料装卸查。

**HiCache 存储后端**
- `/hicache/storage-backend`（GET/PUT/DELETE，L881-952）+ `POST /hicache/storage-backend/clear`（L861-869）+ 废弃别名 `/clear_hicache_storage_backend`（L845-856）。
- PUT/DELETE 前置检查 `admin_api_key` 是否配置（L888-889），未配置直接 400 返回 `_admin_api_key_missing_response()`——这是 `ADMIN_FORCE` 语义的手工模拟（L1851-1857 的 FIXME 注释解释了为何不直接用 ADMIN_FORCE：auth 中间件会把所有端点卷进鉴权）。
- attach/detach 只允许在无运行/排队请求时执行。

**性能观测**
- `/start_profile`（L955-977）：透传 output_dir/start_step/num_steps/activities/with_stack/record_shapes/profile_by_stage/merge_profiles/profile_prefix/profile_stages 全部 torch profiler 参数。
- `/stop_profile`（L980-988）。
- `/set_trace_level`（L991-998）：同步函数（无 await），设全局 trace level。
- `/freeze_gc`（L1001-1011）：前后端一起冻结 GC（防 GC 停顿抖动）。
- `/start_expert_distribution_record` / `/stop_...` / `/dump_...`（L1014-1044）：MoE 专家分布观测。

**权重热更新家族**（L1047-1311）
- `/update_weights_from_disk`（L1047-1069）：返回三元组 `(success, message, num_paused_requests)`。
- `/init_weights_send_group_for_remote_instance`（L1072-1086）+ `/send_weights_to_remote_instance`（L1089-1103）：跨 SGLang 实例直传权重（checkpoint-engine 类集成）。
- `/get_remote_instance_transfer_engine_info`（废弃）/`/remote_instance_transfer_engine_info`（L1106-1141）：查指定 rank 的传输引擎信息，内部转发到 `engine_info_bootstrap_url`。
- `/init_weights_update_group` / `/destroy_weights_update_group`（L1144-1172）：RL 训练场景的参数更新进程组。
- `/update_weights_from_tensor`（L1175-1194）：HTTP 只传 tensor 元数据，tensor 本体走进程组拷贝；二进制 base64。
- `/update_weights_from_distributed`（L1197-1213）/`/update_weights_from_ipc`（L1216-1230，checkpoint-engine 集成点，成功后置 `initial_weights_loaded=True`）。
- `/update_weight_version`（L1233-1261）：可选先 `abort_request(abort_all=True)`；然后**直接改 `server_args.weight_version`**（注释：单一事实源，简单操作不走复杂锁机制）。
- `/get_weights_by_name`（L1264-1275）与 `/weights_checker`（L1302-1311）。
- `/release_memory_occupation` / `/resume_memory_occupation`（L1278-1299）：临时释放/恢复 GPU 显存（配合权重加载）。

**LoRA**
- `/load_lora_adapter`（L1328-1343）/`/load_lora_adapter_from_tensors`（L1346-1358，无 auth 装饰器）/`/unload_lora_adapter`（L1361-1376）：运行时装卸 adapter。

**会话与请求控制**
- `/open_session` / `/close_session`（L1379-1400）：server-side session。
- `/configure_logging`（L1403-1408）：运行时改 request logging 配置。
- `/abort_request`（L1411-1421）：按 rid 或 abort_all。
- `/pause_generation` / `/continue_generation`（L1466-1485）：全局暂停/恢复（权重更新前置动作）。

**纯文本工具（不触引擎）**
- `/parse_function_call`（L1424-1443）：本地跑 `FunctionCallParser.parse_non_stream`，返回 normal_text+calls。
- `/separate_reasoning`（L1446-1463）：本地跑 `ReasoningParser.parse_non_stream`，拆 reasoning_text/normal_text。

### 8. Native 生成端点：`generate_request()`（L708-742）

- **流式分支**（L715-733）：
  ```python
  return StreamingResponse(
      stream_results(),                       # SSE: b"data: {...}\n\n" ... b"data: [DONE]\n\n"
      media_type="text/event-stream",
      background=_global_state.tokenizer_manager.create_abort_task(obj),
  )
  ```
  `ValueError` 被转成 error 事件继续以 SSE 吐出（不让流中途断掉）。
  关键设计：`background=create_abort_task(obj)`——**客户端断连后由 background task 延迟 2s 触发 abort**（tokenizer_manager.py L1658-1670），利用 FastAPI 的 background 机制在响应体发送完毕后兜底清理。
- **非流式分支**（L734-742）：`generate_request(obj, request).__anext__()` 只取第一个输出即返回；`ValueError` 转错误响应。
- `/encode`（L745-754，embedding）与 `/classify`（L757-766，reward/classification）与 generate 同构，输入类型换成 `EmbeddingReqInput`。

### 9. REST 路由表（全量枚举）

> 格式：方法 | 路径 | 行号 | 说明。`[鉴权]` = `@auth_level(ADMIN_OPTIONAL)`；`[依赖]` = `Depends(validate_json_request)`。

**Native API**

| 方法 | 路径 | 行号 | 说明 |
|---|---|---|---|
| GET | `/health` | 507 | liveness（默认不生成） |
| GET | `/health_generate` | 508 | readiness（真实生成探测） |
| GET | `/get_model_info` | 582 | 废弃 → `/model_info` |
| GET | `/model_info` | 592 | 模型元信息 |
| GET | `/get_weight_version`、`/weight_version` | 612-613 | 废弃 → 404 引导去 `/model_info` |
| GET | `/get_server_info` | 622 | 废弃 → `/server_info` |
| GET | `/server_info` | 632 | server_args+internal_states+kv_events |
| GET | `/get_load` | 655 | 废弃 → 投影 `/v1/loads` |
| POST/PUT | `/set_internal_state` | 684 | [鉴权] 运行时改内部参数 |
| POST | `/dumper/{method}` | 694 | [鉴权] 条件注册（DUMPER_SERVER_PORT=reuse） |
| POST/PUT | `/generate` | 708 | 核心 generate（SSE 流式可选） |
| POST/PUT | `/encode` | 745 | embedding |
| POST/PUT | `/classify` | 757 | 分类/reward |
| GET/POST | `/flush_cache` | 769 | [鉴权] 清 radix cache |
| POST | `/add_external_corpus` | 787 | [鉴权] ngram 外部语料 |
| POST | `/remove_external_corpus` | 812 | [鉴权] |
| GET | `/list_external_corpora` | 830 | [鉴权] |
| GET/POST | `/clear_hicache_storage_backend` | 845 | [鉴权] 废弃 |
| POST | `/hicache/storage-backend/clear` | 861 | [鉴权] |
| PUT | `/hicache/storage-backend` | 881 | [鉴权] attach |
| DELETE | `/hicache/storage-backend` | 913 | [鉴权] detach |
| GET | `/hicache/storage-backend` | 940 | [鉴权] 状态查询 |
| GET/POST | `/start_profile` | 955 | [鉴权] |
| GET/POST | `/stop_profile` | 980 | [鉴权] |
| GET/POST | `/set_trace_level` | 991 | |
| GET/POST | `/freeze_gc` | 1001 | [鉴权] |
| GET/POST | `/start_expert_distribution_record` | 1014 | [鉴权] |
| GET/POST | `/stop_expert_distribution_record` | 1025 | [鉴权] |
| GET/POST | `/dump_expert_distribution_record` | 1036 | [鉴权] |
| POST | `/update_weights_from_disk` | 1047 | [鉴权] |
| POST | `/init_weights_send_group_for_remote_instance` | 1072 | [鉴权] |
| POST | `/send_weights_to_remote_instance` | 1089 | [鉴权] |
| GET | `/get_remote_instance_transfer_engine_info` | 1106 | [鉴权] 废弃 |
| GET | `/remote_instance_transfer_engine_info` | 1117 | [鉴权] |
| POST | `/init_weights_update_group` | 1144 | [鉴权] |
| POST | `/destroy_weights_update_group` | 1160 | [鉴权] |
| POST | `/update_weights_from_tensor` | 1175 | [鉴权] |
| POST | `/update_weights_from_distributed` | 1197 | [鉴权] |
| POST | `/update_weights_from_ipc` | 1216 | [鉴权] |
| POST | `/update_weight_version` | 1233 | [鉴权] |
| GET/POST | `/get_weights_by_name` | 1264 | [鉴权] |
| GET/POST | `/release_memory_occupation` | 1278 | [鉴权] |
| GET/POST | `/resume_memory_occupation` | 1290 | [鉴权] |
| POST | `/weights_checker` | 1302 | [鉴权] |
| GET/POST | `/slow_down` | 1314 | [鉴权] 测试辅助 |
| POST | `/load_lora_adapter` | 1328 | [鉴权] |
| POST | `/load_lora_adapter_from_tensors` | 1346 | 无鉴权装饰器 |
| POST | `/unload_lora_adapter` | 1361 | [鉴权] |
| GET/POST | `/open_session` | 1379 | |
| GET/POST | `/close_session` | 1393 | |
| GET/POST | `/configure_logging` | 1403 | [鉴权] |
| POST | `/abort_request` | 1411 | [鉴权] |
| POST | `/parse_function_call` | 1424 | 纯本地解析 |
| POST | `/separate_reasoning` | 1446 | 纯本地解析 |
| POST | `/pause_generation` | 1466 | [鉴权] |
| POST | `/continue_generation` | 1477 | [鉴权] |

**OpenAI 兼容**

| 方法 | 路径 | 行号 | 说明 |
|---|---|---|---|
| POST | `/v1/completions` | 1491 | [依赖] → `openai_serving_completion` |
| POST | `/v1/chat/completions` | 1499 | [依赖] → `openai_serving_chat` |
| POST | `/v1/embeddings` | 1509 | [依赖] → `openai_serving_embedding` |
| POST | `/v1/classify` | 1521 | [依赖] → `openai_serving_classify` |
| POST | `/v1/tokenize`（别名 `/tokenize`） | 1533-1543 | [依赖] 别名不进 schema |
| POST | `/v1/detokenize`（别名 `/detokenize`） | 1551-1561 | [依赖] |
| POST | `/v1/audio/transcriptions` | 1569 | multipart 表单；response_format 白名单 json/text/verbose_json |
| WebSocket | `/v1/realtime` | 1609 | 仅 transcription 子集，chat 模式被 `Literal["transcription"]` 拒绝 |
| GET | `/v1/models` | 1620 | base model + 全部已加载 LoRA adapter 均列为 ModelCard |
| GET | `/v1/models/{model:path}` | 1652 | 检索单个 model card，404 带 OpenAI 错误格式 |
| POST | `/v1/score` | 1677 | [依赖] CausalLM logprob 与 SeqCls 双支持 |
| POST | `/v1/responses` | 1685 | [依赖] dict 接收→`ResponsesRequest`；AsyncGenerator 时包 SSE |
| GET | `/v1/responses/{response_id}` | 1705 | 检索后台 response |
| POST | `/v1/responses/{response_id}/cancel` | 1713 | 取消后台 response |
| POST/PUT | `/v1/rerank` | 1721 | [依赖] |
| GET | `/v1/loads` | v1_loads.py:135 | 经 router include（L418-420） |

**Ollama 兼容**（路径可被环境变量覆写）

| 方法 | 路径（默认） | 行号 | 环境变量 |
|---|---|---|---|
| GET/HEAD | `/`（或自定义） | 1736-1748 | `SGLANG_OLLAMA_ROOT_ROUTE` |
| POST | `/api/chat` | 1751 | `SGLANG_OLLAMA_CHAT_ROUTE` |
| POST | `/api/generate` | 1757 | `SGLANG_OLLAMA_GENERATE_ROUTE` |
| GET | `/api/tags` | 1765 | `SGLANG_OLLAMA_TAGS_ROUTE` |
| POST | `/api/show` | 1771 | `SGLANG_OLLAMA_SHOW_ROUTE` |

未配置 Ollama root 时，`/` 返回 "SGLang is running"；配置后返回 "Ollama is running"。

**Anthropic 兼容**

| 方法 | 路径 | 行号 | 说明 |
|---|---|---|---|
| POST | `/v1/messages` | 1780 | [依赖] Messages API |
| POST | `/v1/messages/count_tokens` | 1790 | [依赖] token 计数 |

**SageMaker / Vertex AI**

| 方法 | 路径 | 行号 | 说明 |
|---|---|---|---|
| GET | `/ping` | 1801 | 恒 200（纯 HTTP liveness，SageMaker 契约） |
| POST | `/invocations` | 1807 | 转 chat completions |
| POST | `/vertex_generate` | 1818 | `AIP_PREDICT_ROUTE` 可覆写；instances[] → batch GenerateReqInput，复用本文件 `generate_request()` |

### 10. warmup 家族（L1876-2083）

`_execute_server_warmup(server_args)`（在后台线程跑）三阶段：

1. **等服务起来**（L1885-1902）：最多 120s 轮询 `/model_info`，失败 `kill_process_tree(os.getpid())` 自杀。
2. **构造探测请求**（L1904-1969），按模型形态四路分支：
   - `skip_tokenizer_init`：发 `input_ids=[[10,11,12]]*dp_size`；
   - VLM 且非 disaggregation：发带 32x32 黑底 PNG 的 chat completions（base64 常量 `MINIMUM_PNG_PICTURE_BASE64`，L1873；注释说明 GLM4v 要求最小 32x32）；
   - 普通 generation：`text="The capital city of France is"` ×dp_size（dp=1 时降为单字符串，规避 embedding list-size-1 bug，L1958-1961）；
   - embedding 模型：走 `/encode`，`max_new_tokens=1`。
3. **发送并置状态**（L1971-2034）：
   - 普通模式：POST `/generate`，超时 `SGLANG_WARMUP_TIMEOUT`（>0 时）否则 600s；成功置 `ServerStatus.Up`。
   - **PD disaggregation 模式**（L1985-2024）：特殊 payload——`ignore_eos=True`、`bootstrap_host=[FAKE_BOOTSTRAP_HOST]*dp_size`、`bootstrap_room = [i*(2**63//dp_size)+(i%tp_size)]`（hack 保证各 dp rank 唯一 room 以启用 fake transfer）、`input_ids=[[10,11,12,13]]*dp_size`；超时上限 1800s（deep_gemm 预编译非常慢）；失败只置 `UnHealthy` 不杀进程（PD 侧 warmup 失败容忍度更高）。

`_wait_and_warmup`（L2037-2062）：
- `checkpoint_engine_wait_weights_before_ready` 时先 `_wait_weights_ready()`（L2065-2083：等 `initial_weights_loaded`，上限 `SGLANG_WAIT_WEIGHTS_READY_TIMEOUT`=120s，超时只打 error 不杀）；
- `skip_server_warmup` 直接置 Up；
- ready 后打 "The server is fired up and ready to roll!"；
- 可选 `delete_ckpt_after_loading` 删 checkpoint 目录；
- `debug_tensor_dump_input_file` 模式下 warmup 完自杀（只为 dump 输入）；
- 调 `launch_callback()`。

### 11. 启动编排：`launch_server()` 与 `_setup_and_run_http_server()`（L2086-2381）

`launch_server`（L2335-2381）只有两步：

1. `Engine._launch_subprocesses(server_args, ...)` → 返回 `(tokenizer_manager, template_manager, port_args, scheduler_init_result, subprocess_watchdog)`。Scheduler/Detokenizer 子进程在这里被 spawn（`run_scheduler_process`/`run_detokenizer_process` 从 `entrypoints/engine.py` 导入，L70-75）。
2. `_setup_and_run_http_server(...)`。

`_setup_and_run_http_server`（L2133-2332）是 HTTP 层的最终装配：

- `set_global_state(...)`（L2148-2154）；把 `subprocess_watchdog` 挂到 tokenizer_manager 上（L2157-2158，注释：SIGQUIT handler 的单一事实源）。
- `enable_metrics` 时挂 `add_prometheus_track_response_middleware`（L2160-2161；与 lifespan 里的 `add_prometheus_middleware` 分工：前者按响应跟踪）。

**Granian/HTTP2 分支**（L2164-2190）：
- `--enable-http2` 时把 `(port_args, server_args, scheduler_info)` 写入 shm（**复用多 tokenizer 机制**传参给独立 worker 进程）；
- 设 `SGLANG_GRANIAN_PARENT_PID` 环境变量让 worker 能定位 shm 段；
- **先 `_close_main_process_sockets()`**（L2086-2105：关掉主进程的 `recv_from_detokenizer`/`send_to_scheduler`，兼容 SenderWrapper 的双层 socket 结构）避免 worker 绑定冲突；
- `_run_granian_server`（L2108-2130）：`Interfaces.ASGI + HTTPModes.auto + Loops.uvloop + workers=1`，支持 SSL；
- finally 里 unlink shm。

**认证中间件**（L2204-2222）：仅单 tokenizer 模式；配了 `api_key`/`admin_api_key` 或存在 ADMIN_FORCE 端点时挂 `add_api_key_middleware`。注释详述了向后兼容语义（api_key only = 全端点要求 key；无 key = 无限制但 ADMIN_FORCE 端点仍须 admin key）。

**uvicorn 启动三种形态**（L2242-2326）：
1. 单 worker + `enable_ssl_refresh`：手工 `uvicorn.Config` + `config.load()` 拿到 SSLContext，起 `SSLCertRefresher` 后台刷新证书，`asyncio.run` 驱动（L2243-2279）；
2. 单 worker 默认：`uvicorn.run(app, ..., loop="uvloop")`（L2282-2294）；
3. 多 worker（`tokenizer_worker_num > 1`）：`uvicorn.run("sglang.srt.entrypoints.http_server:app", workers=N, ...)`——传**字符串 import 路径**让 uvicorn 自行 fork，每个 worker 经 lifespan→`init_multi_tokenizer()` 从 shm 恢复参数；额外配 `timeout_worker_healthcheck`；显式不支持 ssl refresh（L2305-2310 打 warning）；调整 uvicorn LOGGING_CONFIG 让本模块日志走 default handler（L2297-2303）。

finally 块（L2327-2332）：多 tokenizer 时 unlink shm 并 `clear_all_sockets()`。

## 与其他模块的交互

**import（本文件依赖）**：
- `entrypoints/engine.py`：`Engine`、`init_tokenizer_manager`、`run_scheduler_process`、`run_detokenizer_process`——子进程启动逻辑全在这。
- `managers/tokenizer_manager.py`：`TokenizerManager`、`ServerStatus`（health check 与 warmup 直接读写其状态）。
- `managers/io_struct.py`：30+ 个 `*ReqInput` 数据类——HTTP 层的请求体 schema 与 ZMQ 消息体复用同一套定义（L707 注释：fastapi implicitly converts json to dataclass）。
- `entrypoints/openai/serving_*.py`：9 个 OpenAI serving handler + `tool_server`（Demo/MCP）。
- `entrypoints/ollama/{protocol,serving}.py`、`entrypoints/anthropic/{protocol,serving}.py`：两套兼容层。
- `entrypoints/v1_loads.py`：`router`（`GET /v1/loads`，内部反向 import 本文件的 `get_global_state`——唯一循环引用点，用函数内延迟 import 规避）。
- `managers/multi_tokenizer_mixin.py`：`MultiTokenizerRouter`/`TokenizerWorker`/`write_data_for_multi_tokenizer`/`read_from_shared_memory`/`get_main_process_id`。
- `managers/template_manager.py`：chat/completion 模板管理。
- `utils/auth.py`：`auth_level` 装饰器、`add_api_key_middleware`、`app_has_admin_force_endpoints`。
- `utils/json_response.py`：orjson 三件套。
- `utils/watchdog.py`：`SubprocessWatchdog`（子进程存活监控）。
- `observability/`：trace、func_timer；`parser/reasoning_parser.py`、`function_call/function_call_parser.py`；`entrypoints/warmup.py`；`disaggregation/utils.py`（`FAKE_BOOTSTRAP_HOST`/`DisaggregationMode`）。

**被调用（谁启动它，grep 验证 8 处）**：
- `sglang/launch_server.py` L48（CLI 主入口）；
- `sglang/srt/entrypoints/http_server_engine.py` L9、`sglang/srt/ray/http_server.py` L38（Ray 集成）、`sglang/compile_deep_gemm.py` L21、`sglang/lang/backend/runtime_endpoint.py` L383、`sglang/test/bench_one_batch_server_internal.py` L23。

**运行时数据流**：
```
HTTP client → uvicorn/Granian → 本文件路由 → TokenizerManager.generate_request()
  → ZMQ PUSH → Scheduler(s) → ZMQ → DetokenizerManager → ZMQ PULL
  → TokenizerManager.handle_loop() → async generator → HTTP 响应
```
管理端点则大多走 `TokenizerControlMixin`（tokenizer_manager 的控制方法）单向下发 ZMQ 控制消息；少数端点纯本地（parse_function_call/separate_reasoning）或纯 HTTP（/ping）。

## 关键设计决策

1. **"HTTP 层零推理逻辑"的薄路由哲学**：所有 `/v1/*` 端点都是一行转发，协议适配（OpenAI/Ollama/Anthropic/SageMaker/Vertex 五套皮）全部下沉到各自 `serving_*.py`；`io_struct.py` 的 dataclass 同时充当 HTTP schema 与 IPC 消息体，消除"接口层二次定义"的漂移风险。
2. **health check 的"心跳旁路"设计**：不等待探测请求的真实完成，只看 `last_receive_tstamp` 是否被任何 ZMQ 消息刷新（L557-565）。忙时零开销、闲时真探测，还天然区分 `/health`（liveness）与 `/health_generate`（readiness）两种语义；失败时把 `server_status` 置 `UnHealthy` 会联动 sigterm_watchdog 的快速退出路径。
3. **多 HTTP worker 的 shm 自举协议**：单 worker 用 app 属性传参，多 worker/Granian 用共享内存 + 每进程独立 `tokenizer_ipc_name`（L254-256）实现回包路由。代价是多 worker 模式放弃 API key 支持（L249-251），收益是 tokenizer/HTTP 层可水平扩展。
4. **流式请求的断连兜底交给 background task**：SSE 响应挂 `create_abort_task`（延迟 2s abort），配合 `_wait_one_response` 的 type-1/type-3 断连检测，构成完整 abort 矩阵（tokenizer_manager.py 文件尾 L2886-2897 有完整表格）。
5. **warmup 按拓扑定制探测流量**：普通模型一句话、VLM 最小 PNG、disaggregation 模式 fake-bootstrap 多 rank 请求（L1985-2024）。把"服务可用"定义为"真实走过一次完整 PD 链路"。
6. **错误格式的双轨制**：普通端点平铺 `ErrorResponse`，`/v1/responses` 用 OpenAI 嵌套 envelope；422→400 的改写（L452-485）为对齐 OpenAI 客户端 SDK 的容错行为。
7. **鉴权分层的折中**：`auth_level(ADMIN_OPTIONAL)` 装饰器为主，但 HiCache attach/detach 等需要强制 admin key 的端点手工检查（L1851-1857 FIXME 记录了待重构原因）。

## 阅读建议

1. **先读 L2343-2357 的 launch_server docstring**——10 行讲清整个多进程拓扑，是理解 SGLang 的地图。
2. **按调用顺序读**：`launch_server` → `_setup_and_run_http_server` → `lifespan` → 任选一个 `/v1` 端点 → `TokenizerManager.generate_request`。跳过 70+ 管理端点细节（用到再查 §9 路由表）。
3. 对照 `python/sglang/srt/managers/io_struct.py` 看 `GenerateReqInput` 字段，理解 HTTP JSON 如何无缝变成 ZMQ 消息。
4. 想理解多 tokenizer 扩展，配合 `managers/multi_tokenizer_mixin.py` 的 `SenderWrapper`/`TokenizerWorker`；想理解 health check 语义，跳到 `tokenizer_manager.py` 的 `handle_loop`（L1697-1710）看 `last_receive_tstamp` 刷新点。
5. 速查全部路由：`rg "@app\.(get|post|put|api_route|websocket)" http_server.py`；注意两个**条件注册**路由（`DUMPER_SERVER_PORT`、`SGLANG_OLLAMA_ROOT_ROUTE`）与 5 个可被环境变量改写的 Ollama 路径不在静态路由表里。
6. 版本对比提示：`/get_*` 前缀端点全是废弃 shim（get_model_info/get_server_info/get_load/get_weight_version/get_remote_instance_transfer_engine_info），读老资料时注意映射到新端点。
7. 相关环境变量速查：`SGLANG_HEALTH_CHECK_TIMEOUT`（20）、`SGLANG_WAIT_WEIGHTS_READY_TIMEOUT`（120）、`SGLANG_WARMUP_TIMEOUT`、`SGLANG_TIMEOUT_KEEP_ALIVE`、`SGLANG_UVICORN_WORKER_HEALTHCHECK_TIMEOUT`、`DISABLE_OPENAPI_DOC`、`SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION`、`SGLANG_GRANIAN_PARENT_PID`、`DUMPER_SERVER_PORT`、`SGL_FORCE_SHUTDOWN`（后者在 tokenizer_manager 消费）。
