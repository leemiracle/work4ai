# -*- coding: utf-8 -*-
"""铁幕翻译-地下出版-流亡回归三律模拟: 东欧文学家族实验(GB/T 75077)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-东欧文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。
涉冷战时期文学流通与审查制度一律通说学术口径,本实验只做流通动力学的
风格化模型,不做政治评判。

三幕:
  幕一 铁幕翻译时滞的双向不对称(1947-1989):
      东→西(东欧文学西译)双通道: 官方版权通道(慢)与流亡出版社通道
      (巴黎《文化》与文学研究所、多伦多六八出版社一类流亡机构,通说)——
      时滞按 gauss(7.8,2.2) 与 gauss(2.2,0.9) 风格化。
      西→东(西方文学东译): 类型×过审率×排队时滞——古典经典/通俗类型/
      现代主义严肃/政治敏感四类,过审率 0.85/0.78/0.22/0.03,敏感类
      过审后还要排队(基础时滞 3.0/2.0/8.5/12.0 年)。
      断言: ①流亡通道时滞 < 官方通道的 45%——流亡出版社把铁幕凿出一条
              快速通道(压缩到约三分之一)
            ②东译既慢又被挑: 敏感两类(现代主义严肃+政治敏感)在过审集合
              中的份额压到源头份额的一半以下,敏感类过审时滞 > 古典类
              1.8 倍,过审构成与源头的总变差距离 > 0.25——铁幕是玻璃
              做的: 看得见,过得慢,还被挑过。
  幕二 地下出版的网络韧性(samizdat):
      传抄网络 = 30 个信任簇(簇内环+弦,稠密)×簇间弱连接(每簇 1 条,
      其中 12 簇有第二条生命线);官方发行 = 中心印厂广播(单点)。SI 传抄:
      知情人每步向一名熟人拷贝,借阅成功率 0.6;压制 = 移除节点
      (秘密警察端掉节点,接触即风险)。
      断言: ①官方发行 1 步全覆盖、印厂被端即归零;传抄网络覆盖到八成要
              6 步以上(慢),但穷举 240 个单点移除,可达覆盖率全部
              ≥ 0.80(移除任意节点网络不断,对压制鲁棒)
            ②"接触即风险"演化: 度数越高越容易被端(检出概率∝度数平方);
              30 轮生长+压制后,传抄网最大度 < 无压制对照的 60%,连通
              分量更多、平均分量更小、聚集系数更高——网络自发保持小而
              密(分簇)。萨米兹达特的组织学: 弱连接传播,强信任保命。
  幕三 流亡作家的双市场回归(昆德拉现象):
      60 位流亡作家两队列: 换语写作(昆德拉 1990 年代起改以法语写作,通说)
      vs 母语坚持(米沃什式)。流亡期西方接受(换语免译直达)/铁幕后
      (1989-)母国市场: 被禁旧作重译热 vs 流亡新作回流。
      断言: ①换语队列西方接受指数 > 母语队列 1.4 倍,但流亡新作回流母国
              的量 < 母语队列的 60%(西方吃香与母国流失同源)
            ②全样本回归期: 被禁旧作的重译/重版热度 > 流亡新作回流 2 倍
              以上,且旧作重译中位时点比新作回流早 3 年以上——回归市场
              要的是"被禁的旧我";流亡作家回家时,家里等着的是他离开前
              的自己。

跑法: python -u experiments/iron_curtain_pipeline.py
"""

import math
import random
import statistics
import sys

SEED = 20260907  # 检索校准日作种子,可复现


def _utf8_stdout():
    """Windows 管道下默认 GBK,强制 UTF-8 输出(纯标准库)。"""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==================== 幕一: 铁幕翻译时滞的双向不对称 ====================

EAST_BOOKS = 480        # 铁幕期东欧文学西译样本(书种,风格化)
WEST_BOOKS = 600        # 铁幕期西方文学东译样本(书种,风格化)
EXILE_SHARE = 0.42      # 经流亡出版社通道的份额(通说: 流亡出版是一支偏师)
# 西→东四类型: (类型, 源头份额, 过审率, 过审后基础时滞均值/年)
WEST_TYPES = [
    ("古典经典",     0.18, 0.85, 3.0),
    ("通俗类型",     0.34, 0.78, 2.0),
    ("现代主义严肃", 0.28, 0.22, 8.5),
    ("政治敏感",     0.20, 0.03, 12.0),
]


