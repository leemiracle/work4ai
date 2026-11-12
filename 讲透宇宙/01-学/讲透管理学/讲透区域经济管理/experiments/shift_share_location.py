# -*- coding: utf-8 -*-
"""区位熵 + 转移份额分解 + 古德哈特区域版(名义集聚)。

00 章 §七(反直觉)、02 章 §二(区域数据的识别问题)、04 章走廊 1/2 配套实验。纯标准库。

设定: 两个研究区域(A/B)× 两个部门(制造 m/服务 s),外加一个大的「域外」块锚定
     全国基准——转移份额分解的天平必须外生,不能让被评估区域自己污染砝码
     (域外就业约为研究区域的 34 倍,污染 <0.5pp)。
     区域 A 的制造业注入真实竞争优势 α=+6pp(增长比全国同行业快 6 个百分点),
     其余区域-部门按全国行业速度增长(叠加 σ=0.3pp 的高斯噪声模拟统计毛刺)。
对照: 区位熵层: LQ_{r,s}=(E_{r,s}/E_r)/(E_{n,s}/E_n),>1.25 判集聚(常用参考线)。
         断言 LQ 正确识别 A 的集聚部门=制造业,其余三格不误报。
     分解层: ΔE_{r,s}=NS+IM+RS 代数恒等(全国增长/行业结构/区域竞争,零残差);
         受控数据下 RS/E0 还原注入的 α(真实竞争优势),未注入处 ≈0;
         全国加总 ΣRS=0——竞争效应是零和的影子。
     古德哈特层: 区位熵(注册口径)一旦成为考核指标,B 地诱导 40 家制造企业
         「注册地迁移」(名义就业 +800,无真实活动):注册口径 LQ 虚高越过集聚线,
         就业口径与税收口径纹丝不动;且全国底数被污染,A 的真实集聚读数被反向稀释
         ——断言就业/税收双口径交叉验证才能识破。
场景: t0→t1 一期增长;注册迁移发生在 t1 之后(考核前夜)。

跑法: python experiments/shift_share_location.py
"""

import random

SECTORS = ("m", "s")                     # m=制造业, s=服务业
SECTOR_NAME = {"m": "制造", "s": "服务"}
REGIONS = ("A", "B", "O")                # O=域外(全国其他,只当天平砝码)
ALPHA = {"A": {"m": 0.06, "s": 0.0},     # 注入的真实竞争优势:A 制造业 +6pp
         "B": {"m": 0.0, "s": 0.0},
         "O": {"m": 0.0, "s": 0.0}}
G_NAT = {"m": 0.20, "s": 0.04}           # 全国行业增长目标(域外按此精确增长)


def tot(reg, emp):
    return sum(emp[reg][s] for s in SECTORS)


def nat(emp, sec):
    return sum(emp[r][sec] for r in REGIONS)


def location_quotient(emp, r, s):
    """LQ_{r,s}=(E_{r,s}/E_r)/(E_{n,s}/E_n)——区域的部门结构对着全国的镜子照。"""
    share_reg = emp[r][s] / tot(r, emp)
    share_nat = nat(emp, s) / sum(tot(r, emp) for r in REGIONS)
    return share_reg / share_nat


# ---------- Part 1: t0 区位熵——集聚部门识别 ----------
def part1_lq(emp0):
    print("=" * 66)
    print("Part 1 区位熵(t0):LQ=(区域部门份额)/(全国部门份额),>1.25 判集聚")
    print("=" * 66)
    rows = []
    print(f"{'区域':>4} | {'部门':>4} | {'就业':>8} | {'LQ':>7} | 判定")
    for r in ("A", "B"):
        for s in SECTORS:
            q = location_quotient(emp0, r, s)
            verdict = "集聚 ●" if q > 1.25 else "—"
            rows.append((r, s, q, verdict))
            print(f"{r:>4} | {SECTOR_NAME[s]:>4} | {emp0[r][s]:8.1f} | {q:7.3f} | {verdict}")
    print("  (域外 O 只当天平砝码不参评;真实优势只注入了 A×制造一格)")
    return rows


# ---------- Part 2: t0→t1 增长 + 转移份额三效应分解 ----------
def grow(emp0, sigma, rng):
    """按 全国行业速度+区域优势+噪声 生成 t1 就业(浮点,不做取整——取整在小基数上是二次噪声)。"""
    emp1 = {}
    for r in REGIONS:
        emp1[r] = {}
        for s in SECTORS:
            eps = 0.0 if r == "O" else rng.gauss(0.0, sigma)   # 域外精确锚定
            g = G_NAT[s] + ALPHA[r][s] + eps
            emp1[r][s] = emp0[r][s] * (1.0 + g)
    return emp1


