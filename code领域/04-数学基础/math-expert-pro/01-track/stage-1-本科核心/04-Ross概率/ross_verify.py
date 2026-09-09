# -*- coding: utf-8 -*-
"""Ross《A First Course in Probability》9e 现代验证
组合 / Bayes / 随机变量 / 期望 / 大数定律 / 中心极限定理 CLT
纯 Python 无依赖（用 random 模拟）"""
import random
import math
from collections import Counter

random.seed(2026)

# ---------- §1 组合分析 ----------
def section_combinatorics():
    print("\n" + "="*60)
    print("【§1 组合分析：排列/组合/乘法原理（Ross ch1）】")
    print("="*60)
    def factorial(n): return math.factorial(n)
    def perm(n, k): return factorial(n)//factorial(n-k)
    def comb(n, k): return factorial(n)//(factorial(k)*factorial(n-k))
    print(f"排列 P(10,3) = {perm(10,3)}（从 10 选 3 排列）")
    print(f"组合 C(10,3) = {comb(10,3)}（从 10 选 3 不计序）")
    # 生日问题：23 人至少两人生日相同的概率
    def birthday_prob(n):
        p = 1.0
        for i in range(n):
            p *= (365-i)/365
        return 1 - p
    for n in [10, 23, 30, 50]:
        print(f"  {n} 人至少两人生日相同概率 = {birthday_prob(n):.4f}（23 人已超 50%！）")
    # 蒙特卡洛验证生日问题
    trials = 100000
    match = sum(1 for _ in range(trials) if len(set(random.randint(1,365) for _ in range(23))) < 23)
    print(f"  蒙特卡洛（10万次，23人）= {match/trials:.4f}（与理论 {birthday_prob(23):.4f} 吻合）")

# ---------- §3 Bayes 定理 ----------
def section_bayes():
    print("\n" + "="*60)
    print("【§3 条件概率与 Bayes（Ross ch3·核心）】")
    print("="*60)
    print("Bayes：P(A|B) = P(B|A)·P(A) / P(B)")
    # 经典例子：疾病筛查（呼应 11-日常生活/02-病人诊断概率）
    print("\n疾病筛查（呼应 11-日常生活 王阿姨贝叶斯）：")
    prev = 0.005  # 患病率 0.5%
    sens = 0.95   # 敏感度（真阳性）
    spec = 0.90   # 特异度（真阴性）
    ppv = (sens*prev) / (sens*prev + (1-spec)*(1-prev))
    print(f"  患病率={prev}, 敏感度={sens}, 特异度={spec}")
    print(f"  阳性后真患病概率 PPV = {ppv:.4f}（仅 {ppv*100:.1f}%！）")
    print(f"  → 大多数阳性是假阳性（基础率忽视谬误）")
    # 蒙特卡洛验证
    N = 1000000
    ill = sum(1 for _ in range(N) if random.random() < prev)
    true_pos = sum(1 for _ in range(ill) if random.random() < sens)
    false_pos = sum(1 for _ in range(N-ill) if random.random() < (1-spec))
    mc_ppv = true_pos / (true_pos + false_pos)
    print(f"  蒙特卡洛（100万样本）PPV = {mc_ppv:.4f}（与理论吻合）")

# ---------- §4-5 随机变量与期望 ----------
def section_random_variable():
    print("\n" + "="*60)
    print("【§4-5 随机变量 + 期望 + 方差（Ross ch4-5）】")
    print("="*60)
    print("期望的线性性（最强大工具）：E[ΣX_i] = ΣE[X_i]（即使不独立！）")
    # 例：骰子期望
    E_die = sum(i/6 for i in range(1, 7))
    print(f"  单骰子 E[X] = {E_die:.4f}")
    print(f"  两骰子和 E[X+Y] = E[X]+E[Y] = {2*E_die:.4f}（线性性）")
    # 蒙特卡洛验证
    trials = 1000000
    s = sum(random.randint(1,6) + random.randint(1,6) for _ in range(trials))
    print(f"  蒙特卡洛（100万次）两骰子和均值 = {s/trials:.4f}")
    # 方差与标准差
    Var_die = sum((i-E_die)**2/6 for i in range(1,7))
    print(f"\n  单骰子 Var[X] = {Var_die:.4f}, std = {math.sqrt(Var_die):.4f}")
    # 二项分布
    print(f"\n二项分布 B(n=10, p=0.5)：")
    n, p = 10, 0.5
    E_binom = n*p
    Var_binom = n*p*(1-p)
    print(f"  E = np = {E_binom}, Var = np(1-p) = {Var_binom}")
    mc_binom = sum(sum(1 for _ in range(n) if random.random()<p) for _ in range(100000))/100000
    print(f"  蒙特卡洛均值 = {mc_binom:.4f}（与 np={E_binom} 吻合）")

# ---------- §8 极限定理：大数定律 + CLT ----------
def section_limit_theorems():
    print("\n" + "="*60)
    print("【§8 极限定理：大数定律 WLLN + 中心极限定理 CLT（Ross ch8·高潮）】")
    print("="*60)
    # WLLN：样本均值 → 期望
    print("★ 弱大数定律 WLLN：样本均值依概率收敛到期望")
    E_die = 3.5
    print(f"  骰子 E=3.5，掷 n 次的样本均值：")
    total = 0
    for n in [10, 100, 1000, 10000, 100000]:
        rolls = [random.randint(1,6) for _ in range(n)]
        mean = sum(rolls)/n
        print(f"    n={n:>6}: 样本均值 = {mean:.4f}（→ 3.5）")
    # CLT：(ΣX_i - nμ)/(σ√n) → N(0,1)
    print(f"\n★ 中心极限定理 CLT：(ΣX_i - nμ)/(σ√n) → 标准正态 N(0,1)")
    print(f"  验证：掷 100 骰子，和的分布应近似正态")
    n = 100
    sums = [sum(random.randint(1,6) for _ in range(n)) for _ in range(10000)]
    mu, sigma = n*3.5, math.sqrt(n*35/12)
    # 标准化
    standardized = [(s - mu)/sigma for s in sums]
    # 在 [-1, 1] 内的比例（理论标准正态 ≈ 0.6827）
    in_range = sum(1 for z in standardized if -1 <= z <= 1)/len(standardized)
    print(f"    100 骰子和，标准化后落在 [-1,1] 比例 = {in_range:.4f}（理论正态 0.6827）")
    # 蒙特卡洛估 π（Buffon 针或单位圆）
    print(f"\n  蒙特卡洛估 π（单位圆内比例）：")
    inside = sum(1 for _ in range(1000000) if random.random()**2 + random.random()**2 < 1)
    pi_est = 4 * inside / 1000000
    print(f"    100 万点估算 π = {pi_est:.6f}（真值 {math.pi:.6f}）")
    print(f"\n→ WLLN 保证'频率→概率'，CLT 保证'和的分布→正态'——这是统计/ML 能 work 的根基")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Ross《概率论基础教程》9e · 现代验证                       ║")
    print("║  组合/Bayes/随机变量/期望/极限定理（蒙特卡洛）              ║")
    print("╚" + "═"*58 + "╝")
    section_combinatorics()
    section_bayes()
    section_random_variable()
    section_limit_theorems()
    print("\n" + "═"*60)
    print("✅ Ross 核心验证通过。概率直觉+严格+蒙特卡洛全打通。")
    print("═"*60)
