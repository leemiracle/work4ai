#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""实验① 数罪并罚计算器——限制加重原则的抽象示例(GB/T 82030 刑法学支)

演示 03 章 L4"三轨结构"的可机械化面:
  吸收原则   : 死刑/无期徒刑吸收其他主刑 → 执行最重者
  限制加重   : 同种自由刑 → max(各刑) <= 执行刑 <= min(总和, 法定上限)
               上限分档(通说结构, 抽象示例): 管制封顶 3, 拘役封顶 1,
               有期徒刑总和不满 35 封顶 20, 满 35 封顶 25
  并科原则   : 附加刑(罚金)简单相加

纪律: 全部案例为抽象数字, 不指涉任何真实案件; 规则按通说结构抽象化,
教学演示用途, 不构成法律意见。纯标准库, assert 自验证, exit 0。
"""

from dataclasses import dataclass

# ---------------------------------------------------------------- 规则层

RANK = {"死刑": 5, "无期徒刑": 4, "有期徒刑": 3, "拘役": 2, "管制": 1}
CAP = {"管制": 3.0, "拘役": 1.0}  # 单位: 年
SINGLE_MAX = {"有期徒刑": 15.0, "拘役": 1.0, "管制": 3.0}  # 单罪宣告刑上限(通说结构)


def execution_range(terms):
    """同种自由刑的执行刑区间(限制加重)。terms: [(刑种, 年数), ...]"""
    kinds = {k for k, _ in terms}
    assert len(kinds) == 1, "抽象简化: 本计算器只处理同种自由刑"
    kind = terms[0][0]
    years = [y for _, y in terms]
    for y in years:
        assert y <= SINGLE_MAX[kind], f"单罪宣告刑超上限: {kind} {y:g} 年"
    lo, total = max(years), sum(years)
    if kind == "有期徒刑":
        hi = 20.0 if total < 35 else 25.0  # 总和分档封顶(通说结构)
    else:
        hi = CAP[kind]
    return lo, min(total, hi)


def combine(terms):
    """数罪并罚三轨总装。terms: [(刑种, 年数), ...] 按罪逐一给定。
    返回 (执行主刑描述, 罚金合计)。混合主刑种时按吸收规则处理重刑种。"""
    mains = sorted([t for t in terms if t[0] in RANK],
                   key=lambda t: RANK[t[0]], reverse=True)
    fines = sum(y for k, y in terms if k == "罚金")
    assert mains, "至少需要一項主刑"
    top_kind = mains[0][0]
    if top_kind in ("死刑", "无期徒刑"):
        return f"执行{top_kind}(吸收其余主刑)", fines  # 吸收原则
    lo, hi = execution_range([m for m in mains])
    return f"决定执行刑 ∈ [{lo:g}, {hi:g}] 年(限制加重)", fines


# ---------------------------------------------------------------- 案例层(全部抽象数字)

CASES = [
    # (说明, 输入, 预期)
    ("单罪不并罚", [("有期徒刑", 10.0)], (10.0, 10.0)),
    ("三罪合计 27 年<35, 封顶 20", [("有期徒刑", 11.0), ("有期徒刑", 9.0), ("有期徒刑", 7.0)], (11.0, 20.0)),
    ("三罪合计恰好 35 年, 封顶 25", [("有期徒刑", 15.0), ("有期徒刑", 12.0), ("有期徒刑", 8.0)], (15.0, 25.0)),
    ("三罪合计 40 年>=35, 封顶 25", [("有期徒刑", 15.0), ("有期徒刑", 12.0), ("有期徒刑", 13.0)], (15.0, 25.0)),
    ("拘役封顶 1 年", [("拘役", 0.5), ("拘役", 0.75)], (0.75, 1.0)),
    ("管制封顶 3 年", [("管制", 2.0), ("管制", 2.0)], (2.0, 3.0)),
    ("总和低于最高单刑不可能", [("有期徒刑", 8.0), ("有期徒刑", 1.0)], (8.0, 9.0)),
]


def main():
    for note, terms, (elo, ehi) in CASES:
        lo, hi = execution_range(terms)
        assert lo == elo and hi == ehi, (note, terms, (lo, hi))
        assert lo <= hi, "区间下界不得超过上界"
        print(f"[OK] {note}: {terms} -> 执行区间 [{lo:g}, {hi:g}]")

    # 吸收原则(抽象示例)
    desc, fines = combine([("死刑", 0.0), ("有期徒刑", 15.0)])
    assert desc.startswith("执行死刑") and fines == 0
    print(f"[OK] 吸收原则: {desc}")
    desc, _ = combine([("无期徒刑", 0.0), ("有期徒刑", 10.0)])
    assert desc.startswith("执行无期徒刑")
    print(f"[OK] 吸收原则: {desc}")

    # 并科原则(罚金附加刑相加, 抽象数字)
    desc, fines = combine([("有期徒刑", 5.0), ("有期徒刑", 4.0), ("罚金", 3.0), ("罚金", 2.0)])
    assert "限制加重" in desc and fines == 5.0
    print(f"[OK] 并科原则: {desc}; 罚金合计 {fines:g} 万(抽象数字)")

    # 限制加重数学不变量: 合法宣告刑组合(单罪<=15)下, 区间非空且上界<=cap
    import itertools
    for combo in itertools.product([3.0, 8.0, 12.0, 15.0], repeat=3):
        lo, hi = execution_range([("有期徒刑", y) for y in combo])
        assert max(combo) == lo and hi <= 25 and lo <= hi, combo
    print("[OK] 不变量: max<=E<=min(sum,cap) 对 4^3 合法组合全部成立")

    # 结构前提自检: 单罪宣告超上限应被拒绝
    try:
        execution_range([("有期徒刑", 25.0)])
        raise SystemExit("应拒绝单罪 25 年输入")
    except AssertionError:
        print("[OK] 前置校验: 单罪宣告刑 25 年超出结构上限 15, 被拒绝")

    # 设计性提醒: 区间内取哪一点是"酌情决定"——不可机械化(04 章裂缝)
    print("\n注意: 区间内的取值由裁量决定, 属 04 章'半自动档'——本计算器止步于区间。")
    print("全部 assert 通过, exit 0")


if __name__ == "__main__":
    main()
