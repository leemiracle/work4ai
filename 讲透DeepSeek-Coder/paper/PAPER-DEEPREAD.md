# DeepSeek-Coder V1→V2 演进 + DeepSeekMoE 数学全景：论文深度解读

> 覆盖三篇论文（均已在 arXiv 核实标题与日期）：
> - **arXiv 2401.14196**《DeepSeek-Coder: When the Large Language Model Meets Programming -- The Rise of Code Intelligence》（2024-01-25 提交，v2 于 01-26）
> - **arXiv 2406.11931**《DeepSeek-Coder-V2: Breaking the Barrier of Closed-Source Models in Code Intelligence》（2024-06-17 提交）
> - **arXiv 2401.06066**《DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models》（2024-01-11 提交，被 Coder-V2 引用为架构基座）
>
> 勘误注：任务描述中 "V2 338B" 系口径混淆——**338 是支持的编程语言数量**，V2 总参数为 **236B（激活 21B）**、Lite 为 16B（激活 2.4B）。本文统一采用论文原文数字。
>
> 本文同时服务 讲透DeepSeek-Coder/ 与 讲透DeepSeek-Coder-V2/（后者 paper/ 下有指向本文的符号链接，内容共享）。

## 1. 一句话定位与时间线

**一句话定位**：V1 证明了"仓库级预训练 + FIM + 从零训练"的开源代码模型可以追平 GPT-3.5；MoE 论文解决了"专家不专"的架构病；V2 把两者嫁接到 DeepSeek-V2 的 MoE 底座上，用 21B 激活参数在代码与数学上首次把开源模型推到与 GPT-4-Turbo 同档。

三篇论文构成一条五个月的演进链：

| 时间 | 论文 | 角色 |
|---|---|---|
| 2024-01-11 | DeepSeekMoE | 架构预研：细粒度专家分割 + 共享专家隔离，2B→16B→145B 三级验证 |
| 2024-01-25 | DeepSeek-Coder | 数据与训练预研：repo 级语料管线 + FIM 消融，1.3B–33B dense |
| 2024-06-17 | DeepSeek-Coder-V2 | 合流：DeepSeek-V2 中间 checkpoint + 6T 续训 = MoE 化代码模型 |

团队均为 DeepSeek-AI（V1 与北大 HCST 合作，MoE 与北大/清华/南大合作），训练框架统一为 HAI-LLM（幻方），硬件 A100/H800 集群。

## 2. 动机与痛点：三代问题各不相同

**V1 面对的范式缺陷**：(1) 闭源模型（Codex、GPT-3.5）垄断代码智能，开源侧 StarCoder/CodeLlama 与之有肉眼可见差距；(2) 此前所有代码预训练都是 **file-level**——文件被打散拼接，模型看不到跨文件依赖，而真实工程是 repo 级的；(3) 单纯 next token prediction 学不会"中间填空"，而 IDE 补全恰恰是最高频落地场景。

**MoE 论文面对的架构病**：GShard 式 top-K 路由有两个先天缺陷——**knowledge hybridity**（专家数量少，如 8/16 个，每个专家被迫混杂装下 token 带来的各种知识，难以同时利用）与 **knowledge redundancy**（不同专家接到的 token 常需公共知识，多个专家各自重复学一遍）。两者共同封死了 MoE 的理论上界（同参 dense 模型）。

**V2 面对的经济账**：开源代码模型（含自家 V1-33B）与 GPT-4-Turbo/Claude 3 Opus/Gemini 1.5 Pro 仍有差距；dense 模型继续堆参数算力不可持续。答案是把 MoE 论文的架构（已三级验证）+ DeepSeek-V2 的底座（MLA 注意力 + 已训 4.2T tokens）+ V1 的代码数据配方（repo 级 + FIM）三合一。

## 3. 核心方法

### 3.1 V1：仓库级语料管线（论文真正的第一贡献）

四步流水线（README "Procedure of Data Creation" 与论文 §2 一一对应）：

