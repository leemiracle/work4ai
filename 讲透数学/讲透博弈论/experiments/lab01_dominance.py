#!/usr/bin/env python3
"""讲透博弈论实验 1：占优与均衡基础实验室。
E1 猜数博弈 100 个 k-level 代理模拟（×0.7 链 vs 均衡 0） | E2 三原型+附加 2×2（+猜拳 3×3）nashpy 全 NE 对拍（手算 vs nashpy 一致 ✓） | E3 IESDS 剔除序列+弱占优陷阱
产出：ne_basic.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import nashpy as nash
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]
rng = np.random.default_rng(42)

# ----------------------------------------------------------------------
# 统一记号（与 00 章三原型完全一致）：
#   A[i, j] = 行玩家在（行 i, 列 j）的收益，B[i, j] = 列玩家收益
# ----------------------------------------------------------------------
GAMES = {
    "囚徒困境（T5 R3 P1 S0）": dict(
        A=np.array([[3.0, 0.0], [5.0, 1.0]]), B=np.array([[3.0, 5.0], [0.0, 1.0]]),
        row_act=("C 合作", "D 背叛"), col_act=("C 合作", "D 背叛"),
        hand_pure={(1, 1)}, hand_mixed=None,
        note="D 严格占优 C（对 C: 5>3；对 D: 1>0）→ 唯一均衡 (D,D)，占优通道免检、无混合",
    ),
    "性别战争（BoS）": dict(
        A=np.array([[2.0, 0.0], [0.0, 1.0]]), B=np.array([[1.0, 0.0], [0.0, 2.0]]),
        row_act=("歌剧", "足球"), col_act=("歌剧", "足球"),
        hand_pure={(0, 0), (1, 1)}, hand_mixed=((2/3, 1/3), (1/3, 2/3)),
        note="两个纯 NE + 1 个混合（行 2/3 歌剧、列 1/3 歌剧，双方收益 2/3）",
    ),
    "鹰鸽博弈（v=2, c=4）": dict(
        A=np.array([[-1.0, 2.0], [0.0, 1.0]]), B=np.array([[-1.0, 2.0], [0.0, 1.0]]).T,
        row_act=("鹰 H", "鸽 D"), col_act=("鹰 H", "鸽 D"),
        hand_pure={(0, 1), (1, 0)}, hand_mixed=((0.5, 0.5), (0.5, 0.5)),
        note="反协调：两非对称纯 NE (H,D)/(D,H) + 对称混合 x*=v/c=0.5",
    ),
    "匹配硬币（无纯 NE）": dict(
        A=np.array([[1.0, -1.0], [-1.0, 1.0]]), B=np.array([[-1.0, 1.0], [1.0, -1.0]]),
        row_act=("正面", "反面"), col_act=("正面", "反面"),
        hand_pure=set(), hand_mixed=((0.5, 0.5), (0.5, 0.5)),
        note="零和、无纯 NE，唯一混合 (1/2,1/2)——02 章'猜拳无纯 NE'的 2×2 表亲",
    ),
    "猎鹿（Stag Hunt）": dict(
        A=np.array([[4.0, 1.0], [3.0, 2.0]]), B=np.array([[4.0, 3.0], [1.0, 2.0]]),
        row_act=("猎鹿", "抓兔"), col_act=("猎鹿", "抓兔"),
        hand_pure={(0, 0), (1, 1)}, hand_mixed=((0.5, 0.5), (0.5, 0.5)),
        note="两个纯 NE（收益占优 vs 风险占优之争）+ 对称混合 (1/2,1/2)——05 章主角",
    ),
    "罚点球（03 章主角）": dict(
        A=np.array([[0.65, 0.95], [0.95, 0.55]]), B=1.0 - np.array([[0.65, 0.95], [0.95, 0.55]]),
        row_act=("踢左", "踢右"), col_act=("扑左", "扑右"),
        hand_pure=set(), hand_mixed=((4/7, 3/7), (4/7, 3/7)),
        note="常和：行=射门方向、列=扑救方向（同侧得分率低）；混合 x*=4/7≈0.5714，博弈值 5.45/7≈0.7786",
    ),
    "弱占优陷阱博弈（01/E3）": dict(
        A=np.array([[0.0, 1.0], [1.0, 0.0]]), B=np.array([[1.0, 1.0], [2.0, 0.0]]),
        row_act=("U", "D"), col_act=("L", "R"),
        hand_pure={(0, 1), (1, 0)}, hand_mixed=None,
        note="两个纯 NE (U,R)/(D,L)；列玩家 L 弱占优 R——弱占优剔除会把 NE (U,R) 删掉（E3 演示）。"
             "简并：对手固定出 U 时列玩家 L/R 同收益 1 → (U, σ) 连续统，支撑枚举只报纯 NE",
    ),
    "猜拳 RPS（3×3，无纯 NE）": dict(
        A=np.array([[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]]),
        B=np.array([[0.0, 1.0, -1.0], [-1.0, 0.0, 1.0], [1.0, -1.0, 0.0]]),
        row_act=("石头", "布", "剪刀"), col_act=("石头", "布", "剪刀"),
        hand_pure=set(), hand_mixed=((1/3, 1/3, 1/3), (1/3, 1/3, 1/3)),
        note="9 个纯策略组合全灭（无纯 NE）→ 必须进入混合策略（03 章）；唯一混合 (1/3,1/3,1/3)",
    ),
}


def pure_ne_cells(A, B):
    """手算一侧：逐格检验两个'单方偏离'问题（02 章判定法）。"""
    ne = set()
    for i in range(A.shape[0]):
        for j in range(B.shape[1]):
            if A[i, j] == A[:, j].max() and B[i, j] == B[i, :].max():
                ne.add((i, j))
    return ne


def fmt_vec(v):
    return "(" + ", ".join(f"{x:.4f}" for x in np.asarray(v)) + ")"


def fmt_pure(cell, g):
    return f"({g['row_act'][cell[0]]}, {g['col_act'][cell[1]]})"


# ======================================================================
print("=" * 68)
print("E1 · 0-100 猜数博弈（目标 = 平均数 × 0.7）：100 个 k-level 代理")
print("=" * 68)
# 理性层级分布（截断在 k=6）：多数人落在 level-1~2（Nagel 1995 / Camerer 2004 的实测形态）
LEVEL_W = np.array([0.30, 0.32, 0.20, 0.10, 0.05, 0.02, 0.01])
levels = rng.choice(np.arange(len(LEVEL_W)), size=100, p=LEVEL_W)
reports = np.empty(100)
reports[levels == 0] = rng.uniform(0.0, 100.0, size=(levels == 0).sum())
prev_mean = 50.0                                        # 兜底：level-0 理论均值 E[U[0,100]] = 50
for k in range(1, len(LEVEL_W)):                       # level-k = 0.7 × level-(k-1) 均值
    cur = reports[levels == k - 1]
    if cur.size:
        prev_mean = cur.mean()
    if (levels == k).any():                            # 空层无代理可赋值，跳过（防 NaN 传播）
        reports[levels == k] = 0.7 * prev_mean

chain = [50.0]                                          # 确定性 k 链：50 → 35 → 24.5 → …
for _ in range(6):
    chain.append(0.7 * chain[-1])
print("k 链（level-k 的报告）: " + " → ".join(f"{c:g}" for c in chain) + " → … → 0（唯一均衡）")
bound, bounds = 100.0, []                               # IESDS 上界链：任何 >70 的数被 70 严格占优
while bound > 1.0:
    bound *= 0.7
    bounds.append(bound)
print("IESDS 上界链: 100 → " + " → ".join(f"{b:.2f}" for b in bounds[:5]) + f" → … → 0（×0.7^{len(bounds)} 后已 <1）")

target = 0.7 * reports.mean()
win = int(np.argmin(np.abs(reports - target)))
print(f"\n模拟：全员平均报告 = {reports.mean():.2f}，获胜目标 = 0.7×平均 = {target:.2f}")
print(f"胜者：level-{levels[win]} 代理，报告 {reports[win]:.2f}（各 level 平均报告: "
      + ", ".join(f"L{k}={reports[levels == k].mean():.2f}" for k in range(len(LEVEL_W))
                  if (levels == k).any()) + "）")
print("理论对照：公共知识理性 → 唯一均衡 0（无人报告）；Nagel 1995 实测胜出数落在 level-1~2（≈25~35）")
print(f"诚实标注：本模拟是 k-level 模型，胜者 level-{levels[win]} 是模型性质；它与实测叙事一致——均衡 0 不是赢家")

# ======================================================================
print("\n" + "=" * 68)
print("E2 · 三原型 + 附加 2×2（+猜拳 3×3）：手算 vs nashpy support_enumeration 对拍")
print("=" * 68)
n_ok = 0
for name, g in GAMES.items():
    A, B = g["A"], g["B"]
    hand, method = g["hand_pure"], pure_ne_cells(A, B)   # 手算表（章内逐格判定的结论）+ 判定法代码化
    eqs, seen = [], set()
    for s, t in nash.Game(A, B).support_enumeration():
        key = (tuple(np.round(s, 9)), tuple(np.round(t, 9)))
        if key not in seen:
            seen.add(key)
            eqs.append((np.asarray(s), np.asarray(t)))
    nash_pure = {(int(np.argmax(s)), int(np.argmax(t))) for s, t in eqs
                 if (s > 1e-9).sum() == 1 and (t > 1e-9).sum() == 1}
    ok = True
    verdict = []
    if hand != method:                                   # 三方对拍第 1 步：手算表 vs 判定法
        ok = False
        verdict.append(f"⚠ 手算表 {hand} 与逐格判定法 {method} 不一致")
    if method == nash_pure:                              # 三方对拍第 2 步：判定法 vs nashpy
        verdict.append("纯 NE 一致 ✓")
    else:
        ok = False
        verdict.append(f"纯 NE 不一致：判定法 {method} vs nashpy {nash_pure}")
    if g["hand_mixed"] is not None:                      # 手算混合概率 vs nashpy
        hm_h, hm_v = g["hand_mixed"]
        hit = any(np.allclose(s, hm_h, atol=1e-6) and np.allclose(t, hm_v, atol=1e-6) for s, t in eqs)
        verdict.append(f"混合 {fmt_vec(hm_h)}×{fmt_vec(hm_v)} " + ("一致 ✓" if hit else "未在 nashpy 结果中复现！"))
        ok = ok and hit
    print(f"\n【{name}】")
    print(f"  手算纯 NE: {sorted(fmt_pure(c, g) for c in hand) or '无'}    {g['note']}")
    for s, t in eqs:
        print(f"    nashpy: P1={fmt_vec(s)}  P2={fmt_vec(t)}")
    print(f"  → 手算 vs nashpy：{'，'.join(verdict)}")
    n_ok += ok
print(f"\nE2 总对拍：{n_ok}/{len(GAMES)} 局全部一致 ✓" if n_ok == len(GAMES)
      else f"\nE2 总对拍：仅 {n_ok}/{len(GAMES)} 局一致——差异如上，如实标注")

# ======================================================================
print("\n" + "=" * 68)
print("E3 · IESDS 严格重复剔除 + 弱占优陷阱")
print("=" * 68)


def find_dominated(pay, own, other, strict):
    """在 (own, other) 残余索引里找被（严格|弱）占优的 own 策略，返回 (被占优者, 占优者)。"""
    for a in own:
        for b in own:
            if b == a:
                continue
            diffs = [pay[b][o] - pay[a][o] for o in other]
            if all(d > 0 for d in diffs) or (not strict and all(d >= 0 for d in diffs) and any(d > 0 for d in diffs)):
                return a, b
    return None


def iterate_dominance(A, B, strict, label):
    """逐轮剔除（先行后列），打印剔除序列；strict=True 为 IESDS，False 为 IESWDS。"""
    rows, cols = list(range(A.shape[0])), list(range(A.shape[1]))
    tag = "严格（IESDS）" if strict else "弱（IESWDS）"
    print(f"\n{label} · {'严格占优剔除 IESDS' if strict else '弱占优剔除 IESWDS'}：")
    step = 0
    while True:
        hit = find_dominated(A, rows, cols, strict)
        if hit:
            a, b = hit
            rows.remove(a)
            step += 1
            print(f"  第{step}步：行玩家 行{a} 被 行{b} {'严格' if strict else '弱'}占优 → 剔除 行{a}，残余行 {rows}")
            continue
        hit = find_dominated(B.T, cols, rows, strict)
        if hit:
            a, b = hit
            cols.remove(a)
            step += 1
            print(f"  第{step}步：列玩家 列{a} 被 列{b} {'严格' if strict else '弱'}占优 → 剔除 列{a}，残余列 {cols}")
            continue
        break
    surv = [(r, c) for r in rows for c in cols]
    if surv:
        pay_txt = ", ".join(f"({A[r][c]:g},{B[r][c]:g})" for r, c in surv)
        print(f"  残余组合：{[(f'行{r}', f'列{c}') for r, c in surv]}，收益 [{pay_txt}]")
    else:
        print("  残余为空")
    return surv


# --- 3×3 IESDS 演示矩阵：R → U → C → D 四连剔，收敛到唯一 NE (M,L) ---
A3 = np.array([[1.0, 0.0, 0.0], [3.0, 2.0, 1.0], [2.0, 1.0, 0.0]])   # 行玩家 U/M/D × 列 L/C/R
B3 = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 1.0, 0.0]])
print("3×3 演示矩阵（行 U/M/D × 列 L/C/R，单元=行收益,列收益）：")
for i in range(3):
    print("   " + "  ".join(f"({A3[i,j]:g},{B3[i,j]:g})" for j in range(3)))
surv = iterate_dominance(A3, B3, strict=True, label="IESDS 演示")
eqs3 = list(nash.Game(A3, B3).support_enumeration())
print(f"  nashpy 全 NE：{[(fmt_vec(s), fmt_vec(t)) for s, t in eqs3]}")
print(f"  对照：剔除收敛到 (行1=M, 列0=L) 收益 (3,1)；nashpy 唯一 NE 与之一致 → 严格占优剔除绝不删除任何 NE ✓"
      if len(eqs3) == 1 and np.allclose(eqs3[0][0], [0, 1, 0]) and np.allclose(eqs3[0][1], [1, 0, 0])
      else "  ⚠ nashpy 结果与剔除收敛点不一致——如实标注，勿放宽")

# --- 弱占优陷阱：同一博弈，严格剔除什么都不删，弱剔除删掉一个真 NE ---
g = GAMES["弱占优陷阱博弈（01/E3）"]
print("\n弱占优陷阱博弈（行 U/D × 列 L/R）：")
for i in range(2):
    print("   " + "  ".join(f"({g['A'][i,j]:g},{g['B'][i,j]:g})" for j in range(2)))
surv_s = iterate_dominance(g["A"], g["B"], strict=True, label="同一博弈")
print("  → 严格 IESDS 一步未剔（R 不被严格占优：对 U 无差异）→ 两个 NE (U,R)/(D,L) 全部保留 ✓")
surv_w = iterate_dominance(g["A"], g["B"], strict=False, label="同一博弈")
print("  → ⚠ 陷阱兑现：弱占优剔除序列 R→U 收敛到 (D,L)，但 (U,R) 本是原博弈的真 NE（E2 已验证）")
print("     教训：弱占优剔除可能删除均衡、且结果依赖剔除顺序——只可作'参考点删除'；严格占优剔除永不删 NE")

# ======================================================================
# ne_basic.png：1×3 子图，三原型收益热图 + 纯 NE 红圈标注
# ======================================================================
proto = ["囚徒困境（T5 R3 P1 S0）", "性别战争（BoS）", "鹰鸽博弈（v=2, c=4）"]
titles = {
    "囚徒困境（T5 R3 P1 S0）": "唯一纯 NE (D,D)：背叛严格占优",
    "性别战争（BoS）": "两个纯 NE + 混合（行2/3, 列1/3）",
    "鹰鸽博弈（v=2, c=4）": "反协调：两非对称纯 NE + 混合 x*=0.5",
}
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
for ax, name in zip(axes, proto):
    gg = GAMES[name]
    A, B = gg["A"], gg["B"]
    ax.imshow(A, cmap="RdYlGn", vmin=-1.5, vmax=5.5, aspect="auto")
    ne = pure_ne_cells(A, B)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"({A[i,j]:g},{B[i,j]:g})", ha="center", va="center", fontsize=13)
    for (i, j) in ne:
        ax.scatter([j], [i], s=680, facecolors="none", edgecolors="red", linewidths=3)
    ax.set_xticks([0, 1], gg["col_act"]); ax.set_yticks([0, 1], gg["row_act"])
    ax.set_xlabel("列玩家", fontsize=11); ax.set_ylabel("行玩家", fontsize=11)
    ax.set_title(f"{name.split('（')[0]}\n{titles[name]}", fontsize=11)
fig.suptitle("三原型收益网格与纯策略纳什均衡（红圈 = 无人想单方偏离）", fontsize=13)
fig.tight_layout()
OUT = Path(__file__).resolve().parent / "ne_basic.png"   # 恒定落到 experiments/ 下，与运行 cwd 无关
fig.savefig(OUT, dpi=140)
print(f"\nsaved {OUT}")
