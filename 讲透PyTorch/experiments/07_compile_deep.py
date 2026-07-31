"""
实验 07 —— ★torch.compile 深入: 用 profiler 看清它到底做了什么
对应文档: 06-编译与图模式.md
核心: 实验05里 compile 在 CPU 上"变慢"了(0.72x), 容易让人以为 compile 没用.
      本实验用 profiler 揭示 compile 真正的价值: 算子融合(operator fusion) + 消除 Python 开销.
      即使 CPU 加速不明显, "kernel 数量骤减"这一事实也能让你看懂 compile 的机制.
跑法: python3 07_compile_deep.py
"""
import torch
import torch.nn as nn
from torch.profiler import profile, ProfilerActivity
import time

torch.manual_seed(0)

# 一个典型的 MLP block: Linear->GELU->Linear->GELU->Linear->Dropout->ResAdd
class Block(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.fc1, self.fc2 = nn.Linear(d, 4*d), nn.Linear(4*d, d)
        self.gel = nn.GELU(); self.drop = nn.Dropout(0.1)
    def forward(self, x):
        h = self.drop(self.gel(self.fc1(x)))
        return x + self.drop(self.fc2(h))   # 残差

model = Block(256).eval()
x = torch.randn(128, 256)

print("=" * 66)
print("一、动态图 vs 静态图: PyTorch 的根本特性")
print("=" * 66)
print("  Eager(动态图, define-by-run): 每次 forward 都是普通 Python 执行, 边跑边建图")
print("    优点: 易调试(可断点/可print/可任意控制流)  缺点: 每次都有 Python 开销, 无法全局优化")
print("  Graph(静态图, 如 TF1/JAX): 先定义完整图再执行")
print("    优点: 编译器能全局优化(融合/常量折叠)  缺点: 难调试, 控制流受限")
print("  torch.compile 的精妙: 保持 eager 易用, 但'抓取'一段计算编译成优化图")
print("    本质 = 动态图的易用 + 静态图的性能(首次调用抓图+编译, 后续走编译图)")

print("\n" + "=" * 66)
print("二、profiler 看 eager 模式的算子数量")
print("=" * 66)
with torch.no_grad():
    with profile(activities=[ProfilerActivity.CPU]) as prof:
        for _ in range(5):
            model(x)
events_eager = prof.key_averages()
total_eager = sum(e.count for e in events_eager)
print(f"  eager: 共 {len(events_eager)} 种算子, 总算子调用数 {total_eager}")
top = sorted(events_eager, key=lambda e: -e.count)[:6]
for e in top:
    print(f"    {e.key:25s} 调用 {e.count:5d} 次")

print("\n" + "=" * 66)
print("三、profiler 看 compile 后的算子数量 (看融合!)")
print("=" * 66)
print("  编译中(首次抓图+生成代码, 有一次性开销)...")
compiled = torch.compile(model)
try:
    with torch.no_grad():
        # warmup 触发编译
        for _ in range(3):
            compiled(x)
        with profile(activities=[ProfilerActivity.CPU]) as prof:
            for _ in range(5):
                compiled(x)
        events_c = prof.key_averages()
        total_c = sum(e.count for e in events_c)
        print(f"  compiled: 共 {len(events_c)} 种算子, 总算子调用数 {total_c}")
        # 找 fused/compiled 相关的算子
        for e in sorted(events_c, key=lambda e: -e.count)[:6]:
            print(f"    {e.key:25s} 调用 {e.count:5d} 次")
        if total_c < total_eager:
            print(f"\n  ★ 算子调用数从 {total_eager} 降到 {total_c} (融合生效!)")
            print("    多个细碎算子(GELU的exp/tanh, Dropout的mask)被融合成更少的复合 kernel")
        else:
            print(f"  算子数 {total_c} vs eager {total_eager} (CPU 上融合收益有限, GPU 上更显著)")
except Exception as e:
    print(f"  compile 在本环境受限: {type(e).__name__}")

print("\n" + "=" * 66)
print("四、torch._dynamo 解释: 看 compile 抓到了什么 (explain)")
print("=" * 66)
try:
    exp = torch._dynamo.explain(model)(x)
    print(f"  抓到的图数量: {exp.graph_count}")
    print(f"  图中算子数:   {sum(len(g) for g in [exp.graphs]) if hasattr(exp,'graphs') else '?'}")
    print("  => dynamo 用 sys.settrace 跟踪 Python 字节码, 把 model(x) 翻译成 FX 图")
    print("     再交给后端(Inductor)生成 Triton(GPU)/C++(CPU) fused kernel")
except Exception as e:
    print(f"  explain 受限: {type(e).__name__} (版本相关, 略)")

print("\n" + "=" * 66)
print("五、compile 的局限: 动态控制流会'断图'(graph break)")
print("=" * 66)
def dyn_fn(x, n):
    # 数据依赖的控制流: 每次形状不同 -> 无法静态编译
    for _ in range(n):
        x = torch.relu(x)
    return x
try:
    cfn = torch.compile(dyn_fn, fullgraph=False)
    r = cfn(torch.randn(4), 3)
    print(f"  数据依赖循环可编译(allow graph break): 输出 shape {r.shape}")
except Exception as e:
    print(f"  {type(e).__name__}")
print("  compile 何时'不灵':")
print("    - 数据依赖的 shape 变化(变长序列, 每次不同) -> recompile, 变慢")
print("    - 频繁调用小函数 -> Python 抓图开销 > 融合收益")
print("    - CPU + 小模型 -> 融合省的访存不如 GPU 明显(实验05的0.72x就是这个原因)")
print("  compile 何时'真香':")
print("    - GPU + 中大模型 + 固定 shape -> 算子融合大幅减访存, 常见 1.5~3x 加速")
print("    - 训练(连反向也一起编译) -> AOTAutograd 把 fwd+bwd 整图优化")

print("\n核心洞察:")
print("  - PyTorch 本质是动态图(eager), compile 是在保持易用前提下'按需编译'的折中")
print("  - compile 的价值 = 算子融合(减内存读写) + 消 Python 开销, 不是魔法")
print("  - 收益强依赖场景: GPU/大模型/固定shape 赢家; CPU/小模型/动态shape 可能负收益")
print("  - 三段流水线: Dynamo(Python字节码→FX图) → AOTAutograd(融合fwd/bwd) → Inductor(生成kernel)")
