# 深度解析：`python/sglang/srt/mem_cache/memory_pool.py`

> 源码: python/sglang/srt/mem_cache/memory_pool.py @ commit ec075d8bc

这是 SGLang KV Cache 内存管理的物理层：定义了"请求→token 槽位"的映射表（`ReqToTokenPool`）、Mamba/线性注意力混合架构的状态池（`MambaPool`/`HybridReqToTokenPool`），以及真正持有 KV 字节的缓冲区家族（`KVCache` ABC 及 `MHATokenToKVPool`/`MLATokenToKVPool`/`DSATokenToKVPool` 等 7 个实现）。文件全长 2270 行，覆盖 MHA、MLA（DeepSeek 系）、DSA（稀疏注意力索引）、FP4/FP8 量化 KV、NPU/CPU 后端等多种形态。需要特别注意：模块 docstring（L18-25）描述的"两层内存池"中，`TokenToKVPoolAllocator`（槽位号分配器）在当前 commit 已迁至同目录的 **allocator.py**——本文件专注物理缓冲区与请求级映射，槽位管理语义将在"与其他模块的交互"一节结合 allocator.py 讲清。`alloc`/`free`/`available_size` 这组动词在本文件与 allocator.py 中各有出现，语义分层是理解 SGLang 显存治理的钥匙。

---

## 0. 全景：四层解耦的 KV Cache 体系

SGLang 把"KV Cache"这个词拆成了四个各司其职的组件（第 4 个在同目录其他文件）：

```
┌──────────────────────────────────────────────────────────────────┐
│ RadixCache (radix_cache.py)                                      │
│   前缀树：按 token 序列共享/复用 KV，决定"哪些槽位还有效、哪些可逐出" │
├──────────────────────────────────────────────────────────────────┤
│ TokenToKVPoolAllocator (allocator.py)                            │
│   槽位号管理：无分页版 alloc(n)→连续/离散 token 下标；              │
│   分页版 PagedTokenToKVPoolAllocator alloc_extend/alloc_decode    │
├──────────────────────────────────────────────────────────────────┤
│ KVCache 家族 (本文件 L701-2218)          ←—— 物理字节持有者        │
│   k_buffer/v_buffer/kv_buffer：[size+page_size, head_num, head_dim]│
│   提供 get/set_kv_buffer、move_kv_cache 等字节级操作               │
├──────────────────────────────────────────────────────────────────┤
│ ReqToTokenPool (本文件 L139) + MambaPool (L207)                   │
│   请求级映射：req_to_token[req_idx, :seq_len] = token 槽位号数组    │
│   Mamba 状态池：混合架构中每请求一份 conv/temporal 状态             │
└──────────────────────────────────────────────────────────────────┘
```

一次 decode step 的数据流：Scheduler 从 `RadixCache` 匹配前缀 → allocator 分配新 token 的槽位号写入 `Req.out_cache_loc` → `req_to_token` 映射表更新 → attention backend 用 `req_pool_indices` 读映射表拿到每请求的 token 槽位向量 → kernel 直接在 `KVCache` 缓冲区上 scatter/gather。

### 容量算例（以 MHATokenToKVPool 为例）

物理字节数公式（每层）：

```
k_buffer[layer] = (size + page_size) × head_num × head_dim × store_dtype.itemsize
v_buffer[layer] = (size + page_size) × head_num × v_head_dim × store_dtype.itemsize
总 = layer_num × (k + v)
```

以 Llama-3-70B（TP=8）为例：80 层、每卡 8 个 KV head（GQA，64 总 head / 8）、head_dim=128、bf16（2 字节）：

```
每 token 每卡 = 80 层 × 8 head × 128 dim × 2B × 2(K和V) = 655,360 B ≈ 0.625 MB
一张 80GB 卡留 20GB 给 KV → size ≈ 20GB / 0.625MB ≈ 32,000 tokens
```

这就是 `model_runner.py` 显存 profiling 反推 `max_total_num_tokens` 的算术。切 `--kv-cache-dtype fp8_e5m2` 后 itemsize 减半、容量翻倍（store_dtype=uint8，1 字节）；MLA（DeepSeek-V3：kv_lora_rank 512 + rope 128 = 640 维、单"head"）则每 token 每层仅 640×2B，比等价 MHA 小一个量级——这是 MLA 池单缓冲设计的商业意义。

---

## 1. 工具函数：KV 写入的多级分派

### `get_tensor_size_bytes`（L86-89）

递归求张量（或张量列表）字节数：`np.prod(t.shape) * t.dtype.itemsize`。所有 pool 的 `mem_usage` 统计和启动日志都经它。

### `_set_kv_buffer_impl`（L92-136）——一次 KV 写入的四条路径

这是所有非 MLA pool 写 KV 的公共底座，按平台/形态逐级降级：

