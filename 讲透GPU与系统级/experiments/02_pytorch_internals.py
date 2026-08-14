"""
讲透 PyTorch 内部 —— autograd / SDPA 后端 / torch.compile
============================================================
4 个实验, 揭开 PyTorch 的黑盒 (纯 CPU 可验证):
  实验1: autograd 怎么建反向图 (前向记录 grad_fn, 反向拓扑排序)
  实验2: 手写 autograd (numpy, 验证链式法则 = PyTorch 干的事)
  实验3: SDPA 怎么选后端 (Flash / mem-efficient / math)
  实验4: torch.compile 做了什么 (算子融合 fusion)

核心洞察: PyTorch 不是一个"黑盒", 而是【自动微分 + 动态调度 + 算子融合】的工程系统。
跑法: python3 02_pytorch_internals.py
"""
import torch
import torch.nn.functional as F
import numpy as np
import warnings
warnings.filterwarnings("ignore")

torch.manual_seed(0)

# ============================================================
# 实验 1: autograd 反向图 —— 前向记录, 反向走图
# ============================================================
print("=" * 72)
print("实验 1: autograd 反向图 —— PyTorch 怎么自动求导")
print("=" * 72)
print("""
autograd 原理:
  前向时: 每个算子生成一个 backward 节点, 挂在输出的 grad_fn 上 → 形成 DAG
  反向时: 从 loss 出发, 按拓扑序逆向遍历, 每个节点用【链式法则】算梯度
  本质: 你写的是前向, PyTorch 自动帮你构造反向图 (define-by-run)
""")

x = torch.randn(4, requires_grad=True)
y = x * 2              # MulBackward
z = y.sum()            # SumBackward
w = z * z + 1          # MulBackward + AddBackward
print("计算: x → y=2x → z=sum(y) → w=z²+1")
print(f"  x.grad_fn = {x.grad_fn}  (叶子, 无)")
print(f"  y.grad_fn = {y.grad_fn}  (MulBackward0)")
print(f"  z.grad_fn = {z.grad_fn}  (SumBackward0)")
print(f"  w.grad_fn = {w.grad_fn}  (AddBackward0, 组合节点)")
print(f"  w.grad_fn.next_functions = {w.grad_fn.next_functions[0][0]}  (链到 MulBackward)")
print("  ==> 前向时每个 op 生成 backward 节点, 串成 DAG\n")

w.backward()
print(f"反向后 x.grad = {x.grad}")
print(f"  手算: dw/dx = dw/dz · dz/dy · dy/dx = 2z · 1 · 2 = 2·{z.item():.3f}·2 = {2*z.item()*2:.3f}")
print(f"  (autograd 自动做了链式法则!)\n")


# ============================================================
# 实验 2: 手写 autograd (numpy, 验证链式法则)
# ============================================================
print("=" * 72)
print("实验 2: 手写 autograd —— 用 numpy 复刻 PyTorch 干的事")
print("=" * 72)

