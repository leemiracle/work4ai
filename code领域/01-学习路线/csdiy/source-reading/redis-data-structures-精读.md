# Redis 数据结构精读：SDS / Ziplist / Skiplist / Dict

> Redis 不只用一种数据结构——它为每种场景设计了最优结构。
> 这篇精读拆解 5 种核心结构，回答"为什么 Redis 单线程还能这么快"。
>
> 配套：[redis-eventloop-逐行拆解.md](redis-eventloop-逐行拆解.md) | [tinycache](../projects/tinycache/) | [tinydb/btree.py](../projects/tinydb/btree.py)
> csdiy 对应：csapp Ch2(位级) + Ch6(cache) + patterns §7(享元/对象池)

---

## 一、Redis 数据结构全景

```
Redis 命令           底层结构（根据数据量自动切换）
──────────────────────────────────────────────────────
SET key val       → SDS（字符串）
LPUSH list val    → Quicklist（小: Ziplist, 大: Listpack 链表）
SADD set val      → Intset（全整数）或 Dict（哈希表）
HSET field val    → Ziplist（小）或 Dict（大）
ZADD score val    → Ziplist（小）或 Skiplist+Dict（大）
```

**核心设计哲学**：不是一种结构打天下，而是**根据数据特征自动选择最优结构**。

| 结构 | 用在哪 | 时间复杂度 | 空间效率 |
|------|--------|-----------|---------|
| **SDS** | 字符串 key/value | O(1) strlen/append | 高（预分配） |
| **Ziplist** | 小 list/hash/zset | O(N) 但 N≤128 时极快 | 极高（连续内存） |
| **Quicklist** | 大 list | O(1) 头尾, O(N) 中间 | 高（分段 ziplist） |
| **Dict** | hash/set | O(1) 平均 | 中（有负载因子） |
| **Skiplist** | zset | O(log N) | 中（多级指针） |
| **Intset** | 纯整数 set | O(log N) 二分 | 极高（紧凑数组） |

---

## 二、SDS（Simple Dynamic String）

### 为什么不用 C 的 char*

C 字符串 `char*` 的问题：
1. `strlen()` 是 O(N)（遍历到 `\0`）
2. 没有 binary safe（`\0` 截断）
3. 容易缓冲区溢出（`strcat` 不检查长度）
4. 频繁 realloc（每次 append 都可能扩容）

### SDS 结构

```c
// 参照 Redis sds.h
struct sdshdr {
    uint32_t len;      // 已使用长度 → O(1) strlen
    uint32_t alloc;    // 分配总长度 → 空间预分配
    char flags;        // 类型（sdshdr5/8/16/32/64）
    char buf[];        // 实际数据（binary safe）
};
```

### 关键优化

**1. O(1) strlen**
```c
size_t sdslen(const sds s) {
    return SDS_HDR(s)->len;  // 直接读字段，不遍历
}
```
Redis 每处需要 key 长度的地方（hash、比较、拷贝）都是 O(1)。

**2. 空间预分配（空间换时间）**

```c
// sds.c: sdsMakeRoomFor（简化）
sds sdsMakeRoomFor(sds s, size_t addlen) {
    size_t free = SDS_HDR(s)->alloc - SDS_HDR(s)->len;
    if (free >= addlen) return s;  // 够用，不扩

    size_t newlen = SDS_HDR(s)->len + addlen;
    if (newlen < SDS_MAX_PREALLOC)  // < 1MB
        newlen *= 2;                // 2 倍扩容
    else
        newlen += SDS_MAX_PREALLOC; // 每次加 1MB
    // realloc
}
```

**预分配的效果**：
- 连续 append N 次：C 字符串 O(N²) realloc，SDS O(N) amortized
- 这就是 Redis `APPEND` 命令快的原因

**3. 惰性释放**
SDS 缩短时不立即 free，只减小 `len`。下次 append 时复用。
（参照 patterns §7 享元/对象池：复用比回收快）

**4. 类型分级（sdshdr5/8/16/32/64）**

```c
// 小字符串用 1 字节存长度（sdshdr8），大字符串用 4 字节（sdshdr32）
// 节省内存：100 万个短 key × 3 字节省 = 3MB
```

csdiy 交叉：csapp Ch2（位级表示）—— SDS 的 flags 字段就是"用最少的 bit 存类型"。

---

## 三、Ziplist（压缩列表）

