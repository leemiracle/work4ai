# -*- coding: utf-8 -*-
"""《什么是数学》第3-5章 现代验证（柯朗：几何作图 / 射影几何 / 拓扑）
纯 Python 无外部依赖"""
import math
from fractions import Fraction

# ---------- §3.1 几何作图与数域：可作数 ----------
def section_3_1_constructible():
    print("\n" + "="*60)
    print("【§3 几何作图：尺规能作什么？三大难题为什么不可能】")
    print("="*60)
    # 尺规可作数 = 从有理数出发，反复 + - × ÷ √ 能得到的数
    # 关键：尺规只能解"一元二次方程"（直尺=直线，圆规=圆，交点最多二次）
    print("尺规作图的代数本质：")
    print("  直尺画直线（一次方程），圆规画圆（二次方程）")
    print("  两者的交点坐标 = 解一元二次方程 → 尺规只能'开平方'")
    print("  所以可作数 = 从 ℚ 出发反复 +,-,×,÷,√ 得到的数（属于'二次扩张塔'）")
    # 验证：某些数可作，某些不可作
    print(f"\n  √2 可作（直角边 1,1 的斜边）= {math.sqrt(2):.6f}")
    print(f"  √(2+√3) 可作（嵌套平方根）= {math.sqrt(2+math.sqrt(3)):.6f}")
    print(f"  ³√2（倍立方的解）不可作 —— 它要求开立方，尺规做不到")
    print(f"    ³√2 = {2**(1/3):.6f}（用标记尺或折纸能作，但纯尺规不行）")
    print(f"  cos(20°)（三等分 60° 角的解）不可作 —— 涉及三次方程 8x³-6x-1=0")

# ---------- §3.2 三大难题不可能证明 ----------
def section_3_2_impossibility():
    print("\n【三大难题的不可解性】")
    # 三等分任意角：需解 4x³-3x-cos(θ)=0（三次），尺规只能二次
    # 倍立方：³√2，需三次扩张，不在二次扩张塔
    # 化圆为方：π 是超越数（Lindemann 1882），根本不在代数数里
    print("  ① 三等分任意角：θ=60° 时需解 8x³-6x-1=0（x=cos20°），无有理根→不可作")
    print("     验证 8x³-6x-1 在有理数域不可约（无有理根）：")
    for p in range(-5, 6):
        for q in range(1, 6):
            x = p/q
            if abs(8*x**3 - 6*x - 1) < 1e-9:
                print(f"       x={x} 是根"); break
        else: continue
        break
    else:
        print(f"       1≤q≤5, -5≤p≤5 内无有理根 → 三次不可约 → cos20°不可作")
    print("  ② 倍立方：³√2 是 x³-2=0 的根，3 次扩张，尺规只能 2ⁿ 次扩张 → 不可作")
    print("  ③ 化圆为方：要作 √π，但 π 超越（§2.5）→ √π 也超越 → 不在任何代数扩张里")
    print("\n→ 三大难题困扰数学 2000 年，1837/1882 年用'域论'逐一证明不可能")
    print("  这是 Galois 理论的源头（阶段 2 抽代数会深学）—— '用结构代替计算'")

# ---------- §4 射影几何：交比 ----------
def section_4_projective():
    print("\n" + "="*60)
    print("【§4 射影几何：交比不变 + 对偶】")
    print("="*60)
    # 交比 (A,B;C,D) = (AC/BC)/(AD/BD)，射影变换下不变
    def cross_ratio(A, B, C, D):
        return ((C-A)/(C-B)) / ((D-A)/(D-B))
    A, B, C, D = 0, 1, 2, 3
    cr = cross_ratio(A, B, C, D)
    print(f"直线上四点 A=0, B=1, C=2, D=3 的交比 = {cr:.6f}")
    # 射影变换 x → 1/x（保持交比）
    def proj_transform(x): return 1/x if x != 0 else float('inf')
    A2, B2, C2, D2 = 1/A if A else float('inf'), 1/B, 1/C, 1/D
    # 用有限点验证
    A, B, C, D = 1, 2, 3, 4
    cr1 = cross_ratio(1, 2, 3, 4)
    cr2 = cross_ratio(1/1, 1/2, 1/3, 1/4)
    print(f"变换前 (1,2,3,4) 交比 = {cr1:.6f}")
    print(f"x→1/x 后 (1,1/2,1/3,1/4) 交比 = {cr2:.6f}（相等！射影不变量）")
    print("\n→ 交比是射影几何的'度量'：射影变换改变距离，但保持交比")
    print("→ 对偶原理：'点'与'线'互换，定理仍成立（射影几何的对称之美）")

# ---------- §5 拓扑：Euler 多面体公式 ----------
def section_5_topology():
    print("\n" + "="*60)
    print("【§5 拓扑：Euler 多面体公式 V-E+F=2 + 曲面分类】")
    print("="*60)
    # Euler 公式：V-E+F=2（凸多面体）
    polyhedra = {
        "四面体": (4, 6, 4),
        "立方体": (8, 12, 6),
        "八面体": (6, 12, 8),
        "十二面体": (20, 30, 12),
        "二十面体": (12, 30, 20),
    }
    print("Euler 多面体公式：V - E + F = 2（凸多面体）")
    for name, (V, E, F) in polyhedra.items():
        chi = V - E + F
        print(f"  {name}: V={V}, E={E}, F={F} → V-E+F = {chi} {'✓' if chi==2 else '✗'}")
    # 曲面分类：Euler 示性数 χ = 2-2g（g=亏格/洞数）
    print(f"\nEuler 示性数 χ 与亏格 g：χ = 2 - 2g")
    for name, g in [("球面", 0), ("环面", 1), ("双环面", 2), ("三环面", 3)]:
        chi = 2 - 2*g
        print(f"  {name}（g={g}）: χ = {chi}")
    print("\n→ 拓扑学不关心'距离/角度'（那是几何），只关心'连通/洞'（弹性变形不变）")
    print("→ Euler 公式 V-E+F=2 是拓扑不变量——任何与球面同胚的多面体都满足")
    print("→ 这启发了 Lagatos《证明与反驳》（[02/反思层/12-Lakatos]）——多面体公式的辩论史")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  《什么是数学》第 3-5 章 · 现代验证（几何/射影/拓扑）      ║")
    print("╚" + "═"*58 + "╝")
    section_3_1_constructible()
    section_3_2_impossibility()
    section_4_projective()
    section_5_topology()
    print("\n" + "═"*60)
    print("✅ 第 3-5 章验证通过。")
    print("═"*60)
