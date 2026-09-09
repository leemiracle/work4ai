#!/usr/bin/env python3
"""
475 本书 × 28 视角深度分析生成器
===================================
为每本书生成一份 .md 文件，包含 28 视角的逐一切入：
  - 适用度（强/中/弱/不适用）
  - 启动提问（针对本书的具体提问）
  - 本书应用（基于书的主题/TOC）
  - 切面产出（这本书能照出什么）
  - 接入 13 目录

用法:
  python3 scripts/book_views_deep.py            # 全部
  python3 scripts/book_views_deep.py --limit 5  # 试点
"""
import os
import re
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
OUTPUT_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍深度分析")

# === 28 视角元信息 ===
VIEWS = {
    "V01": ("反例驱动", "A", "删假设看反例", "强"),
    "V02": ("公理逆向", "A", "公理反推", "强"),
    "V03": ("历史发生学", "A", "重走错路", "中"),
    "V04": ("最小非平凡例子", "A", "n=2 验证", "强"),
    "V05": ("严格度光谱", "A", "Tao 三阶自检", "强"),
    "V06": ("计算实验", "A", "Python 跑一遍", "强"),
    "V07": ("代几对偶", "B", "代数 ↔ 几何", "中"),
    "V08": ("范畴俯瞰", "B", "找泛性质", "中"),
    "V09": ("物理直觉", "B", "数学 → 物理", "中"),
    "V10": ("复杂度", "B", "判定多难", "弱"),
    "V11": ("信息论", "B", "信息含量", "中"),
    "V12": ("Curry-Howard", "C", "命题=类型", "弱"),
    "V13": ("Lean 形式化", "C", "Mathlib 对应", "中"),
    "V14": ("ML 锚点", "C", "数学 → ML", "中"),
    "V15": ("工程出口", "C", "数学 → 工程", "强"),
    "V16": ("艺术音乐", "C", "数学 → 艺术", "弱"),
    "V17": ("反例配对", "D", "反例族谱", "中"),
    "V18": ("不可能性", "D", "永远做不到", "中"),
    "V19": ("替代范式", "D", "其他范式", "中"),
    "V20": ("比较文学", "D", "多书并读", "强"),
    "V21": ("审美游戏", "E", "Lockhart 美学", "中"),
    "V22": ("费曼讲解", "E", "讲给妈", "强"),
    "V23": ("问题驱动", "E", "开问题清单", "中"),
    "V24": ("跨书追踪", "E", "概念多书对照", "强"),
    "V25": ("真实数据", "F", "Python 拟合", "强"),
    "V26": ("失败案例", "F", "数学误用灾难", "中"),
    "V27": ("日常化身", "F", "家用化身", "弱"),
    "V28": ("社会系统", "F", "社会子系统", "中"),
}

# === 主题 → 视角推荐矩阵 ===
THEME_TO_STRONG_VIEWS = {
    "分析·微积分": ["V01", "V03", "V04", "V05", "V06", "V13", "V22"],
    "分析·实分析/测度": ["V05", "V08", "V17", "V18", "V20", "V24"],
    "分析·复分析": ["V07", "V09", "V17", "V20", "V24"],
    "分析·泛函": ["V08", "V11", "V15", "V17", "V20"],
    "分析·调和/小波": ["V11", "V14", "V15", "V25", "V27"],
    "代数·线性": ["V04", "V07", "V14", "V15", "V20", "V24"],
    "代数·抽象": ["V02", "V08", "V12", "V19", "V20", "V24"],
    "代数·交换/环模": ["V02", "V08", "V13", "V17", "V20"],
    "代数·同调": ["V08", "V13", "V18", "V20"],
    "代数·群论": ["V07", "V08", "V16", "V20", "V24"],
    "代数·表示": ["V08", "V09", "V15", "V20"],
    "几何·微分/黎曼": ["V07", "V09", "V15", "V21", "V25"],
    "几何·代数": ["V08", "V13", "V17", "V18", "V21"],
    "几何·拓扑": ["V04", "V08", "V17", "V18", "V24"],
    "概率·统计": ["V04", "V14", "V22", "V25", "V26", "V27"],
    "概率·随机过程": ["V09", "V15", "V19", "V25", "V26", "V28"],
    "数论": ["V15", "V18", "V19", "V21", "V23"],
    "组合/图论": ["V04", "V10", "V15", "V23", "V25"],
    "逻辑/基础/集合/范畴": ["V08", "V12", "V13", "V18", "V19"],
    "优化/变分/控制": ["V08", "V09", "V14", "V25", "V28"],
    "动力系统/ODE/PDE": ["V09", "V11", "V25", "V26", "V28"],
    "数值/计算/算法": ["V06", "V10", "V12", "V15", "V25"],
    "数学物理": ["V09", "V11", "V19", "V25"],
    "信息/编码/密码": ["V11", "V15", "V18", "V25", "V28"],
    "金融数学": ["V15", "V19", "V25", "V26", "V28"],
    "建模/应用": ["V22", "V25", "V26", "V27", "V28"],
    "数学史/科普/方法论": ["V03", "V16", "V21", "V22", "V27"],
    "其他": ["V04", "V05", "V22", "V24"],
}

