#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透Loop E3：四种循环形状模拟（Heartbeat / Cron / Hook / Goal）

形状学（vibeengines handbook 2026-07，2607.00038 的 trigger 分类）：
  Heartbeat  短间隔连续轮询（秒-分钟），监控/值守。风险：重叠事故（上一 tick 未完，下一 tick 又开）
  Cron       定时批量（每日/每周），报告/审计。风险：空转成本（没活也烧）
  Hook       事件触发（PR push/CI 失败/消息到达），响应式。风险：事件风暴时成本线性爆炸
  Goal       反复迭代直到机器可查条件为真，迁移/重构。风险：无上限+低进展=烧钱黑洞

模拟 24 小时窗口：
  - 工作到达：泊松过程 λ(t)=base*(1+峰值因子)（白天多夜里少）
  - Heartbeat: 每 tick 检查队列，有活则干（消耗调用）；重叠版 vs 加锁版
  - Cron: 每 24h 一次批量
  - Hook: 每事件一次调用
  - Goal: 每个任务迭代直到完成/上限；无上限版 vs cap 版

输出：experiments/03_results.json + 03_loop_shapes.png
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
    hours=24,
    lambda_base=2.0,      # 基础事件到达率（件/小时）
    peak=2.0,             # 白天峰值因子（t=10h 最大）
    c_check=500,          # 一次"检查/心跳"调用 token
    c_work=3000,          # 一次"干活"调用 token
    heartbeat_min=10,     # heartbeat 周期（分钟）
    p_collision=0.06,     # 上一 tick 未完成的概率（重叠事故率，与负载相关）
    collision_cost=15000, # 一次重叠事故的代价（冲突修复 token）
    goal_iter_tokens=2000,# goal 每轮迭代 token
    goal_p_progress=0.3,  # goal 每轮推进概率
    goal_cap=None,        # goal 无上限（演示）
    goal_cap_bounded=25,  # goal 有 cap 版
    N_sims=2000,          # 蒙特卡洛天数
    seed=42,
)

def arrivals_24h(rng):
    """泊松到达：非均匀率 λ(t)=base*(1+peak*cos 峰值在 t=10)"""
    ts = []
    t = 0.0
    while True:
        lam = P["lambda_base"] * (1 + P["peak"] * np.exp(-((t - 10) ** 2) / 18))
        t += rng.expovariate(lam)
        if t >= P["hours"]:
            return ts
        ts.append(t)

def simulate_day(rng):
    arr = arrivals_24h(rng)
    n_jobs = len(arr)
    res = {"n_jobs": n_jobs}

    # --- Heartbeat：每 10 分钟醒一次，队列有活就干 ---
    ticks = int(P["hours"] * 60 / P["heartbeat_min"])
    # 排队模型：每 tick 处理 1 件（简化）
    queue_hb, done_hb, collisions = 0, 0, 0
    arr_set = list(arr)
    pending = []
    for i in range(ticks):
        t_now = (i + 1) * P["heartbeat_min"] / 60
        pending += [a for a in arr_set if a <= t_now]
        arr_set = [a for a in arr_set if a > t_now]
        busy = False
        if pending:
            pending.pop(0)
            busy = True
            done_hb += 1
        # 重叠事故：busy 时上一 tick 任务仍占着（简化概率模型）
        if busy and rng.random() < P["p_collision"]:
            collisions += 1
        res["hb_locked"] = dict(
            tokens=ticks * P["c_check"] + done_hb * P["c_work"] + collisions * P["collision_cost"],
            done=done_hb, collisions=collisions, note="有锁：串行无重叠")
        # 无锁版：重叠事故率翻 3 倍（两 agent 同改一状态）
    res["hb_locked"]["collisions"] = collisions
    # 无锁版单独算
    q2, done2, col2 = 0, 0, 0
    arr_set2 = list(arr)
    pending2 = []
    for i in range(ticks):
        t_now = (i + 1) * P["heartbeat_min"] / 60
        pending2 += [a for a in arr_set2 if a <= t_now]
        arr_set2 = [a for a in arr_set2 if a > t_now]
        if pending2:
            pending2.pop(0)
            done2 += 1
            if rng.random() < P["p_collision"] * 3:
                col2 += 1
    res["hb_nolock"] = dict(tokens=ticks * P["c_check"] + done2 * P["c_work"] + col2 * P["collision_cost"],
                            done=done2, collisions=col2, note="无锁：重叠事故率×3")

    # --- Cron：每天一次批量（全部活一次处理） ---
    res["cron"] = dict(tokens=P["c_check"] + n_jobs * P["c_work"],
                       done=n_jobs, note="日批：延迟最高但成本最低（无逐 tick 检查）")

    # --- Hook：每事件一次 ---
    res["hook"] = dict(tokens=n_jobs * (P["c_check"] + P["c_work"]),
                       done=n_jobs, note="事件驱动：延迟≈0，成本随事件率线性")

    # --- Goal：每任务迭代到完成 ---
    def goal_run(cap):
        rng_g = rng
        W, t = 3, 0  # 每件任务 3 单位工作（简化）
        while W > 0:
            t += 1
            if cap is not None and t >= cap:
                return t * P["goal_iter_tokens"], False
            if rng_g.random() < P["goal_p_progress"]:
                W -= 1
        return t * P["goal_iter_tokens"], True

    tok_u, done_u = 0, 0
    tok_b, done_b = 0, 0
    for _ in range(n_jobs):
        tk, ok = goal_run(P["goal_cap"]); tok_u += tk; done_u += ok
        tk, ok = goal_run(P["goal_cap_bounded"]); tok_b += tk; done_b += ok
    res["goal_nocap"] = dict(tokens=tok_u, done=done_u, total=n_jobs,
                             note="无上限：每件必做完（进度100%）但成本无界")
    res["goal_cap25"] = dict(tokens=tok_b, done=done_b, total=n_jobs,
                             note="cap=25：有界，放弃超难任务")
    return res

