"""01 NLP 导论实验：歧义性多层面演示 + 三代方法消歧对比。纯标准库，几秒跑完。
铁证 1: 一句 5 词英文在"词法层"就有多种歧义组合；
铁证 2: 规则/统计/神经三代方法对同一歧义的消歧思路完全不同（各有死角）。
对应讲透NLP/01-导论-NLP全景.md §3、§5。
"""
from itertools import product
from collections import Counter

SENTENCE = "I saw her duck"

# 词法歧义词典：每个歧义词的多种 (词性, 词义)
LEXICON = {
    "duck": [("N", "鸭子"), ("V", "躲避/低头")],
    "saw":  [("V_past", "看见(see 过去式)"), ("N", "锯子")],
    "her":  [("PRP$", "她的(物主)"), ("PRP", "她(宾格)")],
}

print("=" * 60)
print(f"Part A: 多层歧义演示 —— 原句 \"{SENTENCE}\"")
print("=" * 60)
print("\n歧义词的可能解读:")
for word in SENTENCE.split():
    senses = LEXICON.get(word.lower())
    if senses:
        print(f"  {word:5s} → {len(senses)} 种: {senses}")

# 枚举所有词法组合
combos = [[(w, s[0], s[1]) for s in LEXICON.get(w.lower(), [("?", w)])] for w in SENTENCE.split()]
total = 1
for c in combos:
    total *= len(c)
print(f"\n仅【词法层】的歧义组合总数: {total} 种（尚未含句法/语义/语用层）")
print("枚举:")
for i, combo in enumerate(product(*combos), 1):
    gloss = " ".join(f"{w}({pos})" for w, pos, _ in combo)
    meaning = " + ".join(g for _, _, g in combo)
    print(f"  解读{i}: {gloss}")
    print(f"         含义: {meaning}")

# === Part B: 三代方法对 duck 词性消歧 ===
print("\n" + "=" * 60)
print("Part B: 三代方法消歧同一歧义（duck: 名词 vs 动词）")
print("上下文: 'I saw her duck'")
print("=" * 60)

print("\n① 规则派（1950s-80s）: 手写 if-then 规则")
print("   规则示例: IF her=PRP$(物主) THEN duck=N; IF her=PRP(宾格) THEN duck=V")
print("   痛点: 必须先消 her 的歧义 → 规则依赖外部知识，覆盖不到就崩")

print("\n② 统计派（1990s-2010s）: 数语料频次")
CORPUS_BIASED_N = ["her duck swam", "feed her duck", "her duck quacked"]  # duck=N 上下文
CORPUS_BIASED_V = ["watch her duck", "her duck under", "saw her duck"]    # duck=V 上下文
NOUN_AFTER = {"swam", "quacked", "flew"}      # duck 后接这些 → 多半是名词
VERB_AFTER = {"under", "down", "into"}        # duck 后接这些 → 多半是动词
all_sents = CORPUS_BIASED_N + CORPUS_BIASED_V
votes = Counter()
for sent in all_sents:
    ws = sent.split()
    if "duck" in ws and ws.index("duck") + 1 < len(ws):
        nxt = ws[ws.index("duck") + 1]
        if nxt in NOUN_AFTER:
            votes["N"] += 1
        elif nxt in VERB_AFTER:
            votes["V"] += 1
print(f"   玩具语料({len(all_sents)} 句)统计 'her duck' 后接词 → 推词性:")
print(f"   投票: {dict(votes)}")
print("   痛点: 只看局部 bigram，'watch her duck' 这种模糊上下文仍难；数据稀疏")

print("\n③ 神经派（2014-）: 整句编码成向量，端到端学词性")
print("   做法: 把 'I saw her duck' 编码成 768 维向量 → softmax 输出 duck 的词性")
print("   优势: 看全句上下文 + 连续表示可泛化（ducking/ducks 互帮）")
print("   代价: 黑箱 / 需大数据 / 幻觉（新型歧义）")

print("\n" + "=" * 60)
print("铁证结论")
print("=" * 60)
print(f"1. 一句 {len(SENTENCE.split())} 词的英文，仅词法层就有 {total} 种歧义组合；")
print(f"   加上句法（her 修饰谁）+ 语义（saw 看见/锯）+ 语用（农场/木工坊），")
print(f"   合法解读远不止 {total} 种。")
print("2. 三代方法各能部分消歧，但各有死角：")
print("   规则=可解释但脆；统计=数据驱动但短视；神经=强大但黑箱。")
print("→ 歧义是 NLP 核心难点，贯穿每一层；三代方法史 = 一部消歧方法进化史。")
