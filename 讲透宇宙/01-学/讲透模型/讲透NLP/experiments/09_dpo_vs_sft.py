#!/usr/bin/env python3
"""
讲透NLP · Ch9 后训练 — 配套实验: SFT vs DPO 在 Tiny GPT 上的对比
对应文档: 09-后训练-SFT对齐DPO-test-time.md

两个反直觉发现:
  1. DPO 训得太狠 → KL 爆炸 + 熵坍塌 (概率漂移到 ref 模型之外)
  2. SFT 在好回答上 P 上升, 但坏回答的 P 也在变 (无对比信号)
     —— 当 chosen/rejected 共享 token 时, P(rejected) 甚至可能先升后降!

跑法: python3 -u 09_dpo_vs_sft.py  (~5-20 秒)
"""
import math
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(1)
torch.manual_seed(42)

VOCAB_SIZE = 14   # 0=pad, 1=bos, 2=eos, 3-6=question, 7-9=good-answer, 10-12=bad-answer, 13=misc
PROMPT_LEN = 3
RESP_LEN   = 3


def P(*args, **kwargs):
    print(*args, **kwargs, flush=True)


# ============================================================
#  Part 0: Tiny GPT 模型 (因果 self-attention + pre-norm)
# ============================================================

class CausalSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_head  = d_model // n_heads
        self.qkv     = nn.Linear(d_model, 3 * d_model)
        self.proj    = nn.Linear(d_model, d_model)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x).view(B, T, 3, self.n_heads, self.d_head)
        q, k, v = qkv.unbind(dim=2)               # each: (B, T, nh, dh)
        q = q.transpose(1, 2)                      # (B, nh, T, dh)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        mask = torch.triu(torch.full((T, T), float('-inf')), diagonal=1)
        scores = scores + mask
        attn = F.softmax(scores, dim=-1)
        out = (attn @ v).transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.ln1  = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads)
        self.ln2  = nn.LayerNorm(d_model)
        self.ffn  = nn.Sequential(
            nn.Linear(d_model, d_model * 4), nn.GELU(),
            nn.Linear(d_model * 4, d_model))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class TinyGPT(nn.Module):
    def __init__(self, vocab_size=VOCAB_SIZE, d_model=64, n_heads=4,
                 n_layers=2, max_len=8):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)
        self.blocks  = nn.ModuleList(
            [TransformerBlock(d_model, n_heads) for _ in range(n_layers)])
        self.ln_f    = nn.LayerNorm(d_model)
        self.head    = nn.Linear(d_model, vocab_size, bias=False)
        self.head.weight = self.tok_emb.weight   # weight tying
        self.apply(self._init_weights)

    def _init_weights(self, module):
        # GPT-2 风格小方差初始化: 否则 weight-tying + N(0,1) embedding
        # 会让初始 logits 极度尖锐 (logP=-122 而非均匀的 ~-8),
        # 参考模型一开始就熵坍塌, DPO 的 β 对比实验全部失真。
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=0.02)

    def forward(self, idx):
        B, T = idx.shape
        pos = torch.arange(T).unsqueeze(0)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        for blk in self.blocks:
            x = blk(x)
        return self.head(self.ln_f(x))


# ============================================================
#  核心函数: 概率计算 + SFT loss + DPO loss + 诊断
# ============================================================

def response_logprobs(model, prompts, responses):
    """批量计算 Σ_t log p(y_t | x, y_<t), 返回 (B,) 总 log-prob."""
    full   = torch.cat([prompts, responses], dim=1)    # (B, P+R)
    logits = model(full)                                # (B, P+R, V)
    plen   = prompts.size(1)
    pred   = logits[:, plen - 1: plen - 1 + responses.size(1), :]  # (B, R, V)
    logp   = F.log_softmax(pred, dim=-1)
    return logp.gather(2, responses.unsqueeze(-1)).squeeze(-1).sum(1)


def sft_loss_fn(model, prompts, chosens):
    """SFT = chosen response 的负对数似然."""
    return -response_logprobs(model, prompts, chosens).mean()


