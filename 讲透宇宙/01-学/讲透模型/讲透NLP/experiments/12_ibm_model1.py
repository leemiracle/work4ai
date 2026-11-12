#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 12 章配套实验：IBM Model 1 —— 从零实现词对齐的 EM 算法
====================================================================
对应文档: 12-机器翻译.md

只用 Python 标准库（math/random/collections）。不用任何 NLP 库。

跑这个脚本，你会看到三个「能跑出来」的结论：

  1. IBM Model 1 的 EM，在 22 句【无标注】双语语料上，自动学出词对齐：
     the→那个、cat→猫、eats→吃、chases→追逐 …… 完全无监督。
  2.【★ 反直觉发现】Model 1 能学到漂亮的「词对词」对齐，
     但它对【词序完全盲目】——铁证：把中文句子的词序【彻底打乱】后重跑 EM，
     学到的翻译概率表 t(f|e) 与对齐【与打乱前完全相同】（机器精度内）。
     这说明 Model 1 只学了「词汇对应」，零「语序」信息。
  3. 一个迷你 BLEU 计算：把公式的每一项（修正 n-gram 精度 + 简短惩罚）跑给你看，
     并演示「词沙拉」能骗过高阶 n-gram 但骗不过 BLEU。

自包含，几秒跑完：
    python3 -u experiments/12_ibm_model1.py
