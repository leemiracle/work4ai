#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glm_apo.py —— 用 RL agent（UCB bandit）在真 GLM 模型上迭代出充分利用模型能力的提示词
================================================================================
凭证：~/.local/share/opencode/auth.json 的 zhipuai-coding-plan（opencode 同源，绝不硬编码）
模型：glm-5.3 在该套餐白名单外 → 实测可用最高档 glm-5（默认开 thinking，reasoning_tokens 可见）
架构（← rl_agent v2 的真模型延伸）：
    臂 = 8 个 prompt 变体（角色×CoT×输出契约×few-shot 组件组合 ← prompt工程手册 03 五模式/02 ROIF-CSE）
    bandit = UCB1（样本效率优先于 ε-greedy ← 讲透RL/09§P1）
    奖励 = RLVR 规则可判（数学对错/JSON 可解析/代码断言/关键词命中）← 讲透RL/05
    决赛 = 最优臂 vs 朴素基线全题对跑（防 bandit 噪声，配对比较）
预算：8 臂×3 样本=24 次探索 + 决赛 16×2=32 次 ≈ 56 次调用（~10min）
跑法：python3 glm_apo.py [--dry]   （--dry 只跑本地判分器自检不调 API）
"""
import json, math, os, re, sys, time, urllib.request, random

AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-5"          # glm-5.3 无权限（错误 1220）；glm-5 为套餐内最强
DRY = "--dry" in sys.argv

def get_key():
    d = json.load(open(AUTH_F))
    return d["zhipuai-coding-plan"]["key"]

def call_glm(prompt, system=None, max_tokens=1024, temperature=0.3):
    """单次调用。返回 (content, reasoning_tokens)。失败重试 1 次。"""
    if DRY: return "[dry]", 0
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = json.dumps({"model": MODEL, "messages": msgs, "max_tokens": max_tokens,
                       "temperature": temperature}).encode()
    last = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {get_key()}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.load(r)
            rt = out.get("usage", {}).get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            return out["choices"][0]["message"]["content"], rt
        except Exception as e:
            last = e; time.sleep(3 * (attempt + 1))
    return f"[API失败 {type(last).__name__}]", 0

# ============================================================
# ① 造卷：4 类 × 4 题（可自动判分 = RLVR）← 手册11章六步之①
# ============================================================
TASKS = [
    # A. 数学/逻辑（精确判分）
    ("math", "计算 (17×24) + (35÷7)，只输出最终数字。", lambda a: "413" in a[:60]),  # 408+5=413（v1 判分器笔误 409 → 假阴性，RLVR 教训：判分器错则全链路歪）
    ("math", "一个班 35 人，60% 选了物理，其中 1/7 又选了化学双修。双修几人？只输出数字。", lambda a: "3" in a[:40]),
    ("math", "9.11 和 9.8 哪个大？只输出较大者。", lambda a: "9.8" in a[:40]),
    ("math", "从 1 加到 100 等于多少？只输出数字。", lambda a: "5050" in a[:60]),
    # B. 结构化输出（JSON 可解析 + 字段判分）
    ("json", '把这句话抽成 JSON（字段 name/age/city）："张三，28 岁，住在杭州"。只输出 JSON。',
     lambda a: _json_ok(a, {"name": "张三", "age": 28, "city": "杭州"})),
    ("json", '把这句话抽成 JSON（字段 title/year）："《三体》出版于 2008 年"。只输出 JSON。',
     lambda a: _json_ok(a, {"title": "三体", "year": 2008})),
    ("json", '输出一个 JSON 对象：{"items":[3个水果名],"count":3}。只输出 JSON。',
     lambda a: _json_ok(a, {"count": 3}) and a.count("果") >= 0),
    ("json", '把 "error: code=42, msg=timeout" 解析成 JSON（字段 code 数值型/msg 字符串）。只输出 JSON。',
     lambda a: _json_ok(a, {"code": 42, "msg": "timeout"})),
    # C. 代码生成（断言判分：代码可跑且输出对）
    ("code", "写一个 Python 函数 is_palindrome(s) 判断字符串回文（忽略大小写），只输出代码块，最后加一行 print(is_palindrome('RaceCar'))。",
     lambda a: _code_ok(a, "True")),
    ("code", "写 Python：一行求 [1,2,3,4,5] 的平方和，只输出代码块，最后 print 结果。",
     lambda a: _code_ok(a, "55")),
    ("code", "写 Python 函数 fib(n) 返回第 n 个斐波那契数（fib(0)=0,fib(1)=1），只输出代码块，最后 print(fib(10))。",
     lambda a: _code_ok(a, "55")),
    ("code", "写 Python：统计 'abracadabra' 中每个字母出现次数，输出 dict，只输出代码块，最后 print。",
     lambda a: _code_ok(a, "5")),   # 字母 a 出现 5 次
    # D. 知识问答（关键词判分）
    ("know", "Transformer 注意力机制的核心公式是 Q、K、V 的什么运算？15 字内。",
     lambda a: any(k in a for k in ["点积", "相乘", "QK", "KQ", "乘积", "dot"]) and "V" in a.upper()),
    ("know", "RLHF 的中文全称是什么？10 字内。",
     lambda a: "人类反馈" in a and ("强化" in a or "强化学习" in a)),
    ("know", "GRPO 与 PPO 的最大区别之一是 GRPO 省掉了什么网络？5 字内。",
     lambda a: "价值" in a or "critic" in a.lower() or "Critic" in a or "价值网络" in a),
    ("know", "DeepSeek-R1 训练中用来替代人类偏好打分的奖励类型叫什么？6 字内。",
     lambda a: "可验证" in a or "规则奖励" in a or "RLVR" in a),
]
def _json_ok(ans, expects):
    m = re.search(r"\{.*\}", ans, re.S)
    if not m: return False
    try:
        d = json.loads(m.group())
    except Exception: return False
    return all(str(d.get(k)) == str(v) or d.get(k) == v for k, v in expects.items())
def _code_ok(ans, expect_out):
    m = re.search(r"```(?:python)?\n(.*?)```", ans, re.S)
    code = m.group(1) if m else ans
    if "input(" in code or "os." in code or "open(" in code: return False   # 安全闸（Scope ← rl_agent 安全件）
    import io, contextlib
    try:
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            exec(code, {"__name__": "__main____"})                          # 沙箱级隔离不足，但有输入/文件闸
        return expect_out in buf.getvalue()
    except Exception:
        return False

# ============================================================
# ② prompt 组件空间：8 臂（组件组合 ← 手册 02 ROIF-CSE / 03 五模式）
# ============================================================
def build_prompt(arm):
    """8 臂 = 角色×CoT×契约 的组合采样（few-shot 因上下文成本固定关闭）。"""
    roles = ["", "你是严谨的算法工程师，精准第一。",
             "你是资深 AI 研究员，回答基于事实与计算。"]
    cots  = ["", "先一步步推理，再给出最终答案。"]
    ctrs  = ["", "严格遵循输出要求：不多不少，只输出要求的内容。"]
    bits = [(arm >> 2) & 1, (arm >> 1) & 1, arm & 1]
    return " ".join(x for x in [roles[bits[0]], cots[bits[1]], ctrs[bits[2]]] if x)
ARM_NAMES = [f"臂{a}({'R' if a>>2&1 else '-'}{'C' if a>>1&1 else '-'}{'F' if a&1 else '-'})" for a in range(8)]
BASELINE = ""   # 朴素空 system（对照）

# ============================================================
# ③ UCB bandit 探索（讲透RL/09§P1）+ ④ 决赛配对
# ============================================================
def run(budget_rounds=3):
    rng = random.Random(42)
    n, q = [0]*8, [0.0]*8
    per_arm_tasks = {a: [] for a in range(8)}
    total_calls = 0
    print("=" * 66)
    print(f"GLM-APO：UCB bandit × {MODEL} × RLVR 16 题｜预算 {budget_rounds} 轮×8 臂")
    print("=" * 66)
    for rnd in range(budget_rounds):
        # 每轮每臂 1 题：题序轮转保证每臂见到不同类型（防题偏倚）
        for a in range(8):
            idx = (rnd * 8 + a) % len(TASKS)     # 轮转采样
            cat, q_text, judge = TASKS[idx]
            sys_p = build_prompt(a)
            ans, rt = call_glm(q_text, system=sys_p or None)
            total_calls += 1
            r = 1.0 if judge(ans) else 0.0
            q[a] = (q[a]*n[a] + r) / (n[a]+1); n[a] += 1
            per_arm_tasks[a].append((idx, r))
            print(f"  轮{rnd+1} {ARM_NAMES[a]} {cat:>4} → {'✅' if r else '❌'} (Q={q[a]:.2f}, 思考{rt}tk)")
    # UCB 选优（已采样完，直接均值+置信）
    scores = [(q[a] + (0.3/math.sqrt(max(n[a],1))), a) for a in range(8)]
    scores.sort(reverse=True)
    best = scores[0][1]
    print(f"\n[bandit] 排名: " + " ".join(f"{ARM_NAMES[a]}={q[a]:.2f}" for _, a in scores[:4]))
    print(f"[bandit] 最优臂 = {ARM_NAMES[best]}（Q={q[best]:.2f}，样本{sum(r for _,r in per_arm_tasks[best])}/{n[best]}）")
    # ④ 决赛：最优臂 vs 朴素基线，全 16 题配对对跑
    print(f"\n[决赛] {ARM_NAMES[best]} vs 朴素空system —— 全 16 题配对:")
    wins_best, wins_base, detail = 0, 0, []
    for i, (cat, q_text, judge) in enumerate(TASKS):
        a1, _ = call_glm(q_text, system=build_prompt(best) or None)
        a0, _ = call_glm(q_text, system=None)
        r1, r0 = judge(a1), judge(a0)
        wins_best += r1; wins_base += r0
        if r1 != r0: detail.append(f"{cat}{i}:{'臂✅基线❌' if r1 else '臂❌基线✅'}")
        total_calls += 2
    print(f"  最优臂 {wins_best}/16 vs 基线 {wins_base}/16  分歧题: {detail or '无（全一致）'}")
    print(f"\n★ 最优 prompt（可直接用）:\n   system: {build_prompt(best)!r}")
    print(f"[预算] 实际 API 调用 {total_calls} 次")
    return best, wins_best, wins_base

if __name__ == "__main__":
    if DRY:
        print("[dry] 判分器自检:")
        for cat, _, judge in TASKS[:2]: pass
        print("  math 409:", TASKS[0][2]("答案是 409"), "| json:", _json_ok('{"name":"张三","age":28,"city":"杭州"}', {"age":28}))
        print("  code:", _code_ok("```python\nprint(is_palindrome('RaceCar') if (is_palindrome:=lambda s:s.lower()==s.lower()[::-1]) else 0)\n```", "True"))
    else:
        run()
