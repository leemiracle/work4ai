# DeepSeek-R1 论文深度解读：纯 RL 激发 LLM 推理能力

> 论文：DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
> arXiv: [2501.12948](https://arxiv.org/abs/2501.12948)（v1 2025-01-22，v2 2026-01-04）· 正式刊登 **Nature 645: 633-638 (2025)** · 团队 DeepSeek-AI（200 人署名）
> 本地仓：`~/ai/explore/deepseek-ai/DeepSeek-R1`（模型发布仓，随仓附论文 PDF 原件 `DeepSeek_R1.pdf`，MIT 协议）

---

## 1. 一句话定位

**DeepSeek-R1 首次公开验证：不依赖任何人工标注的推理轨迹（无 SFT 冷启动），仅靠大规模强化学习 + 可验证奖励，就能让基础模型自发涌现反思、验证、长链思考等推理行为，最终追平 OpenAI-o1-1217，并把这种能力以蒸馏方式普惠到 1.5B-70B 小模型。**

发表时间线：v1 于 2025 年 1 月 22 日（农历春节前）横空出世，一天内引爆全球 AI 圈与资本市场；2025 年经同行评审刊登于 Nature（v2 为 Nature 修订版）。这是 DeepSeek 继 V3 之后的"第一代推理模型"（R1-Zero 与 R1 双型号），也是开源推理模型的分水岭之作。

## 2. 动机与痛点：此前的 test-time scaling 范式卡在哪

论文引言点名的时代背景：OpenAI o1 率先证明**推理时扩展（inference-time scaling）**——拉长 Chain-of-Thought（CoT）就能大幅提升数学/代码/科学推理，但 o1 技术闭源，社区复现路径全部碰壁：

- **过程奖励模型 PRM**（Lightman et al. 2023; Math-Shepherd）：需要为每一步推理打分，标注贵且定义模糊；
- **RL 自我纠错**（Kumar et al. 2024）：依赖监督数据，效果有限；
- **搜索算法 MCTS/Beam Search**（AlphaZero-like、AlphaGeometry 系）：搜索空间爆炸，价值模型难训。

共同软肋：**推理能力=人工示范的函数**。要么蒸馏 o1 的 CoT 数据，要么堆人工标注，没有一个公开方法达到 o1 级别。DeepSeek 的反问是：如果只给模型"答对给分"的规则信号，推理能力会不会自己长出来？——R1-Zero 给出肯定答案，这就是标题中 "Incentivizing"（激发/激励）一词的本意：**推理能力原本就潜伏在基础模型里，RL 只是激发它**。

## 3. 核心方法：三段式创新

### 3.1 DeepSeek-R1-Zero：基座上的纯 RL（无 SFT）

直觉：把 DeepSeek-V3-Base 当白纸，只用最弱的格式约束模板（Table 1：`<think>推理过程</think><answer>答案</answer>`），奖励完全由规则判定，观察模型自然演化。

**算法：GRPO（Group Relative Policy Optimization）**，出自自家 DeepSeekMath（Shao et al. 2024, arXiv:2402.03300）。核心改进是砍掉 PPO 中与策略模型同尺寸的 critic 网络，用**组内相对排名**估计 baseline（advantage）：

$$
J_{GRPO}(\theta) = \mathbb{E}\Big[q \sim P(Q),\ \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}\Big]\Big[\frac{1}{G}\sum_{i=1}^{G}\Big(\min\big(\rho_i A_i,\ \mathrm{clip}(\rho_i, 1-\varepsilon, 1+\varepsilon)A_i\big) - \beta\, D_{KL}(\pi_\theta \| \pi_{ref})\Big)\Big]
$$

其中重要性采样比 $\rho_i = \pi_\theta(o_i|q)/\pi_{\theta_{old}}(o_i|q)$，KL 项用非负无偏估计量 $D_{KL} = \frac{\pi_{ref}(o_i|q)}{\pi_\theta(o_i|q)} - \log\frac{\pi_{ref}(o_i|q)}{\pi_\theta(o_i|q)} - 1$（不直接约束每个 token，防过度保守）。advantage 由同组 $G$ 个采样的奖励归一化而来：

$$
A_i = \frac{r_i - \mathrm{mean}(\{r_1,\dots,r_G\})}{\mathrm{std}(\{r_1,\dots,r_G\})}
$$

