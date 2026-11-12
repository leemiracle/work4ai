# DeepSeekMath 论文深度解读（PAPER-DEEPREAD）

> 主论文：**arXiv 2402.03300**《DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models》（v1 2024-02-05，v3 2024-04-27）
> 前置关联：**arXiv 2310.06786**《OpenWebMath: An Open Dataset of High-Quality Mathematical Web Text》（2023-10-10，简要带过）
> ⚠️ **勘误（任务模板要求核实）**：任务描述称 2310.06786 为"DeepSeekMath 7B 初版"，**不属实**。经 arXiv 页核实，2310.06786 实为 **OpenWebMath**（Paster / Dos Santos / Azerbayev / Jimmy Ba，多伦多大学组）——它是本仓 README §3 引用的**种子语料论文**（数学语料部分描述正确），并非 DeepSeek 团队的前身论文。DeepSeekMath 的真正基座是 DeepSeek-LLM（arXiv 2401.02954）与 DeepSeek-Coder-v1.5（arXiv 2401.14196）。本报告按"README 实际引用关系"处理：以 2402.03300 为主，OpenWebMath 作为语料管线种子一节简要带过。

---

## 1. 一句话定位与团队背景

**一句话定位**：DeepSeekMath 是第一个在竞赛级 MATH 基准上突破 50%（51.7%）且不用外部工具与投票的开源 7B 模型，其两大支柱是"从 Common Crawl 迭代挖掘出的 120B token 数学语料"与"去掉 critic、用组内相对奖励做基线的 GRPO 算法"——GRPO 后来成为 DeepSeek-R1 与整个开源 RLHF 社区（TRL、verl 等）的标准算法。

**团队与时间线**：DeepSeek-AI 联合清华（邵智宏）、北大（王培义、朱奇豪）实习生产出；Daya Guo 为通讯作者。v1 投稿于 2024 年 2 月，v3（终版）更新于 2024 年 4 月，补充了统一范式分析与大量消融。三阶段产物全部开源：DeepSeekMath-Base / Instruct / RL 7B（HF 权重）+ 本评测仓。

---

## 2. 动机与痛点

1. **开源与闭源的数学鸿沟**：GPT-4 / Gemini-Ultra 在 MATH 上 ~52-53%，而当时最强开源（Mistral 7B、Llemma 34B）只有 14-25%，差距悬殊且闭源不可研究。
2. **"高质量数学数据从哪来"无解**：社区迷信 arXiv 语料（Minerva、MathPile 85% 来自 arXiv），但从未系统验证其收益；Common Crawl 里的数学网页潜力巨大却没有可靠的筛选管线。
3. **PPO 做 RL 微调太贵**：标准 PPO（InstructGPT 式）需要同时常驻 4 个模型——policy、reference、reward、**critic（value network）**。critic 与 policy 同量级（7B），显存与计算负担翻倍；且在数学 RL 中奖励通常只在**序列末尾一个 token**上给出，逐 token 精确的 value function 既难训练又只用来当 baseline（降方差），性价比极低。

论文的回答：①用 fastText 迭代分类器从 CC 挖出 9 倍于 OpenWebMath 的高质量语料；②把 critic 整个删掉，用"同一问题的 G 个采样的平均奖励"当 baseline——这就是 GRPO。

---

## 3. 核心方法

### 3.1 DeepSeekMath Corpus：迭代式数学语料挖掘（论文 §2.1，README §3）

直觉：给定小而优的种子集（OpenWebMath），训一个轻量分类器去召回"长得像种子"的网页，再用领域统计+人工标注反哺种子，滚雪球四轮：

1. 以 OpenWebMath 为正例（50 万条）、CC 一般网页为负例（50 万条），训 **fastText** 分类器（向量 256 维、lr 0.1、word n-gram≤3、3 epoch）；
2. 从 **去重后的 40B HTML 网页**（URL 去重 + 近去重）中召回数学页，按分类器分数排序只留头部（首轮留 40B token，用 40/80/120/160B 预训练实验定容）；
3. 把 CC 按域名分桶，某域名下 **>10% 网页被首轮收集**即判为数学域（如 mathoverflow.net）；
4. 人工标注数学域内的 URL 前缀（如 mathoverflow.net/questions），把其下未收集网页加入种子；
5. 回到第 1 步，**迭代 4 轮**后得 35.5M 页 / **120B token**（第 4 轮时 98% 已被第 3 轮覆盖，收敛）。

