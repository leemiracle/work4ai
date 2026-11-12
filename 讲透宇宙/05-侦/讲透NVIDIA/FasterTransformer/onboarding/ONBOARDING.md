# FasterTransformer ONBOARDING

> 仓库：NVIDIA/FasterTransformer @ `df4a7534`（2023-10-19 最后提交，README 更新）· 代码根 `src/fastertransformer/`
> 图谱：3447 节点 / 5717 边 / 14 层 / 16 步 tour / 0 issues / fingerprints 684 文件 @ df4a7534
> 本文所有行号锚均从源码逐条核实（2026-11 快照），格式 `路径:行号`。

---

## 1. 项目定位

**FasterTransformer（FT）是 NVIDIA 的 Transformer 推理加速库——TensorRT-LLM 的前世代。** README 第一行即宣告其历史地位：开发已转入 TensorRT-LLM，本仓库保持可用但不再演进（`README.md:1`）。因此今天读 FT 的价值不在"用它"，而在读懂 LLM 推理引擎的源头工程范式：融合 kernel、GEMM 离线调优、双框架算子、服务化部署这四件后来被 TRT-LLM 全盘继承的事。

**技术形态**：纯 CUDA/C++ 实现的 Transformer 前向库，建立在 CUDA、cuBLAS、cuBLASLt 与 CUTLASS 之上（`README.md:32`），在 Volta/Turing/Ampere 上自动启用 Tensor Core FP16/BF16，Turing 后支持 INT8，Hopper 后支持 FP8。构建系统按目标框架切换：`BUILD_TF`/`BUILD_TF2` 打开 TensorFlow 出口（`CMakeLists.txt:47-48`），默认编译 PyTorch 出口与 C++ 库；CUDA 架构基线为 SM 70/75/80/86（`CMakeLists.txt:178`）。

**支持矩阵**（`README.md:37` 起）覆盖 19 个模型 × 框架组合：NLU 侧 BERT/XLNet/Longformer/DeBERTa，生成侧 GPT/OPT/GPT-J/GPT-NeoX/BLOOM/GPT-MoE/T5/T5-MoE/BART，视觉 Swin/ViT，语音 WeNet（仅 C++ 出口）。精度列 FP16/INT8/稀疏（Ampere 后）/FP8（Hopper 后），并行能力列张量并行与流水线并行。性能结论可作阅读预期锚点：BERT 大 batch 下 EFF-FT + INT8-v2 相对 FP16 约 3.5x（`README.md:143`）、极端 5x（`README.md:153`）；翻译任务上 FT-Decoder 相对 TF 1.5-3x、FT-Decoding 4-18x（`README.md:186`），相对 PyTorch Decoding 3.8-13x（`README.md:192`）——**decode 阶段（自回归逐步生成）是 FT 加速比最大的战场，这决定了 kernels 与 decoding 体系在仓库中的权重**。

**第三方基座**在 `3rdparty/`：CUTLASS（模板 GEMM，见第 5 节）、cub（排序原语）、Megatron-LM v2.6 子模块（`.gitmodules:1`，供 BLOOM/GPT-MoE checkpoint 转换）、trt_fused_multihead_attention（TensorRT 的 prefill FMHA kernel 直接借调）、fp8_qgmma_1x1（Hopper FP8 QGEMMA 模板）与 INIReader（Triton backend 读 ini 配置）。一个重要观察：FT 不是从零写一切，而是"自研 kernel + 精选借用"的混合体，借用边界就在 3rdparty。

## 2. 架构总览（14 层）

图谱 14 层沿一条主轴展开：**算子 → 层 → 模型 → 框架 → 部署**。这条轴在构建脚本里有权威自述——`src/fastertransformer/CMakeLists.txt:15-27` 的 `add_subdirectory` 序列依次挂载 `utils → kernels → layers → models → (tf_op|th_op) → triton_backend → tensorrt_plugin`，与图谱 L02→L14 一一对应。顶层 `CMakeLists.txt:301-305` 再挂 `3rdparty/src/examples/tests`。

