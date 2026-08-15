# CS329H: Machine Learning from Human Preferences

> Stanford University, Autumn 2025
> Instructors: **Sanmi Koyejo** (公平性 ML) + **Andreas Haupt** (机制设计 + ML)
> TA: Sang Truong
> Time: Mon/Wed 3:00-4:20 PM, Thornton 102
> Prerequisites: CS221 / CS229 / CS230 / CS224N + 概率 + 线性代数
> Difficulty: ⭐⭐⭐⭐⭐ (研究生研讨课)

---

## 📚 课程独特定位

**CS329H 不是普通 RLHF 课**。讲师组合（Koyejo 公平性 + Haupt 机制设计）揭示其独特视角：

> **把"人类偏好"当计量经济学问题严格建模**，而不是当作工程 trick。

这是其他 RLHF 课没有的——CS329H 把 Arrow 不可能性定理、Social Choice Theory、Mechanism Design 都纳入 RLHF 的理论框架。

---

## 🎯 学习目标

1. **掌握** Choice Theory（RUM / Bradley-Terry / Rasch / Luce）
2. **理解** 偏好聚合的数学困难（Arrow 定理 / Condorcet 悖论）
3. **实现** Preference learning 算法（MLE / Bayesian inference）
4. **分析** RLHF 在 LLM 训练中的角色
5. **批判** 单一 reward model 假设（pluralistic alignment）
6. **认识** 隐私 + inversion problem

---

## 📅 完整模块（17 讲）

### Week 1: Foundations
- **L1 (Sep 22)** — Intro to Preference Modeling
- **L2 (Sep 24)** — Background I: Choice Theory
  - **IIA** (Independence of Irrelevant Alternatives)
  - **RUM** (Random Utility Model)
  - **Bradley-Terry** model
  - **Luce** choice axiom

### Week 2: Learning from Preferences
- **L3 (Sep 29)** — Background II: Implementing Choice Models
  - `torch-choice` 库（讲师组开发）
- **L4 (Oct 1)** — Learning I: Structure of Utilities
  - **Rasch** model (IRT)
  - **Thurstone** model
  - Bradley-Terry 详解

### Week 3: MLE / Bayesian
- **L5 (Oct 6)** — Learning II: Full-information MLE, Bayesian inference
  - Online vs offline learning
- **L6 (Oct 8)** — Learning III: Parametric Families

### Week 4: Elicitation
- **L7 (Oct 13)** — Elicitation I: Measurement Objective
  - Rasch vs Bradley-Terry 对比
  - Bayes vs Frequentist
- **L8 (Oct 15)** — Elicitation II: Sequential Optimal Design

### Week 5: Decision (Dueling Bandits → RLHF)
- **L9 (Oct 20)** — Elicitation III
- **L10 (Oct 22)** — Decision I: Stateless Dueling
  - Parametric vs nonparametric
- **L11 (Oct 27)** — **Decision II: Stateful Dueling, RLHF, LMarena** ⭐
  - 真正的 RLHF 训练流程
  - LMSYS Chatbot Arena 数据分析

### Week 6: Asymptotic Theory + Guest
- **L12 (Oct 29)** — Decision III: Asymptotic Optimality
- **L13 (Nov 3)** — **Guest: Dylan Hadfield-Menell** ⭐
  - Cooperative Inverse RL (CIRL)
  - Alignment = Shared reward function 的不确定性建模

### Week 7: Aggregation + Pluralism
- **L14 (Nov 5)** — Aggregation I: Paradox of Liberalism (Sen)
  - Non-nosy preferences
  - Personalization
  - Recommendation systems
- **L15 (Nov 10)** — Aggregation II: Nosy Preferences
  - Median voters
  - Community Notes (Twitter/X)
  - Borda count
- **L16 (Nov 12)** — Aggregation III: Statistical Perspective
- **L17 (Nov 17)** — **Guest: Craig Boutilier** ⭐ (Google DeepMind 首席经济学家)
  - Recommendation / 公平分配 / 机制设计 → ML 桥接

### Week 8: Privacy
- **L18 (Nov 19)** — **Privacy and the Inversion Problem** ⭐
  - 从偏好反推用户身份
  - Differential Privacy

---

## 🧮 核心数学框架

### 1. Random Utility Model (RUM)
$$U_{ij} = V_{ij} + \epsilon_{ij}, \quad \epsilon \sim \text{Gumbel}(0, 1)$$

选择概率：
$$P(i \text{ chosen from } S) = \frac{e^{V_i}}{\sum_{j \in S} e^{V_j}}$$

### 2. Bradley-Terry Pairwise
$$P(i \text{ beats } j) = \frac{\pi_i}{\pi_i + \pi_j} = \sigma(v_i - v_j)$$

其中 $\pi_i = e^{v_i}$ 是 item $i$ 的"强度"。

**MLE 训练**:
$$\mathcal{L} = -\sum_{(w,l) \in \mathcal{D}} \log \sigma(v_w - v_l)$$

梯度：
$$\frac{\partial \mathcal{L}}{\partial v_w} = -(1 - \sigma(v_w - v_l))$$

### 3. Rasch Model (IRT)
$$P(\text{correct}_{u,i}) = \sigma(\theta_u - \beta_i)$$
- $\theta_u$: 用户 u 的能力
- $\beta_i$: 题 i 的难度

