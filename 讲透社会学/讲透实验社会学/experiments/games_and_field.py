# -*- coding: utf-8 -*-
"""博弈与田野:公共品/最后通牒/列表实验三律。

00-体系结构.md(反直觉:个体理性加总成集体损失/公平是期望收益的解/隐私用精度付账)、
03-可构造与结构.md(实验设计卡/处理操纵卡/预注册卡)与 04-实验社会学转代码.md
(走廊 1/2/3)的配套实验。纯标准库(random/math/statistics)。

三律:
  律一 公共品博弈(n=4,禀赋 20,组池乘子 m=1.6,MPCR=m/n=0.4<1):
      占优策略贡献 0 → 每人 20;全贡献 → 每人 m×20=32;帕累托损失 12/人=37.5%。
      再模拟 10 轮重复博弈(条件合作者按上期组均值×0.9 调整 + 20% 搭便车者,
      末轮预期合作终止额外砍半),断言平均贡献逐轮下降且末轮最低
      (末轮效应/Isaac-Walker 式衰减)——个体理性加总成集体损失。
  律二 最后通牒(响应者拒绝概率经验分段:x<0.15→0.9;0.15≤x<0.25→0.5;
      0.25≤x<0.35→0.15;x≥0.35→0.05;提议者期望收益 U(x)=(1−x)(1−P拒(x))):
      最优 offer x*=0.25、U=0.6375;贪心 offer x=0.05 的 U=0.095 仅为其 14.9%
      ——公平不是道德装饰,是期望收益最大化的解;社会规范把分配点推离
      子博弈完美均衡。
  律三 列表实验的方差代价(真实敏感态度 p=0.3,控制组 4 条中性条目每条
      "是"概率 0.5,处理组 4+1 敏感条目,每组 n=500):
      估计量 p̂=μ处理−μ控制 无偏(MC 2000 次均值 0.3±0.01);
      但 SE≈直接提问的 3.2 倍(理论:Var 控制=4×0.25/500、
      Var 处理=(4×0.25+0.3×0.7)/500,比率=√(2.21/0.21)≈3.24,MC 互证
      落在 [2.9,3.6])——隐私买来,用精度付账。

跑法: python -u -X utf8 experiments/games_and_field.py
"""

import math
import random
import statistics

ENDOW = 20.0        # 禀赋
N_PLAYERS = 4       # 组规模
MULT = 1.6          # 组池回报乘子 m
MPCR = MULT / N_PLAYERS   # 边际人均回报 = m/n = 0.4 < 1


def pg_payoff(own, others_total):
    """公共品博弈支付:留下(20−c)+ MPCR×组池总额(含自己贡献)。"""
    return (ENDOW - own) + MPCR * (own + others_total)


# ============================ 律一:公共品博弈 ============================

def act1_one_shot():
    print("=" * 84)
    print("律一 公共品博弈·一次性:占优策略的算术(n=4,禀赋 20,m=1.6,MPCR=0.4)")
    print("=" * 84)
    print(f"\n每人支付 = (20 − c_i) + {MPCR}×Σ全组c_j;每贡献 1 个代币:"
          f"自留可得 1,入池只得 {MPCR}(其余 {MULT - MPCR:.1f} 漏给组员)")
    all_keep = pg_payoff(0.0, 0.0)
    all_give = pg_payoff(ENDOW, 3 * ENDOW)
    loss_abs = all_give - all_keep
    loss_pct = loss_abs / all_give
    defect = pg_payoff(0.0, 3 * ENDOW)
    print(f"\n  全搭便车(c=0)…… 每人 {all_keep:.1f}")
    print(f"  全贡献(c=20)…… 每人 {all_give:.1f}(= m×20)")
    print(f"  帕累托损失 …… {loss_abs:.0f}/人 = {loss_pct:.1%}")
    print(f"  单边偏离(他人全贡献,自己捂住)…… {defect:.1f} > {all_give:.1f}")

    assert all_keep == 20.0, "全搭便车时每人应得 20"
    assert abs(all_give - MULT * ENDOW) < 1e-12, "全贡献时每人应得 m×20=32"
    assert abs(loss_abs - 12.0) < 1e-12 and abs(loss_pct - 0.375) < 1e-12, \
        "帕累托损失应为 12/人 = 37.5%"
    # 占优:无论他人贡献多少,捂住都比贡献好 20 − MPCR×20 = 12
    for S in (0.0, 40.0, 60.0):
        assert pg_payoff(0.0, S) - pg_payoff(ENDOW, S) == 12.0, \
            "贡献 0 应严格占优(任何他人总额下都好 12)"
    assert defect > all_give > all_keep, "偏离>全贡献>全搭便车:个体理性毁掉集体最优"
    print(f"\n✓ 律一(一次性)断言通过:均衡 20/人 vs 帕累托最优 32/人,"
          f"损失 37.5%;单边偏离拿 {defect:.0f}——合作无人守得住")
    return all_give, all_keep


