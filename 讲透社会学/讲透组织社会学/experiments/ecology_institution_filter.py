# -*- coding: utf-8 -*-
"""生态、制度与信息:组织社会学三个核心机制的最小实现。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(结构卡三张的样板)、
04-组织社会学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定随机种子,逐幕 assert。

与同波家族实验零重叠:历史社会学 path_and_moment.py 管「时间中的事件」
(Polya 罐/Arthur 锁定/危机丛集),数理社会学管「微观规则×聚合」(Schelling/
WS/BA),经济社会学 embedded_markets.py 管「关系与市场」(信任制裁/嵌入);
这里管「组织的三层结构」——种群层的密度依赖、场域层的制度同构、科层层的
信息串。三个对象、三层尺度,互不抢地盘。

三律:
  幕一 密度依赖的 U 形死亡率(Hannan-Freeman 种群生态的核心律):
      把组织种群密度 N 钉住(死亡即补员),每期死亡数 ~ Binomial(N, μ(N)),
      死亡率 μ(N) = μ0 + 竞争(N/K) − 合法化增益(a·N/(N+N_½),logistic 饱和):
      断言(MC 网格扫描)①两力分解:只留合法化→死亡率随密度单调降(新形态
      被正名),只留竞争→单调升(红海)②合成的总死亡率随密度先降后升呈 U 形,
      且 U 形谷底随承载力 K 右移(K=100→K=200 谷底约翻倍)——「新组织形态
      先享受正名红利,再挤入竞争红海」(生态位逻辑的最小机器)③种群轨迹侧写:
      多条种群史从 N=1 长起(进入率也吃密度合法化),实现死亡率按密度带做
      暴露加权聚合——种群爬坡时先穿过谷底(正名时代:死亡率降),再涨进
      红海(死亡率回升),一生被 U 形切成两半。
  幕二 同构三机制的传播形状(DiMaggio-Powell 铁笼再访):
      场域 200 组织,同一项实践的采纳动力学三机制对照——
      强制(顶层 15 组织采纳,沿权力树自上而下,另有 20 个无依属关系的
      独立组织只能被环境慢慢渗透)/模仿(频率依赖:采纳率 ∝ 已采纳份额,
      恰是 logistic 方程 ds/dt=γ·s(1−s) 的离散版)/规范(5 个专业圈×40 组织
      的圈内网络扩散,圈间仅 1 座桥);断言①三机制最终采纳率都接近饱和
      (≥0.92)但轨迹形状不同:强制最快且阶梯状(整层整层地跳),模仿 S 形
      最陡中段(最大单期增量出现在份额 0.35-0.65),规范受网络拓扑约束最慢
      ②最终残留多样性(未采纳比例)模仿 < 强制——强制的尾巴是不受权力边
      管辖的独立组织(「抵抗尾巴」)——「三种力都能把场域变整齐,但留下的
      不齐各不相同」。
  幕三 科层串的信息过滤(Merton dysfunction 的定量面):
      指令 s=±1 自顶层经 L 层,每层保真率 p(AR(1) 型衰减信道:
      y = p·x + √(1−p²)·ε,ε~N(0,1),逐层独立);断言①顶层-底层信号保真度
      (相关系数)按复合律衰减 p_L = p^L——L 翻倍,保真度平方级跌落;
      底层读对指令方向的概率随层数单调滑向 0.5(纯猜)②每层设 m 个并行
      渠道取平均可部分恢复:噪声标准差 ∝ 1/√m,退税按同一汇率递减
      (判读买到 0.98 需每层约 49 条渠道)——「科层的层是信息税,
      宽度是部分退税」。

跑法: python -X utf8 experiments/ecology_institution_filter.py
"""

import math
import random
import statistics

SEED_BASE = 20260909  # 建族日固定种子;各幕/各档逐格加号,可复现


# ==================== 幕一:密度依赖的 U 形死亡率 ====================

MU0 = 0.11     # 基础死亡率
A_LEGIT = 0.10  # 合法化增益上限(密度→合法性→死亡率下降)
N_HALF = 12     # 合法化的半饱和密度
C_COMP = 0.20   # 竞争系数(死亡率随密度线性上升,斜率 C/K)
GRID_N = list(range(1, 61))   # 密度网格 1..60
T_SCAN = 4000   # 每格每重复的期数
REPS1 = 6       # 每格重复数
K_LIST = (100, 200)           # 两个承载力世界
TRAJ_REPS = 300  # 轨迹侧写的重复数(带聚合用)
T_TRAJ = 800     # 每条轨迹的步数
F0 = 3.0        # 每期新组织进入率(低密度时)


