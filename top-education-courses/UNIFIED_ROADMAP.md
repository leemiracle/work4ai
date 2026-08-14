# 🗺️ 教育学 · 统一学习路线图（30 课最优路径）

> 对标 [`../top-physics-courses/UNIFIED_ROADMAP.md`]。从 79 门精选 30 课的逻辑，移植到教育学。30 课按"**学习科学的内在逻辑**"排序，每课标：**衔接关系 + 核心问题 + 推荐载体 + 知识检查（F2 门）**。
>
> ⚠️ 具体课程编号/链接 **【待联网核实】**。载体优先选**免费可得 + 共识经典**。

---

## 三条阅读路径（按角色选）

### 🅰️ 路径 A：教育研究者 / 学习科学 PhD（全 30 课，24–36 月）
按顺序走。目标是能做**循证教育研究**。

### 🅱️ 路径 B：AI 教育产品经理 / 工程师（12 课，3–6 月）
只读标 ⭐ 的课 + [`ai_for_education/`]。目标：做出不坑学生的 AI 导师。

### 🅲️ 路径 C：教师 / 家长（10 课，2–3 月）
只读标 🍎 的课。目标：用学习科学改进日常教学/育儿。

---

## 第一阶段：奠基（课 1–6）—— "学习是什么"

### 课 1 · 🍎 教育学第一问题：谁在学
- **衔接**：入口，无前置
- **核心**：教育史主线 + 中心转移（读 [`EDUCATION_FEYNMAN_NARRATIVE.md`]）
- **载体**：本库费曼叙事
- **F2 检查**：用 3 句话讲清"教育学的中心如何从教师移到学习者"

### 课 2 · ⭐ 行为主义骨架：reward 怎么塑形
- **衔接**：← 课 1
- **核心**：经典/操作性条件反射、强化程式、消退
- **载体**：[`LEARNING_THEORIES/01_behaviorism.md`] + Skinner《Science and Human Behavior》选章
- **F2**：画一个"想让学生举手发言"的强化程式

### 课 3 · ⭐ 认知主义骨架：脑内结构怎么变
- **核心**：信息加工模型、工作记忆、长时记忆、图式
- **载体**：[`LEARNING_THEORIES/02_cognitivism.md`] + 《How People Learn》(NRC, 2000)
- **F2**：解释为什么"工作记忆 4±1 chunk"决定了教学要分块

### 课 4 · 🍎 皮亚杰发展阶段 + 同化/顺应
- **核心**：四阶段、图式平衡
- **载体**：Piaget《The Psychology of the Child》选章
- **F2**：举一个"前运算儿童做不到守恒"的实验并解释原因

### 课 5 · ⭐ 维果茨基 ZPD + 支架
- **核心**：最近发展区、scaffolding、社会文化
- **载体**：[`LEARNING_THEORIES/03_constructivism.md`] + Vygotsky《Mind in Society》
- **F2**：为什么"给答案"破坏 ZPD？设计一个"恰好够"的支架

### 课 6 · 人本主义：intrinsic motivation
- **核心**：罗杰斯以学习者为中心、意义学习
- **载体**：[`LEARNING_THEORIES/04_humanism.md`] + Rogers《Freedom to Learn》
- **F2**：区分 extrinsic vs intrinsic reward，举学习中的例子

---

## 第二阶段：测量（课 7–12）—— "怎么知道学会了"

### 课 7 · ⭐ Bloom 教育目标分类法（1956/2001）
- **核心**：六层（记忆→理解→应用→分析→评价→创造）
- **载体**：[`ASSESSMENT/01_bloom_taxonomy.md`] + Anderson & Krathwohl 修订版
- **F2**：把同一道"光合作用"题，改成考六层各一层

### 课 8 · 🍎 形成性 vs 总结性评估
- **核心**：Scriven 1967 区分；Black & Wiliam "Inside the Black Box"
- **载体**：[`ASSESSMENT/02_formative_summative.md`]
- **F2**：你的课里哪些是形成性、哪些是总结性？形成性怎么加强？

