"""
实验 12 —— 现代分布式与高级特性概览 (FlexAttention/DTensor/FSDP2/TP/torchao)
对应文档: 08-现代PyTorch(2.x特性).md
诚实声明: 本环境为单 CPU + 无 GPU, 这些特性多数需要 GPU 或多机分布式才能真跑.
          本实验做'API 可达性验证 + 原理讲解', 让你知道它们是什么、何时用、怎么入门.
跑法: python3 12_modern_overview.py
"""
import torch

print("=" * 68)
print("一、FlexAttention (2.5 prototype): 几行代码定义任意 attention")
print("=" * 68)
try:
    from torch.nn.attention.flex_attention import flex_attention, create_block_mask
    print("  ✓ flex_attention 可 import (运行需 torch.compile + GPU)")
    print("  原理: 你用普通 PyTorch 写一个 score_modify 函数(如 sliding/causal/prefix),")
    print("        FlexAttention 经 compile 自动生成 fused FlashAttention kernel.")
    print("  价值: 不用手写 Triton/CUDA attention kernel, 就能高效实现各种 attention 变体")
    print("        (文档/长序列模型的 sliding window、prefix-LM 的复合 mask 等)")
    print("  对比 SDPA: SDPA 内置几种固定 mask; FlexAttention 任意可编程(稀疏 mask 还加速)")
except Exception as e:
    print(f"  import 受限: {type(e).__name__}")

print("\n" + "=" * 68)
print("二、DTensor (分布式张量抽象, 2.5 namespace 稳定)")
print("=" * 68)
try:
    from torch.distributed.tensor import DTensor
    from torch.distributed.device_mesh import DeviceMesh
    from torch.distributed.tensor.placement_types import Replicate, Shard
    print("  ✓ DTensor / DeviceMesh / placement 可 import")
    print("  核心思想: DTensor = 本地 tensor + placements(描述如何分布在设备网格上)")
    print("    placements 三种: Replicate(复制) / Shard(dim)(按维度切分) / Partial(待规约)")
    print("    DeviceMesh: 设备的逻辑网格(如 2D: data_parallel × tensor_parallel)")
    print("  价值: 用 DTensor 写代码, 它自动处理 all-gather/all-reduce 等集合通信")
    print("        上层(FSDP2/TP)都建立在 DTensor 上, 分布式编程从'手写通信'变'声明 placement'")
    print("  注: 真正运行需 init_process_group 多进程; 单进程只能理解抽象")
except Exception as e:
    print(f"  import 受限: {type(e).__name__}")

print("\n" + "=" * 68)
print("三、FSDP2 (fully_shard, 2.5+) 与 张量并行 TP (2.3+)")
print("=" * 68)
print("  FSDP2 (torch.distributed.fsdp.fully_shard):")
print("    基于 DTensor 重写的全新 FSDP, 取代 FSDP1 (FullyShardedDataParallel)")
print("    更易组合(可对任意子模块 shard)、更易调试、原生支持 HSDP(混合分片)")
print("    用法: fully_shard(module) 一行把模块参数按 DTensor 分片到各 GPU")
print("  Tensor Parallelism (TP, torch.distributed.tensor.parallel):")
print("    把单层(如 Linear/attention)的权重切到多 GPU 并行算(Megatron 风格)")
print("    FSDP=切不同层到不同数据; TP=切同一层到不同 GPU. LLM 训练常 FSDP+TP 组合")
print("  何时用: 单卡放不下大模型 -> FSDP; 单层算太慢/太大 -> TP; 通常组合使用")

print("\n" + "=" * 68)
print("四、torchao: PyTorch 原生量化/优化库 (现代量化, 取代老 torch.quantization)")
print("=" * 68)
try:
    import torchao
    print(f"  ✓ torchao 已安装: {torchao.__version__}")
except Exception:
    print("  torchao 未安装 (pip install torchao; 是独立库, 非 torch 内置)")
print("  老方案 torch.quantization (实验10): PTQ/QAT, 偏经典 CV (XNNPACK/int8)")
print("  新方案 torchao:")
print("    - 低比特量化: int4_weight_only / int8_weight_only (LLM 推理主力)")
print("    - MXFP (微缩浮点, 8bit/4bit 浮点): 比 int 精度更好, H100+ 原生支持")
print("    - 与 torch.compile/export 深度集成, 自动生成量化 kernel")
print("  对比: torch.quantization=经典CV端侧; torchao=LLM/GPU 现代量化 (衔接'讲透激活函数04章')")

print("\n" + "=" * 68)
print("五、其他重要现代特性速览")
print("=" * 68)
features = [
    ("Compiled Autograd (2.5 prototype)", "把反向传播也编译, 训练加速(不只前向)"),
    ("Triton kernels in compile (2.3)", "用户可用 Triton 写自定义 GPU 算子并融入 compile"),
    ("CUDA Graphs 集成", "compile 可捕获成 CUDA Graph, 消除 kernel launch 开销"),
    ("regional compile (2.5)", "重复模块(如 Transformer 层)只编译一次, 减冷启动"),
    ("torch.distributed.checkpoint (2.1)", "分布式训练断点保存/恢复, 支持拓扑变化 reshard"),
    ("ExecuTorch", "端侧部署(手机/嵌入式), 取代老的 torch.mobile"),
    ("DebugMode + tlparse (2.10)", "数值发散调试, 定位'两个模型为何结果不同'"),
    ("combo-kernels (2.10)", "水平融合: 无依赖的并行算子合成单 kernel, 减 launch 开销"),
]
for name, desc in features:
    print(f"  • {name}")
    print(f"      {desc}")

print("\n" + "=" * 68)
print("六、2.x 版本演进时间线 (基于官方 release blog 核实)")
print("=" * 68)
timeline = [
    ("2.0 (2023.3)", "torch.compile(Dynamo+Inductor+Triton), SDPA 稳定 — 2.x 起点"),
    ("2.1 (2023.10)", "torch.export prototype, 动态形状, distributed.checkpoint"),
    ("2.3 (2024.4)", "Triton kernels in compile, TP, AOTInductor, export dynamic_shapes"),
    ("2.5 (2024.10)", "FlexAttention, cuDNN SDPA, FSDP2(fully_shard), DTensor 稳定, Compiled Autograd"),
    ("2.10 (2026.1)", "TorchScript 废弃(→torch.export), varlen_attn, DebugMode, combo-kernels"),
]
for v, d in timeline:
    print(f"  {v}: {d}")

print("\n核心洞察: PyTorch 2.x 的主线 = 编译化(compile/export/AOTInductor) + 分布式原生(DTensor/FSDP2/TP)")
print("  老范式(TorchScript/手写分布式)在退场, 新范式(export + DTensor)是现代 PyTorch 的必修课")
