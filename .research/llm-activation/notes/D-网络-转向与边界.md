# D 网络资源层：激活转向 × 涌现争论 × RLVR 能力边界

> 用途：《激活大语言模型能力-总结卡》补网络资源层
> 抓取方式：webfetch 直抓 arXiv abs 页 / arXiv API 元数据 / Anthropic 官方页
> 抓取日期：2026-08-15（所有"v?/更新日期"以抓取时 arXiv 页面为准）

## 抓取成败清单

| # | 目标 | 结果 |
|---|------|------|
| 1 | arXiv:2212.04000（ActAdd） | **[ID 有误]** 该 ID 实为格点量子场论论文（Risch & Schaefer & Sommer, hep-lat, "The influence of gauge field smearing on discretisation effects"）。ActAdd 原文（Turner/Michaud et al., 2022-12，Alignment Forum 首发）未以该 ID 上 arXiv；arXiv API 全字段检索 "Activation Addition"+"without optimization" 亦 0 命中 → 按规则换同族后继 CAA（arXiv:2312.06681，含 ActAdd 谱系作者 Turner） |
| 2 | arXiv:2310.01405（RepEng） | ✅ 成功（v4, 2025-03-03） |
| 3 | arXiv:2306.03341（ITI） | ✅ 成功（v6, 2024-06-26, NeurIPS 2023 spotlight） |
| 4 | arXiv:2304.15004（涌现之辩） | ✅ 成功（v2, 2023-05-22） |
| 5 | arXiv:2504.13837（RLVR 边界） | ✅ 成功（v5, 2025-11-24, NeurIPS 2025 Oral） |
| 6 | Anthropic 可解释性 | ✅ 成功（tracing-thoughts 博文 + attribution graphs 双论文，2025-03-27） |
| 补 | arXiv:2303.13506（Quantization Model） | ✅ 顺带抓到（API 检索命中），作为涌现争论"真相变论"方补充 |

---

## 1. 激活转向（换源）：CAA — Steering Llama 2 via Contrastive Activation Addition

**来源**：https://arxiv.org/abs/2312.06681（arXiv API 元数据，v4 2024-07-05）
**论文**：Steering Llama 2 via Contrastive Activation Addition — Panickssery, Gabrieli, Schulz, Tong, Hubinger, **Turner**（Anthropic 系；Turner 即 ActAdd/activation engineering 谱系发起人）

**要点**
1. **残差流加性干预的数学形式**：对正/负行为样本对（如"忠实回答 vs 幻觉回答"）取残差流激活差值的均值得到 steering vector `v`；推理时在用户 prompt 之后的**所有 token 位置**加 `α·v`，α 可正可负，连续调节行为强度——权重完全不动。
2. 在 Llama-2-Chat 的多选行为数据集 + 开放生成任务上显著改变模型行为；效果**叠加在微调与 system prompt 之上**，且能力损失极小（"minimally reduces capabilities"）。
3. 谱系定位：ActAdd（2022-12）用单对前后缀的激活差；CAA 把它升级为**数据集级对比均值**，更稳健，并用多种激活空间解释方法反推高层概念在 LLM 中的表征方式。
4. 2025 后续（本次顺带抓到）：FGAA（arXiv:2501.09929，v3 2025-04-02）把转向搬进 **SAE 稀疏特征空间**，在 Gemma-2-2B/9B 上优于 CAA、SAE decoder steering、SAE-TS——转向已与稀疏可解释性合流。
5. 局限：转向强度 vs 通用能力的 tradeoff 在所有被测方法中一致存在（FGAA 摘要印证）。

**可信度**：高（arXiv 正式条目、四轮修订、代码可复现；ActAdd 原文本体未能抓取，此处经其后继论文转述其思想，已标注）

---

## 2. RepEng：Representation Engineering — A Top-Down Approach to AI Transparency

**来源**：https://arxiv.org/abs/2310.01405（v4 2025-03-03）
**论文**：Andy Zou 等 21 位作者（CMU/Berkeley/MITS 等，含 Dan Hendrycks、Dawn Song、Zico Kolter）

**要点**
1. **命名并系统化 RepE 领域**：借鉴认知神经科学，把分析单元从神经元/circuit 上移到"**群体级表征**"（population-level representations）——概念在激活空间中是一等公民。
2. **Top-down 路线**：先声明高层概念（诚实、无害、公平、权力寻求……），再读出（reading）/操纵（steering）其在残差流中的方向；与自底向上的 neuron→circuit 路线互补。
3. 展示了 monitor + manipulate 双向能力：同一套概念方向既可**监视**模型内部状态，又可在推理时**注入**控制行为——覆盖一系列安全相关任务。
4. 主张这是"top-down transparency"研究纲领的基线工作，代码开源（github.com/andyzoujm/representation-engineering），v4 到 2025-03 仍在修订。
5. 注意：摘要未给具体 benchmark 数字（如 TruthfulQA 提升幅度），总结卡引用时应回原文核对，避免转引失真。

**可信度**：高（领域命名论文、超21作者、社区广泛引用；具体数字需回原文核实）

---

