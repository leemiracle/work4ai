#!/usr/bin/env python3
"""
v2: 增强版总索引生成器
- 扩展主题关键词（v1 "其他" 过多）
- 加入 28 视角适配建议
- 输出 TOTAL-INDEX-v2.md
"""
import re
from pathlib import Path

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
OUTPUT = INDEX_ROOT / "TOTAL-INDEX.md"
VIEWS_OUTPUT = INDEX_ROOT / "视角适配矩阵.md"

SERIES_ORDER = ["通俗数学名著译丛", "华章数学丛书", "现代数学基础丛书", "美国研究生数学"]

# === 扩展主题分类（v3 · 减"其他"） ===
THEME_KEYWORDS = {
    "分析·微积分": ["微积分", "Calculus", "数学分析", "Mathematical Analysis", "Mathematics Analysis", "高等微积分"],
    "分析·实分析/测度": ["实分析", "Real Analysis", "测度", "Measure", "Integration", "积分", "Lebesgue", "Real.and", "集值分析"],
    "分析·复分析": ["复分析", "复变", "Complex", "Holomorphic", "全纯", "解析函数", "Riemann.Surface", "黎曼曲面", "Teichmueller", "Bergman"],
    "分析·泛函": ["泛函", "Functional", "Banach", "巴拿赫", "Hilbert", "希尔伯特", "Operator", "算子", "Spectral", "谱理论", "C-Algebra", "C*-代数", "C*-algebra", "Arveson", "Topological.Vector", "拓扑线性", "Analysis.Now", "Hardy-Hilbert", "Semigroup"],
    "分析·调和/小波": ["调和", "Fourier", "Harmonic", "小波", "wavelet", "Wavelet", "Bergman"],
    "代数·线性": ["线性代数", "Linear Algebra", "矩阵", "Matrix", "Vector Space", "向量空间"],
    "代数·抽象": ["抽象代数", "Abstract Algebra", "代数原书", "代数学", "Algebra", "Universal.Algebra", "泛代数"],
    "代数·交换/环模": ["交换代数", "Commutative", "环", "Ring", "模", "Module", "Ideal", "Crystallograph", "Associative.Algebra", "结合代数"],
    "代数·同调": ["同调", "Homological", "Homology", "上同调", "Cohomology", "K-Theory", "Sheaf", "层论"],
    "代数·群论": ["群论", "Group Theory", "有限群", "Finite Group", "Lie Group", "李群", "Coxeter", "群和", "Reflection.Group", "Permutation", "置换群", "Algebraic.Group", "代数群", "半群", "Semigroup", "Linear.Algebraic.Group"],
    "代数·表示": ["表示", "Representation"],
    "几何·微分/黎曼": ["微分几何", "Differential Geometry", "黎曼", "Riemannian", "Finsler", "辛几何", "Symplectic", "张量", "Tensor", "Differential.Manifold", "微分流形", "Cartan", "Symmetric.Space"],
    "几何·代数": ["代数几何", "Algebraic Geometry", "概形", "Scheme", "Variety", "椭圆曲线", "模形式", "Modular", "曲线模", "Algebraic.Function", "Abelian.Function"],
    "几何·拓扑": ["拓扑", "Topology", "流形", "Manifold", "同伦", "Homotopy", "Knot", "纽结", "纤维丛", "Fibre", "Fiber", "Hyperbolic", "双曲", "Differential.Topology", "微分拓扑", "Geometric.Topology"],
    "概率·统计": ["概率", "Probability", "统计", "Statistics", "Random", "随机过程", "Stochastic", "Gaussian", "高斯", "Random.Walk", "随机游走", "Random.Process"],
    "概率·随机过程": ["随机", "Stochastic", "Brownian", "布朗", "马尔可夫", "Markov", "鞅", "Martingale", "Ergodic", "遍历", "随机分析", "Point.Process", "点过程"],
    "数论": ["数论", "Number Theory", "丢番图", "Diophantine", "椭圆曲线", "Elliptic", "p-adic", "Cyclotomic", "Fermat", "Galois", "伽罗瓦", "局部域", "Local.Field", "代数数论"],
    "组合/图论": ["组合", "Combinator", "图论", "Graph", "枚举", "Enumeration", "polytop", "多面体", "Discrete", "离散", "Polytope"],
    "逻辑/基础/集合/范畴": ["逻辑", "Logic", "集合", "Set Theory", "范畴", "Categor", "Type", "类型论", "递归", "Computab", "Model Theory", "模型论", "Axiomatic", "公理"],
    "优化/变分/控制": ["优化", "Optimi", "变分", "Variation", "凸分析", "Convex", "控制", "Control", "规划", "Programming", "排队", "Queueing", "整数规划", "Mathematical.Program", "Bifurcation", "分岔", "分歧"],
    "动力系统/ODE/PDE": ["动力系统", "Dynamical", "微分方程", "Differential Equation", "ODE", "PDE", "Elliptic", "椭圆", "抛物", "Parabolic", "演化方程", "波动方程", "反应扩散", "发展方程", "Ginzburg", "Landau", "Hamilton", "Nonlinear", "非线性"],
    "数值/计算/算法": ["数值", "Numerical", "计算", "Computational", "算法", "Algorithm", "Computab"],
    "数学物理": ["力学", "Mechanic", "物理", "Physic", "相对论", "Relativity", "量子", "Quantum", "Ginzburg", "Landau", "Hamilton", "Classical"],
    "信息/编码/密码": ["信息", "Information", "编码", "Coding", "密码", "Crypt"],
    "金融数学": ["金融", "Financial", "数理金融", "衍生", "Option", "期货"],
    "建模/应用": ["建模", "Model", "应用", "Appli"],
    "数学史/科普/方法论": ["史", "History", "故事", "游戏", "趣", "娱乐", "近代", "当代", "黄金", "巨人", "科普"],
}


