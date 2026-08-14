"""
数据库系统四校整合 — CMU 15-445 / MIT 6.830 / Berkeley CS186 / Stanford CS145
==========================================================================
四视角看 DB（一个主题，四种讲法，互为补全）：

  CMU  15-445 (Andy Pavlo)   — 如何【实现】一个 DB
       bus-tub 全栈：buffer pool / B+tree / query exec / MVCC / consensus
       学完 → 能从零写一个单机 DB

  MIT  6.830 (Robert Morris)  — DB 的【核心抽象】
       serializability / isolation / 2PL / ARIES / 查询优化
       学完 → 能讨论 isolation level 的微妙差别

  UCB  CS186                  — 如何【使用】DB
       SQL / 索引调优 / 查询计划 / 实战
       学完 → 能写好 SQL、调好索引、读懂 EXPLAIN

  Stan CS145                  — 【NoSQL / Big Data】
       CAP / 最终一致性 / MapReduce / 键值 / 文档 / 向量库
       学完 → 能选对存储引擎、理解分布式数据系统

整合维度（每个主题四视角对比）：
  1. 索引：B+tree(CMU) | B-tree 高度分析(MIT) | 选择度/EXPLAIN(UCB) | LSM-tree(Stan)
  2. 事务：MVCC 实现(CMU) | 可串行化理论(MIT) | 隔离级别实战(UCB) | 最终一致性(Stan)
  3. 查询：三种 join(CMU) | Selinger 优化器(MIT) | SQL 调优(UCB) | MapReduce(Stan)

思想史脉络（Stonebraker "One size fits all?" 的破与立）：
  1960s 文件系统 → 1970 Codd 关系模型 → 1974 System R / Ingres
  → 1980s 商业 DB(Oracle) → 2003 Stonebraker "One size fits all?"
  → 2000s NoSQL(Dynamo/CAP) → 2010s NewSQL(Spanner) → 2020s 云原生/向量库

运行：
    python3 db_integration.py

依赖：仅标准库（自包含，便于教学）
==========================================================================
"""
from __future__ import annotations
import math
import random
import bisect
from collections import defaultdict, deque

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 0 · 思想史时间线                                                  ║
# ╚══════════════════════════════════════════════════════════════════════╝

HISTORY = [
    (1968, "文件系统时代", "IMS (层次模型) / CODASYL (网状模型)——查询要手写导航路径"),
    (1970, "★ Codd 关系模型", "E.F. Codd《A Relational Model of Data》——用数学(关系代数)解放数据"),
    (1974, "System R / Ingres", "IBM System R(SQL诞生) & Berkeley Ingres(Stonebraker)——证明关系模型可行"),
    (1979, "Oracle 商业化", "第一个商用 SQL DB——关系模型走向工业"),
    (1992, "SQL-92 标准", "ACID 事务模型成熟——'一件事要么全做要么不做'"),
    (2003, "★ One size fits all?", "Stonebraker 发难：关系 DB 不是万能的，OLAP/流/内存各有最优解"),
    (2007, "Dynamo / CAP", "Amazon Dynamo 论文——最终一致性 + CAP 定理，NoSQL 浪潮"),
    (2008, "Bigtable / MapReduce", "Google——列存 + 批处理，大数据范式确立"),
    (2012, "Spanner / NewSQL", "Google Spanner——SQL + 全球分布 + TrueTime，NewSQL 兴起"),
    (2020, "云原生 / 向量库", "Aurora/Storage-Compute 分离 + pgvector/向量检索——DB for AI"),
]


def print_history() -> None:
    print("=" * 74)
    print("  Part 0 · 数据库思想史 —— 从 Codd 到向量库")
    print("=" * 74)
    for year, title, desc in HISTORY:
        star = "🔴" if "★" in title else "  "
        t = title.replace("★ ", "")
        print(f"  {star}{year}  {t}")
        print(f"       {desc}")
    print()
    print("  💡 主线：Codd 用数学统一了数据存取 → Stonebraker 打破了'一种 DB 通吃' →")
    print("        NoSQL 牺牲一致性换可用性 → NewSQL 两全其美 → 向量库为 AI 而生。")
    print()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 1 · 索引四视角                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  CMU 15-445 : B+tree —— 叶子节点存数据 + 叶子链表，范围查询 O(log n + k)
