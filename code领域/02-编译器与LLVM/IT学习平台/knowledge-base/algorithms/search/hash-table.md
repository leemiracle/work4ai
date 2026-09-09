# 哈希表

## 基本信息
- **分类**: 数据结构 -> 查找优化
- **时间复杂度**: O(1) 平均, O(n) 最坏
- **空间复杂度**: O(n)

## 核心概念
哈希表通过哈希函数将键映射到数组索引，实现快速查找、插入和删除操作。

## 关键组件
1. **哈希函数**: 将输入映射到固定范围
2. **桶数组**: 存储实际数据
3. **冲突解决**: 链地址法或开放寻址法

## 冲突解决策略

### 链地址法
每个桶存储链表，冲突时添加到链表末尾
```python
class HashTable:
    def __init__(self, size=1000):
        self.size = size
        self.buckets = [[] for _ in range(size)]
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def insert(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
```

### 开放寻址法
冲突时寻找下一个可用桶（线性探测、二次探测、双重哈希）
```python
class OpenAddressingHashTable:
    def __init__(self, size=1000):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
    
    def _hash(self, key, attempt=0):
        return (hash(key) + attempt) % self.size
    
    def insert(self, key, value):
        attempt = 0
        while attempt < self.size:
            index = self._hash(key, attempt)
            if self.keys[index] is None or self.keys[index] == key:
                self.keys[index] = key
                self.values[index] = value
                return
            attempt += 1
        raise Exception("Table is full")
```

## 应用场景
- 缓存实现（Redis、Memcached）
- 快速查找（符号表、索引）
- 去重（集合、唯一值）
- 计数（频率统计）

## 性能优化
- **负载因子**: 保持在 0.7 以下，适时扩容
- **哈希函数**: 选择低冲突、快计算（MurmurHash、CityHash）
- **动态扩容**: 负载因子超过阈值时重新哈希

## 相关概念
- [[二叉搜索树]]
- [[平衡树]]
- [[布隆过滤器]]

## 经典实现
- Python: `dict`
- C++: `std::unordered_map`
- Java: `HashMap`
- JavaScript: `Map`

## 参考资源
- CLRS Chapter 11
- MIT 6.006 Lecture 8
- 《算法导论》第11章

## 练习题
- 实现 LRU 缓存
- 设计自定义哈希函数
- 解决哈希碰撞问题