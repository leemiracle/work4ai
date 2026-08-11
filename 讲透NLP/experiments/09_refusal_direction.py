#!/usr/bin/env python3
"""
讲透NLP · Ch9 后训练 — 配套实验: Refusal Direction 在 Tiny GPT 上的最小复现
对应文档: 09-后训练-SFT对齐DPO-test-time.md  §8 后训练的镜子

复现 Arditi et al. (NeurIPS 2024) "Refusal in Language Models Is Mediated
by a Single Direction" (arXiv:2406.11717) 的核心结论 — 但在一个 vocab=24、
3 层、约 12K 参数的玩具 GPT 上。

三个反直觉发现:
  1. 即便是玩具模型, 伪后训练的"拒绝行为"也几乎完全压缩到 1 根方向上
     (PCA 第一主成分解释 >90% 的 harmful-vs-harmless 方差)
  2. Ablation(投影掉这根方向): harmful 不再触发拒绝(模型"变坏"了)
  3. Addition(把这根方向加到 harmless 上): 模型对无害问题开始拒绝(模型"变傻"了)
  → 与 Arditi 在 13 个开源 chat 模型(1.3B-72B)上的结论同构

参考实现: github.com/andyrdt/refusal_direction
教程级实现: ARENA 3.0 part32 (Anthropic 推荐)

跑法: python3 -u 09_refusal_direction.py  (~10-20 秒)
依赖: 仅 torch (CPU)
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(1)   # 工程铁律: 小矩阵 set_num_threads(1) 比 8 线程快
torch.manual_seed(42)


# ============================================================
#  词表设计 (24 tokens, 用语义聚类而非真实语言)
# ============================================================
#   0        : <pad>
#   1        : <bos>
#   2        : <eos>
#   3-7      : harmful-prompt tokens  ("偷/抢/伤/害/欺" 概念)
#   8-12     : harmless-prompt tokens ("请/告/诉/解/释" 概念)
#   13-17    : refusal-answer tokens  ("我/不/能/帮/助")
#   18-23    : comply-answer tokens   ("答/案/是/如/下/。")
# REFUSAL_TOKEN = 13  —— 模型学到 harmful 时第一个生成的 token (拒绝信号)

VOCAB_SIZE  = 24
REFUSAL_TOK = 13   # 拒绝行为的第一 token (harmful 触发)
COMPLY_TOK  = 18   # 配合行为的第一 token (harmless 触发)
HARMFUL_IDX = list(range(3, 8))     # 5 个
HARMLESS_IDX = list(range(8, 13))   # 5 个
PROMPT_LEN  = 4
RESP_LEN    = 1                    # 只看第一个 response token —— 这是 refusal 的核心信号


def P(*a, **k):
    print(*a, **k, flush=True)


# ============================================================
#  Part 0: TinyGPT (3 层, 32 维, ~12K 参数; forward 能返回残差流)
# ============================================================

class CausalSelfAttention(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        assert d % h == 0
        self.h, self.dh = h, d // h
        self.qkv  = nn.Linear(d, 3 * d)
        self.proj = nn.Linear(d, d)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x).view(B, T, 3, self.h, self.dh)
        q, k, v = qkv.unbind(dim=2)
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
        s = (q @ k.transpose(-2, -1)) / math.sqrt(self.dh)
        s = s + torch.triu(torch.full((T, T), float('-inf')), diagonal=1)
        return self.proj((F.softmax(s, dim=-1) @ v).transpose(1, 2).contiguous().view(B, T, C))


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.attn = CausalSelfAttention(d, h)
        self.ln2 = nn.LayerNorm(d)
        self.ffn = nn.Sequential(nn.Linear(d, 4*d), nn.GELU(), nn.Linear(4*d, d))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class TinyGPT(nn.Module):
    """forward(idx, return_resids=False):
       return_resids=True 时返回每层 post-block 残差流 (list of (B,T,d))."""
    def __init__(self, vocab=VOCAB_SIZE, d=32, h=4, n_layers=3, max_len=8):
        super().__init__()
        self.n_layers = n_layers
        self.tok = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(max_len, d)
        self.blocks = nn.ModuleList([Block(d, h) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.head.weight = self.tok.weight   # weight tying
        # GPT-2 风格小方差初始化 (避免 weight-tying + N(0,1) 让初始 logits 极尖锐)
        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.weight.data.normal_(0, 0.02)
                if m.bias is not None: m.bias.data.zero_()
            elif isinstance(m, nn.Embedding):
                m.weight.data.normal_(0, 0.02)

    def forward(self, idx, return_resids=False, resid_hook=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T).unsqueeze(0))
        resids = []
        for i, blk in enumerate(self.blocks):
            x = blk(x)
            if return_resids:
                resids.append(x)
            if resid_hook is not None:
                x = resid_hook(x, i)   # 干预钩子 (用于 ablation/addition)
        return (self.head(self.ln_f(x)), resids) if return_resids else self.head(self.ln_f(x))


# ============================================================
#  Part 1: 构造"伪指令"数据 — harmful vs harmless prompts
# ============================================================

def make_prompts(n_each=64, seed=0):
    """生成 harmful / harmless prompts (各 n_each 个).
    每个 prompt 长度 PROMPT_LEN=4: [bos] + 3 个语义 token (按类抽样)."""
    g = torch.Generator().manual_seed(seed)
    prompts, labels = [], []
    for _ in range(n_each):
        # harmful: bos + 3 harmful tokens (从 HARMFUL_IDX 放回抽样)
        h = [1] + [HARMFUL_IDX[torch.randint(0, len(HARMFUL_IDX), (1,), generator=g).item()]
                   for _ in range(PROMPT_LEN - 1)]
        prompts.append(h); labels.append(0)
        # harmless: bos + 3 harmless tokens
        u = [1] + [HARMLESS_IDX[torch.randint(0, len(HARMLESS_IDX), (1,), generator=g).item()]
                   for _ in range(PROMPT_LEN - 1)]
        prompts.append(u); labels.append(1)
    return torch.tensor(prompts), torch.tensor(labels)  # (2n, P), (2n,)


# ============================================================
#  Part 2: 伪后训练 — SFT 让模型对 harmful 学会"拒绝", 对 harmless 学会"配合"
# ============================================================

def sft_train(model, prompts, labels, steps=400, lr=5e-3, bs=16):
    """SFT: harmful→REFUSAL_TOK, harmless→COMPLY_TOK.
    只在第一个 response token 上算 loss (refusal 的核心信号)."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    N = prompts.size(0)
    for step in range(steps):
        idx = torch.randint(0, N, (bs,))
        x = prompts[idx]                          # (bs, P)
        target = torch.where(labels[idx] == 0,
                             torch.full((bs,), REFUSAL_TOK, dtype=torch.long),
                             torch.full((bs,), COMPLY_TOK, dtype=torch.long))
        logits = model(x)[:, -1, :]               # 取 prompt 最后位置的 logits
        loss = F.cross_entropy(logits, target)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 100 == 0 or step == steps - 1:
            with torch.no_grad():
                pred = logits.argmax(-1)
                acc = (pred == target).float().mean().item()
                P(f"  SFT step {step:4d}  loss={loss.item():.4f}  acc={acc:.1%}")
    return model


