# -*- coding: utf-8 -*-
"""杀伤链 vs 杀伤网:闭合时间与抗打击性蒙特卡洛(00/01/04 章配套实验)。

01 章方向一(杀伤链→杀伤网)与 04 章 C1 走廊的成品:
F2T2EA 六环节(发现/定位/跟踪/瞄准/打击/评估)在两种拓扑下的闭合模拟:
  ① 中心化单链(每环单节点):串行管线,断一环即断——单点故障域
     覆盖全部六个环节
  ② 杀伤网(每环双节点,热冗余):任一存活节点对可闭合本环——
     打掉一个节点,该环降级为单节点继续工作
五个结构化断言:
  ① 六环结构完整(F2T2EA 顺序、均值全正、无重复)
  ② 速度:网状平均闭合时间约为单链一半(min-of-2 指数均值 m/2
     解析锚),且显著更短
  ③ 抗单点打击:单链存活率 0.0(任一节点皆要害)vs 网状 1.0
     (无单点要害)——纯拓扑贡献,与资源多少无关
  ④ 抗三点打击:网状存活率 ≈ 160/220(组合解析:12 节点取 3,
     恰打空某环两节点的三重组共 60 种),单链 0.0
  ⑤ 降级仍快:网状被敲掉一个节点后的平均闭合时间,仍短于完好单链
     ——冗余的"速度韧性双收益"
⚠ 纪律(02/04 章):节点时延为示意值(参数即史观);本脚本输出为
推演级(D5)证据,不可当建制文书或条令陈述引用;冗余的速度收益
(min)与韧性收益(路径数)在本设计中同源,解耦须另行设计实验。

跑法: python experiments/kill_web_closure.py
"""

import math
import random

# F2T2EA 六环(美系军语;引用须声明体系——家族 02 章对译表)
# mean 为该环节单节点平均时延(分钟,示意值:传感器捕获慢、
# 打击环节快;01 章方向四"瓶颈迁移律"的基准分布)
STAGES = [
    dict(en="find",    cn="发现", mean=30.0, note="搜索捕获目标"),
    dict(en="fix",     cn="定位", mean=8.0,  note="精确位置解算"),
    dict(en="track",   cn="跟踪", mean=10.0, note="持续跟踪更新"),
    dict(en="target",  cn="瞄准", mean=7.0,  note="火控解算与批准"),
    dict(en="engage",  cn="打击", mean=4.0,  note="交战动作执行"),
    dict(en="assess",  cn="评估", mean=12.0, note="战果判定与再打击"),
]

CHAIN_NODES_PER_STAGE = 1   # 中心化单链:每环单节点
WEB_NODES_PER_STAGE = 2     # 杀伤网:每环双节点热冗余
N_RUNS = 20000              # 蒙特卡洛样本数(种子固定可复现)
SEED = 20260907


def stage_time(rng, mean, k):
    """本环节闭合时延:k 个并行节点取最快——min of k 个 Exp(mean)。

    单节点(k=1)即经典链;双节点(k=2)为网状并行闭合,
    解析均值 mean/k。
    """
    return min(rng.expovariate(1.0 / mean) for _ in range(k))


def simulate(rng, redundancy, strikes=0):
    """一次闭合模拟:先随机敲掉 strikes 个节点,再逐环闭合。

    返回 (闭合时间, 是否闭合)——某环节节点全灭则该链路失败。
    节点池 = 六环 × 每环节点数;打击目标从池中均匀随机抽取
    (对位"无情报优势的随机打击";定向打击见文末局限声明)。
    """
    alive = [redundancy] * len(STAGES)
    pool = [(s, n) for s in range(len(STAGES))
            for n in range(redundancy)]
    for s, n in rng.sample(pool, strikes):
        alive[s] -= 1
    if any(a == 0 for a in alive):
        return None, False
    total = 0.0
    for s, stage in enumerate(STAGES):
        total += stage_time(rng, stage["mean"], alive[s])
    return total, True


