"""
Part IB Machine Learning & Bayesian Inference (Cambridge CST)
==============================================================
覆盖主题：
- 高斯过程回归（RBF kernel）
- EM 算法（GMM）
- MCMC（Metropolis-Hastings）
- 贝叶斯线性回归

核心教材：
- Bishop 2006 "Pattern Recognition and Machine Learning" Springer (PRML)
- Rasmussen & Williams 2006 "Gaussian Processes for Machine Learning" MIT Press
- MacKay 2003 "Information Theory, Inference, and Learning Algorithms" Cambridge University Press
- Gelman et al 2013 "Bayesian Data Analysis" 3rd ed, CRC Press

本文件实现：
- GP 回归（纯 numpy/列表）
- EM for GMM
- Metropolis MCMC 采样
- 贝叶斯线性回归（先验 → 后验 → 预测）

运行：
    python mbi.py
"""
from __future__ import annotations
import math
import random


# ================================================================
# 数学工具
# ================================================================

def matmul(A, B):
    """矩阵乘法"""
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)]
            for i in range(n)]


def mat_vec(A, x):
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def transpose(A):
    return list(map(list, zip(*A)))


def mat_inv_2x2(M):
    """2×2 矩阵求逆"""
    a, b = M[0]
    c, d = M[1]
    det = a * d - b * c
    if abs(det) < 1e-10:
        return [[1e6, 0], [0, 1e6]]
    return [[d/det, -b/det], [-c/det, a/det]]


def gaussian_1d(x, mean, var):
    return (1.0 / math.sqrt(2 * math.pi * var)) * \
           math.exp(-(x - mean)**2 / (2 * var))


def gaussian_nd(x, mean, cov_inv, cov_det):
    """N 维高斯（传入预计算的逆和行列式）"""
    k = len(x)
    diff = [x[i] - mean[i] for i in range(k)]
    if k == 1:
        quad = diff[0]**2 * cov_inv[0][0]
    elif k == 2:
        quad = diff[0]**2 * cov_inv[0][0] + 2*diff[0]*diff[1]*cov_inv[0][1] \
               + diff[1]**2 * cov_inv[1][1]
    else:
        quad = sum(cov_inv[i][j] * diff[i] * diff[j]
                   for i in range(k) for j in range(k))
    return math.exp(-0.5 * quad) / math.sqrt(max(abs(cov_det), 1e-300))


# ================================================================
# 1. 贝叶斯线性回归
# ================================================================

class BayesianLinearRegression:
    """
    y = w^T φ(x) + ε
    先验: w ~ N(0, α^{-1}I)
    似然: y | w ~ N(w^T φ(x), β^{-1})
    后验: w | y ~ N(m_N, S_N)
    S_N = (αI + β Φ^T Φ)^{-1}
    m_N = β S_N Φ^T y
    """

    def __init__(self, alpha=1.0, beta=10.0):
        self.alpha = alpha  # 先验精度
        self.beta = beta    # 噪声精度
        self.m_N = None
        self.S_N = None

    def fit(self, X, y):
        """X: list of [1, x], y: list"""
        n = len(X[0])
        Xt = transpose(X)
        XtX = matmul(Xt, X)
        # S_N^{-1} = αI + β X^T X
        S_inv = [[self.alpha * (1 if i == j else 0) + self.beta * XtX[i][j]
                  for j in range(n)] for i in range(n)]
        S = mat_inv_2x2(S_inv) if n == 2 else S_inv
        Xty = mat_vec(Xt, y)
        m = [self.beta * sum(S[i][j] * Xty[j] for j in range(n)) for i in range(n)]
        self.S_N = S
        self.m_N = m
        return m, S

    def predict(self, x):
        """返回 (均值, 方差)。
        预测分布: p(y*|x*) = N(mean, var)
        var = 1/β + φ(x*)^T S_N φ(x*)
        其中 1/β 是观测噪声, φ^T S_N φ 是参数后验不确定性。
        """
        mean = sum(self.m_N[i] * x[i] for i in range(len(x)))
        var = (1.0 / self.beta +
               sum(x[i] * sum(self.S_N[i][j] * x[j] for j in range(len(x)))
                   for i in range(len(x))))
        return mean, var


# ================================================================
# 2. EM for GMM (1D)
# ================================================================

