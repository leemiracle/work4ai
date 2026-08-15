"""
Princeton COS 本科课程补充项目集
==================================
覆盖课程：
- COS 217 Programming Systems
- COS 240 Reasoning about Computation
- COS 343 Algorithms (graduate-level algorithms)
- COS 341 Discrete Mathematics
- COS 436 Human-Computer Interaction
- COS 432 Information Security
- COS 485 Introduction to Neural Networks
- COS 495 / 496 Independent Work Topics
- MAT 200 Introduction to Logic
- ORF 309 Probability and Stochastic Systems
"""
import math
import random
import string
from collections import Counter, defaultdict


# ============ COS 217 Programming Systems ============

def cos217_linker_symbol_table():
    """COS 217: C compilation pipeline + symbol resolution."""
    print("\n📋 COS 217: C 编译流水线 + 符号表")
    pipeline = [
        ("预处理 (cpp)", "展开 #include / #define / #ifdef"),
        ("编译 (cc1)",   "C → 汇编: 词法→语法→语义→IR→优化→asm"),
        ("汇编 (as)",    "汇编 → 可重定位目标文件 (.o)"),
        ("链接 (ld)",    "符号解析 + 重定位 → 可执行文件"),
    ]
    for stage, desc in pipeline:
        print(f"   {stage}: {desc}")

    # Symbol table simulation
    symbols = {
        "main":   {"defined": True,  "section": ".text", "addr": 0x401000},
        "printf": {"defined": False, "section": "UNDEF",  "addr": None},  # from libc
        "global_var": {"defined": True, "section": ".data", "addr": 0x402000},
    }
    print("\n   符号表:")
    for name, info in symbols.items():
        status = "已定义" if info["defined"] else "外部引用"
        addr = hex(info["addr"]) if info["addr"] else "待链接"
        print(f"     {name}: {status}, section={info['section']}, addr={addr}")


# ============ COS 240 Reasoning about Computation ============

def cos240_nash_equilibrium():
    """COS 240: Game theory — Nash equilibrium computation."""
    print("\n📋 COS 240: Nash 均衡（囚徒困境）")
    # Prisoner's Dilemma payoff matrix
    # (P1's years, P2's years)
    #          Cooperate    Defect
    # Cooperate  (-1,-1)     (-3, 0)
    # Defect      (0,-3)     (-2,-2)
    payoffs = {
        ("C", "C"): (-1, -1),
        ("C", "D"): (-3, 0),
        ("D", "C"): (0, -3),
        ("D", "D"): (-2, -2),
    }

    # Find Nash equilibrium: no player can improve by deviating
    print("   收益矩阵 (P1刑期, P2刑期):")
    for (s1, s2), (p1, p2) in payoffs.items():
        print(f"     P1={s1}, P2={s2}: ({p1}, {p2})")

    # Check each cell for Nash equilibrium
    for (s1, s2) in payoffs:
        p1, p2 = payoffs[(s1, s2)]
        # Can P1 improve by switching?
        alt_s1 = "D" if s1 == "C" else "C"
        p1_better = payoffs[(alt_s1, s2)][0] > p1
        # Can P2 improve?
        alt_s2 = "D" if s2 == "C" else "C"
        p2_better = payoffs[(s1, alt_s2)][1] > p2
        is_nash = not p1_better and not p2_better
        if is_nash:
            print(f"   ✅ Nash 均衡: P1={s1}, P2={s2} (收益 {p1},{p2})")
        else:
            print(f"   ❌ 非均衡:    P1={s1}, P2={s2}")


# ============ COS 343 Algorithms ============

def cos343_union_find_amortized():
    """COS 343: Union-Find with amortized analysis."""
    print("\n📋 COS 343: Union-Find 摊还分析")
    n = 100
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        ops = 0
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
            ops += 1
        return x, ops

    def union(x, y):
        rx, ops1 = find(x)
        ry, ops2 = find(y)
        if rx == ry:
            return ops1 + ops2
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return ops1 + ops2 + 1

    # Random unions
    random.seed(42)
    total_ops = 0
    num_ops = 500
    for _ in range(num_ops):
        x, y = random.randint(0, n-1), random.randint(0, n-1)
        total_ops += union(x, y)

    components = len(set(find(i)[0] for i in range(n)))
    print(f"   {n} 个元素，{num_ops} 次操作")
    print(f"   总操作步数: {total_ops}, 平均: {total_ops/num_ops:.2f}")
    print(f"   连通分量: {components}")
    print(f"   → Ackermann 反函数 α(n) ≈ 4，实际中几乎 O(1) 每次操作")


