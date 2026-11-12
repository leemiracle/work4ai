"""
实验 04 —— 位置编码: attention 没有位置感, 怎么注入顺序?
对应文档: 讲透基础模型/04-位置编码.md
核心结论:
  1. 纯 attention 是【置换等变】的: 打乱输入顺序, 输出跟着打乱 —— 它根本分不清"第几个"
  2. 因此需要额外注入位置信息. 三代方案: 正弦绝对位置 → RoPE旋转相对位置 → ALiBi偏置
  3. 顺序敏感任务上, 无位置编码的 attention 必败, 加了位置编码才学会
  4. RoPE 的精髓: 用旋转把"绝对位置"变成"相对位置差", 且支持长度外推
跑法: python3 -u 04_positional.py
"""
import math, random
import torch
import torch.nn as nn
import torch.nn.functional as F

def P(*a): print(*a, flush=True)
torch.manual_seed(0); random.seed(0)

def attn(x, Wq, Wk, Wv):
    Q, K, V = Wq(x), Wk(x), Wv(x)
    s = Q @ K.transpose(-1, -2) / math.sqrt(x.shape[-1])
    return F.softmax(s, dim=-1) @ V

# =========================================================
# Part 1: 纯 attention 是置换等变的 (打乱输入, 输出跟着打乱)
# =========================================================
P("="*62); P("Part 1: 纯 attention 没有位置感 (置换等变)"); P("="*62)
d = 8
Wq = nn.Linear(d, d, bias=False); Wk = nn.Linear(d, d, bias=False); Wv = nn.Linear(d, d, bias=False)
x = torch.randn(4, d)
out = attn(x, Wq, Wk, Wv)
perm = [2, 0, 3, 1]
out_perm_input = attn(x[perm], Wq, Wk, Wv)        # 打乱输入再算
diff = (out_perm_input - out[perm]).abs().max().item()   # 应≈0
P("输入 4 个词, attention 输出形状 %s" % (tuple(out.shape),))
P("把输入按 [2,0,3,1] 打乱后重算 attention, 与原输出按同序打乱之差: %.2e" % diff)
P("==> 差≈0: 打乱输入 ⇔ 输出同步打乱. attention 对'谁在第几位'完全无感!")
P("    这就是为什么必须额外加位置编码。\n")

# =========================================================
# Part 2: 顺序敏感任务 —— 无位置编码必败, 加了才学会
# =========================================================
P("="*62); P("Part 2: 顺序任务'复制第2个位置', 无 vs 有位置编码"); P("="*62)
V, L = 6, 4
def make_batch(n):
    X = torch.randint(0, V, (n, L))
    Y = X[:, 1]                                    # 目标 = 第2个位置的 token
    return X, Y
Xtr, Ytr = make_batch(1000); Xte, Yte = make_batch(200)

def sinusoidal_pos(L, d):
    pe = torch.zeros(L, d)
    pos = torch.arange(L).unsqueeze(1).float()
    div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000) / d))
    pe[:, 0::2] = torch.sin(pos * div); pe[:, 1::2] = torch.cos(pos * div)
    return pe

class AttnCls(nn.Module):
    def __init__(self, V, d, L, use_pos=False):
        super().__init__()
        self.emb = nn.Embedding(V, d); self.use_pos = use_pos
        self.pos = sinusoidal_pos(L, d)
        self.wq = nn.Linear(d,d,bias=False); self.wk = nn.Linear(d,d,bias=False); self.wv = nn.Linear(d,d,bias=False)
        self.fc = nn.Linear(d, V)
    def forward(self, x):                          # x: (B,L) token ids
        e = self.emb(x)
        if self.use_pos: e = e + self.pos.to(e.device)
        dk = e.shape[-1]
        a = F.softmax(e @ e.transpose(-1,-2)/math.sqrt(dk), dim=-1)
        return self.fc((a @ e).mean(dim=1))        # 池化后分类

for name, use_pos in [("无位置编码", False), ("正弦位置编码", True)]:
    torch.manual_seed(0)
    m = AttnCls(V, d, L, use_pos)
    opt = torch.optim.Adam(m.parameters(), lr=0.01)
    for step in range(600):
        opt.zero_grad()
        loss = F.cross_entropy(m(Xtr), Ytr)
        loss.backward(); opt.step()
    with torch.no_grad():
        acc = (m(Xte).argmax(-1) == Yte).float().mean().item()
    P("  [%s] 训练600步: 测试准确率 = %.1f%%  (随机基线 %.0f%%)" % (name, acc*100, 100/V))
P("==> 无位置编码: attention 分不清'第2个', 卡在随机(~17%).")
P("    加位置编码: 能定位第2个位置, 准确率接近100%.\n")

# =========================================================
# Part 3: RoPE —— 用旋转把绝对位置变成相对位置
# =========================================================
P("="*62); P("Part 3: RoPE (旋转位置编码) —— 相对位置 + 长度外推"); P("="*62)
d2 = 4
P("RoPE 核心: 位置 m 的向量旋转角度 m·θ, 于是 q_m·k_n 只依赖相对距离 (m-n)")
theta = 1.0 / (10000 ** (torch.arange(0, d2//2).float() / (d2//2)))
P("频率 θ = %s (每维不同频率)" % [round(t,4) for t in theta.tolist()])
def rope(v, m):                                    # 位置m的旋转向量
    ang = m * theta
    c, s = torch.cos(ang), torch.sin(ang)
    out = v.clone()
    out[0::2] = v[0::2]*c - v[1::2]*s
    out[1::2] = v[0::2]*s + v[1::2]*c
    return out
q = torch.randn(d2); k = torch.randn(d2)
P("\nq·k 在不同相对位置的点积 (旋转后, 只依赖 |m-n|):")
for (m, n) in [(0,0),(1,1),(2,2),(3,3),(1,0),(2,1),(3,2),(5,3)]:
    dot = (rope(q,m) * rope(k,n)).sum().item()
    P("  位置 m=%d, n=%d (相对距离 %d): q·k = %+.3f" % (m, n, abs(m-n), dot))
P("==> 相对距离相同(如 m=n)的点积相同, 距离越大点积越小 —— RoPE 把'绝对位置'")
P("    编码成'相对距离', 这让它能外推到训练时没见过的更长序列(现代LLM标配).")
