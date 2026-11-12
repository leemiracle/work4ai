#!/usr/bin/env python3
"""讲透博弈论 CLI · Kuhn 扑克对赌台：python cli/kuhn_poker.py [--demo|--hands N]
--demo：CFR 机器人 vs CFR 机器人自赌 500 手——P1 平均收益 vs 理论 −1/18 ≈ −0.0556（± 抽样波动，
        并打印 2·标准误带；单手收益 O(1)，500 手 SE ≈ 0.07——诚实标注抽样噪声）；
交互模式：你是 P1，CFR 机器人是 P2。每手发牌 J/Q/K（各一张），你先动 check/bet；
        机器人每一手都【当场揭示】它在该信息集抽签用的真实混合概率；结束（q 退出）打印
        总比分 + 机器人六信息集完整策略表 + 诈唬频率点评（J 面对你 check 后的下注率 = 诈唬）。
依赖：experiments/lab07_learning_cfr.py 的 KuhnCFR（sys.path 自动接入；纯 numpy）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from lab07_learning_cfr import KuhnCFR                      # noqa: E402

import numpy as np                                          # noqa: E402

CARD_NAME = "JQK"
TRAIN_ITERS = 50_000
DEMO_HANDS = 500


def bot_sigma(bot_avg, player, card, hist):
    """机器人在信息集 (player, card, hist) 的平均策略；缺键（未访问）时均匀。"""
    key = f"P{player + 1}:{CARD_NAME[card]}:{hist}"
    return bot_avg.get(key, np.ones(2) / 2)


def settle(hist, c1, c2):
    return KuhnCFR._terminal_payoff(hist, c1, c2)


def play_demo(bot_avg, rng):
    print(f"CFR bot vs CFR bot 自赌 {DEMO_HANDS} 手（双方按平均策略抽签）")
    print(f"理论锚点：博弈值（P1）= −1/18 ≈ {-1/18:+.4f}；单手收益 O(1)，SE ≈ 1.5/√{DEMO_HANDS} ≈ "
          f"{1.5 / DEMO_HANDS ** 0.5:.3f}（2·SE 带 = ±{3 / DEMO_HANDS ** 0.5:.3f}）")
    total = 0.0
    for _ in range(DEMO_HANDS):
        c1, c2 = rng.choice(3, size=2, replace=False)
        hist = ""
        while True:
            player, actions = KuhnCFR._legal(hist)
            if player is None:
                break
            p = player - 1
            sigma = bot_sigma(bot_avg, p, (c1, c2)[p], hist)
            a = actions[int(rng.random() < sigma[1])]        # sigma[1] = 第二动作（B/C）概率
            hist += a
        total += settle(hist, c1, c2)[0]
    avg = total / DEMO_HANDS
    se = 1.5 / DEMO_HANDS ** 0.5
    ok = abs(avg - (-1 / 18)) < 2 * se
    print(f"  P1 平均收益 = {avg:+.4f}（vs −0.0556；2·SE 带 ±{2 * se:.3f} 内 {'✓' if ok else '⚠'}）；"
          f"P2 = {-avg:+.4f}")
    print("  诚实标注：这是【均衡剖面的一次抽样实现】，非精确值——lab07 E3 的全树枚举才是精确对拍（−0.0556）。")
    return avg


def play_interactive(bot_avg, rng):
    print("你 = P1（先动），CFR bot = P2。动作：K=check 过牌 / B=bet 下注 1 / F=fold 弃牌 / C=call 跟注。")
    print("每手结束 bot 当场揭示它抽签用的混合概率；输入 q 结束并总结。\n")
    score, hands = 0.0, 0
    bluff_attempts = 0                        # bot 拿 J 且你 check 后它下注 = 诈唬现场
    while True:
        c1, c2 = rng.choice(3, size=2, replace=False)
        hands += 1
        hist = ""
        print(f"—— 第 {hands} 手：你的牌 {CARD_NAME[c1]}（bot 暗牌）——")
        while True:
            player, actions = KuhnCFR._legal(hist)
            if player is None:
                break
            if player == 1:
                choice = None
                while choice not in actions and choice != "Q":
                    choice = input(f"  你的动作 [{'/'.join(actions)}]（q 结束）: ").strip().upper()
                if choice == "Q":
                    return score, hands, bluff_attempts
                hist += choice
            else:
                sigma = bot_sigma(bot_avg, 1, c2, hist)
                a = actions[int(rng.random() < sigma[1])]
                hist += a
                act_cn = {"K": "check 过牌", "B": "bet 下注 1", "F": "fold 弃牌", "C": "call 跟注"}[a]
                print(f"  bot {act_cn}（它在该信息集的真实混合概率：{actions[0]}={sigma[0]:.3f} / "
                      f"{actions[1]}={sigma[1]:.3f}——抽签抽中 {a}）")
                if hist == "KB" and c2 == 0 and a == "B":
                    bluff_attempts += 1
        p1, _ = settle(hist, c1, c2)
        score += p1
        result = "你赢" if p1 > 0 else ("你输" if p1 < 0 else "平")
        print(f"  终局 {hist or '(无动作)'}：bot 暗牌是 {CARD_NAME[c2]}——{result} {p1:+.0f} 筹码；"
              f"当前总分 {score:+.0f}\n")
        if input("  回车再来一手，q 结束总结: ").strip().lower() == "q":
            return score, hands, bluff_attempts


def summarize(bot_avg, score, hands, bluff_attempts):
    print("\n" + "=" * 60)
    print(f"总结：{hands} 手，你（P1）总分 {score:+.0f}，平均 {score / max(hands, 1):+.4f}/手")
    print("理论提示：P1 先动劣势，均衡期望 ≈ −0.0556/手——你若长期高于它，说明 bot 的抽签运气欠佳或你在剥削它的混合")
    print(f"诈唬现场：bot 拿 J 且你 check 后它下注（诈唬）共 {bluff_attempts} 次" if bluff_attempts
          else "本局未出现 bot 拿 J 你 check 它下注的诈唬现场")
    print("\nbot（P2）六信息集完整平均策略：")
    for key in sorted(k for k in bot_avg if k.startswith("P2")):
        hist = key.split(":")[2]
        names = ("check", "bet") if hist == "K" else ("fold", "call")
        p = bot_avg[key]
        print(f"  {key:<10s} {names[0]}={p[0]:.3f}  {names[1]}={p[1]:.3f}")
    j_key = "P2:J:K"
    if j_key in bot_avg:
        b = bot_avg[j_key][1]
        print(f"\n诈唬频率点评：bot 拿 J 且你 check 后以 {b:.3f} 下注诈唬——Kuhn 均衡族里这个数落在")
        print(f"  [0, 1/3]（K 的下注率应是它的三倍左右）；面对你的 bet 它拿 J 永远弃、拿 K 永远跟，")
        print(f"  拿 Q 以约 1/3 概率跟注——这就是 16 章手推的均衡形状，你刚跟它打了个照面。")


def main():
    demo = "--demo" in sys.argv
    rng = np.random.default_rng(2026)
    print(f"训练 CFR 机器人（vanilla，{TRAIN_ITERS} 次迭代，chance 全枚举）…", flush=True)
    bot = KuhnCFR().train(TRAIN_ITERS)
    bot_avg = bot.average_strategy()
    print(f"完成：精确博弈值（平均策略剖面）= {bot.converged_value():+.4f} vs 理论 −0.0556\n")
    if demo:
        play_demo(bot_avg, rng)
        return
    score, hands, ba = play_interactive(bot_avg, rng)
    summarize(bot_avg, score, hands, ba)


if __name__ == "__main__":
    main()
