# flash_mla/flash_mla_interface.py 精讲

> 原文件：`flash_mla/flash_mla_interface.py`（435 行）

## ① 角色定位

FlashMLA 对外的**唯一 Python 门面**：`get_mla_metadata` / `flash_mla_with_kvcache`（分页 KV 解码）、`flash_mla_sparse_fwd`（稀疏 prefill）、`flash_attn_varlen_func` 系列（varlen prefill + autograd）都从这里进入。它把 PyTorch 张量翻译成 `flash_mla_cuda` C++ 扩展的调用约定，本身不含 CUDA 逻辑。

## ② 内部结构

- **`FlashMLASchedMeta`**（8-34 行）：嵌套 `Config` dataclass + 两个可复用张量槽位；`have_initialized` 实现惰性初始化。
- **`get_mla_metadata`**（37-50 行）：只返回 `(FlashMLASchedMeta(), None)` 空壳，真正元数据推迟到首次 `flash_mla_with_kvcache` 生成。
- **`flash_mla_with_kvcache`**（53-173 行）：首次调用做 sanity check 并把形状/模式写入 `sched_meta.config`；后续逐项断言一致（b/s_q/h_q/page_block_size/h_k/causal/is_fp8_kvcache/topk/extra 系列），防复用错配。按 `indices` 是否为 None 二分：稀疏走 `sparse_decode_fwd`（要求 fp8 KV 且非 causal），稠密走 `dense_decode_fwd`。
- **`flash_mla_sparse_fwd`**（176-211 行）：一次性稀疏 prefill，返回 `(output, max_logits, lse)`。
- **`FlashAttnVarlenFunc`**（328 行起）：autograd.Function；SM100 bwd 暂不支持 GQA（283 行 raise）。

## ③ 外部连接

依赖仅 `torch` 与编译产物 `flash_mla.cuda`。被 `flash_mla/__init__.py` re-export；推理框架由此接入 V3 系列解码。workspace 分配也在本层：prefill fwd 固定 32 MB（241 行），bwd 按 `4*bs*s_aligned*h*d` 精确估算（297-304 行）。

## ④ 数据流

解码主路径：`q (b, s_q, h_q, 576)` + `k_cache (num_blocks, page_block_size, h_k=1, head_dim)` + dense 的 `block_table/cache_seqlens` 或 sparse 的 `indices (b, s_q, topk)` → 接口层确定 topk、extra 系列、`softmax_scale`（缺省 `d_qk**-0.5`）→ C++ 返回 `out (b, s_q, h_q, 512)`、`lse (b, h_q, s_q)`，并回填元数据供复用。docstring（92-98 行）给出 FP8 每 token 656 字节布局：512 B 量化 NoPE（fp8_e4m3）+ 16 B scale（4×fp32）+ 128 B RoPE（64×bf16 不量化）。

## ⑤ 设计决策

- **惰性元数据**：调度元数据依赖 `cache_seqlens/topk_length` 的运行时值，无法在 `get_mla_metadata` 时刻确定，索性推迟到首调；复用则省掉每个 decode step 的 scheduler kernel。代价是断言只覆盖形状，`cache_seqlens` 值不变靠文档约定。
- **MLA 潜在 KV 模式**：`h_k=1`（MQA 化潜在 KV）、`head_dim 576 / head_dim_v 512` 不对齐，对应 V3 的 NoPE+RoPE 分离存储；fp8 只压 NoPE 段、RoPE 保 bf16。
- **attn_sink 公式**（88 行）：输出乘 `exp(lse)/(exp(lse)+exp(attn_sink))`，+inf 归零——sink 折进 combine 内核而非单独 kernel。
- **兼容化石显式化**：`num_splits` 必须传 None、返回二元组，注释直言是历史遗留。

## ⑥ 新人提示

1. 先读 docstring 再读代码——KV 布局、索引语义是协议级文档。
2. `topk_length` 按左截断省算力，但 199 行警告了 NaN 边界情形。
3. 断言链挡住 C++ 层来不及查的一致性错误；`lse` 在 C++ 侧已 transpose 成 `(b, h_q, s_q)`。
