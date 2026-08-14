"""
CS 61C Machine Structures — UC Berkeley
================================================
覆盖主题：
- C / 汇编 / RISC-V（Lec 3-6）
- CPU 流水线 + hazard（Lec 13-15）
- Cache 层次结构（direct-mapped / set-associative）（Lec 9-11）
- IEEE 754 浮点数（Lec 2）
- 内存管理 / 虚拟地址翻译（Lec 16-18）

核心教材/参考：
- Patterson & Hennessy "Computer Organization and Design RISC-V Edition" 2nd ed (Morgan Kaufmann 2020)
- Hennessy & Patterson "Computer Architecture: A Quantitative Approach" 6th ed (Morgan Kaufmann 2017)
- IEEE Std 754-2019 "IEEE Standard for Floating-Point Arithmetic"

本文件实现：
- RISC-V 子集模拟器（ADD/SUB/LW/SW/BEQ/JAL 等）
- Direct-mapped cache 模拟器（带 miss rate 统计）
- 5-stage pipeline（IF/ID/EX/MEM/WB）含 data hazard + forwarding
- IEEE 754 编解码

运行：
    python arch.py
"""
from __future__ import annotations
import struct


# ============================================================
# 1. RISC-V 子集模拟器
# ============================================================

class RISCVSim:
    """
    单周期 RISC-V 模拟器（子集）。
    支持：addi add sub lw sw beq jal
    寄存器 x0..x31（x0 恒 0），内存按字寻址。
    """
    def __init__(self):
        self.reg = [0] * 32
        self.pc = 0
        self.mem = {}  # word-addressed
        self.instructions_executed = 0

    def _set_reg(self, idx, val):
        if idx != 0:  # x0 hardwired to 0
            self.reg[idx] = val & 0xFFFFFFFF

    def _get_reg(self, idx):
        return self.reg[idx]

    def load_program(self, program: list[tuple]):
        """program: list of (opcode, rd, rs1, rs2, imm)"""
        self.program = program

    def run(self, max_steps: int = 10000):
        while 0 <= self.pc < len(self.program) and self.instructions_executed < max_steps:
            instr = self.program[self.pc]
            self.pc += 1
            self._execute(instr)
            self.instructions_executed += 1

    def _execute(self, instr):
        op = instr[0]
        if op == "addi":
            _, rd, rs1, imm = instr
            self._set_reg(rd, self._get_reg(rs1) + imm)
        elif op == "add":
            _, rd, rs1, rs2 = instr
            self._set_reg(rd, self._get_reg(rs1) + self._get_reg(rs2))
        elif op == "sub":
            _, rd, rs1, rs2 = instr
            self._set_reg(rd, self._get_reg(rs1) - self._get_reg(rs2))
        elif op == "lw":
            _, rd, rs1, imm = instr
            addr = (self._get_reg(rs1) + imm) // 4
            self._set_reg(rd, self.mem.get(addr, 0))
        elif op == "sw":
            _, rs2, rs1, imm = instr
            addr = (self._get_reg(rs1) + imm) // 4
            self.mem[addr] = self._get_reg(rs2)
        elif op == "beq":
            _, rs1, rs2, offset = instr
            if self._get_reg(rs1) == self._get_reg(rs2):
                self.pc += offset  # offset in instructions
        elif op == "jal":
            _, rd, offset = instr
            self._set_reg(rd, self.pc)
            self.pc += offset
        else:
            raise ValueError(f"Unknown opcode: {op}")


# ============================================================
# 2. Direct-Mapped Cache（Patterson §5.4）
# ============================================================

class DirectMappedCache:
    """
    Address = [tag | index | block offset]
    Direct-mapped: 每个地址映射到唯一一个 cache line。
    Miss 类型（3C model, Hennessy §B.1）：
    - Compulsory miss（第一次访问）
    - Capacity miss（cache 满了）
    - Conflict miss（同一 index 被 eviction）
    """
    def __init__(self, num_lines: int = 16, block_size: int = 4):
        self.num_lines = num_lines
        self.block_size = block_size
        self.offset_bits = block_size.bit_length() - 1
        self.index_bits = num_lines.bit_length() - 1
        self.tags = [None] * num_lines
        self.valid = [False] * num_lines
        self.hits = 0
        self.misses = 0
        self.miss_compulsory = 0
        self.miss_conflict = 0

    def access(self, byte_addr: int) -> bool:
        """返回 True if hit"""
        block_addr = byte_addr >> self.offset_bits
        index = block_addr % self.num_lines
        tag = block_addr >> self.index_bits

        if self.valid[index] and self.tags[index] == tag:
            self.hits += 1
            return True

        # Miss
        self.misses += 1
        if not self.valid[index]:
            self.miss_compulsory += 1
        else:
            self.miss_conflict += 1
        self.tags[index] = tag
        self.valid[index] = True
        return False

    def stats(self):
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / max(total, 1),
            "miss_rate": self.misses / max(total, 1),
            "compulsory": self.miss_compulsory,
            "conflict": self.miss_conflict,
        }


