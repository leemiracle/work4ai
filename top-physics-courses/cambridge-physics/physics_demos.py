"""
Cambridge 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个

Cambridge 特色：Natural Sciences Tripos 重计算 + Cavendish Lab 重直觉。
"""

import math
import random

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
    # 零轴
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


def ascii_histogram(values, bins=20, width=50, label="count"):
    """把一组数值采样画成 ASCII 直方图。"""
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    counts = [0] * bins
    for v in values:
        idx = int((v - lo) / (hi - lo) * (bins - 1e-9))
        counts[idx] += 1
    peak = max(counts)
    print(f"  {label}   range=[{lo:.3g}, {hi:.3g}]   N={len(values)}")
    for i, c in enumerate(counts):
        bar = "#" * int(c / peak * width)
        edge = lo + (hi - lo) * i / bins
        print(f"  {edge:8.3g} |{bar:<{width}} {c}")


# ============================================================
# Demo 1 — 傅科摆 (Cambridge Tripos 经典计算题)
# ============================================================

def demo_foucault_pendulum():
    """傅科摆：你怎么知道地球在转？

    白话：在北极挂一个大摆球，你会看到摆动平面慢慢转动——
    其实摆没变，是地球在你脚下偷偷转。这就是傅科摆证明地球自转。

    反直觉：在剑桥（纬度 52.2°N），摆转一圈不是 24 小时，而是约 30.4 小时！
    因为只有"垂直分量"的地球转动才有效，要除以 sin(纬度)。
    类比：在旋转的唱片机上打台球——球的轨迹会被"扭曲"，但你站在
    唱机外看，球其实走的是直线。
    """
    banner("Demo 1 · 傅科摆 — 用一个摆证明地球在转")

    def rotation_period_hours(lat_deg):
        """T = 24h / sin(纬度)。北极 sin=1 即 24h，赤道 sin=0 即无穷大。"""
        s = math.sin(math.radians(lat_deg))
        return 24.0 / s if abs(s) > 1e-6 else float("inf")

    cities = [
        ("北极", 90.0),
        ("剑桥 Cambridge", 52.2),
        ("巴黎 Paris (1851 原版)", 48.85),
        ("伦敦 London", 51.5),
        ("赤道 Singapore", 1.35),
    ]
    print("  地点                       纬度      旋转一圈所需时间")
    print("  " + "-" * 58)
    for name, lat in cities:
        T = rotation_period_hours(lat)
        print(f"  {name:<26} {lat:>6.2f}°    {T:>8.2f} 小时")

    print("\n  Cambridge Tripos 题目：证明 T = 24h / sin(φ)")
    print("  推导：地球角速度 Ω 的垂直分量 = Ω·sin(φ)。摆感受到的有效")
    print("        牵连转动 = Ω·sin(φ)。所以周期 = 2π / (Ω sinφ) = 24h/sinφ。")
    cam_T = rotation_period_hours(52.2)
    print(f"\n  ✦ 在剑桥：T = 24h / sin(52.2°) = 24 / {math.sin(math.radians(52.2)):.4f}")
    print(f"         = {cam_T:.2f} 小时 ≈ 30 小时 24 分")
    print("  ✦ 反直觉：越靠近赤道转得越慢，赤道上完全不转！")

    # 模拟俯视图：摆平面方向角随时间的旋转
    print("\n  俯视剑桥大教堂的傅科摆 (24 小时观察)：")
    hours = list(range(0, 25, 2))
    for h in hours:
        angle = (h / cam_T) * 360.0  # 累计旋转角度
        rad = math.radians(angle)
        # 摆动方向单位向量
        dx, dy = math.cos(rad), math.sin(rad)
        # 画一个小箭头
        cx, cy = 20, 0
        ex, ey = cx + dx * 15, cy + dy * 8
        line = [" "] * 42
        line[20] = "+"
        # 简易箭头
        steps = 15
        for s in range(1, steps + 1):
            px = int(20 + dx * s)
            py = 0  # 单行展示
            if 0 <= px < 42:
                line[px] = "="
        head = int(20 + dx * steps)
        if 0 <= head < 42:
            line[head] = ">"
        print(f"  t={h:>2}h 角度={angle:>5.1f}°  " + "".join(line))
    print("\n  类比：唱片机上的台球——球走直线，但唱片在转，所以你看到弯曲。")


