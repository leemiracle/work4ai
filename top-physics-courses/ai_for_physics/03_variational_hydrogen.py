"""
变分法求氢原子基态能量 — 量子化学的最小实现
=============================================
用一组高斯基函数 (STO-3G 风格) 做变分法, 求 H 原子 (Z=1) 基态能量。

哈密顿 (原子单位 ℏ=m_e=e=4πε₀=1):
    H = -½∇² - Z/r       (动能 + 核吸引, 单电子无排斥)

变分原理: 试探波函数 ψ = Σ c_i φ_i, 最小化 ⟨ψ|H|ψ⟩/⟨ψ|ψ⟩
    → 广义本征值问题  H c = E S c
    其中 H_ij = ⟨φ_i|H|φ_j⟩, S_ij = ⟨φ_i|φ_j⟩

基组: N 个归一化 s 型高斯  φ_i(r) = (2α_i/π)^(3/4) exp(-α_i r²)
     用不同 α_i 覆盖不同空间尺度

精确基态能量: E = -0.5 Hartree = -13.6 eV (氢原子 1s)

零依赖 (仅 NumPy), 目标: 变分能量误差 < 1%
"""
import math
import numpy as np

np.random.seed(42)

# ============ 基组: N 个 s 型高斯 (Even-Tempered, α_i = α_0 β^i) ============
N_BASIS = 6
ALPHA_MIN, ALPHA_MAX = 0.10, 8.0   # 覆盖宽空间尺度
# 几何级数: α_i = α_min * (α_max/α_min)^(i/(N-1))
ALPHAS = ALPHA_MIN * (ALPHA_MAX / ALPHA_MIN) ** (np.arange(N_BASIS) / (N_BASIS - 1))
print(f"基组: {N_BASIS} 个高斯, α = {np.round(ALPHAS, 3)}")

# 归一化因子 N_i = (2α_i/π)^(3/4)
NORMS = (2 * ALPHAS / math.pi) ** 0.75


def phi(i, r):
    """第 i 个基函数 (球对称, 不含 4πr²)"""
    return NORMS[i] * np.exp(-ALPHAS[i] * r * r)


# ============ 数值积分网格 (球坐标) ============
R_GRID = np.linspace(1e-4, 15.0, 2000)   # 避开 r=0 (1/r 奇点)
DR = R_GRID[1] - R_GRID[0]
R2 = R_GRID ** 2


def overlap(i, j):
    """S_ij = ∫ φ_i φ_j d³r = 4π ∫ φ_i φ_j r² dr"""
    integrand = phi(i, R_GRID) * phi(j, R_GRID) * R2
    return 4 * math.pi * np.trapz(integrand, R_GRID)


def kinetic(i, j):
    """T_ij = ½ ∫ ∇φ_i·∇φ_j d³r = 8π α_i α_j ∫ r⁴ φ_i φ_j dr
    (分部变换 + 球对称 ∇φ = -2α r φ r̂)"""
    integrand = (R_GRID ** 4) * phi(i, R_GRID) * phi(j, R_GRID)
    return 8 * math.pi * ALPHAS[i] * ALPHAS[j] * np.trapz(integrand, R_GRID)


def nuclear(i, j, Z=1.0):
    """V_ij = ⟨φ_i|(-Z/r)|φ_j⟩ = -4π Z ∫ φ_i φ_j r dr"""
    integrand = R_GRID * phi(i, R_GRID) * phi(j, R_GRID)
    return -4 * math.pi * Z * np.trapz(integrand, R_GRID)


# ============ 组装矩阵 ============
S = np.array([[overlap(i, j) for j in range(N_BASIS)] for i in range(N_BASIS)])
T = np.array([[kinetic(i, j) for j in range(N_BASIS)] for i in range(N_BASIS)])
V = np.array([[nuclear(i, j) for j in range(N_BASIS)] for i in range(N_BASIS)])
H = T + V

print(f"\n重叠矩阵 S (应接近单位, 因基函数归一化但非正交):")
print(np.round(S, 4))

# ============ 解广义本征值问题 H c = E S c (纯 NumPy) ============
# 1. S 对角化: S = U_s D_s U_s^T
eigvals_s, U_s = np.linalg.eigh(S)
# 2. S^(-1/2) = U_s D_s^(-1/2) U_s^T
S_inv_half = U_s @ np.diag(1.0 / np.sqrt(eigvals_s)) @ U_s.T
# 3. 变换: H' = S^(-1/2) H S^(-1/2)
H_prime = S_inv_half @ H @ S_inv_half
# 4. 标准对角化
energies, coeffs_prime = np.linalg.eigh(H_prime)
# 5. 回变系数 c = S^(-1/2) c'
coeffs = S_inv_half @ coeffs_prime

