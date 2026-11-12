# 07 · BERT 编码器系

## 角色定位

BERT 家族是编码器前向主力：bert/ 为 fp32/fp16/bf16 模板基线，bert_int8/bert_fp8 为量化支线，deberta/longformer/xlnet 为注意力变体。均输出 hidden states（无自回归解码）；出口在 th_op/bert 与 triton_backend/bert。

## 内部结构

**基线 Bert**：按 attention_type 组装 Fused/Unfused Attention 与 Gelu/Relu FFN。forward 主干（models/bert/Bert.cc:317）：输入 `input_hidden_state`+`sequence_lengths` → 四分支预处理 → 层循环（:459）内 pre-LN→attention→AddBiasResidual+LN→FFN → pre-LN 补终层 LN → RebuildPadding。**勘误一**：`Bert::forward` 无 embedding 查表与 pooling，输入已是 hidden state（查表在上游）；"embedding→N 层→pooling"完整链只在 BertFP8 存在。

**三精度=三份独立目录复制，非模板参数化**：Bert 实例化 float/half/bf16（Bert.cc:709）；BertINT8 自成一套，模型级仅一个 `BertLayerINT8` 复用，layer_idx 以 CPU Tensor 传入（models/bert_int8/BertINT8.cc:269）。int8 差异全在 scale：入口把基类 `BertLayerWeight*` 向下转型取 `scale_list_`（models/bert_int8/BertLayerINT8.cc:172）；mode1 每层量化输入（per-tensor），attention 出 int32 由 COL32 融合 LN 反量化，gemm2/gemm8 输出走 per-channel（`d_scale_list_[p2_offset_+3*hidden]`）；mode2/3 层间直传 int8+COL32，仅首末层量化/反量化。scale 载体 ScaleList 为平铺数组：72 激活 amax+`9*768` per-channel 权重 amax（p2_offset_=72，utils/ScaleList.h:46）。BertFP8 仅 `<fp8_e4m3,bf16>` 一组实例化（models/bert_fp8/BertFP8.cc:567），forward 吃 `input_ids`：单 kernel 融合去 padding+三表查表+embedding LN+量化（:260），循环后 dequant 回 half，pooler=末 token+dense+tanh 可选。

**FP8 权重二进制**：无魔数/版本头/对齐的裸字节流：每层按 weights→vec→sp→d_scale→h_scale 拼接，模型级 9 张 embedding/pooler 量殿后；serialize 仅逐段 memcpy（models/bert_fp8/serialize.hpp:13）。

## 外部连接

`bert_preprocess_kernels` 为 bert/int8/deberta 共用；disentangled/longformer/xlnet 各有专属 kernel；`layers/attention_layers` 下挂各注意力层及 int8/FP8 镜像；`bert/bert_gemm.cc` 生成 cublasLt 配置表（int8 走 igemm）。

## 数据流（Longformer 一条链）

输入 hidden `[b,s,in_dim]`+local/global_attn_mask(0/1;-10000/0)。①`invokeInitLongformerIdx` 用 cub 前缀和压出紧凑 `global_idx`+计数，`invokeLocalAttnMaskShift` 平移滑窗 mask。②每层 6 路投影：q/k/v+global k/v 走 Gemm，**global query 单独 stridedBatchedGemm（行数=max_global_token_num）**只为全局 token 生成查询（models/longformer/LongformerEncoder.cc:265）。③`invokeAddBiasTransposeToMultiHead` 一次转置 5 路，qg 另转（:290）。④双路径：滑窗按 window 分块，头/尾块 2w×w、中间块 3w×w batchedGemm；global 路径算"全局 q×全体 k"+"全体 q×全局 k"，softmax+scatter 融合单 kernel。⑤转回 single 头序→attn output Gemm→residual+LN→FFN→LN；全程 padded 不 remove-padding（与 Bert 相反）。

## 设计决策

**三目录 fork**：量化边角会污染模板主干，FT 整目录复制（改结构须动三处）。**Deberta 分工**：layer 只做三个 GEMM——c2c=QK^T、c2p=Qc·Kr^T（layers/attention_layers/DisentangledAttentionLayer.cc:309）、p2c=Kc·Qr^T；kernel 按相对距离现场算桶下标 gather 求和（v1 线性/v2 log 桶，kernels/disentangled_attention_kernels.cu:306），无预计算桶矩阵。模型级自查 word embedding（位置表传 nullptr），相对嵌入表 [2*bucket,h] 过 LN 送每层。**Xlnet 勘误二**：本仓**没有 two-stream**——双流是预训练排列 LM 专用；推理单流，`XlnetAttentionLayer` 一个 batch=3 的 stridedBatchedGemm 同算 Q/K/V（layers/xlnet_attention_layers/XlnetAttentionLayer.cc:49），相对项走 content/位置（`invokeRelShiftBd`，:163）/段编码三路；preProcess 预计算 mask/seg_mat/attr_k_head_r（Xlnet.cc:159），LN 后置。

## 新人提示

① `ScaleList::size_` 硬编码 `9*768`，非 768 隐层直接用有越界风险。② fused attention 在 fp32/bf16 或超长序列下自动降级 unfused（models/bert/Bert.cc:341）。③ BertINT8 向下转型不报错，传错权重读越界。④ Xlnet `freeBuffer` 漏 free `attn_out_buf_`（models/xlnet/Xlnet.cc:104），`word_emb_k_` 是死成员。⑤ Longformer 要求 `seq_len % window == 0`，`in_dim_` 仅首层生效。
