#!/usr/bin/env python3
"""讲透博弈论 CLI · 拍卖行：python cli/auction_house.py [--demo]
--demo：均衡机器人自拍 2000 场（n=4，估值 ~U[0,100]；一价出 0.75v（BNE (n−1)/n·v，08 章）、
        二价出 v（占优，08 章）、英式坚持到价格过 v 才退）——三拍卖平均卖价 vs 理论
        E[次高] = 100·(n−1)/(n+1) = 60（容差 ±2，08/13 章收益等价的 CLI 版）；
交互：你与 3 个均衡机器人竞拍三种拍卖——一价/二价密封报一次价；英式逐轮升价（每轮 +10，
        输入"继续/退出"）。每场成交后揭示所有人估值与出价，并给最优反应点评：
        一价的均衡出价是 0.75v、二价是 v 本尊、英式是坚持到 v——你偏离了多少、亏在哪，当场算账。
依赖：纯标准库 + numpy（独立实现，不 import lab04）。"""
import sys
import numpy as np

rng = np.random.default_rng(2026)
N_BOTS = 3            # 你 + 3 个机器人 = n=4
THEORY = 60.0         # E[次高] = 100·(n−1)/(n+1) = 60（n=4）


def fpsb_revenue(vals):
    """一价：机器人按 BNE b=0.75v 出价，卖价 = 最高出价。"""
    return 0.75 * vals.max()


def spsb_revenue(vals):
    """二价：机器人报真实估值，卖价 = 次高估值。"""
    return np.sort(vals)[-2]


def english_revenue(vals):
    """英式（升价时钟理想化）：坚持到价格过 v 才退，卖价 = 次高退出价 = 次高估值。"""
    return np.sort(vals)[-2]


def demo():
    ROUNDS = 2000
    vals = rng.uniform(0, 100, (ROUNDS, N_BOTS))     # 演示场机器人对机器人：4 个机器人
    vals4 = np.column_stack([vals, rng.uniform(0, 100, ROUNDS)])
    r1 = np.array([fpsb_revenue(v) for v in vals4]).mean()
    r2 = np.array([spsb_revenue(v) for v in vals4]).mean()
    r3 = np.array([english_revenue(v) for v in vals4]).mean()
    print("拍卖行 · 均衡机器人自拍 2000 场（n=4，估值 ~U[0,100]）——服务 08/13 章\n")
    print(f"  理论锚点（手推）：E[次高] = 100·(n−1)/(n+1) = {THEORY:.0f}；一价收入 = E[0.75·v_max] = 0.75×80 = 60")
    print(f"  一价密封（b=0.75v）  平均卖价 = {r1:6.2f}（vs 60，|偏差| {abs(r1 - THEORY):.2f}）")
    print(f"  二价密封（b=v 占优） 平均卖价 = {r2:6.2f}（vs 60，|偏差| {abs(r2 - THEORY):.2f}）")
    print(f"  英式升价（退于 v）   平均卖价 = {r3:6.2f}（vs 60，|偏差| {abs(r3 - THEORY):.2f}）")
    ok = all(abs(r - THEORY) < 2 for r in (r1, r2, r3))
    print(f"→ 三拍卖同入 60±2 —— " + ("收益等价成立（CLI 版对拍）✓" if ok else "⚠ 超容差——如实标注"))


def read_number(prompt, lo, hi):
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "q":
            return None
        try:
            x = float(raw)
            if lo <= x <= hi:
                return x
        except ValueError:
            pass
        print(f"  请输入 {lo}-{hi} 之间的数字（q 退出）")


