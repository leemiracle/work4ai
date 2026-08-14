"""
00_why_kv_cache.py — 为什么 KV Cache 是推理的生命线

纯 CPU + numpy 模拟，验证三件事：
  1. 没有 KV Cache，自回归生成的总计算量是 O(n²)；有 KV Cache 是 O(n)
  2. 实际计时：生成第 N 个 token 时，重算 vs 复用的耗时差距
  3. KV Cache 的显存占用公式 + 真实模型（Llama/Qwen/DeepSeek）的实例计算

跑法：python3 00_why_kv_cache.py
"""
import numpy as np
import time

np.random.seed(42)

# ============================================================
# 实验 1：O(n²) vs O(n) —— KV Cache 把自回归生成从平方降到线性
# ============================================================
# 模拟 attention：给定已生成序列 X∈R^{n×d}，新 token q∈R^{1×d}
#   - 无 cache：每步重新对全部历史算 attention（重算 K=XW_K, V=XW_V）
#   - 有 cache：只用 q 算新 k=qW_K, v=qW_V，追加进 cache，再 attend
# 用 FLOPs（浮点运算次数）量化"工作量"。

d = 64          # head_dim（简化）
n_max = 200     # 生成到第 200 个 token

def flops_no_cache(step, d, n_history):
    """第 step 步、历史长度 n_history 时，重算的 FLOPs。
    每步要重算所有历史的 K, V（2 * n_history * d * d）+ attention（n_history * d）。
    """
    kv_proj = 2 * n_history * d * d   # K 和 V 投影
    attn = n_history * d * 2          # Q·K + softmax·V（简化）
    return kv_proj + attn

def flops_with_cache(step, d):
    """有 cache：每步只算 1 个新 token 的 K, V（2 * d * d）+ attention（d）。
    """
    kv_proj = 2 * d * d               # 只投影 1 个新 token
    attn = step * d * 2               # 新 Q 对 cache 里 step 个 K/V
    return kv_proj + attn

total_no_cache = 0
total_with_cache = 0
history = 0
for step in range(1, n_max + 1):
    total_no_cache   += flops_no_cache(step, d, history)     # 重算全部历史
    total_with_cache += flops_with_cache(step, d)            # 只算新 token
    history += 1

print("=" * 64)
print("实验 1：O(n²) vs O(n) —— 生成 200 个 token 的累计 FLOPs")
print("=" * 64)
print(f"  无 KV Cache（每步重算全部历史）: {total_no_cache:>14,} FLOPs")
print(f"  有 KV Cache（只算新 token）    : {total_with_cache:>14,} FLOPs")
print(f"  加速比                        : {total_no_cache / total_with_cache:>10.1f}x")
print(f"  → 无 cache 是 O(n²)，有 cache 是 O(n)；n={n_max} 时差距约 n/2 = {n_max/2:.0f}x")

# ============================================================
# 实验 2：实际计时 —— 单步重算 vs 单步复用的真实耗时
# ============================================================
print()
print("=" * 64)
print("实验 2：生成第 100 个 token 时，单步耗时对比（d=64, numpy）")
print("=" * 64)

d = 64
n_history = 100
X = np.random.randn(n_history, d).astype(np.float32)
W_K = np.random.randn(d, d).astype(np.float32)
W_V = np.random.randn(d, d).astype(np.float32)
q = np.random.randn(1, d).astype(np.float32)
K_cache = X @ W_K     # 假设已有 cache
V_cache = X @ W_V

# 无 cache：重算全部历史
t0 = time.perf_counter()
for _ in range(2000):
    K = X @ W_K                    # 重算所有历史的 K
    V = X @ W_V                    # 重算所有历史的 V
    scores = q @ K.T               # (1, n)
    attn_out = scores @ V          # (1, d)
t_no = (time.perf_counter() - t0) / 2000 * 1e6   # us

# 有 cache：只算新 token
t0 = time.perf_counter()
for _ in range(2000):
    k_new = q @ W_K                # 只算新 token 的 k
    v_new = q @ W_V                # 只算新 token 的 v
    # 实际还要 append 到 cache，这里省略；attend 时用整个 cache
    scores = q @ K_cache.T
    attn_out = scores @ V_cache
t_yes = (time.perf_counter() - t0) / 2000 * 1e6  # us

print(f"  无 cache 单步: {t_no:>8.1f} μs  （含重算 {n_history} 个历史 token 的 K/V）")
print(f"  有 cache 单步: {t_yes:>8.1f} μs  （只投影 1 个新 token）")
print(f"  单步加速比   : {t_no/t_yes:>6.1f}x")
print(f"  → 生成越往后，cache 收益越大（历史越长，重算越贵）")

# ============================================================
# 实验 3：KV Cache 显存占用 —— 真实模型实例
# ============================================================
print()
print("=" * 64)
print("实验 3：KV Cache 显存占用（真实模型，单位 GB）")
print("=" * 64)
# 公式：KV_cache = 2 (K和V) × batch × seq_len × num_layers × num_kv_heads × head_dim × bytes_per_param
# FP16 = 2 bytes

def kv_cache_gb(seq_len, num_layers, num_kv_heads, head_dim, batch=1, bytes_per=2):
    return 2 * batch * seq_len * num_layers * num_kv_heads * head_dim * bytes_per / 1e9

models = [
    # (名字, layers, kv_heads, head_dim, 最大上下文)
    ("Llama-3-8B",        32,   8,  128, 8192),
    ("Llama-3-70B",       80,   8,  128, 8192),
    ("Qwen2.5-7B",        28,   4,  128, 32768),
    ("DeepSeek-V3 (无MLA)", 61, 128,  192, 65536),  # 朴素 KV 假设
    ("GPT-OSS-120B",      80,  16,  128, 65536),
]

print(f"  {'模型':<22} {'L':>4} {'kv头':>5} {'dim':>4} {'ctx':>6} "
      f"{'batch=1':>10} {'batch=32':>11}")
print(f"  {'-'*22} {'-'*4} {'-'*5} {'-'*4} {'-'*6} {'-'*10} {'-'*11}")
for name, L, H, hd, max_ctx in models:
    gb_b1  = kv_cache_gb(max_ctx, L, H, hd, batch=1)
    gb_b32 = kv_cache_gb(max_ctx, L, H, hd, batch=32)
    print(f"  {name:<22} {L:>4} {H:>5} {hd:>4} {max_ctx:>6} "
          f"{gb_b1:>8.2f}GB {gb_b32:>9.2f}GB")

print()
print("  反直觉（这就是 KV Cache 成为核心战场的原因）：")
print("    1. 单请求时 KV Cache 看着不大（Llama-70B 才 2.68GB）")
print("    2. 可 batch=32 并发时，Llama-70B 的 KV Cache 就要 ~86GB —— 接近权重本身")
print("    3. DeepSeek-V3 若用朴素 KV，batch=32 + 65k 上下文要 12.5TB —— 根本装不下！")
print("       这正是 MLA（Multi-head Latent Attention）把 KV 压缩 ~10-90x 的根本动机")
print("    4. vLLM 的 PagedAttention / SGLang 的 RadixAttention 都是在优化这坨显存")
