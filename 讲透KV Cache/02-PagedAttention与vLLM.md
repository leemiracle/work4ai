# 02 — PagedAttention 与 vLLM：推理服务的内存革命

> 「讲透 KV Cache」核心章。01 讲了 KV Cache 是什么。本篇讲 **PagedAttention**（vLLM 的核心创新）——把操作系统的**分页虚拟内存**思想搬到 LLM 推理，让显存利用率从 20% 飙到 90%+。这是 2023 LLM 推理最重要的工程突破。

---

## 1. 灵魂：KV Cache 的碎片化问题

$$
\boxed{\text{PagedAttention} = \text{OS 分页内存管理} \to \text{LLM KV Cache}}
$$

传统 KV Cache 为每个序列**连续分配**显存。但序列长度不同、动态增长 → **碎片化**严重，显存利用率只有 ~20-40%。

PagedAttention 把 KV Cache 分成固定大小的**块（block）**，按需分配——像 OS 的虚拟内存。

---

## 2. 传统 KV Cache 的问题

### 2.1 预分配浪费

每个请求预分配 max_length 的 KV Cache 空间。但大部分序列远短于 max_length → **大量预分配空间浪费**。

### 2.2 碎片化

不同序列长度 → 连续分配导致**外部碎片**（小空隙无法利用）。

### 2.3 批处理受限

显存不够 → batch size 小 → 吞吐量低。

---

## 3. PagedAttention（vLLM, Kwon 2023）

### 3.1 核心思想

KV Cache 不连续存储，而是分成**固定大小的块**（如每块 16 个 token）：

```
逻辑视图（序列看到的）: [token_0, token_1, ..., token_100]
物理存储（实际在显存）: 块3 → 块7 → 块1 → 块9 → ...（不连续）
块表（Block Table）: [3, 7, 1, 9, ...]（逻辑→物理映射）
```

### 3.2 和 OS 分页的对应

| OS 虚拟内存 | PagedAttention |
|---|---|
| 页（4KB）| 块（16 token）|
| 页表 | 块表 |
| 缺页中断 | 新块分配 |
| 进程隔离 | 序列隔离 |

### 3.3 收益

| 指标 | 传统 | PagedAttention |
|---|---|---|
| 显存利用率 | 20-40% | **90%+** |
| 最大 batch | 小 | **大（2-4×）**|
| 吞吐量 | 基准 | **2-4× 提升** |

---

## 4. Continuous Batching（连续批处理）

### 4.1 传统 batching 的问题

不同序列长度不同 → 短序列完成后要**等**最长的 → GPU 空转。

### 4.2 Continuous batching

每当一个序列完成，**立刻插入**新请求到空出的槽位 → GPU 永远满载。

这和 PagedAttention 配合——块级分配让"插入"几乎零成本。

---

## 5. vLLM 的架构

```
请求 → 调度器（continuous batching）→ PagedAttention（KV Cache 管理）
                                         ↓
                                    模型前向（支持多种架构）
                                         ↓
                                    流式输出
```

vLLM 的设计哲学：**把 KV Cache 管理从模型推理中解耦**——模型只管算，KV Cache 管理由专门的调度器处理。

---

## 6. 其他推理优化技术

| 技术 | 思路 | 效果 |
|---|---|---|
| **PagedAttention** | 分页 KV | 显存利用率 |
| **Tensor Parallelism** | 模型切分到多 GPU | 大模型推理 |
| **Speculative Decoding** | 小模型猜 + 大模型验 | 延迟降低 |
| **量化**（INT4/INT8）| 低精度推理 | 显存/速度 |
| **Prefix Caching** | 缓存共享前缀的 KV | 多请求共享 system prompt |

---

## 7. 批判性

- **PagedAttention 有开销**：块表的间接寻址有微小延迟（但远小于省下的显存收益）
- **不是所有模型支持**：vLLM 需要为每种架构适配（但主流模型已覆盖）
- **竞品涌现**：TensorRT-LLM / SGLang 也在做类似优化——推理引擎竞争激烈

> **诚实结论**：PagedAttention 是 2023 LLM 推理最重要的工程创新——它把"分页虚拟内存"这个 50 年前的 OS 思想搬到了 AI。理解它，就理解了为什么 vLLM 能成为最流行的推理引擎。

---

## 📌 下一步

[03-Continuous Batching深入](03-ContinuousBatching.md)（待补）｜ [04-推理优化全景](04-推理优化全景.md)（待补：投机解码/量化/并行）。

## ✍️ 练习

1. OS 的虚拟内存为什么用分页？vLLM 为什么也用？共同原因是什么？（提示：避免连续分配的碎片化。）
2. Continuous batching 让 GPU 永远满载。代价是什么？（提示：请求延迟不可预测——新请求可能插队。）
3. 如果两个请求共享相同的 system prompt（如"You are a helpful assistant"），能共享 KV Cache 吗？（提示：能——Prefix Caching 就是做这个。）
