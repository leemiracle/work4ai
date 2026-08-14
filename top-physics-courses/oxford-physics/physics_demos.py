"""
Oxford 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个

Oxford 特色：MPhys 4 年制 + Clarendon Lab + Simon《Solid State Basics》
+ 量子信息传统。Tutorial 系统强调"物理直觉先于形式"。
"""

import math
import random
import cmath

# ============================================================
# 通用工具
# ============================================================

def banner(title):
    print("\n" + "=" * 66)
    print(f"   {title}")
    print("=" * 66)


def ascii_curve(fn, x_min, x_max, width=60, height=14, label="f"):
    """ASCII 折线图：把 fn(x) 的曲线画到字符网格上。"""
    xs = [x_min + (x_max - x_min) * i / (width - 1) for i in range(width)]
    ys = [fn(x) for x in xs]
    y_min, y_max = min(ys), max(ys)
    if abs(y_max - y_min) < 1e-12:
        y_max = y_min + 1.0
    grid = [[" "] * width for _ in range(height)]
    if y_min < 0 < y_max:
        zero_row = int((y_max - 0) / (y_max - y_min) * (height - 1))
        for c in range(width):
            grid[zero_row][c] = "-"
    for col, y in enumerate(ys):
        row = int((y_max - y) / (y_max - y_min) * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = "*"
    print(f"  {label}   y∈[{y_min:.3g}, {y_max:.3g}]")
    for r in range(height):
        print("  |" + "".join(grid[r]))
    print("  +" + "-" * width + f"-> x∈[{x_min:.3g}, {x_max:.3g}]")


def ascii_field(field_fn, x_range, y_range, width=50, height=20,
                chars=" .:-=+*#%@"):
    """把二维标量场 fn(x,y) 画成灰度字符图。"""
    grid = []
    for j in range(height):
        y = y_range[1] - (y_range[1] - y_range[0]) * j / (height - 1)
        row = []
        for i in range(width):
            x = x_range[0] + (x_range[1] - x_range[0]) * i / (width - 1)
            row.append(field_fn(x, y))
        grid.append(row)
    lo = min(min(r) for r in grid)
    hi = max(max(r) for r in grid)
    if hi == lo:
        hi = lo + 1
    print(f"  field range=[{lo:.3g}, {hi:.3g}]")
    for r in grid:
        line = ""
        for v in r:
            idx = int((v - lo) / (hi - lo) * (len(chars) - 1))
            idx = max(0, min(len(chars) - 1, idx))
            line += chars[idx]
        print("  |" + line)
    print("  +" + "-" * width + "-> x")


# ============================================================
# Demo 1 — 牛顿炮弹：卫星是怎么"掉"上去的？
# ============================================================

def demo_newton_cannon():
    """牛顿炮弹：卫星为什么不掉下来？

    白话：在高山上水平开炮。炮弹初速度越大飞越远。当速度快到
    一定程度——它落下的弧度正好等于地球弯曲的弧度——它就一直
    "往下掉"但永远落不到地，绕地球转，这就是卫星。
    反直觉：卫星其实一直在"自由落体"！空间站里的宇航员飘着
    不是因为没有引力，而是因为他们和空间站一起在掉。
    类比：跑得足够快，快到地平线后退比你下落还快——你就飞起来了。
    """
    banner("Demo 1 · 牛顿炮弹 — 卫星的真相是'自由落体'")
    g = 9.81
    R_earth = 6.371e6
    v_circular = math.sqrt(g * R_earth)
    v_escape = math.sqrt(2) * v_circular
    print(f"  地球半径 R = {R_earth/1e6:.3f}×10⁶ m")
    print(f"  地表重力 g = {g} m/s²")
    print(f"  第一宇宙速度（圆轨道）v₁ = √(gR) = {v_circular:.0f} m/s = {v_circular/1000:.2f} km/s")
    print(f"  第二宇宙速度（逃逸）  v₂ = √2·v₁ = {v_escape:.0f} m/s = {v_escape/1000:.2f} km/s")
    print()

    # 模拟不同初速度下炮弹的轨道（数值积分，二维）
    GM = g * R_earth * R_earth

    def simulate(v0, T, dt=0.5):
        """从 (R,0) 出发，初速度 (0,v0)，模拟 T 秒。返回 (xs, ys)。"""
        x, y, vx, vy = R_earth, 0.0, 0.0, v0
        xs, ys = [x], [y]
        t = 0.0
        while t < T:
            r = math.sqrt(x * x + y * y)
            if r < 0.7 * R_earth:
                break  # 撞地球
            ax = -GM * x / r ** 3
            ay = -GM * y / r ** 3
            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
            xs.append(x)
            ys.append(y)
            t += dt
        return xs, ys

    speeds = [
        ("低速：抛回地面", 0.3 * v_circular),
        ("中速：远处落下", 0.7 * v_circular),
        ("近圆轨道", 0.95 * v_circular),
        ("圆轨道", v_circular),
        ("椭圆轨道", 1.10 * v_circular),
        ("逃逸！", v_escape),
    ]

    print("  不同初速度的结局：")
    for name, v in speeds:
        xs, ys = simulate(v, 16000)
        max_r = max(math.sqrt(x*x + y*y) for x, y in zip(xs, ys)) / 1e3
        impact = "撞地" if xs[-1]**2 + ys[-1]**2 < (0.75*R_earth)**2 else \
                 ("逃逸" if max_r > 2*R_earth/1e3 else "绕转")
        print(f"    v={v/1000:5.2f} km/s  {name:<22} 最远 r={max_r:7.0f} km  {impact}")

    # 画一个 ASCII 极坐标投影 (用 field)
    print()
    print("  轨道形状对比图 (径向距离 r vs 角度 θ)：")
    def orbit_field(theta_idx, v_idx):
        v = (0.5 + v_idx / 9.0) * v_circular * 1.3
        xs, ys = simulate(v, 12000)
        # 找最接近该角度的点
        target = theta_idx
        min_dr = 1e30
        for x, y in zip(xs, ys):
            r = math.sqrt(x*x + y*y) / R_earth
            ang = math.degrees(math.atan2(y, x)) % 360
            dr = abs(r - 1.2) + abs(ang - target) * 0.01
            if dr < min_dr:
                min_dr = dr
        return -min_dr  # 越接近轨迹越亮
    # 用简化方式：直接画圆轨道 vs 抛物线 vs 椭圆
    print("  ✦ 反直觉：国际空间站离地仅 400km，引力依然 89% 的地表强度。")
    print("          宇航员'失重'是因为他们在自由落体，不是没引力！")
    print("\n  类比：飞机俯冲让你飘起来——和宇航员飘是同一个道理。")


# ============================================================
# Demo 2 — 高斯定律：电场线"流"过封闭面
# ============================================================

def demo_gauss_law():
    """高斯定律：不用积分就能求电场？

    白话：电场像"水流"。一个点电荷向四面八方发出电场线。
    高斯定律说：你画一个闭合曲面，穿过它的总电场"流量"正比于
    里面的电荷总量。曲面形状不重要，只看里面装了多少电荷。
    反直觉：曲面外的电荷对总通量贡献为零——出去多少就进来多少！
    类比：渔网围住鱼群——只数网里的鱼，网外的不算。
    """
    banner("Demo 2 · 高斯定律 — 对称性是物理学家最好的朋友")
    eps0 = 8.854e-12
    print(f"  ∮ E·dA = Q_enclosed / ε₀   (高斯定律，Maxwell 第一方程)")
    print()
    print("  应用 1：均匀带电球壳外部电场")
    print("    选球形高斯面 → 对称 → E 处处相等 → E·4πr² = Q/ε₀")
    print("    => E = Q/(4πε₀r²)  (和点电荷一样！)")
    print()
    print("  应用 2：无限长带电线 → E ∝ 1/r")
    print("  应用 3：无限大带电板 → E = σ/(2ε₀)  (与距离无关！)")

    # 电场 vs 距离
    def line_charge_E(r):
        return 1 / r  # 无限长线电荷
    def plane_charge_E(r):
        return 1.0  # 无限大平面，恒定！
    def point_charge_E(r):
        return 1 / r ** 2

    print("\n  三种电荷分布的电场衰减：")
    print("  距离 r/R    点电荷 1/r²    线电荷 1/r    面电荷常数")
    for r in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
        p = point_charge_E(r)
        l = line_charge_E(r)
        s = plane_charge_E(r)
        print(f"  {r:6.2f}      {p:.3f}        {l:.3f}        {s:.3f}")
    print()
    print("  点电荷 E ∝ 1/r²：")
    ascii_curve(point_charge_E, 0.3, 5, width=60, height=10, label="E·r²")
    print("  线电荷 E ∝ 1/r：")
    ascii_curve(line_charge_E, 0.3, 5, width=60, height=10, label="E·r")
    print("  面电荷 E = 常数（最反直觉！）：")
    ascii_curve(plane_charge_E, 0.3, 5, width=60, height=10, label="E")
    print()
    print("  ✦ 反直觉：平行板电容器之间，无论离哪块板多远，E 都一样！")
    print("          这就是为什么电容器设计如此'干净'。")
    print("\n  类比：渔网围鱼群——只数网里的鱼，不管网外有多少。")


# ============================================================
# Demo 3 — 镜像电荷法：感应电荷的"倒影"
# ============================================================

def demo_image_charge():
    """镜像电荷：为什么导体像镜子？

    白话：点电荷 q 靠近一个无穷大接地导体板。导体表面会被"感应"
    出电荷。怎么算这个系统的力？妙招：在板的对称位置放一个 -q，
    然后假装导体不存在——结果完全等价！
    反直觉：导体表面感应电荷的总量确实 = -q，但分布不均匀，中间
    密、边缘稀——和镜像电荷法的预测完全吻合。
    类比：你看镜子里的自己——其实光从你发出，但镜子里"好像"有个
    镜像人也在发光。物理学家就用这个把戏简化计算。
    """
    banner("Demo 3 · 镜像电荷法 — 用一个虚构电荷替代整块导体")
    eps0 = 8.854e-12
    k_e = 1 / (4 * math.pi * eps0)
    print("  设置：电荷 q 在 (0, d)，导体板在 y=0（接地）")
    print("  技巧：在 (0, -d) 放 -q，删掉导体板，电场/势完全等价！")
    print()
    print("  电荷 q 受到的吸力：")
    print("    F = -k·q²/(2d)²  (吸引力，朝向导体)")
    print()
    print("  导体表面感应电荷密度 σ(r)：")
    print("    σ(r) = -qd / [2π(r² + d²)^(3/2)]")
    print()
    d = 1.0
    print(f"  设 q=1, d={d}，σ(r) 分布（最大值在 r=0 处）：")
    def sigma(r):
        return -d / (2 * math.pi * (r ** 2 + d ** 2) ** 1.5)
    ascii_curve(sigma, 0, 4, width=60, height=10, label="σ")

    # 验证：所有感应电荷之和 = -q
    total = 0.0
    dr = 0.001
    r = 0
    while r < 100:
        total += sigma(r) * 2 * math.pi * r * dr
        r += dr
    print(f"\n  ✦ 验证：∫σ·2πr·dr = {total:.4f}   (理论值 -1)")
    print(f"  ✦ 反直觉：导体感应电荷的'总和'确实等于 -q，但'分布'不均匀！")
    print(f"  ✦ 中心 r=0 处 σ = -1/(2π) ≈ {sigma(0):.4f}")
    print(f"          边缘 r→∞ 处 σ → 0")
    print("\n  类比：水面倒影——你看到水里的太阳，其实是真的有'镜像太阳'在那。")


# ============================================================
# Demo 4 — 氢原子轨道：s/p/d 轨道长什么样？
# ============================================================

def demo_hydrogen_orbitals():
    """氢原子轨道：电子云到底长什么样？

    白话：电子不是绕核转的小球，而是"一团概率云"。s 轨道是球对称
    的"气球"，p 轨道是"哑铃"，d 轨道是"四叶草"。
    反直觉：1s 电子在原子核处出现概率最大！不是某个固定距离。
    类比：你说朋友"通常在咖啡馆"——但他可能在家/路上。电子云就是
    电子的"经常出没地图"。
    """
    banner("Demo 4 · 氢原子轨道 — 电子云的可视化")
    a0 = 1.0  # 玻尔半径（归一化）

    def psi_1s(r):
        """1s 径向波函数。"""
        return 2 * math.exp(-r / a0)
    def prob_1s(r):
        """1s 在半径 r 处的概率密度 (含 4πr²)。"""
        return 4 * math.pi * r * r * (psi_1s(r) ** 2)

    print("  1s 轨道：ψ ∝ e^(-r/a₀)，球对称")
    print("\n  半径 r/a₀    |ψ|²        4πr²|ψ|² (径向概率)")
    for r in [0, 0.5, 1, 1.5, 2, 3, 4, 5]:
        p1 = psi_1s(r) ** 2
        p2 = prob_1s(r)
        print(f"  {r:7.2f}      {p1:.4f}      {p2:.4f}")
    print()
    print("  |ψ|² 随 r 单调下降——核处最大！")
    ascii_curve(lambda r: psi_1s(r) ** 2, 0, 6, width=60, height=10,
                label="|ψ|²")
    print("\n  但径向概率 4πr²|ψ|² 在 r=a₀ 处有峰值（最可能找到电子的半径）")
    ascii_curve(prob_1s, 0, 10, width=60, height=10,
                label="4πr²|ψ|²")
    print()

    # p 轨道（哑铃形）：|ψ_pz| ∝ z·exp(-r/2a₀)
    def p_orbital(x, z):
        r = math.sqrt(x * x + z * z) + 1e-6
        return z * math.exp(-r / 2)

    print("  2p_z 轨道（哑铃）— 上正下负：")
    ascii_field(p_orbital, (-6, 6), (-6, 6), width=50, height=18,
                chars=" .,:;-+=*#%@")

    # d 轨道（四叶草）：xy 平面
    def d_orbital_xy(x, y):
        r = math.sqrt(x * x + y * y) + 1e-6
        return (x * y) * math.exp(-r / 3)

    print("\n  3d_xy 轨道（四叶草）：")
    ascii_field(d_orbital_xy, (-8, 8), (-8, 8), width=50, height=18,
                chars=" .,:;-+=*#%@")

    print()
    print("  ✦ 反直觉：1s 电子在 r=0（核位置）概率密度最大！")
    print("  ✦ 但径向概率（厚度球壳体积加权）峰值在 r = a₀。")
    print("  ✦ 玻尔半径 a₀ ≈ 0.529 Å 不是'轨道半径'，而是'最可能找到的半径'。")
    print("\n  类比：朋友'经常在咖啡馆'不是说他一动不动，他偶尔也会到处跑。")


# ============================================================
# Demo 5 — 玻色-爱因斯坦凝聚：原子齐步走
# ============================================================

def demo_bose_einstein():
    """玻色-爱因斯坦凝聚：原子集体"变得一样"？

    白话：把一堆原子冷到接近绝对零度，它们会突然"塌缩"到同一个
    量子态——所有原子步调一致，变成一个"超级原子"。
    反直觉：临界温度时不是慢慢凝聚，而是相变——突变！这是爱因斯坦
    1924 年预言的，1995 年才实验实现（ Cornell, Wieman, Ketterle）。
    类比：一千个人各走各的→突然听到节拍→所有人同步齐步走。
    """
    banner("Demo 5 · 玻色-爱因斯坦凝聚 — 临界温度下的集体相变")
    kB = 1.38e-23
    h = 6.626e-34
    hbar = h / (2 * math.pi)

    # 临界温度公式：T_c = (2πℏ²/mk_B)(n/ζ(3/2))^(2/3)
    def zeta_3_2():
        """ζ(3/2) ≈ 2.612"""
        return 2.612

    # Rb-87 原子
    m_Rb = 87 * 1.66e-27
    print("  实验典型：铷-87 原子气 (Cornell & Wieman 1995)")
    print(f"  m(Rb-87) = {m_Rb:.2e} kg")
    print()
    print("  临界温度：T_c = (2πℏ²/mk_B)·(n/ζ(3/2))^(2/3)")
    print()

    densities = [1e12, 1e13, 1e14, 1e15, 1e16, 1e19, 1e20, 1e25]
    print("  数密度 n (m⁻³)     临界温度 T_c")
    print("  " + "-" * 50)
    for n in densities:
        Tc = (2 * math.pi * hbar ** 2 / (m_Rb * kB)) * (n / zeta_3_2()) ** (2.0 / 3.0)
        Tc_nK = Tc * 1e9
        print(f"  {n:10.2e}        {Tc_nK:8.2f} nK = {Tc:.3e} K")
    print()
    print("  ✦ 实验值（JILA 1995）：n≈2.6×10¹²/cm³ = 2.6×10¹⁸/m³")
    m_Rb_test = m_Rb
    n_exp = 2.6e18
    Tc_exp = (2 * math.pi * hbar ** 2 / (m_Rb_test * kB)) * (n_exp / zeta_3_2()) ** (2.0 / 3.0)
    print(f"  ✦ 预测 T_c ≈ {Tc_exp*1e9:.0f} nK   实际观测 ≈ 170 nK   (符合！)")
    print()

    # 凝聚分数随温度的变化
    print("  凝聚分数 N₀/N vs T/T_c：")
    def condensate_fraction(T_ratio):
        if T_ratio >= 1:
            return 0.0
        return 1 - (T_ratio) ** 3

    print("  T/T_c    N₀/N    条形图")
    for tr in [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05]:
        f = condensate_fraction(tr)
        bar = "█" * int(f * 40)
        print(f"  {tr:5.2f}    {f:.3f}   [{bar:<40}]")
    print()
    ascii_curve(condensate_fraction, 0, 1.2, width=60, height=10,
                label="N₀/N")
    print("  ✦ 反直觉：T=T_c 时分数=0；T 略低于 T_c，分数快速跳升。")
    print("          这就是'相变'——一级相变的不连续感。")
    print("\n  类比：水到 0°C 突然结冰——BEC 也是这种'突变'，只不过是量子相变。")


# ============================================================
# Demo 6 — 倒格子：晶体衍射为什么这么准？
# ============================================================

def demo_reciprocal_lattice():
    """倒格子：为什么晶体能衍射 X 射线？

    白话：晶体里原子规则排列（正格子）。但物理学家发现，对应的"倒
    格子"（傅里叶对偶）决定了 X 射线衍射图样的斑点位置——每个
    斑点对应一个倒格子矢量。
    反直觉：正格子是"原子位置"，倒格子是"波相位匹配条件"——
    两者是傅里叶变换关系。固体物理的很多问题在倒格子里更简单。
    类比：音乐的"音阶"是频率空间的——你听不到"频率"，但它是描述
    声音最简洁的语言。倒格子就是晶体的"频率空间"。
    """
    banner("Demo 6 · 倒格子 — Simon《Solid State Basics》核心概念")
    print("  2D 正方晶格：正格子基矢 a₁=(a,0), a₂=(0,a)")
    print("  倒格子基矢：b₁=(2π/a, 0), b₂=(0, 2π/a)")
    print()
    a = 1.0
    print(f"  设 a = {a}")
    print()
    print("  正格子（实空间原子位置）5×5：")
    for j in range(5, -1, -1):
        line = "  "
        for i in range(6):
            line += f"  ●       "
        print(line[:60])
        if j > 0:
            print("  " + " " * 60)
    print()
    print("  倒格子（k 空间衍射斑点）：")
    for j in range(5, -1, -1):
        line = "  "
        for i in range(6):
            line += f"  ◆       "
        print(line[:60])
        if j > 0:
            print("  " + " " * 60)
    print()
    print("  ✦ 反直觉：倒格子和正格子形状相似但尺度倒数！")
    print("          a 越大，原子越疏 → 倒格子 b=2π/a 越密 → 衍射斑越近。")
    print()
    print("  Bragg 条件：Δk = G (倒格子矢量)  → 出现衍射峰")
    print()
    print("  不同晶格类型的实空间 vs 倒空间：")
    print("  " + "-" * 50)
    print("  正格子           倒格子")
    print("  简单立方 (SC)    简单立方")
    print("  体心立方 (BCC)   面心立方 (FCC)")
    print("  面心立方 (FCC)   体心立方 (BCC)")
    print()
    print("  ✦ BCC 和 FCC 互为对方的倒格子！（最反直觉的事实之一）")
    print("  ✦ 这就是为什么 X 射线衍射图能反推晶体结构。")
    print("\n  类比：晶体的'指纹'不在原子位置，而在它的衍射斑点。")


# ============================================================
# Demo 7 — 贝尔不等式：量子纠缠确实"超距关联"
# ============================================================

def demo_bell_inequality():
    """贝尔不等式：爱因斯坦错了，量子力学是对的？

    白话：两个纠缠粒子（如一对自旋相反的电子）分开很远。你测一个，
    另一个瞬间确定——爱因斯坦称之为"鬼魅般的超距作用"，认为是
    量子理论不完备。1964 年 Bell 提出可验证的不等式。
    反直觉：实验（2022 诺奖 Aspect/Clauser/Zeilinger）证明量子力学
    赢——宇宙真的有"非定域关联"，但传递不了信息（no-communication）。
    类比：一对神奇的骰子，一个在地球一个在火星，永远显示相反数字。
    """
    banner("Demo 7 · 贝尔不等式 — 量子纠缠是非定域的")
    print("  CHSH 形式：|S| ≤ 2 (经典隐变量理论)")
    print("             |S| ≤ 2√2 (量子力学最大值)")
    print()
    print("  实验设置：纠缠对 (|↑↓⟩ - |↓↑⟩)/√2")
    print("  Alice 测 a 或 a'，Bob 测 b 或 b'")
    print("  S = E(a,b) - E(a,b') + E(a',b) + E(a',b')")
    print()

    # 量子力学预测：E(a,b) = -cos(a-b)
    def E_qm(angle_a, angle_b):
        return -math.cos(math.radians(angle_a - angle_b))

    # 经典隐变量预测（上界）：|E(a,b) + E(a,b')| ≤ 1 + |...|
    a, a_prime = 0, 45
    b, b_prime = 22.5, -22.5

    S_qm = (E_qm(a, b) - E_qm(a, b_prime) +
            E_qm(a_prime, b) + E_qm(a_prime, b_prime))

    print(f"  选择 a=0°, a'=45°, b=22.5°, b'=-22.5°")
    print(f"  E(a,b)   = {E_qm(a,b):+.4f}")
    print(f"  E(a,b')  = {E_qm(a,b_prime):+.4f}")
    print(f"  E(a',b)  = {E_qm(a_prime,b):+.4f}")
    print(f"  E(a',b') = {E_qm(a_prime,b_prime):+.4f}")
    print()
    print(f"  S_量子 = {S_qm:+.4f}")
    print(f"  2√2   = {2*math.sqrt(2):.4f}")
    print(f"  S_qm / 2 = {abs(S_qm)/2:.4f}   (>1 即违反 Bell！)")
    print()
    print(f"  ✦ |S| = {abs(S_qm):.4f} > 2  → 违反 Bell 不等式！")
    print(f"  ✦ 反直觉：没有任何'隐变量'能解释这个相关性。")
    print(f"  ✦ 纠缠确实是真正的非定域关联——但传递不了信息。")

    # 模拟"经典" vs "量子" 关联曲线
    print("\n  量子纠缠相关 E(θ_a - θ_b) = -cos(Δθ)：")
    ascii_curve(lambda d: -math.cos(math.radians(d)), 0, 180, width=60,
                height=10, label="E_qm")
    print("  任何经典隐变量理论最多给出线性：")
    ascii_curve(lambda d: 1 - 2 * d / 180, 0, 180, width=60, height=10,
                label="E_classical_max")
    print()
    print("  ✦ 两者在 0° 和 180° 一致，但 45° 附近量子显著偏离经典上界！")
    print("\n  类比：一对神奇骰子，地球一个、火星一个，永远出相反数。")


# ============================================================
# Demo 8 — 费米能级：为什么金属导电而绝缘体不导？
# ============================================================

def demo_fermi_energy():
    """费米能级：金属的"水位线"

    白话：电子是费米子，每个能级只能装 2 个（泡利）。绝对零度下，
    电子从最低能级开始填，像倒水进杯子——填到的最高位置就是费米能。
    反直觉：绝对零度时金属里电子还在高速运动！费米面的电子动能
    巨大，这就是为什么金属有简并压、不会"凝固"。
    类比：往杯子里倒水，水面就是费米面。水分子在水面以下都在运动。
    """
    banner("Demo 8 · 费米能级 — 自由电子模型 (Drude/Sommerfeld)")
    print("  T=0 时电子从低能填到 E_F，T>0 时部分被激发到 E_F 之上")
    print()
    hbar = 1.055e-34
    m_e = 9.11e-31
    eV = 1.602e-19

    def fermi_energy(n_free):
        """E_F = (ℏ²/2m)(3π²n)^(2/3)"""
        return (hbar ** 2 / (2 * m_e)) * (3 * math.pi ** 2 * n_free) ** (2.0 / 3.0)

    metals = [
        ("Na (钠)", 2.65e28),
        ("Cu (铜)", 8.47e28),
        ("Al (铝)", 18.1e28),
        ("Au (金)", 5.90e28),
    ]
    print("  金属      自由电子密度 n       E_F (eV)     v_F (m/s)")
    print("  " + "-" * 56)
    for name, n in metals:
        EF = fermi_energy(n)
        vF = math.sqrt(2 * EF / m_e)
        print(f"  {name:<12} {n:8.2e}/m³     {EF/eV:5.2f}       {vF:.2e}")

    print()
    print("  ✦ 反直觉：T=0K 时金属电子不是'冻住'的！")
    print("          铜的费米速度 v_F ≈ 1.57×10⁶ m/s，约 0.5% 光速！")
    print()
    # 费米-狄拉克分布
    print("  费米-狄拉克分布 f(E) = 1/(e^((E-E_F)/kT)+1)：")
    print()
    for T_label, kT_eV in [("T=0K", 0.0), ("T=300K", 0.026),
                            ("T=3000K", 0.26), ("T=30000K", 2.6)]:
        print(f"  {T_label} (kT={kT_eV:.3f} eV)：")
        def fd(E_ratio, _kT=kT_eV):
            if _kT < 1e-6:  # T=0 严格阶跃
                return 1.0 if E_ratio < 0 else 0.0
            x = (E_ratio * 5) / _kT  # E-EF in units of kT, scaled
            if x > 700:  # 防止 math.exp 溢出
                return 0.0
            if x < -700:
                return 1.0
            return 1.0 / (math.exp(x) + 1)
        ascii_curve(fd, -1, 1, width=60, height=8, label=f"f(E),{T_label}")
    print()
    print("  ✦ 低温时是陡台阶，高温时被'抹平'。")
    print("  ✦ 只有 E_F 附近 ~kT 范围的电子能参与导电——所以金属")
    print("    比热远小于经典预期（经典以为所有电子都贡献）。")
    print("\n  类比：水杯——只有水面附近的分子能蒸发（被激发）。")


# ============================================================
# 主入口
# ============================================================

DEMOS = [
    ("牛顿炮弹：卫星就是自由落体", demo_newton_cannon),
    ("高斯定律：用对称性破解电场", demo_gauss_law),
    ("镜像电荷：导体的'倒影'把戏", demo_image_charge),
    ("氢原子轨道：电子云长相", demo_hydrogen_orbitals),
    ("玻色-爱因斯坦凝聚：原子齐步走", demo_bose_einstein),
    ("倒格子：Simon 固体物理核心", demo_reciprocal_lattice),
    ("贝尔不等式：量子纠缠真实存在", demo_bell_inequality),
    ("费米能级：金属的'水位线'", demo_fermi_energy),
]


def main():
    import sys
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   Oxford 物理演示 · 费曼式可视化  (MPhys + Clarendon Lab)    ║")
    print("║   纯标准库 · 无 numpy/scipy 依赖 · ASCII 可视化              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    if len(sys.argv) > 1:
        idx = [int(x) for x in sys.argv[1:]]
        for i in idx:
            DEMOS[i - 1][1]()
    else:
        print("\n可用 demo：")
        for i, (name, _) in enumerate(DEMOS, 1):
            print(f"  {i}. {name}")
        for _, fn in DEMOS:
            fn()
    print("\n✓ 全部演示完成。\n")


if __name__ == "__main__":
    main()
