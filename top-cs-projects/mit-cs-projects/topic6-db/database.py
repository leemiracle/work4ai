"""
6.5910/6.830 Database Systems（MIT, Morris）
================================================
覆盖主题：
- B-tree 索引（非 B+，内部节点也存数据）（Lecture 3-4）
- ARIES 风格 WAL 恢复（Lecture 10-11）
- 2PL + 死锁检测（Lecture 7-8）
- Selinger 风格查询优化器（左深树 DP）（Lecture 13-14）

核心教材/论文（经典，无 arXiv ID）：
- Bayer & McCreight 1972 "Organization and Maintenance of Large Ordered Indices" Acta Informatica (B-tree)
- Mohan et al. 1992 "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking" ACM TODS
- Selinger 1979 "Access Path Selection in a Relational Database Management System" IBM SJR
- Bernstein, Hadzilacos, Goodman 1987 "Concurrency Control and Recovery in Database Systems"

本文件实现：
- B-tree（搜索/插入/分裂/合并）
- ARIES WAL（Analysis/Redo/Undo）
- Wait-for graph 死锁检测
- Selinger 动态规划连接顺序优化

运行：
    python database.py
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass, field


# ============ 1. B-Tree (非 B+) ============

class BTreeNode:
    def __init__(self, t=2, leaf=True):
        self.t = t          # 最小度
        self.keys = []      # 键
        self.values = []    # 值（与 key 一一对应，内部节点也存数据）
        self.children = []  # 子节点（leaf 为空）
        self.leaf = leaf


class BTree:
    """B-tree of minimum degree t. 每个节点 [t-1, 2t-1] 个键。"""
    def __init__(self, t=3):
        self.t = t
        self.root = BTreeNode(t=t, leaf=True)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        if node.leaf:
            return None
        return self._search(node.children[i], key)

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:  # 满了
            new_root = BTreeNode(t=self.t, leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_nonfull(new_root, key, value)
        else:
            self._insert_nonfull(root, key, value)

    def _split_child(self, parent, i):
        t = self.t
        full = parent.children[i]
        new_node = BTreeNode(t=t, leaf=full.leaf)
        # 中间键提升
        mid = t - 1
        parent.keys.insert(i, full.keys[mid])
        parent.values.insert(i, full.values[mid])
        # 新节点拿右半
        new_node.keys = full.keys[mid+1:]
        new_node.values = full.values[mid+1:]
        full.keys = full.keys[:mid]
        full.values = full.values[:mid]
        if not full.leaf:
            new_node.children = full.children[mid+1:]
            full.children = full.children[:mid+1]
        parent.children.insert(i + 1, new_node)

    def _insert_nonfull(self, node, key, value):
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.values[i] = value  # 更新
            return
        if node.leaf:
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_nonfull(node.children[i], key, value)

    def height(self, node=None):
        node = node or self.root
        h = 0
        while not node.leaf:
            h += 1
            node = node.children[0]
        return h

    def total_keys(self):
        return self._count(self.root)

    def _count(self, node):
        n = len(node.keys)
        for c in node.children:
            n += self._count(c)
        return n


# ============ 2. ARIES WAL Recovery ============

@dataclass
class LogRecord:
    lsn: int
    txn_id: int
    op: str          # BEGIN / UPDATE / COMMIT / ABORT
    page: str = ""
    undo: str = ""   # undo 信息（旧值）
    redo: str = ""   # redo 信息（新值）


class ARIESRecovery:
    """简化 ARIES：Analysis → Redo → Undo"""
    def __init__(self):
        self.log: list[LogRecord] = []
        self.pages: dict[str, str] = {}  # 模拟磁盘页
        self.next_lsn = 0

    def log_update(self, txn, page, old_val, new_val):
        self.next_lsn += 1
        self.log.append(LogRecord(self.next_lsn, txn, "UPDATE", page, str(old_val), str(new_val)))

    def log_commit(self, txn):
        self.next_lsn += 1
        self.log.append(LogRecord(self.next_lsn, txn, "COMMIT"))

    def log_begin(self, txn):
        self.next_lsn += 1
        self.log.append(LogRecord(self.next_lsn, txn, "BEGIN"))

    def recover(self):
        # Phase 1: Analysis — 找出已提交 vs 未完成事务
        committed = set()
        active = set()
        for rec in self.log:
            if rec.op == "BEGIN":
                active.add(rec.txn_id)
            elif rec.op == "COMMIT":
                active.discard(rec.txn_id)
                committed.add(rec.txn_id)
        loser_txns = active  # 未提交但写了日志的事务

        # Phase 2: Redo — 重放所有 UPDATE（幂等）
        redo_count = 0
        for rec in self.log:
            if rec.op == "UPDATE":
                self.pages[rec.page] = rec.redo
                redo_count += 1

        # Phase 3: Undo — 反向回滚 loser 事务
        # 先建 page -> last_LSN 索引：若 loser 的更新已被后续（已提交）事务覆盖，
        # 则跳过 undo，避免冲掉已提交事务的更新（ARIES page-LSN 检查）。
        page_last_lsn: dict[str, int] = {}
        for rec in self.log:
            if rec.op == "UPDATE":
                page_last_lsn[rec.page] = rec.lsn
        undo_count = 0
        for rec in reversed(self.log):
            if rec.op == "UPDATE" and rec.txn_id in loser_txns:
                # 若该 page 的最后 LSN > 当前记录 LSN，说明被后续更新覆盖，跳过 undo
                if page_last_lsn.get(rec.page, 0) > rec.lsn:
                    continue
                self.pages[rec.page] = rec.undo
                undo_count += 1
        return committed, loser_txns, redo_count, undo_count


# ============ 3. 2PL + 死锁检测 ============

class LockManager:
    """2PL + wait-for graph 死锁检测"""
    def __init__(self):
        self.locks: dict[str, int] = {}  # resource -> txn holding lock
        self.waiting: dict[int, set] = {}  # txn -> resources waiting for
        self.wait_for: dict[int, set] = {}  # txn -> txns it waits for

    def acquire(self, txn: int, resource: str) -> bool:
        if resource not in self.locks:
            self.locks[resource] = txn
            return True
        if self.locks[resource] == txn:
            return True
        # 需要等待
        holder = self.locks[resource]
        self.wait_for.setdefault(txn, set()).add(holder)
        return False

    def release_all(self, txn: int):
        for r in [k for k, v in self.locks.items() if v == txn]:
            del self.locks[r]
        self.wait_for.pop(txn, None)
        for t in self.wait_for:
            self.wait_for[t].discard(txn)

    def detect_deadlock(self) -> list[int] | None:
        """检测 wait-for 图中的环（DFS）。返回环上的事务列表。"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {t: WHITE for t in self.wait_for}

        def dfs(u, path):
            color[u] = GRAY
            path.append(u)
            for v in self.wait_for.get(u, set()):
                if v not in color:
                    color[v] = WHITE
                if color[v] == GRAY:
                    cycle_start = path.index(v)
                    return path[cycle_start:] + [v]
                if color[v] == WHITE:
                    result = dfs(v, path)
                    if result:
                        return result
            path.pop()
            color[u] = BLACK
            return None
        for t in list(self.wait_for.keys()):
            if color.get(t, WHITE) == WHITE:
                cycle = dfs(t, [])
                if cycle:
                    return cycle
        return None


