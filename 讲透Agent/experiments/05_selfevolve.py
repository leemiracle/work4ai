"""
实验 05 — 最小 DGM 复刻: 自改 system prompt 的 Agent, "存档开放式探索" vs "贪心单链"
对应文档: 讲透Agent/05-自进化延伸.md §4.5 + 自进化2.0-整体叠加.md §9
参照: Darwin Gödel Machine (arXiv:2505.22954) 三机制的最小复刻:
  ① 自改自身配置  ② 实证评估做选择  ③ 变体存档保垫脚石

映射表 (DGM 概念 → 本实验):
  Agent 的 system prompt = 规则集基因组 (8 条规则, 各有 开关 + 参数)
  编码基准 (SWE-bench)   = 10 个任务的隐藏打分 (每任务有权重 w 与理想参数 ideal)
  冻结的基础模型 (LLM)   = 条件突变算子: 读评估反馈 → 编辑被归因牵连的规则
  自指耦合 (编码能力=自改能力) = 当前分数越高 → 突变越精准 (σ 越小)
  开放式探索 (archive)   = 保留全部变体, 父代按分数概率采样 (贪心 = 只从最优当父代)

景观欺骗设计 (本实验的核心机关):
  R3 = "旧路径"高地 (+0.22), 且在位时 R6 旧补丁有效 (+0.18)
  R7 = "新路径", 被 R3 门控: R3 在位时 R7 的贡献被遮蔽成 -0.02 (归因看不见!)
       R3 关闭后 R7 才亮出真实贡献, 但需要把参数从 ~0.72 爬到 0.98 (坡道函数)
  → 贪心链: 拆 R3 立即掉进深谷 (评估变差→改动被丢弃), 且 R7 在位时归因为零
    ("向上盲区": 局部视角看不见被遮蔽的全局更优解) → 永远卡在局部峰 A
  → 存档链: 深谷变体 (低分但"有趣") 留在存档里被再次采样 → 从谷底归因看到 R7
    → 爬坡到全局峰 B —— 这就是 DGM "垫脚石" 机制的复刻

实测结论 (30 种子 × 80 代 × 每代 5 次变异-评估, 纯标准库秒级, 2026-08-24):
  贪心单链       : 登顶 0/30, 终代 0.746 (范围 0.745-0.747) — 焊死局部峰 A
  存档+随机变异  : 登顶 11/30, 终代均值 0.765 — 拿到继承权后随机也能过谷
  存档+归因自改  : 登顶 15/30, 终代均值 0.784 — 完整最小 DGM
  置换检验(5000): vs 贪心 p<0.0001; vs 随机 p=0.048 — 双消融均显著
  ★ 最大跳变来自"继承权政策"(0/30→11/30), 其次才是"自改进技巧"(+4/30)
    → 探索权 > 探索技巧: 给垫脚石留继承权, 比更会变异更重要

跑法: python3 -u 05_selfevolve.py   (产物: 05_selfevolve.png)
"""
import random, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

def P(*a): print(*a, flush=True)

random.seed(20260824)

# ============================================================
# Part 1: 世界 — 10 个任务 × 8 条规则的隐藏打分景观
# ============================================================
N_RULES, N_TASKS = 8, 10
NORM = 5.7   # 归一常数 (每任务理论满分 ≈ 5.7)

TASKS = []
for t in range(N_TASKS):
    w = [0.70 + 0.02 * ((t * 3 + r * 5) % 5) for r in range(6)]  # R0-R5 主项
    ideal = [0.75 + 0.04 * math.sin(t * 1.7 + r * 0.9) for r in range(6)]
    w += [0.0, 0.85]          # R6 结构性补丁(见 bonus), R7 新路径
    ideal += [0.5, 0.98]
    TASKS.append((w, ideal))

