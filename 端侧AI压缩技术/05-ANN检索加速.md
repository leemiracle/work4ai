# 05 · ANN 检索加速：HNSW / IVF / Funnel Retrieval

> **本章核心**：从 100 万甚至 1 亿向量里找 top-K，**精确检索是 O(N·d)** 不可行。本章讲 4 种近似最近邻（ANN）算法、2 种二阶段检索、3 个端侧可用的库。

---

## 一、为什么需要 ANN

### 1.1 精确 KNN 的代价

100 万文档 × 768d × 4 字节 = 3 GB 库。每次检索：
- 100 万 × 768 FLOPs（点积）= 768 M FLOPs
- 中端手机 CPU ~10 GFLOPS → **每次检索 80ms+**

100 亿文档？80 秒。**不可行**。

### 1.2 ANN 的承诺

ANN（Approximate Nearest Neighbor）用空间换时间：
- 构建索引（离线）：几小时
- 查询（在线）：log N 或 sub-linear

**典型加速**：
- 100 万文档：80ms → 5ms（16× 加速）
- 1 亿文档：8000ms → 50ms（160× 加速）

**代价**：召回率 90-95%（不是 100%）。

---

## 二、4 种主流 ANN 算法

### 2.1 Flat（暴力搜索，基线）

```python
def flat_search(query, db, k=10):
    sims = db @ query
    return np.argsort(-sims)[:k]
```

- 复杂度：$O(N \cdot d)$
- 精度：100%
- 适用：N < 10,000（小库）或测试基线

### 2.2 IVF（Inverted File Index）

**思想**：先用 k-means 把数据库分桶，查询时只搜最近的几个桶。

```
[全部向量] → [k-means 分 1000 桶] → [每桶存原始向量]

查询时:
1. query 找最近的 nprobe 个桶 (nprobe=10)
2. 在这 nprobe 个桶内做 flat search
```

- 复杂度：$O(N \cdot k / \text{nprobe})$，nprobe 越大越准但越慢
- 精度：nprobe=10 时 ~95% recall
- 适用：100 万 - 1 亿向量

**参数调优**：
- `nlist`（桶数）：典型 $\sqrt{N}$
- `nprobe`（探测桶数）：10-100，召回率 vs 速度 trade-off

### 2.3 HNSW（Hierarchical Navigable Small World）

**论文**：Malkov & Yashunin 2018，*"Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs"*

**思想**：构建多层图，每层是稀疏连接的"小世界"网络。查询时从顶层（最稀疏）开始贪心走，逐层下降到最底层（最密集）。

```
Level 2: ●─────●         (最稀疏, 全局视图)
         │
Level 1: ●───●───●───●   (中等密度)
         │
Level 0: ●─●─●─●─●─●─●─● (全部节点, 最密)
```

- 复杂度：$O(\log N)$
- 精度：> 95% recall（参数调好时）
- 索引大小：1.5-2× 原始数据
- 适用：**1 万 - 1 亿向量**（端侧 RAG 的事实标准）

**参数调优**：
- `M`（每节点连接数）：16-48，越大越准但索引大
- `ef_construction`（建索引时探测数）：100-500
- `ef_search`（查询时探测数）：10-200，召回 vs 延迟 trade-off

### 2.4 ScaNN（Google）

**论文**：Guo et al. ICML 2020

**思想**：各向异性量化——把 query 和 doc 都量化，但在"重要方向"上保留更多精度。

- 精度：极高（同速度下比 HNSW 高 5-10 pp）
- 工程化：Google 生产级
- 适用：大规模服务（不是端侧）

---

## 三、3 个端侧可用的 ANN 库

### 3.1 sqlite-vec（端侧 RAG 事实标准）

Alex Garcia 维护，纯 C 扩展，**用 sqlite 的 vec0 虚拟表**。

