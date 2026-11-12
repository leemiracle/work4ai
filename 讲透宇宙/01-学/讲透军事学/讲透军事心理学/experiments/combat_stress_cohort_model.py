# -*- coding: utf-8 -*-
"""
combat_stress_cohort_model.py — 战斗减员-心理减员队列模型
(S.L.A. Marshall 射击率命题 × Appel-Beebe 崩溃点 × PIE 前送/后送政策对照)

对应章:04-军事心理学转代码(走廊②,主样本)/00-体系结构(反直觉发现⑥:
      马歇尔命题的方法论争议)/03-可构造与结构(阈值结构:崩溃点)
GB/T 83020 军事心理学 · 家族层实验(纯标准库,assert 自验证)

做什么:一个 N 人步兵队列的战斗日蒙特卡洛——
  1) 射击率:按 Marshall 命题校准的参与率(低纽带场景落在 15-25% 带)
  2) 崩溃:日应激剂量累积越过个人崩溃点 → 精神减员发作(episodes)
  3) 政策:前线处置(PIE,归队率0.70,阈值回落) vs 后送(0.20,慢性离队)
  4) 对照:高/低凝聚力的剂量差 → 首次崩溃日、减员结构的分岔

参数表=模型的质量声明(04 章"化身眼"):
  · 崩溃点 N(220,40) 战斗日 —— Appel & Beebe 1946 通说"聚合战斗日
    200-240 天崩溃"【通说档】
  · 前送归队率 0.70 / 后送 0.20 —— 二战前线处置归队率"常报六至
    八成、后送骤降"的化身【命题化身档】
  · 射击率基线 p = 0.10 + 0.35*cohesion + 0.20*leadership —— 按
    Marshall 1947"仅 15-25% 实际开火"校准;该数字后被 Spiller 1988/
    Engen 2011 质疑,本模型只复现命题逻辑,不背书数字【有争议档】
  · 剂量系数/负伤率 0.002/日、再崩溃阈值 ×0.85 —— 无文献锚,
    仅为让机制成立的自设【自设档】

运行:python combat_stress_cohort_model.py   (全部 assert 通过即 exit 0)
"""

import random


# ---------- 1. 射击率:Marshall 命题的化身 ----------

def firing_fraction(cohesion, leadership, seed=7, n_soldiers=400,
                    n_engagements=200):
    """单兵单次交战对敌开火的概率(命题校准,非实测)"""
    p = 0.10 + 0.35 * cohesion + 0.20 * leadership
    rng = random.Random(seed)
    fired = sum(1 for _ in range(n_soldiers * n_engagements)
                if rng.random() < p)
    return fired / float(n_soldiers * n_engagements)


def demo_firing():
    print("[1] 射击率(Marshall 1947 命题校准;数字连同争议一起读)")
    f_low = firing_fraction(0.2, 0.2)   # 低凝聚力、低领导信任
    f_high = firing_fraction(0.8, 0.7)  # 高凝聚力、高领导信任
    print("    低纽带场景:对敌开火率 = %.1f%%(命题带 15-25%%)" % (100 * f_low))
    print("    高纽带场景:对敌开火率 = %.1f%%(训练与纽带的方向性抬升)"
          % (100 * f_high))
    # 命题带校准:低纽带场景落在 15-25%
    assert 0.15 <= f_low <= 0.25, f_low
    # 方向:纽带与领导抬升参与率
    assert f_high > f_low + 0.15, (f_low, f_high)


# ---------- 2. 崩溃队列:剂量×崩溃点×政策 ----------

