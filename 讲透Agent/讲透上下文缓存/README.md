---
card_id: CACH-00
title: "讲透上下文缓存：KV Cache、Prompt Caching 与记忆经济学"
universe: 讲透上下文缓存
burke:
  scene: "长上下文 LLM 贵且慢，重复 prefix 浪费算力"
  agent: "被长上下文成本烧钱的工程师"
  agency: "KV Cache + prompt caching + 语义缓存 + PagedAttention"
  act: "把重复计算变成预计算的复用"
  purpose: "在延迟/成本/质量三角中找最优"
tension: "缓存=用空间换时间换正确性——命中省 90%，未命中浪费，过期出错"
arc: [直觉, 数学(KV cache 复杂度), 代码(语义缓存), 不足(失败模式), 应用(经济学)]
status: in_progress
next_card: CACH-01
refs:
  - "Vaswani et al., Attention Is All You Need, 2017 (O(n²) 复杂度)"
  - "vLLM, PagedAttention, 2023 (Kwon et al., SOSP)"
  - "SGLang, RadixAttention, 2024"
  - "Anthropic Prompt Caching, 2024-2025 (90% off cache read)"
  - "Augment Context Engine, 2025 (60万 token)"
updated: 2026-08-13
---
# ⚡ 讲透上下文缓存：LLM 推理的经济学

> **User Story**：作为一个被长上下文成本烧钱的人，我想理解 LLM 时代的缓存原语，以便在延迟/成本/质量间找最优。

## 🎭 戏剧张力

Transformer 推理的核心成本：

> **self-attention 是 O(n²)**——序列翻倍，计算量 4 倍。但**生成第 t 个 token 时，前 t-1 个 token 的 K/V 没变**，完全可以缓存复用。这就是 KV Cache：把 O(n²) 摊销成「首次 O(n²) + 之后每 token O(n)」。
>
> 但缓存有代价：**显存**。一个 70B 模型，4K context 的 KV cache 就要好几 GB。于是有了 PagedAttention（vLLM）、RadixAttention（SGLang）、prompt caching（厂商 API）——全在解决「如何高效存/复用/共享 KV」。

## 📚 五幕总览

| 幕 | 文件 | 一句话 |
|---|---|---|
| 直觉 | [`01-直觉-缓存即预计算的回忆.md`](01-直觉-缓存即预计算的回忆.md) | CPU 缓存类比 + KV Cache 是 Transformer 推理核心 |
| 数学 | [`02-数学-KV Cache与缓存命中.md`](02-数学-KV%20Cache与缓存命中.md) | O(n²)→O(n) 摊销；显存公式；LRU/LFU；语义命中率 |
| 代码 | [`03-代码-最小KV-cache与语义缓存.md`](03-代码-最小KV-cache与语义缓存.md) | numpy 对比有/无 cache + 100 行语义缓存 |
| 不足 | [`04-不足-缓存失败模式.md`](04-不足-缓存失败模式.md) | stale / 语义相似≠语义相同 / 前缀失效 / 隐私泄漏 |
| 应用 | [`05-应用-缓存经济学.md`](05-应用-缓存经济学.md) | 厂商价格对比 + RAG vs long context vs cache 权衡 |

## 📊 2024-2026 缓存经济学（价格即真理）

| 方案 | 机制 | 成本节省 | 失效条件 |
|---|---|---|---|
| **Anthropic Prompt Caching** | 前缀 KV 持久化 5 分钟 | **cache read 比 input 便宜 90%**，cache write 贵 25% | 5 分钟 TTL；前缀改一字全失效 |
| **Gemini Context Caching** | 显式创建缓存对象 | 类似 90% off | 用户显式管理 TTL |
| **vLLM PagedAttention** | OS 虚拟内存思路管理 KV | 吞吐 2-4× | 自部署场景 |
| **SGLang RadixAttention** | 用基数树共享公共前缀 KV | 多请求共享前缀时极大收益 | 前缀需真正公共 |
| **DeepSeek Context Cache** | 命中自动复用 | 显著降本 | 命中率依赖工作负载 |
| **Augment Context Engine** | 大规模代码语义索引 | **60 万 token 真实可用** | coding agent 专用 |

## 💡 核心洞察

> **缓存是「无思考的负熵」**——它不像记忆那样理解语义，只认「前缀相同」。这让它在**确定性 prefix**（system prompt、few-shot、代码库）上极强，但在**语义相似但字面不同**的场景失效。所以：**prompt caching 解决「重复」，语义缓存试图解决「相似」，长期记忆（`讲透记忆/`）才解决「理解」。** 三者是认知复杂度的递进。

## 🗺️ 三角权衡（核心决策图）

```
        RAG（外部检索）
         /  低成本
        /   高延迟
       /
       ⊙──── 长上下文（全塞进去）
        \   高成本
         \  低延迟
          \
    语义缓存（相似复用）
          命中省，未命中亏
```

📜 **本宇宙编辑史**：[`HISTORY.md`](HISTORY.md)

## 🔗 与其他宇宙

- **[`讲透KV Cache/`](../讲透KV Cache/)**：底层机制见 KV Cache 宇宙（PagedAttention/RadixAttention 的数据结构层）
- 与 **`讲透记忆/`**：缓存是「无语义复用」，记忆是「有语义复用」。
- 与 **`讲透代码生成/`**：coding agent 的瓶颈往往是 context 管理（Augment 的意义）。
- 与 **`故事原语/02-熵论辩证`**：缓存是「把已算好的有序状态保留下来」=典型的负熵注入。

---
📌 **下一步**：`02`（显存公式）和 `05`（经济学）最实用。