def mu_theory(n, k):
    """理论死亡率:μ(N) = μ0 + C·N/K − a·N/(N+N_½)。"""
    return MU0 + C_COMP * n / k - A_LEGIT * n / (n + N_HALF)


def valley_theory(k):
    """U 形谷底(理论):解 C/K = a·N_½/(N+N_½)² → N* = sqrt(a·N_½·K/C) − N_½。"""
    return math.sqrt(A_LEGIT * N_HALF * k / C_COMP) - N_HALF


def hazard_scan(rng_seed_base, k, legit=True, comp=True):
    """把种群密度钉在 GRID_N 各档(死亡即补员),实测每期死亡率。
    legit=False 关掉合法化(纯竞争世界),comp=False 关掉竞争(纯合法化世界)。"""
    out = []
    for n in GRID_N:
        deaths_total = 0
        for r in range(REPS1):
            rng = random.Random(rng_seed_base + n * 13 + r)
            acc = 0
            for _ in range(T_SCAN):
                mu = MU0
                if comp:
                    mu += C_COMP * n / k
                if legit:
                    mu -= A_LEGIT * n / (n + N_HALF)
                acc += rng.binomialvariate(n, mu)
            deaths_total += acc
        out.append(deaths_total / (n * T_SCAN * REPS1))
    return out


def quad_vertex(ys, center, half=3):
    """以 center 为中心取 2*half+1 点做最小二乘抛物线,返回顶点横坐标(网格下标)。"""
    xs = [center + d for d in range(-half, half + 1)]
    xm = sum(xs) / len(xs)
    ym = sum(ys[i] for i in xs) / len(xs)
    sxx = sum((x - xm) ** 2 for x in xs)
    sxy = sum((x - xm) * (ys[i] - ym) for x, i in zip(xs, xs))
    b = sxy / sxx
    sxx2 = sum((x - xm) ** 4 for x in xs)
    sxxy = sum((x - xm) ** 2 * (ys[i] - ym) for x, i in zip(xs, xs))
    a2 = sxxy / sxx2
    return xm - b / (2 * a2)


def trajectory(rng, k):
    """一条种群史:N 从 1 长起;进入率 = F0·(N/(N+8))·exp(−N/k)
    (诞生率也吃密度合法化:低密度时新形态不被正名,没人敢进——Hannan-Carroll
    诞生率定律的简化),死亡 ~ Binomial(N, μ(N))。
    返回逐期 (N, 死亡数) 序列。"""
    n = 1
    out = []
    for _ in range(T_TRAJ):
        mu = mu_theory(n, k)
        deaths = rng.binomialvariate(n, min(0.98, mu))
        lam = F0 * (n / (n + 8)) * math.exp(-n / k)
        # Knuth 泊松
        l_e = math.exp(-lam)
        births = 0
        p = 1.0
        while True:
            p *= rng.random()
            if p <= l_e:
                break
            births += 1
        out.append((n, deaths))
        n = max(1, n - deaths + births)
    return out


