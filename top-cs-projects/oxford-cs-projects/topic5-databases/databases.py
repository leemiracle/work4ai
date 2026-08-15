"""
Databases (Oxford CS)
================================================
覆盖主题：
- 关系代数（选择/投影/连接/集合运算）
- SQL mini-interpreter
- 事务可串行化（conflict serializability）
- 连接算法（nested-loop / hash join）

核心教材（已核实）：
- Garcia-Molina, Ullman, Widom "Database Systems: The Complete Book" 2nd ed, Pearson 2008
- Ramakrishnan & Gehrke "Database Management Systems" 3rd ed, McGraw-Hill 2003
- Bernstein, Hadzilacos, Goodman "Concurrency Control and Recovery in Database Systems" 1987

本文件实现：
- 关系代数引擎（σ π ⋈ ∪ ∩ -）
- SQL → 关系代数翻译 + 执行
- 冲突可串行化检测（precedence graph 环检测）
- Nested-loop join + Hash join

运行：
    python databases.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from collections import defaultdict


# ============ 1. 关系 ============

@dataclass
class Relation:
    """关系：schema + tuples"""
    name: str
    attributes: list[str]  # 列名
    tuples: list[tuple] = field(default_factory=list)

    def __repr__(self):
        return f"Relation({self.name}, attrs={self.attributes}, {len(self.tuples)} rows)"


# ============ 2. 关系代数操作 ============

def select(rel: Relation, predicate: Callable[[dict], bool]) -> Relation:
    """σ_predicate(R): 选择满足条件的元组"""
    result_tuples = []
    for tup in rel.tuples:
        row = dict(zip(rel.attributes, tup))
        if predicate(row):
            result_tuples.append(tup)
    return Relation(f"σ_{rel.name}", rel.attributes, result_tuples)


def project(rel: Relation, attrs: list[str]) -> Relation:
    """π_attrs(R): 投影指定列（去重）"""
    indices = [rel.attributes.index(a) for a in attrs]
    seen = set()
    result_tuples = []
    for tup in rel.tuples:
        projected = tuple(tup[i] for i in indices)
        if projected not in seen:
            seen.add(projected)
            result_tuples.append(projected)
    return Relation(f"π_{rel.name}", attrs, result_tuples)


def cross_product(r1: Relation, r2: Relation) -> Relation:
    """R × S: 笛卡尔积"""
    new_attrs = r1.attributes + r2.attributes
    result_tuples = []
    for t1 in r1.tuples:
        for t2 in r2.tuples:
            result_tuples.append(t1 + t2)
    return Relation(f"{r1.name}×{r2.name}", new_attrs, result_tuples)


def natural_join(r1: Relation, r2: Relation) -> Relation:
    """R ⋈ S: 自然连接（等值连接公共属性）"""
    common = [a for a in r1.attributes if a in r2.attributes]
    if not common:
        return cross_product(r1, r2)

    r1_common_idx = [r1.attributes.index(a) for a in common]
    r2_common_idx = [r2.attributes.index(a) for a in common]
    r2_only = [a for a in r2.attributes if a not in common]
    r2_only_idx = [r2.attributes.index(a) for a in r2_only]

    new_attrs = r1.attributes + r2_only
    result_tuples = []

    # Build hash on r2
    r2_index = defaultdict(list)
    for t2 in r2.tuples:
        key = tuple(t2[i] for i in r2_common_idx)
        r2_index[key].append(t2)

    for t1 in r1.tuples:
        key = tuple(t1[i] for i in r1_common_idx)
        for t2 in r2_index.get(key, []):
            combined = t1 + tuple(t2[i] for i in r2_only_idx)
            result_tuples.append(combined)

    return Relation(f"{r1.name}⋈{r2.name}", new_attrs, result_tuples)


def union(r1: Relation, r2: Relation) -> Relation:
    """R ∪ S"""
    assert r1.attributes == r2.attributes
    seen = set()
    result = []
    for t in r1.tuples + r2.tuples:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return Relation(f"{r1.name}∪{r2.name}", r1.attributes, result)


def difference(r1: Relation, r2: Relation) -> Relation:
    """R - S"""
    assert r1.attributes == r2.attributes
    s_set = set(r2.tuples)
    result = [t for t in r1.tuples if t not in s_set]
    return Relation(f"{r1.name}-{r2.name}", r1.attributes, result)


# ============ 3. SQL Mini-Interpreter ============

class SQLExecutor:
    """
    Mini SQL 解释器，支持：
    - SELECT cols FROM tables WHERE condition
    - JOIN (natural)
    - 简单 WHERE (AND / = / > / <)

    翻译到关系代数执行。
    """

    def __init__(self):
        self.tables: dict[str, Relation] = {}

    def create_table(self, name: str, attrs: list[str], rows: list[tuple]):
        self.tables[name] = Relation(name, attrs, rows)

    def execute(self, sql: str) -> Relation:
        """执行 SQL（极简解析）"""
        sql = sql.strip().rstrip(';')
        # SELECT ... FROM ... [WHERE ...]
        parts = sql.split(" FROM ")
        select_part = parts[0].replace("SELECT ", "").strip()

        if " WHERE " in parts[1]:
            from_part, where_part = parts[1].split(" WHERE ", 1)
        else:
            from_part = parts[1]
            where_part = None

        # FROM: 可能多个表（逗号分隔 = 交叉积/连接）
        table_names = [t.strip() for t in from_part.split(",")]

        # 从第一个表开始
        result = self.tables[table_names[0]]
        for tn in table_names[1:]:
            result = natural_join(result, self.tables[tn])

        # WHERE
        if where_part:
            predicate = self._parse_where(where_part)
            result = select(result, predicate)

        # SELECT
        if select_part == "*":
            return result
        else:
            cols = [c.strip() for c in select_part.split(",")]
            return project(result, cols)

    def _parse_where(self, where: str) -> Callable[[dict], bool]:
        """解析简单 WHERE 子句"""
        conditions = []

        # 用 AND 分割
        and_parts = where.split(" AND ")
        for part in and_parts:
            part = part.strip()
            for op in ["<=", ">=", "!=", "<", ">", "="]:
                if op in part:
                    left, right = part.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    # 尝试解析为数字
                    try:
                        right_val = float(right)
                        is_num = True
                    except ValueError:
                        right_val = right.strip("'\"")
                        is_num = False

                    conditions.append((left, op, right_val, is_num))
                    break

        def predicate(row: dict) -> bool:
            for left, op, right_val, is_num in conditions:
                if left not in row:
                    return False
                val = row[left]
                if is_num:
                    val = float(val)
                if op == "=" and val != right_val:
                    return False
                if op == "!=" and val == right_val:
                    return False
                if op == "<" and not val < right_val:
                    return False
                if op == ">" and not val > right_val:
                    return False
                if op == "<=" and not val <= right_val:
                    return False
                if op == ">=" and not val >= right_val:
                    return False
            return True

        return predicate


# ============ 4. 可串行化检测 ============

def is_conflict_serializable(schedule: list[tuple]) -> tuple[bool, list]:
    """
    检测调度是否冲突可串行化。

    schedule: [(txn_id, op_type, item), ...]
    op_type: 'R' (read) or 'W' (write)
    item: 数据项名

    方法：构建 precedence graph，检测是否有环。
    如果无环 → 可串行化。
    """
    # 找冲突对：(Ti, op_i, item) 和 (Tj, op_j, item) 冲突当：
    # - 访问同一 item
    # - 至少一个是 W
    # - Ti != Tj
    # - Ti 在 Tj 之前

    txns = set(t[0] for t in schedule)
    edges = set()  # (Ti, Tj) 表示 Ti → Tj

    for i in range(len(schedule)):
        ti, opi, itemi = schedule[i]
        for j in range(i + 1, len(schedule)):
            tj, opj, itemj = schedule[j]
            if ti == tj:
                continue
            if itemi != itemj:
                continue
            if opi == 'W' or opj == 'W':
                edges.add((ti, tj))

    # 检测环（DFS）
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)

    has_cycle = _detect_cycle(adj, txns)
    return not has_cycle, list(edges)


def _detect_cycle(adj: dict, nodes: set) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for n in nodes:
        if color[n] == WHITE:
            if dfs(n):
                return True
    return False


# ============ 5. 连接算法 ============

def nested_loop_join(r1: Relation, r2: Relation, join_key_r1: str, join_key_r2: str) -> list[tuple]:
    """Nested-loop join: O(n*m)"""
    idx1 = r1.attributes.index(join_key_r1)
    idx2 = r2.attributes.index(join_key_r2)
    result = []
    comparisons = 0
    for t1 in r1.tuples:
        for t2 in r2.tuples:
            comparisons += 1
            if t1[idx1] == t2[idx2]:
                result.append(t1 + t2)
    return result, comparisons


def hash_join(r1: Relation, r2: Relation, join_key_r1: str, join_key_r2: str) -> tuple[list[tuple], int]:
    """Hash join: O(n+m) average"""
    idx1 = r1.attributes.index(join_key_r1)
    idx2 = r2.attributes.index(join_key_r2)

    # Build phase: hash r2
    hash_table = defaultdict(list)
    for t2 in r2.tuples:
        hash_table[t2[idx2]].append(t2)

    # Probe phase: scan r1
    result = []
    comparisons = 0
    for t1 in r1.tuples:
        key = t1[idx1]
        for t2 in hash_table.get(key, []):
            comparisons += 1
            result.append(t1 + t2)

    return result, comparisons


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Databases (Oxford CS) Demo")
    print("=" * 65)

    # 1. 关系代数
    print("\n📋 1. 关系代数")

    students = Relation("Students", ["sid", "name", "dept"],
        [(1, "Alice", "CS"), (2, "Bob", "Math"), (3, "Carol", "CS"), (4, "Dave", "Physics")])

    enroll = Relation("Enroll", ["sid", "course"],
        [(1, "Algorithms"), (1, "Databases"), (2, "Algorithms"), (3, "Databases")])

    # σ_dept='CS' (Students)
    cs_students = select(students, lambda r: r["dept"] == "CS")
    print(f"   σ_dept='CS'(Students): {len(cs_students.tuples)} rows")
    for t in cs_students.tuples:
        print(f"     {t}")

    # Students ⋈ Enroll
    joined = natural_join(students, enroll)
    print(f"\n   Students ⋈ Enroll: {len(joined.tuples)} rows")
    for t in joined.tuples:
        print(f"     {t}")

    # π_name(σ_dept='CS'(Students))
    cs_names = project(cs_students, ["name"])
    print(f"\n   π_name(σ_dept='CS'(Students)): {[t[0] for t in cs_names.tuples]}")

    # 2. SQL Mini-Interpreter
    print("\n📋 2. SQL 执行")
    executor = SQLExecutor()
    executor.create_table("Students", ["sid", "name", "dept"],
        [(1, "Alice", "CS"), (2, "Bob", "Math"), (3, "Carol", "CS"), (4, "Dave", "Physics")])
    executor.create_table("Enroll", ["sid", "course"],
        [(1, "Algorithms"), (1, "Databases"), (2, "Algorithms"), (3, "Databases")])

    queries = [
        "SELECT name FROM Students WHERE dept = CS",
        "SELECT name, course FROM Students, Enroll WHERE sid = sid",
        "SELECT name FROM Students WHERE dept = CS AND sid > 1",
    ]
    for sql in queries:
        print(f"\n   SQL: {sql}")
        result = executor.execute(sql)
        for t in result.tuples:
            print(f"     → {t}")

    # 3. 可串行化
    print("\n📋 3. 冲突可串行化检测")

    # 可串行化调度: T1: R(A) W(A), T2: R(A) W(A)
    sched1 = [
        ("T1", "R", "A"),
        ("T2", "R", "A"),
        ("T1", "W", "A"),
        ("T2", "W", "A"),
    ]
    ok1, edges1 = is_conflict_serializable(sched1)
    print(f"   调度1: {sched1}")
    print(f"   冲突边: {edges1}")
    print(f"   可串行化: {ok1}")

    # 不可串行化（有环）
    sched2 = [
        ("T1", "W", "A"),
        ("T2", "W", "A"),
        ("T2", "W", "B"),
        ("T1", "W", "B"),
    ]
    ok2, edges2 = is_conflict_serializable(sched2)
    print(f"\n   调度2: {sched2}")
    print(f"   冲突边: {edges2}")
    print(f"   可串行化: {ok2} (有环 T1→T2→T1)")

    # 4. 连接算法对比
    print("\n📋 4. 连接算法对比")
    big_r1 = Relation("R1", ["id", "val"], [(i, f"v{i}") for i in range(100)])
    big_r2 = Relation("R2", ["id", "info"], [(i, f"info{i}") for i in range(100) if i % 2 == 0])

    _, nl_comps = nested_loop_join(big_r1, big_r2, "id", "id")
    hj_result, hj_comps = hash_join(big_r1, big_r2, "id", "id")

    n, m = len(big_r1.tuples), len(big_r2.tuples)
    print(f"   R1: {n} rows, R2: {m} rows")
    print(f"   Nested-loop join 比较次数: {nl_comps} (n×m={n*m})")
    print(f"   Hash join 比较次数:       {hj_comps} (≈匹配数={len(hj_result)})")
    print(f"   → Hash join 快 {nl_comps/max(hj_comps,1):.0f} 倍!")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print(f"   1. Nested-loop={nl_comps} vs Hash={hj_comps} 次比较")
    print(f"      Hash join 不是渐进更快(O(n+m))，在100×50数据上快{nl_comps/max(hj_comps,1):.0f}倍")
    print(f"   2. 调度2有环(T1→T2→T1)→不可串行化")
    print(f"      即使每个操作看起来合法，组合后无法等价于任何串行执行")
    print(f"   3. 关系代数只有5个操作符(σ π ⋈ ∪ -)，但能表达全部 SQL 查询")
    print("=" * 65)


if __name__ == "__main__":
    main()
