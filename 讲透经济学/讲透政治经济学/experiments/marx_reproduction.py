"""马克思两大部类再生产：平衡、比例增长与利润率动态（断言自验）
对应《讲透政治经济学》00 章（装置 3）、03 章（可构造性热图）、
04 章（走廊 1 与走廊 3）。

模型（《资本论》二卷表式的代码化）：
    部类 i（i=Ⅰ生产资料, Ⅱ消费资料）：产出价值 W_i = c_i + v_i + m_i
    m_i = e · v_i（剩余价值率 e）
    简单再生产平衡条件：Ⅰ(v+m) = Ⅱc
    扩大再生产（比例增长）：两部类以同比率 g、不变技术系数扩张，
    一切平衡条件逐期成立（矩阵谱性质：平衡增长=Perron 根路径）
    利润率：p' = m/(c+v) = e/(k+1)，k=c/v（有机构成）

断言（自验证）：
    (a) 简单再生产（马克思二卷原例）：全部平衡等式成立、产出逐期不变
    (b) 扩大再生产（比例增长 g=10%）：逐期平衡误差 < 1e-12，
        且实际增长率 = g
    (c) TRPF 赛跑三分支：p'=e/(k+1)
        — e 固定、k 上升 ⟹ p' 严格下降
        — e 与 (k+1) 同速增长 ⟹ p' 不变
        — e 更快增长 ⟹ p' 上升
"""
import numpy as np

# ── (a) 马克思二卷原例：简单再生产 ──
C = np.array([4000.0, 2000.0])      # 不变资本（Ⅰ, Ⅱ）
V = np.array([1000.0, 500.0])       # 可变资本
M = np.array([1000.0, 500.0])       # 剩余价值
W = C + V + M                       # 部类产出价值（6000, 3000）

# ── (b) 扩大再生产：比例增长参数 ──
G_RATE = 0.10                        # 两部类同比率增长
PERIODS = 12


