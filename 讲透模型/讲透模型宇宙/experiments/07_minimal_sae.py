#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_minimal_sae.py — 手搓最小稀疏自编码器(SAE), 在superposition数据上恢复特征
讲透模型宇宙 / Ch07 实验
纯标准库(numpy可选), 几秒跑完。
"""
import random
try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

def main():
    print("=" * 66)
    print("最小 SAE: 在 superposition 数据上恢复隐藏特征")
    print("=" * 66)
    if not HAS_NP:
        print("(需要 numpy, 请 pip install numpy)"); return

    rng = np.random.default_rng(7)
    D = 4          # 激活维度 (4维装6个特征 = superposition)
    F_TRUE = 6     # 真实特征数 > 维度数
    F_SAE = 12     # SAE 宽度 (过完备)
    N = 2000       # 样本
    SPARSITY = 2   # 每个样本平均激活的真特征数

    # 1. 造真特征方向 W_true (D x F_TRUE), 单位化
    W_true = rng.standard_normal((D, F_TRUE))
    W_true /= np.linalg.norm(W_true, axis=0, keepdims=True)

    # 2. 造稀疏特征激活, 合成激活 x = W_true @ f  (superposition)
    F_act = np.zeros((F_TRUE, N))
    for j in range(N):
        active = rng.choice(F_TRUE, size=SPARSITY, replace=False)
        F_act[active, j] = rng.uniform(0.5, 2.0, size=SPARSITY)
    X = W_true @ F_act + 0.05 * rng.standard_normal((D, N))   # (D, N)

    # 3. 初始化 SAE 参数
    W_enc = rng.standard_normal((F_SAE, D)) * 0.05
    b_enc = np.zeros(F_SAE)
    W_dec = rng.standard_normal((D, F_SAE)) * 0.05
    W_dec /= np.linalg.norm(W_dec, axis=0, keepdims=True)     # decoder 列单位化
    b_dec = np.zeros(D)
    L1 = 0.03
    lr = 0.015

    # 4. 训练 (SGD + 梯度裁剪)
    Xb = X.T  # (N, D)
    def clip(g):
        n = np.linalg.norm(g)
        return g * (min(1.0, 5.0 / (n + 1e-9)))
    for step in range(1500):
        f = np.maximum(0, Xb @ W_enc.T + b_enc)        # (N, F_SAE)
        x_hat = f @ W_dec.T + b_dec                     # (N, D)
        recon = np.mean((Xb - x_hat) ** 2)
        sparse = np.mean(np.abs(f))
        # 梯度
        dx = -(Xb - x_hat)                              # dL/dx_hat
        gW_dec = dx.T @ f                               # (D, F_SAE)
        gb_dec = dx.sum(0)
        df = dx @ W_dec                                 # (N, F_SAE)
        df[f <= 0] = 0                                  # ReLU 反传
        df += L1 * np.sign(f)                           # L1 梯度
        gW_enc = df.T @ Xb
        gb_enc = df.sum(0)
        gW_dec = clip(gW_dec); gW_enc = clip(gW_enc)
        gb_dec = clip(gb_dec); gb_enc = clip(gb_enc)
        W_enc -= lr * gW_enc; b_enc -= lr * gb_enc
        W_dec -= lr * gW_dec
        W_dec /= np.linalg.norm(W_dec, axis=0, keepdims=True)  # 保持单位
        b_dec -= lr * gb_dec
        if step % 500 == 0 or step == 1499:
            print(f"  step {step:>4}: 重建loss={recon:.4f}  稀疏={sparse:.3f}")

    # 5. 评估: 每个真特征方向, 找 SAE 里最近的方向 (余弦)
    print("\n[恢复分析] 每个真特征 -> SAE最近方向的余弦相似度:")
    recovered = 0
    for i in range(F_TRUE):
        sims = W_dec.T @ W_true[:, i]                   # (F_SAE,)
        best = np.argmax(np.abs(sims))
        c = abs(sims[best])
        ok = "OK" if c > 0.9 else "未恢复"
        if c > 0.9: recovered += 1
        print(f"  真特征{i}: 最近SAE特征#{best:>2}, |余弦|={c:.3f}  {ok}")

    # 6. 死特征统计
    f_final = np.maximum(0, Xb @ W_enc.T + b_enc)
    active_per_feat = (f_final > 1e-4).sum(0)
    dead = (active_per_feat == 0).sum()
    print(f"\n[死特征] SAE 共 {F_SAE} 个特征, 其中 {dead} 个从不激活(死特征)")

    print("\n" + "=" * 66)
    print(">>> 发现 <<<")
    print(f"  真特征 {F_TRUE} 个, SAE 恢复 {recovered} 个 (余弦>0.9)")
    print(f"  死特征 {dead}/{F_SAE}  (大SAE里死特征是常态)")
    print("  => SAE能恢复大部分概念方向(几何重建), 但不完美。")
    print("  => 真实大模型 SAE 需几千万宽度, 还要过'因果验证'(见正文7.4)。")
    print("=" * 66)

if __name__ == "__main__":
    main()
