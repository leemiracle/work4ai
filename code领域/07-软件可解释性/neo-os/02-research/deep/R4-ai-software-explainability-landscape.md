# R4 — AI 驱动的复杂软件可解释性工具竞品全景（2024-2026）：Neo-OS 的护城河与蓝海验证

> **调研主题**：AI 驱动的复杂软件可解释性工具竞品全景——Neo-OS 的护城河与蓝海验证 | **日期**：2026-08-05 | **核实等级**：核心竞品 ✅官网一手 / 关键 arXiv ✅abs页核实 / 部分推断 ⚡标注 | **核实日期**：2026-08-05

---

## 一、TL;DR（5 条结论）

1. **Neo-OS 作为完整系统没有被抢先。** 截至 2026-08，没有任何竞品同时做到「L0 硬件级 trace（eBPF/Intel PT）+ L2.5 形式化因果规则（Lean4）+ L3 教学级英文解释（三层讲透 × 17 视角）」三件套，且面向**任意复杂软件**（不限于云微服务或 AI agent）。这是**确认的蓝海**。

2. **但每一层单独都有强敌，且差距在快速收窄。** L3（自然语言查询/RCA 解释）已被 Datadog Bits AI、Honeycomb Canvas、Chronosphere 高度商业化成熟；L0（eBPF+LLM）已有 AgentSight/Kgent/GPTtrace 等学术先行者；L2.5（Lean4 形式化软件行为）已有 **Lean4Agent**（2026-06，首个用 Lean4 验证 agent workflow 的框架）和 **LeanCTX**（53 个 Lean4 定理验证 AI 运行时）触及同一思想。三层的**整合**是护城河，整合本身也是最难执行的部分。

3. **最危险的竞品不是单一产品，而是「TAAF 式 trace→KG→LLM」与「Lean4Agent 式形式化 workflow 验证」两条学术线的合流。** 这两线一旦融合（trace + 形式化 + 英文），就与 Neo-OS 的内核正面相撞。预估窗口 12-24 个月。

4. **Neo-OS 最被低估的差异化资产是 L3「三层讲透 × 17 视角」的教学深度。** 全部竞品都停留在「问答/RCA 报告」层面（一次性、flat、无认知阶梯），无人做 pedagogical（直觉→数学→代码、费曼门、17 视角）。这是继承 work4ai 的真护城河，竞品短期内难以复制，因为它需要的是内容方法论而非纯技术。

5. **反面证据反而最强地支持 Neo-OS 的 L2.5 形式化层。** 2026 年最新 RCA 研究显示，LLM RCA agent 的**主导失败模式是「解释性幻觉」（Hallucination in Interpretation，71.2%）**，且 prompt engineering 无法解决——结论是「需要验证模块交叉检查 agent 解释」。这正是 Neo-OS L2.5（Lean4 soundness guarantee）要解决的。形式化不是锦上添花，是刚需。

---

## 二、竞品全景（按 4 类组织）

### 类别 A：AI for Code Understanding（代码理解）

| 产品 | 最新状态（核实） | 核心能力 | 与 Neo-OS 重叠 |
|------|----------------|---------|---------------|
| **Sourcegraph**（Cody→Code Intelligence Platform 7.0） | 🟢 活跃。Series D **$150M，$2.6B 估值**（2025-10）。2026-02 发布 7.0，定位「AI agent + 开发者共享的代码智能层」。Deep Search（MCP）、Agentic Batch Changes（公测）✅ | 静态代码图谱（SCIP）+ RAG + BM25 检索，跨仓语义搜索；为 AI agent 提供代码上下文 | **静态代码**层面与 Neo-OS L2 world model 有重叠；但 Sourcegraph **不碰运行时 trace、不做形式化、解释是 flat QA 非教学级** |
| **Cursor / Composer** | 🟢 活跃（头部 AI IDE，估值数十亿级）⚡ | 原生 AI IDE，Composer 多文件编辑，代码库索引 | 纯开发时、代码级；**无运行时、无形式化、无系统级行为解释** |
| **Greptile** | 🟢 活跃但已**转型**。$4.1M seed（2024-06）。2025-05 转向 **AI 代码审查机器人**，$30/dev/月，2000+ 团队。曾做代码库自然语言 Q&A API ✅ | 语义代码检索 + LLM；现已聚焦 PR review | **已退出「理解代码库」主战场**，转向 review；对 Neo-OS 威胁下降 |
| **Bloop** | 🔴 **已死**。仓库 **2025-01-02 归档（ARCHIVED）**，最后版本 v0.6.5（2024-04）。曾是「ChatGPT for your code」，Rust+Tantivy+Qdrant ✅ | 本地 on-device 嵌入、会话式代码搜索 | **死亡竞品**——证明「纯代码搜索+LLM」赛道不足以独立存活，工具 1 年就死 |