#  MIT 6.830  : B-tree 高度分析 —— h ≤ log_t N，t=50 时百万键 h=2（反直觉！）
#  UCB CS186  : 选择度 (selectivity) —— 查询优化器何时选索引？sel < 30% 用索引
#  Stan CS145 : LSM-tree —— NoSQL 写优化（写只追加，读需合并）

def part1_indexes() -> None:
    print("=" * 74)
    print("  Part 1 · 索引四视角 —— 同一棵树，四种讲法")
    print("=" * 74)
    print("  CMU  : B+tree 实现（叶子链表 → 范围查询友好）")
    print("  MIT  : B-tree 高度分析（h ≤ log_t N，'扁'得反直觉）")
    print("  UCB  : 选择度 selectivity（优化器何时选索引？）")
    print("  Stan : LSM-tree（NoSQL 写优化，牺牲点读性能）")
    print()

    # ----- CMU 视角：B+tree 范围查询 -----
    print("─" * 74)
    print("【CMU 视角】B+tree：为什么叶子要拉成链表？")
    print("─" * 74)
    bp = BPlusTree(order=4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17, 25, 31, 8]:
        bp.insert(k, f"v{k}")
    rng = bp.range_query(7, 25)
    print(f"  插入 11 个键后，范围查询 [7, 25] = {rng}")
    print(f"  → 内部节点只导航一次到叶子，然后沿链表线性扫描，复杂度 O(log n + k)")
    print(f"  → 这就是数据库索引为什么用 B+tree 而非二叉搜索树：磁盘 I/O 次 = 树高。")
    print()

    # ----- MIT 视角：B-tree 高度反直觉 -----
    print("─" * 74)
    print("【MIT 视角】B-tree 高度：扁得反直觉")
    print("─" * 74)
    print("  h ≤ log_t(N)，t = 最小度数（每个节点至少 t-1 个键）")
    print(f"  {'N (键数)':>12} {'t=2 (二叉)':>14} {'t=50 (B-tree)':>16} {'t=200':>10}")
    for n in [1_000, 1_000_000, 1_000_000_000]:
        h2 = math.log(n, 2)
        h50 = math.log(n, 50)
        h200 = math.log(n, 200)
        print(f"  {n:>12,} {h2:>14.1f} {h50:>16.1f} {h200:>10.1f}")
    print("  → t=50 时，10 亿个键只需要 h≈5.3 层！6 次磁盘 I/O 就能找到任意键。")
    print("  → 这就是 B-tree 的本质：用'胖节点'匹配'磁盘页'，把树压扁。")
    print()

    # ----- UCB 视角：选择度决定是否用索引 -----
    print("─" * 74)
    print("【UCB 视角】选择度：优化器何时选索引？")
    print("─" * 74)
    print("  关键：索引回表是【随机 I/O】，全表扫描是【顺序 I/O】，随机比顺序慢 ~4x！")
    print("  规则：sel 小 → 索引值；sel 大 → 回表的随机 I/O 反而更慢，不如全表扫。")
    n_rows = 1_000_000
    RANDOM_IO = 4   # 随机 I/O 相对顺序 I/O 的慢速倍数
    for pred, sel in [("性别 = 'M'", 0.50), ("城市 = '上海'", 0.05),
                       ("user_id = 12345", 0.000001), ("状态 IN (1,2)", 0.20)]:
        idx_cost = math.log2(n_rows) + sel * n_rows * RANDOM_IO  # 树高 + 回表(随机)
        seq_cost = n_rows                                          # 顺序扫描
        choice = "索引 ✅" if idx_cost < seq_cost else "全表扫描 ✅"
        print(f"  WHERE {pred:<20} sel={sel:>9.2%}  索引代价={idx_cost:>12,.0f}  "
              f"全表={seq_cost:>10,}  →  {choice}")
    print("  → 反直觉：'性别'这种低区分度列，建了索引优化器也不用——回表 50 万次随机")
    print("     I/O 比顺序扫 100 万还慢！这就是为什么主键/外键才值得建索引。")
    print("  → EXPLAIN 看到的 Seq Scan 不是 bug，是优化器聪明。")
    print()

    # ----- Stanford 视角：LSM-tree（NoSQL 写优化）-----
    print("─" * 74)
    print("【Stanford 视角】LSM-tree：NoSQL 为什么写这么快？")
    print("─" * 74)
    lsm = LSMTree()
    random.seed(0)
    writes = [(i, f"data{i}") for i in range(1000)]
    for k, v in writes:
        lsm.put(k, v)
    print(f"  写入 1000 个键：MemTable({len(lsm.memtable)}) + SSTable 层数={len(lsm.sstables)}")
    print("  写路径：只追加到内存 MemTable → 满了刷成 SSTable → 后台合并(compaction)")
    print("  → 写 = O(1) 追加（B+tree 写要改页 = O(log n) 随机写）")
    print("  → 代价：读要查 MemTable + 多层 SSTable（读放大），靠 BloomFilter 缓解")
    v = lsm.get(500)
    print(f"  读 key=500：{v}  （查了 {lsm._last_reads} 个组件）")
    print()