# ============================================================
# Demo 2 — 拉格朗日力学：从能量直接推运动方程
# ============================================================

def demo_lagrangian():
    """拉格朗日：为什么物理学家不再用 F=ma？

    白话：牛顿要你画所有力的箭头再分解，太累。拉格朗日说：
    只写"动能减势能"（L = T - V），套一个公式，运动方程自动出来。
    反直觉：为什么是"减"不是"加"？因为这是作用量 S = ∫L dt 取极小
    的最优路径——大自然是个"经济学家"，总选最省事的路径。
    类比：GPS 导航给你三条路，你选最短的——大自然也一样，光、
    抛物线、行星轨道，都是"最短路径"原则的产物。
    """
    banner("Demo 2 · 拉格朗日力学 — 一个公式替代所有受力分析")

    print("  系统：弹簧振子 (质量 m, 弹簧常数 k)")
    print("  坐标：x (偏离平衡位置)")
    print()
    print("  步骤 1：写动能 T = (1/2) m·ẋ²")
    print("  步骤 2：写势能 V = (1/2) k·x²")
    print("  步骤 3：拉格朗日量 L = T - V = (1/2)mẋ² - (1/2)kx²")
    print()
    print("  步骤 4：套 Euler-Lagrange 方程：")
    print("            d/dt(∂L/∂ẋ) - ∂L/∂x = 0")
    print("         => d/dt(m·ẋ) - (-k·x) = 0")
    print("         => m·ẍ + k·x = 0   ← 看，跟牛顿推出来的完全一样！")
    print()
    print("  ✦ 反直觉：根本不用画受力图！只要知道能量就够了。")
    print("  ✦ 对复杂系统（双摆、陀螺、场），牛顿法会崩溃，拉格朗日依然轻松。")

    # 数值验证：用 Verlet 积分
    m, k = 1.0, 4.0
    omega = math.sqrt(k / m)
    x, v, t, dt = 1.0, 0.0, 0.0, 0.05
    analytical = []
    numerical = []
    times = []
    while t < 4 * math.pi / omega:
        a = -k / m * x
        v += 0.5 * a * dt
        x += v * dt
        v += 0.5 * a * dt
        times.append(t)
        numerical.append(x)
        analytical.append(math.cos(omega * t))
        t += dt
    print("\n  数值积分 vs 解析解 cos(ωt)，ω = √(k/m):")
    print(f"  ω = √({k}/{m}) = {omega:.4f} rad/s   周期 T = {2*math.pi/omega:.4f} s")
    print()
    print("  时间      解析解      数值解      误差")
    for i in range(0, len(times), 6):
        t = times[i]
        a, n = analytical[i], numerical[i]
        print(f"  {t:6.2f}   {a:+.4f}    {n:+.4f}    {abs(a-n):.2e}")
    print("\n  误差 < 1e-4，证明拉格朗日推的方程和现实完全一致。")
    print("  类比：GPS 给三条路选最短——大自然选作用量最小的路径运动。")


# ============================================================
# Demo 3 — RC 电路充放电：电容器是"水箱"
# ============================================================

