# -*- coding: utf-8 -*-
"""双边市场网络效应模拟:读者×广告主交叉外部性、临界规模与赢者通吃。

00-体系结构.md(美之时刻 2 / 反直觉 1:发行亏损是设计)与 03-可构造与结构.md
(双轮映射 / 临界质量 / 补贴设计)的配套实验。纯标准库,且全程**无随机数**——
确定性动力系统,每次运行结果相同,断言可复现。

模型(与 03 章 §二/§三严格同构):
  读者最优反应   N_R = F_R · clip01((q0 − p_R + α·N_A)/θmax_R)   ← 广告收入反哺内容
  广告主最优反应 N_A = F_A · clip01((r·N_R − p_A)/θmax_A)         ← 读者规模即触达
  α = 「反哺−骚扰」的净外部性:α>0 双轮正转(广告黄金年代),α<0 死亡螺旋
  动态:两侧按惯性 λ 部分调整(广告合同粘滞/读者习惯),叠代至收敛

默认参数的解析不动点(clip 未激活区解线性方程):
  冷寂均衡 (N_A, N_R) = (0, 100)        —— 无广告→低质→少读者→无广告
  起飞均衡 (N_A, N_R) = (200, 1000)     —— 满广告→高质→满读者
  不稳定不动点(分水岭) N_A* ≈ 21.43, N_R* ≈ 292.86 —— 多稳态的盆域边界

四组实验:
  1) 冷启动坍塌:零广告主 → 冷寂均衡(单边内容再好也救不了双边冷启动)
  2) 临界规模扫描:种子 0..40,定位「21 崩 / 22 起」的分水岭,与解析不动点对照
  3) 补贴设计:p_R 2.0→0.2(低于成本的发行价)抹平分水岭,冷启动直接起飞
     —— 00 章「发行亏损是设计而非失败」的数学实拍
  4) 赢者通吃:两平台同参数,广告主种子 30 vs 25 的微小先发优势 → 一家通吃

跑法: python3 -u experiments/00_two_sided.py
"""

# ---- 结构参数(改动这里=做 03 章 §六的敏感性练习) ----
F_R, THETA_R = 1000.0, 10.0    # 读者市场容量 / 参与门槛上限(受众异质,θ~U[0,10])
F_A, THETA_A = 200.0, 8.0      # 广告主市场容量 / 门槛上限(θ~U[0,8])
Q0, P_R = 3.0, 2.0             # 内容基础价值 / 发行价(补贴设计的旋钮)
ALPHA = 0.09                   # 读者从每个广告主处的净外部性(收入反哺−广告骚扰)
R_AD, P_A = 0.02, 5.0          # 每个读者给广告主的价值 / 广告刊例价
LAM = 0.3                      # 两侧调整惯性(0=瞬时最优反应,1=完全不动)


def clip01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def readers_resp(n_a, p_r=P_R):
    """读者侧最优反应:异质门槛 θ~U[0,θmax_R] 的群体中,U_R≥θ 者参与的比例。"""
    return F_R * clip01((Q0 - p_r + ALPHA * n_a) / THETA_R)


def adv_resp(n_r):
    """广告主侧最优反应:利润 r·N_R−p_A ≥ θ(~U[0,θmax_A]) 者参与的比例。"""
    return F_A * clip01((R_AD * n_r - P_A) / THETA_A)


def evolve(n_a0, n_r0, p_r=P_R, max_periods=3000, tol=5e-4, patience=10):
    """惯性部分调整的叠代动力学。返回 (N_A 终值, N_R 终值, 收敛轮数)。"""
    n_a, n_r = float(n_a0), float(n_r0)
    calm = 0
    for t in range(1, max_periods + 1):
        d_a = LAM * (adv_resp(n_r) - n_a)          # 两侧同步更新(用旧值)
        d_r = LAM * (readers_resp(n_a, p_r) - n_r)
        n_a, n_r = n_a + d_a, n_r + d_r
        calm = calm + 1 if max(abs(d_a), abs(d_r)) < tol else 0
        if calm >= patience:
            return n_a, n_r, t
    return n_a, n_r, max_periods


