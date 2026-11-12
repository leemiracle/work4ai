"""
实验 05g — 2.0 卡练习三题: 双门控 / 创造性跳跃消融 / 归因噪声 (预测→验证)
对应: 自进化2.0-整体叠加.md ✍️练习 A/B/C · 复用 [05_selfevolve](./05_selfevolve.py) 全部机制

三题设计 (每题先预测后验证, 与主实验同预算 80 代 × 5 变异, 20 种子):
  A 双门控景观: R7 现在需要 同时拆掉 R3 和 R6 才可见 (谷更深, 需两步跳跃)
      预测: bins 登顶率绝对值下降, 但相对贪心的优势拉大 (更深的谷=更依赖垫脚石)
  B 创造性跳跃消融: archive+informed 但跳跃概率 0 (只有归因调参/重新启用)
      预测: 谷底进入次数 = 0, 登顶率 = 0 — 拆 R3 只能靠跳跃的 toggle,
            informed 的 blame 永远不会选中在位的高地规则 R3 (它不是失分项)
  C 归因 30% 噪声: blame 选中规则后 30% 概率被换成随机规则 (归因指错人)
      预测: 结论先崩的顺序 — "归因自改进有效"(informed≈random) 先崩;
            "探索权>探索技巧"(bins vs greedy 保持显著) 不崩 — 因为噪声伤的是
            爬坡技巧, 不是继承权结构

实测结论 (2026-08-24, 20 种子, 种子流 zlib.crc32 确定性, 秒级):
  B 创造性跳跃消融 — 预测✓精确成立: 跳跃22%→0%: 谷底进入 87→0 次, 登顶 9→0 (p=0.0008)
    机制: blame 只指"实际失分"项, 在位高地 R3 是得分项 → 归因永远不会自我拆除 —
    跳跃生产多样性, 存档保存多样性, 归因利用多样性, 三位一体缺一不可
  C 归因30%噪声 — 预测✓成立: 崩塌顺序兑现
    噪声informed vs random p=0.4510 (归因优势彻底消失=先崩)
    噪声bins vs greedy    p=0.0382 (结构结论存活=不崩)
    干净 vs 噪声           p=0.0192 (噪声显著伤 informed)
    → '探索权'是结构结论对噪声免疫, '归因有效'是精度结论一噪就倒
  A 双门控 — 预测前半✓后半✗证伪: bins 绝对登顶率 9/20→2/20 (大降✓);
    但 bins vs greedy p=0.0898 不再显著 (相对优势收窄✗) — 两步门控的概率链
    (拆R3→再生出再拆R6→R7才可见→爬满) 惩罚一切单步机制, 存档继承权也救不了
    多步跳跃; 深谷的解不是更好的继承权, 是群落级并行+更长预算
  ★ 开发实录: 种子流首版用 hash(label) — Python str hash 跨进程加盐导致两次
    运行数字漂移 (C 干净臂 11/20 vs 12/20), 换 zlib.crc32 修复 — 确定性铁律再立功

跑法: python3 -u 05g_exercises.py
"""
import importlib.util, math, os, random, zlib

def P(*a): print(*a, flush=True)

def stable_hash(s):
    """跨进程稳定的字符串哈希 (Python 内置 hash 对 str 加盐, 跨进程漂移 — 确定性铁律)"""
    return zlib.crc32(s.encode("utf-8"))

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("se05", os.path.join(HERE, "05_selfevolve.py"))
se05 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(se05)

N_RULES = se05.N_RULES