def act1():
    print("=" * 84)
    print("幕一 密度依赖的 U 形死亡率(Hannan-Freeman 核心律;"
          f"μ(N)={MU0} + {C_COMP}·N/K − {A_LEGIT}·N/(N+{N_HALF});"
          f"密度钉住在 1..60,每格 {REPS1} 重复×{T_SCAN} 期)")
    print("=" * 84)
    vt100, vt200 = valley_theory(100), valley_theory(200)
    print(f"\n理论谷底:K=100 → N*={vt100:.1f};K=200 → N*={vt200:.1f}"
          "   (N* = √(a·N_½·K/C) − N_½,随 K 开方右移)")

    # ① 两力分解
    legit_only = hazard_scan(SEED_BASE + 1000000, 10**9, legit=True, comp=False)
    comp_only = hazard_scan(SEED_BASE + 2000000, 100, legit=False, comp=True)
    d_legit = legit_only[0] - legit_only[-1]
    d_comp = comp_only[-1] - comp_only[0]
    print(f"\n① 两力分解(实测):只留合法化(K→∞):μ(1)={legit_only[0]:.4f} → "
          f"μ(60)={legit_only[-1]:.4f}(单调降 {d_legit:.4f});"
          f"只留竞争(K=100):μ(1)={comp_only[0]:.4f} → μ(60)={comp_only[-1]:.4f}"
          f"(单调升 {d_comp:.4f})")
    print("   ——同一种「组织多」:对合法性是营养(被正名),对资源是拥挤(红海)")

    # ② U 形合成 + 谷底随 K 移动
    results = {}
    for k in K_LIST:
        emp = hazard_scan(SEED_BASE + (3000000 if k == 100 else 4000000), k)
        i_min = min(range(len(emp)), key=lambda i: emp[i])
        vertex = quad_vertex(emp, i_min)
        results[k] = (emp, i_min, vertex)
        print(f"\n② K={k}(实测曲线,抽样打印):")
        print("   " + " ".join(f"N{n}:{emp[n - 1]:.3f}" for n in (1, 5, 10, 15, 20, 30, 40, 50, 60)))
        print(f"   粗谷底(网格 argmin)N={GRID_N[i_min]},抛物线拟合顶点 N*̂={vertex:.1f}"
              f"(理论 {valley_theory(k):.1f})")
        print(f"   μ(1)={emp[0]:.4f},μ̂(谷底)={emp[i_min]:.4f},μ(60)={emp[-1]:.4f}"
              f"——先降 {emp[0] - emp[i_min]:.4f} 再升 {emp[-1] - emp[i_min]:.4f}")
    emp100, imin100, v100 = results[100]
    emp200, imin200, v200 = results[200]

    # ③ 种群轨迹侧写:多条种群史,实现死亡率按密度带做暴露加权聚合
    bands = [(1, 5), (11, 18), (24, 40)]
    deaths_b = {b: 0 for b in bands}
    expos_b = {b: 0 for b in bands}
    peak_all = 0
    for r in range(TRAJ_REPS):
        traj = trajectory(random.Random(SEED_BASE + 5000000 + r), 100)
        peak_all = max(peak_all, max(n for n, _ in traj))
        for n, d in traj:
            for b in bands:
                if b[0] <= n <= b[1]:
                    deaths_b[b] += d
                    expos_b[b] += n
                    break
    hb = {b: deaths_b[b] / expos_b[b] for b in bands}
    eq_last = statistics.mean(n for n, _ in traj[-100:])
    print(f"\n③ 轨迹侧写(K=100,{TRAJ_REPS} 条种群史×{T_TRAJ} 期;"
          "进入率也吃密度合法化:λ=F0·(N/(N+8))·exp(−N/K)):")
    print(f"   种群从 N=1 长到末百期均值 N≈{eq_last:.1f}"
          f"(池化峰值 N≈{peak_all});实现死亡率按密度带(暴露加权):")
    for b in bands:
        print(f"   N∈[{b[0]},{b[1]}]:  {hb[b]:.4f}"
              f"(暴露 {expos_b[b]} 组织·期)")
    print("   ——每一条种群史都在重演同一件事:密度爬坡时先穿过谷底(正名"
          "时代:死亡率降),再涨进红海(死亡率回升);组织形态的一生被"
          " U 形切成两半")

    print("\n读数:")
    print("  · 「同行越多越好活」与「同行越多越难活」各对一半:前半段密度")
    print("    买合法性(形态被环境承认,死亡风险降),后半段密度买竞争(生态位")
    print("    挤压,死亡风险升)——U 形是两条单调曲线的叠加,不是玄学")
    print(f"  · 谷底不是常数,是 K(承载力)的函数:K=100→{v100:.1f},"
          f"K=200→{v200:.1f}——市场变大,红海后移,但形状不变")
    print("  · 这是 Hannan-Freeman 把「组织变迁」从组织内部搬到种群层的第一步:")
    print("    解释组织的生死,不看单个老板的英明,看种群密度所在的那段曲线")

    # 断言 1
    assert all(legit_only[i] > legit_only[i + 5] for i in (0, 20, 40, 54)), \
        "纯合法化世界死亡率应随密度单调下降"
    assert all(comp_only[i] < comp_only[i + 5] for i in (0, 20, 40, 54)), \
        "纯竞争世界死亡率应随密度单调上升"
    assert emp100[0] - min(emp100) > 0.008, "K=100 的 U 形左臂应足够深"
    assert emp100[-1] - min(emp100) > 0.02, "K=100 的 U 形右臂应足够深"
    assert abs(GRID_N[imin100] - vt100) <= 3.0, \
        f"K=100 粗谷底 {GRID_N[imin100]} 应近理论 {vt100:.1f}"
    assert abs(GRID_N[imin200] - vt200) <= 3.0, \
        f"K=200 粗谷底 {GRID_N[imin200]} 应近理论 {vt200:.1f}"
    assert abs(v100 - vt100) <= 3.5, f"K=100 谷底拟合值 {v100:.1f} 应近理论 {vt100:.1f}"
    assert abs(v200 - vt200) <= 3.5, f"K=200 谷底拟合值 {v200:.1f} 应近理论 {vt200:.1f}"
    assert v200 > v100 + 4, f"承载力翻倍应把谷底右移(K=200 {v200:.1f} vs K=100 {v100:.1f})"
    assert GRID_N[imin200] > GRID_N[imin100] + 4, "粗谷底也应随 K 右移"
    assert min(emp200) < min(emp100) - 0.008, "K 更大的世界谷底应更深(竞争更稀)"
    assert peak_all > valley_theory(100) + 5, "种群应长过谷底进入红海段"
    assert all(expos_b[b] >= 2000 for b in bands), "三个密度带都应有足够暴露"
    assert hb[bands[0]] > hb[bands[1]] + 0.004, \
        (f"正名时代:低密度带死亡率 {hb[bands[0]]:.4f} 应高于谷底带 "
         f"{hb[bands[1]]:.4f}")
    assert hb[bands[2]] > hb[bands[1]] + 0.006, \
        (f"红海时代:高密度带死亡率 {hb[bands[2]]:.4f} 应显著高于谷底带 "
         f"{hb[bands[1]]:.4f}")
    print(f"\n✓ 幕一断言通过:总死亡率 U 形(先降 {emp100[0] - min(emp100):.4f}"
          f" 再升 {emp100[-1] - min(emp100):.4f});谷底 K=100→{GRID_N[imin100]}"
          f"(拟合 {v100:.1f})、K=200→{GRID_N[imin200]}(拟合 {v200:.1f})"
          f",理论 {vt100:.1f}/{vt200:.1f},随 K 右移;")
    print(f"  轨迹侧写:密度带死亡率 {hb[bands[0]]:.3f}→{hb[bands[1]]:.3f}"
          f"→{hb[bands[2]]:.3f}——正名时代在前,红海在后,"
          "新组织形态先吃红利再挤红海")
    return dict(v100=v100, v200=v200)


