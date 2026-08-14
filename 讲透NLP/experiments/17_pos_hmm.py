#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 17 章配套实验：HMM 词性标注（从零实现）
====================================================================
只用 Python 标准库 + NumPy（不用 NLTK / sklearn / torch）。

跑这个脚本，你会看到四个「能跑出来」的结论：

  1. 在小语料上训 HMM POS tagger（转移概率矩阵 A + 发射概率矩阵 B）
  2. 从零实现 Viterbi 解码（动态规划，对数空间，带回溯）
  3. 消融实验：转移 vs 发射，各自贡献多少？
     · 发射概率贡献了大部分 token 准确率（已知词大多无歧义 → 符合直觉）
     · 但 ★ 转移概率是处理未知词（OOV）的唯一机制：
       去掉转移 → 未知词准确率从 84.6% 直接归零（0.0%）
  4. 未知词也能靠上下文（转移概率）猜对词性——"标签序列的语法骨架"
     不需要见过这个词就能工作。

自包含，几秒跑完：
    python3 experiments/17_pos_hmm.py
"""

import math
import numpy as np

SEED = 42
np.random.seed(SEED)


# ============================================================
# 1. 小型标注语料（Penn Treebank 风格 / slash 格式）
# ============================================================
# 故意用有限词汇让词频重复，保证发射概率可估。
# 包含歧义词（back/can/set/like/run/walk），在不同句法位置出现不同词性。
CORPUS_RAW = """\
the/DT dog/NN barks/VBZ ./.
the/DT cat/NN sleeps/VBZ ./.
a/DT man/NN walks/VBZ ./.
the/DT woman/NN writes/VBZ ./.
the/DT boy/NN plays/VBZ ./.
the/DT girl/NN sings/VBZ ./.
the/DT bird/NN flies/VBZ ./.
the/DT fish/NN swims/VBZ ./.
the/DT child/NN reads/VBZ ./.
the/DT teacher/NN talks/VBZ ./.
the/DT dog/NN ran/VBD ./.
the/DT cat/NN slept/VBD ./.
a/DT man/NN walked/VBD ./.
the/DT woman/NN wrote/VBD ./.
the/DT boy/NN played/VBD ./.
the/DT girl/NN sang/VBD ./.
the/DT bird/NN flew/VBD ./.
the/DT fish/NN swam/VBD ./.
the/DT child/NN read/VBD ./.
the/DT teacher/NN talked/VBD ./.
the/DT dogs/NNS bark/VBP ./.
the/DT cats/NNS sleep/VBP ./.
the/DT men/NNS walk/VBP ./.
the/DT women/NNS write/VBP ./.
the/DT boys/NNS play/VBP ./.
the/DT girls/NNS sing/VBP ./.
the/DT birds/NNS fly/VBP ./.
the/DT fish/NNS swim/VBP ./.
the/DT children/NNS read/VBP ./.
the/DT teachers/NNS talk/VBP ./.
the/DT big/JJ dog/NN runs/VBZ ./.
the/DT small/JJ cat/NN sleeps/VBZ ./.
a/DT red/JJ car/NN drives/VBZ ./.
the/DT old/JJ man/NN walks/VBZ ./.
the/DT young/JJ girl/NN sings/VBZ ./.
the/DT fast/JJ bird/NN flies/VBZ ./.
the/DT slow/JJ turtle/NN crawls/VBZ ./.
a/DT tall/JJ tree/NN stands/VBZ ./.
the/DT happy/JJ boy/NN plays/VBZ ./.
the/DT sad/JJ girl/NN cries/VBZ ./.
the/DT good/JJ book/NN sells/VBZ ./.
the/DT bad/JJ dog/NN bites/VBZ ./.
the/DT dog/NN will/MD run/VB ./.
the/DT man/NN can/MD walk/VB ./.
the/DT woman/NN must/MD write/VB ./.
the/DT boy/NN may/MD play/VB ./.
the/DT girl/NN should/MD sing/VB ./.
the/DT bird/NN will/MD fly/VB ./.
the/DT fish/NN can/MD swim/VB ./.
the/DT dogs/NNS will/MD run/VB ./.
the/DT cats/NNS can/MD sleep/VB ./.
the/DT men/NNS must/MD walk/VB ./.
she/PRP runs/VBZ ./.
he/PRP walks/VBZ ./.
it/PRP sleeps/VBZ ./.
she/PRP writes/VBZ ./.
he/PRP plays/VBZ ./.
she/PRP sings/VBZ ./.
he/PRP ran/VBD ./.
she/PRP walked/VBD ./.
it/PRP slept/VBD ./.
he/PRP wrote/VBD ./.
she/PRP played/VBD ./.
she/PRP will/MD run/VB ./.
he/PRP can/MD walk/VB ./.
they/PRP should/MD play/VB ./.
we/PRP must/MD go/VB ./.
I/PRP will/MD read/VB ./.
you/PRP can/MD sing/VB ./.
they/PRP run/VBP ./.
we/PRP walk/VBP ./.
I/PRP play/VBP ./.
you/PRP sing/VBP ./.
they/PRP read/VBP ./.
the/DT cat/NN runs/VBZ in/IN the/DT park/NN ./.
the/DT dog/NN sleeps/VBZ on/IN the/DT bed/NN ./.
the/DT man/NN walks/VBZ to/IN the/DT store/NN ./.
a/DT bird/NN flies/VBZ over/IN the/DT house/NN ./.
the/DT fish/NN swims/VBZ in/IN the/DT water/NN ./.
the/DT boy/NN plays/VBZ with/IN the/DT ball/NN ./.
the/DT dog/NN and/CC the/DT cat/NN play/VBP ./.
the/DT man/NN and/CC the/DT woman/NN walk/VBP ./.
a/DT boy/NN and/CC a/DT girl/NN sing/VBP ./.
the/DT dogs/NNS and/CC the/DT cats/NNS run/VBP ./.
the/DT dog/NN is/VBZ running/VBG ./.
the/DT cat/NN is/VBZ sleeping/VBG ./.
a/DT man/NN is/VBZ walking/VBG ./.
the/DT woman/NN is/VBZ writing/VBG ./.
the/DT boy/NN is/VBZ playing/VBG ./.
the/DT dogs/NNS are/VBP running/VBG ./.
the/DT cats/NNS are/VBP sleeping/VBG ./.
the/DT men/NNS are/VBP walking/VBG ./.
the/DT dog/NN has/VBZ run/VBN ./.
the/DT cat/NN has/VBZ slept/VBN ./.
the/DT book/NN was/VBD read/VBN ./.
the/DT song/NN was/VBD sung/VBN ./.
the/DT food/NN was/VBD eaten/VBN ./.
I/PRP have/VBP two/CD dogs/NNS ./.
she/PRP has/VBZ three/CD cats/NNS ./.
the/DT man/NN has/VBZ one/CD car/NN ./.
five/CD birds/NNS fly/VBP ./.
two/CD fish/NNS swim/VBP ./.
Mary/NNP runs/VBZ ./.
John/NNP walks/VBZ ./.
Mary/NNP will/MD sing/VB ./.
John/NNP can/MD play/VB ./.
Mary/NNP ran/VBD ./.
John/NNP wrote/VBD ./.
she/PRP will/MD back/VB the/DT bill/NN ./.
the/DT back/NN of/IN the/DT house/NN is/VBZ red/JJ ./.
go/VB back/RB now/RB ./.
they/PRP can/MD fish/VB ./.
the/DT can/NN is/VBZ on/IN the/DT table/NN ./.
she/PRP set/VBD the/DT table/NN ./.
the/DT set/NN is/VBZ ready/JJ ./.
I/PRP like/VBP the/DT book/NN ./.
birds/NNS like/VBP the/DT food/NN ./.
she/PRP runs/VBZ fast/RB ./.
the/DT fast/JJ car/NN is/VBZ red/JJ ./.
the/DT dog/NN runs/VBZ fast/RB ./.
the/DT old/JJ man/NN walks/VBZ slowly/RB ./.
a/DT big/JJ dog/NN runs/VBZ faster/RBR ./.
the/DT small/JJ cat/NN runs/VBZ fastest/RBS ./.
the/DT red/JJ car/NN is/VBZ faster/RBR ./.
the/DT good/JJ dog/NN is/VBZ the/DT best/JJS ./.
"""


def parse_corpus(raw):
    """解析 slash 格式语料 → [(word, tag), ...] 的列表"""
    corpus = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        tokens = []
        for pair in line.split():
            if "/" in pair:
                word, tag = pair.rsplit("/", 1)
                tokens.append((word.lower(), tag))
            else:
                tokens.append((pair.lower(), "."))
        corpus.append(tokens)
    return corpus


CORPUS = parse_corpus(CORPUS_RAW)


# ============================================================
# 2. HMM 训练：估计转移概率 A 与发射概率 B
# ============================================================
START, END = "<s>", "</s>"


class HMMTagger:
    """
    隐马尔可夫词性标注器。

    状态 = 词性标签；观测 = 词。
    转移概率 A[tag_prev][tag]   ≈ P(tag_i | tag_{i-1})
    发射概率 B[tag][word]       ≈ P(word_i | tag_i)

    add-k 平滑处理零概率；未知词用均匀发射。
    """

    def __init__(self, k_transition=0.0, k_emission=0.5):
        self.k_trans = k_transition    # 转移平滑
        self.k_emit = k_emission       # 发射平滑
        self.tags = []
        self.tag2i = {}
        self.vocab = set()
        # 概率表（对数空间）
        self.logA = None    # (n_states, n_states)  含 START/END
        self.logB = None    # (n_tags, n_vocab)
        self.word2i = {}

    # ---------- 训练 ----------
    def fit(self, sentences):
        """sentences: [[(word, tag), ...], ...]"""
        tag_counts = {}
        bigram_counts = {}    # (prev, cur) -> count
        emit_counts = {}      # (tag, word) -> count

        for sent in sentences:
            tags = [START] + [t for _, t in sent] + [END]
            for i in range(len(tags) - 1):
                prev, cur = tags[i], tags[i + 1]
                bigram_counts[(prev, cur)] = bigram_counts.get((prev, cur), 0) + 1
                tag_counts[prev] = tag_counts.get(prev, 0) + 1
            tag_counts[tags[-1]] = tag_counts.get(tags[-1], 0) + 1

            for word, tag in sent:
                emit_counts[(tag, word)] = emit_counts.get((tag, word), 0) + 1
                self.vocab.add(word)

        real_tags = sorted({t for s in sentences for _, t in s})
        self.tags = real_tags
        self.tag2i = {t: i for i, t in enumerate(real_tags)}
        self.word2i = {w: i for i, w in enumerate(sorted(self.vocab))}
        n_tags = len(real_tags)
        n_vocab = len(self.vocab)

        all_states = [START] + real_tags + [END]
        state2i = {s: i for i, s in enumerate(all_states)}

        # --- 转移概率 A: P(cur|prev) = (count(prev,cur)+k) / (count(prev)+k*N) ---
        N_trans = len(all_states)
        self.logA = np.full((len(all_states), len(all_states)), -1e18)
        for prev in all_states:
            denom = tag_counts.get(prev, 0) + self.k_trans * N_trans
            if denom == 0:
                denom = N_trans
            for cur in all_states:
                if prev == END or cur == START:
                    continue
                if prev == START and cur == END:
                    continue
                c = bigram_counts.get((prev, cur), 0)
                p = (c + self.k_trans) / denom
                self.logA[state2i[prev], state2i[cur]] = math.log(max(p, 1e-18))

        # --- 发射概率 B: P(word|tag) = (count(tag,word)+k) / (count(tag)+k*V) ---
        tag_totals = {}
        for (tag, word), c in emit_counts.items():
            tag_totals[tag] = tag_totals.get(tag, 0) + c
        self.logB = np.full((n_tags, n_vocab), -1e18)
        for ti, tag in enumerate(real_tags):
            denom = tag_totals.get(tag, 0) + self.k_emit * n_vocab
            if denom == 0:
                denom = n_vocab
            for wi, word in enumerate(sorted(self.vocab)):
                c = emit_counts.get((tag, word), 0)
                p = (c + self.k_emit) / denom
                self.logB[ti, wi] = math.log(max(p, 1e-18))

        self._uniform_emit = -math.log(n_vocab)   # log(1/V)

    # ---------- 发射分数（支持未知词 + 消融模式）----------
    def emission_logprob(self, ti, word, mode="normal"):
        """mode: 'normal'(正常发射; 未知词→均匀) / 'uniform'(所有词均匀)"""
        if mode == "uniform":
            return self._uniform_emit
        wi = self.word2i.get(word)
        if wi is not None:
            return self.logB[ti, wi]
        return self._uniform_emit   # 未知词 → 均匀

    # ---------- Viterbi 解码 ----------
    def viterbi(self, words, emit_mode="normal", trans_mode="normal"):
        """对数空间 Viterbi，O(T·N²)。"""
        T = len(words)
        N = len(self.tags)
        all_states = [START] + self.tags + [END]
        M = len(all_states)
        si_start = 0

        if trans_mode == "uniform":
            uniform_trans = -math.log(M)

        def trans_logprob(prev_state, cur_state):
            if trans_mode == "uniform":
                return uniform_trans
            return self.logA[prev_state, cur_state]

        dp = np.full((T + 1, M), -1e18)
        bp = np.full((T + 1, M), -1, dtype=int)

        # 初始化
        for j in range(N):
            trans = trans_logprob(si_start, j + 1)
            emit = self.emission_logprob(j, words[0], emit_mode)
            dp[0, j + 1] = trans + emit
            bp[0, j + 1] = si_start

        # 递推
        for t in range(1, T):
            for j in range(N):
                emit = self.emission_logprob(j, words[t], emit_mode)
                best_val, best_prev = -1e18, 0
                for i in range(N):
                    val = dp[t - 1, i + 1] + trans_logprob(i + 1, j + 1)
                    if val > best_val:
                        best_val, best_prev = val, i + 1
                dp[t, j + 1] = best_val + emit
                bp[t, j + 1] = best_prev

        # 终止
        best_val, best_last = -1e18, 0
        for i in range(N):
            val = dp[T - 1, i + 1] + trans_logprob(i + 1, M - 1)
            if val > best_val:
                best_val, best_last = val, i + 1

        # 回溯
        path = []
        cur = best_last
        for t in range(T - 1, -1, -1):
            path.append(self.tags[cur - 1])
            cur = bp[t, cur]
        path.reverse()
        return path


# ============================================================
# 3. 评估工具
# ============================================================
def evaluate(tagger, sentences, emit_mode="normal", trans_mode="normal"):
    total, correct = 0, 0
    sent_total, sent_correct = 0, 0
    for sent in sentences:
        words = [w for w, _ in sent]
        gold = [t for _, t in sent]
        pred = tagger.viterbi(words, emit_mode, trans_mode)
        for g, p in zip(gold, pred):
            total += 1
            if g == p:
                correct += 1
        sent_total += 1
        if gold == pred:
            sent_correct += 1
    return correct / total, sent_correct / sent_total


def evaluate_known_unknown(tagger, sentences, train_words,
                           emit_mode="normal", trans_mode="normal"):
    known_t, known_c = 0, 0
    unk_t, unk_c = 0, 0
    for sent in sentences:
        words = [w for w, _ in sent]
        gold = [t for _, t in sent]
        pred = tagger.viterbi(words, emit_mode, trans_mode)
        for w, g, p in zip(words, gold, pred):
            if w in train_words:
                known_t += 1
                known_c += 1 if g == p else 0
            else:
                unk_t += 1
                unk_c += 1 if g == p else 0
    ka = known_c / known_t if known_t else 0
    ua = unk_c / unk_t if unk_t else 0
    return ka, ua, known_t, unk_t


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 68)
    print("讲透NLP · 17 序列标注 POS 与 NER — HMM 词性标注（从零实现）")
    print("=" * 68)
    n_tokens = sum(len(s) for s in CORPUS)
    print(f"语料：{len(CORPUS)} 句，{n_tokens} 个 token")

    # --- 训练/测试划分（固定 seed）---
    rng = np.random.RandomState(SEED)
    indices = rng.permutation(len(CORPUS))
    n_test = len(CORPUS) // 5       # 20% 测试
    test_idx = set(indices[:n_test].tolist())
    train_idx = set(indices[n_test:].tolist())
    train_sents = [CORPUS[i] for i in sorted(train_idx)]
    test_sents = [CORPUS[i] for i in sorted(test_idx)]
    print(f"划分：训练 {len(train_sents)} 句 / 测试 {len(test_sents)} 句")

    tagger = HMMTagger(k_transition=0.01, k_emission=0.5)
    tagger.fit(train_sents)
    train_words = set()
    for s in train_sents:
        for w, _ in s:
            train_words.add(w)
    print(f"标签集：{len(tagger.tags)} 个词性 | 词汇表：{len(tagger.vocab)} 个词（训练集）")
    print(f"标签：{', '.join(tagger.tags)}\n")

    # =========================================================
    # 结论 1：完整 HMM 基线 + Viterbi 解码示例
    # =========================================================
    print("─" * 68)
    print("结论 1：完整 HMM（转移 A + 发射 B）+ Viterbi 解码")
    print("─" * 68)
    acc_tok, acc_sent = evaluate(tagger, test_sents)
    print(f"测试集 token 准确率 = {acc_tok*100:.1f}%")
    print(f"测试集 句子完全正确 = {acc_sent*100:.1f}%\n")

    demo = [("she", "PRP"), ("will", "MD"), ("back", "VB"),
            ("the", "DT"), ("bill", "NN"), (".", ".")]
    words = [w for w, _ in demo]
    gold = [t for _, t in demo]
    pred = tagger.viterbi(words)
    print("  歧义句解码示例（back 可作 VB / NN / RB / JJ / VBD）：")
    print(f"  句子 : {' '.join(words)}")
    print(f"  金标 : {' '.join(gold)}")
    print(f"  预测 : {' '.join(pred)}")
    print(f"  结果 : {'✓' if gold == pred else '✗'}\n")

    # =========================================================
    # 结论 2：消融实验——转移 vs 发射，各贡献多少？
    # =========================================================
    print("═" * 68)
    print("结论 2：消融实验（ablation）—— 转移 vs 发射，谁贡献更多？")
    print("═" * 68)
    print("""
  方法设计：
    · 完整模型  ：转移 A + 发射 B（正常 HMM）
    · 屏蔽发射B ：所有词均匀发射 → 只剩转移信号
    · 屏蔽转移A ：所有标签转移等概率 → 只剩发射信号（≈ unigram 标注器）