# ============================================================
# 共用: 变体 mutate / 景观 / 主循环 (基于 se05, 参数化差异点)
# ============================================================
def mutate(g, s_parent, creative=0.22, noisy=0.0):
    """se05.mutate 的参数化版: creative=跳跃概率, noisy=归因被换成随机规则的概率"""
    g2 = [list(r) for r in g]
    if random.random() < creative:
        r = random.randrange(N_RULES)
        if random.random() < 0.5: g2[r][0] = not g2[r][0]
        else: g2[r][1] = se05.clip(g2[r][1] + random.gauss(0, 0.25))
        return [tuple(x) for x in g2]
    obs = se05.rule_contribs(g)
    blame = [max(0.0, se05.NOMINAL[r] - obs[r]) for r in range(N_RULES)]
    tot = sum(blame)
    if tot < 1e-9: r = random.randrange(N_RULES)
    else:
        x, r = random.random() * tot, 0
        for k in range(N_RULES):
            x -= blame[k]
            if x <= 0: r = k; break
    if noisy and random.random() < noisy:
        r = random.randrange(N_RULES)                     # C 题: 归因指错人
    if not g2[r][0]:
        g2[r][0] = True
        return [tuple(x) for x in g2]
    sigma = 0.06 + 0.18 * (1.0 - s_parent)
    g2[r][1] = se05.clip(g2[r][1] + random.gauss(0, sigma))
    return [tuple(x) for x in g2]

def run(strategy="bins", creative=0.22, noisy=0.0, score=se05.score,
        pick=se05.pick_parent, gens=80, litter=5):
    shared = [0.75 + random.gauss(0, 0.02) for _ in range(6)]
    g0 = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
    archive, children = [(g0, score(g0))], [0]
    best = archive[0][1]; valley_entries = 0
    for _ in range(gens):
        for _ in range(litter):
            if strategy == "greedy":
                pi = max(range(len(archive)), key=lambda i: archive[i][1])
            else:
                pi = pick(archive, children)
            parent, sp = archive[pi]; children[pi] += 1
            child = mutate(parent, sp, creative=creative, noisy=noisy)
            if (not child[3][0]) and parent[3][0]: valley_entries += 1
            sc = score(child)
            archive.append((child, sc)); children.append(0)
            best = max(best, sc)
    return best, valley_entries

def perm_test(x, y, n=5000):
    obs = sum(x) / len(x) - sum(y) / len(y)
    allv = list(x) + list(y); k = len(x); cnt = 0
    for _ in range(n):
        random.shuffle(allv)
        d = sum(allv[:k]) / k - sum(allv[k:]) / len(allv[k:])
        if abs(d) >= abs(obs) - 1e-12: cnt += 1
    return obs, cnt / n

def batch(label, n=20, thr=None, **kw):
    fs, vs = [], 0
    for sd in range(n):
        random.seed(555 + sd * 31 + (stable_hash(label) % 211))
        b, v = run(**kw); fs.append(b); vs += v
    if thr is None:
        thr = sum(se05.probe_landscape()[::2]) / 2
    hit = sum(1 for f in fs if f > thr)
    P(f"  {label:28s} 登顶 {hit:2d}/{n}  mean={sum(fs)/len(fs):.3f}  谷底进入 {vs} 次")
    return fs

