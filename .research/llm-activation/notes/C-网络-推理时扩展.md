# C-网络资源前沿层：推理时扩展 / 测试时计算（2024-2026）

> 任务：为《激活大语言模型能力-总结卡》补充网络资源前沿层。
> 代理：仅 webfetch（无搜索引擎），逐 URL 直抓。抓取日期：2026-08-15。
> 状态：6 源成功；huggingface.co 域名 3 次传输失败（博客×2 + 模型卡×1），已弃用并如实标注。

---

## 源 1｜s1: Simple test-time scaling（budget forcing）

- **来源**：https://arxiv.org/abs/2501.19393 ｜ Muennighoff, Yang, Shi, Li, Fei-Fei, Hajishirzi, Zettlemoyer, Liang, Candès, Hashimoto（Stanford/Berkeley 等）｜ 2025-01-31 v1, v3 2025-03-01
- **可信度**：高（arXiv 一手摘要页；模型/数据/代码全开源 github.com/simplescaling/s1）

**要点**：
1. **目标**：寻找 o1 之后最简 test-time scaling 复现路径——答案是"小数据 SFT + 采样干预"，不需要 RL。
2. **s1K 数据集**：仅 1,000 条问题+推理轨迹，按三条准则经消融验证筛选：难度（difficulty）、多样性（diversity）、质量（quality）。
3. **budget forcing 机制**：通过 (a) 强制终止思考 或 (b) 在模型试图结束时**多次追加 "Wait"** 强制延长思考，实现对测试时计算的直接控制；延长后模型会复查答案，常能修正错误推理步骤。
4. **关键数字**：Qwen2.5-32B-Instruct 在 s1K 上 SFT 得 s1-32B，竞赛数学（MATH 与 AIME24）**超 o1-preview 最多 27%**；budget forcing 把 AIME24 从 50% **外推**至 57%（超出无干预时的固有权重上限）。
5. **"1K > 10K"主张**：论文正文消融显示按三准则筛选的 1K 样本优于 10K 规模的朴素数据集（摘要未列具体数字）[未核实具体数值，仅摘要层面确认三准则经消融验证]。

---

## 源 2｜Scaling LLM Test-Time Compute Optimally（Snell et al.）

- **来源**：https://arxiv.org/abs/2408.03314 ｜ Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar（UC Berkeley/Google DeepMind）｜ 2024-08-06
- **可信度**：高（arXiv 一手摘要页；该文是 compute-optimal 推理的奠基引用，R1 论文 G.2 节直接引用）

**要点**：
1. **两条扩展机制**：(1) **并行**——针对稠密的过程奖励模型（process-based verifier）搜索（best-of-N + 打分）；(2) **顺序**——按提示在测试时自适应更新模型的响应分布（迭代修订）。
2. **核心发现**：两条机制的有效性**关键取决于提示难度**——不存在普适最优策略，动机是 compute-optimal 策略：按题自适应分配测试时算力。
3. **效率数字**：compute-optimal 策略比 best-of-N 基线**效率提升 >4x**。
4. **与小模型的关系**：FLOPs 对齐评估中，在小基模已有非平凡成功率的题目上，测试时计算可**胜过 14x 更大的模型**。
5. **曲线形态/交叉点**（正文结论，本次仅抓摘要页）[部分未核实]：顺序修订在较低预算/较易题上更优，并行搜索在高预算/难题上更优，最优策略随难度交叉移动——这是"难度条件化分配"主张的具体化。

---

## 源 3｜DeepSeek-R1：纯 RL 激励推理（GRPO / aha moment / 蒸馏 80 万）

- **来源**：https://arxiv.org/abs/2501.12948 及 HTML 全文 https://arxiv.org/html/2501.12948v2 ｜ DeepSeek-AI（Guo, Yang, Zhang, Song 等 200+ 作者）｜ v1 2025-01-22；v2 2026-01-04；**Nature 645:633-638 (2025)**
- **可信度**：高（一手 abs + 全文；全文 289KB 已本地存档并逐段核读）

