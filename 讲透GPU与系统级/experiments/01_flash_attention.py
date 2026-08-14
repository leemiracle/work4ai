"""
讲透 FlashAttention —— GPU 内存层次 + online softmax + tiling 的数学魔法
=============================================================================
纯 CPU + numpy 完整验证 FlashAttention 的核心魔法:
  实验1: 内存层次直觉 (读写比计算贵)
  实验2: online softmax (流式计算, 数学严格等价)
  实验3: naive vs flash attention (分块 + online softmax, 带 sanity check)

核心洞察: FlashAttention 快不是因为算得少, 而是读写 HBM 少。
跑法: python3 01_flash_attention.py
"""
import numpy as np
import time

np.random.seed(0)

# ============================================================
# 实验 1: 内存层次直觉
# ============================================================
print("=" * 72)
print("实验 1: GPU 内存层次 —— 为什么 FlashAttention 在意'读写次数'")
print("=" * 72)
print("""
GPU 两层关键存储 (H100):
  SRAM (片上)  ~228 MB   ~19 TB/s   ← 极快但小
  HBM  (显存)  ~80 GB    ~3.35 TB/s ← 大但慢 6×
  CPU 类比: L1/L2 cache (KB-MB) vs DRAM (GB)

现代 GPU 算力增长远快于带宽 → 瓶颈常是【把数据从 HBM 搬到计算单元】, 即 memory-bound。
""")
N = 10_000_000
arr = np.random.rand(N).astype(np.float32)
t = time.time(); arr.sum(); t_seq = time.time() - t
idx = np.random.permutation(N)
t = time.time(); arr[idx].sum(); t_rand = time.time() - t
print(f"用 CPU cache 效应模拟 HBM 随机访问代价:")
print(f"  顺序访问: {t_seq*1000:.1f} ms  | 随机访问: {t_rand*1000:.1f} ms  → 慢 {t_rand/t_seq:.1f}×")
print(f"  ==> 同样计算量, 访问模式不同速度差 {t_rand/t_seq:.0f}×。FlashAttention 就是优化访问模式。\n")


# ============================================================
# 实验 2: online softmax —— 流式计算 softmax 的数学魔法
# ============================================================
print("=" * 72)
print("实验 2: online softmax —— 不需看到完整向量就能算 softmax!")
print("=" * 72)
print("""
朴素 softmax: s_i = exp(x_i - m)/Σexp(x_j-m), 需【先】算 m=max(x)
  → 两趟遍历; 若 x 是 n×n 矩阵, 必须【物化整个矩阵到 HBM】! 这就是 naive attention 贵的原因。

online softmax: 逐个处理 x_i, 流式维护 (m_running, l_running):
  m_new = max(m_old, x_i)
  l_new = l_old * exp(m_old - m_new) + exp(x_i - m_new)
  最后 s_i = exp(x_i - m_final)/l_final
  → 【一趟遍历】, 不需预知 max → 让"分块+增量"成为可能。
""")

def naive_softmax(x):
    m = np.max(x); e = np.exp(x - m); return e / np.sum(e)

def online_softmax(x):
    m, l = -np.inf, 0.0
    for xi in x:
        m_old = m; m = max(m, xi)
        l = l * np.exp(m_old - m) + np.exp(xi - m)
    return np.exp(x - m) / l

x = np.random.randn(1000)
print(f"naive vs online softmax (1000 维): 最大差异 {np.abs(naive_softmax(x)-online_softmax(x)).max():.2e}")
print(f"  和: naive={naive_softmax(x).sum():.10f}, online={online_softmax(x).sum():.10f}\n")


# ============================================================
# 实验 3: naive vs flash attention (干净实现 + sanity check)
# ============================================================
print("=" * 72)
print("实验 3: naive attention vs flash attention (分块 tiling)")
print("=" * 72)

def naive_attention(Q, K, V):
    scores = Q @ K.T / np.sqrt(Q.shape[-1])     # n×n 物化!
    m = scores.max(axis=-1, keepdims=True)       # per-row max (attention 必须 per-row softmax!)
    w = np.exp(scores - m)
    w = w / w.sum(axis=-1, keepdims=True)        # per-row 归一化
    return w @ V

