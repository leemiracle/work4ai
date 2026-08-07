#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 G 配套实验：CCG 基本算子 + 语义组合演示
=========================================================
纯 Python 标准库，零依赖，几秒跑完。

核心：
  1. 实现范畴语法的前向应用 (>) 和后向应用 (<)
  2. 实现前向组合 (>B)
  3. 同步执行 λ-reduction，演示"句法推导 = 语义合成"

★ 反直觉发现：
  CCG 的范畴归约和 λ-reduction 完全同构——
  每一步句法操作精确对应一步语义函数应用。
  你不需要两套系统：句法树自动产出语义。
  而且类型提升让推导变成严格的从左到右增量处理。

python3 experiments/G_ccg_parser.py
"""
from dataclasses import dataclass
from typing import Optional, Callable


# ============================================================
# 1. 范畴（Category）表示
# ============================================================
# 范畴要么是原子（"S", "NP", "N"），要么是函数 X/Y 或 X\Y
# 用元组表示函数范畴: ("slash", result, arg, direction)
#   direction = "/" (forward, 右找参数) 或 "\" (backward, 左找参数)

@dataclass
class Cat:
    """CCG 范畴。"""
    atomic: Optional[str] = None          # 原子范畴: "S", "NP", "N"
    slash: Optional[str] = None           # "/" 或 "\"
    result: Optional['Cat'] = None        # 函数返回的范畴
    arg: Optional['Cat'] = None           # 函数参数的范畴

    def __repr__(self) -> str:
        if self.atomic:
            return self.atomic
        r, a = repr(self.result), repr(self.arg)
        return f"({r}{self.slash}{a})"

    def __eq__(self, other):
        if not isinstance(other, Cat):
            return False
        if self.atomic and other.atomic:
            return self.atomic == other.atomic
        if self.slash and other.slash:
            return (self.slash == other.slash
                    and self.result == other.result
                    and self.arg == other.arg)
        return False

    def __hash__(self):
        return hash(repr(self))


# 构造器快捷方式
def atom(name: str) -> Cat:
    return Cat(atomic=name)

def fwd(res: Cat, arg: Cat) -> Cat:
    """X/Y: 前向函数，右边找 arg"""
    return Cat(slash="/", result=res, arg=arg)

def bwd(res: Cat, arg: Cat) -> Cat:
    """X\\Y: 后向函数，左边找 arg"""
    return Cat(slash="\\", result=res, arg=arg)


# ============================================================
# 2. 组合算子
# ============================================================

def forward_application(left: Cat, right: Cat) -> Optional[Cat]:
    """规则 >:  X/Y   Y  =>  X
    
    左边的函数吃掉右边的参数，返回结果范畴。
    """
    if left.slash == "/" and left.arg == right:
        return left.result
    return None

def backward_application(left: Cat, right: Cat) -> Optional[Cat]:
    """规则 <:  Y   X\\Y  =>  X
    
    右边的函数从左边吃参数，返回结果范畴。
    """
    if right.slash == "\\" and right.arg == left:
        return right.result
    return None

def forward_composition(left: Cat, right: Cat) -> Optional[Cat]:
    """规则 >B:  X/Y   Y/Z  =>  X/Z
    
    前向组合：两个函数合成一个。
    """
    if (left.slash == "/" and right.slash == "/"
            and left.arg == right.result):
        return fwd(left.result, right.arg)
    return None


# ============================================================
# 3. λ-表达式（语义表示）
# ============================================================
# λ-表达式用 Python lambda 模拟，不做完整类型检查
# 语义用字符串显示

class Sem:
    """简单语义包装器，支持显示和 apply。"""
    def __init__(self, repr_str: str, apply_fn: Callable = None):
        self._repr = repr_str
        self._apply = apply_fn

    def apply(self, arg_sem: 'Sem') -> 'Sem':
        if self._apply:
            return self._apply(arg_sem)
        return Sem(f"{self._repr}({arg_sem._repr})")

    def compose(self, other_sem: 'Sem') -> 'Sem':
        """f∘g = λx.f(g(x))"""
        return Sem(f"({self._repr} ∘ {other_sem._repr})")

    def __repr__(self):
        return self._repr


# ============================================================
# 4. 词条（Lexical Entry）
# ============================================================
@dataclass
class LexEntry:
    word: str
    cat: Cat
    sem: Sem


# 简单词典
def make_lexicon() -> dict[str, list[LexEntry]]:
    S, NP, N = atom("S"), atom("NP"), atom("N")
    
    # serves : (S\NP)/NP : λy.λx.serve(x,y)
    serves_cat = bwd(S, NP)  # S\NP
    serves_cat = fwd(serves_cat, NP)  # (S\NP)/NP
    serves_sem = Sem("λy.λx.serve(x,y)", 
                     lambda y: Sem(f"λx.serve(x,{y})", 
                                   lambda x: Sem(f"serve({x},{y})")))
    
    # loves : (S\NP)/NP : λy.λx.love(x,y)
    loves_cat = fwd(bwd(S, NP), NP)
    loves_sem = Sem("λy.λx.love(x,y)",
                    lambda y: Sem(f"λx.love(x,{y})",
                                  lambda x: Sem(f"love({x},{y})")))

    return {
        "united":  [LexEntry("United", NP, Sem("united"))],
        "miami":   [LexEntry("Miami", NP, Sem("miami"))],
        "romeo":   [LexEntry("Romeo", NP, Sem("romeo"))],
        "juliet":  [LexEntry("Juliet", NP, Sem("juliet"))],
        "serves":  [LexEntry("serves", serves_cat, serves_sem)],
        "loves":   [LexEntry("loves", loves_cat, loves_sem)],
        "the":     [LexEntry("the", fwd(NP, N), Sem("λx.x", lambda x: x))],
        "flight":  [LexEntry("flight", N, Sem("flight"))],
        # 类型提升版本的主语
        # United_T : S/(S\NP) : λf.f(united)
        "united_t": [LexEntry("United↑", fwd(S, bwd(S, NP)),
                              Sem("λf.f(united)", 
                                  lambda f: f.apply(Sem("united")))),
                     LexEntry("United", NP, Sem("united"))],
    }


# ============================================================
# 5. CCG 解析器（二元 CKY + 三种算子）
# ============================================================

def parse_sentence(words: list[str], lexicon: dict) -> list[dict]:
    """
    用 CKY 风格的 bottom-up 解析，尝试所有算子组合。
    返回所有成功推导（以 S 为根覆盖全句）。
    每个推导 = {"cat": Cat, "sem": Sem, "steps": [str], "tree": str}
    """
    n = len(words)
    # chart[i][j] = list of (cat, sem, steps, tree_str)
    chart: list[list[list]] = [[[] for _ in range(n)] for _ in range(n)]

    # 初始化对角线：查词典
    for i in range(n):
        w = words[i].lower()
        entries = lexicon.get(w, [])
        for e in entries:
            chart[i][i].append((e.cat, e.sem, [], repr(e.cat)))

    # 填充 chart（自底向上）
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            cell = []
            for k in range(i, j):
                for (lc, ls, lsteps, ltree) in chart[i][k]:
                    for (rc, rs, rsteps, rtree) in chart[k + 1][j]:
                        # 尝试三种算子
                        for op_name, op_fn, sem_op in [
                            (">", forward_application, 
                             lambda lf, rf: lf.apply(rf)),
                            ("<", backward_application, 
                             lambda lf, rf: rf.apply(lf)),
                            (">B", forward_composition, 
                             lambda lf, rf: lf.compose(rf)),
                        ]:
                            result_cat = op_fn(lc, rc)
                            if result_cat is not None:
                                new_sem = sem_op(ls, rs)
                                step = f"  {ltree:>16s} {op_name:<3s} {rtree:<16s} => {result_cat}"
                                tree_str = repr(result_cat)
                                cell.append((result_cat, new_sem,
                                            lsteps + rsteps + [step],
                                            tree_str))
            chart[i][j].extend(cell)

    # 返回以 S 为根的推导
    S = atom("S")
    results = []
    for (cat, sem, steps, tree) in chart[0][n - 1]:
        if cat == S:
            results.append({"cat": cat, "sem": sem, "steps": steps})
    return results


# ============================================================
# 6. 运行实验
# ============================================================

print("=" * 66)
print(" 实验 G：CCG 基本算子 + 语义组合")
print("=" * 66)

lex = make_lexicon()

# ---- 实验 1: United serves Miami（标准推导 >, <）
print("\n" + "=" * 60)
print(" 实验 1: United serves Miami（标准推导: > 和 <）")
print("=" * 60)

words1 = ["united", "serves", "miami"]
print(f"\n  词条范畴:")
print(f"    United : NP")
print(f"    serves : (S\\NP)/NP")
print(f"    Miami  : NP")

results1 = parse_sentence(words1, lex)
if results1:
    r = results1[0]
    print(f"\n  推导步骤:")
    for s in r["steps"]:
        print(s)
    print(f"\n  最终范畴: {r['cat']}")
    print(f"  最终语义: {r['sem']}")
else:
    print("  [解析失败]")


# ---- 实验 2: Romeo loves Juliet
print(f"\n\n{'='*60}")
print(" 实验 2: Romeo loves Juliet")
print(f"{'='*60}")

words2 = ["romeo", "loves", "juliet"]
results2 = parse_sentence(words2, lex)
if results2:
    r = results2[0]
    print(f"\n  推导步骤:")
    for s in r["steps"]:
        print(s)
    print(f"\n  最终范畴: {r['cat']}")
    print(f"  最终语义: {r['sem']}")


# ---- 实验 3: 类型提升——从左到右增量推导
print(f"\n\n{'='*60}")
print(" 实验 3: 类型提升 (Type Raising) — 从左到右增量推导")
print(f"{'='*60}")

print("""
  普通推导:
    United    serves       Miami
    NP        (S\\NP)/NP   NP
                >               → S\\NP      [serves 吃 Miami]
    <                          → S          [United 吃 S\\NP]
    
  注意: 最后一步是 backward (<)，主语在左边被函数吃。

  类型提升后:
    United↑            serves       Miami
    S/(S\\NP)          (S\\NP)/NP   NP
         >B                        → S/NP     [compose! United∘serves]
              >                     → S       [S/NP 吃 Miami]

  ★ 全程 forward (>B, >)，严格从左到右！
     这更接近人类增量式语言处理。
