# 深度解析：`python/sglang/srt/managers/schedule_batch.py`

> 源码: python/sglang/srt/managers/schedule_batch.py @ commit ec075d8bc（全文 2773 行）

## 0. 这份文件在 SGLang 中的位置

文件头注释（L24-36）一锤定音：

```
ScheduleBatch -> ForwardBatch

- ScheduleBatch is managed by `scheduler.py::Scheduler`.
  It contains high-level scheduling data. Most of the data is on the CPU.
- ForwardBatch is managed by `model_runner.py::ModelRunner`.
  It contains low-level tensor data. Most of the data consists of GPU tensors.
  It is constructed directly from a ScheduleBatch by `ForwardBatch.init_new`.
```

本文件定义了调度器的**全部核心数据结构**：`Req`（单请求的完整生命周期状态机，约 800 行）、`ScheduleBatch`（一批请求的 CPU/GPU 混合视图与组批原语）、以及前缀匹配输入、增量 detokenize、finish 判定、retract 复位、KV 释放配合等机制。`ForwardBatch` 本体在 `model_executor/forward_batch_info.py`，但它由 `ScheduleBatch` 直接构造（本文 §6 一并说明）。

文件地图：

| 行号 | 内容 |
|---|---|
| L129-135 | 多模态 pad 值哨兵（`MM_PAD_SHIFT_VALUE = 1_000_000`，防与真实 token id 冲突） |
| L143-210 | `BaseFinishReason` 及 5 个子类（结束原因的可序列化表示） |
| L212-620 | 多模态数据结构族：`Modality` / `MultimodalDataItem` / `MultimodalProcessorOutput` / `MultimodalInputs` |
| L623-640 | `ReqLogprob`（logprob 结果容器） |
| L643-1439 | **`Req`**：单请求状态机 |
| L1442-1465 | Mamba 前缀缓存 track 辅助 |
| L1468-2773 | **`ScheduleBatch`**：批数据结构与组批原语 |

---

## 1. 结束原因与多模态（快速过）

- `FINISH_MATCHED_TOKEN / FINISH_MATCHED_STR / FINISHED_MATCHED_REGEX / FINISH_LENGTH / FINISH_ABORT`（L148-210）都实现 `to_json()`，最终原样出现在 API 响应的 `finish_reason` 字段里。
- `MultimodalDataItem`（L238）是一个"属性包"：通过 `__getattr__`/`__setitem__`（L266-284）允许处理器动态挂字段（`pixel_values`、`image_grid_thw` 等），`set_pad_value`（L292）给每项分配 `1_000_000 + hash` 区间的 pad token id——图像 token 在 input_ids 里被展开成这些 pad 占位，前缀缓存与 logprob 计算都要感知它们（`sanity_check_mm_pad_shift_value` L128 保证 vocab 不越界）。
- `MultimodalInputs`（L461）聚合一次请求的全部模态输入，`merge`（L581）支持多轮追加。

细看四个类各自的分工：

| 类 | 行号 | 分工 |
|---|---|---|
| `Modality` | L212 | 枚举 IMAGE/AUDIO/VIDEO，`from_str` 解析用户参数 |
| `MultimodalDataItem` | L238 | 单个模态项（一张图/一段音频）：动态属性包 + `pad_value`（占位 token id）+ `has_cuda_ipc_proxy/reconstruct`（L348-375，跨进程传输大张量的 IPC 代理重建） |
| `MultimodalProcessorOutput` | L440-507 | 处理器产物：特征张量 + `build_padded_input_ids`（把 `<image>` 单 token 展开成 pad 序列） |
| `MultimodalInputs` | L461-620 | 请求级聚合：`precomputed_embedding_items`、`mrope_positions`、`release_features`（L495，prefill 前释放 CPU 特征防泄漏）、`contains_*_inputs` 谓词 |

这部分与 `multimodal_processor.py` 配套，主链路阅读可先跳过。

---

## 2. `Req`：单请求状态机（L643-1439）

`Req.__init__` 有 40+ 参数、330 行字段赋值。按功能分组理解（行号为赋值处）：

### 2.1 输入与输出

| 字段 | 行号 | 说明 |
|---|---|---|
| `origin_input_ids: array("q")` | L691 | 原始 prompt token（`array` 而非 list，省内存且可拼接） |
| `origin_input_ids_unpadded` | L692 | 多模态 pad 展开前的版本（detokenize 用） |
| `output_ids: array("q")` | L698 | 每个 decode 步的输出（append-only） |
| `fill_ids` | L700 | **`origin_input_ids + output_ids` 的滚动视图**——"下轮前向真正要消费的完整序列"，chunked prefill 与 retract 都靠它重算 |
| `seqlen`（property） | L975 | `len(origin_input_ids) + len(output_ids)` |
| `input_embeds` / `positional_embed_overrides` | L703-704 | embedding 直通输入与位置覆盖（禁用前缀缓存，L1076-1077） |

### 2.2 req 级内存管理账本（L707-711）

```python
self.kv_committed_len = 0   # 已"提交"的 KV 长度（会被 radix cache 接管的边界）
self.kv_allocated_len = 0   # 实际分配长度（>= committed，投机解码会多分配）
self.kv_committed_freed / self.kv_overallocated_freed  # 释放幂等断言
```