# ============ COS 341 Discrete Mathematics ============

def cos341_combinatorics_generating():
    """COS 341: Generating functions and combinatorics."""
    print("\n📋 COS 341: 组合数学 + 生成函数")

    # Fibonacci via generating function
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    fibs = [fib(i) for i in range(15)]
    print(f"   Fibonacci 数列 (前15项): {fibs}")
    print(f"   F(14)/F(13) = {fibs[14]/fibs[13]:.6f} (→ 黄金比 {1.618034:.6f})")

    # Catalan numbers: C_n = (2n)! / (n!(n+1)!)
    def catalan(n):
        return math.factorial(2*n) // (math.factorial(n) * math.factorial(n+1))

    catalans = [catalan(i) for i in range(10)]
    print(f"   Catalan 数列 (前10项): {catalans}")
    print(f"   C_4 = {catalans[4]} = 14 (4对括号的合法配对数)")


# ============ COS 436 Human-Computer Interaction ============

def cos436_fitts_law():
    """COS 436: Fitts' Law — pointing device modeling."""
    print("\n📋 COS 436: Fitts' Law (人机交互)")
    # MT = a + b * log2(D/W + 1) = a + b * ID
    # ID = index of difficulty, MT = movement time
    a, b = 0.1, 0.15  # empirical constants (seconds)

    print("   Fitts' Law: MT = a + b * log2(D/W + 1)")
    print(f"   {'按钮大小':>10} {'距离':>8} {'难度(ID)':>10} {'移动时间(ms)':>14}")
    for W, D in [(10, 100), (10, 500), (50, 100), (50, 500), (5, 1000)]:
        ID = math.log2(D / W + 1)
        MT = (a + b * ID) * 1000  # ms
        print(f"   {W:>10}px {D:>8}px {ID:>10.2f} {MT:>14.1f}")
    print("   → 按钮越大、越近 → 移动越快（Google 搜索按钮的设计原理）")


# ============ COS 432 Information Security ============

def cos432_sql_injection():
    """COS 432: SQL injection demonstration + prevention."""
    print("\n📋 COS 432: SQL 注入演示")
    # Vulnerable query construction
    username = "admin' --"
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = 'x'"
    print(f"   恶意输入: username = \"{username}\"")
    print(f"   生成的 SQL: {query}")
    print(f"   → '--' 注释掉了密码检查！攻击者无需密码登录 admin")

    # Prevention: parameterized queries
    safe_query = "SELECT * FROM users WHERE username = ? AND password = ?"
    print(f"\n   防御: 参数化查询")
    print(f"   SQL: {safe_query}")
    print(f"   参数: ('admin\\' --', 'x')")
    print(f"   → 引号被转义，-- 不再是注释")


# ============ COS 485 Neural Networks ============

def cos485_backprop_manual():
    """COS 485: Manual backpropagation on a tiny network."""
    print("\n📋 COS 485: 手算反向传播")
    # Network: input x → hidden h = sigmoid(w1*x + b1) → output y = w2*h + b2
    # Loss: L = 0.5*(y - target)^2

    x = 2.0
    w1, b1, w2, b2 = 0.5, 0.1, -0.3, 0.2
    target = 1.0
    lr = 0.1

    def sigmoid(z):
        return 1.0 / (1.0 + math.exp(-max(-50, min(50, z))))

    # Forward pass
    z1 = w1 * x + b1
    h = sigmoid(z1)
    y = w2 * h + b2
    loss = 0.5 * (y - target) ** 2

    print(f"   前向传播: x={x}")
    print(f"   z1 = {w1}*{x} + {b1} = {z1:.4f}")
    print(f"   h  = σ({z1:.4f}) = {h:.4f}")
    print(f"   y  = {w2}*{h:.4f} + {b2} = {y:.4f}")
    print(f"   L  = 0.5*({y:.4f} - {target})^2 = {loss:.6f}")

    # Backward pass
    dy = y - target          # dL/dy
    dw2 = dy * h             # dL/dw2
    db2 = dy                  # dL/db2
    dh = dy * w2              # dL/dh
    dz1 = dh * h * (1 - h)   # dL/dz1 (sigmoid derivative)
    dw1 = dz1 * x             # dL/dw1
    db1 = dz1                 # dL/db1

    print(f"\n   反向传播:")
    print(f"   ∂L/∂w2 = {dw2:.6f}")
    print(f"   ∂L/∂w1 = {dw1:.6f}")
    print(f"   ∂L/∂b1 = {db1:.6f}")

    # Gradient descent step
    w1_new = w1 - lr * dw1
    w2_new = w2 - lr * dw2
    print(f"\n   更新后: w1={w1_new:.4f}, w2={w2_new:.4f}")


