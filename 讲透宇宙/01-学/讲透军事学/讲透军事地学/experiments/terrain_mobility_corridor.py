# -*- coding: utf-8 -*-
"""机动走廊分析:最短路径 vs 最小暴露路径 vs 综合路径(00/04 章配套实验)。

主题(与[讲透运筹学]家族互链不重复——那边管最短路/网络流的形式本体,
这边管"代价层怎么从地形里长出来"):
栅格地形(高程+地表类型)上,给定起点终点与观察哨,三条 Dijkstra
路径的对比——快而暴露的走廊 vs 慢而隐蔽的走廊 vs 折中走廊。

模型(虚构地形,不对应任何现实地区;敏感纪律:方法演示而已):
  地形:52×36 格网(格距 100 m)。高程=基面 40 m+南北两条跨向山脊
        (带一垭口一鞍部)+观察哨所在孤丘+种子噪声(平滑);
        地表:开阔/草甸/森林(森林冠层高 10 m,自带隐蔽)。
  通行规则:坡度(中心差分)>限值即不可通行;水域不可通行
        (桥格除外)——桥是走廊的咽喉。
  通视:观察哨(塔高 15 m)对格心(车高 2 m)的视线,沿线高程与
        冠层遮挡;目标格为森林则隐蔽(冠层高于车高)。
        暴露长=路径落在"至少被一个哨通视"的格上的长度。
  三种代价(Dijkstra 最小化):
    最短路径:地表加权路程(开阔 1.0/草甸 1.05/森林 2.6);
    最小暴露:cost = 3000×暴露长 + 加权路程(暴露压到近乎零优先);
    综合路径:cost = 加权路程 + λ×暴露长(λ=12,距离×暴露折中)。

三组断言:
  ① 绕行律:暴露代价使路径绕行——综合路径距离>最短路径、
     而暴露<最短路径(快路穿暴露区,折中路绕开它)。
  ② 排序律:暴露惩罚 0→λ→3000 单调加码,暴露长单调不增、
     距离单调不减——代价权重对走廊选择的单调响应。
  ③ 坡度截断律:收紧坡度限值,走廊逐条死掉——限值 22° 时
     北鞍部(约 27°)先死、只余南垭口(约 18°);限值 15° 时
     垭口亦死,脊线把目的地截断为不可达(Dijkstra 返回 None)。

⚠ 参数纪律(承家族 02/04 章:参数=兵棋观):高程/植被/坡度限值/
  λ 均为教科书级示例参数;结论只做结构比较(绕行/排序/截断),
  不做基数宣称。微地形分析的现实对应(自主系统的路线/能见度/
  障碍评估)见 01 章热线三(MWI West Point,检索校准 2026-09-07)。

跑法:python experiments/terrain_mobility_corridor.py(全部 assert 通过即 exit 0)
"""

import heapq
import math
import random

# ── 地形常量(格距 100 m)────────────────────────────────────────
W, H, CELL = 52, 36, 100.0
RIDGE_X, SIG_R = 26, 2.2          # 脊线位置/宽度(格)
RIDGE_H = 330.0                   # 脊线全高(m)
GAP_PASS, GAP_COL = 0.70, 0.53    # 南垭口(y≈27)/北鞍部(y≈12)的削峰系数
                                   # (垭口侧翼≈18°,鞍部侧翼≈27°,脊线≈45°)
CANOPY, MAST, VEHICLE = 10.0, 15.0, 2.0
OPEN, GRASS, FOREST = 1.0, 1.05, 2.6
SURF_CH = {OPEN: ".", GRASS: ",", FOREST: "T"}
START, GOAL = (3, 30), (48, 5)
OBS = [(35, 10), (33, 24)]        # 观察哨(东侧孤丘上)


