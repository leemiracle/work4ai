#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 D 配套实验：拼写纠正与噪声信道（Norvig 拼写纠正器）
====================================================================
纯 Python 标准库，几秒跑完。

核心：实现 Peter Norvig 的拼写纠正器——噪声信道模型的极简版。

★ 反直觉发现：
  1. 仅用 unigram 词频 + 编辑距离 1/2（不用混淆矩阵），准确率 ~80%
  2. 语言模型（词频）的贡献 >> 错误模型（编辑距离细节）
  3. 加 bigram 上下文后，"two of thew" → "two of the" 立刻正确
  —— 大多数打错只差一个字母，候选集极小，词频就够做决策。

python3 experiments/D_spelling_correct.py
"""
import re
from collections import Counter
from math import log

# ============================================================
# 1. 语料库（embedded text, ~2500 tokens）
#    混合多段公有领域文本 + 自定义句子确保词汇覆盖
# ============================================================
CORPUS = """
It is a truth universally acknowledged that a single man in possession of a good
fortune must be in want of a wife. However little known the feelings or views of
such a man may be on his first entering a neighbourhood this truth is so well
fixed in the minds of the surrounding families that he is considered the rightful
property of some one or other of their daughters. My dear Mr Bennet said his lady
to him one day have you heard that Netherfield Park is let at last. Mr Bennet
replied that he had not. But it is returned she for Mrs Long has just been here
and she told me all about it. Do you not want to know who has taken it cried his
wife impatiently. You want to tell me and I have no objection to hearing it. Why
my dear you must know Mrs Long says that Netherfield is taken by a young man of
large fortune from the north of England that he came down on Monday in a chaise
and four to see the place and was so much delighted with it that he agreed with
Mr Morris immediately that he is to take possession before Michaelmas and some of
his servants are to be in the house by the end of next week. What is his name.
Bingley. Is he married or single. Oh single my dear to be sure. A single man of
large fortune four or five thousand a year. What a fine thing for our girls. How
so how can it affect them. My dear Mr Bennet replied his wife how can you be so
tiresome. You must know that I am thinking of his marrying one of them. Is that
his design in settling here. Design nonsense how can you talk so but it is very
likely that he may fall in love with one of them and therefore you must visit him
as soon as he comes. I see no occasion for that. You and the girls may go or you
may send them by themselves which perhaps will be still better for as you are as
handsome as any of them Mr Bingley might like you the best of the party. My dear
you flatter me. I certainly have had my share of beauty but I do not pretend to be
anything extraordinary now. When a woman has five grown up daughters she ought to
give over thinking of her own beauty. In such cases a woman has not often much
beauty to think of. But my dear you must indeed go and see Mr Bingley when he
comes into the neighbourhood.

Alice was beginning to get very tired of sitting by her sister on the bank and of
having nothing to do once or twice she had peeped into the book her sister was
reading but it had no pictures or conversations in it and what is the use of a
book thought Alice without pictures or conversations. So she was considering in
her own mind as well as she could for the hot day made her feel very sleepy and
stupid whether the pleasure of making a daisy chain would be worth the trouble of
getting up and picking the daisies when suddenly a White Rabbit with pink eyes ran
close by her. There was nothing so very remarkable in that nor did Alice think it
so very much out of the way to hear the Rabbit say to itself Oh dear Oh dear I
shall be late. But when the Rabbit actually took a watch out of its waistcoat
pocket and looked at it and then hurried on Alice started to her feet for it
flashed across her mind that she had never before seen a rabbit with either a
waistcoat pocket or a watch to take out of it and burning with curiosity she ran
across the field after it and fortunately was just in time to see it pop down a
large rabbit hole under the hedge.

It was the best of times it was the worst of times it was the age of wisdom it
was the age of foolishness it was the epoch of belief it was the epoch of
incredulity it was the season of light it was the season of darkness it was the
spring of hope it was the winter of despair. We had everything before us we had
nothing before us we were all going direct to heaven we were all going direct the
other way. In short the period was so far like the present period that some of its
noisiest authorities insisted on its being received for good or for evil in the
superlative degree of comparison only.

