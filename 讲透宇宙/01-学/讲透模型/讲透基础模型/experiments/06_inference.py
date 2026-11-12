"""
实验 06 —— 推理优化: KV Cache / 量化 / 蒸馏 (让大模型又快又省)
对应文档: 讲透基础模型/06-推理优化.md
核心结论:
  1. KV Cache: 自回归生成时缓存历史 K/V, 投影从 O(n²d²) 降到 O(nd²), attention 从 O(n³d) 降到 O(n²d)
  2. 量化: FP32→INT8/INT4, 显存省 4x/8x, 代价是微小精度损失
  3. 蒸馏: 用大模型(teacher)的软标签训小模型(student)
注: KV Cache 的墙钟加速需 GPU+FlashAttention, CPU toy 受 kernel-launch overhead 干扰,
    故本实验用【理论 FLOPs】展示其本质优势, 墙钟计时仅作参考。
跑法: python3 -u 06_inference.py
"""
import math, time
import torch
import torch.nn as nn
import torch.nn.functional as F

def P(*a): print(*a, flush=True)
torch.manual_seed(0)
d = 256

# =========================================================
# Part 1: KV Cache —— 用理论 FLOPs 揭示本质 (O(n²)→O(n))
# =========================================================
P("="*62); P("Part 1: KV Cache —— 计算量从 O(n²) 降到 O(n) per step"); P("="*62)
P("生成第 t 个 token 时(序列已长 t):")
P("  无 cache: 对整个序列重算 3 个投影(每个 t·d²) + attention(2·t²·d)")
P("  有 cache: 只投影新 token(3·d²) + 用缓存 K/V 算 attention(2·t·d)\n")

def flops_nocache(t):   # 生成第t个token(序列长t) 无cache
    return 3 * t * d * d + 2 * t * t * d
def flops_cache(t):     # 有cache
    return 3 * d * d + 2 * t * d

init_len, N_gen = 10, 80
tot_nc = sum(flops_nocache(t) for t in range(init_len, init_len + N_gen))
tot_c  = sum(flops_cache(t)    for t in range(init_len, init_len + N_gen))
P("生成 %d 个 token 的【总 FLOPs】(d=%d):" % (N_gen, d))
P("  无 KV Cache: %.3e FLOPs" % tot_nc)
P("  有 KV Cache: %.3e FLOPs  (计算量减少 %.0fx)" % (tot_c, tot_nc / tot_c))
P("\n单步 FLOPs 随序列增长:")
for t in [10, 30, 50, 90]:
    P("  序列长 %d: 无cache %s, 有cache %s (%.0fx)" %
      (t, f"{flops_nocache(t):.2e}", f"{flops_cache(t):.2e}", flops_nocache(t)/flops_cache(t)))
P("==> 序列越长, cache 的 FLOPs 优势越大(无cache O(t²), 有cache O(t)).")
P("    真实 LLM(序列数千、GPU+FlashAttention)能加速数十倍; 这就是流式秒回的基础.\n")

# 墙钟计时(参考, 受 CPU overhead 影响不体现真实加速)
Wq = nn.Linear(d, d, bias=False); Wk = nn.Linear(d, d, bias=False); Wv = nn.Linear(d, d, bias=False)
def attn(Q, K, V): return F.softmax(Q @ K.transpose(-1,-2) / math.sqrt(d), -1) @ V
seq = torch.randn(init_len, d); t0 = time.perf_counter()
for _ in range(N_gen):
    attn(Wq(seq), Wk(seq), Wv(seq)); seq = torch.cat([seq, torch.randn(1, d)])
P("[参考] CPU 墙钟计时: 无cache %.2fs" % (time.perf_counter()-t0) +
  " (注: CPU+小矩阵下 kernel-launch overhead 主导, 体现不出 FLOPs 优势; 真实加速看 FLOPs 比)\n")

# =========================================================
# Part 2: 量化
# =========================================================
P("="*62); P("Part 2: 量化 —— 省显存换微小精度损失"); P("="*62)
w = torch.randn(2000) * 0.08
def quantize(w, bits):
    levels = 2**(bits-1) - 1
    scale = w.abs().max() / levels
    return torch.round(w / scale).clamp(-levels, levels) * scale
err8 = (w - quantize(w, 8)).pow(2).mean().sqrt()
err4 = (w - quantize(w, 4)).pow(2).mean().sqrt()
P("FP32 → INT8: 误差 %.2e, 显存省4x (误差/权重幅度 %.1f%%, 几乎无损)" % (err8, 100*err8/w.abs().mean()))
P("FP32 → INT4: 误差 %.2e, 显存省8x (误差/权重幅度 %.1f%%, AWQ/GPTQ 保护重要权重后可用)" % (err4, 100*err4/w.abs().mean()))
P("==> 70B 模型: FP32 需 280GB, INT4 仅 35GB —— 单卡可跑.\n")

# =========================================================
# Part 3: 蒸馏
# =========================================================
P("="*62); P("Part 3: 蒸馏 —— teacher 的软标签训 student"); P("="*62)
P("Hinton 2015: 大模型(teacher)输出概率含'暗知识'(类间相似度信息),")
P("小模型(student)学这个软分布比学硬标签更好.")
P("  loss = α·CE(student, 硬标签) + (1-α)·KL(softmax(student/T) ‖ softmax(teacher/T))")
P("典型: GPT-4 蒸馏到小模型(Alpaca); DeepSeek-R1 推理能力蒸馏到 1.5B/7B.")
P("==> 蒸馏是'穷人的 Scaling Law': 把大模型能力搬到小模型, 无需重训.")
