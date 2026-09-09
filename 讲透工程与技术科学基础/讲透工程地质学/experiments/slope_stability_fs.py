# -*- coding: utf-8 -*-
"""
边坡稳定安全系数(教学版)
=========================

家族实验 · 讲透工程地质学(GB/T 41030)
主题呼应走廊 C1:无限边坡模型的教学版——干燥时 FS=tan(φ)/tan(β),
加孔隙水压力项后看水怎么改写安全画像;再让参数带上不确定性,
对比「安全系数法」与「可靠度法」两种范式。

模型(无限边坡假定:滑面平行坡面、埋深 z、土层均质):
    抗滑应力 = c' + (γ·z·cos²β − u)·tan(φ')      (有效应力原理 σ'=σ−u)
    滑动应力 = γ·z·sinβ·cosβ
    FS = 抗滑 / 滑动

三个实验:
  [1] 干燥(c'=0, u=0):FS 精确退化为 tan(φ)/tan(β);
      FS 对内摩擦角 φ 严格单调增、对坡度 β 严格单调减;
      β=φ 处 FS=1(自然休止角的语言学)。
  [2] 孔隙水压力:水位平行坡面、饱和度 s∈[0,1],
      滑面处孔压 u = s·γ_w·z·cos²β ⇒ FS 对 s 严格线性下坠;
      全饱和时 FS 缩到干燥值的 1−γ_w/γ ≈ 0.51(近乎减半)——
      「水是滑坡的主犯」的参数化:雨季滑坡机制的机构就是
      入渗抬孔压、有效应力下坠(00 章故事框一的最纯演出)。
      附雨季蒙特卡洛:s~U(0,1) 时季内失稳时间占比 ≈ 1−s_crit。
  [3] 参数不确定性(范式差):φ~N(μ,σ),β 固定,FS<1 ⟺ φ<β。
      A 场地:确定性 FS=1.51(过 1.5 红线)但失效概率≈8.5%(超 5%);
      B 场地:确定性 FS=1.31(不过红线)但失效概率<0.1%(远低于 5%)。
      确定论画像说 A 更安全,概率画像说 A 更危险——
      安全系数法与可靠度法回答的是两个不同的问题。

物理约定:干燥公式取 c'=0 以保持 tan(φ)/tan(β) 的解析清晰;
生产版让 c'、φ' 与地下水位带联合分布(方法同构扩展)。
教学版只让 φ 带不确定性(03 章参数卡的统计身份字段)。

只用标准库 random/math;固定随机种子,结果可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random

GAMMA = 20.0        # 土的天然重度 kN/m³(典型值,通说量级)
GAMMA_W = 9.81      # 水的重度 kN/m³
Z = 5.0             # 假想滑面埋深 m(无限边坡的深度参数)


# ----------------------------------------------------------------模型件

def fs_infinite(phi_deg, beta_deg, c=0.0, gamma=GAMMA, z=Z, ru=0.0):
    """无限边坡安全系数(一般式,ru=孔压比 u/(γ·z))。

    FS = [c' + (γ·z·cos²β − u)·tanφ'] / (γ·z·sinβ·cosβ)
    """
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)
    u = ru * gamma * z
    resisting = c + (gamma * z * math.cos(beta) ** 2 - u) * math.tan(phi)
    driving = gamma * z * math.sin(beta) * math.cos(beta)
    return resisting / driving


def fs_infinite_sat(phi_deg, beta_deg, s, gamma=GAMMA, gamma_w=GAMMA_W,
                    c=0.0, z=Z):
    """饱和度 s∈[0,1] 版:水位平行坡面,滑面孔压 u=s·γ_w·z·cos²β。

    c'=0 时解析式 FS(s) = FS(0)·(1 − s·γ_w/γ):严格线性。
    """
    beta = math.radians(beta_deg)
    u = s * gamma_w * z * math.cos(beta) ** 2
    return fs_infinite(phi_deg, beta_deg, c=c, gamma=gamma, z=z,
                       ru=u / (gamma * z))


def norm_cdf(x):
    """标准正态分布函数 Φ(x)(解析互证用)。"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def mc_pf(mu_deg, sigma_deg, beta_deg, shots):
    """实验 3 蒙特卡洛:φ~N(μ,σ)(拒绝采样 φ>0.5°),返回
    (失效概率 P(FS<1)=P(φ<β), FS 样本均值)。

    干燥 c'=0 下 FS<1 ⟺ tanφ<tanβ ⟺ φ<β(角度均在 (0°,90°))。
    """
    fail = 0
    fs_sum = 0.0
    for _ in range(shots):
        while True:
            phi = random.gauss(mu_deg, sigma_deg)
            if phi > 0.5:
                break
        if phi < beta_deg:
            fail += 1
        fs_sum += math.tan(math.radians(phi)) / \
            math.tan(math.radians(beta_deg))
    return fail / shots, fs_sum / shots


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """干燥无限边坡:退化恒等式 + 双单调 + β=φ 处 FS=1。"""
    section("实验 [1] 干燥无限边坡:FS=tan(φ)/tan(β) 的两支单调")
    # (a) 一般式在 c'=0、u=0 时精确退化为 tan(φ)/tan(β)
    max_dev = 0.0
    for phi, beta in ((30.0, 20.0), (38.0, 25.0), (42.0, 33.0)):
        fs_full = fs_infinite(phi, beta)
        fs_simple = math.tan(math.radians(phi)) / math.tan(math.radians(beta))
        max_dev = max(max_dev, abs(fs_full - fs_simple))
    assert max_dev < 1e-12, "实验[1]:一般式未精确退化为 tan(φ)/tan(β)"
    print(f"(a) 退化恒等式:|FS_full − tan(φ)/tan(β)| 最大 {max_dev:.2e} ✓")

    # (b) FS 对 φ 单调增
    print("(b) 固定 β=25°,扫 φ(20°→45°):")
    print("   φ°      FS      ΔFS")
    prev = None
    mono_phi = True
    for phi in [20.0 + 2.5 * k for k in range(11)]:
        fs = fs_infinite(phi, 25.0)
        d = "" if prev is None else f"{fs - prev:+.4f}"
        if prev is not None and fs <= prev + 1e-9:
            mono_phi = False
        print(f"  {phi:4.1f}   {fs:.4f}   {d}")
        prev = fs
    assert mono_phi, "实验[1]:FS 对内摩擦角不单调增"

    # (c) FS 对 β 单调减
    print("(c) 固定 φ=38°,扫 β(15°→35°):")
    print("   β°      FS      ΔFS")
    prev = None
    mono_beta = True
    for beta in [15.0 + 2.5 * k for k in range(9)]:
        fs = fs_infinite(38.0, beta)
        d = "" if prev is None else f"{fs - prev:+.4f}"
        if prev is not None and fs >= prev - 1e-9:
            mono_beta = False
        print(f"  {beta:4.1f}   {fs:.4f}   {d}")
        prev = fs
    assert mono_beta, "实验[1]:FS 对坡度不单调减"

    # (d) β=φ 处 FS=1:自然休止角
    dev_id = max(abs(fs_infinite(phi, phi) - 1.0) for phi in
                 (22.0, 31.0, 40.0))
    assert dev_id < 1e-9, "实验[1]:β=φ 处 FS≠1"
    print(f"(d) 恒等式:β=φ 处 FS=1(最大偏差 {dev_id:.2e})——"
          "干燥松散土的自然休止角就是它自己的强度角")
    print("断言通过:①FS 对 φ 单调增 ②对 β 单调减 ③β=φ 处 FS=1")


