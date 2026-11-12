#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E3 —— Context Rot mini：长度单独不杀人，"同形干扰项 × 长度"才杀人
====================================================================
背景：E2 实测词面 needle 在 0.5B/3.2K 与 glm/6.4K 全满——复证 Chroma 批评
     （NIAH 高估长上下文能力）。本实验换更接近真实 agent 轨迹的杀伤条件：
     干扰项与 needle 同句式、同关键词域、不同值（KX-2076→王倩 vs KX-2077→林澈），
     要求模型做精确绑定而非模糊检索。
设计：needle 固定在 50% 位置；8 条干扰句均匀撒在 ±10% 之外；
     条件 {clean, distractor} × 长度 {1K, 4K, 8K} × 4 needle × {qwen, glm}
预期：clean 全程高企；distractor 随长度崩塌（绑定混淆）；glm 抗性 > qwen（规模效应）
用法（按长度分块防超时；qwen 8K 单call≈230s）：
  python3 e3_rot.py --model qwen --lengths 1000
  python3 e3_rot.py --model qwen --lengths 4000
  python3 e3_rot.py --model qwen --lengths 8000
  python3 e3_rot.py --model glm --lengths 1000,4000,8000
  python3 e3_rot.py --plot
产出：results/e3_rot.json + e3_rot.png
对应章节：Ch03（Context Rot）
"""
import os, sys, json, time, argparse, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import local_qwen, glm, _get_qwen, RES_DIR

random.seed(2600)

# ---------- 真 needle（与 E2 同款，已校准：clean 3.2K 全对） ----------
NEEDLES = [
    ("密钥编号 KX-2077 由值班工程师林澈保管。", "密钥 KX-2077 由谁保管？只答姓名。", "林澈"),
    ("备份服务器的重启口令是 蓝鲸-4417。", "备份服务器的重启口令是什么？只答口令本身。", "4417"),
    ("三期迁移的截止日期定在 9 月 14 日。", "三期迁移的截止日期是几月几日？只答日期。", "14"),
    ("接口限流阈值被临时上调到 4800。", "接口限流阈值临时上调到了多少？只答数字。", "4800"),
]

# ---------- 同形干扰（同句式/同域/不同值；每 needle 2 条） ----------
DISTRACTORS = [
    "密钥编号 KX-2076 由巡检员王倩保管。",
    "密钥编号 KX-2078 由外包司机陈默保管。",
    "测试服务器的重启口令是 蓝鲸-4419。",
    "备份路由器的管理口令是 白鲨-4417。",
    "二期联调的截止日期定在 9 月 18 日。",
    "三期回滚的启动日期定在 10 月 14 日。",
    "网关限流阈值被临时上调到 4600。",
    "接口超时阈值被临时上调到 5800。",
]

FILLER_UNIT = ("上下文工程要求工程师对进入窗口的每一段信息负责：系统指令、工具定义、检索片段、"
               "对话历史与中间结果，都要在有限预算内争取位置与形式。")

NEEDLE_FRAC = 0.50          # needle 固定在中段（E2 证明 clean 下位置无差异）
EXCLUDE_BAND = 0.10         # 干扰项不得落在 needle ±10% 内

def build_context(target_tok, condition):
    tok, _ = _get_qwen()
    unit = len(tok(FILLER_UNIT, add_special_tokens=False).input_ids)
    n_units = max(target_tok // unit, 6)
    cut = int(n_units * NEEDLE_FRAC)
    # 干扰槽位：等间距 8 个，避开 needle 邻域
    if condition == "distractor":
        cand = [int(n_units * f) for f in (0.06, 0.17, 0.28, 0.39, 0.61, 0.72, 0.83, 0.94)]
        dslots = {min(max(c, 1), n_units - 1): d for c, d in zip(cand, DISTRACTORS)}
    else:
        dslots = {}
    parts = []
    for i in range(n_units + 1):
        if i == cut:
            parts.append("__NEEDLE__")
        if i in dslots:
            parts.append(dslots[i])
        if i < n_units:
            parts.append(FILLER_UNIT)
    # 只放第一条 needle？不——每格实验独立调用时替换 __NEEDLE__ 为当前 needle
    return "".join(parts)

def norm(s):
    return s.replace(" ", "").replace("：", ":").replace(",", "").replace("，", "")

def ask(model, prompt):
    if model == "qwen":
        return local_qwen(prompt, max_new_tokens=12)
    return glm("glm-4-flash", prompt, max_tokens=16, temperature=0.0)["content"]

def run_grid(model, lengths, conds=("clean", "distractor")):
    p = os.path.join(RES_DIR, "e3_rot.json")
    out = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    for L in lengths:
        for cond in conds:
            key = f"{model}|{L}|{cond}"
            if key in out.get("cells", {}):
                print(f"[skip] {key}"); continue
            template = build_context(L, cond)
            tok, _ = _get_qwen()
            actual = len(tok(template.replace("__NEEDLE__", NEEDLES[0][0]),
                             add_special_tokens=False).input_ids)
            correct = 0; details = []
            t0 = time.time()
            for sent, q, ans in NEEDLES:
                ctx = template.replace("__NEEDLE__", sent)
                reply = ask(model, ctx + "\n\n" + q)
                ok = norm(ans) in norm(reply)
                correct += ok
                details.append({"q": q[:18], "ok": bool(ok), "reply": reply[:30],
                                "bound_confusion": (not ok) and any(
                                    w in norm(reply) for w in ("王倩", "陈默", "4419", "4417", "18", "4600", "5800"))})
            out.setdefault("cells", {})[key] = {
                "acc": correct / len(NEEDLES), "n": len(NEEDLES), "actual_tok": actual,
                "confused": sum(1 for d in details if d["bound_confusion"]),
                "details": details}
            print(f"[done] {key} acc={correct}/{len(NEEDLES)} confused={out['cells'][key]['confused']} ({time.time()-t0:.0f}s)")
            json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[saved-merged] {p}")

def plot():
    p = os.path.join(RES_DIR, "e3_rot.json")
    if not os.path.exists(p):
        print("无结果"); return
    cells = json.load(open(p, encoding="utf-8"))["cells"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    models = sorted({k.split("|")[0] for k in cells})
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4.8), squeeze=False)
    for mi, m in enumerate(models):
        ax = axes[0][mi]
        for cond, color in (("clean", "#55a868"), ("distractor", "#c44e52")):
            lens = sorted({int(k.split("|")[1]) for k in cells if k.startswith(m + "|") and k.endswith("|" + cond)})
            xs = [l // 1000 for l in lens]
            ys = [cells[f"{m}|{l}|{cond}"]["acc"] * 100 for l in lens]
            ax.plot(xs, ys, marker="o", color=color,
                    label=f"{cond}" + ("（同形干扰×8）" if cond == "distractor" else ""))
            for x, y in zip(xs, ys):
                ax.annotate(f"{y:.0f}", (x, y), textcoords="offset points", xytext=(0, 6),
                            fontsize=9, ha="center")
        ax.set_title(f"{m}"); ax.set_xlabel("上下文长度（K tok）")
        ax.set_ylabel("答对率 %"); ax.set_ylim(-5, 108); ax.grid(alpha=0.3); ax.legend(fontsize=9)
    fig.suptitle("E3 Context Rot mini：长度单独（clean）不伤词面检索；同形干扰 × 长度才崩塌（needle 固定 50%）", fontsize=12)
    fig.tight_layout()
    png = os.path.join(RES_DIR, "e3_rot.png")
    fig.savefig(png, dpi=150)
    print(f"[saved] {png}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["qwen", "glm"])
    ap.add_argument("--lengths", default="1000")
    ap.add_argument("--conds", default="clean,distractor")
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()
    if a.plot:
        plot()
    else:
        run_grid(a.model, [int(x) for x in a.lengths.split(",")],
                 tuple(a.conds.split(",")))