def sealed(kind):
    v_you = float(rng.uniform(5, 100))
    bots = rng.uniform(0, 100, N_BOTS)
    name = "一价密封（付自己的出价）" if kind == "fpsb" else "二价密封（付次高价）"
    optimal = 0.75 * v_you if kind == "fpsb" else v_you
    print(f"\n== {name} == 你的真实估价：{v_you:.1f}（对手估值已暗抽）")
    bid = read_number("  你的出价（0-100，q 退出）: ", 0, 100)
    if bid is None:
        return
    bot_bids = 0.75 * bots if kind == "fpsb" else bots.copy()
    all_bids = np.array([bid] + list(bot_bids))
    winner = int(np.argmax(all_bids))
    price = all_bids[winner] if kind == "fpsb" else np.sort(all_bids)[-2]
    reveal(bots, bot_bids, bid, winner, price, you_are=0)
    # ---- 最优反应点评 ----
    dev = bid - optimal
    s2 = np.sort(bots)[-2]      # 对手中次高（你若赢，付的价由它/最高者决定）
    print(f"  点评：{name.split('（')[0]}的均衡出价是 {'0.75×v = ' + f'{optimal:.1f}' if kind == 'fpsb' else 'v 本身 = ' + f'{optimal:.1f}'}——"
          f"你偏离了 {dev:+.1f}")
    if kind == "spsb":
        if bid > v_you and price > v_you:
            print(f"  ⚠ 高报的代价现场：你以 {price:.1f} 买下（> 估值 {v_you:.1f}），净亏 {price - v_you:.1f}——二价里诚实是占优策略")
        elif bid < v_you and np.max(bot_bids) < v_you and np.max(bot_bids) >= bid:
            print(f"  ⚠ 低报的代价现场：对手最高 {np.max(bot_bids):.1f} 落在你的报价与估值之间——本可赚 {v_you - np.max(bot_bids):.1f}，被低报丢掉")
        else:
            print("  本场你的偏离恰好没改变结局（对手次高落在安全区）——但期望意义上偏离只亏不赚")
    else:
        if bid > 0.75 * v_you:
            print(f"  高于均衡：赢率升、赢时多付——若因此以 > {v_you:.1f} 成交就是净亏（本场成交价 {price:.1f}）")
        else:
            print(f"  低于均衡：省了钱但赢率降——对手最高出价 {np.max(bot_bids):.1f}，你 {'赢了' if winner == 0 else '输了'}")
        print(f"  （一价的均衡是 BNE 不是占优——报 0.75v 只在'对手都报 0.75v'时最优：08 章 §四）")


def english():
    v_you = float(rng.uniform(5, 100))
    bots = rng.uniform(0, 100, N_BOTS)
    print(f"\n== 英式升价（升价时钟，每轮 +10；坚持到价格过你估价才退是占优策略） ==")
    print(f"    你的真实估价：{v_you:.1f}（对手估值已暗抽）")
    price = 0.0
    dropout_you = None
    while price < 100:
        price += 10
        alive = (bots > price).sum() + (dropout_you is None)
        if alive == 0:
            break
        if dropout_you is None:
            ans = input(f"  价格升到 {price:.0f}——继续竞拍还是退出？[y=继续 / n=退出 / q 终局]: ").strip().lower()
            if ans == "q":
                return
            if ans == "n":
                dropout_you = price
                print(f"    你在 {price:.0f} 退出")
        else:
            if not (bots > price).any():
                break
    if dropout_you is None:
        dropout_you = 100.0                       # 坚持到最后
    dropouts = np.array([dropout_you] + list(bots))
    winner = int(np.argmax(dropouts))
    price_final = np.sort(dropouts)[-2]
    bot_bids = bots.copy()
    reveal(bots, bot_bids, dropout_you, winner, price_final, you_are=0, bid_label="退出价")
    print(f"  点评：英式的占优策略是'价格升过 v 才退'——你的退出价该是 {v_you:.1f}，实际 {dropout_you:.0f}"
          f"（偏离 {dropout_you - v_you:+.1f}）。私人价值下英式 ≡ 二价（13 章 §一）：赢者付的是次高退出价。")


def reveal(bots, bot_bids, my_bid, winner, price, you_are, bid_label="出价"):
    print(f"  —— 揭牌 —— 你的{bid_label}：{my_bid:.1f}｜机器人出价：", end="")
    print("、".join(f"{b:.1f}" for b in bot_bids))
    print(f"  机器人估值：", end="")
    print("、".join(f"{b:.1f}" for b in bots))
    if winner == you_are:
        print(f"  成交：你以 {price:.1f} 拍下")
    else:
        print(f"  成交：机器人 {winner}（0 号是你）以 {price:.1f} 拍下")


def main():
    if "--demo" in sys.argv:
        demo()
        return
    print("拍卖行 · 三拍卖人机竞拍（n=4，估值 ~U[0,100]；机器人按均衡出价）\n")
    print("  1. 一价密封   2. 二价密封   3. 英式升价   q. 退出")
    while True:
        c = input("选拍卖 [1/2/3/q]: ").strip().lower()
        if c == "q":
            return
        if c == "1":
            sealed("fpsb")
        elif c == "2":
            sealed("spsb")
        elif c == "3":
            english()
        else:
            print("  请输入 1/2/3 或 q")


if __name__ == "__main__":
    main()