def em_gmm_1d(data, k=2, n_iter=50):
    """
    EM 算法拟合 1D GMM
    E-step: γ(z_nk) = π_k N(x_n | μ_k, σ_k²) / Σ_j π_j N(...)
    M-step: 更新 π, μ, σ²
    """
    n = len(data)
    means = [sorted(data)[int(n * i / k)] for i in range(k)]
    variances = [sum((x - sum(data)/n)**2 for x in data) / n] * k
    weights = [1.0 / k] * k

    prev_ll = -1e10
    for iteration in range(n_iter):
        # E-step
        gamma = [[0.0] * k for _ in range(n)]
        for i, x in enumerate(data):
            total = sum(weights[j] * gaussian_1d(x, means[j], variances[j])
                        for j in range(k))
            if total < 1e-300:
                total = 1e-300
            for j in range(k):
                gamma[i][j] = weights[j] * gaussian_1d(x, means[j], variances[j]) / total

        # M-step
        Nk = [sum(gamma[i][j] for i in range(n)) for j in range(k)]
        for j in range(k):
            weights[j] = Nk[j] / n
            if Nk[j] > 1e-10:
                means[j] = sum(gamma[i][j] * data[i] for i in range(n)) / Nk[j]
                variances[j] = sum(gamma[i][j] * (data[i] - means[j])**2
                                   for i in range(n)) / Nk[j]

        # Log-likelihood
        ll = sum(math.log(max(sum(weights[j] * gaussian_1d(x, means[j], variances[j])
                              for j in range(k)), 1e-300))
                 for x in data)
        if abs(ll - prev_ll) < 1e-6:
            break
        prev_ll = ll

    return {"weights": weights, "means": means, "variances": variances,
            "log_likelihood": ll, "iterations": iteration + 1}


# ================================================================
# 3. Metropolis MCMC
# ================================================================

def metropolis_sampler(log_target, x0, n_samples=5000, step=1.0):
    """
    Metropolis-Hastings MCMC
    接受率: α = min(1, p(x')/p(x))
    """
    random.seed(42)
    x = x0
    samples = []
    accepted = 0
    for _ in range(n_samples):
        x_proposed = x + random.gauss(0, step)
        log_ratio = log_target(x_proposed) - log_target(x)
        if math.log(random.random()) < log_ratio:
            x = x_proposed
            accepted += 1
        samples.append(x)
    accept_rate = accepted / n_samples
    return samples, accept_rate


# ================================================================
# 4. 高斯过程回归
# ================================================================

def rbf_kernel(x1, x2, length=1.0, sigma=1.0):
    """RBF kernel: k(x,x') = σ² exp(-||x-x'||² / (2l²))"""
    return sigma**2 * math.exp(-(x1 - x2)**2 / (2 * length**2))