**类别 A 判断**：这一类全部停留在**静态源码 + RAG + flat 问答**，无运行时行为、无形式化保证、无教学深度。Neo-OS 的「行为可解释性」与它们的「代码可检索性」是不同问题域。Greptile 转型、Bloop 死亡，说明纯代码库 QA 单独难以构成可持续产品——这是 Neo-OS 需警惕的市场信号。

### 类别 B：Observability + LLM（可观测性 + LLM）

| 产品 | 最新状态 | 核心能力 | 与 Neo-OS 重叠 |
|------|---------|---------|---------------|
| **Datadog Bits AI** | 🟢 极成熟。Bits Chat（GA 2026-06）、Bits Investigation（GA 2025-06，2026-03 升级「深度推理、2×提速」）、Bits Code（生成生产修复）、Bits Agent Builder（GA）。号称 TTR 降低 **95%**。2026 Gartner MQ 可观测性领导者（第六次）✅ | NLQ 查询；自主 SRE agent（假设→验证→根因）；trace span 级分析；MCP 连接 Claude/Cursor/Codex | **L3 RCA 层高度重叠**；但 Datadog **只吃自家遥测**（非 eBPF/Intel PT 硬件级）、**无形式化保证**、**无教学级解释**、**只服务云原生不服务 OS/编译器/GPU** |
| **Honeycomb**（Canvas / Intelligence） | 🟢 活跃。Query Assistant（2023），Canvas（2025-11，AI 协作画布），Honeycomb Intelligence（2025-09），Agent Observability（2026-05）✅ | NLQ；AI 调查笔记本；Anomaly Detection；强调「人-agent 协作」哲学；OpenTelemetry GenAI 原生 | 与 Datadog 类似；**明确拒绝「黑盒吐文字」**，强调可验证的推理步骤——理念上最接近 Neo-OS 的 transparency 哲学，但仍无形式化、无硬件 trace |
| **Chronosphere** | 🟢 活跃。NLQ（2026-05），Guided Troubleshooting（2025-11，含 **Temporal Knowledge Graph + Differential Diagnosis + Leaf Errors**）✅ | NLQ→PromQL；时序知识图谱；差分诊断；**这是可观测性厂商中最接近「结构化因果」的** | KG + DDx 与 Neo-OS L1 因果有理念重叠；但 **无形式化、无硬件级、无教学级、仅云指标** |
| **Cribl** | 🟢 活跃。Cribl AI、Search Investigations（Preview，含 Deep Investigation 假设驱动模式）、MCP 集成 ✅ | NLQ→KQL；假设驱动深度调查；web search 补充 | 数据管道层；**无形式化、无硬件 trace** |

**类别 B 判断**：这一类是 **L3（英文解释/RCA）的商业化冠军**，但全部有两个结构性盲区：(1) 数据源是**自家探针/SDK 采集的应用遥测**，不是 eBPF/Intel PT 硬件级 ground-truth trace；(2) **零形式化保证**——解释的可信度完全依赖 LLM，而研究表明这正是失败主因。Chronosphere 的「Temporal KG + DDx」是最接近 Neo-OS L1 因果结构的工业化尝试。

### 类别 C：学术 LLM-as-explainer（系统行为解释/RCA）

