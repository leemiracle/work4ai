# Oxford Prelims M1 — Linear Algebra I/II

> **学校**：Oxford | **学院**：Mathematical Institute | **学期**：Prelims (Year 1)
> **一手来源**：[maths.ox.ac.uk/system/files/attachments/Prelims%20Mathematics%20Synopses%202024-25.pdf](https://www.maths.ox.ac.uk/system/files/attachments/Prelims%20Mathematics%20Synopses%202024-25.pdf)

## 课程信息
- **学期**：Prelims Year 1
- **教材**：Cameron, *Linear Algebra*
- **特色**：本科线代英式入门

## 教学大纲
1. Vectors, matrices, linear systems
2. Vector spaces, subspaces
3. Linear maps, matrices
4. Determinants
5. Eigenvalues, eigenvectors
6. Diagonalization
7. Inner products

## 与 ML 的关联
- 标准线代基础

---

## 📍 在数学全景中的位置

Oxford Prelims M1 是 Year 1 入门线代——英式公理化风格，从向量空间而非矩阵计算起步，为整个 Oxford 数学学位奠基。

```
高中数学                     本课（Year 1 入门线代）                    Oxford 后续
───────                      ──────────────                            ───────────
A-Level Further Maths ──▶  Prelims M1 线代 (Cameron)  ──┬──▶  Part A A0 线代深化 (Year 2)
                                                          ├──▶  Part A A12 数值分析
                                                          └──▶  Part B/C: 随机矩阵/优化
```

- **前置**：A-Level 数学（会基本矩阵）。
- **本课特色**：**公理化 + 几何**——Oxford 从向量空间公理出发（不像美国先教矩阵运算），强调"结构先于计算"。教材 Cameron *Linear Algebra*。
- **后续**：Part A A0（对偶/Jordan/谱理论深化）；Part C C7.1 随机矩阵理论（LoRA/LLM 前沿的数学基础）。

> 一句话：**Prelims M1 是"英式严格线代"的起点——先建抽象骨架，再填计算血肉。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **线性方程组 $A\mathbf{x}=\mathbf{b}$ → 线性回归**
   - Prelims M1 的核心应用：超定系统无解 → 最小二乘。$A^TA\hat{\mathbf{x}}=A^T\mathbf{b}$。

2. **特征值/对角化 → PageRank / 马尔可夫**
   - 转移矩阵最大特征值 $=1$，稳态 = 对应特征向量。Oxford 特色是把这放在"线性映射"框架下。

3. **内积与正交 → Gram-Schmidt / QR**
   - 正交基的构造 → 数值稳定的最小二乘。

4. **行列式 → 体积/可逆性**
   - $|\det A|$ = 平行体体积。几何直觉先行。

5. **对角化 → 矩阵幂 $A^k$**
   - $A=Q\Lambda Q^{-1}$ ⟹ $A^k=Q\Lambda^kQ^{-1}$。→ 动力系统迭代分析。

---

## 🆕 2024-2026 最新研究（线代基础在 ML 的前沿）

1. **对角化 → LoRA 的低秩直觉（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）的低秩更新 $W_0+BA$，入门理解就来自 Prelims 学的"矩阵的秩与子空间"。

2. **正交基 → 正交初始化的稳定性（2024-2025）**
   - LLM 训练稳定性研究回归"正交权重"，其基础正是 Gram-Schmidt/正交矩阵。

3. **Oxford Part C 随机矩阵（C7.1）→ LLM 权重谱分析（2024-2026）**
   - Prelims M1 打的基础，最终通向用 Marchenko-Pastur 律分析 LLM 权重的奇异值分布。

📌 **下一步**：→ [Prelims M2 Analysis](../prelims_m2_analysis/)
