# -*- coding: utf-8 -*-
"""匹配·搜索·保险三律:Beveridge 曲线的两种失业 / 保留工资与失业保险的双面账 /
工伤保险的经验费率与安全激励。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(匹配引擎与池化引擎的
严格可构造性)、04-劳动科学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics/bisect),无第三方依赖。

三律:
  律一 Beveridge 曲线的两种失业(搜寻匹配的最小模型,DMP 传统):
      劳动力规模归一,就业者每期以分离率 s 离职(外生);失业者与空位以
      匹配函数 M=A·√(U·V) 相遇(随机搜索,A 为匹配效率),找到即就业。
      稳态:s·(1−U)=A·√(U·V)。
      断言:①需求冲击(空位 V 变动)使稳态 (U,V) 沿一条向右下倾斜的曲线
      移动——U 与 V 负相关(周期性失业的几何:Beveridge 曲线);②匹配
      效率 A 下降使曲线整体外移(同一 V 下 U 更高;把 U 压回原位需要更多
      空位;存在 U、V 双高的稳态点)——结构性失业与周期性失业在 UV 平面
      上是「沿曲线移动 vs 曲线本身移动」的分离。
  律二 保留工资与失业保险的双面账(McCall 搜索模型):
      失业者每期抽一个对数正态工资报价,接受 iff w≥保留工资 w*,接受后
      工资终身不变;w* 由动态规划固定点给出(失业金 b 越高,等待的期权
      价值越高,w* 越高)。
      断言:①b↑ 拒绝更多报价,平均失业期拉长;②但接受后的工资更高
      (匹配质量改善)——两笔账同时打印:多领的失业金与多搜的月份
      (成本面),换来的工资增益(收益面)。失业保险不是免费午餐,
      也不是洪水猛兽,是一笔显式换购。
  律三 工伤保险的经验费率与安全激励(风险池的定价几何):
      企业风险异质(基础事故率 p 分高低两组),可选安全投资(每级把
      事故率乘以 0.75,每级每期成本固定);两制度对照:
      统一费率(全员按池均定价,与自身风险无关)vs 经验费率
      (费率=α·池均+(1−α)·自身近 3 期实发索赔率,α=0.3)。
      断言:统一费率下安全投资的边际收益只剩未保险残余(δ=10%),
      高风险企业投资显著更低(被池均补贴→搭便车);经验费率把
      (1−α)=70% 的自身风险内化进价格,恢复按风险分化的投资,
      池子整体事故率随之下降——保费怎么定价,安全就怎么被投资。

跑法: python3 -u experiments/matching_search_insurance.py
"""

import bisect
import math
import random
import statistics

# ==================== 律一:Beveridge 曲线的两种失业 ====================

SEP_RATE = 0.02   # 岗位分离率 s(月度,外生:裁员/倒闭/离职的总流量)
A_BASE = 0.50     # 基准匹配效率 A
A_LOW = 0.36      # 匹配效率下降(结构性冲击;0.36/0.50=0.72,降 28%)
V_GRID = [0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.045, 0.050]


def steady_u_analytic(a, v, s=SEP_RATE):
    """稳态失业率解析解:s²(1−U)²=A²·U·V ⇔ U²−(2+c)U+1=0,c=A²V/s²(取小根)。"""
    c = a * a * v / (s * s)
    b = 2.0 + c
    disc = math.sqrt(b * b - 4.0)
    return (b - disc) / 2.0


def steady_u_sim(a, v, u0=0.08, periods=20000, s=SEP_RATE):
    """仿真到稳态:U ← U + s(1−U) − min(A√(U·V), U)。

    每期流入 s(1−U)(分离),流出 A√(U·V)(匹配成功,不超过失业存量)。
    """
    u = u0
    for _ in range(periods):
        flow_out = min(a * math.sqrt(u * v), u)
        u_new = u + s * (1.0 - u) - flow_out
        if abs(u_new - u) < 1e-13:
            return u_new
        u = u_new
    return u


