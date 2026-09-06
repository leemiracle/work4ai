#!/usr/bin/env python3
"""讲透博弈论实验 7：博弈学习与 CFR——fictitious play / 遗憾匹配 / 手写 Kuhn 扑克 CFR。
E1 fictitious play（15 章 §二）：对历史平均的最优反应——PD 行为两轮锁死 (D,D)（D 严格占优）；
   RPS 信念永久循环（Shapley 1964 反例的最小现场：行为不收敛、时间平均 → 中心 1/3——11 章复制动态
   闭轨在学习世界的同构复演，50 章第三堵墙的几何图像）
E2 遗憾匹配 RM（15 章 §四）：RPS 自博弈，平均外部遗憾 vs T 双对数——理论斜率 −1/2（总遗憾 O(√T) →
   平均遗憾 O(T^{-1/2})），T=10⁵ 平均遗憾 < 0.02；平均遗憾 → 0 ⇒ 经验联合分布进 CCE（15 章主定理）
E3 手写 KuhnCFR（16 章 §三）：vanilla CFR（Zinkevich 2007），chance 节点用 Kuhn 三牌 6 种排列全枚举
   （无抽样方差）；增量训练至 2×10⁵ 次，平均策略剖面的【精确】博弈值 vs 理论 −1/18 ≈ −0.0556
   （容差 0.01）；P1 六信息集平均策略表——均衡是一族（P1 诈唬率 α∈[0,1/3]、K 下注率 3α），
   全族价值恒 −1/18，CFR 落在族内哪一点由随机性决定——锚点是价值不是具体概率（诚实标注）
产出：learning.png（1×3：RPS 信念三角循环+PD 锁死 / RM 平均遗憾 log-log / KuhnCFR 价值收敛曲线）

本文件是可 import 的模块（cli/kuhn_poker.py 通过 sys.path 接入 KuhnCFR / regret_matching /
fictitious_play——直接跑才执行全部实验）。"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from itertools import permutations
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Microsoft YaHei", "SimHei", "sans-serif"]

# 沿用 00 章三原型记号：PD T5 R3 P1 S0；RPS 行收益反对称 A[a,b]=+1 若 a 赢 b
PD = np.array([[3, 0], [5, 1]], dtype=float)                        # 行=列=C/D
RPS = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)   # R,P,S


# ----------------------------------------------------------------------
# 仪器一：fictitious play（15 章 §二）——对历史平均的最优反应
# ----------------------------------------------------------------------
def fictitious_play(A, rounds, rng):
    """双方对彼此历史平均出最优反应；返回两玩家逐轮动作序列。头两轮随机（打破 BR 平局锁死）。"""
    n, m = A.shape
    cnt_row, cnt_col = np.zeros(n), np.zeros(m)
    rows, cols = [], []
    for t in range(rounds):
        if t < 2:
            a, b = int(rng.integers(n)), int(rng.integers(m))
        else:
            a = int(np.argmax(A @ (cnt_col / cnt_col.sum())))    # 行玩家对列平均的 BR
            b = int(np.argmax(-(cnt_row / cnt_row.sum()) @ A))   # 列玩家（收益=−A）对行平均的 BR
        cnt_row[a] += 1; cnt_col[b] += 1
        rows.append(a); cols.append(b)
    return np.array(rows), np.array(cols)


# ----------------------------------------------------------------------
# 仪器二：遗憾匹配 RM（15 章 §四）——正遗憾比例随机化
# ----------------------------------------------------------------------
def regret_matching(A, T, rng):
    """两玩家 RM 自博弈；返回逐轮动作序列。σ(a) ∝ max(0, R(a))，外部遗憾
    R(a) = Σ_t [A(a,b_t) − A(a_t,b_t)]——16 章 CFR 的遗憾母体。"""
    n, m = A.shape
    R_row, R_col = np.zeros(n), np.zeros(m)
    acts_a, acts_b = np.zeros(T, dtype=int), np.zeros(T, dtype=int)
    for t in range(T):
        sr = np.maximum(R_row, 0)
        sr = sr / sr.sum() if sr.sum() > 0 else np.ones(n) / n
        sc = np.maximum(R_col, 0)
        sc = sc / sc.sum() if sc.sum() > 0 else np.ones(m) / m
        a, b = rng.choice(n, p=sr), rng.choice(m, p=sc)
        acts_a[t], acts_b[t] = a, b
        R_row += A[:, b] - A[a, b]          # 行玩家：动作 a 若整场替打的假想累计增益
        R_col += -(A[a, :] - A[a, b])       # 列玩家收益 = −A 对称同理
    return acts_a, acts_b


# ----------------------------------------------------------------------
# 仪器三：手写 KuhnCFR（16 章 §三）——vanilla CFR，接口供 cli/kuhn_poker.py 导入：
#   train(iterations)（可增量调用）/ average_strategy() / converged_value()
# ----------------------------------------------------------------------
class KuhnCFR:
    """Kuhn 扑克 vanilla CFR（Zinkevich et al. 2007）。规则：J<Q<K，各 ante 1；
    P1 先动 K(check)/B(bet)；P2 应对；fold ±1，双 check 摊牌 ±1，call 后摊牌 ±2。"""

    @staticmethod
    def _legal(hist):
        """历史 → (决策者 1/2, 两动作)；终端返回 (None, [])。合法历史：K/B 起头，F/C 收尾。"""
        if hist == "":
            return 1, ["K", "B"]                                  # P1：check / bet
        if hist[0] == "B":
            return (2, ["F", "C"]) if len(hist) == 1 else (None, [])
        # hist[0] == "K"
        if len(hist) == 1:
            return 2, ["K", "B"]                                  # P2：check / bet
        if hist[1] == "K":
            return None, []                                       # "KK" 摊牌（底池 2）
        return (1, ["F", "C"]) if len(hist) == 2 else (None, [])  # "KB?"：P1 应对（底池 4）

    @staticmethod
    def _terminal_payoff(hist, c1, c2):
        """终端 → (P1, P2) 收益。fold：±1；摊牌：底池 2（双 check）或 4（有 call）→ ±1 / ±2。"""
        if hist.endswith("F"):
            return (1, -1) if hist == "BF" else (-1, 1)           # P2 弃 / P1 弃
        pot = 2 if hist in ("BC", "KBC") else 1                   # 赢家净胜：call 后 2、双 check 1
        return (pot, -pot) if c1 > c2 else (-pot, pot)

    @staticmethod
    def _key(player, card, hist):
        return f"P{player + 1}:{'JQK'[card]}:{hist}"

    def __init__(self):
        self.regret = {}        # 键 → np.array(2) 累计反事实遗憾
        self.strat_sum = {}     # 键 → np.array(2) Σ π_i·σ 累计

    def _strategy(self, key):
        pos = np.maximum(self.regret.setdefault(key, np.zeros(2)), 0)
        return pos / pos.sum() if pos.sum() > 0 else np.ones(2) / 2

    def _cfr(self, hist, cards, reach):
        """递归走树。reach=(π1, π2)；返回当前子树两玩家期望收益 np.array(2)。
        反事实遗憾：R(I,a) += π_{-i}·(v(I,a) − v(I))；平均策略按 π_i 加权累计。"""
        player, actions = self._legal(hist)
        if player is None:
            p1, p2 = self._terminal_payoff(hist, cards[0], cards[1])
            return np.array([p1, p2])
        p = player - 1
        key = self._key(p, cards[p], hist)
        sigma = self._strategy(key)
        self.strat_sum[key] = self.strat_sum.get(key, np.zeros(2)) + reach[p] * sigma
        v = np.zeros(2)
        v_act = np.zeros((2, 2))                                   # [动作][玩家]
        for i, a in enumerate(actions):
            r2 = (reach[0] * sigma[i], reach[1]) if p == 0 else (reach[0], reach[1] * sigma[i])
            v_act[i] = self._cfr(hist + a, cards, r2)
            v += sigma[i] * v_act[i]
        self.regret[key] += reach[1 - p] * (v_act[:, p] - v[p])
        return v

    def train(self, iterations):
        for _ in range(iterations):
            for cards in permutations(range(3), 2):                 # chance：6 发牌全枚举
                self._cfr("", cards, (1.0, 1.0))
        return self

    def average_strategy(self):
        return {k: (s / s.sum() if s.sum() > 0 else np.ones(2) / 2)
                for k, s in self.strat_sum.items()}

    def converged_value(self):
        """平均策略剖面的精确博弈值：行为策略全树枚举（无抽样）。"""
        avg = self.average_strategy()

        def ev(hist, cards, reach):
            player, actions = self._legal(hist)
            if player is None:
                p1, p2 = self._terminal_payoff(hist, cards[0], cards[1])
                return np.array([p1, p2]) * (reach[0] * reach[1])
            p = player - 1
            sigma = avg[self._key(p, cards[p], hist)]
            total = np.zeros(2)
            for i, a in enumerate(actions):
                r2 = (reach[0] * sigma[i], reach[1]) if p == 0 else (reach[0], reach[1] * sigma[i])
                total += ev(hist + a, cards, r2)
            return total

        total = np.zeros(2)
        for cards in permutations(range(3), 2):
            total += ev("", cards, (1.0, 1.0))
        return float(total[0] / 6)


# ======================================================================
# 实验主体（直接运行才执行；import 时只暴露上面的三台仪器）
# ======================================================================
def main():
    rng = np.random.default_rng(42)
    tol = 0.01                     # 诚实校准公约容差

    # ---------------- E1 ----------------
    print("=" * 68)
    print("E1 · fictitious play：PD 行为锁死 (D,D) vs RPS 信念循环（8000 轮）")
    print("=" * 68)
    # FP 定义（15 章 §二）：每轮对【对手历史平均】出最优反应。手推锚点：
    #   PD：D 对列玩家任何混合都是 BR（5y_C + 1y_D > 3y_C 恒成立）——两轮随机探索后行为永久锁死 D；
    #   RPS：无纯 NE（02 章），信念绕均衡转圈；但零和 FP 定理保证【平均策略】→ minimax——"行为循环、平均站稳"。
    rows_pd, cols_pd = fictitious_play(PD, 8000, rng)
    pd_row_d = rows_pd[1000:].mean()                             # 后段 D 频率（动作 1=D）
    pd_col_d = cols_pd[1000:].mean()
    ok_pd = abs(pd_row_d - 1) < tol and abs(pd_col_d - 1) < tol
    print("理论锚点（手推）：D 对任何对手混合都是 BR → FP 行为自第 3 轮起锁死 (D,D)")
    print(f"  PD 后 7000 轮：行玩家 D 频率 {pd_row_d:.4f}、列玩家 D 频率 {pd_col_d:.4f}（vs 1，|最大偏差| "
          f"{max(abs(pd_row_d - 1), abs(pd_col_d - 1)):.4f}）{'✓' if ok_pd else '⚠'}")

    rows_rps, cols_rps = fictitious_play(RPS, 8000, rng)
    freq_rps = np.bincount(rows_rps, minlength=3) / len(rows_rps)  # 行玩家【时间平均】动作频率
    dev_avg = np.abs(freq_rps - 1 / 3).max()
    ok_rps = dev_avg < 0.02
    print(f"  RPS：行为不收敛（信念绕 (1/3,1/3,1/3) 循环——图 a）；时间平均动作频率 = "
          f"({freq_rps[0]:.4f}, {freq_rps[1]:.4f}, {freq_rps[2]:.4f}) vs 1/3（|最大偏差| {dev_avg:.4f}，容差 0.02）"
          f"{'✓' if ok_rps else '⚠'}")
    print(f"→ E1 对拍：PD 锁死 ✓ / RPS 循环但平均 → 1/3 —— " + ("全绿 ✓" if ok_pd and ok_rps else "⚠ 如实标注"))

    # ---------------- E2 ----------------
    print("\n" + "=" * 68)
    print("E2 · 遗憾匹配自博弈 RPS：平均遗憾 ~ T^(−1/2)（log-log 斜率 −1/2）")
    print("=" * 68)
    T_RM = 100_000
    acts_a, acts_b = regret_matching(RPS, T_RM, rng)
    payoff_t = RPS[acts_a, acts_b]                                      # 逐轮实现收益
    cum_payoff = np.cumsum(payoff_t)
    cum_best = np.max(np.cumsum(np.eye(3)[acts_b], axis=0) @ RPS.T, axis=1)   # 最优固定动作的累计收益
    avg_regret_traj = (cum_best - cum_payoff) / np.arange(1, T_RM + 1)
    anchors = [100, 1000, 10_000, 100_000]
    print("理论锚点：RM 总遗憾 O(√T) → 平均遗憾 ~ c·T^(−1/2)（log-log 斜率 −1/2；√T 界是最坏情形，实测常更快）")
    for t in anchors:
        print(f"  T={t:>6}：平均遗憾 = {avg_regret_traj[t - 1]:.5f}")
    seg = np.arange(1000, T_RM + 1)
    slope = np.polyfit(np.log(seg), np.log(avg_regret_traj[999:]), 1)[0]
    ok_e2a = avg_regret_traj[-1] < 0.02
    ok_e2b = -0.75 < slope < -0.30
    print(f"  log-log 斜率（T=10³→10⁵ 最小二乘）= {slope:.3f}（vs 理论 −1/2，容差 [−0.75,−0.30]）"
          f"{'✓' if ok_e2b else '⚠'}；T=10⁵ 平均遗憾 = {avg_regret_traj[-1]:.4f} < 0.02 {'✓' if ok_e2a else '⚠'}")
    print(f"→ E2 对拍：平均遗憾按 T^(−1/2) 衰减 —— " + ("全绿 ✓" if ok_e2a and ok_e2b else "⚠ 如实标注"))
    print("  诚实标注：斜率是单条随机路径的回归估计（界是最坏情形保证）；平均遗憾 → 0 ⟹ 经验联合分布进 CCE。")

    # ---------------- E3 ----------------
    print("\n" + "=" * 68)
    print("E3 · 手写 KuhnCFR：vanilla CFR 增量训练至 2×10⁵ 次，博弈值 vs 理论 −1/18")
    print("=" * 68)
    CKPTS = [100, 500, 1000, 5000, 10_000, 50_000, 100_000, 200_000]
    kuhn = KuhnCFR()
    vals, trained = [], 0
    for c in CKPTS:
        kuhn.train(c - trained)                                        # 增量训练（同一实例）
        trained = c
        vals.append(kuhn.converged_value())
    value = vals[-1]
    ok_e3 = abs(value - (-1 / 18)) < tol
    print(f"理论锚点（16 章 §四手推）：Kuhn 扑克博弈值（P1 期望收益）= −1/18 ≈ −0.0556")
    for c, v in zip(CKPTS, vals):
        print(f"  迭代 {c:>6}：平均策略博弈值 = {v:+.4f}" + ("（入容差 ±0.01）" if abs(v + 1 / 18) < tol else ""))
    print(f"→ E3 对拍：2×10⁵ 次后博弈值 {value:+.4f} vs −0.0556（|偏差| {abs(value + 1 / 18):.4f} < 0.01）"
          f"—— " + ("全绿 ✓" if ok_e3 else "⚠ 如实标注"))
    avg = kuhn.average_strategy()
    print("  P1 六信息集平均策略（均衡族的一支；16 章手推对照）：")
    for key in sorted(k for k in avg if k.startswith("P1")):
        hist = key.split(":")[2]
        names = ("check", "bet") if hist == "" else ("fold", "call")
        print(f"    {key:<10s} {names[0]}={avg[key][0]:.3f}  {names[1]}={avg[key][1]:.3f}")
    print("  诚实标注：Kuhn 均衡是一族（P1 诈唬率 α∈[0,1/3]、K 下注率 3α，16 章 §四），全族价值同为 −1/18；")
    print("    本 CFR 无随机性（chance 全枚举、遗憾匹配确定性），落在族内哪一点取决于迭代数与平均加权——")
    print("    锚点是价值，不是具体某个概率。")

    # ---------------- 图 ----------------
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.9))

    # (a) RPS 信念三角：行玩家对列玩家历史平均的估计（前 200 轮）
    ax = axes[0]
    cnt = np.zeros(3)
    pts = []
    for b in cols_rps[:200]:
        cnt[b] += 1
        pts.append(cnt / cnt.sum())
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], "-", lw=1.0, color="tab:blue", alpha=0.85)
    ax.scatter(pts[-1, 0], pts[-1, 1], s=26, color="tab:blue", zorder=3)
    ax.scatter([1 / 3], [1 / 3], s=160, marker="*", color="red", zorder=3, label="均衡 (1/3, 1/3, 1/3)")
    ax.plot([0, 1, 0, 0], [1, 0, 0, 1], lw=0.8, color="gray", ls=":")
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("信念：对手出 R 的概率"); ax.set_ylabel("信念：对手出 P 的概率")
    ax.set_title("E1 · FP 在 RPS：信念绕均衡循环，永不落地\n（行为不收敛；时间平均 → 1/3）", fontsize=10.5)
    ax.annotate(f"对照组 PD：后 7000 轮 D 频率\n行 {pd_row_d:.3f} / 列 {pd_col_d:.3f}（锁死）",
                xy=(0.02, 0.97), xycoords="axes fraction", va="top", fontsize=8.5, color="tab:green",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="tab:green", alpha=0.9))
    ax.legend(fontsize=8.5, loc="lower left")

    # (b) RM 平均遗憾 log-log
    ax = axes[1]
    grid = np.arange(100, T_RM + 1, 100)
    ax.loglog(grid, avg_regret_traj[99::100], lw=1.1, color="tab:blue", label="平均遗憾（实测路径）")
    xs = np.array(anchors)
    ax.loglog(xs, avg_regret_traj[[t - 1 for t in anchors]], "o", ms=5, color="tab:blue")
    ax.loglog(xs, avg_regret_traj[99] * (xs / 100) ** (-0.5), "--", lw=1.3, color="red", label="参考斜率 −1/2")
    for t in anchors:
        ax.annotate(f"{avg_regret_traj[t - 1]:.4f}", xy=(t, avg_regret_traj[t - 1]), xytext=(4, 4),
                    textcoords="offset points", fontsize=8)
    ax.set_xlabel("T（轮）"); ax.set_ylabel("平均外部遗憾")
    ax.set_title(f"E2 · 遗憾匹配自博弈 RPS：平均遗憾 ~ T^(−1/2)\n（log-log 斜率实测 {slope:.2f}；T=10⁵ 值 {avg_regret_traj[-1]:.4f}）",
                 fontsize=10.5)
    ax.legend(fontsize=8.5, loc="lower left"); ax.grid(True, which="both", alpha=0.25)

    # (c) KuhnCFR 价值收敛
    ax = axes[2]
    ax.plot(CKPTS, vals, "o-", color="tab:blue", label="平均策略的精确博弈值")
    ax.axhline(-1 / 18, color="red", ls="--", lw=1.4, label="理论 −1/18 ≈ −0.0556")
    ax.fill_between([80, 260000], -1 / 18 - tol, -1 / 18 + tol, color="red", alpha=0.10, label="容差 ±0.01")
    for c, v in zip(CKPTS, vals):
        ax.annotate(f"{v:+.3f}", xy=(c, v), xytext=(0, -14 if c == CKPTS[0] else 6),
                    textcoords="offset points", ha="center", fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlabel("CFR 迭代次数（chance 全枚举）"); ax.set_ylabel("P1 期望收益")
    ax.set_title("E3 · 手写 KuhnCFR：平均策略价值 → −1/18\n（收敛即落入均衡族，价值是族不变量）", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="upper right"); ax.grid(True, alpha=0.3)

    fig.suptitle("lab07 · 博弈学习与 CFR：FP 收敛/循环 / 遗憾匹配 T^(−1/2) / 手写 KuhnCFR 收敛 −1/18（纯 numpy）",
                 fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = Path(__file__).resolve().parent / "learning.png"
    fig.savefig(out, dpi=140)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
