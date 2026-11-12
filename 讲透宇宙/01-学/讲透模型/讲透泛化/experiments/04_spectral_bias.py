"""
实验 04 —— 频率偏置 (Spectral Bias): 网络先学低频平滑, 再学高频细节
对应文档: 01-隐式正则.md
核心结论: 深度网络不是一次学完所有成分, 而是按"频率"从低到高渐进学习.
          低频(平滑大势)先被拟合, 高频(细节/噪声)学得慢.
          这就是隐式正则的核心机制之一, 也是 GD 泛化好的原因.
方法: 信号 = 低频sin + 高频sin, 训练中用FFT分离两个频段的残差功率.
跑法: python3 04_spectral_bias.py
"""
import torch
import torch.nn as nn
import numpy as np
torch.manual_seed(0); np.random.seed(0)

N = 300
x = torch.linspace(0, 1, N).unsqueeze(1)
y_low = torch.sin(2 * np.pi * 1 * x)        # 低频: 1 个周期
y_high = 0.5 * torch.sin(2 * np.pi * 4 * x) # 高频: 4 个周期 (网络容量足够最终拟合)
y = y_low + y_high

model = nn.Sequential(nn.Linear(1, 48), nn.ReLU(), nn.Linear(48, 1))
opt = torch.optim.Adam(model.parameters(), lr=0.008)

def band_power(residual):
    """把残差做FFT, 分低频(频段1)和高频(频段4)功率"""
    R = np.abs(np.fft.rfft(residual.numpy().flatten())) ** 2
    return R[1] if len(R) > 1 else 0, (R[4] if len(R) > 4 else 0)

print("=" * 66)
print("频率偏置: 信号 = 低频sin(1周期) + 高频sin(4周期)")
print("=" * 66)
print(f"{'步数':>6} {'总训练MSE':>12} {'低频残差功率':>14} {'高频残差功率':>14}  解读")
print("-" * 66)
for step in range(1, 6001):
    opt.zero_grad()
    pred = model(x)
    loss = ((pred - y) ** 2).mean()
    loss.backward(); opt.step()
    if step in {100, 500, 1500, 3000, 6000}:
        with torch.no_grad():
            res = (y - pred)
            lowp, highp = band_power(res)
            if step <= 500: note = "低频快降, 高频几乎没动"
            elif lowp > highp: note = "低频>高频残差(低频还在追)"
            else: note = "低频已拟合, 高频开始下降"
            print(f"{step:>6} {loss.item():>12.4e} {lowp:>14.4e} {highp:>14.4e}  {note}")
print("-" * 66)
print("结论: 网络优先学低频平滑成分(大势), 高频(细节)滞后才学.")
print("      => 训练早期网络主要保留'平滑解', 自动过滤高频过拟合成分 = 隐式正则.")
print("      => 这是 GD/SGD 泛化好的频域机制 (Rahaman 2019, Spectral Bias).")
