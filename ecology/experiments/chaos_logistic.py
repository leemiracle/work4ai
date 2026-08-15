"""实验1: 逻辑斯谛离散模型的混沌分岔图 (May 1976, Nature)
验证: 简单规则可产生复杂性。随 r 增大 -> 倍周期分岔 -> 混沌。
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def logistic_map(N, r, K=1.0):
    return r * N * (1 - N / K)

# 分岔图: 对每个 r, 迭代, 取稳态后的点
rs = np.linspace(1.5, 4.0, 600)
N0 = 0.2
fig, ax = plt.subplots(figsize=(9, 6))

for r in rs:
    N = N0
    # 丢掉前 500 步(瞬态)
    for _ in range(500):
        N = logistic_map(N, r)
    # 记录后 200 步(吸引子)
    pts = []
    for _ in range(200):
        N = logistic_map(N, r)
        pts.append(N)
    ax.scatter([r]*len(pts), pts, s=0.15, c='navy', alpha=0.5, edgecolors='none')

# 标注关键分岔点
ax.axvline(3.0, color='r', ls='--', alpha=0.5)
ax.text(3.02, 0.05, 'r=3 首次分岔(2周期)', color='r', rotation=90, fontsize=8)
ax.axvline(3.449, color='orange', ls='--', alpha=0.5)
ax.text(3.46, 0.05, '4周期', color='orange', rotation=90, fontsize=8)
ax.axvline(3.5699, color='green', ls='--', alpha=0.5)
ax.text(3.58, 0.05, 'r≈3.57 混沌起点', color='green', rotation=90, fontsize=8)
ax.set_xlabel('内禀增长率 r')
ax.set_ylabel('稳态种群 N/K')
ax.set_title('逻辑斯谛离散模型分岔图 (May 1976) —— 简单规则产生混沌')
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig('/tmp/opencode/ecology/fig1_chaos_bifurcation.png', dpi=110)
print("分岔图已保存: fig1_chaos_bifurcation.png")

# 验证: Feigenbaum 常数近似 (4.669...) —— 连续分岔间距比
bifurc_r = [3.0, 3.44949, 3.54409, 3.56441, 3.56876]
deltas = [ (bifurc_r[i+1]-bifurc_r[i])/(bifurc_r[i]-bifurc_r[i-1]) for i in range(1,len(bifurc_r)-1)]
print(f"Feigenbaum δ 估计(理论4.6692): {[f'{d:.3f}' for d in deltas]}")

# 周期检测: r=2.8 -> 1点稳态, r=3.2 -> 2周期, r=3.5 -> 4周期, r=3.9 -> 混沌
print("\n--- 不同 r 的稳态行为 ---")
for r in [2.8, 3.2, 3.5, 3.83, 3.9]:
    N = 0.2
    for _ in range(2000): N = logistic_map(N, r)
    tail = [N:=logistic_map(N, r) for _ in range(8)]
    uniq = len(set([round(x,4) for x in tail]))
    print(f"r={r}: 稳态轨道末8点={tail},  去重后点数={uniq}")
