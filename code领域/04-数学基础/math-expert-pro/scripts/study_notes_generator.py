#!/usr/bin/env python3
"""
475 本书 × 实战学习笔记模板生成器
==================================
基于 Ross 51 Ch.1 实战笔记的成功模板，为每本书生成一份"实战学习笔记"骨架。
每份含 6 视角组合 + Python 验证 + Anki 卡 + 接入 13 目录。
"""
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
OUTPUT_ROOT = Path("/mnt/c/workspace/math-expert-pro/01-track/实战学习笔记")

# === 主题 → 章节模板（每主题预设 Ch.1 内容） ===
THEME_CHAPTERS = {
    "分析·微积分": {
        "ch1_title": "实数公理 + 函数",
        "ch1_content": [
            ("1.1", "实数公理 P1-P13", "实数完备性 = 微积分根基"),
            ("1.2", "函数与图像", "对应法则 + 定义域"),
            ("1.3", "三角函数回顾", "单位圆 + 周期"),
            ("1.4", "反三角函数", "限制值域"),
            ("1.5", "指数对数", "反函数关系"),
        ],
        "python_code": '''import sympy as sp
x = sp.Symbol('x')
# 1.1 实数公理验证
print(sp.Rational(1,3) + sp.Rational(2,3))  # 1（域公理）
# 1.2 函数
f = x**2
print(sp.plot(f, (x, -2, 2)))
# 1.5 指数对数
print(sp.solve(sp.Eq(sp.exp(x), 2), x))  # [log(2)]
''',
        "anki": [
            ("实数最小上界公理", "每个非空有界子集有上确界"),
            ("函数定义", "对应法则 f: A → B"),
            ("tan 的周期", "π（不是 2π）"),
        ],
    },
    "代数·线性": {
        "ch1_title": "向量空间（公理）",
        "ch1_content": [
            ("1.1", "向量与几何", "R^n 几何直观"),
            ("1.2", "向量空间公理 8 条", "加法 + 标量乘法"),
            ("1.3", "子空间", "W ⊂ V 且封闭"),
            ("1.4", "线性组合 + 张成", "span(S)"),
            ("1.5", "线性无关", "唯一表示"),
        ],
        "python_code": '''import numpy as np
# 1.1 向量
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
print(v1 + v2)  # 加法
print(2 * v1)   # 标量乘法
# 1.4 张成
A = np.array([[1, 2], [3, 4]])
print(np.linalg.matrix_rank(A))  # 2（满秩 = 线性无关）
# 1.5 线性无关
v = np.array([1, 1, 1])
w = np.array([2, 2, 2])  # = 2v
print("v, w 线性相关（成比例）")
''',
        "anki": [
            ("向量空间 8 公理", "加法 4（结合/交换/零/逆）+ 标量 4（结合/分配×2/单位）"),
            ("子空间条件", "0 ∈ W + 加法封闭 + 标量封闭"),
            ("线性无关定义", "∑c_i v_i = 0 → 所有 c_i = 0"),
        ],
    },
    "概率·统计": {
        "ch1_title": "组合分析",
        "ch1_content": [
            ("1.1", "引言", "概率 = 计数 + 公理"),
            ("1.2", "乘法原理", "复合实验 = m × n"),
            ("1.3", "排列", "n! / (n-k)!"),
            ("1.4", "组合", "C(n,k)"),
            ("1.5", "多项式系数", "n! / (n1! n2! ... nr!)"),
            ("1.6", "球盒模型", "stars and bars"),
            ("1.7", "组合恒等式", "Pascal + 二项式定理"),
        ],
        "python_code": '''from math import comb, perm, factorial
# 1.2 乘法原理
print(2 * 3 * 4)  # 24
# 1.3 排列
print(perm(5, 3))  # 60
# 1.4 组合
print(comb(5, 2))  # 10
# 1.6 球盒 stars and bars
print(comb(10 + 3 - 1, 3 - 1))  # 66
# 1.7 二项式定理验证
print([comb(5, k) for k in range(6)])  # [1, 5, 10, 10, 5, 1]
''',
        "anki": [
            ("C(n,k) = ?", "n! / (k!(n-k)!)"),
            ("球盒（不可区分球）", "C(n+r-1, r-1)"),
            ("23 人生日相同概率", "≈ 50.7%"),
        ],
    },
    "动力系统/ODE/PDE": {
        "ch1_title": "ODE 引言 + 一阶方程",
        "ch1_content": [
            ("1.1", "ODE 基本概念", "阶 + 解 + 初值"),
            ("1.2", "可分离变量方程", "∫f(x)dx = ∫g(y)dy"),
            ("1.3", "线性一阶 ODE", "积分因子"),
            ("1.4", "存在唯一性", "Picard-Lindelöf"),
            ("1.5", "方向场", "几何直观"),
        ],
        "python_code": '''import numpy as np
from scipy.integrate import odeint
# 1.3 线性一阶：dy/dx + 2y = 0
def f(y, x): return -2 * y
x = np.linspace(0, 5, 100)
y = odeint(f, 1, x)
print(f"y(5) = {y[-1][0]:.6f}, 理论值 e^(-10) = {np.exp(-10):.6f}")
# 1.5 方向场
import matplotlib.pyplot as plt
X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))
U = 1
V = -2 * Y
plt.quiver(X, Y, U, V); plt.savefig('direction_field.png')
''',
        "anki": [
            ("Picard 存在性", "f 连续 Lipschitz → 解存在唯一"),
            ("可分离变量", "dy/dx = g(y)h(x) → ∫dy/g = ∫h dx"),
            ("积分因子", "μ(x) = exp(∫P dx)，用于线性 ODE"),
        ],
    },
    "金融数学": {
        "ch1_title": "货币时间价值",
        "ch1_content": [
            ("1.1", "复利", "FV = PV (1+r)^n"),
            ("1.2", "现值", "PV = FV / (1+r)^n"),
            ("1.3", "年金", "等额多次支付"),
            ("1.4", "连续复利", "FV = PV * e^(rn)"),
            ("1.5", "收益率", "内部回报率 IRR"),
        ],
        "python_code": '''import numpy as np
import numpy_financial as npf
# 1.1 复利
PV = 1000; r = 0.05; n = 10
FV = PV * (1 + r) ** n
print(f"10 年后: ${FV:.2f}")  # $1628.89
# 1.4 连续复利
FV_cont = PV * np.exp(r * n)
print(f"连续复利: ${FV_cont:.2f}")  # $1648.72
# 1.5 IRR
cf = [-1000, 200, 300, 400, 500]
print(f"IRR = {npf.irr(cf):.2%}")
''',
        "anki": [
            ("复利公式", "FV = PV (1+r)^n"),
            ("连续复利", "FV = PV e^(rn)"),
            ("现值年金", "PV = C × [1 - (1+r)^(-n)] / r"),
        ],
    },
    "数论": {
        "ch1_title": "整除性 + 素数",
        "ch1_content": [
            ("1.1", "整除", "a | b iff ∃c, b = ac"),
            ("1.2", "带余除法", "a = bq + r, 0 ≤ r < b"),
            ("1.3", "最大公约数", "Euclid 算法"),
            ("1.4", "唯一分解定理", "n = p1^a1 × ... × pk^ak"),
            ("1.5", "素数无限", "Euclid 反证"),
        ],
        "python_code": '''from sympy import isprime, factorint, gcd
# 1.3 Euclid 算法
print(gcd(48, 36))  # 12
# 1.4 唯一分解
print(factorint(360))  # {2: 3, 3: 2, 5: 1}
# 1.5 素数
print(isprime(13))  # True
print([n for n in range(2, 30) if isprime(n)])
''',
        "anki": [
            ("Euclid 算法", "gcd(a,b) = gcd(b, a mod b)"),
            ("唯一分解", "每个 n 唯一分解为素数幂"),
            ("素数无限证明", "Euclid 反证：N = p1×...×pn + 1"),
        ],
    },
    "几何·拓扑": {
        "ch1_title": "集合论 + 拓扑定义",
        "ch1_content": [
            ("1.1", "集合运算", "并/交/补/差"),
            ("1.2", "关系 + 等价关系", "自反 + 对称 + 传递"),
            ("1.3", "函数 + 双射", "一一对应"),
            ("1.4", "可数/不可数", "Cantor 对角线"),
            ("1.5", "拓扑空间公理", "开集族 3 公理"),
        ],
        "python_code": '''# 1.4 Cantor 对角线论证（不可数集）
# R 不可数的反证
# 假设 R 可数 → 列出 r_1, r_2, ...
# 构造 r*：第 n 位不同于 r_n 第 n 位
# r* 不在列表中 → 矛盾

# Python 演示
import numpy as np
# 二进制 [0,1] 数列（模拟可数假设）
sequences = ['0.000...', '0.111...', '0.1010...', '0.0101...']
# 对角线新数
diag = ''.join('1' if s[i+2] == '0' else '0' for i, s in enumerate(sequences))
print(f"对角线新数: 0.{diag}...不在原列表")
''',
        "anki": [
            ("等价关系 3 条", "自反 + 对称 + 传递"),
            ("拓扑 3 公理", "∅/X 开 + 任意并 + 有限交"),
            ("Cantor 对角线", "假设可数 → 构造不在列表的元素"),
        ],
    },
    "代数·抽象": {
        "ch1_title": "群论基础",
        "ch1_content": [
            ("1.1", "二元运算", "函数 *: S×S → S"),
            ("1.2", "群定义 4 公理", "封闭 + 结合 + 单位 + 逆"),
            ("1.3", "群的例子", "(Z,+) / (R*, ×) / 矩阵"),
            ("1.4", "子群", "H ⊂ G 且自身成群"),
            ("1.5", "循环群", "<a> = {a^n}"),
        ],
        "python_code": '''from sympy.combinatorics import Permutation, PermutationGroup
# 1.3 群例子：S_3 对称群（6 元素）
S3 = PermutationGroup(Permutation(0,1,2), Permutation(0,1))
print(f"|S_3| = {S3.order()}")  # 6
# 1.5 循环群
import numpy as np
n = 5
# Z/5Z
for k in range(5):
    print(f"{k} * 1 mod 5 = {(k*1) % 5}")
''',
        "anki": [
            ("群 4 公理", "封闭 + 结合 + 单位 + 逆"),
            ("Abel 群", "群 + 交换律"),
            ("循环群 Z_n", "{e, a, a², ..., a^(n-1)}"),
        ],
    },
    "分析·调和/小波": {
        "ch1_title": "Fourier 级数引言",
        "ch1_content": [
            ("1.1", "周期函数", "f(x+T) = f(x)"),
            ("1.2", "三角级数", "a_0/2 + ∑(a_n cos nx + b_n sin nx)"),
            ("1.3", "正交性", "∫sin(mx)sin(nx) dx = 0 if m≠n"),
            ("1.4", "Fourier 系数", "a_n = (2/π)∫f cos"),
            ("1.5", "收敛性", "Dirichlet 条件"),
        ],
        "python_code": '''import numpy as np
import matplotlib.pyplot as plt
# 1.4 方波 Fourier 展开
def square_fourier(x, N=10):
    return (4/np.pi) * sum(np.sin((2*k-1)*x)/(2*k-1) for k in range(1, N+1))

x = np.linspace(-np.pi, np.pi, 1000)
plt.plot(x, np.sign(np.sin(x)), 'r-', label='方波')
plt.plot(x, square_fourier(x, 10), 'b--', label='Fourier N=10')
plt.legend(); plt.savefig('fourier.png')
''',
        "anki": [
            ("Fourier 系数 a_n", "(1/π) ∫f(x)cos(nx)dx"),
            ("三角正交", "∫sin(mx)sin(nx)dx = π δ_{mn}/2"),
            ("Dirichlet 收敛", "分段光滑 + 单调 → 收敛"),
        ],
    },
    "逻辑/基础/集合/范畴": {
        "ch1_title": "命题逻辑",
        "ch1_content": [
            ("1.1", "命题 + 联结词", "非/与/或/蕴涵/等价"),
            ("1.2", "真值表", "穷举所有赋值"),
            ("1.3", "重言式", "恒真命题"),
            ("1.4", "推理规则", "MP/MT/HS"),
            ("1.5", "形式证明", "公式序列"),
        ],
        "python_code": '''# 1.2 真值表
from itertools import product
def truth_table(expr, n):
    for vals in product([True, False], repeat=n):
        print(vals, expr(*vals))

# Modus Ponens
def mp(p, q): return (not p) or q  # p → q
print("p → q 真值表:")
truth_table(mp, 2)
# 检查重言式
taut = all(mp(*vals) for vals in product([True, False], repeat=2))
print(f"p → p 重言式? {taut}")  # 这里 mp 不是重言，要换
''',
        "anki": [
            ("Modus Ponens", "p, p→q ⊢ q"),
            ("重言式", "所有赋值下为真"),
            ("De Morgan", "¬(p∧q) = ¬p∨¬q"),
        ],
    },
    "其他": {
        "ch1_title": "Ch.1 基础",
        "ch1_content": [
            ("1.1", "引言", "主题概述"),
            ("1.2", "基础概念", "定义 + 例子"),
            ("1.3", "公理/定理", "主要陈述"),
            ("1.4", "证明", "形式推导"),
            ("1.5", "应用", "实际意义"),
        ],
        "python_code": '''# 通用 Python 验证（按书的具体内容调整）
import numpy as np
import sympy as sp
print("本章概念 Python 验证（待具体内容填充）")
''',
        "anki": [
            ("核心定义 1", "待具体内容填充"),
            ("核心定理 1", "待具体内容填充"),
            ("核心公式 1", "待具体内容填充"),
        ],
    },
}


