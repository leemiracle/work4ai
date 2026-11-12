# -*- coding: utf-8 -*-
"""
deterrence_bargaining.py —— 讲透战略学家族实验(83025)

三部分(家族 README 实验表 / 04 章走廊一/二/三的成品):
  Part A  谢林竞争性讨价还价:消耗战混合策略均衡——解析解 + 蒙特卡洛互证
  Part B  威慑成功的贴现阈值 δ*:MAD 态势 vs 单方优势态势的稳定性对比
  Part C  威慑三角(常规/核/网络)稳定性矩阵 + 域间可信度传导

学科纪律声明:本实验是经典博弈论概念(消耗战/威慑均衡/谢林议价)的
教学化模拟,全部参数为教学假设,不指涉任何现实国家、政策或力量数据;
输出为模型性质(04 章裂缝清单:S4 模型级),不是态势判断。

运行:python experiments/deterrence_bargaining.py  (纯标准库,assert 自验)
"""
import random

random.seed(42)  # 可复跑

# ============================================================
# Part A  消耗战(war of attrition)混合策略均衡
# ============================================================
# 设定:两人争夺标的 V,每回合双方同时选 坚持/让步;
#   一方坚持一方让步 -> 坚持者得 V,让步者 0;
#   双方让步 -> 平分 V/2;双方坚持 -> 各付成本 c,进入下一回合。
# 对称混合均衡:坚持概率 p* 满足对手在 坚持/让步 之间无差别,
#   解得 p* = 1 - c/V(推导见家族 04 章走廊一)。
V, C = 10.0, 2.0
P_STAR = 1.0 - C / V            # 解析均衡:坚持概率
Q_YIELD = 1.0 - P_STAR          # 让步概率 = c/V
# 回合终局概率 = 至少一方让步 = 1 - p*^2;期望回合数 = 1/(1-p*^2)
E_ROUNDS = 1.0 / (1.0 - P_STAR ** 2)


def play_one_attrition():
    """模拟一场消耗战,返回 (回合数, 双方总让步次数)。"""
    rounds = 0
    while True:
        rounds += 1
        a = random.random() < P_STAR    # True=坚持
        b = random.random() < P_STAR
        if a and b:
            continue                    # 双坚持:付成本进入下一回合
        # 至少一方让步 -> 终局
        yields = (not a) + (not b)
        return rounds, yields


def part_a():
    n_games = 200_000
    total_rounds = 0
    total_yields = 0
    double_yields = 0
    for _ in range(n_games):
        r, y = play_one_attrition()
        total_rounds += r
        total_yields += y
        if y == 2:
            double_yields += 1
    sim_mean_rounds = total_rounds / n_games
    # 注意条件化:游戏必终局于"至少一方让步"的回合,故终局时刻的
    # 统计量是条件概率(分母=终局概率 1-p*^2),不是无条件的 q*:
    #   终局让步率(每方) = q*/(1-p*^2);双让步占比 = q*^2/(1-p*^2)
    # 这是消耗战的一个微妙处:均衡的无条件让步流 vs 终局时刻的条件画像。
    end_prob = 1.0 - P_STAR ** 2
    cond_yield_rate = Q_YIELD / end_prob
    cond_double = Q_YIELD ** 2 / end_prob
    sim_yield_rate = total_yields / (2 * n_games)
    print(f"[Part A] 消耗战混合策略 (V={V}, c={C})")
    print(f"  解析:p*={P_STAR:.4f}, q*={Q_YIELD:.4f}, E[回合]={E_ROUNDS:.4f}")
    print(f"  解析(终局条件):让步率={cond_yield_rate:.4f}, 双让步占比={cond_double:.4f}")
    print(f"  模拟:让步率={sim_yield_rate:.4f}, 平均回合={sim_mean_rounds:.4f}, "
          f"双让步占比={double_yields / n_games:.4f}")
    assert abs(sim_yield_rate - cond_yield_rate) < 0.01, "终局让步率偏离条件解析值"
    assert abs(sim_mean_rounds - E_ROUNDS) < 0.05, "平均回合数偏离几何期望"
    assert abs(double_yields / n_games - cond_double) < 0.01, "双让步占比偏离条件解析值"
    # 均衡的无差别性:坚持与让步的期望支付相等(均应为 0,对称零和构造)
    # 直接验证无差别条件:对手以 p* 坚持时,我坚持的期望 = 我让步的期望
    payoff_hold = P_STAR * (0.0 - C) + Q_YIELD * (V - C)   # 对手坚持→进下一轮(零和起点);对手让步→我净得 V-c
    payoff_fold = 0.0
    assert abs(payoff_hold - payoff_fold) < 1e-9, "无差别条件不成立——解析解错"
    print("  PASS: 模拟与解析互证一致(让步率/平均回合/双让步占比/无差别条件)\n")


# ============================================================
# Part B  威慑成功的贴现阈值 δ*
# ============================================================
# 设定(家族 00 章反直觉② / 03 章骨架二 / 04 章走廊二):
#   挑战者面对现状(支付 0)与越线(立即得 G,未来遭报复损失 D,
#   以贴现因子 δ 折现)。越线净支付 = G - δD。
#   威慑成立 ⇔ G - δD ≤ 0 ⇔ δ ≥ δ* = G / D。
# 两种态势:
#   MAD(相互确保摧毁):报复可确保执行,D_mad 大(二次打击兜底)
#   单方优势(有防御/反制削弱报复):有效报复 D_adv = D_mad·(1-d)
# 结论断言:MAD 的 δ* 显著更低——只有在极端不耐心(δ 很小)时
#   威慑才失效;单方优势抬高等于把"和平的门槛"提高。
G = 6.0            # 越线即时收益(教学参数)
D_MAD = 10.0       # MAD 态势下挑战者面临的报复损失
DEFENSE_D = 0.6    # 单方优势态势:防御/反制削去 60% 报复效果
D_ADV = D_MAD * (1.0 - DEFENSE_D)
DELTA_STAR_MAD = G / D_MAD
DELTA_STAR_ADV = G / D_ADV


