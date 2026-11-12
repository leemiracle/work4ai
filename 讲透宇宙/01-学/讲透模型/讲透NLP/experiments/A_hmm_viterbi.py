#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 A 配套实验：HMM 与 Viterbi 算法（从零实现）
====================================================================
纯 NumPy，几秒跑完。

核心：用 Viterbi 做 POS tagging（词性标注），状态=N/V，观测=单词。

★ 反直觉发现：
  "duck" 这个词的发射概率 V 略高于 N（0.21 vs 0.19），
  逐词贪心（只看发射概率）会判 duck = V（动词）。
  但 Viterbi 综合了转移概率 P(N|V)=0.8 >> P(V|V)=0.2，
  正确判出 duck = N（名词）——上下文完全压过了词本身。

python3 experiments/A_hmm_viterbi.py
"""
import math
import numpy as np

def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 1. 定义微型 HMM
# ============================================================
# 状态：N(名词), V(动词)
STATES = ['N', 'V']
N_STATES = len(STATES)

# 观测词表
VOCAB = ['fly', 'duck', 'fish', 'birds']
W2I = {w: i for i, w in enumerate(VOCAB)}
N_VOCAB = len(VOCAB)

# 初始概率 π：句子首词更可能是名词
PI = np.array([0.7, 0.3])

# 转移矩阵 A[i][j] = P(state j | state i)
#    to:  N    V
A = np.array([
    [0.6, 0.4],  # from N: 名词后接动词很常见(N→V)
    [0.8, 0.2],  # from V: 动词后接名词很常见(V→N)
])

# 发射矩阵 B[j][k] = P(word k | state j)
# 注意：duck 的发射 V(0.21) 略高于 N(0.19)
#          fly   duck  fish  birds
B = np.array([
    [0.10, 0.19, 0.21, 0.50],  # from N: birds 强烈名词
    [0.40, 0.21, 0.19, 0.20],  # from V: fly 强烈动词
])

# 验证概率归一
assert np.allclose(PI.sum(), 1.0), "PI must sum to 1"
assert np.allclose(A.sum(axis=1), 1.0), "A rows must sum to 1"
assert np.allclose(B.sum(axis=1), 1.0), "B rows must sum to 1"


# ============================================================
# 2. 前向算法（问题 1：评估 P(O|λ)）
# ============================================================
def forward(observations, A, B, PI):
    """
    前向算法。
    observations: list of observation indices [o_1, ..., o_T]
    返回 alpha: (T, N) 每行是 alpha_t(j)
    """
    T = len(observations)
    N = A.shape[0]
    alpha = np.zeros((T, N))
    # 初始化
    alpha[0] = PI * B[:, observations[0]]
    # 递推
    for t in range(1, T):
        for j in range(N):
            alpha[t, j] = np.sum(alpha[t-1] * A[:, j]) * B[j, observations[t]]
    return alpha


# ============================================================
# 3. Viterbi 算法（问题 2：解码最优状态序列）
# ============================================================
def viterbi(observations, A, B, PI):
    """
    Viterbi 解码（log 空间，数值稳定）。
    返回 (best_path, delta_log, psi)
    """
    T = len(observations)
    N = A.shape[0]

    log_A = np.log(A + 1e-30)
    log_B = np.log(B + 1e-30)
    log_PI = np.log(PI + 1e-30)

    delta = np.full((T, N), -np.inf)   # log 最优路径概率
    psi = np.zeros((T, N), dtype=int)   # 回溯指针

    # 初始化
    delta[0] = log_PI + log_B[:, observations[0]]
    psi[0] = -1  # 无前驱

    # 递推
    for t in range(1, T):
        for j in range(N):
            candidates = delta[t-1] + log_A[:, j]
            psi[t, j] = np.argmax(candidates)
            delta[t, j] = candidates[psi[t, j]] + log_B[j, observations[t]]

    # 回溯
    path = np.zeros(T, dtype=int)
    path[-1] = np.argmax(delta[-1])
    for t in range(T-2, -1, -1):
        path[t] = psi[t+1, path[t+1]]

    return path, delta, psi


# ============================================================
# 4. 逐词贪心（只看发射概率，不看转移）—— 作为对照组
# ============================================================
def greedy_decode(observations, B, PI):
    """每个位置独立取 argmax，先验只在 t=1 起作用。"""
    T = len(observations)
    path = np.zeros(T, dtype=int)
    path[0] = np.argmax(PI * B[:, observations[0]])
    for t in range(1, T):
        path[t] = np.argmax(B[:, observations[t]])
    return path


# ============================================================
# 主程序
# ============================================================
def main():
    P("=" * 68)
    P("讲透NLP · 附录 A：HMM 与 Viterbi（从零实现）")
    P("=" * 68)

    P(f"""
  微型 HMM:
    状态 = {{N(名词), V(动词)}}
    词表 = {VOCAB}

  初始概率 π = {PI}  (首词偏名词)

  转移矩阵 A[i→j]:
        to N   to V
    N:   {A[0,0]:.1f}    {A[0,1]:.1f}
    V:   {A[1,0]:.1f}    {A[1,1]:.1f}   ← V→N={A[1,0]:.1f} >> V→V={A[1,1]:.1f}

  发射矩阵 B[state→word]:
           fly   duck  fish  birds
    N:    {B[0,0]:.2f}  {B[0,1]:.2f}  {B[0,2]:.2f}  {B[0,3]:.2f}
    V:    {B[1,0]:.2f}  {B[1,1]:.2f}  {B[1,2]:.2f}  {B[1,3]:.2f}
         ↑            ↑
         fly=V强      duck: V(0.21) 略 > N(0.19)!
