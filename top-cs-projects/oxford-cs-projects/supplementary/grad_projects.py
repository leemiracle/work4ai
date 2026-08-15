"""
Oxford CS 研究生 MSc ACS 课程微项目集
覆盖：
- Machine Learning (deep)
- Deep NLP (Youn Kim)
- Computer Vision (deep)
- Quantum Computing
- Automated Reasoning (deep)
- Categories Proofs Processes (deep)
- Verification of Hardware & Software
- Foundations of CS (deep)
- Advanced Security
- Software Verification
"""
import math
import random
from collections import defaultdict


# ============ Machine Learning (Deep) ============

def micro_ml_cross_validation():
    """ML: k-fold 交叉验证"""
    print("\n📋 Machine Learning: k-Fold 交叉验证")
    random.seed(42)
    data = list(range(100))
    random.shuffle(data)

    k = 5
    fold_size = len(data) // k
    accuracies = []

    for fold in range(k):
        start = fold * fold_size
        end = start + fold_size
        test_set = data[start:end]
        train_set = data[:start] + data[end:]
        # Mock 准确率（用训练集大小的函数模拟）
        acc = 0.80 + random.gauss(0, 0.03)
        accuracies.append(acc)

    mean_acc = sum(accuracies) / k
    std_acc = math.sqrt(sum((a - mean_acc) ** 2 for a in accuracies) / k)

    print(f"   数据集: {len(data)} 样本, k={k}")
    print(f"   各折准确率: {[f'{a:.3f}' for a in accuracies]}")
    print(f"   平均: {mean_acc:.3f} ± {std_acc:.3f}")
    print(f"   → 交叉验证给出模型性能的置信区间")


# ============ Deep NLP (Youn Kim) ============

def micro_nlp_attention():
    """Deep NLP: Self-Attention 机制"""
    print("\n📋 Deep NLP: Self-Attention 计算")
    # 简化 scaled dot-product attention
    seq_len = 4
    d_k = 8
    random.seed(42)

    Q = [[random.gauss(0, 1) for _ in range(d_k)] for _ in range(seq_len)]
    K = [[random.gauss(0, 1) for _ in range(d_k)] for _ in range(seq_len)]
    V = [[random.gauss(0, 1) for _ in range(d_k)] for _ in range(seq_len)]

    # Attention: softmax(QK^T / sqrt(d_k)) V
    def softmax(lst):
        exps = [math.exp(v) for v in lst]
        total = sum(exps)
        return [e / total for e in exps]

    scores = [[sum(Q[i][d] * K[j][d] for d in range(d_k)) / math.sqrt(d_k)
               for j in range(seq_len)] for i in range(seq_len)]

    attn_weights = [softmax(row) for row in scores]

    # 输出
    output = [[sum(attn_weights[i][j] * V[j][d] for j in range(seq_len))
               for d in range(d_k)] for i in range(seq_len)]

    print(f"   输入: {seq_len} 个 token, d_k={d_k}")
    print(f"   Attention 权重矩阵 (softmax后):")
    for i in range(seq_len):
        print(f"     token{i}: {[f'{w:.2f}' for w in attn_weights[i]]}")
    print(f"   → 每行加起来 = 1.0 (softmax 归一化)")


# ============ Computer Vision (Deep) ============

def micro_cv_histogram_eq():
    """CV: 直方图均衡化"""
    print("\n📋 Computer Vision: 直方图均衡化")
    # 模拟低对比度图像（像素集中在 50-100）
    random.seed(42)
    pixels = [random.randint(50, 100) for _ in range(256)]

    # 计算直方图
    hist = [0] * 256
    for p in pixels:
        hist[p] += 1

    # 累积分布函数
    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i-1] + hist[i]

    # 找到第一个非零 cdf
    cdf_min = min(v for v in cdf if v > 0)
    total = len(pixels)

    # 映射
    lut = [0] * 256
    for i in range(256):
        if cdf[i] > 0:
            lut[i] = round((cdf[i] - cdf_min) / (total - cdf_min) * 255)

    # 应用
    equalized = [lut[p] for p in pixels]

    before_range = (min(pixels), max(pixels))
    after_range = (min(equalized), max(equalized))

    print(f"   原始像素范围: {before_range[0]}-{before_range[1]} (对比度低)")
    print(f"   均衡化后范围: {after_range[0]}-{after_range[1]} (对比度提升)")
    print(f"   → 均衡化拉伸了像素值分布到全范围")


