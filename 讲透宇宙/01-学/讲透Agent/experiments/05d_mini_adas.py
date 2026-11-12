"""
实验 05d — L4 补缺: mini-ADAS — "workflow 即代码, 设计即搜索" 的最小可跑版
对应: 自进化2.0-整体叠加.md §7 自查表 L4 行 · ADAS (arXiv:2408.08435) / AFlow (arXiv:2410.10762) 思想复刻

ADAS 核心主张: "agent 架构设计"不是手工活, 是搜索问题 — 元 agent 在(代码)设计空间里
搜索工作流, 实证评估做选择. 本实验把三要素各留一个最小实现:
  设计空间   workflow = direct(求解器) + 可选算子集 ⊆ {decompose 分解, verify 校验,
             retry 重试, ensemble2 双路集成} (规范序执行, 2^4=16 个工作流)
  元 agent   冻结为确定性提议器 (toggle 算子变异 + 随机探索) — 隔离"搜索的价值"变量,
             与 05/05b 的"冻结 LLM"同一手法; 真系统里提议器 = LLM 写代码
  实证评估   24 题训练集打分选优, 12 题测试集报告 — 训练/测试分离 (搜索不许看测试)

任务模拟器 (诚实声明: 确定性模拟, 非真 LLM): 3 题型 × 12 题, 骰子钉题 id (crc32, 05c 教训前置)
  单步题  base 0.90                    ensemble2 +0.05
  多步题  base 0.35, decompose → 0.88
  噪声题  base 0.45, verify → 0.60, verify+retry → 0.88
搜索: 5 迭代 × 每代 3 候选 (变异最优 ×2 + 全随机 ×1), 存档保历史
对照: 空间仅 16 个 → 搜索结束后穷举验证"搜到的是否全局最优" (真实 ADAS 天文空间做不到)

实测结论 (20 种子 × 5 迭代 × 3 候选, 秒级, 2026-08-24):
  穷举地面真值: direct+decompose+verify+retry+ensemble2  训练 0.958 / 测试 1.000 / 成本 ×5
  种子工作流 direct                                          训练 0.583 / 测试 0.583 / 成本 ×1
  toggle 单算子翻转: 达全局最优 10/20, 末代训练均值 0.875 — 半数种子卡在"平坦山脊"
  block  LLM 式块编辑: 达全局最优 17/20, 末代训练均值 0.933 — 可靠性显著更高
  ★ 编辑粒度提升的是"达标率"(可靠性), 不是速度(两者达标中位迭代都是 2)
  ★ verify 单加在 8 题噪声桶上期望只翻 ~1 题 → 比特式爬山常年在山脊失速;
    必须协同落成 verify+retry 的块编辑, 正是 LLM 提议器相对比特变异的真实优势
  ★ 开发实录两坑: ①首跑训练/测试划分 i//12 漏整类噪声题 (穷举对照揪出)
    ②单跑对比换种子结论翻转 → 改 20 种子统计 (轶事≠证据)

跑法: python3 -u 05d_mini_adas.py   (产物: 05d_mini_adas.png)
"""
import itertools, os, random, zlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

def P(*a): print(*a, flush=True)

random.seed(31415)

# ============================================================
# Part 1: 任务 — 36 题 (3 题型 × 12), 骰子钉题 id
# ============================================================
TYPES = ["single", "multi", "noisy"]
TYPE_CN = {"single": "单步题", "multi": "多步题", "noisy": "噪声题"}
TRAIN = [(t, f"train{t}_{j}") for t in range(3) for j in range(8)]   # 每型 8 题
TEST  = [(t, f"test{t}_{j}")  for t in range(3) for j in range(4)]   # 每型 4 题

def p_correct(type_id, wf):
    t = TYPES[type_id]
    if t == "single": return 0.90 + (0.05 if "ensemble2" in wf else 0.0)
    if t == "multi":  return (0.88 if "decompose" in wf else 0.35) + (0.03 if "ensemble2" in wf else 0.0)
    base = 0.45
    if "verify" in wf: base = 0.88 if "retry" in wf else 0.60
    return base + (0.03 if "ensemble2" in wf else 0.0)

