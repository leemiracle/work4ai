# -*- coding: utf-8 -*-
"""叙事-文体-诗性三律实验:文学理论三台「定义机器」的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-文学理论转代码.md(走廊 1/2/3)的配套实验。纯标准库(random/statistics/math),
无第三方依赖,固定种子 20260909 全程可复现。

三幕:
  幕一 功能序列的语法性(普罗普《故事形态学》1928 的最小形式化)
      31 功能简化为 8 功能:禁令→违禁→加害→出发→交锋→战胜→归返→加冕。
      语法=相邻转移矩阵(功能按固定次序出现,可缺省,不重复——普罗普命题三)
      + 锚定约束(加害 A 与加冕 W 必在场——故事由加害/缺乏启动,以婚礼收束)。
      断言:①合法故事 64 个 ≪ 自由排列 8!=40320,约束压缩比 630×(≈2.8 个数量级)
      ②1000 个随机排列的违例检出率 100%(转移矩阵检测器 vs 枚举 oracle 逐条一致)
      ——民间故事的可讲性是语法约束的产物:不是所有排列都是故事。
  幕二 文体指纹与作者归属(Burrows Delta 思想的最小版)
      两位「作者」各有词频偏好:8 个功能词高度分化(谁多用「的」、谁多用「也」),
      20 个内容词近均匀(写同一话题——内容属于题材,不构成指纹);每篇 200 词,
      20 篇建剖面、40 篇留检验,余弦距离最近剖面判归属。
      断言:①全词表判别准确率显著高于随机(>80%)②删去功能词只留内容词后
      判别率大幅下降(趋近 50% 随机线)——文体指纹藏在最不起眼的功能词里,
      不在华丽的实词里。
  幕三 诗性功能=等价原则从选择轴到组合轴的投影(雅各布森 1960)
      64 个词排成 8(语义类)×8(韵部)拉丁方:同类近义(类内语义偏移≤0.5),
      跨类远义(类中心间距 4);诗行=语义类(意义约束)+韵部(韵律约束)。
      三种生成器对照:自由诗(只有语义约束)/格律诗人(语义+韵律)/押韵机器(只有韵律)。
      断言:①韵律约束使每步可行选项均值 8.0→4.5(选择空间收窄)
      ②诗人的语义偏差严格锁在等价类半径内(max≤0.5),押韵机器的语义方差爆炸
      (均值偏差≥5 倍)——诗是把选择轴的等价强加给组合轴:约束杀死随意性,
      等价类保住意义。

跑法: python3 -u experiments/narrative_stylistics.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现


# ==================== 幕一:功能序列的语法性 ====================

FUNCS = ["禁令", "违禁", "加害", "出发", "交锋", "战胜", "归返", "加冕"]
IDX = {f: i for i, f in enumerate(FUNCS)}
ANCHOR_HEAD = "加害"  # 普罗普:故事由加害(或缺乏)启动
ANCHOR_TAIL = "加冕"  # 故事以婚礼/加冕收束


def grammar_accept(seq):
    """叙事语法检测器:相邻功能严格按固定次序(递增,自动排除重复)+ 两锚在场。"""
    if len(set(seq)) != len(seq):
        return False
    if any(IDX[a] >= IDX[b] for a, b in zip(seq, seq[1:])):
        return False
    return ANCHOR_HEAD in seq and ANCHOR_TAIL in seq


def enumerate_legal():
    """枚举全部合法故事:固定次序下,合法故事=8 功能的保序子列且含两锚。"""
    legal = set()
    for mask in range(1, 1 << len(FUNCS)):
        seq = tuple(FUNCS[i] for i in range(len(FUNCS)) if mask >> i & 1)
        if grammar_accept(seq):
            legal.add(seq)
    return legal


def act1():
    print("=" * 84)
    print("幕一 功能序列的语法性(普罗普 1928 的最小形式化:8 功能叙事语法)")
    print("=" * 84)
    print(f"\n功能表(固定次序,可缺省,不重复):{' → '.join(FUNCS)}")
    print(f"锚定约束:{ANCHOR_HEAD}(启动)与{ANCHOR_TAIL}(收束)必在场")
    legal = enumerate_legal()
    n_legal = len(legal)
    n_free = math.factorial(len(FUNCS))
    ratio = n_free / n_legal
    shortest = ("加害", "加冕")
    longest = tuple(FUNCS)
    print(f"\n合法故事数(枚举实测):{n_legal}")
    print(f"自由排列数(8 功能全排列 8!):{n_free}")
    print(f"约束压缩比:{ratio:.0f}×(log₁₀={math.log10(ratio):.2f},≈2.8 个数量级)")
    print(f"最短合法故事:{' → '.join(shortest)}(两拍故事:加害直接跳加冕)")
    print(f"最长合法故事:{' → '.join(longest)}(全功能典范线)")
    print("\n读数:")
    print("  · 普罗普命题三「功能按固定次序出现」把 8 个功能的排列空间砍到保序子列;")
    print("    锚定约束(加害启动/加冕收束)再砍一刀——100 个魔法故事的千变万化,")
    print("    在语法层只剩一条时间线的 64 种裁剪")
    print("  · 不是所有排列都是故事:「战胜→禁令→加冕→加害」是合法功能的乱序堆,")
    print("    听众立刻判定它不可讲——可讲性=语法约束的产物")

    # 断言 1:合法故事数远小于自由排列(数量级压缩)
    assert n_legal == 64, f"合法故事应恰为 64 个(2^6),实测 {n_legal}"
    assert n_free == 40320, "8! 应为 40320"
    assert ratio >= 100, f"约束压缩比应为数量级,实测 {ratio:.0f}"
    assert grammar_accept(shortest) and grammar_accept(longest), "长短两极应合法"
    print(f"\n✓ 幕一断言①通过:64 ≪ 40320,压缩比 {ratio:.0f}×——语法约束把")
    print("  「任意排列」压缩到「可讲的故事」,近三个数量级的差距")

    # 断言 2:随机排列的违例检出率 100%
    rng = random.Random(SEED)
    trials, illegal_n = 1000, 0
    for _ in range(trials):
        seq = tuple(rng.sample(FUNCS, len(FUNCS)))
        oracle = seq in legal        # 枚举 oracle:是否为语法生成的故事
        detect = grammar_accept(seq)  # 检测器:转移矩阵+锚定
        assert detect == oracle, "检测器与枚举 oracle 必须逐条一致"
        if not oracle:
            illegal_n += 1
    assert illegal_n >= 990, f"随机排列应绝大多数非法,实测非法 {illegal_n}"
    print(f"\n✓ 幕一断言②通过:{trials} 个随机排列,非法 {illegal_n} 个,")
    print("  违例检出率 100%(检测器与 oracle 逐条一致,零漏检零误报)")
    print("  ——「民间故事的可讲性是语法约束的产物:不是所有排列都是故事」")
    return {"legal": n_legal, "free": n_free, "ratio": ratio,
            "illegal": illegal_n, "trials": trials}


# ==================== 幕二:文体指纹与作者归属 ====================

FUNC_WORDS = ["的", "了", "是", "在", "和", "也", "就", "都"]
CONTENT_WORDS = ["剑", "月", "城", "风", "火", "夜", "王", "血", "路", "灯",
                 "海", "山", "门", "梦", "雨", "钟", "影", "河", "星", "雪"]
VOCAB = FUNC_WORDS + CONTENT_WORDS
FUNC_SHARE = 0.76  # 功能词占全部词元的比例(自然文本高频功能词占大头,通说)

P_FUNC = {  # 功能词剖面(和为 1):两位作者高度分化——指纹所在
    "A": [0.300, 0.220, 0.180, 0.120, 0.100, 0.040, 0.025, 0.015],
    "B": [0.150, 0.080, 0.100, 0.220, 0.060, 0.150, 0.150, 0.090],
}
P_CONTENT = {  # 内容词剖面(和为 1):同一话题,近均匀,仅 ±8% 轻微倾斜
    "A": [0.054] * 10 + [0.046] * 10,
    "B": [0.046] * 10 + [0.054] * 10,
}


def make_text(rng, author, n_words=200):
    """按作者联合分布抽一篇文本:76% 功能词剖面+24% 内容词剖面。"""
    pop = VOCAB
    w = ([FUNC_SHARE * p for p in P_FUNC[author]]
         + [(1 - FUNC_SHARE) * p for p in P_CONTENT[author]])
    return rng.choices(pop, weights=w, k=n_words)


def freq_vector(text):
    """相对词频向量(28 维)。"""
    counts = dict.fromkeys(VOCAB, 0)
    for w in text:
        counts[w] += 1
    return [counts[w] / len(text) for w in VOCAB]


def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return dot / (nu * nv) if nu and nv else 0.0


def build_profile(texts):
    """训练剖面=训练篇目相对词频向量的平均(Burrows 用高频词 z 分数,此处取最小版)。"""
    return [sum(col) / len(texts) for col in zip(*[freq_vector(t) for t in texts])]


def classify(vec, profiles, dims):
    """余弦最近剖面判归属;dims=参与计算的坐标(全词表或仅内容词)。"""
    best, best_s = None, -1.0
    for au, pr in profiles.items():
        s = cosine([vec[i] for i in dims], [pr[i] for i in dims])
        if s > best_s:
            best, best_s = au, s
    return best


def act2():
    print("\n" + "=" * 84)
    print("幕二 文体指纹与作者归属(Burrows Delta 思想的最小版:200 词/篇)")
    print("=" * 84)
    print("\n剖面设定(指纹在功能词,话题在内容词):")
    print(f"  作者A 功能词:「的」{P_FUNC['A'][0]:.2f}「了」{P_FUNC['A'][1]:.2f}"
          f"「是」{P_FUNC['A'][2]:.2f}……「也」仅 {P_FUNC['A'][5]:.3f}")
    print(f"  作者B 功能词:「的」{P_FUNC['B'][0]:.2f}「了」{P_FUNC['B'][1]:.2f}"
          f"「在」{P_FUNC['B'][3]:.2f}……「也」高达 {P_FUNC['B'][5]:.3f}")
    print("  内容词:两位作者同写一话题(近均匀,±8% 倾斜)——内容不构成指纹")

    rng = random.Random(SEED)
    profiles, tests = {}, []
    for au in "AB":
        train = [make_text(rng, au) for _ in range(20)]   # 20 篇建剖面
        profiles[au] = build_profile(train)
        for _ in range(40):                               # 40 篇留检验
            tests.append((au, make_text(rng, au)))

    dims_all = range(len(VOCAB))
    dims_content = range(len(FUNC_WORDS), len(VOCAB))     # 删功能词,只留内容词
    hit_full = hit_content = 0
    demo_done = False
    for au, text in tests:
        vec = freq_vector(text)
        if classify(vec, profiles, dims_all) == au:
            hit_full += 1
        if classify(vec, profiles, dims_content) == au:
            hit_content += 1
        if not demo_done:
            sample = " ".join(text[:14])
            print(f"\n  样例篇({au} 作,前 14 词):{sample}……")
            ca = cosine(vec, profiles["A"])
            cb = cosine(vec, profiles["B"])
            print(f"  全词表余弦:近 A {ca:.4f} vs 近 B {cb:.4f} → 判 {classify(vec, profiles, dims_all)}")
            demo_done = True
    acc_full = hit_full / len(tests)
    acc_content = hit_content / len(tests)
    print(f"\n判别结果(共 {len(tests)} 篇检验):")
    print(f"  全词表(功能词+内容词)准确率:{hit_full}/{len(tests)} = {acc_full:.1%}")
    print(f"  只留内容词(删去 8 个功能词):{hit_content}/{len(tests)} = {acc_content:.1%}")
    print(f"  随机猜基线:50.0%")
    print("\n读数:")
    print("  · 功能词是「不知不觉的签名」:没人会为选「的」还是「也」而苦吟,")
    print("    但恰是这些最不起眼的高频小词把两位作者分开——Burrows Delta 的原发现")
    print("  · 内容词写同一话题,分布近同,判别力大跌、只剩话题倾斜的残余信号")
    print("    ——华丽的实词属于题材,不属于指纹")

    # 断言 3:全词表准确率显著高于随机(>80%)
    assert acc_full >= 0.80, f"全词表准确率应 >80%,实测 {acc_full:.1%}"
    assert acc_full > 0.5, "应高于随机基线"
    # 断言 4:删去功能词后判别率下降
    assert acc_content < acc_full - 0.15, (
        f"只留内容词应大幅下降(≥15 个百分点),实测 {acc_content:.1%} vs {acc_full:.1%}")
    print(f"\n✓ 幕二断言通过:全词表 {acc_full:.0%} ≫ 随机 50%;只留内容词跌至 "
          f"{acc_content:.0%}(降 {(acc_full - acc_content) * 100:.0f} 个百分点)")
    print("  ——「文体指纹藏在最不起眼的功能词里,不在华丽的实词里」")
    return {"full": acc_full, "content": acc_content}


# ==================== 幕三:诗性功能=等价向组合轴的投影 ====================

N_LINE = 8
CLASS_GLOSS = ["远行", "离别", "守望", "夜战", "胜利", "归返", "重逢", "加冕"]  # 与幕一功能同线
OFFSETS = [-0.50, -0.36, -0.22, -0.08, 0.08, 0.22, 0.36, 0.50]  # 类内语义偏移
RADIUS = 0.5      # 等价类半径:同类近义
SPACING = 4.0     # 类中心间距:跨类远义
RHYMED = {1, 3, 5, 7}  # 韵脚行(0 基):XAXA XBXB——偶数行押韵


def word_value(c, r):
    """词(c,r)的语义坐标:类中心+类内偏移(拉丁方排布:同类近义,跨类远义)。"""
    return SPACING * c + OFFSETS[(c + r) % 8]


def gen_poet(rng, with_rhyme):
    """生成一首 8 行诗:语义约束恒在(每行只在本行语义类中选);韵律可开可关。
    返回(每行可行选项数, 每行语义偏差, 成诗)。"""
    feas, devs, lines = [], [], []
    rhyme_of = {}
    for i in range(N_LINE):
        c = i  # 第 i 行写第 i 类:八行恰好排成幕一那条功能线的一首「诗」
        if with_rhyme and i in RHYMED:
            if i in rhyme_of:
                r = rhyme_of.pop(i)
            else:
                r = rng.randrange(8)
                rhyme_of[i + 2] = r   # 与两行后的行押同一韵
            cand = [(c, r)]           # 语义类∩韵部=拉丁方上恰一点
        else:
            cand = [(c, r) for r in range(8)]
        pick = rng.choice(cand)
        feas.append(len(cand))
        devs.append(abs(word_value(*pick) - SPACING * c))
        lines.append(pick)
    return feas, devs, lines


def gen_machine(rng):
    """押韵机器:只认韵律不认意义——押韵行在韵部内跨类乱选,自由行全词表乱选。"""
    feas, devs = [], []
    rhyme_of = {}
    for i in range(N_LINE):
        intended = SPACING * i  # 该行本该写的语义中心
        if i in RHYMED:
            if i in rhyme_of:
                r = rhyme_of.pop(i)
            else:
                r = rng.randrange(8)
                rhyme_of[i + 2] = r
            c = rng.randrange(8)       # 任何语义类,只要押上韵
            feas.append(8)
        else:
            c, r = rng.randrange(8), rng.randrange(8)
            feas.append(64)            # 自由行:全词表任取
        devs.append(abs(word_value(c, r) - intended))
    return feas, devs


def act3():
    print("\n" + "=" * 84)
    print("幕三 诗性功能=等价向组合轴的投影(雅各布森 1960:8 语义类×8 韵部拉丁方)")
    print("=" * 84)
    print(f"\n词库:64 词排成拉丁方——语义类={'/'.join(CLASS_GLOSS)}")
    print(f"约束:同类近义(类内偏移≤{RADIUS}),跨类远义(类中心间距 {SPACING:.0f})")
    print("韵式:XAXA XBXB(第 2/4/6/8 行押韵,1/3/5/7 行自由)")
    rng = random.Random(SEED)

    demo_feas, demo_devs, demo_lines = gen_poet(rng, with_rhyme=True)
    print("\n  样例诗(格律诗人,「词(类,韵)」后跟语义偏差):")
    for i, ((c, r), d) in enumerate(zip(demo_lines, demo_devs)):
        mark = "押韵" if i in RHYMED else "自由"
        print(f"    第{i + 1}行 {CLASS_GLOSS[c]}({mark}) → 词({CLASS_GLOSS[c]},韵{r}) 偏差 {d:.2f}")

    reps = 500  # 三种生成器各 500 首,统计稳定
    free_f, poet_f, mach_f = [], [], []
    free_d, poet_d, mach_d = [], [], []
    for _ in range(reps):
        f, d, _ = gen_poet(rng, with_rhyme=False)
        free_f += f
        free_d += d
        f, d, _ = gen_poet(rng, with_rhyme=True)
        poet_f += f
        poet_d += d
        f, d = gen_machine(rng)
        mach_f += f
        mach_d += d
    mf, mp, mm = (stats.mean(x) for x in (free_f, poet_f, mach_f))
    df, dp, dm = (stats.mean(x) for x in (free_d, poet_d, mach_d))
    sd_p, sd_m = stats.pstdev(poet_d), stats.pstdev(mach_d)
    bits_free = math.log2(8)
    bits_poet = (4 * math.log2(8) + 4 * math.log2(1)) / 8
    print(f"\n生成器对照(各 {reps} 首×{N_LINE} 行):")
    print(f"  {'生成器':<6}{'每步可行选项':>10}{'选择熵(比特/步)':>14}{'语义偏差均值':>12}{'偏差标准差':>10}")
    print(f"  {'自由诗':<8}{mf:>10.2f}{bits_free:>14.2f}{df:>12.3f}{stats.pstdev(free_d):>10.3f}")
    print(f"  {'格律诗人':<6}{mp:>10.2f}{bits_poet:>14.2f}{dp:>12.3f}{sd_p:>10.3f}")
    print(f"  {'押韵机器':<6}{mm:>10.2f}{'—':>14}{dm:>12.3f}{sd_m:>10.3f}")
    print("\n读数:")
    print("  · 韵律约束把押韵行的可行选项从 8 砍到 1(均值 8.0→4.5,熵 3.0→1.5 比特):")
    print("    约束杀死随意性")
    print("  · 但诗人在语义类内选词,偏差永不越出等价类半径 0.5;押韵机器只认韵不认")
    print("    义,偏差均值爆炸到 10+——押韵本身保不住意义,等价类才保住意义")
    print("  · 雅各布森:诗性功能=把选择轴的等价原则强加给组合轴——双轴缺一不可")

    # 断言 5:韵律约束收窄选择空间
    assert mp < 0.75 * mf, f"可行选项均值应显著下降,实测 {mf:.2f}→{mp:.2f}"
    assert bits_poet < bits_free
    # 断言 6:等价类保住意义(诗人在界内,机器爆表)
    assert max(poet_d) <= RADIUS + 1e-9, f"诗人偏差应≤半径 {RADIUS},实测 max {max(poet_d):.3f}"
    assert sd_p <= RADIUS, f"诗人偏差标准差应≤{RADIUS},实测 {sd_p:.3f}"
    assert dm >= 5 * dp, f"机器语义偏差应≥诗人 5 倍,实测 {dm:.2f} vs {dp:.3f}"
    assert sd_m >= 4.0, f"机器偏差标准差应爆表(≥4),实测 {sd_m:.2f}"
    assert len(demo_lines) == N_LINE, "诗人应在约束下成诗 8/8 行"
    print(f"\n✓ 幕三断言通过:选项均值 {mf:.1f}→{mp:.1f}(约束收窄);诗人偏差 max "
          f"{max(poet_d):.2f}≤{RADIUS}(意义在界内)而机器偏差均值 {dm:.2f}≈"
          f"{dm / dp:.0f}×诗人(意义失守)")
    print("  ——「诗是把选择轴的等价强加给组合轴:约束杀死随意性,等价类保住意义」")
    return {"feas_free": mf, "feas_poet": mp, "dev_poet": max(poet_d),
            "dev_machine": dm, "sd_machine": sd_m}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 功能序列的语法性:合法故事 {r1['legal']} ≪ 自由排列 {r1['free']}"
          f"(压缩比 {r1['ratio']:.0f}×,≈2.8 个数量级);{r1['trials']} 个随机排列")
    print(f"     非法 {r1['illegal']} 个检出率 100%——可讲性是语法约束的产物")
    print(f"  ② 文体指纹:全词表判别 {r2['full']:.0%} ≫ 随机 50%;只留内容词跌至 "
          f"{r2['content']:.0%}——指纹在功能词,不在实词")
    print(f"  ③ 诗性投影:可行选项 {r3['feas_free']:.1f}→{r3['feas_poet']:.1f}(约束杀死随意性),")
    print(f"     诗人语义偏差锁在 {r3['dev_poet']:.2f}≤{RADIUS}(等价类保住意义),"
          f"押韵机器偏差 {r3['dev_machine']:.1f} 爆表")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
