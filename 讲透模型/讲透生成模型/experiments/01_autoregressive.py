"""
讲透生成模型 · 实验 01 —— 自回归模型 AR (GPT 的本质)
===================================================
字符级 next-char 预测: 把序列概率链式分解为
    p(x_1, x_2, ..., x_n) = prod_i p(x_i | x_1, ..., x_{i-1})
训练时用 teacher forcing (喂真实前文, 预测下一个字符);
生成时自回归 (每步用上一步的输出当下一步的输入, 一个一个吐字符 —— 这就是 GPT)。

跑法:  python3 01_autoregressive.py     (CPU 约 20 秒)
要点:  ① loss 下降 ② 自回归生成像语料 ③ 贪心 vs 采样的差别
"""
import torch, torch.nn as nn
torch.set_num_threads(1)          # 小模型单线程更快
torch.manual_seed(0)

# ------------------------------------------------------------------
# 1. 语料 + 词表 (字符级)
# ------------------------------------------------------------------
TEXT = "the cat sat on the mat. the dog sat on the log. " * 40
chars = sorted(set(TEXT))
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for i, c in enumerate(chars)}
V = len(chars)
print(f"语料长度 {len(TEXT)} 字符 | 词表大小 V={V} ({''.join(chars)})")
data = torch.tensor([stoi[c] for c in TEXT])

# ------------------------------------------------------------------
# 2. 模型: Embedding -> GRU -> Linear  (最小版 GPT 的核心)
#    输入一串字符下标, 输出每个位置对下一个字符的预测分布
# ------------------------------------------------------------------
class CharAR(nn.Module):
    def __init__(self, vocab, hid=64):
        super().__init__()
        self.emb = nn.Embedding(vocab, hid)
        self.gru = nn.GRU(hid, hid, batch_first=True)
        self.fc  = nn.Linear(hid, vocab)
    def forward(self, x, h=None):
        e = self.emb(x)
        out, h = self.gru(e, h)
        return self.fc(out), h                      # logits[B,L,V], 隐状态

m   = CharAR(V)
opt = torch.optim.Adam(m.parameters(), 1e-3)
CTX = 16                                           # 上下文窗口长度

def get_batch(n=32):
    """随机切长度 CTX+1 片段: 输入前 CTX 个, 目标后移一位 (预测下一个)."""
    ixs = torch.randint(0, len(data) - CTX - 1, (n,))
    x = torch.stack([data[ix:ix + CTX]     for ix in ixs])
    y = torch.stack([data[ix + 1:ix + CTX + 1] for ix in ixs])
    return x, y

# ------------------------------------------------------------------
# 3. 训练 (teacher forcing: 用真实上文, 最大化下一个字符的似然)
# ------------------------------------------------------------------
print("\n训练 (teacher forcing)...")
for it in range(800):                              # GRU 较慢, 800 步已收敛
    x, y = get_batch()
    logits, _ = m(x)
    loss = nn.functional.cross_entropy(logits.reshape(-1, V), y.reshape(-1))
    opt.zero_grad(); loss.backward(); opt.step()
    if it % 200 == 0:
        print(f"  step {it:4d}: loss = {loss.item():.3f}")
print(f"  step  800: loss = {loss.item():.3f}   (越低 = 预测下一个字符越准)")

# ------------------------------------------------------------------
# 4. 自回归生成 —— GPT 的真面目: 一个字符一个字符地吐
#    关键: 第 i 个字符必须等第 i-1 个采样出来才能预测 (所以逐 token 慢)
# ------------------------------------------------------------------
@torch.no_grad()
def generate(seed="the ", n=80, temperature=0.8):
    m.eval()
    h = None
    cur = torch.tensor([[stoi[c] for c in seed]])   # 先喂 seed
    out = seed
    for _ in range(n):
        logits, h = m(cur, h)                       # 只用最后一步的预测
        prob = torch.softmax(logits[0, -1] / temperature, dim=0)
        nxt = torch.multinomial(prob, 1)            # 按分布采样下一个字符
        out += itos[nxt.item()]
        cur = nxt[None]                             # 上一步输出 = 下一步输入 (自回归!)
    return out

print("\n=== 自回归生成 (采样, temperature=0.8 —— 每次可能不同) ===")
print(generate("the ", 80))
print("\n=== 自回归生成 (近似贪心 argmax, temperature≈0 —— 永远确定性) ===")
print(generate("the ", 80, temperature=1e-4))

print("""
要点:
  1. 训练 = 最大化 ∏ p(x_i|前文) = 最小化 cross-entropy.   <- 这是『似然类』
  2. 生成 = 一个一个吐, 第 i 个依赖第 i-1 个的采样结果.      <- 所以逐 token 慢, 不能并行
  3. temperature 高 → 多样/可能乱; 低 → 保守/可能复读.       <- GPT 的 temperature 参数就是这个
  4. 这是 GPT/Llama/Gemini 的核心机制, 只是 token 级 + Transformer, 规模大千万倍.
""")
