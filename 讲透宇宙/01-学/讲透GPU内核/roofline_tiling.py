#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roofline 计算 + tiling 重用模拟（教学用，纯 NumPy）。

两个实验：
  1) roofline(model, bytes)：算算术强度并判 compute/memory bound
  2) tiling_reuse(L, tile)：模拟带容量上限的理想缓存下，naive vs tiled matmul
     的内存访问次数——验证"分块把每元素读 L/tile 次"的重用数学。
真实跑法：python3 roofline_tiling.py
"""
import numpy as np

# ---- 实验 1：roofline ----
GPUS = {  # (peak TFLOPS FP16/BF16, HBM GB/s)
    'A100': (312, 2039),
    'H100': (990, 3350),
    'B200': (2250, 8000),
}

def roofline(name, flops, moved_bytes, verbose=True):
    peak_t, peak_bw = GPUS[name]
    ai = flops / moved_bytes                      # FLOP/B
    ridge = peak_t * 1e12 / (peak_bw * 1e9)       # 平衡点 FLOP/B
    bw_bound_t = moved_bytes / (peak_bw * 1e9)    # 按带宽跑完的时间
    co_bound_t = flops / (peak_t * 1e12)          # 按算力跑完的时间
    bound = 'compute' if ai >= ridge else 'memory'
    t = max(bw_bound_t, co_bound_t)
    if verbose:
        print(f'[{name}] 强度 {ai:.1f} FLOP/B vs 屋脊 {ridge:.0f} → {bound}-bound, '
              f'T≥{t*1e3:.2f} ms (算力口 {co_bound_t*1e3:.2f} / 带宽口 {bw_bound_t*1e3:.2f})')
    return bound, t

# ---- 实验 2：tiling 重用 ----
def access_counts(L, tile, cache_elems):
    """返回 (naive_reads, tiled_reads)：A[L,L]×B[L,L] 每元素乘加一次所需的内存读次数（理想缓存模型）。"""
    # naive 三重循环 A[i,k],B[k,j]：无重用假设 = 每次乘加读 2 个标量 → L^3 * 2 次
    naive = 2 * L ** 3
    # tiled：C 子块 tile×tile 计算需要 A 行块(tile×L) 与 B 列块(L×tile) 各 tile 次
    # 理想缓存容量 >= 2*tile*L 时，A 行块/B 列块读入后被重用 tile 次：
    # 每 (i,j) 块对读 (tile*L + L*tile) 字段，共 (L/tile)^2 块对
    if cache_elems < 2 * tile * L:
        raise ValueError('缓存容量不足以驻留行块+列块，模拟不成立')
    blocks = (L // tile) ** 2
    tiled = blocks * 2 * tile * L
    return naive, tiled

def main():
    print('== 实验 1：roofline（7B 模型单 token decode vs 4K prefill，FP16）==')
    P = 7e9; two = 2
    roofline('A100', flops=two*P, moved_bytes=two*P)              # decode：读全部权重
    s, d, L = 4096, 4096, 32
    act_bytes = 4 * s * d * L * 2       # 激活读写：每层 ~4×s×d 标量×2B
    roofline('A100', flops=two*P*s, moved_bytes=two*P + act_bytes)  # prefill：权重一遍+激活流
    roofline('H100', flops=two*P, moved_bytes=two*P)
    print()
    print('== 实验 2：tiling 重用（L=1024 矩阵，cache=4M 元素）==')
    L = 1024
    for tile in (32, 64, 128, 256):
        naive, tiled = access_counts(L, tile, cache_elems=4_000_000)
        # 数值正确性抽验（小矩阵真算）
        rng = np.random.default_rng(0)
        A = rng.standard_normal((256, 256)); B = rng.standard_normal((256, 256))
        C_ref = A @ B
        t2 = tile if tile <= 256 else 256
        C = np.zeros_like(C_ref)
        for i in range(0, 256, t2):
            for j in range(0, 256, t2):
                for k in range(0, 256, t2):
                    C[i:i+t2, j:j+t2] += A[i:i+t2, k:k+t2] @ B[k:k+t2, j:j+t2]
        assert np.allclose(C, C_ref), 'tiling 数值不等价!'
        print(f'tile={tile:>3}: naive 读 {naive/1e9:.2f}G 次 vs tiled {tiled/1e9:.2f}G 次 '
              f'→ 访存降为 1/{naive/tiled:.0f}（理论 1/{tile}）')

if __name__ == '__main__':
    main()