def analytic_interior(p_r=P_R):
    """联立两条反应曲线解内部不动点(分水岭);clip 未激活区内是线性方程组。"""
    coef = 1.0 - (F_A * R_AD * F_R * ALPHA) / (THETA_A * THETA_R)
    rhs = F_A * (R_AD * F_R * (Q0 - p_r) / THETA_R - P_A) / THETA_A
    n_a = rhs / coef
    n_r = F_R * (Q0 - p_r + ALPHA * n_a) / THETA_R
    return n_a, n_r


def tri_survival(gap, span):
    """P(ξ1−ξ2 > −gap),ξk~U[−span,span] 独立同分布,差服从对称三角分布。"""
    b = 2.0 * span                                   # 三角分布支集 [−b, b]
    x = -gap
    if x <= -b:
        return 1.0
    if x >= b:
        return 0.0
    if x <= 0.0:
        return 1.0 - (x + b) ** 2 / (2.0 * b * b)
    return (b - x) ** 2 / (2.0 * b * b)


def winner_take_all(seed_a1=30.0, seed_a2=25.0, span=1.5, max_periods=3000):
    """两平台竞争:读者按「效用+品牌偏好」单归属;广告主单归属到读者更多的一家。

    span=品牌偏好强度:偏好差 span 的两倍决定效用差距多大才能通吃全部读者。
    """
    n_a1, n_a2 = seed_a1, seed_a2
    calm = 0
    t = 0
    for t in range(1, max_periods + 1):
        u1 = Q0 - P_R + ALPHA * n_a1
        u2 = Q0 - P_R + ALPHA * n_a2
        share1 = tri_survival(u1 - u2, span)         # 读者单归属分蛋糕
        n_r1, n_r2 = F_R * share1, F_R * (1.0 - share1)
        t1 = adv_resp(n_r1) if n_r1 >= n_r2 else 0.0  # 广告主跟读者走
        t2 = adv_resp(n_r2) if n_r2 > n_r1 else 0.0
        d1 = LAM * (t1 - n_a1)
        d2 = LAM * (t2 - n_a2)
        n_a1, n_a2 = n_a1 + d1, n_a2 + d2
        calm = calm + 1 if max(abs(d1), abs(d2)) < 5e-4 else 0
        if calm >= 10:
            break
    u1 = Q0 - P_R + ALPHA * n_a1
    u2 = Q0 - P_R + ALPHA * n_a2
    share1 = tri_survival(u1 - u2, span)
    return n_a1, n_a2, F_R * share1, F_R * (1.0 - share1), t