1. **抓取与规则过滤**：2023 年 2 月前创建的 GitHub 公开仓，87 种语言，套用 StarCoder Data 规则（平均行长>100 字符剔除、字母占比<25% 剔除、HTML 可见文本比、JSON/YAML 50–5000 字符等），数据剩原始的 **32.8%**；
2. **依赖解析**（Algorithm 1）：正则抽取同仓文件间调用关系（Python `import`、C# `using`、C `include`），做**改进拓扑排序**——不取零入度点而是取最小入度点（容忍依赖环），保证被依赖文件排在前面；文件路径以注释形式写入拼接样本；
3. **repo 级 minhash 近去重**：以整个仓库拼接文本为去重单位（而非文件级），保护仓库结构完整性；
4. **质量筛查与去污染**：编译器 + 质量模型过滤语法错误/低可读性代码；对 HumanEval/MBPP/GSM8K/MATH 做 10-gram（≥10-gram 相同即剔除）与 3–10 gram 精确匹配去污染。

最终语料 **798GB / 6.03 亿文件 / 87 语言**，配比 87% 代码 + 10% 代码相关英文（GitHub Markdown + StackExchange）+ 3% 无关中文。

### 3.2 V1：Fill-in-the-Middle 的工程化定论

文档级、packing 前执行，PSM 模式，FIM rate 0.5。训练样本形如：

$$
\texttt{<|fim\_start|>}\ f_{pre}\ \texttt{<|fim\_hole|>}\ f_{suf}\ \texttt{<|fim\_end|>}\ f_{middle}\ \texttt{<|eos\_token|>}
$$

1.3B 模型 + Python 子集的消融（HumanEval-FIM 单行填空）给出三条此后被全行业采用的结论：**100% FIM rate 填空最强但伤常规补全**（存在 trade-off）；**50% PSM 优于 MSP**（T5 式多 span 掩码）；最终选 **50% PSM** 平衡两能力。（勘误注：论文 sentinel 写作 `fim_start/fim_hole/fim_end`，README 与实际 tokenizer 用 `<｜fim▁begin｜>`/`<｜fim▁hole｜>`/`<｜fim▁end｜>` 下横线变体，用法见 README Code Insertion 示例。）

### 3.3 V1：架构与三段训练

DeepSeek LLM 同构：decoder-only + RoPE + SwiGLU + FlashAttention-2，33B 引入 GQA（组大小 8）。三档超参（hidden/intermediate/layers/heads）：1.3B=2048/5504/24/16；6.7B=4096/11008/32/32；33B=7168/19200/62/56。Tokenizer 为 32K BPE（HuggingFace tokenizers）。

训练三段式：**1.8T tokens @4K 窗口 → 200B tokens @16K**（RoPE 线性缩放 factor 1→4、base 1000→100000，理论 64K、实测 16K 内可靠）→ **2B tokens 指令微调**（Alpaca 格式、`<|EOT|>` 分隔、lr 1e-5、batch 4M tokens）。

论文 §5 还预告了 **V1.5**：改从 DeepSeek-LLM-7B 继续预训练 2T tokens（70% 代码/10% Markdown+SE/7% 代码相关 NL/7% 数学 NL/6% 双语 NL），纯 NTP@4K——数学与自然语言大涨、代码略降，说明"代码特化 vs 通用能力"在 dense 时代只能靠数据配比调和。这个矛盾正是 V2 用 MoE 续训要解的。

### 3.4 DeepSeekMoE 数学完整展开

**基线（GShard 式 top-K 路由）**，第 $l$ 层 FFN 换成 MoE 层后：

$$
\mathbf{h}_t^l = \sum_{i=1}^{N} \left( g_{i,t} \operatorname{FFN}_i(\mathbf{u}_t^l) \right) + \mathbf{u}_t^l \tag{3}
$$

$$
g_{i,t} = \begin{cases} s_{i,t}, & s_{i,t} \in \operatorname{Topk}(\{s_{j,t}\}_{j=1}^{N}, K) \\ 0, & \text{otherwise} \end{cases} \tag{4}
\qquad
s_{i,t} = \operatorname{Softmax}_i\left( (\mathbf{u}_t^l)^{T} \mathbf{e}_i^l \right) \tag{5}
$$

其中 $\mathbf{e}_i^l$ 是专家质心（router 权重），$g_{i,t}$ 稀疏——每 token 只算 $K$ 个专家。

**创新一：细粒度专家分割**。每个专家的 FFN 中间维砍成 $1/m$，专家数变 $mN$ 个，激活数相应乘 $m$ 倍（参数量与计算量不变）：