1. **JIT `store_cache` kernel**（L105-113）：CUDA/HIP 且 K/V 行宽相同（`same_kv_dim`）且 `can_use_store_cache(row_bytes)` 时，把 K/V cache 与新算出的 k/v 都 `view(-1, row_dim)` 成二维行块，按 `indices` 整行拷贝——`row_bytes = head_num*head_dim*itemsize` 必须满足 kernel 的对齐/宽度约束（sglang.jit_kernel.kvcache 提供检测）。
2. **CPU AMX**（L115-123）：`torch.ops.sgl_kernel.store_cache_cpu`，x86 AMX 路径。
3. **CUDA Graph 捕获期双流 overlap**（L127-133）：`get_is_capture_mode()` 且有 `alt_stream` 时，K 写在当前流、V 写切到 alt 流并行——小 batch 下两次拷贝延迟叠加是可观测的，值得用 stream 并行抹掉；捕获期外不用（避免运行时流同步开销与图重放语义冲突）。
4. **朴素回退**（L134-136）：`k_cache[indices] = k`。

---

## 2. `ReqToTokenPool`（L139-204）——请求→token 槽位映射表

### 数据结构（L142-163）

```python
self.req_to_token = torch.zeros((self._alloc_size, max_context_len),
                                dtype=torch.int32, device=device)
self.free_slots = list(range(1, self._alloc_size))
```

- 形状 `(size+1, max_context_len)` 的 int32 大表：第 `i` 行就是第 `i` 个在飞请求的"token 槽位号数组"，`req_to_token[i, :len]` 即该请求前 `len` 个 token 各自的 KV 槽位。attention kernel（如 FlashInfer 的 page table 接口）直接把这张表的行切片当 page table 用。
- **slot 0 是 padding**（L154-156 注释）：`_alloc_size = size + 1`，free_slots 从 1 开始。CUDA Graph 的 padded batch 会把补齐出来的假请求的 `req_pool_indices` 默认填 0，假读假写全部落在第 0 行，无害。这个约定贯穿所有 pool（MambaPool L362、KVCache L913 同款注释）。
- 分配在 `TorchMemorySaverAdapter.region(GPU_MEMORY_TYPE_KV_CACHE)` 上下文里（L159）——RL 场景 `ReleaseMemoryOccupationReq(tags=["kv_cache"])` 归还显存时按 region 精确释放。

### 四个语义动词

- **`write(indices, values)`**（L165-166）：直接写表。chunked prefill/decode 时 Scheduler 把 `out_cache_loc` 段写入对应行。
- **`available_size()`**（L168-169）：`len(free_slots)`——还能接多少新请求，Scheduler 准入控制的上界之一。
- **`alloc(reqs: list[Req]) -> Optional[List[int]]`**（L171-196）：本文件最精妙的方法。它接收的是 **Req 对象列表**而非数字：
  - L174：先挑出 `req_pool_idx is not None` 的请求——这些是 **chunked prefill 跨 chunk 续跑**的请求，直接复用原槽位（映射表前缀还在，续写即可）；
  - L181-184：断言复用者必须 `inflight_middle_chunks > 0 or kv_committed_len > 0`（正在分块中或已有提交的 KV），防止空槽位被误"复用"；L176-180 的注释显示这条约束曾更严（一个 batch 只允许一个 chunked 复用者，PR #20476 放松）；
  - L187-188：新请求数超过 free_slots 则**整体返回 None**（不部分分配），由 Scheduler 决定 retract 还是等待；
  - L192-195：把槽位号写到每个 Req 的 `req_pool_idx` 字段上并返回。
- **`free(req)`**（L198-201）：单请求归还，槽位号 append 回 free_slots，`req.req_pool_idx = None`（重复 free 会在下次 alloc 的断言处炸出）。
- **`clear()`**（L203-204）：flush_cache 时全量重置。

注意 free_slots 是 **Python list**（FIFO 语义，append/pop 尾部），而 MambaPool 用 **GPU tensor**——前者由 CPU 侧 Scheduler 串行调用，后者需要在 forward stream 上被 kernel 消费，介质选择反映调用上下文。

---

## 3. `MambaPool`（L207-497）——线性注意力状态池

Mamba/GDN 类混合架构不存 per-token KV，而是每请求一份**滚动状态**（conv 窗口 + SSM temporal 状态），语义上更接近 ReqToTokenPool 的"每请求一槽"。

### 两个 frozen dataclass（L208-235）

- `State`：`conv: List[Tensor]` + `temporal: Tensor`。`at_layer_idx(layer)`（L213-224）切片出单层状态，**用 `dataclasses.fields()` 而非 `vars()`**——L216 注释点明：`vars()` 会导致 torch.compile graph break。`mem_usage_bytes()`（L226）同样走 fields。
- `SpeculativeState(State)`：投机解码 verify 阶段需要**每个 draft token 一份中间 SSM 状态和 conv 窗口**（L310-339 的两个缓冲，形状 `[num_layers, spec_state_size+1, num_draft_tokens, ...]`），accept 后从中间状态恢复，避免整段重算。

### 缓冲区布局与平台分支（L237-367）

