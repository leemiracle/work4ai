#!/usr/bin/env python3
"""
tinycpu/isa.py — 指令集架构（参照 Y86-64 / RISC-V 简化版）

参照：csapp Ch4(Y86处理器) / RISC-V ISA / x86-64
csdiy 对应：csapp Ch4(处理器体系结构) + Arch Lab

指令格式（8 位操作码 + 操作数）:
  HALT   = 0x00  停机
  NOP    = 0x10  空操作
  RRMOVL = 0x20  寄存器→寄存器移动 rA → rB
  IRMOVL = 0x30  立即数→寄存器 C → rB
  RMMOVL = 0x40  寄存器→内存 rA → M[rB+D]
  MRMOVL = 0x50  内存→寄存器 M[rA+D] → rB
  OPL    = 0x60  算术逻辑运算 rA OP rB → rB
  JXX    = 0x70  跳转
  CMOVXX = 0x20  条件移动（RRMOVL 的条件版）
  CALL   = 0x80  函数调用
  RET    = 0x90  函数返回
  PUSHL  = 0xA0  压栈
  POPL   = 0xB0  出栈
"""
from enum import IntEnum
from dataclasses import dataclass

class OpCode(IntEnum):
    HALT=0x00; NOP=0x10
    RRMOVL=0x20; IRMOVL=0x30; RMMOVL=0x40; MRMOVL=0x50
    OPL=0x60; JXX=0x70; CALL=0x80; RET=0x90; PUSHL=0xA0; POPL=0xB0

class AluOp(IntEnum):
    ADD=0; SUB=1; AND=2; XOR=3; MUL=4; SHL=5; SHR=6

class CondCode(IntEnum):
    ALWAYS=0; LE=1; LT=2; EQ=3; NE=4; GE=5; GT=6

@dataclass
class Instruction:
    """一条机器指令（参照 Y86 指令编码）"""
    opcode: OpCode
    rA: int = 0       # 源寄存器（4 bit）
    rB: int = 0       # 目标寄存器（4 bit）
    imm: int = 0      # 立即数/地址偏移
    alu_op: AluOp = AluOp.ADD
    cond: CondCode = CondCode.ALWAYS

# 寄存器名（参照 Y86）
REGISTERS = ["eax","ecx","edx","ebx","esp","ebp","esi","edi"]
N_REGISTERS = 8

def assemble(asm_text):
    """简单汇编器（参照 csapp Arch Lab 的 yas）
    支持：irmovl, rrmovl, rmmovl, mrmovl, addl, subl, jmp, ret, halt"""
    program = []
    labels = {}
    lines = [l.split('#')[0].strip() for l in asm_text.split('\n')]
    # 第一遍：收集标签
    addr = 0
    for line in lines:
        if not line: continue
        if line.endswith(':'):
            labels[line[:-1].strip()] = addr; continue
        addr += 1
    # 第二遍：编码
    for line in lines:
        if not line or line.endswith(':'): continue
        parts = line.replace(',', ' ').split()
        cmd = parts[0].lower()
        if cmd == 'halt': program.append(Instruction(OpCode.HALT))
        elif cmd == 'nop': program.append(Instruction(OpCode.NOP))
        elif cmd == 'irmovl':
            imm = _parse_val(parts[1], labels)
            rB = REGISTERS.index(parts[2]) if parts[2] in REGISTERS else 0
            program.append(Instruction(OpCode.IRMOVL, rB=rB, imm=imm))
        elif cmd == 'rrmovl':
            rA = REGISTERS.index(parts[1]); rB = REGISTERS.index(parts[2])
            program.append(Instruction(OpCode.RRMOVL, rA=rA, rB=rB))
        elif cmd in ('addl','subl','andl','xorl','mull'):
            rA = REGISTERS.index(parts[1]); rB = REGISTERS.index(parts[2])
            op = {'addl':AluOp.ADD,'subl':AluOp.SUB,'andl':AluOp.AND,
                  'xorl':AluOp.XOR,'mull':AluOp.MUL}[cmd]
            program.append(Instruction(OpCode.OPL, rA=rA, rB=rB, alu_op=op))
        elif cmd in ('jmp','jle','jl','je','jne','jge','jgt'):
            target = _parse_val(parts[1], labels)
            cond = {'jmp':CondCode.ALWAYS,'jle':CondCode.LE,'jl':CondCode.LT,
                    'je':CondCode.EQ,'jne':CondCode.NE,'jge':CondCode.GE,'jgt':CondCode.GT}[cmd]
            program.append(Instruction(OpCode.JXX, imm=target, cond=cond))
        elif cmd == 'rmmovl':
            rA = REGISTERS.index(parts[1]); offset, rB = _parse_mem(parts[2])
            program.append(Instruction(OpCode.RMMOVL, rA=rA, rB=rB, imm=offset))
        elif cmd == 'mrmovl':
            offset, rA = _parse_mem(parts[1]); rB = REGISTERS.index(parts[2])
            program.append(Instruction(OpCode.MRMOVL, rA=rA, rB=rB, imm=offset))
        elif cmd == 'ret': program.append(Instruction(OpCode.RET))
    return program

def _parse_val(s, labels):
    if s in labels: return labels[s]
    try: return int(s, 0)
    except: return 0

def _parse_mem(s):
    """解析 D(rB) 格式"""
    if '(' in s:
        offset_str, reg_part = s.split('(')
        offset = int(offset_str) if offset_str else 0
        reg = REGISTERS.index(reg_part.rstrip(')'))
        return offset, reg
    return 0, REGISTERS.index(s) if s in REGISTERS else 0
