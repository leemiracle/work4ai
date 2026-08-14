# 附录 J — PPMI 点互信息：从共现矩阵到词向量

> 对应 SLP3 附录 J。第 5 章讲了 word2vec 和 GloVe，但词向量背后的核心直觉其实更简单：**两个词共现的频率比随机期望高多少**。PPMI（Positive Pointwise Mutual Information）量化这个直觉，再配 SVD 降维，就能在不做任何神经网络的情况下得到质量惊人的词向量。
>
> 配套实验：`experiments/J_ppmi_svd.py`

---

## 1. 直觉：一起出现的词，意义相关

在维基百科语料中，*cherry* 和 *pie* 共现 442 次，*digital* 和 *computer* 共现 1670 次。但光看绝对计数不够——高频词和谁都共现多。我们需要问：**比随机期望多多少？**

$$\text{PMI}(w, c) = \log \frac{P(w, c)}{P(w) \cdot P(c)}$$

分子 = 实际共现概率；分母 = 假设独立时的期望共现概率。比值 > 1（PMI > 0）说明两个词有真正的关联。

> 🧩 **反直觉**：负 PMI 理论上表示“比期望少共现”（排斥关系），但实践中不可靠（需要天文级语料才能可信地估计低频事件的“不共现”）。所以一律截断为 0 → **PPMI**。

---

## 2. 数学层

### 2.1 从共现矩阵到 PPMI

给定共现矩阵 $F$，$f_{ij}$ = 词 $w_i$ 与上下文 $c_j$ 的共现次数。归一化为概率后：

$$p_{ij} = \frac{f_{ij}}{\sum_{i'} \sum_{j'} f_{i'j'}}, \quad p_{i\cdot} = \sum_j p_{ij}, \quad p_{\cdot j} = \sum_i p_{ij}$$

$$\text{PPMI}(w_i, c_j) = \max\left(\log_2 \frac{p_{ij}}{p_{i\cdot} \cdot p_{\cdot j}},\ 0\right)$$

### 2.2 手算示例（SLP3 原书数据）

|  | computer | data | result | pie | sugar |
|--|----------|------|--------|-----|-------|
| **cherry** | 2 | 8 | 9 | **442** | **25** |
| **strawberry** | 0 | 0 | 1 | **60** | **19** |
| **digital** | 1670 | 1683 | 85 | 5 | 4 |
| **information** | 3325 | **3982** | 378 | 5 | 13 |

$\text{PPMI}(\text{cherry}, \text{pie}) = \log_2\frac{0.0377}{0.0415 \times 0.0437} = 4.38$（强关联 ✓）

$\text{PPMI}(\text{cherry}, \text{computer}) = \max(-6.7, 0) = 0$（负 PMI 截断 ✓）

### 2.3 PMI 对低频词的偏置

极低频词偶发共现一次，PMI 就爆炸。两种修正：

1. **$P_\alpha$ 上下文平滑**（Levy et al. 2015）：$P_\alpha(c) \propto \text{count}(c)^\alpha$，$\alpha=0.75$ 最佳——压低低频上下文的概率，从而降低其 PMI。
2. **Laplace 平滑**：所有计数加 $k$（$k=0.1\text{-}3$），缩小高频和低频之间的差距。

### 2.4 SVD ≈ word2vec 的理论桥梁

对 PPMI 矩阵做 **奇异值分解**（SVD）：

$$\text{PPMI} \approx U_k \Sigma_k V_k^\top$$

取前 $k$ 个奇异值，$U_k \Sigma_k$ 就是每个词的 $k$ 维稠密向量。

**Levy & Goldberg (2014) 的惊人发现**：

$$\text{word2vec Skip-gram} \approx \text{SVD}(\text{Shifted PPMI matrix})$$

word2vec 隐式地在对 PPMI 矩阵做低秩近似！两者的差距主要在偏移常数和采样策略，而非根本不同的原理。这就是为什么 PPMI+SVD 在语义类比任务上能接近 word2vec。

---

## 3. 代码层

```bash
cd 讲透NLP && python3 experiments/J_ppmi_svd.py
```

实验从零实现 PPMI 矩阵 + SVD 降维（纯 `math` + `fractions`，零依赖），在玩具语料上演示 **king - man + woman ≈ queen** 类比有效——没有任何神经网络，纯线性代数就捕捉到了语义结构。

> 🧩 **反直觉发现**：在精心设计的 toy 数据上，PPMI+SVD 的 king→queen 类比方向 **cos > 0.9**。word2vec 的魔力不在算法，而在“分布假设 + 低秩结构”本身。

---

## 4. 批判性视角

- **PPMI 不如 contextual embedding**：PPMI 产生的是**静态**词向量（一个词一个向量），无法处理多义。BERT 的上下文 embedding 对此有根本优势。
- **窗口大小是关键超参**：小窗口（±2）捕捉句法/功能相似性，大窗口（±10）捕捉主题/语义相似性。没有“正确”答案，取决于任务。
- **SVD 的局限**：对极大词表（百万级），全矩阵 SVD 不可行，需要随机化 SVD。而 word2vec 的在线 SGD 天然可扩展——这是工程上 word2vec 取代 PPMI+SVD 的主要原因，不是因为效果更好。

---

## ✍️ 练习

1. ⭐ 用 J.2 的共现矩阵手算 PPMMI(strawberry, sugar)。验证是否与原书值 5.51 一致。
2. $\alpha=0.75$ 的上下文平滑为什么能降低低频词的 PMI？（提示：$P_\alpha(c) > P(c)$ 当 $c$ 低频时。）
3. ★ 在 `J_ppmi_svd.py` 中把窗口从 ±1 改为 ±3，观察类比效果变化。窗口大小如何影响语义 vs 句法相似性？

→ [K-基于框架的对话系统.md](K-基于框架的对话系统.md)：词向量理解了词义，对话系统则需要理解“用户想做什么”——框架填充。
