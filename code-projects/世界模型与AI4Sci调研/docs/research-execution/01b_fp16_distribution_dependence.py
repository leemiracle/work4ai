#!/usr/bin/env python3
"""
课题 NA-1 第二步实验：FP16 误差 scaling vs 输入分布
跑法：python3 01b_fp16_distribution_dependence.py
依赖：numpy only
"""
import numpy as np

u16 = 2**(-11)

def run_experiment():
    np.random.seed(42)
    ns = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    n_trials = 50
    scale = 0.1
    distributions = {
        "正态 N(0,1)":    lambda n: np.random.randn(n) * scale,
        "均匀 U(-√3,√3)": lambda n: (np.random.rand(n)*2-1) * np.sqrt(3) * scale,
        "拉普拉斯":        lambda n: np.random.laplace(0, 1, n) * scale,
        "双峰 ±1":        lambda n: np.random.choice([-scale, scale], n),
    }
    print(f"{'分布':>16s}  {'α':>8s}  {'≈√n?':>6s}")
    print("-" * 40)
    for name, gen in distributions.items():
        all_errs = []
        for n in ns:
            errs = []
            for _ in range(n_trials):
                a = gen(n)
                exact = np.float64(a).sum()
                acc = np.float16(0)
                for x in a:
                    acc = np.float16(acc + np.float16(x))
                errs.append(abs(float(acc)-exact)/abs(exact) if abs(exact)>1e-20 else 0)
            all_errs.append(np.mean(errs))
        valid = [(np.log(n), np.log(max(e,1e-20))) for n,e in zip(ns,all_errs) if e>1e-15]
        alpha = np.polyfit([v[0] for v in valid], [v[1] for v in valid], 1)[0] if len(valid)>=3 else float('nan')
        is_sqrt = "✓" if abs(alpha-0.5)<0.15 else "✗"
        print(f"{name:>16s}  {alpha:>8.3f}  {is_sqrt:>6s}")

if __name__ == "__main__":
    run_experiment()
