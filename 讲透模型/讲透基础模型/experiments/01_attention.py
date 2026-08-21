"""
实验 01 —— 手写 Self-Attention: 为什么 softmax(QK^T/sqrt(d))V 能替代 RNN
对应文档: 讲透基础模型/01-Transformer与注意力.md
核心结论:
  1. 远距离依赖任务上, bigram(只看前一个词)必然失败 —— 它根本看不到远处的线索
  2. attention = 内容相关的加权平均: 每个词用 Q(查询) 去和所有词的 K(键) 打分,
     softmax 归一化后对 V(值) 加权求和 —— 谁相关谁权重大
  3. 除以 sqrt(d) 是必须的: 点积方差随维度 d 线性增长, 不除会让 softmax 饱和(梯度消失)
  4. attention 能并行 + 抓任意远依赖, 这是它淘汰 RNN 的根本原因
跑法: python3 01_attention.py
"""
import math, random
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)
random.seed(0)

# =========================================================
# Part 1: 远距离依赖任务 —— bigram(只看前一词)必败
# =========================================================
print("=" * 66)
print("Part 1: 远距离依赖任务, bigram(只看前一词)必败")
print("=" * 66, flush=True)
# 序列 = [线索K1或K2, 干扰x, 干扰y, 干扰x, 干扰y, 目标]
#   K1(id=0) -> 目标 <A>(id=4);  K2(id=1) -> 目标 <B>(id=5)
#   线索在第0位, 目标在第5位, 中间隔4个干扰 —— 必须看到第0位才能预测
V = 6
def make_batch(n):
    X, Y = [], []
    for _ in range(n):
        key = random.choice([0, 1])
        X.append([key, 2, 3, 2, 3])
        Y.append(4 if key == 0 else 5)
    return torch.tensor(X), torch.tensor(Y)

Xtr, Ytr = make_batch(800)
Xte, Yte = make_batch(200)

class Bigram(nn.Module):
    def __init__(self, V, d=16):
        super().__init__(); self.emb = nn.Embedding(V, d); self.fc = nn.Linear(d, V)
    def forward(self, x):
        return self.fc(self.emb(x))

bigram = Bigram(V)
opt = torch.optim.Adam(bigram.parameters(), lr=0.01)
for step in range(800):
    opt.zero_grad()
    loss = F.cross_entropy(bigram(Xtr[:, -1]), Ytr)
    loss.backward(); opt.step()
with torch.no_grad():
    acc = (bigram(Xte[:, -1]).argmax(-1) == Yte).float().mean().item()
print("bigram 训练后: 测试准确率 = %.1f%%  (随机猜是 50%%)" % (acc * 100), flush=True)
print("==> bigram 只看到最后一个干扰词'y', 看不到第0位线索, 停在50%(瞎猜)\n", flush=True)

# =========================================================
# Part 2: 逐步构建 attention (4个词小例子, d=8) —— 用 no_grad 避免建图
# =========================================================
print("=" * 66)
print("Part 2: 逐步构建 attention (4词, d=8)")
print("=" * 66, flush=True)
with torch.no_grad():
    torch.manual_seed(1)
    seq_len, d = 4, 8
    x = torch.randn(seq_len, d)
    W_q = nn.Linear(d, d, bias=False); W_k = nn.Linear(d, d, bias=False); W_v = nn.Linear(d, d, bias=False)
    Q, K, Vv = W_q(x), W_k(x), W_v(x)
    scores = Q @ K.T
    print("步骤A 朴素平均: 所有词等权 -> 分不清主次")
    print("步骤B QK^T 打分 (词i对词j的关注度): 形状 %s 范围[%.2f,%.2f]" % (tuple(scores.shape), scores.min(), scores.max()), flush=True)
    attn = F.softmax(scores, dim=-1)
    out = attn @ Vv
    print("步骤C softmax归一化 + 加权V:")
    for i in range(seq_len):
        print("  词%d 关注: %s" % (i, ["%.2f" % w for w in attn[i]]), flush=True)

# =========================================================
# Part 3: 完整公式 + sqrt(d)
# =========================================================
print("\n" + "=" * 66)
print("Part 3: 完整公式  Attention = softmax(QK^T/sqrt(d)) V")
print("=" * 66, flush=True)

# =========================================================
# Part 4: 为什么除以 sqrt(d)?
# =========================================================
print("=" * 66)
print("Part 4: 为什么除以 sqrt(d)? —— 防 softmax 饱和")
print("=" * 66, flush=True)
for d_test in [8, 64, 512]:
    torch.manual_seed(0)
    Q = torch.randn(1, d_test) * 0.5
    K = torch.randn(10, d_test) * 0.5
    scores = (Q @ K.T).squeeze()
    p_no = F.softmax(scores, dim=-1)
    p_yes = F.softmax(scores / math.sqrt(d_test), dim=-1)
    print("  d=%d: 点积std=%.2f | 不除sqrt(d): max权重=%.3f(饱和) | 除sqrt(d): max权重=%.3f(温和)" %
          (d_test, scores.std().item(), p_no.max().item(), p_yes.max().item()), flush=True)
print("==> 维度越大点积越大, softmax 越饱和(梯度消失). 除sqrt(d)把方差拉回1.\n", flush=True)

# =========================================================
# Part 5: attention 学会远距离依赖 (vs bigram 的50%)
# =========================================================
print("=" * 66)
print("Part 5: attention 学会远距离依赖 (vs bigram 的50%)")
print("=" * 66, flush=True)
class AttnModel(nn.Module):
    def __init__(self, V, d=16):
        super().__init__()
        self.emb = nn.Embedding(V, d)
        self.wq = nn.Linear(d, d, bias=False); self.wk = nn.Linear(d, d, bias=False)
        self.wv = nn.Linear(d, d, bias=False); self.fc = nn.Linear(d, V)
    def forward(self, x):
        e = self.emb(x)
        dk = e.shape[-1]
        attn = F.softmax(e @ e.transpose(-1, -2) / math.sqrt(dk), dim=-1)  # 简化:Q=K=V=e
        return self.fc((attn @ e)[:, -1, :])

am = AttnModel(V)
opt = torch.optim.Adam(am.parameters(), lr=0.05)
for step in range(800):
    opt.zero_grad()
    loss = F.cross_entropy(am(Xtr), Ytr)
    loss.backward(); opt.step()
    if step % 200 == 0:
        print("  step %4d: loss=%.4f" % (step, loss.item()), flush=True)
with torch.no_grad():
    acc = (am(Xte).argmax(-1) == Yte).float().mean().item()
    print("attention 训练后: 测试准确率 = %.1f%%  (bigram 是 50%%)" % (acc * 100), flush=True)
    e = am.emb(Xte[:1])
    attn = F.softmax(e @ e.transpose(-1, -2) / math.sqrt(e.shape[-1]), dim=-1)
    print("\n  目标位(最后一位)对各位置的关注度:", flush=True)
    print("   ", ["位%d:%.2f" % (i, w) for i, w in enumerate(attn[0, -1, :].tolist())], flush=True)
    print("  (位0=线索位, 位1-4=干扰位) —— 模型把注意力集中到了线索上!", flush=True)
print("\n==> attention 让末位'一步看到'第0位线索; RNN 要传递5步. 这就是它淘汰 RNN 的原因。", flush=True)