def repeated_public_goods(n_groups=400, rounds=10, seed=20260901):
    """10 轮重复公共品:80% 条件合作者(按上期组均值×0.9 调整,带 ±10% 噪声,
    首轮高起步 0.85-1.0×20)+ 20% 搭便车者(恒 0);末轮预期合作终止再砍半。
    返回各轮平均贡献与平均支付。"""
    rng = random.Random(seed)
    free_rider = [[rng.random() < 0.2 for _ in range(N_PLAYERS)]
                  for _ in range(n_groups)]
    prev = None
    means, payoffs = [], []
    for t in range(1, rounds + 1):
        round_c = []
        for g in range(n_groups):
            mean_prev = sum(prev[g]) / N_PLAYERS if prev else None
            cs = []
            for i in range(N_PLAYERS):
                if free_rider[g][i]:
                    c = 0.0
                elif t == 1:
                    c = ENDOW * rng.uniform(0.85, 1.0)   # 首轮高贡献
                else:
                    c = 0.9 * mean_prev * rng.uniform(0.9, 1.1)
                    if t == rounds:                      # 末轮效应
                        c *= 0.5
                    c = min(max(c, 0.0), ENDOW)
                cs.append(c)
            round_c.append(cs)
        prev = round_c
        m = sum(sum(cs) for cs in round_c) / (n_groups * N_PLAYERS)
        means.append(m)
        payoffs.append(ENDOW + (MULT - 1.0) * m)         # 组均支付=20+0.6×均值
    return means, payoffs


def act1_repeated():
    print("\n" + "-" * 84)
    print("律一·续 10 轮重复博弈:条件合作者×0.9 追赶 + 20% 搭便车(末轮效应)")
    print("-" * 84)
    means, payoffs = repeated_public_goods()
    print(f"\n{'轮':>3} {'平均贡献':>9} {'平均支付':>9}   (帕累托最优支付 32.0/轮)")
    for t, (m, p) in enumerate(zip(means, payoffs), 1):
        bar = "#" * max(1, int(m / 0.5))
        print(f"{t:>3} {m:>9.2f} {p:>9.2f}   {bar}")
    r1, r10 = means[0], means[-1]
    avg_pay = sum(payoffs) / len(payoffs)
    print("\n读数:")
    print(f"  · 首轮平均贡献 {r1:.2f}(禀赋的 {r1 / ENDOW:.0%})——人并非天生搭便车")
    print(f"  · 逐轮滑落,末轮 {r10:.2f}(仅禀赋 {r10 / ENDOW:.1%}),且低于衰减趋势——"
          "预期到『这是最后一轮』,条件合作者提前撤梯子(末轮效应)")
    print(f"  · 十轮平均支付 {avg_pay:.2f} < 32.0:合作从半山腰出发,一路向下漏")

    # 断言:平均贡献逐轮严格下降,末轮最低
    for t in range(len(means) - 1):
        assert means[t + 1] < means[t], \
            f"第 {t + 1}→{t + 2} 轮应下降:{means[t]:.2f} → {means[t + 1]:.2f}"
    assert means[-1] == min(means), "末轮应为全程最低"
    assert r1 > 0.6 * ENDOW, "首轮条件合作者应高起步(>60% 禀赋)"
    assert 20.0 < payoffs[0] < 32.0, "首轮支付应介于全背叛与帕累托最优之间"
    print(f"\n✓ 律一(重复)断言通过:贡献 {r1:.2f}→{r10:.2f} 逐轮下降且末轮最低"
          f"(Isaac-Walker 式衰减);个体理性加总成集体损失")


def act1():
    act1_one_shot()
    act1_repeated()


# ============================ 律二:最后通牒 ============================

def reject_prob(x):
    """响应者拒绝概率的经验分段(实验数据式的阶梯)。"""
    if x < 0.15:
        return 0.9
    if x < 0.25:
        return 0.5
    if x < 0.35:
        return 0.15
    return 0.05


def act2():
    print("\n" + "=" * 84)
    print("律二 最后通牒:公平是期望收益最大化的解")
    print("=" * 84)
    xs = [i / 100 for i in range(1, 100)]
    U = {x: (1 - x) * (1 - reject_prob(x)) for x in xs}
    x_star = max(U, key=U.get)
    u_star = U[x_star]
    u_greedy = U[0.05]
    ratio = u_greedy / u_star
    print(f"\nU(x) = (1−x)×(1−P拒(x)),分段拒绝率:0.9/0.5/0.15/0.05")
    print(f"{'x(offer)':>9} {'P拒绝':>6} {'U(x)':>8}")
    for x in (0.05, 0.15, 0.25, 0.35, 0.50):
        print(f"{x:>9.2f} {reject_prob(x):>6.2f} {U[x]:>8.4f}"
              + ("   ← 最优" if x == x_star else ""))
    print(f"\n  子博弈完美均衡(自利响应者)推 x→0;经验世界里 x=0.01 的 U="
          f"{U[0.01]:.3f}——贪心被拒绝率吃掉")
    print(f"  最优 offer x* = {x_star},U = {u_star:.4f};贪心 offer 0.05 的 "
          f"U = {u_greedy:.3f},仅为最优的 {ratio:.1%}")

    assert abs(x_star - 0.25) < 1e-9, f"x* 应为 0.25,实测 {x_star}"
    assert abs(u_star - 0.6375) < 1e-9, f"U(x*) 应为 0.6375,实测 {u_star}"
    assert abs(u_greedy - 0.095) < 1e-9, "U(0.05) 应为 0.95×0.1=0.095"
    assert abs(ratio - 0.149) < 0.001, "贪心收益占比应≈14.9%"
    assert U[0.25] > U[0.15] > U[0.05], "从贪心走向公平,期望收益单调改善"

    # MC 互证:固定 offer 面对随机响应者
    rng = random.Random(20260902)
    n_pairs = 200_000
    print(f"\nMC 互证({n_pairs:,} 对提议者×响应者/档):")
    for x in (0.05, 0.25):
        acc = sum(1 for _ in range(n_pairs) if rng.random() >= reject_prob(x))
        u_emp = (1 - x) * acc / n_pairs
        print(f"  x={x:.2f}: 经验 U = {u_emp:.4f}(理论 {U[x]:.4f})")
        assert abs(u_emp - U[x]) < 0.005, f"MC 经验 U 应收敛到理论(x={x})"
    print(f"\n✓ 律二断言通过:把拒绝当真实约束,最优化自动落在公平区——"
          f"社会规范把分配点推离子博弈完美均衡(x→0)整整 0.25")