### 课 9 · 项目反应理论 IRT 入门
- **核心**：能力 θ vs 题目难度 b、Rasch 模型、自适应测试 CAT
- **载体**：[`ASSESSMENT/03_psychometrics.md`] + Lord《Applications of Item Response Theory》选章
- **F2**：为什么 CAT 比固定卷更高效？数学上怎么做到

### 课 10 · 🍎 Hattie 可见学习 + 效应量
- **核心**：d 解读、顶级干预、低效神话
- **载体**：[`EDUCATION_BREAKTHROUGHS.md`] + Hattie《Visible Learning》
- **F2**：举 3 个 d>0.6 的干预和 3 个 d≈0 的神话

### 课 11 · Bloom 2 Sigma Problem
- **核心**：1984 原论文、掌握学习、规模化困境
- **载体**：[`ai_for_education/`] + Bloom 1984 原文
- **F2**：为什么 40 年无解？LLM 真能解吗，列出 2 个风险

### 课 12 · 大规模评估：PISA / TIMSS
- **核心**：国际测评设计、跨国比较的陷阱
- **载体**：OECD PISA 框架文档 **【待联网核实】**
- **F2**：PISA 排名能直接说明"教育好坏"吗？列 2 个误读

---

## 第三阶段：机制（课 13–20）—— "学习为什么会发生/不发生"

### 课 13 · ⭐ 测试效应 / 检索练习
- **核心**：检索 > 重读；Roediger & Karpicke 2006
- **载体**：[`NEUROEDUCATION/README.md`] + Brown《Make It Stick》
- **F2**：为什么 Anki 有效？设计一周复习计划

### 课 14 · 间隔效应 + 遗忘曲线
- **核心**：Ebbinghaus、SM-2 算法
- **载体**：同上
- **F2**：集中 4 小时 vs 分散 4×1 小时，哪个记得久？为什么

### 课 15 · ⭐ 认知负荷理论 (Sweller)
- **核心**：内在/外在/相关负荷；worked examples
- **载体**：Sweller 相关综述 **【待联网核实】**
- **F2**：新手为什么该看 worked example 而不是刷题

### 课 16 · 🍎 元认知与自我调节
- **核心**：Flavell、Zimmerman 三阶段
- **载体**：[`METHODS/`] + Zimmerman 综述
- **F2**：学霸和普通生在元认知上差在哪？怎么训练

### 课 17 · 反馈的科学：Hattie & Timperley
- **核心**：反馈四层（任务/过程/自我调节/自我）；"feed up/back/forward"
- **载体**：Hattie & Timperley (2007) **【待联网核实】**
- **F2**：表扬"你真聪明"为什么有害（成长型思维接口）

### 课 18 · 成长型思维 (Dweck)
- **核心**：fixed vs growth mindset； praising effort vs ability
- **载体**：Dweck《Mindset》
- **F2**：设计一句给学生的"过程表扬"

### 课 19 · 多元智能 / 学习风格：一个有效一个神话
- **核心**：Gardner 多元智能（流行但有争议）vs VARK 学习风格（**已证伪**）
- **载体**：Pashler et al. 2008 综述（学习风格证伪）**【待联网核实】**
- **F2**：为什么"匹配学习风格"无效？澄清一个流行误区

### 课 20 · 教育神经科学：脑可塑性 / 敏感期
- **核心**：突触修剪、敏感期窗口、读脑 ≠ 脑科学
- **载体**：[`NEUROEDUCATION/README.md`] + 《Mind, Brain, and Education Science》(Tokuhama-Espinosa)
- **F2**：举一个"脑科学被过度解读"的例子（如"左脑人"神话）

---

## 第四阶段：教学（课 21–25）—— "怎么教"