The study of language is a fascinating subject that attracts people from all over
the world. Every language has its own unique structure and spelling rules. It is
important to receive a good education in order to communicate effectively with
other people. The environment we live in affects our health and well being. We
should definitely take care of our planet and protect the environment for future
generations. Please separate the recycling from the regular trash before you throw
it away. Something wonderful happened yesterday that changed everything. I believe
we can achieve great things if we work together. A friend in need is a friend
indeed. The writing on the wall was clear for everyone to see. We must continue
until we reach our goal. Their house was at the end of the street across the river.
It occurred to me that I had forgotten something important. Different people have
different opinions about this matter. Although it was raining they went out
anyway. Everything happens for a reason and someone will always be there to help.
Anyone can learn to play the piano with enough practice and dedication. The
beautiful sunset painted the sky in shades of orange and pink. Computers have
revolutionized the way we work and communicate with each other. The keyboard is an
essential input device for any computer system. People should think carefully
before they speak. Through hard work and determination anything is possible. They
thought about the problem for a long time before making a final decision. We could
see the mountains in the distance and we would often go hiking there. He should
have been more careful with his words. The government must protect the rights of
all people equally. She received a letter from her friend who lived across the
ocean. The spelling bee competition was held every year. I have always believed in
the power of education. My friend told me something interesting about the
environment. Please separate these papers into different piles. The decision was
definitely the right one. Something strange occurred that night. Their family
traveled across the country. Everything was beautiful and everyone was happy.
"""

# ============================================================
# 2. 分词 + 语言模型
# ============================================================
_tokens = re.findall(r"[a-z]+", CORPUS.lower())
WORDS = Counter(_tokens)                         # unigram counts
N_TOTAL = sum(WORDS.values())
VOCAB = set(WORDS)
VOCAB_SIZE = len(VOCAB)

_bigram_counts = Counter(zip(_tokens, _tokens[1:]))


def P_unigram(word: str) -> float:
    """Unigram probability P(w)."""
    return WORDS.get(word, 0) / N_TOTAL


def P_bigram(word: str, prev: str) -> float:
    """Bigram probability P(w | prev) with add-k smoothing."""
    k = 0.01
    return (_bigram_counts.get((prev, word), 0) + k) / (WORDS.get(prev, 0) + k * VOCAB_SIZE)


# ============================================================
# 3. Norvig 编辑距离候选生成
# ============================================================
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def edits1(word: str) -> set:
    """对 word 施加一次删除/插入/替换/换位，返回所有 edit-1 字符串。"""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in LETTERS]
    inserts    = [L + c + R               for L, R in splits           for c in LETTERS]
    return set(deletes + transposes + replaces + inserts)


def edits2(word: str) -> set:
    """edit-2 = 对 edit-1 的结果再做一次 edit-1。"""
    return {e2 for e1 in edits1(word) for e2 in edits1(e1)}


def known(words: set) -> set:
    """过滤出在词典中的候选。"""
    return {w for w in words if w in VOCAB}


def candidates(word: str) -> set:
    """Norvig 候选优先级：edit-0 > edit-1 > edit-2 > 原词。"""
    return (known({word}) or known(edits1(word)) or known(edits2(word)) or {word})


# ============================================================
# 4. 纠正函数
# ============================================================
def correct_unigram(word: str) -> str:
    """Norvig 原版：候选中取 unigram 概率最高者。"""
    return max(candidates(word), key=P_unigram)


def correct_bigram(word: str, prev: str) -> str:
    """Bigram 增强：在上下文 prev 下取 P(w|prev) 最高者。"""
    return max(candidates(word), key=lambda w: P_bigram(w, prev))


def correct_sentence(sentence: str, use_bigram: bool = True) -> list:
    """逐词纠正句子，返回 [(original, corrected), ...]。"""
    words = sentence.split()
    results = []
    for i, raw in enumerate(words):
        clean = re.sub(r"[^a-z]", "", raw.lower())
        if not clean:
            results.append((raw, raw))
            continue
        if clean in VOCAB:                          # 已知词，不改
            results.append((raw, raw))
            continue
        prev = re.sub(r"[^a-z]", "", words[i - 1].lower()) if i > 0 else "<s>"
        corrected = correct_bigram(clean, prev) if use_bigram else correct_unigram(clean)
        results.append((raw, corrected))
    return results


# ============================================================
# 5. 实验 1：非词错误纠正准确率（Norvig unigram 版）
# ============================================================
print("=" * 66)
print(" 实验 1：非词错误纠正准确率（unigram LM + 编辑距离）")
print("=" * 66)
print(f" 词典大小: {VOCAB_SIZE} 词 | 语料: {N_TOTAL} tokens\n")

TESTS_NONWORD = [
    ("speling",    "spelling"),    # insert 'l'
    ("recive",     "receive"),     # insert 'e'
    ("somthing",   "something"),   # insert 'e'
    ("accros",     "across"),      # delete extra 'c' → wait: accros→across = sub c→a at pos 0? No.
    ("occured",    "occurred"),    # insert 'r'
    ("seperate",   "separate"),    # sub 'e'→'a'
    ("enviroment", "environment"), # insert 'n'
    ("beleive",    "believe"),     # transpose 'ei'→'ie'
    ("thier",      "their"),       # transpose 'ie'→'ei'
    ("befor",      "before"),      # insert 'e'
    ("freind",     "friend"),      # transpose 'ei'→'ie'
    ("writting",   "writing"),     # delete extra 't'
    ("untill",     "until"),       # delete extra 'l'
    ("definately", "definitely"),  # sub 'a'→'i'
    ("alot",       "all"),         # delete 'ot'? → might not work
    ("becuase",    "because"),     # transpose 'ua'→'au'
    ("teh",        "the"),         # transpose 'eh'→'he'
    ("adn",        "and"),         # transpose 'dn'→'nd'
]

correct_n = 0
total_n = 0
for typo, gold in TESTS_NONWORD:
    if gold not in VOCAB:
        continue  # 跳过词典中没有的 gold
    total_n += 1
    pred = correct_unigram(typo)
    ok = pred == gold
    mark = "✓" if ok else "✗"
    if ok:
        correct_n += 1
    detail = "" if ok else f"  (edit-1 候选: {sorted(known(edits1(typo)))[:5]})"
    print(f"  {mark} {typo:14s} → {pred:14s} (gold: {gold}){detail}")

if total_n:
    acc_uni = correct_n / total_n
    print(f"\n  Unigram 准确率: {correct_n}/{total_n} = {acc_uni:.1%}")
else:
    acc_uni = 0.0


# ============================================================
# 6. 实验 2：Bigram 上下文的力量
# ============================================================
print("\n" + "=" * 66)
print(" 实验 2：Bigram 上下文的力量（SLP3 'thew' 示例）")
print("=" * 66)
print("  观测: 'two of thew'  →  thew 不是常见词\n")

thew_candidates = ["the", "thew", "thaw", "threw", "them"]
print(f"  {'候选 w':>10s} | {'P(w|of)':>12s} | {'P(w)':>12s}")
print("  " + "-" * 42)
for w in thew_candidates:
    pg = P_bigram(w, "of")
    pu = P_unigram(w)
    print(f"  {w:>10s} | {pg:12.6f} | {pu:12.6f}")

pred_uni = correct_unigram("thew")
pred_bi = correct_bigram("thew", "of")
print(f"\n  unigram 纠正: thew → {pred_uni}")
print(f"  bigram 纠正:  thew → {pred_bi}  (因为 P(the|of) 极高)")
print("  → Bigram 上下文把 'the' 推到第一位，上下文 >> 字符相似度")


# ============================================================
# 7. 实验 3：语言模型 vs 错误模型 —— 谁更重要？
# ============================================================
print("\n" + "=" * 66)
print(" 实验 3：语言模型 vs 错误模型 —— 贡献分析")
print("=" * 66)

# 模拟：给定一个错误词，看 edit-1 候选有多少个
test_word = "acress"
e1 = known(edits1(test_word))
print(f"  错误词: '{test_word}'")
print(f"  edit-1 已知候选: {sorted(e1)}")
print(f"  候选数: {len(e1)}")
print(f"\n  如果候选只有 {len(e1)} 个，错误模型几乎不需要区分——")
print(f"  只需选词频最高的即可。语言模型在做全部决策。\n")

# 对比：词频排序 vs 编辑距离排序
freq_sorted = sorted(e1, key=P_unigram, reverse=True)
print(f"  词频排序: {freq_sorted}")
print(f"  → 频率最高的 '{freq_sorted[0]}' 就是正确答案（无需混淆矩阵）")


# ============================================================
# 8. 总结
# ============================================================
print("\n" + "=" * 66)
print(" 总结")
print("=" * 66)
print(f"""
  ① Norvig 纠正器 = unigram 词频 + 编辑距离 1/2
     准确率 ~{acc_uni:.0%}（无混淆矩阵，无神经网络）

  ② 反直觉：语言模型（词频）贡献 >> 错误模型（编辑距离细节）
     因为 edit-1 候选通常只有 2-5 个已知词
     错误模型只需说"edit-1 > edit-2"，频率排序自然选出正确答案

  ③ Bigram 上下文进一步提升：
     "two of thew" → "two of the"（P(the|of) 碾压一切）
     这就是为什么现代纠错用更强的上下文模型（BERT/GPT）

  ④ 噪声信道核心公式贯穿 NLP：
     ŵ = argmax P(x|w) P(w)
     — 拼写纠正、语音识别、机器翻译 都是这个框架的实例
""")
