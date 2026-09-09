# 数据库 · 程序员视角：从慢 SQL 与死锁反推数据库原理

> 学数据库最好的方式不是背 ACID 定义，而是把你在生产被它坑过的那些诡异事故——慢查询、死锁、索引失效、脏读、连接打满、写入越来越慢——一个个钉死在底层机制上。
> 本文每节都从一个**真实事故**出发，反推背后的存储/并发/恢复原理，再给**能直接复制粘贴的排查命令**和修复方向，最后落到 CMU 15-445 的教学数据库 **bustub** 源码。
>
> 配套课程：CMU 15-445（Andy Pavlo，bustub 四大 Project：Buffer Pool / B+Tree / Executor / Concurrency）。配套教材：DDIA（Designing Data-Intensive Applications）第 4 章存储、第 8 章事务。

---

## 〇、心智模型：数据库就是在"加速查找"和"安全共享"

所有数据库事故，归根结底只撞到三类墙：

| 墙 | 数据库做的事 | 出事的表现 |
|----|-------------|-----------|
| **存储引擎** | 把行存进页、用 B+ 树/哈希加速查找、用缓冲池当磁盘缓存 | 慢查询、索引失效、缓冲池抖动 |
| **并发控制** | 锁 / MVCC 让成百上千个事务不打架 | 死锁、脏读、不可重复读、幻读 |
| **持久化恢复** | WAL 先写日志后改页，保证掉电不丢 | 写入越来越慢、fsync 代价、页撕裂 |

下面六节，就是这堵墙上的六种典型裂缝。

---

## 一、加了个查询，突然慢了 100 倍

### 事故现场
某个订单查询平时 5ms，某天业务加了个 `ORDER BY create_time`，监控显示这条 SQL P99 直接飙到 800ms。`EXPLAIN` 一看，`type: ALL`、`rows: 480万`、`Extra: Using filesort`——它在**全表扫描**外加**文件排序**。明明 `create_time` 上加了索引啊？

### 反推原理：B+ 树、索引选择性、最左前缀

**关键概念一：B+ 树为什么是数据库索引的天选结构。** 一条 SQL 慢，本质是"找数据时磁盘 IO 次数太多"。磁盘一次随机读 ~10ms，内存 ~100ns，差十万倍。索引的目标就是**把"扫 N 行"压成"扫 log N 个页"**。

B+ 树（不是 B 树）的关键设计：**数据只存在叶子节点，内部节点只存 key + 子指针**。看 bustub 的页布局就一目了然：

```cpp
// src/include/storage/page/b_plus_tree_internal_page.h:46  内部节点
// n 个 key 配 n+1 个指针；第一个 key 恒为 INVALID，查找时忽略它
//   KEY(1)(INVALID) | KEY(2) | ... | KEY(n)
//   PAGE_ID(1) | PAGE_ID(2) | ... | PAGE_ID(n)     指针 PAGE_ID(i) 指向 K(i)<=K<K(i+1) 的子树
KeyType key_array_[INTERNAL_PAGE_SLOT_CNT];
ValueType page_id_array_[INTERNAL_PAGE_SLOT_CNT];

// src/include/storage/page/b_plus_tree_leaf_page.h:113  叶子节点
// 数据（RID）只存在叶子；叶子之间用 next_page_id_ 串成链表，范围扫描 O(范围/页)
page_id_t next_page_id_;
KeyType key_array_[LEAF_PAGE_SLOT_CNT];
ValueType rid_array_[LEAF_PAGE_SLOT_CNT];
```

**B+ 树 vs B 树的胜负手**：内部节点不存数据 → 同样大小的页（bustub 默认 4KB）能塞更多 key → 树更矮 → 查找 IO 更少。一棵存千万行的 B+ 树通常只有 3~4 层，3~4 次 IO 即可定位任意一行；叶子链表让范围查询顺着 `next_page_id_` 一路扫，不必回根。

**关键概念二：索引选择性（cardinality）。** 优化器用不用索引看**代价估算**：用索引要回表（先查索引拿 RID，再查聚簇索引拿整行），筛选比例不够则回表代价比全表扫还大，于是放弃索引。`gender` 选择性 ≈ 0.5，加索引没用；`id`/`order_no` 接近 1，最适合。

**关键概念三：最左前缀匹配。** 联合索引 `(a, b, c)` 在 B+ 树里是**按 a 排序、a 相同按 b、b 相同按 c** 存的。所以：
- `WHERE a=1` ✅（能用，最左列在）
- `WHERE a=1 AND b=2` ✅
- `WHERE b=2` ❌（跳过 a，在 B+ 树里 b 是无序的，没法二分）
- `WHERE a=1 AND c>5`（a 用上了，但 c 用不上——中间缺 b，且遇到范围后右边列失效）

事故里 `ORDER BY create_time` 全表扫，多半是 `WHERE` 没走索引，优化器算完发现"排序无论如何都要 filesort"，干脆全表扫。

### 排查命令（都能跑）