| 图谱层 | 目录 | 文件数 | 职责 |
|---|---|---|---|
| L01 | 根 + cmake + docker | 18 | 门面与构建骨架 |
| L02 | `utils/` | 64 | Tensor 抽象/分配器/通信/GEMM 封装与调优 |
| L03 | `kernels/` 数值基础 | 57 | layernorm/激活/量化/转置/归约原语 |
| L04 | `kernels/` 生成循环 | 23 | 采样/束搜索/停止判定/惩罚 |
| L05 | `kernels/` 注意力族 | 34 | MMHA 12 实例 + unfused 三精度 + 变体 |
| L06 | `cutlass_extensions/` + `kernels/cutlass_kernels/` | 55 | 权重仅量化 GEMM 与 MoE GEMM |
| L07 | `layers/attention_layers*` | 54 | 注意力层封装（kernel 之上） |
| L08 | `layers/` 其余 | 41 | FFN/DynamicDecode/beam/sampling/adapter |
| L09 | `models/` 编码器系 | 66 | BERT/DeBERTa/Longformer/XLNet/ViT/Swin |
| L10 | `models/` 解码器系 | 90 | GPT 系/T5/BART/通用 Decoding |
| L11 | `models/wenet/` | 22 | Conformer 语音 |
| L12 | `th_op/` | 75 | PyTorch 出口 |
| L13 | `tf_op/` | 20 | TensorFlow 1.x 出口 |
| L14 | `triton_backend/` + `tensorrt_plugin/` | 65 | 生产部署双通道 |

三条结构规律：

1. **三分 kernels**：顶层 `kernels/` 按"数值基础（L03）/注意力（L05）/生成循环（L04）"自然分野——前向逐元素算子、注意力主干、自回归决策各成体系，目录即语义。
2. **每层一套三件套**：layer 抽象（如 `src/fastertransformer/layers/attention_layers/BaseAttentionLayer.h:140` 的 BaseAttentionLayer）+ weight 结构（`src/fastertransformer/layers/attention_layers/AttentionWeight.h:24`、`src/fastertransformer/layers/FfnWeight.h:24`）+ model 组装。官方把这套范式写成模板 `templates/adding_a_new_model/README.md`，是接入新模型的照葫芦画瓢指南。
3. **核心库框架无关**：L02-L11 不 include 任何 torch/tf 头，框架差异全部收敛在 L12/L13 的 Op 层——这是 FT 同时服务两大框架的关键设计。

## 3. utils 与 GEMM 调优

utils 是 FT 一切上层代码踩的地基，64 个文件里最有用的读码入口有四组。

**张量与内存**。FT 不依赖框架张量，自有抽象 `struct Tensor`（`src/fastertransformer/utils/Tensor.h:107`，字段含 where/type/shape/data，图谱 fanIn 44/fanOut 52）与命名张量表 `class TensorMap`（`src/fastertransformer/utils/Tensor.h:304`）——模型前向的输入输出全是 `TensorMap*`，这套约定贯穿 L07-L11。显存走分配器体系：`class IAllocator`（`src/fastertransformer/utils/allocator.h:64`）给出 `reMalloc` 复用语义（`src/fastertransformer/utils/allocator.h:75`：缓冲够大则原地复用并按需清零），派生 cudaAllocator/torchAllocator 等实现。`cuda_utils.h` 是全图谱扇入最高的头（86 入），设备查询、CudaTimer、错误检查都在这里；`memory_utils.cu`（约 910 行）承担 deviceBuffer 分配/拷贝。

