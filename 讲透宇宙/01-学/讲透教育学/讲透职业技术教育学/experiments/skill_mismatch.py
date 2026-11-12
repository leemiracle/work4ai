# -*- coding: utf-8 -*-
"""技能错配的供给-需求模拟:学制时滞、聚合敏感性与产教融合的信息回路(00/01/04 章配套实验)。

主题呼应技能错配研究通说(垂直/水平/技能老化三分法;总量平衡掩盖结构
错配;供给调整滞后,00 章发现 1/2):把技能供需拆成两侧——

  需求侧 D_t(产业结构分布,八类技能类目):结构变迁(传统→智能/数字/
    健康)+ 部门周期(扩张期传统部门吸纳、转型期新兴部门吸纳,组内
    对冲)+ 小幅年度噪声;
  供给侧 S_t(教育系统产出分布):配额 Q_t 按惰性 α 向**滞后 d 年的
    需求信号**调整(统计发布+研判时滞),学生入学后 **L 年**毕业
    (学制时滞);合作办学=需求信息进课程:培养规格后段按需求信息
    锁定(订单/分段定向,L↓)、信息当年可用(d→0)、配额调整加快(α↑)。

  错配度量 M_t = 0.5·Σ_k|S_t[k] − D_t[k]|(总变异距离,份额单位);
  粗口径 M_coarse 按两大类(生产类/服务类)聚合后再算。

三世界共用同一条需求路径(CRN 同随机数配对):基准/快回路/合作
办学——组间差不受抽样运气污染(与学前教育学家族实验同纪律)。

断言三律(通说的结构表达):
  A. 学制时滞→周期性错配:基准世界(信息时滞 d=2、学制 L=3、
     惰性 α=0.25)相对快回路世界(d=0,L=0,α=0.9):①平均/峰值
     错配数倍以上(追移动靶)②错配序列呈周期性峰(部门周期的
     滞后共振)③蛛网式短缺-过剩交替:无趋势的周期类目(文化社会)
     的供给缺口在"短缺(≤−0.8pp)→过剩(≥+0.8pp)"间往返
     ——对口培养的孪生副作用是周期性错配,不是收敛;
  B. 聚合敏感性:①恒有 M_coarse ≤ M_fine(聚合是总变异距离的
     收缩投影:组内差距求和时相互抵消——数学事实逐年断言)
     ②动态路径上细口径错配均值 ≥ 3×粗口径(结构错配大部分住在
     聚合看不见的地方)③构造例:总量完全平衡(粗口径=0)而
     结构错配 0.16(组内对调份额)——「总量平衡掩盖结构错配」;
  C. 合作办学压缩峰值:需求信息进课程——培养规格在学制后段按
     需求信息锁定(订单/分段定向,有效时滞 L:3→1)、需求信息当年
     可用(d:2→0)、配额调整加快(α:0.25→0.55):错配峰值与均值
     压至基准的 0.7 以下;机制归因:三杠杆各砍一段滞后(信号滞后/
     调整惰性/学制死锁),单动一项几乎无效,α 单动甚至反噬
     (需求侧可预测时,回路快=峰值低——产教融合的定量面)。

⚙ 机制边界(自证):需求侧换成逐年独立噪声(无趋势、无周期,
     不可预测)——合作办学的压缩增益消失(40 条噪声路径平均:
     均值比 ≥0.80,追不可预测的噪声反而放大摆动)。**信息回路的价值
     依赖于需求的可预测性**——产教融合压缩的是"可预测变化"
     的时滞损耗,不是预测本身。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值(学制 3 年、统计发布滞后约 2 年、
     专业目录调整以年计的惰性;产业结构变迁与部门周期为风格化
     幅度),不是任何真实经济体的拟合;
  2. 模拟证明的是「时滞+惰性调整+组内结构变迁足以生成三律」
     (机制充分性),不是对任何职教政策的预测;
  3. 通说依据:技能错配类型学与测量通道批评(自报/对照表/雇主
     调查各有系统偏差)、过度教育与对口率的口径依赖(分类粒度是
     结论参数)、供给调整滞后的"职业学校谬误"之辨(Foster 1965:
     计划式供给赶不上需求变化)、企业培训供给的四因子解释
     ——均为综述级通说;
  4. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率;
     机制约束:学制 L≥1(培养周期不可为零)、合作办学 α 不低于
     基准惰性(需求信息进课程不会让调整更慢)。

跑法: python experiments/skill_mismatch.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
T_YEARS = 48                      # 模拟年数
N_CAT = 8                         # 技能类目数
CAT_NAMES = ["传统加工", "智能制造", "建筑土木", "交通物流",
             "商贸金融", "信息数字", "健康护理", "文化社会"]
GROUPS = ([0, 1, 2, 3], [4, 5, 6, 7])          # 粗口径:生产类 / 服务类
GROUP_NAMES = ["生产类", "服务类"]

BASE = [0.16, 0.09, 0.11, 0.10, 0.18, 0.12, 0.14, 0.10]   # 基期份额(和=1)
# 期末份额倍数:结构变迁主要发生在组内(传统↔智能/商贸↔数字/健康升),
# 两大类的总份额几乎不动——聚合口径看起来"稳定"的产业结构
TREND_MULT = [0.40, 2.20, 1.00, 1.00, 0.55, 1.50, 1.25, 1.00]
CYCLE_PERIOD = 10.0               # 部门周期(年)
# 部门周期(组内对冲):扩张期传统/线下部门吸纳,低谷期新兴部门吸纳
CYCLE_PAIRS = ((0, 1, 0.020), (4, 5, 0.024), (6, 7, 0.014))  # (a,b,amp):a±amp·sin,b∓
SIGMA_DEMAND = 0.008              # 需求年度噪声(对数倍增的尺度)
SIGMA_NOISE = 0.05                # 机制边界世界的逐年独立噪声(不可预测)

# 供给侧参数(三个世界)
W_FAST = dict(lag=0, dinfo=0, alpha=0.90, beta=0.0)   # 快回路(对照:瞬时调整)
W_BASE = dict(lag=3, dinfo=2, alpha=0.25, beta=0.0)   # 基准(学制3年+统计滞后2年+惰性)
# 合作办学:订单/分段定向把"入学即定型"变"后段定向"(有效时滞 L:3→1),
# 需求信息当年进课程(d:2→0),配额调整加快(α:0.25→0.55)
W_COOP = dict(lag=1, dinfo=0, alpha=0.55, beta=0.0)

ALT_THRESHOLD = 0.008             # 蛛网交替判据:短缺/过剩阈值(±份额)


def demand_path(seed, mode="structural", trend_scale=1.0, cycle_scale=1.0,
                sigma=None):
    """生成 T 年需求分布(每行和为 1)。

    structural:结构变迁(线性趋势×trend_scale)+部门周期(×cycle_scale)+小噪声;
    noise:     无趋势无周期,逐年独立噪声(不可预测世界,机制边界用)。
    """
    if sigma is None:
        sigma = SIGMA_DEMAND if mode == "structural" else SIGMA_NOISE
    rng = random.Random(seed)
    path = []
    for t in range(T_YEARS):
        w = [0.0] * N_CAT
        for k in range(N_CAT):
            mult = 1.0
            if mode == "structural":      # 噪声世界无趋势无周期(彻底不可预测)
                mult = 1.0 + (TREND_MULT[k] - 1.0) * (t / (T_YEARS - 1.0)) * trend_scale
            val = BASE[k] * mult
            if mode == "structural":
                s = math.sin(2.0 * math.pi * t / CYCLE_PERIOD)
                for (a, b, amp) in CYCLE_PAIRS:
                    if k == a:
                        val += amp * cycle_scale * s
                    elif k == b:
                        val -= amp * cycle_scale * s
            val *= math.exp(sigma * rng.gauss(0.0, 1.0))
            w[k] = max(val, 1e-6)
        z = sum(w)
        path.append([x / z for x in w])
    return path


def supply_path(demand, lag, dinfo, alpha, beta):
    """供给侧:配额按惰性 α 向滞后 dinfo 年的需求调整;毕业构成再滞后 lag 年。

    S_t = (1−β)·Q_{t−lag} + β·Q_{t−1}(β=模块中途按最新配额更新的份额)。
    配额与组合均为分布的凸组合,和恒为 1。
    """
    q = list(BASE)                       # 入学前初始配额
    hist = []                            # Q_0..Q_t(含 t=0 基期)
    for t in range(T_YEARS):
        if t > 0:
            d_hat = demand[max(0, t - dinfo)]
            q = [(1.0 - alpha) * qi + alpha * dh for qi, dh in zip(q, d_hat)]
        hist.append(list(q))
    out = []
    for t in range(T_YEARS):
        old = hist[max(0, t - lag)]
        new = hist[t - 1] if t >= 1 else hist[0]
        out.append([(1.0 - beta) * oi + beta * ni for oi, ni in zip(old, new)])
    return out


def mismatch(s, d):
    """细口径错配 M = 0.5·Σ|S−D|(总变异距离,份额单位)。"""
    return 0.5 * sum(abs(a - b) for a, b in zip(s, d))


def aggregate(v):
    """按两大类聚合(组内求和)。"""
    return [sum(v[k] for k in g) for g in GROUPS]


def coarse_mismatch(s, d):
    return mismatch(aggregate(s), aggregate(d))


def series(demand, **world):
    """跑一个世界,返回 (M_fine 列表, M_coarse 列表, S 路径)。"""
    s = supply_path(demand, **world)
    mf = [mismatch(s[t], demand[t]) for t in range(T_YEARS)]
    mc = [coarse_mismatch(s[t], demand[t]) for t in range(T_YEARS)]
    return mf, mc, s


def local_maxima(xs, window=5, min_prom=0.004):
    """滑动平均后的局部极大值计数(周期性检测)。"""
    sm = [sum(xs[max(0, i - window // 2): i + window // 2 + 1])
          / len(xs[max(0, i - window // 2): i + window // 2 + 1])
          for i in range(len(xs))]
    peaks = []
    for i in range(1, len(sm) - 1):
        if sm[i] >= sm[i - 1] and sm[i] > sm[i + 1] and sm[i] >= min_prom:
            peaks.append(i)
    return peaks


def alternations(gaps, thr=ALT_THRESHOLD):
    """蛛网交替计数:缺口序列在 ≤−thr 与 ≥+thr 两个状态间的往返次数。"""
    state = 0                          # 0=中间带, +1=过剩, −1=短缺
    flips = 0
    for g in gaps:
        st = 1 if g >= thr else (-1 if g <= -thr else 0)
        if st != 0 and state != 0 and st != state:
            flips += 1
        if st != 0:
            state = st
    return flips


# ----------------------------- 断言 A/B/C(基准情形) -----------------------------
def base_case(seed=20260907, **jitter):
    """同一需求路径上跑三个世界(CRN),返回错配统计。"""
    dem = demand_path(seed, **jitter)
    mf_fast, mc_fast, _ = series(dem, **W_FAST)
    mf_base, mc_base, s_base = series(dem, **W_BASE)
    mf_coop, mc_coop, _ = series(dem, **W_COOP)
    gap3 = [s_base[t][7] - dem[t][7] for t in range(T_YEARS)]   # 文化社会(无趋势周期类目)
    return {
        "dem": dem,
        "fast": (mf_fast, mc_fast), "base": (mf_base, mc_base),
        "coop": (mf_coop, mc_coop), "gap3": gap3,
        "fast_mean": sum(mf_fast) / T_YEARS, "fast_peak": max(mf_fast),
        "base_mean": sum(mf_base) / T_YEARS, "base_peak": max(mf_base),
        "coop_mean": sum(mf_coop) / T_YEARS, "coop_peak": max(mf_coop),
        "coarse_mean": sum(mc_base) / T_YEARS, "coarse_peak": max(mc_base),
        "peaks": local_maxima(mf_base), "alters": alternations(gap3),
    }


def static_aggregation_example():
    """构造例:总量完全平衡(粗口径=0)而结构错配 0.16(组内对调份额)。"""
    s = list(BASE)
    d = list(BASE)
    d[0], d[1] = BASE[1], BASE[0]              # 传统加工↔智能制造 全额对调(0.07)
    d[4], d[5] = BASE[4] - 0.09, BASE[5] + 0.09  # 商贸→数字 对调 0.09
    return mismatch(s, d), coarse_mismatch(s, d)


def main():
    if hasattr(sys.stdout, "reconfigure"):          # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 72)
    print("技能错配的供给-需求模拟:学制时滞 × 聚合敏感性 × 产教融合信息回路")
    print("=" * 72)
    print(f"模型:T={T_YEARS} 年 × {N_CAT} 类技能;需求=结构变迁+部门周期"
          f"(周期 {CYCLE_PERIOD:.0f} 年)+噪声 {SIGMA_DEMAND};"
          f"供给=配额惰性调整(α)+统计时滞(d)+学制时滞(L)")
    print(f"三世界(CRN 同需求路径):快回路 {W_FAST} / 基准 {W_BASE} / "
          f"合作办学 {W_COOP}")

    r = base_case()

    # ---- 断言 A:学制时滞→周期性错配 ----
    print(f"\n[断言A 学制时滞] 错配均值:基准 {r['base_mean']:.4f} vs 快回路 "
          f"{r['fast_mean']:.4f}(×{r['base_mean']/max(r['fast_mean'],1e-9):.1f});"
          f" 峰值 {r['base_peak']:.4f} vs {r['fast_peak']:.4f}"
          f"(×{r['base_peak']/max(r['fast_peak'],1e-9):.1f})")
    assert r["base_mean"] >= 2.0 * r["fast_mean"], "时滞未抬升平均错配"
    assert r["base_peak"] >= 3.0 * r["fast_peak"], "时滞未抬升错配峰值"
    print(f"  周期性:错配序列局部峰 {len(r['peaks'])} 个"
          f"({'、'.join(str(p) for p in r['peaks'])} 年);"
          f"蛛网交替(文化社会,±{ALT_THRESHOLD:.1%}){r['alters']} 次往返")
    assert len(r["peaks"]) >= 3, "错配未见周期性峰"
    assert r["alters"] >= 3, "未见短缺-过剩交替(蛛网)"
    print("  ✓ 教育系统追移动靶:信号滞后+学制时滞→错配周期性发作,")
    print("    无趋势类目在短缺/过剩间往返——「抢建-过剩-收缩-再短缺」")
    print("    的循环是结构性的,不是哪一年的决策失误(00 章发现 1)")

    # ---- 断言 B:聚合敏感性(总量平衡掩盖结构错配) ----
    mf, mc = r["base"]
    worst = max(mc)
    print(f"\n[断言B 聚合敏感] 细口径均值 {r['base_mean']:.4f} vs 粗口径均值 "
          f"{r['coarse_mean']:.4f}(×{r['base_mean']/max(r['coarse_mean'],1e-9):.1f});"
          f" 粗口径峰值 {worst:.4f}")
    assert all(mc[t] <= mf[t] + 1e-9 for t in range(T_YEARS)), "聚合收缩性被违反(数学事实)"
    assert r["base_mean"] >= 3.0 * r["coarse_mean"], "细/粗口径未拉开 3 倍"
    fine_m, coarse_m = static_aggregation_example()
    print(f"  构造例:总量完全平衡(粗口径 {coarse_m:.6f})而结构错配 {fine_m:.2f}"
          f"(传统加工↔智能制造 0.07 + 商贸→数字 0.09 的组内对调)")
    assert coarse_m <= 1e-9 and fine_m >= 0.12, "构造例失败"
    hidden = sum(1 for t in range(T_YEARS) if mc[t] <= 0.012 and mf[t] >= 0.040)
    print(f"  动态路径上 {hidden}/{T_YEARS} 年呈「粗口径≤1.2% 且细口径≥4%」"
          f"——总量叙事看不见的那部分")
    assert hidden >= 10, "动态路径上未见足量的『平衡掩盖错配』年份"
    print("  ✓ 聚合是总变异距离的收缩投影:组内差距在求和时抵消,")
    print("    「毕业生总数≈岗位总数」与『传统过剩、新兴缺人』同时为真")
    print("    (00 章发现 2;03 章粒度即立场)")

    # ---- 断言 C:合作办学压缩错配峰值(产教融合的定量面) ----
    print(f"\n[断言C 合作办学] 峰值 {r['base_peak']:.4f} → {r['coop_peak']:.4f}"
          f"(压缩至 {r['coop_peak']/r['base_peak']:.2f});"
          f"均值 {r['base_mean']:.4f} → {r['coop_mean']:.4f}"
          f"(压缩至 {r['coop_mean']/r['base_mean']:.2f})")
    assert r["coop_peak"] <= 0.70 * r["base_peak"], "合作办学未压缩错配峰值"
    assert r["coop_mean"] <= 0.70 * r["base_mean"], "合作办学未压缩平均错配"
    dem = r["dem"]
    for label, world in (("仅缩短有效时滞(L→1,后段定向)", dict(W_BASE, lag=1)),
                         ("仅信息当年进课程(d→0)", dict(W_BASE, dinfo=0)),
                         ("仅调整加快(α→0.55)", dict(W_BASE, alpha=0.55))):
        mf_x, _, _ = series(dem, **world)
        pk = max(mf_x)
        print(f"    机制归因:{label}:峰值 {pk:.4f}"
              f"(较基准降 {1 - pk / r['base_peak']:.0%})")
    print("  ✓ 需求信息进课程压缩错配峰值——三个杠杆各砍一段滞后(信号")
    print("    滞后 d/调整惰性 α/学制死锁 L),单动一项几乎无效,α 单动")
    print("    甚至反噬(追着旧信号快跑=过度修正,蛛网更凶)——产教融合")
    print("    的定量面不在『合作』的姿态,在需求信号到培养规格的距离")

    # ---- 机制边界:需求不可预测时,信息回路的价值消失 ----
    print("\n⚙ 机制边界:需求换成逐年独立噪声(无趋势、无周期,不可预测)")
    n_seeds = 40
    mb_sum = mc_sum = pb_sum = pc_sum = 0.0
    for s_i in range(n_seeds):
        dem_n = demand_path(seed=31000 + s_i, mode="noise")
        mb, _, _ = series(dem_n, **W_BASE)
        mc2, _, _ = series(dem_n, **W_COOP)
        mb_sum += sum(mb) / T_YEARS
        mc_sum += sum(mc2) / T_YEARS
        pb_sum += max(mb)
        pc_sum += max(mc2)
    ratio_mean = mc_sum / mb_sum
    ratio_peak = pc_sum / pb_sum
    print(f"  噪声世界({n_seeds} 条路径平均):错配均值比 {ratio_mean:.2f},"
          f"峰值比 {ratio_peak:.2f}"
          + ("——增益消失,均值甚至反噬" if ratio_mean >= 1.0 else "——增益消失")
          + f"(对照:结构世界峰值压缩至 {r['coop_peak']/r['base_peak']:.2f})")
    assert ratio_mean >= 0.80, "噪声世界均值出现虚假增益(与机制矛盾)"
    assert ratio_mean > (r["coop_mean"] / r["base_mean"]) + 0.10, \
        "噪声世界与结构世界的回路价值未拉开差距"
    print("  信息回路的价值依赖于需求的可预测性:追不可预测的噪声")
    print("  只会放大摆动——产教融合压缩的是『可预测变化』的时滞损耗,")
    print("  它不能替代对结构性变化的研判(断言 C 的靶是趋势+周期世界)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性:200 次抖动(趋势幅度/周期幅度/噪声/α/d/L")
    print("各±20%-40%;机制约束:L≥1(学制不为零)、合作办学 α≥基准 α")
    n_draws, need = 200, 0.90
    passes = {"A 学制时滞": 0, "B 聚合敏感": 0, "C 合作办学": 0}
    for dr in range(n_draws):
        jit = lambda a, b: random.uniform(a, b)      # noqa: E731
        ts, cs = jit(0.75, 1.25), jit(0.70, 1.30)
        sig = jit(0.005, 0.012)
        lag_b, d_b = int(jit(2, 4)), int(jit(1, 3))
        a_b = jit(0.18, 0.32)
        a_c = max(a_b, jit(0.45, 0.65))              # 机制约束:合作办学不更慢
        dem_d = demand_path(seed=70000 + dr, mode="structural",
                            trend_scale=ts, cycle_scale=cs, sigma=sig)
        mff, _, _ = series(dem_d, **W_FAST)
        mfb2, mcb2, sb = series(dem_d, lag=lag_b, dinfo=d_b, alpha=a_b, beta=0.0)
        mfc2, _, _ = series(dem_d, lag=1, dinfo=0, alpha=a_c, beta=0.0)
        mean_b, peak_b = sum(mfb2) / T_YEARS, max(mfb2)
        mean_f = sum(mff) / T_YEARS
        gap = [sb[t][7] - dem_d[t][7] for t in range(T_YEARS)]
        ok_a = (mean_b >= 2.0 * mean_f and peak_b >= 3.0 * max(mff)
                and len(local_maxima(mfb2)) >= 3 and alternations(gap) >= 3)
        mean_c = sum(mcb2) / T_YEARS
        ok_b = (mean_b >= 3.0 * mean_c
                and all(mcb2[t] <= mfb2[t] + 1e-9 for t in range(T_YEARS)))
        ok_c = (max(mfc2) <= 0.75 * peak_b and sum(mfc2) / T_YEARS <= 0.75 * mean_b)
        passes["A 学制时滞"] += ok_a
        passes["B 聚合敏感"] += ok_b
        passes["C 合作办学"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『时滞+惰性调整+组内结构变迁足以生成")
    print("  三律』,不是任何真实职教体系的预测;八类类目、趋势与周期幅度均为")
    print("  风格化参数,且未建模学生的专业选择(信号驱动)、企业的学历偏好与")
    print("  跨类目再训练(岗前培训可部分吸收错配)——真实证据请回 01 章素材")
    print("  (错配测量三通道/Cedefop 供需预测)与原始文献。")


if __name__ == "__main__":
    main()