def pearson(xs, ys):
    """Pearson 相关系数(线性相关;Beveridge 曲线凸,取 -0.85 为界)。"""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy)


def spearman(xs, ys):
    """Spearman 秩相关(单调相关;严格单调递减时恰为 −1)。"""
    def ranks(vs):
        order = sorted(range(len(vs)), key=lambda i: vs[i])
        rk = [0.0] * len(vs)
        for pos, i in enumerate(order):
            rk[i] = float(pos)
        return rk
    return pearson(ranks(xs), ranks(ys))


def act1():
    print("=" * 84)
    print("律一 Beveridge 曲线的两种失业(匹配函数 M=A·√(U·V),分离率 s=%.2f)" % SEP_RATE)
    print("=" * 84)
    print("\n需求冲击=空位 V 变动(雇主招聘意愿);结构冲击=匹配效率 A 变动(搜索与甄选的效率)")
    print(f"{'V(空位率)':>9} {'U*(A=0.50)':>10} {'U*(A=0.36)':>10} "
          f"{'紧度θ=V/U':>9} {'找到率f':>7}  读数")
    u_hi, u_lo = [], []
    for v in V_GRID:
        u1 = steady_u_sim(A_BASE, v)
        u2 = steady_u_sim(A_LOW, v)
        u_hi.append(u1)
        u_lo.append(u2)
        # 解析对表(数学复核)
        assert abs(u1 - steady_u_analytic(A_BASE, v)) < 1e-9
        assert abs(u2 - steady_u_analytic(A_LOW, v)) < 1e-9
        theta = v / u1
        f = SEP_RATE * (1 - u1) / u1
        print(f"{v:>9.3f} {u1:>10.4f} {u2:>10.4f} {theta:>9.2f} {f:>7.3f}"
              "  同一 V,低效率下失业更高")
    print("\n读数:")
    print("  · 同一条曲线内(A 不变):V 越高 U 越低——稳态点沿一条向右下倾斜的")
    print("    曲线移动,这就是 Beveridge 曲线(周期性失业的几何:需求冲击=沿曲线移动);")
    print("  · A 从 0.50 降到 0.36(结构冲击):每一个 V 上的 U 都变高——曲线整体")
    print("    外移,不是沿着旧曲线走。")

    # 沿曲线换挡:同一 A 下需求冲击的过渡路径
    print("\n过渡路径(A=0.50 不变,从繁荣 V=0.045 切到衰退 V=0.015,再切回):")
    path = [(0, None)]
    u = 0.06
    marks = {}
    for month in range(1, 121):
        v_now = 0.015 if 1 <= month <= 60 else 0.045
        flow_out = min(A_BASE * math.sqrt(u * v_now), u)
        u = u + SEP_RATE * (1.0 - u) - flow_out
        if month in (12, 60, 72, 120):
            marks[month] = (v_now, u)
    for month, (v_now, u) in sorted(marks.items()):
        tag = "衰退期(空位收缩)" if month <= 60 else "繁荣期(空位扩张)"
        print(f"  第 {month:>3} 个月:V={v_now:.3f},U={u:.4f}  {tag}")
    print("  · 同一条曲线上换挡:空位收缩→失业爬升;空位扩张→失业回落——纯周期性")

    # 断言 1:曲线向右下倾斜(每个 A 内 U 随 V 单调下降,相关系数强负)
    assert all(a2 > b2 for a2, b2 in zip(u_hi, u_hi[1:])), "A=0.50 内 U 应随 V 单调下降"
    assert all(a2 > b2 for a2, b2 in zip(u_lo, u_lo[1:])), "A=0.36 内 U 应随 V 单调下降"
    r1 = pearson(V_GRID, u_hi)
    rho1 = spearman(V_GRID, u_hi)
    assert r1 < -0.85, f"U 与 V 应强负相关(线性),实测 r={r1:.4f}"
    assert abs(rho1 + 1.0) < 1e-12, f"U(V) 应严格单调递减,实测 ρ={rho1:.4f}"

    # 断言 2:效率下降→曲线外移(每个 V 上 U 更高);恢复同 U 需要更多空位;
    #         存在 U、V 双高的稳态点(结构性失业与空位并存)
    assert all(u2 > u1 for u1, u2 in zip(u_hi, u_lo)), "效率下降后每个 V 上 U 都应更高"
    v0 = 0.035
    u0_star = steady_u_analytic(A_BASE, v0)
    v_restore = SEP_RATE ** 2 * (1 - u0_star) ** 2 / (A_LOW ** 2 * u0_star)  # 由稳态式反解
    assert abs(steady_u_analytic(A_LOW, v_restore) - u0_star) < 1e-9
    # 双高点:低效率曲线上的 (U,V) 可以两点都高于基准稳态
    u_double = steady_u_analytic(A_LOW, 0.045)
    assert u_double > u0_star and 0.045 > v0
    print(f"\n结构性读数:基准稳态 (U={u0_star:.4f}, V={v0:.3f});A 降到 {A_LOW} 后——")
    print(f"  · 同一 V={v0:.3f} 上,U 升到 {steady_u_analytic(A_LOW, v0):.4f}(+"
          f"{100*(steady_u_analytic(A_LOW, v0)/u0_star-1):.0f}%);")
    print(f"  · 要把 U 压回 {u0_star:.4f},V 必须升到 {v_restore:.3f}(空位多投 "
          f"{100*(v_restore/v0-1):.0f}%);")
    print(f"  · 低效率曲线上存在双高点 (U={u_double:.4f}, V=0.045)——失业与空位双高并存。")
    print(f"\n✓ 律一断言通过:两条曲线内 U(V) 均严格单调下降(Spearman ρ={rho1:.1f},"
          f"线性 r={r1:.3f};Beveridge 曲线向右下倾斜);A 下降使曲线整体外移,"
          f"恢复同 U 需多投 {100*(v_restore/v0-1):.0f}% 空位"
          "——周期性失业=沿曲线移动,结构性失业=曲线本身移动")

