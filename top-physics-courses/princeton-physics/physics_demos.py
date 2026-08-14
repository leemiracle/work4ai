"""
Princeton 物理演示 · 费曼式可视化
=================================
配套：本目录各 topic*/ 的 .md 教学文档
风格：每个 demo = 白话 + 可视化 + 反直觉 + 类比，纯标准库

课程对应：
  PHY 207  分析力学 (Taylor)
  PHY 208  电磁学 (Griffiths)
  PHY 305  量子力学 (Griffiths)
  PHY 411  经典力学 (Goldstein)
  PHY 503  量子力学 II (Sakurai)
  PHY 505  统计力学 (Pathria)
  PHY 563  广义相对论 (Carroll)
  PPPL     等离子体物理 (磁约束聚变)
  IAS      弦理论/AdS-CFT

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
# Demo 1 · 哈密顿方程——相空间中的流体  (PHY 411)
# ============================================================

def demo_hamilton():
    """
    白话：牛顿说 F=ma，哈密顿说：把位置 x 和动量 p 当成平等的伙伴，
    它们组成的'相空间'里，系统像水流一样沿等高线走——永远不耗散！
    反直觉：哈密顿力学看起来只是换了变量，但它揭示了一个深刻的事实：
    经典力学本质上就是相空间里的几何学——这直接通向量子力学和统计力学。
    类比：看地图你只看'在哪里'（x），哈密顿让你同时看'在哪里'和'往哪冲'（p），
    合在一起就是一张'命运之河'的俯瞰图。
    """
    print("\n" + "=" * 64)
    print("  Demo 1 · 哈密顿方程与相空间 (Goldstein Ch.8)")
    print("=" * 64)

    print("\n  简谐振子 H = p²/(2m) + ½kx²")
    print("  哈密顿方程： ẋ = ∂H/∂p = p/m")
    print("              ṗ = −∂H/∂x = −kx")
    print()

    # 数值积分绘制相空间轨迹
    m = 1.0; k = 1.0; dt = 0.01; t_end = 2 * math.pi * 3
    phase_pts = []
    for E in [0.5, 1.0, 2.0, 3.5]:
        x0 = math.sqrt(2 * E / k)
        x, p = x0, 0.0
        traj = []
        t = 0.0
        while t <= t_end:
            traj.append((x, p))
            # 半隐式 Euler（辛积分器，保持能量守恒）
            p += (-k * x) * dt
            x += (p / m) * dt
            t += dt
        phase_pts.extend(traj)
        print(f"  E={E:.1f}: 初始 x₀={x0:.2f}, p₀=0.00  "
              f"→ 相空间椭圆（能量守恒）")

    ascii_scatter(phase_pts, title="相空间轨迹 (x vs p)",
                  xlab="x (位置)", ylab="p (动量)")

    print("\n  ※ 反直觉：相空间轨迹是闭合的——意味着运动必然周期性重复。")
    print("  ※ 哈密顿力学的威力：直接推广到量子力学（算符替换）和统计力学。")
    print("  ※ 生活类比：钟摆的相空间图像一个椭圆跑道——能量越大圈越大。")

# ============================================================
# Demo 2 · 正则变换——换个角度看同一个世界  (PHY 411)
# ============================================================

def demo_canonical_transform():
    """
    白话：同一件事换个角度看可能简单很多。哈密顿力学允许你做'正则变换'——
    换一组坐标，只要保持相空间体积不变（刘维尔定理），物理就完全等价。
    反直觉：简谐振子在 (x, p) 坐标里是个椭圆（振荡），但换到'作用量-角度'
    (J, θ) 坐标里——它变成了匀速运动！问题瞬间变简单。
    类比：地球绕太阳，在地面坐标系里画出来很复杂的螺旋线，
    但在'日心坐标系'里就是一个干净的椭圆。
    """
    print("\n" + "=" * 64)
    print("  Demo 2 · 正则变换：作用量-角度变量 (J, θ)")
    print("=" * 64)

    m = 1.0; k = 1.0; omega = math.sqrt(k / m)
    print(f"\n  ω = √(k/m) = {omega:.3f}")
    print("  变换：J = E/ω,  θ = ωt")
    print("  新哈密顿量：K = Jω  (线性！)")
    print()

    # 在 (x,p) 空间：椭圆轨迹
    E = 2.0
    pts_xp = []
    t = 0.0; dt = 0.02
    while t <= 2 * math.pi:
        x = math.sqrt(2*E/k) * math.cos(omega * t)
        p = -math.sqrt(2*m*E) * math.sin(omega * t)
        pts_xp.append((x, p))
        t += dt
    ascii_scatter(pts_xp, title="(x, p) 空间：椭圆 = 振荡",
                  xlab="x", ylab="p")

    # 在 (J, θ) 空间：水平直线！
    J = E / omega
    pts_jt = [(t / (2*math.pi) * 2 * math.pi, J) for t_val in range(0, 64)]
    theta_vals = [i * 0.1 for i in range(64)]
    pts_jt2 = [(th, J) for th in theta_vals]
    ascii_scatter(pts_jt2, title="(J, θ) 空间：直线 = 匀速转动",
                  xlab="θ", ylab="J")

    print(f"  J = E/ω = {J:.4f} (常数)")
    print(f"  θ̇ = ∂K/∂J = ω = {omega:.3f}")
    print("  → 动力学方程平凡化：J 不变，θ 线性增长。")
    print("\n  ※ 反直觉：一个看起来复杂的振荡问题，换坐标系后变成了"
          "'什么都不发生'——这正是理论物理的美学！")
    print("  ※ Princeton IAS 传统：Wigner、Witten 用对称性把复杂问题化简。")

# ============================================================
# Demo 3 · 多极展开——远处看电荷分布  (PHY 208)
# ============================================================

def demo_multipole():
    """
    白话：从很远看一群电荷，细节都看不清了——你只能分辨出它的'总电荷'
    （单极）、'电荷偏向哪边'（偶极）、'形状像棒还是像饼'（四极）……
    这就是多极展开。离得越远，高阶项越不重要。
    反直觉：一个复杂的电荷分布，在远处的行为竟然可以只用几个数字
    （总电荷、偶极矩……）就完全描述！这就是物理学中的'有效理论'思想。
    类比：远处看一栋楼，你先看到'有栋楼'（单极），走近看到'门朝东'
    （偶极），再近看到'是方形的'（四极）……
    """
    print("\n" + "=" * 64)
    print("  Demo 3 · 多极展开：远场的'越来越简单'")
    print("=" * 64)

    print("\n  V(r) = Q/(4πε₀r) [1 + p·r̂/r + Q_ij r̂_i r̂_j / r² + ...]")
    print("         单极    偶极      四极\n")

    r = 1.0
    print(f"  {'距离 r':>10s}  {'单极 (1/r)':>12s}  "
          f"{'偶极 (1/r²)':>14s}  {'四极 (1/r³)':>14s}")
    print(f"  {'─'*10}  {'─'*12}  {'─'*14}  {'─'*14}")
    pts_mono = []; pts_dip = []; pts_quad = []
    for i in range(1, 21):
        r = i * 0.5
        mono = 1.0 / r
        dip = 1.0 / r**2
        quad = 1.0 / r**3
        pts_mono.append((r, mono))
        pts_dip.append((r, dip))
        pts_quad.append((r, quad))
        if i in [1, 2, 4, 8, 16, 20]:
            print(f"  {r:>10.1f}  {mono:>12.4f}  "
                  f"{dip:>14.6f}  {quad:>14.8f}")

    ascii_scatter(pts_mono + pts_dip + pts_quad,
                  title="多极项衰减速率 1/rⁿ",
                  xlab="r", ylab="势")

    print("\n  ※ 反直觉：r=10 时，偶极比单极弱 10 倍，四极弱 100 倍——"
          "远处几乎只看到总电荷！")
    print("  ※ 如果总电荷为零（如水分子），偶极项就是主要贡献。")
    print("  ※ 生活类比：远处看烟花——先看到一个亮点（单极），"
          "再看出往哪个方向散开（偶极）。")

# ============================================================
# Demo 4 · 角动量耦合与 Clebsch-Gordan  (PHY 503)
# ============================================================

def demo_clebsch_gordan():
    """
    白话：两个小磁针（自旋 ½）合在一起，可以组成'三重态'（都对齐）
    或'单态'（反平行抵消）。这个'怎么组合'的规则就是 Clebsch-Gordan 系数。
    反直觉：两个自旋 ½ 组合出总自旋 1 和 0——但单态 |0,0⟩ 的能量
    和三重态完全不同！氢原子的超精细分裂（21cm 线）就是这么来的。
    类比：两个齿轮可以同向转（三重态，省力）或反向转（单态，抵消）。
    """
    print("\n" + "=" * 64)
    print("  Demo 4 · 角动量耦合：两个自旋½ → 1 ⊕ 0")
    print("=" * 64)

    sqrt2 = math.sqrt(2)
    print("\n  两个自旋 ½ 的基底：|↑↑⟩, |↑↓⟩, |↓↑⟩, |↓↓⟩")
    print()
    print("  三重态 (j=1):")
    print("    |1, 1⟩  = |↑↑⟩                    (自旋平行向上)")
    print("    |1, 0⟩  = (|↑↓⟩ + |↓↑⟩) / √2      (对称叠加)")
    print("    |1,−1⟩  = |↓↓⟩                    (自旋平行向下)")
    print()
    print("  单态 (j=0):")
    print("    |0, 0⟩  = (|↑↓⟩ − |↓↑⟩) / √2      (反对称叠加)")
    print()
    print("  Clebsch-Gordan 系数表 ⟨j₁m₁ j₂m₂ | JM⟩：")
    print("  ┌──────────┬─────────┬──────────┬─────────┬──────────┐")
    print("  │          │ |1,1⟩   │ |1,0⟩    │ |1,−1⟩  │ |0,0⟩    │")
    print("  ├──────────┼─────────┼──────────┼─────────┼──────────┤")
    print("  │ |↑↑⟩     │   1     │    0     │    0    │    0     │")
    print("  │ |↑↓⟩     │   0     │  1/√2    │    0    │  1/√2    │")
    print("  │ |↓↑⟩     │   0     │  1/√2    │    0    │ −1/√2    │")
    print("  │ |↓↓⟩     │   0     │    0     │    1    │    0     │")
    print("  └──────────┴─────────┴──────────┴─────────┴──────────┘")

    # 角动量加法图示
    print("\n  角动量加法图示：")
    print("    |↑↑⟩:  ↑ + ↑ = ↑↑   总 S_z = +1   (j=1)")
    print("    |↓↓⟩:  ↓ + ↓ = ↓↓   总 S_z = −1   (j=1)")
    print("    |↑↓⟩ + |↓↑⟩:        总 S_z =  0   (j=1, 三重态)")
    print("    |↑↓⟩ − |↓↑⟩:        总 S_z =  0   (j=0, 单态)")

    # 氢原子超精细结构
    print("\n  应用：氢原子 21cm 线")
    E_hf = 5.9e-6  # eV
    f_21 = 1420.4  # MHz
    lam = 21.1     # cm
    print(f"    单态↔三重态能量差 ΔE = {E_hf*1e6:.1f} μeV")
    print(f"    跃迁频率 f = {f_21:.1f} MHz")
    print(f"    波长 λ = {lam} cm")
    print(f"    → 射电天文学用来测绘银河系氢气分布！")

    print("\n  ※ 反直觉：单态和三重态只差交换两个粒子的符号——")
    print("    但这个符号差别导致了宇宙中最重要的谱线之一！")
    print("  ※ Princeton 的 Wigner 用群论系统地处理了这些问题。")

# ============================================================
# Demo 5 · 玻尔兹曼分布与 Maxwell 速率分布  (PHY 505)
# ============================================================

def demo_boltzmann():
    """
    白话：气体里的分子有的快有的慢，但绝大多数在'平均速度'附近。
    玻尔兹曼发现了一个铁律：速度为 v 的概率正比于 exp(−mv²/2kT)——
    温度越高，分布越'胖'（分子跑得更快）。
    反直觉：即使在绝对零度附近，分子也不会完全停下（量子效应）。
    而且最概然速率 ≠ 平均速率 ≠ 方均根速率——它们是三个不同的数！
    类比：考试分数分布——大部分人集中在平均分附近，极端高分低分都少。
    """
    print("\n" + "=" * 64)
    print("  Demo 5 · 玻尔兹曼分布 P(v) ∝ v² exp(−mv²/2kT)")
    print("=" * 64)

    kT = 1.0; m = 1.0

    for T_label, T in [("低温 T=0.5", 0.5), ("室温 T=1.0", 1.0),
                        ("高温 T=2.0", 2.0)]:
        speeds = []
        for _ in range(5000):
            # 拒绝采样
            while True:
                v = random.expovariate(1.0 / math.sqrt(2 * kT * T / m)) * 0.5
                v += random.uniform(0, 3 * math.sqrt(T))
                weight = v * v * math.exp(-m * v * v / (2 * T))
                if v > 0 and random.random() < weight / (v * v):
                    speeds.append(v)
                    break
                if v > 0 and random.random() < weight / (2 * T):
                    speeds.append(v)
                    break
        if speeds:
            vp = math.sqrt(2 * T / m)
            vrms = math.sqrt(3 * T / m)
            vavg = math.sqrt(8 * T / (math.pi * m))
            print(f"\n  {T_label}:  最概然速率 v_p = {vp:.3f}")
            print(f"            平均速率   v̄  = {vavg:.3f}")
            print(f"            方均根    v_rms = {vrms:.3f}")
            ascii_hist(speeds, bins=20, title=f"速率分布 ({T_label})")

    print("\n  ※ 反直觉：v_p < v̄ < v_rms——三个'典型速率'不一样！")
    print("  ※ 温度翻倍 → 最概然速率只增加 √2 ≈ 1.41 倍（不是 2 倍）。")
    print("  ※ 生活类比：人群身高分布——大部分人'差不多高'，"
          "极端高矮的人很少。")

# ============================================================
# Demo 6 · 史瓦西度规与引力红移  (PHY 563)
# ============================================================

def demo_schwarzschild_redshift():
    """
    白话：光从黑洞附近逃出来时会被'拉伸'——波长变长，颜色变红。
    离黑洞越近，红移越厉害。在事件视界处，光被无限红移——
    外面的观察者永远看不到光逃出来。
    反直觉：这不是多普勒效应！是时空本身被引力弯曲了——
    靠近黑洞的时间走得比远处慢。这不是光线'累'了，是时间变慢了。
    类比：从深井底部喊话——声音听起来低沉（类比红移），
    但实际上是因为声音传播介质被'压缩'了。
    """
    print("\n" + "=" * 64)
    print("  Demo 6 · 史瓦西度规：引力红移")
    print("=" * 64)

    print("\n  光从半径 r 处发出，在无穷远观测到的频率：")
    print("    f_obs / f_emit = √(1 − r_s/r)")
    print("    红移 z = 1/√(1 − r_s/r) − 1")
    print("    其中 r_s = 2GM/c² (史瓦西半径)\n")

    pts = []
    print(f"  {'r / r_s':>10s}  {'f_obs/f_emit':>14s}  "
          f"{'红移 z':>10s}  {'时间膨胀':>10s}")
    print(f"  {'─'*10}  {'─'*14}  {'─'*10}  {'─'*10}")
    for rs_ratio in [1.01, 1.05, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0,
                     10.0, 50.0, 100.0]:
        factor = math.sqrt(1 - 1.0 / rs_ratio)
        z = 1 / factor - 1
        pts.append((math.log10(rs_ratio), factor))
        print(f"  {rs_ratio:>10.2f}  {factor:>14.6f}  "
              f"{z:>10.4f}  {1/factor:>10.4f}")

    ascii_scatter(pts, title="频率比 vs 距离 (对数)",
                  xlab="log₁₀(r/r_s)", ylab="f_obs/f_emit")

    # GPS 修正
    print("\n  实际应用：GPS 卫星")
    r_gps = 26560  # km
    r_earth = 6371
    M_ratio = r_earth / (2 * r_gps)  # r_s/r for earth at GPS orbit
    factor_gps = math.sqrt(1 - M_ratio)
    print(f"    GPS 卫星高度 ~ {r_gps - r_earth} km")
    print(f"    引力时间修正 ≈ {(1-factor_gps)*1e10:.1f} × 10⁻¹⁰")
    print(f"    → 每天累积偏差 ~ 45 μs → 位置误差 ~ 14 km/天！")
    print(f"    → 不修正 GPS 根本没法用！")

    print("\n  ※ 反直觉：在 r = r_s（事件视界），红移 z → ∞——")
    print("    你看到坠落者永远'停在'视界处，而他感觉自己瞬间穿过。")
    print("  ※ Princeton 的 Wheeler 命名了'黑洞'一词。")

# ============================================================
# Demo 7 · PPPL 等离子体磁约束  (PPPL)
# ============================================================

def demo_plasma_confinement():
    """
    白话：要把原子核压到一起发生核聚变，需要上亿度的高温。这么热的东西
    没有任何材料容器能装——所以我们用磁场做'隐形笼子'：带电粒子在磁场中
    绕磁力线打转（拉莫尔回旋），回旋半径越小，'关'得越紧。
    反直觉：磁场不对带电粒子做功（力垂直于速度）！它只改变方向，不改变速率。
    粒子像串在磁力线上的珠子，自由地沿线滑动，但很难横穿出去。
    类比：把珠子穿在铁丝上——珠子可以沿铁丝滑动，但不能横着跑出去。
    """
    print("\n" + "=" * 64)
    print("  Demo 7 · PPPL 磁约束聚变：拉莫尔回旋")
    print("=" * 64)

    print("\n  回旋频率：ω_c = qB/m")
    print("  拉莫尔半径：r_L = mv⊥/(qB)")
    print("  回旋周期：T_c = 2πm/(qB)\n")

    q = 1.6e-19  # C
    # 电子在不同磁场中的拉莫尔半径
    m_e = 9.11e-31  # kg
    m_p = 1.67e-27  # kg

    print("  电子 (m=9.11e-31 kg) 在不同磁场中：")
    print(f"  {'B (T)':>10s}  {'ω_c (GHz)':>12s}  "
          f"{'r_L (μm)':>12s}  {'T_c (ps)':>10s}")
    print(f"  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*10}")
    v_perp = 1e6  # m/s
    pts_rL = []
    for B_t in [0.001, 0.01, 0.1, 1.0, 5.0, 10.0]:
        omega_c = q * B_t / m_e
        r_L = m_e * v_perp / (q * B_t)
        T_c = 2 * math.pi / omega_c
        pts_rL.append((math.log10(B_t + 0.001), r_L * 1e6))
        print(f"  {B_t:>10.3f}  {omega_c/1e9:>12.2f}  "
              f"{r_L*1e6:>12.4f}  {T_c*1e12:>10.2f}")

    ascii_scatter(pts_rL, title="电子拉莫尔半径 vs 磁场",
                  xlab="log₁₀(B)", ylab="r_L (μm)")

    print("\n  质子 vs 电子比较 (B=1 T)：")
    B = 1.0
    rL_e = m_e * v_perp / (q * B)
    rL_p = m_p * v_perp / (q * B)
    ratio = m_p / m_e
    print(f"    电子 r_L = {rL_e*1e6:.4f} μm")
    print(f"    质子 r_L = {rL_p*1e6:.2f} μm")
    print(f"    比值 = m_p/m_e = {ratio:.0f}")
    print(f"    → 质子比电子难约束 {ratio:.0f} 倍！")

    print("\n  ※ PPPL 的 NSTX 托卡马克：B ~ 1 T, T ~ 10⁸ K")
    print("    磁场把上亿度的等离子体'兜住'——这可是人类的恒星之火！")
    print("\n  ※ 反直觉：磁场不改变粒子能量——只改变方向。")
    print("  ※ 生活类比：陀螺在桌面上转——外力推它，它不倒而是进动。"
          "带电粒子在磁场中也类似。")

# ============================================================
#  主程序
# ============================================================

DEMOS = [
    ("哈密顿方程与相空间 (PHY 411)",       demo_hamilton),
    ("正则变换 (PHY 411)",                 demo_canonical_transform),
    ("多极展开 (PHY 208)",                 demo_multipole),
    ("Clebsch-Gordan 角动量耦合 (PHY 503)", demo_clebsch_gordan),
    ("玻尔兹曼分布 (PHY 505)",             demo_boltzmann),
    ("引力红移 (PHY 563)",                 demo_schwarzschild_redshift),
    ("PPPL 等离子体磁约束 (PPPL)",          demo_plasma_confinement),
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
    print("  ║        Princeton 物理演示 · 费曼式可视化                  ║")
    print("  ║        理论物理 · PPPL · IAS 弦理论                      ║")
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
    print("  💡 Feynman 在 Princeton：「理论物理的终极目标是")
    print("     用最简单的语言描述最复杂的自然。」")
    print("=" * 64 + "\n")

if __name__ == "__main__":
    main()
