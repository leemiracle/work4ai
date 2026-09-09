#!/usr/bin/env python3
"""
课题 PR-5 实验：排队论分析 LLM Serving (M/G/1)
跑法：python3 03_queueing_llm_serving.py
依赖：numpy only
"""
import numpy as np

def mg1_mean_wait(lam, E_S, sigma_S):
    rho = lam * E_S
    E_S2 = E_S**2 + sigma_S**2
    return lam * E_S2 / (2 * (1 - rho))

def simulate_mg1(lam, E_S, sigma_S, n_reqs=20000):
    inter = np.random.exponential(1/lam, n_reqs)
    arrivals = np.cumsum(inter)
    service = np.maximum(np.random.normal(E_S, sigma_S, n_reqs), 0.001)
    starts = np.zeros(n_reqs)
    for i in range(1, n_reqs):
        starts[i] = max(starts[i-1] + service[i-1], arrivals[i])
    waits = starts - arrivals
    return np.mean(waits), np.percentile(waits, 99)

def run_experiment():
    np.random.seed(42)
    lam, E_S = 20, 0.04
    print(f"M/G/1: λ={lam}, E[S]={E_S}, ρ={lam*E_S:.2f}")
    print(f"{'σ_S':>6s}  {'理论W_q':>10s}  {'模拟W_q':>10s}  {'P99':>10s}")
    for sigma in [0.01, 0.02, 0.05, 0.06, 0.08, 0.10]:
        wt = mg1_mean_wait(lam, E_S, sigma)
        ws, p99 = simulate_mg1(lam, E_S, sigma)
        print(f"{sigma:>6.2f}  {wt:>10.4f}  {ws:>10.4f}  {p99:>10.4f}")
    print(f"\nM/M/1 是 M/D/1 的 {mg1_mean_wait(lam,E_S,E_S)/mg1_mean_wait(lam,E_S,0):.1f}×")

if __name__ == "__main__":
    run_experiment()