# ==================== 律二:保留工资与失业保险的双面账 ====================

MU_W, SIGMA_W = 0.0, 0.6   # 工资报价:对数正态(中位数 1.0,右尾偏斜)
BETA = 0.90                # 月度贴现因子
K_GRID = 4001              # 报价网格点数(等权离散化)
B_LOW, B_HIGH = 0.4, 1.0   # 两档失业金(相对工资中位数的比例)
N_SPELLS = 20000           # 每档模拟的失业期数

_ND = statistics.NormalDist(0.0, 1.0)
_W = sorted(math.exp(MU_W + SIGMA_W * _ND.inv_cdf((k + 0.5) / K_GRID))
            for k in range(K_GRID))
_SUFFIX = [0.0] * (K_GRID + 1)          # 后缀和:S(w*)=Σ_{w≥w*} w·p
for _i in range(K_GRID - 1, -1, -1):
    _SUFFIX[_i] = _SUFFIX[_i + 1] + _W[_i]


def _tail(wstar):
    """返回 (S(w*), F(w*)):报价分布的尾部均值积分与左尾概率。"""
    i = bisect.bisect_left(_W, wstar)
    return _SUFFIX[i] / K_GRID, i / K_GRID


def reservation_wage(b):
    """McCall 固定点:w*=(1−β)·V_U;V_U·(1−βF)=b+(β/(1−β))·S(w*)。"""
    wstar = b
    for _ in range(5000):
        s_tail, f_mass = _tail(wstar)
        v_u = (b + BETA / (1.0 - BETA) * s_tail) / (1.0 - BETA * f_mass)
        new = (1.0 - BETA) * v_u
        if abs(new - wstar) < 1e-13:
            return new
        wstar = new
    return wstar