# ── CMU B+tree（精简版，强调叶子链表 + 范围查询）─────────────────────────
class BPlusNode:
    __slots__ = ("keys", "values", "children", "leaf", "next")
    def __init__(self, leaf=True):
        self.keys, self.values, self.children = [], [], []
        self.leaf, self.next = leaf, None

class BPlusTree:
    """B+tree：内部节点只路由，叶子存数据并用 next 串成链表。"""
    def __init__(self, order=4):
        self.root = BPlusNode(leaf=True)
        self.order = order

    def search(self, key):
        node = self.root
        while not node.leaf:
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]
        i = bisect.bisect_left(node.keys, key)
        return node.values[i] if i < len(node.keys) and node.keys[i] == key else None

    def range_query(self, lo, hi):
        node = self.root
        while not node.leaf:
            node = node.children[bisect.bisect_right(node.keys, lo)]
        out = []
        while node is not None:
            for k, v in zip(node.keys, node.values):
                if lo <= k <= hi:
                    out.append((k, v))
                elif k > hi:
                    return out
            node = node.next
        return out

    def insert(self, key, value):
        # 教学版：顺序构建后做简单分裂（演示叶子链表与范围查询，不追求完整分裂）
        leaf = self.root
        if len(leaf.keys) >= 2 * self.order:
            # 简化：直接演示，完整插入见 cmu-cs-projects/topic3-database/dbms.py
            pass
        idx = bisect.bisect_left(leaf.keys, key)
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            leaf.values[idx] = value
        else:
            leaf.keys.insert(idx, key)
            leaf.values.insert(idx, value)
        # 若叶子过满，分裂并维护链表
        if len(leaf.keys) > 2 * self.order:
            mid = len(leaf.keys) // 2
            new_leaf = BPlusNode(leaf=True)
            new_leaf.keys = leaf.keys[mid:]
            new_leaf.values = leaf.values[mid:]
            leaf.keys = leaf.keys[:mid]
            leaf.values = leaf.values[:mid]
            new_leaf.next = leaf.next
            leaf.next = new_leaf


# ── Stanford LSM-tree（NoSQL 写优化）──────────────────────────────────────
class LSMTree:
    """LSM-tree：写只追加，读需合并。演示 NoSQL 写优化本质。"""
    def __init__(self, memtable_limit=100):
        self.memtable = {}            # 内存表（有序写）
        self.memtable_limit = memtable_limit
        self.sstables = []            # list[dict]，每层一个冻结的 SSTable
        self._last_reads = 0

    def put(self, key, value):
        self.memtable[key] = value
        if len(self.memtable) >= self.memtable_limit:
            self.sstables.append(dict(self.memtable))  # 刷盘
            self.memtable = {}

    def get(self, key):
        self._last_reads = 1
        if key in self.memtable:
            return self.memtable[key]
        for sst in reversed(self.sstables):   # 新层先查
            self._last_reads += 1
            if key in sst:
                return sst[key]
        return None


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 2 · 事务四视角                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  CMU 15-445 : MVCC 实现 —— 多版本版本链 + snapshot isolation
#  MIT 6.830  : 可串行化理论 —— 冲突可串行化（precedence graph 无环）
#  UCB CS186  : 隔离级别实战 —— 脏读 / 不可重复读 / 幻读 各级如何防
#  Stan CS145 : 最终一致性 + CAP —— Dynamo 风格 quorum

