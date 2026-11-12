"""转型经济体制度绩效表：分组差异、收敛与反弹（断言自验）
对应《讲透比较经济学》00 章（自然实验工具箱）、03 章（识别构造学）、
04 章（走廊 1：绩效数据表）。

⚠ 数据纪律（03 章 §四"账本即制度"的工程对策）：
    表内数字为 IMF WEO / 世界银行公开口径的**教学圆整近似值**——
    真实研究必须回原源核对（且注意 1990s 苏东 MPS→SNA 口径不可通约的
    历史遗留）。本实验断言只验**计算内部一致性**（分组方向、相关
    符号、秩一致），不声称复现任何官方统计。

表：转型经济体两窗口平均实际 GDP 增速（%/年，近似）、谷底年、
2000 年人均 GDP（千美元，名义近似）。中国为渐进参照行（不进分组断言）。

断言（自验证）：
    (a) 转型衰退分组：苏联空间组 1990-2000 均值 < 中东欧组均值；
        波兰唯一显著为正；苏联空间组谷底年中位数更晚（J 曲线更深更长）
    (b) 收敛：2000 年人均 GDP 与 2000-2010 增速负相关（r < −0.3，后发追赶）
    (c) 反弹秩一致：90 年代增速与 00 年代增速 Kendall τ < 0
        （跌得深反弹强——均值回归的转型版）
"""
import numpy as np

# 国名, 分组, 增速90s, 增速00s, 谷底年, 2000人均GDP(千$)
DATA = [
    ("波兰",     "CEE",  3.8, 3.6, 1991, 4.5),
    ("匈牙利",   "CEE",  1.0, 3.0, 1993, 4.6),
    ("捷克",     "CEE",  0.5, 3.2, 1992, 5.8),
    ("斯洛伐克", "CEE",  1.5, 4.0, 1993, 3.8),
    ("斯洛文尼亚","CEE", 2.0, 3.3, 1992, 10.0),
    ("罗马尼亚", "CEE", -1.0, 4.0, 1992, 1.7),
    ("保加利亚", "CEE", -1.5, 3.5, 1997, 1.7),
    ("俄罗斯",   "FSU", -3.5, 4.5, 1998, 1.8),
    ("乌克兰",   "FSU", -7.0, 4.0, 1999, 0.7),
    ("白俄罗斯", "FSU", -0.5, 6.5, 1994, 1.3),
    ("哈萨克斯坦","FSU", -2.5, 7.0, 1995, 1.2),
    ("中国",     "REF", 10.4, 10.5, None, 0.9),   # 渐进参照行
]
ARR = np.array([[r[2], r[3], float(r[4]) if r[4] else np.nan, r[5]] for r in DATA])
CEE = np.array([r[2] for r in DATA if r[1] == "CEE"])
FSU = np.array([r[2] for r in DATA if r[1] == "FSU"])
CEE_TROUGH = [r[4] for r in DATA if r[1] == "CEE"]
FSU_TROUGH = [r[4] for r in DATA if r[1] == "FSU"]
G90 = ARR[:11, 0]                    # 断言组（11 国）
G00 = ARR[:11, 1]
PC00 = ARR[:11, 3]


def pearson(x, y):
    xm, ym = x - x.mean(), y - y.mean()
    return float(np.dot(xm, ym) / np.sqrt(np.dot(xm, xm) * np.dot(ym, ym)))


def kendall_tau(x, y):
    """手写 Kendall τ（n 小，逐对比较；平局不计入分母）。"""
    c = d = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx * dy > 0:
                c += 1
            elif dx * dy < 0:
                d += 1
    return (c - d) / (c + d) if (c + d) else 0.0


def main():
    # ── (a) 转型衰退分组 ──
    cee_mean, fsu_mean = CEE.mean(), FSU.mean()
    poland = DATA[0][2]
    cee_med, fsu_med = float(np.median(CEE_TROUGH)), float(np.median(FSU_TROUGH))
    print(f"(a) 1990-2000 年均增速：中东欧均值={cee_mean:+.2f}%  "
          f"苏联空间均值={fsu_mean:+.2f}%   (断言 FSU < CEE)")
    print(f"    波兰={poland:+.1f}%（断言 >0，教科书'唯一免衰退'）")
    print(f"    谷底年中位数：CEE={cee_med:.0f}  FSU={fsu_med:.1f}   "
          f"(断言 FSU 更晚——J 曲线更深更长)")
    assert fsu_mean < cee_mean, "苏联空间转型衰退应深于中东欧"
    assert poland > 0, "波兰为唯一显著正增长样本（教学近似）"
    assert fsu_med > cee_med, "苏联空间谷底应显著更晚"

    # ── (b) 收敛：初始人均收入 vs 后续增长 ──
    r_conv = pearson(PC00, G00)
    print(f"\n(b) 收敛：corr(2000 人均GDP, 2000-2010 增速) = {r_conv:+.3f}"
          f"   (断言 < −0.3，后发追赶)")
    assert r_conv < -0.3, "穷国（苏联空间）2000s 应增长更快——条件收敛"

    # ── (c) 反弹秩一致：90s vs 00s ──
    tau = kendall_tau(G90, G00)
    r_reb = pearson(G90, G00)
    print(f"(c) 反弹：Kendall τ(增速90s, 增速00s) = {tau:+.3f}  "
          f"Pearson r = {r_reb:+.3f}   (断言 τ<0 且 r<0)")
    assert tau < 0 and r_reb < 0, "跌得深反弹强——衰退深度与后续增速负相关"

    # ── 参照行：中国（不断言，只对照） ──
    print(f"\n参照：中国 90s={DATA[11][2]:+.1f}%  00s={DATA[11][3]:+.1f}%"
          "——渐进路径无转型衰退（分组断言之外的样本，归 [讲透转型研究]）")

    print("\n全部断言通过 ✅  分组差异✓ 收敛符号✓ 反弹秩一致✓。")
    print("带走一句（04 章）：一行计算+一页假设——DID 类方法的代码极简，"
          "有效性全在识别假设里；数据声明（口径/圆整/分组）是结果的一部分。")

if __name__ == "__main__":
    main()
