"""
实验 05 —— 梯度消失与梯度爆炸 (深度网络的连乘诅咒)
对应文档: 06-反传的故障.md
核心: 反传是局部导数的连乘. 深层网络里:
  - 局部导数 <1 (sigmoid) -> 连乘指数衰减 -> 梯度消失, 浅层学不动
  - 局部导数 >1 (大权重) -> 连乘指数增长 -> 梯度爆炸, 训练崩溃
  - ReLU 正轴导数=1 -> 不衰减, 配合残差连接让深网可训
本实验实测每层梯度范数随深度的变化.
跑法: python3 05_vanishing_exploding.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

print("=" * 66)
print("梯度消失/爆炸: 20 层网络每层权重梯度范数 (浅层=靠输入)")
print("=" * 66)

def grad_profile(act_name):
    act = {"Sigmoid": nn.Sigmoid(), "ReLU": nn.ReLU(), "Tanh": nn.Tanh()}[act_name]
    layers = [nn.Linear(32, 32)]
    for _ in range(19):
        layers += [act, nn.Linear(32, 32)]
    model = nn.Sequential(*layers)
    x = torch.randn(4, 32)
    loss = model(x).pow(2).sum()
    loss.backward()
    norms = []
    for m in model:
        if isinstance(m, nn.Linear) and m.weight.grad is not None:
            norms.append(m.weight.grad.norm().item())
    return norms

for name in ["Sigmoid", "Tanh", "ReLU"]:
    norms = grad_profile(name)
    print(f"\n[{name}] 每层梯度范数 (层0=最浅/靠输入, 层19=最深/靠输出):")
    for i, n in enumerate(norms):
        bar = "#" * min(40, max(0, int(n * 8)))
        print(f"  Linear {i:2d}: {n:10.3e}  {bar}")
    if norms:
        ratio = norms[-1] / max(norms[0], 1e-30)
        print(f"  深/浅梯度比 = {ratio:.2e}")

print("\n" + "=" * 66)
print("数学根因: 局部导数连乘")
print("=" * 66)
print(f"  Sigmoid 最大导数 = 0.25 -> 0.25^20 = {0.25**20:.2e} (消失)")
print(f"  ReLU    正轴导数 = 1.0  -> 1.0^20  = {1.0**20:.2e} (不消失)")
print("  (Tanh 导数最大1但|x|稍大骤降, 深层仍会衰减)")

print("\n" + "=" * 66)
print("残差连接: 给梯度一条绕过连乘的高速公路")
print("=" * 66)
torch.manual_seed(0)
# 带残差的 20 层网络 (每层 y = x + f(x))
class ResBlock(nn.Module):
    def __init__(self, act):
        super().__init__()
        self.fc = nn.Linear(32, 32); self.act = act
    def forward(self, x):
        return x + self.act(self.fc(x))   # 残差: 梯度可经 +x 直接流过

for name, act in [("Sigmoid+Res", nn.Sigmoid()), ("ReLU+Res", nn.ReLU())]:
    torch.manual_seed(0)
    model = nn.Sequential(*[ResBlock(act) for _ in range(20)])
    x = torch.randn(4, 32)
    model(x).pow(2).sum().backward()
    norms = [m.fc.weight.grad.norm().item() for m in model]
    print(f"  [{name}] 浅层梯度范数: {norms[0]:.4f}  深层: {norms[-1]:.4f}  (残差让浅层不再消失!)")

print("\n核心洞察:")
print("  - 反传 = 局部导数连乘, 这是消失/爆炸的根 (不是 bug, 是链式法则的必然)")
print("  - 解决: ReLU(导数=1) + 残差连接(梯度短路) + 合理初始化 + BatchNorm/LayerNorm")
print("  - 这也是 ResNet 能训上百层、Transformer 用残差+LayerNorm 的根本原因")