$$
\mathbf{h}_t^l = \sum_{i=1}^{mN} \left( g_{i,t} \operatorname{FFN}_i(\mathbf{u}_t^l) \right) + \mathbf{u}_t^l, \quad g_{i,t} \neq 0 \iff s_{i,t} \in \operatorname{Topk}(\cdot, mK) \tag{6–8}
$$

组合数论证是全文最漂亮的直觉：$N=16$ 时 top-2 只有 $\binom{16}{2}=120$ 种组合；切成 4 份后 64 选 8 有 $\binom{64}{8}=4{,}426{,}165{,}368$ 种——**组合灵活性爆炸式增长，知识获取才可能"精准定位"**。

**创新二：共享专家隔离**。$K_s$ 个专家永被激活，专门吸收公共知识；为保持计算量不变，路由专家的激活数减 $K_s$。完整架构：

$$
\mathbf{h}_t^l = \underbrace{\sum_{i=1}^{K_s} \operatorname{FFN}_i(\mathbf{u}_t^l)}_{\text{共享专家，无门控}} + \underbrace{\sum_{i=K_s+1}^{mN} \left( g_{i,t} \operatorname{FFN}_i(\mathbf{u}_t^l) \right)}_{\text{Topk}(\cdot,\ mK-K_s)\ \text{路由专家}} + \mathbf{u}_t^l \tag{9–11}
$$

**双层负载均衡损失**（防路由崩溃 + 防设备瓶颈）：