def rule_contribs(g):
    """每条规则在 10 任务上的平均观测贡献 — agent 的'评估日志'就是这份归因"""
    per = [[] for _ in range(N_RULES)]
    for w, ideal in TASKS:
        for r in range(6):
            en, p = g[r]
            per[r].append(w[r] * ((1 - abs(p - ideal[r])) if en else 0.35))
        r3on, r6on, (r7en, p7) = g[3][0], g[6][0], g[7]
        per[3].append(0.22 if r3on else 0.0)            # R3 高地
        per[6].append(0.18 if (r3on and r6on) else 0.0) # 旧补丁只托举旧路径
        if r3on:   # R7 被 R3 遮蔽: 开着只有干扰, 关着无事 — 归因完全看不见它
            per[7].append(-0.02 if r7en else 0.0)
        else:      # 门开了: 坡道函数, 低参数区产出平缓但非零 (中间进步可被选择看见)
            per[7].append(0.95 * max(0.0, (p7 - 0.58) / 0.40) ** 2 if r7en else 0.10)
    return [sum(v) / len(v) for v in per]

def score(g):
    return sum(rule_contribs(g)) / NORM

def clip(p): return min(0.99, max(0.01, p))

def probe_landscape():
    """三个标定基因组: 局部峰 A / 深谷 V / 全局峰 B"""
    shared = [sum(TASKS[t][1][r] for t in range(N_TASKS)) / N_TASKS for r in range(6)]
    gA = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
    gV = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
    gV[3] = (False, shared[3])                            # 只拆 R3 → 掉谷
    gB = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.98)]
    gB[3] = (False, shared[3])                            # 拆 R3 + 爬满 R7 → 全局峰
    return score(gA), score(gV), score(gB)

# ============================================================
# Part 2: 冻结的"LLM" — 读反馈改自己 prompt 的突变算子
# ============================================================
NOMINAL = [sum(TASKS[t][0][r] for t in range(N_TASKS)) / N_TASKS for r in range(6)] + [0.18, 0.95]

def mutate(g, s_parent, mode):
    """模拟 LLM 自改 system prompt. mode: informed(归因导向) / random(无反馈)"""
    g2 = [list(r) for r in g]
    if random.random() < 0.22:                            # 创造性跳跃 (22%, 两策略相同)
        r = random.randrange(N_RULES)
        if random.random() < 0.5: g2[r][0] = not g2[r][0]
        else: g2[r][1] = clip(g2[r][1] + random.gauss(0, 0.25))
        return [tuple(r) for r in g2]
    if mode == "random":                                  # 消融: 不读反馈, 均匀乱改
        r, sigma = random.randrange(N_RULES), 0.15
    else:                                                 # informed: 归因牵连的规则, 分越高改得越准
        obs = rule_contribs(g)
        blame = [max(0.0, NOMINAL[r] - obs[r]) for r in range(N_RULES)]
        tot = sum(blame)
        if tot < 1e-9: r = random.randrange(N_RULES)
        else:
            x, r = random.random() * tot, 0
            for k in range(N_RULES):
                x -= blame[k]
                if x <= 0: r = k; break
        if not g2[r][0]:                                  # 读 spec 自改: 被牵连且被禁用的规则
            g2[r][0] = True                               # → 显然该重新启用 (R7 死端修复)
            return [tuple(x) for x in g2]
        sigma = 0.06 + 0.18 * (1.0 - s_parent)            # 自指耦合: 能力强→编辑精准
    g2[r][1] = clip(g2[r][1] + random.gauss(0, sigma))
    return [tuple(r) for r in g2]

# ============================================================
# Part 3: 三种进化策略 — 唯一差异是"父代选择政策"
# ============================================================
def pick_parent(archive, children):
    """DGM 式存档采样 + 适应度共享(quality-diversity, MAP-Elites 思想):
    按分数档位竞争(档位权重只看分数, 不看数量), 档内均匀且新鲜者优先
    → 防止'一堆同分中性变体'稀释低分垫脚石的继承权"""
    smax = max(s for _, s in archive) + 1e-9
    bins = {}
    for i, (_, s) in enumerate(archive):
        bins.setdefault(round(s, 2), []).append(i)
    bw = {b: (b / smax) ** 2 for b in bins}
    x, acc = random.random() * sum(bw.values()), 0.0
    for b, w in bw.items():
        acc += w
        if x <= acc:
            pool = [i for i in bins[b] if children[i] == 0] or bins[b]
            return random.choice(pool)
    return random.choice([i for i in range(len(archive))])