def simulate_search(wstar, seed):
    """模拟失业期:每期抽报价,接受 iff w≥w*;返回(各期长度, 各接受工资)。"""
    rng = random.Random(seed)
    spells, wages = [], []
    for _ in range(N_SPELLS):
        length = 0
        while True:
            length += 1
            w = math.exp(MU_W + SIGMA_W * rng.gauss(0.0, 1.0))
            if w >= wstar:
                spells.append(length)
                wages.append(w)
                break
    return spells, wages


def act2():
    print("\n" + "=" * 84)
    print("律二 保留工资与失业保险的双面账(McCall 搜索:报价对数正态,β=%.2f)" % BETA)
    print("=" * 84)
    rows = {}
    for label, b in (("低金 b=0.4", B_LOW), ("高金 b=1.0", B_HIGH)):
        wstar = reservation_wage(b)
        s_tail, f_mass = _tail(wstar)
        p_acc = 1.0 - f_mass
        rows[label] = {
            "b": b, "wstar": wstar, "p_acc": p_acc,
            "spell_th": 1.0 / p_acc, "wage_th": s_tail / p_acc,
        }
    seed_off = {"低金 b=0.4": 840741, "高金 b=1.0": 840742}
    for label, row in rows.items():
        spells, wages = simulate_search(row["wstar"], seed_off[label])
        row["spell_sim"] = statistics.mean(spells)
        row["wage_sim"] = statistics.mean(wages)
        row["rej_rate"] = 1.0 - row["p_acc"]

    print(f"\n{'档位':>10} {'保留工资w*':>9} {'拒绝率':>7} {'失业期(仿真)':>9}"
          f" {'失业期(理论)':>9} {'接受工资(仿真)':>10} {'(理论)':>7}")
    for label, r in rows.items():
        print(f"{label:>10} {r['wstar']:>9.4f} {r['rej_rate']:>7.1%}"
              f"{r['spell_sim']:>10.2f} {r['spell_th']:>11.2f}"
              f"{r['wage_sim']:>12.4f} {r['wage_th']:>9.4f}")

    lo = rows["低金 b=0.4"]
    hi = rows["高金 b=1.0"]
    d_spell = hi["spell_sim"] - lo["spell_sim"]
    d_ui = hi["b"] * hi["spell_sim"] - lo["b"] * lo["spell_sim"]
    d_wage = hi["wage_sim"] - lo["wage_sim"]
    print(f"\n两笔账(b 从 {B_LOW} 提到 {B_HIGH}):")
    print(f"  成本面:平均失业期 {lo['spell_sim']:.2f} → {hi['spell_sim']:.2f} 个月"
          f"(+{d_spell:.2f});")
    print(f"          每段失业保险基金多付 {d_ui:.2f} 个月失业金;")
    print(f"  收益面:接受工资 {lo['wage_sim']:.4f} → {hi['wage_sim']:.4f}"
          f"(+{100*d_wage/lo['wage_sim']:.1f}%,匹配质量改善,且终身高薪);")
    print(f"  换购率:每多搜 1 个月,接受工资 +{d_wage/d_spell:.3f}"
          f"(≈+{100*d_wage/lo['wage_sim']/d_spell:.1f}%)——")
    print("  失业保险不是免费午餐(失业期变长),也不是洪水猛兽(匹配变好),")
    print("  是一笔显式换购:用更长的搜索时间与基金支出,买更高的匹配质量。")

    # 断言:①b↑ 抬高保留工资与失业期;②接受工资更高;③仿真贴理论
    assert hi["wstar"] > lo["wstar"] + 0.1, "高金应显著抬高保留工资"
    assert hi["spell_sim"] > 1.15 * lo["spell_sim"], \
        f"高金应拉长失业期:实测 {hi['spell_sim']:.2f} vs {lo['spell_sim']:.2f}"
    assert hi["wage_sim"] > 1.01 * lo["wage_sim"], \
        f"高金应提高接受工资:实测 {hi['wage_sim']:.4f} vs {lo['wage_sim']:.4f}"
    for label, r in rows.items():
        assert abs(r["spell_sim"] / r["spell_th"] - 1.0) < 0.08, \
            f"{label} 失业期仿真应贴理论:{r['spell_sim']:.2f} vs {r['spell_th']:.2f}"
        assert abs(r["wage_sim"] / r["wage_th"] - 1.0) < 0.03, \
            f"{label} 接受工资仿真应贴理论:{r['wage_sim']:.4f} vs {r['wage_th']:.4f}"
    print(f"\n✓ 律二断言通过:w* {lo['wstar']:.3f}→{hi['wstar']:.3f};失业期 "
          f"{lo['spell_sim']:.2f}→{hi['spell_sim']:.2f} 个月(+{d_spell:.2f});"
          f"接受工资 +{100*d_wage/lo['wage_sim']:.1f}%——双面账成立,"
          "保险=显式换购")

