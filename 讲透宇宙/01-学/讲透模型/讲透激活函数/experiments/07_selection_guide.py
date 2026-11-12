"""
实验 07 —— 激活函数场景选型对比 (隐藏层)
对应文档: 本讲解的"场景选择"部分
核心问题: 同一个任务、同样的网络结构, 只换隐藏层激活, 结果差多少?
任务: make_moons (经典非线性二分类, 需要非线性边界)
对比: Sigmoid / Tanh / ReLU / LeakyReLU / GELU / SiLU
产出: activation_selection.png (loss 收敛曲线对比)
跑法: python3 07_selection_guide.py
"""
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(0); np.random.seed(0)

# ---------------------------------------------------------------
# 1. 生成 make_moons 数据 (非线性可分, 激活函数选得好才能学出来)
# ---------------------------------------------------------------
def make_moons(n=2000, noise=0.15):
    n1 = n // 2
    t = np.linspace(0, np.pi, n1)
    X1 = np.c_[np.cos(t), np.sin(t)]
    X2 = np.c_[1 - np.cos(t), -np.sin(t) - 0.5]
    X = np.r_[X1, X2] + np.random.randn(n, 2) * noise
    y = np.r_[np.zeros(n1), np.ones(n1)]
    idx = np.random.permutation(n)
    return X[idx].astype(np.float32), y[idx].astype(np.float32)

X, y = make_moons(n=1000)
Xtr = torch.from_numpy(X[:800]); ytr = torch.from_numpy(y[:800]).unsqueeze(1)
Xte = torch.from_numpy(X[800:]); yte = torch.from_numpy(y[800:]).unsqueeze(1)

# ---------------------------------------------------------------
# 2. 可插拔激活的 MLP (2-32-32-1), 输出层固定 sigmoid (二分类)
# ---------------------------------------------------------------
def build(act_name, depth=6):
    """6 层全连接: 深到足以暴露 sigmoid/tanh 的梯度消失"""
    acts = {
        "Sigmoid": nn.Sigmoid(), "Tanh": nn.Tanh(),
        "ReLU": nn.ReLU(), "LeakyReLU": nn.LeakyReLU(0.1),
        "GELU": nn.GELU(), "SiLU": nn.SiLU(),
    }
    a = acts[act_name]
    layers = [nn.Linear(2, 32), a]
    for _ in range(depth - 1):
        layers += [nn.Linear(32, 32), a]
    layers += [nn.Linear(32, 1), nn.Sigmoid()]
    return nn.Sequential(*layers)

def train_and_eval(act_name, steps=200, lr=0.05):
    torch.manual_seed(0)
    model = build(act_name)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCELoss()
    history = []
    for i in range(steps):
        opt.zero_grad()
        out = model(Xtr)
        loss = loss_fn(out, ytr)
        loss.backward()
        opt.step()
        history.append(loss.item())
    with torch.no_grad():
        acc = ((model(Xte) > 0.5).float() == yte).float().mean().item()
    return history, acc

# ---------------------------------------------------------------
# 3. 跑全部激活, 收集收敛曲线与最终精度
# ---------------------------------------------------------------
print("=" * 60)
print("隐藏层激活函数选型对比 (make_moons 二分类, 同结构 MLP)")
print("=" * 60)
results = {}
histories = {}
for name in ["Sigmoid", "Tanh", "ReLU", "LeakyReLU", "GELU", "SiLU"]:
    h, acc = train_and_eval(name)
    results[name] = acc
    histories[name] = h
    # 收敛步数: loss 首次降到 0.3 以下的步数
    conv = next((i for i, l in enumerate(h) if l < 0.3), -1)
    print(f"  {name:11s}: 最终测试精度={acc*100:5.1f}%  | 收敛(loss<0.3)步数={conv if conv>=0 else '未达':>4}")

# 画收敛曲线 (英文标签避免字体警告)
plt.figure(figsize=(9, 5.5))
for name, h in histories.items():
    plt.plot(h, label=name, linewidth=1.8)
plt.xlabel("Training Step"); plt.ylabel("Training Loss (BCE)")
plt.title("Hidden-Layer Activation Selection on make_moons")
plt.yscale("log"); plt.grid(alpha=0.3); plt.legend()
plt.tight_layout(); plt.savefig("activation_selection.png", dpi=110); plt.close()
print("\nsaved: activation_selection.png")

# ---------------------------------------------------------------
# 4. 反模式演示: 输出层选错激活的代价 (回归任务)
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("反模式: 输出层激活选错 (回归任务 y 输出 [-2, 2])")
print("=" * 60)
Xr = torch.linspace(-3, 3, 300).unsqueeze(1)
yr = 2 * torch.sin(Xr * 1.5)  # 目标范围约 [-2, 2]

def reg_model(out_act):
    return nn.Sequential(nn.Linear(1, 32), nn.ReLU(),
                         nn.Linear(32, 32), nn.ReLU(),
                         nn.Linear(32, 1), out_act)

for name, act, desc in [
    ("Linear(id)", nn.Identity(), "正确: 回归输出层不加激活"),
    ("Sigmoid", nn.Sigmoid(), "错误: 输出被压到(0,1), 永远学不出负值和大值"),
    ("Tanh", nn.Tanh(), "错误: 输出被压到(-1,1), 幅度不够"),
]:
    torch.manual_seed(0)
    m = reg_model(act)
    opt = torch.optim.Adam(m.parameters(), lr=0.01)
    for _ in range(600):
        opt.zero_grad(); ((m(Xr) - yr) ** 2).mean().backward(); opt.step()
    with torch.no_grad():
        pred_range = (m(Xr).min().item(), m(Xr).max().item())
        mse = ((m(Xr) - yr) ** 2).mean().item()
    print(f"  输出层={name:12s}: 预测值域=[{pred_range[0]:+.2f},{pred_range[1]:+.2f}]  目标=[-2,2]  MSE={mse:.4f}  # {desc}")

print("\n结论: 输出层激活由'任务类型'硬性决定, 选错会让模型物理性无法表达目标!")