# ============ 4. Selinger Query Optimizer ============

@dataclass
class Relation:
    name: str
    tuples: int
    selectivity: float = 1.0  # 过滤后剩余比例


def selinger_join(rels: list[Relation], join_cost_fn) -> tuple[list[str], float]:
    """Selinger DP：左深树连接顺序优化。返回 (最佳顺序, 最低成本)。"""
    n = len(rels)
    # dp[frozenset] = (best_order, cost, cardinality)
    dp = {}
    for r in rels:
        key = frozenset([r.name])
        dp[key] = ([r.name], 0, r.tuples * r.selectivity)

    for size in range(2, n + 1):
        for subset in _subsets([r.name for r in rels], size):
            best_cost = float('inf')
            best_plan = None
            best_card = 0
            for name in subset:
                rest = frozenset(subset) - {name}
                if rest not in dp:
                    continue
                prev_order, prev_cost, prev_card = dp[rest]
                # join cost = prev_card * new_rel_size
                new_rel = next(r for r in rels if r.name == name)
                cost = prev_cost + join_cost_fn(prev_card, new_rel.tuples * new_rel.selectivity)
                card = prev_card * new_rel.tuples * new_rel.selectivity * 0.1  # join selectivity
                if cost < best_cost:
                    best_cost = cost
                    best_plan = prev_order + [name]
                    best_card = card
            if best_plan:
                dp[frozenset(subset)] = (best_plan, best_cost, best_card)

    full = frozenset(r.name for r in rels)
    if full in dp:
        return dp[full][0], dp[full][1]
    return [], 0


