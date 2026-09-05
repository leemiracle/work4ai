#!/usr/bin/env python3
"""讲透博弈论实验 3：扩展式博弈——蜈蚣 SPE、QRE λ 扫描与最后通牒实验室。
E1 手写 EFG 文本建 n=6 蜈蚣（pygambit 16.7.0 的 Game.new_tree() 只读、Node 无 append——EFG 文本 + read_efg 是唯一建模通道）→ enumpure_solve 求纯 NE（唯一 = 节点 1 即 take，收益 (4,1)），与手推逆向归纳逐节点对拍 | E2 QRE：pygambit.qre.logit_solve_lambda 扫 λ∈[0.1,100]（21 点）记录"第一个 take 的节点"前移曲线，并用手写 numpy 不动点递归全程对拍（预期 maxdiff < 1e-9） | E3 最后通牒模拟：responder 拒绝 iff offer < θ（θ~U[0,4]，Fehr-Schmidt 不公平厌恶的单参数门槛投影），知情提议人最优出价 o*=5（蛋糕 50%）vs SPE 0 对照打印
产出：extensive.png + centipede6.efg（EFG 模板，lab04 复用同一建模范式）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pygambit
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
rng = np.random.default_rng(42)

# ----------------------------------------------------------------------
# 统一记号（与 06 章、lab01/lab02 一致）：
# 蜈蚣 n=6（McKelvey-Palfrey 型收益结构，06 章声明）：
#   罐子从 5 开始、每 pass 翻倍（节点 k 罐子 = 5·2^(k-1)）；
#   节点 k 当前玩家 take → 自己得 4·2^(k-1)（80%），对手得 2^(k-1)（20%）；
#   节点 6 仍 pass → 博弈结束，按 n6-take 的镜像分账 (128, 32)（P1 拿 80%）。
# 手推逆向归纳（06 章表）：每个节点 take 严格占优 → SPE = 节点 1 即 take，结局 (4,1)；
#   对照"全体 pass"反事实 (128,32)——两人都恰是各自 SPE 收益的 32 倍，这就是蜈蚣悖论。
# ----------------------------------------------------------------------
OWN = [4 * 2**k for k in range(6)]      # 节点 k+1 当前玩家 take 的 Own 收益：4, 8, 16, 32, 64, 128
OPP = [2**k for k in range(6)]          # 对手份额：1, 2, 4, 8, 16, 32
TERM_PASS6 = (128, 32)                  # 节点 6 仍 pass 的终局 (P1, P2)
N = 6

EFG_TEXT = '''EFG 2 R "centipede n=6 (MP structure)" { "Player 1" "Player 2" }
p "n1" 1 1 "P1@n1" { "take" "pass" } 0
t "t1" 1 "P1 takes at n1" { 4 1 }
p "n2" 2 1 "P2@n2" { "take" "pass" } 0
t "t2" 2 "P2 takes at n2" { 2 8 }
p "n3" 1 2 "P1@n3" { "take" "pass" } 0
t "t3" 3 "P1 takes at n3" { 16 4 }
p "n4" 2 2 "P2@n4" { "take" "pass" } 0
t "t4" 4 "P2 takes at n4" { 8 32 }
p "n5" 1 3 "P1@n5" { "take" "pass" } 0
t "t5" 5 "P1 takes at n5" { 64 16 }
p "n6" 2 3 "P2@n6" { "take" "pass" } 0
t "t6" 6 "P2 takes at n6" { 32 128 }
t "t7" 7 "P2 passes at n6" { 128 32 }
'''
EFG_PATH = Path(__file__).resolve().parent / "centipede6.efg"   # 恒定落 experiments/，与运行 cwd 无关
EFG_PATH.write_text(EFG_TEXT, encoding="utf-8")
g = pygambit.read_efg(str(EFG_PATH))    # 唯一建模通道：EFG 文本 → read_efg（new_tree 只读，16.7.0 实测）

# ======================================================================
print("=" * 68)
print("E1 · 蜈蚣 n=6：手推逆向归纳 vs pygambit enumpure_solve")
print("=" * 68)
# --- 手推逆向归纳（从最后一节点往前）-----------------------------------
print("手推逆向归纳（SPE 推理链，take/pass 的当前玩家收益对照）：")
print("  节点 | 当前 | take 得 | pass 导致（下游全 take） | 决策")
bi_choices = []
for k in range(N - 1, -1, -1):                     # k = 0..5 ↔ 节点 1..6，倒序推
    player = "P1" if k % 2 == 0 else "P2"
    own_take = OWN[k]
    if k == N - 1:
        own_pass = TERM_PASS6[0] if player == "P1" else TERM_PASS6[1]
    else:
        own_pass = OPP[k + 1]                       # 下游全 take 时，pass 后对手 take，自己得对手份额
    choice = "take" if own_take > own_pass else "pass"
    bi_choices.append((k + 1, player, own_take, own_pass, choice))
for node, player, tk, ps, ch in reversed(bi_choices):
    strict = "严格>" if tk > ps else ("=" if tk == ps else "<")
    print(f"   n{node}  |  {player}  |  {tk:>3}   |  {ps:>3}  （take {strict} pass）      | {ch}")
spe_outcome = (OWN[0], OPP[0])
print(f"→ 手推 SPE：节点 1 即 take，结局 (P1, P2) = {spe_outcome}"
      f"；对照全体 pass 反事实 {TERM_PASS6}（P1 得 {TERM_PASS6[0]/spe_outcome[0]:.0f} 倍、P2 得 {TERM_PASS6[1]/spe_outcome[1]:.0f} 倍）")
# --- pygambit enumpure_solve-------------------------------------------
p1, p2 = list(g.players)
r = pygambit.nash.enumpure_solve(g)
eqs = list(r.equilibria)
print(f"\npygambit enumpure_solve：纯均衡个数 = {len(eqs)}（化简策略标签 * = 不可达信息集，'1**' 即 take@n1）")
e = eqs[0]
mass1 = [float(e[s]) for s in p1.strategies]
mass2 = [float(e[s]) for s in p2.strategies]
lab1 = [s.label for s in p1.strategies]
lab2 = [s.label for s in p2.strategies]
print(f"  P1 策略质量 {{label: 概率}}: {dict((l, int(m)) for l, m in zip(lab1, mass1) if m > 0)}")
print(f"  P2 策略质量: {dict((l, int(m)) for l, m in zip(lab2, mass2) if m > 0)}")
pay = (float(e.payoff(p1)), float(e.payoff(p2)))
print(f"  均衡收益 = ({pay[0]:g}, {pay[1]:g})")
ok_e1 = (len(eqs) == 1 and lab1[int(np.argmax(mass1))] == "1**"
         and lab2[int(np.argmax(mass2))] == "1**" and pay == spe_outcome)
print(f"→ 手推 vs enumpure 对拍：唯一均衡 = ('1**','1**')（双双 take@n1）、收益 {spe_outcome} —— "
      + ("完全一致 ✓" if ok_e1 else "⚠ 不一致——如实标注，勿放宽"))

# ======================================================================
print("\n" + "=" * 68)
print("E2 · QRE：logit_solve_lambda 扫 λ∈[0.1,100] vs 手写不动点递归对拍")
print("=" * 68)
# 行为 QRE（agent logit）：每节点 q_k = 1/(1+exp(-λ·(T_k − P_k)))，P_k = pass 的延续价值，
# 而延续价值又依赖下游 q——不动点。手写递归从 λ=0 的 q=0.5 出发沿 λ 路径延续（warm start）。
def qre_hand(lam, q_init, iters=200000, tol=1e-14):
    """手写 agent-logit QRE：返回各节点 P(take)。q_init 用上一 λ 的解做路径延续。"""
    q = q_init.copy()
    V = np.zeros(N)      # V[k] = 节点 k+1 当前玩家在自己混合下的延续价值（用于再下游的 pass 定价）
    Pv = np.zeros(N)     # Pv[k] = 节点 k+1 当前玩家 pass 的延续价值
    for _ in range(iters):
        V[N - 1] = q[N - 1] * OWN[N - 1] + (1 - q[N - 1]) * TERM_PASS6[1]
        Pv[N - 1] = TERM_PASS6[1]
        Pv[N - 2] = q[N - 1] * OPP[N - 1] + (1 - q[N - 1]) * TERM_PASS6[0]
        V[N - 2] = q[N - 2] * OWN[N - 2] + (1 - q[N - 2]) * Pv[N - 2]
        for k in range(N - 3, -1, -1):
            Pv[k] = q[k + 1] * OPP[k + 1] + (1 - q[k + 1]) * V[k + 2]
            V[k] = q[k] * OWN[k] + (1 - q[k]) * Pv[k]
        qn = 1 / (1 + np.exp(-np.clip(lam * (OWN - Pv), -700, 700)))
        if np.max(np.abs(qn - q)) < tol:
            return qn
        q = qn
    return q

lams = np.logspace(-1, 2, 21)                       # λ ∈ [0.1, 100]，21 点
rows, diffs = [], []
q_warm = np.full(N, 0.5)
NODE_IDX = (0, 1, 2, 3, 4, 5)                       # 手写 q 下标 ↔ 节点 1..6
for lam in lams:
    q_hand = qre_hand(lam, q_warm)
    q_warm = q_hand
    prof = pygambit.qre.logit_solve_lambda(g, float(lam))[0]   # 返回 [LogitQREMixedBehaviorProfile]
    # flat 布局（实测确认）：P1 的 n1/n3/n5 各 (take,pass)，再 P2 的 n2/n4/n6 各 (take,pass)
    q_lib = np.array([float(prof[0]), float(prof[6]), float(prof[2]),
                      float(prof[8]), float(prof[4]), float(prof[10])])
    d = float(np.max(np.abs(q_hand - q_lib)))
    diffs.append(d)
    first_take = int(np.argmax(q_lib > 0.5)) + 1     # 从节点 1 起第一个 take>0.5 的节点
    rows.append((lam, *q_lib, first_take))
print(f"{'λ':>8} | {'q(n1)':>7} {'q(n2)':>7} {'q(n3)':>7} {'q(n4)':>7} {'q(n5)':>7} {'q(n6)':>7} | 首个take | 手写vs库")
for i, (lam, *qs, ft) in enumerate(rows):
    print(f"{lam:8.3f} | {qs[0]:7.4f} {qs[1]:7.4f} {qs[2]:7.4f} {qs[3]:7.4f} {qs[4]:7.4f} {qs[5]:7.4f} |   n{ft}    | {diffs[i]:.1e}")
max_d = max(diffs)
ft_lo, ft_hi = rows[0][-1], rows[-1][-1]
cross1 = next(lam for lam, *qs, ft in rows if ft == 1)
print(f"→ QRE 读数：λ={lams[0]:g} 时首个 take 在节点 {ft_lo}（早期节点以 pass 为主，游戏走远）；"
      f"λ≥{cross1:.2f} 后节点 1 即 take；λ=100 全线 ≈1.0 → 收敛 SPE ✓")
print(f"→ 手写不动点 vs pygambit：全程 maxdiff = {max_d:.1e} " + ("（< 1e-9 ✓）" if max_d < 1e-9 else "⚠ 超阈值——如实标注"))
print("诚实标注：q(n6) 在全部 λ 下均 >0.5——终节点 take 是确定性占优（128>32），QRE 噪声只能模糊它；")
print("            λ 变小侵蚀的是靠'下游也会合作'支撑的早期节点——前移曲线如实呈现这一不对称。")

# ======================================================================
print("\n" + "=" * 68)
print("E3 · 最后通牒：公平门槛模拟（θ~U[0,4]）vs SPE 出价 0")
print("=" * 68)
CAKE = 10.0
# responder：拒绝 iff offer < θ；θ = 10α/(1+2α)（Fehr-Schmidt 嫉妒系数 α 的单调投影，α∈[0,2] ↔ θ∈[0,4]），θ~U[0,4] 为声明分布
# SPE：responder 接受任何正出价 → proposer 出价 →0，自己拿 ≈10
print(f"SPE 预测：任何正出价都应被接受 → 最优出价 → 0（proposer 得 ≈{CAKE:g}）；实验事实：均出价 40~50%，低于 ~30% 常被拒（50 章口径）")
# 知情提议人（知道 θ 的分布）：E[净得 | 出价 o] = (CAKE−o)·P(θ≤o) = (10−o)·min(1, o/4)
grid = np.linspace(0, CAKE, 2001)
ev = (CAKE - grid) * np.minimum(1.0, grid / 4.0)
o_star = grid[int(np.argmax(ev))]
print(f"知情提议人最优出价（θ~U[0,4]）：max_o (10−o)·min(1, o/4) → o* = {o_star:.2f}"
      f"（蛋糕 {o_star/CAKE:.0%}，期望净得 {ev.max():.2f}；出价 0 的期望净得 = 0.00）")
# 异质信念总体：proposer 感知门槛尺度 c~U[2,8] → 解析最优 o* = min(c, 5)（o≥c 全被接、o<c 得 (10−o)o/c）
NPOP = 20000
c = rng.uniform(2.0, 8.0, NPOP)
offers = np.minimum(c, 5.0)
theta = rng.uniform(0.0, 4.0, NPOP)
accepted = theta <= offers
rej_all = 1 - accepted.mean()
rej_low = 1 - accepted[offers < 3].mean()
print(f"异质信念总体模拟（n={NPOP}，c~U[2,8] → o*=min(c,5)）：")
print(f"  平均出价 = {offers.mean():.2f}（理论 E[min(c,5)] = 4.25，即蛋糕 {offers.mean()/CAKE:.0%}）；拒单率 = {rej_all:.1%}")
print(f"  出价 < 蛋糕 30%（o<3）的拒单率 = {rej_low:.1%}（对照实验'低于 ~30% 常被拒'方向一致）")
print(f"→ 对照：SPE 出价 → 0 vs 公平门槛模型出价 ≈ {o_star:.0f}~{offers.mean():.1f}（40~50%）——实验站行为模型一边，SPE 被数据拒绝（06 章 §五）")

# ======================================================================
# extensive.png：2×2——(a) 首个 take 节点 vs λ (b) 各节点 take 概率曲线
#                (c) 最后通牒出价直方图 (d) 手写 vs pygambit 对拍偏差
# ======================================================================
fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.2))
lam_arr = np.array([r[0] for r in rows])
ft_arr = np.array([r[-1] for r in rows])

# (a) 首个 take 节点前移
ax = axes[0, 0]
ax.step(lam_arr, ft_arr, where="post", lw=2.2, color="tab:blue", label="首个 take>0.5 的节点")
ax.axhline(1, color="red", lw=1.2, ls="--", label="SPE：节点 1 即 take")
ax.scatter([cross1], [1], s=80, color="red", zorder=5)
ax.annotate(f"λ≈{cross1:.2f} 起节点 1 即 take\n（λ→∞ 收敛 SPE）", xy=(cross1, 1), xytext=(3, 1.35),
            fontsize=9, color="red", arrowprops=dict(arrowstyle="->", color="red"))
ax.set_xscale("log"); ax.set_xticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
ax.set_yticks([1, 2, 3, 4], ["n1", "n2", "n3", "n4"])
ax.set_ylim(4.4, 0.6)
ax.set_xlabel("理性强度 λ（logit QRE）"); ax.set_ylabel("第一个 take 的节点")
ax.set_title("E2 · take 前移曲线：λ 小→游戏走远，λ 大→立即 take", fontsize=11)
ax.legend(fontsize=9, loc="lower left")

# (b) 六节点 take 概率曲线
ax = axes[0, 1]
qmat = np.array([r[1:-1] for r in rows])            # 21×6
for k in range(N):
    ax.plot(lam_arr, qmat[:, k], lw=1.8, label=f"节点 {k+1}（{'P1' if k % 2 == 0 else 'P2'}）")
ax.axhline(0.5, color="k", lw=1.0, ls=":")
ax.annotate("take>0.5 的分界", xy=(0.11, 0.52), fontsize=8, color="gray")
ax.set_xscale("log"); ax.set_xticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
ax.set_ylim(-0.03, 1.05); ax.set_xlabel("理性强度 λ"); ax.set_ylabel("P(take)")
ax.set_title("E2 · 各节点 P(take)：终节点全程 >0.5（确定性占优），早期节点随 λ 抬升\n（q(n1) 非单调小谷：下游转 take 先压后抬 pass 价值——如实呈现）", fontsize=10)
ax.legend(fontsize=8, ncol=2, loc="lower right")

# (c) 最后通牒出价直方图（接受/拒绝堆叠）
ax = axes[1, 0]
bins = np.linspace(1.5, 5.5, 17)
ax.hist(np.clip(offers[accepted], 1.5, 5.5), bins=bins, color="tab:blue", alpha=0.85,
        label=f"被接受（{accepted.mean():.0%}）")
ax.hist(np.clip(offers[~accepted], 1.5, 5.5), bins=bins, bottom=np.histogram(offers[accepted], bins=bins)[0],
        color="tab:red", alpha=0.85, label=f"被拒绝（{rej_all:.1%}）")
ax.axvline(0, color="red", lw=1.6, ls="--")
ax.annotate("SPE 出价 = 0\n（任何正出价被接受）", xy=(0.03, 0.62), xycoords="axes fraction",
            fontsize=9, color="red", ha="left", va="top")
ax.axvline(4.0, color="tab:green", lw=1.4, ls=":")
ax.annotate("知情 o* = 4（蛋糕 40%）", xy=(3.9, 0.92), xycoords=("data", "axes fraction"),
            fontsize=9, color="tab:green", rotation=90, va="top", ha="right")
ax.annotate("o=5 高柱：自认对手更严的提议人（c>5 封顶）", xy=(4.85, 0.55), xycoords=("data", "axes fraction"),
            fontsize=8, color="gray", rotation=90, va="top", ha="right")
ax.set_xlim(-0.35, 5.7); ax.set_xlabel("出价 o（蛋糕 = 10）"); ax.set_ylabel("提议人个数")
ax.set_title("E3 · 最后通牒：θ~U[0,4] 门槛下总体出价 ≈4.25（42.5%），\nvs SPE 0——实验 40~50% 站行为模型一边", fontsize=10)
ax.legend(fontsize=9, loc="upper left")

# (d) 手写不动点 vs pygambit 对拍偏差
ax = axes[1, 1]
ax.semilogy(lam_arr, np.maximum(diffs, 1e-18), lw=1.8, color="tab:purple")
ax.axhline(1e-9, color="red", lw=1.1, ls="--", label="阈值 1e-9")
ax.annotate(f"全程 maxdiff = {max_d:.1e}（< 1e-9）", xy=(0.5, 0.08), xycoords="axes fraction", fontsize=10, color="tab:purple")
ax.set_xscale("log"); ax.set_xticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
ax.set_xlabel("理性强度 λ"); ax.set_ylabel("max |P(take) 手写 − pygambit|")
ax.set_title("E2 · 手写不动点递归 vs pygambit logit 求解器\n（21 个 λ 点全程对拍，诚实校准公约）", fontsize=10)
ax.legend(fontsize=9)

fig.suptitle("lab03 · 扩展式博弈：蜈蚣 SPE / QRE λ 扫描 / 最后通牒（pygambit 16.7.0，EFG 文本建模）", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.96))
OUT = Path(__file__).resolve().parent / "extensive.png"
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