""")

    # ----------------------------------------------------------
    # Part 1：前向算法 —— 计算 P(O|λ)
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 1：前向算法 —— 评估 P(O | λ)")
    P("-" * 68)

    sentence1 = "birds fly duck"
    obs1 = [W2I[w] for w in sentence1.split()]

    alpha = forward(obs1, A, B, PI)
    P_O = alpha[-1].sum()

    P(f"\n  句子: '{sentence1}'")
    P(f"  观测索引: {obs1} = [{', '.join(VOCAB[i] for i in obs1)}]")
    P(f"\n  前向概率表 α_t(j):")
    P(f"  {'t':>4}  {'观测':>8}  {'α(N)':>12}  {'α(V)':>12}")
    for t in range(len(obs1)):
        P(f"  {t+1:>4}  {VOCAB[obs1[t]]:>8}  {alpha[t,0]:>12.6f}  {alpha[t,1]:>12.6f}")
    P(f"\n  P(O|λ) = Σ α_T(j) = {P_O:.6f}")
    P(f"           = e^(-{-math.log(P_O):.3f})")
    P(f"  → 这条观测序列在当前模型下的似然值")

    # ----------------------------------------------------------
    # Part 2：Viterbi 解码
    # ----------------------------------------------------------
    P("\n" + "-" * 68)
    P("Part 2：Viterbi 解码 —— 找最可能的词性序列")
    P("-" * 68)

    P(f"\n  句子: '{sentence1}'")
    P(f"  逐词展开 Viterbi 递推（log 空间）:\n")

    path1, delta1, psi1 = viterbi(obs1, A, B, PI)

    P(f"  {'t':>4}  {'词':>8}  {'δ(N)':>10}  {'δ(V)':>10}  {'ψ(N)':>6}  {'ψ(V)':>6}")
    P("  " + "-" * 52)
    for t in range(len(obs1)):
        psi_N = STATES[psi1[t, 0]] if psi1[t, 0] >= 0 else "—"
        psi_V = STATES[psi1[t, 1]] if psi1[t, 1] >= 0 else "—"
        P(f"  {t+1:>4}  {VOCAB[obs1[t]]:>8}  {delta1[t,0]:>10.4f}  {delta1[t,1]:>10.4f}  {psi_N:>6}  {psi_V:>6}")

    P(f"\n  最优路径（回溯）: {' '.join(STATES[s] for s in path1)}")
    P(f"  即: {' '.join(f'{VOCAB[obs1[t]]}({STATES[path1[t]]})' for t in range(len(obs1)))}")

    # ----------------------------------------------------------
    # Part 3：★ 反直觉 —— 上下文 vs 发射概率
    # ----------------------------------------------------------
    P("\n" + "-" * 68)
    P("Part 3：★ 反直觉发现 —— 转移概率压过发射概率")
    P("-" * 68)

    # 逐词贪心（只看发射概率）
    greedy1 = greedy_decode(obs1, B, PI)

    P(f"""
  句子: '{sentence1}'
  词: {"  ".join(VOCAB[obs1[t]] for t in range(len(obs1)))}

  ┌────────────────────────────────────────────────────────────┐
  │ 方法对比                                                   │
  ├────────────────────────────────────────────────────────────┤
  │ 逐词贪心 (只看发射概率):
  │   birds → argmax B(·|birds) = N  (0.50 > 0.20) ✓
  │   fly   → argmax B(·|fly)   = V  (0.40 > 0.10) ✓
  │   duck  → argmax B(·|duck)  = V  (0.21 > 0.19) ✗ ← 错!
  │   结果: {' '.join(STATES[s] for s in greedy1)}
  │
  │ Viterbi (发射 + 转移):
  │   birds → N  ✓
  │   fly   → V  ✓  (δ_V={delta1[1,1]:.4f} >> δ_N={delta1[1,0]:.4f})
  │   duck  → N  ✓  ← 转折点!
  │   结果: {' '.join(STATES[s] for s in path1)}
  └────────────────────────────────────────────────────────────┘