### 为什么不用普通链表

普通链表（`struct Node { void* val; Node* next; }`）的问题：
1. 每个节点 2 个指针 = 16 字节开销（64 位系统）
2. 指针追逐（pointer chasing）→ cache miss 频繁
3. 内存碎片化（每个节点单独 malloc）

### Ziplist 结构

```
Ziplist = 连续内存块
┌─────────┬──────────┬─────────┬────────┬─────────┬────────┐
│ zlbytes │ zltail   │ zllen   │ entry1 │ entry2  │ zlend  │
│ 4 bytes │ 4 bytes  │ 2 bytes │        │         │ 1 byte │
└─────────┴──────────┴─────────┴────────┴─────────┴────────┘

每个 entry:
┌──────────────┬──────────────┬─────────┐
│ prevlen      │ encoding     │ data    │
│ 1 or 5 bytes │ 1+ bytes     │ 变长    │
└──────────────┴──────────────┴─────────┘
```

**关键设计**：
- **连续内存**：整个列表在一个 malloc 块里 → cache 友好
- **prevlen**：前一个 entry 的长度 → 支持反向遍历
- **encoding**：变长编码，小整数用 1 字节，大整数用 5 字节
- **无指针**：靠偏移量导航 → 省内存

### 性能特征

| 操作 | 复杂度 | 实际表现 |
|------|--------|---------|
| 头部插入 | O(N)（要移动后面所有数据） | N<128 时极快（数据在 cache 里） |
| 尾部插入 | O(1)（zltail 直接定位） | 极快 |
| 随机访问 | O(N)（从头遍历） | N<128 时可接受 |
| 内存效率 | 无指针开销 | 比链表省 50%+ 内存 |

**为什么 N<128 时 O(N) 反而比 O(1) 快？**

csdiy 交叉：csapp Ch6（存储器层次结构）。
- Ziplist 连续内存 → 一个 cache line（64B）能装 8-16 个 entry
- 链表每个节点在不同地址 → 每次访问可能 cache miss
- **cache miss（~100ns）远大于遍历 128 个连续 entry（~50ns）**
- 这就是"数据局部性"的力量

### Redis 的自动切换

```c
// 参照 Redis t_hash.c
#define OBJ_HASH_MAX_ZIPLIST_ENTRIES 128  // 超过 → 转 Dict
#define OBJ_HASH_MAX_ZIPLIST_VALUE   64   // 单个 value >64B → 转 Dict

// 每次写入后检查
void hashTypeTryConversion(robj *o, ...) {
    if (o->encoding == OBJ_ENCODING_ZIPLIST) {
        if (ziplistLen(o->ptr) > hash_max_ziplist_entries ||
            sdslen(value) > hash_max_ziplist_value) {
            // 转成 Dict（哈希表）
            hashTypeConvert(o, OBJ_ENCODING_HASHTABLE);
        }
    }
}
```

**设计哲学**：小数据用紧凑结构（省内存+cache 友好），大数据用高效结构（O(1) 访问）。

---

## 四、Skiplist（跳表）

### 用在哪

Redis 的 `ZSET`（有序集合）底层。`ZADD/ZRANK/ZRANGEBYSCORE` 的核心。

### 为什么不用红黑树

| 维度 | 红黑树 | 跳表 |
|------|--------|------|
| 复杂度 | O(log N) | O(log N) 期望 |
| 实现复杂度 | 高（旋转+着色） | 低（随机层级+链表） |
| 范围查询 | 不友好（要中序遍历） | 极友好（底层链表遍历） |
| 并发友好 | 差（旋转锁整棵子树） | 好（局部加锁） |
| 内存 | 每节点 2 指针 | 每节点 ~1.33 指针（平均） |

Redis 作者 antirez 的原话：*"They are simpler to implement, and marginally faster."*

### 跳表结构

```
Level 3:  HEAD ────────────────────── 30 ──────────── NIL
Level 2:  HEAD ─────── 10 ────────── 30 ────── 50 ── NIL
Level 1:  HEAD ── 5 ── 10 ── 20 ── 30 ── 40 ── 50 ── NIL
Level 0:  HEAD ── 5 ── 10 ── 20 ── 30 ── 40 ── 50 ── NIL  ← 完整链表
```