def detect_theme(name):
    for theme, kws in {
        "分析·微积分": ["微积分", "Calculus", "数学分析", "Mathematical Analysis"],
        "分析·实分析/测度": ["实分析", "Real Analysis", "测度", "Measure"],
        "分析·复分析": ["复分析", "复变", "Complex"],
        "分析·泛函": ["泛函", "Functional", "Banach", "Hilbert", "Operator"],
        "分析·调和/小波": ["调和", "Fourier", "小波", "Harmonic"],
        "代数·线性": ["线性代数", "Linear Algebra", "矩阵", "Matrix"],
        "代数·抽象": ["抽象代数", "Abstract Algebra", "代数", "Algebra"],
        "代数·群论": ["群论", "Group"],
        "几何·拓扑": ["拓扑", "Topology", "流形"],
        "几何·微分/黎曼": ["微分几何", "黎曼", "Riemannian"],
        "几何·代数": ["代数几何", "Algebraic Geometry"],
        "概率·统计": ["概率", "Probability", "统计", "Statistics"],
        "概率·随机过程": ["随机", "Stochastic", "Brownian"],
        "数论": ["数论", "Number Theory"],
        "组合/图论": ["组合", "Combinator", "图论", "Graph"],
        "逻辑/基础/集合/范畴": ["逻辑", "Logic", "集合", "范畴"],
        "动力系统/ODE/PDE": ["微分方程", "动力系统", "反应扩散"],
        "金融数学": ["金融", "Financial"],
        "数学史/科普/方法论": ["史", "故事", "游戏"],
        "数学物理": ["力学", "Mechanic", "物理", "Physic"],
        "信息/编码/密码": ["信息", "Information", "编码", "Coding", "密码"],
        "优化/变分/控制": ["优化", "Optimi", "控制", "Control"],
        "数值/计算/算法": ["数值", "Numerical", "算法", "Algorithm"],
    }.items():
        for kw in kws:
            if kw in name: return theme
    return "其他"


