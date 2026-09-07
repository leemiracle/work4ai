#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""实验② 判例引用 DAG——环检测与权威深度(GB/T 82030 程序法屉)

演示 04 章走廊⑤:
  1) 判例引用关系必须是 DAG——引用环在时间上不可能
     (判决只能引用已存在的先例; "A 引 B 且 B 引 A"= 至少一份判决
      引用了还不存在的东西)
  2) Kahn 拓扑排序做环检测: 出队总数 < 节点数 ⇒ 有环
  3) 权威深度 = 判例上游最长引用链, 作为判例权重的可计算代理

案例全部为抽象编号, 不指涉任何真实判例。纯标准库, assert 自验证, exit 0。
"""

from collections import defaultdict, deque


def build_adj(edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)  # 权威自上游流向下游
    return adj


def kahn_order(nodes, edges):
    """Kahn 拓扑排序。edges: (上游, 下游) 引用边。返回 (拓扑序, 是否有环)。"""
    adj = build_adj(edges)
    indeg = {n: 0 for n in nodes}
    for _, v in edges:
        indeg[v] += 1
    q = deque(sorted(n for n in nodes if indeg[n] == 0))  # sorted: 稳定输出
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for m in sorted(adj[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    return order, len(order) == len(nodes)


def find_cycle(nodes, edges):
    """DFS 三色标记定位一个具体环。无环返回 None。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    parent = {}
    adj = build_adj(edges)

    for root in sorted(nodes):
        if color[root] != WHITE:
            continue
        stack = [(root, iter(sorted(adj[root])))]
        color[root] = GRAY
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = BLACK
                stack.pop()
            elif color[nxt] == WHITE:
                parent[nxt] = node
                color[nxt] = GRAY
                stack.append((nxt, iter(sorted(adj[nxt]))))
            elif color[nxt] == GRAY:  # 回边: node -> nxt 构成环
                path, cur = [node], node
                while cur != nxt:
                    cur = parent[cur]
                    path.append(cur)
                return list(reversed(path)) + [nxt]
    return None


def authority_depth(nodes, edges):
    """每个判例的上游最长链(DAG 上最长路径, 按拓扑序 DP)。"""
    order, acyclic = kahn_order(nodes, edges)
    assert acyclic, "有环图无权威深度——先做环检测"
    adj = build_adj(edges)
    depth = {n: 0 for n in nodes}
    for u in order:  # 上游先算
        for v in adj[u]:
            depth[v] = max(depth[v], depth[u] + 1)
    return depth


def main():
    # 抽象判例语料: 仿先例体系的常见形状(奠基判例被反复引用)
    nodes = [f"C{i}" for i in range(1, 8)]
    edges = [
        ("C1", "C3"), ("C2", "C3"),           # C3 同时引用 C1/C2
        ("C3", "C4"), ("C3", "C5"),           # 中枢判例分叉
        ("C4", "C6"), ("C5", "C6"),           # 汇流
        ("C6", "C7"),
    ]
    order, acyclic = kahn_order(nodes, edges)
    assert acyclic, "正常语料不应有环"
    assert order[:2] == ["C1", "C2"], "无前置的判例应最先出队"
    print(f"[OK] 环检测: 语料无环, 拓扑序 {order}")

    d = authority_depth(nodes, edges)
    assert d["C1"] == 0 and d["C3"] == 1 and d["C4"] == 2 and d["C6"] == 3 and d["C7"] == 4
    hub = max(d, key=d.get)
    assert hub == "C7"
    print(f"[OK] 权威深度: {d}")
    print(f"[OK] 最深上游链: {hub} (深度 {d[hub]}) —— 可计算的'判例权重'代理")

    # 环检测: 构造一条"时间不可能"的引用(A 引 B, B 引 A)
    bad_nodes = ["X", "Y"]
    bad_edges = [("X", "Y"), ("Y", "X")]
    order2, acyclic2 = kahn_order(bad_nodes, bad_edges)
    assert not acyclic2, "引用环必须被检出"
    cycle = find_cycle(bad_nodes, bad_edges)
    assert cycle[0] == cycle[-1] and len(cycle) == 3
    print(f"[OK] 引用环被检出: {' -> '.join(cycle)} (至少一份判决引用了尚不存在的东西)")

    # 三节点旋转环(抽象): X→Y→Z→X
    order3, acyclic3 = kahn_order(["X", "Y", "Z"],
                                  [("X", "Y"), ("Y", "Z"), ("Z", "X")])
    assert not acyclic3 and len(order3) == 0
    print("[OK] 三节点旋转环同样被检出(拓扑序为空)")

    # 不变量: 对无环语料, 每条边 (u,v) 满足 depth[v] >= depth[u]+1
    for u, v in edges:
        assert d[v] >= d[u] + 1, (u, v)
    print("[OK] 不变量: 每条引用边使下游深度至少 +1")

    print("\n注意: 图只回答'引用结构'——某判例是否约束本案是解释问题(04 章档二)。")
    print("全部 assert 通过, exit 0")


if __name__ == "__main__":
    main()
