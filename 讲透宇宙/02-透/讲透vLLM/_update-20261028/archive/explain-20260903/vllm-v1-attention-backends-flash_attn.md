# vLLM v1 深度解析：FlashAttention 后端（flash_attn.py）

> 文件：`vllm/v1/attention/backends/flash_attn.py`（约 1830 行）
> 知识图谱 layer：`attention`（55+ 后端中的默认主力）；被 flash_attn_diffkv、whisper_causal、qwen4_exp/inkling QSA 复用

## 角色定位

这是 vLLM v1 对 FlashAttention（FA2/FA3/FA4 统一封装）的**完整后端实现**，遵循 v1 attention 的三件套协议：`AttentionBackend`（能力协商类方法）→ `MetadataBuilder`（每步构建元数据）→ `Impl`（每个 attention 层一个实例，执行 forward）。它在请求生命周期中处于 forward 最内层：ModelRunner 的 `_build_attention_metadata` 调 builder.build()，模型每层 attention 的 `forward()` 落到 `FlashAttentionImpl.forward()`。

## 内部结构

**`FlashAttentionBackend`**（classmethod 协商）：声明支持的 dtype（fp16/bf16）、KV cache dtype（含 fp8）、`get_supported_kernel_block_sizes`（FA4 hd256 内核要求 256 页；否则 MultipleOf(16)）、sliding window / non-causal / batch invariance / per-head quant / mm_prefix（PrefixLM 双向，需 FA4）/ sink 等能力。`supports_combination()` 是选择器仲裁点——比如"FP8 KV 需要 SM90 FA3 或 SM100 FA4"、"mm_prefix 需要 FA4"。

**`FlashAttentionMetadata`**（dataclass）：注释里的 context_len/query_len/seq_len 关系图是理解 varlen 的钥匙。核心字段：`query_start_loc`（cumsum 前缀，[num_reqs+1]）、`seq_lens`、`block_table`、`slot_mapping`、cascade 专用（`common_prefix_len / cu_prefix_query_lens / prefix_kv_lens / suffix_kv_lens`）、DCP 专用（`dcp_context_kv_lens`）、FA3 AOT `scheduler_metadata`、R-SWA 三件套、mm_prefix 双向区间张量。

**`FlashAttentionMetadataBuilder`**：`build()` 三分支——DCP>1（上下文并行拆分本地 KV 长度）、cascade（公共前缀 ≥1 块时构 prefix/suffix 两段元数据）、普通路径（单次 varlen）。CUDA graph 兼容的 persistent 设备缓冲都在 `__init__` 预分配：FA3 scheduler_metadata 上界 buffer（写入后**尾部清零**——注释警告残留脏值会让 thread block 覆写输出）、R-SWA window tensor（避免 forward 内 CPU→CUDA 拷贝破坏捕获）、mm_prefix 区间 staging。`_cudagraph_support`：FA3 为 ALWAYS，FA2 因 max_query_len=1 packed-GQA 特殊处理只能 UNIFORM_BATCH。

**`FlashAttentionImpl`**：构造时解析 FA 版本（head_size/sink/alibi/softcap 组合决策）、滑窗转 `(left, right)` 元组（causal 为 `(w-1, 0)`）、DCP combine 算子选择。

## 数据流：forward 的三条路径

**主路径（非 cascade）**：`kv_cache.transpose(1, 2).split(head_size)` 把 `[blocks, heads, block, 2D]` 劈成 K/V 视图 → `canonicalize_singleton_dim_strides` 修退化 stride（TP 下 num_kv_heads=1 时 TMA 要求 ≥16 字节对齐）→ fp8 KV view 降位 → 组装 `flash_attn_varlen_func`：`cu_seqlens_q=query_start_loc`、`seqused_k=seq_lens`、`block_table` 分页读 KV、`window_size`、fp8 descale（`.expand` 到 `(num_seq, num_kv_heads)`）、FA4 的 `dynamic_causal`（per-seq causal 张量）/`mask_mod`（R-SWA 或 mm_prefix 的 CuTE-DSL 闭包）。**注意 forward 开头的警告注释：piecewise CUDA graph 下此函数 eager 执行，`view`/切片都有可观 CPU 开销，任何改动必须基准测试。**

