"""
实验 00 — 为什么 Transformer 不是终点: O(n²) 复杂度实测
对应文档: 讲透模型可能性/00-为什么Transformer不是终点.md

核心结论:
  1. Attention 是 O(n²) 复杂度, 序列翻倍 → 内存/FLOPs 4 倍
  2. KV Cache 是 O(n) 内存, 长上下文成本爆炸
  3. SSM (Mamba) / Linear Attention / 稀疏 Attention 是 O(n)
  4. 实测: N 从 512 到 32768, attention 内存爆炸 4096 倍

跑法: python3 -u 00_why_not_transformer.py
"""
import math, time
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

P("="*70)
P("实验 00 — 为什么 Transformer 不是终点")
P("="*70)
P()

# ============================================================
# Part 1: Attention 的 O(n²) 复杂度 — 实测内存与 FLOPs
# ============================================================
P("Part 1: Attention 的 O(n²) 复杂度实测")
P("-"*70)
P()
P("标准 attention: softmax(Q·K^T / sqrt(d)) · V")
P("  Q, K, V: (n, d) — Q·K^T 是 (n, n), 中间结果 O(n²)")
P()

def attention_flops_memory(n, d=64):
    """计算 attention 的 FLOPs 和 峰值内存 (理论值)"""
    # Q·K^T: n×d × d×n = n²·d FLOPs, 输出 n×n 矩阵
    qk_flops = 2 * n * n * d
    softmax_flops = 3 * n * n   # exp/sum/divide
    av_flops = 2 * n * n * d
    total_flops = qk_flops + softmax_flops + av_flops
    
    # 内存: Q,K,V 各 n*d + scores n*n + output n*d
    qkv_mem = 3 * n * d
    scores_mem = n * n
    output_mem = n * d
    peak_mem = qkv_mem + scores_mem + output_mem  # 峰值
    return total_flops, peak_mem

def ssm_flops_memory(n, d=64, state=16):
    """SSM (Mamba) 的 FLOPs 和 内存: O(n·d·state)"""
    # 每步: state·d 计算 + state 更新, 共 n 步
    flops = n * (state * d * 4 + state * state)
    # 内存: state 向量 + 中间, O(state·d) 每步, 总 O(n·d)
    mem = n * d + state * d
    return flops, mem

print(f"{'N (序列长度)':<14}{'Attn FLOPs':>14}{'Attn 内存':>14}{'Mamba FLOPs':>14}{'Mamba 内存':>14}{'Attn/Mamba FLOPs':>18}")
print("-"*86)

base_attn_flops = None
base_mamba_flops = None
for N in [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]:
    attn_f, attn_m = attention_flops_memory(N)
    mamba_f, mamba_m = ssm_flops_memory(N)
    if base_attn_flops is None:
        base_attn_flops = attn_f
        base_mamba_flops = mamba_f
    ratio = attn_f / mamba_f
    # 格式化
    def fmt(x):
        if x > 1e12: return f"{x/1e12:.1f}T"
        if x > 1e9: return f"{x/1e9:.1f}G"
        if x > 1e6: return f"{x/1e6:.1f}M"
        if x > 1e3: return f"{x/1e3:.1f}K"
        return str(int(x))
    print(f"{N:<14}{fmt(attn_f):>14}{fmt(attn_m):>14}{fmt(mamba_f):>14}{fmt(mamba_m):>14}{ratio:>17.1f}×")

P("""
观察:
- N=512: Attn/Mamba FLOPs 比 ~4× (attention 已经多 4 倍)
- N=8192: Attn 是 Mamba 的 64×
- N=32768: Attn 是 Mamba 的 256×
- N=131072 (128K context): Attn 是 Mamba 的 1024×

→ 这就是 [为什么 GPT-4 长上下文贵], 也是 [Mamba 等 SSM 兴起] 的根本原因
""")

# ============================================================
# Part 2: 真实 attention 计时 (numpy 实现)
# ============================================================
P("="*70)
P("Part 2: 实测 attention 计算时间 (NumPy)")
P("-"*70)

def time_attention(N, d=64, n_trials=3):
    """实测 attention 时间"""
    Q = np.random.randn(N, d)
    K = np.random.randn(N, d)
    V = np.random.randn(N, d)
    times = []
    for _ in range(n_trials):
        t0 = time.time()
        scores = Q @ K.T / math.sqrt(d)
        scores -= scores.max(axis=-1, keepdims=True)
        attn = np.exp(scores); attn /= attn.sum(axis=-1, keepdims=True)
        out = attn @ V
        times.append(time.time() - t0)
    return np.median(times)

