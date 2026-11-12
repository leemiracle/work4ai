#!/usr/bin/env python3
"""
讲透NLP · Ch15 ASR — 配套实验: CTC 解码 (greedy + beam search) + 两个反直觉发现
对应文档: 15-自动语音识别-ASR.md

四个部分:
  Part 1: 模拟训练好的 ASR 输出 (帧级概率矩阵)
  Part 2: 从零实现 CTC greedy decode + prefix beam search decode
  Part 3: 反直觉发现 1 — blank 是 CTC 的灵魂 (去掉它, 双字母/静音全崩)
  Part 4: 反直觉发现 2 — beam search 提升 << LM rescoring (条件独立的代价)

跑法: python3 -u 15_ctc_decode.py  (纯 NumPy, ~3 秒)
"""
import numpy as np

# ============================================================
#  工具函数
# ============================================================

def softmax(x, axis=-1):
    """数值稳定的 softmax"""
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def P(*a, **kw):
    """强制 flush 的 print"""
    print(*a, **kw, flush=True)


def ctc_collapse(alignment):
    """
    CTC 折叠函数 B:
      1. 先合并连续重复字符
      2. 再去掉所有 blank ('-')
    alignment: list of chars, e.g. ['H','H','-','E','E','L',...]
    返回: 折叠后的字符串
    """
    result = []
    prev = None
    for ch in alignment:
        if ch != prev:
            result.append(ch)
        prev = ch
    return ''.join(ch for ch in result if ch != '-')


def simple_dedup(seq):
    """不用 blank 的简单去重 (只合并连续重复)"""
    result = []
    prev = None
    for ch in seq:
        if ch != prev:
            result.append(ch)
        prev = ch
    return ''.join(result)


def char_error_rate(hyp, ref):
    """
    字符错误率 CER = (S + D + I) / N
    用 Levenshtein 距离 (允许插入/删除/替换).
    返回: (cer, subs, dels, ins)
    """
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    return dp[m][n] / max(len(ref), 1), dp[m][n], 0, 0


# ============================================================
#  Part 1: 模拟训练好的 ASR 输出
# ============================================================
P("=" * 72)
P("Part 1: 模拟训练好的 ASR 输出 (帧级概率矩阵)")
P("=" * 72)

# 词表: blank '-' + H E L O P + 噪声字符 X (模拟干扰)
VOCAB = ['-', 'H', 'E', 'L', 'O', 'P', 'X']  # index 0 = blank
BLANK_IDX = 0
V = len(VOCAB)
TARGET = "HELLO"

np.random.seed(42)

# 模拟说 "HELLO" 的 18 帧音频:
#   帧  0-2: 静音    -> blank
#   帧  3-5: "H"     -> H
#   帧  6-7: 静音    -> blank
#   帧  8-9: "E"     -> E
#   帧 10:  静音     -> blank
#   帧 11-12: "L"    -> L
#   帧 13:  静音     -> blank  ← 关键! 两个 L 之间的 blank
#   帧 14-15: "L"    -> L
#   帧 16:  静音     -> blank
#   帧 17:  "O"      -> O

T = 18
frame_labels = [
    '-', '-', '-',      # 0-2
    'H', 'H', 'H',      # 3-5
    '-', '-',            # 6-7
    'E', 'E',            # 8-9
    '-',                 # 10
    'L', 'L',            # 11-12
    '-',                 # 13 ← 双 L 的分隔!
    'L', 'L',            # 14-15
    '-',                 # 16
    'O',                 # 17
]

# logits: 每帧正确字符的 logit 设为高值, 其余随机低值
logits = np.random.randn(T, V) * 0.3
for t in range(T):
    true_char = frame_labels[t]
    true_idx = VOCAB.index(true_char)
    logits[t, true_idx] += 3.0  # 强信号
    # 随机给某个错误字符一点干扰 (模拟条件独立的缺陷)
    if np.random.rand() < 0.2:
        noise_idx = np.random.randint(1, V)  # 不干扰 blank
        logits[t, noise_idx] += 1.5

probs = softmax(logits, axis=-1)  # (T, V)

