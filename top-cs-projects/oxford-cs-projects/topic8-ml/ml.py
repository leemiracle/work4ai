"""
Machine Learning (Oxford CS)
================================================
覆盖主题：
- 贝叶斯线性回归
- 高斯过程回归
- 核方法（RBF / 多项式核）
- SVM 对偶形式

核心论文/教材（已核实）：
- Rasmussen & Williams "Gaussian Processes for Machine Learning" MIT Press 2006
- Bishop "Pattern Recognition and Machine Learning" Springer 2006
- Cortes & Vapnik "Support-Vector Networks" Machine Learning 1995
- MacKay "Information Theory, Inference, and Learning Algorithms" Cambridge 2003

本文件实现：
- 贝叶斯线性回归（含后验不确定性）
- 高斯过程回归（RBF 核，含预测方差）
- SVM 对偶问题求解（SMO 简化版）
- 核函数对比（RBF / 多项式 / 线性）

运行：
    python ml.py
"""
from __future__ import annotations
import math
import random


# ============ 矩阵工具（纯 Python） ============

def mat_mul(A, B):
    n, m, p = len(A), len(A[0]), len(B[0])
    C = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            s = 0.0
            for k in range(m):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C


def mat_vec(A, x):
    n, m = len(A), len(A[0])
    return [sum(A[i][j] * x[j] for j in range(m)) for i in range(n)]


def mat_transpose(A):
    return [list(row) for row in zip(*A)]


def mat_add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def mat_inverse_2x2(A):
    """2×2 矩阵求逆"""
    a, b = A[0][0], A[0][1]
    c, d = A[1][0], A[1][1]
    det = a * d - b * c
    return [[d / det, -b / det], [-c / det, a / det]]


def mat_inverse(A):
    """n×n 矩阵求逆（高斯消元法）"""
    n = len(A)
    # 增广矩阵 [A | I]
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        # 选主元
        pivot = max(range(col, n), key=lambda i: abs(M[i][col]))
        M[col], M[pivot] = M[pivot], M[col]
        piv = M[col][col]
        if abs(piv) < 1e-12:
            piv = 1e-12 if piv >= 0 else -1e-12
        for j in range(2 * n):
            M[col][j] /= piv
        for i in range(n):
            if i != col and abs(M[i][col]) > 1e-12:
                factor = M[i][col]
                for j in range(2 * n):
                    M[i][j] -= factor * M[col][j]
    return [row[n:] for row in M]


def mat_det(A):
    """行列式（递归展开）"""
    n = len(A)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    det = 0.0
    for j in range(n):
        minor = [[A[i][k] for k in range(n) if k != j] for i in range(1, n)]
        det += ((-1) ** j) * A[0][j] * mat_det(minor)
    return det


# ============ 1. 贝叶斯线性回归 ============

class BayesianLinearRegression:
    """
    贝叶斯线性回归：
    先验: p(w) = N(w | 0, α⁻¹I)
    似然: p(y | x, w) = N(y | w^T φ(x), β⁻¹)

    后验: p(w | D) = N(w | m_N, S_N)
    m_N = β S_N Φ^T y
    S_N = (αI + β Φ^T Φ)⁻¹

    预测: p(y* | x*) = N(y* | m_N^T φ(x*), σ²*)
    σ²* = 1/β + φ(x*)^T S_N φ(x*)
    """

    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        self.alpha = alpha  # 先验精度
        self.beta = beta    # 噪声精度
        self.m_N = None     # 后验均值
        self.S_N = None     # 后验协方差

    def _design_matrix(self, X):
        """φ(x) = [1, x, x²] （多项式基函数）"""
        return [[1.0, x, x * x] for x in X]

    def fit(self, X: list, y: list):
        Phi = self._design_matrix(X)
        Phi_T = mat_transpose(Phi)
        n_features = len(Phi[0])

        # S_N = (αI + β Φ^T Φ)⁻¹
        PhiTPhi = mat_mul(Phi_T, Phi)
        prior = [[self.alpha if i == j else 0.0 for j in range(n_features)]
                 for i in range(n_features)]
        Sigma_inv = mat_add(prior, [[self.beta * PhiTPhi[i][j] for j in range(n_features)]
                                     for i in range(n_features)])
        self.S_N = mat_inverse(Sigma_inv)

        # m_N = β S_N Φ^T y
        PhiTy = mat_vec(Phi_T, y)
        self.m_N = mat_vec(
            [[self.beta * v for v in row] for row in self.S_N], PhiTy
        )

    def predict(self, x):
        """预测均值和方差"""
        phi = [1.0, x, x * x]
        mean = sum(self.m_N[i] * phi[i] for i in range(len(phi)))
        # 方差 = 1/β + φ^T S_N φ
        Sphi = mat_vec(self.S_N, phi)
        var = 1.0 / self.beta + sum(phi[i] * Sphi[i] for i in range(len(phi)))
        return mean, math.sqrt(max(var, 0))


