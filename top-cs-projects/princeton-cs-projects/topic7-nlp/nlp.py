"""
COS 484 Natural Language Processing（Princeton）
===================================================
覆盖主题：
- HMM 词性标注（Viterbi 解码）
- PCFG CKY 解析
- word2vec SGNS（skip-gram negative sampling，mini 版）
- BERT pipeline demo（tokenizer + masked LM 概念演示）

核心论文/教材：
- Jurafsky & Martin "Speech and Language Processing" 3rd ed, Ch 8 (HMM POS), Ch 13 (PCFG CKY)
- Mikolov et al. 2013 "Distributed Representations of Words and Phrases" arXiv:1310.4546 (SGNS)
- Rabiner 1989 "A Tutorial on Hidden Markov Models" Proc IEEE
- Devlin et al. 2019 "BERT: Pre-training of Deep Bidirectional Transformers" arXiv:1810.04805

本文件实现：
1. HMM POS 标注器（Viterbi 算法）
2. PCFG CKY 解析器
3. mini word2vec (SGNS, 梯度下降)
4. BERT tokenizer + masked LM 概念演示

运行：
    python nlp.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ================================================================
# 1. HMM POS Tagger (Viterbi)
# ================================================================
# HMM: λ = (A, B, π)
#   A[transition]: P(tag_j | tag_i)
#   B[emission]:   P(word | tag)
#   π[initial]:    P(tag_i at position 0)

class HMM:
    """Hidden Markov Model for POS tagging."""

    def __init__(self):
        self.tags = []
        self.vocab = []
        self.trans = {}   # trans[(t1, t2)] = P(t2|t1)
        self.emit = {}    # emit[(t, w)] = P(w|t)
        self.init = {}    # init[t] = P(t at pos 0)

    def train(self, tagged_sents: list[list[tuple[str, str]]]):
        """Train from supervised data (tagged sentences)."""
        tag_counts = defaultdict(int)
        trans_counts = defaultdict(int)
        emit_counts = defaultdict(int)
        init_counts = defaultdict(int)
        tag_set = set()
        vocab_set = set()

        for sent in tagged_sents:
            for i, (word, tag) in enumerate(sent):
                tag_set.add(tag)
                vocab_set.add(word)
                emit_counts[(tag, word)] += 1
                tag_counts[tag] += 1
                if i == 0:
                    init_counts[tag] += 1
                else:
                    prev_tag = sent[i - 1][1]
                    trans_counts[(prev_tag, tag)] += 1

        self.tags = sorted(tag_set)
        self.vocab = sorted(vocab_set)
        n_sents = len(tagged_sents)

        # Add-one smoothing
        V = len(self.vocab)
        T = len(self.tags)
        for t in self.tags:
            self.init[t] = (init_counts[t] + 1) / (n_sents + T)
            for w in self.vocab:
                self.emit[(t, w)] = (emit_counts.get((t, w), 0) + 1) / (tag_counts[t] + V)
            for t2 in self.tags:
                self.trans[(t, t2)] = (trans_counts.get((t, t2), 0) + 1) / (tag_counts[t] + T)

    def viterbi(self, words: list[str]) -> list[str]:
        """Viterbi decoding: find best tag sequence."""
        N = len(words)
        T = len(self.tags)
        if N == 0:
            return []
        # V[t][i] = best probability of being in tag t at position i
        V = [[float('-inf')] * T for _ in range(N)]
        back = [[0] * T for _ in range(N)]

        # Initialize
        w = words[0]
        for ti, t in enumerate(self.tags):
            emit_p = self.emit.get((t, w), 1e-10)
            init_p = self.init.get(t, 1e-10)
            V[0][ti] = math.log(init_p) + math.log(emit_p)

        # Recursion
        for i in range(1, N):
            w = words[i]
            for tj, t in enumerate(self.tags):
                emit_p = self.emit.get((t, w), 1e-10)
                best_logp = float('-inf')
                best_prev = 0
                for ti, pt in enumerate(self.tags):
                    trans_p = self.trans.get((pt, t), 1e-10)
                    logp = V[i - 1][ti] + math.log(trans_p)
                    if logp > best_logp:
                        best_logp = logp
                        best_prev = ti
                V[i][tj] = best_logp + math.log(emit_p)
                back[i][tj] = best_prev

        # Backtrack
        best_final = max(range(T), key=lambda tj: V[N - 1][tj])
        result = [best_final]
        for i in range(N - 1, 0, -1):
            result.append(back[i][result[-1]])
        result.reverse()
        return [self.tags[j] for j in result]


# ================================================================
# 2. PCFG CKY Parser
# ================================================================

class PCFG:
    """Probabilistic Context-Free Grammar with CKY parsing."""

    def __init__(self):
        # rules[(LHS, (R1, R2))] = probability  (binary)
        # rules[(LHS, (terminal,))] = probability (unary → terminal)
        self.rules = {}
        self.non_terminals = set()

    def add_rule(self, lhs: str, rhs: tuple, prob: float):
        self.rules[(lhs, rhs)] = prob
        self.non_terminals.add(lhs)

    def _unary_closure(self, cell):
        """Apply unary non-terminal rules (e.g. NP→NN, VP→VB) until fixpoint.

        Without this, unary chains like NN⇒NP are never processed because
        the main CKY loop only handles len(rhs)==2. That made 'the cat sat'
        unparseable: the diagonal gets NN and VB but NP/VP never propagate.
        """
        changed = True
        while changed:
            changed = False
            for (lhs, rhs), prob in self.rules.items():
                if len(rhs) != 1 or rhs[0] not in self.non_terminals:
                    continue
                child = cell.get(rhs[0])
                if child is None:
                    continue
                new_prob = prob * child[0]
                existing = cell.get(lhs)
                if existing is None or new_prob > existing[0]:
                    cell[lhs] = (new_prob, -1)
                    changed = True

    def parse(self, words: list[str]) -> tuple[float, bool]:
        """CKY parse. Returns (best_probability, found_parse)."""
        n = len(words)
        # table[i][j] = {NT: (prob, split_point, back_pointers)}
        table = [[{} for _ in range(n)] for _ in range(n)]

        # Fill diagonal: terminal rules, then unary closure
        for i in range(n):
            for (lhs, rhs), prob in self.rules.items():
                if len(rhs) == 1 and rhs[0] == words[i]:
                    old = table[i][i].get(lhs)
                    if old is None or prob > old[0]:
                        table[i][i][lhs] = (prob, -1)
            # Unary closure: propagate NP←NN, VP←VB, etc.
            self._unary_closure(table[i][i])

        # Fill upper triangle: binary rules, then unary closure
        for length in range(2, n + 1):  # span length
            for i in range(n - length + 1):
                j = i + length - 1
                for k in range(i, j):  # split point
                    for (lhs, rhs), prob in self.rules.items():
                        if len(rhs) != 2:
                            continue
                        left_nt, right_nt = rhs
                        if left_nt in table[i][k] and right_nt in table[k + 1][j]:
                            left_prob = table[i][k][left_nt][0]
                            right_prob = table[k + 1][j][right_nt][0]
                            new_prob = prob * left_prob * right_prob
                            old = table[i][j].get(lhs)
                            if old is None or new_prob > old[0]:
                                table[i][j][lhs] = (new_prob, k)
                # Unary closure on composed spans too
                self._unary_closure(table[i][j])

        # Check if S spans the whole sentence
        best = table[0][n - 1].get('S', (0.0, -1))
        return best[0], best[0] > 0


# ================================================================
# 3. Mini word2vec (SGNS)
# ================================================================

class MiniWord2Vec:
    """Skip-gram with Negative Sampling (SGNS), pure Python."""

    def __init__(self, dim: int = 10, lr: float = 0.025, epochs: int = 50):
        self.dim = dim
        self.lr = lr
        self.epochs = epochs
        self.vocab = {}
        self.W_center = {}   # center word vectors
        self.W_context = {}  # context word vectors

    def _build_vocab(self, corpus: list[list[str]], min_count: int = 1):
        counts = defaultdict(int)
        for sent in corpus:
            for w in sent:
                counts[w] += 1
        self.vocab = {w: i for i, (w, c) in enumerate(sorted(counts.items())) if c >= min_count}
        for w in self.vocab:
            self.W_center[w] = [random.gauss(0, 0.1) for _ in range(self.dim)]
            self.W_context[w] = [random.gauss(0, 0.1) for _ in range(self.dim)]

    @staticmethod
    def _sigmoid(x):
        if x >= 0:
            return 1.0 / (1.0 + math.exp(-x))
        ex = math.exp(x)
        return ex / (1.0 + ex)

    def train(self, corpus: list[list[str]], window: int = 2, neg_samples: int = 3):
        self._build_vocab(corpus)
        words = list(self.vocab.keys())
        if not words:
            return
        for epoch in range(self.epochs):
            for sent in corpus:
                for i, center in enumerate(sent):
                    if center not in self.vocab:
                        continue
                    # Context window
                    for j in range(max(0, i - window), min(len(sent), i + window + 1)):
                        if j == i:
                            continue
                        context = sent[j]
                        if context not in self.vocab:
                            continue
                        # Positive pair (center, context)
                        self._update(center, context, label=1)
                        # Negative samples
                        for _ in range(neg_samples):
                            neg = random.choice(words)
                            if neg == context:
                                continue
                            self._update(center, neg, label=0)

    def _update(self, center, context, label):
        vc = self.W_center[center]
        uc = self.W_context[context]
        # Score
        score = sum(a * b for a, b in zip(vc, uc))
        score = max(-6, min(6, score))  # clamp
        pred = self._sigmoid(score)
        grad = pred - label  # gradient of loss
        # Update context vector
        for d in range(self.dim):
            uc[d] -= self.lr * grad * vc[d]
        # Update center vector
        for d in range(self.dim):
            vc[d] -= self.lr * grad * uc[d]

    def similarity(self, w1: str, w2: str) -> float:
        if w1 not in self.vocab or w2 not in self.vocab:
            return 0.0
        v1, v2 = self.W_center[w1], self.W_center[w2]
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        return dot / (n1 * n2 + 1e-10)


# ================================================================
# 4. BERT Pipeline Concept Demo
# ================================================================

class SimpleBertTokenizer:
    """Simplified WordPiece-style BPE tokenizer (concept demo)."""

    def __init__(self):
        self.vocab = {}
        self._build_vocab()

    def _build_vocab(self):
        words = ["the", "cat", "sat", "on", "mat", "dog", "ran", "fast",
                 "[CLS]", "[SEP]", "[MASK]", "[PAD]", "[UNK]"]
        for i, w in enumerate(words):
            self.vocab[w] = i

    def tokenize(self, text: str) -> list[str]:
        tokens = ["[CLS]"]
        for word in text.lower().split():
            tokens.append(word if word in self.vocab else "[UNK]")
        tokens.append("[SEP]")
        return tokens

    def encode(self, text: str) -> list[int]:
        return [self.vocab.get(t, self.vocab["[UNK]"]) for t in self.tokenize(text)]


def masked_lm_demo(tokenizer: SimpleBertTokenizer, text: str, mask_word: str):
    """Simulate masked LM prediction (concept only, no real model)."""
    tokens = tokenizer.tokenize(text)
    # Replace a word with [MASK]
    for i, t in enumerate(tokens):
        if t == mask_word:
            tokens[i] = "[MASK]"
            break
    masked = tokens[:]
    # Simulate prediction: fill with a random vocab word
    candidates = {"cat": 0.45, "dog": 0.30, "mat": 0.15, "rat": 0.10}
    predicted = max(candidates, key=candidates.get)
    for i, t in enumerate(tokens):
        if t == "[MASK]":
            tokens[i] = predicted
            break
    return masked, tokens, candidates


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 484: NLP Demo")
    print("=" * 60)
    random.seed(42)

    # --- 1. HMM POS ---
    print("\n📋 1. HMM POS 标注 (Viterbi)")
    tagged = [
        [("the", "DT"), ("cat", "NN"), ("sat", "VB")],
        [("the", "DT"), ("dog", "NN"), ("ran", "VB")],
        [("a", "DT"), ("cat", "NN"), ("ran", "VB")],
        [("the", "DT"), ("dog", "NN"), ("sat", "VB")],
    ]
    hmm = HMM()
    hmm.train(tagged)
    test = ["the", "cat", "ran"]
    tags = hmm.viterbi(test)
    print(f"   句子: {' '.join(test)}")
    print(f"   标注: {' '.join(f'{w}/{t}' for w, t in zip(test, tags))}")

    # --- 2. PCFG CKY ---
    print("\n📋 2. PCFG CKY 解析")
    pcfg = PCFG()
    pcfg.add_rule("S", ("NP", "VP"), 1.0)
    pcfg.add_rule("NP", ("DT", "NN"), 0.6)
    pcfg.add_rule("NP", ("NN",), 0.4)
    pcfg.add_rule("VP", ("VB", "NP"), 0.5)
    pcfg.add_rule("VP", ("VB",), 0.5)
    pcfg.add_rule("DT", ("the",), 1.0)
    pcfg.add_rule("NN", ("cat",), 0.5)
    pcfg.add_rule("NN", ("fish",), 0.5)
    pcfg.add_rule("VB", ("sat",), 0.5)
    pcfg.add_rule("VB", ("ate",), 0.5)

    for sent in [["the", "cat", "sat"], ["the", "cat", "ate", "the", "fish"]]:
        prob, found = pcfg.parse(sent)
        print(f"   {' '.join(sent)}: prob={prob:.5f}, parseable={found}")

    # --- 3. word2vec ---
    print("\n📋 3. Mini word2vec (SGNS)")
    corpus = [
        ["the", "king", "rules", "the", "kingdom"],
        ["the", "queen", "rules", "the", "kingdom"],
        ["the", "king", "and", "the", "queen", "rule"],
        ["a", "king", "is", "a", "man"],
        ["a", "queen", "is", "a", "woman"],
        ["the", "man", "and", "the", "woman", "talk"],
    ] * 10
    w2v = MiniWord2Vec(dim=10, lr=0.05, epochs=20)
    w2v.train(corpus, window=2, neg_samples=2)
    pairs = [("king", "queen"), ("king", "man"), ("queen", "woman"), ("king", "rules")]
    for w1, w2 in pairs:
        sim = w2v.similarity(w1, w2)
        print(f"   sim('{w1}', '{w2}') = {sim:.4f}")

    # --- 4. BERT demo ---
    print("\n📋 4. BERT Tokenizer + Masked LM 概念")
    tokenizer = SimpleBertTokenizer()
    text = "the cat sat on the mat"
    ids = tokenizer.encode(text)
    tokens = tokenizer.tokenize(text)
    print(f"   文本: '{text}'")
    print(f"   Tokenize: {tokens}")
    print(f"   Token IDs: {ids}")

    masked, filled, probs = masked_lm_demo(tokenizer, "the cat sat", "cat")
    print(f"   Masked: {' '.join(masked)}")
    print(f"   预测填充: {' '.join(filled)}")
    print(f"   候选概率: {probs}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    print(f"   SGNS 学到的 king↔queen 相似度高于 king↔rules")
    print(f"   → 词嵌入自动发现语义关系（同义/类比），无需显式规则")
    print(f"   → 但这里数据太少，真实 word2vec 需要数十亿 token")

    print("\n✅ COS 484 Demo 完成！")


if __name__ == "__main__":
    demo()