P(f"\n词表: {VOCAB}")
P(f"目标序列: '{TARGET}'")
P(f"输入帧数 T={T}, 词表大小 V={V}")

argmax_alignment = [VOCAB[i] for i in np.argmax(probs, axis=1)]
P(f"\n每帧 argmax (greedy 对齐): {''.join(argmax_alignment)}")
P(f"  折叠后: '{ctc_collapse(argmax_alignment)}'")

P(f"\n前 6 帧的概率分布 (top-3):")
for t in range(min(6, T)):
    top3 = np.argsort(probs[t])[::-1][:3]
    parts = "  ".join(f"{VOCAB[i]}={probs[t, i]:.2f}" for i in top3)
    P(f"  帧{t:2d}: {parts}")


# ============================================================
#  Part 2: CTC Greedy Decode + Prefix Beam Search
# ============================================================
P("\n" + "=" * 72)
P("Part 2: 从零实现 CTC Greedy + Prefix Beam Search")
P("=" * 72)


def ctc_greedy_decode(probs, vocab, blank_idx=0):
    """CTC Greedy: 每帧 argmax → 合并重复 → 去 blank"""
    alignment = [vocab[i] for i in np.argmax(probs, axis=1)]
    return ctc_collapse(alignment)


def ctc_beam_search_decode(probs, vocab, blank_idx=0, beam_width=5):
    """
    CTC Prefix Beam Search (Hannun 2017, "Sequence Modeling with CTC")

    核心思想: 对每个候选前缀维护两个概率:
      pb  = 对齐路径以 blank 结尾的累计概率
      pnb = 对齐路径以非 blank 字符结尾的累计概率

    这是因为: 当连续输出同一个字符 c 时, 是否产生新字符
    取决于前一个输出是否是 blank:
      ...c c   → 折叠为 c   (不产生新字符, prefix 不变)
      ...c - c → 折叠为 cc  (产生新字符, prefix 扩展!)
    所以必须分别跟踪 blank 结尾和非 blank 结尾的概率.
    """
    T, V = probs.shape
    # beam: {prefix_tuple: {'pb': float, 'pnb': float}}
    beam = {(): {'pb': 1.0, 'pnb': 0.0}}

    for t in range(T):
        new_beam = {}

        for prefix, d in beam.items():
            pb = d['pb']    # prob ending in blank
            pnb = d['pnb']  # prob ending in non-blank
            total = pb + pnb

            for c in range(V):
                y = probs[t, c]
                char = vocab[c]

                if c == blank_idx:
                    # blank: prefix 不变, 现在以 blank 结尾
                    key = prefix
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pb'] += total * y

                elif len(prefix) > 0 and prefix[-1] == char:
                    # 当前字符 == 前缀最后一个字符
                    # Case A: 连续重复 (前一个也是 c, 非 blank 结尾)
                    #   折叠后不变, 仍然是非 blank 结尾
                    key = prefix
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pnb'] += pnb * y

                    # Case B: blank 后的新 c (blank 结尾 → 现在输出 c)
                    #   折叠后产生新字符! prefix 扩展
                    key2 = prefix + (char,)
                    if key2 not in new_beam:
                        new_beam[key2] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key2]['pnb'] += pb * y

                else:
                    # 不同字符: prefix 必定扩展
                    key = prefix + (char,)
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pnb'] += total * y

        # 剪枝: 保留 total prob 最大的 beam_width 个
        sorted_items = sorted(
            new_beam.items(),
            key=lambda x: x[1]['pb'] + x[1]['pnb'],
            reverse=True
        )
        beam = dict(sorted_items[:beam_width])

    best = max(beam.items(), key=lambda x: x[1]['pb'] + x[1]['pnb'])
    best_score = best[1]['pb'] + best[1]['pnb']
    return ''.join(best[0]), best_score


# 运行 Greedy
greedy_result = ctc_greedy_decode(probs, VOCAB, BLANK_IDX)
P(f"\nGreedy decode 结果:  '{greedy_result}'")