# ==================== 律三:工伤保险的经验费率与安全激励 ====================

N_FIRMS, N_HIGH, N_LOW = 60, 30, 30
P_HIGH_RANGE, P_LOW_RANGE = (0.06, 0.10), (0.01, 0.03)   # 基础事故率区间
LOAD_FACTOR = 0.75        # 每级安全投资把事故率乘以 0.75(至多 3 级)
MAX_LEVELS = 3
C_LEVEL = 45.0            # 每级每期安全成本(防护/培训/检修的年化支出)
L_CLAIM = 100.0           # 每起工伤的赔付额(单位化)
N_EXP = 50                # 每期每企业的独立风险敞口数(伯努利试验数)
DELTA = 0.10              # 未保险残余的内化份额(停工/换人/罚款,δ=10%)
ALPHA = 0.30              # 经验费率的池化权重(自身经验可信度 1−α=70%)
W_WINDOW = 3              # 费率回看的期数(月)
T_PERIODS = 24            # 总期数
MEASURE_FROM = 12         # 从第 12 期起量测(跳过预热)


def make_firms(seed):
    """生成风险异质的企业:高低两组各半,组内事故率均匀分布。"""
    rng = random.Random(seed)
    firms = []
    for idx in range(N_FIRMS):
        if idx < N_HIGH:
            p = P_HIGH_RANGE[0] + (P_HIGH_RANGE[1] - P_HIGH_RANGE[0]) * rng.random()
            grp = "高"
        else:
            p = P_LOW_RANGE[0] + (P_LOW_RANGE[1] - P_LOW_RANGE[0]) * rng.random()
            grp = "低"
        firms.append({"p": p, "grp": grp, "s": 0, "hist": []})
    return firms


def p_eff(f):
    return f["p"] * LOAD_FACTOR ** f["s"]


def choose_investment(f, regime, pool_rate):
    """企业近视优化:选 s 最小化 期望保费 + δ·未保险残余 + c·s。

    保费按敞口计价(每期 N_EXP 个风险敞口,费率×敞口×赔付额);
    统一费率=池均定价(与 s 无关);经验费率把 (1−α) 的自身费率内化
    进价格(企业知道自己的工艺,以真实 p(s) 预期;噪声体现在实发
    索赔驱动的费率结算里)。
    """
    best_s, best_cost = 0, None
    for s in range(MAX_LEVELS + 1):
        pe = f["p"] * LOAD_FACTOR ** s
        rate = pool_rate if regime == "uniform" \
            else ALPHA * pool_rate + (1 - ALPHA) * pe
        cost = N_EXP * L_CLAIM * (rate + DELTA * pe) + C_LEVEL * s
        if best_cost is None or cost < best_cost - 1e-12:
            best_s, best_cost = s, cost
    return best_s