```sql
-- 1. 看执行计划，这是排查慢 SQL 的第一招。重点看这几列：
EXPLAIN SELECT * FROM orders WHERE user_id=123 ORDER BY create_time;
-- type:  ALL=全表扫描(差) | index=全索引扫描 | range=范围扫 | ref=索引等值 | const=主键等值(好)
-- key:   实际用的索引，NULL 就是没用上
-- rows:  估算要扫描的行数，越大越危险
-- Extra: Using index=覆盖索引(好) | Using filesort=需要额外排序(差) | Using temporary=建临时表(差)

-- 2. 真正跑一遍拿真实耗时和行数（MySQL 8.0+），EXPLAIN 只是估算
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id=123 ORDER BY create_time;

-- 3. 看索引的基数（选择性），cardinality/表行数 接近1才值得建索引
SHOW INDEX FROM orders;          -- 看 Cardinality 列
-- 估算选择性：
SELECT COUNT(DISTINCT user_id)/COUNT(*) FROM orders;

-- 4. 开慢查询日志，让数据库自己抓"罪魁"
SHOW VARIABLES LIKE 'slow_query_log%';            -- 看是否开启、日志路径
SET GLOBAL slow_query_log = 'ON';                 -- 临时开
SET GLOBAL long_query_time = 1;                   -- 超过1秒算慢查询
-- 然后去 slow_query_log_file 指的文件里看，每条慢 SQL 带耗时、扫描行数
```

### 修复方向
- **给对索引**：高选择性、常出现在 `WHERE`/`JOIN ON`/`ORDER BY` 的列才建索引；别给 `gender`/`status` 这种低基数列建。
- **覆盖索引**：把 `SELECT` 用到的列都塞进联合索引，省掉回表。`SELECT user_id,create_time FROM orders WHERE user_id=123` 若有 `(user_id, create_time)` 索引，`Extra` 会显示 `Using index`，不用回表。
- **范围查询避免 `*`**：`SELECT *` 触发回表，只查需要的列。
- **排序**：`ORDER BY` 的列尽量和 `WHERE` 的索引列组合成联合索引，让 B+ 树的天然有序替你省掉 filesort。

### 一行本质
> **慢查询 = 找数据时磁盘 IO 太多；B+ 树用"内部只存 key + 叶子存数据 + 叶子链表"把 IO 压到 log N 层，优化器靠选择性决定用不用索引。**

**bustub 对应**：`src/include/storage/index/b_plus_tree.h`（B+ 树主类 + `Context` 调度上下文）、`src/include/storage/page/b_plus_tree_internal_page.h`（内部节点页：n key 配 n+1 指针）、`src/include/storage/page/b_plus_tree_leaf_page.h`（叶子页：`next_page_id_` 串链表）、`src/storage/index/b_plus_tree.cpp`（Insert/Remove/GetValue 实现）、`src/storage/index/index_iterator.cpp`（范围扫描迭代器）。

---

## 二、两个事务都 update 同一行，卡住了

### 事故现场
线上某转账接口偶发"卡死不返回"。复现：两个请求几乎同时到，事务 A 给账户 1 扣款、账户 2 加钱；事务 B 给账户 2 扣款、账户 1 加钱。两个都挂着不动，最后其中一个报 `ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction`。日志里赫然一段 `*** (1) TRANSACTION` / `*** (2) TRANSACTION` 的死锁报告。

### 反推原理：锁、两阶段锁、死锁检测

**关键概念一：两阶段锁（2PL）。** 事务拿锁分两阶段：**增长阶段**（GROWING）只拿锁不释放，**收缩阶段**（SHRINKING）只释放不拿。这样保证可串行化。严格 2PL（Strict 2PL）更进一步：**X 锁一直持有到事务提交/回滚才释放**，从而避免"读到一个未提交事务中途的值"。看 bustub 的事务状态机：

```cpp
// src/include/concurrency/transaction.h  事务隔离级别
enum class IsolationLevel { READ_UNCOMMITTED, SNAPSHOT_ISOLATION, SERIALIZABLE };

// src/include/concurrency/lock_manager.h:39  五种锁模式
enum class LockMode { SHARED, EXCLUSIVE, INTENTION_SHARED, INTENTION_EXCLUSIVE,
                      SHARED_INTENTION_EXCLUSIVE };
// S/X 是行/表锁；IS/IX/SIX 是"意向锁"，加在表上表示"我里面有行锁"，
// 这样别的事务想 LOCK 整张表时，看一眼表头就知道有没有人在锁行，不必扫所有行。
```

**意向锁的意义**：没有它，事务 A 想给整张表加 X 锁，得检查每一行有没有人持锁——O(N)。有了意向锁，事务 B 给行加锁前先在表上加 IX，A 只看表级有没有冲突意向锁即可——O(1)。

**关键概念二：锁请求队列。** 每个资源（一行/一张表）有一个等待队列，FIFO 授锁。看 bustub 的队列结构：

```cpp
// src/include/concurrency/lock_manager.h:65  每个资源的锁队列
class LockRequestQueue {
  std::list<std::shared_ptr<LockRequest>> request_queue_;  // 等待/已授权的请求链表
  std::condition_variable cv_;          // 阻塞等待锁的事务在这上面 sleep
  txn_id_t upgrading_ = INVALID_TXN_ID; // 正在升级锁的事务（升级优先于普通请求）
  std::mutex latch_;
};
```

事务调 `LockRow()` 时，如果资源已被不兼容的锁占用，就在 `cv_` 上 `wait()` 阻塞，直到持锁者 `Unlock` 时 `notify_all()` 唤醒。

**关键概念三：死锁与等待图（waits-for graph）。** 死锁四条件：互斥、持有并等待、不可剥夺、循环等待。事务 A 等 B 的锁、B 等 A 的锁，永久卡死。**数据库不会让它们永远卡**——它跑一个后台线程周期性检测：建一张"等待图"，节点是事务，A 在等 B 持有的锁就画一条 A→B 的边，**图里有环就是死锁**。bustub 的实现：

```cpp
// src/include/concurrency/lock_manager.h:274  等待图
std::unordered_map<txn_id_t, std::vector<txn_id_t>> waits_for_;  // A 在等谁
// RunCycleDetection() 后台线程周期跑 DFS（FindCycle），发现环就 abort 环里 txn_id 最大的事务
auto FindCycle(txn_id_t source, std::vector<txn_id_t> &path,
               std::unordered_set<txn_id_t> &on_path,
               std::unordered_set<txn_id_t> &visited, txn_id_t *abort_txn_id) -> bool;
```

