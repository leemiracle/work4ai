# -*- coding: utf-8 -*-
"""部门间协调的最小可算现场:投入产出乘数(列昂节夫逆矩阵手写实现)。

00-体系结构/03-可构造与结构/04-转代码 三章配套实验。纯标准库。

数学事实链:
  1. 直接消耗系数 a_ij = 部门 j 每单位产出消耗部门 i 的产品(A 的列=投入结构)
  2. 列昂节夫逆 L = (I-A)^{-1} = I + A + A^2 + ...  (Neumann 级数;ρ(A)<1 时收敛)
     —— 04 章代码走廊:逆矩阵第 j 列 = 对部门 j 的 1 元最终需求在全系统激起的总回响
  3. 产出乘数 m_j = L 第 j 列列和,恒 > 1(间接效应被精确求和)
  4. 部门自给度:自耗系数 a_jj 越大(部门内部循环越强),本部门对角元 L_jj 越大
  5. 进口渗漏:国内系数按 (1-m) 缩小,乘数收缩(需求漏到国外去了)
  6. 假想抽取(HEM):把一个部门从表里抽掉,其余部门总产出的损失=抽取效应(断供测痛)

手算例(2×2,农业/制造业):
  A = [[0.15, 0.40],
       [0.30, 0.10]]         两列中间投入率 0.45/0.50,均 <1,生产性成立
  (I-A)^{-1} = (1/0.645) * [[0.90, 0.40],
                            [0.30, 0.85]]
             = [[1.3953, 0.6202],
                [0.4651, 1.3178]]
  乘数(列和):农业 = 1.2/0.645 ≈ 1.8605,制造业 = 1.25/0.645 ≈ 1.9380

跑法: python3 -u experiments/00_input_output.py
"""


