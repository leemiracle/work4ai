#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
art_demos.py — 艺术费曼式可跑 demo（纯标准库，python3 直接跑）
================================================================================
对应 top-art-courses 八大主题中「数学/算法可切入」的部分。

设计原则（与 work4ai 铁律一致）：
  - 纯标准库（math/colorsys/turtle 不用，全用 math + 基本类型），python3 直接跑
  - 每个 demo = 费曼一句话直觉 + 数学/算法 + 可跑输出 + 艺术反思
  - 覆盖：黄金比例(构图) / 色彩理论 / 透视(绘画) / 分形(生成艺术) / L-system / 风格迁移概念(AI艺术)

用法:
    python3 art_demos.py

依赖: Python 3.6+ 标准库（无 numpy/PIL，ASCII 可视化）
================================================================================
"""

import math

# ============================================================================
# Demo 1 —— 构图基础：黄金比例 φ 与斐波那契
# ============================================================================
def golden_ratio_demo():
    """
    黄金比例 φ = (1+√5)/2 ≈ 1.618。
    艺术应用：帕特农神庙立面、达芬奇《维特鲁威人》、构图三分法、斐波那契螺旋。
    费曼：φ 是「让人眼最舒服」的比例——数学与美学的交汇点。
    """
    phi = (1 + math.sqrt(5)) / 2
    print(f"  φ = (1+√5)/2 = {phi:.6f}")
    print(f"  1/φ   = {1/phi:.6f}   (≈ {phi-1:.6f} = φ−1，自相似性)")
    print(f"  φ²    = {phi**2:.6f}   (≈ {phi+1:.6f} = φ+1)")

    # 斐波那契：相邻两项之比 → φ
    fib = [1, 1]
    for _ in range(18):
        fib.append(fib[-1] + fib[-2])
    print(f"  斐波那契前 8 项: {fib[:8]}")
    ratios = [fib[i + 1] / fib[i] for i in range(4, 12)]
    print(f"  F(n+1)/F(n) 演化: {[f'{r:.4f}' for r in ratios[:5]]} ... → φ")
    print(f"  💡 构图应用: 三分法、斐波那契螺旋、人体比例(达芬奇《维特鲁威人》)")


# ============================================================================
# Demo 2 —— 色彩理论：RGB ↔ HSL + 配色生成
# ============================================================================
def rgb_to_hsl(r, g, b):
    """RGB(0-255) → HSL(H:0-360, S/L:0-1)。"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60, s, l


def hsl_to_rgb(h, s, l):
    """HSL → RGB(0-255)。"""
    c = (1 - abs(2 * l - 1)) * s
    h_ = (h % 360) / 60
    x = c * (1 - abs(h_ % 2 - 1))
    if   h_ < 1: r, g, b = c, x, 0
    elif h_ < 2: r, g, b = x, c, 0
    elif h_ < 3: r, g, b = 0, c, x
    elif h_ < 4: r, g, b = 0, x, c
    elif h_ < 5: r, g, b = x, 0, c
    else:        r, g, b = c, 0, x
    m = l - c / 2
    return round((r + m) * 255), round((g + m) * 255), round((b + m) * 255)


def color_harmonics(rgb):
    """从一色生成互补色(180°)、三元色(120°)、类比色(30°)。"""
    h, s, l = rgb_to_hsl(*rgb)
    out = {"原色": rgb}
    for name, delta in [("互补色(180°)", 180), ("三元色(120°)", 120), ("类比色(+30°)", 30)]:
        out[name] = hsl_to_rgb(h + delta, s, l)
    return out


def color_theory_demo():
    """
    色彩理论：色相/饱和度/明度 (HSL) 是比 RGB 更符合人脑的色彩空间。
    艺术应用：莫奈的色彩并置、马蒂斯的纯色、互补色震动感（梵高《星夜》黄蓝）。
    """
    base = (30, 90, 200)  # 一种蓝色（近似梵高星夜）
    print(f"  基础色 RGB{base}")
    h, s, l = rgb_to_hsl(*base)
    print(f"  → HSL: H={h:.1f}° S={s:.2f} L={l:.2f}")
    print("  色彩和谐配色:")
    for name, c in color_harmonics(base).items():
        print(f"    {name:<16}: RGB{c}")
    print("  💡 互补色并置产生'震动'（梵高黄蓝），三元色平衡，类比色和谐")


