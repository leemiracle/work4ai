"""
实验 07 —— mutation/view 在反传里的边界 (PyTorch 反传最硬核的部分)
对应文档: 08-PyTorch真实反传边界.md (ezyang "Autograd and Mutation")
核心: 真实代码有 in-place 修改和视图别名. 反传的根本立场是'只为纯计算求导',
      它如何处理这些? 本实验展示反传的几个边界行为.
跑法: python3 07_mutation_views.py
"""
import torch

print("=" * 66)
print("一、反传的根本立场: 只为'隐式的纯计算'求导")
print("=" * 66)
# in-place 操作 y.mul_(2) 被反传当成 y2 = y*2
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = x ** 2
y2 = y * 2          # 纯计算版
y2.sum().backward()
print(f"  纯计算: y=x²; y2=y*2; sum(y2).backward()")
print(f"    x.grad = {x.grad.tolist()}  (= 4x, 因为 d(2x²)/dx=4x)")

x2 = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y3 = x2 ** 2
y3.mul_(2)          # in-place 版 (反传等价看待为纯计算!)
y3.sum().backward()
print(f"  in-place: y=x²; y.mul_(2); sum(y).backward()")
print(f"    x2.grad = {x2.grad.tolist()}  (与纯计算完全一致! 反传不为 in-place 单独建规则)")

print("\n" + "=" * 66)
print("二、version counter: 检测'反传用到的值被 mutation 失效'")
print("=" * 66)
x = torch.tensor([1.0, 2.0], requires_grad=True)
y = x ** 2          # y 是非leaf中间结果, 反传需要它的计算
z = y.sum()         # z 依赖 y
print(f"  操作: y=x²; z=sum(y); 然后 y.add_(1) (在非leaf y 上原地改)")
print(f"  改前 y._version = {y._version}")
y.add_(1)           # 在非leaf y 上 in-place (允许), 但破坏了 z 对 y 的依赖版本
print(f"  改后 y._version = {y._version}  (变了!)")
try:
    z.backward()
    print("    backward 成功 (不该)")
except RuntimeError as e:
    print(f"    ✗ 报错: {str(e)[:80]}...")
print("  => 反传靠 version counter 检测: z 依赖的 y 被 in-place 改过, 旧 y 失效, 拒绝算")
print("     这是反传的安全网, 防止用过期数据算出错误梯度")

print("\n" + "=" * 66)
print("三、view + mutation: CopySlices 的用武之地")
print("=" * 66)
# v = y[0]; v.mul_(2) 只改 y 的一行, 反传用 CopySlices 复合节点处理
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)
y = x ** 2
v = y[0]            # view: y 的第0行
v.mul_(2)           # 只改 y 的第0行 (in-place on view)
loss = y.sum()
loss.backward()
print(f"  操作: y=x²; v=y[0]; v.mul_(2); sum(y).backward()")
print(f"    x.grad =\n{x.grad}")
print("  => 第0行梯度是 4x(因 v 被×2, ∂=4x), 第1行是 2x(未改)")
print("     反传用 CopySlices 节点正确处理'view 上的局部 in-place'")
print(f"  v.grad_fn = {v.grad_fn}  (rebase 到新节点)")

print("\n" + "=" * 66)
print("四、detach: 断开梯度但不断 version")
print("=" * 66)
x = torch.tensor([1.0, 2.0], requires_grad=True)
y = x ** 2
yd = y.detach()     # 摘下当普通数据
print(f"  y.requires_grad={y.requires_grad}, yd.requires_grad={yd.requires_grad}")
print(f"  但 yd 仍共享 version counter: y._version={y._version}, yd._version={yd._version}")
print("  => detach 断梯度传播, 但反传安全网(version)仍生效")

print("\n核心洞察 (反传的工程边界):")
print("  - 反传只为'纯计算'求导, in-place 被重写成等价纯计算处理")
print("  - version counter: 检测反传缓存被 mutation 失效, 报错而非算错")
print("  - view 上的 mutation 用 CopySlices + rebase 正确处理")
print("  - 这是'数学反传'到'PyTorch backward'的鸿沟, 见 ezyang 'Autograd and Mutation'")