这对"双账本"是 KV 生命周期的心脏：`pop_committed_kv_cache()`（L1001）与 `pop_overallocated_kv_cache()`（L1009）把 `[0, commit)` 与 `[commit, allocated)` 两段分别交给 `release_kv_cache`（mem_cache/common.py L567）处理——committed 段进 radix cache 供复用，over-allocated 段直接 free。`_cache_commit_len`（L994）在 `strip_thinking_cache` 模式下把 thinking tokens 划入 over-allocated 段（不缓存思维链，#22373）。

### 2.3 前缀缓存视图（L805-829）

```python
self.prefix_indices: torch.Tensor   # 命中的 KV slot 序列（GPU int64 张量）
self.extend_input_len: int          # 本轮需要新算的 token 数 = len(fill_ids) - len(prefix_indices)
self.last_node / last_host_node / best_match_node   # radix 树上的匹配节点（device/host/HiCache）
self.host_hit_length / storage_hit_length           # host 内存 / L3 存储命中长度
self.cache_protected_len: int       # 已插入树缓存的受保护前缀长度
self.inflight_middle_chunks: int    # chunked prefill 计数（>0 表示"prefill 未完成"）
```

这些字段全部由 `init_next_round_input` 刷新（见 §2.5）。

### 2.4 finish 状态与两段式完成（L773-787）

```python
self.finished_reason   # 真正的结束原因（一旦设置，请求将在下轮被 filter 出批）
self.finished_len      # 输出中命中 stop 的位置（投机解码一步多 token 时必需）
self.to_finish         # ★ 事件循环中途的"待完成"暂存——绝不能中途直接设 finished_reason
```

L780-783 的注释解释了 `to_finish` 存在的原因：**中途（如超时/abort）直接设置 `finished_reason` 会让请求在当轮被 filter 掉，但输出流程要求它至少走完一次 process_batch_result，否则客户端永远收不到响应**。`to_finish` 在下一次 `update_finish_state`（L1275-1278）才转正。

其余分组速览：mamba 池跟踪（L759-771，ping-pong buffer + 延迟 COW/clear）、增量 detokenize 游标（L789-800 `surr_offset/read_offset`）、logprob 参数与暂存（L843-871）、retraction 标记（L832-834）、投机解码统计（L914-926，接受长度直方图）、PD 分离传输游标（L938-959 `start_send_idx/tmp_end_idx/metadata_buffer_index`）、观测打点（L928-936）。

### 2.5 `init_next_round_input()`（L1043-1131）——每次进入前向前的对表

Scheduler 在把请求放进 prefill 批之前（或 HiCache prefetch 前）调用它：

1. `fill_ids = origin_input_ids + output_ids`（L1052）；
2. 计算最大可匹配前缀 `_compute_max_prefix_len`（L1133）：**至多 `input_len - 1`**——最后一个 token 必须留给本轮前向计算（否则模型永远不算新 token）；带 logprob 时再夹到 `logprob_start_len`；
3. `tree_cache.match_prefix(...)`（L1082-1107）：radix 树前缀匹配，一次拿回 `prefix_indices / last_node / host_hit_length / mamba_branching_seqlen` 等全套前缀视图；`SGLANG_RADIX_FORCE_MISS` 可强制 miss（测试用）；
4. 被 retract 过的多模态请求要修复 mrope positions（L1116-1129）；
5. `set_extend_input_len(len(fill_ids) - len(prefix_indices))`（L1131）。

`set_extend_input_len`（L1387-1403）同时推导 `extend_logprob_start_len`——logprob 起点在"当前 extend 块内"的相对坐标，供 `prepare_for_extend` 切 logits。

用一个具体例子把这几个量的关系钉死。假设 prompt = `[a, b, c, d, e]`（5 token），radix cache 里命中了 `[a, b, c]`，则：

```
origin_input_ids = [a, b, c, d, e]        (5)
output_ids       = []                      (0)
fill_ids         = [a, b, c, d, e]        (5，L1052 拼接)
prefix_indices   = [k0, k1, k2]           (3，match_prefix 返回的 KV slot)
_extend_input_len = 5 - 3 = 2             (L1131：只算 d, e)
prepare_for_extend 里:
  input_ids[i]  = fill_ids[3:] = [d, e]    (L1817)
  seq_lens[i]   = 5                        (L1819)
  prefix_lens[i]= 3                        (L1821)
  out_cache_loc 段 = 2 个新 slot           (alloc_for_extend)
decode 一步后（生成了 x）:
  output_ids = [x]; fill_ids = [a..e, x] (6)
  下轮 prepare_for_decode: input_ids[i]=x(由 future_map resolve),
  seq_lens 5→6, alloc 1 个新 slot
```

一句话：**`fill_ids` 是"序列的真相"，`prefix_indices` 是"已算过的前缀"，两者之差就是本轮 extend 的工作量；decode 是 extend_input_len=1 的特例。**

### 2.6 finish 判定：`update_finish_state()`（L1271-1301）

每步 decode 后由 batch_result_processor 调用，优先级从高到低：

