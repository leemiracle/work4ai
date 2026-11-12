# vllm/v1/core/kv_cache_manager.py — KVCacheManager：KV 显存经济学的管理者面

> 源码：`vllm/v1/core/kv_cache_manager.py`（930 行）｜Scheduler 与块管理器之间的唯一门面｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`KVCacheManager`（vllm/v1/core/kv_cache_manager.py:131）是**调度器与底层块管理器之间的唯一门面**。它活在 EngineCore 进程里，与 GPU 无直接关系——管理的是"块簿记"，真正显存在 worker 侧按 `KVCacheConfig.num_blocks` 分配。PagedAttention 的"显存经济学"（哪些 token 的 KV 驻留、哪些块可复用、哪些该逐出）的决策全部发生在这里。请求生命周期：进入 waiting → Scheduler 每步 `get_computed_blocks()` 查前缀缓存（:266）→ `allocate_slots()` 分配（:379）→ 完成或被抢占时 `free()`（:628）。相比 9 月版，它的 API 面向 disagg/混合注意力又长出一圈：零块校验、full-sequence 准入闸、按 processed 前缀释放、为 connector 服务的截断视图与边界状态排空。

## ② 内部结构

**`KVCacheBlocks`**（:34-128，dataclass）：调度器侧块集合封装，docstring 明言目的是 "hide KVCacheManager's internal data structure from the Scheduler"（:36-39）。`blocks[i][j]`=第 i 个 kv_cache_group 的第 j 块——外层维度是 group 而非 token 块，为不同 group 不同 block_size 留余地。`__add__`（:56）拼接、`get_block_ids(allow_none, group_ids)`（:81-107）、`get_unhashed_block_ids_all_groups`（:114，跳过 null 块）、`new_empty`（:126）。

**`KVCacheManager` 状态源只有两个**：`coordinator`（:168，`get_kv_cache_coordinator` 工厂，混合模型得 HybridKVCacheCoordinator 内挂多个 single-type manager）与 `block_pool`（:199，物理块池：引用计数+前缀缓存哈希表）。其余皆轻量：`watermark_blocks = watermark×num_blocks`（:210，watermark 现由 scheduler_config 传入）；`kv_cache_event_metadata`（:211，各组 kind/sliding_window，给 KV 事件打语义标签）；不可变单例 `empty_kv_cache_blocks`（:224，免高频空分配 GC）。2026-10 新面孔：`max_in_flight_tokens`（:155，回收感知的准入上限，未设时塌缩为 max_model_len）；`mamba_shared_prefix_checkpoint` 谓词（:188-193，两侧共用一个判定，"调度器不会把 chunk 停在 manager 会拒绝的 junction 上"）；`retained_hit_group_ids`（:200，稀疏保留组只收本地/外部命中覆盖的前缀，:494-503 截断）。

**四大主方法**：
- `get_computed_blocks`（:266）：入口短路（未启用 caching 或请求 `prefix_cache_hit_limit==0`，:251-253——**2026-10 起命中上限是逐请求的**）；`find_longest_cache_hit`（:304）；全命中也须重算最后一个 token（:296-301 注释，且可能连带整块）；返回三元组，第三个 `shared_prefix_boundary = 命中数+未缓存共享前缀`（:323-325），即最长单组命中处——稀疏保留组（Mamba/滑窗）没覆盖到的接缝，防止复用断链。
- `get_computed_blocks_for_connector`（:330）：混合模型各组命中分歧时的仲裁——以 full-attention 命中为准报给 connector，`hit_diverged`（:377）标记"FA 命中深于滞后组"；若滞后组反而更深（FA 尾被逐出）则回退 `get_computed_blocks` 调和（:368-372）。
- `allocate_slots`（:379）：docstring 的块布局图（:428-449）是全文件最重要文档——`comp | new_comp | ext_comp | new | lookahead` 五段、三段"to be"区域、ref_cnt 增与未增的分界。执行四步：①零 token 且无命中可采纳直接 ValueError（:482-490，异步加载/重放步可无自身槽位）；②`full_sequence_must_fit` 准入闸（:530-547，防 chunked prefill 只查首块就过度准入）；③**先释放滑窗外 skipped blocks 再算需求**（:563-567，且按 `total_computed - num_in_flight_tokens` 的 processed 口径——在途步骤的注意力窗口还在读、被拒的 spec token 会回滚）；④`required+watermark ≤ free-reserved` 核对（:583-587）→ 命中块只加引用（:595）→ 新块分配（:603）→ `delay_cache_blocks` 提前返回（:612，P/D 异步收块）→ 否则 `cache_blocks` 提交前缀缓存，**cap 到 `request.num_tokens`**（:620-623，draft token 可能被拒不许缓存）。
- `free`（:628）：委托 coordinator，逆序释放保证 LRU 尾块先逐出。

