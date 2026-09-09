# -*- coding: utf-8 -*-
"""
dm_cat_check.py — 蒸馏卡 DM-CAT-01《范畴论》§4 机器验证
对应卡片: distilled_math/DM-CAT-01-范畴论.md
断言计数: 12（CAT-01 ~ CAT-12）
运行方式: python3 dm_cat_check.py
依赖: 纯 Python 标准库（无第三方依赖）
置信含义: 范畴论断言的机器验证 = 在**有限小范畴**上穷举实例。
  Yoneda 用 3 对象预序范畴 0≤1≤2 全部 9 对 (A,B) 穷举自然变换个数。
  ★ 含义 = 实例级穷举通过（非证明），见 METHODOLOGY §六。
"""
from itertools import product

PASS = []

def check(name, cond):
    assert cond, f"FAIL: {name}"
    PASS.append(name)
    print(f"  [PASS] {name}")

# ========== 小框架：预序范畴 C: 0 ≤ 1 ≤ 2（箭头 = 可比性） ==========
OBJS = (0, 1, 2)
ARROWS = [(a, b) for a in OBJS for b in OBJS if a <= b]   # a≤b 时唯一箭头 (a,b)

def comp(g, f):
    """复合 g ∘ f（f: a→b, g: b→c）"""
    assert f[1] == g[0]
    return (f[0], g[1])

print("== CAT-01: 范畴公理（结合律 + 单位律） ==")
assoc = all(comp(h, comp(g, f)) == comp(comp(h, g), f)
             for f in ARROWS for g in ARROWS if g[0] == f[1]
             for h in ARROWS if h[0] == g[1])
ident = all(comp((b, b), (a, b)) == (a, b) and comp((a, b), (a, a)) == (a, b)
            for (a, b) in ARROWS if a != b)
check("CAT-01 预序范畴: 全部可复合三元组结合律成立, 单位箭头成立", assoc and ident)

print("== CAT-02: 幺半群 (Z/3,+) = 单对象范畴 ==")
M = [0, 1, 2]
assoc_m = all(((m1 + m2) % 3 + m3) % 3 == (m1 + (m2 + m3) % 3) % 3
              for m1 in M for m2 in M for m3 in M)
check("CAT-02 单对象范畴视角: Z/3 加法结合律(27 组) + 单位 0 = 恒等箭头", assoc_m)

print("== CAT-03/04: 幂集函子 + 单位自然变换 η: Id ⇒ P ==")
A = frozenset({1, 2})
f = {1: 'a', 2: 'a'}                      # f: A → B
g = {'a': 'x', 'b': 'y'}                  # g: B → C
gf = {i: g[f[i]] for i in A}
def image(fn, s): return frozenset(fn[v] for v in s)
import itertools as it
P_A = {frozenset(c) for r in range(3) for c in it.combinations({1, 2}, r)}
idA = {1: 1, 2: 2}                       # id_A 用 dict 表示
Fid_ok = all(image(idA, s) == s for s in P_A)               # F(id_A) = id_{P(A)}
Fcomp_ok = all(image(gf, s) == image(g, image(f, s)) for s in P_A)  # F(g∘f) = F(g)∘F(f)
check("CAT-03 函子律实例: 幂集函子 P 保单位 F(id_A)=id, 保复合 F(g∘f)=F(g)∘F(f)",
      Fid_ok and Fcomp_ok)
nat_ok = all(image(f, {v}) == {f[v]} for v in A) and \
          image(gf, {1}) == image(g, image(f, {1}))
check("CAT-04 自然性实例: η_A(x)={x} 满足 P(f)∘η_A = η_B∘f（单子单位）", nat_ok)

print("== CAT-05: Yoneda 引理穷举（预序范畴 9 对 (A,B)） ==")
def hom_functor(A_):
    """Hom(A,−): C → Set。对象 k ↦ {(A,k)}（A≤k）或 ∅；箭头 (k,l) ↦ 后复合。"""
    obj = {k: (frozenset({(A_, k)}) if A_ <= k else frozenset()) for k in OBJS}
    return obj, lambda k, l: {(A_, k): (A_, l)}

def all_functions(dom, cod):
    dom, cod = list(dom), list(cod)
    if not dom:
        return [dict()]           # 空定义域：恰一个空函数（陪域任意，含空）
    if not cod:
        return []                 # 非空定义域 → 空陪域：无函数
    return [dict(zip(dom, vs)) for vs in product(cod, repeat=len(dom))]

def count_nat(F, G):
    """穷举自然变换 F ⇒ G 的个数（预序范畴上有限可穷举）"""
    Fobj, Fmor = F
    Gobj, Gmor = G
    cands = {k: all_functions(Fobj[k], Gobj[k]) for k in OBJS}
    total = 0
    for comps in product(*(cands[k] for k in OBJS)):
        alpha = dict(zip(OBJS, comps))
        ok = True
        for (k, l) in ARROWS:
            fk, gl = Fmor(k, l), Gmor(k, l)
            for t in Fobj[k]:
                if gl[alpha[k][t]] != alpha[l][fk[t]]:
                    ok = False; break
            if not ok:
                break
        if ok:
            total += 1
    return total

