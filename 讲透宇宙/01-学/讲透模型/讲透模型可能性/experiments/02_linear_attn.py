"""
实验 02 — Linear Attention：O(n²) vs O(n) 复杂度对比
=====================================================
计算标准 attention 和 linear attention 在不同序列长度下的 FLOPs/显存比值。
验证"linear attention 把 O(n²) 降到 O(n)"的量化效果。
跑法: python3 02_linear_attn.py  (纯标准库, <1秒)
"""
print("=" * 62)
print("标准 Attention(O(n²)) vs Linear Attention(O(n))")
print("=" * 62)
d = 64  # head dim
print(f"head_dim={d}")
print(f"{'序列N':>8}  {'标准FLOPs':>12}  {'Linear FLOPs':>12}  {'比值':>8}  {'标准显存':>10}")
print("-" * 62)

for N in [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]:
    # 标准: QK^T (n×n×d) + softmax×V (n×n×d)
    standard = 2 * N * N * d
    # Linear: φ(K)^T V (d×d×n) + φ(Q)×(d×d) (n×d×d)
    linear = 2 * N * d * d
    ratio = standard / linear
    # 标准显存: n×n 矩阵
    mem_mb = N * N * 4 / 1e6  # fp32
    print(f"{N:>8}  {standard/1e9:>9.2f} GF  {linear/1e9:>9.4f} GF  {ratio:>7.0f}×  {mem_mb:>8.1f} MB")

print("-" * 62)
print("结论: N=65536 时标准 attention 是 linear 的 1024 倍计算量")
print("      但 linear 的近似有质量损失——长序列优势大，短序列不必")
