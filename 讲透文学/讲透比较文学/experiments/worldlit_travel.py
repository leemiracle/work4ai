# -*- coding: utf-8 -*-
"""世界文学的旅行:翻译流网络、观念漂移与母题变异三幕实验。

00-体系结构.md(反直觉三律:世界文学空间有首都/理论搬家必改姓/创造性
叛逆是再生产)、03-可构造与结构.md(翻译流网络/漂移累积/母题变异计数的
严格可构造性)、04-比较文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(random/statistics/math),无第三方依赖;每幕固定随机种子,可复现。

幕一 世界文学体系的核心-边缘(卡萨诺瓦《文学世界共和国》/莫莱蒂世界文学体系):
    18 种语言为节点,各带人口(母语者,通说近似,百万)与「文学资本」初始禀赋
    s(历史形成的翻译基础设施:出版工业/职业译者供给/学术体系,相对单位;
    人口与资本不成比例——孟加拉语人口≈法语四倍而文学资本远低,这正是卡萨诺
    瓦的起点)。网络按生长模型长成:种子=伦敦-巴黎双城直接译道(历史核心);
    其余语言按文学建制化的大致先后入网,每个新入网语言开一条直接译道,通到
    哪个已入网语言由概率 ∝ (度数 k + 资本 s) 决定——优先连接:伙伴越多、
    资本越厚的语言越吸引新译道(译者供给/出版社注意力的马太效应;文学资本
    靠积累与中介增值)。再加 12 条后续加密译道(同规则)。建成后对全部有序
    语言对求最短路,「转译路径」=经由第三语言的翻译路径。
    断言:①枢纽语言(典型为英语)的转译中介份额中位数 ≥ 其人口份额的 4 倍
    (中介地位靠资本复利,不靠人口体量);
      ②移除枢纽后语言对连通率中位数下降 ≥ 0.20(世界文学空间有首都,
        拔掉首都,共和国散架)。
幕二 观念旅行的漂移累积(萨义德「旅行理论」):
    概念=单位语义向量;每站跨语传播=部分保留+部分漂移:
        v ← normalize( v + δ·b + σ·ξ ),
    b=该站接受语境的问题域方向(语境引力,把概念往自己的问题域拉),
    ξ=各向同性噪声。旅程 k 站;配对对照臂 δ=0(同语境同噪声,纯噪声扩散)。
    断言:①末端与原义的角度距离期望随站数单调增;
          ②漂移非各向同性:位移在「本旅程诸语境问题域」方向上的投影显著为正
            (有偏臂 ≥0.30,噪声臂 ≈0),且同站数下有偏臂漂得比纯噪声臂远
            (≥1.25 倍)——理论搬家必改姓,且改姓有方向:每站语境把概念往
            自己的问题域拉。
幕三 变异率的系统差(曹顺庆变异学/埃斯卡皮「创造性叛逆」):
    同一母题(核心成分 10 + 边缘成分 10)在两个系统各传讲 8 代:
    强规范系统(严格文类传统,如格律诗体/仪式性格式:核心每代变异率 0.02,
    边缘 0.10)vs 弱规范系统(自由文类,如长篇小说:核心 0.08,边缘 0.22)。
    3000 条世系;变异率=与原母题不同成分的占比。
    断言:①弱规范系统总变异率 ≥ 强系统的 1.5 倍(情节更自由);
          ②强规范系统内核心变异 ≤ 边缘变异的一半(仪式性格式稳定,装饰自由);
          ③核心的保守性是系统性质:弱系统核心变异 ≥ 强系统的 2.5 倍;
          ④蒙特卡洛均值与解析期望 1−(1−m)^k 吻合(|差|<0.03)。

跑法: python3 -u experiments/worldlit_travel.py
"""

import math
import random
import statistics


# ==================== 幕一:世界文学体系的核心-边缘 ====================

