# 深度解析：`python/sglang/srt/managers/scheduler.py`

> 源码: python/sglang/srt/managers/scheduler.py @ commit ec075d8bc（全文 3909 行）

## 0. 这份文件在 SGLang 中的位置

`Scheduler` 是 SGLang 调度心脏：每个 TP/DP/PP rank 组合对应一个 scheduler 子进程，它持有 `waiting_queue`（待 prefill 请求）与 `running_batch`（连续批解码中的请求），负责**组批**（continuous batching 的 admission control）、**调用 ModelRunner 执行前向**、**管理 KV Cache 预算**（token 级别的分配、回收、retract），并通过 mixin 支持**分布式**（TP/PP/DP-attention/EP）与 **PD 分离部署**（prefill/decode 分离）。

一句话总结主链路：

```
run_scheduler_process()                     # 进程入口 (L3837)
  └─ Scheduler.__init__()                   # 30+ 个 init_* 组件 (L297)
  └─ run_event_loop()                       # (L1351)
       └─ dispatch_event_loop()             # 按 pp/pdmux/overlap/disagg 选循环 (L3749)
            └─ event_loop_overlap()         # 默认主循环 (L1399)
                 每步: recv_requests → process_input_requests → get_next_batch_to_run
                       → (get_new_batch_prefill | update_running_batch)
                       → run_batch → [下一拍] process_batch_result
```

文件可分为四大块：
1. **L287-1349：`Scheduler` 类的构造与初始化**（`__init__` + 约 30 个 `init_*` 方法）
2. **L1351-2347：请求接收与队列管理**（event loop 入口、dispatcher、`handle_generate_request`、waiting queue 各种 abort 策略）
3. **L2348-3134：组批与前向执行核心**（`get_next_batch_to_run` / `get_new_batch_prefill` / `update_running_batch` / `run_batch` / `process_batch_result`）
4. **L3135-3909：运维类控制面**（flush/abort/pause/LoRA/权重更新/内部状态）+ 模块级入口函数（`dispatch_event_loop` / `run_scheduler_process`）

---

## 1. 进程的诞生：从 `run_scheduler_process` 到 event loop

### 1.1 `run_scheduler_process()`（L3837-3909）

每个 GPU rank 由 `launch_tensor_parallel_group` 等入口 fork 出一个 scheduler 子进程，最终都落到这里：

- `configure_scheduler_process()`（L3780）：设置进程名（`sglang::scheduler_DP0_TP1` 形式）、logger 前缀、CPU 亲和性与 NUMA 绑定——调度进程对 CPU 抖动极敏感，这是延迟稳定性的第一道保障。
- 构造 `Scheduler` 实例后通过 `pipe_writer.send(scheduler.get_init_info())`（L3889）把 `max_total_num_tokens` / `max_req_input_len` 回传给父进程完成启动握手（`get_init_info` L1337）。
- event loop 阻塞运行直到 shutdown。任何异常会 `SIGQUIT` 父进程，可选 `SGLANG_KILLPG_ON_SCHEDULER_EXCEPTION` 直接 kill 整个进程组，避免兄弟 rank 刷屏 NCCL traceback（L3894-3904）。

### 1.2 `Scheduler` 类的 mixin 架构（L287-294）

```python
class Scheduler(
    SchedulerDisaggregationDecodeMixin,   # PD 分离 decode 侧事件循环
    SchedulerDisaggregationPrefillMixin,  # PD 分离 prefill 侧事件循环
    SchedulerMultiplexMixin,              # PD 复用（pdmux）
    SchedulerPPMixin,                     # 流水线并行事件循环
    SchedulerDllmMixin,                   # 扩散 LLM
    SchedulerMlxOverlapMixin,             # MLX 后端 overlap
):
```

正文里的 `event_loop_normal` / `event_loop_overlap` 只是一族循环中的两个；`dispatch_event_loop()`（L3749-3777）按 `disaggregation_mode × pp_size × enable_overlap` 组合出 10 种循环变体（如 `event_loop_pp_disagg_prefill`、`event_loop_overlap_disagg_decode`）。这体现了本文件的第一个设计模式：**用 mixin + dispatch 把"调度骨架不变、各模式改写个别步骤"的组合爆炸收敛进子类**。

### 1.3 `__init__` 的 init 链（L297-558）

构造函数是一长串组件装配，关键几步（按行号）：

