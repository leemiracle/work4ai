#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透Loop E1+E2：内循环解剖 × 停止条件三守卫对比（循环动力学模拟器）

设计决策（为什么用模拟器不用真 LLM）：
  循环级动力学（成本累积/停止时点/停滞检测）是确定性数学。行为模拟器能
  精确控制参数（自评虚报率/验证器漏检率/停滞概率）做消融——真 0.5B 模型
  在循环任务上退化为噪声，给不出干净曲线（项目已知教训）。

模型：
  任务有剩余工作量 W（整数单位）。每轮：
    - agent 以 p_progress 推进 1 单位（消耗 c token）
    - 停止策略判断是否停：
      * self   自评停止：模型自报"完成"。W>0 时仍以 p_claim_idle 虚报（过度自信）
      * machine 机器可查：跑测试。W>0 时测试仍绿的概率 = p_leak（漏检率）
      * machine+cb  机器可查+熔断：连续 K 轮无进展 → stalled 终态
  hard cap：超过 cap 轮 → exhausted 终态（可关闭，演示失控烧钱）

终态（对齐 2607.00038 的五终态命名，取其中四个）：
  success  真完成且停了 / premature(早停) 假完成被放行 / stalled 熔断 / exhausted 烧穿上限

输出：experiments/01_results.json + 01_loop_dynamics.png
"""
import json, os, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- 中文字体铁律 ----
for f in font_manager.findSystemFonts(fontpaths=None, fontext="ttf"):
    if "NotoSansCJK" in f or "Noto Sans CJK" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

P = dict(          # 全部模拟器参数（显式落盘，可复现）
    W0=8,            # 初始剩余工作单位
    p_progress=0.35, # 每轮真实推进概率
    p_claim_done=0.95,   # 真完成时自报完成概率
    p_claim_idle=0.10,   # 未完成时虚报完成概率（模型过度自信）
    p_leak=0.01,     # 机器验证漏检率（W>0 但测试绿）。注意：多轮累积早停率≈1-(1-p_leak)^T
    K_stall=8,       # 熔断阈值：连续 K 轮无进展。权衡：太小→误熔断(p_progress低时)，太大→止损慢
    cap=60,          # hard cap（None=无上限，演示失控）
    c_per_turn=2000, # 每轮 token 成本
    N=10000,         # 蒙特卡洛次数
    seed=42,
)

TERMINAL = ("success", "premature", "stalled", "exhausted")

def run_once(strategy, rng, W0, p_progress, p_claim_done, p_claim_idle,
             p_leak, K_stall, cap, c_per_turn, p_progress_actual=None):
    """单次 loop 仿真。返回 (终态, 总轮数, 总token, 停止时真实剩余工作)"""
    if p_progress_actual is None:
        p_progress_actual = p_progress
    W = W0
    stall = 0
    t = 0
    while True:
        t += 1
        progressed = rng.random() < p_progress_actual
        if progressed and W > 0:
            W -= 1
            stall = 0
        else:
            stall += 1
        tokens = t * c_per_turn
        # --- 停止判定（Loop Engineering 全部押在这） ---
        if strategy == "self":
            done_claim = rng.random() < (p_claim_done if W == 0 else p_claim_idle)
            if done_claim:
                return ("success" if W == 0 else "premature"), t, tokens, W
        else:  # machine / machine+cb
            test_green = rng.random() < ((1.0) if W == 0 else p_leak)
            if test_green:
                return ("success" if W == 0 else "premature"), t, tokens, W
            if strategy == "machine+cb" and stall >= K_stall:
                return "stalled", t, tokens, W
        if cap is not None and t >= cap:
            return ("success" if W == 0 else "exhausted"), t, tokens, W

def monte_carlo(strategy, N, **kw):
    rng = random.Random(P["seed"] + abs(hash(strategy)) % 10000)
    out = {"terminal": {k: 0 for k in TERMINAL}, "tokens": [], "turns": [], "W_left": []}
    for _ in range(N):
        term, t, tok, W = run_once(strategy, rng, **kw)
        out["terminal"][term] += 1
        out["tokens"].append(tok)
        out["turns"].append(t)
        out["W_left"].append(W)
    n = N
    return {
        "terminal_pct": {k: v / n * 100 for k, v in out["terminal"].items()},
        "tokens_mean": float(np.mean(out["tokens"])),
        "tokens_p50": float(np.percentile(out["tokens"], 50)),
        "tokens_p95": float(np.percentile(out["tokens"], 95)),
        "turns_mean": float(np.mean(out["turns"])),
        "wasted_tokens_mean": float(np.mean([t * kw["c_per_turn"] for t, W in zip(out["turns"], out["W_left"]) if W > 0])) if any(W > 0 for W in out["W_left"]) else 0.0,
        "_raw_tokens": out["tokens"],
    }

def main():
    kw = dict(W0=P["W0"], p_progress=P["p_progress"],
              p_claim_done=P["p_claim_done"], p_claim_idle=P["p_claim_idle"],
              p_leak=P["p_leak"], K_stall=P["K_stall"], cap=P["cap"],
              c_per_turn=P["c_per_turn"])

    # ============ E1：最小内循环演示（一次 self 策略 run 的逐轮轨迹） ============
    rng = random.Random(7)
    traj = []
    W, t = P["W0"], 0
    while t < 40:
        t += 1
        prog = rng.random() < P["p_progress"]
        if prog and W > 0:
            W -= 1
        claim = rng.random() < (P["p_claim_done"] if W == 0 else P["p_claim_idle"])
        traj.append({"turn": t, "W_left": W, "progressed": prog, "claims_done": claim})
        if claim:
            break
    e1_demo = {
        "loop": "while not done: act -> observe -> check_stop",
        "trace": traj,
        "ended_at_turn": t,
        "ended_by": "self-claim",
        "real_W_left": W,
        "verdict": "PREMATURE(早停)" if W > 0 else "SUCCESS",
    }

    # ============ E2a：三策略蒙特卡洛 ============
    strategies = ["self", "machine", "machine+cb"]
    results = {s: monte_carlo(s, P["N"], **kw) for s in strategies}

    # ============ E2b：失控实验——同一 agent，无 hard cap，agent 卡死（p=0.05） ============
    kw_nocap_dead = dict(kw, cap=None, p_progress=0.05)
    kw_cap_dead = dict(kw, p_progress=0.05)
    runaway = {
        "self_nocap": monte_carlo("self", 2000, **kw_nocap_dead),
        "machine_nocap": monte_carlo("machine", 2000, **kw_nocap_dead),
        "machine+cb_nocap": monte_carlo("machine+cb", 2000, **kw_nocap_dead),
        "machine_cap60": monte_carlo("machine", 2000, **kw_cap_dead),
    }
    # machine 无 cap 且漏检率>0：几何等待 1/p_leak —— 记录理论期望轮数对照
    runaway["theory_E_turns_machine_nocap(p_leak=0.02)"] = 1 / kw["p_leak"]

    # ============ E2c：p_progress 扫描 × 策略 → 平均成本曲线 ============
    sweep = {"p_list": [0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9], "curves": {}}
    for s in strategies:
        curve = []
        for pp in sweep["p_list"]:
            r = monte_carlo(s, 3000, **dict(kw, p_progress=pp))
            curve.append({"p": pp, "tokens_mean": r["tokens_mean"],
                          "premature_pct": r["terminal_pct"]["premature"],
                          "exhausted_pct": r["terminal_pct"]["exhausted"]})
        sweep["curves"][s] = curve

    # ============ 落盘 json ============
    out = {"params": P, "E1_demo": e1_demo,
           "E2a_three_guards": {s: {k: v for k, v in r.items() if k != "_raw_tokens"}
                                for s, r in results.items()},
           "E2b_runaway": {k: {kk: vv for kk, vv in r.items() if kk != "_raw_tokens"}
                           for k, r in runaway.items() if isinstance(r, dict)}
                          | {"theory_E_turns_machine_nocap(p_leak=0.02)": runaway["theory_E_turns_machine_nocap(p_leak=0.02)"]},
           "E2c_sweep": sweep}
    with open(os.path.join(HERE, "01_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ============ 画图（三联） ============
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    # 图1：三策略终态占比 + 成本
    labels = ["自评停止", "机器可查", "机器可查+熔断"]
    xs = np.arange(3)
    bottom = np.zeros(3)
    colors = {"success": "#2e7d32", "premature": "#c62828", "stalled": "#ef6c00", "exhausted": "#6a1b9a"}
    names_cn = {"success": "成功", "premature": "早停(假完成)", "stalled": "熔断止损", "exhausted": "烧穿上限"}
    for term in TERMINAL:
        vals = np.array([results[s]["terminal_pct"][term] for s in strategies])
        axes[0].bar(xs, vals, bottom=bottom, label=names_cn[term], color=colors[term])
        bottom += vals
    for i, s in enumerate(strategies):
        axes[0].text(i, 102, f"均 {results[s]['tokens_mean']/1000:.0f}k tok",
                     ha="center", fontsize=10, fontweight="bold")
    axes[0].set_xticks(xs); axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("终态占比 %"); axes[0].set_ylim(0, 115)
    axes[0].set_title(f"E2a 停止策略三守卫对比（N={P['N']}）\n自评虚报率={P['p_claim_idle']}, 验证漏检率={P['p_leak']}")
    axes[0].legend(loc="lower right", fontsize=9)

    # 图2：卡死 agent（p=0.05）四种配置的平均 token（log 刻度）
    cfgs = ["自评\n无cap", "机器可查\n无cap", "机器+熔断\n无cap", "机器可查\ncap=60"]
    r_keys = ["self_nocap", "machine_nocap", "machine+cb_nocap", "machine_cap60"]
    vals = [runaway[k]["tokens_mean"] for k in r_keys]
    bars = axes[1].bar(np.arange(4), vals,
                       color=["#c62828", "#c62828", "#ef6c00", "#2e7d32"])
    axes[1].set_yscale("log")
    for i, v in enumerate(vals):
        axes[1].text(i, v * 1.15, f"{v/1000:.0f}k", ha="center", fontsize=10, fontweight="bold")
    axes[1].set_xticks(np.arange(4)); axes[1].set_xticklabels(cfgs, fontsize=10)
    axes[1].set_ylabel("平均 token（log）")
    axes[1].set_title("E2b 卡死 agent（每轮真实推进率=0.05）\n无 cap + 机器验证 = 几何等待 1/p_leak=50 轮起步\n熔断在第 4 轮截断，cap 是最后防线")

    # 图3：p_progress 扫描成本曲线
    for s, cn in zip(strategies, labels):
        axes[2].plot([c["p"] for c in sweep["curves"][s]],
                     [c["tokens_mean"] / 1000 for c in sweep["curves"][s]],
                     marker="o", label=cn)
    axes[2].set_xlabel("每轮真实推进率 p_progress"); axes[2].set_ylabel("平均 token (k)")
    axes[2].set_title("E2c 推进率扫描：越强的 agent 优势越小？\n守卫的价值在低 p 区（左侧）最大")
    axes[2].legend(); axes[2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "01_loop_dynamics.png"), dpi=130)
    print("saved:", os.path.join(HERE, "01_loop_dynamics.png"))

    # ============ 终端摘要 ============
    print("\n===== E1 最小内循环（self 策略单次轨迹） =====")
    print(f"  第 {e1_demo['ended_at_turn']} 轮自报完成 → 真实剩余工作 W={e1_demo['real_W_left']} → {e1_demo['verdict']}")
    print("\n===== E2a 三守卫对比 =====")
    for s, cn in zip(strategies, labels):
        r = results[s]
        print(f"  {cn:12s} 成功 {r['terminal_pct']['success']:5.1f}% | 早停 {r['terminal_pct']['premature']:5.1f}% | "
              f"熔断 {r['terminal_pct']['stalled']:5.1f}% | 烧穿 {r['terminal_pct']['exhausted']:5.1f}% | 均 {r['tokens_mean']/1000:.0f}k tok")
    print("\n===== E2b 卡死 agent 失控实验 =====")
    for k, cn in zip(r_keys, cfgs):
        print(f"  {cn.replace(chr(10),' '):14s} 均 {runaway[k]['tokens_mean']/1000:8.0f}k tok")
    print(f"  理论：机器可查无cap，卡死时 E[轮数]≈1/p_leak={1/P['p_leak']:.0f} 轮（漏检漏出的出口）")

if __name__ == "__main__":
    main()
