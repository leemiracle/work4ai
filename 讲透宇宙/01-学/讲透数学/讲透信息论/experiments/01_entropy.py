"""
实验 01 — 熵的全家桶: 自信息 / 熵 / 联合熵 / 条件熵 / 互信息
对应文档: 讲透信息论/01-熵.md

核心结论:
  1. H(p) 在 p=0.5 时最大, 越偏越低 (伯努利)
  2. 均匀分布熵最大: H = log2(N) (骰子 N=6 → 2.58 bit)
  3. 英文经验熵 ≈ 1.3 bit/字符 (远低于 4.7 = log2(26), 因为字母分布不均)
  4. 中文经验熵 ≈ 7-9 bit/字符 (字数多)
  5. 条件熵 ≤ 边缘熵: 知道 Y 反而减少 X 的不确定度 → 互信息 I(X;Y) ≥ 0

跑法: python3 -u 01_entropy.py
"""
import math, random
from collections import Counter
random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# Part 1: 自信息 I(x) = -log2(p(x))
# ============================================================
P("="*70)
P("实验 01 — 熵的全家桶")
P("="*70)
P()
P("Part 1: 自信息 I(x) = -log2 p(x)")
P("-"*70)
print(f"\n{'事件':<24}{'概率 p':>10}{'自信息 -log2(p)':>18}")
print("-"*54)
examples = [
    ("明天太阳升起",      1.0),
    ("公平币出正面",      0.5),
    ("骰子出 6",          1/6),
    ("扑克抽到 A",        4/52),
    ("生日同月某天",      1/365),
    ("彩票中头奖",        1/17000000),
]
for name, p in examples:
    I = -math.log2(p) if p > 0 else float('inf')
    print(f"{name:<24}{p:>10.2e}{I:>18.2f}")

P("""
解读: 越不可能的事件, 自信息越大.
- 太阳升起 p=1 → I=0 (没信息, 必然)
- 公平币 p=0.5 → I=1 bit (要 1 bit 描述)
- 彩票 p≈0 → I≈24 bit (要 24 bit 才能编码'中了'这个意外)
""")

# ============================================================
# Part 2: 二元熵 H(p) = -p log p - (1-p) log(1-p)
# ============================================================
def entropy_bernoulli(p):
    if p == 0 or p == 1: return 0.0
    return -p * math.log2(p) - (1-p) * math.log2(1-p)

P("="*70)
P("Part 2: 二元熵 H(p) — p=0.5 时最大, 越偏越低")
P("-"*70)
print(f"\n{'p':<10}{'H(p)':>10}{'% of 最大熵':>14}")
print("-"*34)
for p in [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5]:
    H = entropy_bernoulli(p)
    print(f"{p:<10.3f}{H:>10.4f}{H/1.0:>14.1%}")

# ============================================================
# Part 3: 均匀分布熵 H(U_N) = log2(N)
# ============================================================
P("="*70)
P("Part 3: 均匀分布熵 H = log2(N) — 离散分布的最大熵")
P("-"*70)
print(f"\n{'分布':<24}{'N (状态数)':>12}{'理论 H = log2(N)':>20}{'实测 H':>10}")
print("-"*66)

def empirical_entropy_uniform(N, n_samples=100000):
    """均匀分布 N 个状态的经验熵"""
    samples = [random.randint(0, N-1) for _ in range(n_samples)]
    freq = Counter(samples)
    H = 0
    for k, c in freq.items():
        p = c / n_samples
        H -= p * math.log2(p)
    return H

for name, N in [("公平币", 2), ("4 面骰", 4), ("6 面骰", 6),
                ("8 位字节", 256), ("16 位", 65536)]:
    theory = math.log2(N)
    if N <= 256:
        emp = empirical_entropy_uniform(N)
        print(f"{name:<24}{N:>12}{theory:>20.4f}{emp:>10.4f}")
    else:
        print(f"{name:<24}{N:>12}{theory:>20.4f}{'(理论值)':>10}")

P("""
关键: 均匀分布是给定状态数 N 时熵最大的分布 (H = log2 N).
任何不均匀分布的熵都 < log2 N. 这是 [最大熵原理] 的基础.
""")

