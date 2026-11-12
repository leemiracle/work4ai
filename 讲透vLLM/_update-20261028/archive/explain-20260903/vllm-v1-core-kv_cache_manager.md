# vLLM v1 深度解析：KVCacheManager（kv_cache_manager.py）

> 文件：`vllm/v1/core/kv_cache_manager.py`（约 900 行）
> 知识图谱 layer：`sched-kv-cache`（调度与 KV Cache 管理，49 节点）

## 角色定位

`KVCacheManager` 是**调度器（Scheduler）与底层块管理器之间的唯一门面（facade）**。它活在 EngineCore 进程里，与 GPU 无直接关系——它管理的是"块簿记"（bookkeeping），真正的显存在 Worker 侧按 `KVCacheConfig.num_blocks` 分配。整个 PagedAttention 的"显存经济学"（哪些 token 的 KV 驻留显存、哪些块可复用、哪些该逐出）的决策全部发生在这里。

在请求生命周期中：请求进入 waiting 队列 → Scheduler 每步调用 `get_computed_blocks()` 查前缀缓存 → `allocate_slots()` 为新 token 分配块 → 请求完成或被抢占时 `free()`。图谱反向边显示它被 `v1/core/sched/scheduler.py` 和 5 个 KV transfer connector（mooncake、offloading、hf3fs）消费，前者是主客户，后者做 KV 卸载/迁移时需要读写块表。

## 内部结构

**`KVCacheBlocks`**（dataclass）：调度器侧持有的块集合封装，`blocks[i][j]` 表示第 i 个 kv_cache_group 的第 j 个块。设计意图写在 docstring 里——"hide KVCacheManager's internal data structure from the Scheduler"。它提供 `__add__`（两组块拼接）、`get_block_ids()`、`get_unhashed_block_ids()` 等纯视图操作。注意外层维度是 group 而非 token 块——为未来不同 group 用不同 block_size 留余地。Manager 预构造了不可变的 `empty_kv_cache_blocks` 单例，避免高频空分配的 GC 开销。

**`KVCacheManager`** 只有两个真正的状态源：
- `self.coordinator`：由 `get_kv_cache_coordinator()` 工厂创建，混合模型（Mamba+full attention）得到 `HybridKVCacheCoordinator`，内部再挂多个 single-type manager；
- `self.block_pool = coordinator.block_pool`：物理块池，负责引用计数与前缀缓存哈希表。

其余如 `watermark_blocks`（准入水位线，按 `watermark × num_blocks` 折算成块数）、`kv_cache_event_metadata`（各组 spec 的 kind/sliding_window，用于给 KV 事件打语义标签）都是轻量配置。

## 核心数据流

**前缀查找 `get_computed_blocks(request)`**：入口先短路（未启用 caching、或请求要求 prompt logprobs / all-pooling 时跳过），然后 `coordinator.find_longest_cache_hit(request.block_hashes, max_cache_hit_length)`。一个精妙的细节：`max_cache_hit_length = request.num_tokens - 1`——即使全部命中也必须重算最后一个 token 才能拿到 logits，且 `allocate_slots` 要求 block 对齐，可能连带重算整整一块。返回三元组 `(blocks, num_new_computed_tokens, shared_prefix_boundary)`，第三个值是 Marconi 式稀疏保留（Mamba/sliding window 组未覆盖的交界点），防止稀疏前缀缓存把复用接缝丢掉。

**分配 `allocate_slots(request, num_new_tokens, ...)`**：docstring 里那张块布局图是全文件最重要的文档——序列被划分为 `comp | new_comp | ext_comp | new | lookahead` 五段，分别对应已计算、本轮新命中前缀、connector 外部提供、待计算、投机 lookahead。三阶段执行：①先释放滑窗外的 skipped blocks（即使分配失败也做，减少逐出）；②核对 `get_num_blocks_to_allocate + watermark ≤ free_blocks`，不足返回 None（调度器会推迟该请求）；③`allocate_new_computed_blocks`（命中块只加引用不拷贝）+ `allocate_new_blocks`，最后 `cache_blocks` 把新算完的块按哈希提交进前缀缓存——但 cap 到 `request.num_tokens`，因为投机解码的 draft token 可能被拒绝，不能缓存。

**释放 `free(request)`**：委托 `coordinator.free()`，逆序释放以保证 LRU 语义下尾部块先被逐出。

## 关键设计决策

1. **门面 + 协调器分层**：Manager 不懂 Mamba/滑窗/全注意力的差异，差异全部下沉到 coordinator 的 per-group manager；Manager 只做参数校验、水位线、事件注解。新增注意力类型不动这个文件。
2. **hybrid 前缀分歧处理**：`get_computed_blocks_for_connector()` 专门处理混合模型下"full-attention 尾被逐出而 Mamba 状态还活着"的分歧，以 full-attention 命中为准并向 connector 报告 `hit_diverged`，让外部补齐差量。
3. **watermark 只对 waiting/preempted 且已有调度请求的步生效**——避免每个 running 请求都被扣减造成显存浪费。
4. **面向 disagg 的钩子**：`delay_cache_blocks`（P/D 分离时等远端传输完成再缓存）、`take_kv_cache_block_copies`（CoW 拷贝排水）、`take_boundary_state_offloads`（Mamba align 边界状态交接）、`take_new_block_ids`（KV-zero：新块清零防脏数据腐蚀 attention）。

## 新人提示

- 阅读切入点：先读 `allocate_slots` 的 docstring 块布局图，再读 `KVCacheBlocks` 的 docstring，最后看 `KVCacheCoordinator`（下一层）。
- 易混淆点①：`get_num_common_prefix_blocks` 看似缓存工具，实际是给 FlashAttention cascade attention 用的（找 batch 内公共前缀）；它统计的是"有 KV 的所有请求"而非"本步调度的请求"，可能返回 0（存在未调度的异类请求时）。
- 易混淆点②：`free()` 释放≠逐出。释放只是减引用，块进了前缀缓存还能被后续请求命中；真正逐出发生在 block_pool 分配不足时。
- 易混淆点③：Manager 在 CPU 侧只认 block_id，Worker 侧才把 block_id 翻译成显存偏移（slot_mapping），两者通过 SchedulerOutput 中的 new_block_ids 传递。
