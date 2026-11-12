# vllm/v1/core/sched/scheduler.py — Scheduler：V1 引擎的心脏

> 源码：`vllm/v1/core/sched/scheduler.py`（3726 行）｜统一 token 记账 + 双预算两阶段调度｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`Scheduler`（vllm/v1/core/sched/scheduler.py:86）是 v1 引擎**计算调度层**的核心：每个 engine step 第一步就是 `schedule()`——决定哪些请求、各推进多少 token，产出 `SchedulerOutput` 交 executor 执行；`update_from_output()`（:2234）回写。它统管 KV 块分配、prefix caching、抢占、多模态 encoder、投机解码、KV/EC connector（P/D）与流式会话。**2026-10 起两大形态变化**：其一，async scheduling 的重叠机制改由 worker 侧承担，`AsyncScheduler` 缩成 56 行薄壳（async_scheduler.py:13，只覆写 `_update_after_schedule` 做占位记账 :44；重叠本体移到 executor 的 AsyncModelRunnerOutput 路径，multiproc_executor.py:1132）；其二，diffusion 走独立 `DiffusionScheduler`（diffusion_scheduler.py:37，由 vllm/config/vllm.py:2078 选中）。

## ② 内部结构

**队列与状态**（`__init__` :87-489）：`requests` 注册表（:216）+ **三级 waiting**——`waiting`（:225）/`kv_holding_waiting`（:229，块持有者永远先排干，"绝不排在可能分配失败而中止扫描的请求后面"，:226-229 注释）/`deferred_waiting`（:232，被跳过者集合，取代旧版 skipped_waiting）+ `running`（:233）；没有显式 FINISHED 队列，完成态记在 `RequestStatus`+`finished_req_ids`（:239）。2026-10 新面孔：**`max_num_active_seqs` 准入上限与 `max_num_seqs` 槽位分离**（:132-138）；DSV41 SWA bounded replay 组（:295-307）；动态投机解码查表 `dynamic_sd_lookup`（:315-322，按 batch 取最优 K）；`aux_output_connector`（:471，routed experts）；`_inflight_prefills` 预留（:482）与 KV fetch 分阶段计数（:486-489）。KVCacheManager 构造（:344-363）已膨胀到 20 参数。

**`schedule()`（:688-1758，约 1070 行）两阶段**：先读 woosuk 的不变量注释（:690-699）——"没有 prefill phase 也没有 decode phase，每个请求只有 `num_computed_tokens` 追赶 `num_tokens_with_spec`"。阶段一 RUNNING（:783-1025）：`num_new_tokens` 依次被 token/input 双预算（:835-837，input 给 draft 槽留量 :710）、long_prefill 阈值自适应下限（:748-758）、async 占位守卫（:789-803）、PP 解码错峰 `next_decode_eligible_step`（:805）、mamba 块对齐（:849）裁剪；`allocate_slots` 失败进抢占循环（:901-969）：PRIORITY 选 `(priority, arrival_time)` 最大受害者并**回滚其本步已记账预算**（:921-957），FCFS 直接 `running.pop()`（:959）；`drop_stale_output=requires_kv_delivery`（:961-965）。阶段二 WAITING（仅本步无抢占，:1039）：本地+connector 前缀查找（:1099-1116）→ 远端更长则截断本地 sub-block 尾巴避免 CoW（:1123-1167）→ 异步加载走 `WAITING_FOR_REMOTE_KVS`（:1497）→ decode 请求 pad 到 uniform spec 尺寸保 cudagraph（:1300-1319）→ `allocate_slots` 带 reserved_blocks 防异步加载死锁（:1409-1441）→ 阻塞态甄别 `_handle_blocked_waiting_request`（:3462）。收口产出 `SchedulerOutput`（:1699-1724，含 skip_drafts/动态 K :1684-1688、new_block_ids_to_zero）。

**辅助主力**：`_preempt_request`（:1773）释放全部块、`num_computed_tokens=0`（:1796）、回队首（:1816），async 下把在途输出标记 stale 逆流排干（:1806-1810）；`_update_after_schedule`（:1819）**调度即记账**（:1832 乐观推进）；`update_from_output`（:2234）主循环里排干 stale（:2292-2297）、spec 拒绝回滚（:2334-2338）、按 client_index 分桶输出（:2615）；流式会话三件套（`add_request` :2902/`_update_request_as_session` :1853/`_handle_stopped_request` :2691，resumable 请求停在前沿再续）；延迟释放栅栏 `_drain_deferred_frees`（:3075）；KV 加载失败恢复 `_handle_invalid_blocks`（:3646，多 group 布局直接 raise）。