def build_terrain(seed=7):
    """高程场+地表场:基面+脊线(双缺口)+哨丘+平滑噪声+西河+三片森林。"""
    rng = random.Random(seed)
    elev = [[40.0 + rng.uniform(-2.5, 2.5) for _ in range(W)] for _ in range(H)]
    for _ in range(2):                                   # 两轮平滑压噪声
        elev = [[(elev[y][x] + sum(elev[vy][vx] for vx, vy in _nb4(x, y)) / 5.0)
                 for x in range(W)] for y in range(H)]
    for y in range(H):                                   # 跨向山脊+双缺口
        gap = 1.0 - GAP_PASS * math.exp(-((y - 27) / 2.5) ** 2) \
                  - GAP_COL * math.exp(-((y - 12) / 2.5) ** 2)
        for x in range(W):
            elev[y][x] += RIDGE_H * gap * math.exp(-((x - RIDGE_X) / SIG_R) ** 2)
    for ox, oy in OBS:                                  # 观察哨孤丘
        for y in range(H):
            for x in range(W):
                elev[y][x] += (55.0 if (ox, oy) == OBS[0] else 45.0) \
                    * math.exp(-((x - ox) ** 2 + (y - oy) ** 2) / (2 * 2.5 ** 2))
    surf = [[OPEN] * W for _ in range(H)]
    for cx, cy, r in ((17, 27, 4), (38, 28, 5), (45, 16, 4)):
        for y in range(H):
            for x in range(W):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    surf[y][x] = FOREST
    for y in range(H):                                  # 西河(桥在 x=18)
        for x in range(24):
            if y == 20:
                surf[y][x] = -1.0                       # 水域
    surf[20][18] = OPEN                                 # 桥格
    for y in range(H):                                  # 河岸草甸
        for x in range(W):
            if surf[y][x] == OPEN and any(surf[vy][vx] == -1.0
                    for vx, vy in _nb4(x, y)):
                surf[y][x] = GRASS
    return elev, surf


def _nb4(x, y):
    return [(min(max(x + dx, 0), W - 1), min(max(y + dy, 0), H - 1))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]


def slope_field(elev):
    """中心差分坡度(度):s = atan(|∇z|/格距)。"""
    sl = [[0.0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            dzx = (elev[y][min(x + 1, W - 1)] - elev[y][max(x - 1, 0)]) / (2 * CELL)
            dzy = (elev[min(y + 1, H - 1)][x] - elev[max(y - 1, 0)][x]) / (2 * CELL)
            sl[y][x] = math.degrees(math.atan(math.hypot(dzx, dzy)))
    return sl


def los(elev, surf, o, c):
    """观察哨 o 对格 c 的通视:沿线采样,高程或冠层抬过视线即遮蔽。"""
    (x0, y0), (x1, y1) = o, c
    if surf[y1][x1] == FOREST:
        return False                                    # 森林格自带隐蔽
    z0, z1 = elev[y0][x0] + MAST, elev[y1][x1] + VEHICLE
    d = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(d * 2))
    for i in range(1, n):
        t = i / n
        x, y = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
        xi, yi = int(round(x)), int(round(y))
        sight = z0 + t * (z1 - z0)
        obst = elev[yi][xi] + (CANOPY if surf[yi][xi] == FOREST else 0.0)
        if obst > sight:
            return False
    return True


def exposure_set(elev, surf):
    """暴露格集合:至少被一个观察哨通视的格。"""
    ex = set()
    for y in range(H):
        for x in range(W):
            if any(los(elev, surf, o, (x, y)) for o in OBS):
                ex.add((x, y))
    return ex


def dijkstra(elev, surf, sl, ex, slope_limit, w_exp):
    """w_exp=暴露惩罚(每暴露米加价);返回(路径,几何长,暴露长)或 None。"""
    blocked = lambda x, y: (sl[y][x] > slope_limit) or \
        (surf[y][x] == -1.0 and (x, y) != (18, 20))
    if blocked(*START) or blocked(*GOAL):
        return None
    dist = {START: 0.0}
    prev = {}
    pq = [(0.0, START)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        if u == GOAL:
            break
        ux, uy = u
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            v = (ux + dx, uy + dy)
            if not (0 <= v[0] < W and 0 <= v[1] < H) or blocked(*v):
                continue
            step = math.hypot(dx, dy) * CELL
            cost = step * (surf[v[1]][v[0]] if surf[v[1]][v[0]] > 0 else OPEN) \
                + w_exp * (step if v in ex else 0.0)
            nd = d + cost
            if nd < dist.get(v, math.inf):
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))
    if GOAL not in dist:
        return None
    path, node = [GOAL], GOAL
    while node != START:
        node = prev[node]
        path.append(node)
    path.reverse()
    length = exposed = 0.0
    for i in range(1, len(path)):
        a, b = path[i - 1], path[i]
        step = math.hypot(b[0] - a[0], b[1] - a[1]) * CELL
        length += step
        exposed += step if b in ex else 0.0
    return path, length, exposed


def draw(elev, surf, sl, ex, routes=()):
    """ASCII 战场图:地形底+暴露叠层+路线。"""
    grid = []
    for y in range(H):
        row = []
        for x in range(W):
            if surf[y][x] == -1.0:
                ch = "=" if (x, y) == (12, 20) else "~"
            elif sl[y][x] > 22:
                ch = "^"                        # 陡坡(默认限值外)
            else:
                ch = SURF_CH[surf[y][x]]
            row.append("*" if (x, y) in ex and surf[y][x] != FOREST else ch)
        grid.append(row)
    for (x, y) in OBS:
        grid[y][x] = "O"
    marks = {START: "S", GOAL: "G"}
    for i, r in enumerate(routes):
        for c in r:
            marks.setdefault(c, str(i + 1))
    for (x, y), ch in marks.items():
        grid[y][x] = ch
    return "\n".join("".join(r) for r in grid)