def eye(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def mat_sub(X, Y):
    return [[a - b for a, b in zip(rx, ry)] for rx, ry in zip(X, Y)]


def mat_mul(X, Y):
    n, k, m = len(X), len(Y), len(Y[0])
    return [
        [sum(X[i][t] * Y[t][j] for t in range(k)) for j in range(m)] for i in range(n)
    ]


def mat_vec(X, v):
    return [sum(a * b for a, b in zip(row, v)) for row in X]


def gauss_jordan_inverse(M):
    """手写 Gauss-Jordan 求逆(列主元消元)。奇异矩阵直接报错。"""
    n = len(M)
    aug = [list(map(float, M[i])) + list(map(float, eye(n)[i])) for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-14:
            raise ValueError("矩阵奇异:系统不可解(检查 A 或口径)")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [x / p for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col]:
                factor = aug[r][col]
                aug[r] = [x - factor * y for x, y in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


def leontief_inverse(A):
    """列昂节夫逆 (I-A)^{-1} —— 乘数体系的母算具。"""
    return gauss_jordan_inverse(mat_sub(eye(len(A)), A))


def leontief_inverse_series(A, tol=1e-13, max_rounds=100000):
    """Neumann 级数 I+A+A^2+...:波及"一轮一轮"落进矩阵(03 章逐轮视角)。"""
    n = len(A)
    L = eye(n)
    Ak = eye(n)                     # A^k,从 I 起步
    for rounds in range(1, max_rounds + 1):
        Ak = mat_mul(Ak, A)
        added = False
        for i in range(n):
            for j in range(n):
                L[i][j] += Ak[i][j]
                if Ak[i][j] > tol:
                    added = True
        if not added:               # 本轮波及全部低于容差:级数收敛
            return L, rounds
    raise RuntimeError("级数不收敛:谱半径>=1?(先验 Hawkins-Simon 证书)")


def spectral_radius(A, iters=500):
    """幂法估计谱半径 ρ(A)——可解性证书(Hawkins-Simon 的迭代版)。"""
    n = len(A)
    v = [1.0] * n
    for _ in range(iters):
        w = mat_vec(A, v)
        norm = max(abs(x) for x in w)
        if norm == 0:
            return 0.0
        v = [x / norm for x in w]
    Av = mat_vec(A, v)
    return max(abs(x) for x in Av)


def multipliers(L):
    """产出乘数 = 逆矩阵列和:对部门 j 的 1 元最终需求拉动的全社会总产出。"""
    n = len(L)
    return [sum(L[i][j] for i in range(n)) for j in range(n)]


def approx(x, y, tol=1e-9):
    return abs(x - y) <= tol


def show(title, L):
    print(title)
    for row in L:
        print("   [" + "  ".join(f"{v:7.4f}" for v in row) + " ]")


def main():
    # ================= 1. 2×2 手算例:农业 / 制造业 =================
    A = [[0.15, 0.40],
         [0.30, 0.10]]
    L = leontief_inverse(A)

    det = 0.645                       # 手算:0.85*0.90-0.40*0.30
    hand = [[0.90 / det, 0.40 / det],
            [0.30 / det, 0.85 / det]]
    for i in range(2):
        for j in range(2):
            assert approx(L[i][j], hand[i][j]), (i, j, L[i][j], hand[i][j])

    m = multipliers(L)
    assert approx(m[0], 1.20 / det) and approx(m[1], 1.25 / det)
    assert all(x > 1.0 for x in m), "乘数必须 >1:间接效应"
    assert all(L[i][i] >= 1.0 for i in range(2)), "对角元 >=1:自耗至少计入自身"

    print("=" * 64)
    print("1) 2×2 列昂节夫逆(农业/制造业)——与手算逐格吻合")
    print("=" * 64)
    show("(I-A)^{-1} =", L)
    print(f"产出乘数:农业 {m[0]:.4f},制造业 {m[1]:.4f}   (恒>1:间接效应)")

    # ================= 2. Neumann 级数:波及逐轮落表 =================
    Ls, rounds = leontief_inverse_series(A)
    for i in range(2):
        for j in range(2):
            assert approx(Ls[i][j], L[i][j], 1e-9), "级数必须收敛到同一逆矩阵"
    rho = spectral_radius(A)
    assert rho < 1.0
    print()
    print(f"2) Neumann 级数 I+A+A^2+... :{rounds} 轮收敛(谱半径 ρ(A)≈{rho:.4f})")
    print("   与 Gauss 求逆逐格一致——'无穷轮波及'与'一次求逆'是同一头兽")

    # ================= 3. 3×3:农业 / 制造业 / 服务业 =================
    A3 = [[0.15, 0.10, 0.05],
          [0.20, 0.40, 0.20],
          [0.10, 0.15, 0.25]]
    L3 = leontief_inverse(A3)
    m3 = multipliers(L3)
    assert all(x > 1.0 for x in m3)
    assert approx(m3[0], 2.0268, 1e-3) and approx(m3[1], 2.5410, 1e-3)
    assert approx(m3[2], 2.1460, 1e-3)
    # 自给度关系:最大自耗系数 a22=0.40 ⟹ 最大对角元 L22=0.6325/0.3355
    assert max(range(3), key=lambda i: L3[i][i]) == 1
    assert approx(L3[1][1], 0.6325 / 0.3355, 1e-3)

    print()
    print("3) 3×3(农/制造/服务):乘数与自给度")
    show("(I-A)^{-1} =", L3)
    print(f"产出乘数:农业 {m3[0]:.4f},制造业 {m3[1]:.4f},服务 {m3[2]:.4f}")
    print("   制造业自耗系数最大(a22=0.40)⟹ 对角元 L22 最大 "
          f"({L3[1][1]:.4f})⟹ 自给度越高,本部门乘数越大")

    # ================= 4. 自给度对照:a22 从 0.10 提到 0.25 =================
    A2 = [[0.15, 0.40],
          [0.30, 0.25]]
    L2 = leontief_inverse(A2)
    assert L2[1][1] > L[1][1], "部门内部循环增强 ⟹ 本部门乘数上升"
    assert (L2[1][1] - L[1][1]) > (L2[0][0] - L[0][0]), "增益应集中于该部门"
    print()
    print("4) 自给度对照:制造业 a22 0.10→0.25(内部循环增强)")
    print(f"   L22: {L[1][1]:.4f} → {L2[1][1]:.4f} (+{(L2[1][1]/L[1][1]-1)*100:.1f}%),"
          f" 制造业乘数 {m[1]:.4f} → {multipliers(L2)[1]:.4f}")

    # ================= 5. 进口渗漏:30% 中间投入改进口 =================
    leak = 0.30
    Am = [[(1 - leak) * a for a in row] for row in A]
    Lm = leontief_inverse(Am)
    mm = multipliers(Lm)
    assert mm[0] < m[0] and mm[1] < m[1], "需求漏到国外 ⟹ 国内乘数收缩"
    assert all(Lm[i][i] >= 1.0 for i in range(2))
    print()
    print(f"5) 进口渗漏:中间投入 {leak*100:.0f}% 改进口(国内系数×{1-leak:.1f})")
    print(f"   乘数:农业 {m[0]:.4f}→{mm[0]:.4f},制造业 {m[1]:.4f}→{mm[1]:.4f}"
          "  ——引用乘数必问'渗漏扣了没'")

    # ================= 6. HEM 假想抽取:抽掉制造业,断供测痛 =================
    y = [100.0, 150.0, 120.0]
    x = mat_vec(L3, y)

    def drop(A_in, vec_in, k):
        n = len(A_in)
        A_out = [[A_in[i][j] for j in range(n) if j != k] for i in range(n) if i != k]
        return leontief_inverse(A_out), [v for t, v in enumerate(vec_in) if t != k]

    L_sub, y_sub = drop(A3, y, k=1)                # 抽取制造业(行列同删)
    x_sub = mat_vec(L_sub, y_sub)
    base_rest = x[0] + x[2]
    effect = base_rest - sum(x_sub)
    assert effect > 100.0, "制造业抽取的宏观痛感应显著为正"
    print()
    print("6) 假想抽取(HEM):把制造业从表里抽掉(断供测痛)")
    print(f"   最终需求 y={y}")
    print(f"   基准总产出(农/服务两部)={base_rest:.1f},抽取后={sum(x_sub):.1f}")
    print(f"   抽取效应 = {effect:.1f}(其余部门产出损失 "
          f"{effect/base_rest*100:.1f}%)——供应链韧性测算的最小版")

    print()
    print("读数:")
    print("  · 乘数恒>1:间接效应被 (I-A)^{-1} 精确求和;列和=1 元需求的全社会回响")
    print("  · 两种求逆互相印证:Gauss 一次到位;级数逐轮显形(收敛速度=谱半径)")
    print("  · 自给度越高 ⟹ 本部门乘数越大;进口渗漏 ⟹ 国内乘数收缩")
    print("  · HEM=删点测痛:部门网上的'系统重要性'实验(04 章断供走廊)")


if __name__ == "__main__":
    main()
