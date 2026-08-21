"""
实验: 信息论地基 —— 自信息 / 熵 / 交叉熵 / KL散度 / 最大似然等价性
对应文档: 讲透基础模型/math/信息论地基-熵交叉熵KL.md
核心结论:
  1. 自信息 I(x) = -log p(x): 一个事件带来的'惊讶度', 也等于最优编码它的比特数
  2. 熵 H(X) = E[I(X)]: 平均惊讶度 = 平均最短编码长度 = 不可压缩的下限
  3. 交叉熵 H(P,Q) = 用 Q 的编码去传 P 的事件, 平均花的比特数 (>= H(P))
  4. KL散度 D_KL(P||Q) = H(P,Q) - H(P) >= 0 (Gibbs 不等式, 模型与真实的'额外代价')
  5. 最大似然估计 == 最小化交叉熵 == 最小化 KL (这三件事是同一件事)
跑法: python3 entropy_demo.py
"""
import math
import numpy as np
import torch

# =========================================================
# Part 1: 自信息 I(x) = -log2 p(x) —— '惊讶度' 即 '编码长度'
# =========================================================
print("=" * 66)
print("Part 1: 自信息 I(x) = -log2 p(x)  (越罕见越惊讶, 编码越长)")
print("=" * 66)
print("%-22s%12s%14s" % ("事件", "概率 p", "自信息(bits)"))
for name, p in [("太阳东升", 1.0), ("硬币正面", 0.5), ("骰子点数6", 1/6),
                ("彩票中奖", 1e-6), ("瞎编的事件", 1e-9)]:
    I = -math.log2(p) if p > 0 else float('inf')
    print("  %-20s%12.2g%14.2f" % (name, p, I))
print("==> 罕见事件的'惊讶'趋于无穷 —— 这就是 -log 的来源: 它同时是")
print("    (a)收到该消息的'意外程度'  (b)最优编码它所需的最少比特数")

# =========================================================
# Part 2: 熵 H(X) = -sum p log p —— 平均不确定性 / 压缩下限
# =========================================================
print("\n" + "=" * 66)
print("Part 2: 熵 H(X) = -sum p*log2 p  (平均最短编码长度 = 不可压缩下限)")
print("=" * 66)
def H(p_list):
    p = np.array(p_list); p = p[p > 0]
    return -np.sum(p * np.log2(p))

print("  公平硬币 [0.5, 0.5]      : H = %.3f bits  (1次抛掷=1bit不确定性)" % H([0.5,0.5]))
print("  偏置硬币 [0.99,0.01]     : H = %.3f bits  (几乎确定, 熵很低)" % H([0.99,0.01]))
print("  公平骰子 [1/6]*6         : H = %.3f bits  (= log2(6))" % H([1/6]*6))
print("  必然事件 [1.0]           : H = %.3f bits  (完全确定)" % H([1.0]))
# 熵与'猜中所需的最少是非题数'等价
print("==> 熵 = '最优策略下, 平均要问多少个是非题才能确定结果'")
print("    公平硬币要1题, 公平骰子要 log2(6)=2.58 题, 偏置硬币几乎0题")

# =========================================================
# Part 3: 交叉熵 H(P,Q) 与 KL散度 —— 模型 Q 给真实 P 造成的代价
# =========================================================
print("\n" + "=" * 66)
print("Part 3: 交叉熵 H(P,Q) = 用Q的编码传P的事件;  KL = 多花的比特")
print("=" * 66)
def cross_entropy(p_list, q_list):
    p = np.array(p_list, dtype=float); q = np.array(q_list, dtype=float)
    return -np.sum(p * np.log2(q))

P = [0.7, 0.3]                       # 真实分布: a->b(70%), c(30%) —— 就是 00_why_ntp 的规律
scenarios = {
    "Q=完美匹配[0.7,0.3]": [0.7, 0.3],
    "Q=瞎猜均匀[0.5,0.5]": [0.5, 0.5],
    "Q=搞反了[0.3,0.7]":   [0.3, 0.7],
    "Q=过度自信[0.9,0.1]": [0.9, 0.1],
}
Hp = H(P)
print("  真实分布 P = [0.7, 0.3],  其熵 H(P) = %.4f bits (不可压缩下限)\n" % Hp)
print("  %-24s%12s%12s%12s" % ("模型分布 Q", "交叉熵H(P,Q)", "KL散度", "多花bits"))
for name, Q in scenarios.items():
    ce = cross_entropy(P, Q)
    kl = ce - Hp                       # KL = 交叉熵 - 熵
    print("  %-24s%12.4f%12.4f%12.4f" % (name, ce, kl, kl))
print("==> KL>=0 恒成立, 且 Q=P 时 KL=0 (Gibbs 不等式). 训练模型 = 把 KL 压到 0")
print("    '搞反了[0.3,0.7]' 的 KL 最大, '过度自信[0.9,0.1]' 也被罚 —— KL 同时惩罚方向错和过度自信")

