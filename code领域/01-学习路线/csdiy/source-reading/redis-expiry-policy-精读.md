# Redis 过期键策略精读：惰性删除 + 定期删除 + 内存淘汰

> Redis 怎么知道一个 key 过期了？什么时候删？内存不够了怎么办？
>
> 配套：[redis-data-structures-精读.md](redis-data-structures-精读.md) | [tinycache](../projects/tinycache/)
> csdiy 对应：os §四(page cache/定时任务) + patterns §9(状态机)

---

## 一、问题：100 万个 key 带 TTL，怎么高效过期？

### 方案 A：定时器（每个 key 一个 timer）
```
SET key val EX 3600 → 创建一个 3600 秒后的定时器
```
**问题**：100 万个定时器 → 大量 CPU 和内存开销。

### 方案 B：纯惰性（GET 时检查）
```
GET key → 检查是否过期 → 过期则删除并返回 nil
```
**问题**：如果某些 key 从不被 GET → 永远不删除 → 内存泄漏。

### 方案 C：Redis 的方案（惰性 + 定期）

Redis 用两种策略组合：

```
SET key val EX 3600
    ↓
（key 存入 dict，同时记录过期时间到 expires dict）

                    ┌──── 惰性删除 ────┐
                    │                   │
任何操作 key 时    │ GET/SET/SCAN...  │
    →              │ 检查 expires      │
                    │ 过期则删除        │
                    └───────────────────┘

                    ┌──── 定期删除 ────┐
                    │                   │
serverCron 10Hz    │ 随机抽 20 个 key  │
    →              │ 检查是否过期       │
                    │ 过期比例>25%→再来 │
                    └───────────────────┘
```

---

## 二、惰性删除（Lazy Expiration）

```c
// 参照 Redis db.c: expireIfNeeded
int expireIfNeeded(redisDb *db, robj *key) {
    if (!keyIsExpired(db, key)) return 0;

    // 主从模式下，从节点不主动删除（等主节点 DEL 命令）
    if (server.masterhost != NULL)
        return 1;  // 告诉调用者"key 已过期"，但不删

    // 删除 key（参照 db.c: deleteExpiredKey）
    dbDelete(db, key);  // 从 dict 和 expires 都删
    server.stat_expiredkeys++;
    propagateDeletion(db, key);  // 传播 DEL 给从节点+AOF
    notifyKeyspaceEvent(NOTIFY_EXPIRED, "expired", key, db->id);
    return 1;
}

// 每个读写操作前都调用
robj *lookupKey(redisDb *db, robj *key, int flags) {
    if (expireIfNeeded(db, key) == 1) {
        // key 已过期 → 返回 NULL
        return NULL;
    }
    return dictFind(db->dict, key->ptr);
}
```

**你的 tinycache 也实现了这个**（参照 tinycache/main.py 的 CacheDict.get）：
```python
# tinycache 的惰性过期
def get(self, key):
    entry = ...
    if entry.expire_at > 0 and time.time() > entry.expire_at:
        self._delete_at(idx, key)  # 过期 → 删除
        return None
    return entry.value
```

---

## 三、定期删除（Active Expiration）

```c
// 参照 Redis expire.c: activeExpireCycle
#define ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP 20
#define ACTIVE_EXPIRE_CYCLE_FAST_DURATION 1000  // μs

void activeExpireCycle(int type) {
    // 每次 serverCron 调用
    // 从每个 DB 随机抽样检查

    do {
        // 随机抽 20 个带 TTL 的 key
        for (int j = 0; j < ACTIVE_EXPIRE_CYCLE_KEYS_PER_LOOP; j++) {
            robj *key = dictGetRandomKey(db->expires);
            long ttl = getExpire(db, key);

            if (ttl < now) {
                // 过期了 → 删除
                dbDelete(db, key);
                expired++;
            }
            total++;

            // 如果 DB 里 key 不多了，提前退出
            if (total > sample_count) break;
        }

        // 百分比阈值：如果过期比例 > 25%，再来一轮
        // 参照 Redis "如果超过 25% 的抽样已过期 → 继续抽样"
        percentage_expired = expired / total;

    } while (percentage_expired > ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP / 4);
    // ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP = 20 → 阈值 = 5（25%）
}
```

**关键设计**：
- 每次 serverCron（100ms）抽 20 个 key → 极轻量
- 过期比例 > 25% → 多做几轮（自适应）
- 如果某些 key 永远不被抽样到 → 惰性删除兜底

**你的 tinycache 也实现了**：
```python
# tinycache 的定期删除
async def active_expire_loop(self):
    while True:
        deleted = self.data.active_expire(limit=100)
        await asyncio.sleep(1.0)  # 1 秒一次
```

---

## 四、内存淘汰（Eviction Policy）

当内存超过 `maxmemory` 限制时，Redis 需要主动淘汰一些 key。

### 8 种淘汰策略

