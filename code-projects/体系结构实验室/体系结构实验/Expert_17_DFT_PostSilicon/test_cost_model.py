#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cost_model.py — D3000M 量产测试成本与 DPPM 逃逸率推算模型

配合 Expert_17_DFT_PostSilicon/README.md §2.2-§2.3 使用。
用业界 ATE 成本模型 + DFT 缺陷覆盖模型，推算每颗 D3000M 的测试成本
与「测试逃逸导致的 DPPM」。

运行: python3 test_cost_model.py

所有数字均为 [推测-依据]，依据见 README §2.2-§2.3。
非飞腾官方数据，仅供体系结构实验项目教学使用。
"""

# ============================================================
# 输入参数（全部标注来源）
# ============================================================

# --- 芯片参数（D3000M，来自实测 + E14 推测）---
DIE_AREA_MM2 = 120          # die 面积 mm² [推测-E14 §5.2]
SCAN_FF = 800_000           # 扫描 FF 数 [推测-E17 §2.2，8核4-wide OoO 中位]
TGT_FREQ_GHZ = 2.5          # 标称频率 GHz [实测-Lab]

# --- 工艺参数（14nm 级）---
YIELD = 0.60                # 良率 [推测-E14 §5.2 Murphy D0=0.4]
GOOD_DIE_PER_WAFER = 314    # 每晶圆 good die [推测-E14 §5.2]

# --- DFT 参数 ---
TEST_COVERAGE = 0.99        # stuck-at 测试覆盖率 TC [推测-E17 §2.2 业界服务器基准]
TRANSITION_TC = 0.90        # transition 覆盖率 [推测-E17 §2.2]
COMPRESSION_RATIO = 200     # 扫描压缩比 [推测-E17 §2.1 业界100-500x]

# --- ATE 成本参数 [报告-VLSIresearch] ---
ATE_PRICE_USD = 2_000_000   # 高端 ATE 单台 (Teradyne/Advantest) [推测-中位]
ATE_DEPREC_YEARS = 5        # 折旧年限
ATE_UTILIZATION = 0.75      # 75% 利用率
HANDLER_PRICE_USD = 500_000 # handler 单台 [推测]
HANDLER_DEPREC_YEARS = 5

# --- 测试时间分解（秒）[推测-E17 图1] ---
TEST_PHASES_WAFER = {
    "DC scan (低速stuck-at)":   0.8,
    "AC scan (at-speed transition)": 1.5,
    "MBIST (cache March自测)":   0.5,
    "IO/PHY (DDR/PCIe链路)":     1.0,
    "功能测试 (boot code)":      1.0,
    "IDDQ (静态漏电)":           0.3,
}
TEST_PHASES_FINAL = {
    "封装后final scan":          1.5,
    "speed bin (shmoo快测)":     1.0,
    "老化后复测 (burn-in后)":    1.5,
}
BURN_IN_HOURS = 0.04        # burn-in 小时/颗 (24-48h批量摊到每颗 ~24h=1天的1/24~1/48) [推测]


# ============================================================
# 模型计算
# ============================================================

def ate_cost_per_second(ate_price, years, util):
    """每秒 ATE 机时成本"""
    # 年可用秒数 = 365天 * 24h * 3600s * util
    annual_seconds = 365 * 24 * 3600 * util
    return ate_price / (years * annual_seconds)


def handler_cost_per_second(price, years, util):
    """每秒 handler 机时成本"""
    annual_seconds = 365 * 24 * 3600 * util
    return price / (years * annual_seconds)


def dppm_escape(yield_rate, tc, burn_in_reduction=0.875):
    """
    DPPM 逃逸率 = 良率损失 * (1 - TC) * (1 - burn_in筛除比例)
    burn_in_reduction: burn-in 能筛掉的比例 (默认 87.5%，即 DPPM 压到 1/8)
    返回: DPPM (百万分之几的坏件逃到客户)
    """
    defect_rate = 1.0 - yield_rate          # 坏 die 比例
    test_escape = defect_rate * (1.0 - tc)  # 逃过测试的坏 die
    after_burnin = test_escape * (1.0 - burn_in_reduction)  # burn-in 后残余
    return after_burnin * 1_000_000         # 转 DPPM


def main():
    print("=" * 70)
    print("D3000M 量产测试成本与 DPPM 逃逸模型")
    print("=" * 70)
    print(f"芯片: 飞腾 D3000M (FTC862, ARMv8.4, 8核, 2.5GHz)")
    print(f"工艺: 14nm级 | die面积: {DIE_AREA_MM2}mm² | 扫描FF: {SCAN_FF:,}")
    print(f"良率: {YIELD*100:.0f}% | good die/晶圆: {GOOD_DIE_PER_WAFER}")
    print(f"TC(stuck-at): {TEST_COVERAGE*100:.0f}% | TC(transition): {TRANSITION_TC*100:.0f}%")
    print(f"压缩比: {COMPRESSION_RATIO}×")
    print()

    # --- 1. 测试时间分解 ---
    print("─" * 70)
    print("【1】单颗 die 测试时间分解（推测）")
    print("─" * 70)
    wafer_time = 0
    print("  Wafer 级（probe card，封装前）:")
    for phase, t in TEST_PHASES_WAFER.items():
        print(f"    {phase:<35} {t:.1f} 秒")
        wafer_time += t
    print(f"    {'小计':<35} {wafer_time:.1f} 秒")

    final_time = 0
    print("  Final 级（封装后）:")
    for phase, t in TEST_PHASES_FINAL.items():
        print(f"    {phase:<35} {t:.1f} 秒")
        final_time += t
    print(f"    {'小计':<35} {final_time:.1f} 秒")

    total_time = wafer_time + final_time
    print(f"\n  ★ 合计测试时间: {total_time:.1f} 秒/颗")
    print(f"    (压缩比 {COMPRESSION_RATIO}× 已计入, 不压将达 {total_time*COMPRESSION_RATIO/10:.0f}+ 秒)")

    # --- 2. 每秒成本 ---
    print("\n" + "─" * 70)
    print("【2】ATE / Handler 每秒机时成本")
    print("─" * 70)
    ate_per_sec = ate_cost_per_second(ATE_PRICE_USD, ATE_DEPREC_YEARS, ATE_UTILIZATION)
    hnd_per_sec = handler_cost_per_second(HANDLER_PRICE_USD, HANDLER_DEPREC_YEARS, ATE_UTILIZATION)
    print(f"  ATE 单台: ${ATE_PRICE_USD:,} / {ATE_DEPREC_YEARS}年折旧 / {ATE_UTILIZATION*100:.0f}%利用")
    print(f"    → 每秒 ATE 成本: ${ate_per_sec:.4f}")
    print(f"  Handler 单台: ${HANDLER_PRICE_USD:,} / {HANDLER_DEPREC_YEARS}年折旧")
    print(f"    → 每秒 Handler 成本: ${hnd_per_sec:.4f}")
    print(f"    → 合计每秒: ${ate_per_sec + hnd_per_sec:.4f}")

    # --- 3. 每颗测试成本 ---
    print("\n" + "─" * 70)
    print("【3】每颗 D3000M 测试成本（核心产出）")
    print("─" * 70)
    per_sec_total = ate_per_sec + hnd_per_sec
    wafer_cost = wafer_time * per_sec_total
    final_cost = final_time * per_sec_total
    # burn-in 成本 (oven 摊销, 业界 ~$0.5-2/颗)
    burnin_cost = max(BURN_IN_HOURS * 10, 0.5)  # 简化: ~$0.5-1/颗
    total_cost = wafer_cost + final_cost + burnin_cost

    print(f"  Wafer test:  {wafer_time:.1f}s × ${per_sec_total:.4f}/s = ${wafer_cost:.2f}")
    print(f"  Final test:  {final_time:.1f}s × ${per_sec_total:.4f}/s = ${final_cost:.2f}")
    print(f"  Burn-in:     ~{BURN_IN_HOURS*24:.0f}h批量摊销         = ${burnin_cost:.2f}")
    print(f"  ─────────────────────────────────────────")
    print(f"  ★ 每颗测试总成本: ${total_cost:.2f}")

    sell_price_low, sell_price_high = 500, 1000
    pct = total_cost / sell_price_low * 100
    print(f"\n  信创售价 ${sell_price_low}-{sell_price_high}, 测试成本占比 {pct:.2f}-{total_cost/sell_price_high*100:.2f}%")
    print(f"  (对比: 裸 die 成本 ~$15 [E14], 封装 ~$5-15 [E15])")
    print(f"  结论: 测试不是成本大头, 但它决定 DPPM 与质量一致性")

    # --- 4. DPPM 逃逸分析 ---
    print("\n" + "─" * 70)
    print("【4】DPPM 逃逸率分析（质量守门员）")
    print("─" * 70)
    dppm_no_burnin = dppm_escape(YIELD, TEST_COVERAGE, burn_in_reduction=0.0)
    dppm_with_burnin = dppm_escape(YIELD, TEST_COVERAGE, burn_in_reduction=0.875)
    print(f"  良率损失: {1-YIELD:.0%} 的 die 有致命缺陷")
    print(f"  TC={TEST_COVERAGE*100:.0f}% → 逃逸率 = {1-YIELD:.0%} × {1-TEST_COVERAGE:.0%} = {(1-YIELD)*(1-TEST_COVERAGE):.4f}")
    print(f"\n  无 burn-in:  DPPM = {dppm_no_burnin:,.0f}  (太高, 服务器不可接受)")
    print(f"  有 burn-in(筛87.5%): DPPM = {dppm_with_burnin:,.0f}  (信创可接受, 金融仍偏高)")
    print(f"\n  对标:")
    print(f"    Intel/AMD 服务器 CPU DPPM 目标: < 100  [报告-Intel quality]")
    print(f"    D3000M (推测):                   {dppm_with_burnin:,.0f}")
    print(f"  差距来源: TC 99% vs Intel ~99.5%+ | 良率 60% vs Intel ~85%+ | 后发厂商积累")

    # --- 5. 一片晶圆的测试经济性 ---
    print("\n" + "─" * 70)
    print("【5】单晶圆测试经济性")
    print("─" * 70)
    wafer_test_revenue_saved = GOOD_DIE_PER_WAFER * total_cost
    gross_die = int(GOOD_DIE_PER_WAFER / YIELD)
    bad_caught = gross_die - GOOD_DIE_PER_WAFER
    print(f"  gross die: ~{gross_die} | good die: {GOOD_DIE_PER_WAFER} | 坏 die 被测出: ~{bad_caught}")
    print(f"  测每颗 good die 成本: ${total_cost:.2f} × {GOOD_DIE_PER_WAFER} = ${wafer_test_revenue_saved:.0f}/晶圆")
    print(f"  wafer 成本 ~$4500 [E14], 测试追加 ${wafer_test_revenue_saved:.0f} = 晶圆成本的 {wafer_test_revenue_saved/4500*100:.1f}%")
    print(f"  测出坏 die 省下的封装成本: ~{bad_caught} × $10 = ${bad_caught*10:,} (避免封装废件)")

    # --- 6. 敏感性分析 ---
    print("\n" + "─" * 70)
    print("【6】敏感性：TC 与 burn-in 对 DPPM 的影响")
    print("─" * 70)
    print(f"  {'TC':>6} | {'无burn-in DPPM':>14} | {'有burn-in DPPM':>14} | {'评价':>20}")
    print(f"  {'─'*6}─┼─{'─'*14}─┼─{'─'*14}─┼─{'─'*20}")
    for tc in [0.95, 0.98, 0.99, 0.995, 0.999]:
        d_nb = dppm_escape(YIELD, tc, 0.0)
        d_wb = dppm_escape(YIELD, tc, 0.875)
        if d_wb > 1000:
            eval_str = "信创勉强可接受"
        elif d_wb > 100:
            eval_str = "企业级接近"
        else:
            eval_str = "Intel 级标杆"
        print(f"  {tc*100:>5.1f}% | {d_nb:>14,.0f} | {d_wb:>14,.0f} | {eval_str:>20}")

    print("\n" + "=" * 70)
    print("结论: D3000M 测试成本 ~$%.0f/颗 (占售价 <0.1%%), 不是成本大头;" % total_cost)
    print("      但 DPPM ~%d (有burn-in) 高于 Intel <100, 质量一致性是追赶项。" % dppm_with_burnin)
    print("      errata 不公开 + DPPM 偏高 = 飞腾从信创升级到通用企业的两道槛。")
    print("=" * 70)


if __name__ == "__main__":
    main()
