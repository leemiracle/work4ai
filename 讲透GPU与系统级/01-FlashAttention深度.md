# 01 FlashAttention 深度：GPU 内存层次 + online softmax + tiling

> 硬核系统级第一课。FlashAttention (Dao 2022) 是近三年最重要的工程突破——让 $O(n^2)$ attention 能跑长序列。
> 配套实验: `experiments/01_flash_attention.py` (纯 CPU numpy 完整验证)
> 核心洞察: **FlashAttention 快, 不是因为算得少, 而是因为读写 HBM 少。**

---

## 一、GPU 内存层次: 为什么"读写"比"计算"贵

GPU 有两层关键存储 (H100):

| 存储 | 容量 | 带宽 | 角色 |
|------|------|------|------|
| **SRAM** (共享内存, 片上) | ~228 MB | ~19 TB/s | 极快但小, kernel 在这里算 |
| **HBM** (显存) | ~80 GB | ~3.35 TB/s | 大但慢 6×, 数据在这存 |

CPU 类比: L1/L2 cache (KB-MB) vs DRAM (GB)。

**关键趋势**: 算力 (FLOPS) 增长远快于带宽 (TB/s)。所以现代 GPU 上, 瓶颈常常是**把数据从 HBM 搬到计算单元**, 而不是计算本身。这叫 **memory-bound**。

**实验1 实测** (CPU cache 模拟):
```
顺序访问 sum:  3.7 ms   (cache 命中)
随机访问 sum:  153.7 ms (cache 失效)  → 慢 42×
```
同样的计算量, 访问模式不同, 速度差 42×。FlashAttention 的全部价值就是**优化访问模式**。

---

## 二、naive attention 为什么贵: 物化 n×n 矩阵

标准 attention:
$$\text{softmax}\!\left(\frac{QK^T}{\sqrt{d}}\right) V$$

朴素实现要**物化**中间矩阵到 HBM:
1. 算 `scores = Q @ K.T` → **n×n 矩阵写回 HBM**
2. softmax → **读 n×n, 写 n×n**
3. `@ V` → **读 n×n**

n=16K 时, 这个中间矩阵 ~**2 GB**! 反复读写 HBM → 慢 + 爆显存。

---

## 三、魔法一: online softmax (流式计算, 数学基石)

### 问题
朴素 softmax $s_i = \frac{e^{x_i - m}}{\sum e^{x_j - m}}$ 必须**先**知道 $m = \max(x)$ → 两趟遍历 → 若 $x$ 是 n×n, 必须先物化整个矩阵。

### 解法: 流式更新
逐个处理 $x_i$, 维护 running 的 $(m, l)$:
$$m_\text{new} = \max(m_\text{old},\, x_i)$$
$$l_\text{new} = l_\text{old} \cdot e^{m_\text{old} - m_\text{new}} + e^{x_i - m_\text{new}}$$

关键: $m_\text{old} - m_\text{new} \le 0$, 所以 $e^{m_\text{old}-m_\text{new}}$ 把旧的累积"缩放"到新基准。

**实验2 实测**: naive vs online softmax, 1000 维, **最大差异 2.43e-17** (严格等价!), 但 online 只需一趟。

> 这是 FlashAttention 的数学基石——**不需要预先看到完整向量**, 所以可以分块增量计算。

---

## 四、魔法二: tiling (分块, 永不物化 n×n)

把 Q/K/V 分成 block×block 的小块, 每块在 SRAM 里算:

```
对每个 query 块 Qi:
  初始化 Oi=0, li=0, mi=-inf  (未归一化, per-row)
  对每个 key 块 Kj, Vj:
    S = Qi @ Kj^T * scale      ← block×block, 留在 SRAM!
    m_block = rowmax(S)
    P = exp(S - m_block)       ← 用 block max
    # online 合并 (跨块的 mi, li, Oi)
    mi_new = max(mi, m_block)
    alpha = exp(mi - mi_new)   ← 旧贡献缩放
    beta  = exp(m_block - mi_new) ← 新块缩放
    li = li*alpha + rowsum(P)*beta
    Oi = Oi*alpha + (P*beta) @ Vj   ← 未归一化输出
    mi = mi_new
  Oi = Oi / li                 ← 最后归一化
```

