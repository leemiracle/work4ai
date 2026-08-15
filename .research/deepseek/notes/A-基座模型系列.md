# DeepSeek 基座模型系列六仓研究笔记（V1 / V2 / V3 / V3.2 / MoE / R1）

> 研究型代码考古笔记。基础目录：`C:\workspace\work4ai\.tools\deepseek-repos\`。
> 诚实约束：所有数字均来自本仓库实际读到的文件（README / config JSON / model.py / kernel.py / finetune.py）。仓库内 PDF 技术报告（V2/MoE/V3.2/R1）无法直接解析，相关未读内容明确标注"未读到"，不做编造。

---

## 0. 六仓总览

| 仓库 | 发布 | 一句话定位 | 仓库内实际内容 |
|---|---|---|---|
| DeepSeek-LLM | 2023-11 | V1 稠密基座，LLaMA 架构 + 数据/训练策略贡献 | README + 评测数据，无模型源码 |
| DeepSeek-MoE | 2024-01 | MoE 先导研究：细粒度专家分割 + 共享专家隔离 | README + DeepSpeed 微调脚本 |
| DeepSeek-V2 | 2024-05 | MLA + 细粒度 MoE 首次量产：236B/21B | README + PDF（模型代码在 HF） |
| DeepSeek-V3 | 2024-12 | 671B/37B，aux-loss-free 负载均衡 + MTP + FP8 训练 | README + README_WEIGHTS + 完整推理源码（model.py/kernel.py/configs） |
| DeepSeek-V3.2-Exp | 2025-09 | DSA（DeepSeek Sparse Attention）实验版 | README + 推理源码（Indexer + TileLang kernels） |
| DeepSeek-R1 | 2025-01 | 纯 RL 激励推理能力 + 蒸馏家族 | README（训练管线在 PDF，未读到） |

---

## 1. DeepSeek-LLM（V1 基座，2023-11）

### 1.1 定位一句话
DeepSeek 第一代从零训练的稠密 LLaMA 式基座（7B/67B），核心贡献在数据管线与"长程主义"缩放策略，而非架构。

### 1.2 核心机制与数字（来源：`DeepSeek-LLM/README.md`）
- **架构**：自回归 Transformer decoder，与 LLaMA 相同。7B 用 MHA，67B 用 GQA（README §4 Pre-Training）。上下文 4096。
- **训练数据**：2T tokens（英文+中文），组成：互联网文本、数学、代码、书籍 + 遵守 robots.txt 的自采集数据。
- **数据管线**："cc_cleaner"（分布式、频繁 checkpoint 的批处理系统）；MinhashLSH 做文档级+字符串级去重；启发式规则+模型双重过滤；"确定性随机化"（deterministic randomization）允许训练全程持续改进数据。
- **超参**（README 原文数字）：
  - 7B：batch size 2304，lr 4.2e-4
  - 67B：batch size 4608，lr 3.2e-4
  - AdamW；多步学习率调度：2000 步 warmup，1.6T tokens 时降到峰值 31.6%，1.8T tokens 时降到 10%
- **Tokenizer**：HuggingFace Byte-level BPE + 定制 pre-tokenizer（非 SentencePiece）；为此向 llama.cpp 提 PR#4070 支持全部 HF pre-tokenizer。
- **关键评测**：67B Base MMLU 71.3 / GSM8K 63.4 / HumanEval 显性 42.7；67B Chat GSM8K 84.1、HumanEval 73.8、匈牙利高考 65 分。
- **诚实实验（对 work4ai 极有价值）**：加入 2000 万中文多选题（+MC）后 MMLU 49.4→60.9、C-Eval 47.0→71.3，但**不提升非 MC 式知识评测** → 团队明确决定不在预训练/微调中使用 MC 数据以防 benchmark 过拟合（README §3 "Revisit Multi-Choice Question Benchmarks"）。
- **中间 checkpoint**：通过 AWS S3（request-payer）开放 7B/67B 全程中间检查点——缩放研究的一手材料。

### 1.3 工程亮点
- 显存画像表（README §6）：7B 单卡 A100-40G（bs=1/4096 序列 21.25GB）；67B 需 8×A100-40G。
- vLLM tp_size=4 示例；GGUF/GPTQ 量化路径说明。
- 中间 checkpoint 开放是为支持"更广泛研究"——训练动态可复现。

### 1.4 演进关系
纯稠密、标准注意力，KV cache 无优化 → 67B 推理成本高企，直接催生 V2 的 MLA（KV cache 压缩 93.3%）与 MoE 化。

### 1.5 work4ai 输入
- **讲透LLM / 讲透模型**：2T token、batch/lr 数字与多步调度是"缩放长程主义"的具体样本；+MC 实验是"benchmark 过拟合"最佳教学案例。
- **讲透微调**：7B/67B Chat 的 SFT 提升（GSM8K 17.4→62.6 @7B）可作为 SFT 威力基准。
- **Karpathy经典代码精读**：仓库本身无源码，但 HF tokenizer 的 BPE 实现是配套阅读材料。

---

## 2. DeepSeek-MoE（MoE 先导研究，2024-01）

### 2.1 定位一句话
用 16.4B 参数验证"细粒度专家分割 + 共享专家隔离"两大 MoE 设计原则，以 ~40% 计算量匹配 DeepSeek 7B / LLaMA2 7B。

### 2.2 核心机制与数字（来源：`DeepSeek-MoE/README.md`、`finetune/finetune.py`）
- **两大策略**（README §1 原文）：fine-grained expert segmentation（细分专家，更多小专家+更多激活组合）与 shared experts isolation（隔离共享专家，沉淀公共知识，减少路由专家冗余）。
- **数字**：16.4B 总参，2T 中英 token 从零训练，单张 40GB GPU 可部署（无量化）；计算量约为 DeepSeek 7B 的 40.5%、LLaMA2 7B 的 39.6%（README §2 两张评测图）。
- **模型源码位置**：`modeling_deepseek.py` 在 HuggingFace 模型仓库（README 给出链接），本 git 仓库**不含**模型定义——专家数/top-k 具体值本仓库未读到（论文 PDF 无法解析，此处不编造；V2-Lite 的 64 experts/top-6/2 shared 配置见 §3，属后续验证版）。
- **微调脚本**（`finetune/finetune.py`，322 行）：
  - DeepSpeed ZeRO-3 全参（8×A100-40G，per_device_bs=16，grad_accum=4，lr 2e-5，cosine，warmup 10 步，flash_attention_2）
  - 或 QLoRA 路线：`bits=4` + nf4 + double_quant，ZeRO-2 no-offload，单卡 A100-80G 可跑，lora_rank 8 / alpha 32 / dropout 0.1，trainable 默认 `q_proj,v_proj,k_proj,o_proj,gate_proj,down_proj,up_proj`
- **提示模板**：与 V1 相同的 User/Assistant + `<｜end▁of▁sentence｜>` 特殊 token；SFT 数据格式 instruction/output（Open-Platypus 式）。

### 2.3 工程亮点
- 微调脚本把"全参 ZeRO-3"与"4bit QLoRA"两条路径写清并在 README 给出完整命令行——MoE 微调的工程参考实现。
- 数据格式/tokenize 函数（`_tokenize_fn`，IGNORE_INDEX=-100 掩蔽）是标准 SFT 教学样板。

### 2.4 演进关系
设计原则 → V2 全尺寸验证（160 专家）→ V3 定稿（256 专家 + sigmoid 路由）。是"研究先行、产品跟进"两步走范式的第一步。

### 2.5 work4ai 输入
- **讲透模型 / 讲透LLM**："40% 计算量 ≈ 稠密 7B"是 MoE 经济性的第一手数字。
- **讲透微调**：QLoRA on MoE 的完整可复刻命令（nf4/double_quant/ZeRO-2）。
- **讲透泛化**：共享专家 = 知识的"公共基底"，路由专家 = 特化，可作为模块化泛化的案例。

---

## 3. DeepSeek-V2（MLA + 细粒度 MoE，2024-05）

### 3.1 定位一句话
236B 总参/21B 激活的 MoE，首次把 MLA（KV cache 低秩压缩）与 DeepSeekMoE 组合进量产模型，实现"更强、更省、更快"。

### 3.2 核心机制与数字
（来源：`DeepSeek-V2/README.md`；模型精确配置来自 `DeepSeek-V3/inference/configs/config_236B.json` 与 `config_16B.json`——V3 仓库为 V2 236B/V2-Lite 16B 附带了推理配置。V2 技术报告 PDF 在仓库内但未解析。）

**README 层面数字**：
- 236B 总参 / 21B 激活，上下文 128K；V2-Lite：16B/2.4B，32K。
- 预训练 8.1T tokens；后训练 SFT + RL（Chat-RL 版）。
- 对比 V1 67B：**训练成本省 42.5%、KV cache 减少 93.3%、最大生成吞吐 5.76×**（README §1，三张对比图）。
- 评测：Base MMLU 78.5 vs V1 71.3；Chat(RL) HumanEval 81.1、GSM8K 92.2、AlignBench 7.91 超 gpt-4-0613 的 7.53。
- NIAH 128K 全绿。

**精确架构数字（config_236B.json，V2 236B）**：
```
dim 5120, n_layers 60（其中 1 层 dense FFN，59 层 MoE）, n_heads 128
vocab 102400, inter_dim 12288（dense FFN）, moe_inter_dim 1536
n_routed_experts 160, n_shared_experts 2, n_activated_experts 6（top-6）
n_expert_groups 8, n_limited_groups 3（节点阈值路由：8 组中选 3 组）
route_scale 16.0, score_func 未写 → 默认 softmax（见 V3 model.py:72 默认值）
MLA: q_lora_rank 1536, kv_lora_rank 512, qk_nope_head_dim 128, qk_rope_head_dim 64, v_head_dim 128
```
**V2-Lite（config_16B.json）**：dim 2048, 27 层(1 dense), 16 heads, 64 experts, 2 shared, top-6, **q_lora_rank=0**（Lite 去掉 Q 侧低秩以省参数）, kv_lora_rank 512。

**MLA 机制**（结构由 V3 `inference/model.py` 的 `MLA` 类实现，V2 同构；KV cache 吸收的数学在 V2 论文，仓库内未读到，以下按可读代码描述）：
- `wkv_a`: dim → (kv_lora_rank 512 + qk_rope_head_dim 64)，即每 token 只缓存 512 维潜在向量 + 64 维 rope key（576 维/token/层），而非 MHA 的 (128+128)×128 heads。
- `kv_norm`(RMSNorm) 后由 `wkv_b`: 512 → 128 heads × (128 nope-k + 128 v) 上投影。
- 解码路径（model.py `attn_impl="absorb"` 分支）：**把 wkv_b 权重吸收进 query**（`q_nope · wkv_b` 直接对 kv_cache 潜在向量打分，einsum "bshc,btc"），softmax 后再与 wkv_b 的 V 段相乘还原——矩阵乘法结合律换序，避免解码时重展开 K/V。
- rope 部分（k_pe）单独缓存（pe_cache），因为 RoPE 与潜在投影不可交换——解耦式位置编码是 MLA 成立的关键。

### 3.3 工程亮点
- BF16 推理需 8×80GB；HF `device_map="sequential"` + `max_memory`（不能 auto）。
- SGLang 推荐：MLA 优化、FP8(W8A8)、FP8 KV cache、Torch Compile（README §8）；vLLM 需并 PR#4650。
- Lite 版（16B/2.4B）作为 MLA+MoE 的研究入口，单机可跑。

### 3.4 演进关系
解决 V1 两大瓶颈：KV cache 随序列线性膨胀（MLA：-93.3%）与稠密 FLOPs（MoE：21B 激活）。遗留问题：auxiliary-loss 负载均衡干扰梯度、softmax 路由的专家专业化受限 → V3 解决。

### 3.5 work4ai 输入
- **讲透KV Cache**（核心）：MLA 是 KV cache 压缩的教科书案例——576 vs (128+128)×128 维/token，93.3% 压缩率、投影矩阵吸收技巧、解耦 RoPE。
- **讲透Transformer**：低秩 KV 联合压缩 = MQA/GQA 之后的第三条路线。
- **讲透分布式AI系统**：8 组选 3 的 group 路由即"节点内约束"，跨节点负载的雏形。
- **讲透上下文缓存**：128K NIAH 全绿 + KV 压缩是长上下文服务的前提。

---

## 4. DeepSeek-V3（671B MoE，2024-12）

### 4.1 定位一句话
671B/37B 激活的集大成基座：MLA + DeepSeekMoE 定稿 + aux-loss-free 负载均衡 + MTP 训练目标 + FP8 大规模训练，14.8T token 仅耗 2.788M H800 GPU 小时。

### 4.2 核心机制与数字
（来源：`README.md`、`README_WEIGHTS.md`、`inference/model.py`、`inference/kernel.py`、`inference/configs/config_671B.json`）

**精确架构（config_671B.json）**：
```
dim 7168, n_layers 61（前 3 层 dense FFN，58 层 MoE）, n_heads 128, vocab 129280
inter_dim 18432, moe_inter_dim 2048
n_routed_experts 256, n_shared_experts 1, n_activated_experts 8
n_expert_groups 8, n_limited_groups 4, route_scale 2.5
score_func sigmoid, dtype fp8
MLA: q_lora_rank 1536, kv_lora_rank 512, qk_nope 128, qk_rope 64, v_head 128
```

**训练数字（README）**：14.8T tokens；预训练 2.664M H800 GPU 小时 + 后训练 ~0.1M = 2.788M 总计；**全程无不可恢复 loss spike、无回滚**。HF 权重总量 685B = 671B 主干 + 14B MTP 模块（README §3 Note）。

**Auxiliary-loss-free 负载均衡**（`inference/model.py` `Gate` 类，L535-598）——本轮最重要的可读实现：
```python
self.bias = nn.Parameter(...) if self.dim == 7168 else None   # L564：仅 V3 尺寸创建
scores = scores.sigmoid(); original_scores = scores
if self.bias is not None: scores = scores + self.bias          # bias 只进选择
...
indices = torch.topk(scores, self.topk)[1]                     # 用 bias 后的分数选专家
weights = original_scores.gather(1, indices)                   # 权重取 bias 前的原始分
```
bias 是**仅用于 top-k 选择的每专家偏置**（不参与梯度、不影响路由权重数值），负载偏低时步进上调、均衡后回调（γ 更新规则在论文，仓库内未读到）。对比：V2 的 236B config 无 bias 字段——auxiliary-loss-free 是 V3 新增。此外保留了序列级组约束（`n_expert_groups=8, n_limited_groups=4`：组分数取 top-2 之和再选 4 组，L695-703），无 auxiliary loss 版本用 `amax` 组分（L698）。
sigmoid 路由 + `route_scale 2.5`（选 8 专家归一化后乘 2.5 补偿），shared_experts 用 `MLP(dim, n_shared*moe_inter_dim)` 实现（L667）。

**MTP 多 token 预测**（`README_WEIGHTS.md`）：
- 开源权重含 **1 个 MTP 模块**（`num_nextn_predict_layers=1`），独立参数 **11.5B**、激活 2.4B。
- 结构：共享主干 Embedding 与输出 Head；`enorm`/`hnorm`（两个 RMSNorm）+ `eh_proj`（norm 结果降维拼接投影）+ 一层完整 Transformer 层（`model.layers.61`）。
- 用途：训练时多 token 目标（主 loss + MTP loss 权重 λ，具体值在论文未读到）；推理时作 speculative decoding（README §2：可用于推理加速）。
- 加载规则：MTP 层号紧接主干 61 层之后（L55-57）。

**FP8 混合精度**（`kernel.py` + README_WEIGHTS）：
- 权重 `e4m3`，**128×128 block 缩放**（`weight_block_size: [128,128]`），`weight_scale_inv` float32 存储；激活 dynamic 量化，粒度 per-token-per-128-channel（README_WEIGHTS §FP8）。
- `act_quant`（kernel.py L38-57）：128 一组取 amax，clamp 1e-4，scale=amax/448（e4m3 最大值 448）。
- `fp8_gemm`：Triton autotune（BLOCK_M {16,32,64} × BLOCK_N {32,64,128} × stages {3..6}）。
- 官方只发 FP8 权重，`fp8_cast_bf16.py` 提供转换。

**后训练**：从 R1 系列某模型做长 CoT 蒸馏，"验证/反思模式并入 V3，同时控制输出风格与长度"（README §2 Post-Training）。

**评测**：Base MMLU 87.1 超 LLaMA3.1-405B 的 84.4；Chat AIME24 39.2、MATH-500 90.2、Codeforces 百分位 51.6、Arena-Hard 85.5、AlpacaEval2.0 LC 70.0。

### 4.3 工程亮点
- **跨节点 MoE 通信瓶颈**：算法-框架-硬件协同设计，"几乎完全计算通信重叠"（README §2；对应开源 DualPipe 仓库，不在本六仓内）。
- 推理 demo：`torchrun --nnodes 2 --nproc-per-node 8`，`convert.py --n-experts 256 --model-parallel 16`——16 卡 EP/TP 混合的参考。
- `model.py` 中的并行原语可直接教学：`ParallelEmbedding`（词表切分+all_reduce）、`ColumnParallelLinear`/`RowParallelLinear`、MoE 按 `experts_start_idx..end_idx` 分片 + `dist.all_reduce`（L684-692）。
- 生态矩阵：SGLang（DP Attention、FP8、多节点 TP）、vLLM（TP+PP）、LMDeploy、TRT-LLM、LightLLM（PD 分离在 V2 已有、V3 开发中——README §6.6）、AMD/昇腾 Day-1 适配。

### 4.4 演进关系
| V2 痛点 | V3 对策 |
|---|---|
| aux loss 负载均衡损害性能 | bias-only 路由偏置（aux-loss-free）|
| 21B 激活 / 160 专家 | 37B 激活 / 256 专家 + 1 shared（更专）|
| softmax 路由 | sigmoid 路由 + 组约束保留 |
| BF16 训练成本 | FP8 block-wise 训练（首次超大规模验证）|
| 无 MTP | 1 层 MTP（训练增益 + 推测解码）|
| 8.1T tokens | 14.8T tokens，单位成本反而更低 |

### 4.5 work4ai 输入
- **讲透分布式AI系统**（核心仓库）：FP8 128×128 block GEMM kernel、EP 分片循环、通信重叠、2 节点 16 卡部署——`inference/` 三文件就是一套完整教材。
- **讲透KV Cache**：MLA 吸收式的完整 einsum 实现（`attn_impl="absorb"` vs `"naive"` 两分支对照）。
- **讲透模型 / 讲透LLM**：aux-loss-free 负载均衡的"选择与加权解耦"设计——一小段代码改变 MoE 训练范式。
- **讲透GPU系统专栏**：act_quant/fp8_gemm 的 Triton 实现是量化 kernel 精读素材。

---

## 5. DeepSeek-V3.2-Exp（DSA 稀疏注意力，2025-09）

### 5.1 定位一句话
在 V3.1-Terminus 骨架上把 MLA 替换为 DSA（DeepSeek Sparse Attention）的实验版：用 Lightning Indexer 每 token 动态选 top-2048 键，长上下文训练/推理计算大幅下降而性能基本持平。

### 5.2 核心机制与数字
（来源：`README.md`、`inference/model.py`、`inference/kernel.py`、`inference/config_671B_v3.2.json`）

**配置**（config_671B_v3.2.json）：与 V3.1 完全同骨架（dim 7168/61 层/256 专家/top-8/sigmoid/ue8m0 scale），新增：
```
index_n_heads 64, index_head_dim 128, index_topk 2048
```
实验设计：刻意对齐 V3.1 训练配置以隔离 DSA 的净效应（README §Introduction）。评测：MMLU-Pro 85.0 持平、AIME25 89.3（vs 88.4）、HLE 19.8（vs 21.7 略降）、Codeforces 2121（vs 2046）、BrowseComp 40.1（vs 38.5）。

**Lightning Indexer**（`model.py` `Indexer` 类，L435-487）——DSA 核心：
- **查询侧复用 MLA 的 q_lora 压缩**：`wq_b: Linear(q_lora_rank 1536 → 64 heads × 128)` 直接从 MLA 的潜在 query（`qr = q_norm(wq_a(x))`，L560）投影出 indexer query——不重复压缩。
- **键侧**：`wk: Linear(7168 → 128)` + `k_norm`(**LayerNorm**，非 RMSNorm——两种 norm 在同层混用)。head 拆 64 维 rope + 64 维 nope。
- **RoPE 布局陷阱**（README §Update 2025.11.17，重大实现细节）：indexer 的 RoPE 要求**非交错(non-interleaved)**布局，MLA 的 RoPE 是**交错(interleaved)**——此前 demo 写错会掉点。`apply_rotary_emb(..., interleaved=False)`（L464,470）。
- **Hadamard 旋转**：`rotate_activation()`（L428-432，fast_hadamard_transform，scale=hidden^-0.5）在量化前打散 outlier，随后 `act_quant` 到 FP8——indexer 全程 FP8 计算。
- **逐 token 逐头加权**：`weights_proj: Linear(7168 → 64)` fp32，`weights × n_heads^-0.5 × q_scale × softmax_scale` 作为每头权重（L478-479）。
- **打分 kernel**（kernel.py `fp8_index_kernel` L200-251）：
```
logits = k_smem @ q_smem^T            (FP8 GEMM → FP32)
logits = ReLU(logits) × q_s(权重)     (每头 ReLU 激活——非对称打分)
logits_sum = Σ_h logits                (64 头求和)
index_score = logits_sum × k_s(e8m0)
```
ReLU 计分是 DSA"token 选择"的判别函数（每头只累计正相关的键）。
- **Top-k 选择与一致性**：`index_score.topk(min(2048, end_pos))`（L483），然后 `dist.broadcast + assert all equal`（L484-486）——强制所有 TP rank 选出同一 token 集合。
- **Mask 注入**（MLA forward，L582-586 prefill / L599-602 decode）：`torch.full(-inf).scatter_(-1, topk_indices, 0)` 生成 index_mask 加到注意力分数上——**softmax 内的硬稀疏化**，选中的 2048 个键 mask=0、其余 -inf。
- **两种稀疏模式**：仓库代码实现的是 **token 选择（T2T，每 query token 独立选 token）**；块选择（block selection，prefill 阶段 query 块→key token）在论文/高性能 kernel 中（DeepGEMM PR#200、FlashMLA PR#98，README §Open-Source Kernels 指出 paged 版本在那边），本仓库 demo 未含——标注：块选择实现未在本仓库读到。

**其他改动**：
- MLA 的 KV cache 显式模拟 FP8 精度（L569-571 act_quant 再反量化，注释"实际部署用 fp8 kv cache"）。
- 解码路径缓存 `dequant_wkv_b`（L591-592）避免重复反量化。
- RowParallelLinear all_reduce 前升 fp32（L265）、MLP/Expert 在 fp32 域做 SiLU 乘（L643）——数值稳定性细节。
- kernel 从 Triton 换成 **TileLang**（研究可读性优先），启用 ue8m0 指数缩放（`fast_round_scale` = 2^ceil(log2(amax/448))，纯幂次 scale 免除法）。

### 5.3 工程亮点
- SGLang 启动：`--tp 8 --dp 8 --enable-dp-attention`——DSA 与 DP 注意力组合的参考部署（README）。
- kernel 双轨制：TileLang 教学 + DeepGEMM/FlashMLA 生产（README §Open-Source Kernels）。
- `assert torch.all(topk_indices == topk_indices_)` 用 broadcast 校验分布式一致性——防御式工程。

### 5.4 演进关系
MLA 解决"KV 存多大"，DSA 解决"注意力算多少"：计算复杂度从 O(L²) 降到 O(L×2048)。承接 V3.1-Terminus 权重，是"下一代的中间实验步"（README 原文 an intermediate step）。

### 5.5 work4ai 输入
- **讲透Transformer / 讲透上下文缓存**（核心）：DSA 是注意力稀疏化的前沿案例——与滑动窗口/H2O/Quest 等静态或启发式方法对照"学习的索引器"。
- **讲透KV Cache**：indexer 的 k_cache 是**第二个 FP8 KV cache**（128 维/token），"索引缓存 + 潜在缓存"双缓存的内存账。
- **讲透分布式AI系统**：TP 各 rank top-k 一致性问题（broadcast+assert）、Hadamard 旋转消除 FP8 outlier。
- **讲透GPU系统**：fp8_index kernel 精读（ReLU 计分 GEMM、e8m0 scale、TileLang pipelined 双缓冲）。

---

## 6. DeepSeek-R1（RL 推理模型，2025-01）

### 6.1 定位一句话
首个公开验证"纯 RL（无 SFT 冷启动）即可激励 LLM 推理能力"的模型家族：R1-Zero 纯 RL 涌现长 CoT，R1 加冷启动数据修可读性，再用 80 万样本蒸馏出 6 个小模型。

### 6.2 核心机制与数字（来源：`DeepSeek-R1/README.md`；GRPO/奖励细节在 PDF 未读到）
- **基座**：DeepSeek-V3-Base（671B/37B/128K），架构同 V3（README §3）。
- **R1-Zero**：跳过 SFT 直接大规模 RL → 涌现 self-verification、reflection、生成长 CoT；副作用：无尽重复、可读性差、语言混杂（README §1）。
- **R1 管线**：README §2 明确"**两个 RL 阶段 + 两个 SFT 阶段**"（four-stage：冷启动 SFT → 推理 RL → 全场景 SFT → 对齐 RL；各阶段顺序与命名以论文为准，README 只给"2×RL+2×SFT 作为推理与非推理能力的种子"的表述——细粒度流程未在仓库文本中展开）。
- **蒸馏**：用 R1 生成的推理数据微调 Qwen2.5/Qwen2.5-Math/Llama3 系列，共 **1.5B/7B/8B/14B/32B/70B 六个**；Qwen 系用 **800k 样本**（README §7 License 注脚）。
- **蒸馏 > 小模型 RL**：README §2 结论"大模型推理模式蒸馏进小模型，优于在小模型上直接 RL 发现的模式"。
- **评测数字**：R1 AIME24 79.8（o1-1217 79.2）、MATH-500 97.3、MMLU 90.8、Codeforces Rating 2029；Distill-Qwen-32B AIME 72.6 超 o1-mini 63.6、MATH-500 94.3——32B 稠密 SOTA。
- **推理配置**：max 生成 32768 token，temp 0.6 / top-p 0.95，64 采样估 pass@1（README §4）。
- **使用建议**（README §6，工程上很重要）：温度 0.5-0.7（推荐 0.6）防重复循环；**不要加 system prompt**；数学题提示"step by step + \boxed{}"；**强制以 `<think>\n` 开头**防止跳过思考模式。
- 官方 Web 两个生产级 prompt 模板：文件上传模板与中英文搜索引用模板（[citation:X] 格式、引用分散在正文、列举类 ≤10 点、创作类要长）——现网 RAG 提示工程一手材料。
- License：MIT，明确允许蒸馏训练其他 LLM。

### 6.3 工程亮点
- 部署直接复用 V3 栈（vLLM/SGLang）；Distill 模型与 Qwen/Llama 用法一致（`vllm serve ... --tensor-parallel-size 2 --max-model-len 32768 --enforce-eager`）。
- 官方 prompt 模板 = 长上下文引用规范的可抄作业。

### 6.4 演进关系
V3 给了廉价 671B 基座 → R1 证明基座潜力上限由 RL 挖掘 → R1 反哺 V3.1/V3.2（V3 README 后训练即 R1 蒸馏）——**基座↔推理模型互哺闭环**。

### 6.5 work4ai 输入
- **讲透RL**（核心）：R1-Zero 是"RL 激励推理（无 SFT）"的里程碑样本；"蒸馏优于小模型 RL"是 scaling 教训；rule-based reward 细节需引论文（未在仓库读到，注意标注）。
- **讲透泛化**：AIME/MATH/Codeforces 跨域同时上涨 = 推理能力的迁移性证据。
- **讲透微调**：800k 样本蒸馏出 32B 超 o1-mini——SFT 数据质量/来源（teacher 分布）决定上限。
- **讲透LLM**：`<think>` 模式、温度与重复循环的关系、跳过思考的失败模式。

---

## 7. 六仓纵向综合：MLA–MoE–MTP–DSA–RL 五条技术线

### 7.1 演进链总表

| 维度 | V1 (2023-11) | MoE (2024-01) | V2 (2024-05) | V3 (2024-12) | R1 (2025-01) | V3.2 (2025-09) |
|---|---|---|---|---|---|---|
| 注意力 | MHA/GQA | MHA | **MLA** | MLA | MLA | MLA + **DSA** |
| FFN | Dense | 细粒度 MoE | 160 专家/2 共享/top-6 | **256 专家/1 共享/top-8, sigmoid** | 同 V3 | 同 V3 |
| 负载均衡 | — | aux loss（论文，未读到） | aux loss + 组约束 | **aux-loss-free bias + 组约束** | 同 V3 | 同 V3 |
| KV/token/层 | MHA 全量 | MHA 全量 | 576 维（512 潜在+64 rope） | 576 维 | 576 维 | 576 + 128（indexer） |
| 训练精度 | bf16 | bf16 | bf16 | **fp8 e4m3 128×128 block** | — | **+ ue8m0 指数 scale** |
| 训练量 | 2T | 2T | 8.1T | **14.8T** | RL（量未读到） | 对齐 V3.1 |
| 上下文 | 4K | 4K | 128K（Lite 32K） | 128K | 128K | 128K（注意力 O(L×2048)） |
| 参数/激活 | 7B/67B 稠密 | 16.4B/~40% 计算量 | 236B/21B | **671B/37B (+MTP 14B)** | 671B/37B | 671B/37B |
| 成本叙事 | — | 40% 计算量≈7B | 省训练 42.5%/吞吐 5.76× | **2.788M H800 时** | 蒸馏 800k 样本 | 长上下文成本大降 |

### 7.2 五条技术线的演进规律

**MLA 线（注意力存储）**：MHA/GQA → MLA（潜在压缩+吸收）→ MLA+DSA indexer（潜在缓存之上加第二索引缓存）。规律：每代把"每 token 必须存/算什么"压缩一个量级；解耦 RoPE（pe_cache 独立）是低秩压缩成立的不变量；V3.2 甚至把 indexer 的 128 维键也做成 FP8——存储与精度同步降级而质量守恒。

**MoE 线（计算稀疏）**：设计原则（细分+共享隔离）→ 全尺寸验证（160/2/top-6 softmax+aux loss）→ 定稿（256/1/top-8 sigmoid+bias-free）。规律：专家数翻倍、共享专家 2→1（知识更集中沉淀于路由专家）；路由从"softmax+辅助损失"到"sigmoid+仅选择偏置"——**把负载均衡从损失函数里拿出来塞进推理规则里**，训练目标越来越纯。`Gate.forward` 里 `original_scores.gather` 这一行是范式转换的全部代码差异。

**MTP 线（训练目标/解码加速）**：V3 首次引入 1 层 MTP（11.5B 参数，共享 embedding/head，eh_proj 拼接）。一鱼两吃：训练时多 token 监督信号密化，推理时推测解码。V3.1/V3.2 配置继承（config_v3.1/v3.2 同骨架），社区（SGLang issue#2591）跟进部署。

**DSA 线（注意力计算稀疏）**：从"存得少"（MLA）到"算得少"。Lightning Indexer 复用 MLA 的 q_lora 潜在 query（wq_b 直接吃 1536 维 qr），说明**压缩表示成了新模块的接口**——架构内复利。ReLU 计分 + FP8 + Hadamard 防 outlier + top-2048 硬 mask，全链路为硬件成本设计。非交错 vs 交错 RoPE 的 bug（2025.11.17 修正）提示：细节错误的代价是静默掉点。

**RL 线（后训练）**：V2 已有 Chat(RL) 版（GRPO，细节在论文）→ R1-Zero 证明纯 RL 可激励推理 → R1 用冷启动+四阶段修可读性 → 蒸馏反哺 V3/V3.1/V3.2 后训练。规律：**基座效率（MLA/MoE/FP8）降低RL实验成本 → RL 产出推理数据 → 蒸馏回基座**，形成闭环；"大模型 RL + 小模型蒸馏"击败"小模型直接 RL"。

### 7.3 贯穿六仓的工程哲学
1. **以"激活参数/token 成本"为第一设计约束**：40% → 42.5%省 → 2.788M GPU时 → O(L×2048)，每代 README 首屏都是成本对比图。
2. **研究仓先行验证、产品仓定稿**：MoE→V2→V3 三步走，每步都在上一代真机上验证。
3. **推理 demo 即文档**：V3/V3.2 的 `model.py` 用无框架纯 PyTorch 写清 MLA 吸收、MoE 分片、FP8 GEMM、indexer——研究可读性优先（TileLang 注释自述）。
4. **诚实工程**：V1 拒绝 MC 数据刷分；V3 公开"无 spike 无回滚"；V3.2 主动公告 RoPE bug；R1 公开 R1-Zero 的缺陷。
5. **细节即性能**：mscale=0.1·ln(factor)+1 的 YaRN 修正、sigmoid 权重归一×route_scale 2.5、LayerNorm vs RMSNorm 混用、all_reduce 前升 fp32——每个 0.1% 的堆叠。

### 7.4 阅读优先级建议（给 work4ai 内容生产）
1. `DeepSeek-V3/inference/model.py`（808 行，五星级精读对象：MLA+MoE+FP8+并行全图景）
2. `DeepSeek-V3.2-Exp/inference/model.py` 的 `Indexer` 类 + `kernel.py` 的 `fp8_index_kernel`（DSA 唯一公开参考实现）
3. `DeepSeek-V3/README_WEIGHTS.md`（MTP 权重结构与 FP8 量化格式）
4. `DeepSeek-R1/README.md` 的官方 prompt 模板与使用建议（生产级）
5. `DeepSeek-LLM/README.md` 的 +MC 实验（benchmark 诚信案例）

---

*生成于 2026-08-15；基于本地浅克隆 `C:\workspace\work4ai\.tools\deepseek-repos\` 六仓实际文件。未读到的内容（各技术报告 PDF 内的具体训练超参、GRPO 细节、DSA 块选择实现、V2 aux loss 公式、MoE 论文消融）已在文中标注。*
