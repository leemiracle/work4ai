# -*- coding: utf-8 -*-
"""古德哈特定律数值演示 + 简单 A/B 检验 + t 检验功效曲线。

00 章 §七(反直觉:指标成为目标即失真)与 02 章 §三(报告规范)/04 章走廊 2 配套实验。纯标准库。

设定: 管理者想优化真目标 T(长期价值/组织健康),手里只有代理指标 P(点击率/工时/完成量)可测。
     行动空间=单位预算的二维分配 a=(a1,a2),代理方向 x=(1,0),
     真目标方向 y=(cosφ, sinφ)——φ 是「错位角」:指标体系歪了多少。
     P(a)=x·a,T(a)=y·a。
对照: 几何层(期望,确定性):优化代理 ⟹ a=x ⟹ T=cosφ,损失 L=1−cosφ 应随 φ 单调上升;
         φ>90° 时 cosφ<0——优化代理反而把真目标做负(古德哈特的机器形态)。
     实验层(蒙特卡洛):对照版 vs 按代理优化的新版,每用户 Bernoulli 结果;
         代理提升固定 δ_P=+3pp,真目标提升=δ_P·cosφ(代理提升在真方向上的投影);
         两个指标各做 Welch t 检验(大样本正态近似)——看「代理显著赢、真目标显著输」的判决书。
     功效层:真实效应 δ=2pp 的 t 检验功效曲线 power(n),与经验功效对照,
         并解出 80% 功效所需样本量——「管理效应小 ⟹ 必须上规模」的机器版。
场景: φ 从 0°(指标=目标)扫到 180°(指标=反目标);A/B 两臂各 20000 用户。

跑法: python experiments/00_goodhart_ab.py
"""

import math
import random

# ---------- 极简正态 CDF/分位 ----------
def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p):  # 粗界+二分精修
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------- 统计两件套:Welch t 与双侧 p(大样本正态近似,A/B 平台标准做法) ----------
def t_welch(xs_mean, xs_var, xs_n, ys_mean, ys_var, ys_n):
    se2 = xs_var / xs_n + ys_var / ys_n
    return (xs_mean - ys_mean) / math.sqrt(se2)


def p_two_sided(z):
    return max(2.0 * (1.0 - norm_cdf(abs(z))), 1e-16)   # clamp 防下溢显示 0


def run_arm(rng, p, n):
    """一臂的 Bernoulli 结果:返回 (均值, 样本方差)。"""
    s = sum(1 for _ in range(n) if rng.random() < p)
    mean = s / n
    var = (s * (1.0 - mean) ** 2 + (n - s) * mean ** 2) / max(1, n - 1)
    return mean, var


# ---------- Part 1: 古德哈特几何(期望层,确定性) ----------
def goodhart_geometry():
    print("=" * 66)
    print("Part 1 古德哈特几何:优化代理所得的真目标 T=cosφ,损失 L=1−cosφ")
    print("=" * 66)
    grid = [0.0, math.pi / 6, math.pi / 3, math.pi / 2,
            2 * math.pi / 3, 5 * math.pi / 6, math.pi]
    rows = []
    for phi in grid:
        rows.append((phi, math.cos(phi), 1.0 - math.cos(phi)))
    print(f"{'错位角φ':>10} | {'cosφ(真目标)':>12} | {'损失 L=1−cosφ':>14}")
    for phi, c, loss in rows:
        print(f"{math.degrees(phi):8.0f}° | {c:14.3f} | {loss:14.3f}")
    return rows


