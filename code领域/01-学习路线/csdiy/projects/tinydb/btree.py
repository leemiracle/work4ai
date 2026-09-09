#!/usr/bin/env python3
"""
tinydb/btree.py — 真正的 B+ 树实现（参照 sqlite-btree 精读）

csdiy 对应：
  - source-reading/sqlite-btree-逐行拆解.md（balance_nonroot 分裂算法）
  - notes/db-程序员视角 §一（B+ 树、索引选择性）
  - projects/tinydb/main.py（page-based 存储，线性扫描版）

核心算法（参照 SQLite btree.c）：
  - search: 从根到叶子二分查找
  - insert: 找叶子 → 插入 → 满了分裂 → 中间 key 上推
  - split: balance_nonroot 的简化版
  - range: 叶子节点链表遍历（B+ 树 vs B 树的核心优势）
  - visualize: ASCII 可视化树结构

对比 tinydb/main.py：
  - main.py 的 Page.find_cell() = 线性扫描 O(N)
  - 本文件 BPlusTree.search() = O(log N) 二分 + 树遍历
"""
import bisect, random, sys
from dataclasses import dataclass, field
from typing import Optional, Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# B+ 树节点（参照 SQLite btree page 的两种类型）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEAF = 0x0D      # 参照 SQLite leaf table page = 0x0D
INTERNAL = 0x05   # 参照 SQLite interior table page = 0x05