# 运行 Beam Search (不同 beam width)
P(f"\nBeam search decode 结果:")
for bw in [1, 3, 5, 10]:
    result, score = ctc_beam_search_decode(probs, VOCAB, BLANK_IDX, beam_width=bw)
    cer, _, _, _ = char_error_rate(result, TARGET)
    marker = " ← beam=1 不是 greedy!" if bw == 1 else ""
    P(f"  beam_width={bw:2d}: '{result}'  (prob={score:.4e}, CER={cer:.1%}){marker}")

P(f"\n  参考答案:           '{TARGET}'")
P(f"  (beam=1 与 greedy 不同, 因为 beam search 对所有路径求和,")
P(f"   而 greedy 只取每帧最优 → 路径求和可能改变最优前缀)")


# ============================================================
#  Part 3: 反直觉发现 1 — blank 是 CTC 的灵魂
# ============================================================
P("\n" + "=" * 72)
P("反直觉发现 1: blank 是 CTC 的灵魂")
P("  去掉 blank, greedy decode 直接崩溃")
P("=" * 72)

P(f"\n完整对齐 (含 blank): {''.join(argmax_alignment)}")
P(f"CTC 折叠后:          '{ctc_collapse(argmax_alignment)}'")

# 模拟"不用 blank": 去掉 blank 列, 静音帧会随机挑一个字符
P(f"\n模拟: 如果没有 blank, 静音帧会输出什么?")
P(f"(静音帧模型没有明确目标 → 会随机挑一个高概率字符)")

no_blank_probs = probs[:, 1:].copy()  # 去掉 blank 列 (index 0)
no_blank_vocab = VOCAB[1:]            # ['H','E','L','O','P','X']
no_blank_argmax = [no_blank_vocab[i] for i in np.argmax(no_blank_probs, axis=1)]
P(f"无 blank 对齐: {''.join(no_blank_argmax)}")

deduped = simple_dedup(no_blank_argmax)
P(f"简单去重后:    '{deduped}'")
cer_no_blank, _, _, _ = char_error_rate(deduped, TARGET)
P(f"CER (无 blank): {cer_no_blank:.1%}")

cer_with_blank, _, _, _ = char_error_rate(ctc_collapse(argmax_alignment), TARGET)
P(f"CER (有 blank): {cer_with_blank:.1%}")

P(f"\n{'─'*55}")
P("★ 结论: 没有 blank, 静音帧产生的噪声字符全部混入输出!")
P("  blank 允许'这帧不输出任何东西', 是 CTC 处理变长的关键.")
P(f"{'─'*55}")

# 单独演示: 双字母分隔问题
P(f"\n额外演示: blank 如何分隔双字母")
P(f"  目标 'HELLO' 有两个连续的 L:")
double_l_with = ['L', 'L', '-', 'L', 'L']
P(f"    有 blank: {''.join(double_l_with)} → '{ctc_collapse(double_l_with)}' ✓")
double_l_without = ['L', 'L', 'L', 'L']
P(f"    无 blank: {''.join(double_l_without)} → '{simple_dedup(double_l_without)}' ✗ (丢了一个 L!)")
P(f"\n  blank 在两个 L 之间充当'分隔符', 让折叠函数知道这是两个独立的 L.")


# ============================================================
#  Part 4: 反直觉发现 2 — beam search << LM rescoring
# ============================================================
P("\n" + "=" * 72)
P("反直觉发现 2: beam search 提升极小, 语言模型 rescoring 提升巨大")
P("  CTC 条件独立假设 → 解码算法优化空间有限 → 语言知识才是关键")
P("=" * 72)


def generate_test_sample(word, V, vocab, signal=4.0, noise_level=0.8,
                         interference_rate=0.25, interference_boost=3.0):
    """
    为一个词生成帧级概率矩阵.
    中等噪声 + 定向干扰 → 模拟条件独立的缺陷: greedy 偶尔出错.
    干扰专门针对非 blank 字符 (包括噪声字符 X), 造成替换/插入.
    """
    frames_spec = ['-'] * 2
    for i, ch in enumerate(word):
        n_frames = np.random.randint(2, 4)
        frames_spec.extend([ch] * n_frames)
        if i < len(word) - 1:
            frames_spec.extend(['-'] * np.random.randint(1, 3))
    frames_spec.extend(['-'] * 2)

    T = len(frames_spec)
    logits = np.random.randn(T, V) * noise_level
    for t in range(T):
        true_idx = vocab.index(frames_spec[t])
        logits[t, true_idx] += signal
        if np.random.rand() < interference_rate:
            candidates = [i for i in range(1, V) if i != true_idx]
            noise_idx = np.random.choice(candidates)
            logits[t, noise_idx] += interference_boost
    return softmax(logits, axis=-1), word


