#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dm_lin_check.py — DM-LIN-01 线性代数蒸馏卡 L1 验证（12 断言）
对应卡: DM-LIN-01-线性代数.md §4
运行: python3 dm_lin_check.py   （依赖 numpy, sympy）
铁律: 浮点断言带容差; 符号断言 simplify 后判等。
"""
import numpy as np
import sympy as sp

rng = np.random.default_rng(42)
OK = FAIL = 0

def check(name, cond):
    global OK, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond: OK += 1
    else: FAIL += 1
    print(f"[{tag}] {name}")

# L1 交换律反例: AB != BA
A = np.array([[0., 1.], [0., 0.]]); B = np.array([[0., 0.], [1., 0.]])
check("L1 AB≠BA（交换律失效反例）", not np.allclose(A @ B, B @ A))

# L2 条件数 vs 行列式脱钩
D1 = np.diag([1e-3, 1e-3]); D2 = np.diag([1.0, 1e-6])
k1 = np.linalg.cond(D1); k2 = np.linalg.cond(D2)
check("L2 κ(diag(ε,ε))=1 而行列式极小（κ 与 det 脱钩）", abs(k1 - 1) < 1e-12 and k2 > 1e5)

# L3 可对角化 ≠ 正交可对角化: [[1,1],[0,2]] 特征向量不正交
M = np.array([[1., 1.], [0., 2.]])
w, V = np.linalg.eig(M)
inner = abs(V[:, 0] @ V[:, 1])
check("L3 可对角化矩阵特征向量可不正交（|<v1,v2>|>0.3）", inner > 0.3)

# L4 谱半径 < 谱范数（幂零反例）
N = np.array([[0., 1.], [0., 0.]])
rho = np.max(np.abs(np.linalg.eigvals(N))); nrm = np.linalg.norm(N, 2)
check("L4 ρ(A)=0 但 ‖A‖₂=1（谱半径≠谱范数）", rho < 1e-15 and abs(nrm - 1) < 1e-12)

# L5 谱定理数值: 随机对称阵全实谱 + 正交对角化重构
S = rng.standard_normal((8, 8)); S = (S + S.T) / 2
ev = np.linalg.eigvalsh(S)
w5, V5 = np.linalg.eigh(S)
resid = np.linalg.norm(V5 @ np.diag(w5) @ V5.T - S)
check("L5 对称阵 eigh 全实谱 + 正交对角化残差<1e-12", np.allclose(ev.imag, 0) and resid < 1e-12)

# L6 Eckart-Young: 截断 SVD 逼近误差 = sigma_{k+1}（谱范数与 Frobenius 两侧）
G = rng.standard_normal((12, 8)); k = 3
U, sv, Vt = np.linalg.svd(G, full_matrices=False)
Gk = U[:, :k] @ np.diag(sv[:k]) @ Vt[:k, :]
err2 = np.linalg.norm(G - Gk, 2); errF = np.linalg.norm(G - Gk, 'fro')
check("L6 Eckart-Young: 谱范数误差=σ4 且 Frobenius 误差=√(Σσ²)_(>k)",
      abs(err2 - sv[k]) < 1e-12 and abs(errF - np.sqrt(np.sum(sv[k:]**2))) < 1e-12)

# L7 Cayley-Hamilton（符号）: 具体整数矩阵满足自身特征多项式
# 坑1: cp.subs(lam, m) 常数项不乘 I → 返回 Add 混合类型必错；
# 坑2: sum() 初值必须给 zeros 矩阵。手动多项式求值才可靠。
m = sp.Matrix([[2, 1, 0], [1, 3, 1], [0, 1, 2]])
lam = sp.symbols('λ')
cp = m.charpoly(lam).as_expr()          # det(λI - A), 首一
poly = sp.Poly(cp, lam)
terms = [(k[0], c) for k, c in zip(poly.monoms(), poly.coeffs())]
pA = sum((c * m**k for k, c in terms), sp.zeros(3, 3))
check("L7 Cayley-Hamilton: p(A)=0（3×3 符号验证，手动矩阵多项式求值）", pA == sp.zeros(3, 3))

# L8 Gershgorin: 特征值逐个落入某圆盘
M8 = np.array([[4., 1., 0.2], [0.5, -3., 1.], [0.1, 0.3, 6.]])
ev8 = np.linalg.eigvals(M8)
radii = np.abs(M8).sum(axis=1) - np.abs(np.diag(M8))
inside = [any(abs(ev8[i].real - M8[j, j]) <= radii[j] + 1e-12 for j in range(3)) for i in range(3)]
check("L8 Gershgorin: 全部特征值落入圆盘并集", all(inside))

# L9 Courant-Fischer（正确形式）: 降序 λ2 = min_{dim S=n-1} max_{x∈S} R(x)。
# 教师初稿两处真错误被本断言抓住（诚实留痕）:
#   ① 公式方向写反（min-max 的子空间维数是 n-k+1 不是 k）；
#   ② 子空间 max Rayleigh 是压缩矩阵 QᵀSQ 的最大特征值，不是基向量 Rayleigh 的 max。
S9 = rng.standard_normal((6, 6)); S9 = (S9 + S9.T) / 2
ev9 = np.linalg.eigvalsh(S9)[::-1]       # 降序
best = np.inf
for _ in range(500):
    Q = np.linalg.qr(rng.standard_normal((6, 5)))[0]   # n-1 = 5 维子空间
    lam_comp = np.linalg.eigvalsh(Q.T @ S9 @ Q)[-1]    # 压缩矩阵最大特征值
    best = min(best, lam_comp)
check("L9 Courant-Fischer: 5 维子空间 min-max ≥ λ2 且收敛（误差<0.1）",
      best >= ev9[1] - 1e-12 and abs(best - ev9[1]) < 0.1)

# L10 Sylvester 判据: 顺序主子式全正 ⟺ 最小特征值>0（随机 SPD 抽样 20 次）
ok10 = True
for _ in range(20):
    X = rng.standard_normal((5, 5)); P = X @ X.T + 0.5 * np.eye(5)
    leads = all(np.linalg.det(P[:i, :i]) > 0 for i in range(1, 6))
    ok10 &= leads and (np.linalg.eigvalsh(P).min() > 0)
check("L10 Sylvester: SPD ⟹ 顺序主子式全正 ∧ eigmin>0（20 次抽样）", ok10)

# L11 最小二乘: 正规方程解的残差正交于列空间
Amat = rng.standard_normal((20, 5)); b = rng.standard_normal(20)
xls, *_ = np.linalg.lstsq(Amat, b, rcond=None)
r = b - Amat @ xls
check("L11 正规方程: Aᵀr=0（残差⊥列空间，<1e-12）", np.abs(Amat.T @ r).max() < 1e-12)

# L12 Cholesky: SPD ⟹ A=LLᵀ 重构
Y = rng.standard_normal((7, 7)); SPD = Y @ Y.T + np.eye(7)
L12 = np.linalg.cholesky(SPD)
check("L12 Cholesky 重构 ‖LLᵀ−A‖<1e-12 且下三角", 
      np.linalg.norm(L12 @ L12.T - SPD) < 1e-12 and np.allclose(L12, np.tril(L12)))

print(f"\n== 结果：{OK}/{OK+FAIL} 通过 ==")
raise SystemExit(0 if FAIL == 0 else 1)
