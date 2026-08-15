"""
CS 288 Natural Language Processing — UC Berkeley
================================================
覆盖主题：
- HMM 前向-后向算法 + Viterbi 解码（Lec 4-6）
- PCFG + CKY 解析（Lec 8-9）
- IBM Model 1 词对齐（Lec 11）
- Neural seq2seq + attention（Lec 14-16）

核心教材/参考：
- Jurafsky & Martin "Speech and Language Processing" 3rd ed (Draft 2024), Ch 8-13/17-18
- Rabiner "A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition" Proc IEEE 77(2) (1989)
- Brown et al. "The Mathematics of Statistical Machine Translation" Computational Linguistics 19(2) (1993), IBM Model 1
- Koehn "Statistical Machine Translation" (Cambridge 2010), Ch 4

本文件实现：
- HMM forward/backward + Viterbi（词性标注）
- PCFG + CKY parser
- IBM Model 1 EM 词对齐
- mini seq2seq + attention（纯 Python）

运行：
    python nlp.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict


# ============================================================
# 1. HMM（Rabiner 1989）
# ============================================================

class HMM:
    """
    λ = (A, B, π)
    A[i][j] = P(q_{t+1}=j | q_t=i) 转移矩阵
    B[i][o] = P(o | q_t=i) 发射矩阵
    π[i] = P(q_0=i) 初始分布
    """
    def __init__(self, states, observations, A, B, pi):
        self.states = states
        self.obs = observations
        self.A = A  # dict[state][state] → prob
        self.B = B  # dict[state][obs] → prob
        self.pi = pi  # dict[state] → prob

    def forward(self, obs_seq):
        """
        α_t(i) = P(o_1..o_t, q_t=i | λ)
        α_1(i) = π_i B_i(o_1)
        α_{t+1}(j) = [Σ_i α_t(i) A_{ij}] B_j(o_{t+1})
        返回 P(O|λ) = Σ_i α_T(i)
        """
        T = len(obs_seq)
        alpha = [{} for _ in range(T)]
        # Init
        for s in self.states:
            alpha[0][s] = self.pi.get(s, 0) * self.B[s].get(obs_seq[0], 1e-10)
        # Recursion
        for t in range(1, T):
            for j in self.states:
                s = sum(alpha[t-1][i] * self.A[i].get(j, 0) for i in self.states)
                alpha[t][j] = s * self.B[j].get(obs_seq[t], 1e-10)
        return alpha

    def backward(self, obs_seq):
        """
        β_t(i) = P(o_{t+1}..o_T | q_t=i, λ)
        β_T(i) = 1
        β_t(i) = Σ_j A_{ij} B_j(o_{t+1}) β_{t+1}(j)
        """
        T = len(obs_seq)
        beta = [{} for _ in range(T)]
        for s in self.states:
            beta[T-1][s] = 1.0
        for t in range(T - 2, -1, -1):
            for i in self.states:
                beta[t][i] = sum(
                    self.A[i].get(j, 0) * self.B[j].get(obs_seq[t+1], 1e-10) * beta[t+1][j]
                    for j in self.states
                )
        return beta

    def viterbi(self, obs_seq):
        """
        Viterbi: argmax_{q_1..q_T} P(q_1..q_T, o_1..o_T | λ)
        δ_t(j) = max over q_1..q_{t-1} P(...) with q_t=j
        δ_t(j) = [max_i δ_{t-1}(i) A_{ij}] · B_j(o_t)
        """
        T = len(obs_seq)
        delta = [{} for _ in range(T)]
        psi = [{} for _ in range(T)]
        for s in self.states:
            delta[0][s] = self.pi.get(s, 0) * self.B[s].get(obs_seq[0], 1e-10)
        for t in range(1, T):
            for j in self.states:
                best_prev, best_val = None, -1
                for i in self.states:
                    val = delta[t-1][i] * self.A[i].get(j, 0)
                    if val > best_val:
                        best_val, best_prev = val, i
                delta[t][j] = best_val * self.B[j].get(obs_seq[t], 1e-10)
                psi[t][j] = best_prev
        # Backtrack
        path = [max(delta[T-1], key=delta[T-1].get)]
        for t in range(T-1, 0, -1):
            path.append(psi[t][path[-1]])
        return path[::-1]


# ============================================================
# 2. PCFG + CKY（Jurafsky Ch 13）
# ============================================================

def cky_parse(grammar: dict, sentence: list[str]) -> bool:
    """
    CKY 算法（Cocke-Kasami-Younger）：O(n³) CYK parsing。
    grammar: {rhs_tuple: [lhs_symbols]}  （CNF 形式）
    返回 chart，sentence 是否可被文法接受。
    """
    n = len(sentence)
    # chart[i][j] = 能从 span [i..j] 推导出的 nonterminals 集合
    chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
    # 初始化对角线（单词）
    for i in range(n):
        word = sentence[i]
        for rhs, lhss in grammar.items():
            if rhs == (word,):
                for lhs in lhss:
                    chart[i][i+1].add(lhs)
    # 递推
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            for k in range(i + 1, j):
                for B in chart[i][k]:
                    for C in chart[k][j]:
                        for rhs, lhss in grammar.items():
                            if rhs == (B, C):
                                for lhs in lhss:
                                    chart[i][j].add(lhs)
    return "S" in chart[0][n], chart


# ============================================================
# 3. IBM Model 1 词对齐（Brown et al. 1993）
# ============================================================

def ibm_model1_em(source_sents, target_sents, n_iters=10):
    """
    IBM Model 1: 无隐藏结构的词对齐模型。
    P(e|f) ∝ Π_j Σ_i t(e_j|f_i) / (l+1)
    EM:
      E-step: count[e|f] += t(e|f) * P(alignment)
      M-step: t(e|f) = count[e|f] / Σ_e' count[e'|f]
    """
    # 初始化 t(e|f) 均匀
    t = defaultdict(lambda: 0.5)
    for _ in range(n_iters):
        count = defaultdict(float)
        total = defaultdict(float)
        for src, tgt in zip(source_sents, target_sents):
            src_words = ["NULL"] + src
            tgt_words = tgt
            # E-step
            for tw in tgt_words:
                s_total = sum(t[(tw, fw)] for fw in src_words)
                for fw in src_words:
                    c = t[(tw, fw)] / max(s_total, 1e-10)
                    count[(tw, fw)] += c
                    total[fw] += c
        # M-step
        for (tw, fw) in count:
            t[(tw, fw)] = count[(tw, fw)] / max(total[fw], 1e-10)
    return dict(t)


# ============================================================
# 4. mini seq2seq + attention（Bahdanau 2015）
# ============================================================

def attention_weights(query, keys):
    """
    Additive attention score (Bahdanau):
        score(q, k) = v^T tanh(W_q q + W_k k)
    简化：用点积 score(q, k_i) = q · k_i
    返回 softmax 归一化的权重。
    """
    q = query
    scores = [sum(q[j] * k[j] for j in range(len(q))) for k in keys]
    m = max(scores)
    exp_s = [math.exp(s - m) for s in scores]
    total = sum(exp_s)
    return [e / total for e in exp_s]


class MiniSeq2Seq:
    """
    极简 seq2seq（字符级反转任务演示 attention）：
    Encoder → context vector per step → attention → decoder。
    纯 Python（无 torch）用随机权重演示前向传播结构。
    """
    def __init__(self, vocab_size, hidden_dim=8):
        self.V = vocab_size
        self.H = hidden_dim
        random.seed(42)
        # embedding
        self.emb = [[random.gauss(0, 0.1) for _ in range(hidden_dim)] for _ in range(vocab_size)]
        # encoder RNN weights (simplified linear)
        self.W_enc = [[random.gauss(0, 0.1) for _ in range(hidden_dim)] for _ in range(hidden_dim)]
        # decoder
        self.W_dec = [[random.gauss(0, 0.1) for _ in range(hidden_dim + hidden_dim)] for _ in range(hidden_dim)]
        self.out = [[random.gauss(0, 0.1) for _ in range(vocab_size)] for _ in range(hidden_dim)]

    def encode(self, src_ids):
        """编码器：用 W_enc 投影 embedding → RNN 更新 → 各步不同的 hidden state（keys）"""
        h = [0.0] * self.H
        keys = []
        for tok in src_ids:
            e = self.emb[tok]
            # 用 W_enc 投影 embedding：各维度得到不同的线性组合（区别于旧版所有维度共享同一标量）
            proj = [sum(e[j] * self.W_enc[i][j] for j in range(self.H)) for i in range(self.H)]
            h = [math.tanh(h[i] * 0.5 + proj[i] * 10.0) for i in range(self.H)]
            keys.append(list(h))
        return keys, h

    def decode_step(self, prev_token, prev_hidden, keys):
        """带 attention 的解码器一步"""
        # 将 prev_token 嵌入并融入 query（旧版 prev_token 未使用）
        e_prev = self.emb[prev_token]
        query = [prev_hidden[i] + e_prev[i] for i in range(self.H)]
        # Attention: query 对 encoder keys 打分
        attn = attention_weights(query, keys)
        # context = Σ α_i key_i
        context = [sum(attn[i] * keys[i][j] for i in range(len(keys))) for j in range(self.H)]
        # concat query + context → decoder input
        dec_input = query + context
        new_hidden = [math.tanh(sum(dec_input[j] * self.W_dec[i][j] for j in range(len(dec_input))) * 0.1)
                      for i in range(self.H)]
        # output logits
        logits = [sum(new_hidden[i] * self.out[i][j] for i in range(self.H)) for j in range(self.V)]
        return logits, new_hidden, attn


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 288 NLP Demo")
    print("=" * 60)

    # 1. HMM 词性标注
    print("\n📋 1. HMM（词性标注 + Viterbi）")
    states = ["N", "V", "D"]  # Noun, Verb, Det
    obs = ["the", "dog", "runs", "fast"]
    A = {"D": {"N": 0.8, "V": 0.1, "D": 0.1},
         "N": {"V": 0.5, "N": 0.3, "D": 0.2},
         "V": {"D": 0.3, "N": 0.4, "V": 0.3}}
    B = {"D": {"the": 0.8, "dog": 0.05, "runs": 0.05, "fast": 0.1},
         "N": {"the": 0.01, "dog": 0.5, "runs": 0.3, "fast": 0.19},
         "V": {"the": 0.01, "dog": 0.05, "runs": 0.8, "fast": 0.14}}
    pi = {"D": 0.5, "N": 0.3, "V": 0.2}
    hmm = HMM(states, obs, A, B, pi)

    sentence = ["the", "dog", "runs"]
    alpha = hmm.forward(sentence)
    prob = sum(alpha[-1][s] for s in states)
    tags = hmm.viterbi(sentence)
    print(f"   句子: {sentence}")
    print(f"   Viterbi 最佳标签: {tags}")
    print(f"   P(sentence) = {prob:.6f}")

    # 2. PCFG + CKY
    print("\n📋 2. PCFG + CKY Parser")
    # CNF grammar: S→NP VP, NP→Det N, VP→V NP, Det→'the', N→'cat', N→'dog', V→'chased'
    grammar = {
        ("NP", "VP"): ["S"],
        ("Det", "N"): ["NP"],
        ("V", "NP"): ["VP"],
        ("the",): ["Det"],
        ("cat",): ["N"],
        ("dog",): ["N"],
        ("chased",): ["V"],
    }
    sent = ["the", "dog", "chased", "the", "cat"]
    accepted, chart = cky_parse(grammar, sent)
    print(f"   句子: {sent}")
    print(f"   CKY 接受: {accepted}")
    print(f"   chart[0][5] = {chart[0][5]}")

    # 3. IBM Model 1
    print("\n📋 3. IBM Model 1 词对齐")
    # 英中对照（4 句，打破对称性让每个词对都有唯一共现信号）
    src = [["the", "dog"], ["the", "cat"], ["the", "dog", "runs"], ["the", "cat", "runs"]]
    tgt = [["狗"], ["猫"], ["狗", "跑"], ["猫", "跑"]]
    t = ibm_model1_em(src, tgt, n_iters=20)
    # 显示学到的对齐概率
    print(f"   t(狗|the) = {t.get(('狗', 'the'), 0):.3f}")
    print(f"   t(狗|dog) = {t.get(('狗', 'dog'), 0):.3f}")
    print(f"   t(猫|cat) = {t.get(('猫', 'cat'), 0):.3f}")
    print(f"   t(跑|runs) = {t.get(('跑', 'runs'), 0):.3f}")

    # 4. Attention
    print("\n📋 4. Attention（seq2seq 演示）")
    seq2seq = MiniSeq2Seq(vocab_size=10, hidden_dim=8)
    src_ids = [1, 3, 5, 2]  # 输入序列
    keys, final_h = seq2seq.encode(src_ids)
    logits, new_h, attn = seq2seq.decode_step(prev_token=0, prev_hidden=final_h, keys=keys)
    print(f"   输入 token ids: {src_ids}")
    print(f"   编码后 keys 数量: {len(keys)}")
    print(f"   解码第 1 步 attention weights: {[f'{a:.3f}' for a in attn]}")
    print(f"   attention sum = {sum(attn):.4f} (应=1.0)")
    top_logit = max(range(len(logits)), key=lambda i: logits[i])
    print(f"   预测下一个 token id: {top_logit} (logit={logits[top_logit]:.3f})")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   IBM Model 1 只有 t(e|f) 翻译概率表，没有'对齐'变量，")
    print("   但 EM 隐含地对所有可能对齐做期望。")
    print("   结果：t(狗|dog), t(猫|cat), t(跑|runs) 从均匀 0.5 → 1.0（学到了正确对齐）。")
    print("   这就是 EM 的'隐变量发现'：即使不知道哪个词对齐哪个，")
    print("   通过反复迭代，模型自己'发现'了对齐结构。")
    print()
    print("   Attention 的 softmax 权重保证 Σ=1，")
    print("   不同 key 的权重差异体现了 decoder 对不同 encoder 位置的'关注'。")
    print("   Transformer 完全用 attention 替代 RNN，让序列建模并行化。")


if __name__ == "__main__":
    demo()
