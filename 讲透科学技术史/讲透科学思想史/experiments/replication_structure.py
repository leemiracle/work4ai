# -*- coding: utf-8 -*-
"""复现危机的统计结构教学版:发表偏倚×功效的零模型(00/01/04 章配套实验)。

主题呼应 01 章检索校准素材(Feest 2024;Rubin 2025——拉卡托斯镜头):
复现危机的"危机感"有多少是**统计结构自带的**,不需要任何人造假?
本脚本模拟一个全部研究都诚实抽样、只有一条规矩的世界:
  **p<0.05(方向一致)才发表**——然后看已发表文献长什么样、复现会怎样。

模型约定(零模型声明):
- 每项研究:真效应 d(标准化均值差),样本量 n,标准误 se=1/sqrt(n);
  观测效应 obs = d + se*Z,Z~N(0,1)(纯抽样波动,无 p-hacking 无造假);
- "显著"=单侧 z>=1.96(等价于双侧 0.05 且方向一致,注释同 04 章 C2);
- 复现:同一真效应、新抽一批样本(同设计 n 不变,除非另注)。

三条断言(01 章热线的统计结构面):
  ① 赢家诅咒:小样本×低先验(大量零/小真效应)领域,已发表结果的
     观测效应系统性夸大真效应;大样本领域该夸大消失;
  ② 双降律:复现成功率随原始真效应量与样本量两者同时下降而下降,
     且逐格逼近解析功效 Φ(d*sqrt(n)-1.96);
  ③ 失败≠造假:在零造假的世界里,纯抽样波动仍产生相当比例的
     复现失败(功效不足的真效应研究)与方向翻转(假阳性原件)——
     给"危机"祛魅的统计结构面(Rubin 2025 的算术版)。

⚠ 纪律(04 章边界):本脚本是**零模型**(对照物),不是任何具体领域
的实证;参数=教学选择,输出度量的是统计结构的性质,不度量任何
真实文献群。跑法: python experiments/replication_structure.py
"""

import math
import random

Z_ALPHA = 1.96  # 单侧 2.5% ≈ 双侧 5%(方向一致)


