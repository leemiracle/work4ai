# 00 · 为什么 KV Cache 是推理的生命线

> 本章是「讲透 KV Cache」的开篇。一句话定位：**自回归生成（GPT/Llama/Qwen 都是）每一步都要让新 token 去看历史所有 token——如果不缓存，每步都得把全部历史重算一遍，复杂度 O(n²)；缓存了是 O(n)。这一步优化，决定了 LLM 推理能不能跑得动。**
>
> 但 KV Cache 本身要占显存，且随上下文线性增长——**到了 2024-2026，KV Cache 反过来成了推理显存的第一大头**，所有推理优化（vLLM 的 PagedAttention / SGLang 的 RadixAttention / DeepSeek 的 MLA / 量化）都围绕它转。本系列就是把这件事往死里钻透。
>
> 配套实验：`experiments/00_why_kv_cache.py`（纯 CPU + numpy，已实跑验证）
> 配套资源：[`讲透公开课/03-AI Infra 源码导读`](<../讲透公开课/03-AI Infra 源码导读清单.md>)（vLLM/SGLang 源码）+ [`讲透GPU与系统级/03-推理引擎`](../讲透GPU与系统级/03-推理引擎.md)（系统级概览，本系列是其深钻版）

---

## 一、直觉层：KV Cache 到底缓存了什么

### 1.1 一个比喻

想象你在写一本小说，每写一个新字，都得**回顾前面所有已写的内容**，确认逻辑连贯：

- **没有草稿纸**：每写一个字，你就从头把整本小说重读一遍——写到第 1 万字时，每写一字要重读 1 万字。
- **有草稿纸（KV Cache）**：每写完一段，你把"这段的关键线索"记在草稿纸上；写下个字时，只看草稿纸 + 刚写的上一字，不用重读原文。

LLM 的自回归生成就是这件事。**草稿纸上记的，就是 KV Cache。**

### 1.2 回忆一下 self-attention 在算什么

一个 token $x_i$ 进 transformer，先变成三个向量：

$$
Q_i = x_i W_Q, \quad K_i = x_i W_K, \quad V_i = x_i W_V
$$

- **Q**（query）：我在找什么样的信息
- **K**（key）：我能提供什么样的信息（用来被别人匹配）
- **V**（value）：我实际携带的信息（匹配上之后输出什么）

第 $i$ 个 token 的注意力输出是：

$$
\text{out}_i = \text{softmax}\left(\frac{Q_i \cdot K_{1:i}}{\sqrt{d}}\right) V_{1:i}
$$

> 🔑 **关键观察**：要算 $\text{out}_i$，需要**所有历史 token 的 $K$ 和 $V$**（$K_{1:i}, V_{1:i}$）——但**不需要历史的 $Q$**（因为只有当前 token $i$ 在发问）。

### 1.3 KV Cache = 把历史的 K 和 V 留下来

自回归生成时：

- **生成第 $i$ 个 token**：只需要算当前 token 的 $Q_i, K_i, V_i$，然后用 $Q_i$ 去匹配历史的 $K_{1:i-1}$（在 cache 里）+ 自己的 $K_i$，加权求和历史的 $V_{1:i-1}$（在 cache 里）+ 自己的 $V_i$。
- **生成完后**：把 $K_i, V_i$ **追加**进 cache，供下一步用。

$$
\boxed{\text{KV Cache} = \text{每层 attention 缓存的所有历史 token 的 } K, V \text{ 矩阵}}
$$

> 🎯 **一句话**：Q 是"即时查询"用完即弃，K/V 是"历史档案"必须保留——KV Cache 就是 transformer 推理时的"记忆体"。

---

## 二、没有 KV Cache 会怎样：O(n²) 灾难

### 2.1 数学：为什么是 O(n²)

假设生成 $n$ 个 token，序列长度从 1 涨到 $n$：

- **无 cache**：第 $i$ 步要重新计算 $i$ 个历史 token 的 $K, V$（投影开销 $O(i \cdot d^2)$）+ attention（$O(i \cdot d)$）。累计开销：

$$
\sum_{i=1}^{n} O(i \cdot d^2) = O(n^2 d^2)
$$

- **有 cache**：每步只算 1 个新 token 的 $K, V$（$O(d^2)$）+ attention（$O(n \cdot d)$）。累计开销：

