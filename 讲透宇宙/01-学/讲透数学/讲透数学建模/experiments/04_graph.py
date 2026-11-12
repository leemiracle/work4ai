"""
实验 04 — 图与网络：PageRank 幂法
====================================
迭代计算网页重要性。被重要页面链接 = 更重要。
跑法: python3 04_graph.py  (需 numpy, <1秒)
"""
import numpy as np

# 4 页面链接图（列=源，行=目标；每列归一化）
# A→B; B→A,C,D; C→D; D→B
P = np.array([
    [0.0, 1/3, 0.0, 0.0],   # A 的入链
    [1.0, 0.0, 0.0, 1.0],   # B
    [0.0, 1/3, 0.0, 0.0],   # C
    [0.0, 1/3, 1.0, 0.0],   # D
])

d, N = 0.85, 4
pr = np.ones(N) / N

for i in range(100):
    pr_new = (1 - d) / N + d * P @ pr
    if np.allclose(pr, pr_new, atol=1e-8):
        break
    pr = pr_new

print("=" * 50)
print("PageRank（d=0.85, 收敛于第 %d 步）" % i)
print("=" * 50)
for name, score in zip(["A", "B", "C", "D"], pr):
    bar = "█" * int(score * 40)
    print(f"  {name}: {score:.4f} {bar}")
print()
print("B 最重要（被 A 和 D 链接，D 只链 B）")
print("C 最不重要（只被 B 的 1/3 链接）")
