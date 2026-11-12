# 03 · 数值 kernel：layernorm / 激活 / 量化 / 布局 / 自定义 all-reduce

> 源码：`src/fastertransformer/kernels/`（103 文件）。行号锚均本地现场核实。

## 角色定位

kernels 是 FT 的计算原子层：GEMM 归 cublasLt，注意力另有子目录，逐元素变换、归约、重排全在此。本文覆盖 LN（fp16/int8/fp8 三代）、激活、量化、布局四族，加归约原语与自定义 all-reduce 两块底座。这些小 kernel 的启动与显存流量和 GEMM 同量级，是延迟敏感推理的主战场。

## 内部结构

**LN 族**：终态 `generalAddBiasResidualLayerNormOpt/Opt2` 用五个编译期开关全特例化（`kernels/layernorm_kernels.cu:24`），T 为 half2/bfloat162，每线程 2 元素故 mean 除 n 再除 2（`kernels/layernorm_kernels.cu:97`）；Opt2 改单遍 E[x²]−E[x]²、双 partial sum 一次归约（`kernels/layernorm_kernels.cu:240`）。T5 版实为 RMSNorm：不减均值、无 beta（`kernels/layernorm_kernels.cu:1780`），误传 beta 则回退标准版（`kernels/layernorm_kernels.cu:1814`）。

**激活族**：Gelu/Relu/Silu/Identity functor 化、half2 特化；enum `ActivationType`（`utils/activation_types.h:23`，含 GeGLU/ReGLU/SiGLU 门控）经 `layers/FfnLayer.cc:561` switch 映射到模板；门控乘与 int8 原地反量化/重量化收进同一 generic_activation。tanh_opt 在 sm75+ 用硬件指令（`kernels/activation_kernels.cu:41`）。

**量化族三套 scale 语义并存**：invokeQuantization 吃预倒数 scale；invokeQuantizeWeight 吃原始 amax、自算 x*127/amax 且按 per-channel amax[row]，同 kernel 顺手做 COL32/COL4_4R2_8C 布局置换（`kernels/quantize_weight.cu:72`）；校准核却输出 amax/127。int8 转换原语是单条 cvt.rni.sat.s8.f32 PTX（`kernels/int8_utils.cuh:25`）。

**布局族**：transpose_int8/layout_transformer 服务 COL32 互转；reverse_roll/image_shift_partition/image_merge 为 Swin 循环移位三件套；其余十余文件分担 multi-head、变长 padding 与小 GEMV。

**底座**：warpReduceSum 是 5 步 __shfl_xor_sync 蝴蝶（`kernels/reduce_kernel_utils.cuh:78`）；几乎所有数值 .cu include 此头——LN/softmax/topk/校准共用原语，改一处动全身。

## 外部连接

上游：FfnLayer/attention 层直调激活；bert_int8 串起量化→GEMM→COL32 融合 LN；ParallelGpt 权重加载期校准。custom AR 经 AbstractCustomComm 注入；moe_kernels/vit_kernels 另篇详述。

## 数据流

**例一：int8 量化→GEMM→反量化**。`models/bert_int8/BertLayerINT8.cc:210` 调 invokeQuantization(int8_buf_, from_tensor, m*n, &d_scale_list_[3])：ScaleList.h 钉死每 amax 槽 4 值 [amax, amax/127, amax/127/127, 127/amax]，+3 即预倒数 scale；内核 float4→char4 向量化（`kernels/quantization_int8_kernels.cu:22`）。GEMM 出 int32 后由 COL32 融合 LN 反量化；int8_mode=2 则 LN 按 per-token abs_max 量化并写回 dequant scale——边界闭环。

**例二：自定义 all-reduce 数据环**。8 卡各持 48MB peer buffer、P2P 互指。元素≤393216（`kernels/custom_ar_kernels.h:32`）走一口气内核（`kernels/custom_ar_kernels.cu:139`）：block0 前 8 线程向对端 barrier 槽写递增 flag，全员自旋等待（`kernels/custom_ar_kernels.cu:166`）；放行后每线程从 8 卡同 offset 各取 uint4（8 个 half），PTX add.f16x2 累加直写——NVLink 单跳。超阈值走 twoShot：先 reduce-scatter，跨 block 用 release/acquire 栅栏（`kernels/custom_ar_kernels.cu:275`）再 all-gather。小消息快过 NCCL：免协议状态机与多 kernel 启动，通信+栅栏+计算融进单个常驻 kernel。天花板：单节点 8 卡、NVSwitch、48MB，越界回退 NCCL（`utils/custom_ar_comm.cc:114`）。

## 设计决策

1) 编译期开关让分支消失，代价是实例爆炸。2) half2 向量化贯穿逐元素算子，打包深度 2 渗进公式。3) Opt 两遍 vs Opt2 单遍方差：后者省一半全局读但有消减风险，GPT-3 大 n 选 V2 属吞吐优先。4) 三套 scale 语义不统一是历史层积。5) 激活勘误：本版无 gelu_tanh——enum 只有一个 Gelu，tanh 近似是唯一实现（`kernels/activation_kernels.cu:54`）；门控三形态才是真多形态轴。

## 新人提示

勘误雷区：① `kernels/calibrate_quantize_weight_kernels.cu:89` if(amax_val>val) 方向写反，收敛到最小绝对值——侥幸该 Ldk 版全仓零调用，死代码带雷，启用即错。② `kernels/quantize_weight.cu:114` format!=1 & format!=2 误用位与，语义侥幸等价。③ V1 Opt 方差读裸 input（`kernels/layernorm_kernels.cu:104`）而非融合值，依赖 input 与 output 同 buffer 别名，换调用姿势即翻车——优先 Opt2。④ DEFALUT_ALGO_AR_SIZE_THRESHOLD 拼写错误钉进公开宏，勿顺手改。⑤ FLAG 取模 0x146 防回绕，复用 buffer 必须递增 flag。守则：动 LN 必查 n%2、n%32、blockDim/32 三重假设；动量化先画 scale 流向图。
