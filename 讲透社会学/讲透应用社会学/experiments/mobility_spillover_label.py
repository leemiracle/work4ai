# -*- coding: utf-8 -*-
"""流动、溢出与标签:应用社会学三个核心机制的最小实现。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(结构卡三张的样板)、
04-应用社会学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定随机种子,逐幕 assert。

与同波家族实验零重叠:组织社会学 ecology_institution_filter.py 管「组织的三层
结构」(种群密度依赖/场域同构/科层信息串),数理社会学管「微观规则×聚合」,
社会地理学管「空间格局」,社会学方法管「抽样与测量」;这里管「应用研究的
三个计量现场」——流动表(分层与流动的可观测结构)、社区干预(应用因果推断
的溢出陷阱)、标签过程(社会反应的反馈回路)。三个对象、三套量,互不抢地盘。

三律:
  幕一 代际流动表的两张面孔(对数线性思想的最小机器):
      构造两个 5×5 父-子职业流动表,两社会边际完全相同、仅流动强度不同——
      社会 A=独立性表(获得与出身无关),社会 B=对角乘子 ×φ 的继承参数再经
      IPF(迭代比例拟合)把双边际精确钉回同一分布;断言①两表边际逐格相等
      (<1e-9)之下,对角继承率(出身=获得)A≈Σmᵢ²≈0.24 vs B≈0.45+,且随 φ
      单调上升——「同一个阶层结构比例,可以藏完全不同的开放度」②流动率
      (非对角占比)之差在两张边际表上完全不可见;抽样层(各 2500 对父-子)
      复核:两样本边际差在噪声内,对角差远超 8 倍标准误;独立性检验 G²
      (df=16,5% 临界 26.3)一个不爆阈、一个爆表。
  幕二 SUTVA 与社区溢出(应用干预的计量陷阱):
      社区健康促进干预,社区内环网络(每人 2 邻居),直接效应 τ,每有一个
      受治邻居得溢出 θτ;对照两种随机化——个体随机化(社区内各半受治,
      合并处理-对照均值差估计)vs 社区随机化(整社区全治/全不治);总效应
      基准=全治世界−全不治世界=τ(1+2θ)。断言①θ=0 两设计均≈τ;②θ>0 时
      个体随机化只量到直接效应 τ,系统性低估总效应,低估量=2θτ 随 θ 单调
      增(θ=0.5 时个体估计只占总效应的一半)③社区随机化全程命中总效应
      ——「社区是干预的单位,个体是测量的单位,拿错尺就量错布」。
  幕三 标签的放大回路(初级越轨→次级越轨):
      个体每轮以倾向 q 越轨,越轨以概率 p 被捕;被捕→获得标签:就业指数
      ×0.6、越轨倾向×λ(社会反应的反馈);高标签环境(λ=3.2)vs 低标签环境
      (λ=1.3),同初始 q、同被捕率 p;断言①λ 足够大出现「标签自锁」:被捕过
      的人在末十轮的再越轨率,高标签环境远高于低标签环境,累计越轨人均
      次数数倍——「刑罚的重量有一部分以再犯的形式回流」②对照无反馈
      (λ=1)两环境无差③从未被捕者两环境底色相同(选择校正后的解析值
      1−[(1−q₀)/(1−q₀p)]^L:条件在「从未被捕」会截掉末窗越轨)——差异
      全部由标签的反馈制造,不由人群初始差异制造。

跑法: python -X utf8 experiments/mobility_spillover_label.py
"""

import math
import random
import statistics

SEED_BASE = 20260909  # 建族日固定种子;各幕/各档逐格加号,可复现


# ==================== 幕一:代际流动表的两张面孔 ====================

MARG = (0.08, 0.22, 0.34, 0.24, 0.12)   # 五阶级边际(父辈=子辈=同一分布)
CLASS_NAMES = ("高级专业与管理", "低层非体力", "小业主", "技术工人", "非技术工人")
PHI_MAIN = 6.0                          # 社会 B 的对角继承乘子
PHI_SCAN = (1.0, 2.0, 4.0, 8.0)         # 开放度参数扫描
IPF_ITERS = 2000                        # IPF 迭代数(边际钉到 1e-12 量级)
N_PAIR = 2500                           # 每个社会抽的父-子对数
G2_CRIT_5PCT = 26.30                    # df=16 的卡方 5% 临界值