# ==================== 幕二:同构三机制的传播形状 ====================

N_ORG = 200
LEVELS = [1, 14, 50, 115]   # 权力树:顶 + 3 层(合计 180),余 20 个独立组织
P_COERCE = 0.85             # 有已采纳上级时,本期的采纳概率
P_TRICKLE = 0.012           # 独立组织被环境渗透的每期概率
GAMMA_MIM = 0.35            # 模仿:采纳率 = γ·已采纳份额
Q_NORM = 0.14               # 规范:每条已采纳专业圈邻边每期的传播概率
N_CIRCLE = 5                # 专业圈数
T_END2 = 160
REPS2 = 40


def build_power_tree():
    """权力树:node 0 为顶;LEVELS 累计 180 个节点有上级,180..199 无依属。"""
    parent = {}
    off = 0
    bounds = []
    for sz in LEVELS:
        bounds.append((off, off + sz))
        off += sz
    for l in range(1, len(LEVELS)):
        lo, hi = bounds[l]
        plo, phi = bounds[l - 1]
        for v in range(lo, hi):
            i = v - lo
            parent[v] = plo + (i * (phi - plo)) // (hi - lo)
    return parent, bounds


def build_prof_network(rng):
    """专业圈网络:5 圈×40 组织;圈内=环+1 条随机弦(平均度≈3);相邻圈间
    仅 1 座桥(专业圈的拓扑瓶颈:圈间交流要走独木桥)。"""
    adj = [[] for _ in range(N_ORG)]
    seen = set()

    def add(u, v):
        if u == v or (min(u, v), max(u, v)) in seen:
            return
        seen.add((min(u, v), max(u, v)))
        adj[u].append(v)
        adj[v].append(u)

    per = N_ORG // N_CIRCLE
    for c in range(N_CIRCLE):
        base = c * per
        for j in range(per):
            add(base + j, base + (j + 1) % per)          # 环
            add(base + j, base + rng.randrange(per))      # 弦
    for c in range(N_CIRCLE):                             # 桥
        add(c * per + rng.randrange(per),
            ((c + 1) % N_CIRCLE) * per + rng.randrange(per))
    return adj