""")

# 用类型提升的词典解析
results3 = parse_sentence(["united_t", "serves", "miami"], lex)
if results3:
    r = results3[0]
    print(f"  类型提升推导步骤:")
    for s in r["steps"]:
        print(s)
    print(f"\n  最终范畴: {r['cat']}")
    print(f"  最终语义: {r['sem']}")
    print(f"\n  ✓ 同样的语义结果，但推导方向完全不同！")


# ---- 实验 4: 算子验证
print(f"\n\n{'='*60}")
print(" 实验 4: 三种算子验证")
print(f"{'='*60}")

S, NP, N = atom("S"), atom("NP"), atom("N")
SNP = bwd(S, NP)           # S\NP
SNPNP = fwd(SNP, NP)       # (S\NP)/NP

# Forward application: (S\NP)/NP  +  NP  =>  S\NP
result = forward_application(SNPNP, NP)
print(f"\n  >  (S\\NP)/NP  NP  =>  {result}")

# Backward application: NP + S\NP => S
result = backward_application(NP, SNP)
print(f"  <  NP  S\\NP      =>  {result}")

# Forward composition: S/(S\NP) + (S\NP)/NP => S/NP
T_cat = fwd(S, bwd(S, NP))  # S/(S\NP)
result = forward_composition(T_cat, SNPNP)
print(f"  >B S/(S\\NP) (S\\NP)/NP => {result}")


# ---- 总结
print(f"\n\n{'='*60}")
print(" 总结")
print(f"{'='*60}")
print("""
  ① CCG 只需两条函数应用规则 (> 和 <) 就能完成基本解析
     每条规则是一步函数调用，结果范畴是函数的返回值

  ② 句法和语义完全同构：
     > (forward application)  ↔ λ-reduction (函数应用到右侧参数)
     < (backward application) ↔ λ-reduction (函数应用到左侧参数)
     >B (forward composition) ↔ λ-composition f∘g

  ③ 类型提升把"参数"变成"函数"：
     NP  →  S/(S\\NP)
     使推导从 backward (<) 变成全 forward (>B, >)
     → 严格从左到右，更接近人类增量理解

  ④ ★ 反直觉：你不需要"句法分析器 + 语义分析器"两个系统。
     CCG 的范畴推导就是语义组合——一步到位。
     这就是为什么 CCG 是语义解析的事实标准。
""")
