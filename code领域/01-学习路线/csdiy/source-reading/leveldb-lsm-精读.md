# LevelDB LSM 树精读：写入优化的存储引擎

> B+ 树优化读取，LSM 树优化写入。这是现代存储引擎的两大阵营。
>
> 配套：[sqlite-btree-逐行拆解.md](sqlite-btree-逐行拆解.md) | [tinydb/btree.py](../projects/tinydb/btree.py)
> csdiy 对应：db §一(B+树) + §六(WAL) | 微小知识交叉：tinydb/tinykafka

---

## 一、为什么有 LSM 树

### B+ 树的问题

B+ 树（SQLite/PostgreSQL/MySQL 用）优化了读取——每次查询 O(log N)。

但**写入代价高**：
- 每次 INSERT 可能触发页分裂（随机写）
- 随机写比顺序写慢 100 倍（参照 csapp Ch6：磁盘 seek ≈ 10ms vs 顺序 ≈ 0.1ms）
- WAL 保证了持久性，但数据页的随机写仍然昂贵

### LSM 树的核心思想

**把随机写变成顺序写**。

```
传统 B+ 树写入：
  INSERT key=42 → 找到目标页（随机读）→ 修改页（随机写）→ fsync（等磁盘）

LSM 树写入：
  INSERT key=42 → 追加到 WAL（顺序写）→ 写入 MemTable（内存）→ 完了！
```

写入只碰两次 IO：
1. WAL 追加（顺序写，极快）
2. MemTable 是内存操作（零 IO）

磁盘上的数据（SSTable）只通过后台 **Compaction** 整理——批量顺序写。

### 谁用 LSM

| 项目 | LSM 实现 | 语言 |
|------|---------|------|
| LevelDB | 原创 | C++ |
| RocksDB | LevelDB 的生产级 fork | C++ |
| Cassandra | LSM + 分区 | Java |
| HBase | LSM + HDFS | Java |
| TiDB/TiKV | RocksDB 之上 | Rust |
| DynamoDB | 内部用类似 LSM | 闭源 |

**如果你用任何分布式数据库，底层大概率是 LSM。**

---

## 二、LevelDB 架构全景

```
                    ┌──────────────────────────┐
   写入 ──→ WAL ──→ │  MemTable（内存跳表）      │
                    │    ↓ 满了（默认 4MB）      │
                    │  Immutable MemTable        │
                    └──────────┬───────────────┘
                               │ 后台线程 flush
                    ┌──────────↓───────────────┐
                    │  Level 0 SSTable（磁盘）   │ ← overlap 的文件
                    │    ↓ compaction            │
                    │  Level 1 SSTable           │ ← 有序，不 overlap
                    │    ↓ compaction            │
                    │  Level 2 SSTable           │
                    │    ↓ （每层 10 倍增长）     │
                    │  Level N...                │
                    └──────────────────────────┘
```

### 组件详解

#### MemTable

内存中的有序数据结构（LevelDB 用 **跳表 SkipList**）。

```cpp
// 参照 LevelDB db/skiplist.h
template<typename Key, class Comparator>
class SkipList {
    struct Node {
        Key key;
        Node* next_[kMaxHeight];  // 多级指针
    };
    Node* head_;
    int max_height_;
};
```

为什么用跳表而不是红黑树？
- **插入时不需要旋转**（无锁插入更容易）
- **范围查询友好**（链表直接遍历）
- **实现比红黑树简单**（~100 行 vs ~500 行）
- 期望 O(log N)，和红黑树一样

csdiy 交叉：[redis-eventloop 精读](redis-eventloop-逐行拆解.md) 提到 Redis 的 `zset` 也用跳表。

#### SSTable（Sorted String Table）

磁盘上的有序文件。格式：

```
[data block 1] [data block 2] ... [data block N]
[meta block]（bloom filter）
[index block]（每个 data block 的 key 范围）
[footer]（指向 index 和 meta 的偏移）
```

每个 data block 内的 key 有序。读时：
1. 二分 index block → 找到目标 data block
2. 读 data block → 二分找 key

#### WAL（Write-Ahead Log）

和 tinydb 的 WAL 完全同构（参照 db §六）。

```cpp
// 参照 LevelDB db/log_writer.h
class Writer {
    void AddRecord(const Slice& data) {
        // 追加写，7 种 record type（full/first/middle/last）
        // CRC32 校验 → 防止部分写入
    }
};
```

---

## 三、写入路径

