"""
实验 06 —— SwiGLU: 朴素实现 vs 权重拼接融合实现
对应文档: 06-SwiGLU底层Kernel.md
核心结论:
  1. SwiGLU(X) = Swish(XW_gate) ⊙ (XW_up), 是门控线性单元 (取代整个 FFN 的激活)
  2. 朴素: 两次独立 GEMM, 中间结果写回 HBM (显存带宽灾难)
  3. 融合: 把 [W_gate, W_up] 拼接 -> 单次 GEMM -> epilogue 里 swish+乘法 (省 HBM 读写)
  4. 两者数值结果在数学上完全等价 (本实验验证), 差别只在底层访存效率
跑法: python3 06_swiglu_fusion.py
"""
import torch
import torch.nn.functional as F
import time

torch.manual_seed(0)

# 假设 LLM 维度: hidden=1024, intermediate=4096, batch=64
B, H, I = 64, 1024, 4096
X = torch.randn(B, H)
W_gate = torch.randn(H, I)
W_up = torch.randn(H, I)

def swish(t):
    return t * torch.sigmoid(t)

# ---------------------------------------------------------------
# 朴素实现: 两次独立 GEMM + 中间写回 + 逐元素乘
# ---------------------------------------------------------------
def swiglu_naive(X, W_gate, W_up):
    H1 = X @ W_gate          # GEMM1 -> 写回 HBM
    H2 = X @ W_up            # GEMM2 -> 写回 HBM (X 又被读一次!)
    S = swish(H1)            # 读 H1, 算 swish -> 写回 HBM
    out = S * H2             # 读 S, 读 H2, 乘 -> 写回 HBM
    return out

# ---------------------------------------------------------------
# 融合实现: 权重拼接 -> 单次 GEMM -> epilogue(swish+乘)
# ---------------------------------------------------------------
def swiglu_fused(X, W_gate, W_up):
    # 预拼接权重 (推理时一次性完成, 之后复用)
    W_concat = torch.cat([W_gate, W_up], dim=1)   # [H, 2I]
    # 单次 GEMM: X 只从 HBM 读一次
    H12 = X @ W_concat                              # [B, 2I]
    H1, H2 = H12.chunk(2, dim=-1)                   # 在寄存器/共享内存里切分
    # epilogue: 直接对寄存器里的 H1 做 swish, 再与 H2 相乘 (不写回中间结果)
    out = swish(H1) * H2
    return out

out_naive = swiglu_naive(X, W_gate, W_up)
out_fused = swiglu_fused(X, W_gate, W_up)

print("=" * 64)
print("数值等价性验证")
print("=" * 64)
print(f"朴素输出 shape: {tuple(out_naive.shape)}")
print(f"融合输出 shape: {tuple(out_fused.shape)}")
print(f"两者最大绝对差: {(out_naive - out_fused).abs().max().item():.3e}")
print("==> 数学上完全等价 (差异仅为浮点误差)\n")

# ---------------------------------------------------------------
# 访存分析 (概念性): 统计朴素 vs 融合的中间张量 HBM 写/读次数
# ---------------------------------------------------------------
print("=" * 64)
print("访存分析 (中间张量 HBM 读写次数, 理论统计)")
print("=" * 64)
elem = 4  # float32 字节
def mb(t):
    return t.numel() * elem / 1e6

# 朴素: 3 个 [B,I] 中间张量各被写一次读一次 = 6 次穿越 HBM
mid = mb(out_naive)
print(f"朴素实现中间张量 HBM 流量:")
print(f"  H1={mid:.1f}MB(写) + H2={mid:.1f}MB(写) + S={mid:.1f}MB(写) + 读回 = ~{6*mid:.1f}MB 穿越总线")
print(f"  另外 X 被读了 2 次")
# 融合: 只写回最终 out (epilogue 内部在寄存器完成)
print(f"融合实现中间张量 HBM 流量:")
print(f"  仅写回最终 out = {mid:.1f}MB; H1/H2 切分与 swish 全在寄存器/共享内存完成")
print(f"  X 只被读 1 次")
print(f"  ==> 中间流量从 ~{6*mid:.1f}MB 降到 {mid:.1f}MB (理论 ~6x), 这就是 CUTLASS Epilogue 融合的意义\n")

# ---------------------------------------------------------------
# 实测耗时 (CPU 上 GEMM 不占优, 主要体现访存差别, 仅供方向性参考)
# ---------------------------------------------------------------
print("=" * 64)
print("实测耗时 (CPU, 方向性参考)")
print("=" * 64)
for fn, name in [(swiglu_naive, "朴素"), (swiglu_fused, "融合")]:
    # warmup
    for _ in range(3):
        fn(X, W_gate, W_up)
    t0 = time.perf_counter()
    for _ in range(50):
        fn(X, W_gate, W_up)
    dt = (time.perf_counter() - t0) / 50 * 1000
    print(f"  {name}: {dt:.3f} ms/次")
print("\n注: 真正的收益在 GPU 上 (GEMM 计算快, 访存成瓶颈); CPU 上 GEMM 本身就慢, 差距较小。")
print("    工业级收益来自: (1) X 只读一次; (2) 中间结果不落 HBM; (3) Tensor Core 饱和度更高。")
