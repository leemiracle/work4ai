"""
MIT 物理演示 · 费曼式可视化（8.01/8.02/8.04/8.09 + OpenCourseWare）
================================
配套：本目录各 topic*/ 的 .md 教学文档（Kleppner 8.012 / Purcell 8.022 / Griffiths 8.04 体系）
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
    """二维散点图。points=[(x,y),...]；marks=[(x,y,char),...] 额外标记。"""
    allp = list(points) + [m[:2] for m in (marks or [])]
    xs = [p[0] for p in allp]; ys = [p[1] for p in allp]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    if xmax - xmin < 1e-9: xmax = xmin + 1
    if ymax - ymin < 1e-9: ymax = ymin + 1
    grid = [[" "] * width for _ in range(height)]
    if xmin < 0 < xmax:
        cz = int((0 - xmin) / (xmax - xmin) * (width - 1))
        for r in range(height): grid[r][cz] = "│"
    if ymin < 0 < ymax:
        rz = int((ymax - 0) / (ymax - ymin) * (height - 1))
        for c in range(width): grid[rz][c] = "─"
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

def demo_1_gyroscope():
    """陀螺进动：为什么旋转的陀螺不会倒下？"""
    banner("Demo 1 · 陀螺进动：力向下，运动却横向（Kleppner 8.012 风格）")
    note(
        "白话：一个静止的陀螺一松手就倒了。但如果它在高速自转，它不但不倒，",
        "还会让转轴慢慢绕圈走——这叫'进动'。转得越快，进动越慢。",
        "",
        "反直觉：重力明明向下拉，陀螺却往【侧面】跑！因为力矩 τ=r×mg 垂直于角动量 L，",
        "         所以 dL/dt 也垂直于 L——L 的大小不变，只是方向旋转（像圆周运动）。",
        "         力和效果差 90°，这和磁场让电荷做圆周运动是同一个数学结构。",
        "类比：推一个静止的轮子，它往前走；但推一个高速旋转的轮子的轴，它却拐弯。",
    )
    # 数值模拟：L 在 xy 平面进动，力矩 τ = r×mg 沿水平切向
    L = 1.0              # 自旋角动量大小
    m, g, r = 1.0, 9.81, 0.1
    tau = m * g * r      # 重力力矩大小
    Omega = tau / L      # 进动角速度 Ω = τ/L
    theta = 0.0
    dt = 0.02
    traj = []
    for i in range(180):
        # L 方向以 Ω 进动（绕竖直 z 轴）
        theta += Omega * dt
        lx = L * math.cos(theta)
        ly = L * math.sin(theta)
        traj.append((lx, ly))
    plot_xy(traj, title="角动量 L 的水平分量轨迹：匀速画圆 = 稳态进动",
            marks=[(L, 0, "起")])
    print(f"\n  自旋角动量 L = {L}    力矩 τ = mgr = {tau}")
    print(f"  进动角速度 Ω = τ/L = {Omega:.3f} rad/s    进动周期 = {2*math.pi/Omega:.2f} s")
    note(
        "看：角动量矢量的水平分量匀速画圆——这就是进动。",
        f"     进动周期 {2*math.pi/Omega:.2f}s，远慢于自旋——所以陀螺'慢悠悠'地转圈。",
        "     关键：L 的大小始终不变（|L|=const），只有方向在变——因为力矩⊥L。",
        "     如果陀螺不自旋（L=0），Ω→∞ 意味着它直接倒下——没有进动来'托住'它。",
    )


# ───────────────────────────── Demo 2 ─────────────────────────────

def demo_2_relativistic_em():
    """相对论电磁学：磁场是电场的相对论效应（Purcell 8.022）"""
    banner("Demo 2 · 磁力 = 电力的相对论面具（Purcell 风格）")
    note(
        "白话：一根通电导线，旁边有个运动的电荷，电荷会被'磁力'吸引/排斥。",
        "但如果你跟着电荷一起跑（换到电荷的参考系），电荷不动了，磁力消失了！",
        "取而代之的是一种'电力'——因为长度收缩让导线带上了净电荷。",
        "",
        "反直觉：磁力根本不是新的力！它就是电力，只是从运动参考系看出来的样子。",
        "         磁场 = 电场 + 狭义相对论。整个电磁学可以只用电场+相对论推导出来。",
        "类比：风不是新东西——风就是'静止的空气'，只是你坐着车跑时感受到的。",
    )
    c = 3.0e8
    v0 = 1.0e6     # 电子漂移速度（很慢！）
    lam = 1.0      # 线电荷密度基准（实验室系中性：λ+ = λ, λ- = -λ）
    u = 0.5 * c    # 试探电荷速度
    eps0 = 8.85e-12
    mu0 = 1.0 / (eps0 * c * c)
    r_dist = 0.01  # 距导线 1 cm
    # 实验室系：磁力 F = q u B, B = μ0 I/(2πr), I = λ v0
    I = lam * v0
    B = mu0 * I / (2 * math.pi * r_dist)
    F_mag = 1.0 * u * B
    # 电荷静止系 S'：净电荷密度 ρ' = γ_u · (ρ - u j/c²) = -γ_u u λ-/c² (因为 ρ=0, j=λ-v0)
    # 取 λ- = -λ，j = λ-v0 = -λ v0
    j = -lam * v0
    gamma_u = 1.0 / math.sqrt(1 - (u / c) ** 2)
    rho_prime = gamma_u * (0.0 - u * j / c ** 2)   # = γ_u u λ v0 / c²
    E_prime = rho_prime / (2 * math.pi * eps0 * r_dist)
    F_elec = 1.0 * E_prime
    print("  ── 两种视角看同一件事：运动电荷受力 ──")
    print(f"  导线：正离子静止 λ+={lam}, 电子漂移 v0={v0:.1e} m/s, 中性(λ+ + λ-=0)")
    print(f"  试探电荷速度 u = {u:.2e} m/s = {u/c:.1f}c, 距导线 r = {r_dist*100} cm\n")
    print(f"  【实验室系】电力=0(中性线), 只有磁力:")
    print(f"     B = μ₀I/2πr = {B:.3e} T")
    print(f"     F_磁 = quB  = {F_mag:.3e} N\n")
    print(f"  【电荷静止系 S'】磁力=0(电荷不动), 只有电力:")
    print(f"     γ_u = {gamma_u:.4f}")
    print(f"     长度收缩 → 净电荷密度 ρ' = γ_u·u·λ·v₀/c² = {rho_prime:.3e} C/m")
    print(f"     E' = ρ'/2πε₀r = {E_prime:.3e} V/m")
    print(f"     F_电 = qE'   = {F_elec:.3e} N\n")
    print(f"  验证：F_电/F_磁 = {F_elec/F_mag:.4f}  (理论应 = γ_u = {gamma_u:.4f} ✓)")
    note(
        "看：同一个力，实验室系叫'磁力'，电荷系叫'电力'——大小差 γ_u 倍（力的变换）。",
        "     源头都是洛伦兹收缩：运动让电荷密度改变。磁不是独立的东西，是电的相对论面具。",
        "     深意：只要存在磁场，就暗示参考系在运动——磁场是相对论的最直接证据。",
    )


# ───────────────────────── Crank-Nicolson 工具 ─────────────────────────

def _thomas(a, b, c, d):
    """复数三对角方程组求解（Thomas 算法）。a=下,b=主,c=上,d=右端。"""
    n = len(b)
    cp = [0j] * n; dp = [0j] * n
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = [0j] * n
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


# ───────────────────────────── Demo 3 ─────────────────────────────

def demo_3_wave_packet():
    """薛定谔方程波包演化：粒子为什么会'散开'？"""
    banner("Demo 3 · 高斯波包的量子演化（Crank-Nicolson，8.04 风格）")
    note(
        "白话：把一个粒子'捏'在一个小区域里（位置确定），然后放开。",
        "随时间推移，它会越变越宽——这就是'波包扩散'。位置越准，扩散越快。",
        "",
        "反直觉：粒子没人碰，自己就'胖'了！因为位置越确定 → 动量越不确定（海森堡），",
        "         动量分散 → 各分量走不同速度 → 波包铺开。不确定性原理的实时表演。",
        "类比：把一束光聚焦得越小，它散开得越快（衍射）。挤压气球的一头，另一头鼓起。",
    )
    N = 200
    dx = 0.1
    dt = 0.01
    x = [i * dx for i in range(N)]
    x0, sigma, k0 = 6.0, 1.0, 1.0
    psi = [cmath.exp(-(xi - x0) ** 2 / (2 * sigma ** 2)) * cmath.exp(1j * k0 * xi) for xi in x]
    norm0 = math.sqrt(sum(abs(p) ** 2 for p in psi) * dx)
    psi = [p / norm0 for p in psi]
    coeff = 1j * dt / (2 * dx * dx)   # ℏ=m=1: i∂ψ/∂t = -(1/2)∂²ψ/∂x²
    n_int = N - 2
    lower = [-coeff / 2] * n_int      # LHS (I + iΔt/2 H) 的下/上对角
    upper = [-coeff / 2] * n_int
    diag = [1 + coeff] * n_int
    diag_m = [1 - coeff] * n_int      # RHS (I - iΔt/2 H) 的主对角
    snapshots = {}
    snapshots[0] = [abs(p) ** 2 for p in psi]
    for step in range(1, 801):
        # RHS: (1-coeff)ψ_i + (coeff/2)(ψ_{i-1}+ψ_{i+1})  ← 注意是 +coeff/2（保幺正性！）
        rhs = [diag_m[i] * psi[i + 1] + (coeff / 2) * (psi[i] + psi[i + 2])
               for i in range(n_int)]
        new_int = _thomas(lower[:], diag[:], upper[:], rhs)
        for i in range(n_int):
            psi[i + 1] = new_int[i]
        psi[0] = psi[-1] = 0j
        if step in (300, 800):
            snapshots[step] = [abs(p) ** 2 for p in psi]
    norm_final = sum(abs(p) ** 2 for p in psi) * dx
    curves = [(f"t={s}", snapshots[s], ch)
              for (s, ch) in zip(sorted(snapshots), "●★◆")]
    plot_curves(curves, height=10, title=f"|ψ|² 演化：波包移动 + 变宽（末态范数={norm_final:.4f}）")
    note(
        f"看：t=0 波包窄而高（位置确定）；t=800 波包宽而矮——它'散'开了。",
        f"     Crank-Nicolson 是【幺正】算法：范数始终守恒（末态={norm_final:.4f}≈1），",
        "     不会像 Euler 那样'泄能'。这是模拟量子系统必须用的方法。",
        "     初始 σ=1（很窄）→ 动量不确定大 → 扩散快。把 σ 加大，扩散立刻变慢。",
    )


# ───────────────────────────── Demo 4 ─────────────────────────────

def demo_4_partition():
    """配分函数：一个公式算出所有热力学量（8.044）"""
    banner("Demo 4 · 配分函数 Z → 热力学量（两能级系统 / Schottky 反常）")
    note(
        "白话：一个小磁针在磁场里有两个状态：顺着场（能量低）和逆着场（能量高）。",
        "给它一个温度 T，配分函数 Z = e^(-E₁/kT) + e^(-E₂/kT) 把所有状态'称重'加起来。",
        "从 Z 这个神奇的函数，能算出能量、熵、热容——全部热力学量一网打尽。",
        "",
        "反直觉：热容在 kT≈ΔE 处出现【尖峰】（Schottky 异常）！",
        "         低温时粒子冻在基态（吸不动热），高温时两态等概率（也吸不动），",
        "         只有 kT≈能隙时，少量升温就能翻转大量粒子 → 热容峰值。",
        "类比：共振吸收——推秋千只有频率匹配才有效；热容峰值就是'温度匹配能隙'。",
    )
    k = 1.0
    Delta = 1.0    # 能隙
    Ts = [0.1 + 0.1 * i for i in range(80)]
    Us, Ss, Cs = [], [], []
    U_prev = None
    dT = Ts[1] - Ts[0]
    for T in Ts:
        b = Delta / (k * T)
        Z = 1.0 + math.exp(-b)        # E0=0, E1=Δ
        U = Delta * math.exp(-b) / Z  # 平均能量
        F = -k * T * math.log(Z)
        S = (U - F) / T
        Us.append(U); Ss.append(S)
        if U_prev is not None:
            Cs.append((U - U_prev) / dT / k)
        U_prev = U
    Cs.append(Cs[-1] if Cs else 0)
    plot_curves([("内能 U", [u / Delta for u in Us], "●"),
                 ("熵 S/k", Ss, "★"),
                 ("热容 C/k", [c / max(Cs) for c in Cs], "◆")],
                title="两能级系统：U, S, C 随 kT/Δ 变化（C 在 kT≈0.4Δ 处达峰）")
    T_peak = Ts[Cs.index(max(Cs))]
    print(f"\n  热容峰值出现在 kT/Δ ≈ {T_peak/Delta:.2f}  （Schottky 异常）")
    print(f"  低温极限：U→0（冻在基态），C→0；高温极限：U→Δ/2（等概率），C→0")
    note(
        "看：热容(◆)在 kT/Δ≈0.4 处冲到峰值，两头都归零——这就是 Schottky 异常。",
        "     配分函数 Z 是统计力学的'万能钥匙'：ln Z 求导就得到 U、F、S、C 等一切。",
        "     这套方法适用于任何系统——分子、磁体、光子气体——只要能数清能级。",
    )


# ───────────────────────────── Demo 5 ─────────────────────────────

def demo_5_spherical_harmonics():
    """球谐函数 / 勒让德多项式：原子轨道的角向形状"""
    banner("Demo 5 · 勒让德多项式 & 球谐函数（原子轨道的角向形状）")
    note(
        "白话：电子在原子里的'轨道'，其角度部分由球谐函数 Y_l^m 描述。",
        "l=0 是球对称（s 轨道），l=1 是哑铃形（p 轨道），l=2 是四叶草（d 轨道）。",
        "",
        "反直觉：这些形状不是随便画的——它们是球面上拉普拉斯算符的本征函数！",
        "         '节点数 = l'和驻波、吉他弦是同一个数学：边界条件 → 量子化 → 分立形状。",
        "         化学键的方向性（sp³ 四面体等）根源就在这些角向驻波的对称性。",
        "类比：鼓面的振动模式——圆形鼓只能敲出特定频率的同心环/花瓣图案。",
    )
    N = 90
    thetas = [math.pi * i / N for i in range(N + 1)]
    cos_t = [math.cos(th) for th in thetas]

    def legendre(l, xs):
        if l == 0: return [1.0] * len(xs)
        if l == 1: return list(xs)
        ps = [1.0] * len(xs); p1 = list(xs)
        for ll in range(1, l):
            p2 = [((2 * ll + 1) * xs[i] * p1[i] - ll * ps[i]) / (ll + 1) for i in range(len(xs))]
            ps, p1 = p1, p2
        return p1
    curves = []
    for l, ch in [(0, "s"), (1, "p"), (2, "d"), (3, "f")]:
        pl = legendre(l, cos_t)
        curves.append((f"l={l} ({ch}轨道)", pl, ch))
    plot_curves(curves, title="P_l(cosθ) vs θ：l 越大节点越多（节点数=l）")
    note(
        "看：l=0(s) 无节点全正；l=1(p) 一个节点（正负叶）；l=2(d) 两节点（四叶草）；l=3(f) 三节点。",
        "     |Y_l^m|² 就是原子轨道电子云的角向形状——化学家画的 s/p/d/f 就是从这来的。",
        "     节点数越多 = 角动量越大 = 能量越高（氢原子能级也依赖 l）。",
    )


# ───────────────────────────── Demo 6 ─────────────────────────────

def demo_6_fourier_series():
    """傅里叶级数：方波逼近与 Gibbs 现象"""
    banner("Demo 6 · 傅里叶级数逼近方波（Gibbs 现象永不消失）")
    note(
        "白话：任何周期函数都能拆成一堆正弦波的叠加——这就是傅里叶级数。",
        "用的项越多，逼近越准。但是！在'尖角'处，永远有个 9% 的过冲消不掉。",
        "",
        "反直觉：无论加多少项，方波跳变处的过冲始终 ≈ 9%（Gibbs 现象）！",
        "         无穷多个光滑正弦波叠加，竟无法完美制造一个真正的尖角。",
        "         这是数学的深刻限制：连续函数级数收敛不代表能复原间断点。",
        "类比：用无数根面条拼一个直角——总有一个小圆弧，永远拼不出完美的直角。",
    )
    N = 120
    xs = [2 * math.pi * i / N for i in range(N)]
    square = [1.0 if (x % (2 * math.pi)) < math.pi else -1.0 for x in xs]

    def partial_sum(n_terms, x):
        s = 0.0
        for k in range(1, n_terms + 1):
            m = 2 * k - 1  # 只用奇次谐波
            s += math.sin(m * x) / m
        return 4 * s / math.pi
    plot_curves(
        [("方波", square, "█"),
         ("1 项", [partial_sum(1, x) for x in xs], "1"),
         ("5 项", [partial_sum(5, x) for x in xs], "5"),
         ("20项", [partial_sum(20, x) for x in xs], "2")],
        title="方波的傅里叶逼近：项数越多越准，但跳变处过冲不消失")
    # 在间断点(x=0)附近精细采样，捕捉 Gibbs 过冲（过冲峰很窄，粗网格会漏掉！）
    fine_xs = [0.0005 * (i + 1) for i in range(200)]
    peak_val = max(partial_sum(50, x) for x in fine_xs)
    over_abs = peak_val - 1.0
    over_frac = over_abs / 2.0   # 占跳变幅度(=2.0)的比例
    print(f"\n  50 项逼近在 x≈0⁺ 处的峰值 = {peak_val:.3f}, 过冲 = {over_abs:.3f}")
    print(f"  过冲占跳变量的 {over_frac*100:.1f}%  （理论 Gibbs 常数 ≈ 8.9%，与项数无关）")
    note(
        "看：1 项≈一个正弦波；5 项已像方波但有波纹；20 项波纹变密但过冲依旧。",
        "     过冲 ≈ 跳变量的 9%，无论加多少项都不消失——这就是 Gibbs 现象。",
        "     它告诉我们：无穷多个光滑正弦波的叠加，也无法完美复现一个真正的尖角。",
    )


# ───────────────────────────── Demo 7 ─────────────────────────────

def demo_7_normal_modes():
    """耦合振子的简正模：复杂运动 = 纯音的叠加（8.03）"""
    banner("Demo 7 · 耦合振子 & 简正模（能量在两个摆之间来回流动）")
    note(
        "白话：两个摆用一根弹簧连起来。你推一下左摆，能量会'流'到右摆，再流回来——",
        "如此反复，形成'拍'。但这看似复杂的运动，其实是两个最简单的'纯振动'叠加。",
        "",
        "反直觉：不管初始条件多乱，系统的运动总能分解成两个'简正模'：",
        "         ① 同相模（两摆同步，弹簧不伸缩，频率 ω₁=√(g/L)）；",
        "         ② 反相模（两摆反向，弹簧用力拉，频率 ω₂=√(g/L+2k/m) > ω₁）。",
        "         这两个频率的差产生'拍'——能量在两摆间周期性转移。",
        "类比：两个频率略不同的音叉同时响→听到'哇哇'的拍频。简正模就是'纯音'。",
    )
    dt = 0.02
    steps = 1500
    g, L, k, m = 9.81, 1.0, 0.5, 1.0
    omega1 = math.sqrt(g / L)
    omega2 = math.sqrt(g / L + 2 * k / m)
    # 初始：只推左摆
    th1, th2 = 0.3, 0.0
    w1 = w2 = 0.0
    th1_traj, th2_traj = [], []
    for i in range(steps):
        a1 = -(g / L) * th1 - (k / m) * (th1 - th2)
        a2 = -(g / L) * th2 - (k / m) * (th2 - th1)
        w1 += a1 * dt; w2 += a2 * dt
        th1 += w1 * dt; th2 += w2 * dt
        if i % 3 == 0:
            th1_traj.append(th1); th2_traj.append(th2)
    t_axis = [i * dt * 3 for i in range(len(th1_traj))]
    plot_curves([("摆 1（被推的）", th1_traj, "1"), ("摆 2（被动）", th2_traj, "2")],
                title="两摆角度随时间：能量从摆1→摆2→摆1 周期性转移（拍）")
    T_beat = 2 * math.pi / abs(omega2 - omega1)
    print(f"\n  ω₁(同相) = {omega1:.3f}    ω₂(反相) = {omega2:.3f}")
    print(f"  拍频周期 T_beat = 2π/|ω₂-ω₁| = {T_beat:.2f} s")
    print(f"  （即约每 {T_beat:.1f}s 能量从摆1完全转移到摆2再回来）")
    note(
        "看：摆1的振幅周期性变大变小，摆2相反——能量像水一样在两个摆间流动。",
        "     这就是'拍'。任何耦合系统都能分解成简正模——找到它们就等于解出了全部运动。",
        "     拓展：分子的振动谱、晶格的声子、耦合电路——全都是简正模的语言。",
    )


# ─────────────────────────── 调度入口 ───────────────────────────

DEMOS = [
    ("陀螺进动", demo_1_gyroscope),
    ("相对论电磁", demo_2_relativistic_em),
    ("波包演化", demo_3_wave_packet),
    ("配分函数", demo_4_partition),
    ("球谐函数", demo_5_spherical_harmonics),
    ("傅里叶级数", demo_6_fourier_series),
    ("简正模/拍", demo_7_normal_modes),
]


def main():
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    print("╔" + "═" * 70 + "╗")
    print("║" + "  MIT 物理演示 · 费曼式可视化（纯标准库，无依赖）".center(54) + "║")
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
