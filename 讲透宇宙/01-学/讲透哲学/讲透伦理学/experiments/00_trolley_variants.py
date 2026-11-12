# -*- coding: utf-8 -*-
"""电车困境变体发生器与「道德判断一致性」检查(00/03/04 章配套实验)。

模型声明(纪律声明,先读再用):
  - 本脚本的判断模型是**预设教学玩具**:基准率的量级取自道德心理学
    文献报告方向的粗简化——Foot 1967(电车难题原版)/Thomson 1976-1985
    (天桥/环路/移植医生)/Greene 2001 起 fMRI 双加工研究/豪泽等
    Moral Sense Test 网络大样本(扳道≈90% 许可、天桥≈10-20% 许可的
    经典落差)。它构造的是「直觉如何分布」的可检查假设,不是实测数据,
    不用于预测任何真人。
  - 人口统计学参数的修正项同样是玩具(方向取自文献常见报告方向:
    男性/年轻/伦理训练者对「许可伤害」略高,高宗教性略低等),
    量级为教学设定。换一组修正项,水平会变——断言的是「翻转模式」,
    不是具体数字。

断言五组(道德判断的可量化结构):
  A. 双重效应断崖:对**每一个**人口统计学单元,
     mean(副作用类:扳道/脚手架) - mean(手段类:天桥/移植医生) ≥ 0.40
     —— 断崖在人口扫描下不消失(00 章 §七发现 1 / 03 章 §一)。
  B. 翻转模式:对每个单元,脚手架(身体挡车/伤害为副作用)与
     天桥(身体挡车/伤害为手段)许可率差 ≥ 0.35——
     同样的身体、同样的 5↔1,直觉随「伤害角色」一字之差翻转。
  C. 序结构:每个单元内 扳道 > 脚手架 > 环路(骑墙) > 天桥 > 移植医生;
     环路作为 DDE 争议案稳定居中(03 章 §五三步法的「骑墙维度」)。
  D. 算术不解释判决:移植医生与扳道算术相同(杀 1 救 5),
     每个单元内 扳道 - 移植医生 ≥ 0.50——功利算术不是许可率的函数。
  E. 无关参数不变性 + 一致性检查器:非道德参数(轨道颜色/受害者姓名)
     不改变许可率;一致性检查器正确标出「准天桥却拒扳道」
     (DDE 序不一致)与「准救 5 却拒救 100」(数量单调性不一致)两类。

跑法: python experiments/00_trolley_variants.py
(纯标准库,零依赖;输出变体表 + 人口扫描报告 + 断言自验证)
"""

import itertools
import math

# ---------------------------------------------------------------- 经典变体(5)
# harm_role: "side_effect"(伤害为副作用) / "means"(伤害为手段);
# contested=True 表示其 DDE 分类本身在文献中有争议(环路)。
CLASSICS = [
    {"name": "扳道", "en": "switch", "action": "turn",
     "harm_role": "side_effect", "n_save": 5, "n_kill": 1,
     "note": "扳道岔引电车驶离五人;侧轨一人之死是副作用(若他不在更好)"},
    {"name": "脚手架", "en": "scaffold", "action": "turn",
     "harm_role": "side_effect", "n_save": 5, "n_kill": 1,
     "note": "人卡在侧轨上方脚手架;扳道后电车碰落脚手架致死,身躯挡车"},
    {"name": "环路", "en": "loop", "action": "turn",
     "harm_role": "means", "contested": True, "n_save": 5, "n_kill": 1,
     "note": "侧轨环回主线;侧轨一人之身躯是挡车的必要手段(DDE 争议案)"},
    {"name": "天桥", "en": "footbridge", "action": "push",
     "harm_role": "means", "n_save": 5, "n_kill": 1,
     "note": "推下天桥壮汉以其身躯挡车;其死是救人的手段"},
    {"name": "移植医生", "en": "transplant", "action": "harvest",
     "harm_role": "means", "n_save": 5, "n_kill": 1,
     "note": "摘一名健康人器官救五名垂死者;与扳道同算术(杀1救5)"},
]
BY_NAME = {v["name"]: v for v in CLASSICS}

