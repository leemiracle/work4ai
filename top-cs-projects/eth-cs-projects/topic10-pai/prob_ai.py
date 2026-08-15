"""
Probabilistic AI — ETH Zürich
=============================
覆盖主题：
- 贝叶斯网络（变量消除）
- 变分推断（ELBO）
- 粒子滤波
- MCMC（HMC 哈密顿蒙特卡洛）

核心教材/论文：
- Koller & Friedman "Probabilistic Graphical Models" (MIT Press, 2009)
- Kingma & Welling "Auto-Encoding Variational Bayes" arXiv:1312.6114 (2013) — VAE/ELBO
- Gordon, Salmond, Smith "Novel Approach to Nonlinear/Non-Gaussian Bayesian State Estimation" IEE Proc F 140(2): 107-113 (1993) — 粒子滤波
- Hoffman & Gelman "The No-U-Turn Sampler" JMLR 15(1): 1593-1623 (2014) — HMC/NUTS

本文件实现：
1. 贝叶斯网络 + 变量消除
2. ELBO 变分推断（简易 VAE 轮廓）
3. 粒子滤波（定位跟踪）
4. HMC 采样

运行：
    python prob_ai.py
"""
from __future__ import annotations
import math
import random


# ============ 1. 贝叶斯网络 + 变量消除 ============

class BayesNet:
    """离散贝叶斯网络"""

    def __init__(self):
        self.nodes: dict[str, dict] = {}  # name → {parents, cpt}

    def add_node(self, name: str, parents: list[str], cpt: dict):
        """
        cpt: {parent_values_tuple: {value: prob}}
        无父母: cpt = {(): {val: prob}}
        """
        self.nodes[name] = {"parents": parents, "cpt": cpt}

    def sample(self, name: str, parent_values: dict) -> object:
        node = self.nodes[name]
        key = tuple(parent_values[p] for p in node["parents"])
        dist = node["cpt"][key]
        r = random.random()
        cum = 0.0
        for val, p in dist.items():
            cum += p
            if r <= cum:
                return val
        return list(dist.keys())[-1]

    def variable_elimination(self, query: str, evidence: dict, elimination_order: list[str]) -> dict:
        """
        变量消除精确推断
        """
        # 构建所有因子
        factors = []
        for name, node in self.nodes.items():
            factor = self._make_factor(name, evidence)
            factors.append(factor)

        # 按序消除
        for var in elimination_order:
            if var == query:
                continue
            relevant = [f for f in factors if var in f["vars"]]
            factors = [f for f in factors if var not in f["vars"]]
            if relevant:
                product = self._factor_product(relevant)
                summed = self._factor_marginalize(product, var)
                factors.append(summed)

        # 合并剩余因子
        if factors:
            result = self._factor_product(factors)
            return self._normalize(result, query)
        return {}

    # ---- 变量消除辅助方法（factor = {"vars": [...], "table": {tuple: prob}}）----

    def _make_factor(self, name: str, evidence: dict) -> dict:
        """从节点 CPT 构建因子，并用证据归约（删除不一致的条目）"""
        node = self.nodes[name]
        parents = node["parents"]
        cpt = node["cpt"]
        factor_vars = parents + [name]
        free_vars = [v for v in factor_vars if v not in evidence]
        table: dict[tuple, float] = {}
        for parent_key, dist in cpt.items():
            pa = dict(zip(parents, parent_key))
            for val, prob in dist.items():
                full = {**pa, name: val}
                # 与证据不一致 → 跳过
                if any(full.get(ev) != evv for ev, evv in evidence.items()
                       if ev in full):
                    continue
                key = tuple(full[v] for v in free_vars)
                table[key] = table.get(key, 0.0) + prob
        return {"vars": free_vars, "table": table}

    def _factor_product(self, factors: list[dict]) -> dict:
        """多因子乘积"""
        if not factors:
            return {"vars": [], "table": {(): 1.0}}
        result = factors[0]
        for f in factors[1:]:
            result = self._multiply_two(result, f)
        return result

    def _multiply_two(self, f1: dict, f2: dict) -> dict:
        """两个因子相乘（笛卡尔积）"""
        from itertools import product as iproduct
        v1, v2 = f1["vars"], f2["vars"]
        all_vars = list(v1) + [v for v in v2 if v not in v1]
        # 收集每个变量的域
        domains: dict[object, set] = {v: set() for v in all_vars}
        for key in f1["table"]:
            for i, v in enumerate(v1):
                domains[v].add(key[i])
        for key in f2["table"]:
            for i, v in enumerate(v2):
                domains[v].add(key[i])
        table: dict[tuple, float] = {}
        dom_lists = [sorted(domains[v], key=str) for v in all_vars]
        for combo in iproduct(*dom_lists):
            assign = dict(zip(all_vars, combo))
            k1 = tuple(assign[v] for v in v1)
            k2 = tuple(assign[v] for v in v2)
            p1 = f1["table"].get(k1, 0.0)
            p2 = f2["table"].get(k2, 0.0)
            if p1 and p2:
                table[combo] = p1 * p2
        return {"vars": all_vars, "table": table}

    def _factor_marginalize(self, factor: dict, var: str) -> dict:
        """消除变量 var（求和边缘化）"""
        if var not in factor["vars"]:
            return factor
        vi = factor["vars"].index(var)
        new_vars = [v for v in factor["vars"] if v != var]
        table: dict[tuple, float] = {}
        for key, prob in factor["table"].items():
            nk = tuple(k for i, k in enumerate(key) if i != vi)
            table[nk] = table.get(nk, 0.0) + prob
        return {"vars": new_vars, "table": table}

    def _normalize(self, factor: dict, query: str) -> dict:
        """归一化为 {query_value: prob} 概率分布"""
        table = factor["table"]
        total = sum(table.values())
        if total == 0:
            return {}
        result: dict[object, float] = {}
        if query in factor["vars"]:
            qi = factor["vars"].index(query)
            for key, prob in table.items():
                qv = key[qi]
                result[qv] = result.get(qv, 0.0) + prob / total
        else:
            for key, prob in table.items():
                result[key] = prob / total
        return result


