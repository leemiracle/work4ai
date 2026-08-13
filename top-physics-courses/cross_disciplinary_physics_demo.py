"""
物理学跨学科双螺旋 · 可视化 demo
==================================
配套文档：../../top-physics-courses/PHYSICS_CROSS_DISCIPLINARY.md

本文件用 ASCII 可视化展示：
  §1 物理 → 其他学科的辐射图谱（8 条主线 + 影响力）
  §2 其他学科 → 物理的反向启发（6 条主线）
  §3 7 大跨学科组合性价比矩阵（量化）
  §4 跨学科"啊哈时刻"时间线（戏剧性瞬间）

运行：
    python3 cross_disciplinary_physics_demo.py
"""
from __future__ import annotations
import sys
from dataclasses import dataclass

SEP = "=" * 76
SUBSEP = "-" * 76


# ============================================================================
# §1 物理 → 其他学科辐射图谱
# ============================================================================

@dataclass
class Influence:
    target: str          # 目标学科
    direction: str       # 物理学贡献了什么
    story: str           # 真实案例
    impact: int          # 影响力 1-5
    year: int            # 关键年份
    nobel: str = ""      # 是否获得诺奖（哪个领域）

PHYSICS_OUT = [
    Influence("化学",    "量子力学 → 化学键本质",            "泡林《化学键的本质》, DFT 量子化学",      5, 1927, "1998 化学"),
    Influence("生物",    "X射线衍射 + 薛定谔《生命是什么》", "Crick读薛定谔转行→DNA双螺旋",            5, 1944, "1962 医学"),
    Influence("计算机",  "量子力学 → 量子计算",              "费曼1981: '用quantum模拟quantum'",      5, 1981, ""),
    Influence("AI/ML",   "统计力学 → 神经网络",              "Hopfield自旋玻璃→神经网络",              5, 1982, "2024 物理"),
    Influence("信息论",  "玻尔兹曼熵 ↔ 信息熵",              "Shannon熵 = 玻尔兹曼熵; Landauer原理",   5, 1948, ""),
    Influence("金融",    "布朗运动 → 期权定价",              "Black-Scholes公式",                     4, 1973, "1997 经济"),
    Influence("工程",    "量子力学 → 半导体/激光",           "晶体管, 激光, MRI, 量子比特",            5, 1947, "1956 物理"),
    Influence("数学",    "弦理论 → 镜像对称",                "物理启发数学家拿Fields Medal",          4, 1990, "1990 Fields"),
    Influence("哲学",    "量子测量 → 心灵哲学",              "薛定谔猫, 多世界, 决定论",               3, 1935, ""),
]


def demo_physics_out():
    print(f"\n{SEP}")
    print("§1 物理学深刻启发了谁？（物理 → X 辐射图谱）")
    print(SEP)
    print("物理学不只是'自己的学科'，它是现代科学的源头活水。\n")

    # 按影响力排序
    sorted_inf = sorted(PHYSICS_OUT, key=lambda x: -x.impact)
    print(f"  {'目标学科':<10} {'影响力':<8} {'年份':<6} {'物理学贡献了什么':<28} {'真实案例'}")
    print(f"  {SUBSEP}")
    for inf in sorted_inf:
        stars = "⭐" * inf.impact
        nobel_tag = f" [{inf.nobel}]" if inf.nobel else ""
        print(f"  {inf.target:<10} {stars:<8} {inf.year:<6} {inf.direction:<28} {inf.story}{nobel_tag}")

    # 总影响力统计
    print(f"\n  ▶ 影响力分布")
    for impact in range(5, 0, -1):
        count = sum(1 for i in PHYSICS_OUT if i.impact == impact)
        if count:
            bar = "█" * count * 3
            print(f"  {'⭐'*impact:<6} {bar} {count} 个领域")

    print(f"\n  💡 核心规律：")
    print(f"     • 物理学是'方法论学科'——它的工具（量子/统计/对称性）适用于任何复杂系统")
    print(f"     • 5 颗⭐的领域（化学/生物/AI/信息论/工程）都因物理学的数学工具而革命")
    print(f"     • 2024 诺奖给 Hopfield/Hinton 是物理学的'回归'——神经网络的根在统计力学")


# ============================================================================
# §2 其他学科 → 物理反向启发
# ============================================================================

