"""
实验 00 — 为什么需要 Agent: ReAct 循环 (Reasoning + Acting)
对应文档: 讲透Agent/00-为什么需要Agent.md
核心结论:
  1. 单次 LLM 调用是"闭眼猜": 没有工具、没有中间反馈, 复杂任务必然失败/幻觉
  2. Agent = LLM + 工具 + 循环. 核心是 ReAct 循环: Thought→Action→Observation→...→Final
  3. 每步 Action 调用工具改变环境, Observation 把新信息喂回, Agent 据此调整 —— 像人在环境里探索
  4. 本实验: 真实工具 + 真实循环框架, planner 用规则模拟 LLM(真实Agent用LLM推理)
跑法: python3 -u 00_react.py
"""
def P(*a): print(*a, flush=True)

# ============ 真实工具 (Agent 能调用的) ============
WEATHER = {"北京": "25℃", "上海": "30℃", "广州": "35℃", "深圳": "32℃"}
POPULATION = {"北京": "2189万", "上海": "2487万", "广州": "1881万"}
def calculate(expr):
    try: return str(eval(expr))
    except Exception as e: return f"错误:{e}"
def lookup_weather(city): return WEATHER.get(city, f"未知城市:{city}")
def lookup_population(city): return POPULATION.get(city, f"未知城市:{city}")
TOOLS = {"calculate": calculate, "lookup_weather": lookup_weather, "lookup_population": lookup_population}

# ============ ReAct Agent 框架 (真实循环) ============
def react_agent(task, planner, max_steps=8):
    P("="*60); P(f"任务: {task}"); P("="*60)
    history = []
    for step in range(max_steps):
        thought, action = planner(task, history)        # 决策(真实Agent由LLM生成)
        P(f"\n[Thought {step+1}] {thought}")
        if action[0] == "FINAL":
            P(f"👉 Final Answer: {action[1]}")
            return action[1]
        tool_name, args = action
        P(f"  Action: {tool_name}({args})")
        obs = TOOLS[tool_name](**args)
        P(f"  Observation: {obs}")
        history.append((thought, action, obs))
    P("⚠ 超过最大步数"); return None

# ============ 规则 planner (模拟 LLM 的推理决策) ============
import re
def planner(task, history):
    # 解析"X和Y的温度差/人口差"
    m = re.search(r"(北京|上海|广州|深圳).*?(北京|上海|广州|深圳)", task)
    cities = list(m.groups()) if m else []
    is_weather = "温度" in task or "天气" in task
    is_pop = "人口" in task
    tool = "lookup_weather" if is_weather else "lookup_population" if is_pop else None

    done = {}  # 已查的城市
    for th, act, obs in history:
        if act[0] == tool:
            done[act[1]["city"]] = obs
    # 逐个查
    for c in cities:
        if c not in done:
            return f"需要{c}的数据, 去查", (tool, {"city": c})
    # 都查了, 算差
    if tool and len(done) >= 2:
        vals = [int(re.search(r"\d+", done[c]).group()) for c in cities]
        expr = f"{vals[1]}-{vals[0]}"
        if not any(h[1][0]=="calculate" for h in history):
            return f"两个城市都查到了, 算差值 {expr}", ("calculate", {"expr": expr})
        # 已算完
        calc_obs = [h[2] for h in history if h[1][0]=="calculate"]
        return f"算完了, 给出最终答案", ("FINAL", f"{cities[1]}比{cities[0]}{'温度' if is_weather else '人口'}高/多 {calc_obs[-1]}{'℃' if is_weather else '万'}")
    return "无法规划", ("FINAL", "我不会这个任务")

# ============ Part 1: 单次 LLM 为什么不行 ============
P("="*60); P("Part 1: 单次 LLM 调用为什么搞不定"); P("="*60)
P("任务: '北京和上海的温度差是多少?'")
P("单次 LLM(无工具): 内部知识可能记错温度(幻觉), 也无法保证最新.")
P("  → 可能答 '5℃' (碰巧对) 或 '10℃' (编的), 不可靠.\n")

# ============ Part 2: ReAct Agent 循环解决 ============
P("="*60); P("Part 2: ReAct Agent —— 推理+行动循环"); P("="*60)
react_agent("北京和上海的温度差是多少?", planner)

P("\n"+"="*60); P("Part 3: 再来一个任务 (人口差)"); P("="*60)
react_agent("广州和上海的人口差多少?", planner)

P("\n"+"="*60); P("Agent 的本质"); P("="*60)
P("单次LLM: 输入→输出, 一次定生死, 没有反馈.")
P("Agent  : 输入→Thought→Action(工具)→Observation→Thought→...→Final")
P("  关键: ①工具让LLM突破'只知道训练数据'的限制(查实时/算精确)")
P("        ②循环让LLM根据中间结果调整(像人遇错改策略)")
P("        ③Observation是环境的反馈, 让Agent'睁眼'而非'闭眼猜'")
P("\n注: 本实验planner用规则模拟LLM决策(便于CPU跑通).")
P("    真实Agent的Thought/Action由LLM生成(如GPT/豆包), 更灵活能处理任意任务.")