# ============ 2. 核函数 ============

def rbf_kernel(x1, x2, length_scale=1.0, var_f=1.0):
    """RBF (高斯) 核: k(x,x') = σ²_f exp(-||x-x'||²/(2l²))"""
    dist_sq = sum((a - b) ** 2 for a, b in zip([x1], [x2]))
    return var_f * math.exp(-dist_sq / (2 * length_scale ** 2))


def polynomial_kernel(x1, x2, degree=2, coef0=1.0):
    """多项式核: k(x,x') = (x·x' + c)^d"""
    dot = x1 * x2
    return (dot + coef0) ** degree


def linear_kernel(x1, x2):
    """线性核: k(x,x') = x·x'"""
    return x1 * x2


# ============ 3. 核岭回归（核方法） ============

class KernelRidge:
    """
    核岭回归（Kernel Ridge Regression）:
    min  Σ (y_i - f(x_i))² + λ ||f||²_H    (H: RKHS)
    表示定理: f(x) = Σ α_i k(x_i, x)
    解: α = (K + λI)^{-1} y
    """

    def __init__(self, kernel, lam=0.1):
        self.kernel = kernel
        self.lam = lam

    def fit(self, X, y):
        n = len(X)
        K = [[self.kernel(X[i], X[j]) for j in range(n)] for i in range(n)]
        for i in range(n):
            K[i][i] += self.lam
        K_inv = mat_inverse(K)
        self.alpha = [sum(K_inv[i][j] * y[j] for j in range(n))
                      for i in range(n)]
        self.X = X

    def predict(self, x):
        return sum(self.alpha[i] * self.kernel(self.X[i], x)
                   for i in range(len(self.X)))


# ============ 4. 高斯过程回归 ============

class GaussianProcessRegressor:
    """
    GP 回归:
    f ~ GP(0, k)
    先验: p(f) = N(0, K)   where K_ij = k(x_i, x_j)
    后验预测:
    μ* = K_*^T (K + σ²_n I)⁻¹ y
    σ²* = k(x*,x*) - K_*^T (K + σ²_n I)⁻¹ K_*
    """

    def __init__(self, kernel=rbf_kernel, length_scale=1.0, noise=0.1):
        self.kernel_fn = kernel
        self.length_scale = length_scale
        self.noise = noise
        self.X_train = []
        self.y_train = []
        self.K_inv = None

    def _kernel(self, x1, x2):
        if self.kernel_fn == rbf_kernel:
            return rbf_kernel(x1, x2, self.length_scale)
        return self.kernel_fn(x1, x2)

    def fit(self, X, y):
        self.X_train = list(X)
        self.y_train = list(y)
        n = len(X)
        # 构建核矩阵 K
        K = [[self._kernel(X[i], X[j]) for j in range(n)] for i in range(n)]
        # K + σ²_n I
        for i in range(n):
            K[i][i] += self.noise ** 2
        self.K_inv = mat_inverse(K)

    def predict(self, x):
        n = len(self.X_train)
        # K_* = [k(x*, x_1), ..., k(x*, x_n)]
        K_star = [self._kernel(x, xi) for xi in self.X_train]
        # μ* = K_*^T K_inv y
        K_inv_y = mat_vec(self.K_inv, self.y_train)
        mean = sum(K_star[i] * K_inv_y[i] for i in range(n))
        # σ²* = k(x*,x*) - K_*^T K_inv K_*
        k_ss = self._kernel(x, x)
        K_inv_Kstar = mat_vec(self.K_inv, K_star)
        var = k_ss - sum(K_star[i] * K_inv_Kstar[i] for i in range(n))
        return mean, math.sqrt(max(var, 0))


# ============ 5. SVM 对偶（SMO 简化版） ============

def rbf_kernel_simple(x1, x2):
    """简化的 RBF 核（1D）"""
    return math.exp(-(x1 - x2) ** 2)