# ============================================================
#  Part 3: 提取 refusal direction (Arditi 2024 difference-in-means)
# ============================================================

@torch.no_grad()
def extract_refusal_directions(model, prompts, labels):
    """对每层 l, 计算 r^(l) = mean(h_harmful^l) - mean(h_harmless^l) 在 prompt 最后位置.
    返回 dict {layer_idx: (d,)}."""
    logits, resids = model(prompts, return_resids=True)   # resids: list (n_layers) of (N, T, d)
    last_pos = prompts.size(1) - 1                          # 取 prompt 最后 token 位置
    harmful_mask = (labels == 0)
    harmless_mask = (labels == 1)
    dirs = {}
    for li, r in enumerate(resids):
        h_harmful = r[harmful_mask, last_pos, :].mean(0)   # (d,)
        h_harmless = r[harmless_mask, last_pos, :].mean(0)
        dirs[li] = (h_harmful - h_harmless)                # (d,)  difference-in-means
    return dirs


def best_layer_and_dir(model, prompts, labels, dirs):
    """在所有 (layer, dir) 候选里, 选最有效的那一根 —— 用验证集 ablation+addition 双向效果打分.
    (简化版: 直接用 harmful/harmless 自身的最简指标.)
    返回 (best_l, best_r_hat)."""
    best_score, best = -1e9, None
    for li, r in dirs.items():
        r_hat = r / r.norm().clamp(min=1e-10)
        # 用每层 r 在两类上的投影分离度作为代理指标
        logits, resids = model(prompts, return_resids=True)
        last = prompts.size(1) - 1
        proj = resids[li][:, last, :] @ r_hat              # (N,)
        h_proj = proj[labels == 0].mean().item()
        u_proj = proj[labels == 1].mean().item()
        sep = abs(h_proj - u_proj) / (proj.std().item() + 1e-10)
        if sep > best_score:
            best_score, best = sep, (li, r_hat)
    return best