# ---------------------------------------------------------------- 预设判断模型
# 基准许可率(教学玩具,量级锚见模块 docstring)
BASE = {
    ("turn", "side_effect", "switch"): 0.88,
    ("turn", "side_effect", "scaffold"): 0.74,
    ("turn", "means", "loop"): 0.55,        # 骑墙:低于扳道高于天桥
    ("push", "means", "footbridge"): 0.18,
    ("harvest", "means", "transplant"): 0.07,
}

# 人口统计学单元的修正项(方向取自文献常见报告方向,量级为教学设定)
GENDERS = ["male", "female"]
AGES = ["young", "mid", "senior"]
TRAININGS = [True, False]           # 是否受过伦理学训练
RELIGIOSITIES = ["high", "low"]
CULTURES = ["WEIRD", "east_asian"]  # 粗二分,声明见 docstring


def adjustment(cell, harm_role):
    """一个人口单元对「许可伤害」判断的加性修正。"""
    a = 0.0
    if cell["gender"] == "male":
        a += 0.03
    if cell["age"] == "young":
        a += 0.02
    elif cell["age"] == "senior":
        a -= 0.02
    if cell["training"]:
        a += 0.04
        if harm_role == "means":    # 训练对「手段类伤害」的上移略多
            a += 0.04
    if cell["religiosity"] == "high":
        a -= 0.04
    if cell["culture"] == "east_asian":
        a += 0.02 if harm_role == "side_effect" else -0.03
    return a


def permit(variant, cell):
    """预设许可率 = 基准 + 数量梯度(log) + 人口修正,截断到 [0.02, 0.98]。
    注意:只读道德相关维度(行动/伤害角色/人数);轨道颜色、姓名等
    非道德维度被模型结构性忽略(断言 E-1 的可检验性由此而来)。"""
    key = (variant["action"], variant["harm_role"], variant["en"])
    base = BASE.get(key, 0.80 if variant["harm_role"] == "side_effect" else 0.20)
    n_save = variant.get("n_save", 5)
    numbers_bonus = 0.05 * math.log10(max(n_save, 1) / 5.0)  # 救越多越许可,弱梯度
    p = base + numbers_bonus + adjustment(cell, variant["harm_role"])
    return min(0.98, max(0.02, p))


def all_cells():
    keys = ["gender", "age", "training", "religiosity", "culture"]
    for combo in itertools.product(GENDERS, AGES, TRAININGS, RELIGIOSITIES, CULTURES):
        yield dict(zip(keys, combo))


BASELINE = {"gender": "female", "age": "mid", "training": False,
            "religiosity": "low", "culture": "WEIRD"}

SIDE_EFFECT = [v["name"] for v in CLASSICS if v["harm_role"] == "side_effect"]
MEANS_SOLID = ["天桥", "移植医生"]                      # 环路(contested)不入断言
ORDER = ["扳道", "脚手架", "环路", "天桥", "移植医生"]   # 断言 C 的全序


# ---------------------------------------------------------------- 变体发生器
def generate_variants(n_save_list=(1, 3, 5, 10, 30, 100)):
    """行动×伤害角色×交换比 的笛卡尔积枚举(过滤平凡组合),供走廊 1 使用。"""
    out = []
    for action, role, n_save in itertools.product(
            ("turn", "push", "harvest"), ("side_effect", "means"), n_save_list):
        if n_save < 2:               # 杀 1 救 1 无道德张力,过滤
            continue
        en = {"turn": "gen-turn", "push": "gen-push", "harvest": "gen-harvest"}[action]
        out.append({"name": f"生成:{action}/{role}/救{n_save}", "en": en,
                    "action": action, "harm_role": role,
                    "n_save": n_save, "n_kill": 1})
    return out