X_TO_PHYSICS = [
    Influence("数学",    "黎曼几何 → 广义相对论",            "爱因斯坦求助格罗斯曼学几何",            5, 1912, ""),
    Influence("数学",    "群论 → 标准模型",                  "盖尔曼用SU(3)群预言Ω⁻粒子",          5, 1961, ""),
    Influence("数学",    "拓扑 → 量子霍尔/拓扑相",            "Thouless用陈数解释量子化",            5, 1980, "2016 物理"),
    Influence("生物",    "光合作用 → 量子生物学",            "Fleming发现细菌利用量子相干",         4, 2007, ""),
    Influence("信息论",  "信息熵 → 黑洞熵/It from Qubit",    "Bekenstein把信息塞进黑洞",            5, 1973, ""),
    Influence("哲学",    "马赫实证主义 → 爱因斯坦相对论",     "马赫让爱因斯坦质疑绝对时间",          4, 1905, ""),
    Influence("化学",    "化学键 → 量子化学反馈物理",        "Marcus电子转移理论",                 3, 1992, "1992 化学"),
    Influence("经济",    "复杂系统 → 经济物理学",            "Bouchaud用相变解释市场崩溃",          3, 1998, ""),
]


def demo_x_to_physics():
    print(f"\n{SEP}")
    print("§2 谁深刻启发了物理？（X → 物理 反向启发图谱）")
    print(SEP)
    print("物理学也从来不孤立——它从其他学科汲取了大量灵感。\n")

    sorted_inf = sorted(X_TO_PHYSICS, key=lambda x: -x.impact)
    print(f"  {'来源学科':<10} {'影响力':<8} {'年份':<6} {'启发了什么物理突破':<28} {'真实故事'}")
    print(f"  {SUBSEP}")
    for inf in sorted_inf:
        stars = "⭐" * inf.impact
        nobel_tag = f" [{inf.nobel}]" if inf.nobel else ""
        print(f"  {inf.target:<10} {stars:<8} {inf.year:<6} {inf.direction:<28} {inf.story}{nobel_tag}")

    # 学科频率统计
    print(f"\n  ▶ 启发物理的学科频率统计")
    source_counts = {}
    for inf in X_TO_PHYSICS:
        source_counts[inf.target] = source_counts.get(inf.target, 0) + 1
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count * 3
        print(f"  {source:<8} {bar} {count} 次")

    print(f"\n  💡 核心规律：")
    print(f"     • 数学是物理学最大的输入源（黎曼/群论/拓扑都开启了物理革命）")
    print(f"     • 信息论是新兴的输入源（黑洞信息/It from Qubit）")
    print(f"     • 生物/经济正在成为新输入源（量子生物学/经济物理）")


# ============================================================================
# §3 7 大跨学科组合性价比矩阵
# ============================================================================

@dataclass
class Combo:
    name: str
    learn_months: int    # 学习月数
    impact: int          # 产出影响力 1-5
    prob: int            # 成功概率 1-5
    case: str
    path: str            # 入场路径

    @property
    def cost(self) -> float:
        """学习成本 = 月数（最小 0.5，避免除零；持续阅读按 1 月折算）"""
        return max(self.learn_months, 0.5)

    @property
    def roi(self) -> float:
        """性价比 = 影响力 × 概率 / 成本"""
        return (self.impact * self.prob) / self.cost * 10

COMBOS = [
    Combo("物理+ML",        6, 5, 5, "AlphaFold/GNoME/PINN/2024诺奖", "学CS231N+读AlphaFold"),
    Combo("物理+信息论",    3, 4, 5, "Bekenstein黑洞熵/It from Qubit", "读MacKay《信息论》"),
    Combo("物理+生物",     12, 4, 4, "薛定谔→DNA, 冷冻电镜, 量子生物",  "学Nelson《生物物理》"),
    Combo("物理+金融",      6, 3, 4, "Black-Scholes, Renaissance Tech", "学随机过程+期权"),
    Combo("物理+数学",     24, 5, 3, "黎曼→GR, 拓扑→量子霍尔, 群论",    "学一个数学分支"),
    Combo("物理+化学",      6, 4, 5, "DFT, Marcus理论, 量子化学",        "学量子化学"),
    Combo("物理+哲学",      0, 3, 5, "马赫→爱因斯坦, 测量问题",          "读库恩/费曼"),
]