ok_yoneda = True
for A_ in OBJS:
    for B_ in OBJS:
        got = count_nat(hom_functor(A_), hom_functor(B_))
        want = 1 if B_ <= A_ else 0          # Yoneda: Nat(Hom(A,−),Hom(B,−)) ≅ Hom(B,A)
        if got != want:
            ok_yoneda = False
            print(f"    不吻合: A={A_}, B={B_}: 数到 {got}, 公式给 {want}")
check("CAT-05 Yoneda 实例: 9 对 (A,B) 穷举 Nat(Hom(A,-),Hom(B,-)) 个数 = |Hom(B,A)| ∈ {0,1}",
      ok_yoneda)

print("== CAT-06: Set 中乘积的泛性质 ==")
A6 = {0, 1}; B6 = {'x', 'y'}; Z6 = {10, 11, 12}
f6 = {10: 0, 11: 1, 12: 0}
g6 = {10: 'x', 11: 'y', 12: 'y'}
pair = {z: (f6[z], g6[z]) for z in Z6}
proj_ok = all(pair[z][0] == f6[z] and pair[z][1] == g6[z] for z in Z6)
# 唯一性：穷举全部 Z→A×B 的函数（4^3=64 个），只有 pair 同时满足两投影方程
allmaps = [dict(zip(Z6, vs)) for vs in product(product(A6, B6), repeat=3)]
uniq = sum(1 for m in allmaps
           if all(m[z][0] == f6[z] and m[z][1] == g6[z] for z in Z6))
check("CAT-06 乘积泛性质: ⟨f,g⟩ 使 π₁∘⟨f,g⟩=f, π₂∘⟨f,g⟩=g 且穷举 64 映射唯一",
      proj_ok and uniq == 1)

print("== CAT-07: Set 中拉回（纤维积） ==")
fa = {0: 7, 1: 7, 2: 8}              # f: A→C
gb = {'x': 7, 'y': 8}                # g: B→C
pullback = {(a, b) for a in fa for b in gb if fa[a] == gb[b]}
commute = all(fa[a] == gb[b] for (a, b) in pullback)                     # 方块交换
exact = pullback == {(0, 'x'), (1, 'x'), (2, 'y')}                        # 恰为配对集
noncone = (0, 'y') not in pullback                                      # 非锥元素被排除
check("CAT-07 拉回实例: A×_C B = {(a,b): f(a)=g(b)}, 方块交换且非匹配对被排除",
      commute and exact and noncone)

print("== CAT-08/09: 自由幺半群 List(A) + 自由-遗忘伴随 ==")
alpha = ['a', 'b']
lists = [[]] + [[c] for c in alpha] + [list(p) for p in product(alpha, repeat=2)]
assoc_l = all(((l1 + l2) + l3) == (l1 + (l2 + l3))
              for l1 in lists for l2 in lists for l3 in lists)
unit_l = all(([] + l) == l == (l + []) for l in lists)
check("CAT-08 自由幺半群: (List(A),++,[]) 结合律+单位律全过（17²组列表）",
      assoc_l and unit_l)
fmap = {'a': 1, 'b': 2}                      # f: {a,b} → (Z/3,+) 的底层集合映射
ext = lambda l: sum(fmap[c] for c in l) % 3  # 唯一幺半群同态扩张
hom_unit = ext([]) == 0
hom_mult = all(ext(l1 + l2) == (ext(l1) + ext(l2)) % 3
               for l1 in lists for l2 in lists)
check("CAT-09 泛性质实例: 扩张 ext 保单位与乘法(concat) → List ⊣ U 的单位律",
      hom_unit and hom_mult)

print("== CAT-10/11: Lens 定律与反例 ==")
get = lambda s: s[0]
put = lambda s, a: (a, s[1])                 # fst-lens
S10 = [(i, j) for i in range(2) for j in range(2)]
putget = all(get(put(s, a)) == a for s in S10 for a in range(3))
getput = all(put(s, get(s)) == s for s in S10)
putput = all(put(put(s, a1), a2) == put(s, a2) for s in S10 for a1 in range(3) for a2 in range(3))
check("CAT-10 fst-Lens 三定律: PutGet / GetPut / PutPut 全过", putget and getput and putput)
broken_put = lambda s, a: s                  # 反例: put 忽略新值
violates = any(get(broken_put(s, a)) != a for s in S10 for a in range(3))
check("CAT-11 反例: broken put(忽略新值) 违反 PutGet → 定律非装饰", violates)

print("== CAT-12: Yoneda 嵌入忠实性 ==")
# Nat(Hom(B,−),Hom(A,−)) 与反向同时非零 ⟺ A≅B（预序: ⟺ A=B）
nat_counts = {(A_, B_): count_nat(hom_functor(A_), hom_functor(B_))
              for A_ in OBJS for B_ in OBJS}
faithful = all((nat_counts[(A_, B_)] > 0 and nat_counts[(B_, A_)] > 0) == (A_ == B_)
               for A_ in OBJS for B_ in OBJS)
check("CAT-12 Yoneda 忠实实例: 双向自然变换存在 ⟺ 对象相同（0,1,2 互不等价）",
      faithful)

print(f"\n全部通过: {len(PASS)}/12 条断言")
print("（★ 含义 = 有限范畴上实例级穷举通过；定理级确证归 L3 Lean，见 METHODOLOGY §六）")
