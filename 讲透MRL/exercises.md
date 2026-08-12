# 讲透 MRL · 练习题

> "输出倒逼输入"——做不出题说明没真懂。建议每章学完后做对应练习。

---

## 00 章 防误解前言

### Q0.1（判断）
判断对错并说明理由：用 MRL 训练 embeddinggemma-300m 后截断到 128 维，**模型权重文件**会缩小 6 倍。

<details><summary>答案</summary>
错。MRL 不改变模型权重，只改变输出向量。权重仍是 308M 参数 ~1.2GB。截断只缩小**输出向量**（768×4=3072 字节 → 128×4=512 字节，6×↓）。
</details>

### Q0.2（多选）
下列哪些说法正确？
- a) MRL 让推理更快
- b) MRL 与 1-bit binary 量化正交可叠加
- c) MRL 让 RAM 占用变小
- d) bge-small-zh-v1.5 是 MRL 训练的

<details><summary>答案</summary>
只有 b 正确。
- a 错：MRL 不加速推理（前向不变）
- c 错：模型加载到 RAM 的部分不变
- d 错：bge-small-zh-v1.5 不是 MRL 训练
</details>

---

## 01 章 直觉与几何

### Q1.1（编程）
写一个 Python 函数 `truncate_and_renorm(v, m)`，输入单位向量 `v` 和维度 `m`，返回截断+renorm 后的向量。验证输出范数是 1。

<details><summary>答案</summary>

```python
import numpy as np
def truncate_and_renorm(v, m):
    head = v[:m]
    return head / (np.linalg.norm(head) + 1e-12)

# 验证
np.random.seed(0)
v = np.random.randn(768); v /= np.linalg.norm(v)
out = truncate_and_renorm(v, 128)
assert abs(np.linalg.norm(out) - 1.0) < 1e-6
```
</details>

### Q1.2（思考）
为什么 MRL 训练的模型，前 1/8 维的方差会比后 1/8 维大 5 倍？

<details><summary>答案</summary>
MRL loss 在多个嵌套维度上同时优化，前几维要"兼顾"所有 resolution 的 loss（768d loss + 256d loss + 128d loss + ... 都依赖前几维）。后几维只参与高维 loss。梯度反向作用让前几维权重学到"承载多分辨率信息"，几何后果就是方差前置。
</details>

### Q1.3（计算）
给定单位向量 v（768 维），截断到 256 维时范数是 0.753。问：v 的前 256 维平方和占总能量的多少？

<details><summary>答案</summary>
0.753² = 0.567。前 256 维（占维度 33%）承载了 56.7% 的能量——MRL 训练让能量前置。
</details>

---

## 02 章 MRL 数学

### Q2.1（推导）
设 base loss 是 InfoNCE：$\mathcal{L}_{\text{NCE}} = -\log \frac{\exp(\text{sim}(\mathbf{z}, \mathbf{z}^+)/\tau)}{\sum_j \exp(\text{sim}(\mathbf{z}, \mathbf{z}^-_j)/\tau)}$。

写出 $d=4$、$\mathcal{M}=\{2, 4\}$、$c_m=1/2$ 的 MRL loss 完整表达式。

<details><summary>答案</summary>
$$
\mathcal{L}_{\text{MRL}} = \frac{1}{2} \left[ \mathcal{L}_{\text{NCE}}(\mathbf{z}_{[:2]}, \mathbf{z}^+_{[:2]}, \{\mathbf{z}^-_{j,[:2]}\}) + \mathcal{L}_{\text{NCE}}(\mathbf{z}_{[:4]}, \mathbf{z}^+_{[:4]}, \{\mathbf{z}^-_{j,[:4]}\}) \right]
$$

注意 $\mathbf{z}_{[:2]}$ 在算 sim 前要 renorm。
</details>

### Q2.2（实现）
用 NumPy 实现 §2.2 的 MRL loss。

<details><summary>答案</summary>
参考 [03 章 §1.1](03-从零实现.md) 完整代码。
</details>