class Tensor:
    """极简 autograd: 记录前向 op, 反向时走链式法则"""
    def __init__(self, data, _children=(), _op=""):
        self.data = np.array(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._backward = lambda: None      # 反向函数 (闭包)
        self._prev = set(_children)
        self._op = _op

    def __add__(self, other):
        out = Tensor(self.data + other.data, (self, other), "+")
        def _backward():
            self.grad += out.grad           # 加法的梯度: 直通
            other.grad += out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        out = Tensor(self.data * other.data, (self, other), "*")
        def _backward():
            self.grad += other.data * out.grad   # 乘法: d(a*b)/da = b
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def relu(self):
        out = Tensor(np.maximum(0, self.data), (self,), "relu")
        def _backward():
            self.grad += (self.data > 0) * out.grad   # relu: x>0 时梯度直通
        out._backward = _backward
        return out

    def backward(self):
        """拓扑排序 + 逆向遍历 (就是 PyTorch 做的!)"""
        topo = []
        visited = set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev: build(child)
                topo.append(v)
        build(self)
        self.grad = 1.0                       # loss 对自己梯度=1
        for v in reversed(topo):              # 逆拓扑序
            v._backward()

# 复刻实验1的计算: w = (relu(x1)*x2 + x1)^2 的简化版
x1 = Tensor([2.0, -1.0])
x2 = Tensor([3.0, 4.0])
a = x1.relu()           # [2, 0]
b = a * x2              # [6, 0]
c = b + x1             # [8, -1]
loss = c * c            # [64, 1]
loss.backward()
print("手写 autograd: w = (relu(x1)*x2 + x1)²")
print(f"  x1.data = {x1.data}, x1.grad = {x1.grad}")
print(f"  x2.data = {x2.data}, x2.grad = {x2.grad}")

# 用 PyTorch 对照
x1_t = torch.tensor([2.0, -1.0], requires_grad=True)
x2_t = torch.tensor([3.0, 4.0], requires_grad=True)
loss_t = (torch.relu(x1_t) * x2_t + x1_t) ** 2
loss_t.sum().backward()
print(f"  PyTorch:  x1.grad = {x1_t.grad.numpy()}, x2.grad = {x2_t.grad.numpy()}")
print(f"  ==> 手写 autograd 与 PyTorch 完全一致! 这就是 define-by-run 的本质\n")


# ============================================================
# 实验 3: SDPA 怎么选后端
# ============================================================
print("=" * 72)
print("实验 3: scaled_dot_product_attention 的多后端")
print("=" * 72)
print("""
F.scaled_dot_product_attention (SDPA) 是个【调度器】, 不是单一实现:
  - FlashAttention 后端: 最快 (有 GPU 时), 用 tiling (01 篇)
  - memory-efficient 后端: 省显存的备选
  - math 后端: 纯朴素实现 (最慢, 但最兼容), CPU 上的 fallback
PyTorch 根据输入 (dtype/device/causal/形状) 自动选最优后端。
""")

q = torch.randn(2, 4, 16, 32)   # batch, heads, seq, dim
k = torch.randn(2, 4, 16, 32)
v = torch.randn(2, 4, 16, 32)

# 看选了哪个后端 (CPU 上通常是 math)
for impl in ["auto", "flash_attention", "mem_efficient", "math", "cudnn_attention"]:
    try:
        with torch.nn.attention.sdpa_kernel([getattr(torch.nn.attention.SDPBackend, impl.upper())] if impl != "auto" else None):
            out = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        print(f"  后端 {impl:18s}: ✓ 可用, 输出 shape={tuple(out.shape)}")
    except Exception as e:
        print(f"  后端 {impl:18s}: ✗ 不可用 ({str(e)[:40]})")

print("  ==> CPU 上 fallback 到 math 后端; 有 GPU 时自动用 Flash。")
print("      这就是为什么 mini-GPT 用 SDPA 而非手写 softmax(QK^T)V (01 篇)\n")


# ============================================================
# 实验 4: torch.compile 的算子融合
# ============================================================
print("=" * 72)
print("实验 4: torch.compile —— 把多个小算子融合成一个大 kernel")
print("=" * 72)
print("""
torch.compile (PyTorch 2.0+) 做两件事:
  1. 图捕获: 把 Python 的动态执行 trace 成静态计算图
  2. 算子融合 (fusion): 把多个逐元素算子合并成 1 个 kernel, 减少 HBM 读写
     例: y = relu(x * 2 + 1)  朴素要 3 次读写; 融合后 1 次
""")

def f(x):
    return torch.relu(x * 2 + 1).sum()

x = torch.randn(1000, requires_grad=True)

# eager (朴素)
x_eager = x.clone().requires_grad_(True)
import time
t = time.time()
for _ in range(100): f(x_eager)
t_eager = time.time() - t

# compiled (融合)
try:
    f_compiled = torch.compile(f, mode="reduce-overhead")
    f_compiled(x.clone().requires_grad_(True))  # warmup (编译)
    t = time.time()
    for _ in range(100): f_compiled(x.clone().requires_grad_(True))
    t_compiled = time.time() - t
    print(f"  eager (朴素):    {t_eager*1000:.1f} ms / 100 次")
    print(f"  compiled (融合): {t_compiled*1000:.1f} ms / 100 次")
    print(f"  加速: {t_eager/t_compiled:.2f}× (CPU 上加速有限; GPU 上可达 2-5×, 因融合省 HBM 读写)")
except Exception as e:
    print(f"  (compile 在此环境受限: {str(e)[:50]})")
    print(f"  eager: {t_eager*1000:.1f} ms (compile 跳过)")

print("""
  融合的本质 (连接 01 篇):
    朴素: x → 读HBM → ×2 → 写HBM → 读HBM → +1 → 写HBM → 读HBM → relu → 写HBM  (6次HBM)
    融合: x → 读HBM → [×2,+1,relu 在寄存器里一次完成] → 写HBM  (2次HBM)
    和 FlashAttention 同理: 减少 HBM 读写次数 = 加速。
""")

print("=" * 72)
print("全部 4 个实验完成!")
print("核心: PyTorch = define-by-run autograd + 多后端调度 + 算子融合")
print("      所有优化都指向同一个目标: 减少 HBM 读写 (01 篇的主旋律)")
print("=" * 72)
