# -*- coding: utf-8 -*-
"""三段论有效性判定器:256 式穷举 × 周延规则 × 小论域语义对拍(00 章核心实验)。

理论现场:
  · 亚里士多德《前分析篇》立三段论(4 格 × 4³ 式 = 256 个候补);
    中世纪给 19 式起拉丁名,传统逻辑数出 24/256 有效(含 9 个弱化式)
  · 有效性 = 没有反例(真值保持):规则判定(语法侧)与论域穷举(语义侧)必须对拍——
    "一个论证有效"就是"不可能前提真而结论假",这个"不可能"可以被小论域暴力拍实
  · 存在预设(existential import):全称命题预设主项非空吗?
    传统读法=三个词项的外延一律非空(全域预设)→ 24 式有效;
    现代读法=允许空类(Boole 以后)→ 只剩 15 式。
    9 个弱化式的命运押在一个空类上——这是传统逻辑与现代逻辑的分水岭,
    也是本家族(哲学侧)与数学宇宙数理逻辑家族(数学侧)的分家现场。

跑法: python3 -u experiments/00_syllogism.py
依赖: 纯标准库
"""

from itertools import combinations, product

# ---------- 类型表:A 全称肯定 / E 全称否定 / I 特称肯定 / O 特称否定 ----------
# dist_subj/dist_pred: 词项在该位置是否周延(distributed);
# negative/particular: 品质(肯定/否定)与量(全称/特称)
PROP = {
    "A": dict(dist_subj=True,  dist_pred=False, negative=False, particular=False),
    "E": dict(dist_subj=True,  dist_pred=True,  negative=True,  particular=False),
    "I": dict(dist_subj=False, dist_pred=False, negative=False, particular=True),
    "O": dict(dist_subj=False, dist_pred=True,  negative=True,  particular=True),
}

# 四个格的词项排布:(大前提主,大前提谓,小前提主,小前提谓);结论恒为 S-P
# S=小项(结论主项) P=大项(结论谓项) M=中项
FIGURE = {
    1: ("M", "P", "S", "M"),  # 中项作大前提主项、小前提谓项
    2: ("P", "M", "S", "M"),  # 中项两度作谓项
    3: ("M", "P", "M", "S"),  # 中项两度作主项
    4: ("P", "M", "M", "S"),  # 中项作大前提谓项、小前提主项
}

# 传统的 24 个有效式(拉丁名;带 * 的 9 个弱化式依赖"词项非空"预设,见实验 3)
VALID24 = {
    ("AAA", 1): "Barbara", ("EAE", 1): "Celarent", ("AII", 1): "Darii", ("EIO", 1): "Ferio",
    ("AAI", 1): "Barbari*", ("EAO", 1): "Celaront*",
    ("EAE", 2): "Cesare", ("AEE", 2): "Camestres", ("EIO", 2): "Festino", ("AOO", 2): "Baroco",
    ("EAO", 2): "Cesaro*", ("AEO", 2): "Camestrop*",
    ("AAI", 3): "Darapti*", ("IAI", 3): "Disamis", ("AII", 3): "Datisi",
    ("EAO", 3): "Felapton*", ("OAO", 3): "Bocardo", ("EIO", 3): "Ferison",
    ("AAI", 4): "Bramantip*", ("AEE", 4): "Camenes", ("IAI", 4): "Dimaris",
    ("EAO", 4): "Fesapo*", ("EIO", 4): "Fresison", ("AEO", 4): "Camenop*",
}


# ---------- 判定器一:词项规则(语法侧,中世纪课堂的机械化) ----------

