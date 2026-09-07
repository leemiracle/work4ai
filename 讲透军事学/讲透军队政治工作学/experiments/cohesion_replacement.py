# -*- coding: utf-8 -*-
"""凝聚力×替换制度模拟:单位轮换 vs 个体替换(00 章反直觉① +
04 章 C1 走廊的成品实验)——越战人员管理教训的机制化。

模型:两个"营位"以同等节奏接敌(每轮一次交战),仅人员制度不同:
  A 营位=单位替换制:营位由整建营填充;满 D_DEPLOY 轮部署后整建制
    换防,由一个"共同训成"的整建营(入场前已共训 PRETRAIN 轮,
    入场即满凝聚、满训练)接替——减员在部署期发生,补员在换防后
    的重训期集中完成(本实验以"满编新营接替"近似)。
  B 营位=个体替换制:同一个营常驻;每轮减员即时以个体新兵回填,
    且每名成员服役满 TOUR_LEN 轮即单独离队(个人服役期制度)。
纽带与战力:
  士兵属性=在本单位的共处轮数 tenure + 训练水平(新兵 TRAIN0 起,
    每轮 +TRAIN_GAIN,上限 TRAIN_MAX;A 营入场均已共同训成=满值)
  两人的纽带强度以共处时长代理:co-time(i,j)=min(tenure_i,tenure_j)
  营凝聚力 = P(随机两人共处 >= T_BOND 轮) = (tenure>=T_BOND 比例)^2(精确)
  战斗力 = (凝聚地板+(1-凝聚地板)x凝聚力)x平均训练水平——凝聚力是
    放大器不是开关:纪律与训练托底(COH_FLOOR),纽带决定上限
  每轮战损率 = BASE x(基准战力/战斗力)
  新兵(共处<T_BOND)战损风险 x NEWBIE_RISK——任职初期风险最高(通说方向锚)

四个断言:
  1 稀释律:B 营凝聚力从满值显著下滑到稳态——个体替换=持续稀释纽带存量
  2 稳态差:A 营位平均部署凝聚力显著高于 B 营稳态凝聚力
  3 战损比:B 营位人均战损率 >= 1.8 x A 营位——凝聚力折成战损
  4 扩大律:B-A 累计战损差随轮次单调扩大(后段每轮差 > 前段每轮差)
    ——低凝聚 -> 高战损 -> 多补员 -> 更低凝聚的恶性循环

⚠ 建模边界(00 章假设二·标准士兵假设的机器面):
  纽带仅以共处时长代理——领导力/信念/选拔相容性(Shils & Janowitz
  已证明重要)全部未建模;参数=人员政策假设,引用须附来源;
  A 制度的代价(一岗多备的编制开销与换防运力)未计价——输出是
  制度比较的序数结论(哪种制度更护存量),不是任何真实军队的
  战损预言(04 章 1 可机械化边界)。

跑法: python experiments/cohesion_replacement.py
"""
import math
import random

N = 600              # 营兵力
ROUNDS = 48          # 模拟轮数(月)
SEED = 20260907      # 固定种子=可复现;换种子看方差是正确姿势

T_BOND = 4           # 成钮时长:共处满 T 轮才算"老战友"(最敏感的组织假设)
D_DEPLOY = 12        # A 营单次部署长度(轮)
TOUR_LEN = 12        # B 营个人服役期:满 12 轮单独离队(个人轮换制度)
PRETRAIN = 6         # A 营新接替营的战前共同训练轮数(>=T_BOND,入场即成钮)
BASE = 0.025         # 基准战损率:满战力营每轮 2.5%
REF_POWER = 0.9      # 基准战力:满凝聚(1.0)x 满训练(0.9)
COH_FLOOR = 0.25     # 凝聚地板:零凝聚单位仍有纪律与训练托底(防"开关式"失真)
TRAIN0, TRAIN_GAIN, TRAIN_MAX = 0.5, 0.025, 0.9
NEWBIE_RISK = 1.5    # 新兵超额战损倍率(任职初期风险最高,通说方向锚)
RATE_CAP = 0.30      # 战损率上限:防恶性循环数值失控