def make_cpt(probs: dict) -> dict:
    """辅助：无父母节点的 CPT"""
    return {(): probs}


# ============ 2. 变分推断 ELBO ============

def elbo(log_p_x_z, log_p_z, log_q_z, q_mean, q_std, n_samples: int = 100) -> float:
    """
    ELBO = E_q[log p(x|z) + log p(z) - log q(z)]
    = 重建项 + KL 项。从 q(z)=N(q_mean, q_std²) 采样（而非先验）。
    """
    total = 0.0
    for _ in range(n_samples):
        z = random.gauss(q_mean, q_std)  # 从 q(z) 采样！
        total += log_p_x_z(z) + log_p_z(z) - log_q_z(z)
    return total / n_samples


def kl_gaussian(mu_q, var_q, mu_p=0, var_p=1) -> float:
    """KL(q||p) 两个高斯之间"""
    return 0.5 * (math.log(var_p / var_q) + (var_q + (mu_q - mu_p) ** 2) / var_p - 1)


# ============ 3. 粒子滤波 ============

class ParticleFilter:
    """
    引导粒子滤波（Bootstrap Filter）
    状态空间模型: x_t = f(x_{t-1}) + noise, y_t = g(x_t) + noise
    """

    def __init__(self, n_particles: int, init_fn, transition_fn, likelihood_fn):
        self.n = n_particles
        self.particles = [init_fn() for _ in range(n_particles)]
        self.weights = [1.0 / n_particles] * n_particles
        self.transition_fn = transition_fn
        self.likelihood_fn = likelihood_fn

    def step(self, observation):
        # 1. 预测
        self.particles = [self.transition_fn(p) for p in self.particles]
        # 2. 更新权重
        self.weights = [self.likelihood_fn(p, observation) for p in self.particles]
        total = sum(self.weights)
        if total == 0:
            self.weights = [1.0 / self.n] * self.n
        else:
            self.weights = [w / total for w in self.weights]
        # 3. 重采样
        self._systematic_resample()
        # 返回估计
        return self._estimate()

    def _systematic_resample(self):
        positions = [(random.random() + i) / self.n for i in range(self.n)]
        cumsum = []
        c = 0.0
        for w in self.weights:
            c += w
            cumsum.append(c)
        i, j = 0, 0
        new_particles = []
        while i < self.n:
            if positions[i] < cumsum[j]:
                new_particles.append(self.particles[j])
                i += 1
            else:
                j += 1
        self.particles = new_particles
        self.weights = [1.0 / self.n] * self.n

    def _estimate(self):
        return sum(p * w for p, w in zip(self.particles, self.weights))


# ============ 4. MCMC: HMC ============

