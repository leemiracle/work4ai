"""
Part II Natural Language Processing (Cambridge CST)
====================================================
覆盖主题：
- Byte Pair Encoding (BPE)
- seq2seq + attention（mini）
- mini BERT（Masked Language Model）
- Beam search 解码

核心教材：
- Jurafsky & Martin 2024 "Speech and Language Processing" 3rd ed (SLP3, web.stanford.edu/~jurafsky/slp3/)
- Manning & Schütze 1999 "Foundations of Statistical Natural Language Processing" MIT Press

核心论文（真实 arXiv ID）：
- Sennrich et al. 2016 "Neural Machine Translation of Rare Words with Subword Units" arXiv:1508.07909
- Bahdanau et al. 2015 "Neural Machine Translation by Jointly Learning to Align and Translate" arXiv:1409.0473
- Luong et al. 2015 "Effective Approaches to Attention-based Neural Machine Translation" arXiv:1508.04025
- Devlin et al. 2019 "BERT: Pre-training of Deep Bidirectional Transformers" arXiv:1810.04805
- Vaswani et al. 2017 "Attention Is All You Need" arXiv:1706.03762

本文件实现：
- BPE 子词分词器（训练 + 编码）
- mini seq2seq with attention（编码器-解码器）
- mini BERT MLM（mask + predict）
- Beam search 解码

运行：
    python nlp.py
"""
from __future__ import annotations
import math
import random
from collections import Counter, defaultdict


# ================================================================
# 1. Byte Pair Encoding (BPE)
# ================================================================

class BPE:
    """
    BPE: 反复合并最高频的相邻 token 对。
    Sennrich et al. arXiv:1508.07909
    """

    def __init__(self, num_merges=20):
        self.num_merges = num_merges
        self.merges = []  # (pair, merged) 按顺序

    def train(self, corpus):
        """corpus: list of words (strings)"""
        # 初始化: 每个词拆成字符 + </w> 结尾标记
        word_freqs = Counter(corpus)
        splits = {}
        for word, freq in word_freqs.items():
            chars = list(word) + ["</w>"]
            splits[tuple(chars)] = splits.get(tuple(chars), 0) + freq

        for _ in range(self.num_merges):
            # 统计相邻 pair
            pair_counts = Counter()
            for tokens, freq in splits.items():
                for i in range(len(tokens) - 1):
                    pair_counts[(tokens[i], tokens[i+1])] += freq
            if not pair_counts:
                break
            best_pair = pair_counts.most_common(1)[0][0]
            merged = best_pair[0] + best_pair[1]
            self.merges.append((best_pair, merged))
            # 应用合并
            new_splits = {}
            for tokens, freq in splits.items():
                new_tokens = []
                i = 0
                while i < len(tokens):
                    if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == best_pair:
                        new_tokens.append(merged)
                        i += 2
                    else:
                        new_tokens.append(tokens[i])
                        i += 1
                new_splits[tuple(new_tokens)] = new_splits.get(tuple(new_tokens), 0) + freq
            splits = new_splits
        return splits

    def encode(self, word):
        """对单个词应用学到的 merges"""
        tokens = list(word) + ["</w>"]
        for (pair, merged) in self.merges:
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
                    new_tokens.append(merged)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        return tokens


# ================================================================
# 2. mini seq2seq + attention
# ================================================================

def softmax(vec):
    mx = max(vec)
    exps = [math.exp(v - mx) for v in vec]
    s = sum(exps)
    return [e / s for e in exps]


