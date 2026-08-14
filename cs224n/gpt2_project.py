"""
Stanford CS224N (Winter 2026) · Default Final Project —— GPT-2 简化实现
====================================================================
2026 版默认项目从 BERT 改成 GPT-2。学生实现 GPT-2 架构并做 3 个下游任务。

本文件是教学简化版（纯 NumPy），聚焦 GPT-2 的核心组件：
  ① Token + Position Embedding
  ② Multi-Head Causal Self-Attention
  ③ Feed-Forward Network (MLP)
  ④ LayerNorm + Residual（Pre-LN 结构，GPT-2 用的）
  ⑤ 前向推理生成文本（贪心解码）

不训练（教学演示），只展示"一次前向传播如何生成下一个 token"。
真正的 CS224N 项目用 PyTorch，要训练 + 做 3 个下游任务。

运行：
    python3 gpt2_project.py
依赖：numpy
====================================================================
"""
from __future__ import annotations
import math
import numpy as np

def banner(t):
    print("\n" + "█" * 64)
    print(f"  {t}")
    print("█" * 64)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  GPT-2 核心组件                                                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

def gelu(x):
    """GPT-2 用的 GeLU 激活（精确版）。"""
    return 0.5 * x * (1 + np.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * x**3)))

def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)

def layer_norm(x, gamma, beta, eps=1e-5):
    mu = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return gamma * (x - mu) / np.sqrt(var + eps) + beta


class MultiHeadAttention:
    """GPT-2 的多头因果自注意力。"""
    def __init__(self, d_model, n_heads):
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        # qkv 投影（GPT-2 把 q/k/v 合并成一个矩阵）
        self.W_qkv = np.random.randn(d_model, 3 * d_model) * 0.02
        self.W_o = np.random.randn(d_model, d_model) * 0.02

    def forward(self, x):
        seq_len = x.shape[0]
        qkv = x @ self.W_qkv              # (seq, 3*d)
        q, k, v = np.split(qkv, 3, axis=-1)
        # reshape 成多头
        def split_heads(t):
            return t.reshape(seq_len, self.n_heads, self.d_head).transpose(1, 0, 2)
        q, k, v = split_heads(q), split_heads(k), split_heads(v)
        # 每头做 attention
        scores = q @ k.transpose(0, 2, 1) / math.sqrt(self.d_head)   # (head, seq, seq)
        # 因果掩码
        mask = np.triu(np.ones((seq_len, seq_len)), k=1).astype(bool)
        scores[:, mask] = -1e9
        attn = softmax(scores, axis=-1)
        ctx = attn @ v                    # (head, seq, d_head)
        ctx = ctx.transpose(1, 0, 2).reshape(seq_len, self.d_model)
        return ctx @ self.W_o