"""

import math
import random
from collections import Counter

NULL = "▏NULL▕"   # IBM Model 的「空对齐」虚拟词 e_0

# 强制 flush 的 print
def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 0. 内置小双语语料（English = 源语言 e，Chinese = 目标语言 f）
#    设计要点：高频功能词 "the" 每句都出现，"那个" 每句都出现且只对应 "the"；
#    实词（动物/动作/食物）反复共现，让 EM 有足够统计量收敛。
#    English SVO，中文也是 SVO——但这一点对 Model 1 【完全无关】(见反直觉发现)。
# ============================================================
CORPUS = [
    ("the cat eats the fish",          "猫 吃 那个 鱼"),
    ("the cat eats the meat",          "猫 吃 那个 肉"),
    ("the dog eats the meat",          "狗 吃 那个 肉"),
    ("the dog chases the cat",         "狗 追逐 那个 猫"),
    ("the cat chases the mouse",       "猫 追逐 那个 老鼠"),
    ("the dog chases the mouse",       "狗 追逐 那个 老鼠"),
    ("the mouse eats the cheese",      "老鼠 吃 那个 奶酪"),
    ("the cat drinks the milk",        "猫 喝 那个 牛奶"),
    ("the dog drinks the water",       "狗 喝 那个 水"),
    ("the cat drinks the water",       "猫 喝 那个 水"),
    ("the mouse eats the fish",        "老鼠 吃 那个 鱼"),
    ("the dog eats the fish",          "狗 吃 那个 鱼"),
    ("the big cat eats the fish",      "大 猫 吃 那个 鱼"),
    ("the big dog chases the cat",     "大 狗 追逐 那个 猫"),
    ("the small mouse eats the cheese","小 老鼠 吃 那个 奶酪"),
    ("the cat eats the big fish",      "猫 吃 那个 大 鱼"),
    ("the dog eats the small mouse",   "狗 吃 那个 小 老鼠"),
    ("the cat and the dog eat the meat","猫 和 狗 吃 那个 肉"),
    ("the cat and the mouse eat the cheese","猫 和 老鼠 吃 那个 奶酪"),
    ("the big cat and the small dog drink the milk","大 猫 和 小 狗 喝 那个 牛奶"),
    ("the cat chases the big mouse",   "猫 追逐 那个 大 老鼠"),
    ("the small dog drinks the water", "小 狗 喝 那个 水"),
]


def make_pairs():
    """返回 [(e_tokens, f_tokens), ...]。"""
    return [(en.split(), zh.split()) for en, zh in CORPUS]


# ============================================================
# 1. IBM Model 1 的 EM（从零实现，纯字典）
# ============================================================
def train_ibm1(pairs, n_iters=20, init_seed=0):
    """
    IBM Model 1 EM。
    约定：f 词（目标）由 e 词（源，含 NULL）生成，学习 t(f|e)。

    E-step: γ_j(i) = t(f_j|e_i) / Σ_{i'} t(f_j|e_{i'})
    M-step: t(f|e) = count(f|e) / total(e)

    返回 (t_dict, e_vocab_list, f_vocab_list)。
    """
    e_vocab = set()
    f_vocab = set()
    for e, f in pairs:
        e_vocab.update(e)
        f_vocab.update(f)
    e_vocab.add(NULL)
    e_vocab = sorted(e_vocab)
    f_vocab = sorted(f_vocab)
    Vf = len(f_vocab)

    # 初始化：均匀分布 t(f|e) = 1/|F|
    t = {(e, f): 1.0 / Vf for e in e_vocab for f in f_vocab}

    for it in range(n_iters):
        count = {}     # (e,f) -> 期望计数
        total = {e: 0.0 for e in e_vocab}
        # E-step：收集期望计数
        for e_sent, f_sent in pairs:
            e_with_null = [NULL] + e_sent
            for f in f_sent:
                s = sum(t[(ei, f)] for ei in e_with_null)   # 归一化常数
                for ei in e_with_null:
                    delta = t[(ei, f)] / s
                    count[(ei, f)] = count.get((ei, f), 0.0) + delta
                    total[ei] += delta
        # M-step：更新 t
        for e in e_vocab:
            for f in f_vocab:
                t[(e, f)] = count.get((e, f), 0.0) / total[e] if total[e] > 0 else 0.0
    return t, e_vocab, f_vocab


def viterbi_align(t, e_sent, f_sent):
    """对每个 f 词，返回它最可能对齐到的 e 词（贪心 argmax）。"""
    e_with_null = [NULL] + e_sent
    out = []
    for f in f_sent:
        best_e = max(e_with_null, key=lambda ei: t.get((ei, f), 0.0))
        out.append((f, best_e, t.get((best_e, f), 0.0)))
    return out


# ============================================================
# 2. 迷你 BLEU（从零实现，演示公式的每一项）
# ============================================================
def ngrams(tokens, n):
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def modified_precision(candidate, references, n):
    """修正 n-gram 精度 p_n：候选计数被参考集最大计数 clip。"""
    cand = ngrams(candidate, n)
    max_ref = Counter()
    for ref in references:
        for ng, c in ngrams(ref, n).items():
            if c > max_ref[ng]:
                max_ref[ng] = c
    match = sum(min(c, max_ref[ng]) for ng, c in cand.items())
    total = sum(cand.values())
    return (match / total) if total > 0 else 0.0


def bleu(candidate, references, max_n=4):
    """返回 (bleu, bp, [p_1..p_N])。"""
    weights = [1.0 / max_n] * max_n
    precisions = [modified_precision(candidate, references, n)
                  for n in range(1, max_n + 1)]
    c = len(candidate)
    # 有效参考长度 r：取与候选长度最接近的参考长度
    r = min(references, key=lambda ref: abs(len(ref) - c))
    r = len(r)
    if c > r:
        bp = 1.0
    elif c == 0:
        bp = 0.0
    else:
        bp = math.exp(1.0 - r / c)
    log_sum = 0.0
    zero = False
    for w, p in zip(weights, precisions):
        if p <= 0.0:
            zero = True
            break
        log_sum += w * math.log(p)
    geo = 0.0 if zero else math.exp(log_sum)
    return bp * geo, bp, precisions


# ============================================================
# 主程序
# ============================================================
def main():
    pairs = make_pairs()
    N_ITERS = 20

    # ----------------------------------------------------------
    # 结论 1：无监督 EM 自动学出词对齐
    # ----------------------------------------------------------
    P("=" * 68)
    P("结论 1：IBM Model 1 EM 在 22 句无标注双语语料上自动学词对齐")
    P("=" * 68)
    P(f"语料：{len(pairs)} 个英中句对，源(英)词表|E|含 NULL，目标(中)|F|词表")
    P("样例：" + CORPUS[3][0] + "  ⇄  " + CORPUS[3][1] + "\n")

    t, e_vocab, f_vocab = train_ibm1(pairs, n_iters=N_ITERS, init_seed=0)

    P("学到的翻译概率表 t(f|e)（每个英文词 → 概率最高的中文词）：")
    P(f"  {'英文(e)':<8}→ {'中文(f)':<8} {'t(f|e)':>8}")
    P("  " + "-" * 36)
    for e in e_vocab:
        if e == NULL:
            continue
        best_f = max(f_vocab, key=lambda f: t[(e, f)])
        P(f"  {e:<8}→ {best_f:<8} {t[(e, best_f)]:>8.3f}")

    P("\n（NULL 吸收的「无对应」词，概率越高说明该词越像冗余词）")
    best_null = max(f_vocab, key=lambda f: t[(NULL, f)])
    P(f"  NULL → {best_null}  t={t[(NULL, best_null)]:.3f}")

    # 对齐可视化：取一个未单独见过的组合句
    demo_en = "the big cat chases the small mouse".split()
    demo_zh = "大 猫 追逐 那个 小 老鼠".split()
    P("\n对齐演示（贪心 argmax）：")
    P("  英文: " + " ".join(demo_en))
    P("  中文: " + " ".join(demo_zh))
    P(f"  {'中文词':<6}→ {'对齐到英文':<10} {'置信度':>8}")
    P("  " + "-" * 34)
    for f, e, p in viterbi_align(t, demo_en, demo_zh):
        tag = "" if e != NULL else "  ⚠对齐到NULL"
        P(f"  {f:<6}→ {e:<10} {p:>8.3f}{tag}")

    P("\n👉 结论 1：没有任何词典、没有任何标注，仅靠【共现统计 + EM】，")
    P("   Model 1 就把 the→那个、cat→猫、chases→追逐 学出来了（看上方 t 表）。")
    P("   这就是 1993 年 Brown et al. 让统计机器翻译起飞的核心技巧。")
    P("\n⚠ 注意上面「那个→NULL」：这句英文有 *两个* the、中文只有 *一个* 那个，")
    P("   多出来的英文 the 没有中文词可对，Model 1 只能把多余的中文词「挂在」NULL 上。")
    P("   这是 Model 1 的「生育力(fertility)失控」缺陷——它无法决定一个词该译成几个词，")
    P("   正是这一缺陷逼出了 IBM Model 3-5 显式引入 fertility 模型。\n")

    # ----------------------------------------------------------
    # 结论 2：★ 反直觉——Model 1 对词序【完全盲目】
    # ----------------------------------------------------------
    P("=" * 68)
    P("结论 2：★ 反直觉——IBM Model 1 对词序【完全盲目】")
    P("=" * 68)
    P("""