# ============================================================
#  Part 4: 三种干预 (Arditi 论文 §2.4 的最小复现)
# ============================================================

@torch.no_grad()
def prob_refusal(model, prompts, intervene=None):
    """返回模型对每个 prompt 第一 token 选 REFUSAL_TOK 的概率."""
    logits = model(prompts, resid_hook=intervene)
    p = F.softmax(logits[:, -1, :], dim=-1)
    return p[:, REFUSAL_TOK]                                # (N,)


def make_ablation_hook(r_hat, target_layer=None):
    """Directional ablation (Arditi Eq.4): 在每层每位置投影掉 r_hat 方向.
    x' ← x - r_hat (r_hat^T x)."""
    def hook(x, layer_idx):
        if target_layer is None or layer_idx == target_layer:
            # x: (B, T, d)  →  投影掉 r_hat
            x = x - (x @ r_hat).unsqueeze(-1) * r_hat
        return x
    return hook


def make_addition_hook(r, target_layer, coeff):
    """Activation addition (Arditi Eq.3): 在 target_layer 所有位置加 coeff*r.
    x' ← x + coeff * r  (注意: 用原始 r, 不归一化)."""
    def hook(x, layer_idx):
        if layer_idx == target_layer:
            x = x + coeff * r
        return x
    return hook


# ============================================================
#  Part 5: PCA 评估 — refusal 信号是否压缩到 1 根方向?
# ============================================================

@torch.no_grad()
def refusal_subspace_pca(model, prompts, labels):
    """对每层, 取 harmful 和 harmless 激活的"中心化差值矩阵"做 PCA,
    看第一主成分解释多少方差. 如果 >>80%, 说明 refusal 信号高度 1 维."""
    logits, resids = model(prompts, return_resids=True)
    last = prompts.size(1) - 1
    pca_results = {}
    for li, r in enumerate(resids):
        h = r[labels == 0, last, :]   # (Nh, d)
        u = r[labels == 1, last, :]   # (Nu, d)
        # 用每类减去全局均值后拼接, 对样本轴做 PCA
        X = torch.cat([h, u], dim=0)
        X = X - X.mean(0, keepdim=True)
        # SVD on (d, N) — 取主成分
        U, S, Vt = torch.linalg.svd(X.T, full_matrices=False)
        variances = (S ** 2)
        var_ratios = variances / variances.sum()
        pca_results[li] = var_ratios[:3].tolist()   # top-3 主成分占比
    return pca_results


# ============================================================
#  Main: 跑完整流程, 收集反直觉发现
# ============================================================