# (代码, 母语人口[百万,通说近似], 文学资本初始禀赋 s[相对单位])
# 列序=入网序(文学建制化的大致先后,通说口径的相对量级,模型假设之一)。
LANGS = [
    ("EN", 380.0, 10.0),   # 种子双城之一:战后出版工业与学术体系的先发积累
    ("FR", 80.0, 6.0),     # 种子双城之二:巴黎,文学现代性的历史首都(卡萨诺瓦)
    ("RU", 150.0, 4.0),
    ("DE", 76.0, 4.0),
    ("ZH", 940.0, 4.0),
    ("ES", 485.0, 3.0),
    ("JA", 125.0, 2.0),
    ("IT", 65.0, 2.0),
    ("PL", 40.0, 2.0),
    ("AR", 275.0, 1.5),
    ("PT", 235.0, 1.5),
    ("TR", 85.0, 1.5),
    ("NL", 25.0, 1.5),
    ("EL", 13.0, 1.5),
    ("HI", 345.0, 1.0),
    ("KO", 77.0, 1.0),
    ("VI", 85.0, 1.0),
    ("SW", 200.0, 1.0),
]
N_LANG = len(LANGS)
POP_TOTAL = sum(p for _, p, _ in LANGS)
POP_SHARE = [p / POP_TOTAL for _, p, _ in LANGS]
CODES = [c for c, _, _ in LANGS]
N_EXTRA = 12          # 后续加密译道条数(生长树 17 条之外)
N_REAL = 200          # 蒙特卡洛实现数(断言取中位数,单一实现只是展示)


def pick_endpoint(rng, adj, s, joined, banned=-1):
    """在已入网语言中按 k_i + s_i 掷骰选一个端点(banned=另一端,不许重复)。"""
    w = [(len(adj[i]) + s[i]) if i in joined and i != banned else 0.0
         for i in range(N_LANG)]
    total = sum(w)
    x = rng.random() * total
    acc = 0.0
    for i, wi in enumerate(w):
        acc += wi
        if x <= acc:
            return i
    return max(joined)


def build_network(rng):
    """生长模型:种子双城译道 → 语言依次入网各开一条优先连接译道 → 加密译道。"""
    s = [cap for _, _, cap in LANGS]
    adj = [set() for _ in range(N_LANG)]
    joined = {0, 1}
    adj[0].add(1)
    adj[1].add(0)                       # 种子:伦敦-巴黎
    for newcomer in range(2, N_LANG):   # 依次入网,各开一条直接译道
        host = pick_endpoint(rng, adj, s, joined)
        adj[newcomer].add(host)
        adj[host].add(newcomer)
        joined.add(newcomer)
    for _ in range(N_EXTRA):            # 后续加密:两个端点都按优先连接
        a = pick_endpoint(rng, adj, s, joined)
        b = pick_endpoint(rng, adj, s, joined, banned=a)
        adj[a].add(b)
        adj[b].add(a)
    return adj


def bfs_path(adj, src, dst):
    """最短路(BFS,固定节点序保证可复现);不通返回 None。"""
    if dst in adj[src]:
        return [src, dst]
    prev = {src: None}
    queue = [src]
    while queue:
        cur = queue.pop(0)
        for nxt in sorted(adj[cur]):
            if nxt not in prev:
                prev[nxt] = cur
                if nxt == dst:
                    path = [dst]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return path[::-1]
                queue.append(nxt)
    return None


def measure(adj):
    """对一个实现量:连通率/各语言转译中介份额(全部有序对最短路统计)。"""
    pairs = [(i, j) for i in range(N_LANG) for j in range(N_LANG) if i != j]
    reach = 0
    relay_pairs = 0                     # 至少经由一个第三语言的路径
    between = [0] * N_LANG              # 作为中间语言(转译枢纽)被经过的次数
    for i, j in pairs:
        path = bfs_path(adj, i, j)
        if path is None:
            continue
        reach += 1
        if len(path) >= 3:
            relay_pairs += 1
            for m in path[1:-1]:
                between[m] += 1
    conn = reach / len(pairs)
    share = [b / relay_pairs if relay_pairs else 0.0 for b in between]
    return conn, share, relay_pairs


