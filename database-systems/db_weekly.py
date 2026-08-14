"""
数据库 4 周实战练习册 —— 把 db_integration.py 的理论变成可跑的练习
====================================================================
配合 database-systems/db_integration.py 食用。

  Week 1 · UCB CS186    —— SQL 调优实战（3 个从慢到快的案例）
  Week 2 · CMU 15-445   —— 造轮子（buffer pool LRU + B+tree 分裂）
  Week 3 · MIT 6.830    —— 论文级练习（ARIES 恢复 + 可串行化判定）
  Week 4 · Stanford     —— 分布式（CAP 选型 + MapReduce join + quorum）

每周末有 ✍️ 自测题，跑通代码 + 答对自测 = 过关。

运行：
    python3 db_weekly.py
依赖：仅标准库
====================================================================
"""
from __future__ import annotations
import math
import random
from collections import defaultdict, OrderedDict

def banner(title):
    print("\n" + "█" * 74)
    print(f"  {title}")
    print("█" * 74)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 1 · UCB CS186 —— SQL 调优实战                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week1_sql_tuning() -> None:
    banner("Week 1 · UCB CS186 —— SQL 调优：3 个从慢到快的案例")

    print("""
  目标：学会读懂 EXPLAIN，识别慢查询的根因，对症下药。
  方法：每个案例先看"慢 SQL"，分析为什么慢，再看"快 SQL"。
""")

    # ── 案例 1：SELECT * 的陷阱 ──
    print("─" * 74)
    print("【案例 1】SELECT * 陷阱 —— 为什么少查几列能快 10 倍？")
    print("─" * 74)
    print("""
  ❌ 慢：
    SELECT * FROM orders WHERE user_id = 100;
    问题：orders 表有 20 列（含 TEXT 类型的备注），SELECT * 要把所有列读出。
          即使有 user_id 索引，也要【回表】读完整行（随机 I/O）。

  ✅ 快：
    SELECT order_id, total FROM orders WHERE user_id = 100;
    改进：只查 2 列。如果建了 (user_id, order_id, total) 【联合索引】，
          索引本身就有全部数据 → 【覆盖索引】，根本不用回表！

  💡 EXPLAIN 怎么读：
    慢：Index Scan + Heap Fetches=1000   ← 索引找到后回表 1000 次
    快：Index Only Scan                  ← 索引够用，零回表
""")

    # ── 案例 2：函数让索引失效 ──
    print("─" * 74)
    print("【案例 2】函数包了一层，索引就废了")
    print("─" * 74)
    print("""
  ❌ 慢：
    SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15';
    问题：DATE() 函数包裹列 → 优化器无法用 created_at 上的索引！
          B+tree 索引的是原始值，函数变换后无法二分查找。
          只能全表扫描，逐行算 DATE() 再比较。

  ✅ 快：
    SELECT * FROM orders
    WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16';
    改进：用范围查询代替函数，优化器能用 created_at 索引做 range scan。

  💡 铁律：WHERE 左边别包函数！把变换移到右边常量上。
""")

    # ── 案例 3：N+1 查询 ──
    print("─" * 74)
    print("【案例 3】N+1 查询 —— ORM 最常见的性能杀手")
    print("─" * 74)
    # 模拟 N+1 vs JOIN
    users = {i: f"user{i}" for i in range(100)}
    orders = [(i, f"user{random.randint(0,99)}") for i in range(50)]
    # N+1: 先查所有 user，再每个 user 查一次 order
    n_plus_1_queries = 1 + len(users)
    # JOIN: 一次查完
    join_queries = 1
    print(f"""
  场景：查 100 个用户及其订单。
  ❌ N+1 模式（Django/SQLAlchemy 默认 lazy-load 常见坑）：
    users = User.objects.all()         # 1 次查询
    for u in users:
        u.orders.all()                # 每人 1 次 = {len(users)} 次查询
    总查询数 = {n_plus_1_queries}，网络往返 {n_plus_1_queries} 次，极慢。

  ✅ JOIN / prefetch：
    users = User.objects.prefetch_related('orders').all()  # 只 {join_queries} 次查询
    总查询数 = 2（1 次用户 + 1 次批量订单），快 {n_plus_1_queries // 2}x。
""")

    print("─" * 74)
    print("  ✍️ W1 自测题：")
    print("     Q1: 查询 SELECT COUNT(*) FROM t WHERE status=1 走了全表扫描，")
    print("         status 有索引，为什么？该怎么优化？")
    print("     Q2: LIKE '%abc' 为什么用不了索引？LIKE 'abc%' 呢？")
    print("     (提示：B+tree 是有序的，前缀匹配能二分，后缀不能)")
    print("─" * 74)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 2 · CMU 15-445 —— 造轮子                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week2_build_db() -> None:
    banner("Week 2 · CMU 15-445 —— 造轮子：buffer pool + B+tree")

    print("""
  目标：手写 DB 的两个核心组件，理解"内部发生了什么"。
  bus-tub 风格（简化），用 Python 演示原理。
""")

    # ── 练习 1：Buffer Pool LRU ──
    print("─" * 74)
    print("【练习 1】Buffer Pool + LRU 替换策略")
    print("─" * 74)
    print("  问题：磁盘 1000 页，内存只能放 4 页。请求序列如何影响命中率？")
    pool = BufferPool(capacity=4)
    # 局部访问模式
    access = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    hits = 0
    for page in access:
        if pool.access(page):
            hits += 1
    rate = hits / len(access)
    print(f"  访问序列 {access}")
    print(f"  LRU 命中率 = {hits}/{len(access)} = {rate:.0%}")
    print("  → 容量不够时，LRU 淘汰最久未用的页。局部性好的话命中率会高。")
    print("  → bus-tub Project 1 就是实现这个 + clock/LRU 策略对比。")
    print()

    # ── 练习 2：B+tree 分裂 ──
    print("─" * 74)
    print("【练习 2】B+tree 插入与叶子分裂")
    print("─" * 74)
    tree = SimpleBPlusTree(leaf_capacity=3)
    keys = [10, 20, 5, 15, 25]
    print(f"  叶子容量=3，依次插入 {keys}：")
    for k in keys:
        tree.insert(k)
        events = tree.events
    for ev in tree.events:
        print(f"    {ev}")
    print(f"  最终叶子: {tree.leaves}")
    print("  → 第 4 个插入触发分裂：一个叶子分成两个，中间 key 上推。")
    print("  → bus-tub Project 2 实现完整 B+tree（含内部节点分裂/合并/借贷）。")
    print()

    print("─" * 74)
    print("  ✍️ W2 自测题：")
    print("     Q1: LRU 在'扫描全表'时表现极差（扫描抖动），为什么？")
    print("         (提示：全表扫 > 内存容量，每页只访问一次却被塞满)")
    print("     Q2: B+tree 为什么用'叶子链表'而 B-tree 不用？")
    print("         (提示：范围查询 SELECT WHERE id BETWEEN ...) ")
    print("─" * 74)


