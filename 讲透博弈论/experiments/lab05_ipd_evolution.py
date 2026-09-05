#!/usr/bin/env python3
"""讲透博弈论实验 5：重复博弈与演化——axelrod IPD 锦标赛、Moran 入侵、手写复制动态。
E1 axelrod 锦标赛（10 策略 round-robin，turns=200，repetitions=50，Tournament seed=42）：
   善良阵营（TFT/Grudger/WSLS/Cooperator）vs 不善良阵营（Prober/ZDExtort2/BackStabber/Alternator/Random/Defector）
   ——排名表按"每轮每对手平均得分"（results.scores 与玩家声明顺序对齐，别拿它 zip ranked_names——
   ranked_names 是按总分降序的另一张表，已实测核实；分母 turns·(N−1)，默认无自对局）。
   直觉预期（Axelrod 1980 叙事）：善良且可激怒者领跑、Defector/Random 垫底——实测如实对照。
E2 Moran 过程（axelrod.MoranProcess，BD 模式、无变异、stop_on_fixation 默认开；实测：score_history 为
   该代每人每轮对全部对手的总分，无自对局，适应度 ∝ 总分）：TFT 入侵 ALLD 种群，初始比例
   i/N ∈ {0.1, 0.2, 0.4, 0.6, 0.8}，每档 30 seeds 估固定概率，对照中性漂移基线 i/N。
   手推锚点：单挑 TFT 0.995 分/轮 < ALLD 1.02（单挑输）；种群适应度交叉阈值
   0.995+2.005x > 1+0.02x ⟺ x > 0.005/1.985 ≈ 0.00252（0.25%）——i=1/10 已过线，选择顺风，
   实测固定概率应高于 i/N（合作红利随比例放大）。
E3 手写复制动态（欧拉积分，dt=0.05 显式声明）：鹰鸽 v=2,c=4 → f_H=2−3x、f_D=1−x、ẋ=x(1−x)(1−2x)，
   x₀∈{0.1,0.5,0.9} 三轨收敛 x*=v/c=0.5（±0.01）；RPS 零和矩阵 A=[[0,−1,1],[1,0,−1],[−1,1,0]] 的
   内点 (1/3,1/3,1/3)：雅可比特征值理论 0, ±i√3/3=±0.5774i（纯虚 → 中心+闭轨 → 无 ESS 的机制）；
   轨线终值远离中心但时间平均 → (1/3,1/3,1/3)（50 章第三堵墙的几何图像）。
产出：ipd_evo.png（1×3：锦标赛得分条形 / Moran 固定概率 vs 初始比例 / 复制动态相图+RPS 环）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import axelrod as axl
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
rng = np.random.default_rng(42)
TOL = 0.01               # 诚实校准公约容差

# ======================================================================
print("=" * 68)
print("E1 · axelrod 锦标赛：10 策略 round-robin（turns=200, repetitions=50, seed=42）")
print("=" * 68)
# 注意（已实测核实，axelrod 4.14）：results.scores[i] 与【玩家声明顺序】对齐，
#   ranked_names 是按总分降序的另一张名字表——两者不能 zip（老教程常见错法）。
#   每对手平均分 = mean(scores_i)/(turns·(N−1))；Tournament 默认无自对局（TFT 对 4 对手 499 分已手算核对）。
ROSTER = [  # (策略类, 善良?, 一句话性格)——善良 = 永不出手背叛（Axelrod 1980 的 nice）
    (axl.TitForTat,         True,  "以牙还牙：善良·报复·宽容·清晰"),
    (axl.Grudger,           True,  "一被背叛记仇到底：善良·报复·零宽容"),
    (axl.WinStayLoseShift,  True,  "赢就守、输就变：善良·会学习"),
    (axl.Cooperator,        True,  "永远合作：善良但可被无限剥削"),
    (axl.Prober,            False, "开局试探，专割天真者"),
    (axl.ZDExtort2,         False, "零行列式勒索：你只能拿残羹"),
    (axl.BackStabber,       False, "装到最后两轮才捅刀"),
    (axl.Alternator,        False, "轮流 C,D：规律得可预测"),
    (axl.Random,            False, "掷硬币 0.5"),
    (axl.Defector,          False, "永远背叛"),
]
players = [cls() for cls, _, _ in ROSTER]
N = len(players)
tour = axl.Tournament(players=players, turns=200, repetitions=50, seed=42)  # seed 锁含 Random 档的全部随机源
res = tour.play(progress_bar=False)
per_turn = [np.mean(s) / (200 * (N - 1)) for s in res.scores]     # 与声明顺序对齐
order = np.argsort(per_turn)[::-1]                                # 自己按平均分降序排
print(f"理论锚点（Axelrod 1980/1984 叙事）：善良（不先背叛）是锦标赛首要分裂线；善良且可激怒（TFT 型）领跑预期；Defector/Random 垫底预期")
print(f"{'排名':>3} | {'策略':<28} | {'每轮每对手均分':>12} | {'重复间std':>9} | 性格")
for rank, idx in enumerate(order, 1):
    cls, nice, tag = ROSTER[idx]
    s_turns = np.array(res.scores[idx]) / (200 * (N - 1))
    print(f"{rank:>3} | {cls.name:<28} | {per_turn[idx]:>12.4f} | {s_turns.std():>9.4f} | {tag}")
e1_rows = [(ROSTER[idx][0].name, per_turn[idx], ROSTER[idx][1]) for idx in order]
nice_mean = np.mean([v for _, v, n in e1_rows if n])
nasty_mean = np.mean([v for _, v, n in e1_rows if not n])
top4_nice = sum(n for _, _, n in e1_rows[:4])
print(f"善良阵营平均 {nice_mean:.3f} vs 不善良阵营平均 {nasty_mean:.3f}；前四名中善良者 {top4_nice}/4")
print(f"诚实标注：本赛场'天真者浓度'（Cooperator/Alternator 在场）与对手池构成会改写排名——"
      f"无名定理说任何名次都能被'谁在场'重排（10 章 §三），锦标赛测的是人口结构不是绝对优劣；"
      f"随机源已锁 Tournament seed=42（含 Random 档，可复现）。")

# ======================================================================
print("\n" + "=" * 68)
print("E2 · Moran 过程：TFT 入侵 ALLD 固定概率 vs 初始比例（N=10, turns=200, 30 seeds/档）")
print("=" * 68)
# 手推单挑锚点（turns=200）：TFT vs ALLD：t1 C 吃 S=0，之后互相 D → TFT = 199/200 = 0.995 分/轮；
#   ALLD vs TFT = (5 + 199)/200 = 1.02 → 单挑 TFT 输。
#   种群适应度（每轮每对手平均）：f_TFT(x) = 0.995 + 2.005x（遇 TFT 得 3），f_ALLD(x) = 1 + 0.02x（遇 ALLD 得 1）
#   → 交叉阈值 x > 0.005/1.985 ≈ 0.00252 (0.25%)——i=1/10 已过线，选择顺风 → 固定概率应 > 中性基线 i/N
N_POP, TURNS_MP, K = 10, 200, 30
match0 = axl.Match((axl.TitForTat(), axl.Defector()), turns=TURNS_MP)
match0.play()
per_round = np.array(match0.scores())          # (turns, 2)：每轮 (TFT, ALLD) 得分对（已实测核实）
tft_pt, alld_pt = per_round.mean(axis=0)       # 列均值 = 各自每轮平均分
thr = (1.0 - tft_pt) / (3.0 - tft_pt - 0.02)             # 0.995+2.005x = 1+0.02x → x = 0.005/1.985
print(f"单挑手推 vs Match 实测：TFT {tft_pt:.4f} 分/轮（手推 199/200=0.995）、ALLD {alld_pt:.4f}（手推 204/200=1.02）——单挑 TFT 输")
print(f"适应度交叉阈值（手推）：x* 满足 0.995+2.005x = 1+0.02x → x = {thr:.5f}（0.25%）——i=1/10=10% 已过线 → 选择顺风")
print(f"{'i/10':>5} | {'实测固定概率':>10} | {'±2se':>8} | {'中性基线 i/N':>10} | 判读")
e2_rows, ok_e2, n_sig = [], True, 0
for i in (1, 2, 4, 6, 8):
    wins = 0
    for k in range(K):
        pop = [axl.TitForTat() for _ in range(i)] + [axl.Defector() for _ in range(N_POP - i)]
        mp = axl.MoranProcess(players=pop, turns=TURNS_MP, seed=100 * i + k)
        mp.play()
        wins += (mp.winning_strategy_name == "Tit For Tat")
    p_hat = wins / K
    se = (p_hat * (1 - p_hat) / K) ** 0.5
    above = p_hat > i / N_POP                   # 方向对拍（brief 锚点）：固定概率压中性漂移基线
    sig = p_hat - 2 * se > i / N_POP            # 2se 显著性——30 seeds 精度有限，与方向分报，不混为一谈
    e2_rows.append((i / N_POP, p_hat, se))
    if not above:
        ok_e2 = False
    if sig:
        n_sig += 1
    verdict = ("✓（2se 显著）" if sig else "✓（2se 不显著——30 seeds 精度如实标注）") if above else "⚠ 未压基线——如实标注"
    print(f"{i}/{N_POP:>3} | {p_hat:>10.3f} | {2 * se:>8.3f} | {i / N_POP:>10.1f} | {verdict}")
print(f"→ E2 对拍：各档实测固定概率压中性基线 i/N（单挑输≠群体输，合作红利随比例放大）—— 方向 {('全对 ✓' if ok_e2 else '⚠ 有档未超')}"
      f"；2se 显著 {n_sig}/5 档")
print("  诚实标注：30 seeds/档的估计精度有限（二项 se ~0.09）；TFT 优势是频率依赖的（阈值 0.25% 已过），"
      "换成 Grudger/WSLS 入侵数值会不同；MoranProcess 实测形态：BD 模式、score_history=该代每人每轮对全部对手的总分"
      "（无自对局，适应度∝总分）、stop_on_fixation 默认开。")

# ======================================================================
print("\n" + "=" * 68)
print("E3 · 手写复制动态（欧拉积分 dt=0.05，声明）：鹰鸽三轨收敛 x*=0.5 + RPS 闭轨")
print("=" * 68)
DT, N_STEPS = 0.05, 500     # 积分步长显式声明；t ∈ [0, 25]
# 鹰鸽（v=2, c=4，00 章记号）：f_H = x·(v−c)/2 + (1−x)·v = 2−3x；f_D = (1−x)·v/2 = 1−x
#   ẋ = x(f_H − f̄) = x(1−x)(f_H − f_D) = x(1−x)(1−2x)；不动点 {0, 1, 1/2}，g'(1/2) = −0.5 < 0 → 渐近稳定
def hd_rhs(x):
    fH = 2 - 3 * x
    fD = 1 - x
    fbar = x * fH + (1 - x) * fD
    return x * (fH - fbar)
print(f"理论锚点（11 章 §三手推）：ẋ = x(1−x)(1−2x)，x* = v/c = 2/4 = 0.5（渐近稳定，g'(1/2)=−0.5）")
hd_tracks = []
ok_e3a = True
for x0 in (0.1, 0.5, 0.9):
    x = x0
    traj = [x]
    for _ in range(N_STEPS):
        x = x + DT * hd_rhs(x)
        traj.append(x)
    hd_tracks.append(np.array(traj))
    flag = "✓" if abs(x - 0.5) < TOL else "⚠ 超容差"
    ok_e3a &= abs(x - 0.5) < TOL
    print(f"  x₀ = {x0:.1f} → 终值 {x:.6f}（vs x*=v/c=0.5，|偏差| = {abs(x - 0.5):.6f}）{flag}")
print(f"→ E3a 对拍：三轨收敛 x*=0.5（容差 {TOL}）—— " + ("全绿 ✓" if ok_e3a else "⚠ 如实标注"))

# RPS（零和）：A = [[0,−1,1],[1,0,−1],[−1,1,0]]，反对称 → x'Ax ≡ 0 → ẋᵢ = xᵢ(Ax)ᵢ
#   内点 p = (1/3,1/3,1/3)：J(p) = A/3，A 的特征值 {0, ±i√3} → 理论 {0, ±i√3/3 = ±0.5774i}
A = np.array([[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]])
def rps_rhs(x):
    ax_vec = A @ x
    return x * ax_vec
def rps_step(x, dt):
    x1 = x + dt * rps_rhs(x)            # 欧拉步；反对称 → x'Ax=0 → 总和 1 在步长内精确守恒
    x1 = np.maximum(x1, 0)              # 离散化可能出单纯形——截回（诚实标注：数值护栏）
    return x1 / x1.sum()
print(f"理论锚点（11 章 §五手推）：内点 (1/3,1/3,1/3) 处雅可比特征值理论 = 0, ±i√3/3 ≈ ±0.5774i（纯虚 → 中心 → 闭轨 → 无 ESS）")
p0 = np.array([1 / 3, 1 / 3, 1 / 3])
J = np.zeros((3, 3))
for j in range(3):                       # 数值雅可比（中心差分）
    e = np.zeros(3); e[j] = 1e-6
    J[:, j] = (rps_rhs(p0 + e) - rps_rhs(p0 - e)) / 2e-6
eig = np.linalg.eigvals(J)
eig_sorted = sorted(eig, key=lambda z: (abs(z.imag), z.imag))   # 理论序：0、−i√3/3、+i√3/3
th_eig = [0.0, -0.57735j, 0.57735j]
for z, th in zip(eig_sorted, th_eig):
    okz = abs(z.real) < TOL and abs(abs(z.imag) - abs(th)) < TOL
    print(f"  数值特征值 {z:.4f}（vs 理论 {th:+.4f}，|Re|={abs(z.real):.5f}、|Im|={abs(z.imag):.5f}）" + (" ✓" if okz else " ⚠"))
zeros = [z for z in eig if abs(z) < TOL]                # 理论谱 {0, ±i√3/3}：恰一个 0 + 一对纯虚
pures = [z for z in eig if abs(z) >= TOL]
ok_e3b = len(zeros) == 1 and len(pures) == 2 and all(abs(z.real) < TOL and abs(abs(z.imag) - 0.57735) < TOL for z in pures)
DT_RPS, STEPS_RPS = 0.02, 2500           # RPS 用更细步长减轻欧拉漂移（闭轨对离散化敏感，诚实标注）
orbits = []
for x0 in ([0.5, 0.3, 0.2], [0.2, 0.5, 0.3], [0.6, 0.2, 0.2]):
    x = np.array(x0, dtype=float)
    traj = [x.copy()]
    for _ in range(STEPS_RPS):
        x = rps_step(x, DT_RPS)
        traj.append(x.copy())
    orbits.append(np.array(traj))
x_end = orbits[0][-1]
t_avg = orbits[0].mean(axis=0)
print(f"  轨线1 终值 ({x_end[0]:.3f}, {x_end[1]:.3f}, {x_end[2]:.3f})——远离中心（行为频率不收敛）；时间平均 ({t_avg[0]:.3f}, {t_avg[1]:.3f}, {t_avg[2]:.3f}) vs 1/3（|偏差| {np.abs(t_avg - 1/3).max():.3f}，容差 0.02）")
ok_e3c = np.abs(t_avg - 1 / 3).max() < 0.02
print(f"→ E3b 对拍：特征值纯虚 ±0.5774i {'✓' if ok_e3b else '⚠'}；E3c 时间平均 → 中心（'行为不收敛、平均趋向均衡'，50 章第三堵墙）—— " + ("全绿 ✓" if ok_e3b and ok_e3c else "⚠ 如实标注"))
print("  诚实标注：零和 RPS 的理论图像是闭轨族（中心），欧拉离散化会让轨线缓慢内外漂移（数值伪影，非理论）——"
      "步长已压细并加单纯形护栏；'孤立极限环'要 a≠1 的广义 RPS（Hofbauer-Sigmund），此处演示的是中心型。")

# ======================================================================
# ipd_evo.png：1×3——(a) 锦标赛得分条形 (b) Moran 固定概率 vs 初始比例 (c) RPS 相图 + 鹰鸽内嵌
# ======================================================================
fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.9))

# (a) 锦标赛条形
ax = axes[0]
names = [n.replace("Win-Stay Lose-Shift", "WSLS").replace("Tit For Tat", "TFT") for n, _, _ in e1_rows]
vals = [v for _, v, _ in e1_rows]
colors = ["tab:blue" if n else "tab:red" for _, _, n in e1_rows]
bars = ax.bar(range(len(vals)), vals, width=0.68, color=colors, alpha=0.88)
for bar, v in zip(bars, vals):
    ax.annotate(f"{v:.3f}", xy=(bar.get_x() + bar.get_width() / 2, v), xytext=(0, 3),
                textcoords="offset points", ha="center", fontsize=7.5, rotation=90)
ax.set_xticks(range(len(vals)))
ax.set_xticklabels(names, rotation=40, ha="right", fontsize=8)
ax.set_ylabel("每轮每对手平均得分（turns=200, reps=50）")
ax.set_title("E1 · axelrod 十策略锦标赛：\n善良阵营（蓝）vs 不善良阵营（红）", fontsize=10.5)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="tab:blue", label=f"善良策略（均值 {nice_mean:.3f}）"),
                   Patch(color="tab:red", label=f"不善良（均值 {nasty_mean:.3f}）")], fontsize=8.5, loc="upper right")

# (b) Moran 固定概率
ax = axes[1]
xs = [r[0] for r in e2_rows]
ps = [r[1] for r in e2_rows]
ses = [r[2] for r in e2_rows]
ax.plot([0, 1], [0, 1], "k--", lw=1.3, label="中性漂移基线 p = i/N")
ax.errorbar(xs, ps, yerr=2 * np.array(ses), fmt="o", ms=7, capsize=4, color="tab:blue", label="TFT 入侵 ALLD 实测（±2se，30 seeds/档）")
ax.annotate("单挑输（0.995 < 1.02/轮）\n群体赢：合作红利随比例放大", xy=(0.5, 0.60), fontsize=8.5, color="tab:blue")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
ax.set_xlabel("TFT 初始比例 i/N")
ax.set_ylabel("TFT 固定概率（Moran BD，N=10）")
ax.set_title("E2 · Moran 入侵：实测固定概率\n压中性基线 i/N（频率依赖选择）", fontsize=10.5)
ax.legend(fontsize=8, loc="upper left")

# (c) RPS 单纯形相图 + 鹰鸽内嵌
ax = axes[2]
V = np.array([[0, 0], [0.5, np.sqrt(3) / 2], [1, 0]])   # 顶点：策略1(R), 2(P), 3(S)
def to_simplex(x):
    return x[0] * V[0] + x[1] * V[1] + x[2] * V[2]
tri = plt.Polygon(V, fill=False, color="gray", lw=1.2)
ax.add_patch(tri)
for orb, c in zip(orbits, ["tab:blue", "tab:orange", "tab:green"]):
    pts = np.array([to_simplex(p) for p in orb[::20]])
    ax.plot(pts[:, 0], pts[:, 1], color=c, lw=1.2, alpha=0.85)
    ax.annotate("", xy=pts[-4], xytext=pts[-8], arrowprops=dict(arrowstyle="->", color=c, lw=1.4))
ctr = to_simplex([1 / 3, 1 / 3, 1 / 3])
ax.plot(*ctr, "r*", ms=13)
ax.annotate("中心 (1/3,1/3,1/3)\n特征值 ±i√3/3 纯虚\n→ 闭轨，无 ESS", xy=ctr, xytext=(0.72, 0.60),
            fontsize=8, color="red", arrowprops=dict(arrowstyle="->", color="red", lw=1.0))
for v, lab, dxy in [(V[0], "策略1", (-0.03, -0.07)), (V[1], "策略2", (-0.03, 0.01)), (V[2], "策略3", (0.0, -0.07))]:
    ax.annotate(lab, xy=v, xytext=(v[0] + dxy[0], v[1] + dxy[1]), fontsize=9)
ax.set_xlim(-0.12, 1.12); ax.set_ylim(-0.12, 0.98)
ax.axis("off")
ax.set_title("E3 · 复制动态：RPS 闭轨（相图，欧拉 dt=0.02）\n行为频率转圈、时间平均 → 中心（内嵌：鹰鸽收敛）", fontsize=10.5)
axin = ax.inset_axes([0.02, 0.55, 0.38, 0.40])   # 左上空白区（三角左边缘外侧）——不遮三个顶点标签
for traj in hd_tracks:
    axin.plot(np.arange(len(traj)) * DT, traj, lw=1.4)
axin.axhline(0.5, color="red", ls="--", lw=1.1)
axin.set_title("鹰鸽 $\\dot{x}=x(1-x)(1-2x)$：x*=0.5", fontsize=7.5)
axin.tick_params(labelsize=6.5)
axin.set_xlabel("t", fontsize=7); axin.set_ylabel("x（鹰比例）", fontsize=7)

fig.suptitle("lab05 · 重复博弈与演化：axelrod IPD 锦标赛（10 策略 × 50 reps）/ Moran 入侵固定概率 / 手写复制动态（鹰鸽收敛 + RPS 闭轨）", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.94))
OUT = Path(__file__).resolve().parent / "ipd_evo.png"
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
print("总结：E1 锦标赛如实记录（善良分裂线）｜E2 各档压中性基线 " + ("✓" if ok_e2 else "⚠") +
      f"（2se 显著 {n_sig}/5）｜E3 鹰鸽 x*=0.5 " + ("✓" if ok_e3a else "⚠") + "、特征值 ±0.5774i " + ("✓" if ok_e3b else "⚠") +
      "、时间平均→中心 " + ("✓" if ok_e3c else "⚠"))