# === 启动提问模板 ===
VIEW_PROMPTS = {
    "V01": [
        "把书中每个定理的每条假设逐个删除，看会出什么反例？",
        "书中提到哪些病态反例（Weierstrass/Cantor/Vitali/Peano）？它们揭示什么假设的必要性？",
        "如果换成 $\\mathbb{Q}$ 而非 $\\mathbb{R}$，书中定理还成立吗？",
    ],
    "V02": [
        "书中每条公理的「反例碑文」是什么——历史上没有这条公理会怎样？",
        "书中公理系统是否 Gödel 不完备？它无法证明什么？",
        "公理之间的独立性——能否去掉某条用其他公理推导？",
    ],
    "V03": [
        "作者当年是怎么想出来的？原始论文是哪年？",
        "书中概念的第一版是什么？怎么错的？谁修正的？",
        "如果这个数学家没生，会推迟多少年？",
    ],
    "V04": [
        "n=2 / dim=2 / |G|=2 时书中定理还成立吗？",
        "书中每个概念在最小非平凡例子上长什么样？",
        "找临界规模：n=k 成立但 n=k+1 失败吗？",
    ],
    "V05": [
        "读这本书时，我现在处于 Tao 哪一阶（pre-rigorous / rigorous / post-rigorous）？",
        "书的哪一章是 rigorous 阶段黄金标本？",
        "我能在 3 个月后达到 post-rigorous 阶吗？",
    ],
    "V06": [
        "每章用 Python / SymPy / numpy 跑一遍——哪里崩？",
        "Lean 4 + Mathlib4 中本书的定理叫什么？",
        "能否把书中证明 extract 成程序？",
    ],
    "V07": [
        "每个代数陈述对应的几何图像是什么？能画吗？",
        "用 Desmos / GeoGebra / matplotlib 可视化",
        "几何对偶：代数 ↔ 几何 ↔ 物理三栏翻译",
    ],
    "V08": [
        "书中的数学构造，其泛性质是什么？",
        "是哪个伴随对的单位/余单位？",
        "Yoneda 引理能否简化书中的证明？",
    ],
    "V09": [
        "书中数学概念对应什么物理过程？",
        "力学 / 量子 / 热力学的类比？",
        "Noether 对应（对称 → 守恒律）？",
    ],
    "V10": [
        "构造书中对象是 P / NP / 不可判定？",
        "书中算法的复杂度类？",
        "存在多项式算法吗？",
    ],
    "V11": [
        "书中对象的 Shannon 熵 / Kolmogorov 复杂度？",
        "数学证明压缩了多少信息？",
        "最大熵原理能用上吗？",
    ],
    "V12": [
        "书中存在性证明能 extract 出什么程序？",
        "把命题翻译成类型——是哪个类型？",
        "证明能否改写成 Lean / Coq？",
    ],
    "V13": [
        "书中定理在 Mathlib4 里叫什么？路径是？",
        "我自己能形式化书中的哪一章？",
        "Mathlib 还缺哪些定理（贡献机会）？",
    ],
    "V14": [
        "书中概念在 ML 算法里是哪一步？",
        "ML 论文有引用这本书吗？",
        "用 PyTorch 复现书中算法？",
    ],
    "V15": [
        "书中数学支撑哪些真实工程系统？",
        "依赖链：数学 → 哪个职业 → 哪个决策？",
        "数学失效时崩成什么？",
    ],
    "V16": [
        "书中数学在艺术 / 音乐 / 建筑里如何现身？",
        "对称群 / 黄金比 / 调和 / 分形——哪些现身？",
        "用书中数学创作一件艺术作品？",
    ],
    "V17": [
        "书中定理配哪些反例？反例族如何归类？",
        "病态边界在哪？",
        "配 06-counterexamples 文件夹",
    ],
    "V18": [
        "书中理论的 Gödel / CAP / No-Free-Lunch 极限在哪？",
        "永远做不到什么？",
        "不可能性的哲学意义？",
    ],
    "V19": [
        "书中范式的替代是什么？（非标准/直觉主义/范畴）",
        "同一概念的其他刻画？",
        "范式之争的本质？",
    ],
    "V20": [
        "同一概念在其他书里怎么写？",
        "三栏对照：定义 / 证明 / 例子",
        "作者文风对比？",
    ],
    "V21": [
        "书中最美的定理/证明是什么？为什么美？",
        "找「啊哈」瞬间",
        "写 Lockhart 式审美短文",
    ],
    "V22": [
        "能向妈讲清书中概念吗？",
        "用大白话 + 比喻 + 例子",
        "录 3 分钟语音讲解",
    ],
    "V23": [
        "书中哪些章节是开放问题驱动的？",
        "我能从书中找到当前研究的什么开问题？",
        "Hilbert 23 问题风格——我能列我的开问题清单？",
    ],
    "V24": [
        "书中概念在其他书/论文中各怎么定义？",
        "多书并读同一概念，找共识和分歧",
        "建概念穿透卡（跨 13 目录）",
    ],
    "V25": [
        "书中定理能拟合什么真实数据？",
        "Python + 真实数据集验证",
        "残差分析 + 误差量化",
    ],
    "V26": [
        "书中数学被误用导致过什么灾难？",
        "LTCM / 2008 / Fukushima / Vioxx——书涉及哪个？",
        "数学误用的认知偏差是什么？",
    ],
    "V27": [
        "书中数学在家用品 / 手机 / 超市如何现身？",
        "拍照家用物品 + 数学注释",
        "用书中概念解释厨房现象",
    ],
    "V28": [
        "书中数学支撑哪个社会子系统（金融/电网/医疗/通信）？",
        "系统耦合：与其他子系统的依赖",
        "政策启示——决策者该懂什么？",
    ],
}