主缓冲形状 `(num_mamba_layers, size+1, ...)`：层维在最前，每层一张"每请求一行"的状态表；conv 可能有多组（List），temporal 单张。三个平台分支：NPU 的 conv state 有专用布局（L282-289）；CPU AMX 为 kernel 优化换了布局（L291-295）；分配同样走 memory saver region + nvlink disagg 专用 custom mem pool（L261-272）。slot 0 照例 padding（L362 注释）。

### 语义动词与生命周期

- `alloc(need_size) -> Optional[Tensor]`（L379-385）：返回 free_slots 张量切片（GPU tensor！）。
- `free(free_index)`（L402-405）：`torch.cat` 拼回。
- **`clear_slots(indices)`**（L387-400）：归零状态。docstring 强调 "Must run on forward stream"——状态池不像 KV 池可以只还号不清水，脏状态复用会直接污染下一个请求。
- `copy_from(src, dst)`（L412-419）：槽位间整状态拷贝——radix cache 命中/请求迁移（如 PD 分离 bootstrap）时把源请求状态克隆给新槽位。
- `get_cpu_copy`/`load_cpu_copy`（L421-441）：CPU offloading，双侧 `synchronize()` 保证 non_blocking 拷贝完成。
- **`get_contiguous_buf_infos()`**（L443-470）：给 **RDMA 注册**用的三元组（每层 data_ptr/nbytes/单页 nbytes）。刻意排除投机解码的 intermediate 缓冲（L452-454 注释：尺寸不同、不应传输）——PD 分离只搬"定态状态"。
- `get_state_dim_per_tensor()`（L472-497）：指出状态张量第 2 维（TP 切的那维：conv_dim/tp、num_heads/tp）的尺寸，跨机传输时按 TP 分片用。

---

## 4. `HybridReqToTokenPool`（L500-698）——混合架构的复合池

组合而非继承的典范：继承 `ReqToTokenPool`（复用映射表逻辑），内部持有 `MambaPool`（L551），用两张映射张量把两个池的槽位空间缝合：

- `req_index_to_mamba_index_mapping`（L564-566）：req 槽位 → mamba 槽位，int32，`get_mamba_indices()`（L627）供 forward 时查。
- `req_index_to_mamba_ping_pong_track_buffer_mapping`（L568-574）：overlap schedule 开启时 buffer_size=2（L526）——两步流水需要一个请求占**两个** mamba 状态槽（当前步用 A、下一步预写 B），关掉则 1。

**`alloc(reqs)`**（L583-625）在父类之上叠加 mamba 槽分配：`req.mamba_pool_idx is not None` 的请求（radix cache 续跑/继续 chunked）复用原槽（L591 注释），否则 `mamba_pool.alloc(1)` 并置 `mamba_needs_clear=True`（L599，首次使用前要清零脏状态）。断言消息直接给出调参指引（L597：`try to increase --mamba-full-memory-ratio or --max-mamba-cache-size`）——运维友好。

**`free_mamba_cache(req, keep_slot)`**（L651-690）：释放 mamba 槽 + 可选保留 ping-pong 双槽中的一个（keep 语义在 L663-689 展开为切片运算，注释特意说明"避免对 device tensor 做 Python list 高级索引"）。

**`mamba2_layer_cache(layer_id)`**（L630-634）：先 `layer_transfer_counter.wait_until(layer_id - start_layer)` 再给状态——这是 PD 分离**逐层传输**的同步钩子：第 N 层状态没传完就阻塞在这，传完放行，实现传输与计算的流水重叠。

---

## 5. `KVCache` ABC（L701-794）——所有物理 KV 池的合同

构造参数合同（L702-740）：`size`（token 容量）、`page_size`、`dtype`（逻辑 dtype）、`layer_num`、`start_layer/end_layer`（**层区间**——pipeline parallel 或跨机分离时本 pool 只负责模型的一部分层）、`enable_memory_saver`。

三个关键通用语义：

1. **`store_dtype` 与 `dtype` 分离**（L718-722）：FP8 时 `store_dtype = torch.uint8`，注释直言原因——*"Tensor.index_put is not implemented for torch.float8_e5m2"*。物理上按 uint8 存字节，读出时 `view(dtype)` 还原成 fp8 视图（见 MHATokenToKVPool L1029-1031）。所有量化池（FP4 系）沿用此模式。
2. **逐层传输钩子**：`register_layer_transfer_counter`（L784-785）注册 `LayerDoneCounter`；各子类的 `get_key_buffer/get_value_buffer` 开头都有 `wait_until(layer_id - start_layer)`——**读缓冲区即同步点**，注意力层读 KV 前自然等待该层 KV 迁移完成，无需额外调度代码。
3. **辅助设施**：`cpu_offloading_chunk_size = 8192`（L732，分块 offload 防峰值显存）、nvlink disagg 的 custom mem pool（L737-740）、`_finalize_allocation_log`（L742-760，统一的启动日志与 mem_usage 统计，兼容 K/V 分开报和合并报两种返回形态）。

抽象接口：`get_key_buffer/get_value_buffer/get_kv_buffer/set_kv_buffer`（L762-782）。

---

