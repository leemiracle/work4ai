# vllm/model_executor/models/llama.py — Llama：模型接入的样板间与通用 fallback

> 源码：`vllm/model_executor/models/llama.py`（585 行）｜改编自 HF modeling_llama.py（:5）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

位于 **models（模型实现层）**，是 vLLM 的**基线模型与"新模型接入"事实模板**：MLP/Attention/DecoderLayer/Model/ForCausalLM 五件套（vllm/model_executor/models/llama.py:82/:125/:251/:347/:464）是全仓 300+ 模型实现的范本。2026-10 起多了一重身份——**registry 里的通用 fallback**：InternLM3/IQuestCoder/TeleChat3 与裸名 `LlamaModel`/`MistralModel` 等 5+ 架构直接映射 `("llama","LlamaForCausalLM")`（vllm/model_executor/models/registry.py:143-155/:242，:238 注释言明"多模型共享同架构全收录"）。生命周期中最底层：model_runner 调 `forward()` 执行 batch 前向；inference-only、兼容 HF 权重（:25），为 PagedAttention/TP/PP/CUDA graph 全面重写。

## ② 内部结构

- **`LlamaMLP`**（:82）：`MergedColumnParallelLinear(gate_up_proj)` 两段拼接（:95）→ `maybe_fused_act_quant`（:120，**2026-10 新**：激活与下游输入量化按注册表匹配融合 kernel）→ `RowParallelLinear(down_proj)`。仅支持 silu（:112）；`reduce_results/disable_tp` 留给复用方。
- **`LlamaAttention`**（:125）：TP 切分——`num_heads=total/tp_size`，GQA 时 `kv_heads<tp_size` 复制 KV 头（:156）；`head_dim` 优先取 config（:158）；`QKVParallelLinear`（:165）一次算 QKV → split → `rotary_emb`（:231，`get_rope` 以 `rope_parameters` dict 传参 :246）→ `Attention`（:212）→ `o_proj` RowParallel（:175）。per-layer sliding window 走 `layer_types`（:185-204），Eagle3 draft 需减 `target_layer_count` 换算层号（:190-196）。
- **`LlamaDecoderLayer`**（:251）：norm → attn → norm → mlp，**residual 贯穿**（:313-330，RMSNorm 返回新 hidden+新 residual）。兼容三方言：Smaug attention_bias（:267）、internlm3 qkv_bias（:272）、`is_causal=False` 走 `EncoderOnlyAttention`（:276-283，双向嵌入模型）。`attn_layer_type`（:257）与 `get_quant_config` 钩子（:332）是接缝。
- **`LlamaModel`**（:347，`@support_torch_compile` 标 4 参数 batch 维 dynamic :337-346）：`VocabParallelEmbedding` 条件三连——PP 首 rank / tied+末 rank / `spec_decode_needs_target_embed`（:377-388，MTP 需目标 embedding）+ `make_layers`（:389）+ 末 rank norm。
- **`LlamaForCausalLM`**（:464）：基类 `LocalArgmaxMixin, nn.Module, SupportsLoRA/PP/Eagle/Eagle3/Quant`；`lm_head` 仅末 rank（tied 共享 :509）；**新增 `compute_logits_local`**（:553，`skip_gather=True`）配 `LocalArgmaxMixin`（interfaces.py:1570）——draft 头 argmax 通信 O(batch×vocab)→O(batch×2×tp)。

## ③ 外部连接

- **依赖**：`layers/` 全家桶（linear/layernorm/attention/vocab_parallel_embedding/logits_processor/quantization/fusion）、`distributed/__init__`（:37）、`compilation/decorators`、models/utils（:70-79）、interfaces 六协议、adapters 工厂。
- **被复用三层参照系**：①registry 直映射（见①）；②import 派生——mistral（`MistralDecoderLayer(LlamaDecoderLayer)` vllm/model_executor/models/mistral.py:144 + `attn_layer_type=MistralAttention` :155）、llama4（`layer_type=Llama4DecoderLayer` llama4.py:725）、aria（MoE 换 MLP :245）、ernie_mtp（拿 `LlamaDecoderLayer` 当 MTP block :58）、llama_eagle(3)、jamba（借 `LlamaMLP` :40）等 20+ 文件；③**layer_type 参数化**——三级构造函数都收 `layer_type`（:257/:365/:489），MoE/MTP/多模态族不改本文件就能换层实现。SSM-hybrid 族（granitemoehybrid/olmo_hybrid）走独立 mamba 路线，不直接 import 本文件。
- 双向变体：`as_seq_cls_model/as_embedding_model(LlamaForCausalLM)` 类定义期动态生成基类（:568-571），TYPE_CHECKING 分支保类型检查（:564）。

