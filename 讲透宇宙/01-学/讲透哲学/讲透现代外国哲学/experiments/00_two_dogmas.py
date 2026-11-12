# -*- coding: utf-8 -*-
"""分析-综合边界模拟:蒯因《经验论的两个教条》的计算重演(家族 04 章 · 走廊 B)。

理论现场:
  · 「分析真理(凭意义为真)vs 综合真理(凭事实为真)」是逻辑实证主义的地基缝
  · 蒯因 1951:这条缝靠「同义性」定义,同义性靠「保全真值的可替换性」,
    可替换性又预设「分析性」——循环(第一教条)
  · 第二教条:信念之网整体面对经验边界;预测失败时修哪条信念无算法规定

本脚本在一个人工语义网络里把两个教条做成四个可跑演示:
  §1 循环定义检测(定义图上的环——03 章「定义图里的环是 bug」)
  §2 「同义性」的不可判定:网络内部没有任何测试能把「定义性联结」与「经验性联结」分开
     (可替换性测试 vs 定义展开测试给出相反判决)
  §3 分析/综合身份翻转:同一句子,在两种语言约定下,一枚分析、一枚综合
  §4 信念之网的整体论修补:同一冲突,修定义/修归类都能恢复一致(第二教条)

跑法: python3 -u experiments/00_two_dogmas.py
依赖: 纯标准库
"""

from itertools import product

HR = "-" * 62


# ---------- §1 循环定义检测(定义图上的环) ----------

# 人工词典:词项 -> 定义它的词项集合。
# 原始词(adult/male/female 等)没有定义条目——它们是「约定地」到底的地板。
LEXICON_CIRC = {
    "bachelor":  {"unmarried", "adult", "male"},   # 学院派方言:清晰定义
    "spinster":  {"unmarried", "adult", "female"},
    "unmarried": {"unpaired"},                     # 词典学方言:用近义词互相定义
    "unpaired":  {"single"},
    "single":    {"unmarried"},                    # 环:unmarried → unpaired → single → unmarried
}


def definition_cycles(graph):
    """定义图上的环检测(DFS 三色标记)。返回环列表,每环首尾同点。"""
    color = {t: 0 for t in graph}          # 0=白 1=灰 2=黑
    cycles, stack = [], []

    def dfs(node):
        color[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if color.get(nxt, 0) == 0:
                dfs(nxt)
            elif color.get(nxt, 0) == 1:   # 回边 → 环
                i = stack.index(nxt)
                cycles.append(stack[i:] + [nxt])
        stack.pop()
        color[node] = 2

    for term in sorted(graph):
        if color[term] == 0:
            dfs(term)
    return cycles


def reachable_terms(term, graph):
    """从 term 出发沿定义边可达的全部词项(BFS)。"""
    seen, frontier = {term}, [term]
    while frontier:
        nxt = []
        for t in frontier:
            for dep in graph.get(t, ()):
                if dep not in seen:
                    seen.add(dep)
                    nxt.append(dep)
        frontier = nxt
    return seen


def section1():
    print(HR)
    print("§1 循环定义检测:定义图上的环是 bug")
    print(HR)
    cycles = definition_cycles(LEXICON_CIRC)
    for c in cycles:
        print("  检出环: " + " -> ".join(c))
    cyclic_terms = {t for c in cycles for t in c[:-1]}

    # 断言:恰好检出那三个人为构造的循环簇成员,未污染其他词
    assert cyclic_terms == {"unmarried", "unpaired", "single"}, cyclic_terms
    assert "bachelor" not in cyclic_terms and "spinster" not in cyclic_terms

    # bachelor 的定义展开:悬在原始词 + 一个循环簇上
    reach = reachable_terms("bachelor", LEXICON_CIRC)
    primitives = sorted(t for t in reach if t not in LEXICON_CIRC)
    print(f"  bachelor 可达词项: {sorted(reach)}")
    print(f"  展开到底的地板(原始词,无定义条目): {primitives}")
    print(f"  地板之外还悬着循环簇: {sorted(cyclic_terms & reach)}")
    print("  → 定义链的底部是【约定的原始词】,不是被【发现】的语义原子;")
    print("    词典学方言则干脆在环里打转——同义性的权威来自约定,不来自网络内部。\n")
    return cyclic_terms


# ---------- §2 「同义性」的不可判定(可替换性测不出意义) ----------

# 世界样本库:若干可能世界,每个世界给出一组一元谓词的外延。
# 动了手脚:有心脏(heart)与有肾脏(kidney)在所有抽样世界里外延恒同
# ——蒯因的反例:「与心同物」和「与肾同物」共延却显然不同义。
DOMAIN = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "heidi"]

