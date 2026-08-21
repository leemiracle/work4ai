#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 C 配套实验：Kneser-Ney 平滑 vs Add-1（从零实现）
====================================================================
纯 Python 标准库，几秒跑完。

在微型语料上训练 bigram LM，对比三种方法的困惑度（perplexity）：
  1. 无平滑（MLE）
  2. Add-1（Laplace）
  3. Kneser-Ney（绝对折扣 + 延续概率）

★ 反直觉发现：
  1. Add-1 大幅高估未见 bigram 概率 → PPL 比 KN 差 30%+
  2. 延续概率正确处理 "Francisco 问题"：
     只跟特定词搭配的词，continuation 很低
  3. KN 的折扣 D=0.75 看似"偷"了一点点概率，
     但省下来的概率被精准分配给合理的回退

python3 experiments/C_kneser_ney.py
"""
import math
from collections import defaultdict, Counter

def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 1. 微型语料（训练集 + 测试集）
# ============================================================
TRAIN_SENTENCES = [
    "the cat sat on the mat",
    "the dog sat on the rug",
    "the cat ran on the rug",
    "the dog ran on the mat",
    "the bird flew over the house",
    "the fish swam in the river",
    "the cat ate the fish on the mat",
    "the dog ate the bone on the rug",
    "the bird ate the worm on the mat",
    "the cat slept on the mat all day",
    "the dog slept on the rug all day",
    "the fish swam in the lake all day",
    "the bird flew over the river all day",
    "the cat ran after the dog on the mat",
    "the dog ran after the cat on the rug",
    "the fish ate the worm in the river",
    "the bird sat on the house all day",
    "the cat sat on the rug all night",
    "the dog ate the fish on the mat",
    "the bird swam over the lake all night",
]

TEST_SENTENCES = [
    "the cat ran on the mat",
    "the dog flew over the house",
    "the bird ate the fish",
    "the cat swam in the river",
    "the dog sat on the mat",
    "the fish ran on the rug",
    "the bird slept on the house",
    "the cat ate the bone",
]

def tokenize(sent):
    return sent.lower().split()


# ============================================================
# 2. 统计 N-gram
# ============================================================
class BigramStats:
    def __init__(self, sentences):
        self.unigram = Counter()
        self.bigram = Counter()
        self.bigram_types_pre = defaultdict(set)   # {w2: {w1, ...}}
        self.bigram_types_suc = defaultdict(set)   # {w1: {w2, ...}}
        self.total_tokens = 0
        self.vocab = set()

        for sent in sentences:
            tokens = tokenize(sent)
            self.vocab.update(tokens)
            for w in tokens:
                self.unigram[w] += 1
                self.total_tokens += 1
            for i in range(len(tokens) - 1):
                w1, w2 = tokens[i], tokens[i+1]
                self.bigram[(w1, w2)] += 1
                self.bigram_types_pre[w2].add(w1)
                self.bigram_types_suc[w1].add(w2)

        self.V = len(self.vocab)
        self.total_bigram_types = len(self.bigram)

    def N1plus_pre(self, w):
        """N_{1+}(·w) = w 的不同前驱数"""
        return len(self.bigram_types_pre.get(w, set()))

    def N1plus_suc(self, w):
        """N_{1+}(w·) = w 的不同后继数"""
        return len(self.bigram_types_suc.get(w, set()))


# ============================================================
# 3. 三种平滑方法
# ============================================================
def prob_mle(stats, w1, w2):
    """MLE（无平滑）—— 零概率灾难"""
    c1 = stats.unigram[w1]
    if c1 == 0:
        return 0.0
    return stats.bigram[(w1, w2)] / c1


def prob_add1(stats, w1, w2):
    """Add-1 (Laplace) 平滑"""
    c1 = stats.unigram[w1]
    return (stats.bigram[(w1, w2)] + 1) / (c1 + stats.V)


def prob_kneser_ney(stats, w1, w2, D=0.75):
    """
    Modified Interpolated Kneser-Ney (bigram).

    P_KN(w2|w1) = max(c(w1,w2) - D, 0) / c(w1)
                  + λ(w1) * P_CONT(w2)

    λ(w1) = D / c(w1) * N_{1+}(w1·)
    P_CONT(w2) = N_{1+}(·w2) / N_{1+}(··)
    """
    c1 = stats.unigram[w1]
    c12 = stats.bigram[(w1, w2)]

    if c1 == 0:
        uw2 = stats.unigram[w2]
        if stats.total_tokens == 0:
            return 1.0 / stats.V
        return max(uw2, 0.5) / (stats.total_tokens + 0.5 * stats.V)

    # 第一项：绝对折扣
    discounted = max(c12 - D, 0.0) / c1

    # λ(w1)
    n1p_suc = stats.N1plus_suc(w1)
    lam = D * n1p_suc / c1

    # P_CONT(w2)
    n1p_pre = stats.N1plus_pre(w2)
    total_types = stats.total_bigram_types
    if total_types == 0:
        p_cont = 1.0 / stats.V
    else:
        p_cont = n1p_pre / total_types

    return discounted + lam * p_cont


# ============================================================
# 4. 困惑度计算
# ============================================================
def compute_ppl(stats, sentences, prob_func, method_name=""):
    """在测试句子上计算困惑度（perplexity）"""
    log_prob_sum = 0.0
    n_bigrams = 0
    n_zero = 0

    for sent in sentences:
        tokens = tokenize(sent)
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i+1]
            p = prob_func(stats, w1, w2)
            if p <= 0:
                n_zero += 1
                p = 1e-10
            log_prob_sum += math.log(p)
            n_bigrams += 1

    avg_log = log_prob_sum / n_bigrams
    ppl = math.exp(-avg_log)
    return ppl, n_bigrams, n_zero


# ============================================================
# 主程序
# ============================================================
def main():
    P("=" * 68)
    P("讲透NLP · 附录 C：Kneser-Ney vs Add-1 平滑（从零实现）")
    P("=" * 68)

    stats = BigramStats(TRAIN_SENTENCES)

    P(f"""
  语料统计:
    训练集: {len(TRAIN_SENTENCES)} 句, {stats.total_tokens} tokens, 词表 V = {stats.V}
    测试集: {len(TEST_SENTENCES)} 句
    Bigram 类型数 N_{{1+}}(··) = {stats.total_bigram_types}
