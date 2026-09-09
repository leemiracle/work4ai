"""
pytest 套件 — 验证 rv32i_sim.py + assembler.py

运行：
    cd Capstone/cpu_simulator
    pytest tests/ -v

设计原则（现代方式）：
- 每个 test 只验证一件事，名字表达意图
- 用 fixture 共享 CPU 构造逻辑
- 用 parametrize 批量测试同质用例
- 区分 unit test（单条指令 / 单个 ALU 操作）和 integration test（完整程序）
"""
import os
import sys
import glob
import re
import pytest

# 让 tests/ 能 import 同级目录的 rv32i_sim 和 assembler
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rv32i_sim import (CPU, decode, _alu, _to_signed, _branch_taken,
                       MASK32, build_sum_program, InstKind)
from assembler import assemble, assemble_file, AssemblerError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fresh_cpu_factory():
    """返回一个构造 CPU 的工厂；每个 test 用全新 CPU。"""
    def _make(src: str, **kwargs):
        return CPU(assemble(src), **kwargs)
    return _make


def run_and_read(src: str, reg: int, **kwargs) -> tuple:
    """跑一段汇编，返回 (寄存器值, 统计)。"""
    cpu = CPU(assemble(src), **kwargs)
    stats = cpu.run()
    return cpu.rf.read(reg), stats


# ============================================================================
# 1. Decoder 单测：每条 RV32I 指令的 decode 是否正确
# ============================================================================

