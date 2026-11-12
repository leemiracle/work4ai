"""
实验 07 — Transformer 的信息流: attention 作为信息路由 / 信息瓶颈
对应文档: 讲透信息论/07-Transformer的信息流.md

核心结论:
  1. softmax 是信息瓶颈: 把任意实数向量 → 概率分布, 熵 H ∈ [0, log N]
  2. attention 权重的熵反映 "集中度": H 低 = 聚焦少数 token; H 高 = 平均看全部
  3. multi-head = 多路信息路由: 不同 head 关注不同 token 对
  4. attention 信息流 = "按相关度加权聚合" + "残差保留原信息"

跑法: python3 -u 07_attention_info.py
"""
import math, random
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)

def entropy(p_list):
    """概率分布的熵"""
    H = 0
    for p in p_list:
        if p > 0: H -= p * math.log2(p)
    return H

# ============================================================
# Part 1: softmax 是信息瓶颈
# ============================================================
P("="*70)
P("实验 07 — Transformer 的信息流: attention 作为信息路由")
P("="*70)
P()
P("Part 1: softmax 是信息瓶颈 — 实数 → 概率分布")
P("-"*70)
print(f"\n{'logits':<40}{'H(softmax(logits))':>22}{'性质':<24}")
print("-"*86)

cases = [
    ([10, 0, 0, 0],     "极峰 (one-hot)"),
    ([1, 1, 1, 1],      "均匀"),
    ([1, 0, 0, 0],      "弱峰"),
    ([3, 2, 1, 0],      "渐变"),
    ([2, -1, 0, 1],     "混合"),
    ([100, -100, 0, 0], "极端 (饱和)"),
]
for logits, name in cases:
    arr = np.array(logits)
    probs = softmax(arr)
    H = entropy(probs)
    print(f"{str(logits):<40}{H:>22.4f}    {name}")

P("""
关键观察:
- one-hot 极峰 (logits=[10,0,0,0]): H ≈ 0 (信息全聚焦一个位置)
- 均匀 (logits=[1,1,1,1]): H = log2(4) = 2 (信息平均分散)
- softmax 把 [实数向量] 压成 [概率分布], 是个信息瓶颈:
  - 输入是任意实数 (无限信息)
  - 输出是 N-1 维概率单纯形 (有限信息)
  - 信息被压缩到 [N-1 个自由度] (概率分布约束)
""")

# ============================================================
# Part 2: attention 权重的熵 — 集中 vs 分散
# ============================================================
P("="*70)
P("Part 2: attention 权重的熵反映 '集中度'")
P("-"*70)

def attention(Q, K, V):
    """标准 attention: softmax(QK^T / sqrt(d)) V"""
    d = Q.shape[-1]
    scores = Q @ K.T / math.sqrt(d)
    weights = softmax(scores, axis=-1)
    return weights @ V, weights

# 模拟一个 8 token 的序列
N, d = 8, 16
np.random.seed(42)
Q = np.random.randn(N, d)
K = np.random.randn(N, d)
V = np.random.randn(N, d)

_, attn_weights = attention(Q, K, V)

print(f"\n8 个 token 的 attention weight 矩阵 (前 4 行, 保留 2 位):")
print(f"{'query↓ key→':<10}", end="")
for j in range(N): print(f"  k{j}", end="")
print(f"{'entropy':>10}")
print("-"*70)
for i in range(min(4, N)):
    H = entropy(attn_weights[i])
    print(f"q{i:<8}", end="")
    for j in range(N):
        print(f"{attn_weights[i][j]:>4.2f}", end="")
    print(f"{H:>10.3f}")

P("""
观察:
- 不同 query 的 attention 熵不同 (有的 ~2.0 平均, 有的 ~1.5 集中)
- 没有 query 完全 one-hot (entropy=0) — 因为 sqrt(d) 缩放让 softmax 温和
- 这就是 [注意力分散度] 的信息论度量
""")

# ============================================================
# Part 3: scaling 因子 1/sqrt(d) 是 "softmax 温度"
# ============================================================
P("="*70)
P("Part 3: 1/sqrt(d) 是 softmax 温度 — 影响 attention 集中度")
P("-"*70)

np.random.seed(42)
N, d = 8, 16
Q = np.random.randn(N, d)
K = np.random.randn(N, d)
scores = Q @ K.T  # 未缩放

print(f"\n{'温度 T':<12}{'平均 attention 熵':>20}{'最集中的 entropy':>20}{'最分散的 entropy':>20}")
print("-"*72)
for d_scale in [1, 4, 16, 64, 256]:  # 模拟不同 d
    scaled = scores / math.sqrt(d_scale)
    weights = softmax(scaled, axis=-1)
    H_list = [entropy(weights[i]) for i in range(N)]
    avg_H = sum(H_list) / len(H_list)
    print(f"sqrt({d_scale})={math.sqrt(d_scale):<6.2f}{avg_H:>20.4f}{min(H_list):>20.4f}{max(H_list):>20.4f}")

