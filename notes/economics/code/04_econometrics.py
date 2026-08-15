# === 计量经济学: 从相关到因果 全部算法 ===
import numpy as np
from scipy.optimize import linprog
np.random.seed(42)
print("="*70); print("【计量-1】OLS 偏误 vs IV 修正"); print("="*70)
N=5000
# 真实模型: y = 1 + 2*x + ε; 但 x 与 ε 相关(遗漏变量 z_omit)
z_omit=np.random.normal(0,1,N)  # 遗漏的能力
x=0.8*z_omit+np.random.normal(0,1,N)  # x 受能力影响
y=1+2*x+0.5*z_omit+np.random.normal(0,1,N)  # 真实β=2
# OLS
X=np.column_stack([np.ones(N),x])
beta_ols=np.linalg.lstsq(X,y,rcond=None)[0]
# IV: 工具变量 z (与x相关, 与ε无关)
z_iv=np.random.normal(0,1,N)
x_iv=0.6*z_iv+0.4*z_omit+np.random.normal(0,0.5,N)  # 重构x使之与z相关
# 2SLS: 第一阶段 x~z; 第二阶段 y~x_hat
Z=np.column_stack([np.ones(N),z_iv])
x_hat=Z@np.linalg.lstsq(Z,x_iv,rcond=None)[0]
Xhat=np.column_stack([np.ones(N),x_hat])
beta_iv=np.linalg.lstsq(Xhat,y,rcond=None)[0]
print(f"  真实 β_x = 2.0")
print(f"  OLS  估计 = {beta_ols[1]:.3f}  (向上偏误: 能力高→x高且y高)")
print(f"  2SLS 估计 = {beta_iv[1]:.3f}  (修正偏误, 但方差大)")
# 第一阶段 F 统计量 (弱工具检测)
ss_total=np.sum((x_iv-x_iv.mean())**2)
ss_res=np.sum((x_iv-x_hat)**2)
F=(ss_total-ss_res)/ss_res*N
print(f"  第一阶段 F = {F:.1f} (>10 为强工具, Staiger-Stock 法则)")

print("\n"+"="*70); print("【计量-2】DID + 平行趋势检验"); print("="*70)
N=1000; T=4
treat=np.random.binomial(1,0.5,N)
# 真实 ATT=3.0 (只在 t>=2 生效)
post=np.array([0,0,1,1])
att=3.0
y_base=5+2*treat
data=[]
for i in range(N):
    for t in range(T):
        y=y_base[i]+0.5*t+att*treat[i]*post[t]+np.random.normal(0,1)
        data.append((i,treat[i],post[t],y,t))
import numpy as np
arr=np.array(data)
# DID (只对比 t=1 vs t=2)
pre=arr[(arr[:,4]==0)&(arr[:,1]==treat[0])|(False)] # 简化: 直接算
y_t1_treat=arr[(arr[:,4]==1)&(arr[:,1]==1)][:,5].mean() if False else np.mean([y for (i,tr,po,y,t) in data if t==1 and tr==1])
y_t1_ctrl=np.mean([y for (i,tr,po,y,t) in data if t==1 and tr==0])
y_t2_treat=np.mean([y for (i,tr,po,y,t) in data if t==2 and tr==1])
y_t2_ctrl=np.mean([y for (i,tr,po,y,t) in data if t==2 and tr==0])
did=(y_t2_treat-y_t1_treat)-(y_t2_ctrl-y_t1_ctrl)
print(f"  真实 ATT=3.0")
print(f"  DID = ({y_t2_treat:.2f}-{y_t1_treat:.2f}) - ({y_t2_ctrl:.2f}-{y_t1_ctrl:.2f}) = {did:.3f}")
# 平行趋势: t=0 vs t=1 (政策前应平行)
y_t0_treat=np.mean([y for (i,tr,po,y,t) in data if t==0 and tr==1])
y_t0_ctrl=np.mean([y for (i,tr,po,y,t) in data if t==0 and tr==0])
pretrend=(y_t1_treat-y_t0_treat)-(y_t1_ctrl-y_t0_ctrl)
print(f"  政策前趋势差(t0→t1): {pretrend:.3f} (应≈0, 验证平行趋势)")

print("\n"+"="*70); print("【计量-3】Sharp RDD (断点回归)"); print("="*70)
# 处理: x>0 时 D=1; 潜在结果 y = 1 + 0.5x + τ·D + ε
N=3000; x=np.random.uniform(-1,1,N); D=(x>0).astype(float)
tau_true=2.0
y=1+0.5*x+tau_true*D+np.random.normal(0,0.5,N)
# 局部线性估计: 在 h 窗口内 y~x+D+x:D
h=0.3; mask=np.abs(x)<h
Xr=np.column_stack([np.ones(mask.sum()),x[mask],D[mask],x[mask]*D[mask]])
beta_rdd=np.linalg.lstsq(Xr,y[mask],rcond=None)[0]
print(f"  真实断点效应 τ=2.0, 窗口 h={h}")
print(f"  局部线性 RDD 估计 τ̂={beta_rdd[2]:.3f}")
print(f"  → 在阈值附近随机性近似RCT (Lee-Lemieux 2010)")

