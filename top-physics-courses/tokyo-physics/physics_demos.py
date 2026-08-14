"""
Tokyo 物理演示 · 费曼式可视化
===============================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

课程对应：
  力学       刚体转动、回转仪
  电磁学     电磁感应、变压器原理
  量子力学   测不准原理、隧道效应
  统计力学   黑体辐射、玻色分布
  数学方法   球面调和函数
  Kavli IPMU 暗物质/暗能量宇宙学
  東大物性   超导/超流凝聚态

特色：IPMU 宇宙学 + 东京大学凝聚态传统

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个
"""
import math
import sys
import random

random.seed(42)

# ============================================================
#  ASCII 可视化辅助
# ============================================================

def ascii_scatter(points, w=62, h=16, title="", xlab="", ylab=""):
    if not points:
        print("  (无数据)"); return
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin: xmax += 1
    if ymax == ymin: ymax += 1
    pad = (ymax - ymin) * 0.06
    ymin -= pad; ymax += pad
    grid = [[' '] * w for _ in range(h)]
    for x, y in points:
        c = int((x - xmin) / (xmax - xmin) * (w - 1))
        r = int((ymax - y) / (ymax - ymin) * (h - 1))
        c = max(0, min(w - 1, c)); r = max(0, min(h - 1, r))
        grid[r][c] = '●'
    bar = "─" * w
    print(f"\n  ┌ {title} {'─' * max(1, w - len(title) - 2)}┐")
    for row in grid:
        print(f"  │{''.join(row)}│")
    print(f"  └{bar}┘")
    print(f"   {xlab}: [{xmin:.3g}, {xmax:.3g}]   {ylab}: [{ymin:.3g}, {ymax:.3g}]")

def ascii_hist(data, bins=24, w=46, title=""):
    if not data:
        print("  (无数据)"); return
    lo, hi = min(data), max(data)
    if hi == lo: hi += 1
    counts = [0] * bins
    for v in data:
        i = min(int((v - lo) / (hi - lo) * bins), bins - 1)
        counts[i] += 1
    mx = max(counts) or 1
    print(f"\n  ┌ {title} {'─' * 20}┐")
    for i in range(bins):
        bl = int(counts[i] / mx * w)
        le = lo + i * (hi - lo) / bins
        he = lo + (i + 1) * (hi - lo) / bins
        print(f"  │ [{le:7.3g},{he:7.3g}) {'█' * bl}{' ' * (w - bl)} {counts[i]:4d}")
    print(f"  └{'─' * (w + 26)}┘")

def ascii_bar(values, labels, w=40, title=""):
    mx = max(abs(v) for v in values) or 1
    print(f"\n  ┌ {title} {'─' * 20}┐")
    for lab, val in zip(labels, values):
        bl = int(abs(val) / mx * w)
        sign = '+' if val >= 0 else '-'
        print(f"  │ {lab:<22s} {sign}{'█' * bl:<{w}} {val:.4g}")
    print(f"  └{'─' * (w + 32)}┘")

# ============================================================
# Demo 1 · 刚体转动惯量——质量的'分布'才是关键
# ============================================================