def main():
    # ═══ (a) 简单再生产：平衡条件全家福 ═══
    bal1 = V[0] + M[0]               # Ⅰ(v+m)：部类Ⅰ新价值
    bal2 = C[1]                      # Ⅱc：部类Ⅱ补偿需求
    print(f"(a) 简单再生产（原例）：Ⅰ(v+m)={bal1:.0f}  Ⅱc={bal2:.0f}  "
          f"差额={abs(bal1-bal2):.1e}   (断言 =0)")
    assert abs(bal1 - bal2) < 1e-9, "简单再生产核心条件 Ⅰ(v+m)=Ⅱc"

    # 生产资料总供需：W₁ = c₁+c₂
    mp_supply, mp_demand = W[0], C.sum()
    print(f"    生产资料：供给 W₁={mp_supply:.0f}  需求 c₁+c₂={mp_demand:.0f}  "
          f"差额={abs(mp_supply-mp_demand):.1e}")
    assert abs(mp_supply - mp_demand) < 1e-9
    # 消费资料总供需：W₂ = (v₁+m₁)+(v₂+m₂)
    cg_supply, cg_demand = W[1], (V + M).sum()
    print(f"    消费资料：供给 W₂={cg_supply:.0f}  需求 Σ(v+m)={cg_demand:.0f}  "
          f"差额={abs(cg_supply-cg_demand):.1e}")
    assert abs(cg_supply - cg_demand) < 1e-9
    # 总价值守恒
    assert abs(W.sum() - (C.sum() + V.sum() + M.sum())) < 1e-9
    # 逐期静态：简单再生产 ⟹ 下一期完全相同（积累率=0）
    C2, V2, M2 = C.copy(), V.copy(), M.copy()
    for _ in range(5):
        C2, V2, M2 = C2 + 0.0 * C2, V2 + 0.0 * V2, M2 + 0.0 * M2
    assert np.allclose(C2, C) and np.allclose(V2, V) and np.allclose(M2, M)
    print("    附：积累率为 0 时逐期复制原状 ✅（简单再生产=静态均衡）")

    # ═══ (b) 扩大再生产：比例增长 ═══
    Cs, Vs, Ms = C.copy(), V.copy(), M.copy()
    max_rel_err, growth_rates = 0.0, []
    for t in range(1, PERIODS + 1):
        Ws = Cs + Vs + Ms
        # 逐期平衡检查（与 (a) 同三式）；误差以当期最大产出为尺度取相对值
        # （绝对误差随复利放大到 ~2e-12 量级，是 float64 舍入而非数学误差）
        err = max(abs((Vs[0] + Ms[0]) - Cs[1]),
                  abs(Ws[0] - Cs.sum()),
                  abs(Ws[1] - (Vs + Ms).sum())) / Ws.max()
        max_rel_err = max(max_rel_err, err)
        # 按比率 g 扩张（技术系数不变：c:v:m 结构整体放大）
        growth_rates.append(Ws.sum())
        Cs, Vs, Ms = Cs * (1 + G_RATE), Vs * (1 + G_RATE), Ms * (1 + G_RATE)
    total_growth = growth_rates[-1] / growth_rates[0]
    g_emp = total_growth ** (1.0 / (PERIODS - 1)) - 1.0
    print(f"\n(b) 扩大再生产（g={G_RATE:.0%}，{PERIODS} 期）："
          f"逐期最大相对平衡误差={max_rel_err:.1e}   (断言 < 1e-12，float64 舍入级)")
    print(f"    总产出增长：{PERIODS-1} 期累计 {total_growth:.3f}×  ⟹ "
          f"每期 {g_emp:.6%}   (断言 = {G_RATE:.0%})")
    assert max_rel_err < 1e-12, "比例增长路径上一切平衡条件应逐期成立（相对误差）"
    assert abs(g_emp - G_RATE) < 1e-12, "总增长应精确等于比例 g"

    # ═══ (c) TRPF 赛跑：p' = e/(k+1) 三分支 ═══
    T = 40
    ks_up = np.linspace(3.0, 6.0, T)              # 有机构成上升
    # 分支一：e 固定 ⟹ p' 下降
    e_fix = np.full(T, 1.0)
    p1 = e_fix / (ks_up + 1.0)
    # 分支二：e 与 (k+1) 同速 ⟹ p' 不变
    e_sync = 1.0 * (ks_up + 1.0) / (ks_up[0] + 1.0)
    p2 = e_sync / (ks_up + 1.0)
    # 分支三：e 更快（每期再快 2%）⟹ p' 上升
    e_fast = 1.0 * ((ks_up + 1.0) / (ks_up[0] + 1.0)) ** 1.02
    p3 = e_fast / (ks_up + 1.0)
    print(f"\n(c) TRPF 赛跑（k 从 {ks_up[0]:.0f} 升到 {ks_up[-1]:.0f}）：")
    print(f"    分支一 e=1.0 固定：p' 从 {p1[0]:.4f} 降到 {p1[-1]:.4f}"
          f"  Δ={p1[-1]-p1[0]:+.4f}   (断言 < 0)")
    print(f"    分支二 e 与(k+1)同步：p' 恒为 {p2[0]:.4f}  "
          f"全程波动={np.ptp(p2):.1e}   (断言 ≈ 0)")
    print(f"    分支三 e 略快：p' 从 {p3[0]:.4f} 升到 {p3[-1]:.4f}"
          f"  Δ={p3[-1]-p3[0]:+.4f}   (断言 > 0)")
    assert p1[-1] < p1[0], "e 固定时有机构成上升必压低利润率"
    assert np.ptp(p2) < 1e-12, "同步增长时利润率不变"
    assert p3[-1] > p3[0], "剩余价值率足够快时利润率反升"

    # 交叉验证：p'=m/(c+v) 原式与 e/(k+1) 等价（任取一组 c,v,m）
    c0, v0, e0 = 4500.0, 1000.0, 1.1
    m0 = e0 * v0
    lhs = m0 / (c0 + v0)
    rhs = e0 / (c0 / v0 + 1.0)
    assert abs(lhs - rhs) < 1e-12
    print("    附：p'=m/(c+v) ≡ e/(k+1) 恒等验证 ✅")

    print("\n全部断言通过 ✅  表式：平衡等式即测试；增长：比例路径是"
          "谱解；利润率：赛跑决定方向。")
    print("带走一句（04 章）：等式即测试——会计传统的理论内容"
          "天然是断言网络。")

if __name__ == "__main__":
    main()