def ctc_beam_search_nbest(probs, vocab, blank_idx=0, beam_width=10, nbest=5):
    """CTC prefix beam search, 返回 top-nbest 个候选及其概率."""
    T, V = probs.shape
    beam = {(): {'pb': 1.0, 'pnb': 0.0}}

    for t in range(T):
        new_beam = {}
        for prefix, d in beam.items():
            pb, pnb = d['pb'], d['pnb']
            total = pb + pnb
            for c in range(V):
                y = probs[t, c]
                char = vocab[c]
                if c == blank_idx:
                    key = prefix
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pb'] += total * y
                elif len(prefix) > 0 and prefix[-1] == char:
                    key = prefix
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pnb'] += pnb * y
                    key2 = prefix + (char,)
                    if key2 not in new_beam:
                        new_beam[key2] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key2]['pnb'] += pb * y
                else:
                    key = prefix + (char,)
                    if key not in new_beam:
                        new_beam[key] = {'pb': 0.0, 'pnb': 0.0}
                    new_beam[key]['pnb'] += total * y
        sorted_items = sorted(new_beam.items(),
                              key=lambda x: x[1]['pb'] + x[1]['pnb'], reverse=True)
        beam = dict(sorted_items[:beam_width])

    # 返回 top-nbest
    ranked = sorted(beam.items(), key=lambda x: x[1]['pb'] + x[1]['pnb'], reverse=True)
    results = []
    for prefix, d in ranked[:nbest]:
        results.append((''.join(prefix), d['pb'] + d['pnb']))
    return results


def dictionary_rescoring(nbest_list, valid_words):
    """
    词典级 LM rescoring (模拟真实 ASR 的 word-level LM):
    1. 如果候选已是合法词, 直接返回
    2. 否则, 综合考虑 CTC概率 和 与最近合法词的编辑距离
    """
    best_word = None
    best_score = -1e9
    for candidate, ctc_prob in nbest_list:
        # LM 分数: 合法词给高分, 非法词按编辑距离惩罚
        if candidate in valid_words:
            lm_score = 0.0
        else:
            # 找最近的合法词, 编辑距离越小越好
            min_dist = min(
                _levenshtein(candidate, w) for w in valid_words
            )
            lm_score = -2.0 * min_dist  # 每个编辑距离扣 2 分

        # 综合得分 = log(CTC概率) + LM分数
        combined = np.log(ctc_prob + 1e-12) + lm_score
        if combined > best_score:
            best_score = combined
            best_word = candidate if candidate in valid_words else \
                min(valid_words, key=lambda w: _levenshtein(candidate, w))
    return best_word


def _levenshtein(a, b):
    """编辑距离"""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    return dp[n]


# ---- 在多个测试样本上统计平均 CER ----
test_words = ["HELLO", "HELP", "HOPE", "HELL", "HOLE", "POLO", "HOOP", "PEEL"]
valid_set = set(test_words)
N_TEST = 100

P(f"\n在 {N_TEST} 个随机测试样本上统计平均 CER...")
P(f"测试词: {test_words}")
P(f"噪声设置: signal=4.0, noise=0.8, interference_rate=0.25, boost=3.0")
P(f"LM: 词典型 word-level LM (8 个合法词), N-best rescoring")

np.random.seed(777)
samples = []
for trial in range(N_TEST):
    word = test_words[trial % len(test_words)]
    p, w = generate_test_sample(word, V, VOCAB)
    samples.append((p, w))

results = {'greedy': [], 'beam5': [], 'beam10': [], 'beam20': [], 'dict': []}

