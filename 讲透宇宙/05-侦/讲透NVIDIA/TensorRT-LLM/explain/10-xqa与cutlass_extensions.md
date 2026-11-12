# 10 · xqa 与 cutlass_extensions：GQMMA 聚束解码与自足模板宇宙

## 一、角色定位

`cpp/kernels/xqa/` 是生成阶段（decode）专用的 MQA/GQA 优化 kernel 仓——README 第一句即定位 "optimized kernels for generation-phase MQA/GQA"。它与 fmha_v2 分工：fmha_v2 管 context 大 tile，xqa 管小批量、长 KV、beam/投机解码并存的解码态。`cpp/tensorrt_llm/cutlass_extensions/` 则是 TRT-LLM 对上游 CUTLASS 的扩展层：weight-only 量化 GEMM、NVLS 系统屏障等自研件。二者共同构成图谱 L13/L14 的 kernel 深水区。

## 二、内部结构

**xqa 按硬件代分文件**。`mha.cu` 是 Ampere 时代 SIMT 路径，靠手写转置机器（mha.cu:420 的 `template <bool swizzled, uint32_t rows, uint32_t cols>` 与 :1043 的 transArr2D/transInstInMatOuter 双层转置参数系）在寄存器里排布 HMMA 操作数。`mha_sm90.cu`（3710 行）是 Hopper TMA+QGMMA 路径：模板参数从 `nbThrds=64, beamWidth`（mha_sm90.cu:274）起排，`ScratchMem` 类（:542）管理 scratch，QGMMA 描述符来自 `gmma.cuh`/`gmma_impl.cuh`（4591 行、103 处 template，descriptor 编排的真正实现体）。`mla_sm120.cu` 是 Blackwell MLA 解码：`kernel_mha` 带 `__launch_bounds__(32*4*3,1)` 与 `__cluster_dims__(cgaSize,1,1)`（mla_sm120.cu:1801），`launchMLA`（:1885）经 `makeLaunchConfig`（:1945）配 PDL（ENABLE_PDL 程序化依赖启动，:1945-1987），TMA tensorMap Q/K/V 直传 kernel 参数。**投机解码支持**编译期开：`specDec.h` 的 `SpecDecParams{qSeqLen, qCuSeqLens, mask}`（specDec.h，SPEC_DEC 宏包裹）承载树状 mask；beamWidth 是模板一等公民。控制面脚本 `gen_cubins.py`/`gen_cpp_header.py` 把 kernel 编译成 cubin 并生成消费头——与 fmha_v2 的生成思路同宗。

**mha_stdheaders.cuh（1298 行）是仓内最奇特的文件**：kernel 里不能引标准库，于是手写 `numeric_limits<int32_t>`（mha_stdheaders.cuh:65）/`numeric_limits<float>`（:75）、`conditional`（:108）、`enable_if`（:123）、`is_same`（:227 device 实现，:199 顶部还给 host 侧留了 `std::is_same` 别名）——C++ 模板元编程在 CUDA device 侧的自足克隆。同目录 `barriers.cuh`（硬件 barrier/semaphore）、`ldgsts.cuh`（cp.async，内含 red.global 原子写）、`mhaUtils.cuh`、`RefChecker.cuh`（debug 对账）。

**cutlass_extensions 的两大件**。其一 weight-only 家族：`weight_only_quant_op.h` 定义 `WeightOnlyQuantOp` 四档枚举（UNDEFINED/PER_COLUMN_SCALE_ONLY/FINEGRAINED_SCALE_ONLY/FINEGRAINED_SCALE_AND_ZEROS）+ `isFinegrained/hasZero` constexpr 谓词——整个 weight-only 世界的"标尺类型"；SM100 落地件是 `gemm/collective/collective_builder_sm100_weightonly.hpp`/`collective_mma_sm100_weightonly.hpp`/`builders/sm100_umma_builder_weightonly.inl`（解包-进-MMA：dequantize 在 UMMA 流水内完成）。其二是 `system_barrier.h`：L65 起以 `CUTE_ARCH_MULTIMEM_SM90_ENABLED` 门控内联 PTX `multimem.red.release.gpu.global.add.u32`（:73）与 `.sys` 域变体（:77），L92 显式拦截未启用 NVLS 的误用——**RED 与 multimem 两条归约指令在这里同框**：red.global 用于单侧原子写（ldgsts.cuh），multimem.red 用于 NVLS 多播内存的归约。

