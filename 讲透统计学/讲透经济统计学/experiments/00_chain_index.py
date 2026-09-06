# -*- coding: utf-8 -*-
"""链式指数 vs 固定权重拉氏指数:替代偏差的数值实拍(两商品技术进步场景)。

00/02/04 章 配套实验。纯标准库,零依赖。

场景(鲍莫尔成本病 × 摩尔定律的极简版):
  商品 A「算力」——技术进步品,价格每年下降 10%:   p_A(t) = 1000 · 0.90^t
  商品 B「服务」——成本病品,价格每年上涨 4%:     p_B(t) = 40 · 1.04^t
  基期篮子:q_A(0)=1(1000 元),q_B(0)=50(2000 元)→ 基期支出份额 A 1/3 / B 2/3
  消费者有替代行为(需求自价格弹性,对降价品弹性更大):
    q_A(t) = q_A(0) · (p_A(t)/p_A(0))^(-2.0)   —— 算力越便宜买越多
    q_B(t) = q_B(0) · (p_B(t)/p_B(0))^(-0.3)   —— 服务涨价略微少买

三个指数(基期=100):
  固定权重拉氏(十年不换权重,模拟旧式 CPI):
    L_fix(t) = Σ p_t·q_0 / Σ p_0·q_0
  链式拉氏(每年换一次权重再连乘,模拟链式 CPI 的思路):
    L_chn(t) = Π_{s=1..t} Σ p_s·q_{s-1} / Σ p_{s-1}·q_{s-1}
  链式费雪(拉氏与帕氏的几何平均,美国 GDP 环比的实际做法,参考列):
    F_chn(t) = Π √(L_s · P_s),P_s = Σ p_s·q_s / Σ p_{s-1}·q_s

要看的读数:固定权重假设消费者十年不响应相对价格变化——
它给出的"生活成本涨幅"系统性高于链式(替代偏差);这就是
Boskin 委员会(1996)之后美国 CPI 从固定权重走向链式的数值原因。

跑法: python 讲透统计学/讲透经济统计学/experiments/00_chain_index.py
"""
import math

YEARS = 10
P_A0, P_B0 = 1000.0, 40.0          # 基期价格
Q_A0, Q_B0 = 1.0, 50.0             # 基期数量(基期支出 1000 vs 2000)
ELAST_A, ELAST_B = -2.0, -0.3      # 需求自价格弹性:对降价的算力更敏感

p = [(P_A0 * 0.90 ** t, P_B0 * 1.04 ** t) for t in range(YEARS + 1)]
q = [(Q_A0 * (0.90 ** t) ** ELAST_A, Q_B0 * (1.04 ** t) ** ELAST_B)
     for t in range(YEARS + 1)]


def cost(pa, pb, qa, qb):
    return pa * qa + pb * qb


def fixed_laspeyres(t):
    """固定权重:永远用基期篮子 q_0 计价。"""
    return cost(p[t][0], p[t][1], q[0][0], q[0][1]) / cost(p[0][0], p[0][1], q[0][0], q[0][1])


def chained_indices(t):
    """链式拉氏/帕氏/费雪:每年换权重,逐段连乘(01 段=拉氏段)。"""
    las = paas = fisher = 1.0
    for s in range(1, t + 1):
        (pa0, pb0), (pa1, pb1) = p[s - 1], p[s]
        (qa0, qb0), (qa1, qb1) = q[s - 1], q[s]
        las *= cost(pa1, pb1, qa0, qb0) / cost(pa0, pb0, qa0, qb0)   # 用上期量
        paas *= cost(pa1, pb1, qa1, qb1) / cost(pa0, pb0, qa1, qb1)  # 用当期量
        fisher *= math.sqrt(
            cost(pa1, pb1, qa0, qb0) / cost(pa0, pb0, qa0, qb0)
            * cost(pa1, pb1, qa1, qb1) / cost(pa0, pb0, qa1, qb1))
    return las, paas, fisher


def main():
    print("=" * 72)
    print("替代偏差实拍:固定权重拉氏 vs 链式(算力 -10%/年,服务 +4%/年,基期=100)")
    print("=" * 72)
    print(f"{'年':>3} {'固定拉氏':>9} {'链式拉氏':>9} {'链式费雪':>9} {'固定-链式(pp)':>13}")
    fix_prev, chn_prev = 100.0, 100.0
    for t in range(0, YEARS + 1):
        fix = fixed_laspeyres(t) * 100
        las, _, fis = chained_indices(t)
        chn = las * 100
        ann_fix = (fix / fix_prev - 1) * 100
        ann_chn = (chn / chn_prev - 1) * 100
        ann_note = "" if t == 0 else f"  年率: 固定 {ann_fix:+.2f}% vs 链式 {ann_chn:+.2f}%"
        print(f"{t:>3} {fix:>9.2f} {chn:>9.2f} {fis * 100:>9.2f} {fix - chn:>13.2f}{ann_note}")
        fix_prev, chn_prev = fix, chn

    fix10 = fixed_laspeyres(YEARS) * 100
    las10, paas10, fis10 = chained_indices(YEARS)
    chn10 = las10 * 100
    mean_bias = (math.log(fixed_laspeyres(YEARS)) - math.log(las10)) / YEARS * 100

    print()
    print("读数:")
    print(f"  · 十年累计:固定拉氏 {fix10:.1f} vs 链式拉氏 {chn10:.1f}——同一组价格数据,")
    print(f"    仅因『权重是否响应替代』,累计通胀相差 {fix10 - chn10:.1f} 点")
    print(f"  · 平均每年偏差约 {mean_bias:.2f} 个百分点(Boskin 委员会估计现实 CPI 替代偏差")
    print("    0.2-0.4 pp/年;本演示把替代弹性放大,是为了让偏差肉眼可见)")
    print(f"  · 链式帕氏 {paas10 * 100:.1f} ≤ 链式费雪 {fis10 * 100:.1f} ≤ 链式拉氏 {chn10:.1f}:")
    print("    帕氏/拉氏互为真生活成本指数(Konüs)的下/上界,费雪取几何中点(00 章)")

    # 断言 1: 固定权重高估通胀——固定拉氏累计 > 链式拉氏累计(替代偏差为正)
    assert fix10 > chn10, "固定权重应高估生活成本涨幅(替代方向:转向降价品)"

    # 断言 2: 偏差量级——十年累计至少 2 个百分点(演示场景放大过的替代弹性)
    assert fix10 - chn10 > 2.0, "替代偏差十年累计应超过 2 点"

    # 断言 3: 指数的对偶序——帕氏 ≤ 费雪 ≤ 拉氏(链式下逐段保持)
    assert paas10 <= fis10 <= las10, "帕氏 ≤ 费雪 ≤ 拉氏 的序被破坏?"

    print()
    print(f"自验证断言通过:固定 {fix10:.1f} > 链式 {chn10:.1f}(高估 {fix10 - chn10:.1f} 点);"
          f"帕氏 {paas10 * 100:.1f} ≤ 费雪 {fis10 * 100:.1f} ≤ 拉氏 {chn10:.1f} ✓")


if __name__ == "__main__":
    main()