**通信底座**。两路：跨机/跨卡走 NCCL（`utils/nccl_utils.cc` 的 ftNcclInitialize 建通信器，张量并行与流水线并行两组 comm）；单机多卡小消息走自研 IPC all-reduce——`class AbstractCustomComm`（`src/fastertransformer/utils/custom_ar_comm.h:31`）抽象接口，`src/fastertransformer/kernels/custom_ar_kernels.cu:139` 的 `oneShotAllReduceKernel` 与 `:202` 的 `twoShotAllReduceKernel` 落地（one-shot 适合小张量、two-shot 适合大张量）。这条低延迟路径专为 decode 阶段的 TP all-reduce 设计，是 FT 在小 batch 下压延迟的招式。

**GEMM 三兄弟**。cuBLAS 封装按精度分三个 Wrapper：`class cublasMMWrapper`（`src/fastertransformer/utils/cublasMMWrapper.h:30`，19 个方法，FP16/BF16/FP32 主路径）、cublasINT8MMWrapper（imma 描述符）、cublasFP8MMWrapper（`cublasFP8MMWrapper.cu`，约 1021 行，Hopper FP8 的 cublasLt heuristic/缩放管理）。

**调优闭环——FT 的招牌工程**。核心问题：cuBLAS 的 GEMM 算法空间巨大，同一形状不同 algo 性能差数倍。FT 的解法是离线扫表 + 运行时查表：
- `class cublasAlgoMap`（`src/fastertransformer/utils/cublasAlgoMap.h:82`）维护 m/n/k → algo 配置表，`src/fastertransformer/utils/cublasAlgoMap.cc:41` 的 `loadGemmConfig` 从 ini 文件加载；
- `utils/gemm.cc`（约 1184 行）在 `:265` 处按形状查 `cublas_algo_map_->getAlgo(...)` 选定算法再调 cublas；
- 扫表工具在 `utils/gemm_test/`，按模型族九组：`encoder/gpt/t5/swin/xlnet/decoding` 的 `*_gemm_func.cc` + INT8 变体 `encoder_igemm_func.cc`、`swin_igemm_func.cc`（gpt 侧 igemm 并入 `gpt_gemm_func.cc`，含稀疏 GEMM 探测）。

**使用闭环**：examples 下各模型二进制（如 `examples/cpp/multi_gpu_gpt`）先跑 gemm 调优扫全形状 → 产出 `*.in` 配置 → 生产加载查表。理解了这套"形状→算法"预调优，就理解了 FT 性能的第一来源。

## 4. kernels 体系

顶层 `kernels/` 114 个文件三分天下：数值基础、注意力族、生成循环。

**数值基础（L03）**。`layernorm_kernels.cu` 约 2953 行是仓内最大 .cu——dtype × 向量化宽度 × pre/post-norm × int8/fp8 变体的全模板展开，入口声明在 `src/fastertransformer/kernels/layernorm_kernels.h:54`（invokeAddBiasResidualLayerNorm 等）。归约原语 `reduce_kernel_utils.cuh`（约 370 行，图谱 27 入/30 出）是众多 kernel 复用的 warp/block 级 max/sum 基石。**remove-padding 约定**：`src/fastertransformer/kernels/bert_preprocess_kernels.h:37` 的 `invokeGetPaddingOffset` 把变长 batch 压成无 padding 紧凑布局再算 GEMM——变长序列不浪费算力，这是 BERT 路径的标准前处理。

