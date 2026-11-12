# 08 · llama 家族深潜：RMSNorm/RoPE 骨架与 200+ 家族的公共祖先

## ① 角色定位

`src/transformers/models/llama/modeling_llama.py` 只有 512 行、9 个类、4 个模块级函数，却是全仓复用率最高的文件：**107 个家族的 modular 文件 import 它**（models/*/modular_*.py 全量 grep 实测），另有 26 个家族的 configuration 引用 llama 配置。qwen2/qwen3/phi/mistral 系……几乎所有 2023 后的 dense decoder 模型都是它的语法变奏。它是 modular 继承网（见第 07 篇）的根节点，读懂它等于拿到半仓模型的通行证。

## ② 内部结构

骨架自底向上四层：

- **LlamaRMSNorm**（L53）：注释直言"equivalent to T5LayerNorm"（L56-57）。forward 里先 `to(torch.float32)` 再求 `pow(2).mean` 与 `rsqrt`（L61-63），权重乘法回到原 dtype——fp16/bf16 下数值稳定的教科书姿势。类上挂着 `@use_kernel_forward_from_hub("RMSNorm")`（L52）：可从 kernels-community 换装 Triton 实现（详见第 12 篇 hub_kernels）。
- **RoPE 三件套**：LlamaRotaryEmbedding（L73）预计算 cos/sin；`rotate_half`（L130）把后半维取负拼接；`apply_rotary_pos_emb`（L138，装饰器 L137 同样是 hub kernel 挂点）做 `(q*cos)+(rotate_half(q)*sin)`。unsqueeze_dim=1 的广播语义在 docstring 里讲了整整一段（L141-155）——head 维在前在后都能适配。
- **LlamaMLP**（L163）：SwiGLU 三线性层 gate_proj/up_proj/down_proj（L169-171），`down_proj(act_fn(gate(x)) * up(x))`（L175），激活函数经 `ACT2FN[config.hidden_act]` 字符串反查（L172），bias 由 `config.mlp_bias` 控制——llama3.1 起新增的可选项。
- **LlamaAttention**（L217）：q/k/v/o 四投影（L231-238），head_dim 优先 `getattr(config,"head_dim",...)` 显式配置（L221），KV 头数少于 Q 头数即 GQA，`repeat_kv`（L179）在 eager 路径展开 KV。`is_causal=True` 在 L229 直接写死。`eager_attention_forward`（L191）是兜底后端：softmax 前显式升 float32（L205）。

LlamaDecoderLayer（L284）继承 **GradientCheckpointingLayer**（非裸 nn.Module）；LlamaForCausalLM（L421）混入 GenerationMixin，且集中声明四张并行计划表：`_tied_weights_keys`（L422）、`_tp_plan`（L423）、`_pp_plan`（L424）、`_fsdp_plan`（L425）——张量/流水/FSDP 并行策略从训练脚本下沉为模型类属性。

## ③ 外部连接

向内：LlamaForSequenceClassification/QuestionAnswering/TokenClassification（L495-502）全部是 `Generic*` 泛型任务头的薄壳——三行类体或纯 `...`，实现在 modeling_layers 的泛型层，这是 2026 版"任务头泛型化"的样板。向外：107 家族经 modular 拍平复制此骨架；注意力后端经 `ALL_ATTENTION_FUNCTIONS.get_interface(self.config._attn_implementation, eager_attention_forward)`（L274-276）运行时分派到 sdpa/flash/flex 等 integrations 注册的实现；`use_kernel_forward_from_hub/use_kernelized_func` 从 integrations 导入（L27）。

## ④ 数据流

一次 decode forward：embed_tokens → 32 层 DecoderLayer（每层 input_layernorm→Attention→residual→post_attention_layernorm→MLP→residual）→ norm → lm_head。position_embeddings 作为 (cos,sin) 元组由模型级 rotary 模块预计算后逐层下发，而非每层自算——省计算也让各层共享同一 RoPE 状态。注意力内：投影→view/transpose 整形→apply_rotary_pos_emb→`past_key_values.update()` 写 Cache（L271）→接口分派→reshape 回 (batch,seq,-1)→o_proj。Cache 更新在 RoPE 之后、注意力之前，保证缓存里存的是已旋转的 KV。

## ⑤ 设计决策与勘误

- **scaling 收口**：`self.scaling = head_dim**-0.5`（L226）作为参数传给 attention_interface 而非藏在各后端里，eager/flash/sdpa 共用同一缩放语义。
- **勘误一**：网传"llama 用 torch.nn.RMSNorm"不实——这里手写 nn.Module 类（L53），与 torch 内置的 nn.RMSNorm 语义等价但实现独立，且必须独立（要挂 hub kernel 装饰器与自定义 extra_repr）。
- **勘误二**："llama 不支持序列分类"是旧闻——L495 起三个任务头经泛型层直接可用，只是类体短到容易被搜索忽略。
- **勘误三**：`_tp_plan` 等四表是类级声明，不等于自动并行——消费方（accelerate/FSDP 插件）读取它们，模型本体只负责"声明意图"。
- eager 后端 softmax 的 float32 显式转换（L205）常被读代码的人当成冗余删掉，删了低精度训练就会静默溢出。

## ⑥ 新人提示

读新模型先 diff 它与 llama 的 modular 差（如 `qwen2/modular_qwen2.py` 只有十几行实质差异）；调数值问题先看 RMSNorm 与 softmax 两处 float32 上提是否被 custom kernel 绕过；想加新注意力后端，实现签名对齐 eager_attention_forward 的 (module,q,k,v,mask,scaling,dropout,**kwargs) 即可注册进 ALL_ATTENTION_FUNCTIONS。改 llama 骨架 = 改百余家族，PR 必须跑全量 slow 测试。
