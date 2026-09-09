# 从零造 22 个系统：工程实践总结

> 把 22 个参照世界级开源项目的迷你实现，总结成可复用的工程经验。
>
> 这是 csdiy 的"毕业论文"——用费曼法，把学到的教给别人。

---

## 做了什么

22 个项目，每个参照一个真实开源项目：

```
网络层    tinyproxy(frp) · tinycache(Redis) · tinyhttpd(nginx) · tinydns(CoreDNS) · tinyrpc(gRPC)
存储层    tinydb(SQLite) · tinysearch(ES) · tinyvector(Pinecone) · tinykafka(Kafka)
系统层    tinyshell(bash) · tinydocker(Docker) · tinydebug(gdb)
分布式    tinyraft(etcd)
工具层    tinygit(git) · tinyprof(perf) · tinyjson(simdjson)
AI 层     tinyml(micrograd) · tinyinfer(vLLM)
语言层    tinycompiler(Lox) · tinyregex(RE2) · tinycompress(gzip)
安全层    tinyencrypt(OpenSSL)
```

---

## 学到的 10 个核心工程原则

### 1. 事件循环的本质是同一个骨架

Redis/nginx/Go/Python asyncio，所有高性能网络服务器的核心都是：
```
while True:
    events = epoll_wait()        # 等事件
    for event in events:
        handler = callback_table[event.fd]
        handler(event)           # 分发
    run_expired_timers()         # 定时任务
```

差异只在 dispatch 的方式（回调 vs goroutine vs coroutine）。

→ 参照：[eventloop-evolution-redis-nginx-go.md](../source-reading/eventloop-evolution-redis-nginx-go.md)

### 2. 存储引擎是三重放大的权衡

B+ 树优化读取（1× 写放大），LSM 优化写入（顺序追加）。没有银弹。

```
你的写入多吗？  → LSM（LevelDB/RocksDB）
你的读取多吗？  → B+ 树（SQLite/PostgreSQL）
你需要搜索吗？  → 倒排索引（Elasticsearch）
```

→ 参照：[storage-engine-comparison-精读.md](../source-reading/storage-engine-comparison-精读.md) + [tinydb/btree.py](tinydb/btree.py)

### 3. 数据结构的选择比算法优化重要 100 倍

Redis 为每种场景设计了最优结构：
- 小数据用 Ziplist（紧凑+cache 友好）
- 大数据用 Dict/Skiplist（O(1)/O(log N)）
- 纯整数用 Intset（省 20 倍内存）

**不要用一种结构打天下。**

→ 参照：[redis-data-structures-精读.md](../source-reading/redis-data-structures-精读.md)

### 4. WAL 是持久化的基石

所有可靠存储系统都用 WAL：
```
写操作 → WAL 追加（顺序写，极快）→ fsync → 内存修改 → 后台异步写数据页
```

crash 后 → 从 WAL 重放 → 恢复到一致状态。

→ 参照：tinydb（WAL 实现）+ [leveldb-lsm-精读.md](../source-reading/leveldb-lsm-精读.md)

### 5. 一致性哈希解决动态扩容

`hash(key) % N` 加节点时几乎全部重新分布。一致性哈希只影响相邻区间。

```
3 节点 → 4 节点：
  hash%3：~100% key 要迁移
  一致性哈希：~25% key 要迁移（只影响新区间）
```

→ 参照：[consistent-hashing-精读.md](../source-reading/consistent-hashing-精读.md)

### 6. RESP 协议的简洁美

Redis 的 RESP 协议极简：
```
*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n
```
人类可读 + 容易解析 + 无版本兼容包袱。

对比：Protobuf 需要 .proto 文件 + 代码生成。RESP 只要 readline() 就能解析。

→ 参照：tinycache 的 RESP 解析器

### 7. Thompson NFA 不回溯 → 不会 ReDoS

回溯正则引擎（PCRE/Python re）在恶意输入上可能 O(2^n)。Thompson NFA 保证 O(n×m)。

**安全关键场景（处理用户输入的正则）应该用 RE2。**

→ 参照：tinyregex（Thompson NFA 实现）

### 8. Bloom Filter 用 1KB 内存省 99% 磁盘 IO

LevelDB/Cassandra 在读 SSTable 前先查 Bloom Filter——"肯定不在"就跳过。

```
100 万元素，1MB bitset，1% 假阳性 → 省掉 99% 的磁盘 IO
```

→ 参照：[bloom-filter-精读.md](../source-reading/bloom-filter-精读.md)

### 9. 状态机 > if-else 链

当状态 > 3 且转移复杂时，状态机比 if-else 更清晰、更可测试。

```
TCP 11 状态 = 状态机
HTTP 解析 = 状态机
Raft 节点状态 = 状态机
编译器 Lexer = 状态机
```

→ 参照：[linux-tcp-state-machine-精读.md](../source-reading/linux-tcp-state-machine-精读.md) + tinyraft

### 10. 最好的学习方式是"从零造一个"

读 100 篇文章不如造 1 个系统。每个 tiny 项目都逼你理解：
- 设计决策的**为什么**（不只是怎么用）
- 工程**权衡**（没有银弹）
- **边界情况**（crash/并发/大输入）

→ 参照：你实现了 B+ 树分裂、WAL 恢复、RESP 解析、Thompson NFA、LZ77 压缩、SHA-256...

---

## 性能数据（你的实现）

| 操作 | 性能 | 对比 |
|------|------|------|
| B+ 树搜索 | 1.8M ops/s | 你实现的 O(log N) |
| B+ 树范围查询 | 30M ops/s | 叶子链表遍历 |
| LZ77 压缩率 | 25.14x | 4.5KB → 180B |
| SHA-256（纯 Python） | 6.8K ops/s | hashlib(C)的 1/330 |
| 正则匹配 | 134K ops/s | Thompson NFA |
| 倒排索引搜索 | 38K ops/s | 100 文档 BM25 |
| ML 前向+反向 | 118K ops/s | Value 类 autograd |

---

## 下一步（如果继续深化）

1. **给真实项目提 PR** — frp/Redis/gnet
2. **启动一个真实有用的项目** — 不再是"教学版"
3. **写英文博客** — 把这些经验分享给世界
4. **参与开源** — Socialization（SECI 的最后一块）

---

## 一句话总结

> 22 个项目 × 19 篇精读 × 26 个费曼挑战 = **从"读过"到"造过"到"理解了为什么"**。
>
> **最好的工程师不是读最多书的人，而是造过最多东西的人。**

---

*csdiy v1.0 — 22 projects · 19 deep-reads · 26 feynman challenges · 12/12 integration test · 95% coverage*