## 三、外部连接

xqa 上游是 `tensorrt_llm/_torch/attention` 的 TRTLLM 后端与 `cpp/tensorrt_llm/kernels/decoderMaskedMultiheadAttention*`（老解码注意力接口）；`PAGED_KV_CACHE_LAYOUT=1` 编译期开关使其接受 vLLM 风格分页 KV 池（split-wise、sequence-first 布局）——跨生态复用的实证。运行时开关 `XQA_USE_QGMMA`（默认 Hopper 尽量走 TMA+QGMMA，置 0 回退 mha.cu）、`XQA_NB_SUB_SEQ`（每 KV head 的 thread block 数）。cutlass_extensions 的 weight-only 件被 `kernels/cutlass_kernels/fpA_intB_gemm/`（W4A/W8A GEMM 族）、`kernels/weightOnlyBatchedGemv/`（解码态批量 GEMV）与 `thop/weightOnlyQuantGemm.cpp`（torch op 绑定）三层消费；system_barrier.h 则被 allreduce/MNNVL 线（thop/allreduceOp.cpp）复用。

## 四、数据流

解码一轮：调度器给出 (nbReq, beam, kvLen) → 选路径：Hopper 且配置允许 → mha_sm90：TMA 装 KV tile → QGMMA 做 Q·K → scale+mask（specDec.h 的树 mask 若开）→ softmax → QGMMA 做 P·V → 半精度回写；Ampere/特殊形状 → mha.cu SIMT 路径寄存器转置；Blackwell MLA → mla_sm120 cluster kernel + PDL 与前序 kernel 重叠启动。cubin 产物由 gen_cubins.py 预编译、gen_cpp_header.py 生成头，运行时零 JIT。weight-only GEMM 一轮：量化权重 + scale（+zero）按 WeightOnlyQuantOp 档位流过 SM100 UMMA builder 的 epilogue 融合解包，激活侧保持高精度。

## 五、设计决策

① **按硬件代分文件而非统一抽象**：SIMT/QGMMA/cluster 三代执行模型差异太大，统一模板只会造出三层 if constexpr 的怪物；分文件的代价是接口手工同步（mha.h）。② **stdheaders 自足克隆**：编译期依赖必须闭包在 kernel 内，device 侧类型萃取不可依赖 libstdc++——这是嵌入式 CUDA 的经典取舍。③ **beamWidth 进模板**：解码态 beam 是常量，模板特化让寄存器分配静态化。④ **multimem.red 直接写 PTX 而非等 cooperative groups API**：NVLS 归约的 release 语义需要精确控制（.gpu vs .sys 域），内联汇总是当时的唯一通道。⑤ xlsx 设计记录（`mha_sm90_transpose.xlsx`）入仓但不参与构建——转置排布的可视化计算底稿，scanner 曾误判为代码（见 README 勘误）。

## 六、新人提示

入口顺序：xqa/README.md（环境变量与构建）→ mha.h 公共数据结构 → 按目标硬件代读对应 .cu。读 gmma_impl.cuh 前先读 gmma.cuh 的描述符布局，否则 4591 行全是黑话。调 QGMMA 回退问题时记得 XQA_USE_QGMMA=0 是最快的二分手段。改 weight-only 支持先在 weight_only_quant_op.h 定档位，再去 builder——档位是所有下游 kernel 的分派键。system_barrier 改动务必保留 L92 的编译期拦截，误用 multimem 在非 NVLS 机器上是运行期才炸的静默错。stdheaders 里加新 trait 时保持与 std 语义逐条对齐，注释里已给 cppreference 链接（mha_stdheaders.cuh:225）。
