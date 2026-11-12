# DeepSeek-V3.2-Exp 精读：DSA 稀疏注意力与高效推理架构

> 论文：*DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models*，arXiv:2512.02556（2025-12-02，DeepSeek-AI）
> 仓内另附 V3.2-Exp 阶段报告：`DeepSeek_V3_2.pdf`；本地仓：`~/ai/explore/deepseek-ai/DeepSeek-V3.2-Exp`

## 0. 论文核实说明（任务要求）

README 本身无 arXiv 链接（引用块只是 misc tech report）。经检索核实：**DeepSeek-V3.2 技术报告 = arXiv:2512.02556**，且论文明言 *"DeepSeek-V3.2 uses exactly the same architecture as DeepSeek-V3.2-Exp"*——V3.2 只是同一架构在更多 post-training 算力下的完整版，因此解读本仓（V3.2-Exp）以 2512.02556 为论文主体、仓内 V3.2-Exp 发布说明（2025-09-29）为补充，完全成立。

关于任务提到的 **DeepThink**：它不是论文里的模块名，而是 DeepSeek API 层对 reasoning/thinking 模式的产品命名（对应模型侧 thinking vs non-thinking 双模式）。V3.2-Exp 上线时 API 同步开启 DeepThink 模式；在技术报告里对应的是 §3.2 "Thinking in Tool-Use"（把思维链引入工具调用）与 thinking 模式评测行。本仓真正的技术核心是 **DSA（DeepSeek Sparse Attention）**。

## 1. 一句话定位

DeepSeek-V3.2-Exp 是通往下一代架构的中间实验步：在 V3.1-Terminus（671B MoE，128K 上下文已扩展）之上，通过**继续训练**引入首个"可训练的细粒度稀疏注意力"DSA——用一个小型 lightning indexer 为每个 query 挑 top-2048 个 token 做注意力，把核心注意力复杂度从 O(L²) 降到 O(Lk)，而 benchmark 性能与稠密版打平；完整版 V3.2 再叠加规模化 RL 与大规模 agent 任务合成，对标 GPT-5，其高算力变体 Speciale 在 IMO/IOI 2025 拿金牌。

## 2. 动机与痛点

论文诊断开源模型落后闭源的三个结构性缺陷：

1. **架构**：vanilla attention 的 O(L²) 使长序列训练与推理都昂贵——既挡部署，也挡长上下文 RL（post-training 需要大量长轨迹）。
2. **资源分配**：开源界 post-training 算力投入普遍不足，难题上不去。
3. **Agent 能力**：开源模型在工具使用的泛化与指令遵循上与闭源差距明显。

此前稀疏注意力（NSA、Quest、SlashAttention 等）多为**推理时**加速、top-k 由启发式决定，无法用于训练。DSA 的关键主张：**选择哪些 token 本身用一个可学习的小网络（indexer）在训练中学出来**，且与 MLA 兼容、可从已有稠密 checkpoint 继续训练热启动。

## 3. 核心方法

### 3.1 DSA 原型：lightning indexer + 细粒度 token 选择

**Lightning indexer** 计算位置 t 的 query 与每个前文位置 s 的 index score：

$$I_{t,s} = \sum_{j=1}^{H^I} w^I_{t,j} \cdot \mathrm{ReLU}\left(\mathbf{q}^I_{t,j} \cdot \mathbf{k}^I_s\right)$$

- 头数 H^I 少（部署版 64 头、head_dim 128，远小于主模型 128 头×192 维），q/k 各一个低维投影，标量权重 w_t,j 由 query 状态动态产生（对头加权求和）；
- 激活选 **ReLU 而非 softmax**：纯为 kernel 吞吐（无归一化的逐元素运算可完美 FP8 化）。

**细粒度选择**：每个 query 仅取 index score 的 **top-k=2048** 个 key-value 条目做 MLA 注意力：

$$\mathbf{u}_t = \mathrm{Attn}\left(\mathbf{h}_t, \{\mathbf{c}_s \mid I_{t,s} \in \text{Top-k}(I_{t,:})\}\right)$$

注意粒度是"每 query 各自挑 token"（fine-grained），而非分块级（coarse）稀疏——这是"首次"声称的落点。