# ============ Quantum Computing ============

def micro_quantum_entanglement():
    """Quantum: Bell 态（纠缠）"""
    print("\n📋 Quantum Computing: Bell 态纠缠")
    # |Φ+⟩ = (|00⟩ + |11⟩) / √2
    # 测量时两个 qubit 总是相同（00 或 11）

    random.seed(42)
    n_trials = 10000
    results = defaultdict(int)
    for _ in range(n_trials):
        if random.random() < 0.5:
            results['00'] += 1
        else:
            results['11'] += 1

    print(f"   Bell 态 |Φ+⟩ = (|00⟩ + |11⟩)/√2")
    print(f"   {n_trials} 次测量:")
    for outcome in ['00', '01', '10', '11']:
        count = results[outcome]
        pct = count / n_trials * 100
        print(f"     |{outcome}⟩: {count} ({pct:.1f}%)")
    print(f"   → 只出现 00 和 11（纠缠！测量一个就知道另一个）")


# ============ Automated Reasoning (Deep) ============

def micro_ar_davis_putnam():
    """AR: Davis-Putnam (非 DPLL，变量消去版)"""
    print("\n📋 Automated Reasoning: Davis-Putnam 变量消去")
    # 规则: 选取变量 x，对所有含 x 的 clause 和含 ¬x 的 clause 做归结
    # 然后删除所有含 x 或 ¬x 的 clause

    clauses = [
        {1, 2},      # x1 ∨ x2
        {-1, 3},     # ¬x1 ∨ x3
        {-2, 3},     # ¬x2 ∨ x3
        {-3},        # ¬x3
    ]

    # 消去变量 3（¬x3 + 任何含 x3 的 clause）
    has_3 = [c for c in clauses if 3 in c]
    has_neg3 = [c for c in clauses if -3 in c]
    print(f"   含 x3: {has_3}, 含 ¬x3: {has_neg3}")

    new_clauses = []
    for c in clauses:
        if 3 not in c and -3 not in c:
            new_clauses.append(c)
    for c1 in has_3:
        for c2 in has_neg3:
            resolvent = (c1 - {3}) | (c2 - {-3})
            if not any(-l in resolvent for l in resolvent):  # tautology check
                new_clauses.append(resolvent)

    print(f"   消去 x3 后: {new_clauses}")
    print(f"   继续消去 → 最终空子句 = UNSAT")


# ============ Categories Proofs Processes (Deep) ============

def micro_cpp_yoneda():
    """CPP: Yoneda 引理（直觉）"""
    print("\n📋 Categories Proofs & Processes: Yoneda 引理")
    print("   Yoneda 引理: Nat(Hom(A, -), F) ≅ F(A)")
    print("   自然变换 Hom(A,-) → F 的集合 ≅ F(A) 的元素")
    print()
    print("   直觉: 一个对象 A 完全由它和其他对象的关系决定")
    print("   'Tell me who talks to you, and I'll tell you who you are'")
    print()
    print("   在编程中: 自由定理(free theorem)来自参数化类型")
    print("   e.g., forall a. [a] → [a] 的函数必须保持元素顺序")
    print("   —— 因为它不能检查元素类型（parametricity）")


# ============ Verification of Hardware & Software ============

def micro_verification_invariants():
    """Verification: 不变式验证"""
    print("\n📋 Verification: 循环不变式")
    # 验证: 求 x^n 的循环（仅用乘法）
    def power(x, n):
        """Contract: requires n >= 0, ensures result = x^n"""
        result = 1.0
        i = 0
        # Invariant: result = x^i AND 0 <= i <= n
        while i < n:
            result *= x
            i += 1
            # 不变式检查（运行时验证）
            assert abs(result - x ** i) < 1e-10 * max(1, abs(x**i))
            assert 0 <= i <= n
        return result

    # 验证
    for x, n in [(2, 10), (3, 5), (1.5, 4), (0.5, 8)]:
        result = power(x, n)
        expected = x ** n
        ok = abs(result - expected) < 1e-10
        print(f"   {x}^{n} = {result:.4f}, 预期 {expected:.4f} {'✓' if ok else '✗'}")
    print(f"   → 循环不变式 'result = x^i' 在每步保持")


# ============ Foundations of CS (Deep) ============

