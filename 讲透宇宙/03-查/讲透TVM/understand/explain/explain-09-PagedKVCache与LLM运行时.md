# explain-09 · fork LLM 定制线：src/runtime/vm/paged_kv_cache.cc 与 attn_backend（FlashInfer 桥）

## 角色定位

`paged_kv_cache.cc`（3336 行，runtime/vm 目录最大文件）是本 fork **LLM 定制线的旗舰**：文件头 L21 自我定位 "Runtime paged KV cache object for language models"。它实现了 vLLM 式 **PagedAttention** 的运行时对象——按页（page_size 粒度）管理多条序列的 K/V 显存，支持 prefill/decode 分治、sliding window、token tree（speculative decoding）、MLA（DeepSeek 系 latent attention）、KV 跨设备传输（NVSHMEM/disco）与 checkpoint 存取。类注释 L111-130 规定了三方协议：`BeginForward(seq_ids, append_lengths)` → `Attention(q,k,v)`（注意力对历史+新输入计算，新 KV 同时入缓存）→ `EndForward()`；EndForward 之后必须重新 BeginForward 才能再 Attention。类本体 `PagedAttentionKVCacheObj : public AttentionKVCacheObj`（L131）刻意放匿名可达的 private 区（L103-109 注释："keep the implementation private as they may subject to future changes. Users can interact with it through the runtime API function calls"）——唯一入口是 L3226 注册的 `vm.builtin.paged_attention_kv_cache_create`，由编译出的 VM 字节码在初始化时调用。

同目录 `attn_backend.cc`（136 行）是**注意力后端桥**：把 Python 侧传入的 `[backend_name, run_func, plan_func]` 数组转换成类型化的 C++ 函数对象，"tirx"（TVM 自产 kernel）与 "flashinfer"（外部库）两种后端在此归一。

## 内部结构

**配置与存储布局**（L133-197）：`page_size_/num_layers_/num_qo_heads_/num_kv_heads_/qk_head_dim_/v_head_dim_` 等十几个 const 配置；`attn_kinds_` 逐层记录注意力类型（L57-70 的 `AttnKindToString` 列出四类：mha/mla/linear/mha_sliding——**线性注意力（Mamba 类）与 MLA 同为一等公民**）；`pages_` 的布局注释 L189-191：`(num_pages, 2, num_heads, page_size, qk_head_dim)`，"2" 维 0=K 1=V；L187 注明启用 KV 传输时整块由 NVSHMEM 分配（`nvshmem_pages_` L197）。RoPE 三模式（none/normal/inline，L72-83），构造器 L411 附近有条规则：sliding window + 非 None RoPE 时强制 inline。

**三层簿记**（L198-249）：页级（`free_page_ids_` 空闲页栈 + `seq_map_` 序号→序列）、块级（`global_block_pool_` 全局 token-block 池 + `free_block_idx_`）、批级（`cur_batch_size_/cur_seq_ids_/cur_append_lengths_` 与 `is_chain_on_depths_/num_depths_`——**token tree 的深度分层调度**，每个 depth 独立决定用 decode 还是 prefill kernel，L238-239 `use_decode_kernel_`）。

**双流与脏标记**（L221-225、3030-3048）：辅助数组（page_indptr/page_indices/last_page_len 等 20+ 个 L268-322 的 host 缓冲）修改后置 `dirty_aux_data_device_`，`ComputeStreamWaitForCopyStream()` 才批量同步到 GPU 并调 `KernelBeginForward()`；L3037-3042 注释解释 FlashInfer 的 plan kernel 已不收显式 stream 参数、跑在当前流上——所以要在 copy 流上临时 SetStream 再切回 compute 流，**保持旧行为的兼容补丁写法**。

**FlashInfer 计划阶段**（L2740-2850）：`NeedKernelBeginForward()`（L2740-2754）扫描 8 个注意力函数槽位（prefill/ragged/decode/sliding 两套/tree-mask 两套/mla prefill），任一挂 FlashInfer 即需 plan；`MHAKernelBeginForward`（L2773 起）按层段 attn_kinds 分派 MHA/MLA 两路，再按 depth 循环给 decode（L2793）/prefill（L2802）分别喂 workspace；MLA 路（L2823 起）单独检查 sliding window 不支持。L1167 注释揭示一个关键优化点：GQA group ≥4 且 FlashInfer 启用时的 decode 路径选择。

