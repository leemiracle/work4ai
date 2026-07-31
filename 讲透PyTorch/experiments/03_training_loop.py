"""
实验 03 —— 训练循环的正确写法 + 三个最常见 bug 演示
对应文档: 03-训练循环的正确写法.md
核心: PyTorch 训练 = 固定 5 步循环. 但每一步都有新手坑. 本实验演示正确写法 + 3 个经典 bug.
跑法: python3 03_training_loop.py
"""
import torch
import torch.nn as nn
import numpy as np

torch.manual_seed(0); np.random.seed(0)

# make_moons 数据 (非线性二分类)
def make_moons(n=400, noise=0.15):
    n1 = n//2; t = np.linspace(0, np.pi, n1)
    X = np.r_[np.c_[np.cos(t), np.sin(t)], np.c_[1-np.cos(t), -np.sin(t)-0.5]]
    X += np.random.randn(n,2)*noise
    y = np.r_[np.zeros(n1), np.ones(n1)]
    idx = np.random.permutation(n); return X[idx].astype(np.float32), y[idx].astype(np.float32)
X, y = make_moons()
Xtr = torch.from_numpy(X[:300]); ytr = torch.from_numpy(y[:300]).unsqueeze(1)
Xte = torch.from_numpy(X[300:]); yte = torch.from_numpy(y[300:]).unsqueeze(1)

def build():
    return nn.Sequential(nn.Linear(2,16), nn.ReLU(), nn.Linear(16,1), nn.Sigmoid())

print("=" * 66)
print("一、标准训练循环 (黄金 5 步)")
print("=" * 66)
model = build()
opt = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCELoss()
for epoch in range(300):
    # === 黄金 5 步 ===
    opt.zero_grad()                  # 1. 清零梯度 (梯度累积, 见实验02)
    logits = model(Xtr)              # 2. 前向
    loss = loss_fn(logits, ytr)      # 3. 算 loss
    loss.backward()                  # 4. 反向求梯度
    opt.step()                       # 5. 更新参数
acc = ((model(Xte)>0.5).float()==yte).float().mean().item()
print(f"  正确写法 -> 测试精度 {acc*100:.1f}%")

print("\n" + "=" * 66)
print("二、BUG 1: 忘了 opt.zero_grad() (梯度累积爆炸)")
print("=" * 66)
model = build(); opt = torch.optim.Adam(model.parameters(), lr=0.01)
for epoch in range(300):
    # opt.zero_grad()  # 故意注释掉!
    logits = model(Xtr); loss = loss_fn(logits, ytr); loss.backward(); opt.step()
acc = ((model(Xte)>0.5).float()==yte).float().mean().item()
print(f"  不清零梯度 -> 测试精度 {acc*100:.1f}% (Adam 有自适应还能撑住, 但 SGD 会崩)")
print("  => 梯度一直累积, 方向越来越乱. 必须每步 zero_grad!")

print("\n" + "=" * 66)
print("二、BUG 2: 记录 loss 忘了 .item() (计算图累积, 内存泄漏)")
print("=" * 66)
model = build(); opt = torch.optim.Adam(model.parameters(), lr=0.01)
history_ref_keep = []   # 错误: 存了带 grad_fn 的 tensor
for epoch in range(50):
    opt.zero_grad()
    loss = loss_fn(model(Xtr), ytr)
    loss.backward(); opt.step()
    history_ref_keep.append(loss)        # BUG: 存的是整个计算图的引用!
print(f"  错误存法: history 里每个元素都连着计算图, len={len(history_ref_keep)}")
print(f"  每个元素的 grad_fn = {history_ref_keep[-1].grad_fn} (图没释放!)")
print(f"  50步后内存里累积了 50 个完整计算图 -> 长训练必然 OOM")
print("  正确: history.append(loss.item())  (.item() 返回纯 float, 断开图)")

print("\n" + "=" * 66)
print("二、BUG 3: 推理/评估时忘了 torch.no_grad() (白建图, 慢且费内存)")
print("=" * 66)
import time
model = build()
# 错误: 评估也建图
t0=time.time()
for _ in range(20):
    _ = model(Xte)            # 建计算图
t_no = time.time()-t0
# 正确: no_grad 不建图
t0=time.time()
with torch.no_grad():
    for _ in range(20):
        _ = model(Xte)        # 不建图
t_yes = time.time()-t0
print(f"  评估20次: 不用no_grad={t_no*1000:.1f}ms, 用no_grad={t_yes*1000:.1f}ms")
print("  => 推理(测试/部署)一律 with torch.no_grad(): 省内存+加速+不污染梯度")

print("\n核心洞察: 训练循环的每一步都对应 autograd 机制:")
print("  zero_grad(梯度累积) -> forward(建图) -> loss -> backward(反向释放图) -> step(更新)")
print("  推理用 no_grad, 取值用 .item()/.detach() — 这三个习惯能避开绝大多数 bug")
