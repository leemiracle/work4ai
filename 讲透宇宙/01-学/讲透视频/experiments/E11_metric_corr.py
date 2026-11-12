"""
E11 解答 · 评估指标与人类偏好的相关性(方法论演示)
===================================================
自动指标可信吗? 用 Spearman 秩相关衡量"指标排序 ≈ 人类偏好排序"。
本脚本用手写 Spearman(不依赖 scipy) 在合成数据上演示完整方法论;
真实场景替换为 VBench 分数 + 人类打分即可。

运行: python3 E11_metric_corr.py    # 约 2 秒
输出: E11_metric_corr.png
"""
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def spearman(a, b):
    """手写 Spearman 秩相关: 秩变换 + Pearson。"""
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / (np.linalg.norm(ra) * np.linalg.norm(rb) + 1e-12))


rng = np.random.default_rng(0)
n = 12  # 样本视频数

# 隐变量: 真实质量 q
q = rng.uniform(0, 1, n)
# 人类偏好 = 真实质量 + 噪声(人类也不完全一致)
human = q + rng.normal(0, 0.12, n)
# 指标A(如 VBench 某维): 与质量强相关 → 好指标
metric_A = q + rng.normal(0, 0.10, n)
# 指标B(如 FVD 单独): 与质量基本无关 → 差指标
metric_B = rng.uniform(0, 1, n)
# 指标C: 中等相关
metric_C = q + rng.normal(0, 0.35, n)

rA, rB, rC = spearman(metric_A, human), spearman(metric_B, human), spearman(metric_C, human)
print(f"[Spearman ρ vs 人类偏好]  指标A(强相关): {rA:+.3f}")
print(f"{' '*24}指标B(无关):    {rB:+.3f}")
print(f"{' '*24}指标C(中等):    {rC:+.3f}")
print(f"  判读: |ρ|>0.7 高可信; 0.4-0.7 中等; <0.4 该维度与人类偏好脱节。")

# Bootstrap 置信区间(方法论关键: 报告区间而非点值)
def boot_ci(x, y, B=2000):
    rs = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        rs.append(spearman(x[idx], y[idx]))
    return np.percentile(rs, [2.5, 97.5])

for name, m, r in [('A', metric_A, rA), ('B', metric_B, rB), ('C', metric_C, rC)]:
    lo, hi = boot_ci(m, human)
    print(f"  指标{name}: ρ={r:+.2f}  95%CI [{lo:+.2f}, {hi:+.2f}]{'  ← CI含0, 不可信!' if lo < 0 < hi else ''}")

fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8))
for ax, (name, m, r) in zip(axes, [('指标A(强)', metric_A, rA), ('指标B(无关)', metric_B, rB), ('指标C(中)', metric_C, rC)]):
    ax.scatter(m, human, s=60, alpha=0.8)
    ax.set_xlabel(f'{name} 分数'); ax.set_ylabel('人类偏好')
    ax.set_title(f'Spearman ρ = {r:+.2f}', color='#369' if abs(r) > 0.6 else '#c66')
plt.suptitle('E11 · 指标可信度 = 与人类偏好的秩相关(Bootstrap 报区间)', fontweight='bold')
plt.tight_layout(); plt.savefig('E11_metric_corr.png', dpi=110, bbox_inches='tight')
print("\n[输出] E11_metric_corr.png")
print("  真实操作: 12 个 Wan/HunyuanVideo 生成视频 → VBench 16 维分数 + ≥5 人打分 → 本脚本。")
