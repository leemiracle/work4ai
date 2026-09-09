#!/usr/bin/env python3
"""讲透博弈论实验 6：合作博弈与机制设计——Shapley 公理 + Gale-Shapley 稳定匹配 + 谎报 DSIC。
E1 Shapley 值（12 章 §二/§三）：公式 φᵢ=Σ_S |S|!(n−|S|−1)!/n!·[v(S∪{i})−v(S)] 枚举 2ⁿ 子集——
   三人投票博弈 φ=(1/3,1/3,1/3)、机场跑道（100/180/220，c(S)=max）φ=(100/3,220/3,340/3) 与 12 章手算对拍；
   机场另用"随机次序读法"（3!=6 种排列枚举增量再平均）独立复算——公式与次序平均是同一台机器；
   四公理逐条数值验证：有效（Σφ=v(N)）/ 对称（机场标签互换 φ 同步互换——非对称博弈上的实质检验）/
   哑元（加第 4 家零成本航司 φ₄=0 且其余分毫不动）/ 可加（投票+独裁 φ(v+w)=φ(v)+φ(w)）
E2 Gale-Shapley 手写（12 章 §五）：4×4 随机偏好（声明：seed=8 经扫描选定，seed=42 的实例两方向终局相同
   且受方无任何可改进谎报——唯一稳定匹配的实例演示不了"可操纵"，如实标注）——男求婚与女求婚各跑一遍，
   两个终局都做阻塞对全枚举检查（阻塞对=0 = 稳定性定理复算）；志愿位对比展示求婚方优势
E3 谎报实验（14 章 IC/DSIC 的最小现场）：8 个玩家 × 各 4!=24 种谎报偏好逐一重跑男求婚 DA——
   求婚方（男）严格改进 0 次 = DSIC 数值验证（Dubins-Freedman 1981：任何实例皆 0，定理保证）；
   受方（女）严格改进 ≥1 次 = Roth 1982 不可双向复制；打印一个具体谎报轨迹
产出：coop.png（1×3：机场跑道洋葱增量 / 两方向匹配志愿位对比 / 谎报严格改进计数）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from itertools import permutations
from math import factorial
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
TOL = 1e-9                     # 精确枚举无随机误差，容差取浮点精度

# ======================================================================
print("=" * 68)
print("E1 · Shapley 值：公式枚举 + 随机次序复算 + 四公理数值验证")
print("=" * 68)


def shapley(v, n):
    """公式 φᵢ = Σ_{S⊆N\\{i}} |S|!(n−|S|−1)!/n! · [v(S∪{i})−v(S)]——2ⁿ 子集全枚举。"""
    phi = np.zeros(n)
    for i in range(n):
        others = [j for j in range(n) if j != i]
        for mask in range(1 << (n - 1)):          # 枚举 N\\{i} 的全部子集
            S = [others[k] for k in range(n - 1) if mask >> k & 1]
            w = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
            phi[i] += w * (v(S + [i]) - v(S))
    return phi


# --- 三人投票博弈（12 章 §三例一）：v(S)=1 若 |S|≥2 ---
v_vote = lambda S: 1.0 if len(S) >= 2 else 0.0
phi_vote = shapley(v_vote, 3)
hand_vote = np.array([1 / 3, 1 / 3, 1 / 3])
print("公式 φᵢ = Σ_S |S|!(n−|S|−1)!/n!·[v(S∪{i})−v(S)]（12 章 §二手算母体）")
print(f"  三人投票（51% 规则）：φ = ({phi_vote[0]:.4f}, {phi_vote[1]:.4f}, {phi_vote[2]:.4f})"
      f" vs 手算 (1/3, 1/3, 1/3)——|最大偏差| = {np.abs(phi_vote - hand_vote).max():.2e} ✓")

# --- 机场跑道（12 章 §三例二）：三家航司成本 100/180/220，c(S)=max{成员成本} ---
COSTS = [100, 180, 220]
c_air = lambda S: max(COSTS[i] for i in S) if S else 0.0
phi_air = shapley(c_air, 3)
hand_air = np.array([100 / 3, 220 / 3, 340 / 3])
print(f"  机场跑道（c(S)=max）：φ = ({phi_air[0]:.4f}, {phi_air[1]:.4f}, {phi_air[2]:.4f})"
      f" vs 手算 (100/3, 220/3, 340/3)——|最大偏差| = {np.abs(phi_air - hand_air).max():.2e} ✓")

# --- 随机次序读法独立复算（12 章 §二："一切入伙次序下的平均边际贡献"）---
print("  机场的随机次序读法（3!=6 种排列枚举增量再平均）：")
order_rows = []
for perm in permutations(range(3)):
    incr, built = [0.0, 0.0, 0.0], 0.0            # 增量按【玩家编号】对齐（到达序与玩家序不同——平均才不串位）
    for i in perm:                                # i 到场：跑道已比自家规格长就分文不付（增量非负）
        need = c_air([i])
        incr[i] = max(0.0, need - built)
        built = max(built, need)
    order_rows.append((perm, incr))
line = "    " + "   ".join(f"{''.join(map(str, p))}: ({r[0]:.0f}, {r[1]:.0f}, {r[2]:.0f})" for p, r in order_rows[:3])
print(line)
line = "    " + "   ".join(f"{''.join(map(str, p))}: ({r[0]:.0f}, {r[1]:.0f}, {r[2]:.0f})" for p, r in order_rows[3:])
print(line)
phi_order = np.mean([r for _, r in order_rows], axis=0)
ok_order = np.abs(phi_order - phi_air).max() < 1e-12
print(f"    平均 = ({phi_order[0]:.4f}, {phi_order[1]:.4f}, {phi_order[2]:.4f})——与公式逐位一致"
      f"（|最大偏差| = {np.abs(phi_order - phi_air).max():.2e}）{'✓ 公式=随机次序平均，同一台机器' if ok_order else '⚠ 不一致——如实标注'}")

# --- 四公理逐条过审 ---
print("  四公理逐条过审：")
eff_ok = abs(phi_air.sum() - c_air([0, 1, 2])) < TOL and abs(phi_vote.sum() - v_vote([0, 1, 2])) < TOL
print(f"    ① 有效：机场 Σφ = {phi_air.sum():.4f} = c(N) = {c_air([0, 1, 2]):.0f}；"
      f"投票 Σφ = {phi_vote.sum():.4f} = v(N) = 1 —— {'✓' if eff_ok else '⚠'}")

c_swap = lambda S: max([180, 100, 220][i] for i in S) if S else 0.0   # 标签 1↔2 互换后的机场
phi_swap = shapley(c_swap, 3)
sym_ok = abs(phi_swap[0] - phi_air[1]) < TOL and abs(phi_swap[1] - phi_air[0]) < TOL and abs(phi_swap[2] - phi_air[2]) < TOL
print(f"    ② 对称：机场标签 1↔2 互换 → φ 变为 ({phi_swap[0]:.4f}, {phi_swap[1]:.4f}, {phi_swap[2]:.4f})"
      f" = 原 φ 的 1↔2 位互换 —— {'✓（在非对称博弈上检验，投票博弈人人对称检验不出错）' if sym_ok else '⚠'}")

c4 = lambda S: max([COSTS[i] for i in S if i < 3] + [0.0])            # 加第 4 家零成本航司（哑元）
phi4 = shapley(c4, 4)
dum_ok = abs(phi4[3]) < TOL and np.abs(phi4[:3] - phi_air).max() < TOL
print(f"    ③ 哑元：机场 + 第 4 家零成本航司 → φ₄ = {phi4[3]:.2e}，其余三家 ({phi4[0]:.4f}, {phi4[1]:.4f}, {phi4[2]:.4f}) 分毫不动 —— {'✓' if dum_ok else '⚠'}")

v_dict = lambda S: 1.0 if 0 in S else 0.0                            # 1 号"独裁"博弈：φ=(1,0,0)
phi_sum = shapley(lambda S: v_vote(S) + v_dict(S), 3)
add_ok = np.abs(phi_sum - (phi_vote + shapley(v_dict, 3))).max() < TOL
print(f"    ④ 可加：投票 v + 独裁 w → φ(v+w) = ({phi_sum[0]:.4f}, {phi_sum[1]:.4f}, {phi_sum[2]:.4f})"
      f" = φ(v)+φ(w) = (1/3+1, 1/3, 1/3) —— {'✓' if add_ok else '⚠'}")
ok_e1 = eff_ok and sym_ok and dum_ok and add_ok and np.abs(phi_vote - hand_vote).max() < 1e-12 \
        and np.abs(phi_air - hand_air).max() < 1e-12 and ok_order
print(f"→ E1 对拍：公式/手算/随机次序三路一致，四公理全过 —— " + ("全绿 ✓" if ok_e1 else "⚠ 如实标注"))

# ======================================================================
print("\n" + "=" * 68)
print("E2 · Gale-Shapley 手写：4×4 稳定匹配 + 两方向差异")
print("=" * 68)
# 声明：偏好由 default_rng(8) 抽取。seed=8 经扫描选定——seed=42 的实例男/女求婚终局相同
#   （唯一稳定匹配）且受方无任何可改进谎报，演示不了"多稳定匹配 + 受方可操纵"；换 seed 属实例选择，非挑选结论
#   （求婚方 DSIC 在任何实例都成立，E3 的 0 不依赖 seed——定理保证）。
rng = np.random.default_rng(8)
M = {m: [int(x) for x in rng.permutation(4)] for m in range(4)}   # 男 m 的偏好序（女编号降序）
W = {w: [int(x) for x in rng.permutation(4)] for w in range(4)}   # 女 w 的偏好序


def gale_shapley(prop, rec):
    """要求-接受算法（12 章 §五四步）：prop 一侧求婚、rec 一侧暂存；返回 求婚方→受方 匹配。"""
    free = list(prop)
    next_i = {p: 0 for p in prop}
    held = {}                                                      # 受方 → 当前暂存求婚者
    while free:
        m = free.pop(0)
        w = prop[m][next_i[m]]
        next_i[m] += 1
        if w not in held:
            held[w] = m
        elif rec[w].index(m) < rec[w].index(held[w]):              # 暂存更中意者、拒掉其余（含已暂配者）
            free.append(held[w])
            held[w] = m
        else:
            free.append(m)
    return {m: w for w, m in held.items()}


def blocking_pairs(match_m2w, M, W):
    """全枚举阻塞对：m 更爱 w 胜过现任 且 w 更爱 m 胜过现任。"""
    w2m = {w: m for m, w in match_m2w.items()}
    return [(m, w) for m in range(4) for w in range(4)
            if M[m].index(w) < M[m].index(match_m2w[m]) and W[w].index(m) < W[w].index(w2m[w])]


def rank(prefs, who, target):
    return prefs[who].index(target) + 1                            # 志愿位：1=首选


match_m = gale_shapley(M, W)                                       # 男求婚（man→woman）
match_w = {int(m): int(w) for w, m in gale_shapley(W, M).items()}  # 女求婚（角色互换，仍列 man→woman）
w2m_m = {w: m for m, w in match_m.items()}                         # 男求婚终局的 woman→man
w2m_w = {w: m for m, w in match_w.items()}                         # 女求婚终局的 woman→man
print("偏好（声明：default_rng(8) 抽取，见上）——行=玩家，列表=偏好降序：")
print("  男：" + "  ".join(f"m{m}:{M[m]}" for m in range(4)))
print("  女：" + "  ".join(f"w{w}:{W[w]}" for w in range(4)))
print(f"男求婚终局：{'  '.join(f'm{m}→w{match_m[m]}' for m in range(4))}"
      f"（男志愿位 {[rank(M, m, match_m[m]) for m in range(4)]}，女志愿位 {[rank(W, w, w2m_m[w]) for w in range(4)]}）")
print(f"女求婚终局：{'  '.join(f'm{m}→w{match_w[m]}' for m in range(4))}"
      f"（男志愿位 {[rank(M, m, match_w[m]) for m in range(4)]}，女志愿位 {[rank(W, w, w2m_w[w]) for w in range(4)]}）")
bp_m, bp_w = blocking_pairs(match_m, M, W), blocking_pairs(match_w, M, W)
print(f"稳定性检查（全枚举 16 对）：男求婚终局阻塞对 {len(bp_m)} 个；女求婚终局阻塞对 {len(bp_w)} 个"
      f"—— {'双双 0 = 稳定性定理复算 ✓' if not bp_m and not bp_w else '⚠ 出现阻塞对——如实标注'}")
men_better = all(rank(M, m, match_m[m]) <= rank(M, m, match_w[m]) for m in range(4))
women_better = all(rank(W, w, w2m_w[w]) <= rank(W, w, w2m_m[w]) for w in range(4))
print(f"两方向读数：男求婚里男整体不差（求婚方最优性），女求婚里女整体不差——"
      f"{'✓（Gale-Shapley 1962：两个终局都是稳定匹配，各是求婚方一侧的最优稳定匹配）' if men_better and women_better else '⚠'}")
ok_e2 = not bp_m and not bp_w and men_better and women_better and match_m != match_w
print(f"→ E2 对拍：两终局皆稳定（阻塞对=0）且互不相同（多稳定匹配在场），求婚方优势可读 —— "
      + ("全绿 ✓" if ok_e2 else "⚠ 如实标注"))

# ======================================================================
print("\n" + "=" * 68)
print("E3 · 谎报实验：求婚方 DSIC vs 受方可操纵（8 玩家 × 24 种谎报全枚举）")
print("=" * 68)
# 手推锚点（定理，非实例巧合）：Dubins-Freedman 1981——男求婚 DA 里任何男任何谎报都不可能严格改进（0 次，任何实例）；
#   Roth 1982——存在实例与谎报让受方严格改进（实例性：本实例 [0,4,0,4]）。
base_rank_m = {m: rank(M, m, match_m[m]) for m in range(4)}
base_rank_w = {w: rank(W, w, w2m_m[w]) for w in range(4)}
improve_m, worse_m = [], 0
for m in range(4):                                                 # 求婚方谎报：其他人真话，m 交 24 种假偏好
    cnt = 0
    for perm in permutations(range(4)):
        M_lie = {x: (list(perm) if x == m else M[x]) for x in range(4)}
        res = gale_shapley(M_lie, W)
        if rank(M, m, res[m]) < base_rank_m[m]:                    # 按真偏好评价
            cnt += 1
        elif rank(M, m, res[m]) > base_rank_m[m]:
            worse_m += 1
    improve_m.append(cnt)
improve_w, examples = [], []
for w in range(4):                                                 # 受方谎报：w 交假偏好，男求婚照跑
    cnt = 0
    for perm in permutations(range(4)):
        W_lie = {x: (list(perm) if x == w else W[x]) for x in range(4)}
        res = gale_shapley(M, W_lie)                               # man→woman，需反转查 w 的配偶
        got = next(mm for mm, ww in res.items() if ww == w)
        if rank(W, w, got) < base_rank_w[w]:
            cnt += 1
            if not examples or examples[0][0] != w:
                examples.insert(0, (w, list(perm), got))
    improve_w.append(cnt)
print(f"理论锚点（定理）：求婚方严格改进 0 次（Dubins-Freedman 1981，任何实例）；受方改进为实例性（Roth 1982，存在性）")
print(f"  男（求婚方）4 人 × 24 种谎报 = 96 次：严格改进 {sum(improve_m)} 次（逐人 {improve_m}），"
      f"严格变差 {worse_m} 次——谎报无利、且可能自伤")
print(f"  女（受方）  4 人 × 24 种谎报 = 96 次：严格改进 {sum(improve_w)} 次（逐人 {improve_w}）")
for w, lie, got in reversed(examples[:1]):
    print(f"    具体轨迹：w{w} 谎报偏好 {lie} → 终局配 m{got}"
          f"（第 {rank(W, w, got)} 志愿，原第 {base_rank_w[w]} 志愿）——受方操纵成功")
ok_e3 = sum(improve_m) == 0 and sum(improve_w) >= 1
print(f"→ E3 对拍：求婚方 0 改进 = DSIC 数值验证；受方 {sum(improve_w)} 次改进 = 不可双向复制 —— "
      + ("全绿 ✓" if ok_e3 else "⚠ 如实标注"))
print("  诚实标注：枚举的是完整严格偏好序谎报（4! 种）；定理还覆盖截断式谎报（宣布'不可接受'，12 章练习③的手推现场）。")
print("    受方可改进是实例性结论——seed=42 的实例恰为 0（唯一稳定匹配时无谎报余地），本实验用 seed=8 让两种现象同场。")

# ======================================================================
# coop.png：1×3——(a) 机场跑道洋葱增量 (b) 两方向匹配志愿位对比 (c) 谎报严格改进计数
# ======================================================================
fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.9))

# (a) 机场跑道的洋葱切法：Shapley 分摊 = 按层切增量
ax = axes[0]
layers = [(0, 100, [0, 1, 2], "基座 0–100：三家平摊"), (100, 180, [1, 2], "升级 100–180：2、3 号平摊"),
          (180, 220, [2], "封顶 180–220：3 号独付")]
colors3 = ["tab:blue", "tab:orange", "tab:green"]
for li, (lo, hi, members, label) in enumerate(layers):
    widths = {p: (hi - lo) / len(members) if p in members else 0 for p in range(3)}
    base = [0, 0, 0]
    for lj in range(li):                                          # 前几层的累计（该玩家已付部分）
        prev = layers[lj]
        base = [base[p] + (prev[1] - prev[0]) / len(prev[2]) if p in prev[2] else base[p] for p in range(3)]
    ax.barh([f"航司{i+1}（成本{COSTS[i]}）" for i in range(3)],
            [widths[p] for p in range(3)], left=base, color=colors3[li], label=label, height=0.55)
    for p in range(3):
        if widths[p] > 0:
            ax.annotate(f"{widths[p]:.1f}", xy=(base[p] + widths[p] / 2, 2 - p), ha="center", va="center", fontsize=8.5)
for p, tot in enumerate(phi_air):
    ax.annotate(f"φ={tot:.1f}", xy=(tot + 14, 2 - p), va="center", fontsize=9.5, fontweight="bold")
ax.set_xlim(0, 268)
ax.set_xlabel("分摊额（合计 = 220）")
ax.set_title("E1 · 机场跑道的洋葱切法：Shapley 分摊 = 按层切增量\n（基座人人有份、升级差价用者自付）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="lower right")

# (b) 两方向匹配志愿位对比（1=首选，条越矮越好）
ax = axes[1]
labels_b = [f"m{m}" for m in range(4)] + [f"w{w}" for w in range(4)]
ranks_mprop = [rank(M, m, match_m[m]) for m in range(4)] + [rank(W, w, w2m_m[w]) for w in range(4)]
ranks_wprop = [rank(M, m, match_w[m]) for m in range(4)] + [rank(W, w, w2m_w[w]) for w in range(4)]
x = np.arange(8)
ax.bar(x - 0.19, ranks_mprop, width=0.38, color="tab:blue", label="男求婚终局的志愿位")
ax.bar(x + 0.19, ranks_wprop, width=0.38, color="tab:orange", label="女求婚终局的志愿位")
for xi, (a, b) in enumerate(zip(ranks_mprop, ranks_wprop)):
    ax.annotate(str(a), xy=(xi - 0.19, a), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8.5)
    ax.annotate(str(b), xy=(xi + 0.19, b), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8.5)
ax.axvline(3.5, color="gray", lw=0.9, ls=":")
ax.annotate("男（左边条矮 = 男求婚对男更好）", xy=(1.5, 4.45), fontsize=8.5, ha="center", color="dimgray")
ax.annotate("女（右边条矮 = 女求婚对女更好）", xy=(5.5, 4.45), fontsize=8.5, ha="center", color="dimgray")
ax.set_xticks(x, labels_b)
ax.set_yticks([1, 2, 3, 4], ["第1志愿", "第2志愿", "第3志愿", "第4志愿"])
ax.set_ylim(0, 4.9)
ax.set_title("E2 · 同一市场、两个稳定匹配：谁求婚谁占优\n（两个终局阻塞对都 = 0；求婚方得最优稳定匹配）", fontsize=10.5)
ax.legend(fontsize=8.5, loc="upper left")

# (c) 谎报严格改进计数：求婚方全 0（DSIC）vs 受方可正（Roth 1982）
ax = axes[2]
x = np.arange(8)
counts = improve_m + improve_w
colors_c = ["tab:green"] * 4 + ["tab:orange"] * 4
ax.bar(x, counts, color=colors_c, width=0.6)
for xi, cval in zip(x, counts):
    ax.annotate(str(cval), xy=(xi, cval), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9.5)
ax.axvline(3.5, color="gray", lw=0.9, ls=":")
ax.annotate("求婚方（男）：全 0\n= DSIC（定理保证，任何实例）", xy=(1.5, 3.4), fontsize=9, ha="center", color="tab:green")
ax.annotate(f"受方（女）：合计 {sum(improve_w)} 次 ≥1\n= 可操纵（Roth 1982，实例性）", xy=(5.5, 3.4), fontsize=9, ha="center", color="tab:orange")
ax.set_xticks(x, labels_b)
ax.set_ylabel("谎报后严格改进的次数（24 种谎报/人）")
ax.set_ylim(0, 4.6)
ax.set_title(f"E3 · 谎报实验：诚实只对一侧成立\n（求婚方 0 改进；受方可改进者合计 {sum(improve_w)} 次）", fontsize=10.5)

fig.suptitle("lab06 · 合作博弈与机制设计：Shapley 公理数值验证 / Gale-Shapley 两方向稳定匹配 / 谎报 DSIC 实验（纯 numpy 枚举）", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.94))
OUT = Path(__file__).resolve().parent / "coop.png"
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
