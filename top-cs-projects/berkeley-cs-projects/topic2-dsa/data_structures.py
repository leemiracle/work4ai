"""
CS 61B Data Structures — UC Berkeley (Hug)
================================================
覆盖主题：
- 二叉堆（priority queue）（Lec 12）
- 红黑树（平衡 BST）（Lec 11）
- 哈希表（chaining + open addressing）（Lec 10）
- 图：DFS / BFS / 拓扑排序（Lec 22-24）

核心教材/参考：
- Sedgewick & Wayne "Algorithms" 4th ed (Addison-Wesley 2011), §3.4-3.5, §4.2
- Goodrich & Tamassia "Data Structures and Algorithms in Java" 6th ed, Ch 3/7/9/13
- Cormen Leiserson Rivest Stein "Introduction to Algorithms" 3rd ed (MIT 2009), §13 (RB-tree), §11 (hash), §22 (BFS/DFS)

本文件实现：
- Binary Min-Heap（含 up/down heapify）
- 红黑树（左旋/右旋 + 插入修复）
- 哈希表（chaining + linear probing 双模对比）
- 图 DFS/BFS/拓扑排序（Kahn 算法）

运行：
    python data_structures.py
"""
from __future__ import annotations
from collections import deque
import random


# ============================================================
# 1. Binary Min-Heap（Sedgewick §2.4）
# ============================================================

