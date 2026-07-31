"""
实验 01 —— ReLU 自动微分与反向传播 (手动掩码 vs autograd 对比)
对应文档: 01-ReLU自动微分与反向传播.md
核心结论:
  1. ReLU 前向: Y = max(0, X)
  2. 反向: dL/dX = dL/dY ⊙ M, 其中 M = (X > 0) 是布尔掩码 (梯度门控)
  3. x <= 0 处导数约定为 0 (次梯度约定), 框架用掩码实现而非存整个 X
  4. 手写掩码反向与 PyTorch autograd 结果完全一致
跑法: python3 01_relu_autograd.py
"""
import torch

torch.manual_seed(42)

# ---------------------------------------------------------------
# 第一步: 手写 ReLU 前向 + 反向, 透明展示"梯度门控"
# ---------------------------------------------------------------
print("=" * 64)
print("第一步: 手写 ReLU 前向/反向 (透视梯度门控机制)")
print("=" * 64)

X = torch.tensor([-2.0, -0.5, 0.0, 0.5, 2.0, 3.0])
print(f"输入 X        = {X.tolist()}")

# 前向: Y = max(0, X)
Y = torch.clamp(X, min=0)
print(f"前向 Y=max(0,X) = {Y.tolist()}")

# 关键: 缓存的不是整个 X, 而是"布尔掩码" (省显存)
# 注: 也可以直接用 Y > 0 生成掩码 (in-place 优化)
Mask = (X > 0).float()       # 这就是 ReLU 的局部导数 f'(x) 的离散版
print(f"掩码 M=(X>0)   = {Mask.tolist()}   <-- 这就是反向时的局部导数")
print(f"  对应 x<=0 处: 局部导数=0 (次梯度约定, x=0 取 0)")
print(f"  对应 x>0  处: 局部导数=1 (无损通行)")

# 假设上游梯度 dL/dY (来自上一层 / 损失)
grad_Y = torch.tensor([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
print(f"\n上游梯度 dL/dY = {grad_Y.tolist()}")

# 反向: dL/dX = dL/dY ⊙ M  (Hadamard 积)
grad_X_manual = grad_Y * Mask
print(f"手算 dL/dX = dL/dY ⊙ M = {grad_X_manual.tolist()}")
print("  x<=0 位置: 上游梯度被截断为 0 (门关闭)")
print("  x>0  位置: 上游梯度原样通过 (门打开)")

# ---------------------------------------------------------------
# 第二步: 用 autograd 验证手算结果
# ---------------------------------------------------------------
print("\n" + "=" * 64)
print("第二步: PyTorch autograd 验证 (应与手算完全一致)")
print("=" * 64)

X2 = X.clone().requires_grad_(True)
Y2 = torch.relu(X2)
# 用与上面相同的上游梯度做反向
Y2.backward(grad_Y)

print(f"autograd dL/dX = {X2.grad.tolist()}")
print(f"手算     dL/dX = {grad_X_manual.tolist()}")
print(f"两者最大差: {(X2.grad - grad_X_manual).abs().max().item():.2e}  ==> 完全一致 ✓")

# ---------------------------------------------------------------
# 第三步: 验证"缓存掩码而非整个输入"的工程优化
# ---------------------------------------------------------------
print("\n" + "=" * 64)
print("第三步: 工程优化——用输出 Y>0 代替存输入 X (in-place, 省显存)")
print("=" * 64)
# 等价掩码: 因为 Y>=0 恒成立, 且 Y>0 当且仅当 X>0
Mask_from_Y = (Y > 0).float()
print(f"由 X>0 得掩码: {Mask.tolist()}")
print(f"由 Y>0 得掩码: {Mask_from_Y.tolist()}")
print(f"两种掩码一致: {torch.equal(Mask, Mask_from_Y)}  ==> 反向时无需保留输入 X, 进一步省显存")
