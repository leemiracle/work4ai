# 精讲：llama_model.py — 参考架构实现与 EAGLE draft 基座

> 位置：`python/mlc_llm/model/llama/llama_model.py` · 542 行 · 复杂度 complex
> 图谱：eagle/llava/mixtral 均 import 本文件复用；标签含「投机解码」

## 角色定位

全仓 40+ 架构的「原型样本」：读起来像 PyTorch，产出的是 **TVM Relax IRModule**。它定义全仓架构目录的写作范式——config 数据类、逐层组件、CausalLM 包装、接口族、KV cache 工厂、spec 导出。

更关键：LlamaForCausalLM 是**投机解码 hidden states 供给方**——专门提供 `*_to_last_hidden_states` 接口族供 EAGLE draft；eagle/llava/mixtral 从这里「抄作业」。

## 内部结构

自底向上七层积木：

1. **LlamaConfig(ConfigBase)**：`__post_init__` 负责默认值推导链——rope_theta 缺省 10000；context_window_size 回退 max_position_embeddings/max_sequence_length；num_key_value_heads 缺省=query 头数（MHA）；head_dim 缺省 hidden_size//heads；prefill_chunk_size 缺省 min(上下文, 8192)。
2. **LlamaFFN**：gate_up_proj 出 2×intermediate，split 两半 `silu(x1)*x2` 再 down_proj——fused gate-up。
3. **LlamaEmbedding**：nn.Embedding 加 `lm_head_forward`（权重转置 matmul）——tie_word_embeddings 省一份参数。
4. **LlamaAttention**：q/k/v 合并成一个 nn.Linear（输出 (hq+2hkv)×d）；KV 写入与注意力一起交给 `paged_kv_cache.attention_with_fused_qkv(...)`——**注意力 kernel 是黑盒**。
5. **LlamaDecoderLayer**：attention→残差→FFN→残差；`_set_tp()` 给四个投影打 `shard_strategy` 注解（qkv 按 [q,k,v] 段切 dim0，o_proj/mlp 切 dim1）；`_apply_residual` 在 TP>1 时插 `ccl_allreduce("sum")`。
6. **LlamaModel**：层循环，遇 `layer_partition` 边界插 `pipeline_stage_boundary`（PP 切分点）。
7. **LlamaForCausalLM**：接口族 + `create_paged_kv_cache` + `get_default_spec()`。

**推理接口族是矩阵式**：{prefill, decode, verify}×{单条, batch_}×{→logits, →hidden_states} 共 12 个方法；get_default_spec 逐一声明 shape 模板——spec 是 `export_tvm` 签名合同。

## 外部连接

- **imports**：`nn/`（PagedKVCache/RopeMode）、`op`、`support/`
- **被 import**：model.py 注册中心、llama_loader（配对）、eagle_model（draft）、llava_model（视觉接主干）、mixtral_model（MoE FFN）
- **运行时**：编译产物被 C++ `function_table.cc` 按符号加载

## 数据流

一次 decode step：

```
token id → embed() [TP 时 ccl_broadcast_from_worker0]
→ N× DecoderLayer:
    RMSNorm → qkv_proj → attention_with_fused_qkv
    (写 KV 页+算注意力, sm_scale=d^-0.5) → o_proj → [+allreduce] → +residual
    RMSNorm → gate_up/silu·x/down → +residual
→ final RMSNorm → get_logits（tie 时转置 embedding；强制 float32）
```

EAGLE 走 `batch_prefill_to_last_hidden_states`：唯一区别**不走 lm_head**，hidden states 直供 draft 模型。

## 设计决策

1. **注意力外包给 KV cache 对象**：不写注意力 kernel，只调 attention_with_fused_qkv——DispatchKVCacheCreation 有权在 TIR/FlashInfer 间换实现，模型层零感知。
2. **TP 用属性注解而非代码**：分片是「给权重贴标签」，切分在编译期；运行时唯一痕迹是残差 allreduce——单卡多卡代码一致。PP 同理。
3. **spec 驱动导出**：动态维度（seq_len/batch）留符号变量，供 LowBatchGemvSpecialize 克隆特化。
4. **GQA 兼容**：kv 头数可小于 query 头数，整除性有 assert。

## 新人提示

- **学新架构先读本文件再 diff 目标架构**：差异通常只在 config 字段、attention（MLA）或 FFN（MoE）。
- **接口命名律**：`batch_`=多请求拼接；`_to_last_hidden_states`=供 EAGLE draft。
- **shape 报错九成是 spec 与 forward 不符**。
- **tie_word_embeddings 陷阱**：共享时 logits 走转置矩阵乘，量化对齐留意。
- **别找采样**：编译期由 AttachGPUSamplingFunc 挂载。
