"""
物理学突破方法论 · 可视化 demo
================================
配套文档：../../top-physics-courses/PHYSICS_BREAKTHROUGHS.md

本文件用 ASCII 可视化展示：
  §1 突破的 7 大模式（历史案例时间线）
  §2 每个分支的"瓶颈→突破→当前危机"链条
  §3 突破的"反向信号"诊断器（你的研究是否有突破迹象？）
  §4 未来 10 年突破预测

运行：
    python3 physics_breakthroughs_demo.py
"""
from __future__ import annotations
import sys
import math
from dataclasses import dataclass
from typing import List, Tuple

SEP = "=" * 76
SUBSEP = "-" * 76


# ============================================================================
# §1 突破的 7 大模式（时间线可视化）
# ============================================================================

@dataclass
class Breakthrough:
    year: int
    who: str
    what: str
    pattern: str   # 7 大模式之一
    impact: str

BREAKTHROUGHS = [
    Breakthrough(1687, "牛顿",      "万有引力定律（苹果+月亮统一）",     "统一",      "经典力学框架"),
    Breakthrough(1865, "麦克斯韦",  "电+磁+光统一",                   "统一",      "电磁理论"),
    Breakthrough(1887, "迈克尔逊-莫雷", "找不到以太",                  "实验反常",   "→ 相对论"),
    Breakthrough(1900, "普朗克",    "黑体辐射量子化",                 "实验反常",   "→ 量子力学"),
    Breakthrough(1905, "爱因斯坦",  "推翻绝对时间 + E=mc²",            "推翻假设",   "狭义相对论"),
    Breakthrough(1907, "爱因斯坦",  "电梯思想实验 → 等效原理",         "思想实验",   "→ 广义相对论"),
    Breakthrough(1925, "海森堡",    "矩阵力学（推翻确定轨迹）",        "推翻假设",   "量子力学"),
    Breakthrough(1928, "狄拉克",    "狄拉克方程（预言反物质）",        "数学新工具", "→ QED"),
    Breakthrough(1948, "费曼",      "路径积分（新数学框架）",          "数学新工具", "→ QFT"),
    Breakthrough(1964, "贝尔",      "贝尔不等式（推翻局域实在论）",     "推翻假设",   "→ 2022 诺奖"),
    Breakthrough(1967, "温伯格等",  "电弱统一",                       "统一",      "标准模型"),
    Breakthrough(1972, "安德森",    "More Is Different（粒子→凝聚态）", "跨学科",    "凝聚态独立"),
    Breakthrough(1982, "Hopfield",  "统计力学→神经网络",               "跨学科",    "→ 2024 诺奖"),
    Breakthrough(1997, "Maldacena", "AdS-CFT 对偶（弦→凝聚态）",       "跨学科",    "全息原理"),
    Breakthrough(2012, "CERN LHC",  "发现希格斯玻色子",               "新工具",    "标准模型完成"),
    Breakthrough(2015, "LIGO",      "首次探测引力波",                 "新工具",    "引力波天文学"),
    Breakthrough(2022, "JWST",      "早期宇宙星系（挑战ΛCDM）",        "新工具",    "→ 宇宙学危机"),
    Breakthrough(2024, "Google",    "Willow 量子纠错盈亏平衡",         "新工具",    "→ 容错量子计算"),
]


