"""
实验 04 — 能力评估: Benchmark 全景 + 数据污染陷阱
对应文档: 讲透模型/04-能力评估.md

核心结论:
  1. 不同 benchmark 评估不同能力 (知识/推理/代码/数学)
  2. 数据污染 (contamination) 让分数虚高
  3. 多选题 (MMLU) vs 生成题 (HumanEval) vs 偏好 (Arena) 各有局限
  4. 真正的评估 = 多维度 + 防污染 + 人工

跑法: python3 -u 04_eval.py
"""
import math, random
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

P("="*70)
P("实验 04 — 能力评估: Benchmark + 数据污染")
P("="*70)
P()

# ============================================================
# Part 1: 不同 benchmark 评估不同能力
# ============================================================
P("Part 1: 主流 Benchmark 全景")
P("-"*70)
print(f"\n{'Benchmark':<14}{'类型':<14}{'指标':<14}{'评估能力':<28}{'陷阱':<20}")
print("-"*90)
benchmarks = [
    ("MMLU",     "多选题",  "acc",         "广泛知识 (57 学科)", "可能记忆"),
    ("HumanEval","生成代码", "pass@1",      "Python 编程",        "题库小 (164)"),
    ("GSM8K",    "数学题",  "acc",         "小学数学推理",       "数据污染"),
    ("MATH",     "数学题",  "acc",         "竞赛数学",           "极难"),
    ("BBH",      "多步推理", "acc",         "复杂推理 (BIG-Bench)", "人工写答案"),
    ("TruthfulQA","问答",   "acc",         "抗幻觉/真实性",      "题目刁钻"),
    ("HellaSwag","完形",    "acc",         "常识推理",           "数据简单"),
    ("ARC",      "科学题",  "acc",         "中小学科学",         "已 saturated"),
    ("LMSys",    "人对打",  "Elo",         "人类偏好",           "偏好主观"),
    ("AlpacaEval","指令",   "胜率",        "指令遵循",           "可被 gamed"),
]
for name, type_, metric, ability, trap in benchmarks:
    print(f"{name:<14}{type_:<14}{metric:<14}{ability:<28}{trap:<20}")

P("""
关键: 没有"万能 benchmark", 每个评估 [特定能力], 也有 [特定陷阱]
""")

# ============================================================
# Part 2: 数据污染 (Contamination) 实验
# ============================================================
P("="*70)
P("Part 2: 数据污染 — 为什么 [分数高 ≠ 能力强]")
P("-"*70)
P()
P("模拟: 训一个 [死记硬背] 模型 vs [真理解] 模型")
P()

# 模拟测试题: 100 道数学题, 每题 4 选 1
N_QUESTIONS = 100
true_answers = np.random.randint(0, 4, N_QUESTIONS)

def simulate_clean_model(true_capability=0.6):
    """真理解的模型: 每题以 capability 概率答对"""
    preds = []
    for a in true_answers:
        if random.random() < true_capability:
            preds.append(a)
        else:
            # 猜错 (从其他 3 个选项随机)
            wrong = [x for x in range(4) if x != a]
            preds.append(random.choice(wrong))
    return np.array(preds)

def simulate_contaminated_model(true_capability=0.3, contamination_rate=0.5):
    """真理解弱 + 数据污染: contamination_rate 比例的题 [背答案]"""
    preds = []
    for i, a in enumerate(true_answers):
        if random.random() < contamination_rate:
            preds.append(a)  # 背过这道题, 直接答
        elif random.random() < true_capability:
            preds.append(a)  # 真理解
        else:
            wrong = [x for x in range(4) if x != a]
            preds.append(random.choice(wrong))
    return np.array(preds)

def accuracy(preds, true):
    return float(np.mean(preds == true))

# 测试
clean = simulate_clean_model(true_capability=0.6)
contam = simulate_contaminated_model(true_capability=0.3, contamination_rate=0.5)

print(f"{'模型':<32}{'真理解能力':>14}{'污染率':>10}{'测试 acc':>12}{'结论':<20}")
print("-"*88)
print(f"{'真理解模型':<32}{0.6:>14.0%}{'0%':>10}{accuracy(clean, true_answers):>12.1%}    acc = 真能力")
print(f"{'污染模型 (50% 题背过)':<32}{0.3:>14.0%}{'50%':>10}{accuracy(contam, true_answers):>12.1%}    acc 虚高!")

# 改污染率, 看 acc 怎么涨
print(f"\n污染率扫描 (真能力固定 0.3):")
print(f"{'污染率':<10}{'测试 acc':>12}{'acc - 真能力':>16}")
print("-"*38)
for cr in [0, 0.1, 0.3, 0.5, 0.7, 1.0]:
    preds = simulate_contaminated_model(true_capability=0.3, contamination_rate=cr)
    acc = accuracy(preds, true_answers)
    print(f"{cr:<10.0%}{acc:>12.1%}{acc-0.3:>+16.1%}")