def phi(x):
    """标准正态 CDF(erf 实现,纯标准库)。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def power(d, n):
    """单侧检验的解析功效:P(Z >= 1.96 | 真效应 d, 样本 n)。"""
    return phi(d * math.sqrt(n) - Z_ALPHA)


def run_study(d, n, rng):
    """一项诚实研究:返回观测效应与显著性(纯抽样波动)。"""
    se = 1.0 / math.sqrt(n)
    obs = d + se * rng.gauss(0.0, 1.0)
    return obs, obs / se >= Z_ALPHA


# ── 场景配置:两个领域,同一发表规则 ────────────────────────────
FIELDS = {
    # 小样本 × 低先验:60% 零效应 + 40% 小效应(0.05-0.45),n=15..40
    "低功效领域(小样本×低先验)": dict(
        n_studies=6000, n_range=(15, 40),
        prior=lambda rng: 0.0 if rng.random() < 0.6 else rng.uniform(0.05, 0.45)),
    # 大样本 × 同一先验:n=200..600,功效结构性抬升
    "高功效领域(大样本×同先验)": dict(
        n_studies=6000, n_range=(200, 600),
        prior=lambda rng: 0.0 if rng.random() < 0.6 else rng.uniform(0.05, 0.45)),
}


def simulate_field(name, cfg, rng):
    """跑一个领域:诚实研究流+显著才发表;返回带发表标记的记录。"""
    lo, hi = cfg["n_range"]
    recs = []
    for _ in range(cfg["n_studies"]):
        d = cfg["prior"](rng)
        n = rng.randint(lo, hi)
        obs, sig = run_study(d, n, rng)
        recs.append(dict(d=d, n=n, obs=obs, pub=sig))
    pub = [r for r in recs if r["pub"]]
    print(f"\n[{name}] 做 {len(recs)} 项研究,显著并发表 {len(pub)} 项"
          f"(发表率 {len(pub)/len(recs):.1%}——发表偏倚的第一眼)")
    return recs, pub


def part1_winners_curse(rng):
    """断言①:赢家诅咒——已发表观测效应夸大真效应,且夸大随功效消失。"""
    print("=" * 76)
    print("断言① 赢家诅咒:显著才发表 → 已发表结果的后验夸大")
    print("=" * 76)
    ratios = {}
    pubrates = {}
    for name, cfg in FIELDS.items():
        recs, pub = simulate_field(name, cfg, rng)
        true_eff = [r for r in pub if r["d"] > 0]  # 发表了的真效应研究
        mean_true = sum(r["d"] for r in true_eff) / len(true_eff)
        mean_obs = sum(r["obs"] for r in true_eff) / len(true_eff)
        ratio = mean_obs / mean_true
        ratios[name] = ratio
        pubrates[name] = len(pub) / len(recs)
        print(f"  发表的真效应研究 {len(true_eff)} 项:"
              f"观测均值 {mean_obs:.3f} vs 真效应均值 {mean_true:.3f}"
              f" → 夸大比 {ratio:.2f}×")
    low = "低功效领域(小样本×低先验)"
    high = "高功效领域(大样本×同先验)"
    assert ratios[low] > 1.4, "低功效领域夸大比应显著大于 1(赢家诅咒)"
    assert ratios[high] < 1.15, "高功效领域夸大比应接近 1"
    assert ratios[low] > ratios[high], "夸大必须随功效上升而消失"
    assert pubrates[low] < 0.2 and pubrates[high] > pubrates[low], \
        "低功效领域发表率应低且低于高功效领域"
    print(f"  ✓ 小样本×低先验领域:文献里的效应量被发表门槛抬升 "
          f"{ratios[low]:.2f}×;同一先验放大样本后夸大比降到 "
          f"{ratios[high]:.2f}×——**读文献先问功效,再信效应量**")


def part2_double_decrease(rng):
    """断言②:双降律——复现成功率随真效应量/样本量双降而降,逼近解析功效。"""
    print("\n" + "=" * 76)
    print("断言② 双降律:复现成功率 = 功效的函数(效应量×样本量)")
    print("=" * 76)
    cells = {}  # (d, n) -> (模拟成功率, 解析功效)
    for d in (0.1, 0.3, 0.5):
        for n in (25, 100):
            reps, ok = 4000, 0
            for _ in range(reps):
                _, sig = run_study(d, n, rng)  # 复现=同真效应重抽
                ok += sig
            sim, ana = ok / reps, power(d, n)
            cells[(d, n)] = (sim, ana)
            print(f"  d={d:.1f}, n={n:>3}:复现成功率 {sim:.3f}"
                  f" ~ 解析功效 {ana:.3f} (差 {abs(sim-ana):.3f})")
    for cell, (sim, ana) in cells.items():
        assert abs(sim - ana) <= 0.035, f"模拟应逼近解析功效:{cell}"
    for n in (25, 100):  # 效应量轴:同 n,效应越大成功率越高
        assert cells[(0.5, n)][0] > cells[(0.3, n)][0] > cells[(0.1, n)][0], \
            "成功率应随效应量上升"
    for d in (0.1, 0.3, 0.5):  # 样本轴:同效应,样本越大成功率越高
        assert cells[(d, 100)][0] > cells[(d, 25)][0], "成功率应随样本量上升"
    gap = cells[(0.5, 100)][0] - cells[(0.1, 25)][0]
    assert gap > 0.8, "双降:两端格差应巨大"
    print(f"  ✓ 双降律成立:低效应×小样本格(约 {cells[(0.1, 25)][0]:.2%})与"
          f"高效应×大样本格(约 {cells[(0.5, 100)][0]:.2%})相差 {gap:.2f}——"
          "**复现成功率不是道德变量,是设计变量**")


def part3_failure_not_fraud(rng):
    """断言③:零造假世界里,纯抽样波动自产复现失败与方向翻转。"""
    print("\n" + "=" * 76)
    print("断言③ 失败≠造假:诚实世界的复现失败分解")
    print("=" * 76)
    cfg = FIELDS["低功效领域(小样本×低先验)"]
    recs, pub = simulate_field("低功效领域(复现场)", cfg, rng)

    succ = flip = 0            # 真效应发表的复现结果
    an_pow = an_flip = 0.0     # 逐研究解析功效/翻转率(期望)
    null_pub = null_flip = null_succ = 0   # 假阳性原件(零真效应)
    forecast = 0.0             # 用文献效应量做的天真预测(赢家诅咒的下游)
    for r in pub:
        obs_rep, sig_rep = run_study(r["d"], r["n"], rng)   # 同设计复现
        forecast += phi(r["obs"] * math.sqrt(r["n"]) - Z_ALPHA)
        if r["d"] == 0.0:
            null_pub += 1
            null_flip += obs_rep < 0
            null_succ += sig_rep
        else:
            succ += sig_rep
            flip += obs_rep < 0
            an_pow += power(r["d"], r["n"])
            an_flip += phi(-r["d"] * math.sqrt(r["n"]))
    true_pub = len(pub) - null_pub
    rate_succ, rate_flip = succ / true_pub, flip / true_pub
    exp_pow, exp_flip = an_pow / true_pub, an_flip / true_pub
    overall_fail = 1 - (succ + null_succ) / len(pub)
    naive_forecast = forecast / len(pub)

    print(f"  发表的真效应研究 {true_pub} 项:复现成功率 {rate_succ:.3f}"
          f"(解析期望 {exp_pow:.3f});方向翻转率 {rate_flip:.3f}"
          f"(解析期望 {exp_flip:.3f})")
    print(f"  发表的假阳性原件(真效应为零){null_pub} 项:"
          f"复现成功率 {null_succ/max(1,null_pub):.3f},"
          f"方向翻转率 {null_flip/max(1,null_pub):.3f}(≈50%)")
    print(f"  全体已发表研究的复现失败率 {overall_fail:.1%}"
          f"——这个世界里**没有任何人造假**")
    print(f"  天真预测(按文献效应量估计的功效){naive_forecast:.3f}"
          f" vs 实际成功率 {1-overall_fail:.3f}"
          f" → 乐观差 {naive_forecast-(1-overall_fail):.3f}")

    assert abs(rate_succ - exp_pow) <= 0.05, "复现成功率应等于逐研究功效均值"
    assert 1 - rate_succ > 0.3, "零造假世界的失败率仍应相当可观"
    assert abs(rate_flip - exp_flip) <= 0.02 and rate_flip > 0.02, \
        "真效应研究的方向翻转=可计算的纯抽样事件"
    assert null_pub >= 30, "发表偏倚必然放行一批假阳性原件"
    assert abs(null_flip / max(1, null_pub) - 0.5) <= 0.12, \
        "假阳性原件的复现方向翻转率应≈50%"
    assert abs(null_succ / max(1, null_pub) - 0.025) <= 0.05, \
        "零真效应下复现'成功'率应≈2.5%(单侧α)"
    assert naive_forecast - (1 - overall_fail) > 0.15, \
        "用夸大的文献效应量预测复现必然系统性乐观(①→③下游)"
    print("  ✓ 三条全过:失败的主项是功效不足的真效应研究(设计问题),\n"
          "    翻转的主项是本就为零的假阳性原件(门槛问题)——\n"
          "    **纯抽样波动即可生产'危机'量级的失败,复现失败≠原研究造假**")


def main():
    rng = random.Random(20260907)  # 定种子:结果可复现
    print("复现危机的统计结构教学版(零模型:人人诚实,只有'显著才发表'一条规矩)")
    part1_winners_curse(rng)
    part2_double_decrease(rng)
    part3_failure_not_fraud(rng)
    print("\n" + "=" * 76)
    print("三条断言全部通过 ✓")
    print("\n一句话收束:把'危机'翻译成统计结构——文献夸大(①)是门槛的形状,\n"
          "复现成功率(②)是设计的函数,失败与翻转(③)是抽样的常态;\n"
          "剩下的问题(实践规范/激励/政治化)才轮到科学论与政策(01 章热线,\n"
          "呼应 Feest 2024『危机是什么的危机』与 Rubin 2025 拉卡托斯镜头)。")
    print("\n⚠ 纪律提醒:本脚本是零模型/对照物,参数=教学选择;\n"
          "度量的是统计结构的性质,不指涉任何真实文献群(04 章 C2 边界)。")


if __name__ == "__main__":
    main()
