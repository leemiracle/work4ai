#!/usr/bin/env python3
"""
assembler.py — 迷你 RV32I 汇编器（Capstone-B 配套）

提供:
    assemble(source: str) -> List[int]              # 汇编字符串
    assemble_file(path: str) -> List[int]           # 汇编文件
    assemble_program(path) -> (words, result_reg, expected)  # CLI 友好包装

支持:
- 全部 RV32I 40 条基础指令
- 32 个 ABI 别名（x0..x31, zero/ra/sp/gp/tp/t0-6/a0-7/s0-11/fp）
- 标签（label:）+ 2-pass 解析
- 伪指令: nop/li/mv/neg/not/j/jr/ret/beqz/bnez/seqz/snez/call/tail
- 注释: `#` 行内注释
- 直接字: `.word 0x00309463` (调试用)
- 内存数据段: `.data` 之后用 `.word value1, value2, ...`

设计意图:
手算 RV32I 立即数编码（B-type imm[12|10:5|4:1|11] 那种"打乱顺序"）极不可靠，
本汇编器把"人写的助记符"转成"机器可以直接跑的 32-bit 字"，让 Capstone-B 的
测试程序（sum/fib/bubble_sort）可读、可改、可信。
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

MASK32 = 0xFFFFFFFF

REGISTERS: Dict[str, int] = {f"x{i}": i for i in range(32)}
REGISTERS.update({
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
    "t0": 5, "t1": 6, "t2": 7,
    "s0": 8, "fp": 8, "s1": 9,
    "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14,
    "a5": 15, "a6": 16, "a7": 17,
    "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "s8": 24, "s9": 25, "s10": 26, "s11": 27,
    "t3": 28, "t4": 29, "t5": 30, "t6": 31,
})


# ============================================================================
# 指令编码表
# ============================================================================

def _bits(value: int, hi: int, lo: int) -> int:
    """取 value[hi:lo]（含端点），例如 _bits(x, 11, 5)。"""
    mask = ((1 << (hi - lo + 1)) - 1) << lo
    return (value & mask) >> lo


def _reg(name: str) -> int:
    name = name.strip().lower()
    if name not in REGISTERS:
        raise AssemblerError(f"unknown register: {name!r}")
    return REGISTERS[name]


def _imm(tok: str, symbols: Optional[Dict[str, int]] = None) -> int:
    tok = tok.strip()
    if symbols is not None and tok in symbols:
        return symbols[tok]
    try:
        # 支持 0x.. / -0x.. / 十进制
        return int(tok, 0)
    except ValueError as e:
        raise AssemblerError(f"bad immediate {tok!r}: {e}")


def _encode_r(opcode: int, rd: int, funct3: int, rs1: int, rs2: int, funct7: int) -> int:
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def _encode_i(opcode: int, rd: int, funct3: int, rs1: int, imm: int) -> int:
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def _encode_i_shift(opcode: int, rd: int, funct3: int, rs1: int, shamt: int, funct7: int) -> int:
    """SLLI/SRLI/SRAI：imm[11:5]=funct7，imm[4:0]=shamt。"""
    return ((funct7 & 0x7F) << 25) | ((shamt & 0x1F) << 20) | (rs1 << 15) | \
           (funct3 << 12) | (rd << 7) | opcode


def _encode_s(opcode: int, funct3: int, rs1: int, rs2: int, imm: int) -> int:
    imm &= 0xFFF
    imm_hi = _bits(imm, 11, 5)
    imm_lo = _bits(imm, 4, 0)
    return (imm_hi << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | \
           (imm_lo << 7) | opcode


def _encode_b(opcode: int, funct3: int, rs1: int, rs2: int, imm: int) -> int:
    # imm 是 PC 相对，单位是字节（最低位必须为 0）
    if imm & 1:
        raise AssemblerError(f"branch target not 2-aligned: imm={imm}")
    imm &= 0x1FFF   # 13-bit
    b12  = _bits(imm, 12, 12)
    b10_5 = _bits(imm, 10, 5)
    b4_1  = _bits(imm, 4, 1)
    b11   = _bits(imm, 11, 11)
    # imm[4:1] → inst[11:8]，故 b4_1 左移 8（注意不是 11！）
    return (b12 << 31) | (b10_5 << 25) | (rs2 << 20) | (rs1 << 15) | \
           (funct3 << 12) | (b4_1 << 8) | (b11 << 7) | opcode


def _encode_u(opcode: int, rd: int, imm: int) -> int:
    """RISC-V 汇编约定：用户写 lui rd, X 的 X 是要放进 inst[31:12] 的 20 位字段值，
    需要左移 12 位。例如 lui a0, 0x12345 编码后 imm 字段 = 0x12345 << 12。"""
    return ((imm & 0xFFFFF) << 12) | (rd << 7) | opcode


def _encode_j(opcode: int, rd: int, imm: int) -> int:
    if imm & 1:
        raise AssemblerError(f"jal target not 2-aligned: imm={imm}")
    imm &= 0x1FFFFF  # 21-bit
    b20    = _bits(imm, 20, 20)
    b10_1  = _bits(imm, 10, 1)
    b11    = _bits(imm, 11, 11)
    b19_12 = _bits(imm, 19, 12)
    return (b20 << 31) | (b19_12 << 12) | (b11 << 20) | (b10_1 << 21) | \
           (rd << 7) | opcode


# ============================================================================
# 指令分发表
# ============================================================================

# 每项: mnemonic -> handler(operands, ctx) -> 32-bit int  （ctx 含 symbols/pc）
# 伪指令在 Pass 1 展开（可能展开成多条），Pass 2 用真实指令编码。

class AssemblerError(Exception):
    pass


# R-type: add/sub/sll/slt/sltu/xor/srl/sra/or/and
_R_TYPE = {
    "add":  (0x00, 0x00),  # (funct7, funct3)
    "sub":  (0x20, 0x00),
    "sll":  (0x00, 0x01),
    "slt":  (0x00, 0x02),
    "sltu": (0x00, 0x03),
    "xor":  (0x00, 0x04),
    "srl":  (0x00, 0x05),
    "sra":  (0x20, 0x05),
    "or":   (0x00, 0x06),
    "and":  (0x00, 0x07),
}

# I-type ALU: addi/slti/sltiu/xori/ori/andi
_I_ALU = {
    "addi":  0x0,
    "slti":  0x2,
    "sltiu": 0x3,
    "xori":  0x4,
    "ori":   0x6,
    "andi":  0x7,
}

# Shift-immediate: slli/srli/srai
_I_SHIFT = {
    "slli": (0x00, 0x1),
    "srli": (0x00, 0x5),
    "srai": (0x20, 0x5),
}

# Load: lb/lh/lw/lbu/lhu
_LOAD = {
    "lb":  0x0, "lh":  0x1, "lw":  0x2,
    "lbu": 0x4, "lhu": 0x5,
}

# Store: sb/sh/sw
_STORE = {
    "sb": 0x0, "sh": 0x1, "sw": 0x2,
}

# Branch: beq/bne/blt/bge/bltu/bgeu
_BRANCH = {
    "beq":  0x0, "bne":  0x1,
    "blt":  0x4, "bge":  0x5,
    "bltu": 0x6, "bgeu": 0x7,
}


def _split_operands(rest: str) -> List[str]:
    """切分 'x1, x2, 0x10' → ['x1', 'x2', '0x10']，容忍空白。"""
    return [tok.strip() for tok in rest.split(",") if tok.strip()]


# ============================================================================
# Pass 1: 解析行 → (mnemonic, operands, pc)；处理伪指令展开
# ============================================================================

# 伪指令展开表：每个伪指令返回一个 list of (mnemonic, operands_str) 元组
# 注意：展开里的 label 引用留到 Pass 2 解析
def _expand_pseudo(mnem: str, ops: List[str], pc: int,
                   symbols: Dict[str, int]) -> List[Tuple[str, List[str]]]:
    """返回展开后的真实指令列表（可能多条）。
    每条 = (mnemonic, operands_list)。
    """

    if mnem == "nop":
        return [("addi", ["x0", "x0", "0"])]
    if mnem == "mv":
        return [("addi", [ops[0], ops[1], "0"])]
    if mnem == "neg":
        return [("sub", [ops[0], "x0", ops[1]])]
    if mnem == "not":
        return [("xori", [ops[0], ops[1], "-1"])]
    if mnem == "seqz":
        return [("sltiu", [ops[0], ops[1], "1"])]
    if mnem == "snez":
        return [("sltu", [ops[0], "x0", ops[1]])]
    if mnem == "j":
        return [("jal", ["x0", ops[0]])]
    if mnem == "jr":
        # jr rs  →  jalr x0, rs, 0
        return [("jalr", ["x0", ops[0], "0"])]
    if mnem == "ret":
        return [("jalr", ["x0", "ra", "0"])]
    if mnem in ("beqz",):
        return [("beq", [ops[0], "x0", ops[1]])]
    if mnem in ("bnez",):
        return [("bne", [ops[0], "x0", ops[1]])]
    # —— 反向分支伪指令（操作数顺序翻转）——
    # ble rs, rt  ⟷  bge rt, rs
    if mnem == "ble":  return [("bge",  [ops[1], ops[0], ops[2]])]
    if mnem == "bgt":  return [("blt",  [ops[1], ops[0], ops[2]])]
    if mnem == "bleu": return [("bgeu", [ops[1], ops[0], ops[2]])]
    if mnem == "bgtu": return [("bltu", [ops[1], ops[0], ops[2]])]
    if mnem == "call":
        # call offset  →  jal ra, offset
        return [("jal", ["ra", ops[0]])]
    if mnem == "tail":
        return [("jal", ["x0", ops[0]])]
    if mnem == "li":
        rd, imm = ops[0], _imm(ops[1], symbols)
        if -2048 <= imm < 2048:
            return [("addi", [rd, "x0", str(imm)])]
        # 否则 lui + addi（处理 addi 的 12-bit 符号位）
        # 把 imm 拆为 hi20 + lo12，hi20 要补正 lo12 的负号
        lo = imm & 0xFFF
        # 若 lo 的符号位为 1（即 lo >= 0x800），lui 需多 +1
        hi = (imm >> 12) & 0xFFFFF
        if lo & 0x800:
            hi = (hi + 1) & 0xFFFFF
        # lui 的操作数约定是 inst[31:12] 字段值（即 20 位），直接传 hi
        return [
            ("lui",  [rd, str(hi)]),
            ("addi", [rd, rd, str(_sext(lo, 12))]),
        ]
    # 非伪指令，原样返回
    return [(mnem, ops)]


def _sext(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


# ============================================================================
# Pass 2: 编码每条指令
# ============================================================================

def encode_instruction(mnem: str, ops: List[str], pc: int,
                       symbols: Dict[str, int]) -> int:
    """编码单条真实指令（mnem 已是真实指令，非伪指令）。"""

    # R-type
    if mnem in _R_TYPE:
        funct7, funct3 = _R_TYPE[mnem]
        if len(ops) != 3:
            raise AssemblerError(f"{mnem} expects 3 operands, got {ops}")
        rd, rs1, rs2 = _reg(ops[0]), _reg(ops[1]), _reg(ops[2])
        return _encode_r(0x33, rd, funct3, rs1, rs2, funct7)

    # I-type ALU
    if mnem in _I_ALU:
        funct3 = _I_ALU[mnem]
        rd, rs1, imm = _reg(ops[0]), _reg(ops[1]), _imm(ops[2], symbols)
        return _encode_i(0x13, rd, funct3, rs1, imm)

    # Shift-imm
    if mnem in _I_SHIFT:
        funct7, funct3 = _I_SHIFT[mnem]
        rd, rs1, shamt = _reg(ops[0]), _reg(ops[1]), _imm(ops[2], symbols)
        if not (0 <= shamt < 32):
            raise AssemblerError(f"shift amount out of range: {shamt}")
        return _encode_i_shift(0x13, rd, funct3, rs1, shamt, funct7)

    # Load
    if mnem in _LOAD:
        funct3 = _LOAD[mnem]
        # 格式: lw rd, imm(rs1)
        rd, mem_op = ops[0], ops[1]
        imm, rs1 = _parse_mem_operand(mem_op, symbols)
        return _encode_i(0x03, _reg(rd), funct3, rs1, imm)

    # Store
    if mnem in _STORE:
        funct3 = _STORE[mnem]
        # 格式: sw rs2, imm(rs1)
        rs2_tok, mem_op = ops[0], ops[1]
        imm, rs1 = _parse_mem_operand(mem_op, symbols)
        return _encode_s(0x23, funct3, rs1, _reg(rs2_tok), imm)

    # Branch
    if mnem in _BRANCH:
        funct3 = _BRANCH[mnem]
        rs1, rs2, label = _reg(ops[0]), _reg(ops[1]), ops[2]
        target = _resolve_label(label, symbols, pc)
        return _encode_b(0x63, funct3, rs1, rs2, target - pc)

    # JAL
    if mnem == "jal":
        rd_tok, label = ops[0], ops[1]
        target = _resolve_label(label, symbols, pc)
        return _encode_j(0x6F, _reg(rd_tok), target - pc)

    # JALR
    if mnem == "jalr":
        # 格式1: jalr rd, rs1, imm   格式2: jalr rd, imm(rs1)
        if len(ops) == 3:
            rd, rs1, imm = _reg(ops[0]), _reg(ops[1]), _imm(ops[2], symbols)
        elif len(ops) == 2 and "(" in ops[1]:
            rd, (imm, rs1) = _reg(ops[0]), _parse_mem_operand(ops[1], symbols)
        else:
            raise AssemblerError(f"jalr bad operands: {ops}")
        return _encode_i(0x67, rd, 0x0, rs1, imm)

    # LUI
    if mnem == "lui":
        rd, imm = _reg(ops[0]), _imm(ops[1], symbols)
        return _encode_u(0x37, rd, imm)

    # AUIPC
    if mnem == "auipc":
        rd, imm = _reg(ops[0]), _imm(ops[1], symbols)
        return _encode_u(0x17, rd, imm)

    # FENCE
    if mnem == "fence":
        return 0x0000000F

    # ECALL / EBREAK
    if mnem == "ecall":
        return 0x00000073
    if mnem == "ebreak":
        return 0x00100073

    raise AssemblerError(f"unknown instruction: {mnem!r}")


def _parse_mem_operand(tok: str, symbols: Dict[str, int]) -> Tuple[int, int]:
    """解析 'imm(rs1)' 或 '(rs1)' → (imm, rs1_idx)。"""
    m = re.match(r"^\s*(-?(?:0x)?[0-9a-fA-F]+)?\s*\(\s*(\w+)\s*\)\s*$", tok)
    if not m:
        # 也接受 'rs1' 形式（imm=0）
        return 0, _reg(tok)
    imm_str, reg_str = m.group(1), m.group(2)
    imm = _imm(imm_str, symbols) if imm_str else 0
    return imm, _reg(reg_str)


def _resolve_label(tok: str, symbols: Dict[str, int], pc: int) -> int:
    if tok in symbols:
        return symbols[tok]
    # 也可能是纯数字
    try:
        return _imm(tok, symbols)
    except AssemblerError:
        raise AssemblerError(f"undefined label: {tok!r} (pc=0x{pc:x})")


# ============================================================================
# Lexer + 主流程
# ============================================================================

def _tokenize_line(line: str) -> Tuple[Optional[str], str, str]:
    """返回 (label, mnemonic, rest)。
    label 仅当行首是 'label:' 时返回。
    """
    # 去注释
    line = line.split("#", 1)[0].strip()
    if not line:
        return None, "", ""

    label = None
    # 形如 'label: rest' 或 'label:'
    m = re.match(r"^([A-Za-z_][A-Za-z_0-9]*)\s*:\s*(.*)$", line)
    if m:
        label = m.group(1)
        line = m.group(2).strip()

    if not line:
        return label, "", ""

    parts = line.split(None, 1)
    mnemonic = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""
    return label, mnemonic, rest


def assemble(source: str) -> List[int]:
    """汇编字符串源码，返回 32-bit 字列表。"""
    lines = source.splitlines()

    # —— Pass 1: 收集标签，记录每条"逻辑指令"的 (pc, mnem, ops) ——
    # 同时处理 .data/.word 段。
    pc = 0
    symbols: Dict[str, int] = {}
    items: List[Tuple[int, str, List[str]]] = []  # (pc, mnem, ops)
    raw_words: List[Tuple[int, int]] = []         # (pc, word)  来自 .word

    pending_labels: List[str] = []  # 当前未绑定的标签（等下条指令时挂上）
    section = "text"

    for line_no, raw_line in enumerate(lines, 1):
        try:
            label, mnem, rest = _tokenize_line(raw_line)
            if label:
                pending_labels.append(label)

            if not mnem:
                continue

            ops = _split_operands(rest)

            if mnem == ".text":
                section = "text"
                continue
            if mnem == ".data":
                section = "data"
                continue
            if mnem == ".word":
                # 每个逗号分隔的值都是一个 32-bit 字
                for tok in ops:
                    word = _imm(tok, symbols) & MASK32
                    for lbl in pending_labels:
                        symbols[lbl] = pc
                    pending_labels.clear()
                    raw_words.append((pc, word))
                    pc += 4
                continue
            if mnem.startswith("."):
                # 其他 directive 暂不支持
                continue

            if section != "text":
                continue

            # 伪指令展开
            expanded = _expand_pseudo(mnem, ops, pc, symbols)
            for sub_mnem, sub_ops in expanded:
                for lbl in pending_labels:
                    symbols[lbl] = pc
                pending_labels.clear()
                items.append((pc, sub_mnem, sub_ops))
                pc += 4

        except AssemblerError as e:
            raise AssemblerError(f"line {line_no}: {e}") from e

    if pending_labels:
        # 末尾标签（指向程序结束）
        for lbl in pending_labels:
            symbols[lbl] = pc

    # —— Pass 2: 编码 ——
    out: Dict[int, int] = {}
    for pc_i, mnem, ops in items:
        try:
            out[pc_i] = encode_instruction(mnem, ops, pc_i, symbols) & MASK32
        except AssemblerError as e:
            raise AssemblerError(f"encode {mnem} {ops} @0x{pc_i:x}: {e}") from e
    for pc_i, word in raw_words:
        out[pc_i] = word

    # 排序输出
    return [out[k] for k in sorted(out.keys())]


def assemble_file(path: str) -> List[int]:
    with open(path) as f:
        return assemble(f.read())


def assemble_program(path: str) -> Tuple[List[int], Optional[int], Optional[int]]:
    """CLI 友好：返回 (words, result_reg, expected)。
    约定源文件可用 '# @expect: rd=N expected=M' 注解声明结果。"""
    result_reg: Optional[int] = None
    expected: Optional[int] = None
    with open(path) as f:
        src = f.read()
    for m in re.finditer(r"#\s*@expect:\s*x?(\d+)\s*=\s*(-?\d+)", src):
        result_reg, expected = int(m.group(1)), int(m.group(2))
        break
    return assemble(src), result_reg, expected


# ============================================================================
# Self-test
# ============================================================================

if __name__ == "__main__":
    test_src = """
        # sum 1..10
        addi x1, x0, 0          # sum = 0
        addi x2, x0, 1          # i = 1
        addi x3, x0, 11         # end = 11
    loop:
        add  x1, x1, x2         # sum += i
        addi x2, x2, 1          # i++
        bne  x2, x3, loop       # if i != 11, loop
        ecall                   # halt
    """
    words = assemble(test_src)
    print(f"assembled {len(words)} instructions:")
    for i, w in enumerate(words):
        print(f"  0x{i*4:02x}: 0x{w:08x}")