def ipf_diag_table(phi):
    """对数线性思想的最小机器:独立性表的对角 ×φ(继承参数),再 IPF 往返
    拟合把行、列边际精确钉回 MARG——边际(结构)与关联(流动)是两个自由度。"""
    n = len(MARG)
    t = [[MARG[i] * MARG[j] for j in range(n)] for i in range(n)]
    for i in range(n):
        t[i][i] *= phi
    for _ in range(IPF_ITERS):
        for i in range(n):                       # 行拟合
            f = MARG[i] / sum(t[i])
            for j in range(n):
                t[i][j] *= f
        for j in range(n):                       # 列拟合
            f = MARG[j] / sum(t[i][j] for i in range(n))
            for i in range(n):
                t[i][j] *= f
    return t


def diag_share(t):
    return sum(t[i][i] for i in range(len(t)))


def max_margin_gap(t):
    n = len(MARG)
    rows = [max(abs(sum(t[i]) - MARG[i]) for i in range(n))]
    cols = [max(abs(sum(t[i][j] for i in range(n)) - MARG[j]) for j in range(n))]
    return max(rows + cols)


def dissimilarity(a, b):
    return 0.5 * sum(abs(a[i][j] - b[i][j]) for i in range(len(a))
                     for j in range(len(a)))


def sample_counts(rng, t, n):
    """从 25 格多项分布抽 n 对父-子(手写二分查累积,免依赖 bisect)。"""
    flat, cum = [], []
    c = 0.0
    for i in range(5):
        for j in range(5):
            c += t[i][j]
            cum.append(c)
            flat.append((i, j))
    counts = [[0] * 5 for _ in range(5)]
    for _ in range(n):
        u = rng.random() * c
        # bisect_right:找最小 k 使 cum[k] > u,则 u 落在第 k 格
        lo, hi = 0, len(cum)
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid] <= u:
                lo = mid + 1
            else:
                hi = mid
        i, j = flat[lo]
        counts[i][j] += 1
    return counts


def g2_independence(counts):
    """对数似然比独立性检验统计量 G²(=df=16 的卡方近似)。"""
    n = sum(map(sum, counts))
    row = [sum(r) for r in counts]
    col = [sum(counts[i][j] for i in range(5)) for j in range(5)]
    g = 0.0
    for i in range(5):
        for j in range(5):
            o = counts[i][j]
            e = row[i] * col[j] / n
            if o > 0:
                g += 2.0 * o * math.log(o / e)
    return g


