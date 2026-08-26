#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2 —— 位置效应：放进去 ≠ 用得上
=================================
问题：同一句关键事实放在上下文的首/中/尾，模型还能答对吗？窗口越长越差吗？
设计：4 个 needle 事实句，插入 filler 段落的 5%/50%/92% 处，问题固定在末尾。
     Qwen（CPU，计时实测 1K≈28s/4K≈91s → 网格瘦身 {600,3200}）
     glm-4-flash（API 快，{600,1600,3200,6400}）
预期：U 型曲线（首因+近因效应），长上下文中段塌陷。
用法（分块防超时）：
  python3 e2_position.py --model qwen --lengths 600
  python3 e2_position.py --model qwen --lengths 3200
  python3 e2_position.py --model glm  --lengths 600,1600,3200,6400
产出：results/e2_position.json（增量合并）+ e2_position.png（全量后画）
对应章节：Ch02（位置效应）
"""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import local_qwen, glm, _get_qwen, save, load, RES_DIR

# ---------- needle 与评分 ----------
NEEDLES = [
    ("密钥编号 KX-2077 由值班工程师林澈保管。", "密钥 KX-2077 由谁保管？只答姓名。", "林澈"),
    ("备份服务器的重启口令是 蓝鲸-4417。", "备份服务器的重启口令是什么？只答口令本身。", "4417"),
    ("三期迁移的截止日期定在 9 月 14 日。", "三期迁移的截止日期是几月几日？只答日期。", "14"),
    ("接口限流阈值被临时上调到 4800。", "接口限流阈值临时上调到了多少？只答数字。", "4800"),
]

FILLER_UNIT = ("上下文工程要求工程师对进入窗口的每一段信息负责：系统指令、工具定义、检索片段、"
               "对话历史与中间结果，都要在有限预算内争取位置与形式。")
POSITIONS = {"首(5%)": 0.05, "中(50%)": 0.50, "尾(92%)": 0.92}

def build_context(target_tok, pos_frac, needle):
    tok, _ = _get_qwen()
    unit = len(tok(FILLER_UNIT, add_special_tokens=False).input_ids)
    n_units = max(target_tok // unit, 4)
    blocks = [FILLER_UNIT] * n_units
    # 在 pos_frac 处切开插入 needle（按单元粒度）
    cut = max(1, int(n_units * pos_frac))
    parts = blocks[:cut] + [needle] + blocks[cut:]
    ctx = "".join(parts)
    return ctx, len(tok(ctx, add_special_tokens=False).input_ids)

def norm(s):
    return s.replace(" ", "").replace("：", ":").replace(",", "").replace("，", "")

def ask(model, ctx, question):
    prompt = ctx + "\n\n" + question
    if model == "qwen":
        return local_qwen(prompt, max_new_tokens=12), 0
    r = glm("glm-4-flash", prompt, max_tokens=16, temperature=0.0)
    return r["content"], r["latency_ms"]

def run_grid(model, lengths):
    out = {}
    p = os.path.join(RES_DIR, "e2_position.json")
    if os.path.exists(p):
        try:
            out = json.load(open(p, encoding="utf-8"))
        except Exception:
            out = {}
    for L in lengths:
        for pname, frac in POSITIONS.items():
            key = f"{model}|{L}|{pname}"
            if key in out.get("cells", {}):
                print(f"[skip] {key}")
                continue
            correct = 0; details = []
            t_cell = time.time()
            for sent, q, ans in NEEDLES:
                ctx, actual = build_context(L, frac, sent)
                reply, _ = ask(model, ctx, q)
                ok = norm(ans) in norm(reply)
                correct += ok
                details.append({"q": q[:18], "ok": bool(ok), "reply": reply[:30]})
            out.setdefault("cells", {})[key] = {
                "acc": correct / len(NEEDLES), "n": len(NEEDLES),
                "actual_tok": actual, "details": details}
            print(f"[done] {key} acc={correct}/{len(NEEDLES)} ({time.time()-t_cell:.0f}s)")
            json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[saved-merged] {p}")

def plot():
    p = os.path.join(RES_DIR, "e2_position.json")
    if not os.path.exists(p):
        print("无结果可画"); return
    out = json.load(open(p, encoding="utf-8"))
    cells = out["cells"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    models = sorted({k.split("|")[0] for k in cells})
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4.8), squeeze=False)
    for mi, m in enumerate(models):
        ax = axes[0][mi]
        lens = sorted({int(k.split("|")[1]) for k in cells if k.startswith(m + "|")})
        for L in lens:
            xs, ys = [], []
            for pname in POSITIONS:
                k = f"{m}|{L}|{pname}"
                if k in cells:
                    xs.append(pname); ys.append(cells[k]["acc"] * 100)
            ax.plot(xs, ys, marker="o", label=f"≈{L} tok")
        ax.set_title(f"{m}")
        ax.set_ylabel("needle 答对率 %")
        ax.set_ylim(-5, 105)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
    fig.suptitle("E2 位置效应：关键事实放首/中/尾 × 上下文长度（问题固定在末尾）", fontsize=13)
    fig.tight_layout()
    png = os.path.join(RES_DIR, "e2_position.png")
    fig.savefig(png, dpi=150)
    print(f"[saved] {png}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["qwen", "glm"])
    ap.add_argument("--lengths", default="600")
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()
    if a.plot:
        plot()
    else:
        run_grid(a.model, [int(x) for x in a.lengths.split(",")])