**去污染**：与评测题恰好匹配 **10-gram**（短文本 ≥3-gram 精确匹配）的网页整段剔除，覆盖 GSM8K / MATH / CMATH / AGIEval。

**质量验证**（1.3B 小模型各训 150B token，Table 1）：DeepSeekMath Corpus 在 GSM8K/MATH/CMATH = **23.8%/13.6%/41.5%**，大幅领先 Proof-Pile-2（14.3/11.2/19.9）、OpenWebMath（11.5/8.9/16.8）、MathPile（2.7/3.3/1.2）——后者甚至不如不训练。语料中英双语，中文基准（CMATH 41.5%）独一档。

### 3.2 DeepSeekMath-Base 7B：继续预训练配方（论文 §2.3）

- 初始化：**DeepSeek-Coder-Base-v1.5 7B**（代码模型起步优于通用 LLM，§5.1.1 消融支持）；
- 数据 500B token 配比：**56% DeepSeekMath Corpus + 4% AlgebraicStack + 10% arXiv + 20% GitHub code + 10% 中英自然语言**；
- 训练：lr 峰值 4.2e-4（multi-step 衰减），batch 10M token，HAI-LLM 框架，AdamW（β1=0.9, β2=0.95, wd=0.1）。

结果：GSM8K **64.2%**、MATH **36.2%**，超过大它 77 倍的闭源 Minerva 540B（58.8/33.6）；MMLU 54.9% / BBH 59.5% 还比前身 Coder-v1.5 涨了（数学训练反哺通用推理）。

### 3.3 SFT（论文 §3）

776K 条指令数据，覆盖三种格式：**CoT**（逐步推理）、**PoT**（程序推理）、**TIR**（工具集成推理）。英文侧给 GSM8K/MATH 人工标注 TIR 解答 + MathInstruct 子集 + Lila-OOD；中文侧 K-12 题 76 子话题。训练仅 500 步（batch 256，lr 5e-5，4K 上下文，样本随机拼接）。得到 DeepSeekMath-Instruct 7B：MATH 46.8%（超所有开源与多数闭源，仅次于 GPT-4/Gemini-Ultra），TIR 模式 MATH 57.4%。

### 3.4 GRPO：从 PPO 到无 critic 的组相对策略优化（论文 §4.1，重点）

#### 第一步：PPO 基线（式 1、式 2）

PPO 是 actor-critic 算法，优化带 clip 的代理目标：

$$
\mathcal{J}_{PPO}(\theta)=\mathbb{E}\big[q\sim P(Q),\, o\sim\pi_{\theta_{old}}(O|q)\big]\frac{1}{|o|}\sum_{t=1}^{|o|}\min\Big[\rho_t A_t,\ \text{clip}(\rho_t,\,1-\varepsilon,\,1+\varepsilon)A_t\Big],
$$

其中 $\rho_t=\dfrac{\pi_\theta(o_t|q,o_{<t})}{\pi_{\theta_{old}}(o_t|q,o_{<t})}$ 是重要性采样比率，$\varepsilon$ 为 clip 超参。优势 $A_t$ 由 **GAE** 基于 reward 序列 $\{r_{\geq t}\}$ 和**学出来的 value function $V_\psi$** 计算。RLHF 标准做法还把 per-token KL 惩罚揉进 reward（式 2）：

$$
r_t = r_\varphi(q,o_{\leq t}) - \beta\log\frac{\pi_\theta(o_t|q,o_{<t})}{\pi_{ref}(o_t|q,o_{<t})}.
$$

**两个痛点**：(a) $V_\psi$ 与 policy 同量级 → 显存/计算近翻倍；(b) LLM 数学 RL 里 reward 通常只在**末 token**打分，逐 token 的 value function 训不准；而 $V_\psi$ 在这里**仅仅充当降方差的 baseline**。既然只是 baseline，何必训一个 7B 模型去估？