| 工作 | 核实 | 核心贡献 | 与 Neo-OS 重叠 |
|------|------|---------|---------------|
| **TAAF** | ✅ arXiv:2601.02632，Alireza Ezaz 等，2026-01-06 提交，**ICSE 2026 录用** | **trace→时序状态系统→查询特定知识图谱→LLM 解释**。TraceQA-100 基准。graph-grounding 提升准确率 31.2%（短区间最高 95.5%） | ⚠️ **这是与 Neo-OS L1+L2+L3 最接近的学术工作**。但 TAAF **无形式化验证、无教学深度（flat QA）、trace 是 kernel 级但未提 eBPF/Intel PT 作为统一 L0、无五原子本体** |
| **AgentSight** | ✅ arXiv:2508.02736，Yusheng Zheng 等，2025-08-02 提交，v2 2025-08-15，PACMI'2025 | **eBPF + LLM 做 AI agent 可观测性**。「boundary tracing」用 eBPF 拦截 TLS LLM 流量 + 监控 kernel 事件，二级 LLM 做因果关联与解释。<3% 开销。开源 | L0(eBPF)+LLM 与 Neo-OS 重叠；但 **仅限 AI agent、安全导向非教学导向、无形式化** |
| **Kgent / GPTtrace / MCPtrace** | ✅ eunomia-bpf 项目，Kgent 发表于 eBPF'24（SIGCOMM workshop），DOI 10.1145/3672197.3673434 | LLM + 符号执行（Z3）从自然语言**生成** eBPF 程序；AI 解释 trace 结果 | 与 Neo-OS L0(eBPF) + L3 解释有重叠；但方向是「LLM 写 eBPF」而非「eBPF trace → 解释任意系统」；**无形式化因果、无 world model** |
| **LLM-RCA 系列**（OpenRCA / LATS-RCA / KRCA / JUSTDIAG / PRAXIS / RC-LLM） | ✅ 多篇，2025-2026 | LLM agent 做云微服务根因分析。KRCA 部署快手 6 个月降诊断时间 77.3%。LATS-RCA 生产环境 65.1% 准确率 | **L3 RCA 层全面重叠**；**关键反面证据来源**（见类别反面） |

**类别 C 判断**：学术圈正在**快速逼近 Neo-OS 的思想**。TAAF（ICSE 2026）几乎是 Neo-OS 的「去形式化、去教学化」简化版。AgentSight 把 eBPF+LLM 落到了 AI agent 场景。**没有一篇同时做形式化 + 教学 + 任意软件**，但「trace→结构化抽象→LLM 解释」的范式已是公认方向（ICSE 录用证明主流认可）。

### 类别 D：形式化 + LLM（Lean4 / verified）

| 工作 | 核实 | 核心贡献 | 与 Neo-OS 重叠 |
|------|------|---------|---------------|
| **AlphaProof / AlphaProof Nexus** | ✅ Nature 2025（s41586-025-09833-y）；Nexus 仓库 2026-05 | Lean4 + RL（AlphaZero 式）证明数学竞赛题；IMO 银牌。Nexus 自主解决 Erdős 开放问题 + OEIS 猜想 | 神经符号闭环（LLM 生成 + Lean4 验证）与 Neo-OS L2.5 理念同源；但 **领域是纯数学，不碰软件系统行为** |
| **Lean4Agent** | ✅ arXiv:2606.06523，Ruida Wang 等，2026-06 | **首个用 Lean4（dependent-type）建模与验证 agent workflow 的框架**。FormalAgentLib 三层（结构/语义/轨迹）。验证通过的 workflow 比失败的高 11.94% | ⚠️⚠️ **这是与 Neo-OS L2.5 最接近的工作**——Lean4 形式化「软件行为（agent 轨迹）」。但 **验证对象是 agent workflow 而非任意系统行为、无 eBPF trace、无教学级英文输出、Hoare logic 而非因果规则** |
| **LeanCTX** | ✅ GitHub yvgude/lean-ctx，PAPER.md | Lean4 形式化 AI 开发运行时（context policy/compression/secret/handoff），**53 定理，0 sorry，<2s 编译**。Proof-Carrying Context | Lean4 验证「软件基础设施行为」已证明可行；但 **验证的是 AI tool 自身边界，非对外部复杂系统的解释** |
| **heartpunk/learnability** | ✅ GitHub 仓库 | Lean4 证明：对有限行为系统，迭代精化总能提取**忠实的行为模型**（extraction_exists 定理，bisimulation） | 理论上支持 Neo-OS L2 world model 蒸馏的可信度；**但纯理论，无实现、无 trace、无教学** |
| **OpenProver / Leanabell-Prover-V2 / DeepSeek-Prover-V2 / Goedel-Prover-V2** | ✅ 多篇 | LLM + RL 生成 Lean4 数学证明，7B 模型达 MiniF2F 78.2% | 全部是**数学定理证明**，与软件系统行为解释无关 |