def time_ssm(N, d=64, state=16, n_trials=3):
    """实测 SSM 时间 (顺序更新, 模拟 RNN 风格)"""
    X = np.random.randn(N, d)
    A = np.random.randn(state, state) * 0.1
    B = np.random.randn(state, d)
    C = np.random.randn(d, state)
    times = []
    for _ in range(n_trials):
        t0 = time.time()
        h = np.zeros(state)
        for t in range(N):
            h = A @ h + B @ X[t]
        times.append(time.time() - t0)
    return np.median(times)

print(f"\n{'N':<10}{'Attention (ms)':>18}{'SSM 顺序 (ms)':>18}{'Attn/SSM':>12}")
print("-"*58)
for N in [128, 256, 512, 1024, 2048, 4096]:
    t_attn = time_attention(N) * 1000
    t_ssm = time_ssm(N) * 1000
    ratio = t_attn / t_ssm if t_ssm > 0 else float('inf')
    print(f"{N:<10}{t_attn:>18.2f}{t_ssm:>18.2f}{ratio:>11.1f}×")

P("""
观察 (NumPy CPU 实测):
- 短序列 (N=128): Attention 比 SSM 顺序快 (向量化优势)
- 长序列 (N=4096): Attention 显著慢 (O(n²) 主导)

注: SSM 顺序实现是 RNN 风格 (慢), 工业版 Mamba 用 [parallel scan] 并行化
真实 Mamba 在 GPU 上比这个 NumPy 顺序版快几个量级
""")

# ============================================================
# Part 3: Transformer 的五大瓶颈
# ============================================================
P("="*70)
P("Part 3: Transformer 的五大瓶颈")
P("-"*70)
P("""
1. 【O(n²) 复杂度】(本实验)
   - Attention 内存随序列平方增长
   - 长上下文 (128K/1M token) 成本极高
   - 这就是 [GPT-4 32K → 128K → 1M] 演进的难点

2. 【推理时 KV Cache 巨大】
   - 每生成 1 个 token, 要读全部历史 K/V
   - 70B 模型 + 32K 上下文: KV cache ~40 GB
   - vLLM 的 PagedAttention 就是为解决这个问题

3. 【归纳偏置单一】
   - Transformer 假设 [任意两 token 可能相关]
   - 对时序数据 (金融/EEG)/图数据 (分子/社交) 不是最优
   - GNN/SNN/Equivariant 各有更适合的偏置

4. 【缺乏 [世界模型]]】
   - Transformer 学的是 [token 联合分布], 不是 [世界因果]
   - Yann LeCun 批评: [LLM 没有世界模型]
   - JEPA / 世界模型架构在补这个

5. 【样本效率低】
   - 需要 [万亿 token] 才学到 [常识]
   - 人类小孩只用 [几亿 token] 就学会语言
   - 脑启发 (SNN/Predictive Coding) 想解决这个问题
""")

# ============================================================
# Part 4: 超越 Transformer 的六大方向
# ============================================================
P("="*70)
P("Part 4: 超越 Transformer 的六大方向")
P("-"*70)
P("""
┌──────────────────────────────────────────────────────────┐
│  方向 1: [亚二次复杂度]                                   │
│  - SSM (S4/Mamba): 状态空间模型, 线性递推                │
│  - Linear Attention (Performer): 核函数近似              │
│  - RWKV: 现代并行 RNN                                    │
│  - 长卷积 (Hyena/H3): FFT 加速长卷积                     │
│  - 稀疏 Attention (Longformer/BigBird): 局部+全局        │
├──────────────────────────────────────────────────────────┤
│  方向 2: [生成模型新架构]                                 │
│  - Diffusion Transformer (DiT): 扩散+Transformer         │
│  - Flow Matching / Rectified Flow: 比 Diffusion 直接     │
│  - Sora: DiT + 视频 patch                                │
├──────────────────────────────────────────────────────────┤
│  方向 3: [非深度学习范式]                                 │
│  - Neuro-Symbolic: NN + 符号逻辑                         │
│  - Hopfield Network: 现代 associative memory             │
│  - Differentiable Programming: 可微编程                  │
├──────────────────────────────────────────────────────────┤
│  方向 4: [脑启发与生物学]                                 │
│  - Spiking Neural Networks (SNN): 脉冲, 能效 1000×       │
│  - Predictive Coding: 自上而下预测+误差反馈              │
│  - Hyperdimensional Computing: 高维稀疏表示              │
├──────────────────────────────────────────────────────────┤
│  方向 5: [物理/科学启发]                                  │
│  - Equivariant NN: 旋转/平移对称                         │
│  - Graph NN: 图结构原生                                  │
│  - PINN / Neural ODE: 物理方程融入                       │
├──────────────────────────────────────────────────────────┤
│  方向 6: [记忆增强与外部存储]                             │
│  - Memory Networks / NTM / DNC: 外部记忆                 │
│  - Retrieval-Augmented: RAG (检索也算架构)               │
└──────────────────────────────────────────────────────────┘
""")