## 3. ITI：Inference-Time Intervention — Eliciting Truthful Answers from a Language Model

**来源**：https://arxiv.org/abs/2306.03341（v6 2024-06-26；NeurIPS 2023 spotlight）
**论文**：Kenneth Li, Oam Patel, Fernanda Viégas, Hanspeter Pfister, Martin Wattenberg（Harvard）

**要点**
1. **机制**：用探针在少量 attention heads 上定位"真实性方向"，推理时把激活沿该方向平移（shifting activations across a limited number of attention heads）——比全层残差流转向更**局部**。
2. **量化结果**：Alpaca 在 TruthfulQA 上真实性 32.5% → 65.1%（摘要原文数字）。
3. **真实性-有用性 tradeoff**：两者此消彼长，通过调节干预强度取得平衡——转向系数是连续旋钮，不是开关。
4. **数据效率**：几百个样本即可定位 truthful 方向（对比 RLHF 需要大规模标注）；最小侵入、计算开销极低。
5. **核心洞察（对总结卡最关键）**："LLMs may have an internal representation of the likelihood of something being true, even as they produce falsehoods on the surface"——模型内部已有真假表征，表面输出错误只是"没触发对的能力"。这是"激活=触发已有能力"论点的最早实证之一。

**可信度**：高（NeurIPS spotlight，可复现，作者为可视化/可解释性名家）

---

## 4. 涌现争论：度量伪影论 vs 真相变论

### 4a. Are Emergent Abilities of Large Language Models a Mirage?（度量伪 artifact 论）

**来源**：https://arxiv.org/abs/2304.15004（v2 2023-05-22）
**论文**：Rylan Schaeffer, Brando Miranda, Sanmi Koyejo（Stanford）

**要点**
1. 涌现的"锐利性+不可预测性"两特征可由**研究者选择的度量**解释：对固定模型输出，非线性/不连续度量（如 exact match 的 0/1 判定）制造出"瞬间出现"的假象；换线性/连续度量后性能随规模**平滑、连续、可预测**。
2. 三路验证：(1) 在 InstructGPT/GPT-3 家族上对"已宣称涌现"任务做出并验证 3 个度量预测；(2) BIG-Bench 涌现元分析验证 2 个度量预测；(3) 在视觉任务上**人为制造出**从未见过的"伪涌现"。
3. 结论：所谓涌现能力"随不同度量或更好统计而蒸发"，未必是 scaling 的基本性质。

### 4b. 补充：The Quantization Model of Neural Scaling（真相变论方的机制模型）

**来源**：https://arxiv.org/abs/2303.13506（v3 2024-01-13；NeurIPS 2023；本次 API 检索顺带抓到）
**论文**：Eric J. Michaud, Ziming Liu, Uzay Girit, Max Tegmark（MIT）

**要点**
1. 量化假设：网络知识与技能被"量子化"为离散 chunk（**quanta**），按使用频率降序学习。
2. quanta 使用频率的幂律 → 同时解释 loss 幂律与**随规模的突变式能力出现**——给"真相变论"提供了能同时拟合两类现象的机制模型。
3. 用语言模型梯度自动把行为分解为技能 quanta，初步发现其频率分布近似幂律（与经验 scaling 指数对应）。

### 2024 后争论现状 [基于上两源+2504.13837 的推断，非独立抓取]
- **方法论层面已收敛**：度量敏感成常识——大 k pass@k 平滑曲线已成能力边界标准探针（2504.13837 全文即以此为方法 论，NeurIPS 2025 Oral 通过评审即为旁证）。
- **本体层面仍开放**：伪影论与相变论从对立走向调和——"能力确实按离散 chunk 习得（quanta），但其'突然性'部分是 0/1 度量放大"。专门综述本次未抓取（未竟事项）。

**可信度**：4a 高（NeurIPS 2023，引用量极大的"反对派旗舰"）；4b 高（NeurIPS 2023）；现状段为推断，已显式标注

---

## 5. RLVR 能力边界：Does RL Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?

**来源**：https://arxiv.org/abs/2504.13837（v5 2025-11-24；**NeurIPS 2025 Oral**；ICML 2025 AI4MATH workshop best paper）
**论文**：Yang Yue, Zhiqi Chen, Rui Lu, Andrew Zhao, Zhaokai Wang, Yang Yue, Shiji Song, Gao Huang（清华，高焕组）

**要点**
1. **pass@k 探针设计**：跨模型族、RL 算法、数学/代码/视觉推理 benchmark，用**大 k 的 pass@k** 系统探测 RLVR 训练后模型的能力边界。
2. **核心发现**：RLVR 模型在小 k（如 k=1）胜过基座，但 **k 大时基座 pass@k 反超**——现行训练设定未激发根本性的新推理模式。
3. **coverage + perplexity 分析**：观测到的推理能力**源自基座且被基座上界限定**；把基座当上界做量化分析，6 种主流 RLVR 算法表现相近，且都远未吃满基座潜力。
4. **对照组**：蒸馏可从教师模型引入新推理模式，**真正扩展**模型推理能力——与 RLVR 形成鲜明反差。
5. **与"R1 涌现说"的张力**：DeepSeek-R1 报告叙事是"RL 涌现反思/验证等新行为"，本文主张现行 RLVR 是**放大/提纯基座已有 pass@k 覆盖**（pass@1↑），而非扩展边界；作者呼吁持续 scaling、多轮 agent-环境交互等新 RL 范式才可能兑现"RL 造新能力"。与涌现争论呼应：pass@1 是 0/1 式"锐利度量"，pass@k 才显平滑真相。

