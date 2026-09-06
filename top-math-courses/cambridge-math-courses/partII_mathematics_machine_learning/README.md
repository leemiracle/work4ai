# Cambridge Part II — Mathematics of Machine Learning

> **学校**：Cambridge | **学院**：Statistical Laboratory
> **一手来源**：[dpmms.cam.ac.uk/study/II/MathematicsofMachineLearning](https://www.dpmms.cam.ac.uk/study/II/MathematicsofMachineLearning/) + [statslab.cam.ac.uk/~rds37/machine_learning.html](https://www.statslab.cam.ac.uk/~rds37/machine_learning.html)（**一手核实**）

## 课程信息
- **学期**：Lent (16 lectures, D-course)
- **教授**：Richard Samworth (RDS)
- **教材**：
  - **Shalev-Shwartz & Ben-David, *Understanding Machine Learning*** ★
  - Wainwright, *High-Dimensional Statistics*
  - Bach, *Learning Theory from First Principles*
  - Hastie, Tibshirani, Friedman, *ESL*
- **先修**：Part IB Statistics + Part II Probability and Measure（推荐）
- **特色**：**Cambridge 数学专业 ML 课的金标准**

## 教学大纲（一手核实自 RDS 2026 版）
1. **Bayes risk**
2. **Empirical Risk Minimization (ERM)** ★
3. **Concentration inequalities** (Hoeffding, sub-Gaussian)
4. **Finite hypothesis class** bounds
5. **VC dimension** ★
6. **Rademacher complexity** ★
7. **Convex analysis for ERM**
8. **Stochastic gradient descent** ★
9. **Random forests**
10. **Boosting (AdaBoost)**
11. **Neural networks**（单隐层 universal approximation + 收敛）

## 与 ML 的关联（**直接关联**）
- **学完后**：能读懂所有 ML 理论论文
- 涵盖 **统计学习理论** 的标准工具集

## 参考资源
- **课程笔记（免费 PDF）**：[statslab.cam.ac.uk/~rds37/teaching/machine_learning/notes_cur.pdf](https://www.statslab.cam.ac.uk/~rds37/teaching/machine_learning/notes_cur.pdf) ★
- **Shalev-Shwartz & Ben-David**（免费 PDF）
- **Wainwright, *High-Dimensional Statistics***（Ch 2, 4）
- **Past Tripos papers**: [maths.cam.ac.uk/undergrad/pastpapers](https://www.maths.cam.ac.uk/undergrad/pastpapers) (Paper 1/2/3/4 Section II "31J")

## 学习建议
- **节奏**：每周 6-8 小时，10-12 周
- **必备先修**：[Part II Probability and Measure](../partII_probability_measure/)
- **MIT 对照**：MIT 18.175 + 9.520（统计学习理论课）

📌 **下一步**：→ [Part II Numerical Analysis](../partII_numerical_analysis/) 或 Stanford CME 364A（待写/未落盘）

---

## 📍 在数学全景中的位置

```
概率论 (浓度不等式)        凸分析 (优化理论)
        │                        │
        └────────┬───────────────┘
                 ▼
          本课: ML 的数学理论
     ┌───────────┼───────────────┐
     ▼           ▼               ▼
  PAC 学习    VC 维/Rademacher   凸 ERM
  (可学习性)  (容量控制)         (优化保证)
     │           │               │
     ▼           ▼               ▼
  泛化界 ★    偏差-方差         SGD 收敛
  (为什么 ML 有效)               (训练理论)
     │
     ▼
  深度学习泛化谜题 (双下降, NTK, PAC-Bayes)
```

- **前置**：[Part II Probability and Measure](../partII_probability_measure/) + [Stanford CME 364A 凸优化](../../stanford-math-courses/cme364A_convex_optimization/)
- **本课**：ERM → 浓度不等式 → VC 维 → Rademacher → 凸学习 → SGD → 神经网络
- **后续/交叉**：[Oxford C7.1 随机矩阵](../../oxford-math-courses/partC_c7_1_random_matrix_theory/)（高维统计 → 泛化）

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. VC 维 → 模型选择
$$L_{\text{true}} \leq L_{\text{train}} + O\!\left(\sqrt{\frac{\mathrm{VC}\log(n/\mathrm{VC})}{n}}\right)$$
复杂度（VC 维）越高 → 需要更多样本。指导正则化系数和模型容量选择。

### 2. Rademacher 复杂度 → 域适应
$$\hat{\mathfrak{R}}_S(\mathcal{H}) = \mathbb{E}_\sigma\left[\sup_h \frac{1}{n}\sum \sigma_i h(x_i)\right]$$
度量假设类"拟合随机噪声"的能力 → 非分布泛化的核心工具。

### 3. 偏差-方差 → 双下降 ★
经典理论：参数↑→方差↑→过拟合。但深度学习在 $p \gg n$ 时测试误差**反而下降**（Belkin 2019 [1812.11118](https://arxiv.org/abs/1812.11118) ✅）。这是当前 ML 理论最热门的未解之谜。

### 4. NTK → 无限宽网络的精确泛化界
$$f_t(x) \approx f_0(x) + K_{\text{NTK}}(x, X)(K_{\text{NTK}}(X,X) + \lambda I)^{-1}(Y - f_0(X))$$
无限宽网络 ≈ 核岭回归 → 可精确分析泛化。

### 5. PAC-Bayes → 最紧的神经网络泛化界
$$L \leq \hat{L} + \sqrt{\frac{\mathrm{KL}(Q\|P) + \log(2\sqrt{n}/\delta)}{2n}}$$

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **双下降理论** | 过参数化区间的精确泛化曲线分析 | Belkin et al. [1812.11118](https://arxiv.org/abs/1812.11118) ✅ |
| **NTK 泛化** | 无限宽极限的核岭回归等价 → 精确界 | Jacot et al. NeurIPS 2018 ✅ |
| **PAC-Bayes 紧界** | 用于 LLM 和 Transformer 的 PAC-Bayes 泛化分析 | ⚠️ 2024 进展 |
| **隐式偏差 SGD** | SGD 收敛到低范数/平坦解的理论证明 | ⚠️ |
| **大模型缩放律** | Neural Scaling Laws 的理论解释 | ⚠️ 2024-2025 |

> ⚠️ 深度学习泛化理论发展极快，标记项建议核实。

---

📌 **下一步**：→ [Part II Numerical Analysis](../partII_numerical_analysis/) 或 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)