**注意力族（L05）——FT 最著名的资产 MMHA**（Masked Multi-Head Attention）。参数结构 `Multihead_attention_params_base`（`src/fastertransformer/kernels/decoder_masked_multihead_attention.h:52`）与继承版 `:123`；分派器 `src/fastertransformer/kernels/decoder_masked_multihead_attention.cu:26` 的 `multihead_attention_` 按 `hidden_size_per_head` switch 转发，头宽 32-256 共 12 个编译实例（`kernels/decoder_masked_multihead_attention/` 目录下 12 个 .cu，含 48/80/96/112/144/160/192/224 这些非 2 幂头宽的独立实例化——控制编译体积与寄存器压力）。核心模板 `decoder_masked_multihead_attention_template.hpp`（约 1959 行）`:1119` 的 `masked_multihead_attention_kernel` 在**单个 kernel 内**完成 QKV 读入、KV cache 写回、QK 点积、softmax、输出重排——decode 步全程不落中间矩阵。device 工具库 `decoder_masked_multihead_attention_utils.h`（约 1856 行）提供 half/bf16/fp8 向量化原语，`src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_template.hpp:226` 的注记 "THREADS_PER_KEY * sizeof(K_vec_m_) = 128 bytes" 道出 KV cache 按 128B 事务对齐读的访存设计。**对照面 unfused 三精度族**：`unfused_attention_kernels.cu` 约 2512 行（FP16/BF16）、INT8 版 3229 行、FP8 版约 1160 行，QKV bias/转置（`src/fastertransformer/kernels/unfused_attention_kernels.h:117` invokeAddFusedQKVBiasTranspose）、softmax（`src/fastertransformer/kernels/unfused_attention_kernels.h:59` invokeMaskedSoftmax）、context 重排各自独立 kernel——用于 prefill 与 MMHA 不支持的头宽/精度组合。**prefill 高速路**：GPT 上下文注意力直接借用 TensorRT 的融合 kernel（`src/fastertransformer/layers/attention_layers/GptContextAttentionLayer.h:20` include `3rdparty/trt_fused_multihead_attention/qkvToContext.h`）。**变体支线**：DeBERTa 解缠注意力 `src/fastertransformer/kernels/disentangled_attention_kernels.h:36`（invokeDisentangledAttention，相对位置双偏置）、Longformer 滑窗 `src/fastertransformer/kernels/longformer_kernels.h:38`（invokeLongformerMHASoftmax）、XLNet 相对位置流 `src/fastertransformer/kernels/xlnet_attention_kernels.h:58`（invokeCalAttnScore）。

**生成循环（L04）**。自回归每步的"选下一个 token"决策 kernel 群：束搜索回溯 `src/fastertransformer/kernels/decoding_kernels.h:102`（invokeGatherTree）；top-p 采样 `src/fastertransformer/kernels/sampling_topp_kernels.h:30`（invokeTopPSampling，约 1430 行排序+累积截断实现）；束搜索假设池 `src/fastertransformer/kernels/beam_search_topk_kernels.h:31`（struct BeamHypotheses）；在线 softmax 束搜索 `src/fastertransformer/kernels/online_softmax_beamsearch_kernels.h:23`（invokeTopkSoftMax）；温度/重复惩罚在 `beam_search_penalty_kernels` 与 `sampling_penalty_kernel`；停止判定 stop_criteria、禁词 ban_bad_words、logprob 换算各一小文件。**注意甄别：top-k/top-p 联合采样的入口不在 decoding_kernels 而在 `src/fastertransformer/kernels/sampling_topk_kernels.h:82` 的 invokeTopKTopPSampling**，decoding_kernels 管的是 gatherTree/初始化/finalize 等循环骨架。GPT 专属辅助在 `src/fastertransformer/kernels/gpt_kernels.h:87`（invokeBuildDecoderAttentionMask）、`:96`（invokeLookupHiddenStateOfLastToken）等 20 余个 invoke。

**两个跨类 kernel**：MoE 门控路由 `src/fastertransformer/kernels/moe_kernels.h:47`（topk_gating_softmax_kernelLauncher：softmax→top-k→按专家 permute，`src/fastertransformer/kernels/moe_kernels.h:64` 还有 CubKeyValueSorter 类封装 cub 排序）与第 3 节已述的 custom all-reduce。

## 5. CUTLASS 扩展

绕开 cuBLAS 的自研 GEMM 高速路，服务 cuBLAS 覆盖不了的两类场景：**权重仅量化 GEMM（w4a16/w8a16）** 与 **MoE 专家分组 GEMM**。代码两处合流：