| 步骤 | 行号 | 作用 |
|---|---|---|
| `init_soft_watchdog` | L313 | 最先启动：watchdog 守护线程会读 `forward_ct` / `cur_batch`，必须在一切之前初始化 |
| `ParallelState` 装配 | L357-375 | 把 tp/pp/dp/attn_tp/attn_cp/moe_ep/moe_dp 全部 rank 信息收拢为 `self.ps`，后续组件统一从这取 |
| `init_ipc_channels` | L394 | 与 TokenizerManager / Detokenizer 的 ZMQ 通道 |
| `init_model_worker` | L420 | 拉起 `TpModelWorker`（内含 ModelRunner），投机解码时还会 `maybe_init_draft_worker`（L727） |
| `kv_cache_builder.build_kv_cache` | L426-453 | 构建内存池三件套：`req_to_token_pool`（req→KV slot 映射表）、`token_to_kv_pool_allocator`（KV token 分配器）、`tree_cache`（radix 前缀缓存），并回填 `max_total_num_tokens` 等预算上限 |
| `init_running_status` | L490 | **核心数据结构登场**：`waiting_queue`、`running_batch`、`cur_batch`、`last_batch`（详见 §3.1） |
| `init_chunked_prefill` | L493 | chunked prefill 参数（详见 §4.3） |
| `init_schedule_policy` | L508 | `SchedulePolicy`（排队策略）+ `PrefillDelayer` + `NewTokenRatioTracker` |
| `init_disaggregation` | L517 | PD 分离队列 |
| `init_overlap` | L520 | 双 CUDA stream + `FutureMap`（详见 §6.1） |
| `init_request_dispatcher` | L531 | 类型→handler 分发表 |
| 一票组件 init | L528-556 | watchdog/权重更新/LoRA/grammar/receiver/DP-attention 适配器/pool 统计/不变量检查/KV 事件发布/负载查询/输出流式化/**批结果处理器** |

注意 `self.is_initializing` 标志（L309/L558）包裹整个构造，供 watchdog 区分"启动慢"与"卡死"。

---

## 2. 两条 event loop：normal 与 overlap

### 2.1 `run_event_loop()`（L1351-1369）

创建 **`schedule_stream`**（优先级 0 的 CUDA stream）并把整个调度循环放进该 stream context——这是理解 overlap 调度的钥匙：**调度侧的 GPU 写操作（如 `alloc` 写 `req_to_token`、FutureMap resolve）运行在 schedule stream，而模型前向运行在 forward stream**，两者并行。CPU 平台把 `synchronize` 打成 no-op（L1364-1365）。

### 2.2 `event_loop_normal()`（L1372-1396）——同步版骨架

```python
while True:
    recv_reqs = self.request_receiver.recv_requests()   # 收请求（非阻塞，每次最多 max_recv_per_poll）
    self.process_input_requests(recv_reqs)              # 分发进 waiting_queue 等
    if self._engine_paused: continue                    # pause_generation 时只收不跑
    batch = self.get_next_batch_to_run()                # ★ 组批决策
    self.cur_batch = batch
    if batch:
        result = self.run_batch(batch)                  # ★ 发起前向
        self.process_batch_result(batch, result)        # ★ 同步处理输出（等 GPU 完成）
    else:
        self.on_idle()                                  # 空闲自检
    self.last_batch = batch
```

同步版每步都要等前向 + 拷贝完成才进入下一轮调度，CPU 调度时间（组批、tensor 构造、allocate）完全串行在 GPU 空闲期里。

### 2.3 `event_loop_overlap()`（L1399-1455）——生产默认

核心改造有三点：

1. **`result_queue` 延迟一拍**（L1401-1403）：`run_batch` 只发起前向（异步），把 `(batch.copy(), batch_result)` 压进 deque；**下一轮循环**才 `pop_and_process()` 处理上一批的输出。于是"本批 GPU 计算"与"上批 CPU 后处理 + 本批 CPU 调度"重叠。
2. **WAR barrier**（L1417-1419）：`schedule_stream.wait_stream(self.forward_stream)`——本轮调度要写的共享 GPU 缓冲（如 `req_to_token` 表、FutureMap buffer）必须等上一批前向的读操作结束，避免 write-after-read 竞态。仅 CUDA 启用（L1367）。
3. **sampling 延迟触发**（L1446-1449）：`launch_batch_sample_if_needed`（L3053）——带 grammar（structured output）时采样依赖上一批的 bitmask 结果，必须等上批 `process_batch_result` 执行完才能 launch 本批的采样，所以被排到循环末尾；同时它会释放 `delay_sample_func` 闭包引用的 `next_token_logits`/`vocab_mask` 大张量，注释里明确指出不释放会造成"steady VRAM leak"（L3074-3082）。

**overlap 关闭开关**：`is_disable_overlap_for_batch()`（L1457-1488）在两种情况退回同步语义（当轮立即 `pop_and_process`）：
- 环境变量 `SGLANG_DISABLE_CONSECUTIVE_PREFILL_OVERLAP` 且本批与上批都是 extend（连续 prefill 关 overlap 换首批 TTFT）；
- spec-v2 + grammar + decode 且 result_queue 非空（功能尚不支持）。

DP-attention 模式下用全局同步过的 `is_extend_in_batch` 判断，保证所有 DP rank 做出**相同的 overlap 决策**，否则集体通信会死锁（L1460-1462 注释）。

### 2.4 一拍 overlap 迭代的时间线

把 L1410-1455 的一次循环展开成时间线（T0 为循环起点），可以更直观地看到"谁在等谁"：

```
GPU  schedule stream        forward stream                 copy stream
     ─────────────────      ─────────────────────────      ──────────────
T0   WAR barrier: 等 ────►  [上批 N-1 前向仍在读共享缓冲]
T1   get_next_batch_to_run
       ├ filter/merge（CPU）
       ├ alloc KV（GPU 写 req_to_token）
       └ prepare_for_extend/decode
T2   run_batch:                                      [本批 N 前向启动]
       future_map.resolve_future ──┐                 （与 T3 的 CPU 工作
       set_input_ids_sentinel      │                  完全并行）
       publish(上批哨兵值)  ◄──────┼──── [上批 N-1 采样已完成]
T3   pop_and_process:                                    [上批 N-1 的
       process_batch_result(N-1)      │  copy_done ───►  D2H 拷贝]
       （copy_done.synchronize 等 ────┘
        待拷贝流完成才真正拿到 token）
T4   launch_batch_sample_if_needed(N)（grammar 时延迟采样）
T5   last_batch = batch; 进入下一轮
```

三个关键观察：
1. **CPU 的 T1/T3 与 GPU 的 T2 前向并行**——这是 overlap 的全部收益来源；
2. `process_batch_result` 是唯一必须停下等 GPU 的点（`copy_done.synchronize()`，batch_result_processor.py L593/L186），且它等的是**上一批**，等待窗口被本批前向覆盖；
3. 采样（T4）可能被推迟到循环末尾，因为 grammar bitmask 依赖上一批的 process 结果（L1447 注释）。

### 2.5 PP / PD 分离 / pdmux 的循环变体

`dispatch_event_loop`（L3749）选择的其余循环变体都遵循同样的骨架，差异集中在三处：

| 变体 | 定义处 | 与主干的差异 |
|---|---|---|
| `event_loop_pp` | SchedulerPPMixin | 跑 microbatch 批次（`self.running_mbs`），首/中间/末 rank 的输入输出处理不同；chunked 请求可能跨 microbatch 存活（见 L2390-2393 的丢弃逻辑） |
| `event_loop_normal_disagg_prefill` | DisaggregationPrefillMixin | prefill 完成后不进本地 running_batch，而是通过 KV sender 把 KV 发给 decode 实例（`start_send_idx/tmp_end_idx` 分块发送） |
| `event_loop_overlap_disagg_decode` | DisaggregationDecodeMixin | 收 KV 代替 prefill：`disagg_decode_prealloc_queue`（预分配 KV 行）→ `disagg_decode_transfer_queue`（等 KV 传完）→ 组 `PREBUILT` 模式批直接 decode（`_run_batch_prebuilt` L2923-2924） |
| `event_loop_pdmux` | SchedulerMultiplexMixin | prefill/decode 双角色时间片轮转，`SPLIT_PREFILL` 模式配合 `forward_batch_split_prefill`（L2982-2985） |

`init_disaggregation`（L992-1123）负责装配这些模式需要的队列与 bootstrap 元数据缓冲（`MetadataBuffers` / `ReqToMetadataIdxAllocator`）。主链路阅读可以先无视这些分支，但要知道：**所有变体都复用 `get_next_batch_to_run` 之后的 run_batch/process_batch_result 骨架**。

---

## 3. 请求如何进入调度器

### 3.1 四个关键状态容器（`init_running_status` L853-870）

```python
self.waiting_queue: List[Req] = []          # 已验证、待 prefill 的请求
self.running_batch: ScheduleBatch           # 连续批解码中的批（初始为空批）
self.cur_batch / self.last_batch            # 本轮/上一轮实际下发的批
self.chunked_req: Optional[Req]             # 正在被分块的 prefill 请求（全局唯一）
```

另有 `return_health_check_ipcs`（健康检查应答队列）与 `flush_wrapper` / `session_controller` 等组件引用。

### 3.2 `process_input_requests()`（L1490-1513）

每轮循环把收到的 IPC 消息逐条交给 `self._request_dispatcher`——一个 `TypeBasedDispatcher`（L1224-1319 注册了 40+ 条类型映射：generate/embedding/abort/flush/profile/权重更新/LoRA/load 查询……）。产出若非 None 则通过 `ipc_channels.send_to_tokenizer` 回发。两个细节：

- **健康检查短路**（L1494-1501）：服务忙时健康检查请求不进 pipeline，直接登记 ipc 句柄，由 `maybe_send_health_check_signal`（L3113）在批处理间隙应答——防止长 prefill 卡死 HTTP 健康探针。
- `flush_wrapper.check_pending()` 处理挂起的 cache 清理。

### 3.3 `handle_generate_request()`（L1845-2068）——单请求准入

这是 dispatcher 中最重的 handler，做一次完整的**入口验证与 Req 构造**：

1. 三路分支：普通请求构造 `Req`（L1865-1904，透传 rid/采样参数/logprob/LoRA/session/优先级/disagg bootstrap 等约 30 个字段）；session 请求走 `session_controller`（L1925-1943）；session 不存在则立刻 abort 入队。
2. PD 分离模式下缺 `bootstrap_room` 直接 400（L1907-1923）。
3. 多模态：展开 image token 为 pad token（`_try_apply_padded_mm_input_ids` L1795 或 `pad_input_ids_func`）、计算 mrope positions（L1817），展开后超长则 abort（L1994-2003）。
4. `init_req_max_new_tokens`（L1699）裁剪 `max_new_tokens` 不超过上下文余量。
5. `validate_input_length` 校验 prompt 长度，`logprob_start_len` 归一化（L2019-2043）。
6. 最后交给 grammar manager：带约束的请求先进 grammar 编译队列，就绪后由 `_get_new_batch_prefill_raw` 开头取回（L2499-2503）；普通请求直接 `_add_request_to_queue`。

### 3.4 `_add_request_to_queue()`（L2103-2125）与三道闸门

按部署模式分流：普通模式做 `abort_on_queued_limit → prefetch_kvcache → waiting_queue.append`；prefill 分离模式进 bootstrap 队列；decode 分离模式进 prealloc 队列。前面的防线包括：

- `_set_or_validate_priority`（L2127）：优先级调度关闭却带 priority 的请求可配置为直接拒绝。
- `_abort_on_queued_limit`（L2152-2199）：`waiting_queue` 超过 `max_queued_requests` 时默认拒绝新请求；优先级模式下改为驱逐队内优先级最低者（平局先踢更新者）。
- `_abort_on_waiting_timeout`（L2201）与 `_abort_on_running_timeout`（L1321）：两级超时兜底（`SGLANG_REQ_WAITING_TIMEOUT` / `SGLANG_REQ_RUNNING_TIMEOUT`），每次组批前在 `get_next_batch_to_run` 开头执行（L2351-2352）。

---

## 4. 组批核心：从 waiting_queue 到一个可运行的 batch

### 4.1 `get_next_batch_to_run()`（L2348-2469）——每步的决策入口

这是调度器最重要的 120 行，逐步分解：

**Step 1：超时清理**（L2351-2352）如上。

**Step 2：chunked 请求隔离**（L2357-2370）。把 `self.chunked_req`（以及 dLLM staging 请求）从即将合并的 last_batch 中排除（`chunked_req_to_exclude` 集合），原因是 chunked 请求**没完成 prefill，不能进 running_batch**。若它上一轮真的被调度过（`_chunked_req_scheduled_last_iter`），先 `stash_chunked_request`（L2309：`maybe_cache_unfinished_req` 把已算前缀插入 radix cache 换 evictable 配额）。`_chunked_req_scheduled_last_iter` 标志的注释（L891-898）值得读：它防止 hybrid-SWA 压力下 `add_chunked_req` 早退导致的 double-free。

**Step 3：merge 上一个 extend 批进 running_batch**（L2385-2412）。若 `last_batch` 是 extend（prefill）批：先 `filter_batch` 剔除已完成/chunked 请求，batch 变小则清 `batch_is_full`；非空则与 `running_batch` `merge_batch`。这就是 continuous batching 的 prefill→decode 转换点：**上一轮新 prefill 的请求从此成为 decoding 常驻批的一员**。

**Step 4：尝试组新 prefill 批**（L2424-2427）：`get_new_batch_prefill()`（dLLM 有专用变体）。返回非 None 则"prefill 优先"直接下发（L2442-2444）——SGLang 的调度优先级是 **new prefill > decode**（TTFT 优先哲学，与 vLLM 默认相反）。

**Step 5：否则推进 decode**（L2445-2454）：`update_running_batch(running_batch)` 做 retract 检查 + `prepare_for_decode`。

**Step 6：DP-attention 同步**（L2429-2440, L2457-2459）：`require_mlp_sync` 时各 DP rank 要对齐"本轮是否有 prefill"，通过 `dp_attn_adapter.maybe_prepare_mlp_sync_batch` 广播决策，保证 MoE 层 all-reduce 的批形状一致（spec+dp-attn 时还要保证 prefill/decode 不混批，L2435-2438 注释）。

**Step 7：ngram embedding 表填充**（L2462）与调度时间打点。

### 4.2 `_get_new_batch_prefill_raw()`（L2496-2735）——prefill 的 admission control

这是组批策略的主战场，流程：

1. **grammar 就绪回灌**（L2499-2503）与 HiCache 事件检查。
2. **快速退出**（L2512-2530）：`batch_is_full`（running 批已满的缓存标志，避免每轮重复检查）或 waiting_queue 空且无 chunked_req → None；`get_num_allocatable_reqs`（L2471：`pp_max_micro_batch_size - running_bs` 再夹 `req_to_token_pool.available_size()`）≤0 时置 `batch_is_full=True` 返回。注意 chunked_req 不受此限——PP 下跨 microbatch 的 chunked 请求必须永远放行，否则内存泄漏（L2519-2523 长注释）。
3. **排队策略排序**（L2533）：`self.policy.calc_priority(waiting_queue, running_batch)`。`SchedulePolicy`（schedule_policy.py L141）支持 `fcfs`（默认）/`lpm`（最长前缀优先，>128 请求自动退化 FCFS）/`dfs-weight`/`lof`（最长输出优先）/`random`/`routing-key`，优先级调度叠加在排序之上；LPM 还带 **in-batch prefix caching 去重**——多个请求共享同一短前缀时只先放一个，提高缓存命中率（schedule_policy.py L227-273）。
4. **动态 chunk 尺寸**（L2541-2547）：PP 场景 `predict_next_chunk_size` 根据历史长度预测下一 chunk 大小。
5. **构造 `PrefillAdder`**（L2550-2566，见 §5）并先喂 chunked 请求（`add_chunked_req`，L2568-2573）。
6. **主循环**（L2587-2650）：遍历排序后的 waiting_queue，逐个 `adder.add_one_req(req)`：
   - LoRA 请求过 `_can_schedule_lora_req`（L2737：drainer 状态 + `max_loras_per_batch` 限制 + 可选 overlap 加载）；
   - 每轮检查 `batch_is_full`（can_run_list 达到可分配请求数上限）；优先级抢占模式下满批时可尝试 `adder.preempt_to_schedule`（L2601-2605）；
   - HiCache storage 检查 prefetch 进度（L2607-2615）；
   - `req.init_next_round_input(tree_cache)` 做 radix 前缀匹配（详见 schedule_batch 解析 §4.2）；
   - `add_one_req` 返回 `NO_TOKEN` → 置 `batch_is_full` 并 break；未入批成功且持有新分配 mamba slot 的请求要回滚释放（L2640-2649 防泄漏注释）。
7. **收尾**（L2652-2735）：从 waiting_queue 移除 can_run_list；`new_chunked_req` 登记为 `self.chunked_req` 且 `inflight_middle_chunks += 1`；`ScheduleBatch.init_new(...)` + `prepare_for_extend()`（KV 分配在这里发生）；记录 `PrefillStats`；**mixed chunked prefill** 分支（L2715-2731）：`is_mixed_chunk` 且无 logprob 时，把 running_batch 的 decode 请求 `mix_with_running` 拼进本 prefill 批（`ForwardMode.MIXED`），让 prefill 与 decode 同批执行，同时 running_batch 被替换成空批。

### 4.3 chunked prefill 的状态机（`init_chunked_prefill` L872-917）

- `chunked_prefill_size`：每步 prefill 的 token 上限（多模态 + Transformers 后端自动禁用，L877-887）。
- `self.chunked_req` 全局唯一：同一时刻只允许一个请求处于"分块中"。
- `is_mixed_chunk`：chunk 与 decode 混批开关。
- `enable_dynamic_chunking`：PP 专属的动态 chunk（L905-917）。

一个 8192-token prompt、chunk=2048 的请求完整走一遍状态机（配合 `inflight_middle_chunks` 计数，schedule_batch.py L826-829 / L271-276）：

```
轮次  chunked_req   add_chunked_req 行为            can_run_list      inflight_middle_chunks
T0    None          add_one_req 触发截断→new_chunked_req  [req(2048)]   0 → 1（入队时 L2672）
T1    req           优先续块 2048                     [req(2048)]     1 → 2（T0 结果处理时 2696-2699 递减？）
T2    req           优先续块 2048                     [req(2048)]     ...
T3    req           最后一块 1808，add_chunked_req 返回 None（不再截断，L699）
T4    None          req 完成全部 prefill，进入 running_batch merge
```

要点：`stash_chunked_request`（L2309）在每轮 T1+ 开头把"上一块已算出的 KV"插入 radix cache（`maybe_cache_unfinished_req(chunked=True)`），这样即使中途 retract，已算的块也不会浪费；而 `contains_last_prefill_chunk`（L2688-2690）标记本批是否含某 chunked 请求的最后一块，供下游决定何时把首 token 流出去。

### 4.3.1 组批决策的完整判据清单（速查）

`_get_new_batch_prefill_raw` 会因以下任一条件停止向批内加请求（按检查顺序）：

| 判据 | 位置 | 效果 |
|---|---|---|
| grammar 尚未编译完 | L2499 | 就绪的回灌队列，未就绪的等下轮 |
| `batch_is_full` 或 waiting_queue 空 | L2512 | 直接返回 None |
| `get_num_allocatable_reqs <= 0` | L2524 | 置 batch_is_full，返回 None |
| LoRA：drainer 排空中 / 超 max_loras_per_batch | L2588, L2737 | skip 该请求 |
| can_run_list 达到可分配请求数 | L2592 | 置 batch_is_full（优先级抢占可突破） |
| HiCache prefetch 未完成 | L2607 | skip 该请求（不 break） |
| `adder.add_one_req` → NO_TOKEN | L2628 | 置 batch_is_full，break |
| `adder.add_one_req` → OTHER | L2627 | 直接 break（预算/上限类原因） |
| preempt 失败 | L2601 | break |

### 4.4 `update_running_batch()`（L2765-2849）——decode 的 admission control

```
filter_batch（剔完成/被 retract）→ HiCache flush → check_decode_mem() 判定下轮 KV 是否够
   ├─ 够：new_token_ratio_tracker.decay_step()
   └─ 不够：retract_decode() ★
最后 prepare_for_decode()（L2848）
```

**retract（回退）机制**是 SGLang 独有的内存压力应对：decode 中若连下一个 token 的 KV 都分配不出来（`check_decode_mem` → `new_tokens_required_next_decode` 估算，见 schedule_batch 解析 §5.3），不 crash 而是按"输出越多越先被踢"的排序（`retract_decode` schedule_batch.py L2308-2370）把请求逐个踢出 running_batch：释放其全部 KV（**不插入 radix tree**，因为立刻要用这块空间）、`reset_for_retract` 重置状态、重新 `_add_request_to_queue(is_retracted=True)` 排队——下次会重新 prefill（好在 radix cache 里可能还留着它的前缀）。连最后一个请求都放不下时优雅 abort（L2344-2361）并重算 `new_token_ratio`（retract 后新增 token 比例估计更保守）。scheduler 侧负责打日志、metrics 上报和向 tokenizer 发 AbortReq（L2800-2834）。

---

## 5. PrefillAdder：token 预算的会计（schedule_policy.py L405-1036）

虽然定义在 `schedule_policy.py`，但它是 §4.2 的直接协作者，必须一起读。它把"这个 batch 还能塞多少"建模为一组递减预算：

| 预算字段 | 含义 | 初值来源 |
|---|---|---|
| `rem_total_tokens` | KV 池总余量（available+evictable−offset） | 实时 property（L496-513），减去 running 批未来 token 的估算 offset（`_get_running_request_total_token_offset`：`min(max_new_tokens−已生成, CLIP_MAX_NEW_TOKENS) × new_token_ratio`） |
| `cur_rem_tokens` | 当前轮 token 余量（不含 max_new 预留） | 同上但不扣 max_new |
| `rem_input_tokens` | 本批 prefill token 上限（`max_prefill_tokens`） | server_args 推导 |
| `rem_chunk_tokens` | 本 chunk 剩余（chunked_prefill_size） | 可被动态 chunk 覆盖 |
| `rem_swa_tokens` | hybrid-SWA 池余量（滑动窗口专属预算，L515-521） | 实时 property |
| `rem_dllm_tokens` | 扩散 LLM 块预算 | `max_running_reqs × block_size` |

`add_one_req`（L813-965）的三段决策：
1. **前置检查**：prefill delayer 协商（分布式延迟 prefill 以对齐 DP rank）、CP 限制单请求、`prefill_max_requests`、`ignore_eos` 走专门的保守路径 `add_one_req_ignore_eos`（L718：维护 req_states 排序列表模拟未来 token 释放）。
2. **预算判定**：`total_tokens = extend_input_len + max_new + page_size`（L843-855，page 对齐余量）；页分配下用 `ceil_paged_tokens`；`_lock_node` 临时锁住 radix 节点后**复查** `rem_total_tokens`（锁后 evictable 可能减少，L872-875）。HiCache 命中走 `init_load_back` 把宿主机 KV 拉回 GPU 并更新 prefix（L882-893）。
3. **三种入批结局**：非 chunked 直接进 `can_run_list` 并 `_update_prefill_budget`（扣减全部预算）；需要分块则截断 `trunc_len = rem_chunk_tokens // page_size * page_size`（确定性推理还要按 `truncation_align_size` 对齐，L940-946），请求进 `can_run_list` 同时登记为 `new_chunked_req`，预算只扣本 chunk；预算耗尽返回 `NO_TOKEN`/`OTHER` 让 scheduler 停止扫描。

`budget_state()`（L563-580）给出三态返回值 `CONTINUE/NO_TOKEN/OTHER`，是 scheduler 主循环 break 的唯一依据。

另有 `preempt_to_schedule`（L967-1036）：优先级抢占——高优请求差多少 token 就从 running 批里挑低优请求释放（`release_req` + 回收其预算 offset），凑够即提交。注释（L975-980）解释了为什么必须跳过"KV 已释放但尚未 filter 出批"的两段式完成请求：避免 double-free。

---

## 6. `run_batch()` 与 overlap 的底层机制

### 6.1 `init_overlap()`（L1125-1154）建立的三件套

- **双 stream**：`schedule_stream`（调度写）+ `forward_stream`（模型前向，来自 ModelRunner）+ `copy_stream`（D2H 结果拷贝）。
- **`FutureMap`**（`overlap_utils.py` L74）：按 `req_pool_idx` 索引的跨迭代中继缓冲。前向完成后 `publish(future_indices, seq_lens+1)` 写入新 seq_lens/采样 token；下一轮调度 `resolve_future(batch)` 把 `batch.input_ids` 里的负数哨兵（`set_input_ids_sentinel` L2977 写入）替换成真实 token——**调度器在 GPU 采样完成之前就能用"未来值占位符"组好下一批**。spec-v2 场景还有 pinned host 拷贝 + 专用 D2H stream（L108-119）把 seq_lens 拉回 CPU 供调度用。
- **`batch_record_buf`（2 槽环形）**（L1153）：见下。

### 6.2 `run_batch()`（L2907-3036）逐段读

generation 路径 + overlap 分支（L2928-2981）：

1. `future_map.resolve_seq_lens_cpu(batch)`：spec-v2 的 seq_lens 只有前向知道（接受长度不确定），从 buf 拉。
2. `_overlap_forward_isolation(batch)`（L2866-2905）：把 ScheduleBatch 变成"一次前向的事务"——
   - **快照**：spec-v2 会在前向中改写 `forward_mode/input_ids/seq_lens/spec_info`，进出各一次全字段 snapshot/restore；
   - **sampling_info 替身**：换成 `copy_for_forward()`（不携带 orchestrator），防止 V2 多次 `init_new` 重复累积惩罚；
   - **pin 2 迭代**：`record_batch_in_overlap`（L2851-2864）把 `(batch, 字段快照列表)` 存进 `batch_record_buf` 双槽——**纯粹为了骗过 torch caching allocator**：schedule stream 产出的 GPU tensor 若被 Python GC 回收，其显存可能在前向 stream 还在读时被复用；持引用两轮即可保证生命期跨过前向完成。GenerationBatchResult 还能通过 `extra_keep_alive_refs` 追加引用（L2957-2960）。
3. `forward_stream.wait_stream(schedule_stream)` 后进入 `forward_stream_ctx` 调 `model_worker.forward_batch_generation(batch)`（L2945-2951）——真正的模型执行在 TpModelWorker/ModelRunner。
4. **非 spec**：前向返回立刻 `future_map.publish(future_indices, batch.seq_lens+1)` + `stash`（暂存 next_token_ids）+ `batch_result.copy_to_cpu()`（L2952-2973，内部用 copy_stream 异步拷贝，`copy_done` Event 供下游 synchronize）。**spec-v2** 则通过 `on_publish` 回调让 scheduler 侧准备与 draft_extend 重叠（L2939-2943）。
5. `set_input_ids_sentinel`（L2977）把 input_ids 替换为负数哨兵，交由下轮 resolve。

非 overlap 分支（L2986-2999）简单得多：直接前向、同步把 `next_token_ids` 写回 `batch.input_ids`、`update_cache_from_scheduler`。

此外 L3004-3013 是一个容易忽略的正确性细节：overlap 会改写 batch 字段，所以 `return_logprob` 时必须**此刻**把 `extend_input_len_per_req` 等拷进 result，后处理才能拿到正确值。

### 6.3 `process_batch_result()`（L3084-3111）

按 forward_mode 分派给 `batch_result_processor`（scheduler_components/batch_result_processor.py）：
- decode → `process_batch_result_decode`（该文件 L588）：`copy_done.synchronize()` 等拷贝 → 归一化输出 → 逐 req：`output_ids.append(next_token_id)` → `update_finish_state`（stop 条件判定）→ 完成则 `release_kv_cache`（把 KV 插回 radix tree、释放 req slot）并 `_handle_finished_req`（stream 输出 + completion 打点），未完成且是 prefill 批则 `maybe_cache_unfinished_req` → grammar/logprob/hidden states 处理 → `output_streamer.stream_output`（`stream_interval` 控制输出粒度）。
- extend → `process_batch_result_prefill`（该文件 L178）：首 token 落袋、chunked 请求 `inflight_middle_chunks` 递减并跳过流式输出。
- 另有 prebuilt（PD decode）/idle/dLLM 变体。收尾统一做 metrics、FPM、多模态输入清理与心跳。

---

## 7. 空闲与自愈

- `on_idle()`（L3164-3195）：完全空闲时做内存泄漏检查（`invariant_checker._check_all_pools`）、tree cache 一致性检查、每 30s 打 idle 指标、发布 KV 事件、重置 new_token_ratio 与 device timer，最后 `maybe_sleep_on_idle` 省电。
- `is_fully_idle()`（L3197-3245）：空闲判定非常保守——running/cur/last batch、chunked_req、result_queue（overlap 在途批）、PP 各 microbatch、waiting_queue，甚至 grammar 队列、disagg bootstrap/prealloc/transfer 队列、HiCache 异步 in-flight 操作都要清零。注释点明原因：`flush_cache` 等**破坏性操作**只有在所有 in-flight 异步操作排干后才是安全的。
- watchdog（`init_watch_dog_memory_saver_input_blocker` L969）：超时 dump 线程栈并可选 coredump，配合 `debug-distributed-hang` 排障。

---

## 8. 与其他模块的交互

| 对端 | 通道 | 内容 |
|---|---|---|
| TokenizerManager | ZMQ（`init_ipc_channels` L591 / `init_request_receiver` L1550） | 收 TokenizedGenerateReqInput 等；发 BatchOutput/AbortReq/健康检查。多模态大 payload 走 CUDA-IPC 或 mm_receiver |
| TpModelWorker / ModelRunner | 进程内调用 | `forward_batch_generation` / `forward_batch_embedding`；Scheduler 拿到的 `batch_result` 是 `GenerationBatchResult` |
| ScheduleBatch / Req（schedule_batch.py） | 进程内 | 组批的全部数据结构；`prepare_for_extend/decode` 完成 KV 分配 |
| PrefillAdder / SchedulePolicy（schedule_policy.py） | 进程内 | admission control 与排序 |
| mem_cache（req_to_token_pool / token_to_kv_pool_allocator / tree_cache） | 进程内 | KV 预算的全部事实来源 |
| FutureMap（managers/overlap_utils.py） | GPU buffer | overlap 跨迭代 relay |
| disaggregation/*（mixin） | 各队列 + transfer backend | PD 分离 bootstrap/prealloc/transfer |
| dp_attn adapter | NCCL | DP-attention 的 mlp sync / global batch 形状对齐 |
| GrammarManager（constrained/） | grammar 队列 | 约束解码编译异步化 |
| SchedulerComponents（scheduler_components/*） | 组合 | metrics_reporter / profiler / weight_updater / lora_drainer / pool_stats_observer / invariant_checker / kv_events_publisher / load_inquirer / output_streamer / batch_result_processor 等十余个解耦组件 |

这套"Scheduler 大类 + 组件类"结构是本文件的可维护性核心：主循环保持 ~50 行，所有旁支逻辑（打点、权重、LoRA、flush）都外置成 `init_xxx()` 装配的组件。

---

## 9. 关键设计决策

1. **Overlap 调度 = 双 stream + 延迟一拍 + FutureMap 哨兵**。CPU 调度（组批、分配、tensor 构造）与 GPU 前向并行；采样结果通过"负数哨兵 + 按 req_pool_idx 中继"在下一轮前才落地。代价是大量的正确性补偿代码：WAR barrier、`batch_record_buf` 防 GC、`copy()` 快照、`extend_input_len_per_req` 提前拷贝、两段式请求完成（`to_finish` → `finished_reason`，schedule_batch.py L780-783 注释：中途直接置 finished 会导致请求被 filter 却永不回复）。
2. **Token 级而非请求级的 admission control**。PrefillAdder 同时刻画 KV 余量（含 evictable）、每批 prefill 上限、chunk 上限、SWA 独立预算，并为每个 running 请求按 `new_token_ratio`（动态估计的"平均还会生成多少 token"）预扣未来 KV——宁可保守也不让 decode OOM。
3. **Retract 优先于 crash**。decode 内存不足时回退请求而非失败；配合 radix cache，被回退请求重 prefill 的代价被前缀命中大幅摊薄。`new_token_ratio` 在 retract 后立即收紧。
4. **Prefill 优先 + chunked prefill + mixed chunk**。新请求优先获得计算（低 TTFT），超长 prompt 被切成固定 token 预算的 chunk 逐拍处理，chunk 与 decode 可混批（MIXED）填满算力。

### 9.1 与 vLLM 调度器的直观对比（帮助迁移理解）

| 维度 | SGLang Scheduler | vLLM Scheduler（v0/V1） |
|---|---|---|
| prefill/decode 关系 | prefill 优先抢占当拍，`running_batch` 常驻 | 默认 chunked prefill + decode 交替（V1 连续批） |
| 预算粒度 | token 级三本账（rem_total/rem_input/rem_chunk）+ SWA 独立账 | block 级 watermark（v0）/ token budget（V1） |
| decode OOM | retract 回退重排队（radix 兜底） | preemption（recompute/swap 两种模式） |
| overlap 实现 | 双 stream + FutureMap 哨兵 + 延迟一拍 result_queue | V1 结构化异步（async output proc） |
| 调度策略 | lpm/dfs-weight/lof/random/routing-key 可插拔 | FCFS + prefix caching 加权 |

这张表也解释了为什么 SGLang 在"多轮共享前缀 + 高并发"负载（agent、编码助手）下吞吐优势明显：`retract + radix cache` 组合让内存压力下的重算代价最小化。
5. **调度决策与模式扩展解耦**。mixin 提供事件循环变体；`TypeBasedDispatcher` 提供 IPC 扩展；组件类提供运维功能；正文主循环因此非常稳定。
6. **DP-attention 的全局一致性约束**处处可见：overlap 决策、prefill/decode 混批禁令都要全 rank 对齐，这是理解相关"看似多余"的同步代码的钥匙。
7. **防御式资源管理**：未入批请求回滚 mamba slot、chunked 请求永远放行防泄漏、preempt 跳过两段式完成请求、HiCache in-flight 排干后才 flush——每一处都有对应的 leak/double-free 事故注释，值得逐条精读。

---

## 10. 阅读建议

**第一遍（主链路，约 500 行）**：`event_loop_overlap`（L1399）→ `get_next_batch_to_run`（L2348）→ `get_new_batch_prefill`（L2476）→ `update_running_batch`（L2765）→ `run_batch`（L2907）→ `process_batch_result`（L3084）。配合 schedule_batch.py 的 `prepare_for_extend/prepare_for_decode/filter_batch/merge_batch` 交替读。

**第二遍（请求生命周期）**：`handle_generate_request`（L1845）→ `_add_request_to_queue`（L2103）→ Req 在 waiting→prefill 批→running 批→finished→`release_kv_cache` 的完整旅程；再读 retract 路径（`update_running_batch` L2780 起 + schedule_batch.py `retract_decode`）。

**第三遍（overlap 专项）**：`init_overlap`（L1125）→ overlap_utils.py `FutureMap` → `_overlap_forward_isolation`（L2866）→ `launch_batch_sample_if_needed`（L3053）。建议同时打开 profile（generate-profile skill）观察 schedule stream 与 forward stream 的时间线。

**调试入口**：`SGLANG_REQ_WAITING_TIMEOUT` / `SGLANG_REQ_RUNNING_TIMEOUT`（超时 abort）、`SGLANG_TEST_RETRACT*`（强制触发 retract 测试）、`SGLANG_DISABLE_CONSECUTIVE_PREFILL_OVERLAP`、`SGLANG_ENABLE_STRICT_MEM_CHECK_DURING_BUSY`（每步内存不变量检查）、watchdog dump。日志关键字：`"Retract requests"`（L2822）、`"Prefill out of memory"`（mem_cache/common.py）。

**延伸阅读**：`scheduler_components/batch_result_processor.py`（输出后处理另一半）、`schedule_policy.py`（预算会计）、`managers/overlap_utils.py`（哨兵机制）、disaggregation mixin（PD 分离如何改写同一条主链路）。

---

## 附录 A：Scheduler 方法索引（按行号）

### 初始化族（L560-1746）

| 方法 | 行号 | 一句话职责 |
|---|---|---|
| `init_zbal_on_npu` | 560 | NPU 上提前切换内存分配器 |
| `init_model_config` | 570 | 解析 ModelConfig / 上下文长度 / is_generation |
| `init_ipc_channels` | 591 | ZMQ 通道与 TP 组初始化 |
| `init_idle_sleeper` | 608 | 空闲微睡眠（降功耗） |
| `init_tokenizer` | 624 | 可选加载分词器（skip_tokenizer_init 时仅 eos 表） |
| `init_mamba_backend` / `init_moe_gemm_config` | 677/680 | 后端 kernel 选型 |
| `init_tp_model_worker` / `init_model_worker` | 704/769 | 拉起 TpModelWorker（ModelRunner 持有者） |
| `maybe_init_draft_worker` | 727 | 投机解码 draft 模型 |
| `init_running_status` | 853 | waiting_queue / running_batch / cur/last_batch |
| `init_chunked_prefill` | 872 | chunk 预算与 mixed chunk 开关 |
| `init_schedule_policy` | 919 | SchedulePolicy / PrefillDelayer / NewTokenRatioTracker |
| `init_soft_watchdog` / `init_watch_dog_...` | 963/969 | 看门狗与内存冻结输入阻塞 |
| `init_disaggregation` | 992 | PD 分离队列与传输后端 |
| `init_overlap` | 1125 | 双 stream + FutureMap + batch_record_buf |
| `maybe_init_ngram_embedding` | 1156 | n-gram embedding 模型支持 |
| `init_deterministic_inference_config` | 1207 | 确定性推理的 chunk 对齐尺寸 |
| `init_request_dispatcher` | 1224 | 40+ 条 IPC 类型分发表 |
| `init_weight_updater` / `init_lora_drainer` / `init_lora_overlap_loader` | 1522/1532/1541 | 热更新与 LoRA 公平调度 |
| `init_grammar_manager` / `init_request_receiver` | 1547/1550 | 约束解码 / 统一收包器 |
| `init_dp_attn_adapter` | 1574 | DP-attention 同步适配器 |
| `init_pool_stats_observer` / `init_invariant_checker` | 1589/1606 | 池统计 / 内存不变量检查 |
| `init_kv_events_publisher` / `init_load_inquirer` | 1624/1639 | KV 事件流 / /v1/loads |
| `init_output_streamer` / `init_batch_result_processor` | 1662/1675 | 输出流式化 / 批结果处理组件 |

### 主链路族（L1321-3134）

| 方法 | 行号 | 一句话职责 |
|---|---|---|
| `_abort_on_running_timeout` | 1321 | running 批超时 abort（置 to_finish） |
| `run_event_loop` | 1351 | 建 schedule_stream 并 dispatch |
| `event_loop_normal` / `event_loop_overlap` | 1372/1399 | 两条主循环 |
| `is_disable_overlap_for_batch` | 1457 | 本批是否退回同步处理 |
| `process_input_requests` | 1490 | IPC 消息分派 |
| `init_req_max_new_tokens` | 1699 | 裁剪 max_new_tokens |
| `_process_and_broadcast_mm_inputs` | 1720 | 多模态输入 TP 广播（rank0 处理后散播） |
| `_try_apply_padded_mm_input_ids` | 1795 | 后端自带 pad 展开的捷径 |
| `_maybe_compute_mrope_positions` | 1817 | 三维 rope 位置 |
| `handle_generate_request` | 1845 | 生成请求准入（§3.3） |
| `handle_batch_generate_request` | 2070 | 批量请求循环调用上面的 |
| `_prefetch_kvcache` | 2081 | HiCache L3 预取登记 |
| `_add_request_to_queue` | 2103 | 按部署模式入队 |
| `_set_or_validate_priority` | 2127 | 优先级校验 |
| `_abort_on_queued_limit` | 2152 | 队列满拒绝/驱逐 |
| `_abort_on_waiting_timeout` | 2201 | 等待超时清理 |
| `handle_embedding_request` | 2231 | embedding 模型对称路径 |
| `stash_chunked_request` | 2309 | chunked 前缀插树 |
| `_build_hisparse_decode_batch` | 2312 | HiSparse staging→decode 批 |
| `get_next_batch_to_run` | 2348 | ★ 每步决策入口（§4.1） |
| `get_num_allocatable_reqs` | 2471 | 可分配请求数 |
| `get_new_batch_prefill` / `_get_new_batch_prefill_raw` | 2476/2496 | ★ prefill 组批（§4.2） |
| `_can_schedule_lora_req` | 2737 | LoRA 批约束 |
| `update_running_batch` | 2765 | ★ decode 组批 + retract（§4.4） |
| `record_batch_in_overlap` | 2851 | 快照钉入双槽防 GC |
| `_overlap_forward_isolation` | 2867 | SB 前向事务化 |
| `run_batch` | 2907 | ★ 发起前向（§6.2） |
| `launch_batch_sample_if_needed` | 3053 | grammar 延迟采样 |
| `process_batch_result` | 3084 | ★ 输出处理分派（§6.3） |
| `maybe_send_health_check_signal` | 3113 | 忙时健康检查应答 |

### 控制面族（L3124-3746，浏览即可）

`add/remove/list_external_corpus`（3124-3153）、`clear/attach/detach_hicache_storage`（3154-3343）、`flush_cache`（3344，只在 `is_fully_idle` 时执行）、`get/set_internal_state`（3374/3404）、`save_*_model`（3450-3456）、`handle_rpc_request`（3456）、`abort_request`（3478，按 rid 从 waiting/running/chunked 三处摘除）、`pause/continue_generation`（3581/3630，RL 训练暂停引擎用）、LoRA 装卸（3642-3665）、`slow_down`（3682）、session 开关（3701-3709）、`handle_freeze_gc`/`handle_dumper_control`（3714/3720）。

### 模块级函数

| 函数 | 行号 |
|---|---|
| `dispatch_event_loop` | 3749 |
| `configure_scheduler_process` | 3780 |
| `run_scheduler_process` | 3837 |
