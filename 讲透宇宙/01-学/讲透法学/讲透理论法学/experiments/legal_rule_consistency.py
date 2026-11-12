# -*- coding: utf-8 -*-
"""
legal_rule_consistency.py — 法条命题逻辑一致性检查器

对应章:04-理论法学转代码(走廊①:命题一致性——"算得准"档)
      /03-可构造与结构(§刚性结构:不矛盾是合法性底线,富勒八原则之五)
      /02-语言特征(§一:法条的"要件→效果"假言结构即蕴含式)
GB/T 82010 理论法学 · 家族层实验(纯标准库,assert 自验证)

做什么:把示例法条(交通 3 条 + 合同 3 条)命题化为真值约束,
穷举全部赋值,检测四件事:
  1) 一致性    —— 规则+事实的合取是否可满足(有没有模型)
  2) 直接冲突  —— 规则对:同时点火而效果互斥(给出情形 witness)
  3) 最小冲突核 —— 哪几条规则/事实顶牛(不可满足的最小子集)
  4) 蕴含与漏洞 —— 系统 ⊨ 查询?不蕴含 = 规范漏洞(给出反例模型)

法理学现场(实验专门演示):
  · 命题化必有隐性建模决策:不补"红绿不同时亮"的领域约束,
    检查器会报出物理上不可能的假冲突(场景 A)
  · 冲突是"情形相对"的:规则集自身可满足 ≠ 无冲突,
    冲突在具体事实加入时才显形(场景 B/C)
  · 不一致前提可推出一切(ex falso):所以蕴含查询必须先过一致性门(场景 B)
  · 但书的形式效果:把两条规则的"同时点火"直接剪掉(场景 A×B 对照)

运行:python legal_rule_consistency.py   (全部 assert 通过即 exit 0)
"""

from itertools import combinations, product


# ---------- 1. 命题表示:公式 = 嵌套 tuple ----------
# ("var", 名) / ("not", f) / ("and", f, g) / ("or", f, g) / ("implies", f, g)

def v(name):
    return ("var", name)

def NOT(f):
    return ("not", f)

def AND(*fs):
    out = fs[0]
    for f in fs[1:]:
        out = ("and", out, f)
    return out

def OR(f, g):
    return ("or", f, g)

def IMP(f, g):
    return ("implies", f, g)


def vars_of(f, acc=None):
    if acc is None:
        acc = set()
    if f[0] == "var":
        acc.add(f[1])
    elif f[0] == "not":
        vars_of(f[1], acc)
    else:
        vars_of(f[1], acc)
        vars_of(f[2], acc)
    return acc


def eval_f(f, a):
    kind = f[0]
    if kind == "var":
        return a[f[1]]
    if kind == "not":
        return not eval_f(f[1], a)
    if kind == "and":
        return eval_f(f[1], a) and eval_f(f[2], a)
    if kind == "or":
        return eval_f(f[1], a) or eval_f(f[2], a)
    if kind == "implies":
        return (not eval_f(f[1], a)) or eval_f(f[2], a)
    raise ValueError("未知公式节点: %r" % (f,))


# ---------- 2. 穷举与可满足性(命题逻辑可判定:2^n 赋值全查) ----------

def models(formulas):
    """逐个产出满足全部公式的赋值(字典)。"""
    vs = sorted(set().union(*[vars_of(f) for f in formulas])) if formulas else []
    for bits in product([False, True], repeat=len(vs)):
        a = dict(zip(vs, bits))
        if all(eval_f(f, a) for f in formulas):
            yield a

def satisfiable(formulas):
    """返回一个模型(字典);不可满足返回 None。"""
    for m in models(formulas):
        return m
    return None


# ---------- 3. 蕴含式规则 + 直接冲突 ----------

class Rule:
    """法条命题化:名字 + 前件(要件)+ 后件(法律效果)。"""
    def __init__(self, name, ante, cons):
        self.name, self.ante, self.cons = name, ante, cons
    def formula(self):
        return IMP(self.ante, self.cons)
    def __repr__(self):
        return self.name