# === 主题 → 真实系统映射（用于 V25/V28） ===
THEME_TO_SYSTEMS = {
    "分析·微积分": ["桥梁设计", "行星轨道"],
    "分析·实分析/测度": ["概率模型根基"],
    "分析·复分析": ["量子场论", "信号处理", "滤波器设计"],
    "分析·泛函": ["量子力学", "核方法 ML", "控制系统"],
    "分析·调和/小波": ["JPEG", "MP3", "MRI", "5G OFDM", "雷达"],
    "代数·线性": ["GPT 大模型", "Netflix 推荐", "PCA", "图像压缩"],
    "代数·抽象": ["RSA 加密", "ECC 椭圆曲线", "晶体结构"],
    "代数·交换/环模": ["代数几何基础"],
    "代数·同调": ["代数拓扑工具"],
    "代数·群论": ["魔方", "晶体", "对称密码"],
    "代数·表示": ["量子化学", "粒子物理"],
    "几何·微分/黎曼": ["广义相对论", "AlphaFold", "机器人"],
    "几何·代数": ["现代代数几何研究"],
    "几何·拓扑": ["数据分析 TDA", "物质相变"],
    "概率·统计": ["GPT", "量化", "民调", "AB 测试"],
    "概率·随机过程": ["量化期权", "扩散模型", "COVID 建模"],
    "数论": ["RSA", "比特币 ECDSA", "Diffie-Hellman", "Signal"],
    "组合/图论": ["PageRank", "TSP 物流", "社交网络", "GNN"],
    "逻辑/基础/集合/范畴": ["Coq", "Lean", "AWS s2n", "CompCert"],
    "优化/变分/控制": ["SGD", "SVM", "无人机", "SpaceX"],
    "动力系统/ODE/PDE": ["IPCC 气候", "COVID", "电网", "天气预报"],
    "数值/计算/算法": ["GPU", "FEM 仿真", "天气预报"],
    "数学物理": ["核聚变 ITER", "弦理论", "量子计算"],
    "信息/编码/密码": ["5G LDPC", "Wi-Fi", "QR 码", "CD"],
    "金融数学": ["期权市场", "Basel III", "LTCM 警示"],
    "建模/应用": ["城市管理", "供应链"],
    "数学史/科普/方法论": ["数学教育", "文化传承"],
    "其他": ["通用基础"],
}