# ============================================================================
# Demo 3 —— 绘画基础：一点透视投影（3D → 2D）
# ============================================================================
def one_point_perspective(x, y, z, d=5.0):
    """
    一点透视：3D 点 (x,y,z) 投影到 2D 画面。z=0 为画面，d 为观察者到画面距离。
        x' = d·x / (d+z),   y' = d·y / (d+z)
    艺术应用：文艺复兴透视术（布鲁内莱斯基/阿尔贝蒂《论绘画》1435）。
    """
    f = d / (d + z)
    return x * f, y * f


def perspective_demo():
    """
    透视术是文艺复兴的数学革命——把"所见"科学化。
    达芬奇《最后的晚餐》灭点在耶稣头部 = 用透视引导视线。
    """
    print("  一点透视：把 3D 立方体投影到画面（观察者距画面 d=5）")
    cube = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0),        # 前面 z=0
            (-1, -1, 4), (1, -1, 4), (1, 1, 4), (-1, 1, 4)]         # 后面 z=4
    print("  3D 顶点          →  2D 画面投影")
    for p in cube:
        x2, y2 = one_point_perspective(*p)
        print(f"    ({p[0]:+.0f},{p[1]:+.0f},{p[2]})  →  ({x2:+.3f}, {y2:+.3f})")
    print("  💡 远处的边(z=4)投影更靠近灭点(0,0)——这就是'近大远小'的数学")


