# -*- coding: utf-8 -*-
"""啤酒游戏与牛鞭效应:四级供应链的方差放大模拟。

00 章 §七(反直觉:理性个体 → 失控系统)与 04 章走廊 3(仿真走廊)配套实验。纯标准库。

设定: 四级供应链 零售(0) → 批发(1) → 分销(2) → 工厂(3),相邻两级间提前期 L(参数化)。
     终端需求一次脉冲: 脉冲窗口内翻倍、随后回到基线(另加正态噪声, 可关)。
     各级按库存目标订货(order-up-to + 指数平滑预测, 参数 alpha / safety):
       预测   f ← f + α·(预测基线 − f)     基线 = 下游订单(无共享)或终端需求(信息共享)
       目标   y = f·(L + 1 + safety)
       订货   q = max(0, y − (净库存 + 在途))
     订单当期即达上游;货物经 L 周在途到达;未满足需求记为欠交(净库存为负可透支)。
对照: 三条断言是供应链文献经典结果的教学化(Forrester 1958 系统动力学首录;
     Sterman 1989 啤酒游戏实验;Lee-Padmanabhan-Whang 1997 理性牛鞭):
     ① 订单方差逐级放大(牛鞭:即使每级都做"理性"的库存目标控制)
     ② 信息共享(终端 POS 直达各级)显著削弱放大
     ③ 放大倍数对提前期单调(提前期越长,鞭子越响)
场景: 基线需求 100/周,脉冲窗口第 4-7 周(0 基)翻倍到 200;噪声 σ=15;
     蒙特卡洛 300 次重复取均值做断言,另跑一次零噪声确定性局做展示。

跑法: python experiments/bullwhip_beer_game.py
"""

import math
import random

BASE = 100.0                 # 基线需求
PULSE_START, PULSE_END = 4, 8    # 一次脉冲: 第 4..7 周(0 基)需求翻倍
HORIZON = 60                 # 模拟周数
ECH = 4                      # 零售/批发/分销/工厂
NAMES = ("零售", "批发", "分销", "工厂")


def terminal_demand(t, sigma, rng):
    """终端需求: 基线,脉冲窗口翻倍,叠加正态噪声(σ=0 即确定性局)。"""
    d = BASE * (2.0 if PULSE_START <= t < PULSE_END else 1.0)
    if sigma > 0.0:
        d += rng.gauss(0.0, sigma)
    return max(d, 0.0)


def simulate(lead_time=2, info_share=False, alpha=0.3, safety=1.0,
             sigma=15.0, seed=7, horizon=HORIZON):
    """跑一局啤酒游戏,返回 (各级订单序列, 终端需求序列)。"""
    rng = random.Random(seed)
    f = [BASE] * ECH                       # 各级初始预测 = 基线(暖启动)
    net = [BASE * (1.0 + safety)] * ECH    # 初始净库存 = 稳态解
    pipe = [[BASE] * lead_time for _ in range(ECH)]   # 在途管道: 每周到达一船基线量
    orders = [[] for _ in range(ECH)]
    demand = []

    for t in range(horizon):
        d = terminal_demand(t, sigma, rng)
        demand.append(d)
        for k in range(ECH):               # 从零售往上逐级结算(订单当期即达)
            incoming = pipe[k].pop(0)      # 1) 收到 L 周前发出的货
            net[k] += incoming
            faced = d if k == 0 else orders[k - 1][t]   # 要满足的下游订单
            net[k] -= faced                            # 2) 出货(不够则欠交)
            basis = d if info_share else faced         # 3) 预测基线: POS 共享与否
            f[k] += alpha * (basis - f[k])
            y = f[k] * (lead_time + 1.0 + safety)      # 4) 库存目标
            ip = net[k] + sum(pipe[k])                 # 库存位置 = 净库存 + 在途
            q = max(0.0, y - ip)                       # 5) 本级订货(不许为负)
            orders[k].append(q)
            pipe[k].append(q)                          # 订货经 L 周在途到达
    return orders, demand


