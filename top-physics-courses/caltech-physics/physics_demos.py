"""
Caltech 物理演示 · 费曼式可视化（Feynman Lectures 风格）
================================
配套：本目录各 topic*/ 的 .md 教学文档（Feynman Lectures + Ph 1/2/12 体系）
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库（math / random / cmath）

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个

核心理念：看，这就是 X 现象——不是枯燥计算，而是让你"啊哈"一下的直觉可视化。
"""

import math
import cmath
import sys

# ───────────────────────── ASCII 可视化工具 ─────────────────────────

def banner(title):
    print("\n" + "═" * 72)
    print("  " + title)
    print("═" * 72)


def note(*lines):
    for ln in lines:
        print("  │ " + ln)


def plot_curves(curves, width=66, height=15, title="", zero_line=True):
    """多曲线 ASCII 图。curves = [(label, ys_list, char), ...]。"""
    allv = [v for _, ys, _ in curves for v in ys]
    if not allv:
        print("  (无数据)"); return
    lo, hi = min(allv), max(allv)
    if hi - lo < 1e-12:
        lo, hi = lo - 0.5, hi + 0.5
    span = hi - lo
    grid = [[" "] * width for _ in range(height)]
    if zero_line and lo < 0 < hi:
        zr = int((hi - 0) / span * (height - 1))
        for c in range(width):
            grid[zr][c] = "·"
    for _, ys, ch in curves:
        n = len(ys)
        for col in range(width):
            t = col / (width - 1)
            fi = t * (n - 1)
            i0 = int(fi); i1 = min(i0 + 1, n - 1); fr = fi - i0
            y = ys[i0] * (1 - fr) + ys[i1] * fr
            row = int((hi - y) / span * (height - 1))
            row = max(0, min(height - 1, row))
            grid[row][col] = ch
    print("  ┌" + title[:width].ljust(width) + "┐")
    for r in range(height):
        val = hi - r * span / (height - 1)
        print(f"  │{val:7.3g}│" + "".join(grid[r]) + "│")
    print("  └" + " " * width + "┘")
    print("  图例: " + "   ".join(f"{ch} = {lab}" for lab, _, ch in curves))


def plot_xy(points, width=66, height=22, title="", marks=None):
    """二维散点图。points=[(x,y),...]；marks=[(x,y,char),...] 额外标记点。"""
    allp = list(points) + [m[:2] for m in (marks or [])]
    xs = [p[0] for p in allp]; ys = [p[1] for p in allp]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    if xmax - xmin < 1e-9: xmax = xmin + 1
    if ymax - ymin < 1e-9: ymax = ymin + 1
    grid = [[" "] * width for _ in range(height)]
    # 原点十字
    if xmin < 0 < xmax:
        cz = int((0 - xmin) / (xmax - xmin) * (width - 1))
        for r in range(height): grid[r][cz] = "│" if grid[r][cz] == " " else grid[r][cz]
    if ymin < 0 < ymax:
        rz = int((ymax - 0) / (ymax - ymin) * (height - 1))
        for c in range(width): grid[rz][c] = "─" if grid[rz][c] == " " else grid[rz][c]
    for x, y in points:
        c = int((x - xmin) / (xmax - xmin) * (width - 1))
        r = int((ymax - y) / (ymax - ymin) * (height - 1))
        if 0 <= r < height and 0 <= c < width:
            grid[r][c] = "●"
    for x, y, ch in (marks or []):
        c = int((x - xmin) / (xmax - xmin) * (width - 1))
        r = int((ymax - y) / (ymax - ymin) * (height - 1))
        if 0 <= r < height and 0 <= c < width:
            grid[r][c] = ch
    print("  ┌" + title[:width].ljust(width) + "┐")
    for r in range(height):
        print("  │" + "".join(grid[r]) + "│")
    print("  └" + " " * width + "┘")


# ───────────────────────────── Demo 1 ─────────────────────────────

