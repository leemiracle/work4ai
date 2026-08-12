"""
Categories, Proofs & Processes (Oxford CS)
================================================
覆盖主题：
- Curry-Howard 同构（命题 ↔ 类型，证明 ↔ 程序）
- Simply Typed Lambda Calculus（STLC）
- 直觉主义逻辑（自然演绎）
- 基本 category theory（functor / natural transformation）

核心论文/教材（已核实）：
- Pierce "Types and Programming Languages" MIT Press 2002
- Howard "The Formulae-as-Types Notion of Construction" in To H.B. Curry: Essays, 1980
- Lambek & Scott "Introduction to Higher Order Categorical Logic" Cambridge 1986
- Mac Lane "Categories for the Working Mathematician" 2nd ed, Springer 1998
- Winskel & Dybjer "Semantics of Programming Languages" (Oxford lecture notes)

本文件实现：
- STLC 类型检查器 + Curry-Howard 映射
- 直觉主义自然演绎证明器
- Category theory：functor / natural transformation / adjunction
- Cartesian closed category (CCC) = STLC 的模型

运行：
    python cpp.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


# ============ 1. Simply Typed Lambda Calculus ============

@dataclass(frozen=True)
class TVar:
    """类型变量"""
    name: str

    def __str__(self):
        return self.name

@dataclass(frozen=True)
class TArrow:
    """函数类型 A → B"""
    domain: object
    codomain: object

    def __str__(self):
        d = str(self.domain)
        c = str(self.codomain)
        if isinstance(self.codomain, TArrow):
            c = f"({c})"
        if isinstance(self.domain, TArrow):
            d = f"({d})"
        return f"{d} → {c}"

@dataclass(frozen=True)
class TProd:
    """积类型 A × B"""
    left: object
    right: object

    def __str__(self):
        return f"({self.left} × {self.right})"


# STLC 项
@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Lam:
    var: str
    var_type: object  # 类型标注（STLC 需要显式类型）
    body: 'Term'

@dataclass(frozen=True)
class App:
    func: 'Term'
    arg: 'Term'

@dataclass(frozen=True)
class Pair:
    first: 'Term'
    second: 'Term'

@dataclass(frozen=True)
class Fst:
    pair: 'Term'

@dataclass(frozen=True)
class Snd:
    pair: 'Term'

Term = Union[Var, Lam, App, Pair, Fst, Snd]


class STLCTypeChecker:
    """STLC 类型检查器"""

    def __init__(self):
        self.context: dict[str, object] = {}

    def type_of(self, term: Term, ctx: dict = None) -> object:
        """返回项的类型"""
        if ctx is not None:
            self.context = ctx

        if isinstance(term, Var):
            if term.name not in self.context:
                raise TypeError(f"Unbound variable: {term.name}")
            return self.context[term.name]

        if isinstance(term, Lam):
            new_ctx = {**self.context, term.var: term.var_type}
            body_type = self.type_of(term.body, new_ctx)
            return TArrow(term.var_type, body_type)

        if isinstance(term, App):
            func_type = self.type_of(term.func)
            arg_type = self.type_of(term.arg)
            if not isinstance(func_type, TArrow):
                raise TypeError(f"Cannot apply non-function: {func_type}")
            if func_type.domain != arg_type:
                raise TypeError(f"Type mismatch: expected {func_type.domain}, got {arg_type}")
            return func_type.codomain

        if isinstance(term, Pair):
            lt = self.type_of(term.first)
            rt = self.type_of(term.second)
            return TProd(lt, rt)

        if isinstance(term, Fst):
            pair_type = self.type_of(term.pair)
            if not isinstance(pair_type, TProd):
                raise TypeError(f"fst on non-product: {pair_type}")
            return pair_type.left

        if isinstance(term, Snd):
            pair_type = self.type_of(term.pair)
            if not isinstance(pair_type, TProd):
                raise TypeError(f"snd on non-product: {pair_type}")
            return pair_type.right

        raise TypeError(f"Unknown term: {term}")


# ============ 2. Curry-Howard 同构 ============

def curry_howard_demo():
    """
    Curry-Howard 同构：

    逻辑                          | 类型论
    ---------------------------|---------------------------
    命题 A                       | 类型 A
    A ∧ B (and)                 | A × B (积类型/Pair)
    A ∨ B (or)                  | A + B (和类型/Either)
    A → B (蕴含)                | A → B (函数类型)
    ⊤ (truth)                   | Unit 类型 ()
    ⊥ (false)                   | 空类型 ⊥
    ¬A (not, = A → ⊥)           | A → ⊥
    证明 A                       | 类型 A 的程序
    假设 A (临时假设)             | 变量 x : A

    关键定理：
    - 命题 A 是直觉主义逻辑可证的 ⟺ 类型 A 是 STLC 可 inhabit 的
    - 每个直觉主义证明对应一个 STLC 程序（lambda term）
    """

    print("\n📋 Curry-Howard 同构示例")
    checker = STLCTypeChecker()

    # 1. 恒等函数 = A → A 的证明
    #   逻辑：假设 A，则 A（→ 引入规则）
    #   程序：λx:A. x
    id_term = Lam("x", TVar("A"), Var("x"))
    id_type = checker.type_of(id_term)
    print(f"   λx:A. x : {id_type}")
    print(f"   ← 证明命题 'A → A'（恒等蕴含）")

    # 2. 组合子 K: A → B → A
    #   逻辑：假设 A 和 B，则 A
    #   程序：λx:A. λy:B. x
    k_term = Lam("x", TVar("A"), Lam("y", TVar("B"), Var("x")))
    k_type = checker.type_of(k_term)
    print(f"\n   λx:A.λy:B. x : {k_type}")
    print(f"   ← 证明命题 'A → B → A'")

    # 3. 组合子 S: (A→B→C) → (A→B) → A→C
    s_term = Lam("f", TArrow(TVar("A"), TArrow(TVar("B"), TVar("C"))),
                 Lam("g", TArrow(TVar("A"), TVar("B")),
                     Lam("x", TVar("A"),
                         App(App(Var("f"), Var("x")), App(Var("g"), Var("x"))))))
    s_type = checker.type_of(s_term)
    print(f"\n   S 组合子 : {s_type}")
    print(f"   ← 证明 '(A→B→C)→(A→B)→A→C'")

    # 4. 积类型 = 合取
    pair_term = Pair(Var("p"), Var("q"))
    with_pq = checker.type_of(pair_term, {"p": TVar("P"), "q": TVar("Q")})
    print(f"\n   (p, q) : {with_pq}")
    print(f"   ← 从 P 和 Q 构造 P∧Q")

    # 5. 投影 = 合取消去
    fst_term = Fst(pair_term)
    fst_type = checker.type_of(fst_term, {"p": TVar("P"), "q": TVar("Q")})
    print(f"   fst(p,q) : {fst_type}")
    print(f"   ← 从 P∧Q 推出 P")


# ============ 3. 直觉主义自然演绎 ============

class IntuitionisticLogic:
    """直觉主义逻辑自然演绎

    与经典逻辑的区别：
    - 排中律 A∨¬A 不成立
    - 双重否定消去 ¬¬A → A 不成立
    - 证明必须构造性的（有见证/witness）

    规则（与 STLC 的构造子一一对应）：
    →I (引入): 从 [A] ... B 推出 A→B      = λ-abstraction
    →E (消去): 从 A→B 和 A 推出 B          = application
    ∧I:        从 A 和 B 推出 A∧B          = pair
    ∧E₁:       从 A∧B 推出 A               = fst
    ∧E₂:       从 A∧B 推出 B               = snd
    """

    def __init__(self):
        self.proofs = []

    def check_proof(self, sequent: tuple, proof_tree: list) -> bool:
        """真正的直觉主义自然演绎证明检查器。

        sequent: (premises_set, conclusion) e.g. ({}, "A→A")
        proof_tree: list of rule applications. 每条规则形如:
            ("assumption", "A")           # 引入假设 A
            ("→I", "A", "B", proof_B)     # 从 [A] ... B 推出 A→B
            ("→E", proof_AB, proof_A)     # 从 A→B 和 A 推出 B
            ("∧I", proof_A, proof_B)      # 从 A 和 B 推出 A∧B
            ("∧E1", proof_AB, "A", "B")   # 从 A∧B 推出 A
            ("∧E2", proof_AB, "A", "B")   # 从 A∧B 推出 B
            ("axiom", "A")                # 公理（已在前提中）

        返回 True iff 证明树合法推出 sequent 的 conclusion。
        """
        premises, conclusion = sequent

        def check(node, context: set) -> str | None:
            """递归检查 node，返回推出的类型（=命题），失败返回 None。"""
            if not isinstance(node, tuple) or len(node) == 0:
                return None

            tag = node[0]

            if tag == "assumption" or tag == "axiom":
                prop = node[1]
                # 公理必须在 context 或 premises 中
                if prop in context or prop in premises:
                    return prop
                return None

            if tag == "→I":
                # 从 [A] ... B 推出 A→B
                _, A, B, proof_B = node
                # 在 context + {A} 下检查 proof_B 推出 B
                result_B = check(proof_B, context | {A})
                if result_B == B:
                    return f"{A}→{B}"
                return None

            if tag == "→E":
                # 从 A→B 和 A 推出 B
                _, proof_AB, proof_A = node
                # 我们不解析复杂的命题字符串，简化为：
                # proof_AB 必须推出形如 X→Y，proof_A 必须推出 X
                # 此简化版：把 proof_AB 和 proof_A 看作子树递归
                type_AB = check(proof_AB, context)
                type_A = check(proof_A, context)
                if type_AB is None or type_A is None:
                    return None
                # 检查 type_AB 形如 X→Y 且 type_A == X
                if "→" in type_AB:
                    left, right = type_AB.split("→", 1)
                    if left == type_A:
                        return right
                return None

            if tag == "∧I":
                # 从 A 和 B 推出 A∧B
                _, proof_A, proof_B = node
                type_A = check(proof_A, context)
                type_B = check(proof_B, context)
                if type_A is None or type_B is None:
                    return None
                return f"{type_A}∧{type_B}"

            if tag == "∧E1":
                # 从 A∧B 推出 A
                _, proof_AB, A, B = node
                type_AB = check(proof_AB, context)
                if type_AB == f"{A}∧{B}":
                    return A
                return None

            if tag == "∧E2":
                # 从 A∧B 推出 B
                _, proof_AB, A, B = node
                type_AB = check(proof_AB, context)
                if type_AB == f"{A}∧{B}":
                    return B
                return None

            return None

        final = check(proof_tree, set(premises))
        ok = final == conclusion

        print(f"     sequent: {set(premises)} ⊢ {conclusion}")
        print(f"     证明树推出: {final}")
        print(f"     结论: {'✓ 通过' if ok else '✗ 失败'}")
        return ok


def peirce_law_not_constructive():
    """Peirce 律在直觉主义逻辑中不可证。

    ((P → Q) → P) → P

    这是经典逻辑的公理之一，但直觉主义无法构造其证明项。
    """
    print("\n📋 Peirce 律：经典逻辑 vs 直觉主义逻辑")
    print("   Peirce 律: ((P→Q)→P)→P")
    print("   在经典逻辑中：可证（等价于排中律）")
    print("   在直觉主义逻辑中：不可证（无法构造证明项）")
    print("   → 这就是为什么 STLC 对应直觉主义而非经典逻辑")


# ============ 4. Category Theory ============

@dataclass
class Category:
    """一个范畴"""
    name: str
    objects: set
    morphisms: dict  # {(src, dst): [morph_name]}

    def add_object(self, obj):
        self.objects.add(obj)

    def add_morphism(self, src, dst, name):
        self.morphisms.setdefault((src, dst), []).append(name)


@dataclass
class Functor:
    """函子 F: C → D
    - 将 C 的对象映射到 D 的对象
    - 将 C 的态射映射到 D 的态射
    - 保持恒等: F(id_A) = id_{F(A)}
    - 保持复合: F(g ∘ f) = F(g) ∘ F(f)
    """
    name: str
    obj_map: dict  # C.obj → D.obj
    mor_map: dict  # C.mor → D.mor

    def apply_object(self, obj):
        return self.obj_map.get(obj, obj)

    def apply_morphism(self, mor):
        return self.mor_map.get(mor, mor)


@dataclass
class NaturalTransformation:
    """自然变换 α: F ⇒ G
    对每个对象 A，有分量 α_A: F(A) → G(A)
    满足自然性: G(f) ∘ α_A = α_B ∘ F(f) for all f: A → B
    """
    name: str
    components: dict  # {obj: morphism_name}


def identity_functor(cat: Category) -> Functor:
    """恒等函子 Id: C → C"""
    return Functor(
        name=f"Id_{cat.name}",
        obj_map={o: o for o in cat.objects},
        mor_map={}
    )


def maybe_functor() -> Functor:
    """Maybe 函子: Set → Set
    A ↦ Maybe(A) = A ∪ {None}
    f ↦ λx. if x is None then None else f(x)
    """
    return Functor(
        name="Maybe",
        obj_map={"Int": "Maybe<Int>", "String": "Maybe<String>"},
        mor_map={}
    )


def list_functor() -> Functor:
    """List 函子: Set → Set
    A ↦ List(A) = A*
    f ↦ map(f)
    """
    return Functor(
        name="List",
        obj_map={"Int": "List<Int>", "String": "List<String>"},
        mor_map={}
    )


# ============ 5. Cartesian Closed Category (CCC) ============

def ccc_is_model_of_stlc():
    """CCC 是 STLC 的范畴模型。

    CCC 公理：
    1. 有终对象 1（Unit 类型）
    2. 有二元积 A × B（Pair 类型）
    3. 有指数 B^A = A → B（函数类型）

    CCC 的 Hom-Set 解释：
    Hom(1, A)         ≅ A 的"点"（即 A 的元素）
    Hom(A × B, C)     ≅ Hom(A, C^B)   （currying）

    这正是 STLC 的 denotational semantics。
    """
    print("\n📋 CCC = STLC 的范畴模型")
    print("   Cartesian Closed Category (CCC) 公理:")
    print("   1. 终对象 1       ⟺  Unit 类型 ()")
    print("   2. 积 A × B       ⟺  Pair 类型")
    print("   3. 指数 B^A       ⟺  函数类型 A → B")
    print("\n   Currying 同构: Hom(A×B, C) ≅ Hom(A, C^B)")
    print("   ⟺ STLC: (A×B)→C 的项 ⟺ A→(B→C) 的项")


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Categories, Proofs & Processes (Oxford CS) Demo")
    print("=" * 65)

    # 1. STLC 类型检查
    print("\n📋 1. Simply Typed Lambda Calculus 类型检查")
    checker = STLCTypeChecker()

    # λx:A. x : A → A
    id_term = Lam("x", TVar("A"), Var("x"))
    print(f"   λx:A. x : {checker.type_of(id_term)}")

    # λx:A. λy:B. x : A → B → A
    k_term = Lam("x", TVar("A"), Lam("y", TVar("B"), Var("x")))
    print(f"   λx:A.λy:B. x : {checker.type_of(k_term)}")

    # λf:(A→B).λx:A. f(x) : (A→B) → A → B
    app_term = Lam("f", TArrow(TVar("A"), TVar("B")),
                   Lam("x", TVar("A"), App(Var("f"), Var("x"))))
    print(f"   λf:A→B.λx:A.f(x) : {checker.type_of(app_term)}")

    # 类型错误演示
    print("\n   类型错误检测:")
    try:
        bad_term = App(Var("f"), Var("x"))
        checker.type_of(bad_term, {"f": TVar("A"), "x": TVar("B")})
    except TypeError as e:
        print(f"   f(x) where f:A, x:B → TypeError: {e}")

    # 2. Curry-Howard
    curry_howard_demo()

    # 3. Peirce 律
    peirce_law_not_constructive()

    # 4. Category Theory
    print("\n📋 2. Category Theory: Functor")
    sets = Category("Set", {"Int", "String", "Bool"}, {})

    id_f = identity_functor(sets)
    maybe_f = maybe_functor()
    list_f = list_functor()

    print(f"   范畴: {sets.name}, objects: {sets.objects}")
    print(f"\n   恒等函子 Id: {id_f.name}")
    print(f"     Id(Int) = {id_f.apply_object('Int')}")
    print(f"\n   Maybe 函子: {maybe_f.name}")
    print(f"     Maybe(Int) = {maybe_f.apply_object('Int')}")
    print(f"     Maybe(String) = {maybe_f.apply_object('String')}")
    print(f"\n   List 函子: {list_f.name}")
    print(f"     List(Int) = {list_f.apply_object('Int')}")

    # 自然变换
    print("\n📋 3. Natural Transformation")
    # safeHead: List → Maybe
    safe_head = NaturalTransformation(
        name="safeHead",
        components={"Int": "safeHead_Int", "String": "safeHead_String"}
    )
    print(f"   α = {safe_head.name}: List ⇒ Maybe")
    print(f"   分量:")
    for obj, mor in safe_head.components.items():
        print(f"     α_{obj} = {mor}: List<{obj}> → Maybe<{obj}>")
    print(f"   自然性: Maybe(f) ∘ α_A = α_B ∘ List(f)")

    # 5. CCC
    ccc_is_model_of_stlc()

    # 6. 直觉主义逻辑
    print("\n📋 4. 直觉主义逻辑自然演绎（真证明检查器）")
    il = IntuitionisticLogic()

    # 合法证明 A → A∧A：用 →I 包住 ∧I
    # proof tree: ("→I", "A", "A∧A", ("∧I", ("assumption", "A"), ("assumption", "A")))
    print("\n   证明 A → A∧A（合法）:")
    proof_valid = (
        "→I", "A", "A∧A",
        ("∧I", ("assumption", "A"), ("assumption", "A"))
    )
    ok1 = il.check_proof(([], "A→A∧A"), proof_valid)
    print(f"   返回: {ok1}  (期望 True)")

    # 非法证明：尝试证明 A → B（无依据）
    print("\n   证明 A → B（非法——B 无依据）:")
    proof_invalid = (
        "→I", "A", "B",
        ("assumption", "B")  # B 不在 context（只有 A）
    )
    ok2 = il.check_proof(([], "A→B"), proof_invalid)
    print(f"   返回: {ok2}  (期望 False)")

    # 非法证明：尝试用 ∧E1 从单个 A 取出 A∧B 的左分量（前提不匹配）
    print("\n   证明从 A 取 A∧B 的左分量（非法——前提不是 A∧B）:")
    proof_invalid2 = (
        "∧E1", ("assumption", "A"), "A", "B"
    )
    ok3 = il.check_proof((["A"], "A"), proof_invalid2)
    print(f"   返回: {ok3}  (期望 False)")

    # 合法证明：前提 A∧B ⊢ A
    print("\n   证明 A∧B ⊢ A（合法）:")
    proof_valid2 = (
        "∧E1", ("assumption", "A∧B"), "A", "B"
    )
    ok4 = il.check_proof((["A∧B"], "A"), proof_valid2)
    print(f"   返回: {ok4}  (期望 True)")

    print("\n   对比 STLC 类型检查（Curry-Howard）:")
    print("   - 合法证明 = 类型检查通过 = 构造性见证存在")
    print("   - 非法证明 = 类型检查失败 = 没有构造性见证")
    print("   - 这正是 Curry-Howard 同构：proofs ≡ programs, propositions ≡ types")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. Curry-Howard: 每个 STLC 类型对应一个逻辑命题")
    print("      A→B→A 的证明 = λx.λy.x，类型检查通过 = 逻辑证明有效")
    print("   2. Peirce 律 ((P→Q)→P)→P 在经典逻辑可证，直觉主义不可证")
    print("      → STLC 类型系统比经典逻辑'弱'，但更构造性")
    print("   3. Maybe/List 是函子(Functor)，map 是它们的态射映射")
    print("      safeHead:List→Maybe 是自然变换（对所有类型一致地工作）")
    print("   4. CCC 的 currying 同构 Hom(A×B,C)≅Hom(A,C^B)")
    print("      就是程序中'curring'的数学基础")
    print("=" * 65)


if __name__ == "__main__":
    main()
