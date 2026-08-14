"""
Part IB Compiler Construction (Cambridge CST)
=============================================
覆盖主题：
- 词法分析（lexer / scanner）
- 递归下降解析器（recursive-descent parser）
- 抽象语法树（AST）
- 类型检查（type checker）
- 栈机代码生成

核心教材：
- Aho, Lam, Sethi & Ullman 2006 "Compilers: Principles, Techniques,
  and Tools" 2nd ed (Dragon Book), Addison-Wesley
- Appel 2004 "Modern Compiler Implementation in ML/C/Java"
- Wirth 1996 "Compiler Construction" Addison-Wesley

本文件实现：
- Lexer: 源码 → token 流
- Parser: 递归下降 → AST（表达式 + 语句 + 赋值）
- TypeChecker: AST → 类型（int / bool / type error）
- CodeGen: AST → 栈机指令序列
- StackMachine VM: 执行生成的代码

运行：
    python compiler.py
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# ================================================================
# 1. Lexer
# ================================================================

@dataclass
class Token:
    type: str    # NUMBER, IDENT, OP, KW, EOF
    value: str
    pos: int

KEYWORDS = {"let", "if", "else", "while", "true", "false", "print"}

def lex(source: str) -> list[Token]:
    tokens = []
    i = 0
    while i < len(source):
        c = source[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < len(source) and source[j].isdigit():
                j += 1
            tokens.append(Token("NUMBER", source[i:j], i))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < len(source) and (source[j].isalnum() or source[j] == '_'):
                j += 1
            word = source[i:j]
            tokens.append(Token("KW" if word in KEYWORDS else "IDENT", word, i))
            i = j
            continue
        if source[i:i+2] in ("==", "<=", ">=", "!=", "&&", "||"):
            tokens.append(Token("OP", source[i:i+2], i))
            i += 2
            continue
        if c in "+-*/(){}=<>!;,":
            tokens.append(Token("OP", c, i))
            i += 1
            continue
        raise SyntaxError(f"Unknown char {c!r} at {i}")
    tokens.append(Token("EOF", "", len(source)))
    return tokens


# ================================================================
# 2. AST 节点
# ================================================================

@dataclass
class Num: value: int
@dataclass
class Bool: value: bool
@dataclass
class Var: name: str
@dataclass
class BinOp:
    op: str; left: object; right: object
@dataclass
class UnaryOp:
    op: str; operand: object
@dataclass
class Assign:
    name: str; value: object
@dataclass
class Let:
    name: str; value: object
@dataclass
class If:
    cond: object; then_body: list; else_body: list
@dataclass
class While:
    cond: object; body: list
@dataclass
class Print:
    expr: object
@dataclass
class Block:
    stmts: list


# ================================================================
# 3. 递归下降 Parser
# ================================================================

class Parser:
    """文法:
    stmt  := let IDENT = expr | IDENT = expr | if (expr) block [else block]
           | while (expr) block | print (expr) | block
    block := { stmt* }
    expr  := or_expr
    or    := and (|| and)*
    and   := cmp (&& cmp)*
    cmp   := add ((==|!=|<|>|<=|>=) add)?
    add   := mul ((+|-) mul)*
    mul   := unary ((*|/) unary)*
    unary := (!|-)unary | atom
    atom  := NUMBER | true | false | IDENT | (expr)
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t
    def expect(self, val):
        t = self.advance()
        if t.value != val:
            raise SyntaxError(f"Expected {val!r}, got {t.value!r}")
        return t

    def parse(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.parse_stmt())
        return Block(stmts)

    def parse_stmt(self):
        t = self.peek()
        if t.type == "KW" and t.value == "let":
            self.advance()
            name = self.advance().value
            self.expect("=")
            val = self.parse_expr()
            return Let(name, val)
        if t.type == "KW" and t.value == "if":
            self.advance()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            then_b = self.parse_block()
            else_b = []
            if self.peek().type == "KW" and self.peek().value == "else":
                self.advance()
                else_b = self.parse_block()
            return If(cond, then_b, else_b)
        if t.type == "KW" and t.value == "while":
            self.advance()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            body = self.parse_block()
            return While(cond, body)
        if t.type == "KW" and t.value == "print":
            self.advance()
            self.expect("(")
            expr = self.parse_expr()
            self.expect(")")
            return Print(expr)
        if t.value == "{":
            return self.parse_block()
        if t.type == "IDENT":
            name = self.advance().value
            self.expect("=")
            val = self.parse_expr()
            return Assign(name, val)
        raise SyntaxError(f"Unexpected token {t}")

    def parse_block(self):
        self.expect("{")
        stmts = []
        while self.peek().value != "}":
            stmts.append(self.parse_stmt())
        self.expect("}")
        return Block(stmts)

    def parse_expr(self): return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek().value == "||":
            self.advance()
            right = self.parse_and()
            left = BinOp("||", left, right)
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.peek().value == "&&":
            self.advance()
            right = self.parse_cmp()
            left = BinOp("&&", left, right)
        return left

    def parse_cmp(self):
        left = self.parse_add()
        if self.peek().value in ("==", "!=", "<", ">", "<=", ">="):
            op = self.advance().value
            right = self.parse_add()
            return BinOp(op, left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().value in ("*", "/"):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.peek().value in ("!", "-"):
            op = self.advance().value
            return UnaryOp(op, self.parse_unary())
        return self.parse_atom()

    def parse_atom(self):
        t = self.advance()
        if t.type == "NUMBER":
            return Num(int(t.value))
        if t.type == "KW" and t.value == "true":
            return Bool(True)
        if t.type == "KW" and t.value == "false":
            return Bool(False)
        if t.type == "IDENT":
            return Var(t.value)
        if t.value == "(":
            e = self.parse_expr()
            self.expect(")")
            return e
        raise SyntaxError(f"Unexpected atom {t}")


# ================================================================
# 4. Type Checker
# ================================================================

class TypeChecker:
    def __init__(self):
        self.env = {}
        self.errors = []

    def check(self, node):
        if isinstance(node, Num): return "int"
        if isinstance(node, Bool): return "bool"
        if isinstance(node, Var):
            if node.name not in self.env:
                self.errors.append(f"Undefined var: {node.name}")
                return "error"
            return self.env[node.name]
        if isinstance(node, UnaryOp):
            t = self.check(node.operand)
            if node.op == "!" and t != "bool":
                self.errors.append(f"! expects bool, got {t}")
            if node.op == "-" and t != "int":
                self.errors.append(f"- expects int, got {t}")
            return "bool" if node.op == "!" else "int"
        if isinstance(node, BinOp):
            lt = self.check(node.left)
            rt = self.check(node.right)
            if node.op in ("+", "-", "*", "/"):
                if lt != "int" or rt != "int":
                    self.errors.append(f"{node.op} needs int, got {lt},{rt}")
                return "int"
            if node.op in ("&&", "||"):
                if lt != "bool" or rt != "bool":
                    self.errors.append(f"{node.op} needs bool")
                return "bool"
            if node.op in ("==", "!=", "<", ">", "<=", ">="):
                if lt != rt:
                    self.errors.append(f"{node.op} type mismatch {lt} vs {rt}")
                return "bool"
        if isinstance(node, Let):
            t = self.check(node.value)
            self.env[node.name] = t
            return t
        if isinstance(node, Assign):
            if node.name not in self.env:
                self.errors.append(f"Assign to undefined: {node.name}")
                return "error"
            t = self.check(node.value)
            if t != self.env[node.name]:
                self.errors.append(f"Type mismatch assign {node.name}")
            return t
        return "void"


# ================================================================
# 5. 栈机代码生成
# ================================================================

class CodeGen:
    """生成栈机指令: PUSH n, LOAD var, STORE var,
    ADD/SUB/MUL/DIV, EQ/LT/GT, JMP/JZ/JNZ, PRINT

    注意: && 和 || 目前生成位运算 (AND/OR)，未实现短路求值。
    标准短路求值需用 JZ/JNZ 跳过右操作数求值。"""

    def __init__(self):
        self.code = []

    def gen(self, node):
        if isinstance(node, Num):
            self.code.append(("PUSH", node.value))
        elif isinstance(node, Bool):
            self.code.append(("PUSH", 1 if node.value else 0))
        elif isinstance(node, Var):
            self.code.append(("LOAD", node.name))
        elif isinstance(node, BinOp):
            self.gen(node.left)
            self.gen(node.right)
            op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV",
                      "==": "EQ", "!=": "NE", "<": "LT", ">": "GT",
                      "<=": "LE", ">=": "GE", "&&": "AND", "||": "OR"}
            self.code.append((op_map.get(node.op, "ADD"),))
        elif isinstance(node, UnaryOp):
            self.gen(node.operand)
            if node.op == "-":
                self.code.append(("NEG",))
            elif node.op == "!":
                self.code.append(("NOT",))
        elif isinstance(node, (Let, Assign)):
            self.gen(node.value)
            self.code.append(("STORE", node.name))
        elif isinstance(node, Print):
            self.gen(node.expr)
            self.code.append(("PRINT",))
        elif isinstance(node, Block):
            for s in node.stmts:
                self.gen(s)
        elif isinstance(node, If):
            self.gen(node.cond)
            jz_addr = len(self.code)
            self.code.append(("JZ", None))  # placeholder
            self.gen(Block(node.then_body))
            if node.else_body:
                jmp_addr = len(self.code)
                self.code.append(("JMP", None))
                self.code[jz_addr] = ("JZ", len(self.code))
                self.gen(Block(node.else_body))
                self.code[jmp_addr] = ("JMP", len(self.code))
            else:
                self.code[jz_addr] = ("JZ", len(self.code))
        elif isinstance(node, While):
            start_addr = len(self.code)
            self.gen(node.cond)
            jz_addr = len(self.code)
            self.code.append(("JZ", None))  # placeholder: cond false → exit
            self.gen(node.body)             # body 已是 Block（parse_block 返回）
            self.code.append(("JMP", start_addr))  # loop back to cond
            self.code[jz_addr] = ("JZ", len(self.code))  # backpatch exit target
        return self.code