# ---------- Part 2: A/B 扫描(代理 vs 真目标两份判决书) ----------
def ab_sweep(seed=20260907):
    print()
    print("=" * 66)
    print("Part 2 A/B 扫描:δ_P=+3pp 固定,真目标提升=δ_P·cosφ(每臂 20000 用户)")
    print("=" * 66)
    rng = random.Random(seed)
    n, dP = 20000, 0.03
    p_proxy0, p_true0 = 0.10, 0.35          # 对照版:点击率 10%,留存 35%
    phis = [0.0, math.pi / 3, math.pi / 2,
            2 * math.pi / 3, 5 * math.pi / 6, math.pi]
    results = []
    print(f"{'φ':>6} | {'代理提升':>16} | {'真目标提升':>16} | 真目标 p 值")
    for phi in phis:
        c0, v0 = run_arm(rng, p_proxy0, n)                  # 对照·代理
        c1, v1 = run_arm(rng, p_proxy0 + dP, n)             # 处理·代理
        t0, w0 = run_arm(rng, p_true0, n)                   # 对照·真
        t1, w1 = run_arm(rng, p_true0 + dP * math.cos(phi), n)  # 处理·真
        z_proxy = t_welch(c1, v1, n, c0, v0, n)
        z_true = t_welch(t1, w1, n, t0, w0, n)
        results.append({"phi": phi,
                        "proxy_lift": c1 - c0, "proxy_p": p_two_sided(z_proxy),
                        "true_lift": t1 - t0, "true_p": p_two_sided(z_true)})
        r = results[-1]
        print(f"{math.degrees(phi):5.0f}° | {r['proxy_lift']*100:+9.2f}pp "
              f"(p={r['proxy_p']:.2e}) | {r['true_lift']*100:+9.2f}pp "
              f"(p={r['true_p']:.2e})")
    return results


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (vx * vy)


# ---------- Part 3: t 检验功效曲线(小效应要多少人) ----------
def analytic_power(delta, n, p_bar, alpha=0.05):
    """双侧 z 检验功效(合并方差正态近似):power=Φ(λ−z)+Φ(−λ−z),λ=δ·√(n/2σ²)。"""
    sigma2 = p_bar * (1.0 - p_bar)
    lam = delta * math.sqrt(n / (2.0 * sigma2))
    z = norm_ppf(1.0 - alpha / 2.0)
    return norm_cdf(lam - z) + norm_cdf(-lam - z)


def empirical_power(delta, n, p0=0.35, reps=400, seed=97):
    """真实效应 δ 下重复实验,数 p<0.05 的频率。"""
    rng = random.Random(seed)
    hits = 0
    for _ in range(reps):
        m0, v0 = run_arm(rng, p0, n)
        m1, v1 = run_arm(rng, p0 + delta, n)
        if p_two_sided(t_welch(m1, v1, n, m0, v0, n)) < 0.05:
            hits += 1
    return hits / reps


def power_curve():
    print()
    print("=" * 66)
    print("Part 3 功效曲线:真目标真实提升 δ=+2pp,α=.05 双侧")
    print("=" * 66)
    delta, p_bar = 0.02, 0.35
    print(f"{'n/臂':>8} | {'解析功效':>8} | {'经验功效(400次)':>14}")
    table = []
    for n in (500, 1000, 2000, 5000, 10000, 20000):
        pw = analytic_power(delta, n, p_bar)
        ep = empirical_power(delta, n)
        table.append((n, pw, ep))
        print(f"{n:8d} | {pw:8.3f} | {ep:14.3f}")
    # 80% 功效所需样本量(二分)
    lo, hi = 100, 10_000_000
    for _ in range(60):
        mid = (lo + hi) / 2
        if analytic_power(delta, mid, p_bar) < 0.80:
            lo = mid
        else:
            hi = mid
    n80 = round((lo + hi) / 2)
    z_a, z_b = norm_ppf(0.975), norm_ppf(0.80)
    n_formula = 2.0 * p_bar * (1 - p_bar) * (z_a + z_b) ** 2 / delta ** 2
    print(f"80% 功效所需 n/臂:功效曲线解 = {n80},公式 n=2σ²(z_α+z_β)²/δ² = {n_formula:.0f}")
    return table, n80, n_formula