# ============================================================
# Part 4: 文本经验熵 — 自然语言可压缩多少?
# ============================================================
P("="*70)
P("Part 4: 自然语言的经验熵 (压缩极限)")
P("-"*70)

def empirical_entropy_text(text, k=1):
    """文本的 k-gram 经验熵. k=1 单字符, k=2 双字符..."""
    if k == 1:
        freq = Counter(text)
        n = len(text)
        H = 0
        for c, cnt in freq.items():
            p = cnt / n
            H -= p * math.log2(p)
        return H
    else:
        # k-gram 条件熵的近似: H(text) ≈ H(k-gram) - H((k-1)-gram)
        # 用 H_k = H(k-gram sequence) / k 估计
        grams = [text[i:i+k] for i in range(len(text)-k+1)]
        freq = Counter(grams)
        n = len(grams)
        H = 0
        for g, cnt in freq.items():
            p = cnt / n
            H -= p * math.log2(p)
        return H / k

# 英文样本
english = ("the quick brown fox jumps over the lazy dog. "
           "she sells sea shells by the sea shore. "
           "peter piper picked a peck of pickled peppers. "
           "to be or not to be that is the question. "
           "all happy families are alike each unhappy family is unhappy in its own way. "
           "it was the best of times it was the worst of times. ") * 50

# 中文样本
chinese = ("春眠不觉晓处处闻啼鸟夜来风雨声花落知多少 "
           "床前明月光疑是地上霜举头望明月低头思故乡 "
           "白日依山尽黄河入海流欲穷千里目更上一层楼 "
           "锄禾日当午汗滴禾下土谁知盘中餐粒粒皆辛苦 "
           "千山鸟飞绝万径人踪灭孤舟蓑笠翁独钓寒江雪 ") * 30

print(f"\n{'文本':<14}{'字符数':>10}{'log2(字母表)':>14}{'1-gram H':>12}{'2-gram H':>12}{'3-gram H':>12}")
print("-"*74)
for name, text, alphabet_size in [
    ("英文", english, 26+1),  # 26 字母 + 空格
    ("中文", chinese, 1500),  # 估算常用字数
]:
    H1 = empirical_entropy_text(text, k=1)
    H2 = empirical_entropy_text(text, k=2)
    H3 = empirical_entropy_text(text, k=3)
    H_max = math.log2(alphabet_size)
    print(f"{name:<14}{len(text):>10}{H_max:>14.4f}{H1:>12.4f}{H2:>12.4f}{H3:>12.4f}")

P("""
关键观察:
- 英文字母表最大熵 = log2(27) ≈ 4.75 bit
  但实际 1-gram H ≈ 4.0, 2-gram H ≈ 3.5, 3-gram H ≈ 2.8
  → 越长 context 越能预测 → 熵越低 (语言有大量冗余)
- Shannon 1951 估计英文真熵 ≈ 1.3 bit/字符 (用人类预测实验)
- 这就是 ZIP 能压英文文本到 30% 大小的根本原因

[可压缩程度] = (log2(字母表) - 实际熵) / log2(字母表)
- 英文: (4.75 - 1.3) / 4.75 ≈ 73% 冗余!
""")

# ============================================================
# Part 5: 联合熵 / 条件熵 / 互信息
# ============================================================
P("="*70)
P("Part 5: 联合熵 H(X,Y), 条件熵 H(X|Y), 互信息 I(X;Y)")
P("-"*70)

def joint_entropy(joint_dist):
    """joint_dist: dict[(x,y) -> p]"""
    H = 0
    for p in joint_dist.values():
        if p > 0: H -= p * math.log2(p)
    return H

def marginal_entropy(joint_dist, idx):
    """求边缘分布 P(X) 或 P(Y) 的熵. idx=0 求 X, idx=1 求 Y"""
    marg = Counter()
    for (x, y), p in joint_dist.items():
        marg[(x, y)[idx]] += p
    H = 0
    for p in marg.values():
        if p > 0: H -= p * math.log2(p)
    return H