### Q2.3（思考）
为什么 `matryoshka_dims` 必须包含全维 $d$？

<details><summary>答案</summary>
如果不含全维 loss，模型可能"为了低维表现而牺牲高维精度"。全维 loss 是 anchor，保证 MRL 模型在全维下不输给标准训练。
</details>

---

## 03 章 从零实现

### Q3.1（编程）
实现 `MatryoshkaAdaptor`，并在 STS-B 数据上训 5 个 epoch，画出截断前后的 Recall@5 曲线。

<details><summary>答案</summary>
参考 [03 章 §3.2](03-从零实现.md)。期望：截断到 128d 时 Recall 比 adaptor 前高 5-15 pp。
</details>

### Q3.2（设计）
如果你的语料是法律文档，adaptor 应该用什么数据训？通用 STS 还是法律 STS？

<details><summary>答案</summary>
法律 STS（或你的法律语料的无监督版本）。Adaptor 是 data-specific 的——论文 §6.1 表明，"customizing the embedding to the specific corpus" 是性能提升的核心来源。
</details>

### Q3.3（思考）
Permutation 方法（[03 章 §4](03-从零实现.md)）相比 MLP Adaptor 的最大优势是什么？

<details><summary>答案</summary>
**完全保留原 cosine 相似度**——重排不改变向量内积。这意味着现有索引可以原地更新（只重排存向量），不需要重建。MLP Adaptor 改变了向量本身，必须重索引。
</details>

---

## 04 章 反直觉实验

### Q4.1（实验）
跑 `experiments/01_mrl_core.py`，回答：
- 截断到 32 维时，MRL 数据的 Recall@5 是多少？
- 非 MRL 数据呢？
- MRL 优势是多少个百分点？

<details><summary>答案</summary>
（不同 seed 数字略不同）参考值：MRL=1.000，非MRL=0.960，优势 +4 pp。
</details>

### Q4.2（思考）
为什么 Spearman 在轻度截断时下降，但 Recall 不降？

<details><summary>答案</summary>
Spearman 衡量**全排序**一致性——截断后整体排序会有小扰动。
Recall@K 只关心**前 K 个是否还在前 K**——top-K 是最稳定的，扰动一般不影响。
所以 Recall 比 Spearman 更鲁棒。
</details>

### Q4.3（开放）
设计一个实验，验证"截断到训练时未选过的维度（如 96d）MRL 退化为随机截断"。

<details><summary>答案</summary>
方案：训一个 MRL 模型，matryoshka_dims=[128, 256, 512, 768]。评估时扫描 64/96/128/160/192/224/256 维。
预期：128/256 表现好（在训练 dim），64/96/160/192/224 表现差（不在训练 dim）。
</details>

---

## 05 章 端侧部署

### Q5.1（实操）
从 ModelScope 下载 embeddinggemma-300m，跑截断扫描（768/512/256/128）。

<details><summary>答案</summary>
参考 [05 章 §2-3](05-端侧部署工程.md) 完整代码。
</details>

### Q5.2（SQL）
写 sqlite-vec 的 SQL：从 768 维原表生成 128 维 + binary 量化表。

<details><summary>答案</summary>

```sql
CREATE VIRTUAL TABLE vec_docs_128_binary USING vec0(
    doc_id TEXT PRIMARY KEY,
    embedding BIT[128]
);

INSERT INTO vec_docs_128_binary(doc_id, embedding)
SELECT doc_id, vec_quantize_binary(
    vec_normalize(vec_slice(embedding_full, 0, 128))
)
FROM vec_docs_full;
```
</details>

### Q5.3（决策）
你的场景：手机端 RAG，10 万中文文档，RAM 预算 200 MB。选什么模型 + 什么 dim？

