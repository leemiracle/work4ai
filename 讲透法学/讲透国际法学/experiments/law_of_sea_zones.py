# -*- coding: utf-8 -*-
"""
law_of_sea_zones.py — 海洋法距离权利演示（UNCLOS 分区的平面简化模型）

对应章：00-体系结构（§二 海洋分区）/ 03-可构造与结构（§一 UNCLOS 议题束工艺）/
       04-国际法学转代码（走廊①：海洋法几何——"算得准"档）
GB/T 82040 国际法学 · 家族层实验

演示内容：
  1. 距离权利三区：领海 12 海里（主权所及，无害通过）/ 毗连区 24 海里
     （仅海关·财政·移民·卫生四类管制，UNCLOS 第 33 条）/ 专属经济区 200 海里
     （资源性主权权利，第 56-77 条）/ 之外公海（第 87 条六大自由）
  2. 两国重叠 EEZ 的等距线（中间线）简化构造——逐点构造法的教学版
  3. 岛屿扩展效应与"岩石条款"（第 121(3) 条）：同一个布尔值，
     代码里一行，法庭里十年（见 04 章裂缝清单）

模型边界（必读）：
  - 平面欧氏几何教学模型；真实划界必须用大地测量学（WGS84 椭球测地线）
    与法定基点/基线库（正常基线=沿海低潮线；曲折海岸可划直线基线）
  - 等距线取"简化中间线"：对每对基线逐点构造；真实案件的基点取舍、
    海岸凹凸与"有关情况"修正远比本演示复杂（UNCLOS 第 74/83 条要求
    "公平解决"——规范判断在几何之外）
  - 岩石条款取保守读法：岩礁仅产生领海，不产生毗连区/EEZ
    （毗连区是否随领海保留，学说有争议；本模型从简）

运行：python law_of_sea_zones.py   （纯标准库，assert 自验证，exit 0）
"""

import math

# ---------------------------------------------------------------- 分区常量

TERRITORIAL_NM = 12.0   # 领海宽度上限（UNCLOS 第 3 条）
CONTIGUOUS_NM = 24.0    # 毗连区外限（第 33 条：自领海基线量起不超过 24 海里）
EEZ_NM = 200.0          # 专属经济区外限（第 57 条）

ZONE_RANK = {           # 权利强度递减序：用于"多重主张取最强"
    "territorial_sea": 0,
    "contiguous_zone": 1,
    "eez": 2,
    "high_seas": 3,
}


def zone_from_distance(dist_nm: float) -> str:
    """单基线距离 → 海域法域（04 章走廊① 的 if-elif 直译）。"""
    if dist_nm <= TERRITORIAL_NM:
        return "territorial_sea"   # 主权所及，但须容无害通过（第 17 条）
    if dist_nm <= CONTIGUOUS_NM:
        return "contiguous_zone"   # 四类管制权（第 33 条），非主权
    if dist_nm <= EEZ_NM:
        return "eez"               # 资源性主权权利（第 56 条），非主权
    return "high_seas"             # 公海自由（第 87 条）


# ---------------------------------------------------------------- 几何基元

def point_segment_distance(px: float, py: float,
                           ax: float, ay: float,
                           bx: float, by: float) -> float:
    """点到线段的欧氏距离（基线由折线段组成）。"""
    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0.0:                       # 退化：单点基线（岛屿）
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))                   # 投影参数截断到 [0,1]
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def polyline_distance(px: float, py: float, polyline) -> float:
    """点到基线折线（顶点列表）的最小距离 = 到各线段距离取 min。"""
    return min(
        point_segment_distance(px, py,
                               polyline[i][0], polyline[i][1],
                               polyline[i + 1][0], polyline[i + 1][1])
        for i in range(len(polyline) - 1)
    )


# ---------------------------------------------------------------- 沿海国模型

class CoastalState:
    """沿海国 = 若干基线折线（全效力）+ 若干岛屿/岩礁点。

    island = (x, y, is_rock)：
      is_rock=False → 第 121(1)(2) 条岛屿，全效力（领海/毗连区/EEZ）
      is_rock=True  → 第 121(3) 条岩礁："不能维持人类居住或其本身经济
                      生活的岩礁不应有专属经济区"——注意：'能不能维持
                      人类居住'是法律-事实认定（有淡水算吗？季节性渔民
                      算吗？），代码只能把它做成开关，现实里是一场诉讼
    """

    def __init__(self, name, baselines, features=()):
        self.name = name
        self.baselines = list(baselines)
        self.features = list(features)

    def _full_effect_distance(self, px, py):
        """到全部全效力基线（含非岩石岛屿）的最小距离。"""
        ds = [polyline_distance(px, py, b) for b in self.baselines]
        ds += [math.hypot(px - fx, py - fy)
               for fx, fy, rock in self.features if not rock]
        return min(ds) if ds else math.inf

    def _rock_distance(self, px, py):
        """到岩礁点的最小距离（岩礁只产生领海）。"""
        ds = [math.hypot(px - fx, py - fy)
              for fx, fy, rock in self.features if rock]
        return min(ds) if ds else math.inf

    def distance(self, px, py):
        return min(self._full_effect_distance(px, py),
                   self._rock_distance(px, py))

    def zone(self, px, py):
        """该点相对本国的法域：全效力主张与岩礁主张取更强者。"""
        z_full = zone_from_distance(self._full_effect_distance(px, py))
        d_rock = self._rock_distance(px, py)
        z_rock = "territorial_sea" if d_rock <= TERRITORIAL_NM else "high_seas"
        return z_full if ZONE_RANK[z_full] <= ZONE_RANK[z_rock] else z_rock


