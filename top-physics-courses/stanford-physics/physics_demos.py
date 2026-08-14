"""
Stanford 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

课程对应：
  PHYS 61  荣誉力学 (Kleppner/Taylor)
  PHYS 63  荣誉电磁学 (Purcell)
  PHYS 107 热物理 (Schroeder)
  PHYS 130 量子力学 (Griffiths)
  PHYS 131 数学物理方法 (Boas)
  PHYS 370 弦理论入门
  SLAC    粒子加速器物理

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
    """points: [(x, y), ...] -> ASCII 散点/折线图"""
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
    """data: [float, ...] -> ASCII 直方图"""
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
    """水平条形图"""
    mx = max(abs(v) for v in values) or 1
    print(f"\n  ┌ {title} {'─' * 20}┐")
    for lab, val in zip(labels, values):
        bl = int(abs(val) / mx * w)
        sign = '+' if val >= 0 else '-'
        print(f"  │ {lab:<22s} {sign}{'█' * bl:<{w}} {val:.4g}")
    print(f"  └{'─' * (w + 32)}┘")

# ============================================================
# Demo 1 · 有效势能法解轨道问题  (PHYS 61)
# ============================================================

def demo_effective_potential():
    """
    白话：卫星为什么不掉进太阳？因为角动量像一堵'隐形墙'（离心势垒）。
    引力挖坑、离心垒墙，合在一起就是一个'碗'——卫星在碗底绕圈圈。
    反直觉：角动量 L 越大碗越浅、碗底越远；但能量超过碗沿就直接飞走（逃逸）！
    类比：弹珠在碗里转——太慢掉到底（坠毁），太快飞出碗（逃逸太空）。
    """
    print("\n" + "=" * 64)
    print("  Demo 1 · 有效势能 V_eff(r) = L²/(2r²) − 1/r   [G=M=μ=1]")
    print("=" * 64)

    for L in [0.3, 0.5, 0.8]:
        pts = []
        r = 0.15
        while r <= 6.0:
            v = L * L / (2 * r * r) - 1.0 / r
            pts.append((r, v))
            r += 0.08
        ascii_scatter(pts, title=f"有效势能  L={L}")

    # 解析求圆形轨道半径
    for L in [0.3, 0.5, 0.8]:
        r_circ = L * L          # dV/dr=0 -> r = L²
        v_min = L*L/(2*r_circ**2) - 1/r_circ
        print(f"  L={L}: 稳定圆轨道半径 r₀ = L² = {r_circ:.3f},  "
              f"V_min = {v_min:.4f}")

    print("\n  ※ 反直觉：L 越大，轨道越远（r₀ = L²），但势阱越浅——"
          "更容易被扰动踢飞！")
    print("  ※ 生活类比：碗转得越快弹珠越往外靠，但碗壁也越浅。")

# ============================================================
# Demo 2 · 科里奥利力——旋转参照系中的弯曲轨迹  (PHYS 61)
# ============================================================

def demo_coriolis():
    """
    白话：站在旋转的转盘上直直地扔球，球却弯了！不是球真的弯了，
    是你在转，参照系在转，于是多出了一个'假力'叫科里奥利力。
    反直觉：北半球台风总是逆时针旋转——不是因为地球自转方向，
    而是因为科里奥利力让气流偏右（北半球）。
    类比：在旋转木马上传球给对面的朋友，球总往旁边飘。
    """
    print("\n" + "=" * 64)
    print("  Demo 2 · 科里奥利力轨迹 (旋转参照系)")
    print("=" * 64)

    omega = 1.0; v0 = 1.0; dt = 0.01; t_end = 6.0
    # 数值积分：ẍ = 2ωẏ + ω²x,  ÿ = −2ωẋ + ω²y
    x, y, vx, vy = 0.0, 0.0, v0, 0.0
    t = 0.0
    traj = []
    while t <= t_end:
        traj.append((x, y))
        ax = 2 * omega * vy + omega * omega * x
        ay = -2 * omega * vx + omega * omega * y
        vx += ax * dt; vy += ay * dt
        x += vx * dt; y += vy * dt
        t += dt
    ascii_scatter(traj, title="科里奥利轨迹（旋转系中看自由粒子）",
                  xlab="x", ylab="y")

    # 惯性系中的直线 vs 旋转系中的螺旋
    print("\n  惯性系视角：球走直线")
    print("  旋转系视角：球走螺旋（同时受科里奥利力 + 离心力）")
    print(f"\n  科里奥利加速度 = 2ω × v   (ω={omega}, v₀={v0})")
    print(f"  最大偏转 ≈ 2ωv₀ = {2*omega*v0:.2f} m/s²")

    print("\n  ※ 反直觉：北半球射出的炮弹会偏右——一战中英军常打到自己人！")
    print("  ※ 生活类比：洗手池水涡方向不是科里奥利力决定的（太弱了），"
          "但台风确实是！")

# ============================================================
# Demo 3 · 相对论电磁学——E 和 B 是同一个东西  (PHYS 63)
# ============================================================

def demo_relativistic_em():
    """
    白话：一个静止电荷只产生电场。但如果你跑过去看它——它就有磁场了！
    电场和磁场不是两种东西，是同一个电磁场在不同参照系中的'投影'。
    反直觉：磁力本质上就是电力的相对论修正——如果光速无限大，磁力就消失了！
    类比：一个圆柱体从正面看是长方形，侧面看是圆——它们是同一个物体的不同视角。
    """
    print("\n" + "=" * 64)
    print("  Demo 3 · 相对论电磁场变换 (Purcell 电动力学)")
    print("=" * 64)

    c = 1.0  # 自然单位
    print("\n  场变换公式（沿 x 方向以速度 v 运动）：")
    print("    E'⊥ = γ(E⊥ + v × B)")
    print("    B'⊥ = γ(B⊥ − v × E/c²)")
    print()

    # 电荷静止系：只有 E = q/(4πε₀r²)，B = 0
    # 以速度 v 运动：产生磁场 B' = −γv×E/c²
    betas = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]
    gamma_vals = []
    e_ratios = []
    for beta in betas:
        gamma = 1.0 / math.sqrt(1 - beta**2)
        gamma_vals.append(gamma)
        e_ratios.append(gamma)  # 垂直方向电场增强 γ 倍
        print(f"  β = v/c = {beta:.2f}  →  γ = {gamma:.4f}  "
              f"  E'⊥/E = {gamma:.3f}  B'/E = {gamma*beta/c**2:.4f}")

    print()
    ascii_bar(gamma_vals, [f"β={b:.2f}" for b in betas],
              title="γ 因子 vs 速度")

    print("\n  ※ 反直觉：β=0.99 时电场强度增强 7 倍——高速运动电荷的"
          "电场被'压缩'到垂直方向！")
    print("  ※ 生活类比：手电筒前进时光看起来更亮（相对论束效应）。")

# ============================================================
# Demo 4 · 量子叠加与测量坍缩  (PHYS 130)
# ============================================================

def demo_superposition_collapse():
    """
    白话：量子粒子可以同时'既在这里又在那里'——直到你去看（测量）它的瞬间，
    它突然'决定'只在一个地方。这叫波函数坍缩。
    反直觉：测量结果不是随机的——概率由 |振幅|² 决定（玻恩规则），
    但每次测量结果都是确定的（0 或 1），不是模糊的。
    类比：抛硬币在空中旋转时既不是正面也不是反面（叠加态），
    落地瞬间'决定'了——但量子硬币真的是同时两面朝上！
    """
    print("\n" + "=" * 64)
    print("  Demo 4 · 量子叠加 |ψ⟩ = cosθ|0⟩ + sinθ|1⟩ 与玻恩规则")
    print("=" * 64)

    theta = math.pi / 5  # 倾斜角度
    alpha = math.cos(theta)
    beta = math.sin(theta)
    p0 = alpha ** 2
    p1 = beta ** 2
    print(f"\n  |ψ⟩ = {alpha:.4f}|0⟩ + {beta:.4f}|1⟩")
    print(f"  P(|0⟩) = |α|² = {p0:.4f}   P(|1⟩) = |β|² = {p1:.4f}")
    print()

    for N in [10, 100, 1000, 10000]:
        count0 = sum(1 for _ in range(N) if random.random() < p0)
        freq0 = count0 / N
        print(f"  N={N:>6d} 次测量: P(0)_测量 = {freq0:.4f}  "
              f"(理论 {p0:.4f}, 误差 {abs(freq0-p0):.4f})")

    # 模拟坍缩序列
    print("\n  连续 20 次测量序列（1=|1⟩, 0=|0⟩）：")
    seq = "".join("1" if random.random() < p1 else "0" for _ in range(20))
    print(f"    {' '.join(seq)}")
    print(f"    → 每次测量后波函数坍缩为确定的 |0⟩ 或 |1⟩")

    print("\n  ※ 反直觉：两个测量之间的量子粒子恢复叠加态——"
          "前提是中间没有观测它！")
    print("  ※ 生活类比：薛定谔的猫——在你开箱子前，猫真的是又死又活。")

# ============================================================
# Demo 5 · 热机效率与 PV 图  (PHYS 107)
# ============================================================

def demo_heat_engine():
    """
    白话：热机从热的地方吸热，做功，把余热扔到冷的地方。效率就是：
    你用掉的能量 / 你吸入的能量。卡诺证明了——效率有上限，只取决于温差！
    反直觉：即使没有摩擦、没有损耗，热机效率也到不了 100%！
    除非冷端是绝对零度（−273°C）。
    类比：水力发电——水从高处（热）流到低处（冷）途中推水轮机做功。
    水不会全部变成电，一部分必然流到下游。
    """
    print("\n" + "=" * 64)
    print("  Demo 5 · 卡诺热机效率 η = 1 − Tc/Th")
    print("=" * 64)

    T_h = 600  # 热源温度 (K)
    T_c = 300  # 冷源温度 (K)
    eta_max = 1 - T_c / T_h

    print(f"\n  热源 T_h = {T_h} K  冷源 T_c = {T_c} K")
    print(f"  卡诺效率上限 η_max = 1 − {T_c}/{T_h} = {eta_max:.2%}")
    print()

    # 不同温差下的效率
    ratios = [0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]
    etas = [1 - r for r in ratios]
    print("  冷热比 Tc/Th  →  效率：")
    for r, e in zip(ratios, etas):
        print(f"    {r:.2f}        →  {e:.1%}")
    print(f"    要 100% 效率，需要 Tc = 0 K（绝对零度，不可达）")

    # PV 图：卡诺循环（等温+绝热）
    pts = []
    # 等温膨胀 (Th): PV = const
    V = 1.0
    while V <= 3.0:
        P = 3.0 / V
        pts.append((V, P))
        V += 0.05
    # 绝热膨胀: PV^γ = const (γ=5/3)
    V = 3.0
    while V <= 4.5:
        P = 1.0 * (3.0 / V) ** (5/3)
        pts.append((V, P))
        V += 0.05
    # 等温压缩 (Tc): PV = const (lower)
    V = 4.5
    while V >= 1.5:
        P = 1.5 / V
        pts.append((V, P))
        V -= 0.05
    # 绝热压缩回到起点
    V = 1.5
    while V >= 1.0:
        P = 1.0 * (1.5 / V) ** (5/3)
        pts.append((V, P))
        V -= 0.05
    ascii_scatter(pts, title="卡诺循环 PV 图 (等温↔绝热)",
                  xlab="V (体积)", ylab="P (压强)")

    print("\n  ※ 反直觉：蒸汽机效率只有 ~40%，不是工程师无能——是宇宙定律！")
    print("  ※ 生活类比：用温差发电的效率永远不如直接用电——熵增不可逆。")

# ============================================================
# Demo 6 · 贝塞尔函数与勒让德多项式  (PHYS 131)
# ============================================================

def legendre(n, x):
    """P_n(x) 递推"""
    if n == 0: return 1.0
    if n == 1: return float(x)
    p0, p1 = 1.0, float(x)
    for k in range(1, n):
        p2 = ((2 * k + 1) * x * p1 - k * p0) / (k + 1)
        p0, p1 = p1, p2
    return p1

def bessel_j0(x):
    """J₀(x) 级数展开"""
    s = 0.0; term = 1.0; k = 0
    x2 = (x / 2) ** 2
    while abs(term) > 1e-14 and k < 80:
        s += term; k += 1
        term *= -x2 / (k * k)
    return s

def bessel_j1(x):
    """J₁(x) 级数展开"""
    s = 0.0; term = x / 2.0; k = 0
    x2 = (x / 2) ** 2
    while abs(term) > 1e-14 and k < 80:
        s += term; k += 1
        term *= -x2 / (k * (k + 1))
    return s

def demo_special_functions():
    """
    白话：贝塞尔函数是圆盘上波动的'指纹'——鼓面振动、天线辐射都用它。
    勒让德多项式是球面上函数的'乐高积木'——电子轨道形状就是它们的组合。
    反直觉：这些看起来奇怪的函数其实是'最自然'的——它们自然出现在有
    圆形/球形对称性的问题中，就像 sin/cos 出现在直线上一样。
    类比：sin/cos 是一维波动的'字母'，贝塞尔/勒让德是二维/三维的'字母'。
    """
    print("\n" + "=" * 64)
    print("  Demo 6 · 贝塞尔函数 J₀(x) 与勒让德多项式 Pₙ(x)")
    print("=" * 64)

    # 贝塞尔 J₀
    pts = [(x / 10, bessel_j0(x / 10)) for x in range(0, 200)]
    ascii_scatter(pts, title="贝塞尔函数 J₀(x)", xlab="x", ylab="J₀")
    j0_zeros_est = []
    prev = bessel_j0(0.1)
    for i in range(1, 400):
        x = i * 0.1
        curr = bessel_j0(x)
        if prev > 0 and curr <= 0:
            j0_zeros_est.append(x)
        prev = curr
    print(f"  J₀ 零点（鼓面共振频率）：{[f'{z:.2f}' for z in j0_zeros_est[:5]]}")
    print(f"  → 鼓面模式的频率比 = 零点平方比（不是整数比！）")

    # 勒让德多项式
    for n in [0, 1, 2, 3, 4]:
        pts = [(x / 20, legendre(n, x / 20)) for x in range(-20, 21)]
        ascii_scatter(pts, title=f"勒让德 P{n}(x)",
                      xlab="x", ylab=f"P{n}")

    print("\n  P₂(x) = (3x²−1)/2  → 'd 轨道'形状")
    print("  P₃(x) = (5x³−3x)/2 → 'f 轨道'形状")
    print("\n  ※ 反直觉：J₀ 的零点不是 π 的整数倍——"
          "鼓的泛音不是和谐音程（所以鼓声不如琴声悦耳）！")
    print("  ※ 生活类比：勒让德多项式像折纸——每增加一阶多一个褶皱。")

# ============================================================
# Demo 7 · SLAC 粒子加速器——为什么用对撞机？  (SLAC)
# ============================================================

def demo_slac_kinematics():
    """
    白话：要探测物质内部，就得用高速粒子去'撞击'它。但如果你用粒子打静止靶，
    大部分能量白白浪费在让碎片向前飞——只有对撞才能把能量全部用上！
    反直觉：把加速器能量翻倍，打静止靶的'有效能量'只增加 √2 倍，
    但在对撞机中增加 2 倍——这就是为什么 SLAC 建了直线对撞机！
    类比：两辆卡车对撞 vs 一辆卡车撞墙——对撞的破坏力大得多。
    """
    print("\n" + "=" * 64)
    print("  Demo 7 · SLAC 对撞机 vs 固定靶：质心能量 √s")
    print("=" * 64)

    m_e = 0.511    # MeV (电子质量)
    m_p = 938.3    # MeV (质子质量)

    print(f"\n  电子质量 m_e c² = {m_e} MeV")
    print(f"  质子质量 m_p c² = {m_p} MeV\n")

    print("  电子打静止质子靶 (固定靶)：")
    print("    s = m_e² + m_p² + 2 m_p E_beam")
    print("    √s ≈ √(2 m_p E_beam)  (高能极限)\n")

    print("  电子-正电子对撞 ( collider )：")
    print("    √s = 2 E_beam\n")

    print(f"  {'E_beam (GeV)':>14s}  {'固定靶 √s (GeV)':>18s}  "
          f"{'对撞 √s (GeV)':>16s}  {'比值':>8s}")
    print(f"  {'─'*14}  {'─'*18}  {'─'*16}  {'─'*8}")

    coll_pts = []
    ft_pts = []
    for E_gev in [1, 5, 10, 50, 100, 500, 1000]:
        E_mev = E_gev * 1000
        # 固定靶 (e on proton at rest)
        s_ft = m_e**2 + m_p**2 + 2 * m_p * E_mev
        sqrt_s_ft = math.sqrt(s_ft) / 1000  # back to GeV
        # 对撞 (e+ e-)
        sqrt_s_col = 2 * E_gev
        ratio = sqrt_s_col / sqrt_s_ft
        print(f"  {E_gev:>14d}  {sqrt_s_ft:>18.2f}  "
              f"{sqrt_s_col:>16d}  {ratio:>8.1f}")
        coll_pts.append((E_gev, sqrt_s_col))
        ft_pts.append((E_gev, sqrt_s_ft))

    ascii_scatter(coll_pts + ft_pts, title="质心能量 √s vs 束流能量",
                  xlab="E_beam (GeV)", ylab="√s (GeV)")

    print("\n  ※ 反直觉：1000 GeV 电子打固定靶，有效能量仅 43 GeV——"
          "浪费了 95.7%！")
    print("  ※ SLAC 的 SLC 直线对撞机就是为此而生——"
          "把 e⁺e⁻ 对头撞，50 GeV × 2 = 100 GeV 全部有效。")
    print("  ※ 生活类比：两列火车对撞比一列撞墙恐怖得多——"
          "相对速度翻倍，能量四倍。")

# ============================================================
#  主程序
# ============================================================

DEMOS = [
    ("有效势能法解轨道 (PHYS 61)",        demo_effective_potential),
    ("科里奥利力轨迹 (PHYS 61)",          demo_coriolis),
    ("相对论电磁场变换 (PHYS 63)",         demo_relativistic_em),
    ("量子叠加与测量坍缩 (PHYS 130)",      demo_superposition_collapse),
    ("卡诺热机效率与 PV 图 (PHYS 107)",    demo_heat_engine),
    ("贝塞尔与勒让德函数 (PHYS 131)",      demo_special_functions),
    ("SLAC 对撞机运动学 (SLAC)",          demo_slac_kinematics),
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
    print("  ║         Stanford 物理演示 · 费曼式可视化                  ║")
    print("  ║         SLAC · PHYS 41–131 · PHYS 370                    ║")
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
    print("  💡 费曼说：「如果你不能向一个 12 岁的孩子解释清楚，")
    print("     那你自己也没有真正理解。」")
    print("=" * 64 + "\n")

if __name__ == "__main__":
    main()