```
client: Put("key", "value")
    │
    ↓
1. 写 WAL（追加 + fsync）
    │  → 参照 db §六：先写日志保证 crash 安全
    ↓
2. 写 MemTable（跳表 Insert）
    │  → 内存操作，零磁盘 IO
    ↓
3. 返回 OK（客户端不等磁盘整理）

    ─── 后台线程（异步）───

4. MemTable 满了（4MB）→ 变成 Immutable MemTable
    │
    ↓
5. 新建一个空 MemTable 接收新写入
    │
    ↓
6. 后台线程把 Immutable flush 到 Level 0 SSTable
    │  → 顺序写磁盘（极快）
    │
    ↓
7. Level 0 文件数超限（默认 4 个）→ 触发 Compaction
```

**写入延迟**：步骤 1-3 完成 → 客户端返回。
- WAL fsync ≈ 1-10ms（唯一磁盘 IO）
- MemTable insert ≈ 微秒级（内存）
- **总延迟 ≈ fsync 延迟**

对比 B+ 树写入延迟：
- 找到目标页（随机读 ≈ 10ms）
- 修改 + 分裂（随机写 ≈ 10ms）
- fsync WAL ≈ 1-10ms
- **总延迟 ≈ 20-30ms**

**LSM 写入比 B+ 快 2-3 倍**（主要省了随机写）。

---

## 四、读取路径

```
client: Get("key")
    │
    ↓
1. 查 MemTable（内存跳表）
    │  → 找到？返回 ✅
    │  → 没找到 ↓
    ↓
2. 查 Immutable MemTable（内存）
    │  → 找到？返回 ✅
    │  → 没找到 ↓
    ↓
3. 查 Level 0 SSTable（磁盘，可能有重叠）
    │  → 对每个文件二分 index → 读 block → bloom filter → 二分 key
    │  → 找到？返回 ✅
    │  → 没找到 ↓
    ↓
4. 查 Level 1 SSTable（磁盘，有序不重叠）
    │  → 二分找到唯一可能的文件 → 读 block → bloom filter → key
    │  → 找到？返回 ✅
    │  → 没找到 ↓
    ↓
5. 查 Level 2...N（越来越慢）
```

**读取放大**：最坏要查 N 层，每层可能有多次 IO。

优化：
- **Bloom Filter**：快速判断 key 是否"可能在"这个 SSTable（99% 概率排除）
- **Block Cache**：缓存热 data block（LRU）
- **Table Cache**：缓存打开的文件 fd

**LSM 读取比 B+ 慢**——因为要查多层。但 bloom filter + cache 把大多数读取优化到只查 MemTable 或 Level 0。

---

## 五、Compaction（核心复杂度所在）

### Minor Compaction（Level 0 → Level 1）

```
Level 0（4 个文件，可能有 key 重叠）:
  file_006: [apple, banana, cherry]
  file_007: [banana, dog, elephant]  ← 和 file_006 重叠！
  file_008: [apple, cat, fish]
  file_009: [dog, grape]

         ↓ Minor Compaction（合并排序）

Level 1（有序不重叠）:
  file_010: [apple, banana, cat]     ← 合并 file_006-009 的结果
  file_011: [cherry, dog]
  file_012: [elephant, fish, grape]
```

### Major Compaction（Level N → Level N+1）

```
Level 1（2MB，10 个文件）:
  [A-E] [E-J] [J-P] [P-Z]...

Level 2（20MB，100 个文件）:
  [A-B] [B-D] [D-F]...               ← 和 Level 1 的 [A-E] 重叠

         ↓ Major Compaction

Level 2（更新后）:
  [A-B'] [B'-D'] [D'-E'] [E-J']...   ← 合并后的新文件
```

### Compaction 的代价

- **写放大**：同一个 key 被写多次（每层 compaction 一次）
  - LevelDB 默认 7 层 → 同一个 key 最多被写 7 次
  - 对比 B+ 树：一个 key 只写一次（原地更新）

- **空间放大**：旧版本 key 在 compaction 前占空间
  - LSM 是"追加写" → 同一个 key 有多个版本
  - compaction 后才清理旧版本

- **读放大**：查多层
  - bloom filter 缓解大部分

**这就是 LSM 的三重放大（Write/Space/Read Amplification）**——是它用"顺序写"换来的代价。

---

## 六、B+ 树 vs LSM 树：终极对比

