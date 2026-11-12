#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 03 章 实验：N元语法语言模型
=================================================
在莎士比亚小语料（公版十四行诗，自包含）上从零实现 unigram / bigram / trigram，
对比困惑度（无平滑 / add-K），跑出两个反直觉结论：

  发现 1：小语料上 trigram 的 PPL 反而高于 bigram（数据稀疏 → 高阶上下文命中率暴跌）
  发现 2：add-1（Laplace）严重过度平滑；最优 K ≈ 0.01–0.05 ≪ 1

依赖：仅 NumPy + 标准库。几秒跑完。
跑法：
    cd 讲透NLP
    python3 -u experiments/03_ngram_lm.py
"""
import re
import math
from collections import Counter, defaultdict

import numpy as np

# ---------------------------------------------------------------- 莎士比亚小语料（公版，5 首十四行诗，自包含）
CORPUS = """
shall i compare thee to a summer's day
thou art more lovely and more temperate
rough winds do shake the darling buds of may
and summer's lease hath all too short a date
sometime too hot the eye of heaven shines
and often is his gold complexion dimmed
and every fair from fair sometime declines
by chance or nature's changing course untrimmed
but thy eternal summer shall not fade
nor lose possession of that fair thou ow'st
nor shall death brag thou wand'rest in his shade
when in eternal lines to time thou grow'st
so long as men can breathe or eyes can see
so long lives this and this gives life to thee
let me not to the marriage of true minds
admit impediments love is not love
which alters when it alteration finds
or bends with the remover to remove
o no it is an ever fixed mark
that looks on tempests and is never shaken
it is the star to every wand'ring bark
whose worth's unknown although his height be taken
love's not time's fool though rosy lips and cheeks
within his bending sickle's compass come
love alters not with his brief hours and weeks
but bears it out even to the edge of doom
if this be error and upon me proved
i never writ nor no man ever loved
my mistress' eyes are nothing like the sun
coral is far more red than her lips' red
if snow be white why then her breasts are dun
if hairs be wires black wires grow on her head
i have seen roses damasked red and white
but no such roses see i in her cheeks
and in some perfumes is there more delight
than in the breath that from my mistress reeks
i love to hear her speak yet well i know
that music hath a far more pleasing sound
i grant i never saw a goddess go
my mistress when she walks treads on the ground
and yet by heaven i think my love as rare
as any she belied with false compare
when in disgrace with fortune and men's eyes
i all alone beweep my outcast state
and trouble deaf heaven with my bootless cries
and look upon myself and curse my fate
wishing me like to one more rich in hope
featured like him like him with friends possessed
desiring this man's art and that man's scope
with what i most enjoy contented least
yet in these thoughts myself almost despising
haply i think on thee and then my state
like to the lark at break of day arising
from sullen earth sings hymns at heaven's gate
for thy sweet love remembered such wealth brings
that then i scorn to change my state with kings
that time of year thou mayst in me behold
when yellow leaves or none or few do hang
upon those boughs which shake against the cold
bare ruined choirs where late the sweet birds sang
in me thou see'st the twilight of such day
as after sunset fadeth in the west
which by and by black night doth take away
death's second self that seals up all in rest
in me thou see'st the glowing of such fire
that on the ashes of his youth doth lie
as the deathbed whereon it must expire
consumed with that which it was nourished by
this thou perceiv'st which makes thy love more strong
to love that well which thou must leave ere long
"""

BOS, EOS = "<s>", "</s>"


def tokenize_lines(corpus):
    """每行一句；小写化，保留词内撇号（summer's / ow'st），其余按词切分。"""
    return [re.findall(r"[a-z']+", ln.strip().lower())
            for ln in corpus.strip().splitlines() if ln.strip()]


def pad(sents, n):
    """给每句加 (n-1) 个 <s> 前缀和 1 个 </s> 后缀。"""
    return [[BOS] * (n - 1) + s + [EOS] for s in sents]


def build_counts(padded, n):
    """counts[context_tuple] = Counter(下一个词)。"""
    counts = defaultdict(Counter)
    for s in padded:
        for i in range(len(s) - n + 1):
            ctx = tuple(s[i:i + n - 1])
            counts[ctx][s[i + n - 1]] += 1
    return counts


def perplexity(test_padded, n, counts, V, k):
    """
    add-k 平滑下的困惑度。k==0 表示无平滑：遇到训练时未见的 n-gram 记 inf。
    返回 (ppl, 总预测数, 未命中数)。
    """
    log_sum, total, unseen = 0.0, 0, 0
    for s in test_padded:
        for i in range(n - 1, len(s)):
            ctx = tuple(s[i - n + 1:i])
            w = s[i]
            den = sum(counts[ctx].values())
            num = counts[ctx][w]
            if k == 0:
                if num == 0:
                    unseen += 1
                    continue
                p = num / den
            else:
                p = (num + k) / (den + k * V)
            log_sum += math.log(p)
            total += 1
    if unseen:
        return float("inf"), total + unseen, unseen
    return math.exp(-log_sum / total) if total else float("inf"), total, 0


def generate(counts_bigram, seed, max_len=25):
    """从 bigram 模型采样生成（按计数加权随机）。"""
    rng = np.random.default_rng(seed)
    ctx, out = (BOS,), []
    for _ in range(max_len):
        c = counts_bigram.get(ctx)
        if not c:
            break
        words = list(c.keys())
        probs = np.array(list(c.values()), dtype=float)
        probs /= probs.sum()
        w = rng.choice(words, p=probs)
        if w == EOS:
            break
        out.append(w)
        ctx = (w,)
    return " ".join(out)


def main():
    sents = tokenize_lines(CORPUS)
    n_test = max(1, len(sents) // 6)
    train, test = sents[:-n_test], sents[-n_test:]

    vocab = sorted({w for s in sents for w in s} | {EOS})
    V = len(vocab)
    print("=" * 68)
    print("讲透NLP Ch3 · N元语法语言模型实验（莎士比亚小语料）")
    print("=" * 68)
    print(f"语料 {len(sents)} 行 | 训练 {len(train)} 行 | 测试 {len(test)} 行 | 词汇表 V={V}")

    names = {1: "unigram", 2: "bigram ", 3: "trigram"}
    models = {}
    print("\n[表 A] 三种阶数 × 三种平滑 的测试集困惑度（越低越好）")
    print("-" * 68)
    print(f"{'阶数':<9}{'无平滑':>14}{'add-1':>12}{'add-0.01':>13}")
    print("-" * 68)
    for n in (1, 2, 3):
        tr_p, te_p = pad(train, n), pad(test, n)
        cnt = build_counts(tr_p, n)
        models[n] = (te_p, cnt)
        p0, N0, u0 = perplexity(te_p, n, cnt, V, 0)
        p1, _, _ = perplexity(te_p, n, cnt, V, 1.0)
        p01, _, _ = perplexity(te_p, n, cnt, V, 0.01)
        s0 = f"inf({u0}/{N0})" if math.isinf(p0) else f"{p0:.1f}"
        print(f"{names[n]:<9}{s0:>14}{p1:>12.1f}{p01:>13.1f}")

    print("\n" + "=" * 68)
    print("【反直觉发现 1】阶数越高，PPL 不一定越低（数据稀疏爆炸）")
    print("=" * 68)
    print("固定 add-0.01 平滑，横向比较三种阶数：")
    for n in (1, 2, 3):
        te_p, cnt = models[n]
        p, _, _ = perplexity(te_p, n, cnt, V, 0.01)
        bar = "#" * int(min(60, p / max(1, V) * 60))
        print(f"  {names[n]}  PPL = {p:7.1f}   {bar}")
    print("  ==> trigram 的 2 词上下文在跨诗测试里几乎全未命中 → 大量位置退化为 1/V，")
    print("      PPL 反而最高（最差）。小数据下 bigram 才是甜点阶数。")

    print("\n" + "=" * 68)
    print("【反直觉发现 2】add-1（Laplace）过度平滑，最优 K ≪ 1")
    print("=" * 68)
    te2, cnt2 = models[2]
    print("bigram 的 K 扫描：")
    Ks = [1, 0.5, 0.1, 0.05, 0.01, 0.001, 1e-4]
    best_k, best_ppl = None, float("inf")
    for k in Ks:
        p, _, _ = perplexity(te2, 2, cnt2, V, k)
        tag = "  <-- add-1（教材默认，最差）" if k == 1 else ""
        print(f"  K = {k:<8g}  PPL = {p:9.1f}{tag}")
        if p < best_ppl:
            best_k, best_ppl = k, p
    print(f"  ==> 最优 K ≈ {best_k}，PPL ≈ {best_ppl:.1f}。add-1 的 PPL 比最优值高出数倍~数十倍。")

    demo_ctx = ("the",) if ("the",) in cnt2 else max(cnt2, key=lambda c: sum(cnt2[c].values()))
    top_w = cnt2[demo_ctx].most_common(1)[0][0]
    c_ctx = sum(cnt2[demo_ctx].values())
    c_top = cnt2[demo_ctx][top_w]
    print(f"\n  以训练集上下文 {demo_ctx} 为例：C(上下文)={c_ctx}, 其后最常见词='{top_w}' C={c_top}")
    print(f"    MLE       P('{top_w}'|{demo_ctx[0]}) = {c_top / c_ctx:.3f}   （无平滑真相）")
    print(f"    add-1     P('{top_w}'|{demo_ctx[0]}) = {(c_top + 1) / (c_ctx + V):.3f}   "
          f"<-- 被 V={V} 严重稀释")
    print(f"    add-0.01  P('{top_w}'|{demo_ctx[0]}) = {(c_top + 0.01) / (c_ctx + 0.01 * V):.3f}   "
          f"<-- 接近 MLE，保留信号")

    print("\n" + "=" * 68)
    print('【彩蛋】用 bigram 模型采样生成"莎士比亚风"句子（贪心结构，词级乱搭）')
    print("=" * 68)
    for seed in range(3):
        print(f"  [{seed}] " + generate(cnt2, seed))

    print("\n" + "-" * 68)
    print("三条铁律结论：")
    print("  ① 无平滑 → 测试集必有未命中 → PPL = inf（零概率问题）。")
    print("  ② 小数据上 trigram PPL > bigram PPL：高阶 ≠ 更好，取决于数据量。")
    print("  ③ add-1 过度平滑；工程实际用 add-k(k≪1) 或 Kneser-Ney。")
    print("  这正是神经语言模型（连续表示 + softmax 天然平滑）取代 N-gram 的根因。")
    print("-" * 68)


if __name__ == "__main__":
    main()
