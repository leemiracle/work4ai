# UT Austin M 383C — Methods of Applied Mathematics

> **学校**：UT Austin | **学期**：Fall (研究生)
> **一手来源**：[web.ma.utexas.edu/users/koch/M383C](https://web.ma.utexas.edu/users/koch/M383C/) + [math.utexas.edu/information/graduate-students/preliminary-exams](https://math.utexas.edu/information/graduate-students/preliminary-exams)

## 课程信息
- **编号**：M 383C / CSEM 386C（互认）
- **教授**：Hans Koch（Fall 2022 版本，已一手核实）
- **先修**：M 365C + 本科线代
- **教材**：**Kreyszig, *Introductory Functional Analysis with Applications*** ★；配 Reed & Simon
- **特色**：**UT Austin Applied Math Prelim 第一学期**——**泛函分析 + 应用**

## 教学大纲（Koch Fall 2022 版本，一手核实）
1. **Preliminaries**（integration, function spaces, properties）
2. **Banach spaces** ★
   - Continuous linear functionals & transformations
   - **Hahn-Banach 定理**
   - Duality, weak convergence
   - **Baire 定理, Uniform Boundedness**
   - **Open Mapping, Closed Graph, Closed Range 定理**
   - Compactness
   - **Spectrum, Fredholm alternative**
3. **Hilbert spaces** ★
   - Orthogonality, bases, projections
   - Bessel & Parseval relations
   - **Riesz representation 定理**
   - **Spectral theory for compact, self-adjoint and normal operators** ★
   - **Sturm-Liouville theory**
4. **Distributions** ★
   - Seminorms and locally convex spaces
   - Test functions, distributions
   - Calculus with distributions
5. **Applications**

## 与 ML 的关联（**ML 高级理论**）
- **Banach 不动点定理** → 神经网络存在性
- **谱理论** → RKHS（kernel methods）
- **Sobolev 空间** → 神经网络的函数空间视角
- **Distributions** → 信号处理 / 卷积神经网络
- 学完后：能读 ML 理论的高级论文（Cucker & Smale, Bach 等）

## 参考资源
- Kreyszig, *Introductory Functional Analysis with Applications* (Wiley, 1978)
- Reed & Simon, *Methods of Modern Mathematical Physics* Vol 1
- **Koch 讲义**：[web.ma.utexas.edu/users/koch/M383C](https://web.ma.utexas.edu/users/koch/M383C/)（UT Austin 公开）
- Lax, *Functional Analysis* (Wiley)
- MIT 对照：[MIT 18.102](../../mit-math-courses/)

## 学习建议
- **节奏**：每周 6-8 小时，14 周
- **先修**：M 365C（Rudin）必须扎实

📌 **下一步**：→ [M 383E Numerical Linear Algebra](../m383e_numerical_linear_algebra/) 或 [M 385C Theory of Probability](../m385c_theory_of_probability/)

---

## 📍 在数学全景中的位置

- **前置**：[M 365C 实分析](../m365c_real_analysis/) + ODE + 线性代数
- **本课**：应用数学工具箱 → 量纲分析 + 渐近方法 + 变分法 + 积分变换（研究生核心）
- **交叉**：[Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/) + [Berkeley 185 复分析](../../berkeley-math-courses/math185_complex_analysis/)

## 🔬 理论联系实际
1. **变分法 → VAE/ELBO**：$\mathcal{L}_{\text{ELBO}}$ 是泛函，VAE 用变分法优化
2. **渐近分析 → Neural Scaling Laws**：大参数/大数据的极限标度行为
3. **量纲分析 → Scaling Laws**：Kaplan et al. [2001.08361](https://arxiv.org/abs/2001.08361) ✅
4. **稳定性分析 → GAN 训练**：纳什均衡的分岔理论分析

## 🆕 2024-2026 最新研究
| 子主题 | 进展 | 参考 |
|---|---|---|
| Scaling Laws | Chinchilla 最优计算分配 | [Hoffmann et al. 2022, 2203.15556](https://arxiv.org/abs/2203.15556) ✅ |
| 变分推断 | 用变分法做贝叶斯深度学习 | ⚠️ 2024 |
| 渐近展开 | 大模型训练 dynamics 的渐近分析 | ⚠️ 研究 |