class BufferPool:
    """CMU bus-tub 风格：LRU 替换的 buffer pool。"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.pool = OrderedDict()  # page -> True, 顺序即 LRU
        self.events = []

    def access(self, page):
        if page in self.pool:
            self.pool.move_to_end(page)  # 命中，移到最新
            return True
        # miss
        if len(self.pool) >= self.capacity:
            evicted, _ = self.pool.popitem(last=False)
            self.events.append(f"淘汰页 {evicted}，")
        self.pool[page] = True
        return False


class SimpleBPlusTree:
    """教学版 B+tree：单层叶子 + 分裂（演示原理，非完整实现）。"""
    def __init__(self, leaf_capacity=3):
        self.leaf_capacity = leaf_capacity
        self.leaves = []   # list of sorted list (叶子链)
        self.events = []

    def insert(self, key):
        if not self.leaves:
            self.leaves = [[key]]
            self.events.append(f"插入 {key} → 首个叶子 {self.leaves}")
            return
        # 找目标叶子（教学版：插第一个没满的）
        target = self.leaves[-1]
        target.append(key)
        target.sort()
        if len(target) > self.leaf_capacity:
            mid = len(target) // 2
            new_leaf = sorted(target[mid:])
            target[:] = sorted(target[:mid])
            self.leaves.append(new_leaf)
            self.events.append(f"插入 {key} → 触发分裂！叶 {target} | {new_leaf}")
        else:
            self.events.append(f"插入 {key} → 叶 {target}")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 3 · MIT 6.830 —— 论文级练习                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week3_papers() -> None:
    banner("Week 3 · MIT 6.830 —— 论文练习：ARIES 恢复 + 可串行化判定")

    print("""
  目标：用"论文级"的精度理解事务恢复与并发正确性。
  读 3 篇：ARIES (Mohan 1992) / 2PL (Bernstein 1987) / Selinger (1979)
