# 存储引擎终极对比：B+ 树 vs LSM 树 vs SSTable vs 列式

> 一个文档讲清所有存储引擎的取舍。
>
> 配套：[sqlite-btree-逐行拆解.md](sqlite-btree-逐行拆解.md) | [leveldb-lsm-精读.md](leveldb-lsm-精读.md) | [tinydb/btree.py](../projects/tinydb/btree.py)
> csdiy 对应：db 全部 + csapp Ch6(存储器层次)

---

## 全景表

| 引擎 | 代表 | 写入 | 读取 | 空间 | 最佳场景 |
|------|------|------|------|------|---------|
| **B+ 树** | SQLite/MySQL/PG | 随机写 O(log N) | O(log N) 1-2 IO | 1× | 读多写少 |
| **LSM 树** | LevelDB/RocksDB/Cassandra | 顺序写 O(1) | O(N)→O(log N) | 1.5-3× | 写多读少 |
| **SSTable** | LevelDB 的磁盘层 | 批量写 | 二分+索引 | 高 | LSM 的底层 |
| **列式** | Parquet/ClickHouse | 批量写 | 列扫描 O(1) | 极高（压缩） | OLAP 分析 |
| **倒排** | Elasticsearch/Lucene | 追加写 | O(1) 查词 | 中 | 全文搜索 |
| **时间序列** | InfluxDB/TDengine | 顺序写 | 按时间 O(log N) | 高（压缩） | 监控数据 |

---

## 写入路径对比

### B+ 树写入
```
INSERT key=42
  → 找到目标叶子页（随机读 IO #1）
  → 修改页（内存）
  → 如果满了 → 分裂（随机写 IO #2）
  → WAL fsync（顺序写 IO #3）
  → 脏页延迟写回（随机写 IO #4，异步）

总延迟：10-30ms（2-3 次随机 IO）
```

### LSM 树写入
```
INSERT key=42
  → WAL 追加（顺序写 IO #1）
  → MemTable 写入（内存，零 IO）
  → 返回

总延迟：1-5ms（1 次顺序 IO）
```

### 结论
**LSM 写入比 B+ 快 3-5 倍**。代价是读取时要查多层。

---

## 读取路径对比

### B+ 树读取
```
SELECT WHERE key=42
  → 根页（可能 cache 命中）
  → 内部页（可能 cache 命中）
  → 叶子页（IO）
  → 找到

总延迟：1-10ms（1 次随机 IO，如果 cache 命中则零 IO）
```

### LSM 读取
```
SELECT WHERE key=42
  → MemTable（内存）
  → Immutable MemTable（内存）
  → Level 0 SSTable #1（bloom filter → 可能 IO）
  → Level 0 SSTable #2（bloom filter → 可能 IO）
  → Level 0 SSTable #3（bloom filter → 跳过 ✅）
  → Level 0 SSTable #4（bloom filter → 跳过 ✅）
  → Level 1 SSTable（bloom filter → 可能 IO）
  → Level 2+ ...（越来越不可能命中）

总延迟：0.1-50ms（看命中哪层）
```

### 结论
**B+ 读取比 LSM 稳定**（始终 1-2 次 IO）。LSM 读取范围大（0.1-50ms），但 bloom filter + cache 让大多数读取只查 MemTable。

---

## 三重放大对比

| 放大类型 | B+ 树 | LSM 树 | 说明 |
|---------|-------|--------|------|
| **写放大** | 1-3× | 7-30× | 同一 key 被写多少次 |
| **读放大** | 1-3× | 1-10× | 查一个 key 要多少次 IO |
| **空间放大** | 1× | 1.5-3× | 旧版本占多少额外空间 |

---

## 选择指南

```
你的场景？
│
├── OLTP（银行/电商/IM）
│   读多写少，需要事务
│   → B+ 树（MySQL/PostgreSQL）
│
├── 时序/日志（监控/IoT/事件）
│   写多读少，按时间查
│   → LSM（RocksDB/Cassandra/InfluxDB）
│
├── 全文搜索（搜索引擎/日志分析）
│   → 倒排索引（Elasticsearch）
│
├── OLAP（报表/BI/数据仓库）
│   批量读、聚合
│   → 列式（ClickHouse/Parquet）
│
└── 嵌入式（App 内置存储）
    → B+ 树（SQLite）或 LSM（LevelDB/rocksdb）
```

---

## 你造过的东西

| 你实现的 | 对应引擎 | 核心算法 |
|---------|---------|---------|
| tinydb/main.py | 线性扫描（最原始） | 遍历所有页 |
| tinydb/btree.py | **B+ 树** | 从根到叶子+分裂 |
| tinydb 的 WAL | WAL（增量日志） | 追加+fsync+checkpoint |
| tinycache/rdb.py | RDB 快照 | 全量序列化 |
| tinykafka | 追加日志（LSM 的前身） | 分区+消费组 |
| tinysearch | 倒排索引 | BM25 排序 |

**你已经亲手实现了 B+ 树、WAL、RDB、追加日志、倒排索引——存储引擎的核心组件。**

---

## 一句话总结

> B+ 树 = 读优（原地更新，1-2 次 IO 查找）
> LSM = 写优（顺序追加，后台整理）
> 倒排 = 搜优（词→文档映射）
> 列式 = 分析优（列压缩+向量化）
>
> **没有"最好的"存储引擎，只有"最合适的"。** 理解三重放大，你就能做对选择。

---

*配套：[sqlite-btree-逐行拆解.md](sqlite-btree-逐行拆解.md) | [leveldb-lsm-精读.md](leveldb-lsm-精读.md) | [tinydb/btree.py](../projects/tinydb/btree.py)*
