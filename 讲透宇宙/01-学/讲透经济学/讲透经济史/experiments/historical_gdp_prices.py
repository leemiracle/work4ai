# -*- coding: utf-8 -*-
"""
历史 GDP 与价格数据断言（走廊1：历史数据断言 + 走廊2：增长核算）
对应章：讲透经济史/04-经济史转代码.md

数据口径（2026-09 模型知识核对，通行教科书量级；如与 Maddison Project /
BEA / Friedman-Schwartz 最新版不符，以原始出处为准）：
- 人均 GDP：Maddison 2007《世界经济千年史》1990 年国际元（ GK 口径）
- 大萧条：美国 1929-33 实际 GNP/GDP 累计跌幅、CPI 通缩、失业率（ Lebergott 口径）
- 价格革命：16 世纪西班牙物价累计涨幅（ Hamilton 研究，约 3-4 倍）
- 恶性通胀：德国 1923 年物价指数上涨倍数（ >10^9 量级）
断言一律用宽松区间——历史数据的诚实用法。
"""
import math

# Maddison 2007 口径：人均 GDP（1990 国际元，取整）
PER_CAPITA = {
    "英国": {1500: 714, 1700: 1250, 1820: 1707, 1870: 3190, 1913: 4921},
    "美国": {1820: 1257, 1870: 2445, 1913: 5301, 1950: 9561},
    "中国": {1820: 600, 1870: 530, 1913: 552, 1950: 448},
}
# 1820 年占世界 GDP 份额（%，Maddison 2007 表 8a）
WORLD_SHARE_1820 = {"中国": 32.9, "印度": 16.0, "西欧": 23.6, "美国": 1.8}

def cagr(v0, v1, years):
    return (v1 / v0) ** (1.0 / years) - 1.0

def main():
    # 断言1：工业革命前后英国人均增速换代（马尔萨斯陷阱→现代增长）
    pre = cagr(PER_CAPITA["英国"][1500], PER_CAPITA["英国"][1700], 200)
    mid = cagr(PER_CAPITA["英国"][1700], PER_CAPITA["英国"][1820], 120)
    post = cagr(PER_CAPITA["英国"][1820], PER_CAPITA["英国"][1870], 50)
    assert 0.0 < pre < 0.004, pre          # 1500-1700：千年 0.1-0.2% 量级
    assert 0.002 < mid < 0.009, mid        # 1700-1820：温和启动
    assert post > 1.25 * mid, (mid, post)  # 1820 后显著换代
    print(f"[1] 英国人均增速：1500-1700 {pre:.2%} → 1700-1820 {mid:.2%} "
          f"→ 1820-1870 {post:.2%}（陷阱→现代增长的换代）")

    # 断言2：1820 中国总量第一与人均落后的并存（大分流的起点形态）
    assert 30 < WORLD_SHARE_1820["中国"] < 36, WORLD_SHARE_1820["中国"]
    ratio = PER_CAPITA["英国"][1820] / PER_CAPITA["中国"][1820]
    assert 2.5 < ratio < 3.2, ratio
    print(f"[2] 1820：中国占世界 GDP {WORLD_SHARE_1820['中国']}%，"
          f"但英国人均已是中国的 {ratio:.1f} 倍——总量大≠人均富")

    # 断言3：大萧条量级（美国 1929-33）
    gnp_fall, cpi_fall, unemployment = 26.7, 24.0, 24.9  # 通行估计（%）
    assert 24 <= gnp_fall <= 30 and 18 <= cpi_fall <= 30 and 22 <= unemployment <= 26
    print(f"[3] 大萧条：实际 GNP 累计跌 {gnp_fall}%，CPI 跌 {cpi_fall}%，"
          f"1933 失业率 {unemployment}%（通缩+产出双塌方）")

    # 断言4：增长核算恒等式——1870-1913 美国（BLS/Kendrick 型通行量级）
    # 实际产出年增 ~3.9%、资本存量 ~5.6%、劳动 ~2.2%、α=1/3
    g_y, g_k, g_l, alpha = 0.039, 0.056, 0.022, 1/3
    tfp = g_y - alpha * g_k - (1 - alpha) * g_l
    tfp_share_output = tfp / g_y                 # TFP 占产出增速份额
    tfp_share_prod = tfp / (g_y - g_l)           # TFP 占人均（劳动生产率）增速份额
    assert 0.10 < tfp_share_output < 0.20, tfp_share_output
    assert 0.25 < tfp_share_prod < 0.45, tfp_share_prod
    print(f"[4] 1870-1913 美国增长核算：TFP 残差 {tfp:.2%}/年，"
          f"占产出增速 {tfp_share_output:.0%}、占人均增速 {tfp_share_prod:.0%}"
          f"（'我们测度了我们无知的名字'）")

    # 断言5：价格革命与恶性通胀的量级（对数感）
    price_revolution = 3.5      # 16 世纪西班牙物价约 3-4 倍（Hamilton）
    germany_1923 = 1.0e9        # 德国 1923 年物价上涨逾十亿倍
    assert 2.5 <= price_revolution <= 5.0
    assert math.log10(germany_1923) >= 9
    print(f"[5] 16 世纪价格革命 ×{price_revolution}（白银涌入）vs "
          f"1923 德国 ×10^{math.log10(germany_1923):.0f}（月率翻番 20 个月）——"
          f"温和通胀与恶性通胀隔着 8 个数量级")

    print("\n全部断言通过 ✓ （区间断言=历史数据的老实语法）")

if __name__ == "__main__":
    main()
