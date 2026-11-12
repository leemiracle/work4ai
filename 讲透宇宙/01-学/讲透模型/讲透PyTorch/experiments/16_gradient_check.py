"""
实验 04 —— 梯度检查 (gradient check): 用数值微分验证反传正确性
对应文档: 03-VJP统一视角.md (数值梯度 vs 解析梯度)
核心: 反传(解析梯度)可能写错. 用数值微分(中心差分)独立验证它.
      torch.autograd.gradcheck 就是这个工具. 本实验演示它的原理和用法.
跑法: python3 04_gradient_check.py
"""
import torch

print("=" * 66)
print("一、gradcheck: 数值梯度验证解析梯度(反传)")
print("=" * 66)
# 一个简单函数
def f(x):
    return (x * x + torch.sin(x)).sum()

x = torch.randn(4, dtype=torch.double, requires_grad=True)
ok = torch.autograd.gradcheck(f, x, eps=1e-6, atol=1e-4)
print(f"  f(x) = sum(x² + sin(x)), gradcheck 通过: {ok}")
print("  (gradcheck 内部用中心差分算数值梯度, 与反传的解析梯度比较)")

print("\n" + "=" * 66)
print("二、手写梯度检查: 看数值 vs 解析具体差多少")
print("=" * 66)
def f2(x):
    return x.pow(3).sum()   # ∂/∂x = 3x²
x = torch.randn(3, dtype=torch.double, requires_grad=True)
# 解析梯度(反传)
out = f2(x); out.backward()
analytic = x.grad.clone()
# 数值梯度(中心差分) - gradcheck 内部就是这么做
numeric = torch.zeros_like(x)
eps = 1e-6
with torch.no_grad():
    for i in range(3):
        orig = x[i].item()
        x[i] = orig + eps; fp = f2(x).item()
        x[i] = orig - eps; fm = f2(x).item()
        x[i] = orig
        numeric[i] = (fp - fm) / (2 * eps)
# 精确解析: 3x²
exact = 3 * x.detach()**2
print(f"  x = {x.detach().tolist()}")
print(f"  解析(反传)  : {analytic.tolist()}")
print(f"  数值(差分)  : {numeric.tolist()}")
print(f"  精确(3x²)   : {exact.tolist()}")
print(f"  反传 vs 数值最大差: {(analytic-numeric).abs().max().item():.2e}")
print(f"  反传 vs 精确最大差: {(analytic-exact).abs().max().item():.2e}")

print("\n" + "=" * 66)
print("三、故意写错的梯度: gradcheck 能抓出来")
print("=" * 66)
class WrongCube(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        return x ** 3
    @staticmethod
    def backward(ctx, g):
        return g * 2 * x  # 故意写错! 正确应是 3x²·g (这里少了因子3, 也不对)
wc = WrongCube.apply
x = torch.randn(3, dtype=torch.double, requires_grad=True)
try:
    torch.autograd.gradcheck(wc, x)
    print("  gradcheck 通过 (不应该!)")
except RuntimeError as e:
    print(f"  gradcheck 捕获错误! ✓")
    print(f"  说明: 写错的 backward 会被数值梯度当场揭穿")
print("\n核心洞察:")
print("  - 反传(解析梯度)实现易错, 数值微分虽慢但独立可信")
print("  - gradcheck = 用数值梯度验证解析梯度的标准工具, 写自定义算子必跑")
print("  - 工程实践: 开发/调试时 gradcheck, 训练时用反传(快)")