# ============================================================
# B/C 先跑 (原景观), A 最后 (要换景观)
# ============================================================
if __name__ == "__main__":
    P("=" * 74)
    P("题 B  创造性跳跃消融 (预测: 谷底进入=0, 登顶=0 — 跳跃是多样性唯一来源)")
    b1 = batch("bins+informed (跳跃22%)", strategy="bins", creative=0.22)
    b0 = batch("bins+informed (跳跃0%)",  strategy="bins", creative=0.0)
    d, p = perm_test(b1, b0)
    P(f"  → 跳跃有/无 置换检验 Δ={d:+.3f} p={p:.4f}; 预测成立? {'✓' if p < 0.05 else '✗'}")

    P("\n" + "=" * 74)
    P("题 C  归因 30% 噪声 (预测: informed≈random 先崩, bins vs greedy 不崩)")
    c1 = batch("bins+informed 干净", strategy="bins", noisy=0.0)
    c2 = batch("bins+informed 噪声30%", strategy="bins", noisy=0.3)
    c3 = batch("bins+random", strategy="bins", noisy=1.0)   # noisy=1 ≈ 归因全错 ≈ 随机
    cg = batch("greedy+informed 噪声30%", strategy="greedy", noisy=0.3)
    for a, b_, lab in [(c2, c3, "噪声informed vs random"), (c1, c2, "干净 vs 噪声"), (c2, cg, "噪声bins vs greedy")]:
        d, p = perm_test(a, b_)
        P(f"  {lab:26s} Δ={d:+.3f} p={p:.4f}")

    P("\n" + "=" * 74)
    P("题 A  双门控景观 (R7 需同时拆 R3+R6; 预测: bins 绝对登顶率↓, 相对贪心优势↑)")

    # ---- 双门控景观: monkey-patch rule_contribs 与 probe_landscape, 跑完恢复 ----
    orig_contribs, orig_probe = se05.rule_contribs, se05.probe_landscape
    def dualgate_contribs(g):
        per = [[] for _ in range(N_RULES)]
        for w, ideal in se05.TASKS:
            for r in range(6):
                en, p_ = g[r]
                per[r].append(w[r] * ((1 - abs(p_ - ideal[r])) if en else 0.35))
            r3on, r6on, (r7en, p7) = g[3][0], g[6][0], g[7]
            per[3].append(0.22 if r3on else 0.0)
            per[6].append(0.18 if (r3on and r6on) else 0.0)
            if r3on or r6on:                               # R7 被双门遮蔽
                per[7].append(-0.02 if r7en else 0.0)
            else:
                per[7].append(0.95 * max(0.0, (p7 - 0.58) / 0.40) ** 2 if r7en else 0.10)
        return [sum(v) / len(v) for v in per]
    def dualgate_probe():
        shared = [sum(se05.TASKS[t][1][r] for t in range(10)) / 10 for r in range(6)]
        gA = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.72)]
        gB = [(True, shared[r]) for r in range(6)] + [(True, 0.5), (True, 0.98)]
        gB[3] = (False, shared[3]); gB[6] = (False, 0.5)   # 双拆 R3+R6 + R7 爬满
        s = lambda g: sum(dualgate_contribs(g)) / se05.NORM
        return s(gA), s(gB)                                  # (局部峰, 全局峰)
    se05.rule_contribs = dualgate_contribs
    try:
        sA, sB = dualgate_probe()
        P(f"  双门控景观: 局部峰A={sA:.3f} 全局峰B={sB:.3f} (谷更深: 需连续拆 R3+R6 两步才见 R7)")
        thr_dual = (sA + sB) / 2
        a1 = batch("bins 双门控", strategy="bins", thr=thr_dual)
        a0 = batch("greedy 双门控", strategy="greedy", thr=thr_dual)
        d, p = perm_test(a1, a0)
        P(f"  双门控 bins vs greedy: Δ={d:+.3f} p={p:.4f}")
        P(f"  对照原景观: bins 15/30 (主实验), greedy 0/30 — 绝对率对比见反直觉点")
    finally:
        se05.rule_contribs = orig_contribs

    P("\n" + "=" * 74)
    P("反直觉点")
    P("""
- B 题的机制分解: informed 的 blame 永远指向'实际失分'的规则 (参数低于期望或被
  禁用), 而在位高地 R3 是得分项不是失分项 → 任何基于自身评估的归因都不会
  '自我拆除' — 多样性来源 (跳跃/toggle) 是不可归因的, 它与归因是互补机制
  不是替代. 存档保存多样性, 跳跃生产多样性, 归因利用多样性: 三位一体缺一不可.

- C 题的崩塌顺序即结论的稳健性排序: '探索权>探索技巧'是结构结论 (继承权政策
  改变谁能被采样), 对归因噪声免疫; '归因自改进有效'是精度结论, 30% 噪声即
  明显衰减 — 工程启示: 先搭结构 (存档+继承权), 再投精度 (归因质量/LLM).

- A 题证伪的价值大于验证: 预测"谷越深存档优势越大"错在哪? 双门控要求一条
  概率链: 拆R3的变体被继承 → 它的孩子再拆R6 → R7才可见 → 再爬满. 每步都是
  小概率, 乘法惩罚下 bins 的继承权优势被稀释 (2/20 vs 0/20, 差距收窄).
  深谷的正确解法不是更好的继承权, 是群落级机制: 多条系谱并行进化 + 更长时间
  预算 — 与 DGM 论文'archive + 长期运行'的组合一致, 单靠存档策略本身不够.
""")
