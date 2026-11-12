# -*- coding: utf-8 -*-
"""
公差叠加与 MMC 修正实验(教学版)
================================

家族实验 · 讲透工程图学(GB/T 41060)
主题呼应走廊 C1:把「公差怎么叠」「RSS 省多少」「MMC 奖励什么」写成可计算的模型。

模型:
  [律1] 最坏情况叠加(worst case / 算术叠加):
        封闭环公差 = Σ 各环公差(全部同向坏到头的保守界)。
        n 环各 ±t → 封闭环最坏 ±n·t:环数翻倍,公差翻倍(线性放大)。
  [律2] 统计叠加(RSS,root sum square / 方和根):
        封闭环公差 = √(Σ tᵢ²)——各环偏差独立随机、互相抵消的统计界。
        n 环各 ±t → ±√n·t;最坏法/RSS 的比值恰为 √n:
        环数越多,两法差距越大(8 环 2.83 vs 4 环 2.00)。
  [律3] MMC 修正与装配成功率(虚拟边界+蒙特卡洛):
        孔 ⌀10.0~10.5(MMC=10.0,孔的最小实体是 MMC),位置度公差
        在 MMC 时 ⌀0.2。实际尺寸偏离 MMC 多少,bonus 就线性补入多少:
        有效公差 = 尺寸公差 + 几何公差 + bonus(=实际尺寸−MMC)。
        代数恒等式:位置误差 e ≤ 0.2+(D−10.0) ⟺ D−e ≥ 9.8=MMC−公差
        ——MMC 合格 ⟺ 过 ⌀9.8 功能量规(虚拟条件),合格即保证装配。
        刚性 RFS 判定(e≤0.2,不奖励偏离)是它的严格子集。

三个实验(全部断言自验证):
  [1] 最坏法线性:n=4 各 ±0.05 → ±0.20;n=8 → ±0.40;
      逐 n 扫描确认 worst=n·t,环数翻倍公差翻倍。
  [2] RSS:n=8 → √8×0.05≈0.1414;n=4 → 0.100;
      比值 worst/RSS:4 环 2.00、8 环 2.83,恰为 √n(差距随环数拉大)。
  [3] MMC bonus 线性 + 蒙特卡洛 10 万件:同一批零件,
      MMC 修正判定的通过率显著高于刚性 RFS 判定(把 bonus 换算成
      更多零件落入接受域);MMC 通过 ⟺ 过 ⌀9.8 虚拟边界量规。

只用标准库 math/random;固定随机种子,可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random


# ----------------------------------------------------------------模型件

def worst_case(tols):
    """最坏情况(算术)叠加:封闭环公差 = 各环公差直接相加。"""
    return sum(tols)


def rss(tols):
    """统计(RSS/方和根)叠加:封闭环公差 = √(Σ tᵢ²)。"""
    return math.sqrt(sum(t * t for t in tols))


def bonus_mmc(actual_size, mmc_size):
    """孔的 MMC bonus:实际尺寸偏离 MMC(变大)多少,补多少。

    孔的 MMC = 最小极限尺寸(实体最多);偏离方向是变大,bonus≥0。
    """
    return max(0.0, actual_size - mmc_size)


def effective_tol(geo_tol, actual_size, mmc_size):
    """MMC 修正下的有效几何公差 = 几何公差 + bonus(线性补入)。"""
    return geo_tol + bonus_mmc(actual_size, mmc_size)


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """最坏情况叠加:线性放大,环数翻倍公差翻倍。"""
    section("实验 [1] 最坏情况叠加:封闭环最坏公差 = 环数 × 单环公差")

    t = 0.05                                       # 单环公差 ±0.05
    stack4 = [t] * 4
    stack8 = [t] * 8
    w4, w8 = worst_case(stack4), worst_case(stack8)
    print(f"(a) 装配尺寸链 4 环,各 ±{t} → 封闭环最坏 ±{w4:.2f}")
    print(f"    装配尺寸链 8 环,各 ±{t} → 封闭环最坏 ±{w8:.2f}")
    assert math.isclose(w4, 0.20, abs_tol=1e-9), "实验[1]:4 环最坏公差应为 ±0.20"
    assert math.isclose(w8, 0.40, abs_tol=1e-9), "实验[1]:8 环最坏公差应为 ±0.40"
    assert math.isclose(w8, 2.0 * w4, abs_tol=1e-9), \
        "实验[1]:环数翻倍,最坏公差应翻倍(线性放大)"

    # (b) 逐 n 扫描:worst(n) = n·t 严格成立(线性,无曲率)
    print("(b) 逐 n 扫描:最坏法公差 = n × 单环公差(线性)")
    print("   n   worst(±)   n·t")
    for n in range(1, 11):
        w = worst_case([t] * n)
        assert math.isclose(w, n * t, abs_tol=1e-9), \
            f"实验[1]:n={n} 的最坏公差应恰为 n·t"
        print(f"  {n:2d}   {w:.3f}    {n * t:.3f}")
    print("断言通过:①4 环 ±0.20、8 环 ±0.40 ②worst=n·t 逐点成立,环数"
          "翻倍公差翻倍——**最坏法把每个环都设想成同向坏到头,代价随环数线性放大**"
          "(图纸越复杂,最坏法越不可忍受)")


# ----------------------------------------------------------------实验 2

def experiment2():
    """RSS 统计叠加:√(Σtᵢ²) 与最坏法的 √n 倍差距。"""
    section("实验 [2] RSS 平方和开根:与最坏法的差距 = √n")

    t = 0.05
    r4, r8 = rss([t] * 4), rss([t] * 8)
    print(f"(a) 4 环 RSS = √(4×{t}²) = {r4:.4f} ≈ ±0.100")
    print(f"    8 环 RSS = √8×{t} = {r8:.4f} ≈ ±0.141")
    assert math.isclose(r4, 0.100, abs_tol=1e-9), "实验[2]:4 环 RSS 应为 ±0.100"
    assert math.isclose(r8, 0.1414, abs_tol=1e-4), \
        "实验[2]:8 环 RSS 应为 √8×0.05≈0.1414"
    assert math.isclose(r8, math.sqrt(8) * t, abs_tol=1e-12), \
        "实验[2]:RSS=√(Σtᵢ²) 的定义式应逐点成立"

    # (b) 比值表:worst/RSS = √n,环数越多差距越大
    w4, w8 = worst_case([t] * 4), worst_case([t] * 8)
    ratio4, ratio8 = w4 / r4, w8 / r8
    print("(b) 最坏法/RSS 比值(环数越多,两法差距越大):")
    print("   n   worst(±)   RSS(±)   比值   √n")
    for n in (2, 4, 6, 8, 10):
        w, r = worst_case([t] * n), rss([t] * n)
        print(f"  {n:2d}   {w:.3f}     {r:.4f}   {w / r:.3f}  {math.sqrt(n):.3f}")
        assert math.isclose(w / r, math.sqrt(n), abs_tol=1e-9), \
            f"实验[2]:n={n} 的 worst/RSS 比值应恰为 √n"
    print(f"    断言:4 环比值 {ratio4:.2f}(=√4)、8 环比值 {ratio8:.2f}"
          f"(=√8)——比值=√n,环数翻倍差距再乘 √2")
    assert ratio8 > ratio4, "实验[2]:环数越多,最坏法与 RSS 差距应越大"
    assert math.isclose(ratio8 / ratio4, math.sqrt(2), abs_tol=1e-9)

    # (c) 教学读数:8 环链上 RSS 把公差从 0.40 收回 0.14
    print(f"(c) 教学读数:8 环链最坏法要 ±0.40 才稳,RSS 只要 ±{r8:.4f}"
          "——前提是各环**独立随机**、无系统性同向偏差;"
          "工艺有系统性漂移(刀具磨损/夹具偏置)时独立性假设失效,"
          "RSS 会系统性乐观(工程上常折中取系数或混用两法)")
    print("断言通过:①RSS=√(Σtᵢ²) ②8 环 0.141 vs 最坏 0.40,比值 √8≈2.83;"
          "4 环 0.100 vs 0.20,比值 2.00——**统计叠加买的是「独立偏差互相抵消」,"
          "环数越多这笔折扣越大,但折扣兑付的前提是独立性**")


# ----------------------------------------------------------------实验 3

def experiment3():
    """MMC bonus 与装配成功率:线性 bonus + 蒙特卡洛对比 RFS。"""
    section("实验 [3] MMC bonus 与装配成功率(虚拟边界 9.8 + 蒙特卡洛)")

    # 零件定义:孔 ⌀10.0~10.5,位置度 ⌀0.2 @ MMC(基准体系略,取径向合成)
    mmc = 10.0                                     # 孔的 MMC=最小尺寸
    geo_tol = 0.2                                  # MMC 时的位置度公差(直径)
    vc = mmc - geo_tol                             # 虚拟条件(功能量规销径)
    print(f"(a) 零件:孔 ⌀{mmc}~⌀{mmc + 0.5},位置度 ⌀{geo_tol} @MMC"
          f"→ 虚拟条件 VC={vc:.1f}(⌀{vc:.1f} 量规销)")

    # bonus 线性:偏离 MMC 多少补多少(斜率 1)
    print("(b) bonus 随实际尺寸偏离 MMC 线性增长(有效公差=0.2+bonus):")
    print("   实际尺寸D   偏离MMC   bonus   有效公差")
    effs = []
    for d in (10.0, 10.1, 10.25, 10.4, 10.5):
        b = bonus_mmc(d, mmc)
        eff = effective_tol(geo_tol, d, mmc)
        effs.append((d, b, eff))
        print(f"   {d:.2f}      {d - mmc:.2f}     {b:.2f}     {eff:.2f}")
        assert math.isclose(b, d - mmc, abs_tol=1e-12), \
            "实验[3]:bonus 应等于偏离 MMC 的量(线性,斜率 1)"
    for (d1, _, e1), (d2, _, e2) in zip(effs, effs[1:]):
        assert math.isclose(e2 - e1, d2 - d1, abs_tol=1e-12), \
            "实验[3]:有效公差应随实际尺寸线性增长(差分斜率=1)"
    print("    断言:bonus=D−MMC 逐点成立,有效公差对 D 的差分斜率=1"
          "——**孔越做越大(实体越少),允许的位置误差越多,装配照样成**")

    # (c) 代数恒等式:MMC 判定 ⟺ 过 ⌀9.8 功能量规
    print(f"(c) 恒等式:位置误差 e ≤ {geo_tol}+(D−{mmc}) ⟺ D−e ≥ {vc:.1f}"
          "——MMC 合格就是「过 ⌀9.8 销」,合格即保证与 9.8 轴装配")

    # (d) 蒙特卡洛 10 万件:MMC 修正判定 vs 刚性 RFS 判定
    n_parts = 100000
    e_max = 0.6                                    # 位置误差(直径量)均匀 0~0.6
    rfs_pass = 0
    mmc_pass = 0
    gage_pass = 0
    subset_violation = 0
    gage_mismatch = 0
    for _ in range(n_parts):
        d = mmc + 0.5 * random.random()            # 实际孔径 ~ U(10.0, 10.5)
        e = e_max * random.random()                # 实际位置误差 ~ U(0, 0.6)
        ok_rfs = e <= geo_tol                      # 刚性判定:公差不随尺寸变
        ok_mmc = e <= effective_tol(geo_tol, d, mmc)
        ok_gage = (d - e) >= vc                    # 功能量规:⌀9.8 销能插入
        rfs_pass += ok_rfs
        mmc_pass += ok_mmc
        gage_pass += ok_gage
        if ok_rfs and not ok_mmc:
            subset_violation += 1                  # RFS 通过而 MMC 不通过(不可能)
        if ok_mmc != ok_gage:
            gage_mismatch += 1                     # 判定式与量规式不一致(不可能)
    rate_rfs, rate_mmc = rfs_pass / n_parts, mmc_pass / n_parts
    diff = rate_mmc - rate_rfs
    print(f"(d) 蒙特卡洛 {n_parts} 件(D~U[10.0,10.5],e~U[0,0.6]):")
    print(f"    刚性 RFS 判定通过率:{rate_rfs:.4f}({rfs_pass} 件)")
    print(f"    MMC  修正判定通过率:{rate_mmc:.4f}({mmc_pass} 件)")
    print(f"    差值(MMC−RFS):{diff:.4f}——同一批零件,bonus 把 "
          f"{int(diff * n_parts)} 件从「报废/返工」救回「合格」")
    assert diff > 0, "实验[3]:MMC 判定通过率必须高于刚性 RFS"
    assert diff > 0.3, "实验[3]:差值应显著(理论差≈0.40)"
    assert subset_violation == 0, "实验[3]:RFS 合格集应是 MMC 合格集的子集"
    assert gage_mismatch == 0 and gage_pass == mmc_pass, \
        "实验[3]:MMC 判定应与 ⌀9.8 虚拟边界量规逐件一致"
    print(f"    核验:RFS 通过而 MMC 拒收的件数={subset_violation}(子集关系);"
          f"MMC 判定与量规判定不一致的件数={gage_mismatch}(恒等式)")
    print("断言通过:①bonus=D−MMC 线性(斜率 1)②MMC 通过率显著高于 RFS"
          f"({rate_mmc:.4f} vs {rate_rfs:.4f},差 {diff:.4f}>0)"
          "③MMC 合格 ⟺ 过 ⌀9.8 功能量规——**MMC 的语义是功能性的:"
          "奖励的不是「误差大」,是「实体少而仍有间隙」**;"
          "RFS 是量具不变的功能等价,代价是这 "
          f"{int(diff * n_parts)} 件好零件")


# ----------------------------------------------------------------主控

def main():
    print("公差叠加与 MMC 修正实验(教学版)——讲透工程图学家族实验")
    print("最坏法线性叠加 + RSS 统计叠加 + MMC bonus 虚拟边界;纯标准库"
          "(math/random);固定种子,可复现")
    random.seed(20260908)
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①最坏法公差=环数×单环公差,环数翻倍公差翻倍"
          "(4 环 ±0.20/8 环 ±0.40,线性)"
          "②RSS=√(Σtᵢ²)(8 环 0.141 vs 最坏 0.40;比值 worst/RSS=√n,"
          "8 环 2.83 vs 4 环 2.00,环数越多差距越大)"
          "③MMC bonus 随偏离 MMC 线性补入,有效公差=尺寸+几何+bonus;"
          "同批零件 MMC 判定通过率显著高于刚性 RFS,且 MMC 合格⟺过 ⌀9.8 "
          "虚拟边界量规")
    print("=" * 64)


if __name__ == "__main__":
    main()
