# ETH 401-3904 — Convex Optimization

> **学校**：ETH Zurich | **学院**：D-MATH
> **一手来源**：[vvz.ethz.ch](https://www.vvz.ethz.ch)

## 课程信息
- **编号**：401-3904-00L
- **教材**：**Boyd & Vandenberghe, *Convex Optimization*** ★；或 Bubeck 现代版
- **特色**：与 Stanford CME 364A 同类的 ETH 版

## 教学大纲
1. Convex sets & functions
2. Convex optimization problems
3. Duality（Lagrange 对偶）
4. KKT 条件 ★
5. Algorithms: gradient descent, Newton, interior point
6. Approximation & fitting
7. Statistical estimation
8. Applications: signal processing, ML, finance

## 与 ML 的关联（**ML 工程师必修**）
- 与 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 同类
- 学完后：能推导所有 ML 训练算法

## 参考资源
- Boyd & Vandenberghe, *Convex Optimization* (免费 PDF)
- Bubeck, *Convex Optimization: Algorithms and Complexity* (Foundations & Trends, 2015)
- 视频：Boyd Stanford 课程

📌 **下一步**：→ 进入 [UT Austin](../../ut-austin-math-courses/)

---

## 📍 在数学全景中的位置

- **前置**：线代 + 多变量微积分
- **本课**：凸优化（与 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 同类，ETH 版更侧重 Bubeck 复杂度理论）
- **后续**：[ETH 401-3901 组合优化](../e401_3901_linear_combinatorial_optimization/)（整数规划凸松弛）

---

## 🔬 理论联系实际

1. **Nesterov 加速 → PyTorch `SGD(nesterov=True)`**：$O(1/k^2)$ vs GD 的 $O(1/k)$
2. **Bubeck 下界**：GD 在凸问题上已是最优一阶方法（不加速）
3. **强凸场景**：Nesterov 给 $\sqrt{\kappa}$ 加速 → 百倍提速
4. **RLHF/DPO 凸化**：见 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)
5. **Adam/AMSGrad 收敛性**：Reddi 2018 修复 Adam 不收敛问题

---

## 🆕 2024-2026 最新研究

- **Schedule-Free Optimization**（Defazio 2024）：无需 lr schedule 的加速
- **分布式凸优化下界**：通信 vs 计算权衡
- **差分隐私凸优化**：隐私约束下的复杂度下界
