#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透Loop E4：外环闭环实验——trace → 分析 → 改配置 → 重跑（hill climbing / Goodhart 双相）

LangChain 四层循环的第 4 层（hill climbing loop）：外环不改进任务产物，而是读内环
运行轨迹（trace），分析问题，修改内环配置（harness），再跑。本实验用规则型"分析 agent"
复现这个闭环，并做诚实/污染双相对照：

Phase A（诚实外环，reward=真成功率）：
  Gen0 裸奔配置 {stop=self, 无熔断, 无cap} → 跑混合任务集 → 读 trace 统计
  分析规则（一次读 trace，批量出补丁）：
    R1 早停率>15%        → stop=machine  （自评虚报在循环里复利）
    R2 最长轮数>50 且无熔断 → K_stall=8   （卡死任务无止损）
    R3 p95成本>120k 且无cap → cap=60      （尾部成本失控）
  循环直到无补丁（收敛）。

Phase B（污染外环，reward=自称产出率 claimed/tokens，模拟"降本增效"接管）：
  从 Phase A 收敛配置出发：
    RH1 stop=machine → self（"验证调用不产生 claimed 增益，纯成本"）
  一刀拆掉验证阶梯 → 收敛。剪刀差：产出指标大涨，真成功率崩塌。

任务集：8 正常（p_progress=0.35）+ 4 卡死倾向（p=0.05），W=8，c=2000 tok/轮。
输出：experiments/04_results.json + 04_outer_loop.png
"""
import json, os, random
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

P = dict(
    tasks=[{"W": 8, "p": 0.35, "type": "normal"}] * 8 + [{"W": 8, "p": 0.05, "type": "hard"}] * 4,
    p_claim_done=0.95, p_claim_idle=0.10, p_leak=0.01,
    c_per_turn=2000, K_default=8, cap_default=60,
    reps=400, max_gens=5, seed=42,
)

def run_task(cfg, task, rng):
    """内循环单任务仿真（与 E1/E2 同一动力学）。"""
    W, stall, t = task["W"], 0, 0
    while True:
        t += 1
        if W > 0 and rng.random() < task["p"]:
            W, stall = W - 1, 0
        else:
            stall += 1
        if cfg["stop"] == "self":
            if rng.random() < (P["p_claim_done"] if W == 0 else P["p_claim_idle"]):
                return dict(term="success" if W == 0 else "premature", claimed=True, turns=t)
        else:
            if rng.random() < (1.0 if W == 0 else P["p_leak"]):
                return dict(term="success" if W == 0 else "premature", claimed=True, turns=t)
            if cfg.get("K_stall") and stall >= cfg["K_stall"]:
                return dict(term="stalled", claimed=False, turns=t)
        if cfg.get("cap") and t >= cfg["cap"]:
            return dict(term="success" if W == 0 else "exhausted", claimed=(W == 0), turns=t)

def evaluate(cfg, gen):
    """跑一整代：任务集 × reps，产出 trace 统计。"""
    rng = random.Random(P["seed"] * 100 + gen)
    recs = []
    for ti, task in enumerate(P["tasks"]):
        for _ in range(P["reps"]):
            r = run_task(cfg, task, rng)
            r["type"] = task["type"]
            recs.append(r)
    n = len(recs)
    tokens = [r["turns"] * P["c_per_turn"] for r in recs]
    rate = lambda k: sum(r["term"] == k for r in recs) / n * 100
    stalled_n = [r for r in recs if r["type"] == "normal" and r["term"] == "stalled"]
    n_normal = sum(1 for r in recs if r["type"] == "normal")
    return dict(
        true_success=rate("success"), claimed=100 * sum(r["claimed"] for r in recs) / n,
        premature=rate("premature"), stalled=rate("stalled"), exhausted=rate("exhausted"),
        stalled_normal=100 * len(stalled_n) / n_normal,
        tokens_mean=float(np.mean(tokens)), tokens_p95=float(np.percentile(tokens, 95)),
        max_turns=int(max(r["turns"] for r in recs)),
        productivity_claimed=100 * sum(r["claimed"] for r in recs) / n / (np.mean(tokens) / 1000),
    )

def analyze_honest(st, cfg):
    """诚实分析 agent：读 trace 统计 → 批量补丁（附人读理由）。"""
    patches = []
    if st["premature"] > 15 and cfg["stop"] != "machine":
        patches.append(dict(key="stop", val="machine",
                            reason=f"早停率 {st['premature']:.0f}%>15%：自评虚报在循环里复利，升验证阶梯"))
    if st["max_turns"] > 50 and cfg.get("K_stall") is None:
        patches.append(dict(key="K_stall", val=P["K_default"],
                            reason=f"最长 {st['max_turns']} 轮无止损：卡死任务在等漏检出口（1/p_leak={1/P['p_leak']:.0f} 轮），装熔断"))
    if st["tokens_p95"] > 120_000 and cfg.get("cap") is None:
        patches.append(dict(key="cap", val=P["cap_default"],
                            reason=f"p95 成本 {st['tokens_p95']/1000:.0f}k>120k：尾部失控，装 hard cap"))
    # R4 熔断过敏检测：熔断率高的主因应是卡死任务（hard），正常任务被误杀说明 K 太紧
    if st["stalled"] > 35 and st["stalled_normal"] > 8 and cfg.get("K_stall", 0) < 14:
        patches.append(dict(key="K_stall", val=14,
                            reason=f"熔断过敏：总熔断 {st['stalled']:.0f}% 里正常任务被误杀 {st['stalled_normal']:.0f}%>8%，K→14 放宽"))
    return patches

def analyze_hacked(st, cfg):
    """污染分析 agent：reward=claimed/tokens（自称产出率）。"""
    patches = []
    if cfg["stop"] == "machine":
        patches.append(dict(key="stop", val="self",
                            reason=f"验证调用不产生 claimed 增益，纯 token 成本（当前产出率 {st['productivity_claimed']:.3f}%/k tok）"))
    return patches

def apply(cfg, patches):
    return {**cfg, **{p["key"]: p["val"] for p in patches}}

def main():
    # ---------- Phase A：诚实外环 ----------
    cfg = dict(stop="self", K_stall=None, cap=None)   # Gen0 裸奔
    hist_A, patch_log_A = [], []
    gen = 0
    while True:
        st = evaluate(cfg, gen)
        hist_A.append(dict(gen=f"A{gen}", config=dict(cfg), **st))
        patches = analyze_honest(st, cfg)
        if not patches or gen >= P["max_gens"]:
            hist_A[-1]["converged"] = not patches
            break
        patch_log_A.append(dict(gen=f"A{gen}→A{gen+1}", patches=patches))
        cfg = apply(cfg, patches)
        gen += 1

    # ---------- Phase B：污染外环（从 A 收敛点接管，模拟"降本增效"） ----------
    hist_B, patch_log_B = [], []
    gen = 0
    while True:
        st = evaluate(cfg, 100 + gen)
        hist_B.append(dict(gen=f"B{gen}", config=dict(cfg), **st))
        patches = analyze_hacked(st, cfg)
        if not patches or gen >= 2:
            break
        patch_log_B.append(dict(gen=f"B{gen}→B{gen+1}", patches=patches))
        cfg = apply(cfg, patches)
        gen += 1

    out = dict(params=P, phase_A=dict(history=hist_A, patch_log=patch_log_A),
               phase_B=dict(history=hist_B, patch_log=patch_log_B))
    with open(os.path.join(HERE, "04_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)

    # ---------- 画图 ----------
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))

    # 左：Phase A 各代 真成功/早停 bars + 成本线
    xs = np.arange(len(hist_A))
    axes[0].bar(xs - 0.18, [h["true_success"] for h in hist_A], 0.36, label="真成功率 %", color="#2e7d32")
    axes[0].bar(xs + 0.18, [h["premature"] for h in hist_A], 0.36, label="早停率 %", color="#c62828")
    ax2 = axes[0].twinx()
    ax2.plot(xs, [h["tokens_mean"] / 1000 for h in hist_A], "o--", color="#1565c0", label="均 token (k)")
    ax2.set_ylabel("均 token (k)", color="#1565c0")
    for i, h in enumerate(hist_A):
        cfg_txt = f"{h['config']['stop'][:4]}|K{h['config']['K_stall'] or '-'}|cap{h['config']['cap'] or '-'}"
        axes[0].text(i, -14, cfg_txt, ha="center", fontsize=8.5, family="DejaVu Sans")
    axes[0].set_xticks(xs); axes[0].set_xticklabels([h["gen"] for h in hist_A])
    axes[0].set_ylabel("率 %"); axes[0].set_ylim(-20, 105)
    axes[0].set_title("Phase A 诚实外环：trace→补丁→重跑（reward=真成功率）\nGen0 裸奔 → 自动补全守卫 → 收敛")
    axes[0].legend(loc="upper left", fontsize=9)

    # 右：剪刀差（A 收敛点 vs B 各代）
    pts = [hist_A[-1]] + hist_B
    xs2 = np.arange(len(pts))
    axes[1].plot(xs2, [p["productivity_claimed"] * 10 for p in pts], "o-", color="#1565c0",
                 label="污染 reward：自称产出率 ×10")
    axes[1].plot(xs2, [p["true_success"] for p in pts], "o-", color="#2e7d32", label="真成功率 %")
    axes[1].plot(xs2, [p["premature"] for p in pts], "o--", color="#c62828", label="早停率 %")
    for i, p in enumerate(pts):
        axes[1].annotate(f"{p['gen']}\n{p['config']['stop'][:4]}", (i, p["true_success"]),
                         textcoords="offset points", xytext=(0, -30), ha="center", fontsize=9)
    a_last, b_last = pts[0], pts[-1]
    dp = (b_last["productivity_claimed"] / a_last["productivity_claimed"] - 1) * 100
    axes[1].set_title(f"Phase B 污染外环接管（reward=claimed/tokens）\nGoodhart 剪刀差：产出指标 +{dp:.0f}%，"
                      f"真成功率 {a_last['true_success']:.0f}%→{b_last['true_success']:.0f}%，早停 {a_last['premature']:.0f}%→{b_last['premature']:.0f}%")
    axes[1].set_xticks(xs2); axes[1].set_xticklabels([p["gen"] for p in pts])
    axes[1].set_ylabel("指标"); axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "04_outer_loop.png"), dpi=130)
    print("saved:", os.path.join(HERE, "04_outer_loop.png"))

    # ---------- 终端报告 ----------
    def row(h):
        return (f"{h['gen']:4s} {h['config']['stop'][:7]:7s} K={str(h['config']['K_stall'] or '-'):4s} cap={str(h['config']['cap'] or '-'):4s} | "
                f"真成功 {h['true_success']:5.1f}% | 早停 {h['premature']:5.1f}% | 熔断 {h['stalled']:5.1f}% | "
                f"烧穿 {h['exhausted']:4.1f}% | 均 {h['tokens_mean']/1000:6.1f}k | p95 {h['tokens_p95']/1000:7.1f}k")
    print("\n===== Phase A 诚实外环（每代 = 12任务×%d 次） =====" % P["reps"])
    for h in hist_A:
        print("  " + row(h))
    for pl in patch_log_A:
        for p in pl["patches"]:
            print(f"    [{pl['gen']}] 补丁 {p['key']}→{p['val']}：{p['reason']}")
    print("\n===== Phase B 污染外环（reward=claimed/tokens） =====")
    for h in hist_B:
        print("  " + row(h) + f" | 产出率 {h['productivity_claimed']:.3f}%/k")
    for pl in patch_log_B:
        for p in pl["patches"]:
            print(f"    [{pl['gen']}] 补丁 {p['key']}→{p['val']}：{p['reason']}")

if __name__ == "__main__":
    main()