WORLDS = []
for i, extra in enumerate([[], ["bob"], ["bob", "carol"], ["alice", "grace"]]):
    heart = set(DOMAIN) - set(extra)                 # 有心脏的
    kidney = set(heart)                              # ← 人为令两谓词处处共延
    WORLDS.append({
        "w%d" % i: {
            "heart": heart,
            "kidney": kidney,
            "bitesNails": {"alice", "dave", "grace"},  # 对照组:普通经验谓词
        }
    })

# 「定义侧」记录(谁与谁在词典里共享定义 unfold 出的同簇)
DEFINITIONAL_CLUSTERS = [
    {"heart", "blood-pump-organ"},      # heart 的词典义经 blood-pump-organ
    {"kidney", "urine-filter-organ"},   # kidney 的词典义经 urine-filter-organ
    {"bitesNails", "nervous-habit"},    # 对照谓词的词典义
]


def substitution_test(p, q, worlds):
    """可替换性测试:在所有抽样世界的所有真句中,把 p 换成 q 是否保全真值。"""
    for w in worlds:
        ext = next(iter(w.values()))
        if ext[p] != ext[q]:            # 任一世界外延不同 → 不可替换
            return False
    return True


def definitional_cluster_of(term):
    for cluster in DEFINITIONAL_CLUSTERS:
        if term in cluster:
            return cluster
    return {term}


def section2():
    print(HR)
    print("§2 同义性的不可判定:两个测试,相反判决")
    print(HR)

    # 测试 A:保全真值的可替换性(外延标准)
    sub_heart_kidney = substitution_test("heart", "kidney", WORLDS)
    sub_heart_nails = substitution_test("heart", "bitesNails", WORLDS)
    print(f"  [测试A 可替换性] heart ≡ kidney ? {sub_heart_kidney}")
    print(f"  [测试A 可替换性] heart ≡ bitesNails ? {sub_heart_nails}")

    # 测试 B:定义展开(词典标准)
    same_cluster = definitional_cluster_of("heart") & definitional_cluster_of("kidney")
    print(f"  [测试B 定义展开] heart 与 kidney 共享词典簇 ? {bool(same_cluster)}")

    assert sub_heart_kidney is True                     # 外延测试说「同义」
    assert same_cluster == set()                        # 词典测试说「不同义」
    assert sub_heart_nails is False                     # 对照组:外延不同,测试A才说不同

    print("  → 冲突:可替换性只看见外延(共延即判同义),看不见意义;")
    print("    而词典权威本身来自约定。蒯因第一教条的现场:")
    print("    网络内部不存在把「定义性联结」与「经验性联结」分开的中立测试。\n")


# ---------- §3 分析/综合身份翻转(同一句子,两种约定) ----------

# 目标句 S:「所有 bachelor 都未婚」
# 约定 A(学院派方言 L1):词典规定 bachelor := unmarried ∧ adult ∧ male
# 约定 B(岛屿方言 L2):bachelor 是原始谓词(习惯用法:适婚成年男性,
#                     不问婚否)——只由世界样本给外延
PEOPLE = [
    {"name": "john", "unmarried": False, "adult": True,  "male": True},
    {"name": "paul", "unmarried": True,  "adult": True,  "male": True},
    {"name": "rita", "unmarried": True,  "adult": True,  "male": False},
]

ISLAND_WORLD = {  # L2 方言的一个可能世界:bachelor 的外延由习惯给出,含已婚者
    "bachelor": {"john", "paul"},       # john 已婚但在岛屿方言里是 bachelor
    "unmarried": {"paul", "rita"},
}


def bachelor_L1(p):                      # 约定 A:bachelor 由定义生成
    return p["unmarried"] and p["adult"] and p["male"]


