#!/usr/bin/env python3
"""
tinylinker — 参照 ld/lld 的迷你链接器

参照：GNU ld / LLVM lld / mold
csdiy 对应：csapp Ch7(链接) + CS143 编译器

核心：符号解析 + 重定位 + 输出可执行文件
"""
import struct

class Symbol:
    def __init__(self, name, addr=0, defined=False, section=None):
        self.name = name; self.addr = addr
        self.defined = defined; self.section = section

class Relocation:
    def __init__(self, offset, sym_name, type="R_X86_64_PC32", addend=0):
        self.offset = offset; self.sym_name = sym_name
        self.type = type; self.addend = addend

class ObjectFile:
    """简化版 .o 文件（参照 ELF relocatable）"""
    def __init__(self, name):
        self.name = name
        self.symbols: dict[str, Symbol] = {}
        self.relocations: list[Relocation] = []
        self.text = bytearray()  # .text section（代码）
        self.data = bytearray()  # .data section

    def add_symbol(self, name, addr=0, section="text"):
        self.symbols[name] = Symbol(name, addr, True, section)

    def add_extern(self, name):
        self.symbols[name] = Symbol(name, defined=False)

    def add_relocation(self, offset, sym_name, addend=0):
        self.relocations.append(Relocation(offset, sym_name, addend=addend))

    def append_text(self, code: bytes):
        self.text.extend(code)

class TinyLinker:
    """
    链接器（参照 csapp Ch7 + ld）

    步骤：
    1. 符号解析：收集所有 .o 的符号表 → 合并为全局符号表
    2. 重定位：对每个重定位条目，用全局符号表地址修补代码
    3. 输出：合并所有 section → 生成"可执行文件"
    """
    def __init__(self):
        self.objects: list[ObjectFile] = []
        self.global_symbols: dict[str, Symbol] = {}

    def add_object(self, obj: ObjectFile):
        self.objects.append(obj)

    def link(self) -> bytes:
        """链接所有 .o → 输出合并后的 binary"""
        # ① 符号解析（参照 csapp Ch7 §7.6.1）
        # 分配地址（简化：按顺序排布）
        text_base = 0x400000
        data_base = 0x600000
        current_text = text_base
        current_data = data_base

        for obj in self.objects:
            obj.text_base = current_text
            obj.data_base = current_data
            # 注册已定义符号
            for sym in obj.symbols.values():
                if sym.defined:
                    if sym.section == "text":
                        sym.addr = current_text + sym.addr
                    elif sym.section == "data":
                        sym.addr = current_data + sym.addr
                    self.global_symbols[sym.name] = sym
            current_text += len(obj.text)
            current_data += len(obj.data)

        # 检查未定义符号
        for obj in self.objects:
            for sym in obj.symbols.values():
                if not sym.defined and sym.name not in self.global_symbols:
                    raise ValueError(f"Undefined symbol: {sym.name}")

        # ② 重定位（参照 csapp Ch7 §7.7）
        for obj in self.objects:
            for rel in obj.relocations:
                target_sym = self.global_symbols.get(rel.sym_name)
                if not target_sym:
                    raise ValueError(f"Relocation symbol not found: {rel.sym_name}")
                # 修补 .text 中的地址引用（简化版）
                abs_offset = rel.offset  # 在 obj.text 内的偏移
                patch_value = target_sym.addr + rel.addend
                if abs_offset + 4 <= len(obj.text):
                    struct.pack_into("<I", obj.text, abs_offset, patch_value & 0xFFFFFFFF)

        # ③ 输出（合并所有 section）
        output = bytearray()
        for obj in self.objects:
            output.extend(obj.text)

        return bytes(output)

    def symbol_table_dump(self):
        """符号表（参照 nm 命令）"""
        print(f"\n  {'Symbol':20s} {'Address':12s} {'Section'}")
        print(f"  {'─'*20} {'─'*12} {'─'*10}")
        for name, sym in sorted(self.global_symbols.items(), key=lambda x: x[1].addr):
            print(f"  {name:20s} {sym.addr:#012x} {sym.section}")

def main():
    print("tinylinker — 链接器（参照 ld/lld + csapp Ch7）\n")

    # 创建两个 .o 文件
    main_obj = ObjectFile("main.o")
    main_obj.append_text(b"\x55\x48\x89\xe5")  # push rbp; mov rbp, rsp
    main_obj.append_text(b"\xb8\x00\x00\x00\x00")  # mov eax, 0 (placeholder for message addr)
    main_obj.add_symbol("main", 0, "text")
    main_obj.add_extern("message")
    main_obj.add_relocation(4, "message")  # 偏移 4 处需要 message 地址

    data_obj = ObjectFile("data.o")
    data_obj.data.extend(b"Hello, Linker!\x00")
    data_obj.add_symbol("message", 0, "data")

    # 链接
    linker = TinyLinker()
    linker.add_object(main_obj)
    linker.add_object(data_obj)

    try:
        output = linker.link()
        print(f"  链接成功！输出 {len(output)} 字节")
        linker.symbol_table_dump()
        print(f"\n  output hex: {output.hex()}")
    except ValueError as e:
        print(f"  链接失败: {e}")

if __name__ == "__main__": main()
