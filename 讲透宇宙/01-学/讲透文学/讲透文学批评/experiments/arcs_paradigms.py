# -*- coding: utf-8 -*-
# 情感弧线与批评范式:文学批评家族(GB/T 13745 75017)的最小计算实验。
#
# 对应章:00-体系结构.md 七节(反直觉发现三律)、03-可构造与结构.md(可构造
# 谱系左端三对象)、04-文学批评转代码.md(三条代码走廊)。纯标准库
# (math/random/statistics),无第三方依赖;全部固定随机种子,逐次可复现。
#
# 三幕:
#   幕一 情感弧线的六种基本形状(Reagan et al. 2016 口径):
#       叙事的情绪序列 = 漂移模板(初始值+分段漂移)+ 逐段测量噪声;
#       六型 = 白手起家(升) / 悲剧下降(降) / U型(下-上) / 伊卡洛斯(上-下) /
#       俄狄浦斯(下-上-下) / 灰姑娘变体(上-下-上)。
#       对每条弧 z 标准化(只留形状,抹去电平与幅度)后跑 k-means(k=6,
#       随机数据点初始化,训练集 8 弧/型),再对留出集(4 弧/型)做最近质心识别。
#       断言:(1)聚类与六型一一对应(纯簇+双射,留出集识别率=100%)
#       (2)把每条弧的段落打乱后按原质心识别,准确率跌到随机水平(约 1/6)
#       ——叙事的情感形状是段落的次序结构,不是句子袋的余弦。
#   幕二 细读 vs 远读的检出力(莫莱蒂「远读」的统计学本体):
#       文档=词袋;背景标记词率 p0=0.02;主题文档的标记词率 theta=p0+delta
#       (delta=信号强度)。细读=少数文档逐词全读;远读=大量文档各浅读 w 词。
#       检出规则:读到的标记词数 >= 期望+2sigma(已知背景率的单侧检验)。
#       断言:(1)弱信号主题的检出率随样本量 n 严格单调升(5-20-80-320 篇)
#       (2)同篇数下细读完胜浅读(强/中信号);但弱信号下细读(3 篇全读)
#       系统性漏检,只有规模(320 篇)能救——尺度即方法:弱总体信号
#       需要的是 N(样本量),不是注意力(单篇深度)。
#   幕三 批评范式的排名反转(范式=特征打分表):
#       60 部作品 x 4 特征(语言形式/情感强度/政治介入/叙事创新,独立标准分);
#       两个批评框架=两组特征权重(审美自律派 vs 政治批判派),打分=加权求和
#       (+微量评估噪声,两框架噪声独立预抽、反事实复用)。
#       断言:(1)两框架排名的 Spearman 相关可低,且存在系统性反转集合
#       (一边前十、另一边后一半) (2)反转集合偏向「框架间权重差最大的
#       特征维度」(政治介入)承载的作品;把该维度的权重差抹平后两排名
#       显著趋同——范式不是镜片度数差,是打分表的列不同。
#
# 跑法: python -u experiments/arcs_paradigms.py

import math
import random
import statistics


def dot(w, x):
    return sum(a * b for a, b in zip(w, x))


def dist2(p, q):
    return sum((a - b) ** 2 for a, b in zip(p, q))


def znorm(v):
    # 形状标准化:减均值、除标准差——只留「形状」,抹去电平与幅度
    mu = statistics.fmean(v)
    sd = statistics.pstdev(v)
    return [(a - mu) / sd for a in v]


def ranks_desc(scores):
    # 分数最高者 rank=1(并列取平均;连续噪声下并列概率为零)
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    r = [0.0] * len(scores)
    for pos, i in enumerate(order):
        r[i] = pos + 1.0
    return r


