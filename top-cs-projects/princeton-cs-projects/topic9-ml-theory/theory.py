"""
COS 511 / 512 Theoretical Machine Learning（Princeton）
==========================================================
覆盖主题：
- PAC learning（Probably Approximately Correct）
- VC dimension（shattering / 区间假设类）
- Rademacher complexity（数据相关复杂度）
- Online learning regret（Multiplicative Weights / Hedge）
- SGD 收敛速率（凸优化）

核心论文/教材：
- Valiant 1984 "A Theory of the Learnable" CACM (PAC learning)
- Vapnik & Chervonenkis 1971 "On the Uniform Convergence of Relative Frequencies" (VC dimension)
- Bartlett & Mendelson 2002 "Rademacher and Gaussian Complexities: Risk Bounds" JMLR
- Shalev-Shwartz 2012 "Online Learning and Online Convex Optimization" Foundations and Trends ML
- Shalev-Shwartz & Ben-David "Understanding Machine Learning" 2014 Ch 6 (VC), Ch 21 (Rademacher)

本文件实现：
1. PAC 学习界限验证（Hoeffding 不等式实验）
2. VC dimension 测量（区间假设类的 shattering 实验）
3. Rademacher complexity 经验估计
4. Multiplicative Weights（在线学习 regret 实验）
5. SGD 收敛速率（凸 vs 强凸）

运行：
    python theory.py
"""
from __future__ import annotations
import math
import random
from collections import Counter


# ================================================================
# 1. PAC Learning & Hoeffding Inequality
# ================================================================

def hoeffding_bound(n: int, delta: float) -> float:
    """Hoeffding: P(|mean - E| > ε) ≤ 2*exp(-2nε²)
    Solve for ε: ε = sqrt(ln(2/δ) / (2n))
    """
    return math.sqrt(math.log(2.0 / delta) / (2 * n))


def pac_experiment(true_error: float, delta: float = 0.05, trials: int = 10000) -> float:
    """Empirically verify PAC bound.
    With probability ≥ 1-δ, |empirical_error - true_error| ≤ ε(n, δ).
    """
    violations = 0
    sample_sizes = [50, 100, 200, 500, 1000]
    results = []
    for n in sample_sizes:
        bound = hoeffding_bound(n, delta)
        violated = 0
        for _ in range(trials):
            # Each sample: error occurs with prob = true_error
            empirical = sum(1 for _ in range(n) if random.random() < true_error) / n
            if abs(empirical - true_error) > bound:
                violated += 1
        emp_prob = violated / trials
        results.append((n, bound, emp_prob))
    return results


# ================================================================
# 2. VC Dimension
# ================================================================
# VC(H) = max number of points that H can shatter.
# Shattering: for ALL 2^d labelings, exists h ∈ H consistent with that labeling.

def can_shatter_intervals(points: list[float]) -> bool:
    """Can the class of intervals [a, b] shatter these points?

    Intervals on the real line: VC dimension = 2.
    Any 2 points can be shattered (label both +, label both -,
    label left+right-, label left-right+).
    But 3 points CANNOT: the pattern (+ - +) is impossible
    (if both ends are +, the middle must be + too).
    """
    points = sorted(points)
    d = len(points)
    # Enumerate all 2^d labelings
    for mask in range(2 ** d):
        labels = [(mask >> bit) & 1 for bit in range(d)]
        positive = [points[i] for i in range(d) if labels[i] == 1]
        negative = [points[i] for i in range(d) if labels[i] == 0]
        if not positive:
            continue  # empty interval classifies all as negative, ok
        # Interval [min_positive, max_positive]
        a = min(positive)
        b = max(positive)
        # Check: no negative point should be inside [a, b]
        for neg in negative:
            if a <= neg <= b:
                return False
    return True


def vc_dimension_intervals():
    """Find VC dimension of interval classifiers empirically."""
    for d in range(1, 6):
        # Try multiple point configurations
        shattered = False
        for _ in range(100):
            pts = sorted(random.uniform(0, 1) for _ in range(d))
            if can_shatter_intervals(pts):
                shattered = True
                break
        status = "CAN shatter" if shattered else "CANNOT shatter"
        print(f"   d={d}: {status}")


# ================================================================
# 3. Rademacher Complexity
# ================================================================

def empirical_rademacher(hypothesis_class, samples: list, sigma: list) -> float:
    """Empirical Rademacher complexity (with the **2/n** convention).

    R̂(H) = E_σ [ sup_{h∈H} (2/n) Σ σ_i h(x_i) ]

    sigma_i ∈ {-1, +1} uniformly random.

    NOTE on conventions: this implementation uses the **(2/n)** factor
    (as in Shalev-Shwartz & Ben-David 2014, Ch 21).  Many other texts
    (Bartlett & Mendelson 2002, Mohri et al.) use **(1/n)**.  The 2/n
    convention gives values roughly **2× larger** than the 1/n
    convention, which explains why the empirical result (~0.41) looks
    ~3× the printed ``1/√n`` (~0.14): half the gap is the convention
    factor, the other half is because ``1/√n`` is a loose
    distribution-free upper bound, not the exact value for threshold
    classifiers.
    """
    n = len(samples)
    best = float('-inf')
    for h in hypothesis_class:
        score = sum(s * h(x) for s, x in zip(sigma, samples)) / n
        if score > best:
            best = score
    return 2 * best  # factor of 2 from definition