## 6. `MHATokenToKVPool`（L797-1147）——标准 MHA 池，读它就懂八成

### 缓冲区布局（L905-948）

```python
self.k_buffer = [torch.zeros((self.size + self.page_size, head_num, head_dim),
                             dtype=self.store_dtype, device=...) for _ in range(layer_num)]
self.v_buffer = [ ... (size+page_size, head_num, v_head_dim) ... ]
```

- **每层一对独立张量**（List[Tensor] 而非一张 4D 大张量）：层维留在 Python 列表层面，使得"单层读写"零偏移算术、且 `get_contiguous_buf_infos` 能给出每层独立的 RDMA 注册地址。代价是跨层操作需要 kernel 侧指针表（见下）。
- 第一维 `size + page_size`：slot 0..page_size 是 padding 区（L913 注释），分页分配器保证用户槽位号从对齐边界之后开始。
- K 与 V 的 head_dim 可以不同（`v_head_dim`，L830-834；GQA/OSS 模型需要），SWA（滑动窗口）层可用独立的 `swa_head_num/swa_head_dim` 覆盖（L828-834）。
- **设备侧指针表**（L931-948）：`k_data_ptrs/v_data_ptrs/data_ptrs`（uint64 张量，装每层缓冲的 `data_ptr()`）与 `data_strides`（每行字节数）。这让一个 Triton kernel 通过 `tl.load(data_ptrs + bid)` 直接解引用任意层的缓冲——`copy_all_layer_kv_cache_tiled` 因此能**一次 launch 拷贝所有层的 K+V**（见 L1094 的 move_kv_cache）。

### 读写路径

- `get_key_buffer(layer_id)`（L1033-1039）：先过 layer_transfer_counter 同步钩子（L1034-1036 注释特别警告：此 API 仅供 attention backend 调用、内嵌同步，别拿去做信息查询），再按 `layer_id - start_layer` 索引、必要时 view 还原 dtype。
- `set_kv_buffer(layer, loc, cache_k, cache_v, k_scale, v_scale, layer_id_override)`（L1055-1092）：语义次序是 ① 若输入 dtype ≠ 池 dtype 且带 scale，先 `div_(scale)` 反量化缩放再 `to(self.dtype)` 量化（L1069-1075）；② `store_dtype != dtype` 时 view 成字节（L1077-1079）；③ 交给 `_set_kv_buffer_impl` 四级分派。`layer_id_override`（L1063）供 HybridLinearKVPool 这类做层号重映射的外层使用。

### `move_kv_cache`（L1094-1146）——KV 搬家（retract/整理/CUDA Graph 换位）

1. **越界预检**（L1096-1098）：`maybe_detect_oob` 在搬之前抓 stale 索引——注释给出的动机是 *"Catch stale indices here instead of as an illegal-addr or silent KV corruption"*：脏槽位号要么炸成难查的 CUDA illegal address，要么更糟——静默写坏别的请求的 KV。
2. **原生路径**（L1100-1102）：`SGLANG_NATIVE_MOVE_KV_CACHE` 环境变量切换到 `move_kv_cache_native`（L2221，纯 PyTorch 逐层 gather-scatter，调试用）。
3. **Triton tiled 路径**（L1104-1146）：`_init_kv_copy_and_warmup`（L858-903）按行字节数选 tile 尺寸（≥8192B 行用 512B tile/8 warps，≥4096 用 256B，否则 128B——启发式在 L860-874），并**在启动时用 dummy loc 预热编译**；真正搬时按 `num_locs_upper`（128/256）分块 launch，块内 `next_power_of_2(N)` 让 Triton 特化不至于爆炸（L876-877 注释）。

---

## 7. MHA 变体池三连

### `NoOpMHATokenToKVPool`（L1149-1256）——embedding 模式的"空池"

`--is-embedding` + FA 后端 `fa_skip_kv_cache` 路径：prefill-only、无 decode、attention 直接用原始 K/V，根本不需要物理 KV。但调度器的容量视图（`self.size`）必须保留（准入控制照常工作），于是每层只分配 `(page_size, head_num, head_dim)` 的**KB 级占位张量**（L1167-1192 注释解释：让持有 buffer 引用的代码路径——指针表、层传输计数器、stride 算术——全部无 None-guard 存活）。防误用双保险：`set_kv_buffer` 直接 raise（L1232-1240，错误信息手把手教排查）、`get_kv_size_bytes` 报零（L1228-1230，显存账本不失真）。

### `MHATokenToKVPoolFP4`（L1259-1399）——FP4 量化 MHA

物理布局：数据 `(m, n, k//2)`（两个 FP4 打包进一个 uint8）+ scale `(m, (n*k)/16)`（scale_block_size=16，L1274）；读写分别走 `KVFP4QuantizeUtil.batched_dequantize/batched_quantize`（L1326/L1372），读时反量化成完整张量交后端。写路径同样有 capture-mode 双流 overlap（L1382-1393）。

### `HybridLinearKVPool`（L1402-1628）——full-attention 层 + mamba 层的统一门面