**`cutlass_extensions/include/cutlass_extensions/`——模板扩展，目录结构与 CUTLASS 原生镜像对齐**（arch/gemm/epilogue/... 对应 cutlass 同名目录）：
- `src/fastertransformer/cutlass_extensions/include/cutlass_extensions/ft_gemm_configs.h:51` 的 `struct CutlassGemmConfig`：CTA tile/stage/cluster 候选集统一定义；
- 反量化主线：`src/fastertransformer/cutlass_extensions/include/cutlass_extensions/gemm/warp/mma_tensorop_dequantizer.h:80` 声明的 `class MmaTensorOpDequantizer`（四个特化在 `:89/:196/:289/:376`）——在 **mma 输出片段上就地反量化**（scale/zero-point/interleave 逆变换），省掉单独的 dequant kernel 与中间显存；`arch/mma.h` 的 OpMultiplyAddDequantizeInterleavedBToA 把 interleave 逆变换再下沉到 mma 层；
- MoE 调度：`src/fastertransformer/cutlass_extensions/include/cutlass_extensions/gemm/kernel/moe_problem_visitor.h:50` 的 `BaseMoeProblemVisitor` 与 `src/fastertransformer/cutlass_extensions/include/cutlass_extensions/gemm/kernel/gemm_moe_problem_visitor.h:58` 的 `GemmMoeProblemVisitor`——按"每个 expert 一段 M 维"切 tile，天然处理 expert 间不均匀；
- 布局与数值：`tile_interleaved_layout.h`（interleaved 权重布局）、`interleaved_numeric_conversion.h`（int4/int8 → 半精度转换）。

**`kernels/cutlass_kernels/`——面向用户的落地**：
- fpA_intB 混合精度：`src/fastertransformer/kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm.h:39` 的 `class CutlassFpAIntBGemmRunner`（`:44` gemm / `:55` gemm_bias_act 两个入口），模板主体 `src/fastertransformer/kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm_template.h:107` 组装 CUTLASS DefaultGemm、`:128` 换成 `cutlass::gemm::kernel::GemmFpAIntB` 自定义 kernel（Mma 片段带反量化）；
- MoE GEMM：`moe_gemm/moe_gemm_kernels_template.h`（约 920 行，对齐 padding + expert 批次处理），实例化按 **A/B dtype 全组合 7 个 .cu**：`moe_gemm_kernels_fp16_fp16/fp16_uint4/fp16_uint8/bf16_bf16/bf16_uint4/bf16_uint8/fp32_fp32.cu`；
- INT8：`src/fastertransformer/kernels/cutlass_kernels/int8_gemm/int8_gemm.h:61` 的 `dispatch_to_arch` 按 SM 架构分派 kernel 变体，四档输出精度；
- 启发式：`src/fastertransformer/kernels/cutlass_kernels/cutlass_heuristic.cc:110` 的 `get_candidate_configs`（按 SM 与 weight-only 场景枚举 tile/stage/splitK 候选）+ `src/fastertransformer/kernels/cutlass_kernels/cutlass_heuristic.h:26` 的 `estimate_best_config_from_occupancies`（按 occupancy 估最优）——相当于 CUTLASS 版的"gemm 调优"，但不需要离线扫表。

选型心法：**FP16/BF16 主路径 GEMM 永远走 cublas 三兄弟（第 3 节），INT8/权重仅量化/MoE 才走 CUTLASS 线**——两条 GEMM 路线并存是 FT 的常态，读代码时先看调用方拿的是哪个 Wrapper/Runner。

## 6. models 三系

`models/` 178 个文件按"算什么"分三系，每族都遵循**四件套范式**：顶层模型类 + Layer/Block 组件 + Weight 权重组织 + gemm 调优入口（接入新模型照 `templates/adding_a_new_model/` 模板走同样四步）。

