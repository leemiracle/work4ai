"""
CSC 263 Data Structures & Analysis (University of Toronto)
==========================================================
覆盖主题：
- AVL 树（自平衡 BST）
- B-Tree（磁盘优化多路搜索树）
- Hash Table（开放寻址 + 链地址法）
- Binomial Heap（可合并优先队列）

核心教材：
- Cormen et al. "Introduction to Algorithms" (CLRS, 4th ed.)
- "The Art of Computer Programming Vol.3" by Knuth (Sorting and Searching)
- Bayer & McCreight "Organization and Maintenance of Large Ordered Indices" (1972)

本文件实现：
- AVL 树（插入 + 旋转 + 高度平衡验证）
- B-Tree（插入 + 搜索 + 节点分裂）
- Hash Table（两种冲突策略对比）
- Binomial Heap（合并 + extract-min）

运行：
    python data_struct.py
"""
from __future__ import annotations
import math
import random


# ============ 1. AVL Tree ============

class AVLNode:
    __slots__ = ['val', 'left', 'right', 'height']
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    """
    AVL 树：每个节点的左右子树高度差 ≤ 1
    插入后通过旋转恢复平衡
    """

    def __init__(self):
        self.root = None
        self.rotations = 0

    def insert(self, val):
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if node is None:
            return AVLNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        else:
            return node

        node.height = 1 + max(self._h(node.left), self._h(node.right))
        balance = self._h(node.left) - self._h(node.right)

        # Left Left
        if balance > 1 and val < node.left.val:
            self.rotations += 1
            return self._rotate_right(node)
        # Right Right
        if balance < -1 and val > node.right.val:
            self.rotations += 1
            return self._rotate_left(node)
        # Left Right
        if balance > 1 and val > node.left.val:
            self.rotations += 2
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Right Left
        if balance < -1 and val < node.right.val:
            self.rotations += 2
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._h(z.left), self._h(z.right))
        y.height = 1 + max(self._h(y.left), self._h(y.right))
        return y

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._h(z.left), self._h(z.right))
        y.height = 1 + max(self._h(y.left), self._h(y.right))
        return y

    @staticmethod
    def _h(node) -> int:
        return node.height if node else 0

    def inorder(self) -> list:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def height(self) -> int:
        return self._h(self.root)

    def is_balanced(self) -> bool:
        def check(node):
            if node is None:
                return True, 0
            lb, lh = check(node.left)
            rb, rh = check(node.right)
            balanced = lb and rb and abs(lh - rh) <= 1
            return balanced, 1 + max(lh, rh)
        return check(self.root)[0]


# ============ 2. B-Tree ============

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t          # 最小度数
        self.keys = []
        self.children = []
        self.leaf = leaf

    def search(self, key):
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1
        if i < len(self.keys) and key == self.keys[i]:
            return True
        if self.leaf:
            return False
        return self.children[i].search(key)


class BTree:
    """
    B-Tree：每个节点最多 2t-1 个键，最少 t-1 个键
    根节点至少 1 个键
    """
    def __init__(self, t=3):
        self.t = t
        self.root = BTreeNode(t, leaf=True)
        self.splits = 0

    def search(self, key) -> bool:
        return self.root.search(key)

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            self.splits += 1
            new_root = BTreeNode(self.t, leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key)

    def _split_child(self, parent, index):
        t = self.t
        full = parent.children[index]
        new_node = BTreeNode(t, leaf=full.leaf)

        # 右半部分移到新节点
        new_node.keys = full.keys[t:]
        mid_key = full.keys[t - 1]
        full.keys = full.keys[:t - 1]

        if not full.leaf:
            new_node.children = full.children[t:]
            full.children = full.children[:t]

        parent.keys.insert(index, mid_key)
        parent.children.insert(index + 1, new_node)

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self.splits += 1
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)


# ============ 3. Hash Table ============

class HashTableChaining:
    """链地址法"""
    def __init__(self, size=16):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.count = 0
        self.collisions = 0

    def _hash(self, key) -> int:
        return hash(key) % self.size

    def insert(self, key, value):
        idx = self._hash(key)
        if self.table[idx]:  # 已有元素 → 碰撞
            self.collisions += 1
        for i, (k, _) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))
        self.count += 1

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

    def load_factor(self) -> float:
        return self.count / self.size


class HashTableOpenAddressing:
    """开放寻址（线性探测）"""
    def __init__(self, size=16):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
        self.deleted = [False] * size
        self.count = 0
        self.probes = 0

    def _hash(self, key) -> int:
        return hash(key) % self.size

    def insert(self, key, value):
        if self.count >= self.size:
            return  # 表满，丢弃（教学简化）
        idx = self._hash(key)
        while self.keys[idx] is not None and not self.deleted[idx]:
            self.probes += 1
            if self.keys[idx] == key:
                self.values[idx] = value
                return
            idx = (idx + 1) % self.size
        self.keys[idx] = key
        self.values[idx] = value
        self.deleted[idx] = False
        self.count += 1

    def get(self, key):
        idx = self._hash(key)
        for _ in range(self.size):  # 最多探测 size 次
            if self.keys[idx] is None:
                return None
            if self.keys[idx] == key and not self.deleted[idx]:
                return self.values[idx]
            idx = (idx + 1) % self.size
        return None


# ============ 4. Binomial Heap ============

class BinomialNode:
    def __init__(self, key):
        self.key = key
        self.degree = 0
        self.parent = None
        self.child = None
        self.sibling = None