def act1():
    print("=" * 84)
    print("幕一 世界文学体系的核心-边缘:翻译流网络的生长与优先连接(种子 75021)")
    print("=" * 84)
    rng = random.Random(75021)
    hub_is_en = 0
    hub_btwn, conn_post, drop = [], [], []
    showcase = None
    for r in range(N_REAL):
        adj = build_network(rng)
        conn, share, relays = measure(adj)
        # 枢纽=中介地位(度数+文学资本)最高者——不是人口最大者
        hub = max(range(N_LANG), key=lambda i: len(adj[i]) + LANGS[i][2])
        hub_is_en += (hub == 0)
        # 去枢纽化:删掉枢纽及其所有直接译道,重测剩余语言间的连通
        adj2 = [set(x for x in adj[i] if x != hub) for i in range(N_LANG)
                if i != hub]
        rest = [i for i in range(N_LANG) if i != hub]
        idx = {old: new for new, old in enumerate(rest)}
        adj3 = [set(idx[x] for x in adj2[idx[i]]) for i in rest]
        pairs2 = [(a, b) for a in range(len(rest)) for b in range(len(rest))
                  if a != b]
        reach2 = sum(1 for a, b in pairs2 if bfs_path(adj3, a, b) is not None)
        conn2 = reach2 / len(pairs2)
        hub_btwn.append(share[hub])
        conn_post.append(conn2)
        drop.append(conn - conn2)
        if r == 0:
            showcase = (adj, hub, conn, share, relays, conn2)
    adj, hub, conn, share, relays, conn2 = showcase

    print(f"\n18 种语言(母语人口合计 {POP_TOTAL:.0f} 百万),生长模型:种子=EN-FR"
          f" 双城译道,诸语言依次入网各开一条优先连接译道,再加 {N_EXTRA} 条"
          f"加密译道;{N_REAL} 个实现,首个实现展示:")
    degs = sorted(range(N_LANG), key=lambda i: -len(adj[i]))
    print(f"\n  展示实现的直接译道伙伴度前六:" + ", ".join(
        f"{CODES[i]}={len(adj[i])}" for i in degs[:6]))
    print(f"  连通率(全部有序语言对可互通):{conn:.1%}")
    top_btwn = sorted(range(N_LANG), key=lambda i: -share[i])[:3]
    print(f"  转译路径 {relays} 条(经由第三语言),中介份额前三:" + ", ".join(
        f"{CODES[i]}={share[i]:.1%}" for i in top_btwn))
    demo = bfs_path(adj, 17, 15)
    print("  样例转译路径 SW→KO:" + "→".join(CODES[i] for i in demo))
    print(f"  移除枢纽 {CODES[hub]} 后连通率:{conn2:.1%}(降 {conn - conn2:.1%})")

    med = lambda xs: statistics.median(xs)
    print(f"\n{N_REAL} 个实现的中位数:")
    print(f"  枢纽=EN 的实现占比      {hub_is_en / N_REAL:.1%}"
          f"(EN 人口份额仅 {POP_SHARE[0]:.1%},不是最大语种)")
    print(f"  枢纽转译中介份额        {med(hub_btwn):.1%}")
    print(f"  枢纽人口份额            {POP_SHARE[0]:.1%}(固定)")
    print(f"  中介份额/人口份额       {med(hub_btwn) / POP_SHARE[0]:.1f} 倍")
    print(f"  连通率:前 100%(生长模型保证) → 去枢纽后 {med(conn_post):.1%}"
          f"(中位降幅 {med(drop):.1%})")
    print("\n读数:")
    print("  · 生长+优先连接:英语凭翻译基础设施的先发禀赋(而非人口——汉语")
    print("    人口是它两倍多)在马太效应下复利称霸;边缘语言之间几乎不开")
    print("    直接译道,交往须经首都——卡萨诺瓦「文学世界共和国」的不对称")
    print("    结构,莫莱蒂所说的中心-边缘体系")
    print("  · 拔掉枢纽,大量语言对直接断路:无标度网络的「目标攻击脆弱性」")
    print("    (Albert-Jeong-Barabási 2000 的文学版)——世界文学空间有首都,")
    print("    而且首都极少;去枢纽化实验是世界文学体系论的压力测试")

    # 断言一:中介份额远超人口份额;枢纽稳定为 EN;去枢纽连通性显著受损
    assert hub_is_en / N_REAL >= 0.80, f"枢纽应稳定为 EN,实测 {hub_is_en}/{N_REAL}"
    assert med(hub_btwn) >= 4 * POP_SHARE[0], (
        f"中介份额应 ≥4 倍人口份额,实测 {med(hub_btwn):.3f} vs {POP_SHARE[0]:.3f}")
    assert med(drop) >= 0.20, f"去枢纽后连通率中位降幅应 ≥0.20,实测 {med(drop):.3f}"
    assert abs(conn - 1.0) < 1e-12, "展示实现建网后应全连通(生长模型保证)"
    print(f"\n✓ 幕一断言通过:中介份额 {med(hub_btwn):.0%} ≈ 人口份额 "
          f"{POP_SHARE[0]:.0%} 的 {med(hub_btwn) / POP_SHARE[0]:.1f} 倍;"
          f"去枢纽连通率中位降 {med(drop):.0%}——世界文学空间有首都")