# ---------------------------------------------------------------- 场景布置
# A 国：直线海岸 x=0（陆地在 x<0），基线自 (0,-20) 到 (0,20)；
#       附属岛屿 (100,5)（切换 rock 开关演示第 121(3) 条）
# B 国：直线海岸 x=COAST_B（陆地在 x>COAST_B），两海岸相距 COAST_B 海里

COAST_A_BASELINE = [(0.0, -20.0), (0.0, 20.0)]
ISLAND_A = (100.0, 5.0)
COAST_B = 340.0
COAST_B_BASELINE = [(COAST_B, -20.0), (COAST_B, 20.0)]


def build_A(island=ISLAND_A, rock=False):
    feats = [(*island, rock)] if island else []
    return CoastalState("A", [COAST_A_BASELINE], feats)


def build_B(coast_x=COAST_B):
    return CoastalState("B", [[(coast_x, -20.0), (coast_x, 20.0)]])


# ---------------------------------------------------------------- 测试一：分区判定

def test_zone_from_distance():
    assert zone_from_distance(0.0) == "territorial_sea"
    assert zone_from_distance(12.0) == "territorial_sea"      # 边界含于领海
    assert zone_from_distance(12.01) == "contiguous_zone"
    assert zone_from_distance(24.0) == "contiguous_zone"
    assert zone_from_distance(24.01) == "eez"
    assert zone_from_distance(200.0) == "eez"
    assert zone_from_distance(200.01) == "high_seas"
    # 包络有序性：三区半径严格递增（UNCLOS 距离权利的"套娃"结构）
    assert TERRITORIAL_NM < CONTIGUOUS_NM < EEZ_NM


def test_zone_classification():
    a = build_A(island=None)               # 先看纯海岸（无岛屿）
    cases = [
        (5.0,   0.0, "territorial_sea"),   # 基线内 5 海里
        (18.0,  0.0, "contiguous_zone"),   # 12<18<=24
        (30.0,  0.0, "eez"),               # 24<30<=200
        (170.0, 400.0, "high_seas"),       # 离一切基线均 >200（开放大洋）
    ]
    for x, y, want in cases:
        got = a.zone(x, y)
        assert got == want, f"({x},{y}): expect {want}, got {got}"
        print(f"  A.zone({x:>6.1f},{y:>6.1f}) = {got:<16} d={a.distance(x, y):7.2f} nm")


def test_monotonicity():
    """沿正法线方向离岸，法域权利单调减弱（套娃只会越套越大不会反转）。"""
    a = build_A(island=None)
    prev = -1
    for x in range(1, 260, 3):
        rank = ZONE_RANK[a.zone(float(x), 0.0)]
        assert rank >= prev, f"rank decreased at x={x}"
        prev = rank
    assert prev == 3  # 最终抵达公海


# ---------------------------------------------------------------- 测试二：重叠 EEZ 与等距线

def overlap_point(a, b, x, y):
    """两国的 EEZ 主张在同一海点重叠（对各自基线均 <=200）。"""
    return (a.distance(x, y) <= EEZ_NM) and (b.distance(x, y) <= EEZ_NM)


def test_eez_overlap():
    a, b = build_A(island=None), build_B(COAST_B)   # 两海岸相距 340
    assert overlap_point(a, b, 170.0, 0.0)          # 170+170<=200*2 → 重叠
    assert not overlap_point(a, b, 130.0, 0.0)      # B 侧 210>200 → 不重叠
    assert not overlap_point(a, b, 210.0, 0.0)      # A 侧 210>200 → 不重叠
    # 重叠带宽度 = 200+200-340 = 60 海里，即 x∈[140,200]
    assert overlap_point(a, b, 140.0, 0.0)
    assert overlap_point(a, b, 200.0, 0.0)
    assert not overlap_point(a, b, 139.9, 0.0)
    print(f"  coasts 340 nm apart -> EEZ overlap band width = "
          f"{2 * EEZ_NM - COAST_B:.0f} nm (x in [140, 200])")