""")

    # Part 1：三种方法的困惑度对比
    P("-" * 68)
    P("Part 1：★ 三种方法的困惑度（Perplexity）对比")
    P("-" * 68)

    ppl_mle,   n_bg, n_zero_mle   = compute_ppl(stats, TEST_SENTENCES, prob_mle)
    ppl_add1,  _,    n_zero_add1  = compute_ppl(stats, TEST_SENTENCES, prob_add1)
    ppl_kn,    _,    n_zero_kn    = compute_ppl(stats, TEST_SENTENCES, lambda s,w1,w2: prob_kneser_ney(s,w1,w2,D=0.75))

    P(f"""
  在 {len(TEST_SENTENCES)} 句测试集 ({n_bg} 个 bigram) 上:

  ┌────────────────────────┬───────────┬────────────────┬──────────────────┐
  │ 方法                   │ PPL       │ vs KN          │ 零概率 bigram    │
  ├────────────────────────┼───────────┼────────────────┼──────────────────┤
  │ MLE (无平滑)           │ {ppl_mle:>8.1f}  │ {ppl_mle/ppl_kn:>+5.1f}×          │ {n_zero_mle:>3} 个 (概率=0) │
  │ Add-1 (Laplace)        │ {ppl_add1:>8.1f}  │ {ppl_add1/ppl_kn:>+5.1f}×          │ {n_zero_add1:>3} 个         │
  │ Kneser-Ney (D=0.75)    │ {ppl_kn:>8.1f}  │ 基准            │ {n_zero_kn:>3} 个         │
  └────────────────────────┴───────────┴────────────────┴──────────────────┘

  ★ 反直觉 1: KN 的 PPL 比 Add-1 低 {(1 - ppl_kn/ppl_add1)*100:.0f}%+!
  ★ 反直觉 2: Add-1 有 {n_zero_add1} 个零概率 bigram
