"""
01_kv_cache_accounting.py — KV Cache 的数学与内存账

回答 00 篇的三道思考题 + DeepSeek MLA 压缩比实测。
纯计算，无需 GPU。

跑法：python3 01_kv_cache_accounting.py
"""

# ============================================================
# 思考题 1：GQA → MHA，KV Cache 变大几倍？
# ============================================================
print("=" * 64)
print("思考题 1：Llama-3-8B 把 GQA 换成 MHA，KV Cache 变大几倍？")
print("=" * 64)
# Llama-3-8B: Q 头 = 32, KV 头 = 8 (GQA)
q_heads = 32
kv_heads_gqa = 8
kv_heads_mha = 32   # MHA: 每 Q 头独立 KV 头
ratio = kv_heads_mha / kv_heads_gqa
print(f"  GQA: KV 头 = {kv_heads_gqa}    →  KV Cache 基准")
print(f"  MHA: KV 头 = {kv_heads_mha}   →  KV Cache = 基准 × {ratio:.0f}")
print(f"  → 变大 {ratio:.0f} 倍（Llama-3-8B 的 1.07GB → {1.07*ratio:.2f}GB）")
print(f"  → 这就是为什么 Llama-2 之后全行业转 GQA：质量几乎不降，省 4x 显存")

# ============================================================
# 思考题 2：FP16 → INT4，KV Cache 降多少？
# ============================================================
print()
print("=" * 64)
print("思考题 2：Llama-3-8B KV Cache 从 FP16 量化到 INT4")
print("=" * 64)
bytes_fp16 = 2
bytes_int4 = 0.5    # 4 bit = 0.5 byte
bytes_fp8 = 1
gb_fp16 = 1.07      # 00 篇实测
gb_int4 = gb_fp16 * bytes_int4 / bytes_fp16
gb_fp8 = gb_fp16 * bytes_fp8 / bytes_fp16
print(f"  FP16 (2 bytes): {gb_fp16:.2f} GB  (基准)")
print(f"  FP8  (1 byte) : {gb_fp8:.2f} GB  (×{bytes_fp8/bytes_fp16:.1f})")
print(f"  INT4 (0.5 byte): {gb_int4:.2f} GB  (×{bytes_int4/bytes_fp16:.2f})")
print(f"  → INT4 量化把 KV Cache 压缩到 1/4，但代价是质量损失（需精心设计量化方案）")

# ============================================================
# 思考题 3：为什么 DeepSeek-V3 必须用 MLA？
# ============================================================
print()
print("=" * 64)
print("思考题 3：DeepSeek-V3 为什么必须用 MLA，不能像 Llama 用 GQA？")
print("=" * 64)
# DeepSeek-V3 配置
layers = 61
seq_len = 65536
head_dim = 192
bytes_fp16 = 2

def kv_gb(num_kv_heads, per_head_dim, latent_dim=None):
    """朴素 KV：每个 token 每层存 num_kv_heads × per_head_dim 维的 K 和 V。
    MLA：每个 token 每层只存 latent_dim 维的压缩 latent（解压时才还原 K/V）。
    """
    if latent_dim is None:
        # 朴素：K 和 V 各一份
        return 2 * seq_len * layers * num_kv_heads * per_head_dim * bytes_fp16 / 1e9
    else:
        # MLA：只存 latent（K/V 联合压缩），外加少量 RoPE 部分
        # DeepSeek-V3: latent_dim = 512, rope 部分 = 64 维
        rope_dim = 64
        return seq_len * layers * (latent_dim + rope_dim) * bytes_fp16 / 1e9

# 方案 A: 朴素 MHA（128 KV 头）
gb_plain = kv_gb(128, 192)
# 方案 B: 假设用 GQA（降到 16 KV 头，已经是很激进的 GQA）
gb_gqa = kv_gb(16, 192)
# 方案 C: MLA（latent_dim = 512，DeepSeek-V2/V3 实际配置）
gb_mla = kv_gb(0, 0, latent_dim=512)

print(f"  DeepSeek-V3: {layers} 层, 上下文 {seq_len}, head_dim={head_dim}")
print(f"  方案 A（朴素 MHA, 128 KV 头）: {gb_plain:>8.2f} GB / 单请求")
print(f"  方案 B（激进 GQA, 16 KV 头） : {gb_gqa:>8.2f} GB / 单请求")
print(f"  方案 C（MLA, latent=512）    : {gb_mla:>8.2f} GB / 单请求")
print()
print(f"  压缩比:")
print(f"    MLA vs 朴素 MHA : {gb_plain/gb_mla:>5.1f}x")
print(f"    MLA vs GQA-16   : {gb_gqa/gb_mla:>5.1f}x")
print()
print(f"  → 即使最激进的 GQA（16头），单请求仍要 {gb_gqa:.1f}GB，batch=32 就 {gb_gqa*32:.0f}GB")
print(f"  → 只有 MLA 把单请求压到 {gb_mla:.1f}GB，batch=32 才 {gb_mla*32:.0f}GB，DeepSeek-V3 才能真正部署")
print(f"  → 这就是 MLA 是 2024-2025 最重要架构创新之一的根本原因")

# ============================================================
# 补充：prefill vs decode 的 FLOPs 与带宽账
# ============================================================
print()
print("=" * 64)
print("补充：prefill vs decode 的算力/带宽特性")
print("=" * 64)
# 假设 d_model = 4096, n_layers = 32, seq=2048, 生成 1 token
d_model = 4096
n_layers = 32
seq_prompt = 2048

# prefill：处理整个 prompt，attention 是 seq × seq 矩阵，compute-bound
flops_prefill_attn = n_layers * seq_prompt * seq_prompt * d_model * 2
bytes_prefill = n_layers * seq_prompt * d_model * 2   # 读权重

# decode：每步生成 1 token，attention 是 1 × seq，但要从 HBM 读整个 KV cache
flops_decode_attn = n_layers * 1 * seq_prompt * d_model * 2
bytes_decode = n_layers * (seq_prompt * d_model * 2)   # 读 KV cache（核心）

print(f"  prefill（处理 {seq_prompt} token prompt）:")
print(f"    FLOPs       : {flops_prefill_attn:>14,}")
print(f"    算术强度    : {flops_prefill_attn/bytes_prefill:>10.1f} FLOPs/byte  → compute-bound")
print(f"  decode（生成 1 token，历史 {seq_prompt}）:")
print(f"    FLOPs       : {flops_decode_attn:>14,}")
print(f"    算术强度    : {flops_decode_attn/bytes_decode:>10.1f} FLOPs/byte  → memory-bound")
print(f"  → decode 算术强度比 prefill 低 {flops_prefill_attn/bytes_prefill / (flops_decode_attn/bytes_decode):.0f}x")
print(f"  → 所以 decode 时 GPU 大量算力闲置在等 HBM 数据 → 这是投机解码（speculative decoding）的动机")
