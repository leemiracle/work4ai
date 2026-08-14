#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 02 · 词与 token · 编辑距离
experiments/02_edit_distance.py

自包含、几秒跑完。只依赖标准库 + NumPy（NumPy 仅用于展示 DP 矩阵）。
打印结论性数字：
  - SLP 经典 intention→execution：标准(sub=1)=5  vs  SLP版(sub=2)=8
  - 对称性：dist(a,b)==dist(b,a) 恒成立（断言验证）
  - 归一化破坏直觉：原始距离相同(=1)，归一化后 0.25 vs 0.5；按 source 长度归一化则不对称
  - 中文 char-level vs 英文 word-level：同一算法，不同粒度
  - 拼写纠正失败模式：Levenshtein 把 recieve→relieve(错)，Damerau 才救回 receive
"""

import random
import numpy as np


# ============================================================================
# 1. 标准编辑距离（Levenshtein），替换代价可调
# ============================================================================
def levenshtein(a, b, sub_cost=1):
    """a, b 可以是 str 也可以是 list（词级时传 list[str]）。返回距离。"""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else sub_cost
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # 删除
                dp[i][j - 1] + 1,        # 插入
                dp[i - 1][j - 1] + cost,  # 替换/匹配
            )
    return dp[m][n]


# ============================================================================
# 2. 带回溯指针：重建编辑路径 + SLP 风格 DP 表可视化
# ============================================================================
def levenshtein_trace(a, b, sub_cost=1):
    """返回 (距离, 操作列表)。操作: ('=',x,y)匹配 ('S',x,y)替换 ('D',x,'.')删除 ('I','.',y)插入"""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    ptr = [[None] * (n + 1) for _ in range(m + 1)]  # 'D'对角 'U'上(删) 'L'左(插)
    for i in range(1, m + 1):
        dp[i][0] = i
        ptr[i][0] = 'U'
    for j in range(1, n + 1):
        dp[0][j] = j
        ptr[0][j] = 'L'
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else sub_cost
            cands = [
                (dp[i - 1][j - 1] + cost, 'D'),
                (dp[i - 1][j] + 1, 'U'),
                (dp[i][j - 1] + 1, 'L'),
            ]
            dp[i][j], ptr[i][j] = min(cands, key=lambda x: x[0])
    # 回溯
    ops = []
    i, j = m, n
    while i > 0 or j > 0:
        p = ptr[i][j]
        if p == 'D':
            op = ('=', a[i - 1], b[j - 1]) if a[i - 1] == b[j - 1] else ('S', a[i - 1], b[j - 1])
            ops.append(op)
            i -= 1; j -= 1
        elif p == 'U':
            ops.append(('D', a[i - 1], '.'))  # 删除 a 的字符
            i -= 1
        else:
            ops.append(('I', '.', b[j - 1]))  # 插入 b 的字符
            j -= 1
    ops.reverse()
    return dp[m][n], ops


def print_alignment(a, b, sub_cost=1):
    d, ops = levenshtein_trace(a, b, sub_cost)
    top = ''.join(str(o[1]) for o in ops)
    mid = ''.join({'=': '|', 'S': '*', 'D': 'D', 'I': 'I'}[o[0]] for o in ops)
    bot = ''.join(str(o[2]) for o in ops)
    return d, top, mid, bot


def print_dp_table(a, b, sub_cost=1):
    """SLP 教科书风格的 DP 表：行=a（含首列标签），列=b（含首行标签）。"""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else sub_cost
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    arr = np.array(dp)
    col_labels = ['#'] + list(b)
    row_labels = ['#'] + list(a)
    print(f"  DP 表 (sub_cost={sub_cost})   行=source '{a}'   列=target '{b}'")
    print("    " + " ".join(f"{c:>3}" for c in col_labels))
    for r, rl in enumerate(row_labels):
        cells = " ".join(f"{arr[r, c]:>3}" for c in range(n + 1))
        print(f"  {rl:>2} {cells}")
    print(f"  >>> 右下角 D[{m},{n}] = {arr[m, n]}")
    return int(arr[m, n])


# ============================================================================
# 3. Damerau-Levenshtein：多一个"相邻交换"操作（代价 1）
# ============================================================================
def damerau_levenshtein(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)  # 相邻交换
    return dp[m][n]


# ============================================================================
# 4. 归一化
# ============================================================================
def norm_by_max(d, a, b):
    return d / max(len(a), len(b)) if max(len(a), len(b)) else 0.0

def norm_by_sum(d, a, b):
    return d / (len(a) + len(b)) if (len(a) + len(b)) else 0.0

def norm_by_source(d, a, b):
    return d / len(a) if len(a) else 0.0


# ============================================================================
# 5. 拼写纠正 demo
# ============================================================================
def spell_correct(query, dictionary, dist_fn, topk=5):
    scored = [(dist_fn(query, w), w) for w in dictionary]
    scored.sort(key=lambda x: (x[0], x[1]))
    return scored[:topk]


# ============================================================================
def banner(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def main():
    random.seed(0)

    banner("发现 1：'编辑距离'不是一个数 —— 代价表变了，答案就变")
    s, t = "intention", "execution"
    d_std = levenshtein(s, t, sub_cost=1)
    d_slp = levenshtein(s, t, sub_cost=2)
    print(f'  "{s}" -> "{t}"')
    print(f"  标准 Levenshtein (sub_cost=1) = {d_std}")
    print(f"  SLP3 版          (sub_cost=2) = {d_slp}   ← 教科书经典值")
    print("  >>> 同一对词，距离差了 60%。查文献要先问清代价表。")
    print_dp_table(s, t, sub_cost=2)

    banner("发现 2：对称性 —— dist(a,b)==dist(b,a) 恒成立（断言验证）")
    alpha = "abcde"
    ok = True
    n_tests = 2000
    for _ in range(n_tests):
        la, lb = random.randint(0, 8), random.randint(0, 8)
        a = "".join(random.choice(alpha) for _ in range(la))
        b = "".join(random.choice(alpha) for _ in range(lb))
        if levenshtein(a, b) != levenshtein(b, a):
            ok = False
            print(f"  ✗ 反例: dist({a!r},{b!r}) != dist({b!r},{a!r})")
            break
    print(f"  随机测试 {n_tests} 对字符串（含空串），对称性：{'✓ 恒成立' if ok else '✗ 被打破'}")
    print("  >>> 数学上 Levenshtein 是真·度量（非负、对称、三角不等式成立）。")

    banner("发现 3：归一化破坏直觉（最重要、最容易踩坑）")
    pairs = [("abc", "xabc"), ("a", "xa")]
    print("  原始距离相同(=1)，但'感觉'完全不同：")
    print(f"  {'pair':<18}{'dist':>6}{'norm/max':>10}{'norm/sum':>10}")
    for a, b in pairs:
        d = levenshtein(a, b)
        print(f"  {a!r:>9} {b!r:<8}{d:>6}{norm_by_max(d,a,b):>10.2f}{norm_by_sum(d,a,b):>10.2f}")
    print("\n  按三种分母归一化 (abc,xabc)：")
    a, b = "abc", "xabc"
    d = levenshtein(a, b)
    print(f"    dist/max(a,b)        = {d}/{max(len(a),len(b))} = {norm_by_max(d,a,b):.3f}   (对称)")
    print(f"    dist/(len(a)+len(b)) = {d}/{len(a)+len(b)} = {norm_by_sum(d,a,b):.3f}   (对称)")
    print(f"    dist/len(source=a)   = {d}/{len(a)} = {norm_by_source(d,a,b):.3f}   ← source 视角")
    print(f"    dist/len(source=b)   = {d}/{len(b)} = {norm_by_source(d,b,a):.3f}   ← 反方向")
    print("  >>> 按源串长度归一化：1/3 != 1/4，变成不对称的'方向性错误率'！")

    banner("发现 4：中文 char-level vs 英文 word-level —— 同一算法，不同粒度")
    en_a = "I love natural language processing".split()
    en_b = "I love natural language".split()
    d_en = levenshtein(en_a, en_b)
    print(f'  英文词级: {en_a}')
    print(f'           {en_b}')
    print(f'           词级编辑距离 = {d_en}  (删掉 "processing")')
    zh_raw = "我喜欢自然语言处理"
    print(f'\n  中文原句: "{zh_raw}"')
    print(f'           "{zh_raw}".split() = {zh_raw.split()}   ← 1 个"词"！毫无用处')
    print(f'           按字切 list("{zh_raw}") = {list(zh_raw)}   ← 这才是处理单元')
    zh_a = list("我喜欢自然语言处理")
    zh_b = list("我喜欢自然语言")
    d_zh = levenshtein(zh_a, zh_b)
    print(f'  中文 char-level: {" ".join(zh_a)}')
    print(f'                  {" ".join(zh_b)}')
    print(f'                  字符级编辑距离 = {d_zh}  (删掉 "处" "理")')
    print("  >>> 算法完全一样，只是把 list 元素从'英文词'换成'汉字'。")

    banner("发现 5：拼写纠正的失败模式 —— 为什么光有编辑距离不够")
    query = "recieve"
    dictionary = ["receive", "relieve", "retrieve", "recipe", "receipt",
                  "recent", "believe", "achieve", "recede", "receptive"]
    print(f'  查询: "{query}"   词典: {dictionary}\n')
    print("  【标准 Levenshtein】（替换=1，无交换操作）")
    for d, w in spell_correct(query, dictionary, lambda x, y: levenshtein(x, y, 1)):
        print(f"    d={d}  {w}")
    print('  >>> Top-1 = "relieve"(d=1)，把 "recieve" 纠正成 "relieve" —— 错的！')
    print('       "receive"（正确答案）被排到 d=2，因为 ie↔ei 是两次替换。\n')
    print("  【Damerau-Levenshtein】（加'相邻交换'=1）")
    for d, w in spell_correct(query, dictionary, damerau_levenshtein):
        print(f"    d={d}  {w}")
    print('  >>> "receive" 降到 d=1（一次相邻交换），进入 Top-1 梯队。')
    print('       但 "relieve" 也是 d=1 —— 仍然平手，光靠距离分不出胜负！')
    print("\n  结论：纯编辑距离做拼写纠正必然失败，因为：")
    print("    (a) 不懂'交换'这种高频键盘错误 → 用 Damerau 部分缓解；")
    print("    (b) 不懂'哪个词更常见' → 需要 N-gram 语言模型先验 P(word)。")
    print("  >>> 这正是 SLP3 Ch3（N-gram LM）+ Appendix D（噪声信道）的存在理由：")
    print("       正确的纠正 = argmax_w P(w) · P(error | w)，第一项就是'词频'。")

    banner("彩蛋：编辑路径可视化（SLP 风格对齐图）")
    for a, b in [("cat", "cats"), ("function", "faction"), ("abc", "xabc")]:
        d, top, mid, bot = print_alignment(a, b)
        print(f'\n  "{a}" -> "{b}"   distance = {d}')
        print(f"    {top}")
        print(f"    {mid}     (=匹配  *替换  D删除  I插入)")
        print(f"    {bot}")

    print("\n" + "=" * 72)
    print("  全部跑完。核心铁证数字：")
    print(f"    intention→execution : 标准={d_std}, SLP={d_slp}")
    print(f"    对称性              : {'✓' if ok else '✗'} (2000 随机测试)")
    print("    归一化不对称        : dist/len(src) 1/3 ≠ 1/4")
    print("    拼写纠正            : Levenshtein 选错(relieve), Damerau 才含 receive")
    print("=" * 72)


if __name__ == "__main__":
    main()
