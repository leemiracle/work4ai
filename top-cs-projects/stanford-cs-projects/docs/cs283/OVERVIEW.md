# CS283: Governing Artificial Intelligence — Law, Policy, and Institutions

> Stanford University（政策旗舰研讨课）
> Instructors: **Sanmi Koyejo**（公平性 ML）+ **Anka Reuel**（AI 治理）+ **Rob Reich**（政治哲学）+ **Nathaniel Persily**（宪法/选举法）
> Format: 跨学院研讨 + 政策备忘录 + 案例研究
> Prerequisites: 无严格技术先修；建议对 AI 基础有了解
> Difficulty: ⭐⭐⭐⭐（跨学科深度，技术 + 法学 + 政治学交汇）
> 官网: http://cs283.stanford.edu/（建设中）

---

## 📚 课程定位

CS283 是斯坦福**AI 治理领域的旗舰课程**，其独特之处在于**四位来自不同学院的讲师联合授课**——这在斯坦福课程体系中极为罕见：

| 讲师 | 学院 | 视角 |
|------|------|------|
| **Sanmi Koyejo** | 计算机科学 | 技术可行性 / 公平性 ML / 模型审计 |
| **Anka Reuel** | 计算机科学 | AI 治理框架 / 政策制定 |
| **Rob Reich** | 政治哲学 | 民主制度 / 技术伦理 / 权力分析 |
| **Nathaniel Persily** | 法学院 | 宪法 / 选举法 / 平台监管 |

> **核心命题**：AI 不是单纯的技术问题，而是**需要法律、政策、制度协同治理的社会技术系统**。

这门课回应了一个时代命题：当 AI 系统影响选举、就业、司法、医疗时，**谁来决定 AI 应该做什么？依据什么规则？通过什么机构？**

### 课程哲学
不同于纯粹的技术安全课（如 CS120），CS283 的视角是**制度性的**：
- 技术安全问："如何让模型更安全？"
- AI 治理问："**谁有权定义'安全'？如何建立问责机制？**"

---

## 🎯 学习目标

完成 CS283 后，学生应能够：

1. **理解** AI 治理的多利益相关方框架（政府 / 企业 / 公民社会 / 学术界）
2. **分析** 现有 AI 监管框架（EU AI Act、美国行政令、中国算法管理规定）
3. **掌握** 多元价值对齐（Pluralistic Alignment）的理论基础——为什么单一价值观不够
4. **运用** 投票与偏好聚合机制（多数投票、Borda、Approval、Deliberative）
5. **评估** AI 系统的社会影响——公平性、问责性、透明性、可申诉性
6. **撰写** 政策备忘录（Policy Memo）——将技术洞察转化为治理建议
7. **批判** 技术解决方案主义——认识到有些问题不能靠技术"修好"

---

## 📅 完整模块（推断版，基于四讲师研究 + 治理框架）

### Part 1: AI 治理的基础框架
- **M1** — 为什么需要 AI 治理？（历史类比：核能、生物技术、互联网）
- **M2** — AI 的社会技术性质（不只是代码，更是人 + 制度 + 数据）
- **M3** — 治理的多层次架构（国际 → 国家 → 行业 → 企业 → 模型级）

### Part 2: 法律与监管视角（Persily + Reich）
- **M4** — AI 与选举民主（deepfake、虚假信息、选民操控）
- **M5** — AI 与宪法权利（言论自由 vs 平台内容审核）
- **M6** — 全球 AI 立法对比
  - **EU AI Act**——风险分级框架（禁止/高风险/有限/最小风险）
  - **美国**——行政令 + 部门指南（NIST AI RMF）
  - **中国**——算法推荐管理规定 + 生成式 AI 管理办法
- **M7** — 平台责任与第 230 条（Section 230）的 AI 时代挑战

### Part 3: 公平性与多元价值（Koyejo）
- **M8** — 公平性 ML 基础（demographic parity、equalized odds、calibration）
- **M9** — **多元价值对齐**（Pluralistic Alignment）⭐
  - 为什么"对齐到谁"比"如何对齐"更根本
  - Arrow 不可能性定理的 AI 含义
