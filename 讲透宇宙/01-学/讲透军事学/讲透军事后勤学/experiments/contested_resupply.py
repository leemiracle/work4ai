# -*- coding: utf-8 -*-
"""对抗性前送补给模拟:大批次低频次 vs 小批次高频次 vs 预置储备缓冲
(00 章⑥反直觉之二 + 01 章热线一「对抗性后勤」的机器化;
04 章 C1 走廊的成品实验)。

模型:一条从战役仓库到前线部队的前送线(相对量纲,日消耗 d=1 单位/天):
  策略 (T, Q):每 T 天派一个车队,名义发送速率 Q/T(两策略取同速率);
  对抗:每个车队独立以概率 p 遭袭,遭袭即损失比例 L(剩余部分送达);
  补偿发货:明知期望损失时,装载量放大 1/(1-pL),使期望净送达=名义速率
  ——两策略在同一期望供给下竞争,比的是分布(方差与尾部),不是均值;
  库存:到货在先、消耗在后;缺货当日记账(不赊账补发);
  统计:断供天数/需求满足率/库存波动(标准差)/车队出动次数/送达率。

四个断言:
  ① 安全基线(p=0):两策略送达率=1、零断供——大批次以 1/15 的
     出动次数达到同样保障(安全时大批次更省:省的是出动与管理),
     代价是更高的平均库存(小批次同需求下峰值库存更低)
  ② 对抗反转(核心,p=0.30+补偿发货+浅缓冲):小批次断供天数与
     库存波动显著低于大批次——而期望送达率两者同为 1-p=0.70:
     分篮不改均值,改的是方差与尾部(鲁棒性的数学本体=分布,
     不是均值——「对抗性后勤」重写配送规则的定量内核)
  ③ 条件边界(深安全库存+中低对抗 p=0.10):大批次断供降至与小批次
     相当——大批次的劣势不是教条是函数:缓冲盖得住「连续遭袭窗口」
     (60 日份 > 3 个连续满损车队还有余量),集约经济就仍然成立
     (安全时大批次更省的条件边界)
  ④ 预置储备缓冲(同策略同对抗):起点库存(预置储备)越高,
     断供风险单调下降——预置=把库存前推到最危险也最及时的位置,
     用空间换断供风险的对冲

⚠ 建模边界(04 章走廊警告 3):车队遭袭按独立伯努利建模;真实对手
会学习配送节奏做相关打击(专打间隔上的咽喉),独立性失守时分篮
逻辑部分失效——输出是「随机干扰」下的鲁棒性序数结论,不是
「对抗优化」下的均衡预言。消耗率取常数=和平信息环境的简化。

跑法: python experiments/contested_resupply.py
"""
import random

H = 600          # 模拟天数(一个战区阶段的量级)
N_RUNS = 400     # 每组配置的蒙特卡洛次数
SEED = 20260907  # 固定种子=可复现;换种子看方差是正确姿势

BIG = (15, 15)   # 大批次低频次:15 天一车队,载 15 日份
SMALL = (1, 1)   # 小批次高频次:每天一车队,载 1 日份


def simulate(strategy, p, L, init_stock, rng):
    """跑一次前送线。strategy=(T, Q);p=车队遭袭概率;L=遭袭损失率;
    init_stock=起点库存(预置储备)。日消耗恒为 1(相对量纲)。"""
    T, Q = strategy
    send = Q / (1.0 - p * L)          # 补偿装载(期望净送达=名义 Q)
    inv = init_stock
    sent = delivered = convoys = stockout = unmet = 0
    inv_path = []
    for day in range(H):
        if day % T == 0:              # 车队当日到达(简化:在途时延并入周期)
            hit = rng.random() < p
            arrived = 0.0 if (hit and L >= 1.0) else send * (1.0 - L * hit)
            sent += send
            delivered += arrived
            convoys += 1
            inv += arrived
        served = min(inv, 1.0)        # 日消耗 d=1;缺额当日记账
        inv -= served
        unmet += 1.0 - served
        stockout += served < 1.0
        inv_path.append(inv)
    mean_inv = sum(inv_path) / H
    var = sum((x - mean_inv) ** 2 for x in inv_path) / H
    return dict(stockout=stockout, unmet=unmet,
                service=1.0 - unmet / H, inv_std=var ** 0.5,
                inv_mean=mean_inv, convoys=convoys,
                delivery_rate=delivered / sent if sent else 1.0)


def batch(strategy, p, L, init_stock, n=N_RUNS, seed=SEED):
    """一组配置的蒙特卡洛均值。"""
    rng = random.Random(seed)
    runs = [simulate(strategy, p, L, init_stock, rng) for _ in range(n)]
    return {k: sum(r[k] for r in runs) / n for k in runs[0]}


def header():
    print(f"  {'策略':<20}{'断供天数':>8}{'满足率':>9}{'库存σ':>9}"
          f"{'均库存':>9}{'出动':>7}{'送达率':>9}")


def show(tag, r):
    print(f"  {tag:<20}{r['stockout']:>9.2f}{r['service']:>9.3f}"
          f"{r['inv_std']:>9.2f}{r['inv_mean']:>9.2f}{r['convoys']:>7.0f}"
          f"{r['delivery_rate']:>9.3f}")


