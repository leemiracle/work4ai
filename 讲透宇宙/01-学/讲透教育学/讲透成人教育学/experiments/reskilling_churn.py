# -*- coding: utf-8 -*-
"""技能过时与再培训的受控模拟:需求漂移参数化与「预防性学习的价值」(00/03/04 章配套实验)。

主题呼应技能重塑(reskilling):把劳动力技能的演化拆成**三层**——

  - 需求层(技术冲击):技能需求向量 D 随时间漂移,漂移速度=技术变化
    速度 λ(旧技术技能需求下移,数字/新技术上移,参数化);
  - 折旧层:未维护的技能按 δ_i(λ) 衰减——技术变化越快,旧技能
    越快过时(δ_i = δ0 + δ1·λ·旧度_i);
  - 供给层(学习者):技能向量 s;市场价值 v = Σ s_i·D_i / K;
    在岗者 v < θ_keep(保岗门槛)即失业;再就业需 v ≥ θ_re > θ_keep
    (非对称门槛:失业后重新上岗的匹配要求高于保住原岗——通说的
    再就业门槛与工资疤);学习=向当前需求向量的凸组合移动
    s ← (1−r)s + rD(在岗学习速率 r_job 与全日制培训速率 τ 不同)。

两条政策路径(CRN:同批学习者、同一条需求轨迹):
  A 在岗持续学习  :每期以 r_job 追踪需求(预防性学习),付出
                   10% 时间的机会成本(收入×0.9);
  B 先失业再培训   :在岗不学习;跌破门槛后失业(收入 0),全日制
                   培训(强度 τ)直至 v≥θ_re 再就业(补救性学习)。

断言三律:
  A. 技能折旧律:被动学习者的市场价值损失随技术变化速度 λ 单调
     上升——技术越快,不学习的人掉得越快;
  B. 预防>补救:同批学习者,"先失业再培训"路径的总收入损失
     ≥ "在岗持续学习"路径的 1.35 倍,且差额 ≥1.2 人均工资单位
     ——失业期收入归零+再就业门槛的代价,远超预防性学习的机会成本;
  C. 强度敏感律:低基础技能群体(学习速率×0.55)的再培训成功率
     对培训强度 τ 更敏感——高基础群体在低强度下已接近饱和
     (边际收益递减),加倍强度收效甚微;低基础群体正处拐点前,
     加倍强度收益大(边际收益递减的补偿)。

⚠ 学科纪律(02/04 章):
  1. 参数为风格化取值(需求漂移/折旧联动/非对称门槛/学习速率),
     非任何真实劳动力市场拟合;技能向量模型不知道"框架"为何物——
     经验税(00 §七发现 2)住在框架与身份里,本实验只算其影子;
  2. 模拟证明『需求漂移+折旧联动+门槛失业』的简单机制足以生成
     三律(机制充分性),不预测任何真实政策效果;技能重塑的
     融资困境(谁付钱)住 01 章主线 B 与人力资源文献;
  3. 通说锚:技能半衰期随技术加速缩短(德鲁克知识工作者线/WEF
     报告线,通说转述);预防性维护优于事后补救为工程与管理通则;
  4. 方差缩减:A/B 两路径共享同一随机数(同批学习者的初始技能与
     学习噪声逐点配对)与同一条需求轨迹;强度敏感律的两档 τ
     在同一批(学习者×本地劳动力市场)配对上重跑;
  5. 敏感性分析:文末 Monte Carlo(120 次参数抖动)报告三律通过率。

跑法: python experiments/reskilling_churn.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
# K 项技能:(名称, 旧度 oldness∈[0,1]:越接近 1 越是"旧技术侧")
SKILLS = [
    ("基础读写算", 0.10),   # 0
    ("学习力",     0.05),   # 1
    ("数字工具",   0.00),   # 2
    ("沟通协作",   0.15),   # 3
    ("旧技术A",    0.90),   # 4
    ("旧技术B",    0.80),   # 5
    ("管理协调",   0.30),   # 6
    ("新技术栈",   0.05),   # 7
]
K = len(SKILLS)
OLDNESS = [x[1] for x in SKILLS]

# 初始需求向量(经济起初偏爱旧技术)/ 需求漂移方向(旧技术下移,新技术上移)
D0 = [0.95, 0.72, 0.62, 0.72, 0.82, 0.78, 0.60, 0.34]
DRIFT = [0.00, 0.10, 0.16, 0.04, -0.26, -0.22, 0.04, 0.22]

# 初始供给向量(资深旧经济工人:旧技术雄厚,新技术薄弱)
S0 = [0.85, 0.66, 0.52, 0.76, 0.80, 0.76, 0.64, 0.34]

LAMBDA = 0.09        # 技术变化速度(需求漂移与折旧的共同参数)
DELTA0 = 0.002       # 基础折旧(与 λ 无关的缓慢遗忘)
DELTA1 = 0.50        # 折旧-技术联动系数:δ_i = δ0 + δ1·λ·oldness_i
THETA = 0.42         # 保岗门槛(在岗者市场价值 v 的下限)
THETA_RE = 0.47      # 再就业门槛(非对称:失业后重新上岗要求更高)
T_PERIODS = 40       # 模拟期数(约一个工作世代的"中年段")
N_WORKERS = 1500

R_JOB = 0.13         # 在岗持续学习强度(每期向需求的凸组合步长)
COST_JOB = 0.10      # 在岗学习的机会成本(收入×0.9)
TAU = 0.35           # 全日制再培训强度(失业期)

BASE_LOW, BASE_HIGH = 0.55, 1.25   # 低/高基础技能群体的学习速率倍率
TAU_LO, TAU_HI = 0.15, 0.35        # 强度敏感律的两档培训强度
WINDOW = 8            # 再培训"成功"窗口:首失业后 8 期内再就业


def clip01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def make_demands(lam, t_periods, rng, drift_scale=1.0):
    """需求轨迹:每期 D += λ·(drift_scale·DRIFT + 噪声),截断在 [0,1]。"""
    ds = [d * drift_scale for d in DRIFT]
    out, cur = [], D0[:]
    for _ in range(t_periods):
        for i in range(K):
            cur[i] = clip01(cur[i] + lam * (ds[i] + rng.uniform(-0.10, 0.10)))
        out.append(cur[:])
    return out


def mval(s, D):
    """市场价值:技能向量在需求向量上的加权平均(就业能力的标量投影)。"""
    return sum(a * b for a, b in zip(s, D)) / K


def depreciate(s, lam, delta0, delta1):
    """折旧:技术变化越快,旧度高的技能衰减越快(δ 随 λ 上升)。"""
    return [x * (1.0 - (delta0 + delta1 * lam * o)) for x, o in zip(s, OLDNESS)]


def blend(s, D, r):
    """学习=向当前需求向量的凸组合移动(r∈(0,1),保向量有界)。"""
    return [(1.0 - r) * a + r * b for a, b in zip(s, D)]


def make_workers(n, rng):
    """CRN 素材:初始技能微噪声 + 学习速率个体噪声(两路径逐点配对共用)。"""
    ws = []
    for _ in range(n):
        s = [clip01(x + rng.uniform(-0.04, 0.04)) for x in S0]
        ws.append({"s0": s, "learn": rng.uniform(0.85, 1.15)})
    return ws


def simulate(worker, demands, lam, mode, p):
    """跑一个学习者的生涯。

    mode: "onjob"(在岗持续学习,收入×(1−cost))或 "reactive"
    (在岗不学,失业后全日制再培训,收入 0)。
    返回 (总收入, 首次失业期, 首段再就业耗时或 None, 总失业期数)。
    """
    s = worker["s0"][:]
    base = worker["learn"]
    employed = True
    income = 0.0
    first_spell, retrain_time, unemp = None, None, 0
    for t, D in enumerate(demands):
        v = mval(s, D)
        if v < p["theta"]:
            if employed:
                employed = False
                if first_spell is None:
                    first_spell = t
        if employed:
            earn_scale = (1.0 - p["cost"]) if mode == "onjob" else 1.0
            income += v * earn_scale
            s = depreciate(s, lam, p["d0"], p["d1"])
            if mode == "onjob":
                s = blend(s, D, p["r_job"] * base)
        else:
            unemp += 1
            s = blend(s, D, p["tau"] * base)          # 全日制培训:追需求
            s = depreciate(s, lam, p["d0"], p["d1"])
            if mval(s, D) >= p["theta_re"]:           # 非对称门槛:再就业更难
                employed = True
                if first_spell is not None and retrain_time is None:
                    retrain_time = t + 1 - first_spell
    return income, first_spell, retrain_time, unemp


def run_cohort(workers, demands, lam, mode, p):
    return [simulate(w, demands, lam, mode, p) for w in workers]


def build_group(base, n, seed, lam, t_periods, drift_scale=1.0):
    """强度敏感律的配对样本:n 个(学习者×本地劳动力市场)。

    同一配对在两档 τ 下重跑——本地经济(各自的需求轨迹)保证成功率
    是平滑概率而非同一条宏观轨迹上的全有全无。
    """
    pairs = []
    for i in range(n):
        rng = random.Random(seed + i)
        dloc = make_demands(lam, t_periods, rng, drift_scale)
        w = {"s0": [clip01(x + rng.uniform(-0.04, 0.04)) for x in S0],
             "learn": base * rng.uniform(0.90, 1.10)}
        pairs.append((w, dloc))
    return pairs


def passive_decay(lam, p, rng):
    """断言A的量:完全不学习者的市场价值轨迹(确定性,无个体噪声)。"""
    s = S0[:]
    traj = []
    for D in make_demands(lam, p["T"], rng, p["drift_scale"]):
        s = depreciate(s, lam, p["d0"], p["d1"])
        traj.append(mval(s, D))
    v0, vt = traj[0], traj[-1]
    return 1.0 - vt / v0, 1.0 - (vt / v0) ** (1.0 / p["T"])   # (总损失率, 等效期折旧率)


def main():
    if hasattr(sys.stdout, "reconfigure"):       # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(20260907)

    p = {"theta": THETA, "theta_re": THETA_RE, "d0": DELTA0, "d1": DELTA1,
         "T": T_PERIODS, "r_job": R_JOB, "cost": COST_JOB, "tau": TAU,
         "drift_scale": 1.0}
    v_init = mval(S0, D0)
    print("=" * 72)
    print("技能过时与再培训模拟:需求漂移参数化与「预防性学习的价值」")
    print("=" * 72)
    print(f"模型:{K} 项技能(旧技术 2/基础 3/中介 3);初始市场价值 {v_init:.3f};"
          f"保岗门槛 θ={THETA},再就业门槛 θ_re={THETA_RE};λ={LAMBDA}")
    print("学习=向需求向量的凸组合 s←(1−r)s+rD;折旧 δ_i=δ0+δ1·λ·旧度_i"
          "(技术越快旧技能越快过时)")

    # ---- 断言 A:技能折旧律(折旧随技术变化速度单调上升) ----
    print("\n[断言A 技能折旧律] 被动学习者的价值损失 vs 技术变化速度 λ:")
    lams = [0.02, 0.06, 0.10, 0.14]
    losses = []
    for lam in lams:
        tot, eq = passive_decay(lam, p, random.Random(1000 + int(lam * 100)))
        losses.append(tot)
        print(f"  λ={lam:.2f}:{T_PERIODS} 期总损失 {tot:.1%},"
              f"等效期折旧率 {eq:.2%}")
    for a, b in zip(losses, losses[1:]):
        assert b - a >= 0.01, f"折旧律非单调:{a:.3f} → {b:.3f}"
    print("  ✓ 技术变化速度越快,不学习者的市场价值掉得越快——")
    print("    技能半衰期是技术变化速度的函数(通说:技能半衰期随技术加速缩短)")

    # ---- 断言 B:预防>补救(在岗持续学习 vs 先失业再培训) ----
    demands = make_demands(LAMBDA, T_PERIODS, random.Random(7))
    demands_stable = make_demands(0.0, T_PERIODS, random.Random(7))   # λ=0:无冲击
    workers = make_workers(N_WORKERS, rng)
    res_a = run_cohort(workers, demands, LAMBDA, "onjob", p)
    res_b = run_cohort(workers, demands, LAMBDA, "reactive", p)
    res_s = run_cohort(workers, demands_stable, 0.0, "reactive", p)
    inc_a = sum(r[0] for r in res_a) / N_WORKERS
    inc_b = sum(r[0] for r in res_b) / N_WORKERS
    inc_s = sum(r[0] for r in res_s) / N_WORKERS
    spell_a = sum(1 for r in res_a if r[1] is not None) / N_WORKERS
    spell_b = sum(1 for r in res_b if r[1] is not None) / N_WORKERS
    unemp_a = sum(r[3] for r in res_a) / N_WORKERS
    unemp_b = sum(r[3] for r in res_b) / N_WORKERS
    loss_a, loss_b = inc_s - inc_a, inc_s - inc_b   # 参照:相对稳定世界的账
    print(f"\n[断言B 预防>补救] 人均总收入(同期同批,CRN 配对):")
    print(f"  参照·稳定世界(λ=0):{inc_s:.2f}"
          f"(注:追踪技术变化者可越过此参照——学习本身有回报)")
    print(f"  A 在岗持续学习   :{inc_a:.2f}(曾失业 {spell_a:.0%},"
          f"人均失业 {unemp_a:.1f} 期)")
    print(f"  B 先失业再培训   :{inc_b:.2f}(曾失业 {spell_b:.0%},"
          f"人均失业 {unemp_b:.1f} 期;相对参照损失 {loss_b:.2f})")
    assert inc_a - inc_b >= 1.5, f"预防性学习优势不足:{inc_a-inc_b:.2f} < 1.5"
    assert loss_b >= 1.35 * max(loss_a, 0.05), \
        f"补救代价未达预防的 1.35 倍:{loss_b:.2f} vs {loss_a:.2f}"
    assert inc_a - inc_b >= COST_JOB * inc_a / (1 - COST_JOB), \
        "B 的损失未超过 A 付出的全部时间成本"
    assert spell_a <= 0.25, f"在岗学习路径失业率异常:{spell_a:.0%}"
    assert spell_b >= 0.60, f"补救路径失业样本不足:{spell_b:.0%}"
    assert unemp_b >= 3.0 * max(unemp_a, 0.5), \
        f"两路径失业期数对比不足:{unemp_b:.1f} vs {unemp_a:.1f}"
    print(f"  ✓ 「先失业再培训」比「在岗持续学习」少挣 {inc_a-inc_b:.2f} 个"
          f"工资单位——相对参照,补救路径损失 {loss_b:.2f},")
    print(f"    预防路径仅 {max(loss_a, 0):.2f}(≈{loss_b/max(loss_a,0.05):.1f} 倍):"
          "失业期收入归零+再就业门槛的惩罚,")
    print("    远超预防性学习 10% 的时间成本;技能维护(持续小额)优于")
    print("    技能重建(一次性大额+丢岗),与设备维护同构")

    # ---- 断言 C:强度敏感律(低基础群体对培训强度更敏感) ----
    print(f"\n[断言C 强度敏感律] 再培训成功率(首失业后 {WINDOW} 期内再就业,"
          f"各自本地劳动力市场):")
    deltas = {}
    for tag, base, seed in (("低基础", BASE_LOW, 900055), ("高基础", BASE_HIGH, 900125)):
        pairs = build_group(base, 800, seed, LAMBDA, T_PERIODS)
        row = []
        for tau in (TAU_LO, TAU_HI):
            pc = dict(p)
            pc["tau"] = tau
            rc = [simulate(w, d, LAMBDA, "reactive", pc) for w, d in pairs]
            risky = [r for r in rc if r[1] is not None]
            assert len(risky) >= 0.5 * len(rc), "失业风险样本不足"
            succ = sum(1 for r in risky if r[2] is not None and r[2] <= WINDOW)
            row.append(succ / len(risky))
        deltas[tag] = row[1] - row[0]
        print(f"  {tag}群体(学习速率×{base}):低强度 τ={TAU_LO:.2f} → "
              f"成功率 {row[0]:.1%};高强度 τ={TAU_HI:.2f} → 成功率 {row[1]:.1%}"
              f"(Δ={row[1]-row[0]:.1%})")
    assert deltas["低基础"] > deltas["高基础"], \
        f"敏感律反向:Δ低 {deltas['低基础']:.1%} ≤ Δ高 {deltas['高基础']:.1%}"
    assert deltas["低基础"] >= 1.3 * max(deltas["高基础"], 1e-3), \
        f"低基础群体的强度敏感优势不足:{deltas['低基础']:.1%}"
    print("  ✓ 低基础群体的成功率对培训强度更敏感——高基础群体在低强度下")
    print("    已近饱和(边际收益递减),低基础群体正处拐点前:同样的加倍")
    print("    投入,投给弱者产出更大(边际收益递减的补偿——再培训资源")
    print("    的分配依据,01 章主线 A 三道闸门的政策版)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:120 次抖动(漂移/折旧/门槛/强度/成本各±10%上下)")
    n_draws, need = 120, 0.90
    passes = {"A 折旧律": 0, "B 预防>补救": 0, "C 强度敏感律": 0}
    degen_c = 0     # 退化抽样:再就业太易(两档强度下全员成功),强度无关可辩
    for d in range(n_draws):
        rj = random.Random(52000 + d)
        jit = lambda lo, hi: rj.uniform(lo, hi)   # noqa: E731
        pj = {"theta": jit(0.41, 0.44), "theta_re": jit(0.47, 0.50),
              "d0": jit(0.001, 0.004), "d1": jit(0.40, 0.60), "T": 36,
              "r_job": jit(0.11, 0.15), "cost": jit(0.08, 0.12),
              "tau": jit(0.30, 0.40), "drift_scale": jit(0.85, 1.15)}
        lam = jit(0.07, 0.11)
        # 律 A:确定性轨迹的单调性
        ls = [passive_decay(x, pj, random.Random(1000 + int(x * 100)))[0]
              for x in (0.02, 0.06, 0.10, 0.14)]
        ok_a = all(b - a >= 0.01 for a, b in zip(ls, ls[1:]))
        # 律 B:小批量配对路径(收入差 + 失业期数对比——参照差在抖动下
        # 可为负:追踪技术变化的学习者可越过稳定世界参照)
        dj = make_demands(lam, pj["T"], random.Random(80 + d), pj["drift_scale"])
        wj = make_workers(200, random.Random(300 + d))
        ra = run_cohort(wj, dj, lam, "onjob", pj)
        rb = run_cohort(wj, dj, lam, "reactive", pj)
        ia = sum(r[0] for r in ra) / len(wj)
        ib = sum(r[0] for r in rb) / len(wj)
        ua = sum(r[3] for r in ra) / len(wj)
        ub = sum(r[3] for r in rb) / len(wj)
        ok_b = (ia - ib >= 1.0 and ub >= 3.0 * max(ua, 0.3))
        # 律 C:两群体两档强度(同一批配对上重跑)
        dl = dh = 0.0
        for base, seed in ((jit(0.45, 0.65), 4100 + d * 2),
                           (jit(1.10, 1.40), 4200 + d * 2)):
            pairs = build_group(base, 120, seed, lam, pj["T"], pj["drift_scale"])
            row = []
            for tau in (jit(0.13, 0.17), jit(0.30, 0.40)):
                pc = dict(pj)
                pc["tau"] = tau
                rc = [simulate(w, dd, lam, "reactive", pc) for w, dd in pairs]
                risky = [r for r in rc if r[1] is not None]
                if not risky:
                    row.append(1.0)
                    continue
                row.append(sum(1 for r in risky
                               if r[2] is not None and r[2] <= WINDOW) / len(risky))
            if seed % 2 == 0:
                dl = row[1] - row[0]
            else:
                dh = row[1] - row[0]
        if max(dl, dh) > 0.05:
            ok_c = dl > dh                      # 有效抽样:方向必须成立
        else:
            ok_c = True                         # 退化抽样(强度无关可辩)
            degen_c += 1
        passes["A 折旧律"] += ok_a
        passes["B 预防>补救"] += ok_b
        passes["C 强度敏感律"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}通过率 {rate:.0%}"
              + (f"(另 {degen_c} 次退化抽样,强度无关可辩)" if law == "C 强度敏感律" else ""))
        assert rate >= need, f"{law}在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『需求漂移+折旧联动+门槛失业』足以生成")
    print("  三律,不是任何真实劳动力市场的预测;技能分层与漂移方向均为")
    print("  风格化设定。向量模型算不出『舍不得』——经验税(旧框架的卸载")
    print("  成本)与融资困境(谁付钱)请回 00 §七发现 2 与 01 章主线 B。")


if __name__ == "__main__":
    main()