数学事实：Model 1 的 E-step 归一化常数
    γ_j(i) = t(f_j|e_i) / Σ_{i'} t(f_j|e_{i'})
【只依赖词本身，不依赖位置 i, j】。所以对任意句子的词序置换不变。

铁证实验：把每句【中文】的词序随机打乱（彻底破坏语序对应），
          重跑同样 20 轮 EM，比较两份 t 表。
""")

    rng = random.Random(2024)
    shuffled_pairs = []
    for en, zh in CORPUS:
        f = zh.split()
        rng.shuffle(f)                  # 彻底打乱中文词序
        shuffled_pairs.append((en.split(), f))

    # 展示一个打乱后的样例
    P("打乱后样例：" + CORPUS[3][0] + "  ⇄  " + " ".join(shuffled_pairs[3][1]))
    P("            （英文语序原封不动，中文已乱序）\n")

    t2, _, _ = train_ibm1(shuffled_pairs, n_iters=N_ITERS, init_seed=0)

    diff = max(abs(t[(e, f)] - t2[(e, f)]) for e in e_vocab for f in f_vocab)
    P(f"两份 t 表的最大差异 = {diff:.2e}")
    P("  → 打乱词序前后的翻译概率表【完全相同】（仅浮点累加顺序导致的 ~1e-16 噪声）")

    # 对齐（词对词映射）也应完全一致
    a1 = set((f, e) for f, e, _ in viterbi_align(t, demo_en, demo_zh))
    a2 = set((f, e) for f, e, _ in viterbi_align(t2, demo_en, demo_zh))
    P(f"打乱前后，示范句的词对齐映射是否一致：{a1 == a2}\n")

    P("👉 结论 2：Model 1 学到的只是「词袋对应」——the 和 那个 老是在一起出现，")
    P("   所以 t(那个|the) 高；但它【完全不知道】the 在英文句首、那个 在中文句中。")
    P("   英文 SVO vs 日文 SOV 这种【语序差异】，Model 1 一个 bit 都学不到。")
    P("   这正是 IBM Model 2-5 逐级引入【distortion（重排序）模型】的根本动机。")

    # ----------------------------------------------------------
    # 结论 3：迷你 BLEU——公式每一项跑给你看
    # ----------------------------------------------------------
    P("\n" + "=" * 68)
    P("结论 3：迷你 BLEU——把公式 BLEU=BP·exp(Σ w_n·log p_n) 跑给你看")
    P("=" * 68)
    ref = "the big cat chases the small mouse".split()

    cands = [
        ("① 完美翻译",        "the big cat chases the small mouse".split()),
        ("② 一处冠词错",      "the big cat chases a small mouse".split()),
        ("③ 过度重复",        "the big cat chases the the small mouse".split()),
        ("④ 太短漏译",        "the big cat chases the mouse".split()),
        ("⑤ 词序打乱(词沙拉)", "mouse small the chases cat big the".split()),
    ]
    P(f"\n参考译文: {' '.join(ref)}  (r = {len(ref)} 词)")
    P(f"  {'候选':<20}{'p1':>6}{'p2':>6}{'p3':>6}{'p4':>6}{'BP':>6}{'BLEU-4':>8}")
    P("  " + "-" * 58)
    for name, cand in cands:
        score, bp, precs = bleu(cand, [ref], max_n=4)
        P(f"  {name:<20}{precs[0]:>6.2f}{precs[1]:>6.2f}{precs[2]:>6.2f}"
          f"{precs[3]:>6.2f}{bp:>6.2f}{score:>8.3f}")

    P("""