def shift_share(emp0, emp1):
    """Dunn 式三效应:ΔE = NS(全国增长)+IM(行业结构)+RS(区域竞争)。返回逐格分解。"""
    g_n = sum(tot(r, emp1) for r in REGIONS) / sum(tot(r, emp0) for r in REGIONS) - 1.0
    out = {}
    for r in REGIONS:
        for s in SECTORS:
            e0 = emp0[r][s]
            g_rs = emp1[r][s] / e0 - 1.0                       # 区域-部门实际增速
            g_ns = nat(emp1, s) / nat(emp0, s) - 1.0           # 全国行业增速(含域外)
            ns, im = e0 * g_n, e0 * (g_ns - g_n)
            rs = e0 * (g_rs - g_ns)
            out[(r, s)] = {"dE": emp1[r][s] - e0, "NS": ns, "IM": im, "RS": rs,
                           "g_rs": g_rs, "g_ns": g_ns}
    return out, g_n


def part2_shift_share(emp0, emp1):
    print()
    print("=" * 66)
    print("Part 2 转移份额分解(t0→t1):ΔE = 全国增长NS + 行业结构IM + 区域竞争RS")
    print("=" * 66)
    dec, g_n = shift_share(emp0, emp1)
    print(f"全国总增速 g_n={g_n:.4f};全国行业增速 g_ns: 制造 "
          f"{dec[('A','m')]['g_ns']:.4f} / 服务 {dec[('A','s')]['g_ns']:.4f}")
    print(f"{'格子':>6} | {'ΔE':>8} | {'NS':>8} | {'IM':>8} | {'RS':>8} | RS/E0(还原优势)")
    for r in ("A", "B"):
        for s in SECTORS:
            d = dec[(r, s)]
            print(f"{r}×{SECTOR_NAME[s]:>2} | {d['dE']:8.2f} | {d['NS']:8.2f} | "
                  f"{d['IM']:8.2f} | {d['RS']:8.2f} | {d['RS'] / emp0[r][s]:+9.4f}")
    return dec


# ---------- Part 3: 古德哈特区域版——名义集聚与双口径识破 ----------
def part3_goodhart(emp1, rng):
    print()
    print("=" * 66)
    print("Part 3 古德哈特区域版:区位熵(注册口径)成为考核指标之后")
    print("=" * 66)
    # 就业口径=真实活动;税收口径=真实产出代理(同税率×就业+小噪声)
    emp_tax = {r: {s: emp1[r][s] * (1.0 + rng.gauss(0.0, 0.01)) for s in SECTORS}
               for r in ("A", "B")}
    emp_tax["O"] = {s: emp1["O"][s] for s in SECTORS}
    # B 地动员 40 家制造企业注册地迁移:名义就业 +800,无真实就业、无真实税收
    MIG_FIRMS, FIRM_SIZE = 40, 20.0
    phantom = MIG_FIRMS * FIRM_SIZE
    emp_reg = {r: dict(emp1[r]) for r in REGIONS}
    emp_reg["B"]["m"] += phantom
    emp_tax_reg = {r: dict(emp_tax[r]) for r in REGIONS}
    emp_tax_reg["B"]["m"] += phantom * 0.02          # 迁移企业只在注册地留一点税点

    q_emp = location_quotient(emp1, "B", "m")        # 就业口径(真)
    q_tax = location_quotient(emp_tax, "B", "m")     # 税收口径(真)
    q_reg = location_quotient(emp_reg, "B", "m")     # 注册口径(虚)
    q_A_emp = location_quotient(emp1, "A", "m")      # 邻区 A:就业口径
    q_A_reg = location_quotient(emp_reg, "A", "m")   # 邻区 A:注册口径(被反向稀释)

    print(f"真实优势在 A×制造,B×制造本无优势(就业口径 LQ={q_emp:.3f})")
    print(f"B 地诱导 {MIG_FIRMS} 家制造企业注册地迁移(名义就业 +{phantom:.0f},无真实活动):")
    print(f"{'口径':>6} | {'B×制造 LQ':>10} | 过集聚线(1.25)?")
    print(f"{'就业':>6} | {q_emp:10.3f} | {'是' if q_emp > 1.25 else '否(真实)'}")
    print(f"{'税收':>6} | {q_tax:10.3f} | {'是' if q_tax > 1.25 else '否(真实)'}")
    print(f"{'注册':>6} | {q_reg:10.3f} | {'是——名义集聚' if q_reg > 1.25 else '否'}")
    print(f"邻区 A×制造:就业口径 LQ={q_A_emp:.3f} → 注册口径 {q_A_reg:.3f}"
          f"(全国底数被污染,真实集聚读数被反向稀释)")
    return {"emp": q_emp, "tax": q_tax, "reg": q_reg,
            "A_emp": q_A_emp, "A_reg": q_A_reg, "phantom": phantom}


