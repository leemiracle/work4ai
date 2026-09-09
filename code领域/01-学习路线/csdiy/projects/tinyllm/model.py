#!/usr/bin/env python3
"""
tinyllm/model.py — Transformer 语言模型

参照：nanoGPT (Karpathy) / Attention Is All You Need / HF transformers
csdiy 对应：nanoGPT精读 + tinytransformer

组件：
  CausalSelfAttention — 因果多头注意力
  FeedForward         — 前馈网络 (2层MLP + GELU)
  TransformerBlock    — Pre-LN 残差块
  GPT                 — 完整 GPT 模型
"""
import math, random

def softmax_rows(matrix):
    mx = [max(row) for row in matrix]
    result = []
    for i, row in enumerate(matrix):
        exps = [math.exp(v - mx[i]) for v in row]
        s = sum(exps)
        result.append([e / s for e in exps])
    return result

class CausalSelfAttention:
    """因果多头自注意力（参照 nanoGPT §四 逐行精读）"""
    def __init__(self, d_model, n_heads):
        self.n_heads = n_heads; self.d_head = d_model // n_heads; self.d_model = d_model
        # QKV 合三为一（参照 nanoGPT §4.1）
        self.n_embd = d_model
        self.qkv_weight = [[random.gauss(0, 0.02) for _ in range(3 * d_model)] for _ in range(d_model)]
        self.proj_weight = [[random.gauss(0, 0.02) for _ in range(d_model)] for _ in range(d_model)]
    def _matmul(self, A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
    def forward(self, x):
        seq = len(x)
        qkv = self._matmul(x, self.qkv_weight)  # [seq, 3*d]
        Q, K, V = [row[:self.d_model] for row in qkv], [row[self.d_model:2*self.d_model] for row in qkv], [row[2*self.d_model:] for row in qkv]
        # 逐头计算（简化版，不拆维度）
        scores = self._matmul(Q, [[K[j][i] for j in range(seq)] for i in range(self.d_model)])  # [seq, seq]
        # 缩放
        scores = [[s / math.sqrt(self.d_model) for s in row] for row in scores]
        # 因果 mask（参照 nanoGPT §4.3）
        for i in range(seq):
            for j in range(i + 1, seq): scores[i][j] = -1e9
        attn = softmax_rows(scores)
        # 加权求和 V
        out = self._matmul(attn, V)
        # 输出投影
        return self._matmul(out, self.proj_weight)

class FeedForward:
    """前馈网络（参照 nanoGPT §五）"""
    def __init__(self, d_model, d_ff=None):
        d_ff = d_ff or 4 * d_model
        self.w1 = [[random.gauss(0, 0.02) for _ in range(d_ff)] for _ in range(d_model)]  # [d_model][d_ff]
        self.w2 = [[random.gauss(0, 0.02) for _ in range(d_model)] for _ in range(d_ff)]  # [d_ff][d_model]
    def _matmul(self, A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
    @staticmethod
    def _gelu(x): return [0.5 * v * (1 + math.tanh(math.sqrt(2 / math.pi) * (v + 0.044715 * v ** 3))) for v in x]
    def forward(self, x):
        h = self._matmul(x, self.w1)  # [seq, d_ff]
        h = [self._gelu(row) for row in h]  # GELU
        return self._matmul(h, self.w2)  # [seq, d_model]

class TransformerBlock:
    """Pre-LN 残差块（参照 nanoGPT §六）"""
    def __init__(self, d_model, n_heads, d_ff=None):
        self.attn = CausalSelfAttention(d_model, n_heads)
        self.ff = FeedForward(d_model, d_ff)
        self.ln1_gamma = [1.0] * d_model; self.ln1_beta = [0.0] * d_model
        self.ln2_gamma = [1.0] * d_model; self.ln2_beta = [0.0] * d_model
    def _layernorm(self, x, gamma, beta, eps=1e-5):
        m = sum(x) / len(x); v = sum((xi - m) ** 2 for xi in x) / len(x)
        return [(xi - m) / math.sqrt(v + eps) * g + b for xi, g, b in zip(x, gamma, beta)]
    def forward(self, x):
        ln1 = [self._layernorm(row, self.ln1_gamma, self.ln1_beta) for row in x]
        attn_out = self.attn.forward(ln1)
        x = [[x[i][j] + attn_out[i][j] for j in range(len(x[0]))] for i in range(len(x))]
        ln2 = [self._layernorm(row, self.ln2_gamma, self.ln2_beta) for row in x]
        ff_out = self.ff.forward(ln2)
        return [[x[i][j] + ff_out[i][j] for j in range(len(x[0]))] for i in range(len(x))]

class GPT:
    """完整 GPT 模型（参照 nanoGPT §七）"""
    def __init__(self, vocab_size=256, d_model=64, n_heads=4, n_layers=2, max_seq=128):
        self.vocab_size = vocab_size; self.d_model = d_model; self.max_seq = max_seq
        # 词嵌入 + 位置嵌入
        self.tok_emb = [[random.gauss(0, 0.02) for _ in range(d_model)] for _ in range(vocab_size)]
        self.pos_emb = [[random.gauss(0, 0.02) for _ in range(d_model)] for _ in range(max_seq)]
        # Transformer 层
        self.blocks = [TransformerBlock(d_model, n_heads) for _ in range(n_layers)]
        # 最终 LayerNorm
        self.ln_f_gamma = [1.0] * d_model; self.ln_f_beta = [0.0] * d_model
        # Weight Tying（参照 nanoGPT §7.1）
        self.lm_head = self.tok_emb
    def forward(self, token_ids):
        x = [[self.tok_emb[tid][j] + self.pos_emb[i][j] for j in range(self.d_model)]
             for i, tid in enumerate(token_ids)]
        for block in self.blocks:
            x = block.forward(x)
        m = sum(self.ln_f_gamma) / len(self.ln_f_gamma)
        x = [[(v - m) * g + b for v, g, b in zip(row, self.ln_f_gamma, self.ln_f_beta)] for row in x]
        logits = [[sum(row[j] * self.lm_head[v][j] for j in range(self.d_model)) for v in range(self.vocab_size)] for row in x]
        return logits
    def param_count(self):
        tok = self.vocab_size * self.d_model; pos = self.max_seq * self.d_model
        block = sum(self._block_params(b) for b in self.blocks)
        return tok + pos + block + self.vocab_size * self.d_model  # +lm_head(=tok, tied)
    @staticmethod
    def _block_params(b):
        attn = 3 * b.attn.d_model * b.attn.d_model + b.attn.d_model ** 2
        ff = len(b.ff.w1) * len(b.ff.w1[0]) + len(b.ff.w2) * len(b.ff.w2[0])
        ln = 4 * b.attn.d_model; return attn + ff + ln