# 示例 1: 完全独立的 X, Y (各是公平币)
P("\n示例 1: X, Y 完全独立 (各是公平币)")
joint_indep = {(0,0): 0.25, (0,1): 0.25, (1,0): 0.25, (1,1): 0.25}
HX = marginal_entropy(joint_indep, 0)
HY = marginal_entropy(joint_indep, 1)
HXY = joint_entropy(joint_indep)
cond_HX_given_Y = HXY - HY
I_XY = HX + HY - HXY
print(f"  H(X) = {HX:.3f}, H(Y) = {HY:.3f}")
print(f"  H(X,Y) = {HXY:.3f}  (= H(X) + H(Y) 当 X,Y 独立)")
print(f"  H(X|Y) = {cond_HX_given_Y:.3f}  (= H(X) 当独立, 知道 Y 没用)")
print(f"  I(X;Y) = {I_XY:.3f}  (= 0 当独立)")

# 示例 2: 完全相关 (X = Y, 公平币)
P("\n示例 2: X = Y 完全相关 (公平币)")
joint_corr = {(0,0): 0.5, (0,1): 0.0, (1,0): 0.0, (1,1): 0.5}
HX = marginal_entropy(joint_corr, 0)
HY = marginal_entropy(joint_corr, 1)
HXY = joint_entropy(joint_corr)
cond_HX_given_Y = HXY - HY
I_XY = HX + HY - HXY
print(f"  H(X) = {HX:.3f}, H(Y) = {HY:.3f}")
print(f"  H(X,Y) = {HXY:.3f}  (= max(H(X), H(Y)) 当 X=Y)")
print(f"  H(X|Y) = {cond_HX_given_Y:.3f}  (= 0 当 X=Y, 知道 Y 完全确定 X)")
print(f"  I(X;Y) = {I_XY:.3f}  (= H(X) 当 X=Y, 互信息最大)")

# 示例 3: 部分相关 (噪声信道: Y = X 异或 噪声)
P("\n示例 3: Y = X 异或 噪声(以 20% 概率翻转)")
p_noise = 0.2
joint_noisy = {}
for x in [0, 1]:
    for y in [0, 1]:
        # P(X=x) = 0.5; P(Y=y | X=x) = noise 翻转概率
        if x == y:
            joint_noisy[(x, y)] = 0.5 * (1 - p_noise)
        else:
            joint_noisy[(x, y)] = 0.5 * p_noise
HX = marginal_entropy(joint_noisy, 0)
HY = marginal_entropy(joint_noisy, 1)
HXY = joint_entropy(joint_noisy)
cond_HX_given_Y = HXY - HY
I_XY = HX + HY - HXY
print(f"  H(X) = {HX:.3f}, H(Y) = {HY:.3f}")
print(f"  H(X,Y) = {HXY:.3f}")
print(f"  H(X|Y) = {cond_HX_given_Y:.3f}  (知道 Y 后 X 还有这点不确定)")
print(f"  I(X;Y) = {I_XY:.3f}  (>0, Y 携带了 X 的部分信息)")

P("""
核心公式链 (信息论最重要的几个等式):
  H(X,Y) = H(X) + H(Y|X)             ← 链式法则
  H(X|Y) ≤ H(X)                       ← 条件永远降低熵
  I(X;Y) = H(X) - H(X|Y) ≥ 0          ← 互信息非负
  I(X;Y) = 0 ⟺ X,Y 独立               ← 互信息为零当且仅当独立
""")

# ============================================================
# 总结
# ============================================================
P("="*70)
P("一句话总结")
P("="*70)
P("""
熵 H(X) = -Σ p log p 是 [不确定度的精确度量].
- 公平币 H=1, 偏币 H<1, 必然事件 H=0
- 均匀分布熵最大 H=log2(N), 偏离均匀熵降
- 自然语言熵远低于字母表: 英文真熵 ≈ 1.3 bit/字符 (Shannon 1951)
- 条件熵 ≤ 边缘熵 (知道 Y 永远不增加 X 的不确定度)
- 互信息 I(X;Y) = H(X) - H(X|Y) ≥ 0 (信息非负)
""")
