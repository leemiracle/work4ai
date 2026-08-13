# 01 - SVD：矩阵的"DNA"（配 T&B Ch 5）

> SVD（奇异值分解）是数值线代**最美也最有用**的工具——PCA、LoRA、推荐系统、压缩感知都建立在它之上。

---

## 一、直觉

### 1.1 几何视角

任何实矩阵 $A \in \mathbb{R}^{m \times n}$ 都可以分解为：

$$A = U \Sigma V^T$$

- $U$：$m \times m$ 正交矩阵（旋转）
- $\Sigma$：$m \times n$ 对角矩阵（伸缩，对角元素 $\sigma_i \geq 0$ 叫**奇异值**）
- $V$：$n \times n$ 正交矩阵（旋转）

→ 任何线性变换 = 旋转 + 伸缩 + 旋转。

### 1.2 反直觉：SVD 唯一排序

奇异值按递减排列 $\sigma_1 \geq \sigma_2 \geq \ldots \geq 0$。**最大的几个奇异值"携带大部分信息"**。

### 1.3 低秩近似（Eckart-Young 定理）

$A$ 的最佳 $k$ 秩近似（Frobenius 范数下）：$A_k = \sum_{i=1}^k \sigma_i u_i v_i^T$。

→ 截断 SVD 给你**最优低秩近似**。这是 PCA / 压缩 / LoRA 的数学基础。

---

## 二、数学层

### 2.1 存在性

每个矩阵都有 SVD（即使非方阵 / 奇异）。

### 2.2 与特征值的关系

- $A^T A$ 的特征值 = $\sigma_i^2$
- $A A^T$ 的特征值 = $\sigma_i^2$
- $\text{rank}(A)$ = 非零奇异值个数

### 2.3 Eckart-Young 定理 ⭐

$$\min_{\text{rank}(B) \leq k} \|A - B\|_F = \sqrt{\sigma_{k+1}^2 + \ldots}$$

→ $A_k$（截断 SVD）是 $A$ 的最佳 $k$ 秩近似。

### 2.4 数值秩

如果 $\sigma_{k+1}, \sigma_{k+2}, \ldots \approx 0$（小于 $\epsilon \sigma_1$），则 $A$ 的"数值秩" = $k$（即使理论秩更大）。

---

## 三、应用

| 应用 | 怎么用 SVD |
|------|----------|
| **PCA** | 数据矩阵的 SVD → 主成分 |
| **推荐系统** | 用户-物品矩阵的截断 SVD |
| **LoRA**（LLM 微调）| $W = U \Sigma V^T$，只学低秩更新 |
| **图像压缩** | 像素矩阵截断 SVD |
| **词嵌入** | 共现矩阵的 SVD（Levy-Goldberg 2014）|
| **去噪** | 小奇异值 = 噪声，丢弃 |

---

## 四、实验

跑 `python3 -u experiments/01_svd.py`：
- Hilbert 矩阵的 SVD + 条件数
- 图像压缩（截断 SVD）
- LoRA 思想演示

---

## 五、不足

- SVD 计算成本 $O(mn^2)$（大矩阵慢）
- 奇异值不"鲁棒"（小扰动可能改变数值秩）
- 截断 SVD 不一定保留"结构"（如稀疏性）

---

📌 **下一步**：跑实验。读 [`02-QR分解.md`](02-QR分解.md)（待写）。

## ✍️ 练习

1. 写出 SVD 的几何意义。
2. 证 Eckart-Young（提示：用 $\|A - B\|_F^2 = \sum \sigma_i^2(A-B)$）。
3. 🐍 在实验里用 SVD 压缩一张图，看 5/10/50 秩的差别。
4. 思考：为什么 LoRA 只学 $U, V$ 不学 $\Sigma$？
5. ⚡ Mathlib：找 `Matrix.SVD`（如已形式化）。