class SimpleSVM:
    """
    SVM 对偶问题:
    max  Σ α_i - ½ Σ Σ α_i α_j y_i y_j K(x_i, x_j)
    s.t. 0 ≤ α_i ≤ C, Σ α_i y_i = 0

    决策: f(x) = Σ α_i y_i K(x_i, x) + b

    简化 SMO 求解。
    """

    def __init__(self, C=1.0, kernel=rbf_kernel_simple, max_iter=100):
        self.C = C
        self.kernel = kernel
        self.max_iter = max_iter
        self.alphas = []
        self.b = 0.0
        self.X = []
        self.y = []

    def fit(self, X, y):
        self.X = list(X)
        self.y = list(y)
        n = len(X)
        self.alphas = [0.0] * n
        self.b = 0.0

        # 预计算核矩阵
        K = [[self.kernel(X[i], X[j]) for j in range(n)] for i in range(n)]

        # 简化 SMO
        for _ in range(self.max_iter):
            alpha_prev = list(self.alphas)
            for i in range(n):
                # E_i = f(x_i) - y_i
                f_i = sum(self.alphas[j] * self.y[j] * K[i][j] for j in range(n)) + self.b
                E_i = f_i - y[i]

                if (y[i] * E_i < -0.001 and self.alphas[i] < self.C) or \
                   (y[i] * E_i > 0.001 and self.alphas[i] > 0):
                    # 选 j ≠ i
                    j = (i + 1) % n
                    if j == i:
                        continue
                    f_j = sum(self.alphas[k] * self.y[k] * K[j][k] for k in range(n)) + self.b
                    E_j = f_j - y[j]

                    alpha_i_old = self.alphas[i]
                    alpha_j_old = self.alphas[j]

                    # 计算边界 L, H
                    if y[i] != y[j]:
                        L = max(0, self.alphas[j] - self.alphas[i])
                        H = min(self.C, self.C + self.alphas[j] - self.alphas[i])
                    else:
                        L = max(0, self.alphas[i] + self.alphas[j] - self.C)
                        H = min(self.C, self.alphas[i] + self.alphas[j])
                    if L == H:
                        continue

                    eta = 2 * K[i][j] - K[i][i] - K[j][j]
                    if eta >= 0:
                        continue

                    # 更新 alpha_j
                    self.alphas[j] -= y[j] * (E_i - E_j) / eta
                    self.alphas[j] = max(L, min(H, self.alphas[j]))

                    # 更新 alpha_i
                    self.alphas[i] += y[i] * y[j] * (alpha_j_old - self.alphas[j])

                    # 更新 b
                    b1 = (self.b - E_i
                          - y[i] * (self.alphas[i] - alpha_i_old) * K[i][i]
                          - y[j] * (self.alphas[j] - alpha_j_old) * K[i][j])
                    b2 = (self.b - E_j
                          - y[i] * (self.alphas[i] - alpha_i_old) * K[i][j]
                          - y[j] * (self.alphas[j] - alpha_j_old) * K[j][j])
                    if 0 < self.alphas[i] < self.C:
                        self.b = b1
                    elif 0 < self.alphas[j] < self.C:
                        self.b = b2
                    else:
                        self.b = (b1 + b2) / 2

            # 收敛检查
            diff = sum((self.alphas[i] - alpha_prev[i]) ** 2 for i in range(n))
            if diff < 1e-6:
                break

    def predict(self, x):
        n = len(self.X)
        f = sum(self.alphas[i] * self.y[i] * self.kernel(self.X[i], x)
                for i in range(n)) + self.b
        return 1 if f >= 0 else -1


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Machine Learning (Oxford CS) Demo")
    print("=" * 65)

    random.seed(42)

    # 生成数据: y = 2x + 0.5x² + noise
    print("\n📋 1. 贝叶斯线性回归")
    X_train = [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
    y_train = [2*x + 0.3*x*x + random.gauss(0, 0.3) for x in X_train]

    blr = BayesianLinearRegression(alpha=0.1, beta=10.0)
    blr.fit(X_train, y_train)
    print(f"   后验权重均值 m_N: {[f'{v:.3f}' for v in blr.m_N]}")
    print(f"   (真值约: [0, 2, 0.3])")

    # 预测 + 不确定性
    for x in [-1.5, 0.0, 1.5]:
        mean, std = blr.predict(x)
        true_val = 2*x + 0.3*x*x
        print(f"   x={x:+.1f}: 预测={mean:.3f}±{std:.3f}, 真值={true_val:.3f}")

    # 2. 高斯过程回归
    print("\n📋 2. 高斯过程回归")
    # 少量训练数据
    X_gp = [-3, -1, 0, 1, 3]
    y_gp = [math.sin(x) + random.gauss(0, 0.1) for x in X_gp]

    gp = GaussianProcessRegressor(kernel=rbf_kernel, length_scale=1.0, noise=0.1)
    gp.fit(X_gp, y_gp)

    print(f"   训练数据: sin(x) + noise, {len(X_gp)} 个点")
    # 预测
    test_points = [-2, -0.5, 0.5, 2]
    for x in test_points:
        mean, std = gp.predict(x)
        true_val = math.sin(x)
        in_ci = abs(mean - true_val) < 2 * std
        print(f"   x={x:+.1f}: GP预测={mean:.3f}±{std:.3f}, sin(x)={true_val:.3f}, "
              f"在95%CI内: {'✓' if in_ci else '✗'}")

    # 3. 核函数对比
    print("\n📋 3. 核函数对比")
    x1, x2 = 1.0, 1.5
    print(f"   k({x1}, {x2}):")
    print(f"     RBF (l=1.0):     {rbf_kernel(x1, x2, 1.0):.4f}")
    print(f"     RBF (l=0.5):     {rbf_kernel(x1, x2, 0.5):.4f}")
    print(f"     多项式 (d=2):     {polynomial_kernel(x1, x2, 2):.4f}")
    print(f"     线性:             {linear_kernel(x1, x2):.4f}")

    # 3b. 核岭回归（核方法）
    print("\n📋 3b. 核岭回归（RBF 核）")
    krr = KernelRidge(kernel=lambda a, b: rbf_kernel(a, b, 1.0), lam=0.1)
    krr.fit(X_gp, y_gp)
    for x in [-2, 0.5, 2]:
        mean = krr.predict(x)
        true_val = math.sin(x)
        print(f"   x={x:+.1f}: KRR预测={mean:.3f}, sin(x)={true_val:.3f}")

    # 4. SVM 分类
    print("\n📋 4. SVM 分类")
    # 1D 可分数据
    X_svm = [-3, -2.5, -2, 2, 2.5, 3]
    y_svm = [-1, -1, -1, 1, 1, 1]

    svm = SimpleSVM(C=1.0, max_iter=50)
    svm.fit(X_svm, y_svm)

    correct = 0
    for x, y in zip(X_svm, y_svm):
        pred = svm.predict(x)
        correct += (pred == y)

    print(f"   训练数据: {list(zip(X_svm, y_svm))}")
    print(f"   支持向量 alpha: {[f'{a:.3f}' for a in svm.alphas]}")
    print(f"   b = {svm.b:.3f}")
    print(f"   训练准确率: {correct}/{len(X_svm)}")

    # 测试新点
    for x in [-2.8, 0, 2.8]:
        pred = svm.predict(x)
        print(f"   predict({x:+.1f}) = {pred}")

    # 边际似然（简化）
    print("\n📋 5. GP 边际似然（模型选择）")
    # 对比不同 length_scale 的边际似然
    best_l, best_ll = None, -1e10
    for l in [0.1, 0.5, 1.0, 2.0, 5.0]:
        gp_test = GaussianProcessRegressor(kernel=rbf_kernel, length_scale=l, noise=0.1)
        gp_test.fit(X_gp, y_gp)
        ll = _log_marginal_likelihood(gp_test, X_gp, y_gp)
        marker = " ← best" if ll > best_ll else ""
        if ll > best_ll:
            best_ll = ll
            best_l = l
        print(f"   l={l:.1f}: log p(y|X) = {ll:.2f}{marker}")
    print(f"   最优 length_scale = {best_l}")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. GP 预测在远离训练数据的地方不确定性增大（std 增大）")
    print("      这是贝叶斯方法的核心优势：知道'自己不知道'")
    print("   2. SVM 的 alpha 大部分为 0，只有支持向量非零")
    print("      决策边界只由少数点决定——这是 SVM 稀疏性的体现")
    print(f"   3. GP 最优 length_scale={best_l}，过小(0.1)或过大(5.0)的边际似然都更低")
    print("      —— 边际似然自动做了奥卡姆剃刀（模型复杂度惩罚）")
    print("=" * 65)


def _log_marginal_likelihood(gp, X, y):
    """GP log 边际似然: log p(y|X) = -½ y^T Ky^-1 y - ½ log|Ky| - n/2 log(2π)
    其中 Ky = K + σ²I（含噪声），gp.K_inv = Ky^-1。"""
    n = len(X)
    K_inv_y = mat_vec(gp.K_inv, y)
    data_fit = -0.5 * sum(y[i] * K_inv_y[i] for i in range(n))
    # log|Ky| = -log|Ky^-1| = -log|gp.K_inv|
    # 故 -½ log|Ky| = +½ log|gp.K_inv|
    log_det_K_inv = math.log(abs(mat_det(gp.K_inv)) + 1e-300)
    complexity = 0.5 * log_det_K_inv
    const = -n / 2 * math.log(2 * math.pi)
    return data_fit + complexity + const


if __name__ == "__main__":
    main()