class TestDecode:
    """逐条验证 RV32I 解码（助记符 + 字段 + flags）。"""

    def test_add(self):
        # add x5, x6, x7  →  funct7=0, rs2=7, rs1=6, funct3=0, rd=5, opcode=0x33
        inst = decode(0x007302B3, addr=0)
        assert inst.op == "add"
        assert inst.kind == InstKind.OP
        assert (inst.rd, inst.rs1, inst.rs2) == (5, 6, 7)
        assert inst.reads_rs1 and inst.reads_rs2 and inst.writes_rd

    def test_sub(self):
        # sub x5, x6, x7  →  用 assembler 生成（避免手算 hex 出错）
        prog = assemble("sub x5, x6, x7")
        inst = decode(prog[0], addr=0)
        assert inst.op == "sub"
        assert (inst.rd, inst.rs1, inst.rs2) == (5, 6, 7)

    @pytest.mark.parametrize("op,funct3,funct7", [
        ("sll", 0x1, 0x00), ("slt", 0x2, 0x00), ("sltu", 0x3, 0x00),
        ("xor", 0x4, 0x00), ("srl", 0x5, 0x00), ("sra", 0x5, 0x20),
        ("or",  0x6, 0x00), ("and", 0x7, 0x00),
    ])
    def test_r_type_all(self, op, funct3, funct7):
        # 编码: funct7 | rs2=7 | rs1=6 | funct3 | rd=5 | 0x33
        raw = (funct7 << 25) | (7 << 20) | (6 << 15) | (funct3 << 12) | (5 << 7) | 0x33
        inst = decode(raw, addr=0)
        assert inst.op == op

    def test_addi(self):
        # addi x5, x6, 100  →  imm=100, rs1=6, funct3=0, rd=5, opcode=0x13
        raw = (100 << 20) | (6 << 15) | (0 << 12) | (5 << 7) | 0x13
        inst = decode(raw, addr=0)
        assert inst.op == "addi"
        assert inst.imm == 100

    def test_addi_negative_imm(self):
        # addi x5, x6, -1  →  imm 字段 = 0xFFF（12-bit -1）
        raw = (0xFFF << 20) | (6 << 15) | (0 << 12) | (5 << 7) | 0x13
        inst = decode(raw, addr=0)
        assert inst.imm == -1   # 符号扩展

    def test_lui(self):
        # lui x5, 0x12345  →  imm 字段 = 0x12345
        raw = (0x12345 << 12) | (5 << 7) | 0x37
        inst = decode(raw, addr=0)
        assert inst.op == "lui"
        assert inst.imm == 0x12345000   # 解码后是 32-bit 寄存器结果值

    def test_auipc(self):
        raw = (0x1 << 12) | (5 << 7) | 0x17
        inst = decode(raw, addr=0x100)
        assert inst.op == "auipc"
        assert inst.imm == 0x1000

    def test_jal(self):
        # jal x1, 0x100  (pc=0)
        # imm = 0x100，J-type 编码:
        # imm[20]=0, imm[10:1]=0x80, imm[11]=0, imm[19:12]=0
        imm = 0x100
        b20 = (imm >> 20) & 1
        b10_1 = (imm >> 1) & 0x3FF
        b11 = (imm >> 11) & 1
        b19_12 = (imm >> 12) & 0xFF
        raw = (b20 << 31) | (b19_12 << 12) | (b11 << 20) | (b10_1 << 21) | (1 << 7) | 0x6F
        inst = decode(raw, addr=0)
        assert inst.op == "jal"
        assert inst.imm == 0x100
        assert inst.is_jal and inst.writes_rd

    def test_load_variants(self):
        for op, funct3 in [("lb", 0), ("lh", 1), ("lw", 2), ("lbu", 4), ("lhu", 5)]:
            raw = (8 << 20) | (6 << 15) | (funct3 << 12) | (5 << 7) | 0x03
            inst = decode(raw, addr=0)
            assert inst.op == op
            assert inst.is_load

    def test_store_variants(self):
        for op, funct3 in [("sb", 0), ("sh", 1), ("sw", 2)]:
            # imm=0, rs2=7, rs1=6, funct3, opcode=0x23
            raw = (7 << 20) | (6 << 15) | (funct3 << 12) | 0x23
            inst = decode(raw, addr=0)
            assert inst.op == op
            assert inst.is_store

    @pytest.mark.parametrize("op,funct3", [
        ("beq", 0), ("bne", 1), ("blt", 4), ("bge", 5), ("bltu", 6), ("bgeu", 7),
    ])
    def test_branch_variants(self, op, funct3):
        raw = (funct3 << 12) | 0x63
        inst = decode(raw, addr=0)
        assert inst.op == op
        assert inst.is_branch

    def test_ecall_ebreak(self):
        assert decode(0x00000073, 0).op == "ecall"
        assert decode(0x00100073, 0).op == "ebreak"

    def test_illegal_opcode(self):
        # 0x7F 不是合法 opcode
        inst = decode(0x0000007F, 0)
        assert inst.op == "illegal"


# ============================================================================
# 2. ALU 单测
# ============================================================================

class TestALU:

    @pytest.mark.parametrize("op, a, b, expected", [
        ("add", 5, 3, 8), ("sub", 5, 3, 2), ("and", 0xFF, 0x0F, 0x0F),
        ("or", 0xF0, 0x0F, 0xFF), ("xor", 0xFF, 0x0F, 0xF0),
        ("sll", 1, 4, 16), ("srl", 0x100, 4, 0x10),
        ("slt", 3, 5, 1), ("slt", 5, 3, 0),
        ("sltu", 0xFFFFFFFF, 1, 0),   # unsigned: 大数 > 1
    ])
    def test_alu_r_type(self, op, a, b, expected):
        assert _alu(op, a, b, 0, 0) == expected

    @pytest.mark.parametrize("op, a, imm, expected", [
        ("addi", 5, 3, 8), ("andi", 0xFF, 0x0F, 0x0F),
        ("ori", 0xF0, 0x0F, 0xFF), ("xori", 0xFF, 0x0F, 0xF0),
        ("slli", 1, 4, 16), ("srli", 0x100, 4, 0x10),
    ])
    def test_alu_i_type(self, op, a, imm, expected):
        assert _alu(op, a, 0, imm, 0) == expected

    def test_sra_arithmetic_shift(self):
        # 0x80000000 算术右移 4 位 → 0xF8000000
        assert _alu("sra", 0x80000000, 4, 0, 0) == 0xF8000000
        # 0x40000000 算术右移 4 位 → 0x04000000（正数，与 srl 相同）
        assert _alu("sra", 0x40000000, 4, 0, 0) == 0x04000000

    def test_slti_signed(self):
        assert _alu("slti", -1, 0, 1, 0) == 1   # -1 < 1
        assert _alu("slti", 1, 0, -1, 0) == 0   # 1 !< -1

    def test_lui(self):
        assert _alu("lui", 0, 0, 0x12345000, 0) == 0x12345000

    def test_auipc(self):
        assert _alu("auipc", 0, 0, 0x1000, 0x100) == 0x1100

    def test_to_signed(self):
        assert _to_signed(0xFFFFFFFF) == -1
        assert _to_signed(0x7FFFFFFF) == 0x7FFFFFFF
        assert _to_signed(0x80000000) == -0x80000000