### 3.2 在 MLA 下实例化（MQA 模式）

kernel 层面要求每个 KV 条目能被多个 query 复用，因此 DSA 挂在 MLA 的 **MQA 模式**上：每个 token 压缩成一个 latent 向量 c_s（kv_lora_rank=512），被该 query 的全部 128 个头共享。indexer 则另存一份自己的小 key 缓存（128 维/每 token，FP8）。复杂度：主注意力 O(L²)→O(Lk)；indexer 虽仍是 O(L²)，但其每 token 计算量相对 MLA 低一个量级，配合 FP8 与专用 kernel 后整体端到端显著加速。

### 3.3 两阶段继续预训练（从 V3.1-Terminus 热启动）

两阶段训练数据分布与 V3.1-Terminus 的 128K 长上下文扩展数据**完全对齐**（这是"严格对照"的实验设计）。

**阶段一 Dense Warm-up**（只训 indexer）：保持稠密注意力，冻结除 indexer 外全部参数。把主注意力分数按头求和、沿序列 L1 归一化得到目标分布 p_{t,:}，用 KL 损失教 indexer 模仿：

$$\mathcal{L}^I = \sum_t \mathbb{D}_{KL}\left(p_{t,:} \,\|\, \mathrm{Softmax}(I_{t,:})\right)$$

lr 1e-3，仅 1000 步 × 16 条 × 128K = 2.1B tokens。

**阶段二 Sparse Training**（全参数）：启用 top-k 选择，全模型自适应稀疏模式。KL 对齐只在被选集合 S_t 上计算，且 **indexer 的输入从计算图 detach**——indexer 只吃 KL 损失、主模型只吃语言建模损失，互不污染梯度。lr 7.3e-6，15000 步 × 480 条 × 128K = **943.7B tokens**。

### 3.4 推理成本

H800 实测（$2/GPU·h 计价）：prefill 与 decode 的每 token 成本随位置增长的曲线大幅压平（仓内 `cost.jpg`）。短序列 prefill 特殊处理：用 **masked MHA 模式模拟 DSA**（把 top-k 做成加性 mask），因为短上下文下这比真正 gather 稀疏 KV 更快——同一模块两副 kernel 面孔。

### 3.5 规模化后训练（V3.2 完整版）

- **Specialist Distillation**：从同一 base 各训 6 个领域专家（数学/编程/通用推理/通用 agent/agentic coding/agentic search，均含 thinking 与 non-thinking 两模式）+ 写作与通用 QA，各吃大规模 RL；再由专家产出领域数据蒸馏出最终 checkpoint；蒸馏模型与专家的差距由后续 RL 抹平。
- **Mixed RL（GRPO 单阶段）**：推理+agent+人类对齐合并在一个 RL 阶段，避免多阶段灾难遗忘。奖励：可验证任务用 rule-based outcome reward + length penalty + 语言一致性奖励；通用任务用 generative reward model（每 prompt 自带 rubric）。
- **GRPO 稳定化四件套**（scaling RL 的工程核心）：
  1. *Unbiased KL Estimate*：修正 K3 估计量，用 π_θ/π_old 重要性比加权，梯度无偏——原 K3 在 π_θ≪π_ref 时会给低概率 token 无界权重，噪声累积导致崩坏；数学域甚至可以免去 KL。
  2. *Off-Policy Sequence Masking*：大 batch rollout 拆多 mini-batch 必然 off-policy，训练/推理框架实现差异又加剧；对"负优势 且 序列 KL>δ"的样本置零 mask（只 mask 负样本——从自己的错误学最有价值，强 off-policy 的负样本则有毒）。
  3. *Keep Routing*：MoE 在推理框架采样时的专家路由路径原样带回训练侧强制复用，消除路由不一致导致的参数子空间跳变（自 V3-0324 起标配）。
  4. *Keep Sampling Mask*：top-p/top-k 截断 mask 从采样侧保留到训练侧，保证 π_old 与 π_θ 动作子空间一致。