def demo_roi_matrix():
    print(f"\n{SEP}")
    print("§3 7 大跨学科组合性价比矩阵（量化排行）")
    print(SEP)
    print("性价比 = 影响力 × 成功概率 / 学习成本\n")

    # 按性价比排序
    sorted_combos = sorted(COMBOS, key=lambda c: -c.roi)

    print(f"  {'排名':<4} {'组合':<14} {'学习成本':<10} {'影响力':<8} {'概率':<6} {'性价比':<10} {'代表案例'}")
    print(f"  {SUBSEP}")
    medals = ["🥇", "🥈", "🥉", "4", "5", "6", "7"]
    for i, combo in enumerate(sorted_combos):
        medal = medals[i] if i < len(medals) else str(i+1)
        cost_str = f"{combo.learn_months}月" if combo.learn_months > 0 else "持续"
        impact_stars = "⭐" * combo.impact
        prob_pct = f"{combo.prob*20}%"
        roi_str = f"{combo.roi:.1f}"
        print(f"  {medal:<3} {combo.name:<14} {cost_str:<10} {impact_stars:<8} {prob_pct:<6} {roi_str:<10} {combo.case}")

    # 性价比可视化
    print(f"\n  ▶ 性价比条形图\n")
    max_roi = max(c.roi for c in sorted_combos)
    for combo in sorted_combos:
        bar_len = int(combo.roi / max_roi * 40)
        bar = "█" * bar_len
        print(f"  {combo.name:<14} {bar} {combo.roi:.1f}")

    print(f"\n  💡 性价比之王：")
    print(f"     🥇 物理+ML：6 个月学 ML，可能开新方向（AlphaFold 已经证明）")
    print(f"     🥈 物理+信息论：3 个月学 Shannon，通往黑洞信息/量子计算")
    print(f"     🥉 物理+生物：1 年学生物，通往生物物理/量子生物学")
    print(f"\n  ⚠️ 物理+数学门槛最高（2 年）但天花板最高——所有物理革命几乎都伴随新数学")


# ============================================================================
# §4 跨学科"啊哈时刻"时间线
# ============================================================================

@dataclass
class AhaMoment:
    year: int
    who: str
    scene: str         # 场景
    insight: str       # 啊哈
    consequence: str   # 后果

AHA_MOMENTS = [
    AhaMoment(1907, "爱因斯坦",   "专利局办公桌前",
              "自由下落的人感觉不到引力——引力和加速等效！",
              "8 年后 → 广义相对论"),
    AhaMoment(1943, "薛定谔",     "都柏林三一学院演讲",
              "生命靠读取信息对抗熵增——'负熵'！",
              "Crick 读后转生物 → DNA 双螺旋"),
    AhaMoment(1948, "Shannon",    "贝尔实验室写信息熵公式",
              "H=-Σp log p 和玻尔兹曼熵一模一样！",
              "信息 = 物理 → Landauer → 黑洞信息"),
    AhaMoment(1972, "Bekenstein", "普林斯顿博士生办公室",
              "黑洞吃掉信息必须增加熵！熵 ∝ 视界面积？",
              "Hawking 反驳反而发现霍金辐射"),
    AhaMoment(1980, "Hopfield",   "加州理工办公室深夜盯自旋玻璃方程",
              "E=-ΣJ s_i s_j 不就是大脑吗？自旋=神经元！",
              "Hopfield 网络 → 深度学习 → 2024 诺奖"),
    AhaMoment(1981, "Feynman",    "MIT 第一届物理与计算会议",
              "经典计算机模拟量子太慢——让计算机本身是量子的！",
              "40 年后 Google Willow 量子优越性"),
    AhaMoment(2007, "Fleming",    "Berkeley 实验室看光合细菌光谱",
              "细菌利用量子相干传输激发能！",
              "量子生物学诞生"),
    AhaMoment(2010, "van Raamsdonk", "写论文时推演",
              "减少量子纠缠 → 时空几何消失！没有纠缠就没有时空",
              "It from Qubit → 量子引力新方向"),
]


