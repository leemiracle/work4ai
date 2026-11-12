"""02_nand_gate_sim.py — NAND 完备性现场验证（对应 03/04 章）

只从一个原语 nand(a,b) = NOT(a AND b) 出发，现场构造：
  NOT → AND → OR → XOR → 半加器 → 全加器 → 4 位行波进位加法器，
最后对全部 256 种输入组合与整数加法对照，逐位验证。

这就是「用最愚笨的零件拼出智能」的最小现场——03 章的美之时刻可执行版。

运行：python 02_nand_gate_sim.py
"""


def nand(a: int, b: int) -> int:
    """唯一的物理原语：与非门（真实芯片中它是最省晶体管的基本门）。"""
    return 1 - (a & b)


# ── 从 NAND 逐级构造 ──────────────────────────────────────────
def not_(a: int) -> int:          # NOT a = NAND(a, a)
    return nand(a, a)


def and_(a: int, b: int) -> int:  # AND = NOT(NAND)
    return not_(nand(a, b))


def or_(a: int, b: int) -> int:   # OR = NAND(NOT a, NOT b)（德摩根）
    return nand(not_(a), not_(b))


def xor(a: int, b: int) -> int:   # XOR = OR(AND(a,NOT b), AND(NOT a,b))
    return or_(and_(a, not_(b)), and_(not_(a), b))


def half_adder(a: int, b: int) -> tuple[int, int]:
    """半加器：返回 (sum, carry)。"""
    return xor(a, b), and_(a, b)


def full_adder(a: int, b: int, cin: int) -> tuple[int, int]:
    """全加器：两位+进位输入 → (sum, carry out)。由两个半加器+OR 组成。"""
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, cin)
    return s2, or_(c1, c2)


def add4(x: list[int], y: list[int]) -> list[int]:
    """4 位行波进位加法器（低位在前）。返回 4 位和（溢出丢弃）。"""
    assert len(x) == 4 and len(y) == 4
    out, cin = [], 0
    for i in range(4):
        s, cin = full_adder(x[i], y[i], cin)
        out.append(s)
    return out


def to_bits(v: int) -> list[int]:
    """整数 → 4 位小端位串。"""
    return [(v >> i) & 1 for i in range(4)]


def main() -> None:
    # 单元验证：真值表级
    assert [not_(0), not_(1)] == [1, 0]
    assert [(a, b, and_(a, b)) for a in (0, 1) for b in (0, 1)] == [
        (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]
    assert [(a, b, xor(a, b)) for a in (0, 1) for b in (0, 1)] == [
        (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    print("单门真值表：NOT/AND/XOR 全部正确")

    # 穷举验证：4 位加法器 vs 整数加法（256 种组合，模 16）
    for xv in range(16):
        for yv in range(16):
            got = sum(bit << i for i, bit in enumerate(add4(to_bits(xv), to_bits(yv))))
            want = (xv + yv) % 16
            assert got == want, f"{xv}+{yv}: 门级={got}, 期望={want}"
    print("4 位行波进位加法器：256/256 组合与整数加法逐位一致")

    # 递进结构统计：从 1 种门到一台会算术的机器
    print(f"\n只用 1 个原语 nand()，构造出：NOT/AND/OR/XOR/半加器/全加器/4位加法器")
    print("[ALL ASSERTS PASSED] NAND 完备性现场成立——一个门，足以开始计算的一切。")


if __name__ == "__main__":
    main()