查找 `40`：
1. Level 3: HEAD → 30（< 40，继续）
2. Level 3: 30 → NIL（降级）
3. Level 2: 30 → 50（> 40，降级）
4. Level 1: 30 → 40（== 40，找到！）

**只需 4 次比较**，而不是遍历整条链表。

### Redis 的跳表实现

```c
// 参照 Redis server.h
typedef struct zskiplistNode {
    sds ele;                           // 元素值
    double score;                      // 分数（排序依据）
    struct zskiplistLevel {
        struct zskiplistNode *forward;  // 前进指针
        unsigned long span;             // 跨度（用于 ZRANK）
    } level[];                         // 多级指针（柔性数组）
    struct zskiplistNode *backward;     // 后退指针（反向遍历）
} zskiplistNode;

typedef struct zskiplist {
    zskiplistNode *header, *tail;
    unsigned long length;
    int level;  // 当前最大层级
} zskiplist;
```

**关键设计**：
- **span（跨度）**：记录每级指针跳过了多少节点 → `ZRANK` 命令 O(log N)
- **backward（后退指针）**：Level 0 的前驱 → `ZREVRANGE` 支持
- **score + ele 双排序**：先按 score 排，score 相同按 ele 字典序

### 随机层级生成

```c
// 参照 Redis t_zset.c: zslRandomLevel
int zslRandomLevel(void) {
    int level = 1;
    while ((random() & 0xFFFF) < (ZSKIPLIST_P * 0xFFFF))  // P=0.25
        level++;
    return (level < ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
}
```

P=0.25 意味着每个节点有 25% 概率再升一层。
- 平均每节点 1/(1-0.25) = 1.33 个指针
- 最高 32 层（ZSKIPLIST_MAXLEVEL=32）

### 和 tinydb/btree.py 的对比

你实现的 B+ 树和跳表都是有序结构，但：

| 维度 | B+ 树 | 跳表 |
|------|-------|------|
| 精确复杂度 | O(log N) 保证 | O(log N) 期望 |
| 数据存储 | 叶子节点存数据 | 每个节点都存数据 |
| 范围查询 | 叶子链表 | 底层链表 |
| 分裂 | 需要（插入时） | 不需要（随机层级） |
| 适合 | 磁盘（page 对齐） | 内存（指针灵活） |

**B+ 树适合磁盘（页对齐，减少 IO），跳表适合内存（无分裂，实现简单）。** 这就是为什么数据库用 B+ 树而 Redis 用跳表。

---

## 五、Dict（哈希表）

### Redis Dict vs tinydb/tinycache 的哈希表

你在 tinycache 里实现了 `CacheDict`（链地址法）。Redis 的 Dict 更精巧：

### 结构

```c
// 参照 Redis dict.h
typedef struct dict {
    dictht ht[2];       // 两个哈希表！用于渐进式 rehash
    long rehashidx;     // -1 = 没在 rehash
    // ...
} dict;

typedef struct dictht {
    dictEntry **table;   // 桶数组
    unsigned long size;  // 桶数（2 的幂）
    unsigned long used;  // 已存 entry 数
} dictht;
```

### 渐进式 Rehash（Redis 的杀手锏）

普通哈希表扩容时：一次性 rehash 所有 entry → 如果有 1000 万 key，服务卡顿几秒。

Redis 的方案：**用两个哈希表，逐步搬迁**。

```
扩容前：
  ht[0]: [A] [B] [C] [D]  size=4, used=4
  ht[1]: 空

扩容触发（负载因子 > 1）：
  ht[0]: [A] [B] [C] [D]  size=4  ← 旧表（查询时也查这里）
  ht[1]: [.] [.] [.] [.] [.] [.] [.] [.]  size=8  ← 新表

渐进式搬迁（每次操作搬 1 个桶）：
  第 1 次 PUT：搬 ht[0][0] → ht[1]，rehashidx=1
  第 2 次 GET：搬 ht[0][1] → ht[1]，rehashidx=2
  ...
  第 4 次操作：搬完，rehashidx=-1，ht[0]←ht[1]，ht[1]←空
```

