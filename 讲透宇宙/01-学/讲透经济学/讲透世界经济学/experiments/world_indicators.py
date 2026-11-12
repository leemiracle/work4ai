# -*- coding: utf-8 -*-
"""
世界经济学指标断言（走廊1：套利检测 + 走廊2：RCA + 走廊3：份额与恒等式）
对应章：讲透世界经济学/04-世界经济学转代码.md

数据口径（2026-09 模型知识核对；如与 IMF WEO/官方 BOP 不符以原始出处为准）：
- 汇率：教学构造（一致报价组 + 一处扰动）
- 贸易矩阵：教学构造（RCA 定义即算法的演示）
- 世界份额：IMF WEO 口径 2023 年名义 GDP（宽区间断言）
"""
# ── 三边套利：USD → JPY → EUR → USD ────────────────────────────
# 一致报价组：EUR/JPY 恰等于 EUR/USD × USD/JPY
USDJPY, EURUSD, EURJPY = 150.00, 1.0800, 162.00   # 1.08×150=162 ✓
EURJPY_BAD = 158.00                                # 扰动报价（偏离约 2.5%）

def loop_usdjpy_eur(usdjpy, eurusd, eurjpy):
    """1 USD → JPY → EUR → USD 的环积（=1 表示无套利）"""
    return usdjpy * eurusd / eurjpy

def main():
    # 断言1：一致报价组环积贴 1（无套利，带宽=0.5% 点差量级）
    loop = loop_usdjpy_eur(USDJPY, EURUSD, EURJPY)
    assert abs(loop - 1.0) < 0.005, loop
    print(f"[1] 一致报价环积 = {loop:.4f}（无套利：EUR/JPY=EUR/USD×USD/JPY）")

    # 断言2：扰动一处报价 → 套利现身，利润率可算
    loop_bad = loop_usdjpy_eur(USDJPY, EURUSD, EURJPY_BAD)
    assert abs(loop_bad - 1.0) > 0.01, loop_bad
    print(f"[2] 扰动后环积 = {loop_bad:.4f} → 套利利润 ≈ {(loop_bad-1)*100:.1f}%"
          f"（买 JPY 卖坏价 EURJPY）")

    # 断言3：RCA——构造矩阵中每国的设计优势被 RCA 检出
    X = {  # 出口矩阵（教学构造）：国家 × 品类
        "A国": {"机械": 60, "纺织": 10, "能源": 5},
        "B国": {"机械": 10, "纺织": 40, "能源": 10},
        "C国": {"机械": 5,  "纺织": 10, "能源": 50},
    }
    sectors = ["机械", "纺织", "能源"]
    grand = sum(sum(row.values()) for row in X.values())
    world_share = {s: sum(X[c][s] for c in X) / grand for s in sectors}
    rca = {c: {s: (X[c][s] / sum(X[c].values())) / world_share[s] for s in sectors}
           for c in X}
    for c, expect in [("A国", "机械"), ("B国", "纺织"), ("C国", "能源")]:
        best = max(rca[c], key=rca[c].get)
        assert best == expect and rca[c][expect] > 1.8, (c, rca[c])
    print(f"[3] RCA 检出设计优势：A→机械 {rca['A国']['机械']:.2f}，"
          f"B→纺织 {rca['B国']['纺织']:.2f}，C→能源 {rca['C国']['能源']:.2f}"
          f"（基线=1，>1 即相对专注）")

    # 断言4：世界经济份额（IMF WEO 口径 2023 名义，宽区间）
    share_2023 = {"美国": 26.3, "中国": 17.0, "欧盟": 17.2, "日本": 4.0}
    assert 24 < share_2023["美国"] < 28 and 15 < share_2023["中国"] < 19
    assert 15 < share_2023["欧盟"] < 20 and 3.5 < share_2023["日本"] < 4.5
    top3 = share_2023["美国"] + share_2023["中国"] + share_2023["欧盟"]
    assert 55 < top3 < 65, top3
    print(f"[4] 2023 名义份额：{share_2023}——三极合计 {top3:.0f}%"
          f"（世界从一超多强漂向三极）")

    # 断言5：国际收支恒等式——复式记账必平，误差项是仪表盘
    bop = {"经常账户CA": -400, "资本账户KA": 10, "金融账户FA": 380, "误差EO": 10}
    assert sum(bop.values()) == 0, bop
    assert abs(bop["误差EO"]) / abs(bop["经常账户CA"]) < 0.05
    print(f"[5] BOP 恒等式：{bop} → 合计=0 ✓（逆差由金融账户融资，"
          f"误差项<CA 的 5%）")

    print("\n全部断言通过 ✓ （守恒律执行器：套利/RCA/份额/恒等式）")

if __name__ == "__main__":
    main()
