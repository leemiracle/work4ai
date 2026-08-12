"""
10-708 Probabilistic Graphical Models (CMU)
================================================
覆盖主题（对应 lecture）：
- Exact inference: Variable Elimination (VE)
- HMM: Forward-Backward + Viterbi decoding
- Sequential Monte Carlo: Bootstrap Particle Filter
- MCMC: Gibbs sampling on 2D Ising model

核心教材/论文：
- "Koller & Friedman 2009 Probabilistic Graphical Models" MIT Press
- "Pearl 1988 Probabilistic Reasoning in Intelligent Systems"
- "Rabiner 1989 IEEE Proc" — HMM tutorial (forward-backward/Viterbi)
- "Gordon Salmond Smith 1993 IEE Proc F" — bootstrap particle filter

本文件实现：
- Variable elimination on discrete Bayes net
- HMM forward-backward + Viterbi
- Bootstrap particle filter
- Gibbs sampling on 2D Ising lattice

运行：
    python3 pgm.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict

# ============ 1. Variable Elimination ============

class Factor:
    """Discrete factor: variables → table."""
    def __init__(self, variables: list[str], table: dict):
        self.variables = variables  # list of variable names
        self.table = table          # key=tuple of values → prob

    def sum_out(self, var: str) -> 'Factor':
        if var not in self.variables:
            return self
        idx = self.variables.index(var)
        new_vars = [v for v in self.variables if v != var]
        new_table = defaultdict(float)
        for key, prob in self.table.items():
            new_key = tuple(k for i, k in enumerate(key) if i != idx)
            new_table[new_key] += prob
        return Factor(new_vars, dict(new_table))


def variable_elimination(factors: list[Factor], query: str,
                          evidence: dict = None) -> dict:
    """VE inference. Returns P(query | evidence)."""
    evidence = evidence or {}
    # Apply evidence
    reduced = []
    for f in factors:
        rf = f
        for var, val in evidence.items():
            if var in rf.variables:
                idx = rf.variables.index(var)
                # keep only rows matching the evidence value
                rf.table = {k: v for k, v in rf.table.items()
                            if isinstance(k, tuple) and len(k) > idx and k[idx] == val}
                # project out (marginalize) the evidence variable from the factor
                new_vars = [v for v in rf.variables if v != var]
                new_table = {}
                for k, prob in rf.table.items():
                    new_key = tuple(x for i, x in enumerate(k) if i != idx)
                    new_table[new_key] = prob
                rf = Factor(new_vars, new_table)
        reduced.append(rf)

    # Eliminate non-query, non-evidence variables
    all_vars = set()
    for f in reduced:
        all_vars.update(f.variables)
    hidden = all_vars - {query} - set(evidence.keys())

    for var in hidden:
        # multiply all factors with this var
        relevant = [f for f in reduced if var in f.variables]
        others = [f for f in reduced if var not in f.variables]
        if relevant:
            product = relevant[0]
            for f in relevant[1:]:
                product = _simple_multiply(product, f)
            summed = product.sum_out(var)
            others.append(summed)
        reduced = others

    # Multiply remaining and normalize
    result = reduced[0]
    for f in reduced[1:]:
        result = _simple_multiply(result, f)

    # normalize
    total = sum(result.table.values())
    return {k: v/total for k, v in result.table.items()} if total > 0 else {}

def _simple_multiply(f1: Factor, f2: Factor) -> Factor:
    """Multiply two factors with shared variables."""
    new_vars = list(f1.variables)
    for v in f2.variables:
        if v not in new_vars:
            new_vars.append(v)
    new_table = defaultdict(float)
    for k1, v1 in f1.table.items():
        for k2, v2 in f2.table.items():
            assignment = {}
            for var, val in zip(f1.variables, k1):
                assignment[var] = val
            consistent = True
            for var, val in zip(f2.variables, k2):
                if var in assignment and assignment[var] != val:
                    consistent = False
                    break
                assignment[var] = val
            if consistent:
                new_key = tuple(assignment[v] for v in new_vars)
                new_table[new_key] += v1 * v2
    return Factor(new_vars, dict(new_table))


# ============ 2. HMM Forward-Backward + Viterbi ============

def hmm_forward(observations, A, B, pi):
    """Forward algorithm: P(O) and alpha values."""
    T = len(observations)
    N = len(pi)
    alpha = [[0.0]*N for _ in range(T)]
    # init
    for i in range(N):
        alpha[0][i] = pi[i] * B[i][observations[0]]
    # recurse
    for t in range(1, T):
        for j in range(N):
            alpha[t][j] = sum(alpha[t-1][i]*A[i][j] for i in range(N)) * B[j][observations[t]]
    return alpha

def hmm_backward(observations, A, B):
    """Backward algorithm."""
    T = len(observations)
    N = len(A)
    beta = [[0.0]*N for _ in range(T)]
    for i in range(N):
        beta[T-1][i] = 1.0
    for t in range(T-2, -1, -1):
        for i in range(N):
            beta[t][i] = sum(A[i][j]*B[j][observations[t+1]]*beta[t+1][j] for j in range(N))
    return beta

def hmm_viterbi(observations, A, B, pi):
    """Viterbi: most likely state sequence."""
    T = len(observations)
    N = len(pi)
    delta = [[0.0]*N for _ in range(T)]
    psi = [[0]*N for _ in range(T)]
    for i in range(N):
        delta[0][i] = pi[i] * B[i][observations[0]]
    for t in range(1, T):
        for j in range(N):
            best_val, best_state = 0, 0
            for i in range(N):
                val = delta[t-1][i] * A[i][j]
                if val > best_val:
                    best_val, best_state = val, i
            delta[t][j] = best_val * B[j][observations[t]]
            psi[t][j] = best_state
    # backtrack
    states = [0]*T
    states[T-1] = max(range(N), key=lambda i: delta[T-1][i])
    for t in range(T-2, -1, -1):
        states[t] = psi[t+1][states[t+1]]
    return states


# ============ 3. Bootstrap Particle Filter ============

def particle_filter(observations, n_particles=200, transition_std=0.5):
    """Track a 1D random walk with particle filter."""
    particles = [random.gauss(0, 1) for _ in range(n_particles)]
    estimates = []
    for obs in observations:
        # predict (transition)
        particles = [p + random.gauss(0, transition_std) for p in particles]
        # weight (observation likelihood: obs = state + noise)
        weights = [math.exp(-(p - obs)**2 / (2 * 0.09)) for p in particles]
        total = sum(weights)
        weights = [w/total for w in weights]
        # resample
        cum = []
        s = 0
        for w in weights:
            s += w
            cum.append(s)
        new_particles = []
        for _ in range(n_particles):
            r = random.random()
            idx = 0
            while idx < len(cum)-1 and cum[idx] < r:
                idx += 1
            new_particles.append(particles[idx])
        particles = new_particles
        estimates.append(sum(particles)/n_particles)
    return estimates


# ============ 4. Gibbs Sampling on 2D Ising Model ============

def ising_gibbs(width=8, height=8, beta=0.4, n_sweeps=200):
    """Gibbs sampling on 2D Ising model. beta = coupling strength."""
    grid = [[random.choice([-1, 1]) for _ in range(width)] for _ in range(height)]
    magnetizations = []
    for sweep in range(n_sweeps):
        for r in range(height):
            for c in range(width):
                # local field from neighbors
                neighbors = 0
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < height and 0 <= nc < width:
                        neighbors += grid[nr][nc]
                # P(s=+1) = sigmoid(2*beta*neighbors)
                p_pos = 1.0 / (1.0 + math.exp(-2*beta*neighbors))
                grid[r][c] = 1 if random.random() < p_pos else -1
        mag = sum(sum(row) for row in grid) / (width*height)
        magnetizations.append(mag)
    return grid, magnetizations


# ============ Demo ============

def demo():
    print("=" * 60)
    print("10-708 PGM: VE, HMM, Particle Filter, Ising Gibbs")
    print("=" * 60)
    random.seed(42)

    # --- 1. Variable Elimination (sprinkler network) ---
    print("\n📋 1. Variable Elimination — Sprinkler Network")
    # P(Rain=T | WetGrass=T)
    f_rain = Factor(['R'], {(True,): 0.2, (False,): 0.8})
    f_sprinkler = Factor(['S','R'], {
        (True,True):0.01,(True,False):0.4,(False,True):0.99,(False,False):0.6})
    f_wet = Factor(['W','S','R'], {
        (True,True,True):0.99,(True,True,False):0.9,(True,False,True):0.8,(True,False,False):0.0,
        (False,True,True):0.01,(False,True,False):0.1,(False,False,True):0.2,(False,False,False):1.0})
    result = variable_elimination([f_rain, f_sprinkler, f_wet], 'R', evidence={'W':True})
    if result:
        p_rain = result.get((True,), 0)
        print(f"   P(Rain=T | WetGrass=T) = {p_rain:.4f}")
        print(f"   Prior P(Rain=T) = 0.2 → posterior = {p_rain:.4f}")
        print(f"   💡 观察到湿草地后，下雨概率从 20% 升至 {p_rain:.0%}")

    # --- 2. HMM ---
    print("\n📋 2. HMM Forward-Backward + Viterbi")
    # Weather HMM: 0=Sunny, 1=Rainy; obs: 0=umbrella, 1=no umbrella
    A = [[0.7, 0.3], [0.4, 0.6]]  # transition
    B = [[0.1, 0.9], [0.8, 0.2]]  # emission (umbrella given weather)
    pi = [0.6, 0.4]
    obs = [0, 0, 1, 0, 0]  # umbrella, umbrella, no, umbrella, umbrella
    alpha = hmm_forward(obs, A, B, pi)
    p_obs = sum(alpha[-1])
    states = hmm_viterbi(obs, A, B, pi)
    weather = ['Sunny','Rainy']
    print(f"   Observations: {[('umbrella','no')[o] for o in obs]}")
    print(f"   Viterbi best path: {[weather[s] for s in states]}")
    print(f"   P(observations) = {p_obs:.5f}")

    # --- 3. Particle Filter ---
    print("\n📋 3. Bootstrap Particle Filter")
    true_states = [0.0]
    for _ in range(20):
        true_states.append(true_states[-1] + random.gauss(0, 0.5))
    observations = [s + random.gauss(0, 0.3) for s in true_states]
    estimates = particle_filter(observations, n_particles=100)
    rmse = math.sqrt(sum((e-t)**2 for e,t in zip(estimates, true_states))/len(estimates))
    obs_rmse = math.sqrt(sum((o-t)**2 for o,t in zip(observations, true_states))/len(observations))
    print(f"   20-step tracking: PF RMSE = {rmse:.3f}")
    print(f"   Raw observation RMSE = {obs_rmse:.3f}")
    print(f"   💡 粒子滤波 RMSE {rmse/obs_rmse:.2f}x 观测噪声 → 平滑效果")

    # --- 4. Ising Model ---
    print("\n📋 4. Gibbs Sampling — 2D Ising Model")
    grid_lo, mag_lo = ising_gibbs(beta=0.2, n_sweeps=100)
    grid_hi, mag_hi = ising_gibbs(beta=0.8, n_sweeps=100)
    print(f"   β=0.2 (weak coupling): |magnetization| = {abs(mag_lo[-1]):.3f}")
    print(f"   β=0.8 (strong coupling): |magnetization| = {abs(mag_hi[-1]):.3f}")
    print(f"   💡 强耦合 → 自发磁化（相变！2D Ising 临界 β_c ≈ 0.44）")

    print("\n✅ 10-708 PGM 完成！")
    print("   覆盖：Variable Elimination / HMM FB+Viterbi / Particle Filter / Ising Gibbs")


if __name__ == "__main__":
    demo()