**类别 D 判断**：形式化 + LLM 爆发，但**全部集中在数学定理或 AI agent workflow**，**无人用 Lean4 形式化「任意复杂软件的运行时因果规则」并产出英文解释**。Lean4Agent（2026-06）是最危险的信号——它证明「Lean4 验证软件行为」这条思路成立且有效（+11.94%）。Neo-OS 的 L2.5 必须明确区分自己验证的是**领域无关的系统因果规则**（五原子），而非 agent workflow。

---

## 三、对比矩阵（1-5 分制）

> 评分维度：L0 抓事件（eBPF/Intel PT 硬件级）｜L2 world model（蒸馏）｜L2.5 形式化（Lean4 soundness）｜L3 英文（教学级/非flat）｜商业化成熟度｜与 Neo-OS 重叠度

| 竞品 | L0 | L2 | L2.5 | L3教学 | 商业成熟 | 重叠度 |
|------|----|----|------|--------|---------|--------|
| **Neo-OS（目标态）** | 5 | 5 | 5 | 5 | 1（立项） | — |
| Sourcegraph | 1 | 3（静态代码图谱） | 0 | 2（flat QA） | 5（$2.6B） | 2 |
| Cursor | 0 | 2 | 0 | 1 | 5 | 1 |
| Greptile | 0 | 2 | 0 | 1 | 3（转型中） | 1 |
| Datadog Bits AI | 2（自家探针） | 3（topology+假设） | 0 | 3（RCA报告） | 5（领导者） | 4 ⚠️ |
| Honeycomb Canvas | 2 | 3 | 0 | 3 | 4 | 3 |
| Chronosphere | 2 | 4（时序KG+DDx） | 0 | 3 | 4 | 4 ⚠️ |
| Cribl | 2 | 2 | 0 | 2 | 3 | 2 |
| **TAAF（学术）** | 4（kernel trace） | 4（时序KG） | 0 | 2（QA） | 0（论文） | 5 ⚠️⚠️ |
| **AgentSight（学术）** | 5（eBPF） | 2 | 0 | 2（安全解释） | 0（开源） | 4 |
| **Lean4Agent（学术）** | 0 | 2 | 5（Lean4） | 0 | 0 | 4 ⚠️⚠️ |
| LeanCTX | 0 | 1 | 5（Lean4, 53定理） | 0 | 0 | 3 |
| AlphaProof 系列 | 0 | 0 | 5（Lean4） | 0 | 1（API） | 1 |
| Kgent/GPTtrace | 5（eBPF生成） | 2 | 1（Z3符号） | 2 | 1 | 3 |

**矩阵洞察**：
- **没有一个竞品在 L2.5 + L3教学 两格同时 ≥3**。这是最清晰的蓝海证据。
- **L2.5 形式化**这一列，只有 Lean4Agent / LeanCTX / AlphaProof 系列得高分，而它们全部在 L0、L3教学 得 0-1 分。
- **L3 教学级**这一列，**全部竞品 ≤3**（最高是 Datadog/Honeycomb 的「RCA 报告」级，非教学级）。Neo-OS 的三层讲透 ×17 视角是**无对标**维度。
- 重叠度 ≥4 的有 Datadog（L3 RCA）、Chronosphere（KG+DDx）、TAAF（trace+KG+LLM）、AgentSight（eBPF+LLM）、Lean4Agent（Lean4 行为）——它们各自只覆盖 Neo-OS 的一个切面。

