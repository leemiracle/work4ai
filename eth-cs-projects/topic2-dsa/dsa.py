"""
Algorithmen und Datenstrukturen (AlgoDat) — ETH Zürich
======================================================
覆盖主题：
- 排序网络（Batcher）
- 红黑树（插入 + 删除修复）
- 布谷鸟哈希（Cuckoo Hashing）
- 图算法（DFS / BFS / MST-Kruskal / Dijkstra）

核心教材：
- Cormen, Leiserson, Rivest, Stein "Introduction to Algorithms" 3rd ed. (MIT Press, 2009) Ch. 13 (RB Tree), Ch. 11 (Hashing), Ch. 23 (MST)
- Pagh & Rodler "Cuckoo Hashing" J. Algorithms 51(2): 122-144 (2004)
- Bayer "Symmetric Binary B-Trees" (红黑树原始论文) Acta Informatica 1(4): 290-306 (1972)

本文件实现：
1. 红黑树（插入 + 修复 + 验证性质）
2. 布谷鸟哈希（双表 + 踢出）
3. Kruskal MST + 并查集
4. DFS / BFS 追踪

运行：
    python dsa.py
"""
from __future__ import annotations
import random


# ============ 1. 红黑树 ============

RED = 'R'
BLACK = 'B'


class RBNode:
    __slots__ = ('key', 'color', 'left', 'right', 'parent')

    def __init__(self, key, color=RED):
        self.key = key
        self.color = color
        self.left: RBNode | None = None
        self.right: RBNode | None = None
        self.parent: RBNode | None = None


class RBTree:
    """
    红黑树五性质：
    1. 每个节点红或黑
    2. 根黑
    3. 叶子(NIL)黑
    4. 红节点的子节点必黑（无连续红）
    5. 任一节点到后代叶子的所有路径含相同数量黑节点（黑高）
    → 高度 ≤ 2·log(n+1)
    """

    def __init__(self):
        self.root: RBNode | None = None

    def insert(self, key):
        node = RBNode(key)
        # 标准 BST 插入
        parent = None
        cur = self.root
        while cur:
            parent = cur
            cur = cur.left if key < cur.key else cur.right
        node.parent = parent
        if parent is None:
            self.root = node
        elif key < parent.key:
            parent.left = node
        else:
            parent.right = node
        node.color = RED
        self._insert_fixup(node)

    def _insert_fixup(self, z: RBNode):
        """修复红黑性质"""
        while z.parent and z.parent.color == RED:
            gp = z.parent.parent
            if gp is None:
                break
            if z.parent == gp.left:
                uncle = gp.right
                if uncle and uncle.color == RED:
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                uncle = gp.left
                if uncle and uncle.color == RED:
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
        self.root.color = BLACK

    def _left_rotate(self, x: RBNode):
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x: RBNode):
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def verify(self) -> tuple[bool, str]:
        """验证红黑树性质"""
        if self.root is None:
            return True, "空树"
        if self.root.color != BLACK:
            return False, "根非黑"
        ok, msg, bh = self._verify_node(self.root)
        return ok, msg

    def _verify_node(self, node: RBNode | None) -> tuple[bool, str, int]:
        if node is None:
            return True, "", 1  # NIL 黑高=1
        # 无连续红
        if node.color == RED:
            if (node.left and node.left.color == RED) or (node.right and node.right.color == RED):
                return False, f"连续红 @ {node.key}", 0
        ok_l, msg_l, bh_l = self._verify_node(node.left)
        ok_r, msg_r, bh_r = self._verify_node(node.right)
        if not ok_l:
            return False, msg_l, 0
        if not ok_r:
            return False, msg_r, 0
        if bh_l != bh_r:
            return False, f"黑高不等 @ {node.key}: {bh_l} vs {bh_r}", 0
        return True, "", bh_l + (1 if node.color == BLACK else 0)

    def height(self) -> int:
        def _h(node):
            if node is None:
                return 0
            return 1 + max(_h(node.left), _h(node.right))
        return _h(self.root)

    def inorder(self) -> list:
        result = []
        def _in(node):
            if node:
                _in(node.left)
                result.append(node.key)
                _in(node.right)
        _in(self.root)
        return result


# ============ 2. 布谷鸟哈希 ============

