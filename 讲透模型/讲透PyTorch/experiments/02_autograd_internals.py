"""
实验 02 —— 透视 autograd 内部: grad_fn / 计算图 / no_grad / detach / grad累积
对应文档: 01-Autograd与计算图.md
核心目标: 看清 PyTorch autograd 的真实内部结构, 理解每个常见操作的意义.
跑法: python3 02_autograd_internals.py
"""
import torch

print("=" * 64)
print("一、grad_fn: 每个运算都留下'出生证明'")
print("=" * 64)
x = torch.tensor([2.0, 3.0], requires_grad=True)
y = x * 2
z = y.sum()
print(f"x = {x}  (requires_grad={x.requires_grad})")
print(f"y = x*2 = {y.detach()}  -> y.grad_fn = {y.grad_fn}")
print(f"z = y.sum() = {z}  -> z.grad_fn = {z.grad_fn}")
print("  => grad_fn 记录'我是怎么算出来的'. 反向时用它回溯 (就是手写版的 _backward)")
print(f"  => x 是用户创建的, x.grad_fn = {x.grad_fn} (叶子节点, 无 grad_fn)")

print("\n" + "=" * 64)
print("二、计算图是 DAG (有向无环图), backward 后默认释放")
print("=" * 64)
x = torch.tensor(3.0, requires_grad=True)
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)
y = torch.relu(w * x + b)
y.backward()
print(f"  y = relu({w.item()}*{x.item()} + {b.item()}) = {y.item()}")
print(f"  dy/dw = {w.grad.item()}, dy/dx = {x.grad.item()}, dy/db = {b.grad.item()}")
print("  计算图: x,w,b -> w*x -> +b -> relu -> y. backward 沿图反向传梯度")
print(f"  backward 后 y.grad_fn 是否保留: {y.grad_fn} (默认释放, 省内存)")

print("\n" + "=" * 64)
print("三、梯度累积 (为何必须 optimizer.zero_grad!)")
print("=" * 64)
x = torch.tensor(2.0, requires_grad=True)
for i in range(3):
    y = (x ** 2).sum()   # dy/dx = 2x = 4
    y.backward()
    print(f"  第{i+1}次 backward 后, x.grad = {x.grad.item()}  (应是4, 但在累积!)")
print("  => PyTorch 梯度默认'累积'而非'覆盖'. 训练循环不清零会梯度爆炸!")
print("  => 这就是 optimizer.zero_grad() 必不可少的原因 (也支持手动 x.grad=None)")

print("\n" + "=" * 64)
print("四、三种'切断梯度'的方式: no_grad / detach / requires_grad_")
print("=" * 64)
# 1. torch.no_grad(): 上下文内不建图 (推理/评估时用, 省内存加速)
x = torch.tensor(2.0, requires_grad=True)
with torch.no_grad():
    y = x * 3
print(f"  torch.no_grad() 内: y=x*3, y.requires_grad = {y.requires_grad} (不跟踪, 推理用)")
# 2. .detach(): 从计算图摘下一个 tensor (当普通数据用)
x = torch.tensor(2.0, requires_grad=True)
y = x ** 2
yd = y.detach()
print(f"  y.detach(): y.requires_grad={y.requires_grad}, yd.requires_grad={yd.requires_grad} (摘下当数据)")
print(f"  典型用途: 记录 loss 值用 loss.detach().item() (否则计算图累积内存泄漏!)")
# 3. requires_grad_(False): 就地关闭
x = torch.tensor(2.0, requires_grad=True)
x.requires_grad_(False)
print(f"  x.requires_grad_(False) 后: {x.requires_grad} (冻结参数用, 如预训练 backbone)")

print("\n" + "=" * 64)
print("五、retain_graph: 同一个图 backward 两次")
print("=" * 64)
x = torch.tensor(2.0, requires_grad=True)
y = x ** 2 + x ** 3   # 共享 x 的计算
y.backward(retain_graph=True)
g1 = x.grad.item()
y.backward()           # 第二次需要 retain_graph, 否则报错(图已释放)
g2 = x.grad.item()
print(f"  第一次 backward: grad={g1}; 第二次: grad={g2} (累积)")
print("  => retain_graph=True 保留计算图供多次 backward (如 GAN/高阶梯度场景)")

print("\n核心洞察:")
print("  - grad_fn = 手写版的 _backward (记录运算怎么求导)")
print("  - 计算图 = 前向时自动建的 DAG, backward 后默认释放")
print("  - 梯度累积 = PyTorch 设计选择, 训练必须 zero_grad")
print("  - no_grad(推理)/detach(取值)/requires_grad_(冻结) 三种断梯度方式各司其职")
