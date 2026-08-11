# CS120: Introduction to AI Safety

> Stanford University, Autumn 2026
> Instructor: **Zachary Robertson** (也是 CS221 讲师!)
> Time: Tue/Thu 11:30-12:50, Hewlett 102 (anticipated)
> Prerequisites: 无官方先修（推荐 ML/统计）
> Difficulty: ⭐⭐⭐⭐
> 官网: https://stanford-cs120.github.io/fall2026/

---

## 📚 课程定位

**Stanford 首门本科 AI Safety 课**。2026 秋首次开设。

> "AI Safety 取决于 3 个维度：
> 1. 人类输入怎么被应用
> 2. unintended effects 怎么产生
> 3. 能否被有意义的评估 + 审计"

---

## 📅 完整模块（11 周 20 讲）

### Week 1: What is AI Safety?
- **L1 (Sep 22)** — What does safe AI mean?
- **L2 (Sep 24)** — Foundation models and the AI dev pipeline

### Week 2: Human Feedback + Pluralism
- **L3 (Sep 29)** — Human feedback, preferences, reward models
- **L4 (Oct 1)** — **Pluralism, disagreement, preference aggregation**

### Week 3: Data Work
- **L5 (Oct 6)** — Data work, curation, documentation
- **L6 (Oct 8)** — **Labor, provenance, institutional choices**

### Week 4: Failure Modes
- **L7 (Oct 13)** — Unintended effects, sociotechnical failure
- **L8 (Oct 15)** — Robustness, distribution shift, deployment context

### Week 5: Evaluation Validity
- **L9 (Oct 20)** — What makes an evaluation valid?
- **L10 (Oct 22)** — **Benchmarks, contamination, measurement limits**

### Week 6: Red Teaming + Interpretability
- **L11 (Oct 27)** — Red teaming and adversarial evaluation
- **L12 (Oct 29)** — Interpretability and evidence about model behavior

### Week 7: Scalable Oversight
- **L13 (Nov 5)** — **Human oversight, scalable supervision** ⭐
  - 当 AI 能力 > 评估者时怎么办？
  - Debate / IRIS / Weak-to-Strong

### Week 8: Audits + Governance
- **L14 (Nov 10)** — Evaluating increasingly capable systems
- **L15 (Nov 12)** — Case study / Guest
- **L16 (Nov 17)** — **Audits, access, third-party evaluation**
- **L17 (Nov 19)** — **Governance, assurance, oversight institutions**

### Week 11: Synthesis
- **L18 (Dec 1)** — Final project workshop
- **L19 (Dec 3)** — Synthesis: building auditable and governable AI

---

## 🎯 5 大核心主题

### 1. Human Feedback 的政治学
偏好不统一，怎么 aggregate？→ Arrow 不可能性定理

### 2. Data Work
标注员工作条件 / 数据出处 / 同意
→ 🔴 Longpre 2024 *Data Authenticity Broken*

### 3. 评估的有效性
benchmark 怎么被污染？怎么 measure "true capability"？
→ Press *How to Build Good Benchmarks*

### 4. Scalable Oversight ⭐
当 AI > 评估者时怎么办？→ OpenAI Superalignment（已解散）

### 5. 第三方审计
政府 / 学术界 / 公民社会怎么 access AI？
→ Anthropic RSP / OpenAI Preparedness Framework

---

## 💻 项目代码

📁 `topic3-safety/pluralistic_safety.py`

**实现**:
1. ✅ 偏好聚合（Plurality / Borda / Condorcet）
2. ✅ Condorcet 悖论
3. ✅ Pluralistic Alignment 模拟
4. ✅ Red Teaming（5 种攻击模板 + 检测）

---

## 📊 关键论文

### 🔴 P0
1. **Anthropic** "Responsible Scaling Policy" (RSP)
2. **OpenAI** "Preparedness Framework"
3. **Reich, Sahami, Goulden** *System Error* (教材)
4. Longpre 2024 *Data Authenticity Broken*
5. Sorensen *Pluralistic Alignment*

### 🟡 P1
6. Burns *Weak-to-Strong Generalization*
7. Irving *AI Safety via Debate*
8. NIST AI RMF
9. EU AI Act

---

## 📋 评估方式

- 周读 + 短测验
- 课堂参与
- **Final project**（empirical study / evaluation / audit / lit review / governance analysis）

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想做 Safety 研究** | CS120 → CS329X → CS329H |
| **想做 AI 政策** | CS120 → CS283 → 政府实习 |
| **想做 alignment** | CS120 → CS329H（数学）|
| **本科入门** | CS120（先修无要求）|

---

## 💡 课程意义

CS120 是 **Stanford 正式承认 AI Safety 是本科可学领域**的标志。其他学校（Berkeley / MIT / CMU）也在跟进。

---

**对应代码**: `topic3-safety/pluralistic_safety.py`
