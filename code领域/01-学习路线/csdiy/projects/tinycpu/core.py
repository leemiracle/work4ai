#!/usr/bin/env python3
"""
tinycpu/core.py — CPU 核心（寄存器 + ALU + 条件码）

参照：csapp Ch4(Y86 SEQ 实现) / RISC-V datapath
csdiy 对应：csapp Ch4 + Arch Lab

核心组件：
  RegisterFile  — 8 个通用寄存器 + PC
  ALU           — 算术逻辑单元
  ConditionCodes — ZF/SF/OF 标志位
  CPU           — 单指令周期执行器（参照 SEQ）"""
from .isa import *

class ALU:
    """算术逻辑单元（参照 csapp Ch4 §4.2.3）
    执行运算并设置条件码 ZF/SF/OF"""
    def __init__(self):
        self.ZF = 0; self.SF = 0; self.OF = 0  # 零/符号/溢出标志
    def execute(self, op: AluOp, a: int, b: int):
        """执行运算 → 返回结果 + 设置标志位"""
        if op == AluOp.ADD:
            result = a + b; self.OF = 1 if _overflow_add(a, b, result) else 0
        elif op == AluOp.SUB:
            result = a - b; self.OF = 1 if _overflow_sub(a, b, result) else 0
        elif op == AluOp.AND: result = a & b
        elif op == AluOp.XOR: result = a ^ b
        elif op == AluOp.MUL: result = a * b
        elif op == AluOp.SHL: result = a << b
        elif op == AluOp.SHR: result = a >> b
        else: result = 0
        self.ZF = 1 if result == 0 else 0
        self.SF = 1 if result < 0 else 0
        return result
    def check_cond(self, cond: CondCode):
        """检查条件码是否满足跳转条件"""
        if cond == CondCode.ALWAYS: return True
        elif cond == CondCode.LE: return self.ZF or self.SF != self.OF
        elif cond == CondCode.LT: return self.SF != self.OF
        elif cond == CondCode.EQ: return self.ZF
        elif cond == CondCode.NE: return not self.ZF
        elif cond == CondCode.GE: return self.SF == self.OF
        elif cond == CondCode.GT: return not self.ZF and self.SF == self.OF
        return False

def _overflow_add(a, b, r): return (a < 0 and b < 0 and r >= 0) or (a >= 0 and b >= 0 and r < 0)
def _overflow_sub(a, b, r): return (a >= 0 and b < 0 and r < 0) or (a < 0 and b >= 0 and r >= 0)

class CPU:
    """单指令周期 CPU（参照 csapp Ch4 SEQ 实现）

    每条指令经历：
      Fetch（取指）→ Decode（译码）→ Execute（执行）→ Memory（访存）→ WriteBack（写回）→ PC Update
    """
    def __init__(self, mem_size=4096):
        self.regs = [0] * N_REGISTERS  # eax...edi
        self.pc = 0                    # 程序计数器
        self.alu = ALU()
        self.memory = [0] * mem_size   # 简单内存（参照 csapp Y86 Memory）
        self.flags = {"ZF": 0, "SF": 0, "OF": 0}
        self.halted = False
        self.cycles = 0
        self.program = []

    def load_program(self, instructions: list):
        """加载程序（参照 csapp load to memory）"""
        self.program = instructions; self.pc = 0; self.halted = False

    def load_assembly(self, asm_text):
        """从汇编代码加载"""
        self.load_program(assemble(asm_text))

    def step(self):
        """执行一条指令（参照 csapp Ch4 SEQ 的时钟周期）"""
        if self.halted or self.pc >= len(self.program):
            self.halted = True; return False
        instr = self.program[self.pc]; self.cycles += 1

        # ① Fetch
        # ② Decode
        valA = self.regs[instr.rA]; valB = self.regs[instr.rB]
        valC = instr.imm
        # ③ Execute
        if instr.opcode == OpCode.HALT: self.halted = True; return False
        elif instr.opcode == OpCode.NOP: pass
        elif instr.opcode == OpCode.IRMOVL:
            self.regs[instr.rB] = valC  # C → rB
        elif instr.opcode == OpCode.RRMOVL:
            self.regs[instr.rB] = valA  # rA → rB
        elif instr.opcode == OpCode.OPL:
            self.regs[instr.rB] = self.alu.execute(instr.alu_op, valA, valB)
        elif instr.opcode == OpCode.RMMOVL:
            addr = valB + valC; self.memory[addr] = valA  # rA → M[rB+D]
        elif instr.opcode == OpCode.MRMOVL:
            addr = valA + valC; self.regs[instr.rB] = self.memory[addr]
        elif instr.opcode == OpCode.JXX:
            if self.alu.check_cond(instr.cond): self.pc = valC; return True
        elif instr.opcode == OpCode.RET:
            self.pc = self.regs[4]  # esp 指向返回地址
            return True

        self.pc += 1
        return True

    def run(self, max_cycles=10000):
        """运行直到 halt 或达到最大周期"""
        while not self.halted and self.cycles < max_cycles:
            self.step()
        return self.cycles

    def dump_registers(self):
        """打印寄存器（参照 gdb info registers）"""
        for i, name in enumerate(REGISTERS):
            print(f"  {name:4s} = {self.regs[i]:>10d}  (0x{self.regs[i] & 0xFFFFFFFF:08X})")
        print(f"  pc   = {self.pc:>10d}")
        print(f"  ZF={self.alu.ZF} SF={self.alu.SF} OF={self.alu.OF}")

    def dump_memory(self, start=0, count=16):
        """打印内存（参照 gdb x/16xw）"""
        print(f"  Memory [0x{start:04X}]:")
        for i in range(count):
            addr = start + i
            if addr < len(self.memory):
                print(f"    0x{addr:04X}: {self.memory[addr]:>10d}  (0x{self.memory[addr] & 0xFFFFFFFF:08X})")
