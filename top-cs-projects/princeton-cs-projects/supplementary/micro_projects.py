"""
Princeton COS 杂项微项目集
============================
覆盖课程/项目：
- COS 498 Junior Independent Work
- COS 398 Sophomore Independent Work
- COS 495/W Special Topics
- COS 116 Computational Thinking
- COS 109 Computers and Technology
- COS 126 加深 (TOY machine extension)
- SML practice (函数式编程练习)
- FreeType 1 (字体渲染概念)
- Hedge Fund Trading (量化交易模拟)
- CS-aware writing (技术写作)
"""
import math
import random
from collections import Counter, defaultdict


# ============ COS 498 Junior Independent Work ============

def cos498_collaborative_filtering():
    """COS 498: 推荐系统 — 协同过滤."""
    print("\n📋 COS 498: 协同过滤推荐")
    # User-item rating matrix
    ratings = {
        "Alice":  {"Inception": 5, "Matrix": 5, "Titanic": 1, "Avatar": 3},
        "Bob":    {"Inception": 4, "Matrix": 5, "Titanic": 2, "Avatar": 2},
        "Carol":  {"Inception": 1, "Matrix": 1, "Titanic": 5, "Avatar": 4},
        "Dave":   {"Inception": 5, "Matrix": 4, "Titanic": 2, "Avatar": 5},
    }

    def cosine_sim(u1, u2):
        common = set(ratings[u1].keys()) & set(ratings[u2].keys())
        if not common:
            return 0.0
        dot = sum(ratings[u1][m] * ratings[u2][m] for m in common)
        n1 = math.sqrt(sum(r ** 2 for r in ratings[u1].values()))
        n2 = math.sqrt(sum(r ** 2 for r in ratings[u2].values()))
        return dot / (n1 * n2)

    # Recommend for Eve (partial ratings)
    eve = {"Inception": 5, "Matrix": 4}
    all_users = ["Alice", "Bob", "Carol", "Dave"]
    sims = {u: cosine_sim("Alice", u) for u in all_users}  # using Alice as proxy
    # Simple: predict Eve's rating for Titanic
    target_movie = "Titanic"
    weighted_sum = 0
    sim_sum = 0
    for user in all_users:
        if target_movie in ratings[user]:
            # Treat Eve's profile as similar to Alice
            sim = cosine_sim("Alice", user)
            weighted_sum += sim * ratings[user][target_movie]
            sim_sum += abs(sim)
    prediction = weighted_sum / sim_sum if sim_sum > 0 else 0
    print(f"   Eve 评分: {eve}")
    print(f"   用户相似度 (vs Alice): {sims}")
    print(f"   预测 Eve 对 {target_movie} 的评分: {prediction:.2f}")


# ============ COS 398 Sophomore Independent ============

def cos398_cellular_automaton():
    """COS 398: 元胞自动机 — Rule 110 (Turing complete)."""
    print("\n📋 COS 398: 元胞自动机 (Rule 110)")
    # Rule 110 is Turing complete (Cook 2004)
    # Rule 110 binary: 01101110 = 110
    rule = 110
    # Rule lookup: 111→0, 110→1, 101→1, 100→0, 011→1, 010→1, 001→1, 000→0
    patterns = {}
    for i in range(8):
        patterns[(i >> 2) & 1, (i >> 1) & 1, i & 1] = (rule >> i) & 1

    width = 40
    steps = 15
    # Initialize with single dot in center
    row = [0] * width
    row[width // 2] = 1

    print(f"   Rule {rule} (Turing complete, Cook 2004):")
    for s in range(steps):
        line = "".join("#" if c else "." for c in row)
        print(f"   {line}")
        new_row = [0] * width
        for i in range(1, width - 1):
            new_row[i] = patterns[row[i-1], row[i], row[i+1]]
        row = new_row


# ============ COS 495/W Special Topics ============

def cos495w_differential_privacy():
    """COS 495W: 差分隐私."""
    print("\n📋 COS 495W: 差分隐私 (Laplace 机制)")
    # Laplace mechanism: add noise Lap(0, Δf/ε) to query result
    # ε = privacy budget, Δf = sensitivity

    def laplace_noise(scale):
        u = random.uniform(-0.5, 0.5)
        return -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))

    # True query: count of people with disease
    true_count = 42
    sensitivity = 1  # adding/removing 1 person changes count by 1

    for epsilon in [0.1, 0.5, 1.0, 5.0]:
        scale = sensitivity / epsilon
        noisy_results = [true_count + laplace_noise(scale) for _ in range(1000)]
        mean_noise = sum(r - true_count for r in noisy_results) / len(noisy_results)
        noise_spread = math.sqrt(sum((r - true_count) ** 2 for r in noisy_results) / len(noisy_results))
        print(f"   ε={epsilon:.1f}: 噪声均值={mean_noise:.2f}, 标准差={noise_spread:.2f}")
    print(f"   真值={true_count}")
    print("   → ε 越小（更隐私），噪声越大（更不准）")


