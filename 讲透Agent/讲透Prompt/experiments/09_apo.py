"""
实验 09 — 自动 Prompt 优化 (APO): 文本梯度 vs 随机搜索
对应文档: 讲透Prompt/09-Prompt自动优化.md
素材: arXiv:2502.11560 (优化理论) + arXiv:2502.16923 (AWS 5-part 框架, EMNLP 2025)
核心结论:
  1. APO = 把 prompt 工程从"手搓"变成"搜索": 优化目标 max E[acc(f(P(x)), y)]
  2. 文本梯度 (ProTeGi 思想): 从错误样本反推"改进方向"的自然语言描述, 定向改写 prompt
  3. 错误驱动的定向改写 收敛快于 随机搜索 (同预算下)
  4. 种子×算子交叉: 差种子+好算子 > 好种子+差算子 (算子比种子重要)
  5. AlignPro 上界直觉: prompt 优化无法突破模型自身缺陷 (模拟模型 80% 否定处理 → acc 封顶 <100%)
跑法: python3 -u 09_apo.py
"""
import random

def P(*a): print(*a, flush=True)

# ============================================================
# 玩具世界: 情感分类 APO
# ============================================================
# 句子 = 特征组合: pos(正面词数) neg(负面词数) nto(有无否定词) excl(有无感叹号)
# 真实规则 (oracle): (pos - neg) × (否定则取反) > 0 → 正面
# 模拟 LLM f(P, x): 只使用 prompt P 中【激活】的特征 (prompt 提到什么, 模型才会用什么)
#   内在缺陷: ① 感叹号无信息 ② 否定处理只有 80% 生效 (模拟模型能力不完美)
#   干扰特征: 激活后无益, 且有 10% 概率翻错答案 (模拟"往 prompt 塞无关指令反而干扰模型")

USEFUL = ["pos_words", "neg_words", "negation"]           # 3 个有用特征
DISTRACT = ["count_exclamations", "check_text_length", "mention_weather",
            "add_emoji", "write_in_formal_tone", "count_punctuation"]  # 6 个干扰
FEATURES = USEFUL + DISTRACT                              # 搜索空间 9 选 3
FEATURE_DESC = {"pos_words": "统计正面词", "neg_words": "统计负面词", "negation": "注意否定词会翻转情感"}

def make_sentence(rng):
    return {"pos": rng.randint(0, 3), "neg": rng.randint(0, 3),
            "nto": rng.random() < 0.4, "excl": rng.random() < 0.3}

def oracle(s):  # 真实标签
    score = s["pos"] - s["neg"]
    if s["nto"]: score = -score
    return score > 0

def simulate_llm(prompt, s, rng):  # 模拟模型: prompt 激活哪些特征, 就用哪些
    score = 0
    if "pos_words" in prompt: score += s["pos"]
    if "neg_words" in prompt: score -= s["neg"]
    if "negation" in prompt and s["nto"]:
        if rng.random() < 0.8: score = -score   # 模型缺陷: 否定处理 80% 生效
    if any(f in prompt for f in DISTRACT) and rng.random() < 0.10:
        score = -score                          # 干扰指令: 10% 概率把模型带偏
    return score > 0

def evaluate(prompt, data, rng):
    return sum(simulate_llm(prompt, s, rng) == oracle(s) for s in data) / len(data)

# ============================================================
# 两个候选生成算子 (APO 5-part 框架中的 "operator" 维度)
# ============================================================
def op_textual_gradient(prompt, data, errors, rng):
    """文本梯度 (ProTeGi 思想): 分析错误样本 → 反馈'缺失方向' → 定向补词.
    带噪: 只能从错误里看到'句子里有什么', 20% 概率反馈成干扰方向 (模拟 LLM 反馈不完美)"""
    feedback = []
    if any(s["nto"] for s in errors) and "negation" not in prompt:
        feedback.append("negation")
    if any(s["neg"] > 0 for s in errors) and "neg_words" not in prompt:
        feedback.append("neg_words")
    if not feedback:
        cands = [f for f in FEATURES if f not in prompt]
        if cands: feedback.append(rng.choice(cands))
    if rng.random() < 0.2:  # 噪声: 20% 概率把方向搞错成随机干扰项
        feedback = [rng.choice([f for f in DISTRACT if f not in prompt] or feedback)]
    return sorted(set(prompt) | set(feedback))

def op_random(prompt, data, errors, rng):
    """随机算子: 从 9 个特征里随机加一个 (无错误分析, 会撞上干扰项)"""
    cands = [f for f in FEATURES if f not in prompt]
    return sorted(set(prompt) | ({rng.choice(cands)} if cands else set()))

def apo_loop(seed_prompt, op, data, rng, rounds=6):
    """APO 主循环: 评估 → 收集错误 → 算子改写 → 循环 (带早停: 无提升回退)"""
    prompt, best_acc, trace = list(seed_prompt), evaluate(seed_prompt, data, rng), [seed_prompt]
    for r in range(rounds):
        errs = [s for s in data if simulate_llm(prompt, s, rng) != oracle(s)]
        if not errs: break
        cand = op(prompt, data, errs, rng)
        acc = evaluate(cand, data, rng)
        if acc > best_acc:  # 贪心接受 (只有提升才换)
            prompt, best_acc = cand, acc
        trace.append(tuple(prompt))
    return prompt, best_acc, trace