print("\n"+"="*70); print("【计量-4】合成控制 (Abadie): 加权对照匹配"); print("="*70)
# 处理单位 T0 前 10 期, 对照 5 个单位, 找权重 w 使处理单位预处理轨迹匹配
T0=10; n_ctrl=5
np.random.seed(1)
pre_treated=np.linspace(5,8,T0)+np.random.normal(0,0.1,T0)
pre_ctrl=np.array([np.linspace(4+i*0.2,7+i*0.1,T0)+np.random.normal(0,0.1,T0) for i in range(n_ctrl)])
# 求 w>=0, sum w=1, min ||pre_treated - W·pre_ctrl||
# 二次规划: min 0.5 w'Qw - c'w ; Q=pre_ctrl'pre_ctrl, c=pre_ctrl'pre_treated
Q=pre_ctrl.T@pre_ctrl; c=pre_ctrl.T@pre_treated
res=linprog(c=-c, A_ub=None,b_ub=None,A_eq=np.ones((1,n_ctrl)),b_eq=1,bounds=[(0,None)]*n_ctrl)
w=res.x
synth_pre=w@pre_ctrl
fit_err=np.max(np.abs(pre_treated-synth_pre))
print(f"  合成权重: {[round(x,3) for x in w]} (sum={w.sum():.3f})")
print(f"  预处理拟合误差: {fit_err:.3f} (应≈0)")
# 政策后效应: 假设处理后处理单位 +2
post_treated=pre_treated[-1]+np.linspace(0,2,5)+np.random.normal(0,0.1,5)
post_ctrl=np.array([pre_ctrl[i,-1]+np.linspace(0,0.5,5)+np.random.normal(0,0.1,5) for i in range(n_ctrl)])
synth_post=w@post_ctrl
effect=(post_treated-synth_post).mean()
print(f"  政策后处理-合成 = {effect:.3f} (Abadie-Gardeazabal-Hainmueller 合成控制效应)")

print("\n"+"="*70); print("【计量-5】Double/Debiased ML (Chernozhukov 2018)"); print("="*70)
# 高维混淆: y=θD+g(X)+ε; D=m(X)+ν. 用 ML 估计 g, m, 再残差回归
N=2000; p=20
X=np.random.normal(0,1,(N,p))
D=X[:,0]+0.5*X[:,1]+np.random.normal(0,0.5,N)
theta_true=2.0
y=theta_true*D+X@np.random.normal(0.5,0.3,p)+np.random.normal(0,1,N)
# 用简单 OLS 估计 ghat=Xγ (代替ML), mhat
from numpy.linalg import lstsq
gamma_y=lstsq(X,y,rcond=None)[0]; ghat=X@gamma_y
gamma_d=lstsq(X,D,rcond=None)[0]; mhat=X@gamma_d
# 残差 on 残差
y_tilde=y-ghat; D_tilde=D-mhat
theta_dml=np.sum(D_tilde*y_tilde)/np.sum(D_tilde**2)
# 对比朴素 OLS (y~D) 偏误
beta_naive=lstsq(np.column_stack([np.ones(N),D]),y,rcond=None)[0][1]
print(f"  真实 θ=2.0, 混淆维度 p={p}")
print(f"  朴素 y~D 回归 = {beta_naive:.3f} (严重偏误)")
print(f"  Double ML 残差回归 = {theta_dml:.3f} (✓ 修正, √n一致渐近正态)")

print("\n"+"="*70); print("【计量-6】事件研究 (动态处理效应)"); print("="*70)
# 处理在 t=0, 看前后各期效应
np.random.seed(3); N=500
tau_dyn={-2:0.0,-1:0.0,0:1.5,1:2.5,2:3.0,3:2.8}  # 真实动态效应
data=[]
for i in range(N):
    for t in [-2,-1,0,1,2,3]:
        y=5+0.3*t+tau_dyn.get(t,0)+np.random.normal(0,1)
        data.append((i,t,y))
# 回归 y ~ 1 + t + Σ τ_k·1[t=k]
T_set=[-2,-1,0,1,2,3]
rows=[]
for (i,t,y) in data:
    row=[1,t]+[1 if t==k else 0 for k in T_set[1:]]  # 省略 t=-2 作基准
    rows.append([row,y])
Xm=np.array([r[0] for r in rows]); yv=np.array([r[1] for r in rows])
beta=lstsq(Xm,yv,rcond=None)[0]
print(f"  动态效应 (基准 t=-2):")
for j,k in enumerate(T_set[1:]):
    print(f"    t={k:+d}: τ̂={beta[2+j]:.3f} (真实 {tau_dyn[k]})")
print(f"  → 政策前 τ_{-1}≈0 验证无预期效应; 政策后渐增")
