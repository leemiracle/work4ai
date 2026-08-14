"""
Compilers (Oxford CS)
================================================
覆盖主题：
- LL(1) 预测解析（FIRST/FOLLOW/FIRST+ 集合）
- LR(0) DFA 构造（项目集规范族，无 ACTION-GOTO 表）
- 语义分析（类型检查 + 符号表）
- 栈式虚拟机代码生成

核心教材（已核实）：
- Aho, Lam, Sethi, Ullman "Compilers: Principles, Techniques, and Tools" 2nd ed (Dragon Book), Pearson 2006
- Appel "Modern Compiler Implementation in ML" Cambridge 2004
- Grune & Jacobs "Parsing Techniques" 2nd ed, Springer 2008

本文件实现：
- LL(1) 解析器（含 FIRST/FOLLOW 计算）
- LR(0) 自动机构建
- 类型检查器（简单表达式）
- 栈式虚拟机代码生成

运行：
    python compilers.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict


# ============ 1. Grammar 定义 ============

@dataclass
class Grammar:
    """上下文无关文法"""
    terminals: set[str]
    nonterminals: set[str]
    productions: dict[str, list[list[str]]]  # NT -> [[symbol, ...], ...]
    start: str

    def __repr__(self):
        lines = [f"Grammar(start={self.start})"]
        for nt, prods in self.productions.items():
            for p in prods:
                lines.append(f"  {nt} → {' '.join(p) if p else 'ε'}")
        return "\n".join(lines)


# ============ 2. LL(1) 解析 ============

class LL1Parser:
    """LL(1) 预测解析器"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.first: dict[str, set[str]] = {}
        self.follow: dict[str, set[str]] = {}
        self.parse_table: dict[tuple[str, str], list[str]] = {}
        self._compute_first()
        self._compute_follow()
        self._build_table()

    def _compute_first(self):
        """计算 FIRST(X) 集合"""
        for t in self.grammar.terminals:
            self.first[t] = {t}
        for nt in self.grammar.nonterminals:
            self.first[nt] = set()

        changed = True
        while changed:
            changed = False
            for nt, prods in self.grammar.productions.items():
                for prod in prods:
                    if not prod:  # epsilon
                        if '' not in self.first[nt]:
                            self.first[nt].add('')
                            changed = True
                        continue
                    # FIRST(prod[0]) ⊆ FIRST(nt)（除非 prod[0] 能推出 ε）
                    for sym in prod:
                        add = self.first.get(sym, {sym}) - {''}
                        if add - self.first[nt]:
                            self.first[nt] |= add
                            changed = True
                        if '' not in self.first.get(sym, set()):
                            break
                    else:
                        # 所有符号都能推出 ε
                        if '' not in self.first[nt]:
                            self.first[nt].add('')
                            changed = True

    def _compute_follow(self):
        """计算 FOLLOW(X) 集合"""
        for nt in self.grammar.nonterminals:
            self.follow[nt] = set()
        self.follow[self.grammar.start].add('$')

        changed = True
        while changed:
            changed = False
            for nt, prods in self.grammar.productions.items():
                for prod in prods:
                    for i, sym in enumerate(prod):
                        if sym not in self.grammar.nonterminals:
                            continue
                        # FIRST(prod[i+1:]) - {ε} ⊆ FOLLOW(sym)
                        rest = prod[i+1:]
                        first_rest = set()
                        all_nullable = True
                        for s in rest:
                            fs = self.first.get(s, {s})
                            first_rest |= fs - {''}
                            if '' not in fs:
                                all_nullable = False
                                break
                        if first_rest - self.follow[sym]:
                            self.follow[sym] |= first_rest
                            changed = True
                        if all_nullable:
                            if self.follow[nt] - self.follow[sym]:
                                self.follow[sym] |= self.follow[nt]
                                changed = True

    def _first_of_string(self, symbols: list[str]) -> set[str]:
        """FIRST(α) where α is a string of symbols"""
        result = set()
        for sym in symbols:
            fs = self.first.get(sym, {sym})
            result |= fs - {''}
            if '' not in fs:
                return result
        result.add('')
        return result

    def _build_table(self):
        """构建 LL(1) 预测分析表"""
        for nt, prods in self.grammar.productions.items():
            for prod in prods:
                first_alpha = self._first_of_string(prod) - {''}
                for t in first_alpha:
                    self.parse_table[(nt, t)] = prod
                if '' in self._first_of_string(prod):
                    for t in self.follow[nt]:
                        self.parse_table[(nt, t)] = prod

    def parse(self, tokens: list[str]) -> bool:
        """LL(1) 预测解析"""
        stack = [self.grammar.start, '$']
        stack.reverse()  # ['$', start]
        input_stream = tokens + ['$']
        pos = 0

        steps = []
        while stack:
            top = stack.pop()
            cur = input_stream[pos]
            if top == '$':
                return cur == '$'
            if top in self.grammar.terminals:
                if top == cur:
                    pos += 1
                else:
                    return False  # error
            else:
                key = (top, cur)
                if key not in self.parse_table:
                    return False  # error
                prod = self.parse_table[key]
                # push production in reverse
                for sym in reversed(prod):
                    stack.append(sym)
                steps.append((top, prod, cur))

        return pos == len(input_stream) - 1

    def is_ll1(self) -> bool:
        """检查文法是否是 LL(1)（无冲突）"""
        # 每个 (NT, terminal) 只有一个 production
        return True  # build_table 会覆盖，冲突在此简化中不检测