""")

    # ── 练习 1：ARIES 恢复 ──
    print("─" * 74)
    print("【练习 1】ARIES 三阶段恢复：崩溃后怎么把 DB 救回来？")
    print("─" * 74)
    log = [
        ("T1", "BEGIN", None, None),
        ("T1", "UPDATE", "X", (10, 20)),   # X: old=10 → new=20
        ("T1", "COMMIT", None, None),
        ("T2", "BEGIN", None, None),
        ("T2", "UPDATE", "Y", (5, 8)),     # Y: 5 → 8
        # 💥 崩溃！T2 没 commit
    ]
    print("  日志（崩溃前）：")
    for r in log:
        print(f"    {r}")
    print("\n  💥 崩溃后 ARIES 三阶段：")
    print("    1. Analysis：扫描日志，确定 T1 已 commit、T2 未 commit（loser）")
    print("    2. Redo：重放所有 UPDATE（幂等），把 DB 恢复到崩溃前最后一刻")
    print("       → X=20, Y=8")
    print("    3. Undo：回滚 loser 事务 T2 的更新")
    print("       → Y 恢复为 5（用日志里的 old value）")
    print("  最终：X=20 (T1 committed), Y=5 (T2 undone)")
    print("  → ARIES 核心：先全部 Redo（保证不丢已写数据），再 Undo loser。")
    print("  → 这就是数据库 crash-safe 的秘密：WAL + ARIES。")
    print()

    # ── 练习 2：可串行化判定 ──
    print("─" * 74)
    print("【练习 2】可串行化判定：这个并发调度对不对？")
    print("─" * 74)
    schedule = [
        ("T1", "W", "x"), ("T2", "R", "x"), ("T2", "W", "y"), ("T1", "R", "y")
    ]
    print(f"  调度 S = {schedule}")
    print("  步骤：找冲突操作（同数据项，至少一个 W，不同事务）")
    # 建冲突图
    edges = set()
    for i, (ta, oa, da) in enumerate(schedule):
        for j, (tb, ob, db) in enumerate(schedule):
            if i < j and ta != tb and da == db and ("W" in (oa, ob)):
                edges.add((ta, tb))
    print(f"  冲突边: {edges if edges else '无'}")
    # 检测环
    has_cycle = detect_cycle(edges)
    if has_cycle:
        print("  图有环 ⟲ → 不可串行化 ❌（不存在等价的串行执行）")
    else:
        print("  图无环 → 可串行化 ✅（等价于某个串行顺序）")
    print("  → MIT 教你：用冲突图判断并发是否正确，比'感觉对不对'严谨得多。")
    print()

    print("─" * 74)
    print("  ✍️ W3 自测题：")
    print("     Q1: 如果 T2 在读 x 之前 T1 已经 commit，结论会变吗？")
    print("     Q2: ARIES 为什么必须先 Redo 再 Undo，不能反过来？")
    print("         (提示：Undo 需要正确的 old value，但崩溃时可能只写了一半)")
    print("─" * 74)


def detect_cycle(edges):
    """在有向边集合上检测环（教学版，小规模）。"""
    graph = defaultdict(list)
    nodes = set()
    for a, b in edges:
        graph[a].append(b)
        nodes.add(a); nodes.add(b)
    for start in nodes:
        stack, visited = [start], set()
        while stack:
            n = stack.pop()
            if n == start and visited:
                return True
            if n in visited:
                continue
            visited.add(n)
            stack.extend(graph[n])
        # 只检测回到 start 的环
    # 简化：有任意两点互达即算有环（本题 T1↔T2）
    for a, b in edges:
        if (b, a) in edges:
            return True
    return False


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Week 4 · Stanford —— 分布式数据系统                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def week4_distributed() -> None:
    banner("Week 4 · Stanford CS145 —— 分布式：CAP 选型 + MapReduce join")

    print("""
  目标：学会为业务选对存储（SQL/NoSQL/NewSQL），理解分布式数据权衡。
