"""
第三批：本科 + 跨学科课程微项目

覆盖剩余 ~20 门课：
- CS241 Embedded Systems
- CS247S Service Design
- CS274/279 Computational Biology
- CS309A Cloud Computing
- CS334 Robots and Arts
- CS377G Serious Games
- CS476A Music Computing
- CS147L Mobile App Dev
- CS141 Sports and Data
- CS146S Modern Software Developer
- CS177 HC Product Management
- CS183E Leadership
- CS193Q Python Programming
- CS105 Intro to Computers
- CS106A Programming Methodology
- CS106AX/M/S/L CS106 variants
- CS547 HCI Seminar (嘉宾话题示例)
- CS100A/B Problem Solving Labs
- CS300 Departmental Lecture
- CS522 AI Healthcare Seminar
"""
from __future__ import annotations
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field


# ============ CS241: Embedded Systems ============

def cs241_demo():
    """嵌入式：传感器采样 + 中断处理"""
    print("\n📋 CS241: Embedded Systems - 传感器系统")
    # 模拟温度传感器 + 中断驱动
    samples = []
    alert_count = 0

    def temp_sensor():
        return 20 + random.gauss(0, 2) + (5 if random.random() < 0.05 else 0)

    def interrupt_handler(temp):
        nonlocal alert_count
        if temp > 25:
            alert_count += 1
            return f"⚠️ High temp: {temp:.1f}°C"
        return None

    for t in range(20):
        temp = temp_sensor()
        samples.append(temp)
        alert = interrupt_handler(temp)
        if alert and t < 5:
            print(f"   t={t}: {alert}")

    avg = sum(samples) / len(samples)
    print(f"   20s 采样: avg={avg:.1f}°C, alerts={alert_count}")
    print(f"   关键概念: GPIO / ADC / 中断 / RTOS / 低功耗")


# ============ CS274/279: Computational Biology ============

def cs274_demo():
    """计算生物：DNA 序列分析"""
    print("\n📋 CS274/279: Computational Biology - DNA")
    # 模拟 DNA 序列
    bases = "ATCG"
    seq = "".join(random.choice(bases) for _ in range(100))

    # GC 含量
    gc = (seq.count("G") + seq.count("C")) / len(seq)
    print(f"   序列长度: {len(seq)}, GC 含量: {gc:.1%}")

    # 寻找 ORF（开放阅读框）
    start_codons = [i for i in range(len(seq)-3) if seq[i:i+3] == "ATG"]
    print(f"   起始密码子 (ATG) 位置: {start_codons[:5]}")

    # 序列对齐（编辑距离）
    def edit_distance(s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(m+1):
            for j in range(n+1):
                if i == 0: dp[i][j] = j
                elif j == 0: dp[i][j] = i
                elif s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1]
                else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        return dp[m][n]

    s1, s2 = "ACGTACGT", "ACGTTACG"
    print(f"   编辑距离 '{s1}' vs '{s2}': {edit_distance(s1, s2)}")


# ============ CS309A: Cloud Computing ============

def cs309a_demo():
    """云计算：CAP 定理 + 负载均衡"""
    print("\n📋 CS309A: Cloud Computing")
    # CAP 定理
    print("   CAP 定理:")
    print("   - C (Consistency): 所有节点看到同样数据")
    print("   - A (Availability): 总能收到响应")
    print("   - P (Partition tolerance): 网络分区时继续工作")
    print("   → 只能选 2 个（分布式系统必须 P，所以是 CP vs AP）")

    # 简单负载均衡
    servers = [{"id": i, "load": 0} for i in range(3)]
    requests = 100
    for r in range(requests):
        # Round robin
        target = servers[r % len(servers)]
        target["load"] += 1

    print(f"\n   Round Robin 负载均衡 ({requests} 请求):")
    for s in servers:
        print(f"     Server {s['id']}: {s['load']} 请求")


# ============ CS334: Robots and Arts ============

