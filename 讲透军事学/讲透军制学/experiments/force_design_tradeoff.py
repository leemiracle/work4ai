# -*- coding: utf-8 -*-
"""力量结构权衡模拟:同预算三组合的齐射战损推演(00/04 章配套实验)。

问题(力量设计时代的典型军制学题):同一笔预算,买
  A. 少量高价平台(5 艘高端:火力强/带防御/带 C2 节点)
  B. 大量廉价平台(50 艘低端:便宜/血厚靠数量/无节点)
  C. 混合(3 高端 + 20 低端)
面对同一支参考敌军(2 高端 + 25 低端,预算 90),哪种结构的费效比高?

模型(休斯 salvo 齐射交换的异质版 + C2 网络依赖):
  每回合双方同时齐射:
    命中量 = max(0, 敌齐射火力×u − 我防御拦截×v),u,v~U(0.9,1.1)
    命中按目标分配规则落在存活平台上,扣持续力(HP),死则记价值损失
  C2 依赖:廉价平台无指挥/传感节点,己方无高价(C2)平台存活时
    其火力打 κ 折(建制假设——"分散红利×网络依赖"的乘积机制)
  分配规则(边界变量):随机分配(对手无法点名)vs 价值优先
    (对手优先打高价节点——分布式结构的经典软肋)

四个断言组:
  ① 结构:三组合预算严格用满=100,敌军=90,配置如声明
  ② 基线(随机分配,κ=0.55):混合组合净价值(敌毁−己损)与胜率
     严格占优——混合优势的存在性
  ③ 稳健域(随机分配,κ=0.40/0.70):混合组合保持最优——
     节点保险费在"廉价平台依赖网络"区间的稳健收益
  ④ 条件边界(两处翻转):
     a 自主性边界(随机分配,κ=1.00):大量廉价组合反超——
       廉价平台全自主时,养 C2 节点的预算是纯负债
     b 点名边界(价值优先分配,κ=1.00):大量廉价组合大幅反超——
       对手专打高价节点,混合结构两头受损

⚠ 军制学纪律(02/04 章):参数(火力/防御/成本/κ)是建制假设的
示例值,不是任何真实军队的数据;推演输出=机器化的反事实,
结论的形式永远是"在 κ=X、分配规则=Y 的假设下……"。

跑法: python experiments/force_design_tradeoff.py
"""

import random

# ── 平台类型(高低端;数值为示例建制参数)─────────────────────
CAPITAL = dict(name="高价平台", cost=20.0, off=2.0, dfn=1.0, hp=2.0,
               c2=True)          # 火力强/带防御/自带 C2 节点
CHEAP = dict(name="廉价平台", cost=2.0, off=0.2, dfn=0.02, hp=1.0,
             c2=False)           # 便宜/HP 密度 5 倍(分散红利)/无节点

BUDGET_BLUE = 100.0
ROUNDS_MAX = 60
TRIALS = 400
NOISE = (0.9, 1.1)               # 齐射/拦截的共同战场条件扰动


def fleet(specs):
    """specs=[(type, count)] → 平台列表(dict 的浅拷贝实例)。"""
    out = []
    for t, n in specs:
        out += [dict(t, hp_left=t["hp"]) for _ in range(int(n))]
    return out


PORTFOLIOS = {
    "少量高价": fleet([(CAPITAL, 5)]),                    # 5×20=100
    "大量廉价": fleet([(CHEAP, 50)]),                     # 50×2=100
    "混合组合": fleet([(CAPITAL, 3), (CHEAP, 20)]),       # 60+40=100
}
RED = fleet([(CAPITAL, 2), (CHEAP, 25)])                  # 40+50=90


def spend(fs):
    return sum(f["cost"] for f in fs)


def salvo_power(fs, kappa):
    """总齐射火力;无 C2 节点存活时,廉价平台火力打 κ 折。"""
    has_c2 = any(f["c2"] for f in fs)
    total = 0.0
    for f in fs:
        eff = 1.0 if (f["c2"] or has_c2) else kappa
        total += f["off"] * eff
    return total


def defense_power(fs):
    return sum(f["dfn"] for f in fs)