**编码器系（L09，NLU 与视觉，66 文件）**。主力 `class Bert: public BaseLayer`（`src/fastertransformer/models/bert/Bert.h:33`），前向 `src/fastertransformer/models/bert/Bert.cc:306`：embedding → 逐层（attention+FFN+residual/layernorm）→ 输出，全程 remove-padding 紧凑布局；INT8 镜像 `bert_int8/BertINT8.cc`、FP8 镜像 bert_fp8。变体族：DeBERTa（解缠注意力）、Longformer（滑窗）、XLNet（两流）。**视觉双家族注意类名甄别**：Swin 的模型类真名是 `SwinTransformer`（`src/fastertransformer/models/swin/Swin.cc:166` 的 forward，`:124` 的 patchEmbed 是图像切块入口；SwinBlock×SwinBasicLayer 组 stage），ViT 的真名是 `ViTTransformer`（`src/fastertransformer/models/vit/ViT.cc:260`）——图谱/目录里的 "Swin"/"ViT" 只是目录名，代码里 grep "class Swin" 会落空。两者各有 INT8 镜像（swin_int8/vit_int8），配专属 kernel（image_shift_partition/image_merge/normalize）。

**解码器系（L10，生成家族，90 文件）**。核心 `multi_gpu_gpt`：`src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.cc:534` 的 forward（约 1786 行，仓内最大单文件之一）总装**两阶段生成**——prefill 阶段 `src/fastertransformer/models/multi_gpu_gpt/ParallelGptContextDecoder.cc:303` 对整段 prompt 做因果注意力并写满 KV cache（走 TRT FMHA），decode 阶段逐 token 走 MMHA；张量并行按头切分、流水线并行按层切分，另有 prompt learning（p-tuning）支持。同构变体：GPT-J 并行结构（`gptj/GptJ.cc`，约 1250 行）、GPT-NeoX 旋转 embedding（`gptneox/GptNeoX.cc`，约 1200 行）、FP8 版 `class GptFP8`（`src/fastertransformer/models/gpt_fp8/GptFP8.h:30`，前向 `src/fastertransformer/models/gpt_fp8/GptFP8.cc:245`，Hopper 专属）。编码-解码双流：T5 全家（`src/fastertransformer/models/t5/T5Decoding.cc:26` 起，约 1080 行，相对位置偏置 + 束搜索终局）、BART 全套 Encoder/Decoder/Decoding。**通用组件**：`src/fastertransformer/models/decoder/Decoder.cc:160`（自回归层循环装配）与 `src/fastertransformer/models/decoding/Decoding.cc:304`（beamsearch/采样终局封装，KV cache 重排、logprob 统计）被 GPT/BART 共用——T5/GPT 各自的 Decoding 是专用版。

**WeNet 语音系（L11，22 文件）**。FT 唯一的端到端语音族：`src/fastertransformer/models/wenet/WenetEncoder.cc:299`（Conformer 块 = 自注意力+深度卷积+FFN）、`src/fastertransformer/models/wenet/WenetDecoder.cc:195`（注意力重打分+CTC）、`ConformerConvLayer.cc`（下采样卷积模块）、`RelPositionAttentionLayer.cc`（相对位置注意力）与专属 kernel `WenetKernels.cu`（约 3220 行）。其输出走 CIF 并行框架而非自回归逐 token——与文本族的生成循环体系完全无关，README 矩阵中 WeNet 也确实只有 C++ 出口（`README.md:37` 表内）。

权重组织一条线：`models/BaseWeight.h` 为公共基类，各层权重结构如 `src/fastertransformer/layers/attention_layers/AttentionWeight.h:24`/`src/fastertransformer/layers/FfnWeight.h:24`（kernel nullptr 判空的"可选权重"惯例，LoRA adapter 权重即这样挂进 AttentionWeight）。

## 7. th_op/tf_op 双框架

FT 的框架策略是**核心库框架无关 + Op 薄封装**：th_op（75 节点）与 tf_op（20 节点）平行出口，框架差异全部收敛在此。