---

## 四、蓝海定位：Neo-OS 独特组合的护城河深度

### 4.1 五个竞争象限全部「单点突破」，无人「三件套集成」

把竞品画在「L0 硬件 trace」×「L2.5 形式化」×「L3 教学英文」的三维空间里，存在五个已验证的「单点簇」，但**没有竞品占据「三者交集」的八分之一象限**：

- **eBPF + LLM**（AgentSight/Kgent）：有 L0，无 L2.5/L3教学
- **Trace + KG + LLM**（TAAF）：有 L0+L2，无 L2.5/L3教学
- **Lean4 + 软件行为**（Lean4Agent/LeanCTX）：有 L2.5，无 L0/L3教学
- **Lean4 + 数学**（AlphaProof 系）：有 L2.5，纯数学域
- **NLQ + RCA**（Datadog/Honeycomb/Chronosphere）：有 L3（flat），无 L0 硬件/L2.5 形式化

### 4.2 护城河深度评估（按可复制难度排序）

1. **L3 三层讲透 × 17 视角（最深护城河）**：这不是技术问题，是**内容方法论 + 认知科学**问题。继承自 work4ai 的 60+ 主题实证，需要长周期积累，竞品即使有再多钱也难以在 18 个月内复制——因为瓶颈是「教学法设计能力」而非算力/数据。⚡推断：这是 Neo-OS 最被低估的资产。

2. **L2.5 Lean4 形式化因果规则（次深）**：Lean4 本身开源、AlphaProof 证明可行，但「把任意软件的运行时因果抽象成五原子并形式化」是**全新的形式化领域**（现有 Lean4 工作全在数学或 agent workflow）。RCA 文献的反面证据（71.2% 解释幻觉）证明这是刚需，但「形式化粒度种子」是 Neo-OS 自己 ROADMAP 里标的命门——**护城河深，但自己也未必能快速填满**。

3. **领域无关五原子内核（中等护城河）**：Event/State/Causality/Invariant/DecisionPoint 的抽象是否真的能跨 OS/编译器/游戏引擎/GPU/数据库通用，是**待验证假设**。若验证成功则是强护城河（通用性 = 网络效应）；若验证失败则退化为「每域一个 adapter 工程」，护城河变浅。

4. **L2 commit 蒸馏 world model（较浅护城河，技术易复制）**：从软件 commit/trace 历史蒸馏领域模型，技术上 Sourcegraph（代码图谱）和 Datadog（topology 学习）都在做类似的事。7B 本机常驻是工程优势非概念壁垒。

5. **L0 eBPF/Intel PT（最浅护城河，基础设施化）**：eBPF + LLM 已被 eunomia 生态（Kgent/AgentSight/GPTtrace）充分探索并开源。Intel PT + LLM 几乎无人做（蓝海更纯），但 eBPF 这一路已不稀缺。

### 4.3 蓝海净评估

**蓝海确认存在**，定位在：「形式化保证的教学级解释」×「硬件级 ground-truth trace」×「领域无关内核」。但需诚实承认：**这个蓝海的「水」很深（执行难度极高），且两岸（TAAF 派 + Lean4Agent 派）正在各自动工**。窗口期估计 12-24 个月（学术合流）/ 24-36 个月（工业整合）。

---

## 五、反面：Neo-OS 最可能被谁吃掉（危险前 3）

### 🥇 威胁 1：Datadog 向下吃「L0 + 形式化」+ 横向扩域

**为什么最危险**：Datadog 已有行业最大的生产遥测数据集（号称「最大 RCA benchmark」）、最成熟的 L3 RCA（Bits Investigation，自主假设验证）、最强分发（Gartner 领导者六连冠）。它只需两个动作就能撞上 Neo-OS：(a) 把探针从应用层下沉到 eBPF/硬件（已在 Datadog Agent MCP 做 on-demand shell + kernel 可见性）；(b) 在 Bits Investigation 里加一层结构化因果规则校验。

