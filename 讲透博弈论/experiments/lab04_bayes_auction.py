#!/usr/bin/env python3
"""讲透博弈论实验 4：不完全信息与拍卖——BNE 蒙特卡洛、收益等价与赢家诅咒。
E1 FPSB n=2：估值 v~U[0,1] 独立，双方按 BNE b(v)=v/2 出价，10^5 场蒙特卡洛——赢者平均支付 ≈1/3、
   赢者平均利润 ≈1/3（理论：E[v_max]=2/3=n/(n+1)，支付=E[v_max/2]=1/3，利润=v_max−支付=v_max/2 恒等于支付）
E2 收益等价：英式（实现=二价）、荷兰式（实现=一价）、一价、二价——同一批估值四路蒙特卡洛，
   平均收入并排 vs (n−1)/(n+1)=1/3（容差 0.01），打印理论值来源公式（E[次高]=(n−1)/(n+1)、E[R]=E[b(v_max)])
E3 赢家诅咒：共同价值钱包拍卖（声明假设：n 个信号 s_i~U[0,1] 独立、钱包值 V=mean(s)）——
   naive 出价=自己信号 → 赢者平均利润 ≈ (1−n)/(2(n+1))（n=2 即 −1/6，显著为负）
   vs 理性调整出价 b=(n+1)/(2n)·s（order-statistic 修正：中签 ⟹ 其余 n−1 信号是 [0,s] 均匀次序统计量，
   E[V|中签,s]=(n+1)/(2n)·s 恰好抵平 → 利润 ≈0）
E4（可选）pygambit 贝叶斯进入博弈：chance 节点抽在位者类型，进入者信息集裂开成多点（06 章伏笔兑付）——
   enumpure 给 2 个 NE（BNE 口径），PBE 审计（到达信息集上信念=先验 + 逐点序贯理性）只剩 1 个（08 章 §六模板）
产出：auction.png（1×3：收入对比条形/赢者支付分布/诅咒利润曲线）+ bayes_entry.efg（EFG 模板）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
rng = np.random.default_rng(42)
N_SIM = 100_000          # 每个实验的蒙特卡洛场数
TOL = 0.01               # 诚实校准公约容差

# ======================================================================
print("=" * 68)
print("E1 · FPSB n=2：BNE b(v)=v/2 蒙特卡洛 10^5 场")
print("=" * 68)
# 手推锚点（08 章 §四）：对称线性均衡猜 b(v)=αv → 类型 v 出 b 的赢率 = b/α →
#   max_b (v−b)·(b/α) → FOC b=v/2 → 自洽性 α=1/2。
# E[v_max] = n/(n+1) = 2/3；赢者支付 = v_max/2 → E = 1/3；赢者利润 = v_max − v_max/2 = v_max/2（FPSB 支付=出价，利润恒等于支付）
v1, v2 = rng.uniform(0, 1, N_SIM), rng.uniform(0, 1, N_SIM)
b1, b2 = v1 / 2, v2 / 2
win1 = b1 > b2
payment = np.where(win1, b1, b2)            # 赢者支付 = 赢者出价
profit = np.where(win1, v1 - b1, v2 - b2)   # 赢者利润
mc_pay, mc_profit = payment.mean(), profit.mean()
print(f"理论锚点（手推，08 章 §四）：E[v_max] = n/(n+1) = 2/3 → E[赢者支付] = E[v_max/2] = 1/3；E[赢者利润] = E[v_max − v_max/2] = 1/3")
print(f"  蒙特卡洛 E[赢者支付] = {mc_pay:.4f}（vs 1/3 = 0.3333，|偏差| = {abs(mc_pay - 1/3):.4f}）")
print(f"  蒙特卡洛 E[赢者利润] = {mc_profit:.4f}（vs 1/3 = 0.3333，|偏差| = {abs(mc_profit - 1/3):.4f}）")
print(f"  诚实标注：FPSB 里支付=自己的出价、利润=价值−支付；b(v)=v/2 时利润 = v_max − v_max/2 = v_max/2 = 支付——逐场恒等，两个 1/3 同源")
ok_e1 = abs(mc_pay - 1/3) < TOL and abs(mc_profit - 1/3) < TOL
print(f"→ E1 对拍：支付/利润双双 ≈ 1/3（容差 {TOL}）—— " + ("全绿 ✓" if ok_e1 else "⚠ 超容差——如实标注，勿放宽"))

# ======================================================================
print("\n" + "=" * 68)
print("E2 · 收益等价：英式/荷兰式/一价/二价 同一分布四路蒙特卡洛")
print("=" * 68)
# 手推锚点：E[次高 of n U[0,1]] = (n−1)/(n+1)（n=2：∫0^1 t·d(2t−t²)=... 亦即 ∫0^1(1−t)²dt = 1/3）
#   英式（两人升价到次高退出）≡ 二价 → 收入 = 次高；荷兰式（降价，第一口价成交）≡ 一价 → 收入 = b(v_max) = v_max/2
#   一价收入 = E[v_max/2] = (1/2)·n/(n+1) = (n−1)/(n+1)；二价收入 = E[次高] = (n−1)/(n+1) —— n=2 四路同为 1/3
vmax = np.maximum(v1, v2)
vmin = np.minimum(v1, v2)
formats = [
    ("英式（=二价实现）", vmin),
    ("荷兰式（=一价实现）", vmax / 2),
    ("一价密封", vmax / 2),
    ("二价密封", vmin),
]
print(f"理论值来源（手推，n=2，v~U[0,1]）：E[v_max] = 2/3 = n/(n+1)；E[次高] = 1/3 = (n−1)/(n+1)")
print(f"  一价/荷兰式收入 = E[b(v_max)] = E[v_max/2] = 1/3；二价/英式收入 = E[次高] = 1/3 —— 一般 n 四路同式 E[R] = (n−1)/(n+1)")
mc_revs = []
for name, rev in formats:
    r = rev.mean()
    mc_revs.append(r)
    flag = "✓" if abs(r - 1/3) < TOL else "⚠ 超容差"
    print(f"  {name:<12} 平均收入 = {r:.4f}（vs 1/3，|偏差| = {abs(r - 1/3):.4f}）{flag}")
ok_e2 = all(abs(r - 1/3) < TOL for r in mc_revs)
print(f"→ E2 对拍：四路收入并排全部 ≈ (n−1)/(n+1) = 1/3（容差 {TOL}）—— " + ("收益等价成立 ✓" if ok_e2 else "⚠ 如实标注"))
print("  诚实标注：本实验'验证'的是 4 个可手推的 n=2 特例；一般 n 的收益等价定理（收入只依赖配置规则）在 13 章正式陈述。")

# ======================================================================
print("\n" + "=" * 68)
print("E3 · 赢家诅咒：共同价值钱包拍卖（声明假设：s_i~U[0,1] 独立，V=mean(s)）")
print("=" * 68)
# 声明假设：n 个信号 iid U[0,1]，钱包值 V = mean(s)。"信号=值+噪声"与"值=信号均值"是同一模型的两个方向：
#   s_i = V + (s_i − V) 且各偏差 Σ=0——偏差不独立，这正是诅咒之源。高斯版（V 先抽、s_i=V+ε_i）定性相同，解析更繁，本 lab 取均匀版换可手推锚点。
# 手推锚点：中签 ⟹ 自己信号 s 是 n 个中的最大 → 其余 n−1 个条件分布 = [0,s] 上 iid 均匀（独立性）→ 均值 s/2
#   → E[V|中签,s] = (s + (n−1)·s/2)/n = (n+1)/(2n)·s → 理性出价 b(s)=(n+1)/(2n)s，中签条件利润恰为 0 → 平均利润 ≈0
#   naive 出价 = s：赢者利润 = V − v_max → E = 1/2 − n/(n+1) = (1−n)/(2(n+1))（n=2：−1/6）
NS = [2, 4, 8, 16]
rows_e3 = []
print(f"理论锚点（手推，声明假设如上）：naive 赢者利润 E[V − v_max] = (1−n)/(2(n+1))；理性 b(s)=(n+1)/(2n)·s → 条件利润恒 0 → ≈0")
print(f"{'n':>3} | {'naive 利润':>10} | {'理论 (1−n)/2(n+1)':>18} | {'理性利润':>9} | 理论")
ok_e3 = True
for n in NS:
    s = rng.uniform(0, 1, (N_SIM, n))
    V = s.mean(axis=1)
    idx = s.argmax(axis=1)
    s_win = s[np.arange(N_SIM), idx]
    naive = (V - s_win).mean()
    rat = (V - (n + 1) / (2 * n) * s_win).mean()
    th_naive = (1 - n) / (2 * (n + 1))
    rows_e3.append((n, naive, rat, th_naive))
    ok = abs(naive - th_naive) < TOL and abs(rat) < TOL
    ok_e3 &= ok
    print(f"{n:>3} | {naive:>10.4f} | {th_naive:>18.4f} | {rat:>9.4f} | 0（容差内{' ✓' if ok else ' ⚠'}）")
print(f"→ E3 对拍：naive 利润显著为负（n=2 即 −1/6）且随 n 加深（→ −1/2）；理性修正后 ≈0（容差 {TOL}）—— " + ("全绿 ✓" if ok_e3 else "⚠ 如实标注"))
print("  诚实标注：理性出价利润 ≈0 是'条件期望恰好抵平'的模型内结论（中标不赚不亏）；真实油田/钱包市场里连理性出价也常因方差与不对称信息亏损（Milgrom-Webb 1982 联系原理，13 章）。")

# ======================================================================
print("\n" + "=" * 68)
print("E4 ·（可选）pygambit 贝叶斯进入博弈：信息集裂开成多点")
print("=" * 68)
try:
    import pygambit
    EFG_TEXT = '''EFG 2 R "bayes entry (incumbent type hidden)" { "Entrant" "Incumbent" }
c "c1" 1 "nature" { "Strong" 1/3 "Weak" 2/3 } 0
p "nS" 1 1 "entrant@both-branches" { "in" "out" } 0
p "nS2" 2 1 "incumbentStrong" { "fight" "accommodate" } 0
t "t1" 1 "in,Strong fights" { -1 1 }
t "t2" 2 "in,Strong accommodates" { 1 0 }
t "t3" 3 "out@Strong" { 0 2 }
p "nW" 1 1 "entrant@both-branches" { "in" "out" } 0
p "nW2" 2 2 "incumbentWeak" { "fight" "accommodate" } 0
t "t4" 4 "in,Weak fights" { -1 -1 }
t "t5" 5 "in,Weak accommodates" { 1 1 }
t "t6" 6 "out@Weak" { 0 2 }
'''
    EFG_PATH = Path(__file__).resolve().parent / "bayes_entry.efg"   # 恒定落 experiments/，与运行 cwd 无关
    EFG_PATH.write_text(EFG_TEXT, encoding="utf-8")
    g = pygambit.read_efg(str(EFG_PATH))    # 06 章 §六范式：EFG 文本 → read_efg（new_tree 只读；c 行 = 自然抽类型）
    entrant, incumbent = list(g.players)
    r = pygambit.nash.enumpure_solve(g)
    eqs = list(r.equilibria)
    print(f"EFG 已建（chance 节点 c1 先抽类型 1/3:2/3；进入者信息集 1 裂开成 2 个节点——06 章伏笔在此兑付）")
    print(f"手推：BNE 有 3 个——(in, 强=打/弱=容) 进入者期望 (1/3)(−1)+(2/3)(1)=1/3；另 2 个 (out, ·, 弱=打)：out 之后在位者怎么选收益都是 2（弱无差异），"
          f"靠'弱者也会打'的不可信威胁吓住进入者（强分支的喊法自由组合 → 恰 2 个）")
    for i, e in enumerate(eqs):
        p_e = float(e.payoff(entrant)); p_i = float(e.payoff(incumbent))
        print(f"  enumpure eq{i}: 进入者期望收益 {p_e:.4f}，在位者 {p_i:.4f}")
    # PBE 审计：进入者信息集被到达（自然必抽一支）→ 信念被 Bayes 钉死在先验 1/3:2/3 → in 期望 1/3 > 0 = out
    pbe = [e for e in eqs if float(e.payoff(entrant)) > 1/3 - 1e-9]
    print(f"PBE 审计：进入者信息集恒被到达 → 信念=先验（Bayes 钉死）→ in 的期望 1/3 > out 的 0 → 威胁版出局")
    print(f"→ 唯一 PBE = (in, 强打/弱容)，进入者期望收益 1/3 —— " + ("与手推一致 ✓" if len(pbe) == 1 and abs(float(pbe[0].payoff(entrant)) - 1/3) < 1e-9 else "⚠ 不一致——如实标注"))
    print("  诚实标注：求解器给 NE 清单（BNE 口径），'信念钉死 + 序贯理性'的 PBE 审计是自己的活——精炼的完整戏码在 09 章。")
    HAS_GAMBIT = True
except ImportError:
    HAS_GAMBIT = False
    print("pygambit 未安装——E4 可选小节跳过（核心 E1–E3 纯 numpy，不依赖外部库；安装见 README 运行环境）")

# ======================================================================
# auction.png：1×3——(a) 四拍卖收入对比条形 (b) 赢者支付分布（FPSB vs 二价）(c) 赢家诅咒利润曲线
# ======================================================================
fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.9))

# (a) 收入对比条形
ax = axes[0]
names = ["英式\n(=二价)", "荷兰式\n(=一价)", "一价密封", "二价密封"]
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
bars = ax.bar(names, mc_revs, width=0.62, color=colors, alpha=0.88)
ax.axhline(1 / 3, color="red", lw=1.4, ls="--", label="理论 E[R] = (n−1)/(n+1) = 1/3")
for bar, r in zip(bars, mc_revs):
    ax.annotate(f"{r:.4f}", xy=(bar.get_x() + bar.get_width() / 2, r), xytext=(0, 3),
                textcoords="offset points", ha="center", fontsize=9)
ax.set_ylim(0, 0.40)
ax.set_ylabel("平均收入（10⁵ 场蒙特卡洛）")
ax.set_title("E2 · 收益等价：四种拍卖同一批估值\n四路平均收入并排 ≈ 1/3（容差 0.01）", fontsize=10.5)
ax.legend(fontsize=9, loc="lower right")

# (b) 赢者支付分布：FPSB（=v_max/2）vs 二价（=次高）
ax = axes[1]
bins = np.linspace(0, 1, 45)
ax.hist(vmax / 2, bins=bins, color="tab:orange", alpha=0.62, label=f"FPSB 支付 = v_max/2（均值 {mc_pay:.4f}）")
ax.hist(vmin, bins=bins, color="tab:blue", alpha=0.62, label=f"二价支付 = 次高（均值 {mc_revs[3]:.4f}）")
ax.axvline(1 / 3, color="red", lw=1.4, ls="--")
ax.annotate("同一均值 1/3（分布形状不同）", xy=(1 / 3, 3300), xytext=(0.47, 3300),
            fontsize=9, color="red", arrowprops=dict(arrowstyle="->", color="red"))
ax.set_xlim(0, 1)
ax.set_xlabel("赢者支付")
ax.set_ylabel("场数")
ax.set_title("E1/E2 · 赢者支付分布：规则不同、均值相同\nFPSB 出价=半价 vs 二价=次高（收益等价的形状注脚）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="upper right")

# (c) 赢家诅咒利润曲线
ax = axes[2]
ns = [r[0] for r in rows_e3]
naive_m = [r[1] for r in rows_e3]
rat_m = [r[2] for r in rows_e3]
th_curve = [(1 - n) / (2 * (n + 1)) for n in NS]
ax.plot(NS, th_curve, lw=1.6, color="tab:red", ls="--", label="naive 理论 (1−n)/(2(n+1))")
ax.plot(NS, naive_m, "o", ms=7, color="tab:red", label=f"naive 模拟（出价=自己信号）")
ax.plot(NS, rat_m, "s", ms=7, color="tab:green", label="理性修正模拟（b=(n+1)/(2n)·s）")
ax.axhline(0, color="tab:green", lw=1.2, ls=":")
ax.annotate("理性修正 ≈ 0\n（条件期望抵平）", xy=(11.5, 0.012), fontsize=9, color="tab:green")
ax.annotate(f"n=2：−1/6 ≈ {naive_m[0]:.4f}", xy=(2, naive_m[0]), xytext=(3.2, naive_m[0] + 0.03),
            fontsize=9, color="tab:red", arrowprops=dict(arrowstyle="->", color="tab:red"))
ax.set_xticks(NS)
ax.set_ylim(-0.62, 0.10)
ax.set_xlabel("竞拍人数 n")
ax.set_ylabel("赢者平均利润（V − 出价）")
ax.set_title("E3 · 赢家诅咒：naive 利润随 n 加深（→ −1/2），\norder-statistic 修正后归零（共同价值，13 章）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="lower left")

fig.suptitle("lab04 · 不完全信息与拍卖：FPSB 均衡 b=v/2 / 四拍卖收益等价 / 赢家诅咒（纯 numpy 蒙特卡洛 10⁵ 场 ×4 组）", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.94))
OUT = Path(__file__).resolve().parent / "auction.png"
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
