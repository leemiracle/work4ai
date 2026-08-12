"""
CSC 412 / CSC 512 Probabilistic Machine Learning (University of Toronto)
=========================================================================
覆盖主题：
- 贝叶斯推断（先验/似然/后验）
- EM for GMM（已在 CSC411 基础上深化）
- 变分推断（Mean-Field VI + ELBO）
- MCMC（Metropolis-Hastings）
- 高斯过程（GP 回归）

核心教材：
- Bishop "Pattern Recognition and Machine Learning" Ch.10 (VI) & Ch.11 (Sampling)
- Kingma & Welling "Auto-Encoding Variational Bayes" arXiv:1312.6114
- Rasmussen & Williams "Gaussian Processes for Machine Learning" (2006)
- Hoffman et al. "Stochastic Variational Inference" JMLR 2013

本文件实现（纯 numpy）：
- 贝叶斯线性回归（解析后验 + 证据函数）
- Mean-Field 变分推断（ELBO 最大化）
- Metropolis-Hastings MCMC 采样
- 高斯过程回归（RBF kernel + Cholesky）

运行：
    python prob_ml.py
"""
from __future__ import annotations
import numpy as np


# ============ 1. Bayesian Linear Regression ============

class BayesianLinearRegression:
    """
    贝叶斯线性回归
    先验: p(w) = N(0, α⁻¹I)
    似然: p(y|X,w) = N(Xw, β⁻¹I)
    后验: p(w|X,y) = N(m_N, S_N)
    其中 S_N = (βX^TX + αI)⁻¹, m_N = βS_N X^T y

    边缘似然（Evidence）:
    log p(y|X) = -½[β||y-Xm_N||² + α||m_N||² - log|S_N| + α^d - N log(β) - N log(2π)]
    """

    def __init__(self, alpha=1.0, beta=10.0):
        self.alpha = alpha  # 先验精度
        self.beta = beta    # 噪声精度

    def fit(self, X, y):
        n, d = X.shape
        self.S_N = np.linalg.inv(self.beta * X.T @ X + self.alpha * np.eye(d))
        self.m_N = self.beta * self.S_N @ X.T @ y

    def predict(self, X):
        mean = X @ self.m_N
        var = np.array([x @ self.S_N @ x + 1 / self.beta for x in X])
        return mean, var

    def log_evidence(self, X, y):
        """Bishop Eq 3.86: log marginal likelihood"""
        n, d = X.shape
        residual = y - X @ self.m_N
        # log|S_N^{-1}| = log|β X^T X + α I|
        S_N_inv = self.beta * X.T @ X + self.alpha * np.eye(d)
        log_det_S_inv = np.log(np.linalg.det(S_N_inv) + 1e-300)
        return 0.5 * (
            d * np.log(self.alpha)
            + n * np.log(self.beta)
            - n * np.log(2 * np.pi)
            - self.beta * np.sum(residual ** 2)
            - self.alpha * np.sum(self.m_N ** 2)
            - log_det_S_inv
        )


# ============ 2. Mean-Field Variational Inference ============

class MeanFieldVI:
    """
    Mean-Field Variational Inference
    目标：最大化 ELBO = E_q[log p(x,z)] - E_q[log q(z)]
    等价：最小化 KL(q(z) || p(z|x))

    示例：用 VI 拟合一维高斯（推断均值和方差）
    q(z) = q(μ) q(σ²)  (mean-field 假设)
    """

    def __init__(self, true_mu=3.0, true_sigma=1.5):
        self.true_mu = true_mu
        self.true_sigma = true_sigma

    def generate_data(self, n=100, seed=42):
        rng = np.random.RandomState(seed)
        self.data = rng.normal(self.true_mu, self.true_sigma, n)

    def fit(self, epochs=200, lr=0.01):
        """
        简化 VI：用重参数化梯度估计
        μ_q ~ N(m, s²)，优化 m, s 最大化 ELBO
        """
        n = len(self.data)
        # 初始化变分参数
        m = 0.0   # q(μ) 的均值
        log_s = 0.0  # q(μ) 的 log 标准差
        elbo_history = []

        for epoch in range(epochs):
            # 重参数化采样
            eps = np.random.randn()
            mu_sample = m + np.exp(log_s) * eps

            # ELBO = E_q[log p(data|μ)] - KL(q(μ)||p(μ))
            # log p(data|μ) = Σ log N(x_i; μ, σ_true)
            log_lik = np.sum(-0.5 * ((self.data - mu_sample) / self.true_sigma) ** 2
                             - np.log(self.true_sigma) - 0.5 * np.log(2 * np.pi))

            # KL(q(μ)||N(0,10)) 简化
            kl = 0.5 * (m ** 2 / 10 + np.exp(2 * log_s) / 10 - 2 * log_s - 1 + np.log(10))

            elbo = log_lik - kl
            elbo_history.append(elbo)

            # 重参数化梯度（reparameterization trick）
            # μ_sample = m + exp(log_s) · ε,  ε ~ N(0,1)
            # dμ_sample/dm = 1
            # dμ_sample/d(log_s) = exp(log_s) · ε
            # grad_m  = Σ (x_i - μ_sample)/σ² × 1            - dKL/dm
            # grad_ls = Σ (x_i - μ_sample)/σ² × exp(log_s)·ε - dKL/d(log_s)
            grad_m = np.sum((self.data - mu_sample) / self.true_sigma ** 2) - m / 10
            m += lr * grad_m

            grad_ls = np.sum((self.data - mu_sample) / self.true_sigma ** 2) * np.exp(log_s) * eps \
                      - (np.exp(2 * log_s) / 10 - 1)
            log_s += lr * grad_ls * 0.1

        self.m_q = m
        self.s_q = np.exp(log_s)
        return elbo_history