# ---------- 主流程 ----------
def main():
    geo = goodhart_geometry()
    ab = ab_sweep()
    table, n80, n_formula = power_curve()

    phis = [r["phi"] for r in ab]
    coss = [math.cos(r["phi"]) for r in ab]
    losses = [-r["true_lift"] for r in ab]          # 真目标损失=−提升
    corr = pearson(phis, losses)                    # φ vs 损失(单调但非线性)
    corr_cos = pearson(coss, [r["true_lift"] for r in ab])   # cosφ vs 提升(严格线性)

    print()
    print("读数:")
    print("  · Part 1:损失 L=1−cosφ 随错位角单调上升;φ>90° 后 cosφ<0——")
    print("    把代理指标优化到底,真目标反而为负。古德哈特/坎贝尔定律的几何形态:")
    print("    失真不在测量误差,在「指标方向」本身歪了。")
    print("  · Part 2:所有 φ 下代理指标都显著 +3pp(p 极小)——按代理看,新版全面获胜;")
    print(f"    但 φ=150° 时真目标提升 {ab[-2]['true_lift']*100:+.2f}pp(p={ab[-2]['true_p']:.4f})——")
    print("    同一批用户、同一次实验,代理判决『上线』、真目标判决『回滚』。")
    print("    A/B 测试只会检验你给它看的指标;选错指标,随机对照只会把错误钉得更牢。")
    print(f"  · Part 3:δ=2pp 的真实效应,80% 功效要每臂约 {n80} 人;")
    print("    n=1000 时功效不足三成——小样本管理实验『做不出显著』多半不是效应不存在,")
    print("    而是功效不够;反之大 n 下无关紧要的效应也会 p<0.05(统计显著≠管理显著)。")

    # ---------- 自验证断言 ----------
    # 几何:损失随 φ 严格单调上升;越过 90° 真目标为负
    for (pa, _, l1), (pb, _, l2) in zip(geo, geo[1:]):
        assert l2 > l1, "几何层损失应随错位角严格上升"
    assert all(c < 0 for ang, c, _ in geo if ang > math.pi / 2), \
        "φ>90° 时 cosφ<0(优化代理=损害真目标)"
    assert geo[-1][1] == -1.0, "完全错位(180°)时优化代理=最大化损害真目标"

    # A/B:代理指标全部显著为正;错位角与真目标损失强正相关(古德哈特主断言)
    assert all(r["proxy_lift"] > 0.02 and r["proxy_p"] < 0.05 for r in ab), \
        "优化代理应当稳定提升代理指标(古德哈特的前半句:指标确实会赢)"
    assert corr > 0.80, f"错位角与真目标损失应强正相关(实测 r={corr:.3f})"
    assert corr_cos > 0.93, \
        f"真目标提升应与 cosφ 近似线性(实测 r={corr_cos:.3f};期望斜率=δ_P)"
    # 头条对照:强错位下真目标显著为负;零错位下真目标随之受益
    loss_150 = -ab[4]["true_lift"]
    assert loss_150 > 0.015 and ab[4]["true_p"] < 0.05, \
        "强错位(150°)下优化代理应显著损害真目标"
    assert ab[0]["true_lift"] > 0.005, "零错位(0°)下真目标应随代理提升而受益"
    assert pearson(phis, [r["true_lift"] for r in ab]) < -0.80, \
        "错位角与真目标提升应强负相关"

    # 功效:单调;解析与经验吻合;80% 样本量与公式一致
    for (n1, p1, _), (n2, p2, _) in zip(table, table[1:]):
        assert n2 > n1 and p2 > p1, "功效应随样本量单调上升"
    assert all(abs(pw - ep) < 0.08 for _, pw, ep in table), \
        "经验功效应贴近解析功效曲线(蒙特卡洛容差 0.08)"
    assert abs(n80 - n_formula) / n_formula < 0.05, "二分解与功效公式应一致(5% 内)"
    assert n80 > 8000, "δ=2pp 的效应 80% 功效需要每臂近万人——小效应必须上规模"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