# ============================================================================
# 3. 分支判定单测
# ============================================================================

class TestBranch:
    def test_beq(self):
        assert _branch_taken("beq", 5, 5) is True
        assert _branch_taken("beq", 5, 6) is False

    def test_bne(self):
        assert _branch_taken("bne", 5, 6) is True
        assert _branch_taken("bne", 5, 5) is False

    def test_blt_signed(self):
        # 0xFFFFFFFF = -1 signed，比 0 小
        assert _branch_taken("blt", 0xFFFFFFFF, 0) is True
        assert _branch_taken("blt", 0, 0xFFFFFFFF) is False

    def test_bltu_unsigned(self):
        # 0xFFFFFFFF 大数 unsigned，比 0 大
        assert _branch_taken("bltu", 0, 0xFFFFFFFF) is True
        assert _branch_taken("bltu", 0xFFFFFFFF, 0) is False


# ============================================================================
# 4. Assembler 单测
# ============================================================================

class TestAssembler:

    def test_roundtrip_simple(self):
        prog = assemble("addi x1, x0, 42")
        inst = decode(prog[0], 0)
        assert inst.op == "addi"
        assert inst.imm == 42

    def test_label_resolution(self):
        prog = assemble("""
            beq x0, x0, target
            addi x1, x0, 99    # 应被跳过
        target:
            addi x2, x0, 7
        """)
        # beq 跳到 target=8，跳过中间 addi
        cpu = CPU(prog)
        cpu.run()
        assert cpu.rf.read(1) == 0    # x1 没写
        assert cpu.rf.read(2) == 7    # x2 写了

    def test_pseudo_nop_mv(self):
        prog_nop = assemble("nop")
        prog_addi = assemble("addi x0, x0, 0")
        assert prog_nop[0] == prog_addi[0]

        prog_mv = assemble("mv x1, x2")
        prog_addi = assemble("addi x1, x2, 0")
        assert prog_mv[0] == prog_addi[0]

    def test_pseudo_li_small(self):
        # 小立即数: li x1, 42  →  addi x1, x0, 42
        prog = assemble("li x5, 42")
        inst = decode(prog[0], 0)
        assert inst.op == "addi"
        assert len(prog) == 1

    def test_pseudo_li_large(self):
        # 大立即数: li x1, 0x12345678  →  lui + addi
        prog = assemble("li x5, 0x12345678")
        assert len(prog) == 2
        cpu = CPU(prog)
        cpu.run()
        assert cpu.rf.read(5) == 0x12345678

    def test_pseudo_li_negative(self):
        prog = assemble("li x5, -100")
        cpu = CPU(prog)
        cpu.run()
        assert _to_signed(cpu.rf.read(5)) == -100

    def test_pseudo_branch_reversal(self):
        # ble rs, rt, label  ⟷  bge rt, rs, label
        p1 = assemble("ble x1, x2, end\nend:")
        p2 = assemble("bge x2, x1, end\nend:")
        assert p1[0] == p2[0]

    def test_register_aliases(self):
        # 全部 ABI 别名应该工作
        for name, idx in [("zero", 0), ("ra", 1), ("sp", 2), ("gp", 3),
                          ("tp", 4), ("t0", 5), ("a0", 10), ("s0", 8),
                          ("fp", 8), ("t6", 31)]:
            prog = assemble(f"addi {name}, x0, 0")
            inst = decode(prog[0], 0)
            assert inst.rd == idx

    def test_memory_operand_parsing(self):
        # lw a0, 8(sp)  →  imm=8, rs1=2
        prog = assemble("lw a0, 8(sp)")
        inst = decode(prog[0], 0)
        assert inst.op == "lw"
        assert inst.rs1 == 2 and inst.imm == 8

    def test_directive_word(self):
        prog = assemble(".word 0x12345678, 0xAABBCCDD")
        assert prog == [0x12345678, 0xAABBCCDD]

    def test_negative_branch_offset(self):
        # 关键 case: 原骨架的 bne 编码 bug 就是这个
        # 让 bne 前有一条指令（占 4 字节），bne 在 pc=4，回跳到 loop（pc=0），offset=-4
        prog = assemble("""
        loop:
            addi x1, x1, 1
            bne x2, x3, loop
        """)
        # prog[1] 是 bne，地址 = 4；loop=0，offset = -4
        inst = decode(prog[1], 4)
        assert inst.op == "bne"
        assert inst.imm == -4   # 回跳 4 字节

    def test_assembler_error_unknown_mnemonic(self):
        with pytest.raises(AssemblerError):
            assemble("frobnicate x1, x2")


