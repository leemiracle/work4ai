"""
ETH Zürich 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个

ETH 特色：德语区严谨风格 + PSI 实验室 + Einstein 校友传统。
继承 Gerthsen/Cohen-Tannoudji 的形式严谨 + 物理直觉传统。
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


def ascii_field(field_fn, x_range, y_range, width=50, height=18,
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
# Demo 1 — 欧拉方程与陀螺：为什么自行车不会倒？
# ============================================================

def demo_euler_rigid_body():
    """欧拉方程：旋转的物体为什么"不听话"？

    白话：自由旋转的刚体在三个主轴上的转动惯量不同。欧拉方程告诉你
    角动量怎么变化。最反直觉的是：绕"中间"惯量轴的旋转是不稳定的！
    反直觉：网球拍定理——你把球拍绕中间轴抛起，它落地时会"翻转"。
    这是数学上必然的不稳定性，不是手感问题。
    类比：在三个直径不同的西瓜之间找平衡——中间那个永远站不稳。
    """
    banner("Demo 1 · 欧拉刚体方程 — 网球拍定理 (Dzhanibekov 效应)")
    print("  欧拉方程（无外力矩）：")
    print("    I₁·dω₁/dt = (I₂-I₃)·ω₂·ω₃")
    print("    I₂·dω₂/dt = (I₃-I₁)·ω₃·ω₁")
    print("    I₃·dω₃/dt = (I₁-I₂)·ω₁·ω₂")
    print()
    # 三个主转动惯量（典型刚体）
    I1, I2, I3 = 1.0, 2.0, 3.0  # I1 < I2 < I3
    print(f"  主转动惯量 I₁={I1}, I₂={I2}, I₃={I3}")
    print(f"  I₁ 最小轴: 稳定（绕最小轴旋转）")
    print(f"  I₃ 最大轴: 稳定（绕最大轴旋转）")
    print(f"  I₂ 中间轴: 不稳定！微小扰动指数放大")
    print()

    def simulate_axis(axis, omega_init, eps=1e-3, dt=0.01, T=20.0):
        """模拟在某个轴上小扰动的发展。axis: 1/2/3。"""
        w = [eps if i + 1 != axis else omega_init for i in range(3)]
        Is = [I1, I2, I3]
        log = []
        t = 0.0
        while t < T:
            dw = [
                (Is[1] - Is[2]) / Is[0] * w[1] * w[2],
                (Is[2] - Is[0]) / Is[1] * w[2] * w[0],
                (Is[0] - Is[1]) / Is[2] * w[0] * w[1],
            ]
            for i in range(3):
                w[i] += dw[i] * dt
            log.append((t, w[0], w[1], w[2]))
            t += dt
        return log

    for axis, name, stable in [(1, "最小轴 I₁", True),
                                 (2, "中间轴 I₂", False),
                                 (3, "最大轴 I₃", True)]:
        log = simulate_axis(axis, 5.0)
        max_dev = max(abs(row[axis]) for row in log)
        print(f"  绕 {name} 旋转，小扰动 ε=10⁻³ 的演化：")
        print(f"     最大偏差 = {max_dev:.4f}  ({'稳定' if max_dev < 0.05 else '爆炸性增长'})")
        # 画扰动增长曲线
        idx = axis  # 0-based
        ascii_curve(lambda k: abs(log[int(k*len(log)/60)][idx]),
                    0, 1, width=50, height=8, label=f"|ω_{axis}| vs t")
        print()

    print("  ✦ 反直觉：中间轴旋转的扰动不是振荡，而是指数放大！")
    print("  ✦ 这就是为什么扔网球拍时它会'翻面'——这是几何必然。")
    print("  ✦ 国际空间站 1985 年 Dzhanibekov 演示了同样的'神秘翻转'。")
    print("\n  类比：椭圆有长轴和短轴稳定，但任何'中间方向'都会让你滚下来。")


# ============================================================
# Demo 2 — 电磁波偏振：光也有"方向"
# ============================================================

def demo_em_polarization():
    """电磁波偏振：光为什么能被偏振片挡住？

    白话：光是一种电磁波，电场方向垂直于传播方向。如果电场总沿一个
    方向振动——线偏振；如果方向随时间旋转——圆偏振。
    反直觉：自然光的电场方向是随机的。一片偏振片就能把它"过滤"
    成单一方向——光强减半。
    类比：把一根绳子穿过栅栏，你只能上下挥动——栅栏就是偏振片。
    """
    banner("Demo 2 · 电磁波偏振 — ETH Gerthsen 经典")
    print("  电场 E 和磁场 B 互相垂直，且都垂直于传播方向 k")
    print("  E·B = 0, E·k = 0, B·k = 0")
    print()

    # 线偏振：E 沿固定方向
    print("  线偏振光 (E 沿 y 轴振动)：")
    print("      E")
    print("      ↑   ↑   ↑   ↑   ↑   ↑")
    print("      |   |   |   |   |   |")
    print("  ----+---+---+---+---+---+---> k (传播方向)")
    print()
    print("  圆偏振光 (E 旋转)：")
    for j in range(10):
        angle = j * 36
        rad = math.radians(angle)
        ey = math.sin(rad)
        # 简化版箭头
        if abs(ey) > 0.7:
            ch = "↑"
        elif ey > 0.3:
            ch = "╱"
        elif ey > -0.3:
            ch = "·"
        elif ey > -0.7:
            ch = "╲"
        else:
            ch = "↓"
        print(f"     {ch}", end="")
    print("\n     ----> k  (E 矢量末端画螺旋)")
    print()

    # 偏振片旋转的 Malus 定律
    print("  Malus 定律：I = I₀·cos²(θ)")
    print("  θ (°)    I/I₀    条形图")
    for theta in range(0, 91, 10):
        ratio = math.cos(math.radians(theta)) ** 2
        bar = "█" * int(ratio * 40)
        print(f"  {theta:4d}    {ratio:.3f}   [{bar:<40}]")
    print()
    ascii_curve(lambda t: math.cos(math.radians(t)) ** 2, 0, 180, width=60,
                height=10, label="I/I₀ (Malus)")
    print()
    print("  ✦ 反直觉：两片偏振片正交(90°)时全黑，")
    print("          但中间插入一片 45° 偏振片，光又'复活'了！")
    print("  ✦ 这违反经典直觉，但量子测量'塌缩到本征态'能完美解释。")
    print("  ✦ 应用：3D 电影、LCD 屏幕、偏振太阳镜、应力检测。")
    print("\n  类比：栅栏间挥绳——你只能让绳子沿一个方向抖动。")


# ============================================================
# Demo 3 — 角动量代数：[J_x, J_y] = iℏJ_z
# ============================================================

def demo_angular_momentum():
    """角动量代数：为什么量子角动量是"楼梯"？

    白话：经典角动量是一个矢量，可以指向任何方向。量子角动量也
    是矢量——但被两个量子数限制：总大小 J² = j(j+1)ℏ² 离散，
    z 分量 J_z = m·ℏ 只能取 m = -j, -j+1, ..., j。
    反直觉：哪怕在"本征态" |j,m⟩，J_x 和 J_y 也是不确定的！
    你只能同时知道 J² 和 J_z，不能知道 J_x。这就是海森堡不确定。
    类比：陀螺进动——你能知道它绕主轴转得多快（J_z），但进动
    方向（J_x, J_y）一直在变。
    """
    banner("Demo 3 · 角动量代数 — Cohen-Tannoudji 风格")
    print("  对易关系：[J_x, J_y] = iℏJ_z   (及轮换)")
    print("  本征态 |j, m⟩：")
    print("    J²|j,m⟩ = ℏ²j(j+1) |j,m⟩")
    print("    J_z|j,m⟩ = ℏm |j,m⟩,  m = -j, -j+1, ..., j")
    print()

    for j in [1, 3.0/2, 2, 5.0/2]:
        m_vals = []
        m = -j
        while m <= j + 1e-9:
            m_vals.append(m)
            m += 1
        J2 = j * (j + 1)
        J_mag = math.sqrt(J2)
        print(f"  j = {j}    J/ℏ = √(j(j+1)) = √{J2:.2f} = {J_mag:.3f}")
        print(f"    m 的取值: {m_vals}")
        print(f"    m/√(j(j+1)) 最大占比: {max(m_vals)/J_mag:.3f}")
        # 画 |J| 的"圆锥"
        print(f"    J_z 的可能方向（量子圆锥）：")
        for mm in m_vals:
            ratio = mm / J_mag
            bar = " " * 10 + "|" * int(abs(ratio) * 20)
            print(f"      m={mm:+.1f} →  {'→' if mm>=0 else '←'}" + bar[:30])
        print()

    print("  ✦ 反直觉：最大 m=j 时，J_z/|J| = j/√(j(j+1)) < 1！")
    print("          意味着 J 永远不能完全沿 z 轴对齐。")
    print(f"          j=1/2: 比例 1/√3 = {1/math.sqrt(3):.3f}")
    print(f"          j→∞  : 比例 → 1 (经典极限)")
    print()
    print("  ✦ 这就是为什么经典的'矢量完全对齐'在量子世界不存在。")
    print("  ✦ '量子圆锥'：J 沿 z 的投影确定，但 x,y 在圆锥上均匀分布。")
    print("\n  类比：陀螺进动——你确定它绕主轴多快，但进动方向未知。")


# ============================================================
# Demo 4 — 自旋 1/2：Stern-Gerlach 实验
# ============================================================

def demo_spin_half():
    """自旋 1/2：电子怎么"旋转"？

    白话：电子有内禀角动量叫"自旋"，自旋量子数是 1/2。在磁场中，
    自旋只能"朝上"或"朝下"两种状态——没有中间值。
    反直觉：自旋不是真的电子在"自转"——如果用经典图像算，电子
    表面速度会超光速！自旋是纯粹的量子内禀属性。
    类比：你问朋友"已婚吗"，只有"是/否"两种答案——没有"半婚"。
    """
    banner("Demo 4 · 自旋 1/2 — Stern-Gerlach 历史性实验")
    print("  1922 年 Stern-Gerlach：银原子束穿过非均匀磁场")
    print("  结果：屏上不是一条线，而是两团斑点！")
    print()
    print("       入射束 →  [磁场 ∂B/∂z]  →  屏幕上出现：")
    print("                                       ●  (自旋向上)")
    print("                                       ─────")
    print("                                       ─────")
    print("                                       ●  (自旋向下)")
    print()
    print("  Pauli 矩阵：")
    print("    σ_x = [[0, 1], [1, 0]]")
    print("    σ_y = [[0, -i], [i, 0]]")
    print("    σ_z = [[1, 0], [0, -1]]")
    print("  S_i = (ℏ/2)·σ_i")
    print()

    # |+x⟩ = (|+z⟩ + |-z⟩)/√2，验证在 z 测量时 50/50
    print("  实验 1：|+x⟩ 态用 z 轴装置测量")
    print("  |+x⟩ = (|+z⟩ + |-z⟩)/√2")
    print("  P(+z) = |⟨+z|+x⟩|² = 1/2")
    print("  P(-z) = |⟨-z|+x⟩|² = 1/2")
    print("  → 50% 概率向上，50% 向下，结果完全随机！")
    print()

    # 自旋进动模拟：B 场中的自旋
    print("  实验 2：磁场中的自旋进动")
    print("  哈密顿 H = -γ·B·S_z,  本征态 |±z⟩ 相位演化")
    gamma = 1.0
    B = 1.0
    omega = gamma * B  # Larmor 频率
    print(f"  Larmor 频率 ω = γ·B = {omega} (归一化)")
    print(f"  初始 |+x⟩ 在 B 沿 z 时，<S_x> 随时间余弦振荡：")
    ascii_curve(lambda t: math.cos(omega * t), 0, 4 * math.pi, width=60,
                height=10, label="<S_x>/ℏ")
    print()

    # 多次 Stern-Gerlach 实验链
    print("  实验 3：连续 Stern-Gerlach 装置")
    print("  [SG-z] → 选 |+z⟩ → [SG-x] → 选 |+x⟩ → [SG-z] → ?")
    print("  答案：50/50 又出现 |+z⟩ 和 |-z⟩！")
    print("  ✦ 反直觉：中间的 x 测量'抹除'了原来的 z 信息。")
    print("  ✦ 这就是量子测量的本质：测量改变系统状态。")
    print()
    print("  ✦ 自旋不是电子'自转'——经典图像下电子表面速度会超光速！")
    print("  ✦ 自旋是纯粹的相对论量子内禀属性（Dirac 方程自然导出）。")
    print("\n  类比：问'已婚吗'——只能回答是/否，没有'半婚'中间态。")


# ============================================================
# Demo 5 — 1D Ising 模型：相变的"实验室"
# ============================================================

def demo_ising_model():
    """伊辛模型：磁铁为什么到一定温度就失磁？

    白话：1D 链上每个格点有自旋 ↑ 或 ↓，相邻自旋倾向同向（铁磁）。
    温度高时热涨落打乱对齐，温度低时相互作用占优，自旋集体同向。
    反直觉：1D Ising 模型在任何 T>0 都没有自发磁化！只有在 T=0 才
    完全有序。2D 才有真正的相变（Onsager 1944 年精确解）。
    类比：一群人在广场，让所有人朝同一方向——人多容易，太阳大
    大家就各走各的。
    """
    banner("Demo 5 · 1D Ising 模型精确解 — ETH 统计力学传统")
    print("  哈密顿 H = -J·Σ s_i·s_{i+1}  (J>0 铁磁)")
    print("  配分函数 Z = Σ exp(-βH)")
    print()
    print("  1D 精确解 (Ising 1925)：")
    print("    Z = (2cosh(βJ))^N")
    print("    自由能/N = -kT·ln(2cosh(J/kT))")
    print("    无自发磁化（任意 T>0）")
    print()

    def free_energy_per_site(beta_J):
        """f/(kT) = -ln(2cosh(βJ))"""
        return -math.log(2 * math.cosh(beta_J))

    def energy_per_site(beta_J):
        """u = -J·tanh(βJ)"""
        return -math.tanh(beta_J)

    def specific_heat(beta_J):
        """c/(kB) = (βJ)²·sech²(βJ)"""
        return (beta_J ** 2) / (math.cosh(beta_J) ** 2)

    print("  J/(kT)   ⟨E⟩/J     C_v/(kB·J²)")
    print("  " + "-" * 36)
    for bJ in [0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]:
        e = energy_per_site(bJ)
        c = specific_heat(bJ)
        print(f"  {bJ:6.2f}    {e:+.4f}    {c:.4f}")

    print()
    print("  平均能量 <E>/J = -tanh(J/kT)：")
    ascii_curve(energy_per_site, 0.01, 10, width=60, height=10,
                label="<E>/J")
    print("\n  比热 C_v 的峰值在 βJ ≈ 0.88 (Schottky 反常)：")
    ascii_curve(specific_heat, 0.01, 10, width=60, height=10,
                label="C_v")

    # 直接蒙特卡洛模拟 1D Ising
    random.seed(7)
    print("\n  Monte Carlo 模拟（N=200, 单位 J/kT=βJ）：")
    for beta_J in [0.5, 2.0, 8.0]:
        N = 200
        spins = [random.choice([-1, 1]) for _ in range(N)]
        for _step in range(5000):
            i = random.randint(0, N - 1)
            nb = spins[(i - 1) % N] + spins[(i + 1) % N]
            dE = 2 * beta_J * spins[i] * nb
            if dE <= 0 or random.random() < math.exp(-dE):
                spins[i] *= -1
        m = abs(sum(spins)) / N
        bar = "█" * int(m * 50)
        print(f"    βJ={beta_J:4.1f}  磁化 |m| = {m:.3f}  [{bar:<50}]")
    print()
    print("  ✦ 反直觉：1D Ising 在有限温度下 |m|→0（无序），永不磁化！")
    print("  ✦ 因为 1D 链上的'畴壁'在任何 T>0 都会成对产生并扩散。")
    print("  ✦ 2D Ising 才有 T_c ≈ 2.269·J/k 的真正相变（Onsager 1944）。")
    print("\n  类比：广场上的人——人多能统一方向，太阳大就各走各的。")


# ============================================================
# Demo 6 — 群论基础：对称操作是物理学的"语法"
# ============================================================

def demo_group_theory():
    """群论：物理学家的"对称词典"

    白话：把一个物体旋转、镜像、平移，如果它看起来一样——它就有
    对称性。群论就是描述这些操作的数学语言。Wigner 说"群论是
    量子力学的自然语言"。
    反直觉：守恒律来自对称性！时间平移对称 → 能量守恒；空间平移
    → 动量守恒；旋转对称 → 角动量守恒。Noether 定理的深刻结论。
    类比：扑克牌——4 个花色就是"对称群"，规则对所有花色都一样。
    """
    banner("Demo 6 · 群论与对称性 — ETH 数学物理传统")
    print("  对称操作举例：旋转 C_n、镜像 σ、反演 i")
    print()
    print("  ▶ 等边三角形的对称性 (D₃ 群)：")
    print("     1 (恒等), C₃ (旋转 120°), C₃²,")
    print("     σ₁, σ₂, σ₃ (三个对称面)")
    print()
    # 画三角形 + 标号
    print("           顶点 1")
    print("              ●")
    print("             / \\")
    print("            /   \\")
    print("           /     \\")
    print("     3 ●--+-------● 2")
    print()
    print("  ▶ 群乘法表 (D₃)：")
    elements = ["1", "C3", "C3²", "σ1", "σ2", "σ3"]
    # 简化展示部分乘法
    table = {
        ("1","1"):"1", ("1","C3"):"C3", ("1","σ1"):"σ1",
        ("C3","1"):"C3", ("C3","C3"):"C3²", ("C3","σ1"):"σ2",
        ("C3²","C3"):"1", ("σ1","C3"):"σ3", ("σ1","σ1"):"1",
    }
    print("     ·  |  1    C3   C3²  σ1   σ2   σ3")
    print("     ---+----------------------------")
    for a in elements[:3]:
        row = f"     {a:<2} |"
        for b in elements:
            r = table.get((a, b), "-")
            row += f"  {r:<3}"
        print(row)
    print("     (其他行类似，封闭性、结合律都满足)")
    print()
    print("  ▶ Noether 定理：对称性 ⟺ 守恒律")
    print("     时间平移对称   →  能量守恒")
    print("     空间平移对称   →  动量守恒")
    print("     旋转对称       →  角动量守恒")
    print("     U(1) 规范对称  →  电荷守恒")
    print()
    print("  ✦ 反直觉：能量守恒不是宇宙的'规定'，而是'时间均匀性'的推论！")
    print("  ✦ 如果时间真的不均匀（如宇宙常数变化），能量就不守恒。")
    print("  ✦ 这就是为什么广义相对论中'全局能量'概念会失效。")
    print("\n  类比：扑克牌的 4 花色——'对称'意味着规则对各花色都一样。")


# ============================================================
# Demo 7 — London 方程：超导体的"磁场驱逐"
# ============================================================

def demo_london_equations():
    """London 方程：超导体为什么排斥磁场？

    白话：超导体内部电阻为零，电流无损耗流动。更神奇的是：磁场完全
    被排斥出超导体内部——Meissner 效应。London 兄弟 1935 年写下
    简洁方程描述它。
    反直觉：Meissner 效应不是"零电阻"的推论！零电阻只是说磁场不能
    变化；Meissner 说磁场本身被排斥。这是不同的现象。
    类比：你穿了一件"磁场雨衣"——雨水（磁场）从外面冲来，但雨衣
    让你身体完全干燥。
    """
    banner("Demo 7 · London 方程 — 超导 Meissner 效应 (PSI 重点)")
    print("  London 第一方程：∂J/∂t = (n_s e²/m)·E")
    print("    (电场加速超导电流，无阻力 → 无穷电导率)")
    print()
    print("  London 第二方程：∇×J = -(n_s e²/m)·B")
    print("    (磁场产生超导涡旋电流，反过来屏蔽磁场)")
    print()
    print("  结合 Maxwell 方程得：∇²B = B/λ_L²")
    print("    解 B(x) = B₀·exp(-x/λ_L)")
    print("    其中 λ_L = √(m/(μ₀n_s e²)) 是 London 穿透深度")
    print()

    mu0 = 4 * math.pi * 1e-7
    me = 9.11e-31
    e = 1.602e-19

    def london_depth(n_s):
        return math.sqrt(me / (mu0 * n_s * e * e))

    print("  不同超导体的 London 穿透深度：")
    print("  材料          n_s (m⁻³)        λ_L (nm)")
    print("  " + "-" * 50)
    for name, n_s in [("Al (铝)", 6.0e28), ("Pb (铅)", 1.3e29),
                       ("Nb (铌)", 5.6e28), ("YBCO", 1.0e28)]:
        lam = london_depth(n_s) * 1e9
        print(f"  {name:<14} {n_s:10.2e}      {lam:6.1f}")

    print()
    print("  磁场衰减 B(x)/B₀ = exp(-x/λ_L)：")
    ascii_curve(lambda x: math.exp(-x), 0, 5, width=60, height=10,
                label="B(x)/B₀")
    print()
    print("  ✦ 反直觉：超导体不是'磁屏蔽材料'，而是主动产生涡流抵消外场！")
    print("  ✦ 磁场在表面 λ_L (~50nm) 内就衰减殆尽，内部磁场=0。")
    print("  ✦ Meissner 效应 ≠ 零电阻：")
    print("      - 零电阻：磁场一旦进入就出不来（磁通冻结）")
    print("      - Meissner：磁场被主动'推出去'（无论历史）")
    print("  ✦ 这就是为什么磁悬浮列车能悬浮——Meissner 排斥磁铁。")
    print()
    print("  类型 I vs 类型 II 超导体：")
    print("    Type I (纯金属)：完全 Meissner，临界场 H_c")
    print("    Type II (合金)：H_c1 < H < H_c2 之间磁通量子化穿透")
    print()
    print("  类比：超导体是'磁场雨衣'——内部保持干燥。")


# ============================================================
# Demo 8 — 等效原理：Einstein 在 ETH 的顿悟
# ============================================================

def demo_equivalence_principle():
    """等效原理：为什么电梯里和火箭里感觉一样？

    白话：1907 年 Einstein 在专利局想"一生最快乐的想法"：自由下落
    的人感觉不到重力——加速度和引力等效。这成为广义相对论的种子。
    反直觉：在没有窗户的电梯里，你无法分辨自己是被火箭加速（无引力）
    还是在引力场中静止——这是物理上不可区分的。
    类比：坐电梯时电梯启动瞬间你变"重"——和被火箭加速感觉一样。
    """
    banner("Demo 8 · 等效原理 — Einstein 在 ETH 的最快乐想法")
    print("  弱等效原理：惯性质量 = 引力质量")
    print("    F = m_i·a   (牛顿第二定律，m_i 惯性)")
    print("    F = m_g·g   (引力，m_g 引力质量)")
    print("    => a = (m_g/m_i)·g")
    print("    实验上 m_g/m_i = 1 精度达 10⁻¹⁵！(Eöt-Wash 实验)")
    print()
    print("  强等效原理：局部引力场 ≡ 加速参考系")
    print("    没有局部实验能区分'引力'和'加速'。")
    print()

    # 自由落体和零重力等效的"思想实验"
    print("  ▶ 思想实验：密封舱内的人")
    print()
    print("  情景 A：停在地球表面              情景 B：火箭太空加速")
    print("  ┌───────────────┐                ┌───────────────┐")
    print("  │               │                │               │")
    print("  │  人 感觉'重'  │                │  人 感觉'重'  │")
    print("  │  ↓            │                │  ↓            │")
    print("  │═══════════════│                │═══════════════│")
    print("  │   地面支持     │                │  火箭推动 ↑   │")
    print("  └───────────────┘                └───────────────┘")
    print("       g = 9.81 m/s²                    a = 9.81 m/s²")
    print()
    print("  ✦ 反直觉：人在 A 和 B 中感觉完全相同！无法分辨。")
    print("  ✦ 这意味着引力'不是力'，而是时空弯曲的表现。")
    print()

    # 引力红移
    print("  ▶ 引力红移（等效原理的预言）：")
    print("  光从高引力势向低引力势传播时蓝移，反之红移。")
    G = 6.674e-11
    c = 3e8
    M_earth = 5.972e24
    R_earth = 6.371e6
    # 红移 z ≈ GM/(Rc²)
    z_shift = G * M_earth / (R_earth * c * c)
    print(f"    地表到无穷远的红移 z = GM/(Rc²)")
    print(f"    = {G}×{M_earth:.3e}/({R_earth:.3e}×{c:.2e}²)")
    print(f"    = {z_shift:.2e}")
    print(f"    → 频率移动仅 {z_shift*1e9:.2f} ppb（极微弱，但 Pound-Rebka 1960 测到了）")
    print()

    # GPS 必须考虑相对论修正
    print("  ▶ 应用：GPS 卫星必须用相对论修正！")
    print("  卫星轨道高度 h ≈ 20200 km, 速度 v ≈ 3.87 km/s")
    h_gps = 20200e3
    v_gps = 3870.0
    # SR 时间膨胀（卫星快→慢）
    sr_factor = -v_gps ** 2 / (2 * c * c)
    # GR 引力蓝移（卫星高→快）
    gr_factor = G * M_earth / (c * c) * (1 / R_earth - 1 / (R_earth + h_gps))
    total = sr_factor + gr_factor
    per_day = total * 86400 * 1e6  # 微秒/天
    print(f"    SR 修正 (速度)： {sr_factor:+.3e} (时间变慢)")
    print(f"    GR 修正 (引力)： {gr_factor:+.3e} (时间变快)")
    print(f"    合计每天偏差：   {per_day:+.1f} μs/天")
    print(f"    若不修正，GPS 位置漂移 ~{per_day*1e-6*c/2:.0f} m/天 → 不可用！")
    print()
    print("  ✦ 反直觉：广义相对论不是抽象理论——你的手机 GPS 每天都在用。")
    print("  ✦ Einstein 从等效原理出发，1915 年写出 Einstein 场方程，")
    print("          预言了黑洞、引力波、宇宙膨胀——全部被证实。")
    print("\n  类比：电梯启动瞬间你变'重'——和火箭加速感觉一模一样。")


# ============================================================
# 主入口
# ============================================================

DEMOS = [
    ("欧拉方程：网球拍定理", demo_euler_rigid_body),
    ("电磁波偏振：光的方向", demo_em_polarization),
    ("角动量代数：量子楼梯", demo_angular_momentum),
    ("自旋 1/2：Stern-Gerlach 实验", demo_spin_half),
    ("1D Ising 模型：相变实验室", demo_ising_model),
    ("群论：对称性即守恒律", demo_group_theory),
    ("London 方程：超导 Meissner 效应", demo_london_equations),
    ("等效原理：Einstein 的顿悟", demo_equivalence_principle),
]


def main():
    import sys
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   ETH Zürich 物理演示 · 费曼式可视化  (德语严谨 + PSI)       ║")
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