def section3():
    print(HR)
    print("§3 分析/综合身份翻转:同一句子的两种命运")
    print(HR)
    S = "所有 bachelor 都未婚 (All bachelors are unmarried)"

    # 约定 A:枚举全部未婚/成年/男性赋值组合,S 不可能为假 → 分析
    keys = ("unmarried", "adult", "male")
    combos = product([True, False], repeat=3)
    holds = all(
        not bachelor_L1(dict(zip(keys, c))) or dict(zip(keys, c))["unmarried"]
        for c in combos
    )
    assert holds is True
    status_A = "analytic(分析:否定它=违反词典)"
    print(f"  约定A(词典方言 L1):{S}\n    → {status_A}")

    # 约定 B:存在一致的可能世界使 S 为假 → 综合
    counter = [n for n in ISLAND_WORLD["bachelor"] if n not in ISLAND_WORLD["unmarried"]]
    assert counter == ["john"]
    status_B = "synthetic(综合:反例世界一致,其否定不矛盾)"
    print(f"  约定B(岛屿方言 L2):反例世界 {ISLAND_WORLD} 存在已婚 bachelor={counter}\n    → {status_B}")

    print("  → 同一个句子,分析性是【语言约定的函数】,不是世界自身的事实;")
    print("    卡尔纳普能造『L-内真』靠的是显式语义规则(约定),")
    print("    而第一教条要的『无约定的边界』——本演示找不到。\n")


# ---------- §4 信念之网的整体论修补(第二教条) ----------

# 观察冲突:教堂记录说 john 已婚(F2),人口登记说 john 是 bachelor(F1),
# 词典说 bachelor→未婚(D1),民法说 已婚→非未婚(D2)。四条一起必然翻车。
# 命题骨架:B=bachelor(john)  U=unmarried(john)  M=married(john)
CLAUSES = {
    "D1: 词典 bachelor→未婚":   lambda B, U, M: (not B) or U,
    "D2: 民法 已婚→非未婚":      lambda B, U, M: (not M) or (not U),
    "F1: 登记 bachelor(john)":  lambda B, U, M: B,
    "F2: 教堂 married(john)":   lambda B, U, M: M,
}


def consistent(clauses):
    """暴力枚举真值指派,检查子句集是否可同时满足。"""
    return any(all(c(B, U, M) for c in clauses.values())
               for B, U, M in product([False, True], repeat=3))


def section4():
    print(HR)
    print("§4 信念之网的整体论修补:修哪条都行,无算法规定")
    print(HR)
    assert consistent(CLAUSES) is False
    print("  冲突: {" + "; ".join(CLAUSES) + "}")
    print("  → 整体不一致(必然推出 U 与 ¬U)。\n")

    repairs = {}
    for drop in CLAUSES:                       # 逐条撤销,看哪些单点修补奏效
        rest = {k: v for k, v in CLAUSES.items() if k != drop}
        repairs[drop] = consistent(rest)
    for drop, ok in sorted(repairs.items()):
        mark = "恢复一致" if ok else "仍冲突"
        print(f"    撤销 [{drop}] → {mark}")

    # 断言:至少两种「性质不同」的单点修补都成立(修事实 F1 / 修定义 D1)
    assert repairs["F1: 登记 bachelor(john)"] is True
    assert repairs["D1: 词典 bachelor→未婚"] is True
    print("\n  → 撤销 F1=『john 不算 bachelor』(修归类/修事实);")
    print("    撤销 D1=『bachelor 不定义为未婚』(修定义/修词典)。")
    print("    两条路都恢复一致——经验判决落在网的【整体】上,")
    print("    没有任何算法规定该修哪一条。蒯因:")
    print("    『任何陈述都可以在任何情况下被持有为真,只要在别处做出足够剧烈的调整。』\n")


def main():
    print("分析-综合边界模拟 —— 蒯因《经验论的两个教条》计算重演")
    print("家族:讲透现代外国哲学 · 04 章 走廊 B · 纯标准库\n")
    section1()
    section2()
    section3()
    section4()
    print(HR)
    print("全部断言通过。结论:分析-综合的缝,在语义网络内部找不到——")
    print("它只能被【约定】画上去;而信念之网面对经验,是整张网一起接招。")


if __name__ == "__main__":
    main()
