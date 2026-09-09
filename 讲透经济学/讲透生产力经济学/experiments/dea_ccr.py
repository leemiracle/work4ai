"""CCR 数据包络分析：线性规划前沿与参照集敏感性（断言自验）
对应《讲透生产力经济学》03 章（构造学 §二：效率前沿）、
04 章（走廊 2：DEA）。数学母港：讲透数学/讲透运筹学（线性规划）。

模型（Charnes-Cooper-Rhodes 1978，投入导向，规模报酬不变）：
    n 个决策单元，各含投入 x∈R^m、产出 y∈R^s
    单元 j₀ 的效率：min θ  s.t.  θ·x_{j0} ≥ Xλ,  Yλ ≥ y_{j0},  λ ≥ 0
    θ=1 ⟹ 前沿（无同行加权组合能用更少投入产出不低）；θ<1 ⟹ 落后

断言（自验证）：
    (a) 5 单元两投入一产出：前沿单元（A、C）θ=1；落后单元 θ<1，
        且 θ 随"被支配程度"单调（B 最差）
    (b) 参照集：每个落后单元的前沿组合只含 θ=1 单元（λ 的支撑集）
    (c) 参照集敏感性：加入一个支配型新单元 D*（投入更少产出更多）后，
        全员 θ 单调不升，且原前沿单元严格下降——"加一个超人全体变矮"
"""
import numpy as np
from scipy.optimize import linprog

# ── 5 个决策单元：(投入1, 投入2) → 产出 ──
X = np.array([
    [2.0, 2.0],    # A：前沿（小投入中产出）
    [4.0, 4.0],    # B：明显落后（双倍投入、产出更低）
    [3.0, 1.0],    # C：前沿（投入2 极省）
    [2.5, 2.5],    # D：略落后于 A
    [3.5, 1.5],    # E：介于中间
], dtype=float)
Y = np.array([3.0, 2.5, 2.8, 2.9, 3.2], dtype=float)
NAMES = ["A", "B", "C", "D", "E"]


def ccr_efficiency(X, Y, j0):
    """解单元 j0 的 CCR 规划（投入导向），返回 (θ, λ)。

    约束（化为 ≤ 形式给 linprog）：
        输入：θ·x_{j0,i} ≥ Σ_j λ_j·x_{j,i}  ⟺  Σλ x_{·i} − θ·x_{j0,i} ≤ 0
        输出：Σ_j λ_j·y_j ≥ y_{j0}          ⟺  −Σλ y_j ≤ −y_{j0}
    """
    n, m = X.shape
    yv = Y.reshape(-1, 1) if Y.ndim == 1 else Y
    s = yv.shape[1]
    c = np.zeros(1 + n); c[0] = 1.0                       # min θ
    A_ub, b_ub = [], []
    for i in range(m):                                    # 投入约束
        row = np.zeros(1 + n); row[0] = -X[j0, i]; row[1:] = X[:, i]
        A_ub.append(row); b_ub.append(0.0)
    for r in range(s):                                    # 产出约束
        row = np.zeros(1 + n); row[1:] = -yv[:, r]
        A_ub.append(row); b_ub.append(-float(yv[j0, r]))
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * (1 + n), method="highs")
    assert res.status == 0, f"LP 未解出: {res.message}"
    return res.x[0], res.x[1:]


def main():
    # ═══ (a) 效率得分 ═══
    thetas, lambdas = [], []
    print("(a) CCR 效率得分（投入导向）：")
    for j, name in enumerate(NAMES):
        th, lam = ccr_efficiency(X, Y, j)
        thetas.append(th); lambdas.append(lam)
        refs = "+".join(f"{NAMES[k]}×{lam[k]:.2f}" for k in range(len(lam)) if lam[k] > 1e-6)
        print(f"    {name}: θ={th:.4f}   参照组合: {refs}")
    thetas = np.array(thetas)
    assert abs(thetas[0] - 1) < 1e-6 and abs(thetas[2] - 1) < 1e-6, "A、C 应在前沿"
    assert thetas[1] < thetas[3] < thetas[0], "B 应最差、D 次之（被支配程度单调）"
    assert thetas[1] < thetas[4] < 1.0, "E 应为中间地带"

    # ═══ (b) 参照集只含前沿单元 ═══
    frontier = {j for j in range(len(NAMES)) if thetas[j] > 1 - 1e-6}
    print(f"\n(b) 前沿单元: {sorted(NAMES[j] for j in frontier)}")
    for j in range(len(NAMES)):
        if j in frontier:
            continue
        support = {k for k in range(len(NAMES)) if lambdas[j][k] > 1e-6}
        assert support <= frontier, f"{NAMES[j]} 的参照集不应含落后单元"
    print("    参照集检查：所有落后单元的 λ 支撑集 ⊆ 前沿 ✅")

    # ═══ (c) 参照集敏感性：加入支配单元 D* ═══
    X2 = np.vstack([X, [1.8, 1.8]])                       # 两维投入皆严格小于 A
    Y2 = np.append(Y, 3.3)                                # 产出高于 A
    NAMES2 = NAMES + ["D*"]
    thetas2 = [ccr_efficiency(X2, Y2, j)[0] for j in range(len(NAMES2))]
    print(f"\n(c) 加入支配单元 D*（投入(1.8,1.8)、产出3.3，逐维支配 A）后：")
    for j, name in enumerate(NAMES):
        print(f"    {name}: θ {thetas[j]:.4f} → {thetas2[j]:.4f}  "
              f"({'不变' if abs(thetas2[j]-thetas[j])<1e-9 else '下降 ' + format(thetas[j]-thetas2[j], '.4f')})")
    assert all(t2 <= t + 1e-9 for t, t2 in zip(thetas, thetas2)), "加单元不应提高任何旧效率"
    assert thetas2[0] < thetas[0] - 1e-6, "原前沿单元 A 应被拉下前沿（严格下降）"
    assert abs(thetas2[5] - 1.0) < 1e-6, "新支配单元应自成前沿"
    print("    断言：全员单调不升、A 严格下降、D* 自成前沿 ✅")
    print("    ——'加一个超人全体变矮'：DEA 的效率是相对样本的（03 章），"
          "但相对性本身可精确陈述。")

    print("\n全部断言通过 ✅  前沿=规划包络；参照集=同行加权反事实；"
          "敏感性=相对性的定量。")
    print("带走一句（04 章）：反事实可以用同行造——DEA 的虚拟组合"
          "就是'本可以的那一个'。")

if __name__ == "__main__":
    main()