def run(strategy, gens=80, litter=5):
    shared = [0.75 + random.gauss(0, 0.02) for _ in range(6)]   # 手工种子 agent (DGM 同款设定)
    g0 = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
    archive, children = [(g0, score(g0))], [0]
    best = archive[0][1]; curve = [best]
    mode = "random" if strategy == "archive+random" else "informed"
    for _ in range(gens):
        for _ in range(litter):                        # 每个孩子独立选父代 (DGM: 每迭代一个候选)
            if strategy == "greedy":                   # 贪心: 父代永远 = 历史最优
                pi = max(range(len(archive)), key=lambda i: archive[i][1])
            else:                                      # 存档: 档位采样保垫脚石
                pi = pick_parent(archive, children)
            parent, sp = archive[pi]; children[pi] += 1
            child = mutate(parent, sp, mode)
            sc = score(child)
            archive.append((child, sc)); children.append(0)
            best = max(best, sc)
        curve.append(best)
    return curve, best

# ============================================================
# Part 4: 跑 30 种子 × 3 策略 + 置换检验
# ============================================================
def perm_test(x, y, n=5000):
    obs = sum(x) / len(x) - sum(y) / len(y)
    allv = list(x) + list(y); k = len(x); cnt = 0
    for _ in range(n):
        random.shuffle(allv)
        d = sum(allv[:k]) / k - sum(allv[k:]) / len(allv[k:])
        if abs(d) >= abs(obs) - 1e-12: cnt += 1
    return obs, cnt / n