# ============ COS 116 Computational Thinking ============

def cos116_binary_search_game():
    """COS 116: 二分搜索游戏 (猜数字)."""
    print("\n📋 COS 116: 二分搜索 (猜数字游戏)")
    random.seed(42)
    target = random.randint(1, 1000)
    lo, hi = 1, 1000
    guesses = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        guesses += 1
        if mid == target:
            break
        elif mid < target:
            lo = mid + 1
        else:
            hi = mid - 1

    print(f"   目标: {target} (范围 1-1000)")
    print(f"   二分搜索找到: {guesses} 次猜测")
    print(f"   理论最大: {math.ceil(math.log2(1000))} 次 (log2(1000)≈{math.log2(1000):.1f})")
    print(f"   → 从 1000 个候选中定位只需 ~10 步！")


# ============ COS 109 Computers and Technology ============

def cos109_data_representation():
    """COS 109: 数据表示 (integers, floats, unicode)."""
    print("\n📋 COS 109: 数据表示")
    # Integer overflow
    max_int32 = 2**31 - 1
    print(f"   32-bit 最大整数: {max_int32:,}")
    print(f"   +1 溢出 → {-2**31:,} (符号位翻转)")

    # Float precision
    f = 0.1 + 0.2
    print(f"\n   0.1 + 0.2 = {f} (≠ 0.3！IEEE 754 精度损失)")
    print(f"   差异: {f - 0.3:.2e}")

    # Unicode
    emoji = "🎓"
    print(f"\n   Unicode: '{emoji}' = U+{ord(emoji):04X}")
    print(f"   UTF-8 编码: {emoji.encode('utf-8').hex()} ({len(emoji.encode('utf-8'))} bytes)")

    # Compression
    text = "aaaaabbbbcccdd"
    rle = "5a4b3c2d"  # run-length encoding concept
    print(f"\n   原始: '{text}' ({len(text)} bytes)")
    print(f"   RLE:  '{rle}' ({len(rle)} bytes, 节省 {1 - len(rle)/len(text):.0%})")


# ============ COS 126 加深: TOY machine multiplication ============

def cos126_toy_multiplication():
    """COS 126 加深: TOY machine 循环乘法."""
    print("\n📋 COS 126 加深: 循环乘法模拟")
    # Simulate: multiply 6 × 4 = 24 using repeated addition
    a, b = 6, 4
    result = 0
    steps = 0
    while b > 0:
        result += a
        b -= 1
        steps += 1
    print(f"   {a} × {b + steps} = {result}")
    print(f"   循环执行 {steps} 次（TOY 使用 JZ/JAL 指令实现循环）")
    # TOY instruction trace
    print(f"   对应 TOY 伪代码:")
    print(f"     R[A]=6, R[B]=4, R[C]=0")
    print(f"     loop: if R[B]==0 goto done")
    print(f"           R[C] = R[C] + R[A]")
    print(f"           R[B] = R[B] - 1")
    print(f"           goto loop")
    print(f"     done: OUT R[C]  // 输出 {result}")


# ============ SML Practice ============

def sml_practice_pattern_matching():
    """SML practice: pattern matching and recursion."""
    print("\n📋 SML 练习: 模式匹配 + 递归")

    # Simulate SML list functions in Python
    def length(lst):
        """fun length [] = 0 | length (x::xs) = 1 + length(xs)"""
        return 0 if not lst else 1 + length(lst[1:])

    def reverse(lst):
        """fun reverse [] = [] | reverse (x::xs) = reverse(xs) @ [x]"""
        return [] if not lst else reverse(lst[1:]) + [lst[0]]

    def map_sml(f, lst):
        """fun map f [] = [] | map f (x::xs) = f(x) :: map f xs"""
        return [] if not lst else [f(lst[0])] + map_sml(f, lst[1:])

    lst = [1, 2, 3, 4, 5]
    print(f"   列表: {lst}")
    print(f"   length: {length(lst)}")
    print(f"   reverse: {reverse(lst)}")
    print(f"   map (×2): {map_sml(lambda x: x*2, lst)}")

    # Quicksort in SML style
    def qsort(lst):
        if not lst:
            return []
        pivot = lst[0]
        rest = lst[1:]
        smaller = [x for x in rest if x <= pivot]
        larger = [x for x in rest if x > pivot]
        return qsort(smaller) + [pivot] + qsort(larger)

    random.seed(42)
    arr = [random.randint(0, 100) for _ in range(10)]
    print(f"   qsort({arr})")
    print(f"        = {qsort(arr)}")


