# 09 · GPT 生成族：ParallelGpt / GptJ / GptNeoX / GptFP8 与权重体系

## 角色定位

GPT 族是 decode-only 自回归生成：门面一次调用吃进 prompt、吐出全部 token。`multi_gpu_gpt/ParallelGpt` 是参数化旗舰，靠 `gptVariantParams` 通吃 GPT/Megatron/OPT；`gptj/`、`gptneox/` 是旁路复刻（各自 fork 全套）；`gpt_fp8/` 是 GPT-NeoX-20B 的 FP8 专版。`models/BaseWeight.h` 实为 49 行 FtWeight 结构体（:24），加载逻辑分散在各 `*Weight::loadModel`。

## 内部结构

ParallelGpt 门面持 prefill 的 `ParallelGptContextDecoder`、逐 token 的 `ParallelGptDecoder`、采样分派 `DynamicDecodeLayer` 三件套（`models/multi_gpu_gpt/ParallelGpt.cc:34-86`），后者在 beam/topk/topp 子层间分派（`layers/DynamicDecodeLayer.h:34`）。两 decoder 组装的 attention 层族不同，decoding 侧不带 rotary；GptJ/GptNeoX 的层要传 `rotary_embedding_dim/neox_rotary_style`（`models/gptj/GptJDecoder.cc:26-40`）且残差不同，只得整链自持 decoder——"复制改"而非"参数化"的根因。GPT-J 的 parallel attention：QKV 融合权重取自 `attention.query_key_value` 且 bias 置零（`models/gptj/GptJDecoderLayerWeight.cc:116-122`），FFN 与 attention 共用同一 LayerNorm 输出、残差一次相加（`models/gptj/GptJDecoder.cc:298-311`）。GPT-NeoX 默认同款并行残差（`models/gptneox/GptNeoX.h:64`），预除 TP 再 all-reduce 复用缓冲（`models/gptneox/GptNeoXDecoder.cc:340-356`）；rotary 风格靠常量区分（`models/gptneox/GptNeoX.h:42`）。

## 外部连接

上游两入口：th_op 以 torch 张量数组喂构造器（`th_op/multi_gpu_gpt/ParallelGptOp.cc:24-49`），Triton 后端走 `loadModel` 读 `.bin`（`triton_backend/multi_gpu_gpt/ParallelGptTritonModel.cc:427`）。加载先 `getModelFileType(config.ini)` 定精度再 `loadWeightFromBin`，并探测 `model.lm_head.weight.bin` 决定输出投影是否共享 embedding（`models/multi_gpu_gpt/ParallelGptWeight.cc:293-323`）。prompt learning 三型齐备：prefix_prompt 按层存 KV 型权重、p_prompt_tuning 存 `[prompt_len,hidden]`（`ParallelGptWeight.cc:51-56`）。下游连 kernels 与 NCCL（TP all-gather logits、PP send/recv）。

## 数据流

以 `forward(TensorMap)`（`ParallelGpt.cc:574`）走：①解析 session/memory/continue_gen（:732）；②KV cache 一次 malloc、`value_cache_=key_cache_+size`（:134），K 尾维按 16 字节拆维（:808）；③按 task_name_ids 查 `prompt_learning_table`（:914）；④prefill：context decoder 一次前向算完 prompt 并写满 KV（:1090），置 `sequence_lengths=input_len-1`（:1105）；⑤循环 `step_=input_len..gen_len`（:1201），每步 decoder 单 token 增量写 KV（:1346）→末层 norm（:1356）→lm_head GEMM，TP>1 时 all-gather 拼 logits（:1374）；⑥dynamic decode 产出 ids/finished/cache_indirections/log_probs（:1501），采样参数经 :1458 合入输入表随步迭代；⑦`setOutputTensors` 剥 prompt 虚拟 token 收口（:1585）。

## 设计决策

家族双轨：ParallelGpt 参数化吸收变体（MoE 按 `moe_layer_index` 逐层切换），GptJ/GptNeoX/GptFP8 复制改——没有 microbatch、shared_contexts、int8 与 MoE，换 rotary/并行残差的专用融合。GptFP8 最特殊：checkpoint 存 fp32 权重+13 个 scale 文件，加载时在线量化，mode1 逐通道、mode2 逐张量（`models/gpt_fp8/GptFP8DecoderLayerWeight.cc:199-337`），scale 缺失退化恒等（:228）；KV cache 默认 bf16，仅 `FP8_MHA` 宏才 fp8（`models/gpt_fp8/GptFP8.h:76-82`）。

## 新人提示

四条勘误：①全仓 GPT 族无 `startForward`（那是 T5 Decoding 的 API），"两入口"实为 forward 的 vector/TensorMap 双重载；②BaseWeight.h 只有 FtWeight 四字段，无 getModelConfig/fromCkpt/safetensors/numpy 分支（那些在 T5/BERT Weight 与仓外 Triton python）；③GptJ 无 qk_layernorm、GptNeoX 无 rotary_pct 关键字，partial rotary 由后端换算成 `rotary_embedding_dim` 传入；④ParallelGpt 不复用 `models/decoder/Decoder.cc`（带 cross-attention 的 seq2seq 底座，:282）。另：vector 版 forward 取 cum_log_probs 用 `at(4)` 非 at(3)（`ParallelGpt.cc:567`）；GptFP8 仅实例化 fp8e4m3+bf16 一对（`GptFP8Weight.cc:232`）；入门先读 initialize 与 forward 两段。