1. 已完成 → 直接返回；
2. `to_finish` 转正（abort 类）；
3. 长度到顶 → `FINISH_LENGTH`；
4. grammar 终止；
5. `_check_token_based_finish`（L1206）：逐 token 查 stop_token_ids / eos / tokenizer 附加停止符，命中记 `finished_len`（投机解码一步出多 token，必须定位是第几个）；
6. `_check_vocab_boundary_finish`（L1255）：token id 越界（NaN logits）兜底，改写为 eos 并以 `"NaN happened"` 结束；
7. `_check_str_based_finish`（L1230）：在 `tail_str`（L1161，只解码尾部窗口，控开销）里查 stop 字符串/正则。

配套的 `check_match_stop_str_prefix`（L1177）服务流式输出：stop 串的**前缀**已出现在尾部时暂停推送，避免 stop 内容泄露给用户。`init_incremental_detokenize`（L1141）实现 HF 同款的增量解码窗口（surrounding offset 抗 BPE 清理算法）。

### 2.7 `reset_for_retract()`（L1303-1346）

被 retract（§5.4）时把请求打回"从未运行过"的状态：清 prefix、锁、logprob 暂存、mamba 跟踪、KV 账本全部归零；`retraction_count` 累计、`retracted_stain` 永久置位（cached_tokens 只统计首次，避免重复计数，见 §4.2 L1926）。`input_embeds` 请求特殊处理：直接丢弃已生成 output_ids 重来（embeds 与新 token 无法混合重 prefill，L1339-1345 注释）。

---

## 3. `ScheduleBatch`：字段全景（L1468-1645）

`@dataclasses.dataclass`，字段注释自带分组标签，照抄如下并补充解读：

### 3.1 `=== Core ===`（L1472-1473）
`reqs: List[Req]`——**唯一权威来源**，ForwardBatch 的 lora_ids/rids/grammars/positions 全部从它派生。

### 3.2 `=== Global config and shared resources ===`（L1475-1489）
`req_to_token_pool / token_to_kv_pool_allocator / tree_cache / model_config / enable_overlap / device`：引擎级单例引用，每个批实例都带着（方便任何方法直接访问内存池）。空 running_batch 只有 `reqs=[] + batch_is_full`，其余为默认 None。

### 3.3 `=== Batch-variant scheduler state ===`（L1491-1529）
调度器私有、ForwardBatch 不读：`batch_is_full`（跳过 prefill 检查的缓存标志）、`chunked_req/contains_last_prefill_chunk`（chunked prefill）、`decoding_reqs`（mixed batch 携带的 decode 请求）、split prefill 三件套、`req_pool_indices_cpu`（GPU 镜像的 CPU 副本，overlap 工具用）、FPM/指标字段。

### 3.4 `=== GPU tensors crossing to ForwardBatch ===`（L1531-1567）
**批的"模型输入张量"**：`input_ids [b]`（decode 时 1 token/req；extend 时是所有请求 extend 段的拼接扁平张量）、`input_embeds`、`req_pool_indices [b]`、`seq_lens [b]`、`orig_seq_lens`（Qwen-1M）、`out_cache_loc`（本批新分配的 KV slot，extend 时长度 = extend_num_tokens，decode 时 = bs）、mamba track/COW/clear 三组、encoder-decoder 的 `encoder_lens/encoder_out_cache_loc`、logprob 的 `extend_input_logprob_token_ids`。

### 3.5 `=== Config / flags ===`（L1569-1605）
`forward_mode`（ForwardMode 枚举）、DP-attention 协调字段（`is_extend_in_batch/can_run_dp_cuda_graph/tbo_split_seq_index`）、`return_logprob/is_prefill_only/spec_algorithm/has_grammar/dllm_config`、`seq_lens_sum/extend_num_tokens`。

### 3.6 `=== Host metadata ===`（L1607-1631）
CPU 侧镜像与列表：`seq_lens_cpu`、`multimodal_inputs`、`top_logprobs_nums/token_ids_logprobs`、encoder CPU 列表、`prefix_lens/extend_lens/extend_logprob_start_lens`（extend 专有的三列表）、`global_num_tokens`（DP attention 下全局批形状）。

### 3.7 `=== Compound ===` 与 `=== One-shot ===`（L1633-1644）
`sampling_info: SamplingBatchInfo`（惩罚器/grammar mask 的批化容器）、`spec_info: SpecInput`（投机解码批信息）；`seq_lens_cpu_cache/capture_hidden_mode/return_hidden_states_before_norm` 是**一次性覆盖项**——`ForwardBatch.init_new` 消费后立刻置回默认（forward_batch_info.py L457-465 的"契约"注释）。

这个分组成员注释本身就是最好的架构文档：**哪些字段过河到 ForwardBatch（crossing）、哪些留在调度侧（scheduler state）、以什么形式过河（GPU tensor / by-value 标志 / host 列表 / 复合对象）**，一目了然。

---

## 4. `ScheduleBatch` 核心方法 I：构造与 extend

### 4.1 `init_new()`（L1646-1679）

类工厂：从 `reqs` 归纳出批级布尔（`return_logprob = any(...)`、`is_prefill_only = all(...)`、`has_grammar = any(...)`），绑定资源引用。scheduler 在三处调用它：新 prefill 批、hisparse decode 批（scheduler.py L2316）、以及 DP-attention 的 idle 批。

### 4.2 `prepare_for_extend()`（L1808-2107）——prefill 批的物化

这是本文件最长的方法（300 行），scheduler 的 `_get_new_batch_prefill_raw` 在 admission 通过后调用。逐段：

**① 从 Req 列表构造 CPU 输入**（L1815-1851）：

