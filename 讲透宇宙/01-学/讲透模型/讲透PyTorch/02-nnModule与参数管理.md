# 02 · nn.Module 与参数管理

> 所有模型（从 `nn.Linear` 到 Transformer）都是 `nn.Module` 的组织。搞懂它，你就搞懂了 PyTorch 模型的"组织学"：参数怎么注册、子模块怎么嵌套、怎么保存加载、怎么窥探中间层。

---

## 一、自定义 Module

```python
class MLP(nn.Module):
    def __init__(self, in_dim, hid, out_dim):
        super().__init__()                  # 必须调! 注册内部容器
        self.fc1 = nn.Linear(in_dim, hid)   # 赋给 self -> 自动注册为子模块
        self.fc2 = nn.Linear(hid, out_dim)
    def forward(self, x):                    # 定义前向
        return self.fc2(torch.relu(self.fc1(x)))

model = MLP(4, 8, 2)
model(x)   # 实际调 model.__call__(x), 内部再调 forward (还会触发 hooks)
```

---

## 二、自动参数注册

把 `nn.Parameter` 或子 `nn.Module` 赋给 `self`，PyTorch **自动跟踪**：

```python
for p in model.parameters():       # 自动列出所有参数
    ...
optimizer = Adam(model.parameters(), lr=1e-3)   # 一行优化全部
```

> 不需要手动列参数清单。这是 Module 的核心便利。

---

## 三、子模块嵌套（树形）

```python
list(model.children())   # 直接子模块
list(model.modules())    # 递归全部模块
```

复杂模型（Transformer）就是 Module 树。保存/迁移/冻结都基于这棵树。

---

## 四、state_dict：保存/加载的本质

```python
sd = model.state_dict()                    # 有序字典: {名字: tensor}
torch.save(sd, "model.pt")
model2 = MLP(4,8,2)
model2.load_state_dict(torch.load("model.pt"))   # 加载
```

> **官方推荐**：保存 `state_dict`（只存张量，与代码解耦），不要 `torch.save(model)`（pickle 绑定代码，易碎）。

---

## 五、Hooks：窥探/改中间层的后门（调试利器）

不改 `forward` 就能看/改中间层输出：

```python
feats = {}
def hook(module, inp, out):
    feats['fc1'] = out.detach()
h = model.fc1.register_forward_hook(hook)
model(x)                  # 触发, feats['fc1'] 拿到 fc1 输出
h.remove()                # 用完移除
```

三种 hook：
- `register_forward_hook`（看前向输出，最常用，取特征）
- `register_forward_pre_hook`（改前向输入）
- `register_full_backward_hook`（看反向梯度）

用途：特征可视化、Grad-CAM、调试中间层、自定义正则。

---

## 六、批判性视角

- **`forward` 别直接调**：用 `model(x)`（`__call__` 会触发 hooks 和预处理）；直接 `model.forward(x)` 跳过 hooks。
- **buffers vs parameters**：BatchNorm 的 running_mean 是 buffer（不是 parameter，不优化但要保存），`state_dict` 都含。
- **冻结参数**：`param.requires_grad_(False)` 或 `with torch.no_grad()`，配合 optimizer 只传需要训练的参数。

---

## 📌 下一步

- 跑 `experiments/04_module_hooks.py`（参数/子模块/state_dict/hooks 全透视）。
- 模型有了 → [03-训练循环](03-训练循环.md) 让它学起来。

## 🔬 深度阅读（nn.Module 与算子的内核）
- **Kieran Didi "How does PyTorch implement a linear layer?"** — 从源码追踪 `nn.Linear` → `addmm` 的完整路径（dispatcher → native_functions.yaml → codegen → structured kernels）。**想读 PyTorch 源码，从这篇开始。**
- **ezyang "A brief taxonomy of PyTorch operators by shape behavior"** — 理解算子分类，对看懂 Module 内部有帮助。
- **PyTorch Developer Podcast** — 有专门讲 nn.Module / 参数注册的单集。

## ✍️ 练习

1. 为何 `__init__` 必须调 `super().__init__()`？不调会怎样？
2. `torch.save(model)` vs `torch.save(model.state_dict())`，为何推荐后者？
3. hooks 为何用完要 `remove()`？
4. BatchNorm 的 `running_mean` 是 parameter 还是 buffer？为什么？
