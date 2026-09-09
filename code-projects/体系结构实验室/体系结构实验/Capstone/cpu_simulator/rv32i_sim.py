#!/usr/bin/env python3
"""
rv32i_sim.py — RV32I 周期级 5 级流水线模拟器（完整版）

Capstone-B: 自写 CPU 模拟器
对应教材: 🎓 ETHz DDCA + CS61C Proj3 + CAQA Appendix C

================================================================================
设计要点（"现代的方式"）
================================================================================
1. **完整 RV32I**：40 条指令全覆盖（含 LUI/AUIPC/JAL/JALR/6 分支/5 load/3 store/
   6 算术立即/3 移位/10 R-type/FENCE/ECALL/EBREAK）。
2. **5 级流水线**：IF → ID → EX → MEM → WB，双缓冲（from/to）避免同周期读写竞争。
3. **3 路 Forwarding**：EX/MEM → EX（ALU 结果）、MEM/WB → EX（含 load 数据）。
4. **Load-Use Stall**：ID 阶段检测，插入 1 cycle 气泡。
5. **分支解析在 EX**：错误预测 flush 2 条（IF/ID、ID/EX）。
6. **2-bit 饱和分支预测器**：per-PC，IF 阶段查询，EX 阶段更新。
7. **可测试**：纯函数化解码 + dataclass，配 pytest 套件（见 tests/）。
8. **可观测**：每条指令的 lifecycle 可追溯，Stats 汇总 IPC/stall/flush/branch 预测准确率。

================================================================================
用法
================================================================================
    # 跑内置示例（sum 1..10 = 55）
    python3 rv32i_sim.py

    # 跑测试程序
    python3 rv32i_sim.py test_progs/fib.s

    # 详细模式（逐周期 trace）
    python3 rv32i_sim.py --trace test_progs/bubble_sort.s

    # 关闭 forwarding（观察 IPC 跌幅，教学用）
    python3 rv32i_sim.py --no-forward test_progs/sum.s
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Tuple

MASK32 = 0xFFFFFFFF  # 32-bit 无符号掩码


# ============================================================================
# Section 1: RV32I 解码
# ============================================================================

# RV32I 指令的"行为分类"，决定它在流水线里怎么走
class InstKind(Enum):
    OP_IMM = auto()      # ADDI/SLTI/.../SLLI/SRLI/SRAI  (I-type ALU)
    OP = auto()          # ADD/SUB/... (R-type ALU)
    LUI = auto()         # LUI
    AUIPC = auto()       # AUIPC
    JAL = auto()         # JAL
    JALR = auto()        # JALR
    BRANCH = auto()      # BEQ/BNE/BLT/BGE/BLTU/BGEU
    LOAD = auto()        # LB/LH/LW/LBU/LHU
    STORE = auto()       # SB/SH/SW
    FENCE = auto()       # FENCE / FENCE.I
    SYSTEM = auto()      # ECALL / EBREAK


# opcode 字段（指令低 7 位）→ InstKind
OPCODE_MAP: Dict[int, InstKind] = {
    0x37: InstKind.LUI,
    0x17: InstKind.AUIPC,
    0x6F: InstKind.JAL,
    0x67: InstKind.JALR,
    0x63: InstKind.BRANCH,
    0x03: InstKind.LOAD,
    0x23: InstKind.STORE,
    0x13: InstKind.OP_IMM,
    0x33: InstKind.OP,
    0x0F: InstKind.FENCE,
    0x73: InstKind.SYSTEM,
}


@dataclass
class Instruction:
    """解码后的 RV32I 指令。flags 提前算好，避免流水线里反复判 kind。"""
    addr: int
    raw: int
    op: str = "illegal"
    kind: InstKind = InstKind.SYSTEM
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0
    # —— 行为 flags（让流水线代码更线性）——
    reads_rs1: bool = False
    reads_rs2: bool = False
    writes_rd: bool = False
    is_load: bool = False
    is_store: bool = False
    is_branch: bool = False
    is_jal: bool = False
    is_jalr: bool = False
    is_control: bool = False   # ecall/ebreak


# —— 立即数符号扩展（12 位 / 13 位 / 21 位）——
def _sext(value: int, bits: int) -> int:
    """把 value 当作 bits 位有符号数，返回 Python int。"""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def _decode_imm(raw: int, kind: InstKind) -> int:
    """按指令类型抽取并符号扩展立即数。"""
    if kind == InstKind.OP:
        # R-type 没有立即数；强制返回 0（防止掉到 U-type 分支取错位）
        return 0
    if kind in (InstKind.OP_IMM, InstKind.LOAD, InstKind.JALR, InstKind.SYSTEM):
        # I-type: imm[11:0] = inst[31:20]
        return _sext(raw >> 20, 12)
    if kind == InstKind.STORE:
        # S-type: imm[11:5]=inst[31:25], imm[4:0]=inst[11:7]
        imm = ((raw >> 25) << 5) | ((raw >> 7) & 0x1F)
        return _sext(imm, 12)
    if kind == InstKind.BRANCH:
        # B-type: imm[12|10:5|4:1|11]，注意 imm[0] 恒为 0
        imm = (((raw >> 31) & 1) << 12) | \
              (((raw >> 7) & 1) << 11) | \
              (((raw >> 25) & 0x3F) << 5) | \
              (((raw >> 8) & 0xF) << 1)
        return _sext(imm, 13)
    if kind == InstKind.JAL:
        # J-type: imm[20|10:1|11|19:12]，imm[0]=0
        imm = (((raw >> 31) & 1) << 20) | \
              (((raw >> 12) & 0xFF) << 12) | \
              (((raw >> 20) & 1) << 11) | \
              (((raw >> 21) & 0x3FF) << 1)
        return _sext(imm, 21)
    # U-type (LUI/AUIPC): imm[31:12] = inst[31:12]，高 20 位
    return raw & 0xFFFFF000  # 已是对齐的 32-bit 有符号值（自然符号扩展于 Python int）


# funct3 → 操作码，按 kind 分发
def _decode_op(kind: InstKind, funct3: int, funct7: int, raw: int) -> str:
    """返回助记符；非法返回 'illegal'。"""
    if kind == InstKind.OP_IMM:
        # SLLI/SRLI/SRAI 用 funct7 区分；其余用 funct3
        if funct3 == 0x0: return "addi"
        if funct3 == 0x2: return "slti"
        if funct3 == 0x3: return "sltiu"
        if funct3 == 0x4: return "xori"
        if funct3 == 0x6: return "ori"
        if funct3 == 0x7: return "andi"
        if funct3 == 0x1: return "slli" if (funct7 == 0x00) else "illegal"
        if funct3 == 0x5:
            if funct7 == 0x00: return "srli"
            if funct7 == 0x20: return "srai"
            return "illegal"
        return "illegal"
    if kind == InstKind.OP:
        table = {
            (0x0, 0x00): "add",  (0x0, 0x20): "sub",
            (0x1, 0x00): "sll",
            (0x2, 0x00): "slt",  (0x3, 0x00): "sltu",
            (0x4, 0x00): "xor",
            (0x5, 0x00): "srl",  (0x5, 0x20): "sra",
            (0x6, 0x00): "or",
            (0x7, 0x00): "and",
        }
        return table.get((funct3, funct7), "illegal")
    if kind == InstKind.BRANCH:
        return {0x0: "beq", 0x1: "bne", 0x4: "blt",
                0x5: "bge", 0x6: "bltu", 0x7: "bgeu"}.get(funct3, "illegal")
    if kind == InstKind.LOAD:
        return {0x0: "lb", 0x1: "lh", 0x2: "lw",
                0x4: "lbu", 0x5: "lhu"}.get(funct3, "illegal")
    if kind == InstKind.STORE:
        return {0x0: "sb", 0x1: "sh", 0x2: "sw"}.get(funct3, "illegal")
    if kind == InstKind.LUI:    return "lui"
    if kind == InstKind.AUIPC:  return "auipc"
    if kind == InstKind.JAL:    return "jal"
    if kind == InstKind.JALR:   return "jalr"   # jalr 固定 funct3=0
    if kind == InstKind.FENCE:  return "fence"
    if kind == InstKind.SYSTEM:
        # ECALL=0x00000073, EBREAK=0x00100073
        if raw == 0x00000073: return "ecall"
        if raw == 0x00100073: return "ebreak"
        return "system"
    return "illegal"


def decode(raw: int, addr: int) -> Instruction:
    """从 32-bit 原始字解码出 Instruction。addr 用于 JAL/分支计算目标。"""
    raw &= MASK32
    opcode = raw & 0x7F
    rd  = (raw >> 7)  & 0x1F
    rs1 = (raw >> 15) & 0x1F
    rs2 = (raw >> 20) & 0x1F
    funct3 = (raw >> 12) & 0x7
    funct7 = (raw >> 25) & 0x7F

    kind = OPCODE_MAP.get(opcode)
    if kind is None:
        return Instruction(addr=addr, raw=raw, op="illegal", kind=InstKind.SYSTEM)

    op = _decode_op(kind, funct3, funct7, raw)
    imm = _decode_imm(raw, kind)

    inst = Instruction(addr=addr, raw=raw, op=op, kind=kind,
                       rd=rd, rs1=rs1, rs2=rs2, imm=imm)
    # —— 设置行为 flags ——
    inst.reads_rs1 = kind in (InstKind.OP, InstKind.BRANCH, InstKind.STORE,
                              InstKind.OP_IMM, InstKind.LOAD, InstKind.JALR,
                              InstKind.AUIPC)
    inst.reads_rs2 = kind in (InstKind.OP, InstKind.BRANCH, InstKind.STORE)
    inst.writes_rd = kind in (InstKind.OP, InstKind.OP_IMM, InstKind.LUI,
                              InstKind.AUIPC, InstKind.JAL, InstKind.JALR,
                              InstKind.LOAD)
    inst.is_load    = kind == InstKind.LOAD
    inst.is_store   = kind == InstKind.STORE
    inst.is_branch  = kind == InstKind.BRANCH
    inst.is_jal     = kind == InstKind.JAL
    inst.is_jalr    = kind == InstKind.JALR
    inst.is_control = op in ("ecall", "ebreak")
    # SPECIAL: andi/ori/xori 不读 rs2；slli/srli/srai 也不读 rs2，移位量在 imm
    if kind == InstKind.OP_IMM:
        inst.reads_rs2 = False
    # SPECIAL: lui 不读 rs1
    if kind in (InstKind.LUI,):
        inst.reads_rs1 = False
    return inst


# ============================================================================
# Section 2: 寄存器堆 / 内存
# ============================================================================

class RegFile:
    """32 个通用寄存器，x0 永远为 0。"""
    __slots__ = ("regs",)

    def __init__(self) -> None:
        self.regs: List[int] = [0] * 32

    def read(self, idx: int) -> int:
        return 0 if idx == 0 else self.regs[idx] & MASK32

    def write(self, idx: int, val: int) -> None:
        if idx != 0:
            self.regs[idx] = val & MASK32


class Memory:
    """字节寻址、小端、可变大小数据内存。load/store 按 RV32I 语义切片。"""

    def __init__(self, size: int = 4096) -> None:
        self.bytes = bytearray(size)

    def _check(self, addr: int) -> int:
        if not (0 <= addr < len(self.bytes)):
            raise IndexError(f"data memory access out of range: 0x{addr:x}")
        return addr

    def load(self, addr: int, size: int, signed: bool) -> int:
        addr = self._check(addr)
        # 允许 1/2/4 字节非对齐访问（RV32I 实际要求对齐，但模拟器放宽便于测试）
        raw = int.from_bytes(self.bytes[addr:addr + size], "little")
        if signed:
            return _sext(raw, size * 8)
        return raw & MASK32 if size == 4 else raw

    def store(self, addr: int, size: int, val: int) -> None:
        addr = self._check(addr)
        val &= (1 << (size * 8)) - 1
        self.bytes[addr:addr + size] = val.to_bytes(size, "little")


# ============================================================================
# Section 3: 2-bit 饱和分支预测器
# ============================================================================

# 状态机:  SN(0) --taken--> WN(1) --taken--> WT(2) --taken--> ST(3)
#          ST(3) --not taken--> WT(2) --not taken--> WN(1) --not taken--> SN(0)
# 预测 taken 当且仅当 state >= 2

class TwoBitPredictor:
    """Per-PC 2-bit 饱和预测器。"""

    def __init__(self) -> None:
        self.state: Dict[int, int] = {}
        # 统计
        self.predictions = 0
        self.mispredictions = 0

    def predict(self, pc: int) -> bool:
        """返回 True=taken。默认 weakly not-taken (state=1)。"""
        return self.state.get(pc, 1) >= 2

    def update(self, pc: int, taken: bool) -> None:
        s = self.state.get(pc, 1)
        if taken:
            s = min(3, s + 1)
        else:
            s = max(0, s - 1)
        self.state[pc] = s


# ============================================================================
# Section 4: 流水线寄存器（双缓冲：f_* = 上一周期末，t_* = 本周期末）
# ============================================================================

@dataclass
class PipeReg:
    valid: bool = False
    inst: Optional[Instruction] = None
    # 操作数快照（在 ID 阶段从 RegFile 读，之后靠 forwarding 更新）
    rs1_val: int = 0
    rs2_val: int = 0
    # ALU 输出（EX 阶段写）
    alu_result: int = 0
    # MEM 阶段 load 读到的数据（load 专用；非 load 时 = alu_result）
    mem_data: int = 0
    # 预测记录（IF 写）
    predicted_taken: bool = False
    predicted_target: int = 0

    @staticmethod
    def bubble() -> "PipeReg":
        return PipeReg(valid=False)


# ============================================================================
# Section 5: ALU 与分支判定
# ============================================================================

def _alu(op: str, a: int, b: int, imm: int, pc: int) -> int:
    """ALU 运算 + 地址计算 + AUIPC/JAL 目标计算。返回 32-bit 无符号。

    约定：
      - R-type（add/sub/...）使用 (a, b)
      - I-type 算术（addi/slti/...）使用 (a, imm)
      - I-type 移位（slli/srli/srai）使用 (a, shamt=imm & 0x1F)
      - load/store 地址 = a + imm
      - LUI 返回 imm；AUIPC 返回 pc + imm
      - JAL/JALR 返回跳转目标；返回地址（pc+4）由 EX 阶段单独写
    """
    # —— 地址计算（共用：a + imm）——
    if op in ("lb", "lh", "lw", "lbu", "lhu", "sb", "sh", "sw"):
        return (a + imm) & MASK32

    # —— I-type 算术 ——
    if op == "addi":  return (a + imm) & MASK32
    if op == "slti":  return 1 if _to_signed(a) < imm else 0
    if op == "sltiu": return 1 if (a & MASK32) < (imm & MASK32) else 0
    if op == "xori":  return (a ^ (imm & MASK32)) & MASK32
    if op == "ori":   return (a | (imm & MASK32)) & MASK32
    if op == "andi":  return (a & (imm & MASK32)) & MASK32

    # —— I-type 移位（移位量在 imm 低 5 位）——
    if op == "slli":  return (a << (imm & 0x1F)) & MASK32
    if op == "srli":  return (a & MASK32) >> (imm & 0x1F)
    if op == "srai":  return (_to_signed(a) >> (imm & 0x1F)) & MASK32

    # —— R-type ——
    if op == "add":  return (a + b) & MASK32
    if op == "sub":  return (a - b) & MASK32
    if op == "sll":  return (a << (b & 0x1F)) & MASK32
    if op == "slt":  return 1 if _to_signed(a) < _to_signed(b) else 0
    if op == "sltu": return 1 if (a & MASK32) < (b & MASK32) else 0
    if op == "xor":  return (a ^ b) & MASK32
    if op == "srl":  return (a & MASK32) >> (b & 0x1F)
    if op == "sra":  return (_to_signed(a) >> (b & 0x1F)) & MASK32
    if op == "or":   return (a | b) & MASK32
    if op == "and":  return (a & b) & MASK32

    # —— U-type / 跳转目标 ——
    if op == "lui":   return imm & MASK32
    if op == "auipc": return (pc + imm) & MASK32
    if op == "jal":   return (pc + imm) & MASK32      # 跳转目标；rd=pc+4 由 EX 单独算
    if op == "jalr":  return (a + imm) & MASK32        # 目标；最低位清零见 EX
    return 0


def _to_signed(x: int) -> int:
    x &= MASK32
    return x - (1 << 32) if (x & 0x80000000) else x


def _branch_taken(op: str, a: int, b: int) -> bool:
    sa, sb = _to_signed(a), _to_signed(b)
    if op == "beq":  return (a & MASK32) == (b & MASK32)
    if op == "bne":  return (a & MASK32) != (b & MASK32)
    if op == "blt":  return sa < sb
    if op == "bge":  return sa >= sb
    if op == "bltu": return (a & MASK32) < (b & MASK32)
    if op == "bgeu": return (a & MASK32) >= (b & MASK32)
    return False


# 把"字节数"映射到 load/store 指令
_LOAD_SPEC = {"lb": (1, True), "lh": (2, True), "lw": (4, True),
              "lbu": (1, False), "lhu": (2, False)}
_STORE_SPEC = {"sb": 1, "sh": 2, "sw": 4}


# ============================================================================
# Section 6: CPU 核心
# ============================================================================

@dataclass
class Stats:
    cycles: int = 0
    inst_retired: int = 0
    stalls: int = 0          # load-use 气泡数
    flushes: int = 0         # 分支错误预测导致的 flush 数（按指令条数）
    branch_count: int = 0
    branch_mispred: int = 0
    jal_count: int = 0
    jalr_count: int = 0

    @property
    def ipc(self) -> float:
        return self.inst_retired / self.cycles if self.cycles else 0.0

    @property
    def branch_accuracy(self) -> float:
        if self.branch_count == 0: return 0.0
        return 1.0 - self.branch_mispred / self.branch_count


class CPU:
    """RV32I 5 级流水线 CPU。"""

    def __init__(self, imem: List[int], dmem_size: int = 4096,
                 forward_enabled: bool = True,
                 predictor: Optional[TwoBitPredictor] = None) -> None:
        # 指令内存：每元素是一条 32-bit 指令字
        self.imem = imem
        self.dmem = Memory(dmem_size)
        self.rf = RegFile()
        self.pc = 0
        self.forward_enabled = forward_enabled
        self.bp = predictor if predictor is not None else TwoBitPredictor()
        self.stats = Stats()
        self.halted = False    # ECALL/EBREAK 触发

        # 双缓冲流水线寄存器
        self.f_if_id = PipeReg.bubble()
        self.f_id_ex = PipeReg.bubble()
        self.f_ex_mem = PipeReg.bubble()
        self.f_mem_wb = PipeReg.bubble()
        self.t_if_id = PipeReg.bubble()
        self.t_id_ex = PipeReg.bubble()
        self.t_ex_mem = PipeReg.bubble()
        self.t_mem_wb = PipeReg.bubble()

        # 跨阶段控制信号（EX 写，IF/ID 读）
        self._flush_request = False
        self._redirect_pc: Optional[int] = None
        self._stall_request = False
        # ecall/ebreak 进入流水线后，永久停止取新指（否则 ret 后代码会被错误重取）
        self.halt_fetch = False

        # 调试
        self.trace: List[str] = []
        self.enable_trace = False

    # ------------------------------------------------------------------
    # 主驱动
    # ------------------------------------------------------------------
    def run(self, max_cycles: int = 100000) -> Stats:
        """跑到流水线排空、或命中 ecall/ebreak、或达到 max_cycles。"""
        last_retired = -1
        same_count = 0
        while self.stats.cycles < max_cycles:
            self.step()
            # 流水线全空 → 程序结束
            if not (self.f_if_id.valid or self.f_id_ex.valid
                    or self.f_ex_mem.valid or self.f_mem_wb.valid):
                break
            # 死锁检测： retired 长时间不变且无 valid → 已 break；retired 不变但有 valid → 死锁
            if self.stats.inst_retired == last_retired:
                same_count += 1
                if same_count > 64:
                    raise RuntimeError(
                        f"CPU deadlock detected at cycle {self.stats.cycles}; "
                        f"PC=0x{self.pc:x}")
            else:
                same_count = 0
                last_retired = self.stats.inst_retired
            if self.halted and not (self.f_if_id.valid or self.f_id_ex.valid
                                    or self.f_ex_mem.valid or self.f_mem_wb.valid):
                break
        return self.stats

    def step(self) -> None:
        """执行一个周期。逆序调用各阶段（避免本周期写被同周期读）。"""
        self.stats.cycles += 1
        self._flush_request = False
        self._redirect_pc = None
        self._stall_request = False

        # 阶段 1: WB —— 从 f_mem_wb 写回 RegFile
        self._wb()
        # 阶段 2: MEM —— 从 f_ex_mem 访存，写 t_mem_wb
        self._mem()
        # 阶段 3: EX —— 从 f_id_ex + forwarding，写 t_ex_mem；分支解析
        self._ex()
        # 阶段 4: ID —— 从 f_if_id，检测 load-use stall，写 t_id_ex
        self._id()
        # 阶段 5: IF —— 取指、分支预测，写 t_if_id；next_pc 决定
        self._if()

        # —— commit 阶段：双缓冲提交 ——
        self.f_if_id = self.t_if_id
        self.f_id_ex = self.t_id_ex
        self.f_ex_mem = self.t_ex_mem
        self.f_mem_wb = self.t_mem_wb

        if self._redirect_pc is not None:
            self.pc = self._redirect_pc & MASK32
        elif not self._stall_request:
            self.pc = (self.pc + 4) & MASK32
        # stall 时不更新 PC，下周期重取

        if self.enable_trace:
            self.trace.append(
                f"cyc={self.stats.cycles:5d} pc=0x{self.pc:08x} "
                f"if_id={_fmt(self.f_if_id)} id_ex={_fmt(self.f_id_ex)} "
                f"ex_mem={_fmt(self.f_ex_mem)} mem_wb={_fmt(self.f_mem_wb)}")

    # ------------------------------------------------------------------
    # 各阶段
    # ------------------------------------------------------------------
    def _wb(self) -> None:
        wb = self.f_mem_wb
        if not wb.valid or wb.inst is None:
            return
        inst = wb.inst
        if inst.is_control:
            self.halted = True
        if inst.writes_rd:
            # 写回的是"最终结果"：load 用 mem_data，其余用 alu_result
            value = wb.mem_data if inst.is_load else wb.alu_result
            self.rf.write(inst.rd, value)
        self.stats.inst_retired += 1

    def _mem(self) -> None:
        ex = self.f_ex_mem
        if not ex.valid or ex.inst is None:
            self.t_mem_wb = PipeReg.bubble()
            return
        inst = ex.inst
        result = ex.alu_result
        if inst.is_load:
            size, signed = _LOAD_SPEC[inst.op]
            result = self.dmem.load(ex.alu_result, size, signed) & MASK32
        elif inst.is_store:
            size = _STORE_SPEC[inst.op]
            self.dmem.store(ex.alu_result, size, ex.rs2_val)
        # 推进到 MEM/WB
        self.t_mem_wb = PipeReg(valid=True, inst=inst,
                                alu_result=ex.alu_result,
                                mem_data=result,
                                rs1_val=ex.rs1_val, rs2_val=ex.rs2_val)

    def _ex(self) -> None:
        ide = self.f_id_ex
        if not ide.valid or ide.inst is None:
            self.t_ex_mem = PipeReg.bubble()
            return
        inst = ide.inst

        # —— Forwarding：决定 ALU 的两个源操作数 ——
        a = ide.rs1_val
        b = ide.rs2_val
        if self.forward_enabled:
            a = self._forward(ide.rs1_val, inst.rs1, inst.reads_rs1)
            b = self._forward(ide.rs2_val, inst.rs2, inst.reads_rs2)

        result = _alu(inst.op, a, b, inst.imm, inst.addr) & MASK32

        # —— 控制流解析（branch / jalr）——
        # JAL 在 IF 已预测且永远正确（target 静态已知），故 EX 不再处理 jal
        if inst.is_branch:
            self.stats.branch_count += 1
            actual_taken = _branch_taken(inst.op, a, b)
            predicted_taken = ide.predicted_taken
            if actual_taken != predicted_taken:
                # 错误预测：flush IF/ID 和 ID/EX
                self._flush_request = True
                target = (inst.addr + (inst.imm if actual_taken else 4)) & MASK32
                self._redirect_pc = target
                self.stats.flushes += 2
                self.stats.branch_mispred += 1
                self.bp.predictions += 1
                self.bp.mispredictions += 1
            else:
                self.bp.predictions += 1
            self.bp.update(inst.addr, actual_taken)

        elif inst.is_jalr:
            self.stats.jalr_count += 1
            target = (a + inst.imm) & ~1 & MASK32   # JALR 目标最低位清零
            # JALR 在 IF 没法预测（依赖 rs1），故总是当作"预测 not taken"
            #   → 实际总是 taken → 永远 flush 2
            self._flush_request = True
            self._redirect_pc = target
            self.stats.flushes += 2
            result = (inst.addr + 4) & MASK32        # rd = return addr

        elif inst.is_jal:
            self.stats.jal_count += 1
            # JAL 在 IF 已被静态预测（target = pc+imm），EX 只写返回地址到 rd
            result = (inst.addr + 4) & MASK32

        self.t_ex_mem = PipeReg(valid=True, inst=inst,
                                alu_result=result,
                                rs1_val=b if inst.is_store else ide.rs2_val,
                                rs2_val=b if inst.is_store else ide.rs2_val)

    def _forward(self, regfile_val: int, rs: int, reads: bool) -> int:
        """3 路转发：EX/MEM > MEM/WB > RegFile。"""
        if not reads or rs == 0:
            return regfile_val
        # 优先：紧邻的上一条指令（EX/MEM 槽）
        src = self.f_ex_mem
        if src.valid and src.inst is not None and src.inst.writes_rd \
                and src.inst.rd == rs and not src.inst.is_load:
            return src.alu_result
        # 次选：再上一条（MEM/WB 槽，含 load 数据）
        src = self.f_mem_wb
        if src.valid and src.inst is not None and src.inst.writes_rd \
                and src.inst.rd == rs:
            return src.mem_data if src.inst.is_load else src.alu_result
        return regfile_val

    def _id(self) -> None:
        # —— EX 阶段触发的 flush 也要冲掉 id_ex（否则 bne 后的顺序指令会泄漏）——
        if self._flush_request:
            self.t_id_ex = PipeReg.bubble()
            return
        if_id = self.f_if_id
        if not if_id.valid or if_id.inst is None:
            self.t_id_ex = PipeReg.bubble()
            return
        inst = if_id.inst

        # —— 一旦 ecall/ebreak 进入 ID，永久停止后续 IF ——
        if inst.is_control:
            self.halt_fetch = True

        # —— Load-use hazard 检测：f_id_ex 是 load，且其 rd 被当前指令用 ——
        prev = self.f_id_ex
        if (self.forward_enabled and prev.valid and prev.inst is not None
                and prev.inst.is_load and prev.inst.writes_rd
                and prev.inst.rd != 0
                and (prev.inst.rd == inst.rs1 if inst.reads_rs1 else False)
                or (prev.valid and prev.inst is not None
                    and prev.inst.is_load and prev.inst.writes_rd
                    and prev.inst.rd != 0
                    and inst.reads_rs2 and prev.inst.rd == inst.rs2)):
            # 插入 1 cycle 气泡：t_id_ex 为空，IF 不取新指令
            self.t_id_ex = PipeReg.bubble()
            self._stall_request = True
            self.stats.stalls += 1
            # 保留 IF/ID（让下周期重新 ID 同一条指令）
            self.t_if_id = if_id
            return

        # —— 读寄存器，推进到 ID/EX ——
        self.t_id_ex = PipeReg(valid=True, inst=inst,
                               rs1_val=self.rf.read(inst.rs1),
                               rs2_val=self.rf.read(inst.rs2),
                               predicted_taken=if_id.predicted_taken,
                               predicted_target=if_id.predicted_target)

    def _if(self) -> None:
        # —— 若 EX 阶段发了 flush，把 IF/ID 槽冲掉 ——
        if self._flush_request:
            self.t_if_id = PipeReg.bubble()
            return
        # —— 若 ID 阶段发了 stall，IF/ID 已被 ID 保留，不取新指令 ——
        if self._stall_request:
            return  # t_if_id 已由 _id() 写好
        # —— ecall/ebreak 已进入流水线，永久停止取指 ——
        if self.halt_fetch:
            self.t_if_id = PipeReg.bubble()
            return

        pc = self.pc
        idx = pc // 4
        if idx < 0 or idx >= len(self.imem):
            self.t_if_id = PipeReg.bubble()
            return
        raw = self.imem[idx] & MASK32
        inst = decode(raw, pc)

        # —— 分支预测：决定本周期末的 next_pc ——
        predicted_taken = False
        target = (pc + 4) & MASK32
        if inst.is_branch:
            predicted_taken = self.bp.predict(pc)
            target = (pc + inst.imm) & MASK32 if predicted_taken else (pc + 4) & MASK32
        elif inst.is_jal:
            target = (pc + inst.imm) & MASK32
        # 若预测了 taken，本周期就改 _redirect_pc，使下周期从 target 取
        if predicted_taken or inst.is_jal:
            self._redirect_pc = target

        self.t_if_id = PipeReg(valid=True, inst=inst,
                               predicted_taken=predicted_taken,
                               predicted_target=target)


# ============================================================================
# Section 7: 工具
# ============================================================================

def _fmt(reg: PipeReg) -> str:
    if not reg.valid or reg.inst is None:
        return "----"
    return f"{reg.inst.op:8s}@0x{reg.inst.addr:04x}"


# ============================================================================
# Section 8: 内置自测程序（不依赖外部文件即可验证模拟器）
# ============================================================================

def build_sum_program() -> Tuple[List[int], int, int]:
    """sum = 1+2+...+10 = 55，结果在 x1。
    返回 (指令列表, 结果寄存器索引, 期望值)。

    注意：用 assembler.assemble() 生成 hex，避免手算 B-type 立即数编码出错。
    原骨架里的硬编码 hex (0x00309463) 把 bne 编成了 +8 而非 -8，循环只跑一次。
    """
    from assembler import assemble
    src = """
        addi x1, x0, 0          # sum = 0
        addi x2, x0, 1          # i = 1
        addi x3, x0, 11         # end = 11
    loop:
        add  x1, x1, x2         # sum += i
        addi x2, x2, 1          # i++
        bne  x2, x3, loop       # if i != 11, goto loop
        ecall                   # halt
    """
    return assemble(src), 1, 55


# ============================================================================
# Section 9: CLI
# ============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="RV32I 5-stage pipeline simulator")
    parser.add_argument("program", nargs="?", default=None,
                        help="program file (.hex lines or .s via mini-assembler)")
    parser.add_argument("--trace", action="store_true", help="dump per-cycle trace")
    parser.add_argument("--no-forward", action="store_true",
                        help="disable forwarding (for teaching)")
    parser.add_argument("--max-cycles", type=int, default=100000)
    args = parser.parse_args(argv)

    if args.program is None:
        prog, res_reg, expected = build_sum_program()
        print(f"[builtin] sum(1..10) program, expect x{res_reg} = {expected}")
    else:
        # 见同目录 assembler.py；这里若给 .s 走汇编器，.hex 走直接加载
        try:
            from assembler import assemble_program
            prog, res_reg, expected = assemble_program(args.program)
        except ImportError:
            prog, res_reg, expected = load_hex(args.program), None, None

    cpu = CPU(prog, forward_enabled=not args.no_forward)
    cpu.enable_trace = args.trace
    stats = cpu.run(max_cycles=args.max_cycles)

    print(f"cycles         : {stats.cycles}")
    print(f"inst retired   : {stats.inst_retired}")
    print(f"IPC            : {stats.ipc:.3f}")
    print(f"stalls (load-use): {stats.stalls}")
    print(f"flushes (mispred): {stats.flushes} ({stats.branch_mispred} mispredictions)")
    print(f"branches       : {stats.branch_count}  "
          f"(accuracy {stats.branch_accuracy * 100:.1f}%)")
    print(f"JAL/JALR       : {stats.jal_count}/{stats.jalr_count}")

    if res_reg is not None:
        actual = cpu.rf.read(res_reg)
        status = "PASS" if actual == expected else "FAIL"
        print(f"result x{res_reg}    : {actual}  (expect {expected})  [{status}]")

    if args.trace:
        print("\n--- trace (last 30 cycles) ---")
        for line in cpu.trace[-30:]:
            print(line)
    return 0


def load_hex(path: str) -> List[int]:
    """每行一个 32-bit 十六进制字（0x........ 或 8 位 hex）。"""
    words = []
    with open(path) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if not line.startswith("0x"):
                line = "0x" + line
            words.append(int(line, 16) & MASK32)
    return words


if __name__ == "__main__":
    sys.exit(main())