if __name__ == "__main__":
    sA, sV, sB = probe_landscape()
    thr = (sA + sB) / 2
    P("=" * 70)
    P("Part 1  景观标定 (归一化分数)")
    P(f"  局部峰 A (全规则开, R3 旧路径)   : {sA:.3f}")
    P(f"  深谷 V   (拆 R3, R7 未爬)       : {sV:.3f}   ← 谷深 {sA - sV:.3f}, 贪心链不可穿越")
    P(f"  全局峰 B (拆 R3 + R7 爬到 0.98) : {sB:.3f}   ← 比 A 高 {sB - sA:.3f}")
    P(f"  判峰阈值 thr = (A+B)/2          : {thr:.3f}")
    P("=" * 70)

    SEEDS, GENS = 30, 80
    strategies = ["greedy", "archive+random", "archive+informed"]
    curves, finals, hits = {}, {}, {}
    for si, st in enumerate(strategies):
        cs, fs = [], []
        for seed in range(SEEDS):
            random.seed(10007 * seed + 101 * si + 7)
            c, b = run(st, gens=GENS)
            cs.append(c); fs.append(b)
        curves[st], finals[st] = cs, fs
        hits[st] = sum(1 for b in fs if b > thr)
        m = [sum(c[g] for c in cs) / len(cs) for g in range(GENS + 1)]
        P(f"Part 4  {st:18s} 终代最优 mean={sum(fs)/len(fs):.3f}  "
          f"min={min(fs):.3f}  max={max(fs):.3f}  登顶B率 {hits[st]}/{SEEDS}")

    P("-" * 70)
    d1, p1 = perm_test(finals["archive+informed"], finals["greedy"])
    d2, p2 = perm_test(finals["archive+informed"], finals["archive+random"])
    P(f"置换检验(5000次): 存档+归因 vs 贪心      Δ={d1:+.3f}  p={p1:.4f}")
    P(f"置换检验(5000次): 存档+归因 vs 存档+随机 Δ={d2:+.3f}  p={p2:.4f}")

    # ---- 画图: 左=学习曲线(均值±std), 右=登顶率 ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.6))
    colors = {"greedy": "#d62728", "archive+random": "#ff9f1c", "archive+informed": "#1f77b4"}
    labels = {"greedy": "贪心单链 (无开放式探索)", "archive+random": "存档+随机变异 (无自改进)",
              "archive+informed": "存档+归因自改 (完整 DGM)"}
    for st in strategies:
        cs = curves[st]
        m = [sum(c[g] for c in cs) / len(cs) for g in range(GENS + 1)]
        sd = [math.sqrt(sum((c[g] - m[g]) ** 2 for c in cs) / len(cs)) for g in range(GENS + 1)]
        xs = list(range(GENS + 1))
        ax1.plot(xs, m, lw=2.2, color=colors[st], label=labels[st])
        ax1.fill_between(xs, [a - b for a, b in zip(m, sd)], [a + b for a, b in zip(m, sd)],
                         color=colors[st], alpha=0.15)
    ax1.axhline(sA, ls="--", lw=1, color="#888"); ax1.text(0.2, sA + 0.004, "局部峰 A", fontsize=9, color="#555")
    ax1.axhline(sB, ls="--", lw=1, color="#888"); ax1.text(0.2, sB + 0.004, "全局峰 B", fontsize=9, color="#555")
    ax1.set_xlabel("代数 (每代 5 次变异+评估)"); ax1.set_ylabel("历史最优分数")
    ax1.set_title("最小 DGM: 存档保垫脚石 vs 贪心爬山 (30 种子 × 80 代, 对齐 DGM 原文 80 迭代)")
    ax1.legend(fontsize=9, loc="lower right"); ax1.grid(alpha=0.3)
    bs = [hits[st] / SEEDS for st in strategies]
    bars = ax2.bar([labels[st] for st in strategies], bs, color=[colors[st] for st in strategies])
    for b, v, st in zip(bars, bs, strategies):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.0%}\n({hits[st]}/{SEEDS})",
                 ha="center", fontsize=10)
    ax2.set_ylim(0, 1.15); ax2.set_ylabel("登顶全局峰 B 的种子比例")
    ax2.set_title("发现被遮蔽路径的概率")
    ax2.tick_params(axis="x", labelsize=8.5)
    fig.tight_layout()
    fig.savefig("05_selfevolve.png", dpi=130)
    P("\n图已保存: 05_selfevolve.png")

    P("=" * 70)
    P("反直觉点")
    P("""
- 三条策略的'创造力'完全相同 (同一突变算子, 同一 22% 创造性跳跃), 唯一差异是
  父代选择政策 — 贪心只从历史最优当父代, 存档按档位竞争给所有变体继承权.
  结果贪心 0/30 焊死在局部峰: 不是它想不到拆 R3, 而是拆 R3 的'掉分孩子'
  永远没资格当父代. → 开放式探索的本质是'给垫脚石留继承权', 不是'更会变异'.

- 归因盲区是结构性的: R3 在位时 R7 的观测贡献是 -0.02, 任何基于自身评估的
  归因都看不见 R7 的价值 (向上盲区). 只有'已经拆了 R3 的失败变体'才能看见
  R7 → 低分变体携带高分变体拿不到的信息, 这就是存档的价值.

- 探索权 > 探索技巧: 0/30→11/30 的跳变全部来自继承权政策 (存档+档位采样),
  归因导向的自改进只再 +4/30 (p=0.048) — 它加速的是'从谷底爬坡'的速度,
  而存档保证的是'能到谷底并活着'. 与 DGM 消融同构 (arXiv:2505.22954:
  去掉自改进或去掉存档, SWE-bench 20%→50% 的爬坡都消失), 也和 quality-
  diversity 文献 (MAP-Elites/novelty search, Clune 学派) 的核心主张一致:
  保多样性机制本身就是进化能力, 不是锦上添花.

- 调参实录即教训: 首版登顶率仅 1/30, 逐层修复了三处 — ①禁用规则的死端
  (归因看见'预期0.95实测0'显然该重新启用) ②批次选父反而稀释继承权(回滚)
  ③中性大群稀释垫脚石(档位采样=适应度共享). 每一处都对应真实 agent 自进化
  系统的一个工程要害: 读 spec 的自改才有方向; 父代政策比变异算子更关键;
  同分变体堆会闷死探索.
""")
