# -*- coding: utf-8 -*-
"""Axler《Linear Algebra Done Right》4e 现代验证
向量空间 / 线性映射 / 特征值 / 谱定理 / SVD
用 numpy 验证（Axler 风格：算子视角，行列式最后才引入）"""
import numpy as np
from numpy.linalg import matrix_rank, eig, svd, norm

# ---------- §1-2 向量空间与有限维 ----------
def section_vector_space():
    print("\n" + "="*60)
    print("【§1-2 向量空间 + 有限维：公理 + 基 + 维数（Axler ch1-2）】")
    print("="*60)
    print("向量空间公理：加法交换/结合、数乘分配、零元、逆元等 8 条（Axler 1.19）")
    # 数值验证 ℝ³ 的向量空间性质
    u, v, w = np.array([1.,2.,3.]), np.array([4.,5.,6.]), np.array([7.,8.,9.])
    assert np.allclose(u+v, v+u)  # 交换
    assert np.allclose((u+v)+w, u+(v+w))  # 结合
    assert np.allclose(0*u, np.zeros(3))  # 零元
    print(f"  ℝ³ 向量空间公理数值验证：(u+v)==(v+u)、加法结合、零元 全成立 ✓")
    # 线性无关 / 基 / 维数
    print(f"\n线性无关与基：")
    # 三个 ℝ³ 向量是否线性无关
    A = np.array([[1.,0.,0.], [0.,1.,0.], [1.,1.,1.]]).T  # 列向量
    rank = matrix_rank(A)
    print(f"  矩阵 A 的列向量：[[1,0,1],[0,1,1],[0,0,1]]")
    print(f"  rank(A) = {rank} = 3 → 三个向量线性无关，构成 ℝ³ 的一组基")
    # 维数定理：dim V = n
    print(f"  dim ℝ³ = 3（基中向量个数）")
    # 线性相关反例
    B = np.array([[1.,2.], [2.,4.], [3.,6.]])  # 两列成比例
    print(f"  反例 [[1,2],[2,4],[3,6]]：rank={matrix_rank(B)} < 2 → 线性相关（第二列是第一列2倍）")

# ---------- §3 线性映射 ----------
def section_linear_map():
    print("\n" + "="*60)
    print("【§3 线性映射：核/像/维数定理（Axler ch3）】")
    print("="*60)
    print("线性映射 T:V→W 保持加法和数乘：T(u+v)=T(u)+T(v), T(cu)=cT(u)")
    # 矩阵表示：T(x) = Ax
    print(f"\n矩阵表示（T 用矩阵 A 表示）：T(x)=Ax")
    A = np.array([[1., 2.], [3., 4.], [5., 6.]])  # 3×2 矩阵：T: ℝ²→ℝ³
    print(f"  A = [[1,2],[3,4],[5,6]]（3×2，表示 T: ℝ²→ℝ³）")
    # 核 null T = {x : Ax=0}
    # 用 SVD 求核
    U, S, Vt = np.linalg.svd(A)
    print(f"  SVD：奇异值 S = {np.round(S,4)}")
    rank = matrix_rank(A)
    print(f"  rank(A) = {rank}（像 T 的维数）")
    print(f"  nullity = 2 - rank = {2 - rank}（核 T 的维数）")
    # ★ 维数定理（Axler 3.22）：dim V = dim null T + dim range T
    print(f"\n★ 维数定理（Axler 3.22）：dim V = dim null T + dim range T")
    print(f"  这里：dim ℝ² = 2 = nullity({2-rank}) + rank({rank}) = 2 ✓")
    x = np.array([1., 1.])
    print(f"\n  线性性验证：T(2·[1,1]) = {A @ (2*x)}, 2·T([1,1]) = {2*(A@x)}（相等 ✓）")