# ============ 3. LR(0) 自动机 ============

class LR0Parser:
    """LR(0) 项目集规范族构建"""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states: list[frozenset] = []
        self.transitions: dict[tuple[frozenset, str], frozenset] = {}

    def _closure(self, items: set) -> frozenset:
        """LR(0) 闭包"""
        changed = True
        items = set(items)
        while changed:
            changed = False
            for nt, pos, prod in list(items):
                if pos < len(prod):
                    sym = prod[pos]
                    if sym in self.grammar.nonterminals:
                        for p in self.grammar.productions.get(sym, []):
                            new_item = (sym, 0, tuple(p))
                            if new_item not in items:
                                items.add(new_item)
                                changed = True
        return frozenset(items)

    def _goto(self, items: frozenset, symbol: str) -> frozenset:
        """GOTO(I, X)"""
        moved = set()
        for nt, pos, prod in items:
            if pos < len(prod) and prod[pos] == symbol:
                moved.add((nt, pos + 1, prod))
        if not moved:
            return frozenset()
        return self._closure(moved)

    def build_dfa(self):
        """构建 LR(0) DFA（增广开始符 S'→S，确保初始状态含 start 全部产生式）"""
        # 增广：引入 S'→S，CLOSURE({S'→•S}) 自然纳入 start 的全部产生式
        augmented_start = self.grammar.start + "'"
        start_item = (augmented_start, 0, (self.grammar.start,))
        initial = self._closure({start_item})
        self.states = [initial]

        queue = [initial]
        while queue:
            state = queue.pop(0)
            # 所有可能的转移符号
            symbols = set()
            for nt, pos, prod in state:
                if pos < len(prod):
                    symbols.add(prod[pos])

            for sym in symbols:
                nxt = self._goto(state, sym)
                if nxt and nxt not in self.states:
                    self.states.append(nxt)
                    queue.append(nxt)
                if nxt:
                    self.transitions[(state, sym)] = nxt


# ============ 4. 语义分析（类型检查） ============

@dataclass
class TypeChecker:
    """简单表达式类型检查器"""

    def __init__(self):
        self.symbol_table: dict[str, str] = {}  # var -> type

    def declare(self, name: str, typ: str):
        self.symbol_table[name] = typ

    def check(self, expr) -> str:
        """检查表达式类型。
        expr = ('num', value) | ('var', name) | ('binop', op, left, right)
        """
        if expr[0] == 'num':
            return 'int'
        if expr[0] == 'var':
            name = expr[1]
            if name not in self.symbol_table:
                raise TypeError(f"Undeclared variable: {name}")
            return self.symbol_table[name]
        if expr[0] == 'binop':
            _, op, left, right = expr
            lt = self.check(left)
            rt = self.check(right)
            if op in ['+', '-', '*', '/']:
                if lt != 'int' or rt != 'int':
                    raise TypeError(f"Arithmetic on non-int: {lt} {op} {rt}")
                return 'int'
            if op in ['<', '>', '==', '!=']:
                if lt != rt:
                    raise TypeError(f"Comparison of different types: {lt} {op} {rt}")
                return 'bool'
        raise TypeError(f"Unknown expr: {expr}")


# ============ 5. 栈式代码生成 ============

class CodeGen:
    """为简单表达式生成栈式虚拟机代码"""

    def __init__(self):
        self.code: list[str] = []
        self.temp_count = 0

    def gen(self, expr) -> list[str]:
        """递归生成代码"""
        if expr[0] == 'num':
            self.code.append(f"PUSH {expr[1]}")
        elif expr[0] == 'var':
            self.code.append(f"LOAD {expr[1]}")
        elif expr[0] == 'binop':
            _, op, left, right = expr
            self.gen(left)
            self.gen(right)
            self.code.append(f"OP {op}")
        return self.code

    def to_asm(self) -> str:
        return "\n".join(f"  {i}: {inst}" for i, inst in enumerate(self.code))