| 策略 | 范围 | 算法 |
|------|------|------|
| `noeviction` | — | 不淘汰，写入直接报错 |
| `allkeys-lru` | 所有 key | LRU（最近最少使用） |
| `allkeys-lfu` | 所有 key | LFU（最少使用频率） |
| `allkeys-random` | 所有 key | 随机删除 |
| `volatile-lru` | 有 TTL 的 key | LRU |
| `volatile-lfu` | 有 TTL 的 key | LFU |
| `volatile-random` | 有 TTL 的 key | 随机 |
| `volatile-ttl` | 有 TTL 的 key | 删最快要过期的 |

### Redis 的近似 LRU

真正的 LRU 需要维护一个链表（每次访问都移到头部）→ 内存开销大。

Redis 用**近似 LRU**：
```c
// 参照 Redis evict.c
#define EVPOOL_SIZE 16  // 每次抽样 16 个 key

struct evictionPoolEntry {
    unsigned long long idle;  // 空闲时间（越大越该淘汰）
    sds key;
    int dbid;
};

int performEvictions(void) {
    while (server.used_memory > server.maxmemory) {
        // 随机抽 16 个 key → 选 idle 最大的淘汰
        for (int i = 0; i < EVPOOL_SIZE; i++) {
            key = dictGetRandomKey(db->dict);
            idle = estimateObjectIdleTime(key);
            // 更新 evictionPool（保持 idle 最小的被挤出）
            updateEvictionPool(pool, key, idle);
        }

        // 淘汰 pool 中 idle 最大的
        best = pool[0];  // pool 按 idle 降序排列
        dbDelete(db, best->key);
        freed++;
    }
}
```

**近似 LRU 的效果**：
- 不精确（只抽样 16 个，可能漏掉真正的 LRU）
- 但**足够好**（论文证明 10 个样本的近似 LRU 接近真实 LRU）
- **省内存**（不需要维护全局链表）

csdiy 交叉：[db §一](../notes/db-程序员视角-从慢SQL到原理.md) — 数据库的 buffer pool 也用类似的 LRU 变体（Clock/ARC/LRU-K）。

### LFU（Least Frequently Used）

Redis 4.0+ 新增。每个 key 记录访问频率（用 **Morris 计数器**做概率性递增）。

```c
// 参照 Redis object.c
#define LFU_GET_MLOGBITS(obj) ((obj)->lru & 0xff)  // 低 8 位存频率
#define LFU_GET_LDT(obj)      ((obj)->lru >> 8)    // 高 24 位存时间戳

void updateLFU(robj *obj) {
    long counter = LFU_GET_MLOGBITS(obj);
    // Morris 计数器：概率性递增（访问越多，递增概率越低）
    // 参照 csapp 位级操作
    double r = (double)rand() / RAND_MAX;
    double baseval = counter - LFU_INIT_VAL;
    if (baseval < 0) baseval = 0;
    double p = 1.0 / (baseval * server.lfu_log_factor + 1);
    if (r < p) counter++;

    // 衰减：长时间不访问 → 频率降低
    unsigned long age = elapsed() - LFU_GET_LDT(obj);
    counter = counter - (age * server.lfu_decay_time) / 60;

    LFU_SET_MLOGBITS(obj, counter);
}
```

---

## 五、和 tinycache 的对照

| 机制 | Redis | tinycache |
|------|-------|-----------|
| 惰性删除 | expireIfNeeded | CacheDict.get 检查 |
| 定期删除 | activeExpireCycle (10Hz) | active_expire_loop (1Hz) |
| 内存淘汰 | 8 种策略 | ❌ 未实现（未来方向） |
| 过期存储 | 独立 expires dict | DictEntry.expire_at 字段 |

**如果你想给 tinycache 加内存淘汰**：
```python
# 未来实现
class CacheDict:
    def evict_if_needed(self, max_memory: int):
        """LRU 淘汰（参照 Redis performEvictions）"""
        while self.used_memory > max_memory:
            # 随机抽 16 个 key
            samples = random.sample(self.table, min(16, self.size))
            # 淘汰最久没用的
            oldest = min(samples, key=lambda e: e.last_access)
            self.delete(oldest.key)
```

---

## 六、一句话总结

> Redis 的过期策略 = 惰性删除（GET 时检查）+ 定期删除（serverCron 抽样）+ 内存淘汰（近似 LRU/LFU）。
>
- **惰性**：保证 GET 永远不返回过期数据
- **定期**：保证不被访问的 key 最终被清理
- **淘汰**：保证内存不溢出
>
> 三者协作 → Redis 在有限内存里管理百万 TTL key，不泄漏不溢出。

---

*配套：[redis-data-structures-精读.md](redis-data-structures-精读.md) | [tinycache](../projects/tinycache/) | [redis-eventloop-逐行拆解.md](redis-eventloop-逐行拆解.md)*
