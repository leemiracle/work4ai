"""
讲透 Transformer —— 综合实验脚本
=================================
3 个递进实验, 从核心组件到完整系统:
  实验1: 手写 Self-Attention (numpy) —— 证明"就是几个矩阵乘法"
  实验2: 注意力热力图 —— 直观看到"哪个词关注哪个词"
  实验3: mini-GPT (PyTorch) —— ~100 行搭一个真 GPT, 训练 + 生成

跑法: python3 transformer_overview.py
核心洞察: Transformer = Self-Attention(全局视野) + 并行计算 + 残差/归一化让堆叠可训练
"""
import numpy as np
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
torch.manual_seed(0)

# ============================================================
# 实验 1: 手写 Self-Attention (纯 numpy)
# ============================================================
print("=" * 72)
print("实验 1: 手写 Self-Attention  (纯 numpy, 证明就是矩阵乘法)")
print("=" * 72)

seq_len, d_model = 4, 8          # 4 个词, 每词 8 维嵌入
X = np.random.randn(seq_len, d_model)
print(f"输入 X (词嵌入): shape = {X.shape}  ({seq_len} 个词, 每个 {d_model} 维)\n")

# 三个可学习权重矩阵: 把 X 投影成 Q, K, V
W_Q = np.random.randn(d_model, d_model)
W_K = np.random.randn(d_model, d_model)
W_V = np.random.randn(d_model, d_model)

Q = X @ W_Q                      # (4,8) @ (8,8) = (4,8)
K = X @ W_K
V = X @ W_V
print(f"Q = X @ W_Q : {Q.shape}   (Query: 我在找什么?)")
print(f"K = X @ W_K : {K.shape}   (Key:   我有什么可被找?)")
print(f"V = X @ W_V : {V.shape}   (Value: 找到我, 给你什么信息?)\n")

# 注意力核心公式: softmax(Q @ K^T / sqrt(d_k)) @ V
d_k = d_model
scores = Q @ K.T                 # (4,4) 每个词对所有词的"匹配分数"
print(f"1. scores = Q @ K.T          : {scores.shape}  (4词两两的相似度)")

scores_scaled = scores / math.sqrt(d_k)
print(f"2. scores / sqrt(d_k={d_k})   : 除以 sqrt(d_k)={math.sqrt(d_k):.2f} 控制数值范围")

# softmax (沿行, 每个词对所有人的注意力权重和=1)
def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True))   # 减最大值防溢出 = logsumexp 技巧!
    return e / e.sum(axis=axis, keepdims=True)
weights = softmax(scores_scaled, axis=-1)
print(f"3. weights = softmax(scores): {weights.shape}  (每行和={weights.sum(axis=-1)[0]:.4f})")
print(f"   第 0 个词的注意力分配: {[round(w,3) for w in weights[0]]}\n")

output = weights @ V
print(f"4. output = weights @ V      : {output.shape}  ← 这就是 Self-Attention 的输出!")
print(f"\n==> 整个 Self-Attention = 上面 4 步, 本质就是矩阵乘法 + softmax\n")

# 验证: 用 PyTorch 对照
X_t = torch.tensor(X, dtype=torch.float32)
attn_t = F.scaled_dot_product_attention(
    torch.tensor(Q), torch.tensor(K), torch.tensor(V))
print(f"PyTorch 验证: 最大差异 = {np.abs(output - attn_t.numpy()).max():.2e}  (一致!)\n")

# 为什么除以 sqrt(d_k)? —— 演示不除会怎样
print("为什么除以 sqrt(d_k)?")
d_large = 512
Q_big = np.random.randn(seq_len, d_large); K_big = np.random.randn(seq_len, d_large)
raw = Q_big @ K_big.T
print(f"  d_k=512 时, 裸 QK^T 的标准差 = {raw.std():.1f}  (softmax 会变成近乎 one-hot!)")
print(f"  除以 sqrt(512)={math.sqrt(512):.1f} 后      = {(raw/math.sqrt(d_large)).std():.1f}  (softmax 平滑)")
print(f"  ==> 不除 sqrt(d_k): softmax 梯度趋于 0, 训练不动 (和你学的损失函数课有关)\n")


# ============================================================
# 实验 2: 注意力热力图 (可视化"注意力")
# ============================================================
print("=" * 72)
print("实验 2: 注意力热力图  (一个句子, 看每个词关注谁)")
print("=" * 72)

