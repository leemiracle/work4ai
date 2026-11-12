# vllm/model_executor/models/llama.py — Llama 模型参考实现深解

## 角色定位

位于 **models（模型实现层）**，是 vLLM 的**基线模型与"新模型接入"事实模板**（图谱 tags：`model-implementation / baseline / tensor-parallel`）。280+ 个模型实现都以它的五件套结构为范本。在请求生命周期中处于最底层：engine → worker → model_runner 调用 `LlamaForCausalLM.forward()` 执行一次 batch 前向。文件头声明改编自 HF `modeling_llama.py`，但为 PagedAttention/TP/PP/CUDA graph 重写。

## 内部结构（图谱 contains 五类）

- **`LlamaMLP`**：`MergedColumnParallelLinear(gate_up_proj)`（两个 intermediate_size 拼接）→ `SiluAndMul` → `RowParallelLinear(down_proj)`。
- **`LlamaAttention`**：`QKVParallelLinear(qkv_proj)` 一次算出 Q/K/V → `split` → `rotary_emb(positions,q,k)` → `self.attn(q,k,v)`（统一 `Attention` 层，内部选 FlashAttention 等后端）→ `RowParallelLinear(o_proj)`。TP 切分逻辑：`num_heads = total_num_heads // tp_size`；GQA 时若 `kv_heads < tp_size` 则**复制 KV heads**（`num_kv_heads = max(1, ...)`）。Eagle3 draft 模型的 `layer_idx` 需减 `target_layer_count` 换算；`layer_types` 支持 per-layer sliding window。
- **`LlamaDecoderLayer`**：input_layernorm → attn → post_attention_layernorm → mlp，**residual 贯穿**（RMSNorm 返回新 hidden+新 residual）。
- **`LlamaModel`**（挂 `@support_torch_compile`，batch 维标 dynamic）：`VocabParallelEmbedding`（PP 首 rank；tied embeddings 时末 rank 也要）+ `make_layers` 生成层列表 + 末 rank 的 final norm。
- **`LlamaForCausalLM`**：`lm_head = ParallelLMHead`（仅末 rank，tied 时 `tie_weights` 共享 embedding）+ `LogitsProcessor`。另有 `LlamaBidirectionalForSequenceClassification / LlamaBidirectionalModel`——经 `as_seq_cls_model()/as_embedding_model()` 工厂**在类定义期动态生成基类**，实现双向注意力的嵌入/分类变体。

## 外部连接

图谱 **27 条出边**：vllm 并行原语（`distributed/__init__` 的 `get_pp_group/get_tensor_model_parallel_world_size`）、layers 全家桶（linear/layernorm/rotary_embedding/vocab_parallel_embedding/logits_processor/attention/quantization）、`compilation/decorators`、models/utils（`make_layers/AutoWeightsLoader/PPMissingLayer/WeightsMapper`）。**21 条入边**是被继承/复用的证据：mistral、glm/glm4、phi3、llama4、llama_eagle(3)、jamba、ernie45 等——Llama 家族方言都从这份文件派生。

## 数据流（含 TP/PP 交界）

```
input_ids ─VocabParallelEmbedding→ hidden_states
每层: RMSNorm → QKV 投影(column 切分,无通信) → split+RoPE → Attention
     (PagedAttention 读写 KV cache) → o_proj(RowParallel,**all-reduce**)
     RMSNorm → gate_up(column) → SiLU → down(RowParallel,all-reduce)
PP 边界: 非 last rank 返回 IntermediateTensors{hidden_states,residual}
         → 由 parallel_state 的 PP group send/recv_tensor_dict 传给下一 stage
末: final norm → lm_head(词表切分) → LogitsProcessor(all-gather logits)
```

## 关键设计决策

1. **能力 mixin 协议化**：`LlamaForCausalLM(LocalArgmaxMixin, nn.Module, SupportsLoRA, SupportsPP, SupportsEagle, SupportsEagle3, SupportsQuant)`。`SupportsPP`（interfaces.py:776）要求 `make_empty_intermediate_tensors` + forward 接受 `intermediate_tensors`——这是 PP 兼容的静态契约；`SupportsQuant.__new__` 自动把 quant_config 挂上实例并做权重名映射；`EagleModelMixin._maybe_add_hidden_state` 按配置采集中间层 hidden states 供 EAGLE 投影头训练/推测解码。
2. **weights 加载映射**：HF 权重名 → vLLM 模块名经 `WeightsMapper(orig_to_new_stacked)`：`q/k/v_proj → qkv_proj`（shard_id 区分）、`gate/up_proj → gate_up_proj`（0/1 槽位）；`AutoWeightsLoader` 递归加载。LoRA 侧配套 `packed_modules_mapping`（qkv_proj ↔ [q,k,v]）。
3. **PP 省显存**：非本 stage 的模块用 `PPMissingLayer()` 占位（embed/norm/lm_head），层范围由 `start_layer/end_layer` 控制。
4. **量化即插即用**：所有 linear 构造都收 `quant_config`，GPTQ/AWQ/FP8 在 layer 级替换 kernel，模型代码零改动。

## 新人提示

- **接入新模型先抄这份文件**：改 config 解析、attention 特例、`WeightsMapper`，注册到 registry 即可。
- 最易混淆的是 **column vs row parallel linear**（体现在 `layers/linear.py`，本文件是用法示范）：`QKVParallelLinear/MergedColumnParallelLinear/ColumnParallelLinear` 按**输出维切分**（每卡算自己那段输出，输入完整，无通信）；`RowParallelLinear` 按**输入维切分**（每卡持有部分输入的完整输出列，前向尾部 all-reduce 求和）。attention 里 qkv 用 column（按 head 切），o_proj/down_proj 用 row——**column 后接 row 恰好只需一次 all-reduce**，这是 Megatron 式 TP 的通信最优配对。
- `prefix` 参数贯穿构造（如 `model.layers.3.self_attn`），`extract_layer_index` 靠它定位层号——别在自定义层里丢掉。
- vocab 维度切分：`ParallelLMHead` 与 embedding 一样按词表切，logits 由 `LogitsProcessor` all-gather 回全词表。