**理论直觉**：policy gradient 定理告诉我们 $\mathbb{E}[\nabla\log\pi\cdot b(q)] = 0$ 对任何只依赖 $q$（不依赖动作）的基线成立，减去基线不改期望梯度、只降方差。经典 REINFORCE with baseline 用 $b(q)=V_\psi(q)$；而组内 $G$ 条同题采样的平均奖励 $\frac{1}{G}\sum_i r_i$ 恰是 $V(q)$ 的**蒙特卡洛估计**——同一批样本既用来估基线又用来算梯度，于是 critic 的整条学习曲线（GAE、TD 误差、critic loss）都可以整体删除，代价只是每题多采 $G$ 倍输出（推理便宜、显存不涨）。这是"用采样换显存"的工程权衡，也是 GRPO 能在单机多卡上跑通 7B RL 的根本原因。

#### 第二步：GRPO 目标（式 3）

对每个问题 $q$，从旧策略采 **一组** 输出 $\{o_1,\dots,o_G\}\sim\pi_{\theta_{old}}(O|q)$，用组内平均奖励替代 value function 当 baseline：

$$
\mathcal{J}_{GRPO}(\theta)=\mathbb{E}\Big[q\sim P(Q),\,\{o_i\}_{i=1}^G\sim\pi_{\theta_{old}}\Big]\ \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|}\sum_{t=1}^{|o_i|}\Big\{\min\big[\rho_{i,t}\hat A_{i,t},\ \text{clip}(\rho_{i,t},1-\varepsilon,1+\varepsilon)\hat A_{i,t}\big]-\beta\,\mathbb{D}_{KL}[\pi_\theta\Vert\pi_{ref}]\Big\},
$$

结构上与 PPO 的区别仅两处：①外层多一层组平均 $\frac{1}{G}\sum_i$；②**KL 正则直接从 reward 里挪到 loss 里**（逐 token 减 $\beta\mathbb{D}_{KL}$），避免污染 advantage 的计算。作者还指出组相对形式与 reward model 的训练方式（同题比较式标注）天然对齐。

#### 第三步：无偏 KL 估计（式 4，Schulman 2020 的 k3 估计器）

$$
\mathbb{D}_{KL}[\pi_\theta\Vert\pi_{ref}] = \frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_\theta(o_{i,t}|q,o_{i,<t})} - \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_\theta(o_{i,t}|q,o_{i,<t})} - 1 \ \geq 0,
$$

即 $u - \log u - 1$（$u=\pi_{ref}/\pi_\theta$），由 $x-\log x\geq 1$ 恒非负，保证惩罚项永远不为负、且方差比朴素 KL 更低。

#### 第四步：组相对优势（outcome / process 两种监督）

**Outcome Supervision（OS）**：reward model 对整条输出打一个分，组内 z-score 归一化后广播到所有 token：

$$
\hat A_{i,t} = \tilde r_i = \frac{r_i - \text{mean}(\mathbf r)}{\text{std}(\mathbf r)},\qquad \forall t.
$$

**Process Supervision（PS）**：过程奖励模型对每个推理步末尾打分（第 $i$ 条输出第 $j$ 步末 token 下标为 $index(j)$），所有步的分数**合并进同一个组归一化**，再按"后续步骤奖励之和"折算到每个 token：

$$
\tilde r_i^{index(j)} = \frac{r_i^{index(j)}-\text{mean}(\mathbf R)}{\text{std}(\mathbf R)},\qquad
\hat A_{i,t} = \sum_{index(j)\geq t}\tilde r_i^{index(j)}.
$$

#### 第五步：迭代 GRPO（Algorithm 1）

外层每轮：$\pi_{ref}\leftarrow\pi_\theta$（参考模型跟随当前策略）；内层 M 步：$\pi_{old}\leftarrow\pi_\theta$ → 每题采 $G$ 条输出 → 打 reward → 组相对 advantage → 做 $\mu$ 次 GRPO 内层更新。每轮结束后用策略模型的采样结果 + **10% 历史数据 replay** 持续训练 reward model，防止旧 RM 跟不上新策略。

#### 附录视角：梯度统一范式（式 5 / Table 10 / 式 21）

所有方法（SFT/RFT/DPO/Online RFT/PPO/GRPO）的梯度都可写成：