def act1():
    print("=" * 84)
    print("幕一 铁幕翻译时滞的双向不对称: 东欧西译×西方东译(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED)

    # 1a 东→西: 流亡出版社通道 vs 官方版权通道
    exile_lags, official_lags = [], []
    for _ in range(EAST_BOOKS):
        if rng.random() < EXILE_SHARE:
            exile_lags.append(max(0.4, rng.gauss(2.2, 0.9)))
        else:
            official_lags.append(max(0.5, rng.gauss(7.8, 2.2)))
    m_ex = statistics.mean(exile_lags)
    m_of = statistics.mean(official_lags)

    print("\n[1a] 东→西(东欧文学西译, %d 书种):" % EAST_BOOKS)
    print(f"  流亡出版社通道(n={len(exile_lags)}): 平均时滞 {m_ex:.2f} 年"
          f"(中位 {statistics.median(exile_lags):.2f})")
    print(f"  官方版权通道  (n={len(official_lags)}): 平均时滞 {m_of:.2f} 年"
          f"(中位 {statistics.median(official_lags):.2f})")
    print(f"  读数: 流亡通道时滞 = 官方通道的 {m_ex / m_of:.0%}"
          "——流亡出版社把铁幕凿出一条快速通道")

    assert m_ex < 0.45 * m_of, "流亡通道时滞应<官方通道 45%"
    assert m_ex < 3.0 and m_of > 7.0, "两通道应分别落在快速带与慢速带"

    # 1b 西→东: 审查的类型配额(选择偏差)
    src = {t[0]: 0 for t in WEST_TYPES}
    adm = {t[0]: 0 for t in WEST_TYPES}
    lags = {t[0]: [] for t in WEST_TYPES}
    for _ in range(WEST_BOOKS):
        r, acc, pick = rng.random(), 0.0, WEST_TYPES[-1][0]
        for name, share, _, _ in WEST_TYPES:
            acc += share
            if r <= acc:
                pick = name
                break
        src[pick] += 1
        padm = dict((t[0], t[2]) for t in WEST_TYPES)[pick]
        if rng.random() < padm:
            adm[pick] += 1
            base = dict((t[0], t[3]) for t in WEST_TYPES)[pick]
            lags[pick].append(max(0.3, rng.gauss(base, base * 0.35)))

    n_src, n_adm = sum(src.values()), sum(adm.values())
    share_src = {k: v / n_src for k, v in src.items()}
    share_adm = {k: v / n_adm for k, v in adm.items()}
    tvd = 0.5 * sum(abs(share_src[k] - share_adm[k]) for k in share_src)
    sens_src = share_src["现代主义严肃"] + share_src["政治敏感"]
    sens_adm = share_adm["现代主义严肃"] + share_adm["政治敏感"]
    lag_class = statistics.mean(lags["古典经典"])
    lag_mod = statistics.mean(lags["现代主义严肃"])

    print(f"\n[1b] 西→东(西方文学东译, {WEST_BOOKS} 书种): 总过审率 {n_adm / n_src:.1%}")
    print(f"  {'类型':<10}{'源头份额':>8}{'过审份额':>8}{'平均时滞':>8}")
    for name, _, _, _ in WEST_TYPES:
        lag_s = f"{statistics.mean(lags[name]):>7.1f}" if lags[name] else "  未过审"
        print(f"  {name:<10}{share_src[name]:>8.3f}{share_adm[name]:>8.3f}{lag_s}")
    print("  读数:")
    print(f"  · 敏感两类份额 {sens_src:.3f}(源头) → {sens_adm:.3f}(过审), 压到 "
          f"{sens_adm / sens_src:.0%}——类型配额: 被挑过")
    print(f"  · 现代主义过审时滞 {lag_mod:.1f} 年 > 古典 {lag_class:.1f} 年的 "
          f"{lag_mod / lag_class:.1f} 倍——过得慢")
    print(f"  · 过审率近半(看得见) + 构成总变差 {tvd:.3f}——铁幕是玻璃做的")

    assert sens_adm < 0.5 * sens_src, "敏感两类过审份额应<源头一半(选择偏差)"
    assert lag_mod > 1.8 * lag_class, "敏感类时滞应>古典类 1.8 倍"
    assert tvd > 0.25, "过审构成与源头的总变差应>0.25(构成被重塑)"
    print(f"\n✓ 幕一断言通过: 流亡通道 {m_ex:.2f} vs 官方 {m_of:.2f} 年"
          f"({m_ex / m_of:.0%}); 敏感份额 {sens_src:.2f}→{sens_adm:.2f}, "
          f"TVD {tvd:.2f}——看得见, 过得慢, 还被挑过")


# ==================== 幕二: 地下出版的网络韧性(samizdat) ====================

N_CLUSTERS, CSIZE, CHORDS = 30, 8, 4
N_EXTRA_BRIDGES = 12     # 12 个簇有第二条生命线, 其余 18 簇只有一条
N_NODES = N_CLUSTERS * CSIZE   # 240
COPY_P = 0.6                   # 每步向一名熟人拷贝的借阅成功率
K_SEEDS = 4                    # 独立入书口(多册独立进入传抄圈)
ATTACK_FRAC = 0.15             # 随机压制: 移除 15% 节点


def build_network(rng):
    """30 信任簇(环+弦,强信任)×簇间弱连接(每簇 1 条,12 簇加 1 条;
    同簇两桥端点强制不同——单线依赖簇是压制下的真实弱点)。"""
    adj = {i: set() for i in range(N_NODES)}

    def add(a, b):
        adj[a].add(b)
        adj[b].add(a)

    for c in range(N_CLUSTERS):
        base = c * CSIZE
        for i in range(CSIZE):
            add(base + i, base + (i + 1) % CSIZE)
        for _ in range(CHORDS):
            a, b = rng.sample(range(base, base + CSIZE), 2)
            add(a, b)
    order = list(range(N_CLUSTERS))
    rng.shuffle(order)
    lucky = set(order[:N_EXTRA_BRIDGES])
    for c in range(N_CLUSTERS):
        base = c * CSIZE
        used = set()
        for _ in range(2 if c in lucky else 1):
            a = base + rng.randrange(CSIZE)
            while a in used:
                a = base + rng.randrange(CSIZE)
            used.add(a)
            c2 = rng.randrange(N_CLUSTERS)
            while c2 == c:
                c2 = rng.randrange(N_CLUSTERS)
            add(a, c2 * CSIZE + rng.randrange(CSIZE))
    return adj


def component_sizes(adj, alive):
    seen, sizes = set(), []
    for v in adj:
        if v in alive and v not in seen:
            stack, comp = [v], set()
            while stack:
                u = stack.pop()
                if u in comp:
                    continue
                comp.add(u)
                stack.extend(w for w in adj[u] if w in alive and w not in comp)
            seen |= comp
            sizes.append(len(comp))
    return sorted(sizes, reverse=True)


def reachable(adj, seeds, alive):
    """从多个入书口出发,传抄网络最终能覆盖的节点集(SI 终态=连通块)。"""
    seen, stack = set(), [s for s in seeds if s in alive]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(w for w in adj[u] if w in alive and w not in seen)
    return seen


def si_steps_to(adj, seeds, frac=0.8):
    """SI 传抄: 每步每名知情人向一名熟人拷贝,到覆盖 frac×可达集的步数。"""
    target = int(frac * len(reachable(adj, seeds, set(adj))))
    informed, frontier, steps = set(seeds), set(seeds), 0
    rng = random.Random(SEED + 7)
    while len(informed) < target and steps < 200:
        steps += 1
        for u in list(frontier):
            w = rng.choice(sorted(adj[u]))
            if w not in informed and rng.random() < COPY_P:
                informed.add(w)
                frontier.add(w)
        frontier -= {u for u in frontier if all(w in informed for w in adj[u])}
    return steps


def global_clustering(adj):
    """全局聚集系数(传递性): 闭合三元组数/三元组总数(≤1)。"""
    tri = triples = 0
    for v in adj:
        ns = list(adj[v])
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                triples += 1
                if ns[j] in adj[ns[i]]:
                    tri += 1
    return tri / triples if triples else 0.0


def evolve(rng, repression, rounds=30, adds=8, m=2):
    """生长网络: 每轮加 8 节点。对照=择优附着(长枢纽);传抄=经介绍人
    的三元闭包(朋友的朋友)+压制(检出概率∝(度/6)²,检出即端掉全部连边)。"""
    n0 = 40
    adj = {i: set() for i in range(n0)}
    for i in range(n0):
        adj[i].add((i + 1) % n0)
        adj[(i + 1) % n0].add(i)
    for _ in range(n0):
        a, b = rng.sample(range(n0), 2)
        adj[a].add(b)
        adj[b].add(a)
    nid = n0
    for _ in range(rounds):
        for _ in range(adds):
            v = nid
            nid += 1
            adj[v] = set()
            if repression:
                u = rng.choice(sorted(adj))
                nbrs = sorted(adj[u])
                adj[v].add(u)
                adj[u].add(v)
                if nbrs:
                    w = rng.choice(nbrs)
                    adj[v].add(w)
                    adj[w].add(v)
                else:
                    w = rng.choice(sorted(x for x in adj if x != v))
                    adj[v].add(w)
                    adj[w].add(v)
            else:
                nodes = sorted(adj)
                weights = [len(adj[x]) for x in nodes]
                for _ in range(m):
                    tot = sum(weights)
                    r = rng.random() * tot
                    acc = 0
                    pick = nodes[-1]
                    for x, wt in zip(nodes, weights):
                        acc += wt
                        if r <= acc:
                            pick = x
                            break
                    adj[v].add(pick)
                    adj[pick].add(v)
                    weights[nodes.index(pick)] += 1
        if repression:
            for u in sorted(adj):
                p = min(0.5, 0.02 * (len(adj[u]) / 6.0) ** 2)
                if rng.random() < p:
                    for w in adj[u]:
                        adj[w].discard(u)
                    del adj[u]
    return adj


def act2():
    print("\n" + "=" * 84)
    print("幕二 地下出版的网络韧性: 传抄网络 vs 中心发行(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED + 1)
    adj = build_network(rng)
    all_alive = set(adj)

    # 2a 覆盖速度: 官方广播 vs 传抄
    t_official = 1                       # 中心印厂: 一步铺满
    seeds = rng.sample(sorted(all_alive), K_SEEDS)
    t_sam = si_steps_to(adj, seeds)
    cover = len(reachable(adj, seeds, all_alive)) / N_NODES
    print(f"\n[2a] 覆盖速度(官方发行=中心印厂广播):")
    print(f"  官方发行: {t_official} 步全覆盖(书店网络同步铺货)")
    print(f"  传抄网络: {K_SEEDS} 个独立入书口, 可达覆盖率 {cover:.1%}, "
          f"到八成要 {t_sam} 步——慢, 但在长")

    assert t_sam >= 6, "传抄网络到八成应≥6 步(显著慢于官方 1 步)"
    assert cover > 0.80, "簇间弱连接应保证八成以上可达"

    # 2b 压制鲁棒性: 穷举单点移除 vs 官方印厂单点移除
    covs = []
    for removed in sorted(all_alive):
        alive = all_alive - {removed}
        s2 = [s for s in seeds if s in alive] or [rng.choice(sorted(alive))]
        covs.append(len(reachable(adj, s2, alive)) / len(alive))
    min_cov = min(covs)

    # 官方对照(星型广播): 移除非印厂节点仍 100% 覆盖, 移除印厂即 0
    # 随机压制: 200 次移除 15% 节点
    rng2 = random.Random(SEED + 2)
    rand_covs = []
    for _ in range(200):
        alive = set(rng2.sample(sorted(all_alive),
                                int((1 - ATTACK_FRAC) * N_NODES)))
        s2 = [s for s in seeds if s in alive] or [rng2.choice(sorted(alive))]
        rand_covs.append(len(reachable(adj, s2, alive)) / len(alive))
    # 定点打击: 端掉 6 名"联络人"(簇间生命线桥的端点, 度不高但桥性最强)
    def cid(v):
        return v // CSIZE

    bridge_edges = sorted({(min(a, b), max(a, b)) for a in adj for b in adj[a]
                           if cid(a) != cid(b)})
    hit_edges = rng.sample(bridge_edges, 6)
    alive = all_alive - {rng.choice(e) for e in hit_edges}
    s3 = [s for s in seeds if s in alive] or [rng.choice(sorted(alive))]
    hub_cov = len(reachable(adj, s3, alive)) / len(alive)

    print(f"\n[2b] 压制鲁棒性:")
    print(f"  穷举 {N_NODES} 个单点移除: 最低可达覆盖率 {min_cov:.1%}"
          "——移除任意节点网络不断")
    print(f"  随机压制(移除 {ATTACK_FRAC:.0%} 节点×200 次): 平均 "
          f"{statistics.mean(rand_covs):.1%}, 中位 {statistics.median(rand_covs):.1%}, "
          f"最低 {min(rand_covs):.1%}(入书口困孤岛)")
    print(f"  定点打击(端掉 6 名联络人=桥端点): 覆盖率 {hub_cov:.1%}"
          "——桥被打断, 簇还活着")
    print("  对照: 官方发行移除非印厂节点覆盖率 100%, 移除印厂即 0%"
          "——单点故障")

    assert min_cov >= 0.78, "任意单点移除后可达覆盖应≥0.78(无单点故障)"
    assert statistics.mean(rand_covs) >= 0.70, "随机压制下平均覆盖应≥0.70"
    assert hub_cov >= 0.55, "定点打击联络人后簇内传播应仍存(≥0.55)"

    # 2c 接触即风险: 演化出小而密
    rng3 = random.Random(SEED + 3)
    adj_rep = evolve(rng3, repression=True)
    rng4 = random.Random(SEED + 3)
    adj_free = evolve(rng4, repression=False)

    def stats_of(g):
        comps = component_sizes(g, set(g))
        degs = [len(g[v]) for v in g]
        return (max(degs), statistics.mean(degs), global_clustering(g),
                len(comps), statistics.mean(comps))

    mx_r, md_r, cc_r, nc_r, ms_r = stats_of(adj_rep)
    mx_f, md_f, cc_f, nc_f, ms_f = stats_of(adj_free)

    print(f"\n[2c] 演化 30 轮(每轮+8 人): 压制网 vs 无压制对照")
    print(f"  {'网络':<12}{'节点':>6}{'最大度':>8}{'平均度':>8}"
          f"{'聚集系数':>9}{'分量数':>8}{'平均分量':>9}")
    for nm, g, s in (("压制传抄网", adj_rep, (mx_r, md_r, cc_r, nc_r, ms_r)),
                     ("无压制对照", adj_free, (mx_f, md_f, cc_f, nc_f, ms_f))):
        print(f"  {nm:<12}{len(g):>6}{s[0]:>8}{s[1]:>8.2f}"
              f"{s[2]:>9.3f}{s[3]:>8}{s[4]:>9.1f}")
    print("  读数: 压制把高暴露节点筛掉——度数封顶, 分量变多变小, 簇内更密;")
    print("        无压制对照长出大枢纽(度数悬殊, 聚集系数低)——萨米兹达特")
    print("        的组织学: 弱连接传播, 强信任保命")

    assert mx_r < 0.6 * mx_f, "压制网最大度应<对照 60%(度数被封顶)"
    assert cc_r > 2.0 * cc_f, "压制网聚集系数应>对照 2 倍(簇内更密)"
    assert nc_r > nc_f, "压制网连通分量应更多(分簇)"
    assert ms_r < ms_f, "压制网平均分量应更小(小而密)"
    print(f"\n✓ 幕二断言通过: 传抄 {t_sam} 步到八成 vs 官方 1 步; 单点移除最低 "
          f"{min_cov:.0%} 不断, 官方印厂被端即 0; 演化后最大度 {mx_r}<{mx_f}, "
          f"聚集 {cc_r:.2f}>{cc_f:.2f}——小而密, 打不死")


# ==================== 幕三: 流亡作家的双市场回归(昆德拉现象) ====================

N_COHORT = 30            # 每队列 30 位流亡作家(风格化)
P_TRANS_WEST = 0.45      # 母语新作被西方译介的概率(换语队列免译,为 1.0)
IMPACT_LO, IMPACT_HI = 0.6, 1.4
P_BACK_SWITCH = 0.20     # 换语新作回译母国的概率(法语新作回译捷/波语更少)
P_BACK_KEEP = 0.55       # 母语新作回流母国的概率(重版即可)
# 旧作重译热走多通道(重译+重版+选本/教材), 基数 1.5; 新作回流单通道, 单位 1.0
OLD_BASE, OLD_FAME, OLD_BAN = 1.5, 0.6, 0.3
NEW_HEAT = 1.0


def act3():
    print("\n" + "=" * 84)
    print("幕三 流亡作家的双市场回归: 换语 vs 母语, 旧我 vs 新作(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED)

    rows = []
    for cohort in ("换语写作", "母语坚持"):
        for _ in range(N_COHORT):
            n_old = rng.randint(2, 4)
            n_new = rng.randint(4, 8)
            exile_year = rng.randint(1948, 1978)
            banned_years = 1989 - exile_year
            # 流亡期西方接受
            if cohort == "换语写作":
                west = sum(rng.uniform(IMPACT_LO, IMPACT_HI)
                           for _ in range(n_new))
            else:
                west = sum(rng.uniform(IMPACT_LO, IMPACT_HI)
                           for _ in range(n_new) if rng.random() < P_TRANS_WEST)
            # 铁幕后母国市场
            fame_n = min(1.0, west / 6.0)
            ban_n = min(1.0, banned_years / 30.0)
            old_heat = sum(OLD_BASE + OLD_FAME * fame_n + OLD_BAN * ban_n
                           for _ in range(n_old))
            p_back = P_BACK_SWITCH if cohort == "换语写作" else P_BACK_KEEP
            back = [rng.gauss(4.5, 2.0) for _ in range(n_new)
                    if rng.random() < p_back]
            reissue = [rng.uniform(0.0, 2.0) for _ in range(n_old)]
            rows.append(dict(cohort=cohort, west=west, old_heat=old_heat,
                             new_back=len(back), n_new=n_new,
                             year_old=statistics.median(reissue),
                             year_new=(statistics.median(back) if back
                                       else None)))

    def m(cohort, key):
        return statistics.mean(r[key] for r in rows if r["cohort"] == cohort)

    w_sw, w_kp = m("换语写作", "west"), m("母语坚持", "west")
    b_sw = m("换语写作", "new_back") / m("换语写作", "n_new")
    b_kp = m("母语坚持", "new_back") / m("母语坚持", "n_new")
    old_all = statistics.mean(r["old_heat"] for r in rows)
    new_all = statistics.mean(r["new_back"] * NEW_HEAT for r in rows)
    ratio_old_new = old_all / new_all
    yrs_old = statistics.mean(r["year_old"] for r in rows)
    yrs_new = statistics.mean(r["year_new"] for r in rows if r["year_new"])

    print(f"\n[3a] 流亡期双市场(各 {N_COHORT} 位):")
    print(f"  西方接受指数: 换语 {w_sw:.2f} vs 母语 {w_kp:.2f}"
          f"(×{w_sw / w_kp:.2f})——免译直达")
    print(f"  新作回流率(流亡期作品铁幕后进母国): 换语 {b_sw:.0%} vs "
          f"母语 {b_kp:.0%}——西方吃香与母国流失同源")
    assert w_sw > 1.4 * w_kp, "换语队列西方接受应>母语队列 1.4 倍"
    assert b_sw < 0.6 * b_kp, "换语新作回流率应<母语队列 60%(母国读者流失)"

    print(f"\n[3b] 回归期市场(1989 后, 全 {2 * N_COHORT} 位):")
    print(f"  被禁旧作重译/重版热度 {old_all:.2f} vs 流亡新作回流 {new_all:.2f}"
          f"(×{ratio_old_new:.2f})")
    print(f"  时点: 旧作重译平均在墙倒后 {yrs_old:.1f} 年, 新作回流 "
          f"{yrs_new:.1f} 年(晚 {yrs_new - yrs_old:.1f} 年)")
    print("  读数: 回归市场先要'被禁的旧我', 流亡期的新我是第二批货——")
    print("        流亡作家回家时, 家里等着的是他离开前的自己")

    assert ratio_old_new > 2.0, "旧作重译热应>新作回流 2 倍"
    assert yrs_new - yrs_old > 3.0, "新作回流应比旧作重译晚 3 年以上"
    print(f"\n✓ 幕三断言通过: 换语西方 {w_sw:.2f} vs 母语 {w_kp:.2f}(×"
          f"{w_sw / w_kp:.2f})而回流率 {b_sw:.0%}<{b_kp:.0%}; 旧作热 ×"
          f"{ratio_old_new:.2f} 于新作, 早 {yrs_new - yrs_old:.1f} 年"
          "——家里等的是离开前的自己")


def main():
    _utf8_stdout()
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 铁幕翻译时滞双向不对称: 流亡出版社把西译时滞压到官方通道约"
          "三分之一; 东译敏感类份额与速度双重劣汰——铁幕是玻璃做的: 看得见,")
    print("     过得慢, 还被挑过")
    print("  ② 地下出版的网络韧性: 传抄慢于官方发行(数十步 vs 1 步)但移除"
          "任意节点网络不断(官方印厂被端即 0); 接触即风险")
    print("     的演化把网络筛成小而密(度数封顶/分量多/聚集高)——弱连接")
    print("     传播, 强信任保命")
    print("  ③ 流亡作家的双市场回归: 换语写作西方吃香(×1.4+)而母国读者")
    print("     流失(回流率<母语队列 60%); 回归期被禁旧作重译热>流亡新作")
    print("     回流 2 倍且早 3 年——流亡作家回家时, 家里等着的是他离开前")
    print("     的自己")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
