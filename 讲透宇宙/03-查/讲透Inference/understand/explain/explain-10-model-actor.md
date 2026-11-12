# explain-10 · core/model.py——ModelActor：每个副本一个的推理会话与生成通道

## 角色定位

`ModelActor`（`xinference/core/model.py:205`，`xo.StatelessActor`+`CancelMixin`，1424 行）是**每个模型副本一个**的会话层 actor，跑在 worker 为它孵化的独立子进程池里（进程标题被改成 `Model: <replica_uid>`，`:476-479`）。它是 REST 层与引擎模型对象之间唯一的桥：对上暴露 chat/generate/embedding/rerank/transcriptions/speech/text_to_image/text_to_video/world_generate/infer 等全套能力方法（`core/model.py:834-1418`），对下经 `__getattr__` 直接透传到 `self._model`（`:362-363`）。三大横切关注点都在这层实现：请求限流、指标埋点、OOM 自毁。

## 内部结构

`__init__`（`:259-326`）定下两个关键结构：`_lock`——**只有非批处理模型有锁**（`getattr(self._model, "allow_batch", False)` 为 True 则 None，`:286-288`），allow_batch 的模型（transformers 带调度器/vLLM）自己管并发，锁反而会把并发推理串成独占；`_metrics_labels` 九元标签组（model_type/uid/replica_index/name/engine/worker/format/quantization/gpu_index，`:303-315`）是所有指标的维度基数。两个重量级装饰器：`request_limit`（`:89-171`）实现并发计数限流——超限抛 "Rate limit reached"（REST 层翻译成 429），流式请求的计数**不在这里减**（生成器还没消费完，`:145-147`），由消费端调 `decrease_serve_count`（`:365-371`）归还；`oom_check`（`:174-202`）捕 OutOfMemoryError 转 `_handle_oom_error`（`:554-`，带重入门闸 `:559-561` 防 OOM 线程二次触发）。状态机 `_model_state`：registering→loading→ready→stopping，`_require_ready`（`:350-357`）是所有推理方法的守门员（loading 抛 ModelNotReadyError、其他坏态抛 RuntimeError）。

## 外部连接

上游：REST 层 `require_model` 经 supervisor `get_model` 拿到本 actor ref；worker 在 `launch_builtin_model` 里创建它（`core/worker.py:4538-4552`）并在引擎异步加载后调 `wait_for_load`（`:509-512`，模型侧 wait + 状态置 ready）。下游：`self._model` 是各引擎的模型对象（LLM/embedding/... 之一），`load()`（`:473-501`）在线程池里跑 `_model.load()` 并对 "busy or unavailable" 错误做 5 秒间隔重试（`:492-499`）；`stop()`（`:547-552`）优先 stop 其次 close。分布式协调三通道：`need_create_pools/set_pool_addresses/get_pool_addresses`（`:514-524`）对接 worker 的 per-GPU 池创建，`set_worker_addresses`（`:526`）与 `get_driver_info`（`:541-545`，注释：driver 恒为第一个 worker，持有分布式 store 等信息）支撑跨 worker 分片；`start_transfer_for_vllm`（`:374`）为 xavier 创建 TransferActor。`abort_request`（`:918-935`）两级取消：先 `CancelMixin._cancel_running_task` 杀运行中任务，再委托模型自己的 abort_request（BatchScheduler 的 `abort_request` 就是这么到达的）。

## 数据流

所有推理方法共享一条管道 `_call_wrapper`（`:750-829`）：①`_invoke` 按函数类型分派（协程直等 / 同步函数 `asyncio.to_thread` / world 生成这类同步子进程适配器用 `asyncio.shield` 保活到线程观察到取消并收割进程，`:754-771`）；②**无锁路径**（批处理模型）：返回值若是生成器，包成 `_to_generator/_to_async_gen`（`:614-701`）——逐 chunk 记 TTFT、抓最后一个 usage 块记 token 指标，json 序列化成 SSE bytes；③**有锁路径**（互斥模型）：在锁内启动生成器后立刻把 `(gen, stream_out, stop)` 三元组丢进 `_pending_requests` 队列（`:787-811`），后台任务 `_handle_pending_requests`（`:703-742`，post_create 时启动 `:333-335`）逐个泵生成器，把产出转投 stream_out 队列，消费侧再从队列读——**锁内只做"启动"，消费移出锁外**，这样 N 个流式请求共享一把锁还能交错产出；④非流式返回直接 json_dumps。`chat`（`:861-916`）的方法分派规则：有 `_batch_scheduler` 才保留 request_id（abort 需要），否则弹掉（`:869-874`）；`chat/async_chat` 二选一（`:868-888`）；finally 里对非流式响应解析 usage 记 completion 指标、TTFT（此时 TTFT≈总时长，`:890-916`）。

## 设计决策

①**双层并发模型**：allow_batch 模型完全信任引擎调度（无锁），互斥模型用"锁内启动+队列泵出"的技巧把流式与互斥调和——这是全文件最精巧的设计，`_handle_pending_requests` 的注释还点了 CPython issue 112182（StopIteration 被吞的坑）；②**指标即契约**：`request_limit` 装饰器把 request_total/errors_total/serve_count/duration 四件套埋进每个能力方法，指标名与 `core/metrics.py` 的定义严格对应；③**OOM 自毁而非恢复**：模型进程 OOM 后 CUDA 状态不可信，`_handle_oom_error` 上报状态后 `os._exit(1)` 让 worker 的 sub-pool monitor 走重建流程——把恢复交给进程边界；④`xo.generator` 装饰（`:832/:859`）标记方法返回生成器，xoscar 据此做流式 RPC 而非攒齐再回。

## 新人提示

加新能力方法的模板就是 `create_embedding`（`:937-949`）：`@request_limit` + `_require_ready` + hasattr 分派 + `_call_wrapper_json`。排查"流式请求计数不减导致限流误判"看三处：消费端是否正常走到 StopAsyncIteration、是否调了 `decrease_serve_count`、`_stream_out_generator` 是否因异常提前 break（`:740-742`）。`__pre_destroy__`（`:208-`）按模型类型做差异化清理（vLLM 销毁 transfer actor、pytorch 系释放 GPU），改引擎记得同步这里。调试时 `get_pending_requests_count`（`:1423`）+ `model_serve_count` 指标可以判断是"泵堵了"还是"限流卡了"。