# ============================================================
P("=" * 60); P("Part 1: 文本梯度演化现场 — 差种子如何被一步步修复"); P("=" * 60)
rng = random.Random(42)
data = [make_sentence(rng) for _ in range(200)]
P("验证集: 200 句 | 特征库:", ", ".join(FEATURES))
P("真实规则: (正面词数-负面词数)×(否定取反) > 0 → 正面\n")

seed_bad = ["pos_words"]  # 差种子: 只会说"统计正面词" (不懂负面/否定)
def fmt_prompt(t):  # 打印: 有用特征中文名, 干扰特征标 [干扰]
    return ", ".join(FEATURE_DESC.get(f, f"[干扰]{f}") for f in t)

P(f"种子 prompt (差): [{FEATURE_DESC[seed_bad[0]]}]")
acc0 = evaluate(seed_bad, data, random.Random(7))
P(f"初始准确率: {acc0:.1%}  ← 单特征模型的极限")
P(f"搜索空间: {len(FEATURES)} 个候选指令, 其中只有 {len(USEFUL)} 个有用, {len(DISTRACT)} 个是干扰项\n")

prompt, acc, trace = apo_loop(seed_bad, op_textual_gradient, data, random.Random(7))
P("文本梯度循环 (每轮: 错误分析 → 反馈 → 改写):")
for i, t in enumerate(trace):
    P(f"  轮{i}: prompt={{{fmt_prompt(t)}}} acc={evaluate(list(t), data, random.Random(7)):.1%}")
P(f"==> 终态准确率 {acc:.1%}  实际改写轮数: {len(trace)-1}")

P("\n" + "=" * 60); P("Part 2: 文本梯度 vs 随机搜索 (50 次重复实验)"); P("=" * 60)
res_grad, res_rand = [], []
for i in range(50):
    rng_i = random.Random(1000 + i)
    data_i = [make_sentence(rng_i) for _ in range(200)]
    _, a_g, _ = apo_loop(seed_bad, op_textual_gradient, data_i, random.Random(2000 + i))
    _, a_r, _ = apo_loop(seed_bad, op_random,          data_i, random.Random(3000 + i))
    res_grad.append(a_g); res_rand.append(a_r)
avg_g, avg_r = sum(res_grad) / 50, sum(res_rand) / 50
P(f"同预算 (6轮×50次): 文本梯度平均 acc = {avg_g:.1%} | 随机搜索平均 acc = {avg_r:.1%}")
win = sum(g > r for g, r in zip(res_grad, res_rand))
P(f"文本梯度获胜次数: {win}/50")
P("==> 错误驱动的定向改写稳定优于盲目随机 (组合空间里, 方向信息值钱)")

P("\n" + "=" * 60); P("Part 3: 种子×算子交叉 — 好种子+差算子 vs 差种子+好算子"); P("=" * 60)
seed_good = ["pos_words", "neg_words"]  # 好种子: 已懂两个特征, 只缺否定
cross = {"好种子+随机": [], "差种子+梯度": []}
for i in range(50):
    rng_i = random.Random(5000 + i)
    data_i = [make_sentence(rng_i) for _ in range(200)]
    _, a1, _ = apo_loop(seed_good, op_random,          data_i, random.Random(6000 + i))
    _, a2, _ = apo_loop(seed_bad,  op_textual_gradient, data_i, random.Random(7000 + i))
    cross["好种子+随机"].append(a1); cross["差种子+梯度"].append(a2)
for k, v in cross.items():
    P(f"{k}: 平均 acc = {sum(v)/len(v):.1%}")
better = sum(b > a for a, b in zip(cross["好种子+随机"], cross["差种子+梯度"]))
P(f"差种子+梯度 反超好种子+随机 的次数: {better}/50")
P("==> 【反直觉】算子质量 > 种子质量: 好算子能把差种子拉到好种子够不到的高度,")
P("    因为梯度会修 ALL 缺陷, 而随机算子在好种子的剩余空间里瞎撞")

P("\n" + "=" * 60); P("Part 4: AlignPro 上界 — prompt 优化救不了模型缺陷"); P("=" * 60)
full = USEFUL[:]  # 理论最优 prompt: 全部有用特征激活 (一个干扰都不加)
acc_full = evaluate(full, data, random.Random(7))
P(f"全有用特征 prompt {{{', '.join(FEATURE_DESC[f] for f in full)}}}")
P(f"准确率: {acc_full:.1%}  ← 没到 100%!")
P("原因: 模拟模型否定处理只有 80% 生效 → 无论 prompt 怎么写, ~20% 否定句必错")
P("AlignPro (2025) 理论化了这个观察: 离散 prompt 优化存在收益上界,")
P("相对 RLHF 最优策略有不可消除的次优差距 → prompt 优化有天花板, 别指望它修模型")