def test_equidistance_line():
    """简化等距线（中间线）：逐点构造 |dA - dB| ≈ 0 的轨迹。

    两平行直线基线特例下，中间线恰为 x = COAST_B/2 = 170。
    真实案件：基点取舍 + 海岸凹凸 + '有关情况'修正 + 成比例检验，
    远非纯几何（UNCLOS 第 74/83 条'公平解决'）。本测试只验证
    '等距构造'这一步的几何自洽。
    """
    a, b = build_A(island=None), build_B(COAST_B)
    median_points = []
    for y in range(-18, 19, 6):
        best_x, best_gap = None, 1e9
        for i in range(564, 798):                    # x in [141, 199.5]
            x = i * 0.25
            if not overlap_point(a, b, x, float(y)):
                continue
            gap = abs(a.distance(x, y) - b.distance(x, y))
            if gap < best_gap:
                best_x, best_gap = x, gap
        if best_x is not None and best_gap < 0.05:
            median_points.append((best_x, float(y)))

    assert len(median_points) == 7                   # 每条扫描线各得一点
    for x, y in median_points:
        dA, dB = a.distance(x, y), b.distance(x, y)
        assert abs(dA - dB) < 0.05, f"not equidistant at ({x},{y})"
        assert TERRITORIAL_NM < min(dA, dB)          # 中间线在两侧领海之外
        assert max(dA, dB) <= EEZ_NM                 # 且落在双方 EEZ 主张内
    xs = [p[0] for p in median_points]
    assert all(abs(x - COAST_B / 2.0) < 0.5 for x in xs)  # 平行基线特例：x=170
    print(f"  median line: {len(median_points)} points, "
          f"x in [{min(xs):.2f}, {max(xs):.2f}] (theory: x=170.00)")


def test_no_overlap_when_far():
    """两海岸相距 420>400 海里：EEZ 不再重叠 → 无划界问题，中间出现公海走廊。

    00 章练习的手动版：距离不足则无划界问题——反过来，
    距离够远则连'等距线'这个题目都不存在。
    """
    far = 420.0
    a, b = build_A(island=None), build_B(far)
    for i in range(201, 220):                        # 走廊 x∈(200,220)
        assert not overlap_point(a, b, float(i), 0.0)
    assert a.zone(210.0, 0.0) == "high_seas"
    assert b.zone(210.0, 0.0) == "high_seas"         # 对两国都是公海
    print(f"  coasts {far:.0f} nm apart -> no EEZ overlap; "
          f"high-seas corridor at x in (200, 220)")


# ---------------------------------------------------------------- 测试三：岛屿与岩石

def test_island_effect():
    """岛屿把 A 国的权利包络向外推 100 海里（第 121(1)(2) 条：岛屿全效力）。"""
    a = build_A(ISLAND_A, rock=False)
    # (250,5)：距大陆基线 250>200（大陆 EEZ 不及），距岛 150<=200 → 岛的 EEZ
    assert a._full_effect_distance(250.0, 5.0) == 150.0
    assert a.zone(250.0, 5.0) == "eez", "island should extend the EEZ envelope"
    # 岛自身周边：12/24 海里套娃照常生成
    assert a.zone(100.0, 5.0 + 12.0) == "territorial_sea"   # 边界含于领海
    assert a.zone(100.0, 5.0 + 13.0) == "contiguous_zone"
    assert a.zone(100.0, 5.0 + 24.0) == "contiguous_zone"
    assert a.zone(100.0, 5.0 + 25.0) == "eez"


def test_rock_provision():
    """岩石条款（第 121(3) 条）：is_rock=True → 岛屿只产生领海。

    同一个地理点、同一行几何代码，法域因一个法律-事实认定而翻转——
    '能不能维持人类居住'不是坐标的函数，是诉讼的结论。
    """
    a = build_A(ISLAND_A, rock=True)
    # (250,5)：距大陆 250>200，距岩礁 150>12 → 岩礁无 EEZ → 公海
    assert a.zone(250.0, 5.0) == "high_seas", "rock must not generate EEZ"
    # 岩礁领海仍在：距岩礁 5 海里处是领海
    assert a.zone(105.0, 5.0) == "territorial_sea"
    # 距岩礁 13 海里（>12）：岩礁不再给任何区；此处距大陆 105<=200 → EEZ
    assert a.zone(113.0, 5.0) == "eez"


# ---------------------------------------------------------------- 主程序

def main():
    print("UNCLOS distance-rights demo (flat-earth teaching model)")
    print(f"zones: TS<={TERRITORIAL_NM:.0f}nm  CZ<={CONTIGUOUS_NM:.0f}nm  "
          f"EEZ<={EEZ_NM:.0f}nm  then high seas\n")

    for fn in (test_zone_from_distance, test_zone_classification,
               test_monotonicity, test_eez_overlap, test_equidistance_line,
               test_no_overlap_when_far, test_island_effect,
               test_rock_provision):
        print(f"[{fn.__name__}]")
        fn()
    print("\nALL ASSERTIONS PASSED")


if __name__ == "__main__":
    main()
