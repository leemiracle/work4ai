"""
实验 02 —— Scaling Law: 为什么模型越大, loss 越低 (且呈幂律)
对应文档: 讲透基础模型/02-ScalingLaw.md
核心结论:
  1. 固定数据和算力, 只放大模型参数量, loss 按幂律 L(N) ∝ N^α (α<0) 持续下降
  2. log(loss) vs log(N) 是直线 —— '越大越准'的数学形态
  3. Chinchilla: 数据和参数要协同放大 (最优 D ≈ 20·N)
跑法: python3 -u 02_scaling_law.py
"""
import math, random, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

def P(*a): print(*a, flush=True)

torch.manual_seed(0); random.seed(0)

text = ("the quick brown fox jumps over the lazy dog. "
        "deep learning models predict the next token. "
        "attention is all you need said the transformer. ") * 20
chars = sorted(set(text)); V = len(chars)
stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in text])
CTX = 12
Xall = torch.stack([data[i:i+CTX] for i in range(len(data)-CTX)])
Yall = data[CTX:]; N = len(Xall)
P("数据 %d 字符, 词表 %d, 样本 %d" % (len(text), V, N))

class NGramNet(nn.Module):
    def __init__(self, V, d, ctx):
        super().__init__()
        self.emb = nn.Embedding(V, d)
        self.fc1 = nn.Linear(ctx*d, d); self.fc2 = nn.Linear(d, V)
    def forward(self, x):
        return self.fc2(F.relu(self.fc1(self.emb(x).view(x.size(0), -1))))

sizes = [8, 16, 32, 64]
P("\n" + "="*60 + "\nPart 1: 扫描模型大小 (固定数据/步数)\n" + "="*60)
P("%8s%14s%14s" % ("维度d", "参数量N", "最终loss"))
params, losses = [], []
for d in sizes:
    torch.manual_seed(0)
    m = NGramNet(V, d, CTX)
    nparam = sum(p.numel() for p in m.parameters())
    opt = torch.optim.Adam(m.parameters(), lr=0.003)
    for step in range(200):
        idx = torch.randint(0, N, (128,))
        opt.zero_grad()
        loss = F.cross_entropy(m(Xall[idx]), Yall[idx])
        loss.backward(); opt.step()
    params.append(nparam); losses.append(loss.item())
    P("%8d%14d%14.4f" % (d, nparam, loss.item()))

P("\n" + "="*60 + "\nPart 2: 拟合幂律 loss ∝ N^α\n" + "="*60)
lp = np.log(params); ll = np.log(losses)
alpha, beta = np.polyfit(lp, ll, 1)
P("拟合: log(loss) = %.4f·log(N) + %.4f" % (alpha, beta))
P("幂指数 α = %.4f  (α<0 ⇒ N越大loss越低; |α|小 ⇒ 下降慢但永不停)" % alpha)
a4, b4 = np.polyfit(lp[:2], ll[:2], 1)
P("\n外推验证 (用前2点定线, 预测后2点):")
for i in [2, 3]:
    pred = math.exp(a4*lp[i] + b4)
    P("  N=%d: 实测=%.4f, 幂律预测=%.4f" % (params[i], losses[i], pred))

P("\n" + "="*60 + "\nPart 3: Chinchilla 最优分配\n" + "="*60)
P("Kaplan(2020): 固定算力优先放大参数 N")
P("Chinchilla(2022): 最优 D ≈ 20·N (数据参数等比放大)")
P("==> LLaMA(7B, 1-2T token) 参数比 GPT-3(175B, 300B token) 小一个量级,")
P("    却更强 —— 因为每个参数分到的 token 更多。这就是 Chinchilla 启示。")
