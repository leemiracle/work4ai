# Prompt 综述精华 · 四篇地图

> **定位**：`讲透Prompt/` 的外部学术地图——四篇高影响力综述的核实蒸馏 + 与本系列章节的映射。补上系列缺失的"自动 Prompt 优化（APO）"学术层。
> 来源：用户提供清单 → 逐篇 arXiv abs 页核实（2026-08-17），非凭记忆。标 ✅ = 已核实的 arXiv abs 页信息。

---

## 一、四篇定位矩阵

| 综述 | 视角 | 规模 | 机构 | 独有价值 | 状态 |
|---|---|---|---|---|---|
| **The Prompt Report** ✅ [arXiv:2406.06608](https://arxiv.org/abs/2406.06608) v6 2025-02 | 分类学本体论 | 33 术语 + 58 文本技术 + 40 多模态技术 | 马里兰（Schulhoff/Carpuat/Resnik）+ OpenAI（Anadkat）等 31 人 | **领域标准词汇表**——解决"术语冲突+本体碎片化"（原话 conflicting terminology and a fragmented ontological understanding）；配网站 [trigaten.github.io/Prompt_Survey_Site](https://trigaten.github.io/Prompt_Survey_Site/) | 最全面 |
| **Sahoo et al.** ✅ [arXiv:2402.07927](https://arxiv.org/abs/2402.07927) v2 2025-03 | 按应用领域 | 29+ 技术 × (方法/应用/模型/数据集) 四栏 | IIT Patra + AI5（Saha/Jain/Chadha） | **应用对照表**——每技术附 strengths/limitations + 数据集清单；被引最高（2000+） | 入门首选 |
| **APE 优化视角** ✅ [arXiv:2502.11560](https://arxiv.org/abs/2502.11560) | 优化理论统一 | 跨模态全谱 | 北邮（Wenwu Li/Xiangfeng Wang 等） | **首个优化理论框架**：prompt 优化 = 离散/连续/混合空间上的最大化问题；4 计算范式分类 | 理论最深 |
| **AWS APO 综述** ✅ [arXiv:2502.16923](https://arxiv.org/abs/2502.16923) **EMNLP 2025 主会** | 黑盒 APO 工程框架 | 5-part taxonomy | Amazon AWS（Ramnath 等 21 人） | **5 维工程拆解**：在哪优化/优化什么/优化准则/候选生成算子/迭代搜索算法；具体方法谱系最全 | 工程最实用 |

另：**iScience 2025-06（Cell 子刊）**"Unleashing the potential of prompt engineering"——非 arXiv，跨学科受众（含 VLM prompt + 安全对抗章），定位为学术期刊版科普，不单独展开。

**四篇关系**：Report 管"有什么技术"（本体），Sahoo 管"用在哪"（应用），2502.11560 管"为什么能优化"（理论），2502.16923 管"怎么自动搜"（工程）——本体→应用→理论→工程，恰好四层。

---

## 二、The Prompt Report 核心提炼（2406.06608）

### 2.1 术语体系（33 术语中最关键的 8 个）

| 术语 | 定义要点 |
|---|---|
| Prompting | 与 GenAI 交互的全部输入行为（超类）|
| Prompt Engineering | **迭代地**组合/测试/选择 prompt 的系统性过程——关键词是迭代，非一次性 |
| Prompt / Prompting Technique | 输入本体 / 改变 prompt 的抽象操作（技术≠模板）|
| Zero/Few-Shot | 无示例 / 1-N 示例（few-shot ⊂ in-context learning）|
| Thought Generation | 让模型生成推理过程（CoT 是其子类）|
| Decomposition | 任务拆分（least-to-most / plan-and-solve）|
| Ensembling | 多 prompt/多路径投票（Self-Consistency 是其子类）|
| Self-Criticism | 模型自检输出（Self-Refine/Chain-of-Verification）|

### 2.2 58 技术的六族分类（用户八类表的修正版）

用户表里的 Meta/Role Prompting 实际是 Instruction/Prompt 模板层的子技术；Report 主分类树为：**Zero-shot 族 / Few-shot 族（含示例选择与排序）/ Thought Generation 族（CoT+变体）/ Decomposition 族 / Ensembling 族 / Self-Criticism 族**——注意 Self-Consistency 属 Ensembling 不属 CoT，ToT 属 Thought Generation 的搜索扩展。

### 2.3 实践要点（论文 best practices 章精选）

1. **迭代是定义的一部分**：手工 prompt 工程的有效性来自循环改进，不是灵感。
2. SOTA 模型的建议随版本变化（v6 已更新到 2025 模型观）：**先 zero-shot 指令化，失败再 few-shot，再上推理技术**——与本系列阅读顺序一致。
3. 评测必须与具体模型版本绑定（prompt 敏感性 = 模型敏感性）。

---

## 三、APO 双综述提炼（自动 Prompt 优化——本系列最大增量）

### 3.1 优化理论框架（2502.11560）

**统一形式化**：$\max_{P \in \mathcal{P}} \mathbb{E}_{(x,y) \sim \mathcal{D}_{val}} [g(f(P(x)), y)]$，其中 prompt 空间三分：

| 空间 | 变量 | 可微性 | 代表方法 |
|---|---|---|---|
| 离散 $\mathcal{P}_d$ | 硬指令 I / 思维序列 T / few-shot 示例 $\{e_i\}$ | ❌ 组合爆炸 | APE/ProTeGi/EvoPrompt/DSPy |
| 连续 $\mathcal{P}_c$ | 可学习嵌入 $\theta_i \in \mathbb{R}^d$（soft prompt）| ✅ 梯度直接可用 | Prefix-Tuning/Prompt-Tuning/P-Tuning |
| 混合 $\mathcal{P}_h$ | 离散×连续 | 部分 | 离散化投影（soft→hard 回译）|

VLM 特有：空间标注 prompt $[I,T,R_1..R_m; x]$（bbox/marker/mask/多边形）。

**四计算范式**：① FM-based（LLM 当优化器：OPRO/DSPy——"FM as optimizer"）② 进化计算（EvoPrompt = FM 生成 × 遗传算子）③ 梯度（soft prompt 直接 SGD；离散需近似）④ 强化学习（策略梯度估计离散梯度）。

### 3.2 黑盒 APO 工程框架（2502.16923，AWS，EMNLP 2025）

**黑盒三特征**：无需参数访问 / 系统化搜索解空间 / **保持人类可读**（这是 APO 相对微调的核心卖点）。

**5-part 拆解**（工程师视角的方法谱系）：

| 维度 | 选项谱系 |
|---|---|
| 优化空间 | 离散指令 / 示例选择+排序 / soft prompt |
| 种子来源 | 人写（ProTeGi）/ APE 诱导（几百样本够）/ README 诱导（SCULPT）/ 模板填充（UniPrompt）|
| 候选生成算子 | **文本梯度**（ProTeGi：LLM 反馈≈"梯度方向"；TextGrad 同路）/ MCTS（PromptAgent 四步：选择-扩展-模拟-回溯）/ 遗传（SPRIG：300 组件语料 add/rephrase/swap/delete；CLAPS：K-means 聚类留 top-2000 词）/ 元提示（OPRO/PE2：解法+分数进 meta-prompt）/ 微调小模型当优化器（BPO 7B 对齐 / FIPO 本地化保隐私）/ GAN 对抗式 |
| 评估准则 | 任务指标 / 多目标（Jafari：体积法优于简单加权；SOS：安全分纳入目标）|
| 迭代算法 | 贪心 / 束搜索 / 蒙特卡洛 / 遗传 / 测试时动态（Prompt-OIRL：离线奖励模型+best-of-N 按查询选 prompt）|

**理论锚点**：AlignPro (2025) 给出离散 prompt 优化的**收益上界** + 相对 RLHF 最优策略的次优差距——prompt 优化有天花板，非万能。

### 3.3 与本系列的关系

本系列 00-08 讲的是"手工技术"（对应 Report 的 58 技术），APO 是"让机器搜 prompt"（对应 3.1/3.2）——**04 上下文工程与评估 是最近的挂载点**（评测 = 优化的目标函数），但 APO 值得独立小节。已有实战桥：[`../Agent框架案例/prompt工程工具链/`](../Agent框架案例/prompt工程工具链/README.md) 六仓蓝图（optimizer/promptfoo）正是 APO 落地工具。

---

## 四、四篇 ↔ 讲透Prompt 章节映射（补桥互链）

| 本系列章节 | 对应综述内容 | 增量提示 |
|---|---|---|
| 00-为什么Prompt是控制信号 | Report 术语表（Prompting 定义/迭代性）| "prompt=P(输出\|输入)的条件" 与 Report 本体论互补：我们给数学，它给词汇 |
| 01-Few-shot与ICL | Report Few-shot 族（示例选择/排序敏感）| Sahoo 应用表：哪些任务 few-shot 增益最大 |
| 02-CoT思维链 | Report Thought Generation 族 | — |
| 03-结构化输出 | Report 模板技术 | — |
| 04-上下文工程与评估 | APO 评估准则层 | 已加"评估的下一站是自动优化"参考节 |
| 05-SelfConsistency | Report **Ensembling 族**（非 CoT 族）| 分类归属修正 |
| 06-TreeofThoughts | Thought Generation 的搜索扩展 | PromptAgent 用 MCTS 优化 prompt = ToT 思想反哺 APO |
| 07-ReAct | Report 工具使用相关技术 | APE 综述 frontier：agent-oriented prompt design 是未开垦地 |
| 08-Prompt安全 | iScience 对抗防御章 | SOS：安全分纳入多目标优化 |
| **09-Prompt自动优化** ✅ 已立项 | **APO 双篇全量落地**（2502.11560 形式化 + 2502.16923 5-part + 方法谱系表 + 决策树 + 实验 09_apo.py 四铁证）| 地图 §三的实体化 |
| 总纲 5W3H（22 手段）| Report 58 技术 | 完整映射见下表 |

### 22 手段 ↔ Report 六族 完整映射表

| 总纲族（按激活力度）| 手段 # | Report 归属 | 备注 |
|---|---|---|---|
| A 思维链家族 | 1-2 | Thought Generation | CoT 主干 |
| A 思维链家族 | 3-4 | **Ensembling**（非 CoT）| SC/USC 是采样投票——归属修正点 |
| B 思维结构 | 5-6 | Thought Generation（搜索扩展）| ToT/GoT 超出线性 CoT |
| B 思维结构 | 7-8 | **Decomposition** | L2M/Plan-and-Solve 是任务拆分不是推理链 |
| C 反思与自改 | 9-11 | Self-Criticism | Reflexion/Self-Refine/Self-Critique |
| D 推理+行动 | 12-13 | 工具使用组合（Report 边缘）| ReAct 是 CoT×工具的组合技术 |
| E Persona | 14 | Role Prompting（指令模板子层）| 不在六族顶层 |
| E Persona | 15 | Multi-Agent Prompting | 多 agent 辩论类 |
| F 情绪触发 | 16-17 | 指令措辞类（实证弱）| Report 收录但证据级别低 |
| G 格式约束 | 18 | Self-Criticism（验证后答）| — |
| G 格式约束 | 19 | **超出 Report 范围** | 约束解码在解码层不在 prompt 层（03 章承接）|
| H 外部增强 | 20 | **超出 Report 范围** | RAG 在检索层（讲透RAG 承接）|
| H 外部增强 | 21 | Self-Criticism 扩展 | Constitutional AI 循环 |
| H 外部增强 | 22 | **超出 Report 范围** | APO 爆发在 Report(2024-06) 之后 → **09 章承接** |

映射揭示的结构：总纲 22 手段中 **19 个落在 Report 六族内**，3 个越界（RAG/约束解码/APO）恰好对应"prompt 层之外的三层"（检索层/解码层/优化层）——总纲比 Report 走得更宽，Report 比总纲分得更细。

---

## 五、一级论文索引（综述引用的核心论文，arXiv 逐个核实 ✅ 2026-08-17）

> 综述是地图，这是地图标注的城池。核实方法：arXiv abs 页 / 官方 repo / 权威综述参考文献交叉（APE 的 ID 取自 OPRO ICLR 2024 论文参考文献原文）。

### 5.1 APO 方法谱系（六方法 + 位置）

| 论文 | arXiv | 发表 | 机构 | 核心贡献 | 在四范式中的位置 |
|---|---|---|---|---|---|
| APE（Zhou et al. 2022）| [2211.01910](https://arxiv.org/abs/2211.01910) | ICLR 2023 | UofT/MS 等 | LLM 反向诱导指令；几百样本够用 | FM as optimizer（起点）|
| ProTeGi（Pryzant et al.）| [2305.03495](https://arxiv.org/abs/2305.03495) | **EMNLP 2023** | Microsoft | 文本梯度 + Beam Search | 梯度（离散近似）|
| OPRO（Yang et al.）| [2309.03409](https://arxiv.org/abs/2309.03409) | **ICLR 2024** | Google DeepMind | 轨迹优化；GSM8K +8% / BBH +50% vs 人写 | FM as optimizer |
| DSPy（Khattab et al.）| [2310.03714](https://arxiv.org/abs/2310.03714) | **ICLR 2024** | Stanford | 声明式编译框架 | 编译器（统一外壳）|
| MIPRO（Opsahl-Ong et al.）| [2406.11695](https://arxiv.org/abs/2406.11695) | **EMNLP 2024** | Stanford | 贝叶斯代理联合搜指令+示例 | FM + 搜索混合 |
| TextGrad（Yuksekgonul et al.）| [2406.07496](https://arxiv.org/abs/2406.07496) | **NeurIPS 2024** | Stanford | 文本自动微分；GPT-4o GPQA 51%→55% | 梯度（泛化）|

代码锚点：OPRO→[google-deepmind/opro](https://github.com/google-deepmind/opro)；ProTeGi→[microsoft/LMOps/prompt_optimization](https://github.com/microsoft/LMOps)；DSPy/MIPRO→[stanfordnlp/dspy](https://github.com/stanfordnlp/dspy)；TextGrad→[zou-group/textgrad](https://github.com/zou-group/textgrad)。

### 5.2 谱系的"下一跳"（二批核实时从引用网络挖到，留观）

| 论文 | 方向 | 留观理由 |
|---|---|---|
| GEPA（Agrawal 2025）| 反思式 prompt 进化，声称胜 RL | APO frontier，若做 09 章扩展则核实 |
| EvoAgentX [2507.03616](https://arxiv.org/abs/2507.03616) | TextGrad/AFlow/MIPRO 整合进 agent 工作流进化（GAIA +20%）| APO×多 Agent 汇流——与讲透Agent 自演化（arXiv:2507.21046 What 轴）对接 |
| Promptbreeder | 自指涉 prompt 进化（父 prompt 进化出子 prompt 的变异提示）| 进化范式深水区 |

### 5.3 SE 实证线论文（详见 [Prompt-SE实证线](./Prompt-SE实证线-软件工程.md)）

| 论文 | 锚点 | 状态 |
|---|---|---|
| Which Prompting Technique Should I Use? | [2506.05614](https://arxiv.org/abs/2506.05614) | ✅ 14 技术×10 SE 任务×4 模型 |
| Do Advanced LMs Eliminate the Need for PE? | [2411.02093](https://arxiv.org/abs/2411.02093) | ✅ 推理模型 zero-shot 常更优（GPT-4o 90.4→96.3 vs o1-mini 93.9 零提升）|
| MDPI SE-PE SLR（42 篇）| [mdpi 6(9):206](https://www.mdpi.com/2673-2688/6/9/206) | ✅ 四簇：手工/RAG/CoT/自动调优 |
| PET 可复现性危机（Vaugrante et al.）| TMLR 2025 | ✅ 6 技术×7 模型几乎全无显著增益 |
| 推理进步真相（McGinness & Baumgartner）| [2505.19676](https://arxiv.org/abs/2505.19676) / [2509.12645](https://arxiv.org/abs/2509.12645) | ✅ 隐藏 CoT 解释 2023→2024 提升 |

---

## 六、差距分析与下一步

1. ~~**本系列缺 APO 章**~~ ✅ **已解决（2026-08-17）**：[09-Prompt自动优化.md](./09-Prompt自动优化.md) 立项落盘——五幕全展开（直觉/数学/方法谱系速查表/决策树/四坑/三步落地）+ 实验 [09_apo.py](./experiments/09_apo.py) 四铁证（梯度 93.4% vs 随机 70.5%；差种子+好算子 40/50 反超好种子+差算子；一轮 49%→96.5%；上界 96.5%≠100%）。22↔58 映射表也已补全（§四）。
2. **根 README 的讲透Prompt 条目**无需动（系列完整度未变）。
3. ~~实验机会~~ ✅ 已跑：ProTeGi 式文本梯度 toy 版实跑验证——"好种子+差算子 不如 差种子+好算子"**成立**（40/50 反超）。反直觉发现的幕后：第一版玩具特征库只有 3 个（随机 6 轮必然撞满，差异不可见），加入 6 个干扰项后才拉开——**"搜索空间里干扰项的存在才是方向信息值钱的前提"**，这本身是 APO 的一个更深的注脚。
4. **SE 实证延伸** ✅（2026-08-17 二批）：[Prompt-SE实证线-软件工程.md](./Prompt-SE实证线-软件工程.md)——Prompt-SE 2026 研讨会（已核实）+ 定量骨架 2506.05614（14 技术×10 SE 任务×4 模型，其六族组织与本地图 §四 映射同构）+ 可复现性危机两证据线；对"综述说什么"补上"证据说什么"。

---
生成：2026-08-17 · arXiv 核实：2406.06608 v6 / 2402.07927 v2 / 2502.11560 / 2502.16923（EMNLP 2025 main）全 ✅