# 用一个有教学意义的句子, 每个词一个随机嵌入, 训练一点点让 attention 有意义
sentence = ["The", "cat", "sat", "on", "the", "mat", "because", "it", "was", "tired"]
seq2 = len(sentence)
d2 = 16
np.random.seed(42)
emb = np.random.randn(seq2, d2)
W_Q2 = np.random.randn(d2, d2) * 0.5
W_K2 = np.random.randn(d2, d2) * 0.5
W_V2 = np.random.randn(d2, d2) * 0.5

Q2 = emb @ W_Q2; K2 = emb @ W_K2; V2 = emb @ W_V2
scores2 = Q2 @ K2.T / math.sqrt(d2)
weights_full = softmax(scores2, axis=-1)        # 完整 attention (Encoder 风格)

# causal mask (GPT 风格: 每个词只能看前面的词)
mask = np.triu(np.ones((seq2, seq2)), k=1).astype(bool)   # 上三角 = True = 屏蔽
scores_masked = scores2.copy()
scores_masked[mask] = -np.inf
weights_causal = softmax(scores_masked, axis=-1)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
for ax, W, title in zip(axes, [weights_full, weights_causal],
                        ["Full Self-Attention (Encoder, e.g. BERT)\nevery word sees all words",
                         "Causal Self-Attention (Decoder, e.g. GPT)\neach word sees only past words"]):
    im = ax.imshow(W, cmap="Blues", aspect="auto", vmin=0, vmax=W.max())
    ax.set_xticks(range(seq2)); ax.set_xticklabels(sentence, rotation=45, ha="right", fontsize=10)
    ax.set_yticks(range(seq2)); ax.set_yticklabels(sentence, fontsize=10)
    ax.set_xlabel("attended to (Key)"); ax.set_ylabel("query (Query)")
    ax.set_title(title, fontsize=11)
    for i in range(seq2):
        for j in range(seq2):
            ax.text(j, i, f"{W[i,j]:.2f}", ha="center", va="center",
                    color="white" if W[i,j] > W.max()*0.6 else "black", fontsize=7)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.tight_layout()
fig.savefig("attention_heatmap.png", dpi=110)
print(f"  句子: {' '.join(sentence)}")
print(f"  左图: 全连接 attention (BERT 风格, 每个词看到所有词)")
print(f"  右图: causal mask (GPT 风格, 上三角屏蔽, 只能看前面的词)")
print(f"  ==> 图存 attention_heatmap.png\n")


# ============================================================
# 实验 3: mini-GPT (PyTorch) —— ~100 行搭一个真 GPT
# ============================================================
print("=" * 72)
print("实验 3: mini-GPT  (PyTorch, 字符级, 训练 + 生成)")
print("=" * 72)

# 语料: 关于 transformer 的英文, 字符级建模
text = ("the transformer is a neural network architecture that relies entirely "
        "on self attention to compute representations of its input output sequence "
        "the transformer was introduced in 2017 and uses attention instead of recurrence "
        "it enables parallel training and long range dependency modeling across tokens ")
text = text * 4                                              # 重复扩充数据量
chars = sorted(set(text))
vocab_size = len(chars)
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in text], dtype=torch.long)
print(f"语料长度: {len(data)} 字符,  词表大小: {vocab_size}")
print(f"前 60 字符: '{text[:60]}'\n")


class MiniGPT(nn.Module):
    """~80 行的真 GPT (nanoGPT 极简版)"""
    def __init__(self, vocab_size, d_model=64, n_head=4, n_layer=2, block_size=48):
        super().__init__()
        self.block_size = block_size
        # 1. 嵌入层: token 嵌入 + 位置嵌入 (这就是 Positional Encoding 的可学习版)
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Parameter(torch.zeros(1, block_size, d_model))
        # 2. N 个 Transformer Block
        self.blocks = nn.ModuleList([TransformerBlock(d_model, n_head) for _ in range(n_layer)])
        # 3. 输出层 (logits)
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok_emb(idx) + self.pos_emb[:, :T, :]      # token + 位置
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, vocab_size), targets.view(-1))
        return logits, loss