## ④ 数据流（含 TP/PP 交界）

```
input_ids ─VocabParallelEmbedding→ hidden_states
每层: RMSNorm → QKV 投影(column 切分,无通信) → split+RoPE
     → Attention(PagedAttention 读写 KV cache) → o_proj(Row,**all-reduce**)
     RMSNorm → gate_up(column) → maybe_fused_act_quant → down(Row,all-reduce)
PP 边界: 非 last rank 返回 IntermediateTensors{hidden_states,residual,
         + aux_hidden_states_N 槽位}
         → parallel_state PP 组 isend/irecv_tensor_dict 传下一 stage
末 rank: final norm → lm_head(词表切分) → LogitsProcessor
        (all-gather；spec decode draft 走 compute_logits_local 免 gather)
```

**aux hidden states 跨 PP 机制是 2026-10 新面孔**：`supports_aux_hidden_states_over_pp=True`（:358）声明能力；层循环里 `_maybe_add_hidden_state`（:429/:439，取 hidden+residual 还原完整值）按 `aux_hidden_state_layers` 采样，`pack_local_aux_hidden_states`（:452）以 PP 槽位基址（bisect 算，interfaces.py:1652）打包进 IntermediateTensors，末 stage 用 `collect_remote_aux_hidden_states`（:425）收齐上游槽位——EAGLE3/MTP 投影头的中间层 hidden 在 PP 切分下不再丢失。

## ⑤ 设计决策

1. **能力协议静态化**：`SupportsPP` 要求 `make_empty_intermediate_tensors`+forward 收 `intermediate_tensors`（工厂化 :399）；`SupportsQuant.__new__` 自动挂 quant_config 并做权重名映射；`EagleModelMixin` 按配置采集中间层——兼容性在类声明里读得出来。
2. **weights 加载靠映射不改名**：`WeightsMapper(orig_to_new_stacked)`（:348-357）把 HF 的 `q/k/v_proj→qkv_proj`、`gate/up_proj→gate_up_proj` 槽位对齐；`AutoWeightsLoader` 递归加载（:459）；LoRA 侧配 `packed_modules_mapping`（:475）。
3. **PP 省显存**：非本 stage 模块用 `PPMissingLayer()` 占位（:388/:517），层范围由 `make_layers` 的 `start_layer/end_layer` 控制（:389）。
4. **量化即插即用再进一步**：所有 linear 收 `quant_config`（GPTQ/AWQ/FP8 在 layer 级换 kernel，模型代码零改动）；2026-10 的 `maybe_fused_act_quant`（:120）把"激活→量化"也收进融合注册表，按 (act 类型, 输入量化 key) 查表换 fused kernel。
5. **`prefix` 贯穿构造**，`extract_layer_index`（:141）靠它定位层号——sliding window 与 Eagle3 换算都依赖，自定义层别丢掉。

## ⑥ 新人提示

- **接入新模型先看这份文件**：多数情况不必抄——先看 registry 能否直映射；要改优先用 `layer_type`/`attn_layer_type` 注入（mistral/llama4/ernie_mtp 三范例），别复制整个文件。
- 最易混淆的是 **column vs row parallel**：`QKVParallelLinear/MergedColumnParallelLinear` 按输出维切（每卡算自己那段输出，无通信）；`RowParallelLinear` 按输入维切（尾部 all-reduce 求和）。qkv 用 column、o_proj/down 用 row——**column 后接 row 只需一次 all-reduce**，Megatron 式 TP 的通信最优配对。
- 词表维切分：`ParallelLMHead` 按词表切，logits 由 `LogitsProcessor` all-gather 回全词表（:550）；draft 走 `compute_logits_local`。
- bidirectional 变体（:574-585）是空壳，注意力类型由 `LlamaBidirectionalConfig` 控制。
- `forward` 的 `**extra_layer_kwargs`（:412）透传给每层——给层加新输入参数走这条通道，不改 Model 签名。