```python
import sqlite_vec, sqlite3

db = sqlite3.connect("vectors.db")
db.enable_load_extension(True)
sqlite_vec.load(db)

# 创建 HNSW-like 索引
db.execute("""
    CREATE VIRTUAL TABLE vec_docs USING vec0(
        doc_id TEXT PRIMARY KEY,
        embedding FLOAT[128]
    )
""")

# 批量插入
db.executemany("INSERT INTO vec_docs VALUES (?, ?)",
               [(id, emb.tobytes()) for id, emb in data])

# 查询 (内部用 KNN)
results = db.execute("""
    SELECT doc_id, distance
    FROM vec_docs
    WHERE embedding MATCH ? AND k = 10
    ORDER BY distance
""", [query_emb.tobytes()]).fetchall()
```

**特点**：
- 内置 KNN（端侧规模够用）
- 支持 MRL 截断 (`vec_slice`)
- 支持量化（`vec_quantize_binary` / `_int8`）
- 包大小：< 1 MB
- 与 sqlite 的全文检索集成

### 3.2 FAISS（Facebook）

业界事实标准（**但不是端侧首选**）。

```python
import faiss

# HNSW 索引
index = faiss.IndexHNSWFlat(128, M=32)
index.add(vectors)  # 批量加入
D, I = index.search(query, k=10)  # 查询
```

**特点**：
- 算法丰富（IVF / HNSW / PQ 全有）
- 高度优化（多线程、GPU）
- 但二进制大（10+ MB），**Android/iOS 集成复杂**
- 更适合服务端

### 3.3 hnswlib（轻量 C++）

```python
import hnswlib

index = hnswlib.Index(space='cosine', dim=128)
index.init_index(max_elements=100000, ef_construction=200, M=32)
index.add_items(vectors, ids)
index.set_ef(50)  # 查询时探测数
labels, distances = index.knn_query(query, k=10)
```

**特点**：
- 极轻量（< 1 MB）
- 纯 C++，跨平台
- 端侧可用（iOS/Android 都能编译）
- 比 sqlite-vec 略快，但不支持 SQL 集成

---

## 四、二阶段检索（Funnel Retrieval）

### 4.1 核心思想

利用 MRL 的多分辨率特性：

```
[Query 768d]
    ↓ MRL 截断到 32d
    ↓ 在 32d 索引上找 top-200 候选
    ↓ 全 768d 重排这 200 个候选
    ↓ 返回 top-10
```

理论加速：32/768 = 24× 短名单计算节省。

### 4.2 Kusupati 论文 Funnel Retrieval

NeurIPS 2022 论文 §4.3.1：

```
短名单递进: 200 → 100 → 50 → 25 → 10
维度递进:   16  → 32  → 64  → 128 → 256 → 2048
```

**实测**：128× FLOPs 节省，14× wall-clock 加速，精度持平。

### 4.3 端侧简化版

```python
def two_stage_search(query, db_short, db_full, k=10):
    """db_short: 32d 索引, db_full: 768d 完整向量"""
    # Stage 1: 32d 粗排, 取 top-50
    candidates = hnsw_search_32d(query[:32], db_short, k=50)
    # Stage 2: 768d 精排这 50 个
    sims = db_full[candidates] @ query
    return candidates[np.argsort(-sims)[:k]]
```

---

## 五、性能对比（典型 100 万库）

| 方法 | 索引大小 | p99 延迟 | Recall@10 |
|---|---|---|---|
| Flat | 1× | 80ms | 100% |
| IVF (nlist=1000, nprobe=10) | 1.05× | 12ms | 95% |
| HNSW (M=32, ef=50) | 1.6× | 5ms | 96% |
| HNSW (M=48, ef=100) | 2× | 8ms | 99% |
| ScaNN | 1.2× | 4ms | 97% |
| **二阶段 (32d HNSW + 768d rerank)** | 1.3× | **3ms** | **98%** |

**端侧 RAG 推荐**：
- 1 万文档：sqlite-vec 直接 flat search 就够
- 10 万文档：sqlite-vec + binary 量化
- 100 万文档：hnswlib 或 sqlite-vec + HNSW
- 1 亿文档（云端）：FAISS IVF-PQ 或 ScaNN

