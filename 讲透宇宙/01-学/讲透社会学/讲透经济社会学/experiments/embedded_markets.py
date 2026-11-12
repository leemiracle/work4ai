# -*- coding: utf-8 -*-
"""嵌入市场三幕实验:嵌入的交易治理 / 弱关系的非冗余信息 / r>g 的财富分化机器。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(三张结构卡的可构造端)、
04-经济社会学转代码.md(三条走廊)的配套实验。纯标准库(math/random/statistics),
无第三方依赖。

三幕:
  幕一 嵌入的交易治理——信任的两种价钱(封闭买安全,桥接买机会):
      60 名交易者,15% 机会主义者(永远背叛),其余互惠者(条件合作:不与
      自己黑名单上的人交易,配对时优先老主顾);欺诈(合作遇背叛)信息沿
      网络边传播——被欺诈者及其邻居未来都拒绝与欺诈者交易;合作成功的
      交易会沉淀为关系(网络加边),关系又开启新的引荐。三种市场结构各跑
      300 轮:匿名市场(每轮随机配对、无声誉记忆、无关系沉淀)、封闭网络
      (6 个 10 人街区,街区内环形 4 邻居)、桥接网络(同封闭,但 15% 的
      边重连到随机远方)。断言:①嵌入网络(封闭/桥接)长期合作率显著高于
      匿名市场——嵌入是治理机器,不是道德装饰;②封闭与桥接的合作率相当,
      但新配对形成率(新交易伙伴探索率)封闭显著更低——高聚类用新机会
      换安全,桥接用弱纪律换机会。
  幕二 弱关系的非冗余信息——结构洞的载体:
      96 人分 16 个亲友圈(每圈 6 人,圈内全连=强关系),另设 40 条跨圈
      远程弱关系(仅占全部边的 ~14%)。每轮,上一轮新知情者以 β=0.7 向
      每个邻居播报一次「新机会」(单次播报);60 次广播取平均,并对照
      「全部拆除弱边」的世界。断言:①首次到达经由弱边的占比显著高于
      弱边占比(约 1.6 倍)——少数弱边抢下超额的首达;②弱边路径的冗余
      重复到达率显著低于强边路径(差 15 个百分点以上)——强关系圈里
      同一条消息转一圈又回到你耳边;③拆除全部弱边,消息出不了源圈子
      (覆盖率 ~18% vs 保留弱边 ~99%)——你 cousin 的同事知道的事,
      你的强关系圈永远不知道。
  幕三 r>g 的财富分化机器——不平等只由收益率结构产生:
      5000 个家户各持两本账户:金融资本账户(期初对数正态,中位数 100,
      σ=0.8,每期复利 r=5%±0.8% 小噪声)与劳动积累账户(人人等额 100,
      每期随经济增速 g=2% 累积)。总财富=两本账户之和,模拟 100 期。
      断言:①前 10% 财富占比(资本存量份额)单调上升;②基尼系数单调
      上升;③对照 r=g=2% 时两指标基本平稳——没有任何「贪婪」行为,
      分化完全由收益率结构这台机器产生(资本按 r 复利且期初集中,
      劳动按 g 增长且人人等额)。

跑法: python -u experiments/embedded_markets.py
"""

import math
import random
import statistics

# ==================== 幕一:嵌入的交易治理 ====================

N_AGENTS = 60
N_ROUNDS = 300
OPP_FRAC = 0.15     # 机会主义者比例(永远背叛)
EXPLORE = 0.08      # 每次配对时尝试「请邻居引荐新伙伴」的概率
BLOCK = 10          # 街区规模(封闭网络)
REWIRE = 0.15       # 桥接网络的重连比例


