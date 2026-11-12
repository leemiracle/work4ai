"""
讲透优化器 —— 综合实验脚本
============================
3 个子实验, 一次性讲透优化器:
  实验1: 2D 优化轨迹可视化 (最有冲击力!)
         在 Rosenbrock 香蕉函数 + 病态椭圆碗上, 手动 numpy 实现
         SGD / Momentum / AdaGrad / RMSProp / Adam, 画出下降轨迹
  实验2: 学习率敏感性矩阵 (SGD vs Adam, 谁对 lr 更宽容)
  实验3: 真实训练 loss 曲线 (小网络拟合, 6 个 torch 优化器对比)

跑法: python3 optimizer_overview.py
核心洞察: 所有优化器都是在解决"梯度是噪声 + 各方向曲率不同"这个矛盾
"""
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
torch.manual_seed(0)

# ============================================================
# 手动实现 5 个优化器 (本质就是几行 numpy!)
# ============================================================
class SGD:
    def __init__(self, lr=0.01): self.lr = lr; self.t = 0
    def step(self, theta, grad):
        return theta - self.lr * grad

class Momentum:
    """重球惯性: 平滑震荡方向, 加速一致方向"""
    def __init__(self, lr=0.01, mu=0.9):
        self.lr = lr; self.mu = mu; self.v = None
    def step(self, theta, grad):
        if self.v is None: self.v = np.zeros_like(theta)
        self.v = self.mu * self.v - self.lr * grad    # 惯性累积
        return theta + self.v

class AdaGrad:
    """累积历史梯度平方, 大梯度方向步子缩小"""
    def __init__(self, lr=0.5, eps=1e-8):
        self.lr = lr; self.eps = eps; self.G = None
    def step(self, theta, grad):
        if self.G is None: self.G = np.zeros_like(theta)
        self.G += grad ** 2                           # 只增不减!
        return theta - self.lr * grad / (np.sqrt(self.G) + self.eps)

class RMSProp:
    """指数移动平均代替总和, 只看最近的梯度"""
    def __init__(self, lr=0.1, rho=0.9, eps=1e-8):
        self.lr = lr; self.rho = rho; self.eps = eps; self.E = None
    def step(self, theta, grad):
        if self.E is None: self.E = np.zeros_like(theta)
        self.E = self.rho * self.E + (1 - self.rho) * grad ** 2
        return theta - self.lr * grad / (np.sqrt(self.E) + self.eps)

class Adam:
    """Momentum(惯性) + RMSProp(自适应) + 偏差校正"""
    def __init__(self, lr=0.05, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr = lr; self.b1 = beta1; self.b2 = beta2; self.eps = eps
        self.m = None; self.v = None; self.t = 0
    def step(self, theta, grad):
        if self.m is None:
            self.m = np.zeros_like(theta); self.v = np.zeros_like(theta)
        self.t += 1
        self.m = self.b1 * self.m + (1 - self.b1) * grad            # 一阶矩
        self.v = self.b2 * self.v + (1 - self.b2) * grad ** 2       # 二阶矩
        mhat = self.m / (1 - self.b1 ** self.t)                     # 偏差校正
        vhat = self.v / (1 - self.b2 ** self.t)
        return theta - self.lr * mhat / (np.sqrt(vhat) + self.eps)


# ============================================================
# 两个经典测试地形
# ============================================================
def rosenbrock(theta):
    """Rosenbrock 香蕉函数: 弯曲峡谷, 优化器的噩梦
       全局最小在 (1,1), 但峡谷又窄又弯"""
    x, y = theta
    return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

def rosenbrock_grad(theta):
    x, y = theta
    dx = -2 * (1 - x) - 400 * x * (y - x ** 2)
    dy = 200 * (y - x ** 2)
    return np.array([dx, dy])

def ill_bowl(theta):
    """病态椭圆碗: x 方向比 y 方向陡 10 倍, SGD 会震荡"""
    x, y = theta
    return 10 * x ** 2 + y ** 2

def ill_bowl_grad(theta):
    x, y = theta
    return np.array([20 * x, 2 * y])


def optimize(optimizer, grad_fn, theta0, n_steps):
    """跑 n_steps 步, 返回轨迹"""
    theta = theta0.copy()
    traj = [theta.copy()]
    for _ in range(n_steps):
        g = grad_fn(theta)
        theta = optimizer.step(theta, g)
        traj.append(theta.copy())
    return np.array(traj)


# ============================================================
# 实验 1: 2D 优化轨迹可视化
# ============================================================
print("=" * 72)
print("实验 1: 2D 优化轨迹 (手动 numpy 实现 5 个优化器)")
print("=" * 72)

fig, axes = plt.subplots(2, 3, figsize=(18, 11))

terrains = [
    ("Ill-conditioned bowl:  10x^2 + y^2", ill_bowl, ill_bowl_grad,
     np.array([2.0, 2.0]), (-3, 3, -3, 3), [0.02, 0.02, 0.5, 0.3, 0.3]),
    ("Rosenbrock banana:  (1-x)^2 + 100(y-x^2)^2", rosenbrock, rosenbrock_grad,
     np.array([-1.2, 1.0]), (-1.5, 2.2, -0.5, 2.5), [0.002, 0.001, 0.5, 0.01, 0.01]),
]

opt_names = ["SGD", "Momentum", "AdaGrad", "RMSProp", "Adam"]
opt_classes = [SGD, Momentum, AdaGrad, RMSProp, Adam]
colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]