# ----------------------------------------------------------------实验 2

def experiment2():
    """孔隙水压力:FS 对饱和度严格线性;全饱和近乎减半;临界饱和度。"""
    section("实验 [2] 孔隙水压力:水怎么改写 FS(雨季的参数化)")
    phi, beta = 40.0, 26.0
    fs0 = fs_infinite_sat(phi, beta, 0.0)
    fs1 = fs_infinite_sat(phi, beta, 1.0)
    print(f"参数:φ={phi:g}° β={beta:g}° γ={GAMMA:g} γ_w={GAMMA_W:g} kN/m³")

    # (a) 线性:中点值=两端均值(解析式 FS(s)=FS0·(1−s·γ_w/γ))
    fs_mid = fs_infinite_sat(phi, beta, 0.5)
    dev_lin = abs(fs_mid - 0.5 * (fs0 + fs1))
    assert dev_lin < 1e-12, "实验[2]:FS 对饱和度不线性"
    ratio = fs1 / fs0
    dev_ratio = abs(ratio - (1.0 - GAMMA_W / GAMMA))
    assert dev_ratio < 1e-12, "实验[2]:全饱和缩水比≠1−γ_w/γ"
    print(f"(a) FS(0)={fs0:.4f}  FS(0.5)={fs_mid:.4f}  FS(1)={fs1:.4f}")
    print(f"    中点线性偏差 {dev_lin:.2e};全饱和/干燥 = {ratio:.4f}"
          f"(理论 1−γ_w/γ={1 - GAMMA_W / GAMMA:.4f})——水进来,FS 近乎减半")

    # (b) 饱和度扫描表(雨季水位爬升)
    print("(b) 饱和度扫描:")
    print("   s      FS     状态")
    prev = None
    mono_s = True
    for s in [0.1 * k for k in range(11)]:
        fs = fs_infinite_sat(phi, beta, s)
        state = "稳定" if fs >= 1.5 else ("临界" if fs >= 1.0 else "失稳")
        if prev is not None and fs >= prev - 1e-9:
            mono_s = False
        print(f"  {s:.1f}   {fs:.4f}   {state}")
        prev = fs
    assert mono_s, "实验[2]:FS 未随饱和度单调下降"

    # (c) 临界饱和度:公式 vs 二分(线性式的 FS=1 交点)
    s_crit_formula = (1.0 - 1.0 / fs0) / (GAMMA_W / GAMMA)
    lo, hi = 0.0, 1.0
    for _ in range(60):                              # 二分定位 FS=1
        mid = 0.5 * (lo + hi)
        if fs_infinite_sat(phi, beta, mid) >= 1.0:
            lo = mid
        else:
            hi = mid
    s_crit_bi = 0.5 * (lo + hi)
    assert abs(fs_infinite_sat(phi, beta, s_crit_formula) - 1.0) < 1e-9, \
        "实验[2]:公式临界饱和度处 FS≠1"
    assert abs(s_crit_formula - s_crit_bi) < 1e-6, "实验[2]:二分与公式不合"
    print(f"(c) 临界饱和度 s_crit = {s_crit_formula:.4f}(公式与二分一致):"
          "该坡干燥时 FS="
          f"{fs0:.2f},但雨季孔压只需爬到 {s_crit_formula * 100:.0f}% "
          "饱和就到失稳线——缓坡厚土的雨季机关")

    # (d) 缓坡对照:临界饱和度可以大于 1(该机制下单靠静水永不失稳)
    phi2, beta2 = 40.0, 20.0
    fs0b = fs_infinite_sat(phi2, beta2, 0.0)
    s_crit2 = (1.0 - 1.0 / fs0b) / (GAMMA_W / GAMMA)
    print(f"(d) 对照 φ={phi2:g}°、β={beta2:g}°:FS(0)={fs0b:.3f},"
          f"s_crit={s_crit2:.3f} > 1——"
          "此机制下全饱和也不失稳(别的机制另说,见 00 章假设三)")
    assert s_crit2 > 1.0

    # (e) 雨季蒙特卡洛:饱和态 s~U(0,1),季内失稳占比 ≈ 1−s_crit
    shots = 100000
    fail = 0
    for _ in range(shots):
        if fs_infinite_sat(phi, beta, random.random()) < 1.0:
            fail += 1
    frac = fail / shots
    expect = 1.0 - s_crit_formula
    print(f"(e) 雨季 MC({shots} 采样,s~U(0,1)):失稳占比 "
          f"{frac:.4f}(期望 1−s_crit={expect:.4f})")
    assert abs(frac - expect) < 0.01, "实验[2]:雨季占比偏离期望"
    print("断言通过:①FS 对饱和度严格线性 ②单调下坠、全饱和≈减半 "
          "③临界饱和度公式=二分 ④雨季占比与 1−s_crit 一致——"
          "水是滑坡的主犯:孔压每涨一分,FS 按同一斜率掉一分")