def direct_conflict(r1, r2, background=()):
    """直接冲突 = 存在(满足背景约束的)情形使两规则同时点火,
    而两个效果不可能同时成立。
    返回点火情形(witness 赋值)或 None。
    注意:背景约束是命题化时的隐性建模决策——缺了它,
    检查器可能报出物理上不可能的假冲突(见场景 A)。"""
    trigger = satisfiable(list(background) + [r1.ante, r2.ante])
    if trigger is None:
        return None                      # 永不同时点火(但书的形式效果)
    coexist = satisfiable(list(background) + [r1.ante, r2.ante,
                                              r1.cons, r2.cons])
    if coexist is not None:
        return None                      # 效果可以并存
    return trigger                       # 同时点火且效果互斥:冲突情形


# ---------- 4. 一致性 + 最小冲突核 ----------

def consistent(rules, facts=()):
    return satisfiable([r.formula() for r in rules] + list(facts)) is not None


def minimal_core(rules, facts=()):
    """不可满足的最小子集(标签形式返回:哪几条规则/事实顶牛)。"""
    items = [("规则:" + r.name, r.formula()) for r in rules]
    items += [("事实:" + _fact_label(f), f) for f in facts]
    for size in range(1, len(items) + 1):
        for sub in combinations(items, size):
            if satisfiable([f for _, f in sub]) is None:
                return [label for label, _ in sub]
    return []  # 整体可满足:无冲突核

def _fact_label(f):
    if f[0] == "var":
        return f[1] + "=真"
    if f[0] == "not" and f[1][0] == "var":
        return f[1][1] + "=假"
    return "复合事实"


# ---------- 5. 蕴含 / 漏洞 ----------

def entails(rules, facts, query):
    """rules+facts ⊨ query 当且仅当 rules+facts+¬query 不可满足。
    注意:前提本身不一致时,任何 query 都'被蕴含'(ex falso)。"""
    return satisfiable([r.formula() for r in rules] + list(facts)
                       + [NOT(query)]) is None


# =====================================================================
# 场景 A:交通条款(含例外)—— 一致 + 漏洞检出 + 但书修复
# =====================================================================

R_A1 = Rule("A1 红灯禁行(执行紧急任务的车辆除外)",
            AND(v("red"), NOT(v("emergency"))), NOT(v("pass")))
R_A2 = Rule("A2 绿灯放行", v("green"), v("pass"))
R_A3 = Rule("A3 执行紧急任务的车辆不受红灯限制",
            v("emergency"), v("pass"))
RULES_A = [R_A1, R_A2, R_A3]
BG_A = [IMP(v("red"), NOT(v("green")))]   # 领域约束:红绿不同时亮

def scenario_a():
    print("== 场景 A:交通条款(带但书)==")
    m = satisfiable([r.formula() for r in RULES_A])
    assert m is not None, "场景 A 应当一致"
    print("  一致 OK  模型示例:", {k: int(m[k]) for k in sorted(m)})

    # 教学点:不补领域约束 → 物理不可能情形的假冲突
    fake = direct_conflict(R_A1, R_A2)          # 无背景约束
    assert fake is not None, "缺领域约束时应报假冲突(红绿同亮)"
    print("  缺领域约束:报出假冲突(红绿同亮)——命题化必有隐性建模决策!")
    for r1, r2 in combinations(RULES_A, 2):
        assert direct_conflict(r1, r2, BG_A) is None, "补领域约束后应无冲突"
    print("  补'红绿互斥'背景约束后:两两直接冲突:无 OK")

    # 教学点:但书的形式效果 = 剪掉同时点火
    assert satisfiable([R_A1.ante, R_A3.ante]) is None, "但书剪掉同时点火"
    print("  但书的形式效果:R_A1 与 R_A3 永不同时点火 OK")

    # 漏洞查询:通行是否必须(绿灯 或 紧急任务)?
    q = IMP(v("pass"), OR(v("green"), v("emergency")))
    assert entails(RULES_A, [], q) is False, "无 R4 时应存在漏洞"
    counter = satisfiable([r.formula() for r in RULES_A] + [NOT(q)])
    print("  漏洞检出 OK  反例情形(通行却既非绿灯也非紧急):",
          {k: int(counter[k]) for k in sorted(counter)})
    r4 = Rule("A4 机动车通行以绿灯或紧急任务为前提",
              v("pass"), OR(v("green"), v("emergency")))
    assert entails(RULES_A + [r4], [], q) is True, "补 R4 后漏洞应闭合"
    print("  加前提规则 R4 后漏洞闭合 OK")


