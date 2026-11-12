# -*- coding: utf-8 -*-
"""Mamdani 模糊推理温度控制器:一句口语规则的编译之旅。

00 章(体系结构)与 04 章(转代码)配套实验。纯标准库,无第三方依赖。

流程(04 章 §一 的五步编译):
  ①模糊化(三角隶属) ②min-蕴含 ③max-聚合 ④重心解模糊
规则(口语原文,风扇功率控制):
  IF 误差负大(NB) THEN 功率低(L)
  IF 误差负小(NS) THEN 功率中低(ML)
  IF 误差零(ZE)   THEN 功率中(M)
  IF 误差正小(PS) THEN 功率中高(MH)
  IF 误差正大(PB) THEN 功率高(H)
验证(自断言):
  · 控制曲面连续(小扰动→小输出变化)
  · 单调(误差越正功率越高)
  · 边界行为(饱和于两端)

跑法: python 讲透数学/讲透模糊数学/experiments/00_mamdani.py
"""

# ---------- 走廊 A:隶属函数库(三角) ----------

def trimf(x, a, b, c):
    """三角隶属函数:顶点 b,肩点 a 与 c;支持肩形(a=b 或 b=c,端点=1)。"""
    if x < a or x > c:
        return 0.0
    lo = 1.0 if a == b else (x - a) / (b - a)   # 左肩:端点直接满隶属
    hi = 1.0 if b == c else (c - x) / (c - b)   # 右肩:同上
    return max(0.0, min(1.0, min(lo, hi)))


# ---------- 语言变量(词集→曲线组) ----------

# 输入:温度误差 e = T_target - T_current(正=偏冷需加热,这里统一按"误差正→输出大")
E_TERMS = {  # 论域 [-3, 3] °C
    "NB": lambda e: trimf(e, -3, -3, -1.2),
    "NS": lambda e: trimf(e, -3, -1.5, 0.0),
    "ZE": lambda e: trimf(e, -1.5, 0.0, 1.5),
    "PS": lambda e: trimf(e, 0.0, 1.5, 3.0),
    "PB": lambda e: trimf(e, 1.2, 3, 3),
}
# 输出:风扇/加热功率档位,论域 [0, 100] %
U_TERMS = {
    "L":  (0.0, 0.0, 35.0),
    "ML": (15.0, 35.0, 55.0),
    "M":  (35.0, 55.0, 75.0),
    "MH": (55.0, 75.0, 95.0),
    "H":  (65.0, 100.0, 100.0),
}
RULES = [("NB", "L"), ("NS", "ML"), ("ZE", "M"), ("PS", "MH"), ("PB", "H")]


# ---------- 走廊 B+C:推理机与解模糊器 ----------

def infer_power(e, grid=None):
    """Mamdani 推理:①μ(e) ②min-蕴含 ③max-聚合 ④重心解模糊。"""
    if grid is None:
        grid = [i * 100.0 / 400 for i in range(401)]  # 输出论域离散网格
    aggregated = [0.0] * len(grid)
    for ante, cons in RULES:                       # ②③:每条规则 min 蕴含,逐点 max 聚合
        w = E_TERMS[ante](e)
        if w <= 0.0:
            continue
        a, b, c = U_TERMS[cons]
        for i, u in enumerate(grid):
            clipped = min(w, trimf(u, a, b, c))
            if clipped > aggregated[i]:
                aggregated[i] = clipped
    num = sum(aggregated[i] * u for i, u in enumerate(grid))   # ④重心法
    den = sum(aggregated)
    return num / den if den > 1e-12 else 50.0  # 全零(不应发生)回中位


def control_surface(step=0.1):
    """离线预计算控制曲面(04 章 §四:量产形态=查表)。整数索引步进,避免浮点累积越界。"""
    n = int(round(6.0 / step))
    table = {}
    for i in range(n + 1):
        e = -3.0 + i * step
        table[round(e, 4)] = infer_power(max(-3.0, min(3.0, e)))  # 端点 clamp 防御
    return table


def main():
    print("=" * 64)
    print("Mamdani 温度控制器:IF 误差正大 THEN 功率高 ×5 条规则")
    print("=" * 64)
    print(f"{'误差e(°C)':>10} {'功率(%)':>8}")
    for e in (-2.5, -1.5, -0.5, 0.0, 0.5, 1.5, 2.5):
        print(f"{e:>10.1f} {infer_power(e):>8.1f}")

    surf = control_surface()
    es = sorted(surf)

    # ---- 自断言 1:控制曲面连续光滑(相邻步长变化有界——导数有界的数值形态) ----
    max_jump = max(abs(surf[es[i + 1]] - surf[es[i]]) for i in range(len(es) - 1))
    print(f"\n[断言1] 曲面光滑性:相邻步长(0.1°C)输出最大变化 = {max_jump:.3f} %(阈值 4.0=有界导数)")
    assert max_jump < 4.0, "min-max 推理的分段平滑性:无跳变、导数有界"

    # ---- 自断言 2:单调(误差越正,功率越高;允许局部平段) ----
    mono_violation = sum(
        1 for i in range(len(es) - 1) if surf[es[i + 1]] < surf[es[i]] - 0.5
    )
    print(f"[断言2] 单调性:显著下降段计数 = {mono_violation}(应为 0)")
    assert mono_violation == 0, "规则库语义=误差正→功率大,曲面应单调不减"

    # ---- 自断言 3:边界饱和(两端输出贴近 0/100 档) ----
    lo, hi = surf[es[0]], surf[es[-1]]
    print(f"[断言3] 边界饱和:e=-3 → {lo:.1f}%(≤12)  e=+3 → {hi:.1f}%(≥88)")
    assert lo <= 12.0 and hi >= 88.0, "端点应饱和于 L/H 档"

    # ---- 反直觉实证:局部改规则的鲁棒性(min-max 的分段性) ----
    global RULES
    backup = RULES[:]
    RULES = [("NB", "L"), ("NS", "ML"), ("ZE", "H"), ("PS", "MH"), ("PB", "H")]  # 改 ZE 后果
    far = [infer_power(e) for e in (2.2, 2.5)]
    near = infer_power(0.0)
    RULES = backup
    print(f"\n[鲁棒性] 只翻转 ZE 规则的后果词:中心 e=0 输出翻转(55→{near:.0f}%),")
    print(f"          远端 e≈2.4 输出几乎不动({far[0]:.1f}%/{far[1]:.1f}%)——改动不传播(04 章 §二)")

    print("\n读数:五条口语规则 → 连续/单调/饱和的控制曲面;")
    print("      推理全程只有 min/max/加权平均——可机械化的极限=离线一张表(量产形态)。")


if __name__ == "__main__":
    main()
