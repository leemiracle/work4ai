#!/usr/bin/env python3
"""E2 · 拓扑成本模拟：线性 loop vs 并行 fan-out vs DAG+join（规则模拟）

讲透Graph Ch02 的核心实验。LangGraph 的核心主张：
  "agent graphs 通常不是 DAG" + Send API 运行时动态扇出。
本实验把三种拓扑的 token 成本与轮次算清楚：

  A 线性 loop（6 步串行）：每步都背着全部历史 → 成本 O(N²)
  B 并行 fan-out + join（map-reduce）：worker 只拿 plan+自己那份 → O(N)
  C DAG + 验证门 + 重试环：B 的基础上加 verify 节点与期望重试

参数刻意贴近真实 agent 工作负载（数百 token 级），结论对参数不敏感。

输出：E2_result.json + E2_topology.png
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- 参数（贴真实负载；结论对参数不敏感） ----------
N = 6                # 子任务数
SYS = 500            # 每次调用的 system/计划开销（token）
OUT_STEP = 400       # 每步产出（token）
PAYLOAD = 300        # 并行 worker 的专属输入（token）
SUMMARY = 100        # worker 回传 join 的摘要（token）
VERIFY_PASS = 0.85   # 验证门通过率（C 拓扑）

# ---------- A 线性 loop：第 i 步上下文 = SYS + 累积的 (i-1) 步产出 ----------
a_inputs, a_total, seq = [], 0, []
for i in range(1, N + 1):
    ctx = SYS + (i - 1) * OUT_STEP + PAYLOAD
    a_inputs.append(ctx)
    seq.append({"step": i, "input_tokens": ctx, "output_tokens": OUT_STEP})
    a_total += ctx + OUT_STEP
a_rounds = N  # 串行轮次

# ---------- B 并行 fan-out + join ----------
b_worker_in = SYS + PAYLOAD                      # 每个 worker
b_workers_total = N * (b_worker_in + SUMMARY)
b_join_in = SYS + N * SUMMARY
b_total = b_workers_total + b_join_in + SUMMARY * 2   # join 也产出最终摘要
b_rounds = 2  # fan-out 一轮（并发）+ join 一轮

# ---------- C DAG + 验证门 + 重试环 ----------
# 每个 worker 后接 verify；不过则重试，期望次数 = 1/p
exp_tries = 1 / VERIFY_PASS
c_workers = N * exp_tries * (b_worker_in + SUMMARY + SYS // 2)  # verify 调用更短
c_join = b_join_in + SUMMARY * 2
c_total = c_workers + c_join
c_rounds = 2 * exp_tries  # 期望轮次（每轮都过一遍 verify）

rows = {
    "A_线性loop": {"total_tokens": int(a_total), "rounds": a_rounds,
                    "growth": "O(N²)——历史越背越重"},
    "B_并行fanout_join": {"total_tokens": int(b_total), "rounds": b_rounds,
                           "growth": "O(N)——worker 无历史包袱"},
    "C_DAG+验证门+重试": {"total_tokens": int(c_total), "rounds": round(c_rounds, 1),
                          "growth": f"B×期望重试(1/p={exp_tries:.2f})"},
}

print("=" * 76)
print("E2 · 拓扑成本模拟（N=%d 子任务）" % N)
print("=" * 76)
print("A 线性 loop 每步输入 token:", a_inputs)
print("-" * 76)
for name, r in rows.items():
    print(f"{name:<20} 总token={r['total_tokens']:>8,}   轮次={r['rounds']:<6} {r['growth']}")
print("-" * 76)
saving_b = 1 - b_total / a_total
print(f"B 相对 A 省 {saving_b:.0%} token，轮次 {a_rounds}→{b_rounds}（时延近似 ÷{a_rounds/b_rounds:.0f}）")
print(f"C 的验证门把成本抬回 B 的 {c_total/b_total:.1f} 倍——可靠性是买来的：")
print(f"  单分支通过率 {VERIFY_PASS} → 全体一次全过的概率 {VERIFY_PASS**N:.1%}，"
      f"期望重试 {exp_tries:.2f}×/分支")
print("  （呼应讲透Loop E4：无验证的『省』是假省——污染 reward 的 Goodhart 剪刀差）")

# ---------- 图 ----------
fig, axes = plt.subplots(1, 3, figsize=(14, 4.3))

ax = axes[0]
ax.bar(range(1, N + 1), a_inputs, color="#e76f51", label="线性: 每步输入")
ax.bar(range(1, N + 1), [SYS + PAYLOAD] * N, color="#2a9d8f",
       label="并行: worker 输入(恒定)", width=0.55)
ax.set_xlabel("第 i 个子任务")
ax.set_ylabel("输入 token")
ax.set_title(f"上下文增长：O(N²) vs O(N)\n(6步线性总输入 {sum(a_inputs):,} vs 并行 {N*(SYS+PAYLOAD):,})")
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.3)

ax = axes[1]
names = list(rows)
tot = [rows[k]["total_tokens"] for k in names]
rnd = [rows[k]["rounds"] for k in names]
xs = range(len(names))
ax.bar([x - 0.2 for x in xs], [t / 1000 for t in tot], width=0.4, label="总 token (千)", color="#264653")
ax.bar([x + 0.2 for x in xs], [r * 1000 for r in rnd], width=0.4, label="轮次 ×1000", color="#e9c46a")
ax.set_xticks(xs)
ax.set_xticklabels(["A 线性", "B 并行", "C +验证"], fontsize=9)
ax.legend(fontsize=8)
ax.set_title("三种拓扑的成本/时延")
ax.grid(axis="y", alpha=0.3)

ax = axes[2]
ks = list(range(1, 13))
for p, c in ((0.95, "#2a9d8f"), (0.85, "#e9c46a"), (0.7, "#e76f51")):
    ax.plot(ks, [p ** k for k in ks], marker="o", ms=3, color=c, label=f"全体一次过 p={p}")
ax.set_xlabel("并行分支数 k")
ax.set_ylabel("P(所有分支一次通过)")
ax.set_title("fan-out 的隐税：分支越多\n越需要验证门/重试环（环!）")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

fig.suptitle("E2 · 拓扑即成本：线性 loop 的 O(N²) 历史税 与 fan-out 的可靠性税", fontsize=12)
fig.tight_layout()
png = os.path.join(HERE, "E2_topology.png")
fig.savefig(png, dpi=130)

result = {
    "experiment": "E2 topology cost simulation",
    "type": "成本模型模拟（非 LLM 实验；参数见文件头）",
    "params": {"N": N, "SYS": SYS, "OUT_STEP": OUT_STEP, "PAYLOAD": PAYLOAD,
               "SUMMARY": SUMMARY, "VERIFY_PASS": VERIFY_PASS},
    "A_linear": {"per_step_inputs": a_inputs, "total_tokens": int(a_total), "rounds": a_rounds, "steps": seq},
    "B_fanout_join": {"worker_input": b_worker_in, "total_tokens": int(b_total), "rounds": b_rounds},
    "C_dag_verify": {"expected_tries_per_branch": round(exp_tries, 3), "total_tokens": int(c_total),
                     "rounds": round(c_rounds, 1), "all_pass_once": round(VERIFY_PASS ** N, 4)},
    "comparison": rows,
    "saving_B_vs_A": f"{1 - b_total / a_total:.0%}",
    "png": os.path.basename(png),
}
with open(os.path.join(HERE, "E2_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\n落盘: E2_result.json + E2_topology.png")
