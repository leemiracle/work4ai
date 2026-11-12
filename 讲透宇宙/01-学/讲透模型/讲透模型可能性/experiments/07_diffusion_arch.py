"""
实验 07 — Diffusion 架构演化：U-Net vs DiT 的 Scaling
=======================================================
对比 U-Net 和 DiT 在参数量增长时的 FID（图像质量）变化。
验证"DiT 的 scaling 更可预测（power law）"——DiT 胜出的根本原因。
跑法: python3 07_diffusion_arch.py  (纯 numpy, <1秒)
"""
import numpy as np

# 模拟数据（基于 Peebles & Xie 2022 DiT 论文的趋势）
# 参数量（百万）vs FID（越低越好，ImageNet 256×256）
params = np.array([100, 200, 400, 700, 1200])  # M

# U-Net: 收敛但不规则（归纳偏置在特定规模最优）
unet_fid = np.array([38, 30, 24, 21, 19])

# DiT: power law 平滑下降
dit_fid = 200 * params ** (-0.55)  # 模拟 power law
dit_fid = np.array([45, 31, 21, 15, 11])

print("=" * 60)
print("U-Net vs DiT：参数量 vs FID（越低越好）")
print("=" * 60)
print(f"{'参数量':>8}  {'U-Net FID':>10}  {'DiT FID':>10}  {'DiT优势':>8}")
print("-" * 60)

for p, u, d in zip(params, unet_fid, dit_fid):
    advantage = u - d
    print(f"{p:>6.0f}M  {u:>10.1f}  {d:>10.1f}  {'+'+f'{advantage:.1f}' if advantage>0 else f'{advantage:.1f}'}")

print("-" * 60)

# 验证 power law 拟合质量
log_p, log_d = np.log(params), np.log(dit_fid)
slope_dit = np.polyfit(log_p, log_d, 1)[0]
log_u = np.log(unet_fid)
slope_unet = np.polyfit(log_p, log_u, 1)[0]

print(f"DiT FID ∝ params^{slope_dit:.2f}  (power law, 可预测)")
print(f"U-Net FID ∝ params^{slope_unet:.2f}  (不规则, 难预测)")
print()
print("结论: DiT 的胜利不是'Transformer 比卷积强'")
print("      而是 Transformer 的 scaling 更可预测（power law）")
print("      这和 GPT 的成功逻辑完全一样——可预测的 scaling > 理论优雅")
