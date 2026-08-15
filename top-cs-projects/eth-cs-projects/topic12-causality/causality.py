"""
Causality (Jonas Peters) — ETH Zürich
=====================================
覆盖主题：
- PC 算法（因果发现 + 方向确定）
- do-calculus（Pearl 3 规则 + Simpson 悖论数值验证）
- 工具变量（IV）估计
- LiNGAM（简化线性非高斯因果发现 — Hyvärinen 峰度法）

核心教材/论文：
- Pearl "Causality: Models, Reasoning, and Inference" (Cambridge University Press, 2009)
- Spirtes, Glymour, Scheines "Causation, Prediction, and Search" (MIT Press, 2000) — PC algorithm
- Peters, Janzing, Schölkopf "Elements of Causal Inference" (MIT Press, 2017)
- Shimizu et al. "A Linear Non-Gaussian Acyclic Model for Causal Discovery" JMLR 7: 2003-2030 (2006) — LiNGAM
- Hyvärinen & Smith "Pairwise Likelihood Ratios for Estimation of Non-Gaussian SEMs" arXiv:1303.5168 (2013)

运行：
    python causality.py
"""
from __future__ import annotations
import math
import random
from itertools import combinations


# ============ Helper Functions ============

def pearson_corr(x: list[float], y: list[float]) -> float:
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return 0
    return cov / (sx * sy)


def kurtosis(x: list[float]) -> float:
    """
    经验超额峰度的绝对值 |kappa| = |E[(x-mu)^4]/sigma^4 - 3|
    高斯分布 kappa=0；均匀分布 kappa approx -1.2 (|kappa|=1.2)；拉普拉斯 kappa approx 3。
    """
    n = len(x)
    mu = sum(x) / n
    var = sum((xi - mu) ** 2 for xi in x) / n
    if var < 1e-15:
        return 0.0
    return abs(sum((xi - mu) ** 4 for xi in x) / n / var ** 2 - 3)


def _gauss_solve(A: list[list[float]], b: list[float]) -> list[float]:
    """Solve Ax = b via Gauss-Jordan elimination with partial pivoting."""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        if abs(M[col][col]) < 1e-12:
            M[col][col] = 1e-12
        for r in range(n):
            if r != col:
                factor = M[r][col] / M[col][col]
                for c in range(col, n + 1):
                    M[r][c] -= factor * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def _regress_residuals(data: list[list[float]], target_idx: int,
                       cond_indices: list[int]) -> list[float]:
    """Multivariate OLS: regress target on conditioning vars (+ intercept), return residuals."""
    n = len(data)
    if not cond_indices:
        return [row[target_idx] for row in data]
    k = len(cond_indices) + 1  # intercept + conditioning vars
    XTX = [[0.0] * k for _ in range(k)]
    XTy = [0.0] * k
    for row in data:
        xi = [1.0] + [row[c] for c in cond_indices]
        yi = row[target_idx]
        for a in range(k):
            XTy[a] += xi[a] * yi
            for b in range(k):
                XTX[a][b] += xi[a] * xi[b]
    beta = _gauss_solve(XTX, XTy)
    residuals = []
    for row in data:
        pred = beta[0]
        for j, c in enumerate(cond_indices):
            pred += beta[j + 1] * row[c]
        residuals.append(row[target_idx] - pred)
    return residuals


# ============ 1. PC 算法 ============

def partial_corr(data: list[list[float]], i: int, j: int,
                 conditioning: list[int]) -> float:
    """
    计算偏相关系数 rho(X_i, X_j | X_K)
    支持任意大小的条件集（多变量 OLS 回归残差相关）。
    """
    if not conditioning:
        xi = [row[i] for row in data]
        xj = [row[j] for row in data]
        return pearson_corr(xi, xj)
    res_i = _regress_residuals(data, i, conditioning)
    res_j = _regress_residuals(data, j, conditioning)
    return pearson_corr(res_i, res_j)