# =========================================================
# Part 4: Gibbs 不等式 D_KL(P||Q) >= 0 的数值与解析证明
# =========================================================
print("\n" + "=" * 66)
print("Part 4: 为什么 KL >= 0? —— Gibbs 不等式 (Jensen 不等式的直接推论)")
print("=" * 66)
print("  解析证明: D_KL(P||Q) = sum p*log(p/q) = sum p*log(p/q)")
print("           令 f(t) = t*log(t) (凸函数), 由 Jensen 不等式:")
print("           sum p*log(p/q) = sum q*(p/q)*log(p/q) >= (sum p)*log(sum p / sum q) ...")
print("           更直接: 用 -log 的凸性, D_KL = E_P[-log(Q/P)] >= -log(E_P[Q/P]) = -log(1) = 0")
# 数值验证: 随机大量分布对, KL 永远 >= 0
rng = np.random.default_rng(0)
min_kl = float('inf')
for _ in range(100000):
    p = rng.random(4); p /= p.sum()
    q = rng.random(4); q /= q.sum()
    kl = np.sum(p * np.log2(p/q))
    min_kl = min(min_kl, kl)
print("  数值验证: 10万组随机分布对, KL 最小值 = %.6f  (始终 >= 0, 仅 P=Q 时=0)" % min_kl)

# =========================================================
# Part 5: 最大似然 == 最小交叉熵 == 最小 KL (三合一)
# =========================================================
print("\n" + "=" * 66)
print("Part 5: 最大似然估计 == 最小交叉熵 == 最小 KL (这是同一件事!)")
print("=" * 66)
# 场景: 一枚真币 p(正)=0.7, 抛了 N 次, 用最大似然估计参数
true_p = 0.7
for N in [10, 100, 1000]:
    torch.manual_seed(N)
    flips = torch.bernoulli(torch.full((N,), true_p))   # 模拟抛硬币
    heads = flips.sum().item()
    # 最大似然: argmax q^heads*(1-q)^(N-heads) => q_hat = heads/N
    q_mle = heads / N
    # 交叉熵 = -[p*log q + (1-p)*log(1-q]  (p=真实0.7)
    ce = -(0.7*math.log2(q_mle) + 0.3*math.log2(1-q_mle))
    print("  N=%4d次: 出现正面%d, MLE估计 q=%.3f  |  该 q 下交叉熵=%.4f bits (真熵H(P)=%.4f)"
          % (N, int(heads), q_mle, ce, H([0.7,0.3])))
print("==> 最小化交叉熵的 q 恰好等于最大似然估计 q=heads/N. ")
print("    所以模型训练写 'cross_entropy_loss' 本质就是在做最大似然估计 —— ")
print("    而交叉熵 - 熵 = KL, 熵是常数, 所以最小交叉熵 == 最小KL. 三者完全等价。")

# =========================================================
# Part 6: 算术编码 —— 把'预测下一个词'变成真实压缩
# =========================================================
print("\n" + "=" * 66)
print("Part 6: 算术编码 —— 预测分布越好, 压得越短 (压缩即理解的落点)")
print("=" * 66)
# 用 00_why_ntp 的序列规律: a->b(0.7)/c(0.3), b/c->a
# 算术编码: 把序列映射到 [0,1) 的一个小区间, 区间长度 = 该序列的联合概率
# 理论上最优编码长度 = -log2(联合概率)
import random
random.seed(42)
def gen_seq(n):
    s = ['a']
    for _ in range(n-1):
        s.append('b' if (s[-1]=='a' and random.random()<0.7) or s[-1]!='a' and False else
                 ('c' if s[-1]=='a' else 'a'))
    return s
def gen_seq(n):
    s=['a']
    for _ in range(n-1):
        s.append('b' if s[-1]=='a' and random.random()<0.7 else ('c' if s[-1]=='a' else 'a'))
    return s
seq = gen_seq(1000)
def trans(ch):
    return {'a':[0.0,0.7,0.3],'b':[1.0,0.0,0.0],'c':[1.0,0.0,0.0]}['abc'.index(ch)] if False else \
           ([0.0,0.7,0.3] if ch=='a' else [1.0,0.0,0.0])
# 联合概率 = prod P(next|cur)
logp_perfect = 0.0       # 用真实规律编码
for i in range(1, len(seq)):
    p = trans(seq[i-1])['abc'.index(seq[i])]
    logp_perfect += math.log2(p)
opt_bits = -logp_perfect
uniform_bits = len(seq)*math.log2(3)
print("  1000-token 序列:")
print("    用真实规律(完美模型)算术编码 = %.0f bits" % opt_bits)
print("    不知道规律, 等概率编码       = %.0f bits" % uniform_bits)
print("    压缩率: %.1f%%  (模型越懂规律, 压得越狠)" % (100*(1-opt_bits/uniform_bits)))
print("==> 这就是基础模型预训练的物理意义: 把整个互联网'算术编码'到最短。")
print("    能压到最短的模型, 必然抓住了互联网的全部可学规律 —— 这就是'理解'。")