- **M10** — 偏好聚合机制
  - 多数投票 / Borda 计数 / Approval 投票 / Deliberative 民主
  - Condorcet 悖论——投票循环
- **M11** — 模型审计与红队测试（Red Teaming as governance tool）

### Part 4: 机构与问责（Reuel + Reich）
- **M12** — AI 治理机构设计（AI Safety Institute、独立监管机构）
- **M13** — 企业 AI 治理（OpenAI 的 Supervised Board、Anthropic 的 Long-Term Benefit Trust）
- **M14** — AI 开源 vs 闭源的治理辩论
- **M15** — 国际 AI 治理协作（AI Safety Summit、联合国 AI 机构提案）

### Part 5: 前沿议题
- **M16** — AI 与劳动（自动化、技能溢价、再培训制度）
- **M17** — AI 与隐私（数据权利、被遗忘权、联邦学习作为治理工具）
- **M18** — 通用人工智能（AGI）的治理——如何为未来做准备
- **M19** — 学生政策备忘录展示
- **M20** — 总结：迈向负责任的 AI 治理

---

## 🧮 核心概念与框架

### 1. 多元价值对齐（Pluralistic Alignment）

传统对齐范式的问题：
$$\text{单一 reward model} \quad R(s,a) \rightarrow \text{"最优"行为}$$

但**谁的 reward？** 2024 年 Sorensen 等人提出路线图：

> **核心论点**：不存在"普遍正确"的价值观，AI 系统应**显式建模和尊重价值多元性**。

技术路径：
- **Overton 窗口**：明确哪些行为可接受（范围），而非定义"最优"
- **可配置对齐**：不同用户/社区可以有不同的行为策略
- **揭示分歧**：当价值观冲突时，系统应**揭示**而非**掩盖**分歧

### 2. 投票机制比较

| 机制 | 规则 | 优点 | 缺点 |
|------|------|------|------|
| **多数投票** | 每人选 1 个 | 简单 | 忽略偏好强度 |
| **Borda 计数** | 排名赋分 | 考虑全序 | 易受策略投票 |
| **Approval** | 选多个可接受项 | 灵活 | 阈值难定 |
| **Condorcet** | 两两对决 | 理论最优 | 可能无赢家（循环）|

### 3. Condorcet 悖论

三人三候选人的经典循环：
```
投票者 1: A > B > C
投票者 2: B > C > A
投票者 3: C > A > B
```
两两对决：A 击败 B，B 击败 C，C 击败 A → **没有赢家**。

> 这是 Arrow 不可能性定理的具体体现：≥3 个候选人时，**没有完美的聚合机制**。对 AI 治理的含义是——**任何对齐方案都涉及价值权衡**。

### 4. EU AI Act 风险分级

| 风险等级 | 示例 | 监管要求 |
|----------|------|---------|
| **不可接受**（禁止）| 社会评分、操纵性 AI | 完全禁止 |
| **高风险** | 招聘、信贷、司法、医疗 | 严格合规（透明、人类监督、审计）|
| **有限风险** | 聊天机器人、深度伪造 | 透明义务（告知用户）|
| **最小风险** | 垃圾邮件过滤 | 无额外要求 |

### 5. AI 治理的红队测试

红队（Red Teaming）从攻击性测试工具**升级为治理机制**：
- 企业内部红队（OpenAI、Google）
- 政府 sponsored 红队（UK AISI、US AISI）
- 公开红队竞赛（DEF CON AI Village）

---

## 💻 项目代码（本仓库）

📁 `topic3-safety/pluralistic_safety.py`

该文件实现的内容**直接对应 CS283 Part 3 的多元价值对齐主题**：

**实现内容**：
1. ✅ **投票机制实现**（多数 / Borda / Approval / Condorcet）
2. ✅ **Condorcet 悖论演示**——经典的 A>B>C>A 投票循环
3. ✅ **PluralisticAligner**——根据用户特定价值观选择不同策略
4. ✅ **Red Teaming 框架**——5 种对抗攻击模板 + 安全/不安全 agent 对比测试

```bash
cd topic3-safety
python3 pluralistic_safety.py
```

