#!/usr/bin/env python3
"""lab05 · 抽象解释：区间域、假阳性与 CEGAR 一轮（05 章 §二/§三）。
程序: x=0; y=0; while (x<8) { x=x+3; y=y+x; }
具体执行: x∈{0,3,6,9}, 出口 x=9, y=3+6+9=18（逐轮 y=3,9,18）。
断言 y==18：具体成立；区间域（带加宽）只能给 y∈[0,+∞] → 假阳性（证不出）。
CEGAR：从具体轨迹提炼谓词 x∈{0,3,6,9} → 精化域精确复算 → y==18 可证。
手推锚点（章内§二/§三）: 区间三轮 [0,0]→[0,3]→[0,6]，第 3 轮加宽后 [0,+∞]；
谓词精化后 x 轮换 {0,3,6,9}，y 精确到 18。
"""
from fractions import Fraction

INF = None  # 用 None 表示 +∞ 上界


def iv_str(iv):
    """打印用: (0, None) → [0,+∞]。"""
    lo, hi = iv
    return f"[{lo},+∞]" if hi is None else f"[{lo},{hi}]"


def iv_add(a, b):  # 区间加
    lo = a[0] + b[0]
    hi = (None if a[1] is None or b[1] is None else a[1] + b[1])
    return (lo, hi)


def iv_join(a, b):  # 并/汇合
    return (min(a[0], b[0]),
            None if a[1] is None or b[1] is None else max(a[1], b[1]))


def interval_exec(widen=True):
    """区间域不动点迭代。返回出口 (x_iv, y_iv) 及逐轮 trail。"""
    x, y = (Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))  # 入口
    trail = []
    for it in range(1, 30):
        # 循环体: x=x+3; y=y+x （对区间: 顺序复合）
        nx = iv_add(x, (3, 3))
        ny = iv_add(y, nx)
        # 汇合（不动点）
        jx, jy = iv_join(x, nx), iv_join(y, ny)
        if widen and it >= 3:  # 第 3 轮起加宽: 上界在涨 → 冲 +∞
            if jx[1] is not None and nx[1] is not None and nx[1] > x[1]:
                jx = (jx[0], None)
            if ny[1] is not None and ny[1] > y[1]:
                jy = (jy[0], None)
        trail.append((it, jx, jy))
        if (jx, jy) == (x, y):
            break
        x, y = jx, jy
    return x, y, trail


def concrete_exec():
    x = y = 0
    while x < 8:
        x += 3; y += x
    return x, y  # (9, 18)


def refined_exec():
    """CEGAR 精化: 谓词 x∈{0,3,6,9}（从具体轨迹提炼），精化域用精确集合。"""
    xs = {0}; ys = {0}
    changed = True
    while changed:
        changed = False
        for xv in list(xs):
            nx = xv + 3
            if nx not in xs and nx <= 9:  # 谓词域内且循环条件 x<8 的下一步
                xs.add(nx); changed = True
    # y 随 x 精确累积（按 x 值轮次）
    y_vals = {0: 0}
    order = sorted(xs)
    acc = 0
    for xv in order:
        if xv < 8:  # 进入循环体的轮次
            acc += xv + 3
            y_vals[xv + 3] = acc
    exit_y = y_vals[9]
    return sorted(xs), exit_y


def selftest():
    cx, cy = concrete_exec()
    assert (cx, cy) == (9, 18), (cx, cy)
    xiv, yiv, trail = interval_exec()
    assert xiv == (0, None) and yiv == (0, None), (xiv, yiv)  # 加宽后均 [0,+∞]
    xs, ey = refined_exec()
    assert xs == [0, 3, 6, 9] and ey == 18, (xs, ey)
    print(f"具体: 出口 (x,y)=({cx},{cy})，y 逐轮 3,9,18")
    for it, jx, jy in trail:
        tail = "  ← 第3轮起加宽" if it == 3 else ""
        print(f"  区间第{it}轮: x∈{iv_str(jx)}, y∈{iv_str(jy)}{tail}")
    print(f"区间域: x∈{iv_str(xiv)}, y∈{iv_str(yiv)} → 证不出 y==18（假阳性）")
    print(f"CEGAR 精化: x 轮换 {xs}, y 精确 = {ey} → y==18 可证 ✓")
    print("lab05 自检通过")


if __name__ == "__main__":
    selftest()
