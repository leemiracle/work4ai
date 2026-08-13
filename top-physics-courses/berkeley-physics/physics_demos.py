"""
UC Berkeley 物理演示 · 费曼式可视化
================================
配套：本目录各 topic*/ 的 .md 教学文档（Berkeley Physics Course 经典 5 卷 + 7A/8A 体系）
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库（math / random / cmath）

运行：
    python3 physics_demos.py            # 跑全部
    python3 physics_demos.py 3 5        # 只跑第 3 和第 5 个

核心理念：看，这就是 X 现象——不是枯燥计算，而是让你"啊哈"一下的直觉可视化。
"""

import math
import random
import cmath
import sys

# ───────────────────────── ASCII 可视化工具 ─────────────────────────

def banner(title):
    print("\n" + "═" * 72)
    print("  " + title)
    print("═" * 72)


def note(*lines):
    """打印一段说明（左侧带竖线，像引用块）。"""
    for ln in lines:
        print("  │ " + ln)


def plot_curves(curves, width=66, height=15, title="", zero_line=True):
    """多曲线 ASCII 图。curves = [(label, ys_list, char), ...]。
    横轴=采样序号(0..len-1)，纵轴=数值。自动缩放。"""
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
    nmax = max(len(ys) for _, ys, _ in curves)
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
    leg = "  图例: " + "   ".join(f"{ch} = {lab}" for lab, _, ch in curves)
    print(leg[:width + 20])


def plot_bars(values, width=60, title="", unit=""):
    """水平柱状图（归一化到 width）。values = [(label, value), ...]。"""
    if not values:
        print("  (无数据)"); return
    vmax = max(abs(v) for _, v in values) or 1.0
    print("  ── " + title + " ──")
    for lab, v in values:
        nbar = int(round(abs(v) / vmax * width))
        sign = "+" if v >= 0 else "-"
        print(f"  {lab:>8} │{sign * nbar:<{width}}│ {v:9.4g}{unit}")


# ───────────────────────────── Demo 1 ─────────────────────────────

def demo_1_harmonic():
    """谐振子：为什么弹簧会来回振动？—— Euler vs Verlet 能量守恒"""
    banner("Demo 1 · 谐振子数值积分：Euler 发散，Verlet 守恒")
    note(
        "白话：拉一下弹簧再松手，它就来回振动，永不停止（没有摩擦的话）。",
        "位置偏离平衡点越远，被拉回来的力越大——这就是'回复力' F = -kx。",
        "",
        "反直觉：用最朴素的 Euler 法做数值积分，能量会越积越多（弹簧越振越猛）！",
        "         必须用 Verlet（蛙跳）法——一种'辛'积分器——才能保能量守恒。",
        "类比：秋千（无阻尼谐振子）；汽车减震器（阻尼谐振子）。",
        "      Euler 像个每次交易都向上取整的糊涂会计；Verlet 是复式记账的好会计。",
    )
    omega = 1.0
    dt = 0.1
    steps = 400
    x0, v0 = 1.0, 0.0
    E0 = 0.5 * v0 ** 2 + 0.5 * omega ** 2 * x0 ** 2

    # 显式 Euler 法：用【旧值】同时更新位置和速度——这个会能量发散！
    # （注意：若用"先更新速度再更新位置"的半隐式 Euler/Cromer，反而会守恒，
    #   那是辛积分器。这里特意用显式 Euler 来展示它的致命缺陷。）
    xe, ve = x0, v0
    e_euler = []
    for i in range(steps):
        xe_new = xe + ve * dt
        ve_new = ve - omega ** 2 * xe * dt   # 用旧的 xe
        xe, ve = xe_new, ve_new
        if i % 4 == 0:
            e_euler.append(0.5 * ve ** 2 + 0.5 * omega ** 2 * xe ** 2)

    # 速度 Verlet 法
    xv, vv = x0, v0
    e_verlet = []
    for i in range(steps):
        a = -omega ** 2 * xv
        xv += vv * dt + 0.5 * a * dt * dt
        a2 = -omega ** 2 * xv
        vv += 0.5 * (a + a2) * dt
        if i % 4 == 0:
            e_verlet.append(0.5 * vv ** 2 + 0.5 * omega ** 2 * xv ** 2)

    plot_curves(
        [("Euler（发散！）", e_euler, "E"),
         ("Verlet（守恒）", e_verlet, "V"),
         ("真实能量", [E0] * len(e_verlet), "-")],
        title=f"机械能随时间演化  (E₀={E0:.3f}, dt={dt})",
    )
    note(
        f"看：Euler 的能量从 {E0:.3f} 漂移到 {e_euler[-1]:.3f}（+{(e_euler[-1]/E0-1)*100:.0f}%），",
        f"     而 Verlet 始终在 {min(e_verlet):.4f}~{max(e_verlet):.4f} 之间振荡（数值精度内守恒）。",
        "启示：模拟行星轨道、分子动力学时，必须用辛积分器，否则系统会假性'发热'。",
    )


