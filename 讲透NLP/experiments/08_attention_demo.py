#!/usr/bin/env python3
"""
讲透NLP · Ch8 Transformer — 配套实验: Self-Attention 从零实现 + 两个反直觉发现
对应文档: 08-Transformer.md

三个部分:
  Part 1: 从零实现 self-attention (纯 NumPy)
  Part 2: 反直觉发现 1 — 不除 √d, softmax 权重饱和 (一个 token 拿走 ~99% 注意力)
  Part 3: 反直觉发现 2 — multi-head 在小维度上是"分组"而非"多头"
                (数学铁证: 每个头的注意力分数矩阵 rank ≤ head_dim)

跑法: python3 -u 08_attention_demo.py  (纯 NumPy, ~1 秒)
"""
import math
import numpy as np

def P(*a, **kw):
    """强制 flush 的 print, 防止输出缓冲"""
    print(*a, **kw, flush=True)


# ============================================================
#  工具函数
# ============================================================

def softmax(x, axis=-1):
    """数值稳定的 softmax"""
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def attention_weights(Q, K, scale=True):
    """
    计算 attention 权重矩阵 (不做 V 聚合, 只看权重).
    Q: (N, d_k),  K: (N, d_k)
    返回: (N, N) 每行是一个 query 对所有 key 的注意力权重
    """
    d_k = Q.shape[-1]
    scores = Q @ K.T                       # (N, N) 两两点积 = 相似度
    if scale:
        scores = scores / math.sqrt(d_k)  # ★ 关键的 √d 缩放
    return softmax(scores, axis=-1)


def effective_rank(M):
    """
    矩阵的有效秩 = exp(归一化奇异值的香农熵).
    参考: Roy & Vetterli 2007.
    全秩 16×16 矩阵 → 有效秩接近 16; 低秩矩阵 → 有效秩接近实际秩.
    """
    s = np.linalg.svd(M, compute_uv=False)
    s = s / (s.sum() + 1e-12)              # 归一化为概率分布
    H = -np.sum(s * np.log(s + 1e-12))     # 奇异值的香农熵
    return math.exp(H)


def bar_chart(weights_row, width=36):
    """把一行 attention 权重画成 ASCII 柱状图"""
    N = len(weights_row)
    lines = []
    for j in range(N):
        bar_len = int(weights_row[j] * width)
        bar = "█" * bar_len
        lines.append(f"  key {j}: {bar:<{width}} {weights_row[j]*100:5.1f}%")
    return "\n".join(lines)


# ============================================================
#  Part 1: 从零实现 Self-Attention
# ============================================================
P("=" * 72)
P("Part 1: 从零实现 Self-Attention (纯 NumPy)")
P("=" * 72)

np.random.seed(42)
N, d_k = 6, 64        # 6 个 token, 每个用 64 维表示
d_v = 64

# 模拟 3 个投影矩阵 (真实 Transformer 是学出来的, 这里用随机初始化演示)
W_Q = np.random.randn(d_k, d_k) * 0.1
W_K = np.random.randn(d_k, d_k) * 0.1
W_V = np.random.randn(d_v, d_v) * 0.1

# 输入: 6 个 token 的 embedding (比如一句话的 6 个词)
X = np.random.randn(N, d_k)

# Step 1: 投影出 Q, K, V
Q = X @ W_Q   # (6, 64)  — "我在找什么"
K = X @ W_K   # (6, 64)  — "我有什么标签"
V = X @ W_V   # (6, 64)  — "找到我给你什么"

P(f"""
输入 X  shape: {X.shape}   ({N} 个 token, {d_k} 维)
投影后  Q:  {Q.shape}  K: {K.shape}  V: {V.shape}

Step 2: 相似度矩阵 QK^T  shape: ({N}, {N})
  每行 = 一个 query 对所有 key 的原始分数 (未归一化)
  每列 = 一个 key 被所有 query 查询

Step 3: 缩放 + softmax → 注意力权重
Step 4: 权重 @ V → 输出
""")

# Step 2-4: 完整 attention
scores = Q @ K.T                            # (6, 6)
scaled_scores = scores / math.sqrt(d_k)     # 关键缩放
weights = softmax(scaled_scores, axis=-1)   # (6, 6)
output = weights @ V                        # (6, 64)

P("完整公式:  Attention(Q,K,V) = softmax(QK^T / √d_k) V")
P(f"\n  scores       = Q @ K.T          shape {scores.shape}")
P(f"  / √{d_k}      = / {math.sqrt(d_k):.1f}          (缩放)")
P(f"  softmax      → weights          shape {weights.shape}")
P(f"  weights @ V  → output           shape {output.shape}")
P(f"\n  ✓ 全程只有 3 次矩阵乘法 + 1 次 softmax, 没有循环 → 完全并行!")