```python
input_ids  = [r.fill_ids[len(r.prefix_indices):] for r in reqs]  # 每个请求只取"新算"段
seq_lens   = [len(r.fill_ids) for r in reqs]                      # 完整长度（含前缀）
prefix_lens = [len(r.prefix_indices) for r in reqs]
extend_num_tokens = sum(...)                                      # 全批新算 token 总数
```

随后 `flatten_arrays_to_int64_tensor`（L1844）把变长列表拍平成一张 GPU int64 张量——extend 批的 `input_ids` 是**拼接的扁平张量**，各请求边界由 `extend_lens` 前缀和隐含（注意力 kernel 靠 `extend_seq_lens/extend_prefix_lens` 还原变长结构）。所有 H2D 拷贝都走 `pin_memory + non_blocking=True` 的异步路径（`_pin = is_pin_memory_available(...)` L1843）。

**② KV 分配 + 写映射表：`alloc_for_extend(self)`**（L1867-1869，实现在 mem_cache/common.py L429-492）：

1. `batch.maybe_evict_swa()`：先释放滑窗外的 SWA token；
2. `alloc_req_slots`：给每个请求分配 `req_to_token_pool` 行槽（mamba 池不够时先 evict 树缓存）；
3. `alloc_token_slots / alloc_paged_token_slots_extend`：分配 `extend_num_tokens` 个 KV slot（页分配时按 `prefix_lens/seq_lens/last_loc` 做页对齐续页），失败抛 OOM 异常（带池状态 pretty_print）；
4. **`write_cache_indices`（common.py L104-150）把映射写入 `req_to_token` 大表**：每个请求行 `[0, prefix_len)` 写入 `prefix_indices`（复用旧 KV 的 slot），`[prefix_len, seq_len)` 写入本批 `out_cache_loc` 的对应切片。GPU 路径用 Triton kernel `write_req_to_token_pool_triton`（common.py L54-101，每个请求一个 program，先拷前缀指针再按 extend_lens 前缀和偏移拷新段）；无 Triton 后端时逐请求 `req_to_token_pool.write`。

**③ 逐请求字段搬运**（L1884-2003）：

- `req.kv_committed_len = req.kv_allocated_len = seq_len`（L1890-1891）：本 extend 块全部提交；
- `input_embeds` 按 `[pre_len, pre_len+extend_input_len)` 切片（chunk 截断时 fill_ids 被截而 embeds 没截，L1894-1899 注释）；
- `positional_embed_overrides` 的绝对位置换算成本批相对位置（L1901-1919）；
- **cached_tokens 统计**（L1926-1955）：只在首次（`retracted_stain` 为 False）累计 `pre_len - already_computed`，并一次性把命中拆成 device/host/storage 三源（HiCache 指标）；
- mamba extra buffer 的 track 三元组（L1957-1961）；
- logprob token ids 推导（L1963-2003）：要为 extend 段的每个位置准备"下一个 token"作监督目标，块尾越界用 0 padding（注释里的 chunk 图解值得看）。

**④ 批字段落位**（L2026-2107）：`input_ids/req_pool_indices/out_cache_loc/seq_lens_sum` 等；多模态张量搬 GPU；MIS 分隔符张量化；`SamplingBatchInfo.from_schedule_batch`（L2104）组装采样信息（温度/惩罚/grammar 的批化）。

（`prepare_encoder_info_extend` L1690-1806 处理 encoder-decoder：把图像 token 从 decoder 序列里剥出来单独分配，逻辑独立可跳读。）

### 4.3 `mix_with_running()`（L2217-2247）——mixed chunked prefill

把 decode 中的 running_batch 并入本 prefill 批：`forward_mode = MIXED`；decode 请求 `fill_ids` 刷新、`set_extend_input_len(1)`（伪装成 1-token extend）；拼接 `input_ids/out_cache_loc`，`prefix_lens` 追加 `len(origin)+len(output)+delta`（overlap 时 `delta=0`：输出 token 有一拍延迟，L2232-2233 注释）。这样一批 EXTEND 前向同时完成"prefill 新请求 + decode 老请求"，是 chunked prefill 时代的经典吞吐优化。

---

## 5. `ScheduleBatch` 核心方法 II：decode、filter/merge、retract

### 5.1 `prepare_for_decode()`（L2417-2511）

decode 批每步前调用，比 extend 轻得多：

1. `forward_mode = DECODE`，清 `input_embeds`/CP metadata；
2. spec-v2 走 `draft_input.prepare_for_decode`，spec-v1 直接返回（decode 批在投机前向内部准备，L2428-2436）；
3. 惩罚器累积：overlap 下**手动构造 delayed_output_ids**（L2438-2455）——因为 overlap 的 input_ids 此时还是哨兵，真正的上一 token 要从 `req.output_ids[-1]` 取；
4. `alloc_for_decode(self, token_per_req=1)`（mem_cache/common.py L524-564）：分配 bs 个 slot，并把 `req_to_token[req_pool_indices, seq_lens] = out_cache_loc`（写新 token 的 KV 落点）；页分配时用 `last_loc`（每请求最后一个 slot）判断是否需要开新页；
5. `kv_committed_len += 1; kv_allocated_len += 1`（L2471-2474）；
6. **overlap 语义分叉**（L2476-2485）：`self.seq_lens = self.seq_lens + 1`（**新张量**）vs 非重叠的 `add_(1)`（原地）。新张量是为了不污染还挂在 result_queue 里的上一拍批快照（L2477-2478 注释）；
7. `seq_lens_sum = None`：**惰性重算标记**——ForwardBatch.init_new 需要时才 `sum(seq_lens_cpu)`（forward_batch_info.py L511-512），避免每步全量归约。