"abort 最年轻的事务"（txn_id 最大）是个通用策略——年轻事务做的活少，回滚代价低，且避免饿死。MySQL InnoDB 用的是同样的等待图 + 选择受害者策略，所以你看到的是"自动检测 + 自动回滚其中一个"。

### 排查命令（都能跑）

```sql
-- 1. 查死锁现场（最直接）。输出一段 *** (1) TRANSACTION / *** (2) TRANSACTION 死锁报告，
--    含每个事务执行的最后一条 SQL、持有的锁、等待的锁
SHOW ENGINE INNODB STATUS\G
-- 看 "LATEST DETECTED DEADLOCK" 段，以及 "TRANSACTIONS" 段看当前活跃事务

-- 2. 看锁等待（谁在等谁的锁，等了多久）
SELECT * FROM performance_schema.data_locks;          -- 8.0+，看持有哪些锁
SELECT * FROM performance_schema.data_lock_waits;     -- 8.0+，看谁在等
-- 老版本：
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 3. 调锁等待超时（等锁超过这个秒数就报错，而不是无限等）
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';       -- 默认50秒
SET SESSION innodb_lock_wait_timeout = 5;             -- 业务侧重试就调小

-- 4. PostgreSQL：看锁等待链
SELECT pid, mode, granted, query FROM pg_locks JOIN pg_stat_activity USING (pid);
SELECT * FROM pg_stat_activity WHERE wait_event_type='Lock';  -- 卡住的查询
```

### 修复方向
- **固定加锁顺序**：根治死锁最有效的办法。所有事务都按主键升序加锁（如"先锁账户 1 再锁账户 2"），从根上破除循环等待。
- **缩短事务**：事务越长持锁越久，死锁概率越高，把无关操作（RPC、慢 IO）挪出事务边界。
- **降低隔离级别**：能用 RC 就别用 RR/Serializable，锁持有时间更短。
- **重试兜底**：捕获 `1213` 死锁错误码自动重试整个事务（幂等前提下）——数据库已保证只会死锁不会数据错。

### 一行本质
> **死锁 = 多个事务循环等彼此的锁；数据库用"等待图找环 + 回滚最年轻事务"自动解开，你要做的是固定加锁顺序从源头避免。**

**bustub 对应**：`src/include/concurrency/lock_manager.h`（`LockMode` 五种锁、`LockRequestQueue` 锁队列含 `cv_`/`upgrading_`、`waits_for_` 等待图）、`src/concurrency/lock_manager.cpp`（`LockTable/LockRow` 授锁、`GrantNewLocksIfPossible` 唤醒、`RunCycleDetection/FindCycle` 死锁检测）。

---

## 三、索引加了却没用上

### 事故现场
给 `phone` 列加了索引，`SELECT * FROM users WHERE phone=13800001234` 还是全表扫描，`EXPLAIN` 的 `key` 列是 `NULL`。把条件改成 `WHERE phone='13800001234'`（加引号）突然就用上索引了。就差一对引号，性能差了几百倍。

### 反推原理：索引为什么会失效

B+ 树索引能加速，靠的是**列值在叶子页里有序**，可以二分。一旦条件破坏了"对原始列值有序查找"这个前提，优化器就只能放弃索引。常见的失效姿势：

**(1) 函数包裹了列。** `WHERE DATE(create_time)='2024-01-01'`——B+ 树按 `create_time` 的原始时间戳排序，但你查的是 `DATE()` 函数变换后的值，树里这个顺序是乱的，没法二分。改成区间：`WHERE create_time >= '2024-01-01' AND create_time < '2024-01-02'`，列保持原样，走 range 扫描。

**(2) 隐式类型转换。** 这就是事故的元凶。`phone` 是 `varchar`，`WHERE phone=13800001234`（数字）时 MySQL 规则是"把字符串转成数字再比"，等价于对每行套了 `CAST(phone AS SIGNED)`——又是函数包裹列，索引失效。`phone='13800001234'`（字符串）就不转换，索引生效。**口诀：字符串列就用字符串查。**

**(3) 违反最左前缀。** 联合索引 `(a,b,c)`，`WHERE b=2` 跳过了 a，前面讲过，b 在树里是无序的，用不上。

**(4) 范围之后的列失效。** `(a,b,c)` 上 `WHERE a=1 AND c>5`：a 用上了，但 c 不行——因为 a=1 的范围内，c 并不全局有序（每个 a=1 的子区间里 c 才有序）。范围（`>`/`<`/`BETWEEN`/`LIKE 'x%'`）之后的列都会"断"。

**(5) `LIKE` 左模糊。** `WHERE name LIKE '%张'`——前缀未知，无法定位到 B+ 树的某个区间。`LIKE '张%'`（右模糊）则可以走 range。

**(6) `OR` 两侧不全有索引。** `WHERE a=1 OR b=2`，若 b 无索引，整个条件退化成全表扫（除非改写成 `UNION`）。

**(7) 优化器主动放弃。** 即使语法上能用索引，如果表很小、或索引选择性太低（筛掉的比例不够），优化器算完发现回表代价比全表扫还高，就会主动 `type: ALL`。这不是 bug，是合理的。

### 排查命令（都能跑）