**要点**：
1. **R1-Zero 纯 RL 涌现**：绕过 SFT 冷启动，直接在 DeepSeek-V3-Base 上 RL。AIME 2024 pass@1 从 15.6% → 77.9%，self-consistency（cons@16）达 86.7%，显著超人类参赛者平均水平。
2. **GRPO 细节**：每题采样一组（G=16）输出，**用组内奖励的均值/标准差归一化算优势**（省掉 PPO 的 value model），带 clip + KL 惩罚；lr 3e-6、KL 系数 0.001、rollout 温度 1；单输出上限 32,768 token（8.2k 步后 65,536）；共 10,400 步 ≈ 1.6 epoch。
3. **奖励设计**：纯规则奖励 = 准确性（数学答案框/编译器测例）+ 格式（`<think>`/`<answer>` 标签）；明确**不用神经奖励模型**（outcome 或 process 均不用），因大规模 RL 下易被 reward hacking。
4. **aha moment**：训练中模型反思时 "wait" 一词使用量突增（Table 2 原文案例："Wait, wait. Wait. That's an aha moment I can flag here."），伴随自我验证、回溯、换策略等行为自发涌现——无人教过。
5. **蒸馏 80 万条**：用 R1 生成约 **800,000** 条监督样本，SFT（2-3 epochs）到 Qwen/LLaMA 系小模型（只做 SFT 不做 RL）。Distill-Qwen-**1.5B** 数学即超非推理基线（GPT-4o/Claude-3.5-Sonnet）；**蒸馏 > 小模型直接大规模 RL**（Qwen2.5-32B-Zero 仅与 QwQ-32B-Preview 持平，Distill-Qwen-32B 全面胜出）。
6. **最终 R1 多阶段管线**：冷启动数据 → 推理 RL（+语言一致性奖励）→ 拒绝采样+SFT（80 万，推理+非推理混合）→ 第二阶段 RL（通用偏好 reward model）。终榜：AIME 79.8 / MATH-500 97.3 / Codeforces 96.3 百分位（rating 2029）。

**R1 自述失败模式/限制（G.1/G.2/§6，一手证据）**：
- **小模型上界**：7B dense / 16B MoE 纯 RL 在 AIME 上**无有效提升**（长 CoT 趋向重复）；32B/230B/671B 才见效——纯 RL 成效高度依赖底座容量。
- **PRM 失败**：细粒度步骤难定义、中间步正误难判定（自动标注差、人工不可扩展）、引入即 reward hacking——收益不抵开销。
- **MCTS 失败**：token 生成搜索空间指数级 > 棋类；value model 难训；节点扩展上限导致局部最优。AlphaGo 路线在 LLM 上难复刻。
- **overthinking**：简单题过度推理仍存在（token efficiency 段自述）。
- **两轴互补证据**：pass@64 = 90.0% > pass@1 = 79.8%；majority voting 再把 79.8% 抬到 86.7%——顺序长 CoT 之外并行采样仍有增益。
- 其他：结构输出/工具使用弱、中英外语言混杂、few-shot 提示反而降低性能。

---

## 源 4｜Inference Scaling Laws（compute-optimal 推理）

- **来源**：https://arxiv.org/abs/2408.00724 ｜ Yangzhen Wu, Zhiqing Sun, Shanda Li, Sean Welleck, Yiming Yang（CMU）｜ v1 2024-08-01, v3 2025-03-03
- **可信度**：高（arXiv 一手摘要页）。**勘误**：任务清单预期此号是"过程奖励模型综述"，实际标题为 *Inference Scaling Laws: An Empirical Analysis of Compute-Optimal Inference for Problem-Solving with Language Models*，已如实按实际论文记录。

**要点**：
1. 系统对比贪心、多数投票（majority voting）、best-of-n、加权投票、两种树搜索在不同模型尺寸与算力预算下的成本-性能权衡。
2. **结论一**：用推理策略扩展推理算力可比扩展模型参数**更计算高效**（与 Snell 独立同结论，互为印证）。
3. **结论二**：小模型 + 先进推理算法构成**Pareto 最优**（成本×性能）。
4. 代表数字：**Llemma-7B + 自研树搜索在 MATH 上全面超过 Llemma-34B**（所有测试策略下）。
5. 与源 2 的关系：Snell 用 PRM-verifier + 顺序修订（按题自适应），本文用更广策略族 + 统一 FLOPs 口径，两者共同确立"难度条件化 + 算力-参数可互换"这一 2024 下半年共识。

---

## 源 5｜OpenAI o1 官方发布页

- **来源**：https://openai.com/index/learning-to-reason-with-llms/ ｜ OpenAI ｜ 2024-09-12（一次抓取成功，未动用 Wikipedia 备胎）
- **可信度**：高（一手），但属**厂商自报**数字，横向对比时注意口径。