直觉解释：同一道题采样 G 份答案，**比组内平均好就加强、差就抑制**——无需 value network 即获得相对信号，显存与计算开销近乎减半，这是 671B MoE 能跑得起大规模 RL 的工程前提。

**奖励设计：极简规则奖励（rule-based）**，仅两类——① accuracy reward：数学题按 `\boxed{}` 定格式规则判对错、LeetCode 用编译器+测试用例判通过；② format reward：强制思考过程包在 `<think></think>` 内。**刻意不用神经奖励模型**（无论 outcome 还是 process RM）：大规模 RL 下必然 reward hacking，且重训 RM 让管线复杂化——这一"做减法"的判断后来被社区广泛效仿。

**涌现结果**：AIME 2024 pass@1 从 15.6% 稳步爬到 71.0%（cons@64 达 86.7%，超过 o1-0912 的 83.3%）；响应长度（thinking time）随训练自发增长到数千 token；**aha moment**——中间版本模型在解 $\sqrt{a-\sqrt{a+x}}=x$ 时自己输出 "Wait, wait. Wait. That's an aha moment I can flag here." 然后推翻重来。反思（reflection）、自我验证、换策略等行为**均非人工设计，而是奖励信号下自发涌现**。代价：可读性差、中英混杂、偶尔无限重复。

### 3.2 DeepSeek-R1：冷启动 + 四阶段 pipeline

针对 R1-Zero 的缺陷，R1 采用"两次 RL + 两次 SFT"四阶段流水线：

1. **Cold Start**：数千条长 CoT 数据（few-shot 长 CoT 示例、带反思验证的直接生成、R1-Zero 可读格式输出再人工精修）微调 V3-Base，格式定义为 `|special_token|<reasoning_process>|special_token|<summary>`——推理给模型看、摘要给人看。
2. **Reasoning-oriented RL**：同 R1-Zero 的大规模规则奖励 RL，新增**语言一致性奖励**（CoT 中目标语种词占比），与 accuracy 直接相加。消融显示该奖励带来轻微性能下降，但换来人类可读性——明确的 alignment trade-off。
3. **Rejection Sampling + SFT**：RL 收敛后，从 checkpoint 拒绝采样生成推理数据（每题采多答只留对的，滤掉语言混杂/超长段落/乱码，辅以 DeepSeek-V3 做 generative reward model 判分），约 **600k 推理样本**；非推理数据（写作/事实 QA/自我认知/翻译）复用 V3 管线约 **200k**。合计 **800k 样本对 V3-Base 重训 2 个 epoch**。
4. **RL for all Scenarios**：第二轮 RL 同时服务推理与通用对齐——推理数据仍用规则奖励；通用数据用 reward model 捕捉人类偏好。细节设计：helpfulness 只评估最终 summary（不干扰思考过程），harmlessness 评估全响应。

### 3.3 蒸馏：大模型的推理模式 > 小模型自己 RL

用 800k 样本直接 SFT 六个开源 dense 模型（Qwen2.5-Math-1.5B/7B、Llama-3.1-8B、Qwen2.5-14B/32B、Llama-3.3-70B-Instruct），**只做 SFT 不做 RL**。对照实验（Table 6）：Qwen-32B-Base 自己做 10K+ 步大规模 RL 得 R1-Zero-Qwen-32B（AIME 47.0），被蒸馏版 R1-Distill-Qwen-32B（AIME 72.6）碾压。结论两条：**① 强模型的推理模式可廉价高效地蒸给小模型；② 但要突破智能边界，仍需更强基座 + 更大规模 RL**——蒸馏与 RL 不是替代而是互补。

## 4. 实验与结果：关键数字

评测协议：temperature 0.6、top-p 0.95、最大生成长度 32,768 token、pass@1 由 4-64 次采样平均（greedy 会导致重复且跨 checkpoint 方差大）。LLM 裁判类（AlpacaEval 2.0/ArenaHard）只喂最终 summary 避免长度偏置。

**R1 vs 旗舰（论文 Table 4 摘录）**：

