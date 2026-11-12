# -*- coding: utf-8 -*-
"""政务服务排队与数字化分流模拟:传统大厅 vs 数字化分流 vs 强制在线。

00-体系结构.md(反直觉 1:均值改善、分布恶化;假设表第四行:数字可及假设)、
03-可构造与结构.md(可构造对象 1:服务流程 schema 的渠道维度)与
04-公共管理转代码.md(走廊 1:政务服务排队与分流走廊)的配套实验。纯标准库。

模型(离散事件仿真,按"日"重复 DAYS 次,多日汇总;方案间共用随机数流):
  一个政务服务大厅,开放 T 分钟;需求按泊松流到达(λ/分钟);
  人群两类:数字能力人群(占比 1-d)与数字鸿沟人群(占比 d,如老年/低设备/低技能);
  渠道四条:在线办理(不进场)/预约(时间平滑后进综合窗口)/自助终端(快速)/
  综合窗口(慢速,FIFO 单队列多窗口);
  服务时间对数正态;耐心为指数分布,等待超过耐心即放弃(reneging)。

三个方案(cap=数字能力人群渠道比例,div=数字鸿沟人群渠道比例;
比例=(在线, 预约, 自助),其余走综合窗口):
  A 传统大厅:全员现场排队进综合窗口;
  B 数字化分流:能力人群分流到 在线30%/预约25%/自助20%/窗口25%;
                鸿沟人群全部走窗口(线下兜底);
  C 强制在线:  两类人群都强制 60% 在线——鸿沟人群线上失败率 70%,
                失败者一半当日再赴大厅、一半彻底放弃(办不成)。

排队论背景(Kingman VUT 公式):等待 ≈ 利用率项 × 变化性项 × 服务时间——
数字分流三箭齐发:线上化降利用率 ρ、预约平滑降到达变化性 c_a、自助终端降服务
时间 τ;但"强制在线"把失败成本转嫁给数字鸿沟人群——
数字化的收益记在均值上,代价记在分布上(谁被甩下)。

核心断言:
  1. B 相对 A:现场等待均值与 P90 尾部延迟双降;
  2. C 相对 B:均值口径更好看,但数字鸿沟人群有效完成率坍塌、放弃率跳升
     ——分配效应:同一系统,平均数与最弱人群的体验反向而行。

跑法: python3 -u experiments/service_queue_triage.py
"""

import math
import random
import statistics

# ---- 参数(全局常量) ----
T = 480.0                 # 大厅开放时长(分钟)
LAM = 0.85                # 需求到达率/分钟 → E[N]≈408 人/日
SERVERS = 6               # 综合窗口数
SVC_MEAN, SVC_SIGMA = 6.0, 0.7     # 窗口服务时间(对数正态)
KIOSKS = 2                # 自助终端数
KIOK_MEAN, KIOK_SIGMA = 3.0, 0.4   # 自助服务时间(对数正态)
DIVIDE_SHARE = 0.30       # 数字鸿沟人群占比
PATIENCE = {False: 70.0, True: 35.0}     # 指数耐心均值(分钟):能力/鸿沟
ONLINE_OK = {False: 0.95, True: 0.30}    # 线上一次办结率:能力/鸿沟
GIVEUP_ON_FAIL_DIVIDE = 0.5     # 鸿沟人群线上失败后彻底放弃的概率
FAIL_REATTEND_DELAY = (30.0, 90.0)      # 线上失败后再赴大厅的延迟(分钟)
DAYS = 60
SEED = 20260907

# 方案:渠道比例=(在线, 预约, 自助),其余走综合窗口
SCHEMES = [
    ("A 传统大厅",  {"cap": (0.00, 0.00, 0.00), "div": (0.00, 0.00, 0.00)}),
    ("B 数字化分流", {"cap": (0.30, 0.25, 0.20), "div": (0.00, 0.00, 0.00)}),
    ("C 强制在线",   {"cap": (0.60, 0.15, 0.10), "div": (0.60, 0.00, 0.00)}),
]


def gen_day(day):
    """生成一天的需求(泊松到达);方案间共用同一随机数流(共随机数降方差)。"""
    rng = random.Random(SEED + day)
    people = []
    t = rng.expovariate(LAM)
    while t < T:
        divide = rng.random() < DIVIDE_SHARE
        people.append({
            "t": t,
            "divide": divide,
            "patience": rng.expovariate(1.0 / PATIENCE[divide]),
        })
        t += rng.expovariate(LAM)
    return people