$$
\sum_{i=1}^{n} O(d^2 + n d) = O(n \cdot d^2 + n^2 d)
$$

当 $n \gg d$ 时，cache 版的 $O(n^2 d)$ 仍主导，但**常数项小得多**——而且关键在于：**投影部分从 $O(n^2 d^2)$ 降到 $O(n d^2)$**，这才是数量级的胜利。

### 2.2 实测验证

```bash
cd experiments && python3 00_why_kv_cache.py
```

实测输出（d=64，生成 200 个 token）：

```
实验 1：O(n²) vs O(n) —— 生成 200 个 token 的累计 FLOPs
  无 KV Cache（每步重算全部历史）:    165,568,000 FLOPs
  有 KV Cache（只算新 token）    :      4,211,200 FLOPs
  加速比                        :       39.3x
```

**累计 FLOPs 加速 39 倍**（理论极限约 $n/2 = 100\times$，实测 39 倍是因为 cache 版还要对全部历史做 attention，但这部分是带宽瓶颈不是算力瓶颈）。

单步计时（生成第 100 个 token 时）：

```
实验 2：生成第 100 个 token 时，单步耗时对比（d=64, numpy）
  无 cache 单步:    ~27 μs  （含重算 100 个历史 token 的 K/V）
  有 cache 单步:    ~4 μs   （只投影 1 个新 token）
  单步加速比   :    ~6x
```

> ⚠️ **关键**：这只是 $n=200$ 的小模拟。真实 LLM 生成到几千 token 时，无 cache 的方案会**慢到完全不可用**——这也是为什么所有 LLM 推理引擎（vLLM/SGLang/TGI）都把 KV Cache 当默认配置。

---

## 三、KV Cache 到底存了什么：成本账

### 3.1 显存公式

一个 token 在一层 attention 里要存 $K$ 和 $V$ 两个向量。对于多头注意力：

$$
\text{KV Cache 显存} = \underbrace{2}_{K\text{和}V} \times \text{batch} \times \text{seq\_len} \times \text{num\_layers} \times \text{num\_kv\_heads} \times \text{head\_dim} \times \text{bytes\_per\_param}
$$

- `2`：K 和 V 两份
- `num_kv_heads`：注意是 **KV 头数**，不是 Q 头数（GQA/MQA 里这俩不同！Llama-3 用 GQA，Q 头 32 个但 KV 头只有 8 个）
- `bytes_per_param`：FP16 = 2，FP8 = 1，INT4 = 0.5

### 3.2 真实模型实测

```bash
cd experiments && python3 00_why_kv_cache.py   # 看实验 3
```

实测（FP16）：

| 模型 | layers | KV 头 | head_dim | 最大 ctx | **batch=1** | **batch=32** |
|------|--------|-------|----------|---------|------------|-------------|
| Llama-3-8B | 32 | 8 | 128 | 8192 | 1.07 GB | 34 GB |
| Llama-3-70B | 80 | 8 | 128 | 8192 | 2.68 GB | 86 GB |
| Qwen2.5-7B | 28 | 4 | 128 | 32768 | 1.88 GB | 60 GB |
| **DeepSeek-V3（朴素 KV）** | 61 | 128 | 192 | 65536 | **393 GB** | **12.5 TB** |
| GPT-OSS-120B | 80 | 16 | 128 | 65536 | 43 GB | 1374 GB |

### 3.3 三个反直觉

**反直觉 1**：单请求时 KV Cache 看着不大。
Llama-3-70B 的权重是 ~140 GB（FP16），单条 8k 请求的 KV Cache 才 2.68 GB——像是个零头。

**反直觉 2**：并发 + 长上下文时，KV Cache 反超权重，成为显存大头。
同样 Llama-3-70B，batch=32 时 KV Cache 要 86 GB，**接近权重本身**。推理服务为了吞吐量，并发数往往远超 32——KV Cache 占用直接爆炸。

**反直觉 3**：DeepSeek-V3 若用朴素 KV，根本装不下。
单请求 393 GB，batch=32 要 **12.5 TB**——全球没有单机能装下。这就是 DeepSeek 发明 **MLA（Multi-head Latent Attention）** 的根本动机：把每个 token 的 KV 压缩成一个小得多的 latent 向量（压缩比 ~10-90x），让 65k 上下文的 MoE 模型能实际部署。

