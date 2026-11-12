# 讲透 NVIDIA/FasterTransformer

NVIDIA FasterTransformer（FT）：2020-2023 年 NVIDIA 开源的 Transformer 推理加速库（CUDA C++，Tensor Parallel + 量化 + fused kernel + Triton/TensorRT 双部署面），本仓快照为最终提交 `df4a753`（2023-10-19，此后由 TensorRT-LLM 接棒）。本目录是 knowledge-graph 流水线的讲透产物集。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅（前轮） | `deepwiki/`（概览/构建/模型/attention/FFN/解码等页） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：**3447 节点 / 5717 边 / 14 层 / 16 步 tour / validator 0 issues / fingerprints 684 文件基线 @ df4a7534** |
| explain 精讲 | ✅ 12 篇 | `explain/01-12`（本轮，全部六节结构+行号锚源码核实） |
| onboarding | ⏳ 未做 | — |

图谱 14 层与 explain 12 篇的对应：L01 门面→（各篇外部连接节）；L02→01；L03→03；L04→04；L05→02；L06→05；L07→06；L08→04/06；L09→07/08；L10→09/10；L11→10；L12/L13→11；L14→12。

## explain 索引（12 篇，字数=不计空格字符，锚=行号锚均源码核实+独立抽验）

| 篇 | 文件 | 主题 | 字数 | 锚 |
|---|---|---|---|---|
| 组1 核心链 | | | | |
| 01 | `explain/01-utils底座与GEMM调优.md` | cublas 三兄弟/AlgoMap/gemm_test 离线调优闭环/Tensor-allocator 底座 | 2890 | 25 |
| 02 | `explain/02-MMHA注意力族.md` | MMHA 12 实例特化+Dh/Dh_MAX padding+unfused 三精度+DeBERTa/Longformer/XLNet 内核 | 2934 | 16 |
| 03 | `explain/03-数值kernel.md` | layernorm 三精度/激活/量化 scale 语义/布局变换/自定义 all-reduce 数据环 | 2978 | 22 |
| 04 | `explain/04-生成循环.md` | 惩罚/top-k/top-p 翻转累积/束搜索/DynamicDecode tensor 驱动调度 | 2896 | 12 |
| 05 | `explain/05-CUTLASS扩展.md` | cutlass_extensions 镜像注入/fpA_intB weight-only/int8/MoE grouped GEMM | 2981 | 21 |
| 06 | `explain/06-attention层封装.md` | Base/Unfused/Fused/Decoder/GptContext 层族+TP allreduce 位置+fp8/int8 子族 | 2888 | 18 |
| 组2 模型与部署 | | | | |
| 07 | `explain/07-BERT编码器系.md` | bert 三精度三目录+Deberta 相对位置桶+Longformer 滑窗+XLNet | 2900 | 14 |
| 08 | `explain/08-ViT-Swin视觉族.md` | vit/swin 双精度+ISwinTransformer 接口基类补建案例+shift/边界 kernel | 2900 | 25 |
| 09 | `explain/09-GPT生成族.md` | ParallelGpt 参数化双轨 vs GptJ/NeoX/FP8 复制改+BaseWeight 权重体系 | 2896 | 17 |
| 10 | `explain/10-T5-BART与WeNet.md` | mem_kv 四段切分+T5 无 bias 表达+Conformer 三件套 | 2896 | 18 |
| 11 | `explain/11-th_op-tf_op双框架.md` | th_op 75 节点 vs tf_op 20 节点对照/torch::jit::class_ 双轨/TF 图常量权重 | 2899 | 17 |
| 12 | `explain/12-部署后端.md` | Triton 七族 Model/Instance 分工+TensorRT plugin 五族权重哲学+多卡 NCCL 建立 | 2892 | 15 |

锚终验口径：126 个唯一 `文件:行号` 锚全部通过消歧验证器（basename 仓内唯一匹配自动展开；02 篇 `template.hpp` 为篇内显式声明的别名，4 锚内容逐条人工比对命中；05 篇同名双候选 `fpA_intB_gemm.h` 已改写为全路径）。

## 勘误清单（源码实证，写手甄别+主会话复核）

结构甄别（图谱/目录学层面）：

1. **ISwinTransformer 接口基类为图谱补建节点**：`th_op/swin/SwinOp.h:27` 纯虚接口（`ISwinTransformerINT8Func` 于 `SwinINT8Op.h:25` 同构）——C++ scanner 对 .h 内 class 声明盲区，该类靠人工补建；它使 SwinOp 一个 torch op 按 dtype 虚分派 fp32/half 实现，INT8 另立接口的根因是权重布局不同（量化 scale 多两段）。
2. **cutlass_extensions 镜像结构**：`cutlass_extensions/include/cutlass_extensions/{arch,epilogue,gemm}/...` 刻意镜像 CUTLASS 上游 namespace 目录，扩展在 `namespace cutlass` 内做半特化注入模板查找路径（如 `arch/mma.h:43` 新算子 tag→`default_mma.h:35`），不 fork 上游。
3. **fpA_intB_gemm 子目录双同名陷阱**：`kernels/cutlass_kernels/fpA_intB_gemm/fpA_intB_gemm.h`（运行时总入口）与 `cutlass_extensions/include/cutlass_extensions/gemm/kernel/fpA_intB_gemm.h`（kernel 模板）同名，引用必须带全路径。
4. **th_op DynamicDecodeOp 归 common**：`th_op/common/DynamicDecodeOp.cc` 包装的是通用 `layers/DynamicDecodeLayer`（logits 进 ids 出，独立于任何模型），非某模型专属 op。
5. **FusedSelfAttentionOp 归 decoder**：`tf_op/decoder/FusedSelfAttentionOp.cc` 包装自由函数 `fusedQKV_masked_attention_dispatch`（双侧目录对 `FusedAttentionLayer` 类零引用），TF 注册名实为 `FusedQkvMultiHeadAttention`。
6. **C++ scanner 全盲手扫域**：图谱 imports 边为人工手扫补建（CMake 体系 #include 解析全空），层归组与邻接经人工核源码。

