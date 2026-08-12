# MIT 18.175 — Theory of Probability

> **学校**：MIT | **学期**：Spring（研究生+本科高年级）| **学分**：12 units
> **一手来源**：[catalog.mit.edu/subjects/18/#18.175](https://catalog.mit.edu/subjects/18/) + Prof. Dudley / Prof. Sheffield 历年讲义

## 课程信息
- **编号**：18.175（同号研究生/本科合上）
- **先修**：18.100 实分析（**必须**）
- **教材**：**Durrett, *Probability: Theory and Examples* (5th ed, Cambridge, 2019)** ★
- **备选教材**：Billingsley, *Probability and Measure*；Williams, *Probability with Martingales*；Varadhan, *Probability Theory*

## 教学大纲
1. **Probability spaces**（概率空间、σ-代数、Borel 集）
2. **Random variables & distributions**（随机变量、分布函数、密度）
3. **Expectation**（期望、积分、$L^p$ 空间）
4. **Conditional probability & expectation**（条件期望、martingales 引入）
5. **Modes of convergence**（a.s. / in probability / in $L^p$ / in distribution）
6. **Laws of Large Numbers**（弱大数 / 强大数）
7. **Central Limit Theorem**（特征函数、CLT、Berry-Esseen）
8. **Martingales**（停时、可选停时定理、收敛定理）
9. **Brownian motion**（Brown 运动入门，如时间允许）

## 与 ML 的关联（**ML 理论核心**）
- **集中不等式**（Hoeffding / Bernstein / McDiarmid）：泛化界
- **大数定律 + CLT**：SGD 收敛证明
- **Martingales**：强化学习的理论基础
- **学完本课后**：能读懂 Bartlett / Belkin / Mohri 等 ML 理论论文

## 参考资源
- **教材（开放获取）：Durrett 5th ed PDF**：[services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf](https://services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf)
- **视频**：[MIT 18.175 by Sheffield (2020)](https://www.youtube.com/playlist?list=PLUl4u3cNGP62UU6O3I_PjRV6UhMxFR7-A)（MIT 18.175 / Statistics 213 Harvard 部分视频）
- **替代教材**：Williams, *Probability with Martingales*（Cambridge, 1991）—— 更适合自学的英国版
- **习题集**：Durrett 教材附录习题

## 学习建议
- **节奏**：每周 5-7 小时，14-16 周完成
- **核心**：第 1-7 章（标准 ML 理论用的概率工具）
- **配合**：[Berkeley Stat 134](../../berkeley-math-courses/stat134_probability/)（先学应用版再上 18.175）
- **进阶**：[Berkeley Math 218 随机过程](../../berkeley-math-courses/math218_probability_graduate/)

📌 **下一步**：→ [18.085 计算科学与工程](../18_085_computational_science/) 或 [18.901 拓扑](../18_901_topology/)