$$
\nabla_\theta\mathcal{J}_\mathcal{A}(\theta)=\mathbb{E}\big[(q,o)\sim\mathcal{D}\big]\Big(\frac{1}{|o|}\sum_{t=1}^{|o|}\ \underbrace{GC_\mathcal{A}(q,o,t,\pi_{rf})}_{\text{梯度系数}}\ \nabla_\theta\log\pi_\theta(o_t|q,o_{<t})\Big).
$$

三要素：**Data Source**（离线 SFT 采样 vs 在线 policy 采样）、**Reward Function**（Rule 判答案 vs Model 打分）、**Gradient Coefficient**。GRPO 的梯度系数（式 21，无 clip 简化形式）：

$$
GC_{GRPO} = \hat A_{i,t} + \beta\Big(\frac{\pi_{ref}(o_{i,t})}{\pi_\theta(o_{i,t})}-1\Big).
$$

对照：SFT 的 GC≡1；RFT/Online RFT 只对"答案正确"给 +1（不罚错、不分级）；GRPO 按组归一化 reward **分级奖惩**——这是它超过 Online RFT 的关键消融结论。

#### RL 训练配置（论文 §4.2）

起点 DeepSeekMath-Instruct 7B；数据只用 SFT 里 GSM8K+MATH 的 **CoT 格式 ~144K 题**（其余全部剔除以考察 OOD 泛化）；初始 RM 基于 DeepSeekMath-Base 7B（lr 2e-5）；policy lr 1e-6，KL 系数 β=0.04，**每题采 G=64 条**，max length 1024，batch 1024，每个探索阶段后仅更新 1 步。

**工程解读**：这份超参几乎每个数字都在讲"稳定压倒一切"——policy lr 比 SFT 低 50 倍，探索后只走一步就重新采样（$\pi_{old}$ 与 $\pi_\theta$ 几乎不脱节，clip 很少触发）；β=0.04 的 KL 系数把策略锁死在 Instruct 模型附近，防止 reward hacking；G=64 的大组换来 advantage 估计的低方差（组均值/标准差的蒙特卡洛噪声随 G 收敛）。换句话说，GRPO 在这篇论文里是"极其保守的微调"，这也呼应 §5.2.2 的结论：它修的是输出分布的对齐，不是能力本身。

---

## 4. 实验与结果

**主表（Table 5，Top1）**：

| 模型 | GSM8K (CoT) | MATH (CoT) | MGSM-zh | CMATH | MATH (TIR) |
|---|---|---|---|---|---|
| DeepSeekMath-Instruct 7B | 82.9 | 46.8 | 73.2 | 84.6 | 57.4 |
| **DeepSeekMath-RL 7B (GRPO)** | **88.2** | **51.7** | **79.6** | **88.8** | **58.8** |
| （参照）GPT-4 | 92.0 | 52.9 | – | 86.0 | 69.7 (Code Interpreter) |
| （参照）WizardMath-v1.1 7B | 83.2 | 33.0 | – | – | – |

GRPO 只用英文 CoT 数据训练，却在中文与 TIR 等 OOD 设置上全面提升（CMATH 84.6→88.8）；MATH 64 样本 self-consistency 达 **60.9%**；RL 7B 打赢所有 7B-70B 开源模型及 Gemini Pro / Inflection-2 / GPT-3.5 / GLM-4 / Baichuan-3。

值得注意的是实验设计的克制：作者刻意把 RL 数据收窄到 GSM8K+MATH 的 CoT 子集（144K 题），其余 SFT 数据全部不用——MATH 从 46.8 到 51.7 的提升无法用"多见数据"解释，而 MGSM-zh/CMATH/TIR 的同步上涨更说明 GRPO 学到的是某种与语言和解码格式都无关的通用对齐收益。这张表因此成为"RL 阶段价值"最常被引用的证据之一。

**关键消融**：

**评测协议备注**：Base 模型全部用 few-shot（CoT 4-shot / PoT few-shot）评测以测预训练潜力；Instruct/RL 模型用 zero-shot + 固定 \boxed{} 提示词（即本仓 `run_subset_parallel.py` 的模板）测指令遵循；表中灰色分数是 32 候选多数投票，正文分数一律 Top1。MATH 答案判定不比字符串而比数学等价（sympy 符号/数值双通道），这也是本仓 `eval_utils.py` 的核心逻辑——复现该论文数字时判分器必须对齐，否则会低估 2-3 个点。