**可信度**：高（NeurIPS 2025 Oral，五轮修订，跨族/跨算法/跨 benchmark 系统实验；注意"边界"以可验证奖励域——数学/代码/视觉推理——为限，外推到开放域需谨慎）

---

## 6. 可解释性视角：Anthropic Attribution Graphs（"AI 显微镜"）

**来源**：https://www.anthropic.com/research/tracing-thoughts-language-model（2025-03-27 博文）
**论文**：Circuit tracing: Revealing computational graphs in language models（methods）+ On the biology of a large language model（biology），transformer-circuits.pub/2025/attribution-graphs/；对象 Claude 3.5 Haiku

**要点**
1. **方法**：把稀疏可解释 feature 连成 attribution graphs（circuit 追踪），揭示输入→输出的部分计算路径——"能力以 circuit/feature 形式存在于权重"的可观测化。
2. **跨语言共享特征**：英/法/中激活同一"small/opposite/large"核心特征 circuit → 存在跨语言的"概念空间/思维语言"；且共享度随规模增长（3.5 Haiku 的跨语言共享特征比例是小模型的 2 倍以上）。
3. **提前规划 + 实时激活干预**：写诗第二行**之前**已激活候选韵脚词（如 rabbit）；**减去 rabbit 概念**后模型改写为押 "habit" 的行，**注入 green 概念**则改写为以 green 结尾——feature 级干预实时改写计划，circuit 因果性的直接演示。
4. **心算双路径**：36+59 由"近似估计"与"末位精确"两条并行路径合成；但模型自述用的是学校教的竖式进位法——**实际内部策略 ≠ 自述**，CoT 忠实性存疑（动机性推理案例：先有结论再造中间步骤）。
5. **幻觉机制**：默认存在一个常开的"拒答 circuit"，已知实体（Michael Jordan）的特征会抑制它；人工激活"已知答案"特征可**稳定诱发**对虚构人物（Michael Batkin）的幻觉——幻觉是 known-answer circuit 的自然误触发。
6. **自认局限**：只覆盖短 prompt 的部分计算、工具有伪影、每例需数小时人工分析——不能外推为"已完全看懂模型"。

**可信度**：高（Anthropic 官方、实验可验证、干预因果清晰；但 transformer-circuits 为自出版平台，未经传统同行评审）

---

## 对四层谱系的增量结论（≤5 条）

1. **L1 应分叉出"白盒激活"新分支**：prompt 工程（黑盒激活）之外，ITI/CAA/RepE 同样不动权重、推理期生效，但直接操作残差流方向向量（`a ← a + αv`），且数据效率极高（ITI：数百样本）——四层谱系中激活层宜拆为"黑盒激活（prompt）/白盒激活（steering）"两支。
2. **"能力存于权重、激活只是触发"拿到因果证据链**：ITI（真假方向存在）→ CAA（方向可数据集化、跨行为泛化）→ Anthropic attribution graphs（circuit 级因果：实时干预改写写诗计划、稳定诱发/消除幻觉）——与"基座是能力载体"假设一致，但载体形态是 **feature/circuit 而非单神经元**（RepE 群体表征观、2025 后 SAE 特征空间转向）。
3. **涌现争论 2024+ 落点：方法论收敛、本体调和**：大 k pass@k 平滑曲线成能力探针标准（2504.13837 即用）；"能力按离散 quanta 习得 + 突变性部分来自 0/1 度量放大"成为伪影论与相变论的调和点 [推断，基于 2303.13506 + 2504.13837]。
4. **RLVR 边界之争改写 RL 层定位**：RLVR ≈ 基座 pass@k 覆盖内的**分布收缩/提纯**（pass@1↑、边界不扩），真正扩边界的已验证通道是**蒸馏**与持续 scaling——"R1 涌现说"宜降格为"RL 显影说"（把基座已覆盖的能力显影到 pass@1）。
5. **白盒激活与 mech interp 正在合流**：2025 年转向进入 SAE 特征空间（FGAA），Anthropic 把 feature 串成 circuit 图——"特征级读出+干预"成为共同技术栈，总结卡中激活层与可解释性层应交叉引用而非并列隔离。

## 未竟事项（下次抓取建议）

- ActAdd 原文（Alignment Forum/LessWrong 版）未抓——用户给的 arXiv:2212.04000 为无关论文，直接抓 forum URL 可补
- 2024 后涌现争论专门综述未抓；RLVR 边界之争的反方（如 Apple/DeepSeek 后续回应、pass@k 之外的探索宽度指标）未抓
- transformer-circuits.pub/2023/monosemantic-early 未抓（本主题已被 2025 attribution graphs 覆盖，优先级低）