### 5.2 `filter_batch()`（L2513-2592）与 `merge_batch()`（L2594-2640）

**filter**：剔除已完成（`req.finished()`）/chunked 排除项/指定外的请求。默认派生 `keep_indices`，也可以显式传入（retract、优先级抢占用）。GPU 张量统一 `tensor[keep_indices_device]` 高级索引重排；`out_cache_loc/mamba_*` 直接置 None（下轮 prepare 会重分配）；`seq_lens_sum=None` 同上；`sampling_info/spec_info` 各自实现 filter。两个早退分支（全剔/全留）避免无谓索引。

**merge**：把 prefill 批并入 running 批。注意 L2595-2598 注释的顺序约束：**sampling_info 必须先于 `reqs` 合并**（惩罚器 merge 依赖合并前的 reqs 布局）。GPU 张量 `torch.cat`，logprob 参数列表按"谁有谁没有"补零对齐（L2621-2629），布尔标志 OR/AND 传播（`is_prefill_only` 是 AND——混入一个生成请求整批就不再是 prefill-only）。

**`copy()`**（L2642-2671）：overlap 模式下 run_batch 后压入 result_queue 的**浅快照**——只保留 process_batch_result 需要的字段，`reqs` 切片防后续 filter/merge 原地篡改。

### 5.3 decode 内存预检：`check_decode_mem` / `new_tokens_required_next_decode`（L2248-2298）

判断"全批再 decode 一步需要多少 KV"：
- 非页分配：只数 `kv_committed_len % page_size == 0` 的请求（要开新页的数量 × page_size）——**已有页内空位的请求免费**（L2258-2260）；
- spec-v1：按 `(num_steps × topk, num_draft_tokens)` 上限估算并做页对齐（L2265-2280）；
- spec-v2：`_new_tokens_required_next_decode_spec_v2`（L2282）用 `kv_committed_len + 2*alloc_len - kv_allocated_len` 做"紧致"估计，与 eagle_info_v2 的实际分配对齐。

`check_decode_mem` 先 `evict_from_tree_cache` 腾 evictable，再比较 `available_size`。返回 False 即触发 retract。

### 5.4 `retract_decode()`（L2308-2370）与 `release_req()`（L2372-2388）

retract 的批内实现（scheduler.py `update_running_batch` 的被调方）：

- 排序：`output_ids` 多者优先被踢（生成多的沉没成本反而低——它们重新 prefill 时 radix 命中长；反过来 origin 长的请求更难塞回去，先保留），投机解码因 filter_batch 只能从尾部删而放弃自定义排序（L2314-2326 两段 TODO 注释）；
- 循环 `pop + release_req` 直到 `check_decode_mem` 通过；`release_req` → `release_kv_cache(req, tree_cache, is_insert=False)`（**不插树**：空间立刻要用，L2341-2342）+ 立即 `evict_from_tree_cache(remaining × SGLANG_RETRACT_DECODE_STEPS)` 给幸存者预留步数 + `reset_for_retract`；
- 极端情况：最后一个请求也放不下 → 优雅 abort（HTTP 500）而非 crash scheduler（L2344-2361）;
- 返回 `(retracted_reqs, 新 new_token_ratio 估计, reqs_to_abort)` 三元组，新比例由 `NewTokenRatioTracker.estimate_new_token_ratio_after_retract` 从幸存请求的"剩余生成量/已占 KV"反推——retract 之后调度器对未来的预估立刻收紧。

### 5.5 `maybe_evict_swa()` / `_evict_swa()`（L2673-2767）

hybrid-SWA（滑动窗口注意力）模型专属：decode 时每 `eviction_interval` 步把滑窗之外的 SWA KV 主动 free（radix 与 chunk cache 的边界差异见 Req L716-721 注释）；页对齐的驱逐前沿特意留一页余量，防止叶子节点全部 tombstone 化导致 SWA 内存泄漏（L2742-2751 长注释，配套 swa_radix_cache 的防御代码）。overlap 下首步不驱逐（上一 extend 批还在 GPU 上跑，L2695-2697）。

### 5.6 其他原语

- `prepare_for_idle()`（L2394）：DP-attention 空转批——全空张量 + IDLE 模式，让没有请求的 rank 也能参与集体通信；
- `retract_all()`（L2300）、`prepare_for_split_prefill()`（L2212，PD 复用）；
- `is_spec_v2` property（L2411）：`enable_overlap and not spec_algorithm.is_none()`——spec-v2 与 overlap 深度绑定的又一处体现。

---

## 6. ForwardBatch：过河之后的形态（forward_batch_info.py）

`ForwardBatch.init_new(batch: ScheduleBatch, model_runner)`（该文件 L452-551+）做三件事：

