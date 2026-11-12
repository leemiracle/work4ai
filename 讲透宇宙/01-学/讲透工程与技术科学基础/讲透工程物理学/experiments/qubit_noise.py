# -*- coding: utf-8 -*-
"""
量子比特的噪声工程(教学版)
============================

家族实验 · 讲透工程物理学(GB/T 41025)
主题呼应量子工程支:单量子比特在「退相干(t1)」与「比特翻转(t2)」
两类噪声通道参数化下演化;教学版 3 比特重复码多数表决演示纠错阈值。

三个实验(全部蒙特卡洛逐发采样,与解析式互证):
  [1] 单比特记忆:保真度随时间精确指数衰减
      F(t) = (1 + exp(-t/t_eff)) / 2,合成率 1/t_eff = 1/t1 + 1/t2
      (两独立通道的指数相乘律);误差率对退相干时间单调。
  [2] 重复码纠错阈值(纯比特翻转噪声):物理误差率低于阈值时,
      3 比特多数表决+级联把逻辑误差逐级压低;高于阈值反而逐级放大。
      纯比特翻转噪声下阈值解析精确 = 0.5。
  [3] 阈值随噪声类型偏移:混合噪声(比特/相位偏置 b)下,
      未保护通道直达逻辑层,按总误差率测得的阈值移动——
      纠错阈值不是材料常数,是「噪声谱 × 码」的联合属性,
      工程余量必须按实测噪声谱重新标定。

命名说明(教学版约定):本文件 t1=退相干通道(相位型错误),
t2=比特翻转通道;标准文献中 T1/T2 另有语义(T1=能量弛豫、
T2=相位相干,见家族 02 章术语对译表的翻译陷阱行)。

物理设定(实验 1):记忆态取 |+i>=(|0>+i|1>)/√2(Y 本征态):
相位型错误 Z|+i>=|-i> 直接翻转 Y 基测量结果,比特翻转
X|+i>∝|-i> 同样翻转结果;两错误同时发生则复原(宇称)。
故每发结果是否翻转 = 两通道错误数的奇偶(异或)。
实验 3 的未保护通道按「逻辑块一次直达」抽象(真实量子码中
逐比特中招另有放大,超出教学版,见 00 章/04 章正文)。

只用标准库 random/math;固定随机种子,结果可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random


# ----------------------------------------------------------------公用件

def channel_flip_prob(t, t_noise):
    """单个噪声通道在时刻 t 翻转测量结果的概率。

    约定 p(t) = (1 - exp(-t/t_noise)) / 2:小 t 时约 t/(2*t_noise),
    相干性以 exp(-t/t_noise) 衰减,翻转概率为其中的一半。
    """
    return (1.0 - math.exp(-t / t_noise)) / 2.0


def mc_xor_flip_prob(p1, p2, shots):
    """蒙特卡洛:两独立通道按异或合成结果翻转概率。

    每发:通道 1 翻转(概率 p1)与通道 2 翻转(概率 p2)取异或;
    返回「结果被翻转」的频率(解析值 = p1 + p2 - 2*p1*p2)。
    """
    wrong = 0
    for _ in range(shots):
        if (random.random() < p1) != (random.random() < p2):
            wrong += 1
    return wrong / shots


def majority_error_mc(p, shots, level):
    """重复码级联的蒙特卡洛逻辑误差率(纯比特翻转噪声)。

    level=0:单比特(误差率即 p);level=1:3 比特多数表决;
    level=2:9 比特二级级联(每 3 比特先表决,再对外层 3 比特表决)。
    解析递推:P_{k+1} = 3*P_k^2 - 2*P_k^3(表决在 ≥2 比特翻转时失败)。
    """
    wrong = 0
    for _ in range(shots):
        # 逐比特翻转旗标:每比特独立以概率 p 翻转
        if level == 0:
            fail = random.random() < p
        elif level == 1:
            bits = [random.random() < p for _ in range(3)]
            fail = sum(bits) >= 2
        else:  # level == 2:9 比特 → 三个子块各表决 → 外层表决
            inner = []
            for _blk in range(3):
                bits = [random.random() < p for _ in range(3)]
                inner.append(sum(bits) >= 2)
            fail = sum(inner) >= 2
        if fail:
            wrong += 1
    return wrong / shots


def repetition_logical_prob(p):
    """纯比特翻转下 3 比特重复码的逻辑误差率(解析)。"""
    return 3.0 * p * p - 2.0 * p * p * p


def mc_block_logical_error(p, b, shots):
    """实验 3:混合噪声下「单比特」与「重复码块」的结果翻转率。

    噪声:总误差率 p,其中占比 b 为比特翻转(受码保护),
    占比 1-b 为相位型(未保护,教学版按逻辑块一次直达抽象)。
    单比特:两通道异或 → 翻转率 = XOR(b*p, (1-b)*p)。
    编码块:受保护通道经 3 比特多数表决(3q²-2q³,q=b*p),
    未保护通道直达逻辑层,再与表决失败异或。
    返回 (uncoded, logical)。
    """
    pb, pd = b * p, (1.0 - b) * p
    vote_fail = repetition_logical_prob(pb)      # 受保护通道的表决失败率
    wrong_u = wrong_c = 0
    for _ in range(shots):
        # 未编码单比特:两通道异或
        if (random.random() < pb) != (random.random() < pd):
            wrong_u += 1
        # 编码块:表决失败 xor 未保护直达
        vote = sum(random.random() < pb for _ in range(3)) >= 2
        passthru = random.random() < pd
        if vote != passthru:
            wrong_c += 1
    return wrong_u / shots, wrong_c / shots


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """单比特记忆:保真度指数衰减 + 对退相干时间单调。"""
    section("实验 [1] 单量子比特记忆:保真度随时间指数衰减")
    t1, t2 = 40.0, 25.0                      # 退相干/比特翻转时间(任意单位)
    t_eff_inv = 1.0 / t1 + 1.0 / t2          # 合成率:独立通道指数相乘
    shots = 30000
    print(f"参数:t1={t1:g}(退相干) t2={t2:g}(比特翻转) 每点 {shots} 发")
    print(f"解析合成率 1/t_eff = 1/t1 + 1/t2 = {t_eff_inv:.6f}\n")
    print("  t      F(仿真)   F(解析)   |差|")
    ts = [5.0 * k for k in range(1, 9)]
    max_dev = 0.0
    prev = 1.0
    mono_time = True
    for t in ts:
        p1 = channel_flip_prob(t, t1)
        p2 = channel_flip_prob(t, t2)
        err_mc = mc_xor_flip_prob(p1, p2, shots)
        f_mc = 1.0 - err_mc
        f_an = (1.0 + math.exp(-t * t_eff_inv)) / 2.0
        dev = abs(f_mc - f_an)
        max_dev = max(max_dev, dev)
        if f_mc > prev + 1e-9:               # 保真度必须随时间不增
            mono_time = False
        prev = min(prev, f_mc)
        print(f"{t:5.1f}   {f_mc:.4f}    {f_an:.4f}   {dev:.4f}")

    # 指数律最小二乘拟合:ln(F*2-1) 对 t 的斜率 ≈ -1/t_eff
    ys, xs = [], []
    for t in ts:
        p1 = channel_flip_prob(t, t1)
        p2 = channel_flip_prob(t, t2)
        err = mc_xor_flip_prob(p1, p2, shots)
        v = max(2.0 * (1.0 - err) - 1.0, 1e-6)
        ys.append(math.log(v))
        xs.append(t)
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / \
        sum((x - mx) ** 2 for x in xs)

    # 误差率对退相干时间单调:t1 越短,同一时刻误差越大(t2 固定)
    t_check, shots_m = 20.0, 20000
    err_by_t1 = []
    for t1_try in (50.0, 30.0, 15.0):
        e = mc_xor_flip_prob(channel_flip_prob(t_check, t1_try),
                             channel_flip_prob(t_check, t2), shots_m)
        err_by_t1.append(e)
        print(f"  t1={t1_try:4.0f} → t={t_check:g} 时误差率 {e:.4f}")
    mono_t1 = err_by_t1[0] < err_by_t1[1] < err_by_t1[2]

    print(f"\n拟合衰减率 = {-slope:.6f}(解析 1/t_eff = {t_eff_inv:.6f},"
          f"偏差 {abs(-slope - t_eff_inv) / t_eff_inv * 100:.1f}%)")

    assert max_dev < 0.012, "实验[1]:仿真保真度偏离解析式超容差"
    assert mono_time, "实验[1]:保真度未随时间单调衰减"
    assert abs(-slope - t_eff_inv) / t_eff_inv < 0.05, \
        "实验[1]:衰减率拟合偏离合成率 5% 以上"
    assert mono_t1, "实验[1]:误差率对退相干时间不单调"
    print("断言通过:①保真度精确指数衰减(合成率互证<5%)"
          " ②误差率对退相干时间单调")


# ----------------------------------------------------------------实验 2

def experiment2():
    """纯比特翻转:低于阈值逐级压低,高于阈值逐级放大;阈值=0.5。"""
    section("实验 [2] 重复码纠错阈值(纯比特翻转噪声)")
    shots = 40000
    for p in (0.10, 0.60):
        p0 = p
        l1_mc = majority_error_mc(p, shots, 1)
        l2_mc = majority_error_mc(p, shots, 2)
        l1_an = repetition_logical_prob(p)
        l2_an = repetition_logical_prob(l1_an)
        print(f"物理误差率 p={p:.2f}")
        print(f"  单比特        {p0:.4f}")
        print(f"  3 比特码      {l1_mc:.4f}(解析 {l1_an:.4f})")
        print(f"  级联二级      {l2_mc:.4f}(解析 {l2_an:.4f})")
        if p < 0.5:
            assert l1_mc < p0 and l2_mc < l1_mc, \
                "实验[2]:低于阈值应逐级压低"
            print("  → 低于阈值:冗余逐级压低误差(0.1→0.028→0.0023 量级)")
        else:
            assert l1_mc > p0 and l2_mc > l1_mc, \
                "实验[2]:高于阈值应逐级放大"
            print("  → 高于阈值:冗余逐级放大误差(0.6→0.648→0.715 量级)")
        assert abs(l1_mc - l1_an) < 0.012 and abs(l2_mc - l2_an) < 0.012, \
            "实验[2]:蒙特卡洛偏离解析递推超容差"

    # 阈值定位:解析交叉点恰为 0.5(3p-2p²=1 的根);蒙特卡洛括住它
    shots_b = 50000
    lo, hi = 0.45, 0.55
    u_lo, c_lo = mc_block_logical_error(lo, 1.0, shots_b)
    u_hi, c_hi = mc_block_logical_error(hi, 1.0, shots_b)
    print(f"\n阈值括区:p={lo}(码 {c_lo:.4f} vs 裸 {u_lo:.4f},码优)"
          f" p={hi}(码 {c_hi:.4f} vs 裸 {u_hi:.4f},码劣)")
    assert c_lo < u_lo and c_hi > u_hi, "实验[2]:阈值未落在 [0.45,0.55]"
    print("断言通过:阈值 ∈ [0.45, 0.55](解析精确 0.5)——"
          "低于压低/高于放大的分界存在")


# ----------------------------------------------------------------实验 3

def experiment3():
    """混合噪声:阈值随噪声类型偏移,工程余量要按噪声谱重标。"""
    section("实验 [3] 阈值随噪声类型偏移(偏置噪声)")
    shots = 60000
    p_probe = 0.10
    print(f"(a) 同一总误差率 p={p_probe},看码的净收益随偏置缩水:")
    ratios = {}
    for b, tag in ((1.0, "纯比特翻转"), (0.6, "偏置 0.6(六成比特/四成相位)")):
        u, c = mc_block_logical_error(p_probe, b, shots)
        ratios[b] = c / u
        print(f"  b={b:.1f} {tag}:裸 {u:.4f} → 码 {c:.4f}"
              f"(压至 {c / u * 100:.0f}%)")
    assert ratios[0.6] > ratios[1.0], \
        "实验[3]:未保护通道混入后,同 p 下净收益应缩水"

    # (b) 阈值括区:纯比特翻转阈值=0.5;偏置 0.6 时解析阈值=0.5/b=5/6≈0.833
    print("(b) 按总误差率测阈值(解析:阈值 = 0.5/b,偏置 0.6 → 5/6≈0.833):")
    pts_b1 = (0.45, 0.55)
    pts_b06 = (0.70, 0.95)
    u_lo, c_lo = mc_block_logical_error(pts_b1[0], 1.0, shots)
    u_hi, c_hi = mc_block_logical_error(pts_b1[1], 1.0, shots)
    assert c_lo < u_lo and c_hi > u_hi, "实验[3]:b=1 阈值括区失败"
    print(f"  b=1.0:码在 p={pts_b1[0]} 占优、p={pts_b1[1]} 转劣"
          f" → 阈值∈{pts_b1}(≈0.5)")
    u_lo6, c_lo6 = mc_block_logical_error(pts_b06[0], 0.6, 100000)
    u_hi6, c_hi6 = mc_block_logical_error(pts_b06[1], 0.6, 100000)
    assert c_lo6 < u_lo6 and c_hi6 > u_hi6, "实验[3]:b=0.6 阈值括区失败"
    print(f"  b=0.6:码在 p={pts_b06[0]} 占优、p={pts_b06[1]} 转劣"
          f" → 阈值∈{pts_b06}(解析 5/6≈0.833)")
    # 阈值确实移动了(括区整体上移),且方向向上
    assert pts_b06[0] > pts_b1[1], "实验[3]:阈值未随噪声偏置上移"
    print("断言通过:阈值随噪声类型偏移(0.5 → ≈0.83)——阈值是"
          "「噪声谱×码」的联合属性;偏置下按总误差率看的余量变大,"
          "但同 p 的净收益缩水:工程余量必须按实测噪声谱重新标定")


# ----------------------------------------------------------------主控

def main():
    print("量子比特的噪声工程(教学版)——讲透工程物理学家族实验")
    print("纯标准库(random/math);固定种子,可复现")
    random.seed(20260907)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①指数衰减+单调 ②纠错阈值(低于压低/高于放大)"
          " ③阈值随噪声类型偏移")
    print("=" * 64)


if __name__ == "__main__":
    main()