- **Thinking in Tool-Use**：上下文管理规则——只有新 user 消息到来才丢弃历史 reasoning，纯工具消息（tool output）追加时保留完整思维链，避免每次工具调用都从头重想（R1 做法的 token 浪费）；Roo Code/Terminus 等用 user 消息模拟工具的框架享受不到该优化，官方建议此类框架用 non-thinking 模式。
- **大规模 agent 任务合成**（四类，共 ~8.5 万 prompt / 1827 环境）：
  - code agent 24,667：挖 GitHub issue-PR 对，环境构建 agent 自动装依赖跑测试，要求 gold patch 使 F2P>0 且 P2F=0 才收录，覆盖 8 种语言；
  - search agent 50,275：多 agent 流水线（问题构造→异构候选生成→带搜索的验证 agent 多轮核验），只留"真值对、候选全错"的样本；
  - general agent 4,417：环境合成 agent 自举 ⟨environment, tools, task, verifier⟩ 四元组，解函数只准走工具接口、解必须过验证函数，迭代加难度（论文给的三日杭州行程规划示例很直观：解难验易）；
  - code interpreter 5,908：Jupyter notebook 数学/逻辑/数据科学题。
- **V3.2-Speciale**：只喂推理数据、放宽长度惩罚、并入 DeepSeekMath-V2 的数据与奖励（数学证明）的高算力变体。

## 4. 实验与结果

**V3.2-Exp vs V3.1-Terminus 平价验证**（README 表，训练配置刻意对齐）：MMLU-Pro 85.0/85.0，AIME 2025 88.4→89.3，Codeforces 2046→2121，HLE 21.7→19.8（略降），BrowseComp 38.5→40.1，SWE-V 68.4→67.8——结论"稀疏化零显著回退"。第三方长上下文评测反而更强：AA-LCR reasoning 模式 +4 分、Fiction.liveBench 多指标领先。ChatbotArena Elo 持平（两者 post-training 相同）。

**V3.2 主结果**（thinking 模式，128K 上下文，温度 1.0）：

| | GPT-5-High | Gemini-3.0-Pro | Kimi-K2-Thinking | V3.2 |
|---|---|---|---|---|
| MMLU-Pro | 87.5 | **90.1** | 84.6 | 85.0 |
| HLE | 26.3 | **37.7** | 23.9 | 25.1 |
| AIME 2025 | 94.6 | **95.0** | 94.5 | 93.1 |
| SWE Verified | **77.2** | 76.2 | 71.3 | 73.1 |
| SWE Multilingual | 68.0 | – | 61.1 | **70.2** |
| BrowseComp | 54.9 | – | 60.2* | 51.4/67.6*（上下文管理） |
| Terminal Bench 2.0 | 42.8 | **54.2** | 35.7 | 46.4 |

开源阵营里对 Kimi-K2-Thinking 多数领先、agent 侧（SWE 多语、T-Bench、Tool-Decathlon 35.2 vs GPT-5 的 29.0）尤其亮眼；整体定位"对标 GPT-5-high、逊于 Gemini-3.0-Pro、成本显著更低"。

**Speciale**：AIME 96.0 / HMMT-Feb 99.2 / HMMT-Nov 94.4 / IMOAnswerBench 84.5（括号内输出 token 数显示它靠"想更长"换分，45k tokens/题）；**IOI 2025 与 IMO 2025 双金牌**、ICPC WF 2025 与 CMO 2025 金牌水平——开源模型首次在两大奥赛同时金牌。

## 5. 局限与后续

论文自认三条：① 预训练总 FLOPs 少于闭源前沿，世界知识广度仍落后；② token 效率差——要生成更长轨迹才追平 Gemini-3.0-Pro 输出质量（Speciale 尤甚），未来要提高"推理链智能密度"；③ 复杂任务求解仍逊 frontier。工程侧：DSA 的 indexer 本身仍 O(L²)、top-k 固定 2048 不随序列长度自适应；masked-MHA 短序列路径说明稀疏收益有最小序列长度门槛。后续即 Engram 论文所探索的"条件记忆"新稀疏轴与下一代架构。

## 6. 与代码的对照（本仓 `inference/` 为官方参考实现）