def act1():
    print("=" * 84)
    print("幕一 代际流动表的两张面孔(两社会边际相同、流动强度不同;"
          f"五阶级边际={list(MARG)})")
    print("=" * 84)

    tab_a = ipf_diag_table(1.0)   # φ=1:独立性表
    tab_b = ipf_diag_table(PHI_MAIN)

    # ① 边际相同:逐格核到 1e-9 以下
    ga, gb = max_margin_gap(tab_a), max_margin_gap(tab_b)
    da, db = diag_share(tab_a), diag_share(tab_b)
    print(f"\n① 边际钉死:表 A(独立)与表 B(对角×{PHI_MAIN})的行/列边际"
          f"对 MARG 的最大偏差各 {ga:.2e}/{gb:.2e}(<1e-9)")
    print(f"   对角继承率:表 A={da:.4f}(=Σmᵢ²,独立世界的解析值"
          f"{sum(m * m for m in MARG):.4f}) → 表 B={db:.4f}")
    print(f"   流动率(非对角占比):表 A={1 - da:.4f} → 表 B={1 - db:.4f}")
    print(f"   两表联合分布相异度 D=0.5·Σ|a−b|={dissimilarity(tab_a, tab_b):.4f}"
          "——整整五分之一的父子对换了格子,边际纹丝不动")
    print("   ——同一个阶层结构比例,可以藏完全不同的开放度:边际是「结构」的")
    print("     画像,对角是「继承」的画像,两者是流动表的两个独立自由度")

    # ② 开放度参数 φ 扫描:继承率单调上升,边际全程钉死
    print(f"\n② 继承参数 φ 扫描(开放度是一个自由参数,边际管不着它):")
    diags = []
    for phi in PHI_SCAN:
        t = ipf_diag_table(phi)
        diags.append(diag_share(t))
        print(f"   φ={phi:>4}: 对角继承率={diags[-1]:.4f} "
              f"流动率={1 - diags[-1]:.4f} 边际偏差={max_margin_gap(t):.1e}")

    # ③ 抽样层复核:边际看不见、对角看得见
    rng_a = random.Random(SEED_BASE + 1000)
    rng_b = random.Random(SEED_BASE + 2000)
    ca = sample_counts(rng_a, tab_a, N_PAIR)
    cb = sample_counts(rng_b, tab_b, N_PAIR)
    sa = sum(ca[i][i] for i in range(5)) / N_PAIR
    sb = sum(cb[i][i] for i in range(5)) / N_PAIR
    se_diff = math.sqrt(sa * (1 - sa) / N_PAIR + sb * (1 - sb) / N_PAIR)
    z_diag = (sb - sa) / se_diff
    colsa = [sum(ca[i][j] for i in range(5)) / N_PAIR for j in range(5)]
    colsb = [sum(cb[i][j] for i in range(5)) / N_PAIR for j in range(5)]
    margin_gap = max(abs(x - y) for x, y in zip(colsa, colsb))
    g2a, g2b = g2_independence(ca), g2_independence(cb)
    print(f"\n③ 抽样层复核(各 {N_PAIR} 对父-子):")
    print(f"   样本对角继承率:A={sa:.4f} vs B={sb:.4f},差={sb - sa:.4f}"
          f" = {z_diag:.0f} 倍标准误(噪声内阈值≈3)")
    print(f"   样本列边际最大差:{margin_gap:.4f}(列边际差的标准误量级≈"
          f"{math.sqrt(0.3 * 0.7 / N_PAIR * 2):.4f})——边际完全看不出两个社会不同")
    print(f"   独立性检验 G²(df=16,5% 临界 {G2_CRIT_5PCT}):"
          f"表 A={g2a:.1f}(不拒独立) vs 表 B={g2b:.1f}(爆表)")
    print("   ——只看边际(「各阶级比例」)的社会比较是盲的:流动率之差全部")
    print("     藏在边际看不见的关联结构里")

    # 断言 1
    assert ga < 1e-9 and gb < 1e-9, "IPF 应把双边际钉到 1e-9 以下"
    assert abs(da - sum(m * m for m in MARG)) < 1e-6, "独立世界的对角=Σmᵢ²"
    assert db - da > 0.15, \
        f"同边际下两社会的继承率应差异巨大(实测 {da:.3f} vs {db:.3f})"
    assert all(diags[i] < diags[i + 1] for i in range(len(diags) - 1)), \
        "继承率应随 φ 单调上升(开放度是独立参数)"
    assert all(max_margin_gap(ipf_diag_table(p)) < 1e-9 for p in PHI_SCAN), \
        "φ 扫描全程边际钉死"
    assert z_diag > 8.0, f"样本对角差应远超 8 倍标准误(实测 {z_diag:.0f})"
    assert margin_gap < 0.05 and margin_gap < (sb - sa) / 4.0, \
        "样本边际差应在噪声内且远小于对角差"
    assert g2a < G2_CRIT_5PCT, f"表 A 样本不应拒独立性(G²={g2a:.1f})"
    assert g2b > 150.0, f"表 B 样本应强烈拒独立性(G²={g2b:.1f})"
    print(f"\n✓ 幕一断言通过:边际逐格相同(<1e-9)下继承率 {da:.3f}→{db:.3f}"
          f"(差 {db - da:.3f}),流动率 {1 - da:.3f}→{1 - db:.3f};"
          f"样本层对角差 {z_diag:.0f} 倍标准误而边际差 {margin_gap:.4f} 在噪声内;"
          f"G² {g2a:.0f}(过阈) vs {g2b:.0f}(爆表)")
    return dict(da=da, db=db)


# ==================== 幕二:SUTVA 与社区溢出 ====================

N_COMM = 60      # 社区数
N_IND = 40       # 每社区个体数(社区内环网络,每人左右各 1 邻居)
TAU = 1.0        # 干预的直接效应
SIGMA = 0.5      # 个体噪声标准差
THETA_LIST = (0.0, 0.15, 0.30, 0.50)   # 溢出强度(每受治邻居 θτ)
REPS2 = 12       # 每档重复数


def outcome(rng, treated_self, nb_treated, theta):
    """Y = τ·T + θτ·(受治邻居数) + ε:SUTVA 的违反写在第二项里。"""
    return TAU * treated_self + theta * TAU * nb_treated + rng.gauss(0.0, SIGMA)