def evaluate(wf, items):
    score = 0
    for type_id, qid in items:
        if random.Random(zlib.crc32(qid.encode())).random() < p_correct(type_id, wf):
            score += 1
    return score / len(items)

def wf_cost(wf):
    return 1 + len(wf)   # direct + 每个可选算子各 1 单位调用成本

def wf_code(wf):
    """把工作流打印成伪代码 (workflow 即代码)"""
    lines = ["solve(task):"]
    if "decompose" in wf: lines.append("  subs = decompose(task)            # 多步题: 拆子问题")
    else:                 lines.append("  subs = [task]")
    lines.append("  ans = direct(subs)                   # 基础求解器 (种子唯一能力)")
    if "ensemble2" in wf: lines.append("  ans = majority(ans, direct(subs))  # 双路集成")
    if "verify" in wf:    lines.append("  if not verify(ans):")
    if "retry" in wf:     lines.append("    ans = direct(subs, seed+1)       # 校验失败→重试")
    elif "verify" in wf:  lines.append("    mark(ans, uncertain)             # 只校验不重试")
    return "\n".join(lines)

# ============================================================
# Part 2: mini-ADAS 搜索 — 冻结元 agent (确定性提议器) + 存档 + 实证选择
# ============================================================
ALL_OPS = ["decompose", "verify", "retry", "ensemble2"]

def mutate_wf(wf, style="toggle"):
    """元 agent 的编辑动作. style='toggle': 单算子翻转 (比特式爬山);
    style='block': 随机增/删 1-2 个算子 (LLM 式重写 — 真系统里 LLM 改的是整段代码,
    天然能一次落成'verify+retry'这类必须协同的改动)"""
    if style == "toggle":
        return tuple(sorted(set(wf) ^ {random.choice(ALL_OPS)}))
    missing = [op for op in ALL_OPS if op not in wf]
    if missing and (not wf or random.random() < 0.7):
        k = min(len(missing), random.choice([1, 2]))
        return tuple(sorted(set(wf) | set(random.sample(missing, k))))
    if wf:
        k = min(len(wf), random.choice([1, 2]))
        return tuple(sorted(set(wf) - set(random.sample(list(wf), k))))
    return tuple(sorted({random.choice(ALL_OPS)}))

def random_wf():
    return tuple(sorted(op for op in ALL_OPS if random.random() < 0.4))

def search(style, iters=5, cands=3):
    seed = ()
    archive = [(seed, evaluate(seed, TRAIN))]
    curve = [archive[0][1]]
    for it in range(iters):
        best_wf, best_s = max(archive, key=lambda x: x[1])
        proposals = [mutate_wf(best_wf, style), mutate_wf(best_wf, style), random_wf()]
        for wf in proposals:
            archive.append((wf, evaluate(wf, TRAIN)))
        curve.append(max(s for _, s in archive))
    return archive, curve