**注意力分派**（L1619-1776）：三个入口 `SelfAttention`（L1619）/`CrossAttention`（L1662）/`LinearAttention`（L1776）——线性注意力不经过页缓存而走状态（见 kv_state.h 的 KV state 线）。树形 token 提交由 `CommitAcceptedTokenTreeNodes`（L1781）处理，被拒节点经 `PopN`（L867，L1861 注释：PopN 只改页表结构）回滚。

**构造 FFI**（L3224-3331）：`paged_attention_kv_cache_create` 接 28-29 个参数，逐个 cast；L3235-3243 的 **disco 分组感知**——在 Disco worker 线程里按 `layer_indptr` 把层切给多个 KV cache 组（多 GPU 层并行的运行时基础）；L3298-3311 页数推导：`(total_token_capacity + page_size - 1)/page_size + 1`，sliding window 时每序列再预留 2 页（L3308-3311）。

## 外部连接

- **attn_backend.cc 转换器**：`ConvertPagedPrefillFunc`（attn_backend.cc L27-46）等五个函数按 args[0]=="tirx"/"flashinfer" 造对应 Fun 对象；MLA ragged 额外接受 `qk_head_dim/v_head_dim` override（L63-66 注释：ragged kernel 的 head dim 与压缩 MLA cache 不同）。AttnBackendKind 枚举在 attn_backend.h L47。
- **VM 集成**：VM 字节码经 `vm.builtin.*` 调用（explain-11 的 vm.cc 指令表里能找到这些 builtin）；relax 图里的 `kv_cache` 全局对象由 `kv_state.cc`（146 行，AttentionKVCache 基类）+ `lm_support.cc`（667 行）撑起。
- **周边状态线**：`rnn_state.cc`（505 行，RNN/线性注意力状态）、`tensor_cache_support.cc`（372 行）——fork 把"LLM 运行时状态"整体做成了 runtime 对象家族。
- **kernel 供给**：tirx 后端的 attention kernel 由 TVM 自己编译（可被 dlight/meta_schedule 调优——与 explain-06/07 闭环）；flashinfer 后端经 Python glue 注入外部库函数。

## 数据流

一轮 decode：VM 执行到 attention 算子 → `BeginForward([seq_ids],[1,1,...])` 构建批簿记、按 depth 分层、host 辅助数组刷新、置脏 → `Attention(layer_id, q,k,v)`：先 `ComputeStreamWaitForCopyStream()`（同步辅助数组 + FlashInfer plan）→ transpose_append 把 k/v 写入页（跨页时 f_copy_single_page_ 搬运）→ 调 decode kernel（tirx 或 flashinfer）对全部历史页做注意力 → 输出 o → `EndForward()`。Prefill 同理但走 ragged/paged prefill kernel + chunked（prefill_chunk_size_ 限制单轮最大长度）。

## 设计决策

1. **私有实现 + builtin 唯一入口**（L103-109）：3336 行的复杂状态机只暴露 28 参工厂函数，重构自由度全保留——接口稳定性靠窄门而不是宽 API。
2. **后端函数对象化**（attn_backend.cc）：tirx/flashinfer 差异被封装进统一 Fun 类型（run+plan 两段），KV cache 主逻辑对后端零感知——新增后端（如 cudnn attention）只加一个 Convert 分支。
3. **plan 与 run 分离**：FlashInfer 的 plan（workspace 规划）在 copy 流完成，run 在 compute 流——L3037-3042 那段注释就是双流正确性的活档案。
4. **页表/块池/批簿记三层分离**：页表管显存物理布局、块池管逻辑 token、批簿记管当轮请求——PopN 只动页表（L1861）这类精确注释标明了各层职责边界。
5. **disco 层切分**（L3235-3243）：KV cache 天生按层分片，与 disco 多 worker 对齐——分布式推理不是附加层而是构造参数。

## 新人提示

- 读这个文件先记三方协议（L118-130），再按 L133-330 的成员分组注释逛一遍"字段地图"，方法实现都在其后——直接从 1096 行 BeginForward 顺读容易迷路。
- 调试 OOM：页数公式在 L3307-3311；sliding window 模式每序列多 2 页预留常被忽略。
- "Kernel BeginForward doesn't support sliding window"（L2791/2825）是硬限制：sliding window + FlashInfer plan 路径组合不可用，选后端时先对照。
- 想看 MLA 与 MHA 的差异落点：`f_mla_prefill_` 槽位（L2737/L2837）与 attn_backend.cc L63-66 的 head_dim override——这是 DeepSeek 系模型的关键通道。