**为什么不会完全吃掉**：(1) Datadog 的商业模型是「云可观测性 SaaS」，而 Neo-OS 定位「任意复杂软件（OS/编译器/GPU）」是**非云场景**，Datadog 不会为一个不付费的研究型场景扩域；(2) Datadog 的 RCA 本质是「LLM + 工具调用」，它**没有动机引入 Lean4**（增加复杂度、不直接变现）；(3) Datadog 不做教学级解释（客户要的是「修好」，不是「学懂」）。

**防御**：Neo-OS 必须锁定 Datadog 不愿做的「非云 + 教学 + 形式化」三角，把它定位为「**认知工具**」而非「**运维工具**」。一旦 Neo-OS 被理解成「更好的 Datadog」，就输了。

### 🥈 威胁 2：TAAF × Lean4Agent 学术合流（12-24 个月窗口）

**为什么危险**：TAAF（ICSE 2026）已证明「trace→KG→LLM」范式被主流软件工程会议接受；Lean4Agent（2026-06）已证明「Lean4 验证软件行为」有效（+11.94%）。这两个团队若合流（或在第三方的综述/框架里合流），产出的「**形式化保证的 trace 解释**」就是 Neo-OS L1+L2+L2.5 的学术版。学术合流速度通常 12-24 个月。

**为什么不会完全吃掉**：(1) 学术工作普遍**不做教学级英文**（论文要的是 benchmark 数字，不是费曼门）；(2) 学术工作**不做领域无关内核**（TAAF 只测 SciMark，Lean4Agent 只测 SWE-Bench）；(3) 学术工作**不做五原子抽象**（每篇都为单一 benchmark 定制）。

**防御**：Neo-OS 应**主动引用并定位为这两线的「产品化 + 教学化 + 通用化」整合者**，而非假装它们不存在。最坏情况：被一篇综述抢先命名「Formal Explainability for Software」。建议 Neo-OS 在 6 个月内出一篇 position paper 占位。

### 🥉 威胁 3：eunomia 生态（AgentSight/Kgent）向上扩域 + 加形式化

**为什么危险**：eunomia-bpf 团队是 **eBPF × AI 最活跃的开源生态**，已发表 Kgent（eBPF'24）、AgentSight、GPTtrace、MCPtrace、bpftime，并有 ASPLOS 2026「AgenticOS Workshop」的组织力。他们离 Neo-OS 的 L0 最近，且已开始做「eBPF × 形式化」的交叉（Kgent 用 Z3 符号执行）。若他们把对象从「AI agent」扩到「任意复杂软件」并引入 Lean4，就是 Neo-OS L0+L2.5 的开源版。

**为什么不会完全吃掉**：(1) eunomia 的重心始终是 **eBPF 技术栈本身**（编译器/运行时/安全），不是「可解释性产品」；(2) 他们没有教学级解释的内容基因；(3) 他们关注「AI agent observability」这一热点，未必愿意转向「冷门的传统系统解释」。

**防御**：Neo-OS 可考虑**合作而非对抗**——把 eunomia 的 eBPF 工具链作为 L0 adapter 的首选实现，自己专注 L2.5+L3。 ⚡推断：eunomia 更可能是**盟友/上游**而非直接竞争者。

---

## 六、引用清单（全部 URL + arXiv + 核实状态）

### 6.1 竞品产品（官网一手）