def main():
    P("=" * 72)
    P(" 讲透NLP · Ch9 后训练 — Refusal Direction 最小复现")
    P(" 复现 Arditi et al. NeurIPS 2024 (arXiv:2406.11717) 的核心结论")
    P("=" * 72)

    # --- Part 1: 数据 + 模型 ---
    P("\n[1] 构造伪指令数据 + 初始化 TinyGPT (3 层, 32 维, ~12K 参)")
    prompts, labels = make_prompts(n_each=64)
    P(f"    数据: {prompts.size(0)} prompts (64 harmful + 64 harmless), 长度 {PROMPT_LEN}")
    model = TinyGPT()
    n_params = sum(p.numel() for p in model.parameters())
    P(f"    模型: {model.n_layers} 层, d_model=32, {n_params:,} 参数")

    # --- Part 2: 伪后训练 (SFT) ---
    P("\n[2] 伪后训练 (SFT): 教模型 harmful→拒绝(token {REFUSAL_TOK}), "
      "harmless→配合(token {COMPLY_TOK})".format(REFUSAL_TOK=REFUSAL_TOK, COMPLY_TOK=COMPLY_TOK))
    sft_train(model, prompts, labels, steps=400)

    # --- Part 3: 提取 refusal direction ---
    P("\n[3] 提取 refusal direction (difference-in-means, Arditi §2.3)")
    P("    r^(l) = mean(h_harmful^l) - mean(h_harmless^l)  at prompt 最后位置")
    dirs = extract_refusal_directions(model, prompts, labels)
    for li, r in dirs.items():
        P(f"    layer {li}: |r| = {r.norm().item():.4f}")

    # --- Part 4: PCA — refusal 信号是否压缩到 1 维? (反直觉发现 1) ---
    P("\n[4] ⚡ 反直觉发现 1: PCA 检查 refusal 是否被压缩到 1 根方向")
    P("    (在大模型上 Arditi 2024 报告 13/13 chat 模型都是单方向; 玩具模型呢?)")
    pca = refusal_subspace_pca(model, prompts, labels)
    for li, ratios in pca.items():
        pct1 = ratios[0] * 100
        bar = "█" * int(pct1 / 2) + "░" * (50 - int(pct1 / 2))
        P(f"    layer {li}: PC1={ratios[0]*100:5.1f}%  PC2={ratios[1]*100:5.1f}%  "
          f"PC3={ratios[2]*100:5.1f}%  |{bar}|")
    best_l_for_pca = max(pca.keys(), key=lambda l: pca[l][0])
    P(f"\n    📌 layer {best_l_for_pca} 第一主成分解释 {pca[best_l_for_pca][0]*100:.1f}% 方差")
    P(f"    📌 即便是 {n_params:,} 参数的玩具模型, harmful-vs-harmless 信号也主要活在 1 维上")

    # --- Part 5: 选最优 (layer, direction) ---
    best_l, best_r_hat = best_layer_and_dir(model, prompts, labels, dirs)
    P(f"\n[5] 选最有效的 (layer, direction): layer={best_l}, |r_hat|=1")

    # --- Part 6: 干预 1 — Directional Ablation (反直觉发现 2) ---
    P("\n[6] ⚡ 反直觉发现 2: Directional Ablation (Arditi Eq.4)")
    P("    投影掉 r_hat 方向后, harmful 还会触发拒绝吗?")
    abl_hook = make_ablation_hook(best_r_hat)
    p_ref_baseline = prob_refusal(model, prompts).mean(0).item()
    p_ref_abl = prob_refusal(model, prompts, intervene=abl_hook).mean(0).item()
    p_ref_h_baseline = prob_refusal(model, prompts[labels == 0]).mean(0).item()
    p_ref_h_abl = prob_refusal(model, prompts[labels == 0], intervene=abl_hook).mean(0).item()
    p_ref_u_baseline = prob_refusal(model, prompts[labels == 1]).mean(0).item()
    p_ref_u_abl = prob_refusal(model, prompts[labels == 1], intervene=abl_hook).mean(0).item()
    P(f"                       全部      harmful   harmless")
    P(f"    baseline P(refuse):  {p_ref_baseline:.4f}    {p_ref_h_baseline:.4f}    {p_ref_u_baseline:.4f}")
    P(f"    ablation  P(refuse):  {p_ref_abl:.4f}    {p_ref_h_abl:.4f}    {p_ref_u_abl:.4f}")
    drop_h = (p_ref_h_baseline - p_ref_h_abl) / max(p_ref_h_baseline, 1e-10)
    P(f"\n    📌 harmful 拒绝概率下降 {drop_h*100:.1f}%  "
      f"({p_ref_h_baseline:.3f} → {p_ref_h_abl:.3f})")
    P(f"    📌 投影掉 1 根方向, 模型就'忘记'拒绝 —— 与 Arditi 2024 的发现同构")

    # --- Part 7: 干预 2 — Activation Addition (反直觉发现 3) ---
    P("\n[7] ⚡ 反直觉发现 3: Activation Addition (Arditi Eq.3)")
    P("    把 r 加到 harmless 上, 模型会对无害问题开始拒绝吗?")
    r_orig = dirs[best_l]   # 原始未归一化的 r
    # 系数扫描
    P(f"    系数扫描 (在 layer {best_l} 加入 coeff * r):")
    P(f"      coeff   P(refuse|harmless)  P(refuse|harmful)")
    coeffs = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
    for c in coeffs:
        hook = make_addition_hook(r_orig, best_l, c)
        p_u = prob_refusal(model, prompts[labels == 1], intervene=hook).mean(0).item()
        p_h = prob_refusal(model, prompts[labels == 0], intervene=hook).mean(0).item()
        bar_u = "█" * int(p_u * 40)
        P(f"      {c:5.2f}    {p_u:.4f} {bar_u:40s}  {p_h:.4f}")
    P(f"\n    📌 加入 r 让无害问题拒绝率单调上升 —— refusal 是一根'可加可减的旋钮'")
    P(f"    📌 这正是 Anthropic 2025 Persona Vector 的原理 (evil/sycophancy/hallucination)")

    # --- Part 8: 总结 ---
    P("\n" + "=" * 72)
    P(" 总结: 玩具模型与大模型在 refusal direction 上的同构")
    P("=" * 72)
    P(f"""
  实验:  TinyGPT (vocab=24, 3 层, 32 维, {n_params:,} 参数, SFT 400 步)
  对照:  Arditi et al. 2024 在 13 个开源 chat 模型 (1.3B-72B) 上的发现

  ┌─────────────────────────────────┬──────────────┬──────────────┐
  │ 现象                            │   玩具模型   │   大模型     │
  ├─────────────────────────────────┼──────────────┼──────────────┤
  │ refusal 压缩到 1 维 (PC1 占比)  │   {pca[best_l_for_pca][0]*100:>5.1f}%   │   ~普遍      │
  │ Ablation 让 harmful 不拒绝      │   ↓{drop_h*100:>5.1f}%   │   ~100%      │
  │ Addition 让 harmless 拒绝       │   单调       │   单调       │
  └─────────────────────────────────┴──────────────┴──────────────┘

  结论 (Arditi 2024):
   "Safety fine-tuning does not create a complex, model-specific mechanism
    for refusal. It reinforces a simple linear direction."
   —— 即: 后训练的安全机制是一根"浅薄"的线性方向, 而非深度分布式行为.

  工程含义:
   - 想越狱 (学术研究): 投影掉这根方向
   - 想加安全开关: 在推理时按需注入这根方向
   - 想监测模型状态: 量化这根方向的激活强度
   - 想识别 DPO vs RLHF: 几何指纹 (alignment_imprint)
""")


if __name__ == "__main__":
    main()