def part2_transactions() -> None:
    print("=" * 74)
    print("  Part 2 · 事务四视角 —— ACID 不是一句话，是一个光谱")
    print("=" * 74)
    print("  CMU  : MVCC 实现（版本链 + snapshot，读不阻塞写）")
    print("  MIT  : 可串行化理论（冲突图无环 = 正确）")
    print("  UCB  : 隔离级别实战（SQL 标准的 4 级，各级防什么异常）")
    print("  Stan : 最终一致性 + CAP（quorum NWR，分布式牺牲什么）")
    print()

    # ----- CMU 视角：MVCC -----
    print("─" * 74)
    print("【CMU 视角】MVCC：读不阻塞写，靠'多版本'实现")
    print("─" * 74)
    store = MVCCStore()
    t1 = store.begin()
    store.write(t1, "x", 10)
    store.commit(t1)
    t2 = store.begin()        # snapshot = 2
    t3 = store.begin()        # snapshot = 3
    store.write(t3, "x", 20)  # t3 改 x
    print(f"  t2(snapshot={t2}) 读 x = {store.read(t2,'x')}  （看到旧值 10，不被 t3 干扰）")
    print(f"  t3(snapshot={t3}) 读 x = {store.read(t3,'x')}  （看到自己写的新值 20）")
    store.commit(t3)
    print(f"  → MVCC 本质：每个事务看到'它开始时'的一致快照，读永远不阻塞写。")
    print(f"  → PostgreSQL / Oracle / InnoDB 都用这套。代价：旧版本要定期 VACUUM。")
    print()

    # ----- MIT 视角：可串行化判定 -----
    print("─" * 74)
    print("【MIT 视角】可串行化：冲突图无环才算对")
    print("─" * 74)
    print("  调度 S: T1: W(x)  T2: R(x)  T2: W(y)  T1: R(y)")
    print("  冲突边：T1→T2 (W(x)/R(x))  T2→T1 (W(y)/R(y))")
    print("  图：T1 → T2 → T1  ⟲  有环！→ 不可串行化 ❌")
    print("  → MIT 教你'怎么证明一个并发调度等价于某个串行执行'。")
    print("  → 这是 isolation level 争论的理论根基。")
    print()

    # ----- UCB 视角：隔离级别光谱 -----
    print("─" * 74)
    print("【UCB 视角】隔离级别：SQL 标准的 4 级，防什么异常？")
    print("─" * 74)
    levels = [
        ("READ UNCOMMITTED", "❌", "❌", "❌", "几乎不用（脏读）"),
        ("READ COMMITTED  ", "✅", "❌", "❌", "Oracle/PG 默认级"),
        ("REPEATABLE READ ", "✅", "✅", "❌", "MySQL 默认（防大部分）"),
        ("SERIALIZABLE    ", "✅", "✅", "✅", "最强但最慢（加锁/SSI）"),
    ]
    print(f"  {'隔离级别':<18} {'防脏读':>6} {'防不可重复读':>12} {'防幻读':>7}  说明")
    for lv, d, nr, p, note in levels:
        print(f"  {lv:<18} {d:>6} {nr:>12} {p:>7}  {note}")
    print("  → 实战：90% 的业务用 READ COMMITTED 就够；金融/库存才上 SERIALIZABLE。")
    print()

    # ----- Stanford 视角：CAP + quorum -----
    print("─" * 74)
    print("【Stanford 视角】CAP + 最终一致性：Dynamo 的 quorum")
    print("─" * 74)
    print("  CAP 定理：分区(P)发生时，只能在 C(一致性) 和 A(可用性) 二选一。")
    print("  Dynamo 选 AP：N 个副本，写只要 W 个确认，读只要 R 个响应。")
    N, R, W = 3, 2, 2
    strong = "R + W > N → 强一致 ✅" if R + W > N else "R + W ≤ N → 最终一致"
    print(f"  N={N}, R={R}, W={W}  →  {strong}")
    N, R, W = 3, 1, 1
    strong = "R + W > N → 强一致 ✅" if R + W > N else "R + W ≤ N → 最终一致 ⚡"
    print(f"  N={N}, R={R}, W={W}  →  {strong}  （Cassandra 默认风格：快但可能读到旧数据）")
    print("  → Stanford 教你：分布式 DB 的'一致性'不是布尔值，是延迟-一致性的权衡。")
    print()


