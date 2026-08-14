"""
补充课程微项目集 - 覆盖剩余课程
"""
import math
import random
import re
from collections import Counter


# ============ CS103 Mathematical Foundations ============

def cs103_propositional_logic():
    """命题逻辑：简化版 SAT 求解"""
    print("\n📋 CS103: 命题逻辑（SAT 枚举）")
    # 用结构化 clause：['var', 'op', 'var'] 或 ['NOT', 'var']
    variables = ['p', 'q', 'r']
    clauses = [
        ['p', 'OR', 'q'],         # p ∨ q
        ['NOT_p', 'OR', 'r'],     # ¬p ∨ r
        ['NOT_q', 'OR', 'r'],     # ¬q ∨ r
        ['NOT_r'],                # ¬r
    ]

    def lit_value(lit, vals):
        if lit.startswith('NOT_'):
            return not vals[lit[4:]]
        return vals[lit]

    def clause_sat(clause, vals):
        if len(clause) == 1:
            return lit_value(clause[0], vals)
        if len(clause) == 3 and clause[1] == 'OR':
            return lit_value(clause[0], vals) or lit_value(clause[2], vals)
        return True

    for p in [True, False]:
        for q in [True, False]:
            for r in [True, False]:
                vals = {'p': p, 'q': q, 'r': r}
                if all(clause_sat(c, vals) for c in clauses):
                    print(f"   ✓ 满足的赋值: {vals}")
                    return vals
    print("   UNSAT")
    return None


# ============ CS109 Probability ============

def cs109_bayes_theorem():
    """贝叶斯定理：医疗测试"""
    print("\n📋 CS109: 贝叶斯定理")
    # 罕见病 1% 患病率，测试 sensitivity 99%, specificity 95%
    p_disease = 0.01
    p_pos_given_dis = 0.99
    p_pos_given_no_dis = 0.05

    # P(D | +) = P(+ | D) * P(D) / P(+)
    p_pos = p_pos_given_dis * p_disease + p_pos_given_no_dis * (1 - p_disease)
    p_dis_given_pos = p_pos_given_dis * p_disease / p_pos
    print(f"   患病率: {p_disease:.1%}")
    print(f"   测试阳性时真阳性概率: {p_dis_given_pos:.2%}")
    print(f"   → 这就是 Bayesian 反直觉：即使测试很准，阳性中真患病也只有 ~17%")


# ============ CS154 Theory of Computation ============

def cs154_dfa():
    """确定性有限自动机"""
    print("\n📋 CS154: DFA（识别偶数个 1）")
    # 状态 0: 偶数 1（接受），状态 1: 奇数 1（拒绝）
    transitions = {
        0: {'0': 0, '1': 1},
        1: {'0': 1, '1': 0},
    }
    accept_states = {0}

    def run(s: str) -> bool:
        state = 0
        for c in s:
            state = transitions[state][c]
        return state in accept_states

    tests = ["", "1", "11", "111", "1010", "1111"]
    for s in tests:
        print(f"   '{s}': {'接受' if run(s) else '拒绝'}")


# ============ CS157 Computational Logic ============

def cs157_unification():
    """Prolog 风格的合一"""
    print("\n📋 CS157: Unification (Prolog)")
    # parent(X, Y) + parent(Y, Z) → grandparent(X, Z)
    def unify(t1, t2, bindings=None):
        if bindings is None:
            bindings = {}
        if t1 == t2:
            return bindings
        if isinstance(t1, str) and t1.isupper():  # 变量
            bindings[t1] = t2
            return bindings
        if isinstance(t2, str) and t2.isupper():
            bindings[t2] = t1
            return bindings
        if isinstance(t1, tuple) and isinstance(t2, tuple) and len(t1) == len(t2):
            for a, b in zip(t1, t2):
                unify(a, b, bindings)
            return bindings
        return None

    b = unify(("parent", "X", "alice"), ("parent", "bob", "alice"))
    print(f"   unify parent(X, alice) with parent(bob, alice): {b}")


# ============ CS107 Computer Organization ============

def cs107_bitwise():
    """位运算 + 浮点数表示"""
    print("\n📋 CS107: 位运算")
    # 经典 swap 不用临时变量
    a, b = 5, 9
    a ^= b; b ^= a; a ^= b
    print(f"   XOR swap: 5, 9 → {a}, {b}")

    # IEEE 754 浮点数
    def float_to_bits(x):
        import struct
        return struct.unpack('I', struct.pack('f', x))[0]

    print(f"   1.0 的 IEEE 754 表示: 0x{float_to_bits(1.0):08x}")
    print(f"   0.1 的 IEEE 754 表示: 0x{float_to_bits(0.1):08x}")
    print(f"   +0.0: 0x{float_to_bits(0.0):08x}")
    print(f"   -0.0: 0x{float_to_bits(-0.0):08x}")


# ============ CS144 Networking - HTTP ============