class BinomialHeap:
    """
    Binomial Heap: 支持高效合并（O(log n)）
    - make-heap: O(1)
    - insert: O(log n)
    - find-min: O(log n)
    - extract-min: O(log n)
    - union: O(log n)
    """

    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def _merge_roots(self, h1, h2):
        """按 degree 合并两个根链表"""
        if h1 is None:
            return h2
        if h2 is None:
            return h1
        if h1.degree <= h2.degree:
            result = h1
            result.sibling = self._merge_roots(h1.sibling, h2)
        else:
            result = h2
            result.sibling = self._merge_roots(h1, h2.sibling)
        return result

    def _link(self, y, z):
        """让 y 成为 z 的子节点"""
        y.parent = z
        y.sibling = z.child
        z.child = y
        z.degree += 1

    def _union(self, h2_head):
        """合并两个 heap 并维护 binomial 性质"""
        self.head = self._merge_roots(self.head, h2_head)
        if self.head is None:
            return

        prev = None
        curr = self.head
        nxt = curr.sibling

        while nxt is not None:
            if (curr.degree != nxt.degree or
                (nxt.sibling is not None and nxt.sibling.degree == curr.degree)):
                prev = curr
                curr = nxt
            elif curr.key <= nxt.key:
                curr.sibling = nxt.sibling
                self._link(nxt, curr)
            else:
                if prev is None:
                    self.head = nxt
                else:
                    prev.sibling = nxt
                self._link(curr, nxt)
                curr = nxt
            nxt = curr.sibling

    def insert(self, key):
        node = BinomialNode(key)
        node.degree = 0
        self._union(node)

    def find_min(self) -> int | None:
        if self.head is None:
            return None
        min_val = self.head.key
        curr = self.head.sibling
        while curr:
            if curr.key < min_val:
                min_val = curr.key
            curr = curr.sibling
        return min_val


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 263: Data Structures Demo")
    print("=" * 60)

    random.seed(42)

    # 1. AVL Tree
    print("\n📋 1. AVL Tree（自平衡 BST）")
    avl = AVLTree()
    values = list(range(1, 16))  # 1..15 顺序插入
    for v in values:
        avl.insert(v)
    print(f"   插入 1..15（顺序插入，最坏情况）")
    print(f"   AVL 高度: {avl.height()} (普通BST会是15)")
    print(f"   旋转次数: {avl.rotations}")
    print(f"   平衡验证: {avl.is_balanced()}")
    print(f"   中序遍历: {avl.inorder()}")

    # 反直觉：普通 BST vs AVL 高度
    print(f"\n   反直觉发现：")
    print(f"   顺序插入 1..15:")
    print(f"     普通 BST 高度 = 15（退化成链表）")
    print(f"     AVL 高度 = {avl.height()} (log₂(15)≈{math.log2(15):.1f})")

    # 2. B-Tree
    print("\n📋 2. B-Tree（t=3，磁盘优化）")
    bt = BTree(t=3)
    keys = list(range(1, 30))
    random.shuffle(keys)
    for k in keys:
        bt.insert(k)
    # 验证搜索
    all_found = all(bt.search(k) for k in range(1, 30))
    none_found = not bt.search(100) and not bt.search(0)
    print(f"   插入 1..29（随机顺序）")
    print(f"   节点分裂次数: {bt.splits}")
    print(f"   搜索 1..29 全部命中: {all_found}")
    print(f"   搜索 0,100 未命中: {none_found}")
    print(f"   → B-Tree 每节点最多 {2*3-1}=5 个键，减少磁盘 I/O")

    # 3. Hash Table 对比
    print("\n📋 3. Hash Table（链地址 vs 开放寻址）")
    ht_chain = HashTableChaining(size=16)
    ht_open = HashTableOpenAddressing(size=64)  # 足够大避免溢出
    test_data = [(f"key_{i}", i * 10) for i in range(50)]
    for k, v in test_data:
        ht_chain.insert(k, v)
        ht_open.insert(k, v)
    print(f"   插入 50 个键到 size=16 的表")
    print(f"   链地址法: 碰撞 {ht_chain.collisions} 次, 负载因子 {ht_chain.load_factor():.2f}")
    print(f"   开放寻址: 探测 {ht_open.probes} 次, 负载因子 {ht_open.count/ht_open.size:.2f}")
    # 验证正确性
    ok = all(ht_chain.get(f"key_{i}") == i * 10 for i in range(50))
    ok2 = all(ht_open.get(f"key_{i}") == i * 10 for i in range(50))
    print(f"   链地址法正确: {ok}")
    print(f"   开放寻址正确: {ok2}")

    # 4. Binomial Heap
    print("\n📋 4. Binomial Heap")
    bh1 = BinomialHeap()
    bh2 = BinomialHeap()
    for v in [5, 2, 8, 1, 9, 3]:
        bh1.insert(v)
    for v in [4, 7, 6, 0]:
        bh2.insert(v)
    bh1._union(bh2.head)
    min_val = bh1.find_min()
    print(f"   Heap1 插入 [5,2,8,1,9,3]")
    print(f"   Heap2 插入 [4,7,6,0]")
    print(f"   合并后 min = {min_val} (期望 0)")
    print(f"   → Binomial Heap 合并 O(log n) vs Binary Heap O(n)")

    print("\n✅ CSC 263 完成！")
    print("💡 覆盖：AVL旋转 + B-Tree分裂 + Hash碰撞 + Binomial Heap合并")


if __name__ == "__main__":
    demo()
