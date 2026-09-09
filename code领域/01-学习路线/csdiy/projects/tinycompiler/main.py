#!/usr/bin/env python3
"""
tinycompiler — 参照 craftinginterpreters 的 Lox 解释器

参照：Crafting Interpreters (Bob Nystrom) + Lua
csdiy 对应：CS143 编译器 + csapp Ch3(解析/汇编)

核心：Lexer → Parser(AST) → Interpreter(树遍历求值)
支持：变量、算术、if/else、while、函数、闭包
"""
import sys, re
from dataclasses import dataclass
from typing import Any, Optional, Union

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Token + Lexer（参照 Crafting Interpreters Ch4-6）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEYWORDS = {"var","fun","if","else","while","for","true","false","nil","return","and","or","print"}

@dataclass
class Token:
    type: str; value: Any; line: int

class Lexer:
    """词法分析器（参照 Lox scanner）"""
    def __init__(self, src): self.src=src; self.pos=0; self.line=1
    def error(self,msg): raise SyntaxError(f"Lexer error (line {self.line}): {msg}")
    def tokenize(self):
        tokens=[]
        while self.pos<len(self.src):
            c=self.src[self.pos]
            if c=='\n': self.line+=1; self.pos+=1
            elif c in ' \t\r': self.pos+=1
            elif c=='/' and self._peek(1)=='/':
                while self.pos<len(self.src) and self.src[self.pos]!='\n': self.pos+=1
            elif c.isdigit(): tokens.append(self._number())
            elif c.isalpha() or c=='_': tokens.append(self._identifier())
            elif c=='"': tokens.append(self._string())
            elif c in '+-*/(){};,=<>()!': tokens.append(self._symbol())
            else: self.error(f"Unexpected '{c}'")
        tokens.append(Token("EOF",None,self.line))
        return tokens
    def _peek(self,n=0): return self.src[self.pos+n] if self.pos+n<len(self.src) else '\0'
    def _number(self):
        start=self.pos
        while self.pos<len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos]=='.'): self.pos+=1
        return Token("NUMBER",float(self.src[start:self.pos]),self.line)
    def _identifier(self):
        start=self.pos
        while self.pos<len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos]=='_'): self.pos+=1
        word=self.src[start:self.pos]
        if word in KEYWORDS: return Token(word.upper(),word,self.line)
        return Token("IDENT",word,self.line)
    def _string(self):
        self.pos+=1; start=self.pos
        while self.pos<len(self.src) and self.src[self.pos]!='"': self.pos+=1
        if self.pos>=len(self.src): self.error("Unterminated string")
        val=self.src[start:self.pos]; self.pos+=1
        return Token("STRING",val,self.line)
    def _symbol(self):
        c=self.src[self.pos]; self.pos+=1
        two=self.src[self.pos-1:self.pos+1]
        if two in ('==','!=','<=','>='): self.pos+=1; return Token(two,two,self.line)
        return Token(c,c,self.line)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AST（参照 Lox AST）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Num: value: float