```c
// 参照 Redis dict.c: _dictRehashStep（每次操作搬一个桶）
int dictRehash(dict *d, int n) {
    while (n-- > 0 && d->ht[0].used > 0) {
        // 找到 ht[0] 中第一个非空桶
        while (d->ht[0].table[d->rehashidx] == NULL)
            d->rehashidx++;
        // 把这个桶的所有 entry 搬到 ht[1]
        dictEntry *de = d->ht[0].table[d->rehashidx];
        while (de) {
            dictEntry *next = de->next;
            // 重新 hash 到 ht[1]
            uint32_t h = dictHashKey(d, de->key) & d->ht[1].sizemask;
            de->next = d->ht[1].table[h];
            d->ht[1].table[h] = de;
            d->ht[0].used--;
            d->ht[1].used++;
            de = next;
        }
        d->ht[0].table[d->rehashidx] = NULL;
        d->rehashidx++;
    }
    // 检查是否搬完
    if (d->ht[0].used == 0) {
        zfree(d->ht[0].table);
        d->ht[0] = d->ht[1];
        _dictReset(&d->ht[1]);
        d->rehashidx = -1;
        return 0;  // 搬完了
    }
    return 1;  // 还没搬完
}
```

**效果**：
- 1000 万 key 的 rehash 分散到 1000 万次操作里
- 每次操作只多搬 1 个桶 → 用户无感
- **Redis 不卡顿的秘密之一**

csdiy 交叉：patterns §3（装饰器）—— `dictFind` 在 rehash 期间同时查两个表，对调用者透明。

### SipHash（安全哈希）

Redis 4.0+ 用 SipHash 防止 hash 碰撞攻击（参照 tinyencrypt 的 SHA-256 实现）。

```
攻击场景：攻击者构造大量 hash 相同的 key → 全在同一个桶 → 链表变长 → O(N) 查找 → DoS
防御：SipHash 带随机种子 → 攻击者无法预测 hash 值
```

---

## 六、Intset（整数集合）

当 SET 的所有元素都是整数且数量 ≤ 512 时，Redis 用 Intset 而非 Dict。

```c
// 参照 Redis intset.h
typedef struct intset {
    uint32_t encoding;  // INTSET_ENC_INT16/32/64
    uint32_t length;
    int8_t   contents[];  // 有序整数数组（紧凑存储）
} intset;
```

**升级机制**：
```
初始：intset ENC_INT16 [1, 5, 10]  → 每元素 2 字节 = 6 字节
插入 70000：需要 ENC_INT32
  → 全部升级为 4 字节：[1, 5, 10, 70000] = 16 字节
```

**为什么不用 Dict？**
- 100 个整数：Dict 需要 128 个桶 × 8 字节 + 100 个 entry × 32 字节 = 4352 字节
- Intset：100 × 2 字节 = 200 字节
- **省 20 倍内存**

csdiy 交叉：csapp Ch6（存储器层次结构）—— 紧凑数组 → cache 友好 → 虽然是 O(log N) 二分查找，但实际极快。

---

## 七、综合对比表

| 结构 | Redis 命令 | 适合数据量 | 查找 | 范围 | 内存 | 实现难度 |
|------|-----------|-----------|------|------|------|---------|
| SDS | SET/GET | 任意 | O(1) | N/A | 高 | ⭐ |
| Ziplist | 小 HASH/LIST/ZSET | <128 | O(N)* | 友好 | 极高 | ⭐⭐ |
| Quicklist | LIST | 任意 | O(N) | 友好 | 高 | ⭐⭐⭐ |
| Dict | HASH/SET | 任意 | O(1) | N/A | 中 | ⭐⭐⭐ |
| Skiplist | ZSET | 任意 | O(log N) | 极好 | 中 | ⭐⭐⭐⭐ |
| Intset | 整数 SET | <512 | O(log N) | 排序 | 极高 | ⭐⭐ |

*O(N) 但 N<128 时因 cache 局部性实际比 O(1) 快。

---

## 八、一句话总结

> Redis 快不只是因为"单线程+epoll"（事件循环），更因为**为每种场景设计了最优数据结构**：
> - 小数据用 Ziplist/Intset（紧凑+cache 友好）
> - 大数据用 Dict/Skiplist（高效访问）
> - 字符串用 SDS（O(1) strlen + 预分配）
> - 扩容用渐进式 rehash（无卡顿）
>
> **数据结构的选择比算法优化重要 100 倍。** 这是 Redis 给所有工程师的启示。

---

*配套：[redis-eventloop-逐行拆解.md](redis-eventloop-逐行拆解.md) | [tinycache](../projects/tinycache/) | [tinydb/btree.py](../projects/tinydb/btree.py)*