def demo_seven_patterns():
    print(f"\n{SEP}")
    print("§1 物理学突破的 7 大模式 · 历史时间线（1687-2024）")
    print(SEP)
    print("核心洞见：突破 ≠ 在同一框架里更努力；突破 = 换框架")
    print()

    # 按 7 大模式分组统计
    pattern_counts = {}
    for b in BREAKTHROUGHS:
        pattern_counts[b.pattern] = pattern_counts.get(b.pattern, 0) + 1

    print("  7 大模式的历史出现频率：\n")
    print(f"  {'模式':<14} {'次数':>4}  代表案例")
    print(f"  {SUBSEP}")
    examples = {
        "统一": "牛顿引力 / 麦克斯韦电磁 / 电弱统一",
        "实验反常": "迈克尔逊-莫雷 / 黑体辐射 / μ子g-2",
        "数学新工具": "牛顿微积分 / 费曼路径积分 / 群论",
        "思想实验": "爱因斯坦电梯 / EPR / 薛定谔猫",
        "推翻假设": "绝对时间 / 确定轨迹 / 局域实在论",
        "跨学科": "安德森 / Hopfield / AdS-CFT",
        "新工具": "望远镜 / LHC / LIGO / JWST",
    }
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"  {pattern:<14} {count:>4}  {examples.get(pattern, '')}")

    # 时间线 ASCII
    print(f"\n  ▶ 突破时间线（每年一格）\n")
    min_year, max_year = 1680, 2030
    width = 70
    def year_to_x(y):
        return int((y - min_year) / (max_year - min_year) * width)

    timeline = [' '] * (width + 1)
    labels = []
    for b in BREAKTHROUGHS:
        x = year_to_x(b.year)
        timeline[x] = '★'
        labels.append((x, b.year, b.who, b.pattern))

    print(f"  {min_year}" + "─" * (width - 10) + f"{max_year}")
    print(f"  |{''.join(timeline)}|")
    print()
    # 显示前 8 个标注
    for x, year, who, pattern in labels[:12]:
        padding = " " * (x + 2)
        print(f"  {padding}↑ {year} {who} [{pattern}]")

    print(f"\n  💡 模式分布显示：")
    print(f"     • '推翻假设' 和 '新工具' 是最常见的突破模式")
    print(f"     • '跨学科' 模式在 1970 年后崛起（凝聚态/AI/量子信息）")
    print(f"     • '统一' 模式罕见但影响最大（牛顿/麦克斯韦/爱因斯坦）")


# ============================================================================
# §2 每个分支的瓶颈→突破→危机链条
# ============================================================================

def demo_branch_crises():
    print(f"\n{SEP}")
    print("§2 每个分支的「瓶颈 → 突破 → 当前危机」链条")
    print(SEP)
    print()

    branches = [
        ("经典力学",   "三体不可解(1887)",
         "KAM定理(1954)证明近可积系统稳定",
         "湍流（Navier-Stokes 千禧难题）",
         "AI/ML闭包(2024+)"),
        ("电磁学",     "四个碎片定律不统一",
         "麦克斯韦方程组(1865)统一电+磁+光",
         "磁单极从未发现",
         "超材料/拓扑光子学"),
        ("统计力学",   "宏观可逆 vs 微观不可逆",
         "玻尔兹曼 S=k ln W (1877)",
         "非平衡/生命/玻璃态无统一框架",
         "随机热力学+AI热力学计算机"),
        ("量子力学",   "原子不稳定（经典预言电子坠入核）",
         "矩阵力学+波动力学+路径积分",
         "测量问题/诠释（至今无共识）",
         "量子信息理论→It from Qubit"),
        ("广义相对论", "狭义相对论不含引力",
         "等效原理(1907)→场方程(1915)",
         "量子引力（弦/圈/AdS-CFT都未验证）",
         "AdS-CFT/岛屿公式"),
        ("标准模型",   "量子+相对论不兼容",
         "QED→标准模型→希格斯(2012)",
         "含不了引力；中微子质量；CP破坏不够",
         "暗sector/长寿命粒子/μ子g-2"),
        ("凝聚态",     "10²³ 粒子怎么办？",
         "BCS(1957)+More Is Different(1972)+拓扑相",
         "高温超导机制不明（铜基40年无共识）",
         "量子模拟器解Hubbard模型"),
        ("宇宙学",     "宇宙是永恒不变的？",
         "哈勃膨胀→CMB→暴胀→加速膨胀",
         "暗物质(27%)+暗能量(68%)本质未知",
         "DESI/Euclid/JWST可能推翻ΛCDM"),
    ]

    for name, crisis, breakthrough, current, future in branches:
        print(f"  📦 {name}")
        print(f"     历史瓶颈  → {crisis}")
        print(f"     历史突破  → {breakthrough}")
        print(f"     当前危机  → {current}")
        print(f"     可能突破  → {future}")
        print()

    print(f"  💡 核心规律：每个突破都解决了上一代危机，但留下新的更深危机。")
    print(f"     物理学是'解决→新危机→再解决'的无尽长跑。")