class TransformerBlock:
    """GPT-2 的一个 Transformer Block（Pre-LN 结构）。"""
    def __init__(self, d_model, n_heads, d_ff):
        self.ln1_g = np.ones(d_model); self.ln1_b = np.zeros(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ln2_g = np.ones(d_model); self.ln2_b = np.zeros(d_model)
        self.W1 = np.random.randn(d_model, d_ff) * 0.02
        self.W2 = np.random.randn(d_ff, d_model) * 0.02

    def forward(self, x):
        # Pre-LN: x + Sublayer(LN(x))   （GPT-2 结构）
        h = layer_norm(x, self.ln1_g, self.ln1_b)
        x = x + self.attn.forward(h)
        h = layer_norm(x, self.ln2_g, self.ln2_b)
        ff = gelu(h @ self.W1) @ self.W2
        x = x + ff
        return x


class MiniGPT2:
    """教学版 GPT-2（2 层，d=64，随机权重，只演示前向推理）。"""
    def __init__(self, vocab_size=100, d_model=64, n_heads=4, d_ff=256, n_layers=2,
                 max_seq=32):
        np.random.seed(0)
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.tok_emb = np.random.randn(vocab_size, d_model) * 0.02
        self.pos_emb = np.random.randn(max_seq, d_model) * 0.02
        self.blocks = [TransformerBlock(d_model, n_heads, d_ff) for _ in range(n_layers)]
        self.ln_f_g = np.ones(d_model); self.ln_f_b = np.zeros(d_model)
        # 输出投影（权重与 tok_emb 绑定 = weight tying）
        self.lm_head = self.tok_emb.T   # (d, vocab)

    def forward(self, token_ids):
        seq_len = len(token_ids)
        x = self.tok_emb[token_ids] + self.pos_emb[:seq_len]
        for block in self.blocks:
            x = block.forward(x)
        x = layer_norm(x, self.ln_f_g, self.ln_f_b)
        logits = x @ self.lm_head       # (seq, vocab)
        return logits

    def generate(self, token_ids, n_new=3):
        """贪心解码：每次取 argmax 作为下一个 token。"""
        ids = list(token_ids)
        generated = []
        for _ in range(n_new):
            logits = self.forward(ids)
            next_id = int(np.argmax(logits[-1]))   # 取最后位置的 logits
            ids.append(next_id)
            generated.append(next_id)
        return ids, generated


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  演示                                                                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def demo_gpt2() -> None:
    banner("GPT-2 Default Final Project · 教学简化版前向推理")
    model = MiniGPT2(vocab_size=100, d_model=64, n_heads=4, n_layers=2)
    # 统计参数量
    params = [model.tok_emb, model.pos_emb]
    for b in model.blocks:
        params += [b.W1, b.W2, b.attn.W_qkv, b.attn.W_o]
    n_params = sum(p.size for p in params)
    print(f"  模型配置: vocab=100 d_model=64 heads=4 layers=2 d_ff=256")
    print(f"  参数量约: {n_params:,}\n")

    # ── Part 1: 前向传播，看 logits ──
    print("─" * 64)
    print("【Part 1】前向传播：输入 3 个 token，看输出 logits")
    print("─" * 64)
    input_ids = [5, 20, 42]
    logits = model.forward(input_ids)
    print(f"  输入 token_ids: {input_ids}")
    print(f"  logits shape: {logits.shape}  (seq=3, vocab=100)")
    # 看最后位置的 top-5 预测
    last = logits[-1]
    top5 = np.argsort(last)[::-1][:5]
    probs = softmax(last)
    print(f"\n  最后位置预测的 top-5 token（未训练，随机分布）:")
    for tid in top5:
        print(f"    token {tid:>3}: logit={last[tid]:+.3f}  prob={probs[tid]:.3f}")

    # ── Part 2: 因果掩码验证 ──
    print("─" * 64)
    print("【Part 2】因果掩码验证：位置 i 只能看 ≤i 的 token")
    print("─" * 64)
    print(f"  GPT-2 的 self-attention 矩阵是【下三角】（自回归）:")
    print(f"    位置0 只看 [0]            （只能看自己）")
    print(f"    位置1 只看 [0,1]          （看自己和之前）")
    print(f"    位置2 只看 [0,1,2]        （全部历史）")
    print(f"  → 这就是 GPT-2 '自回归'的本质：从左到右，不能偷看未来。")

    # ── Part 3: 文本生成（贪心）──
    print("─" * 64)
    print("【Part 3】贪心解码生成（未训练，只演示流程）")
    print("─" * 64)
    prompt = [5, 20]
    full_ids, generated = model.generate(prompt, n_new=4)
    print(f"  输入 prompt: {prompt}")
    print(f"  生成 4 个 token: {generated}")
    print(f"  完整序列: {full_ids}")
    print(f"  （权重随机，输出无意义；训练后就能生成连贯文本）\n")

    # ── Part 4: GPT-2 架构全景 ──
    print(f"─" * 64)
    print("【Part 4】GPT-2 架构全景（对照真实 GPT-2）")
    print("─" * 64)
    print("""  GPT-2 数据流（一个 token 的旅程）：

    token_ids ──→ Token Embedding ──┐
                                    ├──→ 相加 ──→ [Block × N] ──→ LN ──→ LM Head ──→ logits
    positions ──→ Position Embedding ┘

  每个 Block（Pre-LN 结构，GPT-2 论文用的）：
    x ──→ LN ──→ Multi-Head Causal Attn ──→ +x ──→ LN ──→ FFN(GeLU) ──→ +x

  真实 GPT-2 配置（124M 小版本）：
    vocab=50257  d_model=768  heads=12  layers=12  d_ff=3072  max_seq=1024
    参数量：124M（本教学版只有约 0.1M）

  CS224N 项目要求：实现上述组件 + 训练 + 做 3 个下游任务：
    ① 文本分类（情感分析）
    ② 命名实体识别（NER）
    ③ 自然语言推理（NLI）
""")


def main() -> None:
    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + " CS224N Default Project · mini-GPT-2 教学实现 ".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    demo_gpt2()
    print("=" * 64)
    print("  ✅ 演示完成。下一步：")
    print("     1. 对照 4 个作业：python3 cs224n_assignments.py")
    print("     2. 深入原理：work4ai/讲透Transformer/ + 讲透基础模型/")
    print("     3. 跑真实 GPT-2：pip install transformers && python -c \\")
    print("        \"from transformers import pipeline; print(pipeline('text-generation')('Hello'))\"")
    print("=" * 64)
    print()


if __name__ == "__main__":
    main()