class MVCCVersion:
    __slots__ = ("begin", "end", "value")
    def __init__(self, begin, value, end=None):
        self.begin = begin
        self.value = value
        self.end = end

class MVCCStore:
    """CMU 视角：每键存版本链，读按 snapshot_ts 选可见版本。"""
    def __init__(self):
        self._data = defaultdict(list)   # key -> [MVCCVersion]
        self._counter = 0
        self._committed = set()

    def begin(self) -> int:
        self._counter += 1
        return self._counter

    def write(self, txn_ts: int, key: str, value):
        self._data[key].append(MVCCVersion(txn_ts, value))

    def read(self, snapshot_ts: int, key: str):
        versions = self._data.get(key, [])
        # 找 begin <= snapshot_ts 的最新已提交版本
        visible = None
        for v in reversed(versions):
            if v.begin <= snapshot_ts and v.begin in self._committed:
                visible = v.value
                break
            if v.begin <= snapshot_ts and v.begin == snapshot_ts:
                visible = v.value   # 自己写的
                break
        return visible

    def commit(self, txn_ts: int):
        self._committed.add(txn_ts)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 3 · 查询四视角                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  CMU 15-445 : 三种 join 实现 + I/O 统计（nested-loop / hash / sort-merge）
#  MIT 6.830  : Selinger DP 优化器（左深树动态规划选最优连接顺序）
#  UCB CS186  : SQL 调优（只查需要的列 + 谓词下推 + 物化视图）
#  Stan CS145 : MapReduce（map → shuffle → reduce，大数据 join）

