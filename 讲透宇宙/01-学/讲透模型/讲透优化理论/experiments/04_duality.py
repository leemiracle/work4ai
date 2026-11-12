"""
讲透优化理论 04 章实验：SVM 对偶 + 强对偶验证。
跑法：python3 -u experiments/04_duality.py
"""
import numpy as np
from scipy.optimize import minimize


def main():
    np.random.seed(42)
    print("讲透优化理论 04 章实验：SVM 对偶 + 强对偶验证")
    print("=" * 65)
    print("[1] SVM 原问题：min ||w||²/2 s.t. y_i(w·x_i+b) ≥ 1")
    print("=" * 65)
    # 线性可分数据
    X_pos = np.random.randn(20, 2) + [2, 2]
    X_neg = np.random.randn(20, 2) + [-2, -2]
    X = np.vstack([X_pos, X_neg])
    y = np.array([1]*20 + [-1]*20)

    # 原问题
    primal_obj = lambda p: 0.5 * np.dot(p[:2], p[:2])
    constraints = [{'type': 'ineq', 'fun': lambda p, i=i: y[i]*(np.dot(p[:2], X[i]) + p[2]) - 1} for i in range(40)]
    res_p = minimize(primal_obj, [0, 0, 0], constraints=constraints)
    w_p, b_p = res_p.x[:2], res_p.x[2]
    primal_val = res_p.fun
    print(f"  原问题最优 w = ({w_p[0]:.4f}, {w_p[1]:.4f}), b = {b_p:.4f}")
    print(f"  原问题最优值 = {primal_val:.4f}")

    print()
    print("=" * 65)
    print("[2] SVM 对偶问题")
    print("=" * 65)
    n = len(y)
    Q = np.outer(y, y) * (X @ X.T)
    dual_obj = lambda a: 0.5 * a @ Q @ a - a.sum()
    res_d = minimize(dual_obj, np.ones(n)/n,
                     constraints=[{'type': 'eq', 'fun': lambda a: np.dot(a, y)}],
                     bounds=[(0, None)]*n)
    alpha = res_d.x
    w_d = (alpha * y) @ X
    sv_idx = np.argmax(alpha > 1e-4)
    b_d = y[sv_idx] - np.dot(w_d, X[sv_idx])
    dual_val = -res_d.fun
    print(f"  对偶恢复 w = ({w_d[0]:.4f}, {w_d[1]:.4f}), b = {b_d:.4f}")
    print(f"  非零 α 个数（support vectors）= {(alpha > 1e-4).sum()}")
    print(f"  对偶最优值 = {dual_val:.4f}")

    print()
    print("=" * 65)
    print("[3] 强对偶验证")
    print("=" * 65)
    gap = primal_val - dual_val
    print(f"  原问题值   = {primal_val:.6f}")
    print(f"  对偶值     = {dual_val:.6f}")
    print(f"  对偶间隙   = {gap:.6f}")
    print(f"  → {'强对偶 ✓（凸 + Slater 满足）' if abs(gap) < 0.05 else '有间隙 ✗'}")
    print("=" * 65)


if __name__ == "__main__":
    main()