def route(people, si, day, scheme):
    """按方案把人分配到 在线/预约/自助/窗口;返回窗口队、自助队与线上结果。"""
    rng = random.Random(SEED + 1000 * (si + 1) + day)
    win, kio = [], []
    online_ok = {True: 0, False: 0}       # 线上一次办结(按人群)
    gave_up = {True: 0, False: 0}         # 线上失败后彻底放弃(按人群)
    for p in people:
        online, appt, kiosk = scheme["div" if p["divide"] else "cap"]
        u = rng.random()
        if u < online:
            if rng.random() < ONLINE_OK[p["divide"]]:
                online_ok[p["divide"]] += 1
            elif p["divide"] and rng.random() < GIVEUP_ON_FAIL_DIVIDE:
                gave_up[True] += 1        # 鸿沟人群:办不成,放弃
            else:
                q = dict(p)               # 线上失败,当日再赴大厅
                q["t"] = min(T - 1.0, p["t"] + rng.uniform(*FAIL_REATTEND_DELAY))
                win.append(q)
        elif u < online + appt:
            p["appt"] = True              # 预约:标记后统一平滑
            win.append(p)
        elif u < online + appt + kiosk:
            kio.append(p)
        else:
            win.append(p)                 # 现场排队进综合窗口
    # 预约平滑:重排到全天等距槽位(±5 分钟抖动)——Kingman 的 c_a 项
    appts = [p for p in win if p.get("appt")]
    if len(appts) >= 2:
        step = T / (len(appts) + 1)
        for i, p in enumerate(appts):
            p["t"] = min(T - 1.0, max(0.0, (i + 1) * step + rng.uniform(-5.0, 5.0)))
    win.sort(key=lambda p: p["t"])
    kio.sort(key=lambda p: p["t"])
    return win, kio, online_ok, gave_up


def serve(queue, n_servers, mean, sigma, si, day):
    """FIFO 多服务台仿真;等待超过耐心即放弃(不占服务台)。"""
    rng = random.Random(SEED + 10007 * (si + 1) + day)
    free = [0.0] * n_servers
    waits, served, reneged = [], {True: 0, False: 0}, {True: 0, False: 0}
    for p in queue:
        i = min(range(n_servers), key=lambda k: free[k])
        start = max(free[i], p["t"])
        wait = start - p["t"]
        if wait > p["patience"]:
            reneged[p["divide"]] += 1
            continue
        free[i] = start + rng.lognormvariate(math.log(mean) - sigma * sigma / 2.0,
                                             sigma)
        waits.append(wait)
        served[p["divide"]] += 1
    return waits, served, reneged


def run_scheme(si, scheme):
    """跑 DAYS 天,汇总会分组的流量与等待分布。"""
    acc = {"waits": [], "demand": {True: 0, False: 0},
           "online_ok": {True: 0, False: 0}, "gave_up": {True: 0, False: 0},
           "served": {True: 0, False: 0}, "reneged": {True: 0, False: 0}}
    for day in range(DAYS):
        people = gen_day(day)
        win, kio, online_ok, gave_up = route(people, si, day, scheme)
        for g in (True, False):
            acc["demand"][g] += sum(1 for p in people if p["divide"] == g)
            acc["online_ok"][g] += online_ok[g]
            acc["gave_up"][g] += gave_up[g]
        for waits, served, reneged in (
            serve(win, SERVERS, SVC_MEAN, SVC_SIGMA, si, day),
            serve(kio, KIOSKS, KIOK_MEAN, KIOK_SIGMA, si, day),
        ):
            acc["waits"].extend(waits)
            for g in (True, False):
                acc["served"][g] += served[g]
                acc["reneged"][g] += reneged[g]
    return acc


def completion(acc, divide):
    """有效完成率 =(线上办结+现场办结)/需求;放弃率 = 1−完成率。"""
    done = acc["online_ok"][divide] + acc["served"][divide]
    return done / acc["demand"][divide]