def dpo_loss_fn(model, ref_model, prompts, chosens, rejecteds, beta):
    """DPO = -log σ(β·[log(π(yw)/πref(yw)) − log(π(yl)/πref(yl))])."""
    logp_w = response_logprobs(model, prompts, chosens)
    logp_l = response_logprobs(model, prompts, rejecteds)
    with torch.no_grad():
        logp_w_ref = response_logprobs(ref_model, prompts, chosens)
        logp_l_ref = response_logprobs(ref_model, prompts, rejecteds)
    ratio_w = logp_w - logp_w_ref
    ratio_l = logp_l - logp_l_ref
    return -F.logsigmoid(beta * (ratio_w - ratio_l)).mean()


def next_token_kl(model, ref_model, seqs):
    """KL(π_θ(·|seq) ‖ π_ref(·|seq)) 在序列末尾的 next-token 分布上."""
    logits     = model(seqs)[:, -1, :]
    ref_logits = ref_model(seqs)[:, -1, :]
    p    = F.softmax(logits, dim=-1)
    logp = F.log_softmax(logits, dim=-1)
    logq = F.log_softmax(ref_logits, dim=-1)
    return (p * (logp - logq)).sum(1).mean().item()


def next_token_entropy(model, seqs):
    """next-token 分布的平均熵."""
    logits = model(seqs)[:, -1, :]
    p    = F.softmax(logits, dim=-1)
    logp = F.log_softmax(logits, dim=-1)
    return -(p * logp).sum(1).mean().item()


# ============================================================
#  偏好数据
# ============================================================
# Tokens: 0=pad, 1=bos, 2=eos
#   3-6 = question tokens (prompt 内容)
#   7-9 = good answer tokens
#   10-12 = bad answer tokens
#   13 = misc
# 好回答用 7-9, 坏回答用 10-12, 都以 eos(2) 结尾
# 最后 2 组: chosen 和 rejected 共享首 token → 展示 SFT 盲区

PREF_PAIRS = [
    # (prompt,         chosen,      rejected)
    ([1, 3, 4],        [7, 8, 2],   [10, 11, 2]),    # 无共享
    ([1, 4, 5],        [7, 9, 2],   [10, 12, 2]),    # 无共享
    ([1, 5, 6],        [8, 9, 2],   [11, 12, 2]),    # 无共享
    ([1, 3, 6],        [9, 7, 2],   [12, 10, 2]),    # 无共享
    ([1, 4, 3],        [7, 8, 2],   [7, 11, 2]),     # 共享首 token 7 + eos
    ([1, 6, 4],        [8, 9, 2],   [8, 12, 2]),     # 共享首 token 8 + eos
]

prompts   = torch.tensor([p[0] for p in PREF_PAIRS])
chosens   = torch.tensor([p[1] for p in PREF_PAIRS])
rejecteds = torch.tensor([p[2] for p in PREF_PAIRS])
MAX_ENT   = math.log(VOCAB_SIZE)


# ============================================================
#  初始化参考模型 (SFT 和 DPO 的共同起点)
# ============================================================
ref_model = TinyGPT()
ref_model.eval()
for param in ref_model.parameters():
    param.requires_grad_(False)

n_params = sum(p.numel() for p in ref_model.parameters())


# ============================================================
#  Part 1: SFT 的盲区 — P(好回答)↑ 但 P(坏回答) 也在变
# ============================================================
P("=" * 66)
P("讲透NLP · Ch9: SFT vs DPO — Tiny GPT 对比实验")
P("=" * 66)
P(f"模型: TinyGPT (vocab={VOCAB_SIZE}, d_model=64, 2层, 4头, {n_params:,} 参数)")
P(f"偏好数据: {len(PREF_PAIRS)} 组 (前4组无共享token, 后2组chosen/rejected共享首token)")
P(f"最大熵 = log({VOCAB_SIZE}) = {MAX_ENT:.3f} nats\n")

P("=" * 66)
P("Part 1: SFT 的盲区 — P(chosen)↑ 但 P(rejected) 也在变 (无对比信号)")
P("=" * 66)

sft_model = copy.deepcopy(ref_model)
for p in sft_model.parameters():
    p.requires_grad_(True)