def demo_rigid_body():
    """
    白话：同样质量的物体，转起来的'懒散程度'（转动惯量）可以差好几倍——
    关键不在质量，而在质量离轴有多远。越远的质量越'懒得转'。
    反直觉：一根棒绕中心和绕端点转，转动惯量差 4 倍！
    这就是为什么花样滑冰选手收手就转快——质量没变，转动惯量变了。
    类比： door——推门把手（远端）轻松转动，推门轴（近端）纹丝不动。
    """
    print("\n" + "=" * 64)
    print("  Demo 1 · 转动惯量：质量分布决定一切")
    print("=" * 64)

    M = 1.0; R = 1.0; L = 1.0

    shapes = [
        ("质点 (距R)",      M * R**2,          "I = mR²"),
        ("细环 (半径R)",     M * R**2,          "I = mR²"),
        ("空心柱 (半径R)",   M * R**2,          "I = mR²"),
        ("实心柱 (半径R)",   M * R**2 / 2,      "I = ½mR²"),
        ("实心球 (半径R)",   2 * M * R**2 / 5,  "I = 2/5 mR²"),
        ("空心球 (半径R)",   2 * M * R**2 / 3,  "I = 2/3 mR²"),
        ("细棒 (中心)",      M * L**2 / 12,     "I = 1/12 mL²"),
        ("细棒 (端点)",      M * L**2 / 3,      "I = 1/3 mL²"),
    ]

    print(f"\n  M = {M} kg,  R = L = {R} m\n")
    print(f"  {'形状':>14s}  {'I (kg·m²)':>10s}  {'公式':>16s}")
    print(f"  {'─'*14}  {'─'*10}  {'─'*16}")
    for name, I, formula in shapes:
        print(f"  {name:>14s}  {I:>10.4f}  {formula:>16s}")

    I_values = [s[1] for s in shapes]
    I_names = [s[0] for s in shapes]
    ascii_bar(I_values, I_names, title="转动惯量比较")

    # 平行轴定理
    print("\n  平行轴定理：I = I_cm + Md²")
    rod_cm = M * L**2 / 12
    print(f"    细棒绕中心 I_cm = {rod_cm:.4f}")
    for d in [0.0, 0.5, 1.0, 2.0]:
        I_parallel = rod_cm + M * d**2
        print(f"    d = {d:.1f} → I = {I_parallel:.4f}  "
              f"(增量 Md² = {M*d**2:.4f})")

    print("\n  ※ 反直觉：细棒绕端点比绕中心难转 4 倍——")
    print("    因为端点处多了 Md² = M(L/2)² 的贡献！")
    print("  ※ 东大传统：刚体力学是入学考试必考题。")
    print("  ※ 生活类比：锤子——头在远端（大 I），敲钉子才有力。")

# ============================================================
# Demo 2 · 变压器原理——电磁感应的魔法
# ============================================================

def demo_transformer():
    """
    白话：两个线圈不接触，一个通电另一个就有电——这不是魔法，是电磁感应！
    变化的磁场穿过第二个线圈，就'感应'出电压。匝数比决定电压比。
    反直觉：理想变压器不创造能量！P₁ = P₂——电压高的一边电流小，
    电压低的一边电流大。就像杠杆：力臂长的一边力小。
    类比：齿轮传动——大齿轮转慢但力大，小齿轮转快但力小。
    """
    print("\n" + "=" * 64)
    print("  Demo 2 · 变压器原理：匝数比 = 电压比")
    print("=" * 64)

    print("\n  理想变压器：V₂/V₁ = N₂/N₁,  P₁ = P₂ → I₂/I₁ = N₁/N₂\n")

    V1 = 100  # V
    N1 = 1000

    print(f"  初级线圈：V₁ = {V1} V, N₁ = {N1} 匝\n")
    print(f"  {'类型':>10s}  {'N₂':>6s}  {'V₂ (V)':>8s}  "
          f"{'I₂/I₁':>8s}  {'用途':>16s}")
    print(f"  {'─'*10}  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*16}")

    configs = [
        ("降压", 100, "门铃/充电器"),
        ("降压", 50, "低压电子"),
        ("降压", 10, "微电子"),
        ("升压", 5000, "霓虹灯"),
        ("升压", 50000, "远距离输电"),
    ]
    for name, N2, use in configs:
        ratio = N2 / N1
        V2 = V1 * ratio
        I_ratio = 1 / ratio
        print(f"  {name:>10s}  {N2:>6d}  {V2:>8.1f}  "
              f"{I_ratio:>8.4f}  {use:>16s}")

    # 输电损耗演示
    print("\n  为什么远距离输电要用高压？")
    P = 1e6  # 1 MW
    for V in [220, 11000, 110000, 500000]:
        I = P / V
        R_line = 10  # 线路电阻 10 Ω
        loss = I**2 * R_line
        eff = (P - loss) / P * 100
        print(f"    V = {V:>7.0f} V → I = {I:>8.1f} A → "
              f"线损 = {loss:.0f} W ({eff:.4f}%)")

    print("\n  ※ 反直觉：电压从 220V 升到 500kV，线损减少几十亿倍！")
    print("    这就是为什么特高压输电是现代电力系统的基础。")
    print("  ※ 东京大学变压器研究→东京电力→日本全国电网。")
    print("  ※ 生活类比：水管——细管（低压）水阻大损耗大，")
    print("    粗管（高压）水流通畅损耗小。")