def pc_algorithm(data: list[list[float]], n_vars: int, alpha: float = 0.1):
    """
    PC 算法：
    1. 完全图
    2. 删除 X_i - X_j 如果存在 K 使 rho(X_i, X_j | K) approx 0
       条件集大小从 0 增到 n_vars-2
    3. V-structure 定向（unshielded collider）
    4. Meek 规则传播方向

    Returns:
      skeleton:   set[frozenset] -- 无向因果骨架边集
      sep_sets:   dict[frozenset, set[int]] -- 每条被删边的分离集
      directed:   set[(from, to)] -- CPDAG 有向边
      undirected: set[frozenset]  -- CPDAG 无向边
    """
    # Step 1: 完全图
    skeleton: set[frozenset] = set()
    for i in range(n_vars):
        for j in range(i + 1, n_vars):
            skeleton.add(frozenset({i, j}))

    sep_sets: dict[frozenset, set[int]] = {}

    # Step 2: 逐边测试，条件集大小从 0 增到 n_vars-2
    L = 0
    while L <= n_vars - 2:
        for edge in list(skeleton):
            if edge not in skeleton:
                continue
            i, j = tuple(sorted(edge))
            others = [v for v in range(n_vars) if v != i and v != j]
            if L > len(others):
                continue
            for cond in combinations(others, L):
                r = partial_corr(data, i, j, list(cond))
                if abs(r) < alpha:
                    skeleton.discard(edge)
                    sep_sets[edge] = set(cond)
                    break
        L += 1

    # Step 3: V-structure 定向（unshielded collider）
    directed: set[tuple[int, int]] = set()
    undirected: set[frozenset] = set(skeleton)

    for k in range(n_vars):
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                if i == k or j == k:
                    continue
                if frozenset({i, j}) in skeleton:
                    continue  # i, j 相邻 -> shielded
                if frozenset({i, k}) not in skeleton or frozenset({j, k}) not in skeleton:
                    continue
                # Unshielded triple: i - k - j
                sep = sep_sets.get(frozenset({i, j}), set())
                if k not in sep:
                    # k 不在分离集中 -> collider: i -> k <- j
                    directed.add((i, k))
                    directed.add((j, k))
                    undirected.discard(frozenset({i, k}))
                    undirected.discard(frozenset({j, k}))

    # Step 4: Meek 规则传播方向
    changed = True
    while changed:
        changed = False
        for edge in list(undirected):
            a, b = tuple(sorted(edge))
            for src, dst in [(a, b), (b, a)]:
                if frozenset({src, dst}) not in undirected:
                    continue
                oriented = False
                # Rule 1: 存在 c->src 且 c 与 dst 不相邻 -> src->dst
                for c in range(n_vars):
                    if (c, src) in directed and c != dst and frozenset({c, dst}) not in skeleton:
                        directed.add((src, dst))
                        undirected.discard(frozenset({src, dst}))
                        changed = True
                        oriented = True
                        break
                if oriented:
                    continue
                # Rule 2: 存在 src->c->dst -> src->dst
                for c in range(n_vars):
                    if (src, c) in directed and (c, dst) in directed and c != src and c != dst:
                        directed.add((src, dst))
                        undirected.discard(frozenset({src, dst}))
                        changed = True
                        break

    return skeleton, sep_sets, directed, undirected


# ============ 2. do-calculus + 通用 d-分离 ============

