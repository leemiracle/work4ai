"""
实验 04 —— nn.Module 透视: 参数管理 / 子模块 / state_dict / hooks
对应文档: 02-nnModule与参数管理.md
核心: 所有模型(从 Linear 到 Transformer)都是 nn.Module 的组织. 搞懂它的:
  1. 自动参数注册 (parameters / named_parameters)
  2. 嵌套子模块 (children / modules)
  3. state_dict (保存/加载的本质)
  4. hooks (窥探/修改中间层, 调试与可视化利器)
跑法: python3 04_module_hooks.py
"""
import torch
import torch.nn as nn

print("=" * 64)
print("一、自定义 Module: 所有模型的组织方式")
print("=" * 64)
class MLP(nn.Module):
    def __init__(self, in_dim, hid, out_dim):
        super().__init__()                      # 必须调用! 注册内部容器
        self.fc1 = nn.Linear(in_dim, hid)       # 赋值给 self -> 自动注册为子模块
        self.fc2 = nn.Linear(hid, out_dim)
        self.relu = nn.ReLU()
    def forward(self, x):                        # 定义前向 (建图)
        return self.fc2(self.relu(self.fc1(x)))

model = MLP(4, 8, 2)
print(f"  model = {model}")
print(f"  调用 model(x) 实际调用 model.__call__(x), 它内部再调 forward (还会触发 hooks)")

print("\n" + "=" * 64)
print("二、自动参数注册 (把 nn.Parameter 赋给 self 即自动跟踪)")
print("=" * 64)
print("  model.parameters():")
for i, p in enumerate(model.parameters()):
    print(f"    [{i}] shape={tuple(p.shape)}, requires_grad={p.requires_grad}")
print(f"  共 {sum(p.numel() for p in model.parameters())} 个参数")
print("  => optimizer(model.parameters()) 就能优化全部参数 (无需手动列清单)")

print("\n  model.named_parameters() (带名字):")
for name, p in model.named_parameters():
    print(f"    {name}: {tuple(p.shape)}")

print("\n" + "=" * 64)
print("三、子模块嵌套 (树形结构)")
print("=" * 64)
print("  model.children() (直接子模块):", [type(c).__name__ for c in model.children()])
print("  model.modules() (递归全部):", [type(m).__name__ for m in model.modules()])
print("  => 复杂模型(Transformer)就是 Module 树; 保存/迁移/冻结都基于这棵树")

print("\n" + "=" * 64)
print("四、state_dict: 保存/加载的本质")
print("=" * 64)
sd = model.state_dict()
print(f"  state_dict 的 keys: {list(sd.keys())}")
print(f"  含 linear 的 weight 和 bias (有序字典, tensor 值)")
# 保存/加载
x = torch.randn(2, 4); y1 = model(x)
torch.save(model.state_dict(), "/tmp/mdl.pt")
model2 = MLP(4, 8, 2); model2.load_state_dict(torch.load("/tmp/mdl.pt"))
y2 = model2(x)
print(f"  保存后加载到新模型, 输出一致: {torch.allclose(y1, y2)}")
print("  => 官方推荐: 保存 sd(load_state_dict), 不保存整个 model(pickle 易碎, 绑定代码)")

print("\n" + "=" * 64)
print("五、Hooks: 窥探与修改中间层 (调试/可视化/特征提取利器)")
print("=" * 64)
torch.manual_seed(0)
model = MLP(4, 8, 2)
# 前向 hook: 捕获某层输入输出
feats = {}
def hook(module, inp, out):
    feats['fc1_out'] = out.detach()
h = model.fc1.register_forward_hook(hook)
_ = model(torch.randn(3, 4))
print(f"  forward hook 捕获 fc1 输出 shape: {tuple(feats['fc1_out'].shape)}  (中间特征!)")
h.remove()   # 用完移除, 避免泄漏
print("  hook 类型:")
print("    register_forward_hook(module, inp, out)  - 看前向输出 (最常用, 取特征)")
print("    register_forward_pre_hook(module, inp)   - 改前向输入")
print("    register_full_backward_hook(module, grad_in, grad_out) - 看反向梯度")
print("  典型用途: 特征可视化/Grad-CAM/调试中间层/实现自定义正则")

print("\n核心洞察:")
print("  - nn.Module = 参数容器 + forward定义 + 树形组织 (所有模型的统一抽象)")
print("  - 参数自动注册: 赋值给 self 即被跟踪, optimizer 直接用 .parameters()")
print("  - state_dict 是保存/加载的标准接口 (只存张量, 与代码解耦)")
print("  - hooks 是不用改 forward 就能窥探/改中间层的'后门'")
