#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 19 章配套实验：Arc-Standard Transition-Based Dependency Parser
===========================================================================
对应文档: 19-依存句法分析.md

只用 Python 标准库。不用任何 NLP 库。

跑这个脚本，你会看到三个「能跑出来」的结论：

  1. Arc-Standard transition-based parser 在【投影】句子上完美工作：
     用「规则 oracle」（知道正确动作）引导，逐步 SHIFT/LEFT-ARC/RIGHT-ARC，
     把 "The cat ate a fish" 和 "猫 吃 了 鱼" 完美解析成依存树。
  2.【★ 反直觉发现】同一个 parser 对【非投影】句子（依存弧交叉）会【卡死】！
     arc-standard 的动作集【数学上无法表示】非投影树——
     因为它只能通过栈顶两个元素建立弧，一旦头部被弹出栈就再也连不上。
  3. 可视化：用 ASCII 画出依存树，并自动检测投影性。

自包含，几秒跑完：
    python3 -u experiments/19_dep_parser.py
"""

import sys
from collections import defaultdict

# ── 常量 ──
LEFT_ARC  = "LEFT-ARC"
RIGHT_ARC = "RIGHT-ARC"
SHIFT     = "SHIFT"
ROOT      = 0


def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 1. Arc-Standard Parser（栈 + 缓冲区 + 动作）
# ============================================================
class ArcStandardParser:
    """
    Arc-Standard 状态机（Nivre 2004）。

    状态 = (stack, buffer, arcs)
      stack : 词索引列表，底部恒为 ROOT(0)
      buffer: 剩余词索引（从左到右）
      arcs  : 已建立的弧 [(head, dep, label), ...]

    动作（只看栈顶两个元素 s0/s1）:
      LEFT-ARC(l)  : s0(栈顶) 是 s1(次栈顶) 的 head → 建 s0→s1，弹出 s1
      RIGHT-ARC(l) : s1(次栈顶) 是 s0(栈顶) 的 head → 建 s1→s0，弹出 s0
      SHIFT        : 把 buffer[0] 压入栈
    """

    def __init__(self, n_words):
        self.stack = [ROOT]
        self.buffer = list(range(1, n_words + 1))
        self.arcs = []

    def left_arc(self, label):
        """s0(栈顶) 是 s1(次栈顶) 的 head；弹出 s1。"""
        s0, s1 = self.stack[-1], self.stack[-2]
        self.arcs.append((s0, s1, label))
        self.stack.pop(-2)

    def right_arc(self, label):
        """s1(次栈顶) 是 s0(栈顶) 的 head；弹出 s0。"""
        s0, s1 = self.stack[-1], self.stack[-2]
        self.arcs.append((s1, s0, label))
        self.stack.pop()

    def shift(self):
        self.stack.append(self.buffer.pop(0))

    def is_terminal(self):
        return len(self.buffer) == 0 and len(self.stack) == 1


# ============================================================
# 2. 规则 Oracle（知道正确动作）
# ============================================================
def make_oracle(gold_heads):
    """
    gold_heads: {word_index: head_index}，ROOT(0) 无条目。
    返回 oracle 函数：给定 (stack, buffer) → 返回正确动作（或 None=卡死/完成）。

    判定规则（arc-standard）:
      • LEFT-ARC : s0 是 s1 的 gold head          → 可以（s1≠ROOT）
      • RIGHT-ARC: s1 是 s0 的 gold head          → 可以，但须确认
                   s0 在 buffer 中没有未处理的 child（否则过早弹出会丢 child）
      • SHIFT    : 其他情况且 buffer 非空
    """
    def oracle(stack, buffer):
        if len(stack) >= 2:
            s0 = stack[-1]
            s1 = stack[-2]

            # LEFT-ARC: s0 是 s1 的正确 head（且 s1 ≠ ROOT）
            if s1 != ROOT and gold_heads.get(s1) == s0:
                return LEFT_ARC

            # RIGHT-ARC: s1 是 s0 的正确 head
            if gold_heads.get(s0) == s1:
                s0_has_remaining_kids = any(
                    gold_heads.get(w) == s0 for w in buffer
                )
                if not s0_has_remaining_kids:
                    return RIGHT_ARC

        if buffer:
            return SHIFT

        return None   # 没动作可做（可能完成，也可能卡死）

    return oracle


# ============================================================
# 3. 解析（带逐步输出）
# ============================================================
def parse(words, gold_heads, gold_labels, title=""):
    """用 oracle 引导解析，返回 (parser, success)。"""
    n = len(words)
    parser = ArcStandardParser(n)
    oracle = make_oracle(gold_heads)

    def w(i):
        return "ROOT" if i == ROOT else words[i - 1]

    if title:
        P(f"\n{'━' * 64}")
        P(f"  {title}")
        P(f"  句子: {' '.join(words)}")
        P(f"{'━' * 64}")

    step = 0
    success = True
    while True:
        action = oracle(parser.stack, parser.buffer)

        if action is None:
            if parser.is_terminal():
                P(f"\n  >>> 解析完成（{step} 步）")
            else:
                P(f"\n  >>> ⚠ 卡死！栈={parser.stack}  缓冲区={parser.buffer}")
                success = False
            break

        step += 1
        if action == LEFT_ARC:
            s0, s1 = parser.stack[-1], parser.stack[-2]
            lbl = gold_labels.get(s1, "dep")
            parser.left_arc(lbl)
            P(f"  {step:>2}. LEFT-ARC ({lbl:<8}) : "
              f"{w(s0)}({s0}) → head of → {w(s1)}({s1})")
        elif action == RIGHT_ARC:
            s0, s1 = parser.stack[-1], parser.stack[-2]
            lbl = gold_labels.get(s0, "dep")
            parser.right_arc(lbl)
            P(f"  {step:>2}. RIGHT-ARC({lbl:<8}) : "
              f"{w(s1)}({s1}) → head of → {w(s0)}({s0})")
        elif action == SHIFT:
            parser.shift()
            pushed = parser.stack[-1]
            P(f"  {step:>2}. SHIFT          : push {w(pushed)}({pushed})")

    return parser, success


# ============================================================
# 4. 可视化 & 投影性检测
# ============================================================
def print_tree(words, arcs):
    """打印缩进式依存树。"""
    children = defaultdict(list)
    for h, d, l in arcs:
        children[h].append((d, l))
    for k in children:
        children[k].sort()

    def w(i):
        return "ROOT" if i == ROOT else f"{words[i - 1]}"

    def show(node, prefix, is_last, label=""):
        connector = "└─ " if is_last else "├─ "
        lab = f"  [{label}]" if label and node != ROOT else ""
        P(f"  {prefix}{connector}{w(node)}{lab}")
        kids = children.get(node, [])
        for i, (dep, lbl) in enumerate(kids):
            ext = "   " if is_last else "│  "
            show(dep, prefix + ext, i == len(kids) - 1, lbl)

    P()
    roots = children.get(ROOT, [])
    if not roots:
        P("  (空树——ROOT 没有孩子)")
        return
    for i, (dep, lbl) in enumerate(roots):
        show(dep, "", i == len(roots) - 1, lbl)


def check_projective(gold_heads):
    """
    判断依存树是否投影。

    投影定义：对每条弧 (head→dep)，head 和 dep 之间的所有词 w
    必须是 head 的后代（即从 head 出发沿依存树可达 w）。

    返回 (is_projective: bool, bad_arc or None)
    """
    children = defaultdict(set)
    for dep, head in gold_heads.items():
        children[head].add(dep)

    def descendants(node):
        seen, stack = {node}, [node]
        while stack:
            cur = stack.pop()
            for c in children.get(cur, set()):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        return seen

    for dep, head in gold_heads.items():
        lo, hi = sorted((head, dep))
        desc = descendants(head)
        for k in range(lo + 1, hi):
            if k != dep and k not in desc:
                return False, (head, dep, k)
    return True, None


def compute_uas(gold_heads, arcs):
    """
    UAS (Unlabeled Attachment Score)
      = 正确找到 head 的词数 / 总词数。
    """
    predicted = {d: h for h, d, _ in arcs}
    correct = sum(1 for w, h in gold_heads.items()
                  if predicted.get(w) == h)
    return correct, len(gold_heads)


# ============================================================
# 5. 例子
# ============================================================

# ── 例 1：英文投影句 ──
# "The cat ate a fish" — 经典 SVO，弧不交叉
#   The(1)→cat(2):det   cat(2)→ate(3):nsubj   ate(3)→ROOT
#   a(4)→fish(5):det    fish(5)→ate(3):obj
EX1_WORDS  = ["The", "cat", "ate", "a", "fish"]
EX1_HEADS  = {1: 2, 2: 3, 3: 0, 4: 5, 5: 3}
EX1_LABELS = {1: "det", 2: "nsubj", 3: "root", 4: "det", 5: "obj"}

# ── 例 2：中文投影句 ──
# "猫 吃 了 鱼" — SVO + 体貌助词"了"
#   猫(1)→吃(2):nsubj   吃(2)→ROOT   了(3)→吃(2):aux   鱼(4)→吃(2):obj
EX2_WORDS  = ["猫", "吃", "了", "鱼"]
EX2_HEADS  = {1: 2, 2: 0, 3: 2, 4: 2}
EX2_LABELS = {1: "nsubj", 2: "root", 3: "aux", 4: "obj"}

# ── 例 3：非投影句（4 词，弧交叉）──
# 这是荷兰语/德语 verb-raising 结构的抽象：
#   w₁ w₂ w₃ w₄
#   弧：w₃(3)→w₁(1), w₁(1)→w₂(2), ROOT→w₃(3), w₁(1)→w₄(4)
#   弧 w₁→w₄ 跨越 w₃，而 w₃ 不是 w₁ 的后代 → 非投影
EX3_WORDS  = ["w₁", "w₂", "w₃", "w₄"]
EX3_HEADS  = {1: 3, 2: 1, 3: 0, 4: 1}
EX3_LABELS = {1: "dep", 2: "dep", 3: "root", 4: "dep"}


# ============================================================
# 6. 主函数
# ============================================================
def main():
    P("╔" + "═" * 62 + "╗")
    P("║  讲透NLP · 第 19 章 · Arc-Standard 依存句法分析器          ║")
    P("╚" + "═" * 62 + "╝")

    # ──────────────────────────────────────────────
    # 例 1：英文投影句
    # ──────────────────────────────────────────────
    proj, _ = check_projective(EX1_HEADS)
    P(f"\n{'─'*64}")
    P(f"  投影性检测: {'投影 ✓ — arc-standard 可以处理' if proj else '非投影 ✗'}")
    P(f"{'─'*64}")

    parser1, ok1 = parse(EX1_WORDS, EX1_HEADS, EX1_LABELS,
                         "例 1 · 英文投影句（The cat ate a fish）")
    P("\n  依存树:")
    print_tree(EX1_WORDS, parser1.arcs)
    c1, t1 = compute_uas(EX1_HEADS, parser1.arcs)
    P(f"\n  UAS = {c1}/{t1} = {c1/t1:.0%}")

    # ──────────────────────────────────────────────
    # 例 2：中文投影句
    # ──────────────────────────────────────────────
    proj2, _ = check_projective(EX2_HEADS)
    parser2, ok2 = parse(EX2_WORDS, EX2_HEADS, EX2_LABELS,
                         "例 2 · 中文投影句（猫 吃 了 鱼）")
    P("\n  依存树:")
    print_tree(EX2_WORDS, parser2.arcs)
    c2, t2 = compute_uas(EX2_HEADS, parser2.arcs)
    P(f"\n  UAS = {c2}/{t2} = {c2/t2:.0%}")

    # ──────────────────────────────────────────────
    # ★ 例 3：非投影句（卡死！）
    # ──────────────────────────────────────────────
    P(f"\n{'━' * 64}")
    P(f"  ★ 例 3 · 非投影句（弧交叉——arc-standard 会卡死）")
    P(f"  句子: {' '.join(EX3_WORDS)}  (模拟荷兰语 verb-raising)")
    P(f"{'━' * 64}")

    proj3, bad_arc = check_projective(EX3_HEADS)
    if not proj3:
        h, d, k = bad_arc
        P(f"\n  投影性检测: 非投影 ✗")
        P(f"    弧 {EX3_WORDS[h-1]}({h}) → {EX3_WORDS[d-1]}({d})")
        P(f"    跨越了词 {EX3_WORDS[k-1]}({k})，"
          f"但 {EX3_WORDS[k-1]}({k}) 不是 {EX3_WORDS[h-1]}({h}) 的后代")

    P(f"\n  正确依存树 (gold):")
    for dep in sorted(EX3_HEADS):
        head = EX3_HEADS[dep]
        hw = "ROOT" if head == 0 else EX3_WORDS[head-1]
        P(f"    {EX3_WORDS[dep-1]}({dep}) → head = {hw}({head})")

    P(f"\n  逐弧检查交叉:")
    for dep in sorted(EX3_HEADS):
        head = EX3_HEADS[dep]
        lo, hi = sorted((head, dep))
        between = [EX3_WORDS[k-1] for k in range(lo+1, hi)]
        cross = "✗ 交叉!" if not proj3 and (head,dep,k)==bad_arc else "✓"
        P(f"    {EX3_WORDS[head-1] if head else 'ROOT'}({head})→{EX3_WORDS[dep-1]}({dep})"
          f"  中间={between or '∅'}  {cross}")

    P(f"\n  让 arc-standard parser 尝试解析:")
    parser3, ok3 = parse(EX3_WORDS, EX3_HEADS, EX3_LABELS)

    P(f"\n  产出的（不完整）依存树:")
    print_tree(EX3_WORDS, parser3.arcs)

    c3, t3 = compute_uas(EX3_HEADS, parser3.arcs)
    P(f"\n  UAS = {c3}/{t3} = {c3/t3:.0%}  ← 词 w₄(4) 没有被分配 head！")

    P(f"\n  {'─' * 60}")
    P(f"  ★ 为什么卡死？逐因分析：")
    P(f"  {'─' * 60}")
    P(f"    1. w₄(4) 的正确 head 是 w₁(1)")
    P(f"    2. 但 w₁(1) 在 Step 5 的 LEFT-ARC 中已被弹出栈")
    P(f"       （当 w₃(3) 入栈后，oracle 判定 w₃ 是 w₁ 的 head，")
    P(f"        于是建立 w₃→w₁ 并弹出 w₁）")
    P(f"    3. arc-standard 只能在【栈顶两个元素之间】建弧")
    P(f"    4. w₁ 已不在栈上 → w₄ 永远找不到正确 head → 卡死")
    P(f"\n    核心矛盾：非投影弧 w₁→w₄ 要求")
    P(f"    「先建 w₁→w₄，再建 w₃→w₁」，")
    P(f"    但 arc-standard 的栈操作要求")
    P(f"    「先处理 w₁ 和 w₂、w₃ 的关系，才能接触 w₄」——")
    P(f"    这两个顺序互斥。")

    # ──────────────────────────────────────────────
    # 总结表
    # ──────────────────────────────────────────────
    P(f"\n{'━' * 64}")
    P(f"  总结")
    P(f"{'━' * 64}")
    P(f"  {'句子':<24} {'投影?':^8} {'arc-standard':^16} {'UAS':^8}")
    P(f"  {'─'*24} {'─'*8} {'─'*16} {'─'*8}")
    P(f"  {'The cat ate a fish':<24} {'✓':^8} {'✅ 完美':^16} {'100%':^8}")
    P(f"  {'猫 吃 了 鱼':<24} {'✓':^8} {'✅ 完美':^16} {'100%':^8}")
    P(f"  {'w₁ w₂ w₃ w₄ (交叉)':<24} {'✗':^8} {'❌ 卡死':^16} {'75%':^8}")
    P(f"")
    P(f"  核心洞察：")
    P(f"    transition-based parser 是线性时间 O(n) 的，极快；")
    P(f"    但代价是【只能产生投影树】——这是数学定理，不是 bug。")
    P(f"    对非投影句子，需要：")
    P(f"      (a) arc-eager + SWAP 动作 (Nivre 2009)")
    P(f"      (b) graph-based MST 解码 (Chu-Liu-Edmonds)")
    P(f"      (c) pseudo-projective 转换 + 后处理修复")


if __name__ == "__main__":
    main()
