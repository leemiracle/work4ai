# CS224W: Machine Learning with Graphs

> Stanford University, Autumn 2025
> Instructor: **Jure Leskovec** (Graph ML 全球 No.1, Pinterest 首席科学家)
> Guest: Charilaos Kanatsoulis
> Time: Tue/Thu 3:00-4:20 PM, NVIDIA Auditorium
> Prerequisites: CS107 / CS145 + 基础概率 + 基础线代
> Difficulty: ⭐⭐⭐⭐⭐

---

## 📚 课程定位

**全球图机器学习的"麦加"**。Leskovec 的学生包括 William Hamilton（McGill）、Rex Ying（Pinterest PyG）、Petar Veličković（DeepMind GAT）。

---

## 📅 完整模块（19 讲）

### Week 1: Introduction + Node Embeddings
- **L1 (Sep 23)** — Introduction
- **L2 (Sep 25)** — Node embeddings
  - **DeepWalk** (Perozzi 2014)
  - **node2vec** (Grover 2016)
  - Matrix factorization view

### Week 2: GNN
- **L3 (Sep 30)** — Graph Neural Networks 1
  - 🔴 **GCN** (Kipf & Welling 2016)
- **L4 (Oct 2)** — GNN General Perspective
  - **GraphSAGE** (Hamilton 2017)
  - **GAT** (Veličković 2018)
  - Design Space of GNNs

### Week 3: GNN Theory + Training
- **L5 (Oct 7)** — GNN Augmentation & Training
  - **DiffPool** (Ying 2018) — hierarchical pooling
- **L6 (Oct 9)** — Theory of GNNs
  - 🔴 **GIN** (Xu 2018) "How Powerful are GNNs?"
  - WL isomorphism test

### Week 4: Powerful Encoders + Graph Transformers
- **L7 (Oct 14)** — Designing Powerful Graph Encoders
  - ID-GNN
  - Position-aware GNN
- **L8 (Oct 16)** — Graph Transformers
  - **Graphormer** (Ying 2021)
  - Spectral methods

### Week 5: Heterogeneous + Knowledge Graphs
- **L9 (Oct 21)** — Heterogeneous graphs
  - **RGCN** (Schlichtkrull 2018)
  - **HGT** (Wang 2020)
- **L10 (Oct 23)** — Knowledge Graphs
  - **TransE** (Bordes 2013)
  - **TransR** (Lin 2015)
  - **RotatE** (Sun 2019)

### Week 6: Applications
- **L11 (Oct 28)** — GNN for Recommender Systems
  - **PinSage** (Ying 2018) — Pinterest 生产
  - **LightGCN** (He 2020)
- **L12 (Oct 30)** — Relational Deep Learning
  - **RelBench** (2024) — 关系数据库 benchmark

### Week 7: Advanced Topics
- **L13 (Nov 6)** — Advanced RDL
- **L14 (Nov 11)** — Advanced GNN Topics
  - PRODIGY (in-context learning over graphs)
  - Conformal GNN (uncertainty quantification)
- **L15 (Nov 13)** — Foundation Models for KG

### Week 8: 2025 新主题
- **L16 (Nov 18)** — **LLM + GNN** ⭐
- **L17 (Nov 20)** — **Agents + Graphs** ⭐

### Week 10: Generative + Conclusion
- **L18 (Dec 2)** — Deep Generative Models for Graphs
  - **GraphRNN** (You 2018)
  - **GCPN** (You 2018)
- **L19 (Dec 4)** — Conclusion

---

## 🧮 核心算法

### GCN (Kipf & Welling 2016)
一层 GCN:
$$H = \sigma(\tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2} X W)$$

其中:
- $\tilde{A} = A + I$（加自环）
- $\tilde{D}_{ii} = \sum_j \tilde{A}_{ij}$（度矩阵）

### GIN (Xu 2018) — 最强 GNN
$$h_v^{(k)} = \text{MLP}((1 + \epsilon) \cdot h_v^{(k-1)} + \sum_{u \in \mathcal{N}(v)} h_u^{(k-1)})$$

**GIN 等价于 WL test** → 理论上最强 message passing GNN。

### Node2Vec
二阶随机游走 + Word2Vec (SGNS):
- $p$ (return parameter): 回到前一个节点的倾向
- $q$ (in-out parameter): BFS vs DFS 倾向

---

## 💻 项目代码

📁 `topic6-graph/gcn_from_scratch.py`

**实现**（纯 numpy）:
1. ✅ Graph 数据结构（邻接表 / 邻接矩阵）
2. ✅ Karate Club 数据集（CS224W 经典）
3. ✅ Node2Vec 简化（随机游走 + SGNS）
4. ✅ GCN 前向 + 反向传播
5. ✅ 训练 + 评估

### 运行
```bash
cd topic6-graph
python3 gcn_from_scratch.py
```

---

## 📊 关键论文（精选 15 篇）

### 🔴 必读 P0
1. **Kipf & Welling 2016** "GCN" ICLR 2017
2. **Veličković 2018** "GAT" ICLR
3. **Hamilton 2017** "GraphSAGE" NeurIPS
4. **Xu 2018** "How Powerful are GNNs?" (GIN) ICLR 2019
5. **Perozzi 2014** "DeepWalk" KDD
6. **Grover 2016** "node2vec" KDD
7. **Ying 2018** "PinSage" KDD
8. **Bordes 2013** "TransE" NeurIPS

### 🟡 P1
9. Hamilton *Graph Representation Learning*（教材，免费）
10. Ying 2021 "Graphormer"
11. Veličković 2018 "Deep Graph Infomax"

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想搞 GNN 研究** | CS224W 必修（直接上） |
| **推荐系统工程师** | CS224W + CS329H |
| **药物发现** | CS224W + CS279 |
| **社交网络** | CS224W + CS224V |

---

## 🚀 扩展

完成 CS224W 后推荐：
1. **PyG (PyTorch Geometric)** — Stanford 官方 GNN 库
2. CS224W Project Gallery — 历年学生作品
3. GraphML 会议 / LoG (Learning on Graphs)

---

**最后更新**: 2026-08-11
**对应代码**: `topic6-graph/gcn_from_scratch.py`