""")

    # Part 2：逐 bigram 对比
    P("-" * 68)
    P("Part 2：逐 bigram 对比 —— Add-1 的'过度打折'问题")
    P("-" * 68)

    demo_pairs = []
    for sent in TEST_SENTENCES:
        tokens = tokenize(sent)
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i+1]
            c12 = stats.bigram[(w1, w2)]
            c1 = stats.unigram[w1]
            demo_pairs.append((w1, w2, c12, c1))

    demo_pairs.sort(key=lambda x: (x[2] == 0, -x[2]))

    P(f"\n  {'bigram':<20} {'c(w1,w2)':>10} {'P(MLE)':>10} {'P(Add1)':>10} {'P(KN)':>10} {'P_CONT(w2)':>12}")
    P("  " + "-" * 76)
    seen_set = set()
    shown = 0
    for w1, w2, c12, c1 in demo_pairs:
        key = (w1, w2)
        if key in seen_set:
            continue
        seen_set.add(key)
        p_mle = prob_mle(stats, w1, w2)
        p_a1 = prob_add1(stats, w1, w2)
        p_kn = prob_kneser_ney(stats, w1, w2, D=0.75)
        n1p_pre = stats.N1plus_pre(w2)
        total_types = stats.total_bigram_types
        p_cont = n1p_pre / total_types if total_types > 0 else 0
        tag = " ← 未见!" if c12 == 0 else ""
        P(f"  {w1+' '+w2:<20} {c12:>10} {p_mle:>10.5f} {p_a1:>10.5f} {p_kn:>10.5f} {p_cont:>12.5f}{tag}")
        shown += 1
        if shown >= 14:
            break

    # Part 3：Continuation Probability 的效果
    P("-" * 68)
    P("Part 3：★ Continuation Probability —— KN 的核心创新")
    P("-" * 68)

    word_stats = []
    for w in sorted(stats.vocab):
        p_uni = stats.unigram[w] / stats.total_tokens
        n1p = stats.N1plus_pre(w)
        total_types = stats.total_bigram_types
        p_cont = n1p / total_types if total_types > 0 else 0
        word_stats.append((w, stats.unigram[w], n1p, p_uni, p_cont))

    P(f"\n  {'词':<12} {'c(w)':>6} {'前驱数':>8} {'P(w) 一元':>12} {'P_CONT(w)':>12} {'差异':>8}")
    P("  " + "-" * 64)
    for w, cw, n1p, p_uni, p_cont in word_stats[:15]:
        diff = "↑" if p_cont > p_uni else ("↓" if p_cont < p_uni else "=")
        P(f"  {w:<12} {cw:>6} {n1p:>8} {p_uni:>12.5f} {p_cont:>12.5f} {diff:>8}")

    # Part 4：折扣参数 D 的敏感性
    P("-" * 68)
    P("Part 4：折扣参数 D 的敏感性")
    P("-" * 68)

    P(f"\n  {'D':>6}  {'KN PPL':>10}")
    P("  " + "-" * 20)
    for D_val in [0.0, 0.25, 0.50, 0.75, 0.90, 0.99, 1.0]:
        ppl, _, _ = compute_ppl(stats, TEST_SENTENCES,
                                lambda s, w1, w2, D=D_val: prob_kneser_ney(s, w1, w2, D=D_val))
        tag = " ← 标准值" if D_val == 0.75 else (" ← 无折扣" if D_val == 0 else "")
        P(f"  {D_val:>6.2f}  {ppl:>10.1f}{tag}")

    # 总结
    P("=" * 68)
    P("一句话总结")
    P("=" * 68)
    P(f"""
  三种 bigram 平滑方法的 PPL:
    MLE (无平滑):      {ppl_mle:>8.1f}  ← 零概率，不可用
    Add-1 (Laplace):   {ppl_add1:>8.1f}  ← 过度打折
    Kneser-Ney:        {ppl_kn:>8.1f}  ← N-gram 平滑天花板

  ★ 反直觉:
    1. KN 比 Add-1 好 {((1 - ppl_kn/ppl_add1)*100):.0f}%+ (PPL 降 {(1 - ppl_kn/ppl_add1)*100:.0f}%+)
    2. 关键创新不是"折扣"(绝对折扣很简单)，
       而是 continuation probability —— 用"搭配多样性"
       替代"绝对频率"来做回退
    3. "Francisco" 问题: KN 正确处理了"高频但搭配单一"的词
""")


if __name__ == "__main__":
    main()
