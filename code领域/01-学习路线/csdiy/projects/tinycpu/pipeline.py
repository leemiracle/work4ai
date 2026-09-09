#!/usr/bin/env python3
"""
tinycpu/pipeline.py — 5 级流水线模拟器

参照：csapp Ch4(PIPE 实现) / Patterson Hennessy §4.5-4.7
csdiy 对应：csapp Ch4 Arch Lab + csapp Ch5(优化)

5 级流水线：
  IF (Instruction Fetch)     → 取指令
  ID (Instruction Decode)    → 译码 + 读寄存器
  EX (Execute)               → ALU 运算
  MEM (Memory Access)        → 读/写内存
  WB (Write Back)            → 写回寄存器

冒险处理：
  数据冒险： forwarding（旁路）+ stall（暂停）
  控制冒险： branch prediction（分支预测）
  结构冒险： 统一内存（简化版无结构冒险）"""
from dataclasses import dataclass
from .isa import *
from .core import ALU

@dataclass
class PipelineLatch:
    """流水线寄存器（级间寄存器，参照 csapp Ch4 图 4.52）"""
    valid: bool = False
    instr: object = None     # Instruction 对象
    pc: int = 0
    valA: int = 0; valB: int = 0; valC: int = 0
    rA: int = 0; rB: int = 0
    alu_result: int = 0
    mem_data: int = 0
    stage: str = ""

class PipelinedCPU:
    """5 级流水线 CPU（参照 csapp Ch4 PIPE）

    每个时钟周期，5 个阶段同时工作（不同指令在不同阶段）。
    理想 CPI = 1（每周期完成 1 条指令）。"""
    def __init__(self, mem_size=4096):
        self.regs = [0] * N_REGISTERS; self.pc = 0
        self.alu = ALU(); self.memory = [0] * mem_size
        self.program = []; self.halted = False
        self.cycles = 0; self.instructions_completed = 0
        self.stalls = 0; self.branches = 0; self.taken = 0
        # 5 个流水线寄存器（级间锁存器）
        self.if_id = PipelineLatch(); self.id_ex = PipelineLatch()
        self.ex_mem = PipelineLatch(); self.mem_wb = PipelineLatch()

    def load_program(self, instructions): self.program = instructions; self.pc = 0; self.halted = False
    def load_assembly(self, asm): self.load_program(assemble(asm))

    def run(self, max_cycles=10000):
        while not self.halted and self.cycles < max_cycles:
            self.clock_tick()
        return {"cycles": self.cycles, "instructions": self.instructions_completed,
                "cpi": self.cycles / max(1, self.instructions_completed),
                "stalls": self.stalls, "branches": self.branches}

    def clock_tick(self):
        """一个时钟周期：所有 5 个阶段并行执行（参照 csapp Ch4 §4.5.4）"""
        self.cycles += 1
        # ─── WB（Write Back）───
        if self.mem_wb.valid:
            instr = self.mem_wb.instr
            if instr and instr.rB is not None and instr.opcode in (OpCode.IRMOVL, OpCode.RRMOVL, OpCode.OPL, OpCode.MRMOVL):
                self.regs[instr.rB] = self.mem_wb.mem_data if instr.opcode == OpCode.MRMOVL else self.mem_wb.alu_result
                self.instructions_completed += 1
            if instr and instr.opcode == OpCode.HALT: self.halted = True

        # ─── MEM（Memory Access）───
        if self.ex_mem.valid:
            instr = self.ex_mem.instr
            self.mem_wb = PipelineLatch(valid=True, instr=instr, alu_result=self.ex_mem.alu_result)
            if instr and instr.opcode == OpCode.RMMOVL:
                addr = self.ex_mem.valB + self.ex_mem.valC
                if addr < len(self.memory): self.memory[addr] = self.ex_mem.valA
            elif instr and instr.opcode == OpCode.MRMOVL:
                addr = self.ex_mem.valA + self.ex_mem.valC
                self.mem_wb.mem_data = self.memory[addr] if addr < len(self.memory) else 0
        else:
            self.mem_wb = PipelineLatch()

        # ─── EX（Execute）───
        if self.id_ex.valid:
            instr = self.id_ex.instr
            # Forwarding（参照 csapp Ch4 §4.5.5）
            valA = self._forward(self.id_ex.valA, self.id_ex.rA)
            valB = self._forward(self.id_ex.valB, self.id_ex.rB)
            alu_result = valB  # 默认
            if instr:
                if instr.opcode == OpCode.IRMOVL: alu_result = self.id_ex.valC
                elif instr.opcode == OpCode.RRMOVL: alu_result = valA
                elif instr.opcode == OpCode.OPL: alu_result = self.alu.execute(instr.alu_op, valA, valB)
                elif instr.opcode in (OpCode.RMMOVL, OpCode.MRMOVL): alu_result = (valB + self.id_ex.valC) if instr.opcode == OpCode.MRMOVL else valB
                elif instr.opcode == OpCode.JXX:
                    self.branches += 1
                    if self.alu.check_cond(instr.cond): self.pc = self.id_ex.valC; self.taken += 1
            self.ex_mem = PipelineLatch(valid=True, instr=instr, alu_result=alu_result,
                                        valA=valA, valB=valB, valC=self.id_ex.valC,
                                        rA=self.id_ex.rA, rB=self.id_ex.rB)
        else:
            self.ex_mem = PipelineLatch()

        # ─── ID（Decode + Register Read）───
        if self.if_id.valid and self.if_id.instr:
            instr = self.if_id.instr
            self.id_ex = PipelineLatch(valid=True, instr=instr, pc=self.if_id.pc,
                                       valA=self.regs[instr.rA], valB=self.regs[instr.rB],
                                       valC=instr.imm, rA=instr.rA, rB=instr.rB)
        else:
            self.id_ex = PipelineLatch()

        # ─── IF（Instruction Fetch）───
        if self.pc < len(self.program):
            self.if_id = PipelineLatch(valid=True, instr=self.program[self.pc], pc=self.pc)
            self.pc += 1
        else:
            self.if_id = PipelineLatch()

    def _forward(self, val, reg):
        """Forwarding 逻辑（参照 csapp Ch4 §4.5.5）
        如果 EX/MEM 或 MEM/WB 有更新 reg 的结果 → 直接旁路"""
        if self.ex_mem.valid and self.ex_mem.instr:
            if self.ex_mem.instr.rB == reg and self.ex_mem.instr.opcode != OpCode.RMMOVL:
                return self.ex_mem.alu_result
        if self.mem_wb.valid and self.mem_wb.instr:
            if self.mem_wb.instr.rB == reg and self.mem_wb.instr.opcode != OpCode.RMMOVL:
                return self.mem_wb.mem_data if self.mem_wb.instr.opcode == OpCode.MRMOVL else self.mem_wb.alu_result
        return val

    def dump_registers(self):
        for i, name in enumerate(REGISTERS):
            print(f"  {name:4s} = {self.regs[i]:>10d}")
        print(f"  pc = {self.pc}")