def var(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def amplification(orders, demand):
    """各级订单方差相对终端需求方差的放大倍数(度量窗: 脉冲前一周起)。"""
    t0 = PULSE_START - 1
    vd = var(demand[t0:])
    return [var(o[t0:]) / vd for o in orders]


def mc_amplification(reps=300, **kw):
    """蒙特卡洛均值放大倍数(每次重复换种子)。"""
    agg = [0.0] * ECH
    for r in range(reps):
        kw2 = dict(kw)
        kw2["seed"] = 1000 * r + kw.get("seed", 7) + 1
        orders, demand = simulate(**kw2)
        for k, a in enumerate(amplification(orders, demand)):
            agg[k] += a
    return [a / reps for a in agg]


def show_series(orders, demand, upto=32):
    print(f"{'周':>3} | {'终端需求':>8} | " + " | ".join(f"{n+'订货':>8}" for n in NAMES))
    for t in range(upto):
        row = " | ".join(f"{orders[k][t]:8.0f}" for k in range(ECH))
        print(f"{t:3d} | {demand[t]:8.0f} | {row}")


def main():
    print("=" * 68)
    print("Part 1 确定性局: 终端需求一次脉冲(第 4-7 周翻倍), L=2, 无信息共享")
    print("=" * 68)
    orders, demand = simulate(lead_time=2, info_share=False, sigma=0.0, seed=1)
    show_series(orders, demand)
    det_amp = amplification(orders, demand)
    print("方差放大倍数(相对终端需求): " +
          " → ".join(f"{n} {a:.1f}" for n, a in zip(NAMES, det_amp)))

    print()
    print("=" * 68)
    print("Part 2 信息共享对照: 300 次蒙特卡洛, L=2, σ=15, 均值放大倍数")
    print("=" * 68)
    amp_no = mc_amplification(lead_time=2, info_share=False)
    amp_sh = mc_amplification(lead_time=2, info_share=True)
    print(f"{'级':>4} | {'无共享':>8} | {'POS 共享':>8} | {'降幅':>7}")
    for k in range(ECH):
        drop = 1.0 - amp_sh[k] / amp_no[k]
        print(f"{NAMES[k]:>4} | {amp_no[k]:8.2f} | {amp_sh[k]:8.2f} | {drop:6.0%}")

    print()
    print("=" * 68)
    print("Part 3 提前期扫描: L ∈ {1,2,3,4}, 无共享, 工厂级放大倍数(300 次均值)")
    print("=" * 68)
    lead_amp = []
    for L in (1, 2, 3, 4):
        a = mc_amplification(lead_time=L, info_share=False)[-1]
        lead_amp.append(a)
        print(f"L={L}: 工厂级放大 = {a:.2f}")

    print()
    print("读数:")
    print("  · Part 1: 终端只翻了一倍,工厂订货冲到 600+ 又砸穿到 0——")
    print("    没有任何人犯错:每级都在忠实地做库存目标控制,放大是结构性的")
    print("    (预测平滑 × 提前期 × 库存目标的乘法,Sterman 的锚定-调整机制)。")
    print("  · Part 2: 终端 POS 直达各级,工厂级放大塌掉八成(链式增长 34 倍 → 5 倍)——")
    print("    但不归一:上游库存仍要消化下游订单的物理冲击。信息共享削弱的是")
    print("    『把下游的过激反应当需求』的那一部分——共享的价值不在『快』,在『方差』。")
    print("  · Part 3: L 每加一周,鞭子响一截——库存目标随 L 线性变大、")
    print("    反馈回路随 L 变慢,两个机制同向叠加(供应链缩短提前期的全部理由)。")

    # ---------- 自验证断言 ----------
    # ① 牛鞭: 方差逐级放大(确定性局与蒙特卡洛均值都要求严格链式)
    for k in range(ECH - 1):
        assert det_amp[k + 1] > det_amp[k], "确定性局: 放大应逐级严格上升"
    assert det_amp[0] > 1.0, "零售级就应放大终端需求方差(需求信号处理)"
    assert det_amp[-1] > 2.0 * det_amp[0], "工厂级放大应显著超过零售级(经典啤酒游戏量级)"
    for k in range(ECH - 1):
        assert amp_no[k + 1] > amp_no[k], "蒙特卡洛: 放大应逐级严格上升"
    assert amp_no[-1] > 3.0 * amp_sh[-1], \
        f"信息共享应显著削弱放大(实测 无共享{amp_no[-1]:.1f} vs 共享{amp_sh[-1]:.1f})"
    assert all(amp_sh[k] < amp_no[k] for k in range(1, ECH)), "共享应削弱每一上游级的放大"
    growth_sh = amp_sh[-1] / amp_sh[0]
    growth_no = amp_no[-1] / amp_no[0]
    assert growth_sh < 0.5 * growth_no, \
        f"共享后链式增长率应大幅放缓(实测 {growth_sh:.1f} vs 无共享 {growth_no:.1f})"

    # ③ 提前期单调: L 越长鞭子越响
    for a, b in zip(lead_amp, lead_amp[1:]):
        assert b > a, "工厂级放大倍数应随提前期严格上升"
    assert lead_amp[-1] > 2.0 * lead_amp[0], "L=4 的放大应显著超过 L=1(提前期代价可观)"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
