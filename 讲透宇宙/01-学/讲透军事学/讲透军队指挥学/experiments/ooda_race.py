# -*- coding: utf-8 -*-
"""OODA 环竞赛模拟:信息优势×指挥方式(集中式/去中心化)的节奏论检验
(00 章⑥反直觉之一 + 04 章 C1 走廊的成品实验)。

模型:红蓝两方各走一个 OODA 环,四阶段时延独立随机(指数分布):
  观察 O:受"信息优势"(传感器网/情报体系)缩短
  判断 J:受"共同理解"(COP/演习训练)缩短——本实验默认双方同构
  决策 D:含定下决心与命令分发;受"任务式指挥"(去中心化授权)大幅缩短
  行动 A:执行时延——本实验默认双方同构
  链路中断(概率 fail_p):集中式须总部中转(重罚 fail_pen 大),
  去中心化本地裁决(轻罚 fail_pen 小)——抗毁性差异的近似
每轮交战:双方各抽一个完整 OODA 环总时延,总时延短者获得先手打击
窗口(节奏论:快者胜的零模型,博伊德通说的机器化)。

四个断言:
  ① 对称性:同构双方胜率≈0.5(模型无偏检验)
  ② 双优胜出:信息优+去中心化 vs 信息劣+集中式,胜率显著>0.5
  ③ 反论(核心):「单优信息+集中式分发」胜率低于「信息略差+去中心化分发」
     ——看得最清的手不该攥着所有裁决权:观察收益被决策分发的
     排队瓶颈吃掉(01 章热线三反论的机器化:AI 决策支持增强的
     是去中心化执行,不是总部集中)
  ④ 脆弱性梯度:链路中断率上升,集中式胜率单调劣化,且快于去中心化

⚠ 建模边界(00 章假设三·独立时钟假设):本模型把敌我当作两个
独立计时器;敌对耦合(你的行动改变对方的观察,如中途岛式
"代填观察")未建模——输出是节奏论视角的序数结论(谁更快),
不是对真实交战的基数预言(04 章§1 可机械化边界)。
时延参数=指挥文化假设,引用须附来源(04 章走廊警告 1)。

跑法: python experiments/ooda_race.py
"""
import random

N_ROUNDS = 40000
SEED = 20260907          # 固定种子=可复现;换种子看方差是正确姿势


def side(name, obs, dec, act, fail_p, fail_pen, ori=2.0):
    """一方配置:四阶段时延均值(相对时间单位,只做序数比较);
    fail_p=链路中断概率;fail_pen=中断罚时(集中式重罚/去中心化轻罚)。"""
    return dict(name=name, obs=obs, ori=ori, dec=dec, act=act,
                fail_p=fail_p, fail_pen=fail_pen)


def cycle_time(rng, s):
    """一次完整 OODA 环时延:四阶段独立指数时延 + 断链罚时。"""
    t = (rng.expovariate(1 / s["obs"]) + rng.expovariate(1 / s["ori"])
         + rng.expovariate(1 / s["dec"]) + rng.expovariate(1 / s["act"]))
    if rng.random() < s["fail_p"]:
        t += s["fail_pen"]
    return t


def expected_cycle(s):
    """期望环时延(打印用):指数分布均值之和 + 期望罚时。"""
    return s["obs"] + s["ori"] + s["dec"] + s["act"] + s["fail_p"] * s["fail_pen"]


def engagement(a, b, rounds, seed):
    """多轮交战:每轮双方各走一个 OODA 环,总时延短者先手。
    返回 a 的胜率(连续分布,平局概率为 0)。"""
    rng = random.Random(seed)
    wins = 0
    for _ in range(rounds):
        ta, tb = cycle_time(rng, a), cycle_time(rng, b)
        if ta != tb:
            wins += ta < tb
    return wins / rounds