def deterred(delta, d_star):
    """给定贴现因子与阈值,威慑是否成立。"""
    return delta >= d_star


def part_b():
    print(f"[Part B] 贴现阈值 δ* (G={G})")
    print(f"  MAD 态势:    D={D_MAD:.1f}, δ*={DELTA_STAR_MAD:.4f}")
    print(f"  单方优势态势: D={D_ADV:.1f}(防御削去{DEFENSE_D:.0%}), δ*={DELTA_STAR_ADV:.4f}")
    # 扫描 δ∈[0,1]:两种态势下威慑成立的区间
    deltas = [i / 20 for i in range(21)]
    mad_set = {d for d in deltas if deterred(d, DELTA_STAR_MAD)}
    adv_set = {d for d in deltas if deterred(d, DELTA_STAR_ADV)}
    print(f"  扫描 21 点:MAD 威慑成立 {len(mad_set)}/21 个点位, "
          f"单方优势 {len(adv_set)}/21 个点位")
    # 核心断言:MAD 威慑成立区间严格包含单方优势的区间
    assert adv_set <= mad_set, "单方优势区间应被 MAD 区间包含"
    assert len(mad_set) > len(adv_set), "MAD 稳定域应严格更大"
    # 数值例:相当有耐心 δ=0.8
    assert deterred(0.8, DELTA_STAR_MAD) and not deterred(0.8, DELTA_STAR_ADV), \
        "δ=0.8 时应只在 MAD 下威慑成立"
    print(f"  例:δ=0.8(相当耐心)→ MAD 威慑成立, 单方优势失效"
          f"(δ*_adv={DELTA_STAR_ADV:.2f}>1:该态势下任何耐心都不够——"
          f"防御侵蚀 Mutual 的极端化,反直觉②的代码化)")
    print("  PASS: MAD 稳定域 ⊃ 单方优势稳定域, 阈值差 = "
          f"{DELTA_STAR_ADV - DELTA_STAR_MAD:.4f}\n")


# ============================================================
# Part C  威慑三角稳定性矩阵 + 域间传导
# ============================================================
# 设定(家族 01 章方向五 / 04 章走廊三):三域 × 三维序数评分(1-5,
# 高=利于稳定)。三维是威慑三要素(沟通/可信度/能力)的域化:
#   归因难度(沟通:找得到该威慑谁)、惩罚可执行性(能力:还手打得着)、
#   升级可控性(可信度:威胁规模可调、可停)。
# 评分为教学假设的序数编码(S4 模型级),只支持域间比较,不做基数宣称。
DOMAINS = ["常规", "核", "网络"]
DIMS = ["归因(沟通)", "惩罚可执行(能力)", "升级可控(可信度)"]
SCORES = {                        # 教学序数假设,来源:学科通说框架
    "常规": [5, 4, 4],
    "核":   [5, 5, 2],
    "网络": [2, 3, 3],
}
# 域间传导:某域红线被越而无反应,对其他域承诺可信度的侵蚀系数(教学假设)
EROSION = {
    ("网络", "核"): 0.3,    # "数字红线失守→核域承诺账户记账"最重(一体化威慑暗面)
    ("网络", "常规"): 0.2,
    ("常规", "核"): 0.2,
    ("核", "常规"): 0.3,
    ("常规", "网络"): 0.2,
    ("核", "网络"): 0.3,
}


def part_c():
    print("[Part C] 威慑三角稳定性矩阵(序数 1-5, 高=利于稳定)")
    header = "  域   | " + " | ".join(f"{d:^12s}" for d in DIMS) + " | 合计"
    print(header)
    totals = {}
    for dom in DOMAINS:
        s = SCORES[dom]
        totals[dom] = sum(s)
        print(f"  {dom} | " + " | ".join(f"{v:^12d}" for v in s) + f" | {totals[dom]:^4d}")
    # 断言 1:网络域综合稳定性最低(01 章方向五反直觉:三要素在该域结构性缺失)
    assert totals["网络"] < min(totals["常规"], totals["核"]), "网络域应为最低"
    # 断言 2:网络域的最短板是归因("打不还手,还手找不到人")
    assert SCORES["网络"][0] == min(SCORES["网络"]), "网络域最短板应为归因"
    # 断言 3:传导侵蚀——网络红线失守对核域可信度的侵蚀是全部单向传导中最重之一
    net_to_nuclear = EROSION[("网络", "核")]
    assert net_to_nuclear >= max(EROSION.values()) - 1e-9, "网络→核传导应为最重"
    # 侵蚀后的"有效稳定分":核域可信度维被网络域失守侵蚀
    nuclear_eff = SCORES["核"][2] * (1.0 - net_to_nuclear)
    print(f"  域间传导示例:网络红线失守 → 核域可信度维 "
          f"{SCORES['核'][2]} → {nuclear_eff:.1f}(侵蚀系数 {net_to_nuclear})")
    assert nuclear_eff < SCORES["核"][2], "侵蚀应为正向"
    print("  PASS: 网络域垫底+归因为最短板+传导侵蚀为正(一体化威慑的账户视角)\n")


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    print("ALL PARTS PASSED (A: 解析+模拟互证 | B: MAD⊃单方优势 | C: 威慑三角)")
