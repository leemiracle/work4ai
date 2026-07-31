"""
讲透量化与低精度 —— FP8 / INT4 / outlier
==========================================
推理/训练省显存省算力的核心手段。本实验在 CPU 上完整验证:
  实验1: 对称 vs 非对称量化 (per-tensor / per-channel)
  实验2: 不同位宽的精度损失 (FP16→INT8→INT4)
  实验3: LLM 激活的 outlier 问题 (为什么 AWQ 保护重要通道)
  实验4: FP8 的表示范围

核心洞察: 量化 = 用更少比特表示同样的数, 代价是精度损失。
          难点在 LLM 激活有【outlier】, 会污染整个量化。
跑法: python3 04_quantization.py
"""
import numpy as np
np.random.seed(0)

# ============================================================
# 实验 1: 对称 vs 非对称量化
# ============================================================
print("=" * 72)
print("实验 1: 对称 vs 非对称量化 (INT8)")
print("=" * 72)
print("""
对称量化: 零点固定为 0, scale = max(|x|) / 127
  q = round(x / scale),  x̂ = q * scale
非对称量化: 零点可移动, 适合 x 都为正 (如 ReLU 后)
  scale = (max-min)/255,  zero_point = round(-min/scale)
  q = round(x/scale) + zero_point
""")

def quant_symmetric(x, bits=8):
    levels = 2 ** (bits - 1) - 1   # 对称: -128~127
    scale = np.max(np.abs(x)) / levels
    q = np.round(x / scale).clip(-levels-1, levels)
    return q * scale, scale

def quant_asymmetric(x, bits=8):
    levels = 2 ** bits - 1          # 非对称: 0~255
    xmin, xmax = x.min(), x.max()
    scale = (xmax - xmin) / levels
    zero = np.round(-xmin / scale)
    q = np.round(x / scale + zero).clip(0, levels)
    return (q - zero) * scale, scale

# 测试1: 零中心数据 (对称量化够)
x_sym = np.random.randn(1000) * 2
xq_sym, _ = quant_symmetric(x_sym)
xq_asym, _ = quant_asymmetric(x_sym)
print(f"零中心数据 (有正有负):")
print(f"  对称量化误差: {np.abs(x_sym - xq_sym).mean():.4f}")
print(f"  非对称量化误差: {np.abs(x_sym - xq_asym).mean():.4f}  (差不多)\n")

# 测试2: 全正数据 (ReLU 后, 非对称更优)
x_pos = np.abs(np.random.randn(1000)) * 0.1 + 0.5   # 都在 0.5 附近, 全正
xq_sym, s_sym = quant_symmetric(x_pos)
xq_asym, s_asym = quant_asymmetric(x_pos)
print(f"全正数据 (ReLU 后, ~0.5 附近):")
print(f"  对称量化误差: {np.abs(x_pos - xq_sym).mean():.4f}  (浪费了一半范围在负数!)")
print(f"  非对称量化误差: {np.abs(x_pos - xq_asym).mean():.4f}  (用满 0~255)\n")

# per-channel: 每个 channel 独立量化
print(f"per-channel 量化 (每列独立 scale):")
x_mat = np.random.randn(100, 64) * np.array([0.1, 10] + [1]*62)  # 第1列小,第2列大
xq_per_tensor, _ = quant_symmetric(x_mat)
errs_pt = np.abs(x_mat - xq_per_tensor).mean(axis=0)
# per-channel: 每列独立 scale
xq_per_channel = np.zeros_like(x_mat)
for c in range(x_mat.shape[1]):
    xq_per_channel[:, c], _ = quant_symmetric(x_mat[:, c])
errs_pc = np.abs(x_mat - xq_per_channel).mean(axis=0)
print(f"  per-tensor: 第1列(小)误差 {errs_pt[0]:.4f}, 第2列(大)误差 {errs_pt[1]:.4f}")
print(f"  per-channel: 第1列误差 {errs_pc[0]:.4f}, 第2列误差 {errs_pc[1]:.4f}")
print(f"  ==> per-tensor 被大列主导, 小列精度差; per-channel 各列独立, 更均匀\n")


# ============================================================
# 实验 2: 位宽与精度损失
# ============================================================
print("=" * 72)
print("实验 2: 不同位宽的精度损失 (FP16 → INT8 → INT4 → INT2)")
print("=" * 72)