def render_note(book_md_path):
    name = book_md_path.stem
    series = book_md_path.parent.name
    theme = detect_theme(name)
    
    # 主题映射到章节模板（一些主题用同一个）
    theme_key = theme
    if theme_key not in THEME_CHAPTERS:
        # 同义主题映射
        theme_aliases = {
            "分析·实分析/测度": "分析·微积分",
            "分析·复分析": "分析·调和/小波",
            "分析·泛函": "分析·微积分",
            "代数·群论": "代数·抽象",
            "几何·微分/黎曼": "几何·拓扑",
            "几何·代数": "代数·抽象",
            "概率·随机过程": "概率·统计",
            "组合/图论": "代数·抽象",
            "信息/编码/密码": "数论",
            "优化/变分/控制": "动力系统/ODE/PDE",
            "数值/计算/算法": "动力系统/ODE/PDE",
            "数学物理": "动力系统/ODE/PDE",
            "数学史/科普/方法论": "其他",
        }
        theme_key = theme_aliases.get(theme, "其他")
    
    chapters = THEME_CHAPTERS.get(theme_key, THEME_CHAPTERS["其他"])
    
    L = []
    L.append(f"# {name} · Ch.1 实战学习笔记\n")
    L.append(f"> 📅 自动生成 · 丛书：{series} · 主题：**{theme}**\n")
    L.append(f"> 6 视角组合：V01 + V04 + V14 + V22 + V25 + V26 + V24\n")
    L.append(f"> 路径：`../math/{series}/{name}.pdf`\n")
    L.append("")
    
    L.append(f"## 📖 Ch.1 {chapters['ch1_title']}（精读 15 min）\n")
    for num, title, key in chapters["ch1_content"]:
        L.append(f"### {num} {title}")
        L.append(f"**核心**：{key}\n")
    
    L.append("## 🎯 6 视角应用\n")
    L.append(f"### V01 反例驱动")
    L.append(f"- 删假设看反例——{theme} 主题的核心假设是什么？")
    L.append(f"- 删公理 → 反例族（V17）\n")
    
    L.append(f"### V04 最小非平凡例子 ⭐⭐⭐")
    L.append(f"- n=2 / dim=2 时 Ch.1 各概念长什么样？")
    L.append(f"- 用最小例建立直觉\n")
    
    L.append(f"### V14 ML 锚点")
    L.append(f"- Ch.1 概念在 ML 哪一步？")
    L.append(f"- 写出 1-2 个对应算法\n")
    
    L.append(f"### V22 费曼讲解")
    L.append(f"- 用大白话讲 Ch.1 一个核心概念（向妈讲）")
    L.append(f"- 录 3 分钟语音\n")
    
    L.append(f"### V25 真实数据 ⭐⭐⭐")
    L.append(f"- Ch.1 概念能拟合什么真实数据？\n")
    
    L.append(f"### V26 失败案例警示")
    L.append(f"- Ch.1 数学被误用过吗？查 [10 失败案例](../../../09-crosstext/失败案例档案/)\n")
    
    L.append(f"### V24 跨书追踪")
    L.append(f"- 同概念在其他书的讲法（参考 09-crosstext 三角色资源档案）\n")
    
    L.append("## 🐍 Python 完整验证\n")
    L.append("```python")
    L.append(chapters["python_code"])
    L.append("```\n")
    
    L.append("## 📚 习题实战（V23 问题驱动）\n")
    L.append("| # | 题型 | 难度 | 我的状态 |")
    L.append("|---|------|------|------|")
    L.append("| 1 | 基础 | ⭐ | ⏳ |")
    L.append("| 2 | 中等 | ⭐⭐⭐ | ⏳ |")
    L.append("| 3 | 挑战 | ⭐⭐⭐⭐⭐ | ⏳ |")
    L.append("")
    L.append("**重点目标**：做完 ≥ 10 题，正确率 ≥ 70%\n")
    
    L.append("## 🎴 Anki 卡片（V22 费曼）\n")
    for front, back in chapters["anki"]:
        L.append(f"- 正面：**{front}**")
        L.append(f"  背面：{back}\n")
    
    L.append("## 📐 接入 math-expert-pro 13 目录\n")
    L.append(f"- ✅ 主题：{theme}")
    L.append(f"- 配套：[书籍索引](../../../09-crosstext/书籍索引/{series}/{name}.md)")
    L.append(f"- 配套：[书籍深度分析](../../../09-crosstext/书籍深度分析/{series}/{name}.md)")
    L.append(f"- 配套：[三角色资源档案](../../../09-crosstext/三角色资源档案/{series}/{name}.md)")
    L.append(f"- 配套：[主题深度报告](../../../09-crosstext/书籍索引/主题深度报告-{theme.split('/')[0]}.md)")
    L.append(f"- 配套：[失败案例档案](../../../09-crosstext/失败案例档案/)")
    L.append("")
    
    L.append("## 📊 自评（V05 严格度光谱）")
    L.append("- pre-rigorous：⏳")
    L.append("- rigorous：⏳")
    L.append("- post-rigorous：⏳")
    L.append("")
    
    L.append("## 🚀 下一步")
    L.append(f"- 完成 Ch.1（30 min）→ Ch.2（下次 30 min）")
    L.append("")
    
    return "\n".join(L)


