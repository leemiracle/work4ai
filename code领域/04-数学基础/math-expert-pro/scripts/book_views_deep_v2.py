#!/usr/bin/env python3
"""
v2: 475 本书 × 28 视角深度升级
- 替换模板字符串"基于书的章节结构和主题定位"
- 注入每本的真实 TOC 前 5 章
- 按主题给出具体的"本书应用"和"切面产出"
"""
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
DEEP_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍深度分析")

# === 主题 → 具体内容映射（升级版） ===
THEME_SPECIFICS = {
    "分析·微积分": {
        "real_data": "高考分数分布 / 行星轨道 / 桥梁应力",
        "failure": "Tolman 桥梁（1940，共振 PDE 误判）",
        "ml": "梯度下降 = 导数应用",
        "mathlib": "Mathlib.Topology.Continuity / Mathlib.Deriv",
        "failure_real": "Ariane 5 1996（浮点溢出）",
    },
    "分析·实分析/测度": {
        "real_data": "股票价格过程 / 信号采样",
        "failure": "Banach-Tarski 悖论（选择公理后果）",
        "ml": "测度论概率基础 PAC-Bayes",
        "mathlib": "Mathlib.MeasureTheory.Measure",
        "failure_real": "LTCM 1998（极端事件概率）",
    },
    "分析·复分析": {
        "real_data": "信号滤波 / 量子散射",
        "failure": "Picard 大定理病态",
        "ml": "复值神经网络",
        "mathlib": "Mathlib.Analysis.Complex",
        "failure_real": "滤波器设计失败",
    },
    "分析·泛函": {
        "real_data": "量子态测量 / 长程相关数据",
        "failure": "Banach-Tarski / 非自反空间病态",
        "ml": "核方法 / 高斯过程 / RKHS",
        "mathlib": "Mathlib.Analysis.Normed.Operator",
        "failure_real": "量子力学误用",
    },
    "分析·调和/小波": {
        "real_data": "音频 / 图像 / 心电图 / 股票 / 5G 信号",
        "failure": "JPEG lossy 误用（医院影像丢信息）",
        "ml": "卷积神经网络 / Scattering Network",
        "mathlib": "Mathlib.Analysis.Fourier",
        "failure_real": "MP3 编码失真",
    },
    "代数·线性": {
        "real_data": "推荐数据 / 图像 / 神经网络权重",
        "failure": "条件数爆炸（数值不稳定）",
        "ml": "PCA / SVD / 神经网络 / 线性回归",
        "mathlib": "Mathlib.LinearAlgebra.Matrix / Mathlib.LinearAlgebra.Eigenspace",
        "failure_real": "Netflix 大赛 2008 维度灾难",
    },
    "代数·抽象": {
        "real_data": "RSA 加密 / 晶体结构",
        "failure": "加密参数弱选（RSA-1024 不安全）",
        "ml": "群等变神经网络",
        "mathlib": "Mathlib.Algebra.Group / Mathlib.Algebra.Ring",
        "failure_real": "Debian OpenSSL 2008（素数 bug）",
    },
    "代数·交换/环模": {
        "real_data": "代数几何基础",
        "failure": "Noetherian 假设失效",
        "ml": "代数统计",
        "mathlib": "Mathlib.Algebra.Ring.Ideal / Mathlib.Algebra.Module",
        "failure_real": "Gröbner 基算法瓶颈",
    },
    "代数·同调": {
        "real_data": "拓扑数据分析 (TDA)",
        "failure": "Ext 计算爆炸",
        "ml": "持续同调 ML",
        "mathlib": "Mathlib.CategoryTheory.Abelian / Mathlib.HomologicalAlgebra",
        "failure_real": "TDA 误用",
    },
    "代数·群论": {
        "real_data": "魔方 / 晶体 / 对称密码",
        "failure": "Monster 群误读",
        "ml": "群等变 CNN",
        "mathlib": "Mathlib.Algebra.Group.Subgroup",
        "failure_real": "魔方不可能复原（部分状态）",
    },
    "代数·表示": {
        "real_data": "量子化学 / 粒子物理",
        "failure": "粒子分类错误",
        "ml": "对称神经网络",
        "mathlib": "Mathlib.RepresentationTheory",
        "failure_real": "标准模型预测偏差",
    },
    "几何·微分/黎曼": {
        "real_data": "GPS 相对论修正 / 行星轨道",
        "failure": "广义相对论奇点",
        "ml": "AlphaFold / 流形学习",
        "mathlib": "Mathlib.Geometry.Manifold / Mathlib.RiemannianGeometry",
        "failure_real": "GPS 不修正会偏 11 km/天",
    },
    "几何·代数": {
        "real_data": "椭圆曲线密码 / 编码论",
        "failure": "Hartshorne 严格度极高",
        "ml": "代数统计",
        "mathlib": "Mathlib.AlgebraicGeometry.Scheme",
        "failure_real": "代数攻击（如 ECC 弱参数）",
    },
    "几何·拓扑": {
        "real_data": "TDA 数据分析 / 物质相变",
        "failure": "非 Hausdorff 病态",
        "ml": "拓扑数据分析 (TDA)",
        "mathlib": "Mathlib.Topology.Basic",
        "failure_real": "TDA 误用（噪声敏感）",
    },
    "概率·统计": {
        "real_data": "民调 / 高考 / 股票 / 疫情",
        "failure": "Sally Clark 1999（独立假设误用）",
        "ml": "贝叶斯 / GPT / 朴素贝叶斯 / Logistic",
        "mathlib": "Mathlib.Probability.*",
        "failure_real": "2016 民调偏差 / Vioxx 2004",
    },
    "概率·随机过程": {
        "real_data": "股票布朗 / COVID 扩散",
        "failure": "LTCM 1998（正态假设）",
        "ml": "扩散模型 / 强化学习",
        "mathlib": "Mathlib.Probability.Stochastic",
        "failure_real": "Imperial Ferguson 2020（SIR 参数）",
    },
    "数论": {
        "real_data": "RSA / ECDSA / 比特币",
        "failure": "弱素数（Debian 2008）",
        "ml": "数论启发优化",
        "mathlib": "Mathlib.NumberTheory.*",
        "failure_real": "ECDSA 误签（2010 Sony PS3）",
    },
    "组合/图论": {
        "real_data": "PageRank / 社交网络 / 物流",
        "failure": "Knight Capital 2012（算法 bug）",
        "ml": "图神经网络 GNN",
        "mathlib": "Mathlib.Combinatorics.SimpleGraph",
        "failure_real": "TSP 路径误优化",
    },
    "逻辑/基础/集合/范畴": {
        "real_data": "Coq / Lean / 形式化验证",
        "failure": "Gödel 不完备（公理误信）",
        "ml": "Neural Theorem Proving",
        "mathlib": "Mathlib.CategoryTheory.* / Mathlib.Logic",
        "failure_real": "SSL 早期形式化漏洞",
    },
    "优化/变分/控制": {
        "real_data": "SGD 神经网络 / 无人机 / SpaceX",
        "failure": "局部极小（鞍点）",
        "ml": "SGD / Adam / 强化学习",
        "mathlib": "Mathlib.Analysis.Convex / Mathlib.Optimization",
        "failure_real": "Ariane 5 1996（控制溢出）",
    },
    "动力系统/ODE/PDE": {
        "real_data": "COVID / 气候 / 电网 / 天气",
        "failure": "Fukushima 2011（极值低估）",
        "ml": "物理启发神经网络 PINN",
        "mathlib": "Mathlib.ODE / Mathlib.PDE",
        "failure_real": "Imperial COVID 2020 / 德州寒潮 2021",
    },
    "数值/计算/算法": {
        "real_data": "GPU 矩阵 / FEM 仿真 / 天气",
        "failure": "Sleipner A 1991（FEM 错误）",
        "ml": "科学计算 + ML",
        "mathlib": "Mathlib.Numerics.*",
        "failure_real": "Ariane 5 / Sleipner A",
    },
    "数学物理": {
        "real_data": "核聚变 ITER / 量子计算",
        "failure": "Pioneer 异常（相对论修正缺失）",
        "ml": "量子机器学习",
        "mathlib": "Mathlib.Geometry.Differential",
        "failure_real": "核聚变实现失败",
    },
    "信息/编码/密码": {
        "real_data": "5G LDPC / Wi-Fi / QR 码 / CD",
        "failure": "A5/1 加密被破（GSM）",
        "ml": "信息瓶颈 IB / 互信息 ML",
        "mathlib": "Mathlib.InformationTheory",
        "failure_real": "Enigma 1940 破解",
    },
    "金融数学": {
        "real_data": "股票 / 期权 / 利率",
        "failure": "LTCM 1998 / 2008 次贷",
        "ml": "量化策略 / 信号",
        "mathlib": "Mathlib.Probability.Stochastic",
        "failure_real": "LTCM 1998 / 2008 / Knight 2012",
    },
    "建模/应用": {
        "real_data": "城市管理 / 供应链 / 人口",
        "failure": "Theranos 2018（统计学造假）",
        "ml": "决策模型",
        "mathlib": "Mathlib.ODE",
        "failure_real": "Theranos / 长期资本管理",
    },
    "数学史/科普/方法论": {
        "real_data": "数学教育 / 文化传承",
        "failure": "Lockhart 悲叹（教育失败）",
        "ml": "AI 教学",
        "mathlib": "—",
        "failure_real": "数学教育广泛失败",
    },
    "其他": {
        "real_data": "通用基础",
        "failure": "—",
        "ml": "—",
        "mathlib": "Mathlib.*",
        "failure_real": "—",
    },
}