**th_op——PyTorch 出口（L12）**。桥接核心 `src/fastertransformer/th_op/th_utils.h:65` 的 `convert_tensor(torch::Tensor)`（重载 `:68` 可指定 MemoryType）完成 torch 张量→FT Tensor 零拷贝包装（只借 data 指针与 shape）。15 个模型族目录，每族把模型注册为 torch CustomClass：BERT 侧 `src/fastertransformer/th_op/bert/BertOp.h:276` 的 `class FasterTransformerBert: public torch::jit::CustomClassHolder`，在 `src/fastertransformer/th_op/bert/BertOp.cc:166-168` 用 `torch::jit::class_` 双命名注册（"FasterTransformerBert" 与 "FasterTransformer::Bert"）；GPT 主力同款双注册（`src/fastertransformer/th_op/multi_gpu_gpt/ParallelGptOp.cc:210` 与 `:212`）。Python 侧 `torch.ops.fastertransformer.Bert.forward(...)` 即直达 L05-L12 全部能力。三个特色算子：`src/fastertransformer/th_op/common/DynamicDecodeOp.cc:447/:449`（把 DynamicDecodeLayer 暴露给 Triton 的流式解码做逐步输出）、`src/fastertransformer/th_op/t5/T5DecodingOp.h:139`（FasterTransformerT5Decoding）、量化工具 `src/fastertransformer/th_op/multi_gpu_gpt/WeightTransposeCalibrateQuantizeOp.h:23`——**此处有个名实甄别：该文件名叫 Op，里面其实没有 Op 类，只有一个自由函数 `weight_transpose_calibrate_quantize(Tensor weight)` 供权重量化校准调用**。

**tf_op——TensorFlow 1.x 出口（L13）**。公共基类 `src/fastertransformer/tf_op/BaseOp.h:45` 的 `class BaseOp: public tf::OpKernel`（封装 OpKernelContext 与 FT Tensor 双向转换），7 个族目录（bert/deberta/decoder/decoding/encoder/gpt/t5），如 `src/fastertransformer/tf_op/bert/BertOp.cc:84` 的 `class BertOp: public BaseOp<T>`。特色是 `tf_op/decoder/FusedSelfAttentionOp.cc` 融合注意力专用算子与 weight_quantize_op 量化工具。

**对照结论**：th_op:tf_op ≈ 75:20 节点（3.75:1）。swin/vit/gptneox/longformer/bart/gpt_fp8 等 2022 年后的新模型只在 PyTorch 侧落地——FT 后期重心已明确倒向 PyTorch/Triton 生态，tf_op 是 TF1.x 时代的存量维护。新人除非维护老 TF 服务，否则优先读 th_op。

## 8. 新人上手

**编译与环境**。从 `README.md` 安装节起步；`docker/Dockerfile.torch` 是 PyTorch 出口的一键环境。关键 CMake 开关：`BUILD_TF/BUILD_TF2`（TF 出口，需 TF_PATH，`CMakeLists.txt:111` 强校验）、`ENABLE_FP8`（Hopper FP8 线）、SM 架构集合（`CMakeLists.txt:178`）。编译产物：C++ 库 + 各 examples 二进制 + Triton backend so。

**三条阅读路线**（按目的选一条主轴，图谱 16 步 tour 同序）：
1. **kernel 主线**（想懂 CUDA 优化）：`kernels/reduce_kernel_utils.cuh`（归约原语）→ `layernorm_kernels.cu`（模板展开范式）→ `src/fastertransformer/kernels/decoder_masked_multihead_attention/decoder_masked_multihead_attention_template.hpp:1119`（MMHA 单 kernel 全程，配 `decoder_masked_multihead_attention_utils.h` 的向量化原语）→ `unfused_attention_kernels.cu` 对照 → `sampling_topp_kernels.cu`（排序截断）。
2. **模型主线**（想接入/移植模型）：`templates/adding_a_new_model/README.md` → Bert 四件套（Bert.h/Bert.cc/`models/bert/BertWeight.cc`/encoder_gemm_func）→ `src/fastertransformer/models/multi_gpu_gpt/ParallelGpt.cc:534`（两阶段生成+双并行）→ `src/fastertransformer/models/decoding/Decoding.cc:304`。
3. **部署主线**（想做服务化）：`th_op/th_utils.h` → 一个 Op（如 `th_op/bert/BertOp.cc`）→ `triton_backend/transformer_triton_backend.hpp` → `triton_backend/multi_gpu_gpt/ParallelGptTritonModel.cc`。