| Benchmark | DeepSeek-V3 | o1-mini | o1-1217 | **DeepSeek-R1** |
|---|---|---|---|---|
| AIME 2024 (pass@1) | 39.2 | 63.6 | 79.2 | **79.8** |
| MATH-500 (pass@1) | 90.2 | 90.0 | 96.4 | **97.3** |
| Codeforces (Percentile) | 58.7 | 93.4 | 96.6 | 96.3（rating 2029） |
| GPQA Diamond | 59.1 | 60.0 | 75.7 | 71.5 |
| MMLU / MMLU-Pro | 88.5 / 75.9 | 85.2 / 80.3 | 91.8 / – | 90.8 / **84.0** |
| SWE-bench Verified | 42.0 | 41.6 | 48.9 | 49.2 |
| AlpacaEval 2.0 (LC) | 70.0 | 57.8 | – | **87.6** |

要点：数学追平/反超 o1-1217；代码竞技场 96.3 百分位=专家水平但 rating 略输（2029 vs 2061）；知识类（MMLU/GPQA）仍逊 o1-1217；开放式写作大比分领先（受益于第二阶段全场景 RL）。一个值得注意的副作用：safety RL 后 C-SimpleQA 从可超 70% 掉到 63.7（模型倾向拒答），论文坦承。