class StackVM:
    """执行栈机指令"""

    def run(self, code):
        stack = []
        env = {}
        pc = 0
        output = []
        while pc < len(code):
            inst = code[pc]
            op = inst[0]
            if op == "PUSH": stack.append(inst[1])
            elif op == "LOAD": stack.append(env.get(inst[1], 0))
            elif op == "STORE": env[inst[1]] = stack.pop()
            elif op == "ADD": b=stack.pop(); a=stack.pop(); stack.append(a+b)
            elif op == "SUB": b=stack.pop(); a=stack.pop(); stack.append(a-b)
            elif op == "MUL": b=stack.pop(); a=stack.pop(); stack.append(a*b)
            elif op == "DIV": b=stack.pop(); a=stack.pop(); stack.append(a//b)
            elif op == "NEG": stack.append(-stack.pop())
            elif op == "EQ": b=stack.pop(); a=stack.pop(); stack.append(int(a==b))
            elif op == "NE": b=stack.pop(); a=stack.pop(); stack.append(int(a!=b))
            elif op == "LT": b=stack.pop(); a=stack.pop(); stack.append(int(a<b))
            elif op == "GT": b=stack.pop(); a=stack.pop(); stack.append(int(a>b))
            elif op == "LE": b=stack.pop(); a=stack.pop(); stack.append(int(a<=b))
            elif op == "GE": b=stack.pop(); a=stack.pop(); stack.append(int(a>=b))
            elif op == "AND": b=stack.pop(); a=stack.pop(); stack.append(a&b)
            elif op == "OR": b=stack.pop(); a=stack.pop(); stack.append(a|b)
            elif op == "NOT": stack.append(1-stack.pop())
            elif op == "JZ":
                if stack.pop() == 0: pc = inst[1]; continue
            elif op == "JMP": pc = inst[1]; continue
            elif op == "PRINT": output.append(str(stack[-1]))
            pc += 1
        return env, output


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB Compiler Construction — Demo")
    print("=" * 64)

    source = """
    let x = 10
    let y = 0
    let i = 1
    while (i <= x) {
        y = y + i
        i = i + 1
    }
    print(y)
    """

    print("\n📋 1. 源代码:")
    for line in source.strip().split('\n'):
        print(f"   {line.strip()}")

    # 2. Lex
    print("\n📋 2. Lexer → Token 流")
    tokens = lex(source)
    for t in tokens[:12]:
        print(f"   {t.type:8s} {t.value}")
    print(f"   ... 共 {len(tokens)} tokens")

    # 3. Parse
    print("\n📋 3. Parser → AST")
    ast = Parser(tokens).parse()
    print(f"   顶层 Block, {len(ast.stmts)} 条语句")
    print(f"   stmt[0]: {ast.stmts[0]}")
    print(f"   stmt[3]: While(...)")

    # 4. Type check
    print("\n📋 4. Type Checker")
    tc = TypeChecker()
    for stmt in ast.stmts:
        tc.check(stmt)
    print(f"   类型环境: {tc.env}")
    print(f"   类型错误: {len(tc.errors)}")

    # 5. Code gen + VM
    print("\n📋 5. CodeGen + StackVM 执行")
    code = CodeGen().gen(ast)
    print(f"   生成 {len(code)} 条栈机指令")
    print(f"   前 8 条: {code[:8]}")
    env, output = StackVM().run(code)
    print(f"   运行后环境: x={env.get('x')}, y={env.get('y')}, i={env.get('i')}")
    print(f"   输出 (print): {output}")
    print(f"   → 1+2+...+10 = {output[0] if output else '?'}")

    # 6. 类型错误演示
    print("\n📋 6. 类型错误检测")
    bad_source = "let a = true + 3"
    bad_ast = Parser(lex(bad_source)).parse()
    bad_tc = TypeChecker()
    for stmt in bad_ast.stmts:
        bad_tc.check(stmt)
    print(f"   源码: {bad_source}")
    print(f"   错误: {bad_tc.errors}")

    print("\n✅ Compiler Construction 完成！")
    print("\n💡 反直觉发现：")
    print("   - 递归下降天然映射运算符优先级（or→and→cmp→add→mul→unary→atom）")
    print("   - 栈机只有 PUSH/LOAD/STORE/OP/JMP 几类指令，却能编译任意程序")
    print("   - 类型检查在编译期完成，运行时零开销")


if __name__ == "__main__":
    demo()