@dataclass
class Str: value: str
@dataclass
class Bool: value: bool
@dataclass
class Nil: pass
@dataclass
class Var: name: str
@dataclass
class Assign: name: str; value: Any
@dataclass
class Binary: left: Any; op: str; right: Any
@dataclass
class Unary: op: str; right: Any
@dataclass
class Logical: left: Any; op: str; right: Any
@dataclass
class Call: callee: Any; args: list
@dataclass
class ExprStmt: expr: Any
@dataclass
class Print: expr: Any
@dataclass
class VarDecl: name: str; init: Any
@dataclass
class Block: stmts: list
@dataclass
class If: cond: Any; then: Any; els: Any
@dataclass
class While: cond: Any; body: Any
@dataclass
class FunDecl: name: str; params: list; body: list
@dataclass
class Return: value: Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Parser（递归下降，参照 Lox parser）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Parser:
    """Pratt parser（参照 Crafting Interpreters Ch8）"""
    def __init__(self,tokens): self.tokens=tokens; self.pos=0
    def peek(self): return self.tokens[self.pos]
    def advance(self): t=self.tokens[self.pos]; self.pos+=1; return t
    def check(self,t): return self.peek().type==t
    def match(self,*types):
        if self.peek().type in types: return self.advance()
        return None
    def error(self,msg): raise SyntaxError(f"Parse error (line {self.peek().line}): {msg}")

    def parse(self):
        stmts=[]
        while not self.check("EOF"): stmts.append(self.statement())
        return stmts

    def statement(self):
        if self.match("VAR"): stmt=self.var_decl()
        elif self.match("PRINT"): stmt=Print(self.expression())
        elif self.match("IF"): return self.if_stmt()
        elif self.match("WHILE"): return self.while_stmt()
        elif self.match("FUN"): return self.fun_decl()
        elif self.match("RETURN"): stmt=Return(self.expression() if not self.check(";") else Nil())
        elif self.match("{"): return Block(self.block())
        else: stmt=ExprStmt(self.expression())
        self.match(";")  # 消费可选的分号
        return stmt

    def var_decl(self):
        name=self.advance().value
        init=Nil()
        if self.match("="): init=self.expression()
        return VarDecl(name,init)

    def if_stmt(self):
        cond=self.expression()
        then=self.statement()
        els=None
        if self.match("ELSE"): els=self.statement()
        return If(cond,then,els)

    def while_stmt(self):
        cond=self.expression()
        body=self.statement()
        return While(cond,body)

    def fun_decl(self):
        name=self.advance().value
        params=[]
        if self.match("("):
            if not self.check(")"):
                params.append(self.advance().value)
                while self.match(","): params.append(self.advance().value)
            if not self.match(")"): self.error("Expected ')' after params")
        if not self.match("{"): self.error("Expected '{' before function body")
        return FunDecl(name,params,self.block())

    def block(self):
        stmts=[]
        while not self.check("}") and not self.check("EOF"): stmts.append(self.statement())
        if not self.match("}"): self.error("Expected '}' after block")
        return stmts

    def expression(self): return self.assignment()
    def assignment(self):
        expr=self.logic_or()
        if self.match("="):
            val=self.assignment()
            if isinstance(expr,Var): return Assign(expr.name,val)
            self.error("Invalid assignment target")
        return expr
    def logic_or(self):
        left=self.logic_and()
        while op:=self.match("OR"):
            left=Logical(left,"or",self.logic_and())
        return left
    def logic_and(self):
        left=self.equality()
        while op:=self.match("AND"):
            left=Logical(left,"and",self.equality())
        return left
    def equality(self):
        left=self.comparison()
        while op:=self.match("==","!="): left=Binary(left,op.type,self.comparison())
        return left
    def comparison(self):
        left=self.term()
        while op:=self.match("<",">","<=",">="): left=Binary(left,op.type,self.term())
        return left
    def term(self):
        left=self.factor()
        while op:=self.match("+","-"): left=Binary(left,op.type,self.factor())
        return left
    def factor(self):
        left=self.unary()
        while op:=self.match("*","/"): left=Binary(left,op.type,self.unary())
        return left
    def unary(self):
        if op:=self.match("-","!"): return Unary(op.type,self.unary())
        return self.call()
    def call(self):
        expr=self.primary()
        while self.match("("):
            args=[]
            if not self.check(")"):
                args.append(self.expression())
                while self.match(","): args.append(self.expression())
            if not self.match(")"): self.error("Expected ')'")
            expr=Call(expr,args)
        return expr
    def primary(self):
        if t:=self.match("NUMBER"): return Num(t.value)
        if t:=self.match("STRING"): return Str(t.value)
        if t:=self.match("TRUE"): return Bool(True)
        if t:=self.match("FALSE"): return Bool(False)
        if t:=self.match("NIL"): return Nil()
        if t:=self.match("IDENT"): return Var(t.value)
        if self.match("("):
            e=self.expression()
            if not self.match(")"): self.error("Expected ')'")
            return e
        self.error(f"Unexpected '{self.peek().value}'")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Interpreter（树遍历求值，参照 Lox interpreter）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Environment:
    """作用域（参照 Lox Environment）"""
    def __init__(self,parent=None): self.vars={}; self.parent=parent
    def get(self,name):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'")
    def set(self,name,val):
        if name in self.vars: self.vars[name]=val; return
        if self.parent: self.parent.set(name,val); return
        raise NameError(f"Undefined variable '{name}'")
    def define(self,name,val): self.vars[name]=val

class ReturnException(Exception):
    def __init__(self,value): self.value=value

class LoxFunction:
    def __init__(self,decl,closure): self.decl=decl; self.closure=closure
    def call(self,interpreter,args):
        env=Environment(self.closure)
        for p,a in zip(self.decl.params,args): env.define(p,a)
        try:
            for s in self.decl.body: interpreter.execute(s,env)
        except ReturnException as r:
            return r.value
        return None