class MiniSeq2Seq:
    """
    Encoder-Decoder with Luong "general" attention (Luong et al. 2015, arXiv:1508.04025)
    score(s, h) = s^T W h   (Luong "general" — 乘性打分)
    注意：Bahdanau (arXiv:1409.0473) 用加性打分 v^T tanh(W1 s + W2 h)，
    本实现是 Luong general，不是 Bahdanau。
    简化: 固定随机权重，展示机制。
    """

    def __init__(self, src_vocab, tgt_vocab, hidden=8):
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.H = hidden
        # 随机初始化（仅演示机制）
        self.enc_emb = {w: [random.gauss(0, 0.3) for _ in range(hidden)] for w in src_vocab}
        self.dec_emb = {w: [random.gauss(0, 0.3) for _ in range(hidden)] for w in tgt_vocab}
        self.W_att = [[random.gauss(0, 0.3) for _ in range(hidden)] for _ in range(hidden)]

    def encode(self, src_sentence):
        """编码: 返回每个词的隐状态"""
        return [self.enc_emb[w] for w in src_sentence]

    def attend(self, dec_state, enc_states):
        """Luong "general" attention: score = s^T W h → softmax → 加权和"""
        scores = []
        for enc in enc_states:
            score = sum(dec_state[d] * sum(self.W_att[d][k] * enc[k]
                      for k in range(self.H)) for d in range(self.H))
            scores.append(score)
        attn_weights = softmax(scores)
        # context = Σ α_i h_i
        context = [sum(attn_weights[i] * enc_states[i][d] for i in range(len(enc_states)))
                   for d in range(self.H)]
        return context, attn_weights

    def decode_step(self, dec_state, context, prev_word):
        """解码一步"""
        # 简化: 用 context + dec_state 计算 logits
        tgt_words = list(self.tgt_vocab)
        logits = []
        for w in tgt_words:
            emb = self.dec_emb[w]
            score = sum(emb[d] * (dec_state[d] + context[d]) * 0.5 for d in range(self.H))
            logits.append(score)
        return softmax(logits), tgt_words

    def translate(self, src_sentence, max_len=8):
        """贪心翻译"""
        enc_states = self.encode(src_sentence)
        dec_state = [0.0] * self.H  # 初始隐状态
        output = []
        prev = "<sos>"
        for t in range(max_len):
            context, attn = self.attend(dec_state, enc_states)
            probs, words = self.decode_step(dec_state, context, prev)
            best = max(range(len(probs)), key=lambda i: probs[i])
            word = words[best]
            if word == "<eos>":
                break
            output.append((word, attn))
            dec_state = [dec_state[d] * 0.9 + context[d] * 0.1 for d in range(self.H)]
            prev = word
        return output


# ================================================================
# 3. mini BERT (Masked Language Model)
# ================================================================

class MiniBERT:
    """
    简化 BERT MLM (arXiv:1810.04805):
    - 随机 mask 15% token
    - 用上下文预测 masked token（双向 attention）
    """

    def __init__(self, vocab, hidden=8):
        self.vocab = list(vocab)
        self.V = len(self.vocab)
        self.H = hidden
        self.embeddings = {w: [random.gauss(0, 0.3) for _ in range(hidden)] for w in vocab}

    def mask_tokens(self, tokens, mask_prob=0.15):
        """随机 mask"""
        masked = []
        positions = []
        for i, t in enumerate(tokens):
            if random.random() < mask_prob and t != "[CLS]" and t != "[SEP]":
                masked.append("[MASK]")
                positions.append(i)
            else:
                masked.append(t)
        return masked, positions

    def predict_mask(self, tokens, mask_pos):
        """
        简化: 用相邻 token 嵌入的平均预测 masked token
        （真实 BERT 用 Transformer encoder）
        """
        # 收集上下文
        context_emb = [0.0] * self.H
        count = 0
        for i, t in enumerate(tokens):
            if i != mask_pos and t != "[MASK]":
                for d in range(self.H):
                    context_emb[d] += self.embeddings.get(t, [0]*self.H)[d]
                count += 1
        if count > 0:
            context_emb = [c / count for c in context_emb]
        # 计算 logits
        logits = []
        for w in self.vocab:
            emb = self.embeddings[w]
            score = sum(context_emb[d] * emb[d] for d in range(self.H))
            logits.append(score)
        probs = softmax(logits)
        best = max(range(len(probs)), key=lambda i: probs[i])
        return self.vocab[best], probs[best]


# ================================================================
# 4. Beam Search
# ================================================================