""")

    # 详细分析 duck 的决策
    P("  为什么 duck 判成了 N？看 t=3 的递推细节:\n")
    duck_idx = obs1[2]
    P(f"  发射概率: B(N→duck)={B[0,duck_idx]:.2f}, B(V→duck)={B[1,duck_idx]:.2f}")
    P(f"            → 发射单独看: V 略占优 (0.21 vs 0.19)\n")

    P(f"  但 t=2 的最优路径到 t=3:")
    P(f"    δ_V(t=2) = {delta1[1,1]:.4f}  (fly 被正确判为 V)")

    # 计算 t=3 的各路径
    log_A = np.log(A + 1e-30)
    log_B = np.log(B + 1e-30)

    to_N_from_V = delta1[1,1] + log_A[1,0] + log_B[0,duck_idx]
    to_V_from_V = delta1[1,1] + log_A[1,1] + log_B[1,duck_idx]

    P(f"\n    到 N: δ_V(t=2) + log A(V→N) + log B(N→duck)")
    P(f"         = {delta1[1,1]:.4f} + {log_A[1,0]:.4f} + {log_B[0,duck_idx]:.4f}")
    P(f"         = {to_N_from_V:.4f}")
    P(f"\n    到 V: δ_V(t=2) + log A(V→V) + log B(V→duck)")
    P(f"         = {delta1[1,1]:.4f} + {log_A[1,1]:.4f} + {log_B[1,duck_idx]:.4f}")
    P(f"         = {to_V_from_V:.4f}")

    ratio = math.exp(to_N_from_V - to_V_from_V)
    P(f"\n    N 路径 / V 路径 = e^({to_N_from_V:.4f} - {to_V_from_V:.4f}) = {ratio:.2f}×")
    P(f"\n  ★ 结论: 发射概率差 0.21/0.19 = {0.21/0.19:.2f}× (微弱 V 优势)")
    P(f"           转移概率差 0.8/0.2 = {0.8/0.2:.1f}× (巨大 N 优势)")
    P(f"           转移完全压过发射 → duck = N ✓")
    P(f"           贪心只看发射 → duck = V ✗")

    # ----------------------------------------------------------
    # Part 4：更多例子验证
    # ----------------------------------------------------------
    P("\n" + "-" * 68)
    P("Part 4：更多句子验证")
    P("-" * 68)

    test_sentences = [
        "birds fly duck",
        "fish fly birds",
        "birds duck fish",
        "fish duck birds",
    ]

    P(f"\n  {'句子':<24} {'贪心(只看发射)':>16} {'Viterbi':>14} {'是否一致':>10}")
    P("  " + "-" * 68)
    for sent in test_sentences:
        obs = [W2I[w] for w in sent.split()]
        vg = greedy_decode(obs, B, PI)
        vt, _, _ = viterbi(obs, A, B, PI)
        same = "✓" if list(vg) == list(vt) else "✗ 不同!"
        P(f"  {sent:<24} {' '.join(STATES[s] for s in vg):>16} "
          f"{' '.join(STATES[s] for s in vt):>14} {same:>10}")

    P(f"""
  观察: 贪心和 Viterbi 经常不一致。不一致的地方，
        就是"上下文(转移)修正了逐词判断(发射)"的地方。
""")

    # ----------------------------------------------------------
    # Part 5：Baum-Welch 简介（概念演示）
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 5：Baum-Welch 学习（概念说明）")
    P("-" * 68)
    P("""
  Baum-Welch = EM 应用于 HMM:
    E 步: 用当前 A,B,π 算 γ_t(i) 和 ξ_t(i,j)
          （每个时刻处于各状态/做各转移的后验概率）
    M 步: 重估参数:
          π_i = γ_1(i)
          a_ij = Σ_t ξ_t(i,j) / Σ_t γ_t(i)
          b_j(k) = Σ_{t:o_t=k} γ_t(j) / Σ_t γ_t(j)

  本实验跳过实现（需要对无标注数据做 EM）。
  在实际 POS tagging 中，通常有标注数据直接统计 A,B,π，
  不需要 Baum-Welch（那更适合语音识别中无文本标注的声学数据）。
""")

    # ----------------------------------------------------------
    # 总结
    # ----------------------------------------------------------
    P("=" * 68)
    P("一句话总结")
    P("=" * 68)
    P("""
  HMM 三个问题的算法:
    前向算法 (sum)  → 评估 P(O|λ)
    Viterbi  (max)  → 解码最优状态序列
    Baum-Welch (EM) → 学习最优参数

  ★ 反直觉: 词本身的歧义（发射概率）可以被上下文（转移概率）
    完全推翻。"duck" 的发射略偏 V，但 Viterbi 判它为 N——
    因为动词后接名词(0.8)远比动词后接动词(0.2)常见。

  这就是为什么 POS tagging 不能逐词判断，必须看序列。
  也是为什么 HMM/CRF/BiLSTM-CRF 用序列模型——
  单个词的词性取决于它前后是什么。
""")


if __name__ == "__main__":
    main()
