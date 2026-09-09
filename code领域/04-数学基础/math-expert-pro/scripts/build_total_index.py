#!/usr/bin/env python3
"""
汇总所有书籍索引，生成一份 TOTAL-INDEX.md（视角分析的导航底座）
"""
import re
from pathlib import Path

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
OUTPUT = INDEX_ROOT / "TOTAL-INDEX.md"

SERIES_ORDER = ["通俗数学名著译丛", "华章数学丛书", "现代数学基础丛书", "美国研究生数学"]

# 主题关键词分类（用于自动归类）
THEME_KEYWORDS = {
    "分析·微积分": ["微积分", "分析", "Calculus", "Analysis", "Mathematical Analysis"],
    "分析·实分析/测度": ["实分析", "测度", "Real", "Measure", "Integration", "积分"],
    "分析·复分析": ["复分析", "复变", "Complex"],
    "分析·泛函": ["泛函", "Functional", "Banach", "Hilbert", "Operator", "算子"],
    "分析·调和": ["调和", "Fourier", "Harmonic", "小波", "wavelet"],
    "代数·线性": ["线性代数", "Linear Algebra", "矩阵", "Matrix"],
    "代数·抽象": ["抽象代数", "Abstract Algebra", "代数", "Algebra"],
    "代数·交换/同调": ["交换代数", "Commutative", "同调", "Homological", "Homology"],
    "代数·群论": ["群论", "Group", "有限群"],
    "代数·表示": ["表示", "Representation"],
    "几何·微分": ["微分几何", "Differential Geometry", "黎曼", "Riemann"],
    "几何·代数": ["代数几何", "Algebraic Geometry"],
    "几何·拓扑": ["拓扑", "Topology", "流形", "Manifold"],
    "概率·统计": ["概率", "统计", "Probability", "Statistics", "Stochastic"],
    "概率·随机过程": ["随机", "Brownian", "马尔可夫", "Markov", "鞅", "Martingale"],
    "数论": ["数论", "Number Theory", "椭圆曲线", "Elliptic"],
    "组合/图论": ["组合", "Combinator", "图论", "Graph"],
    "逻辑/基础/集合": ["逻辑", "Logic", "集合", "Set", "范畴", "Categor", "Type", "递归", "Computab"],
    "优化/变分": ["优化", "Optimi", "变分", "Variation"],
    "动力系统/微分方程": ["动力系统", "Dynamical", "微分方程", "Differential Equation", "ODE", "PDE"],
    "数值/计算": ["数值", "Numerical", "计算", "Computational", "算法", "Algorithm"],
    "数学物理": ["力学", "Mechanic", "物理", "Physic", "相对论", "Relativity", "量子", "Quantum"],
    "信息/编码/密码": ["信息", "Information", "编码", "Coding", "密码", "Crypt"],
    "金融数学": ["金融", "Financial", "数理金融", "衍生"],
    "建模/应用": ["建模", "Model", "应用", "Appli"],
    "李群/李代数": ["李群", "Lie"],
    "数学史/科普": ["史", "History", "故事", "游戏", "趣", "娱乐"],
}


def classify_theme(filename: str, title_meta: str = "") -> str:
    text = filename + " " + title_meta
    for theme, kws in THEME_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                return theme
    return "其他"


def parse_one_md(md_path: Path) -> dict:
    """从单本书的 .md 提取结构化字段"""
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    info = {
        "file": md_path.stem,
        "series": md_path.parent.name,
        "pages": 0,
        "title_meta": "",
        "toc_count": 0,
        "toc_first5": [],
        "has_preface": False,
        "theme": classify_theme(md_path.stem),
    }
    m = re.search(r"页数：(\d+)", text)
    if m:
        info["pages"] = int(m.group(1))
    m = re.search(r"标题：(.+)", text)
    if m:
        info["title_meta"] = m.group(1).strip()
    m = re.search(r"书签目录（共 (\d+) 条）", text)
    if m:
        info["toc_count"] = int(m.group(1))
        # 提取前 5 条 TOC
        toc_block = re.search(r"书签目录.*?```\n(.*?)```", text, re.S)
        if toc_block:
            lines = [l.strip() for l in toc_block.group(1).split("\n") if l.strip()][:5]
            info["toc_first5"] = lines
    if "前言摘要" in text:
        info["has_preface"] = True
    info["theme"] = classify_theme(md_path.stem, info["title_meta"])
    return info