**要点**：
1. **方法定性**：大规模 RL 教模型"用思维链高效思考"；官方图显示性能随 **train-time compute 与 test-time compute 双轴平滑提升**——首次把测试时算力列为可扩展维度。
2. **AIME 2024**：GPT-4o 平均 12%（1.8/15）→ o1 单样本 pass@1 **74%**（11.1/15）→ cons@64 **83%** → **1000 样本 + 学习型打分重排 93%**（13.9/15，全美前 500、超 USAMO 门槛）——一条题内完整展示了"顺序 + 并行 + verifier"三段式推理时扩展。
3. **GPQA Diamond**：超人类 PhD 专家（该基准首个）；MMMU 78.2%（视觉开启，首个接近人类专家）。
4. **Codeforces**：GPT-4o Elo 808（11 百分位）→ o1 1673（89 百分位）→ o1-ioi 1807（93 百分位）；IOI 正规约束下 213 分（49 百分位），放宽到 10,000 次提交则 362.14 **超金牌线**——测试时算力预算直接改变"奖牌颜色"。
5. **隐藏思维链**：不向用户展示原始 CoT（监控对齐机会 vs 用户体验/竞争优势的权衡），只给模型生成的摘要——开源侧（R1/s1）与闭源侧的可复现性分水岭。
6. **负面信号**：人类偏好评测中 o1-preview 在数据分析/编码/数学大胜，但部分自然语言任务**不占优**——推理时扩展非万能。

---

## 源 6｜Overthinking 批评源：Do NOT Think That Much for 2+3=?

- **来源**：https://arxiv.org/abs/2412.21187 ｜ Xingyu Chen, Jiahao Xu, Tian Liang 等（腾讯 AI Lab / 上海交大等）｜ v1 2024-12-30, v2 2025-02-01
- **可信度**：高（arXiv 一手摘要页；v2 声明已补测 DeepSeek-R1 且结论不变）
- **抓取备注**：第一次请求超时，重试成功。

**要点**：
1. **首个系统研究 o1 类模型 overthinking**：对简单问题分配过量计算资源、边际收益极小（"2+3=?" 也长篇思考）。
2. 提出 **outcome 与 process 双视角效率指标**，量化"算力花得值不值"，而不仅看准确率。
3. 用 **self-training 范式**缓解 overthinking：在不损失精度的前提下精简推理过程（GSM8K / MATH500 / GPQA / AIME 全难度谱验证）。
4. 与 R1 论文自述的 overthinking 限制（源 3 要点 6）互为印证：这是 2025 年推理时扩展最公认的成本面批评。

---

## [抓取失败] HuggingFace 博客：DeepSeek-R1 open reasoning

- **来源**：https://huggingface.co/blog/deepseek-r1 ｜ 尝试 2 次
- **替代尝试**：模型卡 https://huggingface.co/deepseek-ai/DeepSeek-R1 亦失败
- **状态**：**[抓取失败]**（Transport error ×3，huggingface.co 域名整体不可达）。其内容（R1 复现、GRPO 图解、Open-R1 项目）与源 3 高度重叠，损失可控；如需补齐，建议日后网络恢复时单独重抓。

---

# 对激活能力四层谱系（L0 涌现 / L1 推理时 / L2 训练侧 / L3 架构接入）的增量结论

1. **L1 两条轴确证且可叠加**：并行采样（self-consistency / BoN + verifier）与顺序长 CoT 是可互换的计算轴（Snell compute-optimal 效率 >4x；CMU 独立同结论）；R1 上 pass@64（90.0%）仍高于 pass@1（79.8%）、majority voting 再 +6.9pt——顺序轴做强后并行轴仍有残余增益，两轴是"乘法"而非"或选"。
2. **L1 的上限由 L0 底座容量决定**：R1 自述 7B/16B 纯 RL 无效（长 CoT 退化为重复）；s1 的奇迹依赖 Qwen2.5-32B 强底座 + 仅 1K 精选数据。R1 结论原文点题：预训练检查点固有巨大推理潜势，解锁靠"难题 + 可靠 verifier + 足够 RL 算力"，而非人工标注——**推理时扩展激活的是 L0 已有潜势**。
3. **L2 是 L1 的放大器，且蒸馏是最经济的下沉通道**：GRPO + 规则奖励把推理行为内化进权重（aha moment 为标志）；80 万条 R1 蒸馏数据让 1.5B 模型数学超 GPT-4o，且蒸馏 > 小模型直接大规模 RL——L2 手段之间也有优劣分层。
4. **失败模式三件套构成边界**：(a) overthinking（腾讯 AI Lab 双指标实证，R1 自认）；(b) 成本（o1 的 93% 靠 1000 样本重排，IOI 金牌靠 10,000 次提交预算）；(c) 小模型/错误空间上界（PRM 步骤难定义、MCTS 在 token 空间难复刻 AlphaGo）。四层谱系中每往下一层（更多算力/更大训练），都受这三条约束反噬。
5. **机制极简性是 2025 年新共识**：budget forcing（追加 "Wait"）证明 L1 可被 <1K 数据 SFT + 纯采样干预激活——从 o1（闭源 RL）→ R1（开源 RL）→ s1（无 RL）的简化轨迹，说明"激活"的最低门槛在持续下降，谱系各层的准入成本随时间递减。

---

*refs: arXiv 2501.19393 / 2408.03314 / 2501.12948 (Nature 645:633-638) / 2408.00724 / 2412.21187 / openai.com o1 page*