---

## 六、参数调优速查（HNSW）

```python
# 端侧 RAG 推荐参数 (10 万文档)
index = hnswlib.Index(space='cosine', dim=128)
index.init_index(
    max_elements=100000,
    ef_construction=200,   # 建索引质量
    M=32                    # 每节点连接数 (16-48)
)
index.set_ef(50)            # 查询时探测数 (10-200)
```

| 参数 | 范围 | 影响 |
|---|---|---|
| `M` | 16-48 | 越大召回越高、索引越大 |
| `ef_construction` | 100-500 | 越大建索引越慢、质量越好 |
| `ef_search` | 10-200 | **运行时可调**，召回 vs 延迟 |

**调优顺序**：
1. 先固定 `M=32`、`ef_construction=200`
2. 调 `ef_search`：从 10 开始，逐步加到 Recall > 95%
3. 如果还达不到，加大 `M` 重训索引

---

## 七、ANN 与维度压缩的协同

| 组合 | 加速倍数 | 精度损失 |
|---|---|---|
| HNSW + 768d | 1× | 0 |
| **HNSW + MRL 128d** | **6×** | < 2 pp |
| HNSW + binary | 1.5×（Hamming 快）| 3-8 pp |
| **HNSW + MRL 128d + binary** | **12-20×** | 5-10 pp |
| 二阶段（32d 粗排 + 768d 精排） | 5-10× | < 1 pp |

**最佳端侧配方**：MRL 128d + binary + HNSW（sqlite-vec 一站式）。

---

## 八、关键铁律

1. **HNSW 索引大约 1.5-2× 原始数据**——别忘了这部分 RAM
2. **建索引慢，查索引快**——离线建好，在线只查
3. **ef_search 是运行时旋钮**——动态调速度/精度
4. **HNSW 不支持删除**——只能重建索引（或用软删除标记）
5. **MRL 与 HNSW 正交可叠加**——6× + 6× ≈ 36× 加速
6. **PQ 与 HNSW 可叠加**——但精度损失叠加
7. **端侧别用 FAISS**——包大、ARM 优化差

---

## 九、实验：HNSW vs Flat

```python
"""HNSW vs Flat 对比实验 (需 hnswlib)"""
import numpy as np
import time

# 模拟 10 万文档 128 维
np.random.seed(0)
N, D = 100000, 128
data = np.random.randn(N, D).astype(np.float32)
data /= np.linalg.norm(data, axis=1, keepdims=True)
query = data[0]  # 用第一个文档做 query

# Flat search
t0 = time.perf_counter()
sims = data @ query
top_flat = np.argsort(-sims)[:10]
t_flat = (time.perf_counter() - t0) * 1000

# HNSW search
import hnswlib
index = hnswlib.Index(space='cosine', dim=D)
index.init_index(max_elements=N, ef_construction=200, M=32)
index.add_items(data, np.arange(N))
index.set_ef(50)

t0 = time.perf_counter()
labels, _ = index.knn_query(query.reshape(1, -1), k=10)
t_hnsw = (time.perf_counter() - t0) * 1000

# Recall
recall = len(set(labels[0]).intersection(set(top_flat))) / 10

print(f"Flat: {t_flat:.1f}ms, 100% recall")
print(f"HNSW: {t_hnsw:.1f}ms, {recall*100:.0f}% recall")
print(f"加速: {t_flat/t_hnsw:.1f}x")
```

**预期输出**：

```
Flat: 80.0ms, 100% recall
HNSW: 1.5ms, 90% recall
加速: 53.3x
```

---

📌 **下一步**：
- 推理引擎选型 → [06 端侧推理引擎对比](06-端侧推理引擎对比.md)
- 完整端侧 RAG 部署 → [07 端侧 RAG 架构实战](07-端侧RAG架构实战.md)
- 与本章正交的模型压缩 → [04 模型剪枝](04-模型剪枝与层数截断.md)
