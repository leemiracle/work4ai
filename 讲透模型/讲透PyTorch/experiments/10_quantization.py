"""
实验 10 —— 量化概览: 用 torch.quantization 把 fp32 模型压成 int8
对应文档: 07-性能与部署.md
核心: 衔接你做过的 ONNX EP / 量化经验. torch.quantization 提供训练后量化(PTQ):
  - 动态量化: 只量化权重, 激活推理时动态量化 (最简单, 无需校准数据)
  - 静态量化: 权重+激活都量化, 需校准数据, 最快
  - 量化感知训练 QAT: 训练时模拟量化, 精度最高
本实验演示动态量化: 模型大小约 1/4, 精度损失极小.
跑法: python3 10_quantization.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

print("=" * 66)
print("一、为什么量化: fp32 -> int8 省 4 倍内存 + CPU 上加速")
print("=" * 66)
print("  fp32: 每参数 4 字节;  int8: 每参数 1 字节 (含 zero-point/scale)")
print("  收益: 内存1/4, 带宽1/4, CPU/GPU 整数算力通常更高")
print("  代价: 精度损失 (需校准或QAT弥补), 见'讲透激活函数04章'量化误差来源")
print("  三种方式:")
print("    动态PTQ: 权重int8, 激活fp32->推理时动态转 (简单, 无需数据)")
print("    静态PTQ: 权重+激活都int8 (需校准数据, 最快)")
print("    QAT: 训练时模拟量化 (精度最高, 需重训)")

print("\n" + "=" * 66)
print("二、动态量化实操 (一行代码)")
print("=" * 66)
model = nn.Sequential(nn.Linear(64,256), nn.ReLU(), nn.Linear(256,64),
                      nn.ReLU(), nn.Linear(64,10))
# 动态量化: 把所有 Linear 的权重转 int8
qmodel = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)

def model_size(m):
    """估算参数占用字节数"""
    return sum(p.numel() * (1 if p.dtype in (torch.qint8, torch.int8) else
                            2 if p.dtype in (torch.float16, torch.bfloat16) else 4)
               for p in m.parameters() if hasattr(p,'dtype'))

# 用 state_dict 量真实大小
import io
def sd_bytes(m):
    buf = io.BytesIO(); torch.save(m.state_dict(), buf); return buf.tell()

print(f"  原始 fp32 模型: {sd_bytes(model)/1024:.1f} KB")
print(f"  动态量化 int8:  {sd_bytes(qmodel)/1024:.1f} KB")
print(f"  压缩比: {sd_bytes(model)/sd_bytes(qmodel):.2f}x")

print("\n" + "=" * 66)
print("三、精度对比 (量化前后输出应几乎一致)")
print("=" * 66)
x = torch.randn(8, 64)
with torch.no_grad():
    out_fp32 = model(x)
    out_int8 = qmodel(x)
diff = (out_fp32 - out_int8).abs().max().item()
print(f"  fp32 vs int8 输出最大差: {diff:.4e}")
print(f"  相对误差: {diff/out_fp32.abs().mean().item():.2%}")
print("  => 动态量化精度损失极小 (激活仍是fp32), 适合快速部署")

print("\n" + "=" * 66)
print("四、速度对比 (CPU 上 int8 通常更快)")
print("=" * 66)
import time
def bench(m, x, n=200):
    with torch.no_grad():
        m(x)
        t0=time.time()
        for _ in range(n): m(x)
        return (time.time()-t0)/n*1000
t_fp = bench(model, x)
t_q = bench(qmodel, x)
print(f"  fp32: {t_fp:.3f} ms/次")
print(f"  int8: {t_q:.3f} ms/次")
print(f"  加速: {t_fp/max(t_q,1e-9):.2f}x")
if t_q >= t_fp:
    print("  ⚠ 小模型+动态量化可能更慢: 权重虽int8但激活是fp32, 每次要dequant反量化,")
    print("    这个cast开销 > int8计算收益. 大模型/静态量化(激活也int8)/QAT 才真正加速。")
    print("    (和 compile 在 CPU 小模型上负收益同理: 优化收益强依赖规模/硬件)")
else:
    print("  int8 加速生效 (CPU 有 int8 矩阵乘优化)")

print("\n" + "=" * 66)
print("五、量化与 ONNX 的衔接 (你的主场)")
print("=" * 66)
print("  torch.onnx.export(qmodel, ...) 可导出量化 ONNX (含 QuantizeLinear/DequantizeLinear 节点)")
print("  ONNX Runtime 的 QLinearConv 等算子能高效执行 (见'讲透激活函数04章')")
print("  对比: torch.quantization (训练侧) -> ONNX (部署侧) -> ORT EP (执行侧)")
print("  这正是你做 Execution Provider 时打通的那条链")

print("\n核心洞察:")
print("  - 量化 = fp32→int8, 省4倍内存, CPU/端侧加速, 精度损失可控")
print("  - 动态PTQ最简单(无数据), 静态PTQ最快(需校准), QAT最准(需重训)")
print("  - 与 ONNX/ORT 链路打通, 是训练→部署完整闭环的关键一环")
