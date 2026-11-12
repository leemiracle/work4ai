# -*- coding: utf-8 -*-
"""技术采用曲线:三项技术的 logistic 扩散模拟+三组教科书直觉的结构化断言。

00 章 S 形采用骨架 + 04 章 C3(采用曲线走廊)的成品。
罗杰斯(Rogers)扩散理论的感知属性 → 模型参数:
  相对优势(relative advantage)/兼容性(compatibility)/可试用性(trialability)
  内禀增长率 r = 基线 + w1·相对优势 + w2·兼容性 + w3·可试用性
网络效应:增长率乘 (1 + β·渗透率)——价值随用户数增长的技术
  (电话/即时通讯)呈正反馈(休斯系统视角的动力学面)
Retrofit:旧技术存量每年以 ρ 比例"加装新组件"进入延长寿命仓,
  不再可被替代——维护转向的定量面:替代不是替换,是协商

三个教科书直觉的结构化断言:
  ① 相对优势单调律:其他属性不变,到达 50% 渗透率的年份
     对相对优势严格单调递减——"越优越的技术普及越快"的参数面
  ② 网络效应拐点左移:网络参数 β 越大,S 曲线拐点(年增量峰值年)
     在时间轴上严格左移、峰值增量越大——网络技术的正反馈
  ③ Retrofit 现象:老技术可加装新组件延长寿命时,新技术替代曲线
     严格右移(任意年份渗透率被压制、到达 25% 更晚)且最终渗透率
     上限显著下移——旧技术的抵抗力定义新技术的天花板

⚠ 史学纪律(02/04 章):本脚本是零模型(机器化 T6)——参数=史观,
输出的是"若扩散只由这些属性决定,曲线应是什么形状";与史实
对勘的残差才是研究对象,不构成任何实证结论。真实数据接入
须先过 03 章构造合法性三问(实施分离/选样声明/口径快照)。

跑法: python experiments/diffusion_s-curves.py
"""
import random

# ── 感知属性 → 内禀增长率(罗杰斯属性权重的教学值)─────────────────
R_BASE, W_ADV, W_CMP, W_TRY = 0.06, 0.20, 0.08, 0.05


def intrinsic_rate(rel_advantage, compatibility, trialability):
    """罗杰斯三属性 → logistic 内禀增长率 r。"""
    return (R_BASE + W_ADV * rel_advantage + W_CMP * compatibility
            + W_TRY * trialability)


def simulate(rel_advantage, compatibility, trialability,
             network=0.0, retrofit_rate=0.0,
             years=100, x0=0.01, noise=0.05, seed=0):
    """三仓采用模拟(质量守恒:N+O+R=1)。

    N=新技术采用者 / O=旧技术存量 / R=加装新组件的延长寿命仓
    每年两条流(均带 ±noise 随机扰动,固定种子可复现):
      conv(旧→新)    = r·N·O·(1+β·N)   口碑扩散+网络效应
      retrofit(旧→R) = ρ·O             旧技术续命(维护转向)
    """
    rng = random.Random(20260907 + seed)
    r = intrinsic_rate(rel_advantage, compatibility, trialability)
    n_pop, o_pop, r_pop = x0, 1.0 - x0, 0.0
    series, gains = [n_pop], []
    for _t in range(1, years + 1):
        conv = max(0.0, r * n_pop * o_pop * (1.0 + network * n_pop)
                   * (1.0 + rng.uniform(-noise, noise)))
        retro = max(0.0, retrofit_rate * o_pop
                    * (1.0 + rng.uniform(-noise, noise)))
        if conv + retro > o_pop:                  # 存量封顶:不无中生有
            scale = o_pop / (conv + retro)
            conv, retro = conv * scale, retro * scale
        n_pop, o_pop, r_pop = (n_pop + conv, o_pop - conv - retro,
                               r_pop + retro)
        series.append(n_pop)
        gains.append(conv)

    def first_year(threshold):
        for t, n in enumerate(series):
            if n >= threshold:
                return t
        return None                                # 视界内未到达

    peak = max(range(len(gains)), key=lambda i: gains[i])
    return dict(series=series, gains=gains,
                t50=first_year(0.5), t25=first_year(0.25),
                t_inf=peak, peak_gain=gains[peak],
                final_new=n_pop, final_old=o_pop, final_retro=r_pop)


# ── 三项演示技术(参数为教学值;真实研究须以 03 章 schema 换实证参数)──
TECHS = [
    dict(name="智能电表(无网络效应)", rel_adv=0.7, compat=0.6,
         trial=0.5, network=0.0, retrofit=0.0, seed=11),
    dict(name="即时通讯(网络效应 β=6)", rel_adv=0.5, compat=0.8,
         trial=0.6, network=6.0, retrofit=0.0, seed=22),
    dict(name="电动车(燃油车可改装 ρ=0.04)", rel_adv=0.8, compat=0.5,
         trial=0.4, network=0.0, retrofit=0.04, seed=33),
]


