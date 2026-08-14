# 讲透数值线代 · 浮点数下的线性代数（基于 Trefethen & Bau）

> 用「直觉 → 数学 → Python 实验 → 应用」的方式，把 Trefethen & Bau《Numerical Linear Algebra》（300 页薄书，全球标准）讲透。
>
> 这本书是**数值分析的圣经**——薄、精、清晰。掌握它 = 理解为什么 `np.linalg.solve` 有时数值爆炸。

---

## 〇、为什么数值线代

### 0.1 浮点数 ≠ 实数

理论上 $A x = b$ 总有解（如果 $A$ 可逆）。但浮点数下：
- 矩阵 $A$ "病态"时，解的数值误差**巨大**
- 条件数 $\kappa(A) = \sigma_{\max}/\sigma_{\min}$ 衡量病态
- 当 $\kappa(A) \approx 10^{16}$（浮点精度极限），数值解完全无意义

### 0.2 你的应用

- **PyTorch**：`torch.linalg.solve` / `matmul` 的数值稳定性
- **ML**：Hessian 病态 → 优化困难
- **物理仿真**：大矩阵求逆的稳定性
- **GPU**：BLAS / LAPACK 底层都是数值线代

---

## 一、章节（基于 Trefethen & Bau）

| # | 文件 | 主题 | T&B 章 | 状态 |
|---|------|------|--------|------|
| 00 | [`00-数值线代是什么.md`](00-数值线代是什么.md) | 浮点误差 + 条件数 | Ch I | ✅ |
| 01 | [`01-SVD.md`](01-SVD.md) | 奇异值分解 + 应用 | Ch 5 | ✅ |
| 02 | `02-QR分解.md` | Gram-Schmidt + Householder | Ch 7-8 | 📝 |
| 03 | `03-条件数与稳定性.md` | backward stability | Ch 12-15 | 📝 |
| 04 | `04-特征值算法.md` | QR algorithm | Ch 25-30 | 📝 |
| 05 | `05-迭代法.md` | Krylov 子空间 / GMRES / CG | Ch 32-38 | 📝 |
| 06 | `06-ML应用.md` | PCA / 低秩近似 / LoRA | 应用 | 📝 |

---

## 二、前置

- 线性代数（见 [`../讲透实分析/`](../讲透实分析/) 之外，需 Axler LADR）
- Python + NumPy
- 基本浮点数知识

---

## 三、与 work4ai 联动

- [`../讲透优化理论/`](../讲透优化理论/) — 凸优化的数值实现
- [`../讲透NLP/05-词嵌入.md`](../讲透NLP/05-词嵌入-word2vec与GloVe.md) — SVD 在词嵌入
- [`../top-math-courses/TEXTBOOK_LIBRARY.md`](../top-math-courses/TEXTBOOK_LIBRARY.md) §七

---

📌 **下一步**：读 [`00-数值线代是什么.md`](00-数值线代是什么.md)。