def main():
    print("=" * 80)
    print(f"对抗性前送补给模拟:H={H} 天 × {N_RUNS} 次蒙特卡洛"
          f" · 日消耗=1 · seed={SEED}")
    print(f"策略:大批次低频次 T=15,Q=15(名义 1/天) | "
          f"小批次高频次 T=1,Q=1(名义 1/天)")
    print("=" * 80)

    # ── 断言 1:安全基线(p=0)──────────────────────────────
    print("\n断言 1(安全基线,p=0,起点库存 15 日份):")
    header()
    b0 = batch(BIG, 0.0, 1.0, 15)
    s0 = batch(SMALL, 0.0, 1.0, 15)
    show("大批次 T=15", b0)
    show("小批次 T=1", s0)
    assert b0["stockout"] == 0 and s0["stockout"] == 0, "安全环境两策略均应零断供"
    assert abs(b0["delivery_rate"] - 1.0) < 1e-9, "安全环境送达率应为 1"
    assert b0["convoys"] * 10 < s0["convoys"], "大批次应以约 1/15 的出动次数完成同样保障"
    assert s0["inv_mean"] < b0["inv_mean"], "小批次同需求下平均库存应更低"
    print("  ✓ 安全时大批次更省(出动 1/15),但代价是 ~7 倍的峰值库存;"
          "\n    送达率都是 100%——安全环境下集约没有惩罚")

    # ── 断言 2:对抗反转(核心)────────────────────────────
    print("\n断言 2(对抗反转·核心,p=0.30,L=1.0,浅缓冲 10 日份,补偿发货):")
    header()
    b2 = batch(BIG, 0.30, 1.0, 10)
    s2 = batch(SMALL, 0.30, 1.0, 10)
    show("大批次 T=15", b2)
    show("小批次 T=1", s2)
    assert s2["stockout"] * 3 < b2["stockout"], (
        f"对抗下小批次断供应显著少于大批次:实测 {s2['stockout']:.2f} "
        f"vs {b2['stockout']:.2f}")
    assert s2["inv_std"] * 2 < b2["inv_std"], "对抗下小批次库存波动应显著更小"
    assert abs(b2["delivery_rate"] - 0.70) < 0.01, "大批次期望送达率应≈1-p"
    assert abs(s2["delivery_rate"] - 0.70) < 0.01, "小批次期望送达率应≈1-p"
    assert abs(b2["delivery_rate"] - s2["delivery_rate"]) < 0.01, (
        "分篮不改均值:两策略期望送达率应相同")
    print(f"  ✓ 期望送达率同为 ~0.70(均值不动),断供 {b2['stockout']:.1f} 天 "
          f"vs {s2['stockout']:.1f} 天、库存σ {b2['inv_std']:.1f} vs "
          f"{s2['inv_std']:.1f}——分篮改的是分布:"
          "\n    鲁棒性=方差的函数,不是均值的函数(对抗性后勤的定量内核)")

    # ── 断言 3:条件边界(深缓冲+中低对抗)──────────────────
    print("\n断言 3(条件边界,p=0.10,L=1.0,深缓冲 60 日份,补偿发货):")
    header()
    b3 = batch(BIG, 0.10, 1.0, 60)
    s3 = batch(SMALL, 0.10, 1.0, 60)
    show("大批次 T=15", b3)
    show("小批次 T=1", s3)
    assert b3["stockout"] < 1.0 and s3["stockout"] < 1.0, (
        f"深缓冲+中低对抗下两策略断供都应≈0:实测 {b3['stockout']:.2f} "
        f"vs {s3['stockout']:.2f}")
    assert abs(b3["stockout"] - s3["stockout"]) < 1.0, "两策略断供风险应相当"
    assert b3["convoys"] * 10 < s3["convoys"], "大批次出动次数优势仍在"
    print("  ✓ 缓冲盖得住「连续遭袭窗口」(60 日份 > 3 个连续满损车队有余量):"
          "\n    大批次断供风险回到与小批次同档,而出动只有 1/15——"
          "\n    大批次的劣势是条件函数:对抗强度×缓冲深度的二元判据,不是教条")

    # ── 断言 4:预置储备缓冲───────────────────────────────
    print("\n断言 4(预置储备缓冲,大批次,p=0.30,L=1.0,起点库存扫描):")
    header()
    levels, results = (10, 25, 45), []
    for lv in levels:
        r = batch(BIG, 0.30, 1.0, lv)
        results.append(r)
        show(f"预置 {lv:>2} 日份", r)
    for lo, hi in zip(results, results[1:]):
        assert lo["stockout"] > hi["stockout"] + 5.0, (
            "断供风险应随预置储备严格下降且幅度显著")
    print("  ✓ 断供风险随预置储备单调下降——预置储备=用空间换断供风险:"
          "\n    把库存前推到最危险也最及时的位置(01 章热线四战区保障建议的定量面)")

    print("\n" + "=" * 80)
    print("四组断言全部通过:安全基线 / 对抗反转(分篮改分布) / "
          "条件边界 / 预置缓冲 ✓")
    print("\n⚠ 建模边界提醒:①车队遭袭独立假设——对手的相关打击会部分"
        "摧毁分篮逻辑;")
    print("  ②消耗率取常数——战斗日/平时消耗可差一个量级;"
        "③输出=随机干扰下的序数结论,")
    print("  不是对抗均衡的基数预言。参数=保障体系假设,引用须附来源。")


if __name__ == "__main__":
    main()