**Triton backend 七族**：目录 bert/gptj/gptneox/multi_gpu_gpt/multi_gpu_gpt_fp8/t5/t5-encoder（`src/fastertransformer/triton_backend/CMakeLists.txt:20-28` 逐个 add_subdirectory，FP8 族受 ENABLE_FP8 门控）。协议核心在 `triton_backend/transformer_triton_backend.hpp`（约 315 行）：`struct AbstractTransformerModelInstance`（`:266`，纯虚 forward + 流式回调 registerCallback）与 `struct AbstractTransformerModel`（`:289`）——后者挂六个静态工厂 `createGptModel/createGptFP8Model/createGptJModel/createGptNeoXModel/createT5Model/createT5EncoderModel`（`:290-295`，按模型仓库的 ini 目录装配）。GPT 工厂落地在 `src/fastertransformer/triton_backend/multi_gpu_gpt/ParallelGptTritonModel.cc:27`，按 ini 读出的 data_type 分派 half/bf16/float 三分支（`:97/:119/:141`）。NCCL 通信器建立统一在 `src/fastertransformer/triton_backend/transformer_triton_backend.cpp:19` 的 `createNcclParams`（TP/PP 两组 comm，多节点走 MPI bcast 换 uid）。**分工**：TritonModel（类工厂/权重加载/跨卡共享）与 TritonModelInstance（单请求张量整理→调 FT 前向）成对出现——Triton 的 continuous batching 由 server 侧驱动，FT 侧只管单个 batch 的前向。

**TensorRT plugin 五族**：bert_fp8/swin/t5/vit/wenet（`src/fastertransformer/tensorrt_plugin/`），以 IPluginV2DynamicExt 嵌入 TRT 图。样本：`src/fastertransformer/tensorrt_plugin/swin/swinTransformerPlugin.h:62` 的 `class SwinTransformerPlugin: public nvinfer1::IPluginV2DynamicExt`（Creator 在 `:218`，INT8 镜像 `src/fastertransformer/tensorrt_plugin/swin/swinTransformerINT8Plugin.h:62`）；T5 是双插件——编码 `src/fastertransformer/tensorrt_plugin/t5/T5Plugin.cu:576` 的 T5EncoderPlugin::enqueue 与生成 `:1309` 的 T5DecodingPlugin::enqueue；语音 `src/fastertransformer/tensorrt_plugin/wenet/EncoderPlugin.cc:401` 的 enqueue。

**测试与验证资产**：`tests/` 下 moe、gemm_dequantize、int8_gemm、weight_only_quant_ops、longformer、decoding、unittests（google test）七组；examples 按出口分 cpp/pytorch/tensorflow/tensorrt/onnx 五目录，其中 `examples/cpp/` 的 16 个族二进制是跑 GEMM 调优与端到端 benchmark 的标准入口。

**迁移提示**：所有新工作应基于 TensorRT-LLM（`README.md:1`）。FT 的当代价值是历史源码：MMHA 融合注意力、custom all-reduce、CUTLASS 权重仅量化 GEMM、gemm 离线调优这套组合拳在 TRT-LLM 中都能找到直系后代——把 FT 读透，TRT-LLM 的代码地图自然浮现。

---

*生成于 understand-anything 流水线（图谱 3447n/5717e/14L/16T@df4a7534）；行号锚全部从源码逐条核实。*