class CausalModel:
    """
    结构因果模型 (SCM) 简化。
    支持有向无环图边、do-干预、通用 d-分离判定（Bayes-Ball 算法）。
    """

    def __init__(self):
        # DAG 邻接: parent -> children 的逆映射 child -> [parents]
        self.parents: dict[str, list[str]] = {}

    def add_edge(self, parent: str, child: str):
        self.parents.setdefault(child, []).append(parent)

    def do(self, var: str):
        """
        do(X=x): 删除所有指向 X 的边
        相当于把 X 设为外生（干预 vs 观察）
        """
        self.parents[var] = []

    def get_ancestors(self, var: str) -> set:
        ancestors = set()
        stack = list(self.parents.get(var, []))
        while stack:
            p = stack.pop()
            if p not in ancestors:
                ancestors.add(p)
                stack.extend(self.parents.get(p, []))
        return ancestors

    def _children(self, node: str) -> list[str]:
        return [child for child, ps in self.parents.items() if node in ps]

    def is_d_separated(self, x: str, y: str, z: set[str]) -> bool:
        """
        通用 d-分离判定（Bayes-Ball / active-trail 算法）。
        X _||_ Y | Z 当且仅当 Z 阻断了所有 X-Y 之间的活跃路径。

        规则：
        - chain/fork (A->B->C 或 A<-B->C): B 不在 Z 中时活跃
        - collider  (A->B<-C): B 或 B 的后代在 Z 中时活跃
        """
        # Phase 1: 计算 Z 及其所有祖先
        anc_z = set(z)
        to_process = list(z)
        while to_process:
            node = to_process.pop()
            for parent in self.parents.get(node, []):
                if parent not in anc_z:
                    anc_z.add(parent)
                    to_process.append(parent)

        # Phase 2: 从 x 出发 BFS，追踪 (node, direction)
        visited: set[tuple[str, str]] = set()
        to_visit: list[tuple[str, str]] = [(x, "up")]
        reachable: set[str] = set()

        while to_visit:
            node, d = to_visit.pop()
            if (node, d) in visited:
                continue
            visited.add((node, d))

            if node not in z:
                reachable.add(node)

            if d == "up" and node not in z:
                # 从子节点到达：链/分叉，可继续向上和向下
                for parent in self.parents.get(node, []):
                    to_visit.append((parent, "up"))
                for child in self._children(node):
                    to_visit.append((child, "down"))
            elif d == "down":
                # 从父节点到达
                if node not in z:
                    # 链节点：可继续向下
                    for child in self._children(node):
                        to_visit.append((child, "down"))
                if node in anc_z:
                    # collider 激活：node 或其后代在 Z 中
                    for parent in self.parents.get(node, []):
                        to_visit.append((parent, "up"))

        return y not in reachable


