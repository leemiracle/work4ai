#!/usr/bin/env python3
"""
课题 NA-1 第一步实验：FP16 累加误差的 Scaling Law
跑法：python3 01_fp16_error_scaling.py
依赖：numpy only
"""
import numpy as np

u16 = 2**(-11)
u32 = 2**(-23)

def run_experiment():
    np.random.seed(42)
    ns = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    n_trials = 50
    results = []
    for n in ns:
        errs16, errs_mixed = [], []
        for _ in range(n_trials):
            a = np.random.randn(n) * 0.1
            exact = np.float64(a).sum()
            acc16 = np.float16(0)
            for x in a:
                acc16 = np.float16(acc16 + np.float16(x))
            errs16.append(abs(float(acc16) - exact) / abs(exact))
            acc32 = np.float32(0)
            for x in a:
                acc32 += np.float32(np.float16(x))
            errs_mixed.append(abs(float(acc32) - exact) / abs(exact))
        results.append((n, np.mean(errs16), np.mean(errs_mixed)))
    log_n = np.log([r[0] for r in results])
    a16 = np.polyfit(log_n, np.log([max(r[1],1e-20) for r in results]), 1)[0]
    a_mixed = np.polyfit(log_n, np.log([max(r[2],1e-20) for r in results]), 1)[0]
    print(f"FP16 累加误差 scaling: ε(n) ∝ n^{a16:.3f} (理论最坏 O(n), 随机预测 O(√n))")
    print(f"FP16+FP32 累加:        ε(n) ∝ n^{a_mixed:.3f}")
    print(f"Higham 上界保守: ~{1/(a16):.0f}× 到 100×")
    return a16, a_mixed

if __name__ == "__main__":
    run_experiment()