def demo_aha_timeline():
    print(f"\n{SEP}")
    print("§4 跨学科的「啊哈时刻」时间线（1907-2010）")
    print(SEP)
    print("真实人物在真实场景下的戏剧性跨界瞬间。\n")

    for i, moment in enumerate(AHA_MOMENTS, 1):
        print(f"  🎬 [{i}] {moment.year} · {moment.who}")
        print(f"      场景：{moment.scene}")
        print(f"      💡 {moment.insight}")
        print(f"      → {moment.consequence}")
        print()

    # 按年代分布
    print(f"  ▶ 啊哈时刻的年代分布\n")
    decades = {}
    for m in AHA_MOMENTS:
        decade = (m.year // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1
    for decade in sorted(decades):
        count = decades[decade]
        bar = "★" * count
        print(f"  {decade}s  {bar} {count} 个")

    print(f"\n  💡 规律：啊哈时刻在 1940s 和 1970-80s 最密集")
    print(f"     1940s: 信息论诞生期（Shannon/薛定谔）")
    print(f"     1970-80s: 跨学科爆发期（Bekenstein/Hopfield/Feynman）")
    print(f"     2000s+: 信息-物理融合（Fleming/van Raamsdonk）")


# ============================================================================
# §5 你的跨学科方向选择器
# ============================================================================

def demo_choose_your_path():
    print(f"\n{SEP}")
    print("§5 你的跨学科方向选择器")
    print(SEP)
    print("根据你的强项/目标/时间，推荐最佳跨学科组合。\n")

    # 按"强项"分析
    print(f"  ▶ 按你的强项推荐\n")
    print(f"  {'你的强项':<12} {'推荐组合':<20} {'为什么':<36} {'入场路径'}")
    print(f"  {SUBSEP}")
    strengths = [
        ("数学好",   "物理+数学/ML",  "数学是物理和ML的共同基础",         "学拓扑/群论或PyTorch"),
        ("编程好",   "物理+量子计算",  "编程能力直接转化为量子算法",        "学量子力学+Qiskit"),
        ("实验好",   "物理+生物",      "实验技能在生物物理极有价值",        "学冷冻电镜/光谱"),
        ("写作好",   "物理+哲学/经济", "表达能力让跨学科传播更远",          "写跨学科论文/科普"),
        ("直觉好",   "物理+信息论",    "信息论直觉通向黑洞/量子计算",       "读MacKay《信息论》"),
    ]
    for strength, combo, why, path in strengths:
        print(f"  {strength:<12} {combo:<20} {why:<36} {path}")

    # 按"目标"分析
    print(f"\n  ▶ 按你的目标推荐\n")
    print(f"  {'你的目标':<16} {'推荐组合':<20} {'代表案例'}")
    print(f"  {SUBSEP}")
    goals = [
        ("理解宇宙",     "物理+数学/信息论",  "爱因斯坦/Bekenstein 路径"),
        ("做有用的事",   "物理+ML/生物",      "AlphaFold/GNoME 路径"),
        ("赚大钱",       "物理+金融",         "Renaissance Tech/Simons 路径"),
        ("思考深刻",     "物理+哲学",         "马赫/费曼路径"),
        ("开创新方向",   "物理+拓扑/信息",    "Thouless/Bekenstein 路径"),
    ]
    for goal, combo, case in goals:
        print(f"  {goal:<16} {combo:<20} {case}")

    # 按"时间预算"分析
    print(f"\n  ▶ 按你的时间预算推荐\n")
    time_budgets = [
        ("3 个月",  "物理+信息论",   "读 MacKay + 思考黑洞信息"),
        ("6 个月",  "物理+ML",       "学 CS231N + 做一个 PINN 项目"),
        ("1 年",    "物理+生物",     "学 Nelson + 进实验室"),
        ("2 年+",   "物理+数学",     "学黎曼几何/拓扑 → 找物理应用"),
        ("持续",    "物理+哲学",     "碎片时间读库恩/费曼"),
    ]
    print(f"  {'时间':<10} {'推荐组合':<16} {'怎么开始'}")
    print(f"  {SUBSEP}")
    for time, combo, how in time_budgets:
        print(f"  {time:<10} {combo:<16} {how}")

    print(f"\n  💡 终极建议：选择你'最想学'的领域，而不是'最该学'的。")
    print(f"     跨学科突破需要长期投入——只有热情能让你坚持。")
    print(f"     Hopfield 研究自旋玻璃不是因为'应该'，是因为他觉得有意思。")


# ============================================================================
# 主入口
# ============================================================================

DEMOS = {
    1: ("物理→X 辐射图谱",       demo_physics_out),
    2: ("X→物理 反向启发",       demo_x_to_physics),
    3: ("跨学科性价比矩阵",      demo_roi_matrix),
    4: ("啊哈时刻时间线",        demo_aha_timeline),
    5: ("跨学科方向选择器",      demo_choose_your_path),
}


def main():
    print("╔" + "═" * 74 + "╗")
    print("║" + " 物理学跨学科双螺旋 · 可视化 demo ".center(74) + "║")
    print("║" + " 配套：top-physics-courses/PHYSICS_CROSS_DISCIPLINARY.md ".center(74) + "║")
    print("╚" + "═" * 74 + "╝")

    args = sys.argv[1:]
    selected = sorted({int(a) for a in args if a.isdigit()}) if args else list(DEMOS.keys())

    for n in selected:
        if n in DEMOS:
            name, fn = DEMOS[n]
            print(f"\n\n▶▶▶ §{n} {name} ▶▶▶")
            try:
                fn()
            except Exception as e:
                import traceback
                print(f"  [!] §{n} 出错：{e}")
                traceback.print_exc()

    print(f"\n{SEP}")
    print("🎯 跨学科突破的核心规律：")
    print("   1. 物理→ML 和 物理→信息论 是性价比之王")
    print("   2. 数学是物理学最大的输入源（黎曼/群论/拓扑）")
    print("   3. 跨学科突破 = 在两个领域看到同一个数学结构")
    print("   4. 选择你'最想学'的领域，热情是最大的资本")
    print(SEP)
    print("📚 完整文档：PHYSICS_CROSS_DISCIPLINARY.md（同目录）")


if __name__ == "__main__":
    main()
