# operators/kvcache/ + amx/la/amx_kernels.hpp：CPU 侧的 attention 与 GEMM 双核心

> 知识图谱 commit 31985f4。先钉事实：CPU 算力分两条腿——MoE GEMM 走 `operators/amx/`（自研，`la/amx_kernels.hpp` 3917 行最重），attention/KV cache 走 `operators/kvcache/`，后者 SIMD 执行体复用 `third_party/llamafile` 的 tinyBLAS。

## 1. 角色定位

两文件同属图谱第 5 层「kt-kernel C++/CUDA 内核层」（kt-kernel 两层共 207 节点）。`kvcache.h`（637 行）声明 `KVCacheConfig`（L111）与 `KVCache` 类（L178），是 QUEST 稀疏检索在 CPU 侧的工程落地；`amx_kernels.hpp` 是全部量化 MoE 算子的计算核心。archive/csrc/ktransformers_ext/ 存同源冻结副本。

## 2. 内部结构

`kvcache.h` 四组：①`AnchorType`（QUEST 等 5 种，L52）与 `RetrievalType`（LAYER/KVHEAD，L83）；②`k_cache_q4/q8/fp16_` 三套 4D vector `[layer, head, block, ...]`（L363-381），K 行主序、V 列主序，两次 GEMM 都行主序访存；③锚点 `anchor_`（L386）与最小堆 `top_similar_block_`（L419）；④按线程预分配缓冲（L459-467），函数内零 malloc。

`kvcache_attn.cpp` 四层：`attn_with_kvcache`（L499，`assert(q_len==1)`）→ `attn`（L469）按 `RetrievalType` 二分；检索 `quantize_q_`（L532，query 量化 q8_0）→ `calculate_block_similarity_layer_`（L608）→ `select_block_layer_`（L737 堆排选块）；并行 `attention_layer_/kvhead_`（L244/L18）用 `do_work_stealing_job` 铺 `(batch, head, block)` 任务；微内核 `attn_with_kvcache_one_block_`（L1542）：`llamafile_sgemm` 算 QK^T（fp16 L1657/int4 L1787）→ `ggml_vec_scale_f32` 乘 1/√d（L1666）→ 掩码 → softmax 留 lse（L1682）→ 第二个 sgemm 算 PV（L1712）。跨块在线 log-sum-exp 合并：同线程连续块免锁（L136-149），换头才加锁（L151-178）。

AMX 侧（namespace amx）：`TileConfig` 配 7 tile（L105-113），int8 用 `_tile_dpbssd`（L64）、int4 用 `_tile_dpbusd`（L78）；`GemmKernel133`（L91）/`GemmKernel224BF`（L567）等按 tile × 量化格式成族。

## 3. 外部连接

图谱：`kvcache.h` 被 `ext_bindings.cpp` 与同目录 4 个实现 cpp 导入，自身依赖 `cpu_backend/worker_pool.h`（`do_work_stealing_job`，worker_pool.h L153）。运行时依赖：llama.cpp ggml 头（量化数据结构）、`llamafile/sgemm.h` → `third_party/llamafile/tinyblas_cpu.h`（`tinyBLAS` L426 / `_Q0_ARM` L667 / `_Q0_AVX2` L828，19 处 `__AVX512*` 分支即 AVX 编译期特化层）、`ggml_vec_scale_f32`（kvcache_utils.cpp L786 向量化）。Python 侧仅暴露 `get/update_cache_total_len`（ext_bindings.cpp L1146-1150）。

## 4. 数据流

decode：fp16 q → K/V 入块 → query 量化 q8_0 → 锚点相似度（批量 L655/逐块 L669）→ top-k 选块 → work-stealing 逐块微内核，tinyBLAS AVX 模板（int8 走 VNNI）两次 GEMM → lse 流式合并 → fp16 写回（L223）；`layer_step/token_step` 不命中则复用历史块表（L805-831）摊销检索。

## 5. 设计决策

- **不全走 AMX**：attention GEMM 窄长填不满 AMX tile，走 AVX tinyBLAS；MoE GEMM 方整才是 AMX 主场。
- **复用而非重造**：量化结构与微内核借 ggml/llamafile，自研价值在检索调度、work-stealing、在线 lse 归约这层「编排」。
- **块状 cache**：一石三鸟——QUEST 检索单元、量化单元、并行任务粒度；K/V 转置错开让两个方向都行主序。
- 技术债：`_layer/_kvhead_` 两套近乎逐行复制（L18-242 vs L244-467）。

## 6. 新人提示

- 切入：先读 `kvcache.h` L504-621 微内核参数文档；AMX 从 `GemmKernel133`（L91）入手。
- 硬约束：`head_dim % 32 == 0`（L1605）、`k_quant_type==0/v_quant_type==1`（L1606-1607）。
- 编译：AMX 需 Sapphire Rapids+；setup.py L300-305 六档 .so，`CPUINFER_BUILD_ALL_VARIANTS=1` 建全变体，`_cpu_detect.py` 运行时择优。
- 测试：AMX 有 `operators/amx/test/`；kvcache 无专测，走 `kt-kernel/test/per_commit`，改检索逻辑用 `get_attn_sparsity`（L1514）自检。
