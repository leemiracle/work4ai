#!/usr/bin/env python3
"""讲透博弈论 CLI · 重复囚徒困境竞技场：python cli/ipd_arena.py [--demo]
--demo：axelrod 十策略循环赛积分榜（无人工输入的冒烟模式，服务 10 章）；
交互：你选对手（编号列出，各配一句中文性格简介）与轮数，逐轮输入 C/D（q 结束）——
        实时显示双方累计得分与对手上一手；终局打印比分 + 策略性格点评
        （合作率 / 报复率 / 宽容度）——10 章 TFT 四美德的亲手体检。
计分沿用 00 章三原型记号：PD T=5, R=3, P=1, S=0。
依赖：axelrod（人类玩家经 Player 适配器接入官方策略对象，不重写策略）。"""
import sys
import numpy as np

import axelrod as axl

ROSTER = [
    (axl.TitForTat,    "以牙还牙：善良·报复·宽容·清晰（Axelrod 1980 冠军）"),
    (axl.Grudger,      "记仇者：一被背叛记仇到底——善良·报复·零宽容"),
    (axl.WinStayLoseShift, "赢留输变： WSLS——赢了重复、输了切换"),
    (axl.Cooperator,   "老好人：永远合作——善良·零报复"),
    (axl.Defector,     "恶棍：永远背叛"),
    (axl.Alternator,   "交替者：C/D/C/D 轮流出"),
    (axl.Random,       "随机者：五五开掷硬币"),
    (axl.Prober,       "探子：先试合作，试探一轮背叛再看你反应"),
    (axl.TitFor2Tats,  "两报还一仇：宽容版 TFT——连续两次背叛才反击"),
    (axl.SuspiciousTitForTat, "疑心 TFT：先背叛一手再以牙还牙"),
]
# 计分表（行=我，列=对手）：(R,R)=(3,3) (T,S)=(5,0) (S,T)=(0,5) (P,P)=(1,1)
SCORE = {("C", "C"): (3, 3), ("D", "D"): (1, 1), ("D", "C"): (5, 0), ("C", "D"): (0, 5)}


class HumanAdapter(axl.Player):
    """把'你'接进 axelrod 策略对象：strategy() 返回本轮预先填入的动作。"""
    name = "Human"
    classifier = {"memory_depth": float("inf"), "stochastic": False,
                  "makes_use_of": set(), "long_run_time": False,
                  "inspects_source": False, "manipulates_source": False,
                  "manipulates_state": False}

    def __init__(self):
        super().__init__()
        self.next_move = "C"

    def strategy(self, opponent):
        return self.next_move


def demo():
    players = [cls() for cls, _ in ROSTER]
    tour = axl.Tournament(players, turns=200, repetitions=20, seed=42)
    results = tour.play(progress_bar=False)
    print("IPD 竞技场 · axelrod 十策略循环赛（turns=200, repetitions=20）——服务 10 章\n")
    ranked = sorted(zip(results.ranked_names, results.scores),
                    key=lambda z: -np.mean(z[1]))
    for i, (name, scores) in enumerate(ranked, 1):
        print(f"  {i:>2}. {name:<22} 场均 {np.mean(scores):6.1f}")
    print("\n  读数（10 章锚点）：TFT 拿下榜首——Axelrod 1980 结论的复现；但请看 Cooperator 第 8、")
    print("  WSLS 垫底：单一循环赛的排名依赖参赛名单（生态效应）——'善良必胜'是生态规律不是定理（10 章阴暗面一节）。")


def interactive():
    print("IPD 竞技场 · 人机对打（计分 T=5 R=3 P=1 S=0；你与对手同屏累计）\n")
    print("对手名单：")
    for i, (_, intro) in enumerate(ROSTER, 1):
        print(f"  {i:>2}. {intro}")
    while True:
        raw = input("\n选对手编号（1-10，q 退出）: ").strip()
        if raw.lower() == "q":
            return
        if raw.isdigit() and 1 <= int(raw) <= len(ROSTER):
            break
    opp_cls, opp_intro = ROSTER[int(raw) - 1]
    while True:
        rounds = input("轮数（10-200）: ").strip()
        if rounds.isdigit() and 10 <= int(rounds) <= 200:
            rounds = int(rounds)
            break
    opp = opp_cls()
    me = HumanAdapter()
    dummy = axl.Match((me, opp), turns=rounds)   # 只借它的 simultaneous_play：同时算双方动作并更新双方历史
    print(f"\n对手：{opp.name}（{opp_intro}）。逐轮输入 C/D，回车默认 C，q 提前终局。\n")
    my_hist, opp_hist, my_score, opp_score = [], [], 0, 0
    for t in range(1, rounds + 1):
        raw = input(f"  第 {t}/{rounds} 轮 你的动作 [C/D]（q 终局）: ").strip().upper()
        if raw == "Q":
            break
        move = raw if raw in ("C", "D") else "C"
        me.next_move = axl.Action.C if move == "C" else axl.Action.D
        my_move, opp_move = dummy.simultaneous_play(me, opp)   # 双方各见对方"截至上一轮"的历史
        my_move, opp_move = str(my_move), str(opp_move)
        my_hist.append(my_move)
        opp_hist.append(opp_move)
        ds, do = SCORE[(my_move, opp_move)]
        my_score += ds
        opp_score += do
        last = f"对手上一手：{opp_move}"
        print(f"    你 {my_move} vs 对手 {opp_move} → 本轮 ({ds},{do})；累计 你 {my_score} : {opp_score}  {last}")
    # ---- 策略性格点评：合作率 / 报复率 / 宽容度 ----
    n = len(my_hist)
    coop_rate = my_hist.count("C") / n if n else 0
    retaliations = triggered = 0
    forgiven = opportunities = 0
    for i in range(1, n):
        if opp_hist[i - 1] == "D":                 # 上一轮对手背叛
            triggered += 1
            retaliations += my_hist[i] == "D"      # 我这轮是否反击
        if opp_hist[i - 1] == "C" and my_hist[i - 1] == "D":   # 对手回到合作、我刚被罚
            opportunities += 1
            forgiven += my_hist[i] == "C"          # 我是否宽容回合作
    retal = retaliations / triggered if triggered else float("nan")
    forgive = forgiven / opportunities if opportunities else float("nan")

    def pct(x):
        return "n/a（无触发场合）" if x != x else f"{x:.0%}"

    print(f"\n终局：你 {my_score} : {opp_score}（{n} 轮）")
    print("你的策略性格点评（10 章 TFT 四美德对照）：")
    print(f"  善良（合作率）        {coop_rate:.0%}")
    print(f"  报复（被叛后反击率）  {pct(retal)}")
    print(f"  宽容（对手回头即合作）{pct(forgive)}")
    print("  清晰：你的模式对手看得懂吗？——选 TFT 打一局对照看看。")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        interactive()
