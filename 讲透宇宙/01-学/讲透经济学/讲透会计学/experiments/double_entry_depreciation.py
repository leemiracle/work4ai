#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复式记账的不变量与折旧三法（对应 00 章 §2 / 03 章 §2 / 04 章走廊①）。

Part A：一家小企业 7 笔真实业务走完借贷分录，逐步断言：
  - 每笔分录 借方合计 == 贷方合计（复式记账的局部守恒）；
  - 每一步 资产 == 负债 + 所有者权益 + 累计净利（会计恒等式的全局守恒）；
  - 期末试算平衡表：全部账户借方余额合计 == 贷方余额合计。
Part B：同一设备 120 万、残值 12 万、5 年，三种折旧法：
  - 直线法 / 双倍余额递减法(末两年改直线) / 年数总和法；
  - 断言三法总折旧恒等于 108 万、期末账面恒等于残值 12 万（殊途同归）；
  - 断言加速折旧前两年计提更多（税盾前置），并按 8% 折现率量化
    折旧税盾现值差异（25% 所得税率）。
"""
import numpy as np

# ---------- Part A：复式记账 = 逐步保持的不变量 ----------
# 科目分类：A=资产 L=负债 E=所有者权益 R=收入 X=费用（借贷方向由分类决定）
CLS = {
    "银行存款": "A", "应收账款": "A", "原材料": "A", "固定资产": "A", "累计折旧": "A-",
    "应付账款": "L", "短期借款": "L", "应交税费": "L",
    "实收资本": "E", "未分配利润": "E",
    "主营业务收入": "R", "主营业务成本": "X", "管理费用": "X", "销售费用": "X",
}
# 期末结转前的净利挂本年利润（动态等式 A = L + E + R - X 的 R/X 即其构成）
balances = {k: 0.0 for k in CLS}          # 正=借方余额，负=贷方余额
entries = [  # (摘要, [(科目, 借/贷, 金额), ...])
    ("股东投入资本", [("银行存款", "借", 1000.0), ("实收资本", "贷", 1000.0)]),
    ("赊购设备",     [("固定资产", "借", 120.0), ("应付账款", "贷", 120.0)]),
    ("现购原材料",   [("原材料", "借", 50.0), ("银行存款", "贷", 50.0)]),
    ("赊销产品",     [("应收账款", "借", 80.0), ("主营业务收入", "贷", 80.0)]),
    ("结转销售成本", [("主营业务成本", "借", 40.0), ("原材料", "贷", 40.0)]),
    ("收回货款",     [("银行存款", "借", 60.0), ("应收账款", "贷", 60.0)]),
    ("计提首年折旧(直线法)", [("管理费用", "借", 21.6), ("累计折旧", "贷", 21.6)]),
]

def net_worth(bal):
    """A = L + E + NI 全局恒等式两边（万元）。"""
    A = sum(bal[k] for k in bal if CLS[k] == "A") + bal["累计折旧"]   # 累计折旧=备抵资产(贷余冲减)
    L = -sum(bal[k] for k in bal if CLS[k] == "L")
    E = -sum(bal[k] for k in bal if CLS[k] == "E")
    NI = -sum(bal[k] for k in bal if CLS[k] == "R") - sum(bal[k] for k in bal if CLS[k] == "X")
    return A, L + E + NI

print("== Part A：七笔业务的局部守恒与全局守恒 ==")
for i, (memo, legs) in enumerate(entries, 1):
    dr = sum(a for _, s, a in legs if s == "借")
    cr = sum(a for _, s, a in legs if s == "贷")
    assert abs(dr - cr) < 1e-9, f"第{i}笔 {memo} 借贷不平!"
    for acc, side, amt in legs:
        balances[acc] += amt if side == "借" else -amt
    lhs, rhs = net_worth(balances)
    assert abs(lhs - rhs) < 1e-9, f"第{i}笔后恒等式破缺: {lhs} != {rhs}"
    print(f"  [{i}] {memo}: 借=贷={dr:7.1f} 万 | A={lhs:7.1f} = L+E+NI={rhs:7.1f}")

td = sum(v for v in balances.values() if v > 0)          # 试算平衡表
tc = -sum(v for v in balances.values() if v < 0)
print(f"  试算平衡表: 借方余额合计 {td:.1f} == 贷方余额合计 {tc:.1f} 万")
assert abs(td - tc) < 1e-9
rev = -balances["主营业务收入"]
exp = balances["主营业务成本"] + balances["管理费用"]
print(f"  净利 = 收入 {rev:.1f} - 费用 {exp:.1f} = {rev - exp:.1f} 万（第7笔折旧是当期费用却不动现金）")

# ---------- Part B：折旧三法 ----------
cost, salvage, life, rate, n = 120.0, 12.0, 5, 0.08, 5
sl  = np.full(n, (cost - salvage) / life)                       # 直线法
ddb = cost * (2 / life) * (1 - 2 / life) ** np.arange(n)        # 双倍余额递减
ddb[3:] = (cost - ddb[:3].sum() - salvage) / 2                  # 末两年改直线
syd = (cost - salvage) * (life - np.arange(n)) / (life * (life + 1) / 2)  # 年数总和法

print("\n== Part B：折旧三法（120 万，残值 12 万，5 年）==")
print("  年份  直线法   双倍余额递减  年数总和法")
for y in range(n):
    print(f"  {y+1}    {sl[y]:6.2f}    {ddb[y]:8.2f}    {syd[y]:7.2f}")

for name, sch in [("直线法", sl), ("双倍余额递减", ddb), ("年数总和法", syd)]:
    assert abs(sch.sum() - (cost - salvage)) < 1e-9, f"{name} 总折旧 != 可折旧额"
    assert abs((cost - sch.sum()) - salvage) < 1e-9, f"{name} 期末账面 != 残值"
    print(f"  [{name}] 总折旧 {sch.sum():.2f} 万，期末账面 {cost - sch.sum():.2f} 万 == 残值")
assert ddb[0] > sl[0] and ddb[:2].sum() > sl[:2].sum(), "加速折旧法前期应计提更多"
print(f"  [加速性] 双倍法前两年计提 {ddb[:2].sum():.1f} 万 > 直线法 {sl[:2].sum():.1f} 万（税盾前置）")

pv = {name: 0.25 * sum(sch[t] / (1 + rate) ** (t + 1) for t in range(n))
      for name, sch in [("直线法", sl), ("双倍余额递减", ddb), ("年数总和法", syd)]}
for k, v in pv.items():
    print(f"  [税盾现值] {k}: {v:6.2f} 万（税率25%、折现8%）")
assert pv["双倍余额递减"] > pv["直线法"], "加速折旧的税盾现值应更高"
print(f"  双倍法比直线法多省税盾现值 {pv['双倍余额递减'] - pv['直线法']:.2f} 万——同样的总额，不同的时间形状")

print("\nALL ASSERTIONS PASSED")