def rule_verdict(mood, figure):
    """五条周延规则判定三段论。返回 (是否有效, 违规清单)。

    R1 中项至少周延一次;R2 结论中周延的词项在前提中必须周延;
    R3 两否定前提无结论;R4 结论否定 iff 恰有一否定前提;R5 特称前提→特称结论。
    """
    major, minor, concl = mood
    ms, mp, ss, sm = FIGURE[figure]  # 大前提主/谓,小前提主/谓

    def dist(ptype, pos):
        return PROP[ptype]["dist_subj"] if pos == "subj" else PROP[ptype]["dist_pred"]

    d = {
        # 中项在两个前提中的周延性(看它各占主/谓哪个位置)
        ("M", "major"): dist(major, "subj" if ms == "M" else "pred"),
        ("M", "minor"): dist(minor, "subj" if ss == "M" else "pred"),
        # 大项 P 在大前提、小项 S 在小前提中的周延性
        ("P", "major"): dist(major, "subj" if ms == "P" else "pred"),
        ("S", "minor"): dist(minor, "subj" if ss == "S" else "pred"),
        # 结论两端
        ("S", "concl"): PROP[concl]["dist_subj"],
        ("P", "concl"): PROP[concl]["dist_pred"],
    }
    faults = []
    if not (d[("M", "major")] or d[("M", "minor")]):
        faults.append("R1 中项不周延(中项两次都不当主语,连接失效)")
    if d[("S", "concl")] and not d[("S", "minor")]:
        faults.append("R2 小项扩大周延(S 在前提里不周延,结论里却周延)")
    if d[("P", "concl")] and not d[("P", "major")]:
        faults.append("R2 大项扩大周延(P 在前提里不周延,结论里却周延)")
    neg_prem = PROP[major]["negative"] + PROP[minor]["negative"]
    if neg_prem == 2:
        faults.append("R3 两否定前提(两个'不是'接不起一条'是')")
    elif PROP[concl]["negative"] != (neg_prem == 1):
        faults.append("R4 否定前提与结论品质不匹配")
    if (PROP[major]["particular"] or PROP[minor]["particular"]) and not PROP[concl]["particular"]:
        faults.append("R5 特称前提推出全称结论(弱前提背不动强结论)")
    return (not faults), faults


# ---------- 判定器二:论域穷举(语义侧,"没有反例"的直接实现) ----------

UNIVERSE = (0, 1, 2)
SUBSETS = [frozenset(c) for r in range(len(UNIVERSE) + 1)
           for c in combinations(UNIVERSE, r)]


def prop_true(ptype, x, y):
    """外延语义。A:x⊆y;E:x∩y=∅;I:x∩y≠∅;O:x⊄y。"""
    if ptype == "A":
        return x <= y
    if ptype == "E":
        return not (x & y)
    if ptype == "I":
        return bool(x & y)
    return bool(x - y)  # "O"


def semantic_verdict(mood, figure, existential_import=True):
    """穷举 S/M/P 的全部外延组合(3 元论域各 8 种,共 8³ 组):
    存在"前提真而结论假"的组合即无效。
    existential_import=True(传统读法):反例必须满足全域预设——S/M/P 外延皆非空;
    False(现代读法):允许空类,"所有 S 是 P"在 S 空时空洞地为真。"""
    ms, mp, ss, sm = FIGURE[figure]
    premises = ((ms, mp, mood[0]), (ss, sm, mood[1]))
    for ext in product(SUBSETS, repeat=3):
        env = dict(zip("SMP", ext))
        if existential_import and not all(env[t] for t in "SMP"):
            continue  # 传统预设:词项指称的类非空,空类组合不入反例候选
        if (all(prop_true(t, env[a], env[b]) for a, b, t in premises)
                and not prop_true(mood[2], env["S"], env["P"])):
            return False
    return True


def counterexample(mood, figure):
    """无效式的现场取证:给出一个"前提真而结论假"的外延组合;有效式返回 None。"""
    ms, mp, ss, sm = FIGURE[figure]
    premises = ((ms, mp, mood[0]), (ss, sm, mood[1]))
    for ext in product(SUBSETS, repeat=3):
        env = dict(zip("SMP", ext))
        if (all(prop_true(t, env[a], env[b]) for a, b, t in premises)
                and not prop_true(mood[2], env["S"], env["P"])):
            return env
    return None


# ---------- 论证检查器:从真实论证到格与式 ----------

def classify(major, minor, concl):
    """三个命题各写 (主项标签, 谓项标签, 类型),标签取 'S'/'P'/'M'。返回 (mood, figure)。"""
    key = (major[0], major[1], minor[0], minor[1])
    figure = next(f for f, k in FIGURE.items() if k == key)
    return (major[2], minor[2], concl[2]), figure


