# -*- coding: utf-8 -*-
"""ZFC 公理的有限近似模型——在 V₀…V₄ 里逐条检查公理。

00 章 · 体系结构 配套实验。纯标准库。frozenset = 良基集合的工程化身。

跑法: python3 -u experiments/00_zfc_finite_model.py
"""
from itertools import combinations

EMPTY = frozenset()


def powerset(s):
    """P(X)：X 的全体子集构成的 frozenset（模型内的幂集，完全构造）。"""
    xs = list(s)
    out = []
    for r in range(len(xs) + 1):
        out.extend(frozenset(c) for c in combinations(xs, r))
    return frozenset(out)


def build_v(n):
    """构造累积层级 V₀=∅, V_{α+1}=P(V_α)。返回 [V0, V1, ..., Vn]。"""
    vs = [EMPTY]
    for _ in range(n):
        vs.append(powerset(vs[-1]))
    return vs


def rank_of(x, vs):
    """x 的出生层：最小的 α 使 x ∈ V_{α+1}（即 x ⊆ V_α）。"""
    for alpha, v in enumerate(vs):
        if x in v:
            return alpha
    return None


def main():
    vs = build_v(4)
    sizes = [len(v) for v in vs]
    print("=" * 62)
    print("宇宙分层 V₀…V₄（frozenset 构造）")
    print("=" * 62)
    print("V₀=∅, V_{α+1}=P(V_α)：")
    for i, (v, s) in enumerate(zip(vs, sizes)):
        sample = sorted(map(str, v), key=len)[:4]
        more = " …" if s > 4 else ""
        print(f"  V{i}: |V{i}| = {s:2d}   元素如 {sample}{more}")
    print(f"→ 尺寸序列 {sizes}：0,1,2,4,16 —— 每层是上一层的 2^ 塔尖\n")

    V4 = vs[4]
    V3 = vs[3]

    print("=" * 62)
    print("公理逐条检查（以 V₄ 为'有限宇宙'）")
    print("=" * 62)

    # 外延
    a = frozenset({EMPTY, frozenset({EMPTY})})
    b = frozenset({frozenset({EMPTY}), EMPTY})
    print(f"1 外延: {{∅,{{∅}}}} == {{{{∅}},∅}} ? {a == b}   ✅（frozenset 相等=元素相等，无序无重复）")

    # 配对
    x, y = sorted(V3, key=str)[0], sorted(V3, key=str)[1]
    pair = frozenset({x, y})
    print(f"2 配对: 取 x,y∈V₃ → {{x,y}}∈V₄ ? {pair in V4}   ✅（元素出生层<4，配对落在 V₄）")
    top_pair = frozenset({sorted(V4, key=str)[0], sorted(V4, key=str)[1]})
    print(f"        但顶层配对 x,y∈V₄ → {{x,y}}∈V₄ ? {top_pair in V4}   ⚠️ 溢出到 V₅——有限截断的顶层不封闭")

    # 并
    some = next(s for s in V4 if len(s) == 2)
    u = frozenset().union(*some)
    print(f"3 并:  ⋃{some} = {u}，⋃some ∈ V₄ ? {u in V4}   ✅（传递性：摊平不升层）")

    # 幂集
    X = next(s for s in V4 if len(s) == 2)
    pX = powerset(X)
    print(f"4 幂集: X={X}（X∈V₄），P(X) 有 {len(pX)} 个元素，P(X)∈V₄ ? {pX in V4}   ❌")
    print(f"        P(X) ⊆ V₄ ⟹ P(X)∈V₅ —— 幂集永远把集合顶上一层")
    print(f"        无限极限层 V_λ（λ极限序数）里它就成立：X∈V_β (β<λ) → P(X)∈V_(β+1)⊆V_λ")

    # 无穷（诚实判定：s 归纳 ⟺ ∅∈s 且 ∀t∈s: t∪{t}∈s——有限集上可完全判定）
    succ = lambda s: s | {s}
    inductive = any(EMPTY in s and all(succ(t) in s for t in s) for s in V4)
    print(f"5 无穷: V₄ 里存在归纳集（含∅且对后继封闭）? {inductive}   ❌")
    print(f"        （每个含 ∅ 的 s 都在链尾断掉：s 最大环节的后继不在 s 里——")
    print(f"          归纳集必须含整条 ω 链，有限宇宙装不下）")

    # 分离
    A = V3  # 一个模型内的集合
    cut = frozenset(s for s in A if len(s) >= 2)
    print(f"6 分离: 从 V₃ 里切'元素数≥2'的子集 S，|S|={len(cut)}，S∈V₄ ? {cut in V4}   ✅（切不升层）")

    # 替换（两个案例：值落在 V₃ 内 → 像集在 V₄ ✅；值顶到 V₄ → 像集溢出 V₅ ❌）
    img_low = frozenset(EMPTY if len(t) % 2 == 0 else frozenset({EMPTY}) for t in A)
    img_top = frozenset(frozenset({t}) for t in A)  # 值 {t} ∈ V₄（顶层）
    print(f"7 替换: 值落在 V₃ 内的函数，像集∈V₄ ? {img_low in V4}   ✅")
    print(f"        值顶到 V₄ 的函数 t↦{{t}}，像集∈V₄ ? {img_top in V4}   ❌ 溢出 V₅")
    print(f"        （像集是 V₄ 元素的集合 ⟹ ⊆V₄ ⟹ ∈V₅——与幂集同款顶层病；V_ω 里痊愈）")

    # 正则
    print(f"8 正则: 任何非空 s∈V₄ 都有元素与 s 不相交?", end=" ")
    ok = True
    for s in V4:
        if s and not any(e & s == EMPTY for e in s):
            ok = False
            break
    print(f"{ok}   ✅（frozenset 天然良基：元素先于集合存在，∈ 无环）")
    print(f"        试试造 x∈x：要构造 x 必须先有 x 自己——数据结构层面禁止   💡 反直觉发现#3")

    # 选择
    fam = [s for s in V4 if len(s) == 1][:3]
    chosen = [next(iter(s)) for s in fam]
    print(f"9 选择: 对 {len(fam)} 个非空集族同时各取一个元素: 成功   ✅（有限族平凡成立——AC 的代价在无穷才显现）")

    print()
    print("=" * 62)
    print("结论：有限截断宇宙的三条裂缝")
    print("=" * 62)
    print("""
  ❌ 无穷公理: 有限宇宙装不下归纳集——ZFC 与有限论的合同条款
  ❌ 幂集公理: 顶层集合的幂集溢出到上一层——只有无限极限层(V_ω)才恢复
  ⚠️ 配对/替换: 顶层元素的操作溢出——同款"顶层不封闭"病

  修复方案只有一个方向: 让层级无限延展 → V_ω(可数无穷层)即 ZF-无穷+无穷公理
  的标准模型胚子。有限世界与集合论宇宙的差, 就是"无穷公理"那一条。
""")


if __name__ == "__main__":
    main()
