"""
NLP (Cotterell) — ETH Zürich
============================
覆盖主题：
- FST 形态学（有限状态转换器）
- WFST 解码
- 字符级语言模型
- Mini 神经 PCFG

核心教材/论文：
- Jurafsky & Martin "Speech and Language Processing" 3rd ed. Ch. 2 (Regex/FST), Ch. 11 (PCFG)
- Mohri "Weighted Automata Algorithms" Handbook of Weighted Automata (2009) — WFST
- Kim et al. "Character-Aware Neural Language Models" AAAI 2016 — char-level LM
- EMNLP/Cotterell group: morphological processing & neural grammar papers

本文件实现：
1. FST 形态分析（英语复数 + 动词第三人称）
2. WFST 最短路径解码
3. 字符级 n-gram 语言模型
4. Mini PCFG inside/outside 解析

运行：
    python nlp.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ============ 1. 有限状态转换器 (FST) ============

class FST:
    """
    有限状态转换器：((state_in), (state_out), input_sym, output_sym)
    upper: input tape (lexical), lower: output tape (surface)
    """

    def __init__(self):
        self.states: set[str] = set()
        self.transitions: list[tuple[str, str, str, str, float]] = []  # (from, to, in, out, weight)
        self.start: str = ""
        self.final: set[str] = set()

    def add_state(self, name: str, final: bool = False):
        self.states.add(name)
        if final:
            self.final.add(name)

    def add_transition(self, frm: str, to: str, in_sym: str, out_sym: str, weight: float = 0):
        self.transitions.append((frm, to, in_sym, out_sym, weight))

    def transduce(self, input_str: str) -> list[tuple[str, float]]:
        """对输入串做转换，返回所有可能输出（支持多字符符号如 +PL）"""
        results = []

        def _search(state: str, idx: int, output: str, weight: float):
            if idx == len(input_str):
                if state in self.final:
                    results.append((output, weight))
                return
            for frm, to, ins, outs, w in self.transitions:
                if frm != state:
                    continue
                if ins == "":
                    # epsilon transition（不消耗输入）
                    _search(to, idx, output + outs, weight + w)
                elif input_str[idx:idx + len(ins)] == ins:
                    # 匹配符号（可能是多字符如 "+PL"）
                    _search(to, idx + len(ins), output + outs, weight + w)

        _search(self.start, 0, "", 0.0)
        return results


def build_english_plural_fst() -> FST:
    """
    英语复数 FST:
    cat + PL → cats, bus + PL → buses, fly + PL → flies
    """
    f = FST()
    f.start = "q0"
    f.add_state("q0")
    f.add_state("q1", final=True)  # 普通 +s
    f.add_state("q2", final=True)  # +es (s/x/z/ch/sh)
    f.add_state("q3", final=True)  # y→ies
    f.add_state("q_err", final=True)

    # 通用字母 → q0（排除 s,x,z → q2, y → q3）
    for c in "abcdefghijklmnopqrtuvw":
        f.add_transition("q0", "q0", c, c, 0)
    # s/x/z → q2
    for c in "sxz":
        f.add_transition("q0", "q2", c, c, 0)
    # y → q3（删 y，+PL 时补 ies）
    f.add_transition("q0", "q3", "y", "", 0)

    # PL 规则
    f.add_transition("q0", "q1", "+PL", "s", 0)
    f.add_transition("q2", "q2", "+PL", "es", 0)
    f.add_transition("q3", "q1", "+PL", "ies", -0.1)  # y 删除后加 ies
    return f


# ============ 2. WFST 解码 ============

class WFSTDecoder:
    """
    WFST: 加权有限状态转换器
    用最短路径（Viterbi 风格）解码
    """

    def __init__(self):
        self.arcs: dict[str, list[tuple[str, str, float]]] = defaultdict(list)
        self.start = ""
        self.final: dict[str, float] = {}

    def add_arc(self, frm: str, to: str, label: str, weight: float):
        self.arcs[frm].append((to, label, weight))

    def add_final(self, state: str, weight: float = 0):
        self.final[state] = weight

    def best_path(self) -> list[str]:
        """Dijkstra 式最短路径"""
        dist = {self.start: 0.0}
        prev = {}
        visited = set()
        best_final = None
        best_final_dist = float('inf')
        import heapq
        pq = [(0, self.start)]
        while pq:
            d, state = heapq.heappop(pq)
            if state in visited:
                continue
            visited.add(state)
            if state in self.final:
                total = d + self.final[state]
                if total < best_final_dist:
                    best_final_dist = total
                    best_final = state
            for to, label, w in self.arcs[state]:
                nd = d + w
                if nd < dist.get(to, float('inf')):
                    dist[to] = nd
                    prev[to] = (state, label)
                    heapq.heappush(pq, (nd, to))
        # 回溯
        path = []
        if best_final:
            node = best_final
            while node != self.start and node in prev:
                p, label = prev[node]
                path.append(label)
                node = p
            path.reverse()
        return path


# ============ 3. 字符级 n-gram LM ============

class CharNgramLM:
    """字符级 n-gram 语言模型（加 K smoothing）"""

    def __init__(self, n: int = 3):
        self.n = n
        self.context_counts: dict[str, int] = defaultdict(int)
        self.ngram_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.vocab = set()

    def train(self, text: str):
        chars = list(text)
        self.vocab.update(chars)
        for i in range(len(chars) - self.n + 1):
            context = "".join(chars[i:i + self.n - 1])
            char = chars[i + self.n - 1]
            self.context_counts[context] += 1
            self.ngram_counts[context][char] += 1

    def prob(self, context: str, char: str, k: float = 0.1) -> float:
        total = self.context_counts.get(context, 0) + k * len(self.vocab)
        count = self.ngram_counts.get(context, {}).get(char, 0) + k
        return count / max(total, 1)

    def perplexity(self, text: str) -> float:
        chars = list(text)
        log_prob = 0
        n_eval = 0
        for i in range(len(chars)):
            context = "".join(chars[max(0, i - self.n + 1):i])
            if len(context) < self.n - 1:
                continue
            p = self.prob(context, chars[i])
            log_prob += math.log(max(p, 1e-10))
            n_eval += 1
        if n_eval == 0:
            return float('inf')
        return math.exp(-log_prob / n_eval)

    def generate(self, length: int = 50) -> str:
        context = " " * (self.n - 1)
        result = []
        for _ in range(length):
            probs = [(c, self.prob(context, c)) for c in self.vocab]
            r = random.random()
            cum = 0
            for c, p in sorted(probs, key=lambda x: -x[1]):
                cum += p
                if r <= cum:
                    result.append(c)
                    context = (context + c)[1:]
                    break
            else:
                c = max(probs, key=lambda x: x[1])[0]
                result.append(c)
                context = (context + c)[1:]
        return "".join(result)


# ============ 4. Mini PCFG ============

class PCFG:
    """概率上下文无关文法"""

    def __init__(self):
        self.rules: dict[str, list[tuple]] = defaultdict(list)  # LHS → [(RHS, prob)]

    def add_rule(self, lhs: str, rhs: tuple, prob: float):
        self.rules[lhs].append((rhs, prob))

    def inside(self, words: list[str]) -> float:
        """
        Inside 算法：计算句子的概率 P(S → words)
        CKY 风格
        """
        n = len(words)
        # table[i][j] = {NT: prob} 表示 words[i:j] 被 NT 推导的概率
        table = [[defaultdict(float) for _ in range(n + 1)] for _ in range(n + 1)]

        # 对角线：词法规则
        for i in range(n):
            for lhs, rules in self.rules.items():
                for rhs, p in rules:
                    if len(rhs) == 1 and rhs[0] == words[i]:
                        table[i][i + 1][lhs] += p

        # CKY 填表
        for span in range(2, n + 1):
            for i in range(n - span + 1):
                j = i + span
                for k in range(i + 1, j):
                    for lhs, rules in self.rules.items():
                        for rhs, p in rules:
                            if len(rhs) == 2:
                                left, right = rhs
                                if left in table[i][k] and right in table[k][j]:
                                    table[i][j][lhs] += p * table[i][k][left] * table[k][j][right]

        return table[0][n].get("S", 0.0)


# ============ Demo ============

def demo():
    print("=" * 60)
    print("NLP (Cotterell): FST + WFST + CharLM + PCFG")
    print("=" * 60)
    random.seed(42)

    # 1. FST 形态学
    print("\n📋 1. FST 英语复数形态学")
    fst = build_english_plural_fst()
    for word in ["cat+PL", "bus+PL", "fly+PL", "dog+PL"]:
        outputs = fst.transduce(word)
        print(f"   {word:12s} → {outputs}")

    # 2. WFST 解码
    print("\n📋 2. WFST 最短路径解码")
    w = WFSTDecoder()
    w.start = "s0"
    w.add_arc("s0", "s1", "the", -2)
    w.add_arc("s0", "s1", "a", -1)
    w.add_arc("s1", "s2", "cat", -3)
    w.add_arc("s1", "s2", "dog", -2)
    w.add_arc("s2", "s3", "ran", -1)
    w.add_final("s3", 0)
    path = w.best_path()
    print(f"   最佳路径: {' '.join(path)}")

    # 3. 字符级 LM
    print("\n📋 3. 字符级 trigram LM")
    corpus = (
        "the cat sat on the mat "
        "the dog ran in the park "
        "the cat and the dog played "
    ) * 20
    lm = CharNgramLM(n=3)
    lm.train(corpus)
    ppl_in_dist = lm.perplexity("the cat sat")
    ppl_oov = lm.perplexity("zzz qxx")
    print(f"   训练语料: {len(corpus)} 字符")
    print(f"   perplexity('the cat sat') = {ppl_in_dist:.2f} (分布内)")
    print(f"   perplexity('zzz qxx') = {ppl_oov:.2f} (分布外，更高)")

    # 4. Mini PCFG
    print("\n📋 4. Mini PCFG (Inside 算法)")
    pcfg = PCFG()
    pcfg.add_rule("S", ("NP", "VP"), 1.0)
    pcfg.add_rule("NP", ("Det", "N"), 0.7)
    pcfg.add_rule("NP", ("N",), 0.3)
    pcfg.add_rule("VP", ("V", "NP"), 0.6)
    pcfg.add_rule("VP", ("V",), 0.4)
    pcfg.add_rule("Det", ("the",), 1.0)
    pcfg.add_rule("N", ("cat",), 0.4)
    pcfg.add_rule("N", ("dog",), 0.4)
    pcfg.add_rule("N", ("mat",), 0.2)
    pcfg.add_rule("V", ("saw",), 0.5)
    pcfg.add_rule("V", ("chased",), 0.5)

    for sentence in [["the", "cat", "saw", "the", "dog"],
                     ["the", "dog", "chased", "the", "cat"]]:
        p = pcfg.inside(sentence)
        print(f"   P({' '.join(sentence)}) = {p:.6f}")

    # 反直觉
    print("\n💡 反直觉发现：字符级 LM 比词级更通用")
    print(f"   字符级 vocab 更小（~100 vs ~100K）")
    print(f"   天然处理 OOV / 拼写错误 / 形态变体")
    print(f"   代价：序列更长（×5），但能学到形态规律")
    print(f"   → fastText / subword BPE 的灵感来源")

    print("\n✅ NLP 完成！")


if __name__ == "__main__":
    demo()