def main():
    rng = random.Random(P["seed"])
    keys = ["hb_locked", "hb_nolock", "cron", "hook", "goal_nocap", "goal_cap25"]
    acc = {k: {"tokens": [], "done": []} for k in keys}
    collisions_nolock = []
    for _ in range(P["N_sims"]):
        r = simulate_day(rng)
        for k in keys:
            acc[k]["tokens"].append(r[k]["tokens"])
            acc[k]["done"].append(r[k]["done"])
        collisions_nolock.append(r["hb_nolock"]["collisions"])

    summary = {}
    for k in keys:
        summary[k] = dict(
            tokens_mean=float(np.mean(acc[k]["tokens"])),
            tokens_p95=float(np.percentile(acc[k]["tokens"], 95)),
            done_mean=float(np.mean(acc[k]["done"])),
        )
    summary["collisions_per_day_nolock_mean"] = float(np.mean(collisions_nolock))

    out = {"params": P, "summary": summary}
    with open(os.path.join(HERE, "03_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # 画图：双联
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    names = ["Heartbeat\n(有锁)", "Heartbeat\n(无锁)", "Cron\n日批", "Hook\n事件驱动", "Goal\n无上限", "Goal\ncap=25"]
    vals = [summary[k]["tokens_mean"] for k in keys]
    p95s = [summary[k]["tokens_p95"] for k in keys]
    x = np.arange(len(keys))
    axes[0].bar(x - 0.18, [v/1000 for v in vals], 0.36, label="日均 token (k)", color="#1976d2")
    axes[0].bar(x + 0.18, [v/1000 for v in p95s], 0.36, label="p95 token (k)", color="#90caf9")
    axes[0].set_xticks(x); axes[0].set_xticklabels(names, fontsize=9)
    axes[0].set_ylabel("token (k)")
    axes[0].set_title(f"E3a 四形状 24h 成本（{P['N_sims']} 天蒙特卡洛）\nHeartbeat 空转检查费 × 无锁事故费；Goal 无上限 p95 起飞")
    axes[0].legend(); axes[0].grid(axis="y", alpha=0.3)

    # 完成度对比（Goal 两版）
    g_u = summary["goal_nocap"]; g_b = summary["goal_cap25"]
    axes[1].bar([0, 1], [g_u["done_mean"], g_b["done_mean"]], color=["#c62828", "#2e7d32"], width=0.5)
    axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(["Goal 无上限", "Goal cap=25"])
    axes[1].set_ylabel("日均完成任务数")
    axes[1].set_title(f"E3b cap 的代价与收益\n无上限日均完成 {g_u['done_mean']:.1f} 件；cap=25 完成 {g_b['done_mean']:.1f} 件但成本有界\n（p_progress={P['goal_p_progress']}，W=3/任务，P(超25轮)≈{100*(1-P['goal_p_progress'])**25:.1f}%）")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "03_loop_shapes.png"), dpi=130)
    print("saved:", os.path.join(HERE, "03_loop_shapes.png"))

    print("\n===== E3 四形状 24h 摘要 =====")
    for k, n in zip(keys, names):
        s = summary[k]
        print(f"  {n.replace(chr(10),'(')+')':16s} 日均 {s['tokens_mean']/1000:7.1f}k | p95 {s['tokens_p95']/1000:7.1f}k | 完成 {s['done_mean']:5.1f}")
    print(f"  无锁 heartbeat 日均重叠事故：{summary['collisions_per_day_nolock_mean']:.2f} 次（每次 {P['collision_cost']} tok 修复代价）")

if __name__ == "__main__":
    main()