# ============================================================================
# §3 突破的"反向信号"诊断器
# ============================================================================

def demo_breakthrough_signals():
    print(f"\n{SEP}")
    print("§3 突破的「反向信号」—— 你的研究是否有突破迹象？")
    print(SEP)
    print("回答以下 7 个问题（y/n），评估你是否在突破边缘。\n")

    signals = [
        ("统一信号",
         "你研究的两个看似不同的现象，可能有同一个数学结构吗？",
         "牛顿（苹果+月亮）/ 麦克斯韦（电+磁+光）都从这里开始"),
        ("反常信号",
         "你的理论和实验有无法解释的不一致吗（不是误差）？",
         "水星近日点多 43 角秒 → GR；紫外灾难 → 量子"),
        ("数学信号",
         "你需要的数学还不存在，需要发明/借用吗？",
         "牛顿发明微积分；爱因斯坦求助格罗斯曼学黎曼几何"),
        ("极端信号",
         "把参数推到极端（∞/0），你的理论在哪里崩溃？",
         "经典物理在黑体高频崩溃 → 量子；GR 在奇点崩溃 → 需量子引力"),
        ("假设信号",
         "你领域里有'所有人都知道但没人证明'的假设吗？",
         "贝尔质疑局域实在论 → 2022 诺奖"),
        ("跨界信号",
         "另一个领域有类似问题，他们的方法能搬过来吗？",
         "Hopfield 把统计力学搬进神经网络 → 2024 诺奖"),
        ("工具信号",
         "未来 5 年哪个新工具上线？它可能打开什么窗口？",
         "LIGO(2015)/JWST(2022) 都是新工具驱动突破"),
    ]

    # 自动评估版（演示用，不实际问用户）
    print("  以下是 7 个'突破信号'检查清单：\n")
    for i, (name, question, example) in enumerate(signals, 1):
        print(f"  [{i}] {name}")
        print(f"      问题：{question}")
        print(f"      案例：{example}")
        print()

    # 模拟一个"卡住的研究"诊断
    print("  ▶ 案例：一个'卡住'的研究 vs 一个'快突破'的研究\n")
    print(f"  {'维度':<16} {'卡住的研究':<28} {'快突破的研究':<28}")
    print(f"  {SUBSEP}")
    stuck_vs_breaking = [
        ("心态",       "再算精确一点",               "换个框架/换个假设"),
        ("反常态度",   "把它当作噪声忽略",            "它是金矿"),
        ("数学",       "用熟悉的工具重复算",          "学新数学/借别的领域"),
        ("跨界",       "只读自己领域论文",            "读 Nature 全栏目"),
        ("假设",       "默认'所有人都知道'的事",      "逐一质疑"),
        ("极端测试",   "只在常规参数下验证",          "推到∞/0看哪里崩溃"),
        ("合作",       "独自死磕",                   "找跨学科合作者"),
    ]
    for dim, stuck, breaking in stuck_vs_breaking:
        print(f"  {dim:<16} {stuck:<28} {breaking:<28}")

    print(f"\n  💡 爱因斯坦：'我们不能用创造问题时同样的思维来解决它。'")
    print(f"     突破几乎总是来自'换框架'，而非'在同框架里更努力'。")


# ============================================================================
# §4 未来 10 年突破预测
# ============================================================================

