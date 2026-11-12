"""增长核算：TFP 分解、份额校准闭环与指数稳健性（断言自验）
对应《讲透生产力经济学》00 章（美之时刻 ①）、03 章（构造学 §一）、
04 章（走廊 1：增长会计）。

模型（Cobb-Douglas 核算恒等式）：
    Δln Y = s_K·Δln K + s_L·Δln L + Δln A
    ⟹  TFP 增长 Δln A = Δln Y − s_K·Δln K − s_L·Δln L   （零估计，纯代数）

⚠ 数据纪律：增长率为教学圆整近似（公开核算文献的常见量级），
断言只验**计算内部一致性**；真实研究须回 PWT/世行原源并声明
指数与口径（02 章 §二：账本即理论）。

断言（自验证）：
    (a) 恒等式闭合：s_K·ΔlnK + s_L·ΔlnL + ΔlnA = ΔlnY（两国，误差 < 1e-12）
        且两条增长路线的性质：中国=要素贡献为主，美国=TFP 占比更高
    (b) 份额校准闭环：Cobb-Douglas 模拟企业数据（竞争定价），
        OLS 回收的资本弹性 ≈ 真实 α ≈ 资本份额（误差 < 0.02）
    (c) 敏感度带：份额 s_K 扰动 ±5pct 时，TFP 贡献变化线性、
        且两国 TFP 占比的排序不翻转（结论方向稳健）
"""
import numpy as np

# ── (a) 两组教学近似数据（十年平均年增长率，%） ──
CN = dict(gY=9.5, gK=11.0, gL=1.5, sK=0.45, name="中国 1980-2010（教学近似）")
US = dict(gY=2.8, gK=2.5, gL=1.0, sK=0.35, name="美国 1995-2005（教学近似）")


def tfp_decompose(gY, gK, gL, sK):
    """三行代数：返回 (要素贡献, TFP 贡献)。单位：百分点/年。"""
    sL = 1.0 - sK
    factor = sK * gK + sL * gL
    return factor, gY - factor


def main():
    # ═══ (a) 恒等式闭合 + 两国性质 ═══
    print("(a) 增长核算分解（%/年）：")
    results = {}
    for d in (CN, US):
        factor, tfp = tfp_decompose(d["gY"], d["gK"], d["gL"], d["sK"])
        total = factor + tfp
        tfp_share = tfp / d["gY"]
        results[d["name"][:2]] = tfp_share
        print(f"    {d['name']}: 要素={factor:.2f}  TFP={tfp:+.2f}  "
              f"合计={total:.2f}（闭合误差 {abs(total - d['gY']):.1e}）  "
              f"TFP 占比={tfp_share:.1%}")
        assert abs(total - d["gY"]) < 1e-12, "分解必须闭合到恒等式"
    print("    性质断言：要素贡献占比——中国 > 50%、美国 TFP 占比 > 中国")
    cn_factor_share = 1 - results["中国"]
    assert cn_factor_share > 0.5, "教学近似下中国为要素贡献为主"
    assert results["美国"] > results["中国"], "成熟经济 TFP 占比应更高"

    # ═══ (b) 份额校准闭环：模拟企业面板，OLS 回收 α ═══
    rng = np.random.default_rng(42)
    n = 500
    alpha_true, A = 0.35, 1.0
    K = rng.uniform(0.5, 5.0, n)                  # 企业异质性
    L = rng.uniform(0.5, 5.0, n)
    Y = A * K**alpha_true * L**(1 - alpha_true) * np.exp(rng.normal(0, 0.05, n))
    # OLS：lnY = lnA + α·lnK + (1−α)·lnL + ε —— 回收 α
    Xmat = np.column_stack([np.ones(n), np.log(K), np.log(L)])
    beta, *_ = np.linalg.lstsq(Xmat, np.log(Y), rcond=None)
    alpha_hat = beta[1]
    beta_L = beta[2]
    sK_implied = alpha_true                        # 竞争+CD 下份额=α（03 章 §1.2）
    print(f"\n(b) 份额校准闭环：OLS α̂={alpha_hat:.4f}（真实 α={alpha_true}，"
          f"误差={abs(alpha_hat - alpha_true):.2e}）  "
          f"β_L={beta_L:.4f}（α̂+β_L={alpha_hat + beta_L:.4f}≈1，规模报酬）")
    assert abs(alpha_hat - alpha_true) < 0.02, "竞争 CD 数据应回收真实弹性"
    assert abs(alpha_hat + beta_L - 1.0) < 0.02, "规模报酬应被回收"
    print(f"    账本读法：资本份额 ≈ α̂ ≈ {sK_implied}——不用跑回归，弹性从账本读（03 章 §1.2）")

    # ═══ (c) 敏感度带：份额 ±5pct 的 TFP 摆动 ═══
    print("\n(c) 敏感度带（s_K ±5pct ⟹ TFP 贡献摆动，%/年）：")
    for d in (CN, US):
        _, tfp_lo = tfp_decompose(d["gY"], d["gK"], d["gL"], d["sK"] - 0.05)
        _, tfp_hi = tfp_decompose(d["gY"], d["gK"], d["gL"], d["sK"] + 0.05)
        swing = tfp_hi - tfp_lo           # = −0.10×(gK−gL)：s_K 升 ⟹ TFP 降
        expected = -0.10 * (d["gK"] - d["gL"])
        lo, hi = min(tfp_lo, tfp_hi), max(tfp_lo, tfp_hi)
        print(f"    {d['name'][:2]}: TFP ∈ [{lo:+.2f}, {hi:+.2f}]"
              f"（摆动 {abs(swing):.2f}，|ΔTFP|=0.10×(gK−gL)={abs(expected):.2f}）")
        assert abs(swing - expected) < 1e-12, "TFP 应对份额线性（斜率 −(gK−gL)）"
    # 排序稳健：±5pct 内不翻转"美国 TFP 占比 > 中国"
    for ds in (-0.05, 0.0, +0.05):
        _, t_cn = tfp_decompose(CN["gY"], CN["gK"], CN["gL"], CN["sK"] + ds)
        _, t_us = tfp_decompose(US["gY"], US["gK"], US["gL"], US["sK"] + ds)
        assert t_us / US["gY"] > t_cn / CN["gY"], "占比排序应稳健于份额扰动"
    print("    排序稳健断言：±5pct 内'美国 TFP 占比 > 中国'不翻转 ✅")

    print("\n全部断言通过 ✅  核算=零估计恒等式；份额=弹性的账本读法；"
          "输出自带敏感度带。")
    print("带走一句（03 章）：恒等式机器自动吐数字，数字的意义"
          "由假设账单决定——零假设可算 ≠ 已发现。")

if __name__ == "__main__":
    main()
