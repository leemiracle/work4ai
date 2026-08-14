# 01 · KV Cache 的数学与内存账

> 本章把 00 篇的直觉变成**可算的公式**。回答三件事：① KV Cache 占多少显存（精确公式 + 00 篇思考题答案）；② prefill vs decode 为什么算力特性截然不同；③ 为什么 decode 是 memory-bound、以及这对推理优化意味着什么。
>
> 配套实验：`experiments/01_kv_cache_accounting.py`（纯计算，已实跑验证）
> 前置：[`00-为什么KV Cache是推理的生命线`](./00-为什么KV Cache是推理的生命线.md)

---

## 一、KV Cache 显存：精确公式

### 1.1 公式推导

一个 token 在一层 attention 里要存 $K$ 和 $V$ 两个向量。每个向量维度 = `num_kv_heads × head_dim`。

**单 token、单层**的 KV Cache 大小：

$$
\text{KV}_{\text{token, layer}} = 2 \times \text{num\_kv\_heads} \times \text{head\_dim} \times \text{bytes\_per\_param}
$$

（`2` 是因为 K 和 V 各一份。）

**整个请求**（batch=$b$、序列长度=$s$、层数=$L$）：

$$
\boxed{\text{KV Cache} = 2 \cdot b \cdot s \cdot L \cdot H_{\text{kv}} \cdot d_h \cdot \text{bpp}}
$$

其中：
- $H_{\text{kv}}$ = **KV 头数**（GQA/MQA 里 $\ne$ Q 头数，是省显存的关键）
- $d_h$ = 每个头的维度（head_dim）
- $\text{bpp}$ = bytes per parameter（FP16=2, FP8=1, INT4=0.5）

### 1.2 验证公式（拿 Llama-3-8B 算）

Llama-3-8B：$L=32$, $H_{\text{kv}}=8$, $d_h=128$, 最大上下文 $s=8192$，FP16（bpp=2），batch=1：

$$
\text{KV} = 2 \times 1 \times 8192 \times 32 \times 8 \times 128 \times 2 = 1{,}073{,}741{,}824 \text{ bytes} = 1.07 \text{ GB}
$$

✅ 和 00 篇实验 3 的实测值完全一致。

> 🔧 **面试速算技巧**：记住 `单 token 单层 KV（FP16）= 2 × H_kv × d_h × 2 bytes`。
> Llama-3-8B：$2 \times 8 \times 128 \times 2 = 4096$ bytes/token/层。
> 单请求 8k 上下文 × 32 层 = $4096 \times 8192 \times 32 \approx 1.07$ GB。

---

## 二、00 篇思考题答案

### 思考题 1：GQA → MHA，KV Cache 变大几倍？

```bash
cd experiments && python3 01_kv_cache_accounting.py   # 看思考题 1
```

```
GQA: KV 头 = 8    →  KV Cache 基准
MHA: KV 头 = 32   →  KV Cache = 基准 × 4
→ 变大 4 倍（Llama-3-8B 的 1.07GB → 4.28GB）
```

**答案**：4 倍。因为 KV Cache 大小正比于 $H_{\text{kv}}$，MHA 的 $H_{\text{kv}}$ = Q 头数 = 32，GQA = 8，比值 4。

> 📜 **历史脉络**：Llama-2-70B 是第一个大规模用 GQA 的生产模型（2023）。之前的 Llama-2-7B/13B 还是 MHA，KV Cache 大 4 倍——这就是为什么 7B 反而比 70B 更难做长上下文服务。GQA 之后全行业跟进（Llama-3 / Qwen2.5 / Mistral / Gemma 全是）。

### 思考题 2：FP16 → INT4，KV Cache 降多少？

```
FP16 (2 bytes) : 1.07 GB  (基准)
FP8  (1 byte)  : 0.54 GB  (×0.5)
INT4 (0.5 byte): 0.27 GB  (×0.25)
→ INT4 量化把 KV Cache 压缩到 1/4
```

**答案**：降到 0.27 GB（1/4）。KV Cache 大小正比于 bpp，INT4 是 FP16 的 1/4。

