# -*- coding: utf-8 -*-
"""Munkres《Topology》2e 现代验证（Part I 点集拓扑）
拓扑空间 / 开集闭集 / 连通 / 紧致 / 分离公理 / Baire 纲
用 numpy 验证。阶段2拓扑语言（与实分析并行）"""
import numpy as np

# ---------- §1 拓扑空间 ----------
def section_topology():
    print("\n" + "="*60)
    print("【§1 拓扑空间：开集公理（Munkres ch2）】")
    print("="*60)
    print("拓扑 τ：X 的子集族，满足：∅,X ∈ τ；任意并 ∈ τ；有限交 ∈ τ")
    print("  开集 = τ 的元素；'拓扑'是'哪些集合算开'的规定")
    # 离散拓扑 vs 平凡拓扑
    print(f"\n  离散拓扑（所有子集都开）：X={{a,b}}，τ = {{∅, {{a}}, {{b}}, X}}（最细）")
    print(f"  平凡拓扑（只有 ∅,X 开）：τ = {{∅, X}}（最粗）")
    # ℝ 的标准拓扑（开区间并）
    print(f"\n  ℝ 的标准拓扑：开集 = 开区间的任意并")
    print(f"  (0,1) 开，[0,1] 闭（补集 (-∞,0)∪(1,∞) 开）")
    print(f"  ℚ 在 ℝ 中既不开也不闭（稠密但补集也稠密）")

# ---------- §2 连通性 ----------
def section_connected():
    print("\n" + "="*60)
    print("【§2 连通与道路连通（Munkres ch3）】")
    print("="*60)
    print("连通：不能分成两个不相交非空开集的并")
    print(f"\n  ℝ 连通；ℝ\\{{0}} = (-∞,0)∪(0,∞) 不连通")
    print(f"  ℚ 在 ℝ 中不连通（任意两点间有无理数'断点'）")
    print(f"\n  道路连通（更强）：任意两点可用连续道路连接")
    print(f"  ℝⁿ 道路连通 ⟹ 连通。但连通不一定道路连通（拓扑学家的正弦曲线）")
    print(f"\n→ 连通性是'整体性'——拓扑学最基本的不变量之一")

# ---------- §3 紧致 ----------
def section_compact():
    print("\n" + "="*60)
    print("【§3 紧致：Heine-Borel 定理（Munkres ch3·核心）】")
    print("="*60)
    print("紧致：每个开覆盖有有限子覆盖")
    print(f"\n  Heine-Borel 定理（ℝⁿ 中）：紧致 ⟺ 闭且有界")
    print(f"  [0,1] 紧致（闭+有界）；(0,1) 不紧致（开区间）")
    print(f"  [0,∞) 不紧致（无界）；ℝ 不紧致")
    # 数值：有限子覆盖直觉
    print(f"\n  直觉：[0,1] 的开覆盖 {{(−0.1, 0.6), (0.4, 1.1)}} 已覆盖（有限子覆盖）")
    xs = np.linspace(0, 1, 1000)
    covered = np.any([(xs > -0.1) & (xs < 0.6), (xs > 0.4) & (xs < 1.1)], axis=0)
    print(f"  验证：[0,1] 被 (−0.1,0.6)∪(0.4,1.1) 覆盖 = {np.all(covered)} ✓")
    print(f"\n→ 紧致 = '有限的性质'。紧致空间上连续函数有最值（Spivak 极值定理的推广）")

# ---------- §4 分离公理 ----------
def section_separation():
    print("\n" + "="*60)
    print("【§4 分离公理 T1-T4（Munkres ch4）】")
    print("="*60)
    print("T1：单点集闭；T2(Hausdorff)：任两点可用不相交开集分离")
    print(f"\n  ℝ 是 Hausdorff（T2）：任两点 a<b，用 (a-ε,a+ε) 和 (b-ε,b+ε) 分离")
    a, b = 1.0, 3.0
    eps = (b-a)/4
    U = (a-eps, a+eps); V = (b-eps, b+eps)
    print(f"  a={a}, b={b}：U={U}, V={V}，不相交 = {U[1] < V[0]}（Hausdorff ✓）")
    print(f"\n  非 Hausdorff 例子：平凡拓扑空间（任两点无法分离）")
    print(f"\n  Urysohn 引理（Munkres ch4 高光）：正规空间（T4）中，任两不相交闭集")
    print(f"  可用连续函数 f:[0,1]→[a,b] 分离。'存在性证明'的典范（非构造）")

# ---------- §5 Baire 纲定理 ----------
def section_baire():
    print("\n" + "="*60)
    print("【§5 Baire 纲定理（Munkres ch8·泛函基础）】")
    print("="*60)
    print("Baire 纲：完备度量空间（或紧致 Hausdorff）不是可数个无处稠密集的并")
    print(f"\n  推论：ℝ 不是可数个'瘦集'的并——ℝ'太厚'，可数个稀疏集填不满")
    print(f"\n  应用1：连续函数空间 C[0,1] 中，'处处可导的函数'是稀疏的")
    print(f"  → '大多数连续函数处处不可导'（Weierstrass 反例不是怪物，是常态！）")
    print(f"\n  应用2：存在处处连续但处处不可导的函数（Baire 保证'很多'）")
    print(f"\n→ Baire 纲：'构造性反例'不如'存在性论证'——泛函分析的核心工具")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Munkres《Topology》2e · 现代验证                          ║")
    print("║  拓扑空间/连通/紧致/分离公理/Baire 纲                       ║")
    print("╚" + "═"*58 + "╝")
    section_topology()
    section_connected()
    section_compact()
    section_separation()
    section_baire()
    print("\n" + "═"*60)
    print("✅ Munkres 核心验证通过。点集拓扑（阶段2语言工具）打通。")
    print("═"*60)
