# msa/sparse_atten_fwd.py：3564 行的稀疏注意力巨构与移植方法论范本

> 文件：`tirx_kernels/msa/sparse_atten_fwd.py`（3564 行，全仓最复杂 kernel 之一）
> 知识图谱定位：「注意力家族移植层（FlashMLA/FlashAttention/MSA）」，上游 = MiniMax MSA @ 80434d7f（`fmha_sm100/.../atten_fwd.py`）。

## 角色定位

MSA（MiniMax）移植家族的核心 forward：**K2 方向的 topK 稀疏注意力**，BF16/FP8 K/V 双 dtype 模式，split-partial 输出形态。家族三件套 `sparse_prepare_flat_schedule` → **`sparse_atten_fwd`** → `sparse_atten_fwd_combine` 构成完整流水线：prepare 两个 kernel 产出 work list 与预留的 split slot，本 kernel 消费之，combine 归约之。它与 cuDNN BSA 同为"稀疏注意力"但方向相反——BSA 是每个 q_block 持有一个 KV block 列表，MSA 是**每个被选中的 KV block 持有一段会 attend 它的 query rows**（k2q CSR：`k2q_q_indices`/`k2q_qsplit_indices`/`k2q_row_ptr`）。

## kernel 算法

工作划分：**一个 CTA = 一个 work item = 一个 KV block × 一段 query rows**。CTA 从 `scheduler_metadata` 读 6 列（head_kv、row_linear、work_q_begin/count、batch、kv_block_idx），grid 直接取 `work_capacity`（work list 的容量而非实际条数），尾部 CTA 读到 `block >= work_count` 就整体早退——这是无 CLC 家族处理动态工作量的标准手法。CTA 把 KV block 加载一次，query rows 按组（`q_tokens_per_group = 128/qhead_per_kv`）走过 online softmax 全流程：UTCMMA 算 QK 得 S → softmax warpgroup 在寄存器里做 row_max/exp2/row_sum → P 打包回 TMEM → UTCMMA 算 PV 累加 O。每组结果写进 **prepare 阶段预分配的 split slot**（`q_idx | (split_slot&0xFF)<<24` 打包索引，softmax 侧 `_resolve_gather4_rows` 的姊妹解码）——同一 query 的多个 partial 天然不碰撞，**全 kernel 零 atomics**；最终由外部 combine 归约。seqused（可变有效 KV 长）按上游优先级**先于** paged 判定，paged 模式下页数由 `total_k/N_BLOCK/num_batches` 三个 ABI 标量恢复——不为省一个参数而破坏契约。两处数值细节值得注意：softmax 用 exp2 域（scale 预乘 log2e），causal 模式下以 `EX2_EMU_FREQ=16` 的频率把 MUFU 指令替换成**三次多项式软件模拟**（上游为吞吐做的混布，noncausal 走纯 MUFU）；FP8 K/V 有两条路——直接 `kind::f8f6f4` MMA，或 `k_stage_fp8` 路径由 softmax warpgroup 经 byte-permute+打包 FMA 反量化成 bf16 再进 f16 MMA。可选 temperature LSE（第二遍 `_scaled_exp2_row_sum_128` 按不同 scale 再求一次温度分母）。

## 代码结构

42 个函数分四层：layout 查询（`USE_GATHER4`/`KV_SUBTILES`/`TOKENS_PER_WARP`——qhead_per_kv 1/2/4 走 gather4 描述符路径、8/16 走普通 TMA，这条轴直接进了 config 矩阵）、数值小工具（`_row_max_128`/`_packed_f32x2`/`_ex2_emulation_2`）、发射器（`_issue_qk`/`_issue_pv`/`_tcgen05_commit`/`_dequant_kv`——FP8 反量化每线程管 `DEQUANT_ITERS = 128*8/128 = 8` 个 16 元素块、每批 4 个）、以及 **`_make_kernel`**——约 1600 行的 trace 巨构。`host_prelude` 编码五个 TMA map：K/V flat rank-3 / paged rank-4（page mode 挂在 descriptor 上，注释强调"rank 跟随张量否则静默产出垃圾"）、Q 的 gather4 map（gather 在指令不在 map）。设备侧 warp 分工写在常量区：softmax0（0-3）、softmax1（4-7）、Q load（8-11）、MMA（12）、KV load（13-14），共 512 线程，同步走 named barrier（编号表 BAR_TMEM_ALLOC=8 到 BAR_EPILOGUE=13/14，注释记载了上游撞号事故与本仓的规避约定）。TMEM 是**手工列空间**：S0/S1 占 [0,256)、O0/O1 续 256，P 精妙地 overlay 在 S 尾部（row_max/row_sum 已取走后销毁 S 尾巴是安全的）。末尾用 `inspect.Signature` 手工装配 launch ABI 并挂 `tirx.kernel_launch_params`——契约精确到参数顺序，paged/seqused/temperature 都是条件插入的条件参数。