1. **消费一次性覆盖**（capture_hidden_mode / seq_lens_cpu_cache / return_hidden_states_before_norm）并复位——SB 上的注释契约在这里兑现；
2. **按引用别名（alias by reference）SB 的 GPU 张量**：`input_ids/req_pool_indices/seq_lens/out_cache_loc/...` 不拷贝直接用（L523-537 "Inputs aliased by reference from ScheduleBatch"）；decode/idle 模式下 extend 专有字段置 None；`seq_lens_sum` 若为 None 就地重算并**写回 SB**（L511-512，缓存语义）；
3. 派生模型执行需要的额外元数据（positions、extend 前缀和、CUDA graph 形状信息等，在 ModelRunner 侧完成）。

`ForwardMode` 枚举（该文件 L75-101）是 SB/FB 共享的批类型语言：`EXTEND`（含前缀的 prefill）/`DECODE`/`MIXED`（mixed chunk）/`IDLE`/`TARGET_VERIFY`、`DRAFT_EXTEND(_V2)`（投机）/`PREBUILT`（PD decode 预装 KV）/`SPLIT_PREFILL`（PD 复用）/`DLLM_EXTEND`。其 `is_extend()/is_prefill()` 等 predicate（L103-159）在 scheduler 的分派逻辑里反复出现——**MIXED/DRAFT_EXTEND/TARGET_VERIFY/DLLM_EXTEND 都算"extend 家族"**，这是读 `get_next_batch_to_run` 时容易踩的坑。

---

## 7. 与其他模块的交互

| 对端 | 交互点 |
|---|---|
| `scheduler.py::Scheduler` | 唯一的写者：init_new / prepare_for_* / filter / merge / retract / copy 全部由 event loop 驱动 |
| `mem_cache/common.py` | `alloc_for_extend/alloc_for_decode/release_kv_cache/evict_from_tree_cache` + Triton kernel `write_req_to_token_pool_triton`（req→token 映射的真正写入者） |
| `mem_cache/*`（allocator/radix_cache/memory_pool） | `match_prefix/cache_unfinished_req/cache_finished_req/inc_lock_ref`；`prefix_indices/last_node` 的类型来自树缓存 |
| `model_executor/forward_batch_info.py` | `ForwardBatch.init_new` 消费 SB；`ForwardMode` 共享 |
| `sampling/sampling_batch_info.py` | `from_schedule_batch` 组装；filter/merge 的孪生方法 |
| `speculative/*`（eagle_info 等） | `spec_info.prepare_for_decode/filter_batch/merge_batch`；spec-v2 与 overlap 的紧耦合 |
| `disaggregation/decode_schedule_batch_mixin.py` | `ScheduleBatchDisaggregationDecodeMixin`：PD decode 侧的 PREBUILT 批扩展 |
| `scheduler_components/batch_result_processor.py` | 读 `req.output_ids/finished()/logprob` 等完成输出闭环 |
| `managers/overlap_utils.py` | FutureMap 对 `input_ids` 哨兵的 resolve；SB GPU 张量的两拍生命期约定 |

---

## 8. 关键设计决策

1. **CPU 调度视图与 GPU 执行视图分层**：ScheduleBatch 大多数字段在 CPU（Python list / CPU tensor），只把模型必需的输入做成 GPU 张量，且**同类字段保持 GPU/CPU 双镜像**（`seq_lens/seq_lens_cpu`、`req_pool_indices/req_pool_indices_cpu`）。调度决策（admission、retract、DP 同步）永远在 CPU 镜像上做，避免同步 GPU。
2. **扁平拼接 + 边界表**的 extend 表示：变长请求段拼成一维 `input_ids`，边界信息放 `prefix_lens/extend_lens`——这既匹配 paged KV 分配器的输出（`out_cache_loc` 天然扁平），也匹配 FlashAttention 的 varlen 前缀和接口。
3. **惰性重算 + 置空**代替维护：`filter/merge` 后 `out_cache_loc=None`、`seq_lens_sum=None`，等下一次 prepare/init_new 重算/重分配。状态字段越少越不容易在 overlap 的乱序写放下出错。
4. **KV 双账本（committed/allocated）**把"radix cache 可回收段"与"超额分配段"的释放路径统一成两个 pop 函数，投机解码、strip_thinking_cache 等多分配场景都复用同一机制（L1009-1019 断言保证幂等）。
5. **两段式完成（to_finish → finished_reason）**与 filter 的时序契约：完成判定只能在 process_batch_result 里落定，中途 abort 走暂存——这是事件循环异步化的必要代价。
6. **retract 是一等公民**：`reset_for_retract` 精确清零 30+ 字段、cached_tokens 的 `retracted_stain` 防重复计数、input_embeds 请求的丢弃重来策略——处处体现"请求随时可能被打回重排队"的假设。
7. **pin_memory + non_blocking + Triton 化映射表写入**：所有 H2D 都异步；`req_to_token` 的批量写入下沉为单个 Triton kernel（每请求一 program），是调度开销可扩展的关键。
8. **页分配意识贯穿始终**：`ceil_paged_tokens`、`last_loc` 续页、`kv_committed_len % page_size` 免费步、SWA 驱动留一页余量——page_size>1 时几乎每个内存字段都有对齐语义。

---

## 9. 阅读建议

**第一遍（数据结构）**：只读两个类的字段区（L646-973、L1468-1645），对照 §2/§3 的分组表；重点吃透 `fill_ids/prefix_indices/extend_input_len` 三角关系与 KV 双账本。

