"""
ETH Zürich Informatik — 杂项微项目
==================================
覆盖 10 个专题：
1. Computational Biology — 序列比对
2. Quantum Computing — 量子门
3. Visual Computing — 卷积
4. Geometric Computing — 凸包
5. Programmable Logic (FPGA) — 状态机综合
6. Algorithmic Game Theory — 纳什均衡
7. Reasoning under Uncertainty — DST
8. Computational Statistics — Bootstrap
9. Optimization for ML — 梯度下降
10. Network Security — Diffie-Hellman
"""
import math
import random


# ============ 1. Computational Biology ============

def micro_cb_sequence_alignment():
    """Needleman-Wunsch 序列比对"""
    print("\n📋 Computational Biology: 序列比对")
    seq1 = "GATTACA"
    seq2 = "GCATGCU"
    m, n = len(seq1), len(seq2)
    match, mismatch, gap = 1, -1, -1
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i * gap
    for j in range(n + 1):
        dp[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            s = match if seq1[i-1] == seq2[j-1] else mismatch
            dp[i][j] = max(
                dp[i-1][j-1] + s,
                dp[i-1][j] + gap,
                dp[i][j-1] + gap,
            )
    print(f"   {seq1} vs {seq2}")
    print(f"   最优比对分数 = {dp[m][n]}")


# ============ 2. Quantum Computing ============

def micro_qc_gates():
    """量子门模拟（单量子比特）"""
    print("\n📋 Quantum Computing: 单量子比特门")
    import cmath
    # |0⟩ = [1, 0]
    # Hadamard: H = 1/√2 [[1,1],[1,-1]]
    H = [[1/math.sqrt(2), 1/math.sqrt(2)],
         [1/math.sqrt(2), -1/math.sqrt(2)]]
    # H|0⟩ = |+⟩ = [1/√2, 1/√2]
    state = [sum(H[i][j] * [1, 0][j] for j in range(2)) for i in range(2)]
    p0 = abs(state[0])**2
    p1 = abs(state[1])**2
    print(f"   |0⟩ --H--> [{state[0]:.3f}, {state[1]:.3f}]")
    print(f"   P(|0⟩)={p0:.3f}, P(|1⟩)={p1:.3f}")
    # Pauli-X 门（NOT）
    X = [[0, 1], [1, 0]]
    not_state = [sum(X[i][j] * [1, 0][j] for j in range(2)) for i in range(2)]
    print(f"   X|0⟩ = {not_state} (量子 NOT)")


# ============ 3. Visual Computing ============

def micro_vc_convolution():
    """图像卷积（边缘检测核）"""
    print("\n📋 Visual Computing: 卷积边缘检测")
    # 5x5 图像
    image = [
        [0, 0, 0, 0, 0],
        [0, 9, 9, 9, 0],
        [0, 9, 9, 9, 0],
        [0, 9, 9, 9, 0],
        [0, 0, 0, 0, 0],
    ]
    # Sobel-X 核
    sobel_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    output = [[0]*3 for _ in range(3)]
    for i in range(1, 4):
        for j in range(1, 4):
            val = 0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    val += image[i+di][j+dj] * sobel_x[di+1][dj+1]
            output[i-1][j-1] = val
    print(f"   图像 5x5 (中心亮块):")
    for row in image:
        print(f"     {row}")
    print(f"   Sobel-X 输出 3x3:")
    for row in output:
        print(f"     {row}")
    print(f"   → 左边缘=-36(暗→亮), 右边缘=+36(亮→暗)")


# ============ 4. Geometric Computing ============

def micro_gc_convex_hull():
    """Andrew's 凸包算法"""
    print("\n📋 Geometric Computing: 凸包")
    points = [(0, 3), (2, 2), (1, 1), (2, 1), (3, 0), (0, 0), (3, 3)]
    points = sorted(set(points))
    def cross(O, A, B):
        return (A[0]-O[0])*(B[1]-O[1]) - (A[1]-O[1])*(B[0]-O[0])
    # 下包
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    # 上包
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    print(f"   点: {points}")
    print(f"   凸包: {hull} ({len(hull)} 个顶点)")


# ============ 5. Programmable Logic (FPGA) ============

def micro_fpga_fsm():
    """FPGA 状态机综合（交通灯控制器）"""
    print("\n📋 Programmable Logic (FPGA): 交通灯 FSM")
    states = ["RED", "RED_YELLOW", "GREEN", "YELLOW"]
    transitions = {
        "RED": ("RED_YELLOW", 2),
        "RED_YELLOW": ("GREEN", 1),
        "GREEN": ("YELLOW", 5),
        "YELLOW": ("RED", 2),
    }
    outputs = {
        "RED": (1, 0, 0),      # (R, Y, G)
        "RED_YELLOW": (1, 1, 0),
        "GREEN": (0, 0, 1),
        "YELLOW": (0, 1, 0),
    }
    state = "RED"
    print(f"   状态机: {' → '.join(states)} → ...")
    for step in range(5):
        r, y, g = outputs[state]
        next_state, dur = transitions[state]
        print(f"   t={step}: {state:12s} → RGB=({r},{y},{g}), 持续{dur}s")
        state = next_state


# ============ 6. Algorithmic Game Theory ============

def micro_agt_nash():
    """2x2 博弈纳什均衡"""
    print("\n📋 Algorithmic Game Theory: 纳什均衡")
    # 囚徒困境
    #        C      D
    # C  (-1,-1) (-3, 0)
    # D  (0,-3)  (-2,-2)
    payoff = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2),
    }
    # 检查 (D, D) 是否是纳什均衡
    # 给定对方 D，单方面偏离到 C 会变差吗？
    dd = payoff[('D', 'D')]
    cd = payoff[('C', 'D')]  # P1 偏离到 C
    dc = payoff[('D', 'C')]  # P2 偏离到 C
    is_nash = dd[0] >= cd[0] and dd[1] >= dc[1]
    print(f"   囚徒困境: (C=合作, D=背叛)")
    print(f"   (D,D) = {dd}, 偏离到 (C,D)={cd}, (D,C)={dc}")
    print(f"   (D,D) 是纳什均衡: {'✓' if is_nash else '✗'}")
    print(f"   → 个体理性导致集体非最优（帕累托劣）")