# ==================== 幕二:观念旅行的漂移累积 ====================

DIM = 6
V0 = [1.0, 0.6, 0.8, 0.5, 0.9, 0.3]      # 概念的初始语义方向(单位化前)
# 六个接受语境的问题域方向(单位向量):语境把概念往自己的问题域拉。
# 设计约束:诸语境的合成方向大体与原义方向近正交(语境拉概念「离开原位」),
# 诸语境彼此既不同向也不对消(各有各的问题域)。
CONTEXTS = [
    ("民族认同域", [0.6, -0.7, 0.5, -0.5, 0.4, -0.3]),
    ("阶级政治域", [0.5, -0.6, -0.4, -0.6, 0.3, -0.5]),
    ("审美自律域", [0.7, -0.5, 0.6, -0.4, -0.3, 0.6]),
    ("现代化域",   [0.3, -0.9, -0.2, -0.5, 0.6, 0.2]),
    ("宗教伦理域", [0.8, -0.4, 0.3, -0.7, -0.1, -0.6]),
    ("性别批判域", [0.1, -0.8, 0.7, -0.3, 0.5, 0.4]),
]
DELTA = 0.20     # 语境引力强度(每站系统性拉偏)
SIGMA = 0.08     # 各向同性噪声强度
K_MAX = 6        # 最长旅程站数
N_TRIP = 2000    # 每站数的旅程数


def normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def act2():
    print("\n" + "=" * 84)
    print("幕二 观念旅行的漂移累积:有偏随机游走 vs 纯噪声(种子 20260907)")
    print("=" * 84)
    rng = random.Random(20260907)
    v0 = normalize(V0)
    bias_dirs = [normalize(b) for _, b in CONTEXTS]
    dist_b, dist_c, align_b, align_c = {}, {}, {}, {}
    for k in range(1, K_MAX + 1):
        db, dc, ab, ac = [], [], [], []
        for _ in range(N_TRIP):
            ctx = [rng.randrange(len(CONTEXTS)) for _ in range(k)]
            noise = [[rng.gauss(0, SIGMA) for _ in range(DIM)] for _ in range(k)]
            drift = [0.0] * DIM
            for c in ctx:
                for t in range(DIM):
                    drift[t] += bias_dirs[c][t]
            bdir = normalize(drift)          # 本旅程诸语境问题域的合成方向
            vb, vc = v0[:], v0[:]
            for step in range(k):
                b = bias_dirs[ctx[step]]
                nse = noise[step]
                vb = normalize([vb[t] + DELTA * b[t] + nse[t] for t in range(DIM)])
                vc = normalize([vc[t] + nse[t] for t in range(DIM)])  # 配对对照
            db.append(1 - cos(vb, v0))
            dc.append(1 - cos(vc, v0))
            ab.append(cos([vb[t] - v0[t] for t in range(DIM)], bdir))
            ac.append(cos([vc[t] - v0[t] for t in range(DIM)], bdir))
        dist_b[k], dist_c[k] = statistics.mean(db), statistics.mean(dc)
        align_b[k], align_c[k] = statistics.mean(ab), statistics.mean(ac)

    print(f"\n概念=6 维单位语义向量;每站 v←normalize(v+{DELTA}·b+{SIGMA}·ξ);"
          f"对照臂去语境引力(同噪声配对)")
    print(f"每站数 {N_TRIP} 次旅程的角度距离(1−cos)与位移对齐度均值:")
    print(f"\n  {'站数 k':>6} {'有偏距离':>9} {'噪声距离':>9} {'有偏对齐':>9} {'噪声对齐':>9}")
    for k in range(1, K_MAX + 1):
        print(f"  {k:>6} {dist_b[k]:>9.3f} {dist_c[k]:>9.3f}"
              f" {align_b[k]:>9.3f} {align_c[k]:>9.3f}")
    print("\n读数:")
    print("  · 距离随站数单调增:每站只保留一部分、漂移一部分,漂移逐站累积——")
    print("    萨义德「旅行理论」的量化:理论搬家必改姓")
    print("  · 对齐度一栏是关键:有偏臂的位移在「诸语境问题域」方向上投影显著")
    print("    为正,噪声臂 ≈0——漂移不是各向同性的磨损,每一站的接受语境都")
    print("    把概念往自己的问题域拉(民族认同域拉出民族文学论,审美自律域")
    print("    拉出纯诗论……同一个词,六种命运)")
    print(f"  · 站数相同时有偏臂漂得更远(k={K_MAX}: {dist_b[K_MAX]:.2f} vs "
          f"{dist_c[K_MAX]:.2f}):系统性引力走线性累积,噪声只走 √k 扩散")

    # 断言二:距离单调增;漂移有方向(有偏≫噪声);有偏比纯噪声漂得远
    for k in range(2, K_MAX + 1):
        assert dist_b[k] > dist_b[k - 1] + 0.005, (
            f"有偏臂距离应随站数严格增,k={k} 处 {dist_b[k]:.3f}≤{dist_b[k-1]:.3f}")
        assert dist_c[k] > dist_c[k - 1], "噪声臂距离也应单调增"
    assert align_b[K_MAX] >= 0.30, f"有偏臂对齐度应 ≥0.30,实测 {align_b[K_MAX]:.3f}"
    assert abs(align_c[K_MAX]) <= 0.05, f"噪声臂对齐度应 ≈0,实测 {align_c[K_MAX]:.3f}"
    assert dist_b[K_MAX] >= 1.25 * dist_c[K_MAX], (
        f"k={K_MAX} 有偏距离应 ≥1.25 倍噪声距离,"
        f"实测 {dist_b[K_MAX]:.3f} vs {dist_c[K_MAX]:.3f}")
    print(f"\n✓ 幕二断言通过:距离单调增;k={K_MAX} 时有偏 {dist_b[K_MAX]:.2f} vs "
          f"噪声 {dist_c[K_MAX]:.2f},对齐 {align_b[K_MAX]:.2f} vs "
          f"{align_c[K_MAX]:+.2f}——理论搬家必改姓,且改姓有方向")