for probs_test, word in samples:
    # Greedy
    g = ctc_greedy_decode(probs_test, VOCAB, BLANK_IDX)
    results['greedy'].append(char_error_rate(g, word)[0])

    # Beam search (不同宽度)
    for bw, key in [(5, 'beam5'), (10, 'beam10'), (20, 'beam20')]:
        b, _ = ctc_beam_search_decode(probs_test, VOCAB, BLANK_IDX, beam_width=bw)
        results[key].append(char_error_rate(b, word)[0])

    # N-best + 词典 rescoring
    nbest = ctc_beam_search_nbest(probs_test, VOCAB, BLANK_IDX, beam_width=20, nbest=5)
    d = dictionary_rescoring(nbest, valid_set)
    results['dict'].append(char_error_rate(d, word)[0])

avg = {k: np.mean(v) for k, v in results.items()}

P(f"\n平均字符错误率 (CER):")
P(f"  Greedy:                   {avg['greedy']:.1%}")
P(f"  Beam search (bw=5):       {avg['beam5']:.1%}")
P(f"  Beam search (bw=10):      {avg['beam10']:.1%}")
P(f"  Beam search (bw=20):      {avg['beam20']:.1%}")
P(f"  N-best + 词典 rescoring:  {avg['dict']:.1%}")

improve_beam = (avg['greedy'] - avg['beam20']) / avg['greedy'] * 100 if avg['greedy'] > 0 else 0
improve_dict = (avg['greedy'] - avg['dict']) / avg['greedy'] * 100 if avg['greedy'] > 0 else 0

P(f"\n{'─'*58}")
P(f"  Beam(20) vs Greedy 提升:      {improve_beam:6.1f}%  ← 解码算法优化")
P(f"  词典 rescoring vs Greedy 提升: {improve_dict:6.1f}%  ← 语言知识注入")
if abs(improve_beam) > 0.5:
    ratio = improve_dict / improve_beam if abs(improve_beam) > 0.5 else float('inf')
    direction = "提升是 beam 的" if improve_beam > 0 else "beam 甚至更差, 而词典提升"
    P(f"  词典 {direction}:        {abs(ratio):6.1f}x")
else:
    P(f"  → Beam search 基本无提升 (条件独立的天花板)")
P(f"  → 词典 rescoring 大幅降低 CER (补回语言知识)")
P(f"{'─'*58}")

P(f"""
★ 反直觉结论:

  1. beam search 加宽 (5→10→20) 对 CER 几乎没帮助 (甚至更差!)
     → CTC 假设帧间条件独立, beam search 只能在
       '选哪条对齐路径'上优化, 无法引入字符间依赖
     → 解码算法已接近条件独立假设的天花板

  2. 词典型 LM rescoring 大幅降低 CER ({avg['greedy']*100:.1f}% → {avg['dict']*100:.1f}%)
     → 语言模型注入了'哪些词是合法的'知识
     → 这正是 CTC 条件独立假设丢失的信息

  本质: CTC 的信息损失发生在'概率分解'阶段 (∏ p(πₜ|X)),
        不在'解码算法'阶段. 再大的 beam width 也救不回来.

  这就是为什么现代 ASR:
    • CTC 系统 → 必须外接 LM (n-gram / neural LM)
    • Attention 系统 → decoder 自带 LM, 但不能流式
    • Whisper → 68万小时数据把语言知识全内化在 decoder
""")

# ============================================================
#  总结
# ============================================================
P("=" * 72)
P("总结: CTC 的两个核心教训")
P("=" * 72)
P("""
  1. blank 不是"空", 是"分隔符"
     → 没有它, 变长对齐和双字母都无法处理
     → CTC 的全部魔法在于 blank + 折叠函数 B

  2. 条件独立是 CTC 的原罪
     → beam search 再大也提升有限 (因为信息在分解时就丢了)
     → LM rescoring 提升巨大 (因为补回了字符间依赖)
     → 这解释了为什么 ASR 从 CTC 走向 Attention, 再走向 Whisper

  ASR 30 年的演化: 从"手工拆分"到"端到端", 再到"暴力 scale".
  和 NLP 从 pipeline 到 LLM 的演化完全同构.
""")
