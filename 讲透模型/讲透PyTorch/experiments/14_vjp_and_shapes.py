"""
实验 02 —— VJP 统一视角 + 梯度形状一致性的精确原因
对应文档: 03-VJP统一视角.md
核心: 反传在每个节点做的就是 雅可比-向量积 J^T·v̄. 本实验:
  1. 用 torch.autograd.functional.vjp 直接展示 VJP
  2. 实证"每层 grad.shape == param.shape"(VJP 维度规则的必然结果)
  3. 手动验证: J^T·v̄ 的维度自动等于输入维度
跑法: python3 02_vjp_and_shapes.py
"""
import torch
import torch.nn as nn

print("=" * 66)
print("一、VJP: 反传在单个节点上做的就是 雅可比转置×向量")
print("=" * 66)
# 定义 f: R^3 -> R^2
def f(x):
    return torch.stack([x[0]*x[1], x[1]+x[2]*x[2]])
x = torch.tensor([2.0, 3.0, 4.0])
# 手算雅可比 J (2x3): [[x1, x0, 0],[0,1,2*x2]] = [[3,2,0],[0,1,8]]
v = torch.tensor([1.0, 1.0])   # 上游梯度 v̄ ∈ R^2
# VJP = J^T · v̄ ∈ R^3 (与输入同形!). vjp 返回 (primal_out, vjp_result)
_, vjp_val = torch.autograd.functional.vjp(f, x, v)
print(f"  f(x) = [x0*x1, x1+x2²] , 输入 x={x.tolist()}")
print(f"  上游梯度 v̄ = {v.tolist()} (输出维度)")
print(f"  VJP = J^T·v̄ = {vjp_val.tolist()} (输入维度, 与 x 同形!)")

# 验证手算雅可比转置
J = torch.tensor([[3.0, 2.0, 0.0], [0.0, 1.0, 8.0]])  # ∂f/∂x
manual_vjp = J.T @ v
print(f"  手算 J^T·v̄ = {manual_vjp.tolist()}  -> 与 torch VJP 一致: {torch.allclose(vjp_val, manual_vjp)} ✓")
print("  => 反传 = 沿图反向、每个节点做一次 J^T·v̄. 输出自动与该节点输入同形")

print("\n" + "=" * 66)
print("二、梯度形状一致的精确原因: VJP 维度规则")
print("=" * 66)
model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
x = torch.randn(5, 4); y = torch.randint(0, 2, (5,))
loss = nn.CrossEntropyLoss()(model(x), y)
loss.backward()
print("  MLP: Linear(4,8)->ReLU->Linear(8,2), 每层 grad.shape vs param.shape:")
for name, p in model.named_parameters():
    g = p.grad
    print(f"    {name:12s} param.shape={tuple(p.shape)}  grad.shape={tuple(g.shape)}  一致={p.shape==g.shape}")
print("\n  为什么必然一致?")
print("    每个参数 W 的雅可比 J ∈ R^(输出维 × 输入维), J^T·v̄ ∈ R^输入维 = W 的形状")
print("    这是线性代数维度规则, 不是框架'特意保证'. 任何形状不符 = 该算子 VJP 实现错了")

print("\n" + "=" * 66)
print("三、JVP vs VJP: 前向模式 vs 反向模式")
print("=" * 66)
# JVP (前向模式): J·u, u ∈ R^输入维 -> 一次算一个输入方向的输出梯度
x3 = torch.tensor([2.0, 3.0, 4.0])   # 重新定义(避免被上面 model 的 x 覆盖)
u = torch.tensor([1.0, 0.0, 0.0])   # 只看 x0 方向
_, jvp_val = torch.autograd.functional.jvp(f, x3, u)
print(f"  JVP (前向模式) J·u, u={u.tolist()}: {jvp_val.tolist()} (输出维)")
print("  - JVP 一次算一个输入方向的输出梯度 -> 要算全 n 输入要跑 n 次")
print("  - VJP 一次算一个输出方向对所有输入 -> loss(m=1) 只跑 1 次就给所有参数梯度")
print("  => 深度学习 n(参数)巨亿、m(loss)=1, 必须用 VJP(反向模式) = 反传")
