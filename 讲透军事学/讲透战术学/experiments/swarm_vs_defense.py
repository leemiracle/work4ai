# -*- coding: utf-8 -*-
"""蜂群饱和攻击 vs 点防御体系:拦截概率×火力通道×到达窗口的交换模型(01/04 章配套实验)。

主题(与军事理论家族的兰彻斯特实验互链不重复——那边管"两军对耗",
这边管"饱和与通道";排队论视角,火力通道=服务台):
低成本蜂群对点防御体系的突防分布与成本交换。

模型:
  防御方:单发拦截概率 p;火力通道数 k(同时接战目标数上限);
          每次接战占用通道 tau 个时间单位(发射-评估-再接战)。
  攻击方:n 架在长度可配的到达窗口内进入拦截区,每架暴露 W 个
          时间单位(过此即突防);未击落者可被再次接战。
  接战节拍:离散周期 t = tau, 2tau, 3tau, …;每周期每通道打 1 架、
  耗 1 发导弹、命中概率 p;优先接战最先突防者(最早到期者)。
  记 C = W // tau(单架暴露窗内的拦截轮次),核心量:
    饱和拐点 n* = k·C;期望突防 E[pen] ≈ n − p·min(有效接战)——
    轻载区(n ≤ k):E[pen] = n·(1−p)^C;饱和区(n ≥ 3kC):E[pen] = n − p·k·C。

四组断言:
  ① 饱和律:p=1 时严格成立 突防 = max(0, n − k·C)(通道买到天花板,
     数量买到线性);p=0.7 时饱和区 E[pen] ≈ n − p·k·C,
     饱和段边际斜率 ≈ 1(过拐点后每增一架几乎必然突防)。
  ② 时间压缩律:同样的 n,压缩到达(齐射/隐蔽抵近)比拉长到达
     逐架放入突防多得多——饱和的第一变量是到达速率 n/T,不是数量 n
     (01 章"蛛网"式隐蔽蜂群模板的抽象:公开研究文献通说,检索校准 2026-09-07)。
  ③ 成本交换律:攻击方"每突防一架的摊销成本" ≪ 防御方"每击落一架
     的导弹成本"(廉价可消耗平台对昂贵拦截弹的量级不对称——
     平台/拦截弹单价取公开研究评论口径的量级示例,只做序数比较)。
  ④ 概率上限律:p<1 时全拦只能多发齐打:单架漏拦率 (1−p)^m 指数
     下降,导弹消耗线性上升——概率的账与钱的账不同斜率。

⚠ 概念辨析(01 章热线一,[2025·Military Review]《Defining Swarm》,
  检索校准 2026-09-07):
  「集群使用」(massed employment)≠「蜂群」(swarm):
  集群使用=数量集中于同一时空,动作由预定计划或人工集中指挥;
  蜂群=节点间自治协同,行为由本地交互涌现。
  本模型只建"到达流"——对防御方两者同构(只见 n 架到达),
  但反制面不同:反集群靠预测与通道,反蜂群还须破坏其交互
  (导航基准/时统/通信拓扑)。到达流之外的一切是本模型的
  显式边界:不建模什么,与建模什么同等重要。

⚠ 参数纪律(承家族 02/04 章:参数=兵棋观):p/k/tau/W/单价均为
  教科书级示例参数;结论只做结构与序数比较,不做基数宣称。

跑法:python experiments/swarm_vs_defense.py(全部 assert 通过即 exit 0)
"""

import random
from collections import deque


def simulate(n, k, p, tau, W, arrivals, trials, seed=7):
    """蒙特卡洛突防模拟。

    arrivals:n 个到达时刻的升序列表(浮点,单位任意但一致);
    返回 (平均突防数, 平均耗弹数)。
    接战条件:arrival < t <= arrival+W(到而后打,到期即突防)。
    """
    rng = random.Random(seed)
    T_end = arrivals[-1] + W          # 最后一个到期时刻;其后清点存活
    total_pen = total_ms = 0
    for _ in range(trials):
        alive = deque()               # 在飞目标(存到期时刻,升序)
        pen = ms = 0
        ai = 0
        t = tau
        while t <= T_end:
            while ai < n and arrivals[ai] < t:      # 新到达
                alive.append(arrivals[ai] + W)
                ai += 1
            while alive and alive[0] < t:           # 已到期=突防
                alive.popleft()
                pen += 1
            engaged = min(k, len(alive))            # 通道分配
            if engaged:
                ms += engaged
                kills = sum(1 for _ in range(engaged) if rng.random() < p)
                for _ in range(kills):              # 优先打最先到期者
                    alive.popleft()
            t += tau
        pen += len(alive)                           # 区内残存者亦突防
        total_pen += pen
        total_ms += ms
    return total_pen / trials, total_ms / trials