**第二遍（一次请求的一生）**：沿着 scheduler 调用序读方法体：`init_next_round_input`（L1043）→ `prepare_for_extend`（L1808）→ 每步 `prepare_for_decode`（L2417）→ `update_finish_state`（L1271）→ filter/merge（L2513/L2594）。用 gdb/日志在 `_get_new_batch_prefill_raw` 打断点，打印同一 rid 的 `fill_ids/extend_input_len` 演化。

**第三遍（压力路径）**：`check_decode_mem`（L2295）→ `retract_decode`（L2308）→ `reset_for_retract`（L1303）→ 重新入队后的 `init_next_round_input`。配合 `SGLANG_TEST_RETRACT=1 SGLANG_TEST_RETRACT_INTERVAL=n` 强制演练。

**第四遍（overlap 契约）**：在 `prepare_for_decode` 里对比 `seq_lens + 1`（新张量）与 `add_(1)`（原地）两个分支；读 `copy()`（L2642）与 scheduler.py 的 `record_batch_in_overlap`，理解"快照保哪些字段、为什么 reqs 要切片"。

**调试入口**：`__str__`（L2769）与 `__repr__`（L1433）可直接打印批/请求；`SGLANG_RADIX_FORCE_MISS` 验证前缀缓存收益；`log_time_stats`（L1366）输出每请求全链路耗时分解。

**延伸阅读**：`mem_cache/common.py`（alloc/write/release 三族函数）、`forward_batch_info.py`（ForwardBatch.init_new 全文）、`sampling/sampling_batch_info.py`（惩罚器批化）、`managers/overlap_utils.py`（哨兵 resolve 的 CUDA kernel）。

---

## 附录 A：Req 字段速查表（按行号分组）

| 组 | 字段 → 行号 | 备注 |
|---|---|---|
| 输入输出 | `origin_input_ids` 691 / `origin_input_ids_unpadded` 692 / `output_ids` 698 / `fill_ids` 700 / `seqlen` 975 / `is_prefill_only` 980 | `array("q")` 可拼接 |
| KV 账本 | `kv_committed_len` 708 / `kv_allocated_len` 709 / 两个 freed 标志 710-711 / `pop_committed_kv_cache` 1001 / `pop_overallocated_kv_cache` 1009 | 释放幂等由断言保证 |
| SWA | `swa_evicted_seqlen` 721 / `swa_uuid_for_lock` 820 / `swa_prefix_lock_released` 822 | 配合 §5.5 |
| 批内下标 | `extend_batch_idx` 724 / `decode_batch_idx` 725 | SWA 驱动节奏用 |
| 推理内容 | `require_reasoning` 731 / `_is_reasoning_over`+`reasoning_tokens` 734-735 / `update_reasoning_tokens` 1419 | think 标签统计 |
| 采样 | `sampling_params` 743（注入 `__req__` 自引用）/ `custom_logit_processor` 744 | |
| 缓存键 | `extra_key` 753（cache_salt+lora）/ `lora_id` 754 / `routing_key` 755 | 决定 radix 命中 |
| 池槽位 | `req_pool_idx` 758 / mamba 六件套 759-771 | mamba 延迟 COW 见 §4.2 |
| finish | `finished_reason` 775 / `finished_len` 777 / `to_finish` 783 / `finished()` 1039 / `update_finish_state` 1271 | 两段式（§2.4） |
| 增量解码 | `surr_offset/read_offset` 798-799 / `decoded_text` 800 / `init_incremental_detokenize` 1141 / `tail_str` 1161 / `check_match_stop_str_prefix` 1177 | 窗口抗 BPE 清理 |
| 多模态 | `multimodal_inputs` 803 / `extend_image_inputs` 1033 / mrope 修复 1116-1129 | |
| 前缀视图 | `prefix_indices` 807 / `extend_input_len` 809 / `extend_logprob_start_len` 811 / `last_node`-`best_match_node` 813-815 / `host_hit_length` 816 / `storage_hit_length` 818 / `cache_protected_len` 824 | `init_next_round_input` 1043 刷新 |
| chunked | `inflight_middle_chunks` 829 | >0 = prefill 未完 |
| retract | `is_retracted` 832 / `retracted_stain` 834 / `retraction_count` 925 / `reset_for_retract` 1303 | |
| 流式游标 | `send_token_offset` 837 / `send_decode_id_offset` 838 / `send_output_token_logprobs_offset` 841 | stream_interval 切片 |
| logprob | `return_logprob` 844 / `logprob_start_len` 846 / `logprob: ReqLogprob` 847 / temp_* 暂存 856-860 | 结果容器 L623 |
| 观测输出 | `hidden_states` 872 / `routed_experts` 880 / `indexer_topk` 885 / `embedding` 892 | |
| grammar | `grammar_key` 895 / `grammar`（可为 Future）896 / `grammar_wait_ct` 899 | 异步编译 |
| 命中统计 | `cached_tokens` 902 / `already_computed` 903 / device/host/storage 三分 906-911 | |
| 投机统计 | `spec_verify_ct` 914 / `spec_num_correct_drafts` 917 / 直方图 922 / `update_spec_correct_drafts_histogram` 1021 | |
| 打点 | `time_stats` 930-935 / `log_time_stats` 1366 | 全链路分解 |
| PD 分离 | `bootstrap_host/port/room` 939-941 / `skip_radix_cache_insert` 942 / `disagg_kv_sender` 943 / `routed_dp_rank` 945 / `start_send_idx` 953 / `tmp_end_idx` 958 / `metadata_buffer_index` 959 | |
| abort | `set_finish_with_abort` 1405（origin 截成 1 token 跳过长 prefill） | |
| KV 换入换出 | `offload_kv_cache` 1347 / `load_kv_cache` 1356 | PD decode offload |