# ============ 7. Reasoning under Uncertainty ============

def micro_ru_dst():
    """Dempster-Shafer 证据理论"""
    print("\n📋 Reasoning under Uncertainty: Dempster-Shafer")
    # 证据理论: belief + plausibility
    # mass 函数 m({A}) = 0.6, m({B}) = 0.3, m({A,B,Θ}) = 0.1
    m1 = {"A": 0.6, "B": 0.3, "Θ": 0.1}
    # Bel(A) = m(A) = 0.6, Pl(A) = m(A) + m(Θ) = 0.7
    bel_A = m1["A"]
    pl_A = m1["A"] + m1["Θ"]
    print(f"   mass: {m1}")
    print(f"   Bel(A) = {bel_A}, Pl(A) = {pl_A}")
    print(f"   区间 [{bel_A}, {pl_A}] = 概率的不确定范围")
    print(f"   → 比 Bayesian 更保守（允许 '不知道'）")


# ============ 8. Computational Statistics ============

def micro_cs_bootstrap():
    """Bootstrap 重采样"""
    print("\n📋 Computational Statistics: Bootstrap 置信区间")
    random.seed(42)
    data = [random.gauss(5, 2) for _ in range(50)]
    sample_mean = sum(data) / len(data)
    # Bootstrap
    n_boot = 1000
    boot_means = []
    for _ in range(n_boot):
        resample = [random.choice(data) for _ in range(len(data))]
        boot_means.append(sum(resample) / len(resample))
    boot_means.sort()
    ci_lo = boot_means[int(0.025 * n_boot)]
    ci_hi = boot_means[int(0.975 * n_boot)]
    print(f"   原始均值 = {sample_mean:.3f}")
    print(f"   95% CI = [{ci_lo:.3f}, {ci_hi:.3f}]")


# ============ 9. Optimization for ML ============

def micro_opt_gd():
    """梯度下降变体对比"""
    print("\n📋 Optimization for ML: 梯度下降")
    # f(x) = x² + 2x + 1 = (x+1)², 最优 x=-1
    def f(x): return x**2 + 2*x + 1
    def grad(x): return 2*x + 2

    x_gd, x_momentum, x_adam = 0.0, 0.0, 0.0
    v = 0.0  # momentum
    m_adam, v_adam = 0.0, 0.0
    lr = 0.1
    for _ in range(50):
        # GD
        x_gd -= lr * grad(x_gd)
        # Momentum
        v = 0.9 * v + lr * grad(x_momentum)
        x_momentum -= v
        # Adam (简化)
        g = grad(x_adam)
        m_adam = 0.9 * m_adam + 0.1 * g
        v_adam = 0.999 * v_adam + 0.001 * g**2
        x_adam -= lr * m_adam / (math.sqrt(v_adam) + 1e-8)

    print(f"   f(x)=(x+1)², 最优 x=-1")
    print(f"   GD:        x={x_gd:.4f}")
    print(f"   Momentum:  x={x_momentum:.4f}")
    print(f"   Adam:      x={x_adam:.4f}")


# ============ 10. Network Security ============

def micro_ns_dh():
    """Diffie-Hellman 密钥交换"""
    print("\n📋 Network Security: Diffie-Hellman")
    # 公开参数
    p = 23  # 小素数（教学）
    g = 5
    # Alice 选 a=6, Bob 选 b=15
    a, b = 6, 15
    A = pow(g, a, p)  # Alice 公钥
    B = pow(g, b, p)  # Bob 公钥
    # 共享密钥
    s_alice = pow(B, a, p)
    s_bob = pow(A, b, p)
    print(f"   p={p}, g={g}")
    print(f"   Alice: a={a}, A=g^a mod p = {A}")
    print(f"   Bob:   b={b}, B=g^b mod p = {B}")
    print(f"   Alice 算 s = B^a mod p = {s_alice}")
    print(f"   Bob   算 s = A^b mod p = {s_bob}")
    print(f"   共享密钥一致: {'✓' if s_alice == s_bob else '✗'}")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 ETH Zürich 杂项微项目")
    print("=" * 60)

    micro_cb_sequence_alignment()
    micro_qc_gates()
    micro_vc_convolution()
    micro_gc_convex_hull()
    micro_fpga_fsm()
    micro_agt_nash()
    micro_ru_dst()
    micro_cs_bootstrap()
    micro_opt_gd()
    micro_ns_dh()

    print("\n" + "=" * 60)
    print("✅ 全部杂项微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