# ---------------------------------------------------------------- 一致性检查器
def consistency_flags(judgments):
    """给定个人判断向量 {变体名: bool(准许?)},标出 DDE 序不一致:
    准许某手段类(天桥/移植医生)却拒绝同算术的副作用类(扳道)——
    更强的许可(把人当手段)没有理由伴随更弱的拒绝(纯副作用)。
    数量单调性不一致由 numbers_flags 独立检查(准救 5 却拒救 100)。"""
    flags = []
    if judgments.get("天桥") and not judgments.get("扳道"):
        flags.append("DDE序不一致: 准天桥(手段)却拒扳道(副作用)")
    if judgments.get("移植医生") and not judgments.get("扳道"):
        flags.append("DDE序不一致: 准移植(手段)却拒扳道(副作用)")
    return flags


def numbers_flags(permit_small, permit_large):
    """数量单调性检查(独立小工具):准救 5 却拒救 100 → 不一致。"""
    return permit_small and not permit_large


# ---------------------------------------------------------------- 报告与断言
def main():
    print("=" * 76)
    print("电车困境变体发生器与道德判断一致性检查(预设教学玩具,见头部声明)")
    print("=" * 76)

    print("\n【一】五个经典变体 × 基准单元(%s)" % ", ".join(
        f"{k}={v}" for k, v in BASELINE.items()))
    print(f"{'变体':<8}{'角色':<12}{'算术':<8}{'许可率':>7}  说明")
    for v in CLASSICS:
        p = permit(v, BASELINE)
        print(f"{v['name']:<8}{v['harm_role']:<12}{'%d↔%d' % (v['n_save'], v['n_kill']):<8}"
              f"{p:>7.2f}  {v['note']}")

    # ---- 断言 A/B/C/D:人口统计学全扫描(48 单元) ----
    print("\n【二】人口统计学扫描(%d 单元 = 性别×年龄×训练×宗教×文化)"
          % (2 * 3 * 2 * 2 * 2))
    min_gap, gap_cell = 9.9, None
    min_flip, flip_cell = 9.9, None
    for cell in all_cells():
        ps = {v["name"]: permit(v, cell) for v in CLASSICS}
        top = sum(ps[n] for n in SIDE_EFFECT) / len(SIDE_EFFECT)
        bottom = sum(ps[n] for n in MEANS_SOLID) / len(MEANS_SOLID)
        gap = top - bottom
        if gap < min_gap:
            min_gap, gap_cell = gap, cell
        flip = ps["脚手架"] - ps["天桥"]
        if flip < min_flip:
            min_flip, flip_cell = flip, cell
        # 断言 A:双重效应断崖(每单元)
        assert gap >= 0.40, f"断崖消失于 {cell}: gap={gap:.2f}"
        # 断言 B:翻转模式(每单元)
        assert flip >= 0.35, f"翻转消失于 {cell}: flip={flip:.2f}"
        # 断言 C:全序结构(每单元)
        order_ps = [ps[n] for n in ORDER]
        assert order_ps == sorted(order_ps, reverse=True), \
            f"序破坏于 {cell}: {[(n, round(ps[n], 2)) for n in ORDER]}"
        # 断言 D:算术不解释判决(每单元;移植医生与扳道同算术)
        assert ps["扳道"] - ps["移植医生"] >= 0.50, \
            f"移植悖论消失于 {cell}: {ps['扳道'] - ps['移植医生']:.2f}"
    print(f"  断崖(副作用均值-手段均值):最小 {min_gap:.2f} @ {gap_cell}——断言 A ≥0.40 通过")
    print(f"  翻转(脚手架-天桥):      最小 {min_flip:.2f} @ {flip_cell}——断言 B ≥0.35 通过")
    print("  序结构 扳道>脚手架>环路>天桥>移植医生:48 单元全部保持——断言 C 通过")
    print("  扳道-移植医生(同算术杀1救5):48 单元全部 ≥0.50——断言 D 通过")
    print("  读数:人口参数移动「水平」(许可率高低),但不移动「断崖与序」——")
    print("        这正是「普遍道德语法」主张的最小玩具证据(03 章 §一)。")

    # ---- 断言 E-1:无关参数不变性 ----
    print("\n【三】无关参数不变性与变体发生器")
    neutral = {"name": "生成:turn/side_effect/救5", "en": "gen-turn",
               "action": "turn", "harm_role": "side_effect", "n_save": 5, "n_kill": 1}
    for extra in ({"track_color": "red", "victim_name": "张三"},
                  {"track_color": "blue", "victim_name": "李四"}):
        v = dict(neutral, **extra)
        assert permit(v, BASELINE) == permit(neutral, BASELINE), \
            "非道德参数不应改变许可率(模型必须结构性忽略颜色/姓名)"
    print("  无关参数(轨道颜色/受害者姓名)不改变许可率——断言 E-1 通过:")
    print("        直觉系统对道德相关变量有选择性;评测集设计据此筛掉噪声维度。")

    variants = generate_variants()
    n_side = sum(1 for v in variants if v["harm_role"] == "side_effect")
    n_means = len(variants) - n_side
    print(f"  发生器:行动(3)×角色(2)×交换比(6)-过滤 = {len(variants)} 个变体"
          f"(副作用类 {n_side} / 手段类 {n_means})")
    # 生成空间内同算术对照:同 n_save 下副作用类 > 手段类(断崖的生成版)
    for n_save in (5, 100):
        side_p = max(permit(v, BASELINE) for v in variants
                     if v["harm_role"] == "side_effect" and v["n_save"] == n_save)
        means_p = max(permit(v, BASELINE) for v in variants
                      if v["harm_role"] == "means" and v["n_save"] == n_save)
        assert side_p - means_p >= 0.30, \
            f"生成空间断崖(n_save={n_save}): {side_p - means_p:.2f}"
    p5 = permit(dict(neutral), BASELINE)
    p100 = permit(dict(neutral, n_save=100), BASELINE)
    print(f"  数量梯度:副作用类救5={p5:.2f} → 救100={p100:.2f}(弱梯度、不压平断崖)")

    # ---- 断言 E-2:一致性检查器 ----
    print("\n【四】一致性检查器(对个人判断向量)")
    cases = [
        ("全准许(铁杆功利)", {n: True for n in ORDER}, 0),
        ("经典 DDE 型(准扳道拒天桥)", {"扳道": True, "脚手架": True, "环路": True,
                                       "天桥": False, "移植医生": False}, 0),
        ("准天桥却拒扳道", {"扳道": False, "脚手架": False, "环路": False,
                             "天桥": True, "移植医生": False}, 1),
        ("准移植却拒扳道", {"扳道": False, "脚手架": True, "环路": False,
                             "天桥": False, "移植医生": True}, 1),
    ]
    for label, vec, expect_n in cases:
        flags = consistency_flags(vec)
        mark = "✓" if len(flags) == expect_n else "✗"
        print(f"  {mark} {label:<22} → 旗帜 {len(flags)} 个 {'/'.join(flags) or '(无)'}")
        assert len(flags) == expect_n, f"检查器误判: {label}"
    assert numbers_flags(True, False) and not numbers_flags(False, False) \
        and not numbers_flags(True, True), "数量单调性检查器行为不符"
    print("  ✓ 数量单调性:准救5却拒救100 → 标记;其余组合不误报")
    print("  读数:检查器不裁决『谁对』,只标出判断向量内部的序裂缝——")
    print("        对齐规格文档该写清楚的,正是每个人自己那条裂缝所在的维度。")

    print("\n全部断言通过:双重效应断崖跨人口稳定;同算术可反判决;")
    print("直觉对道德维度选择性敏感;序不一致可被检查器定位。")
    print("重申:预设模型是教学玩具——量级锚文献方向,断言的是翻转模式不是数字。")


if __name__ == "__main__":
    main()
