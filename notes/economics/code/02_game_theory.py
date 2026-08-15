# === 博弈论与机制设计全部核心算法 ===
import numpy as np
from itertools import combinations
print("="*70); print("【博弈-1】混合策略 NE (零和: 列玩家最小化)"); print("="*70)
# 零和：行玩家收益矩阵 A
A=np.array([[3,-2,2],[-1,1,4],[-2,-3,7]])
# 行玩家 max min: LP; 列玩家 min max
# 行玩家策略: max v s.t. A^T p >= v, sum p=1
n=A.shape[0]
res1=__import__('scipy.optimize',fromlist=['linprog']).linprog(c=[0]*n+[ -1],
    A_ub=np.hstack([-A.T, np.ones((n,1))]), b_ub=[0]*n,
    A_eq=np.hstack([np.ones((1,n)),[[0]]]), b_eq=[1], bounds=[(0,None)]*(n)+[(None,None)])
p=res1.x[:n]; v=-res1.fun
print(f"  零和博弈值 v={v:.3f}")
print(f"  行玩家混合策略: {[round(x,3) for x in p]}")
print(f"  (minimax 定理: von Neumann 1928, 极小极大=极大极小)")

print("\n"+"="*70); print("【博弈-2】2x2 双矩阵支持枚举法求所有 NE"); print("="*70)
A=np.array([[3,0],[0,2]]); B=np.array([[2,0],[0,3]])  # 性别战变体
def mixed_ne_2x2(A,B):
    res=[]
    for i in [0,1]:
        for j in [0,1]:
            # 纯策略 NE 检查
            if A[i,j]>=A[1-i,j] and B[i,j]>=B[i,1-j]: res.append(("纯",(i,j)))
    # 混合 (双方都用两策略)
    # 行玩家以 p 选0, 使列玩家无差异: B[0,0]*p+B[1,0]*(1-p)==B[0,1]*p+B[1,1]*(1-p)
    denom_r=B[0,0]-B[1,0]-B[0,1]+B[1,1]
    denom_c=A[0,0]-A[0,1]-A[1,0]+A[1,1]
    if denom_r!=0 and denom_c!=0:
        p=(B[1,1]-B[1,0])/denom_r
        q=(A[1,1]-A[0,1])/denom_c
        if 0<=p<=1 and 0<=q<=1: res.append(("混合",(round(p,3),round(q,3))))
    return res
for kind,x in mixed_ne_2x2(A,B): print(f"  {kind} NE: {x}")

print("\n"+"="*70); print("【博弈-3】重复囚徒困境: tit-for-tat 的 Folk 定理阈值"); print("="*70)
# 阶段博弈: T,R,P,S (T>R>P>S, 2R>T+S)
T,R,P,S=5,3,1,0
# 折现 δ. 双方 tit-for-tat vs 永远背叛: 偏离诱惑 vs 长期惩罚
# 偏离一次得 T, 之后回到 P. 合作得 R 持续
# 合作条件: R/(1-δ) >= T + δP/(1-δ)  → δ >= (T-R)/(T-P)
delta_min=(T-R)/(T-P)
print(f"  T={T},R={R},P={P},S={S}")
print(f"  合作可持续的最小折现因子 δ* = (T-R)/(T-P) = {delta_min:.3f}")
print(f"  Folk定理: δ→1 时几乎任何可行个人理性收益都可均衡")

print("\n"+"="*70); print("【博弈-4】Myerson 最优拍卖 (虚拟估值+预留价)"); print("="*70)
# 估值均匀 U[0,1], 虚拟估值 φ(v)=v-(1-F)/f = v-(1-v)/1 = 2v-1
# 最优拍卖: 给虚拟估值>0 的最高者，即 v>=1/2 的最高者；预留价 r=1/2
def phi(v): return 2*v-1
n_bidders=3
np.random.seed(7)
vals=np.random.uniform(0,1,n_bidders)
print(f"  {n_bidders} 个竞标者估值: {[round(v,3) for v in vals]}")
eligible=vals[vals>=0.5]
if len(eligible)>0:
    w=np.argmax(vals*(vals>=0.5))
    pay=max(0.5, np.sort(vals)[-2]) if False else max(0.5, sorted(vals)[-2] if vals[w]!=sorted(vals)[-1] else sorted(vals)[-2])
    print(f"  预留价 r=0.5, 赢家=竞标者{w}, 支付={pay:.3f}, 卖家收益={pay:.3f}")