| 维度 | B+ 树（SQLite/PG/MySQL） | LSM 树（LevelDB/RocksDB/Cassandra） |
|------|--------------------------|-------------------------------------|
| 写入 | 随机写（找页→改→fsync） | 顺序写（WAL+MemTable） |
| 读取 | O(log N)，1-2 次 IO | O(log N)，但可能多层 |
| 写延迟 | ~10-30ms | ~1-10ms |
| 读延迟 | ~1-10ms | ~1-50ms（看命中哪层） |
| 写放大 | 1×（原地更新） | 7-10×（多层 compaction） |
| 读放大 | 1× | 1-7×（多层查找） |
| 空间放大 | 1×（原地） | 1.5-3×（旧版本未清理） |
| 最佳场景 | 读多写少 | 写多读少 |

### 选择指南

```
你的场景是读多还是写多？
    │
    ├── 读 >> 写（如：用户资料、商品信息）
    │   → B+ 树（PostgreSQL/MySQL）
    │
    ├── 写 >> 读（如：日志、事件、监控数据）
    │   → LSM（RocksDB/Cassandra）
    │
    └── 读写均衡
        → 看数据量。小→B+树更简单；大→LSM 更可扩展
```

---

## 七、和 csdiy 知识的交叉

### db-程序员视角 §一（B+ 树）

csdiy 精读从"慢 SQL"反推 B+ 树。这篇精读从"B+ 树的不足"引出 LSM。

**连接问题**：为什么 MySQL（B+ 树）适合 OLTP，而 Cassandra（LSM）适合时序数据？
- OLTP：读多写少，B+ 树读取更快
- 时序：写多读少，LSM 写入更快

### db-程序员视角 §六（WAL）

tinydb 的 WAL 和 LevelDB 的 WAL **完全同构**：
- 都是追加写（顺序 IO）
- 都在数据修改前先写 WAL
- 都用 fsync 保证持久化

**区别**：
- tinydb/B+ 树的 WAL 是"防 crash 的保险"——数据最终写到 B+ 树页
- LevelDB 的 WAL + MemTable **本身就是写入路径**——数据先在内存，后台才搬到磁盘

### tinydb/btree.py vs LevelDB

```
tinydb/btree.py（你刚实现的 B+ 树）:
  insert → 找叶子 → 插入 → 分裂 → 可能随机写
  search → 树遍历 O(log N) → 1-2 次 IO

LevelDB（LSM 树）:
  insert → WAL 追加 + MemTable 内存写 → 返回（无随机 IO）
  search → MemTable → Immutable → L0 → L1 → ... → 可能多次 IO
```

**你已经亲手实现了 B+ 树（tinydb/btree.py）**。现在理解了 LSM 的区别——你就能回答面试题："为什么 RocksDB 比 InnoDB 写入快？"

---

## 八、在 tinydb 里加 LSM 模式（未来方向）

如果你想给 tinydb 加 LSM 支持，核心步骤：

```python
# projects/tinydb/lsm.py（未来实现）

class LSMEngine:
    def __init__(self):
        self.wal = open("data.wal", "ab")
        self.memtable = SkipList()  # 或 sorted dict
        self.immutable = None
        self.levels = [[] for _ in range(7)]

    def put(self, key, value):
        # 1. WAL 追加
        self.wal.write(encode(key, value))
        self.wal.flush()
        os.fsync(self.wal.fileno())
        # 2. MemTable 插入
        self.memtable.insert(key, value)
        # 3. 满了 → flush
        if self.memtable.size > 4 * 1024 * 1024:  # 4MB
            self._flush()

    def get(self, key):
        # 1. MemTable
        val = self.memtable.get(key)
        if val is not None: return val
        # 2. Immutable
        if self.immutable:
            val = self.immutable.get(key)
            if val is not None: return val
        # 3. Level 0 → N
        for level in self.levels:
            for sst in level:
                val = sst.get(key)
                if val is not None: return val
        return None
```

---

## 九、一句话总结

> B+ 树优化读取（原地更新，1 次查询），LSM 树优化写入（顺序追加，后台整理）。
>
> LevelDB 的写入 = WAL 追加 + MemTable 内存写 → 1 次 fsync，没有随机 IO。
> 代价 = 读取多层查找 + compaction 写放大。
>
> 你已经在 tinydb/btree.py 实现了 B+ 树。理解 LSM，你就理解了现代存储引擎的两大阵营——所有数据库都在这之间做权衡。

---

*配套：[sqlite-btree-逐行拆解.md](sqlite-btree-逐行拆解.md) | [tinydb/btree.py](../projects/tinydb/btree.py) | [db-程序员视角](../notes/db-程序员视角-从慢SQL到原理.md)*