```sql
-- 1. EXPLAIN 各列解读（这是判断"索引有没有用上"的唯一标准）
EXPLAIN SELECT * FROM users WHERE phone=13800001234;
-- type  最好→最差: system > const > eq_ref > ref > range > index > ALL
--       const: 主键/唯一索引等值；ref: 普通索引等值；range: 范围；index: 扫整个索引树；ALL: 全表
-- key        实际用的索引名，NULL=没用任何索引
-- key_len    用了联合索引的几个列（字节数），可反推用了前几列
-- rows       估算扫描行数
-- Extra:
--   Using index        覆盖索引，不用回表（最优）
--   Using where        用索引过滤后还得多读行做二次判断
--   Using filesort     需要额外排序（差，关注）
--   Using temporary    需要建临时表（差，常见于 GROUP BY/DISTINCT）

-- 2. 强制/忽略某个索引，验证你的判断
SELECT * FROM users FORCE INDEX(idx_phone)  WHERE phone='13800001234';
SELECT * FROM users IGNORE INDEX(idx_phone) WHERE phone='13800001234';
-- 如果 FORCE 后变快，说明优化器估错了；如果是 IGNORE 后一样快，说明这索引本就没用

-- 3. 看优化器为什么这么选（MySQL 8.0+），它会告诉你代价估算过程
EXPLAIN FORMAT=TREE SELECT * FROM users WHERE phone=13800001234;

-- 4. 对比加引号 vs 不加引号的执行计划差异（复现事故）
EXPLAIN SELECT * FROM users WHERE phone=13800001234;   -- type: ALL  ← 隐式转换失效
EXPLAIN SELECT * FROM users WHERE phone='13800001234'; -- type: ref   ← 索引生效
```

### 修复方向
- **列保持原样**：别在 `WHERE` 左边对列套函数。需要按日期查就写成区间 `>=` 且 `< 次日`。
- **类型对齐**：字符串列用字符串字面量查；`JOIN ON` 两端的类型要一致，否则也会触发隐式转换。
- **建对联合索引**：把等值列放前面、范围列放最后，如 `(status, create_time)` 给 `WHERE status=1 AND create_time>?`。
- **覆盖索引**：把 `SELECT` 的列纳入索引，消灭回表。
- **别迷信索引**：低选择性列（性别、状态）的索引优化器多半不用，反而拖慢写入。用 `SHOW INDEX` 的 `Cardinality` 判断。

### 一行本质
> **索引失效 = 你的条件破坏了"对原始列值有序查找"；函数/隐式转换/左模糊/跳过最左列，都会让 B+ 树的二分失效。**

**bustub 对应**：`src/include/storage/index/b_plus_tree.h` 的 `GetValue()`（点查，依赖 key 有序二分）、`Begin(key)`/`End()`（范围扫描，依赖叶子链表有序）。bustub 的 B+ 树假设 key 已经由 `KeyComparator` 定义了全序——这正是"索引能用"的前提；一旦你在查询端做了变换，等价于换了一个 comparator，树里的顺序就作废了。

---

## 四、读到了脏数据 / 同一查询两次结果不同

### 事故现场
报表系统跑一个对账查询：`SELECT SUM(amount) FROM accounts`，跑了两遍结果差了 200 块，但中间没有任何人改数据。或者更糟：转账事务还没提交，另一个查询就看到了"扣了款但没加钱"的中间态。这种"数据对不上"的事故，根因都在**事务隔离级别**。

### 反推原理：隔离级别、MVCC、快照

**关键概念一：四个隔离级别与三种现象。** 并发事务互相干扰会产生三种"脏现象"：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|:---:|:--------:|:---:|
| Read Uncommitted | ✅出现 | ✅出现 | ✅出现 |
| Read Committed（RC） | ❌ | ✅出现 | ✅出现 |
| Repeatable Read（RR） | ❌ | ❌ | ✅出现* |
| Serializable | ❌ | ❌ | ❌ |

- **脏读**：读到别人**未提交**的数据，对方一回滚你就读到了从未存在过的值。
- **不可重复读**：同一事务里读两遍同一行，值变了（别人提交了 update）。
- **幻读**：同一事务里同一范围查两遍，行数变了（别人提交了 insert）。(\* MySQL 的 RR 用 next-key lock 在一定程度上消除了幻读，但标准定义下仍可能。)

**关键概念二：MVCC（多版本并发控制）。** 让"读不阻塞写、写不阻塞读"的核心技术。每行数据不只有一个版本，而是有一条**版本链**。看 bustub 的 MVCC 实现：

```cpp
// src/include/concurrency/transaction.h:73  每个历史版本（undo log）
struct UndoLog {
  bool is_deleted_;                  // 这版是不是删除标记
  std::vector<bool> modified_fields_;// 改了哪几个字段
  Tuple tuple_;                      // 这版的值
  timestamp_t ts_{INVALID_TS};       // 这版的提交时间戳
  UndoLink prev_version_{};          // 指向更老的版本 ← 串成版本链
};

// src/include/concurrency/transaction_manager.h:67  每个页每个槽的版本链头
struct PageVersionInfo {
  std::unordered_map<slot_offset_t, UndoLink> prev_link_;  // slot → 最新版本
};
std::unordered_map<page_id_t, std::shared_ptr<PageVersionInfo>> version_info_;
std::atomic<timestamp_t> last_commit_ts_{0};  // 全局最后提交时间戳
```

事务更新一行时：把旧值存成一个 `UndoLog`，新值写进表堆，`version_info_` 指向这条新 undo log。读的时候，事务拿着自己的 **read_ts**，沿 `prev_version_` 链往回走，找到第一个 `ts_ <= read_ts` 的版本——那就是它"应该看到的"那个历史快照。**于是读老版本的人和写新版本的人互不干扰。**

