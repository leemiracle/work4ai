"""LQR 横向控制: Riccati 递推求 K, 跟踪参考轨迹 (自行车模型线性化)"""
import torch
torch.manual_seed(0)
dt, L = 0.1, 2.5
# 状态 x=[横向误差e, 航向误差θ, 误差变化率ē, θ̇], 输入 u=前轮转角δ
A = torch.tensor([[1., dt, 0., 0.],
                  [0., 1., 0., dt],
                  [0., 0., 1., 0.],
                  [0., dt*5/L, 0., 1.]])   # 简化运动学线性化
B = torch.tensor([[0.],[0.],[0.],[dt*5/L]])
Q = torch.diag(torch.tensor([10., 5., 1., 1.]))
R = torch.tensor([[0.5]])

# Riccati 递推: P = A'PA - A'PB(R+B'PB)^-1 B'PA + Q
P = Q.clone()
for _ in range(500):
    P = A.T@P@A - (A.T@P@B) @ torch.linalg.inv(R + B.T@P@B) @ (B.T@P@A) + Q
K = torch.linalg.inv(R + B.T@P@B) @ (B.T@P@A)
print(f"✅ LQR 增益 K = {K.numpy().round(3)}")
# 闭环仿真: 初始横向误差1m, 航向误差0.1rad
x = torch.tensor([[1.0], [0.1], [0.], [0.]])
for t in range(80):
    u = -K@x
    x = A@x + B@u
print(f"80步后 误差收敛: e={x[0,0]:.4f}m θ={x[1,0]:.4f}rad {'✓稳定' if abs(x[0,0])<0.05 else '✗发散'}")
print("💡 LQR=线性二次最优控制闭式解, 量产中端横向控制主力")