""")

    results = {}
    for name, em, tm in [("完整 HMM (A+B)", "normal", "normal"),
                         ("屏蔽发射B (只用转移)", "uniform", "normal"),
                         ("屏蔽转移A (只用发射)", "normal", "uniform")]:
        a_tok, _ = evaluate(tagger, test_sents, em, tm)
        results[name] = a_tok

    base = results["完整 HMM (A+B)"]
    print(f"  {'模型':<22} {'token准确率':>12} {'相对完整模型':>14}")
    print("  " + "-" * 52)
    for name, a_tok in results.items():
        delta = a_tok - base
        sign = "+" if delta >= 0 else ""
        print(f"  {name:<22} {a_tok*100:>11.1f}% {sign}{delta*100:>11.1f}pp")

    drop_mask_trans = base - results["屏蔽转移A (只用发射)"]   # 屏蔽转移 → 掉多少
    drop_mask_emit = base - results["屏蔽发射B (只用转移)"]   # 屏蔽发射 → 掉多少
    print(f"""
  读法：
    · 屏蔽转移A（只用发射）: 准确率从 {base*100:.1f}% → {results['屏蔽转移A (只用发射)']*100:.1f}%，掉了 {drop_mask_trans*100:.1f}pp
    · 屏蔽发射B（只用转移）: 准确率从 {base*100:.1f}% → {results['屏蔽发射B (只用转移)']*100:.1f}%，掉了 {drop_mask_emit*100:.1f}pp

  → 整体 token 准确率上，发射概率贡献更大（屏蔽发射掉 {drop_mask_emit*100:.1f}pp vs 屏蔽转移掉 {drop_mask_trans*100:.1f}pp）。
    这符合直觉：大部分词是【无歧义】的——"dog" 几乎总是 NN，"barks" 几乎
    总是 VBZ——光看词本身就能标对。转移概率额外贡献 {drop_mask_trans*100:.1f}pp，
    似乎只是"锦上添花"。

  但先别下结论——接下来看未知词。