def fresh_battalion(rng):
    """成建制作战营:全员战前共同训练(入场即满凝聚、满训练)。"""
    return [[PRETRAIN, TRAIN_MAX] for _ in range(N)]


def veteran_battalion(rng):
    """B 营初始状态:开战前已长期共处的老营(满凝聚、满训练);
    入伍时点错峰(tenure 随机分布于服役期内)——到点离队自然滚动。"""
    return [[rng.randint(T_BOND, TOUR_LEN - 1), TRAIN_MAX] for _ in range(N)]


def cohesion(bt):
    """营凝聚力=随机两人共处>=T_BOND 的概率=(共处达标比例)^2(精确)。"""
    frac = sum(1 for ten, _ in bt if ten >= T_BOND) / len(bt)
    return frac * frac


def mean_training(bt):
    return sum(tr for _, tr in bt) / len(bt)


def combat_power(bt):
    """战斗力=(凝聚地板+(1-地板)x凝聚力)x平均训练水平
    (凝聚力是放大器不是开关:地板=纪律与训练的托底战力)。"""
    c = cohesion(bt)
    return (COH_FLOOR + (1 - COH_FLOOR) * c) * mean_training(bt)


def casualty_rate(bt):
    """本营每轮战损率:战力越低损耗越高;上限保护。"""
    return min(BASE * REF_POWER / max(combat_power(bt), 0.05), RATE_CAP)


def take_casualties(rng, bt, rate):
    """按个体风险(新兵 x NEWBIE_RISK)抽减员,返回减员数。"""
    survivors, lost = [], 0
    for ten, tr in bt:
        p = rate * (NEWBIE_RISK if ten < T_BOND else 1.0)
        if rng.random() < p:
            lost += 1
        else:
            survivors.append([ten, tr])
    return survivors, lost