for row, (title, fn, grad_fn, start, lims, lrs) in enumerate(terrains):
    # 画等高线背景 (第一列占满)
    ax_bg = axes[row, 0]
    xs = np.linspace(lims[0], lims[1], 400)
    ys = np.linspace(lims[2], lims[3], 400)
    X, Y = np.meshgrid(xs, ys)
    Z = np.array([[fn(np.array([x, y])) for x in xs] for y in ys])
    ax_bg.contourf(X, Y, Z, levels=30, cmap="viridis", alpha=0.6)
    ax_bg.contour(X, Y, Z, levels=30, colors="white", linewidths=0.4, alpha=0.5)

    # 画 5 个优化器轨迹 (都画在背景图上)
    n_steps = 150 if row == 0 else 3000
    for name, cls, lr, col in zip(opt_names, opt_classes, lrs, colors):
        opt = cls(lr=lr)
        traj = optimize(opt, grad_fn, start, n_steps)
        ax_bg.plot(traj[:, 0], traj[:, 1], "-", color=col, linewidth=1.8,
                   label=f"{name}", alpha=0.9)
        ax_bg.scatter([traj[-1, 0]], [traj[-1, 1]], color=col, s=40, zorder=5,
                      edgecolors="white", linewidths=0.8)
    ax_bg.scatter([start[0]], [start[1]], marker="*", color="white", s=200,
                  zorder=6, edgecolors="black", linewidths=1)
    ax_bg.set_title(title, fontsize=11)
    ax_bg.legend(fontsize=8, loc="upper right")
    ax_bg.set_xlim(lims[0], lims[1]); ax_bg.set_ylim(lims[2], lims[3])

    # 右边两列: 放大画 SGD 和 Adam 的单独对比 (突出差异)
    for col_idx, (name_idx, panel_title) in enumerate(
        [(0, "SGD: zigzags in ravine"), (4, "Adam: smooth & adaptive")], start=1):
        ax = axes[row, col_idx]
        ax.contourf(X, Y, Z, levels=30, cmap="viridis", alpha=0.6)
        ax.contour(X, Y, Z, levels=30, colors="white", linewidths=0.4, alpha=0.5)
        cls = opt_classes[name_idx]; lr = lrs[name_idx]
        traj = optimize(cls(lr=lr), grad_fn, start, n_steps)
        ax.plot(traj[:, 0], traj[:, 1], "-", color=colors[name_idx], linewidth=1.8)
        ax.scatter([traj[0, 0]], [traj[0, 1]], marker="*", color="white", s=150,
                   zorder=6, edgecolors="black")
        ax.scatter([traj[-1, 0]], [traj[-1, 1]], color=colors[name_idx], s=50, zorder=5)
        # 标记终点(真实最小值)
        if row == 1:
            ax.scatter([1], [1], marker="x", color="lime", s=120, linewidths=3, zorder=7)
        ax.set_title(f"{panel_title}", fontsize=10)
        ax.set_xlim(lims[0], lims[1]); ax.set_ylim(lims[2], lims[3])

plt.tight_layout()
fig.savefig("trajectories.png", dpi=110)
print("  ==> 6 张轨迹图已存 trajectories.png")

# 实验1 量化: 各优化器在 Rosenbrock 上 3000 步后的误差
print("\n  Rosenbrock (起点 -1.2, 1.0, 真实最小 1,1) 各优化器 3000 步后:")
for name, cls, lr in zip(opt_names, opt_classes, lrs):
    opt = cls(lr=lr)
    traj = optimize(opt, rosenbrock_grad, np.array([-1.2, 1.0]), 3000)
    final = traj[-1]
    err = np.linalg.norm(final - np.array([1.0, 1.0]))
    print(f"    {name:10s}: 终点=({final[0]:+.3f},{final[1]:+.3f})  距最小值={err:.4f}")
print("  ==> SGD 几乎卡住, Adam 最接近 (1,1)\n")


# ============================================================
# 实验 2: 学习率敏感性矩阵 (SGD vs Adam, 谁更宽容)
# ============================================================
print("=" * 72)
print("实验 2: 学习率敏感性  (拟合 sin, SGD vs Adam, 4 个 lr)")
print("=" * 72)

