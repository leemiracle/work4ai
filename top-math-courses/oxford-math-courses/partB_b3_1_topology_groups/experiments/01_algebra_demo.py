#!/usr/bin/env python3
"""抽象代数核心实验：群作用 + 对称性（CNN/等变网络的根基）"""
import numpy as np
# ML 关联：CNN=Z^d群卷积；AlphaFold=SE(3)等变；群表示→张量

# 1. 对称群 S_3 的乘法表
def perm(p, x): return [x[i] for i in p]
S3 = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]]  # 6 个置换
print("S₃ 乘法表（部分）:")
for p in S3[:3]:
    for q in S3[:3]:
        pq = [p[q[i]] for i in range(3)]  # 先 q 后 p
        print(f"  {p}∘{q} = {pq}")

# 2. 轨道-稳定子定理
print("\n轨道-稳定子定理: |G| = |轨道| × |稳定子|")
# D_4 (正方形对称群, 8 元素) 作用在 4 个顶点上
corners = [(1,1),(1,-1),(-1,-1),(-1,1)]
# 旋转 90 度
R90 = lambda v: (-v[1], v[0])
v0 = (1, 1)
orbit = {v0}
for _ in range(4):
    v0 = R90(v0); orbit.add(v0)
print(f"  角(1,1) 在 D_4 下的轨道: {orbit} (|轨道|={len(orbit)})")
print(f"  |D_4|=8 = |轨道|×|稳定子| = {len(orbit)}×{8//len(orbit)}")
print("=> CNN = 在 Z^d 群上的等变网络（平移对称）")