# ----------------------------------------------------------------实验 3

def experiment3():
    """参数不确定性:确定性 FS 与失效概率给出的安全画像可以相反。"""
    section("实验 [3] 范式差:FS>1.5 与 Pf<5% 给出不同的安全画像")
    beta = 30.0
    cases = {"A": (41.0, 8.0), "B": (37.0, 2.0)}
    shots = 200000
    print(f"β={beta:g}°,干燥 c'=0;φ~N(μ,σ);每场 {shots} 发蒙特卡洛\n")
    print(f"  场地  μ_φ°  σ_φ°   FS_det   Pf(解析)   Pf(MC)    MC均值FS")
    res = {}
    for name, (mu, sigma) in cases.items():
        fs_det = math.tan(math.radians(mu)) / math.tan(math.radians(beta))
        pf_an = norm_cdf((beta - mu) / sigma)       # Pf=P(φ<β) 的解析值
        pf_mc, fs_mean = mc_pf(mu, sigma, beta, shots)
        res[name] = dict(fs_det=fs_det, pf_an=pf_an, pf_mc=pf_mc,
                         fs_mean=fs_mean)
        print(f"   {name}   {mu:4.1f}  {sigma:4.1f}   {fs_det:.4f}"
              f"   {pf_an:.4f}    {pf_mc:.4f}    {fs_mean:.4f}")
        assert abs(pf_mc - pf_an) < 0.005, \
            f"实验[3]:场地{name} MC 失效概率偏离解析值"
    # MC 均值 FS > 确定性 FS(Jensen:tan 凸,平均参数≠参数平均)
    assert res["A"]["fs_mean"] > res["A"]["fs_det"] + 0.01, \
        "实验[3]:凸性放大(平均FS应高于参数平均的FS)"
    print("\n  · MC 平均 FS 高于确定性 FS(tan 的凸性:平均参数的安全"
          "系数≠安全系数的平均)——确定性画像连均值都偏乐观")

    A, B = res["A"], res["B"]
    print(f"\n  确定论画像:FS(A)={A['fs_det']:.2f} > FS(B)={B['fs_det']:.2f}"
          f" → A 更安全,且 A 过 1.5 红线")
    print(f"  概率画像:  Pf(A)={A['pf_mc']:.3f} > Pf(B)={B['pf_mc']:.5f}"
          f" → A 更危险,且 A 超 5% 红线")
    assert A["fs_det"] > 1.5 and A["pf_mc"] > 0.05, \
        "实验[3]:A 场地应『过FS红线、超Pf红线』"
    assert B["fs_det"] < 1.5 and B["pf_mc"] < 0.05, \
        "实验[3]:B 场地应『不过FS红线、远低于Pf红线』"
    assert A["fs_det"] > B["fs_det"] and A["pf_mc"] > B["pf_mc"], \
        "实验[3]:两种画像的排序应相反"
    print("断言通过:A 过 FS=1.5 却超 Pf=5%;B 不过 FS 红线却远低于 "
          "Pf 红线——安全系数答『平均而言抗滑力是滑动力几倍』,"
          "可靠度答『按参数散布失效多大概率』;两个问题都合法,"
          "只听一个的回答做决策,是在赌(00 章方法论之争的定量版)")


# ----------------------------------------------------------------主控

def main():
    print("边坡稳定安全系数(教学版)——讲透工程地质学家族实验")
    print("无限边坡模型 FS=tan(φ)/tan(β)+孔隙水压力项;纯标准库"
          "(random/math);固定种子,可复现")
    random.seed(20260907)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①干燥 FS 双单调+β=φ 恒等式 ②孔压线性压低 FS"
          "(全饱和≈减半,水是主犯)③FS>1.5 与 Pf<5% 的范式差")
    print("=" * 64)


if __name__ == "__main__":
    main()