# ============================================================
# Part 3: 主流程 — 两种提议器 × 20 种子同预算对比 + 穷举对照
# ============================================================
if __name__ == "__main__":
    P("=" * 74)
    P("Part 3  mini-ADAS: 设计即搜索 (5 迭代 × 3 候选, 训练 24 题 / 测试 12 题, 20 种子)")
    # 穷举先算全局最优 (搜索的地面真值)
    full = []
    for k in range(5):
        for combo in itertools.combinations(ALL_OPS, k):
            full.append((evaluate(tuple(combo), TRAIN), tuple(combo)))
    full.sort(reverse=True)
    global_opt, global_score = full[0][1], full[0][0]
    P(f"  穷举地面真值: 全局最优 = direct+{'+'.join(global_opt)}  训练 {global_score:.3f} / 成本 {wf_cost(global_opt)}")

    stats = {}
    for style, cn, color in [("toggle", "toggle 单算子翻转", "#d62728"), ("block", "block LLM 式块编辑", "#1f77b4")]:
        reached, iters_hit, curves, bests = 0, [], [], []
        for sd in range(20):
            random.seed(1000 + sd * 17 + (0 if style == "toggle" else 500))
            archive, curve = search(style)
            best_wf, best_train = max(archive, key=lambda x: x[1])
            curves.append(curve); bests.append(best_train)
            if best_train >= global_score - 1e-9:
                reached += 1
                iters_hit.append(curve.index(global_score))
        stats[style] = (curves, reached, iters_hit, bests, color, cn)
        med = sorted(iters_hit)[len(iters_hit)//2] if iters_hit else -1
        P(f"  [{cn}]  达全局最优 {reached}/20  达标中位迭代 {med}  末代训练最优 mean={sum(bests)/len(bests):.3f}")

    P("\n  block 版典型搜出工作流 (workflow 即代码):")
    for line in wf_code(global_opt).splitlines():
        P("    " + line)
    P(f"  该工作流 测试集 {evaluate(global_opt, TEST):.3f} vs 种子 direct 测试集 {evaluate((), TEST):.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.2))
    for style in ("toggle", "block"):
        curves, _, _, _, color, cn = stats[style]
        m = [sum(c[i] for c in curves) / len(curves) for i in range(6)]
        sd_ = [ (sum((c[i]-m[i])**2 for c in curves)/len(curves))**0.5 for i in range(6)]
        ax1.plot(range(6), m, "o-", lw=2.2, color=color, label=cn)
        ax1.fill_between(range(6), [a-b for a,b in zip(m,sd_)], [a+b for a,b in zip(m,sd_)], color=color, alpha=0.15)
    ax1.set_xlabel("搜索迭代"); ax1.set_ylabel("训练集最优 (20 种子均值±std)")
    ax1.set_title("同预算搜索曲线"); ax1.legend(fontsize=9); ax1.grid(alpha=0.3)
    names = ["toggle\n单算子翻转", "block\nLLM 式块编辑"]
    bars = ax2.bar(names, [stats[s][1]/20 for s in ("toggle","block")], color=[stats[s][4] for s in ("toggle","block")])
    for b_, s in zip(bars, ("toggle","block")):
        ax2.text(b_.get_x()+b_.get_width()/2, b_.get_height()+0.02, f"{stats[s][1]}/20", ha="center", fontsize=11)
    ax2.set_ylabel("5 迭代内达全局最优的种子比例"); ax2.set_ylim(0, 1.1); ax2.grid(alpha=0.3, axis="y")
    ax2.set_title("搜索达标率")
    fig.tight_layout()
    HERE = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(HERE, "05d_mini_adas.png"), dpi=130)
    P("\n图已保存: 05d_mini_adas.png")

    P("=" * 74)
    P("反直觉点")
    P("""
- 单次运行的搜索对比是轶事: 首跑 toggle 卡死在 rank 8/16, 次跑 toggle 一代撞顶 —
  换种子结论翻转. 不做多种子统计的"搜索方法A优于B"结论一律不可信 (与主实验
  30 种子家规同源; ADAS/AFlow 论文的单跑对比因此只能算证据下限).

- 穷举对照是本玩具的奢侈: 空间仅 16 个, 可直接给搜索配"地面真值"; 真实 ADAS
  的设计空间是图灵完备代码, 永远无法穷举, 论文只能报 baseline 对比. 但穷举
  在小空间里揪出了本实验自己的训练/测试划分 bug (首跑 i//12 漏了整类噪声题)
  — 全量验证是搜索系统最好的自检.

- 成本维度的沉默: 两种提议器最终都收敛到'全算子堆满' (成本 ×5) — 只优化分数
  的搜索必然偏爱重工作流; 真实系统必须把成本纳入选择压力 (AFlow 多目标评分),
  否则推理费用失控.
""")