# === 失败案例库（用于 V26） ===
THEME_TO_FAILURES = {
    "分析·实分析/测度": ["Banach-Tarski 悖论（选择公理后果）"],
    "分析·调和/小波": ["JPEG lossy 误用（医院影像丢失诊断信息）"],
    "代数·线性": ["矩阵条件数忽略（数值不稳定）"],
    "代数·抽象": ["加密参数选弱（RSA 1024 已不安全）"],
    "概率·统计": ["Sally Clark 1999（乘法独立误用）", "民调 2016 美国大选（抽样偏差）"],
    "概率·随机过程": ["LTCM 1998（正态假设）", "2008 次贷（高斯 Copula）"],
    "数论": ["Debian OpenSSL 2008 漏洞（素数生成 bug）"],
    "组合/图论": ["Knight Capital 2012（算法错误 $4.4 亿）"],
    "动力系统/ODE/PDE": ["Fukushima 2011（PDE 极值低估）", "Imperial Ferguson 2020（SIR 参数）"],
    "数值/计算/算法": ["Ariane 5 1996（数值溢出 $3.7 亿）", "Sleipner A 1991（FEM 错误）"],
    "金融数学": ["LTCM 1998", "2008 次贷", "London Whale 2012"],
    "建模/应用": ["Theranos 2018（统计学造假）"],
}

# === 接入 13 目录建议（按主题） ===
THEME_TO_DIRECTORIES = {
    "分析·微积分": ["01-track/stage-1-本科核心/02-Spivak微积分/", "04-concepts/极限-多表征.md", "06-counterexamples/"],
    "分析·实分析/测度": ["01-track/stage-2-研究生基础/", "04-concepts/积分-多表征.md", "06-counterexamples/03-不可测集-Vitali.md"],
    "代数·线性": ["01-track/stage-1-本科核心/03-LADR线性代数/", "04-concepts/特征值-多表征.md", "09-crosstext/01-线代三书对照"],
    "概率·统计": ["01-track/stage-1-本科核心/04-Ross概率/", "11-日常生活与公民数学/02-病人理解诊断概率.md"],
    "动力系统/ODE/PDE": ["12-社会系统视角/02-一次疫情的跨职业协作.md", "11-日常生活/04-市民看疫情曲线.md"],
    "金融数学": ["12-社会系统视角/03-金融系统的整体稳定.md", "03-lens-practitioners/05-社会经济视角/"],
    "数论": ["03-lens-practitioners/03-计算信息视角/", "08-projects/05-质数无限的多种证明.md"],
    "几何·拓扑": ["06-counterexamples/", "08-projects/01-FTC微积分基本定理的N条证明.md"],
    "数学史/科普/方法论": ["05-history/", "13-数学作为语言/", "11-日常生活与公民数学/"],
}


def detect_theme(book_md_path: Path) -> str:
    """从书的索引 .md 提取主题（基于书名启发式）"""
    name = book_md_path.stem
    for theme, kws in {
        "分析·微积分": ["微积分", "Calculus", "数学分析", "Mathematical Analysis"],
        "分析·实分析/测度": ["实分析", "Real Analysis", "测度", "Measure", "Lebesgue"],
        "分析·复分析": ["复分析", "复变", "Complex"],
        "分析·泛函": ["泛函", "Functional", "Banach", "Hilbert", "Operator", "算子"],
        "分析·调和/小波": ["调和", "Fourier", "小波", "wavelet", "Harmonic"],
        "代数·线性": ["线性代数", "Linear Algebra", "矩阵", "Matrix"],
        "代数·抽象": ["抽象代数", "Abstract Algebra", "代数", "Algebra"],
        "代数·群论": ["群论", "Group"],
        "几何·拓扑": ["拓扑", "Topology", "流形", "Manifold", "同伦", "Homotopy"],
        "几何·微分/黎曼": ["微分几何", "黎曼", "Riemannian"],
        "几何·代数": ["代数几何", "Algebraic Geometry", "概形"],
        "概率·统计": ["概率", "Probability", "统计", "Statistics"],
        "概率·随机过程": ["随机", "Stochastic", "Brownian", "Markov"],
        "数论": ["数论", "Number Theory", "椭圆曲线", "Elliptic"],
        "组合/图论": ["组合", "Combinator", "图论", "Graph"],
        "逻辑/基础/集合/范畴": ["逻辑", "Logic", "集合", "范畴", "Categor"],
        "动力系统/ODE/PDE": ["微分方程", "Differential Equation", "动力系统"],
        "金融数学": ["金融", "Financial", "期权", "衍生"],
        "数学史/科普/方法论": ["史", "故事", "游戏"],
    }.items():
        for kw in kws:
            if kw in name:
                return theme
    return "其他"