# ============================================================================
# 5. Forwarding / Stall / Flush 单测
# ============================================================================

class TestPipeline:

    def test_forwarding_basic(self):
        """紧邻的依赖指令应该没有气泡（forwarding 生效）。"""
        src = """
            addi x1, x0, 5
            addi x2, x1, 3     # 依赖 x1，应该被 forward
            ecall
        """
        val, stats = run_and_read(src, 2)
        assert val == 8
        # 没有分支，没有 load，所以 0 stall 0 flush

    def test_forward_vs_no_forward(self):
        """关掉 forwarding 后，紧邻的依赖链会读到过时的 RegFile 值，结果错误。
        这正好说明 forwarding 是流水线正确性 / 性能的必需机制。"""
        src = """
            addi x1, x0, 5
            addi x2, x1, 3     # 依赖 x1（上条结果）
            ecall
        """
        # 开 forwarding：x1 = 5 已在 EX/MEM 槽，正确转发 → x2 = 8
        val_fwd, _ = run_and_read(src, 2, forward_enabled=True)
        assert val_fwd == 8
        # 关 forwarding：x2 在 ID 时读 x1，但 x1 还没写回（在 EX/MEM 槽）
        # → 读到 RegFile 的旧值 0 → x2 = 0 + 3 = 3（错误结果，证明 forwarding 必需）
        val_nofwd, _ = run_and_read(src, 2, forward_enabled=False)
        assert val_nofwd == 3

    def test_load_use_stall(self):
        """load 后立即用必须 1-cycle stall。"""
        src = """
            sw  x1, 0(x0)      # 先存个值
            lw  x2, 0(x0)      # 加载
            add x3, x2, x2     # 立即用 load 结果 → stall
            ecall
        """
        # 先准备数据
        prog = assemble("addi x1, x0, 42\nsw x1, 0(x0)\nlw x2, 0(x0)\nadd x3, x2, x2\necall")
        cpu = CPU(prog)
        stats = cpu.run()
        assert cpu.rf.read(3) == 84   # 42 + 42
        assert stats.stalls >= 1      # 必须有 load-use stall

    def test_load_use_no_stall_when_separated(self):
        """load 和用它之间隔一条独立指令 → 无 stall。"""
        src = """
            lw  x2, 0(x0)
            addi x9, x0, 1     # 独立指令，填充 load delay slot
            add x3, x2, x2     # 此时 load 已到 MEM/WB，可 forward
            ecall
        """
        cpu = CPU(assemble(src))
        stats = cpu.run()
        assert stats.stalls == 0

    def test_branch_misprediction_flush(self):
        """第一次 bne 必然 mispredict（预测器初始 WN → predict not taken）。"""
        src = """
        loop:
            addi x1, x1, 1
            bne x1, x0, loop    # 第一次必然 taken，但预测为 not taken → flush
            ecall
        """
        cpu = CPU(assemble(src))
        stats = cpu.run(max_cycles=200)
        # 至少 1 次 misprediction
        assert stats.branch_mispred >= 1
        assert stats.flushes >= 2   # 每次 misprediction flush 2 条

    def test_branch_predictor_learns(self):
        """同一分支多次执行后，2-bit 预测器应该学到 taken，准确率提升。"""
        src = """
            addi x2, x0, 20
        loop:
            addi x1, x1, 1
            bne x1, x2, loop
            ecall
        """
        cpu = CPU(assemble(src))
        stats = cpu.run(max_cycles=500)
        # 20 次分支，第一次 mispredict + 最后一次 exit mispredict ≈ 2 次
        # 即使最坏，准确率也应 > 80%
        assert stats.branch_accuracy > 0.8


