#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ring AllReduce 最小可运行模拟器（教学用）。

模拟 N 个 rank 组成单向环执行 allreduce（reduce-scatter + all-gather 两阶段），
验证数值正确性并统计通信量，与朴素 allreduce（全归 rank0 再广播）对照。
真实跑法：python3 ring_sim.py [N] [L]
"""
import sys
import numpy as np


def ring_allreduce(vectors, log=False):
    """vectors: list[np.ndarray]，每个元素是一张卡上的长度 L 向量（L 可被 N 整除）。

    环算法（每步每 rank 只发给下一个 rank 一块）：
      阶段一 reduce-scatter（N-1 步）：第 i 步 rank r 发送块 (r - i) % N，
        接收块 (r - i - 1) % N 并累加；结束后块 r 已是全体和在 rank r 上的分片。
      阶段二 all-gather（N-1 步）：把各 rank 手中的和分片沿环传一圈。
    """
    n = len(vectors)
    L = len(vectors[0])
    per = L // n
    blocks = [v.reshape(n, per).copy() for v in vectors]  # blocks[r][k] = rank r 手中第 k 块
    sent = [0] * n
    steps = []
    # 阶段一：reduce-scatter
    for i in range(n - 1):
        send_idx = [((r - i) % n) for r in range(n)]
        incoming = [None] * n
        for r in range(n):
            blk = send_idx[r]
            sent[r] += blocks[r][blk].nbytes
            incoming[(r + 1) % n] = (blk, blocks[r][blk].copy())
        for r in range(n):
            if incoming[r] is not None:
                blk, data = incoming[r]
                blocks[r][blk] += data
        steps.append(('rs', i))
    # 阶段二：all-gather
    for i in range(n):
        pass
    for i in range(n - 1):
        send_idx = [((r - i + 1) % n) for r in range(n)]
        incoming = [None] * n
        for r in range(n):
            blk = send_idx[r]
            sent[r] += blocks[r][blk].nbytes
            incoming[(r + 1) % n] = (blk, blocks[r][blk].copy())
        for r in range(n):
            if incoming[r] is not None:
                blk, data = incoming[r]
                blocks[r][blk] = data
        steps.append(('ag', i))
    result = [blocks[r].reshape(L) for r in range(n)]
    return result, sent, steps


def naive_allreduce(chunks_per_rank):
    """朴素法：全部发给 rank0 求和，再由 rank0 广播回去。"""
    n = len(chunks_per_rank)
    sent = [0] * n
    total = np.zeros_like(chunks_per_rank[0])
    for r in range(n):
        total += chunks_per_rank[r]
        sent[r] += chunks_per_rank[r].nbytes  # 发给 rank0
    sent[0] += total.nbytes * (n - 1)  # rank0 广播给其余 n-1 个
    return [total.copy() for _ in range(n)], sent


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    L = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
    rng = np.random.default_rng(42)
    per = L // n
    chunks = [rng.standard_normal(per) for _ in range(n)]
    expected = np.concatenate(chunks).sum()  # 标量对照

    ring_res, ring_sent, steps = ring_allreduce(chunks)
    naive_res, naive_sent = naive_allreduce(chunks)

    # 断言 1：数值正确性（每个 rank 都拿到全体和）
    for r in range(n):
        assert np.allclose(ring_res[r], naive_res[0]), f'rank {r} 数值不等价!'
    assert np.isclose(ring_res[0].sum(), expected)
    # 断言 2：环法每 rank 通信量 = 2*(N-1)/N * S，S=每卡消息大小（量纲坑：不是全体总和！）
    S = chunks[0].nbytes
    theory = 2 * (n - 1) / n * S
    assert all(abs(s - theory) < 1 for s in ring_sent), (ring_sent, theory)

    print(f'N={n} 卡, 每卡向量 {per} float64 (每卡消息 {S/1e6:.1f} MB)')
    print(f'[环法]   每 rank 发送 {ring_sent[0]/1e6:.2f} MB, 理论 2(N-1)/N*S = {theory/1e6:.2f} MB  ✓')
    print(f'[朴素法] rank0 发送 {naive_sent[0]/1e6:.2f} MB, 其余各 {naive_sent[1]/1e6:.2f} MB')
    print(f'[负载均衡] 环法最忙/最闲 rank = {max(ring_sent)/min(ring_sent):.2f} 倍; '
          f'朴素法 = {max(naive_sent)/min(naive_sent):.1f} 倍')
    print(f'[数值] 全部 {n} rank 与 rank0 求和结果逐元素一致 ✓ (allclose)')
    print(f'[步数] reduce-scatter {n-1} 步 + all-gather {n-1} 步 = {len(steps)} 步')


if __name__ == '__main__':
    main()