## ③ 外部连接

- **imports**：kv_cache_manager、request_queue（FCFS/PRIORITY 工厂）、encoder_cache_manager、kv_connector/factory（scheduler 角色 :178-182）、ec_connector、structured_output、spec_decode/dynamic、multimodal/encoder_budget。
- **被依赖**：EngineCore 经 `get_scheduler_cls()`（vllm/config/scheduler.py:231）实例化，只认 `SchedulerInterface`；子类 AsyncScheduler（PP 解码 stagger，async_scheduler.py:20-56）与 DiffusionScheduler。`has_requests()`（:3110）把 connector 的 pending push work 也算"有活"——WRITE 传输排空前引擎不许休眠。

## ④ 数据流

```
EngineCore.add_request → scheduler.add_request（新请求/流式续写两路）
每步: schedule()
  ├─ RUNNING: 双预算裁剪 → allocate_slots 失败→抢占循环
  ├─ WAITING: 前缀查找(本地+远端) → allocate → 入 running
  │    （异步 KV 加载 → WAITING_FOR_REMOTE_KVS，传输完成经
  │     _update_from_kv_xfer_finished :3499 回 WAITING）
  └─ SchedulerOutput → executor.execute_model → ModelRunnerOutput
update_from_output（:2234）: 每请求推进/拒绝回滚/finish 判定
  → dict[client_index, EngineCoreOutputs]（:2615，多前端分桶）→ 前端
```

## ⑤ 设计决策

1. **统一 token 记账**（:690-699）仍是地基：chunked prefill 是"分次追账"，spec decode 是"账面含 draft"，SWA replay 是"命中后回吐一个窗口再追"（`_mark_prefix_replay` :3390）。
2. **抢占=全量重算+stale 逆向排干**：无 V0 的部分重算；async 下在途输出不能丢（会扰动 spec 接受率），改为标记 stale 每步等量排干（:2294-2297），drop 模式才整体丢弃（:2311-2313）。
3. **waiting 三级化**是 prefix caching×KV connector 的必然：块持有者（WAITING_FOR_REMOTE_KVS/STREAMING）与普通等待者混排会造成"扫描中止卡死块持有者"的活锁，:226-229 注释把这条不变量写死。
4. **双 prefill 节流**：DP 模式由引擎核按全局 step_counter 对齐（`throttle_prefills` 参数）；单机也有 local cadence（:397-414/:769-780），且带 capacity escape——release 步排不空 waiting 就停 throttle，否则 waiting 队列无界增长（:760-768）。
5. **乐观推进+事后修正**（:1832/:2334）是重叠调度的前提；配套 `defer_block_free`（:192-194）用 seq FIFO 栅栏（:461-465）保证异步 KV 加载不写"已释放但 GPU 还在写"的块。
6. **draft 可以整步跳过**：`_drafts_unused`（:491）判定"本步产出的 draft 必然无人验证"（非末段 prefill chunk/本步采到 max_tokens），V2 runner 据此置 `skip_drafts`（:1722）省掉 drafter 前向。

## ⑥ 新人提示

- 别顺序啃 1070 行：抓住"RUNNING/WAITING 两循环+预算裁剪链+allocate 失败→抢占"骨架，encoder/mamba/replay 分支按需查。
- 核心不变量只有一个：`num_computed_tokens ≤ num_tokens_with_spec`；排障先看 `make_stats()`（:3202，含 num_skipped_waiting_reqs/KV fetch 分阶段计数）。
- 易混①：`token_budget`（max_num_scheduled_tokens，:139-143）与 `input_budget`（max_num_batched_tokens，:711）两本账，后者扣 draft 槽。
- 易混②：请求"消失"三路径——finish（update_from_output）、abort（finish_requests :2935）、preempt（不消失，回 waiting 队首）。
- 调 prefill 饥饿/TTFT 抖动先查 `prefill_schedule_interval` 与 `long_prefill_token_threshold_adaptive`（:753-758 公平份额下限）。