""")

    # =========================================================
    # 结论 3 ★：未知词——转移概率的真正威力
    # =========================================================
    print("═" * 68)
    print("结论 3 ★【反直觉】未知词（OOV）：转移概率是唯一救命稻草")
    print("═" * 68)

    ka, ua, n_known, n_unk = evaluate_known_unknown(
        tagger, test_sents, train_words)
    ka_e, ua_e, _, _ = evaluate_known_unknown(
        tagger, test_sents, train_words, trans_mode="uniform")
    ka_t, ua_t, _, _ = evaluate_known_unknown(
        tagger, test_sents, train_words, emit_mode="uniform")

    print(f"  测试集中：已知词 {n_known} 个 / 未知词 {n_unk} 个\n")
    print(f"  {'模型':<22} {'已知词准确率':>12} {'未知词准确率':>12}")
    print("  " + "-" * 50)
    print(f"  {'完整 HMM (A+B)':<22} {ka*100:>11.1f}% {ua*100:>11.1f}%")
    print(f"  {'屏蔽转移A (只用发射)':<22} {ka_e*100:>11.1f}% {ua_e*100:>11.1f}%")
    print(f"  {'屏蔽发射B (只用转移)':<22} {ka_t*100:>11.1f}% {ua_t*100:>11.1f}%")

    print(f"""
  ★ 反直觉发现：
    完整模型对未知词准确率 = {ua*100:.1f}%
    屏蔽转移后未知词准确率 = {ua_e*100:.1f}%  ← 直接归零！

    去掉转移概率后，未知词准确率从 {ua*100:.1f}% 暴跌到 {ua_e*100:.1f}%。
    原因：发射概率对未知词毫无信息（词没见过 → 均匀分布），唯一能帮你
    的就是"标签序列的语法骨架"——前一个词性是什么，决定了当前词性
    最可能是什么。没有转移 = 没有任何 OOV 处理能力。

    这才是转移概率的真正价值：不是锦上添花，而是 OOV 的【全部】。
