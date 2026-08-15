"""
Principles of Programming Languages (Oxford CS)
================================================
覆盖主题：
- λ-calculus（无类型：alpha/beta/eta 归约；Church 编码）
- Hindley-Milner 类型推导（Algorithm W）
- Continuations（CPS 变换）
- Monads（State / Option）

核心论文/教材（已核实）：
- Pierce "Types and Programming Languages" MIT Press 2002
- Damas & Milner "Principal type-schemes of functional programs" POPL 1982
- Barendregt "The Lambda Calculus: Its Syntax and Semantics" North-Holland 1984
- Wadler "Monads for functional programming" Marktoberdorf 1992

本文件实现：
- λ-calculus 解释器（beta 归约 + Church numerals）
- HM Algorithm W（类型推导 mini-ML）
- CPS 变换
- State/Option monad

运行：
    python pl.py
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union


# ============ 1. λ-Calculus ============

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class App:
    func: 'Expr'
    arg: 'Expr'

@dataclass(frozen=True)
class Lam:
    param: str
    body: 'Expr'

@dataclass(frozen=True)
class Let:
    """let name = expr1 in expr2  (Hindley-Milner let-polymorphism)"""
    name: str
    expr1: 'Expr'
    expr2: 'Expr'

Expr = Union[Var, App, Lam, Let]


def free_vars(e: Expr) -> set[str]:
    if isinstance(e, Var):
        return {e.name}
    if isinstance(e, App):
        return free_vars(e.func) | free_vars(e.arg)
    if isinstance(e, Lam):
        return free_vars(e.body) - {e.param}
    if isinstance(e, Let):
        return (free_vars(e.expr1) | (free_vars(e.expr2) - {e.name}))
    return set()


_counter = [0]

def fresh_var(base: str = "t") -> str:
    _counter[0] += 1
    return f"{base}{_counter[0]}"


def substitute(e: Expr, var: str, replacement: Expr) -> Expr:
    """[var := replacement] e"""
    if isinstance(e, Var):
        return replacement if e.name == var else e
    if isinstance(e, App):
        return App(substitute(e.func, var, replacement),
                    substitute(e.arg, var, replacement))
    if isinstance(e, Lam):
        if e.param == var:
            return e  # shadowing
        if e.param in free_vars(replacement):
            # alpha conversion: 重命名绑定变量避免捕获
            new_param = fresh_var(e.param)
            renamed = substitute(e.body, e.param, Var(new_param))
            return Lam(new_param, substitute(renamed, var, replacement))
        return Lam(e.param, substitute(e.body, var, replacement))
    return e


def beta_reduce(e: Expr, max_steps: int = 100) -> tuple[Expr, int]:
    """Normal order beta reduction"""
    for step in range(max_steps):
        result = _reduce_once(e)
        if result is None:
            return e, step
        e = result
    return e, max_steps


def _reduce_once(e: Expr) -> Expr | None:
    """做一步 beta 归约（normal order: 最外最左优先）"""
    if isinstance(e, App):
        if isinstance(e.func, Lam):
            # (λx.body) arg → body[x := arg]
            return substitute(e.func.body, e.func.param, e.arg)
        # 先归约函数部分
        reduced_func = _reduce_once(e.func)
        if reduced_func is not None:
            return App(reduced_func, e.arg)
        # 再归约参数部分
        reduced_arg = _reduce_once(e.arg)
        if reduced_arg is not None:
            return App(e.func, reduced_arg)
        return None
    if isinstance(e, Lam):
        reduced = _reduce_once(e.body)
        return Lam(e.param, reduced) if reduced is not None else None
    return None


def church_numeral(n: int) -> Expr:
    """Church 编码：n = λf.λx. f^n(x)"""
    body = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Lam("f", Lam("x", body))


def church_to_int(e: Expr) -> int:
    """解释 Church numeral"""
    def apply_n(f, x, n):
        result = x
        for _ in range(n):
            result = f(result)
        return result
    # 用 Python 函数模拟
    f_marker = lambda v: v + 1
    try:
        result = e  # λf.λx. ...
        # 手动 beta 归约应用到 (λv.v+1) 和 0
        reduced, _ = beta_reduce(App(App(e, Lam("_v", Var("INC"))), Lam("_w", Var("ZERO"))))
        # 用更简单的方式：直接提取 f 出现次数
        body = e
        if isinstance(e, Lam) and isinstance(e.body, Lam):
            inner = e.body.body
            count = 0
            cur = inner
            while isinstance(cur, App):
                count += 1
                cur = cur.arg
            return count
    except Exception:
        return -1


def church_successor(n_expr: Expr) -> Expr:
    """SUCC = λn.λf.λx. f(n f x)"""
    succ = Lam("n", Lam("f", Lam("x",
        App(Var("f"), App(App(Var("n"), Var("f")), Var("x"))))))
    return App(succ, n_expr)


# ============ 2. Hindley-Milner Algorithm W ============

class TypeVar:
    _id = 0
    def __init__(self):
        TypeVar._id += 1
        self.id = TypeVar._id
        self.instance = None  # None, TypeVar, or concrete type (TCon/TArrow)

    def find(self):
        """Follow the chain until we hit a non-TypeVar or unresolved TypeVar."""
        if self.instance is None:
            return self
        if isinstance(self.instance, TypeVar):
            resolved = self.instance.find()
            self.instance = resolved  # path compression
            return resolved
        return self.instance  # concrete type (TCon/TArrow)

    def __repr__(self):
        return f"t{self.find().id}"


@dataclass
class TVar:
    tv: TypeVar

@dataclass
class TCon:
    name: str  # "Int", "Bool"

@dataclass
class TArrow:
    """函数类型 a -> b"""
    left: object
    right: object

@dataclass
class Scheme:
    """多态类型 ∀a. τ"""
    vars: list[TypeVar]
    typ: object


def occurs_in(v: TypeVar, t) -> bool:
    if isinstance(t, TVar):
        return v is t.tv.find()
    if isinstance(t, TArrow):
        return occurs_in(v, t.left) or occurs_in(v, t.right)
    return False


def unify(t1, t2) -> dict:
    """Robinson 统一算法"""
    # 解引用
    if isinstance(t1, TVar):
        v = t1.tv.find()
        if isinstance(v, TypeVar) and v.instance is None:
            if occurs_in(v, t2):
                raise TypeError(f"Occurs check failed: t{v.id} in {t2}")
            v.instance = t2
            return {"ok": True}
        # v 已经被绑定到具体类型，递归
        if isinstance(v, TypeVar):
            return unify(TVar(v), t2)
        return unify(v, t2)  # v 是 TCon/TArrow
    if isinstance(t2, TVar):
        return unify(t2, t1)
    if isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name == t2.name:
            return {"ok": True}
        raise TypeError(f"Cannot unify {t1.name} with {t2.name}")
    if isinstance(t1, TArrow) and isinstance(t2, TArrow):
        unify(t1.left, t2.left)
        unify(t1.right, t2.right)
        return {"ok": True}
    raise TypeError(f"Cannot unify {t1} with {t2}")


def infer(expr: Expr, env: dict) -> object:
    """Algorithm W: 表达式 → 类型

    支持 let-polymorphism（Hindley-Milner 核心）：
    - λ 内的形参是 monomorphic（不可多态使用）
    - let x = e1 in e2 中 x 在 e2 中是 polymorphic（∀ 自由变量）
    """
    if isinstance(expr, Var):
        if expr.name in env:
            scheme = env[expr.name]
            if isinstance(scheme, Scheme) and scheme.vars:
                # 实例化多态类型
                mapping = {v: TypeVar() for v in scheme.vars}
                return _instantiate(scheme.typ, mapping)
            return scheme if not isinstance(scheme, Scheme) else scheme.typ
        raise TypeError(f"Unbound variable: {expr.name}")

    if isinstance(expr, Lam):
        param_type = TVar(TypeVar())
        new_env = {**env, expr.param: param_type}
        body_type = infer(expr.body, new_env)
        return TArrow(param_type, body_type)

    if isinstance(expr, App):
        func_type = infer(expr.func, env)
        arg_type = infer(expr.arg, env)
        result_type = TVar(TypeVar())
        unify(func_type, TArrow(arg_type, result_type))
        return result_type

    if isinstance(expr, Let):
        # Hindley-Milner let-polymorphism:
        # 1) infer e1 in current env → monotype T1
        # 2) generalize T1 against env → scheme ∀ vars.T1
        # 3) extend env with name → scheme
        # 4) infer e2 in extended env
        t1 = infer(expr.expr1, env)
        scheme = _generalize(env, t1)
        new_env = {**env, expr.name: scheme}
        return infer(expr.expr2, new_env)

    raise TypeError(f"Cannot infer {expr}")


def _generalize(env, typ):
    """收集 typ 中所有自由 TypeVar，量化它们成多态 Scheme。

    通用规则：typ 中的 TypeVar 如果不出现在 env 任何 scheme 的 monotype 里，
    就是 "可泛化的"（绑定到 let 后才能多态使用）。
    """
    # 收集 env 中所有已锁定的 TypeVar（monomorphic free vars）
    env_free = set()

    def collect_env_free(t):
        if isinstance(t, dict):
            for v in t.values():
                collect_env_free(v)
        elif isinstance(t, Scheme):
            # 注意：Scheme 中 quantified vars 已是 ∀ 量化，不算 env free
            collect_env_free(t.typ)
        elif isinstance(t, TVar):
            tv = t.tv.find()
            if isinstance(tv, TypeVar):
                env_free.add(tv)

    for v in env.values():
        collect_env_free(v)

    # 收集 typ 中所有自由 TypeVar
    typ_free = []

    def collect_typ_free(t):
        if isinstance(t, TVar):
            tv = t.tv.find()
            if isinstance(tv, TypeVar) and tv not in env_free and tv not in typ_free:
                typ_free.append(tv)
        elif isinstance(t, TArrow):
            collect_typ_free(t.left)
            collect_typ_free(t.right)

    collect_typ_free(typ)
    return Scheme(typ_free, typ)


def _instantiate(typ, mapping):
    if isinstance(typ, TVar):
        if typ.tv in mapping:
            return TVar(mapping[typ.tv])
        return typ
    if isinstance(typ, TArrow):
        return TArrow(_instantiate(typ.left, mapping), _instantiate(typ.right, mapping))
    return typ


def type_to_str(t) -> str:
    """Pretty print a type. t can be TVar, TCon, or TArrow."""
    if isinstance(t, TVar):
        resolved = t.tv.find()
        if isinstance(resolved, TypeVar):
            return f"t{resolved.id}"
        return type_to_str(resolved)  # resolved to concrete type
    if isinstance(t, TCon):
        return t.name
    if isinstance(t, TArrow):
        return f"({type_to_str(t.left)} → {type_to_str(t.right)})"
    if isinstance(t, TypeVar):
        return f"t{t.id}"
    return str(t)


# ============ 3. CPS 变换 ============

def cps_transform(e: Expr, k: str = "k") -> Expr:
    """CPS (Continuation-Passing Style) 变换

    基本思想：每个函数多接收一个 continuation 参数 k，
    不直接返回值，而是把结果传给 k。

    [[x]] k = k x
    [[λx.e]] k = k (λx.λk'. [[e]] k')
    [[e1 e2]] k = [[e1]] (λf. [[e2]] (λa. f a k))
    """
    if isinstance(e, Var):
        return App(Var(k), e)
    if isinstance(e, Lam):
        k2 = fresh_var("k'")
        return App(Var(k), Lam(e.param, Lam(k2, cps_transform(e.body, k2))))
    if isinstance(e, App):
        # [[e1]] (λf. [[e2]] (λa. f a k))
        f_var = fresh_var("f")
        a_var = fresh_var("a")
        inner_k = Lam(f_var, App(
            cps_transform(e.arg, a_var),
            Lam(a_var, App(App(Var(f_var), Var(a_var)), Var(k)))
        ))
        return cps_transform(e.func, f_var)
    return App(Var(k), e)


def cps_transform_simple(e: Expr) -> Expr:
    """简化版 CPS：仅处理 Var"""
    if isinstance(e, Var):
        return e
    return e


# ============ 4. Monads ============

class StateMonad:
    """State monad: S → (A, S)

    return a = λs. (a, s)
    m >>= f = λs. let (a, s') = m(s) in f(a)(s')
    """
    @staticmethod
    def unit(value):
        def run(state):
            return value, state
        return run

    @staticmethod
    def bind(m, f):
        def run(state):
            value, new_state = m(state)
            return f(value)(new_state)
        return run

    @staticmethod
    def get():
        return lambda state: (state, state)

    @staticmethod
    def put(new_state):
        return lambda state: (None, new_state)

    @staticmethod
    def modify(fn):
        return lambda state: (None, fn(state))


class OptionMonad:
    """Option/Maybe monad"""

    @staticmethod
    def unit(value):
        return ("some", value)

    @staticmethod
    def none():
        return ("none", None)

    @staticmethod
    def bind(m, f):
        if m[0] == "none":
            return m
        return f(m[1])


def demo_state_monad():
    """用 state monad 实现计数器"""
    print("\n📋 State Monad：计数器")
    # increment: modify(state + 1)
    increment = StateMonad.modify(lambda s: s + 1)
    # program: increment 3 次，然后 get
    program = StateMonad.bind(
        increment,
        lambda _: StateMonad.bind(
            increment,
            lambda _: StateMonad.bind(
                increment,
                lambda _: StateMonad.get()
            )
        )
    )
    result, final_state = program(0)
    print(f"   初始 state=0, increment×3, get → {result}, final={final_state}")


def demo_option_monad():
    """Option monad：安全除法"""
    print("\n📋 Option Monad：安全除法链")
    def safe_div(a, b):
        if b == 0:
            return OptionMonad.none()
        return OptionMonad.unit(a / b)

    # 100 / 5 / 2 = 10
    chain1 = OptionMonad.bind(
        safe_div(100, 5),
        lambda r1: OptionMonad.bind(
            safe_div(r1, 2),
            lambda r2: OptionMonad.unit(f"结果={r2}")
        )
    )
    print(f"   100 / 5 / 2 = {chain1}")

    # 100 / 0 → none，链短路
    chain2 = OptionMonad.bind(
        safe_div(100, 0),
        lambda r1: OptionMonad.bind(
            safe_div(r1, 2),
            lambda r2: OptionMonad.unit(f"结果={r2}")
        )
    )
    print(f"   100 / 0 / 2 = {chain2} (短路，不报错)")


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Principles of Programming Languages (Oxford) Demo")
    print("=" * 65)

    # 1. λ-calculus
    print("\n📋 1. λ-Calculus: Beta 归约")
    # (λx.x) y → y (identity)
    expr = App(Lam("x", Var("x")), Var("y"))
    result, steps = beta_reduce(expr)
    print(f"   (λx.x) y → {result} (步数={steps})")

    # (λx.λy.x) a b → a (K combinator)
    expr2 = App(App(Lam("x", Lam("y", Var("x"))), Var("a")), Var("b"))
    result2, steps2 = beta_reduce(expr2)
    print(f"   (λx.λy.x) a b → {result2} (步数={steps2})")

    # Church numerals
    print("\n📋 2. Church Numerals")
    zero = church_numeral(0)
    one = church_numeral(1)
    three = church_numeral(3)
    print(f"   0 = λf.λx. x = {zero}")
    print(f"   1 = λf.λx. f(x) = {one}")
    print(f"   3 = λf.λx. f(f(f(x))) = {three}")
    # 验证 Church numeral 值
    print(f"   church numeral 值: 0→{church_to_int(zero)}, 1→{church_to_int(one)}, 3→{church_to_int(three)}")

    # 2. HM Type Inference
    print("\n📋 3. Hindley-Milner 类型推导")
    TypeVar._id = 0
    # λx.x : α → α  (identity)
    identity = Lam("x", Var("x"))
    t = infer(identity, {})
    print(f"   λx.x : {type_to_str(t)}")

    # λx.λy.x : α → β → α  (K combinator)
    k_comb = Lam("x", Lam("y", Var("x")))
    t2 = infer(k_comb, {})
    print(f"   λx.λy.x : {type_to_str(t2)}")

    # λf.λx.f(x) : (α → β) → α → β
    app_fn = Lam("f", Lam("x", App(Var("f"), Var("x"))))
    t3 = infer(app_fn, {})
    print(f"   λf.λx.f(x) : {type_to_str(t3)}")

    # ⭐ Hindley-Milner let-polymorphism (the killer feature)
    # 关键实验：let id = λx.x in B
    #   B 中可同时使用 id 多次（不同类型），每次都 instantiate 新的 α
    # λ-bound 变量没有此特性（monomorphic）
    print("\n📋 4. ⭐ Let-Polymorphism（HM 的杀手锏）")
    TypeVar._id = 0
    Int = TCon("Int")
    Bool = TCon("Bool")

    # 实验 A: let id = λx.x in id 1  →  Int  （id 实例化为 Int→Int）
    TypeVar._id = 0
    Int_1 = TCon("Int_1")
    let_apply_int = Let(
        "id",
        Lam("x", Var("x")),
        App(Var("id"), Var("1")),  # id 1
    )
    try:
        t_let_int = infer(let_apply_int, {"1": Int})
        print(f"   实验 A: let id = λx.x in (id 1)  →  {type_to_str(t_let_int)}  ✓")
        print(f"           （id 被 generalize 成 ∀α.α→α，再 instantiate 成 Int→Int）")
    except TypeError as e:
        print(f"   实验 A 失败: {e}")

    # 实验 B: let id = λx.x in id True  →  Bool （id 实例化为 Bool→Bool）
    TypeVar._id = 0
    let_apply_bool = Let(
        "id",
        Lam("x", Var("x")),
        App(Var("id"), Var("True")),  # id True
    )
    try:
        t_let_bool = infer(let_apply_bool, {"True": Bool})
        print(f"   实验 B: let id = λx.x in (id True)  →  {type_to_str(t_let_bool)}  ✓")
        print(f"           （id 被 generalize 成 ∀α.α→α，再 instantiate 成 Bool→Bool）")
    except TypeError as e:
        print(f"   实验 B 失败: {e}")

    # 实验 C（杀手锏）: 同一个 let 体内用 id 两次（不同类型）
    # let id = λx.x in (λresult.id_2nd)(id 1st)
    # 这里我们利用 "let 体内可以引用 id 多次" 来证明多态：
    # 构造：let id = λx.x in (id (λy.y))  —— id 应用于另一个函数
    # 此时 id 实例化为 (β→β)→(β→β)
    TypeVar._id = 0
    let_apply_fn = Let(
        "id",
        Lam("x", Var("x")),
        App(Var("id"), Lam("y", Var("y"))),  # id (λy.y)
    )
    try:
        t_let_fn = infer(let_apply_fn, {})
        print(f"   实验 C: let id = λx.x in id (λy.y)  →  {type_to_str(t_let_fn)}  ✓")
        print(f"           （id 实例化为 (β→β)→(β→β)，说明多态机制工作）")
    except TypeError as e:
        print(f"   实验 C 失败: {e}")

    # 实验 D（对比）: λ-bound 等价物 — 同样表达式用 λ 包装
    # (λid.id (λy.y)) (λx.x)
    # λ 内 id 被 monotype 锁定，但只用一次不会触发限制
    TypeVar._id = 0
    lambda_eq = App(
        Lam("id", App(Var("id"), Lam("y", Var("y")))),
        Lam("x", Var("x")),
    )
    try:
        t_lam_eq = infer(lambda_eq, {})
        print(f"   实验 D: (λid.id(λy.y))(λx.x)  →  {type_to_str(t_lam_eq)}  ✓")
        print(f"           （仅用一次，λ 和 let 等价；多次用才能见差异——见下）")
    except TypeError as e:
        print(f"   实验 D 失败: {e}")

    # 实验 E（关键对比）: 强制在 λ 体内多次使用 id 但要求不同类型
    # (λid. [id 1 ; id (id True)]) ... 即 id 先用作 Int→Int，又用作 Bool→Bool→Bool
    # 这在 λ 下应该失败（monomorphic），在 let 下应该成功
    # 我们用一个表示 "把两个值组合" 的内建 comb：comb = λa.λb.b（忽略 a 返回 b 类型）
    # 这样：comb (id 1)(id (id True))
    # 在 λ 下：id 一旦绑定为 Int→Int，第二次必须也是 Int，但传了 Bool → 失败
    TypeVar._id = 0
    comb_env = {"1": Int, "True": Bool}
    # 模拟 let f = λx.x in comb(f 1)(f(f True))
    # 用 Church pair 的 second 投影做 comb：pair a b → b
    # 简化为：f (f True)，让 f 同时被实例化为 Bool→Bool 和 Bool→Bool→Bool（这不可能在 monomorphic 下成立）
    # 最简：let f = λx.x in <use f with Int and Bool>
    # 用 pair = λa.λb.a 模拟 tuple 取第一个
    # pair (f 1)(f True): 强制 f 既为 Int→Int 又为 Bool→Bool
    # 用 pair = λa.λb.b (右投影)
    let_double = Let(
        "f",
        Lam("x", Var("x")),
        # body: (λp.p) ((λa.λb.b)(f 1)(f True))
        #       内层强制 f 用于 Int 和 Bool
        App(
            Lam("p", Var("p")),
            App(
                App(Lam("a", Lam("b", Var("b"))), App(Var("f"), Var("1"))),
                App(Var("f"), Var("True"))
            ),
        ),
    )
    try:
        t_let_double = infer(let_double, comb_env)
        print(f"   实验 E (let):  let f=λx.x in (λa.λb.b)(f 1)(f True)  →  {type_to_str(t_let_double)}  ✓")
        print(f"           （let 多态：f 同时被实例化为 Int→Int 和 Bool→Bool，类型检查通过）")
    except TypeError as e:
        print(f"   实验 E (let)  失败: {e}")

    # 同样表达式改用 λ 包装 → 应失败
    TypeVar._id = 0
    lambda_double = App(
        Lam("f",
            App(
                Lam("p", Var("p")),
                App(
                    App(Lam("a", Lam("b", Var("b"))), App(Var("f"), Var("1"))),
                    App(Var("f"), Var("True"))
                ),
            )),
        Lam("x", Var("x")),
    )
    try:
        t_lam_double = infer(lambda_double, comb_env)
        print(f"   实验 F (λ):    (λf.(λa.λb.b)(f 1)(f True))(λx.x)  →  {type_to_str(t_lam_double)}")
        print(f"           （意外通过——可能 λ 内只 unify 一次未触发约束）")
    except TypeError as e:
        print(f"   实验 F (λ):    (λf.(λa.λb.b)(f 1)(f True))(λx.x)")
        print(f"           →  ✗ 失败: {str(e)[:100]}")
        print(f"           （对比: let 版本通过，λ 版本失败 → 这是 HM 多态核心区别）")

    # 3. State/Option Monad
    demo_state_monad()
    demo_option_monad()

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print("   1. λ-calculus 只用 3 条规则(变量/应用/抽象)+1条归约规则(β)")
    print("      就能表达全部计算——Church numerals 用纯函数编码数字")
    print("   2. HM let-polymorphism：let id=λx.x in (id 1, id True) 通过类型检查")
    print("      但等价的 (λid.(id 1, id True))(λx.x) 会失败——这是 Damas-Milner")
    print("      let 多态的核心：只有 let-bound 变量才能多态使用（λ-bound 不能）")
    print("   3. Option monad 链式调用中除以 0 会自动'短路'返回 none")
    print("      —— monad 的本质 = 计算上下文的组合")
    print("=" * 65)


if __name__ == "__main__":
    main()