# ============ FreeType 1: Font Rendering ============

def freetype1_bezier_outline():
    """FreeType 1: 字体轮廓 (贝塞尔曲线)."""
    print("\n📋 FreeType 1: 字体轮廓渲染")
    # Fonts are defined by Bezier curves. Simulate quadratic Bezier.
    def quad_bezier(p0, p1, p2, t):
        x = (1-t)**2 * p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
        return (x, y)

    # Simulate 'C' glyph outline (simplified)
    p0 = (0, 0); p1 = (0, 1); p2 = (1, 1)
    points = [quad_bezier(p0, p1, p2, t/10) for t in range(11)]
    print(f"   二次贝塞尔曲线 (模拟 'C' 上半轮廓):")
    for i, (x, y) in enumerate(points):
        bar = "#" * int(x * 20) + f" ({x:.2f}, {y:.2f})"
        print(f"   t={i/10:.1f}: {bar}")
    print(f"   → FreeType 将贝塞尔曲线栅格化为像素网格")


# ============ Hedge Fund Trading ============

def hedge_fund_mean_reversion():
    """Hedge Fund: 均值回归交易策略."""
    print("\n📋 量化交易: 均值回归策略")
    random.seed(42)
    # Generate price series with mean reversion
    n = 100
    fair_value = 100.0
    prices = [fair_value]
    for _ in range(n - 1):
        shock = random.gauss(0, 2)
        reversion = 0.1 * (fair_value - prices[-1])  # mean reversion
        prices.append(prices[-1] + shock + reversion)

    # Trading strategy: buy when below fair value, sell when above
    position = 0
    pnl = 0
    trades = 0
    threshold = 2.0
    for i in range(1, n):
        deviation = prices[i] - fair_value
        if deviation < -threshold:
            # Buy
            pnl += (fair_value - prices[i])
            trades += 1
        elif deviation > threshold:
            # Sell
            pnl += (prices[i] - fair_value)
            trades += 1

    print(f"   {n} 天价格序列, 均值={fair_value}")
    print(f"   交易阈值: ±{threshold}")
    print(f"   总交易次数: {trades}")
    print(f"   累计 PnL: {pnl:.2f}")
    print(f"   → 均值回归在区间震荡市场有效，趋势市场中亏损")


# ============ CS-aware Writing ============

def cs_aware_writing_citation():
    """CS-aware writing: 学术引用 + LaTeX 公式."""
    print("\n📋 技术写作: LaTeX 公式 + 引用格式")
    formulas = [
        ("Bayes 定理", r"P(H|E) = \frac{P(E|H) \cdot P(H)}{P(E)}"),
        ("Softmax", r"\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}"),
        ("交叉熵损失", r"L = -\sum_{i} y_i \log(\hat{y}_i)"),
        ("梯度下降", r"\theta_{t+1} = \theta_t - \eta \nabla L(\theta_t)"),
    ]
    print("   常用 LaTeX 公式:")
    for name, formula in formulas:
        print(f"   {name}: ${formula}$")

    print(f"\n   引用格式对比:")
    citations = [
        ("APA",  "(Vaswani et al., 2017)"),
        ("IEEE", "[1]"),
        ("ACM",  "[Vaswani et al. 2017]"),
    ]
    for style, example in citations:
        print(f"   {style}: {example}")


# ============ 主入口 ============

def run_all_micro():
    print("=" * 60)
    print("🎓 Princeton COS 杂项微项目集")
    print("=" * 60)

    cos498_collaborative_filtering()
    cos398_cellular_automaton()
    cos495w_differential_privacy()
    cos116_binary_search_game()
    cos109_data_representation()
    cos126_toy_multiplication()
    sml_practice_pattern_matching()
    freetype1_bezier_outline()
    hedge_fund_mean_reversion()
    cs_aware_writing_citation()

    print("\n" + "=" * 60)
    print("✅ 全部杂项微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_micro()