### 课 21 · 🍎 直接教学 vs 发现学习之争
- **核心**：Project Follow Through 数据；Kirschner/Sweller/Clark 2006 "最小指导失败"
- **载体**：[`METHODS/01_direct_instruction.md`]
- **F2**：为什么"纯发现"对新手有害？建构主义错了吗

### 课 22 · 掌握学习 + 翻转课堂
- **核心**：Bloom 掌握学习；Khan Academy 翻转
- **载体**：[`METHODS/03_mastery_flipped.md`]
- **F2**：翻转课堂的前提条件是什么（少了就翻车）

### 课 23 · 项目式学习 PBL
- **核心**：Buck Institute 框架；PBL 的支架
- **载体**：[`METHODS/02_discovery_pbl.md`]
- **F2**：PBL 的最大陷阱是什么

### 课 24 · 苏格拉底法 / 案例法
- **核心**：产婆术、哈佛法学院案例法
- **载体**：[`METHODS/04_socratic_case.md`]
- **F2**：苏格拉底法什么时候有效什么时候失效

### 课 25 · 课程理论：Tyler / Wiggins & McTighe 逆向设计
- **核心**：目标先于活动；UBD
- **载体**：Wiggins & McTighe《Understanding by Design》
- **F2**：用 UBD 倒推设计一节课

---

## 第五阶段：AI 时代（课 26–30）—— "机器怎么教"

### 课 26 · ⭐ ITS 智能辅导系统史
- **核心**：从 SCHOLAR/ACT-R 到 ASSISTments / Cognitive Tutor
- **载体**：[`ai_for_education/`] + VanLehn (2011) "The Relative Effectiveness of ITS" **【待联网核实】**
- **F2**：ITS 的效应量为什么 ~0.7 但没普及（成本/通用性）

### 课 27 · ⭐ 自适应学习算法
- **核心**：IRT-based、贝叶斯知识追踪 BKT、深度知识追踪 DKT
- **载体**：[`ai_for_education/`] + Piech et al. 2015 DKT 论文
- **F2**：DKT 比 BKT 强在哪？局限是什么

### 课 28 · ⭐ LLM 导师设计：Khanmigo / Prompt 教育学
- **核心**：苏格拉底 prompt、不给答案只给提示、幻觉缓解
- **载体**：[`ai_for_education/`] + [`../讲透Prompt/`] + Khanmigo 设计公开材料 **【待联网核实】**
- **F2**：写一个"苏格拉底式数学辅导"prompt，让 AI 不直接给答案

### 课 29 · ⭐ 教育大模型的对齐与评估
- **核心**：教育领域 RLHF、学生模型 vs 教师模型、hallucination 在教育里的致命性
- **载体**：[`../讲透RL/`] + 最新 Ed-LLM 论文 **【待联网核实】**
- **F2**：教育场景的对齐和通用对齐差在哪（错不起）

### 课 30 · 闭环：教育学 ↔ AI 镜像
- **核心**：本项目元主张；学习 = RL 的两面
- **载体**：[`CROSS_DISCIPLINARY.md`] + [`../强化学习视角-元迭代器.md`]
- **F2**：用 RL 语言重述维果茨基的 ZPD（这是毕业题）

---

## 知识检查总原则（F2 费曼门）

每一课结束，必须能：
1. **用自己的话讲给外行听**（费曼 F1）
2. **指出一个反直觉点**（F2 卡壳点）
3. **举一个本课之外的例子**（迁移）
4. **说清"它什么时候失效"**（边界——这是 Hattie 的精神）

做不到任何一条 = 没真懂，回炉。

---

> 🎮 **RL 视角**：这 30 课本身就是一条**精心设计的 curriculum**——按 ZPD 排序，每课依赖前置，反馈点在 F2。这份路线图就是它自己理论的实践。
>
> 📌 **下一步**：选你的路径（A/B/C），从对应第 1 课开始。每完成一课在本文件对应行打 ✓。