def do_calculus_demo():
    """
    do-calculus 3 规则（Pearl 1995）+ Simpson 悖论数值验证。

    Rule 1 (插入/删除观察): P(y|do(x),z,w) = P(y|do(x),w)   if Y _||_ Z | X, W
    Rule 2 (动作/观察交换): P(y|do(x),do(z),w) = P(y|do(x),z,w) if Y _||_ Z | X, W
    Rule 3 (插入/删除动作): P(y|do(x),do(z),w) = P(y|do(x),w)   if Y _||_ Z | X, W

    Simpson 悖论：同一药物在每个子群中看似有害，但总体看似有益。
    P(Recovery|Drug) != P(Recovery|do(Drug))  --- 观察不等于干预！
    """
    # ---- Simpson 悖论经典数据 ----
    # 性别是混杂因子：男性更可能不服药且更容易自愈
    # 男性服药组: 18/30 = 60% 康复
    # 男性未服药:  7/10 = 70% 康复
    # 女性服药组:  2/10 = 20% 康复
    # 女性未服药:  9/30 = 30% 康复
    # ---- 总体（观察）----
    # 服药组:  20/40 = 50% 康复
    # 未服药组: 16/40 = 40% 康复  -> 看似服药有利!
    # ---- do-干预（后门调整 P(Gender)=0.5/0.5）----
    # P(R|do(D))  = 0.6*0.5 + 0.2*0.5 = 0.40
    # P(R|do(~D)) = 0.7*0.5 + 0.3*0.5 = 0.50  -> 干预后服药有害!

    p_male, p_female = 0.5, 0.5
    p_rec_d_male = 18 / 30      # 0.60
    p_rec_nd_male = 7 / 10      # 0.70
    p_rec_d_female = 2 / 10     # 0.20
    p_rec_nd_female = 9 / 30    # 0.30

    # 观察条件概率 P(R|D), P(R|~D)
    p_rec_drug = 20 / 40        # 0.50
    p_rec_nodrug = 16 / 40      # 0.40

    # 干预概率 P(R|do(D)) — 后门调整公式标准化
    p_rec_do_drug = p_rec_d_male * p_male + p_rec_d_female * p_female      # 0.40
    p_rec_do_nodrug = p_rec_nd_male * p_male + p_rec_nd_female * p_female  # 0.50

    print("\n📋 2. do-calculus + Simpson 悖论")
    print("   模型: Gender -> Drug, Gender -> Recovery, Drug -> Recovery")
    print("   （性别是混杂因子）")
    print()
    print("   子群数据:")
    print(f"     男性: 服药 {p_rec_d_male:.0%} vs 未服药 {p_rec_nd_male:.0%} -> 服药更差")
    print(f"     女性: 服药 {p_rec_d_female:.0%} vs 未服药 {p_rec_nd_female:.0%} -> 服药更差")
    print()
    print("   --- 观察（conditioning）---")
    print(f"     P(Recovery|Drug)     = {p_rec_drug:.2f}  (50%)")
    print(f"     P(Recovery|NoDrug)   = {p_rec_nodrug:.2f}  (40%)")
    print(f"     观察结论: 服药有利 (+{(p_rec_drug - p_rec_nodrug) * 100:.0f}pp)  <-- 错觉!")
    print()
    print("   --- 干预（do-calculus 后门调整）---")
    print(f"     P(Recovery|do(Drug))     = {p_rec_do_drug:.2f}  (40%)")
    print(f"     P(Recovery|do(NoDrug))   = {p_rec_do_nodrug:.2f}  (50%)")
    print(f"     干预结论: 服药有害 ({(p_rec_do_drug - p_rec_do_nodrug) * 100:.0f}pp)  <-- 真相!")
    print()
    print(f"   P(R|Drug)={p_rec_drug:.2f} != P(R|do(Drug))={p_rec_do_drug:.2f}")
    print(f"   -> 观察不等于干预：混杂偏差让观察结果完全翻转!")

    # 同时展示通用 d-分离（Bayes-Ball）——用不直接相连的节点
    print()
    # 例 1: 链 Z -> X -> Y，控制 X 后 Z 与 Y d-分离
    cm_chain = CausalModel()
    cm_chain.add_edge("Z", "X")
    cm_chain.add_edge("X", "Y")
    ds_chain = cm_chain.is_d_separated("Z", "Y", {"X"})     # True
    ds_chain0 = cm_chain.is_d_separated("Z", "Y", set())    # False
    print(f"   [d-sep] 链 Z->X->Y: Z _||_ Y | {{X}} = {ds_chain} (ok),  Z _||_ Y | {{}} = {ds_chain0} (active)")
    # 例 2: collider X -> Z <- Y
    cm_coll = CausalModel()
    cm_coll.add_edge("X", "Z")
    cm_coll.add_edge("Y", "Z")
    ds_coll0 = cm_coll.is_d_separated("X", "Y", set())      # True (collider blocks)
    ds_coll1 = cm_coll.is_d_separated("X", "Y", {"Z"})      # False (collider activated)
    print(f"   [d-sep] collider X->Z<-Y: X _||_ Y | {{}} = {ds_coll0} (blocked),  X _||_ Y | {{Z}} = {ds_coll1} (activated!)")

    return cm_chain


# ============ 3. 工具变量 (2SLS) ============

