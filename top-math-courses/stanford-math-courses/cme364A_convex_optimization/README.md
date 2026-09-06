# Stanford CME 364A — Convex Optimization I

> **学校**：Stanford | **学院**：ICME (Institute for Computational and Mathematical Engineering)
> **一手来源**：[web.stanford.edu/class/cme364a](https://web.stanford.edu/class/cme364a/) + [ Boyd CVX Book](https://web.stanford.edu/~boyd/cvxbook)

## 课程信息
- **编号**：CME 364A / MS&E 311
- **先修**：MATH 51（线代 + 多变量）+ 概率/统计基础
- **教材**：**Boyd & Vandenberghe, *Convex Optimization*** (Cambridge, 2004) — **免费 PDF** ★
- **视频**：[Boyd 2014 完整课](https://www.youtube.com/playlist?list=PL3940CE95F3B87249)（**全球最知名优化课**）
- **特色**：**ML 工程师的优化圣经课**

## 教学大纲
1. **Convex sets**
2. **Convex functions**
3. **Convex optimization problems**
4. **Duality**（Lagrange 对偶、KKT 条件）★
5. **Approximation & fitting**
6. **Statistical estimation**
7. **Geometric problems**
8. **Numerical methods**（gradient descent, Newton, interior point）★

## 与 ML 的关联（**所有 ML 都用**）
- **SGD / Momentum / Adam 推导**
- **KKT**：SVM 推导
- **凸松弛**：组合优化
- **学完本课后**：能从优化理论推导所有 ML 训练算法

## 参考资源
- **教材（免费 PDF）**：[web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)
- **视频（Boyd 全套）**：[Stanford ENGR108 YouTube](https://www.youtube.com/playlist?list=PL3940CE95F3B87249)
- **课程主页**：[web.stanford.edu/class/cme364a](https://web.stanford.edu/class/cme364a/)
- **配套**：CVXPY 库 [cvxpy.org](https://cvxpy.org)

## 学习建议
- **节奏**：每周 5-7 小时，10-12 周
- **重点**：第 1-5 章 + 第 9 章（数值方法）
- **配合**：[Boyd 的额外视频](https://www.youtube.com/@StephenLBoyd)

---

## 📍 在数学全景中的位置

```
微积分 / 多变量分析 (梯度, Hessian)
        │
        ▼
线性代数 (正定矩阵, 特征值) ──► 本课: 凸优化
        │                          │
        │                          ├──► 对偶理论 / KKT (SVM, 正则化)
        │                          ├──► 数值优化 (GD, Newton, IPM)
        │                          │
        │           ┌──────────────┴──────────────┐
        │           ▼                             ▼
        │    非凸优化 (深度学习)           凸统计推断 (MML)
        │    SGD / Adam / Lion          经验风险最小化
        │    ↗ 卡局部最小                 Rademacher 复杂度
        │
        └──► 数值线代 (Trefethen & Bau): Hessian 求逆, 条件数
```

- **前置**：[MIT 18.06 线代](../../mit-math-courses/18_06_linear_algebra/)（正定矩阵）+ 多变量微积分（梯度/Hessian）
- **本课**：凸集 → 凸函数 → 凸问题 → 对偶/KKT → 算法（GD/Newton/IPM）
- **后续**：
  - 非凸优化（深度学习）：Adam/Lion，损失非凸
  - [Cambridge Part II ML](../../cambridge-math-courses/partII_mathematics_machine_learning/)：凸优化的统计学习理论视角
  - [ETH 401-3901 组合优化](../../eth-math-courses/e401_3901_linear_combinatorial_optimization/)：整数规划的凸松弛

---

## 🔬 理论联系实际（ML/工程应用，公式级）

### 1. SVM = 凸二次规划 + KKT ★
$$\min_{w,b} \tfrac12\|w\|^2 + C\sum\xi_i \quad \Rightarrow \quad w^\star = \sum_{i:\alpha_i>0}\alpha_i y_i x_i$$
对偶问题 + 互补松弛 → **支持向量**只在间隔边界。详见 [notes.md](notes.md) 第 6 节、[experiments/svm_kkt_derivation.py](experiments/svm_kkt_derivation.py)。

### 2. Adam = 对角预条件的拟牛顿法（[1412.6980](https://arxiv.org/abs/1412.6980) ✅）
$$\theta_{t+1} = \theta_t - \eta\frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}$$
$v_t$ 估计对角 Hessian → 降低有效条件数 $\kappa$。见 [experiments/gradient_descent_convex.py](experiments/gradient_descent_convex.py) 实验 5。

### 3. Lasso = $\ell_1$ 正则的凸优化 → 稀疏解
$$\min_w \tfrac{1}{2n}\|Xw-y\|^2 + \lambda\|w\|_1$$
$\ell_1$ 范数在原点有"尖角"，KKT 软阈值使很多 $w_i=0$。

### 4. 内点法 → SDP 用于聚类/社区检测
$$\max\,\text{Tr}(CX) \quad \text{s.t.}\ X\succeq0,\ X_{ii}=1$$
凸松弛后用障碍法多项式时间求解。

### 5. DPO 把 RLHF 凸化（2024-2026 热点，[2305.18290](https://arxiv.org/abs/2305.18290) ✅）
$$\mathcal{L}_{\text{DPO}} = -\log\sigma\!\left(\beta\log\tfrac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\tfrac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$
logistic loss 凸，消除了 RLHF 的 reward model + PPO 两阶段非凸性。

---

## 🆕 2024-2026 最新研究

| 子主题 | 最新进展 | 参考 |
|---|---|---|
| **大模型优化器** | **Lion**（符号驱动，[2302.00642](https://arxiv.org/abs/2302.00642) ✅）用 sign(m) 替代 m，省显存；**Sophia**（对角 Hessian）、**Schedule-Free Adam**（无需调 lr） | Meta 2024 |
| **凸优化的 RLHF** | DPO 及其变体（IPO, KTO, SimPO）把对齐问题凸化，2024-2025 成主流 | ⚠️ 具体变体需跟踪 |
| **方差缩减** | **Spider**、**SARAH**、**PAGE**：SGD 的 $O(1/\sqrt{k})$ 改进到 $O(1/k)$（凸）或 $O(1/k^{2/3})$（非凸） | 2018-2024 |
| **分布式凸优化** | **FedAvg 收敛分析**：凸损失下 $O(1/\sqrt{T})$，数据异质性（Non-IID）下的 lower bound | 2024 进展 |
| **加速方法** | **Nesterov 加速**（$O(1/k^2)$）的连续极限 = ODE，与扩散模型反向 SDE 有深刻联系 | Su-Boyd-Candes 2014, 后续 2024 |
| **LP/SOCP for ML** | 大规模 SOCP 求解器（SCS, COSMO.jl）用于稳健 PCA、协方差估计 | 2024 |

> ⚠️ 标记项的具体 arXiv 编号建议核实最新版本。

---

📌 **下一步**：→ [CME 108 Scientific Computing](../cme108_scientific_computing/) 或 [ETH 401-3904 Convex Optimization](../../eth-math-courses/e401_3904_convex_optimization/)