# === 主题 → 跨书对照（用于 V20）===
THEME_COMPANIONS = {
    "分析·微积分": "Spivak Calculus / 华章 01 Rudin PMA / 通俗译丛 09",
    "分析·实分析/测度": "Halmos GTM018 / 严加安现代基础 006 / Royden / Rudin R&C",
    "代数·线性": "Axler LADR / Horn-Johnson 华章 52 / Artin Algebra / Strang",
    "概率·统计": "Ross 华章 51 / 严加安 006 / Shiryaev GTM095 / Loève GTM045",
    "动力系统/ODE/PDE": "现代基础 092 / Arnold GTM060 / 现代基础 014",
    "金融数学": "GTM113 Karatzas-Shreve / 华章 50 / Shreve 金融随机分析",
    "数论": "Ireland-Rosen GTM084 / Silverman GTM106 / 华章 39",
    "几何·拓扑": "Munkres 华章 17 / 现代基础 066 / Bott-Tu GTM082",
}


def get_theme(book_md_path: Path) -> str:
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
        "几何·拓扑": ["拓扑", "Topology", "流形", "Manifold"],
        "几何·微分/黎曼": ["微分几何", "黎曼", "Riemannian"],
        "几何·代数": ["代数几何", "Algebraic Geometry"],
        "概率·统计": ["概率", "Probability", "统计", "Statistics"],
        "概率·随机过程": ["随机", "Stochastic", "Brownian", "Markov"],
        "数论": ["数论", "Number Theory", "椭圆曲线"],
        "组合/图论": ["组合", "Combinator", "图论", "Graph"],
        "逻辑/基础/集合/范畴": ["逻辑", "Logic", "集合", "范畴"],
        "动力系统/ODE/PDE": ["微分方程", "Differential Equation", "动力系统", "反应扩散", "演化方程"],
        "金融数学": ["金融", "Financial", "期权", "衍生"],
        "数学史/科普/方法论": ["史", "故事", "游戏"],
    }.items():
        for kw in kws:
            if kw in name: return theme
    return "其他"