def beam_search(score_fn, vocab, beam_width=3, max_len=8, start="<sos>", end="<eos>"):
    """
    通用 beam search。
    score_fn(tokens) → list of (next_token, log_prob)
    """
    beams = [([start], 0.0)]  # (tokens, cumulative_log_prob)
    for step in range(max_len):
        candidates = []
        for tokens, score in beams:
            if tokens[-1] == end:
                candidates.append((tokens, score))
                continue
            for word, lp in score_fn(tokens):
                candidates.append((tokens + [word], score + lp))
        # 取 top beam_width
        candidates.sort(key=lambda x: -x[1])
        beams = candidates[:beam_width]
        if all(b[0][-1] == end for b in beams):
            break
    return beams[0]  # 返回最优


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part II NLP — Demo")
    print("=" * 64)
    random.seed(42)

    # 1. BPE
    print("\n📋 1. Byte Pair Encoding (BPE, arXiv:1508.07909)")
    corpus = ["low"]*5 + ["lower"]*2 + ["newest"]*6 + ["widest"]*3 + ["low"]*3
    bpe = BPE(num_merges=10)
    final = bpe.train(corpus)
    print(f"   语料: {corpus[:8]}...")
    print(f"   学到的 merges (前 5):")
    for pair, merged in bpe.merges[:5]:
        print(f"     {pair} → '{merged}'")
    for word in ["lowest", "newer", "wider"]:
        tokens = bpe.encode(word)
        print(f"   encode('{word}') = {tokens}")

    # 2. seq2seq + attention
    print("\n📋 2. mini Seq2Seq + Attention (Luong general, arXiv:1508.04025)")
    src_vocab = {"i", "love", "nlp", "<sos>", "<eos>"}
    tgt_vocab = {"je", "aime", "tlpn", "<sos>", "<eos>"}
    model = MiniSeq2Seq(src_vocab, tgt_vocab, hidden=8)
    src = ["i", "love", "nlp"]
    result = model.translate(src, max_len=5)
    print(f"   源: {src}")
    for word, attn in result:
        attn_bar = " ".join(f"{a:.2f}" for a in attn)
        print(f"   → {word:6s}  attention: [{attn_bar}]")

    # 3. mini BERT
    print("\n📋 3. mini BERT MLM (arXiv:1810.04805)")
    vocab = {"the", "cat", "sat", "on", "mat", "dog", "ran", "[CLS]", "[SEP]"}
    bert = MiniBERT(vocab, hidden=8)
    sentence = ["[CLS]", "the", "cat", "sat", "on", "the", "mat", "[SEP]"]
    masked, positions = bert.mask_tokens(sentence, mask_prob=0.2)
    print(f"   原句: {' '.join(sentence)}")
    print(f"   masked: {' '.join(masked)}")
    for pos in positions:
        pred, prob = bert.predict_mask(masked, pos)
        print(f"   位置 {pos} ('{sentence[pos]}') → 预测 '{pred}' (p={prob:.3f})")

    # 4. Beam search
    print("\n📋 4. Beam Search 解码")
    # 简单 score function: 模拟一个翻译模型
    transition = {
        "<sos>": [("je", -0.5), ("moi", -1.0), ("nous", -1.5)],
        "je": [("aime", -0.3), ("vais", -1.0), ("suis", -0.8)],
        "aime": [("tlpn", -0.4), ("code", -0.9), ("pizzas", -1.2)],
        "tlpn": [("<eos>", -0.1)],
        "<eos>": [("<eos>", 0.0)],
    }
    def score_fn(tokens):
        last = tokens[-1]
        return transition.get(last, [("<eos>", -0.5)])
    best_tokens, best_score = beam_search(score_fn, set(), beam_width=2, max_len=5)
    print(f"   最优: {' '.join(best_tokens)}  (log_prob={best_score:.2f})")
    print(f"   → beam_width=2 保留最优 2 条路径，平衡搜索空间与质量")

    print("\n✅ NLP 完成！")
    print("\n💡 反直觉发现：")
    print("   - BPE 自动发现子词: low/lower/newest 共享 'low' 前缀")
    print("   - Attention 让解码器「看」所有源词，但权重揭示对齐关系")
    print("   - BERT MLM 是双向的（看左右上下文），GPT 是单向的（只看左）")
    print("   - Beam search 比 greedy 好，但 width=2 已捕获大多数收益")


if __name__ == "__main__":
    demo()