def take_hits(fs, hits, rng, value_targeting):
    """命中分配:随机洗牌 or 价值优先(高价节点先挨打);
    逐平台扣 HP,返回(幸存列表, 被毁价值)。"""
    order = list(fs)
    if value_targeting:
        order.sort(key=lambda f: -f["cost"])
    else:
        rng.shuffle(order)
    destroyed = 0.0
    left = []
    for f in order:
        if hits <= 1e-9:
            left.append(f)
            continue
        dmg = min(f["hp_left"], hits)
        f["hp_left"] -= dmg
        hits -= dmg
        if f["hp_left"] <= 1e-9:
            destroyed += f["cost"]
        else:
            left.append(f)
    return left, destroyed


def fight(blue, kappa, value_targeting, trial):
    """一场齐射推演;返回(蓝净价值=红毁−蓝损, 蓝胜?)。"""
    # 每场重新构造实例,避免跨试验共享可变状态
    blue = [dict(f, hp_left=f["hp"]) for f in blue]
    red = [dict(f, hp_left=f["hp"]) for f in RED]
    red_lost = blue_lost = 0.0
    for rnd_i in range(ROUNDS_MAX):
        cond = random.Random(99_000 + 131 * trial + rnd_i)   # 双方共享战场条件
        u = NOISE[0] + (NOISE[1] - NOISE[0]) * cond.random()
        v = NOISE[0] + (NOISE[1] - NOISE[0]) * cond.random()
        tgt = random.Random(4_700 + 131 * trial + rnd_i)     # 目标分配随机源
        if not blue or not red:
            break
        hits_on_red = max(0.0, salvo_power(blue, kappa) * u
                          - defense_power(red) * v)
        hits_on_blue = max(0.0, salvo_power(red, kappa) * v
                           - defense_power(blue) * u)
        red, d1 = take_hits(red, hits_on_red, tgt, value_targeting)
        blue, d2 = take_hits(blue, hits_on_blue, tgt, value_targeting)
        red_lost += d1
        blue_lost += d2
    blue_win = (not red) and bool(blue)
    return red_lost - blue_lost, blue_win


def evaluate(portfolio_specs, kappa, value_targeting, trials=TRIALS):
    """蒙特卡洛:返回(平均净价值, 胜率)。"""
    base = fleet(portfolio_specs)
    nets, wins = [], 0
    for t in range(trials):
        net, w = fight(base, kappa, value_targeting, t)
        nets.append(net)
        wins += w
    return sum(nets) / len(nets), wins / trials


def fmt_row(name, net, wr):
    return f"  {name:<6} 净价值 {net:>+7.1f}   胜率 {wr:>5.0%}"


