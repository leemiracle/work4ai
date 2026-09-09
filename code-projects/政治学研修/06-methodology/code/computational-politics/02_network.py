#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算政治学代码 2：政治网络分析
演示：议员合作网络的度中心性、聚类系数、桥边（把关人）
纯 Python 标准库。运行：python3 02_network.py
"""
from collections import deque

# 议员合作网络（邻接表；边 = 共同提案）
G = {
    'A': ['B', 'C', 'D'],
    'B': ['A', 'C'],
    'C': ['A', 'B', 'E'],
    'D': ['A', 'E'],
    'E': ['C', 'D', 'F'],
    'F': ['E'],
}

def degree_centrality(g):
    n = len(g)
    return {node: len(adj) / (n - 1) for node, adj in g.items()}

def clustering(g, node):
    nbrs = g[node]
    k = len(nbrs)
    if k < 2:
        return 0.0
    links = 0
    for i in range(k):
        for j in range(i + 1, k):
            if nbrs[j] in g[nbrs[i]]:
                links += 1
    return 2 * links / (k * (k - 1))

def is_connected(g):
    nodes = list(g)
    seen, q = {nodes[0]}, deque([nodes[0]])
    while q:
        u = q.popleft()
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(g)

def find_bridges(g):
    bridges = []
    for u in g:
        for v in list(g[u]):
            g[u].remove(v)
            g[v].remove(u)
            if not is_connected(g):
                bridges.append(tuple(sorted((u, v))))
            g[u].append(v)
            g[v].append(u)
    return sorted(set(bridges))

print("=" * 55)
print("1. 度中心性（连接最多 = 最有影响力）")
print("=" * 55)
dc = degree_centrality(G)
for n, c in sorted(dc.items(), key=lambda x: -x[1]):
    print(f"  议员 {n}: 度中心性 = {c:.3f}")
print("  → A、C、E 连接最多，是网络枢纽\n")

print("=" * 55)
print("2. 聚类系数（我的朋友互相认识？= 圈子紧密程度）")
print("=" * 55)
for n in G:
    print(f"  议员 {n}: 聚类系数 = {clustering(G, n):.3f}")
print("  → B 圈子最紧；F 最松（仅连 E）\n")

print("=" * 55)
print("3. 桥边（删后网络分裂 = 关键连接/把关人）")
print("=" * 55)
print(f"  桥边: {find_bridges(G)}")
print("  → E-F 是桥：F 仅靠它连入主网，E 是把关人（gatekeeper）")