class Interpreter:
    def __init__(self):
        self.globals=Environment()
        self._install_builtins()
    def _install_builtins(self):
        import math
        self.globals.define("clock",lambda *a: __import__("time").time())
        self.globals.define("len",lambda *a: len(a[0]) if a else 0)
        self.globals.define("abs",lambda *a: abs(a[0]))
        self.globals.define("max",lambda *a: max(a))
        self.globals.define("min",lambda *a: min(a))
    def run(self,stmts):
        for s in stmts: self.execute(s,self.globals)
    def execute(self,stmt,env):
        if isinstance(stmt,ExprStmt): self.eval(stmt.expr,env)
        elif isinstance(stmt,Print): print(self._fmt(self.eval(stmt.expr,env)))
        elif isinstance(stmt,VarDecl): env.define(stmt.name,self.eval(stmt.init,env))
        elif isinstance(stmt,Block):
            for s in stmt.stmts: self.execute(s,Environment(env))
        elif isinstance(stmt,If):
            if self._truthy(self.eval(stmt.cond,env)): self.execute(stmt.then,env)
            elif stmt.els: self.execute(stmt.els,env)
        elif isinstance(stmt,While):
            while self._truthy(self.eval(stmt.cond,env)): self.execute(stmt.body,env)
        elif isinstance(stmt,FunDecl):
            env.define(stmt.name,LoxFunction(stmt,env))
        elif isinstance(stmt,Return):
            raise ReturnException(self.eval(stmt.value,env) if stmt.value else None)
    def eval(self,expr,env):
        if isinstance(expr,Num): return expr.value
        if isinstance(expr,Str): return expr.value
        if isinstance(expr,Bool): return expr.value
        if isinstance(expr,Nil): return None
        if isinstance(expr,Var): return env.get(expr.name)
        if isinstance(expr,Assign): val=self.eval(expr.value,env); env.set(expr.name,val); return val
        if isinstance(expr,Binary): return self._binary(expr,env)
        if isinstance(expr,Unary):
            v=self.eval(expr.right,env)
            if expr.op=="-": return -v
            if expr.op=="!": return not self._truthy(v)
        if isinstance(expr,Logical):
            l=self.eval(expr.left,env)
            if expr.op=="and": return self.eval(expr.right,env) if self._truthy(l) else l
            if expr.op=="or": return l if self._truthy(l) else self.eval(expr.right,env)
        if isinstance(expr,Call):
            callee=self.eval(expr.callee,env)
            args=[self.eval(a,env) for a in expr.args]
            if callable(callee): return callee(*args)
            if isinstance(callee,LoxFunction): return callee.call(self,args)
            raise TypeError(f"Not callable: {callee}")
        return None
    def _binary(self,expr,env):
        l=self.eval(expr.left,env); r=self.eval(expr.right,env)
        op=expr.op
        if op=="+":
            if isinstance(l,str) or isinstance(r,str): return str(l)+str(r)
            return l+r
        if op=="-": return l-r
        if op=="*": return l*r
        if op=="/": return l/r
        if op=="==": return l==r
        if op=="!=": return l!=r
        if op=="<": return l<r
        if op==">": return l>r
        if op=="<=": return l<=r
        if op==">=": return l>=r
    def _truthy(self,v):
        if v is None: return False
        if isinstance(v,bool): return v
        return True
    def _fmt(self,v):
        if v is None: return "nil"
        if v is True: return "true"
        if v is False: return "false"
        if isinstance(v,float) and v==int(v): return str(int(v))
        return str(v)

DEMO_CODE = '''
// tinycompiler demo — 参照 Crafting Interpreters 的 Lox 语言

var fib;
fun fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

print "Fibonacci:";
print fib(10);  // 55

var i = 1;
while (i <= 5) {
  print "  count: " + i;
  i = i + 1;
}

fun make_counter() {
  var count = 0;
  fun increment() {
    count = count + 1;
    return count;
  }
  return increment;
}

var counter = make_counter();
print "Counter:";
print counter();  // 1
print counter();  // 2
print counter();  // 3
'''

def main():
    print("tinycompiler — Crafting Interpreters\n")
    code = DEMO_CODE
    if len(sys.argv)>1 and sys.argv[1]=="--file" and len(sys.argv)>2:
        code = open(sys.argv[2]).read()
    elif len(sys.argv)>1 and sys.argv[1]!="--file":
        code = " ".join(sys.argv[1:])

    try:
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        Interpreter().run(ast)
    except (SyntaxError, NameError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)

if __name__=="__main__": main()
