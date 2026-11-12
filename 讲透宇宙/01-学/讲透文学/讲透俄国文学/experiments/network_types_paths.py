# -*- coding: utf-8 -*-
"""人物-典型-路径三律实验:俄国文学(GB/T 75054)三个机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-俄国文学转代码.md(走廊 1/2/3)的配套实验。纯标准库(math/random/statistics),
无第三方依赖,固定种子 20260909 全程可复现。参数为通说代表性案例的风格化参数
(见各幕题注),模拟不冒充文学史计量。

三幕:
  幕一 长篇的人物网络(《战争与和平》式共现网络)
      风格化生成(缩尺约 1:7):罗斯托夫家/博尔孔斯基家/上流沙龙/军界/平民世界
      五个圈子,五位枢纽人物(皮埃尔/娜塔莎/安德烈/尼古拉/库图佐夫)跨圈出场,
      430 个场景按圈子加权采样共现,少量"偶遇场景"直接跨圈搭桥。
      通说锚:《战争与和平》(1865-1869)出场人物五百余人(通说 559);
      皮埃尔贯穿和平线与战争线,被俘营中遇农民卡拉塔耶夫(通说情节);
      巴赫金所谓复调长篇的"多声部并存"。
      断言:①枢纽人物度数远超均值(枢纽结构),介数中心度 top 全是串联
      多圈子的"接线员" ②定向移除枢纽后网络破碎度远超随机移除对照
      ——复调长篇在网络上=多枢纽结构,皮埃尔们是网络的关节。
  幕二 多余人的谱系传递(奥涅金→毕巧林→罗亭→奥勃洛摩夫)
      典型人物作为四维特征向量(智慧才具/行动力/社会效用/自我意识);
      谱系传递=继承(不变带:高自我意识×低行动力被强拉回带内)
      +变异(时代际遇维随机游走,社会效用逐代缓降)。
      通说锚:屠格涅夫《多余人日记》(1849)定名"多余人";杜勃罗留波夫
      《什么是奥勃洛摩夫性格?》(1859);四个通说典型(奥涅金 1823-1831/
      毕巧林 1840/罗亭 1856/奥勃洛摩夫 1859)作风格化锚点。
      断言:①相邻典型相似度>隔代(按谱系距离单调衰减)②核心特征四代
      保守(自我意识≥6.0 且行动力≤3.5 的占比≥96%),散开的是时代际遇维
      ——"多余人"的骨架四代不变,变的是病情的国情。
  幕三 1917 的路径分岔(留下适应/流亡/内部流亡)
      90 位作家的风格化 cohort:分流集中在 1917-1922 革命窗口期,
      此后仅偶发跨路径流动(通说个案:高尔基 1928 回苏/茨维塔耶娃 1939
      归国式的归国者,与再出走者);三条路径各自的逐年产量轨迹
      (留下适应:起伏受调控;流亡:断崖→域外重建读者群的"第二峰"→衰落;
      内部流亡:低而稳)。
      通说锚:第一波流亡(柏林→布拉格→巴黎),蒲宁 1933 成首位俄语
      诺贝尔文学奖得主(通说);流亡文学分期以域外出版重心转移为界。
      断言:①窗口期年分流率≥50× 窗口后年流动率(一次性分岔)
      ②三线产量轨迹分化(分岔前同源;分岔后每个五年段三线极差≥0.15、
      两两最大分道≥0.6)且流亡线出现"第二峰"(峰年反超留下线,其后衰落)
      ——一条 1917 的分岔线把一部文学史切成三部。

跑法: python -u experiments/network_types_paths.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现


# ==================== 幕一:长篇的人物网络 ====================

CIRCLES = ("罗斯托夫家", "博尔孔斯基家", "上流沙龙", "军界", "平民世界")
CIRCLE_W = (0.26, 0.19, 0.20, 0.23, 0.12)
MEMBERS = {
    "罗斯托夫家": ["索尼娅", "彼佳", "老罗斯托夫伯爵", "罗斯托娃伯爵夫人", "韦拉",
                "家庭教师甲", "家庭教师乙", "亲友甲", "亲友乙",
                "亲友丙", "宾客丁"],
    "博尔孔斯基家": ["老博尔孔斯基公爵", "玛丽亚小姐", "布里安小姐", "老仆吉洪",
                "亲随甲", "亲随乙", "邻庄地主甲", "邻庄地主乙", "管家丙"],
    "上流沙龙": ["安娜·帕夫洛夫娜", "瓦西里公爵", "爱伦", "阿纳托尔", "多洛霍夫",
              "鲍里斯", "朱莉", "佩龙斯卡娅", "莫特马尔子爵",
              "沙龙宾客甲", "沙龙宾客乙", "沙龙宾客丙", "沙龙宾客丁",
              "沙龙宾客戊", "沙龙宾客己", "沙龙宾客庚"],
    "军界": ["拿破仑", "巴格拉季昂", "杰尼索夫", "涅斯维茨基", "图申上尉",
           "巴克莱", "拉耶夫斯基", "哥萨克甲",
           "士兵一", "士兵二", "士兵三", "士兵四", "士兵五",
           "近卫军官一", "近卫军官二", "近卫军官三", "近卫军官四",
           "近卫军官五", "近卫军官六", "近卫军官七", "副官乙"],
    "平民世界": ["普拉东·卡拉塔耶夫", "阿尔帕特奇", "车夫甲",
              "农夫一", "农夫二", "农夫三", "农夫四", "农夫五", "农夫六",
              "农夫七", "农夫八", "女仆甲", "女仆乙", "女仆丙", "村妇丁"],
}
# 枢纽人物及其跨圈成员资格(通说情节的风格化:皮埃尔贯穿沙龙/平民/军界被俘线,
# 终娶娜塔莎;娜塔莎串联罗斯托夫家与博尔孔斯基家;安德烈从家宅走向战场;
# 尼古拉军旅后乡居务农;库图佐夫坐镇军界与宫廷)
HUBS = {
    "皮埃尔": ("上流沙龙", "平民世界", "罗斯托夫家", "军界"),
    "娜塔莎": ("罗斯托夫家", "上流沙龙", "博尔孔斯基家"),
    "安德烈": ("博尔孔斯基家", "军界", "上流沙龙"),
    "尼古拉": ("罗斯托夫家", "军界", "平民世界"),
    "库图佐夫": ("军界", "上流沙龙"),
}
N_SCENES = 430
BRIDGE_P = 0.003       # "偶遇场景"概率:极少数不经枢纽的直接跨圈搭桥(全书 1-2 次)
HUB_W = 9.0            # 枢纽人物场场抢戏;次要人物按偏斜活跃度出场(多数人只出现几次)


def build_network(rng):
    """按圈子生成场景,返回邻接表(共现即连边)与人物-圈子表。"""
    home = {}
    for c, ms in MEMBERS.items():
        for m in ms:
            home[m] = c
    for h, cs in HUBS.items():
        home[h] = cs[0]
    circles_of = {m: {home[m]} for m in home}
    for h, cs in HUBS.items():
        circles_of[h] = set(cs)
    act_w = {m: (0.4 + 1.6 * rng.random() ** 2) for m in circles_of if m not in HUBS}
    adj = {m: set() for m in circles_of}
    n_scene = {m: 0 for m in circles_of}
    sizes = (3, 4, 4, 5, 5, 6)
    for _ in range(N_SCENES):
        c = rng.choices(CIRCLES, weights=CIRCLE_W)[0]
        pool = [m for m in circles_of if c in circles_of[m]]
        weights = [HUB_W if m in HUBS else act_w[m] for m in pool]
        k = min(rng.choice(sizes), len(pool))
        picked = []
        pool2, w2 = pool[:], weights[:]
        while len(picked) < k:
            m = rng.choices(pool2, weights=w2)[0]
            picked.append(m)
            i = pool2.index(m)
            pool2.pop(i)
            w2.pop(i)
        if rng.random() < BRIDGE_P:                     # 偶遇:另一圈来人
            others = [m for m in circles_of if c not in circles_of[m]]
            picked.append(rng.choice(others))
        for m in picked:
            n_scene[m] += 1
        for i, a in enumerate(picked):
            for b in picked[i + 1:]:
                adj[a].add(b)
                adj[b].add(a)
    return adj, circles_of, n_scene


def components(adj, removed=()):
    """连通分量:返回[节点列表]的列表(removed 中的人物视作已移除)。"""
    nodes = [v for v in adj if v not in removed]
    seen = set()
    comps = []
    for v in nodes:
        if v in seen:
            continue
        comp, stack = [], [v]
        seen.add(v)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in removed and y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(comp)
    return comps


def betweenness(adj):
    """无权 Brandes 介数中心性(纯列表实现,不用第三方)。"""
    bt = {v: 0.0 for v in adj}
    for s in adj:
        order, preds = [], {v: [] for v in adj}
        sigma = {v: 0 for v in adj}
        dist = {v: -1 for v in adj}
        sigma[s], dist[s] = 1, 0
        queue, head = [s], 0
        while head < len(queue):
            v = queue[head]
            head += 1
            order.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = {v: 0.0 for v in adj}
        for w in reversed(order):
            for v in preds[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                bt[w] += delta[w]
    return {v: b / 2.0 for v, b in bt.items()}


def act1():
    print("=" * 84)
    print("幕一 长篇的人物网络(《战争与和平》式共现网络,五个圈子+五位枢纽)")
    print("=" * 84)
    rng = random.Random(SEED + 1)
    adj, circles_of, n_scene = build_network(rng)
    n_nodes, n_edges = len(adj), sum(len(v) for v in adj.values()) // 2
    top_scene = max(n_scene, key=n_scene.get)
    print(f"\n出场人物 {n_nodes} 人(通说《战争与和平》五百余人,缩尺约 1:{559 // n_nodes}),"
          f"共现边 {n_edges} 条,{N_SCENES} 个场景;出场最多:"
          f"{top_scene} {n_scene[top_scene]}/{N_SCENES} 场")
    deg = {v: len(adj[v]) for v in adj}
    mean_deg = stats.mean(deg.values())
    hub_deg = stats.mean(deg[h] for h in HUBS)
    plain_deg = stats.mean(deg[v] for v in deg if v not in HUBS)
    print(f"平均度数 {mean_deg:.1f};枢纽 {hub_deg:.1f} vs 非枢纽 {plain_deg:.1f}"
          f"(×{hub_deg / plain_deg:.1f})——枢纽结构")
    bt = betweenness(adj)
    top5 = sorted(bt, key=bt.get, reverse=True)[:5]
    print("介数中心度 top5:", "、".join(top5))
    print("            数值:", "、".join(f"{bt[v]:.1f}" for v in top5))
    # 断言 1:枢纽度数远超均值,且介数 top=串联多圈子的接线员
    assert hub_deg >= 3.5 * plain_deg, f"枢纽度数应≥3.5×非枢纽:{hub_deg:.1f} vs {plain_deg:.1f}"
    assert all(v in HUBS for v in top5), f"介数 top5 应全为枢纽:{top5}"
    n_circ = {h: len(circles_of[h]) for h in HUBS}
    print(f"\n✓ 幕一断言①通过:枢纽度数 {hub_deg / plain_deg:.1f}× 于非枢纽;介数 top5"
          f" 全是跨 {min(n_circ.values())}-{max(n_circ.values())} 个圈子的接线员"
          f"({','.join(f'{h}×{n}' for h, n in n_circ.items())})")

    def cross_reach(removed=()):
        """跨圈可达率:家分属不同圈子的人物对中,仍连通者占比(破碎度指标)。"""
        comps = components(adj, removed=removed)
        cid = {}
        for i, comp in enumerate(comps):
            for v in comp:
                cid[v] = i
        live = sorted(v for v in adj if v not in removed)
        pairs = reach = 0
        for i, u in enumerate(live):
            for v in live[i + 1:]:
                if circles_of[u] & circles_of[v]:
                    continue                              # 同圈人物对不计
                pairs += 1
                reach += cid[u] == cid[v]
        return reach / pairs, comps

    x0, comps0 = cross_reach()
    x_t, comps_t = cross_reach(removed=list(HUBS))
    rng2 = random.Random(SEED + 2)
    xs_r, comps_r = [], []
    for _ in range(200):                                # 随机移除同数人物作对照
        victims = rng2.sample(list(adj), len(HUBS))
        x, cx = cross_reach(removed=victims)
        xs_r.append(x)
        comps_r.append(len(cx))
    x_r, comps_r_mean = stats.mean(xs_r), stats.mean(comps_r)
    lcc_t = max(len(c) for c in comps_t) / (n_nodes - len(HUBS))
    print(f"\n完好网络:跨圈可达率 {x0:.0%},连通分量 {len(comps0)} 块")
    print(f"移除 5 枢纽:跨圈可达率 {x_t:.0%},最大连通片占 {lcc_t:.0%},"
          f"碎成 {len(comps_t)} 块(圈子互相失联)")
    print(f"随机移除 5 人(200 次平均):跨圈可达率 {x_r:.0%},平均 {comps_r_mean:.1f} 块")
    # 断言 2:定向移除枢纽的破碎度远超随机移除对照
    assert x0 == 1.0, "完好网络应全域连通"
    assert x_t <= 0.05, f"移除枢纽后跨圈可达率应≤5%:{x_t:.0%}"
    assert x_r >= 0.95, f"随机移除对照应基本保持跨圈可达(≥95%):{x_r:.0%}"
    assert x_r - x_t >= 0.90, f"破碎度差距应≥90 个点:{x_r - x_t:.0%}"
    assert x_r / max(x_t, 0.005) >= 6.0, f"破碎度差距应≥6×:{x_r:.0%} vs {x_t:.0%}"
    assert len(comps_t) >= 5, f"移除枢纽后应碎成≥5 块:{len(comps_t)}"
    print(f"\n✓ 幕一断言②通过:随机移除 5 人跨圈可达率仍有 {x_r:.0%}(平均"
          f"{comps_r_mean:.1f} 块);摘掉皮埃尔们,网络当场碎成 {len(comps_t)} 块"
          f"(=五个圈子孤岛),跨圈可达率崩到 {x_t:.0%}——复调长篇=多枢纽结构,"
          f"枢纽是网络的关节")
    return {"hub_x": hub_deg / plain_deg, "top5": top5, "x_t": x_t,
            "x_r": x_r, "comps_t": len(comps_t), "n_nodes": n_nodes,
            "pierre": n_scene["皮埃尔"] / N_SCENES}


# ==================== 幕二:多余人的谱系传递 ====================

DIMS = ("智慧才具", "行动力", "社会效用", "自我意识")
CANON = {                     # 通说典型的风格化锚点(非文学史计量)
    "奥涅金(1823-31)": (7.0, 3.0, 2.0, 7.0),
    "毕巧林(1840)": (8.0, 5.0, 1.0, 9.0),
    "罗亭(1856)": (8.5, 2.0, 1.5, 6.5),
    "奥勃洛摩夫(1859)": (6.5, 0.8, 0.5, 5.5),
}
# 不变带:核心特征被强拉回带内(高自我意识×低行动力=多余人骨架)
INVARIANT = {"自我意识": (7.4, 0.45, ">=", 6.0), "行动力": (2.2, 0.45, "<=", 3.5)}
DRIFT = {"智慧才具": (0.0, 1.9), "社会效用": (-0.3, 1.9)}   # 时代际遇维:游走+缓降
N_LINEAGES, GENS = 2000, 4
SCALE = 10.0


def sim(a, b):
    """相似度=1-平均绝对差/量程(四维向量,0-1)。"""
    return 1.0 - sum(abs(x - y) for x, y in zip(a, b)) / len(a) / SCALE


def lineage(rng):
    """一条谱系:奥涅金起点,继承(不变带拉回)+变异(际遇维游走)。"""
    gens = [[rng.gauss(v, 0.4) for v in CANON["奥涅金(1823-31)"]]]
    for _ in range(GENS - 1):
        parent = gens[-1]
        child = []
        for j, _d in enumerate(DIMS):
            name = DIMS[j]
            if name in INVARIANT:
                mu, sd, _op, _bound = INVARIANT[name]
                child.append(rng.gauss(mu, sd))          # 骨架:拉回不变带
            else:
                drift, sd = DRIFT[name]
                child.append(parent[j] + drift + rng.gauss(0, sd))
        gens.append(child)
    return gens


def act2():
    print("\n" + "=" * 84)
    print("幕二 多余人的谱系传递(奥涅金→毕巧林→罗亭→奥勃洛摩夫,四维特征向量)")
    print("=" * 84)
    print("四维:", "/".join(DIMS), ";不变带:自我意识 N(7.4,0.45)≥6.0,"
          "行动力 N(2.2,0.45)≤3.5;际遇维:智慧才具/社会效用逐代随机游走(σ=1.9,效用缓降)")
    print("\n通说典型锚点(风格化):")
    for k, v in CANON.items():
        print(f"  {k}: 智慧 {v[0]:.1f}/行动 {v[1]:.1f}/效用 {v[2]:.1f}/意识 {v[3]:.1f}")
    names = list(CANON)
    print("\n  锚点间相似度:相邻", "、".join(f"{sim(CANON[names[i]], CANON[names[i + 1]]):.3f}"
          for i in range(3)),
          ";隔代(奥涅金-罗亭)", f"{sim(CANON[names[0]], CANON[names[2]]):.3f}",
          "——文学史锚点是单次噪声实现, ensemble 律见下")

    rng = random.Random(SEED + 10)
    lineages = [lineage(rng) for _ in range(N_LINEAGES)]
    by_dist = {1: [], 2: [], 3: []}
    for gens in lineages:
        for i in range(GENS):
            for d in (1, 2, 3):
                if i + d < GENS:
                    by_dist[d].append(sim(gens[i], gens[i + d]))
    s1, s2, s3 = (stats.mean(by_dist[d]) for d in (1, 2, 3))
    print(f"\n系综({N_LINEAGES} 条谱系平均):相似度按谱系距离:"
          f"相邻 {s1:.4f} > 隔一代 {s2:.4f} > 隔两代 {s3:.4f}")
    # 断言 1:相邻典型相似度>隔代(单调衰减)
    assert s1 > s2 > s3, f"相似度应按谱系距离单调衰减:{s1:.4f}/{s2:.4f}/{s3:.4f}"
    assert s1 - s2 >= 0.004 and s2 - s3 >= 0.004, "衰减间隔应≥0.004"
    print(f"✓ 幕二断言①通过:谱系距离 1/2/3 代的相似度 {s1:.4f}/{s2:.4f}/{s3:.4f}"
          f" 严格递减——继承+变异使相邻像、隔代疏")

    idx = {d: DIMS.index(d) for d in DIMS}
    n_vec, n_ok = 0, 0
    var_inv, var_drift = [], []
    for gens in lineages:
        cols = list(zip(*gens))                          # 各维跨代取值
        var_inv.append(stats.pstdev(cols[idx["自我意识"]]) ** 2
                       + stats.pstdev(cols[idx["行动力"]]) ** 2)
        var_drift.append(stats.pstdev(cols[idx["智慧才具"]]) ** 2
                         + stats.pstdev(cols[idx["社会效用"]]) ** 2)
        for vec in gens:
            n_vec += 1
            if vec[idx["自我意识"]] >= 6.0 and vec[idx["行动力"]] <= 3.5:
                n_ok += 1
    keep_rate = n_ok / n_vec
    disp_ratio = math.sqrt(stats.mean(var_drift) / stats.mean(var_inv))
    print(f"\n骨架保守率(自我意识≥6.0 且行动力≤3.5):{keep_rate:.1%}"
          f"({n_ok}/{n_vec} 个典型向量)")
    print(f"际遇维/骨架维的谱系内散开度比:{disp_ratio:.1f}×")
    # 断言 2:核心特征全程保守,散开的是时代际遇维
    assert keep_rate >= 0.96, f"骨架保守率应≥96%:{keep_rate:.1%}"
    assert disp_ratio >= 3.0, f"际遇维散开度应≥骨架维的 3 倍:{disp_ratio:.1f}"
    print(f"\n✓ 幕二断言②通过:四代 {keep_rate:.0%} 的典型守着同一副骨架"
          f"(高自我意识×低行动力),际遇维散开 {disp_ratio:.1f}× 于骨架维"
          f"——\"多余人\"的骨架四代不变,变的是病情的国情")
    return {"s1": s1, "s2": s2, "s3": s3, "keep": keep_rate, "disp": disp_ratio}


# ==================== 幕三:1917 的路径分岔 ====================

YEARS = list(range(1910, 1961))
PATHS = ("留下适应", "流亡", "内部流亡")
N_WRITERS = 90
WINDOW = (1917, 1922)       # 革命窗口期
SWITCH_P = 0.0007           # 窗口后每年跨路径流动概率(归国者/再出走者)
PATH_SHARE = (0.58, 0.27, 0.15)

# 三条路径的年产量锚点(风格化;插值成逐年均值)
ANCHORS = {
    "留下适应": [(1910, 1.00), (1916, 1.05), (1919, 0.45), (1922, 0.70),
             (1926, 1.35), (1928, 1.30), (1932, 0.85), (1937, 0.80),
             (1941, 0.50), (1945, 0.70), (1950, 1.00), (1955, 1.05), (1960, 1.00)],
    "流亡": [(1910, 1.00), (1916, 1.00), (1918, 0.30), (1921, 0.32), (1924, 0.78),
           (1927, 1.18), (1930, 1.25), (1934, 0.95), (1938, 0.70), (1941, 0.25),
           (1945, 0.20), (1950, 0.15), (1955, 0.10), (1960, 0.08)],
    "内部流亡": [(1910, 0.80), (1916, 0.85), (1920, 0.45), (1924, 0.40), (1928, 0.50),
            (1933, 0.45), (1937, 0.35), (1945, 0.50), (1950, 0.55), (1955, 0.50),
            (1960, 0.55)],
}


def interp(path, year):
    pts = ANCHORS[path]
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= year <= y1:
            t = (year - y0) / (y1 - y0)
            return v0 + t * (v1 - v0)
    return pts[-1][1]


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 1917 的路径分岔({N_WRITERS} 位作家 cohort,1910-1960 逐年产量)")
    print("=" * 84)
    rng = random.Random(SEED + 20)
    writers = []
    for i in range(N_WRITERS):
        path = rng.choices(PATHS, weights=PATH_SHARE)[0]
        if path == "留下适应":
            year = rng.choices((1917, 1918, 1919), weights=(6, 3, 1))[0]
        elif path == "流亡":
            year = rng.choices(range(1918, 1923), weights=(1, 2, 3, 3, 2))[0]
        else:
            year = rng.choices((1917, 1919, 1921, 1922), weights=(2, 2, 3, 2))[0]
        factor = math.exp(rng.gauss(0, 0.3))             # 个人产量因子
        writers.append({"path": path, "year": year, "f": factor, "out": {}})
    window_n = sum(1 for w in writers if WINDOW[0] <= w["year"] <= WINDOW[1])
    rng_sw = random.Random(SEED + 21)                    # 流动事件用独立流
    switches = []                                        # 窗口后跨路径流动
    for w in writers:
        cur = w["path"]
        for y in YEARS:
            if y > WINDOW[1] and rng_sw.random() < SWITCH_P:
                cur = rng_sw.choice([p for p in PATHS if p != cur])
                switches.append((y, cur))
            if y < w["year"]:                            # 分流前:同一条线
                mean = 1.0
            else:
                mean = interp(cur, y) * w["f"]
            w["out"][y] = max(0, round(rng.gauss(mean, 0.45)))
    rate_window = window_n / (WINDOW[1] - WINDOW[0] + 1)
    rate_after = len(switches) / (1960 - WINDOW[1])
    print(f"\n窗口期(1917-1922)分流 {window_n}/{N_WRITERS} 人"
          f"(年均 {rate_window:.1f} 人/年);窗口后跨路径流动 {len(switches)} 人次"
          f"(年均 {rate_after:.2f} 人/年)")

    def traj(path, lo, hi):
        """路径产量轨迹:该路径作家(按最终去向追溯)在 lo..hi 年的平均产量。"""
        ws = [w for w in writers if w["path"] == path]
        return [stats.mean(w["out"][y] for w in ws) for y in range(lo, hi + 1)]

    def smooth(xs, w=2):
        return [stats.mean(xs[max(0, i - w):i + w + 1]) for i in range(len(xs))]

    pre = {p: stats.mean(traj(p, 1910, 1916)) for p in PATHS}
    print(f"\n分岔前(1910-1916)三线平均产量:{'/'.join(f'{p} {v:.2f}' for p, v in pre.items())}")
    t = {p: smooth(traj(p, 1917, 1960)) for p in PATHS}
    yrs = list(range(1917, 1961))
    print("分岔后(5 年滑动平均,每 6 年采样):")
    for y0 in range(1918, 1961, 6):
        i = min(range(len(yrs)), key=lambda k: abs(yrs[k] - y0))
        print(f"  {yrs[i]}:留下 {t['留下适应'][i]:.2f} / 流亡 {t['流亡'][i]:.2f}"
              f" / 内部流亡 {t['内部流亡'][i]:.2f}")

    # 断言 1:分流集中在窗口期,此后流动≈0(一次性分岔)
    assert window_n / N_WRITERS >= 0.95, f"窗口期分流占比应≥95%:{window_n}"
    assert len(switches) <= 6, f"窗口后流动应≤6 人次:{len(switches)}"
    assert rate_window >= 50 * max(rate_after, 1e-9), \
        f"窗口期年分流率应≥50× 窗口后:{rate_window:.1f} vs {rate_after:.2f}"
    print(f"\n✓ 幕三断言①通过:窗口期年分流率 {rate_window:.0f} 人/年,是窗口后"
          f"({rate_after:.2f} 人/年)的 {rate_window / max(rate_after, 1e-9):.0f}×"
          f";跨路径流动 {len(switches)}/{N_WRITERS} 人——一次性分岔")

    # 断言 2:三线分化+流亡线第二峰
    pre_gap = max(pre.values()) - min(pre.values())
    assert pre_gap <= 0.12, f"分岔前三线应同源(差≤0.12):{pre_gap:.2f}"
    for y0 in range(1925, 1951, 5):                      # 每个五年段都三线分明
        seg = [[t[p][y - 1917] for y in range(y0, y0 + 5)] for p in PATHS]
        spread = max(stats.mean(s) for s in seg) - min(stats.mean(s) for s in seg)
        assert spread >= 0.15, f"{y0} 年段三线应分化(极差≥0.15):{spread:.2f}"
    for a, b in (("留下适应", "流亡"), ("留下适应", "内部流亡"), ("流亡", "内部流亡")):
        gap = max(abs(t[a][y - 1917] - t[b][y - 1917]) for y in range(1923, 1956))
        assert gap >= 0.60, f"{a}与{b}应在某年分道≥0.60:{gap:.2f}"
    em, lv = t["流亡"], t["留下适应"]
    trough_y = min(range(1922, 1926), key=lambda y: em[y - 1917])
    trough = em[trough_y - 1917]
    peak_y = max(range(1926, 1937), key=lambda y: em[y - 1917])
    peak = em[peak_y - 1917]
    assert peak >= 1.8 * trough, f"流亡线第二峰应≥1.8× 初谷:{peak:.2f} vs {trough:.2f}"
    assert 1926 <= peak_y <= 1936
    assert peak > lv[peak_y - 1917], "第二峰年流亡线应反超留下线"
    late = stats.mean(em[y - 1917] for y in range(1946, 1956))
    assert late <= 0.30 * peak, f"1946-1955 流亡线应衰至第二峰的三成以下:{late:.2f}"
    print(f"✓ 幕三断言②通过:分岔前三线同源(极差 {pre_gap:.2f});分岔后每个五年段"
          f"三线极差≥0.15、两两最大分道≥0.60;流亡线 {trough_y} 年坠谷 {trough:.2f}"
          f"→{peak_y} 年「第二峰」{peak:.2f}(×{peak / trough:.1f},且峰年反超"
          f"留下线 {lv[peak_y - 1917]:.2f}),1946-1955 再落至 {late:.2f}")
    print("  ——流亡线第二峰=域外重建读者群(柏林→布拉格/巴黎的出版重心转移,")
    print("    通说流亡文学分期);一条 1917 的分岔线把一部文学史切成三部")
    return {"ratio": rate_window / max(rate_after, 1e-9), "switch": len(switches),
            "pre_gap": pre_gap, "trough": (trough_y, trough),
            "peak": (peak_y, peak), "late": late}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 人物网络:枢纽度数 {r1['hub_x']:.1f}× 于非枢纽,介数 top5"
          f"({'、'.join(r1['top5'][:3])}…)全为接线员;摘枢纽跨圈可达率"
          f" {r1['x_t']:.0%} vs 随机移除 {r1['x_r']:.0%},碎 {r1['comps_t']} 块")
    print(f"  ② 典型谱系:相似度按代距 {r2['s1']:.3f}>{r2['s2']:.3f}>{r2['s3']:.3f};"
          f"骨架保守 {r2['keep']:.0%},际遇维散开 {r2['disp']:.1f}×——骨架不变,国情在变")
    print(f"  ③ 路径分岔:窗口分流率为窗口后 {r3['ratio']:.0f}×(流动仅 {r3['switch']}"
          f" 人次);分岔前三线同源(极差 {r3['pre_gap']:.2f});流亡线"
          f" {r3['trough'][0]} 坠谷 {r3['trough'][1]:.2f}→{r3['peak'][0]} 第二峰"
          f" {r3['peak'][1]:.2f}——1917 一刀,文学史成三部")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
