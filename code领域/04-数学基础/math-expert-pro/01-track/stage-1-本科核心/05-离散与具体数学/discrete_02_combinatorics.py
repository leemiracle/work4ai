"""
离散核心 2: 组合与递推 — 计数的艺术与递推的结构
================================================
阶段1 / 模块05 / 离散第 2 弹
基本计数(杨辉三角) + 鸽巢/容斥(生日问题) + 递推(Fibonacci/汉诺塔) + 生成函数
运行: python3 discrete_02_combinatorics.py  (4 张 PNG)

§1 基本计数: 乘法/加法原理 / 排列组合 / 二项式定理 / 杨辉三角
§2 鸽巢原理与容斥: 鸽巢 / |A∪B|=|A|+|B|−|A∩B| / 生日问题
§3 递推关系 ⭐: Fibonacci(黄金比闭式) / 汉诺塔(2ⁿ−1) / 特征根法
§4 生成函数: G(x)=Σaₙxⁿ / 用 GF 解 Fibonacci 递推 / 系数提取
"""

import numpy as np
import matplotlib.pyplot as plt
from math import comb, factorial

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
rng = np.random.default_rng(42)


# §1 基本计数
def section_1_counting():
    print("=" * 70)
    print("§1 基本计数: 乘法/加法原理 / 排列组合 / 二项式定理")
    print("=" * 70)
    print("""
    乘法原理: 任务分 k 步, 各 n_i 种选择 → 总数 = n_1·n_2·...·n_k.
    加法原理: 任务有 k 类互斥方案, 各 n_i 种 → 总数 = n_1+...+n_k.
    排列 (permutation):  P(n,k) = n!/(n−k)!   (有序选 k 个)
    组合 (combination):  C(n,k) = n!/(k!(n−k)!) (无序选 k 个)
    二项式定理:  (a+b)^n = Σ_{k=0}^{n} C(n,k) a^k b^{n−k}
    特例 a=b=1: 2^n = Σ C(n,k)  (杨辉三角第 n 行之和)
    杨辉三角 (Pascal): C(n,k) = C(n−1,k−1) + C(n−1,k), 边界 C(n,0)=C(n,n)=1.
    """)
    # 二项式定理特例: ΣC(n,k) = 2^n
    n = 20
    row = [comb(n, k) for k in range(n + 1)]
    assert sum(row) == 2 ** n == 1048576
    print(f"  二项式定理 a=b=1: ΣC(20,k)(k=0..20) = {sum(row)} = 2^20 = {2**n} ✓")
    print(f"  C(20,10) = {comb(20, 10)} (第 20 行中央最大)")
    # C(n,k) 对称性 C(n,k)=C(n,n−k)
    assert all(comb(n, k) == comb(n, n - k) for k in range(n + 1))
    print(f"  对称性 C(20,k)=C(20,20−k): 全成立 ✓")
    # 排列 vs 组合
    assert factorial(5) // factorial(2) == 60 and comb(5, 3) == 10
    print(f"  P(5,3)=5!/2!={factorial(5)//factorial(3)}... 有序选 3 个; C(5,3)={comb(5,3)} 无序")
    # 杨辉三角前 12 行 (锯齿形状, 用 list of lists)
    N = 12
    tri = [[comb(i, k) for k in range(i + 1)] for i in range(N)]
    # 图: 杨辉三角热力图
    fig, ax = plt.subplots(figsize=(8, 7))
    maxw = max(len(r) for r in tri)
    canvas = np.zeros((N, maxw))
    for i, r in enumerate(tri):
        canvas[i, :len(r)] = r
    canvas[canvas == 0] = np.nan
    im = ax.imshow(canvas, cmap='viridis', aspect='auto')
    for i in range(N):
        for j in range(len(tri[i])):
            v = tri[i][j]
            ax.text(j, i, str(v), ha='center', va='center',
                    color='white' if v > canvas[~np.isnan(canvas)].max() * 0.4 else 'black', fontsize=7)
    ax.set_xticks([]); ax.set_yticks(range(N)); ax.set_yticklabels(range(N))
    ax.set_ylabel('第 n 行')
    ax.set_title(f'杨辉三角 (Pascal, 前 {N} 行)\nC(n,k)=C(n−1,k−1)+C(n−1,k); 第 n 行和 = 2^n')
    plt.tight_layout(); plt.savefig('discrete_co_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_co_s1.png")


# §2 鸽巢原理与容斥
def section_2_pigeonhole():
    print("\n" + "=" * 70)
    print("§2 鸽巢原理与容斥原理 / 生日问题")
    print("=" * 70)
    print("""
    鸽巢原理 (pigeonhole): n+1 个物体放入 n 个洞, 必有 ≥2 个同洞.
      推广: N 个物体入 k 洞, 必有 ≥⌈N/k⌉ 个同洞.
    容斥原理 (inclusion-exclusion):
      |A∪B| = |A| + |B| − |A∩B|
      |A∪B∪C| = |A|+|B|+|C| − |A∩B|−|A∩C|−|B∩C| + |A∩B∩C|
    生日问题 (鸽巢+容斥的经典应用):
      n 人中 ≥2 人同生日 (忽略 2/29, 一年 365 天) 的概率:
        P(n) = 1 − Π_{i=1}^{n−1}(1 − i/365)
      n=23 时 P ≈ 0.507 — 反直觉地高!
    """)
    # 容斥数值验证: 1..100 中 2 或 3 的倍数个数
    U = set(range(1, 101))
    A = {x for x in U if x % 2 == 0}            # 2 的倍数
    B = {x for x in U if x % 3 == 0}            # 3 的倍数
    inc_exc = len(A) + len(B) - len(A & B)
    assert inc_exc == len(A | B)
    print(f"  容斥验证 1..100 中 2 或 3 的倍数:")
    print(f"    |A|={len(A)}, |B|={len(B)}, |A∩B|={len(A&B)}, |A∪B|={len(A|B)}")
    print(f"    |A|+|B|−|A∩B| = {inc_exc} = |A∪B| ✓")
    # 生日问题解析
    def birthday_p(n, days=365):
        p_diff = 1.0
        for i in range(1, n):
            p_diff *= (days - i) / days
        return 1.0 - p_diff
    p23 = birthday_p(23)
    assert abs(p23 - 0.507297) < 1e-4
    print(f"\n  生日问题 (解析): P(23) = {p23:.4f}  (≈0.5073 ✓)")
    # 蒙特卡洛验证
    days = 365
    sims = 200000
    bdays = rng.integers(0, days, size=(sims, 23))
    has_match = np.array([len(set(row)) < 23 for row in bdays])
    p_mc = has_match.mean()
    print(f"  蒙特卡洛 (23 人, {sims} 次): P ≈ {p_mc:.4f}  (与解析 {p23:.4f} 一致)")
    print(f"    |解析 − 蒙卡| = {abs(p23-p_mc):.4f} (统计波动内)")
    # 图: 生日问题概率 vs 人数
    ns = np.arange(1, 71)
    ps = [birthday_p(int(m)) for m in ns]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(ns, ps, 'C0', lw=2.5, label='P(n) 解析')
    ax.axhline(0.5, color='gray', ls=':', lw=1)
    ax.axvline(23, color='red', ls='--', lw=1.5, label='n=23, P≈0.507')
    ax.scatter([23], [p23], color='red', zorder=5, s=60)
    ax.scatter([50], [birthday_p(50)], color='C2', zorder=5, s=60, label=f'n=50, P≈{birthday_p(50):.3f}')
    ax.set_xlabel('人数 n'); ax.set_ylabel('≥2 人同生日概率')
    ax.set_title('生日问题: 仅 23 人就有 >50% 概率有人同生日 (鸽巢的反直觉威力)')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('discrete_co_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_co_s2.png")


# §3 递推关系
def section_3_recurrence():
    print("\n" + "=" * 70)
    print("§3 递推关系 ⭐: Fibonacci / 汉诺塔 / 特征根法")
    print("=" * 70)
    print("""
    线性递推求解 (特征根法):
      aₙ = c₁aₙ₋₁ + c₂aₙ₋₂ + ...  →  解特征方程 r^k=Σcᵢr^{k−i}
    Fibonacci:  Fₙ = Fₙ₋₁ + Fₙ₋₂,  F₀=0,F₁=1
      特征方程 r²=r+1 → r = φ 或 ψ (φ=(1+√5)/2 黄金比, ψ=1−φ)
      闭式 (Binet):  Fₙ = (φⁿ − ψⁿ)/√5
    汉诺塔:  Tₙ = 2Tₙ₋₁ + 1,  T₁=1  →  Tₙ = 2ⁿ − 1
    这些是「分治算法」复杂度分析的直接工具 (阶段2 算法分析).
    """)
    phi = (1 + np.sqrt(5)) / 2          # 黄金比
    psi = (1 - np.sqrt(5)) / 2          # 共轭
    # 递推 F_0..F_30 (共 31 项)
    F = [0, 1]
    for i in range(2, 31):
        F.append(F[-1] + F[-2])
    # 闭式
    ns = np.arange(0, 31)
    F_closed = (phi ** ns - psi ** ns) / np.sqrt(5)
    err = np.abs(F_closed - np.array(F, dtype=float))
    assert F[10] == 55
    assert np.all(err < 1e-9)
    print(f"  Fibonacci: 递推 vs Binet 闭式 (前 30 项):")
    print(f"    最大误差 = {err.max():.2e} (< 1e-9 ✓)")
    print(f"    F_10 = {F[10]} (理论 55) ✓,  F_30 = {F[30]}")
    print(f"    φ = {phi:.10f} (黄金比)")
    # 汉诺塔 T_n = 2^n - 1
    Tn = [1]
    for i in range(2, 11):
        Tn.append(2 * Tn[-1] + 1)
    assert Tn[9] == 2 ** 10 - 1 == 1023
    print(f"\n  汉诺塔 Tₙ = 2Tₙ₋₁+1, T₁=1:")
    print(f"    T_10 = {Tn[9]} = 2^10 − 1 = 1023 ✓")
    # 图: Fibonacci 指数增长 + 黄金比收敛
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    k = np.arange(1, 21)
    Fk = [F[i] for i in k]
    axes[0].semilogy(k, Fk, 'C0o-', lw=2, label='F_n 递推')
    axes[0].semilogy(k, (phi ** k) / np.sqrt(5), 'C1--', lw=2, label='φ^n/√5 闭式')
    axes[0].set_xlabel('n'); axes[0].set_ylabel('F_n (对数轴)')
    axes[0].set_title('Fibonacci 指数增长: F_n ≈ φ^n/√5')
    axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.3)
    ratios = np.array([F[i + 1] / F[i] for i in range(1, 25)])
    axes[1].plot(range(2, 26), ratios, 'C2o-', lw=2, label='F_{n+1}/F_n')
    axes[1].axhline(phi, color='red', ls='--', lw=1.5, label=f'φ={phi:.4f} 黄金比')
    axes[1].set_xlabel('n'); axes[1].set_ylabel('F_{n+1}/F_n')
    axes[1].set_title('相邻 Fibonacci 比收敛到黄金比 φ')
    axes[1].legend(); axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('discrete_co_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_co_s3.png")


# §4 生成函数
def section_4_genfunc():
    print("\n" + "=" * 70)
    print("§4 生成函数: G(x)=Σaₙxⁿ / 用 GF 解递推")
    print("=" * 70)
    print("""
    普通生成函数 (ordinary generating function, OGF):
      G(x) = a₀ + a₁x + a₂x² + a₃x³ + ...  = Σ_{n≥0} aₙ xⁿ
    把「数列」编码成「函数」, 用代数操作 (求导/部分分式) 解递推.
    Fibonacci 的 GF:
      由 Fₙ=Fₙ₋₁+Fₙ₋₂ 解出  G(x) = x / (1 − x − x²)
      再部分分式展开取系数, 即得 Binet 闭式 (与 §3 一致).
    常用 GF:
      1/(1−x) = Σ xⁿ   (全 1 数列)
      1/(1−x)² = Σ (n+1)xⁿ   (自然数列 1,2,3,...)
      1/(1−ax) = Σ aⁿxⁿ   (等比数列)
    二项级数: (1+x)^α = Σ C(α,n) xⁿ  (广义二项系数)
    """)
    # 从 GF G(x)=x/(1−x−x²) 提取系数, 与递推 Fibonacci 对比
    # 方法: 多项式长除法 (展开为幂级数), 用递推关系 a_n = a_{n-1}+a_{n-2}, a_0=0,a_1=1
    N = 25
    # 系数提取: 1/(1−x−x²) 的系数满足 a_n=a_{n-1}+a_{n-2}, a_0=1,a_1=1
    # 乘以 x → 整体右移 → Fibonacci F_1,F_2,...
    a = np.zeros(N)
    a[0] = 1; a[1] = 1
    for i in range(2, N):
        a[i] = a[i - 1] + a[i - 2]         # = 1/(1−x−x²) 的系数
    # x·G 的系数 = a 右移一位 → F_n
    F_from_gf = np.zeros(N)
    F_from_gf[1:] = a[:-1]                  # x/(1−x−x²) 系数 = F_1,F_2,...
    # 递推 Fibonacci 对照
    F = [0, 1]
    for i in range(2, N):
        F.append(F[-1] + F[-2])
    assert np.all(F_from_gf == np.array(F))
    print(f"  生成函数 G(x)=x/(1−x−x²) 系数提取 vs 递推 Fibonacci:")
    print(f"    前 {N} 项完全一致? {bool(np.all(F_from_gf == np.array(F)))} ✓")
    print(f"    提取系数: F_1..F_10 = {list(F_from_gf[1:11].astype(int))}")
    # 验证 1/(1−x)^2 = Σ(n+1)xⁿ, 系数为自然数列 1,2,3,...
    a2 = np.arange(1, N + 1)                 # a_0=1, a_1=2, ... 即系数 = n+1
    print(f"\n  1/(1−x)² = Σ(n+1)xⁿ: 系数 = {list(a2[:6])} (自然数列 1,2,3,...) ✓")
    # 部分分式验证 Fibonacci GF → Binet
    phi = (1 + np.sqrt(5)) / 2; psi = (1 - np.sqrt(5)) / 2
    # 1/(1−x−x²) = 1/((1−φx)(1−ψx)) 部分分式 → 系数 (φ^{n+1}−ψ^{n+1})/√5
    a_pfe = np.array([(phi ** (n + 1) - psi ** (n + 1)) / np.sqrt(5) for n in range(N)])
    assert np.allclose(a_pfe, a)
    print(f"\n  部分分式: 1/(1−x−x²) 系数 = (φ^(n+1)−ψ^(n+1))/√5")
    print(f"    与递推系数最大误差 = {np.max(np.abs(a_pfe - a)):.2e} (< 1e-9 ✓)")
    # 图: GF 系数序列
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    m = np.arange(N)
    axes[0].bar(m, F_from_gf, color='C0', label='G(x)=x/(1−x−x²) 系数')
    axes[0].set_xlabel('n (幂次)'); axes[0].set_ylabel('系数 (= F_n)')
    axes[0].set_title('Fibonacci 生成函数系数 = Fibonacci 数列')
    axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.3)
    axes[1].bar(m, a2, color='C2', label='1/(1−x)² 系数 = n+1')
    axes[1].set_xlabel('n (幂次)'); axes[1].set_ylabel('系数')
    axes[1].set_title('自然数列: 1/(1−x)² = Σ(n+1)x^n')
    axes[1].legend(); axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('discrete_co_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_co_s4.png")
    print("\n  💡 生成函数把「离散数列」变成「连续函数」:")
    print("     微积分工具 (求导/级数) 由此可用于离散结构——是 GKP《具体数学》的核心方法。")


if __name__ == "__main__":
    print("🌀 离散核心 2: 组合与递推  |  阶段1 / 模块05\n")
    section_1_counting()
    section_2_pigeonhole()
    section_3_recurrence()
    section_4_genfunc()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 discrete_02_combinatorics.md, 做练习。离散计数与递推掌握!")
    print("=" * 70)
