import numpy as np
from scipy.optimize import linprog
np.random.seed(1)
T0=10; n_ctrl=5
pre_treated=np.linspace(5,8,T0)+np.random.normal(0,0.1,T0)         # (10,)
pre_ctrl=np.array([np.linspace(4+i*0.2,7+i*0.1,T0)+np.random.normal(0,0.1,T0) for i in range(n_ctrl)])  # (5,10)
# 正确: Q = pre_ctrl @ pre_ctrl.T  (5,5); c = pre_ctrl @ pre_treated (5,)
Q=pre_ctrl@pre_ctrl.T
c=pre_ctrl@pre_treated
res=linprog(c=-c,A_eq=np.ones((1,n_ctrl)),b_eq=1,bounds=[(0,None)]*n_ctrl,method='highs')
w=res.x
synth_pre=w@pre_ctrl
fit_err=np.max(np.abs(pre_treated-synth_pre))
print(f"合成权重: {[round(x,3) for x in w]} (sum={w.sum():.3f})")
print(f"预处理拟合最大误差: {fit_err:.3f} (应≈0, 证明合成对照完美再现处理单位预处理轨迹)")
post_treated=pre_treated[-1]+np.linspace(0.5,2.5,5)+np.random.normal(0,0.1,5)
post_ctrl=np.array([pre_ctrl[i,-1]+np.linspace(0,0.5,5)+np.random.normal(0,0.1,5) for i in range(n_ctrl)])
synth_post=w@post_ctrl
effect=(post_treated-synth_post).mean()
print(f"政策后处理-合成 均值效应 = {effect:.3f}")
print(f"(Abadie 合成控制: 用对照单位的凸组合构造'反事实'处理单位)")
