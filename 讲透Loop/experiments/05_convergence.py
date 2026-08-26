#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透Loop E5：循环的收敛与发散——IMPROVE 算子的不动点实验（09 章代码基座）

三个演示（全部数值可验）：
  D1  Banach 不动点：收缩映射收敛 / 非收缩发散的分界
      IMPROVE 算子建模为 g(x)=r*x*(1-x)（logistic 式改进映射）：
      |g'(x*)|<1 收缩 → 迭代收敛；|g'(x*)|>1 → 发散
      对照：E4 Phase A（收敛的守卫补丁序列）与 Phase B（发散的拆守卫）
  D2  学习律 (m+1)/2 = m − m/2 的收敛阶：MATH_LOOP_ENGINE 的遗忘-重学模型
      每轮忘掉一半、学回 (m+1)/2：剩余错误 e_{t+1} = e_t − (m+1)/2 * e_t/m …
      实际用简化模型 e_{t+1} = e_t * (1 - r) 的几何收敛 vs 重学模型的次线性
  D3  循环长度/成本期望的闭式 vs 蒙特卡洛对照（E2 的理论再验证）

输出：experiments/05_results.json + 05_convergence.png
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in font_manager.findSystemFonts(fontpaths=None, fontext="ttf"):
    if "NotoSansCJK" in f or "Noto Sans CJK" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

def improve_map(x, r):
    """IMPROVE 算子的玩具模型：当前质量 x∈[0,1]，改进强度 r。
    g(x) = x + r*x*(1-x)：离最优(1)越远改进越多，强度 r 控制步长。
    不动点 x*=1（最优）与 x*=0（躺平）。x*=1 处 g'(1)=1-r：
    r<2 收缩（收敛），r>2 发散振荡 —— 步长过大=改过头。"""
    return x + r * x * (1 - x)

def iterate(x0, r, n=40):
    xs = [x0]
    for _ in range(n):
        nx = improve_map(xs[-1], r)
        nx = min(nx, 1.5)  # 防 overflow，保留发散可见性
        xs.append(nx)
    return xs