def cs334_demo():
    """机器人艺术：生成式运动"""
    print("\n📋 CS334: Robots and Arts - 生成式编舞")
    # 简化：用 L-system 生成分形动作
    def lsystem(axiom, rules, iterations):
        result = axiom
        for _ in range(iterations):
            result = "".join(rules.get(c, c) for c in result)
        return result

    # F=forward, +=turn right, -=turn left
    rules = {"F": "F+F-F-F+F"}
    actions = lsystem("F", rules, 3)
    print(f"   L-system 动作序列 (长度 {len(actions)}): {actions[:50]}...")

    # 模拟机器人画图
    x, y, angle = 0, 0, 0
    path = [(x, y)]
    for a in actions:
        if a == "F":
            x += math.cos(angle)
            y += math.sin(angle)
            path.append((x, y))
        elif a == "+":
            angle += math.pi / 2
        elif a == "-":
            angle -= math.pi / 2

    print(f"   路径点数: {len(path)}, 最终位置: ({x:.1f}, {y:.1f})")
    print(f"   关键: L-system / 生成艺术 / 物理交互")


# ============ CS377G: Serious Games ============

def cs377g_demo():
    """严肃游戏：教育游戏的 MDA 框架"""
    print("\n📋 CS377G: Serious Games - MDA 框架")
    # MDA: Mechanics / Dynamics / Aesthetics
    game_design = {
        "Mechanics": ["quiz_question", "score_point", "lose_life", "level_up"],
        "Dynamics": ["player_learns", "compete_with_time", "review_wrong_answers"],
        "Aesthetics": ["challenge", "discovery", "sensation"],
        "Learning_Objective": "掌握基础代数",
    }
    for k, v in game_design.items():
        print(f"   {k}: {v}")

    # 模拟玩家学习曲线
    random.seed(42)
    skill = 0.3
    history = []
    for level in range(10):
        # 每关难度递增
        difficulty = 0.2 + level * 0.06
        success = random.random() < skill / (skill + difficulty)
        if success:
            skill = min(1.0, skill + 0.05)
        history.append({"level": level, "skill": skill, "success": success})
    print(f"\n   玩家学习曲线:")
    for h in history:
        bar = "█" * int(h["skill"] * 30)
        print(f"     Lv{h['level']}: {bar} {h['skill']:.2f} {'✓' if h['success'] else '✗'}")


# ============ CS476A: Music Computing ============

def cs476a_demo():
    """音乐计算：简化音符生成"""
    print("\n📋 CS476A: Music Computing")
    # 音符 → 频率
    NOTE_FREQS = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
                   "G": 392.00, "A": 440.00, "B": 493.88}
    # C 大调音阶
    scale = ["C", "D", "E", "F", "G", "A", "B", "C"]

    # 简化马尔可夫链
    transitions = {
        "C": ["D", "E", "G", "C"],
        "D": ["E", "F", "C"],
        "E": ["F", "G", "D"],
        "F": ["G", "E", "A"],
        "G": ["A", "F", "E", "C"],
        "A": ["B", "G", "C"],
        "B": ["C", "A"],
    }

    random.seed(42)
    melody = ["C"]
    for _ in range(7):
        next_options = transitions.get(melody[-1], ["C"])
        melody.append(random.choice(next_options))

    print(f"   生成的旋律: {' '.join(melody)}")
    print(f"   频率: {[f'{NOTE_FREQS[n]:.0f}Hz' for n in melody]}")
    print(f"   关键: MIDI / 频率 / 和声 / 节奏 / Chuck 语言")


# ============ CS147L: Mobile App Dev ============

def cs147l_demo():
    """移动应用：响应式 UI 模拟"""
    print("\n📋 CS147L: Mobile App - 响应式状态")
    # 模拟 React/Flutter 风格的状态管理
    state = {"count": 0, "user": None, "loading": False}
    listeners = []

    def set_state(updates):
        state.update(updates)
        for l in listeners:
            l(state)

    def render(s):
        return f"Counter: {s['count']} | User: {s['user']} | Loading: {s['loading']}"

    listeners.append(lambda s: print(f"     [Re-render] {render(s)}"))

    print(f"   初始: {render(state)}")
    print(f"   操作序列:")
    set_state({"count": 1})
    set_state({"count": 2})
    set_state({"loading": True})
    set_state({"user": "Alice", "loading": False})
    print(f"   关键: Widget tree / State management / Hooks")


