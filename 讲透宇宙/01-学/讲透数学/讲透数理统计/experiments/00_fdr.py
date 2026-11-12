# -*- coding: utf-8 -*-
"""多重检验的 p 值动物园 + BH-FDR 控制的实测验证。

00 章 §六(反直觉:假显著成群出现)与 01 章 §二(战线4)/04 章走廊 3 配套实验。纯标准库。

设定: m 个假设,其中 m1 个真有效应(备择为真),m0=m-m1 个原假设为真。
     对每个假设做 z 检验(单观测,效应量 effect),得到双侧 p 值。
对照: 不校正      —— 报告所有 p<0.05,统计假发现比例 (false discovery proportion)
     BH-FDR(q=.05) —— Benjamini-Hochberg 阈值,验证 FDR 长程 ≤ q
场景: 独立检验 vs 正相关检验(共同因子),看 FDR 的稳健性差异。

跑法: python experiments/00_fdr.py
"""

import math
import random


# ---------- 极简正态 CDF/分位 ----------
def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p):  # 粗初值+二分精修
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------- 造一批 p 值 ----------
def make_pvalues(rng, m, m1, effect, corr):
    """corr=0:各检验独立;corr>0:观测值共享共同因子 Z0,制造正相关。"""
    pvals = []
    z_common = rng.gauss(0.0, 1.0) if corr > 0 else 0.0
    for i in range(m):
        z = math.sqrt(corr) * z_common + math.sqrt(1.0 - corr) * rng.gauss(0.0, 1.0)
        if i < m1:                      # 真效应:均值平移 effect
            z += effect
        p = 2.0 * (1.0 - norm_cdf(abs(z)))   # 双侧 p 值
        pvals.append(p)
    return pvals


# ---------- 判定规则 ----------
def reject_raw(pvals, alpha):
    return [p < alpha for p in pvals]


def reject_bh(pvals, q):
    """BH 程序:最大 k 使 p(k) <= (k/m)*q,拒绝前 k 个最小 p。"""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    k_star = 0
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= (rank / m) * q:
            k_star = rank
    if k_star == 0:
        return [False] * m
    head = set(order[:k_star])
    return [i in head for i in range(m)]


def fdp_fpr(reject, m1):
    """返回 (假发现比例 FDP, 假阳性率 FP/原假设数)。m1 个备择真占据前 m1 个下标。"""
    m = len(reject)
    R = sum(reject)
    if R == 0:
        return 0.0, 0.0                              # 无拒绝:FDP 约定 0
    fd = sum(1 for i in range(m) if reject[i] and i >= m1)   # 拒绝了的原真假设
    return fd / R, fd / max(1, m - m1)


def simulate(label, m, m1, effect, corr, reps, seed=20260906):
    rng = random.Random(seed)
    fdp_raw, fdp_bh, power_bh = [], [], []
    for _ in range(reps):
        pv = make_pvalues(rng, m, m1, effect, corr)
        f1, _ = fdp_fpr(reject_raw(pv, 0.05), m1)
        f2, _ = fdp_fpr(reject_bh(pv, 0.05), m1)
        fdp_raw.append(f1)
        fdp_bh.append(f2)
        rejections = reject_bh(pv, 0.05)
        tp = sum(1 for i in range(m1) if rejections[i])
        power_bh.append(tp / m1)
    mean = lambda xs: sum(xs) / len(xs)
    print(f"[{label}] m={m}, m1={m1}, |corr|={corr}")
    print(f"    不校正   E[FDP] = {mean(fdp_raw):.3f}")
    print(f"    BH q=.05 E[FDP] = {mean(fdp_bh):.3f}  (应 ≤ 0.05)   功效 = {mean(power_bh):.3f}")
    return mean(fdp_raw), mean(fdp_bh)


def main():
    m, m1, eff = 1000, 100, 2.5
    power_single = 1.0 - norm_cdf(1.959964 - eff) + norm_cdf(-1.959964 - eff)

    print("=" * 66)
    print(f"FDR 实验:m={m} 个假设,m1={m1} 个真有效应(effect={eff},"
          f"单次 α=.05 功效≈{power_single:.2f})")
    print("=" * 66)

    r_indep = simulate("独立检验  ", m, m1, eff, corr=0.0, reps=300)
    r_corr = simulate("正相关0.6 ", m, m1, eff, corr=0.6, reps=300)

    # 独立情形的解析 FDR(不校正):m0·α / (m0·α + m1·power)
    m0 = m - m1
    fdr_theory = m0 * 0.05 / (m0 * 0.05 + m1 * power_single)

    print()
    print("读数:")
    print(f"  · 不校正:p<0.05 一刀切,长程假发现比例理论值 = "
          f"m0·α/(m0·α+m1·power) = {fdr_theory:.3f}(模拟 {r_indep[0]:.3f} 吻合)——")
    print(f"    每 10 个「发现」里约 {round(r_indep[0]*10)} 个是假的——")
    print("    这就是复现危机的机器形态(00 章 §六反直觉的实测版)。")
    print("  · BH 后:E[FDP] ≤ 0.05——控制的不再是『至少犯一错』(FWER),")
    print("    而是『发现集里错误的比例』(FDR):组学/A/B 平台的法定出口。")
    print("    代价:阈值收紧到 p≈k/m·q,功效下降(见上表)——保证与功效的经典交换。")
    print("  · 正相关下 BH 依旧稳健(正相关时 FDR 只会更小;负相关才会让 BH 超标)")
    print("    ——工程场景(同源监控/共享流量)多为正相关,幸运。")

    # ---------- 自验证断言 ----------
    assert r_indep[0] > 0.20, "不校正的假发现比例应当显著偏高(反直觉现场)"
    assert r_indep[1] <= 0.05 + 0.02, "BH 在独立 p 值下 FDR 应 ≤ q(蒙特卡洛容差)"
    assert r_corr[1] <= 0.05 + 0.02, "BH 在正相关下应保持 FDR 控制(经典结论)"
    assert abs(fdr_theory - r_indep[0]) < 0.03, "模拟应贴近独立情形的解析 FDR"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
