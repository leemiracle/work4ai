# -*- coding: utf-8 -*-
"""
信任校准 × 信号检测论(教学版)
================================

家族实验 · 讲透工程心理学(GB/T 41045)
主题呼应走廊 C1/C2(04 章):信号检测论的判据工程 + Lee & See
(2004)信任动力学的最小仿真 + 依赖错配的成本地形。

模型一(SDT,等方差高斯版):
    噪声样本 ~ N(0,1);信号样本 ~ N(d′,1);判「有信号」当 X>c。
    命中率 H(c)=1−Φ(c−d′);虚警率 F(c)=1−Φ(c)。
    从四格恢复:d′=Z(H)−Z(F);相对判据 c_rel=−[Z(H)+Z(F)]/2。
    等先验、代价 (C_miss, C_fa) 下最优判据(对期望代价求导置零):
        c* = d′/2 + (1/d′)·ln(C_fa/C_miss)。

模型二(信任更新,指数平滑):
    每步表现分 r∈{0,1}(命中/正确拒斥=1;虚警/漏检=0),
    T ← T + α(r − T);稳态信任 ≈ E[r]=1−0.5·F−0.5·m。

模型三(依赖成本,自满耦合 U 形):
    依赖概率 D:采纳系统建议,系统错(概率 1−R)时靠「伴随
    监督」以 v0(1−D) 截获(依赖越多监督越松——自动化自满的
    参数化);手动概率 1−D:付核查成本 c_v,以 q 截获系统错误。
    C(D) = D·(1−R)·(1−v0(1−D))·C_f + (1−D)·[c_v+(1−R)(1−q)C_f]
    是关于 D 的开口向上抛物线,最优
        D*(R) = ( c_v/((1−R)C_f) + (1−q) − (1−v0) ) / (2·v0)
    随 R 单调右移(取边界时截断到 [0,1])。

三个实验(三律):
  [1] SDT 分离律:敏感度与判据是两个自由度——固定 d′ 移动
      判据,命中/虚警沿同一条 ROC 此消彼长;从 (H,F) 精确
      恢复 d′(判据搬家不改敏感度);漏检代价升高 → 最优判据
      左移(命中升、虚警也升,没有免费的命中)。
  [2] 信任动力学律(狼来了):两个系统漏检率相同(都 5%),
      高虚警系统(虚警率≈56%)稳态信任≈0.70,低虚警系统
      (≈9%)≈0.93——虚警拉低感知可靠性 → 依赖不足,即使
      漏检率相同;α 只改收敛速度与波动,不改稳态。
  [3] 依赖错配律:期望成本关于依赖倾向 D 呈 U 形(离散二阶
      差分恒正),最优 D* 随真实可靠性 R 右移(0.80→0.85→
      0.90 对应 D*≈0.20→0.40→0.80);过度信任与信任不足都
      单调变贵——信任校准=把 D 调到 R 对应的最优点。

只用标准库 math/random/statistics;固定随机种子,结果可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random
import statistics

N01 = statistics.NormalDist(0.0, 1.0)   # 标准正态:Φ 与 Z


def phi(x):
    """标准正态分布函数 Φ(x)。"""
    return N01.cdf(x)


def z(p):
    """标准正态分位数 Φ⁻¹(p)。"""
    return N01.inv_cdf(p)


def hit_rate(d_prime, c):
    """命中率 H=1−Φ(c−d′)(信号分布 N(d′,1),判据 c)。"""
    return 1.0 - phi(c - d_prime)


def fa_rate(c):
    """虚警率 F=1−Φ(c)(噪声分布 N(0,1),判据 c)。"""
    return 1.0 - phi(c)


def expected_cost_sdt(c, d_prime, c_miss, c_fa, p_signal=0.5):
    """SDT 期望代价:P(s)(1−H)C_miss + P(n)F·C_fa。"""
    return (p_signal * (1.0 - hit_rate(d_prime, c)) * c_miss
            + (1.0 - p_signal) * fa_rate(c) * c_fa)


def optimal_criterion(d_prime, c_miss, c_fa, p_signal=0.5):
    """等先验最优判据 c*=d′/2+(1/d′)ln(C_fa/C_miss);
    一般先验版 c*=d′/2+(1/d′)ln[P(n)C_fa/(P(s)C_miss)]。"""
    ratio = (1.0 - p_signal) * c_fa / (p_signal * c_miss)
    return d_prime / 2.0 + math.log(ratio) / d_prime


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """SDT 分离律:d′ 与 c 是两个自由度;代价驱动判据搬家。"""
    section("实验 [1] SDT 分离律:同一 d′ 下移动判据,沿 ROC 权衡")
    d_prime = 1.5

    # (a) 扫描判据:H 与 F 沿同一条 ROC 此消彼长
    print(f"(a) 固定 d′={d_prime:g},扫描判据 c(H/F 沿 ROC 双双下降):")
    print("    c      H       F      恢复d′=Z(H)−Z(F)")
    prev_h, prev_f, mono = None, None, True
    for c in [-1.0 + 0.25 * k for k in range(13)]:
        h, f = hit_rate(d_prime, c), fa_rate(c)
        d_rec = z(h) - z(f)                       # 从 (H,F) 恢复敏感度
        if prev_h is not None and (h >= prev_h - 1e-12 or f >= prev_f - 1e-12):
            mono = False
        print(f"  {c:+5.2f}  {h:.4f}  {f:.4f}    {d_rec:.6f}")
        assert abs(d_rec - d_prime) < 1e-9, "实验[1]:恢复 d′ 偏离真值"
        prev_h, prev_f = h, f
    assert mono, "实验[1]:H 与 F 未随判据单调下降"
    print("    判据左移→H 升 F 也升;右移→双降:同一条 ROC 上的搬家")

    # (b) 蒙特卡洛互证:固定判据,采样与解析一致
    shots, c_fixed = 200000, 0.0
    hit = fa = 0
    for _ in range(shots):                        # 信号流
        if random.gauss(d_prime, 1.0) > c_fixed:
            hit += 1
    for _ in range(shots):                        # 噪声流
        if random.gauss(0.0, 1.0) > c_fixed:
            fa += 1
    h_mc, f_mc = hit / shots, fa / shots
    h_an, f_an = hit_rate(d_prime, c_fixed), fa_rate(c_fixed)
    print(f"(b) MC({shots} 发,c={c_fixed:g}):H={h_mc:.4f}/{h_an:.4f}"
          f"(解析)  F={f_mc:.4f}/{f_an:.4f}(解析)")
    assert abs(h_mc - h_an) < 0.01 and abs(f_mc - f_an) < 0.01, \
        "实验[1]:MC 命中/虚警率偏离解析值"

    # (c) 代价驱动最优判据:漏检代价升高 → c* 左移(H、F 同升)
    print("(c) 等先验,C_fa=1,扫描漏检代价 C_miss:")
    print("  C_miss    c*(解析)   c*(网格)   H*      F*")
    grid = [(-3.0 + 6.0 * k / 2400) for k in range(2401)]
    rows, prev = [], None
    for c_miss in (1.0, 10.0, 100.0):
        c_star = optimal_criterion(d_prime, c_miss, 1.0)
        c_num = min(grid, key=lambda c: expected_cost_sdt(
            c, d_prime, c_miss, 1.0))
        h, f = hit_rate(d_prime, c_star), fa_rate(c_star)
        rows.append((c_miss, c_star, c_num, h, f))
        print(f"  {c_miss:6.1f}   {c_star:+7.4f}  {c_num:+7.4f}"
              f"  {h:.4f}  {f:.4f}")
        assert abs(c_num - c_star) < 0.01, "实验[1]:网格最优判据≠解析式"
        if prev is not None:
            assert c_star < prev[1] - 0.1, "实验[1]:漏检代价升,c* 未左移"
            assert h > prev[3] and f > prev[3 + 1], \
                "实验[1]:最优判据左移未带来命中与虚警双升"
        prev = rows[-1]
    print("断言通过:①同一 d′ 下 (H,F) 沿 ROC 权衡且恢复 d′ 不变 "
          "②网格最优=解析式 ③C_miss 升 10 倍/100 倍 → c* 单调左移、"
          "H* 与 F* 双升——敏感度与判据是两个自由度,改阈值是搬家,"
          "不是免费午餐")


# ----------------------------------------------------------------实验 2

def run_trust(d_prime, c, alpha, steps, t0=0.5, p_signal=0.5):
    """信任轨迹仿真:表现分 r(虚警按惩罚进账)→ T←T+α(r−T)。
    返回 (稳态均值, 尾段轨迹标准差, 实测漏检率, 实测虚警率,
    尾段 T<0.8 占比, 尾段样本列表)。"""
    t, tail = t0, []
    miss = fa = 0
    sig_n = noise_n = 0
    for _ in range(steps):
        if random.random() < p_signal:            # 信号事件
            sig_n += 1
            if random.gauss(d_prime, 1.0) > c:    # 命中
                r = 1.0
            else:                                 # 漏检(事后发现)
                miss += 1
                r = 0.0
        else:                                     # 噪声事件
            noise_n += 1
            if random.gauss(0.0, 1.0) > c:        # 虚警(狼来了)
                fa += 1
                r = 0.0
            else:                                 # 正确拒斥
                r = 1.0
        t += alpha * (r - t)
        tail.append(t)
    seg = tail[len(tail) // 4:]                   # 后 3/4 的后段另取
    seg = seg[len(seg) // 3:]                     # 丢掉收敛暂态
    below = sum(1.0 for x in seg if x < 0.8) / len(seg)
    return (statistics.fmean(seg), statistics.pstdev(seg),
            miss / sig_n, fa / noise_n, below, seg)


def experiment2():
    """信任动力学律(狼来了):虚警拉低感知可靠性,漏检率相同。"""
    section("实验 [2] 信任动力学:狼来了——虚警在信任账本上扣款")
    # 两个系统漏检率同为 5%:m=Φ(c−d′)=0.05 ⇒ c=d′+Z(0.05)
    miss_target = 0.05
    d_a, d_b = 1.5, 3.0
    c_a = d_a + z(miss_target)
    c_b = d_b + z(miss_target)
    alpha, steps = 0.05, 40000
    print(f"目标漏检率 {miss_target:.0%}(两系统相同);"
          f"α={alpha:g},步数 {steps},T0=0.5")
    print(f"  系统   d′    c      解析F    E[r]=1−0.5F−0.5m")
    setup = []
    for name, d, c in (("A 高虚警", d_a, c_a), ("B 低虚警", d_b, c_b)):
        f_an = fa_rate(c)
        e_r = 1.0 - 0.5 * f_an - 0.5 * miss_target
        setup.append((name, d, c, f_an, e_r))
        print(f"   {name}  {d:.1f}  {c:+.3f}  {f_an:.4f}     {e_r:.4f}")

    res = {}
    print("\n  系统   稳态T   |T−E[r]|  实测m   实测F    T<0.8占比")
    for name, d, c, f_an, e_r in setup:
        t_ss, t_sd, m, f, below, _ = run_trust(d, c, alpha, steps)
        res[name] = (t_ss, t_sd, m, f, below, e_r)
        print(f"   {name}  {t_ss:.4f}   {abs(t_ss - e_r):.4f}   "
              f"{m:.4f}  {f:.4f}    {below:.1%}")
        assert abs(t_ss - e_r) < 0.03, "实验[2]:稳态信任偏离感知可靠性"
    (t_a, _, m_a, f_a, below_a, e_a), (t_b, _, m_b, f_b, below_b, e_b) = \
        res["A 高虚警"], res["B 低虚警"]

    # (a) 漏检率相同(统计意义),信任差全部由虚警贡献
    assert abs(m_a - m_b) < 0.01 and abs(m_a - miss_target) < 0.01, \
        "实验[2]:两系统漏检率应相同且≈目标值"
    assert t_b - t_a > 0.15, "实验[2]:高虚警系统稳态信任未显著更低"
    print(f"\n(a) 漏检率 {m_a:.3f} vs {m_b:.3f}(相同);"
          f"虚警率 {f_a:.3f} vs {f_b:.3f}(差 6 倍)")
    print(f"    稳态信任 T_A={t_a:.3f} < T_B={t_b:.3f}"
          f"(差 {t_b - t_a:.3f})——虚警拉低感知可靠性→依赖不足")

    # (b) 依赖门槛:高虚警系统长期低于 0.8,低虚警系统长期高于
    assert below_a > 0.85 and below_b < 0.15, "实验[2]:依赖门槛占比异常"
    print(f"(b) T<0.8(依赖门槛)占比:A={below_a:.1%} vs B={below_b:.1%}"
          "——A 被弃用(disuse),B 被留在回路里")

    # (c) α 只改收敛速度与波动,不改稳态
    t_lo, sd_lo, *_ = run_trust(d_a, c_a, 0.05, steps)
    t_hi, sd_hi, *_ = run_trust(d_a, c_a, 0.50, steps)
    print(f"(c) α=0.05: T̄={t_lo:.4f}, σ={sd_lo:.4f};"
          f" α=0.50: T̄={t_hi:.4f}, σ={sd_hi:.4f}")
    assert abs(t_lo - t_hi) < 0.05 and abs(t_lo - e_a) < 0.03, \
        "实验[2]:稳态不应依赖 α"
    assert sd_hi > 2.0 * sd_lo, "实验[2]:大 α 应显著放大轨迹波动"
    print("断言通过:①漏检率相同而稳态信任差>0.15,差距全由虚警贡献 "
          "②高虚警系统长期低于依赖门槛 ③稳态≈E[r] 与 α 无关,"
          "α 升→波动升(灵敏-噪声权衡)——狼来了之后再准的系统也没人听")


# ----------------------------------------------------------------实验 3

C_F, C_V, Q, V0 = 100.0, 12.0, 0.9, 0.5   # 事故代价/核查成本/核查截获/监督上限


def dep_cost(D, R, c_f=C_F, c_v=C_V, q=Q, v0=V0):
    """依赖成本(解析):采纳分支+手动分支,自满耦合 v0(1−D)。"""
    adopt = D * (1.0 - R) * (1.0 - v0 * (1.0 - D)) * c_f
    manual = (1.0 - D) * (c_v + (1.0 - R) * (1.0 - q) * c_f)
    return adopt + manual


def dep_cost_optimal(R, c_f=C_F, c_v=C_V, q=Q, v0=V0):
    """最优依赖 D*(R)(解析,截断到 [0,1])。"""
    a = c_v / ((1.0 - R) * c_f) + (1.0 - q)
    d_star = (a - (1.0 - v0)) / (2.0 * v0)
    return min(1.0, max(0.0, d_star))


def dep_cost_mc(D, R, shots, c_f=C_F, c_v=C_V, q=Q, v0=V0):
    """依赖成本(蒙特卡洛):逐事件采系统对错/是否采纳/是否截获。"""
    total = 0.0
    for _ in range(shots):
        sys_ok = random.random() < R
        if random.random() < D:                  # 采纳系统建议
            if not sys_ok and random.random() >= v0 * (1.0 - D):
                total += c_f                      # 伴随监督没拦住
        else:                                    # 手动核查
            total += c_v
            if not sys_ok and random.random() >= q:
                total += c_f                      # 核查没拦住
    return total / shots


def experiment3():
    """依赖错配律:成本关于 D 呈 U 形,最优 D* 随 R 右移。"""
    section("实验 [3] 依赖错配:U 形成本与随 R 移动的最优点")
    print(f"参数:C_f={C_F:g}(漏检事故) c_v={C_V:g}(核查) "
          f"q={Q:g}(核查截获) v0={V0:g}(监督上限,自满耦合)\n")

    # (a) U 形:离散二阶差分恒正 + 网格最优=解析最优 + 两翼单调
    print("(a) 网格 D∈[0,1],三个可靠性水平:")
    print("   R     D*(解析)  D*(网格)  C(D*)   C(0)   C(1)   左翼  右翼")
    grid = [0.005 * k for k in range(201)]
    stars = []
    for R in (0.80, 0.85, 0.90):
        d_star = dep_cost_optimal(R)
        costs = [dep_cost(d, R) for d in grid]
        d_num = grid[costs.index(min(costs))]
        i_star = min(range(len(grid)), key=lambda i: abs(grid[i] - d_star))
        left_wing = all(costs[i] > costs[i + 1] + 1e-12
                        for i in range(0, i_star - 3))     # D* 左侧单调降
        right_wing = all(costs[i + 1] > costs[i] + 1e-12
                         for i in range(i_star + 3, len(grid) - 1))  # 右侧单调升
        second = all(costs[i + 1] + costs[i - 1] - 2.0 * costs[i] > 0.0
                     for i in range(1, len(grid) - 1))     # 离散凸
        assert second, f"实验[3]:R={R:g} 成本非凸(非 U 形)"
        assert left_wing and right_wing, \
            f"实验[3]:R={R:g} 两翼不单调(过度信任/信任不足未变贵)"
        assert abs(d_num - d_star) < 0.02, \
            f"实验[3]:R={R:g} 网格最优≠解析 D*"
        stars.append((R, d_star, dep_cost(d_star, R)))
        print(f"  {R:.2f}   {d_star:6.3f}   {d_num:6.3f}  "
              f"{dep_cost(d_star, R):6.2f} {costs[0]:6.2f} "
              f"{costs[-1]:6.2f}   单调降 单调升")

    # (b) D* 随 R 单调右移
    assert stars[0][1] < stars[1][1] < stars[2][1], \
        "实验[3]:最优依赖未随可靠性右移"
    print(f"\n(b) R: 0.80→0.85→0.90 对应 D*: "
          f"{stars[0][1]:.3f}→{stars[1][1]:.3f}→{stars[2][1]:.3f}"
          "——系统越可靠,最优依赖越高(右移)")

    # (c) 错配的账单:拿别的 R 校准的 D 用在当前 R 上
    print("(c) 错配账单(同为偏离最优 +0.60 的代价差):")
    for R, d_star, c_best in stars:
        for d_off, tag in ((d_star - 0.60, "信任不足"), (d_star + 0.60, "过度信任")):
            d_off = min(1.0, max(0.0, d_off))
            c_off = dep_cost(d_off, R)
            print(f"   R={R:.2f}: D={d_off:.2f}({tag})  成本 {c_off:6.2f}"
                  f"  vs 最优 {c_best:6.2f}(多付 {c_off - c_best:5.2f})")
            assert c_off > c_best, "实验[3]:错配应比校准更贵"

    # (d) 蒙特卡洛互证:解析期望成本 = 逐事件仿真均值
    R, D, shots = 0.85, 0.50, 200000
    c_an = dep_cost(D, R)
    c_mc = dep_cost_mc(D, R, shots)
    print(f"\n(d) MC({shots} 事件,R={R:g},D={D:g}):"
          f"成本 {c_mc:.4f} vs 解析 {c_an:.4f}")
    assert abs(c_mc - c_an) < 0.5, "实验[3]:MC 成本偏离解析式"
    print("断言通过:①成本关于 D 严格 U 形(离散二阶差分恒正) "
          "②网格最优=解析 D* 且两翼单调 ③D* 随 R 单调右移 "
          "④信任不足与过度信任都单调变贵 ⑤解析=蒙特卡洛——"
          "信任校准=把依赖倾向 D 调到真实可靠性 R 对应的最优点")


# ----------------------------------------------------------------主控

def main():
    print("信任校准×信号检测论(教学版)——讲透工程心理学家族实验")
    print("SDT 判据工程 + 信任更新动力学 + 依赖错配成本;纯标准库"
          "(math/random/statistics);固定种子,可复现")
    random.seed(20260908)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①SDT 分离律(敏感度与判据是两个自由度,"
          "漏检代价升→最优判据左移,命中升虚警也升) ②信任动力学律"
          "(漏检率相同,高虚警系统稳态信任显著更低——狼来了) "
          "③依赖错配律(成本关于 D 呈 U 形,最优 D* 随 R 右移,"
          "过度信任与信任不足都单调变贵)")
    print("=" * 64)


if __name__ == "__main__":
    main()