def two_stage_least_squares(z: list[float], x: list[float], y: list[float]) -> float:
    """
    2SLS: 当 X 有内生性（与误差相关），用工具变量 Z
    第一阶段：回归 X ~ Z，得 X_hat
    第二阶段：回归 Y ~ X_hat
    返回因果效应估计 beta
    """
    n = len(z)
    mz = sum(z) / n
    mx = sum(x) / n

    # Stage 1: X = a + b*Z
    denom1 = sum((zi - mz) ** 2 for zi in z)
    if denom1 == 0:
        return 0
    b1 = sum((zi - mz) * (xi - mx) for zi, xi in zip(z, x)) / denom1
    a1 = mx - b1 * mz
    x_hat = [a1 + b1 * zi for zi in z]

    # Stage 2: Y = a + beta*X_hat
    mxh = sum(x_hat) / n
    my = sum(y) / n
    denom2 = sum((xh - mxh) ** 2 for xh in x_hat)
    if denom2 == 0:
        return 0
    beta = sum((xh - mxh) * (yi - my) for xh, yi in zip(x_hat, y)) / denom2
    return beta


def ols(x: list[float], y: list[float]) -> float:
    """普通最小二乘（有偏）"""
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    denom = sum((xi - mx) ** 2 for xi in x)
    if denom == 0:
        return 0
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / denom


# ============ 4. LiNGAM 简化（Hyvärinen 峰度法）============

