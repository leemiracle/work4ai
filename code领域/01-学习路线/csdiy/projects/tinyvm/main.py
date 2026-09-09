#!/usr/bin/env python3
"""tinyvm — 参照 Lua VM / JVM 的字节码虚拟机
参照：Lua VM / JVM / WebAssembly / Crafting Interpreters Ch15
csdiy 对应：csapp Ch4(处理器) + tinycompiler + tinyasm
核心：字节码解释器 → 栈式 VM"""
from dataclasses import dataclass
from typing import List

# 字节码操作码（参照 Crafting Interpreters clox chunk.h）
OP_CONSTANT = 0x01   # 加载常量
OP_ADD = 0x02; OP_SUB = 0x03; OP_MUL = 0x04; OP_DIV = 0x05
OP_NEGATE = 0x06
OP_TRUE = 0x07; OP_FALSE = 0x08; OP_NIL = 0x09
OP_NOT = 0x0A; OP_EQUAL = 0x0B; OP_GREATER = 0x0C; OP_LESS = 0x0D
OP_PRINT = 0x0E
OP_POP = 0x0F
OP_GET_LOCAL = 0x10; OP_SET_LOCAL = 0x11
OP_JUMP_IF_FALSE = 0x12; OP_JUMP = 0x13
OP_CALL = 0x14
OP_RETURN = 0x00

class Chunk:
    """字节码块（参照 clox Chunk）"""
    def __init__(self): self.code=[]; self.constants=[]
    def write(self, byte): self.code.append(byte)
    def add_constant(self, val): self.constants.append(val); return len(self.constants)-1

class VM:
    """栈式虚拟机（参照 clox VM + csapp Ch4 的 Y86 处理器）"""
    def __init__(self):
        self.stack = []; self.locals = {}
        self.output = []
    def interpret(self, chunk):
        ip = 0
        while ip < len(chunk.code):
            op = chunk.code[ip]; ip += 1
            if op == OP_CONSTANT:
                idx = chunk.code[ip]; ip += 1
                self.stack.append(chunk.constants[idx])
            elif op == OP_ADD: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a+b)
            elif op == OP_SUB: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a-b)
            elif op == OP_MUL: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a*b)
            elif op == OP_DIV: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a/b)
            elif op == OP_NEGATE: self.stack.append(-self.stack.pop())
            elif op == OP_TRUE: self.stack.append(True)
            elif op == OP_FALSE: self.stack.append(False)
            elif op == OP_NIL: self.stack.append(None)
            elif op == OP_NOT: self.stack.append(not self.stack.pop())
            elif op == OP_EQUAL: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a==b)
            elif op == OP_GREATER: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a>b)
            elif op == OP_LESS: b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a<b)
            elif op == OP_PRINT: self.output.append(self.stack.pop())
            elif op == OP_POP: self.stack.pop()
            elif op == OP_GET_LOCAL: slot=chunk.code[ip]; ip+=1; self.stack.append(self.locals.get(slot,0))
            elif op == OP_SET_LOCAL: slot=chunk.code[ip]; ip+=1; self.locals[slot]=self.stack[-1]
            elif op == OP_JUMP_IF_FALSE:
                off=chunk.code[ip]; ip+=1
                if not self.stack[-1]: ip += off
            elif op == OP_JUMP: off=chunk.code[ip]; ip+=1; ip += off
            elif op == OP_RETURN: break
        return self.output

def main():
    print("tinyvm — 字节码虚拟机（参照 Lua VM / JVM）\n")

    # 编译 (3 + 4) * 5
    chunk = Chunk()
    c3 = chunk.add_constant(3.0)
    c4 = chunk.add_constant(4.0)
    c5 = chunk.add_constant(5.0)
    chunk.write(OP_CONSTANT); chunk.write(c3)
    chunk.write(OP_CONSTANT); chunk.write(c4)
    chunk.write(OP_ADD)
    chunk.write(OP_CONSTANT); chunk.write(c5)
    chunk.write(OP_MUL)
    chunk.write(OP_PRINT)
    chunk.write(OP_RETURN)

    print(f"  字节码: {chunk.code}")
    print(f"  常量池: {chunk.constants}")
    vm = VM()
    result = vm.interpret(chunk)
    print(f"  输出: {result} → (3+4)*5 = {result[0]}")

    # 条件跳转：if true print(42) else print(99)
    chunk2 = Chunk()
    chunk2.write(OP_TRUE)
    chunk2.write(OP_JUMP_IF_FALSE); chunk2.write(4)  # 跳过下面的 42
    c42 = chunk2.add_constant(42.0)
    chunk2.write(OP_CONSTANT); chunk2.write(c42)
    chunk2.write(OP_PRINT)
    chunk2.write(OP_JUMP); chunk2.write(3)  # 跳过 else
    c99 = chunk2.add_constant(99.0)
    chunk2.write(OP_CONSTANT); chunk2.write(c99)
    chunk2.write(OP_PRINT)
    chunk2.write(OP_RETURN)

    vm2 = VM()
    result2 = vm2.interpret(chunk2)
    print(f"\n  条件跳转: if true print(42) → {result2}")

    print(f"\n  VM 特点: 栈式（操作数在栈上），简单但高效")
    print(f"  对比 csapp Ch4 Y86: 同样的取指→译码→执行→写回流水")

if __name__ == "__main__": main()
