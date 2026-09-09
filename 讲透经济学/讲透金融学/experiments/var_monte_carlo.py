"""风险价值 VaR 三法对比：参数法在厚尾面前低估尾部（断言自验）
对应《讲透金融学》02 章（Q 世界/P 世界）、04 章（走廊 2：风险走廊）。

方法（单资产 1 日 VaR，损失 L=−r）：
    历史模拟：经验分位数
    参数法：   正态假设  VaR = −(μ̂ + z_α·σ̂)，z_0.99≈2.326
    蒙特卡洛： 显式模拟收益分布（正态冲击 / 标准化 t(4) 厚尾冲击）

断言（自验证）：
    (a) 单调性：99% VaR > 95% VaR（历史法）
    (b) 校准：正态冲击的 MC-VaR99 与参数法解析值相对偏差 < 3%
    (c) 厚尾教训：t(4) 冲击下，参数法（用样本 σ̂ 的正态公式）系统性
        低估 MC-VaR 至少 5% —— 1998 LTCM / 2008 教训的最小复现
"""
import math
import random

MU, SIG, SEED = 0.0002, 0.01, 42        # 日均收益 / 日波动率
Z95, Z99 = 1.645, 2.326                 # 标准正态分位数
N_MC, N_HIST = 400_000, 20_000
rng = random.Random(SEED)


def t_std4(rng):
    """单位方差标准化 t(4)：t = Z0/√((ΣZi²)/4)，再乘 √((ν−2)/ν)=√0.5。"""
    num = rng.gauss(0.0, 1.0)
    den = math.sqrt(sum(rng.gauss(0.0, 1.0) ** 2 for _ in range(4)) / 4.0)
    return (num / den) * math.sqrt(0.5)


def quantile(sorted_vals, a):
    """经验下 α 分位（线性插值）。"""
    pos = a * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def var_historical(alpha):
    rets = sorted(rng.gauss(MU, SIG) for _ in range(N_HIST))
    return -quantile(rets, 1 - alpha)                     # 损失分位


def var_mc(alpha, tail="normal"):
    draw = (lambda: rng.gauss(0.0, 1.0)) if tail == "normal" else (lambda: t_std4(rng))
    rets = sorted(MU + SIG * draw() for _ in range(N_MC))
    return -quantile(rets, 1 - alpha)


def var_param(alpha, sigma=SIG):
    return -(MU - Z(alpha) * sigma)


def Z(alpha):
    return {0.95: Z95, 0.99: Z99}[alpha]


def main():
    # ── (a) 单调性：置信水平越高 VaR 越大 ──
    v95, v99 = var_historical(0.95), var_historical(0.99)
    print(f"(a) 历史法：VaR95={v95*100:.3f}%  VaR99={v99*100:.3f}%   "
          f"(断言 VaR99 > VaR95)")
    assert v99 > v95, "99% VaR 必须大于 95% VaR"

    # ── (b) 正态冲击下 MC ≈ 参数法解析值 ──
    v_mc = var_mc(0.99, "normal")
    v_par = var_param(0.99)
    rel = abs(v_mc - v_par) / v_par
    print(f"(b) 正态冲击：MC={v_mc*100:.3f}%  参数法={v_par*100:.3f}%  "
          f"相对偏差={rel*100:.2f}%   (断言 < 3%)")
    assert rel < 0.03, "同分布下蒙特卡洛应收敛到参数解析值"

    # ── (c) 厚尾：参数法低估尾部 ──
    # 做法：真实世界是 t(4)（肥尾），但风控用"样本σ̂+正态公式"——看错多少
    sample = [MU + SIG * t_std4(rng) for _ in range(N_HIST)]
    sigma_hat = math.sqrt(sum((x - MU) ** 2 for x in sample) / len(sample))
    v_par_wrong = var_param(0.99, sigma_hat)              # 参数法（正态公式+样本σ）
    v_mc_fat = var_mc(0.99, "t")                          # 真实厚尾分位
    under = (v_mc_fat - v_par_wrong) / v_mc_fat
    print(f"(c) 厚尾(t4)：MC真值={v_mc_fat*100:.3f}%  参数法={v_par_wrong*100:.3f}%  "
          f"低估={under*100:.1f}%   (断言 ≥ 5%)")
    assert under >= 0.05, "正态参数法在 t(4) 冲击下应系统性低估 99% VaR"

    print("\n全部断言通过 ✅  VaR：分位数不难算，难的是分布假设——")
    print("参数法把'不知道分布'偷换成'正态分布'，平时省事，危机时刻集体失明")
    print("（这正是监管改用 ES + 多情景压力测试的原因，04 章走廊 2）。")

if __name__ == "__main__":
    main()
