"""
LADR 核心 2: 内积空间与特征值 — 公理化线代下半部分
====================================================
阶段1 / 模块03 / LADR 第2弹
内积 (点积的推广) + Gram-Schmidt 正交化 + 特征值的抽象定义 + 谱定理
运行: python3 ladr_02_eigenvalue.py  (4 张 PNG)

§1 内积空间: 点积的公理化 (长度/角度/正交的推广)
§2 Gram-Schmidt 正交化 (任意基 → 正交基)
§3 特征值抽象定义: T(v)=λv (线性映射的不变方向)
§4 谱定理: 自伴算子可正交对角化 (LADR 的皇冠)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# §1 内积空间
def section_1_inner_product():
    print("=" * 70)
    print("§1 内积空间: 点积的公理化推广")
    print("=" * 70)
    print("""
    内积 <u,v> 满足 4 公理: 正定 / 对称(实) / 第一变元线性 / 共轭(复)。
    由此定义:
      长度 ‖v‖ = √<v,v>
      角度 cos θ = <u,v>/(‖u‖·‖v‖)
      正交 <u,v> = 0
    R^n 上标准内积就是点积 (W1 学过)。但内积可换 (定义不同的「长度/角度」)。
    """)
    u = np.array([2.0, 1.0]); v = np.array([1.0, 3.0])
    ip = u @ v
    norm_u, norm_v = np.linalg.norm(u), np.linalg.norm(v)
    cos = ip / (norm_u * norm_v)
    print(f"  R² 标准内积 (点积):")
    print(f"    <u,v> = {ip}, ‖u‖={norm_u:.3f}, ‖v‖={norm_v:.3f}")
    print(f"    cos θ = {cos:.3f}, θ = {np.degrees(np.arccos(cos)):.1f}°")
    # 不同内积: 加权 <u,v>_W = uᵀ W v, W=diag(4,1)
    W = np.diag([4.0, 1.0])
    ip_w = u @ W @ v
    nu_w = np.sqrt(u @ W @ u); nv_w = np.sqrt(v @ W @ v)
    cos_w = ip_w / (nu_w * nv_w)
    print(f"\n  加权内积 W=diag(4,1):")
    print(f"    <u,v>_W = {ip_w}, cos θ = {cos_w:.3f}, θ = {np.degrees(np.arccos(cos_w)):.1f}° (角度变了!)")
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.arrow(0, 0, u[0], u[1], head_width=0.1, color='C0', lw=2.5, length_includes_head=True)
    ax.arrow(0, 0, v[0], v[1], head_width=0.1, color='C2', lw=2.5, length_includes_head=True)
    ax.text(u[0]+0.1, u[1]+0.1, f'u, ‖u‖={norm_u:.2f}', color='C0')
    ax.text(v[0]+0.1, v[1]+0.1, f'v, θ={np.degrees(np.arccos(cos)):.1f}°', color='C2')
    ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 3.5); ax.set_aspect('equal')
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('内积定义长度/角度/正交\n(内积不同 → 角度不同, 但都是合法内积)')
    plt.tight_layout(); plt.savefig('ladr_ev_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_ev_s1.png")


# §2 Gram-Schmidt
def section_2_gram_schmidt():
    print("\n" + "=" * 70)
    print("§2 Gram-Schmidt 正交化")
    print("=" * 70)
    print("""
    定理: 任何有限维内积空间都有「正交基」(两两正交且长度1)。
    Gram-Schmidt: 从任意基 v₁..vₙ 构造正交基 e₁..eₙ:
      e₁ = v₁/‖v₁‖
      e_k = (v_k - Σ_{i<k}<v_k,e_i>e_i) / ‖...‖  (减去已正交化方向的投影)
    几何: 逐个「掰正」, 让新向量与已正交化的全部垂直。
    """)
    def gram_schmidt(vs):
        es = []
        for v in vs:
            u = v.copy().astype(float)
            for e in es:
                u -= (v @ e) * e   # 减去到已有正交基的投影
            es.append(u / np.linalg.norm(u))
        return np.array(es)
    V = np.array([[1., 1], [1, 2], [1, 0.5]])   # R^3 中 3 个向量 (实际 span R^2)
    V2 = np.array([[1., 1], [0, 1]])            # R^2 两向量
    E = gram_schmidt(V2)
    print(f"  原始基: {V2.tolist()}")
    print(f"  Gram-Schmidt 后: {np.round(E,4).tolist()}")
    print(f"  验证正交: <e1,e2>={E[0]@E[1]:.2e}, ‖e1‖={np.linalg.norm(E[0]):.4f}, ‖e2‖={np.linalg.norm(E[1]):.4f}")
    fig, ax = plt.subplots(figsize=(6, 6))
    for v, c, lbl in [(V2[0], 'C0', 'v1'), (V2[1], 'C2', 'v2'),
                      (E[0], 'red', 'e1 (正交化)'), (E[1], 'purple', 'e2 (正交化)')]:
        ax.arrow(0, 0, v[0], v[1], head_width=0.05, color=c, lw=2.5, length_includes_head=True, label=lbl)
    ax.set_xlim(-0.3, 1.5); ax.set_ylim(-0.3, 1.5); ax.set_aspect('equal')
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('Gram-Schmidt: 任意基 → 正交基\n(减投影, 单位化)')
    plt.tight_layout(); plt.savefig('ladr_ev_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_ev_s2.png")


# §3 特征值抽象
def section_3_eigen():
    print("\n" + "=" * 70)
    print("§3 特征值 (抽象): T(v)=λv 不变方向")
    print("=" * 70)
    print("""
    抽象定义: 对线性映射 T, 若存在非零 v 和标量 λ 使 T(v)=λv,
    则 λ 是 T 的特征值, v 是特征向量。
    几何 (W3 学过): 特征方向是 T「只缩放不旋转」的方向。
    抽象意义: 这些方向是理解 T 的最简坐标 (T 在特征基下是对角的!)。
    """)
    A = np.array([[3., 1], [1, 3]])   # 对称
    w, V = np.linalg.eigh(A)
    print(f"  A = {A.tolist()}")
    print(f"  特征值: {w}")
    print(f"  特征向量 (列): {np.round(V,4).tolist()}")
    for i in range(2):
        v = V[:, i]
        Av = A @ v
        print(f"    λ={w[i]:.1f}: A@v={np.round(Av,4)}, λ·v={np.round(w[i]*v,4)}, 一致? {np.allclose(Av, w[i]*v)}")
    # A 在特征基下 = 对角
    D = np.linalg.inv(V) @ A @ V
    print(f"  A 在特征基下 (V⁻¹AV) = {np.round(D, 6)} (对角化!)")
    fig, ax = plt.subplots(figsize=(6, 6))
    theta = np.linspace(0, 2*np.pi, 100)
    circle = np.stack([np.cos(theta), np.sin(theta)])
    ellipse = A @ circle
    ax.plot(circle[0], circle[1], 'gray', label='单位圆')
    ax.plot(ellipse[0], ellipse[1], 'C0', lw=2.5, label='A 作用后(椭圆)')
    colors = ['red', 'green']
    for i in range(2):
        v = V[:, i]
        ax.plot([-v[0], v[0]], [-v[1], v[1]], color=colors[i], lw=3,
                label=f'λ={w[i]:.0f} 特征方向')
    ax.set_aspect('equal'); ax.set_xlim(-4.5, 4.5); ax.set_ylim(-4.5, 4.5)
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('特征方向 = 椭圆长短轴\n(A 在特征基下是对角矩阵)')
    plt.tight_layout(); plt.savefig('ladr_ev_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_ev_s3.png")


# §4 谱定理
def section_4_spectral():
    print("\n" + "=" * 70)
    print("§4 谱定理 — LADR 的皇冠")
    print("=" * 70)
    print("""
    谱定理 (复/实内积空间): 自伴算子 (T=T*) 一定有「正交特征基」,
    即 T 可被正交对角化:
        T = λ₁·P₁ + λ₂·P₂ + ... + λₙ·Pₙ   (谱分解, P_i 正交投影)
    这是 W3 谱分解的严格版。它保证了 PCA、对称矩阵对角化、二次型等全部成立。
    """)
    rng = np.random.default_rng(0)
    A = rng.standard_normal((4, 4))
    S = A + A.T   # 对称化 (自伴)
    w, V = np.linalg.eigh(S)
    print(f"  随机 4×4 对称矩阵 S:")
    print(f"    特征值: {np.round(w, 4)}")
    print(f"    特征向量正交? VᵀV = I: {np.allclose(V.T @ V, np.eye(4))}")
    print(f"    S = VΛVᵀ 重构: {np.allclose(V @ np.diag(w) @ V.T, S)}")
    print(f"  → 谱定理保证: 实对称矩阵总能正交对角化 (PCA 的数学根基)")
    # 二次型可视化 (椭圆/双曲)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, M, name in [(axes[0], np.array([[2.,1],[1,2]]), '正定 (椭圆)'),
                        (axes[1], np.array([[1.,2],[2,1]]), '不定 (双曲线)')]:
        w, _ = np.linalg.eigh(M)
        x, y = np.meshgrid(np.linspace(-3, 3, 400), np.linspace(-3, 3, 400))
        z = M[0,0]*x**2 + 2*M[0,1]*x*y + M[1,1]*y**2
        ax.contour(x, y, z, levels=20, cmap='viridis')
        ax.set_title(f'xᵀMx 等高线: {name}\n特征值 {np.round(w,2)} (全正=椭圆, 异号=双曲)')
        ax.set_aspect('equal'); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('ladr_ev_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] ladr_ev_s4.png")
    print("\n  💡 至此 LADR 公理化线代完成:")
    print("     向量空间 → 内积 → 正交 → 特征值 → 谱定理")
    print("     数学结构清晰, 是阶段 2「泛函分析/算子理论」的入口。")


if __name__ == "__main__":
    print("🌀 LADR 核心 2: 内积空间与特征值  |  阶段1 / 模块03\n")
    section_1_inner_product()
    section_2_gram_schmidt()
    section_3_eigen()
    section_4_spectral()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 ladr_02_eigenvalue.md, 做练习。LADR 公理化线代完成!")
    print("=" * 70)