def classify_theme(filename: str, title_meta: str = "") -> str:
    text = filename + " " + title_meta
    # 优先级 1：数论（椭圆曲线 / Galois）
    if any(kw in text for kw in THEME_KEYWORDS["数论"]):
        return "数论"
    # 优先级 2：几何·拓扑（流形 / 同伦 / 微分拓扑）
    if any(kw in text for kw in THEME_KEYWORDS["几何·拓扑"]):
        return "几何·拓扑"
    # 优先级 3：动力系统（PDE / 演化方程）
    if any(kw in text for kw in THEME_KEYWORDS["动力系统/ODE/PDE"]):
        return "动力系统/ODE/PDE"
    # 优先级 4：泛函（C-代数 / 算子）
    if any(kw in text for kw in THEME_KEYWORDS["分析·泛函"]):
        return "分析·泛函"
    # 其余按字典顺序
    for theme, kws in THEME_KEYWORDS.items():
        if theme in ["数论", "几何·拓扑", "动力系统/ODE/PDE", "分析·泛函"]:
            continue
        for kw in kws:
            if kw in text:
                return theme
    return "其他"


# === 28 视角适配规则（基于主题 → 推荐视角） ===
THEME_TO_VIEWS = {
    "分析·微积分":           ["V1", "V3", "V4", "V5", "V6", "V13"],
    "分析·实分析/测度":      ["V5", "V8", "V17", "V18", "V24"],
    "分析·复分析":           ["V7", "V9", "V17", "V20", "V24"],
    "分析·泛函":             ["V8", "V11", "V15", "V17", "V20"],
    "分析·调和/小波":        ["V11", "V14", "V15", "V25"],
    "代数·线性":             ["V4", "V7", "V14", "V15", "V20"],
    "代数·抽象":             ["V2", "V8", "V12", "V19", "V20"],
    "代数·交换/环模":        ["V2", "V8", "V13", "V17", "V20"],
    "代数·同调":             ["V8", "V13", "V18", "V20"],
    "代数·群论":             ["V7", "V8", "V16", "V20", "V24"],
    "代数·表示":             ["V8", "V9", "V15", "V20"],
    "几何·微分/黎曼":        ["V7", "V9", "V15", "V21", "V25"],
    "几何·代数":             ["V8", "V13", "V17", "V18", "V21"],
    "几何·拓扑":             ["V4", "V8", "V17", "V18", "V24"],
    "概率·统计":             ["V4", "V14", "V22", "V25", "V26"],
    "概率·随机过程":         ["V9", "V15", "V19", "V25", "V26"],
    "数论":                  ["V15", "V18", "V19", "V21"],
    "组合/图论":             ["V4", "V10", "V15", "V23"],
    "逻辑/基础/集合/范畴":   ["V8", "V12", "V13", "V18", "V19"],
    "优化/变分/控制":        ["V8", "V9", "V14", "V25"],
    "动力系统/ODE/PDE":      ["V9", "V11", "V25", "V26", "V28"],
    "数值/计算/算法":        ["V6", "V10", "V12", "V15"],
    "数学物理":              ["V9", "V11", "V19", "V25"],
    "信息/编码/密码":        ["V11", "V15", "V18", "V25"],
    "金融数学":              ["V15", "V19", "V25", "V26", "V28"],
    "建模/应用":             ["V22", "V25", "V26", "V27", "V28"],
    "数学史/科普/方法论":    ["V3", "V16", "V21", "V22", "V27"],
    "其他":                  ["V4", "V5", "V22", "V24"],  # 默认组合
}