opt = torch.optim.Adam(sft_model.parameters(), lr=3e-3)

with torch.no_grad():
    init_lw = response_logprobs(sft_model, prompts, chosens).mean().item()
    init_ll = response_logprobs(sft_model, prompts, rejecteds).mean().item()
P(f"初始: logP(chosen)={init_lw:.3f}  logP(rejected)={init_ll:.3f}  "
  f"差={init_lw-init_ll:.3f}")
P("")

track = []
for step in range(300):
    opt.zero_grad()
    loss = sft_loss_fn(sft_model, prompts, chosens)
    loss.backward()
    opt.step()
    if step % 25 == 0 or step == 299:
        with torch.no_grad():
            lw = response_logprobs(sft_model, prompts, chosens).mean().item()
            ll = response_logprobs(sft_model, prompts, rejecteds).mean().item()
        track.append((step, lw, ll))
        P(f"  Step {step:3d}: logP(chosen)={lw:+.3f}  logP(rejected)={ll:+.3f}  "
          f"比={lw-ll:+.3f}")

# 分析 P(rejected) 变化
p_rej_init   = math.exp(init_ll)                  # 真正的初始 (训练前)
p_rej_vals   = [math.exp(t[2]) for t in track]
p_rej_max    = max(p_rej_vals)
p_rej_max_st = track[p_rej_vals.index(p_rej_max)][0]
p_rej_final  = p_rej_vals[-1]

P("")
P("─" * 50)
P(f"P(rejected) 轨迹:")
P(f"  初始:    {p_rej_init*100:.4f}%")
P(f"  峰值:    {p_rej_max*100:.4f}%  (Step {p_rej_max_st})")
P(f"  最终:    {p_rej_final*100:.4f}%")
if p_rej_max > p_rej_init * 1.05:
    P(f"\n  ⚠️  反直觉: P(rejected) 先升后降!")
    P(f"     Step {p_rej_max_st} 时 P(rejected)={p_rej_max*100:.4f}% > 初始 {p_rej_init*100:.4f}%")
    P(f"     原因: chosen 和 rejected 共享 token (首 token + eos),")
    P(f"     SFT 抬高共享 token 概率时, 坏回答的概率也被附带抬高。")
P(f"\n  SFT 没有 '这是坏回答' 的信号 — P(rejected) 的变化纯属附带效应。")
P(f"  这就是 SFT 之后还需要 DPO/RLHF 的原因。\n")


# ============================================================
#  Part 2: DPO — 有对比信号的偏好优化
# ============================================================
P("=" * 66)
P("Part 2: DPO (β=0.1) — 偏好对的直接优化, 有对比信号")
P("=" * 66)

dpo_model = copy.deepcopy(ref_model)
for p in dpo_model.parameters():
    p.requires_grad_(True)
opt2 = torch.optim.Adam(dpo_model.parameters(), lr=1e-3)
BETA = 0.1

for step in range(300):
    opt2.zero_grad()
    loss = dpo_loss_fn(dpo_model, ref_model, prompts, chosens, rejecteds, BETA)
    loss.backward()
    opt2.step()
    if step % 50 == 0 or step == 299:
        with torch.no_grad():
            lw = response_logprobs(dpo_model, prompts, chosens).mean().item()
            ll = response_logprobs(dpo_model, prompts, rejecteds).mean().item()
            kl = next_token_kl(dpo_model, ref_model, prompts)
        P(f"  Step {step:3d}: loss={loss.item():.4f}  "
          f"logP(w)={lw:+.3f}  logP(l)={ll:+.3f}  "
          f"比={lw-ll:+.3f}  KL={kl:.4f}")

P(f"\nDPO 明确增大 logP(chosen) - logP(rejected) → P(chosen)/P(rejected)↑")
P(f"同时 KL 保持适中 ({kl:.4f}), 模型没有退化。")
P(f"对比 SFT: SFT 只推高 P(chosen), DPO 同时推高 chosen 并压低 rejected。\n")


