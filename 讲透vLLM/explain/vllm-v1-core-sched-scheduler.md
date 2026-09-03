# vllm/v1/core/sched/scheduler.py — Scheduler：vLLM 的心脏

> 源码：`vllm/v1/core/sched/scheduler.py`（约 3120 行）｜知识图谱 tags: `scheduler`, `continuous-batching`, `preemption`, `core-engine`

## 角色定位

`Scheduler` 是 v1 引擎**计算调度层**的核心——知识图谱上它 `inherits SchedulerInterface`，又被 `async_scheduler.AsyncScheduler` 继承（async scheduling 模式下调度器搬到 worker 侧重叠执行）。请求生命周期中，每个 engine step 的第一步就是 `scheduler.schedule()`：决定哪些请求、各推进多少 token，产出 `SchedulerOutput` 供 model executor 执行；执行后再由 `update_from_output()` 回写状态。它管理 KV cache 分配、prefix caching、抢占、多模态 encoder 输入、投机解码 draft token、KV/EC connector（P/D 分离与 encoder cache 传输）协同——vLLM 吞吐的奥秘大半在此。

## 内部结构

**队列与状态**（`__init__`，75–393 行）：
- `requests: dict[str, Request]`——全量请求注册表；
- `waiting: RequestQueue`（由 `create_request_queue(policy)` 构造，支持 FCFS / PRIORITY 两种 `SchedulingPolicy`）+ `skipped_waiting`（本步因异步依赖/约束被跳过的请求暂存）；
- `running: list[Request]`——**没有显式 FINISHED 队列**：完成态记录在 `Request.status`（`RequestStatus` 状态机）+ `finished_req_ids` set，每步冲刷通知 worker 释放；
- 配套：`KVCacheManager`（块分配/prefix cache）、scheduler 侧 `KVConnector`（P/D 分离时做元数据与异步加载决策）、`ECConnector`（encoder cache 远端传输）、`EncoderCacheManager`、spec decode 状态（`num_spec_tokens`、eagle lookahead）、`deferred_frees` FIFO（重叠 batch 下延迟释放块）。

**主方法**（按调用频率排序）：
- `schedule(throttle_prefills)`（509–1393 行，近 900 行的调度主体，见下）；
- `update_from_output(scheduler_output, model_runner_output)`（1810 行起）：消费采样结果——处理 KV 加载失败块回退、持久化 routed experts、推进每请求 `num_computed_tokens`/finish 判定、生成 `EngineCoreOutputs`；
- `_update_after_schedule()`：**调度即记账**——schedule 结束立刻乐观推进 `num_computed_tokens += num_scheduled_tokens`，使下一步能连续调度；spec token 被拒绝时在 update_from_output 里回调修正；
- `_preempt_request()`：抢占单个请求；
- `add_request` / `finish_requests` / `_free_request`：请求进出；
- `update_draft_token_ids`：接收 draft model 的投机 token。

**schedule() 两阶段结构**（务必先读 511–520 行 woosuk 的注释）：

> "调度器里没有 prefill phase 也没有 decode phase。每个请求只有 `num_computed_tokens` 和 `num_tokens_with_spec`。每一步，调度器试图给请求分配 token，让 `num_computed_tokens` 追上 `num_tokens_with_spec`。这个抽象足以统一覆盖 chunked prefill、prefix caching、speculative decoding 和未来的 jump decoding。"