def execute_stack_vm(code: list[str]) -> int:
    """执行栈式 VM 代码"""
    stack = []
    vars_store = {'x': 10, 'y': 20}
    for inst in code:
        parts = inst.split()
        if parts[0] == 'PUSH':
            stack.append(int(parts[1]))
        elif parts[0] == 'LOAD':
            stack.append(vars_store.get(parts[1], 0))
        elif parts[0] == 'OP':
            b = stack.pop()
            a = stack.pop()
            op = parts[1]
            if op == '+': stack.append(a + b)
            elif op == '-': stack.append(a - b)
            elif op == '*': stack.append(a * b)
            elif op == '/': stack.append(a // b)
    return stack[-1] if stack else 0


# ============ Main Demo ============

def main():
    print("=" * 65)
    print("Compilers (Oxford CS) Demo")
    print("=" * 65)

    # 1. LL(1) Parser
    print("\n📋 1. LL(1) 解析器")

    # 文法: E → T E'
    #         E' → + T E' | ε
    #         T → F T'
    #         T' → * F T' | ε
    #         F → ( E ) | id
    grammar = Grammar(
        terminals={'id', '(', ')', '+', '*', '$'},
        nonterminals={'E', "E'", 'T', "T'", 'F'},
        productions={
            'E': [['T', "E'"]],
            "E'": [['+', 'T', "E'"], []],
            'T': [['F', "T'"]],
            "T'": [['*', 'F', "T'"], []],
            'F': [['(', 'E', ')'], ['id']],
        },
        start='E'
    )
    print("   文法:")
    print(f"   {grammar}")

    parser = LL1Parser(grammar)
    print(f"\n   FIRST 集合:")
    for nt in ['E', "E'", 'T', "T'", 'F']:
        print(f"     FIRST({nt}) = {parser.first[nt]}")
    print(f"\n   FOLLOW 集合:")
    for nt in ['E', "E'", 'T', "T'", 'F']:
        print(f"     FOLLOW({nt}) = {parser.follow[nt]}")

    # 解析 id + id * id
    tokens = ['id', '+', 'id', '*', 'id']
    result = parser.parse(tokens)
    print(f"\n   解析 '{' '.join(tokens)}': {'成功 ✓' if result else '失败 ✗'}")

    # 2. LR(0)
    print("\n📋 2. LR(0) 自动机")

    # 简化文法: S → S S | ( S ) | ( )
    lr0_grammar = Grammar(
        terminals={'(', ')'},
        nonterminals={'S'},
        productions={
            'S': [['(', 'S', ')'], ['(', ')']],
        },
        start='S'
    )
    lr0 = LR0Parser(lr0_grammar)
    lr0.build_dfa()
    print(f"   LR(0) 状态数: {len(lr0.states)}")
    for i, state in enumerate(lr0.states[:4]):
        items = [(nt, pos, prod) for nt, pos, prod in sorted(state)]
        print(f"   State {i}: {items[:3]}{'...' if len(items) > 3 else ''}")

    # 3. 类型检查
    print("\n📋 3. 语义分析：类型检查")
    tc = TypeChecker()
    tc.declare('x', 'int')
    tc.declare('y', 'int')

    expr1 = ('binop', '+', ('var', 'x'), ('var', 'y'))
    typ = tc.check(expr1)
    print(f"   x + y : {typ}")

    expr2 = ('binop', '<', ('binop', '+', ('var', 'x'), ('num', 1)), ('var', 'y'))
    typ2 = tc.check(expr2)
    print(f"   (x + 1) < y : {typ2}")

    # 类型错误
    tc.declare('flag', 'bool')
    try:
        tc.check(('binop', '+', ('var', 'flag'), ('num', 1)))
    except TypeError as e:
        print(f"   flag + 1 : TypeError → {e}")

    # 4. 代码生成
    print("\n📋 4. 代码生成（栈式 VM）")
    cg = CodeGen()
    expr = ('binop', '+', ('binop', '*', ('var', 'x'), ('num', 2)), ('var', 'y'))
    # x*2 + y
    code = cg.gen(expr)
    print(f"   表达式: x*2 + y")
    print(f"   生成的代码:")
    print(f"   {cg.to_asm()}")
    result = execute_stack_vm(code)
    print(f"   执行结果 (x=10, y=20): {result}")

    # 反直觉总结
    print("\n" + "=" * 65)
    print("💡 反直觉发现：")
    print(f"   1. 'id+id*id' 被LL(1)正确解析为 id+(id*id) 而非 (id+id)*id")
    print(f"      —— 文法设计隐含了运算符优先级（不需要额外规则）")
    print(f"   2. 类型检查器拒绝了 flag+1（bool+int）")
    print(f"      —— 类型系统在编译期发现错误，而非运行时崩溃")
    print(f"   3. 栈式VM只需3条指令(PUSH/LOAD/OP)就能计算任意表达式")
    print(f"      x*2+y 生成5条指令，结果={result}")
    print("=" * 65)


if __name__ == "__main__":
    main()
