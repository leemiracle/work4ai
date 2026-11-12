#!/usr/bin/env python3
"""讲透博弈论 WSL 实验 8：OpenSpiel 官方 CFR/CFR+ 跑 Kuhn——与理论、手写三方对拍。
E1 三方对拍（16 章收官锚点）：OpenSpiel 官方 CFRSolver 与 CFRPlusSolver 各训 10⁵ 次迭代，
   每 10³ 次记录【平均策略的精确博弈值】（本文件自写树遍历求值，不用库的近似接口）与
   nash_conv（可剥削度）——终值 vs 理论 −1/18 ≈ −0.0556（容差 0.01）vs lab07 手写 −0.0556：
   理论 / OpenSpiel CFR / OpenSpiel CFR+ / lab07 手写 四路并排。
E2 双算法收敛对比：vanilla CFR（Zinkevich 2007）vs CFR+（Tammelin 2014：交替更新+遗憾正化+
   线性平均）——nash_conv 双对数曲线，同迭代数下 CFR+ 快约一个量级（实测见打印）。
环境：WSL Ubuntu-22.04 + open_spiel（安装见 wsl_labs/README.md）；产出 png 落在本目录（Windows 侧同盘可见）。
产出：openspiel_cfr.png（1×2：平均策略价值收敛 vs −1/18 / nash_conv 双对数双算法）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyspiel
from open_spiel.python.algorithms import cfr, exploitability
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "sans-serif"]
TOL = 0.01
ITERS = 100_000
CADENCE = 1_000
LAB07_HANDWRITTEN = -0.0556          # lab07 E3 手写 vanilla CFR 2×10⁵ 迭代实测（Windows 侧）


def exact_value(game, policy_obj):
    """平均策略剖面的精确博弈值：全树枚举（与 lab07 KuhnCFR.converged_value 同构——
    chance 节点枚举 chance_outcomes、决策节点查 action_probabilities、终端取 player_return(0)）。"""
    def ev(state):
        if state.is_terminal():
            return state.player_return(0)
        if state.is_chance_node():
            return sum(p * ev(state.child(a)) for a, p in state.chance_outcomes())
        ap = dict(policy_obj.action_probabilities(state))
        return sum(p * ev(state.child(a)) for a, p in ap.items())
    return ev(game.new_initial_state())


def run(solver_factory, label):
    """跑满 ITERS，每 CADENCE 次记录 (迭代数, 精确价值, nash_conv)。"""
    game = pyspiel.load_game("kuhn_poker")
    solver = solver_factory(game)
    rows = []
    for t in range(1, ITERS + 1):
        solver.evaluate_and_update_policy()
        if t % CADENCE == 0:
            avg = solver.average_policy()
            rows.append((t, exact_value(game, avg), exploitability.nash_conv(game, avg)))
    print(f"  {label} 完成 {ITERS} 次迭代，记录 {len(rows)} 个检查点")
    return np.array(rows)


print("=" * 68)
print("E1 · 三方对拍：理论 −1/18 / OpenSpiel 官方 / lab07 手写")
print("=" * 68)
print(f"理论锚点（16 章 §四手推 + Kuhn 1950）：Kuhn 扑克博弈值（P1）= −1/18 ≈ {-1/18:.4f}；"
      f"容差 {TOL}；lab07 手写 vanilla CFR（Windows 纯 numpy）= {LAB07_HANDWRITTEN:+.4f}")
rows_cfr = run(cfr.CFRSolver, "OpenSpiel CFR（vanilla）")
rows_p = run(cfr.CFRPlusSolver, "OpenSpiel CFR+")
v_cfr, v_p = rows_cfr[-1, 1], rows_p[-1, 1]
nc_cfr, nc_p = rows_cfr[-1, 2], rows_p[-1, 2]
print(f"  OpenSpiel CFR    终值博弈值 = {v_cfr:+.6f}（|偏差| {abs(v_cfr + 1/18):.6f}）"
      f"{'✓' if abs(v_cfr + 1/18) < TOL else '⚠'}，nash_conv = {nc_cfr:.3e}")
print(f"  OpenSpiel CFR+   终值博弈值 = {v_p:+.6f}（|偏差| {abs(v_p + 1/18):.6f}）"
      f"{'✓' if abs(v_p + 1/18) < TOL else '⚠'}，nash_conv = {nc_p:.3e}")
ok_e1 = abs(v_cfr + 1 / 18) < TOL and abs(v_p + 1 / 18) < TOL
print(f"→ E1 对拍：理论 −1/18 / OpenSpiel CFR {v_cfr:+.4f} / CFR+ {v_p:+.4f} / lab07 手写 −0.0556"
      f" —— " + ("四方一致，全绿 ✓" if ok_e1 else "⚠ 如实标注"))
print("  诚实标注：价值锚点全绿只说明'都到了均衡族'（价值是族不变量）；策略层面的差异看 nash_conv。")

print("\n" + "=" * 68)
print("E2 · 收敛速度对比：vanilla CFR vs CFR+（nash_conv 双对数）")
print("=" * 68)
# 手推预期（16 章 §五）：CFR+ 三处手术（交替更新/遗憾即时正化/线性平均）在 Kuhn 上快约一个量级
ratio = nc_cfr / nc_p if nc_p > 0 else float("inf")
ok_e2 = nc_p < nc_cfr
print(f"  同为 10⁵ 次迭代：CFR nash_conv = {nc_cfr:.3e} vs CFR+ = {nc_p:.3e}（比值 ≈ {ratio:.0f} 倍）")
for t in (1_000, 10_000, 100_000):
    nc1 = rows_cfr[t // CADENCE - 1, 2]
    nc2 = rows_p[t // CADENCE - 1, 2]
    print(f"    迭代 {t:>6}：CFR {nc1:.3e} | CFR+ {nc2:.3e}")
print(f"→ E2 对拍：CFR+ 收敛快于 vanilla CFR —— " + ("✓（16 章 §五的实测版）" if ok_e2 else "⚠ 如实标注"))

# ---------------- 图 ----------------
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))

ax = axes[0]
ax.plot(rows_cfr[:, 0], rows_cfr[:, 1], lw=1.1, color="tab:blue", label="OpenSpiel CFR（vanilla）")
ax.plot(rows_p[:, 0], rows_p[:, 1], lw=1.1, color="tab:orange", label="OpenSpiel CFR+")
ax.axhline(-1 / 18, color="red", ls="--", lw=1.4, label="理论 −1/18 ≈ −0.0556")
ax.axhline(LAB07_HANDWRITTEN, color="green", ls=":", lw=1.4, label="lab07 手写 −0.0556")
ax.fill_between([800, 110000], -1 / 18 - TOL, -1 / 18 + TOL, color="red", alpha=0.10, label="容差 ±0.01")
ax.set_xscale("log")
ax.set_xlabel("迭代次数"); ax.set_ylabel("平均策略的精确博弈值（P1）")
ax.set_title("E1 · 三方对拍：理论 / OpenSpiel 双求解器 / lab07 手写\n（价值是均衡族不变量——四线合一）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="center right"); ax.grid(True, alpha=0.3)

ax = axes[1]
ax.loglog(rows_cfr[:, 0], rows_cfr[:, 2], lw=1.2, color="tab:blue", label="CFR（vanilla）")
ax.loglog(rows_p[:, 0], rows_p[:, 2], lw=1.2, color="tab:orange", label="CFR+（交替+正化+线性平均）")
ax.annotate(f"10⁵ 迭代处：{nc_cfr:.1e} vs {nc_p:.1e}\n（≈{ratio:.0f} 倍差距）",
            xy=(rows_p[-1, 0], nc_p), xytext=(-150, -6), textcoords="offset points",
            fontsize=9, color="dimgray",
            arrowprops=dict(arrowstyle="->", color="dimgray"))
ax.set_xlabel("迭代次数"); ax.set_ylabel("nash_conv（可剥削度）")
ax.set_title("E2 · CFR+ vs vanilla：同迭代数收敛快约一个量级\n（Tammelin 2014 三处手术的实测）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="lower left"); ax.grid(True, which="both", alpha=0.25)

fig.suptitle("lab08 · OpenSpiel 官方 CFR/CFR+ × 理论 −1/18 × lab07 手写：Kuhn 扑克三方对拍（WSL）", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.93))
OUT = Path(__file__).resolve().parent / "openspiel_cfr.png"
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