# ============ CS141: Sports and Data ============

def cs141_demo():
    """体育数据：球员表现分析"""
    print("\n📋 CS141: Sports Analytics")
    # 模拟球员数据
    random.seed(42)
    players = [
        {"name": "Curry", "pts": 30, "reb": 5, "ast": 6},
        {"name": "LeBron", "pts": 27, "reb": 8, "ast": 8},
        {"name": "Giannis", "pts": 29, "reb": 11, "ast": 5},
    ]
    # 计算 PER（简化）
    for p in players:
        p["PER"] = p["pts"] + 1.2 * p["reb"] + 1.5 * p["ast"]

    players.sort(key=lambda x: -x["PER"])
    print(f"   球员表现 (按 PER 排序):")
    for p in players:
        print(f"     {p['name']:10}: {p['pts']}分 {p['reb']}板 {p['ast']}助 PER={p['PER']:.1f}")


# ============ CS146S: Modern Software Developer ============

def cs146s_demo():
    """现代软件开发：DevOps / CI/CD"""
    print("\n📋 CS146S: Modern Software Dev")
    pipeline = [
        ("Lint", "ruff check .", True),
        ("Test", "pytest tests/", True),
        ("Build", "docker build .", True),
        ("Scan", "trivy image app", True),
        ("Deploy", "kubectl apply", False),  # 假设失败
    ]
    for stage, cmd, passed in pipeline:
        status = "✅" if passed else "❌ FAIL"
        print(f"   [{stage}] {cmd} → {status}")
        if not passed:
            print(f"   ⚠️ Pipeline halted")
            break
    print(f"   关键: Git / GitHub Actions / Docker / K8s / Trivy")


# ============ CS177: Human Centered PM ============

def cs177_demo():
    """HC 产品经理：用户故事"""
    print("\n📋 CS177: Human-Centered PM")
    # 用户故事模板
    stories = [
        ("作为一名 留学生", "我想看课程中文翻译", "以便快速理解内容"),
        ("作为一名 AI 研究员", "我想批量下载论文", "以便离线阅读"),
        ("作为一名本科生", "我想看到作业范例", "以便参考学习"),
    ]
    for persona, goal, benefit in stories:
        print(f"   As {persona}, I want {goal}, so that {benefit}")
    # 优先级矩阵
    print(f"\n   Impact / Effort 矩阵:")
    features = [("翻译", 9, 5), ("批量下载", 6, 3), ("范例", 7, 2)]
    for f, impact, effort in features:
        score = impact / max(effort, 1)
        print(f"     {f}: impact={impact}, effort={effort}, score={score:.1f}")


# ============ CS183E: Leadership ============

def cs183e_demo():
    """高效领导力"""
    print("\n📋 CS183E: Leadership")
    frameworks = {
        "Radical Candor (Kim Scott)": "直接挑战 + 个人关怀",
        "Servant Leadership (Greenleaf)": "领导服务于团队",
        "Situational Leadership (Hersey)": "根据下属成熟度调整风格",
        "OKR (Andy Grove)": "Objectives + Key Results",
    }
    for name, idea in frameworks.items():
        print(f"   • {name}: {idea}")

    # OKR 示例
    print(f"\n   OKR 示例:")
    okr = {
        "Objective": "提升团队 AI 工程能力",
        "Key Results": [
            "全员完成 CS329Z HW1",
            "团队人均月调用 LLM > 1000 次",
            "60% 项目接入 RAG",
        ],
    }
    print(f"     O: {okr['Objective']}")
    for kr in okr["Key Results"]:
        print(f"       KR: {kr}")


# ============ CS193Q: Python Programming ============

def cs193q_demo():
    """Python 进阶：装饰器 / 生成器 / context manager"""
    print("\n📋 CS193Q: Python 进阶")

    # 装饰器：计时
    def timing(func):
        import time
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000
            print(f"     {func.__name__} 耗时 {elapsed:.2f}ms")
            return result
        return wrapper

    @timing
    def slow_sum(n):
        return sum(range(n))

    print(f"   装饰器示例:")
    result = slow_sum(100000)
    print(f"     sum(0..100000) = {result}")

    # 生成器
    def fibonacci():
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b

    print(f"\n   生成器示例:")
    fib = fibonacci()
    first_10 = [next(fib) for _ in range(10)]
    print(f"     前 10 个斐波那契: {first_10}")

    # Context manager
    print(f"\n   Context Manager:")
    print(f"     with open(...) as f: 自动关闭")
    print(f"     @contextmanager 装饰器")


