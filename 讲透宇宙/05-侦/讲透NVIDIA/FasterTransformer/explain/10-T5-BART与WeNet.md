# 10 · T5/BART 编码解码族与 WeNet Conformer 全家桶

## 角色定位

`models/t5`、`models/bart`、`models/wenet` 是 FT 的非 GPT 三线：T5 为标准 encoder-decoder（相对位置偏置+无 bias+pre-LN），BART 是其带 bias 近亲，wenet 是 Conformer 语音全家桶。勘误：`models/decoding/Decoding.cc` 并非 T5/BART 共用外壳，而是挂通用 Decoder 的独立遗留类（`models/decoding/Decoding.cc:30`），仅 th_op/tf_op decoding 消费；T5 与 BART 各自复制一份 Decoding，真正共享的只有 attention 层与 DynamicDecodeLayer 等积木，*_gemm.cc 均是调参二进制。

## 内部结构

T5Encoder 强制 pre-LN（`models/t5/T5Encoder.cc:197`），桶化相对位置表展开为 [head,seq,seq] bias。T5Decoder 是单步单元 self-attn→cross-attn→FFN，cross 直接吃 encoder_output（`models/t5/T5Decoder.cc:508`）。mem_kv 所有权钉版：四段 KV 由一次 reMalloc 切出（`models/t5/T5Decoding.cc:106`），写入在 cross 层 step==1 分支——首步对 encoder_output 做 K/V GEMM 直写 mem cache 并就地折入 bias（`layers/attention_layers/DecoderCrossAttentionLayer.cu:914`），此后只算 Q。相对偏置甄别：并非"只在第一层"，bias 构建一次、逐层喂给 self-attn（`models/t5/T5Decoder.cc:467`），cross 永不吃，与论文等价。无 bias 落在权重侧：张量数 `(11+gated)*(with_bias?2:1)`（`models/t5/T5DecoderLayerWeight.cc:49`），偏置槽不分配；tie embeddings 且无 bias 时 logits GEMM 的 alpha 折入 1/sqrt(d_model)。T5AdapterWeight 即 attention/FFN 后旁路 adapter（`models/t5/T5AdapterWeight.h:34`）。BART 差异三处：decoder 双 LN（`models/bart/BartDecoder.cc:392`）；bart_with_bias 默认 true（`models/bart/BartDecoderLayerWeight.h:38`）；BartEncoder 系 T5Encoder 改写非 Bert 变体。

wenet 组装序：CMVN（`models/wenet/WenetEncoder.cc:343`）→ conv2d 降采样 → 投影 → 位置表 slice；每层 macaron FFN(×0.5)→相对位置 MHSA→深度卷积→FFN(×0.5)，四个过渡均用 `invokeGeneralScaleAddBiasResidualPreLayerNorm` 融合残差+下一子层 pre-LN（FFN 处 0.5 即 macaron 半残差），收尾 norm_final、post-LN、CTC 头。RelPosition 与标准 MHA 差异：多 pos_weight GEMM 投影位置（`models/wenet/RelPositionAttentionLayer.cc:142`），Q/K/V bias 与 u/v 可学向量一次折叠，打分拆 Q·K^T 与 Q·P^T 再融合 softmax。勘误：全仓无 lightweight conv，只有 depthwise——一线程一通道、一块一 (batch,time)，fp32 累加、夹窗口代零填充、SiLU 融合（`models/wenet/WenetKernels.cu:1618`）。WenetDecoder 非自回归：CTC 候选整段一次跑完，ctc_weight 硬编码 0.3（`models/wenet/WenetDecoder.cc:221`）后联合重打分。

## 外部连接

T5 四路封装：`th_op/t5` 三 Op（`th_op/t5/T5DecodingOp.cc:406`）；Triton 双形态 `triton_backend/t5` 完整 enc-dec（`T5TritonModelInstance.cc:120`）与 `t5-encoder` 纯编码；TensorRT `tensorrt_plugin/t5`；TensorFlow `tf_op/t5`。BART 仅 th_op/bart；wenet 走 tensorrt_plugin/wenet 双 Plugin。

## 数据流

T5Decoding 端到端：beam>1 先 tile encoder 输出；主循环 `for (step...)`（`models/t5/T5Decoding.cc:723`）每步 embedding 查表 → `decoder_->forward` 逐层 [self-attn(KV cache+indirection 重排)→cross-attn(首步建 mem_kv)→FFN] → post-LN → logits GEMM（词表并行另需 AllGather）→ `dynamic_decode_layer_->forward` 完成 beam/采样，indirection 双缓冲 → NCCL 广播、全 finished 提前跳出 → gather_tree 或 beam_hyps 终化，采样仅转置。与 GPT decoding 差异即每层多一段 cross-attn，K/V 首步物化、后续零重算。

## 设计决策

①四段 KV 单块分配+指针切分：零碎片、一次释放。②cross K/V 首步物化+bias 折入：K/V GEMM 从 O(step) 降为 1 次。③相对偏置逐层喂参免每层存表，代价是二次方缓冲。④无 bias 以权重结构表达而非 GEMM beta，nullptr 覆盖两种 checkpoint。⑤Conformer 融合残差+pre-LN，macaron 0.5 成内核参数。⑥深度卷积自写 kernel 免 cuDNN 转置；整段重打分避逐 token 延迟。

## 新人提示

阅读序 `T5Encoder.cc→T5Decoder.cc→T5Decoding.cc→DecoderCrossAttentionLayer.cu`，BartDecoding 当 diff 复习。调试：decoder batch 维实为 batch×beam；断点打 step==1 看 mem_kv 建表；with_bias 使同一融合内核走 nullptr 分支。勘误：models/decoding 非共用外壳；wenet 只有 depthwise；BartEncoder 非 Bert 变体；T5 的 1/sqrt(d) 在 logits alpha 与 q_scaling（`models/t5/T5Encoder.cc:50`）。