def main():
    all_books = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir():
            continue
        for md in sorted(series_dir.glob("*.md")):
            try:
                info = parse_one_md(md)
                all_books.append(info)
            except Exception as e:
                print(f"ERR {md.name}: {e}")

    # 写出 TOTAL-INDEX.md
    lines = []
    lines.append("# `../math` 全部书籍总索引（475 本 · 视角分析导航底座）\n")
    lines.append(f"> 自动汇总自 [书籍索引/](书籍索引/) 子目录，由 `scripts/build_total_index.py` 生成。\n")
    lines.append("> 用途：作为 28 视角分析的「地图」——按丛书/主题/页数快速定位。\n")
    lines.append("")
    lines.append("## 📊 总览\n")
    by_series = {}
    for b in all_books:
        by_series.setdefault(b["series"], []).append(b)
    lines.append(f"- 总书数：**{len(all_books)}** 本")
    lines.append(f"- 有书签 TOC：{sum(1 for b in all_books if b['toc_count']>0)} 本")
    lines.append(f"- 有前言摘要：{sum(1 for b in all_books if b['has_preface'])} 本")
    lines.append(f"- 总页数：{sum(b['pages'] for b in all_books):,}")
    lines.append("")
    lines.append("### 按丛书分布\n")
    lines.append("| 丛书 | 本数 | 总页数 | 有TOC | 有前言 |")
    lines.append("|------|------|-------|------|-------|")
    for s in SERIES_ORDER:
        if s in by_series:
            bs = by_series[s]
            toc_n = sum(1 for b in bs if b["toc_count"] > 0)
            pre_n = sum(1 for b in bs if b["has_preface"])
            pages = sum(b["pages"] for b in bs)
            lines.append(f"| {s} | {len(bs)} | {pages:,} | {toc_n} | {pre_n} |")
    lines.append("")

    # 按主题分类
    lines.append("## 🎯 按主题分类（视角分析的入口）\n")
    by_theme = {}
    for b in all_books:
        by_theme.setdefault(b["theme"], []).append(b)
    for theme in sorted(by_theme.keys(), key=lambda t: -len(by_theme[t])):
        bs = by_theme[theme]
        lines.append(f"### {theme}（{len(bs)} 本）\n")
        lines.append("| 书名 | 丛书 | 页数 | TOC |")
        lines.append("|------|------|------|-----|")
        for b in sorted(bs, key=lambda x: -x["pages"]):
            short_name = b["file"][:60]
            lines.append(f"| {short_name} | {b['series'][:8]} | {b['pages']} | {b['toc_count']} |")
        lines.append("")

    # 按丛书列出
    lines.append("## 📚 按丛书详细列表\n")
    for s in SERIES_ORDER:
        if s not in by_series:
            continue
        bs = sorted(by_series[s], key=lambda x: x["file"])
        lines.append(f"### {s}（{len(bs)} 本）\n")
        for b in bs:
            toc_marker = "📑" if b["toc_count"] > 0 else "📄"
            pre_marker = "📜" if b["has_preface"] else ""
            lines.append(f"- {toc_marker}{pre_marker} **{b['file']}** ({b['pages']} 页, TOC={b['toc_count']}, 主题={b['theme']})")
        lines.append("")

    # 视角分析建议
    lines.append("## 🎯 视角分析优先级建议（基于 TOC 完整度）\n")
    lines.append("> 优先对 TOC 完整的书做视角分析——它们的内容结构清晰可见。\n")
    toc_rich = sorted([b for b in all_books if b["toc_count"] >= 20], key=lambda x: -x["toc_count"])
    lines.append(f"### TOC ≥ 20 章的书（{len(toc_rich)} 本，深度视角分析首选）\n")
    lines.append("| 书名 | 丛书 | TOC 条数 | 主题 |")
    lines.append("|------|------|---------|------|")
    for b in toc_rich[:50]:
        lines.append(f"| {b['file'][:50]} | {b['series'][:8]} | {b['toc_count']} | {b['theme']} |")
    lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 写入 {OUTPUT}")
    print(f"   总书数：{len(all_books)}")
    print(f"   总页数：{sum(b['pages'] for b in all_books):,}")
    print(f"   TOC ≥ 20：{len(toc_rich)} 本")


if __name__ == "__main__":
    main()
