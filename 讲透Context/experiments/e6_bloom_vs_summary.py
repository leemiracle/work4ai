#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E6 —— Compaction 的数学：Bloom filter vs LLM 摘要，同等 token 预算下的正面对决
================================================================================
灵感：Context Compaction Theory (arXiv 2608.01326, 2026-08)
  - compaction 两策略：Selection（选子集保留）vs Generation（任意有界摘要）
  - Thm 1: Generation ≡ 单向通信复杂度（预算下界可直接移植）
  - 附录 A：生产 compaction endpoint 在 set membership 上错误率接近随机猜，
    同尺寸 Bloom filter 近乎最优 → 通用摘要输给专用数据结构

本实验做玩具级公平复现（N=120 项，给 LLM 比论文 15000 项友好得多的场）：
  集合 S：120 个随机 6-hex ID
  三种 compaction（预算对齐到同一 token 量级 B）：
    A) Selection : 只保留前 40 个 ID 原文（≈ 1/3）
    B) LLM 摘要  : glm-4-flash / 本地 Qwen 把 120 个 ID 压进 B token
    C) Bloom     : m 位、k 哈希，序列化 hex，m 调到 token≈B
  查询：48 个 membership（24 正例 + 24 反例），YES/NO
  指标：Accuracy / FPR / FNR；Bloom 另给理论 FPR=(1-e^{-kn/m})^k 对照