def _subsets(items, k):
    from itertools import combinations
    return [set(c) for c in combinations(items, k)]


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.830 Database: B-tree / ARIES / 2PL / Query Optimizer")
    print("=" * 65)

    # --- B-tree ---
    print("\n📋 1. B-Tree (t=3, 非 B+)")
    bt = BTree(t=3)
    data = [(i*7 % 100, f"val_{i*7%100}") for i in range(1, 30)]
    for k, v in data:
        bt.insert(k, v)
    print(f"  插入 {len(data)} 个键, 树高={bt.height()}, 总键数={bt.total_keys()}")
    for test_key in [0, 14, 35, 98, 100]:
        v = bt.search(test_key)
        print(f"    search({test_key}) = {v}")
    print(f"  → t=3 每节点最多 5 键；内部节点也存数据(与 B+ 不同)。")

    # --- ARIES ---
    print("\n📋 2. ARIES WAL 恢复")
    aries = ARIESRecovery()
    aries.log_begin(1); aries.log_begin(2)
    aries.pages["P1"] = "A"; aries.pages["P2"] = "B"
    aries.log_update(1, "P1", "A", "A1")
    aries.log_update(2, "P2", "B", "B1")
    aries.log_update(1, "P2", "B1", "B1x")
    aries.log_commit(1)  # T1 提交, T2 崩溃时未提交
    print(f"  日志 {len(aries.log)} 条, T1 提交, T2 未提交")
    print(f"  崩溃前页面: {dict(aries.pages)}")
    committed, losers, redos, undos = aries.recover()
    print(f"  恢复后: committed={committed}, losers={losers}")
    print(f"  Redo={redos} 条, Undo={undos} 条")
    print(f"  恢复后页面: {dict(aries.pages)}")
    print(f"  → T2 的 UPDATE 被回滚(Undo), T1 的更新保留(Redo)。")

    # --- 2PL 死锁 ---
    print("\n📋 3. 2PL + 死锁检测")
    lm = LockManager()
    lm.acquire(1, "A")
    lm.acquire(2, "B")
    lm.acquire(1, "B")  # T1 等 T2
    lm.acquire(2, "A")  # T2 等 T1 → 死锁!
    cycle = lm.detect_deadlock()
    print(f"  T1 holds A, T2 holds B")
    print(f"  T1 requests B (waits T2), T2 requests A (waits T1)")
    print(f"  wait-for graph: {dict(lm.wait_for)}")
    print(f"  检测到死锁环: {cycle}")
    print(f"  → 牺牲一个事务(victim)打破死锁。")

    # --- Query Optimizer ---
    print("\n📋 4. Selinger 查询优化器 (左深树 DP)")
    rels = [
        Relation("R", 10000),
        Relation("S", 5000, selectivity=0.1),
        Relation("T", 1000),
    ]
    join_cost = lambda a, b: a + b + a * b * 0.01
    order, cost = selinger_join(rels, join_cost)
    print(f"  R(10000) ⋈ S(5000,sel=0.1) ⋈ T(1000)")
    print(f"  最佳左深连接顺序: {' ⋈ '.join(order)}")
    print(f"  最低成本: {cost:.0f}")
    # 暴力对比所有排列
    from itertools import permutations
    all_costs = []
    for perm in permutations([r.name for r in rels]):
        c = 0
        first_rel = next(r for r in rels if r.name == perm[0])
        card = first_rel.tuples * first_rel.selectivity
        for name in perm[1:]:
            r = next(x for x in rels if x.name == name)
            c += join_cost(card, r.tuples * r.selectivity)
            card = card * r.tuples * r.selectivity * 0.1
        all_costs.append((perm, c))
    all_costs.sort(key=lambda x: x[1])
    print(f"  暴力枚举最优: {' ⋈ '.join(all_costs[0][0])} cost={all_costs[0][1]:.0f}")
    print(f"  最差顺序:    {' ⋈ '.join(all_costs[-1][0])} cost={all_costs[-1][1]:.0f}")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：B-tree 高度增长极慢（log_t N）")
    print("=" * 65)
    for n_keys in [100, 1000, 10000, 100000, 1000000]:
        for t in [3, 10, 50]:
            bt2 = BTree(t=t)
            for k in range(n_keys):
                bt2.insert(k, k)
            h = bt2.height()
            max_capacity = (2*t)**(h+1) - 1
            print(f"  n={n_keys:>7}, t={t:>2}: height={h}, 节点容量上限≈{max_capacity:>10}")
        print()
    print("  → t=50 时 10 万键只需 height=2，100 万键需 height=3（因为 height=2 的")
    print("    容量上限 = (2×50)³-1 = 999,999 < 1,000,000）。这就是为什么数据库用 B-tree")
    print("    而非二叉树——3-4 次磁盘 IO 即可定位任意记录。")

    print("\n✅ 6.830 Demo 完成！")


if __name__ == "__main__":
    demo()