""")

    # ── 练习 1：CAP 选型 ──
    print("─" * 74)
    print("【练习 1】CAP 场景选型：该选 CP 还是 AP？")
    print("─" * 74)
    scenarios = [
        ("银行转账", "CP", "钱不能错，宁可暂不可用也不能不一致"),
        ("电商库存", "CP", "超卖比暂时不可用更严重（但可加缓存最终一致）"),
        ("社交 feed", "AP", "短暂看不到某条动态没关系，可用性优先"),
        ("DNS 域名解析", "AP", "可用性 > 一致性，旧缓存几秒可接受"),
        ("分布式锁/选主", "CP", "两个 leader 比暂时无 leader 危险得多"),
    ]
    print(f"  {'业务场景':<16} {'选择':<6} {'理由'}")
    print("  " + "─" * 60)
    for sc, choice, reason in scenarios:
        print(f"  {sc:<16} {choice:<6} {reason}")
    print("  → CP 系统：ZooKeeper / etcd / HBase / Spanner（强一致，分区时部分不可用）")
    print("  → AP 系统：Cassandra / Dynamo / Riak（高可用，分区时各写各的，最终一致）")
    print()

    # ── 练习 2：Quorum 读写 ──
    print("─" * 74)
    print("【练习 2】Quorum NWR：调参改变一致性")
    print("─" * 74)
    print("  Dynamo 风格：N 副本，写需 W 确认，读需 R 响应。")
    configs = [
        (3, 2, 2, "强一致（R+W>N），延迟中等", "银行账户余额"),
        (3, 3, 1, "写慢但读快，强一致", "写少读多的配置中心"),
        (3, 1, 1, "最快但最终一致（可能读旧）", "社交点赞数"),
    ]
    print(f"  {'N,W,R':<12} {'特性':<28} {'适用'}")
    for n, w, r, feat, use in configs:
        strong = "强" if r + w > n else "弱"
        print(f"  N={n},W={w},R={r}  {feat:<28} {use}")
    print("  → 同样 3 副本，W=2/R=2 和 W=1/R=1 的一致性截然不同。")
    print("  → 这就是 Cassandra/Dynamo 的 tuning knob。")
    print()

    # ── 练习 3：MapReduce join ──
    print("─" * 74)
    print("【练习 3】MapReduce 做大数据 join")
    print("─" * 74)
    # 模拟：两个大表分布在多台机器
    users = [("u1", "Alice"), ("u2", "Bob"), ("u3", "Carol")]
    orders = [("o1", "u1", 100), ("o2", "u2", 200), ("o3", "u1", 50)]
    print(f"  users 表: {users}")
    print(f"  orders 表: {orders}")
    # Map 阶段：每条记录打标签
    mapped = []
    for uid, name in users:
        mapped.append((uid, ("user", name)))
    for oid, uid, total in orders:
        mapped.append((uid, ("order", oid, total)))
    # Shuffle：按 uid 分组
    shuffled = defaultdict(list)
    for k, v in mapped:
        shuffled[k].append(v)
    # Reduce：同 uid 的 user 和 order join
    print("  MapReduce join 结果：")
    for uid, vals in shuffled.items():
        uname = next((v[1] for v in vals if v[0] == "user"), "?")
        ords = [(v[1], v[2]) for v in vals if v[0] == "order"]
        print(f"    {uname}({uid}) 的订单: {ords}")
    print("  → 10TB 的 join，单机跑不动，MapReduce 分到 1000 台机器 = 分钟级。")
    print("  → Spark SQL / Hive SQL 底层都是这个：SQL → DAG → 分布式执行。")
    print()

    print("─" * 74)
    print("  ✍️ W4 自测题：")
    print("     Q1: Spanner 怎么在全球范围实现'强一致 + 高可用'？")
    print("         (提示：TrueTime + Paxos，2PC 跨数据中心)")
    print("     Q2: 你的业务'点赞数'用 CP 还是 AP？为什么？")
    print("─" * 74)


def main() -> None:
    print()
    print("╔" + "═" * 72 + "╗")
    print("║" + " 数据库 4 周实战练习册 · 把理论变成手感 ".center(72) + "║")
    print("╚" + "═" * 72 + "╝")
    week1_sql_tuning()
    week2_build_db()
    week3_papers()
    week4_distributed()
    print("\n" + "=" * 74)
    print("  🎓 4 周通关检查表：")
    print("     □ W1: 能读懂 EXPLAIN，识别 Seq/Index/Hash Join，写出覆盖索引")
    print("     □ W2: 手写过 buffer pool LRU 和 B+tree 分裂")
    print("     □ W3: 能论证一个调度是否可串行化，懂 ARIES 三阶段")
    print("     □ W4: 能为业务选对 CP/AP 存储，懂 quorum 调参")
    print("=" * 74)
    print()


if __name__ == "__main__":
    main()
