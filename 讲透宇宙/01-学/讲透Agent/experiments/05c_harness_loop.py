"""
实验 05c — L5 补缺: harness 自进化闭环 (跑基准 → 归因失分 → 改一个 harness 参数 → 重跑)
对应: 自进化2.0-整体叠加.md §7 自查表 L5 行 · harness 五子系统 (Instructions/Verification/Scope)
形态: penguin-harness RSI 的最小复刻 — "跑基准→找失分点→发 N+1 版, 每轮留快照"

闭环四步 (每轮):
  ① EVAL     固定 40 题基准 × 当前 harness 配置 → 分数 + 分题型失分表
  ② ATTRIBUT 失分归因: 找最大失分桶 (negation / conflict / fmt-trap)
  ③ PROPOSE  改"一个"harness 参数 (规则/示例/严格解析+重试) — 真实系统里这步是 LLM, 此处用确定性策略
  ④ VERIFY   候选配置重跑基准: 提分才 commit (验证即证据), 否则拒绝换下一提案
谱系: 每轮 commit 写 05c_lineage/harness_vN.json + LINEAGE.md (版本可回滚 = 进化得以持续的机制)

harness 参数 ≠ 模型参数: 全部是"环境侧"旋钮 — 指令规则(few-shot 示例/解析器严格度/重试预算)。
模型 ("LLM") 冻结: 题型×配置 → 正确率的确定性模拟器, 隔离"harness 的贡献"这一变量。

实测结论 (2026-08-24, 秒级, 骰子钉题 id 跨进程可复现):
  v1 最小 harness (无规则/无示例/宽松/重试0)     : 35.0%   失分主桶 = 否定题(9)≈冲突题(9)
  v2 + 指令规则 R_neg (否定词处理)               : 57.5%   失分主桶 = 冲突题
     ↘ 第 2 轮第一个提案 (无关规则 R_fmt_noise) 分数不动 → 验证门 REJECT ✓ (不盲目爬升)
  v3 + few-shot 示例 E_conflict (冲突消解范例)    : 75.0%   失分主桶 = 格式陷阱题
  v4 + 严格解析器 + 重试预算 1                   : 92.5%   四桶收敛
  ★ 模型零改动, 3 轮 3 个环境旋钮: 35% → 92.5% (+57.5pp) — "模型已够聪明, harness 让它可靠"
  ★ 首跑踩坑实录: 逐题骰子最初钉在 (题id+配置指纹) 上 → 加无关规则也"涨分"(骰子重排假象);
    修复 = 骰子只钉题 id, 配置只改阈值 — 与性能优化Agent v2"基准必须钉种子"同源铁律

跑法: python3 -u 05c_harness_loop.py   (产物: 05c_lineage/ + 05c_harness_loop.png)
"""
import json, os, random, zlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

def P(*a): print(*a, flush=True)

random.seed(42)