# ==================== 幕三:变异率的系统差 ====================

N_CORE, N_PERIPH = 10, 10                 # 母题=核心成分 10+边缘成分 10
RETELLS = 8                               # 传讲代数
N_LINEAGE = 3000                          # 世系数
MUT = {
    "强规范": (0.02, 0.10),               # (核心变异率, 边缘变异率)
    "弱规范": (0.08, 0.22),
}


def lineage_variation(m_core, m_periph, rng):
    """一条世系传讲 RETELLS 代,返回逐代(核心变异率, 边缘变异率, 总变异率)。"""
    core = [False] * N_CORE                # False=与原母题相同
    periph = [False] * N_PERIPH
    out = []
    for _ in range(RETELLS):
        for i in range(N_CORE):
            if rng.random() < m_core:
                core[i] = True             # 变异即换新,不会换回原样
        for i in range(N_PERIPH):
            if rng.random() < m_periph:
                periph[i] = True
        out.append((sum(core) / N_CORE, sum(periph) / N_PERIPH,
                    (sum(core) + sum(periph)) / (N_CORE + N_PERIPH)))
    return out


def act3():
    print("\n" + "=" * 84)
    print("幕三 变异率的系统差:强规范 vs 弱规范系统(种子 75021021)")
    print("=" * 84)
    print(f"\n母题=核心成分 {N_CORE}(仪式性格式:格律/骨架/禁忌)+边缘成分 "
          f"{N_PERIPH}(情节装饰);传讲 {RETELLS} 代,{N_LINEAGE} 条世系")
    print(f"每代变异率  强规范:核心 {MUT['强规范'][0]:.2f}/边缘 {MUT['强规范'][1]:.2f}"
          f"   弱规范:核心 {MUT['弱规范'][0]:.2f}/边缘 {MUT['弱规范'][1]:.2f}")
    res = {}
    for system, (mc, mp) in MUT.items():
        rng = random.Random(75021021 if system == "强规范" else 75021022)
        rows = [lineage_variation(mc, mp, rng) for _ in range(N_LINEAGE)]
        res[system] = [[statistics.mean(row[k][j] for row in rows)
                        for j in range(3)] for k in range(RETELLS)]
    print(f"\n  {'代数':>4}  {'强规范:核心':>10} {'边缘':>7} {'合计':>7}"
          f"  {'弱规范:核心':>10} {'边缘':>7} {'合计':>7}")
    for k in range(RETELLS):
        s, w = res["强规范"][k], res["弱规范"][k]
        print(f"  {k + 1:>4}  {s[0]:>10.3f} {s[1]:>7.3f} {s[2]:>7.3f}"
              f"  {w[0]:>10.3f} {w[1]:>7.3f} {w[2]:>7.3f}")
    s, w = res["强规范"][-1], res["弱规范"][-1]
    theory = {name: tuple(list(1 - (1 - m) ** RETELLS for m in rates)
                          + [sum(1 - (1 - m) ** RETELLS for m in rates) / 2])
              for name, rates in MUT.items()}
    theory_s, theory_w = theory["强规范"], theory["弱规范"]
    print(f"\n第 {RETELLS} 代实测(强):核心 {s[0]:.1%} 边缘 {s[1]:.1%} 合计 {s[2]:.1%};"
          f"解析 1−(1−m)^k:{theory_s[0]:.1%}/{theory_s[1]:.1%}/{theory_s[2]:.1%}")
    print(f"第 {RETELLS} 代实测(弱):核心 {w[0]:.1%} 边缘 {w[1]:.1%} 合计 {w[2]:.1%};"
          f"解析 1−(1−m)^k:{theory_w[0]:.1%}/{theory_w[1]:.1%}/{theory_w[2]:.1%}")
    print("\n读数:")
    print("  · 弱规范系统的变异累积率全面高于强规范:情节更自由,母题被当地")
    print("    问题重写得更狠——《赵氏孤儿》到伏尔泰手里改朝换代改主题,")
    print("    而十四行诗到哪儿都得十四行")
    print("  · 强规范系统内部:核心(仪式性格式)保守而边缘(装饰)自由——格式")
    print("    是文类的「身份证」,动它就出了文类;装饰是「本地化接口」,随便改")
    print("  · 变异学的机制面:创造性叛逆不是翻译的失败,是文学再生产的方式——")
    print("    两个系统都在变异,只是变异落在母题的哪一层,由规范强度决定")

    # 断言三:弱>强(总);强系统核心≤边缘一半;弱系统核心≥强系统核心 2.5 倍;
    # 实测与解析吻合;逐代单调累积
    assert w[2] >= 1.5 * s[2], (
        f"弱规范总变异率应 ≥1.5 倍强规范,实测 {w[2]:.3f} vs {s[2]:.3f}")
    assert s[0] <= 0.5 * s[1], (
        f"强规范核心变异应 ≤边缘一半,实测 {s[0]:.3f} vs {s[1]:.3f}")
    assert w[0] >= 2.5 * s[0], (
        f"弱规范核心变异应 ≥2.5 倍强规范核心,实测 {w[0]:.3f} vs {s[0]:.3f}")
    for system, th in (("强规范", theory_s), ("弱规范", theory_w)):
        for j in range(3):
            assert abs(res[system][-1][j] - th[j]) < 0.03, (
                f"{system} 第{j}列 MC 均值应与解析吻合,"
                f"实测 {res[system][-1][j]:.3f} vs {th[j]:.3f}")
        for k in range(1, RETELLS):
            assert res[system][k][2] >= res[system][k - 1][2], "总变异率应逐代不减"
    print(f"\n✓ 幕三断言通过:总变异 弱 {w[2]:.0%} ≥1.5× 强 {s[2]:.0%};强系统核心 "
          f"{s[0]:.0%} ≤边缘 {s[1]:.0%} 的一半;弱系统核心 {w[0]:.0%} ≥强系统 "
          f"2.5 倍;MC 与解析 1−(1−m)^k 吻合(<3 个百分点)")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 翻译流网络优先连接:枢纽语言转译中介份额中位数为人口份额的数倍,")
    print("     移除枢纽连通率大幅受损——世界文学空间有首都(卡萨诺瓦/莫莱蒂)")
    print("  ② 观念旅行漂移累积:末端距离随站数单调增,且漂移方向被各站接受语境")
    print("     系统性拉偏(对齐度显著为正)——理论搬家必改姓(萨义德)")
    print("  ③ 变异率系统差:弱规范系统变异累积更快,强规范系统母题核心保守、")
    print("     装饰自由——创造性叛逆是文学再生产的方式(埃斯卡皮/曹顺庆)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