def cs144_http():
    """HTTP 协议"""
    print("\n📋 CS144: HTTP/1.1 请求/响应")
    request = (
        "GET /api/users HTTP/1.1\r\n"
        "Host: api.example.com\r\n"
        "User-Agent: Mozilla/5.0\r\n"
        "Accept: application/json\r\n"
        "\r\n"
    )
    print(f"   Request:\n{request}")
    # 解析
    lines = request.split("\r\n")
    method, path, version = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k] = v
    print(f"   Parsed: {method} {path} {version}")
    print(f"   Headers: {headers}")


# ============ CS240 OS - MapReduce ============

def cs240_mapreduce():
    """模拟 MapReduce"""
    print("\n📋 CS240: MapReduce（Word Count）")
    documents = [
        "the cat sat on the mat",
        "the dog sat on the log",
        "the cat and the dog",
    ]

    def mapper(doc):
        return [(w.lower(), 1) for w in doc.split()]

    def reducer(key, values):
        return (key, sum(values))

    # Map phase
    mapped = []
    for doc in documents:
        mapped.extend(mapper(doc))

    # Shuffle: group by key
    grouped = {}
    for k, v in mapped:
        grouped.setdefault(k, []).append(v)

    # Reduce phase
    results = [reducer(k, v) for k, v in grouped.items()]
    results.sort(key=lambda x: -x[1])
    print(f"   Top 5 words:")
    for word, count in results[:5]:
        print(f"     {word}: {count}")


# ============ CS242 Programming Languages ============

def cs242_lambda():
    """Lambda calculus 基础"""
    print("\n📋 CS242: Lambda Calculus")
    # Church numerals
    church_zero = lambda f: lambda x: x
    church_one = lambda f: lambda x: f(x)
    church_two = lambda f: lambda x: f(f(x))
    church_succ = lambda n: lambda f: lambda x: f(n(f)(x))

    def church_to_int(n):
        return n(lambda x: x+1)(0)

    three = church_succ(church_two)
    print(f"   Church numeral 3 = {church_to_int(three)}")

    # Y combinator（理论）
    Y = lambda f: (lambda x: f(x(x)))(lambda x: f(x(x)))
    print(f"   Y combinator（理论，会无限递归）")


# ============ CS265 Randomized Algorithms ============