**关键概念三：快照隔离（Snapshot Isolation）。** 事务开始时拿一个 `read_ts = last_commit_ts`，整个事务期间都看这个时刻的快照，无论别人怎么提交它看到的都不变——这就解决了"不可重复读"。写冲突用 **first-committer-wins**：两个事务同时改同一行，先提交的赢，后提交的在 commit 时检测到冲突被 abort。bustub 用一把全局 `commit_mutex_` 保证同一时刻只有一个事务能提交并推进 `last_commit_ts_`，再用 `VerifyTxn()` 检查写冲突：

```cpp
// src/include/concurrency/transaction_manager.h:85
std::mutex commit_mutex_;             // 保证 commit 串行
std::atomic<timestamp_t> last_commit_ts_{0};
auto VerifyTxn(Transaction *txn) -> bool;  // 提交时校验写集有没有被别人改过
```

**关键概念四：水位线（Watermark）与 GC。** 老版本不能无限攒着。系统维护一个**水位线** = 所有活跃事务里最小的 read_ts。比水位线还老的 undo log 就没事务会再读了，可以回收。bustub 的 `Watermark` 类：

```cpp
// src/include/concurrency/watermark.h
class Watermark {
  auto AddTxn(timestamp_t read_ts) -> void;     // 事务开始登记自己的 read_ts
  auto RemoveTxn(timestamp_t read_ts) -> void;  // 事务结束移除
  auto GetWatermark() -> timestamp_t;           // 当前最小 read_ts，GC 的依据
};
```

**回到事故**：对账查询两次结果不同，多半是隔离级别只有 RC（每次读都拿最新快照），期间有事务提交了。改成 RR/SI（整个事务一个快照）就不会变。

### 排查命令（都能跑）

```sql
-- 1. 看当前隔离级别
SELECT @@GLOBAL.transaction_isolation, @@SESSION.transaction_isolation;
SHOW VARIABLES LIKE 'transaction_isolation';   -- 老版本 MySQL

-- 2. 设置隔离级别（只影响下一个事务）
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;        -- RC：每次读新快照
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;       -- RR：事务内快照不变（MySQL默认）
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;          -- 串行化，最严

-- 3. 复现"不可重复读"（开两个会话）
-- 会话A: START TRANSACTION; SELECT amount ... WHERE id=1;   -- 第一次：100
-- 会话B: UPDATE accounts SET amount=amount+50 WHERE id=1; COMMIT;
-- 会话A: SELECT amount ... WHERE id=1;   -- RC 下变150，RR 下还是100
-- 会话A: COMMIT;
-- 同理用 READ UNCOMMITTED 可复现"脏读"：会话A 改了不提交，会话B 能读到中间值

-- 4. PostgreSQL 看可见性（每行有 xmin=创建事务,xmax=删除事务）
SELECT xmin, xmax, * FROM accounts WHERE id=1;

-- 5. 长事务排查（持有老快照、阻塞 GC 的元凶）
SELECT * FROM information_schema.INNODB_TRX;          -- MySQL，看活跃事务年龄
SELECT pid, xact_start, state, query FROM pg_stat_activity WHERE xact_start IS NOT NULL;
```

### 修复方向
- **选对隔离级别**：多数业务用 MySQL 默认 RR 即可；对账/报表要结果稳定，务必在同一事务里读，别跨连接。
- **别用 Read Uncommitted**：几乎没有正当理由，脏读会读到从未存在的数据。
- **监控长事务**：跑了几小时的事务会卡住 GC（水位线推不动），undo log 堆积拖慢所有查询。
- **写冲突重试**：SI 下后提交者会被 abort，业务层要捕获并重试。

### 一行本质
> **隔离级别 = 读事务愿意看多新的数据；MVCC 用版本链 + read_ts 让"读老版本"和"写新版本"并行，水位线决定能回收多老的版本。**

**bustub 对应**：`src/include/concurrency/transaction.h`（`UndoLog` 版本结构、`IsolationLevel` 枚举）、`src/include/concurrency/transaction_manager.h`（`version_info_`/`PageVersionInfo` 版本链、`last_commit_ts_`/`commit_mutex_` 实现 first-committer-wins、`VerifyTxn` 写冲突检测）、`src/include/concurrency/watermark.h` + `src/concurrency/watermark.cpp`（水位线，GC 依据）、`src/concurrency/transaction_manager.cpp`（Begin/Commit/Abort/GarbageCollection）。

---

## 五、连接数打满 / 连接池翻车

### 事故现场
大促当晚，应用日志疯狂刷 `Too many connections`，新请求全被拒绝。登上数据库 `SHOW PROCESSLIST` 一看，几百个连接大多 `Sleep` 状态，但 `max_connections` 已经到顶。更诡异的是：把连接池从 50 调到 200，QPS 反而掉了一半——连接越多越慢。

### 反推原理：连接模型、线程/进程开销、连接池

**关键概念一：一个连接 = 一个线程（或进程）+ 一块内存。** 这不是免费的。

- **MySQL**：默认**线程-per-连接**。每个连接一个线程，栈 256KB~1MB，再加 sort_buffer/join_buffer 等会话缓冲，一个连接轻松吃几 MB。`max_connections=1000` × 4MB = 光连接就 4GB。
- **PostgreSQL**：默认**进程-per-连接**（fork 后端进程），开销更大，所以 PG 更依赖连接池（pgbouncer）。
- **bustub 这类嵌入式库**则是单进程内多线程，没有网络连接层，但缓冲池/锁队列这些共享资源的争抢逻辑和生产库完全一致。

**关键概念二：为什么连接池不是越大越好。** 池子的本意是复用连接（省掉反复建连的 TCP 握手 + 鉴权开销）。但池子太大反而有害：数据库 CPU 核数固定（如 8 核），200 个连接同时发查询，上下文切换开销爆炸，还争抢同一批锁（行锁、缓冲池 latch），互相拖慢。HikariCP 作者的经验公式：