## 性能设计

SM100 特性利用堪称全仓最密：① **gather4 TMA**（`cp.async.bulk.tensor.2d...tile::gather4`）——qhead_per_kv∈{1,2,4} 时一条指令按行元数据聚集加载 Q 的散行，`_resolve_gather4_rows` 解码越界标记与假列填充，另有对应的 L2 prefetch gather4 变体；② L2 hint 的方向性论证是注释金句：KV block 只属于一个 CTA（evict-first 流走），Q 行会被 topK 个 CTA 反复读（evict-last 留住）——"load-bearing, not cosmetic"；③ MMA warp 的发射序列 Q0K,Q1K,P0V,Q2K,P1V…用 2-slot S ring 让消费恰好赶在生产前面，V 的 TMA 等待被刻意推迟到两条 prologue QK 之后以重叠传输；④ **三档寄存器预算**：`setmaxnreg` 给 softmax 176/192（causal 与否）、store 112/80、other 48，注释论证三者和恒为 512 才能发射；⑤ 归约树用三输入 `max.f32`（66 条指令 vs 二输入树 127）；⑥ split-P 的 3/4 发布边界（`SPLIT_P_ARRIVE=96`）对齐 `tcgen05.st` 指令边。softmax 侧的分工也值得记：两个 warpgroup 轮流接管一组 query rows 的完整 softmax（缩放聚集、行 max、exp2、行和、P 打包、O partial 写出），`_scale_gather` 这种"Python 函数跑在 trace 期、list 索引直接寻址寄存器组"的写法是 Kern DSL 区分 trace 期与运行期的经典示例。所有 `f32x2` 打包、named barrier 编号（从 8 起避撞）、`DEQUANT_ITERS` 必须在模块作用域定义——每个决定都有"为什么"。

## 与其他家族对比

与 cuDNN 家族同是 CUTLASS DSL 源的重量级移植，差异在：MSA 无 CLC（work list 静态划分、grid=work_capacity、尾部 CTA 早退）、同步靠 named barrier 而非角色专属 Pipeline 对象、且保留了完整的"数值直译+逐行注释论证"文风（`(:689-705)` 式行号回指遍布全文）。与 flashinfer 家族相比是天平两端：一边 590 行标量递推，一边 1600 行 trace 装配十种 barrier 的流水线机器。它与本仓 FlashMLA 的 sparse 系列共享 gather4/TMEM overlay 等手法，横向对读能看出 MiniMax 与 DeepSeek 两大厂在稀疏 MLA 上的工程取舍。

## 新人提示

不要按行号顺序通读。推荐路径：先读 1-290 行的常量与注释区（这里浓缩了上游结构的全部事实）→ `_case` config 矩阵看参数空间（qhead_per_kv 是选路径的主轴，另有 bf16/e4m3/混合 dtype 模式与 f32/bf16 partial）→ trace 里按 warp 角色跳读：warp 0 的元数据发布、KV load 双 warp（1829 行起）、MMA warp（1943 行起，看 Q0K/Q1K/P0V 交替与 2-slot ring）、softmax 从 2100 行后（看 exp2 混布与 P 打包）。验证链也别错过：`prepare_data` 生成 CSR（`k2q`）与 paged 布局，`_frozen_qsplit` 冻结切分顺序做可复现断言，`assert_partials_match` 用 `live_partial_mask` 只比对活 partial——split-partial 语义的测试方法学本身值得学。三类注释必精读：**移植方法论**（magic number 要计算不要抄邻 kernel——bf16 抄 f16 描述符会静默算错；`_stage_16b` 硬编码 bf16 值会在多 Q 组时越界）、**同步编号**（上游 barrier 撞号的历史）、**L2 方向性**。把本文件当"移植疑难杂症手册"用：你将来踩的坑（fp8 无标量类型声明 uint8、paged rank-4、seqused 优先级高于 paged）这里都有带出处的答案。