## ③ 外部连接

- **依赖**：`kv_cache_coordinator`（Hybrid 工厂）、`kv_cache_utils`（BlockHash/KVCacheBlockCopy）、`single_type_kv_cache_manager`（MambaManager，:18）、`kv_cache_interface`（各 spec 类型）、`kv_cache_metrics`。
- **被依赖**：scheduler 是主客户（allocate/free/统计全走它）；KV transfer connector 经 `bind_kv_cache_manager`（vllm/v1/core/sched/scheduler.py:376-377）读写块表——drain 型 API 全是为它们开的：`take_new_block_ids`（:841，KV-zero 防脏数据）、`record_blocks_for_zeroing`（:848，失败加载的未写块补零）、`take_kv_cache_block_copies`（:862，CoW 拷贝排水）、`take_boundary_state_offloads`（:879，Mamba align 边界状态交接，connector 只按 block_id 读绝不按位置解析）、`finalize_partial_tail_offloads`（:905，请求结束时钉住合法尾块）。

## ④ 数据流

```
schedule() 每步: new_step_starts() :928 →（waiting 阶段）
  get_computed_blocks → (blocks, num_local, boundary)
  allocate_slots(num_new_tokens, new_computed_blocks, ext_tokens,
                 delay_cache_blocks, reserved_blocks, ...) → KVCacheBlocks|None
  → SchedulerOutput.req_to_new_blocks → worker 按 block_id 映射显存偏移
请求结束: free()；重叠批下 pop_blocks_for_free(:659) + 延迟栅栏后入池
事件: take_events(:704) 给 BlockStored 注入 kind/sliding_window 语义
  → KVEventBatch 发布给外部消费者
```

## ⑤ 设计决策

1. **门面+协调器分层**：Manager 不懂 Mamba/滑窗/全注意力差异，全部下沉 coordinator 的 per-group manager；新增注意力类型不动本文件。hash_block_size 与调度 block_size 分离（构造参数 :137/:179）让"哈希粒度≠分配粒度"成为一等公民。
2. **释放≠逐出**：free 只减引用，块进前缀缓存仍可被命中；真逐出发生在 block_pool 分配不足时。`evict_blocks`（:673）只给 KV 加载失败路径用。
3. **watermark 只对 waiting/preempted 且本步已有调度请求时生效**（:517-524）——running 请求不扣减，避免显存浪费。
4. **processed 口径是一致性核心**：滑窗释放（:563）、`get_block_ids_for_computed_tokens`（:739）、`estimate_cached_tokens`（:759，跨可缓存组取最小）全都以"已提交 token"为准，乐观推进的 in-flight 部分一律不算——这是 async scheduling 下正确性的地基。
5. **废弃也留门**：`get_num_common_prefix_blocks`（:699-702）**2026-10 起 cascade attention 已整体移除**，恒返回 0，仅为 out-of-tree 调度器保留签名（同看 arg_utils 的 --disable-cascade-attn 同步废弃）。

## ⑥ 新人提示

- 读法：先啃 `allocate_slots` docstring 的布局图（:428-460），再读 `KVCacheBlocks` docstring，最后下潜 `KVCacheCoordinator`。
- 易混①：`empty_kv_cache_blocks` 单例 vs `new_empty()`（:126）——前者跨请求共享不可变，后者给需要可变副本的调用方。
- 易混②：Manager 在 CPU 侧只认 block_id，worker 侧才翻译成显存偏移（slot_mapping），两者靠 SchedulerOutput 的 new_block_ids 传递。
- 易混③：`truncate_computed_blocks`（:808）是**纯切片视图**——refcnt 不动、原 blocks 不变，专门服务"远端命中盖过本地尾巴"的协调；与真释放无关。
- 混合模型排障：命中忽长忽短先怀疑 FA/Mamba 分歧，看 `hit_diverged` 分支（:368-377）是否回退调和。