# ========================= 律三:列表实验的方差代价 =========================

def binomial4(rng):
    return sum(1 for _ in range(4) if rng.random() < 0.5)


def act3():
    print("\n" + "=" * 84)
    print("律三 列表实验:隐私买来,用精度付账(p=0.3,n=500/组)")
    print("=" * 84)
    p, n = 0.3, 500
    var_c = 4 * 0.25                       # 控制组单答方差(4 条中性)
    var_t = 4 * 0.25 + p * (1 - p)         # 处理组:中性噪声 + 敏感信号
    se_list = math.sqrt((var_c + var_t) / n)
    se_direct = math.sqrt(p * (1 - p) / n)
    ratio = se_list / se_direct
    print(f"\n  列表法:p̂ = μ处理 − μ控制(无人被问『你有没有 X 态度』)")
    print(f"  Var 控制/人 = {var_c:.2f};Var 处理/人 = {var_t:.2f}"
          f"(中性噪声 2.00 淹没敏感信号 {p * (1 - p):.2f})")
    print(f"  SE(列表) = √({var_c:.2f}+{var_t:.2f})/√{n} = {se_list:.4f};"
          f"SE(直接) = √{p * (1 - p) / n:.4f} = {se_direct:.4f}")
    print(f"  比率 = {ratio:.3f}——同样的显著性,样本要 ×{ratio ** 2:.1f}"
          f"(≈{int(n * ratio ** 2 / 100) / 10:.1f}k/组)")

    assert abs(var_c - 1.0) < 1e-12 and abs(var_t - 1.21) < 1e-12
    assert abs(ratio - math.sqrt(2.21 / 0.21)) < 1e-12
    assert abs(ratio - 3.244) < 0.01, "理论 SE 比率应≈3.24"

    reps = 2000
    rng = random.Random(20260903)
    ests, directs = [], []
    for _ in range(reps):
        mu_c = sum(binomial4(rng) for _ in range(n)) / n
        mu_t = sum(binomial4(rng) + (1 if rng.random() < p else 0)
                   for _ in range(n)) / n
        ests.append(mu_t - mu_c)
        directs.append(sum(1 for _ in range(n) if rng.random() < p) / n)
    mean_est = sum(ests) / reps
    se_emp_list = statistics.stdev(ests)
    se_emp_direct = statistics.stdev(directs)
    emp_ratio = se_emp_list / se_emp_direct
    print(f"\nMC {reps} 次:")
    print(f"  p̂ 均值 = {mean_est:.4f}(真值 0.3,偏差 {mean_est - p:+.4f})——无偏")
    print(f"  经验 SE:列表 {se_emp_list:.4f} vs 直接 {se_emp_direct:.4f},"
          f"比率 {emp_ratio:.3f}(理论 {ratio:.3f})")

    assert abs(mean_est - p) <= 0.01, f"MC 均值应 0.3±0.01,实测 {mean_est:.4f}"
    assert 2.9 <= emp_ratio <= 3.6, f"MC SE 比率应落 [2.9,3.6],实测 {emp_ratio:.3f}"
    print(f"\n✓ 律三断言通过:无偏(偏差 {abs(mean_est - p):.4f}≤0.01)但方差代价 "
          f"{emp_ratio:.2f} 倍——间接提问买到社会期许偏差的豁免,付掉 3 倍精度")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 公共品:MPCR<1 → 均衡全搭便车(20/人),帕累托损失 37.5%;")
    print("     重复博弈中条件合作被搭便车者持续稀释,逐轮衰减且末轮崩落")
    print("  ② 最后通牒:把经验拒绝率当约束,x*=0.25 是期望收益最大化的解——")
    print("     公平即理性(在社会规范在场的世界里)")
    print("  ③ 列表实验:估计量无偏,SE 代价≈3.2 倍——隐私与精度不可兼得")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
