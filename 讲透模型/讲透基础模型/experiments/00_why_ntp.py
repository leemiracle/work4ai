"""
实验 00 —— 基础模型的第一性原理: 为什么'预测下一个词'能产生智能?
对应文档: 讲透基础模型/00-为什么预测下一个词能产生智能.md
核心结论:
  1. NTP(Next Token Prediction) 看似只是'自动补全', 实则逼着模型自己'发现'
     数据里隐藏的规律 —— 这就是 Ilya 说的'压缩即理解': 要压缩就必须找规律, 找到规律=理解
  2. 训练 NTP = 最小化交叉熵 = 找最短编码 = 最优压缩 (信息论恒等式)
  3. 为什么用交叉熵(CE)而非 MSE: token 是离散分类, CE 在概率空间优化且等价于最大似然;
     MSE 在 logit 空间回归 one-hot, 经 softmax 后概率被严重扭曲, 无法表达不确定性
跑法: python3 00_why_ntp.py
"""
import math, random
import torch
import torch.nn as nn

torch.manual_seed(0)
random.seed(0)

vocab = ['a', 'b', 'c']
stoi = {ch: i for i, ch in enumerate(vocab)}

# =========================================================
# Part 1: NTP 无监督'发现'隐藏规律 —— 压缩即理解的实证
# =========================================================
print("=" * 66)
print("Part 1: 只靠'预测下一个词', 模型自己发现隐藏规律")
print("=" * 66)

# 构造一条'有规律但模型事先一无所知'的序列(一条马尔可夫链):
#   状态 a -> 下一个 70% 是 b, 30% 是 c   (不确定!)
#   状态 b -> 下一个一定是 a              (确定)
#   状态 c -> 下一个一定是 a              (确定)
# 模型从未被告知这条规则, 只能从'预测下一个词'的损失里自己悟出来
def gen(n):
    seq = ['a']
    for _ in range(n - 1):
        if seq[-1] == 'a':
            seq.append('b' if random.random() < 0.7 else 'c')
        else:
            seq.append('a')
    return seq

data = torch.tensor([stoi[ch] for ch in gen(4000)])

# 理论最优: 模型最好的交叉熵能到多少? = 序列的熵
# 一半的转移是 a->? (熵 = -0.7log0.7 -0.3log0.3), 一半是 ?->a (熵=0)
H_a = -0.7 * math.log2(0.7) - 0.3 * math.log2(0.3)      # a 后面的不确定性
H_per_token = H_a / 2                                     # 平均到每个 token
print("序列的理论熵(交叉熵的物理下限) = %.3f bits/token = %.4f nats" % (H_per_token, H_per_token * math.log(2)))
print("模型若真'理解'了规律, 交叉熵应收敛到此下限附近\n")

# 最简语言模型: 用当前 token 预测下一个 token (本质是学一张 3x3 转移概率表)
class TinyLM(nn.Module):
    def __init__(self, V, d=16):
        super().__init__()
        self.emb = nn.Embedding(V, d)
        self.fc = nn.Linear(d, V)
    def forward(self, x):
        return self.fc(self.emb(x))

x, y = data[:-1], data[1:]
model = TinyLM(len(vocab))
opt = torch.optim.Adam(model.parameters(), lr=0.05)

print("用【交叉熵】训练 NTP (这就是所有基础模型预训练的目标):")
loss = None
for step in range(0, 2001, 500):
    opt.zero_grad()
    logits = model(x)
    loss = nn.functional.cross_entropy(logits, y)
    loss.backward(); opt.step()
    print("  step %4d: 交叉熵 = %.4f nats = %.3f bits/token" % (step, loss.item(), loss.item() / math.log(2)))

print("\n模型自己悟出来的转移概率(它从没被告知规则!):")
with torch.no_grad():
    for ch in vocab:
        probs = torch.softmax(model(torch.tensor([stoi[ch]])), dim=-1)[0]
        print("  当前=%s -> 预测 a:%.2f  b:%.2f  c:%.2f" % (ch, probs[0], probs[1], probs[2]))
print("  真实规则: a->b(0.70)/c(0.30);  b->a(1.00);  c->a(1.00)")
print("==> 仅凭'预测下一个词'这一目标, 模型无监督地还原了整条规律 —— 这就是'压缩即理解'")

# =========================================================
# Part 2: 为什么是交叉熵而非 MSE? (呼应用户选中的 MSELoss)
# =========================================================
print("\n" + "=" * 66)
print("Part 2: 为什么基础模型用交叉熵(CE), 不用你熟悉的 MSE?")
print("=" * 66)

# 同样的数据/模型, 改用 MSE: 把 one-hot 当连续向量, 在 logit 空间回归
model_mse = TinyLM(len(vocab))
opt_mse = torch.optim.Adam(model_mse.parameters(), lr=0.05)
onehot = nn.functional.one_hot(y, len(vocab)).float()
for step in range(2000):
    opt_mse.zero_grad()
    loss_m = nn.functional.mse_loss(model_mse(x), onehot)
    loss_m.backward(); opt_mse.step()

print("用【MSE】训练同一任务后, 对不确定转移 a->? 的预测对比:")
print("%17s%8s%8s%8s" % ("", "P(a)", "P(b)", "P(c)"))
with torch.no_grad():
    p_ce = torch.softmax(model(torch.tensor([stoi['a']])), dim=-1)[0]
    p_mse = torch.softmax(model_mse(torch.tensor([stoi['a']])), dim=-1)[0]
    print("  CE 模型:    %8.3f%8.3f%8.3f" % (p_ce[0], p_ce[1], p_ce[2]))
    print("  MSE 模型:   %8.3f%8.3f%8.3f" % (p_mse[0], p_mse[1], p_mse[2]))
    print("  真实分布:      0.000   0.700   0.300")
    raw = model_mse(torch.tensor([stoi['a']]))[0].tolist()
    print("\n  MSE 模型原始 logits:", ["%.3f" % v for v in raw])
print("""\n==> MSE 把 one-hot 当连续值在 logit 空间回归, 让 logit->均值[0,0.7,0.3],
   但 softmax([0,0.7,0.3]) ≈ [0.23,0.46,0.31] ≠ 真实[0,0.7,0.3] —— 概率被严重扭曲!
   原因: MSE 优化的是 logit 与 one-hot 的欧氏距离, 既无概率意义也无信息论意义;
         而 CE 直接在概率空间最大化似然 = 找最短编码 = 最优压缩。""")

# =========================================================
# Part 3: 交叉熵 = 压缩长度 (信息论铁证)
# =========================================================
print("=" * 66)
print("Part 3: 交叉熵 = 压缩长度 —— 用训好的模型给序列算编码长度")
print("=" * 66)
with torch.no_grad():
    logits = model(x)
    nll = nn.functional.cross_entropy(logits, y, reduction='sum').item() / math.log(2)  # 总 bits
    n = len(y)
print("用 CE 模型对 %d 个 token 做算术编码, 需 %.0f bits = %.3f bits/token" % (n, nll, nll / n))
print("理论下限(%d token × %.3f) = %.0f bits" % (n, H_per_token, n * H_per_token))
print("naive 等概率编码(log2 3)     = %.0f bits  (不知道规律时的编码)" % (n * math.log2(3)))
print("==> 模型把序列压到了接近理论熵 —— '预测下一个词'本质上就是一个压缩机。")
print("    Ilya Sutskever 的洞见: 压缩需要发现规律, 发现规律 = 理解, 于是 预测下一个词 ⟹ 理解。")