> 🎯 **一句话**：2020 年的瓶颈是"算力不够"，2024-2026 的瓶颈是"**KV Cache 装不下**"——所有推理优化都在打这场仗。

---

## 四、为什么 KV Cache 是 2024-2026 推理优化的核心战场

围绕 KV Cache，工业界演化出了四条主线（本系列后面几篇逐一深钻）：

### 主线 1：**显存管理** —— PagedAttention / RadixAttention

KV Cache 占用大且随请求动态变化（序列长度不同 → 内部碎片 + 外部碎片）。解决方案：

- **vLLM PagedAttention**：直接套 OS 虚拟内存思想——把 KV Cache 分成固定大小的 page，逻辑连续/物理离散，page table 映射。**这是 OS 思想在 AI 的最经典案例**。
  - 详见 [`讲透GPU与系统级/03-推理引擎`](../讲透GPU与系统级/03-推理引擎.md) 第二节 + 本系列 `02-PagedAttention深挖`
  - 源码：[`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 I1 vLLM 条目，关键文件 `vllm/core/block_manager.py`

- **SGLang RadixAttention**：用基数树（radix tree）自动识别并复用任意共享前缀的 KV Cache（多轮对话 / few-shot / 系统提示词复用）。比 vLLM 的 prefix cache 更通用。
  - 本系列 `03-RadixAttention深挖`
  - 源码：`python/sglang/srt/mem_cache/radix_cache.py`

### 主线 2：**架构压缩** —— GQA / MQA / MLA

从模型架构层面减少 KV 头数或压缩 KV：

- **MQA（Multi-Query Attention）**：所有 Q 头共享 1 组 KV，KV Cache 降 N 倍（N=Q 头数）。代价：质量略降。
- **GQA（Grouped-Query Attention）**：折中——Q 头分组，每组共享 1 组 KV。Llama-3 / Qwen2.5 都用 GQA。
- **MLA（Multi-head Latent Attention）**：DeepSeek 独创，把 KV 联合压缩成低秩 latent 向量，压缩比远超 GQA，且质量几乎不降。本系列 `04-MLA深挖`。

### 主线 3：**精度压缩** —— KV Cache 量化

把 FP16 的 KV Cache 量化到 FP8 / INT8 / INT4 / 甚至是 1-bit：

- vLLM 支持 KV Cache FP8/INT8/INT4 量化
- 极端方案：**KV Cache 1.58-bit**（ternary），2025 学术热点
- 本系列 `05-KV量化`

### 主线 4：**卸载与分层** —— CPU offload / SSD

KV Cache 太大装不下显存？把它分层：

- **热数据**（最近生成的）放 GPU
- **冷数据**（长上下文的早期 token）放 CPU 内存 / NVMe
- vLLM、DeepSpeed-Zero-Inference、FlexGen 都在这方向
- 本系列 `06-分层KV Cache`

---

## 五、本系列规划 + 怎么用

### 5.1 后续篇目（按依赖顺序）

| 篇 | 标题 | 核心问题 |
|----|------|---------|
| **00** | 为什么 KV Cache 是推理的生命线（本篇）| 为什么需要、成本账、为什么是核心战场 |
| 01 | KV Cache 的数学与内存账 | 精确公式 + FLOPs 分析 + prefill/decode 差异 |
| 02 | PagedAttention 深挖 | vLLM 怎么用 OS 虚存思想管 KV Cache |
| 03 | RadixAttention 深挖 | SGLang 怎么用基数树复用共享前缀 |
| 04 | MLA 深挖 | DeepSeek 怎么把 KV 压缩 10-90x |
| 05 | KV Cache 量化 | FP8/INT4/1.58-bit 量化的代价与收益 |
| 06 | 分层 KV Cache | GPU/CPU/SSD 三级存储 |
| 07 | 横评与选型 | 不同场景该用哪种方案 |

### 5.2 与其他系列/资源的关系

```
讲透GPU与系统级/03-推理引擎.md  ← 系统级概览（84 行），本系列是其 KV Cache 部分的深钻
        ↑ 互补
讲透KV Cache（本系列）          ← 把 KV Cache 从概念钻到工业实现
        ↓ 衔接
讲透公开课/03-AI Infra 源码导读  ← 告诉你 vLLM/SGLang 源码在哪、怎么读
        ↓ 配合
讲透公开课/02 数理计算机课      ← 02-C4 6.1810 OS（虚存）+ 02-C8 15-213 CSAPP（缓存）
                                   是理解 PagedAttention 的系统课地基
```

### 5.3 怎么用本系列

- **只想要直觉**：看本篇（00）一、二节就够了
- **想会算 KV Cache 账**（面试常考）：看 01
- **想读懂 vLLM 源码**：看 02 + 配 `讲透公开课/03` 的 vLLM 条目
- **想理解 DeepSeek-V3 为什么能跑起来**：看 04（MLA）
- **想优化自己的推理服务**：看 05 + 06 + 07

---

## 六、一句话总结 + 一道思考题

> 🎯 **一句话**：KV Cache 是自回归 LLM 推理的"记忆体"——没有它每步重算（O(n²)），有了它增量计算（O(n)）；但它本身随上下文线性膨胀，到 2024-2026 成了推理显存第一大头，所有推理优化都围绕它转。

**✍️ 思考题**（答案在 01 篇）：

1. Llama-3-8B 的 KV 头数是 8（GQA），Q 头数是 32。如果把 GQA 换成 MHA（每 Q 头独立 KV 头），KV Cache 会变大多少倍？
2. 同样 Llama-3-8B，把 KV Cache 从 FP16 量化到 INT4，单请求 8k 上下文的 KV Cache 从 1.07 GB 降到多少？
3. 为什么 DeepSeek-V3 必须用 MLA，而不能像 Llama 那样用 GQA？（提示：看它的 layer 数和 MoE 结构）

---

📌 **下一步**

1. **想看精确数学 + 面试题答案**：进 [`01-KV Cache的数学与内存账`](./01-KV Cache的数学与内存账.md)。
2. **想直接读 vLLM 源码**：跳到 `02-PagedAttention深挖`（待写）+ [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 vLLM 条目。
3. **想理解 DeepSeek MLA**：等 `04-MLA深挖`（这个最值得写，因为网上资料零散）。
4. **想跑实验**：`cd experiments && python3 00_why_kv_cache.py`，所有数字都能复现。

---

## 费曼回炉记录（L2 自检 · 已迭代）

- **F2 卡壳点**：早期把 KV Cache 当成"普通的性能优化"，以为只是省点 FLOPs。重读推理引擎源码（vLLM 的 block_manager）才意识到——KV Cache **是 2024-2026 推理显存的第一大头**，权重反而成了次要项；优化方向从"省算力"转成了"塞进显存"。另一个误区是混淆 Q/K/V 的角色：以为三者地位相同都要缓存，重读 attention 公式才看清**Q 是即时查询、用完即弃；K/V 是历史档案、必须保留**——所以只缓存 K 和 V。还有个坑：以为 KV 头数 = Q 头数，重读 GQA/MQA 才发现 Llama-3 的 Q 头 32 个、KV 头只有 8 个，**显存公式必须用 KV 头数**，搞错这一项估算能差 4 倍。
- **F3 术语翻译**：
  - "Q/K/V" → Q 是"我现在想查什么"，K 是"我身上挂着什么标签好让别人找到我"，V 是"被找到后我实际给出的内容"——像图书馆里 Q=搜索词，K=书名/标签，V=书的内容
  - "PagedAttention" → 把长长的 KV Cache 切成一页一页固定大小的小块来存，逻辑上连着、物理上可以散着放，跟操作系统的虚拟内存是一个思路
  - "GQA/MQA/MLA" → 三种"省 KV Cache 的招"：MQA 是所有 Q 头共用一份 KV（最省但略掉精度）；GQA 是分组共用（折中）；MLA 是 DeepSeek 的招——把 KV 压缩成一个低维向量存，用的时候再解压
- **F4 回炉**：v1 只讲"为什么需要 KV Cache"（O(n²)→O(n) 的算力账），定位是性能优化；v2 加入"显存账 + 2024-2026 是核心战场"的视角，把四条主线（PagedAttention / GQA-MLA / 量化 / 分层）全引出。diff 是从"性能技巧"升级为"推理系统的核心矛盾"——前者是 2020 年的旧账，后者是 2024-2026 的现实约束。

<!--
元理论引用：故事即世界迭代器-元理论.md §断言 3
L2 不达标 = KL 散度未修复 = 章节在漂移而非迭代
-->