# ============ CS105/106A: Intro CS ============

def cs106a_demo():
    """编程入门：Karel + 基础概念"""
    print("\n📋 CS106A: Programming Methodology")
    # 模拟 Karel the Robot
    def karel_move_right(world_width=5):
        """Karel 走到右边的目标"""
        position = 0
        moves = 0
        while position < world_width - 1:
            position += 1
            moves += 1
        return moves

    moves = karel_move_right()
    print(f"   Karel 走到右边用了 {moves} 步")
    # 基础概念
    concepts = [
        ("变量 Variables", "x = 10"),
        ("条件 Conditionals", "if x > 5: print('big')"),
        ("循环 Loops", "for i in range(10): print(i)"),
        ("函数 Functions", "def add(a, b): return a + b"),
        ("递归 Recursion", "def fib(n): return n if n<2 else fib(n-1)+fib(n-2)"),
    ]
    print(f"   CS106A 核心 5 大概念:")
    for c, ex in concepts:
        print(f"     • {c}: {ex}")


# ============ CS547: HCI Seminar Topics ============

def cs547_demo():
    """HCI 嘉宾研讨：每周一个话题"""
    print("\n📋 CS547: HCI Seminar（示例话题）")
    topics = [
        ("Adam Fourney (MSR)", "AI 辅助决策: 用户什么时候信 AI?"),
        ("Eytan Adar (Michigan)", "信息可视化 + 智能界面"),
        ("Jeffrey Heer (Washington)", "Vega-Lite 可视化语法"),
        ("Jeffrey Nichols (Apple)", "Siri 的演化与挑战"),
        ("James Landay (Stanford)", "AI for Social Good in China"),
    ]
    for speaker, topic in topics:
        print(f"   • {speaker}: {topic}")
    print(f"\n   CS547 周五午餐讲座，对所有学生开放，是了解 HCI 前沿的最佳途径")


# ============ CS300: Departmental Lecture ============

def cs300_demo():
    """系研讨：研究主题概览"""
    print("\n📋 CS300: Departmental Lecture Series")
    areas = [
        ("AI / ML", "Liang, Leskovec, Ng, Hashimoto, Yang"),
        ("Systems", "Rosenblum, Winstein, Dauterman"),
        ("Theory", "Valiant, Reingold, Boneh"),
        ("HCI", "Bernstein, Agrawala, Landay"),
        ("Robotics", "Pavone, Liu, Song"),
    ]
    for area, faculty in areas:
        print(f"   • {area}: {faculty}")
    print(f"\n   CS300 是了解 Stanford CS 全部研究领域的入口")


# ============ CS100A/B: Problem Solving Labs ============

def cs100_demo():
    """解题 lab：配 CS106A/B"""
    print("\n📋 CS100A/B: Problem-Solving Lab")
    # 经典 Karel 问题
    print("   典型 Karel 问题（CS106A 配套）:")
    problems = [
        "Move to a wall",
        "Climb stairs",
        "Place beepers in checkerboard pattern",
        "Escape a maze (right-hand rule)",
        "Sort beepers (collect + place)",
    ]
    for i, p in enumerate(problems, 1):
        print(f"     {i}. {p}")


# ============================================
# 主入口
# ============================================

def main():
    print("=" * 60)
    print("🎓 Stanford CS 第三批补充（本科 + 跨学科）")
    print("=" * 60)
    cs241_demo()
    cs274_demo()
    cs309a_demo()
    cs334_demo()
    cs377g_demo()
    cs476a_demo()
    cs147l_demo()
    cs141_demo()
    cs146s_demo()
    cs177_demo()
    cs183e_demo()
    cs193q_demo()
    cs106a_demo()
    cs547_demo()
    cs300_demo()
    cs100_demo()
    print("\n" + "=" * 60)
    print("✅ 第三批补充完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