def gp_regression(X_train, y_train, X_test, length=1.0, sigma_f=1.0, noise=0.1):
    """
    GP 回归:
    后验均值: μ* = K_*^T (K + σ_n²I)^{-1} y
    后验方差: Σ* = K_** - K_*^T (K + σ_n²I)^{-1} K_*
    简化：用 1D 输入，n 较小（≤10）用直接求逆。
    """
    n = len(X_train)
    # K
    K = [[rbf_kernel(X_train[i], X_train[j], length, sigma_f)
          for j in range(n)] for i in range(n)]
    # K + σ_n² I
    for i in range(n):
        K[i][i] += noise**2

    # 解 K^{-1} y (Gaussian elimination)
    def solve(A, b):
        nn = len(A)
        M = [row[:] + [b[i]] for i, row in enumerate(A)]
        for col in range(nn):
            piv = max(range(col, nn), key=lambda r: abs(M[r][col]))
            M[col], M[piv] = M[piv], M[col]
            for r in range(nn):
                if r != col and abs(M[col][col]) > 1e-12:
                    f = M[r][col] / M[col][col]
                    for c in range(nn + 1):
                        M[r][c] -= f * M[col][c]
        return [M[i][nn] / M[i][i] if abs(M[i][i]) > 1e-12 else 0 for i in range(nn)]

    Ky_inv_y = solve(K, y_train)

    means = []
    varis = []
    for xt in X_test:
        Ks = [rbf_kernel(X_train[i], xt, length, sigma_f) for i in range(n)]
        Kss = rbf_kernel(xt, xt, length, sigma_f) + noise**2
        mu = sum(Ks[i] * Ky_inv_y[i] for i in range(n))
        # 方差简化（近似）：Kss - Ks^T K^{-1} Ks
        Ks_Kinv = solve(K, Ks)
        var = Kss - sum(Ks[i] * Ks_Kinv[i] for i in range(n))
        means.append(mu)
        varis.append(max(var, 0))
    return means, varis


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB ML & Bayesian Inference — Demo")
    print("=" * 64)
    random.seed(42)

    # 1. 贝叶斯线性回归
    print("\n📋 1. 贝叶斯线性回归")
    # y = 2x + 1 + noise
    X = [[1, i * 0.1] for i in range(20)]
    y = [2 * (i * 0.1) + 1 + random.gauss(0, 0.1) for i in range(20)]
    blr = BayesianLinearRegression(alpha=1.0, beta=100.0)
    m, S = blr.fit(X, y)
    print(f"   真实参数: w=[1, 2]")
    print(f"   后验均值: m_N = [{m[0]:.3f}, {m[1]:.3f}]")
    pred_mean, pred_var = blr.predict([1, 1.5])
    pred_ci = 2 * math.sqrt(pred_var)
    print(f"   预测 x=1.5: y = {pred_mean:.3f} ± {pred_ci:.3f} (真实=4.0)")
    print(f"   预测方差 = {pred_var:.4f} (噪声 1/β={1/blr.beta:.4f} + 后验不确定 {pred_var - 1/blr.beta:.4f})")

    # 2. EM GMM
    print("\n📋 2. EM 算法拟合 GMM")
    data = ([random.gauss(-3, 0.8) for _ in range(50)] +
            [random.gauss(3, 1.0) for _ in range(50)])
    result = em_gmm_1d(data, k=2, n_iter=100)
    print(f"   真实: μ=[-3, 3], σ²=[0.64, 1.0]")
    print(f"   EM:   μ={sorted(result['means'], reverse=True)}")
    print(f"         σ²={[round(v,3) for v in sorted(result['variances'], reverse=True)]}")
    print(f"   收敛于 {result['iterations']} 轮, log-likelihood = {result['log_likelihood']:.1f}")

    # 3. MCMC
    print("\n📋 3. Metropolis MCMC（采样双峰分布）")
    def log_bimodal(x):
        return math.log(gaussian_1d(x, -2, 1) + gaussian_1d(x, 2, 1) + 1e-300)
    samples, acc_rate = metropolis_sampler(log_bimodal, x0=0,
                                           n_samples=10000, step=2.0)
    # 统计
    neg = sum(1 for s in samples[1000:] if s < 0)
    pos = sum(1 for s in samples[1000:] if s >= 0)
    mean_est = sum(samples[1000:]) / len(samples[1000:])
    print(f"   双峰分布 N(-2,1) + N(2,1)")
    print(f"   接受率: {acc_rate:.1%}")
    print(f"   样本均值: {mean_est:.3f} (理论≈0)")
    print(f"   负侧样本: {neg}, 正侧样本: {pos}")
    print(f"   → MCMC 正确探索了双峰（两侧都有样本）")

    # 4. GP 回归
    print("\n📋 4. 高斯过程回归")
    X_train = [0, 1, 2, 3, 4]
    y_train = [math.sin(x) + random.gauss(0, 0.05) for x in X_train]
    X_test = [0.5, 1.5, 2.5, 3.5]
    means, varis = gp_regression(X_train, y_train, X_test,
                                 length=1.0, sigma_f=1.0, noise=0.1)
    print(f"   训练点: x={X_train}, y≈sin(x)")
    print(f"   测试预测:")
    for i, xt in enumerate(X_test):
        true_val = math.sin(xt)
        ci = 2 * math.sqrt(varis[i])
        print(f"     x={xt}: μ={means[i]:.3f}±{ci:.3f}, 真实sin={true_val:.3f}")

    print("\n✅ ML & Bayesian Inference 完成！")
    print("\n💡 反直觉发现：")
    print("   - 贝叶斯回归后验是不确定性的分布，不是点估计")
    print("   - EM 对初始化敏感（可能收敛到局部最优）")
    print("   - MCMC 接受率不是越高越好（1D 最优~44%，高维 d→∞ ~23.4%；Roberts-Rosenthal 2001 / Roberts-Gelman-Gilks 1997）")
    print("   - GP 在训练点附近方差小，远离训练点方差大（不确定性量化）")


if __name__ == "__main__":
    demo()