def main():
    elev, surf = build_terrain()
    sl = slope_field(elev)
    ex = exposure_set(elev, surf)
    print("=" * 76)
    print(f"机动走廊分析:{W}×{H} 格网(格距 {CELL:.0f} m),"
          f"起点 {START} → 终点 {GOAL},观察哨 {OBS}")
    print("地形:^陡坡 T森林 ,草甸 .开阔 ~水域 =桥 O哨 *暴露格")
    print("=" * 76)
    print(draw(elev, surf, sl, ex))

    # ── 断言组①+②:绕行律与排序律 ──────────────────────────
    p_short = dijkstra(elev, surf, sl, ex, 22.0, 0.0)
    p_combi = dijkstra(elev, surf, sl, ex, 22.0, 12.0)
    p_stlth = dijkstra(elev, surf, sl, ex, 22.0, 3000.0)
    (_, L_s, E_s), (_, L_c, E_c), (_, L_t, E_t) = p_short, p_combi, p_stlth
    print(f"\n[1] 绕行律与排序律(坡度限值 22°;暴露惩罚 0/12/3000)")
    print(f"{'路径':<12}{'几何长(m)':>10}{'暴露长(m)':>10}")
    for name, (_, L, E) in (("最短路径", p_short), ("综合路径", p_combi),
                            ("最小暴露", p_stlth)):
        print(f"{name:<12}{L:>10.0f}{E:>10.0f}")
    assert L_c > L_s and E_c < E_s, "①绕行律:综合路径应距离>最短且暴露<最短"
    assert E_s > E_c >= E_t, "②排序律:暴露长随惩罚单调不增"
    assert L_s < L_c <= L_t, "②排序律:几何长随惩罚单调不减"
    print(f"  ① 绕行律 ✓ 综合路径比最短路径长 {L_c - L_s:.0f} m,"
          f" 暴露少 {E_s - E_c:.0f} m——快路穿暴露区,折中路绕开它")
    print(f"  ② 排序律 ✓ 暴露 {E_s:.0f}→{E_c:.0f}→{E_t:.0f} m 单调降,"
          f" 距离 {L_s:.0f}→{L_c:.0f}→{L_t:.0f} m 单调升")

    # ── 断言组③:坡度截断律(限值阶梯 30°→22°→15°)─────────
    print(f"\n[2] 坡度截断律(垭口约 18°,鞍部约 27°,脊线约 43°)")
    r22 = dijkstra(elev, surf, sl, ex, 22.0, 0.0)
    r15 = dijkstra(elev, surf, sl, ex, 15.0, 0.0)
    cross = lambda p: [c for c in p[0] if abs(c[0] - RIDGE_X) <= 1]
    y22 = [c[1] for c in cross(r22)]
    assert r22 is not None, "22°:南垭口应仍可通行"
    assert max(y22) >= 25 and max(y22) <= 29, "22°:过脊点应走南垭口(y≈27)"
    assert r15 is None, "15°:垭口亦被截断,目的地应不可达"
    print(f"  限值 22°:可达 ✓ 但过脊点 y={max(y22)}"
          f"(南垭口)——北鞍部(约 27°)已被截断,走廊从两条减为一条")
    print(f"  限值 15°:Dijkstra 返回 None ✓——脊线把目的地彻底截断:"
          f"坡度阈值是走廊存在性的硬开关")
    r30 = dijkstra(elev, surf, sl, ex, 30.0, 0.0)
    ycross = max(c[1] for c in cross(r30))
    assert r30 is not None and ycross <= 15, "30°:应走北鞍部(更短)"
    print(f"  限值 30°:可达 ✓ 过脊点 y={ycross}(北鞍部复活,"
          f"走廊回到两条,最短路取更短的鞍部)")

    print("\n" + "=" * 76)
    print(draw(elev, surf, sl, ex, routes=[p_short[0], p_stlth[0]]))
    print("三组断言全部通过:绕行律 / 排序律 / 坡度截断律 ✓")
    print("⚠ 参数纪律:高程/植被/限值/λ=教科书级示例,结论只做结构比较;")
    print("  微地形分析的现实进展见 01 章热线三(MWI,检索校准 2026-09-07)。")


if __name__ == "__main__":
    main()
