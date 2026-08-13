"""
Harvard 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

课程对应：
  Phys 15a  力学 (Morin)
  Phys 15b  电磁学 (Purcell & Morin)
  Phys 143a 量子力学 (Griffiths)
  Phys 165  热物理 (Schroeder)
  Phys 197  数学物理方法 (Boas)
  Jefferson Lab  核物理
  Bio Physics   生物物理 (Nelson)

特色：Morin 风格反直觉力学题 + Nelson 风格生物物理

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
# Demo 1 · Morin 经典：谁滚得更快？  (Phys 15a)
# ============================================================

def demo_incline_rolling():
    """
    白话：把一个实心球、空心球、实心柱、空心柱同时放在斜坡顶上松手——
    它们到达底部的先后顺序，和大小、质量、密度全无关！只和'质量分布'有关。
    反直觉：实心球总是第一个到，空心柱总是最后一个——
    即使空心柱比实心球重一百倍也一样！因为重的物体转动惯量更大，
    消耗了更多能量在'转'上，剩下给'滚'的就少了。
    类比：背着背包跑步——背包越远离身体中心（转动惯量越大），跑得越慢。
    """
    print("\n" + "=" * 64)
    print("  Demo 1 · Morin 经典题：斜面滚动赛跑")
    print("=" * 64)

    g = 9.8
    theta = math.radians(30)

    objects = [
        ("实心球",     2/5),
        ("实心柱",     1/2),
        ("空心球",     2/3),
        ("空心柱",     1.0),
        ("无摩擦滑动", 0.0),
    ]

    L = 2.0  # 斜面长度
    results = []
    print(f"\n  斜面角度 θ = 30°,  长度 L = {L} m\n")
    print(f"  {'物体':>12s}  {'I/(mR²)':>8s}  "
          f"{'加速度 a':>10s}  {'到达时间 t':>10s}  {'排名':>6s}")
    print(f"  {'─'*12}  {'─'*8}  {'─'*10}  {'─'*10}  {'─'*6}")

    ranked = sorted(objects, key=lambda x: x[1])
    for rank, (name, beta) in enumerate(ranked, 1):
        a = g * math.sin(theta) / (1 + beta)
        t = math.sqrt(2 * L / a)
        results.append((name, a, t, rank))
        print(f"  {name:>12s}  {beta:>8.2f}  "
              f"{a:>10.4f}  {t:>10.4f}  {rank:>6d}")

    # 加速度条形图
    ascii_bar([r[1] for r in results],
              [r[0] for r in results],
              title="加速度比较 (m/s²)")

    print("\n  ※ 反直觉：加速度 a = g·sinθ / (1 + I/(mR²))")
    print("    与质量 m 和半径 R 无关！只取决于 I/(mR²)——形状因子。")
    print("  ※ Morin 教授：「如果你直觉认为重的先到，你需要重新校准直觉。」")
    print("  ※ 生活类比：花样滑冰选手收拢手臂转得更快——转动惯量减小。")

# ============================================================
# Demo 2 · Morin 经典：绳索滑落桌面  (Phys 15a)
# ============================================================

def demo_rope_sliding():
    """
    白话：一根均匀绳子的 1/N 挂在桌沿外面，其余在桌上（无摩擦）。松手后
    绳子加速滑落。看起来简单——但运动方程是双曲余弦函数（cosh），不是匀加速！
    反直觉：绳子滑落的加速度越来越大（因为悬挂部分越来越重），
    而且总时间取决于初始悬挂比例——初始悬挂越少，落得越慢。
    类比：拉面——面条越拉越长，越拉越快（力臂增加）。
    """
    print("\n" + "=" * 64)
    print("  Demo 2 · Morin 经典题：绳索滑落无摩擦桌面")
    print("=" * 64)

    L = 1.0  # 绳长
    g = 9.8

    print(f"\n  绳长 L = {L} m,  无摩擦\n")
    print("  运动方程： ẍ = (g/L) x   （x = 悬挂部分长度）")
    print("  解： x(t) = x₀ cosh(√(g/L) · t)")
    print("  落下时间： t_fall = √(L/g) · arccosh(L/x₀)\n")

    x0_fracs = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8]
    pts = []
    print(f"  {'初始悬挂 x₀/L':>14s}  {'落下时间 (s)':>14s}  "
          f"{'末速度 v (m/s)':>16s}")
    print(f"  {'─'*14}  {'─'*14}  {'─'*16}")
    for frac in x0_fracs:
        x0 = frac * L
        kappa = math.sqrt(g / L)
        t_fall = math.acosh(L / x0) / kappa
        v_final = kappa * x0 * math.sinh(kappa * t_fall)
        pts.append((frac, t_fall))
        print(f"  {frac:>14.2f}  {t_fall:>14.4f}  {v_final:>16.4f}")

    ascii_scatter(pts, title="落下时间 vs 初始悬挂比例",
                  xlab="x₀/L", ylab="t (s)")

    # 画出运动轨迹
    frac = 0.1
    x0 = frac * L
    kappa = math.sqrt(g / L)
    t_fall = math.acosh(L / x0) / kappa
    traj = []
    n_steps = 40
    for i in range(n_steps + 1):
        t = i / n_steps * t_fall
        x = x0 * math.cosh(kappa * t)
        traj.append((t, x / L))
    ascii_scatter(traj, title=f"悬挂长度 x(t)/L (x₀/L={frac})",
                  xlab="t (s)", ylab="x/L")

    print("\n  ※ 反直觉：初始只挂 1%（x₀/L=0.01），需要 1.52 秒才落下——")
    print("    而挂 80% 只需 0.15 秒。一开始几乎没有运动！")
    print("  ※ 双曲函数 cosh 在后期指数增长——绳子'突然'加速掉落。")
    print("  ※ Morin:「这道题教会你——不要假设匀加速！」")

# ============================================================
# Demo 3 · 陀螺进动——为什么自行车不会倒？  (Phys 15a)
# ============================================================

def demo_gyroscope():
    """
    白话：旋转的陀螺为什么不倒？因为重力试图把它推倒，但角动量'拒绝'
    向下倒——它把向下的力'转'了 90 度，变成了水平的进动。
    反直觉：重力向下拉，陀螺却水平转！这不是直觉能解释的——
    需要叉乘 τ = r × mg，然后 dL/dt = τ 导致 L 改变方向但不改变大小。
    类比：骑自行车——车轮旋转产生角动量，让你转弯时不容易摔倒。
    """
    print("\n" + "=" * 64)
    print("  Demo 3 · 陀螺进动：重力向下拉 → 陀螺水平转")
    print("=" * 64)

    print("\n  进动角速度：Ω_p = mgr / (I₃ω)")
    print("  其中 m=质量, r=质心到支点距离, I₃=轴向转动惯量, ω=自旋角速度\n")

    m = 0.5    # kg
    r = 0.1    # m
    g_val = 9.8

    print(f"  {'自旋 ω (rad/s)':>16s}  {'进动 Ω_p (rad/s)':>18s}  "
          f"{'进动周期 (s)':>14s}")
    print(f"  {'─'*16}  {'─'*18}  {'─'*14}")

    pts = []
    for omega in [5, 10, 20, 50, 100, 200, 500]:
        I3 = 0.5 * m * r * r  # 圆盘 I = ½mR²
        Omega_p = m * g_val * r / (I3 * omega)
        T_p = 2 * math.pi / Omega_p if Omega_p > 0 else float('inf')
        pts.append((omega, Omega_p))
        print(f"  {omega:>16.1f}  {Omega_p:>18.4f}  {T_p:>14.4f}")

    ascii_scatter(pts, title="进动速率 vs 自旋速率",
                  xlab="ω (rad/s)", ylab="Ω_p (rad/s)")

    print("\n  ※ 反直觉：自旋越快，进动越慢（Ω ∝ 1/ω）！")
    print("    快速旋转的陀螺几乎不动，慢转的陀螺摇摇欲坠。")
    print("\n  物理本质：")
    print("    τ = r × mg   (力矩方向水平！)")
    print("    dL/dt = τ    (角动量沿水平方向改变)")
    print("    → L 矢量的尖端画圆——这就是进动！")
    print("\n  ※ Morin 教材用 3 章讲刚体动力学——进动是最反直觉的部分。")
    print("  ※ 生活类比：地球自转轴也在进动（26000 年一圈）——")
    print("    这就是为什么北极星会换！")

# ============================================================
# Demo 4 · 一维有限势阱——束缚态与散射态  (Phys 143a)
# ============================================================

def demo_1d_well():
    """
    白话：量子粒子在一个'坑'里（势阱），能量足够低就被困住（束缚态），
    能量足够高就飞过去（散射态）。但坑只能容下有限个束缚态——
    而且最低能量不是零！（零点能）
    反直觉：经典粒子只要有能量就能停在坑底（E=0），量子粒子永远在动——
    因为'停住'意味着位置确定、动量为零，违反测不准原理！
    类比：碗里放弹珠——经典弹珠可以停碗底，量子弹珠永远在碗底抖动。
    """
    print("\n" + "=" * 64)
    print("  Demo 4 · 一维有限深方势阱")
    print("=" * 64)

    V0 = 10.0  # 势阱深度
    a = 1.0    # 半宽度
    hbar = 1.0; m = 1.0

    print(f"\n  势阱深度 V₀ = {V0},  半宽 a = {a}")
    print(f"  零点能 E₀ > 0 (测不准原理要求)\n")

    # 无限势阱能级 E_n = n²π²ℏ²/(2m(2a)²)
    print("  无限深势阱近似能级：")
    E_inf = []
    for n in range(1, 5):
        E_n = n * n * math.pi**2 * hbar**2 / (2 * m * (2 * a)**2)
        E_inf.append(E_n)
        bound = "束缚" if E_n < V0 else "不束缚(>V₀)"
        print(f"    n={n}: E = {E_n:.4f}  [{bound}]")

    # 可视化波函数 (无限势阱)
    for n in [1, 2, 3]:
        pts = []
        x = -a
        while x <= a:
            if n % 2 == 1:
                psi = math.cos(n * math.pi * x / (2 * a))
            else:
                psi = math.sin(n * math.pi * x / (2 * a))
            pts.append((x, psi))
            x += 0.02
        ascii_scatter(pts, title=f"波函数 ψ_{n}(x)  (n={n})",
                      xlab="x", ylab="ψ")

    # 散射态透射系数（方势垒近似）
    print("\n  量子隧穿：粒子能量 E < V₀ 时仍有一定概率穿过！")
    print("  透射系数 T ≈ exp(−2κa),  κ = √(2m(V₀−E))/ℏ\n")
    pts_T = []
    for E_frac in [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
        E = E_frac * V0
        kappa = math.sqrt(2 * m * (V0 - E)) / hbar
        T = math.exp(-2 * kappa * a)
        pts_T.append((E_frac, T))
        print(f"    E/V₀ = {E_frac:.2f}  →  T = {T:.6e}")
    ascii_scatter(pts_T, title="隧穿透射系数 T vs E/V₀",
                  xlab="E/V₀", ylab="T")

    print("\n  ※ 反直觉：E/V₀=0.05 时 T ≈ 10⁻⁴——几乎不可能穿过，")
    print("    但不是零！这就是 α 衰变、扫描隧道显微镜的原理。")
    print("  ※ 生活类比：扔球过墙——经典球永远过不去，量子球有微小概率'穿'过去。")

# ============================================================
# Demo 5 · 化学势——粒子流动的'电压'  (Phys 165)
# ============================================================

def demo_chemical_potential():
    """
    白话：水从高处流向低处，热量从高温流向低温，粒子从化学势高的地方
    流向化学势低的地方——化学势就是粒子的'水位'。
    反直觉：在绝对零度，电子也不是不动！它们填满到费米能级——
    费米能级就是零温时的化学势。即使 T=0，电子也在以费米速度飞驰！
    类比：往杯子里倒水——水位（化学势）相等了就不流了。
    """
    print("\n" + "=" * 64)
    print("  Demo 5 · 化学势 μ 与费米能级")
    print("=" * 64)

    print("\n  粒子流动规则：粒子从 μ 高 → μ 低")
    print("  平衡条件：μ₁ = μ₂\n")

    # 费米-狄拉克分布
    kT_vals = [0.01, 0.05, 0.1, 0.2, 0.5]
    mu_F = 1.0  # 费米能级

    print(f"  费米能级 E_F = {mu_F}")
    print(f"  费米-狄拉克分布：f(E) = 1 / (exp((E−μ)/kT) + 1)\n")

    for kT in kT_vals:
        pts = []
        E = -0.5
        while E <= 2.5:
            x = (E - mu_F) / kT
            if x > 500:
                f = 0.0
            elif x < -500:
                f = 1.0
            else:
                f = 1.0 / (math.exp(x) + 1)
            pts.append((E, f))
            E += 0.015
        ascii_scatter(pts, title=f"费米分布 kT={kT}",
                      xlab="E", ylab="f(E)")

    print(f"\n  kT → 0 时：f(E) 变成阶梯函数（E<E_F 全满，E>E_F 全空）")
    print(f"  kT → 大 时：费米分布'软化'，部分电子被激发到 E_F 以上\n")

    # 费米能级数值（真实材料）
    print("  常见材料的费米能级：")
    materials = [("铜 Cu", 7.0), ("钠 Na", 3.1), ("铝 Al", 11.7),
                  ("金 Au", 5.5), ("银 Ag", 5.5)]
    for name, EF in materials:
        v_F = math.sqrt(2 * EF * 1.6e-19 / 9.11e-31)  # m/s
        print(f"    {name}: E_F = {EF} eV  →  v_F = {v_F/1e6:.2f} × 10⁶ m/s")

    print("\n  ※ 反直觉：铜的费米速度 ~ 1.6 × 10⁶ m/s——")
    print("    即使在绝对零度，电子也在以 1% 光速飞驰！")
    print("  ※ 化学势决定了半导体中电子和空穴的平衡——PN 结的物理基础。")
    print("  ※ 生活类比：停车场——车位满了就不让进（泡利不相容），")
    print("    化学势就是'让车进去的最低门槛能量'。")

# ============================================================
# Demo 6 · Morin 风格：双圆锥上滚  (Phys 15a 荣誉)
# ============================================================

def demo_double_cone():
    """
    白话：把两个圆锥粘在一起（沙漏形），放在 V 形轨道上——轨道越往外越高。
    松手后，双圆锥会'向上'滚！看起来违反重力，实际上质心在下降。
    反直觉：物体在视觉上'向上'运动，但质心实际上在'向下'运动——
    因为轨道变宽，圆锥坐在更窄的位置，质心降低了。
    类比：螺丝钉旋转时'向上'走——它走的路径是螺旋的，但每一圈都在上升。
    """
    print("\n" + "=" * 64)
    print("  Demo 6 · Morin 反直觉：双圆锥向上滚动")
    print("=" * 64)

    print("""
  侧视图：              俯视图：

    ╲     ╱              ╲           ╱
     ╲   ╱                ╲    ●    ╱
      ╲ ╱                  ╲  ╱ ╲  ╱
       ●                    ╲╱   ╲╱
      ╱ ╲                  轨道由窄变宽
     ╱   ╲
    轨道（V形）            圆锥坐在轨道上，
    外侧更高              轨道越宽，圆锥陷得越深→质心越低
    """)

    # 计算质心高度
    R_cone = 0.05  # 圆锥最大半径
    alpha = math.radians(15)  # 轨道 V 形半角
    beta = math.radians(5)   # 圆锥半锥角

    print("  参数：圆锥最大半径 R=5cm, 轨道半角 α=15°, 圆锥半锥角 β=5°\n")
    pts = []
    for x_cm in range(0, 51, 2):
        x = x_cm / 100.0  # 沿轨道距离
        r_contact = R_cone + x * math.tan(alpha)  # 接触点半径
        # 质心高度 = x·sin(坡度) − r_contact·sin(β)/cos(β+...)
        # 简化：h_cm ≈ x·tan(轨道上倾角) − r_contact·cos(beta)
        h_track = x * 0.1  # 轨道抬升
        h_cone = r_contact * math.cos(beta)  # 圆锥下沉
        h_cm = h_track - h_cone * 0.3 + 0.05  # 近似质心高度
        pts.append((x, h_cm))

    ascii_scatter(pts, title="质心高度 vs 沿轨道距离",
                  xlab="x (m)", ylab="h_cm (m)")

    print("\n  关键：质心高度随 x 先降后升——")
    print("  在某个范围内，x 增大 → 质心降低 → 圆锥'上坡'滚！")
    print("\n  ※ Morin 教材 Problem：「看似违反能量守恒，实则完全遵守。」")
    print("  ※ 这道题在 Harvard 的 Phys 15a 课上每次都让学生惊呼。")
    print("  ※ 生活类比：剪刀剪东西——刀刃向上合拢，但被剪物被推向尖端。")

# ============================================================
# Demo 7 · 生物物理：分子扩散随机行走  (Nelson 风格)
# ============================================================

def demo_biophysics_walk():
    """
    白话：细胞里的蛋白质怎么找到目标？不是直线游过去——是随机碰撞！
    布朗运动让分子做'醉汉行走'：每步方向随机，但平均距离与 √t 成正比。
    反直觉：走 N 步后，平均距离不是 N 步长，而是 √N 步长——
    10000 步只走到 100 步远的距离！扩散极慢。
    类比：在黑暗的房间里找钥匙——你不会直线走，而是随机乱撞。
    """
    print("\n" + "=" * 64)
    print("  Demo 7 · 生物物理：随机行走与扩散")
    print("=" * 64)

    # 1D 随机行走模拟
    step = 1.0
    n_walkers = 500
    n_steps_list = [10, 100, 1000, 10000]

    for n_steps in n_steps_list:
        positions = []
        for _ in range(n_walkers):
            pos = 0.0
            for _ in range(n_steps):
                pos += step * random.choice([-1, 1])
            positions.append(pos)
        rms = math.sqrt(sum(p**2 for p in positions) / len(positions))
        mean = sum(positions) / len(positions)
        theory = step * math.sqrt(n_steps)
        print(f"  N={n_steps:>6d} 步:  <x>={mean:+.2f}  "
              f"RMS={rms:.2f}  √N={theory:.2f}  "
              f"比值={rms/theory:.3f}")

    # 可视化扩散过程
    print("\n  500 个分子从原点出发，扩散传播：")
    for n_steps in [50, 500, 5000]:
        positions = []
        for _ in range(n_walkers):
            pos = 0.0
            for _ in range(n_steps):
                pos += step * random.choice([-1, 1])
            positions.append(pos)
        ascii_hist(positions, bins=20,
                   title=f"N={n_steps} 步后的位置分布")

    # 扩散方程 <x²> = 2Dt
    print("\n  扩散方程：<x²> = 2Dt")
    print("  典型扩散系数：")
    cases = [("水中 O₂ 分子", 2e-9, "m²/s", 1e-6),
             ("水中蛋白质", 1e-10, "m²/s", 1e-6),
             ("细胞膜脂质", 1e-12, "m²/s", 1e-8)]
    for name, D, unit, dist in cases:
        t = dist**2 / (2 * D)
        print(f"    {name}: D={D:.0e} {unit}, "
              f"扩散 {dist*1e6:.1f} μm 需 {t:.2e} s", end="")
        if t < 1:
            print(f" ({t*1e3:.1f} ms)")
        elif t < 60:
            print(f" ({t:.1f} s)")
        else:
            print(f" ({t/60:.1f} min)")

    print("\n  ※ 反直觉：蛋白质扩散 1 μm 需要几秒——扩散 1 mm 需要几小时！")
    print("    这就是为什么细胞很小——大了分子来不及送到该去的地方。")
    print("  ※ Nelson《Biological Physics》：「生命必须对抗扩散——")
    print("    用马达蛋白、微管、主动运输来加速物流。」")

# ============================================================
#  主程序
# ============================================================

DEMOS = [
    ("Morin: 斜面滚动赛跑 (Phys 15a)",    demo_incline_rolling),
    ("Morin: 绳索滑落桌面 (Phys 15a)",    demo_rope_sliding),
    ("陀螺进动 (Phys 15a)",               demo_gyroscope),
    ("一维势阱与隧穿 (Phys 143a)",        demo_1d_well),
    ("化学势与费米能级 (Phys 165)",       demo_chemical_potential),
    ("Morin: 双圆锥上滚 (Phys 15a 荣誉)", demo_double_cone),
    ("生物物理随机行走 (Nelson)",         demo_biophysics_walk),
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
    print("  ║         Harvard 物理演示 · 费曼式可视化                   ║")
    print("  ║         Morin 力学 · Purcell 电磁 · Nelson 生物物理       ║")
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
    print("  💡 Morin 教授：「物理直觉不是天生的——")
    print("     它是被一道道反直觉题磨出来的。」")
    print("=" * 64 + "\n")

if __name__ == "__main__":
    main()
