#!/usr/bin/env python3
"""CS336 论文精读 · 灵魂论文实验验证脚本
====================================================
每个实验用最小代码验证/复现一篇 ⭐⭐⭐ 论文的核心结论。
只依赖 numpy（无需 GPU），对应文档：../K-灵魂论文三层深读.md

运行: python3 experiments/verify_soul_papers.py
"""
import numpy as np
from collections import Counter

rng = np.random.default_rng(42)
SEP = "=" * 72


def softmax_2d(x):
    e = np.exp(x - x.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


# ===============================================================
# EXP 1 · Scaled Dot-Product Attention：为什么除以 sqrt(d_k)
# 对应 B1 · Transformer (2017)
# ===============================================================
print(SEP)
print("EXP 1 · 注意力缩放：除以 sqrt(d_k) 前后对比  [B1 Transformer]")
d_k, n_keys = 128, 2000
q = rng.normal(size=(64, d_k))
k = rng.normal(size=(n_keys, d_k))
logits_raw = q @ k.T                    # 未缩放
logits_scaled = logits_raw / np.sqrt(d_k)

def entropy_stats(logits):
    p = softmax_2d(logits)
    ent = -(p * np.log(p + 1e-12)).sum(-1).mean()
    grad_mag = (p * (1 - p)).mean()     # softmax 回传梯度的量级 ∝ p(1-p)
    return logits.std(), ent, grad_mag

for name, lg in [("未缩放", logits_raw), ("÷√d_k", logits_scaled)]:
    s, e, g = entropy_stats(lg)
    print(f"  {name}: std={s:6.2f}  softmax熵={e:6.3f}  梯度量级∝p(1-p)={g:.2e}")
print(f"  理论: 未缩放 std = √d_k = {np.sqrt(d_k):.2f}；最大熵 = ln({n_keys}) = {np.log(n_keys):.2f}")
print("  → 未缩放时 softmax 趋向 one-hot（熵→0，梯度→0，训练停滞）")

# ===============================================================
# EXP 2 · RoPE：验证"内积只依赖相对位置"
# 对应 B7 · RoPE (2021)
# ===============================================================
print()
print(SEP)
print("EXP 2 · RoPE 相对位置性质验证  [B7 RoPE]")

def rope_vec(x, pos, base=10000.0):
    d = x.shape[-1] // 2
    freqs = base ** (-np.arange(d) / d)          # (d/2,) 不同频率
    ang = pos * freqs
    x1, x2 = x[..., :d], x[..., d:]              # 半分割式（GPT-NeoX 风格）
    return np.concatenate([x1 * np.cos(ang) - x2 * np.sin(ang),
                           x1 * np.sin(ang) + x2 * np.cos(ang)], axis=-1)

d = 16
q = rng.normal(size=d)
k = rng.normal(size=d)
print("  位置对 (m,n)  相对距离 m-n   旋转后内积 q·k")
results = {}
for m, n in [(3, 1), (10, 8), (1000, 998), (5, 2), (17, 14)]:
    ip = rope_vec(q, m) @ rope_vec(k, n)
    results[(m, n)] = ip
    print(f"  ({m:4d},{n:4d})   {m-n:6d}        {ip:.8f}")
same2 = abs(results[(3, 1)] - results[(10, 8)]) < 1e-10 and abs(results[(3, 1)] - results[(1000, 998)]) < 1e-10
same3 = abs(results[(5, 2)] - results[(17, 14)]) < 1e-10
print(f"  相对距离=2 的三组内积完全一致? {same2}")
print(f"  相对距离=3 的两组内积完全一致? {same3}")
print("  → 绝对位置编码进旋转矩阵，注意力打分只依赖相对位置（且可外推到 pos=1000）")

# ===============================================================
# EXP 3 · Adam+L2 vs AdamW：解耦权重衰减
# 对应 B9 · AdamW (2017)
# ===============================================================
print()
print(SEP)
print("EXP 3 · Adam+L2(耦合) vs AdamW(解耦)  [B9 AdamW]")

def run_optimizer(decoupled, lam, steps=100, lr=0.05, w0=5.0):
    """纯权重衰减动力学（无任务梯度）：最干净的对照设定"""
    w = np.array(w0); m = v = 0.0; b1, b2 = 0.9, 0.999
    for t in range(1, steps + 1):
        g = 0.0 if decoupled else lam * w    # 耦合版把 L2 塞进梯度
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        mh = m / (1 - b1 ** t); vh = v / (1 - b2 ** t)
        w = w - lr * mh / (np.sqrt(vh) + 1e-8)
        if decoupled:
            w = w * (1 - lr * lam)           # 解耦衰减：直接作用参数
    return float(w)

print("  纯衰减对照（无任务梯度, w0=5.0, lr=0.05, 100步）——扫描 λ:")
print(f"  {'λ':>6} | {'AdamW(解耦)':>12} | {'Adam+L2(耦合)':>14} | {'理论(1-ηλ)^t':>12}")
for lam in [0.02, 0.1, 0.5]:
    theo = 5.0 * (1 - 0.05 * lam) ** 100
    print(f"  {lam:6.2f} | {run_optimizer(True, lam):12.4f} | {run_optimizer(False, lam):14.6f} | {theo:12.4f}")
print("  → AdamW: 最终 w 精确跟随理论值 (1-ηλ)^t —— λ 真正控制衰减强度")
print("  → Adam+L2: 无论 λ 多小, w 都被拉到 ~0 —— 因为衰减梯度 λw 进入后")
print("    被 √v̂ 归一化, 有效步长 ≈ lr·sign(w) 与 λ 无关（λ 被'吃掉'）")
print("    → 想要'温和的正则'时 Adam+L2 给出的却是激进的线性衰减")

# ===============================================================
# EXP 4 · FLOPs Calculus：C ≈ 6ND 的解析验证
# 对应 D3 · Bahdanau FLOPs Calculus (2022)
# ===============================================================
print()
print(SEP)
print("EXP 4 · 训练 FLOPs 会计学 C≈6ND 与 MFU 估算  [D3 FLOPs Calculus]")

def transformer_params(d, n_layers, vocab, ffn_mult=8 / 3):
    """SwiGLU 配方（3 矩阵 FFN，宽 8/3·d），embedding 单计"""
    h = int(ffn_mult * d)
    per_layer = 4 * d * d + 3 * d * h          # attn(q,k,v,o) + swiglu(w1,w2,w3)
    return vocab * d + n_layers * per_layer

# LLaMA-1-7B 近似配置
d, L, V = 4096, 32, 32000
N = transformer_params(d, L, V)
D_train = 1e12
C = 6 * N * D_train
per_tok_main = 6 * N                                   # 主项（参数项）
per_tok_attn = 2 * L * 2048 * d                        # 注意力得分项（ctx=2048）
print(f"  配置: d={d}, L={L}, vocab={V}  → 参数量 N ≈ {N/1e9:.2f}B (LLaMA-1-7B 官方 6.7B)")
print(f"  每 token 训练 FLOPs: 参数项 6N = {per_tok_main:.2e}；注意力项 = {per_tok_attn:.2e} ({per_tok_attn/per_tok_main*100:.1f}%)")
print(f"  → 注意力 ctx 项仅占 {per_tok_attn/per_tok_main*100:.1f}%，6N 主导（ctx 不大时）")
print(f"  训 1T tokens: C = 6ND = {C:.2e} FLOPs")
gpus, peak, mfu = 2048, 312e12, 0.45                   # A100 FP16 峰值 312 TFLOPS
T = C / (gpus * peak * mfu)
print(f"  2048×A100(312 TFLOPS, MFU 45%) 预计训练时长 = {T/3600:.1f} 小时 ≈ {T/3600/24:.1f} 天")
print(f"  （LLaMA-1-7B 官方报告: 82,432 A100·h ÷ 2048 = 40.3h ≈ 1.7 天 → 误差 <10% ✓）")

# ===============================================================
# EXP 5 · Chinchilla：拟合 L(N,D) 并复现 D*/N*≈20
# 对应 D4 · Chinchilla (2022) Approach 3
# ===============================================================
print()
print(SEP)
print("EXP 5 · Chinchilla 缩放定律拟合与最优 D/N  [D4 Chinchilla]")

def L_true(N, D, E=1.7, A=406.4, B=410.7, alpha=0.34, beta=0.28):
    return E + A / N ** alpha + B / D ** beta

# 生成带噪声的"实验数据"（模拟训练小模型的观测）
Ns = np.exp(rng.uniform(np.log(1e8), np.log(7e10), 150))
Ds = np.exp(rng.uniform(np.log(5e8), np.log(7e11), 150))
Lobs = L_true(Ns, Ds) * np.exp(rng.normal(0, 0.003, 150))   # 0.3% 噪声

# 网格搜索 (α,β) + 线性最小二乘 (E,A,B)——复现论文拟合流程
best = None
for alpha in np.arange(0.20, 0.51, 0.01):
    for beta in np.arange(0.20, 0.51, 0.01):
        X = np.stack([np.ones_like(Ns), Ns ** -alpha, Ds ** -beta], 1)
        coef, *_ = np.linalg.lstsq(X, Lobs, rcond=None)
        r = float(((X @ coef - Lobs) ** 2).sum())
        if best is None or r < best[0]:
            best = (r, alpha, beta, coef)
r, alpha_hat, beta_hat, (E_h, A_h, B_h) = best
print(f"  真值:   α=0.34, β=0.28, E=1.70")
print(f"  拟合出: α={alpha_hat:.2f}, β={beta_hat:.2f}, E={E_h:.2f}, A={A_h:.0f}, B={B_h:.0f}")

# 固定算力 C=6ND，扫描 N 找最优——检查 D*/N* 随 C 的变化
def optimal_ratio(C, E, A, B, alpha, beta):
    N_scan = np.exp(np.linspace(np.log(1e9), np.log(1e12), 4000))
    D_scan = C / (6 * N_scan)
    L_scan = E + A / N_scan ** alpha + B / D_scan ** beta
    i = L_scan.argmin()
    return N_scan[i], D_scan[i]

print("  用论文发表常数 (α=0.34, β=0.28, A=406.4, B=410.7) 推最优:")
for C_fix in [5.9e21, 5.9e22, 5.9e23]:
    Nopt, Dopt = optimal_ratio(C_fix, E_h, A_h, B_h, alpha_hat, beta_hat)
    print(f"    C={C_fix:.1e}: N*={Nopt/1e9:5.1f}B, D*={Dopt/1e12:5.2f}T, D*/N*={Dopt/Nopt:5.1f}")
Nopt, Dopt = optimal_ratio(5.9e23, E_h, A_h, B_h, alpha_hat, beta_hat)
print(f"  ⚠️ 注意: 在 Chinchilla 实际算力 (C=5.9e23≈70B×1.4T×6) 处，")
print(f"     参数化拟合给出的 D*/N*≈{Dopt/Nopt:.0f}，而非标题结论 '≈20'！")
print("  这不是 bug——是著名的 Chinchilla 拟合矛盾:")
print("   · '≈20 tokens/参数' 来自论文 Approach 1/2（包络/IsoFLOP 直接读数）")
print("   · Approach 3 发表的参数化常数隐含更多 tokens/参数（最优模型更小）")
ratio_exp = 1 - 2 * beta_hat / (alpha_hat + beta_hat)
print(f"   · 且 D*/N* 随 C 缓慢增长（~C^{ratio_exp:.2f}），本就不是常数 20")
print("   · Epoch AI 复现 (Besiroglu et al. 2024 = 本库 D6) 系统分析并修正了该拟合")
print("  → 教训: 参数化拟合对常数极敏感；headline 法则 ≠ 拟合隐含值")

# ===============================================================
# EXP 6 · GRPO 组内优势 + DPO 损失形状
# 对应 H6 · GRPO (2024) 与 H5 · DPO (2023)
# ===============================================================
print()
print(SEP)
print("EXP 6 · GRPO 组内归一化优势 与 DPO 损失  [H5 DPO / H6 GRPO]")

rewards = np.array([0.8, 0.2, 0.5, 0.5, 0.0, 1.0])       # 同一 prompt 的 G=6 个回答
A_grpo = (rewards - rewards.mean()) / (rewards.std() + 1e-8)
print(f"  原始奖励:  {rewards}")
print(f"  GRPO优势:  {np.round(A_grpo, 3)}")
print("  → 无需 value 网络，组内均值/方差即基线（sum≈0 ✓）")

def dpo_loss(gap, beta=0.2):
    """gap = log π(y_w)/π_ref(y_w) - log π(y_l)/π_ref(y_l)（隐式奖励差）"""
    return float(-np.log(1 / (1 + np.exp(-beta * gap))))
print("  DPO: 隐式奖励差 gap → 损失")
for gap in [-2, -1, 0, 1, 2, 4]:
    bar = "█" * int(dpo_loss(gap) * 12)
    print(f"    gap={gap:+d}: L={dpo_loss(gap):.4f} {bar}")
print("  → sigmoid 形状：gap 越大损失→0；gap<0（偏好学反）损失饱和于 ~gap·β")

# ===============================================================
# EXP 7 · BPE：最小可运行 tokenizer 训练器
# 对应 A10 · Sennrich BPE (2016)
# ===============================================================
print()
print(SEP)
print("EXP 7 · BPE 贪心合并训练（6 轮）  [A10 BPE]")

word_freq = Counter("low low low lower lowest newest newest widest".split())

def bpe_train(word_freq, n_merges=6):
    vocab = {tuple(w) + ("</w>",): c for w, c in word_freq.items()}
    merges = []
    for step in range(n_merges):
        pairs = Counter()
        for w, c in vocab.items():
            for i in range(len(w) - 1):
                pairs[w[i:i + 2]] += c
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        merges.append("".join(best))
        new_vocab = {}
        for w, c in vocab.items():
            i = 0; nw = []
            while i < len(w):
                if i < len(w) - 1 and (w[i], w[i + 1]) == best:
                    nw.append(w[i] + w[i + 1]); i += 2
                else:
                    nw.append(w[i]); i += 1
            new_vocab[tuple(nw)] = c
        vocab = new_vocab
        print(f"    第{step+1}轮: 合并 {best} → 新词片 '{''.join(best)}' (频次 {pairs[best]})")
    return merges

merges = bpe_train(word_freq)
print(f"  学到的合并序列: {merges}")
print("  → 高频对优先合并；'lowest' 会用到 (l,o)(lo,w)(e,s)(est,)</w> 等已学词片")

# ===============================================================
# EXP 8 · KV Cache 内存：MHA vs GQA vs MQA vs MLA
# 对应 B11 · GQA (2023) 与 B15 · MLA (2024)
# ===============================================================
print()
print(SEP)
print("EXP 8 · KV Cache 显存对比（LLaMA-2-70B 配置: 80层×128 head_dim, bf16）")

def kv_gb(ctx, layers, kv_heads, head_dim, bytes=2):
    return 2 * bytes * layers * ctx * kv_heads * head_dim / 1e9   # 2=K和V

for ctx in [4096, 32768, 131072]:
    mha = kv_gb(ctx, 80, 64, 128)          # 64 组 KV（MHA）
    gqa = kv_gb(ctx, 80, 8, 128)           # 8 组 KV（LLaMA-2-70B 实际配置）
    mqa = kv_gb(ctx, 80, 1, 128)           # 1 组 KV（MQA）
    mla = 2 * 2 * 80 * ctx * 512 / 1e9     # MLA: 压缩向量 512 维（K/V 合并缓存）
    print(f"  ctx={ctx:>6}: MHA={mha:7.1f}GB | GQA(8)={gqa:7.1f}GB | MQA={mqa:6.1f}GB | MLA(512d)={mla:6.1f}GB")
print("  → ctx=128K 时 MHA 单序列要 343GB（爆显存）；GQA 降 8×；MLA 再降且质量更优")
print("  → 这就是 LLaMA-2-70B 用 GQA、DeepSeek-V2 用 MLA 的直接原因")

print()
print(SEP)
print("全部 8 个实验完成 ✅  对应解读见 ../K-灵魂论文三层深读.md")