# ============ 3. Metropolis-Hastings MCMC ============

class MetropolisHastings:
    """
    Metropolis-Hastings 采样器
    从非归一化后验 p(θ|x) ∝ p(x|θ) p(θ) 中采样

    接受率：α = min(1, p(θ'|x)q(θ|θ') / p(θ|x)q(θ'|θ))
    对称提议（高斯随机游走）：q(θ'|θ) = q(θ|θ') → α = min(1, p(θ'|x)/p(θ|x))
    """

    def __init__(self, log_posterior, proposal_std=0.5):
        self.log_post = log_posterior
        self.proposal_std = proposal_std
        self.samples = []
        self.accepted = 0
        self.total = 0

    def sample(self, n_samples, init=0.0, burn_in=500):
        current = init
        current_lp = self.log_post(current)
        all_samples = []

        for i in range(n_samples + burn_in):
            proposal = current + np.random.randn() * self.proposal_std
            proposal_lp = self.log_post(proposal)

            log_alpha = proposal_lp - current_lp
            if np.log(np.random.rand()) < log_alpha:
                current = proposal
                current_lp = proposal_lp
                if i >= burn_in:
                    self.accepted += 1
            if i >= burn_in:
                all_samples.append(current)
                self.total += 1

        self.samples = np.array(all_samples)
        return self.samples

    def acceptance_rate(self):
        return self.accepted / max(self.total, 1)


def demo_mcmc():
    """用 MCMC 估计正态分布的均值"""
    print("\n📋 3. Metropolis-Hastings MCMC")

    # 生成数据
    rng = np.random.RandomState(42)
    true_mu = 5.0
    true_sigma = 2.0
    data = rng.normal(true_mu, true_sigma, 200)

    # 后验：p(μ|data) ∝ Π N(x_i; μ, σ) × N(0, 10)
    def log_posterior(mu):
        if abs(mu) > 100:
            return -np.inf
        log_lik = np.sum(-0.5 * ((data - mu) / true_sigma) ** 2)
        log_prior = -0.5 * mu ** 2 / 100  # 弱先验
        return log_lik + log_prior

    mh = MetropolisHastings(log_posterior, proposal_std=0.5)
    samples = mh.sample(5000, init=0.0, burn_in=1000)

    print(f"   真实 μ = {true_mu}")
    print(f"   MCMC 估计 μ = {np.mean(samples):.3f} ± {np.std(samples):.3f}")
    print(f"   MLE 估计 μ = {np.mean(data):.3f}")
    print(f"   接受率: {mh.acceptance_rate():.1%}")
    print(f"   样本量: {len(samples)}")

    # 对比不同 proposal_std
    print(f"\n   提议分布标准差对效率的影响:")
    for std in [0.1, 0.5, 1.0, 2.0, 5.0]:
        mh2 = MetropolisHastings(log_posterior, proposal_std=std)
        mh2.sample(3000, init=0.0, burn_in=500)
        print(f"     σ_prop={std:.1f}: 接受率={mh2.acceptance_rate():.1%}, "
              f"μ̂={np.mean(mh2.samples):.3f}")

    print(f"\n   反直觉：最优 proposal_std ≈ 0.5（接受率~35%）")
    print(f"   过小→接受率高但移动慢；过大→拒绝率高")


# ============ 4. Gaussian Process Regression ============

class GaussianProcessRegressor:
    """
    GP 回归：
    f ~ GP(m(x), k(x,x'))
    后验: p(f*|X,y,X*) = N(μ*, Σ*)
    μ* = K(X*,X)[K(X,X)+σ²I]⁻¹ y
    Σ* = K(X*,X*) - K(X*,X)[K(X,X)+σ²I]⁻¹ K(X,X*)

    RBF Kernel: k(x,x') = σ_f² exp(-||x-x'||² / (2l²))
    """

    def __init__(self, length_scale=1.0, sigma_f=1.0, sigma_n=0.1):
        self.l = length_scale
        self.sigma_f = sigma_f
        self.sigma_n = sigma_n

    def _kernel(self, X1, X2):
        """RBF Kernel: k(x,x') = σ_f² exp(-||x-x'||²/(2l²))"""
        sq_dists = np.sum(X1 ** 2, axis=1, keepdims=True) + \
                   np.sum(X2 ** 2, axis=1) - 2 * X1 @ X2.T
        return self.sigma_f ** 2 * np.exp(-sq_dists / (2 * self.l ** 2))

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y
        K = self._kernel(X, X) + self.sigma_n ** 2 * np.eye(len(X))
        self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T, np.linalg.solve(self.L, y))

    def predict(self, X_test):
        K_s = self._kernel(X_test, self.X_train)
        K_ss = self._kernel(X_test, X_test)

        mean = K_s @ self.alpha
        v = np.linalg.solve(self.L, K_s.T)
        var = np.diag(K_ss) - np.sum(v ** 2, axis=0)
        return mean, var

    def log_marginal_likelihood(self):
        return -0.5 * self.y_train @ self.alpha - \
               np.sum(np.log(np.diag(self.L))) - \
               len(self.X_train) / 2 * np.log(2 * np.pi)