Qwen-Long/Jamba 类模型只有部分层是 full attention。本类不建大缓冲，而是**聚合**：内部一个 `full_kv_pool`（MHA 或 MLA 池，按 `use_mla` 分支选择类，L1436-1481，NPU/out-of-tree 后端也在此挂接）+ 外部传入的 `mamba_pool`。核心机制是**层号重映射**：`full_attention_layer_id_mapping`（L1482-1484）把全局层号映射到紧凑子池层号，`set_kv_buffer` 用 `layer_id_override` 传下去（L1568-1578）；MLA 路径更巧——`_transfer_id_context`（L1544-1557）用 contextmanager **临时篡改 `layer.layer_id`** 再恢复，让底层 MLA 池无感知。逐层同步钩子统一收到本层（L1517-1523 注释：内层池注册 None，等待逻辑在外层做一次）。

---

## 8. `MLATokenToKVPool`（L1631-1862）——DeepSeek MLA：单缓冲的极致省显存

MLA 的 KV 潜空间投影意味着**每 token 每层只需一个向量**（无独立 V）：

```python
self.kv_buffer = [torch.zeros((size + page_size, 1, kv_cache_dim), ...) for _ in range(layer_num)]
# kv_cache_dim = kv_lora_rank + qk_rope_head_dim  (默认, L1668-1672)
```

- `get_value_buffer`（L1731-1739）返回 `kv_buffer[..., :kv_lora_rank]` 切片——MLA 吸收式解码中 nope 部分被当作 V 用，物理上一个缓冲提供逻辑上的 K 与 V。
- **`set_mla_kv_buffer(layer, loc, cache_k_nope, cache_k_rope)`**（L1763-1812）三条路径：① HIP+DSA+FP8：`set_mla_kv_buffer_triton_fp8_quant` 融合"bf16→fp8 量化+分页写"（L1772-1781）；② DSA fp8 分段存储：`quantize_k_cache_separate` 分别量化 nope/rope 再走双张量 triton 写（L1782-1798，注释给出字节布局：nope 528B = fp8 512 + scales 16，rope 128B bf16）；③ 常规：dtype 对齐后 `set_mla_kv_buffer_triton`（L1799-1812）。
- `get_mla_kv_buffer`（L1814-1835）：triton gather 出 nope/rope 两段。
- CPU offload 的分块读写与 MHA 版同构（L1837-1862）。

### `MLATokenToKVPoolFP4`（L1865-1991）

FP4 版：数据 `(m, 1, kv_cache_dim//2)` + scale `(m, kv_cache_dim//16)`；`set_mla_kv_buffer` 要连发两个 triton 调用分别写数据与 scale（L1980-1991）。

---

## 9. `DSATokenToKVPool`（L1994-2218）——DeepSeek 稀疏注意力索引池

DSA 除了主 KV 缓冲外还需要每层的 **indexer K**（用于稀疏 top-k 选 token）。继承 MLA 池（`use_dsa=True`，`override_kv_cache_dim` 支持 fp8 存储时改写主缓冲维度，L2016-2033）。

### 独特的页内拼排布局（L2058-2077）

```python
index_k_with_scale_buffer: (num_pages, page_size * (index_head_dim + index_head_dim//128*4))
# page_size * head_dim 字节 fp8 数据 ‖ page_size * 4 字节 fp32 scale，拼在同一行
```

L2060-2065 的布局注释是理解此缓冲的钥匙：每页一行，前段是 64×128 的 fp8 索引 K，尾段 view 成 float32 是每 token 的 scale。CUDA 侧强制 `page_size == 64`（L2052），HIP 走 preshuffle（page_size 16 的倍数）或 legacy（page_size 1）双路径（L2042-2050）。

### 访问器与那个重要的 offload 教训

- 四个访问器（`get_index_k_with_scale_buffer` L2084 / `get_index_k_continuous` L2089 / `get_index_k_scale_continuous` L2102 / 融合版 `get_index_k_scale_buffer` L2115——docstring 明说融合一次调用比分开两次快）全部走 `index_buf_accessor` 的 triton 实现，且都带 layer_transfer_counter 同步钩子。
- **`get_cpu_copy`（L2158-2181）的注释值得整段背诵**：主 KV offload 了但 index 缓冲没 offload 的话，retract 释放的页会被别的请求 `set_index_k_scale_buffer` 复用，恢复时主 KV 是旧的、index/scale 是别人的——DSA attention 在那些位置读到垃圾。任何"辅助 per-page 缓冲"都必须与主缓冲同进退，这是池族演进的实战教训沉淀。
- `get_state_buf_infos`（L2202-2212）给 index 缓冲单独提供 RDMA 注册信息；`get_kv_size_bytes`（L2214-2218）把 index 缓冲计入总账。

---

## 10. 跨层拷贝双实现（L2221-2270）