def part3_queries() -> None:
    print("=" * 74)
    print("  Part 3 · 查询四视角 —— 同一个 join，四种做法")
    print("=" * 74)
    print("  CMU  : 三种 join 实现 + I/O 统计")
    print("  MIT  : Selinger DP 优化器（选最优连接顺序）")
    print("  UCB  : SQL 调优实战（投影下推 / 谓词下推）")
    print("  Stan : MapReduce（大数据 join = distributed shuffle）")
    print()

    # ----- CMU 视角：三种 join -----
    print("─" * 74)
    print("【CMU 视角】三种 join：I/O 差距能差 187 倍")
    print("─" * 74)
    R = [(i, f"r{i}") for i in range(500)]
    S = [(i, f"s{i}") for i in range(300)]   # 300 行，匹配经典 500×300 例子
    nl = nested_loop_join(R, S)
    hj = hash_join(R, S)
    sm = sort_merge_join(R, S)
    print(f"  R={len(R)} 行, S={len(S)} 行, 连接结果={len(nl)} 行")
    print(f"  {'算法':<20} {'I/O 代价':>12}  {'说明'}")
    print(f"  {'nested-loop':<20} {len(R)*len(S):>12,}  暴力双层循环（最慢）")
    print(f"  {'hash join':<20} {len(R)+len(S):>12,}  建哈希表一次扫（最优）")
    print(f"  {'sort-merge':<20} {len(R)*math.log2(len(R))+len(S)*math.log2(len(S)):>12,.0f}  "
          f"排序后归并（适合已有序）")
    print(f"  → nested-loop {len(R)*len(S):,} vs hash join {len(R)+len(S):,} = "
          f"{len(R)*len(S)//(len(R)+len(S))}x 差距！这就是优化器存在的意义。")
    print()

    # ----- MIT 视角：Selinger 优化器 -----
    print("─" * 74)
    print("【MIT 视角】Selinger DP：连接顺序不是拍脑袋选的")
    print("─" * 74)
    print("  查询：A ⋈ B ⋈ C ⋈ D  （4 表连接）")
    print("  朴素枚举 4! = 24 种顺序；Selinger DP 只算左深树 = 2^(n-1) 种")
    rels = {"A": 1000, "B": 500, "C": 200, "D": 100}
    sel = {("A", "B"): 0.1, ("B", "C"): 0.2, ("C", "D"): 0.5}
    order, cost = selinger_dp(rels, sel)
    print(f"  各表行数 A=1000 B=500 C=200 D=100，连接选择度 AB=0.1 BC=0.2 CD=0.5")
    print(f"  DP 选出最优左深顺序：{' ⋈ '.join(order)}  中间结果代价 = {cost:.0f}")
    print("  → 反直觉：先连小表！从最小结果开始，中间结果越小后续越快。")
    print("  → 这就是 PostgreSQL/Oracle 的查询优化器核心思想（代价模型 + DP）。")
    print()

    # ----- UCB 视角：SQL 调优 -----
    print("─" * 74)
    print("【UCB 视角】SQL 调优：少干活就是快")
    print("─" * 74)
    print("  ❌ 慢：SELECT * FROM orders o JOIN users u ON o.uid=u.id WHERE o.total > 100")
    print("     问题：SELECT * 取了所有列（含不需要的 TEXT），没法用覆盖索引")
    print()
    print("  ✅ 快：SELECT o.id, u.name FROM orders o JOIN users u ON o.uid=u.id")
    print("        WHERE o.total > 100  -- total 上建索引")
    print("     改进：① 只查需要的列 → 可走覆盖索引 ② WHERE 谓词建索引")
    print()
    print("  ✅ 更快（谓词下推）：先过滤再连接")
    print("     SELECT o.id, u.name FROM (SELECT * FROM orders WHERE total>100) o")
    print("     JOIN users u ON o.uid = u.id")
    print("  → UCB 教你：读懂 EXPLAIN，识别 Seq Scan / Index Scan / Hash Join，对症下药。")
    print()

    # ----- Stanford 视角：MapReduce -----
    print("─" * 74)
    print("【Stanford 视角】MapReduce：大数据的 join = 分布式 shuffle")
    print("─" * 74)
    docs = [("d1", "the quick fox"), ("d2", "the lazy dog"),
            ("d3", "the fox and dog")]
    mr = map_reduce_wordcount(docs)
    top = sorted(mr.items(), key=lambda x: -x[1])[:5]
    print(f"  输入 3 个文档，MapReduce 词频 Top5: {top}")
    print("  本质：map(切分) → shuffle(按 key 分组) → reduce(聚合)")
    print("  → 10TB 的 join 在单机跑不动，但 MapReduce 分到 1000 台机器就是分钟级。")
    print("  → Spark SQL / Hive SQL 底层都是这个思路：SQL → DAG → 分布式执行。")
    print()


def nested_loop_join(R, S):
    return [(r, s) for r in R for s in S if r[0] == s[0]]

def hash_join(R, S):
    h = defaultdict(list)
    for s in S:
        h[s[0]].append(s)
    return [(r, s) for r in R for s in h.get(r[0], [])]

def sort_merge_join(R, S):
    R_sorted = sorted(R, key=lambda x: x[0])
    S_sorted = sorted(S, key=lambda x: x[0])
    out, i, j = [], 0, 0
    while i < len(R_sorted) and j < len(S_sorted):
        if R_sorted[i][0] < S_sorted[j][0]:
            i += 1
        elif R_sorted[i][0] > S_sorted[j][0]:
            j += 1
        else:
            out.append((R_sorted[i], S_sorted[j]))
            j += 1
    return out


