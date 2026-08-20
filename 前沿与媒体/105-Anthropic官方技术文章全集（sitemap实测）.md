# 前沿与媒体 · 105 - Anthropic 官方技术文章全集（sitemap 实测版）

> **数据口径**：2026-08-20 直接抓取 `https://www.anthropic.com/sitemap.xml`（515 个 URL，含 lastmod），全量提取 `/engineering/`(25) + `/research/`(153) + `/news/` 技术子集(约60) + 其他技术页(3)。**非记忆拼凑，是当日实测快照**——与网络流传的"知识库版"（截止 2025、缺整年）相比，本版含 2026 全部新篇。
> **说明**：描述一句话，熟篇按内容写，2026 新篇按 slug 语义忠实转述（不臆造）。
> **配套深读**：核心篇目全文精读卡 → [`106-Anthropic工程博客深读`](./106-Anthropic工程博客深读.md)（harness/agent 工程线 6 篇）与 [`107-Anthropic可解释性研究深读`](./107-Anthropic可解释性研究深读.md)（interp 前沿 4 篇）。全部 URL 前缀 `https://www.anthropic.com` 略。

---

## 一、Engineering 工程博客全集（25 篇，全技术）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2025-03 | [swe-bench-sonnet](https://www.anthropic.com/engineering/swe-bench-sonnet) | Sonnet 刷 SWE-bench 的工程复盘 |
| 2025-09 | [desktop-extensions](https://www.anthropic.com/engineering/desktop-extensions) | Claude Desktop 扩展开发 |
| 2025-11 | [claude-code-sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) | Claude Code 沙箱设计 |
| 2025-11 | [code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp) | MCP 服务器中安全的代码执行 |
| 2025-11 | [effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 长时运行 agent 的 harness 设计（本仓 harness工程手册已深读） |
| 2025-12 | [claude-think-tool](https://www.anthropic.com/engineering/claude-think-tool) | Think Tool：给模型一块"草稿空间" |
| 2025-12 | [a-postmortem-of-three-recent-issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) | 三次线上事故复盘 |
| 2026-01 | [claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) | Claude Code 最佳实践（官方） |
| 2026-01 | [effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 上下文工程：系统性地做"恰好够用的上下文" |
| 2026-01 | [multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) | 多 agent 研究系统（orchestrator+子agent，token 提效 90%+ 那篇） |
| 2026-01 | [writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 怎么给 agent 写工具（接口设计） |
| 2026-01 | [contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | 上下文检索：检索失败率降 49%（chunk 前缀上下文） |
| 2026-02 | [building-c-compiler](https://www.anthropic.com/engineering/building-c-compiler) | 用 Claude 写 C 编译器（57 分钟 13k+ commit 的实验） |
| 2026-03 | [advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use) | 高级工具使用模式（code execution/tool search/MCP 三件套） |
| 2026-03 | [demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | agent 评测去魅（怎么设计 pass/fail） |
| 2026-03 | [eval-awareness-browsecomp](https://www.anthropic.com/engineering/eval-awareness-browsecomp) | BrowseComp 与评测污染意识 |
| 2026-03 | [harness-design-long-running-apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 长时应用的 harness 设计（Memory/MCP/agent循环三支柱） |
| 2026-04 | [equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Agent Skills 与渐进披露（省 token 的开放标准） |
| 2026-04 | [infrastructure-noise](https://www.anthropic.com/engineering/infrastructure-noise) | 基础设施噪声排查 |
| 2026-04 | [managed-agents](https://www.anthropic.com/engineering/managed-agents) | 托管 agent 模式 |
| 2026-05 | [claude-code-auto-mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | Claude Code 自动模式（权限分级） |
| 2026-01→ | [building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) | **必读经典**：workflow vs agent 五模式（持续更新至 2026-08） |
| 2026-04 | [april-23-postmortem](https://www.anthropic.com/engineering/april-23-postmortem) | 4·23 事故复盘 |
| 2026-06 | [how-we-contain-claude](https://www.anthropic.com/engineering/how-we-contain-claude) | 怎么"关住"Claude（agent 遏制工程） |
| 2026-01 | [AI-resistant-technical-evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) | 抗 AI 技术面试设计 |

---

## 二、Research 研究文章全集（153 篇，按主题分组）

### A. 可解释性 / 机制可解释性（约 25 篇， Anthropic 招牌）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2024-08 | [transformer-circuits](https://www.anthropic.com/research/transformer-circuits) | Transformer Circuits 系列总站 |
| 2024-08 | [a-mathematical-framework-for-transformer-circuits](https://www.anthropic.com/research/a-mathematical-framework-for-transformer-circuits) | Transformer 电路的数学框架（一期） |
| 2024-08 | [in-context-learning-and-induction-heads](https://www.anthropic.com/research/in-context-learning-and-induction-heads) | 归纳头与 in-context learning |
| 2024-08 | [toy-models-of-superposition](https://www.anthropic.com/research/toy-models-of-superposition) | 超叠加玩具模型（经典） |
| 2024-12 | [towards-monosemanticity-decomposing-language-models-with-dictionary-learning](https://www.anthropic.com/research/towards-monosemanticity-decomposing-language-models-with-dictionary-learning) | Towards Monosemanticity：字典学习分解（SAE 开山） |
| 2024-08 | [decomposing-language-models-into-understandable-components](https://www.anthropic.com/research/decomposing-language-models-into-understandable-components) | 分解模型为可理解组件 |
| 2024-12 | [softmax-linear-units](https://www.anthropic.com/research/softmax-linear-units) | SoLU 激活函数与可解释性 |
| 2024-12 | [privileged-bases-in-the-transformer-residual-stream](https://www.anthropic.com/research/privileged-bases-in-the-transformer-residual-stream) | 残差流的特权基 |
| 2024-12 | [superposition-memorization-and-double-descent](https://www.anthropic.com/research/superposition-memorization-and-double-descent) | 超叠加·记忆·双下降 |
| 2024-12 | [scaling-laws-and-interpretability-of-learning-from-repeated-data](https://www.anthropic.com/research/scaling-laws-and-interpretability-of-learning-from-repeated-data) | 重复数据学习的缩放律 |
| 2024-12 | [influence-functions](https://www.anthropic.com/research/influence-functions) + [studying-large-language-model-generalization-with-influence-functions](https://www.anthropic.com/research/studying-large-language-model-generalization-with-influence-functions) | 影响函数两篇 |
| 2024-06 | [engineering-challenges-interpretability](https://www.anthropic.com/research/engineering-challenges-interpretability) | 可解释性的工程挑战 |
| 2024-10 | [features-as-classifiers](https://www.anthropic.com/research/features-as-classifiers) | 特征当分类器（线性探针） |
| 2024-12 | [interpretability-dreams](https://www.anthropic.com/research/interpretability-dreams) | 可解释性愿景（2019 老文归档） |
| 2025-02 | [crosscoder-model-diffing](https://www.anthropic.com/research/crosscoder-model-diffing) | CrossCoder：跨模型 diff 权重变化 |
| 2025-05 | [open-source-circuit-tracing](https://www.anthropic.com/research/open-source-circuit-tracing) | 开源电路追踪（Circuit Tracing 工具） |
| 2025-11 | [predictability-and-surprise-in-large-generative-models](https://www.anthropic.com/research/predictability-and-surprise-in-large-generative-models) | 生成模型的可预测性与惊讶 |
| 2026-06 | [natural-language-autoencoders](https://www.anthropic.com/research/natural-language-autoencoders) | 自然语言自编码器（SAE 特征的语言化） |
| 2026-07 | [mapping-mind-language-model](https://www.anthropic.com/research/mapping-mind-language-model) | Mapping the Mind：百万级特征图谱（科普版） |
| 2026-07 | [tracing-thoughts-language-model](https://www.anthropic.com/research/tracing-thoughts-language-model) | Tracing Thoughts：思维追踪（On the Biology 大众版） |
| 2026-07 | [global-workspace](https://www.anthropic.com/research/global-workspace) | 全局工作空间理论与 LLM |
| 2026-07 | [introspection](https://www.anthropic.com/research/introspection) | 模型自我审视能力 |

### B. 对齐 / 训练科学（约 22 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2024-12 | [a-general-language-assistant-as-a-laboratory-for-alignment](https://www.anthropic.com/research/a-general-language-assistant-as-a-laboratory-for-alignment) | 早期对齐实验室（Claude 前身） |
| 2024-12 | [training-a-helpful-and-harmless-assistant-with-reinforcement-learning-from-human-feedback](https://www.anthropic.com/research/training-a-helpful-and-harmless-assistant-with-reinforcement-learning-from-human-feedback) | HH-RLHF 论文 |
| 2024-12 | [constitutional-ai-harmlessness-from-ai-feedback](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback) | **Constitutional AI**（引览最多） |
| 2024-12 | [specific-versus-general-principles-for-constitutional-ai](https://www.anthropic.com/research/specific-versus-general-principles-for-constitutional-ai) | 宪法原则：具体 vs 通用 |
| 2025-11 | [collective-constitutional-ai-aligning-a-language-model-with-public-input](https://www.anthropic.com/research/collective-constitutional-ai-aligning-a-language-model-with-public-input) | 集体宪法 AI（公众输入） |
| 2024-12 | [the-capacity-for-moral-self-correction-in-large-language-models](https://www.anthropic.com/research/the-capacity-for-moral-self-correction-in-large-language-models) | 道德自我纠正能力 |
| 2024-08 | [sleeper-agents-training-deceptive-llms-that-persist-through-safety-training](https://www.anthropic.com/research/sleeper-agents-training-deceptive-llms-that-persist-through-safety-training) | **Sleeper Agents**：安全训练洗不掉的欺骗 |
| 2024-05 | [probes-catch-sleeper-agents](https://www.anthropic.com/research/probes-catch-sleeper-agents) | 线性探针抓睡眠 agent |
| 2025-11 | [reward-tampering](https://www.anthropic.com/research/reward-tampering) | Reward tampering（奖励篡改） |
| 2025-11 | [alignment-faking](https://www.anthropic.com/research/alignment-faking) | **Alignment Faking**：假装对齐（2024 末重磅） |
| 2026-07 | [agentic-misalignment](https://www.anthropic.com/research/agentic-misalignment) | Agentic Misalignment：agent 的越轨行为（2025 末） |
| 2026-07 | [emergent-misalignment-reward-hacking](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) | 涌现式失准与 reward hacking |
| 2026-07 | [disempowerment-patterns](https://www.anthropic.com/research/disempowerment-patterns) | 人类失权模式 |
| 2026-06 | [automated-alignment-researchers](https://www.anthropic.com/research/automated-alignment-researchers) | 自动化对齐研究员 |
| 2026-05 | [teaching-claude-why](https://www.anthropic.com/research/teaching-claude-why) | 教 Claude "为什么"（values教学生态） |
| 2026-07 | [values-wild](https://www.anthropic.com/research/values-wild) | 价值观在野演化 |
| 2026-07 | [claude-values-models-languages](https://www.anthropic.com/research/claude-values-models-languages) | Claude 价值观跨语言一致性 |
| 2026-07 | [persona-vectors](https://www.anthropic.com/research/persona-vectors) | 人格向量（方向编辑人格） |
| 2026-07 | [persona-selection-model](https://www.anthropic.com/research/persona-selection-model) | 人格选择模型 |
| 2025-11 | [claude-character](https://www.anthropic.com/research/claude-character) | Claude 的性格工程 |
| 2026-07 | [assistant-axis](https://www.anthropic.com/research/assistant-axis) | 助手行为轴 |
| 2026-07 | [emotion-concepts-function](https://www.anthropic.com/research/emotion-concepts-function) | 情绪概念的功能 |

### C. 安全 / 红队 / 滥用防护（约 30 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2024-12 | [many-shot-jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking) | Many-shot 越狱（长上下文新攻击面） |
| 2024-12 | [red-teaming-language-models-to-reduce-harms-methods-scaling-behaviors-and-lessons-learned](https://www.anthropic.com/research/red-teaming-language-models-to-reduce-harms-methods-scaling-behaviors-and-lessons-learned) | 红队方法论（规模与教训） |
| 2024-10 | [sabotage-evaluations](https://www.anthropic.com/research/sabotage-evaluations) | 破坏行为评测 |
| 2025-06 | [shade-arena-sabotage-monitoring](https://www.anthropic.com/research/shade-arena-sabotage-monitoring) | SHADE-AREA：监控下的暗中破坏评测 |
| 2025-02 | [forecasting-rare-behaviors](https://www.anthropic.com/research/forecasting-rare-behaviors) | 稀有行为预测（罕见能力外推） |
| 2025-11 | [prompt-injection-defenses](https://www.anthropic.com/research/prompt-injection-defenses) | Prompt 注入防御（compiler 那篇） |
| 2026-07 | [constitutional-classifiers](https://www.anthropic.com/research/constitutional-classifiers) | 宪法分类器（防越狱护栏） |
| 2026-06 | [next-generation-constitutional-classifiers](https://www.anthropic.com/research/next-generation-constitutional-classifiers) | 下一代宪法分类器 |
| 2025-11 | [auditing-hidden-objectives](https://www.anthropic.com/research/auditing-hidden-objectives) | 隐藏目标审计 |
| 2026-06 | [claude-4-cyber](https://www.anthropic.com/research/claude-4-cyber) | Claude 4 网络能力 |
| 2026-06 | [cyber-competitions](https://www.anthropic.com/research/cyber-ai) · [cyber-toolkits](https://www.anthropic.com/research/cyber-toolkits) · [cyber-toolkits-update](https://www.anthropic.com/research/cyber-toolkits-update) | 网络攻防竞赛与工具箱 |
| 2026-07 | [building-ai-cyber-defenders](https://www.anthropic.com/research/building-ai-cyber-defenders) | AI 网络防御者 |
| 2026-06 | [attack-navigator](https://www.anthropic.com/research/attack-navigator) | 攻击导航（MITRE ATT&CK 映射） |
| 2026-06 | [zero-days](https://www.anthropic.com/research/zero-days) · [n-days](https://www.anthropic.com/research/n-days) · [exploit](https://www.anthropic.com/research/exploit) · [exploit-evals](https://www.anthropic.com/research/exploit-evals) | 0-day/1-of-N-day 漏洞利用研究系列 |
| 2026-07 | [discovering-cryptographic-weaknesses](https://www.anthropic.com/research/discovering-cryptographic-weaknesses) | 发现密码学弱点 |
| 2026-06 | [smart-contracts](https://www.anthropic.com/research/smart-contracts) · [property-based-testing](https://www.anthropic.com/research/property-based-testing) | 智能合约与属性测试 |
| 2026-06 | [critical-infrastructure-defense](https://www.anthropic.com/research/critical-infrastructure-defense) | 关键基础设施防御 |
| 2026-06 | [nuclear-safeguards-for-ai](https://www.anthropic.com/research/nuclear-safeguards-for-ai) | AI 核保障 |
| 2026-07 | [biorisk](https://www.anthropic.com/research/biorisk) · [agents-in-biology](https://www.anthropic.com/research/agents-in-biology) · [Evaluating-Claude-For-Bioinformatics-With-BioMysteryBench](https://www.anthropic.com/research/Evaluating-Claude-For-Bioinformatics-With-BioMysteryBench) | 生物风险与生物信息评测 |
| 2026-07 | [off-switch-dual-use](https://www.anthropic.com/research/off-switch-dual-use) | 关机开关的双刃性 |
| 2025-10 | [small-samples-poison](https://www.anthropic.com/research/small-samples-poison) | 小样本投毒 |
| 2026-04 | [trustworthy-agents](https://www.anthropic.com/research/trustworthy-agents) | 可信 agent 框架 |

### D. 评测 / 能力科学（约 20 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2024-12 | [building-effective-agents](https://www.anthropic.com/research/building-effective-agents) | Building Effective Agents（research 版） |
| 2024-12 | [swe-bench-sonnet](https://www.anthropic.com/research/swe-bench-sonnet) | SWE-bench 工程复盘（research 版） |
| 2024-12 | [evaluating-ai-systems](https://www.anthropic.com/research/evaluating-ai-systems) | 评测 AI 系统的挑战 |
| 2024-12 | [discovering-language-model-behaviors-with-model-written-evaluations](https://www.anthropic.com/research/discovering-language-model-behaviors-with-model-written-evaluations) | 模型写评测发现行为 |
| 2024-11 | [statistical-approach-to-model-evals](https://www.anthropic.com/research/statistical-approach-to-model-evals) | 评测的统计方法 |
| 2024-12 | [measuring-faithfulness-in-chain-of-thought-reasoning](https://www.anthropic.com/research/measuring-faithfulness-in-chain-of-thought-reasoning) + [question-decomposition-improves-the-faithfulness-of-model-generated-reasoning](https://www.anthropic.com/research/question-decomposition-improves-the-faithfulness-of-model-generated-reasoning) | CoT 忠实性两篇 |
| 2024-12 | [language-models-mostly-know-what-they-know](https://www.anthropic.com/research/language-models-mostly-know-what-they-know) | 模型大多知道自己知道什么（校准） |
| 2024-12 | [towards-understanding-sycophancy-in-language-models](https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models) | 谄媚问题 |
| 2024-08 | [evaluating-and-mitigating-discrimination-in-language-model-decisions](https://www.anthropic.com/research/evaluating-and-mitigating-discrimination-in-language-model-decisions) | 决策歧视评测与缓解 |
| 2024-12 | [towards-measuring-the-representation-of-subjective-global-opinions-in-language-models](https://www.anthropic.com/research/towards-measuring-the-representation-of-subjective-global-opinions-in-language-models) | 全球主观意见表示（OpinionQA） |
| 2024-12 | [evaluating-feature-steering](https://www.anthropic.com/research/evaluating-feature-steering) | 特征转向评测 |
| 2024-12 | [measuring-progress-on-scalable-oversight-for-large-language-models](https://www.anthropic.com/research/measuring-progress-on-scalable-oversight-for-large-language-models) | 可扩展监督 |
| 2026-07 | [measuring-model-persuasiveness](https://www.anthropic.com/research/measuring-model-persuasiveness) | 说服力测量 |
| 2025-04 | [reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think) | 推理模型不说"想"（CoT ≠ 真实计算） |
| 2026-07 | [AI-fluency-index](https://www.anthropic.com/research/AI-fluency-index) | AI 流利度指数 |
| 2026-07 | [AI-assistance-coding-skills](https://www.anthropic.com/research/AI-assistance-coding-skills) | AI 辅助编程技能研究 |
| 2026-06 | [claude-code-expertise](https://www.anthropic.com/research/claude-code-expertise) | Claude Code 专长研究 |
| 2026-06 | [measuring-agent-autonomy](https://www.anthropic.com/research/measuring-agent-autonomy) | Agent 自主性测量 |
| 2026-08 | [multiagent-systems](https://www.anthropic.com/research/multiagent-systems) | 多 agent 系统（最新） |
| 2026-03 | [long-running-Claude](https://www.anthropic.com/research/long-running-Claude) | 长时运行的 Claude |

### E. AI for Science（约 13 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2026-03 | [introducing-anthropic-science](https://www.anthropic.com/research/introducing-anthropic-science) | Anthropic Science 计划发布 |
| 2026-08 | [Claude-accelerates-protein-design](https://www.anthropic.com/research/Claude-accelerates-protein-design) | Claude 加速蛋白质设计（最新） |
| 2026-06 | [making-claude-a-chemist](https://www.anthropic.com/research/making-claude-a-chemist) | 把 Claude 训成化学家 |
| 2026-03 | [vibe-physics](https://www.anthropic.com/research/vibe-physics) | Vibe Physics（AI 与物理研究范式） |
| 2026-08 | [riemann-zeta](https://www.anthropic.com/research/riemann-zeta) | 黎曼 ζ 猜想相关实验（AI for Math） |
| 2026-07 | [claude-plays-robotics](https://www.anthropic.com/research/claude-plays-robotics) | Claude 玩机器人 |
| 2026-06 | [mythos-preview](https://www.anthropic.com/research/mythos-preview) | Mythos 模型预览（科学特化线） |
| 2026-06→07 | [project-fetch-robot-dog](https://www.anthropic.com/research/project-fetch-robot-dog) · [project-fetch-phase-two](https://www.anthropic.com/research/project-fetch-phase-two) | Project Fetch：机器人狗两阶段 |
| 2026-03→07 | [project-vend-1](https://www.anthropic.com/research/project-vend-1) · [project-vend-2](https://www.anthropic.com/research/project-vend-2) | Project Vend：自动售货 agent |
| 2026-07 | [project-pilot](https://www.anthropic.com/research/project-pilot) | Project Pilot |
| 2025-12 | [bloom](https://www.anthropic.com/research/bloom) | Bloom 项目 |

### F. 社会经济影响（约 20 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2025-08 | [clio](https://www.anthropic.com/research/clio) | Clio：对话隐私分析系统 |
| 2026-01→07 | [anthropic-economic-index-september-2025-report](https://www.anthropic.com/research/anthropic-economic-index-september-2025-report) · [january-2026](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) · [june-2026](https://www.anthropic.com/research/economic-index-june-2026-report) · [march-2026](https://www.anthropic.com/research/economic-index-march-2026-report) | 经济指数四次报告 |
| 2026-07 | [economic-index-primitives](https://www.anthropic.com/research/economic-index-primitives) · [economic-index-geography](https://www.anthropic.com/research/economic-index-geography) | 经济指数方法论/地理分布 |
| 2026-02 | [india-brief-economic-index](https://www.anthropic.com/research/india-brief-economic-index) | 印度简报 |
| 2026-06 | [81k-economics](https://www.anthropic.com/research/81k-economics) | 81k 对话经济学 |
| 2026-07 | [labor-market-impacts](https://www.anthropic.com/research/labor-market-impacts) · [impact-software-development](https://www.anthropic.com/research/impact-software-development) · [estimating-productivity-gains](https://www.anthropic.com/research/estimating-productivity-gains) · [economic-policy-responses](https://www.anthropic.com/research/economic-policy-responses) · [reviewing-the-evidence-on-worker-retraining-programs](https://www.anthropic.com/research/reviewing-the-evidence-on-worker-retraining-programs) | 劳动市场/软件业/生产率/政策/再培训五连 |
| 2026-07 | [2028-ai-leadership](https://www.anthropic.com/research/2028-ai-leadership) | 2028 AI 领导力预测 |
| 2026-03 | [how-australia-uses-claude](https://www.anthropic.com/research/how-australia-uses-claude) · 2026-07 [how-canada-uses-claude](https://www.anthropic.com/research/how-canada-uses-claude) | 澳/加 Claude 使用画像 |
| 2026-06 | [how-ai-is-transforming-work-at-anthropic](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) | AI 怎么改变 Anthropic 自己的工作 |
| 2026-05 | [coding-agents-social-sciences](https://www.anthropic.com/research/coding-agents-social-sciences) | 编程 agent 与社会科学 |
| 2026-07 | [anthropic-interviewer](https://www.anthropic.com/research/anthropic-interviewer) | 面试官工具研究 |
| 2025-04 | [exploring-model-welfare](https://www.anthropic.com/research/exploring-model-welfare) | 模型福利探索 |

### G. 基础设施 / 工具 / 开源（约 12 篇）

| 日期 | 文章 | 一句话 |
|---|---|---|
| 2025-06 | [confidential-inference-trusted-vms](https://www.anthropic.com/research/confidential-inference-trusted-vms) | 可信 VM 机密推理 |
| 2025-11 | [deprecation-commitments](https://www.anthropic.com/research/deprecation-commitments) · 2026-02 [deprecation-updates-opus-3](https://www.anthropic.com/research/deprecation-updates-opus-3) | API 弃用政策与 Opus 3 弃用 |
| 2026-04 | [diff-tool](https://www.anthropic.com/research/diff-tool) | Diff 工具（模型输出对比） |
| 2025-08 | [end-subset-conversations](https://www.anthropic.com/research/end-subset-conversations) | 会话结束子集 |
| 2025-05→10 | [donating-open-source-petri](https://www.anthropic.com/research/donating-open-source-petri) · [petri-open-source-auditing](https://www.anthropic.com/research/petri-open-source-auditing) | Petri 开源捐赠与审计 |
| 2026-05 | [glasswing-initial-update](https://www.anthropic.com/research/glasswing-initial-update) | Glasswing 项目（高影响力研究计划）首报 |
| 2025-11 | [team/*](https://www.anthropic.com/research/team/interpretability) | 五个团队页（alignment/interpretability/societal-impacts/economic-research/frontier-red-team） |
| 2026-05 | [anthropic-institute-agenda](https://www.anthropic.com/research/anthropic-institute-agenda) | Anthropic Institute 议程 |

---

## 三、News 技术类子集（255 篇中筛约 60 篇）

> news 板大部分是商务/政策/人事，以下是**技术相关**的部分（模型发布按代际列）。

### 模型发布线（按时间）

- 2023→2024: [introducing-claude](https://www.anthropic.com/news/introducing-claude) → [claude-2](https://www.anthropic.com/news/claude-2) / [claude-2-1](https://www.anthropic.com/news/claude-2-1) / [releasing-claude-instant-1-2](https://www.anthropic.com/news/releasing-claude-instant-1-2)
- 2024-03→05: [claude-3-family](https://www.anthropic.com/news/claude-3-family)（Haiku/Sonnet/Opus 三尺寸首发）/ [claude-3-haiku](https://www.anthropic.com/news/claude-3-haiku) / [100k-context-windows](https://www.anthropic.com/news/100k-context-windows)
- 2024-06→10: [claude-3-5-sonnet](https://www.anthropic.com/news/claude-3-5-sonnet) / [3-5-models-and-computer-use](https://www.anthropic.com/news/3-5-models-and-computer-use)（computer use 首发）/ [fine-tune-claude-3-haiku](https://www.anthropic.com/news/fine-tune-claude-3-haiku)
- 2025-02→09: [claude-3-7-sonnet](https://www.anthropic.com/news/claude-3-7-sonnet)（extended thinking 混合推理）/ [claude-4](https://www.anthropic.com/news/claude-4) / [claude-opus-4-1](https://www.anthropic.com/news/claude-opus-4-1)
- 2025-09→2026-08: [claude-haiku-4-5](https://www.anthropic.com/news/claude-haiku-4-5) / [claude-sonnet-4-5](https://www.anthropic.com/news/claude-sonnet-4-5) / [claude-sonnet-4-6](https://www.anthropic.com/news/claude-sonnet-4-6) / [claude-opus-4-5](https://www.anthropic.com/news/claude-opus-4-5) → 4-6 / [4-7](https://www.anthropic.com/news/claude-opus-4-7) / [4-8](https://www.anthropic.com/news/claude-opus-4-8) → [claude-opus-5](https://www.anthropic.com/news/claude-opus-5) / [claude-sonnet-5](https://www.anthropic.com/news/claude-sonnet-5)
- 2026 新模型族: [claude-fable-5-mythos-5](https://www.anthropic.com/news/claude-fable-5-mythos-5) / [fable-mythos-access](https://www.anthropic.com/news/fable-mythos-access) / [redeploying-fable-5](https://www.anthropic.com/news/redeploying-fable-5) / [improving-fable-5-s-biology-safeguards](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards)

### 平台 / 技术能力

[model-context-protocol](https://www.anthropic.com/news/model-context-protocol)（MCP 发布）/ [donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)（MCP 捐入 Linux 基金会）/ [contextual-retrieval](https://www.anthropic.com/news/contextual-retrieval) / [skills](https://www.anthropic.com/news/skills)（Agent Skills 发布）/ [prompting-long-context](https://www.anthropic.com/news/prompting-long-context) / [prompt-engineering-for-business-performance](https://www.anthropic.com/news/prompt-engineering-for-business-performance) / [developing-computer-use](https://www.anthropic.com/news/developing-computer-use) / [visible-extended-thinking](https://www.anthropic.com/news/visible-extended-thinking) / [introducing-claude-tag](https://www.anthropic.com/news/introducing-claude-tag) / [claude-text-watermark](https://www.anthropic.com/news/claude-text-watermark)（文本水印，2026-08）/ [Introducing-code-with-claude](https://www.anthropic.com/news/Introducing-code-with-claude) / [github-copilot](https://www.anthropic.com/news/github-copilot)（Copilot 接入 Claude）/ [claude-in-xcode](https://www.anthropic.com/news/claude-in-xcode) / [apple-xcode-claude-agent-sdk](https://www.anthropic.com/news/apple-xcode-claude-agent-sdk) / [claude-code-on-team-and-enterprise](https://www.anthropic.com/news/claude-code-on-team-and-enterprise) / [enabling-claude-code-to-work-more-autonomously](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously) / [projects](https://www.anthropic.com/news/projects) / [claude-science-ai-workbench](https://www.anthropic.com/news/claude-science-ai-workbench) / [finance-agents](https://www.anthropic.com/news/finance-agents)

### 安全技术

[claude-code-security](https://www.anthropic.com/news/claude-code-security) / [mozilla-firefox-security](https://www.anthropic.com/news/mozilla-firefox-security) / [model-safety-bug-bounty](https://www.anthropic.com/news/model-safety-bug-bounty) / [testing-our-safety-defenses-with-a-new-bug-bounty-program](https://www.anthropic.com/news/testing-our-safety-defenses-with-a-new-bug-bounty-program) / [frontier-model-security](https://www.anthropic.com/news/frontier-model-security) / [activating-asl3-protections](https://www.anthropic.com/news/activating-asl3-protections) / [anthropics-responsible-scaling-policy](https://www.anthropic.com/news/anthropics-responsible-scaling-policy) / [responsible-scaling-policy-v3](https://www.anthropic.com/news/responsible-scaling-policy-v3) / [core-views-on-ai-safety](https://www.anthropic.com/news/core-views-on-ai-safety) / [claudes-constitution](https://www.anthropic.com/news/claudes-constitution) / [claude-new-constitution](https://www.anthropic.com/news/claude-new-constitution) / [building-safeguards-for-claude](https://www.anthropic.com/news/building-safeguards-for-claude) / [our-framework-for-developing-safe-and-trustworthy-agents](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents) / [challenges-in-red-teaming-ai-systems](https://www.anthropic.com/news/challenges-in-red-teaming-ai-systems) / [frontier-threats-red-teaming-for-ai-safety](https://www.anthropic.com/news/frontier-threats-red-teaming-for-ai-safety) / [detecting-and-countering-malicious-uses-of-claude-march-2025](https://www.anthropic.com/news/detecting-and-countering-malicious-uses-of-claude-march-2025) / [detecting-and-preventing-distillation-attacks](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks) / [strategic-warning-for-ai-risk-progress-and-insights-from-our-frontier-red-team](https://www.anthropic.com/news/strategic-warning-for-ai-risk-progress-and-insights-from-our-frontier-red-team) / [fable-safeguards-jailbreak-framework](https://www.anthropic.com/news/fable-safeguards-jailbreak-framework) / [AI-enabled-cyber-threats-mitre-attack](https://www.anthropic.com/news/AI-enabled-cyber-threats-mitre-attack) / [investigating-incidents-cybersecurity-evals](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals) / [confidential-draft-s1-sec](https://www.anthropic.com/news/confidential-draft-s1-sec) / [introducing-anthropic-transparency-hub](https://www.anthropic.com/news/introducing-anthropic-transparency-hub)

### 其他技术页（非 news/engineering/research）

- [features/making-of-claude-code](https://www.anthropic.com/features/making-of-claude-code) — Claude Code 幕后制作
- [institute/recursive-self-improvement](https://www.anthropic.com/institute/recursive-self-improvement) — 递归自我改进（Institute 议题页）
- [claude/fable](https://www.anthropic.com/claude/fable) / [claude/mythos](https://www.anthropic.com/claude/mythos) — 两个 2026 新模型族产品页

---

## 四、sitemap 侧写（数字洞察）

1. **规模**：research 153 > news 255（总）> engineering 25。研究输出是工程博客的 6 倍——Anthropic 本质上把官网当论文库用。
2. **2026 两条隐线**：① 新模型族 Fable/Mythos（fable-5/mythos-5，科学特化？）与 Opus/Sonnet 主线并行；② 安全研究爆炸——cyber 系列（zero-days/n-days/exploit/smart-contracts/property-based-testing）集中在 2026-06-17 同日发布，是成体系的"攻防能力"研究波。
3. **经济指数工业化**：economic-index 已出 4 份季度报告 + 方法论 + 地理分册——从研究项目变成了常规统计产品。
4. **与知识库版（贴来的那份）的差异**：该版截止 2025 且缺 entire 2026 线（Fable/Mythos/水印/Institute/cyber 系列/SWE 新篇）；其"七层 Circuits Updates"实际只有 6 篇（2023-05 至 2024-09），之后转向 open-source-circuit-tracing 等新形态。

## refs
- sitemap.xml 官方抓取 2026-08-20（515 URL 全量，python 解析，含 lastmod）；三个清单留档 /tmp/opencode/anth_{engineering,research,news}.txt
- 描述来源：slug 语义 + 2025 前已知文章内容；2026 新篇未逐篇打开核实内容，仅按 slug 忠实转述（如需精读某篇可 webfetch）

*updated: 2026-08-20*