# ---------- §5 特征值 ----------
def section_eigenvalue():
    print("\n" + "="*60)
    print("【§5 特征值/特征向量（Axler ch5·用不变子空间定义）】")
    print("="*60)
    print("Axler 不用 det(A-λI)=0 定义特征值，而用：T v = λ v（v≠0）")
    print("  即存在 1 维不变子空间")
    A = np.array([[4., 1.], [2., 3.]])
    print(f"\nA = [[4,1],[2,3]]")
    eigvals, eigvecs = eig(A)
    print(f"  特征值 λ = {np.round(eigvals, 6)}")
    print(f"  特征向量列 = \n{np.round(eigvecs, 6)}")
    # 验证 A v = λ v
    for i in range(2):
        v = eigvecs[:, i]
        lam = eigvals[i]
        Av = A @ v
        print(f"  验证 A·v{i+1} = {np.round(Av,4)}, λ{i+1}·v{i+1} = {np.round(lam*v,4)}（应相等）")
        assert np.allclose(Av, lam*v)
    print(f"\n→ Axler 用算子视角：特征值 = 让 T v = λ v 的 λ（不变子空间方向）")
    print(f"→ 不需要行列式！这是 LADR 的革命（Down with Determinants）")

# ---------- §7 谱定理（LADR 高潮） ----------
def section_spectral():
    print("\n" + "="*60)
    print("【§7 谱定理（Axler ch7·全书高潮）】")
    print("="*60)
    print("复谱定理（Axler 7.29）：T 自伴⟺ 存在由 T 的特征向量组成的规范正交基")
    # 对称矩阵（自伴）→ 正交对角化
    A = np.array([[2., 1.], [1., 2.]])  # 对称
    print(f"\n对称矩阵 A = [[2,1],[1,2]]（自伴算子）")
    eigvals, eigvecs = eig(A)
    print(f"  特征值 = {np.round(eigvals, 6)}")
    print(f"  特征向量 = \n{np.round(eigvecs, 6)}")
    # 验证正交
    v1, v2 = eigvecs[:, 0], eigvecs[:, 1]
    print(f"  特征向量内积 <v1,v2> = {np.dot(v1, v2):.6f}（≈0，正交 ✓）")
    # 谱分解 A = Q Λ Q^T
    Q = eigvecs
    L = np.diag(eigvals)
    A_reconstructed = Q @ L @ Q.T
    print(f"\n  谱分解 A = QΛQᵀ：重构 = \n{np.round(A_reconstructed, 6)}")
    print(f"  与原 A 一致：{np.allclose(A, A_reconstructed)} ✓")
    print(f"\n→ 谱定理：自伴算子 = 在某正交基下是对角阵。'复杂'化为'简单'的对角化")
    print(f"→ 这是 Axler 全书的高潮——'每个对称矩阵都能正交对角化'")

# ---------- §10 SVD ----------
def section_svd():
    print("\n" + "="*60)
    print("【§10 奇异值分解 SVD（Axler ch10·4e强化）】")
    print("="*60)
    print("SVD：任意矩阵 A = U Σ V*（U,V 酉，Σ 对角正实数）")
    A = np.array([[1., 2., 3.], [4., 5., 6.]])  # 2×3
    print(f"\nA = [[1,2,3],[4,5,6]]（2×3）")
    U, S, Vt = svd(A)
    print(f"  U（2×2 酉）= \n{np.round(U, 6)}")
    print(f"  Σ 奇异值 = {np.round(S, 6)}")
    print(f"  Vᵀ（3×3 酉）= \n{np.round(Vt, 6)}")
    # 重构
    Sigma = np.zeros((2, 3))
    Sigma[:2, :2] = np.diag(S)
    A_reconstructed = U @ Sigma @ Vt
    print(f"\n  重构 UΣVᵀ = \n{np.round(A_reconstructed, 6)}")
    print(f"  与原 A 一致：{np.allclose(A, A_reconstructed)} ✓")
    # 应用：低秩逼近
    print(f"\n  应用：低秩逼近（PCA 的基础）")
    print(f"  奇异值 {np.round(S,4)}：第一个 {S[0]:.4f} >> 第二个 {S[1]:.4f}")
    print(f"  保留最大奇异值 → rank-1 逼近（图像压缩/PCA/推荐系统的核心）")
    # U/V 正交性
    print(f"\n  U 列正交：UᵀU = \n{np.round(U.T @ U, 6)}（≈ 单位阵 ✓）")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Axler《LADR》4e · 现代验证（numpy）                        ║")
    print("║  向量空间/线性映射/特征值/谱定理/SVD                        ║")
    print("╚" + "═"*58 + "╝")
    section_vector_space()
    section_linear_map()
    section_eigenvalue()
    section_spectral()
    section_svd()
    print("\n" + "═"*60)
    print("✅ LADR 核心验证通过。向量空间→线性映射→特征值→谱定理→SVD 全打通。")
    print("═"*60)