# ============================================================
#  Part 2: 反直觉发现 1 — 不除 √d, softmax 饱和
# ============================================================
P("\n" + "=" * 72)
P("Part 2: ★ 反直觉发现 1 — 不除 √d 会怎样?")
P("=" * 72)

P("""
直觉: "注意力越集中越好" → 似乎不缩放让大分数更大, 效果更鲜明?
事实: 不缩放时, 一个 token 拿走 ~99% 注意力, softmax 几乎变成 one-hot.
      在 one-hot 区域, softmax 的梯度趋于 0 → 训练初期模型根本学不动.

数学: 若 Q, K 各分量 ~ N(0,1), 则 Q·K = Σ(d_k 个标准正态乘积),
      期望=0, 方差=d_k. 当 d_k=64 时, std ≈ 8, scores 动辄 ±20,
      softmax 在这么大的输入下输出几乎全是 0 或 1.
""")

# 用真实投影后的 Q, K (和 Part 1 同一个数据)
raw = scores[0]    # query 0 对 6 个 key 的未缩放分数
scaled = scaled_scores[0]

w_raw = softmax(raw, axis=-1)
w_scaled = softmax(scaled, axis=-1)

P("┌──────────────────────────────────────────────────────────────────┐")
P("│  情景: d_k = 64, 看 query 0 对 6 个 key 的注意力分布           │")
P("├──────────────────────────────────────────────────────────────────┤")
P()
P("  【不缩放】 raw scores: " + np.array2string(raw, precision=1, separator=", "))
P()
P(bar_chart(w_raw))
P(f"\n  → 最大权重 = {np.max(w_raw)*100:.1f}%  ← 一个 token 几乎独占全部注意力!")
P()
P("├──────────────────────────────────────────────────────────────────┤")
P()
P("  【÷ √d_k = √64 = 8】 scaled scores: " +
  np.array2string(scaled, precision=1, separator=", "))
P()
P(bar_chart(w_scaled))
P(f"\n  → 最大权重 = {np.max(w_scaled)*100:.1f}%  ← 注意力分散到多个 token")
P()
P("└──────────────────────────────────────────────────────────────────┘")

# 跨不同 d_k 的系统对比
P("\n  不同 d_k 下的 '平均最大注意力权重' (越高 = 越饱和):")
P(f"  {'d_k':<8}{'不缩放':>12}{'÷ √d':>12}")
P("  " + "-" * 32)
for d_k_test in [4, 16, 64, 256, 1024]:
    np.random.seed(0)
    Q_t = np.random.randn(N, d_k_test)
    K_t = np.random.randn(N, d_k_test)
    s_raw = Q_t @ K_t.T
    w_raw_t = softmax(s_raw, axis=-1)
    w_scaled_t = softmax(s_raw / math.sqrt(d_k_test), axis=-1)
    P(f"  {d_k_test:<8}{np.mean(np.max(w_raw_t, axis=-1))*100:>11.1f}%"
      f"{np.mean(np.max(w_scaled_t, axis=-1))*100:>11.1f}%")

P("""
  ★ 结论:
  - d_k 越大, 不缩放时饱和越严重 (d_k=1024 时最大权重 >99%)
  - ÷ √d 把方差稳定在 ~1, softmax 处于"活跃区" → 梯度能正常流动
  - 这就是 Vaswani et al. 2017 论文中 √d_k 的唯一原因!
""")


# ============================================================
#  Part 3: 反直觉发现 2 — multi-head 的 head_dim 太小 = 秩瓶颈
# ============================================================
P("=" * 72)
P("Part 3: ★ 反直觉发现 2 — head_dim 太小: '多头' 退化成 '分组'")
P("=" * 72)

P("""
论文说: "multi-head 让模型从不同表示子空间联合关注信息".
直觉: 头越多 → 视角越多 → 越好?
事实: 每个头的注意力分数矩阵 S_h = Q_h · K_h^T 的秩 ≤ head_dim.
      当 head_dim=2 时, 一个 16×16 的分数矩阵秩 ≤ 2,
      意味着这 16 个 query 只能沿着 2 个"方向"产生不同的注意力模式.

数学证明 (一行):
  Q_h 是 (N, head_dim), K_h 是 (N, head_dim)
  S_h = Q_h · K_h^T  是 (N, N), 但 rank(S_h) ≤ min(N, head_dim)
  → head_dim 就是每个头能表达的"独立关系模式"数量的上限.
""")

N_tokens = 16   # 16 个 token, 让秩瓶颈有发挥空间

