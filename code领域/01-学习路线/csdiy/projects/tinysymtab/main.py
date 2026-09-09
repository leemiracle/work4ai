#!/usr/bin/env python3
"""tinysymtab — 参照编译器符号表
参照：CS143 编译器 / LLVM SymbolTable / nm
csdiy 对应：tinycompiler + tinylinker + csapp Ch7
核心：作用域栈 + 符号查找 + 类型信息"""
from dataclasses import dataclass,field
from typing import Any,Optional

@dataclass
class Symbol:
    name:str; type:str; scope:str; addr:Optional[int]=None; attributes:dict=field(default_factory=dict)

class Scope:
    """作用域（参照编译器的 Scope/SymbolTable）"""
    def __init__(self,name,parent=None):
        self.name=name; self.parent=parent; self.symbols={}
    def define(self,sym): self.symbols[sym.name]=sym; return sym
    def resolve(self,name):
        if name in self.symbols: return self.symbols[name]
        if self.parent: return self.parent.resolve(name)
        return None

class SymbolTable:
    """符号表管理器（参照 LLVM SymbolTable）
    支持嵌套作用域：global → function → block"""
    def __init__(self):
        self.global_scope=Scope("global"); self.current=self.global_scope; self.next_addr=0x1000
    def enter_scope(self,name):
        self.current=Scope(name,self.current); return self.current
    def exit_scope(self): self.current=self.current.parent or self.global_scope
    def define(self,name,type,**attrs):
        sym=Symbol(name,type,self.current.name,self.next_addr,attrs); self.next_addr+=4
        self.current.define(sym); return sym
    def resolve(self,name): return self.current.resolve(name)
    def dump(self):
        scopes=[self.global_scope]
        def collect(scope):
            for sym in scope.symbols.values():
                print(f"  {scope.name:12s} {sym.name:15s} {sym.type:10s} addr={sym.addr:#06x} {sym.attributes}")
            for s in [s for s in [scope] if hasattr(s,'children')]: pass
        collect(self.global_scope)

def main():
    print("tinysymtab — 符号表（参照编译器）\n")
    st=SymbolTable()
    st.define("global_var","int"); st.define("PI","float",const=True)
    st.enter_scope("main")
    st.define("x","int"); st.define("y","int")
    st.enter_scope("for_loop")
    st.define("i","int")
    x=st.resolve("x"); g=st.resolve("global_var"); p=st.resolve("PI")
    print(f"  resolve('i') = {st.resolve('i')}")
    print(f"  resolve('x') = {x} (from parent scope)")
    print(f"  resolve('global_var') = {g} (from global scope)")
    print(f"  resolve('PI') = {p}")
    st.exit_scope(); st.exit_scope()
    print(f"\n  对比 nm 命令: nm a.out → 列出编译后的符号表")

if __name__=="__main__": main()
