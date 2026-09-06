# Princeton MAT 429 — Topology

> **学校**：Princeton | **学期**：Spring
> **一手来源**：[math.princeton.edu/undergraduate](https://www.math.princeton.edu/undergraduate)

## 课程信息
- **编号**：MAT 429
- **先修**：MAT 215 + 217
- **教材**：Munkres, *Topology*；或 Hatcher, *Algebraic Topology*
- **特色**：本科拓扑（点集 + 代数拓扑入门）

## 教学大纲
1. **Topological spaces & continuous maps**
2. **Connectedness, compactness, Hausdorff**
3. **Fundamental group $\pi_1$** ★
4. **Covering spaces**
5. **Simplicial complexes**
6. **Homology 入门**

## 与 ML 的关联
- **拓扑数据分析**（TDA, persistent homology）
- **流形假设**：ML 数据的几何结构
- **学完本课后**：理解 manifold learning 的拓扑基础

## 参考资源
- **教材**：Munkres, *Topology* (2nd ed)
- **进阶**：Hatcher, *Algebraic Topology*（免费 PDF）
- **MIT 对照**：[MIT 18.901](../../mit-math-courses/18_901_topology/)

## 📍 在数学全景中的位置

```
前置                         本课                         后续
───────────────────────────────────────────────────────────────
MAT 215/300 分析      →   Princeton MAT 429       →   MAT 514 概率
(度量空间)                  (一般拓扑 + 基本群)         研究生代数拓扑
```

| 阶梯 | 课程 | 角色 |
|---|---|---|
| 基础 | MAT 215 | 度量空间 |
| **进阶 ★** | **MAT 429** | **点集拓扑 + 基本群 + 覆叠空间** |
| 高阶 | Harvard Math 231br | 同调/上同调 |

## 🔬 理论联系实际
1. **紧致性 → 极值定理**: 权重衰减 → 参数空间紧致 → loss 最小值存在
2. **商拓扑 → 等变网络**: $X/G$ 上的网络设计（DeepSets / GNN / SO(3) 等变）
3. **基本群 → TDA**: 持续同调检测数据中的“洞”
4. **覆叠空间 → 多值函数**: 离散对称性 / 对称性磁绕
5. **同胚 → 流形假设**: 高维数据 = 低维拓扑空间的嵌入

## 🆕 2024-2026 最新研究
- **Topological Data Analysis**: 持续同调分析 LLM 表示空间 ⚠️
- **Equivariant NNs**: SO(3)/SE(3) 等变网络用于分子设计 ⚠️
- **流形学习**: UMAP / t-SNE 的拓扑基础 ⚠️

---

📌 **下一步**：→ [MAT 514 Probability](../mat514_probability/)