def run_coercive(rng):
    """强制:顶层节点集(顶+第一层=15)零时采纳,沿权力边下行;
    独立组织只能被环境慢慢渗透。返回逐期累计采纳序列。"""
    parent, bounds = build_power_tree()
    adopted = set(range(0, bounds[1][1]))   # 顶 + 第一层
    cum = [len(adopted)]
    for _ in range(T_END2):
        new = set()
        for v in range(bounds[1][1], bounds[-1][1]):       # 树上的第 2/3 层
            if v not in adopted and parent[v] in adopted:
                if rng.random() < P_COERCE:
                    new.add(v)
        for v in range(bounds[-1][1], N_ORG):              # 独立组织:抵抗尾巴
            if v not in adopted and rng.random() < P_TRICKLE:
                new.add(v)
        adopted |= new
        cum.append(len(adopted))
    return cum


def run_mimetic(rng):
    """模仿:频率依赖采纳,采纳率 = γ·已采纳份额(logistic 扩散的离散版)。"""
    adopted = set(rng.sample(range(N_ORG), 3))
    cum = [len(adopted)]
    for _ in range(T_END2):
        s = len(adopted) / N_ORG
        p = GAMMA_MIM * s
        new = {v for v in range(N_ORG) if v not in adopted and rng.random() < p}
        adopted |= new
        cum.append(len(adopted))
    return cum