> ⚠️ **但质量代价不小**：KV Cache 量化和权重量化不同——KV 的 outlier（极端值）对 attention 影响极大，naive 的 INT4 量化会显著掉精度。vLLM / SGLang 的 KV 量化都用了专门设计（如分通道缩放、保留 outlier）。本系列 `05-KV量化` 会深挖。

### 思考题 3：为什么 DeepSeek-V3 必须用 MLA，不能用 GQA？

```
DeepSeek-V3: 61 层, 上下文 65536, head_dim=192
方案 A（朴素 MHA, 128 KV 头）:   392.99 GB / 单请求
方案 B（激进 GQA, 16 KV 头） :    49.12 GB / 单请求
方案 C（MLA, latent=512）    :     4.61 GB / 单请求

压缩比:
  MLA vs 朴素 MHA :  85.3x
  MLA vs GQA-16   :  10.7x
```

**答案核心**：即使最激进的 GQA（KV 头降到 16），DeepSeek-V3 单请求仍要 49 GB，batch=32 就 1572 GB——**装不下**。只有 MLA 把单请求压到 4.61 GB，batch=32 才 147 GB，才能真正部署。

**MLA 的核心思想**（本系列 `04-MLA深挖` 详讲）：

$$
\text{朴素：每 token 每层存 } H_{\text{kv}} \times d_h \text{ 维的 K 和 V}
$$
$$
\text{MLA：每 token 每层只存 } d_c \text{ 维的联合 latent 向量，用时再解压}
$$

DeepSeek-V3 的 $d_c = 512$，而朴素 KV 每层每 token 是 $128 \times 192 = 24576$ 维，压缩比 $\approx 48\times$（外加 RoPE 部分实际约 10-90x）。

> 🎯 **一句话**：MLA 不是"少存几个头"（GQA 的思路），而是**降维**——把 K/V 联合压成一个低秩 latent，这是质变。它是 DeepSeek-V2/V3 能在有限显存跑 65k 上下文 MoE 的根本原因，也是 2024-2025 最重要的 attention 架构创新之一。

---

## 三、prefill vs decode：同一模型，两种算力特性

### 3.1 两个阶段

LLM 推理分两阶段，**计算特性截然不同**——这是理解所有推理优化的钥匙：

| 阶段 | 做什么 | attention 形状 | 计算特性 | 瓶颈 |
|------|--------|---------------|---------|------|
| **prefill** | 一次性处理整个 prompt，算出所有 token 的 KV Cache | $(s, s)$ 方阵 | **compute-bound** | GPU 算力 |
| **decode** | 每步生成 1 个 token，用 $Q_1$ 去匹配 cache 里 $s$ 个 $K$ | $(1, s)$ 向量 | **memory-bound** | HBM 带宽 |

### 3.2 用"算术强度"量化（roofline 视角）

**算术强度**（Arithmetic Intensity）= FLOPs / Bytes，即"每读 1 byte 数据能做多少次运算"。GPU 有个峰值算术强度（如 H100 ≈ 200+ FLOPs/byte for FP16）：

- 算术强度 > GPU 峰值 → **compute-bound**（算力打满）
- 算术强度 < GPU 峰值 → **memory-bound**（在等数据）

```bash
cd experiments && python3 01_kv_cache_accounting.py   # 看补充实验
```

实测（$d_{\text{model}}=4096$, $L=32$, prompt=2048 token）：

```
prefill（处理 2048 token prompt）:
  FLOPs       : 1,099,511,627,776
  算术强度    :     2048.0 FLOPs/byte  → compute-bound
decode（生成 1 token，历史 2048）:
  FLOPs       :    536,870,912
  算术强度    :        1.0 FLOPs/byte  → memory-bound
→ decode 算术强度比 prefill 低 2048x
```

### 3.3 为什么 decode 算术强度这么低？

**prefill**：attention 是 $s \times s$ 矩阵乘法，每个元素读一次能参与 $s$ 次计算 → 算术强度高。

**decode**：每步生成 1 个 token，attention 是 $1 \times s$ 向量乘 $s \times d$ 矩阵——**每个 KV Cache 元素只被用 1 次**，但必须从 HBM 全部读出来 → 算术强度 ≈ 1。

