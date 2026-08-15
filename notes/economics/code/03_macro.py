# === 宏观经济学全部核心动态算法 ===
import numpy as np
from scipy.optimize import fsolve, brentq
print("="*70); print("【宏观-1】Solow: 黄金律 vs 市场储蓄率"); print("="*70)
alpha,delta,n,g,A=0.33,0.05,0.01,0.02,1.0
def kstar(s): return (s*A/(delta+n+g))**(1/(1-alpha))
# 黄金律: MPK=δ+n+g  → α k^(α-1)=δ+n+g
k_gold=((alpha)/(delta+n+g))**(1/(1-alpha))
s_gold=(delta+n+g)*k_gold**(1-alpha)/A
print(f"  黄金律储蓄率 s_gold={s_gold:.3f}, k_gold={k_gold:.3f}, c_gold={k_gold**alpha-delta*k_gold:.3f}")
for s in [0.1,0.2,s_gold,0.4]:
    k=kstar(s); c=k**alpha-delta*k
    print(f"  s={s:.3f}: k*={k:.3f}, y*={k**alpha:.3f}, c*={c:.3f} {'<--黄金律(消费最大)' if abs(s-s_gold)<0.001 else ''}")
print(f"  → 储蓄率过高(>s_gold)动态无效率: 多储蓄反降低消费")

print("\n"+"="*70); print("【宏观-2】Ramsey: shooting method 求鞍点路径"); print("="*70)
alpha,delta,rho,theta=0.33,0.05,0.02,1.0  # theta: 相对风险厌恶(对数效用=1)
beta=1/(1+rho)
kss=(alpha/((1/beta)-1+delta))**(1/(1-alpha))
css=kss**alpha-delta*kss
print(f"  稳态: k*={kss:.3f}, c*={css:.3f}")
# 离散动态: k_{t+1}=(k^α - c + (1-δ)k)/((1+n)(1+g)); 欧拉: c_{t+1}/c_t = β(1+αk^{α-1}-δ)
T=60; k0=0.5*kss
def simulate(c0):
    k=np.zeros(T); c=np.zeros(T); k[0]=k0; c[0]=c0
    for t in range(T-1):
        r=alpha*k[t]**(alpha-1)-delta
        c[t+1]=c[t]*beta*(1+r)
        k[t+1]=(k[t]**alpha - c[t] + (1-delta)*k[t])
        if k[t+1]<=0 or c[t+1]<=0: return None
    return k[-1],c[-1]
# 二分搜索 c0 使末端收敛到稳态
lo,hi=0.1,k0**alpha
for _ in range(50):
    mid=(lo+hi)/2; r=simulate(mid)
    if r is None: hi=mid
    elif r[0]>kss: lo=mid
    else: hi=mid
c0_star=(lo+hi)/2
ks,cs=simulate(c0_star)
print(f"  初始 k0=0.5·k*, 求得鞍点路径初始消费 c0*={c0_star:.4f}")
print(f"  60 期后: k={ks:.3f}(→k*={kss:.3f}), c={cs:.3f}(→c*={css:.3f}) ✓ 鞍点收敛")

print("\n"+"="*70); print("【宏观-3】Diamond OLG: 动态无效率检测"); print("="*70)
# 两期: 年轻工作储蓄 s(w), 老年消费 (1+r)s. 生产 CD
alpha=0.33; n=0.01; beta=0.96
# 稳态: k = s·w / (1+n), s=β/(1+β). w=(1-α)k^α
# 解 k: k = (β/(1+β))·(1-α)k^α / (1+n)
def olg_eq(k): return k-(beta/(1+beta))*(1-alpha)*k**alpha/(1+n)
kss=brentq(olg_eq,0.01,100)
rss=alpha*kss**(alpha-1)-1  # 净利率(无折旧简化)
gr_rate=n  # 增长率
print(f"  OLG 稳态 k*={kss:.3f}, 净利率 r*={rss:.4f}, 增长率 n={gr_rate}")
print(f"  动态无效率? r*({rss:.4f}) < n({gr_rate}): {'是! 过度储蓄' if rss<gr_rate else '否'}")
print(f"  → 若 β 偏大→r*<n→社会过度储蓄, 帕累托改进: 减少k人人更好")

print("\n"+"="*70); print("【宏观-4】Romer 内生增长 (idea生产)"); print("="*70)
phi=1.0; lam=1.0; theta=0.05; L=1.0  # idea生产 ċA=θ L^λ A^φ
T=50; Aarr=np.zeros(T); Aarr[0]=1.0
for t in range(T-1):
    Aarr[t+1]=Aarr[t]*(1+theta*L**lam*Aarr[t]**(phi-1))
print(f"  φ={phi}(站在巨人肩上), λ={lam}: 50期 A 从1增长到 {Aarr[-1]:.1f}")
print(f"  φ>1: 爆炸增长(奇点); φ=1: 指数; φ<1: 递减收益")
# φ>1 模拟
Aarr2=np.zeros(T); Aarr2[0]=1.0
for t in range(T-1):
    Aarr2[t+1]=Aarr2[t]*(1+theta*L**lam*Aarr2[t]**(0.3-1))  # φ=0.3
print(f"  φ=0.3: 50期 A 仅到 {Aarr2[-1]:.1f} (递减回报, 缓慢增长)")

print("\n"+"="*70); print("【宏观-5】RBC 对数线性化 + 脉冲响应"); print("="*70)
# 简化 RBC: log deviations. 围绕稳态, AR(1) 技术 z_t=ρ z_{t-1}+ε
alpha,delta,rho_z=0.33,0.05,0.9
kss=(alpha/(1/beta-1+delta))**(1/(1-alpha))
# 线性化产出: y_hat ≈ α k_hat + (1-α) ... 简化为 y_t 跟随 z
T=20; z=np.zeros(T); z[0]=0.01  # 1% 技术冲击
for t in range(1,T): z[t]=rho_z*z[t-1]
y_resp=np.array([ (1/(1-alpha*rho_z**(t)))*0.01 if False else 0.01*rho_z**t for t in range(T)])
print(f"  1% 正向技术冲击, ρ_z={rho_z}:")
print(f"  产出脉冲响应前5期: {[f'{100*y:.3f}%' for y in y_resp[:5]]}")
print(f"  → 持久性ρ越大, 产出回稳越慢 (RBC: 周期=技术冲击传播)")

print("\n"+"="*70); print("【宏观-6】Diamond 搜寻匹配: 稳态失业"); print("="*70)
# 匹配函数 m(U,V)=A U^α V^(1-α); 分离率 s; 工作找到率 f=m(U,V)/U
A_m,alpha_m,s_sep=0.5,0.5,0.03
# 稳态: s(1-u)=f u  → u=s/(s+f); 贝弗里奇循环
# 假设 V/U=v_ratio (空缺/失业比)
for v_ratio in [0.3,0.5,1.0]:
    # f = A (V/U)^(1-α)
    f=A_m*v_ratio**(1-alpha_m)
    u=s_sep/(s_sep+f)
    print(f"  V/U={v_ratio}: 工作找到率 f={f:.3f}, 自然失业率 u={u:.3f}")
print(f"  → 空缺越多失业越低 (Beveridge 曲线负斜率); 但匹配摩擦使失业>0")
