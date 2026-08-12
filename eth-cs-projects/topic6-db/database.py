"""
Database Systems — ETH Zürich
=============================
覆盖主题：
- 关系代数（σ π ⨝ − ×）
- B+ 树索引
- 2PL（两阶段锁）+ 隔离级别
- OLAP 星型模式 + 列存 vs 行存

核心教材/论文：
- Garcia-Molina, Ullman, Widom "Database Systems: The Complete Book" (Pearson, 2008)
- Bayer & McCreight "Organization and Maintenance of Large Ordered Indices" Acta Informatica 1(3): 173-189 (1972) — B-tree
- Mohan et al. "ARIES: A Transaction Recovery Method" ACM TODS 17(1): 94-162 (1992)
- Stonebraker "The Design of the POSTGRES Storage System" VLDB 1987 — 列存思想

本文件实现：
1. 关系代数运算符
2. B+ 树（插入 + 范围查询）
3. 2PL 锁管理器 + 死锁检测
4. 列存 vs 行存模拟

运行：
    python database.py
"""
from __future__ import annotations
import random
from collections import defaultdict


# ============ 1. 关系代数 ============

class Relation:
    """关系：表头 + 行集合"""

    def __init__(self, name: str, attrs: list[str], tuples: list[tuple]):
        self.name = name
        self.attrs = attrs
        self.tuples = [tuple(t) for t in tuples]

    def __repr__(self):
        lines = [f"  {self.name}({', '.join(self.attrs)})"]
        lines.append("  " + "-" * 30)
        for t in self.tuples:
            lines.append("  " + " | ".join(str(v) for v in t))
        return "\n".join(lines)

    # σ (selection)
    def select(self, pred) -> 'Relation':
        return Relation(f"σ({self.name})", self.attrs,
                        [t for t in self.tuples if pred(t)])

    # π (projection)
    def project(self, col_indices: list[int]) -> 'Relation':
        new_attrs = [self.attrs[i] for i in col_indices]
        seen = set()
        new_tuples = []
        for t in self.tuples:
            row = tuple(t[i] for i in col_indices)
            if row not in seen:
                seen.add(row)
                new_tuples.append(row)
        return Relation(f"π({self.name})", new_attrs, new_tuples)

    # ⨝ (natural join on specified columns)
    @staticmethod
    def join(r1: 'Relation', r2: 'Relation',
             r1_col: int, r2_col: int) -> 'Relation':
        """等值连接 r1[r1_col] = r2[r2_col]"""
        # Hash join
        index = defaultdict(list)
        for t in r2.tuples:
            index[t[r2_col]].append(t)
        new_attrs = r1.attrs + r2.attrs
        new_tuples = []
        for t1 in r1.tuples:
            for t2 in index.get(t1[r1_col], []):
                new_tuples.append(t1 + t2)
        return Relation(f"{r1.name}⨝{r2.name}", new_attrs, new_tuples)


# ============ 2. B+ 树 ============

class BPlusNode:
    def __init__(self, leaf: bool = False):
        self.leaf = leaf
        self.keys: list = []
        self.children: list['BPlusNode'] = []  # 内部节点
        self.values: list[list] = []  # 叶子: 每个 key 对应的值列表
        self.next: 'BPlusNode | None' = None  # 叶子链表