# 视角中文名（用于矩阵展示）
VIEW_NAMES = {
    "V1": "反例驱动", "V2": "公理逆向", "V3": "历史发生学", "V4": "最小例子",
    "V5": "严格度光谱", "V6": "计算实验", "V7": "代几对偶", "V8": "范畴俯瞰",
    "V9": "物理直觉", "V10": "复杂度", "V11": "信息论", "V12": "Curry-Howard",
    "V13": "Lean形式化", "V14": "ML锚点", "V15": "工程出口", "V16": "艺术/音乐",
    "V17": "反例配对", "V18": "不可能性", "V19": "替代范式", "V20": "比较文学",
    "V21": "审美游戏", "V22": "费曼讲解", "V23": "问题驱动", "V24": "跨书追踪",
    "V25": "真实数据", "V26": "失败案例", "V27": "日常化身", "V28": "社会系统",
}


def parse_one_md(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    info = {
        "file": md_path.stem,
        "series": md_path.parent.name,
        "pages": 0,
        "title_meta": "",
        "toc_count": 0,
        "has_preface": False,
        "theme": "",
        "views": [],
    }
    m = re.search(r"页数：(\d+)", text)
    if m: info["pages"] = int(m.group(1))
    m = re.search(r"标题：(.+)", text)
    if m: info["title_meta"] = m.group(1).strip()
    m = re.search(r"书签目录（共 (\d+) 条）", text)
    if m: info["toc_count"] = int(m.group(1))
    if "前言摘要" in text: info["has_preface"] = True
    info["theme"] = classify_theme(md_path.stem, info["title_meta"])
    info["views"] = THEME_TO_VIEWS.get(info["theme"], THEME_TO_VIEWS["其他"])
    return info


def main():
    all_books = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir(): continue
        for md in sorted(series_dir.glob("*.md")):
            try:
                all_books.append(parse_one_md(md))
            except Exception as e:
                print(f"ERR {md.name}: {e}")

    # === 写 TOTAL-INDEX.md（v2） ===
    L = []
    L.append("# `../math` 全部书籍总索引 · v2（含 28 视角适配）\n")
    L.append(f"> 自动汇总自 [书籍索引/](书籍索引/) · 由 `scripts/build_total_index_v2.py` 生成\n")
    L.append("> v2 增强：扩展主题分类 + 加入 28 视角适配建议\n")
    L.append("")
    L.append("## 📊 总览\n")
    by_series = {}
    for b in all_books: by_series.setdefault(b["series"], []).append(b)
    L.append(f"- 总书数：**{len(all_books)}** 本")
    L.append(f"- 总页数：**{sum(b['pages'] for b in all_books):,}** 页")
    L.append(f"- 有书签 TOC：{sum(1 for b in all_books if b['toc_count']>0)} 本")
    L.append(f"- 有前言摘要：{sum(1 for b in all_books if b['has_preface'])} 本")
    L.append("")
    L.append("### 按丛书分布\n")
    L.append("| 丛书 | 本数 | 总页数 | 有TOC | 有前言 |")
    L.append("|------|------|-------|------|-------|")
    for s in SERIES_ORDER:
        if s in by_series:
            bs = by_series[s]
            toc_n = sum(1 for b in bs if b["toc_count"] > 0)
            pre_n = sum(1 for b in bs if b["has_preface"])
            pages = sum(b["pages"] for b in bs)
            L.append(f"| {s} | {len(bs)} | {pages:,} | {toc_n} | {pre_n} |")
    L.append("")

    # 按主题
    by_theme = {}
    for b in all_books: by_theme.setdefault(b["theme"], []).append(b)
    L.append("## 🎯 按主题分类（27 类）\n")
    L.append("| 主题 | 本数 | 推荐视角 |")
    L.append("|------|------|---------|")
    for theme in sorted(by_theme.keys(), key=lambda t: -len(by_theme[t])):
        bs = by_theme[theme]
        views = THEME_TO_VIEWS.get(theme, [])
        view_str = " ".join(views[:5])
        L.append(f"| {theme} | {len(bs)} | {view_str} |")
    L.append("")

    # 各主题详细列表
    L.append("## 📚 各主题书籍详细列表\n")
    for theme in sorted(by_theme.keys(), key=lambda t: -len(by_theme[t])):
        bs = by_theme[theme]
        L.append(f"### {theme}（{len(bs)} 本） · 推荐视角：{' '.join(THEME_TO_VIEWS.get(theme, []))}\n")
        L.append("| 书名 | 丛书 | 页数 | TOC | 主题 |")
        L.append("|------|------|------|-----|------|")
        for b in sorted(bs, key=lambda x: -x["pages"]):
            short = b["file"][:55]
            L.append(f"| {short} | {b['series'][:6]} | {b['pages']} | {b['toc_count']} | {b['theme']} |")
        L.append("")

    # 视角分析优先级
    L.append("## 🎯 视角分析优先级\n")
    toc_rich = sorted([b for b in all_books if b["toc_count"] >= 20], key=lambda x: -x["toc_count"])
    L.append(f"### TOC ≥ 20 章（{len(toc_rich)} 本，深度分析首选）\n")
    L.append("| 书名 | 丛书 | TOC | 主题 | 推荐视角 |")
    L.append("|------|------|-----|------|---------|")
    for b in toc_rich[:50]:
        L.append(f"| {b['file'][:50]} | {b['series'][:6]} | {b['toc_count']} | {b['theme']} | {' '.join(b['views'])} |")
    L.append("")

    OUTPUT.write_text("\n".join(L), encoding="utf-8")

    # === 单独写 视角适配矩阵.md ===
    V = []
    V.append("# 28 视角 × 475 本书 适配矩阵\n")
    V.append("> 基于主题分类的自动适配。每本书适合的视角已自动标注。\n")
    V.append("> 用法：选一个视角 → 找所有适合的书；或选一本书 → 看推荐视角。\n")
    V.append("")
    V.append("## 视角 → 书籍 反向索引（哪些书最适合用视角 V?）\n")
    view_to_books = {}
    for b in all_books:
        for v in b["views"]:
            view_to_books.setdefault(v, []).append(b)
    for v in sorted(view_to_books.keys(), key=lambda x: int(x[1:])):
        bs = sorted(view_to_books[v], key=lambda x: -x["pages"])
        V.append(f"### {v} {VIEW_NAMES[v]}（{len(bs)} 本）\n")
        V.append("| 书名 | 丛书 | 主题 |")
        V.append("|------|------|------|")
        for b in bs[:15]:
            V.append(f"| {b['file'][:50]} | {b['series'][:6]} | {b['theme']} |")
        if len(bs) > 15:
            V.append(f"\n*... 还有 {len(bs)-15} 本，详见 [TOTAL-INDEX](TOTAL-INDEX.md)*\n")
        else:
            V.append("")
    VIEWS_OUTPUT.write_text("\n".join(V), encoding="utf-8")

    # 控制台汇总
    print(f"✅ TOTAL-INDEX 写入 {OUTPUT}")
    print(f"✅ 视角适配矩阵 写入 {VIEWS_OUTPUT}")
    print(f"   总书数：{len(all_books)}")
    print(f"   总页数：{sum(b['pages'] for b in all_books):,}")
    print(f"   主题分类：{len(by_theme)} 类")
    print(f"   「其他」分类：{len(by_theme.get('其他', []))} 本")
    print(f"   TOC ≥ 20：{len(toc_rich)} 本")
    print(f"\n视角覆盖：")
    for v in sorted(view_to_books.keys(), key=lambda x: int(x[1:])):
        print(f"   {v} {VIEW_NAMES[v]:12s} → {len(view_to_books[v])} 本")


if __name__ == "__main__":
    main()