# ============================================================
# 3. 5-Stage Pipeline with Forwarding（Patterson §4.7-4.10）
# ============================================================

class Pipeline5Stage:
    """
    IF → ID → EX → MEM → WB
    Data hazard: 上一条指令的 EX 结果被下一条 ID 需要（RAW）。
    Forwarding：EX/MEM → EX, MEM/WB → EX 避免 1-2 stall。
    （load-use hazard 需 1 bubble，本简化模型未实现。）
    """
    def __init__(self):
        self.cycles = 0
        self.stalls = 0

    def simulate(self, instructions: list[dict], forwarding: bool = True) -> dict:
        """
        instructions: [{"op":..., "rd":int, "rs1":int, "rs2":int}, ...]
        返回总周期数 + CPI。
        """
        n = len(instructions)
        # 记录每条指令的 EX 完成周期（rd 可用周期）
        rd_ready = {}  # reg → cycle when value available
        stall_cycles = 0

        for i, instr in enumerate(instructions):
            # 完美 pipeline: 每条指令 +1 cycle（无 hazard）
            issue_cycle = i + 1 + stall_cycles
            ex_cycle = issue_cycle + 1  # EX stage

            # Check RAW hazards
            for src in [instr.get("rs1", 0), instr.get("rs2", 0)]:
                if src == 0:
                    continue
                if src in rd_ready:
                    if forwarding:
                        # Forward from EX: available at ex_cycle_prev
                        # 只需等待到前一条的 EX 完成
                        if rd_ready[src] > ex_cycle:
                            needed = rd_ready[src]
                            extra = needed - ex_cycle
                            stall_cycles += extra
                            ex_cycle += extra
                    else:
                        # No forwarding: must wait until WB completes
                        if rd_ready[src] + 1 > ex_cycle:  # +1 for WB
                            extra = rd_ready[src] + 1 - ex_cycle
                            stall_cycles += extra
                            ex_cycle += extra

            # Record when rd is ready
            if instr.get("rd", 0) != 0:
                if forwarding:
                    rd_ready[instr["rd"]] = ex_cycle  # ready at end of EX
                else:
                    rd_ready[instr["rd"]] = ex_cycle + 2  # end of WB

        self.stalls = stall_cycles
        total_cycles = n + 4 + stall_cycles  # 5 stages = n + 4 fill, + stalls
        self.cycles = total_cycles
        cpi = total_cycles / max(n, 1)
        return {
            "total_cycles": total_cycles,
            "stalls": stall_cycles,
            "CPI": cpi,
            "forwarding": forwarding,
        }


# ============================================================
# 4. IEEE 754（Patterson §3.5）
# ============================================================

def ieee754_decode(bits: int) -> dict:
    """解码 32-bit IEEE 754 single"""
    sign = (bits >> 31) & 1
    exponent = (bits >> 23) & 0xFF
    mantissa = bits & 0x7FFFFF
    value = _decode_components(sign, exponent, mantissa)
    return {"sign": sign, "exponent": exponent, "mantissa": mantissa, "value": value}


def _decode_components(sign, exponent, mantissa):
    if exponent == 0:
        if mantissa == 0:
            return -0.0 if sign else 0.0
        # Denormalized: (-1)^s * 0.mantissa * 2^(-126)
        return (-1) ** sign * (mantissa / 2 ** 23) * 2 ** (-126)
    if exponent == 255:
        if mantissa == 0:
            return float("-inf") if sign else float("inf")
        return float("nan")
    # Normalized: (-1)^s * 1.mantissa * 2^(e-127)
    frac = 1 + mantissa / 2 ** 23
    return (-1) ** sign * frac * 2 ** (exponent - 127)