class CuckooHash:
    """
    双表布谷鸟哈希：两个哈希函数 h1, h2。
    查找 O(1)（最多查 2 个位置）。
    插入可能踢出（rehash）。
    """

    def __init__(self, capacity: int = 16):
        self.cap = capacity
        self.table1: list = [None] * capacity
        self.table2: list = [None] * capacity
        self.size = 0
        self.max_kicks = 6 * int(capacity ** 0.5 // 6 + 1)

    def h1(self, key) -> int:
        return hash(key) % self.cap

    def h2(self, key) -> int:
        return (hash(key) * 2654435761 % 2**32) % self.cap

    def insert(self, key, val, _kicks=0) -> bool:
        if self.lookup(key) is not None:
            # 已存在，更新
            i1 = self.h1(key)
            if self.table1[i1] and self.table1[i1][0] == key:
                self.table1[i1] = (key, val)
                return True
            i2 = self.h2(key)
            self.table2[i2] = (key, val)
            return True

        if _kicks > self.max_kicks:
            return False  # 需 rehash

        i1 = self.h1(key)
        if self.table1[i1] is None:
            self.table1[i1] = (key, val)
            self.size += 1
            return True

        # 踢出
        i2 = self.h2(key)
        if self.table2[i2] is None:
            self.table2[i2] = (key, val)
            self.size += 1
            return True

        # 两个位置都满，踢 table1
        evicted = self.table1[i1]
        self.table1[i1] = (key, val)
        self.size += 1
        return self.insert(evicted[0], evicted[1], _kicks + 1)

    def lookup(self, key):
        i1 = self.h1(key)
        if self.table1[i1] and self.table1[i1][0] == key:
            return self.table1[i1][1]
        i2 = self.h2(key)
        if self.table2[i2] and self.table2[i2][0] == key:
            return self.table2[i2][1]
        return None


# ============ 3. 图算法 ============

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def kruskal_mst(n: int, edges: list[tuple[int, int, float]]) -> list[tuple[int, int, float]]:
    """
    Kruskal 最小生成树
    edges: (u, v, weight)
    """
    edges_sorted = sorted(edges, key=lambda e: e[2])
    uf = UnionFind(n)
    mst = []
    for u, v, w in edges_sorted:
        if uf.union(u, v):
            mst.append((u, v, w))
    return mst


def bfs(adj: dict[int, list[int]], start: int) -> list[int]:
    from collections import deque
    visited = set()
    order = []
    q = deque([start])
    visited.add(start)
    while q:
        node = q.popleft()
        order.append(node)
        for nb in adj.get(node, []):
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
    return order


def dfs(adj: dict[int, list[int]], start: int) -> list[int]:
    visited = set()
    order = []
    def _go(node):
        visited.add(node)
        order.append(node)
        for nb in adj.get(node, []):
            if nb not in visited:
                _go(nb)
    _go(start)
    return order


# ============ Demo ============

def demo():
    print("=" * 60)
    print("AlgoDat: 红黑树 + 布谷鸟哈希 + MST")
    print("=" * 60)
    random.seed(42)

    # 1. 红黑树
    print("\n📋 1. 红黑树")
    tree = RBTree()
    keys = random.sample(range(1000), 200)
    for k in keys:
        tree.insert(k)
    ok, msg = tree.verify()
    h = tree.height()
    import math
    ideal = math.ceil(math.log2(201))
    print(f"   插入 {len(keys)} 个键")
    print(f"   验证: {'✓' if ok else '✗ ' + msg}")
    print(f"   高度: {h}  (理想 log₂(200)={ideal}, 上界 2·log={2*ideal})")
    inorder = tree.inorder()
    print(f"   inorder 排序正确: {inorder == sorted(keys)}")

    # 2. 布谷鸟哈希
    print("\n📋 2. 布谷鸟哈希")
    ch = CuckooHash(capacity=64)
    inserted = 0
    for i in range(40):
        if ch.insert(f"key{i}", f"val{i}"):
            inserted += 1
    found = sum(1 for i in range(40) if ch.lookup(f"key{i}") is not None)
    print(f"   插入 {inserted}/40, 查到 {found}/40")
    print(f"   装载因子: {ch.size}/{ch.cap} = {ch.size/ch.cap:.1%}")

    # 3. Kruskal MST
    print("\n📋 3. Kruskal 最小生成树")
    n = 6
    edges = [
        (0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2),
        (2, 3, 4), (3, 4, 2), (4, 5, 6), (2, 4, 5),
    ]
    mst = kruskal_mst(n, edges)
    total = sum(w for _, _, w in mst)
    print(f"   MST 边数={len(mst)}, 总权重={total}")
    for u, v, w in mst:
        print(f"     {u}--{v} (w={w})")

    # 4. BFS/DFS
    print("\n📋 4. 图遍历 (BFS / DFS)")
    adj = {0: [1, 2], 1: [0, 3, 4], 2: [0, 5], 3: [1], 4: [1, 5], 5: [2, 4]}
    print(f"   BFS(0): {bfs(adj, 0)}")
    print(f"   DFS(0): {dfs(adj, 0)}")

    # 反直觉
    print("\n💡 反直觉发现：红黑树的平衡是「近平衡」")
    tree2 = RBTree()
    for k in range(1, 256):  # 顺序插入 1..255（普通 BST 会退化成链表高度 254）
        tree2.insert(k)
    ok2, _ = tree2.verify()
    h2 = tree2.height()
    print(f"   顺序插入 1..255: 普通 BST 高度=255（退化链表）")
    print(f"   红黑树高度={h2}, log₂(255)≈8, 上界 2×8=16")
    print(f"   → 旋转以 O(1) 额外操作换取 O(log n) 最坏保证")

    print("\n✅ AlgoDat 完成！")


if __name__ == "__main__":
    demo()
