# Prompt 实证线 · 软件工程场景（Prompt-SE）

> **定位**：[Prompt综述精华-四篇地图](./Prompt综述精华-四篇地图.md) 的 SE 延伸——综述给"有什么技术"，实证线给"**证据说什么**"。核心问题：**这些 prompt 技术在真实 SE 任务上到底有没有用？**
> 核实纪律：✅ = conf.researchr.org / arXiv abs 一手核实（2026-08-17）；⚠️ = 用户转述未核实，引用前先验。

---

## 一、证据地图（按可信度排序）

| 证据 | 核实状态 | 一句话结论 |
|---|---|---|
| **Which Prompting Technique Should I Use?** [arXiv:2506.05614](https://arxiv.org/abs/2506.05614) | ✅ | 14 技术 × 10 SE 任务 × 4 模型系统评测：**没有万能技术**，任务×模型对齐才是关键 |
| **Prompt-SE 2026 研讨会**（EASE 2026, Glasgow 6.9-12）| ✅ conf.researchr.org | 首个 SE 实证 prompt 工程专门论坛；EASE 是 CORE-A，最佳论文进 EMSE 特刊（Springer）|
| ├─ Qualitative Coding 论文 | ✅ 页面摘要全核实 | controlled 实证 + κ 一致性 + 十次重复方差分析 |
| ├─ Extract the Gold | ✅ 页面摘要全核实 | ⚠️ **结论修正**：上下文重置**不省总能耗**，但稳定消耗曲线/削峰 |
| **PET 可复现性危机**（Vaugrante et al., TMLR 2025）| ✅ | 7 模型 × 6 技术 × 5 基准复现：**几乎全部技术无统计显著增益** |
| **推理进步的真相**（McGinness & Baumgartner, 2505.19676/2509.12645）| ✅ | 2023→2024 推理提升主要来自**隐藏系统提示/自动 CoT 训练**；2025 思考模型才真正近满分 |
| **"高级模型还需要 PE 吗？"** [arXiv:2411.02093](https://arxiv.org/abs/2411.02093) | ✅（2026-08-17 二次核实）| **推理模型内置推理降低复杂 prompt 收益，zero-shot 常更优**；执行反馈/精确任务指导仍有效——TOSEM 线（用户称刊于 ACM TOSEM 2025）|
| **MDPI 2025 SE-PE 系统综述** [mdpi.com/2673-2688/6/9/206](https://www.mdpi.com/2673-2688/6/9/206) | ✅（2026-08-17 二次核实）| 42 篇 SLR + 共被引网络：**四大簇**（手工 crafting / RAG / CoT / 自动调优）；提出模块化 PE 框架（human-in-the-loop + 自动优化 + 版本控制）|
| Prompt-SE 其余 4 篇（Novice/Goal Extraction/Commit 分类/TDD Governance）| ⚠️ 标题来自转述 | 研讨会真实存在，4 篇标题待 conf 页逐篇核 |

---

## 二、定量骨架：14 技术 × 10 SE 任务 × 4 模型（2506.05614）

### 2.1 设计（值得抄的实验方法）

- 46 技术 → 过滤三原则 → **14 技术**：①功能重复只留一个（ES-KNN vs Vote-K）②排除组合术（DENSE）③**排除依赖外部工具的**（ReAct 出局——测的是 prompt 本身）
- 14 技术按 **The Prompt Report 六族**组织（Zero-Shot/Few-Shot/Thought Generation/Ensembling/Self-Criticism/Decomposition）——与[四篇地图 §四](./Prompt综述精华-四篇地图.md)的六族映射完全同构，可直接对照
- 10 SE 任务：代码生成/修 bug/代码 QA/克隆检测/异常类型/断言生成/代码翻译等；4 模型含 Llama、DeepSeek、o3-mini

### 2.2 核心发现（可操作结论）

1. **没有常胜将军**：无任何技术在所有任务×模型上稳定最优——"prompt 工程必须实证，不能抄通用最佳实践"。
2. **ES-KNN（示例选择）最稳**：跨任务强——结构化指导 + 相关示例是对症的；**Role Prompting 是性价比之选**（低成本换不错收益）。
3. **o3-mini 行为异常**：与其他模型模式不同——**换模型（尤其推理系）必须重测 prompt**，提示词跨模型不可迁移。
4. **Token 经济学**：代码生成/修 bug 的 prompt 压缩平均省 **8000+ token/prompt**；大模型（Llama/DeepSeek）比 o3-mini 更可压缩——prompt 优化=省钱工程。

### 2.3 决策表（SE 场景速查）

| 你的任务 | 首选 | 次选 | 依据 |
|---|---|---|---|
| 代码生成/修 bug | ES-KNN few-shot（有相似历史案例时）| 结构化指令+CoT | 2506.05614 ES-KNN 强跨任务 + Vibe Coding TDM |
| 低预算批量任务 | Role Prompting | zero-shot 直答 | 性价比发现 |
| 代码评审/分类（commit/异常）| few-shot + 明确输出 Schema | — | Prompt-SE commit 分类论文方向 |
| 多轮长会话开发 | **上下文重置（GE 摘要重启）** | — | GE：不省总能耗但削峰稳曲线，防上下文膨胀 |
| 换了新模型/推理系模型 | **全部重测**，勿迁移旧 prompt | 从 zero-shot 基线重新出发 | o3-mini 异常 + TOSEM 方向线索 |
| 定性研究/编码辅助 | multi-shot（模型相关！）| — | κ 提升仅对 Claude Haiku 显著（p=0.004），DeepSeek 无感 |

---

## 三、Prompt-SE 2026：实证方法论的示范（两篇详解）

### 3.1 Qualitative Coding（✅ 全数字核实）

- **设计**：3 模型（Claude Haiku/DeepSeek-Chat/Gemini 2.5 Flash）× 2 策略（zero-shot vs multi-shot 每类 7 示例）对 116 条 SE 社区"心理安全"引文定性编码；**每配置独立跑 10 次**；Cohen's κ 为主指标 + Wilcoxon 检验。
- **发现**：①multi-shot 仅对 Claude Haiku 显著（Δκ=+0.034, p=0.004），对 DeepSeek 无感（Δκ≈-0.001）——**few-shot 增益是模型属性不是通用规律**；②稳定性分化：DeepSeek/Claude SD≈0.017 vs Gemini SD=0.038；③全模型系统性**过度预测"分享负面反馈"（bias 高至 5.25×）、低估"表达担忧"**——LLM 编码有方向性偏见，用于社会科学前必须校准。
- **方法论金标准**：控制实验 + 多运行方差 + 跨模型对比 + 效应量报告——这正是"实证 prompt 工程"该有的样子。

### 3.2 Extract the Gold（✅ 含结论修正）

- **设计**：10 名 CS 本科生用本地意大利语 LM 做编程任务，中途一组做"Gold Extraction"（对话蒸馏为摘要→重启上下文），CodeCarbon 监测能耗。
- **发现（修正转述）**：GE **不一定降低总能耗**，但让消耗模式更规律、削平上下文增长导致的峰值——价值在**稳定性/可预测性**，不在省钱。对生产环境（容量规划/削峰）仍有意义。

---

## 四、更大的背景：prompt 技术的"证据危机"

两条 ✅ 核实的证据线，动摇了"堆 prompt 技巧"的默认假设：

1. **可复现性危机**（TMLR 2025）：CoT/EmotionPrompting/RaR/ExpertPrompting 等 6 技术 × 7 模型 × 5 基准（人工双检子集）复现——**几乎全部无统计显著差异**；指出既往研究的方法学缺陷（多重比较/ cherry-picking）。
2. **推理进步的真相**（2505.19676 → 2509.12645 扩展）：GPT4→GPT4o/Claude Opus 的"推理提升"主要由**隐藏系统提示 + 训练注入自动 CoT** 解释（token 数证据）；2025 思考模型（o3/Gemini 2.5 Pro）才在 PrOntoQA 近满分；且 **小 LLM + Z3 SMT 求解器以极小代价达到同级**——神经符号路线对用户 Lean4 路线是直接佐证。

**综合启示**（对讲透Prompt 全系列的校准）：
- prompt 技术的效果 = f(模型版本, 任务, 测法)——**引用任何"XX 技术有效"都应要求：哪个模型？哪个基准？统计检验了吗？**
- 模型越新，简单 prompt 越接近复杂 prompt（自动 CoT 内化）——**复杂技巧的半衰期在缩短**，zero-shot 基线的重要性在上升（与本系列阅读顺序"先 zero-shot"一致）。
- 这不是"prompt 工程已死"：结构化指导/示例选择/输出 Schema（03 章）/上下文工程（04 章）仍是实证稳健的；死的是**玄学技巧**。

### 4.1 定量锚点：TOSEM 线论文的三组数字（arXiv:2411.02093 ✅）

- **GPT-4o 代码生成**：zero-shot 90.4% → AgentCoder 96.3%（非推理模型仍吃 PE，但增益收窄）。
- **o1-mini**：zero-shot 就 93.9%，PE 技巧**零或负增益**——推理模型的内置 CoT 吞掉了 prompt 技巧的空间。
- **CoT 步长分析**（300 样本实测）：o1-mini 内置 CoT ≥5 步的问题上比 GPT-4o 好 16.67%，<5 步只好 2.89%——**推理模型的溢价集中在真正需要多步推理的问题**；代码摘要这类无需推理的任务，推理模型无优势还更贵。
- 实操结论：任务不需复杂推理 → 非推理模型 + 好基线 prompt；需要多步推理 → 推理模型 + zero-shot，别堆技巧，省下的预算投给执行反馈（测试/lint）。

**二批补充发现**（同轮核实挖到）：GEPA（Agrawal 2025，反思式 prompt 进化可胜 RL）与 EvoAgentX（arXiv:2507.03616，把 TextGrad/AFlow/MIPRO 整合进 agent 工作流进化）——APO 正在从"单 prompt 优化"走向"多 agent 管线优化"，与 [09 章](./09-Prompt自动优化.md) 的 frontier 判断（agent-oriented prompt design 是未开垦地）互证。

---

## 五、与项目的挂点

| 挂点 | 关系 |
|---|---|
| [09-Prompt自动优化](./09-Prompt自动优化.md) | APO 的前提是"评估可靠"——§四 的证据危机 = APO 目标函数设计的警示（metric 错，优化放大错）|
| [四篇地图](./Prompt综述精华-四篇地图.md) | 六族映射 ↔ 2506.05614 的 14 技术六族组织，互为验证 |
| [讲透代码生成/](../讲透代码生成/README.md) | ES-KNN↔CEM 模式；GE↔上下文管理；TDD Governance 论文↔TDM 测试驱动模式 |
| [harness 精华](../harness精华合入-总入口.md) | TDD Governance for Multi-Agent = "验证即证据"公理的 prompt 层实现 |
| 用户 Lean4/数学路线 | LLM+Z3 神经符号证据：形式化工具组合是弯道超车道 |

## 六、留观清单

| 线索 | 动作 |
|---|---|
| ~~ACM TOSEM"高级模型还需要 PE 吗"~~ | ✅ 已核实（arXiv:2411.02093，见 §一/§4.1）；期刊版本（TOSEM 2025）页码待查但不影响引用 |
| ~~MDPI 42 篇 SLR~~ | ✅ 已核实（mdpi.com/2673-2688/6/9/206，见 §一）；"SDLC 全阶段"为转述说法，实测以四簇结构为准 |
| Prompt-SE 其余 4 篇（Novice/Goal Extraction/Commit 分类/TDD Governance）| ⚠️ 标题来自转述；需要时逐篇 webfetch conf.researchr.org 详情页 |
| EMSE 特刊（2027-03 截稿）| 长线观察：Prompt-SE 扩展版论文会含增量实验 |
| GEPA（反思式 prompt 进化胜 RL）| 二批新发现，若深挖 APO frontier 则核实全文 |

---
生成：2026-08-17 · 核实：conf.researchr.org（Prompt-SE 2026 两篇摘要页）+ arXiv 2506.05614 / 2505.19676 / 2509.12645 + TMLR 2025 ✅ · TOSEM/MDPI/4 篇标题 ⚠️ 转述待核