class BPlusTree:
    """B+ 树（教学版，order=4）"""

    def __init__(self, order: int = 4):
        self.order = order
        self.root = BPlusNode(leaf=True)

    def insert(self, key, val):
        leaf = self._find_leaf(key)
        # 插入到叶子
        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < key:
            idx += 1
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            leaf.values[idx].append(val)
            return
        leaf.keys.insert(idx, key)
        leaf.values.insert(idx, [val])

        if len(leaf.keys) >= self.order:
            self._split_leaf(leaf)

    def _find_leaf(self, key) -> BPlusNode:
        node = self.root
        while not node.leaf:
            idx = 0
            while idx < len(node.keys) and key >= node.keys[idx]:
                idx += 1
            node = node.children[idx]
        return node

    def _split_leaf(self, leaf: BPlusNode):
        mid = len(leaf.keys) // 2
        new_leaf = BPlusNode(leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]
        new_leaf.next = leaf.next
        leaf.next = new_leaf

        up_key = new_leaf.keys[0]
        self._insert_into_parent(leaf, up_key, new_leaf)

    def _insert_into_parent(self, left: BPlusNode, key, right: BPlusNode):
        if left is self.root:
            new_root = BPlusNode(leaf=False)
            new_root.keys = [key]
            new_root.children = [left, right]
            self.root = new_root
            return
        # 简化：直接重建
        parent = self._find_parent(self.root, left)
        if parent is None:
            return
        idx = parent.children.index(left)
        parent.keys.insert(idx, key)
        parent.children.insert(idx + 1, right)
        if len(parent.keys) >= self.order:
            self._split_internal(parent)

    def _find_parent(self, node: BPlusNode, child: BPlusNode) -> BPlusNode | None:
        if node.leaf:
            return None
        for c in node.children:
            if c is child:
                return node
            if not c.leaf:
                p = self._find_parent(c, child)
                if p:
                    return p
        return None

    def _split_internal(self, node: BPlusNode):
        mid = len(node.keys) // 2
        up_key = node.keys[mid]
        new_node = BPlusNode(leaf=False)
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        parent = self._find_parent(self.root, node)
        if parent is None:
            new_root = BPlusNode(leaf=False)
            new_root.keys = [up_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            idx = parent.children.index(node)
            parent.keys.insert(idx, up_key)
            parent.children.insert(idx + 1, new_node)

    def range_query(self, lo, hi) -> list:
        """范围查询 [lo, hi]"""
        leaf = self._find_leaf(lo)
        result = []
        while leaf:
            for i, k in enumerate(leaf.keys):
                if k > hi:
                    return result
                if k >= lo:
                    result.extend(leaf.values[i])
            leaf = leaf.next
        return result


# ============ 3. 2PL 锁管理器 ============

class LockManager:
    """
    两阶段锁（2PL）+ 等待图死锁检测
    """

    def __init__(self):
        self.locks: dict[str, str] = {}  # resource → holder txn
        self.waits_for: dict[str, str] = {}  # txn → waiting for resource

    def acquire(self, txn: str, resource: str) -> bool:
        """尝试获取排他锁"""
        if resource not in self.locks:
            self.locks[resource] = txn
            return True
        if self.locks[resource] == txn:
            return True  # 已持有
        self.waits_for[txn] = resource
        return False  # 需等待

    def release(self, txn: str, resource: str):
        if self.locks.get(resource) == txn:
            del self.locks[resource]

    def release_all(self, txn: str):
        to_del = [r for r, h in self.locks.items() if h == txn]
        for r in to_del:
            del self.locks[r]

    def detect_deadlock(self) -> list | None:
        """等待图环检测"""
        # 构建等待图: txn → txn (等待持有者)
        graph: dict[str, str] = {}
        for waiter, resource in self.waits_for.items():
            holder = self.locks.get(resource)
            if holder and holder != waiter:
                graph[waiter] = holder
        # DFS 找环
        visited = set()
        stack = set()

        def has_cycle(node, path):
            if node in stack:
                return path[path.index(node):] + [node]
            if node in visited:
                return None
            visited.add(node)
            stack.add(node)
            if node in graph:
                cycle = has_cycle(graph[node], path + [node])
                if cycle:
                    return cycle
            stack.discard(node)
            return None

        for node in graph:
            result = has_cycle(node, [])
            if result:
                return result
        return None


# ============ 4. 列存 vs 行存 ============

class RowStore:
    """行存储"""
    def __init__(self, schema: list[str]):
        self.schema = schema
        self.rows: list[tuple] = []

    def insert(self, row: tuple):
        self.rows.append(row)

    def scan_column(self, col_idx: int) -> list:
        """扫描某列（需读全行）"""
        return [row[col_idx] for row in self.rows]


class ColumnStore:
    """列存储（每列独立数组）"""
    def __init__(self, schema: list[str]):
        self.schema = schema
        self.columns: dict[str, list] = {name: [] for name in schema}

    def insert(self, row: tuple):
        for i, name in enumerate(self.schema):
            self.columns[name].append(row[i])

    def scan_column(self, col_name: str) -> list:
        """只读目标列（IO 精确）"""
        return self.columns[col_name]


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Database Systems: 关系代数 + B+树 + 2PL + 列存")
    print("=" * 60)
    random.seed(42)

    # 1. 关系代数
    print("\n📋 1. 关系代数")
    students = Relation("Students", ["sid", "name", "dept"],
                        [(1, "Alice", "CS"), (2, "Bob", "EE"), (3, "Carol", "CS")])
    enroll = Relation("Enroll", ["sid", "course"],
                      [(1, "DB"), (1, "ML"), (2, "DB"), (3, "OS")])
    print(students)
    # σ dept=CS
    cs = students.select(lambda t: t[2] == "CS")
    print(f"\n  σ dept='CS':")
    print(cs)
    # ⨝
    joined = Relation.join(students, enroll, 0, 0)
    cs_courses = joined.select(lambda t: t[2] == "CS").project([1, 4])
    print(f"\n  π(name, course) [σ dept=CS ⨝ Enroll]:")
    print(cs_courses)

    # 2. B+ 树
    print("\n📋 2. B+ 树索引")
    tree = BPlusTree(order=4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17, 25, 3, 1]:
        tree.insert(k, f"val{k}")
    result = tree.range_query(7, 20)
    print(f"   插入 11 个键")
    print(f"   range_query(7, 20) = {sorted(result)}")

    # 3. 2PL
    print("\n📋 3. 两阶段锁 (2PL) + 死锁检测")
    lm = LockManager()
    # T1 锁 A, T2 锁 B, T1 等 B, T2 等 A → 死锁
    print(f"   T1 acquire(A): {lm.acquire('T1', 'A')}")
    print(f"   T2 acquire(B): {lm.acquire('T2', 'B')}")
    print(f"   T1 acquire(B): {lm.acquire('T1', 'B')} (等待)")
    print(f"   T2 acquire(A): {lm.acquire('T2', 'A')} (等待)")
    cycle = lm.detect_deadlock()
    print(f"   死锁检测: {'环 ' + str(cycle) if cycle else '无'}")
    print(f"   → 牺牲一个事务(victim)打破死锁")

    # 4. 列存 vs 行存
    print("\n📋 4. 列存 vs 行存 (OLAP 扫描)")
    schema = ["id", "name", "dept", "salary"]
    rs = RowStore(schema)
    cs = ColumnStore(schema)
    N = 10000
    for i in range(N):
        row = (i, f"emp{i}", random.choice(["CS", "EE", "ME"]), random.randint(40, 200))
        rs.insert(row)
        cs.insert(row)

    # 只查 salary 列
    rs_salaries = rs.scan_column(3)
    cs_salaries = cs.scan_column("salary")
    # 模拟 IO 量
    row_io = N * 4  # 读全部列
    col_io = N  # 只读一列
    print(f"   {N} 行 × {len(schema)} 列")
    print(f"   行存扫描 salary 列: 读取 {row_io} 个值 (全部列)")
    print(f"   列存扫描 salary 列: 读取 {col_io} 个值 (仅目标列)")
    print(f"   → 列存 IO 减少为行存的 {col_io/row_io:.0%}")

    # 反直觉
    print("\n💡 反直觉发现：列存在 OLAP 中 IO 减少 75%+")
    print(f"   查 1 列，行存读 4 列，列存只读 1 列 → 4x IO 节省")
    print(f"   这就是 ClickHouse / Vertica / Parquet 的核心优势。")

    print("\n✅ Database Systems 完成！")


if __name__ == "__main__":
    demo()
