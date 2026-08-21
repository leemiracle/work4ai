"""
实验 00 —— Tensor 基础: 它不只是 numpy, 是"会记梯度、能上 GPU"的数组
对应文档: 00-Tensor基础.md
核心点: 1)创建/dtype/device  2)视图(view/reshape)共享内存的本质  3)广播规则与坑
跑法: python3 00_tensor_basics.py
"""
import torch
import numpy as np

print("=" * 64)
print("一、创建与基本属性")
print("=" * 64)
a = torch.tensor([[1., 2.], [3., 4.]])
print(f"a = \n{a}")
print(f"  shape={tuple(a.shape)}, dtype={a.dtype}, device={a.device}, ndim={a.ndim}")
print(f"  (默认 float32, 这是深度学习标准精度; float64 太慢, float16 在 GPU 上用)")

print("\n常见创建方式:")
print(f"  zeros(2,3):\n{torch.zeros(2,3)}")
print(f"  randn(2,2) (标准正态):\n{torch.randn(2,2)}")
print(f"  arange(0,10,2): {torch.arange(0,10,2).tolist()}")

# 与 numpy 互转 (共享内存!)
n = np.array([1.,2.,3.])
t = torch.from_numpy(n)
t[0] = 99
print(f"\n  from_numpy 共享内存: 改 tensor, numpy 也变 -> numpy[0]={n[0]} (重要陷阱!)")

print("\n" + "=" * 64)
print("二、视图(view/reshape): 共享内存的本质 (新手最大坑!)")
print("=" * 64)
x = torch.arange(12.); print(f"  原始 x = {x.tolist()}")
y = x.view(3, 4)        # view 共享内存 (要求 contiguous)
z = x.reshape(2, 6)     # reshape 尽量共享, 必要时拷贝
print(f"  x.view(3,4) =\n{y}")
y[0,0] = 999
print(f"  实测: 改 y[0,0]=999 后, x[0]={x[0].item()}  <- 共享内存! 改视图影响原数据")
print("  => view/reshape 不是拷贝, 是同一块内存的'另一种看法' (省内存的关键)")
print("  => 想要独立拷贝必须 .clone()")

print("\n" + "=" * 64)
print("三、广播(Broadcasting): 形状不同也能运算")
print("=" * 64)
A = torch.ones(3, 4)
b = torch.tensor([10., 20., 30., 40.])   # shape (4,)
print(f"  A(3,4) + b(4,) =\n{A + b}")
print(f"  规则: 从右对齐, 维度为1或相等的轴可广播. b 被复制3次加到每行")
# 经典坑
row = torch.ones(3, 1)
col = torch.ones(1, 4)
print(f"\n  经典坑: row(3,1) + col(1,4) = {(row+col).shape} 结果")
print(f"{row + col}")
print("  => 本意可能不同, 但广播让 (3,1)+(1,4) 得到 (3,4). 调试形状错误先查广播")

print("\n" + "=" * 64)
print("四、dtype 与精度 (影响内存与速度)")
print("=" * 64)
for dt in [torch.float32, torch.float16, torch.float64, torch.int8]:
    t = torch.zeros(1000, dtype=dt)
    print(f"  {str(dt):30s} 单元素 {t.element_size()} 字节, 1000个={t.element_size()*1000}B")
print("  => float32 是默认; float16/bfloat16 省一半内存且加速(GPU); int8 用于量化")

print("\n" + "=" * 64)
print("五、设备(device): CPU vs GPU")
print("=" * 64)
print(f"  当前 device: {x.device}")
print(f"  CUDA 可用: {torch.cuda.is_available()}")
print("  迁移: tensor.to('cuda') / .cuda() / .to(device)")
print("  铁律: 参与运算的 tensor 必须在同一设备, 否则报错 (跨设备操作禁止)")

print("\n核心洞察: Tensor = numpy + (梯度跟踪) + (GPU) + (autograd集成)")
print("  学会 view(共享内存) 和广播规则, 能避开 80% 的形状/内存 bug")