| # | 来源 | 核实 | 日期 |
|---|------|------|------|
| P1 | Sourcegraph Code Intelligence Platform 官网 https://sourcegraph.com/ | ✅ | 2026-08-05 |
| P2 | Sourcegraph 7.0 博客 https://sourcegraph.com/blog/a-new-era-for-sourcegraph-the-intelligence-layer-for-ai-coding-agents-and-developers | ✅ | 2026-02-25 |
| P3 | Sourcegraph Cody Series D $150M / $2.6B https://www.startuphub.ai/investment_rounds/sourcegraph-cody-series-d-2025 | ✅ | 2025-10-22 |
| P4 | Sourcegraph Cody 仓库（ARCHIVED） https://github.com/sourcegraph/cody-public-snapshot | ✅ | 2026-08-05 |
| P5 | Datadog Bits Chat https://www.datadoghq.com/blog/introducing-bits-chat/ | ✅ | 2026-06-08 |
| P6 | Datadog Bits Investigation https://www.datadoghq.com/blog/bits-ai-sre/ | ✅ | 2025-06-10 |
| P7 | Datadog "How we built an AI SRE" https://www.datadoghq.com/blog/building-bits-ai-sre/ | ✅ | 2026-01-12 |
| P8 | Datadog DASH 2026 AI 总览 https://www.datadoghq.com/blog/dash-2026-new-feature-roundup-ai/ | ✅ | 2026-06-09 |
| P9 | Honeycomb Canvas https://www.honeycomb.io/platform/canvas | ✅ | 2025-11-18 |
| P10 | Honeycomb Intelligence https://www.honeycomb.io/platform/intelligence | ✅ | 2025-09-09 |
| P11 | Honeycomb Agent Observability https://www.honeycomb.io/blog/honeycomb-launches-agent-observability-full-visibility-agentic-workflows | ✅ | 2026-05-12 |
| P12 | Chronosphere NLQ https://chronosphere.io/learn/introducing-natural-language-queries/ | ✅ | 2026-05-14 |
| P13 | Chronosphere Guided Troubleshooting https://chronosphere.io/learn/ai-powered-guided-observability/ | ✅ | 2025-11-10 |
| P14 | Cribl AI 文档 https://docs.cribl.io/copilot/ | ✅ | 2026-08-05 |
| P15 | Greptile 2025 大更新（转型 review） https://www.greptile.com/blog/greptile-update | ✅ | 2025-05-30 |
| P16 | Bloop 仓库（ARCHIVED 2025-01-02） https://github.com/BloopAI/bloop | ✅ | 2026-08-05 |
| P17 | eunomia eBPF×AI 综述 https://eunomia.dev/GPTtrace/ | ✅ | 2025-02-10 |
| P18 | MCPtrace https://github.com/eunomia-bpf/MCPtrace | ✅ | 2026-08-05 |

### 6.2 学术论文（arXiv abs 页一手核实）