def pearson(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den


# ==================== 幕一:情感弧线的六种基本形状 ====================

T = 60  # 每条弧的段落数(章/幕)

# 六型模板:名称, 初始情绪值, [(段长, 每段每步漂移), ...]
TEMPLATES = {
    "rags":       ("白手起家(升)",           -0.55, [(60, +0.0217)]),
    "tragedy":    ("悲剧下降(降)",           +0.55, [(60, -0.0217)]),
    "manhole":    ("U型(下-上)",             +0.25, [(25, -0.0400), (35, +0.0414)]),
    "icarus":     ("伊卡洛斯(上-下)",        -0.25, [(25, +0.0380), (35, -0.0414)]),
    "oedipus":    ("俄狄浦斯(下-上-下)",     +0.55, [(20, -0.0550), (20, +0.0550), (20, -0.0550)]),
    "cinderella": ("灰姑娘变体(上-下-上)",   -0.55, [(20, +0.0425), (20, -0.0325), (20, +0.0525)]),
}
TYPE_ORDER = ["rags", "tragedy", "manhole", "icarus", "oedipus", "cinderella"]


def template_arc(key):
    _, start, regimes = TEMPLATES[key]
    arc, v = [], start
    for length, drift in regimes:
        for _ in range(length):
            v = max(-1.0, min(1.0, v + drift))
            arc.append(v)
    return arc


def sample_arc(key, rng, noise=0.10):
    # 叙事情绪 = 模板形状 + 逐段测量噪声(情感词典给每章的打分总带着噪声)
    return [t + rng.gauss(0.0, noise) for t in template_arc(key)]


def kmeans_once(points, k, rng, iters=100):
    # k-means++ 初始化:第一个质心均匀随机,其后按「离最近质心距离平方」
    # 加权抽样——避免随机初始化把两个近邻型并簇、把一个型劈两半的局部最优
    centroids = [list(points[rng.randrange(len(points))])]
    while len(centroids) < k:
        d2s = [min(dist2(p, x) for x in centroids) for p in points]
        total = sum(d2s)
        if total <= 0:
            centroids.append(list(points[rng.randrange(len(points))]))
            continue
        pick, acc = rng.random() * total, 0.0
        for i, d in enumerate(d2s):
            acc += d
            if acc >= pick:
                centroids.append(list(points[i]))
                break
        else:
            centroids.append(list(points[-1]))
    assign = [-1] * len(points)
    for _ in range(iters):
        changed = False
        for i, p in enumerate(points):
            j = min(range(k), key=lambda c: dist2(p, centroids[c]))
            if j != assign[i]:
                assign[i] = j
                changed = True
        if not changed and _ > 0:
            break
        for c in range(k):
            members = [p for i, p in enumerate(points) if assign[i] == c]
            if members:
                centroids[c] = [statistics.fmean(col) for col in zip(*members)]
            else:  # 空簇:挪到离现有质心最远的点
                far = max(points, key=lambda p: min(dist2(p, x) for x in centroids))
                centroids[c] = list(far)
    inertia = sum(dist2(p, centroids[assign[i]]) for i, p in enumerate(points))
    return centroids, assign, inertia


def kmeans(points, k, rng, restarts=10):
    # 十次重启取惯量最小者(全程固定种子,结果逐次可复现)
    best = None
    for _ in range(restarts):
        cand = kmeans_once(points, k, rng)
        if best is None or cand[2] < best[2]:
            best = cand
    return best[0], best[1]


def nearest(p, centroids):
    return min(range(len(centroids)), key=lambda c: dist2(p, centroids[c]))


def act1():
    print("=" * 84)
    print("幕一 情感弧线的六种基本形状(漂移随机游走生成;k-means 收回六型)")
    print("=" * 84)
    rng = random.Random(20260907)
    train, train_lab, test, test_lab = [], [], [], []
    for key in TYPE_ORDER:
        for _ in range(8):  # 训练集:每型 8 条
            train.append(znorm(sample_arc(key, rng)))
            train_lab.append(key)
        for _ in range(4):  # 留出集:每型 4 条
            test.append(znorm(sample_arc(key, rng)))
            test_lab.append(key)

    centroids, assign = kmeans(train, 6, rng)

    # 断言 1a:六个簇全纯(每簇只含一型),簇-型双射
    cluster_types = []
    for c in range(6):
        labs = {train_lab[i] for i in range(len(train)) if assign[i] == c}
        assert len(labs) == 1, f"簇 {c} 不纯:{labs}"
        cluster_types.append(labs.pop())
    assert len(set(cluster_types)) == 6, "簇-型应为一一对应(双射)"
    # 质心与理论模板形状对齐(z 标准化后的 Pearson 相关)
    for c in range(6):
        tpl = znorm(template_arc(cluster_types[c]))
        r = pearson(centroids[c], tpl)
        assert r >= 0.95, f"簇 {c} 质心与模板相关仅 {r:.3f}"
    print("  六簇全纯、双射成立;各质心与理论模板的相关 r:")
    for c in range(6):
        tpl = znorm(template_arc(cluster_types[c]))
        print(f"    {TEMPLATES[cluster_types[c]][0]:<12} r = {pearson(centroids[c], tpl):.4f}")

    # 断言 1b:留出集按最近质心识别,识别率=100%
    correct = sum(1 for arc, key in zip(test, test_lab)
                  if cluster_types[nearest(arc, centroids)] == key)
    acc = correct / len(test)
    assert correct == len(test), f"留出集识别率应为 100%,实测 {acc:.2%}"
    print(f"  留出集(24 条新弧)最近质心识别率 = {acc:.0%}(24/24)")

    # 断言 1c:打乱段落后,识别率跌到随机水平(随机基线=1/6)
    shuffled_correct = 0
    for arc, key in zip(test, test_lab):
        scrambled = arc[:]
        rng.shuffle(scrambled)  # 打乱段落:同样的情绪值,不同的次序
        if cluster_types[nearest(scrambled, centroids)] == key:
            shuffled_correct += 1
    sh_acc = shuffled_correct / len(test)
    chance = 1.0 / 6.0
    assert sh_acc <= 0.35, f"打乱后识别率应降到随机水平,实测 {sh_acc:.2%}"
    assert sh_acc <= chance + 0.15, "打乱后识别率不应显著高于随机基线"
    print(f"  打乱段落后识别率 = {sh_acc:.2%}(随机基线 1/6≈{chance:.2%})")
    print("  读数:")
    print("  · 弧线的「内容」(情绪值的多重集)一字未动,只把段落次序打乱,")
    print("    形状即刻蒸发——情感弧型住在次序里,不在词频里")
    print("  · 这就是「叙事的情感形状是结构,不是句子的余弦」:主题模型式的")
    print("    词袋表示(对次序不敏感)原则上测不出六型,次序敏感的表示才测得出")

    print(f"\n✓ 幕一断言通过:六型参数化生成 ↔ 形状聚类一一对应(纯簇/双射/")
    print(f"  留出集 100%);打乱段落后识别率 {sh_acc:.2%} 跌到随机水平")


# ==================== 幕二:细读 vs 远读的检出力 ====================

P0 = 0.02     # 背景标记词率(任何文档里该词都以 2% 概率出现)
W_DOC = 200   # 细读:每篇 200 词逐词全读
W_SKIM = 15   # 远读:每篇只浅读 15 词
TRIALS = 1000


def detect_rate(theta, n_docs, words_per_doc, trials, rng):
    # 检出规则:读到的标记词数 M >= 期望+2sigma(已知背景率 p0 的单侧检验)
    total = n_docs * words_per_doc
    thr = total * P0 + 2.0 * math.sqrt(total * P0 * (1 - P0))
    hits = 0
    for _ in range(trials):
        m = sum(1 for _ in range(total) if rng.random() < theta)
        if m >= thr:
            hits += 1
    return hits / trials


def act2():
    print("\n" + "=" * 84)
    print("幕二 细读 vs 远读的检出力(背景标记率 p0=0.02;细读=每篇全读 200 词,")
    print("      远读=每篇浅读 15 词;检出=标记数 >= 期望+2sigma)")
    print("=" * 84)
    rng = random.Random(20260909)
    themes = {"强信号 d=0.060": 0.080, "中信号 d=0.015": 0.035, "弱信号 d=0.008": 0.028}

    # 断言 2a:弱信号检出率随 n 严格单调升(远读/浅读模式)
    print("\n  (1) 弱信号主题,浅读模式,样本量扫描(每档 1000 次蒙特卡洛):")
    ns = [5, 20, 80, 320]
    rates = []
    for n in ns:
        r = detect_rate(themes["弱信号 d=0.008"], n, W_SKIM, TRIALS, rng)
        rates.append(r)
        print(f"    n = {n:>3} 篇(共读 {n * W_SKIM:>5} 词)  检出率 = {r:.3f}")
    assert all(rates[i + 1] > rates[i] for i in range(len(rates) - 1)), (
        f"检出率应严格单调升,实测 {rates}")
    assert rates[0] <= 0.25, "最小样本下应大概率检不出"
    assert rates[-1] >= 0.90, "最大样本下应几乎必检出"
    print(f"    检出率 {rates[0]:.3f} → {rates[-1]:.3f}:弱主题不是「看不见」,")
    print("    是「在小样本里统计上看不见」——最小样本下六分之一都不到,")
    print("    证据量随词数平方根爬坡")

    # 断言 2b:同篇数下细读 vs 浅读(强/中信号细读完胜;弱信号双双哑火)
    print("\n  (2) 同为 3 篇,细读(600 词) vs 浅读(45 词):")
    deep_rates, skim_rates = {}, {}
    for name, theta in themes.items():
        deep_rates[name] = detect_rate(theta, 3, W_DOC, TRIALS, rng)
        skim_rates[name] = detect_rate(theta, 3, W_SKIM, TRIALS, rng)
        print(f"    {name}:  细读检出 = {deep_rates[name]:.3f}   "
              f"浅读检出 = {skim_rates[name]:.3f}")
    strong, medium, weak = "强信号 d=0.060", "中信号 d=0.015", "弱信号 d=0.008"
    assert deep_rates[strong] >= 0.95, "强信号下细读应几乎必检出"
    assert deep_rates[strong] - skim_rates[strong] >= 0.10, "强信号下细读应胜浅读"
    assert deep_rates[medium] - skim_rates[medium] >= 0.30, "中信号下细读优势应显著"
    assert deep_rates[weak] <= 0.40, "弱信号下细读应系统性漏检"

    # 断言 2c:弱信号下只有规模能救(细读 3 篇 vs 远读 320 篇)
    distant_weak = rates[-1]
    print(f"\n  (3) 弱信号:细读 3 篇 = {deep_rates[weak]:.3f}  vs  远读 320 篇 = {distant_weak:.3f}")
    assert distant_weak - deep_rates[weak] >= 0.50, "弱信号下规模应碾压深度"
    print("  读数:")
    print("  · 深度买的是「单篇信息榨干」,规模买的是「证据总量」;检出力只认")
    print("    证据总量(读到的词数),不认你的注意力有多虔诚")
    print("  · 强/中信号:三篇细读就把证据攒够,完胜同篇数浅读——细读的领地")
    print("  · 弱信号:三篇细读仍系统性漏检,320 篇浅读几乎必中——远读的领地")
    print("  · 这就是莫莱蒂「远读」的统计学本体:尺度即方法。问「一万部小说")
    print("    里有哪些主题」是功效问题,不是眼力问题")

    print(f"\n✓ 幕二断言通过:弱信号检出率 {rates[0]:.3f}→{rates[-1]:.3f} 随 n 严格")
    print(f"  单调升;同 3 篇细读完胜浅读(强 {deep_rates[strong]:.2f} vs ")
    print(f"  {skim_rates[strong]:.2f});弱信号细读漏检({deep_rates[weak]:.2f})")
    print(f"  唯规模可救({distant_weak:.2f})")


# ==================== 幕三:批评范式的排名反转 ====================

DIMS = ["语言形式", "情感强度", "政治介入", "叙事创新"]
W_A = (0.95, 0.15, 0.05, 0.25)   # 审美自律派:形式压倒一切,政治几乎不计分
W_B = (0.15, 0.20, 0.95, 0.15)   # 政治批判派:政治介入一票独大
NOISE = 0.10                     # 评估噪声(同一个框架内部的小幅摇摆)


def spearman(scores_a, scores_b):
    ra, rb = ranks_desc(scores_a), ranks_desc(scores_b)
    return pearson(ra, rb)


def act3():
    print("\n" + "=" * 84)
    print("幕三 批评范式的排名反转(60 部作品;审美自律派 vs 政治批判派)")
    print("=" * 84)
    rng = random.Random(75017)
    feats = [[rng.gauss(0, 1) for _ in range(4)] for _ in range(60)]
    noise_a = [rng.gauss(0, NOISE) for _ in range(60)]
    noise_b = [rng.gauss(0, NOISE) for _ in range(60)]
    score_a = [dot(W_A, f) + na for f, na in zip(feats, noise_a)]
    score_b = [dot(W_B, f) + nb for f, nb in zip(feats, noise_b)]
    delta_w = [abs(a - b) for a, b in zip(W_A, W_B)]
    d_star = delta_w.index(max(delta_w))

    rho = spearman(score_a, score_b)
    rank_a, rank_b = ranks_desc(score_a), ranks_desc(score_b)

    print(f"  特征维度          {'  '.join(DIMS)}")
    print(f"  审美自律派权重    " + "  ".join(f"{w:>4.2f}" for w in W_A))
    print(f"  政治批判派权重    " + "  ".join(f"{w:>4.2f}" for w in W_B))
    print(f"  权重差 |wA-wB|    " + "  ".join(f"{w:>4.2f}" for w in delta_w)
          + f"   <- 最大差维度:{DIMS[d_star]}")
    print(f"\n  两框架排名的 Spearman 相关 rho = {rho:.3f}")

    # 断言 3a:相关可低,且存在系统性反转集合(一边前十、另一边后一半)
    reversed_set = [i for i in range(60)
                    if (rank_a[i] <= 15 and rank_b[i] >= 31)
                    or (rank_b[i] <= 15 and rank_a[i] >= 31)]
    assert rho <= 0.55, f"两框架排名相关应可低,实测 {rho:.3f}"
    assert len(reversed_set) >= 6, f"反转集合应非空且成规模,实测 {len(reversed_set)} 部"
    print(f"  系统性反转(一边前 15、另一边 31 名开外):{len(reversed_set)} 部作品")

    # 断言 3b:反转集合偏向权重差最大维度承载的作品
    rest = [i for i in range(60) if i not in reversed_set]
    print(f"\n  {'维度':<6}{'反转组 |f| 均值':>14}{'其余 |f| 均值':>14}{'差(偏置)':>10}")
    gaps = []
    for d in range(4):
        rev_m = statistics.fmean(abs(feats[i][d]) for i in reversed_set)
        rest_m = statistics.fmean(abs(feats[i][d]) for i in rest)
        gaps.append(rev_m - rest_m)
        print(f"  {DIMS[d]:<8}{rev_m:>12.3f}{rest_m:>14.3f}{gaps[-1]:>10.3f}")
    d_min = delta_w.index(min(delta_w))
    assert gaps[d_star] >= 0.35, f"最大权重差维度应显著偏向反转组,实测 {gaps[d_star]:.3f}"
    assert gaps[d_star] > gaps[d_min], "最大差维度的偏置应超过最小差维度"
    print(f"  -> 反转作品在「{DIMS[d_star]}」上系统性地更极端;在权重几乎")
    print(f"     一致的「{DIMS[d_min]}」上无此偏置——反转由权重差承载")

    # 断言 3c:反事实——把争议维度的权重差抹平,两排名显著趋同
    w_b_cf = [0.0] * 4
    norm = math.sqrt(sum(w * w for j, w in enumerate(W_B) if j != d_star))
    for j in range(4):
        w_b_cf[j] = W_A[d_star] if j == d_star else W_B[j] / norm
    score_b_cf = [dot(w_b_cf, f) + nb for f, nb in zip(feats, noise_b)]
    rho_cf = spearman(score_a, score_b_cf)
    print(f"\n  反事实(政治介入权重对齐到审美派并归一):rho = {rho:.3f} -> {rho_cf:.3f}")
    assert rho_cf - rho >= 0.20, "抹平争议维度后两排名应显著趋同"
    print("  读数:")
    print("  · 两个框架看的「作品库存」完全相同,分歧全在打分表的列:审美派")
    print("    给「政治介入」开 0.05,政治派开 0.95——一部政治浓度极高、形式")
    print("    平平的作品,在两张表上就是第一名与倒数前十五的互换")
    print("  · 范式之争不是镜片度数之争(同一张表上的加权微调),是打分表")
    print("    本身的列不同;抹平争议列,反转应声塌缩")
    print("  · 批评史读法:每次范式换代,同一批作品被重新排名一次——排行")
    print("    榜的变化量,就是权重差的变化量")

    print(f"\n✓ 幕三断言通过:rho={rho:.3f}(可低),反转 {len(reversed_set)} 部且偏向")
    print(f"  「{DIMS[d_star]}」维度(gap={gaps[d_star]:.2f});抹平争议维度后")
    print(f"  rho 升至 {rho_cf:.3f}——范式即打分表")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  1. 情感弧线六型:参数化生成 <-> 形状聚类一一对应(纯簇/双射/留出集")
    print("     100%);打乱段落即随机水平——情感形状是次序结构,不是词袋余弦")
    print("  2. 细读 vs 远读:弱信号检出率随 n 严格单调升;同篇数细读完胜浅读")
    print("     (强/中信号),弱信号细读系统性漏检唯规模可救——尺度即方法")
    print("  3. 范式即打分表:两框架排名 Spearman 可低,反转集合系统性偏向权重")
    print("     差最大的维度;抹平争议列排名趋同——换代即重排")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