def parse_toc(book_md_path: Path):
    """提取 TOC 前 5 章"""
    text = book_md_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"书签目录.*?```\n(.*?)```", text, re.S)
    if m:
        chapters = [l.strip() for l in m.group(1).split("\n") if l.strip()][:5]
        return [c[:80] for c in chapters]
    return []


def upgrade_one(args):
    book_md_path_str = args[0]
    book_md_path = Path(book_md_path_str)
    deep_path = DEEP_ROOT / book_md_path.parent.name / (book_md_path.stem + ".md")
    if not deep_path.exists():
        return ("skip", book_md_path.name)
    
    text = deep_path.read_text(encoding="utf-8")
    theme = get_theme(book_md_path)
    specs = THEME_SPECIFICS.get(theme, THEME_SPECIFICS["其他"])
    toc = parse_toc(book_md_path)
    
    # 升级 1: 替换"基于书的章节结构和主题定位"
    if toc:
        toc_str = "; ".join(toc[:3])
        replacement_v04 = f"用书的前 3 章作为最小例验证：{toc_str}。每个核心概念在 n=2/dim=2 规模下手算。"
        replacement_general = f"基于书的章节（前 3 章：{toc_str}）和 {theme} 主题。"
    else:
        replacement_v04 = f"在 {theme} 主题下用 n=2 / dim=2 最小例验证全书概念。"
        replacement_general = f"基于 {theme} 主题的标准分析（书无 TOC，按主题推断）。"
    
    text = text.replace("这本书能照出 反例驱动 的什么独特切面？基于书的章节结构和主题定位。", 
                        f"删假设看反例——本书哪条定理最容易被反例击破？{replacement_general}")
    text = text.replace("这本书能照出 公理逆向 的什么独特切面？基于书的章节结构和主题定位。",
                        f"本书的公理系统的「墓碑」——每条公理对应什么历史教训。{replacement_general}")
    text = text.replace("这本书能照出 历史发生学 的什么独特切面？基于书的章节结构和主题定位。",
                        f"本书概念的历史发生顺序 vs 成书顺序。{replacement_general}")
    text = text.replace("这本书能照出 最小非平凡例子 的什么独特切面？基于书的章节结构和主题定位。",
                        replacement_v04)
    text = text.replace("这本书能照出 严格度光谱 的什么独特切面？基于书的章节结构和主题定位。",
                        f"本书处于 Tao 哪一阶？{replacement_general}")
    text = text.replace("这本书能照出 计算实验 的什么独特切面？基于书的章节结构和主题定位。",
                        f"用 Python/SymPy/Lean 验证全书核心定理。{replacement_general}")
    
    # 通用替换（其他视角）
    text = re.sub(r"这本书能照出 (\S+) 的什么独特切面？基于书的章节结构和主题定位。",
                  rf"本书能照出 \1 的什么独特切面？{replacement_general}", text)
    
    # 升级 2: "应用 X 主题的标准 Y 流程" → 注入具体内容
    text = text.replace("应用 分析·微积分 主题的标准 V01 流程", 
                        f"删假设看反例——本书涉及 {theme}，反例多在连续性/可导性假设")
    text = re.sub(r"应用 (\S+) 主题的标准 V(\d+) 流程",
                  lambda m: f"应用 {m.group(1)} 主题的 V{m.group(2)} 标准流程（结合本书 TOC）", text)
    
    # 升级 3: V25 真实数据注入
    if "V25" in text and "真实数据" in text:
        text = text.replace("应用 分析·微积分 主题的标准 V25 流程",
                            f"用 Python 拟合真实数据：{specs['real_data']}")
        for theme_key in THEME_SPECIFICS:
            text = text.replace(f"应用 {theme_key} 主题的标准 V25 流程",
                                f"用 Python 拟合真实数据：{THEME_SPECIFICS[theme_key]['real_data']}")
    
    # 升级 4: V26 失败案例注入
    for theme_key, specs in THEME_SPECIFICS.items():
        text = text.replace(f"应用 {theme_key} 主题的标准 V26 流程",
                            f"本书主题的经典失败案例：{specs['failure_real']}")
    
    # 升级 5: V13 Mathlib 注入
    for theme_key, specs in THEME_SPECIFICS.items():
        text = text.replace(f"应用 {theme_key} 主题的标准 V13 流程",
                            f"用 Lean 形式化：{specs['mathlib']}")
    
    # 升级 6: V14 ML 锚点注入
    for theme_key, specs in THEME_SPECIFICS.items():
        text = text.replace(f"应用 {theme_key} 主题的标准 V14 流程",
                            f"本书数学在 ML 的化身：{specs['ml']}")
    
    # 升级 7: V20 跨书注入
    companion = THEME_COMPANIONS.get(theme, "")
    if companion:
        for vid in ["V20", "V24"]:
            pattern = f"应用 {theme} 主题的标准 {vid} 流程"
            replacement = f"跨书对照：{companion}"
            text = text.replace(pattern, replacement)
    
    deep_path.write_text(text, encoding="utf-8")
    return ("ok", book_md_path.name, theme)


def main():
    tasks = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir(): continue
        for md in sorted(series_dir.glob("*.md")):
            tasks.append((str(md),))
    
    print(f"共 {len(tasks)} 本")
    
    ok, skip = 0, 0
    with ProcessPoolExecutor(max_workers=16) as ex:
        futures = {ex.submit(upgrade_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r[0] == "ok": ok += 1
            else: skip += 1
            if i % 100 == 0:
                print(f"  [{i}/{len(tasks)}] ✅ {ok} / ⏭️ {skip}")
    
    print(f"\n✅ 完成：{ok} ok / {skip} skip")


if __name__ == "__main__":
    main()