**核心**: 中间只有 block×block 小矩阵 (放 SRAM), **永远不物化 n×n**。

### 实验验证 (实验3, 纯 numpy)
```
Sanity check (block=N, 不分块): diff 5.55e-16  ✓
真分块 (block=32 < N=128):      diff 5.00e-16  ✓
n=512, block=64:                diff 3.89e-16  ✓ (数学严格等价!)
```

---

## 五、为什么快: 访存次数 O(n²) → O(n)

| | naive | flash |
|---|---|---|
| 中间矩阵 | 物化 scores + weights (两个 n×n) | 永不物化 n×n |
| HBM 读写 | $O(n^2)$ | $O(n)$ (只读 Q/K/V 写 O) |

**实测对比** (公式, 实验3):

| n | naive 物化 | flash 读写 | flash 省 |
|---|-----------|-----------|---------|
| 1K | 8 MB | 1 MB | 8× |
| 4K | 128 MB | 4 MB | 32× |
| 16K | **2 GB** | 16 MB | 128× |
| 64K | **32 GB** | 64 MB | 512× |

> n=16K 时 naive 中间矩阵 2GB, n=64K 时 32GB (爆显存)! FlashAttention 只 64MB。
> **这就是 FlashAttention 快 2-4× 且省显存 5-20× 的根本原因: 不是算得少, 是读写少。**

---

## 六、教学点: 一个常见 bug (本实验踩过的坑)

我在实现时踩了一个经典 bug: **naive attention 的 softmax 必须 per-row**, 不能全局。

```python
# ❌ 错 (全局 softmax, 把整个 n×n 当一个分布)
m = np.max(scores)                          # 标量!
w = np.exp(scores - m) / np.sum(...)        # 全局归一化

# ✅ 对 (per-row, 每个 query 独立 softmax)
m = scores.max(axis=-1, keepdims=True)      # 每行一个 max
w = np.exp(scores - m)
w = w / w.sum(axis=-1, keepdims=True)       # 每行归一化
```

**为什么**: attention 里, 第 $i$ 个 query 对所有 key 做 softmax (选关注哪些 key), 每行是一个独立分布。全局 softmax 会让所有行加起来才=1, 完全错误。这个 bug 不会报错, 但结果 silently 错——正是你学的损失函数课说的"silent BC breaking change"。

---

## 七、backward: recompute 技巧

前向不存 n×n, 那 backward 怎么求导? FlashAttention 的招: **不存, 反向时重算**。
- 前向只存小的 block 输出 + softmax 归一化常数 (O(n) 而非 O(n²))
- backward 重新分块算一遍 attention, 拿到中间值算梯度
- 多了重算的 FLOPs, 但 FLOPs 便宜, HBM 读写贵 → 净赚

这是"用计算换内存"的典范 (compute vs memory 的权衡)。

---

## 八、与真实实现的连接

- **PyTorch**: `F.scaled_dot_product_attention` 自动调 FlashAttention 后端 (01 篇 mini-GPT 用的)
- **FlashAttention 2/3**: 更好的并行化 (v2) + H100 异步/Fp8 (v3, 达 740 TFLOPS)
- **FlashMLA**: DeepSeek 为 MLA 定制的 kernel (Transformer 项目 01 篇)
- **无 GPU 怎么学**: 本实验证明, 核心数学 (online softmax + tiling) 在 CPU numpy 上就能完全理解。等你有了 GPU, 再学 CUDA 实现 (GPU MODE / 12 篇资源库)。

---

## 参考文献
- Dao et al. 2022, *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness* (开山)
- Dao 2023, *FlashAttention-2*; Shah et al. 2024, *FlashAttention-3*
- Milakov & Gong 2018, *Faster BERT inference with online softmax* (online softmax 的起源)
- Tri Dao 的 GitHub: github.com/Dao-AILab/flash-attention

> **下一步**: 实验 `python3 experiments/01_flash_attention.py` 复现全部验证。然后进入下一主题: PyTorch 内部 (autograd/dispatch/SDPA 后端) 或 推理引擎 (vLLM PagedAttention)。
