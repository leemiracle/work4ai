"""
16-735 + 16-687 Robotics: Methods & Algorithms (CMU)
================================================
覆盖主题（对应 lecture）：
- Optimal control: LQR (Linear Quadratic Regulator) via DARE
- Motion planning: RRT* (asymptotically optimal sampling)
- State estimation: Graph-SLAM (Gauss-Newton optimization)
- Iterative LQR (iLQR) — single step

核心教材/论文：
- "Anderson & Moore 2007 Optimal Control: Linear Quadratic Methods"
- "Karaman & Frazzoli 2011 IJRR" — RRT* (Sampling-based optimal planning)
- "Durrant-Whyte & Bailey 2006 IEEE RAM" — SLAM Part I/II
- "Todorov & Li 2005 CDC" — iLQR / iterative LQG

本文件实现：
- LQR via discrete algebraic Riccati equation (DARE)
- RRT* path planner (rewire + optimal connection)
- Graph-SLAM pose graph (Gauss-Newton)
- iLQR single backward pass

运行：
    python3 robotics.py
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field

# ============ 1. LQR via DARE ============

def solve_dare(A, B, Q, R, n_iters=1000, tol=1e-8):
    """Discrete Algebraic Riccati Equation via iteration.
    P = A^T P A - A^T P B (R + B^T P B)^{-1} B^T P A + Q
    """
    n = len(A)
    P = [[Q[i][j] for j in range(n)] for i in range(n)]

    def mat_mul(X, Y):
        n, m, p = len(X), len(Y), len(Y[0])
        return [[sum(X[i][k]*Y[k][j] for k in range(m)) for j in range(p)]
                for i in range(n)]

    def mat_add(X, Y, sign=1):
        return [[X[i][j] + sign*Y[i][j] for j in range(len(X[0]))] for i in range(len(X))]

    def mat_transpose(X):
        return [[X[j][i] for j in range(len(X))] for i in range(len(X[0]))]

    def mat_inv_1x1(M):
        return [[1.0 / M[0][0]]]

    for _ in range(n_iters):
        At = mat_transpose(A)
        Bt = mat_transpose(B)
        # ATPA = A^T P A
        ATPA = mat_mul(mat_mul(At, P), A)
        # ATPB = A^T P B
        ATPB = mat_mul(mat_mul(At, P), B)
        # BtPB = B^T P B
        BtPB = mat_mul(mat_mul(Bt, P), B)
        # S = R + BtPB (scalar in 1D control)
        S = mat_add(R, BtPB)
        S_inv = mat_inv_1x1(S)
        # K = S_inv B^T P A
        K = mat_mul(S_inv, mat_mul(Bt, mat_mul(P, A)))
        # P_new = Q + ATPA - ATPB K
        P_new = mat_add(mat_add(Q, ATPA), mat_mul(ATPB, K), sign=-1)

        diff = max(abs(P_new[i][j] - P[i][j]) for i in range(n) for j in range(n))
        P = P_new
        if diff < tol:
            break

    # Gain K = (R + B^T P B)^{-1} B^T P A
    Bt = mat_transpose(B)
    BtPB = mat_mul(mat_mul(Bt, P), B)
    S = mat_add(R, BtPB)
    S_inv = mat_inv_1x1(S)
    K = mat_mul(S_inv, mat_mul(Bt, mat_mul(P, A)))
    return P, K


# ============ 2. RRT* Path Planner ============

@dataclass
class Node:
    x: float
    y: float
    parent: int = -1
    cost: float = 0.0

def rrt_star(start, goal, obstacles, x_range, y_range,
             max_iter=300, step=0.5, radius=1.5, goal_tol=0.5):
    """RRT* path planner. obstacles: list of (cx, cy, r)."""
    nodes = [Node(start[0], start[1], cost=0.0)]

    def dist(n1, n2):
        return math.sqrt((n1.x-n2.x)**2 + (n1.y-n2.y)**2)

    def is_free(x, y):
        for ox, oy, r in obstacles:
            if (x-ox)**2 + (y-oy)**2 < r**2:
                return False
        return True

    def collision_free(x1, y1, x2, y2, n_checks=10):
        for t in [i/n_checks for i in range(n_checks+1)]:
            x = x1 + t*(x2-x1)
            y = y1 + t*(y2-y1)
            if not is_free(x, y):
                return False
        return True

    for _ in range(max_iter):
        # random sample (5% goal bias)
        if random.random() < 0.05:
            rx, ry = goal
        else:
            rx = random.uniform(*x_range)
            ry = random.uniform(*y_range)
        rand = Node(rx, ry)

        # find nearest
        nearest_idx = min(range(len(nodes)), key=lambda i: dist(nodes[i], rand))
        nearest = nodes[nearest_idx]

        # steer
        d = dist(nearest, rand)
        if d < 1e-6:
            continue
        ratio = min(step / d, 1.0)
        nx = nearest.x + ratio * (rand.x - nearest.x)
        ny = nearest.y + ratio * (rand.y - nearest.y)
        new_node = Node(nx, ny, parent=nearest_idx, cost=nearest.cost + step)

        if not collision_free(nearest.x, nearest.y, nx, ny):
            continue

        # RRT*: find neighbors and rewire
        neighbors = [i for i, n in enumerate(nodes) if dist(n, new_node) < radius]
        # choose best parent
        for ni in neighbors:
            if collision_free(nodes[ni].x, nodes[ni].y, nx, ny):
                new_cost = nodes[ni].cost + dist(nodes[ni], new_node)
                if new_cost < new_node.cost:
                    new_node.cost = new_cost
                    new_node.parent = ni

        nodes.append(new_node)
        new_idx = len(nodes) - 1

        # rewire neighbors
        for ni in neighbors:
            if ni == new_node.parent:
                continue
            if collision_free(nx, ny, nodes[ni].x, nodes[ni].y):
                through_new = new_node.cost + dist(new_node, nodes[ni])
                if through_new < nodes[ni].cost:
                    nodes[ni].cost = through_new
                    nodes[ni].parent = new_idx

        # goal check
        if dist(new_node, Node(*goal)) < goal_tol:
            return nodes, new_idx
    return nodes, -1


# ============ 3. Graph-SLAM (Gauss-Newton) ============

def graph_slam_1d(odometry, observations, n_iters=10):
    """
    1D pose graph SLAM.
    odometry: list of (relative_motion, variance) between consecutive poses.
    observations: list of (pose_idx, landmark_id, observed_dist, variance).
    """
    n_poses = len(odometry) + 1
    landmarks = set(obs[1] for obs in observations)
    n_lm = len(landmarks)
    lm_index = {lm: i for i, lm in enumerate(landmarks)}

    # State: [x_0, x_1, ..., x_{n_poses-1}, l_0, ..., l_{n_lm-1}]
    n = n_poses + n_lm
    x = [0.0] * n

    for iteration in range(n_iters):
        # Build error + Jacobian (Gauss-Newton)
        H = [[0.0]*n for _ in range(n)]
        b = [0.0]*n

        # Odometry constraints
        for i, (motion, var) in enumerate(odometry):
            err = x[i+1] - x[i] - motion
            info = 1.0/var
            H[i][i] += info; H[i+1][i+1] += info
            H[i][i+1] -= info; H[i+1][i] -= info
            b[i] -= info * err; b[i+1] += info * err

        # Observation constraints (pose to landmark)
        for pose_idx, lm_id, dist, var in observations:
            lm_j = n_poses + lm_index[lm_id]
            err = x[lm_j] - x[pose_idx] - dist
            info = 1.0/var
            H[pose_idx][pose_idx] += info; H[lm_j][lm_j] += info
            H[pose_idx][lm_j] -= info; H[lm_j][pose_idx] -= info
            b[pose_idx] -= info*err; b[lm_j] += info*err

        # Anchor first pose (fix gauge freedom)
        H[0][0] += 1e6
        b[0]   += 1e6 * x[0]    # gradient of (1/2)(1e6)(x₀)²

        # Solve H @ dx = b exactly (Gauss-Newton step) via Gaussian elimination.
        # The diagonal Jacobi approximation does not converge because H is not
        # diagonally dominant (off-diagonal couplings are as large as diagonal).
        aug = [[H[r][c] for c in range(n)] + [b[r]] for r in range(n)]
        for col in range(n):
            piv = max(range(col, n), key=lambda r: abs(aug[r][col]))
            aug[col], aug[piv] = aug[piv], aug[col]
            pv = aug[col][col]
            for j in range(n + 1):
                aug[col][j] /= pv
            for r in range(n):
                if r == col:
                    continue
                f = aug[r][col]
                for j in range(n + 1):
                    aug[r][j] -= f * aug[col][j]
        dx = [aug[i][n] for i in range(n)]
        # Gauss-Newton update: x ← x − H⁻¹ ∇f  (∇f = b, so x − dx)
        for i in range(n):
            x[i] -= dx[i]

    return x[:n_poses], {lm: x[n_poses + lm_index[lm]] for lm in landmarks}


# ============ 4. iLQR (single step) ============

def ilqr_step(A, B, Q, R, x0, horizon=10):
    """Finite-horizon LQR backward + forward pass.

    For linear dynamics  x_{t+1} = A x_t + B u_t
    and quadratic cost   Σ_t (x_t^T Q x_t + u_t^T R u_t)   (terminal cost = Q)

    Computes optimal feedback gains via Riccati recursion, then applies
    them forward.

    Returns (gains, states, controls) where gains[t] = K_t (m×n matrix)
    and the optimal control is  u_t = -K_t x_t.
    """
    n = len(x0)
    m = len(B[0])

    # ---- small dense matrix helpers (n, m are tiny) ----
    def matmul(X, Y):
        return [[sum(X[i][k] * Y[k][j] for k in range(len(Y)))
                 for j in range(len(Y[0]))] for i in range(len(X))]

    def mat_add(X, Y, sign=1):
        return [[X[i][j] + sign * Y[i][j] for j in range(len(X[0]))]
                for i in range(len(X))]

    def mat_sub(X, Y):
        return mat_add(X, Y, sign=-1)

    def transpose(X):
        return [[X[r][c] for r in range(len(X))] for c in range(len(X[0]))]

    def matrix_inverse(M):
        """General inverse via Gauss–Jordan elimination with partial pivoting."""
        sz = len(M)
        aug = [[float(M[i][j]) for j in range(sz)] +
               [1.0 if i == j else 0.0 for j in range(sz)]
               for i in range(sz)]
        for col in range(sz):
            piv = max(range(col, sz), key=lambda r: abs(aug[r][col]))
            aug[col], aug[piv] = aug[piv], aug[col]
            d = aug[col][col]
            for j in range(2 * sz):
                aug[col][j] /= d
            for r in range(sz):
                if r == col:
                    continue
                f = aug[r][col]
                for j in range(2 * sz):
                    aug[r][j] -= f * aug[col][j]
        return [[aug[i][sz + j] for j in range(sz)] for i in range(sz)]

    Bt = transpose(B)
    At = transpose(A)

    # ---- backward Riccati recursion: P_T = Q, iterate P_{t} from P_{t+1} ----
    P = [row[:] for row in Q]          # terminal cost P_T
    gains_rev = []                      # collected K_{T-1}, K_{T-2}, …, K_0
    for _t in range(horizon):
        # B^T P A  (m×n)  and  B^T P B  (m×m)
        BtPA = matmul(matmul(Bt, P), A)
        BtPB = matmul(matmul(Bt, P), B)
        # K = (R + B^T P B)^{-1} B^T P A
        S_inv = matrix_inverse(mat_add(R, BtPB))
        K = matmul(S_inv, BtPA)
        gains_rev.append(K)
        # P_new = Q + A^T P A - A^T P B K
        AtPA = matmul(matmul(At, P), A)
        AtPB = matmul(At, matmul(P, B))
        P = mat_sub(mat_add(Q, AtPA), matmul(AtPB, K))

    gains = gains_rev[::-1]             # chronological: K_0, K_1, …, K_{T-1}

    # ---- forward pass: apply optimal feedback u_t = -K_t x_t ----
    xs = [list(x0)]
    us = []
    for t in range(horizon):
        K_t = gains[t]
        u = [-sum(K_t[i][j] * xs[-1][j] for j in range(n)) for i in range(m)]
        us.append(u)
        x_next = [sum(A[i][j] * xs[-1][j] for j in range(n)) +
                  sum(B[i][j] * u[j] for j in range(m)) for i in range(n)]
        xs.append(x_next)

    return gains, xs, us


# ============ Demo ============

def demo():
    print("=" * 60)
    print("16-735/687 Robotics: LQR, RRT*, Graph-SLAM, iLQR")
    print("=" * 60)
    random.seed(42)

    # --- 1. LQR ---
    print("\n📋 1. LQR via DARE")
    A = [[1.0, 1.0],[0.0, 1.0]]  # double integrator
    B = [[0.0],[1.0]]
    Q = [[1.0, 0.0],[0.0, 1.0]]
    R = [[0.1]]
    P, K = solve_dare(A, B, Q, R)
    print(f"   System: double integrator (A={A}, B={B})")
    print(f"   Optimal gain K = [{K[0][0]:.4f}, {K[0][1]:.4f}]")
    print(f"   Riccati P = [[{P[0][0]:.3f}, {P[0][1]:.3f}], [{P[1][0]:.3f}, {P[1][1]:.3f}]]")
    print(f"   💡 LQR 给出最优稳定控制律 u = -Kx (保证闭环稳定)")

    # --- 2. RRT* ---
    print("\n📋 2. RRT* Path Planning")
    nodes, goal_idx = rrt_star(
        start=(1.0, 1.0), goal=(9.0, 9.0),
        obstacles=[(5.0, 5.0, 1.5), (3.0, 7.0, 1.0)],
        x_range=(0, 10), y_range=(0, 10),
        max_iter=500, step=0.8, radius=2.0, goal_tol=0.8)
    if goal_idx >= 0:
        # backtrack path
        path = []
        idx = goal_idx
        while idx != -1:
            path.append((nodes[idx].x, nodes[idx].y))
            idx = nodes[idx].parent
        path.reverse()
        path_len = sum(math.sqrt((path[i+1][0]-path[i][0])**2 +
                      (path[i+1][1]-path[i][1])**2) for i in range(len(path)-1))
        print(f"   Start (1,1) → Goal (9,9), obstacles at (5,5) & (3,7)")
        print(f"   Path found! {len(path)} nodes, total length = {path_len:.2f}")
        print(f"   Euclidean distance = {math.sqrt(128):.2f}")
        print(f"   💡 RRT* rewires → path cost 随迭代单调下降趋近最优")
    else:
        print(f"   No path found ({len(nodes)} nodes explored)")

    # --- 3. Graph-SLAM ---
    print("\n📋 3. Graph-SLAM (1D)")
    # Robot moves: +2, +3, +1. Observes landmark L1 at distances 5, 3, 1
    odom = [(2.0, 0.1), (3.0, 0.1), (1.0, 0.1)]
    obs = [(0, 'L1', 5.0, 0.5), (1, 'L1', 3.0, 0.5), (2, 'L1', 1.0, 0.5)]
    poses, landmarks = graph_slam_1d(odom, obs, n_iters=20)
    print(f"   Odom: moves +2, +3, +1 → raw poses {[0,2,5,6]}")
    print(f"   SLAM optimized poses: {[round(p,2) for p in poses]}")
    print(f"   Landmark L1: {landmarks.get('L1', 0):.2f}")
    print(f"   💡 多次观测约束 → 里程计漂移被校正")

    # --- 4. iLQR ---
    print("\n📋 4. iLQR Single Step")
    gains, xs, us = ilqr_step(A, B, Q, R, x0=[1.0, 0.0], horizon=5)
    print(f"   Horizon=5, initial state=[1.0, 0.0]")
    print(f"   First control gain K₀: [{gains[0][0][0]:.3f}, {gains[0][0][1]:.3f}]")
    print(f"   Optimal u₀ = {us[0][0]:.4f}")
    print(f"   State trajectory: {[[round(v, 4) for v in s] for s in xs]}")
    print(f"   💡 iLQR 在 LQR 基础上处理非线性系统（迭代线性化）")

    print("\n✅ 16-735/687 Robotics 完成！")
    print("   覆盖：LQR (DARE) / RRT* / Graph-SLAM (Gauss-Newton) / iLQR")


if __name__ == "__main__":
    demo()