P("""
观察:
- 真能力 0.3 + 污染 50% → acc 65% (虚高 35 个百分点!)
- 真能力 0.3 + 污染 100% → acc 100% (看似满分, 其实完全不会!)

→ 这就是为什么 [GSM8K/MMLU 满分] 不代表真懂
   2023 年 LLM 普遍在 GSM8K 上涨 20+ 个百分点, 部分是 [污染]
""")

# ============================================================
# Part 3: 防 contamination 的方法
# ============================================================
P("="*70)
P("Part 3: 防污染的方法")
P("-"*70)
P("""
1. 【动态 benchmark】
   - GSM8K 改数: 把题目里的数字换掉 (8+5 → 7+9)
   - 模型如果 [真懂] 应该还能答对, [背答案] 会废
   - LiveBench / GSM8K-Plus 用这思路

2. 【新出题】
   - 每月新出题 (避免训练数据包含)
   - LMSys Arena / LiveBench 是动态版

3. 【人对战】
   - LMSys Chatbot Arena: 真人盲测两模型, Elo 评分
   - 优点: 测 [真实偏好], 难污染
   - 缺点: 主观, 长尾任务覆盖差

4. 【代码 execution】
   - HumanEval: 写代码 → 真跑 → 看对错
   - 不能靠背, 必须 [写出可运行的代码]
   - 但题库小 (164 题), 容易被专门训练

5. 【多 benchmark 综合】
   - Open LLM Leaderboard 综合多 benchmark
   - 单一 benchmark 易 game, 综合难 game
""")

# ============================================================
# Part 4: 评估的本质 — 三个层次
# ============================================================
P("="*70)
P("Part 4: 评估的三个层次")
P("-"*70)
P("""
┌──────────────────────────────────────────────────────┐
│  Level 1: 准确率 (acc/pass@k)                        │
│  - 多选题/代码题, 客观可量化                          │
│  - 但 [易污染] + [覆盖窄]                             │
├──────────────────────────────────────────────────────┤
│  Level 2: 人类偏好 (Arena/Elo)                       │
│  - 真人盲测, 测真实偏好                               │
│  - 但 [主观] + [长尾弱]                               │
├──────────────────────────────────────────────────────┤
│  Level 3: 任务完成 (端到端)                          │
│  - 让模型真做任务 (写完代码/解决 bug/答客服)          │
│  - 最接近 [实际能力], 但 [难量化]                     │
└──────────────────────────────────────────────────────┘

经验:
- Level 1 (acc): 选模型初筛
- Level 2 (Arena): 决赛
- Level 3 (端到端): 上线前必做
""")

# ============================================================
# Part 5: 当前 SOTA (2024-2025)
# ============================================================
P("="*70)
P("Part 5: 2024-2025 主流模型分数对比 (示意)")
P("-"*70)
print(f"\n{'模型':<18}{'MMLU':>8}{'GSM8K':>8}{'HumanEval':>12}{'MATH':>8}{'Arena Elo':>12}")
print("-"*66)
# 数字来自各公司公开报告, 仅供示意
data = [
    ("GPT-4 Turbo",     "86.4", "92.0", "85.4", "64.3", "1280"),
    ("GPT-4o",          "88.7", "94.0", "90.2", "76.6", "1310"),
    ("Claude-3.5 Sonnet","88.3", "96.4", "92.0", "78.3", "1295"),
    ("Gemini 1.5 Pro",  "85.9", "91.7", "84.1", "67.7", "1290"),
    ("Llama-3.1 405B",  "88.6", "96.8", "89.0", "73.8", "1267"),
    ("Llama-3 70B",     "82.0", "93.0", "81.7", "50.4", "1210"),
    ("Qwen-2.5 72B",    "86.1", "95.8", "86.6", "75.5", "1245"),
    ("DeepSeek-V3",     "88.5", "89.3", "82.6", "61.6", "1255"),
    ("Mixtral 8x7B",    "70.2", "59.1", "40.2", "12.7", "1115"),
]
for row in data:
    print(f"{row[0]:<18}{row[1]:>8}{row[2]:>8}{row[3]:>12}{row[4]:>8}{row[5]:>12}")

P("""
观察:
- 闭源 (GPT-4o/Claude-3.5/Gemini-1.5): 全方位领先
- 开源 (Llama-3.1 405B/Qwen-2.5 72B): 接近闭源, 部分指标持平
- DeepSeek-V3: MoE 架构, 接近闭源
- 小模型 (7B/8x7B): 差距明显, 但 [性价比] 高

注意: 这些分数 [可能含污染], 不要全信!
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
模型评估的复杂性:
1. 不同 benchmark 测不同能力 (MMLU知识/HumanEval代码/GSM8K数学)
2. 数据污染: 真能力 30% + 50% 题背过 → 测试 acc 65% (虚高 35 个百分点)
3. 真能力 30% + 100% 背过 → acc 100% (看似满分实际完全不会)

防污染方法:
- 动态 benchmark (改数/新月出题)
- 人对战 (LMSys Arena)
- 代码 execution
- 多 benchmark 综合

评估三层: 准确率 (初筛) → 偏好 (决赛) → 端到端 (上线前)

2024-2025 现状: 闭源 (GPT-4o/Claude-3.5) 略领先开源, 但差距缩小
""")