def run_normative(rng):
    """规范:专业圈网络扩散,种子=第一圈的 4 个组织(专业委员会)。"""
    adj = build_prof_network(rng)
    adopted = set(range(4))
    cum = [len(adopted)]
    for _ in range(T_END2):
        new = set()
        for v in range(N_ORG):
            if v in adopted:
                continue
            k = sum(1 for u in adj[v] if u in adopted)
            if k and rng.random() < 1.0 - (1.0 - Q_NORM) ** k:
                new.add(v)
        adopted |= new
        cum.append(len(adopted))
    return cum


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 同构三机制的传播形状(场域 {N_ORG} 组织,同一实践,"
          f"三机制各 {REPS2} 次重复×{T_END2} 期)")
    print("=" * 84)
    print("  强制=顶层 15 组织采纳沿权力树下行(20 个独立组织只有环境渗透"
          f" {P_TRICKLE}/期);")
    print(f"  模仿=频率依赖(采纳率={GAMMA_MIM}×已采纳份额);"
          f"规范={N_CIRCLE} 个专业圈网络,圈内环+1 弦、圈间仅 1 桥,"
          f"逐边传播 {Q_NORM}")

    series = {}
    for name, fn in (("强制", run_coercive), ("模仿", run_mimetic),
                     ("规范", run_normative)):
        runs = [fn(random.Random(SEED_BASE + 6000000 + i if name == "强制"
                                 else SEED_BASE + 7000000 + i if name == "模仿"
                                 else SEED_BASE + 8000000 + i))
                for i in range(REPS2)]
        series[name] = runs

    def t_of(runs, thresh):
        n_need = thresh * N_ORG
        return [next((t for t, c in enumerate(r) if c >= n_need), T_END2 + 1)
                for r in runs]

    def jumps(r):
        return [r[t] - r[t - 1] for t in range(1, len(r))]

    m = {}
    for name, runs in series.items():
        finals = [r[-1] / N_ORG for r in runs]
        t50 = t_of(runs, 0.50)
        t90 = t_of(runs, 0.90)
        mjs = [max(jumps(r)) for r in runs]
        # 最大单期增量发生时的累计份额(S 中段诊断)
        shares = []
        for r in runs:
            js = jumps(r)
            t_star = js.index(max(js))
            shares.append(r[t_star + 1] / N_ORG)
        top3 = []
        for r in runs:
            js = sorted(jumps(r), reverse=True)
            top3.append(sum(js[:3]) / max(r[-1], 1))
        m[name] = dict(final=statistics.mean(finals),
                       t50=statistics.mean(t50), t90=statistics.mean(t90),
                       mj=statistics.mean(mjs), sh=statistics.mean(shares),
                       top3=statistics.mean(top3),
                       res=1 - statistics.mean(finals))

    print("\n① 轨迹形状对照(均值):")
    print(f"   {'机制':>4} {'t50':>5} {'t90':>5} {'终采率':>7} "
          f"{'最大单期增量':>8} {'峰值时份额':>7} {'前3跳占比':>7} {'残留':>6}")
    for name in ("强制", "模仿", "规范"):
        d = m[name]
        print(f"   {name:>4} {d['t50']:>5.1f} {d['t90']:>5.1f} {d['final']:>7.1%} "
              f"{d['mj']:>8.1f} {d['sh']:>7.1%} {d['top3']:>7.1%} {d['res']:>6.1%}")
    print("\n   累计采纳曲线(每 10 期一个点,均值):")
    ticks = list(range(0, T_END2 + 1, 10))
    for name in ("强制", "模仿", "规范"):
        row = [statistics.mean(r[t] for r in series[name]) / N_ORG for t in ticks]
        print(f"   {name}: " + " ".join(f"{x:.2f}" for x in row))

    print("\n读数:")
    print("  · 三种力殊途同归:终采率都逼近饱和——场域都会「变整齐」")
    print(f"  · 但整齐的形状各不同:强制整层整层地跳(前 3 跳占全部采纳的"
          f"{m['强制']['top3']:.0%},阶梯状),模仿的中段最陡(最大增量出现在份额"
          f"{m['模仿']['sh']:.0%} 处,S 形),规范一圈一圈地漫(圈间桥是瓶颈,最慢)")
    print(f"  · 留下的不齐也各不同:强制有抵抗尾巴(不受权力边管辖的独立组织,"
          f"残留 {m['强制']['res']:.1%}),模仿几乎无死角({m['模仿']['res']:.1%})")
    print("    ——轨迹形状与残留结构是机制的指纹:看形状能反推是哪种力在起作用")

    # 断言 2
    assert all(m[n]["final"] >= 0.92 for n in m), "三机制终采率均应接近饱和"
    assert m["强制"]["t50"] + 3 < m["模仿"]["t50"] < m["规范"]["t50"] - 5, \
        "到 50% 的时间应为强制<模仿<规范"
    assert m["强制"]["t90"] + 4 < m["模仿"]["t90"] < m["规范"]["t90"] - 15, \
        "到 90% 的时间应为强制<模仿<规范(规范受拓扑约束最慢)"
    assert m["强制"]["mj"] > 2.2 * m["模仿"]["mj"] > 0, \
        "强制的最大单期增量(整层跳)应远超模仿的 S 中段"
    assert m["模仿"]["mj"] > m["规范"]["mj"] + 3, \
        "模仿 S 形中段的陡峭应超过规范的圈间漫延"
    assert 0.35 <= m["模仿"]["sh"] <= 0.65, \
        f"模仿最大增量应出现在份额中段,实测 {m['模仿']['sh']:.2f}"
    assert m["强制"]["top3"] > 2.0 * m["模仿"]["top3"], \
        "强制的采纳应集中在少数几跳(阶梯状),模仿分散(S 形)"
    assert m["强制"]["res"] > m["模仿"]["res"] + 0.012, \
        f"残留多样性应模仿<强制,实测 {m['模仿']['res']:.1%} vs {m['强制']['res']:.1%}"
    print(f"\n✓ 幕二断言通过:终采率 强制{m['强制']['final']:.1%}/"
          f"模仿{m['模仿']['final']:.1%}/规范{m['规范']['final']:.1%} 均近饱和;"
          f"t50 {m['强制']['t50']:.0f}<{m['模仿']['t50']:.0f}<{m['规范']['t50']:.0f},"
          f"t90 {m['强制']['t90']:.0f}<{m['模仿']['t90']:.0f}<{m['规范']['t90']:.0f};")
    print(f"  阶梯(S形/慢漫)指纹:前3跳占比 {m['强制']['top3']:.0%}/"
          f"{m['模仿']['top3']:.0%},峰值份额 {m['模仿']['sh']:.0%};残留 "
          f"{m['模仿']['res']:.1%}<{m['强制']['res']:.1%}(抵抗尾巴)")
    return m


# ==================== 幕三:科层串的信息过滤 ====================

P_FID = 0.90          # 每层保真率 p
L_LIST = (1, 2, 3, 6, 12, 24)
L_MAIN = 12           # 主检验层数
M_LIST = (1, 4, 9)    # 并行汇报渠道数
R3 = 40000            # 蒙特卡洛重复数


def transmit(rng, x, m=1):
    """一层传输(m 个并行渠道取平均):y = (1/m)·Σ[p·x + √(1−p²)·ε]。"""
    tot = 0.0
    c = math.sqrt(1.0 - P_FID * P_FID)
    for _ in range(m):
        tot += P_FID * x + c * rng.gauss(0.0, 1.0)
    return tot / m