## 附录 B：ScheduleBatch 方法索引

| 方法 | 行号 | 调用者 |
|---|---|---|
| `init_new` | 1647 | scheduler 组新 prefill 批 / hisparse / DP idle 批 |
| `batch_size/is_empty` | 1681/1684 | 处处 |
| `prepare_encoder_info_extend/decode` | 1690/2390 | encoder-decoder 模型 |
| `prepare_for_extend` | 1808 | ★ prefill 物化（§4.2） |
| `_mamba_radix_cache_v2_req_prepare_for_extend` | 2109 | mamba 前缀缓存 v2 |
| `_collect_deferred_mamba_cow_and_clear` | 2190 | 延迟到 forward stream 的 COW/清零 |
| `prepare_for_split_prefill` | 2212 | pdmux |
| `mix_with_running` | 2217 | mixed chunk（§4.3） |
| `new_tokens_required_next_decode` (+spec_v2) | 2248/2282 | §5.3 内存预检 |
| `check_decode_mem` | 2295 | update_running_batch |
| `retract_all` | 2300 | pause/flush 前 |
| `retract_decode` | 2308 | ★ §5.4 |
| `release_req` | 2372 | retract/抢占 |
| `prepare_for_idle` | 2394 | DP-attention |
| `is_spec_v2` | 2411 | 处处分支 |
| `prepare_for_decode` | 2417 | ★ 每步 decode（§5.1） |
| `filter_batch` | 2513 | ★ 每步（§5.2） |
| `merge_batch` | 2594 | ★ prefill→decode 合并（§5.2） |
| `copy` | 2642 | overlap result_queue 快照 |
| `maybe_evict_swa` / `_evict_swa` | 2673/2732 | alloc 前（§5.5） |

## 附录 C：一个请求的全生命周期字段演化

把 §2.5 的例子扩展成完整旅程（prompt 5 token，max_new=3，无缓存命中，page_size=1）：

| 阶段 | 触发 | 关键字段变化 |
|---|---|---|
| 入队 | `_add_request_to_queue` | `finished_reason=None`，waiting_queue 尾部 |
| 组批 | `init_next_round_input` | `prefix_indices=[]`，`extend_input_len=5` |
| prefill 物化 | `prepare_for_extend` | `input_ids=[a..e]`(扁平)，`out_cache_loc=5 slot`，`kv_committed_len=5`，`req_pool_idx` 分配，`req_to_token[req_idx,0:5]=out_cache_loc` |
| 首步输出 | `process_batch_result_prefill` | `output_ids=[x1]`；未完成则 `maybe_cache_unfinished_req`（这里一次性 prefill 完，不触发） |
| merge | `get_next_batch_to_run` | 从 last_batch 并入 running_batch（`merge_batch`） |
| decode 步 1 | `prepare_for_decode` | `input_ids=[x1]`，alloc 1 slot，`seq_lens 5→6`，`kv_committed_len=6` |
| decode 步 2 | 同上 | `output_ids=[x1,x2]`，`seq_lens=7` |
| 完成 | `update_finish_state` | 命中 eos → `FINISH_MATCHED_TOKEN(x3)` |
| 释放 | `release_kv_cache` | `cache_finished_req`（把 `[0, kv_committed_len)` 插 radix 树）；`pop_overallocated_kv_cache` free 超额段；`req_to_token_pool.free(req)` 回收行槽 |
| 输出 | `stream_output` | 客户端收到 finish_reason JSON（§1 的 5 类） |

若 decode 步 2 时 KV 不足被 retract：`release_req(is_insert=False)` → KV 直接 free 不进树 → `reset_for_retract`（全字段归零）→ 重新入 waiting_queue → 下次组批时 `init_next_round_input` 重新 match_prefix——**如果前缀还在树里（别的请求插过），retract 的重算成本几乎为零**；这正是 SGLang retract 策略的底气。

## 附录 D：ForwardMode 谓词速查（forward_batch_info.py L103-173）

| 谓词 | 覆盖的模式 | 调度语义 |
|---|---|---|
| `is_extend()` | EXTEND/MIXED/DRAFT_EXTEND/TARGET_VERIFY/SPLIT_PREFILL/DLLM_EXTEND | "prefill 家族"：`get_next_batch_to_run` L2388 据此决定 merge |
| `is_decode()` | 仅 DECODE | process_batch_result 分派 |
| `is_decode_or_idle()` | DECODE/IDLE | ForwardBatch extend 字段置 None 的条件 |
| `is_cuda_graph()` | DECODE/TARGET_VERIFY/IDLE/DLLM_EXTEND | 可走 CUDA graph 的批形状 |
| `is_idle()` | IDLE | DP-attention 空转 |
| `is_mixed()` | MIXED | mixed chunk 处理分支 |
| `is_extend_without_speculative()` | EXTEND/MIXED/SPLIT_PREFILL/DLLM_EXTEND | 排除 spec 的 prefill |