# ============ COS 495 Independent Work Topics ============

def cos495_information_retrieval():
    """COS 495: TF-IDF + BM25 scoring."""
    print("\n📋 COS 495: TF-IDF + BM25 检索")
    docs = [
        "the cat sat on the mat",
        "the dog sat on the log",
        "cats and dogs are pets",
    ]

    # TF-IDF
    N = len(docs)
    df = defaultdict(int)
    for doc in docs:
        for word in set(doc.split()):
            df[word] += 1

    print("   TF-IDF 权重:")
    query = "cat dog"
    for word in query.split():
        idf = math.log((N + 1) / (df.get(word, 0) + 1)) + 1
        print(f"   '{word}': IDF={idf:.4f}")
        for i, doc in enumerate(docs):
            tf = doc.split().count(word)
            tfidf = tf * idf
            print(f"     doc{i}: tf={tf}, TF-IDF={tfidf:.4f}")


# ============ MAT 200 Introduction to Logic ============

def mat200_natural_deduction():
    """MAT 200: Natural deduction proof."""
    print("\n📋 MAT 200: 自然演绎（命题逻辑证明）")
    # Prove: P → Q, Q → R ⊢ P → R (Hypothetical Syllogism)
    proof = [
        ("1", "P → Q",          "Premise"),
        ("2", "Q → R",          "Premise"),
        ("3", "| P",            "Assume (for →I)"),
        ("4", "| Q",            "→E 1,3 (Modus Ponens)"),
        ("5", "| R",            "→E 2,4 (Modus Ponens)"),
        ("6", "P → R",          "→I 3-5"),
    ]
    print("   证明: P → Q, Q → R ⊢ P → R")
    print("   (假言三段论 Hypothetical Syllogism)\n")
    for step, formula, rule in proof:
        indent = "   " if "|" in formula else " "
        formula = formula.replace("|", "│ ")
        print(f"   ({step}) {formula:30s} [{rule}]")


# ============ ORF 309 Probability ============

def orf309_central_limit_theorem():
    """ORF 309: Central Limit Theorem verification."""
    print("\n📋 ORF 309: 中心极限定理验证")
    random.seed(42)
    # Sum of uniform random variables → approaches normal
    n = 5000
    for num_vars in [1, 5, 20, 50]:
        sums = []
        for _ in range(n):
            s = sum(random.uniform(0, 1) for _ in range(num_vars))
            sums.append(s)
        mean = sum(sums) / n
        var = sum((x - mean) ** 2 for x in sums) / n
        theoretical_mean = num_vars * 0.5
        theoretical_var = num_vars * (1/12)
        print(f"   n={num_vars:>3} vars: 均值={mean:.4f} (理论={theoretical_mean:.4f}), "
              f"方差={var:.4f} (理论={theoretical_var:.4f})")
    print("   → 无论原始分布如何，样本和趋于正态分布 (CLT)")


# ============ 主入口 ============

def run_all_undergrad():
    print("=" * 60)
    print("🎓 Princeton COS 本科课程补充项目")
    print("=" * 60)

    cos217_linker_symbol_table()
    cos240_nash_equilibrium()
    cos343_union_find_amortized()
    cos341_combinatorics_generating()
    cos436_fitts_law()
    cos432_sql_injection()
    cos485_backprop_manual()
    cos495_information_retrieval()
    mat200_natural_deduction()
    orf309_central_limit_theorem()

    print("\n" + "=" * 60)
    print("✅ 全部本科补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_undergrad()