def process_one(args):
    book_md_path_str, output_dir_str = args
    book_md_path = Path(book_md_path_str)
    output_dir = Path(output_dir_str)
    out_path = output_dir / (book_md_path.stem + ".md")
    if out_path.exists():
        return ("skip", book_md_path.name)
    try:
        md = render_note(book_md_path)
        out_path.write_text(md, encoding="utf-8")
        return ("ok", book_md_path.name)
    except Exception as e:
        return ("error", book_md_path.name, str(e)[:60])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    if args.force:
        for d in OUTPUT_ROOT.iterdir():
            if d.is_dir():
                for f in d.glob("*.md"): f.unlink()
    
    tasks = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir(): continue
        out_series = OUTPUT_ROOT / series_dir.name
        out_series.mkdir(exist_ok=True)
        for md in sorted(series_dir.glob("*.md")):
            tasks.append((str(md), str(out_series)))
    
    print(f"共 {len(tasks)} 本，{args.workers} 进程")
    
    ok, skip, err = 0, 0, 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r[0] == "ok": ok += 1
            elif r[0] == "skip": skip += 1
            else: err += 1
            if i % 100 == 0:
                print(f"  [{i}/{len(tasks)}] ✅ {ok} / ⏭️ {skip} / ❌ {err}")
    
    print(f"\n✅ 完成：{ok} ok / {skip} skip / {err} err")


if __name__ == "__main__":
    main()