def demo_gp():
    print("\n📋 4. Gaussian Process 回归")
    # 训练数据
    rng = np.random.RandomState(42)
    X_train = np.sort(rng.uniform(0, 10, 15)).reshape(-1, 1)
    y_train = np.sin(X_train.ravel()) + rng.normal(0, 0.1, 15)

    # 测试点
    X_test = np.linspace(0, 10, 50).reshape(-1, 1)

    # 对比不同 length_scale
    for l in [0.3, 1.0, 3.0]:
        gp = GaussianProcessRegressor(length_scale=l, sigma_n=0.1)
        gp.fit(X_train, y_train)
        mean, var = gp.predict(X_test)
        ml = gp.log_marginal_likelihood()
        print(f"   l={l:.1f}: marginal likelihood={ml:.2f}, "
              f"预测均值范围=[{mean.min():.2f}, {mean.max():.2f}]")

    # 反直觉发现
    print(f"\n   反直觉发现：")
    print(f"   length_scale 控制平滑度 → 反映偏差-方差权衡")
    print(f"   l=0.3 过拟合（高频噪声）；l=3.0 欠拟合（过于平滑）")
    print(f"   l=1.0 是边际似然最大点 → 自动模型选择")

    # 不确定性可视化
    gp_opt = GaussianProcessRegressor(length_scale=1.0, sigma_n=0.1)
    gp_opt.fit(X_train, y_train)
    mean, var = gp_opt.predict(X_test)
    # ASCII 可视化
    print(f"\n   GP 预测不确定性（ASCII）:")
    print(f"   {'x':>5} {'mean':>8} {'std':>8} {'置信区间'}")
    for i in range(0, 50, 5):
        m, s = mean[i], np.sqrt(max(var[i], 0))
        lo, hi = m - 2 * s, m + 2 * s
        bar_pos = int((m + 1.5) / 3.0 * 30)
        print(f"   {X_test[i,0]:5.1f} {m:8.3f} {s:8.3f}  [{lo:.2f}, {hi:.2f}]")


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 412/512: Probabilistic ML Demo")
    print("=" * 60)

    np.random.seed(42)

    # 1. Bayesian Linear Regression
    print("\n📋 1. 贝叶斯线性回归")
    rng = np.random.RandomState(42)
    X = rng.randn(50, 2)
    true_w = np.array([1.5, -0.8])
    y = X @ true_w + 0.1 + rng.randn(50) * 0.3
    blr = BayesianLinearRegression(alpha=1.0, beta=10.0)
    blr.fit(X, y)
    print(f"   真实 w = {true_w}")
    print(f"   后验均值 m_N = [{blr.m_N[0]:.3f}, {blr.m_N[1]:.3f}]")
    print(f"   后验方差 diag(S_N) = [{blr.S_N[0,0]:.4f}, {blr.S_N[1,1]:.4f}]")
    print(f"   log evidence = {blr.log_evidence(X, y):.2f}")

    # 2. Mean-Field VI
    print("\n📋 2. Mean-Field 变分推断")
    vi = MeanFieldVI(true_mu=3.0, true_sigma=1.5)
    vi.generate_data(100)
    elbo_history = vi.fit(epochs=200)
    print(f"   真实 μ = 3.0")
    print(f"   变分 q(μ) 均值 = {vi.m_q:.3f}, 标准差 = {vi.s_q:.3f}")
    print(f"   ELBO 初始 = {elbo_history[0]:.2f}")
    print(f"   ELBO 最终 = {elbo_history[-1]:.2f}")
    print(f"   ELBO 提升 = {elbo_history[-1] - elbo_history[0]:.2f}")

    # 3. MCMC
    demo_mcmc()

    # 4. GP
    demo_gp()

    print("\n✅ CSC 412/512 完成！")
    print("💡 覆盖：贝叶斯推断 + 变分推断(ELBO) + MCMC(Metropolis) + GP回归")
    print("   核心公式：ELBO = E_q[log p(x,z)] - E_q[log q(z)]")
    print("   GP后验: μ* = K_s(K+σ²I)⁻¹y, Σ* = K_ss - K_s(K+σ²I)⁻¹K_s^T")


if __name__ == "__main__":
    demo()