def main():
    print("=" * 78)
    print("双边市场网络效应:读者×广告主的交叉外部性(确定性动力系统,无随机数)")
    print("=" * 78)
    print(f"参数: F_R={F_R:.0f} F_A={F_A:.0f} q0={Q0} p_R={P_R} α={ALPHA} "
          f"r={R_AD} p_A={P_A} 惯性λ={LAM}")
    na_star, nr_star = analytic_interior()
    print(f"解析分水岭(不稳定不动点): N_A* = {na_star:.2f}, N_R* = {nr_star:.2f}")
    print(f"解析稳定均衡: 冷寂 (0, {readers_resp(0):.0f}) / 起飞 ({adv_resp(F_R):.0f}, {F_R:.0f})")
    print()

    # ---- 实验 1:冷启动坍塌 ----
    n_a, n_r, t = evolve(0.0, readers_resp(0.0))
    print(f"[1] 冷启动(零广告主种子) → ({n_a:.1f}, {n_r:.1f}),{t} 轮收敛")
    assert n_a <= 0.5 and 95.0 <= n_r <= 105.0, "冷启动应坍塌到冷寂均衡 (0, 100)"

    # ---- 实验 2:临界规模扫描 ----
    print()
    print("[2] 临界规模扫描(种子=初始广告主数,读者随之响应)")
    print(f"{'种子':>4} {'N_R初':>7} {'N_A终':>8} {'N_R终':>8}  结局")
    results = []
    tipping = None
    for seed in range(0, 41):
        n_a_f, n_r_f, _ = evolve(float(seed), readers_resp(float(seed)))
        results.append((seed, n_a_f, n_r_f))
        if n_a_f >= F_A - 1.0 and tipping is None:
            tipping = seed
    shown = {0, 5, 10, 15, 18, 20, 21, 22, 25, 30, 40}
    for seed, n_a_f, n_r_f in results:
        verdict = "起飞" if n_a_f >= F_A - 1.0 else "坍塌"
        mark = "  ← 分水岭" if tipping is not None and seed == tipping else ""
        if seed in shown:
            n_r0 = readers_resp(float(seed))
            print(f"{seed:>4} {n_r0:>7.0f} {n_a_f:>8.1f} {n_r_f:>8.1f}  {verdict}{mark}")
    assert tipping is not None, "扫描中应存在起飞种子"
    assert 15 <= tipping <= 30, f"分水岭应在解析值附近,实测 {tipping}"
    s_prev, na_prev, _ = results[tipping - 1]
    assert na_prev <= 1.0, f"分水岭前一粒种子应坍塌(种子{tipping-1} 终值 {na_prev:.1f})"
    na_tip, nr_tip = results[tipping][1], results[tipping][2]
    assert na_tip >= F_A - 1.0 and nr_tip >= F_R - 5.0, "分水岭种子应起飞到满员"
    print(f"  ✓ 分水岭落在种子 {tipping - 1}→{tipping} 之间;"
          f"解析不稳定不动点 N_A*={na_star:.2f} → 预测最小起飞种子={na_star:.0f}+1"
          f"(≈{na_star + 1:.0f})——模拟与解析咬合")
    print("  ✓ 种子差 1,终态差约 900 读者:多稳态下边际分析在分水岭附近全部失效(03 章)")

    # ---- 实验 3:补贴设计(发行亏损是设计) ----
    print()
    p_sub = 0.2                                        # 低于成本的发行价=广告侧补贴
    n_a0, n_r0 = 0.0, readers_resp(0.0, p_r=p_sub)
    n_a_s, n_r_s, _ = evolve(n_a0, n_r0, p_r=p_sub)
    na_sub_star, _ = analytic_interior(p_r=p_sub)
    print(f"[3] 补贴设计:p_R {P_R}→{p_sub}(低于成本),同样零广告主冷启动")
    print(f"    未补贴冷启动 → ({n_a:.1f}, {n_r:.1f})   [坍塌]")
    print(f"    补贴后冷启动 → ({n_a_s:.1f}, {n_r_s:.1f})   [起飞]")
    print(f"    解析:补贴后内部不动点 N_A* = {na_sub_star:.1f}(<0,即分水岭被抹平——")
    print("           冷寂均衡不再存在,唯一吸引子是满员)")
    assert n_a_s >= F_A - 1.0 and n_r_s >= F_R - 5.0, "补贴后冷启动应起飞"
    assert na_sub_star < 0.0, "补贴后内部不动点应为负(盆域边界消失)"

    # ---- 实验 4:赢者通吃 ----
    print()
    n_a1, n_a2, n_r1, n_r2, t = winner_take_all()
    share1 = n_r1 / (n_r1 + n_r2)
    print("[4] 赢者通吃:两平台同参数,品牌偏好 ±1.5;广告主种子 30 vs 25(先发优势 20%)")
    print(f"    终态: 平台1 (N_A={n_a1:.1f}, N_R={n_r1:.0f})  "
          f"平台2 (N_A={n_a2:.1f}, N_R={n_r2:.0f})  读者份额 {share1:.1%} : {1 - share1:.1%}")
    assert n_r2 <= 10.0 and share1 >= 0.99, "读者应几乎全部流向头部平台"
    assert n_a2 <= 0.5, "输家平台的广告主应全部撤出"
    assert n_a1 >= F_A - 1.0, "赢家平台广告主应满员"
    print("  ✓ 20% 的种子优势 → 100% 的终态份额:交叉外部性把微弱先发优势放大成垄断")

    print()
    print("读数:")
    print("  · [1][2] 双边市场有两个稳定世界(冷寂/起飞),历史由初值选择——")
    print("    平台「先烧钱后盈利」的结构本质:烧钱=把系统推过分水岭(03 章 §三)")
    print("  · [3] 低于成本的发行价不是促销,是移动分水岭的市场设计——")
    print("    广告模式的「发行亏损」同理:用广告侧利润补贴发行侧规模(00 章反直觉 1)")
    print("  · [4] 赢者通吃是多稳态+读者单归属的合谋;品牌偏好(±1.5)只能延缓、")
    print("    不能阻止头部通吃——差异化要强到把外部性回环增益压到 1 以下才可能共存")
    print()
    print("✓ 自验证通过:冷启动坍塌 / 分水岭位置与解析不动点咬合 / 补贴抹平盆域边界 / 赢者通吃")


if __name__ == "__main__":
    main()
