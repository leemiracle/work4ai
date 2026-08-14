"""
实验 00 —— 为什么需要激活函数（非线性坍缩演示）
对应文档: 00-为什么需要激活函数.md
核心结论:
  1. 若网络只有线性层(无激活函数),无论堆多深,整体仍等价于一个线性变换 Y = (W_n...W_1) X = W_eff X
  2. 因此无法拟合任何非线性关系(如 sin、异或)
  3. 加入 ReLU 后,网络才获得非线性表达能力
跑法: python3 00_why_activation.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

# ---------------------------------------------------------------
# 证据1: 纯线性网络 == 单层线性变换 (代数恒等)
# ---------------------------------------------------------------
print("=" * 64)
print("证据1: 纯线性网络堆叠 == 单个线性层 (数值验证)")
print("=" * 64)

# 一个"三层线性网络" (注意线性层权重形状 = (out, in))
W1 = torch.randn(4, 8)   # 8 -> 4
W2 = torch.randn(4, 4)   # 4 -> 4
W3 = torch.randn(2, 4)   # 4 -> 2
x = torch.randn(8, 1)

# 逐层算
y_layer_by_layer = W3 @ (W2 @ (W1 @ x))
# 等价合成单矩阵
W_eff = W3 @ W2 @ W1
y_equiv = W_eff @ x

print("逐层前向结果:    ", y_layer_by_layer.flatten().tolist())
print("合成单矩阵结果:   ", y_equiv.flatten().tolist())
print("最大绝对差:       ", (y_layer_by_layer - y_equiv).abs().max().item())
print("==> 差异在浮点误差量级 (~1e-7),即多层线性恒等于单层线性!\n")

# ---------------------------------------------------------------
# 证据2: 拟合非线性目标 sin(x),纯线性 vs 带 ReLU
# ---------------------------------------------------------------
print("=" * 64)
print("证据2: 拟合非线性目标 y = sin(x),纯线性 vs 带 ReLU")
print("=" * 64)

# 数据: y = sin(x), x in [-pi, pi]
x_data = torch.linspace(-3.14, 3.14, 200).unsqueeze(1)
y_data = torch.sin(x_data)

def train(model, steps=3000, lr=0.01):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    for i in range(steps):
        opt.zero_grad()
        pred = model(x_data)
        loss = loss_fn(pred, y_data)
        loss.backward()
        opt.step()
    return loss.item()

# 模型A: 纯线性 (即便很宽也拟合不了 sin)
linear_net = nn.Sequential(nn.Linear(1, 64), nn.Linear(64, 1))
loss_linear = train(linear_net)

# 模型B: 带 ReLU 的两层 MLP (有非线性)
relu_net = nn.Sequential(nn.Linear(1, 64), nn.ReLU(), nn.Linear(64, 1))
loss_relu = train(relu_net)

print(f"纯线性网络  最终 MSE: {loss_linear:.4f}  (无法拟合 sin,loss 居高不下)")
print(f"ReLU 网络   最终 MSE: {loss_relu:.6f}  (成功逼近 sin)")
print("==> 没有 ReLU(非线性),再宽再深的线性网络也学不出 sin!")