# =====================================================================
# 场景 B:交通条款(删掉例外)—— 冲突在情形加入时显形 + ex falso
# =====================================================================

R_B1 = Rule("B1 红灯一律禁行(无例外)", v("red"), NOT(v("pass")))
RULES_B = [R_B1, R_A3]                    # B1 + A3(紧急车辆可通行)
FACTS_B = [v("red"), v("emergency")]      # 情形:红灯 + 执行紧急任务

def scenario_b():
    print("== 场景 B:删掉但书,情形 = 红灯 AND 紧急任务 ==")
    assert consistent(RULES_B) is True, "规则集自身仍可满足(冲突潜伏)"
    print("  规则集自身:可满足 OK(冲突尚未显形)")
    assert consistent(RULES_B, FACTS_B) is False, "情形加入后应检出冲突"
    print("  加入事实后:不一致 OK —— 规范冲突是'情形相对'的")

    w = direct_conflict(R_B1, R_A3, BG_A)
    assert w is not None, "B1 与 A3 应构成直接冲突"
    print("  直接冲突 OK  B1×A3 点火情形:", {k: int(w[k]) for k in sorted(w)})

    core = minimal_core(RULES_B, FACTS_B)
    assert len(core) == 4 and any("B1" in c for c in core), "最小冲突核"
    print("  最小冲突核(4 条,缺一不可):", core)

    # 不一致前提推出一切:正反两个相反结论同时'被蕴含'
    assert entails(RULES_B, FACTS_B, v("pass")) is True
    assert entails(RULES_B, FACTS_B, NOT(v("pass"))) is True
    print("  ex falso OK  冲突前提下既蕴含'可通行'又蕴含'不可通行'",
          "—— 蕴含查询必须先过一致性门")


# =====================================================================
# 场景 C:合同条款 —— 无辜者不在冲突核里(最小核的定位价值)
# =====================================================================

C1 = Rule("C1 未按约交付构成违约", NOT(v("deliver")), v("breach"))
C2 = Rule("C2 违约经通知,守约方可解除合同",
          AND(v("breach"), v("notice")), v("terminate"))
C3 = Rule("C3 解除合同须经事先通知", v("terminate"), v("notice"))
C3B = Rule("C3' 解除合同无须通知", v("terminate"), NOT(v("notice")))
FACTS_C = [v("breach"), v("notice")]

def scenario_c():
    print("== 场景 C:合同条款(解约通知之争)==")
    assert consistent([C1, C2, C3]) is True
    assert entails([C1, C2, C3], FACTS_C, v("terminate")) is True
    print("  C1+C2+C3:一致 OK 且'应当可解约'被蕴含 OK")

    assert consistent([C1, C2, C3B]) is True, "换 C3' 后规则集自身仍可满足"
    print("  换成 C3'后:规则集自身仍可满足 OK(冲突仍潜伏)")
    assert consistent([C1, C2, C3B], FACTS_C) is False, "情形加入后应冲突"
    print("  情形 = 已违约 AND 已通知:不一致 OK(C2 逼出解约,C3' 又否掉通知)")

    core = minimal_core([C1, C2, C3B], FACTS_C)
    assert len(core) == 4 and not any("C1" in c for c in core), \
        "C1 无辜,不应进最小核"
    print("  最小冲突核:", core, "—— C1(交付条款)无辜,定位价值 OK")


def main():
    scenario_a()
    scenario_b()
    scenario_c()
    print()
    print("全部断言通过:法条命题逻辑一致性检查器自验证成功 (exit 0)")


if __name__ == "__main__":
    main()
