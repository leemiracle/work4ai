#!/usr/bin/env python3
"""
tinyasm — 参照 NASM 的迷你 x86-64 汇编器

参照：NASM / GNU as / LLVM MC
csdiy 对应：csapp Ch3(机器级表示) + CS143 编译器后端

核心：助记符 → 机器码（单遍扫描 + 操作码表）
"""
import struct

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 指令编码表（参照 Intel SDM Vol.2，简化版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 寄存器编码（参照 csapp Ch3 图 3.30）
REGISTERS = {
    "rax": 0, "rcx": 1, "rdx": 2, "rbx": 3,
    "rsp": 4, "rbp": 5, "rsi": 6, "rdi": 7,
    "eax": 0, "ecx": 1, "edx": 2, "ebx": 3,
    "r8": 8, "r9": 9, "r10": 10, "r11": 11,
    "r12": 12, "r13": 13, "r14": 14, "r15": 15,
}

# 指令表：(opcode_byte, operand_types)
# 类型：reg, imm, mem（简化：只支持 reg 和 imm）
INSTRUCTIONS = {
    "mov": {"reg_imm": 0xB8, "reg_reg": 0x89},  # MOV r64, imm32 / MOV r64, r64
    "add": {"reg_reg": 0x01},
    "sub": {"reg_reg": 0x29},
    "push": {"reg": 0x50},
    "pop": {"reg": 0x58},
    "ret": {"none": 0xC3},
    "nop": {"none": 0x90},
    "syscall": {"none": 0x0F05},
    "int": {"imm": 0xCD},
    "jmp": {"imm": 0xE9},
    "cmp": {"reg_reg": 0x39},
}

class TinyAssembler:
    """
    单遍汇编器（参照 NASM 的单遍模式）

    流程：
    1. 逐行读取汇编代码
    2. 解析助记符 + 操作数
    3. 查操作码表 → 编码为机器码
    4. 维护标签表（用于跳转）
    """
    def __init__(self):
        self.labels = {}        # 标签 → 地址
        self.output = bytearray()
        self.base_addr = 0

    def assemble(self, code: str) -> bytes:
        lines = code.strip().split("\n")
        # 第一遍：收集标签地址
        offset = 0
        clean_lines = []
        for line in lines:
            line = line.split(";")[0].strip()  # 去注释
            if not line: continue
            if line.endswith(":"):
                label = line[:-1].strip()
                self.labels[label] = offset
                continue
            # 估算指令长度（粗略）
            offset += self._estimate_size(line)
            clean_lines.append(line)

        # 第二遍：编码
        self.output = bytearray()
        for line in clean_lines:
            machine = self._encode(line)
            self.output.extend(machine)

        return bytes(self.output)

    def _estimate_size(self, line: int):
        """粗略估算指令大小"""
        parts = line.split(None, 1)
        mnemonic = parts[0].lower()
        if mnemonic in ("ret", "nop"): return 1
        if mnemonic == "syscall": return 2
        if mnemonic in ("push", "pop") and len(parts) > 1: return 1
        if mnemonic == "mov" and "imm" in self._operand_types(parts[1] if len(parts)>1 else ""):
            return 5  # REX + opcode + imm32
        return 2  # 默认

    def _operand_types(self, operands_str):
        types = []
        for op in operands_str.split(","):
            op = op.strip()
            if op.startswith("0x") or op.lstrip("-").isdigit():
                types.append("imm")
            elif op in REGISTERS:
                types.append("reg")
            else:
                types.append("mem")
        return types

    def _encode(self, line: str) -> bytes:
        """编码一行汇编 → 机器码"""
        parts = line.split(None, 1)
        mnemonic = parts[0].lower()
        operands = [o.strip() for o in parts[1].split(",")] if len(parts) > 1 else []

        if mnemonic not in INSTRUCTIONS:
            raise ValueError(f"Unknown instruction: {mnemonic}")

        # 无操作数指令
        if not operands:
            opcode = INSTRUCTIONS[mnemonic].get("none")
            if opcode is None:
                raise ValueError(f"{mnemonic} requires operands")
            if opcode > 0xFF:
                return struct.pack(">H", opcode)  # 2 字节（syscall）
            return bytes([opcode])

        # 单操作数
        if mnemonic in ("push", "pop"):
            reg = operands[0].lower()
            if reg in REGISTERS:
                base = INSTRUCTIONS[mnemonic]["reg"]
                reg_code = REGISTERS[reg]
                if reg_code >= 8:
                    return bytes([0x41, base + (reg_code & 7)])  # REX prefix
                return bytes([base + reg_code])

        # MOV reg, imm
        if mnemonic == "mov":
            dst, src = operands[0].lower(), operands[1]
            if dst in REGISTERS and (src.startswith("0x") or src.lstrip("-").isdigit()):
                reg_code = REGISTERS[dst]
                imm = int(src, 0) & 0xFFFFFFFF
                if reg_code >= 8:
                    return bytes([0x49, 0xB8 + (reg_code & 7)]) + struct.pack("<Q", imm)  # REX.W + mov r64, imm64
                return bytes([0xB8 + reg_code]) + struct.pack("<I", imm)
            # MOV reg, reg
            if dst in REGISTERS and src.lower() in REGISTERS:
                dst_code = REGISTERS[dst]
                src_code = REGISTERS[src.lower()]
                modrm = 0xC0 | (src_code << 3) | (dst_code & 7)
                return bytes([0x48, 0x89, modrm])

        # ADD/SUB/CMP reg, reg
        if mnemonic in ("add", "sub", "cmp") and len(operands) == 2:
            dst, src = operands[0].lower(), operands[1].lower()
            if dst in REGISTERS and src in REGISTERS:
                opcode = INSTRUCTIONS[mnemonic]["reg_reg"]
                modrm = 0xC0 | (REGISTERS[src] << 3) | (REGISTERS[dst] & 7)
                return bytes([0x48, opcode, modrm])

        # 默认：返回 nop（占位）
        return bytes([0x90])

    def disassemble(self, addr=0):
        """显示标签表（参照 objdump 的符号表）"""
        print("  Labels:")
        for name, offset in sorted(self.labels.items(), key=lambda x: x[1]):
            print(f"    {self.base_addr + offset:#010x} <{name}>")

def main():
    print("tinyasm — x86-64 汇编器（参照 NASM + csapp Ch3）\n")

    code = """
    ; 简化版汇编程序
    start:
        mov rax, 42
        mov rbx, 10
        add rax, rbx
        push rbp
        mov rbp, rsp
        nop
        pop rbp
        ret
    """

    asm = TinyAssembler()
    machine_code = asm.assemble(code)

    print("  汇编代码:")
    for line in code.strip().split("\n"):
        print(f"    {line}")

    print(f"\n  机器码 ({len(machine_code)} 字节):")
    for i in range(0, len(machine_code), 16):
        chunk = machine_code[i:i+16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        print(f"    {i:04x}: {hex_str}")

    asm.disassemble()

    print("\n  对照 csapp Ch3:")
    print("    mov rax, 42  → B8 2a 00 00 00  (mov eax, imm32)")
    print("    ret          → C3               (near return)")

if __name__ == "__main__": main()