**cascade 路径**（公共前缀长时）：`cascade_attention()` 两段式——prefix 段把**全部请求视为一个序列**跑一次 `flash_attn_varlen_func`（`cu_prefix_query_lens=[0, num_tokens]`，只读 `block_table[:1]` 即公共块的物理位置），suffix 段每请求正常 causal 计算但 `seqused_k -= prefix_len` 且 block_table 偏移 `num_common_kv_blocks`，最后 `merge_attn_states` 用 LSE 数学（log-sum-exp）合并两段。启用与否由 `use_cascade_attention()` 启发式决定：前缀 <256 token 或请求 <8 直接否；否则若 FlashDecoding 更优（粗粒度 CTA/wave 性能模型对比）则否。

**KV 写入 `do_kv_cache_update()`**：`reshape_and_cache_flash` 按 `slot_mapping` scatter 写 K/V 入缓存——slot_mapping 的形状决定实际 token 数，所以无需对 padded K/V 切 `[:num_actual_tokens]`。**读用 block_table、写用 slot_mapping** 是 v1 的一对核心概念：block_table 是"序列→块"的粗粒度映射（attention 读），slot_mapping 是"token→物理槽"的细粒度映射（KV cache 写）。

另有 `_forward_encoder_attention`（encoder-only 双向、无 KV cache）与 `_forward_with_dcp`（all-gather 跨 DCP rank 的 query，context 段非 causal + 本地段 causal，两段 LSE 合并）。

## 关键设计决策

1. **varlen 打包代替 padding**：所有请求 token 稠密拼接成 `[num_tokens, heads, head]`，用 cu_seqlens_q 划界——batch 维不出现在张量里，避免形状随请求数变化破坏 CUDA graph。
2. **AOT scheduler_metadata（FA3）**：提前在 host 侧算好 kernel 的 split 调度计划，forward 内零 host 计算；捕获图时设 `max_num_splits` 上界以预分配中间 buffer（代价是内存换确定性）。
3. **mask_mod 扩展机制**：FA4 的 CuTE-DSL `mask_mod` 闭包 + `aux_tensors` 实现精确 token 级掩码——R-SWA（"causal AND (全局前缀 OR 滑窗)"）与 mm_prefix（"(causal ∧ window) ∨ 双向区间"）都编译进 kernel，`use_fast_sampling=True` 让 FA4 跳过全掩码 KV 块。工厂函数 `functools.cache` 缓存闭包对象，避免 FA4 `hash_callable` 因闭包地址变化反复 JIT。
4. **级联注意力**：N 个请求共享 K 前缀时，前缀 K/V 只读一遍（省 N-1 次显存带宽），suffix 并行不受影响。

## 新人提示

- 切入点：先读 `FlashAttentionMetadata` 字段注释（context/query/seq_len 图），再读 `FlashAttentionImpl.forward` 主路径，最后按兴趣跳 cascade / DCP。
- 易混淆点①：`forward_includes_kv_cache_update = False`——FA 后端的 forward 只做读，KV 写由框架在编译图的单独节点（或 eager 的 `do_kv_cache_update`）完成；某些后端（如 MLA）会合并。
- 易混淆点②：`build()` 里 `use_cascade = common_prefix_len > 0` 只是必要条件，真正决策在 ModelRunner 调用的 `use_cascade_attention()` 启发式；两处不要混。
- 易混淆点③：`_store_scheduler_metadata` 只在 `use_full_cuda_graph` 时写入持久 buffer 并清零尾部——piecewise 模式下直接返回新 tensor。
- 性能直觉：decode 小 batch 时瓶颈在 host 侧元数据构建而非 kernel；这正是 builder 里各种"零 CPU 同步"注释（如 `seq_lens - common_prefix_len` 直接用 GPU 张量）的由来。
