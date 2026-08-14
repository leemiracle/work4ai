#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
13_double_descent.py — 双重下降: 过参数化反而泛化更好 (打脸经典奥卡姆)
讲透模型宇宙 / Ch13 实验
纯标准库(numpy可选), 几秒跑完。
用 Legendre 正交多项式基保证高阶数值稳定, 真正复现 double descent。
复现 Belkin et al. 2019 的定性现象。
"""
import math, random
random.seed(11)

try:
    import numpy as np
    from numpy.polynomial.legendre import legvander
    HAS_NP = True
except ImportError:
    HAS_NP = False

def main():
    print("=" * 68)
    print("Double Descent: 过参数化反而泛化更好 (Legendre 正交基, 数值稳定)")
    print("=" * 68)
    if not HAS_NP:
        print("(需要 numpy, 请 pip install numpy)"); return

    def true_func(x):
        return math.sin(3.0 * x)

    # 数据: x in [-1,1], 用 Legendre 基天然适配
    N_TRAIN = 15
    NOISE = 0.15
    xs = [random.uniform(-1, 1) for _ in range(N_TRAIN)]
    ys = [true_func(x) + random.gauss(0, NOISE) for x in xs]
    N_TEST = 300
    xt = [random.uniform(-1, 1) for _ in range(N_TEST)]
    yt = [true_func(x) for x in xt]

    xs_a = np.array(xs); ys_a = np.array(ys)
    xt_a = np.array(xt); yt_a = np.array(yt)

    results = []
    for d in range(1, 45):
        A = legvander(xs_a, d - 1)        # (N, d) Legendre 基, 数值稳定
        w = np.linalg.pinv(A) @ ys_a      # 最小范数解
        err_tr = np.mean((A @ w - ys_a) ** 2)
        At = legvander(xt_a, d - 1)
        err_te = np.mean((At @ w - yt_a) ** 2)
        results.append((d, err_tr, err_te))

    # 分析: 临界峰值 (test err 最大), 过参数化区最低
    peak = max(results, key=lambda r: r[2])
    over = [r for r in results if r[0] > N_TRAIN]
    best_over = min(over, key=lambda r: r[2])

    print(f"\n数据: {N_TRAIN} 训练点 / {N_TEST} 测试点, 真函数 sin(3x)+噪声{NOISE}")
    print(f"\n{'阶数':>4} {'train MSE':>12} {'test MSE':>12}  备注")
    print("-" * 60)
    for d, etr, ete in results:
        if d in (1,2,4,6,8,10,12,14,15,16,18,20,25,30,35,40,44) or d==peak[0] or (best_over and d==best_over[0]):
            note = ""
            if d == N_TRAIN: note = " <- 阶数=数据点数(插值临界)"
            if d == peak[0]: note = " <- test err 峰值(最差!)"
            if best_over and d == best_over[0]: note = " <- 过参数化后最低(回升)"
            print(f"{d:>4} {etr:>12.5f} {ete:>12.5f}{note}")

    print("\n" + "=" * 68)
    print(">>> 反直觉发现: Double Descent <<<")
    print(f"  阶数<{N_TRAIN}: 欠拟合→刚好, test err 先降 (经典U的左半)")
    print(f"  临界峰值: 阶数={peak[0]}, test MSE={peak[2]:.4f} (最差! 不是最复杂)")
    print(f"  阶数>{N_TRAIN}(过参数化): test err 反而降, 最低在阶数={best_over[0]} (MSE={best_over[2]:.4f})")
    print(f"  => 最差模型是'刚好能插值训练集'的, 不是最复杂的。")
    print(f"  => 过了临界点, 复杂度增加反而泛化更好 = double descent。")
    print(f"  => 现代 LLM 活在过参数化区, 这就是它们不过拟合的原因。")
    print(f"  => 奥卡姆剃刀需修正: 在所有插值解里, 最小范数(SGD隐式偏好)最平滑≈最简单。")
    print("=" * 68)

if __name__ == "__main__":
    main()
