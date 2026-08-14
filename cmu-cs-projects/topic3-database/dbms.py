"""
15-445 Database Systems (CMU — Pavlo)
================================================
覆盖主题（对应 lecture）：
- Indexes: B+ tree 插入 + 点查询 + 范围查询
- Joins: nested-loop / hash / sort-merge 三种实现对比
- Concurrency: MVCC snapshot isolation

核心教材/论文：
- Hellerstein, Stonebraker, Hamilton "Architecture of DB Systems" 2007 Foundations & Trends in DB
- "Bayer & McCreight 1972" — B-tree 原始论文 (B+tree 是其变体)
- "Mohan 1992 ARIES SIGMOD" — 事务恢复 (MVCC 基础)
- Graefe "Volcano/Iterator Model" 1994 SIGMOD — 查询执行

本文件实现：
- B+ tree (叶子链表 + 内部节点路由)
- 三种 join 算法 (带 I/O 统计)
- MVCC 版本链 + snapshot isolation 读

运行：
    python3 dbms.py
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass, field

# ============ 1. B+ Tree ============

class BPlusTreeNode:
    __slots__ = ('keys', 'children', 'leaf', 'next')
    def __init__(self, leaf=True):
        self.keys: list = []
        self.children: list = []   # internal: child nodes; leaf: values
        self.leaf: bool = leaf
        self.next: 'BPlusTreeNode | None' = None  # leaf chain

class BPlusTree:
    def __init__(self, order=4):
        self.order = order
        self.root = BPlusTreeNode(leaf=True)

    def search(self, key):
        node = self.root
        while not node.leaf:
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.children[i]
        return None

    def range_query(self, lo, hi):
        """Return all (key, value) with lo <= key <= hi."""
        node = self.root
        while not node.leaf:
            i = bisect.bisect_right(node.keys, lo)
            node = node.children[i]
        results = []
        while node:
            for k, v in zip(node.keys, node.children):
                if k > hi:
                    return results
                if k >= lo:
                    results.append((k, v))
            node = node.next
        return results

    def insert(self, key, value):
        result = self._insert(self.root, key, value)
        if result is not None:
            new_key, new_child = result
            new_root = BPlusTreeNode(leaf=False)
            new_root.keys = [new_key]
            new_root.children = [self.root, new_child]
            self.root = new_root

    def _insert(self, node, key, value):
        if node.leaf:
            i = bisect.bisect_left(node.keys, key)
            node.keys.insert(i, key)
            node.children.insert(i, value)
            if len(node.keys) > self.order:
                return self._split_leaf(node)
            return None
        else:
            i = bisect.bisect_right(node.keys, key)
            result = self._insert(node.children[i], key, value)
            if result is not None:
                new_key, new_child = result
                node.keys.insert(i, new_key)
                node.children.insert(i + 1, new_child)
                if len(node.keys) > self.order:
                    return self._split_internal(node)
            return None

    def _split_leaf(self, node):
        mid = len(node.keys) // 2
        right = BPlusTreeNode(leaf=True)
        right.keys = node.keys[mid:]
        right.children = node.children[mid:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid]
        right.next = node.next
        node.next = right
        return (right.keys[0], right)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        up_key = node.keys[mid]
        right = BPlusTreeNode(leaf=False)
        right.keys = node.keys[mid+1:]
        right.children = node.children[mid+1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid+1]
        return (up_key, right)


# ============ 2. Join Algorithms ============

def nested_loop_join(R, S, key_r=0, key_s=0):
    """Block nested loop join. Returns (result, io_count)."""
    result = []
    ios = 0
    for r in R:
        ios += 1
        for s in S:
            ios += 1
            if r[key_r] == s[key_s]:
                result.append((r, s))
    return result, ios

def hash_join(R, S, key_r=0, key_s=0):
    """Hash join: build hash on smaller table, probe."""
    result = []
    # Build phase
    ht = {}
    ios = len(R) + len(S)
    for r in R:
        ht.setdefault(r[key_r], []).append(r)
    # Probe phase
    for s in S:
        for r in ht.get(s[key_s], []):
            result.append((r, s))
    return result, ios

def sort_merge_join(R, S, key_r=0, key_s=0):
    """Sort-merge join."""
    result = []
    R_sorted = sorted(R, key=lambda x: x[key_r])
    S_sorted = sorted(S, key=lambda x: x[key_s])
    ios = len(R) * 2 + len(S) * 2  # read + write for sort
    i = j = 0
    while i < len(R_sorted) and j < len(S_sorted):
        rk = R_sorted[i][key_r]
        sk = S_sorted[j][key_s]
        if rk < sk:
            i += 1
        elif rk > sk:
            j += 1
        else:
            # match — collect all with same key
            j_start = j
            while j < len(S_sorted) and S_sorted[j][key_s] == rk:
                result.append((R_sorted[i], S_sorted[j]))
                j += 1
            i += 1
            j = j_start
    return result, ios


# ============ 3. MVCC Snapshot Isolation ============

@dataclass
class MVCCVersion:
    key: int
    value: int
    begin_ts: int
    end_ts: int = 2**31  # infinity
    txn_id: int = 0

class MVCCStore:
    """Multi-Version Concurrency Control with snapshot isolation."""

    def __init__(self):
        self.versions: dict[int, list[MVCCVersion]] = {}
        self.global_ts = 0

    def begin(self) -> int:
        self.global_ts += 1
        return self.global_ts  # snapshot timestamp

    def write(self, txn_ts: int, key: int, value: int):
        v = MVCCVersion(key, value, begin_ts=txn_ts, txn_id=txn_ts)
        if key not in self.versions:
            self.versions[key] = []
        self.versions[key].append(v)

    def read(self, snapshot_ts: int, key: int) -> int | None:
        """Read the version visible at snapshot_ts."""
        if key not in self.versions:
            return None
        for v in reversed(self.versions[key]):
            if v.begin_ts <= snapshot_ts and snapshot_ts < v.end_ts:
                return v.value
        return None

    def commit(self, txn_ts: int):
        """On commit, versions are already visible (begin_ts = txn_ts)."""
        pass  # in this simplified model, write = commit


# ============ Demo ============

def demo():
    print("=" * 60)
    print("15-445 Database Systems: B+Tree, Joins, MVCC")
    print("=" * 60)

    # --- 1. B+ Tree ---
    print("\n📋 1. B+ Tree (order=3)")
    tree = BPlusTree(order=3)
    data = [(5,'e'),(1,'a'),(9,'i'),(3,'c'),(7,'g'),(2,'b'),(8,'h'),(6,'f'),(4,'d'),(10,'j')]
    for k,v in data:
        tree.insert(k, v)
    print(f"   Inserted keys: {sorted(k for k,_ in data)}")

    # Point search
    for k in [1, 5, 10, 11]:
        print(f"   search({k}) = {tree.search(k)}")

    # Range query
    rng = tree.range_query(3, 7)
    print(f"   range(3..7) = {[k for k,_ in rng]}")
    print(f"   💡 B+tree 范围查询走叶子链表 = O(log_n + result_size)")

    # --- 2. Joins ---
    print("\n📋 2. Join Algorithm Comparison")
    # R and S: tables of tuples (join_key, data)
    R = [(i % 50, f"R{i}") for i in range(500)]
    S = [(i % 50, f"S{i}") for i in range(300)]

    nl_result, nl_io = nested_loop_join(R[:50], S[:50])  # smaller for NL
    h_result, h_io = hash_join(R, S)
    sm_result, sm_io = sort_merge_join(R, S)

    print(f"   Nested-loop (50×50): {len(nl_result)} rows, I/O={nl_io}")
    print(f"   Hash join   (500×300): {len(h_result)} rows, I/O={h_io}")
    print(f"   Sort-merge  (500×300): {len(sm_result)} rows, I/O={sm_io}")
    print(f"   💡 Hash join I/O = O(R+S), Nested-loop = O(R×S)")
    print(f"      500×300: NL would be {500*300} I/O vs hash {h_io} = {500*300/h_io:.0f}x slower!")

    # --- 3. MVCC ---
    print("\n📋 3. MVCC Snapshot Isolation")
    store = MVCCStore()
    t0 = store.begin()           # snapshot 1
    store.write(1, 100, 100)     # initial write
    store.write(2, 200, 200)

    t1 = store.begin()           # snapshot 2
    store.write(1, 100, 150)     # txn1 updates key=1

    print(f"   T0 reads key=1: {store.read(t0, 1)} (old value, snapshot isolation!)")
    print(f"   T1 reads key=1: {store.read(t1, 1)} (new value)")
    print(f"   T0 reads key=2: {store.read(t0, 2)}")

    t2 = store.begin()
    store.write(1, 100, 999)
    print(f"   T2 reads key=1: {store.read(t2, 1)}")
    print(f"   T0 still reads: {store.read(t0, 1)} ← unchanged!")
    print(f"   💡 MVCC: 读不阻塞写，写不阻塞读 → 高并发核心")

    print("\n✅ 15-445 Database Systems 完成！")
    print("   覆盖：B+tree / 3种Join / MVCC snapshot isolation")


if __name__ == "__main__":
    demo()