def run_regime(regime, seed):
    """跑 T 期:每期企业先按制度定投资,再实发索赔,费率按近 W 期滚动。"""
    rng = random.Random(seed)
    firms = make_firms(840740)
    p_bar_base = statistics.mean(f["p"] for f in firms)
    premium_paid = {f_id: 0.0 for f_id in range(N_FIRMS)}
    claims_cost = {f_id: 0.0 for f_id in range(N_FIRMS)}
    pool_claims, pool_exp = [], []   # 池子滚动历史(算 p̂_pool)
    fund = 0.0
    for t in range(1, T_PERIODS + 1):
        pool_rate_now = (sum(pool_claims) / sum(pool_exp)
                         if len(pool_claims) >= W_WINDOW else p_bar_base)
        for f_id, f in enumerate(firms):
            # 1) 定投资(近视优化)
            f["s"] = choose_investment(f, regime, pool_rate_now)
            pe = p_eff(f)
            # 2) 实发索赔(每敞口伯努利)
            claims = sum(1 for _ in range(N_EXP) if rng.random() < pe)
            # 3) 费率结算(按敞口):统一=池均基价;经验=α·池均滚动+0.7·自身滚动
            own_hist_claims = sum(c for c, _ in f["hist"][-W_WINDOW:])
            own_hist_exp = sum(e for _, e in f["hist"][-W_WINDOW:])
            own_rate = (own_hist_claims / own_hist_exp
                        if own_hist_exp > 0 else pe)
            if regime == "uniform":
                rate = p_bar_base
            else:
                rate = ALPHA * pool_rate_now + (1 - ALPHA) * own_rate
            prem = N_EXP * L_CLAIM * rate
            premium_paid[f_id] += prem
            claims_cost[f_id] += L_CLAIM * claims
            fund += prem - L_CLAIM * claims
            f["hist"].append((claims, N_EXP))
        pool_claims.append(sum(c for c, _ in
                               (f["hist"][-1] for f in firms)))
        pool_exp.append(N_FIRMS * N_EXP)
    return firms, premium_paid, claims_cost, fund