- **`move_kv_cache_native`（L2221-2234）**：逐层 `k_cache[tgt] = k_cache[src]`，PyTorch 原生 gather-scatter，正确性基准与调试逃生口。
- **`copy_all_layer_kv_cache_tiled`（L2237-2270）**：2D grid（缓冲数 × 字节 tile 数）的 Triton kernel。三个细节：① 从指针表 `tl.load(data_ptrs + bid)` 拿基地址、`tl.cast` 成 uint8 指针——**一个 kernel 服务所有层**；② `tl.multiple_of(byte_off, 16)`（L2257）给编译器 16 字节对齐提示，配合 tile 尺寸启发式榨向量化；③ docstring 标注 "Safe for in-place copy"（L2247）——tgt 与 src 槽位号可能部分重叠（KV 整理场景），tile 内先 load 后 store 的程序序保证了正确性。

---

## 附录 A：池类家族速查表

| 类名 | 行号 | 物理布局（每层） | 适用场景 |
|---|---|---|---|
| `ReqToTokenPool` | L139 | `req_to_token: (size+1, max_context_len) int32` | 一切架构（请求级映射） |
| `MambaPool` | L207 | `conv: (L, size+1, conv_dim/tp, kernel-1)` + `temporal: (L, size+1, heads/tp, head_dim, d_state)` | Mamba/GDN 线性注意力层 |
| `HybridReqToTokenPool` | L500 | 继承 ReqToTokenPool + 聚合 MambaPool + 两张映射张量 | 混合架构（Qwen-Long 等） |
| `KVCache` (ABC) | L701 | —（定义合同） | 所有物理池的基类 |
| `MHATokenToKVPool` | L797 | `k_buffer/v_buffer: (size+page, heads, dim)` | 标准 MHA/GQA 模型 |
| `NoOpMHATokenToKVPool` | L1149 | `(page_size, heads, dim)` 占位（KB 级） | `--is-embedding` + fa_skip_kv_cache |
| `MHATokenToKVPoolFP4` | L1259 | `k/v: (m, n, k//2) uint8` + scale `(m, n*k/16)` | FP4 量化 KV |
| `HybridLinearKVPool` | L1402 | 聚合 full_kv_pool + mamba_pool，层号重映射 | 混合架构的统一门面 |
| `MLATokenToKVPool` | L1631 | `kv_buffer: (size+page, 1, kv_lora_rank+rope_dim)` | DeepSeek MLA |
| `MLATokenToKVPoolFP4` | L1865 | `kv: (m, 1, dim//2)` + scale `(m, dim/16)` | MLA + FP4 |
| `DSATokenToKVPool` | L1994 | MLA 布局 + `index_k_with_scale: (num_pages, 64×132)` | DeepSeek 稀疏注意力索引 |
| `move_kv_cache_native` | L2221 | —（函数） | KV 搬家的原生/调试路径 |
| `copy_all_layer_kv_cache_tiled` | L2237 | —（Triton kernel） | 单 launch 搬所有层 K+V |

选型逻辑在 `model_runner.py`：按模型架构（`use_mla`/mamba 层表/DSA 配置）+ `--kv-cache-dtype` + 平台（CUDA/NPU/out-of-tree）组合出具体类；NPU 的 `NPUMHATokenToKVPool`/`NPUMLATokenToKVPool` 在 `hardware_backend/npu/memory_pool_npu.py`，通过 L1440-1470 的分支挂接。

## 附录 B：allocator.py 分配器语义（槽位号的出生与死亡）

用户视角的 `alloc`/`free`/`available_size` 三动词，在 allocator.py 的两个实现里有精确分工：

### `TokenToKVPoolAllocator`（allocator.py L121）——token 粒度（page_size=1）

- `alloc(need_size)`（L148）：从 free 页池顺序切 `need_size` 个**离散 token 槽位号**，返回张量（radix cache 的节点 value 就是它）；不够返回 None。
- `free(free_index)`（L159）：归还槽位号数组；`free_group_begin/end`（L77-81）把多次 free 攒成事务，`merge_and_sort_free()`（L86）合并排序——radix cache 批量逐出时避免反复重建 free 列表。
- `available_size()`（L144）：剩余 token 数。Scheduler 的 `PrefillAdder` 用它做 prefill 预算；decode 每步每请求 +1，不足时触发 **retract**（把 running 请求退回 waiting，释放其 KV）。
- `clear()`（L135）：全量重建。

### `PagedTokenToKVPoolAllocator`（allocator.py L362）——页粒度（page_size>1）

- `alloc(need_size)`（L386）：按页分配，返回**页号×page_size** 形态的 token 下标（页内连续）。
- `alloc_extend(last_kvs, append_kvs, ...)`（L409）：**chunked prefill 专用**——沿已有分配追加扩展，配套 triton kernel `alloc_extend_kernel`（L241）处理"已有前缀 + 新增段"的页对齐。
- `alloc_decode(...)`（L459）：**decode 专用**——每请求恰好 +1 token（多数情况恰好落进某页空位或整新页），kernel `alloc_decode_kernel`（L327）。
- `free(free_index)`（L498）：按页归还（`free_index // page_size`）。
- 页粒度牺牲少量尾部碎片，换来 FlashInfer 等 paged kernel 的高效寻址与 radix cache 页级共享。