def demo_future_predictions():
    print(f"\n{SEP}")
    print("§4 未来 10 年最可能的突破（预测）")
    print(SEP)
    print()

    predictions = [
        ("暗能量本质",       "高",    "2025-2030", "DESI/Euclid反常",       "可能推翻ΛCDM"),
        ("μ子g-2新物理",    "中高",  "2025-2027", "费米实验室最终结果",     "指向BSM粒子"),
        ("AI加速物理发现",   "极高",  "2025-2030", "AlphaFold/GNoME模式",    "AI成为标配工具"),
        ("量子纠错实用化",   "高",    "2025-2035", "Google Willow后续",      "容错量子计算"),
        ("高温超导机制",     "中",    "2025-2035", "量子模拟器",            "理解铜基/镍基超导"),
        ("暗物质直接探测",   "中",    "2025-2035", "LZ/XENONnT/DARWIN",     "找到或排除WIMPs"),
        ("黑洞信息悖论",     "中",    "2025-2035", "AdS-CFT/岛屿公式",      "理论解决"),
        ("Hubble张力解决",   "中",    "2025-2030", "JWST+新超新星数据",      "新宇宙学模型"),
        ("量子引力实验信号", "低",    "2030-2050", "下一代引力波探测器",     "弦理论首次验证"),
        ("弦理论可验证预言", "极低",  "2030-?",    "范式转换",              "可能需要新爱因斯坦"),
    ]

    print(f"  {'方向':<22} {'概率':<6} {'时间':<12} {'依赖':<22} {'影响'}")
    print(f"  {SUBSEP}")
    for direction, prob, timeframe, dependency, impact in predictions:
        prob_icon = {"极高": "🔴", "高": "🟠", "中高": "🟡", "中": "🟢", "低": "🔵", "极低": "⚫"}.get(prob, "⚪")
        print(f"  {direction:<22} {prob_icon} {prob:<4} {timeframe:<12} {dependency:<22} {impact}")

    # 概率分布
    print(f"\n  ▶ 突破概率分布（按 10 年内可能性）\n")
    prob_order = ["极高", "高", "中高", "中", "低", "极低"]
    for p in prob_order:
        items = [pred for pred in predictions if pred[1] == p]
        if items:
            bar = "█" * len(items) * 3
            print(f"  {p:<6} {bar} {len(items)} 个方向")

    print(f"\n  💡 最可能在 10 年内突破的：")
    print(f"     1. AI for Science（已经发生）")
    print(f"     2. 暗能量本质（DESI/Euclid 数据正在来）")
    print(f"     3. 量子纠错实用化（Willow 已过盈亏平衡）")
    print(f"\n  ⚠️ 最不确定但影响最大的：量子引力——可能需要另一个爱因斯坦")


# ============================================================================
# 主入口
# ============================================================================

DEMOS = {
    1: ("7 大突破模式时间线",     demo_seven_patterns),
    2: ("各分支瓶颈→突破链条",   demo_branch_crises),
    3: ("突破反向信号诊断器",    demo_breakthrough_signals),
    4: ("未来 10 年突破预测",    demo_future_predictions),
}


def main():
    print("╔" + "═" * 74 + "╗")
    print("║" + " 物理学突破方法论 · 可视化 demo ".center(74) + "║")
    print("║" + " 配套：top-physics-courses/PHYSICS_BREAKTHROUGHS.md ".center(74) + "║")
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
    print("🎯 突破方法论的精华：")
    print("   1. 统一（苹果+月亮=引力）")
    print("   2. 实验反常（迈克尔逊-莫雷→相对论）")
    print("   3. 数学新工具（牛顿发明微积分）")
    print("   4. 思想实验（爱因斯坦电梯）")
    print("   5. 推翻假设（推翻绝对时间）")
    print("   6. 跨学科（安德森/Hopfield）")
    print("   7. 新工具（LIGO/JWST）")
    print(SEP)
    print("📚 完整文档：PHYSICS_BREAKTHROUGHS.md（同目录）")


if __name__ == "__main__":
    main()
