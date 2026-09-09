# Bloom Filter 精读：用 1KB 内存判断 100 万元素是否存在

> 一个"可能有"或"肯定没有"的概率数据结构。LevelDB/Cassandra/HBase 的读加速核心。
>
> csdiy 对应：db §三(索引失效) + csapp Ch6(缓存) + tinysearch/tinydb

---

## 一、问题：判断 key 是否存在

传统方案：
| 方案 | 空间 | 查询 | 问题 |
|------|------|------|------|
| Hash Set | O(N) | O(1) | 100 万 key × 100B = 100MB |
| B+ 树索引 | O(N) | O(log N) | 需要 2-3 次磁盘 IO |
| 排序数组+二分 | O(N) | O(log N) | 插入昂贵 |

**Bloom Filter 的方案**：用 **1MB** 判断 100 万 key——可能有假阳性（说存在但不存在），但绝无假阴性（说不存在就一定不存在）。

---

## 二、原理

### 结构

```
BitSet（m 位，初始全 0）:
[0][0][0][0][0][0][0][0][0][0][0][0]...

k 个独立的哈希函数：h1, h2, ..., hk
```

### 插入 key

```
INSERT("hello"):
  h1("hello") % m = 3    → bit[3] = 1
  h2("hello") % m = 7    → bit[7] = 1
  h3("hello") % m = 11   → bit[11] = 1
```

### 查询 key

```
QUERY("hello"):
  h1("hello") % m = 3    → bit[3] == 1 ✅
  h2("hello") % m = 7    → bit[7] == 1 ✅
  h3("hello") % m = 11   → bit[11] == 1 ✅
  → "可能存在"（三个位都是 1）

QUERY("world"):
  h1("world") % m = 5    → bit[5] == 0 ❌
  → "肯定不存在"（只要有一个 0 就一定不存在）
```

### 为什么有假阳性

```
INSERT("apple"):  bit[3]=1, bit[7]=1, bit[11]=1
INSERT("banana"): bit[3]=1, bit[9]=1, bit[15]=1

QUERY("orange"):
  h1("orange")%m=3  → bit[3]==1 ✅（被 apple/bana 设置）
  h2("orange")%m=7  → bit[7]==1 ✅（被 apple 设置）
  h3("orange")%m=11 → bit[11]==1 ✅（被 apple 设置）
  → "可能存在" 但实际不存在 → 假阳性！
```

### 假阳性率公式

```
fp = (1 - e^(-kn/m))^k

k = 哈希函数数量
n = 元素数量
m = bitset 大小（位）

最优 k = (m/n) * ln(2) ≈ 0.693 * (m/n)
```

**示例**：100 万元素，1MB bitset（800 万位）：
- m/n = 8
- 最优 k = 0.693 × 8 ≈ 5.5 → 用 6 个哈希
- 假阳性率 ≈ 0.022（2.2%）

---

## 三、LevelDB 中的应用

LevelDB 每个 SSTable 文件附带一个 Bloom Filter。

```
查询 key=42:
  ① 查 MemTable → 没找到
  ② 查 Level 0 → 对每个 SSTable:
     → 先查 Bloom Filter（内存，O(k)）
     → "肯定不在" → 跳过这个 SSTable（省磁盘 IO！）
     → "可能在" → 读 SSTable 的 data block
  ③ 查 Level 1 → ...
```

**效果**：99% 的 Level 0 文件被 Bloom Filter 过滤掉，不需要读磁盘。

---

## 四、Python 实现（60 行）

```python
import mmh3  # MurmurHash3（非加密哈希，极快）
import math

class BloomFilter:
    def __init__(self, capacity: int, fp_rate: float = 0.01):
        """
        capacity: 预期元素数量
        fp_rate: 可接受的假阳性率
        """
        self.capacity = capacity
        self.fp_rate = fp_rate
        # 计算最优 m 和 k
        self.m = int(-capacity * math.log(fp_rate) / (math.log(2) ** 2))
        self.k = int(self.m / capacity * math.log(2))
        self.bits = bytearray(self.m // 8 + 1)

    def _hashes(self, key: str):
        """k 个哈希值（用 double hashing 技巧，只需 2 次真实哈希）"""
        h1, h2 = mmh3.hash64(key.encode())
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, key: str):
        for idx in self._hashes(key):
            self.bits[idx // 8] |= (1 << (idx % 8))

    def contains(self, key: str) -> bool:
        """True = 可能存在；False = 肯定不存在"""
        for idx in self._hashes(key):
            if not (self.bits[idx // 8] & (1 << (idx % 8))):
                return False  # 只要有一个 0 → 肯定不存在
        return True  # 所有位都是 1 → 可能存在
```

---

## 五、变体

| 变体 | 特点 | 用在哪 |
|------|------|--------|
| Counting BF | 每位用计数器（支持删除） | |
| Cuckoo Filter | 支持删除 + 更高空间效率 | Bloom Filter 的竞争者 |
| Spectral BF | 记录元素频率 | 热点检测 |

---

## 六、一句话总结

> Bloom Filter 用 k 个哈希 + bitset 实现 O(1) 的"可能存在/肯定不存在"判断。
>
> 1MB 100 万 key × 1% 假阳性 → 省掉 99% 的磁盘 IO。LevelDB/Cassandra/HBase 全靠它加速读取。

---

*配套：[leveldb-lsm-精读.md](leveldb-lsm-精读.md) | [tinysearch](../projects/tinysearch/) | [tinydb](../projects/tinydb/)*