| 论文概念 | 代码位置（`inference/`） |
|---|---|
| lightning indexer 公式 (1) | `model.py::Indexer`：`wq_b: Linear(1536→64×128)`（q 从 MLA 的 query latent 投影）、`wk: Linear(7168→128)+k_norm(LayerNorm)`（共享 key，MQA 式）、`weights_proj: Linear(7168→64)` **fp32**（对应 w_t,j）、`softmax_scale=head_dim^-0.5` |
| ReLU 激活 + FP8 | `rotate_activation()`（Hadamard 正交旋转，保内积不变的下精度技巧）→ `act_quant` FP8 量化；`k_cache` 直接是 `float8_e4m3fn` + 分块 `k_scale_cache`；打分 kernel `kernel.py::fp8_index`（TileLang JIT） |
| top-k=2048 选择 | `Indexer.forward` 末尾 `index_score.topk(min(index_topk, end_pos))`，随后 `dist.broadcast + assert` 强校验 TP 各 rank 选出的集合一致（稀疏路径对并行一致性极其敏感的实证） |
| indexer RoPE 布局勘误（2025.11.17） | `model.py:463/469` 两处注释 `# rope in indexer is not interleaved`——indexer 用 non-interleaved，MLA 用 interleaved；早期版本写错导致性能退化，README Update 节公告（论文附录未载，代码考古点） |
| 公式 (2) 稀疏注意力 | `MLA.forward` 两条路径：MHA prefill（`index_mask.scatter_(-1, topk, 0)` 生成 -inf/0 加性 mask 叠上 scores，即"masked MHA 模拟 DSA"）与 MQA decode（latent cache 上的 KV 收集 + mask） |
| MLA/MoE 主干超参 | `config_671B_v3.2.json`：61 层、dim 7168、128 头、256+1 专家 top-8、kv_lora_rank 512、`index_n_heads:64 / index_head_dim:128 / index_topk:2048`、FP8 `ue8m0` scale |
| H800 权重转换与启动 | `convert.py`（HF 权重→MP 分片）、`generate.py`（torchrun 交互式） |
| 高性能内核（README） | DeepGEMM PR#200（indexer logit kernel 含 paged 版）、FlashMLA PR#98（稀疏注意力 kernel）、TileLang 示例（`tile-ai/tilelang/examples/deepseek_v32`，研究友好版）——`kernel.py` 即其精简版 |
| 生态部署 | README：SGLang docker（H200/MI350/NPU a2/a3）、vLLM day-0 recipe（`--enable-dp-attention`） |

学习提示：`Indexer.forward` 里 `weights = weights_proj(x.float()) * n_heads**-0.5` 再与 q_scale、softmax_scale 相乘后**折进 fp8_index kernel 的逐头 scale**——公式 (1) 的 w_t,j 在实现上不是显式乘加，而是被吸收进量化 scale，这是读懂参考实现与论文对应关系的关键一处。

## 7. 学习路径

1. **前置**：MLA（V2 论文 §2，latent 压缩 + MQA 等价视图）、GQA/MQA、KV cache 与 PagedAttention、FP8 训练基础（分块量化/scale 格式 ue8m0）、GRPO（DeepSeekMath 论文或 R1 论文）。
2. **精读顺序**：§2.1 DSA 原型与两阶段训练 → 仓内 `model.py::Indexer` 对照读 → §2.3 成本分析（cost.jpg）→ §3.1 GRPO 四稳定技术（做 RL 工程的价值最高）→ §3.2 agent 合成流水线 → §4 主表。
3. **复现/动手建议**：
   - 本仓参考实现需 `torchrun generate.py`（8×GPU 起，先 `convert.py` 转权重）；学生可在 transformers 的 `DeepseekV32ForCausalLM` 上把 `index_topk` 调小做稀疏敏感性实验；
   - 单卡可完整复现 `Indexer` 的打分逻辑（fp8 换 bf16）：对一个 4K 序列可视化每 query 的 top-2048 位置热图，验证"局部+语义锚点"选择模式；
   - TileLang `fp8_index` kernel 是学 GPU kernel 编写的优秀教材（~60 行完成 FP8 逐头打分 GEMM）；
   - 关注 transformers 文档 `deepseek_v32.md` 的两个实现要点：q_lora_rank 必须存在（indexer 吃 query latent）、transformers 版在 bf16 下直算分数等价于 FP8+Hadamard。

（完）
