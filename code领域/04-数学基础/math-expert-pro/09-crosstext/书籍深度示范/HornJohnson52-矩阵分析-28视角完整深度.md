# 28 视角完整深度示范：Horn-Johnson《矩阵分析》第 2 版

> 路径：`../math/华章数学丛书/52-矩阵分析原书第二版.pdf`
> 阶段：**1 末-2 初** ｜ 主题：代数·线性｜ V14 ML 锚点 + V7 代几对偶 最强

---

## 📊 元数据 + 章节

- **作者**：Roger A. Horn, Charles R. Johnson
- **版次**：2e / Cambridge 2013（中译：华章 52）
- **页数**：~662
- **章节**：0 复习 / 1 特征值相似 / 2 Schur 三角化 / 3 Cayley-Hamilton / 4 Hermite 正定 / 5 SVD / 6 范数数值范围 / 附录

---

# 🎯 28 视角应用

## V01 反例 · 非正规 / 不可对角化
- 不可对角化：Jordan 块 $J_2(0) = \begin{pmatrix}0&1\\0&0\end{pmatrix}$
- 非正规：$A = \begin{pmatrix}1&1\\0&1\end{pmatrix}$，$AA^* \neq A^*A$

## V02 公理 · 矩阵公理（vs 范畴）
- 矩阵 = ${M}_{n}(\mathbb{C})$ 是 *-代数
- 范畴视角（V8）：Mat 是 ${}^*$-保持幺半范畴

## V03 历史 · Cayley-Hamilton 1858 → 现代
- Cayley 1858 提，Frobenius 1878 证一般情形

## V04 最小例 · 2×2 一切
- 特征值：$A = \begin{pmatrix}0&1\\1&0\end{pmatrix}$，特征值 ±1
- SVD：$A = UI V^*$ 三步分解
- 正定：$A = \begin{pmatrix}2&0\\0&3\end{pmatrix}$ → 椭圆

## V05 严格度 · 本书的"黄金工具书"性质
- rigorous 阶段黄金标本（每定理完整证明）
- 不强求 post-rigorous（不像 Arnold）

## V06 计算 · numpy.linalg 全验证
```python
import numpy as np
A = np.array([[2,1],[1,3]])
print(np.linalg.eigvals(A))  # 特征值
print(np.linalg.svd(A))      # SVD
print(np.linalg.norm(A))     # 范数
```

## V07 代几对偶 · ⭐⭐⭐
| 代数 | 几何 |
|------|------|
| $\det A$ | 平行六面体体积 |
| SVD | 旋转-缩放-旋转 |
| 正定 | 椭球 |
| 谱分解 | 主轴 |

## V08 范畴 · Ban 空间范畴 + 算子
- 对象：Banach 空间
- 态射：有界线性算子 $B(X,Y)$
- 函子：对偶 $X \to X^*$

## V09 物理 · ⭐⭐⭐
| 数学 | 物理 |
|------|-----|
| 自伴矩阵 | 量子可观测量 |
| 谱分解 | 量子测量 |
| 正定 | 密度矩阵 |
| 酉矩阵 | 量子门 |
| 张量积 | 复合系统 |

## V10 复杂度 · 矩阵运算的复杂度
- 特征值：$O(n^3)$ QR
- SVD：$O(n^3)$
- 行列式：$O(n^3)$
- 矩阵乘：Strassen $O(n^{2.81})$

## V11 信息论 · 矩阵的"信息含量"
- 谱熵 = $-\sum \sigma_i^2/\|\sigma\|^2 \log(\cdot)$
- 低秩近似 = 信息压缩（PCA）

## V12 Curry-Howard · 矩阵计算的程序
- `numpy.linalg` = 矩阵代数的"证明提取"

## V13 Lean · Mathlib.LinearAlgebra
- `Mathlib.LinearAlgebra.Matrix.Adjugate`
- `Mathlib.LinearAlgebra.Eigenspace`
- `Mathlib.LinearAlgebra.Symmetric`

## V14 ML 锚点 · ⭐⭐⭐⭐⭐
| 数学 | ML |
|------|----|
| 特征值 | PCA / 谱聚类 |
| SVD | 推荐 / LSI / 图像压缩 |
| 正定 | 高斯过程 / 核方法 |
| 范数 | L1/L2 正则化 |
| 数值范围 | RNN 稳定性 |

## V15 工程出口 · ⭐⭐⭐
- PageRank / Netflix / 量化 / 信号处理

## V16 艺术 · 对称美学
- 伊斯兰几何 = 17 种 wallpaper 群
- 晶体 230 种空间群

## V17 反例配对 · 病态矩阵
- Hilbert 矩阵（条件数极大）
- 非正规矩阵（特征值不稳定性）

## V18 不可能性 · 矩阵的 Gödel
- 任意矩阵不可对角化（Jordan 形）
- 5 次以上特征多项式无根式解

## V19 替代 · 范畴论 vs 矩阵 vs 算子
- Axler 反对矩阵 → 用算子
- Bourbaki 用范畴论

## V20 比较 · Axler vs Horn vs Artin
- Axler：抽象算子，无行列式
- Horn：矩阵百科（本书）
- Artin：代数化

## V21 审美 · 矩阵之美
- Cayley-Hamilton：$p_A(A) = 0$
- SVD 的几何对称

## V22 费曼 · 用椭圆讲 SVD
"用 $\begin{pmatrix}2&0\\0&1\end{pmatrix}$ 作用在单位圆上，得到半轴 2 和 1 的椭圆——SVD 就是这种'找半轴'的普适化。"

## V23 问题 · 开问题
- 矩阵乘法下界 $O(n^2)$？
- 条件数 vs 复杂度？

## V24 跨书 · Axler / Horn / Strang
- 三书对照"特征值"讲法

## V25 真实数据 · 用矩阵分析真实数据
```python
# Netflix 推荐大赛数据
import numpy as np
# 用户-电影评分矩阵 R，做 SVD 降维
U, S, Vt = np.linalg.svd(R, full_matrix=False)
R_approx = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

## V26 失败 · 矩阵误用
- 长期资本管理（LTCM）：矩阵条件数忽略
- Netflix 大赛 2008：维度灾难

## V27 日常 · 矩阵在家
- 手机相机 = 矩阵旋转
- JPEG = 矩阵 DCT
- MP3 = 矩阵 FFT

## V28 社会系统 · PageRank / Netflix / 量化
- Google = 矩阵特征向量
- Netflix = 矩阵 SVD
- 量化 = 矩阵协方差

---

## 🎯 6 视角推荐组合

V04（最小例）+ V07（代几对偶）+ V14（ML）+ V15（工程）+ V20（比较）+ V24（跨书）

---

> 📖 配套：[Ross 51 示范](Ross51-概率-28视角完整深度.md) · [V07 代几对偶](../视角深度/V07-代几对偶.md)