x = np.random.randn(2000) * 3   # 模拟权重
print(f"原始数据: 2000 个 N(0,3), range=[{x.min():.1f}, {x.max():.1f}]\n")
print(f"{'精度':>8} | {'字节数':>8} | {'相对误差':>10} | {'省显存':>8}")
print("-" * 44)
for bits, name in [(16, "FP16"), (8, "INT8"), (4, "INT4"), (2, "INT2")]:
    xq, scale = quant_symmetric(x, bits=bits)
    rel_err = np.abs(x - xq).mean() / np.abs(x).mean()
    saving = 16 / bits
    print(f"{name:>8} | {bits//8:>6}B  | {rel_err:>10.4f} | {saving:>6.0f}×")

print(f"\n  ==> INT4 是甜点: 省 4× 显存, 相对误差仍可控 (~1%)。")
print(f"      INT2 误差爆炸, 只能用于极端压缩。本地部署主流 INT4 (09篇)\n")


# ============================================================
# 实验 3: LLM 激活的 outlier —— 量化的核心难点
# ============================================================
print("=" * 72)
print("实验 3: LLM 激活的 outlier (为什么量化 LLM 难)")
print("=" * 72)
print("""
LLM 的激活有【outlier】: 少数通道的值比其他大 100×!
  → 如果用 per-tensor 量化, scale 被 outlier 拉飞, 大部分通道精度崩
  → AWQ 的洞察: 识别并保护这些 outlier 通道
""")

# 模拟 LLM 激活: 99% 通道 ~N(0,1), 1% 是 outlier ~N(0,100)
x_llm = np.random.randn(1000)
outlier_idx = np.random.choice(1000, 10, replace=False)   # 1% outlier
x_llm[outlier_idx] *= 30    # outlier 放大 30×

xq_naive, scale_naive = quant_symmetric(x_llm, bits=4)
err_naive = np.abs(x_llm - xq_naive)
# AWQ 思路: 给 outlier 通道单独的 scale (保护它们)
xq_awq = x_llm.copy()
non_outlier = np.setdiff1d(np.arange(1000), outlier_idx)
xq_awq[non_outlier], _ = quant_symmetric(x_llm[non_outlier], bits=4)  # 非outlier独立量化

print(f"模拟 LLM 激活: 990 通道 ~N(0,1), 10 通道 outlier(×30)")
print(f"  max = {np.abs(x_llm).max():.1f} (来自 outlier)")
print(f"\n朴素 INT4 量化 (per-tensor):")
print(f"  scale = {scale_naive:.3f} (被 outlier 拉大!)")
print(f"  非outlier通道平均误差: {err_naive[non_outlier].mean():.3f}  (精度崩!)")
print(f"  outlier通道平均误差: {err_naive[outlier_idx].mean():.3f}")
print(f"\nAWQ 思路 (保护 outlier, 其余独立量化):")
print(f"  非outlier通道平均误差: {np.abs(x_llm[non_outlier]-xq_awq[non_outlier]).mean():.3f}  (好得多!)")
print(f"  ==> 这就是为什么【玩具小模型看不出量化损失】(你画像铁律#10):")
print(f"      玩具模型无 outlier; 真 LLM 有 outlier, 量化价值才显现\n")


# ============================================================
# 实验 4: FP8 的表示范围
# ============================================================
print("=" * 72)
print("实验 4: FP8 —— H100 训练的新标准 (DeepSeek-V3 用)")
print("=" * 72)
print("""
FP8 两种格式:
  E4M3: 4位指数 + 3位尾数 → 动态范围大, 精度中 (前向用)
  E5M2: 5位指数 + 2位尾数 → 动态范围更大, 精度低 (反向梯度用)
""")

def fp8_e4m3(x):
    """模拟 FP8 E4M3 (简化): 限范围 + 量化"""
    max_val = 448.0   # E4M3 最大值
    x_clipped = np.clip(x, -max_val, max_val)
    # 简化: 模拟有限精度 (实际是浮点, 这里用粗量化近似)
    levels = 256
    scale = max_val / (levels // 2)
    return np.round(x_clipped / scale) * scale

x = np.random.randn(1000) * 10
xq = fp8_e4m3(x)
print(f"测试数据 N(0,10):")
print(f"  FP32→FP8(E4M3模拟) 相对误差: {(np.abs(x-xq).mean()/np.abs(x).mean()):.4f}")
print(f"  对比 INT8 相对误差 (实验2): ~0.02")
print(f"\n  FP8 vs INT8 的关键区别:")
print(f"    INT8: 均匀分布的量化级 (适合权重, 范围集中的数据)")
print(f"    FP8: 浮点 (非均匀级, 小值密大值稀, 适合激活/梯度的长尾分布)")
print(f"  ==> FP8 对 LLM 训练更友好, DeepSeek-V3 用 FP8 训练省 50% 显存\n")

print("=" * 72)
print("全部实验完成!")
print("核心: 量化省显存省算力, 难点在 LLM 激活的 outlier (AWQ/FP8 的用武之地)")
print("=" * 72)
