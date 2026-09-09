"""索洛增长模型：稳态不动点、黄金律与收敛速度（断言自验）
对应《讲透宏观经济学》00 章（长期段）与 04 章（走廊 1：增长模型求解）。

模型（人均形式，技术进步劳动扩大型）：
    k_{t+1} = ( s·k_t^α + (1−δ)·k_t ) / (1+n_eff),   n_eff = n + g + n·g ≈ n+g
    稳态（有效劳动单位）k* = ( s / (n+g+δ) )^(1/(1−α))
    黄金律：max c* = k*^α − (n+g+δ)k*  ⟹  s_gold = α
    收敛速度（对数线性化）：λ = (1−α)(n+g+δ)

断言（自验证）：
    (a) 迭代稳态与解析稳态相对误差 < 1e-6（不动点收敛）
    (b) 黄金律：数值搜索的 s_gold 与解析解 α 相差 < 1e-4
    (c) 收敛速度：线性区（相对缺口 1e-4~0.5）对数回归得 λ_num，
        与解析 λ=(1−α)(n+g+δ) 相对偏差 < 15%（对数线性化近似的带内验证）
"""
import numpy as np

# ── 校准（教学标准值：α=资本收入份额，n=人口，g=技术，δ=折旧，s=储蓄率） ──
ALPHA, N, G, DELTA, S = 0.33, 0.01, 0.02, 0.06, 0.28
NEFF = N + G + N * G          # 有效劳动增长率（离散精确式）


def k_star_analytic(s, alpha=ALPHA, neff=NEFF, delta=DELTA):
    """解析稳态：k̇=0 ⟹ s·k^α=(n+g+δ)k。"""
    return (s / (neff + delta)) ** (1.0 / (1.0 - alpha))


def k_next(k, s=ALPHA * 0 + S, alpha=ALPHA, neff=NEFF, delta=DELTA):
    """离散动态方程（劳动扩大型技术进步下的有效劳动单位）。"""
    return (s * k ** alpha + (1.0 - delta) * k) / (1.0 + neff)


def converge(k0=0.1, tol=1e-12, max_iter=200000, **kw):
    """不动点迭代：单调收敛到稳态（该映射在稳态附近压缩）。"""
    k = k0
    for _ in range(max_iter):
        k_new = k_next(k, **kw)
        if abs(k_new - k) < tol:
            return k_new
        k = k_new
    raise RuntimeError("不收敛——检查参数")


def main():
    # ── (a) 迭代稳态 vs 解析稳态 ──
    k_star_num = converge()
    k_star_ana = k_star_analytic(S)
    err = abs(k_star_num - k_star_ana) / k_star_ana
    print(f"(a) 稳态：迭代={k_star_num:.8f}  解析={k_star_ana:.8f}  "
          f"相对误差={err:.2e}   (断言 < 1e-6)")
    assert err < 1e-6, "不动点迭代应收敛到解析稳态"

    # 收敛路径记录（供 (c) 用）：从 k0=0.1 出发
    path = [0.1]
    for _ in range(4000):
        path.append(k_next(path[-1]))
    path = np.array(path)
    gap = np.log(path) - np.log(k_star_ana)          # 对数缺口

    # ── (b) 黄金律：数值搜索 s_gold vs 解析 α ──
    ss_grid = np.linspace(0.05, 0.90, 45001)        # 步长 ~1.9e-5，网眼 < 容差一半
    c_star = np.array([k_star_analytic(s) ** ALPHA - (NEFF + DELTA) * k_star_analytic(s)
                       for s in ss_grid])
    s_gold_num = ss_grid[int(np.argmax(c_star))]
    print(f"(b) 黄金律储蓄率：数值={s_gold_num:.4f}  解析=α={ALPHA}  "
          f"差={abs(s_gold_num - ALPHA):.2e}   (断言 < 1e-4)")
    assert abs(s_gold_num - ALPHA) < 1e-4, "黄金律应为 s*=α"

    # ── (c) 收敛速度：线性区对数回归 vs 解析 λ=(1−α)(n+g+δ) ──
    lam_ana = (1 - ALPHA) * (NEFF + DELTA)
    # 线性区窗口：相对缺口 r_t 在 [1e-4, 0.5] 之间（远离稳态非线性、
    # 贴近稳态则被浮点噪声污染）——该窗口内 r_{t+1} ≈ (1−λ)·r_t
    r = (path - k_star_ana) / k_star_ana
    mask = (np.abs(r) > 1e-4) & (np.abs(r) < 0.5)
    t_win = np.where(mask)[0]
    slope = np.polyfit(t_win, np.log(np.abs(r[t_win])), 1)[0]
    lam_num = -slope
    half_life = np.log(2.0) / lam_num
    rel = abs(lam_num - lam_ana) / lam_ana
    print(f"(c) 收敛速度：数值={lam_num*100:.2f}%/期  解析={lam_ana*100:.2f}%/期  "
          f"相对偏差={rel*100:.1f}%  半衰期≈{half_life:.0f} 期   (断言 < 15%)")
    assert rel < 0.15, "数值收敛速度应在对数线性化解析值的带内"

    # 附加事实：不同初值都到同一稳态（全局收敛演示）
    k_far = converge(k0=5.0)
    assert abs(k_far - k_star_ana) / k_star_ana < 1e-6
    print("    附：k0=5.0（远端初值）同样收敛到同一稳态 ✅（全局收敛）")

    print("\n全部断言通过 ✅  索洛：稳态是压缩不动点，黄金律是 s*=α，"
          "收敛速度是 λ=(1−α)(n+g+δ)。")
    print("带走一句（00 章）：储蓄率只有水平效应，没有增长效应——"
          "持续增长只能来自 g（技术）。")

if __name__ == "__main__":
    main()