@dataclass
class BPlusNode:
    """
    B+ 树节点（参照 SQLite btree page）

    叶子节点（LEAF）：存 [key, value] pairs
    内部节点（INTERNAL）：存 [key, child_ptr] 用于路由，不存 value

    关键差异（B+ vs B）：
    - B 树：所有节点都存 value
    - B+ 树：只有叶子存 value，内部节点只做路由
    - B+ 树叶子节点用链表连接（范围查询 O(N) 而非 O(N log N)）
    """
    page_type: int
    keys: list = field(default_factory=list)
    values: list = field(default_factory=list)    # 只在叶子节点
    children: list = field(default_factory=list)   # 只在内部节点（child 引用）
    next_leaf: Optional["BPlusNode"] = None       # 叶子链表（范围查询用）

    @property
    def is_leaf(self):
        return self.page_type == LEAF

    def is_full(self, order):
        return len(self.keys) >= order

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# B+ 树核心
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BPlusTree:
    """
    B+ 树（参照 SQLite btree.c + db 教材）

    order（阶）：每个节点最多 order 个 key
    - order=4 时：每个节点最多 4 个 key → 5 个子节点（内部）/ 4 个 value（叶子）
    - SQLite 默认 page 4KB，一个 page 约存 200+ 个 key

    对比 tinydb/main.py 的线性扫描：
    - 线性扫描找 1 个 key：O(N) 遍历所有 page
    - B+ 树找 1 个 key：O(log_order N) 比较次数
    - 100 万条数据：线性扫描 100 万次 vs B+ 树 ~10 次（order=100）
    """

    def __init__(self, order: int = 4):
        self.order = order
        self.root = BPlusNode(page_type=LEAF)
        self.height = 1
        self.count = 0

    # ─── 搜索 ────────────────────────────────────────────

    def search(self, key) -> Any:
        """
        查找 key（参照 SQLite sqlite3BtreeMovetoUnpacked）

        从根开始：
        1. 内部节点：二分找 <= key 的最大子树 → 下降
        2. 叶子节点：二分找 key → 返回 value
        """
        node = self.root
        while not node.is_leaf:
            # 二分查找（参照 SQLite btreeMovetoUnpacked 的二分）
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]

        # 在叶子节点二分查找
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        return None

    def search_verbose(self, key) -> tuple:
        """带路径追踪的搜索（教学用，显示遍历路径）"""
        path = []
        node = self.root
        depth = 0
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, key)
            path.append(f"L{depth}: internal keys={node.keys} → child[{i}]")
            node = node.children[i]
            depth += 1

        i = bisect.bisect_left(node.keys, key)
        path.append(f"L{depth}: leaf keys={node.keys} → pos={i}")
        found = i < len(node.keys) and node.keys[i] == key
        path.append(f"  result: {'FOUND' if found else 'NOT FOUND'}")
        return (node.values[i] if found else None, path)

    # ─── 插入 ────────────────────────────────────────────

    def insert(self, key, value):
        """
        插入 key-value（参照 SQLite sqlite3BtreeInsert + balance_nonroot）

        步骤：
        1. 从根到叶子找到目标叶子节点
        2. 在叶子节点插入（保持有序）
        3. 如果叶子满了 → 分裂 → 中间 key 上推到父节点
        4. 如果父节点也满了 → 继续分裂 → 可能创建新根
        """
        # 找到目标叶子节点 + 记录路径
        path = []
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, key)
            path.append((node, i))
            node = node.children[i]

        # 在叶子节点插入（参照 SQLite insertCell）
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.values[i] = value  # 更新已有 key
            return False  # 不是新 key
        else:
            node.keys.insert(i, key)
            node.values.insert(i, value)
            self.count += 1

        # 检查是否需要分裂（参照 SQLite balance_nonroot）
        if node.is_full(self.order):
            self._split(node, path)

        return True  # 新 key

    def _split(self, node, path):
        """
        分裂节点（参照 SQLite balance_nonroot 的核心逻辑）

        叶子分裂：
          [1,3,5,7] → [1,3] + [5,7]，key=5 上推
        内部分裂：
          [k1,k2,k3,k4] → [k1,k2] + [k4]，k3 上推（不上留在任何节点）
        """
        mid = len(node.keys) // 2

        if node.is_leaf:
            # 叶子分裂（参照 SQLite leaf page split）
            new_node = BPlusNode(
                page_type=LEAF,
                keys=node.keys[mid:],
                values=node.values[mid:],
            )
            new_node.next_leaf = node.next_leaf
            node.next_leaf = new_node
            node.keys = node.keys[:mid]
            node.values = node.values[:mid]
            up_key = new_node.keys[0]  # 新叶子的第一个 key 上推
        else:
            # 内部分裂（参照 SQLite interior page split）
            up_key = node.keys[mid]  # 中间 key 上推（不留在任何子节点）
            new_node = BPlusNode(
                page_type=INTERNAL,
                keys=node.keys[mid + 1:],
                children=node.children[mid + 1:],
            )
            node.keys = node.keys[:mid]
            node.children = node.children[:mid + 1]

        self._insert_into_parent(up_key, node, new_node, path)

    def _insert_into_parent(self, up_key, left_child, right_child, path):
        """
        将分裂后的 key 和新子节点插入父节点
        （参照 SQLite balance 的"向上传播"）

        如果没有父节点（根分裂）→ 创建新根
        如果父节点也满了 → 递归分裂
        """
        if not path:
            # 根节点分裂 → 创建新根（树长高一层）
            new_root = BPlusNode(
                page_type=INTERNAL,
                keys=[up_key],
                children=[left_child, right_child],
            )
            self.root = new_root
            self.height += 1
            return

        parent, child_idx = path[-1]
        parent.keys.insert(child_idx, up_key)
        parent.children.insert(child_idx + 1, right_child)

        if parent.is_full(self.order):
            # 父节点也满了 → 递归分裂（参照 SQLite balance 的"级联分裂"）
            self._split(parent, path[:-1])

    # ─── 范围查询 ────────────────────────────────────────

    def range_query(self, start_key, end_key) -> list:
        """
        范围查询（B+ 树的核心优势，参照 SQLite 的范围扫描）

        B+ 树：找到起始叶子 → 沿叶子链表遍历 → O(N) 收集
        B 树：需要中序遍历整棵树 → O(N log N)
        """
        # 找到起始叶子
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, start_key)
            node = node.children[i]

        # 遍历叶子链表
        results = []
        while node:
            for i, k in enumerate(node.keys):
                if start_key <= k <= end_key:
                    results.append((k, node.values[i]))
                elif k > end_key:
                    return results
            node = node.next_leaf
        return results

    # ─── 删除 ────────────────────────────────────────────

    def delete(self, key) -> bool:
        """
        删除 key（简化版，不做合并/借键）

        真实 SQLite 的 delete 会触发 balance 的"合并"逻辑：
        如果删除后页太空 → 和兄弟页合并 → 可能导致树变矮。
        本实现简化：只删数据，不合并（适合学习基本概念）。
        """
        path = []
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, key)
            path.append((node, i))
            node = node.children[i]

        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.keys.pop(i)
            node.values.pop(i)
            self.count -= 1
            return True
        return False

    # ─── 可视化 ──────────────────────────────────────────

    def visualize(self) -> str:
        """ASCII 可视化树结构（参照 db 教材的树图）"""
        lines = [f"B+Tree (order={self.order}, height={self.height}, keys={self.count})"]
        self._viz(self.root, 0, lines, is_root=True)
        return "\n".join(lines)

    def _viz(self, node, depth, lines, is_root=False, prefix=""):
        indent = "  " * depth
        if node.is_leaf:
            pairs = [f"{k}→{v}" for k, v in zip(node.keys, node.values)]
            arrow = "→" if node.next_leaf else "⊥"
            lines.append(f"{indent}[LEAF{depth}] {', '.join(pairs)} {arrow}")
        else:
            lines.append(f"{indent}[INT{depth}] keys={node.keys}")
            for i, child in enumerate(node.children):
                self._viz(child, depth + 1, lines)

    def stats(self) -> dict:
        """统计信息"""
        return {
            "order": self.order,
            "height": self.height,
            "total_keys": self.count,
            "root_type": "leaf" if self.root.is_leaf else "internal",
            "root_keys": len(self.root.keys),
        }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 测试 + Demo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("=" * 60)
    print("  B+ 树实现（参照 SQLite btree.c）")
    print("=" * 60)

    # ─── Demo 1：基本操作 ───
    print("\n── Demo 1: 基本插入+查找 ──")
    tree = BPlusTree(order=4)  # order=4 容易触发分裂

    data = [(10, "ten"), (20, "twenty"), (5, "five"), (15, "fifteen"),
            (25, "twenty-five"), (30, "thirty"), (3, "three"), (7, "seven")]

    for k, v in data:
        tree.insert(k, v)
        print(f"  insert({k:2d}, {v:12s}) → height={tree.height}")

    print(f"\n{tree.visualize()}")
    print(f"\n  stats: {tree.stats()}")

    # 搜索（含路径追踪）
    print("\n── 搜索路径追踪 ──")
    val, path = tree.search_verbose(25)
    print(f"  search(25) = {val}")
    for line in path:
        print(f"    {line}")

    val, path = tree.search_verbose(100)
    print(f"\n  search(100) = {val}")
    for line in path:
        print(f"    {line}")

    # ─── Demo 2：范围查询 ───
    print("\n── 范围查询 [7, 25] ──")
    results = tree.range_query(7, 25)
    for k, v in results:
        print(f"    {k:3d} → {v}")

    # ─── Demo 3：大规模插入 + 性能 ───
    print("\n── Demo 3: 1000 个随机 key ──")
    big_tree = BPlusTree(order=100)  # 更大的 order → 更矮的树
    random.seed(42)
    keys = random.sample(range(1, 100000), 1000)
    for k in keys:
        big_tree.insert(k, f"val_{k}")

    print(f"  插入 1000 个 key")
    print(f"  stats: {big_tree.stats()}")
    print(f"  树高: {big_tree.height}（线性扫描需要 1000 次比较，B+树只需 ~{big_tree.height}×log2(100)≈{big_tree.height * 7} 次）")

    # 验证
    test_key = keys[500]
    val = big_tree.search(test_key)
    print(f"  search({test_key}) = {val} {'✅' if val else '❌'}")

    missing = 99999  # 不存在的 key
    val = big_tree.search(missing)
    print(f"  search({missing}) = {val} {'✅ 正确返回 None' if val is None else '❌'}")

    # ─── Demo 4：可视化小树 ───
    print("\n── Demo 4: 可视化 ──")
    small = BPlusTree(order=3)
    for k in [1, 3, 5, 7, 9, 2, 4, 6, 8, 10, 11, 12]:
        small.insert(k, f"v{k}")
    print(small.visualize())

    # ─── Demo 5：删除 ───
    print("\n── Demo 5: 删除 ──")
    print(f"  删除前 count={small.count}")
    for k in [5, 10, 1]:
        ok = small.delete(k)
        print(f"  delete({k:2d}) = {'✅' if ok else '❌'}")
    print(f"  删除后 count={small.count}")
    print(f"  search(5) = {small.search(5)} {'✅' if small.search(5) is None else '❌'}")
    print(f"  search(3) = {small.search(3)} {'✅' if small.search(3) else '❌'}")

    print(f"\n{'=' * 60}")
    print("  B+ 树核心算法验证完成")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