def main():
    print("=" * 92)
    print("政务服务排队:传统大厅 vs 数字化分流 vs 强制在线 "
          f"(λ={LAM}/min, 窗口×{SERVERS} τ={SVC_MEAN}min, 自助×{KIOSKS} "
          f"τ={KIOK_MEAN}min, 鸿沟人群={int(DIVIDE_SHARE*100)}%, {DAYS} 日汇总)")
    print("=" * 92)
    print(f"{'方案':<10} {'进场需求':>8} {'线上办结':>8} {'现场等待均值':>12} "
          f"{'P90':>6} {'鸿沟完成率':>10} {'鸿沟放弃率':>10} {'总体完成率':>10}")
    res = {}
    for si, (name, scheme) in enumerate(SCHEMES):
        acc = run_scheme(si, scheme)
        mean_w = statistics.fmean(acc["waits"])
        p90 = statistics.quantiles(acc["waits"], n=10, method="inclusive")[-1]
        demand_all = sum(acc["demand"].values())
        online_all = sum(acc["online_ok"].values())
        comp_div, comp_all = completion(acc, True), \
            sum(acc["online_ok"].values()) + sum(acc["served"].values())
        comp_all /= demand_all
        res[name] = (mean_w, p90, comp_div, 1.0 - comp_div, comp_all, acc)
        print(f"{name:<10} {demand_all:>8d} {online_all:>8d} {mean_w:>12.2f} "
              f"{p90:>6.2f} {comp_div:>10.3f} {1.0 - comp_div:>10.3f} "
              f"{comp_all:>10.3f}")

    (mA, pA, cAd, _, cAa, _), (mB, pB, cBd, gBd, cBa, _), \
        (mC, pC, cCd, gCd, cCa, _) = (res[n] for n, _ in SCHEMES)

    print()
    print("读数:")
    print("  · A→B:线上化移走负载(ρ 0.85→0.55)、预约平滑到达(Kingman 的 c_a 项)、")
    print("    自助终端缩短服务(τ 项)——三箭齐发,等待均值与 P90 同步下降,")
    print("    且鸿沟人群全走窗口兜底,完成率不降反升(放弃率≈现场排队放弃)")
    print("  · B→C:窗口负载进一步下降,均值口径更好看;但鸿沟人群被强制在线——")
    print(f"    线上一次办结率仅 {ONLINE_OK[True]:.0%},失败后 "
          f"{GIVEUP_ON_FAIL_DIVIDE:.0%} 彻底放弃 → 完成率 "
          f"{cBd:.3f} → {cCd:.3f} 坍塌")
    print("    ——数字化的收益记在均值上,代价记在分布上(谁被甩下)")
    print("  · P90 与分组完成率才是公共服务的 SLA:平均等待下降可以与")
    print("    最弱人群的体验恶化同时发生(性能工程分布优先纪律的公共版)")

    # ---- 自验证断言 ----
    # 断言 1:数字化分流降低现场等待均值与 P90 尾部
    assert mB < mA, f"分流应降低均值等待: B {mB:.2f} vs A {mA:.2f}"
    assert pB < pA, f"分流应降低 P90: B {pB:.2f} vs A {pA:.2f}"
    # 断言 2:分流保住(且略升)总体与鸿沟完成率——线下兜底的功劳
    assert cBd > 0.90, f"分流下鸿沟人群完成率应 >0.90: {cBd:.3f}"
    assert cBa > cAa + 0.02, f"分流应提高总体完成率: B {cBa:.3f} vs A {cAa:.3f}"
    # 断言 3:强制在线——均值口径更好看,鸿沟人群可及性坍塌(分配效应)
    assert mC < mB, f"强制在线应进一步压低均值(反讽点): C {mC:.2f} vs B {mB:.2f}"
    assert cCd < cBd - 0.15, f"强制在线应重创鸿沟完成率: C {cCd:.3f} vs B {cBd:.3f}"
    assert gCd > gBd + 0.10, f"强制在线应推高鸿沟放弃率: C {gCd:.3f} vs B {gBd:.3f}"
    assert cCa < cBa - 0.03, f"总体完成率应随强制在线下降: C {cCa:.3f} vs B {cBa:.3f}"
    # 断言 4:量纲体检——传统大厅在 ρ=0.85 下等待可观但不爆炸(模型合理性)
    assert 0.5 < mA < 8.0 and pA > mA, "A 方案等待量级应合理且右偏(P90>均值)"
    print("\n✓ 自验证通过:分流双降等待(均值+P90)且兜底保完成率 | 强制在线"
          "均值更好看但鸿沟完成率 %.3f→%.3f 坍塌、放弃率 %.3f→%.3f 跳升 | "
          "总体完成率 %.3f→%.3f | A 方案量纲合理" %
          (cBd, cCd, gBd, gCd, cBa, cCa))


if __name__ == "__main__":
    main()
