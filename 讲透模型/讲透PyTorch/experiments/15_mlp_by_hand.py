"""
实验 03 —— 手算 MLP 反向传播, 与 autograd 对拍 (把公式落到代码)
对应文档: 04-手算一个MLP的反传.md
核心: 把用户 MLP (1→64→ReLU→1) 的每一步反传公式手动写成 numpy 代码,
      然后与 PyTorch autograd 对拍, 证明手算的链式法则步骤完全正确.
      这是"理解反传"最扎实的一步: 你能亲手复现它.
跑法: python3 03_mlp_by_hand.py
"""
import numpy as np
import torch
import torch.nn as nn

np.random.seed(0); torch.manual_seed(0)

# 网络: x(1) -> z1=W1·x+b1 (64) -> a1=ReLU(z1) (64) -> yhat=W2·a1+b2 (1)
# 用单样本演示 (batch=1), 清晰; 公式直接对应文档 04
W1 = np.random.randn(64, 1).astype(np.float32)   # (64,1)
b1 = np.random.randn(64, 1).astype(np.float32)   # (64,1)
W2 = np.random.randn(1, 64).astype(np.float32)   # (1,64)
b2 = np.random.randn(1, 1).astype(np.float32)    # (1,1)
x = np.random.randn(1, 1).astype(np.float32)     # (1,1)
y = np.array([[0.5]], dtype=np.float32)          # 目标

# ===== 手算前向 + 反向 (每一步都是链式法则) =====
# 前向
z1 = W1 @ x + b1            # (64,1)
a1 = np.maximum(0, z1)      # ReLU (64,1)
yhat = W2 @ a1 + b2         # (1,1)
L = 0.5 * (yhat - y)**2     # 标量损失

# 反向 (从 L 往回)
dL_dyhat = (yhat - y)                       # ∂L/∂yhat (1,1)
dL_dW2 = dL_dyhat @ a1.T                    # ∂L/∂W2 = dL/dyhat · a1^T (1,64)
dL_db2 = dL_dyhat                           # ∂L/∂b2 (1,1)
dL_da1 = W2.T @ dL_dyhat                    # ∂L/∂a1 = W2^T · dL/dyhat (64,1)
dL_dz1 = dL_da1 * (z1 > 0)                  # ReLU 局部导数=掩码 (64,1)
dL_dW1 = dL_dz1 @ x.T                       # ∂L/∂W1 (64,1)
dL_db1 = dL_dz1                             # ∂L/∂b1 (64,1)

print("=" * 66)
print("手算 MLP 反传 (1→64→ReLU→1, 单样本)")
print("=" * 66)
print(f"  前向: L = {L.item():.6f}")
print(f"  反向梯度形状:")
print(f"    dL/dW1 {dL_dW1.shape}  dL/db1 {dL_db1.shape}  dL/dW2 {dL_dW2.shape}  dL/db2 {dL_db2.shape}")
print(f"  (每个 grad 形状都 == 对应参数形状, 这是 VJP 维度规则保证的)")

# ===== 与 PyTorch autograd 对拍 =====
print("\n" + "=" * 66)
print("与 PyTorch autograd 对拍")
print("=" * 66)
tW1 = torch.tensor(W1, requires_grad=True)
tb1 = torch.tensor(b1, requires_grad=True)
tW2 = torch.tensor(W2, requires_grad=True)
tb2 = torch.tensor(b2, requires_grad=True)
tx = torch.tensor(x); ty = torch.tensor(y)
tz1 = tW1 @ tx + tb1
ta1 = torch.relu(tz1)
tyhat = tW2 @ ta1 + tb2
tL = 0.5 * (tyhat - ty)**2
tL.backward()

def cmp(name, manual, torch_grad):
    diff = np.abs(manual - torch_grad.detach().numpy()).max()
    print(f"  {name:10s} 手算 vs autograd 最大差: {diff:.2e}  {'✓ 一致' if diff < 1e-5 else '✗ 不一致'}")

cmp("dL/dW1", dL_dW1, tW1.grad)
cmp("dL/db1", dL_db1, tb1.grad)
cmp("dL/dW2", dL_dW2, tW2.grad)
cmp("dL/db2", dL_db2, tb2.grad)

print("\n核心洞察:")
print("  - 反传每一步 = 上游梯度 × 该层局部导数(雅可比转置)")
print("  - ReLU 的局部导数就是 (z>0) 的 0/1 掩码 (见'讲透激活函数01章')")
print("  - Linear 层: ∂L/∂W = (上游)·(输入)^T, ∂L/∂输入 = W^T·(上游)")
print("  - 你能亲手用 numpy 复现 PyTorch 的 backward, 说明反传不是黑盒")