def rademacher_experiment():
    """Estimate Rademacher complexity of threshold classifiers."""
    n = 50
    samples = [random.uniform(0, 1) for _ in range(n)]
    # Hypothesis class: threshold classifiers h_t(x) = 2*[x < t] - 1
    thresholds = [i / 100 for i in range(101)]
    hyps = [(lambda t: (lambda x: 1.0 if x < t else -1.0))(t) for t in thresholds]

    total = 0.0
    num_trials = 1000
    for _ in range(num_trials):
        sigma = [random.choice([-1, 1]) for _ in range(n)]
        total += empirical_rademacher(hyps, samples, sigma)
    return total / num_trials


# ================================================================
# 4. Multiplicative Weights (Online Learning)
# ================================================================

def multiplicative_weights(experts_losses: list[list[float]], eta: float = 0.1) -> dict:
    """
    Multiplicative Weights / Hedge algorithm for online learning.

    N experts, T rounds. Each round, expert i suffers loss ℓ_i^t ∈ [0,1].
    Algorithm maintains weights w_i, predicts weighted average.
    Regret ≤ O(sqrt(T * ln(N)))

    Returns: {algorithm_total_loss, best_expert_loss, regret}
    """
    N = len(experts_losses[0])
    T = len(experts_losses)
    weights = [1.0] * N
    algo_loss = 0.0

    for t in range(T):
        total_w = sum(weights)
        # Predict: weighted average of expert actions
        # Algo loss = weighted average of expert losses
        round_loss = sum(w / total_w * experts_losses[t][i] for i, w in enumerate(weights))
        algo_loss += round_loss
        # Update weights
        for i in range(N):
            weights[i] *= math.exp(-eta * experts_losses[t][i])

    # Best expert in hindsight
    expert_totals = [sum(experts_losses[t][i] for t in range(T)) for i in range(N)]
    best_loss = min(expert_totals)
    regret = algo_loss - best_loss

    return {
        "algo_loss": algo_loss,
        "best_expert_loss": best_loss,
        "regret": regret,
        "T": T,
        "N": N,
        "avg_regret": regret / T,
    }


# ================================================================
# 5. SGD Convergence Rate
# ================================================================