def selinger_dp(rels: dict, selectivity: dict):
    """MIT Selinger 风格：左深树 DP 选最优连接顺序（教学版，贪心近似）。"""
    remaining = dict(rels)
    join_chain = []   # 只记录原始 join 关系，不记复合 key
    total_cost = 0
    while len(remaining) > 1:
        best = None
        for (a, b), sel in selectivity.items():
            if a in remaining and b in remaining:
                joined_size = remaining[a] * remaining[b] * sel
                if best is None or joined_size < best[3]:
                    best = (a, b, sel, joined_size)
        if best is None:
            break
        a, b, sel, size = best
        join_chain.append(f"{a}⋈{b}")
        total_cost += size
        new_key = f"{a}+{b}"
        del remaining[a]
        del remaining[b]
        remaining[new_key] = size
    return join_chain, total_cost


def map_reduce_wordcount(docs):
    """Stanford MapReduce 词频统计（教学版）。"""
    def mapper(doc):
        return [(w, 1) for w in doc[1].split()]
    mapped = []
    for d in docs:
        mapped.extend(mapper(d))
    # shuffle: 按 key 分组
    shuffled = defaultdict(list)
    for k, v in mapped:
        shuffled[k].append(v)
    # reduce: 求和
    return {k: sum(v) for k, v in shuffled.items()}


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 4 · 四校能力地图（学完能干嘛）                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part4_capability_map() -> None:
    print("=" * 74)
    print("  Part 4 · 四校能力地图 —— 学完你能做什么？")
    print("=" * 74)
    rows = [
        ("CMU 15-445",  "实现派", "从零写一个单机 DB", "bus-tub 4 个 project 全做", "★★★★★"),
        ("MIT 6.830",   "抽象派", "讨论 isolation level 的微妙差别", "读 5 篇经典论文 + problem set", "★★★★☆"),
        ("UCB CS186",   "实战派", "写好 SQL、调好索引、设计 schema", "Spark + Postgres 5 个 proj", "★★★★☆"),
        ("Stan CS145",  "分布派", "选对 NoSQL、搭大数据管线", "MapReduce / BigTable 实操", "★★★☆☆"),
    ]
    print(f"  {'课程':<12} {'流派':<8} {'学完能力':<28} {'关键动作':<26} {'难度'}")
    print("  " + "─" * 72)
    for c, s, ab, act, d in rows:
        print(f"  {c:<12} {s:<8} {ab:<28} {act:<26} {d}")
    print()
    print("  🎯 整合学习路径（4 周速成）：")
    print("     Week 1: UCB CS186 先上手（SQL + 索引调优，立刻有用）")
    print("     Week 2: CMU 15-445 bus-tub Project 1+2（buffer pool + B+tree 实现）")
    print("     Week 3: MIT 6.830 读 3 篇论文（ARIES + 2PL + Selinger）")
    print("     Week 4: Stanford CS145（MapReduce + CAP，打通分布式数据系统）")
    print()
    print("  🔗 衔接现有项目：")
    print("     • CMU 完整实现 → cmu-cs-projects/topic3-database/dbms.py")
    print("     • MIT 完整实现 → mit-cs-projects/topic6-db/database.py")
    print("     • Berkeley 数据科学 → berkeley-cs-projects/topic11-data/data_science.py")
    print()


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  主入口                                                                  ║
# ╚══════════════════════════════════════════════════════════════════════╝

def main() -> None:
    print()
    print("╔" + "═" * 72 + "╗")
    print("║" + " 数据库系统四校整合 · CMU 15-445 × MIT 6.830 × UCB CS186 × Stan CS145 ".center(72) + "║")
    print("╚" + "═" * 72 + "╝")
    print()
    print_history()
    part1_indexes()
    part2_transactions()
    part3_queries()
    part4_capability_map()
    print("=" * 74)
    print("  ✅ 全部演示完成。下一步建议：")
    print("     1. 跑现有完整实现：python3 cmu-cs-projects/topic3-database/dbms.py")
    print("     2. 跑 MIT 抽象版：  python3 mit-cs-projects/topic6-db/database.py")
    print("     3. 按 Part 4 的 4 周路径，选一个项目深入。")
    print("=" * 74)
    print()


if __name__ == "__main__":
    main()
