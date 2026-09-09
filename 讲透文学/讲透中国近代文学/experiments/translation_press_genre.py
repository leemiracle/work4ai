# -*- coding: utf-8 -*-
"""译介-报刊-文类三律实验:中国近代文学(1840-1911)三个机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-中国近代文学转代码.md(走廊 1/2/3)的配套实验。纯标准库(random/statistics/math),
无第三方依赖,固定种子 20260909 全程可复现。参数为通说代表性案例的风格化参数
(见各幕题注),模拟不冒充文献计量。

三幕:
  幕一 译介时滞的结构(翻译的到达是不均匀的)
      以 1873-1911 年逐年扩张的翻译事件为样本:时滞=中译年-西书发表年。
      均值参数 35→3 年递减,标准差 14→1.5 收缩,早期带「老库存」重尾
      (早期译者专挑旧名著,后期转向时新作品);文类配额从政治/侦探高度
      集中滑向多元。通说锚:《巴黎茶花女遗事》1848→1899(51 年)、
      《黑奴吁天录》1852→1901(49 年)、《天演论》1893→1898(5 年)、
      福尔摩斯案 1892→1896《时务报》(4 年)。
      断言:①时滞均值随译出年代分桶严格单调下降 ②时滞标准差同步收缩
      ③早期译介文类集中度(顶级份额/HHI)显著高于后期——先到的是被
      挑过的:翻译的到达不均匀。
  幕二 报刊连载的同步化(公共节拍 vs 私人时间)
      一部 24 回连载小说(《官场现形记》式周更),对照两种阅读制度:
      报刊连载(周更发布,读者在发布窗口内追读)与书本自由阅读
      (各自时间各自速度)。300 名读者逐日推演。
      断言:①连载制下读者间进度标准差 ≪ 自由阅读(≥10 倍差距)
      ②共同阅读的可行窗口(≥半数读者同处一回)只在发布节点±数日出现,
      自由阅读制下近乎不存在——报刊把文学从私人时间搬进公共节拍。
  幕三 文类地位的跃迁(小说界革命的等级表读法)
      四文类(古文/诗/词/小说)地位指数=效用 softmax 份额,1840-1930
      逐年演化。机制三件:报刊与稿酬的缓慢推力(基线漂移)、1902 年
      外生观念冲击(梁启超「小说为文学之最上乘」)、冲击后的人才正反馈
      与地位棘轮(效用以「历史高点-0.25」为地板,一旦立顶不回摆)。
      1915 年撤除倡导,1919 年加压测试(黑幕小说式的逆向冲击-1.2)。
      断言:①冲击前(1840-1901)小说份额平稳低位(均值<9%,极差小)
      ②冲击当年份额跳升≥3 倍且存在超越诗文正统的交叉年,此后始终保持
      ③撤除倡导并施加逆向冲击后地位不回摆(1930 年仍居首)
      ——小说界革命改变的不是写作量,是文类的等级表。

跑法: python3 -u experiments/translation_press_genre.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现


# ==================== 幕一:译介时滞的结构 ====================

T0, T1 = 1873, 1911  # 译出年代窗:《瀛寰琐记》创刊到辛亥
GENRES = ["政治小说", "侦探小说", "科学小说", "言情小说", "国民小说", "其他"]
P_EARLY = [0.62, 0.24, 0.07, 0.02, 0.02, 0.03]  # 早期:政治/侦探把持书目
P_LATE = [0.09, 0.15, 0.09, 0.20, 0.15, 0.32]    # 后期:配额摊开渐多元
ANCHORS = [("巴黎茶花女遗事", 1848, 1899), ("黑奴吁天录", 1852, 1901),
           ("天演论", 1893, 1898), ("福尔摩斯案(时务报)", 1892, 1896)]


def lag_mean(t):
    return max(3.0, 35.0 - 0.85 * (t - T0))


def lag_sd(t):
    return max(1.5, 16.0 - 0.42 * (t - T0))


def p_old(t):
    """「老库存」重尾概率:早期译者专挑旧名著,随年代指数消退。"""
    return 0.40 * math.exp(-(t - T0) / 9.0) + 0.02


def genre_p(t):
    x = (t - T0) / (T1 - T0)
    return [a + (b - a) * x for a, b in zip(P_EARLY, P_LATE)]


def draw_lag(rng, t):
    if rng.random() < p_old(t):
        return rng.uniform(20.0, 40.0)   # 老库存:挑几十年前的旧名著
    return max(1.0, rng.gauss(lag_mean(t), lag_sd(t)))


def act1():
    print("=" * 84)
    print("幕一 译介时滞的结构(1873-1911 翻译事件的延迟分布,通说锚风格化参数)")
    print("=" * 84)
    print("\n通说锚(原作年→中译年→时滞):")
    for name, src, tr in ANCHORS:
        print(f"  《{name}》{src}→{tr},时滞 {tr - src} 年")
    print("参数:时滞均值 35→3 年线性递减,标准差 14→1.5 收缩,")
    print("      老库存重尾概率 0.42→0.03 指数消退,逐年翻译量 2→29 种")

    rng = random.Random(SEED)
    events = []
    for t in range(T0, T1 + 1):
        n = 2 + round(0.7 * (t - T0))
        for _ in range(n):
            lag = draw_lag(rng, t)
            genre = rng.choices(GENRES, weights=genre_p(t))[0]
            events.append((t, lag, genre))
    print(f"\n共模拟 {len(events)} 种译作,按时滞分桶(译出年代):")

    buckets = [(1873, 1882), (1883, 1892), (1893, 1902), (1903, 1911)]
    means, sds = [], []
    for lo, hi in buckets:
        lags = [l for (t, l, g) in events if lo <= t <= hi]
        m, s = stats.mean(lags), stats.pstdev(lags)
        means.append(m)
        sds.append(s)
        print(f"  {lo}-{hi}:{len(lags):4d} 种,时滞均值 {m:5.1f} 年,标准差 {s:4.1f}")

    # 断言 1:均值随译出年代严格单调下降
    assert all(a > b for a, b in zip(means, means[1:])), f"均值应单调下降:{means}"
    # 断言 2:标准差同步收缩
    assert all(a > b for a, b in zip(sds, sds[1:])), f"标准差应收缩:{sds}"
    print(f"\n✓ 幕一断言①通过:均值 {means[0]:.1f}→{means[1]:.1f}→{means[2]:.1f}→"
          f"{means[3]:.1f} 年,严格单调下降(≈6 倍压缩)")
    print(f"✓ 幕一断言②通过:标准差 {sds[0]:.1f}→{sds[1]:.1f}→{sds[2]:.1f}→"
          f"{sds[3]:.1f} 年,同步收缩(到达越来越齐整)")

    # 文类集中度:早期窗口 vs 后期窗口
    def window(lo, hi):
        gs = [g for (t, l, g) in events if lo <= t <= hi]
        n = len(gs)
        counts = dict.fromkeys(GENRES, 0)
        for g in gs:
            counts[g] += 1
        shares = [counts[g] / n for g in GENRES]
        top_g = max(counts, key=counts.get)
        return top_g, max(shares), sum(s * s for s in shares), shares

    e_g, e_top, e_hhi, e_sh = window(1873, 1886)
    l_g, l_top, l_hhi, l_sh = window(1900, 1911)
    e_top2 = sum(sorted(e_sh)[-2:])
    print(f"\n早期窗口(1873-1886)文类配额:首位「{e_g}」份额 {e_top:.0%},"
          f"前二合计 {e_top2:.0%},HHI {e_hhi:.2f}")
    print("  " + " ".join(f"{g}{s:.0%}" for g, s in zip(GENRES, e_sh) if s >= 0.03))
    print(f"后期窗口(1900-1911)文类配额:首位「{l_g}」份额 {l_top:.0%},"
          f"HHI {l_hhi:.2f}")
    print("  " + " ".join(f"{g}{s:.0%}" for g, s in zip(GENRES, l_sh) if s >= 0.03))
    # 断言 3:早期集中度显著高于后期
    assert e_top - l_top >= 0.12, f"顶级份额差应≥12 个点:{e_top:.2f} vs {l_top:.2f}"
    assert e_hhi - l_hhi >= 0.08, f"HHI 差应≥0.08:{e_hhi:.2f} vs {l_hhi:.2f}"
    print(f"\n✓ 幕一断言③通过:顶级份额 {e_top:.0%}→{l_top:.0%},HHI {e_hhi:.2f}→"
          f"{l_hhi:.2f}——早期译介被少数文类把持,后期摊开")
    print("  ——「翻译的到达是不均匀的:先到的是被挑过的」")
    return {"n": len(events), "means": means, "sds": sds,
            "e_top": e_top, "l_top": l_top, "e_hhi": e_hhi, "l_hhi": l_hhi}


# ==================== 幕二:报刊连载的同步化 ====================

N_INST = 24        # 一部 24 回的连载小说
PERIOD = 7         # 周更:《官场现形记》式报刊节拍
N_READERS = 300
LAST_RELEASE = PERIOD * (N_INST - 1)   # 第 24 回发布日(0 基)
SURVEYS = [PERIOD * 12 + 4, LAST_RELEASE + 4]  # 中期(第 13 回后)与收束观察日


def serial_read_days(rng):
    """连载制:每回发布窗口内追读——78% 当天,15% 晚 1-3 天,6% 晚 4-7 天,1% 掉队补读。"""
    days = []
    for i in range(N_INST):
        r = rng.random()
        if r < 0.78:
            d = 0
        elif r < 0.93:
            d = rng.randint(1, 3)
        elif r < 0.99:
            d = rng.randint(4, 7)
        else:
            d = rng.randint(8, 14)
        days.append(PERIOD * i + d)
    return days


def book_read_days(rng):
    """书本自由阅读:随时起读,各自速度(均值 6.5 天/回,个体差异 2.5-16 天)。"""
    speed = min(16.0, max(2.5, rng.gauss(6.5, 2.2)))
    day = rng.randint(0, LAST_RELEASE)
    days = []
    for _ in range(N_INST):
        days.append(day)
        day += max(1, round(rng.gauss(speed, 1.2)))
    return days


def progress_fn(read_days):
    """返回 progress(d)=截至 d 日已读回数的查表函数。"""
    def progress(d):
        return sum(1 for x in read_days if x <= d)
    return progress


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 报刊连载的同步化({N_INST} 回周更小说×{N_READERS} 名读者,两种阅读制度)")
    print("=" * 84)
    rng = random.Random(SEED)
    serial = [progress_fn(serial_read_days(rng)) for _ in range(N_READERS)]
    book = [progress_fn(book_read_days(rng)) for _ in range(N_READERS)]

    # 断言 1:进度方差——连载制把读者拉齐,书本制各自进度
    print(f"\n读者进度抽查(已读回数,{N_READERS} 人):")
    ratios = []
    for day in SURVEYS:
        sv = [p(day) for p in serial]
        bv = [p(day) for p in book]
        sd_s, sd_b = stats.pstdev(sv), stats.pstdev(bv)
        ratio = sd_b / max(sd_s, 0.05)
        ratios.append(ratio)
        print(f"  第 {day} 天(发布节点后):连载制均值 {stats.mean(sv):.1f} 回/"
              f"标准差 {sd_s:.2f};书本制均值 {stats.mean(bv):.1f} 回/标准差 {sd_b:.2f}"
              f"(差距 {ratio:.0f}×)")
    assert min(ratios) >= 10, f"进度标准差比应≥10×,实测 {ratios}"

    # 共同阅读窗口:≥半数读者同处一回(第 1-23 回,排除未开始/已读完两堆)
    def co_reading(modes):
        peaks = []
        for d in range(PERIOD, LAST_RELEASE + 1):
            hist = [0] * (N_INST + 1)
            for p in modes:
                hist[p(d)] += 1
            co = max(hist[i] for i in range(1, N_INST)) / len(modes)
            peaks.append((d, co))
        return peaks

    s_peaks = co_reading(serial)
    b_peaks = co_reading(book)
    s_days = sum(1 for d, c in s_peaks if c >= 0.5)
    b_days = sum(1 for d, c in b_peaks if c >= 0.5)
    b_max = max(c for d, c in b_peaks)
    print(f"\n共同阅读窗口(≥50% 读者同处一回的天数,观察期 {len(s_peaks)} 天):")
    print(f"  连载制:{s_days} 天可行;书本制:{b_days} 天可行(峰值也仅 {b_max:.0%})")
    # 断言 2:连载的共读窗口贴着发布节点,书本制几乎不存在
    assert s_days >= 0.8 * len(s_peaks), f"连载制共读窗口应占八成以上,实测 {s_days}"
    assert b_days == 0 and b_max < 0.30, f"书本制不应有共读窗口,实测 {b_days} 天/{b_max:.0%}"
    # 各回共读窗口的开启日:co(已读完第 i 回)首次 ≥50% 的日子应即发布日
    on_node = 0
    for i in range(1, N_INST + 1):
        rel = PERIOD * (i - 1)          # 第 i 回(1 基)发布日
        pair = {}
        for d in range(max(PERIOD, rel - 2), min(LAST_RELEASE, rel + 6) + 1):
            n_at = sum(1 for p in serial if p(d) == i)
            pair[d] = n_at / len(serial)
        cross = min((d for d, c in pair.items() if c >= 0.5), default=None)
        if cross is not None and 0 <= cross - rel <= 2:
            on_node += 1
    share_node = on_node / N_INST
    print(f"  各回共读窗口开启日:{on_node}/{N_INST} 回在发布日±2 天内首破 50%")
    assert share_node >= 0.9, f"共读窗口应贴发布节点开启,实测 {share_node:.0%}"
    print(f"\n✓ 幕二断言通过:进度标准差两查两验均差 {min(ratios):.0f}× 以上;")
    print(f"  共读窗口连载制 {s_days}/{len(s_peaks)} 天、书本制 {b_days} 天,")
    print(f"  峰值 {share_node:.0%} 贴着发布节点——同题剧评/和诗的对象,")
    print("  只在发布节拍附近成批出现")
    print("  ——「报刊把文学从私人时间搬进公共节拍」")
    return {"ratio_min": min(ratios), "ratios": ratios,
            "s_days": s_days, "b_days": b_days, "node": share_node}


# ==================== 幕三:文类地位的跃迁 ====================

GENRES3 = ["古文", "诗", "词", "小说"]
U0 = {"古文": 2.2, "诗": 2.0, "词": 1.0, "小说": 0.0}
Y0, Y1 = 1840, 1930
SHOCK = 1902      # 梁启超《论小说与群治之关系》:「小说为文学之最上乘」
ADV_END = 1915    # 倡导退潮:外生正反馈撤除
RATCHET = 1906    # 地位棘轮生效:效用以历史高点-0.25 为地板
ADVERSE = 1919    # 压力测试:黑幕小说式的逆向冲击


def shares(u):
    ex = [math.exp(u[g]) for g in GENRES3]
    z = sum(ex)
    return {g: e / z for g, e in zip(GENRES3, ex)}


def act3():
    print("\n" + "=" * 84)
    print("幕三 文类地位的跃迁(四文类 softmax 地位指数,1840-1930,1902 观念冲击)")
    print("=" * 84)
    print("机制:①报刊与稿酬对小说的缓慢推力(1890 起加力) 诗文微降")
    print("      ②1902 外生冲击:小说效用+2.0(「文学之最上乘」的等级表翻转)")
    print("      ③冲击后人才正反馈(份额越大流入越多,至 1915)+地位棘轮")
    print("        (效用以历史高点-0.25 为地板:观念一旦翻转不回摆)")
    print("      ④1919 压力测试:逆向冲击-1.2(黑幕小说式败坏),看地位是否回摆")

    rng = random.Random(SEED)
    u = dict(U0)
    hist = []
    u_max = -1e9
    for y in range(Y0, Y1 + 1):
        # 外生冲击
        if y == SHOCK:
            u["小说"] += 2.0
        # 基线漂移:1890 年后报刊稿酬加力;1911 年后时段外,漂移归零
        if y <= 1911:
            u["小说"] += 0.004 if y < 1890 else 0.012
            u["古文"] -= 0.002
            u["诗"] -= 0.002
            u["词"] -= 0.001
        # 冲击后的人才正反馈(倡导期)
        if SHOCK <= y < ADV_END:
            u["小说"] += 0.03
        # 逆向冲击(压力测试)
        if y == ADVERSE:
            u["小说"] -= 1.2
        # 微噪声
        for g in GENRES3:
            u[g] += rng.gauss(0.0, 0.015)
        # 地位棘轮
        u_max = max(u_max, u["小说"])
        if y >= RATCHET:
            u["小说"] = max(u["小说"], u_max - 0.25)
        hist.append((y, shares(u)))

    def sh(y, g):
        return next(s for yy, s in hist if yy == y)[g]

    pre = [s["小说"] for y, s in hist if y <= SHOCK - 1]
    pre_mean, pre_sd = stats.mean(pre), stats.pstdev(pre)
    print(f"\n冲击前(1840-1901)小说份额:均值 {pre_mean:.1%},标准差 {pre_sd:.1%},"
          f"全程 {min(pre):.1%}-{max(pre):.1%}")
    print(f"1901→1902 小说份额:{sh(1901, '小说'):.1%} → {sh(1902, '小说'):.1%}"
          f"(跳升 {sh(1902, '小说') / sh(1901, '小说'):.1f}×)")
    # 断言 1:冲击前平稳低位,且始终低于诗与文
    assert pre_mean < 0.09 and pre_sd < 0.012 and max(pre) < 0.11
    assert all(s["小说"] < s["诗"] for y, s in hist if y <= SHOCK - 1)
    # 断言 2:冲击当年跳升 ≥3 倍
    assert sh(1902, "小说") >= 3 * sh(1901, "小说")
    # 交叉年:小说首次同时超过古文与诗
    cross = next(y for y, s in hist
                 if s["小说"] > s["古文"] and s["小说"] > s["诗"])
    print(f"交叉年:{cross} 年(小说份额首次同时超过古文与诗)")
    assert 1902 <= cross <= 1912, f"交叉年应在 1902-1912,实测 {cross}"
    assert all(s["小说"] > s["古文"] and s["小说"] > s["诗"]
               for y, s in hist if y >= cross)
    # 断言 3:不可逆——撤倡导+逆向冲击后仍居首
    gap = min(s["小说"] - max(s["古文"], s["诗"])
              for y, s in hist if y >= 1920)
    print(f"1919 逆向冲击后小说份额:{sh(ADVERSE, '小说'):.1%}(地板托住,不回摆)")
    print(f"1920-1930 小说对诗文之首的最小领先:{gap:.1%};1930 年格局:"
          + " ".join(f"{g}{sh(1930, g):.0%}" for g in GENRES3))
    assert gap > 0 and sh(1930, "小说") > 0.30
    print("\n✓ 幕三断言通过:冲击前平稳低位(均值 "f"{pre_mean:.1%}"
          f"),1902 跳升 {sh(1902, '小说') / sh(1901, '小说'):.1f}×,"
          f"交叉年 {cross},此后始终居首;")
    print(f"  1915 撤倡导、1919 逆向冲击均未能回摆——等级表一旦翻转即是棘轮")
    print("  ——「小说界革命改变的不是写作量,是文类的等级表」")
    return {"pre_mean": pre_mean, "cross": cross, "gap": gap,
            "s1902": sh(1902, "小说"), "s1930": sh(1930, "小说")}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 译介时滞:均值 {r1['means'][0]:.0f}→{r1['means'][3]:.0f} 年单调下降,"
          f"标准差 {r1['sds'][0]:.1f}→{r1['sds'][3]:.1f} 收缩;文类集中度")
    print(f"     顶级份额 {r1['e_top']:.0%}→{r1['l_top']:.0%}——翻译的到达不均匀,"
          f"先到的是被挑过的")
    print(f"  ② 连载同步:读者进度标准差差距两次抽查均 ≥{r2['ratio_min']:.0f}×,共读窗口")
    print(f"     连载 {r2['s_days']} 天 vs 书本 {r2['b_days']} 天且 {r2['node']:.0%} "
          f"贴发布节点——文学进了公共节拍")
    print(f"  ③ 文类跃迁:小说份额冲击前均值 {r3['pre_mean']:.1%} 平稳低位,")
    print(f"     1902 跳升后交叉年 {r3['cross']} 登顶,1930 年 {r3['s1930']:.0%} "
          f"仍居首——等级表翻转不可逆")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