def float_to_bits(x: float) -> int:
    """float → 32-bit IEEE 754"""
    return struct.unpack("I", struct.pack("f", x))[0]


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 61C Machine Structures Demo")
    print("=" * 60)

    # 1. RISC-V: 计算 1+2+...+5 = 15
    print("\n📋 1. RISC-V 模拟器（求和循环）")
    sim = RISCVSim()
    # 计算 sum(1..5) = 15
    # x1 = 0 (sum), x2 = 1 (i), x3 = 6 (n+1, 必须含 5 才累加到 5)
    # 注：beq 在 x2 自增后判断，x3=5 会在 x2==5 时提前退出 → 只累加到 4
    program = [
        ("addi", 1, 0, 0),    # x1 = 0
        ("addi", 2, 0, 1),    # x2 = 1
        ("addi", 3, 0, 6),    # x3 = 6 (终止条件 n+1，确保 5 被累加)
        # loop:
        ("add", 1, 1, 2),     # x1 += x2       # idx 3
        ("addi", 2, 2, 1),    # x2++           # idx 4
        ("beq", 2, 3, 2),     # if x2==x3 skip # idx 5 (offset +2 → pc=8 退出)
        ("jal", 0, -4),       # idx 6: pc 先变 7, 7+(-4)=3 → 跳回 idx 3 的 add
        # end:
        ("addi", 0, 0, 0),    # nop (halt point)  # idx 7
    ]
    sim.load_program(program)
    sim.run()
    print(f"   sum(1..5) = x1 = {sim.reg[1]} (期望 15)")
    print(f"   instructions_executed = {sim.instructions_executed}")

    # 2. Cache
    print("\n📋 2. Direct-Mapped Cache 模拟")
    cache = DirectMappedCache(num_lines=4, block_size=4)
    # 顺序访问 0, 4, 8, 12, 0, 4 → 冲突 miss
    addrs = [0, 4, 8, 12, 0, 4, 16, 0]
    for a in addrs:
        hit = cache.access(a)
        print(f"   access {a:3d}: {'HIT ' if hit else 'MISS'}")
    s = cache.stats()
    print(f"   hit_rate = {s['hit_rate']:.1%}, compulsory = {s['compulsory']}, conflict = {s['conflict']}")

    # 3. Pipeline with/without forwarding
    print("\n📋 3. 5-Stage Pipeline（forwarding vs 无 forwarding）")
    # 经典 RAW: sub x1,x2,x3 → add x4,x1,x5
    progs = {
        "无依赖": [{"op": "add", "rd": 1, "rs1": 2, "rs2": 3},
                  {"op": "sub", "rd": 6, "rs1": 7, "rs2": 8},
                  {"op": "add", "rd": 9, "rs1": 10, "rs2": 11}],
        "3条RAW链": [{"op": "add", "rd": 1, "rs1": 2, "rs2": 3},
                    {"op": "sub", "rd": 4, "rs1": 1, "rs2": 5},
                    {"op": "add", "rd": 6, "rs1": 4, "rs2": 7},
                    {"op": "sub", "rd": 8, "rs1": 6, "rs2": 9}],
    }
    for name, prog in progs.items():
        pipe_fwd = Pipeline5Stage()
        r_fwd = pipe_fwd.simulate(prog, forwarding=True)
        pipe_nofwd = Pipeline5Stage()
        r_nofwd = pipe_nofwd.simulate(prog, forwarding=False)
        print(f"   [{name}] {len(prog)} 条指令:")
        print(f"     forwarding:    {r_fwd['total_cycles']} cycles, CPI={r_fwd['CPI']:.2f}")
        print(f"     no forwarding: {r_nofwd['total_cycles']} cycles, CPI={r_nofwd['CPI']:.2f}")

    # 4. IEEE 754
    print("\n📋 4. IEEE 754 浮点数")
    for val in [1.0, 0.1, -0.0, 0.5, 2.0]:
        bits = float_to_bits(val)
        d = ieee754_decode(bits)
        print(f"   {val:>6} → 0x{bits:08X}  sign={d['sign']} exp={d['exponent']:3d} frac={d['mantissa']:08X}")

    # 浮点精度陷阱
    print("\n   浮点精度陷阱:")
    x = 0.1 + 0.2
    print(f"   0.1 + 0.2 = {x}  (≠ 0.3!)")
    print(f"   0.1 + 0.2 == 0.3 → {x == 0.3}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   4 个 cache line 的 direct-mapped cache，访问 [0,4,8,12,0,4,16,0]：")
    s2 = cache.stats()
    print(f"   每个 4 字节映射到唯一 line（block_size=4 → 0→line0, 4→line1...）")
    print(f"   访问 [0,4,8,12,0,4] 时 0/4 仍是 HIT（4 个 line 刚好够，无冲突）。")
    print(f"   但加入 16 后冲突 miss（16 与 0 同 index(0) 不同 tag），再次访问 0 时变成 conflict miss。")
    print("   → 这就是 direct-mapped 的冲突 miss：即使 cache 没满也会 thrash。")
    print("   解决：set-associative（每个 index 2+ ways）让冲突 miss 大幅下降。")
    print()
    print("   Pipeline：3 条 RAW 链，forwarding 让 CPI 从 ~3.50 → ~2.00（实测匹配）。")
    print("   现代 CPU 有 10-20 级流水，forwarding/bypass 是必备，否则 CPI 爆炸。")


if __name__ == "__main__":
    demo()