$$
\mathcal{L}_{\mathrm{ExpBal}} = \alpha_1 \sum_{i=1}^{N'} f_i P_i, \qquad
f_i = \frac{N'}{K'T} \sum_{t=1}^{T} \mathbb{1}(\text{Token } t \text{ selects Expert } i), \qquad
P_i = \frac{1}{T} \sum_{t=1}^{T} s_{i,t} \tag{12–14}
$$

$$
\mathcal{L}_{\mathrm{DevBal}} = \alpha_2 \sum_{i=1}^{D} f_i' P_i', \qquad
f_i' = \frac{1}{|\mathcal{E}_i|} \sum_{j \in \mathcal{E}_i} f_j, \qquad
P_i' = \sum_{j \in \mathcal{E}_i} P_j \tag{15–17}
$$

其中 $N' = mN - K_s$、$K' = mK - K_s$，$\mathcal{E}_i$ 是部署在第 $i$ 台设备上的专家组。实践取**小 $\alpha_1$（防崩溃即可，过大伤性能）+ 大 $\alpha_2$（真瓶颈在设备间）**：2B 单卡实验 $\alpha_1=0.01$、无设备损失；16B 单设备层内部署 $\alpha_1=0.001$；145B 专家并行 4 设备时加 $\alpha_2=0.05$。这套"专家级松弛、设备级严格"的设计哲学后来在 DeepSeek-V2 演进为 auxiliary-loss-free 均衡（本文之外的故事）。

**三级验证**（2B/16B/145B）关键数字：

- **2B**（9 层/1280 hidden，1 shared + 63 routed，专家=0.25×FFN，激活 1+7）：Pile loss **1.808** vs GShard 1.867 / Switch 1.881 / Hash 1.932 / Dense-0.2B 2.060；TriviaQA EM 16.6 vs GShard 10.2。对标 GShard×1.5（专家参数与 FLOPs 均放大到 1.36–1.5 倍）打平（Pile 1.808 = 1.808），对标 Dense×16（16 专家全开，激活专家参数 1.89B vs 0.24B）只差 0.002（1.808 vs 1.806）——**逼近 MoE 理论上界**。
- **16B**（28 层/2048，首层保 dense 因其负载收敛慢，2 shared + 64 routed top-6，专家=0.25×，总 16.4B/激活 2.8B，2T tokens，vocab 100K）：FLOPs 每 4K token **74.4T vs DeepSeek-7B dense 183.5T（40.5%）**，Pile BPB 0.74 反超 0.75，HumanEval 26.8 vs 26.2；对 LLaMA2-7B 代码项碾压（HumanEval 26.8 vs 14.6，MBPP 39.2 vs 21.8）。
- **145B**（62 层/4096，4 shared + 128 routed top-12，专家=0.125×，总 144.6B/激活 22.2B）：当时仅训 245B tokens 的初步研究，已显示可用 **28.5%（乐观 18.2%）**计算匹配 DeepSeek-67B。

**专家特化三连证据**（§4.5，比跑分更有思想价值）：① 按 ratio 屏蔽 top 路由专家，DeepSeekMoE 的 Pile loss 掉得比 GShard×1.5 更快 = 路由专家冗余更低、更不可替代；② 屏蔽共享专家（补激活一个路由专家保持算力不变）Pile loss **1.808 → 2.414** = 共享专家捕获的是路由专家学不到的基础知识；③ 激活路由专家从 7 减到 4 仍≈GShard 全量；从零重训 1+63、top-3（一半激活参数）仍胜 GShard = 知识获取更准、有效参数占比更高。

### 3.5 V2：合流工程

- **续训起点**：DeepSeek-V2 中间 checkpoint（已训 4.2T tokens）+ 6T 新数据 = **10.2T 总曝光**。这一步省掉了从零训练的全部成本，还继承了 V2 的通用能力。
- **新数据**：60% 源代码 / 10% 数学 / 30% 自然语言。代码 1170B tokens = GitHub 规则过滤+近去重后 821B（338 语言）+ 185B 代码相关文本 + DeepSeekMath 式 fastText 迭代召回（CommonCrawl 70B + GitHub 94B）；数学 221B（≈DeepSeekMath 120B 语料的近两倍）；NL 直接采样自 V2 语料。1B 对照实验证明新语料价值：HumanEval 30.5→36.0（1T）/→37.2（2T），MBPP 44.6→49.0/→54.0。
- **架构**：与 DeepSeek-V2 完全一致（细粒度 DeepSeekMoE + MLA 多头潜在注意力 + 解耦 RoPE；16B/236B 超参分别对应 V2-Lite/V2，其中 Lite 即 2 shared + 64 routed、每 token 6 个路由专家的 MoE-16B 配方）。工程插曲：训练中出现梯度尖峰，归因于 exponent normalization，回退常规 normalization 解决。
- **FIM 只给 16B**（0.5 PSM，承接 V1 结论），236B 纯 NTP；tokenizer 换用 V2 的 100K 词表（对比 V1 的 32K）。
- **128K 长上下文**：YaRN（s=40, α=1, β=32）两阶段续训——32K@batch1152×1000 步 → 128K@batch288×1000 步，NIAH 全绿。
- **对齐两段**：SFT（20k 代码指令 + 30k 数学指令取自 V1/DeepSeek-Math + V2 通用指令 = 300M tokens，lr 5e-6，共 1B tokens）→ **GRPO 强化学习**（约 40k 带 test case 的 prompt）。GRPO（Group Relative Policy Optimization，出自 DeepSeekMath）的核心思想是用**同一 prompt 组内多个采样回答的相对奖励互为基线**，从而省掉 PPO 必须独立维护的 critic 模型——V2 论文明确指出这正是它成本更低的原因。代码域的特殊性在于奖励信号的设计：编译器 + 测试用例天然给出 0-1 反馈，但论文发现测试覆盖不足时该信号噪声大且次优，故改为在编译器数据上训练 reward model 再供 RL 使用；内部 LeetCode/Leetcode-zh 测试集上，reward model 信号组显著优于原始编译器信号组。这是"可验证奖励怎么用才稳健"的一份一手工程证据，同一套基础设施后来直接哺育了 DeepSeek-R1。

## 4. 实验与结果：关键数字速览

**V1（vs 当代开源/闭源）**：Base-33B HumanEval **56.1** / MBPP **66.0** / 多语言均值 50.3（CodeLlama-34B：41.0/55.2）；6.7B 已达 CodeLlama-34B 水平。Instruct-33B HumanEval **79.3** 超 GPT-3.5-Turbo（76.2），逼近 GPT-4（84.1）。FIM 单行填空 mean：1.3B 70.4 → 6.7B 80.7 → 33B 81.2，全面领先 StarCoder 69.7。DS-1000 均值 40.2（CodeLlama-34B 34.3）。LeetCode Contest（2023-07 后 180 题，防污染）：Instruct-33B+CoT 28.9 vs GPT-3.5-Turbo 23.3 vs GPT-4-Turbo 41.8——论文坦承 7/8 月赛题仍有污染风险。

**V1 的核心自证——repo 级语料值不值**：论文用 CrossCodeEval（2023 年 3–6 月新建仓构造，严格晚于预训练截断，无泄漏）检验跨文件补全，6.7B + BM25 检索（512 token 跨文件上下文）对 CodeLlama-7B 同设置：Python EM 16.14 vs 13.02、Java 17.72 vs 16.41、TypeScript 14.03 vs 12.34、C# 16.23 vs 13.19，四语言全胜。更关键的是消融行"去掉 repo 级预训练"（同数据规模 file-level 训练）：TS 掉到 13.23、C# 掉到 14.48——**依赖感知的数据组织带来的增益在跨文件依赖最重的语言上最显著**，这是"数据结构即知识"的直接证据。

**V2（vs GPT-4 世代闭源，均为论文口径 greedy/单次）**：

| 基准 | DS-Coder-V2-236B (21B act) | GPT-4-Turbo-0409 | GPT-4o | DS-Coder-V1-33B |
|---|---|---|---|---|
| HumanEval | **90.2** | 88.2 | 91.0 | 79.3 |
| MBPP⁺ | **76.2** | 72.2 | 73.5 | 70.1 |
| LiveCodeBench (1201-0601) | 43.4 | **45.7** | 43.4 | 22.5 |
| Aider | **73.7** | 63.9 | 72.9 | 54.5 |
| SWE-bench | 12.7（开源首个>10%） | 18.3 | 26.7 | 0.0 |
| MATH | 75.7 | 73.4 | **76.6** | - |
| AIME 2024 | **4/30** | 3/30 | 2/30 | - |
| MMLU | 79.2 | - | - | - |

Lite-16B（2.4B 激活）同样能打：HumanEval 81.1 平 Llama3-70B，RepoBench-Python 38.9 ≈ V1-33B dense 39.1，FIM 86.4 并列第一——**1/14 的激活参数换 33B dense 的补全能力**。对 DeepSeek-V2-Chat 的对照（论文 Table 10）显示续训净效应：BBH 79.7→83.9、MATH 类大涨，代价是 TriviaQA 86.7→82.3、NQ 53.4→47.5（web 数据占比下降）。

## 5. 局限与后续

**论文自认**：V1 承认 16K 之外（理论 64K）输出不可靠、LeetCode 有污染残留、多选题非所长；MoE 论文承认 16B 多选题弱（attention 参数仅 0.5B vs dense-7B 的 2.5B，MMLU 45.0 vs 48.2——参数都堆到 FFN/专家上了）、145B 仅初步（245B tokens）；V2 承认知识密集基准回落、CRUXEval 代码推理与 GPT-4o 仍有差距（归因激活参数仅 21B）、Lite 在 SWE-bench/Defects4J 上几乎为零。

**社区与后续**：V1 的 repo 级管线与 50% FIM/PSM 成为代码模型事实标准（StarCoder2、Qwen-Coder 等沿用）；一个常被低估的工程遗产是 tokenizer——V1 用 HuggingFace Byte-level BPE 自定义 pre-tokenizer，无法转 SentencePiece，社区量化生态（GGUF/GPTQ）一度不兼容，官方为此向 llama.cpp 提交 PR #4070 全量支持 HF pre-tokenizer、并在 README 给出 GPTQ 的 RoPE scaling=4 注意事项（`DeepSeek-Coder/README.md` §7 Q&A），这侧面说明"小设计选择会外溢成生态成本"。DeepSeekMoE 的细粒度+共享专家路线在 DeepSeek-V2/V3 一路进化（V3 走到 1 shared + 256 routed、auxiliary-loss-free 均衡）；V2 的"通用底座续训代码化"范式与 GRPO 直接为 DeepSeek-R1 铺路（R1 的 RL 基础设施即 GRPO）。Aider 73.7 全场第一、SWE-bench 开源破 10% 是当时最具标志性的两个数字。

## 6. 与本地代码的对照

| 论文概念 | 本仓位置（~/ai/explore/deepseek-ai/） |
|---|---|
| 数据四步管线（过滤→依赖拓扑排序→repo 级 minhash→质量筛查） | `DeepSeek-Coder/README.md` §3 "Procedure of Data Creation" 四步图文 |
| FIM sentinel tokens（论文式 vs 实际 `<｜fim▁begin｜>/<｜fim▁hole｜>/<｜fim▁end｜>`） | `DeepSeek-Coder/README.md` §4-2 "Code Insertion" 可运行示例 |
| 仓库级补全（依赖排序后的跨文件拼接样本） | `DeepSeek-Coder/README.md` §4-4 utils.py/model.py/main.py 三文件示例+GIF |
| 指令微调 Alpaca 格式 + `<|EOT|>` + IGNORE_INDEX=-100 label mask | `DeepSeek-Coder/finetune/finetune_deepseekcoder.py`（`EOT_TOKEN`、`build_instruction_prompt`、`_tokenize_fn`） |
| 评测复现（HumanEval/MBPP/DS-1000/LeetCode Contest/PAL-Math） | `DeepSeek-Coder/Evaluation/` 五个子目录（LeetCode 基准即论文自建并开源） |
| V1 训练三段式（1.8T@4K→200B@16K→2B SFT） | `DeepSeek-Coder/README.md` §3 "Model Training" 三步 |
| V2 模型表 16B/236B、激活 2.4B/21B、128K | `DeepSeek-Coder-V2/README.md` §2 Model Downloads 表 |
| 338 语言清单（论文 Appendix A） | `DeepSeek-Coder-V2/supported_langs.txt`（实测 338 行） |
| V2 五组评测表（生成/补全/修复/数学/通用+128K NIAH） | `DeepSeek-Coder-V2/README.md` §3.1–3.6（与论文 Tables 3-10 数字一致） |
| MoE 架构（式 9-11） | 本地无 DeepSeek-MoE 权重代码，但 `DeepSeek-MoE/`、`DeepSeek-V2/` 仓在同级目录；V2 模型实现走 HF `trust_remote_code`（README §6 加载示例） |
| 论文 PDF | `DeepSeek-Coder-V2/paper.pdf`；V1 无本地 PDF（arXiv 2401.14196） |

DeepWiki 抽查佐证：`讲透DeepSeek-Coder/deepwiki/2.1-architecture.md` 的架构描述（decoder-only/RoPE/16K/1B–33B 家族/2T tokens）与论文 §3.3 一致，可作为代码侧索引使用。

## 7. 学习路径

**前置**：Transformer 基础（FFN/注意力/RoPE）、BPE 分词、交叉熵语言建模；MoE 部分需要 GShard/Switch Transformer 的 top-K 路由背景。

**精读顺序（建议）**：① DeepSeekMoE §1–3（先懂"为什么专家要又细又共享"，式 3–11 逐行推）→ ② DeepSeekMoE §4.4–4.5（消融与三连分析是方法论精髓：如何证明"特化"这件事）→ ③ DeepSeek-Coder §2–3（数据管线 Algorithm 1 + FIM 消融图）→ ④ DeepSeek-Coder-V2 全文（最薄的一篇，本质是工程合流报告，重点读 §2 数据与 §3.5.2 reward model vs 编译器信号的决策）。

**复现建议**（按成本升序）：(1) FIM 消融可单卡复现——1.3B 级模型 + The Stack Python 子集 + HumanEval-FIM，验证 50% PSM 的 trade-off 曲线；(2) DeepSeekMoE 2B 配方（1+63、top-7、0.25×专家）可用开源 DeepSeekMoE-16B 权重做路由分析复刻 §4.5 的"禁用 top 专家/禁用共享专家"实验，Pile loss 曲线一天可跑完；(3) repo 级拓扑排序管线可直接对任意 GitHub 仓实现（正则 import 图 + 最小入度拓扑排序），是数据工程课的好作业；(4) V2 全量复现不现实，但"从通用底座 checkpoint 续训代码语料"的范式可在 1–2B 尺度用 Lite 配方验证 BBH/MATH 的增益方向。

**一句话收束**：V1 解决"代码模型该吃什么数据"，MoE 解决"参数该怎么装进专家"，V2 证明这两件事可以嫁接在一个通用 MoE 底座上——此后 DeepSeek 系所有代码与推理模型（V3、R1）都是这条路线的后裔。配合本目录 deepwiki/ 全站文档与本地两仓 README/finetune/Evaluation 代码阅读，可形成"论文—文档—代码"三层互证的完整学习闭环。