$$
\text{AI}_{\text{decode}} \approx \frac{2 \cdot s \cdot d}{s \cdot d \cdot \text{bpp}} \approx \frac{2}{\text{bpp}} \approx 1
$$

> 🎯 **一句话**：decode 时，GPU 大量算力闲置在等 HBM 把 KV Cache 喂过来。这是 **FlashAttention、PagedAttention、投机解码** 全部推理优化的共同出发点。

---

## 四、对推理优化的三个推论

理解了"decode 是 memory-bound"，就理解了 2024-2026 推理优化的三大方向：

### 推论 1：FlashAttention 为什么有效

FlashAttention 不是减少 FLOPs（甚至略增），是**减少 HBM 读写**——通过 tiling 把 attention 的中间矩阵留在 SRAM，避免往返 HBM。这恰好针对 decode 的 memory-bound 痛点。

- 详见 [`讲透GPU与系统级/01-FlashAttention深度`](../讲透GPU与系统级/01-FlashAttention深度.md)
- 源码：[`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 K1 FlashAttention 条目

### 推论 2：投机解码（speculative decoding）的动机

既然 decode 时算力闲置 99.9%（算术强度 1 vs GPU 峰值 200+），**用小模型猜几个 token，大模型一次性并行验证**——把闲置算力用起来。

- vLLM / SGLang 都支持（EAGLE / DFlash / n-gram）
- 本系列后续会专章讨论

### 推论 3：PD 分离（prefill-decode disaggregation）

prefill 是 compute-bound（吃算力），decode 是 memory-bound（吃显存带宽）——**两个阶段对硬件的需求截然不同**。SGLang 等新一代推理引擎把这两个阶段**物理分离到不同 GPU**：

- prefill 节点：高算力 GPU（H100）
- decode 节点：高带宽 GPU / 多卡堆 KV Cache

这是 2025-2026 大规模推理服务的前沿方向（DeepSeek / Kimi 都在用）。

---

## 五、面试常考题速查（附速算答案）

| 题 | 速算 |
|----|------|
| Llama-3-8B 单请求 8k 上下文 KV Cache（FP16）| $\approx$ 1 GB |
| batch=32 时呢？| $\approx$ 32 GB |
| 换 INT4 呢？| 除以 4 → 8 GB |
| 为什么 GQA 比 MHA 省？| KV 头数从 Q 头数降到 $H_{\text{kv}}$，正比省 |
| decode 为什么比 prefill 慢？| memory-bound，算术强度低 ~2000x |
| DeepSeek-V3 为什么用 MLA？| GQA 装不下（49GB/请求），MLA 压到 4.6GB |
| FlashAttention 为什么快？| 不减 FLOPs，减 HBM 读写（针对 decode memory-bound）|

---

## 六、本篇要点 + 下一篇

> 🎯 **三句话总结**：
> 1. KV Cache = $2 \cdot b \cdot s \cdot L \cdot H_{\text{kv}} \cdot d_h \cdot \text{bpp}$，会算这个公式就懂了一半面试题。
> 2. prefill 是 compute-bound，decode 是 memory-bound（算术强度差 ~2000x）——所有推理优化都围绕这个差异。
> 3. MLA 是 2024-2025 最重要架构创新，把 DeepSeek-V3 的 KV Cache 压缩 85x，让 65k 上下文 MoE 真正可部署。

**下一篇 [`02-PagedAttention深挖`](.)**（待写）：vLLM 怎么用 OS 虚拟内存思想管理这坨巨大的、动态变化的 KV Cache——为什么"分页"能消除碎片、为什么这是系统工程思维在 AI 的典范。配合 [`讲透公开课/02-C4 6.1810 OS`](../讲透公开课/02-数理计算机神课清单.md) 的虚存章节 + [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 vLLM 源码条目食用。

---

📌 **下一步**

1. **想看 vLLM 怎么管这坨 KV Cache**：催我写 `02-PagedAttention深挖`。
2. **想理解 SGLang 的 RadixAttention**：催我写 `03-RadixAttention深挖`。
3. **想深钻 MLA**：催我写 `04-MLA深挖`（这个最该写，网上资料最散）。
4. **想跑实验**：`cd experiments && python3 01_kv_cache_accounting.py`，所有数字可复现。