def chain(rng, s, layers, m=1):
    y = float(s)
    for _ in range(layers):
        y = transmit(rng, y, m)
    return y


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 科层串的信息过滤(指令 s=±1 经 L 层,每层保真率 p={P_FID},"
          f"AR(1) 衰减信道 y=p·x+√(1−p²)·ε;MC {R3} 次)")
    print("=" * 84)

    # ① 复合衰减:corr(s, y_L) ≈ p^L
    print("\n① 顶层-底层保真度(实测相关 vs 理论 p^L):")
    corrs = {}
    for i, l in enumerate(L_LIST):
        rng = random.Random(SEED_BASE + 9000000 + i)
        sw = swy = sy = y2 = 0.0
        for _ in range(R3):
            s = 1 if rng.random() < 0.5 else -1
            y = chain(rng, s, l)
            sw += s
            swy += s * y
            sy += y
            y2 += y * y
        n = R3
        cov = swy / n - (sw / n) * (sy / n)
        vy = y2 / n - (sy / n) ** 2
        corr = cov / math.sqrt(vy)
        corrs[l] = corr
        print(f"   L={l:>2}: 实测 corr={corr:.4f}  理论 p^L={P_FID ** l:.4f}"
              f"  读对方向概率={phi(corr / math.sqrt(max(1 - corr * corr, 1e-9))):.3f}"
              f"(理论 {phi(P_FID ** l / math.sqrt(1 - P_FID ** (2 * l))):.3f})")
    print(f"   复合律检验:corr(2L) ≈ corr(L)² —— corr(6)²={corrs[6] ** 2:.4f} vs "
          f"corr(12)={corrs[12]:.4f};corr(12)²={corrs[12] ** 2:.4f} vs "
          f"corr(24)={corrs[24]:.4f}")
    print("   ——层数翻倍,保真度不是减半,是平方:12 层的科层串把 0.90 的单层")
    print("   保真磨成 0.28;24 层只剩 0.08,底层读令像抛硬币")

    # ② 并行渠道:每层 m 个渠道取平均
    print(f"\n② 每层 m 个并行汇报渠道取平均(L={L_MAIN}):")
    res = {}
    accs = {}
    corr_m = {}
    pred = P_FID ** L_MAIN
    for j, mch in enumerate(M_LIST):
        rng = random.Random(SEED_BASE + 9500000 + j)
        sq = sy = swy = y2 = 0.0
        hit = 0
        for _ in range(R3):
            s = 1 if rng.random() < 0.5 else -1
            y = chain(rng, s, L_MAIN, mch)
            sq += (y - pred * s) ** 2
            sy += y
            swy += s * y
            y2 += y * y
            if (y > 0) == (s > 0):
                hit += 1
        n = R3
        cov = swy / n
        vy = y2 / n - (sy / n) ** 2
        sd = math.sqrt(sq / n)
        acc = hit / n
        corr_m[mch] = cov / math.sqrt(vy)
        res[mch] = sd
        accs[mch] = acc
        th_sd = math.sqrt((1 - P_FID ** (2 * L_MAIN)) / mch)
        th_acc = phi(pred * math.sqrt(mch) / math.sqrt(1 - P_FID ** (2 * L_MAIN)))
        th_cor = pred / math.sqrt(P_FID ** (2 * L_MAIN)
                                  + (1 - P_FID ** (2 * L_MAIN)) / mch)
        print(f"   m={mch}: 噪声SD实测 {sd:.4f}(理论 √((1−p^2L)/m)={th_sd:.4f});"
              f"方向判读 {acc:.3f}(理论 {th_acc:.3f});"
              f"保真 corr {corr_m[mch]:.3f}(理论 {th_cor:.3f})")
    r4, r9 = res[4] / res[1], res[9] / res[1]
    print(f"   SD 比:m=4 → {r4:.3f}(理论 1/√4=0.500);"
          f"m=9 → {r9:.3f}(理论 1/√9=0.333)——降噪 ∝ 1/√m")
    d1 = accs[4] - accs[1]
    d2 = accs[9] - accs[4]
    m_star = ((2.0537 * math.sqrt(1 - P_FID ** (2 * L_MAIN)) / pred) ** 2)
    print(f"   退税递减:第 1→4 条渠道买回方向判读 {d1:.3f},"
          f"第 5→9 条只买回 {d2:.3f};想把判读买到 0.98,"
          f"需要每层约 {m_star:.0f} 条并行渠道")
    print("   ——宽度是退税,但汇率按 1/√m 递减;真想省税,先数一数"
          "非加不可的层有几层(减层的杠杆是指数级的)")

    # 一条指令的漂移样例
    rng = random.Random(SEED_BASE + 9900000)
    print("\n   样例:「扩张令」(s=+1)下传 12 层的数值漂移(m=1 / m=9 各一条):")
    for mch in (1, 9):
        y = 1.0
        trace = [y]
        for _ in range(L_MAIN):
            y = transmit(rng, y, mch)
            trace.append(y)
        marks = [f"{v:+.2f}" for v in trace]
        print(f"     m={mch}: " + " ".join(marks))
    print("     (宽渠道也可能读反——m=9 的判读正确率约 81%,不是 100%;"    )
    print("      样例即一个方向翻转:末层 −0.14,弱信号被残余噪声压过)")

    print("\n读数:")
    print("  · 科层的每一层都在抽税:复合律 p^L——12 层 0.90 的保真只剩 28%,")
    print("    24 层只剩 8%;这不是执行者的恶意,是结构的地租(Merton 的")
    print("    dysfunction:规则照办,目标置换,信号在层间磨损)")
    print("  · 宽度是部分退税:m 个并行渠道取平均,噪声按 1/√m 缩;但汇率")
    print(f"    递减——第 1→4 条渠道买回 {d1:.3f},第 5→9 条只买回 {d2:.3f},")
    print(f"    想把判读买到 0.98 要每层约 {m_star:.0f} 条;真想省税,")
    print("    先数非加不可的层(减层的杠杆是指数级的:层减半,保真开方)")

    # 断言 3
    for l in L_LIST:
        assert abs(corrs[l] - P_FID ** l) <= 0.02, \
            f"L={l} 实测保真 {corrs[l]:.4f} 应近理论 {P_FID ** l:.4f}"
    assert abs(corrs[12] - corrs[6] ** 2) <= 0.025, "L 翻倍应给平方级衰减"
    assert abs(corrs[24] - corrs[12] ** 2) <= 0.02, "L 再翻倍仍是平方级"
    assert corrs[1] > corrs[3] > corrs[6] > corrs[12] > corrs[24], \
        "保真度应随层数单调衰减"
    assert 0.44 <= r4 <= 0.56, f"m=4 的 SD 比应近 0.5,实测 {r4:.3f}"
    assert 0.27 <= r9 <= 0.39, f"m=9 的 SD 比应近 0.333,实测 {r9:.3f}"
    assert accs[9] > accs[4] > accs[1], "并行渠道应单调提升方向判读"
    assert accs[9] - accs[1] > 0.08, "m=9 应显著恢复判读精度"
    assert d1 > d2 > 0, f"退税应递减(1/√m),实测 {d1:.3f} vs {d2:.3f}"
    assert corr_m[9] > corr_m[1] + 0.25, "m=9 应显著恢复保真度"
    assert corr_m[9] < 0.75, "有限渠道的保真仍远低于满血(退税不白给)"
    print(f"\n✓ 幕三断言通过:复合衰减 corr(L)=p^L(24 层实测 {corrs[24]:.3f}"
          f" vs 理论 {P_FID ** 24:.3f}),L 翻倍平方级;"
          f"并行渠道 SD 比 {r4:.2f}/{r9:.2f}≈1/√m,判读 {accs[1]:.2f}→"
          f"{accs[9]:.2f} 且退税递减({d1:.2f}→{d2:.2f},判读买到 0.98 "
          f"需每层约 {m_star:.0f} 条渠道)——层是信息税,宽是部分退税")
    return dict(corrs=corrs, accs=accs)


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 密度依赖:死亡率随密度 U 形(合法化先降/竞争后升),谷底随承载")
    print("     力 K 右移,轨迹侧写「先正名后红海」——种群生态的核心律")
    print("  ② 同构三机制:终采率均近饱和但形状各异(强制阶梯/模仿 S 形中段最陡/")
    print("     规范拓扑约束最慢),残留多样性模仿<强制(抵抗尾巴)——机制的指纹")
    print("     在轨迹形状与残留结构里,不在终局数字里")
    print("  ③ 科层串:保真度按 p^L 复合衰减(L 翻倍平方级),并行渠道按 1/√m")
    print("     部分退税且汇率递减(判读买到 0.98 需每层约 49 条渠道)")
    print("     ——dysfunction 的定量面")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