**输出示例**:
```
📋 2. Condorcet 悖论（投票循环）
   投票者偏好: [['A','B','C'], ['B','C','A'], ['C','A','B']]
   Condorcet winner: None
   → None! 因为 A>B>C>A 循环

📋 3. Pluralistic Alignment
   u_conservative → policy p1
   u_progressive → policy p2
   u_balanced → policy p3

📋 4. Red Teaming
   安全 agent: ✅ Passed: 5, ❌ Failed: 0
   不安全 agent: ✅ Passed: 0, ❌ Failed: 5
```

> 💡 PluralisticAligner 展示了 CS283 的核心洞见：**不同用户可以有不同的对齐策略，而非强制统一**。

---

## 📊 关键论文与政策文件

### 🔴 必读（P0）
1. **Sorensen et al. 2024** "Position: Roadmap to Pluralistic Alignment" (ICML)
2. **EU AI Act**（2024 正式通过）——全球首部综合性 AI 法律
3. **Bender et al. 2021** "On the Dangers of Stochastic Parrots" (FAIR)

### 🟡 推荐（P1）
4. **Arrow 1951** "Social Choice and Individual Values"（不可能性定理）
5. **Reuel et al. 2024** AI Governance Framework（OpenAI / 学术合作）
6. **U.S. NIST AI Risk Management Framework** (2023)
7. **Acemoglu & Restrepo 2020** "Robots and Jobs"（AI 与劳动经济学）

### 🟢 政策与报告
8. **White House Executive Order on AI** (2023)
9. **UK AI Safety Institute** 首次前沿模型评估报告
10. **UNESCO AI Ethics Recommendation** (2021)
11. Selbst et al. 2019 "Fairness and Abstraction in Sociotechnical Systems" (FAT*)

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **想做 AI 政策** | CS283 + CS202（法律基础）→ 智库/政府实习 |
| **想做 AI 安全研究** | CS283 + CS329H（对齐理论）+ CS120（安全工程）|
| **想做法学+AI** | CS283 + Law School 课程 → 科技法方向 |
| **想做公平性 ML** | CS283（治理框架）+ CS329H（技术实现）|
| **产品经理/伦理官** | CS283（战略视角）+ CS202（法律风险）|

### CS283 vs CS120 vs CS202
| 课程 | 焦点 | 层次 |
|------|------|------|
| **CS283** | AI 治理的制度设计 | **社会/政策层** |
| **CS120** | AI 安全工程技术 | **技术实现层** |
| **CS202** | CS 专业人士的法律基础 | **个人合规层** |

---

## 💡 反思

### 课程优势
1. **真正的跨学科**——四位不同学院讲师带来多元视角，避免技术中心主义
2. **时代前沿**——AI 治理是 2023-2026 最热门的政策议题，内容实时更新
3. **政策实践导向**——政策备忘录训练将学术洞察转化为可操作建议
4. **多元价值视角**——Koyejo 的公平性 ML 研究为课程提供技术支撑

### 潜在局限
1. **技术深度有限**——不会深入实现 RLHF/红队工具（需 CS120/CS329H 补充）
2. **美国中心视角**——EU/中国的监管经验可能覆盖不足
3. **规范 vs 描述**——课程可能偏重"应该怎样"，而非"实际怎样"
4. **快速发展**——政策变化极快，课程内容可能滞后于实际立法

---

## 🚀 扩展阅读

完成 CS283 后推荐：
1. **CS120** — AI 安全工程的技术实现
2. **CS202** — CS 专业人士的法律基础（IP、合同、合规）
3. **CS329H** — 从人类偏好学习（对齐的技术基础）
4. Stanford HAI（以人为本 AI 研究院）的政策报告系列
5. 《AI Snake Oil》（Arvind Narayanan）—— 批判性看待 AI 宣传
6. 《The Alignment Problem》（Brian Christian）—— 对齐问题的科普读物

---

**最后更新**: 2026-08-11
**对应代码**: `topic3-safety/pluralistic_safety.py`（投票机制 + 多元对齐 + 红队测试）
**数据来源**: cs283.stanford.edu（标题确认）+ 四讲师研究 + AI 治理领域知识
