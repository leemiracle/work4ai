"""
实验 05 —— 自定义 autograd.Function + torch.compile
对应文档: 04-性能与部署.md
核心:
  1. 自定义 autograd.Function: 当内置算子不够时, 手写前向+反向(衔接你的算子开发经验)
  2. torch.compile: PyTorch 2.x 的 JIT 编译, 把 Python 开销融化成 fused kernel
跑法: python3 05_custom_function_compile.py
"""
import torch
import torch.nn as nn
import time

print("=" * 66)
print("一、自定义 autograd.Function: 手写前向+反向")
print("=" * 66)

class LeakyReLUFunc(torch.autograd.Function):
    """手写 LeakyReLU 的前向和反向 (这就是 PyTorch 内置算子的写法)"""
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.save_for_backward(x)          # 缓存反向要用到的张量 (省内存)
        ctx.alpha = alpha
        return torch.where(x > 0, x, alpha * x)
    @staticmethod
    def backward(ctx, grad_out):
        (x,) = ctx.saved_tensors          # 取出前向缓存的
        grad_in = torch.where(x > 0, torch.ones_like(x), ctx.alpha * torch.ones_like(x))
        return grad_in * grad_out, None   # 返回 (对 x 的梯度, 对 alpha 的梯度(None=不求))

# 用法: Function.apply(输入...)
x = torch.tensor([-2.0, -0.5, 0.5, 2.0], requires_grad=True)
y = LeakyReLUFunc.apply(x, 0.1)
y.sum().backward()
print(f"  自定义 LeakyReLU(0.1): x={x.tolist()}")
print(f"  反向梯度: {x.grad.tolist()}  (x>0处=1, x<0处=0.1)")

# 对拍内置 leaky_relu
x2 = torch.tensor([-2.0, -0.5, 0.5, 2.0], requires_grad=True)
y2 = torch.nn.functional.leaky_relu(x2, 0.1); y2.sum().backward()
print(f"  内置 leaky_relu 梯度:   {x2.grad.tolist()}")
print(f"  完全一致: {torch.allclose(x.grad, x2.grad)}  ✓")
print("  => 当你写 CUDA 算子/ONNX EP 不支持的算子时, 就是用这个机制接入 autograd")
print("     ctx.save_for_backward(缓存) + forward + backward(链式), 与实验01手写版一一对应")

print("\n" + "=" * 66)
print("二、torch.compile: Python 模型 -> 编译后 fused kernel")
print("=" * 66)
torch.manual_seed(0)
model = nn.Sequential(nn.Linear(64,256), nn.ReLU(), nn.Linear(256,256),
                      nn.ReLU(), nn.Linear(256,10))
x = torch.randn(512, 64)

# Eager (普通模式)
def run(m): 
    with torch.no_grad(): 
        for _ in range(30): m(x)
run(model)  # warmup
t0=time.time(); run(model); t_eager=time.time()-t0

# 编译模式 (首次调用触发编译, 有编译开销)
print("  编译中(首次有一次性开销)...")
compiled = torch.compile(model, mode="reduce-overhead")
try:
    run(compiled)  # 触发编译 (warmup)
    t0=time.time(); run(compiled); t_compiled=time.time()-t0
    print(f"  Eager:    {t_eager*1000:7.1f} ms (30 次推理)")
    print(f"  Compiled: {t_compiled*1000:7.1f} ms (30 次推理)")
    print(f"  加速比: {t_eager/t_compiled:.2f}x")
    # 数值一致
    with torch.no_grad():
        diff = (model(x) - compiled(x)).abs().max().item()
    print(f"  编译前后输出最大差: {diff:.2e} (应极小)")
    print("  compile 模式: reduce-overhead(减 Python 开销) / default(max-autogen)")
    print("  => GPU+大模型收益巨大(算子融合); CPU+小模型收益有限甚至首次更慢(编译开销)")
except Exception as e:
    print(f"  本环境 compile 未生效: {type(e).__name__} (CPU/版本限制, 正常)")

print("\n核心洞察:")
print("  - 自定义 Function = 接入 autograd 的标准方式 (写自定义算子/CUDA kernel 必经)")
print("  - torch.compile = PyTorch 2.x 的核心提速 (Dynamo 抓图 + Inductor 生成 fused kernel)")
print("  - 两者的收益都在 GPU + 大模型上才显著; 但原理值得现在就懂")
