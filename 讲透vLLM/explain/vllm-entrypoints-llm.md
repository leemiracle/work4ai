# vllm/entrypoints/llm.py — 离线推理 LLM 类深解

## 角色定位

位于 **entrypoints（服务入口层）**。`LLM` 是**离线批量推理的同步门面（facade）**：一次构造（加载模型+分配 KV cache），随后 `generate()/chat()` 一把梭整批 prompt。图谱 tags 直白：`entry-point / offline-inference / facade`。它与在线服务的分工写在 docstring 里——离线用 `LLM`，在线 serving 用 `AsyncLLM`。在请求生命周期中，它同时扮演"用户 API"与"引擎驱动循环"（自己 step 引擎直到全部完成）。

## 内部结构

单一公开类 `LLM`，用 **mixin 组合**拆分离线能力（图谱 contains 边仅 `class:LLM`）：

```
class LLM(BeamSearchOfflineMixin, PoolingOfflineMixin, OfflineInferenceMixin)
```

- `OfflineInferenceMixin`（`entrypoints/offline_utils.py`）：`_run_completion/_run_chat/_add_*_requests/_run_engine` 等骨架；
- `PoolingOfflineMixin`：embed/classify/score 等 pooling 任务入口；
- `BeamSearchOfflineMixin`：beam search 离线路径。

`__init__` 做了三件事：①参数归一化——大量 kwargs（dtype/quantization/compilation_config/offload_* 等）拼成 **`EngineArgs`**，dict 自动转对应 config 实例（`_make_config`），`kv_transfer_config` dict 校验转 `KVTransferConfig`；②`LLMEngine.from_engine_args(...)` 创建 V1 引擎（`vllm/v1/engine/llm_engine.py`）；③缓存 `model_config/renderer/input_processor` 并 warmup chat 模板。防御性检查：单进程 `data_parallel_size>1` 直接报错（会 hang，指向多进程示例）；`worker_cls` 为类对象时 cloudpickle 序列化避免 pickle 失败。

## 外部连接

图谱 **25 条出边**：核心是 `engine/arg_utils.py`（EngineArgs）、`v1/engine/llm_engine.py`（LLMEngine）、`config/*`、`sampling_params.py`、`outputs.py`、`chat_utils.py`、`inputs/__init__.py`；还有 RL 向的 `distributed/weight_transfer/base.py`。入边 0（顶层门面无人依赖，`vllm/__init__.py` 延迟导出它）。注意它**不 import torch.distributed**——并行细节全被引擎封装。

## 数据流

```
prompts（str/TokensPrompt/multimodal dict）
  → renderer/tokenizer 预处理（多模态串行，警告 renderer_num_workers 无效）
  → llm_engine.add_request(...)（自动连续 request id）
  → _run_engine 循环 engine.step()（内部 batching/调度/PagedAttention）
  → 聚合 list[RequestOutput]（与输入同序，含 token ids/logprobs）
```

`enqueue()/wait_for_completion()` 把"入队"与"驱动"拆开，配合 `sleep(level=0)+wake_up(tags=["scheduling"])` 可保证全部请求入队后才开始调度（大 batch 控制场景）。

## 关键设计决策

1. **与 AsyncLLM 的关系**：两者都建立在同一套 V1 EngineCore 之上。`AsyncLLM` 是 asyncio 面向 HTTP 的流式客户端；`LLM` 则包一个同步 `LLMEngine`，`generate` 内部就是"add 全部 + step 到完成 + tqdm 进度条"。**同步/异步、离线/在线的差异收在 entrypoint 层，引擎内核共享**——这是 vLLM V1 架构的关键分层。
2. **运维/训练联动面**远超"generate"：`collective_rpc` 向所有 worker 广播方法调用（控制面）；`apply_model(func)` 直接在 worker 内的 nn.Module 上跑函数（RL 框架取 logits/改权重）；weight transfer 五连（`init_weight_transfer_engine/start_weight_update/update_weights/finish_weight_update/update_weight_version`）支撑在线 RL 权重同步（verl 等集成）。
3. **sleep/wake_up 分级**：level 0 暂停调度、level 1 权重下放 CPU 弃 KV、level 2 全弃——服务端换模型的显存腾挪原语。
4. **默认值**：`disable_log_stats` 强制 True（离线不需要周期日志）；`gpu_memory_utilization=0.92`。
5. **`__repr__` 缓存**：模型层级结构视图经 `collective_rpc("get_model_inspection")` 取回并缓存，避免重复 RPC。

## 新人提示

- 阅读切入点：`generate() → _run_completion → _run_engine`（去 offline_utils.py 读实现），一条线理解离线推理。
- 易混淆点：`LLM` 不是 nn.Module，`llm.llm_engine` 才连引擎；`generate()` 要求 `runner_type=="generate"`，embedding 模型要走 `PoolingOfflineMixin` 的 `embed()`；`chat()` 只是把 messages 经 chat 模板渲染后转 `generate`。
- `get_default_sampling_params()` 读的是模型 generation_config 的差量；传 `SamplingParams` 列表须与 prompts 等长配对。
- 想 swap 引擎做测试：`LLM(worker_cls=...)`，类会自动 cloudpickle。