def main():
    print("=" * 72)
    print("力量结构权衡模拟:同预算三组合 × 齐射交换 × C2 网络依赖")
    print("=" * 72)
    print(f"高价平台:成本{CAPITAL['cost']:.0f} 火力{CAPITAL['off']:.1f} "
          f"防御{CAPITAL['dfn']:.1f} HP{CAPITAL['hp']:.0f}(C2 节点)")
    print(f"廉价平台:成本{CHEAP['cost']:.0f} 火力{CHEAP['off']:.1f} "
          f"防御{CHEAP['dfn']:.2f} HP{CHEAP['hp']:.0f}(无节点,κ 折)")
    print(f"蓝方预算 {BUDGET_BLUE:.0f};敌军(2 高价+25 廉价)预算 "
          f"{spend(RED):.0f};试验 {TRIALS} 次/格\n")

    # ── 断言 1:结构与预算 ─────────────────────────────────
    assert abs(spend(PORTFOLIOS["少量高价"]) - 100) < 1e-9
    assert abs(spend(PORTFOLIOS["大量廉价"]) - 100) < 1e-9
    assert abs(spend(PORTFOLIOS["混合组合"]) - 100) < 1e-9
    assert abs(spend(RED) - 90) < 1e-9
    assert len(PORTFOLIOS["混合组合"]) == 23 and len(RED) == 27
    print("断言 1 通过:三组合预算严格相等(100),敌军 90,配置如声明 ✓")

    results = {}          # (targeting, kappa) → {name: (net, winrate)}

    # ── 全矩阵推演(分配规则 × κ)──────────────────────────
    for targeting, tname in ((False, "随机分配(对手不能点名)"),
                             (True, "价值优先(对手专打节点)")):
        for kappa in (0.55, 0.40, 0.70, 1.00):
            print(f"\n[{tname} | 廉价平台自主性 κ={kappa:.2f}]")
            cell = {}
            for name, specs in (("少量高价", [(CAPITAL, 5)]),
                                ("大量廉价", [(CHEAP, 50)]),
                                ("混合组合", [(CAPITAL, 3), (CHEAP, 20)])):
                net, wr = evaluate(specs, kappa, targeting)
                cell[name] = (net, wr)
                print(fmt_row(name, net, wr))
            results[(targeting, kappa)] = cell

    # ── 断言 2:基线占优(随机分配,κ=0.55)─────────────────
    base = results[(False, 0.55)]
    mix_n, mix_w = base["混合组合"]
    others = [base["少量高价"], base["大量廉价"]]
    assert mix_n > max(n for n, _ in others) + 40, \
        "基线:混合组合净价值应显著占优(>+40)"
    assert mix_w >= 0.75 and mix_w > max(w for _, w in others) + 0.4, \
        "基线:混合组合胜率应显著最高"
    print("\n断言 2 通过:基线(随机分配,κ=0.55)混合组合费效比占优 ✓")
    print("          ——分散红利(廉价平台 HP 密度 5 倍)×网络依赖"
          "(高价节点撑火力)的乘积机制成立")

    # ── 断言 3:稳健域(随机分配,κ=0.40/0.70)──────────────
    for kappa in (0.40, 0.70):
        cell = results[(False, kappa)]
        assert cell["混合组合"][0] > max(n for n, _ in
                                        (cell["少量高价"], cell["大量廉价"])) + 10, \
            f"稳健域:随机分配下混合应保持最优(κ={kappa})"
    print("断言 3 通过:随机分配下 κ=0.40/0.55/0.70 混合组合均最优"
          "(稳健域) ✓")
    print("          ——节点保险费(60% 预算买 3 个 C2 节点)在"
          "「廉价平台依赖网络」的区间是稳健投资")

    # ── 断言 4:条件边界(两处翻转)────────────────────────
    edge_a = results[(False, 1.00)]        # a 自主性边界
    many_a, many_a_w = edge_a["大量廉价"]
    mix_a, mix_a_w = edge_a["混合组合"]
    assert many_a > mix_a + 5 and many_a_w > mix_a_w, \
        "自主性边界:廉价平台全自主(κ=1)时,纯数量应反超混合"
    edge_b = results[(True, 1.00)]         # b 点名边界
    many_b, many_b_w = edge_b["大量廉价"]
    mix_b, mix_b_w = edge_b["混合组合"]
    assert many_b > mix_b + 30 and many_b_w >= mix_b_w, \
        "点名边界:对手专打节点+廉价平台全自主时,纯数量应大幅反超"
    print("断言 4 通过:条件边界两处翻转均复现 ✓")
    print(f"          a 自主性边界(随机分配,κ=1.00):大量廉价 {many_a:+.1f}"
          f" > 混合 {mix_a:+.1f}")
    print("            ——廉价平台无需网络时,养节点的预算是纯负债")
    print(f"          b 点名边界(价值优先,κ=1.00):大量廉价 {many_b:+.1f}"
          f" ≫ 混合 {mix_b:+.1f}")
    print("            ——对手专打高价节点,混合结构两头受损;"
          "混合优势是有条件的,不是教条")

    # ── 结论速查表 ────────────────────────────────────────
    print("\n" + "=" * 72)
    print("四组断言全部通过 ✓  矩阵速查(净价值):")
    print(f"{'场景':<26}{'少量高价':>10}{'大量廉价':>10}{'混合组合':>10}")
    for (targeting, kappa), cell in sorted(results.items(),
                                            key=lambda kv: (kv[0][0], kv[0][1])):
        tag = ("随机 " if not targeting else "点名 ") + f"κ={kappa:.2f}"
        print(f"{tag:<26}{cell['少量高价'][0]:>+10.1f}"
              f"{cell['大量廉价'][0]:>+10.1f}{cell['混合组合'][0]:>+10.1f}")
    print("\n⚠ 军制学纪律:参数=建制假设示例值;结论的正确读法是"
          "\n  「在 κ=X、分配规则=Y 的假设下……」——把建制假设当显式"
          "变量扫描,是力量设计推演区别于购物清单比较的第一特征。")


if __name__ == "__main__":
    main()