# ============================================================================
# 6. 集成测试：跑 test_progs/ 下所有 .s 文件
# ============================================================================

class TestPrograms:
    """自动发现 test_progs/*.s 并用 @expect 注解验证。"""

    @pytest.fixture(scope="class")
    def test_progs(self):
        progs_dir = os.path.join(os.path.dirname(__file__), "..", "test_progs")
        cases = []
        for path in sorted(glob.glob(os.path.join(progs_dir, "*.s"))):
            with open(path) as f:
                src = f.read()
            m = re.search(r"@expect:\s*x?(\d+)\s*=\s*(-?\d+)", src)
            if m:
                cases.append((os.path.basename(path),
                              int(m.group(1)), int(m.group(2))))
        return cases

    def test_progs_have_expect_annotations(self, test_progs):
        """所有 test_progs/*.s 都应该有 @expect 注解。"""
        assert len(test_progs) >= 5, "至少要有 5 个测试程序"

    @pytest.mark.parametrize("name,res_reg,expected", [
        # 静态写一份，让 pytest 在收集时就能看到用例名（动态从 fixture 也能，但更繁琐）
        ("sum.s", 10, 55),
        ("fib.s", 11, 55),
        ("branch_zoo.s", 10, 6),
        ("shifts_and_logical.s", 5, 64),
        ("memory_ops.s", 10, 0x12345678),
        ("function_call.s", 10, 42),
        ("bubble_sort.s", 10, 1),
    ])
    def test_program_result(self, name, res_reg, expected):
        progs_dir = os.path.join(os.path.dirname(__file__), "..", "test_progs")
        path = os.path.join(progs_dir, name)
        cpu = CPU(assemble_file(path))
        cpu.run(max_cycles=200000)
        actual = cpu.rf.read(res_reg)
        assert actual == expected, \
            f"{name}: x{res_reg} = {actual} (0x{actual:x}), expected {expected} (0x{expected:x})"


# ============================================================================
# 7. 内置 sum 程序（保护性回归测试）
# ============================================================================

def test_builtin_sum_program():
    """build_sum_program() 是模拟器的 canary，任何回归都该被这个测试抓到。"""
    prog, res_reg, expected = build_sum_program()
    cpu = CPU(prog)
    stats = cpu.run()
    assert cpu.rf.read(res_reg) == expected
    assert stats.inst_retired > 30        # 10 次循环 + setup
    assert stats.branch_count == 10
