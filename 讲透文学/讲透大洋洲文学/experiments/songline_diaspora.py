# -*- coding: utf-8 -*-
"""歌线地理记忆-口传谱系保真-散居双家园市场三律模拟:大洋洲文学家族实验(GB/T 75087)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-大洋洲文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。
原住民文化概念(歌线/梦时/口传谱系)一律按学术通说口径作风格化模拟,
不涉及任何具体族群的神圣知识内容;机制断言是模型读数,不作文化事实
认证,更不作文学价值判断。

三幕:
  幕一 歌线的地理记忆(songline):
      A "歌-地"绑定: 每段歌与一个地景锚点绑定(位置记忆法的考古版);对照为
        无地绑定的串行清单。绑定项有两个独立提取线索(歌词+地景),且锚点
        序列固定、不随清单加长而互相干扰;清单项受近因/干扰衰减。
      B 打断歌线: 地景被分割(篱笆/私有化/边界)使若干链位不可通行,须凭
        航位推算硬闯(每断链一段),且每次重新"入歌"都有再定向损耗;同等
        割裂数下,碎片化(分散断点)断得次数更多,比整块占用更伤。
      断言: ①绑定项逐项检索成功率与"80% 合格传诵率"显著高于对照,且清单
              加长时绑定组不衰减、对照组持续衰减
            ②仅割去 5% 链位即令全程到达率崩到一成以下——失败率对割裂比例
              是超线性的;碎片化分割比整块占用更伤
              ——歌线是把大陆装进歌里的纠错码。
  幕二 口传谱系的代际保真(whakapapa):
      A 纯口传: 韵律与仪式构成冗余校验(口误破坏韵律,当场检出即纠正),
        只有未检出的替换错/换位错才积累;但"可编辑性"低——刻意插入假名
        须过若干诵读者的社群校验(分布式否决)。
      B 转录引入: 第 3 代抄成文本(誊抄本身带入一次抄误);此后社群记忆训练
        衰退(认知卸载:外生假设,账单记在 00 章):口误率上升、校验力下降,
        不可检错加速积累;文本是单点权威,一个抄写员就能静默改谱。
      断言: ①口传的谱系顺序保真高(冗余编码),可编辑性低(社群拦截假名)
            ②转录后校验机制衰退:第 10 代保真反低于纯口传,末代不可检错率
              升到纯口传 3 倍以上;文本静默编辑成功率远高于口传分布式否决
              ——文字不仅记录传统,也解除了记忆的武装。
  幕三 散居写作的双家园市场(太平洋散居):
      市场: 侨居国市场(新西兰/澳大利亚英语主流,盘子大)与母国市场(萨摩亚/
      斐济等,盘子小);散居作者三种题材: H 回望母国/D 双家园离散经验/U
      侨居国本土题材;另设两地本土书作主流竞争盘。
      断言: ①双市场作品(D)在两个市场各有核心读者(核心读者率过线)但均非
              主流(主流榜份额低)
            ②"回望母国"(H)在侨居国有异域溢价(主流榜份额高),在母国遇冷
              (份额近零)——同一本书两种定价;供给侧行为按市场理性把散居
              作者推向 H(两种乡愁之间的套利),而母国市场并不买账。
      分工声明: 东欧文学家族实验管"政治流亡的回归"(流亡作家回家时家里
      等着谁),本家族管"散居的无回归"(双家园常态化的市场结构),两题不同,
      互不重复。

跑法: python -u experiments/songline_diaspora.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现


# ==================== 幕一:歌线的地理记忆(songline) ====================

NS = (12, 24, 48)                      # 传诵清单长度(歌段/条目数)
M_RECALL = 2400                        # 每组传诵者人数
V_VERSE, L_LAND = 0.70, 0.55           # 歌词线索/地景线索的独立提取率
CTRL_BASE, CTRL_DECAY = 0.70, 0.032    # 无绑定清单: 基线提取率/按绝对位次的干扰衰减
PASS_FRAC = 0.80                       # "合格传诵"= 至少 80% 条目正确

L_LEGS, P_CHAIN, Q_BRIDGE, REORIENT = 40, 0.99, 0.38, 0.80
N_CONF = 800                           # 随机割裂构型数
J_LIST = (0, 1, 2, 4, 8)               # 被割链位数
CONT_START = 13                        # 整块占用的起点(避开首尾)


def bound_item_p():
    """歌-地绑定项的提取率: 两条独立线索,任一命中即成。"""
    return 1.0 - (1.0 - V_VERSE) * (1.0 - L_LAND)


def ctrl_item_p(i):
    """无绑定清单第 i 项的提取率: 基线×按绝对位次的干扰衰减。"""
    return CTRL_BASE * math.exp(-CTRL_DECAY * i)


def act1():
    print("=" * 84)
    print("幕一 歌线的地理记忆: '歌-地'绑定检索 与 分割地景的导航崩塌(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED)
    pb = bound_item_p()

    # ---- 1a "歌-地"绑定 vs 无绑定清单 ----
    print(f"\n[1a] 记忆检索: 每组 {M_RECALL} 名传诵者; 绑定项提取率={pb:.3f}"
          f"(双线索), 对照基线 {CTRL_BASE:.2f}×exp(-{CTRL_DECAY}·位次)")
    print(f"{'清单长':<8}{'方式':<10}{'逐项成功率':>10}{'合格传诵率(≥80%对)':>18}")
    res = {}
    for n in NS:
        for bound in (True, False):
            ok_tot, passes = 0, 0
            for _ in range(M_RECALL):
                ok = sum(1 for i in range(n)
                         if rng.random() < (pb if bound else ctrl_item_p(i)))
                ok_tot += ok
                if ok >= PASS_FRAC * n:
                    passes += 1
            rate = ok_tot / (M_RECALL * n)
            res[(n, bound)] = (rate, passes / M_RECALL)
            print(f"{n:<8d}{'歌-地绑定' if bound else '串行清单':<10}"
                  f"{rate:>10.3f}{passes / M_RECALL:>18.3f}")
    print("读数: 绑定=位置记忆法的考古版——锚点序列固定,加长清单不互相干扰;")
    print("      清单越长干扰越重,中段条目最先塌")

    b12, b24, b48 = res[(12, True)][1], res[(24, True)][1], res[(48, True)][1]
    c12, c24, c48 = res[(12, False)][1], res[(24, False)][1], res[(48, False)][1]
    assert res[(24, True)][0] - res[(24, False)][0] > 0.30, \
        "绑定组逐项成功率应显著高于对照(>0.30)"
    assert b24 > 0.70 and c24 < 0.02, "合格传诵率: 绑定>0.70 且对照<0.02"
    assert b48 >= b12 - 0.05, "绑定组加长清单不应衰减(位置锚定)"
    assert res[(12, False)][0] > res[(24, False)][0] > res[(48, False)][0], \
        "对照组逐项成功率应随清单加长单调衰减(干扰)"
    assert c12 > c24, "对照组合格率应随清单加长下降"
    print(f"\n[1a]✓ 绑定 24 段逐项 {res[(24, True)][0]:.3f} vs 对照 "
          f"{res[(24, False)][0]:.3f}; 合格率 {b24:.0%} vs {c24:.1%};"
          f" 加长到 48: 绑定 {b48:.0%} 不降反稳, 对照 {c48:.1%} 衰减到底")

    # ---- 1b 分割地景: 割链位数 vs 全程到达率 ----
    def route_success(severed):
        """整条歌线一次行进的到达率(逐链精确计算)。severed: 被割链位集合。"""
        s, bridged = 1.0, False
        for i in range(L_LEGS):
            if i in severed:
                s *= Q_BRIDGE          # 凭航位推算硬闯本段
                bridged = True
            else:
                s *= REORIENT if bridged else P_CHAIN  # 断后首链再定向
                bridged = False
        return s

    print(f"\n[1b] 分割地景: 全程 {L_LEGS} 链, 链内接力 {P_CHAIN}/链, 断链硬闯 "
          f"{Q_BRIDGE}/段, 断后再入歌首链 ×{REORIENT}")
    print(f"{'割链数':<8}{'割裂占比':>8}{'碎片化到达率':>12}{'失败率':>8}"
          f"{'失败/割裂(放大倍数)':>20}{'整块到达率':>10}")
    scat_arr, cont_arr = {}, {}
    for j in J_LIST:
        vals = []
        for _ in range(N_CONF):
            severed = set(rng.sample(range(L_LEGS), j))
            vals.append(route_success(severed))
        scat_arr[j] = statistics.mean(vals)
        cont_arr[j] = route_success(set(range(CONT_START, CONT_START + j)))
        f = 1.0 - scat_arr[j]
        amp = "—" if j == 0 else "%.1f 倍" % (f / (j / L_LEGS))
        print(f"{j:<8d}{j / L_LEGS:>8.1%}{scat_arr[j]:>12.4f}{f:>8.1%}"
              f"{amp:>20}{cont_arr[j]:>10.4f}")
    print("读数: 割 2 链(5%地景)到达率已塌到一成以下,失败率对割裂占比是超线性的;")
    print("      同等割裂数,碎片化断得次数多、再入歌次数多,比整块占用更伤")
    print("      ——歌线是把大陆装进歌里的纠错码: 冗余在链上,断链即弃权")

    f0, f1 = 1.0 - scat_arr[0], 1.0 - scat_arr[1]
    f2, f4 = 1.0 - scat_arr[2], 1.0 - scat_arr[4]
    assert f1 - f0 > 0.35, "第一道篱笆就应造成>0.35 的到达率损失"
    assert scat_arr[2] < 0.10, "割 5% 链位即应令到达率<10%"
    assert f2 / (2 / L_LEGS) > 15, "失败率对割裂占比应超线性(放大>15 倍)"
    assert f4 > 0.985, "割 10% 链位应近乎全毁"
    for j in (2, 4, 8):
        assert cont_arr[j] > scat_arr[j], "整块占用的到达率应高于碎片化分割"
    print(f"\n[1b]✓ 到达率 {scat_arr[0]:.3f}→{scat_arr[1]:.3f}→{scat_arr[2]:.4f}"
          f"→{scat_arr[4]:.4f}; 失败放大 {f2 / (2 / L_LEGS):.0f} 倍(5%割裂);"
          f" 整块 vs 碎片化: {cont_arr[2]:.4f} vs {scat_arr[2]:.4f}"
          "——歌线是大陆的纠错码")


# ==================== 幕二:口传谱系的代际保真(whakapapa) ====================

N_NAMES, GENS, LINEAGES, TEXT_AT = 30, 10, 600, 3
E0, C0, S0 = 0.06, 0.75, 0.008         # 纯口传: 口误率/韵律校验力/换位率
SCRIBE_ERR = 0.012                     # 誊抄一次的抄误率
OFF_E, OFF_C = 1.18, 0.85              # 卸载后: 口误增长率/校验衰减率
N_RECITERS, FLAG_P = 5, 0.30           # 社群校验: 诵读者数/各自察觉异常率
SILENT_EDIT, EDIT_AT = 0.90, 5         # 文本静默编辑成功率/插入假名的代


def act2():
    print("\n" + "=" * 84)
    print("幕二 口传谱系的代际保真: 韵律冗余校验 vs 转录后的认知卸载")
    print("=" * 84)
    rng = random.Random(SEED + 1)

    def rates(regime, t):
        """第 t 代的(口误率, 校验力, 换位率); 转录后按卸载假设演化。"""
        if regime == "oral" or t <= TEXT_AT:
            return E0, C0, S0
        k = t - TEXT_AT
        return E0 * OFF_E ** k, C0 * OFF_C ** k, S0 * OFF_E ** k

    out = {}
    for regime in ("oral", "text"):
        ident = [1.0] * (GENS + 1)          # 每代谱系身份保真(未坏名占比)
        order = [1.0] * (GENS + 1)          # 每代顺序保真(相邻对正确占比)
        bad_last = 0.0                       # (保留注释位)
        for _ in range(LINEAGES):
            corrupt = [False] * N_NAMES      # 名字身份是否已坏
            swapped = [False] * (N_NAMES - 1)  # 相邻对是否已换位
            for t in range(1, GENS + 1):
                e_t, c_t, s_t = rates(regime, t)
                if regime == "text" and t == TEXT_AT:
                    corrupt = [b or rng.random() < SCRIBE_ERR for b in corrupt]
                for i in range(N_NAMES):
                    if not corrupt[i] and rng.random() < e_t \
                            and rng.random() >= c_t:
                        corrupt[i] = True     # 口误且未被韵律检出→永久替换
                for i in range(N_NAMES - 1):
                    if not swapped[i] and rng.random() < s_t \
                            and rng.random() >= c_t:
                        swapped[i] = True     # 换位且未检出→顺序错固化
            # 只汇总末代快照(逐代曲线用解析近似另算)
            out.setdefault(regime + "_ident", []).append(
                1.0 - sum(corrupt) / N_NAMES)
            out.setdefault(regime + "_order", []).append(
                1.0 - sum(swapped) / (N_NAMES - 1))
            e_last, c_last, _ = rates(regime, GENS)
            out.setdefault(regime + "_u", []).append(e_last * (1 - c_last))
        # 逐代身份保真(解析近似,与末代 MC 对照)
        for t in range(1, GENS + 1):
            e_t, c_t, _ = rates(regime, t)
            u = e_t * (1 - c_t)
            ident[t] = ident[t - 1] * (1 - u)
            if regime == "text" and t == TEXT_AT:
                ident[t] *= (1 - SCRIBE_ERR)
        out[regime + "_curve"] = ident
        out[regime + "_u_last"] = statistics.mean(out[regime + "_u"])

    print(f"\n[2a] 纯口传(韵律与仪式冗余校验) vs 第 {TEXT_AT} 代引入文本转录(此后"
          f"认知卸载: 口误×{OFF_E}/代, 校验×{OFF_C}/代)\n")
    print(f"{'代际':<8}{'口传保真(近似)':>14}{'转录线保真(近似)':>16}")
    cu, ct = out["oral_curve"], out["text_curve"]
    for t in (1, 3, 4, 6, 8, 10):
        print(f"{'第%d代' % t:<8}{cu[t]:>14.3f}{ct[t]:>16.3f}")
    o_id, t_id = statistics.mean(out["oral_ident"]), statistics.mean(out["text_ident"])
    o_or, t_or = statistics.mean(out["oral_order"]), statistics.mean(out["text_order"])
    u_o, u_t = out["oral_u_last"], out["text_u_last"]
    print(f"\n末代 MC 读数: 身份保真 口传 {o_id:.3f} vs 转录线 {t_id:.3f}; "
          f"顺序保真 {o_or:.3f} vs {t_or:.3f};")
    print(f"末代不可检错率: 口传 {u_o:.4f}/代 vs 转录线 {u_t:.4f}/代"
          f"(×{u_t / u_o:.1f})——转录后校验衰退,坏错加速")

    # ---- 2b 可编辑性: 刻意插入假名 ----
    oral_ins = (1 - FLAG_P) ** N_RECITERS       # 口传: 过五诵读者的分布式否决
    oral_keep = oral_ins * (1 - E0 * (1 - C0)) ** (GENS - EDIT_AT)
    text_keep = SILENT_EDIT * 0.98              # 文本: 单点静默编辑,此后长存
    print(f"\n[2b] 可编辑性: 第 {EDIT_AT} 代试图插入一个假名")
    print(f"{'机制':<24}{'插入/编辑成功':>12}{'第10代仍在':>10}")
    print(f"{'口传·社群分布式否决':<24}{oral_ins:>12.3f}{oral_keep:>10.3f}")
    print(f"{'文本·抄写员单点静默改':<24}{SILENT_EDIT:>12.3f}{text_keep:>10.3f}")
    print("读数: 口传要改谱得说服每一个诵读者;文本时代一个抄写员就能改——")
    print("      可编辑性翻上来,篡改阻力塌下去")

    assert o_id >= 0.82, "纯口传末代身份保真应≥0.82(冗余编码兜底)"
    assert o_id - t_id > 0.20, "转录线末代保真应比纯口传低 0.20 以上(卸载悖论)"
    assert o_or >= 0.95, "口传顺序保真应≥0.95(韵律锁序)"
    assert u_t > 3.0 * u_o, "转录线末代不可检错率应>纯口传 3 倍"
    assert text_keep > 4.0 * oral_keep, "文本静默编辑留存应>口传社群否决线 4 倍"
    print(f"\n✓ 幕二断言通过: 口传身份 {o_id:.3f}/顺序 {o_or:.3f} 高保真但可编辑性低"
          f"(假名留存 {oral_keep:.3f}); 转录线第 10 代身份 {t_id:.3f} 反低于口传, "
          f"不可检错 ×{u_t / u_o:.1f}, 静默编辑留存 {text_keep:.3f}"
          "——文字不仅记录传统,也解除了记忆的武装")


# ==================== 幕三:散居写作的双家园市场(太平洋散居) ====================

W_HOST = {"H": 1.38, "D": 0.95, "U": 1.00}   # 侨居国市场题材权重(H=异域溢价)
W_HOME = {"H": 0.60, "D": 0.92, "U": 0.35}   # 母国市场题材权重(H=遇冷)
N_DIAS, N_HOST_DOM, N_HOME_DOM = 1500, 4500, 900
HOME_SCALE = 0.12                              # 母国市场规模(相对侨居国)
THEME_P = {"H": 0.35, "D": 0.35, "U": 0.30}
N_NEWAUTH = 800                                # 供给侧: 新作者选题模拟
HIT_Q, CORE_Q = 0.10, 0.40                     # 主流=前 10%, 核心读者=前 40%


def act3():
    print("\n" + "=" * 84)
    print("幕三 散居写作的双家园市场: 异域溢价·双核读者·两种乡愁的套利")
    print("=" * 84)
    rng = random.Random(SEED + 2)

    def q_draw():
        return max(0.05, min(1.20, rng.gauss(0.50, 0.15)))

    books = []  # (seg, host_appeal, home_appeal)
    for _ in range(N_DIAS):
        r, q = rng.random(), q_draw()
        th = "H" if r < 0.35 else ("D" if r < 0.70 else "U")
        books.append((th, q * W_HOST[th], q * W_HOME[th]))
    for _ in range(N_HOST_DOM):                 # 侨居国本土书
        q = q_draw()
        books.append(("host_dom", q * 1.00, q * 0.03))
    for _ in range(N_HOME_DOM):                 # 母国本土书
        q = q_draw()
        books.append(("home_dom", q * 0.04, q * 1.15))

    def shares(pool, key):
        """返回(各段主流榜份额, 各段核心读者率, 阈值)。pool 为该市场的书。"""
        vals = sorted((b[key] for b in pool), reverse=True)
        n = len(vals)
        t_hit = vals[int(HIT_Q * n) - 1]
        t_core = vals[int(CORE_Q * n) - 1]
        seg_n = {}
        for b in pool:
            seg_n[b[0]] = seg_n.get(b[0], 0) + 1
        hits, core = {}, {}
        for b in pool:
            if b[key] >= t_hit:
                hits[b[0]] = hits.get(b[0], 0) + 1
            if b[key] >= t_core:
                core[b[0]] = core.get(b[0], 0) + 1
        share = {s: hits.get(s, 0) / sum(hits.values()) for s in seg_n}
        corer = {s: core.get(s, 0) / seg_n[s] for s in seg_n}
        return share, corer, t_hit

    host_pool = [b for b in books if b[0] != "home_dom"]
    home_pool = [b for b in books if b[0] != "host_dom"]
    h_share, h_core, t1 = shares(host_pool, 1)
    m_share, m_core, t2 = shares(home_pool, 2)

    name = {"H": "H 回望母国", "D": "D 双家园", "U": "U 侨居国题材",
            "host_dom": "侨居国本土书", "home_dom": "母国本土书"}
    print(f"\n主流=该市场接受度前 {HIT_Q:.0%}, 核心读者=前 {CORE_Q:.0%}; "
          f"母国市场规模=侨居国 {HOME_SCALE:.0%}\n")
    print(f"{'段':<14}{'侨居国主流份额':>12}{'侨居国核心读者率':>14}"
          f"{'母国主流份额':>12}{'母国核心读者率':>14}")
    for s in ("host_dom", "H", "D", "U", "home_dom"):
        print(f"{name[s]:<14}{h_share.get(s, 0):>12.1%}{h_core.get(s, 0):>14.1%}"
              f"{m_share.get(s, 0):>12.1%}{m_core.get(s, 0):>14.1%}")

    h_h = [b[1] for b in books if b[0] == "H"]
    h_m = [b[2] for b in books if b[0] == "H"]
    price_ratio = statistics.mean(h_h) / statistics.mean(h_m)

    # 供给侧: 新作者按"总期望收益+噪声"选题(套利方向)
    payoff = {th: W_HOST[th] * 0.50 + HOME_SCALE * W_HOME[th] * 0.50
              for th in "HDU"}
    supply = {th: 0 for th in "HDU"}
    for _ in range(N_NEWAUTH):
        best = max("HDU", key=lambda th: payoff[th] + rng.gauss(0, 0.08))
        supply[best] += 1
    h_supply = supply["H"] / N_NEWAUTH
    home_hits_h = round(m_share.get("H", 0) * (HIT_Q * len(home_pool)))
    home_share_h_smooth = (home_hits_h + 1) / (HIT_Q * len(home_pool) + 2)

    print(f"\n[3b] '回望母国'(H)的两本账: 侨居国接受指数均值 {statistics.mean(h_h):.3f}"
          f" vs 母国 {statistics.mean(h_m):.3f}(定价×{price_ratio:.2f});")
    print(f"      供给模拟: {N_NEWAUTH} 位新散居作者按市场理性选题, H 占 "
          f"{h_supply:.1%}(套利指向回望母国); 而母国主流榜 H 份额 "
          f"{m_share.get('H', 0):.1%}——供给与母国需求错位")
    print("读数: 散居作者写给两个市场,但两个市场各认各的账——侨居国买'异域',")
    print("      母国买'在场';写离别的书在他乡溢价,在故乡折价")

    assert h_core["D"] > 0.25 and m_core["D"] > 0.40, \
        "双家园作品应在两个市场各有核心读者"
    assert h_share["D"] < 0.12 and m_share["D"] < 0.15, \
        "双家园作品在两个市场均非主流"
    assert h_share["H"] > 0.25 and m_share["H"] < 0.05, \
        "H 应侨居国上榜、母国遇冷(异域溢价/母国冷淡)"
    assert price_ratio > 2.0, "同一本书在两个市场的接受指数应差 2 倍以上"
    assert h_supply > 0.50, "供给侧行为应把散居作者推向回望母国(套利)"
    assert h_supply / home_share_h_smooth > 10, \
        "供给套利份额与母国主流接纳应严重错位(>10 倍)"
    print(f"\n✓ 幕三断言通过: D 双市场各有核心读者(侨居 {h_core['D']:.0%}/母国 "
          f"{m_core['D']:.0%})而两榜均非主流({h_share['D']:.1%}/{m_share['D']:.1%});"
          f" H 侨居国榜 {h_share['H']:.0%} vs 母国榜 {m_share['H']:.1%},"
          f"定价×{price_ratio:.2f}——散居文学是两种乡愁之间的套利")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 歌线的地理记忆: '歌-地'绑定(双线索+锚点序列固定)逐项成功率与合格")
    print("     传诵率显著高于串行清单,且清单加长不衰减;分割地景仅割 5% 链位即令")
    print("     到达率塌到一成以下,碎片化比整块占用更伤——歌线是把大陆装进歌里的")
    print("     纠错码(冗余在链上,断链即弃权)")
    print("  ② 口传谱系的代际保真: 韵律与仪式的冗余校验使口传身份/顺序保真高,但")
    print("     可编辑性低(社群分布式否决拦假名);文本转录引入后认知卸载,末代保真")
    print("     反低于纯口传,静默编辑畅通——文字不仅记录传统,也解除了记忆的武装")
    print("  ③ 散居写作的双家园市场: 双家园作品两市场各有核心读者而均非主流;'回望")
    print("     母国'在侨居国有异域溢价、在母国遇冷,同一本书两种定价;市场理性把")
    print("     散居作者推向回望母国而母国不买账——散居文学是两种乡愁之间的套利")
    print("     (与东欧流亡双市场实验分工: 那边管政治流亡的回归,本家族管散居的无回归)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