产出：results/e6_bloom_vs_summary.json + e6_bloom_vs_summary.png
对应章节：Ch06（Compaction 的数学：通信复杂度下场）
"""
import os, sys, json, random, hashlib, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import _get_qwen, glm, save, RES_DIR

random.seed(20260826)

# ---------- 1. 造集合与查询 ----------
def rand_id():
    return "%06x" % random.getrandbits(24)  # 6 位 hex

S = sorted({rand_id() for _ in range(200)})[:120]           # 集合：120 个 ID
POS = random.sample(S, 24)                                   # 正例查询（在 S 内）
NEG = []
while len(NEG) < 24:                                         # 反例查询（不在 S 内）
    x = rand_id()
    if x not in S:
        NEG.append(x)
QUERIES = [(q, True) for q in POS] + [(q, False) for q in NEG]
random.shuffle(QUERIES)

# ---------- 2. token 计数 ----------
tok, _ = _get_qwen()
def ntok(s): return len(tok(s, add_special_tokens=False).input_ids)

# ---------- 3. Bloom filter ----------
class Bloom:
    def __init__(self, m, k):
        self.m, self.k, self.bits = m, k, [0] * m
    def _idx(self, item, i):
        h = hashlib.blake2b(f"{i}:{item}".encode(), digest_size=8).digest()
        return int.from_bytes(h, "big") % self.m
    def add(self, item):
        for i in range(self.k):
            self.bits[self._idx(item, i)] = 1
    def __contains__(self, item):
        return all(self.bits[self._idx(item, i)] for i in range(self.k))
    def hexout(self):
        packed = 0
        for b in self.bits:
            packed = (packed << 1) | b
        return "%x" % packed

def bloom_theoretical_fpr(m, k, n):
    return (1 - math.exp(-k * n / m)) ** k

# 预算锚点：Selection 保留 40 个 ID 的 token 数
sel_ids = S[:40]
sel_text = "原清单（部分保留）：\n" + "\n".join(sel_ids)
B = ntok(sel_text)                    # 预算锚（约 90-110 tok）
print(f"[预算] Selection 保留 40/120 项 = {B} tokens")

# Bloom：调 m 使序列化 token ≈ B（hex 字符 ≈ 2.5 char/tok，先估后微调）
def bloom_with_budget(target_tok, k=3):
    m = 1024
    while True:
        bf = Bloom(m, k)
        for x in S:
            bf.add(x)
        t = ntok("过滤器(hex)：" + bf.hexout())
        if t >= target_tok * 0.9 or m > 65536:
            return bf, m, t
        m *= 2
BF, M, BT = bloom_with_budget(B)
print(f"[Bloom] m={M} bits, k=3, 序列化={BT} tokens, 理论FPR={bloom_theoretical_fpr(M,3,len(S))*100:.2f}%")

# ---------- 4. LLM 摘要（Generation 策略） ----------
full_list = "原始清单（120 项）：\n" + "\n".join(S)
LIST_TOK = ntok(full_list)
print(f"[原文] 完整清单 {LIST_TOK} tokens（预算 {B}，压缩比 {LIST_TOK/max(BT,1):.1f}×）")

COMPRESS_PROMPT = (
    "以下是一个 ID 清单（共 120 个）。你要把它压缩成不超过 {} tokens 的形式（这是硬约束，"
    "之后只能凭压缩结果回答 ID membership 查询）。你可以用任何编码/分组/压缩技巧，"
    "目标：之后判断『某 ID 是否在清单里』尽量准。只输出压缩结果本身。\n\n{}"
).format(B, full_list)

def make_summary(model_name):
    if model_name == "glm-4-flash":
        r = glm("glm-4-flash", COMPRESS_PROMPT, max_tokens=int(B * 1.6), temperature=0.1)
        return r["content"]
    else:  # 本地 Qwen（thread=1 已在 common 内）
        return local_summary_qwen()

def local_summary_qwen():
    from common import local_qwen
    return local_qwen(COMPRESS_PROMPT, max_new_tokens=int(B * 1.6), temperature=0.2, seed=7)

def ask_membership(model_name, context, qid):
    q = f"{context}\n\n---\n问题：ID {qid} 在原始清单里吗？只答 YES 或 NO。"
    if model_name == "glm-4-flash":
        r = glm("glm-4-flash", q, max_tokens=4, temperature=0.0)
        return "YES" in r["content"].upper()
    else:
        from common import local_qwen
        out = local_qwen(q, max_new_tokens=4)
        return "YES" in out.upper()

# ---------- 5. 评测 ----------
def eval_selection():
    ctx = sel_text
    tp = fp = tn = fn = 0
    for qid, truth in QUERIES:
        pred = qid in sel_ids          # 只能看见保留的 40 个
        tp += pred and truth; fn += (not pred) and truth
        fp += pred and (not truth); tn += (not pred) and (not truth)
    return dict(tp=tp, fp=fp, tn=tn, fn=fn, ctx_tok=B)

def eval_bloom():
    tp = fp = tn = fn = 0
    for qid, truth in QUERIES:
        pred = qid in BF
        tp += pred and truth; fn += (not pred) and truth
        fp += pred and (not truth); tn += (not pred) and (not truth)
    return dict(tp=tp, fp=fp, tn=tn, fn=fn, ctx_tok=BT)

def eval_llm(model_name, summary):
    st = ntok(summary)
    tp = fp = tn = fn = 0
    details = []
    for qid, truth in QUERIES:
        pred = ask_membership(model_name, summary, qid)
        tp += pred and truth; fn += (not pred) and truth
        fp += pred and (not truth); tn += (not pred) and (not truth)
        details.append({"q": qid, "truth": truth, "pred": bool(pred)})
    return dict(tp=tp, fp=fp, tn=tn, fn=fn, ctx_tok=st,
                summary_head=summary[:300], details=details)

def metrics(d):
    acc = (d["tp"] + d["tn"]) / sum(d[k] for k in ("tp", "fp", "tn", "fn"))
    fpr = d["fp"] / max(d["fp"] + d["tn"], 1)
    fnr = d["fn"] / max(d["fn"] + d["tp"], 1)
    return round(acc * 100, 1), round(fpr * 100, 1), round(fnr * 100, 1)

def main():
    res = {}
    print("\n== A) Selection（保留 40/120）==")
    res["selection"] = eval_selection()
    a = metrics(res["selection"])

    print("== B) Bloom filter ==")
    res["bloom"] = eval_bloom()
    res["bloom"]["theoretical_fpr_pct"] = round(bloom_theoretical_fpr(M, 3, len(S)) * 100, 2)
    res["bloom"]["m"] = M; res["bloom"]["k"] = 3
    b = metrics(res["bloom"])

    print("== C) LLM 摘要 × 2 模型 ==")
    for mn, key in [("glm-4-flash", "llm_glm"), ("qwen", "llm_qwen")]:
        try:
            summ = make_summary(mn)
            res[key] = eval_llm(mn, summ)
        except Exception as e:
            res[key] = {"error": str(e)}
        print(f"   {mn} done")

    # 汇总
    rows = [("Selection(40/120)", *a, res["selection"]["ctx_tok"]),
            ("Bloom filter", *b, res["bloom"]["ctx_tok"]),
            ("LLM摘要 glm-4-flash", *(metrics(res["llm_glm"]) if "tp" in res.get("llm_glm", {}) else (0, 0, 0)),
             res.get("llm_glm", {}).get("ctx_tok", 0)),
            ("LLM摘要 Qwen-0.5B", *(metrics(res["llm_qwen"]) if "tp" in res.get("llm_qwen", {}) else (0, 0, 0)),
             res.get("llm_qwen", {}).get("ctx_tok", 0))]
    print("\n================ 对决结果（Accuracy / FPR / FNR %，预算 tok）================")
    for r in rows:
        print(f"  {r[0]:22s} acc={r[1]:5.1f}  FPR={r[2]:5.1f}  FNR={r[3]:5.1f}  预算={r[4]}")

    res["meta"] = {"N": len(S), "n_query": len(QUERIES), "budget_tok": B,
                   "full_list_tok": LIST_TOK, "rows": [list(r) for r in rows],
                   "date": "2026-08-26",
                   "ref": "玩具复现 arXiv 2608.01326 附录A set membership 案例"}
    save("e6_bloom_vs_summary", res)

    # ---------- 画图 ----------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    names = [r[0] for r in rows]
    accs = [r[1] for r in rows]; fprs = [r[2] for r in rows]; fnrs = [r[3] for r in rows]
    x = range(len(rows)); w = 0.27
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar([i - w for i in x], accs, w, label="Accuracy", color="#4c72b0")
    ax.bar(list(x), fprs, w, label="FPR（幻觉：不在却答在）", color="#dd8452")
    ax.bar([i + w for i in x], fnrs, w, label="FNR（遗忘：在却答不在）", color="#55a868")
    for i, r in enumerate(rows):
        ax.text(i - w, accs[i] + 1.5, f"{accs[i]:.0f}", ha="center", fontsize=9)
        ax.text(i, max(fprs[i], 0) + 1.5, f"{fprs[i]:.0f}", ha="center", fontsize=9)
        ax.text(i + w, max(fnrs[i], 0) + 1.5, f"{fnrs[i]:.0f}", ha="center", fontsize=9)
    ax.set_xticks(list(x)); ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel("%"); ax.set_ylim(0, 110)
    ax.set_title(f"E6 同等 token 预算（≈{B} tok）下的 compaction 对决：120 项集合 × 48 次 membership 查询\n"
                 f"（完整清单 {LIST_TOK} tok；Bloom m={M},k=3，理论FPR {res['bloom']['theoretical_fpr_pct']}%）")
    ax.legend(fontsize=9)
    fig.tight_layout()
    p = os.path.join(RES_DIR, "e6_bloom_vs_summary.png")
    fig.savefig(p, dpi=150)
    print(f"[saved] {p}")

if __name__ == "__main__":
    main()