else:
    print(f"  无估值≥0.5，流拍 (Myerson预留价过滤)")
print(f"  → 虚拟估值法把'最大化收益'化为'最大化虚拟剩余'")

print("\n"+"="*70); print("【博弈-5】VCG 多物品组合拍卖 (externality定价)"); print("="*70)
# 2 个物品 A,B, 3 个竞标者; 估值(组合) -> 简化为加性 + 协同
# b1: A=3,B=2,AB=6 (协同1); b2: A=2,B=4,AB=5; b3: A=1,B=1,AB=3
bids={'b1':{'':0,'A':3,'B':2,'AB':6},'b2':{'':0,'A':2,'B':4,'AB':5},'b3':{'':0,'A':1,'B':1,'AB':3}}
# 枚举所有可行分配，找总价值最大
from itertools import product
items=['A','B']
best=None
for alloc in product(['','A','B','AB'],repeat=3):
    # 检查可行性：每个物品只能给一个人
    used=[]
    feasible=True
    for a in alloc: used+=list(a)
    if sorted(used)!=sorted([x for x in used if x]): pass
    from collections import Counter
    c=Counter()
    for a in alloc:
        for it in a: c[it]+=1
    if any(v>1 for v in c.values()): feasible=False
    if not feasible: continue
    total=sum(bids[f'b{i+1}'][alloc[i]] for i in range(3))
    if best is None or total>best[0]: best=(total,alloc)
total,alloc=best
print(f"  最优分配: {dict(zip(['b1','b2','b3'],alloc))}, 总价值={total}")
# VCG 支付: p_i = (他人不参与时的最大总价值) - (他人参与最优分配中他人的价值)
for i,name in enumerate(['b1','b2','b3']):
    # 他人价值
    others_val=sum(bids[f'b{j+1}'][alloc[j]] for j in range(3) if j!=i)
    # 他人不参与时的最优总价值
    best_o=0
    for a2 in product(['','A','B','AB'],repeat=2):
        c=Counter(); 
        for a in a2:
            for it in a:c[it]+=1
        if any(v>1 for v in c.values()):continue
        v=sum(bids[f'b{j+1}'][a2[k]] for k,j in enumerate([x for x in range(3) if x!=i]))
        best_o=max(best_o,v)
    pay=best_o-others_val
    print(f"  {name}: 获得 '{alloc[i]}'(值{bids[name][alloc[i]]}), VCG支付={pay:.2f}, 效用={bids[name][alloc[i]]-pay:.2f}")

print("\n"+"="*70); print("【博弈-6】Top Trading Cycle (房屋交换)"); print("="*70)
# 4 个人，每人有一房，偏好彼此的房子
houses={'p0':'p2','p1':'p0','p2':'p3','p3':'p1'}  # 每人最想要的房的owner
# 简化: 每轮找指向最爱的环
pref={'p0':['p2','p1','p3'],'p1':['p0','p3','p2'],'p2':['p3','p0','p1'],'p3':['p1','p2','p0']}
assign={}; remaining=set(pref)
while remaining:
    # 每人指向剩余中自己最爱的
    ptr={p:next(h for h in pref[p] if h in remaining) for p in remaining}
    # 找环
    for start in remaining:
        cycle=[start]; cur=ptr[start]
        while cur!=start and cur not in cycle: cycle.append(cur); cur=ptr[cur]
        if cur==start:
            for p in cycle: assign[p]=ptr[p]
            remaining-=set(cycle)
            break
print(f"  TTC 分配: {[(p,'得到'+h+'的房') for p,h in assign.items()]}")
print(f"  → 核心 (core) 配置，无人能集体改进")
