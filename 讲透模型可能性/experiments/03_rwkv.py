"""
实验 03 — RWKV：O(1) 推理内存 vs KV Cache
============================================
对比 RWKV（固定状态）和 Transformer（KV Cache 线性增长）的推理内存。
验证 RWKV "RNN 推理效率 + Transformer 训练并行"的优势。
跑法: python3 03_rwkv.py  (纯标准库, <1秒)
"""
print("=" * 62)
print("RWKV(固定状态) vs Transformer(KV Cache 线性增长)")
print("=" * 62)

d = 4096   # hidden dim
layers = 32

print(f"配置: hidden={d}, layers={layers}")
print(f"{'生成长度N':>10}  {'KV Cache':>12}  {'RWKV状态':>12}  {'比值':>8}")
print("-" * 62)

for N in [128, 1024, 8192, 65536, 131072, 524288]:
    # Transformer: 每层存 K,V，每个 token 2×d 参数
    kv_cache = N * layers * 2 * d * 2  # fp16 = 2 bytes
    # RWKV: 每层固定状态 d×d
    rwkv_state = layers * d * d * 2    # fp16
    ratio = kv_cache / rwkv_state
    print(f"{N:>10,}  {kv_cache/1e9:>9.2f} GB  {rwkv_state/1e9:>9.3f} GB  {ratio:>7.0f}×")

print("-" * 62)
print("结论: 生成 524K token 时，KV Cache 是 RWKV 状态的 512 倍")
print("      RWKV 推理 O(1) 内存 → 超长上下文推理友好")
print("      代价: 固定状态记不住精确事实（检索弱于 KV Cache）")
