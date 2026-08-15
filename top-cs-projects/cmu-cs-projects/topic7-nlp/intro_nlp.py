"""
11-411/611 Natural Language Processing (CMU)
================================================
覆盖主题（对应 lecture）：
- Sequence labeling: HMM POS tagger (Viterbi decoding)
- Parsing: CKY algorithm for CNF PCFG
- Word alignment: IBM Model 1 (EM training)

核心教材/论文：
- "Jurafsky & Martin SLP3" Ch 8 (HMM POS tagging), Ch 13 (PCFG/CKY), Ch 25 (MT/IBM Model 1)
- "Brown et al 1993 Computational Linguistics" — IBM Model 1-5
- "Rabiner 1989 IEEE Proc" — HMM (Viterbi)
- "Klein & Manning 2003 ACL" — accurate unlexicalized PCFG parsing

本文件实现：
- Bigram HMM POS tagger (Viterbi)
- CKY parser for CNF PCFG (probabilistic)
- IBM Model 1 word alignment (EM)

运行：
    python3 intro_nlp.py
"""
from __future__ import annotations
import math
from collections import defaultdict

# ============ 1. HMM POS Tagger (Viterbi) ============

class HMMTagger:
    """Bigram HMM POS tagger with Viterbi decoding."""

    def __init__(self):
        self.tags = []
        self.transition = defaultdict(lambda: defaultdict(float))  # tag_i-1 → tag_i
        self.emission = defaultdict(lambda: defaultdict(float))    # tag → word
        self.tag_counts = defaultdict(int)

    def train(self, tagged_sentences):
        """tagged_sentences: list of [(word, tag), ...]"""
        for sent in tagged_sentences:
            prev_tag = '<s>'
            for word, tag in sent:
                self.transition[prev_tag][tag] += 1
                self.emission[tag][word] += 1
                self.tag_counts[tag] += 1
                prev_tag = tag
            self.transition[prev_tag]['</s>'] += 1
        # normalize
        self._normalize(self.transition)
        self._normalize(self.emission)
        self.tags = sorted(self.tag_counts.keys())

    def _normalize(self, counts):
        for key in counts:
            total = sum(counts[key].values())
            for sub in counts[key]:
                counts[key][sub] /= total

    def viterbi(self, words):
        """Viterbi decode word sequence → (best tag sequence, joint prob).

        Returns the most probable tag sequence and its joint probability
        P*(T, W) = P(<s>) · ∏ P(t_i | t_{i-1}) P(w_i | t_i) · P(</s> | t_T).
        """
        T = len(words)
        V = [{} for _ in range(T)]  # V[t][tag] = best prob
        bp = [{} for _ in range(T)]

        # init
        for tag in self.tags:
            emit = self.emission[tag].get(words[0], 1e-6)
            V[0][tag] = self.transition['<s>'].get(tag, 1e-6) * emit

        # recurse
        for t in range(1, T):
            for tag in self.tags:
                emit = self.emission[tag].get(words[t], 1e-6)
                best_prev, best_prob = None, 0
                for prev_tag in self.tags:
                    prob = V[t-1][prev_tag] * self.transition[prev_tag].get(tag, 1e-6)
                    if prob > best_prob:
                        best_prob, best_prev = prob, prev_tag
                V[t][tag] = best_prob * emit
                bp[t][tag] = best_prev

        # backtrack — include </s> transition for the true joint probability
        best_final = max(self.tags,
                         key=lambda t: V[T-1][t] * self.transition[t].get('</s>', 1e-6))
        joint_prob = V[T-1][best_final] * self.transition[best_final].get('</s>', 1e-6)
        tags = [best_final]
        for t in range(T-1, 0, -1):
            tags.append(bp[t][tags[-1]])
        tags.reverse()
        return tags, joint_prob


# ============ 2. CKY Parser for CNF PCFG ============