def demo_rc_transient():
    """RC 电路：电容器为什么会"慢慢"充满？

    白话：电容器像水桶，电池像水泵。泵把电荷灌进桶里，但桶里的
    水位越高，反推力越大，所以充电越来越慢——指数增长。
    反直觉：电容器永远"充不满"！理论上要无穷长时间，但实际上
    3-5 个时间常数后我们就当它满了。
    类比：用吸管给气球吹气，越鼓越费劲，最后你吹不动了。
    """
    banner("Demo 3 · RC 瞬态 — 电容器的指数充放电")
    R, C, V0 = 1000.0, 1e-6, 5.0  # 1kΩ, 1μF, 5V
    tau = R * C  # 时间常数
    print(f"  参数：R={R:.0f}Ω   C={C*1e6:.0f}μF   V₀={V0}V")
    print(f"  时间常数 τ = R·C = {tau*1e6:.0f} μs = {tau*1e3:.2f} ms")
    print()
    print("  充电公式：V(t) = V₀·(1 - e^(-t/τ))")
    print("  放电公式：V(t) = V₀·e^(-t/τ)")
    print()

    print("  充电过程：")
    print("  t/τ    V(t)/V₀   进度条")
    for k in range(0, 8):
        ratio = 1 - math.exp(-k)
        bar = "█" * int(ratio * 30)
        print(f"  {k}τ    {ratio:.4f}    [{bar:<30}]")

    print(f"\n  ✦ 反直觉：1τ 时只充 63.2%，3τ 才到 95%，永远到不了 100%。")
    print(f"  ✦ 工程经验法则：5τ 当作'充满' (99.3%)。")

    print("\n  充电曲线 V(t)/V₀ vs t/τ：")
    ascii_curve(lambda t: 1 - math.exp(-t), 0, 6, width=60, height=12,
                label="V/V₀")
    print("\n  放电曲线 V(t)/V₀ vs t/τ：")
    ascii_curve(lambda t: math.exp(-t), 0, 6, width=60, height=12,
                label="V/V₀")
    print("\n  类比：吹气球——越鼓越费劲，最后停在某个'差不多满'的状态。")


# ============================================================
# Demo 4 — LC 振荡：电场磁场跷跷板
# ============================================================

def demo_lc_oscillator():
    """LC 振荡：电能和磁能如何跳华尔兹？

    白话：电容器存电（电场能），线圈存磁（磁场能）。把充满电的
    电容接到线圈上，电荷来回冲，能量在两种形式间反复跳——振荡。
    反直觉：理想 LC 永远振荡不停！能量 100% 来回转换不损耗。
    实际电路有电阻，所以会衰减——这就是 RLC。
    类比：荡秋千——最高点全是势能，最低点全是动能，反复交换。
    """
    banner("Demo 4 · LC 振荡电路 — 电场与磁场的华尔兹")
    L, C = 1e-3, 1e-6  # 1mH, 1μF
    omega = 1 / math.sqrt(L * C)
    f = omega / (2 * math.pi)
    print(f"  参数：L={L*1e3:.0f}mH   C={C*1e6:.0f}μF")
    print(f"  谐振角频率 ω = 1/√(LC) = {omega:.0f} rad/s")
    print(f"  谐振频率   f = {f:.0f} Hz")
    print()
    print("  能量分配（总能量守恒 = 1）：")
    print("  t/T      电场能 U_E    磁场能 U_B    总能")
    for k in range(13):
        t = k / 12
        ue = math.cos(2 * math.pi * t) ** 2
        ub = math.sin(2 * math.pi * t) ** 2
        print(f"  {t:5.3f}    {ue:.4f}      {ub:.4f}      {ue+ub:.4f}")
    print()
    print("  ✦ 反直觉：电场最大时磁场为零，磁场最大时电场为零——跷跷板！")
    print("  ✦ 总能永远 = 1（理想情况下能量永不损失）。")

    print("\n  电场能 U_E (cos²ωt) 与磁场能 U_B (sin²ωt)：")
    ascii_curve(lambda t: math.cos(t) ** 2, 0, 2 * math.pi, width=60,
                height=10, label="U_E")
    ascii_curve(lambda t: math.sin(t) ** 2, 0, 2 * math.pi, width=60,
                height=10, label="U_B")
    print("  电容电压 V_C(t) = V₀·cos(ωt) — 跟简谐振子一模一样！")
    print("  这就是 Cavendish Lab 的核心直觉：电路 ≡ 力学系统。")
    print("\n  类比：荡秋千——势能和动能来回转换，能量不变。")