def cs265_randomized_quickselect():
    """随机化快速选择（找第 k 大）"""
    print("\n📋 CS265: Randomized Quickselect")
    def quickselect(arr, k):
        if len(arr) == 1:
            return arr[0]
        pivot = random.choice(arr)
        lows = [x for x in arr if x < pivot]
        highs = [x for x in arr if x > pivot]
        pivots = [x for x in arr if x == pivot]
        if k <= len(lows):
            return quickselect(lows, k)
        elif k <= len(lows) + len(pivots):
            return pivot
        else:
            return quickselect(highs, k - len(lows) - len(pivots))

    random.seed(42)
    arr = [random.randint(0, 100) for _ in range(20)]
    print(f"   数组: {arr}")
    median = quickselect(arr, len(arr) // 2)
    print(f"   中位数（期望 O(n)）: {median}, 排序验证: {sorted(arr)[len(arr)//2]}")


# ============ CS259Q Quantum Computing ============

def cs259q_quantum_superposition():
    """量子比特模拟（叠加态）"""
    print("\n📋 CS259Q: Quantum Superposition (模拟)")
    # 单量子比特: α|0⟩ + β|1⟩, |α|² + |β|² = 1
    import cmath

    def measure(alpha, beta, n=1000):
        p0 = abs(alpha)**2
        results = [0] * int(p0 * n) + [1] * (n - int(p0 * n))
        random.shuffle(results)
        return Counter(results[:n])

    # |+⟩ = (|0⟩ + |1⟩)/√2
    alpha = 1/math.sqrt(2)
    beta = 1/math.sqrt(2)
    print(f"   |+⟩ 态测量 1000 次: {measure(alpha, beta)}")
    print(f"   理论概率: |0⟩={abs(alpha)**2:.2f}, |1⟩={abs(beta)**2:.2f}")

    # Hadamard gate H|0⟩ = |+⟩
    print(f"   H 门: |0⟩ → (|0⟩ + |1⟩)/√2")


# ============ CS111 OS - 进程调度 ============

def cs111_process_scheduling():
    """OS 进程调度"""
    print("\n📋 CS111: CPU 调度（FCFS vs SJF vs Round Robin）")

    processes = [("P1", 0, 8), ("P2", 1, 4), ("P3", 2, 9), ("P4", 3, 5)]
    # name, arrival, burst

    # FCFS
    print("\n   FCFS:")
    t = 0
    total_wait = 0
    processes_sorted = sorted(processes, key=lambda x: x[1])
    for name, arr, burst in processes_sorted:
        if t < arr:
            t = arr
        wait = t - arr
        print(f"     {name}: starts={t}, ends={t+burst}, wait={wait}")
        total_wait += wait
        t += burst
    print(f"     Avg wait: {total_wait/len(processes):.2f}")

    # SJF
    print("\n   SJF (non-preemptive):")
    done = []
    t = 0
    total_wait = 0
    remaining = list(processes)
    while remaining:
        available = [p for p in remaining if p[1] <= t]
        if not available:
            t = min(remaining, key=lambda x: x[1])[1]
            continue
        chosen = min(available, key=lambda x: x[2])
        name, arr, burst = chosen
        wait = t - arr
        print(f"     {name}: starts={t}, ends={t+burst}, wait={wait}")
        total_wait += wait
        t += burst
        remaining.remove(chosen)
    print(f"     Avg wait: {total_wait/len(processes):.2f}")


# ============ CS193T - AI 工具实践 ============

def cs193t_prompt_patterns():
    """CS193T Thinking with AI"""
    print("\n📋 CS193T: Prompt 工程 Patterns")
    patterns = [
        ("Zero-shot", "Summarize: <text>"),
        ("Few-shot", "Summarize:\nExample: <example>\nNow: <text>"),
        ("Chain-of-Thought", "Think step by step: <task>"),
        ("Role-play", "You are an expert doctor. <question>"),
        ("ReAct", "Thought: ...\nAction: ...\nObservation: ..."),
        ("Tree-of-Thought", "Explore 3 branches: A/B/C, then pick best"),
    ]
    for name, pattern in patterns:
        print(f"   {name}: {pattern}")


# ============ CS202 Law ============

def cs202_ip_basics():
    """CS202 知识产权基础"""
    print("\n📋 CS202: 知识产权类型")
    types = [
        ("专利 Patent", "保护发明（20 年）", "新算法 / 药物 / 设备"),
        ("版权 Copyright", "保护表达（终身+70 年）", "代码 / 文章 / 音乐"),
        ("商标 Trademark", "保护品牌识别（10 年可续）", "Logo / 名字 / 标语"),
        ("商业秘密 Trade Secret", "保护机密信息（无限期）", "Coca-Cola 配方 / 算法"),
    ]
    for t, desc, ex in types:
        print(f"   • {t}: {desc}（例：{ex}）")

    # AI 生成内容版权
    print("\n   AI 生成内容（2026 法律现状）:")
    print("   • 完全 AI 生成: 一般不受版权保护（US Copyright Office）")
    print("   • AI 辅助 + 人类创作性贡献: 受保护")
    print("   • 训练数据版权: 仍在诉讼中（NYT vs OpenAI）")


# ============ CS7 Personal Finance ============

def cs7_compound_interest():
    """复利"""
    print("\n📋 CS7: 复利的力量")
    principal = 10000
    rate = 0.07  # 7% 假设回报
    years = 30
    for y in [5, 10, 20, 30]:
        amount = principal * (1 + rate) ** y
        print(f"   {y} 年后: ${amount:,.0f} (本金 ${principal:,}, 利率 {rate:.0%})")


# ============ CS24 Minds and Machines ============

def cs24_turing_test():
    """图灵测试思想实验"""
    print("\n📋 CS24: 图灵测试（哲学）")
    questions = [
        ("写一首关于秋天的诗", "测试创造力"),
        ("2 + 2 等于几", "基础能力（不分人机）"),
        ("你今天感觉如何", "情感测试"),
        ("解释量子纠缠", "知识深度"),
    ]
    print("   合格的图灵测试问题应避免:")
    print("   - 数学/逻辑（机器更强）")
    print("   - 单纯记忆（机器更强）")
    print("   应该测试:")
    print("   - 情感 / 共情")
    print("   - 含糊语境理解")
    print("   - 创造性 + 即兴")


# ============ CS42SI Game Dev ============

def cs42si_game_loop():
    """游戏循环"""
    print("\n📋 CS42SI: 游戏循环（Game Loop）")
    print("""
   经典游戏循环:
   while running:
       process_input()      # 输入
       update_state(dt)     # 物理更新
       render()             # 渲染
       dt = clock.tick(60)  # 控制帧率

   关键概念:
   - 帧率 (FPS): 60 fps = 16.7ms/帧
   - delta time: 与帧率无关的物理
   - ECS 架构: Entity / Component / System
    """)


# ============ 主入口 ============

def run_all_supplementary():
    print("=" * 60)
    print("🎓 Stanford CS 补充课程微项目")
    print("=" * 60)

    cs103_propositional_logic()
    cs109_bayes_theorem()
    cs154_dfa()
    cs157_unification()
    cs107_bitwise()
    cs144_http()
    cs240_mapreduce()
    cs242_lambda()
    cs265_randomized_quickselect()
    cs259q_quantum_superposition()
    cs111_process_scheduling()
    cs193t_prompt_patterns()
    cs202_ip_basics()
    cs7_compound_interest()
    cs24_turing_test()
    cs42si_game_loop()

    print("\n" + "=" * 60)
    print("✅ 全部补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_supplementary()