def parse_index(book_md_path: Path) -> dict:
    """解析书的索引 .md"""
    text = book_md_path.read_text(encoding="utf-8", errors="ignore")
    info = {
        "file": book_md_path.stem,
        "series": book_md_path.parent.name,
        "pages": 0,
        "toc_count": 0,
        "toc_first_chapters": [],
        "preface_excerpt": "",
        "theme": detect_theme(book_md_path),
    }
    m = re.search(r"页数：(\d+)", text)
    if m: info["pages"] = int(m.group(1))
    m = re.search(r"书签目录（共 (\d+) 条）", text)
    if m:
        info["toc_count"] = int(m.group(1))
        toc_block = re.search(r"书签目录.*?```\n(.*?)```", text, re.S)
        if toc_block:
            chapters = [l.strip() for l in toc_block.group(1).split("\n") if l.strip()][:8]
            info["toc_first_chapters"] = chapters
    m = re.search(r"前言摘要.*?```\n(.*?)```", text, re.S)
    if m:
        info["preface_excerpt"] = m.group(1).strip()[:500]
    return info


def render_book_views(book_info: dict) -> str:
    """为单本书渲染 28 视角深度分析"""
    L = []
    book_name = book_info["file"]
    theme = book_info["theme"]
    strong_views = set(THEME_TO_STRONG_VIEWS.get(theme, THEME_TO_STRONG_VIEWS["其他"]))
    
    # 头部
    L.append(f"# 28 视角深度分析：{book_name}\n")
    L.append(f"> 自动生成自 [书籍索引](../书籍索引/) · 主题：**{theme}**\n")
    L.append("")
    
    # 元数据
    L.append("## 📊 元数据\n")
    L.append(f"- 丛书：{book_info['series']}")
    L.append(f"- 主题：{theme}")
    L.append(f"- 页数：{book_info['pages']}")
    L.append(f"- TOC 条数：{book_info['toc_count']}")
    L.append(f"- 推荐视角：{' '.join(sorted(strong_views))}")
    L.append("")
    
    # 视角适配热力图
    L.append("## 🔥 视角适配热力图（28 视角 × 适用度）\n")
    L.append("| V | 视角名 | 族 | 适用度 |")
    L.append("|---|------|---|-------|")
    for vid, (vname, family, _, _) in VIEWS.items():
        strength = "🔥 强" if vid in strong_views else ("🟡 中" if vid in ["V04","V05","V06","V22","V24"] else "⚪ 弱")
        L.append(f"| {vid} | {vname} | {family} | {strength} |")
    L.append("")
    
    # 28 视角逐一深度
    L.append("## 🎯 28 视角逐一深度（每个视角的具体应用）\n")
    
    for vid, (vname, family, essence, _) in VIEWS.items():
        applicable = vid in strong_views or vid in ["V04", "V05", "V06", "V22", "V24"]
        strength = "🔥" if vid in strong_views else ("🟡" if applicable else "⚪")
        
        L.append(f"### {vid} {vname}（{family} 族 · {essence}） {strength}\n")
        
        if not applicable:
            L.append(f"> ⚪ 本视角对 {theme} 类书籍适用度低，跳过深度分析。\n")
            continue
        
        # 启动提问
        prompts = VIEW_PROMPTS.get(vid, [])
        L.append("**启动提问**：")
        for p in prompts[:3]:
            L.append(f"- {p}")
        L.append("")
        
        # 本书应用（基于主题）
        L.append(f"**本书应用**（主题 = {theme}）：")
        
        if vid in ["V25", "V28"]:
            systems = THEME_TO_SYSTEMS.get(theme, ["通用"])
            L.append(f"- 真实系统锚点：{', '.join(systems[:4])}")
        elif vid == "V26":
            failures = THEME_TO_FAILURES.get(theme, [])
            if failures:
                L.append(f"- 失败案例：{', '.join(failures[:3])}")
            else:
                L.append("- 暂无该主题的经典失败案例档案")
        elif vid == "V20":
            L.append(f"- 三栏对照本书与同主题其他书")
        elif vid == "V13":
            L.append(f"- Mathlib4 路径（用 gh-grep 搜 `{theme.split('/')[0]}`）")
        elif vid == "V04" and book_info["toc_first_chapters"]:
            L.append(f"- 用本书前 3 章作为最小例验证：")
            for ch in book_info["toc_first_chapters"][:3]:
                L.append(f"  - {ch[:80]}")
        else:
            L.append(f"- 应用 {theme} 主题的标准 {vid} 流程")
        L.append("")
        
        # 切面产出
        L.append("**切面产出**：")
        L.append(f"- 这本书能照出 {vname} 的什么独特切面？基于书的章节结构和主题定位。")
        if book_info["toc_count"] >= 20:
            L.append(f"- TOC 完整（{book_info['toc_count']} 条），可深度逐章分析")
        L.append("")
        
        # 接入目录
        if vid in ["V25", "V26", "V27", "V28"]:
            dirs = THEME_TO_DIRECTORIES.get(theme, [])
            if dirs:
                L.append(f"**接入 13 目录**：{', '.join(dirs[:2])}")
        L.append("")
        
        # 实战
        if vid == "V06" or vid == "V25":
            L.append("**实战**：")
            L.append("```python")
            L.append(f"# {vid} 实战：用 Python 验证 {book_name[:40]} 的核心概念")
            L.append("import numpy as np, scipy as sp")
            L.append(f"# TODO: 基于书的 TOC 实现具体验证")
            L.append("```")
            L.append("")
    
    # 总结
    L.append("## 🎯 综合建议\n")
    L.append(f"**推荐组合**：")
    recommended = sorted(strong_views)[:6]
    L.append(f"- 优先用：{', '.join(recommended)}")
    L.append(f"- 这 6 个视角的组合适合 {theme} 类主题，深度 6 维")
    L.append("")
    L.append(f"**学习路径**：")
    L.append(f"1. 先 V04 最小例子建立直觉")
    L.append(f"2. 再 V05 严格度自检")
    L.append(f"3. 然后 V22 费曼讲解")
    L.append(f"4. 最后 V25/V28 接地气")
    L.append("")
    
    return "\n".join(L)