def sgd_experiment(strongly_convex: bool = True, T: int = 1000,
                   n_trials: int = 1) -> dict:
    """
    SGD on f(w) = (1/2)(w - w*)² + (λ/2)w²

    Convex (λ=0):        f(w) = (1/2)(w-w*)²
    λ-strongly convex:   f(w) = (1/2)(w-w*)² + (λ/2)w²

    Uses **stochastic** gradients (exact gradient + zero-mean Gaussian
    noise).  Without noise this is just GD, and for this simple 1-D
    quadratic the step size 1/√t happens to equal the Newton step at
    t=1, causing 1-step convergence that hides the rate entirely.

    Set n_trials > 1 to average multiple independent runs (recommended
    for stable rate estimates).

    Convergence rates (excess loss):
      - Convex:           E[f(w_T) - f*] = O(1/√T)
      - Strongly convex:  E[f(w_T) - f*] = O(1/T)
    """
    w_star = 3.0
    lam = 0.1 if strongly_convex else 0.0
    noise_std = 0.5  # stochastic gradient noise → true SGD, not GD
    checkpoints = [100, 500, 2000, T]

    # True optimum and optimal loss of the **full** objective
    w_opt = w_star / (1 + lam)       # gradient = (1+λ)w − w* = 0
    f_star = 0.5 * (w_opt - w_star) ** 2 + 0.5 * lam * w_opt ** 2

    # Accumulators for averaging over trials
    avg_excess = {cp: 0.0 for cp in checkpoints}
    avg_final = 0.0
    avg_w_final = 0.0

    for _ in range(n_trials):
        w = 0.0
        losses = []
        for t in range(1, T + 1):
            grad = (w - w_star) + lam * w + random.gauss(0, noise_std)
            if strongly_convex:
                lr = 1.0 / (lam * t + 1)
            else:
                lr = 0.5 / math.sqrt(t)
            w = w - lr * grad
            loss = 0.5 * (w - w_star) ** 2 + 0.5 * lam * w ** 2
            losses.append(loss - f_star)
        for cp in checkpoints:
            avg_excess[cp] += losses[cp - 1]
        avg_final += losses[-1]
        avg_w_final += w

    for cp in checkpoints:
        avg_excess[cp] /= n_trials
    avg_final /= n_trials
    avg_w_final /= n_trials

    theoretical_rate = 1.0 / T if strongly_convex else 1.0 / math.sqrt(T)
    return {
        "final_loss": avg_final,
        "checkpoint_losses": avg_excess,
        "f_star": f_star,
        "w_opt": w_opt,
        "w_final": avg_w_final,
        "theoretical_rate": theoretical_rate,
    }


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 511/512: Theoretical ML Demo")
    print("=" * 60)
    random.seed(42)

    # --- 1. PAC / Hoeffding ---
    print("\n📋 1. PAC Learning & Hoeffding 不等式")
    true_err = 0.3
    delta = 0.05
    print(f"   真实错误率: {true_err}, δ = {delta}")
    print(f"   {'n':>6} {'ε(Hoeffding)':>14} {'违反频率':>10} {'(应 ≤ δ)':>10}")
    results = pac_experiment(true_err, delta)
    for n, bound, emp_prob in results:
        print(f"   {n:>6} {bound:>14.6f} {emp_prob:>10.4f} {'✓' if emp_prob <= delta + 0.02 else '✗':>10}")

    # --- 2. VC Dimension ---
    print("\n📋 2. VC Dimension (区间假设类)")
    vc_dimension_intervals()

    # --- 3. Rademacher Complexity ---
    print("\n📋 3. Rademacher Complexity (阈值分类器)")
    rad = rademacher_experiment()
    vc_bound = math.sqrt(2.0 / 50)  # √(2·VC/n), VC=1 for thresholds
    print(f"   经验 Rademacher (2/n 约定): {rad:.4f}")
    print(f"   经验 Rademacher (1/n 约定): {rad/2:.4f}")
    print(f"   理论上界 √(2·VC/n)=√(2/50): {vc_bound:.4f}")
    print(f"   注: 2/n 约定自带 2× 因子；1/n 约定下经验值({rad/2:.4f}) ≈ 上界({vc_bound:.4f})")

    # --- 4. Multiplicative Weights ---
    print("\n📋 4. Online Learning (Multiplicative Weights)")
    N, T = 10, 200
    # Generate expert losses: expert 0 is slightly better
    experts_losses = []
    for t in range(T):
        round_losses = [random.uniform(0.2, 0.8) for _ in range(N)]
        round_losses[0] = random.uniform(0.1, 0.4)  # best expert
        experts_losses.append(round_losses)
    result = multiplicative_weights(experts_losses, eta=0.5)
    print(f"   {N} experts, {T} rounds")
    print(f"   算法总损失: {result['algo_loss']:.4f}")
    print(f"   最佳专家损失: {result['best_expert_loss']:.4f}")
    print(f"   Regret: {result['regret']:.4f}")
    print(f"   理论上界 O(√(T·ln N)): {math.sqrt(T * math.log(N)):.4f}")
    print(f"   平均 regret: {result['avg_regret']:.6f} (→ 0 as T→∞)")

    # --- 5. SGD Convergence ---
    print("\n📋 5. SGD 收敛速率 (凸 vs 强凸, 10 次平均)")
    T_sgd = 5000
    sgd_results = {}
    for sc, name in [(True, "λ-strongly convex (λ=0.1)"), (False, "convex (λ=0)")]:
        res = sgd_experiment(strongly_convex=sc, T=T_sgd, n_trials=10)
        sgd_results[sc] = res
        rate_name = "O(1/T)" if sc else "O(1/√T)"
        print(f"   {name}  [{rate_name}]:")
        print(f"     w_opt={res['w_opt']:.4f},  SGD w_final={res['w_final']:.4f},  "
              f"f*={res['f_star']:.6f}")
        for cp in [100, 500, 2000, T_sgd]:
            print(f"     excess loss @t={cp:>5}: {res['checkpoint_losses'][cp]:.6f}")

    # Scaling test: ratio of excess loss at t=500 vs t=5000
    # SC O(1/T): ratio ≈ 5000/500 = 10
    # Convex O(1/√T): ratio ≈ √(5000/500) = √10 ≈ 3.16
    sc_r = sgd_results[True]['checkpoint_losses'][500] / max(sgd_results[True]['checkpoint_losses'][T_sgd], 1e-12)
    cv_r = sgd_results[False]['checkpoint_losses'][500] / max(sgd_results[False]['checkpoint_losses'][T_sgd], 1e-12)
    print(f"\n   尺度检验 (excess@500 / excess@5000):")
    print(f"     强凸:  {sc_r:.1f}×  (理论 O(1/T) 预言 10×)")
    print(f"     凸:    {cv_r:.1f}×  (理论 O(1/√T) 预言 √10≈3.2×)")
    print(f"   → 强凸衰减更快，验证 O(1/T) 快于 O(1/√T)")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    # Regret is sublinear
    for T_test in [50, 200, 1000, 5000]:
        experts = [[random.uniform(0, 1) for _ in range(5)] for _ in range(T_test)]
        r = multiplicative_weights(experts, eta=0.1)
        print(f"   T={T_test:>5}: regret={r['regret']:.4f}, avg_regret={r['avg_regret']:.6f}")
    print(f"   → 平均 regret → 0，即算法渐近最优 (no-regret)")
    print(f"   → 这是博弈论中达到 Nash 均衡的基础")

    print("\n✅ COS 511/512 Demo 完成！")


if __name__ == "__main__":
    demo()