P("""
关键观察:
- d 小 (温度低): attention 集中 (熵低, 接近 one-hot)
- d 大 (温度高): attention 分散 (熵高, 接近均匀)

为什么 Transformer 用 1/sqrt(d)?
- 不缩放 (T=1): d 大时 scores 方差大, softmax 饱和 (梯度消失)
- 缩放 1/sqrt(d): 让 scores 方差稳定在 ~1, softmax 处于"活跃区"
→ 这就是 '讲透基础模型/01-Transformer与注意力.md' 中 sqrt(d) 作用的信息论解释.
""")

# ============================================================
# Part 4: multi-head = 多路信息路由
# ============================================================
P("="*70)
P("Part 4: multi-head attention = 多路信息路由")
P("-"*70)

def multi_head_attention(Q, K, V, n_heads=4):
    d = Q.shape[-1]
    d_head = d // n_heads
    # 拆成 n_heads 个头
    all_weights = []
    all_outputs = []
    for h in range(n_heads):
        Qh = Q[:, h*d_head:(h+1)*d_head]
        Kh = K[:, h*d_head:(h+1)*d_head]
        Vh = V[:, h*d_head:(h+1)*d_head]
        out, w = attention(Qh, Kh, Vh)
        all_weights.append(w)
        all_outputs.append(out)
    return all_outputs, all_weights

np.random.seed(42)
d = 16
Q = np.random.randn(N, d); K = np.random.randn(N, d); V = np.random.randn(N, d)
outputs, weights_per_head = multi_head_attention(Q, K, V, n_heads=4)

# 看每个 head 关注的 token 是否不同 (计算 head 间的"差异")
print(f"\n4 个 head 的 attention 模式 (各 head 的 query 0 关注哪些 key):")
print(f"{'head':<8}", end="")
for j in range(N): print(f"  k{j}", end="")
print(f"{'entropy':>10}")
print("-"*50)
for h, w in enumerate(weights_per_head):
    H = entropy(w[0])
    print(f"h{h:<6}", end="")
    for j in range(N):
        print(f"{w[0][j]:>4.2f}", end="")
    print(f"{H:>10.3f}")

# 计算不同 head 的 attention 模式差异
print(f"\n4 个 head 之间的 attention 模式相似度 (query 0):")
print(f"{'':<8}", end="")
for h in range(4): print(f"  h{h}", end="")
print()
for i in range(4):
    print(f"h{i:<6}", end="")
    for j in range(4):
        # 用余弦相似度
        sim = np.dot(weights_per_head[i][0], weights_per_head[j][0]) / (
            np.linalg.norm(weights_per_head[i][0]) * np.linalg.norm(weights_per_head[j][0]))
        print(f"{sim:>4.2f}", end="")
    print()

P("""
关键观察:
- 不同 head 关注的 key 分布不同 (有的是 k0 高, 有的是 k3 高)
- head 之间的 attention 模式相似度通常 < 1 (互补)
→ multi-head = 多路并行信息路由, 每路关注不同的依赖关系
""")

# ============================================================
# Part 5: 信息论视角下的 attention
# ============================================================
P("="*70)
P("Part 5: attention 的信息论视角")
P("-"*70)
P("""
1. 【attention = 信息路由】
   attention weights 决定 [哪个 token 的信息流向哪个 token].
   这是 [按相关度加权的信息聚合], 与 CNN 的 [按位置加权] / RNN 的 [按时间衰减] 不同.

2. 【softmax = 信息瓶颈】
   softmax 把任意实数 → 概率分布, 信息被压缩到 N-1 维.
   - 输入 scores 包含 [相关性大小] 的连续信息
   - 输出 weights 是 [概率分布] (有限信息)
   - 瓶颈处丢失了一些细节, 但带来了 [可微 + 归一化]

3. 【1/sqrt(d) = softmax 温度】
   d 越大, scores 方差越大, softmax 越饱和 (信息全聚到 one-hot).
   1/sqrt(d) 把方差稳定在 1, 让 attention 处于 [活跃区].

4. 【multi-head = 多路并行路由】
   每个 head 学一种 [关系模式] (语法/语义/位置).
   信息论视角: 每个 head 是一个 [信息通道], 多个通道并行处理不同依赖.

5. 【Bits Back 编码 (进阶)】
   Townsend 2019: 用 NN + 逆向推理做无损压缩, 速度接近算术编码.
   这是 [NN = 压缩器] 的极致工程化, 已被集成到 Google JPEG XL.
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
Transformer 的信息流是 [按相关度加权的信息路由]:
- softmax 是信息瓶颈: 把 scores → 概率分布, H ∈ [0, log N]
- attention 熵反映集中度: 低熵 = 聚焦; 高熵 = 分散
- 1/sqrt(d) 是 softmax 温度: 防止饱和, 让 attention 在活跃区
- multi-head = 多路并行信息路由: 每个 head 一种关系模式
- attention 信息流 = [按相关性聚合] + [残差保留原信息]

收尾: 信息论是 AI 的 [隐形地基].
本系列从 -log p 出发, 一路讲透 熵/CE/KL/编码/互信息/压缩/attention.
每个概念都有 AI 对应: 训练 loss / KL 散度 / 对比学习 / LLM 压缩 / attention 信息流.
""")
