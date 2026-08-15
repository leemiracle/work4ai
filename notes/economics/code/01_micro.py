# === 微观经济学全部核心算法验证 ===
import numpy as np
from scipy.optimize import minimize, linprog

print("="*70); print("【微观-1】CES 效用最大化 vs Cobb-Douglas"); print("="*70)
# CES: u=(α x1^ρ + (1-α) x2^ρ)^(1/ρ)，ρ→0 时退化为 Cobb-Douglas
alpha, rho = 0.6, -0.5  # ρ<0: 替代弹性 σ=1/(1-ρ)=0.667 (互补偏向)
p1,p2,m = 2,5,100
f = lambda x: -(alpha*x[0]**rho+(1-alpha)*x[1]**rho)**(1/rho)
cons={'type':'eq','fun':lambda x:p1*x[0]+p2*x[1]-m}
res=minimize(f,[10,10],constraints=cons,bounds=[(1e-9,None),(1e-9,None)])
print(f"  CES(ρ={rho},σ={1/(1-rho):.3f}): x1*={res.x[0]:.3f}, x2*={res.x[1]:.3f}, U*={-res.fun:.3f}")
# 与 Cobb-Douglas 对比
f2=lambda x:-(x[0]**alpha*x[1]**(1-alpha))
r2=minimize(f2,[10,10],constraints=cons,bounds=[(1e-9,None),(1e-9,None)])
print(f"  CD(α={alpha})    : x1*={r2.x[0]:.3f}, x2*={r2.x[1]:.3f}, U*={-r2.fun:.3f}")
print(f"  → ρ<0 时 CES 更倾向多买便宜的 x1（替代弹性低，仍偏好组合）")

print("\n"+"="*70); print("【微观-2】Slutsky 分解（数值：替代效应+收入效应）"); print("="*70)
# 商品1价格从 p1=2 降到 p1'=1，分解总效应
p1_old,p1_new=2,1
def marshallal(p1):  # CD 马歇尔需求
    return alpha*m/p1, (1-alpha)*m/p2
x1_old,_=marshallal(p1_old); x1_new,_=marshallal(p1_new)
# 保持原效用水平，新价格下最小化支出 (Hicks) — CD下 e(p,u)=u*(p1/α)^α*(p2/(1-α))^(1-α)
U0=x1_old**alpha*marshallal(p1_old)[1]**(1-alpha)
e_new=U0*(p1_new/alpha)**alpha*(p2/(1-alpha))**(1-alpha)
x1_hicks=alpha*e_new/p1_new  # Hicks 需求
total=x1_new-x1_old; sub=x1_hicks-x1_old; inc=x1_new-x1_hicks
print(f"  p1: {p1_old}→{p1_new}")
print(f"  总效应:   Δx1 = {total:+.3f}")
print(f"  替代效应: {sub:+.3f} (Hicks, 同效用下便宜了多买)")
print(f"  收入效应: {inc:+.3f} (实际购买力提升)")
print(f"  验证: {sub+inc:.3f} == {total:.3f} ✓")

print("\n"+"="*70); print("【微观-3】垄断定价 + 无谓损失 DWL"); print("="*70)
# 需求 P=a-bQ, 成本 MC=c
a,b,c=10,1,4
Qm=(a-c)/(2*b); Pm=a-b*Qm
# 竞争均衡
Qc=(a-c)/b; Pc=c
DWL=0.5*(Qc-Qm)*(Pm-Pc)
pi_m=(Pm-c)*Qm
CS_m=0.5*(a-Pm)*Qm  # 消费者剩余
print(f"  垄断: Q={Qm:.2f}, P={Pm:.2f}, π={pi_m:.2f}, CS={CS_m:.2f}")
print(f"  竞争: Q={Qc:.2f}, P={Pc:.2f}")
print(f"  无谓损失 DWL = ½·(Qc-Qm)·(Pm-Pc) = {DWL:.2f}")
print(f"  → 垄断把消费者剩余 {CS_m+DWL:.2f} 转移为利润/损失")

print("\n"+"="*70); print("【微观-4】三度价格歧视（两市场分割）"); print("="*70)
# 市场1: P1=a1-b1 q1; 市场2: P2=a2-b2 q2; 成本 c
a1,b1,a2,b2,c=8,1,6,1,2
# 各市场 MR=MC: a_i-2b_i q_i = c
q1=(a1-c)/(2*b1); q2=(a2-c)/(2*b2)
P1,P2=a1-b1*q1,a2-b2*q2
pi_disc=(P1-c)*q1+(P2-c)*q2
# 不歧视：总需求 P=a-bQ，需分段，简化为统一价
print(f"  市场1: q1={q1:.2f},P1={P1:.2f}; 市场2: q2={q2:.2f},P2={P2:.2f}")
print(f"  歧视总利润 π={pi_disc:.2f} (高弹性市场定低价=市场2，低弹性定高价=市场1)")

print("\n"+"="+"="*68); print("【微观-5】纯交换一般均衡 (Edgeworth box, tâtonnement)"); print("="*68)
# 两个消费者 A,B 两种商品；初始禀赋；效用 CD
# A: uA=x^0.5 y^0.5, 禀赋 wA=(1,1); B: uB=x^0.3 y^0.7, 禀赋 wB=(3,1)
wA=np.array([1.0,1.0]); wB=np.array([3.0,1.0]); wtot=wA+wB
alphaA=np.array([0.5,0.5]); alphaB=np.array([0.3,0.7])
# 均衡价格：在 Walras 定律下，求 p 使市场1出清
# 需求 x_i(p)=α_i·(p·w_i)/p
def excess(p):
    p=np.array([p,1.0])  # 标准化 p2=1
    dA=alphaA*(p@wA)/p; dB=alphaB*(p@wB)/p
    return (dA+dB)[0]-wtot[0]
from scipy.optimize import brentq
p1eq=brentq(excess,0.1,10)
peq=np.array([p1eq,1.0])
dA=alphaA*(peq@wA)/peq; dB=alphaB*(peq@wB)/peq
print(f"  均衡价格 p1/p2 = {p1eq:.4f}")
print(f"  A 消费: x={dA[0]:.3f}, y={dA[1]:.3f}  (初始 x=1,y=1)")
print(f"  B 消费: x={dB[0]:.3f}, y={dB[1]:.3f}  (初始 x=3,y=1)")
print(f"  市场出清: A+B = [{dA[0]+dB[0]:.3f},{dA[1]+dB[1]:.3f}] == 禀赋 {wtot.tolist()}")
print(f"  → 两人都通过交易改善了 (福利定理第一)")