# ============================================================
# Demo 3 · 测不准原理——你不可能什么都知道
# ============================================================

def demo_uncertainty():
    """
    白话：量子世界里，你不可能同时精确知道粒子的位置和动量。
    把位置测得越准，动量就越模糊——反之亦然。这不是仪器不够好，
    是自然的根本法则。Δx·Δp ≥ ℏ/2。
    反直觉：这不是测量误差！是粒子本身就不'同时拥有'
    精确的位置和动量。在你测量之前，这些量甚至没有确定值。
    类比：拍运动物体的照片——快门快（位置准）就看不出速度，
    快门慢（速度准）位置就模糊。但量子版的限制是根本性的。
    """
    print("\n" + "=" * 64)
    print("  Demo 3 · 海森堡测不准原理 Δx·Δp ≥ ℏ/2")
    print("=" * 64)

    hbar = 1.0

    print("\n  高斯波包的不确定关系：")
    print("  ψ(x) ∝ exp(−x²/(4σ²))  →  Δx = σ")
    print("  φ(p) ∝ exp(−p²σ²/ℏ²)  →  Δp = ℏ/(2σ)")
    print("  乘积：Δx·Δp = ℏ/2  (最小不确定态)\n")

    print(f"  {'σ (位置宽度)':>14s}  {'Δx':>8s}  {'Δp':>10s}  "
          f"{'Δx·Δp':>10s}  {'≥ ℏ/2?':>8s}")
    print(f"  {'─'*14}  {'─'*8}  {'─'*10}  {'─'*10}  {'─'*8}")

    pts_dx = []; pts_dp = []
    for sigma in [0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
        dx = sigma
        dp = hbar / (2 * sigma)
        product = dx * dp
        ok = "✓" if product >= hbar/2 - 1e-10 else "✗"
        print(f"  {sigma:>14.1f}  {dx:>8.2f}  {dp:>10.4f}  "
              f"{product:>10.4f}  {ok:>8s}")
        pts_dx.append((sigma, dx))
        pts_dp.append((sigma, dp))

    # 波函数可视化
    for sigma in [0.5, 2.0]:
        pts = []
        x = -5
        while x <= 5:
            psi = math.exp(-x**2 / (4 * sigma**2))
            pts.append((x, psi))
            x += 0.05
        ascii_scatter(pts, title=f"位置空间 ψ(x)  σ={sigma}",
                      xlab="x", ylab="ψ")

    print("\n  ※ 反直觉：σ→0 时 Δx→0 但 Δp→∞——")
    print("    把粒子'钉死'在一个点，它的动量变得完全不可知！")
    print("  ※ 反过来：σ→∞ 时 Δx→∞ 但 Δp→0——")
    print("    平面波有确定动量，但'在哪'完全不知道。")
    print("  ※ 生活类比：调焦相机——对焦近处（位置准）看不到远处（动量模糊）。")

# ============================================================
# Demo 4 · 隧道效应——穿墙术是真的
# ============================================================

def demo_tunneling():
    """
    白话：经典世界：球滚不上比它高的坡，就过不去。
    量子世界：粒子有一定概率'穿墙'——即使能量不够！
    这不是粒子获得了额外能量，是波函数在势垒中指数衰减但不为零。
    反直觉：太阳之所以能发光，就是因为质子隧道效应——
    质子的热动能远不够克服库仑排斥，但量子隧穿让聚变得以发生！
    类比：声音穿墙——不是声音有足够能量打破墙，
    是声波在墙中衰减但穿过来了。
    """
    print("\n" + "=" * 64)
    print("  Demo 4 · 量子隧道效应")
    print("=" * 64)

    hbar = 1.0; m = 1.0

    print("\n  矩形势垒：高度 V₀, 宽度 a")
    print("  透射系数：T ≈ exp(−2κa),  κ = √(2m(V₀−E))/ℏ\n")

    V0 = 10.0
    a = 1.0

    # T vs E/V₀
    print(f"  V₀ = {V0}, a = {a}\n")
    print(f"  {'E/V₀':>8s}  {'κ':>8s}  {'T (透射)':>14s}  "
          f"{'1−T (反射)':>12s}")
    print(f"  {'─'*8}  {'─'*8}  {'─'*14}  {'─'*12}")
    pts = []
    for E_frac in [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
        E = E_frac * V0
        kappa = math.sqrt(2 * m * (V0 - E)) / hbar
        T = math.exp(-2 * kappa * a)
        pts.append((E_frac, T))
        print(f"  {E_frac:>8.2f}  {kappa:>8.3f}  {T:>14.6e}  "
              f"{1-T:>12.6e}")

    ascii_scatter(pts, title="透射系数 T vs E/V₀",
                  xlab="E/V₀", ylab="T")

    # T vs 势垒宽度
    print(f"\n  固定 E/V₀ = 0.5, 改变势垒宽度 a：")
    E = 0.5 * V0
    kappa = math.sqrt(2 * m * (V0 - E)) / hbar
    pts_a = []
    for a_val in [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]:
        T = math.exp(-2 * kappa * a_val)
        pts_a.append((a_val, T))
        print(f"    a = {a_val:>5.1f}  →  T = {T:.6e}")
    ascii_scatter(pts_a, title="T vs 势垒宽度 a",
                  xlab="a", ylab="T")

    print("\n  实际应用：")
    print("    • α 衰变：α 粒子隧穿出原子核 → 放射性半衰期")
    print("    • STM 显微镜：电子隧穿真空 → 原子级成像")
    print("    • 太阳核聚变：质子隧穿库仑势垒 → 恒星发光")
    print("    • 闪存 U 盘：电子隧穿氧化层 → 数据存储")

    print("\n  ※ 反直觉：太阳核心温度 ~1.5×10⁷ K，")
    print("    质子动能 ~1 keV，但需要克服 ~500 keV 库仑势垒——")
    print("    没有量子隧穿，太阳根本不会发光！")
    print("  ※ 东大 tradition：隧道二极管（江崎玲於奈，诺贝尔奖 1973）。")

# ============================================================
# Demo 5 · 黑体辐射——量子力学的诞生地
# ============================================================

def planck(lam, T):
    """普朗克黑体辐射谱 B(λ,T) (任意单位，用于形状可视化)"""
    h = 6.626e-34; c = 3e8; k = 1.381e-23
    x = h * c / (lam * k * T)
    if x > 500:
        return 0.0
    return 2 * h * c**2 / lam**5 / (math.exp(x) - 1)

def demo_blackbody():
    """
    白话：加热物体到不同温度，它发的光颜色不同——红色（低温）、
    黄色（中温）、白色（高温）。普朗克发现要解释这个，
    必须假设能量是'一份一份'的（量子化）——量子力学就这么诞生了！
    反直觉：经典物理预言热物体会发出无穷多紫外光（紫外灾难）——
    这显然不可能。普朗克引入'能量量子'才解决了这个矛盾。
    类比：楼梯 vs 斜坡——经典能量像斜坡（任意值），量子能量像楼梯（只能整数级）。
    """
    print("\n" + "=" * 64)
    print("  Demo 5 · 黑体辐射谱（普朗克公式）")
    print("=" * 64)

    print("\n  普朗克公式：B(λ,T) = 2hc²/λ⁵ / (exp(hc/λkT) − 1)")
    print("  维恩位移定律：λ_max · T = 2.898×10⁻³ m·K\n")

    wien = 2.898e-3  # m·K

    for T in [3000, 5000, 5778, 10000]:
        lam_max = wien / T
        # 找峰值（归一化）
        B_max = planck(lam_max, T)
        pts = []
        lam = 50e-9  # 50 nm
        while lam <= 3000e-9:
            B = planck(lam, T)
            if B_max > 0:
                pts.append((lam * 1e9, B / B_max))
            lam += 15e-9
        ascii_scatter(pts, title=f"黑体谱 T={T} K  λ_max={lam_max*1e9:.0f} nm",
                      xlab="λ (nm)", ylab="B/B_max")

    print("  可见光范围：380-750 nm")
    print(f"    T=3000 K  → λ_max={wien/3000*1e9:.0f} nm (红外, 红橙色)")
    print(f"    T=5778 K  → λ_max={wien/5778*1e9:.0f} nm (可见光黄绿, 太阳！)")
    print(f"    T=10000 K → λ_max={wien/10000*1e9:.0f} nm (紫外偏蓝)")

    # 紫外灾难演示
    print("\n  紫外灾难：经典物理 vs 量子物理")
    print("    经典 (Rayleigh-Jeans): B ∝ 1/λ⁴ → λ→0 时 B→∞  (灾难!)")
    print("    量子 (Planck):        λ→0 时 B→0   (正确!)")

    pts_classical = []
    T_sun = 5778
    lam_max = wien / T_sun
    B_max = planck(lam_max, T_sun)
    lam = 50e-9
    while lam <= 2000e-9:
        B_q = planck(lam, T_sun) / B_max
        # Rayleigh-Jeans (归一化到 λ_max 处)
        B_c = (lam_max / lam)**4 * planck(lam_max, T_sun) / B_max
        pts_classical.append((lam * 1e9, min(B_c, 5)))
        lam += 20e-9
    ascii_scatter(pts_classical, title="经典 Rayleigh-Jeans (紫外灾难)",
                  xlab="λ (nm)", ylab="B/B_max")

    print("\n  ※ 反直觉：为什么短波长没有无限多能量？")
    print("    因为高频率的能量量子 E=hf 太大，热激发 '买不起'——")
    print("    就像自动售货机最贵的商品没人买。")
    print("  ※ 普朗克 1900 年提出量子假说——「这是绝望之举」。")
    print("  ※ 生活类比：钢琴——低音弦可以任意小幅度振动，")
    print("    高音弦最小振动幅度就大（能量量子大）。")

# ============================================================
# Demo 6 · 暗物质与暗能量——宇宙的 95% 是看不见的
# ============================================================

def demo_dark_universe():
    """
    白话：星系边缘的恒星转得太快了——快到用可见物质的引力根本拉不住。
    一定有看不见的'暗物质'在帮忙拉。更奇怪的是，宇宙在加速膨胀——
    有一种'暗能量'在推开一切。它们加起来占宇宙的 95%！
    反直觉：你、我、地球、太阳、所有星星——只占宇宙的 5%。
    我们以为是宇宙的主体，其实只是'点缀'。
    类比：晚上看海面——你只看到浪花（可见物质），
    但海水本身（暗物质/暗能量）才是海洋的主体。
    """
    print("\n" + "=" * 64)
    print("  Demo 6 · Kavli IPMU：暗物质与暗能量")
    print("=" * 64)

    print("\n  宇宙构成 (ΛCDM 模型)：")
    print("    ╔══════════════════════════════════════╗")
    print("    ║  暗能量 ████████████████████ 68.3%   ║")
    print("    ║  暗物质 ██████████ 26.8%              ║")
    print("    ║  可见物质 ██ 4.9%                     ║")
    print("    ╚══════════════════════════════════════╝")

    # 星系旋转曲线
    print("\n  星系旋转曲线：v(r) = √(GM(r)/r)")
    print()
    r_virg = 50  # kpc，可见物质范围

    pts_visible = []; pts_dark = []
    for r in range(1, 61):
        # 可见物质：M(r) 渐近常数 → v ~ 1/√r
        M_vis = 100 * (1 - math.exp(-r / 8))
        v_vis = math.sqrt(M_vis / max(r, 0.1))
        pts_visible.append((r, v_vis))
        # 加暗物质：M(r) ∝ r → v ~ 常数（平坦旋转曲线）
        M_dm = M_vis + 8 * r  # 暗物质晕
        v_dm = math.sqrt(M_dm / max(r, 0.1))
        pts_dark.append((r, v_dm))

    ascii_scatter(pts_visible, title="可见物质预言: v ∝ 1/√r (下降！)",
                  xlab="r (kpc)", ylab="v")
    ascii_scatter(pts_dark, title="观测结果 + 暗物质: v ≈ 常数 (平坦！)",
                  xlab="r (kpc)", ylab="v")

    # 暗能量：宇宙加速膨胀
    print("\n  宇宙膨胀历史（示意）：")
    t_vals = [i * 0.2 for i in range(1, 51)]
    pts_nodark = []; pts_dark_e = []
    for t in t_vals:
        # 无暗能量：a(t) ∝ t^(2/3) (减速膨胀)
        a_no = t ** (2/3)
        pts_nodark.append((t, a_no))
        # 有暗能量：后期指数增长 (加速膨胀)
        a_dm = t ** (2/3) * (1 + 0.01 * math.exp(t / 5))
        pts_dark_e.append((t, a_dm))

    ascii_scatter(pts_nodark, title="无暗能量: 减速膨胀",
                  xlab="t", ylab="尺度因子 a")
    ascii_scatter(pts_dark_e, title="有暗能量: 加速膨胀",
                  xlab="t", ylab="尺度因子 a")

    print("\n  Kavli IPMU (东京大学)：")
    print("    • 2011 年 Nobel 物理学奖：暗能量发现 (Perlmutter 等)")
    print("    • Subaru 望远镜巡天：暗物质弱引力透镜观测")
    print("    • XMASS 实验：液氙暗物质直接探测")
    print("    • 理论组：暴胀宇宙学、弦唯象学")

    print("\n  ※ 反直觉：星系边缘恒星的速度 ~220 km/s 和中心附近一样——")
    print("    经典物理说远的应该慢，但暗物质'填平了'速度曲线。")
    print("  ※ 暗能量更诡异：它不是'物质'，是空间本身的性质——")
    print("    空间越多，暗能量越多，推力越强。")
    print("  ※ 生活类比：暗物质像隐形的胶水把星系粘住，")
    print("    暗能量像隐形的弹簧把空间撑开。")

# ============================================================
# Demo 7 · 超导能隙——零电阻的奥秘
# ============================================================

def demo_superconductivity():
    """
    白话：某些金属冷却到极低温，电阻突然变成零——电流永不停歇地流！
    这是因为电子配了对（库珀对），在晶格中'手拉手'穿行，
    没有足够的能量（能隙）就打不散它们。
    反直觉：超导体不是'电阻很小'，是电阻真正为零——
    一个超导环中的电流可以持续几百年不衰减！
    类比：一个人走森林容易被绊倒（电阻），但两个人手拉手就不容易——
    库珀对就是电子'手拉手'。
    """
    print("\n" + "=" * 64)
    print("  Demo 7 · 超导电性与 BCS 能隙")
    print("=" * 64)

    print("\n  BCS 理论：电子通过声子（晶格振动）配对形成库珀对")
    print("  能隙：Δ(T) ≈ Δ₀·tanh(π·√(Tc/T−1)·...)  (T<Tc)")
    print("  临界温度处 Δ → 0，超导消失\n")

    # 超导材料临界温度
    materials = [
        ("Hg (汞)",        4.2,    1911),
        ("Pb (铅)",        7.2,    1913),
        ("Nb₃Sn",         18.5,   1954),
        ("YBa₂Cu₃O₇",     92,     1987),
        ("HgBa₂Ca₂Cu₃O₈", 135,    1993),
        ("LaH₁₀ (高压)",   250,    2019),
    ]
    print(f"  {'材料':>18s}  {'Tc (K)':>8s}  {'发现年份':>8s}  {'类型':>10s}")
    print(f"  {'─'*18}  {'─'*8}  {'─'*8}  {'─'*10}")
    for name, Tc, year in materials:
        sc_type = "高温超导" if Tc > 30 else "常规超导"
        print(f"  {name:>18s}  {Tc:>8.1f}  {year:>8d}  {sc_type:>10s}")

    # 能隙 Δ(T) / Δ₀ vs T/Tc
    Delta0 = 1.0  # 归一化
    Tc = 1.0
    pts = []
    for i in range(1, 100):
        t_ratio = i / 100.0  # T/Tc
        if t_ratio >= 1.0:
            delta = 0.0
        else:
            # 近似 BCS 能隙公式
            arg = max(0, 1 - t_ratio)
            delta = Delta0 * math.tanh(1.74 * math.sqrt(arg))
        pts.append((t_ratio, delta))

    ascii_scatter(pts, title="BCS 能隙 Δ(T)/Δ₀ vs T/Tc",
                  xlab="T/Tc", ylab="Δ/Δ₀")

    # 临界磁场
    print("\n  临界磁场 Bc(T) ≈ Bc(0)·(1 − (T/Tc)²)")
    Bc0 = 1.0
    pts_Bc = []
    for i in range(0, 101):
        t_ratio = i / 100.0
        Bc = Bc0 * (1 - t_ratio**2)
        pts_Bc.append((t_ratio, max(Bc, 0)))
    ascii_scatter(pts_Bc, title="临界磁场 Bc(T)/Bc(0) vs T/Tc",
                  xlab="T/Tc", ylab="Bc/Bc₀")

    print("\n  超导应用：")
    print("    • MRI 医学成像（NbTi 超导磁体）")
    print("    • 磁悬浮列车（山梨中央新干线, 2027 年目标开通）")
    print("    • LHC/CERN 粒子加速器（超导弯转磁体）")
    print("    • 量子计算机（超导量子比特 qubit）")

    print("\n  ※ 反直觉：铜和银——最好的常温导体——在低温下不超导！")
    print("    反而是导电性一般的铝、铅、铌会超导。")
    print("  ※ 东大 tradition：")
    print("    • 京都大学：铜氧化物高温超导发现（1986-87）")
    print("    • 东大物性研：铁基超导研究（2008 至今）")
    print("    • 细野秀雄团队：LaFeAsO 铁基超导 Tc=26K")
    print("  ※ 生活类比：库珀对像一对舞伴——")
    print("    单人容易被人群冲散（有电阻），但舞伴紧紧相随（零电阻）。")

# ============================================================
#  主程序
# ============================================================

DEMOS = [
    ("转动惯量与平行轴定理",             demo_rigid_body),
    ("变压器原理与高压输电",             demo_transformer),
    ("海森堡测不准原理",                 demo_uncertainty),
    ("量子隧道效应",                     demo_tunneling),
    ("黑体辐射与紫外灾难",               demo_blackbody),
    ("Kavli IPMU 暗物质与暗能量",        demo_dark_universe),
    ("超导能隙与 BCS 理论",              demo_superconductivity),
]

def main():
    args = sys.argv[1:]
    if args:
        indices = []
        for a in args:
            try:
                idx = int(a)
                if 1 <= idx <= len(DEMOS):
                    indices.append(idx - 1)
                else:
                    print(f"  ⚠ 跳过无效编号 {idx}（范围 1-{len(DEMOS)}）")
            except ValueError:
                print(f"  ⚠ 忽略非数字参数: {a}")
    else:
        indices = list(range(len(DEMOS)))

    print()
    print("  ╔═══════════════════════════════════════════════════════════╗")
    print("  ║          東京大学 物理演示 · 费曼式可视化                 ║")
    print("  ║          Kavli IPMU · 東大物性研 · ICEC 超导             ║")
    print("  ╚═══════════════════════════════════════════════════════════╝")
    print()
    for i, (name, _) in enumerate(DEMOS):
        print(f"    [{i+1}] {name}")
    print()

    for idx in indices:
        name, func = DEMOS[idx]
        func()

    print("\n" + "=" * 64)
    print("  ✓ 全部演示完成！")
    print("  💡 朝永振一郎（東大, Nobel 1965）：")
    print("     「物理学不是记忆公式，而是理解自然说话的方式。」")
    print("=" * 64 + "\n")

if __name__ == "__main__":
    main()