def main():
    rng = random.Random(20260907)
    emp0 = {"A": {"m": 28.0, "s": 12.0},             # A: 制造占比 70%(真集聚)
            "B": {"m": 10.0, "s": 30.0},             # B: 均衡平庸型
            "O": {"m": 900.0, "s": 1800.0}}          # 域外:全国其他(天平砝码)
    sigma = 0.003                                     # 0.3pp 统计毛刺

    lq_rows = part1_lq(emp0)
    emp1 = grow(emp0, sigma, rng)
    dec = part2_shift_share(emp0, emp1)
    g = part3_goodhart(emp1, rng)

    print()
    print("读数:")
    print("  · Part 1:LQ 一眼锁定 A×制造(2.0+),其余三格都在 1.25 线下——")
    print("    区域语言的第一句话不是『哪个区域强』,是『哪个区域×哪个部门强』。")
    print("  · Part 2:B×服务 ΔE 几乎全是 NS+IM(吃了全国服务增长的大势),RS≈0;")
    print("    A×制造多出的那截才是『本事』——总量排名会说谎,分解才开口说话。")
    print(f"  · Part 3:注册口径把 B×制造 LQ 从 {g['emp']:.2f} 抬到 {g['reg']:.2f},"
          f"越过集聚线;就业/税收双口径交叉一比即穿帮——")
    print("    单口径考核必然被口径本身博弈(古德哈特区域版),而且污染全国底数、")
    print("    反向稀释邻区 A 的真实集聚读数:指标体系错一处,全图跟着歪。")

    # ---------- 自验证断言 ----------
    # Part 1:区位熵正确识别集聚部门,无误报
    q = {(r, s): v for r, s, v, _ in lq_rows}
    assert max(q, key=q.get) == ("A", "m"), "LQ 应把 A×制造识别为最强集聚格"
    assert q[("A", "m")] > 1.25, "A×制造 LQ 应越过集聚线"
    assert all(q[k] < 1.25 for k in q if k != ("A", "m")), "其余三格不应误报集聚"

    # Part 2:恒等式零残差;RS 还原注入优势;未注入处≈0;全国竞争效应加总为零
    for r in ("A", "B"):
        for s in SECTORS:
            d = dec[(r, s)]
            assert abs(d["dE"] - (d["NS"] + d["IM"] + d["RS"])) < 1e-6, \
                "ΔE=NS+IM+RS 应为代数恒等(零残差)"
    for r in ("A", "B"):
        for s in SECTORS:
            rs_unit = dec[(r, s)]["RS"] / emp0[r][s]
            if (r, s) == ("A", "m"):
                assert abs(rs_unit - ALPHA["A"]["m"]) < 0.012, \
                    f"RS 应还原注入的真实竞争优势(实测 {rs_unit:.4f} vs {ALPHA['A']['m']})"
            else:
                assert abs(rs_unit) < 0.012, \
                    f"未注入优势处 RS 应≈0({r}×{s} 实测 {rs_unit:+.4f})"
    assert dec[("A", "m")]["RS"] > max(dec[k]["RS"] for k in dec
                                       if k != ("A", "m")), "A×制造竞争效应应为全场最大"
    sum_rs = sum(dec[(r, s)]["RS"] for r in REGIONS for s in SECTORS)
    assert abs(sum_rs) < 1e-6, "全国加总 ΣRS 应为零(竞争效应是零和的影子)"
    assert dec[("B", "s")]["NS"] + dec[("B", "s")]["IM"] > dec[("B", "s")]["RS"] * 5, \
        "B×服务的增长应主要由大势与结构解释,而非本地竞争"

    # Part 3:注册口径虚高;就业/税收双口径一致且真实;交叉验证识破;邻区被反向稀释
    assert g["reg"] > 1.25, "注册口径 LQ 应虚高越过集聚线(名义集聚)"
    assert g["emp"] < 0.9 and g["tax"] < 0.9, "就业/税收口径应还原真实(无集聚)"
    assert abs(g["tax"] - g["emp"]) < 0.08, "两个真实口径之间应一致(税收≈就业)"
    assert g["reg"] - g["emp"] > 0.8, "注册口径相对就业口径应大幅虚高"
    assert g["reg"] / g["emp"] > 1.8, "口径比值交叉验证应显著报警"
    assert g["A_reg"] < g["A_emp"] - 0.3, "全国底数被污染应反向稀释邻区真实集聚读数"

    print()
    print("ALL ASSERTS PASSED ✓")


if __name__ == "__main__":
    main()