def main():
    print("=" * 64)
    print("实验 1 · 256 式穷举:规则判定 vs 论域穷举 vs 传统 24 式 三方对拍")
    print("=" * 64)
    by_rules, by_sem = set(), set()
    for figure in FIGURE:
        for mood in map("".join, product("AEIO", repeat=3)):
            if rule_verdict(mood, figure)[0]:
                by_rules.add((mood, figure))
            if semantic_verdict(mood, figure, existential_import=True):
                by_sem.add((mood, figure))
    assert by_rules == by_sem == set(VALID24), "三方判定不一致!"
    for fig in (1, 2, 3, 4):
        names = sorted(v for (m, f), v in VALID24.items() if f == fig)
        print(f"  第{fig}格 {sum(1 for (_, f) in VALID24 if f == fig)} 式: {' '.join(names)}")
    print(f"  规则判定 = 语义穷举 = 教科书答案:{len(VALID24)}/256 ✓")
    print("  (语法侧五条规则与语义侧'没有反例'在 256 式上逐式一致——可靠性与完备性的袖珍版)")

    # 知名单点断言(历史锚)
    assert rule_verdict("AAA", 1)[0] and VALID24[("AAA", 1)] == "Barbara"
    assert rule_verdict("EAE", 1)[0] and VALID24[("EAE", 1)] == "Celarent"
    assert not rule_verdict("AAA", 2)[0]          # 中项两不周延,经典无效式
    assert not rule_verdict("AAA", 3)[0]          # 小项扩大周延
    assert rule_verdict("AOO", 2)[0]              # Baroco
    assert rule_verdict("OAO", 3)[0]              # Bocardo
    print("  单点断言:AAA-1/EAE-1/AOO-2/OAO-3 有效,AAA-2/AAA-3 无效 ✓")

    print()
    print("=" * 64)
    print("实验 2 · 论证检查器:三个中文论证的现场")
    print("=" * 64)
    demos = [
        ("Barbara(有效)", [("M", "P", "A"), ("S", "M", "A"), ("S", "P", "A")],
         ("所有哺乳动物是恒温动物;所有鲸是哺乳动物 ⇒ 所有鲸是恒温动物",)),
        ("Darapti(有效,弱化式)", [("M", "P", "A"), ("M", "S", "A"), ("S", "P", "I")],
         ("所有鸟是动物;所有鸟是生物 ⇒ 有生物是动物",)),
        ("AAA-3(无效,经典翻车式)", [("M", "P", "A"), ("M", "S", "A"), ("S", "P", "A")],
         ("所有金属是导体;所有金属是元素 ⇒ 所有元素是导体",)),
    ]
    for title, props, (text,) in demos:
        mood, figure = classify(*props)
        ok, faults = rule_verdict(mood, figure)
        mood = "".join(mood)
        name = VALID24.get((mood, figure), "无专名")
        print(f"  [{title}] 判为 {mood}-{figure}({name}):{'有效' if ok else '无效'}")
        print(f"    {text}")
        if not ok:
            ce = counterexample(mood, figure)
            print(f"    违规:{faults[0]}")
            print(f"    反例:S={sorted(ce['S'])} M={sorted(ce['M'])} P={sorted(ce['P'])}"
                  f"(论域 0/1/2)——'前提真而结论假'的活体,无效性的定义式取证")
    assert rule_verdict(*classify(("M", "P", "A"), ("S", "M", "A"), ("S", "P", "A")))[0]
    assert not rule_verdict(*classify(("M", "P", "A"), ("M", "S", "A"), ("S", "P", "A")))[0]
    print("  三个断言通过 ✓")

    print()
    print("=" * 64)
    print("实验 3 · 存在预设的开关:允许空类之后,有效式从 24 掉到 15")
    print("=" * 64)
    modern = {(m, f) for m, f in VALID24
              if semantic_verdict(m, f, existential_import=False)}
    weakened = set(VALID24) - modern
    print(f"  传统读法(词项一律非空):{len(VALID24)}/256 有效")
    print(f"  现代读法(允许空类):{len(modern)}/256 有效")
    print(f"  为空类殉葬的 {len(weakened)} 个弱化式:")
    for (m, f) in sorted(weakened, key=lambda x: (x[1], x[0])):
        print(f"    {VALID24[(m, f)]:12s} {m}-{f}")
    assert len(modern) == 15 and len(weakened) == 9
    assert all(v.endswith("*") for (m, f), v in VALID24.items() if (m, f) in weakened)
    print("  断言通过:被空类杀死的恰是 9 个带 * 的弱化式 ✓")
    print()
    print("读数:")
    print("  · '所有 S 都是 P' 在 S 为空时说什么?——传统逻辑预设 S 存在,")
    print("    现代逻辑答'空洞地真'。一念之差,九个式子出局:三段论的有效式清单")
    print("    不是永恒真理,而是一项语义决策的函数(00 章 §5、04 章走廊 0 的现场)")
    print("  · 规则判定(语法)与穷举判定(语义)各自自洽且互相印证——")
    print("    '有效性=没有反例'这个定义,本脚本用 20 行把它变成了可运行的东西")


if __name__ == "__main__":
    main()