# ============================================================
# Demo 5 — 量子隧穿：穿墙术是真的
# ============================================================

def demo_quantum_tunneling():
    """量子隧穿：粒子能穿墙？

    白话：经典粒子撞墙会被弹回来。但量子粒子是"波"，波会渗进
    墙里——如果墙够薄，波能从另一边钻出来！这就是隧穿。
    反直觉：单个粒子"出现位置"是概率。它没"穿过"墙，它的波函数
    在墙另一边本来就有非零值——测量时它就"冒"出来。
    类比：往水桶里扔石子，石子可能直接出现在桶外——量子世界就这样。
    """
    banner("Demo 5 · 量子隧穿 — 粒子穿越势垒的概率")
    print("  势垒：高 V₀，宽 a。粒子能量 E < V₀（经典上绝对过不去）")
    print("  透射系数 T ≈ exp(-2κa)，κ = √(2m(V₀-E))/ℏ")
    print()

    def transmission(kappa_a):
        """简化的 T ~ e^(-2κa)。"""
        return math.exp(-2 * kappa_a)

    print("  透射概率 vs 势垒厚度（κa 从 0 到 3）：")
    ascii_curve(transmission, 0, 3, width=60, height=12,
                label="T")
    print()
    print("  κa     透射率 T      直觉")
    for ka in [0.5, 1.0, 1.5, 2.0, 3.0]:
        T = transmission(ka)
        bar = "█" * int(T * 40)
        note = "容易穿" if T > 0.2 else ("难穿" if T > 0.02 else "几乎不可能")
        print(f"  {ka:.1f}    {T:.4f}      [{bar:<40}] {note}")
    print()
    print("  ✦ 反直觉：哪怕墙又高又厚，T 永远 > 0，只是指数级小。")
    print("  ✦ 应用：太阳核聚变（质子隧穿库仑势垒）、STM 显微镜、")
    print("          放射性 α 衰变——全靠隧穿。")
    print("  ✦ 剑桥 Cavendish 当年测 α 衰变实验，正是验证隧穿效应。")
    print("\n  类比：扔 100 万次骰子，'6'连续出现 7 次的概率虽小，但不是零。")


# ============================================================
# Demo 6 — 量子谐振子：能级是楼梯不是斜坡
# ============================================================

def demo_qm_harmonic_oscillator():
    """量子谐振子：能量为什么是"一份一份"的？

    白话：弹簧振子经典上能量可以是任意值。但量子力学说：
    能量只能取 (n + 1/2)ℏω，n=0,1,2,...——像楼梯，不能站在半空。
    反直觉：最低能量（n=0）不是零！是 (1/2)ℏω，叫"零点能"。
    原因是海森堡不确定性——你不能同时停在原点且速度为零。
    类比：在钢琴键上只能按某个键（离散音高），不能按半键。
    """
    banner("Demo 6 · 量子谐振子能级 — 楼梯不是斜坡")
    hbar_w = 1.0  # 用 ℏω=1 做单位
    print(f"  能量公式：E_n = (n + 1/2)·ℏω")
    print(f"  单位：ℏω = {hbar_w:.1f}（设为 1）")
    print()
    print("  能级图 (能量从下到上)：")
    for n in range(7, -1, -1):
        E = (n + 0.5) * hbar_w
        level = " " * int(E * 4) + "━" * 20
        print(f"  n={n}  E={E:.1f}ℏω  {level}")
    print("          " + "^" * 5 + " 零点能 E₀ = ½ℏω ≠ 0")
    print()
    print("  ✦ 反直觉：n=0 时已经有一半的能量，分子在绝对零度也在抖！")
    print("  ✦ 液氦在常压下永不凝固——就是因为零点能太大压不下去了。")

    # 波函数：用 Hermite 多项式的递推
    def hermite(n, x):
        if n == 0:
            return 1.0
        if n == 1:
            return 2 * x
        h0, h1 = 1.0, 2 * x
        for k in range(2, n + 1):
            h0, h1 = h1, 2 * x * h1 - 2 * (k - 1) * h0
        return h1

    def psi(n, x):
        """无量纲谐振子波函数 ψ_n(x)，α=1。"""
        norm = 1.0 / math.sqrt(2 ** n * math.factorial(n) * math.sqrt(math.pi))
        return norm * hermite(n, x) * math.exp(-x * x / 2)

    print("\n  基态波函数 ψ₀(x) — 钟形高斯分布：")
    ascii_curve(lambda x: psi(0, x), -3, 3, width=60, height=10,
                label="ψ₀")
    print("\n  第一激发态 ψ₁(x) — 有一个节点：")
    ascii_curve(lambda x: psi(1, x), -3, 3, width=60, height=10,
                label="ψ₁")
    print("\n  n=4 波函数 ψ₄(x) — 振荡激烈，4 个节点：")
    ascii_curve(lambda x: psi(4, x), -4, 4, width=60, height=10,
                label="ψ₄")
    print("\n  类比：钢琴键只能按离散的键——量子世界的能量也是分立的。")