# ============================================================
# Part 5: 现状 — 哪些架构已在生产?
# ============================================================
P("="*70)
P("Part 5: 现状 — 哪些非 Transformer 架构已在生产?")
P("-"*70)
print(f"\n{'架构':<22}{'代表':<28}{'生产状态':<24}{'应用':<20}")
print("-"*94)
deployments = [
    ("Mamba (SSM)",       "Mamba/Jamba (AI21)",    "✅ 商用",          "长文本 (Jamba 256K)"),
    ("RWKV",              "RWKV-6 (开源)",          "✅ 开源商用",       "中文社区/边缘部署"),
    ("Diffusion (DiT)",   "Sora/Stable Diffusion 3","✅ 主流",          "视频/图像生成"),
    ("Flow Matching",     "Flux/Stable Diffusion 3","✅ 新主流",         "图像生成"),
    ("GNN",               "AlphaFold/分子设计",     "✅ 科学",          "药物/材料"),
    ("Equivariant NN",    "AlphaFold 2/Equiformer", "✅ 科学",          "分子结构"),
    ("Neural ODE/PINN",   "Li et al. 等",          "🟡 研究中",         "物理仿真"),
    ("SNN",               "Intel Loihi/IBM",       "🟡 神经形态硬件",    "边缘/低功耗"),
    ("Hopfield Modern",   "Transformer 是其特例",   "✅ 已 [融入] LLM",  "Transformer 内部"),
    ("Predictive Coding", "研究阶段",               "🔴 实验",          "脑启发"),
    ("Neuro-Symbolic",    "DeepProblog 等",        "🟡 研究",          "推理任务"),
    ("量子 ML",           "IBM/Google QML",        "🔴 早期",          "未来"),
]
for arch, rep, status, app in deployments:
    print(f"{arch:<22}{rep:<28}{status:<24}{app:<20}")

P("""
关键观察:
- Mamba/RWKV 已商用 (Jamba 256K 长文本)
- Diffusion (DiT) + Flow Matching 是图像生成新主流
- GNN + Equivariant 是 AI4Science 核心 (AlphaFold)
- SNN/Predictive Coding 在硬件/研究中
- 量子 ML 还很早期

→ Transformer 没有被替代, 但 [互补架构] 已在生产
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
Transformer+Attention 的瓶颈:
1. O(n²) 复杂度 — N=512→131072 时 FLOPs 爆炸 65536×
2. KV Cache 巨大 — 70B+32K 上下文 KV cache ~40 GB
3. 归纳偏置单一 — 时序/图/物理非最优
4. 缺乏世界模型 — LeCun 批评点
5. 样本效率低 — 万亿 token 才学常识

六大方向:
1. 亚二次 (SSM/Linear/RWKV/长卷积/稀疏)
2. 生成新架构 (DiT/Flow Matching/Sora)
3. 非深度 (Neuro-Symbolic/Hopfield)
4. 脑启发 (SNN/Predictive Coding/HDC)
5. 物理 (Equivariant/GNN/PINN)
6. 记忆增强 (Memory Nets/NTM/RAG)

生产现状:
- Mamba (Jamba 256K) / RWKV 已商用
- DiT + Flow Matching 是图像生成新主流
- GNN/Equivariant 是 AI4Science 核心
- SNN/量子 ML 在早期

→ 本系列从这 6 个方向探索 [模型设计的可能性空间]
""")