def salvo_arrivals(n):
    """齐射:全部 t=0 到达(压缩到达的极限)。"""
    return [0.0] * n


def spread_arrivals(n, spacing):
    """拉长到达:逐架间隔 spacing(串行放入的极限)。"""
    return [i * spacing for i in range(n)]


def main():
    # 基准参数:k=4 通道 / tau=1 / 暴露窗 W=8 → 拦截轮次 C=8,容量 kC=32
    K, TAU, W = 4, 1, 8
    C = W // TAU
    CAP = K * C
    P = 0.7
    TRIALS = 4000
    print("=" * 76)
    print(f"蜂群饱和 vs 点防御:k={K} 通道 · τ={TAU} · 暴露窗 W={W}"
          f" → 拦截轮次 C={C},通道容量 k·C={CAP}")
    print("=" * 76)

    # ── 断言组①:饱和律 ────────────────────────────────────
    print(f"\n[1] 饱和律(p={P};突防数随 n 的分段线性)")
    print(f"{'n':>4} {'平均突防':>8} {'解析(饱和区 n−p·kC)':>16}")
    for n in (4, 8, 16, 32, 48, 64, 96, 128):
        pen, ms = simulate(n, K, P, TAU, W, salvo_arrivals(n), TRIALS)
        print(f"{n:>4} {pen:>8.2f} {max(0.0, n - P * CAP):>16.2f}")

    # ①a p=1 严格版:突防 = max(0, n − k·C),逐周期确定性击落
    for n in (100, 20):
        pen, ms = simulate(n, K, 1.0, TAU, W, salvo_arrivals(n), 200)
        assert pen == max(0, n - CAP), \
            f"p=1 饱和律:突防应恰为 max(0, {n}−{CAP})"
    print(f"  ①a p=1 严格版:n=100→突防 68、n=20→突防 0 "
          f"= max(0, n−k·C) ✓(通道是天花板,数量是线性)")

    # ①b p=0.7 饱和区(n=3·kC 起,每周期通道必满):E[pen]=n−p·kC
    pen96, ms96 = simulate(96, K, P, TAU, W, salvo_arrivals(96), TRIALS)
    assert abs(pen96 - (96 - P * CAP)) < 0.5, "饱和区期望突防 = n − p·k·C"
    assert abs(ms96 - CAP) < 0.5, "饱和区每周期通道必满:耗弹 = k·C"
    print(f"  ①b p=0.7 饱和区:n=96 → 突防 {pen96:.2f} ≈ 96−0.7×32=73.6,"
          f" 耗弹 {ms96:.1f} = 32 ✓")

    # ①c 饱和段边际斜率 ≈ 1(过拐点后每增一架几乎必然突防)
    pen120, _ = simulate(120, K, P, TAU, W, salvo_arrivals(120), TRIALS)
    slope = (pen120 - pen96) / (120 - 96)
    assert abs(slope - 1.0) < 0.05, "饱和段边际斜率应 ≈ 1"
    print(f"  ①c 边际斜率:({pen120:.2f}−{pen96:.2f})/24 = {slope:.3f} ≈ 1 ✓"
          f"——拐点 n*=k·C={CAP} 之后,数量线性买突防")

    # ①d 轻载区(n ≤ k,逐架全打):E[pen] = n·(1−p)^C
    penL, _ = simulate(3, K, 0.6, TAU, 4, salvo_arrivals(3), TRIALS)
    qL = (1 - 0.6) ** (4 // TAU)
    assert abs(penL - 3 * qL) < 0.04, "轻载区期望突防 = n·(1−p)^C"
    print(f"  ①d 轻载区:k=4,τ=1,W=4(C=4),p=0.6,n=3 → 突防 {penL:.3f}"
          f" ≈ 3×0.4^4={3*qL:.3f} ✓——通道空闲时漏拦只来自概率,不来自容量")

    # ── 断言组②:时间压缩律 ────────────────────────────────
    print(f"\n[2] 时间压缩律(同样 n={100},两种到达节奏)")
    pen_salvo, _ = simulate(100, K, P, TAU, W, salvo_arrivals(100), TRIALS)
    pen_spread, _ = simulate(100, K, P, TAU, W,
                             spread_arrivals(100, 2 * W), 1000)
    assert abs(pen_salvo - (100 - P * CAP)) < 0.5, "齐射=饱和区公式"
    assert pen_spread < 0.5, "间隔 2W 逐架放入:暴露窗互不重叠,近乎全灭"
    assert pen_salvo - pen_spread > 70, "压缩到达与拉长到达的突防差应巨大"
    print(f"  齐射(t=0 同时到):突防 {pen_salvo:.1f} ≈ {100 - P*CAP:.1f}")
    print(f"  逐架(间隔 {2*W} 串行):突防 {pen_spread:.2f} ≈ 100×0.3^8"
          f"={100*(1-P)**C:.2f}")
    print("  ✓ 饱和的第一变量是到达速率 n/T,不是数量 n——")
    print("    公开研究所述'蛛网'式模板的排队论骨架:隐蔽抵近=压缩 T"
          "(Lieber 2025,检索校准 2026-09-07)")

    # ── 断言组③:成本交换律 ────────────────────────────────
    print("\n[3] 成本交换律(量级示例参数:平台单价 1,拦截弹单价 150)")
    C_A, C_I = 1.0, 150.0
    kills = 100 - pen_salvo
    att_unit = 100 * C_A / pen_salvo          # 攻方:每突防一架摊销成本
    def_unit = CAP * C_I / kills              # 防方:每击落一架导弹成本
    assert att_unit * 50 < def_unit, "突防摊销单价应远低于击落单价"
    assert att_unit < C_I / 10, "突防一架的成本应远低于一发拦截弹"
    print(f"  攻方每突防一架:{att_unit:.1f} 单位(100 架÷{pen_salvo:.0f} 突防)")
    print(f"  防方每击落一架:{def_unit:.0f} 单位(32 发÷{kills:.1f} 击落)")
    print(f"  ✓ 不对称约 {def_unit/att_unit:.0f} 倍——拦截弹单价≫平台单价时,"
          "'打不光的最好办法是别让它找到你'(01 章疏散+硬化路线的模型面)")

    # ── 断言组④:概率上限律 ────────────────────────────────
    print("\n[4] 概率上限律(单架被接战 m 次:漏拦率 (1−p)^m)")
    rng = random.Random(11)
    for m in (1, 2, 3):
        leaks = sum(1 for _ in range(20000)
                    if not any(rng.random() < P for _ in range(m)))
        rate = leaks / 20000
        theory = (1 - P) ** m
        tol = 5 * (theory * (1 - theory) / 20000) ** 0.5 + 0.002
        assert abs(rate - theory) < tol, f"m={m} 漏拦率应≈(1−p)^m"
        print(f"  m={m}:实测 {rate:.4f} ≈ 理论 {theory:.4f} ✓"
              f"(导弹消耗 ×{m})")
    print("  ✓ 漏拦率指数下降、导弹线性上升:概率的账与钱的账不同斜率;"
          "再叠①——过容量拐点,多发齐打也拦不住(容量先于概率饱和)")

    print("\n" + "=" * 76)
    print("四组断言全部通过:饱和律 / 时间压缩律 / 成本交换律 / 概率上限律 ✓")
    print("⚠ 概念边界:本模型只建到达流——『蜂群』(自治交互涌现)与")
    print("  『集群使用』(massed employment,预定计划/人工集中指挥)在此")
    print("  同构(Military Review 2025《Defining Swarm》,检索校准 2026-09-07);")
    print("  交互层(导航基准/时统/拓扑)须另行建模。参数=兵棋观,"
          "结论只做序数比较。")


if __name__ == "__main__":
    main()