| # | 论文 | arXiv/DOI | 核实 | 关键数字 |
|---|------|-----------|------|---------|
| A1 | **TAAF**: Trace Abstraction and Analysis Framework（ICSE 2026） | arXiv:2601.02632 ✅abs核实 | ✅ | graph-grounding +31.2% 准确率，短区间 95.5% |
| A2 | **AgentSight**: System-Level Observability for AI Agents Using eBPF（PACMI'2025） | arXiv:2508.02736 ✅abs核实 | ✅ | <3% 开销；eBPF 拦截 TLS + kernel 事件 + LLM 因果关联 |
| A3 | **Kgent**: Kernel Extensions LLM Agent（eBPF'24, SIGCOMM workshop） | DOI:10.1145/3672197.3673434 ✅ | ✅ | 80% 语义正确率（2.67× over GPT-4 baseline） |
| A4 | **Lean4Agent**: Formal Modeling and Verification for Agent Workflow（2026-06） | arXiv:2606.06523 ✅ | ✅ | 首个 Lean4 验证 agent workflow；+11.94%；LeanEvolve +7.47% |
| A5 | **LeanCTX**: Proof-Carrying Context（GitHub PAPER.md） | yvgude/lean-ctx ✅ | ✅ | 53 Lean4 定理，0 sorry，<2s 编译；Cedar VGD 方法论 |
| A6 | **AlphaProof**（Nature 2025） | s41586-025-09833-y ✅ | ✅ | IMO 2024 银牌级；TTRL；Lean4 |
| A7 | **AlphaProof Nexus** | github.com/google-deepmind/alphaproof-nexus-results ✅ | ✅ | 9/353 Erdős + 44/492 OEIS 自主证明 |
| A8 | RCA 失败分析「Why Do AI Agents Systematically Fail at Cloud RCA」 | arXiv:2602.09937 ✅ | ✅ | **Hallucination in Interpretation 71.2%**；12 类 pitfall |
| A9 | LATS-RCA | arXiv:2605.03505 ✅ | ✅ | 生产环境 65.1%（benchmark 91.3%）；75 API calls/incident |
| A10 | KRCA（快手） | arXiv:2607.01788 ✅ | ✅ | AC@1 = 0.88；部署 6 个月降诊断时间 77.3% |
| A11 | JUSTDIAG（可问责 RCA） | arXiv:2606.19407 ✅ | ✅ | diagnostic justification；calibrated non-closure |
| A12 | Stalled/Biased/Confused RCA（FORGE'26） | DOI:10.1145/3793655.3793732 ✅ | ✅ | 48,000 场景；16 类 RCA 推理失败 |
| A13 | PRAXIS（SDG+PDG 图遍历 RCA） | arXiv:2512.22113 ✅ | ✅ | +3.1× 准确率，-3.8× token |
| A14 | CHOKE（EMNLP findings 2025）| 2025.findings-emnlp.792 ✅ | ✅ | LLM 高置信幻觉；16-43% 的「knows-but-hallucinates」 |
| A15 | CodeHalu（AAAI 2025） | ojs.aaai.org/.../34717 ✅ | ✅ | 代码幻觉四分类 + CodeHaluEval |
| A16 | LLM 解释忠实度（Walk the Talk） | arXiv:2504.14150 ✅ | ✅ | causal concept faithfulness；医疗/偏见任务误导 |

### 6.3 待核实 / 推断项

- Neo-OS 各层描述：基于本地 README/POSITION 文档 ✅
- 「Sourcegraph 不做运行时 trace / 形式化」：基于官网全部公开页面推断 ⚡（官网未明确否认，但无任何相关 feature）
- 「Cursor/GitHub Copilot Workspace 无系统级行为解释」：基于行业常识 ⚡（未逐一深挖，但这些是开发时代码工具，公认无运行时能力）
- heartpunk/learnability 定理正确性：仅读 README，未 lake build 验证 ⚠️

---

## 七、📌 下一步

1. **最高优先级（P0，1 个月内）**：出一篇 **position paper / arXiv 预印**占位「Formal Explainability for Arbitrary Complex Software」，明确引用 TAAF + Lean4Agent 并定位为「二者的教学化 + 通用化 + 硬件 ground-truth 化整合」。这是防止学术合流抢先的最便宜防御，成本 1-2 周。

2. **P0 命门验证（ROADMAP 已列）**：用 Linux + LLVM 两域做 N=2 提取五原子本体，验证「领域无关内核」假设。若 1000 commit 抽取率 < 60% 或形式化粒度无法收敛，蓝海命题动摇。

3. **竞品监控清单（建立 monthly scan）**：重点盯 4 个信号源——(a) eunomia-bpf GitHub（AgentSight/Kgent 是否扩域）；(b) Datadog/Honeycomb 是否引入「formal/causal guarantee」措辞；(c) arXiv cs.SE + cs.OS 的「trace + formal + LLM」组合论文；(d) ICSE/FSE 2027 投稿周期。

4. **对标 TAAF 做 benchmark**：Neo-OS 应在 TraceQA-100 上跑出**带形式化保证的版本**，证明 L2.5 能把 TAAF 的 95.5% 准确率背后的「幻觉」进一步压低。这是最有说服力的差异化实证。

5. **明确不做什么**：放弃「做更好的 Datadog/Sourcegraph」叙事；放弃「AI agent observability」红海（AgentSight/eunomia 已占）；锁定「**非云 + 非开发时 + 教学级 + 形式化**」四重过滤后的真蓝海（OS 内核 / 编译器 / GPU 驱动 / 游戏引擎 / 数据库内部机制的解释）。