### 4. Luce Choice Axiom (IIA)
$$P(i | S) = \frac{u_i}{\sum_{j \in S} u_j}$$

**IIA 的反直觉**: 加新选项不改变其他相对概率。但人类经常违反 IIA (Debreu 1960)。

### 5. Plackett-Luce 排名
$$P(\text{ranking } i_1 > i_2 > \dots > i_n) = \prod_{k=1}^{n} \frac{u_{i_k}}{\sum_{j \geq k} u_{i_j}}$$

### 6. Arrow 不可能性定理
当 ≥3 个候选人时，**没有任何聚合机制能同时满足**：
- Pareto efficiency（一致同意）
- IIA
- Dictatorship-free

这意味着：**任何 RLHF 都要做价值权衡**。

---

## 📋 作业结构

- **3 次小测验**（数学基础 + 理论）
- **3 次编程作业**（可重复提交）:
  - Coding 1: `torch-choice` 偏好建模
  - Coding 2: Reward modeling
  - Coding 3: Assistance games / CIRL
- **Final project**（pre-analysis plan W7 due）

### 考勤严格
- 3 次无故缺席: -0.5 grade
- 5 次: -1.0 grade
- 10 次: 直接挂科

---

## 💻 项目代码（本仓库）

📁 `topic1-choice/choice_theory.py`

**实现内容**：
1. ✅ Random Utility Model + Gumbel noise 采样
2. ✅ Bradley-Terry + MLE 梯度下降训练
3. ✅ Rasch Model (IRT) 训练
4. ✅ Luce Choice 概率
5. ✅ Plackett-Luce 排名采样
6. ✅ 1000 次蒙特卡洛验证理论概率

### 运行 Demo
```bash
cd topic1-choice
python3 choice_theory.py
```

**输出示例**:
```
📋 1. Random Utility Model
   理论 P(A|A,B,C) = 0.629
   经验频率 (1000 次): {'A': 657, 'B': 213, 'C': 130}

📋 2. Bradley-Terry 模型训练
   训练数据: 500 偏好对
   学到的 v: {'A': 0.81, 'B': -0.21, 'C': -0.60}
   真实 v: {'A': 2.0, 'B': 1.0, 'C': 0.5}
```

---

## 🔬 关键嘉宾

### 1. **Dylan Hadfield-Menell** (MIT,兼职 Stanford)
- **Cooperative Inverse RL** (CIRL) 开山人
- 核心思想：**对齐 = 共享奖励函数的不确定性建模**
- 推荐论文：*Cooperative IRL* NeurIPS 2016

### 2. **Craig Boutilier** (Google DeepMind)
- DeepMind 首席经济学家
- 推荐 / 公平分配 / 机制设计 → ML 桥接
- 推荐论文：*Multiple-Objective Mechanism Design* 

---

## 📊 关键论文清单

### 🔴 必读（P0）
1. **Ouyang et al. 2022** "Training language models to follow instructions" (InstructGPT)
2. **Rafailov et al. 2023** "Direct Preference Optimization" (DPO) NeurIPS
3. **Bai et al. 2022** "Constitutional AI" (RLAIF)
4. **Sorensen et al. 2024** "Position: Roadmap to Pluralistic Alignment" ICML

### 🟡 推荐（P1）
5. Bradley & Terry 1952 "Rank Analysis of Incomplete Block Designs"
6. Luce 1959 "Individual Choice Behavior"
7. Rasch 1960 "Probabilistic Models for Some Intelligence and Attainment Tests"
8. Arrow 1951 "Social Choice and Individual Values"

### 🟢 选读（P2）
9. Sen 1970 "The Impossibility of a Paretian Liberal"
10. Plackett 1975 "The Analysis of Permutations"
11. Soufiani et al. 2014 "Computing Bayes-Nash Equilibrium in Generalized Second-Price Auction"

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **想搞 RLHF 研究** | CS329H 必修 + CS312 (训练工程) |
| **想理解对齐** | CS329H + CS329X (人本) + CS120 (Safety) |
| **想做推荐系统** | CS329H (Choice theory) + CS224W (Graph) |
| **想做经济学 + AI** | CS329H 完美匹配（罕见 niche）|

---

## 💡 反思

### 课程优势
1. **数学严谨**——不是调库，而是从公理推
2. **跨学科视角**——经济学 + ML + 心理学
3. **批判性**——不假设单一 reward 是对的

### 潜在局限
1. **工程深度不足**——不会真训 DPO，只讨论数学
2. **Koyejo + Haupt 的研究偏好主导**——多元化可能不够
3. **没有 hands-on RLHF training**——需要自学 DeepSpeed / TRL

---

## 🚀 扩展阅读

完成 CS329H 后推荐：
1. **CS329X** Human-Centered NLP — 应用层
2. **CS329A** Self-Improving Agents — STaR / RL self-improvement
3. **CS312** Deep Learning Alchemy — 训练工程
4. Anthropic / OpenAI 的 RLHF 实践博客
5. DeepMind 的 Gemini RLHF 报告

---

**最后更新**: 2026-08-11
**对应代码**: `topic1-choice/choice_theory.py`
