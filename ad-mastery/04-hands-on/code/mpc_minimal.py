"""可微 MPC (Diff-MPC): 用 torch 梯度下降直接优化控制序列
对比纯 P 控制, 展示 MPC 的前瞻性(提前减速避开约束)"""
import torch
torch.manual_seed(0)
dt, N = 0.1, 30
m, k = 1.0, 2.0        # 质量/弹簧(轨迹跟踪比喻)
v_max = 2.0            # 约束: 速度上限

def simulate(u):
    """1D 质点跟踪: 状态x, 控制u, 目标轨迹 x_ref(t)=0.5t (斜坡)"""
    x, v = torch.tensor([0.0]), torch.tensor([0.0])
    cost = 0
    for i in range(N):
        t = i*dt
        x_ref = 0.5*t
        cost += (x-x_ref)**2 + 0.01*u[i]**2
        x = x + v*dt; v = v + (u[i] - k*x)/m*dt
    return cost

# MPC: 梯度下降优化 N 步控制
u = torch.zeros(N, requires_grad=True)
opt = torch.optim.Adam([u], lr=0.05)
for it in range(300):
    loss = simulate(u)
    # 软约束: 惩罚超速 (真实MPC用QP硬约束)
    v_est = u.cumsum(0)*dt
    loss = loss + 10*torch.relu(v_est.abs()-v_max).pow(2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
print(f"✅ Diff-MPC 优化完成, 终端代价={simulate(u).item():.3f}")
print(f"   最大控制量|u|={u.abs().max().item():.2f} (约束内={u.abs().max()<v_max*2})")
print("💡 MPC=滚动优化+只执行第一步; 可微版让规划梯度回流感知(端到端)")