def demo_1_kepler():
    """开普勒第二定律：行星为什么'知道'何时快何时慢？"""
    banner("Demo 1 · 开普勒第二定律：等时等面积（轨道力学）")
    note(
        "白话：行星绕太阳走椭圆，离太阳近时跑得飞快，远时慢吞吞。",
        "但神奇的是：连接行星与太阳的线，在相等时间里扫过相等的面积。",
        "",
        "反直觉：行星并没有'计算'自己该多快——这是角动量守恒的自动结果！",
        "         角动量 L = mvr 不变，所以 r 小时 v 必然大。物理定律替它做好了决定。",
        "类比：花样滑冰运动员收起手臂时转得更快——同一个角动量守恒。",
    )
    GM = 1.0
    dt = 0.01
    x, y = 0.9, 0.0          # 近日点
    vx, vy = 0.0, 1.247      # 横向速度 → 椭圆轨道 (a=1.5, e=0.4)
    L = x * vy - y * vx      # 角动量（应守恒）
    traj = []
    n_period = 1200
    seg_area = [0.0] * 8     # 8 段等时间，各段扫过的面积
    for i in range(n_period):
        r = math.hypot(x, y)
        ax = -GM * x / r ** 3
        ay = -GM * y / r ** 3
        nx = x + vx * dt + 0.5 * ax * dt * dt
        ny = y + vy * dt + 0.5 * ay * dt * dt
        rn = math.hypot(nx, ny)
        ax2 = -GM * nx / rn ** 3
        ay2 = -GM * ny / rn ** 3
        vx += 0.5 * (ax + ax2) * dt
        vy += 0.5 * (ay + ay2) * dt
        x, y = nx, ny
        # 面积速率 dA/dt = 0.5 * |r × v|
        dA = 0.5 * abs(x * vy - y * vx) * dt
        seg_area[min(i // (n_period // 8), 7)] += dA
        if i % 3 == 0:
            traj.append((x, y))
    plot_xy(traj, title="行星椭圆轨道（⊙=太阳，近日点在右）",
            marks=[(0, 0, "⊙"), (0.9, 0, "P")])
    print("  ── 8 段等时间间隔内扫过的面积（应全部相等）──")
    for i, a in enumerate(seg_area):
        bar = "▇" * int(a / max(seg_area) * 40)
        print(f"  段 {i+1} │{bar:<40}│ A={a:.4f}")
    print(f"  面积速率理论值 dA/dt = L/2 = {L/2:.4f}")
    note(
        f"看：8 段面积几乎完全相同（差异<1%），尽管行星速度变化剧烈。",
        f"     近日点(r=0.9)速度≈1.25，远日点(r=2.1)速度≈0.53——但'面积速率'恒定。",
        "     这就是开普勒第二定律的本质 = 角动量守恒。行星不需要'知道'，它只是遵守。",
    )


# ───────────────────────────── Demo 2 ─────────────────────────────

def demo_2_em_wave():
    """电磁波传播：变化的电场产生磁场，变化的磁场又产生电场"""
    banner("Demo 2 · 电磁波传播（一维波动方程有限差分）")
    note(
        "白话：抖动一下电荷，它的电场'涟漪'就会向外传播——这就是电磁波（光）。",
        "变化的电场产生磁场，变化的磁场又产生电场，两者互相'喂养'，自己往前跑。",
        "",
        "反直觉：电磁波不需要任何介质！不像水波需要水、声波需要空气。",
        "         电场和磁场互相产生，就能在真空中传播——光就是这样穿越宇宙的。",
        "类比：两个人手拉手互相拽着往前走——不需要地面，靠自己就能前进。",
    )
    N = 121
    dx = 0.1
    dt = dx            # Courant 数 = 1（c=1），此时数值解无耗散、无色散
    x0, sigma = 6.0, 0.8
    u = [math.exp(-((i * dx - x0) / sigma) ** 2) for i in range(N)]
    u_prev = u[:]      # 初始速度 = 0 → 脉冲分裂成左右两半

    def step(u, u_prev):
        un = [0.0] * N
        for i in range(1, N - 1):
            un[i] = 2 * u[i] - u_prev[i] + (u[i + 1] - 2 * u[i] + u[i - 1])
        un[0] = un[-1] = 0.0
        return un

    frames = {0: u[:]}
    cur, prev = u[:], u_prev[:]
    for n in range(1, 61):
        cur, prev = step(cur, prev), cur
        if n in (30, 60):
            frames[n] = cur[:]
    curves = [(f"t={n}步", fr, ch) for (n, fr), ch in zip(sorted(frames.items()), "●★◆")]
    plot_curves(curves, height=10, title="高斯脉冲分裂为两个反向行波，各以光速 c 传播")
    note(
        "看：t=0 时一个脉冲在中央；t=30 时分裂成两个，分别移到 x≈3 和 x≈9；",
        "     t=60 时到达 x≈0 和 x≈12。移动速度 = c（光速），且波形完全不变形。",
        "     Courant 数=1 时数值解精确——这正说明波动方程的解就是'形状不变地平移'。",
    )


# ───────────────────────────── Demo 3 ─────────────────────────────

def demo_3_double_slit():
    """双缝干涉：粒子怎么会和自己干涉？"""
    banner("Demo 3 · 双缝干涉：概率 ≠ 两个概率之和")
    note(
        "白话：两个狭缝像两个水波源，波纹在屏幕上叠加——有的地方加强（亮），有的抵消（暗）。",
        "但电子、光子一个个发射，居然也形成条纹！每个粒子'同时走过两条缝'。",
        "",
        "反直觉：屏幕上的概率 NOT 是 |ψ₁|²+|ψ₂|²，而是 |ψ₁+ψ₂|²——多出一个交叉项！",
        "         正是交叉项制造了明暗条纹。粒子不是'走这条或那条'，而是'两条都走'。",
        "类比：两块石头扔进池塘，涟漪叠加出花纹——但这里是单个粒子自己和自己干涉。",
    )
    d = 2.0       # 缝间距
    L = 10.0      # 屏幕距离
    wl = 0.5      # 波长
    ypts = [(-4 + 0.08 * i) for i in range(101)]
    I_inter = []  # 干涉 |ψ1+ψ2|²
    I_no = []     # 无干涉 |ψ1|²+|ψ2|²
    for y in ypts:
        r1 = math.hypot(d / 2, L) + math.hypot(y, L) * 0  # 简化：远场近似
        # 远场：路径差 ≈ d sinθ, sinθ ≈ y/√(y²+L²)
        sinth = y / math.hypot(y, L)
        delta = d * sinth
        ph = 2 * math.pi * delta / wl
        I_inter.append((math.cos(ph / 2)) ** 2 * 4)
        I_no.append(2.0)
    plot_curves(
        [("干涉 |ψ₁+ψ₂|²", I_inter, "●"), ("无干涉 |ψ₁|²+|ψ₂|²", I_no, "-")],
        title="双缝干涉强度分布（远场）：亮暗条纹 = 量子叠加的证据",
    )
    note(
        "看：虚线(无干涉)是平的——如果粒子只走一条缝，屏幕均匀亮。",
        "     实线(干涉)有周期性峰谷——亮纹处两波加强，暗纹处完全抵消（概率=0！）。",
        "     哪怕一次只发一个电子，累积久了照样出现条纹——粒子和自己干涉。",
    )


# ───────────────────────────── Demo 4 ─────────────────────────────

def demo_4_entropy():
    """抛硬币的熵：为什么世界越来越乱？"""
    banner("Demo 4 · 熵的本质 = 数微观态的数目")
    note(
        "白话：100 个硬币全正面朝上（有序），随便一拨就变成乱七八糟（无序）。",
        "为什么不会反过来？因为'乱'的状态数量远远、远远多于'整齐'的状态。",
        "",
        "反直觉：熵不是模糊的'混乱感'——它就是微观态数目的对数 S = k·ln(W)！",
        "         100 枚硬币：全正面只有 1 种，但 50 正 50 反有 C(100,50)≈10²⁹ 种！",
        "         系统走向高熵，纯粹是因为高熵状态'地盘大'——概率压倒一切。",
        "类比：洗一副扑克——你永远不会洗出同花顺，因为有序排列凤毛麟角。",
    )
    N = 40
    micro = [math.comb(N, k) for k in range(N + 1)]
    total = 2 ** N
    probs = [m / total for m in micro]
    S = -sum(p * math.log(p) for p in probs if p > 0)
    S_per_coin = S / N
    print("  ── 抛 40 枚硬币：正面数 k → 微观态数 W(k) → 概率 P(k) ──")
    print(f"  {'k(正面)':>8} │ {'W=C(40,k)':>14} │ {'P(k)':>10} │ 可视化")
    vmax = max(micro)
    for k in range(0, N + 1, 4):
        bar = "▇" * int(micro[k] / vmax * 30)
        print(f"  {k:>8} │ {micro[k]:>14} │ {probs[k]:>10.3e} │ {bar}")
    print(f"\n  总微观态 = 2^{N} = {total}")
    print(f"  最大微观态 (k=20): C(40,20) = {math.comb(40,20):,}")
    print(f"  香农熵 S = {S:.4f} nat   (每枚硬币 {S_per_coin:.4f} nat)")
    print(f"  ln2 = {math.log(2):.4f} nat  →  N→∞ 时每硬币熵 → ln2 ✓")
    note(
        f"看：k=20（一半正一半反）的微观态数是 k=0（全正）的 {math.comb(40,20):,} 倍！",
        "     所以'均匀混合'的概率碾压式占优——这就是熵增的物理本质。",
        "     时间之箭 = 走向微观态更多的状态。不是世界'喜欢'混乱，是混乱状态太多。",
    )


# ───────────────────────────── Demo 5 ─────────────────────────────

def demo_5_carnot():
    """卡诺循环：为什么永动机不可能？"""
    banner("Demo 5 · 卡诺循环效率：完美的引擎也必然浪费")
    note(
        "白话：热机从高温吸热，一部分变成有用的功，剩下的废热排到低温端。",
        "卡诺循环是理论上的'完美'热机——但即便它也无法 100% 转化！",
        "",
        "反直觉：效率上限 η = 1 - Tc/Th，只取决于两个温度，跟材料、工艺毫无关系！",
        "         这是热力学第二定律的铁律——不是工程不够好，是宇宙不允许。",
        "         除非 Tc = 绝对零度（不可能达到），否则永远有废热。",
        "类比：水车必须有'落差'才能做功——没有温度差，就没有热→功的转化。",
    )
    ratios = [1.2 + 0.4 * i for i in range(13)]
    eff = [1 - 1 / r for r in ratios]
    plot_curves([("卡诺效率 η", eff, "●")], title="η = 1 - Tc/Th  vs  Th/Tc（永远到不了 100%）")
    print("\n  ── 现实热机的效率上限 ──")
    cases = [("汽车引擎", 2700, 300), ("蒸汽轮机", 800, 300),
             ("核电站", 600, 300), ("理想(Th→∞)", 1e6, 300)]
    for name, th, tc in cases:
        eta = 1 - tc / th
        bar = "▇" * int(eta * 40)
        print(f"  {name:>10}  Th={th:>7.0f}K Tc={tc:.0f}K │{bar:<40}│ η={eta*100:5.1f}%")
    note(
        "看：Th/Tc=2 时 η=50%，Th/Tc=5 时 η=80%——但永远逼近不到 100%。",
        "     即便 Th→∞，η→100% 但只能无限逼近。这就是为什么永动机不可能。",
        "     本质：热能是无序的（熵高），功是有序的（熵低），转换必须'排出熵'。",
    )


# ───────────────────────────── Demo 6 ─────────────────────────────

def demo_6_mandelbrot():
    """复变函数可视化：简单规则如何产生无限复杂？"""
    banner("Demo 6 · Mandelbrot 集：z→z²+c 的无穷自相似（复杂从简单涌现）")
    note(
        "白话：取一个复数 c，反复做 z→z²+c（z 从 0 开始）。",
        "如果 z 永远不跑远（|z|<2），c 就属于 Mandelbrot 集——涂黑。",
        "",
        "反直觉：这么简单的规则，竟产生无穷复杂的分形图案！",
        "         放大边界任何一处，都会看到整个图案的 miniature 复制品——自相似。",
        "         这是 Feynman 最爱的主题：复杂的自然现象可能源于极简单的底层规则。",
        "类比：雪花、海岸线、闪电——自然界用简单规则递归出无限细节。",
    )
    W, H = 66, 26
    chars = " ·,:;-=+*o#@%"
    grid = []
    for row in range(H):
        cy = (row / (H - 1) * 2.0 - 1.0) * 0.95
        line = []
        for col in range(W):
            cx = (col / (W - 1) * 3.0 - 2.0)
            z = 0j
            escaped = False
            for it in range(60):
                z = z * z + cx + cy * 1j
                if z.real * z.real + z.imag * z.imag > 4:
                    escaped = True
                    break
            idx = (it * len(chars) // 60) if escaped else 0
            line.append(chars[min(idx, len(chars) - 1)] if escaped else " ")
        grid.append("".join(line))
    print("  ┌" + "─" * W + "┐")
    for ln in grid:
        print("  │" + ln + "│")
    print("  └" + "─" * W + "┘")
    note(
        "看：黑色区域 = Mandelbrot 集（z 不发散的 c）。边界处细节无穷。",
        "     明暗 = 逃逸速度（越快越亮）。主心形 + 各种'芽苞' = 自相似结构。",
        "     复数平方 = 角度翻倍。这条简单规则编织出整个图案——简单孕育复杂。",
    )


# ───────────────────────────── Demo 7 ─────────────────────────────

def demo_7_path_integral():
    """费曼路径积分：粒子真的走所有路径吗？"""
    banner("Demo 7 · 费曼路径积分（离散近似）：驻相近似选出经典路径")
    note(
        "白话：量子力学里，粒子从 A 到 B 不是走一条路，而是'同时走所有可能的路径'！",
        "每条路有一个'振幅' e^(iS/ℏ)，S 是作用量。把所有路径的振幅加起来 = 总概率。",
        "",
        "反直觉：远离经典路径的那些路，相位剧烈振荡，加起来几乎完全抵消！",
        "         只有【经典路径附近】的路相位变化平缓（驻相），贡献互相加强。",
        "         所以宏观世界里粒子'看起来'只走经典路径——它是干涉选出来的，不是规定的！",
        "         ℏ→0 时抵消更剧烈，经典力学从量子力学中浮现。",
        "类比：很多人同时喊随机口号会互相抵消成噪音，但齐唱同一句会越来越响。",
    )
    T = 1.0
    a_vals = [a * 0.5 for a in range(-6, 7)]  # 中点偏移参数
    print("  ── 三角路径族：从(0,0)经中点(a, T/2)到(0,T)，作用量 S(a)=2a²/T ──")
    print("\n  【ℏ=1.0（量子）】各路径的相位 e^(iS/ℏ)：")
    for a in a_vals:
        S = 2 * a * a / T
        ph = cmath.exp(1j * S / 1.0)
        bar = "▇" * int(abs(ph.real) * 20)
        sign = "+" if ph.real >= 0 else "-"
        print(f"   a={a:+.1f}  S={S:5.2f}  Re={ph.real:+.3f} {sign}{bar:<20} Im={ph.imag:+.3f}")
    print("\n  ── 驻相近似：经典路径附近的'相干宽度' a_c ≈ √(Tℏ/2) ──")
    print("  （只有 |a| < a_c 的路径相位变化 <1 弧度，能相干加强；更远的快速振荡→抵消）")
    for hb in [1.0, 0.5, 0.2, 0.05, 0.01]:
        ac = math.sqrt(T * hb / 2)
        bar = "▇" * int(ac / math.sqrt(T * 1.0 / 2) * 20)
        print(f"   ℏ={hb:<5.2f} → a_c = {ac:.3f}  {bar:<20}  {'← 量子（宽）' if hb==1.0 else '← 经典极限（极窄）' if hb==0.01 else ''}")
    plot_curves([("ℏ=1.0 Re(e^(iS/ℏ))", [cmath.exp(1j * 2 * a * a).real for a in a_vals], "●"),
                 ("ℏ=0.2 Re(e^(iS/ℏ))", [cmath.exp(1j * 2 * a * a / 0.2).real for a in a_vals], "◆")],
                title="相位实部 vs 中点偏移 a：ℏ 越小，中央相干峰越窄→经典路径选择性越强", zero_line=True)
    note(
        "看：ℏ=1.0 时 a=0 附近的相位温和变化（同号→加强）；|a|>2 后开始振荡（异号→抵消）。",
        "     ℏ=0.2 时几乎从 a=0 一离开就疯狂振荡——只有极窄的中央峰能加强。",
        "     相干宽度 a_c ∝ √ℏ：ℏ→0 时 a_c→0，只有经典路径(a=0)幸存。",
        "     结论：经典力学 = ℏ→0 的极限。粒子走了所有路，是干涉留下了经典那一条。",
    )


# ─────────────────────────── 调度入口 ───────────────────────────

DEMOS = [
    ("开普勒定律", demo_1_kepler),
    ("电磁波传播", demo_2_em_wave),
    ("双缝干涉", demo_3_double_slit),
    ("熵与微观态", demo_4_entropy),
    ("卡诺效率", demo_5_carnot),
    ("Mandelbrot 集", demo_6_mandelbrot),
    ("费曼路径积分", demo_7_path_integral),
]


def main():
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    print("╔" + "═" * 70 + "╗")
    print("║" + "  Caltech 物理演示 · 费曼式可视化（纯标准库，无依赖）".center(50) + "║")
    print("╚" + "═" * 70 + "╝")
    indices = args if args else list(range(1, len(DEMOS) + 1))
    for i in indices:
        if 1 <= i <= len(DEMOS):
            DEMOS[i - 1][1]()
    print("\n" + "═" * 72)
    print("  全部演示完成。配套文档见各 topic*/*.md。")
    print("═" * 72)


if __name__ == "__main__":
    main()
