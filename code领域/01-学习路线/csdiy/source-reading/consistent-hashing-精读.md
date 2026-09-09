# 一致性哈希精读：分布式存储的数据分布算法

> 为什么 Cassandra 加节点不需要 rehash 所有数据？一致性哈希。
>
> csdiy 对应：tinykafka(分区) + tinyraft(集群) + db §一(分片)

---

## 一、问题：N 个节点怎么分配数据？

### 方案 A：hash(key) % N

```
3 个节点，key="hello":
  hash("hello") % 3 = 1 → 存 node[1]

加一个节点（N=4）:
  hash("hello") % 4 = 2 → 存 node[2] ← 变了！
```

**灾难**：加/删一个节点 → **几乎所有 key 要重新分布**。

### 方案 B：一致性哈希

```
把 hash 空间弯成一个环（0 ~ 2^32-1）：

         node_A (hash=1000)
        /
node_C  ←──────→  node_B
(8000)              (5000)

key="hello" hash=3000:
  环上顺时针找 → 3000 之后第一个节点 = node_B(5000)
  → 存 node_B

加一个 node_D(hash=4000):
  key="hello" hash=3000:
  环上顺时针找 → 3000 之后第一个节点 = node_D(4000) ← 变了！
  但只有 [3000, 4000) 范围的 key 受影响 ← 只影响相邻区间！
```

**效果**：加/删节点只影响**相邻区间的 key**（~1/N），而不是全部。

---

## 二、虚拟节点（解决数据倾斜）

问题：如果只有 3 个物理节点，它们在环上的位置可能不均匀 → 某个节点承担 50% 的 key。

解法：每个物理节点对应 **150 个虚拟节点**（vnode）。

```python
# 3 个物理节点 × 150 vnode = 450 个环上位置
for node in ["node_A", "node_B", "node_C"]:
    for i in range(150):
        vnode_hash = hash(f"{node}#{i}")
        ring[vnode_hash] = node
```

**效果**：虚拟节点越多，分布越均匀（大数定律）。标准做法是 150-200 个 vnode/节点。

---

## 三、Python 实现（80 行）

```python
import hashlib, bisect

class ConsistentHash:
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}          # hash → node_name
        self.sorted_hashes = [] # 排序的 hash 值（用于二分查找）

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        """添加节点"""
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            self.ring[h] = node
            bisect.insort(self.sorted_hashes, h)

    def remove_node(self, node: str):
        """删除节点"""
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            del self.ring[h]
            idx = bisect.bisect_left(self.sorted_hashes, h)
            self.sorted_hashes.pop(idx)

    def get_node(self, key: str) -> str:
        """找 key 对应的节点（顺时针第一个）"""
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.sorted_hashes, h)
        if idx == len(self.sorted_hashes):
            idx = 0  # 环绕到环的起点
        return self.ring[self.sorted_hashes[idx]]
```

---

## 四、真实应用

| 系统 | 用一致性哈希做什么 |
|------|-----------------|
| Cassandra | 数据行 → 节点分布 |
| DynamoDB | partition 分配 |
| Memcached | key → cache 节点 |
| Riak | vnode 分布 |
| Discord (非游戏) | 消息路由 |

**和 Kafka 的分区不同**：Kafka 用 `hash(key) % partition_count`（因为 partition 是预定义的，不会动态增减）。Cassandra 用一致性哈希（节点动态增减）。

---

## 五、和 tinykafka/tinyraft 的交叉

### tinykafka 的分区

你的 tinykafka 用 `hash(key) % partition_count` 分配消息。这适合**固定分区数**的场景。

如果分区数会变化（动态扩容）→ 应该用一致性哈希。

### tinyraft 的集群

Raft 集群通常固定节点数。如果动态增减节点（如 etcd 的 member add/remove），需要：
1. 新节点加入 → 追赶日志（Snapshot + AppendEntries）
2. 不需要重新分布数据（Raft 是复制不是分片）

---

## 六、一句话总结

> 一致性哈希 = 把 hash 空间弯成环 + 顺时针找节点。加/删节点只影响相邻区间（~1/N），而非全部。
>
> 虚拟节点解决数据倾斜。150 vnode/节点 → 99% 均匀分布。

---

*配套：[tinykafka](../projects/tinykafka/) | [tinyraft](../projects/tinyraft/)*