# ---- 实验 3a: 不同 head_dim 的有效秩 ----
P("  实验 3a: 固定 N=16 token, 测量单头分数矩阵的 [有效秩]")
P(f"  (有效秩 = exp(奇异值熵), 上限 = min(head_dim, N))")
P()
P(f"  {'head_dim':<12}{'理论上限':>12}{'实测有效秩':>16}{'诊断':<24}")
P("  " + "-" * 60)

np.random.seed(7)
for head_dim in [2, 4, 8, 16, 32, 64]:
    Q_h = np.random.randn(N_tokens, head_dim)
    K_h = np.random.randn(N_tokens, head_dim)
    S = Q_h @ K_h.T                      # (16, 16) 分数矩阵
    er = effective_rank(S)
    cap = min(head_dim, N_tokens)
    if head_dim <= 4:
        diag = "⚠ 严重瓶颈"
    elif head_dim <= 8:
        diag = "⚠ 中等瓶颈"
    else:
        diag = "✓ 充足"
    P(f"  {head_dim:<12}{cap:>12}{er:>16.2f}    {diag}")

# ---- 实验 3b: 固定 d_model, 改变 head 数 ----
P()
P("  实验 3b: 固定 d_model=64, 改变头数, 看每头有效秩 + 总有效秩")
P(f"  (总有效秩 = 所有头的有效秩之和; 当 head_dim < N 时, 总和 ≈ d_model)")
P()

d_model = 64
P(f"  {'heads':<8}{'head_dim':<12}{'每头有效秩':>14}{'总有效秩':>14}{'解读':<28}")
P("  " + "-" * 72)

for num_heads in [1, 2, 4, 8, 16, 32]:
    if d_model % num_heads != 0:
        continue
    d_head = d_model // num_heads
    np.random.seed(99)
    per_head_ranks = []
    for h in range(num_heads):
        Q_h = np.random.randn(N_tokens, d_head)
        K_h = np.random.randn(N_tokens, d_head)
        S = Q_h @ K_h.T
        per_head_ranks.append(effective_rank(S))
    avg_rank = np.mean(per_head_ranks)
    total_rank = np.sum(per_head_ranks)
    if num_heads == 1:
        interp = "单头: 全部容量在一个头"
    elif d_head <= 4:
        interp = f"⚠ {num_heads}头每头仅{d_head}维 → 每头残废"
    elif d_head <= 8:
        interp = f"⚠ 每头{d_head}维 → 中等瓶颈"
    else:
        interp = f"✓ 每头{d_head}维 → 健康"
    P(f"  {num_heads:<8}{d_head:<12}{avg_rank:>14.2f}{total_rank:>14.1f}    {interp}")

P("""
  ★ 三个结论:

  1. [每头有效秩 ≈ min(head_dim, N)]
     head_dim=2  → 有效秩 ≈ 1.9: 只能表达 ~2 种独立的 token 关系模式.
     head_dim=8  → 有效秩 ≈ 6.7: 中等表达力.
     head_dim=64 → 有效秩 ≈ 12.3: 接近 N=16 上限, 表达力充沛.

  2. [总有效秩随头数增加趋近 d_model, 但每头骤降]
     1头  → 总秩 12.3,  每头 12.3  (1 个强头)
     8头  → 总秩 53.8,  每头  6.7  (8 个中等头)
     32头 → 总秩 62.1,  每头  1.9  (32 个残废头)
     多头是"重新分配容量", 不是"增加容量"!

  3. [head_dim 太小 → 每头残废]
     d_model=64 + 32头: 每头只有 2 维 → 有效秩 1.9 → 只会做最简单的注意力.
     这不是"32 个不同视角", 是"32 个几乎相同的浅薄视角".
     (随机投影下的有效秩是理论上限; 真实训练中退化更严重)

  → 经验法则: head_dim ≥ 32 (最好 ≥ 64).
     BERT-base:   d=768,  12头, head_dim=64   ✓
     GPT-2 small: d=768,  12头, head_dim=64   ✓
     LLaMA-7B:    d=4096, 32头, head_dim=128  ✓
""")

# ============================================================
#  总结
# ============================================================
P("=" * 72)
P("一句话总结")
P("=" * 72)
P("""
  Self-Attention 的核心公式只有一行:
    Attention(Q,K,V) = softmax(QK^T / √d_k) · V

  两个反直觉发现:
    1. ÷ √d_k 不是可选的: 不除 → softmax 饱和 → one-hot → 梯度消失
    2. 多头不是越多越好: head_dim 太小 → 秩瓶颈 → 每头只能看 2 个方向

  NLP 视角: attention 一步看全部 token (全局 + 并行),
            彻底终结了 RNN "必须按顺序处理" 的时代.

  想深入 FlashAttention / RoPE / GQA / MLA?
  → ../讲透Transformer/ (16 篇深度版)
""")