源码级实证勘误（精选）：

7. **MMHA 不含 QKV 投影**：输入是投影已完成的 `qkv_buf`（GEMM 由 cublas 先做完）；fusion 范围=bias+rotary+K/V cache 写入+QK^T+softmax+PV+可选量化；非 2 幂 head size 走 `<T,Dh,Dh_MAX>` 双参数 padding 而非 fallback kernel。
8. **`_Gemm_`/`GemmIdx`/`ex_` 宏全仓不存在**：真实机制是各 layer 直调 `cublas_wrapper_->Gemm`；`utils/gemm.h` 的 Gemm 类是无外部引用半成品；GEMM 配置产物是空格分隔文本 `gemm_config.in` 非 json。
9. **`Bert::forward` 没有 embedding 查表与 pooling**：输入已是 `input_hidden_state`（`Bert.cc:317`）；"embedding→N 层→pooling"完整链只在 BertFP8 存在（`BertFP8.cc:260/:507`）。
10. **FT 的 Xlnet 没有 two-stream**：`XlnetAttentionLayer.cc:49` 用一个 batch=3 的 stridedBatchedGemm 同算 Q/K/V；双流是预训练排列 LM 专用。另 `Xlnet.cc` freeBuffer 漏 free `attn_out_buf_`。
11. **v2 BeamSearchLayer 是不可达死代码**：`DynamicDecodeLayer.cc:375` 的 `if (true || ...)` 使 online 分支永真；"bitmap top-k"全仓零命中属误传。
12. **int4 权重交错块实为 64 行×4 列**（`mixed_gemm_B_layout.h:78`，ColumnsInterleaved=256/64），"32×64"口径不实；`fpA_intB_gemm_dummy_stubs.cu` 是 float 链接桩而非"无 CUTLASS 时的桩"（真豁免=宏+#ifdef 运行时 throw）。
13. **ParallelGpt 无 `startForward` 入口**（那是 T5 Decoding 的 API），实为 forward 的 vector/TensorMap 双重载（`ParallelGpt.cc:534/574`）；`BaseWeight.h` 仅 49 行 FtWeight 结构体，权重加载走各 `*Weight::loadModel` 私有 .bin 格式（无 safetensors）；彩蛋：vector 版取 cum_log_probs 用 `at(4)`（`ParallelGpt.cc:567`）。
14. **`models/decoding/Decoding.cc` 不是 T5/BART 共用外壳**：它是挂通用 Decoder 的独立遗留类；T5/BART 各自复制近乎同构的 Decoding。T5 相对位置偏置由 `T5Decoding.cc:673` 构建一次逐层喂给 self-attn（cross 永不吃）；wenet 全仓无 "lightweight conv"，只有 depthwise（`WenetKernels.cu:1618`）。
15. **triton_backend 是纯库**：ProcessRequests 主循环/条件变量唤醒/auto-complete config.pbtxt 均不在本仓——线程模型实证在 `examples/cpp/multi_gpu_gpt/multi_gpu_gpt_triton_example.cc:350`（每卡一线程+MPI），后端壳在外部 fastertransformer_backend 仓；T5 是单实例内 encoder→decoding GPU 直传（`T5TritonModelInstance.cc:129`），非双仓 mem_kv 序列化协作。
16. **量化/数值细节**：`calibrate_quantize_weight_kernels.cu:89` 比较方向写反（该路径全仓零调用=死代码带雷）；`GeneralT5` LayerNorm 实为 RMSNorm（无均值无 beta）；本版无 gelu_tanh；fp8 融合 MMHA 是半成品（`cuda_fp8_utils.h:24` 的 `FP8_MHA` 宏被注释，不开宏则 fp8 输出分支为空 if 体）；ViT/Swin patch embedding 是真 conv2d（`utils/conv2d.h:80` NHWC+IMPLICIT_GEMM）非 unfold；Swin 的 linear 分类头不在仓内（`SwinOp.cc:134` 返回 pooled 特征）；`Swin.cc:116` freeBuffer 释放从未分配的 buffer 而漏释真分配者。

## 阅读指引

- 先 01（底座）→ 02/03（kernel 双支柱）→ 05（CUTLASS 高速路）→ 06（层封装）→ 04（生成循环），此为组1 核心链；
- 模型面按需：NLU 读 07，视觉读 08，生成读 09，seq2seq/语音读 10；
- 集成与部署收口读 11（双框架算子面）→ 12（Triton/TensorRT 后端）。
- 各篇均为六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），行号锚以 `src/fastertransformer/` 为根的相对路径书写。