def main():
    out = {}

    # ---------- D1：改进强度 r 的收敛/发散分界 ----------
    r_list = [0.5, 1.2, 1.8, 2.0, 2.4, 3.0]
    x0 = 0.3
    d1 = {}
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for r in r_list:
        traj = iterate(x0, r)
        conv = abs(traj[-1] - traj[-2]) < 1e-6
        d1[f"r={r}"] = dict(x_final=round(traj[-1], 6), converged=bool(conv),
                            note="|g'(1)|=|1-r|=" + f"{abs(1-r):.1f}" + (" <1 收缩" if abs(1-r) < 1 else " ≥1 发散"))
    for r, style in zip(r_list, ["-", "-", "-", "--", "--", "--"]):
        axes[0].plot(iterate(x0, r), label=f"r={r}", linestyle=style)
    axes[0].axhline(1.0, color="gray", alpha=0.5, lw=0.8)
    axes[0].set_xlabel("迭代 t（代）"); axes[0].set_ylabel("质量 x_t")
    axes[0].set_title("D1 IMPROVE 步长的分界：r<2 收敛，r>2 振荡发散\n（改进过猛 = 每代都在改过头）")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
    out["D1_step_size"] = d1

    # ---------- D2：遗忘-重学 vs 纯几何收敛 ----------
    # 模型A（纯几何）：每轮固定比例掌握剩余 e_{t+1} = e_t*(1-r)，r=0.35
    # 模型B（遗忘-重学）：每轮忘掉比例 f 的一半再学回：MATH_LOOP 的 (m+1)/2=m-m/2
    #   简化为 e_{t+1} = e_t*(1-r) + (1-e_t)*f   [学走 r 比例的错误，又混回 f 比例]
    r_learn, f_forget = 0.35, 0.10
    T = 30
    eA, eB = [1.0], [1.0]
    for _ in range(T):
        eA.append(eA[-1] * (1 - r_learn))
        eB.append(eB[-1] * (1 - r_learn) + (1 - eB[-1]) * f_forget)
    # 模型B 的不动点：e* = f / (r+f)  （遗忘把收敛地板抬到 f/(r+f)）
    e_star = f_forget / (r_learn + f_forget)
    axes[1].plot(eA, label=f"无遗忘：e_t·(1-{r_learn}) 几何收敛→0", color="#2e7d32")
    axes[1].plot(eB, label=f"遗忘-重学：学{r_learn}/忘{f_forget}", color="#c62828")
    axes[1].axhline(e_star, color="#c62828", alpha=0.6, linestyle="--",
                    label=f"收敛地板 e*=f/(r+f)={e_star:.2f}")
    axes[1].set_xlabel("迭代 t"); axes[1].set_ylabel("剩余错误 e_t")
    axes[1].set_title("D2 遗忘抬高收敛地板：无遗忘→0，有遗忘→f/(r+f)\n（循环的稳态错误由遗忘率决定，不由学习率单独决定）")
    axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)
    out["D2_forgetting"] = dict(
        eA_final=round(eA[-1], 6), eB_final=round(eB[-1], 6),
        e_star_theory=round(e_star, 6),
        lesson="遗忘率 f 与学习率 r 共同决定稳态：e*=f/(r+f)。想降地板：降遗忘(state file!)或升学习",
    )

    # ---------- D3：循环成本的闭式 vs 蒙特卡洛 ----------
    # E2 模型的理论：E[turns]（到成功）= W/p（负二产期望）；对照模拟
    W, p, p_leak = 8, 0.35, 0.01
    rng = np.random.default_rng(42)
    N = 20000
    turns = []
    for _ in range(N):
        w, t = W, 0
        while w > 0 and t < 500:
            t += 1
            if rng.random() < p:
                w -= 1
        turns.append(t)
    mc = float(np.mean(turns))
    theory = W / p
    # 累积早停率：闭式 1-(1-p_leak)^(W/p) vs 同一模拟的实测
    theo_leak = 1 - (1 - p_leak) ** theory
    axes[2].bar([0], [theory], width=0.4, label=f"闭式 W/p={theory:.1f}", color="#1565c0")
    axes[2].bar([1], [mc], width=0.4, label=f"蒙特卡洛={mc:.1f}", color="#90caf9")
    axes[2].text(0.5, theory * 0.5, f"偏差 {abs(theory-mc)/theory*100:.1f}%", ha="center", fontsize=11)
    axes[2].set_xticks([0, 1]); axes[2].set_xticklabels(["闭式公式", "蒙特卡洛 N=20k"])
    axes[2].set_ylabel("E[轮数]")
    axes[2].set_title(f"D3 循环成本闭式律验证：E[T]=W/p\n（累积早停率闭式 {theo_leak*100:.1f}% ↔ E2 实测 19.4%）")
    axes[2].legend(); axes[2].grid(axis="y", alpha=0.3)
    out["D3_closed_form"] = dict(E_turns_theory=theory, E_turns_mc=mc,
                                 deviation_pct=round(abs(theory - mc) / theory * 100, 2),
                                 premature_theory_pct=round(theo_leak * 100, 1),
                                 premature_E2_observed_pct=19.4)

    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "05_convergence.png"), dpi=130)
    with open(os.path.join(HERE, "05_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("saved:", os.path.join(HERE, "05_convergence.png"))

    print("\n===== D1 步长分界 =====")
    for k, v in d1.items():
        print(f"  {k:8s} x_final={v['x_final']:.4f}  收敛={v['converged']}  ({v['note']})")
    print("\n===== D2 遗忘地板 =====")
    print(f"  无遗忘 30 轮后 e={eA[-1]:.5f} | 有遗忘 e={eB[-1]:.4f} | 理论地板 e*={e_star:.4f}")
    print("\n===== D3 闭式 vs 模拟 =====")
    print(f"  E[T]: 闭式 {theory:.1f} vs 蒙特卡洛 {mc:.1f}（偏差 {abs(theory-mc)/theory*100:.1f}%）")
    print(f"  累积早停: 闭式 {theo_leak*100:.1f}% vs E2 实测 19.4%")

if __name__ == "__main__":
    main()