def act3():
    print("\n" + "=" * 84)
    print("律三 工伤保险的经验费率与安全激励(%d 家企业,高/低风险各 %d,安全投资每级事故率×%.2f)"
          % (N_FIRMS, N_HIGH, LOAD_FACTOR))
    print("=" * 84)
    results = {}
    for regime, seed, name in (("uniform", 840743, "统一费率(全员池均定价)"),
                               ("exp", 840744, "经验费率(α=0.3 池均+0.7 自身近3期)")):
        firms, premium, claims, fund = run_regime(regime, seed)
        stats = {}
        for grp in ("高", "低"):
            ids = [i for i, f in enumerate(firms) if f["grp"] == grp]
            stats[grp] = {
                "inv": statistics.mean(firms[i]["s"] for i in ids),
                "rate": statistics.mean(p_eff(firms[i]) for i in ids),
                "prem": statistics.mean(premium[i] for i in ids) / T_PERIODS,
                "claim": statistics.mean(claims[i] for i in ids) / T_PERIODS,
            }
        stats["pool_rate"] = statistics.mean([stats["高"]["rate"], stats["低"]["rate"]])
        stats["fund"] = fund
        stats["total_claims"] = sum(claims.values())
        results[regime] = stats
        print(f"\n【{name}】")
        print(f"{'组':>4} {'安全投资级数':>8} {'事故率':>7} {'每期保费':>8}"
              f" {'每期期望赔付':>9}  保费−赔付(每期)")
        for grp in ("高", "低"):
            st = stats[grp]
            trans = st["prem"] - st["claim"]
            share = abs(trans) / st["claim"]
            tag = "被补贴(搭便车)" if trans < -0.10 * st["claim"] else \
                  ("补贴别人" if trans > 0.10 * st["claim"] else "基本自负")
            print(f"{grp:>4} {st['inv']:>10.2f} {st['rate']:>8.3%} {st['prem']:>9.2f}"
                  f"{st['claim']:>10.2f}   {trans:+7.2f}({share:>5.0%})  {tag}")
        print(f"池子整体事故率:{stats['pool_rate']:.3%};基金全期结余 "
              f"{stats['fund']:+.1f}(总赔付 {stats['total_claims']:.0f} 的 "
              f"{100*abs(stats['fund'])/stats['total_claims']:.1f}%)")

    uni, exp = results["uniform"], results["exp"]
    print("\n读数:")
    print("  · 统一费率:保费与自身风险无关,安全投资的边际收益只剩 δ=10% 的")
    print("    未保险残余——高、低风险企业投资都≈0,高风险企业被池均定价")
    print("    补贴(每期白拿 %.1f),搭便车;" % (uni["高"]["claim"] - uni["高"]["prem"]))
    print("  · 经验费率:自身经验的 70% 内化进价格,高风险企业投资显著恢复")
    print("    (%.2f 级),低风险企业仍≈%.1f 级——投资按风险差异化;" %
          (exp["高"]["inv"], exp["低"]["inv"]))
    print("  · 池子整体事故率 %.2f%% → %.2f%%(降 %.0f%%);交叉补贴从 ±%.1f 缩到 ±%.1f"
          % (100 * uni["pool_rate"], 100 * exp["pool_rate"],
             100 * (1 - exp["pool_rate"] / uni["pool_rate"]),
             abs(uni["低"]["prem"] - uni["低"]["claim"]),
             abs(exp["低"]["prem"] - exp["低"]["claim"])))
    print("  · 两套费率的基金都养得起池子——差别在安全激励,不在偿付能力;")
    print("    保费怎么定价,安全就怎么被投资。")

    # 断言:①统一费率下投资≈0(高风险企业显著更低);②经验费率恢复差异化;
    #        ③池子事故率显著下降;④交叉补贴收窄;⑤基金两制度下均近平衡
    assert uni["高"]["inv"] <= 0.05 and uni["低"]["inv"] <= 0.05, \
        f"统一费率下投资应≈0,实测 高{uni['高']['inv']:.2f}/低{uni['低']['inv']:.2f}"
    assert exp["高"]["inv"] >= 1.8, f"经验费率下高风险应投资≥1.8 级,实测 {exp['高']['inv']:.2f}"
    assert exp["高"]["inv"] - uni["高"]["inv"] >= 1.5, \
        "统一费率下高风险企业的安全投资应比经验费率下显著更低(搭便车)"
    assert exp["高"]["inv"] - exp["低"]["inv"] >= 1.5, "经验费率应恢复按风险分化的投资"
    assert exp["pool_rate"] <= 0.80 * uni["pool_rate"], \
        f"经验费率应显著降池子事故率:{exp['pool_rate']:.3%} vs {uni['pool_rate']:.3%}"
    assert abs(exp["低"]["prem"] - exp["低"]["claim"]) < \
        abs(uni["低"]["prem"] - uni["低"]["claim"]), "经验费率应收窄交叉补贴"
    assert abs(uni["fund"]) < 0.15 * uni["total_claims"], "统一费率基金应近平衡"
    assert abs(exp["fund"]) < 0.15 * exp["total_claims"], "经验费率基金应近平衡"
    print(f"\n✓ 律三断言通过:统一费率下投资 高{uni['高']['inv']:.2f}/低{uni['低']['inv']:.2f}"
          f"(高风险企业搭便车);经验费率下 高{exp['高']['inv']:.2f}/低{exp['低']['inv']:.2f}"
          f"(差异化恢复);池子事故率 %.2f%%→%.2f%%——保费定价即安全激励"
          % (100 * uni["pool_rate"], 100 * exp["pool_rate"]))


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① Beveridge 曲线:需求冲击=沿曲线移动(U 与 V 负相关);匹配效率")
    print("     下降=曲线外移(同一 V 下 U 更高,恢复同 U 需多投 93% 空位,")
    print("     存在 U、V 双高点)——周期性与结构性失业在 UV 平面上可分离")
    print("  ② McCall 搜索:失业金抬高保留工资,失业期拉长、接受工资提高——")
    print("     两笔账同录,保险是一笔显式换购,不是免费午餐也不是洪水猛兽")
    print("  ③ 经验费率:统一费率下高风险企业搭便车(投资≈0),经验费率把")
    print("     70% 自身风险内化进价格,恢复差异化投资,池子事故率降逾三成")
    print("     ——保费怎么定价,安全就怎么被投资")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