class MinHeap:
    """
    数组实现 min-heap，1-indexed（index 0 留空）。
    parent(i) = i//2, left(i) = 2i, right(i) = 2i+1
    insert: O(log n)  sink up
    extract_min: O(log n)  sink down
    """
    def __init__(self):
        self.data = [None]  # index 0 unused

    def __len__(self):
        return len(self.data) - 1

    def insert(self, val):
        self.data.append(val)
        self._swim(len(self.data) - 1)

    def _swim(self, k):
        while k > 1 and self.data[k] < self.data[k // 2]:
            self.data[k], self.data[k // 2] = self.data[k // 2], self.data[k]
            k //= 2

    def extract_min(self):
        if len(self.data) <= 1:
            raise IndexError("heap empty")
        min_val = self.data[1]
        last = self.data.pop()
        if len(self.data) > 1:
            self.data[1] = last
            self._sink(1)
        return min_val

    def _sink(self, k):
        n = len(self.data) - 1
        while 2 * k <= n:
            j = 2 * k
            if j < n and self.data[j + 1] < self.data[j]:
                j += 1
            if self.data[k] <= self.data[j]:
                break
            self.data[k], self.data[j] = self.data[j], self.data[k]
            k = j


# ============================================================
# 2. Red-Black Tree（CLRS §13）
# ============================================================

class RBNode:
    __slots__ = ("key", "color", "left", "right", "parent")
    def __init__(self, key, color="RED"):
        self.key = key
        self.color = color  # "RED" or "BLACK"
        self.left: RBNode | None = None
        self.right: RBNode | None = None
        self.parent: RBNode | None = None


class RedBlackTree:
    """
    RB-tree 性质（CLRS §13.1）：
    1. 每个节点 red 或 black
    2. 根是 black
    3. 每个 NIL leaf 是 black
    4. red 节点的孩子都是 black（不能连续两个 red）
    5. 从任一节点到其所有后代 leaf 的路径上 black 节点数相同（black-height）
    → 高度 ≤ 2 log(n+1)，保证操作 O(log n)
    """
    def __init__(self):
        self.NIL = RBNode(None, "BLACK")
        self.root = self.NIL

    def _left_rotate(self, x: RBNode):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, y: RBNode):
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent == self.NIL:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x

    def insert(self, key):
        z = RBNode(key, "RED")
        z.left = z.right = self.NIL
        y = self.NIL
        x = self.root
        while x != self.NIL:
            y = x
            x = x.left if key < x.key else x.right
        z.parent = y
        if y == self.NIL:
            self.root = z
        elif key < y.key:
            y.left = z
        else:
            y.right = z
        self._insert_fixup(z)

    def _insert_fixup(self, z: RBNode):
        """修复性质 4（连续 red）—— 三种 case + 镜像"""
        while z.parent.color == "RED":
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right  # uncle
                if y.color == "RED":           # Case 1: uncle red → recolor
                    z.parent.color = "BLACK"
                    y.color = "BLACK"
                    z.parent.parent.color = "RED"
                    z = z.parent.parent
                else:
                    if z == z.parent.right:     # Case 2: zig-zag → rotate to linear
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = "BLACK"     # Case 3: zig → rotate + recolor
                    z.parent.parent.color = "RED"
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.color == "RED":
                    z.parent.color = "BLACK"
                    y.color = "BLACK"
                    z.parent.parent.color = "RED"
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = "BLACK"
                    z.parent.parent.color = "RED"
                    self._left_rotate(z.parent.parent)
        self.root.color = "BLACK"

    def inorder(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node != self.NIL:
            self.inorder(node.left, result)
            result.append((node.key, node.color[0]))
            self.inorder(node.right, result)
        return result

    def black_height(self, node=None):
        """验证性质 5"""
        if node is None:
            node = self.root
        if node == self.NIL:
            return 1
        bh = self.black_height(node.left)
        # 验证左右 black-height 一致
        assert self.black_height(node.right) == bh, "RB property 5 violated!"
        return bh + (1 if node.color == "BLACK" else 0)


# ============================================================
# 3. Hash Table —— chaining vs open addressing（CLRS §11）
# ============================================================

class HashChaining:
    """chaining: 每个槽一个链表"""
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.size = 0
        self.buckets: list[list[tuple]] = [[] for _ in range(capacity)]

    def _hash(self, key) -> int:
        return hash(key) % self.capacity

    def put(self, key, val):
        h = self._hash(key)
        for i, (k, _) in enumerate(self.buckets[h]):
            if k == key:
                self.buckets[h][i] = (key, val)
                return
        self.buckets[h].append((key, val))
        self.size += 1

    def get(self, key, default=None):
        h = self._hash(key)
        for k, v in self.buckets[h]:
            if k == key:
                return v
        return default

    def load_factor(self):
        return self.size / self.capacity


class HashOpenAddr:
    """linear probing: h, h+1, h+2, ..."""
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.keys: list = [None] * capacity
        self.vals: list = [None] * capacity
        self.size = 0

    def _hash(self, key) -> int:
        return hash(key) % self.capacity

    def _probe(self, key):
        """找到 key 的位置（或第一个 None）"""
        i = self._hash(key)
        while self.keys[i] is not None and self.keys[i] != key:
            i = (i + 1) % self.capacity
        return i

    def put(self, key, val):
        if self.size >= self.capacity * 0.7:
            self._resize(self.capacity * 2)
        i = self._probe(key)
        if self.keys[i] is None:
            self.size += 1
        self.keys[i] = key
        self.vals[i] = val

    def get(self, key, default=None):
        i = self._probe(key)
        return self.vals[i] if self.keys[i] is not None else default

    def _resize(self, new_cap):
        old_keys, old_vals = self.keys, self.vals
        self.capacity = new_cap
        self.keys = [None] * new_cap
        self.vals = [None] * new_cap
        self.size = 0
        for k, v in zip(old_keys, old_vals):
            if k is not None:
                self.put(k, v)


# ============================================================
# 4. Graph —— DFS / BFS / 拓扑排序（CLRS §22）
# ============================================================

class Graph:
    def __init__(self, directed: bool = False):
        self.adj: dict[str, list[str]] = {}
        self.directed = directed

    def add_edge(self, u, v):
        self.adj.setdefault(u, []).append(v)
        if not self.directed:
            self.adj.setdefault(v, []).append(u)
        else:
            self.adj.setdefault(v, [])

    def bfs(self, start) -> list[str]:
        """CLRS §22.2：层次遍历"""
        visited = {start}
        queue = deque([start])
        order = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in self.adj.get(u, []):
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
        return order

    def dfs(self, start) -> list[str]:
        """CLRS §22.3"""
        visited = set()
        order = []

        def _visit(u):
            visited.add(u)
            order.append(u)
            for v in self.adj.get(u, []):
                if v not in visited:
                    _visit(v)

        _visit(start)
        return order

    def topo_sort(self) -> list[str]:
        """Kahn 算法（BFS 拓扑排序），需要 directed graph"""
        in_degree = {u: 0 for u in self.adj}
        for u in self.adj:
            for v in self.adj[u]:
                in_degree[v] = in_degree.get(v, 0) + 1
        queue = deque([u for u, d in in_degree.items() if d == 0])
        order = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in self.adj.get(u, []):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        return order


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 61B Data Structures Demo")
    print("=" * 60)

    # 1. Min-Heap
    print("\n📋 1. Binary Min-Heap（优先队列）")
    heap = MinHeap()
    vals = [5, 3, 8, 1, 9, 2, 7, 4, 6]
    for v in vals:
        heap.insert(v)
    extracted = [heap.extract_min() for _ in range(len(vals))]
    print(f"   插入 {vals}")
    print(f"   排序输出: {extracted}")

    # 2. Red-Black Tree
    print("\n📋 2. Red-Black Tree（平衡 BST）")
    rbt = RedBlackTree()
    keys = [10, 20, 30, 15, 25, 5, 1]
    for k in keys:
        rbt.insert(k)
    print(f"   插入顺序: {keys}")
    print(f"   中序: {rbt.inorder()}")
    print(f"   black-height = {rbt.black_height()}")

    # 对比：乱序 vs 升序插入的树高度
    import math
    rbt2 = RedBlackTree()
    for k in range(1, 32):  # 升序 1..31
        rbt2.insert(k)
    bh2 = rbt2.black_height()
    naive_height = 32  # 普通 BST 升序插入退化为链表
    print(f"   升序插入 1..31: RB-tree black-height = {bh2}")
    print(f"   普通 BST 升序插入 31 个 → 高度 31（退化为链表！）")
    print(f"   RB-tree 保证高度 ≤ 2*log2(32) = {int(2*math.log2(32))}")

    # 3. Hash Table
    print("\n📋 3. 哈希表对比（chaining vs linear probing）")
    random.seed(42)
    ht_c = HashChaining(capacity=8)
    ht_o = HashOpenAddr(capacity=8)
    test_keys = [f"key{i}" for i in range(20)]
    for k in test_keys:
        ht_c.put(k, len(k))
        ht_o.put(k, len(k))

    # 验证正确性
    ok_c = all(ht_c.get(k) == len(k) for k in test_keys)
    ok_o = all(ht_o.get(k) == len(k) for k in test_keys)
    print(f"   chaining: 20 keys, load_factor={ht_c.load_factor():.2f}, all get OK = {ok_c}")
    print(f"   open-addr: 20 keys, capacity grew to {ht_o.capacity}, all get OK = {ok_o}")

    # 链长度分布
    chain_lens = [len(b) for b in ht_c.buckets]
    print(f"   chaining bucket sizes: {chain_lens} (max={max(chain_lens)})")

    # 4. Graph algorithms
    print("\n📋 4. 图算法（DFS / BFS / 拓扑排序）")
    # 拓扑排序图: 课程依赖
    g = Graph(directed=True)
    deps = [("61A", "61B"), ("61A", "70"), ("61B", "170"), ("70", "170"),
            ("61B", "162"), ("170", "170"), ("61C", "162"), ("70", "189"),
            ("61A", "61C"), ("61B", "188"), ("70", "188")]
    for u, v in deps:
        g.add_edge(u, v)

    topo = g.topo_sort()
    print(f"   拓扑排序（课程依赖）: {topo}")

    bfs_order = g.bfs("61A")
    print(f"   BFS from 61A: {bfs_order}")

    dfs_order = g.dfs("61A")
    print(f"   DFS from 61A: {dfs_order}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print(f"   RB-tree 升序插入 31 个元素，black-height 仅 {bh2}。")
    print("   如果用普通 BST 升序插入，树高度 = 31（一条链表）。")
    print(f"   查找从 O(31) → O({bh2})，快了 {31//bh2} 倍以上。")
    print("   这就是'平衡'的价值：RB-tree 用着色+旋转（每次插入 ≤3 次旋转）")
    print("   保证了最坏情况仍是 O(log n) —— 这是 Java TreeMap / C++ std::map 的底层。")


if __name__ == "__main__":
    demo()