```
池大小 ≈ (CPU 核数 × 2) + 有效磁盘数
```

8 核 + 1 块 SSD ≈ 17 个连接就够了。多出来的连接只是在排队和争抢。把池从 50 调到 200 让 QPS 翻车，正是因为争抢加剧。

**关键概念三：连接的生命周期与会话状态。** 一个连接上执行的 `SET`/`临时表`/`用户变量`/`未提交事务`都是会话级状态。连接池归还连接时如果不 reset，下一个使用者会继承上一个的脏状态（比如未提交的事务、错误的隔离级别）。这就是"连接池翻车"的隐蔽形式。

### 排查命令（都能跑）

```sql
-- 1. 看当前连接数和上限
SHOW VARIABLES LIKE 'max_connections';        -- 上限，默认151
SHOW STATUS LIKE 'Threads_connected';         -- 当前已连接数
SHOW STATUS LIKE 'Threads_running';           -- 正在执行查询的（Sleep 的不算）
SHOW STATUS LIKE 'Max_used_connections';      -- 历史峰值连接数

-- 2. 看每个连接在干嘛（排查"连接被谁占着"）
SHOW PROCESSLIST;                             -- 简版
SHOW FULL PROCESSLIST;                        -- 完整 SQL 文本
-- Id/Host/User/DB/Command(Time)/State/Info
-- Command=Sleep 且 Time 很大 → 空闲连接占着茅坑
-- Command=Query 且 Time 大 → 慢查询卡住连接

-- 3. 杀掉卡住的连接
KILL <Id>;                                    -- 释放一个连接

-- 4. 调空闲连接超时（Sleep 超过这个秒数就自动断开，释放连接）
SHOW VARIABLES LIKE 'wait_timeout';           -- 默认28800秒(8小时)，太长！
SET GLOBAL wait_timeout = 600;                -- 调成10分钟，让空闲连接及时回收
SET GLOBAL interactive_timeout = 600;

-- 5. 调最大连接数（应急，治标）
SET GLOBAL max_connections = 500;             -- 注意内存够不够

-- 6. PostgreSQL 看连接 + 用 pgbouncer 池化
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SHOW max_connections;
```

```bash
# 7. 应用侧看连接池配置（以 HikariCP 为例，在 application.yml）
# maximum-pool-size: 20          ← 别盲目调大，参考 (核数*2+磁盘数)
# connection-timeout: 3000       ← 拿不到连接多久报错
# idle-timeout: 600000           ← 空闲连接多久回收
# max-lifetime: 1800000          ← 连接最长存活(防数据库端先断)

# 8. 看数据库进程的内存，估算每个连接的开销
ps -o pid,rss,cmd -p $(pgrep -f mysqld)
# RSS / 当前连接数 ≈ 每个连接的均摊内存
```

### 修复方向
- **池大小按公式调**：`(核心数×2 + 磁盘数)`，别盲目堆大，请求排队比连接互锁更快。
- **设合理的 wait_timeout**：默认 8 小时太长，空闲连接长期占着连接配额，调到几分钟。
- **用连接池 + 探活**：HikariCP/Druid 归还连接时 `SELECT 1` 探活并 reset 会话状态，避免脏连接。
- **前置 pgbouncer/ProxySQL**：应用和数据库间放一层连接池代理（PG 必备 pgbouncer），让数据库只看到少量真实连接。
- **异步化/排队**：高峰期请求进队列削峰，别让所有请求同时涌向数据库。

### 一行本质
> **连接不是免费的——每个连接吃线程+内存+会话状态；连接池太大反而加剧 CPU/锁争抢，池大小≈核数×2 才是甜点。**

**bustub 对应**：bustub 是单进程内嵌数据库，没有网络连接层，但它的**缓冲池**（`src/include/buffer/buffer_pool_manager.h`：`frames_`/`page_table_`/`replacer_`/`pin_count_`）正是"有限资源池 + 淘汰策略"的同构模型——缓冲池帧数有限（相当于连接数有限），请求页要 pin（相当于占用连接），用完 unpin 交给 `ArcReplacer`（`src/buffer/arc_replacer.cpp`）决定淘汰谁（相当于连接归还池）。理解了缓冲池的"有限资源 + 调度"再看连接池，是一模一样的思路。

---

## 六、写入越来越慢

### 事故现场
一个高写入服务，刚上线 TPS 5000 一切正常。跑了两周，TPS 慢慢掉到 800，`iostat` 显示磁盘 `%util 95%`、`w/s` 很高但每次 `await` 飙到 50ms。监控看 CPU/内存都不紧张，就是磁盘扛不住。为什么"越写越慢"？

### 反推原理：WAL、redo、fsync、顺序 vs 随机写

**关键概念一：WAL（Write-Ahead Logging，预写日志）。** 改一页数据时，**绝不直接改磁盘数据页**，而是先把"要怎么改"写成一条日志追加到日志文件，再改内存里的数据页。崩溃后靠**重放日志**恢复一致状态。这是 ACID 的"D（持久性）"和崩溃恢复的根基。

为什么要"先写日志"（ahead）？数据页随机分布在磁盘各处，改一个要 seek；日志是**顺序追加**，写起来快得多。**先把容易写的日志落盘保住证据，数据页可以慢慢异步刷**。看 bustub 的日志管理器：