def build_block_network(n, block, rng, rewire_p):
    """街区制网络:每街区内环形 4 邻居;rewire_p>0 时按概率把边重连到随机远方节点。"""
    edges = set()
    for b in range(n // block):
        base = b * block
        for i in range(block):
            for d in (1, 2):
                a, c = base + i, base + (i + d) % block
                edges.add((min(a, c), max(a, c)))
    if rewire_p > 0.0:
        for e in sorted(edges):
            if rng.random() < rewire_p:
                a, _ = e
                edges.discard(e)
                while True:
                    w = rng.randrange(n)
                    if w != a and (min(a, w), max(a, w)) not in edges:
                        edges.add((min(a, w), max(a, w)))
                        break
    nbrs = {i: set() for i in range(n)}
    for a, c in edges:
        nbrs[a].add(c)
        nbrs[c].add(a)
    return nbrs


def run_market(condition, seed, n=N_AGENTS, rounds=N_ROUNDS, opp_frac=OPP_FRAC,
               explore=EXPLORE, block=BLOCK, rewire_p=REWIRE):
    """跑一种市场结构。

    嵌入条件:配对沿网络进行;被欺诈者及其邻居拉黑欺诈者;合作成功的
    交易沉淀为关系边(网络生长)。匿名条件:每轮随机配对、无声誉记忆、
    无关系沉淀。返回:长期合作率、新配对率、欺诈事件总数、机会主义者
    末段交易参与率(均对末 50 轮平均)。
    """
    rng = random.Random(seed)
    ops = set(rng.sample(range(n), round(n * opp_frac)))
    if condition == "anonymous":
        nbrs = {i: set() for i in range(n)}
    else:
        nbrs = build_block_network(n, block, rng,
                                   rewire_p if condition == "bridging" else 0.0)
    blacklist = {i: set() for i in range(n)}   # blacklist[i]=i 拒绝与之交易的人
    traded = set()                             # 历史上交易过的配对
    tail_coop, tail_new, tail_opp = [], [], []
    fraud_total = 0
    for rnd in range(rounds):
        order = list(range(n))
        rng.shuffle(order)
        matched = set()
        rnd_c = rnd_tr = rnd_new = rnd_opp = 0
        for i in order:
            if i in matched:
                continue
            j = None
            if condition == "anonymous":
                pool = [x for x in range(n) if x not in matched and x != i]
                if pool:
                    j = rng.choice(pool)
            else:
                if rng.random() < explore:
                    # 探索:请邻居引荐一位「我没交易过」的新伙伴
                    for u in rng.sample(sorted(nbrs[i]), len(nbrs[i])):
                        cand = [w for w in nbrs[u]
                                if w != i and w not in matched
                                and (min(i, w), max(i, w)) not in traded
                                and w not in blacklist[i]
                                and i not in blacklist[w]]
                        if cand:
                            j = rng.choice(cand)
                            break
                if j is None:
                    # 常规:在可交易的邻居里优先老主顾(重复交易=信任惯性)
                    cand = [w for w in nbrs[i] if w not in matched
                            and w not in blacklist[i]
                            and i not in blacklist[w]]
                    if cand:
                        old = [w for w in cand
                               if (min(i, w), max(i, w)) in traded]
                        j = rng.choice(old) if old else rng.choice(cand)
            if j is None:
                continue                      # 本轮无人可配,坐观
            matched.update((i, j))
            key = (min(i, j), max(i, j))
            rnd_tr += 1
            if key not in traded:
                rnd_new += 1
                traded.add(key)
            if i in ops or j in ops:
                rnd_opp += 1
            ai = "D" if i in ops else "C"
            aj = "D" if j in ops else "C"
            rnd_c += (ai == "C") + (aj == "C")
            # 结算:被背叛者拉黑欺诈者;嵌入网络中信息沿边传播给其邻居
            for x, y, ax, ay in ((i, j, ai, aj), (j, i, aj, ai)):
                if ay == "D":
                    if ax == "C":
                        fraud_total += 1
                    if condition != "anonymous":
                        blacklist[x].add(y)
                        for nb in nbrs[x]:
                            blacklist[nb].add(y)
            # 合作成功的交易沉淀为关系(网络生长),关系开启新的引荐
            if condition != "anonymous" and ai == "C" and aj == "C":
                nbrs[i].add(j)
                nbrs[j].add(i)
        if rnd >= rounds - 50 and rnd_tr:
            tail_coop.append(rnd_c / (2 * rnd_tr))
            tail_new.append(rnd_new / rnd_tr)
            tail_opp.append(rnd_opp / rnd_tr)
    coop = statistics.mean(tail_coop)
    new_rate = statistics.mean(tail_new)
    opp_active = statistics.mean(tail_opp)
    return coop, new_rate, fraud_total, opp_active


def act1():
    print("=" * 84)
    print("幕一 嵌入的交易治理:信任的两种价钱(封闭买安全,桥接买机会)")
    print("=" * 84)
    coop_a, new_a, fraud_a, act_a = run_market("anonymous", 8404411)
    coop_c, new_c, fraud_c, act_c = run_market("closed", 8404412)
    coop_b, new_b, fraud_b, act_b = run_market("bridging", 8404413)
    n_opp = round(N_AGENTS * OPP_FRAC)
    print(f"\n{N_AGENTS} 名交易者(机会主义者 {n_opp} 人={OPP_FRAC:.0%},永远背叛;")
    print(f"其余互惠者:不与自己黑名单上的人交易,优先老主顾),{N_ROUNDS} 轮;")
    print(f"嵌入网络中欺诈信息沿边传播,合作成功的交易沉淀为关系边;")
    print(f"配对时以 {EXPLORE:.0%} 概率请邻居引荐新伙伴(探索)。末 50 轮计指标。")
    print(f"\n  {'市场结构':<8}{'长期合作率':>10}{'新配对率':>9}{'欺诈事件':>9}{'欺诈者末段交易参与率':>16}")
    rows = (("匿名市场", coop_a, new_a, fraud_a, act_a),
            ("封闭网络", coop_c, new_c, fraud_c, act_c),
            ("桥接网络", coop_b, new_b, fraud_b, act_b))
    for name, coop, new, fraud, act in rows:
        print(f"  {name:<8}{coop:>10.1%}{new:>9.1%}{fraud:>9}{act:>16.1%}")

    # 断言 1a:嵌入网络(封闭)长期合作率显著高于匿名市场
    assert coop_c - coop_a > 0.05, f"封闭网络合作率应显著高于匿名({coop_c:.3f} vs {coop_a:.3f})"
    # 断言 1b:嵌入网络(桥接)长期合作率显著高于匿名市场
    assert coop_b - coop_a > 0.05, f"桥接网络合作率应显著高于匿名({coop_b:.3f} vs {coop_a:.3f})"
    # 断言 1c:封闭与桥接的合作率相当,但新配对率封闭显著更低
    assert abs(coop_c - coop_b) < 0.05, f"封闭与桥接合作率应相当({coop_c:.3f} vs {coop_b:.3f})"
    assert new_c < 0.02, f"封闭网络新配对率应趋近于 0,实测 {new_c:.4f}"
    assert new_b > 0.05 and new_b > 4 * max(new_c, 1e-4), \
        f"桥接网络新配对率应显著高于封闭({new_b:.4f} vs {new_c:.4f})"
    assert act_a > 0.2 and act_c < 0.02 and act_b < 0.1, \
        "匿名市场欺诈者应照常交易,嵌入网络中应被排斥出局"

    print("\n读数:")
    print(f"  · 匿名市场:每轮随机配对+无声誉记忆,欺诈者换着 victim 骗了 {fraud_a} 次,")
    print(f"    末段仍有 {act_a:.0%} 的交易有其参与,合作率被钉在互惠者占比")
    print(f"    {1 - OPP_FRAC:.0%}——市场不惩罚背叛,背叛就成了理性策略")
    print(f"  · 封闭网络:被骗一次,受害者的邻居全部拉黑欺诈者(信息沿边传播),")
    print(f"    欺诈者骗了 {fraud_c} 次后无人再与其交易(末段参与率 {act_c:.1%})——")
    print("    嵌入把「下次再骗」的价格抬到无处可骗,合作率逼近全员互惠")
    print(f"  · 桥接网络:少数重连边让引荐源源不断带来新伙伴({new_b:.1%} vs 封闭")
    print(f"    {new_c:.1%} 的新配对率),陌生配对偶尔踩雷,合作率仅略降")
    print(f"    ({coop_b:.1%} vs {coop_c:.1%})")
    print("  · 格兰诺维特式权衡的最小机器:封闭与桥接的合作率相当,但封闭的")
    print("    新交易伙伴探索率几乎为零——信任的两种价钱:封闭买安全,桥接买机会")
    print(f"\n✓ 幕一断言通过:嵌入合作率(封闭 {coop_c:.1%}/桥接 {coop_b:.1%})均显著高于"
          f"匿名({coop_a:.1%});封闭与桥接相当,而新配对率 {new_c:.1%} ≪ {new_b:.1%}")
    return rows


# ==================== 幕二:弱关系的非冗余信息 ====================


def diffuse(adj, sources, rng, beta, n, max_rounds=40):
    """一次广播:上一轮新知情者向每个邻居以 beta 概率播报一次(单次播报模型)。

    返回:首达计数(弱/强)、接收计数(弱/强)、冗余计数(弱/强)、90% 覆盖轮数、覆盖率。
    """
    informed = set(sources)
    frontier = list(sources)
    first = {"weak": 0, "strong": 0}
    recv = {"weak": 0, "strong": 0}
    redun = {"weak": 0, "strong": 0}
    t90 = None
    rounds = 0
    while frontier and rounds < max_rounds:
        rounds += 1
        nxt = []
        for u in frontier:
            for v, typ in adj[u]:
                if rng.random() < beta:
                    recv[typ] += 1
                    if v in informed:
                        redun[typ] += 1       # 重复到达:目标早已知情
                    else:
                        informed.add(v)
                        first[typ] += 1       # 首次到达
                        nxt.append(v)
        frontier = nxt
        if t90 is None and len(informed) >= 0.9 * n:
            t90 = rounds
    return first, recv, redun, t90, len(informed) / n


def act2():
    print("\n" + "=" * 84)
    print("幕二 弱关系的非冗余信息:结构洞的载体(你圈子外的事,强关系永远不知道)")
    print("=" * 84)
    n, clique, n_weak, beta, episodes = 96, 6, 40, 0.7, 60
    rng = random.Random(8404420)
    strong = set()                      # 16 个亲友圈,每圈 6 人圈内全连
    for b in range(n // clique):
        base = b * clique
        for i in range(clique):
            for j in range(i + 1, clique):
                strong.add((base + i, base + j))
    tot = dict(fw=0, fs=0, rw=0, rs=0, dw=0, ds=0)
    t90_full, cov_full, cov_so, weak_counts = [], [], [], []
    for _ in range(episodes):
        weak = set()                     # 40 条跨圈远程弱关系
        for i in rng.sample(range(n), n_weak):
            w = (i + rng.randint(10, n - 10)) % n
            if w != i:
                weak.add((min(i, w), max(i, w)))
        weak -= strong
        weak_counts.append(len(weak))
        sources = rng.sample(range(n), 3)
        adj_full = {i: [] for i in range(n)}
        for a, c in strong:
            adj_full[a].append((c, "strong"))
            adj_full[c].append((a, "strong"))
        for a, c in weak:
            adj_full[a].append((c, "weak"))
            adj_full[c].append((a, "weak"))
        adj_so = {i: [] for i in range(n)}     # 对照世界:全部拆除弱边
        for a, c in strong:
            adj_so[a].append((c, "strong"))
            adj_so[c].append((a, "strong"))
        first, recv, redun, t90, cov = diffuse(adj_full, sources, rng, beta, n)
        tot["fw"] += first["weak"]; tot["fs"] += first["strong"]
        tot["rw"] += recv["weak"]; tot["rs"] += recv["strong"]
        tot["dw"] += redun["weak"]; tot["ds"] += redun["strong"]
        t90_full.append(t90 if t90 is not None else 40)
        cov_full.append(cov)
        _, _, _, _, cov2 = diffuse(adj_so, sources, rng, beta, n)
        cov_so.append(cov2)

    n_strong = len(strong)
    mean_weak = statistics.mean(weak_counts)
    weak_share = mean_weak / (n_strong + mean_weak)
    first_total = tot["fw"] + tot["fs"]
    first_weak_share = tot["fw"] / first_total
    redun_rate_weak = tot["dw"] / tot["rw"]
    redun_rate_strong = tot["ds"] / tot["rs"]
    cov_full_mean = statistics.mean(cov_full)
    cov_so_mean = statistics.mean(cov_so)

    print(f"\n{n} 人分 {n // clique} 个亲友圈(每圈 {clique} 人,圈内全连={n_strong} 条强边);")
    print(f"另设 {n_weak} 条跨圈远程弱关系(去重后平均 {mean_weak:.0f} 条,占全部边 "
          f"{weak_share:.0%});")
    print(f"每轮新知情者以 β={beta} 向每个邻居播报一次「新机会」(单次播报);"
          f"{episodes} 次广播平均。")
    print(f"\n  弱边占全部边的比例:{weak_share:.1%}")
    print(f"  首次到达经由弱边的比例:{first_weak_share:.1%}"
          f"(={first_weak_share / weak_share:.2f} 倍于其边数占比;共 {first_total} 次首达)")
    print(f"  冗余重复到达率——弱边路径:{redun_rate_weak:.1%}"
          f"(重复 {tot['dw']}/接收 {tot['rw']})")
    print(f"                        强边路径:{redun_rate_strong:.1%}"
          f"(重复 {tot['ds']}/接收 {tot['rs']})")
    print(f"  最终覆盖率——保留弱边:{cov_full_mean:.0%}(90% 覆盖平均需 "
          f"{statistics.mean(t90_full):.1f} 轮)")
    print(f"              拆除弱边:{cov_so_mean:.0%}(消息出不了源圈子,等多少轮都没用)")

    # 断言 2a:首达经由弱边的占比显著高于弱边占比(1.4 倍以上)
    assert first_weak_share > 1.4 * weak_share, \
        f"弱边首达占比 {first_weak_share:.3f} 应显著高于弱边占比 {weak_share:.3f}"
    # 断言 2b:弱边路径的冗余率显著低于强边路径(比例不足八成,差距超 15 个百分点)
    assert redun_rate_weak < 0.8 * redun_rate_strong, \
        f"弱边冗余率 {redun_rate_weak:.3f} 应显著低于强边 {redun_rate_strong:.3f}"
    assert redun_rate_strong - redun_rate_weak > 0.15, "冗余率差距应超过 15 个百分点"
    # 断言 2c:拆除全部弱边,消息出不了源圈子
    assert cov_full_mean > 0.9 and cov_so_mean < 0.25, \
        f"保留弱边覆盖率 {cov_full_mean:.3f} 应高,拆除弱边 {cov_so_mean:.3f} 应低"

    print("\n读数:")
    print(f"  · 弱边只占 {weak_share:.0%} 的边,却拿下 {first_weak_share:.0%} 的首次到达"
          f"(边数占比的 {first_weak_share / weak_share:.1f} 倍)——强关系圈里")
    print("    大家迟早都知道同一批事,新信息几乎总是从圈外的弱边跳进来")
    print(f"  · 强边接收里 {redun_rate_strong:.0%} 是重复(消息在圈内转一圈又回到")
    print(f"    你耳边),弱边只有 {redun_rate_weak:.0%}——弱关系通向的是「你")
    print("    otherwise 听不到」的人:这就是非冗余,伯特说的结构洞,")
    print("    格兰诺维特说的弱关系的力量")
    print(f"  · 最狠的对照:拆除全部弱边,消息永远出不了那 3 个源圈子")
    print(f"    (覆盖率 {cov_so_mean:.0%} vs {cov_full_mean:.0%})——圈与圈之间")
    print("    没有弱关系,信息就是圈内的回音。求职信息如此,新机会如此:")
    print("    「你 cousin 的同事知道的事,你的强关系圈永远不知道」")
    print(f"\n✓ 幕二断言通过:弱边首达占比 {first_weak_share:.1%}>1.4×弱边占比 {weak_share:.1%};"
          f"冗余率 {redun_rate_weak:.1%}≪强边 {redun_rate_strong:.1%};"
          f"拆除弱边覆盖率塌到 {cov_so_mean:.0%}")
    return first_weak_share, weak_share, redun_rate_weak, redun_rate_strong


# ==================== 幕三:r>g 的财富分化机器 ====================


def gini(sorted_x):
    """基尼系数(输入须升序排序)。"""
    n = len(sorted_x)
    cum = 0.0
    for i, x in enumerate(sorted_x, 1):
        cum += i * x
    total = sum(sorted_x)
    return (2.0 * cum) / (n * total) - (n + 1.0) / n


def top10_share(sorted_x):
    """前 10% 财富占比(输入须升序排序)。"""
    n = len(sorted_x)
    k = n // 10
    return sum(sorted_x[n - k:]) / sum(sorted_x)


def run_wealth(seed, n=5000, periods=100, r=0.05, g=0.02, noise=0.008):
    """两本账户的最小 r>g 机器:资本账户(期初对数正态,中位数 100)复利 r±noise;
    劳动账户(人人等额 100)随增速 g 累积。返回逐期(前 10% 份额, 基尼)序列。"""
    rng = random.Random(seed)
    mu, sigma = math.log(100.0), 0.8
    capital = [math.exp(mu + sigma * rng.gauss(0.0, 1.0)) for _ in range(n)]
    labor = 100.0
    series = []
    for t in range(periods + 1):
        wealth = sorted(k + labor for k in capital)
        series.append((top10_share(wealth), gini(wealth)))
        if t == periods:
            break
        for i in range(n):
            capital[i] *= 1.0 + r + rng.gauss(0.0, noise)
        labor *= 1.0 + g
    return series


def act3():
    print("\n" + "=" * 84)
    print("幕三 r>g 的财富分化机器:不引入任何「贪婪」,分化只由收益率结构产生")
    print("=" * 84)
    treat = run_wealth(8404430)                    # r=5% > g=2%
    ctrl = run_wealth(8404440, r=0.02, g=0.02)     # 对照 r=g=2%
    s10, gn = [p[0] for p in treat], [p[1] for p in treat]
    s10c, gnc = [p[0] for p in ctrl], [p[1] for p in ctrl]

    print("\n  5000 个家户×两本账户:金融资本(期初对数正态,中位数 100,σ=0.8,")
    print("  每期复利 r±0.8% 小噪声)+劳动积累(人人等额 100,每期×(1+g));")
    print("  总财富=两本账户之和;模拟 100 期,固定种子。")
    print(f"\n  {'期数':>4} | {'r>g 前10%份额':>12} {'r>g 基尼':>9} | "
          f"{'r=g 前10%份额':>12} {'r=g 基尼':>9}")
    for t in (0, 20, 40, 60, 80, 100):
        print(f"  {t:>4} | {s10[t]:>12.4f} {gn[t]:>9.4f} | {s10c[t]:>12.4f} {gnc[t]:>9.4f}")

    # 断言 3a:r>g 时前 10% 财富占比逐期单调上升
    assert all(a < b for a, b in zip(s10, s10[1:])), "前 10% 份额应单调上升"
    # 断言 3b:r>g 时基尼系数逐期单调上升
    assert all(a < b for a, b in zip(gn, gn[1:])), "基尼系数应单调上升"
    # 断言 3c:对照 r=g 时两指标基本平稳(变动不到 r>g 情形的十分之一)
    d10, dgn = s10[-1] - s10[0], gn[-1] - gn[0]
    d10c, dgnc = abs(s10c[-1] - s10c[0]), abs(gnc[-1] - gnc[0])
    assert d10 > 0.05 and dgn > 0.10, f"r>g 应显著分化(Δ份额 {d10:.4f}, Δ基尼 {dgn:.4f})"
    assert d10c < 0.01 and dgnc < 0.01, f"r=g 应基本平稳(Δ {d10c:.4f}, Δ {dgnc:.4f})"
    assert d10 > 10 * max(d10c, 1e-6) and dgn > 10 * max(dgnc, 1e-6)

    print(f"\n读数:")
    print(f"  · r=5%>g=2%:前 10% 份额 {s10[0]:.3f}→{s10[-1]:.3f}(+{d10:.3f}),")
    print(f"    基尼 {gn[0]:.3f}→{gn[-1]:.3f}(+{dgn:.3f}),100 期步步单调上升")
    print(f"  · 对照 r=g=2%:前 10% 份额仅动 {d10c:.4f},基尼仅动 {dgnc:.4f}——")
    print("    两本账户同速增长,分布形状原样放大,不平等纹丝不动")
    print("  · 机关:资本账户复利 5% 且期初集中,劳动账户增长 2% 且人人等额;")
    print("    r>g 使总财富分布逐期向资本分布收敛——前 10% 份额单调爬向")
    print("    资本自身的集中度。全程没有一个「贪婪」参数:不偷不抢不囤积,")
    print("    每个家户都做同样的两件事(持有资本、积累劳动),分化完全由")
    print("    收益率结构产生——皮凯蒂不等式的最小计算模型")
    print(f"\n✓ 幕三断言通过:r>g 时份额与基尼双双单调上升(Δ=+{d10:.3f}/+{dgn:.3f}),"
          f"r=g 时基本平稳(Δ={d10c:.4f}/{dgnc:.4f})")
    return s10, gn, s10c, gnc


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 嵌入治理:嵌入网络合作率(封闭/桥接)显著高于匿名市场——欺诈信息")
    print("     沿网络边传播把背叛的价格抬到无处可骗;而封闭与桥接合作率相当、")
    print("     新配对率封闭≪桥接——信任的两种价钱:封闭买安全,桥接买机会")
    print("  ② 弱关系的力量:占边数 14% 的弱边拿下 23% 的首次到达(1.6 倍超额),")
    print("     冗余率显著低于强边;拆除弱边消息出不了源圈子——弱关系是信息")
    print("     结构洞的载体;新机会从圈外跳进来")
    print("  ③ r>g 分化机器:前 10% 份额与基尼逐期单调上升,r=g 对照基本平稳——")
    print("     不需要贪婪,收益率结构本身就是分化机器")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