def montecarlo(redundancy, strikes):
    """N_RUNS 次模拟 → (平均闭合时间|已闭合, p90, 闭合率)。"""
    rng = random.Random(SEED + redundancy * 100 + strikes)
    times, closed = [], 0
    for _ in range(N_RUNS):
        t, ok = simulate(rng, redundancy, strikes)
        if ok:
            closed += 1
            times.append(t)
    rate = closed / N_RUNS
    mean = sum(times) / len(times) if times else float("inf")
    times.sort()
    p90 = times[int(0.9 * len(times))] if times else float("inf")
    return mean, p90, rate


def percentile_label(x):
    return f"{x:.1f}" if x != float("inf") else "—(链路已断)"


def main():
    print("=" * 76)
    print("杀伤链 vs 杀伤网:闭合时间与抗打击性蒙特卡洛"
          f"(N={N_RUNS}, seed={SEED})")
    print("=" * 76)

    chain_mean_total = sum(s["mean"] for s in STAGES)

    # ── 主表:六环 × 两种拓扑 ────────────────────────────────
    print(f"\nF2T2EA 六环(单节点平均时延,合计 {chain_mean_total:.0f} 分钟):")
    for s in STAGES:
        chain = s["mean"]
        web = s["mean"] / WEB_NODES_PER_STAGE
        print(f"  {s['cn']}({s['en']:<6}) {s['note']:<10} "
              f"单链 {chain:>5.1f} 分 | 网状 {web:>5.1f} 分"
              f"(min-of-{WEB_NODES_PER_STAGE} 解析)")

    mc_chain_0 = montecarlo(CHAIN_NODES_PER_STAGE, strikes=0)
    mc_web_0 = montecarlo(WEB_NODES_PER_STAGE, strikes=0)
    mc_chain_1 = montecarlo(CHAIN_NODES_PER_STAGE, strikes=1)
    mc_web_1 = montecarlo(WEB_NODES_PER_STAGE, strikes=1)
    mc_chain_3 = montecarlo(CHAIN_NODES_PER_STAGE, strikes=3)
    mc_web_3 = montecarlo(WEB_NODES_PER_STAGE, strikes=3)

    print(f"\n{'场景':<14}{'平均闭合':>10}{'P90':>10}{'闭合率':>9}")
    print(f"{'单链·完好':<14}{mc_chain_0[0]:>9.1f}分{mc_chain_0[1]:>9.1f}分"
          f"{mc_chain_0[2]:>9.1%}")
    print(f"{'网状·完好':<14}{mc_web_0[0]:>9.1f}分{mc_web_0[1]:>9.1f}分"
          f"{mc_web_0[2]:>9.1%}")
    print(f"{'单链·敲1点':<14}{percentile_label(mc_chain_1[0]):>9}"
          f"{percentile_label(mc_chain_1[1]):>9}{mc_chain_1[2]:>9.1%}")
    print(f"{'网状·敲1点':<14}{mc_web_1[0]:>9.1f}分{mc_web_1[1]:>9.1f}分"
          f"{mc_web_1[2]:>9.1%}")
    print(f"{'单链·敲3点':<14}{percentile_label(mc_chain_3[0]):>9}"
          f"{percentile_label(mc_chain_3[1]):>9}{mc_chain_3[2]:>9.1%}")
    print(f"{'网状·敲3点':<14}{mc_web_3[0]:>9.1f}分{mc_web_3[1]:>9.1f}分"
          f"{mc_web_3[2]:>9.1%}")

    # ── 断言 1:六环结构完整 ────────────────────────────────
    assert [s["en"] for s in STAGES] == \
        ["find", "fix", "track", "target", "engage", "assess"], \
        "F2T2EA 六环顺序应一致"
    assert len({s["en"] for s in STAGES}) == 6, "环节不得重复"
    assert all(s["mean"] > 0 for s in STAGES), "时延均值全正"
    print("\n断言 1 通过:F2T2EA 六环结构完整,顺序·唯一性·正值 ✓")

    # ── 断言 2:速度(网状 ≈ 单链一半,解析锚对表)────────────
    assert math.isclose(sum(s["mean"] for s in STAGES), 71.0), \
        "单链解析均值应为 71 分"
    assert math.isclose(mc_chain_0[0], chain_mean_total, rel_tol=0.06), \
        "单链蒙特卡洛均值应回到解析锚 71 分"
    ratio = mc_web_0[0] / mc_chain_0[0]
    assert 0.40 < ratio < 0.62, "网状/单链均值比应落在 0.5 邻域"
    assert mc_web_0[0] < 0.70 * mc_chain_0[0], \
        "网状平均闭合时间应显著短于单链"
    print(f"断言 2 通过:网状均值 {mc_web_0[0]:.1f} 分 vs 单链 "
          f"{mc_chain_0[0]:.1f} 分(比 {ratio:.2f},解析锚 0.50;"
          "并行备份的 min-of-k 收益)✓")

    # ── 断言 3:抗单点打击(纯拓扑贡献)──────────────────────
    assert mc_chain_1[2] == 0.0, "单链敲 1 点必断:每个节点皆要害"
    assert mc_web_1[2] == 1.0, "网状敲 1 点必活:无单点要害"
    assert mc_web_1[2] - mc_chain_1[2] >= 0.5, "拓扑差距应为断层式"
    print("断言 3 通过:单点打击存活率 网状 100% vs 单链 0% ✓")
    print("            ——单链的故障域覆盖全部六环;网状把故障域"
          "切到环内(降级不失效)")

    # ── 断言 4:抗三点打击(组合解析对表)────────────────────
    # 12 节点均匀敲 3:失败 ⟺ 某环两节点同时被敲。失败三重组 =
    # 6 环 × (补第三节点 10 选 1) = 60;总数 C(12,3) = 220。
    total_triples = math.comb(12, 3)
    failing_triples = 6 * 10
    web3_theory = 1 - failing_triples / total_triples   # 160/220 ≈ 0.727
    assert math.isclose(web3_theory, 160 / 220), "组合解析应为 160/220"
    assert mc_chain_3[2] == 0.0, "单链敲 3 点必断"
    assert abs(mc_web_3[2] - web3_theory) < 0.04, \
        "网状三点存活率应回到组合解析 160/220"
    assert mc_web_3[2] > 0.5 > mc_chain_3[2], "三点打击差距应过半"
    print(f"断言 4 通过:三点打击存活率 网状 {mc_web_3[2]:.1%} "
          f"(解析 {web3_theory:.1%})vs 单链 0% ✓")

    # ── 断言 5:降级仍快(冗余的双收益)─────────────────────
    # 解析:敲 1 点后,被敲环回到单节点均值 m_s,其余环仍 m/2;
    # 对被敲环均匀平均:总均值 = 71/2 + (71/6)/2 ≈ 41.4 < 71。
    degraded_theory = chain_mean_total / 2 \
        + (chain_mean_total / len(STAGES)) / 2
    assert math.isclose(degraded_theory, 41.416666, abs_tol=0.01)
    assert mc_web_1[0] < mc_chain_0[0], \
        "网状敲掉一点后的平均闭合时间仍应短于完好单链"
    assert abs(mc_web_1[0] - degraded_theory) / degraded_theory < 0.06, \
        "降级均值应回到解析锚 41.4 分"
    print(f"断言 5 通过:网状敲 1 点后均值 {mc_web_1[0]:.1f} 分"
          f"(解析 {degraded_theory:.1f})仍 < 完好单链 "
          f"{mc_chain_0[0]:.1f} 分 ✓")
    print("            ——速度与韧性是同一份冗余的两份利息")

    print("\n" + "=" * 76)
    print("五组断言全部通过:六环结构 / 速度 / 抗单点 / 抗三点 / 降级仍快 ✓")
    print("\n⚠ 纪律提醒:节点时延为示意值(参数即史观);打击为均匀随机"
          "(无情报优势假设,定向打击不在本模型);")
    print("  输出为推演级(D5)证据——速度收益(min 并行)与韧性收益"
        "(路径冗余)在本设计中同源,")
    print("  解耦实验与敌案适应分析留给 04 章 C1 走廊的扩展位。")


if __name__ == "__main__":
    main()
