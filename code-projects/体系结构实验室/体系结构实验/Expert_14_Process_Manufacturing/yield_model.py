#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞腾 D3000M 良率与 good die 数推测模型
Expert_14 工艺/制造工程师视角 — 可运行 artifact

三种业界标准良率模型：
  - Poisson      : Y = exp(-D0 * A)            (随机独立缺陷，保守上界)
  - Murphy       : Y = ((1-exp(-D0*A))/(D0*A))^2  (缺陷密度三角形分布，业界最常用)
  - Bose-Einstein: Y = 1 / (1 + D0*A)          (缺陷成团/clustered，乐观)

单位：D0 = defects/cm^2, A = cm^2
die 面积换算：1 mm^2 = 0.01 cm^2

用法：python3 yield_model.py
"""
import math

# ----------------------------------------------------------------------
# 晶圆几何：300mm (12寸) 标准晶圆
# ----------------------------------------------------------------------
WAFER_DIAMETER_MM = 300.0
WAFER_RADIUS_MM = WAFER_DIAMETER_MM / 2.0


def gross_die_per_wafer(die_area_mm2, edge_exclusion_mm=3.0):
    """粗算每片晶圆的完整 die 数（含边缘损失近似）。

    经验公式 gross ≈ floor(pi * (R - die_side/2 - edge)^2 / die_area)
    再扣除 ~5% 边缘 partial die。本函数用业界常用近似。
    """
    import math as m
    die_side = math.sqrt(die_area_mm2)  # 假设方形 die
    usable_r = WAFER_RADIUS_MM - edge_exclusion_mm
    # 圆内可放 die 数近似
    gross = m.pi * (usable_r - die_side / 2.0) ** 2 / die_area_mm2
    # 扣除边缘 5% 部分切割 die
    return int(gross * 0.95)


def yield_poisson(d0, a_cm2):
    return math.exp(-d0 * a_cm2)


def yield_murphy(d0, a_cm2):
    x = d0 * a_cm2
    if x == 0:
        return 1.0
    return ((1.0 - math.exp(-x)) / x) ** 2


def yield_bose_einstein(d0, a_cm2):
    return 1.0 / (1.0 + d0 * a_cm2)


def good_die_per_wafer(die_area_mm2, d0, model="murphy"):
    a_cm2 = die_area_mm2 * 0.01
    gross = gross_die_per_wafer(die_area_mm2)
    if model == "poisson":
        y = yield_poisson(d0, a_cm2)
    elif model == "murphy":
        y = yield_murphy(d0, a_cm2)
    elif model == "bose":
        y = yield_bose_einstein(d0, a_cm2)
    else:
        raise ValueError(model)
    return gross, y, int(gross * y)


def print_row(die_area_mm2, d0):
    a_cm2 = die_area_mm2 * 0.01
    gross = gross_die_per_wafer(die_area_mm2)
    yp = yield_poisson(d0, a_cm2)
    ym = yield_murphy(d0, a_cm2)
    yb = yield_bose_einstein(d0, a_cm2)
    print(f"  die={die_area_mm2:>5.0f}mm² ({a_cm2:.2f}cm²) | D0={d0:.2f} | "
          f"gross={gross:>4} | "
          f"Poisson Y={yp*100:5.1f}% gd={int(gross*yp):>4} | "
          f"Murphy Y={ym*100:5.1f}% gd={int(gross*ym):>4} | "
          f"Bose Y={yb*100:5.1f}% gd={int(gross*yb):>4}")


def main():
    print("=" * 100)
    print("飞腾 D3000M 良率与 good-die 推测（300mm 晶圆，方 die 近似，5% 边缘损失）")
    print("  D3000M die 面积推测区间：100-150 mm²（8 核服务器 SoC，14nm 级密度）")
    print("=" * 100)

    # ---- 14nm 成熟工艺：D0 典型 0.3 - 0.5 defects/cm²（量产成熟期）----
    print("\n【情景 A】14nm 成熟期（D0 = 0.3 ~ 0.5 /cm²，对标 Intel 14nm 量产后期 / 中芯 N+1 成熟）")
    for d0 in (0.3, 0.4, 0.5):
        for die in (100, 120, 150):
            print_row(die, d0)
        print()

    # ---- 7nm 早期 vs 成熟 ----
    print("【情景 B】7nm 工艺（对标台积电 N7 / 中芯 N+2）")
    print("  -- 早期爬坡 D0 = 1.5 /cm²（良率学习曲线前段）")
    for die in (80, 100, 120):
        print_row(die, 1.5)
    print("  -- 成熟期 D0 = 0.5 /cm²（台积电 N7 量产后期）")
    for die in (80, 100, 120):
        print_row(die, 0.5)

    # ---- 中芯 N+2 (类7nm DUV 多重曝光) 高 D0 ----
    print("【情景 C】中芯 N+2（DUV SAQP 多重曝光，D0 推测 1.0 ~ 2.0 /cm²，良率受多重曝光拖累）")
    for d0 in (1.0, 1.5, 2.0):
        for die in (100, 120, 150):
            print_row(die, d0)
        print()

    # ---- D3000M 最终推断（Murphy 模型，业界最常用）----
    print("=" * 100)
    print("【D3000M 最终推断】die=120mm²(中位推测) × 14nm 级 × Murphy 模型")
    print("=" * 100)
    print(f"{'D0(/cm²)':<10}{'Gross die':<12}{'良率Y':<10}{'Good die':<12}{'裸die成本($)':<14}")
    wafer_cost_14nm = 4500  # USD, 14nm 含代工
    for d0 in (0.3, 0.4, 0.5, 0.8):
        gross, y, gd = good_die_per_wafer(120, d0, "murphy")
        die_cost = wafer_cost_14nm / gd if gd > 0 else float('inf')
        print(f"{d0:<10.2f}{gross:<12}{y*100:<10.1f}{gd:<12}{die_cost:<14.1f}")

    print("\n（对比）7nm @ die=100mm²(更高密度) × Murphy, wafer=$9400")
    wafer_cost_7nm = 9400
    for d0 in (0.5, 0.8, 1.0):
        gross, y, gd = good_die_per_wafer(100, d0, "murphy")
        die_cost = wafer_cost_7nm / gd if gd > 0 else float('inf')
        print(f"{d0:<10.2f}{gross:<12}{y*100:<10.1f}{gd:<12}{die_cost:<14.1f}")


if __name__ == "__main__":
    main()