# ============================================================================
# Demo 4 —— 生成艺术：曼德博集合（ASCII）
# ============================================================================
def mandelbrot_ascii(width=70, height=24, max_iter=40):
    """
    曼德博集合 M = { c : z₀=0, z_{n+1}=z_n²+c 不发散 }。
    分形 = 无限自相似。曼德博(1980)开启了分形艺术。
    艺术应用：生成艺术、自然界形态（海岸线/云/树）的数学。
    """
    chars = " .,:;i!*=#@"  # 从暗到亮
    lines = []
    for row in range(height):
        y = (row / height) * 2.4 - 1.2  # y ∈ [-1.2, 1.2]
        line = []
        for col in range(width):
            x = (col / width) * 3.0 - 2.0  # x ∈ [-2, 1]
            zr, zi = 0.0, 0.0
            n = 0
            while n < max_iter and zr * zr + zi * zi < 4:
                zr, zi = zr * zr - zi * zi + x, 2 * zr * zi + y
                n += 1
            if n == max_iter:
                line.append("@")
            else:
                line.append(chars[min(n * len(chars) // max_iter, len(chars) - 1)])
        lines.append("".join(line))
    return "\n".join(lines)


def mandelbrot_demo():
    print("  曼德博集合 z_{n+1}=z_n²+c 的逃逸时间图（ASCII 70×24）:")
    print("  " + "-" * 70)
    body = mandelbrot_ascii()
    for ln in body.split("\n"):
        print("  " + ln)
    print("  " + "-" * 70)
    print("  💡 @ = 集合内（不发散）；其余=逃逸速度。无限放大边界=无限自相似")


# ============================================================================
# Demo 5 —— 生成艺术：L-system 分形树
# ============================================================================
def l_system(axiom, rules, iterations):
    """Lindenmayer 系统：字符串重写 = 植物形态发生的语法（1968）。"""
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(ch, ch) for ch in s)
    return s


def lsystem_demo():
    """
    L-system：生物学家 Lindenmayer 用形式语法模拟植物生长。
    艺术：生成分形树/雪花/海岸线，是「代码艺术/生成艺术」的鼻祖之一。
    """
    # 经典分形树规则
    axiom = "F"
    rules = {"F": "FF+[+F-F-F]-[-F+F+F]"}
    result = l_system(axiom, rules, 3)
    print(f"  L-system 规则: 公理='F', F → 'FF+[+F-F-F]-[-F+F+F]'")
    print(f"  迭代 3 次后字符串长度: {len(result)}（指数增长）")
    print(f"  前 60 字符: {result[:60]}...")
    # 解析（F=前进, +/-=转, [/]=压入/弹出状态）
    import collections
    counts = collections.Counter(result)
    print(f"  符号统计: {dict(counts)}")
    print("  💡 F=树枝段, +/−=分叉角度, [/]=分支堆栈 —— 简单规则生成复杂树形")
    print("     这就是「涌现」：局部规则 → 整体形态（呼应 [复杂系统学-处理work4ai]）")


# ============================================================================
# Demo 6 —— AI 艺术概念：风格统计混合（Gatys 神经风格迁移的简化）
# ============================================================================
def make_pattern(kind, size=8):
    """生成简单的灰度图案（模拟内容图 vs 风格图）。"""
    g = []
    for i in range(size):
        row = []
        for j in range(size):
            if kind == "content":      # 内容：中心亮（一个"物"）
                v = max(0.0, 1.0 - math.hypot(i - size / 2, j - size / 2) / (size / 2))
            elif kind == "style_wave": # 风格A：正弦波纹理
                v = 0.5 + 0.5 * math.sin(i * 0.9) * math.cos(j * 0.9)
            else:                       # 风格B：棋盘
                v = 1.0 if (i + j) % 2 == 0 else 0.0
            row.append(v)
        g.append(row)
    return g


def gram_statistic(grid):
    """
    Gatys(2015) 风格迁移的核心：风格 = 特征的 Gram 矩阵（二阶统计）。
    这里用一阶近似：风格 = {均值, 标准差}；内容 = 原始像素。
    AdaIN(Huang 2017) 就是用均值/方差做风格迁移。
    """
    flat = [v for row in grid for v in row]
    mean = sum(flat) / len(flat)
    var = sum((v - mean) ** 2 for v in flat) / len(flat)
    return mean, math.sqrt(var)


def style_transfer(content, style, alpha=1.0):
    """
    简化 AdaIN：保留内容结构，强制统计量匹配风格。
        out = (content - μ_content)/σ_content · σ_style + μ_style
    """
    mc, sc = gram_statistic(content)
    ms, ss = gram_statistic(style)
    if sc < 1e-6:
        sc = 1e-6
    out = [[(v - mc) / sc * ss * alpha + ms for v in row] for row in content]
    return out


def grid_to_ascii(grid, chars=" .:-=+*#%@"):
    """灰度网格 → ASCII 图。"""
    return "\n".join("".join(chars[min(int(v * (len(chars) - 1)), len(chars) - 1)] for v in row)
                     for row in grid)


def style_transfer_demo():
    """
    Gatys(2015)「艺术风格的神经算法」开创 AI 风格迁移。
    核心：内容=特征响应(CNN 高层)，风格=Gram 矩阵(纹理统计)。
    艺术意义：把"内容 vs 形式"这对千年张力（§2 张力②）变成了可分离的数学量！
    """
    content = make_pattern("content")
    style = make_pattern("style_wave")
    out = style_transfer(content, style)
    print("  内容图（一个亮斑）:")
    print("  " + grid_to_ascii(content).replace("\n", "\n  "))
    print("  风格图（正弦波纹理）:")
    print("  " + grid_to_ascii(style).replace("\n", "\n  "))
    print("  风格迁移结果（保留内容结构 + 套用风格统计）:")
    print("  " + grid_to_ascii(out).replace("\n", "\n  "))
    mc, sc = gram_statistic(content); ms, ss = gram_statistic(style); mo, so = gram_statistic(out)
    print(f"  统计: 内容(μ={mc:.2f},σ={sc:.2f}) 风格(μ={ms:.2f},σ={ss:.2f}) 输出(μ={mo:.2f},σ={so:.2f})")
    print("  💡 输出的统计量≈风格(μ,σ)，结构≈内容 —— 这就是「内容 vs 形式」的数学分离！")


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("=" * 72)
    print(" top-art-courses · art_demos.py".center(72))
    print(" 艺术的数学/算法可跑 demo（纯标准库，python3 直接跑）".center(72))
    print("=" * 72)

    print("\n── Demo 1 · 构图：黄金比例 φ 与斐波那契 ──")
    golden_ratio_demo()

    print("\n── Demo 2 · 色彩理论：RGB↔HSL + 配色 ──")
    color_theory_demo()

    print("\n── Demo 3 · 绘画：一点透视投影 ──")
    perspective_demo()

    print("\n── Demo 4 · 生成艺术：曼德博集合 ──")
    mandelbrot_demo()

    print("\n── Demo 5 · 生成艺术：L-system 分形树 ──")
    lsystem_demo()

    print("\n── Demo 6 · AI 艺术：风格统计混合（AdaIN 简化）──")
    style_transfer_demo()

    print("\n" + "=" * 72)
    print(" 全部 demo 完成。覆盖: 构图/色彩/透视/分形/L-system/AI风格迁移".center(72))
    print("=" * 72)


if __name__ == "__main__":
    main()