# ============================================================
# Demo 7 — 麦克斯韦妖：信息能换成熵吗？
# ============================================================

def demo_maxwell_demon():
    """麦克斯韦妖：一只会分类的小妖能违反热力学第二定律吗？

    白话：箱子里有快慢分子混在一起。假设有个小妖守门，让快的去一边、
    慢的去另一边。结果一边变热一边变冷——熵减少！违反第二定律？
    反直觉：妖不违反定律！因为它要"看"分子速度必须消耗能量/产生熵，
    Landauer 原理说：擦除 1 bit 信息至少耗散 kT·ln2 的热。
    类比：你整理房间时房间变干净了，但你出汗了——熵转移到了环境。
    """
    banner("Demo 7 · 麦克斯韦妖 — 信息即物理")
    random.seed(42)
    N = 4000
    # 初始：均匀分布的"速度"（用高斯近似）
    def sample_speed():
        return sum(random.uniform(-3, 3) for _ in range(4))  # 近高斯

    initial = [sample_speed() for _ in range(N)]
    print(f"  模拟：{N} 个分子，初始速度服从麦克斯韦-玻尔兹曼分布")
    print(f"\n  === 第 0 步：初始平衡态（两边温度相同）===")
    ascii_histogram(initial, bins=18, width=40, label="速度分布")

    # 妖开工：分成左右两箱
    left = []   # 慢箱
    right = []  # 快箱
    threshold = 0.0
    for v in initial:
        if v < threshold:
            left.append(v)
        else:
            right.append(v)
    print(f"\n  === 第 1 步：小妖分类后（左箱=慢/冷，右箱=快/热）===")
    print(f"  左箱 N={len(left)}, <v>={sum(left)/len(left):+.3f}")
    print(f"  右箱 N={len(right)}, <v>={sum(right)/len(right):+.3f}")
    ascii_histogram(left, bins=18, width=40, label="左箱(冷)")
    ascii_histogram(right, bins=18, width=40, label="右箱(热)")

    # 平均动能（与 T 成正比）
    KE_left = sum(v * v for v in left) / len(left)
    KE_right = sum(v * v for v in right) / len(right)
    print(f"\n  左箱 <v²> = {KE_left:.3f}  →  冷")
    print(f"  右箱 <v²> = {KE_right:.3f}  →  热")
    print(f"  温度差建立了！熵看似减少了。")
    print()
    kB = 1.38e-23
    T = 300.0
    bits_erased = N
    landauer_heat = bits_erased * kB * T * math.log(2)
    print(f"  ✦ Landauer 原理：妖擦除 {N} bit 信息至少耗散")
    print(f"    Q_min = N·kT·ln2 = {landauer_heat:.2e} J")
    print(f"  ✦ 这部分熵增 ≥ 系统熵减，第二定律得救！")
    print(f"  ✦ 反直觉：'信息'是物理的，思考也要耗能。")
    print("\n  类比：整理房间让你出汗——你减少的熵 < 环境增加的熵。")


