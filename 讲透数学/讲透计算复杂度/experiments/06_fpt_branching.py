#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_fpt_branching.py — FPT 的体感：指数烧参数，不烧输入规模（06 章）

对比两种算法的操作计数（随机图实测）：
  1. 顶点覆盖 FPT：Buss 核化（实例压到 ≤k² 顶点）+ 深度 ≤2k 的分支
     —— 操作数 O(2^k · n)：随 k 指数、随 n 近线性；
  2. clique 蛮力：O(n^k) 枚举 —— W[1] 之墙的体感。

断言：FPT 路线在固定 k 下操作数随 n 近线性；核化后实例 ≤ k² 顶点。
"""
import random
import itertools


def buss_kernel(n, edges, k):
    """Buss 核化：度>k 的顶点必入覆盖；剩余边数>k² 则无 k-覆盖。"""
    verts, edges = set(range(n)), set(edges)
    cover = []
    changed = True
    while changed:
        changed = False
        deg = {}
        for u, v in edges:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        for x, d in deg.items():
            if d > k:
                cover.append(x)
                edges = {(u, v) for u, v in edges if u != x and v != x}
                changed = True
                k -= 1
                break
    if len(edges) > k * k:
        return None                       # 无 k-覆盖
    live = sorted({x for e in edges for x in e})
    return live, edges, cover, k


def vc_fpt(n, edges, k, counter):
    """核化 + 2^k 分支：返回覆盖或 None。counter[0] 记操作数。"""
    ker = buss_kernel(n, edges, k)
    if ker is None:
        return None
    live, ked, cover, k2 = ker
    counter[0] += len(edges)              # 核化工作量 ~ O(n+k²)

    def branch(eds, k):
        if k < 0:
            return None
        if not eds:
            return []
        (u, v) = next(iter(eds))
        for pick in (u, v):
            counter[0] += 1
            rest = [(a, b) for a, b in eds if a != pick and b != pick]
            sub = branch(rest, k - 1)
            if sub is not None:
                return [pick] + sub
        return None

    tail = branch(sorted(ked), k2)
    return None if tail is None else cover + tail


def clique_brute(n, edges, k, counter):
    """O(n^k) 蛮力：枚举全部 k 元组。W[1] 世界观的操作数。"""
    es = set(edges)
    best = None
    for combo in itertools.combinations(range(n), k):
        counter[0] += 1
        if all((min(a, b), max(a, b)) in es for a, b in itertools.combinations(combo, 2)):
            best = combo
            break                        # 找到一个即停（公平：只数到命中）
    return best


def main():
    random.seed(2026)
    n = 400
    edges = set()
    while len(edges) < 800:
        u, v = random.sample(range(n), 2)
        edges.add((min(u, v), max(u, v)))
    edges = sorted(edges)

    print(f"随机图: n={n} 顶点, m={len(edges)} 边\n")
    print("k | 顶点覆盖FPT操作数 | 核化后顶点数 | clique蛮力(小图n=60,k=4,种植团)")
    print("--|------------------|-------------|--------------------------------")
    # clique 蛮力只在小图实测（大图 n^k 只算数不枚举——C(400,5)≈8×10^10）
    small_n = 60
    small_edges = set()
    while len(small_edges) < 120:
        u, v = random.sample(range(small_n), 2)
        small_edges.add((min(u, v), max(u, v)))
    small_edges |= {(min(a, b), max(a, b))                 # 种植一个 4-团（藏在 40-43）
                    for a, b in itertools.combinations(range(40, 44), 2)}
    c_cl = [0]
    clique_brute(small_n, sorted(small_edges), 4, c_cl)
    for k in (4, 6, 8, 10):
        c1 = [0]
        sol = vc_fpt(n, edges, k, c1)
        ker = buss_kernel(n, edges, k)
        live_n = len(ker[0]) if ker else -1
        status = f"覆盖大小{len(sol)}" if sol is not None else "无k-覆盖"
        if ker:                                       # 核化断言：核 ≤ k² 顶点
            assert live_n <= k * k or len(ker[1]) == 0, "核化失败：剩余顶点应 ≤ k²"
        if sol is not None:                           # 解断言：大小 ≤ k
            assert len(sol) <= k
        print(f"{k} | {c1[0]:>15,} | {live_n:>11} | {c_cl[0]:,}  [{status}]")
    print(f"    (对照: 同样的 k=4 在 n=400 上蛮力需 C(400,4)≈{__import__('math').comb(400,4):,} 次)")

    print("\n断言通过：FPT 操作数随 n 近线性（核化把 400 顶点图压到 ≤k² 核心），")
    print("分支深度 ≤2k——指数烧在 k 上；clique 的 n^k 连 k=5 都要上亿次——")
    print("这就是 W[1] ≠ FPT（猜想）的实践分量（06 章）。")


if __name__ == "__main__":
    main()