def cky_parse(words, grammar_probs):
    """
    CKY parse with probabilistic CNF grammar (including unary closure).

    grammar_probs: dict (LHS, RHS_tuple) → prob
    Returns the CKY table; table[i][j][sym] = (prob, split, rhs_or_child)
      - lexical:  (prob, None,   None)
      - unary:    (prob, 'unary', child_symbol)
      - binary:   (prob, k,      (left_sym, right_sym))
    """
    n = len(words)
    table = [[dict() for _ in range(n + 1)] for _ in range(n + 1)]

    lexical = defaultdict(list)    # terminal word → [(LHS, prob)]
    unary_nt = defaultdict(list)   # child NT → [(parent, prob)]
    binary = defaultdict(list)     # (B, C) → [(A, prob)]

    for (lhs, rhs), prob in grammar_probs.items():
        if len(rhs) == 1 and isinstance(rhs[0], str) and rhs[0][0].islower():
            lexical[rhs[0]].append((lhs, prob))
        elif len(rhs) == 1:
            unary_nt[rhs[0]].append((lhs, prob))      # A → B (NT unary)
        elif len(rhs) == 2:
            binary[rhs].append((lhs, prob))

    def apply_unary(cell):
        """Unary closure: for every B in cell, if A→B exists, add A."""
        changed = True
        while changed:
            changed = False
            for child, parents in unary_nt.items():
                if child not in cell:
                    continue
                child_prob = cell[child][0]
                for parent, rule_prob in parents:
                    new_prob = rule_prob * child_prob
                    if parent not in cell or new_prob > cell[parent][0]:
                        cell[parent] = (new_prob, 'unary', child)
                        changed = True

    # ---- lexical diagonal + unary closure ----
    for i in range(n):
        for lhs, prob in lexical.get(words[i], []):
            if lhs not in table[i][i + 1] or prob > table[i][i + 1][lhs][0]:
                table[i][i + 1][lhs] = (prob, None, None)
        apply_unary(table[i][i + 1])

    # ---- upper triangle (binary) + unary closure ----
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            for k in range(i + 1, j):
                for (b_sym, c_sym), lhs_list in binary.items():
                    if b_sym in table[i][k] and c_sym in table[k][j]:
                        for lhs, rule_prob in lhs_list:
                            total = (rule_prob *
                                     table[i][k][b_sym][0] *
                                     table[k][j][c_sym][0])
                            if lhs not in table[i][j] or total > table[i][j][lhs][0]:
                                table[i][j][lhs] = (total, k, (b_sym, c_sym))
            apply_unary(table[i][j])

    return table

def extract_tree(table, words, i, j, symbol='S'):
    """Recursively extract parse tree from CKY table (handles unary rules)."""
    entry = table[i][j].get(symbol)
    if entry is None:
        return f"({symbol} ?)"
    _prob, split, rhs = entry
    if split == 'unary':
        child_tree = extract_tree(table, words, i, j, rhs)
        return f"({symbol} {child_tree})"
    if split is None:
        return f"({symbol} {words[i]})"
    left = extract_tree(table, words, i, split, rhs[0])
    right = extract_tree(table, words, split, j, rhs[1])
    return f"({symbol} {left} {right})"


# ============ 3. IBM Model 1 (Word Alignment EM) ============

def ibm_model1_em(sentence_pairs, n_iters=10):
    """
    IBM Model 1 EM for word translation probabilities.
    sentence_pairs: list of (foreign_words, english_words)
    Returns t(f|e) translation table.
    """
    # init uniform
    t = defaultdict(lambda: defaultdict(lambda: 0.1))

    for iteration in range(n_iters):
        count = defaultdict(lambda: defaultdict(float))
        total = defaultdict(float)
        for f_words, e_words in sentence_pairs:
            e_words = ['NULL'] + list(e_words)
            # compute normalization
            s_total = {}
            for f in f_words:
                s_total[f] = sum(t[e][f] for e in e_words)
            # E-step: collect fractional counts
            for f in f_words:
                for e in e_words:
                    delta = t[e][f] / max(s_total[f], 1e-10)
                    count[e][f] += delta
                    total[e] += delta
        # M-step
        for e in count:
            for f in count[e]:
                t[e][f] = count[e][f] / max(total[e], 1e-10)
    return t