def simulate(N=400, combat_days=300, cohesion=0.5, leadership=0.5,
             policy="forward", seed=42):
    """跑一个队列。返回减员结构。

    崩溃机制:stress 逐日累积 dose×U(0.5,1.5);越过 cap 发作一次;
      前线处置:70% 归队(stress 减半、cap×0.85——再崩溃更容易),
                30% 后送(慢性离队);
      后送政策:20% 归队,80% 后送。
    并行记账:战斗减员(负伤离队,0.002/日)与心理减员同场竞争。
    """
    rng = random.Random(seed)
    squad = []
    for _ in range(N):
        cap = rng.gauss(220.0, 40.0)            # 【通说档】Appel-Beebe
        squad.append({"cap": max(60.0, cap), "stress": 0.0,
                      "status": "duty", "episodes": 0, "first": None})
    dose = 1.30 - 0.60 * cohesion - 0.30 * leadership   # 【自设档】
    return_rate = 0.70 if policy == "forward" else 0.20  # 【命题化身档】
    wounded = 0
    for day in range(1, combat_days + 1):
        for s in squad:
            if s["status"] != "duty":
                continue
            if rng.random() < 0.002:            # 战斗减员(负伤)
                s["status"] = "wounded"
                wounded += 1
                continue
            s["stress"] += dose * rng.uniform(0.5, 1.5)
            if s["stress"] >= s["cap"]:          # 心理减员发作
                s["episodes"] += 1
                if s["first"] is None:
                    s["first"] = day
                if rng.random() < return_rate:   # 前线处置→归队
                    s["cap"] *= 0.85
                    s["stress"] = 0.5 * s["cap"]
                else:                            # 后送→慢性离队
                    s["status"] = "evac"
    evac = sum(1 for s in squad if s["status"] == "evac")
    episodes = sum(s["episodes"] for s in squad)
    firsts = [s["first"] for s in squad if s["first"] is not None]
    return {"N": N, "evac": evac, "episodes": episodes, "wounded": wounded,
            "first_days": firsts, "dose": dose, "policy": policy}


def mean(xs):
    return sum(xs) / float(len(xs)) if xs else float("nan")


def demo_policy_and_cohesion():
    print("[2] 队列对照(同 seed=42,N=400,300 战斗日)")
    A = simulate(cohesion=0.2, leadership=0.2, policy="forward")
    B = simulate(cohesion=0.2, leadership=0.2, policy="evac")
    C = simulate(cohesion=0.8, leadership=0.7, policy="forward")
    for name, r in (("A 前送·低纽带", A), ("B 后送·低纽带", B),
                    ("C 前送·高纽带", C)):
        print("    %s:发作 %4d 次 | 后送(慢性)%3d 人 | 负伤 %3d 人 | "
              "首崩均值 %6.1f 日"
              % (name, r["episodes"], r["evac"], r["wounded"],
                 mean(r["first_days"])))
    print("    A/B 心理:战斗减员 = %.2f : %.2f"
          % (A["episodes"] / float(A["wounded"]),
             B["episodes"] / float(B["wounded"])))

    # 现场一:前送把慢性损失换成可重复的急性发作——
    #   慢性(后送)人数大减;归队者再次接近崩溃,总发作次数上升
    assert A["evac"] < B["evac"], (A["evac"], B["evac"])
    assert A["episodes"] > B["episodes"], (A["episodes"], B["episodes"])

    # 现场二:纽带改变剂量而非命运——高凝聚力推迟首崩、减员全线下降,
    #   但分布尾巴仍在("没人崩溃"不是可达政策目标)
    assert mean(C["first_days"]) > mean(A["first_days"])
    assert C["episodes"] < A["episodes"]
    assert C["evac"] < A["evac"]

    # 现场三:两条减员流同场记账(卫勤口径的代码倒影)——
    #   低纽带场景下心理减员与战斗减员同数量级(顺序合理性检验);
    #   高纽带场景(C)比率被压低,正是保护因子在起作用
    assert all(r["wounded"] > 0 for r in (A, B, C))
    for r in (A, B):
        ratio = r["episodes"] / float(r["wounded"])
        assert 0.5 < ratio < 10.0, (r["policy"], ratio)
    return A, B, C


def main():
    print("=" * 66)
    print("战斗减员-心理减员队列模型:马歇尔命题×崩溃点×PIE 政策对照")
    print("=" * 66)
    demo_firing()
    A, B, C = demo_policy_and_cohesion()
    print("-" * 66)
    print("全部 assert 通过。读法:")
    print("  · 前送(PIE):慢性离队↓、总发作↑——两本账必须分开记(04章双账眼)")
    print("  · 凝聚力:剂量↓→首崩推迟,但个体崩溃点有分布,零崩溃不可达")
    print("  · 本模型是'命题的化身':参数各带档位注记,输出复现命题逻辑,")
    print("    不构成对任何真实军队的预测。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
