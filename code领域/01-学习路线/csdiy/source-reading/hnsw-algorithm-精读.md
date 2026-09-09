# HNSW 精读：O(log N) 近似最近邻搜索

> 参照：Malkov & Yashunin 2018 / hnswlib / Pinecone
>
> csdiy 对应：tinyrag/vectorstore.py + bloom-filter精读 + consistent-hashing精读

---

## 一、问题：百万向量中找最相似的 K 个

```
给一个查询向量 q，从 N 个向量中找到最相似的 K 个。

精确方法（KNN）：计算 q 和所有 N 个向量的相似度 → 排序 → O(N)
N = 1,000,000 时，每次查询需要 100 万次计算。

近似方法（ANN）：牺牲一点精度 → O(log N)
N = 1,000,000 时，每次查询只需 ~20 次计算。
```

---

## 二、HNSW 的灵感：跳表 + 小世界图

### 跳表（Skip List）

用于有序数据的 O(log N) 查找：
```
Level 2: HEAD ──────────→ 30 ─────→ NIL     （稀疏）
Level 1: HEAD ───→ 10 ──→ 30 ─→ 50 → NIL   （中等）
Level 0: HEAD → 5 → 10 → 20 → 30 → 40 → 50 → NIL  （密集）
```

### 小世界图（Small World Graph）

六度分隔理论：任意两个人通过 ≤6 个中间人就能联系到。

**结合**：HNSW = 多层图（像跳表的层级）+ 每层是小世界图。

---

## 三、HNSW 结构

```
Layer 2 (最稀疏): A ──────────── D
Layer 1 (中等):   A ──── C ──── D ──── F
Layer 0 (最密集): A ─ B ─ C ─ D ─ E ─ F ─ G ─ H
```

**关键设计**：
- Layer 0 包含所有节点（密集连接 → 精确搜索）
- Layer L 只包含 ~1/e^L 比例的节点（稀疏 → 快速导航）
- 新节点有概率 e^{-L} 出现在 Layer L

---

## 四、搜索算法

```
search(q, K):
  ① 从最高层入口点开始（贪心搜索）
     current = entry_point
     for layer in range(max_layer, 0, -1):
         while True:
             neighbors = graph[layer][current].neighbors
             nearest = argmax(sim(q, neighbors))
             if sim(q, nearest) > sim(q, current):
                 current = nearest  # 贪心移动
             else:
                 break  # 局部最优

  ② 在 Layer 0 做精细搜索（ef-search 候选列表）
     candidates = BFS(q, current, ef=50)
     return top-K(candidates)
```

**时间复杂度**：O(log N)（类似跳表的层间导航 + Layer 0 的有限 BFS）。

---

## 五、插入算法

```
insert(x):
  ① 随机选择层级 l（几何分布）
     l = floor(-ln(random()) * mL)  # mL = 1/ln(M)

  ② 从最高层到 l+1 层：贪心搜索找最近入口
  ③ 从 l 层到 0 层：
     - 找 M 个最近邻居 → 建立双向连接
     - 如果邻居连接数超过 Mmax：保留最近 Mmax 个（裁剪）

  ④ 如果 l > 当前最大层：更新入口点
```

---

## 六、你的 tinyrag/vectorstore.py 的 HNSW 实现

```python
class HNSWIndex(VectorStore):
    def _add_to_graph(self, new_id):
        # 随机层级
        level = 0
        while random.random() < 0.5 and level < 5: level += 1
        
        # 找最近 M 个邻居（暴力版，真实 HNSW 用图导航）
        scored = [(cosine_sim(new_emb, self.docs[i].embedding), i) 
                  for i in all_ids]
        scored.sort(key=lambda x: -x[0])
        
        # 双向连接 + 邻居数限制
        for _, neighbor_id in scored[:M]:
            self.graph[new_id].add(neighbor_id)
            self.graph[neighbor_id].add(new_id)
    
    def search(self, query_embedding, top_k=5, ef=20):
        # 贪心图搜索（从入口点开始）
        visited = set(); current = self.entry_point
        best = [(cosine_sim(query_embedding, ...), current)]
        for _ in range(ef * 3):
            neighbors = self.graph[current] - visited
            for n in neighbors:
                s = cosine_sim(query_embedding, ...)
                if s > best[0][0]:
                    current = n  # 移动到更近的邻居
        return sorted(best, reverse=True)[:top_k]
```

**差异**：真实 HNSW 用多层图导航（O(log N)），你的实现用单层图 + 贪心搜索（简化版）。

---

## 七、ANN 算法对比

| 算法 | 数据结构 | 查询 | 插入 | 精度 | 代表 |
|------|---------|------|------|------|------|
| **KNN** | 无（暴力） | O(N) | O(1) | 100% | FAISS IndexFlat |
| **HNSW** | 多层图 | O(log N) | O(log N) | 95-99% | hnswlib, Pinecone |
| **IVF** | 倒排索引 | O(N/k) | O(1) | 90-95% | FAISS IVF |
| **LSH** | 哈希桶 | O(1) | O(1) | 80-90% | Annoy |
| **PQ** | 乘积量化 | O(1) | O(1) | 70-90% | FAISS PQ |

**生产选择**：
- 小数据 (<100K)：KNN（精确，够快）
- 中等数据 (100K-10M)：HNSW（精度/速度平衡最佳）
- 海量数据 (>10M)：IVF+PQ（压缩存储，牺牲精度）

---

## 八、一句话总结

> HNSW = 跳表（多层导航）+ 小世界图（六度分隔）。
>
> 搜索：从高层稀疏图快速导航 → 到底层密集图精细搜索 → O(log N)。
>
> **RAG 系统的向量检索核心：Pinecone/Weaviate/Milvus 全用 HNSW 或其变体。**

---

*配套：[tinyrag/vectorstore.py](../projects/tinyrag/vectorstore.py) | [bloom-filter精读](bloom-filter-精读.md) | [consistent-hashing精读](consistent-hashing-精读.md)*