x_data = torch.linspace(-3.14, 3.14, 200).unsqueeze(1)
y_data = torch.sin(x_data)
loss_fn = nn.MSELoss()

def train_one(opt_name, lr, steps=800):
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(1, 32), nn.ReLU(), nn.Linear(32, 1))
    if opt_name == "SGD":
        opt = torch.optim.SGD(model.parameters(), lr=lr)
    else:
        opt = torch.optim.Adam(model.parameters(), lr=lr)
    losses = []
    for _ in range(steps):
        opt.zero_grad()
        loss = loss_fn(model(x_data), y_data)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    return losses

lrs = [0.001, 0.01, 0.1, 1.0]
fig2, axes2 = plt.subplots(1, 2, figsize=(15, 5.5))
for col, opt_name in enumerate(["SGD", "Adam"]):
    ax = axes2[col]
    for lr in lrs:
        losses = train_one(opt_name, lr)
        ax.semilogy(losses, label=f"lr={lr}", linewidth=1.6)
    ax.set_xlabel("step"); ax.set_ylabel("loss (log)")
    ax.set_title(f"{opt_name}: learning rate sensitivity")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    ax.set_ylim(1e-6, 1)
fig2.tight_layout()
fig2.savefig("lr_sensitivity.png", dpi=110)
print("  ==> 学习率敏感性图已存 lr_sensitivity.png")

print("\n  最终 loss (800 步):")
print(f"  {'lr':>8} | {'SGD':>12} | {'Adam':>12} | {'谁稳':>6}")
print("  " + "-" * 50)
for lr in lrs:
    sgd_loss = train_one("SGD", lr)[-1]
    adam_loss = train_one("Adam", lr)[-1]
    note = ""
    if np.isnan(sgd_loss): note = "SGD 爆炸"
    elif np.isnan(adam_loss): note = "Adam 爆炸"
    print(f"  {lr:>8.3f} | {sgd_loss:>12.2e} | {adam_loss:>12.2e} | {note}")
print("  ==> Adam 在 lr=0.001~0.1 全能收敛; SGD 在 lr=1.0 直接爆炸")
print("      这就是 'Adam 对学习率更宽容' 的量化含义\n")


# ============================================================
# 实验 3: 真实训练 loss 曲线 (6 个优化器对比)
# ============================================================
print("=" * 72)
print("实验 3: 6 个 torch 优化器, 同一任务 loss 曲线对比")
print("=" * 72)

opts_config = [
    ("SGD",          torch.optim.SGD,     dict(lr=0.05)),
    ("SGD+Momentum", torch.optim.SGD,     dict(lr=0.05, momentum=0.9)),
    ("AdaGrad",      torch.optim.Adagrad, dict(lr=0.05)),
    ("RMSProp",      torch.optim.RMSprop, dict(lr=0.01)),
    ("Adam",         torch.optim.Adam,    dict(lr=0.01)),
    ("AdamW",        torch.optim.AdamW,   dict(lr=0.01, weight_decay=0.01)),
]

fig3, ax3 = plt.subplots(figsize=(11, 6))
colors3 = ["#e41a1c", "#ff7f00", "#4daf4a", "#984ea3", "#377eb8", "#a65628"]

print(f"  {'优化器':>14} | {'500步 loss':>12} | {'收敛速度':>10}")
print("  " + "-" * 46)
for (name, opt_cls, kw), col in zip(opts_config, colors3):
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(1, 32), nn.ReLU(), nn.Linear(32, 1))
    opt = opt_cls(model.parameters(), **kw)
    losses = []
    for _ in range(500):
        opt.zero_grad()
        loss = loss_fn(model(x_data), y_data)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    ax3.semilogy(losses, label=name, linewidth=2, color=col)
    # 找首次低于 0.01 的步数
    below = next((i for i, l in enumerate(losses) if l < 0.01), "未达到")
    print(f"  {name:>14} | {losses[-1]:>12.2e} | {below}")

ax3.set_xlabel("step"); ax3.set_ylabel("loss (log)")
ax3.set_title("6 optimizers on sin-fit task (same init, same architecture)")
ax3.legend(fontsize=10); ax3.grid(alpha=0.3)
fig3.tight_layout()
fig3.savefig("training_curves.png", dpi=110)
print("\n  ==> 训练曲线图已存 training_curves.png")
print("\n  观察:")
print("    1. 纯 SGD 最慢 (无惯性无自适应)")
print("    2. SGD+Momentum 大幅提速 (惯性累积)")
print("    3. Adam/RMSProp 收敛最快最稳 (自适应学习率)")
print("    4. AdamW = Adam + 正确的权重衰减 (LLM 微调标配)")

print("\n" + "=" * 72)
print("全部 3 个实验完成! 产物:")
print("  trajectories.png     - 2D 优化轨迹 (核心可视化)")
print("  lr_sensitivity.png   - 学习率敏感性")
print("  training_curves.png  - 训练曲线对比")
print("=" * 72)