<details><summary>答案</summary>
- 模型：embeddinggemma-300m（Q4 量化 ~300 MB，商用 OK）—— 超 RAM 预算
- 备选：bge-small-zh-v1.5-MNN（29 MB）+ Matryoshka-Adaptor
- dim：128d + binary = 16 字节/向量 × 10万 = 1.6 MB 库
- 总 RAM：29 MB（模型）+ 1.6 MB（库）+ 推理 buffer ~50 MB ≈ 80 MB，预算内
</details>

---

## 06 章 前沿综述

### Q6.1（论文）
阅读 [Matryoshka-Adaptor 论文](https://arxiv.org/abs/2407.20243) §6.1。回答： adaptor 在 MRL 训练的模型上还能涨多少？

<details><summary>答案</summary>
论文报告：在 OpenAI text-embedding-3-large（已 MRL）上，截断到 256d 时 adaptor 还能提升 1-2 pp。原因是 adaptor 是数据特异性的，相当于"领域适应"。
</details>

### Q6.2（综述）
列出 2025-2026 至少 5 篇 MRL follow-up 论文，标注 venue。

<details><summary>答案</summary>
见 [06 章 §1 时间线](06-前沿综述-2022-2026论文谱系.md)。例：
- MatQuant ICML 2025
- CSR ICML 2025
- SMEC EMNLP 2025
- 2D-MRL SIGIR 2025
- LIMIT arXiv 2025.08
- To MRL arXiv 2026.05
- MIC arXiv 2026.05
- MatGPTQ arXiv 2026.02
</details>

---

## 07 章 批判收尾

### Q7.1（判断）
某团队宣称："我们要在 1 亿文档库上把嵌入截断到 32 维以节省存储。"评价这个决策。

<details><summary>答案</summary>
不推荐。LIMIT 论文证明 32 维的理论上限是 ~500 文档（自由优化）。1 亿文档至少需要 1024+ 维。建议：用 128d 或 256d，配 binary 量化。
</details>

### Q7.2（决策）
场景：100 万文档，p99 延迟 SLA = 50ms，预算紧。下面哪个方案最好？
- a) 全维 bge-m3 + HNSW
- b) MRL 截断到 128d + HNSW
- c) PQ 量化 + IVF

<details><summary>答案</summary>
b 最佳。MRL 截断 128d（点积 8× 加速）+ HNSW（log N 复杂度）通常能 p99 < 50ms。
a 太慢（1024d 全扫），c 与 MRL 不兼容且召回掉得更多。
</details>

### Q7.3（毕业设计）
设计一个端到端端侧 RAG 系统：手机本地知识库 1 万文档，要求：
- 模型 + 库总 RAM < 200 MB
- 检索 p99 < 100ms
- 中文 Recall@5 > 0.85

给出：模型选型、dim、量化方案、推理引擎、数据库。

<details><summary>答案</summary>
（参考方案）
- 模型：bge-small-zh-v1.5-MNN（29 MB，商用）+ Matryoshka-Adaptor（200 KB）
- dim：256（介于 128 和 512 之间，bge 非 MRL 但 50% 截断风险可控，加 adaptor 后稳）
- 量化：float16（每向量 256×2=512 字节）
- 库体积：1 万 × 512 = 5 MB
- 推理引擎：MNN + mnn-llm（C++ PipelineModule）
- 数据库：sqlite-vec（vec0 虚表）
- 总 RAM：29 + 5 + 50（推理 buffer）≈ 85 MB
- p99：MNN 嵌入 ~50ms + sqlite 检索 ~10ms = 60ms
</details>

---

## 综合自测（满分 100）

| 章节 | 题数 | 每题分 | 小计 |
|---|---|---|---|
| 00-01 | 5 | 5 | 25 |
| 02-03 | 6 | 8 | 48 |
| 04-05 | 3 | 5 | 15 |
| 06-07 | 2 | 6 | 12 |
| **总分** | | | **100** |

> 80+ 分：可以独立做端侧 RAG 部署了。
> 60-80 分：建议重读 [02 章](02-MRL数学.md) 和 [03 章](03-从零实现.md)。
> < 60 分：从 [00 章](00-开场-防误解前言.md) 重头来。