```cpp
// src/include/recovery/log_manager.h:29
class LogManager {
  std::atomic<lsn_t> next_lsn_;          // 全局递增日志序号
  std::atomic<lsn_t> persistent_lsn_;    // 已落盘的最大 LSN
  char *log_buffer_;                     // 日志先攒在这块内存缓冲
  char *flush_buffer_;                   // 刷盘时用另一块（双缓冲，攒和刷并行）
  auto AppendLogRecord(LogRecord *) -> lsn_t;  // 追加一条日志
  void RunFlushThread();                 // 后台线程把 buffer 刷到磁盘
};
// src/include/storage/page/page.h:75  每个数据页头里存着自己的 LSN
inline auto GetLSN() -> lsn_t;           // 这页最后一次被改对应的日志 LSN
inline void SetLSN(lsn_t lsn);           // 恢复时比较页 LSN 和 redo LSN，决定要不要重放
```

`log_buffer_`/`flush_buffer_` 双缓冲是关键优化：一个线程往 `log_buffer_` 追加日志的同时，另一个线程把 `flush_buffer_` 刷盘，刷完两者交换——攒和刷并行，吞吐翻倍。

**关键概念二：fsync 的代价。** 日志"写到 OS 的 page cache"不等于"落盘"，断电还是会丢。只有 `fsync` 才强制冲到物理磁盘。而 fsync 很慢——它要等磁盘真的把数据写进扇区（机械盘要等盘片转过来，SSD 要等 NAND 编程完成），一次几毫秒。这就是写入性能的硬瓶颈。

MySQL InnoDB 用 `innodb_flush_log_at_trx_commit` 控制这个权衡：

| 值 | 行为 | 安全性 | 性能 |
|----|------|:---:|:---:|
| 1（默认） | 每个事务提交都 fsync 日志 | 最安全，掉电不丢 | 最慢 |
| 2 | 每事务写到 OS cache，每秒 fsync 一次 | 掉电丢 OS cache 那 1 秒 | 快很多 |
| 0 | 每秒自己写+fsync | 掉电丢 1 秒 | 最快 |

**关键概念三：随机写 vs 顺序写。** 这是"越写越慢"的核心。日志是顺序追加（`AppendLogRecord`），快；但数据页最终要刷回磁盘上它原本的位置——那是**随机写**，要 seek，慢得多。数据库用几个手段缓解：
- **缓冲池攒脏页**：改了的页（`is_dirty_=true`）先留在内存，攒一批再批量刷（`FlushPage`/`FlushAllPages`），合并小写为大写。
- **后台刷脏**：不像 fsync 那样卡住事务，后台线程慢慢把脏页刷出去。
- **redo 日志可覆盖**：日志是环形的，所有脏页都刷完后，对应的旧日志就能被新日志覆盖，不必无限增长。

```cpp
// src/include/buffer/buffer_pool_manager.h:78  帧头：脏标记 + pin 计数
std::atomic<size_t> pin_count_;
bool is_dirty_;                  // 改过没刷 → 后台择机 FlushPage
std::shared_ptr<DiskScheduler> disk_scheduler_;  // 异步调度磁盘读写
```

**为什么"越写越慢"？** 因为随着数据量增长：① B+ 树变高，每次插入可能触发页分裂（随机写更多页）；② 脏页越来越多，后台刷脏跟不上 redo 生成速度，被迫在事务路径上同步刷（fsync 卡顿放大）；③ 缓冲池命中率下降，更多 IO 落到磁盘。根子还是**磁盘随机写 + fsync 的物理极限**。

**补充：页撕裂（partial page write）。** 若 fsync 前断电，16KB 页可能只写了一半，页内 B+ 树结构损坏，连 redo 都没法重放。InnoDB 用 **doublewrite buffer** 缓解：脏页先顺序写一份到连续区域，再写到各自位置；崩溃恢复时若页损坏就从 doublewrite 取完整副本再重放 redo。

### 排查命令（都能跑）

```sql
-- 1. 看 InnoDB 日志/fsync 相关配置
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';  -- 1=每事务fsync(安全慢) 0/2=快但可能丢
SHOW VARIABLES LIKE 'innodb_flush_method';             -- O_DIRECT 绕过 OS page cache，减少一次拷贝
SHOW VARIABLES LIKE 'sync_binlog';                     -- binlog 的 fsync 策略，binlog 场景关注

-- 2. 看 InnoDB 内部状态，重点看 LOG 段和 BUFFER POOL 段
SHOW ENGINE INNODB STATUS\G
-- LOG 段: log sequence number(当前LSN) / log flushed up to(已刷LSN) 差距大=刷盘跟不上
-- BUFFER POOL AND MEMORY 段: dirty pages 数量、hit rate

-- 3. 看脏页/刷脏压力
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_dirty';   -- 脏页数
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_total';
SHOW GLOBAL STATUS LIKE 'Innodb_data_fsyncs';               -- fsync 次数
SHOW GLOBAL STATUS LIKE 'Innodb_os_log_fsyncs';             -- 日志 fsync 次数
```

```bash
# 4. 看磁盘是不是被打满（最关键）—— 看 %util、await、w/s
iostat -x 1
# %util≈100% 磁盘打满；await 持续高=队列堆积；svctm=单次服务时间

# 5. 看谁在狂写磁盘
iotop -oP            # 按进程
pidstat -d 1

# 6. 追踪 fsync 调用（确认是不是 fsync 拖慢了写入）
strace -p $(pgrep mysqld) -e trace=fsync,fdatasync -c -T
# 如果 fsync 调用密集且耗时长 → 这就是写入瓶颈，考虑调 flush 策略或上更快的盘

# 7. 文件系统层：看 write-back 策略
cat /proc/meminfo | grep Dirty      # 还没落盘的脏页
```