def main():
    rng = random.Random(SEED)
    print("=" * 76)
    print(f"凝聚力x替换制度模拟:{ROUNDS} 轮减员-补充循环 · 单位轮换 vs 个体替换"
          f"(seed={SEED})")
    print("=" * 76)
    print(f"参数:营 {N} 人 | 成钮 T={T_BOND} 轮 | A:整建部署 {D_DEPLOY} 轮+整建制换防"
          f"(新营战前共训 {PRETRAIN} 轮)")
    print(f"      B:常驻+减员即时回填个体新兵+个人服役 {TOUR_LEN} 轮到点即走"
          f" | 新兵战损 x{NEWBIE_RISK}")
    print("      凝聚力=(共处>=T 的比例)^2 | 战斗力=(地板+(1-地板)x凝聚)x训练 | "
          "战损率=基准x基准战力/本营战力")

    a_bt = fresh_battalion(rng)     # A 营位:当前在位的整建营
    b_bt = veteran_battalion(rng)   # B 营位:同一个老营,常驻
    a_swaps, a_deployed = 0, 0
    a_cum = b_cum = 0               # 累计战损(A 营位/B 营位口径)
    a_coh_hist, b_coh_hist, gaps = [], [], []

    for r in range(1, ROUNDS + 1):
        # ── A 营位:整建制作战 ──────────────────────────────
        ca = cohesion(a_bt)
        rate_a = casualty_rate(a_bt)                     # = BASE(满战力)
        a_bt, lost_a = take_casualties(rng, a_bt, rate_a)
        a_cum += lost_a
        for s in a_bt:
            s[0] += 1                                    # 幸存者共处时长+1
        a_deployed += 1
        if a_deployed == D_DEPLOY:                       # 整建制换防
            a_swaps += 1
            a_bt, a_deployed = fresh_battalion(rng), 0   # 共同训成的新营上

        # ── B 营位:常驻+个体替换 ──────────────────────────
        cb = cohesion(b_bt)
        rate_b = casualty_rate(b_bt)
        b_bt, lost_b = take_casualties(rng, b_bt, rate_b)
        b_cum += lost_b
        stay = []
        for ten, tr in b_bt:
            ten += 1
            if ten >= TOUR_LEN:                          # 个人服役期满,单独离队
                continue
            stay.append([ten, min(tr + TRAIN_GAIN, TRAIN_MAX)])
        b_bt = stay
        for _ in range(N - len(b_bt)):                   # 即时回填个体新兵
            b_bt.append([0, TRAIN0])

        a_coh_hist.append(ca)
        b_coh_hist.append(cb)
        gaps.append(b_cum - a_cum)
        if r % 6 == 0 or r == 1:
            print(f"  轮{r:>3}: A 凝聚 {ca:.3f} | B 凝聚 {cb:.3f} "
                  f"B训练 {mean_training(b_bt):.3f} | 累计战损 A {a_cum:>4} "
                  f"B {b_cum:>4} 差 {b_cum - a_cum:>4}")

    rateA_total = a_cum / (N * ROUNDS)
    rateB_total = b_cum / (N * ROUNDS)
    n_batt = 1 + math.ceil(ROUNDS / D_DEPLOY)
    print(f"\nA 营位共使用整建营 {n_batt} 个(初始+换防 {a_swaps} 次);"
          f"人均战损率 A {rateA_total:.3%} vs B {rateB_total:.3%}")

    # ── 断言 1:稀释律(B 营凝聚力从满值跌入低稳态)──────────
    b_steady = sum(b_coh_hist[-8:]) / 8
    assert b_coh_hist[0] == 1.0 and b_steady < 0.70, \
        f"个体替换应显著稀释凝聚力,实测稳态 {b_steady:.3f}"
    print(f"\n断言 1(稀释律):B 营凝聚力 1.000 -> 稳态 {b_steady:.3f} ✓"
          "\n              ——减员回填+服役期满即走=纽带存量持续漏损")

    # ── 断言 2:稳态差(A 营位平均部署凝聚力显著更高)────────
    a_avg = sum(a_coh_hist) / len(a_coh_hist)
    assert a_avg > 0.95 and a_avg - b_steady > 0.30, \
        f"单位轮换应显著护住凝聚力,实测 A {a_avg:.3f} vs B {b_steady:.3f}"
    print(f"断言 2(稳态差):A 营位平均部署凝聚力 {a_avg:.3f} 对 B 稳态 "
          f"{b_steady:.3f},差 {a_avg - b_steady:.3f} ✓"
          "\n              ——整建制进出把稀释集中到换防瞬间,部署期内存量守恒")

    # ── 断言 3:战损比(B 营位人均战损率 >= 1.8 x A)─────────
    ratio = rateB_total / rateA_total
    assert ratio >= 1.8, f"个体替换营战损率应显著更高,实测比值 {ratio:.2f}"
    print(f"断言 3(战损比):B/A 人均战损率 = {ratio:.2f} ✓"
          "\n              ——凝聚力与训练双低 -> 战力折损 -> 战损放大")

    # ── 断言 4:扩大律(累计战损差随轮次单调扩大)────────────
    ck = [gaps[i - 1] for i in range(8, ROUNDS + 1, 8)]
    assert all(x < y for x, y in zip(ck, ck[1:])), f"战损差应单调扩大:{ck}"
    per_round = ck[-1] / ROUNDS
    assert ck[-1] >= 3 * ck[0], "战损差应持续扩大到显著量级"
    print(f"断言 4(扩大律):累计战损差逐段单调扩大 {ck} ✓"
          f"\n              ——平均每轮扩大 {per_round:.0f} 人"
          "(低凝聚->高战损->多补员->更低凝聚的恶性循环)")

    print("\n" + "=" * 76)
    print("四组断言全部通过:稀释律 / 稳态差 / 战损比 / 扩大律 ✓")
    print("\n⚠ 建模边界提醒:纽带仅以共处时长代理(领导/信念/选拔未建模);")
    print("  A 制度的编制与运力代价未计价(制度权衡的另一半);"
          "参数=人员政策假设,")
    print("  引用须附来源。输出=制度比较的序数结论,不是战损预言。")


if __name__ == "__main__":
    main()
