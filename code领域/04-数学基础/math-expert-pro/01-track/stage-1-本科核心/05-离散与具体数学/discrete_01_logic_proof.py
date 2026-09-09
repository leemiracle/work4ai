"""
离散核心 1: 逻辑与证明 — 数学推理的语言与工具
================================================
阶段1 / 模块05 / 离散第 1 弹
命题逻辑 + 谓词逻辑 + 证明策略(归纳法/反证) + 谬误与反例
运行: python3 discrete_01_logic_proof.py  (4 张 PNG)

§1 命题逻辑: 联结词 / 真值表 / 德摩根律
§2 谓词逻辑: 量词 ∀ ∃ / 嵌套量词顺序 / 否定翻转
§3 证明策略 ⭐: 直接 / 逆否 / 反证 / 数学归纳法(强归纳+良序)
§4 常见谬误与反例: 循环论证 / 量词错位 / 一个反例即证伪
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
rng = np.random.default_rng(42)


# §1 命题逻辑
def section_1_propositional():
    print("=" * 70)
    print("§1 命题逻辑: 联结词 / 真值表 / 德摩根律")
    print("=" * 70)
    print("""
    命题 (proposition): 能判断真假的陈述句.
    联结词:
      ¬ (not 否定), ∧ (and 与), ∨ (or 或)
      → (implies 蕴涵: p→q = ¬p∨q), ↔ (iff 等价: 同真同假)
    基本等价律 (可用真值表验证):
      德摩根:   ¬(p∧q) ≡ ¬p∨¬q,  ¬(p∨q) ≡ ¬p∧¬q
      蕴涵消除: p→q ≡ ¬p∨q
      双条件:   p↔q ≡ (p→q)∧(q→p)
    这些是布尔代数的基础——数字电路、SQL WHERE、编程语言核心.
    """)
    NOT = lambda a: 1 - a
    AND = lambda a, b: a * b
    OR = lambda a, b: a + b - a * b
    IMP = lambda a, b: OR(NOT(a), b)          # p→q = ¬p∨q
    p = np.array([0, 0, 1, 1])
    q = np.array([0, 1, 0, 1])
    lhs = NOT(AND(p, q))                       # ¬(p∧q)
    rhs = OR(NOT(p), NOT(q))                   # ¬p∨¬q
    assert np.all(lhs == rhs), "德摩根律失败"
    print(f"  德摩根律 ¬(p∧q) ≡ ¬p∨¬q: 4 种组合全一致? {bool(np.all(lhs == rhs))} ✓")
    print(f"    ¬(p∧q): {lhs.tolist()}")
    print(f"    ¬p∨¬q:  {rhs.tolist()}")
    impl = IMP(p, q)
    assert impl.tolist() == [1, 1, 0, 1], "蕴涵真值错误"
    print(f"\n  蕴涵 p→q = ¬p∨q: {impl.tolist()}  (仅 p=T,q=F 时为假 ✓)")
    iff = (p == q).astype(int)
    print(f"  双条件 p↔q (同真同假): {iff.tolist()}")
    # 分配律 p∧(q∨r) ≡ (p∧q)∨(p∧r) 三变量验证
    r = np.array([0, 1])
    P, Q, R = np.meshgrid(p, q, r, indexing='ij')
    P, Q, R = P.ravel(), Q.ravel(), R.ravel()
    dist_lhs = AND(P, OR(Q, R))
    dist_rhs = OR(AND(P, Q), AND(P, R))
    assert np.all(dist_lhs == dist_rhs)
    print(f"\n  分配律 p∧(q∨r) ≡ (p∧q)∨(p∧r): 8 种组合全一致? {bool(np.all(dist_lhs == dist_rhs))} ✓")
    # 图: 德摩根律真值表热力图
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    labels = ['F', 'T']
    for ax, mat, ttl in [(axes[0], lhs.reshape(2, 2), '¬(p∧q)  德摩根左'),
                         (axes[1], rhs.reshape(2, 2), '¬p∨¬q  德摩根右')]:
        ax.imshow(mat, cmap='Blues', vmin=0, vmax=1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, labels[mat[i, j]], ha='center', va='center',
                        color='white' if mat[i, j] else 'black', fontsize=14)
        ax.set_xticks([0, 1]); ax.set_xticklabels(['q=F', 'q=T'])
        ax.set_yticks([0, 1]); ax.set_yticklabels(['p=F', 'p=T'])
        ax.set_title(ttl)
    fig.suptitle('德摩根律: ¬(p∧q) 与 ¬p∨¬q 真值表完全相同')
    plt.tight_layout(); plt.savefig('discrete_lp_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_lp_s1.png")


# §2 谓词逻辑
def section_2_predicate():
    print("\n" + "=" * 70)
    print("§2 谓词逻辑: 量词 ∀ ∃ 与嵌套顺序")
    print("=" * 70)
    print("""
    谓词 P(x) 是带变量的「命题函数」; 量词把它变成命题:
      ∀x P(x): 对所有 x, P(x) 成立 (全称量词 universal)
      ∃x P(x): 存在 x 使 P(x) 成立 (存在量词 existential)
    关键否定律 (量词翻转):
      ¬∀x P(x) ≡ ∃x ¬P(x)
      ¬∃x P(x) ≡ ∀x ¬P(x)
    ★ 嵌套量词顺序一般不可交换:
      ∀x ∃y R(x,y)  ≠  ∃y ∀x R(x,y)
    """)
    domain = np.arange(1, 11)                 # D = {1,...,10}
    P = (domain ** 2 >= domain)               # P(x) = (x² ≥ x)
    forall_P = bool(np.all(P))
    exists_not_P = bool(np.any(~P))
    equiv = (not forall_P) == exists_not_P
    print(f"  域 D = {{1..10}}, P(x) = (x² ≥ x):")
    print(f"    ∀x P(x) = {forall_P},  ¬∀x P(x) = {not forall_P}")
    print(f"    ∃x ¬P(x) = {exists_not_P}  →  ¬∀x P(x) ≡ ∃x ¬P(x)? {equiv} ✓")
    # 嵌套量词 R(x,y) = (x+y == 11)
    R = (domain[:, None] + domain[None, :]) == 11   # 10×10 布尔
    all_exists = bool(np.all(np.any(R, axis=1)))     # ∀x ∃y: 每行至少一个真
    exists_all = bool(np.any(np.all(R, axis=0)))     # ∃y ∀x: 存在一列全真
    assert all_exists and not exists_all
    print(f"\n  R(x,y) = (x+y=11) 在 D×D:")
    print(f"    ∀x ∃y R(x,y) = {all_exists}   (每一行都至少有一个真)")
    print(f"    ∃y ∀x R(x,y) = {exists_all}   (不存在「全真列」)")
    print(f"    → 顺序交换改变真值! ∀∃ ≠ ∃∀ (经典陷阱)")
    # 图: 10×10 真值表网格
    fig, ax = plt.subplots(figsize=(6.5, 5.8))
    ax.imshow(R.astype(int), cmap='Blues', aspect='equal', vmin=0, vmax=1)
    for i in range(10):
        for j in range(10):
            ax.text(j, i, 'T' if R[i, j] else '.', ha='center', va='center',
                    color='white' if R[i, j] else 'lightgray', fontsize=9)
    ax.set_xticks(range(10)); ax.set_xticklabels(domain)
    ax.set_yticks(range(10)); ax.set_yticklabels(domain)
    ax.set_xlabel('y'); ax.set_ylabel('x')
    ax.set_title('R(x,y)=(x+y=11) 的 10×10 真值表\n每行有 T → ∀x∃y 成立; 无全 T 列 → ∃y∀x 不成立')
    plt.tight_layout(); plt.savefig('discrete_lp_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_lp_s2.png")


# §3 证明策略
def section_3_proof():
    print("\n" + "=" * 70)
    print("§3 证明策略 ⭐: 归纳法 / 反证 / 逆否")
    print("=" * 70)
    print("""
    常见证明策略:
      直接证明:   假设 P, 推出 Q.
      逆否证明:   证 ¬Q→¬P (与 P→Q 等价).
      反证法:     假设 ¬结论, 推出矛盾.
      分情况:     把前提分成若干情形分别证明.
      构造法:     直接构造出满足条件的对象.
    ★ 数学归纳法 (Peano 公理的体现):
      基础: P(1) 成立;   归纳步: P(k) → P(k+1).
      强归纳: 假设 P(1),...,P(k) 全成立来证 P(k+1).
      良序原理: 每个非空自然数集有最小元 (与归纳法等价).
    """)
    # 归纳法验证 Σi = n(n+1)/2
    ns = np.arange(1, 1001)
    actual = np.cumsum(ns)
    formula = ns * (ns + 1) // 2
    assert np.all(actual == formula), "归纳公式失败"
    print(f"  归纳法验证 Σi(1..n)=n(n+1)/2, n=1..1000:")
    print(f"    全部一致? {bool(np.all(actual == formula))} ✓")
    print(f"    Σ(1..100)  = {int(actual[99])}   (理论 100·101/2=5050) ✓")
    print(f"    Σ(1..1000) = {int(actual[999])}  (理论 1000·1001/2={1000*1001//2}) ✓")
    # 反证 √2 无理
    r2 = np.sqrt(2.0)
    print(f"\n  反证 √2 无理 (经典, 与「实数」模块呼应):")
    print(f"    √2 ≈ {r2:.15f},  (√2)²−2 = {r2*r2-2:.2e} (浮点误差, 理论 0)")
    print(f"    逻辑: 设 √2=p/q(既约) → p²=2q² → p 偶 → p=2m → q²=2m² → q 偶")
    print(f"          → p,q 同偶, 与既约矛盾 ✓")
    found = False
    for qq in range(1, 100):
        for pp in range(1, 200):
            if pp * pp == 2 * qq * qq:
                found = True; break
        if found:
            break
    assert not found
    print(f"    数值搜索 q≤99,p≤199: 找到 p²=2q²? {found} (不存在 → 无理 ✓)")
    # Fibonacci 强归纳性质: Σ_{i=1}^{n} F_i = F_{n+2} − 1
    F = [0, 1]
    for i in range(2, 35):
        F.append(F[-1] + F[-2])
    ok_fib = all(sum(F[1:n + 1]) == F[n + 2] - 1 for n in range(1, 30))
    assert ok_fib
    print(f"\n  Fibonacci 强归纳性质: ΣF(1..n) = F_(n+2) − 1, n=1..29:")
    print(f"    全部一致? {ok_fib} ✓")
    print(f"    F_10 = {F[10]}  (理论 55) ✓")
    # 图: 归纳法验证 + Fibonacci 增长
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    n = np.arange(1, 21)
    axes[0].bar(n - 0.2, np.cumsum(n).astype(float), width=0.4, label='Σi 实际', color='C0')
    axes[0].bar(n + 0.2, (n * (n + 1) / 2).astype(float), width=0.4, label='n(n+1)/2 公式', color='C1')
    axes[0].legend(); axes[0].set_xlabel('n')
    axes[0].set_title('归纳法验证: Σi = n(n+1)/2  (前 20 项柱子完全重合)')
    axes[0].grid(True, ls=':', alpha=0.3)
    Fn = [F[i] for i in range(1, 16)]
    axes[1].bar(range(1, 16), Fn, color='C2')
    axes[1].set_xlabel('n'); axes[1].set_ylabel('F_n')
    axes[1].set_title('Fibonacci 数列 (强归纳对象)\n指数增长: 阶段2 证 F_n ≈ φ^n/√5')
    axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('discrete_lp_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_lp_s3.png")


# §4 常见谬误与反例
def section_4_fallacy():
    print("\n" + "=" * 70)
    print("§4 常见谬误与反例的力量")
    print("=" * 70)
    print("""
    常见逻辑谬误:
      循环论证:   把结论当前提偷偷使用.
      量词错位:   混淆 ∀∃ 与 ∃∀ (见 §2).
      肯定后件:   (P→Q) ∧ Q 推 P  (错! Q 可由别的原因成立).
      否定前件:   (P→Q) ∧ ¬P 推 ¬Q (错!).
    ★ 反例 (counterexample) 的力量:
      对「∀n, P(n)」类命题, 一个反例即证伪 (无需更多).
    经典: Euler 公式 n²+n+41 对 n=0..39 全是素数, 但 n=40 时 1681=41².
    """)
    def is_prime(n):
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True
    vals = [m * m + m + 41 for m in range(0, 50)]
    first_counter = None
    for m, v in enumerate(vals):
        if not is_prime(v):
            first_counter = m; break
    assert first_counter == 40
    assert all(is_prime(v) for v in vals[:40])
    print(f"  命题「∀n≥0, n²+n+41 是素数」:")
    print(f"    n=0..39 全素数? {all(is_prime(v) for v in vals[:40])} ✓")
    print(f"    最小反例 n={first_counter}: {vals[first_counter]}={int(round(np.sqrt(vals[first_counter])))}², 不是素数 ✓")
    print(f"    → 一个反例即证伪该「∀」命题")
    # 肯定后件谬误演示
    print(f"\n  肯定后件谬误示例:")
    print(f"    「下雨→地湿; 地湿」推「下雨」? 逻辑无效 (地湿也可能是洒水车)")
    # 图: Euler 素数公式反例
    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    ns = np.arange(0, 45)
    vs = ns * ns + ns + 41
    primality = [is_prime(int(v)) for v in vs]
    colors = ['C2' if p else 'red' for p in primality]
    ax.bar(ns, vs, color=colors)
    ax.axvline(39.5, color='red', ls='--', lw=1.5, label='n=40 反例 (1681=41²)')
    ax.set_xlabel('n'); ax.set_ylabel('n²+n+41')
    ax.set_title('Euler 素数公式: n=0..39 全素数 (绿), n=40 起出现合数 (红)\n一个反例即证伪「∀n」命题')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('discrete_lp_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] discrete_lp_s4.png")
    print("\n  💡 逻辑与证明是「数学推理的元语言」:")
    print("     所有定理证明、程序验证、形式化方法都建立在这套语言之上。")


if __name__ == "__main__":
    print("🌀 离散核心 1: 逻辑与证明  |  阶段1 / 模块05\n")
    section_1_propositional()
    section_2_predicate()
    section_3_proof()
    section_4_fallacy()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 discrete_01_logic_proof.md, 做练习。数学推理的元语言建立!")
    print("=" * 70)