# ============================================================
#  Part 3: DPO 的陷阱 — 训太狠 → KL 爆炸 + 熵坍塌
# ============================================================
P("=" * 66)
P("Part 3: DPO 训太狠 → KL 爆炸, 模型退化")
P("=" * 66)

for beta_val, n_steps, lr in [(0.05, 500, 5e-3), (0.5, 500, 5e-3)]:
    P(f"\n{'─'*50}")
    P(f"  β={beta_val} (KL约束{'弱' if beta_val < 0.1 else '强'}), "
      f"训练 {n_steps} 步, lr={lr}")
    P(f"{'─'*50}")
    m = copy.deepcopy(ref_model)
    for p in m.parameters():
        p.requires_grad_(True)
    opt3 = torch.optim.Adam(m.parameters(), lr=lr)
    for step in range(n_steps):
        opt3.zero_grad()
        loss = dpo_loss_fn(m, ref_model, prompts, chosens, rejecteds, beta_val)
        loss.backward()
        opt3.step()
        if step % 100 == 0 or step == n_steps - 1:
            with torch.no_grad():
                lw = response_logprobs(m, prompts, chosens).mean().item()
                ll = response_logprobs(m, prompts, rejecteds).mean().item()
                kl = next_token_kl(m, ref_model, prompts)
                ent = next_token_entropy(m, prompts)
            flag = " ⚠️退化!" if ent < MAX_ENT * 0.35 else ""
            P(f"  Step {step:4d}: loss={loss.item():.6f}  "
              f"logP(w)={lw:+.3f}  logP(l)={ll:+.3f}  "
              f"KL={kl:7.3f}  entropy={ent:.3f}/{MAX_ENT:.3f}{flag}")
    ratio = ent / MAX_ENT
    P(f"\n  β={beta_val} 结果: KL={kl:.3f}, 熵占比={ratio:.1%}")
    if ratio < 0.35:
        P(f"  ⚠️ 熵坍塌 < 35%: 模型只能输出少数特定序列, 通用能力丧失!")
    elif ratio < 0.70:
        P(f"  ⚠️ 熵明显下降: 模型开始退化, 多样性受损。")
    else:
        P(f"  ✓ 熵正常: β={beta_val} 的 KL 约束有效, 模型保持健康。")

P(f"\n{'='*66}")
P("⚠️ 核心发现: DPO 训得越久 / β 越小, KL 增长越快, 熵越低。")
P("   β 小 (约束弱): 偏好学得快, 但 KL 爆炸更严重, 模型更快退化。")
P("   β 大 (约束强): KL 稳定, 但偏好学得慢。")
P("   实践: DPO 需要 early stopping 或调好 β, 否则 reward hacking。\n")


# ============================================================
#  Part 4: 总结
# ============================================================
P("=" * 66)
P("总结: SFT vs DPO 的关键差异")
P("=" * 66)
P("""
┌──────────┬────────────────────────┬──────────────────────────────┐
│          │ SFT                    │ DPO                          │
├──────────┼────────────────────────┼──────────────────────────────┤
│ 信号类型 │ 只有"好回答" (模仿)    │ 好坏对比 (偏好对)            │
│ 损失函数 │ -log P(chosen)         │ -log σ(β·Δlog-ratio)         │
│ 坏回答   │ P 变化不可控 (附带效应)│ 明确压低 P(rejected)         │
│ 参考模型 │ 不需要                 │ 需要 (冻结, 算 log-ratio)    │
│ 模型数量 │ 1                      │ 2 (policy + ref)             │
│ 风险     │ 无法区分好坏           │ KL 爆炸 / reward hacking     │
│ 在pipeline│ 第一步: 学会格式       │ 第二步: 对齐偏好             │
│ 中的位置 │                        │                              │
└──────────┴────────────────────────┴──────────────────────────────┘

现代 LLM 后训练 pipeline:
  Pretrain → SFT (学会对话格式) → DPO/RLHF (对齐人类偏好)

下一步: test-time compute (CoT / Best-of-N / o1式长思考)
  → 不改参数, 只改推理策略, 用更多计算换更好输出
""")
P("实验完成。配套文档: 09-后训练-SFT对齐DPO-test-time.md")
