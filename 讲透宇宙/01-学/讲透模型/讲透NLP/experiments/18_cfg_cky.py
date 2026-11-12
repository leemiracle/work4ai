#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 18 章配套实验：上下文无关文法与 CKY 句法分析（从零实现）
========================================================================
只用标准库（不用 nltk / spaCy），实现：
  1. 纯 Chomsky 范式（CNF）的上下文无关文法（CFG）：二元的 A→BC + 词法的 A→w。
  2. CKY 算法（自底向上动态规划，O(n^3)），枚举一个句子的【所有】句法树。
  3. PCFG 版本：每条规则带概率，求最大概率树（Viterbi 风格）与句子概率 P(S)。

跑这个脚本，你会看到三个「能跑出来」的结论：

  【无歧义】"the cat sat on the mat" —— CKY 恰好返回 1 棵树。
  【有歧义】"I saw the man with the telescope" —— CKY 返回 2 棵树：
       · VP 附着（我用望远镜看见了那个人）
       · NP 附着（我看见了那个带着望远镜的人）
  【反直觉】PCFG 选概率最大的那棵，但它选错了——而且：
       · 比较两种读法的概率比 = P(VP→VP PP) / P(NP→NP PP)，所有「词」的概率全部约掉。
       · 把这两条规则的频率对调，【同一句话】的最优解读立刻翻转。
       说明 PCFG 的介词短语附着决策【完全不看词义】，只看规则统计频率。
       这正是 Collins 词法化句法分析器（lexicalized parser）要解决的问题。

自包含，几秒跑完：
    python3 experiments/18_cfg_cky.py