def process_one(args):
    book_md_path_str, output_dir_str = args
    book_md_path = Path(book_md_path_str)
    output_dir = Path(output_dir_str)
    out_name = book_md_path.stem + ".md"
    out_path = output_dir / out_name
    if out_path.exists():
        return ("skip", book_md_path.name)
    try:
        info = parse_index(book_md_path)
        md = render_book_views(info)
        out_path.write_text(md, encoding="utf-8")
        return ("ok", book_md_path.name, info["theme"])
    except Exception as e:
        return ("error", book_md_path.name, str(e)[:60])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    if args.force:
        for d in OUTPUT_ROOT.iterdir():
            if d.is_dir():
                for f in d.glob("*.md"):
                    f.unlink()
        print("🧹 已清空")
    
    tasks = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir(): continue
        out_series = OUTPUT_ROOT / series_dir.name
        out_series.mkdir(exist_ok=True)
        for md in sorted(series_dir.glob("*.md")):
            tasks.append((str(md), str(out_series)))
    
    if args.limit:
        tasks = tasks[:args.limit]
    
    print(f"共 {len(tasks)} 本，使用 {args.workers} 进程")
    
    ok, skip, err = 0, 0, 0
    theme_dist = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r[0] == "ok":
                ok += 1
                theme = r[2] if len(r) > 2 else "未知"
                theme_dist[theme] = theme_dist.get(theme, 0) + 1
                if i % 50 == 0:
                    print(f"  [{i}/{len(tasks)}] ✅ {ok} ok / {skip} skip / {err} err")
            elif r[0] == "skip":
                skip += 1
            else:
                err += 1
                print(f"  ❌ {r[1]}: {r[2] if len(r)>2 else ''}")
    
    print(f"\n✅ 完成：{ok} ok ｜ ⏭️ {skip} skip ｜ ❌ {err} err")
    print(f"\n主题分布：")
    for theme, n in sorted(theme_dist.items(), key=lambda x: -x[1]):
        print(f"  {theme}: {n} 本")


if __name__ == "__main__":
    main()
