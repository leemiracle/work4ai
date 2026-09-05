#!/usr/bin/env python3
"""讲透博弈论实验 2：混合、minimax 与真实罚点球实验室。
E1 罚点球手算（03 章 §三：x*=4/7、值 5.45/7）vs nashpy 双枚举对拍（差异 < 1e-8） | E2 scipy.linprog 手解行玩家 minimax LP（值 vs nashpy 均衡值对拍；对偶=列玩家 LP，强对偶=minimax 定理） | E3 Chiappori-Levitt-Groseclose (2002) 真实罚点球统计 vs 2×2 简化理论并排条形图（诚实标注：模型简化，方向性一致）
产出：mixed.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import nashpy as nash
from pathlib import Path
from scipy.optimize import linprog

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
rng = np.random.default_rng(42)

# ----------------------------------------------------------------------
# 统一记号（与 00/03 章、lab01 完全一致）：
#   A[i, j] = 行玩家（射门）在（行 i, 列 j）的收益；罚点球是常和 → 列玩家收益 = 1 − A（零和分析中用 −A）
# ----------------------------------------------------------------------
PEN = np.array([[0.65, 0.95],
                [0.95, 0.55]])              # 行=踢左/踢右，列=扑左/扑右（同侧得分率低）
ROW_ACT = ("踢左", "踢右")
COL_ACT = ("扑左", "扑右")
HAND_X = 4 / 7                              # 03 章 §三 手算：p*(踢左) = (d−c)/(a−b−c+d) = 0.40/0.70
HAND_V = 5.45 / 7                           # 03 章 §三 手算：博弈值 = 0.65·(4/7) + 0.95·(3/7) ≈ 0.7786

# ======================================================================
print("=" * 68)
print("E1 · 罚点球混合均衡：03 章手算 vs nashpy 双枚举对拍")
print("=" * 68)
a, b, c, d = PEN[0, 0], PEN[0, 1], PEN[1, 0], PEN[1, 1]
x_hand = (d - c) / (a - b - c + d)          # 03 章 §2.2 零和公式（本矩阵常和，公式合法）
v_hand = a * x_hand + b * (1 - x_hand)
ind_L = (1 - PEN[0, 0]) * x_hand + (1 - PEN[1, 0]) * (1 - x_hand)   # 守门员视角无差异验算
ind_R = (1 - PEN[0, 1]) * x_hand + (1 - PEN[1, 1]) * (1 - x_hand)
print(f"03 章公式 x* = (d−c)/(a−b−c+d) = ({d:g}−{c:g})/({a:g}−{b:g}−{c:g}+{d:g}) = {x_hand:.10f}（= 4/7 = {HAND_X:.6f}）")
print(f"博弈值 v = 0.65·(4/7) + 0.95·(3/7) = {v_hand:.10f}（= 5.45/7 = {HAND_V:.6f}）")
print(f"无差异验算：守门员扑左期望 {ind_L:.10f} vs 扑右期望 {ind_R:.10f}（差 {abs(ind_L - ind_R):.2e}）")
eqs = list(nash.Game(PEN, -PEN).support_enumeration())
eqv = list(nash.Game(PEN, -PEN).vertex_enumeration())
s, t = np.asarray(eqs[0][0]), np.asarray(eqs[0][1])
v_nash = float(s @ PEN @ t)
diff_sup = max(abs(x_hand - s[0]), abs((1 - x_hand) - s[1]), abs(v_hand - v_nash))
diff_ver = max(abs(x_hand - np.asarray(eqv[0][0])[0]), abs(v_hand - float(np.asarray(eqv[0][0]) @ PEN @ np.asarray(eqv[0][1]))))
print(f"nashpy support_enumeration: P1=({s[0]:.4f}, {s[1]:.4f})  P2=({t[0]:.4f}, {t[1]:.4f})  值 {v_nash:.10f}")
print(f"nashpy vertex_enumeration  : P1=({eqv[0][0][0]:.4f}, {eqv[0][0][1]:.4f})  值 {float(np.asarray(eqv[0][0]) @ PEN @ np.asarray(eqv[0][1])):.10f}")
print(f"→ 手算 vs nashpy（双枚举）：support 最大差 {diff_sup:.2e} / vertex 最大差 {diff_ver:.2e} "
      + ("✓（均 < 1e-8，浮点尾数级）" if max(diff_sup, diff_ver) < 1e-8 else "⚠ 超过 1e-8 阈值——如实标注，勿放宽"))

# ======================================================================
print("\n" + "=" * 68)
print("E2 · scipy.linprog 手解 minimax LP：行玩家问题 vs 其对偶（=列玩家问题）")
print("=" * 68)
# 行玩家 maximin LP（04 章 §四）：max v  s.t.  v ≤ Σᵢ aᵢⱼ xᵢ ∀j,  Σx=1,  x≥0,  v 自由
# scipy 标准形只认 min → 目标取 −v；v 自由 → bounds=(None, None)。变量 z = (v, x_踢左, x_踢右)
c_row = np.array([-1.0, 0.0, 0.0])
A_ub_row = np.hstack([np.ones((2, 1)), -PEN.T])   # 第 j 行：v − Σᵢ aᵢⱼ xᵢ ≤ 0
b_ub = np.zeros(2)
A_eq = np.array([[0.0, 1.0, 1.0]])                 # Σx = 1
b_eq = np.array([1.0])
bounds = [(None, None), (0.0, None), (0.0, None)]
r_row = linprog(c_row, A_ub=A_ub_row, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
v_lp, x_lp = -r_row.fun, r_row.x[1:]
# 对偶 = 列玩家 minimax LP：min w  s.t.  (Ay)ᵢ ≤ w ∀i,  Σy=1,  y≥0,  w 自由
c_col = np.array([1.0, 0.0, 0.0])
A_ub_col = np.hstack([-np.ones((2, 1)), PEN])      # 第 i 行：(Ay)ᵢ − w ≤ 0
r_col = linprog(c_col, A_ub=A_ub_col, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
w_lp, y_lp = r_col.fun, r_col.x[1:]
print(f"行玩家 LP（highs）：v = {v_lp:.10f}，x = ({x_lp[0]:.6f}, {x_lp[1]:.6f})   ← 理论 4/7, 3/7, 5.45/7")
print(f"对偶/列玩家 LP（highs）：w = {w_lp:.10f}，y = ({y_lp[0]:.6f}, {y_lp[1]:.6f})   ← 强对偶 ⟺ minimax 定理")
print(f"→ 对拍 1：LP 值 vs nashpy 均衡值 = {v_lp:.10f} vs {v_nash:.10f}（差 {abs(v_lp - v_nash):.2e}，{'< 1e-6 ✓' if abs(v_lp - v_nash) < 1e-6 else '⚠ 超阈值——如实标注'}）")
print(f"→ 对拍 2：对偶间隙 v − w = {v_lp - w_lp:+.2e}（强对偶/minimax 定理的数值兑现）")
slack = v_lp - x_lp @ PEN                          # 互补松弛：y_j > 0 ⟹ 第 j 列约束取等
print(f"→ 互补松弛读法：y = (4/7,3/7) 全支撑 ⟹ 两列约束同取等：松紧量 = ({slack[0]:+.2e}, {slack[1]:+.2e}) ✓"
      if np.all(y_lp > 1e-9) and np.all(np.abs(slack) < 1e-9)
      else f"→ 互补松弛松紧量 = ({slack[0]:+.2e}, {slack[1]:+.2e})——与支撑理论不符处如实标注")

# ======================================================================
print("\n" + "=" * 68)
print("E3 · 真实罚点球 vs 2×2 简化理论（Chiappori-Levitt-Groseclose 2002）")
print("=" * 68)
REAL_KICK = np.array([0.45, 0.15, 0.40])   # 射门方向 L/C/R：文献常引近似汇总（459 球，法甲+意甲）
THEO_2X2 = np.array([4 / 7, 3 / 7])        # 2×2 理论只含左/右：C 无对应方向
ratio_real = REAL_KICK[0] / REAL_KICK[2]
ratio_theo = THEO_2X2[0] / THEO_2X2[1]
print(f"实测射门分布（近似汇总）：踢左 {REAL_KICK[0]:.2f} / 中路 {REAL_KICK[1]:.2f} / 踢右 {REAL_KICK[2]:.2f}")
print(f"2×2 理论预测：踢左 {THEO_2X2[0]:.4f}（=4/7）/ 踢右 {THEO_2X2[1]:.4f}（=3/7）；中路无对应方向（模型简化）")
print(f"L:R 对比：实测 {ratio_real:.3f} vs 理论 {ratio_theo:.3f} → 方向一致（均左多于右），幅度有偏差")
print("得分率口径：同侧 P_S ≈ 0.63、异侧 ≈ 0.95（论文记法）vs 本系列教学矩阵 0.65/0.55/0.95（圆整，方向量级一致）")
print("诚实标注：真实值为文献常引的近似汇总（原表逐格数字未逐项复核）；2×2 抹去中路——模型简化，方向性一致；"
      "系统性偏差的正式名字叫 QRE（50 章）")

# ======================================================================
# mixed.png：2×2 子图——(a) 单纯形 FP 轨迹 (b) minimax 几何 (c)(d) 真实 vs 理论条形图
# ======================================================================
def fictitious_play(A, iters=80):
    """手写 FP（Robinson 1951：零和收敛）：双方各对对手的历史平均最优反应，画平均轨迹。"""
    m, n = A.shape
    k_cnt = np.zeros(m); g_cnt = np.zeros(n)
    k_cnt[rng.integers(0, m)] += 1; g_cnt[rng.integers(0, n)] += 1
    traj_k, traj_g = [k_cnt / k_cnt.sum()], [g_cnt / g_cnt.sum()]
    for _ in range(iters):
        xbar, ybar = k_cnt / k_cnt.sum(), g_cnt / g_cnt.sum()
        k_cnt[int(np.argmax(A @ ybar))] += 1          # 行玩家 BR（最大化自己收益）
        g_cnt[int(np.argmin(xbar @ A))] += 1          # 列玩家 BR（最小化行玩家收益）
        traj_k.append(k_cnt / k_cnt.sum()); traj_g.append(g_cnt / g_cnt.sum())
    return np.array(traj_k), np.array(traj_g)


traj_k, traj_g = fictitious_play(PEN)
fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.2))

# (a) 混合策略单纯形上的 FP 轨迹：纵轴即单纯形线段（1=纯踢左，0=纯踢右）
ax = axes[0, 0]
ax.axhline(HAND_X, color="red", lw=1.2, ls="--", label="均衡 x* = 4/7 ≈ 0.571（03 章手算）")
ax.plot(traj_k[:, 0], lw=1.8, label="行玩家（踢左概率）FP 平均")
ax.plot(traj_g[:, 0], lw=1.4, ls="-.", label="列玩家（扑左概率）FP 平均")
ax.set_ylim(0, 1); ax.set_xlabel("fictitious play 迭代"); ax.set_ylabel("P(踢左) / P(扑左)")
ax.annotate("纵轴即两策略单纯形：1=纯左，0=纯右", xy=(0.03, 0.04), xycoords="axes fraction", fontsize=9, color="gray")
ax.set_title("E1/E2 · 混合策略单纯形：FP 轨迹收敛 x*=4/7", fontsize=11)
ax.legend(fontsize=9, loc="right")

# (b) minimax 几何：两条约束线 + 下包络峰值 = 博弈值（linprog 与 nashpy 双路对拍同点）
ax = axes[0, 1]
xs = np.linspace(0, 1, 201)
pay_L = PEN[0, 0] * xs + PEN[1, 0] * (1 - xs)   # 对手扑左：0.65x + 0.95(1−x)
pay_R = PEN[0, 1] * xs + PEN[1, 1] * (1 - xs)   # 对手扑右：0.95x + 0.55(1−x)
ax.plot(xs, pay_L, lw=1.5, label="对手扑左时的期望")
ax.plot(xs, pay_R, lw=1.5, ls="-.", label="对手扑右时的期望")
ax.plot(xs, np.minimum(pay_L, pay_R), color="k", lw=2.6, label="下包络 = 最坏情况（安全下界）")
ax.scatter([HAND_X], [HAND_V], s=90, color="red", zorder=5)
ax.annotate("maximin 峰值 = v = 5.45/7 ≈ 0.779\n（linprog/nashpy/手算 三方同点）", xy=(HAND_X, HAND_V),
            xytext=(0.66, 0.62), fontsize=9, arrowprops=dict(arrowstyle="->", color="red"), color="red")
ax.axvline(HAND_X, color="red", lw=0.8, ls=":")
ax.set_xlabel("P(踢左) = x"); ax.set_ylabel("射手期望得分率")
ax.set_title("E2 · minimax 几何：下包络峰值 = 博弈值", fontsize=11)
ax.legend(fontsize=9, loc="lower left")

# (c) E3：射门方向分布——真实（L/C/R）vs 2×2 理论（只有 L/R）
ax = axes[1, 0]
pos = np.arange(3)
ax.bar(pos - 0.2, REAL_KICK, width=0.38, label="实测（Chiappori 2002，459 球，近似汇总）")
ax.bar(pos[:2] + 0.2, THEO_2X2, width=0.38, label="2×2 理论（4/7, 3/7）")
ax.text(2 + 0.2, 0.02, "无此方向\n(模型简化)", ha="center", fontsize=9, color="gray")
for p_, v_ in zip(pos - 0.2, REAL_KICK):
    ax.text(p_, v_ + 0.01, f"{v_:.2f}", ha="center", fontsize=9)
for p_, v_ in zip(pos[:2] + 0.2, THEO_2X2):
    ax.text(p_, v_ + 0.01, f"{v_:.3f}", ha="center", fontsize=9)
ax.set_xticks(pos, ("踢左", "中路", "踢右")); ax.set_ylabel("频率"); ax.set_ylim(0, 0.68)
ax.set_title("E3 · 射门方向：真实 vs 理论（L:R 实测 1.13 vs 理论 1.33，方向一致）\n模型简化：2×2 抹去中路；偏差=QRE（50 章）", fontsize=10)
ax.legend(fontsize=9)

# (d) E3：得分率——实测量级（同侧 P_S≈0.63 / 异侧≈0.95）vs 本系列教学矩阵（0.65/0.55/0.95）
ax = axes[1, 1]
labels = ("同侧\n实测 P_S", "同侧\n模型·踢左", "同侧\n模型·踢右", "异侧\n实测", "异侧\n模型")
vals = (0.63, 0.65, 0.55, 0.95, 0.95)
cols = ("tab:red", "tab:blue", "tab:blue", "tab:red", "tab:blue")
ax.bar(np.arange(5), vals, width=0.55, color=cols)
for i, v_ in enumerate(vals):
    ax.text(i, v_ + 0.012, f"{v_:.2f}", ha="center", fontsize=9)
ax.set_xticks(np.arange(5), labels, fontsize=9); ax.set_ylabel("得分率"); ax.set_ylim(0, 1.08)
ax.set_title("E3 · 得分率：同侧低/异侧高——实测量级 vs 教学圆整矩阵\n（方向与量级一致；矩阵为教学化取整，非原表逐格）", fontsize=10)

fig.suptitle("lab02 · 罚点球的混合、minimax 与真实数据（三路对拍：手算 / nashpy / scipy.linprog）", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.96))
OUT = Path(__file__).resolve().parent / "mixed.png"   # 恒定落到 experiments/ 下，与运行 cwd 无关
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