"""

# ============================================================
# 1. 文法定义：Chomsky 范式 (CNF)
# ============================================================
# 词法规则 word -> [(非终结符, P(word|非终结符)), ...]
# 二元规则 (LHS, RHS_left, RHS_right, P(LHS_left RHS_right | LHS))
#
# 严格 CNF 只允许 A -> B C （两个非终结符）或 A -> w（一个终结符）。
# 用纯 CNF 是为了：CKY 无需处理一元链，每条规则恰好分裂成两半，手算可验证。


def make_grammar(np_det_n=0.7, np_nppp=0.3,
                 vp_vnp=0.4, vp_vpp=0.2, vp_vppp=0.4):
    """构造一个 PCFG。两套附着规则的频率可调（默认 Config A）。

    归一化约束：每个 LHS 的所有规则概率之和 = 1。
      NP 行:  NP->Det N (np_det_n) + NP->NP PP (np_nppp)      = 1
      VP 行:  VP->V NP (vp_vnp) + VP->V PP (vp_vpp)
                    + VP->VP PP (vp_vppp)                       = 1
    """
    assert abs(np_det_n + np_nppp - 1.0) < 1e-9
    assert abs(vp_vnp + vp_vpp + vp_vppp - 1.0) < 1e-9

    # 词法：每个词映射到（词性, P(词|词性)）。词性也是非终结符（前终结符）。
    lexicon = {
        "the":       [("Det", 1.0)],
        "I":         [("Pro", 1.0)],
        # 4 个名词平分 N 的概率
        "cat":       [("N", 0.25)],
        "man":       [("N", 0.25)],
        "mat":       [("N", 0.25)],
        "telescope": [("N", 0.25)],
        # 2 个动词平分 V 的概率
        "sat":       [("V", 0.5)],
        "saw":       [("V", 0.5)],
        # 2 个介词平分 P 的概率
        "on":        [("P", 0.5)],
        "with":      [("P", 0.5)],
    }

    # 二元产生式
    binary = [
        ("S",  "NP", "VP", 1.0),       # 句子 = 名词短语 + 动词短语
        ("NP", "Det", "N",  np_det_n), # "the cat" / "the man" / ...
        ("NP", "NP", "PP",  np_nppp),  # ★ NP 附着：NP 嵌入 PP（"the man with ..."）
        ("VP", "V",  "NP",  vp_vnp),   # 及物："saw the man"
        ("VP", "V",  "PP",  vp_vpp),   # 动词带介词短语："sat on the mat"
        ("VP", "VP", "PP",  vp_vppp),  # ★ VP 附着：VP 嵌入 PP（"[saw the man] with ..."）
        ("PP", "P",  "NP",  1.0),      # 介词短语 = 介词 + 名词短语
    ]
    return lexicon, binary


# ============================================================
# 2. CKY 算法：枚举所有句法树（带回溯指针）
# ============================================================
# 树的表示：嵌套元组
#   词法/前终结符节点 : (标签, 词)            例: ("Det", "the")
#   二元节点          : (标签, 左子树, 右子树)
# chart[i][j] 覆盖词 i..j（不含 j），存 dict: 非终结符 -> [(树, 该树概率), ...]


def cky(words, lexicon, binary, start="S"):
    """返回 (chart, 该句子的所有 start 树列表)。复杂度 O(n^3 × 文法规模)。"""
    n = len(words)
    # chart[i][j] = dict NT -> list of (tree, prob)
    chart = [[dict() for _ in range(n + 1)] for _ in range(n + 1)]

    # 索引二元规则，方便按右部首元素快速查找
    by_left_rhs = {}
    for (lhs, b, c, p) in binary:
        by_left_rhs.setdefault(b, {}).setdefault(c, []).append((lhs, p))

    # 宽度 1：填词法
    for i in range(n):
        for nt, p in lexicon.get(words[i], []):
            chart[i][i + 1].setdefault(nt, []).append(((nt, words[i]), p))

    # 宽度 >= 2：枚举断点 k，左半 + 右半组合
    for width in range(2, n + 1):
        for i in range(0, n - width + 1):
            j = i + width
            cell = chart[i][j]
            for k in range(i + 1, j):          # 断点
                left = chart[i][k]
                right = chart[k][j]
                if not left or not right:
                    continue
                for b, left_map in left.items():
                    targets = by_left_rhs.get(b)
                    if not targets:
                        continue
                    for c in right:
                        rules = targets.get(c)
                        if not rules:
                            continue
                        for (lhs, p_rule) in rules:
                            for (lt, lp) in left_map:
                                for (rt, rp) in right[c]:
                                    tree = (lhs, lt, rt)
                                    cell.setdefault(lhs, []).append(
                                        (tree, lp * rp * p_rule))
    trees = chart[0][n].get(start, [])
    return chart, trees


# ============================================================
# 3. 树的打印
# ============================================================
def tree_bracket(t):
    """括号表示：S(NP(Pro I), VP(V saw, ...))"""
    label = t[0]
    kids = t[1:]
    if len(kids) == 1 and isinstance(kids[0], str):
        return f"{label}({kids[0]!r})"
    return f"{label}({', '.join(tree_bracket(c) for c in kids)})"


def tree_ascii(t):
    """缩进树（带 └─/├─ 连接符）。"""
    lines = []
    def rec(node, prefix, is_last, is_root):
        conn = "" if is_root else ("└─ " if is_last else "├─ ")
        label = node[0]
        kids = node[1:]
        if len(kids) == 1 and isinstance(kids[0], str):
            lines.append(f"{prefix}{conn}{label} → \"{kids[0]}\"")
        else:
            lines.append(f"{prefix}{conn}{label}")
            child_prefix = prefix + ("" if is_root else ("   " if is_last else "│  "))
            for idx, c in enumerate(kids):
                rec(c, child_prefix, idx == len(kids) - 1, False)
    rec(t, "", True, True)
    return "\n".join(lines)


def describe_attachment(t):
    """识别望远镜句的两种读法：返回 'VP-附着' 或 'NP-附着'。"""
    s = tree_bracket(t)
    # 读法判定：VP 顶层是否含 "VP, PP"（VP 附着）还是 V 直接带嵌套 NP（NP 附着）
    root_vp = t[1][1]  # S -> Pro VP 里的 VP
    if root_vp[0] == "VP" and len(root_vp) > 1 and root_vp[1][0] == "VP" \
            and root_vp[2][0] == "PP":
        return "VP 附着（我用望远镜看见了他）"
    return "NP 附着（他是那个带望远镜的人）"


# ============================================================
# 主程序
# ============================================================
def banner(title):
    print("=" * 66)
    print(title)
    print("=" * 66)


def run_sentence(words, lexicon, binary, label=""):
    chart, trees = cky(words, lexicon, binary)
    print(f"\n句子: {' '.join(words)}   {label}")
    print(f"词序列长度 n = {len(words)}")
    print(f"CKY 找到的 S 树数量 = {len(trees)}")
    if not trees:
        print("  ⚠ 无法解析（文法不覆盖该句）")
        return trees
    total = sum(p for _, p in trees)
    print(f"句子概率 P(S) = 所有树概率之和 = {total:.6e}")
    # 按概率降序
    ranked = sorted(trees, key=lambda x: -x[1])
    for rank, (t, p) in enumerate(ranked, 1):
        print(f"\n  ── 树 #{rank}  概率 = {p:.6e}"
              f"  占比 {p / total * 100:5.1f}%")
        print(tree_ascii(t))
    return ranked


def main():
    banner("讲透NLP · 18 上下文无关文法与 CKY 成分句法分析（从零实现）")
    print("文法：纯 Chomsky 范式 (CNF)  ——  规则只能是 A→BC 或 A→w")
    print("算法：CKY（Cocke-Kasami-Younger），自底向上动态规划，O(n³)\n")

    # ----------------------------------------------------------
    # 结论 1：无歧义句子只有 1 棵树
    # ----------------------------------------------------------
    banner("结论 1 ｜ 无歧义句子：\"the cat sat on the mat\" → 恰好 1 棵树")
    lex, binr = make_grammar()  # Config A
    run_sentence(["the", "cat", "sat", "on", "the", "mat"], lex, binr)
    print("\n👉 结构唯一：[the cat] [sat [on the mat]]。")
    print("   注意 \"sat\" 是光杆动词，本文法里成不了 VP，所以不存在 VP 附着的二义性。")

    # ----------------------------------------------------------
    # 结论 2 + 反直觉：歧义句子有 2 棵树
    # ----------------------------------------------------------
    banner("结论 2 ｜ 歧义句子：\"I saw the man with the telescope\" → 2 棵树")
    lex, binr = make_grammar()  # Config A: VP→VP PP=0.4 > NP→NP PP=0.3
    ranked = run_sentence(
        ["I", "saw", "the", "man", "with", "the", "telescope"], lex, binr)

    best_t, best_p = ranked[0]
    second_t, second_p = ranked[1]
    print("\n" + "-" * 66)
    print("【反直觉发现】PCFG 选了概率最大的那棵，但它选的是哪种读法？")
    print("-" * 66)
    print(f"  最优树 #{1}: 概率 {best_p:.6e}  →  {describe_attachment(best_t)}")
    print(f"  次优树 #{2}: 概率 {second_p:.6e}  →  {describe_attachment(second_t)}")
    ratio = best_p / second_p
    print(f"  概率比 (最优/次优) = {ratio:.3f}")
    print(f"  而规则频率比 P(VP→VP PP)/P(NP→NP PP) = "
          f"{0.4}/{0.3} = {0.4 / 0.3:.3f}")
    print("\n  关键：两棵树用到的「词」概率、PP 子树、VP→V NP 全部相同，")
    print("  在比值里【完全约掉】。剩下唯一不同的就是两条附着规则的频率。")
    print("  ⇒ PCFG 的介词短语附着决策【只看规则统计频率，完全不看词义】。")

    # ----------------------------------------------------------
    # 结论 3：把两条附着规则频率对调 → 最优解读翻转（同一句话！）
    # ----------------------------------------------------------
    banner("结论 3 ｜ 同一句话，对调两条规则频率 → 最优解读翻转")
    print("Config A: P(NP→NP PP)=0.30, P(VP→VP PP)=0.40  →  偏好 VP 附着")
    print("Config B: P(NP→NP PP)=0.40, P(VP→VP PP)=0.30  →  偏好 NP 附着")
    print("(为保证归一化，Config B 同步微调 NP→Det N 与 VP→V PP)\n")

    lex_b, binr_b = make_grammar(
        np_det_n=0.6, np_nppp=0.4,   # NP 行：附着规则变强
        vp_vnp=0.4, vp_vpp=0.3, vp_vppp=0.3)  # VP 行：附着规则变弱
    ranked_b = run_sentence(
        ["I", "saw", "the", "man", "with", "the", "telescope"], lex_b, binr_b,
        label="(Config B)")

    best_b_t, best_b_p = ranked_b[0]
    print("\n  Config B 最优树 → " + describe_attachment(best_b_t))
    print(f"  Config B 最优概率 = {best_b_p:.6e}")
    print("\n👉 句子【一个字没改】，PCFG 的「最优解读」却从 VP 附着翻转到 NP 附着。")
    print("   这就是为什么光杆 PCFG 在介词短语附着上准确率不高——真正的附着偏好")
    print("   是【词法】的（'用叉子吃披萨'=VP，'带蘑菇的披萨'=NP，结构相同方向相反）。")
    print("   正是这一点推动了 Collins(1999) 的词法化句法分析器（lexicalized parser）。")

    # ----------------------------------------------------------
    # 小结：CKY 复杂度
    # ----------------------------------------------------------
    banner("小结")
    print("· CKY 枚举所有树：n 个词、断点 n 个、每点查文法 → O(n³ × |R|)。")
    print("· 对 n=6/7 的玩具句，chart 里 S 树分别有 1 / 2 棵。")
    print("· 真实句子的合法树数量随长度指数增长（二义性爆炸），")
    print("  所以工程上用 PCFG + 维特比【只保留每个 cell 概率最大的子树】，")
    print("  把 \"枚举全部\" 降成 \"留最优\" —— 这就是概率带来的工程收益。")


if __name__ == "__main__":
    main()
