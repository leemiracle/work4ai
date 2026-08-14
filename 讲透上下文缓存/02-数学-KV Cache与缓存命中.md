---
card_id: CACH-02
title: "第 2 幕 · 数学：KV Cache 与缓存命中"
universe: 讲透上下文缓存
arc_position: 第 2 幕（数学/冲突）
status: draft
next_card: CACH-03
refs: ["Vaswani, 2017", "Kwon, vLLM, SOSP 2023", "Belady, 1966 (optimal replacement)"]
---

# 📐 第 2 幕 · 数学：KV Cache 与缓存命中

## 1. Transformer 推理复杂度

self-attention 对 $n$ 个 token：每 token 关注所有 token → $O(n^2)$。

**prefill 阶段**（处理 prompt）：$O(n^2)$，一次性。
**decode 阶段**（生成 token）：
- 无 cache：每生成一个 token 重算全部 → $O(n)$ per token × $n$ tokens = $O(n^2)$ 总
- 有 KV cache：每生成一个 token 只算新 token vs 历史 → $O(n)$ per token

**总复杂度**：无 cache $O(n^2) + O(n^2) = O(n^2)$；有 cache $O(n^2) + O(n) = O(n^2)$。

**咦，两者渐进相同？** 是的。区别在**常数项**：decode 阶段 cache 让每 token 从 $O(n)$ 降到 $O(1)$（只算新 K/V，历史从 cache 读）。decode 是主要时间，所以 KV cache 让**实际延迟降一个量级**。

## 2. KV Cache 显存

$$\text{KV memory} = 2 \cdot L \cdot n \cdot d \cdot b$$

- $2$：K 和 V 两个张量
- $L$：层数
- $n$：序列长度
- $d$：隐藏维度
- $b$：每元素字节数（fp16 = 2, int8 = 1）

**例**：Llama-2-70B, $L=80, d=8192$, $n=4096$, fp16：
$$2 \times 80 \times 4096 \times 8192 \times 2 \approx 10.7 \text{ GB}$$

**单请求 4K 就要 10 GB**。这就是为什么长 context 显存爆——**不是计算贵，是 KV cache 占地方**。

**量化压缩**：KV cache 量化到 int4 可省 4×，但精度损失。这是 2024-2026 的活跃研究方向。

## 3. 命中率与成本模型

设请求 prefix 长度 $p$，新输入长度 $u$，输出长度 $o$。
- 无 cache 成本：$C_{\text{no}} = (p+u+o) \cdot c_{\text{input}} + o \cdot c_{\text{output}}$
- cache 命中：$C_{\text{hit}} = p \cdot c_{\text{write}} + u \cdot c_{\text{input}} + o \cdot c_{\text{output}}$

其中 $c_{\text{write}} > c_{\text{input}}$（写入贵），但命中后读取省。Anthropic 定价：$c_{\text{write}} = 1.25 c_{\text{input}}$，$c_{\text{cache\_read}} = 0.1 c_{\text{input}}$。

**命中 $k$ 次后的累计**：
$$C_{\text{total}} = c_{\text{write}} \cdot p + k \cdot c_{\text{cache\_read}} \cdot p$$
$$C_{\text{no, total}} = (k+1) \cdot c_{\text{input}} \cdot p$$

**盈亏平衡**：cache 在 $k \geq 1$ 时已划算（write 1.25 + read 0.1 < 2× input）。**所以「重复 ≥2 次」就值得 cache**。

## 4. 淘汰策略

cache 满了怎么办？经典策略：

| 策略 | 机制 | 适合 |
|---|---|---|
| **LRU** Least Recently Used | 淘汰最久未访问 | 时间局部性强（默认）|
| **LFU** Least Frequently Used | 淘汰访问次数最少 | 频率局部性强 |
| **ARC** Adaptive Replacement Cache | LRU + LFU 自适应 | 混合负载 |
| **Belady (OPT)** | 淘汰未来最远才用的 | 理论最优，需预知未来 |

**Belady 1966** 证明：知道未来访问序列时的最优淘汰。无法实现，但作为 benchmark 上限。

**LLM 场景**：vLLM/SGLang 用类似 LRU + 显式管理。Anthropic 用 TTL（5 分钟）——简单粗暴但产品化。

## 5. 语义缓存的命中率

语义缓存：query $q$ → embedding $\mathbf{q}$ → 在 cache 找 cosine > $\tau$ 的命中。

设真正相关 query 的 embedding 距离分布为 $N(\mu_{\text{rel}}, \sigma)$，无关 query 为 $N(\mu_{\text{irr}}, \sigma)$。

$$P(\text{hit} \mid \text{rel}) = \Phi\left(\frac{\tau - \mu_{\text{rel}}}{\sigma}\right)$$

**阈值 $\tau$ 的权衡**：
- $\tau$ 高：精度高（少返回错答案），召回低（少命中）
- $\tau$ 低：召回高，但可能返回语义相近但答案不同的（灾难）

**生产经验**：$\tau \approx 0.95$ 是常见起点，但必须做 A/B 验证——不同 embedding 模型分布不同。

## 6. PagedAttention 的核心

vLLM 把 KV 空间分成 block（如 16 token/block），用 block table 映射逻辑序列：

```
逻辑序列 A: [block 7][block 3][block 12]
逻辑序列 B: [block 7][block 3][block 9]   ← 共享 prefix!
```

**好处**：
1. 消除显存碎片（按需分配 block，不预留连续空间）
2. 公共 prefix 物理共享（block 7, 3 被 A/B 共享，copy-on-write）

实测吞吐 2-4× 提升。**这是 OS 虚拟内存思想在 LLM 推理的复活**。

---

## 🎬 本幕收束

> 缓存数学 = $O(n^2) \to O(n)$ 摊销 + $2Lndb$ 显存公式 + 命中成本模型 + LRU/LFU 淘汰 + 语义命中率 + PagedAttention 分页。核心：**确定性 prefix（prompt caching）安全，语义相似（语义缓存）危险**。

📌 **下一张卡** → `03-代码-最小KV-cache与语义缓存.md`