# ───────────────────────────── Demo 2 ─────────────────────────────

def demo_2_electric_field():
    """电场线可视化（Purcell 风格）：偶极子的场长什么样？"""
    banner("Demo 2 · 电偶极子的电场线（Purcell / Berkeley Vol.2 风格）")
    note(
        "白话：正电荷像泉水往外喷，负电荷像下水道往里吸。",
        "电场线就是'如果放一个正试探电荷，它会被推着走的路径'。",
        "",
        "反直觉：电场线永远不会相交（否则该点的电荷不知道往哪走）；",
        "         线越密 = 场越强。偶极子中线处场最弱，两极附近最强。",
        "类比：电场线 ≈ 水流线；正电荷 = 泉眼，负电荷 = 排水口。",
    )
    W, H = 53, 21
    charges = [(-1.0, 0.0, +1.0), (1.0, 0.0, -1.0)]  # (x, y, q)
    xmin, xmax = -2.6, 2.6
    ymin, ymax = -1.3, 1.3
    arrows = "→↘↓↙←↖↑↗"
    grid = [[" "] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            px = xmin + (xmax - xmin) * c / (W - 1)
            py = ymax - (ymax - ymin) * r / (H - 1)
            ex = ey = 0.0
            for cx, cy, q in charges:
                dx, dy = px - cx, py - cy
                r2 = dx * dx + dy * dy + 0.01
                f = q / (r2 * math.sqrt(r2))
                ex += f * dx; ey += f * dy
            mag = math.hypot(ex, ey)
            if mag < 0.05:
                continue
            ang = math.atan2(ey, ex)
            idx = int((ang + math.pi) / (2 * math.pi) * 8) % 8
            grid[r][c] = arrows[idx]
    for cx, cy, q in charges:
        cc = int((cx - xmin) / (xmax - xmin) * (W - 1))
        rr = int((ymax - cy) / (ymax - ymin) * (H - 1))
        if 0 <= rr < H and 0 <= cc < W:
            grid[rr][cc] = "⊕" if q > 0 else "⊖"
    print("  ┌" + "─" * W + "┐")
    for row in grid:
        print("  │" + "".join(row) + "│")
    print("  └" + "─" * W + "┘")
    note(
        "看：左 ⊕ 正电荷发出场线，右 ⊖ 负电荷吸入场线，形成偶极子图案。",
        "     箭头方向 = 该点电场方向；箭头越密的地方场越强。",
    )


# ───────────────────────────── Demo 3 ─────────────────────────────

def demo_3_infinite_well():
    """无限深势阱：为什么能量是量子化的？"""
    banner("Demo 3 · 一维无限深势阱（有限差分法，展示驻波与量子化）")
    note(
        "白话：把粒子关在一个'两头是墙'的盒子里（墙无限高，粒子出不去）。",
        "像吉他弦两端固定——只有某些波长的'驻波'刚好能塞进去。",
        "",
        "反直觉：能量不是连续的，只能取 E₁、E₂、E₃…（Eₙ ∝ n²）。",
        "         更反直觉：最低能量态（基态）的动能也不为零——'零点能'！",
        "         因为粒子被关在盒子里不可能完全静止（否则违反对不确定性原理）。",
        "类比：吉他弦的泛音；风琴管里只能形成特定频率的驻波。",
    )
    N = 60              # 内部网格点数
    dx = 1.0 / (N + 1)  # 盒长 L=1
    # 离散拉普拉斯算子的解析本征向量：ψ_k(j)=sin(πkj/(N+1))
    # 本征值 λ_k = 2(1-cos(πk/(N+1)))/dx²；能量 E_k=ℏ²λ_k/(2m)，取 ℏ=m=1
    ns = [1, 2, 3]
    curves = []
    print("  ── 有限差分本征值 vs 解析值 (ℏ=m=L=1) ──")
    rows = []
    for k in ns:
        psi = [math.sin(math.pi * k * j / (N + 1)) for j in range(1, N + 1)]
        norm = math.sqrt(sum(p * p for p in psi) * dx)
        psi = [p / norm for p in psi]
        # 验证：离散拉普拉斯作用在 ψ 上 = λ·ψ
        lam = 0.0
        for j in range(N):
            left = psi[j - 1] if j > 0 else 0.0
            right = psi[j + 1] if j < N - 1 else 0.0
            lap = (left - 2 * psi[j] + right) / dx ** 2
            if abs(psi[j]) > 0.1:
                lam = -lap / psi[j]
        E_num = lam / 2.0
        E_ana = 0.5 * (math.pi * k) ** 2
        rows.append((f"n={k}", E_num, E_ana, abs(E_num - E_ana) / E_ana * 100))
        curves.append((f"n={k} (E={E_ana:.2f})", psi, str(k)))
    print(f"  {'态':>6} │ {'数值 E':>10} │ {'解析 (πn)²/2':>12} │ {'误差%':>7}")
    for lab, en, ea, err in rows:
        print(f"  {lab:>6} │ {en:10.4f} │ {ea:12.4f} │ {err:7.3f}%")
    plot_curves(curves, title="前三个驻波 ψₙ(x)：注意 n 越大节点越多、能量越高")
    note(
        "看：n=1 是半个正弦波（无内部节点），n=2 有 1 个节点，n=3 有 2 个节点。",
        "     E₃/E₁ = 9 —— 第三激发态能量是基态的 9 倍（因为 E ∝ n²）。",
        "     基态能量 E₁ = π²/2 ≈ 4.93 ≠ 0 —— 这就是零点能，粒子永不停下。",
    )


# ───────────────────────────── Demo 4 ─────────────────────────────

def demo_4_ising():
    """Ising 模型蒙特卡洛：温度如何摧毁磁铁？"""
    banner("Demo 4 · 一维 Ising 模型（Metropolis 蒙特卡洛）")
    note(
        "白话：一排小磁针，每个只能朝上(↑)或朝下(↓)。",
        "邻居同向则开心（能量低），反向则难受。温度越高，它们越爱随机翻转。",
        "",
        "反直觉：你以为降温就能让所有磁针对齐？一维 Ising 在任何有限温度下",
        "         都没有铁磁相变！因为翻转一对邻居只花 2J 的能量，熵永远赢。",
        "         （二维 Ising 才有相变，Tc ≈ 2.269 J/k —— Onsager 的杰作。）",
        "类比：一排队的人想统一朝向，但只要有人转头，邻居就跟着转——",
        "      一维链太脆弱，hold 不住长程序；二维网格才够'结实'。",
    )
    random.seed(42)
    L = 50
    n_samples = 8

    def metropolis(L, T, sweeps=400):
        s = [1] * L
        for _ in range(sweeps):
            for _ in range(L):
                i = random.randrange(L)
                nb = s[(i - 1) % L] + s[(i + 1) % L]
                dE = 2 * s[i] * nb
                if dE <= 0 or random.random() < math.exp(-dE / T):
                    s[i] = -s[i]
        m = sum(s) / L
        return s, abs(m)

    Ts = [0.5, 1.5, 5.0]
    for T in Ts:
        s, m = metropolis(L, T)
        row = "".join("▲" if x > 0 else "▼" for x in s)
        print(f"  T={T:>3.1f} │{row}│  |M|={m:.2f}")
    note("  看：T=0.5 时偶有大块同向区域；T=5.0 时完全混乱，磁化 |M|≈0。")

    # 磁化-温度曲线
    pts = []
    for k in range(12):
        T = 0.3 + k * 0.5
        _, m = metropolis(L, T, sweeps=250)
        pts.append(m)
    plot_curves([("|M| vs T", pts, "●")], title="一维 Ising：|M| 随 T 平滑下降（无相变！）")


# ───────────────────────────── Demo 5 ─────────────────────────────

def _fft(a):
    """递归 radix-2 Cooley-Tukey FFT（纯 Python + cmath）。"""
    n = len(a)
    if n <= 1:
        return a
    even = _fft(a[0::2])
    odd = _fft(a[1::2])
    half = n // 2
    T = [cmath.exp(-2j * cmath.pi * k / n) * odd[k] for k in range(half)]
    return [even[k] + T[k] for k in range(half)] + [even[k] - T[k] for k in range(half)]


def demo_5_fft():
    """纯 Python FFT：方波里藏着哪些频率？"""
    banner("Demo 5 · 快速傅里叶变换：把方波'拆'成纯正弦波")
    note(
        "白话：FFT 是一台'频率分离机'。你给它一段混合波形，",
        "它告诉你这里面分别藏着哪些频率、各占多少。",
        "",
        "反直觉：棱角分明的方波，拆开后竟然全是一堆光滑的正弦波！",
        "         而且只用'奇数次'谐波：sin(x)+sin(3x)/3+sin(5x)/5+…",
        "类比：FFT ≈ 三棱镜把白光分解成彩虹；≈ 把钢琴和弦拆成单个琴键。",
    )
    N = 64
    square = [1.0 if (i * 2) // N % 2 == 0 else -1.0 for i in range(N)]
    spec = _fft(square)
    mags = [(k, abs(spec[k]) * 2 / N) for k in range(N // 2)]
    top = sorted(mags, key=lambda t: -t[1])[:6]
    bars = [(f"f={k}", v) for k, v in top]
    plot_bars(bars, title="方波的频谱：只有奇次谐波幸存", unit="")
    note(
        "看：最强的分量在 k=1（基频），其次是 k=3、k=5、k=7…",
        "     偶次谐波（k=2,4,6…）的幅度几乎为零——这就是方波只含奇谐的原因。",
        "     公式：方波 = (4/π)[sin x + sin3x/3 + sin5x/5 + …]",
    )


# ───────────────────────────── Demo 6 ─────────────────────────────

def demo_6_radioactive():
    """放射性衰变蒙特卡洛：为什么是指数衰减？"""
    banner("Demo 6 · 放射性衰变（蒙特卡洛模拟）")
    note(
        "白话：一堆放射性原子，每个时刻都有一定概率'死掉'（衰变）。",
        "没人能预测哪一个会先死——但一大群原子整体上精确地按指数减少。",
        "",
        "反直觉（核心）：衰变是'无记忆'的！一个存在了 10000 年的原子，",
        "         和一个刚诞生的原子，在下一秒衰变的概率完全一样。",
        "         原子不会'变老'——这就是为什么半衰期是常数。",
        "类比：抛硬币——每次正面朝上的概率都是 50%，不管之前抛了多少次。",
    )
    random.seed(7)
    N0 = 10000
    p = 0.01  # 每步衰变概率
    steps = 500
    pop, times = [], []
    n = N0
    half_life = -1
    for t in range(steps):
        decayed = sum(1 for _ in range(n) if random.random() < p)
        n -= decayed
        pop.append(n / N0)
        times.append(t)
        if half_life < 0 and n <= N0 / 2:
            half_life = t
    theory = [math.exp(-p * t) for t in times]
    plot_curves(
        [("蒙特卡洛 N(t)/N₀", pop, "●"), ("理论 e^(-λt)", theory, "-")],
        title=f"衰变曲线  (N₀={N0}, λ={p}, 模拟半衰期≈{half_life} 步)",
    )
    th = math.log(2) / p
    note(
        f"看：模拟曲线和理论指数 e^(-λt) 几乎重合。",
        f"     模拟半衰期 ≈ {half_life} 步，理论 = ln2/λ = {th:.1f} 步。",
        "     因为衰变无记忆，才必然得到指数衰减——这是概率论的必然结果。",
    )


# ───────────────────────────── Demo 7 ─────────────────────────────

def demo_7_brownian():
    """布朗运动：为什么随机步行的'平均距离'可预测？"""
    banner("Demo 7 · 布朗运动 / 随机游走")
    note(
        "白话：花粉在水面被水分子随机撞击，走出一条乱七八糟的轨迹。",
        "每一步方向完全随机，但'平均走多远'却能精确预测。",
        "",
        "反直觉：虽然每一步方向随机，但 RMS 位移 ∝ √t（不是 ∝ t）！",
        "         也就是说距离增长越来越慢——走 10 步平均离原点 √10≈3.2 步，",
        "         走 100 步才 10 步。随机性有可预测的'包络'。",
        "类比：醉汉走路——无法预测他走到哪，但 N 步后 typically 在 √N 步远处。",
    )
    random.seed(123)
    n_walkers, n_steps = 200, 300
    msd_samples = []
    traj = [0.0]
    x = 0.0
    for s in range(n_steps):
        x += random.choice([-1, 1])
        traj.append(x)
    sq = [0.0] * (n_steps + 1)
    for _ in range(n_walkers):
        xx = 0.0
        for s in range(n_steps):
            xx += random.choice([-1, 1])
            sq[s + 1] += xx * xx
    msd = [q / n_walkers for q in sq]               # <x²>  ∝ t  （线性）
    rms = [math.sqrt(max(q, 0)) for q in msd]        # √<x²> ∝ √t （亚线性）
    sqrt_t = [math.sqrt(max(s, 1)) for s in range(n_steps + 1)]
    plot_curves(
        [("RMS 位移 √<x²>", rms, "●"), ("√(步数)", sqrt_t, "-")],
        title=f"RMS 位移 ∝ √t —— 距离增长比时间慢（{n_walkers} walkers 平均）",
    )
    note(
        f"看：<x²> 本身 ∝ 步数（线性增长，每步平均贡献 1），",
        f"     但【RMS 位移】= √<x²> ∝ √t —— 增长越来越慢。",
        f"     100 步只走到 ~10 步远，10000 步才 ~100 步远。这就是扩散慢的本质。",
        "     对比：匀速直线走 10000 步是 10000 步远——随机游走效率极低。",
    )


# ─────────────────────────── 调度入口 ───────────────────────────

DEMOS = [
    ("谐振子积分", demo_1_harmonic),
    ("电偶极子场", demo_2_electric_field),
    ("无限深势阱", demo_3_infinite_well),
    ("Ising 模型", demo_4_ising),
    ("FFT 频谱", demo_5_fft),
    ("放射性衰变", demo_6_radioactive),
    ("布朗运动", demo_7_brownian),
]


def main():
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    print("╔" + "═" * 70 + "╗")
    print("║" + "  UC Berkeley 物理演示 · 费曼式可视化（纯标准库，无依赖）".center(54) + "║")
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