# ============================================================
# Demo 8 — 卡文迪许实验：称地球
# ============================================================

def demo_cavendish_experiment():
    """卡文迪许实验：怎么"称"地球？

    白话：1798 年卡文迪许用一个扭转秤，测了两对铅球之间的引力，
    第一次精确测出万有引力常数 G，从而"称出"地球质量。
    反直觉：两个 1 公斤的铅球之间的引力比一粒灰尘还小（~10^-10 N），
    但卡文迪许用一根细丝的扭转，把它放大到可测。
    类比：用一根头发丝吊着重物， slightest breeze 都能让它转——
    卡文迪许就是把"微风"换成了"引力"。
    """
    banner("Demo 8 · 卡文迪许扭转秤 — 称量地球 (Cavendish Lab 之源)")
    G = 6.674e-11  # 引力常数
    M_earth = 5.972e24
    R_earth = 6.371e6
    print(f"  目标：测 G → 推出地球质量 M⊕")
    print(f"  原理：两个大铅球(M)吸引两个小米球(m)，悬丝扭转角度 θ")
    print()

    # 卡文迪什原始参数
    M_big = 158.0      # kg
    m_small = 0.73     # kg
    d = 0.225          # m，大小球距离
    L = 1.86           # m，横杆长
    kappa_torsion = 1e-9  # 简化扭转系数

    F = G * M_big * m_small / d ** 2
    theta = F * L / kappa_torsion  # 简化的平衡角度
    print(f"  参数：M={M_big}kg  m={m_small}kg  d={d}m  L={L}m")
    print(f"  引力 F = G·M·m/d² = {F:.3e} N   (比蚊子的重量还小！)")
    print(f"  扭转角 θ ≈ F·L/κ ≈ {theta:.3e} rad ≈ {math.degrees(theta):.4f}°")
    print()

    # 反推 G
    # 用地球表面重力 g = G·M⊕/R² → M⊕ = g·R²/G
    g = 9.81
    M_inferred = g * R_earth ** 2 / G
    print(f"  由 g = G·M⊕/R² 反推地球质量：")
    print(f"  M⊕ = g·R²/G = {g}×({R_earth:.3e})²/{G:.3e}")
    print(f"      = {M_inferred:.3e} kg  (实际值 {M_earth:.3e} kg)")
    print()
    print("  ✦ 反直觉：他没真去'称'地球，只是测了 G，然后由地表 g 反推。")
    print("  ✦ 卡文迪许原话是'称量地球' (weighing the world)。")
    print(f"  ✦ 当时精度已能确定地球平均密度 ≈ 5.5 g/cm³（实为 5.51）。")
    print()
    print("  大小球引力 vs 常见力：")
    forces = [
        ("卡文迪许大小球引力", F),
        ("一粒灰尘重量", 1e-9),
        ("蚊子重量", 1e-6),
        ("苹果重量", 1.0),
        ("人重量", 700.0),
    ]
    for name, f in forces:
        print(f"    {name:<22} = {f:.2e} N")
    print("\n  类比：用头发丝悬挂物体——微风也能让它转，这就是放大效应。")


# ============================================================
# 主入口
# ============================================================

DEMOS = [
    ("傅科摆：证明地球在转", demo_foucault_pendulum),
    ("拉格朗日力学：能量法推运动方程", demo_lagrangian),
    ("RC 瞬态：电容充电放电", demo_rc_transient),
    ("LC 振荡：电场磁场华尔兹", demo_lc_oscillator),
    ("量子隧穿：穿墙术", demo_quantum_tunneling),
    ("量子谐振子：能级楼梯", demo_qm_harmonic_oscillator),
    ("麦克斯韦妖：信息即物理", demo_maxwell_demon),
    ("卡文迪许秤：称量地球", demo_cavendish_experiment),
]


def main():
    import sys
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   Cambridge 物理演示 · 费曼式可视化  (Natural Sciences Tripos) ║")
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