**蒸馏家族（Table 5 摘录，AIME 2024 pass@1 / cons@64）**：Distill-Qwen-1.5B **28.9**/52.7（超 GPT-4o 的 9.3 与 Claude-3.5-Sonnet 的 16.0）；7B 55.5/83.3（超 QwQ-32B-Preview）；14B 69.7/80.0；32B **72.6**/83.3（超 o1-mini 的 63.6，MATH-500 达 94.3、LiveCodeBench 57.2）；Llama-70B 70.0/**86.7**。1.5B 手机级模型在数学上打赢 2024 年旗舰，是当时传播最广的爆点。

## 5. 局限与后续

**论文自认局限（§5）**：① 通用能力不及 V3——function calling、多轮、复杂角色扮演、JSON 输出；② 中英双语之外仍会语言混杂；③ 对 prompt 敏感，few-shot 一致性降低性能，推荐 zero-shot 直述问题；④ 软件工程任务提升有限（长评测拖慢 RL，后续拟用拒绝采样+异步评测补齐）。

**失败经验分享（§4.2，社区称"负结果比正结果更宝贵"）**：PRM 三宗罪（细粒度 step 难定义、中间步正误难判、RM 引入 reward hacking）；MCTS 两宗罪（token 生成空间远超棋类导致需截断→局部最优，value model 质量直接决定生成质量→自提升闭环难建立）。

**后续演进**（社区通识，供导航）：DeepSeek 侧：R1-0528 更新版（幻觉/工具调用改善）→ V3.1/V3.2-Exp（推理与通用合并为单模型 + DSA 稀疏注意力，本地 `explore/deepseek-ai/DeepSeek-V3.2-Exp` 仓可对照）；社区侧：GRPO 成为 verl/OpenRLHF/TRL 标准算法并衍生 DAPO、Dr.GRPO（去长度偏置）等变体；蒸馏潮（OpenThinker 等）直接引用本仓 800k 范式；"rule-based verifiable reward + RL"成为 post-training 时代事实标准（后被统称 RLVR）。

## 6. 与代码/仓库的对照

本仓是**模型发布仓**（权重 + 文档，不含训练代码——训练框架未开源），对照映射如下：

| 论文概念 | 本仓位置 / 实现 |
|---|---|
| R1-Zero & R1 模型（671B 总参 / 37B 激活 / 128K 上下文，V3-Base 基座） | `README.md` §3 Model Downloads 表（HF 权重链接）；架构明示"见 DeepSeek-V3 仓"（本地 `explore/deepseek-ai/DeepSeek-V3`，MLA + DeepSeekMoE 实现） |
| 六个蒸馏模型（§2.4，Qwen2.5/Llama3 系） | `README.md` §3 Distill 表：Qwen-1.5B/7B/14B/32B + Llama-8B/70B；注明"微调自 800k 样本，configs/tokenizers 有改动，须用官方设置" |
| Table 4/5 全部评测数字 | `README.md` §4 两张表 + `figures/benchmark.jpg`（论文 Figure 1 同款雷达柱状图） |
| Table 1 训练模板 `<think></think><answer></answer>` | `README.md` §6 Usage Recommendations：推理侧延续——建议强制输出以 `<think>\n` 开头（防空思考绕行）、数学题加 "put your final answer within \boxed{}"（即 accuracy reward 的判分格式）、temperature 0.5-0.7（0.6）防无限重复、**不要加 system prompt** |
| 第二阶段全场景 RL（web 搜索/文件场景） | `README.md` §6 Official Prompts：`search_answer_zh/en_template`（[citation:X] 引用规范）与 `file_template` 完整可读 |
| pass@1 评测协议（§3） | `README.md` §4："64 responses per query, temperature 0.6, top-p 0.95, max 32768" 逐字对应论文 §3 |
| 本地推理 | `README.md` §6：vLLM `vllm serve ... --tensor-parallel-size 2 --max-model-len 32768` / SGLang 启动命令；R1 本体需按 DeepSeek-V3 仓方式跑（当时 HF transformers 尚未原生支持） |
| GRPO 算法出处 | 引用 DeepSeekMath（arXiv:2402.03300）；本地 `explore/deepseek-ai/DeepSeek-Math` 仓 + `work4ai/讲透DeepSeek-Math` 可溯源 |
| 论文原文 | `DeepSeek_R1.pdf`（22 页 Nature 排版版） |
| 仓内知识图谱 | `.understand-anything/`（中文图谱，outputLanguage=zh，2 批扫描+layers，本仓仅 README/LICENSE/workflow 三类文件） |
| 开源协议 | MIT（含权重，明确允许商业使用与蒸馏再训练；Qwen 系蒸馏遵循 Apache 2.0、Llama 系遵循原协议） |

**勘误提示（数字漂移）**：`README.md` §4 表保留了 v1 时点数字，与随仓 Nature 修订版 PDF 存在少量出入——如 Claude-3.5 LiveCodeBench 33.8（README）vs 38.9（论文 Table 4）、GPT-4o 34.2 vs 32.9、QwQ-32B-Preview AIME 44.0（README）vs 50.0（论文 Table 5）。**引用数字以论文 PDF/Nature 版为准**。

**DeepWiki 对照**：`work4ai/讲透DeepSeek-R1/deepwiki/` 尚未抓取（本仓非代码仓，DeepWiki 价值有限），本报告的代码对照全部基于本地仓一手文件（README/PDF/figures/.understand-anything）实证。

## 7. 学习路径

**前置知识**：① PPO 基础（clip 目标、KL 约束、critic 的作用与代价）→ 才能体会 GRPO "组内相对优势"砍 critic 的妙处；② Transformer 推理架构：MLA、DeepSeekMoE（读 DeepSeek-V3 论文/本地讲透V3 笔记）；③ RLHF/SFT 常识（为什么 SFT 是"冷启动"）。

**精读顺序**（建议三天）：
1. §2.2 R1-Zero：GRPO 公式 (1)(2)(3) 手推一遍，对比 PPO 目标函数差异；细读 Table 1 模板与 aha moment 案例（Table 3）；
2. §2.3 R1 四阶段：画出 pipeline 流程图（cold start → reasoning RL → rejection sampling+SFT → all-scenario RL），标注每阶段数据来源与奖励类型；
3. §4 Discussion：Table 6（蒸馏 vs RL）+ §4.2 失败经验——这是全文最有工程含金量的部分；
4. 对照本仓 README 把 Table 4/5 数字与 Usage Recommendations 关联理解（训练协议如何映射为推理协议）。

**复现建议**（按算力梯度）：
- 单卡（24G+）：vLLM/SGLang 跑 `DeepSeek-R1-Distill-Qwen-7B`，按官方协议（temp 0.6/top-p 0.95/max 32768/强制 `<think>\n`）复测 AIME/MATH-500，体验 aha 式输出；
- 单机多卡：用 verl / OpenRLHF / TRL 的 `GRPOTrainer` 在 Qwen2.5-1.5B/7B 上复刻 R1-Zero 配方（GSM8K/MATH 规则奖励 + format reward），观察响应长度自发增长曲线；
- 进阶：做论文 Table 6 的迷你版——同基座"直接 RL vs 蒸馏"对照，验证"强基座推理模式"结论在小尺度是否成立；注意社区已知坑：GRPO 的长度偏置（std 归一化引入）与 Dr.GRPO 修正。

---

*生成于 2026-09-04 · 论文 arXiv 2501.12948（Nature 645:633-638）· 本地仓 commit 见 git log · 全文引用数字均出自随仓 PDF 与 README 实证核对*
