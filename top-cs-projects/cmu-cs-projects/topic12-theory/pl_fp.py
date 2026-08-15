"""
15-150 FP + 15-312 PL + 15-251 GITCS (CMU)
================================================
覆盖主题（对应 lecture）：
- Functional Programming: lambda calculus interpreter (CBV)
- Programming Languages: Hindley-Milner type inference (Algorithm W)
- Logic Programming: mini-Prolog (unification + backtracking)
- Theory: DFA minimization (Hopcroft's algorithm)

核心教材/论文：
- "Pierce Types and Programming Languages" 2002 MIT Press (lambda calc, HM)
- "Damas & Milner 1982 POPL" — Principal type-schemes (Hindley-Milner)
- "Hopcroft 1971" — n log n automaton minimization
- "Sipser Introduction to the Theory of Computation" (DFA minimization Ch 1)

本文件实现：
- Lambda calculus interpreter (call-by-value, Church numerals)
- Algorithm W (Hindley-Milner type inference)
- Mini-Prolog (unification + depth-first search)
- DFA minimization (Hopcroft partition refinement)

运行：
    python3 pl_fp.py
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

# ============ 1. Lambda Calculus Interpreter (CBV) ============

class Term: pass

@dataclass
class Var(Term):
    name: str

@dataclass
class Abs(Term):  # λx.body
    param: str
    body: Term

@dataclass
class App(Term):  # f x
    func: Term
    arg: Term

def free_vars(term: Term) -> set:
    if isinstance(term, Var):
        return {term.name}
    elif isinstance(term, Abs):
        return free_vars(term.body) - {term.param}
    elif isinstance(term, App):
        return free_vars(term.func) | free_vars(term.arg)

def substitute(term: Term, var: str, replacement: Term) -> Term:
    if isinstance(term, Var):
        return replacement if term.name == var else term
    elif isinstance(term, Abs):
        if term.param == var:
            return term  # shadowed
        if term.param in free_vars(replacement):
            # alpha-rename to avoid capture
            new_param = term.param + "'"
            renamed = substitute(term.body, term.param, Var(new_param))
            return Abs(new_param, substitute(renamed, var, replacement))
        return Abs(term.param, substitute(term.body, var, replacement))
    elif isinstance(term, App):
        return App(substitute(term.func, var, replacement),
                   substitute(term.arg, var, replacement))

def cbv_eval(term: Term, max_steps=1000) -> Term:
    """Call-by-value evaluation."""
    for _ in range(max_steps):
        if isinstance(term, Var):
            return term  # free var, can't reduce
        if isinstance(term, Abs):
            return term  # value
        if isinstance(term, App):
            # evaluate func first
            func = cbv_eval(term.func, max_steps)
            if isinstance(func, App):  # stuck
                return func
            if isinstance(func, Abs):
                arg = cbv_eval(term.arg, max_steps)
                if isinstance(arg, App):  # arg not a value
                    return App(func, arg)
                # beta-reduce
                term = substitute(func.body, func.param, arg)
            else:
                return App(func, term.arg)  # can't apply non-function
    return term

# Church numerals
church_zero = Abs('f', Abs('x', Var('x')))
church_succ = Abs('n', Abs('f', Abs('x', App(Var('f'), App(App(Var('n'), Var('f')), Var('x'))))))
church_add = Abs('m', Abs('n', Abs('f', Abs('x',
    App(App(Var('m'), Var('f')), App(App(Var('n'), Var('f')), Var('x')))))))

def church_to_term(n: int) -> Term:
    """n → λf.λx. f^n x"""
    body = Var('x')
    for _ in range(n):
        body = App(Var('f'), body)
    return Abs('f', Abs('x', body))

def term_to_church_int(term: Term) -> Optional[int]:
    """Extract integer from Church numeral (if possible)."""
    if not isinstance(term, Abs):
        return None
    inner = term.body  # λx. ...
    if not isinstance(inner, Abs):
        return None
    count = 0
    expr = inner.body
    while isinstance(expr, App):
        if isinstance(expr.func, Var) and expr.func.name == 'f':
            count += 1
            expr = expr.arg
        else:
            break
    if isinstance(expr, Var) and expr.name == 'x':
        return count
    return None


# ============ 2. Algorithm W (Hindley-Milner) ============

class Type: pass

@dataclass
class TVar(Type):
    name: str

@dataclass
class TCon(Type):
    name: str  # 'Int', 'Bool'
    args: list = None

@dataclass
class TArrow(Type):
    dom: Type
    cod: Type

fresh_counter = [0]
def fresh_var():
    fresh_counter[0] += 1
    return TVar(f't{fresh_counter[0]}')

def occurs(v: str, t: Type) -> bool:
    if isinstance(t, TVar):
        return t.name == v
    if isinstance(t, TArrow):
        return occurs(v, t.dom) or occurs(v, t.cod)
    return False

def apply_subst(subst: dict, t: Type) -> Type:
    if isinstance(t, TVar):
        return apply_subst(subst, subst[t.name]) if t.name in subst else t
    if isinstance(t, TArrow):
        return TArrow(apply_subst(subst, t.dom), apply_subst(subst, t.cod))
    return t

def unify(t1: Type, t2: Type, subst: dict) -> dict:
    t1, t2 = apply_subst(subst, t1), apply_subst(subst, t2)
    if isinstance(t1, TVar):
        if isinstance(t2, TVar) and t1.name == t2.name:
            return subst
        if occurs(t1.name, t2):
            raise TypeError(f"Occurs check fail: {t1.name} in {t2}")
        subst[t1.name] = t2
        return subst
    if isinstance(t2, TVar):
        return unify(t2, t1, subst)
    if isinstance(t1, TArrow) and isinstance(t2, TArrow):
        subst = unify(t1.dom, t2.dom, subst)
        return unify(t1.cod, t2.cod, subst)
    if isinstance(t1, TCon) and isinstance(t2, TCon) and t1.name == t2.name:
        return subst
    raise TypeError(f"Cannot unify {t1} with {t2}")

def infer(expr, env: dict, subst: dict) -> tuple:
    """Infer type of lambda expression. expr is parsed AST."""
    if isinstance(expr, str):  # variable
        if expr in env:
            return env[expr], subst
        raise TypeError(f"Unbound: {expr}")
    if isinstance(expr, tuple) and len(expr) == 3 and expr[0] == 'lambda':
        param, body = expr[1], expr[2]
        tv = fresh_var()
        new_env = dict(env)
        new_env[param] = tv
        body_type, subst = infer(body, new_env, subst)
        return TArrow(tv, body_type), subst
    if isinstance(expr, tuple) and len(expr) == 2:  # application
        func_type, subst = infer(expr[0], env, subst)
        arg_type, subst = infer(expr[1], env, subst)
        ret = fresh_var()
        subst = unify(func_type, TArrow(arg_type, ret), subst)
        return ret, subst
    raise TypeError(f"Cannot infer {expr}")


# ============ 3. Mini-Prolog (Unification + Backtracking) ============

def unify_terms(pattern, fact, bindings=None):
    """Unify two terms. Variables are strings starting with uppercase."""
    if bindings is None:
        bindings = {}
    # follow existing binding
    if isinstance(pattern, str) and pattern in bindings:
        pattern = bindings[pattern]
    if isinstance(fact, str) and fact in bindings:
        fact = bindings[fact]
    if isinstance(pattern, str) and pattern[0].isupper():
        bindings[pattern] = fact
        return bindings
    if isinstance(fact, str) and fact[0].isupper():
        bindings[fact] = pattern
        return bindings
    if pattern == fact:
        return bindings
    if isinstance(pattern, tuple) and isinstance(fact, tuple) and len(pattern) == len(fact):
        for p, f in zip(pattern, fact):
            bindings = unify_terms(p, f, bindings)
            if bindings is None:
                return None
        return bindings
    return None

class Prolog:
    def __init__(self):
        self.rules = []  # list of (head, body)

    def add_fact(self, fact):
        self.rules.append((fact, []))

    def add_rule(self, head, body):
        self.rules.append((head, body))

    def query(self, goal, depth=0, max_depth=20):
        """Depth-first search with backtracking. Returns list of solutions."""
        if depth > max_depth:
            return []
        solutions = []
        for head, body in self.rules:
            bindings = unify_terms(head, goal)
            if bindings is None:
                continue
            if not body:
                solutions.append(bindings)
            else:
                # solve each body goal
                sub_solutions = self._solve_body(body, bindings, depth, max_depth)
                solutions.extend(sub_solutions)
        return solutions

    def _solve_body(self, body, bindings, depth, max_depth):
        if not body:
            return [bindings]
        first = body[0]
        rest = body[1:]
        results = []
        sub_sols = self.query(first, depth+1, max_depth)
        for sol in sub_sols:
            combined = {**bindings, **sol}
            results.extend(self._solve_body(rest, combined, depth, max_depth))
        return results


# ============ 4. DFA Minimization (Hopcroft) ============

def minimize_dfa(states, alphabet, transitions, accept_states):
    """Hopcroft's partition refinement for DFA minimization.
    states: list of state IDs.
    transitions: dict (state, symbol) → state.
    accept_states: set of accepting states.
    """
    # Initial partition: {accept}, {reject}
    accept = set(accept_states)
    reject = set(states) - accept
    partitions = []
    if accept:
        partitions.append(frozenset(accept))
    if reject:
        partitions.append(frozenset(reject))

    changed = True
    while changed:
        changed = False
        new_partitions = []
        for P in partitions:
            # Try to split P by each symbol
            groups = {}
            for s in P:
                signature = []
                for sym in alphabet:
                    nxt = transitions.get((s, sym))
                    # find partition of next state
                    part_idx = -1
                    for i, other in enumerate(partitions):
                        if nxt in other:
                            part_idx = i
                            break
                    signature.append(part_idx)
                key = tuple(signature)
                groups.setdefault(key, set()).add(s)
            if len(groups) > 1:
                changed = True
            for g in groups.values():
                new_partitions.append(frozenset(g))
        partitions = new_partitions

    return partitions


# ============ Demo ============

def demo():
    print("=" * 60)
    print("15-150/312/251: Lambda Calc, HM, Prolog, DFA Min")
    print("=" * 60)

    # --- 1. Lambda Calculus ---
    print("\n📋 1. Lambda Calculus (CBV)")
    # 2 + 3 = 5 using Church numerals
    two = church_to_term(2)
    three = church_to_term(3)
    plus_expr = App(App(church_add, two), three)
    result = cbv_eval(plus_expr)
    result_int = term_to_church_int(result)
    print(f"   Church(2) + Church(3) = Church({result_int})")
    # succ(0) = 1
    one_expr = App(church_succ, church_zero)
    one = cbv_eval(one_expr)
    print(f"   succ(zero) = Church({term_to_church_int(one)})")
    print(f"   💡 λ-calculus 是 Turing-complete：数字/递归全用 λ 表示")

    # --- 2. Hindley-Milner ---
    print("\n📋 2. Hindley-Milner Type Inference (Algorithm W)")
    fresh_counter[0] = 0
    # λx. x  →  ∀α. α → α  (identity)
    id_type, _ = infer(('lambda', 'x', 'x'), {}, {})
    print(f"   λx.x : {id_type}")
    # λf.λx. f x  →  (α→β) → α → β
    apply_type, _ = infer(('lambda', 'f', ('lambda', 'x', ('f', 'x'))), {}, {})
    print(f"   λf.λx.f x : {apply_type}")
    # λx. x x → should fail (occurs check) in HM... actually needs recursion
    try:
        self_app, _ = infer(('lambda', 'x', ('x', 'x')), {}, {})
        print(f"   λx.x x : {self_app}")
    except TypeError as e:
        print(f"   λx.x x : TYPE ERROR ({e})")
    print(f"   💡 HM 自动推断多态类型，无需类型注解")

    # --- 3. Mini-Prolog ---
    print("\n📋 3. Mini-Prolog (Unification + Backtracking)")
    engine = Prolog()
    engine.add_fact(('parent', 'john', 'mary'))
    engine.add_fact(('parent', 'john', 'tom'))
    engine.add_fact(('parent', 'mary', 'alice'))
    engine.add_rule(('grandparent', 'X', 'Z'),
                    [('parent', 'X', 'Y'), ('parent', 'Y', 'Z')])
    # Query: grandparent(john, Who)?
    sols = engine.query(('grandparent', 'john', 'Who'))
    print(f"   Facts: parent(john,mary), parent(john,tom), parent(mary,alice)")
    print(f"   Rule:  grandparent(X,Z) :- parent(X,Y), parent(Y,Z)")
    print(f"   Query: grandparent(john, Who)?")
    for sol in sols:
        print(f"     → Who = {sol.get('Who', '?')}")
    print(f"   💡 Prolog 用 unification + DFS 自动链式推理")

    # --- 4. DFA Minimization ---
    print("\n📋 4. DFA Minimization (Hopcroft)")
    # DFA that accepts strings ending in '01'
    states = [0, 1, 2]
    alphabet = ['0', '1']
    transitions = {
        (0,'0'): 1, (0,'1'): 0,
        (1,'0'): 1, (1,'1'): 2,
        (2,'0'): 1, (2,'1'): 0,
    }
    accept = {2}
    # Add a redundant state (equivalent to state 0)
    states2 = [0, 1, 2, 3]  # state 3 mimics state 0
    transitions2 = dict(transitions)
    transitions2[(3,'0')] = 1
    transitions2[(3,'1')] = 0
    partitions = minimize_dfa(states2, alphabet, transitions2, accept)
    print(f"   DFA: 4 states, accepts strings ending in '01'")
    print(f"   States {{0,3}} should merge (both non-accept, same transitions)")
    print(f"   Minimized: {len(partitions)} equivalence classes")
    for i, p in enumerate(partitions):
        print(f"     Class {i}: {set(p)}")
    print(f"   💡 Hopcroft: {len(states2)} states → {len(partitions)} classes (minimal DFA)")

    print("\n✅ 15-150/312/251 PL/FP/Theory 完成！")
    print("   覆盖：λ-calculus (CBV) / HM Algorithm W / Mini-Prolog / DFA Minimization")


if __name__ == "__main__":
    demo()
