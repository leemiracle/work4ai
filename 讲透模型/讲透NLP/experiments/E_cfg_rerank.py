#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 E 配套实验：PCFG + 词法化重排序（PP 附着歧义）
================================================================
纯 Python 标准库，几秒跑完。

核心：用概率 CKY 解析 PP 附着歧义句，然后用词法化特征重排。

★ 反直觉发现：
  PCFG 对 "eat pizza with fork" 和 "eat pizza with olives"
  给出完全相同的解析树概率（规则不含词）。
  仅加一个 PP 宾语偏好特征，立刻区分
  "用叉子吃"（VP 附着）vs "带橄榄的披萨"（NP 附着）。

python3 experiments/E_cfg_rerank.py
"""
import math

# ============================================================
# 1. 玩具 PCFG（CNF 兼容）
# ============================================================
# 词法规则: word → [(category, prob)]
LEXICAL: dict[str, list[tuple[str, float]]] = {
    "i":         [("Pron", 1.0)],
    "eat":       [("V", 1.0)],
    "saw":       [("V", 1.0)],
    "pizza":     [("N", 1.0)],
    "fork":      [("N", 1.0)],
    "olives":    [("N", 1.0)],
    "cheese":    [("N", 1.0)],
    "man":       [("N", 1.0)],
    "telescope": [("N", 1.0)],
    "with":      [("P", 1.0)],
    "the":       [("Det", 1.0)],
    "a":         [("Det", 1.0)],
}

# 二元规则: (LHS, B, C, prob)   —— 约束: 同一 LHS 的所有规则概率和=1
BINARY: list[tuple[str, str, str, float]] = [
    ("S",   "NP", "VP", 1.0),
    ("NP",  "Det", "N",  0.30),
    ("NP",  "NP",  "PP", 0.25),   # PP 附着 NP
    ("VP",  "V",   "NP", 0.50),   # V + 直接宾语
    ("VP",  "VP",  "PP", 0.35),   # PP 附着 VP
    ("PP",  "P",   "NP", 1.0),
]

# 单元规则: (LHS, B, prob)
UNARY: list[tuple[str, str, float]] = [
    ("NP", "Pron", 0.20),
    ("NP", "N",    0.25),
    ("VP", "V",    0.15),
]
# 概率和检查: NP=0.30+0.25+0.20+0.25=1.0 ✓  VP=0.50+0.35+0.15=1.0 ✓

# 查询索引
_bin_idx: dict[tuple[str, str], list[tuple[str, float]]] = {}
for lhs, b, c, p in BINARY:
    _bin_idx.setdefault((b, c), []).append((lhs, p))
_un_idx: dict[str, list[tuple[str, float]]] = {}
for lhs, child, p in UNARY:
    _un_idx.setdefault(child, []).append((lhs, p))


# ============================================================
# 2. 概率 CKY（保留所有解析树）
# ============================================================
# 树格式:
#   ("leaf", word)
#   ("unary", cat, child_tree)
#   ("bin", cat, left_tree, right_tree, split_k)
# chart[i][j] = list of (category, log_prob, tree)

def _unary_closure(entries: list) -> list:
    """对 entries 施加单元规则（单层即可，文法无长链）。"""
    result = list(entries)
    for cat, lp, tree in entries:
        for parent, prob in _un_idx.get(cat, []):
            result.append((parent, lp + math.log(prob), ("unary", parent, tree)))
    return result


def cky_parse(words: list[str]) -> list[tuple[str, float, tuple]]:
    """返回所有以 S 为根、覆盖全句的 (cat, log_prob, tree)。"""
    n = len(words)
    chart: list[list[list]] = [[[] for _ in range(n)] for _ in range(n)]

    # 对角线: 词法 + 单元闭包
    for i in range(n):
        for cat, prob in LEXICAL.get(words[i], []):
            chart[i][i].append((cat, math.log(prob), ("leaf", words[i])))
        chart[i][i] = _unary_closure(chart[i][i])

    # 自底向上
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            entries = []
            for k in range(i, j):
                for (cl, pl, tl) in chart[i][k]:
                    for (cr, pr, tr) in chart[k + 1][j]:
                        for (parent, prob) in _bin_idx.get((cl, cr), []):
                            lp = pl + pr + math.log(prob)
                            entries.append((parent, lp, ("bin", parent, tl, tr, k)))
            entries = _unary_closure(entries)
            # 去重: 同 (cat, tree_sig) 只留 log_prob 最高的
            best: dict = {}
            for cat, lp, tree in entries:
                sig = _tree_sig(tree)
                key = (cat, sig)
                if key not in best or lp > best[key][1]:
                    best[key] = (cat, lp, tree)
            chart[i][j] = list(best.values())

    return [(c, lp, t) for c, lp, t in chart[0][n - 1] if c == "S"]


def _tree_sig(tree) -> str:
    if tree[0] == "leaf":
        return tree[1]
    if tree[0] == "unary":
        return f"({tree[1]}{_tree_sig(tree[2])})"
    return f"({tree[1]}{_tree_sig(tree[2])}{_tree_sig(tree[3])})"


# ============================================================
# 3. 树分析：PP 附着类型 + PP 宾语
# ============================================================
def _node_cat(tree) -> str:
    """获取树节点的句法类别。"""
    if tree[0] == "leaf":
        word = tree[1]
        for cat, _ in LEXICAL.get(word, []):
            return cat
        return "?"
    return tree[1]  # unary / bin 的第二个元素是类别


def extract_pp_attachment(tree) -> str | None:
    """递归查找 PP 附着点，返回 'VP' 或 'NP' 或 None。"""
    if tree[0] == "leaf":
        return None
    if tree[0] == "unary":
        return extract_pp_attachment(tree[2])
    # binary: ("bin", cat, left, right, k)
    cat = tree[1]
    left, right = tree[2], tree[3]
    if cat == "VP" and _node_cat(left) == "VP" and _node_cat(right) == "PP":
        return "VP"
    if cat == "NP" and _node_cat(left) == "NP" and _node_cat(right) == "PP":
        return "NP"
    # 递归子树
    r = extract_pp_attachment(left)
    if r:
        return r
    return extract_pp_attachment(right)


def get_pp_object(words: list[str]) -> str | None:
    """获取 PP 的宾语名词（简化版：句子最后一个名词）。"""
    for w in reversed(words):
        if any(c == "N" for c, _ in LEXICAL.get(w, [])):
            return w
    return None


# ============================================================
# 4. 词法化重排序器
# ============================================================
# PP 宾语名词 → 偏好的附着类型
# 直觉来源: Hindle & Rooth (1991) PP 附着统计
#   工具/器皿(fork, telescope) → 倾向 VP 附着（动作的方式/工具）
#   食材/配料(olives, cheese)  → 倾向 NP 附着（名词的修饰语）
PP_OBJECT_PREF: dict[str, str] = {
    "fork":      "VP",
    "spoon":     "VP",
    "telescope": "VP",
    "olives":    "NP",
    "cheese":    "NP",
}


def rerank_log_bonus(attach: str | None, pp_obj: str | None) -> float:
    """词法化特征的对数分数。匹配=bonus, 不匹配=penalty。"""
    if attach is None or pp_obj is None:
        return 0.0
    preferred = PP_OBJECT_PREF.get(pp_obj)
    if preferred is None:
        return 0.0
    return math.log(0.9) if attach == preferred else math.log(0.1)


# ============================================================
# 5. 实验主函数
# ============================================================
def run_experiment(sentence: str, alpha: float = 3.0):
    words = sentence.lower().split()
    parses = cky_parse(words)
    pp_obj = get_pp_object(words)

    print(f"\n  句子: \"{sentence}\"")
    print(f"  PP 宾语: '{pp_obj}'  |  偏好附着: {PP_OBJECT_PREF.get(pp_obj, '?')}")
    print(f"  有效解析树数: {len(parses)}\n")

    if not parses:
        print("    [无法解析]")
        return None, None

    # PCFG 排序
    pcfg_sorted = sorted(parses, key=lambda x: x[1], reverse=True)

    # 词法化重排序
    rerank_sorted = sorted(
        parses,
        key=lambda x: x[1] + alpha * rerank_log_bonus(
            extract_pp_attachment(x[2]), pp_obj),
        reverse=True,
    )

    for rank, (cat, lp, tree) in enumerate(pcfg_sorted[:4]):
        attach = extract_pp_attachment(tree) or "无PP"
        bonus = rerank_log_bonus(attach, pp_obj)
        total = lp + alpha * bonus
        print(f"    PCFG #{rank+1}: log_p={lp:+.4f}  PP→{attach:3s}"
              f"  rerank_bonus={alpha*bonus:+.2f}  total={total:+.4f}")

    best_pcfg = pcfg_sorted[0]
    best_rerank = rerank_sorted[0]
    a1 = extract_pp_attachment(best_pcfg[2]) or "无PP"
    a2 = extract_pp_attachment(best_rerank[2]) or "无PP"

    print(f"\n    PCFG 选择:     PP → {a1}")
    print(f"    词法化重排后:  PP → {a2}")
    if a1 != a2:
        print(f"    ⚡ 词法化翻转了排名！")
    else:
        print(f"    ✓ 两者一致")
    return a1, a2


# ============================================================
# 6. 运行实验
# ============================================================
print("=" * 66)
print(" 实验：PCFG vs 词法化重排序 —— PP 附着歧义")
print("=" * 66)

print("\n--- 句子 1: 'I eat pizza with fork' ---")
print("  人类判断: PP 挂 VP（用叉子吃）")
run_experiment("I eat pizza with fork")

print("\n--- 句子 2: 'I eat pizza with olives' ---")
print("  人类判断: PP 挂 NP（带橄榄的披萨）")
run_experiment("I eat pizza with olives")

print("\n--- 句子 3: 'I saw the man with telescope' ---")
print("  人类判断: PP 挂 VP（用望远镜看）")
run_experiment("I saw the man with telescope")


# ============================================================
# 7. 关键对比：PCFG 对两个句子给出相同概率
# ============================================================
print("\n\n" + "=" * 66)
print(" 关键对比：PCFG 不看词 → 两句概率完全相同")
print("=" * 66)

for label, sent in [("fork", "I eat pizza with fork"),
                     ("olives", "I eat pizza with olives")]:
    words = sent.lower().split()
    trees = cky_parse(words)
    vp_lp = np_lp = None
    for cat, lp, tree in trees:
        attach = extract_pp_attachment(tree)
        if attach == "VP" and vp_lp is None:
            vp_lp = lp
        elif attach == "NP" and np_lp is None:
            np_lp = lp
    print(f"\n  ...with {label}:")
    if vp_lp is not None:
        print(f"    VP 附着 log_p = {vp_lp:+.4f}")
    if np_lp is not None:
        print(f"    NP 附着 log_p = {np_lp:+.4f}")

print(f"""
  → 仅替换 fork→olives，PCFG 概率完全不变！
    因为 V→fork 和 V→olives 的概率都是 1.0，
    规则 P(VP→VP PP) 和 P(NP→NP PP) 不含词信息。
    PCFG 认为 "用叉子吃" 和 "带橄榄的披萨" 一样可能。

  ★ 词法化重排序只用了一个 PP 宾语偏好特征，
    就正确区分了这两个完全不同的语义！
    fork=工具→VP | olives=食材→NP
""")


# ============================================================
# 8. 总结
# ============================================================
print("=" * 66)
print(" 总结")
print("=" * 66)
print("""
  ① PCFG 的核心缺陷：规则概率不含词 → PP 附着无法消歧
     "eat pizza with fork" 和 "eat pizza with olives" 概率相同
     PCFG 对两句都选 VP 附着（因为 P(VP→VP PP)=0.35 较高）

  ② 反直觉：加一个极简的 PP 宾语偏好特征就够了
     fork=工具→VP 附着（用叉子吃）✓
     olives=食材→NP 附着（带橄榄的披萨）✓
     不需要复杂模型，一个词法特征就包含足够信号

  ③ 这就是 Collins/Charniak 词法化 PCFG 的核心：
     把规则概率 P(A→BC) 变成 P(A→BC | head_word)
     WSJ F1 从 ~73% 跃升到 ~88%

  ④ 重排序 (reranking) 的思想：
     先用 PCFG 出 top-k 候选，再用判别特征重排
     → 后来发展成 neural parser 的标准范式
""")