def lingam_direction(x: list[float], y: list[float]) -> tuple[str, float]:
    """
    LiNGAM 核心思想：非高斯性使得因果方向可识别（Shimizu et al. 2006）。

    正确方向 X->Y: 残差 e_y = y - b*x 是真正的噪声（独立于 X）。
    错误方向 Y->X: 残差 e_x = x - c*y 是 X 和噪声的混合物，
    由 CLT 类比更接近高斯 -> |峰度| 更小。

    Hyvärinen 峰度判据（Hyvärinen & Smith 2013）：
    正确方向 = 残差更非高斯（|kurtosis| 更大）的方向。

    前提：噪声必须非高斯（否则两个方向残差都是高斯，无法区分）。
    """
    n = len(x)
    # 方向 X->Y
    beta_xy = ols(x, y)
    resid_xy = [y[i] - beta_xy * x[i] for i in range(n)]
    k_xy = kurtosis(resid_xy)

    # 方向 Y->X
    beta_yx = ols(y, x)
    resid_yx = [x[i] - beta_yx * y[i] for i in range(n)]
    k_yx = kurtosis(resid_yx)

    # 正确方向的残差更非高斯（kurtosis 更大）
    if k_xy > k_yx:
        return "X->Y", k_xy
    else:
        return "Y->X", k_yx


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Causality (Jonas Peters): PC + do-cal + IV + LiNGAM")
    print("=" * 60)
    random.seed(42)

    # 1. PC 算法（骨架 + 方向）
    print("\n[1] PC 算法（骨架发现 + 方向确定）")
    # 生成数据：X->Z<-Y (collider at Z), Z->W
    # X,Y 独立，都导致 Z，Z 导致 W
    n = 500
    data = []
    for _ in range(n):
        xv = random.uniform(-1, 1)       # var 0 = X
        yv = random.uniform(-1, 1)       # var 1 = Y
        zv = xv + yv + random.gauss(0, 0.3)  # var 2 = Z (collider)
        wv = zv + random.gauss(0, 0.3)   # var 3 = W
        data.append([xv, yv, zv, wv])

    skeleton, sep_sets, directed, undirected = pc_algorithm(data, n_vars=4, alpha=0.1)
    var_names = ["X", "Y", "Z", "W"]
    print(f"   真实结构: X->Z<-Y, Z->W (collider at Z)")
    print(f"   PC 骨架: {[tuple(sorted(e)) for e in sorted(skeleton, key=lambda f: sorted(f))]}")
    sk_edges = [f"{var_names[i]}-{var_names[j]}" for e in skeleton
                for i, j in [tuple(sorted(e))]]
    print(f"   = {sorted(sk_edges)}")
    # 验证关键性质
    no_xy = frozenset({0, 1}) not in skeleton  # X _||_ Y (independent)
    has_xz = frozenset({0, 2}) in skeleton     # X-Z
    has_yz = frozenset({1, 2}) in skeleton     # Y-Z
    has_zw = frozenset({2, 3}) in skeleton     # Z-W
    no_xw = frozenset({0, 3}) not in skeleton  # X _||_ W | Z
    print(f"   X-Y 无边(独立): {'ok' if no_xy else 'FAIL'}, "
          f"X-Z: {'ok' if has_xz else 'FAIL'}, "
          f"Y-Z: {'ok' if has_yz else 'FAIL'}, "
          f"Z-W: {'ok' if has_zw else 'FAIL'}, "
          f"X-W 无边(条件独立): {'ok' if no_xw else 'FAIL'}")
    print(f"   条件集大小测试: 4 变量 -> 测到 size {4-2} = 2")
    # 方向
    dir_strs = [f"{var_names[a]}->{var_names[b]}" for a, b in sorted(directed)]
    und_strs = [f"{var_names[i]}-{var_names[j]}" for e in sorted(undirected, key=lambda f: sorted(f))
                for i, j in [tuple(sorted(e))]]
    print(f"   V-structure + Meek 定向: {sorted(dir_strs)}")
    print(f"   未定向: {sorted(und_strs) if und_strs else '(无)'}")
    collider_ok = (0, 2) in directed and (1, 2) in directed  # X->Z, Y->Z
    print(f"   Collider X->Z<-Y 正确检测: {'ok' if collider_ok else 'FAIL'}")

    # 2. do-calculus (Simpson 悖论)
    cm = do_calculus_demo()

    # 3. IV
    print("\n[3] 工具变量 (2SLS)")
    # 真模型: Y = 2*X + U, X = Z + 0.5*U（内生性）
    true_beta = 2.0
    n = 1000
    Z, X, Y = [], [], []
    for _ in range(n):
        u = random.gauss(0, 1)
        z = random.gauss(0, 1)
        x = z + 0.5 * u
        y = true_beta * x + u
        Z.append(z); X.append(x); Y.append(y)

    ols_est = ols(X, Y)
    iv_est = two_stage_least_squares(Z, X, Y)
    print(f"   真实因果效应 beta = {true_beta}")
    print(f"   OLS 估计 = {ols_est:.3f} (有偏，因 X 与 U 相关)")
    print(f"   2SLS 估计 = {iv_est:.3f} (无偏，IV 消除内生性)")
    print(f"   OLS 误差: {abs(ols_est - true_beta):.3f}, IV 误差: {abs(iv_est - true_beta):.3f}")

    # 4. LiNGAM (5-seed 验证)
    print("\n[4] LiNGAM（非高斯因果方向 — Hyvärinen 峰度法）")
    print("   数据: X ~ Uniform(-1,1), Y = X + Uniform(-0.5,0.5)")
    print("   (噪声必须非高斯，否则两方向残差都是高斯无法区分)")
    correct = 0
    for seed in [1, 42, 7, 99, 2024]:
        random.seed(seed)
        Xl = [random.uniform(-1, 1) for _ in range(500)]
        Yl = [xi + random.uniform(-0.5, 0.5) for xi in Xl]
        d, score = lingam_direction(Xl, Yl)
        ok = (d == "X->Y")
        if ok:
            correct += 1
        print(f"   seed={seed:>4}: direction={d}  kurtosis={score:.4f}  {'ok' if ok else 'FAIL'}")
    print(f"   正确率: {correct}/5 (验收: >=4)")
    print(f"   -> 非高斯性使因果方向可识别（高斯下不可识别）")

    # 反直觉
    print("\n[*] 反直觉发现：观察 != 干预")
    print(f"   Simpson 悖论: P(R|Drug)=50% > P(R|NoDrug)=40% (服药有利)")
    print(f"   但 P(R|do(Drug))=40% < P(R|do(NoDrug))=50% (服药有害!)")
    print(f"   -> 观察包含混杂偏差，do() 消除后门路径才揭示真因果")
    print(f"   Pearl 的 do-calculus 数学化了这一区别。")

    print("\n[done] Causality 完成!")


if __name__ == "__main__":
    demo()