- **阶段一 RUNNING**：遍历 `running`，`num_new_tokens = num_tokens_with_spec + placeholders - num_computed_tokens`，依次被 `token_budget`（调度预算）、`input_budget`（减去 draft 槽位）、`max_model_len`、mamba 块对齐、encoder 预算裁剪；然后 `kv_cache_manager.allocate_slots()`，**失败则抢占**：PRIORITY 策略选 `(priority, arrival_time)` 最大的受害者（并回滚其本步已记账的预算），FCFS 直接 `running.pop()` 队尾；循环直到能分配或自己也成受害者。
- **阶段二 WAITING**（仅本步无抢占时）：`_select_waiting_queue_for_scheduling()` 在 waiting/skipped_waiting 间选择 → prefix cache 查找（本地 `get_computed_blocks` + connector 的远端命中，两者做块对齐协调：远端严格更长则截断本地尾巴避免 CoW）→ 异步 KV 加载的请求标记 WAITING_FOR_REMOTE_KVS 跳过 → 否则按预算分配新 token；任何原因不能调度的请求 `prepend` 进 `step_skipped_waiting` 下步再试。
- 收口产出 `SchedulerOutput`：new/resumed/running 三类请求、`req_to_new_blocks`、`num_scheduled_tokens`、spec token、encoder input 索引、grammar 标记。

## 外部连接

- **imports**（30+ 模块）：`kv_cache_manager`、`request_queue`、`encoder_cache_manager`、`kv_connector/factory`（P/D）、`ec_connector`、`structured_output`（grammar bitmask）、`spec_decode`、`multimodal/encoder_budget`、`v1/request`（Request 状态机）。
- **被依赖**：EngineCore 经 `get_scheduler_cls()` 工厂实例化（只依赖 `SchedulerInterface` 抽象）；`AsyncScheduler` 继承并覆写 schedule 以适配 worker 侧重叠调度。

## 数据流

```
EngineCore.add_request → scheduler.add_request → requests + waiting
每步: schedule() ─读 running/waiting、写 allocate_slots─▶ SchedulerOutput
      → ModelExecutor.execute_model → ModelRunnerOutput
update_from_output(SchedulerOutput, ModelRunnerOutput)
      → 每请求推进/完成判定 → EngineCoreOutputs → 前端
```

## 关键设计决策

1. **统一 token 记账**：用"追赶 computed↔total"单一不变量替代 V0 的 phase 概念，是 v1 架构最重要的简化——chunked prefill 不过是"一次只追一部分"，spec decode 不过是"total 里含 draft"。
2. **抢占 = 全量重算**：`_preempt_request` 释放全部块、`num_computed_tokens = 0`、`waiting.prepend_request()` 回队首（保住 FCFS 位置）。没有 V0 的"保留 KV 部分重算"——简单性换来 prefix caching 下重算其实很便宜（命中即恢复）。async scheduling 下用 `num_stale_output_tokens`/`drop_stale_output` 标记在途过期输出，防止重采样错序。
3. **乐观推进 + 事后修正**：调度即记账使连续步骤无需等待执行结果；拒绝的 spec token 由 update_from_output 回调。这是 async scheduling（调度与执行重叠）的前提。
4. **Scheduler 侧/Worker 侧双角色 connector**：KVConnector 在 scheduler 侧只做"要不要等远端 KV"的决策（`get_num_new_matched_tokens`、异步加载门控），实际传输在 worker 侧——调度与 IO 解耦。
5. **`defer_block_free` 延迟释放**：多在途 batch 时，一步可能仍在写已结束请求的 KV 块，释放必须栅栏化（`sched_step_seq` FIFO），否则远端加载会读到脏块。

## 新人提示

- **别顺序通读 schedule() 的 900 行**：抓住"两阶段循环 + 预算裁剪链 + allocate 失败→抢占"骨架，encoder/mamba/spec 分支按需查。
- 核心不变量就一个：`num_computed_tokens ≤ num_tokens_with_spec`，所有功能都是围绕它的"追账"。
- 易混淆点①：`token_budget`（max_num_scheduled_tokens）与 `input_budget`（max_num_batched_tokens）是两本账，后者还要给 draft 槽位留量。
- 易混淆点②：请求"消失"的三种路径——正常 finish（update_from_output）、abort（finish_requests）、preempt（其实不消失，回 waiting）。
- 调试用 `make_stats()` 的 `SchedulerStats`（running/waiting 数、KV 利用率）是第一现场；`Request.record_event` 的时间线可还原每请求 TTFT/TPOT 与抢占历史。
