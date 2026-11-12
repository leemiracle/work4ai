# 09 · MoE 新架构群：细粒度路由、288 专家与 DSA 稀疏注意力

## ① 角色定位

2026 版 transformers 的 models 层最活跃的增量是 MoE（混合专家）家族群：deepseek_v2/v3/v32/v4、qwen3_moe、mistral4、step3p7、kimi_k25、glm4v_moe、minimax_m3_vl……它们共享"路由器 + 专家库 + 可选共享专家"的骨架，但路由数学与注意力配套差异极大——这批文件是观察"同一范式分化"的最佳样本。本篇锚点全部落在具体行号上。

## ② 内部结构

路由器三型：

- **DeepseekV3TopkRouter**（modeling_deepseek_v3.py:131）：`top_k = config.num_experts_per_tok`（L134）、`num_local_experts`（L135，configuration 里 L79 把原始名 `n_routed_experts` 映射过来，默认 256）。核心是 **grouped top-k**：分数先 reshape 成 (token, num_group, experts/num_group)（L150,159）每组选优再全局 top-k（L163），并带 `e_score_correction_bias` Buffer（L142）——aux-loss-free 负载均衡的偏差项直接住在路由器里。默认配置 topk_group=4、每 token 8 专家、norm_topk_prob=True（configuration L99-102）。
- **Qwen3MoeTopKRouter**：标准 softmax-topk 无分组，norm_topk_prob 默认 **False**（configuration_qwen3_moe.py:106）——与 DeepSeek 的 True 相反，归一化语义分家。默认 num_experts=128（L105）、moe_intermediate_size=768（L103）。SparseMoeBlock 在 L270。
- **mistral4 的血统混搭**：modular_mistral4.py:27 直接 `from ..deepseek_v2.modeling_deepseek_v2 import DeepseekV2TopkRouter`——Mistral 第 4 代复用 DeepSeek 路由器；配置 n_routed_experts=128、每 token 4 专家（configuration L84,93）、first_k_dense_replace（L94）：前 N 层保持 dense。

**DeepseekV3Experts**（L173）是批量矩阵实现：`gate_up_proj`/`down_proj` 直接是 3D Parameter (num_experts, dim, dim)（L181-182），forward 用 one_hot expert_mask（L193）按专家 gather token 计算——无 loop 的稠密批处理。**step3p7** 是规模极值：n_routed_experts=**288**（configuration_step3p7.py:172，docstring L85）、每 token 8 专家、moe_intermediate_size=1280、外加 share_expert_dim=1280 共享专家旁路（L173）与 num_sliding_attention_heads 滑窗头（L175）。**kimi_k25** 是血统化石：modular_kimi_k25.py:45,249,632 显示 VisionRotaryEmbedding 与 ForConditionalGeneration 全部直接继承 Glm4v——K2.5 多模态与 GLM-4.5V 同构在源码层面坐实。

## ③ 外部连接

modular 继承网：qwen3_moe = llama（modular L24）+ mixtral（L30）+ qwen2_moe 的 DecoderLayer/Experts/MLP/Router 四件套（L36）+ qwen3 的 Attention（L37），L44 注释一锤定音"This is the main diff with qwen2Moe!"——QK-norm 注意力是唯一实质差异。mistral4 = deepseek_v2 路由器 + deepseek_v3 专家 + llama 骨架。下游接口上，MoE 模型普遍输出 `MoeCausalLMOutputWithPast`（modular_qwen3_moe.py:20 import），把 router_logits 一并吐给训练侧算 aux loss（或不算）。

## ④ 数据流

以 deepseek_v3 一层为例：hidden → RMSNorm → 路由器 softmax+sigmoid+bias 修正 → grouped top-k 选出 8 专家与权重 → 归一化(norm_topk_prob) → Experts.forward 按 one_hot 分桶并行算 8 份 expert(x) 加权求和 →（可选共享专家旁路相加）→ 残差。v32 在每层注意力前再插 **DeepseekV32Indexer**（modeling_deepseek_v32.py:160）：自带 wq_b/wk 轻投影（docstring L163-166 言明与主 MLA 分离），scores 经 ReLU（L241）→weights_proj 头加权（L244）→因果掩码（L248-251）→`topk(min(index_topk, seq_len))`（L253）输出加性稀疏掩码（选中 0、未选 -inf），index_topk 默认 **2048**（configuration L120，docstring L34）——DSA"先索引后注意力"在库内的完整落地。

## ⑤ 设计决策与勘误

- **路由器内嵌均衡**是 deepseek 系的分水岭：e_score_correction_bias 让推理期也能做均衡偏置，无需训练期 aux loss 梯度——但 bias 是 Buffer 不是 Parameter（L142），预训练框架外不可学习。
- **勘误一**：网传"transformers 的 MoE 都是 Mixtral 风格"。实测 mistral4 反向 import DeepseekV2TopkRouter，DeepSeek 才是路由数学的输出方。
- **勘误二**："qwen3_moe 与 deepseek_v3 路由等价"不成立：无分组、无 bias、norm_topk_prob 反向默认。
- **勘误三**：288 专家不是 step3p7 全部——share_expert_dim 共享专家（configuration L173）常被漏数，严格说是 288 路由 + 1 共享。
- v32 Indexer 的 top-k **索引本身不外露**（docstring L166-169：只散射进掩码）——想拿索引做可视化的人会扑空。
- Experts 用 3D Parameter 而非 ModuleList：换来了批量 gather 的吞吐，代价是 per-expert 量化/剪枝工具链要特殊适配。

## ⑥ 新人提示

读 MoE 模型先读 configuration 的三个数（专家数/每 token 数/是否归一化）再看 router 类名——名字即流派（TopkRouter=deepseek 系、SparseMoeBlock=qwen 系）。debug 输出 NaN 先查 norm_topk_prob 与 bias 修正的组合。新加 MoE 家族优先 modular 继承 qwen2_moe 四件套或 deepseek_v3 全家，别手写路由。做 v32 类稀疏注意力时记住 indexer 掩码路径与 KV cache 的交互（update_indexer 在 DynamicIndexedLayer 上，modeling L170-172）——缓存类型选错稀疏性就静默失效。
