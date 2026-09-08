# -*- coding: utf-8 -*-
"""连环-味论-物哀三律实验:东方文学(GB/T 75051)三个叙事/诗学机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-东方文学转代码.md(走廊 1/2/3)的配套实验。纯标准库
(math/random/statistics),无第三方依赖,固定种子 20260909 全程可复现。
参数为通说代表性案例的风格化参数(见各幕题注),模拟不冒充文学史计量。

与姊妹篇(讲透意大利文学 terza_rima_frames.py 幕二)的分工声明:那边对
意式并列框 vs 东方连环框只做了静态嵌套深度对照(深度中位/节点再生比);
本实验把"东方连环"推进为机制纵深——中断位×嵌套再生×饶命反馈的
夜夜动力学(买命读数),静态签名是本机制的不动点特例。

三幕:
  幕一 连环叙事的悬念复利机制(《一千零一夜》式)
      机制:每夜只讲最内层故事;新故事两夜式(夜A断于 policy 位,夜B收束);
      夜A断口处按 NEST_Q 概率再生嵌套新故事(外层线头冻结,隔夜衰减);
      王每夜听完按【夜末悬念存量】决定次日是否继续饶命(悬念换命)。
      断口未解张力 hang(p)=4p(1-p)·(1-p^3):前半=经典悬念倒U(太早未
      入局/太晚近解决都低),后半=晚断泄漏(断口太靠近解决,结局可猜)。
      通说锚:《一千零一夜》框架叙事(山鲁佐德夜夜讲故事买命,断在关键
      处),成书层积波斯-印度-埃及诸层(通说);两夜式与再生概率为风格化。
      断言:①最优中断位在中段(寿命-中断位倒U:中段期望寿命高于早断/
      晚断,曲线先爬坡后回落)②中断-续讲悬念存量跨夜累积(挂起线头复
      利:存量逐夜抬升),对照无中断连环(讲完再开,每夜存量清零)总存
      量与期望寿命均单调低——连环是利息,中断是复利:山鲁佐德用叙事结
      构买命。
  幕二 味论(rasa)与情感空间(梵语戏剧学八味,风格化)
      机制:八味置于效价-唤起二维空间(罗素环形情感模型风格化;婆罗多
      《舞论》八味:爱/笑/奇/勇/怒/惧/厌/悲,通说;第九"平静味"为后世
      所增,通说)。混味场景=主味r1+随味r2:观众唤起点=r1+β(r2-r1)+噪
      声,按最近味归类;主味唤起=最近恰为主味,随味显影=次近恰为随味。
      卷入度:欣赏度 A(e)=1-κ(e-e*)^2,最优卷入 e*=1-0.75×唤起(高唤起
      味要审美距离,低唤起味要怀抱——"审美距离"论的可算读法)。
      断言:①相邻味对的主味唤起率与随味显影率均>相对味对(甜-悲不相容
      的戏曲学:爱-悲为空间最远对,主味被挤占)②每种味有最优卷入档
      (逐味倒U;估出 ê* 与唤起严格负相关=斯皮尔曼≤-0.8),卷入校准读
      者总欣赏≥统一卷入读者 1.2×。
  幕三 物哀(mono no aware)的敏感度曲线
      机制:物哀=对易逝之物的审美敏感。对象价值 V(L)=形式(L)×哀感(L)
      =L^2/(L^2+c^2)×e^(-L/τ):太短暂无形式可凝视(昙花一现),太长久
      无哀感可触发(松柏千年)。读者敏感度 s:叙事 30 章中事件峰在终章
      (x^3),结束信号审美核 x^2√(1-x) 峰在 0.8T(将尽未尽处);高 s 读
      者的审美赋值向结束信号核加权(终章审美峰前移)。
      通说锚:"物哀"说出自本居宣长对《源氏物语》的解读(通说);樱花
      七日为日本审美文化的通说形象;《源氏物语》成书 11 世纪初(紫式部
      日记 1008 年条已提及,通说)。
      断言:①审美价值-预期寿命曲线倒U:峰值寿命落在中段(樱花七日区
      间),V(7日)≫V(昙花0.25日)且≫V(松柏3650日)②高敏感组终章审美峰
      位置<低敏感组(前移≥1.5章)且总审美赋值更高——物哀是给时间装上
      敏感器。

跑法: python -u experiments/frame_rasa_nights.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现

# ==================== 幕一:连环叙事的悬念复利机制 ====================

N_CAP = 120                     # 寿命上限(夜)——"买命"读数的封顶
Q0, THETA = 0.50, 3.0           # 王的基线饶命 / 悬念换命阈值
NEST_Q = 0.55                   # 断口处再生嵌套新故事的概率
M_DECAY = 0.90                  # 冻结线头(当夜未被讲述)的隔夜记忆衰减
R_REP = 3000                    # 每策略蒙特卡洛副本数
POLICIES = [0.05, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 0.97]  # 中断位扫描
POLICY_MID = 0.45               # 峰值位(断言锚)


def hang(p):
    """断口未解张力:4p(1-p) 经典悬念倒U × (1-p^3) 晚断泄漏(结局可猜度)。"""
    return 4.0 * p * (1.0 - p) * (1.0 - p ** 3)


def sim_nights(policy, rng, n_nights, interrupt=True):
    """夜夜动力学。interrupt=True:两夜式中断-续讲+断口嵌套再生;
    interrupt=False:无中断连环(讲完再开,每夜一个完整故事,存量恒零)。
    返回 (夜末存量序列, 嵌套深度序列, 存活标志序列)。"""
    stack = []          # 线头栈:元素 {"t": 当前张力, "nest": 断口是否再生嵌套}
    stocks, depths, alives = [], [], []
    for _ in range(n_nights):
        if interrupt:
            if not stack:                       # 开讲新的顶层故事(夜A)
                stack.append({"t": hang(policy),
                              "nest": rng.random() < NEST_Q})
            else:
                top = stack[-1]
                if top["nest"]:                 # 昨夜断口再生:今晚讲嵌套新故事
                    stack.append({"t": hang(policy),
                                  "nest": rng.random() < NEST_Q})
                else:                           # 夜B:收束,最内层线头解决
                    stack.pop()
            for th in stack[:-1]:               # 冻结线头隔夜衰减
                th["t"] *= M_DECAY
            stock = sum(th["t"] for th in stack)
        else:                                   # 讲完再开:当夜收束,存量清零
            stock = 0.0
        stocks.append(stock)
        depths.append(len(stack) if interrupt else 0)
        p_spare = min(1.0, Q0 + stock / THETA)  # 王的饶命判定
        alive = rng.random() < p_spare
        alives.append(alive)
        if not alive:
            break
    return stocks, depths, alives


def mean_lifetime(policy, rng, rep, interrupt=True):
    """期望寿命(夜):R_REP 个副本的平均(存活到 N_CAP 封顶)。"""
    lifes = []
    for _ in range(rep):
        _, _, alives = sim_nights(policy, rng, N_CAP, interrupt)
        lifes.append(len(alives))               # 存活夜数=断在最后一夜
    return stats.mean(lifes)

def act1():
    print("=" * 84)
    print(f"幕一 连环叙事的悬念复利({R_REP} 副本/策略,中断位扫描,风格化参数)")
    print("=" * 84)

    # ---- 断言 1:最优中断位在中段(寿命-中断位倒U) ----
    lifetimes = []
    for i, pol in enumerate(POLICIES):
        rng = random.Random(SEED + 1000003 * i + 7)
        lifetimes.append(mean_lifetime(pol, rng, R_REP))
    print("\n中断位 policy → 期望寿命(夜):")
    for pol, life in zip(POLICIES, lifetimes):
        bar = "#" * int(life / 3)
        print(f"  p*={pol:<5} → {life:6.1f} 夜  {bar}")
    peak = lifetimes.index(max(lifetimes))
    assert POLICIES[peak] == POLICY_MID, \
        f"峰值中断位应在中段 {POLICY_MID}:{POLICIES[peak]}"
    lm, l_early, l_late = lifetimes[peak], lifetimes[1], lifetimes[-2]
    assert lm > 1.5 * l_early and lm > 1.5 * l_late, \
        f"中段应>1.5×早断/晚断:{lm:.1f} vs {l_early:.1f}/{l_late:.1f}"
    ups = [lifetimes[i + 1] - lifetimes[i] for i in range(peak)]
    downs = [lifetimes[i + 1] - lifetimes[i] for i in range(peak, len(POLICIES) - 1)]
    assert all(d > 0 for d in ups), "峰值前应单调爬坡"
    assert all(d < 0 for d in downs), "峰值后应单调回落"
    print(f"\n✓ 幕一断言①通过:倒U——峰值在 p*={POLICY_MID}(期望寿命 "
          f"{lm:.1f} 夜),早断 p*=0.15 仅 {l_early:.1f} 夜、晚断 p*=0.90 仅 "
          f"{l_late:.1f} 夜;太早未入局(hang={hang(0.15):.3f})、太晚近解决且"
          f"结局可猜(hang={hang(0.90):.3f}),中段断口张力 hang={hang(POLICY_MID):.3f} 最大")

    # ---- 断言 2:存量跨夜复利累积 vs 无中断连环每夜清零 ----
    rng = random.Random(SEED + 999)
    traj_int, depths_all = [], []
    for _ in range(400):                        # 中断式轨迹(条件存活,前 30 夜)
        st, dp, al = sim_nights(POLICY_MID, rng, 30, True)
        if len(st) == 30 and all(al):
            traj_int.append(st)
            depths_all.append(dp)
    assert len(traj_int) >= 100, f"30 夜全存活的副本应≥100:{len(traj_int)}"
    mean_stock = [stats.mean(x) for x in zip(*traj_int)]
    mean_depth = stats.mean([stats.mean(d) for d in depths_all])
    med_depth = stats.median([max(d) for d in depths_all])
    first3 = stats.mean(mean_stock[:10])
    last3 = stats.mean(mean_stock[-10:])
    assert mean_stock[0] > 0 and all(s > 0 for s in mean_stock), "中断式存量恒>0"
    assert last3 > 1.3 * first3, \
        f"后段存量应>1.3×前段(复利累积):{last3:.3f} vs {first3:.3f}"
    assert all(mean_stock[i] < mean_stock[i + 4] for i in range(0, 26, 4)), \
        "存量应逐段抬升"
    rng = random.Random(SEED + 998)
    life_noint = mean_lifetime(0.5, rng, R_REP, interrupt=False)
    rng = random.Random(SEED + 997)
    life_int = mean_lifetime(POLICY_MID, rng, R_REP, interrupt=True)
    assert life_noint < 0.25 * N_CAP and life_int > 0.3 * N_CAP, \
        f"无中断连环应早亡({life_noint:.1f}),中断式应长寿({life_int:.1f})"
    ratio = life_int / life_noint
    assert ratio >= 15, f"中断/无中断寿命比应≥15×:{ratio:.1f}"
    print(f"\n中断式(p*={POLICY_MID})夜末悬念存量均值:第1夜 {mean_stock[0]:.2f}"
          f" → 第30夜 {mean_stock[-1]:.2f}(前1/3 均值 {first3:.2f} → 后1/3 "
          f"{last3:.2f},{last3 / first3:.2f}×);嵌套深度均值 {mean_depth:.2f}、"
          f"最深中位 {med_depth:.0f} 层")
    print(f"对照无中断连环(讲完再开):夜末存量恒为 0(每夜清零,单利);"
          f"期望寿命 {life_noint:.1f} 夜 vs 中断式 {life_int:.1f} 夜"
          f"({ratio:.0f}×)")
    print(f"\n✓ 幕一断言②通过:挂起线头跨夜复利(存量逐段抬升 "
          f"{first3:.2f}→{last3:.2f}),无中断连环每夜清零、寿命仅其 "
          f"{1 / ratio:.0%}——连环是利息,中断是复利:山鲁佐德用叙事结构买命")
    return {"peak_pol": POLICIES[peak], "life_peak": lm,
            "life_early": l_early, "life_late": l_late,
            "first3": first3, "last3": last3, "depth": mean_depth,
            "med_depth": med_depth, "life_noint": life_noint,
            "life_int": life_int, "ratio": ratio}

# ==================== 幕二:味论(rasa)与情感空间 ====================

# 八味坐标(效价 v∈[-1,1], 唤起 a∈[0,1];罗素环形情感模型风格化)
RASAS = {
    "爱(śṛṅgāra)": (0.85, 0.45),
    "笑(hāsya)":    (0.65, 0.70),
    "奇(adbhuta)":  (0.40, 0.85),
    "勇(vīra)":     (0.35, 0.90),
    "怒(raudra)":   (-0.60, 0.95),
    "惧(bhayānaka)": (-0.75, 0.80),
    "厌(bībhatsa)": (-0.55, 0.50),
    "悲(karuṇa)":   (-0.80, 0.30),
}
SIGMA, BETA = 0.28, 0.26     # 观众唤起噪声 / 随味拉力
M_AUD = 3000                 # 每味对观众样本数
KAPPA = 6.0                  # 卷入失配代价


def dist(x, y):
    return math.hypot(x[0] - y[0], x[1] - y[1])


def pair_sets():
    """相邻对:每味最近的两味;相对对:每味最远的一味(去重)。
    返回按味名元组全序排列(与哈希随机化无关,保证跨进程可复现)。"""
    names = list(RASAS)
    adj, opp = set(), set()
    for n in names:
        ds = sorted((dist(RASAS[n], RASAS[m]), m) for m in names if m != n)
        for _, m in ds[:2]:
            adj.add(frozenset((n, m)))
        opp.add(frozenset((n, ds[-1][1])))
    key = lambda s: tuple(sorted(s))          # 全序键:消除并列依赖
    return sorted(adj, key=key), sorted(opp - adj, key=key)


def evocation(r1, r2, rng, m=M_AUD):
    """混味场景唤起模拟:返回 (主味唤起率, 随味显影率)。"""
    c1, c2 = RASAS[r1], RASAS[r2]
    names = list(RASAS)
    dom = aux = 0
    for _ in range(m):
        ex = c1[0] + BETA * (c2[0] - c1[0]) + rng.gauss(0, SIGMA)
        ey = c1[1] + BETA * (c2[1] - c1[1]) + rng.gauss(0, SIGMA)
        ranked = sorted(names, key=lambda n: dist((ex, ey), RASAS[n]))
        if ranked[0] == r1:
            dom += 1
            if ranked[1] == r2:
                aux += 1
    return dom / m, aux / m


def spearman(xs, ys):
    """斯皮尔曼秩相关(手排秩,无第三方库)。"""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = float(pos)
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = stats.mean(rx), stats.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) *
                    sum((b - my) ** 2 for b in ry))
    return num / den


def appreciate(rasa, e):
    """欣赏度 A(e)=1-κ(e-e*)²,e*=1-0.75×唤起(下限 0)。"""
    a = RASAS[rasa][1]
    return max(0.0, 1.0 - KAPPA * (e - (1.0 - 0.75 * a)) ** 2)


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 味论与情感空间(八味效价-唤起风格化,每对 {M_AUD} 观众)")
    print("=" * 84)

    # ---- 断言 1:相邻味相容 > 相对味(甜-悲不相容) ----
    rng = random.Random(SEED + 20)
    adj, opp = pair_sets()
    res = {}
    for pair in adj + opp:
        r1, r2 = sorted(pair)
        res[(r1, r2)] = evocation(r1, r2, rng)
    adj_dom = stats.mean(res[tuple(sorted(p))][0] for p in adj)
    adj_aux = stats.mean(res[tuple(sorted(p))][1] for p in adj)
    opp_dom = stats.mean(res[tuple(sorted(p))][0] for p in opp)
    opp_aux = stats.mean(res[tuple(sorted(p))][1] for p in opp)
    love, sorrow = "爱(śṛṅgāra)", "悲(karuṇa)"
    lb = res[(love, sorrow)] if (love, sorrow) in res else \
        res[(sorrow, love)]
    print(f"\n相邻味对({len(adj)} 对):主味唤起率均值 {adj_dom:.3f},"
          f"随味显影率均值 {adj_aux:.3f}")
    print(f"相对味对({len(opp)} 对):主味唤起率均值 {opp_dom:.3f},"
          f"随味显影率均值 {opp_aux:.3f}")
    print(f"甜-悲对(爱-悲,空间最远 d={dist(RASAS[love], RASAS[sorrow]):.3f}):"
          f"主味唤起率 {lb[0]:.3f},随味显影率 {lb[1]:.3f}——主味被第三味挤占")
    assert adj_dom > opp_dom + 0.10, \
        f"相邻主味唤起率应>相对+0.10:{adj_dom:.3f} vs {opp_dom:.3f}"
    assert adj_aux > 1.5 * opp_aux, \
        f"相邻随味显影率应>1.5×相对:{adj_aux:.3f} vs {opp_aux:.3f}"
    assert frozenset((love, sorrow)) in opp, "爱-悲应为相对味对"
    assert lb[0] < 0.85 * adj_dom and lb[1] < 0.2 * adj_aux, \
        f"甜-悲应显著劣于相邻均值:{lb[0]:.3f} vs {adj_dom:.3f};" \
        f"{lb[1]:.3f} vs {adj_aux:.3f}"
    print(f"\n✓ 幕二断言①通过:相邻组合相容度>相对(唤起 {adj_dom:.3f}>"
          f"{opp_dom:.3f},显影 {adj_aux:.3f}>{opp_aux:.3f});甜-悲最远对"
          f"主味唤起仅 {lb[0]:.3f}——八味空间有几何,不是任意混搭")

    # ---- 断言 2:每种味有最优卷入档(高唤起要距离/低唤起要怀抱) ----
    names = list(RASAS)
    arousal = [RASAS[n][1] for n in names]
    e_grid = [i / 20 for i in range(21)]        # 卷入度网格 0..1 步长 0.05
    rng = random.Random(SEED + 21)
    seq = names * 3                               # 24 场混味戏码:八味各 3 场
    rng.shuffle(seq)
    for n in names:
        assert seq.count(n) == 3, "每种味应恰 3 场"
    noise = {(i, e): rng.gauss(0, 0.08)
             for i in range(len(seq)) for e in range(len(e_grid))}
    e_hat = []
    for n in names:                            # 逐味网格寻优(带噪欣赏度)
        idx = [i for i, s in enumerate(seq) if s == n]
        curve = [stats.mean(appreciate(n, e) + noise[(i, k)]
                            for i in idx) for k, e in enumerate(e_grid)]
        e_hat.append(e_grid[curve.index(max(curve))])
    rho = spearman(e_hat, arousal)
    for n, eh, ar in zip(names, e_hat, arousal):
        best = 1.0 - 0.75 * ar
        assert abs(eh - best) <= 0.12, \
            f"{n} 估出最优卷入 {eh} 应贴近理论 {best:.2f}"
        assert appreciate(n, best) - appreciate(n, best - 0.3) >= 0.3 and \
            appreciate(n, best) - appreciate(n, best + 0.3) >= 0.3, \
            f"{n} 应有倒U(±0.3 卷入掉价≥0.3)"
    unif = stats.mean(appreciate(n, 0.5) for n in seq)
    calib = stats.mean(appreciate(n, 1.0 - 0.75 * RASAS[n][1]) for n in seq)
    print(f"\n逐味最优卷入档(网格寻优):")
    for n, eh, ar in zip(names, e_hat, arousal):
        print(f"  {n}:唤起 {ar:.2f} → 最优卷入 ê*≈{eh:.2f}"
              f"(理论 {1 - 0.75 * ar:.2f})")
    print(f"ê* 与唤起的斯皮尔曼秩相关 ρ={rho:.2f}(严格负);24 场戏码总欣赏:"
          f"统一卷入 0.50 → {unif:.3f},逐味校准 → {calib:.3f}"
          f"({calib / unif:.2f}×)")
    assert rho <= -0.8, f"ê* 与唤起应强负相关:{rho:.2f}"
    assert calib >= 1.2 * unif, \
        f"卷入校准应≥1.2×统一卷入:{calib:.3f} vs {unif:.3f}"
    print(f"\n✓ 幕二断言②通过:每种味有最优卷入档(怒/惧/勇高唤起要距离,"
          f"悲/爱低唤起要怀抱,ρ={rho:.2f}),校准读者总欣赏 {calib / unif:.2f}×"
          f"于统一卷入——古典诗论的可计算读法")
    return {"adj_dom": adj_dom, "opp_dom": opp_dom, "adj_aux": adj_aux,
            "opp_aux": opp_aux, "lb_dom": lb[0], "rho": rho,
            "unif": unif, "calib": calib}

# ==================== 幕三:物哀的敏感度曲线 ====================

C_FORM, TAU = 4.0, 12.0       # 形式饱和常数 / 哀感衰减时间(日)
CHERRY, EPH, PINE = 7.0, 0.25, 3650.0   # 樱花七日 / 昙花一现 / 松柏十年
T_CH = 30                      # 叙事总章数
S_BOOST = 2.0                  # 敏感读者的结束信号核加权


def value(L):
    """物哀审美价值 V(L)=形式(L)×哀感(L):L^2/(L^2+c^2) × e^(-L/τ)。"""
    return (L * L / (L * L + C_FORM * C_FORM)) * math.exp(-L / TAU)


def reader_curve(s, rng, t_ch=T_CH):
    """读者在 t 章上的审美赋值曲线(带章间噪声):
    (1-s)·事件峰 x^3 + s·S_BOOST·结束信号核 x^2√(1-x)。"""
    curve = []
    for t in range(1, t_ch + 1):
        x = t / t_ch
        w = (1 - s) * x ** 3 + s * S_BOOST * x * x * math.sqrt(1 - x)
        curve.append(w * (1 + rng.gauss(0, 0.02)))
    return curve


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 物哀的敏感度曲线(V(L)=L²/(L²+{C_FORM:.0f})·e^(-L/{TAU:.0f}),风格化)")
    print("=" * 84)

    # ---- 断言 1:审美价值-预期寿命倒U(樱花七日胜过两极) ----
    grid = [0.25 * i for i in range(1, 241)]    # 0.25 .. 60 日
    vals = [value(L) for L in grid]
    L_peak = grid[vals.index(max(vals))]
    v_ch, v_eph, v_pine = value(CHERRY), value(EPH), value(PINE)
    marks = [("昙花一现(0.25日)", EPH), ("樱花七日(7日)", CHERRY),
             ("百日红(100日)", 100.0), ("松柏十年(3650日)", PINE)]
    print("\n预期寿命 L → 物哀价值 V(L):")
    for name, L in marks:
        v = value(L)
        bar = "#" * int(v / max(vals) * 46)
        print(f"  {name:<16} V={v:.4f}  {bar}")
    print(f"  峰值寿命 L*={L_peak:.2f} 日(中段),V_max={max(vals):.4f}")
    assert 5.0 <= L_peak <= 9.0, f"峰值寿命应落在中段(樱花七日区间):{L_peak}"
    assert v_ch >= 0.98 * max(vals), \
        f"樱花七日应≥0.98×峰值:{v_ch:.4f} vs {max(vals):.4f}"
    assert v_ch >= 50 * v_eph, \
        f"樱花应≥50×昙花:{v_ch:.4f} vs {v_eph:.4f}(太短暂无形式)"
    assert v_ch >= 1e5 * v_pine, \
        f"樱花应≥1e5×松柏:{v_ch:.4f} vs {v_pine:.2e}(太长久无哀感)"
    ups = [vals[i + 1] - vals[i] for i in range(0, vals.index(max(vals)))]
    downs = [vals[i + 1] - vals[i]
             for i in range(vals.index(max(vals)), len(vals) - 1)]
    assert all(d > 0 for d in ups) and all(d < 0 for d in downs), \
        "V(L) 应先升后降(倒U)"
    print(f"\n✓ 幕三断言①通过:倒U——峰值 L*={L_peak:.1f} 日落在中段,V(七日)"
          f"={v_ch:.4f}≈峰值;昙花 {v_eph:.4f}(无形式可凝视)、松柏 "
          f"{v_pine:.2e}(无哀感可触发)两极皆塌——樱花七日胜过昙花一现与松柏千年")

    # ---- 断言 2:高敏感读者终章审美峰前移 ----
    rng = random.Random(SEED + 30)
    readers = [rng.betavariate(2, 2) for _ in range(400)]   # 敏感度分布
    med = stats.median(readers)
    hi = [s for s in readers if s >= med]
    lo = [s for s in readers if s < med]
    assert len(hi) >= 150 and len(lo) >= 150
    peaks_hi, peaks_lo, totals = [], [], {}
    for grp, store in ((hi, peaks_hi), (lo, peaks_lo)):
        for s in grp:
            curve = reader_curve(s, rng)
            store.append(curve.index(max(curve)) + 1)       # 峰章(1 起)
            totals.setdefault(grp is hi, []).append(sum(curve))
    ph, pl = stats.mean(peaks_hi), stats.mean(peaks_lo)
    th, tl = stats.mean(totals[True]), stats.mean(totals[False])
    print(f"\n高敏感组(s≥中位 {med:.2f},n={len(hi)}):审美峰均值第 {ph:.1f} 章,"
          f"总赋值均值 {th:.2f}")
    print(f"低敏感组(s<中位,n={len(lo)}):审美峰均值第 {pl:.1f} 章,"
          f"总赋值均值 {tl:.2f}")
    print(f"峰前移 {pl - ph:.1f} 章;总赋值比 {th / tl:.2f}×"
          f"(事件峰在第 {T_CH} 章,结束信号核峰在 0.8T=第 24 章)")
    assert ph < pl - 1.5, \
        f"高敏感组审美峰应前移≥1.5 章:{ph:.1f} vs {pl:.1f}"
    assert ph < 0.9 * T_CH, f"高敏感组峰应在终章前:{ph:.1f}"
    assert th > tl, f"高敏感组总赋值应更高:{th:.2f} vs {tl:.2f}"
    print(f"\n✓ 幕三断言②通过:高敏感读者审美峰前移({pl:.1f}→{ph:.1f}章,"
          f"移 {pl - ph:.1f} 章)且总赋值 {th / tl:.2f}×——终章未至,哀感先行:"
          f"物哀是给时间装上敏感器")
    return {"L_peak": L_peak, "v_ch": v_ch, "v_eph": v_eph,
            "v_pine": v_pine, "peak_hi": ph, "peak_lo": pl,
            "total_hi": th, "total_lo": tl}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 连环悬念复利:倒U峰值 p*={r1['peak_pol']}(寿命 "
          f"{r1['life_peak']:.0f} 夜 vs 早断 {r1['life_early']:.0f}/晚断 "
          f"{r1['life_late']:.0f});存量复利 {r1['first3']:.2f}→{r1['last3']:.2f},"
          f"无中断连环寿命 {r1['life_noint']:.0f} 夜(1/{r1['ratio']:.0f})"
          f"——中断是复利")
    print(f"  ② 味论空间:相邻唤起 {r2['adj_dom']:.3f}>相对 {r2['opp_dom']:.3f},"
          f"显影 {r2['adj_aux']:.3f}>{r2['opp_aux']:.3f},甜-悲 {r2['lb_dom']:.3f};"
          f"ê*-唤起 ρ={r2['rho']:.2f},校准 {r2['calib'] / r2['unif']:.2f}×"
          f"——每味有最优卷入档")
    print(f"  ③ 物哀曲线:峰值寿命 {r3['L_peak']:.1f} 日(七日≈峰值 "
          f"{r3['v_ch']:.3f});终章审美峰 {r3['peak_lo']:.1f}→{r3['peak_hi']:.1f} 章"
          f"前移——易逝装上敏感器")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