### 修复方向
- **fsync 策略按业务定**：钱、订单类 `innodb_flush_log_at_trx_commit=1`（宁慢不丢）；日志/统计类可设 2（掉电丢 1 秒可接受）换 3~5 倍吞吐。
- **`O_DIRECT` 绕过双缓冲**：`innodb_flush_method=O_DIRECT` 让 InnoDB 直写磁盘，不过 OS page cache（数据库自有缓冲池，再过一层是浪费且增加 fsync 路径）。
- **更快的盘**：HDD→SATA SSD→NVMe，随机写 IOPS 差上千倍，写入瓶颈场景上 NVMe 最直接。
- **批量写**：攒批提交（一次 insert 100 行 vs 100 次 insert 1 行），减少事务/日志/fsync 次数。
- **缓冲池调大**：命中率上去落盘 IO 就少；分库分表/冷热分离把历史数据归档，热表保持小以降低索引高度与随机写放大。

### 一行本质
> **写入慢 = 磁盘随机写 + fsync 的物理极限；WAL 把"随机改页"转成"顺序写日志"绕开 seek，fsync 策略决定掉电丢不丢，缓冲池攒脏页批量刷掉摊薄开销。**

**bustub 对应**：`src/include/recovery/log_manager.h` + `src/recovery/log_manager.cpp`（`next_lsn_`/`persistent_lsn_`、`log_buffer_`/`flush_buffer_` 双缓冲、`AppendLogRecord`/`RunFlushThread`）、`src/recovery/checkpoint_manager.cpp`（检查点，缩短恢复时间）、`src/include/storage/page/page.h`（`GetLSN/SetLSN` 页级 LSN、`OFFSET_LSN`、`is_dirty_`）、`src/include/buffer/buffer_pool_manager.h` + `src/buffer/buffer_pool_manager.cpp`（`is_dirty_`/`FlushPage`/`disk_scheduler_` 脏页延迟刷写）、`src/storage/disk/disk_scheduler.cpp` + `src/storage/disk/disk_manager.cpp`（异步磁盘 IO 调度）。

---

## 附录：把它们串起来的学习路径

1. **先用事故建立直觉**：本文六节覆盖了存储引擎（B+ 树/缓冲池）、并发控制（锁/MVCC/死锁）、恢复（WAL/检查点）三大块。每遇一次生产事故，都回头问"底层哪个机制失效了"。
2. **精读 DDIA 第 4 章（存储与检索）+ 第 8 章（事务）**：前者讲清 B 树 vs LSM、OLTP vs OLAP 存储引擎的差异；后者讲清隔离级别、MVCC、2PL、 Serializable 的代价。这是把"调参"升级成"懂原理"的关键。
3. **动手做 CMU 15-445 的四大 Project**（bustub）：Buffer Pool Manager（P1，理解页/帧/淘汰/脏页）、B+ Tree Index（P2，亲手实现分裂/合并/并发）、Query Execution（P3，理解算子/火山模型）、Concurrency Control（P4，亲手实现锁管理器/死锁检测/MVCC）。做完这四个，本文每一节引用的源码你都会改过一遍。
4. **对照生产系统**：bustub 是"裸"教学实现，MySQL InnoDB / PostgreSQL 是它的工业化版——页格式更复杂、锁有多粒度、MVCC 更精细、WAL 有 group commit。理解 bustub 后读 InnoDB 源码（`btr0btr.cc`/`lock0lock.cc`/`trx0rec.cc`）会有"原来如此"的通透感。
5. **进阶**：CMU 15-721（主存数据库，每节课一篇 paper）讲 group commit、MVCC GC、NUMA 感知的缓冲池——都是把本文这些机制推向极致的工程艺术。

> 注：本文 bustub 引用基于 `cmu-db/bustub`（Spring 2023/2025 版本），四大 Project 分别对应 Buffer Pool / B+Tree / Executor / Concurrency。`src/concurrency/lock_manager.cpp`、`src/storage/index/b_plus_tree.cpp`、`src/buffer/buffer_pool_manager.cpp`、`src/recovery/log_manager.cpp` 是学生实现的核心文件（仓库提供接口与测试框架）。所有 SQL 命令在 MySQL 8.0 / PostgreSQL 14+ 下可直接运行，OS 命令在常见 Linux 下可直接运行。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py --source db` 记录。

### 挑战 1：B+ 树 vs B 树（对应 §一）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么数据库用 B+ 树不用红黑树？ | 说出扇出+范围查询+局部性 |
| L2 联系 | 你的表上哪个索引选择性最高？哪个最低？ | 能看 EXPLAIN |
| L3 创造 | 画一棵 3 层 B+ 树，标注每层能存多少行 | 内部节点 100 扇出 → 100³=100 万 |
| L4 教学 | 向产品经理解释"加了索引为什么还慢"（索引失效） |

### 挑战 2：MVCC 隔离级别（对应 §四）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | MVCC 怎么实现"读不阻塞写"？ | 说出快照+版本链 |
| L2 联系 | 你的业务里哪里可能脏读？哪里需要可串行化？ | 指出具体场景 |
| L3 创造 | 用两个终端模拟 4 种隔离级别的差异 | BEGIN + SET TRANSACTION ISOLATION |
| L4 教学 | 向非 DBA 解释"幻读"和"不可重复读"的区别 |

### 挑战 3：WAL 原理（对应 §六）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么 WAL 让写入更快？ | 顺序写 vs 随机写 |
| L2 联系 | 你的数据库 fsync 频率是多少？ | 知道 innodb_flush_log_at_trx_commit |
| L3 创造 | 解释"先写日志再写数据"在 crash 后怎么恢复 | redo log replay |
| L4 教学 | 向运维解释"数据库越来越慢"可能和 WAL 有关 | fsync 性能瓶颈 |