# ============================================================
# Part 1: 固定基准 — 40 题, 4 题型 × 10 题 (确定性生成)
# ============================================================
TYPES = ["simple", "negation", "conflict", "fmttrap"]
TYPE_CN = {"simple": "简单题", "negation": "否定题", "conflict": "冲突题", "fmttrap": "格式陷阱题"}
BENCH = [(i // 10, f"q{i:02d}") for i in range(40)]          # (题型编号, 题目 id)

# ============================================================
# Part 2: harness 配置 (被进化的对象) + 冻结的"模型"模拟器
# ============================================================
def default_harness():
    return {"rules": [], "examples": [], "strict_parser": False, "retry": 0}

def p_correct(type_id, h):
    """冻结模型: 题型 × harness → 正确率. 模拟'指令覆盖到该模式才会做'的真实瓶颈"""
    t = TYPES[type_id]
    if t == "simple":   return 0.95
    if t == "negation": return 0.30 + (0.60 if "R_neg" in h["rules"] else 0.0)
    if t == "conflict": return 0.25 + (0.55 if "E_conflict" in h["examples"] else 0.0)
    return 0.20 + (0.70 if (h["strict_parser"] and h["retry"] >= 1) else 0.0)   # fmttrap

def evaluate(h):
    """跑一遍基准: 逐题判定. 骰子只钉题目 id (zlib.crc32 稳定哈希, 跨进程可复现),
    配置只改正确率阈值 — 否则改任何配置都会重掷骰子, 无关改动也会"涨分"
    (与性能优化Agent v2 战役'基准必须钉种子'同源坑, 本实验首跑即踩中)"""
    score, per = 0, {t: [0, 0] for t in TYPES}
    for type_id, qid in BENCH:
        rng = random.Random(zlib.crc32(qid.encode("utf-8")))
        ok = rng.random() < p_correct(type_id, h)
        per[TYPES[type_id]][0] += ok; per[TYPES[type_id]][1] += 1
        score += ok
    return score / len(BENCH), per

def attribution(per):
    """失分归因: 各题型失分数排序 (简单题地板高, 降权). 真实系统 = LLM 读失败日志"""
    gaps = [( (n - ok) * (0.3 if t == "simple" else 1.0), t) for t, (ok, n) in per.items()]
    gaps.sort(reverse=True)
    return gaps

# ============================================================
# Part 3: 提案策略 — 归因桶 → 单参数改动 (一轮只动一个旋钮)
# ============================================================
PROPOSALS = {
    "negation": ("加指令规则 R_neg (否定词处理)", lambda h: {**h, "rules": h["rules"] + ["R_neg"]}),
    "conflict": ("加 few-shot 示例 E_conflict (冲突消解范例)", lambda h: {**h, "examples": h["examples"] + ["E_conflict"]}),
    "fmttrap": ("严格解析器 + 重试预算 1", lambda h: {**h, "strict_parser": True, "retry": 1}),
    # 无关提案 (验证门的考题): 对任何题型正确率都没影响
    "noise":    ("加无关规则 R_fmt_noise (装饰性规则)", lambda h: {**h, "rules": h["rules"] + ["R_fmt_noise"]}),
}
NOISE_ROUND = 2   # 第 2 轮先给出无关提案, 被验证门拒绝后才给真提案

def propose(round_no, gaps, h):
    """按归因顺序给出候选; 第 NOISE_ROUND 轮的第一个候选是无关噪声 (考验证门)"""
    ordered = [t for _, t in gaps if t in PROPOSALS]
    if round_no == NOISE_ROUND:
        ordered = ["noise"] + ordered
    return [(PROPOSALS[t][0], PROPOSALS[t][1](h)) for t in ordered]

# ============================================================
# Part 4: 自进化主循环 — 3 轮, 每轮 EVAL→ATTRIBUT→PROPOSE→VERIFY
# ============================================================
def main():
    lineage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05c_lineage")
    os.makedirs(lineage_dir, exist_ok=True)
    h = default_harness()
    score, per = evaluate(h)
    versions = [(h, score)]
    P("=" * 74)
    P("Part 4  harness 自进化闭环 — 模型冻结, 只动环境旋钮, 3 轮")
    P(f"  v1 (种子) score={score:.3f}   harness={json.dumps(h, ensure_ascii=False)}")
    P(f"  失分归因: " + " > ".join(f"{TYPE_CN[t]} {miss:.0f}" for miss, t in attribution(per)))

    log = [f"# 05c harness 谱系 (验证即证据, 每轮可回滚)\n\n| 版本 | 改动 | 分数 | 失分主桶 |\n|---|---|---|---|",
           f"| v1 | 种子(最小) | {score:.3f} | {TYPE_CN[attribution(per)[0][1]]} |"]

    for rnd in range(1, 4):
        cur_h, cur_s = versions[-1]
        _, per = evaluate(cur_h)
        cands = propose(rnd, attribution(per), cur_h)
        P(f"\n--- 第 {rnd} 轮 ---")
        committed = False
        for desc, cand in cands:                       # VERIFY: 提分才 commit
            cs, _ = evaluate(cand)
            verdict = "KEEP" if cs > cur_s else "REJECT"
            P(f"  候选: {desc:38s} → {cs:.3f} ({verdict}, 基线 {cur_s:.3f})")
            if cs > cur_s:
                versions.append((cand, cs))
                _, per2 = evaluate(cand)
                log.append(f"| v{len(versions)} | {desc} | {cs:.3f} | {TYPE_CN[attribution(per2)[0][1]]} |")
                committed = True
                break
        if not committed:
            P("  ⚠ 全部候选被拒绝, 进化停滞 (回滚点 = 上一版本)")
        vh, vs = versions[-1]
        with open(os.path.join(lineage_dir, f"harness_v{len(versions)}.json"), "w", encoding="utf-8") as f:
            json.dump(vh, f, ensure_ascii=False, indent=2)
        P(f"  → v{len(versions)} 已落盘: harness_v{len(versions)}.json  score={vs:.3f}")

    with open(os.path.join(lineage_dir, "LINEAGE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    P(f"\n谱系已写: 05c_lineage/ (harness_v1..v{len(versions)}.json + LINEAGE.md, 真实系统对应 git 每轮一 commit)")

    # ---- 图: v1..vN 分数阶梯 ----
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    xs = [f"v{i+1}" for i in range(len(versions))]
    ys = [s for _, s in versions]
    ax.plot(xs, ys, "o-", lw=2.2, color="#1f77b4")
    for i, (x, y) in enumerate(zip(xs, ys)):
        ax.annotate(f"{y:.1%}", (i, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=10)
    ax.set_ylabel("基准分数 (40 题)")
    ax.set_title("harness 自进化闭环: 模型冻结, 3 轮只动环境旋钮 (含 1 次验证门拒绝)")
    ax.set_ylim(0.3, 1.0); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "05c_harness_loop.png"), dpi=130)
    P("图已保存: 05c_harness_loop.png")

    P("=" * 74)
    P("反直觉点")
    P("""
- 全程"模型"零改动 — 三轮只加了 1 条规则 / 1 个示例 / 1 组解析器+重试, 35%→92.5%.
  对照 Anthropic 的 harness 对照实验 (同模型, 无 harness 产出不可用 vs 全套 harness
  产出可玩): 提升大头在环境侧, 这是"harness 工程"存在的理由.

- 验证门拒绝的那次是关键设计: 无关规则 R_fmt_noise 看起来"也是改进"(加了东西),
  但分数不动 → 拒绝. 没有验证门的进化循环会积累装饰性复杂度, 直到 harness 本身
  变成泥球 (Trellis 对 CLAUDE.md 变大泥球的警告同源).

- 归因价值的边界(诚实版): 本玩具只有 3 个有效旋钮, 实测任意顺序 3 轮都能到 ~89%
  — 小空间里归因不改变终点, 只加速早期爬坡. 归因的真实价值在旋钮多且含无效项时:
  它是导航(不浪费轮次在装饰性改动上), 验证门只是止损(拒坏不找好). 真实系统里
  ③ 归因那步就是 LLM 的位置(读失败日志→定位模式), 是 L5 层自进化最值钱的一环.

- 首跑即踩中基准陷阱: 骰子若随配置变, 无关改动也会"涨分"(噪声重排假象) —
  任何自进化闭环的第一课是把评估的随机源钉死在题目侧(跨轮可比), 这与
  性能优化Agent v2"跨轮 speedup 不可比, 基准必须钉种子"是同一条铁律.
""")

if __name__ == "__main__":
    main()