class TransformerBlock(nn.Module):
    """每个 Block = Causal Self-Attention + FFN, 各带残差 + LayerNorm"""
    def __init__(self, d_model, n_head):
        super().__init__()
        self.n_head = n_head
        self.ln1 = nn.LayerNorm(d_model)
        # Q/K/V 投影 (手写, 你在实验1 学过的!)
        self.q = nn.Linear(d_model, d_model)
        self.k = nn.Linear(d_model, d_model)
        self.v = nn.Linear(d_model, d_model)
        self.proj = nn.Linear(d_model, d_model)
        self.ln2 = nn.LayerNorm(d_model)
        # FFN: 两层线性 + 激活函数 (你学过的 GELU!)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4), nn.GELU(), nn.Linear(d_model * 4, d_model))

    def forward(self, x):
        B, T, C = x.shape
        h = self.ln1(x)
        # 拆成多头: (B,T,C) -> (B, n_head, T, C/n_head)
        q = self.q(h).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        k = self.k(h).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = self.v(h).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        # Causal Self-Attention: SDPA 优化实现, is_causal=True 自动屏蔽未来
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        a = a.transpose(1, 2).contiguous().view(B, T, C)    # 合并多头
        x = x + self.proj(a)                                # 残差连接
        x = x + self.ffn(self.ln2(x))                       # FFN + 残差
        return x


# 训练
block_size = 48
model = MiniGPT(vocab_size, d_model=64, n_head=4, n_layer=2, block_size=block_size)
n_params = sum(p.numel() for p in model.parameters())
print(f"模型参数量: {n_params:,}  (d_model=64, 4 头, 2 层)")
print(f"组件: tok_emb + pos_emb + 2x(Attention+FFN) + LN + head")
print(f"激活: GELU  |  损失: CrossEntropy  |  优化器: Adam  ← 三件套全用上!\n")

opt = torch.optim.Adam(model.parameters(), lr=3e-3)
losses = []
print("训练 next-token prediction (用你学的交叉熵损失):")
print(f"{'步数':>6} | {'loss':>8} | {'进度':>10}")
print("-" * 34)
for step in range(201):
    ix = torch.randint(0, len(data) - block_size - 1, (24,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    logits, loss = model(x, y)
    opt.zero_grad()
    loss.backward()
    opt.step()
    losses.append(loss.item())
    if step % 100 == 0 or step == 200:
        bar = "#" * int(loss.item() / 5 * 10)
        print(f"{step:>6} | {loss.item():>8.4f} | {bar}")

# 生成样本
print("\n生成样本 (温度=0.7, 从训练好的模型采样):")
model.eval()
with torch.no_grad():
    context = torch.tensor([[stoi['t']]])                   # 从 't' 开始
    for temp in [0.3, 1.0]:
        ctx = context.clone()
        for _ in range(50):
            x = ctx[:, -block_size:]
            logits, _ = model(x)
            probs = F.softmax(logits[0, -1] / temp, dim=0)   # 温度控制随机性
            next_id = torch.multinomial(probs, 1).unsqueeze(0)
            ctx = torch.cat([ctx, next_id], dim=1)
        gen = "".join(itos[i.item()] for i in ctx[0])
        print(f"  temp={temp}: \"{gen}\"")

# 训练曲线
fig2, ax2 = plt.subplots(figsize=(11, 5))
ax2.plot(losses, color="#377eb8", linewidth=1)
ax2.set_xlabel("training step"); ax2.set_ylabel("cross-entropy loss")
ax2.set_title(f"mini-GPT training ({n_params:,} params, char-level)\n"
              f"loss: {losses[0]:.3f} -> {losses[-1]:.3f}")
ax2.grid(alpha=0.3); ax2.axhline(losses[-1], color="red", linestyle="--", alpha=0.5)
fig2.tight_layout()
fig2.savefig("mini_gpt_training.png", dpi=110)

print(f"\n==> 训练曲线存 mini_gpt_training.png")
print(f"loss 从 {losses[0]:.3f} 降到 {losses[-1]:.3f}")
print(f"理论随机猜测 loss = ln({vocab_size}) = {math.log(vocab_size):.3f}")
print(f"==> 模型学到了字符级语言规律!\n")

print("=" * 72)
print("全部 3 个实验完成! 产物:")
print("  attention_heatmap.png    - 注意力热力图 (Encoder vs Decoder)")
print("  mini_gpt_training.png    - mini-GPT 训练曲线")
print("=" * 72)
print("\n关键回顾 (你学的三件套如何组装成 Transformer):")
print("  激活函数  -> FFN 里的 GELU")
print("  损失函数  -> next-token 的 CrossEntropy")
print("  优化器    -> Adam")
print("  Self-Attention -> Transformer 的灵魂 (全局视野 + 并行)")
