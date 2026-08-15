# 04 · MLA 深挖：DeepSeek 怎么把 KV 压进 1/10

> [00](./00-为什么KV Cache是推理的生命线.md) §3.3 算过：DeepSeek-V3 若用朴素 GQA，单请求 KV Cache 要 **393GB**，batch=32 要 12.5TB——**地球上没单机能装**。DeepSeek 的 MLA（Multi-head Latent Attention）不"少存 KV"，而是**把 KV 联合压缩成低秩 latent 向量**，只缓存 latent——压缩比 ~10-90x（取决于配置），质量几乎不掉。这是 2024-2026 KV 压缩的**架构级突破**。
>
> 配套：[DeepSeek-V2 MLA 论文](https://arxiv.org/abs/2405.04434) + [00 §3.3](./00-为什么KV Cache是推理的生命线.md)（朴素 KV 装不下的反直觉）

---

**2024 年 5 月，杭州。** DeepSeek 团队对着表格叹气：V2 是 MoE，236B 总参 / 21B 激活，上下文 128K。朴素 KV Cache 在 128K 上下文 + 128 KV heads（MoE 需要更多 head）下，**单请求要 300+GB**。GQA 已经试过——质量崩盘。他们想到一个反直觉的点：**为什么要分别存 K 和 V？把它们一起投影到低秩空间，只存 latent，attention 时再解压**。一周后 MLA 跑通：KV Cache 压缩 ~13x，质量持平 MHA。**这是 2024 年 KV 管理的范式转移**。

---

## 一、复习：GQA / MQA 的极限

- **MQA**：所有 Q 头共享 1 组 KV，压缩 N×（N = Q 头数）——**质量掉很多**
- **GQA**：分 8 组共享（Llama-3 配置），压缩 4×——Llama 极限
- 但 MoE 大模型（DeepSeek）**KV 头数 128**，GQA 压不动——压缩到 32 头就已经掉点

MLA 换思路：**不再"共享头"，而是"压缩表示"**。

## 二、MLA 的数学骨架

### 2.1 联合 KV 压缩

每个 token 不直接存 $K, V$，而是先算一个 **latent 向量** $c$：

$$
c = W^{DKV} \cdot h \quad (\text{维度 } d_c, \text{如 } 512)
$$

$c$ 是 KV 的**联合低秩表示**。Attention 时按需上采：

$$
K = W^{UK} \cdot c, \quad V = W^{UV} \cdot c
$$

**KV Cache 只存 $c$**——每个 token 一层只占 $d_c$ 而不是 $2 \cdot n_{kv} \cdot d_h$。DeepSeek-V2 配置下压缩 ~13×。

### 2.2 位置编码的麻烦：RoPE 解耦

问题：RoPE（旋转位置编码）作用在 K 上，与低秩压缩冲突（旋转矩阵破坏低秩结构）。MLA 的解法：**K 拆两段**——

- 压缩部分 $c^{UK}$（不带 RoPE，被压缩）
- 位置部分 $k^R$（带 RoPE，单独存，小维度如 64）

> 这是 MLA 最反直觉的工程细节：**不是"全压"，是"压一部分+留一小撮"**。

## 三、反模式与陷阱

### 3.1 L4 陷阱 1：把 MLA 当通用银弹

MLA 的核心收益在 **MoE + 长上下文** 这类**朴素 KV 爆炸**的场景。对 Llama-3-8B 这种小 dense 模型 + 短上下文，MLA 收益不明显，但训练复杂度上升——**不值得**。

### 3.2 L4 陷阱 2：以为 MLA 完美兼容 vLLM

**早期 vLLM 不支持 MLA**——因为 MLA 的 attention kernel 要重新写（latent 解压 + RoPE 解耦）。直到 2024 下半年 vLLM 才原生支持。**新架构落地有工程滞后**。

### 3.3 L4 陷阱 3：忽视上采矩阵的成本

MLA 把"存储成本"换成了"计算成本"——attention 时多一次 $W^{UK}, W^{UV}$ 的矩阵乘。**短序列场景**（每请求 < 256 token）反而更慢。

## 四、和 PagedAttention / 量化的关系

| 方案 | 切入点 | 可叠加？ |
|------|-------|---------|
| PagedAttention | **存储布局**（治碎片）| ✅ 与 MLA 正交 |
| KV 量化（[05](./05-KVCache量化.md)）| **精度**（治容量）| ✅ 可对 latent 量化 |
| MLA | **架构**（治表示效率）| ✅ 基础 |

DeepSeek-V3 的部署栈：**MLA + PagedAttention + latent FP8 量化**——三件全开。

## 五、费曼回炉（L2 自检）

- **F2 卡壳点**：我曾以为 MLA 是"更激进的 GQA"。重读论文 §3.1 后发现：**GQA 是"共享头"，MLA 是"投影到低秩空间"**——两件事完全不同，MLA 是**表示学习**思路。
- **F3 术语翻译**：
  - "latent compression" → 把"千字档案"摘要成"百字摘要"存仓库，要用时再展开
  - "RoPE decoupling" → 给摘要加了位置标签，但部分位置信息不进摘要，单独留一张小卡片
- **F4 回炉**：v1 我写"MLA 压缩 90×"——这是 V3 极端配置；v2 改成"**13-90×，取决于配置**"，并强调和 GQA 是**两条不同路线**，不是程度差异。

---

> 🎯 **一句话**：MLA = KV 的低秩联合压缩——**把"存档案"变成"存摘要"**，是 MoE + 长上下文时代的架构必需品，但只在朴素 KV 爆炸时才值得。

📌 **下一步**：[05 KV 量化](./05-KVCache量化.md)（精度压缩），或 03 RadixAttention（待写）（共享前缀复用）。