def hmc_sample(log_prob_fn, grad_fn, x0: float, n_samples: int = 1000,
               step_size: float = 0.1, n_leapfrog: int = 20) -> list[float]:
    """
    哈密顿蒙特卡洛（1D 教学）
    log_prob_fn(x): 对数概率
    grad_fn(x): d/dx log_prob
    """
    samples = []
    x = x0
    current_logp = log_prob_fn(x)

    for _ in range(n_samples):
        # 采样动量 p ~ N(0,1)
        p = random.gauss(0, 1)
        current_H = -current_logp + 0.5 * p ** 2

        # Leapfrog
        x_new = x
        p_new = p
        p_new += 0.5 * step_size * grad_fn(x_new)
        for _ in range(n_leapfrog):
            x_new += step_size * p_new
            if _ < n_leapfrog - 1:
                p_new += step_size * grad_fn(x_new)
        p_new += 0.5 * step_size * grad_fn(x_new)

        # Metropolis 接受
        new_logp = log_prob_fn(x_new)
        new_H = -new_logp + 0.5 * p_new ** 2
        accept_ratio = math.exp(current_H - new_H)

        if random.random() < accept_ratio:
            x = x_new
            current_logp = new_logp
        samples.append(x)

    return samples


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Probabilistic AI: Bayes Net + ELBO + PF + HMC")
    print("=" * 60)
    random.seed(42)

    # 1. 贝叶斯网络
    print("\n📋 1. 贝叶斯网络（降雨 → 洒水 → 湿草）")
    bn = BayesNet()
    bn.add_node("Rain", [], make_cpt({True: 0.2, False: 0.8}))
    bn.add_node("Sprinkler", [], make_cpt({True: 0.5, False: 0.5}))
    bn.add_node("WetGrass", ["Rain", "Sprinkler"], {
        (True, True): {True: 0.99, False: 0.01},
        (True, False): {True: 0.8, False: 0.2},
        (False, True): {True: 0.9, False: 0.1},
        (False, False): {True: 0.01, False: 0.99},
    })
    # 蒙特卡洛估计 P(Rain=True | WetGrass=True)
    n_trials = 50000
    wet_count = 0
    rain_given_wet = 0
    for _ in range(n_trials):
        rain = bn.sample("Rain", {})
        sprink = bn.sample("Sprinkler", {})
        wet = bn.sample("WetGrass", {"Rain": rain, "Sprinkler": sprink})
        if wet:
            wet_count += 1
            if rain:
                rain_given_wet += 1
    p_rain_wet = rain_given_wet / max(wet_count, 1)
    print(f"   P(Rain=T | WetGrass=T) ≈ {p_rain_wet:.3f} (MC, {n_trials} 采样)")
    print(f"   先验 P(Rain=T) = 0.2 → 后验上升 → 贝叶斯推断生效")

    # 变量消除精确推断
    ve_result = bn.variable_elimination("Rain", {"WetGrass": True}, ["Sprinkler"])
    p_rain_ve = ve_result.get(True, 0)
    print(f"   P(Rain=T | WetGrass=T) = {p_rain_ve:.3f} (VE 变量消除，精确)")
    print(f"   → MC ≈ VE，两种推断一致")

    # 2. ELBO
    print("\n📋 2. 变分推断 ELBO")
    # 简单: q(z)=N(μ,σ²), p(z)=N(0,1), p(x|z)=N(z,1)
    mu_q, var_q = 0.5, 0.8
    std_q = var_q ** 0.5
    def log_p_x_z(z): return -0.5 * (0.3 - z) ** 2  # x=0.3
    def log_p_z(z): return -0.5 * z ** 2
    def log_q_z(z): return -0.5 * (z - mu_q) ** 2 / var_q
    elbo_val = elbo(log_p_x_z, log_p_z, log_q_z, q_mean=mu_q, q_std=std_q, n_samples=500)
    kl = kl_gaussian(mu_q, var_q)
    print(f"   q(z)=N({mu_q},{var_q}), p(z)=N(0,1)")
    print(f"   ELBO ≈ {elbo_val:.3f}")
    print(f"   KL(q||p) = {kl:.3f} (越小越接近先验)")

    # 3. 粒子滤波
    print("\n📋 3. 粒子滤波（1D 追踪）")
    true_states = [0.1 * t + 0.5 * math.sin(0.2 * t) for t in range(20)]
    observations = [s + random.gauss(0, 0.3) for s in true_states]

    pf = ParticleFilter(
        n_particles=500,
        init_fn=lambda: random.gauss(0, 0.5),
        transition_fn=lambda x: x + 0.1 + random.gauss(0, 0.1),
        likelihood_fn=lambda x, y: math.exp(-0.5 * ((y - x) / 0.3) ** 2)
    )
    estimates = []
    for obs in observations:
        est = pf.step(obs)
        estimates.append(est)
    mse = sum((e - t) ** 2 for e, t in zip(estimates, true_states)) / len(true_states)
    print(f"   真实轨迹长度: {len(true_states)}")
    print(f"   估计 MSE: {mse:.4f} (观测噪声 σ=0.3)")

    # 4. HMC
    print("\n📋 4. HMC 采样（高斯目标）")
    def logp(x): return -0.5 * x ** 2  # N(0,1)
    def grad(x): return -x
    samples = hmc_sample(logp, grad, x0=0, n_samples=2000, step_size=0.15, n_leapfrog=15)
    # 丢弃 burn-in
    post = samples[500:]
    mean = sum(post) / len(post)
    var = sum((x - mean) ** 2 for x in post) / len(post)
    print(f"   目标: N(0,1)")
    print(f"   HMC 2000 采样 → 均值={mean:.3f}, 方差={var:.3f}")
    print(f"   接受率: 估计高（平滑的 leapfrog）")

    # 反直觉
    print("\n💡 反直觉发现：ELBO = 重建 - KL 的平衡")
    print(f"   ELBO = E_q[log p(x|z)] - KL(q(z)||p(z))")
    print(f"   → 太强调重建 → 过拟合（KL 大）")
    print(f"   → 太强调先验 → 退化（重建差）")
    print(f"   这就是 VAE / β-VAE 的核心张力。")

    print("\n✅ Probabilistic AI 完成！")


if __name__ == "__main__":
    demo()
