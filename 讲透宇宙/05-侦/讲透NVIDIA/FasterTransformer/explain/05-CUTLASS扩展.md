# 05 · CUTLASS 扩展：fpA_intB 混合 GEMM 与 MoE GEMM 模板族

## 角色定位

扩展层 `cutlass_extensions/`+宿主 `kernels/cutlass_kernels/` 补上游 CUTLASS 两空白：weight-only 混合 GEMM——激活 half/bf16 行主×权重 int4/int8 列主，边算边反量化；MoE grouped GEMM——num_experts 个专家矩阵（M 随路由变）一次 kernel 消化，普通 GEMM 即其 num_experts=1 特例（`kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm_template.h:494`）。`int8_gemm/` 为全量化旁支。

## 内部结构

镜像注入：目录复制上游 namespace 骨架（arch/、gemm/{warp,threadblock,kernel}/、epilogue/），文件全写进 `namespace cutlass`，不 fork 即注入模板查找路径——`cutlass_extensions/include/cutlass_extensions/gemm/threadblock/default_mma.h:35` 给 DefaultMma 加 half×int8/int4 半特化（tag OpMultiplyAddDequantizeInterleavedBToA），路由到 DqMma（多 IteratorScale），warp 层按 tag 换 MmaTensorOpComputeBWithF16；DefaultGemm 装配无感知命中。类型链：`cutlass_extensions/include/cutlass_extensions/gemm/kernel/mixed_gemm_B_layout.h:78` 的 LayoutDetailsB 定 B 布局+算子，default_fpA_intB_traits.h 定各 arch 形状，末端换 GemmFpAIntB；每精度组合一个 .cu（`kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm_fp16_int8.cu:20`；MoE 同构）。

## 外部连接

上游 CUTLASS 2.x 头件（DefaultGemmGrouped，`kernels/cutlass_kernels/moe_gemm/moe_gemm_kernels_template.h:120`），开关仓根 CMakeLists:44；下游 weight-only 层调 Runner::gemm/gemm_bias_act（类型对钉死 `kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm.h:28`），MoE 由 moe_kernels.cu 串路由+两级 GEMM（:725/:743）。

## 数据流

fp16×int4 链：①离线 `kernels/cutlass_kernels/cutlass_preprocessors.cc:500` 四变换：permute_B_rows（:138）→subbyte_transpose→interleave_column_major_tensor（:437）→加偏置+打包；②选瓦片后 A 走 gmem→smem→LDS；③warp 级解 uint4→half（interleaved_numeric_conversion.h），`cutlass_extensions/include/cutlass_extensions/gemm/threadblock/dq_mma_pipelined.h:371` 乘列 scale 进 B fragment；④`cutlass_extensions/include/cutlass_extensions/gemm/warp/mma_tensorop_compute_B_with_f16.h:230` 跑 HMMA、fp32 累加；⑤int32→bias+GELU_taylor/ReLU/SiLu→half。

## 设计决策

- **反量化级别**：Volta 在 gmem 加载后解包（`mixed_gemm_B_layout.h:32`），Turing+ 在 LDS 后 MMA 前的 warp 级（tag 义：解到 A 类型）——Tensor Core 无 int8×fp16 指令，B 须预提升成 A 类型复用 HMMA。
- **交错块勘误**："32×64"不实——`mixed_gemm_B_layout.h:78` 处列交错=256/64=4，int4 块=K=64 行×4 列（一条 cache line 恰装 K=64 多列），"32"属行置换；K 及 split-k 每段须整除 ThreadblockK=64，否则 throw（`fpA_intB_gemm_template.h:159`）。
- **MoE 差异在 grouped 调度非算术**：gemm_moe_problem_visitor.h 以路由前缀和生成 tile 队列，persistent threadblock（SM×occupancy 钳 2，`moe_gemm_kernels_template.h:156`）经 `cutlass_extensions/include/cutlass_extensions/gemm/kernel/moe_cutlass_kernel.h:388` 的 next_tile() 逐 tile 认领，A 按前缀和跳行（:400-402）、B 按专家跳（:405）；禁 split-k（`moe_gemm_kernels_template.h:70`）。
- **heuristic**（`kernels/cutlass_kernels/cutlass_heuristic.cc:102`）：quant 候选逐 config 探 occupancy，按末波闲置分数择优；m 小用小 tile（:163），n≥SM×256 禁 split-k（:152）。
- **dummy_stubs 勘误**："无 CUTLASS 桩"不成立——`kernels/cutlass_kernels/CMakeLists.txt:30` 无条件 GLOB 全部 .cu，豁免=宏+#ifdef 运行时 throw（`fpA_intB_gemm_template.h:60`）；`kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm_dummy_stubs.cu:20` 实例化 float 特化仅为链接（同目录 fpA_intB_gemm.h:107 自证）。

## 新人提示

- 读序：fpA_intB_gemm.h（同上目录）→dispatch 链→`mixed_gemm_B_layout.h`→`dq_mma_pipelined.h` 主循环。
- 预处理后权重打印无意义，对拍用 unprocessed 副本；改 B 布局只动 layout+preprocessors（:32）。
- 勘误：scales/biases 按 N 维行主（`kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm.h:30`）；float 特化是占位；int4 须 ThreadblockK=64（:6）。