def micro_foundations_p_vs_np():
    """Foundations: P vs NP 直觉"""
    print("\n📋 Foundations of CS: P vs NP")
    print("   P: 多项式时间可解的判定问题")
    print("   NP: 解可在多项式时间验证的判定问题")
    print()

    # SAT 是 NP 完全问题（Cook-Levin 定理）
    print("   NP 完全问题（若一个多项式时间解决，则 P=NP）:")
    problems = [
        ("SAT", "布尔可满足性"),
        ("3-SAT", "3-CNF 可满足性"),
        ("TSP (判定版)", "旅行商问题"),
        ("Graph Coloring", "图着色 ≤ k"),
        ("Hamiltonian Path", "哈密顿路径"),
        ("Subset Sum", "子集和"),
    ]
    for name, desc in problems:
        print(f"     {name}: {desc}")

    print()
    print("   验证 vs 求解: 给一个 SAT 的解，验证只需 O(n)")
    print("   但求解最坏需 O(2^n) —— 这就是 NP 的核心困难")


# ============ Advanced Security ============

def micro_security_zero_knowledge():
    """Advanced Security: 零知识证明概念"""
    print("\n📋 Advanced Security: 零知识证明（简化）")
    # Ali Baba 洞（经典 ZKP 隐喻）
    print("   零知识证明: Prover 证明知道秘密，但不泄露秘密")
    print()
    print("   场景: Prover(P) 向 Verifier(V) 证明知道密码")
    print("   但 V 学不到任何关于密码的信息")
    print()

    random.seed(42)
    n_rounds = 20
    success = 0
    for _ in range(n_rounds):
        # P 选随机左/右入口进入
        p_choice = random.choice(['L', 'R'])
        # V 随机要求 P 从某侧出来
        v_request = random.choice(['L', 'R'])
        # 如果 P 知道密码，总能满足（通过密码移动到对侧）
        # 如果 P 不知道密码，有 50% 概率失败
        if p_choice == v_request or True:  # P 知道密码
            success += 1

    fake_success = 0
    for _ in range(n_rounds):
        # 假冒者不知道密码
        p_choice = random.choice(['L', 'R'])
        v_request = random.choice(['L', 'R'])
        if p_choice == v_request:
            fake_success += 1

    print(f"   {n_rounds} 轮模拟:")
    print(f"   真 P (知道密码): 通过率 {success}/{n_rounds} = 100%")
    print(f"   假冒者 (不知密码): 通过率 {fake_success}/{n_rounds} = {fake_success/n_rounds*100:.0f}%")
    print(f"   → 20 轮后，假冒者通过概率 = (1/2)^20 ≈ {0.5**20:.2e}")


# ============ Software Verification ============

def micro_sw_verification_hoare():
    """Software Verification: Hoare 逻辑"""
    print("\n📋 Software Verification: Hoare 三元组")

    def hoare_triple(pre, code, post):
        """{P} S {Q}: 如果前置条件 P 成立，执行 S 后，后置条件 Q 成立"""
        return f"{{ {pre} }} {code} {{ {post} }}"

    examples = [
        ("True", "x := 0", "x = 0"),
        ("n ≥ 0", "i := 0; s := 0; while i<n do s:=s+i; i:=i+1", "s = n*(n-1)/2"),
        ("a > 0 ∧ b > 0", "while a≠b do if a>b then a:=a-b else b:=b-a", "a = gcd(a₀,b₀)"),
    ]
    for pre, code, post in examples:
        print(f"   {hoare_triple(pre, code[:40] + ('...' if len(code) > 40 else ''), post)}")

    print()
    print("   → Hoare 逻辑: 程序正确性的形式化证明系统")
    print("   最弱前置条件 (wp): wp(S, Q) = 使 {wp} S {Q} 成立的最弱前置条件")


# ============ 主入口 ============

def run_all_grad():
    print("=" * 65)
    print("🎓 Oxford CS MSc ACS 研究生课程微项目")
    print("=" * 65)

    micro_ml_cross_validation()
    micro_nlp_attention()
    micro_cv_histogram_eq()
    micro_quantum_entanglement()
    micro_ar_davis_putnam()
    micro_cpp_yoneda()
    micro_verification_invariants()
    micro_foundations_p_vs_np()
    micro_security_zero_knowledge()
    micro_sw_verification_hoare()

    print("\n" + "=" * 65)
    print("✅ 全部研究生课程完成！")
    print("=" * 65)


if __name__ == "__main__":
    run_all_grad()