- **代码训练有益数学**（Table 6/7，1.3B）：两阶段 code(400B)→math(150B) 最优（GSM8K 21.9% vs general→math 19.1%）；单阶段混训虽拉低纯 CoT 数学，却让 tool-use 数学（GSM8K+Python 19.7%）与代码能力（HumanEval 29.3%）兼得——这正解释了 Base 7B 从 Coder 起步 + 混 20% code 的配方。
- **arXiv 语料无效甚至有害**（Table 8）：MathPile / ArXiv-RedPajama 训练后多数基准不升反降，颠覆"arXiv=数学数据"的直觉。
- **统一范式消融**（图 5/6）：Online RFT > RFT（在线采样后期优势拉大）；GRPO > Online RFT（分级奖惩 vs 0/1 奖惩）；GRPO+PS > GRPO+OS（细粒度步骤信号更好）；迭代 RL 第 1 轮收益最大。
- **RL 为什么有效**（图 7）：RL 提升 **Maj@K 不提升 Pass@K** → 结论是 RL 主要"把 TopK 里本来就存在的正确答案顶上去"（输出分布更鲁棒/对齐），而非提升模型的根本能力。

---

## 5. 局限与后续

**论文自认局限**：①几何与定理证明弱于闭源模型（dry run 中三角形/椭圆题失败，暗示预训练与 SFT 数据选择偏差）；②受 7B 规模限制，few-shot 能力远逊 GPT-4（zero-shot ≈ few-shot，不会利用示例）；③arXiv 无效结论有三点保留（未测 informalization、未测混入其他数据、未测更大规模）。

**后续演进**：GRPO 成为 DeepSeek-R1（arXiv 2501.12948，2025）的核心训练算法（R1 去掉 RM、用 rule-based reward 的 GRPO 直接从 base 模型激发推理链），进而被 TRL（`GRPOTrainer`）、verl、OpenRLHF 等主流开源框架实现，是 2024-2025 年 LLM 推理 RL 事实标准；"组相对基线"思想与 RLOO/ReMax 等同属"无 critic 的 leave-one-out 均值基线"家族。社区亦有讨论：组内 std 归一化在 reward 全对/全错时数值不稳（后续实现常加 ε 保护）；Dr. GRPO（arXiv 2503.20783）指出按 $1/|o_i|$ 归一化会把"答错的长答案"的惩罚稀释、把"答对的长答案"的奖励放大，引入长度偏置，建议去掉 std 与长度归一化；DAPO（arXiv 2503.14476）则针对"全对/全错组梯度为零、样本浪费"提出动态采样。这些后续工作反过来说明原论文式 3 的两个设计选择（std 归一化、token 均值）是社区持续打磨的起点，而非终点。

---

## 6. 与代码的对照（论文概念 → 本仓文件）

**本仓（deepseek-ai/DeepSeek-Math）不含任何训练代码**——GRPO/预训练/SFT 均在内部框架完成；仓库定位是"模型发布 + 论文评测复现"。DeepWiki（work4ai/讲透DeepSeek-Math/deepwiki/2.4-rl-model.md）亦明确佐证："the exact implementation details of GRPO are not explicitly documented in the repository"。