def align(t_table, f_words, e_words):
    """Find best alignment for a sentence pair."""
    e_words = ['NULL'] + list(e_words)
    alignment = []
    for i, f in enumerate(f_words):
        best_j = max(range(len(e_words)), key=lambda j: t_table[e_words[j]][f])
        alignment.append(best_j)
    return alignment


# ============ Demo ============

def demo():
    print("=" * 60)
    print("11-411/611 NLP: HMM Tagger, CKY, IBM Model 1")
    print("=" * 60)

    # --- 1. HMM POS Tagger ---
    print("\n📋 1. HMM POS Tagger (Viterbi)")
    training = [
        [('the','DT'),('dog','NN'),('barks','VB')],
        [('a','DT'),('cat','NN'),('sleeps','VB')],
        [('the','DT'),('cat','NN'),('runs','VB')],
        [('my','DT'),('dog','NN'),('barks','VB')],
    ]
    tagger = HMMTagger()
    tagger.train(training)
    test = ['the', 'dog', 'runs']
    tags, joint_prob = tagger.viterbi(test)
    print(f"   Sentence: {test}")
    print(f"   Tags:     {tags}")
    print(f"   P(T|W) ∝ P*(T,W) = {joint_prob:.6f}   (Viterbi joint)")
    print(f"   log P*(T,W) = {math.log(joint_prob):.4f}")

    # --- 2. CKY ---
    print("\n📋 2. CKY Parser (CNF PCFG)")
    grammar = {
        ('S', ('NP','VP')): 0.9,
        ('S', ('VP','NP')): 0.1,
        ('NP', ('Det','N')): 0.5,
        ('NP', ('N',)): 0.3,  # unary handled by lexical
        ('VP', ('V','NP')): 0.6,
        ('VP', ('V',)): 0.4,
        # Lexical rules
        ('Det', ('the',)): 1.0,
        ('N', ('dog',)): 0.6,
        ('N', ('cat',)): 0.4,
        ('V', ('chases',)): 0.7,
        ('V', ('barks',)): 0.3,
    }
    words = ['the', 'dog', 'chases']
    table = cky_parse(words, grammar)
    s_entry = table[0][3].get('S')
    parseable = s_entry is not None
    print(f"   Sentence: {' '.join(words)}")
    print(f"   Parseable: {parseable}")
    if parseable:
        print(f"   P(parse) = {s_entry[0]:.4f}")
        print(f"   Tree: {extract_tree(table, words, 0, 3, 'S')}")
    print(f"   💡 CKY O(n³) — unary closure 处理 VP→V, NP→N 等一元规则")

    # --- 3. IBM Model 1 ---
    print("\n📋 3. IBM Model 1 — Word Alignment (EM)")
    pairs = [
        (['le','chien'],['the','dog']),
        (['le','chat'],['the','cat']),
        (['le','chien','noir'],['the','black','dog']),
        (['la','maison'],['the','house']),
        (['le','chat','noir'],['the','black','cat']),
    ]
    t = ibm_model1_em(pairs, n_iters=20)
    # Show learned alignments
    test_f, test_e = ['le','chien','noir'], ['the','black','dog']
    al = align(t, test_f, test_e)
    print(f"   Foreign: {test_f}")
    print(f"   English: ['NULL'] + {test_e}")
    print(f"   Alignment: {al}")
    print(f"   (0=NULL, 1=the, 2=black, 3=dog)")
    print(f"   t(le|the) = {t['the']['le']:.3f}, t(chien|dog) = {t['dog']['chien']:.3f}")
    print(f"   t(noir|black) = {t['black']['noir']:.3f}")
    print(f"   💡 IBM Model 1 无语法模型，纯词到词概率，但 EM 能自动对齐！")

    print("\n✅ 11-411/611 NLP 完成！")
    print("   覆盖：HMM POS Tagger (Viterbi) / CKY Parser / IBM Model 1 EM")


if __name__ == "__main__":
    demo()