# ============ 结果 ============
print("\n" + "=" * 70)
print("  变分法结果: 氢原子 (Z=1) 基态")
print("=" * 70)

E_EXACT = -0.5   # Hartree
print(f"\n  本征值 (Hartree): {np.round(energies, 5)}")
print(f"\n  精确基态能量:    E_1s = {E_EXACT:.5f} Hartree = -13.606 eV")

E_variational = energies[0]   # 最小本征值 = 基态
err = abs(E_variational - E_EXACT)
rel_err = err / abs(E_EXACT)
print(f"  变分基态能量:    E_var = {E_variational:.5f} Hartree = {E_variational*27.211:.3f} eV")
print(f"  绝对误差:        {err:.6f} Hartree")
print(f"  相对误差:        {rel_err*100:.3f}%")

# 基态波函数系数
c0 = coeffs[:, 0]
print(f"\n  基态波函数系数 c_i:")
for i in range(N_BASIS):
    print(f"    φ_{i} (α={ALPHAS[i]:.3f}):  c = {c0[i]:+.4f}")

# 验证归一化 ⟨ψ|ψ⟩ = 1
norm_check = c0 @ S @ c0
print(f"\n  归一化验证 ⟨ψ|ψ⟩ = {norm_check:.6f} (应=1)")

# 对比: 单个高斯 (N=1) 的变分能量 (最差近似)
print("\n" + "=" * 70)
print("  对比: 不同基组大小的变分能量")
print("=" * 70)
print(f"\n  {'基函数数':>8} | {'变分能量':>12} | {'相对误差':>10}")
print("  " + "-" * 40)
for n in [1, 2, 3, 4, N_BASIS]:
    # 取前 n 个 α
    a = ALPHAS[:n]
    nr = (2 * a / math.pi) ** 0.75

    def phic(i, r, al=a, nn=nr):
        return nn[i] * np.exp(-al[i] * r * r)

    def ov(i, j):
        integ = phic(i, R_GRID) * phic(j, R_GRID) * R2
        return 4 * math.pi * np.trapz(integ, R_GRID)

    def ki(i, j):
        integ = (R_GRID ** 4) * phic(i, R_GRID) * phic(j, R_GRID)
        return 8 * math.pi * a[i] * a[j] * np.trapz(integ, R_GRID)

    def nu(i, j):
        integ = R_GRID * phic(i, R_GRID) * phic(j, R_GRID)
        return -4 * math.pi * np.trapz(integ, R_GRID)

    Sc = np.array([[ov(i, j) for j in range(n)] for i in range(n)])
    Hc = np.array([[ki(i, j) + nu(i, j) for j in range(n)] for i in range(n)])
    ev_s, Uc = np.linalg.eigh(Sc)
    Sih = Uc @ np.diag(1 / np.sqrt(ev_s)) @ Uc.T
    Hp = Sih @ Hc @ Sih
    E_min = np.linalg.eigh(Hp)[0][0]
    print(f"  {n:>8} | {E_min:>12.5f} | {abs(E_min-E_EXACT)/0.5*100:>9.3f}%")

print("\n" + "=" * 70)
print("  ✦ 反直觉发现")
print("=" * 70)
print(f"""
  1. 变分原理保证 E_var ≥ E_exact (永远不会低于真实基态)。
     我们得到 {E_variational:.5f} ≥ -0.5, 满足。

  2. 只用 1 个高斯, 误差大; 加到 {N_BASIS} 个, 误差降到 {rel_err*100:.3f}%。
     这是"变分法"的核心: 基组越大, 越接近真实 (但永远不低于)。

  3. 这正是量子化学的基础。真实的分子计算 (PySCF) 用几十到几千个
     高斯基函数, 解同样的广义本征值问题。原理完全一样, 只是规模大。

  4. 对 H 原子, 解析解是 ψ_1s = (1/√π) e^(-r)。
     我们的高斯组合在逼近这个指数函数 —— 这是 STO-3G 的思想
     (用 3 个高斯拟合 1 个 Slater 型轨道)。

  5. 推广: 加双电子积分 (电子-电子排斥), 就是 Hartree-Fock。
     再加关联修正, 就是 CISD/CCSD。这就是量子化学的层级。
""")

if rel_err < 0.01:
    print(f"  ✓ 通过: 相对误差 {rel_err*100:.3f}% < 1%")
else:
    print(f"  ⚠ 误差 {rel_err*100:.3f}%, 可增大基组或调整 α 范围")