def main():
    print("=" * 76)
    print(f"OODA 环竞赛模拟:{N_ROUNDS} 轮蒙特卡洛 · 节奏论零模型"
          f"(seed={SEED})")
    print("=" * 76)

    # 指挥方式参数:集中式=一切裁决过总部(断链重罚);
    # 去中心化=任务式授权,本地闭环(断链轻罚)
    central = dict(fail_p=0.05, fail_pen=6.0)
    decentr = dict(fail_p=0.05, fail_pen=1.5)

    DUAL_SUPERIOR = side("信息优+去中心化", obs=1.8, dec=1.3, act=1.0, **decentr)
    DUAL_INFERIOR = side("信息劣+集中式", obs=3.0, dec=3.4, act=1.0, **central)
    INFO_ONLY = side("信息优+集中式", obs=1.8, dec=3.4, act=1.0, **central)
    LESS_INFO = side("信息略差+去中心化", obs=2.3, dec=1.5, act=1.0, **decentr)
    MIRROR = side("镜像基准", obs=2.4, dec=2.4, act=1.0, **decentr)

    print(f"\n{'配置':<12} {'观察O':>5} {'判断J':>5} {'决策D':>5} {'行动A':>5} "
          f"{'断链率':>5} {'罚时':>5} {'期望环时延':>8}")
    for s in (DUAL_SUPERIOR, DUAL_INFERIOR, INFO_ONLY, LESS_INFO, MIRROR):
        print(f"{s['name']:<12} {s['obs']:>5.1f} {s['ori']:>5.1f} {s['dec']:>5.1f} "
              f"{s['act']:>5.1f} {s['fail_p']:>5.2f} {s['fail_pen']:>5.1f} "
              f"{expected_cycle(s):>8.2f}")
    print("(决策D 含决心形成与命令分发——任务式指挥的作用点;单位为相对时间)")

    # ── 断言 1:对称性(模型无偏)──────────────────────────
    r1 = engagement(MIRROR, MIRROR, N_ROUNDS, SEED)
    assert abs(r1 - 0.5) < 0.01, f"同构双方胜率应≈0.5,实测 {r1:.4f}"
    print(f"\n断言 1(对称性):镜像基准胜率 {r1:.4f} ≈ 0.5 ✓"
          "\n              ——模型无偏:先手规则不偏向任一方")

    # ── 断言 2:双优胜出(信息+分发双优显著胜)──────────────
    r2 = engagement(DUAL_SUPERIOR, DUAL_INFERIOR, N_ROUNDS, SEED)
    assert r2 > 0.65, f"双优方胜率应显著高,实测 {r2:.4f}"
    print(f"断言 2(双优胜出):信息优+去中心化 对 信息劣+集中式 "
          f"胜率 {r2:.4f} ✓")
    print("              ——观察与分发双优,节奏优势显著(决策优势的『快』维)")

    # ── 断言 3:反论检验(核心)────────────────────────────
    # 「单优信息+集中式分发」(INFO_ONLY) vs 「信息略差+去中心化分发」(LESS_INFO)
    r3 = engagement(LESS_INFO, INFO_ONLY, N_ROUNDS, SEED)
    assert r3 > 0.56, f"反论不成立:信息略差+去中心化应胜出,实测 {r3:.4f}"
    print(f"断言 3(反论·核心):信息略差+去中心化 对 单优信息+集中式 "
          f"胜率 {r3:.4f} ✓")
    print("              ——观察时延的收益被决策分发的排队瓶颈吃掉:"
          "\n                 看得最清的手,不该攥着所有裁决权"
          "\n                 (01 章:AI 决策支持增强去中心化执行的反论)")

    # ── 断言 4:脆弱性梯度(断链率上升,集中式单调劣化更快)──
    print("\n断言 4(脆弱性梯度):同作战能力,仅指挥方式不同——")
    prev = None
    for p in (0.0, 0.15, 0.30):
        c = side("集中式", obs=2.0, dec=2.0, act=1.0, fail_p=p, fail_pen=8.0)
        d = side("去中心化", obs=2.0, dec=2.0, act=1.0, fail_p=p, fail_pen=1.2)
        w = engagement(c, d, N_ROUNDS, SEED)
        print(f"  断链率 p={p:.2f}:集中式 胜率 {w:.4f}(期望环差 "
              f"{p * (8.0 - 1.2):+.2f})")
        if p == 0.0:
            assert abs(w - 0.5) < 0.01, "断链为零时两种指挥方式应无差异"
        else:
            assert w < prev - 0.01, "集中式胜率应随断链率单调下降"
        prev = w
    assert prev < 0.45, "高断链率下集中式应显著劣于去中心化"
    print("  ——集中度买效率、去中心化买韧性:对抗环境下二者不可兼得 ✓")

    print("\n" + "=" * 76)
    print("四组断言全部通过:对称性 / 双优胜出 / 反论(信息×分发) / 脆弱梯度 ✓")
    print("\n⚠ 建模边界提醒:独立时钟假设——敌对耦合(代填观察/攻击判断环)"
          "未建模;")
    print("  时延参数=指挥文化假设,引用须附来源。输出=节奏论序数结论,"
          "不是基数预言。")


if __name__ == "__main__":
    main()