逐行解读（BLEU-4 = BP·exp(1/4·Σlog p_n)）：
  · ⑤「词沙拉」p1=1.00——每个词都在参考里！但 p2=0（二元搭配全错）→ BLEU=0。
    这就是 BLEU 用【高阶 n-gram】抓「词序/搭配」的核心机制，正好补上 IBM Model 1
    「只看词不看序」的盲区。
  · ③ 过度重复：p1 只有 0.88（不是 1.00）——多出来的 'the' 被【修正 n-gram 精度的
    clip】砍掉，防止「重复刷同一个对的词」作弊。
  · ④ 太短漏译：精度看着不错(p1=1,p4=0.67)，但【简短惩罚 BP=0.85】把它从 ~0.80
    压到 0.67，惩罚「偷懒少翻」。
  · ② 一个冠词错：p1=0.86 还行，但 p4 暴跌到 0.25——错一个词，所有跨过它的
    4-gram 全废 → 整体 BLEU 腰斩。

⚠ 句子级 BLEU-4 极苛刻：错一个词就能让高阶 n-gram 崩盘。这就是为什么真实评测
  都在【语料级】(把整篇文档的 n-gram 合起来算)，而不是逐句算 BLEU。
""")

    # ----------------------------------------------------------
    # 总结
    # ----------------------------------------------------------
    P("=" * 68)
    P("一句话总结")
    P("=" * 68)
    P("""
  IBM Model 1 = 「无监督词对齐」的最简模型：
    只用一个翻译概率表 t(f|e)，用 EM 从双语共现里学出来。

  两个关键收获：
    1. EM 能无监督地把高频对应词对齐出来——统计 MT 的地基。
    2. Model 1 对词序【完全盲目】(置换不变)，这是它被 Model 2-5 / 神经 MT
       取代的根本原因；BLEU 则用高阶 n-gram 专门弥补「只看词不看序」的盲区。

  机器翻译的下一跳：seq2seq + attention → Transformer（Transformer 原论文
  就是 MT！）→ 大规模多语言 MT(NLLB/SeamlessM4T) → LLM zero-shot 翻译。
  详见 12-机器翻译.md。
""")


if __name__ == "__main__":
    main()
