# Riemann 曲率张量：从 Christoffel 到 Einstein

> 曲率是几何的"DNA"——决定了空间的全部内蕴几何。

## 梯子
1. 度量 g_μν → 长度/角度
2. Christoffel Γ^k_ij = ½g^kl(∂_i g_jl + ∂_j g_il - ∂_l g_ij) → "连接"（平行移动）
3. Riemann 曲率 R^l_ijk = ∂_i Γ^l_jk - ∂_j Γ^l_ik + Γ^l_im Γ^m_jk - Γ^l_jm Γ^m_ik
4. Ricci 曲率 R_ij = R^k_ikj（Riemann 的迹）
5. 标量曲率 R = g^ij R_ij（Ricci 的迹）

## 对称性（Bianchi 恒等式）
R(X,Y)Z + R(Y,Z)X + R(Z,X)Y = 0（第一Bianchi）
∇R = 0（第二Bianchi，缩并后→Einstein方程的守恒律）

## 特殊情况
| 曲率 | 条件 | 例子 |
|------|------|------|
| R=0（平坦） | 度量=Euclid局部 | ℝⁿ, 圆柱面 |
| Ric=λg（Einstein） | 各向同性 | 球面(λ>0), 双曲(λ<0) |
| 常截面曲率 | 各向同性+均匀 | 球面/双曲空间 |
| Ric≥0(Lott-Sturm) | CD(0,N) | 极限空间 |

## 应用
- **广义相对论**：G_μν = R_μν - ½Rg_μν = 8πT_μν（Einstein方程）
- **Ricci流**：∂g/∂t = -2Ric → Perelman 证明 Poincaré
- **比较几何**：Ricci 下界 → 体积比较(Bishop-Gromov)

## 关联
- [代码库 21-微分几何](../../15-applications/代码库/21-微分几何_曲线与曲面.py)
- [百科-05-几何学](../百科-05-几何学.md)
- [百科-15-数学物理](../百科-15-数学物理.md)