### 与 radix_cache 的协同（伪代码）

```python
# prefill 入队时（Scheduler）:
matched = radix_cache.match_prefix(req.input_ids)     # 树上找最长前缀
req.prefix_indices = matched.value                     # 复用旧槽位号（不写 KV）
new_indices = allocator.alloc_extend(matched.value,    # 新 suffix 分配槽位
                 len(req.input_ids) - len(matched.key))
req.out_cache_loc = new_indices
radix_cache.insert(matched.last_node, req.input_ids[len(matched.key):], new_indices)

# 完成时:
radix_cache.cache_finished_req(req)   # KV 留在树上（等 LRU 逐出）
# 或被 retract / abort:
radix_cache.cache_unfinished_req(req) # 前缀段插回树，未完成段槽位 allocator.free()

# 显存吃紧时（LRU）:
victim = radix_cache.evict(num_tokens)  # 从树尾摘节点
allocator.free(victim.value)            # 槽位号归还 → 下次 alloc 复用物理缓冲
```

关键认识：**物理字节从不零化**。free 只归还槽位号，旧 KV 数据留在缓冲区里，直到新写入覆盖——正确性由"只有持有槽位号的请求/树节点才会去读"这一不变式保证。flush_cache 则是整树清空 + allocator.clear + （部分路径）缓冲区重置。

## 与其他模块的交互

- **`allocator.py`（最重要的搭档）**：`TokenToKVPoolAllocator`（L121）管理无分页 token 槽位，`PagedTokenToKVPoolAllocator`（L362）按页管理（详见附录 B）。分配器持有 `get_kvcache()`（L68）引用本文件的物理池——**分配器发号、物理池存字节**，二者经槽位号这个纯整数解耦；`free_group_begin/end`（L77-81）提供事务化批量释放（radix cache 逐出用）。
- **`radix_cache.py` / `swa_radix_cache.py` 等**：前缀树节点 value 存的就是 allocator 发的 token 槽位号；`match_prefix` 命中即免算免写 KV，miss 部分调 `alloc_extend`；`cache_finished_req`/`cache_unfinished_req`（retract 路径）与 evict 最终都落到 `token_to_kv_pool_allocator.free(...)`（radix_cache.py L452/L473/L514 等十余处）。
- **`schedule_batch.Req`**：`req_pool_idx`（ReqToTokenPool 发的号）、`out_cache_loc`（allocator 发的号）、`fill_kv_loc` 把号写入 `req_to_token` 表；`PrefillAdder` 预算同时查 allocator 的 `available_size` 与 req pool 的 `available_size`。
- **attention backends（flashinfer/triton/fa/flashmla...）**：消费侧。`forward_extend/forward_decode` 每层调 `get_key_buffer/get_value_buffer`（内嵌逐层同步钩子）拿paged 表，qkv 投影后调 `set_kv_buffer/set_mla_kv_buffer` 写入。
- **`model_executor/model_runner.py`**：工厂。按 server_args（page_size、kv_cache_dtype、attention 模型架构）选池类型、按显存 profiling 定 `size`，随后把池注入 allocator、radix cache 与 attention backend。
- **disagg（`disagg` 目录 / mooncake）**：`get_contiguous_buf_infos` 三元组用于 RDMA 内存注册；`LayerDoneCounter`（cache_controller.py）配合 `wait_until` 实现逐层传输-计算重叠。
- **`cuda_graph_runner.py`**：padded batch 靠 slot 0 padding 吸收假读写；`get_is_capture_mode` 控制 alt_stream 双流行为。
- **`TorchMemorySaverAdapter` + io_struct 的 `ReleaseMemoryOccupationReq`**：所有池分配都包在 `region(GPU_MEMORY_TYPE_KV_CACHE)` 里，RL 训练间隙可按 tag 归还 KV 显存再恢复（virtual memory 级，不重分配）。

## 关键设计决策

1. **四层解耦：请求映射 / 槽位号 / 物理字节 / 前缀语义彻底分离**。`req_to_token` 表只做"请求视角"索引，allocator 只发号，KVCache 只存字节，radix cache 只管复用语义。每一层可用纯整数接口独立测试，换分页策略不动物理布局，换 MLA 不动调度器。模块 docstring 说"两层"，历史演进实际长成了四层——allocator 迁去独立文件正是这个解耦过程的化石。
2. **slot 0（及 page_size）padding 是 CUDA Graph 的全局契约**。请求池 +1 行、KV 池 +page_size 行、mamba 池 +1 行，padded batch 的哑请求槽位号默认 0，假读写全部落进无人使用的 padding 区。没有这个约定，静态 shape 的图回放会在补齐位写出越界地址。
3. **字节视角的一致性：`store_dtype=uint8` + `view()` 边界还原**。FP8 的 index_put 缺失、FP4 的非标准位宽，全部被"物理上按 uint8 存、逻辑边界 view 回来"统一消化，量化池（FP4/FP8）只需覆写 `_create_buffers` 与量化点。
4. **设备侧指针表让"每层一张张量"的布局零成本**。List[Tensor] 保住了单层操作的简洁与 RDMA 逐层注册能力，`data_ptrs`(uint64)+`data_strides` 设备张量又让单 kernel 跨所有层工作（move_kv_cache 一次 launch 搬完 K+V×layers）——布局可读性与 kernel 效率兼得。
5. **同步钩子内嵌在读取路径（`get_*_buffer` 即 `wait_until`）**。逐层 KV 传输的等待不放在调度器代码里，而是藏在 attention backend 本来就要调的 get 接口里——功能叠加零侵入，L1034-1036 的注释同时立了"仅限 attention 调用"的使用规矩防误用。
6. **降级链与防御性检查成对出现**：写入四级降级（JIT→AMX→双流→朴素）、搬家的 OOB 预检（把 stale 索引从"illegal addr 或静默腐坏"变成确定性报错）、DSA 把辅助缓冲 offload 的教训直接写进注释——每个历史事故都变成了代码里的护栏。

