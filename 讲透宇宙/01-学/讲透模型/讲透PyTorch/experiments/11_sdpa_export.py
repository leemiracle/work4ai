"""
实验 11 —— SDPA + torch.export + AOTInductor (现代 attention 与新导出范式)
对应文档: 08-现代PyTorch(2.x特性).md
这是 PyTorch 2.x 最重要的两个现代能力:
  1. SDPA (scaled_dot_product_attention, 2.0): FlashAttention 的官方封装, Transformer 必备
  2. torch.export (2.1+): 取代 TorchScript 的全图捕获(2.10 已废弃 TorchScript)
  3. AOTInductor: export 后 AOT 编译成 .so, 脱离 Python 部署(取代 TorchScript 部署)
跑法: python3 11_sdpa_export.py
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import time

print("=" * 68)
print("一、SDPA: scaled_dot_product_attention (2.0+, FlashAttention 封装)")
print("=" * 68)
# 手写 attention (教学用, 慢且费显存)
def attention_naive(q, k, v, mask=None):
    import math
    d = q.shape[-1]
    scores = q @ k.transpose(-2,-1) / math.sqrt(d)     # (.., n, n)
    if mask is not None: scores = scores.masked_fill(~mask, float('-inf'))
    attn = torch.softmax(scores, dim=-1)
    return attn @ v

torch.manual_seed(0)
B, H, N, D = 2, 4, 128, 64
q = torch.randn(B, H, N, D); k = v = q

out_naive = attention_naive(q, k, v)
# SDPA: 一行调用, 内部自动选 FlashAttention/memory-efficient 后端
out_sdpa = F.scaled_dot_product_attention(q, k, v)
print(f"  输入: q/k/v shape={tuple(q.shape)} (batch,heads,seq,dim)")
print(f"  手写 vs SDPA 最大差: {(out_naive-out_sdpa).abs().max().item():.2e} (数值一致)")
# SDPA 直接支持 causal mask (一行)
out_causal = F.scaled_dot_product_attention(q, k, v, is_causal=True)
print(f"  SDPA is_causal=True: 一行实现因果 mask (LLM 必备)")
print("  价值: SDPA 内部自动用 FlashAttention(GPU) 省显存+加速, 不用手写 softmax(QK^T)")
print("        手写版要先物化 N×N attention 矩阵(显存 O(N²)), SDPA/Flash 是 O(N)")

# 速度对比
def bench(fn, n=50):
    fn(); t0=time.time()
    for _ in range(n): fn()
    return (time.time()-t0)/n*1000
t_n = bench(lambda: attention_naive(q,k,v))
t_s = bench(lambda: F.scaled_dot_product_attention(q,k,v))
print(f"  速度: 手写={t_n:.2f}ms vs SDPA={t_s:.2f}ms (CPU差距小, GPU上SDPA快很多倍)")

print("\n" + "=" * 68)
print("二、torch.export: 全图捕获 (取代 TorchScript, 2.10 已废弃 TorchScript)")
print("=" * 68)
class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(8, 4)
    def forward(self, x):
        return F.relu(self.fc(x)).sum()
m = TinyModel().eval()
x = torch.randn(3, 8)

# 导出: 捕获成不依赖 Python 的计算图
ep = torch.export.export(m, (x,))
print(f"  export 返回: {type(ep).__name__}")
print(f"  捕获的图节点数: {len(ep.graph.nodes)}")
print(f"  graph 内容(前几行):\n    " + str(ep.graph).split('\n')[1:4].__str__()[:200])
# 运行 exported program
out_exported = ep.module()(x)
out_eager = m(x)
print(f"\n  eager vs exported 最大差: {(out_eager-out_exported).abs().max().item():.2e} (一致)")
print("  torch.export vs TorchScript 的区别:")
print("    TorchScript(torch.jit): 用 trace/script, 脆弱, 动态控制流难处理 -> 2.10 废弃")
print("    torch.export: 基于 PT2 编译栈, sound 的全图捕获, 支持 dynamic_shapes")
print("  动态形状:")
ep_dyn = torch.export.export(m, (x,), dynamic_shapes=({0: torch.export.Dim("b", min=1, max=64)},))
xb = torch.randn(20, 8)
print(f"    动态 batch 导出后, 跑 batch=20: out={ep_dyn.module()(xb).item():.4f}")

print("\n" + "=" * 68)
print("三、AOTInductor: export -> .so, 脱离 Python 部署")
print("=" * 68)
print("  流水线: torch.export(捕获图) → AOTInductor(编译成 .so) → 非 Python 环境加载推理")
print("  对比部署方案:")
print("    TorchScript (.pt):  老方案, 2.10 废弃")
print("    ONNX (.onnx):       跨框架, 但需 onnxruntime(实验06)")
print("    AOTInductor (.so):  PyTorch 原生, 2.x 主推, 编译优化+算子融合")
try:
    import os, tempfile
    so_path = os.path.join(tempfile.gettempdir(), "pt_aoti_model")   # 无扩展名, AOTInductor 自己加 .so
    # aot_compile: 把模型编译成可加载的 .so 包
    aot_so = torch._export.aot_compile(
        m, (x,),
        options={"aot_inductor.output_path": so_path},
    )
    print(f"\n  AOTInductor 编译成功: {so_path}.so (生成共享库)")
    if os.path.exists(so_path + ".so"):
        print(f"  .so 文件大小: {os.path.getsize(so_path + '.so')//1024} KB")
    try:
        # 用官方 API 加载 (脱离原模型 Python 定义)
        runner = torch._C._aoti.AOTIModelContainerRunner(so_path + ".so")
        print("  加载 AOTI runner 成功: 可脱离模型 Python 代码推理")
    except Exception as e2:
        print(f"  底层加载 API: {type(e2).__name__} (加载接口随版本变; 原理: 编译产物可独立部署)")
    print("  => '训练(PyTorch) -> export -> AOT编译 -> 部署(无需PyTorch Python)' 的新闭环")
    print("     相比 ONNX: 保留 PyTorch 语义/优化, 不依赖第三方 runtime; ONNX 则跨框架更通用")
except Exception as e:
    print(f"\n  本环境 AOTInductor 受限: {type(e).__name__}: {str(e)[:100]}")
    print("  原理仍成立: torch.export → AOTInductor 生成 .so → 裸加载推理(无 Python)")

print("\n核心洞察 (PyTorch 2.x 部署新范式):")
print("  SDPA(2.0)  -> Transformer attention 标配, 自动 FlashAttention")
print("  torch.export(2.1) -> 取代 TorchScript 的全图捕获(2.10 废弃 TorchScript)")
print("  AOTInductor(2.3+) -> export 后 AOT 编译成 .so, 原生部署(补/替 ONNX)")
print("  整条链: 训练 -> torch.export -> AOTInductor(.so) -> 部署  (PyTorch 原生闭环)")