def est_individual(rng, theta):
    """个体随机化:每个社区内部随机选一半人受治,合并处理-对照均值差。"""
    tot_t = tot_c = 0.0
    n_t = n_c = 0
    for _ in range(N_COMM):
        treat = set(rng.sample(range(N_IND), N_IND // 2))
        for i in range(N_IND):
            nb = ((i - 1) % N_IND in treat) + ((i + 1) % N_IND in treat)
            y = outcome(rng, i in treat, nb, theta)
            if i in treat:
                tot_t += y
                n_t += 1
            else:
                tot_c += y
                n_c += 1
    return tot_t / n_t - tot_c / n_c


def est_cluster(rng, theta):
    """社区随机化:一半社区全员受治、一半全员不治,社区间均值差。"""
    comm_t = set(rng.sample(range(N_COMM), N_COMM // 2))
    tot_t = tot_c = 0.0
    n_t = n_c = 0
    for c in range(N_COMM):
        full = c in comm_t
        # 全员受治时每人 2 个受治邻居;全不治时 0 个——溢出被完整计入组均值
        y_mean = (TAU + 2.0 * theta * TAU) if full else 0.0
        for _ in range(N_IND):
            y = y_mean + rng.gauss(0.0, SIGMA)
            if full:
                tot_t += y
                n_t += 1
            else:
                tot_c += y
                n_c += 1
    return tot_t / n_t - tot_c / n_c


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 SUTVA 与社区溢出(社区健康促进干预;直接效应 τ={TAU},"
          f"每受治邻居溢出 θτ;{N_COMM} 社区×{N_IND} 人,环网络;"
          f"各设计 {REPS2} 次重复)")
    print("=" * 84)
    print("  个体随机化=社区内各半受治,合并处理-对照均值差(忽略溢出的估计)")
    print("  社区随机化=整社区全治/全不治(溢出完整计入组均值)")
    print("  总效应基准=全治世界−全不治世界=τ(1+2θ)(每人 2 个受治邻居)")

    rows = []
    for k, theta in enumerate(THETA_LIST):
        ind = statistics.mean(
            est_individual(random.Random(SEED_BASE + 10000 + k * 100 + r), theta)
            for r in range(REPS2))
        clu = statistics.mean(
            est_cluster(random.Random(SEED_BASE + 20000 + k * 100 + r), theta)
            for r in range(REPS2))
        total = TAU * (1.0 + 2.0 * theta)
        bias = total - ind
        capture = ind / total
        rows.append((theta, ind, clu, total, bias, capture))
        print(f"\n  θ={theta:.2f}: 个体随机化估计={ind:+.3f}  "
              f"社区随机化估计={clu:+.3f}  总效应={total:.3f}")
        print(f"          个体设计的低估量={bias:.3f}(理论 2θτ={2 * theta:.3f});"
              f"个体估计只捕获总效应的 {capture:.0%}")

    print("\n读数:")
    print("  · θ=0(无溢出)两把尺量出同一个数——个体随机化没有原罪,")
    print("    它的罪只在溢出存在时才成立")
    print(f"  · θ>0:个体随机化稳定量到 τ={TAU}(直接效应),总效应却是 τ(1+2θ)")
    print("    ——处理组的邻居溢出与对照组的邻居溢出相互抵消,溢出被『平均掉』")
    print("    而不是被量到;低估量=2θτ 随 θ 单调增(θ=0.5 时丢掉一半)")
    print("  · 社区随机化全程命中总效应:整社区同进同退,溢出不再互相抵消")
    print("    ——社区是干预的单位,个体是测量的单位,拿错尺就量错布")

    # 断言 2
    by_theta = {r[0]: r for r in rows}
    r0 = by_theta[0.0]
    assert abs(r0[1] - TAU) < 0.05, "θ=0 个体随机化应无偏"
    assert abs(r0[2] - TAU) < 0.05, "θ=0 社区随机化应无偏"
    for r in rows[1:]:
        theta, ind, clu, total, bias, capture = r
        assert bias > 0.05, f"θ={theta} 个体设计应低估总效应(实测低估 {bias:.3f})"
        assert abs(bias - 2.0 * theta * TAU) < 0.06, \
            f"θ={theta} 低估量应≈2θτ(实测 {bias:.3f} vs 理论 {2 * theta:.3f})"
        assert abs(clu - total) < 0.06, \
            f"θ={theta} 社区随机化应命中总效应(实测 {clu:.3f} vs {total:.3f})"
    biases = [r[4] for r in rows]
    assert all(biases[i] < biases[i + 1] for i in range(len(biases) - 1)), \
        "低估量应随 θ 单调增"
    caps = [r[5] for r in rows]
    assert all(caps[i] > caps[i + 1] for i in range(len(caps) - 1)), \
        "个体估计的捕获率应随 θ 单调下降"
    assert by_theta[0.50][5] < 0.6, "θ=0.5 时个体估计应丢掉近半总效应"
    print(f"\n✓ 幕二断言通过:低估量随 θ 单调增("
          + ", ".join(f"{r[4]:.2f}" for r in rows) + "),与 2θτ 吻合;"
          "社区随机化全程命中总效应(偏差<0.06)")
    return rows


# ==================== 幕三:标签的放大回路 ====================

N_POP = 3000      # 人群规模
T_ROUNDS = 60     # 轮数
Q0 = 0.03         # 初始越轨倾向(每轮)
P_CATCH = 0.5     # 越轨后被捕概率(两环境相同——「同初始 p」)
EMP_DROP = 0.6    # 每次被捕:就业指数 ×0.6
Q_CAP = 0.95      # 越轨倾向上限
LATE = 10         # 「末十轮」窗口
LAMBDA_HIGH = 3.2  # 高标签环境:每次被捕 q×3.2
LAMBDA_LOW = 1.3   # 低标签环境:每次被捕 q×1.3
REPS3 = 6          # 每环境重复数


def run_env(rng, lam):
    """一个环境一条人群史:被捕→标签→就业×0.6、q×λ;返回逐人档案。"""
    q = [Q0] * N_POP
    caught = [0] * N_POP
    emp = [1.0] * N_POP
    late_dev = [0] * N_POP
    dev_total = 0
    late_start = T_ROUNDS - LATE
    for t in range(T_ROUNDS):
        for i in range(N_POP):
            if rng.random() < q[i]:
                dev_total += 1
                if t >= late_start:
                    late_dev[i] = 1
                if rng.random() < P_CATCH:
                    caught[i] += 1
                    emp[i] *= EMP_DROP
                    q[i] = min(Q_CAP, q[i] * lam)
    lab = [i for i in range(N_POP) if caught[i] >= 1]
    unl = [i for i in range(N_POP) if caught[i] == 0]
    lab3 = [i for i in range(N_POP) if caught[i] >= 3]
    return dict(
        recid=sum(late_dev[i] for i in lab) / max(len(lab), 1),
        base=sum(late_dev[i] for i in unl) / max(len(unl), 1),
        recid3=sum(late_dev[i] for i in lab3) / max(len(lab3), 1),
        dev_pc=dev_total / N_POP,
        catch_pc=sum(caught) / N_POP,
        emp_lab=statistics.mean(emp[i] for i in lab) if lab else 1.0,
        frac_lab=len(lab) / N_POP,
    )


def agg(lam, salt):
    runs = [run_env(random.Random(SEED_BASE + 30000 + salt * 1000 + r), lam)
            for r in range(REPS3)]
    return {k: statistics.mean(r[k] for r in runs) for k in runs[0]}


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 标签的放大回路(初级越轨→次级越轨;N={N_POP},T={T_ROUNDS} 轮,"
          f"q₀={Q0},被捕率 p={P_CATCH} 两环境相同;"
          f"被捕→就业×{EMP_DROP}、q×λ;各 {REPS3} 次重复)")
    print("=" * 84)

    high = agg(LAMBDA_HIGH, 0)   # 高标签环境
    low = agg(LAMBDA_LOW, 1)     # 低标签环境
    ctrl1 = agg(1.0, 2)          # 对照:两环境都无反馈(λ=1)
    ctrl2 = agg(1.0, 3)

    print(f"\n{'':>14}{'高标签(λ=%.1f)' % LAMBDA_HIGH:>16}"
          f"{'低标签(λ=%.1f)' % LAMBDA_LOW:>16}{'对照A(λ=1)':>12}{'对照B(λ=1)':>12}")
    for key, label in (("recid", "再越轨率(被捕过者,末十轮)"),
                       ("base", "底色(从未被捕者,末十轮)"),
                       ("recid3", "自锁(被捕≥3次者)"),
                       ("emp_lab", "被捕过者就业指数"),
                       ("dev_pc", "累计越轨(人均次)"),
                       ("catch_pc", "累计被捕(人均次)"),
                       ("frac_lab", "被捕过者占比")):
        print(f"{label:>16}{high[key]:>16.4f}{low[key]:>16.4f}"
              f"{ctrl1[key]:>12.4f}{ctrl2[key]:>12.4f}")

    d_recid = high["recid"] - low["recid"]
    d_ctrl = abs(ctrl1["recid"] - ctrl2["recid"])
    ratio_dev = high["dev_pc"] / low["dev_pc"]
    base_theory = 1.0 - ((1.0 - Q0) / (1.0 - Q0 * P_CATCH)) ** LATE
    print("\n读数:")
    print(f"  · 标签自锁:同初始 q、同被捕率 p,仅反应烈度不同——被捕过者的"
          f"末十轮再越轨率 {high['recid']:.2f} vs {low['recid']:.2f}"
          f"(差 {d_recid:.2f});被捕≥3 次者 {high['recid3']:.2f}")
    print(f"  · 累计越轨人均 {high['dev_pc']:.1f} vs {low['dev_pc']:.1f}"
          f"(×{ratio_dev:.1f})——刑罚的重量有一部分以再犯的形式回流:")
    print(f"    每次被捕把就业打到{int(EMP_DROP * 10)}折之外还把 q 乘上 λ,反馈回路让")
    print("    『惩罚』变成『培训』——越轨被抓得越狠的社会反应,产出越多的越轨")
    print(f"  · 对照(λ=1,无反馈):两独立环境再越轨率差 {d_ctrl:.4f}(噪声内)"
          "——差异全部由反馈制造,不由人群或运气制造")
    print(f"  · 底色不变:从未被捕者两环境各 {high['base']:.3f}/"
          f"{low['base']:.3f}(理论 {base_theory:.3f})——低于无条件的"
          f" 1−(1−q₀)^{LATE}={1 - (1 - Q0) ** LATE:.3f}:条件在「从未被捕」")
    print("    上会截掉末窗越轨(末窗越轨过的人更容易被捕而离组)——选择效应")
    print("    的活教材;但它对两环境同向同量,底色相同,全部差异集中在")
    print("    被标签碰过的人身上")

    # 断言 3
    assert d_recid > 0.30, \
        f"标签自锁:高标签环境再越轨率应显著更高(差 {d_recid:.3f})"
    assert high["recid3"] > 0.85, \
        f"被捕≥3 次者应近自锁(实测 {high['recid3']:.3f})"
    assert d_ctrl < 0.025, \
        f"无反馈对照两环境应无差(实测 {d_ctrl:.4f})"
    assert abs(high["base"] - low["base"]) < 0.03, \
        "从未被捕者的底色两环境应相同"
    assert abs(high["base"] - base_theory) < 0.015, \
        f"底色应≈选择校正后的理论值 {base_theory:.3f}"
    assert abs(low["base"] - base_theory) < 0.015, \
        f"低标签环境底色同样应≈{base_theory:.3f}"
    assert ratio_dev > 2.0, \
        f"高标签环境累计越轨应数倍于低标签(×{ratio_dev:.1f})"
    assert high["catch_pc"] > low["catch_pc"] + 0.1, \
        "反馈应推高累计被捕次数"
    assert high["emp_lab"] < low["emp_lab"] - 0.01, \
        "高标签环境被捕者的就业惩罚应更深"
    print(f"\n✓ 幕三断言通过:自锁差 {d_recid:.2f}(被捕≥3 次者 "
          f"{high['recid3']:.2f});对照无差 {d_ctrl:.4f};底色 "
          f"{high['base']:.3f}≈{low['base']:.3f}≈理论 "
          f"{base_theory:.3f};累计越轨 ×{ratio_dev:.1f}"
          "——标签理论的计算读法:反应烈度自变量,再犯率因变量")
    return high, low


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 流动表的两张面孔:边际逐格相同(<1e-9)之下,继承率与流动率")
    print("     可以完全不同(0.24 vs 0.45+),且差异随继承参数 φ 单调放大")
    print("     ——阶层结构比例是「结构」,出身-获得的关联是「流动」,两层各记各的账")
    print("  ② SUTVA 与社区溢出:θ>0 时个体随机化只量到直接效应,低估量=2θτ")
    print("     随 θ 单调增;社区随机化全程命中总效应——干预单位与测量单位")
    print("     必须同层,拿错尺就量错布")
    print("  ③ 标签的放大回路:同初始条件、同被捕率,仅社会反应烈度 λ 不同,")
    print("     即可制造再犯率的巨大分叉(λ=1 时两环境无差)——初级越轨与")
    print("     次级越轨之间隔着的不是个人品质,是反应的反馈回路")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