| 论文概念 | 本仓位置 |
|---|---|
| 三阶段模型 Base/Instruct/RL + 数据管线五步（§2.1 图 2） | `README.md` §1/§3/§4（HF 权重表、5 步语料流程文字版） |
| CoT 评测 prompt（"...reason step by step...\\boxed{}"，§3.2） | `README.md` §5 + `evaluation/run_subset_parallel.py: markup_question()`（中英文模板原样落地） |
| TIR 评测 prompt（"integrate natural language reasoning with programs"） | `evaluation/run_subset_parallel.py`（同函数，tool 分支） |
| CoT / PoT / TIR 三种评测模式（§2.3/§3） | `evaluation/infer/run_cot_eval.py`、`run_pal_eval.py`、`run_tool_integrated_eval.py` |
| PoT 程序执行判定（"The execution result is evaluated as the answer"） | `evaluation/eval/python_executor.py`（`PythonInterpreter.exec_code/eval_code` 沙箱）+ `eval_utils.py: extract_program/run_execute` |
| 答案等价判定（MATH 答案可以是 LaTeX 符号等价） | `evaluation/eval/eval_utils.py: math_equal/symbolic_equal`（sympy `parse_latex` + `N`/`simplify` 数值/符号双通道，带 1s 超时） |
| 各 benchmark 判分逻辑 | `evaluation/eval/eval_script.py: eval_math / eval_mmlu_stem / eval_ocwcourses / eval_agieval_gaokao_math{cloze,qa}` |
| miniF2F-Isabelle 形式化评测（§2.3 Formal Mathematics） | `evaluation/unsafe_score_minif2f_isabelle.py`（需 PISA server，`--eval-atp` 触发） |
| 论文 9 个 benchmark 数据 | `evaluation/datasets/{gsm8k, math, mmlu_stem, sat, ocw, agieval, cmath, mgsm_zh, minif2f}` |
| 评测编排（论文全部表格的复现入口） | `evaluation/submit_eval_jobs.py`（多 GPU 分片）→ `run_subset_parallel.py` → `summarize_results.py`（聚合出 `evaluation_results.json`） |
| GRPO 训练实现 | **不在本仓**；开源等价实现：TRL `GRPOTrainer`、verl、OpenRLHF |

---

## 7. 学习路径

**前置知识**：policy gradient 与 REINFORCE → PPO 的 clip 目标与 GAE（读 Schulman 2017/2015）→ RLHF 流程（InstructGPT, arXiv 2203.02155：policy/reference/RM 三件套与 KL-in-reward）。

**精读顺序**：§2.1 语料管线（理解 fastText 迭代召回，对照 README §3）→ Table 1/8 语料对比实验（建立"数据质量 > 数据直觉"的证据链）→ §4.1.1 手推式 1→3（PPO 到 GRPO 只改两处：组平均基线 + KL 入 loss）→ 式 4 KL 估计器（$u-\log u-1$ 非负性一页纸可证）→ §4.1.2/4.1.3 两种监督的 advantage 公式 → 附录 A.1 式 5/21 统一范式（一张 Table 10 串起 SFT/RFT/DPO/PPO/GRPO）→ §5.2 讨论三节（在线>离线、分级奖惩>0/1、Maj@K≠Pass@K）。

**复现建议**：①无需重训 7B——用 HF 上的 `deepseek-math-7b-rl` 跑本仓 `evaluation/` 全流程（`submit_eval_jobs.py` → `summarize_results.py`）即可复现 Table 5；②GRPO 最小复现：TRL `GRPOTrainer` + Qwen2.5-1.5B/7B-Instruct + GSM8K train split，rule-based reward（答案对=1 错=0，等价于 outcome supervision），G=8~16、β=0.04 起步，观察组内 z-score advantage 与 Maj@4/Pass@4 的分离现象；③语料管线复刻：OpenWebMath 作种子 + fastText 二分类，在 1-2% 规模 CC 切片上走一遍四轮迭代，体会"域统计+人工 URL 标注"的收敛过程。

---

### 附：2310.06786 OpenWebMath 简评（种子语料，一段带过）

OpenWebMath（Paster et al., 2023-10，14.7B token）是 DeepSeekMath 语料管线的**第一轮正例种子**：从 Common Crawl 抽取数学网页，贡献点是"忠实保留 LaTeX 记号的 HTML→文本抽取管线"（boilerplate 去除 + fastText 质量过滤 + 去重），1.4B 小模型在其 14.7B token 上训练即超过 20 倍量级通用语料的效果。它证明了 CC 数学网页的价值上限，DeepSeekMath 则用迭代分类器把这条路线放大 9 倍（120B vs 13.6B token）并给出更强的下游验证——两者是"种子→放大"的直接继承关系。

---

*生成：2026-09-04 · 基于 arXiv 2402.03300v3 HTML 全文 + 本地仓（README/evaluation 源码）+ DeepWiki 2.4-rl-model 抽查*