""")

    # =========================================================
    # 结论 4：未知词靠上下文猜词性——具体案例
    # =========================================================
    print("─" * 68)
    print("结论 4：未知词靠上下文猜词性——具体案例")
    print("─" * 68)
    unk_sentences = [
        [("the", "DT"), ("blue", "JJ"), ("elephant", "NN"),
         ("trumpets", "VBZ"), (".", ".")],
        [("a", "DT"), ("dragon", "NN"), ("will", "MD"),
         ("fly", "VB"), (".", ".")],
        [("the", "DT"), ("robot", "NN"), ("and", "CC"),
         ("the", "DT"), ("alien", "NN"), ("talk", "VBP"), (".", ".")],
    ]
    print("  （'elephant' / 'dragon' / 'robot' / 'alien' 在训练集中未出现）\n")
    for sent in unk_sentences:
        words = [w for w, _ in sent]
        gold = [t for _, t in sent]
        pred_full = tagger.viterbi(words)
        pred_trans = tagger.viterbi(words, emit_mode="uniform")
        print(f"  句子  : {' '.join(words)}")
        print(f"  金标  : {' '.join(gold)}")
        print(f"  完整  : {' '.join(pred_full)}  "
              f"{'✓' if pred_full == gold else '✗'}")
        print(f"  仅转移: {' '.join(pred_trans)}  "
              f"{'✓' if pred_trans == gold else '✗'}")
        print()

    print("  ★ 即使词从未见过，'DT JJ ___ VBZ' 这个转移模式也强烈暗示")
    print("    空格处 = NN。转移概率编码的是语言的句法骨架，与具体词汇无关。")
    print("    这也是为什么 HMM / CRF 在低资源、高 OOV 场景至今有用——")
    print("    语法是通用的，不需要为每个新词重新训练。\n")

    # =========================================================
    # 总结
    # =========================================================
    print("═" * 68)
    print("一句话总结")
    print("═" * 68)
    print(f"""
  HMM 词性标注的核心公式：
    P(tags, words) = ∏ P(tag_i | tag_{{i-1}}) · P(word_i | tag_i)
                      ╰──── 转移 A ────╯   ╰── 发射 B ──╯

  Viterbi 解码：动态规划，O(T · N²)，找全局最优标签路径。

  消融实验的完整图景：
    · 整体 token 准确率：发射 > 转移（屏蔽发射掉 {drop_mask_emit*100:.1f}pp vs 屏蔽转移掉 {drop_mask_trans*100:.1f}pp）
      → 因为大部分已知词无歧义，看词本身就够。
    · 未知词（OOV）准确率：转移是唯一机制
      → 完整模型 {ua*100:.1f}% vs 屏蔽转移后 {ua_e*100:.1f}%

  ★ 转移概率不是"锦上添花"，而是"OOV 保险"：
    你在已知词上看不到它的价值，但遇到从没见过的词时，它就是全部。

  → 想看 CRF / BiLSTM-CRF / BERT 如何接力？
    回到 17-序列标注-POS与NER.md 的方法演化时间线。
""")


if __name__ == "__main__":
    main()
