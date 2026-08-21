"""
实验 05 —— 量化误差的两个真正来源 (舍入误差 + 离群点)
对应文档: 04-量化中的激活函数.md
核心结论:
  1. 激活函数变体(GELU查表/Leaky下溢)不是量化误差"主要来源", 而是"误差放大器"
  2. 真正主要来源: (a) 舍入误差/离散化; (b) 离群点拉大 scale 导致正常值 underflow
  3. 演示 Leaky ReLU 负半轴在统一 scale 下退化成 ReLU
跑法: python3 05_quantization_demo.py
"""
import torch
import torch.nn.functional as F

# ---------------------------------------------------------------
# 工具: 对称 INT8 量化 / 反量化
# ---------------------------------------------------------------
def quantize_symmetric(x, n_bits=8):
    qmax = 2 ** (n_bits - 1) - 1          # INT8: 127
    scale = x.abs().max() / qmax           # 由最大绝对值决定 scale
    x_q = torch.round(x / scale).clamp(-qmax, qmax).to(torch.int8)
    return x_q, scale

def dequantize(x_q, scale):
    return x_q.to(torch.float32) * scale

torch.manual_seed(0)

# ---------------------------------------------------------------
# 来源1: 舍入误差 (纯离散化信息丢失)
# ---------------------------------------------------------------
print("=" * 64)
print("来源1: 舍入误差 (连续->离散的不可逆信息丢失)")
print("=" * 64)
x_normal = torch.randn(1000)              # N(0,1) 分布的正常激活值
xq, s = quantize_symmetric(x_normal)
xd = dequantize(xq, s)
err = (x_normal - xd).abs().mean()
print(f"1000 个 N(0,1) 样本, INT8 对称量化后")
print(f"  平均绝对量化误差 = {err.item():.6f}")
print(f"  相对原始标准差比 = {err.item()/x_normal.std().item():.4%}")
print("  -> 即使没有任何激活函数, 光量化本身就丢了信息\n")

# ---------------------------------------------------------------
# 来源2: 离群点 (拉大 scale -> 正常值 underflow 成 0)
# ---------------------------------------------------------------
print("=" * 64)
print("来源2: 离群点拉大 scale (Transformer 量化的头号杀手)")
print("=" * 64)
x_with_outlier = torch.randn(1000)
x_with_outlier[5] = 100.0                 # 1 个离群点!
xq2, s2 = quantize_symmetric(x_with_outlier)
xd2 = dequantize(xq2, s2)
zero_count = (xq2 == 0).sum().item()
print(f"1000 个样本里塞入 1 个 =100 的离群点")
print(f"  无离群点时 scale = {s.item():.6f}")
print(f"  有离群点时 scale = {s2.item():.6f}  (被放大 ~100 倍!)")
print(f"  有离群点后, 量化为 0 的元素数 = {zero_count}/1000  (正常值大批 underflow)")
print("  -> 这就是 SmoothQuant/AWQ/GPTQ 要专门处理离群点的原因\n")

# ---------------------------------------------------------------
# 激活函数的角色: 误差放大器 (不是源头)
# ---------------------------------------------------------------
print("=" * 64)
print("激活函数变体: 误差放大器 + 逻辑断裂 (Leaky->ReLU 退化)")
print("=" * 64)

# 演示 Leaky ReLU 负半轴在统一 scale 下退化成 ReLU
# 真实痛点: 激活存在离群点 -> scale 被拉大 -> Leaky 的微小负斜率值(αx)下溢成 0
torch.manual_seed(1)
act = torch.randn(2000)                    # 模拟一层激活值
act[10], act[100], act[500] = 70.0, -65.0, 80.0   # 几个离群点 (LLM 常见)

y_leaky_float = F.leaky_relu(act, 0.01)    # 浮点 LeakyReLU, 负值 = 0.01*x
neg_float = (y_leaky_float < 0).sum().item()

# 统一 scale 量化这层激活的输出
yq, sy = quantize_symmetric(y_leaky_float)
y_deq = dequantize(yq, sy)
neg_quant = (y_deq < 0).sum().item()

print(f"LeakyReLU (α=0.01), 输入含离群点 (scale 被拉大到 {sy.item():.4f}):")
print(f"  浮点结果中 <0 的点数: {neg_float}/2000  (负半轴保留微小负值, 防死神经元)")
print(f"  INT8 统一scale后 <0 的点数: {neg_quant}/2000  (微小负值四舍五入成 0!)")
print(f"  负信息存活率: {neg_float}-> {neg_quant} ({neg_quant/max(neg_float,1)*100:.1f}%)")
print(f"  ==> 离群点拉大 scale 后, LeakyReLU 在负半轴事实性退化为普通 ReLU, 丧失设计初衷!")
print()
print("总结论:")
print("  量化误差的'原罪' = 舍入截断 + 离群点 (都在激活函数之前就已发生)")
print("  复杂激活函数 = 误差放大器 (非线性扭曲) + 逻辑断裂发生器")