def flash_attention(Q, K, V, Bc=64):
    """FlashAttention: 分块遍历 key, online softmax 合并。维护【未归一化】的 O 和 l。"""
    N, d = Q.shape
    scale = d ** -0.5
    O = np.zeros((N, d))
    Br = Bc
    for qs in range(0, N, Br):
        qi = Q[qs:qs+Br]                         # Br × d
        br = qi.shape[0]
        Oi = np.zeros((br, d))                   # 未归一化输出
        li = np.zeros(br)                        # 未归一化常数
        mi = np.full(br, -np.inf)                # running max
        for ks in range(0, N, Bc):
            kj = K[ks:ks+Bc]
            vj = V[ks:ks+Bc]
            S = (qi @ kj.T) * scale              # br × Bc, 留在 "SRAM"
            m_block = S.max(axis=-1)             # br
            # 当前 block 在 m_block 基准下的 exp
            P = np.exp(S - m_block[:, None])     # br × Bc
            l_block = P.sum(axis=-1)             # br
            # online 合并: 统一到新 max
            mi_new = np.maximum(mi, m_block)
            alpha = np.exp(mi - mi_new)          # 旧 → 新 (mi=-inf 首次=0)
            beta = np.exp(m_block - mi_new)      # 新 block → 新基准
            li = li * alpha + l_block * beta
            Oi = Oi * alpha[:, None] + (P * beta[:, None]) @ vj
            mi = mi_new
        O[qs:qs+br] = Oi / li[:, None]           # 最后归一化
    return O

# Sanity check 1: block_size = N (不分块) 必须严格等于 naive
print("【Sanity check】 block_size = N (不分块) 必须等于 naive:")
N, d = 128, 32
Q = np.random.randn(N, d); K = np.random.randn(N, d); V = np.random.randn(N, d)
o_naive = naive_attention(Q, K, V)
o_flash_noblock = flash_attention(Q, K, V, Bc=N)
print(f"  差异: {np.abs(o_naive - o_flash_noblock).max():.2e}  (应为 ~0)\n")

# Sanity check 2: block_size < N (真分块) 必须也等于 naive
print("【真分块】 block_size=32 < N=128, 必须仍等于 naive:")
o_flash = flash_attention(Q, K, V, Bc=32)
print(f"  naive vs flash(Bc=32) 差异: {np.abs(o_naive - o_flash).max():.2e}  (应 ~0, 证明分块数学等价)")

# 更大 n
N2, d2 = 512, 64
Q2 = np.random.randn(N2, d2); K2 = np.random.randn(N2, d2); V2 = np.random.randn(N2, d2)
o_n2 = naive_attention(Q2, K2, V2)
o_f2 = flash_attention(Q2, K2, V2, Bc=64)
print(f"  naive vs flash (n={N2}, Bc=64) 差异: {np.abs(o_n2 - o_f2).max():.2e}  (数学严格等价!)")

print(f"""
【中间矩阵物化 (HBM 读写) 随 n 的代价对比 — 公式计算】
  naive: 物化 scores + weights 两个 n×n 矩阵   → O(n²)
  flash: 读 Q,K,V 写 O, 都 n×d; 永不物化 n×n    → O(n)
  {'n':>7} | {'naive':>10} | {'flash':>10} | {'flash 省':>9}
  {'-'*46}""")
for nt in [256, 1024, 4096, 16384, 65536]:
    dt = 64
    bn = 2 * nt * nt * 4
    bf = 4 * nt * dt * 4
    kb = lambda b: f"{b/1024/1024:.0f}MB" if b >= 1048576 else f"{b/1024:.0f}KB"
    print(f"  {nt:>7} | {kb(bn):>10} | {kb(bf):>10} | {bn/bf:>7.0f}×")

print(f"""
==> 核心洞察:
   - naive 物化 n×n, 代价 O(n²)。n=16K 时中间矩阵 ~2GB!
   - flash 分块 + online softmax, 永不物化 n×n, 代价 O(n)。
   - 【数学结果完全一致】(差异 ~1e-16), 但 flash 的 HBM 读写少 2-512×。
   - 这就是 FlashAttention 快 2-4× 且省显存 5-20× 的根本原因: 不是算得少, 是【读写少】。
   - backward 也能用类似 recompute 技巧做到不物化 n×n (本实验只演示 forward)。
""")
print("=" * 72)
print("全部实验完成! FlashAttention = tiling + online softmax 的工程艺术")
print("=" * 72)