def main():
    print("=" * 76)
    print("技术采用曲线:三仓 logistic 扩散(相对优势/兼容性/可试用性参数化)")
    print("=" * 76)

    # ── 主表:三技术渗透率十年快照 ─────────────────────────────
    runs = []
    for i, t in enumerate(TECHS):
        run = simulate(t["rel_adv"], t["compat"], t["trial"],
                       network=t["network"], retrofit_rate=t["retrofit"],
                       seed=t["seed"])
        runs.append((t, run))
        print(f"\n[{i + 1}] {t['name']}")
        row = "  年份:" + "".join(f"{y:>7}" for y in range(0, 101, 10))
        print(row)
        print("  渗透:" + "".join(f"{run['series'][y]:>7.2f}"
                                   for y in range(0, 101, 10)))
        print(f"  拐点年={run['t_inf']}(峰值年增量 {run['peak_gain']:.3f});"
              f"期末:新技术 {run['final_new']:.2f} / 存量旧技术 "
              f"{run['final_old']:.2f} / 加装续命 {run['final_retro']:.2f}")

    # ── 断言 1:相对优势单调律(采用速度对相对优势严格单调)────────
    ladder = [0.2, 0.5, 0.8, 1.0]
    t50s = [simulate(ra, 0.5, 0.5, seed=100 + i)["t50"]
            for i, ra in enumerate(ladder)]
    assert all(x is not None for x in t50s), "教学参数下视界内应全部过半"
    assert all(a > b for a, b in zip(t50s, t50s[1:])), \
        "到达50%年份应对相对优势严格递减(每档间隔应远超噪声)"
    print("\n" + "=" * 76)
    print(f"断言 1 通过:相对优势 {ladder} → 到达50%年份 {t50s} 严格递减 ✓")
    print("            ——采用速度对相对优势单调;'更优越'是扩散的"
          "第一杠杆(罗杰斯属性论的参数面)")

    # ── 断言 2:网络效应拐点左移(β 越大拐点越早、峰值增量越大)────
    betas = [0.0, 5.0, 15.0]
    net_runs = [simulate(0.5, 0.8, 0.6, network=b, seed=200 + i)
                for i, b in enumerate(betas)]
    infs = [run["t_inf"] for run in net_runs]
    peaks = [run["peak_gain"] for run in net_runs]
    assert all(a > b for a, b in zip(infs, infs[1:])), \
        "拐点年应随网络参数严格左移"
    assert all(a < b for a, b in zip(peaks, peaks[1:])), \
        "峰值年增量应随网络参数严格增大"
    assert infs[0] > infs[-1] + 3, "无网络 vs 强网络拐点应差数年以上"
    print(f"断言 2 通过:β {betas} → 拐点年 {infs} 严格左移,"
          f"峰值增量 {[round(p, 3) for p in peaks]} 严格增大 ✓")
    print("            ——网络技术的正反馈把 S 拧陡拧早:"
          "电话比冰箱普及得凶猛的动力学原因")

    # ── 断言 3:Retrofit 现象(替代曲线右移且上限下移)──────────────
    base = simulate(0.8, 0.5, 0.4, seed=301)             # 燃油车不可改装
    retro = simulate(0.8, 0.5, 0.4, retrofit_rate=0.04, seed=302)
    assert retro["t25"] > base["t25"] + 5, \
        "retrofit 应使到达25%渗透率显著推迟(右移)"
    for y in (20, 40, 60, 80, 100):                       # 逐年代压制检验
        assert retro["series"][y] <= base["series"][y] + 0.05, \
            f"第 {y} 年:可改装世界的新技术渗透率应被压制"
    assert retro["final_new"] < base["final_new"] - 0.3, \
        "retrofit 应显著下移最终渗透率上限"
    assert retro["final_retro"] > 0.3, "应有可观存量进入加装续命仓"
    for run in (base, retro):                             # 质量守恒自检
        total = run["final_new"] + run["final_old"] + run["final_retro"]
        assert abs(total - 1.0) < 1e-9, "三仓质量守恒被破坏"
    print(f"断言 3 通过:到达25%年份 {base['t25']} → {retro['t25']}"
          f"(右移);期末上限 {base['final_new']:.2f} → "
          f"{retro['final_new']:.2f}(下移);续命仓 "
          f"{retro['final_retro']:.2f} ✓")
    print("            ——旧技术加装新组件=从存量里划走不可替代份额:"
          "替代不是替换,是协商(维护转向的定量面)")

    # ── 断言 4:S 形自检(无网络技术年增量应先升后降)───────────────
    plain = runs[0][1]
    g, k = plain["gains"], plain["t_inf"]
    assert 5 < k < 40, "普通技术的拐点应在中期"
    assert g[k] > g[0] and g[k] > g[-1], "年增量应先升后降(S 形)"
    assert plain["t50"] is not None and plain["t50"] >= k, \
        "50% 到达年不应早于峰值年增量年(离散年步下拐点含过半跨越)"
    print(f"断言 4 通过:智能电表年增量先升后降(拐点年 {k},"
          f"50% 到达年 {plain['t50']})——教科书 S 形成立 ✓")

    print("\n" + "=" * 76)
    print("四组断言全部通过:相对优势单调 / 网络效应拐点左移 / "
          "Retrofit 右移且上限下移 / S 形自检 ✓")
    print("\n⚠ 史学纪律提醒:本脚本是零模型(机器化 T6)——参数=史观;"
          "相对优势谁定、β 与 ρ 取多少,都是'相关社会群体'的历史判断。")
    print("  与史实曲线对勘、看残差落在哪个参数上,才是它作为研究工具"
          "的正确用法(04 章 §7)。")


if __name__ == "__main__":
    main()