## 附录 C：常见误读 FAQ

**Q1：`ReqToTokenPool.alloc` 和 `TokenToKVPoolAllocator.alloc` 是同一个东西吗？**
不是。前者发的是**请求槽位号**（`req_to_token` 大表的行号，决定"这个请求占哪一行"），后者发的是 **token 槽位号**（KV 缓冲区的行号，决定"每个 token 的 KV 写到哪"）。一个请求拿到 1 个 req_pool_idx 和 N 个 KV 槽位号；`--max-running-requests` 约束前者，`--max-total-tokens` 约束后者。

**Q2：为什么 `free` 之后不把缓冲区清零？**
性能。清零一个 GB 级缓冲区是毫秒级开销，而正确性不需要它——读取方必须持有槽位号，槽位号一旦归还就不可能被旧主人读到。唯一例外是 `MambaPool.clear_slots`：SSM 状态是"读改写"语义（新请求会在旧状态上继续滚动），不清零会直接污染，所以它必须显式归零。

**Q3：`size + page_size` 多出来的 padding 和 slot 0 是浪费吗？**
是有意为之的安全垫。请求池的第 0 行、KV 池的前 page_size 行专门吸收 CUDA Graph padded batch 的哑读哑写（补齐请求的槽位号默认 0），换取静态 shape 图回放的安全性。page_size=64 时多 64 行 × 每行几 KB，相对数十万行的池可忽略。

**Q4：`get_key_buffer` 为什么不建议在 attention backend 之外调用？**
它内嵌了 `layer_transfer_counter.wait_until` 同步（L1034-1036 注释）——PD 分离逐层传输没完成时会阻塞。拿它做信息查询/统计会意外挂住调用线程。

**Q5：MLA 池没有 v_buffer，`get_value_buffer` 返回什么？**
返回 `kv_buffer[..., :kv_lora_rank]` 切片（L1731-1739）。MLA 权重吸收把 nope 部分同时用作 K 与 V 的来源，物理上一个缓冲、逻辑上两个视图——这正是 MLA 省显存的机制本身。

## 阅读建议

1. **三件套连读**：`memory_pool.py`（物理层）→ `allocator.py`（槽位层）→ `radix_cache.py`（复用层）。只读本文件会困惑"谁在调 alloc"；只读 radix 会看不到字节落点；三者串起来才是完整的 KV 生命周期。
2. **拿 `MHATokenToKVPool` 当骨架精读（L797-1147）**：布局（`_create_buffers`）、读（`get_*_buffer`）、写（`set_kv_buffer`→`_set_kv_buffer_impl`）、搬（`move_kv_cache`）四条路径走通后，其余池全是这条骨架的变奏（MLA 换单缓冲、FP4 换打包、DSA 加辅助缓冲）。
3. **追一个 decode step 的槽位号旅程**：`Scheduler.get_next_batch_to_run` → `PagedTokenToKVPoolAllocator.alloc_decode` → `Req.out_cache_loc` → `req_to_token.write` → triton backend 的 `forward_decode` 用 `req_pool_indices` 查表 → kernel 寻址 `k_buffer`。走完这条链，本文件每个类都摸过一遍。
4. **注释即事故史**：L1095（OOB 预检动机）、L2158-2163（DSA offload 教训）、L176-180（放松的断言与 PR 链接）、L216（fields vs vars 的 compile 兼容）——这些注释比代码本身更难得，读到时停一停。
5. **平台分支先跳后回**：NPU/AMX/HIP 分支（L282-295、L2042-2052、L1772-1781）首读可略，主线通了再回来对照 `hardware_backend/` 与 out-of-tree 平台的池实现。
6. **动手实验**：`test/srt/mem_cache/` 下有 allocator 与 radix cache 的单测；用小模型（如 Llama-8B，`--page-size 1` vs `64`）启动时观察本文件 `_finalize_allocation_log` 打印的 "#tokens" 与 mem_usage，再对照 `--kv-cache-dtype fp8_e5m2` 复跑一次，能直观感受 store_dtype 机制对容量的影响。
