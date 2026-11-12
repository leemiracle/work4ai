# 01 — 经典 Agent 范式对比：ReAct vs Plan-Execute vs Reflexion

> 「讲透 Agent」第二篇。上一篇（00）证明"单次 LLM 闭眼猜必败，必须有 Agent 的推理+行动循环"。这一篇解决下一个问题：**循环怎么写？** 把循环写法不同，分出了 Agent 史上三大经典范式。本篇用同一个任务、同一个工具集、200 次重复实测，把三种范式的成功率/token 消耗/失败模式一次跑清楚。
>
> 配套实验：`experiments/01_paradigms.py`。

---

## 1. 灵魂：一句话钉死三种范式

> **ReAct 现场决策、Plan-Execute 先规划后执行、Reflexion 失败后反思——本质是「思考时机」与「是否使用记忆」的差异。ReAct 把思考放在每一步、Plan-Execute 把思考前置、Reflexion 把思考放在失败后。**

$$
\underbrace{\text{ReAct}}_{\text{边走边想}}
\quad\longleftrightarrow\quad
\underbrace{\text{Plan-Execute}}_{\text{想完再走}}
\quad\longleftrightarrow\quad
\underbrace{\text{Reflexion}}_{\text{走错了再想}}
$$

三个范式不是"哪个更好"的关系，而是**三个不同的取舍点**：思考越前置，抗干扰越强但僵化；思考越分散，越灵活但短视；思考越靠后（失败后），单次越快但需要重试。

---

## 2. 直觉：三种范式的比喻

| 范式 | 比喻 | 关键动作 |
|------|------|---------|
| **ReAct** | **现场指挥官**——打仗时根据眼前战况临时决策 | 每一步：观察→思考→行动 |
| **Plan-Execute** | **战前参谋**——开打前先把整套作战方案写下来，士兵只管执行 | 先一次性生成完整计划，再严格按计划走 |
| **Reflexion** | **复盘教练**——第一场打输了没关系，赛后写复盘笔记，下场不再犯同样错 | 失败 → 反思 → 把教训写进记忆 → 重试 |

**一句话区分**：

- ReAct：**"我现在该做什么？"**（每步都问）
- Plan-Execute：**"我整套该怎么做？"**（开始前问一次）
- Reflexion：**"我刚才为什么失败？"**（失败后问）

---

## 3. ReAct：边想边做的现场指挥官

### 3.1 循环结构

```
用户任务
   │
   ▼
┌────────────────────────────────────────┐
│ Thought: 推理 (基于当前 history + obs)   │ ◄─────── 上一步 Observation
│ Action : 选工具+参数                    │
└────────────────────────────────────────┘
   │
   ▼
工具执行 → Observation (环境反馈)
   │
   ▼ (回到 Thought, 直到 LLM 输出 Final Answer)
```

### 3.2 伪代码

```python
def react_agent(task, tools, llm, max_steps=10):
    history = []
    for step in range(max_steps):
        thought, action = llm.decide(task, history)   # LLM 推理
        if action.type == "FINAL":
            return action.answer
        obs = tools[action.name](**action.args)       # 调用工具
        history.append((thought, action, obs))        # 累积到上下文
    return "超出最大步数"
```

### 3.3 优点 / 缺点 / 适用场景

| 优点 | 缺点 | 适用 |
|------|------|------|
| 灵活，能根据中间结果动态调整 | **短视**：每步独立决策，不考虑全局最优 | 工具都可靠、任务流程不固定 |
| 实现简单（业界第一个 Agent 范式） | 工具一多就容易选错（详见实验） | 步数少（≤5 步）的开放性任务 |
| Token 单步成本低 | 失败了不会自我修正 | 探索性、流程无法预先确定的任务 |

**经典反例**：在工具集里同时有 `get_weather`（准）和 `get_weather_guess`（瞎猜），ReAct 每一步独立选，有 ~30% 概率"贪心"选到陷阱工具——这正是实验里 ReAct 只有 60% 成功率的根因。

---

## 4. Plan-Execute：先规划后执行的战前参谋

### 4.1 循环结构

```
用户任务
   │
   ▼
┌──────────────────────────────┐
│ Planner: 一次性生成完整步骤序列  │ ← LLM 调用 1 次, 输出 N 步
└──────────────────────────────┘
   │
   ▼  (严格按 plan 执行, 不再思考)
Step 1: tool_A(...) → obs_1
Step 2: tool_B(...) → obs_2
   ...
Step N: → Final Answer
```

### 4.2 伪代码

```python
def plan_execute_agent(task, tools, llm_planner, llm_executor):
    # === PLAN 阶段 ===
    plan = llm_planner.generate_full_plan(task, tools)  # 一次性输出多步
    # === EXECUTE 阶段 ===
    results = []
    for step in plan:
        obs = tools[step.tool](**step.args)   # 严格按 plan, 不再问 LLM
        results.append(obs)
    return llm_executor.synthesize(task, results)   # 最后再合成答案
```

### 4.3 优点 / 缺点 / 适用场景

| 优点 | 缺点 | 适用 |
|------|------|------|
| **抗干扰**：plan 一旦指定用某工具，后续不会再选错 | **僵化**：plan 漏步或选错，整条执行链全崩 | 任务结构清晰、可预先列出步骤 |
| Token 总成本低（LLM 只调 1-2 次） | 不能根据中间 obs 调整方向 | 多工具易混淆时（plan 显式指定工具） |
| 易并行化（plan 出来后多步可批量跑） | 不适合探索性任务（无法"遇错改道"） | API 编排、ETL、固定流程自动化 |

**真实工程案例**：OpenAI 的 Assistants API、Anthropic 的 Claude 头脑风暴模式、AWS Step Functions + Lambda 编排，本质都是 Plan-Execute——**程序员写死的 Workflow 也属于这一类**（plan 是人写的）。

> ⚠️ **Pipeline ≠ Agent？** 严格意义上，"程序员写死的固定流程"是 Pipeline 不是 Agent。但当 **Planner 由 LLM 充当**（动态生成 plan）时，就跨进了 Agent 的门槛。这是 Plan-Execute Agent 与传统 Workflow 的分水岭。

---

## 5. Reflexion：失败后反思的复盘教练

### 5.1 循环结构

```
用户任务
   │
   ▼
┌──────────────────────────────────┐
│ Episode 1: 跑一次 (通常是 ReAct)   │
└──────────────────────────────────┘
   │
   ▼
成功? → Yes → 返回答案
   │ No
   ▼
┌──────────────────────────────────┐
│ Reflector: 反思为什么失败          │ ← 把失败轨迹+原因写成"教训"
│   "我用了 get_weather_guess,       │
│    它不可靠, 下次别用"             │
└──────────────────────────────────┘
   │
   ▼
把教训加入 memory → 回到 Episode 2 (重试)
   │
   ▼
(最多 N 次, 直到成功或耗尽预算)
```

### 5.2 伪代码

```python
def reflexion_agent(task, tools, llm, max_attempts=3):
    memory = []  # 反思清单
    for attempt in range(max_attempts):
        # 跑一次 (ReAct), 把 memory 注入 system prompt
        result = react_with_memory(task, tools, llm, memory)
        if result.success:
            return result.answer
        # 失败 → 反思
        lesson = llm.reflect(task, result.trace, result.error)
        memory.append(lesson)   # 下次不会再犯同样的错
    return "重试耗尽"
```

### 5.3 优点 / 缺点 / 适用场景

| 优点 | 缺点 | 适用 |
|------|------|------|
| **学得最快**：第二次起成功率暴涨 | 单次任务耗时翻倍（要重试） | 任务难度高、允许重试 |
| 通用：能学会任何"教训"（不仅工具选择） | 反思质量取决于 LLM 自评能力 | 失败可观测、可归因（如代码跑测试） |
| 跨任务复用：memory 可积累 | 反思错位时反而误导（"自我怀疑"） | 长期运行的 Agent（如 Voyager） |

**经典案例**：
- **Reflexion（Shinn et al. 2023）**：在 AlfWorld/HotPotQA 上比 ReAct 提升 11-22%
- **Self-Refine（Madaan et al. 2023）**：让 LLM 给自己的答案挑刺，迭代改进
- **Voyager（Wang et al. 2023）**：Minecraft 里的具身 Agent，把学到的"技能库"作为长期 memory——本质是跨任务的 Reflexion

---

## 6. 数学视角：三种范式都是状态空间搜索

把 Agent 看作在状态空间 $\mathcal{S}$ 里搜索：

$$
\text{Agent}(s_0 \to s_g):\quad s_0 \xrightarrow{a_1} s_1 \xrightarrow{a_2} s_2 \cdots \xrightarrow{a_n} s_g
$$

- $s_0$：初始状态（任务 + 工具集）
- $s_g$：目标状态（任务完成）
- $a_i$：第 $i$ 步动作（通常是工具调用）
- 转移函数 $T(s, a) = s'$：环境（工具执行）决定

三种范式的本质差异，是**搜索策略**：

| 范式 | 搜索策略 | 思考 vs 执行 |
|------|---------|-------------|
| **ReAct** | **贪心搜索**（Greedy）：每步选当前最优 $a_i = \arg\max_a V(s_i, a)$ | 边搜边走 |
| **Plan-Execute** | **开环规划**（Open-loop）：一次性算出整条路径 $\pi = (a_1, ..., a_n)$ | 先算后走 |
| **Reflexion** | **带记忆的重启搜索**：失败 → 更新价值函数 $V \leftarrow V + \alpha \cdot \text{lesson}$ → 重新搜 | 走错了回头再算 |

**关键洞见**：ReAct 是局部最优（每步贪心），Plan-Execute 是开环最优（不考虑环境扰动），Reflexion 通过反思逼近闭环最优。

> 形式化地说：完美的 Plan-Execute（闭环 MPC）需要环境模型 $T$，但 LLM Agent 通常没有 $T$，只能开环。Reflexion 用"试错+反思"在缺失 $T$ 的情况下逼近闭环——这就是它的本质价值。

---

## 7. 实验：同一任务、同一工具集，三种范式跑 600 次

### 7.1 实验设计

**任务族**：3 个多步工具调用任务（查天气/人口 + 计算）。

**工具集（含陷阱）**：

| 工具 | 行为 | 类型 |
|------|------|------|
| `get_weather_official` | 永远返回准确温度 | ✅ 好 |
| `get_weather_guess` | 模拟 LLM 幻觉，偏差 ±5 ~ ±15 | ⚠️ 陷阱 |
| `get_population_official` | 永远返回准确人口 | ✅ 好 |
| `calculate` | 精确计算 | ✅ 好 |
| `calculate_quick` | 25% 概率算错 ±3 | ⚠️ 陷阱 |

**三种范式的差异**（用规则模拟 LLM）：
- **ReAct**：每步以 $p_{\text{trap}} = 0.3$ 的概率"不小心"选到陷阱工具
- **Plan-Execute**：先一次性生成 plan（明确指定用 `_official` 工具），有 20% 概率 plan 漏步或选错
- **Reflexion**：第一次 $p_{\text{trap}} = 0.4$（比 ReAct 还激进），失败后 $p_{\text{trap}} \times 0.3$，最多重试 3 次

### 7.2 跑实验

```bash
cd 讲透Agent/experiments
python3 -u 01_paradigms.py
```

### 7.3 实测结果（200 次/任务，共 600 试验/范式）

```
范式                     成功率      平均步数     平均token         使用过陷阱
----------------------------------------------------------------------
ReAct                60.7%       5.7         343         64.5%
Plan-Execute         83.0%       4.6         536         10.3%
Reflexion            98.2%       9.2         722         77.7%
```

### 7.4 数字解读

1. **ReAct 60.7%**：每步 30% 概率选陷阱 → 跑 2-3 步几乎必踩一次 → 大量任务因数值错误失败。**符合"短视"的预测。**
2. **Plan-Execute 83%**：plan 一旦指定 `_official` 就抗陷阱（陷阱使用率仅 10.3%），但 20% 的 plan bug 拖累上限。**符合"抗干扰但僵化"。**
3. **Reflexion 98.2%**：第一次 ~50%，但反思后第二次起 $p_{\text{trap}}$ 暴跌，几乎不再犯同样错。**符合"学得最快"。**
4. **Token 代价**：Reflexion 是 ReAct 的 **2.1x**（722 vs 343），但成功率是 **1.6x**。Plan-Execute 在两者之间。

### 7.5 反直觉点

- **Plan-Execute 用陷阱率最低（10.3%）**，但 token 反而比 ReAct 高（536 vs 343）——因为 plan 阶段一次性生成完整序列费 token，**但执行阶段每步更省**。
- **Reflexion 用陷阱率最高（77.7%）**，但成功率也最高——因为它**故意**先用激进策略探路（"先试错"），失败后才知道哪些工具不可靠。这是"主动犯错学习"。
- **没有银弹**：Reflexion 不是永远最优——简单任务用 ReAct 更省；流程固定用 Plan-Execute 更稳；高难度可重试才上 Reflexion。

---

## 8. 横评表：何时用哪个

| 维度 | ReAct | Plan-Execute | Reflexion |
|------|:-----:|:------------:|:---------:|
| **思考时机** | 每一步 | 任务开始前 | 失败之后 |
| **是否用记忆** | ❌ | ❌ | ✅（反思清单） |
| **抗工具陷阱** | 差（30% 误选）| 好（plan 显式指定）| 中（首次差，后续好）|
| **Token 成本** | 低（~340）| 中（~540）| 高（~720）|
| **延迟** | 中（多轮 LLM）| 低（LLM 1-2 次）| 高（要重试）|
| **任务结构要求** | 不固定 | 可预先列出 | 失败可观测 |
| **典型框架** | LangChain Agent | AutoGPT、BabyAGI | Reflexion、Self-Refine |
| **典型应用** | 客服、问答 | 工作流自动化、API 编排 | 代码生成（带测试）、解数学题 |

**实战组合拳**（业界主流）：

```
Plan-Execute 做骨架  +  Reflexion 兜底重试  +  ReAct 应对意外
```

例：写代码任务 → Plan-Execute 列出"读需求→写代码→跑测试→修 bug"四步 → 每步用 ReAct 灵活应对 → 测试失败用 Reflexion 反思改进。

---

## 9. 批判：每种范式的失败模式

| 范式 | 致命失败模式 | 真实案例 |
|------|-------------|---------|
| **ReAct** | 死循环：A→B→A→B（每步都"再确认一下"）| GPT-4 早期 Function Calling 经常陷入 |
| **Plan-Execute** | Plan 漂移：环境变了，plan 还在跑老路 | 早期 AutoGPT 任务一长就"忘初心" |
| **Reflexion** | 反思错位：把对的反思成错的，越改越糟 | LLM 自评不准时（数学弱模型）会自我误导 |

**最大教训**：
- ReAct 适合**短而开放**的任务（≤5 步）
- Plan-Execute 适合**长而结构化**的任务（步骤可预先列出）
- Reflexion 适合**可重试且失败可观测**的任务（如带测试的代码）
- 真实生产环境几乎都用**组合**，单范式都不够

---

## 10. 一句话总结

> **ReAct 是现场指挥官（边走边想），Plan-Execute 是战前参谋（想完再走），Reflexion 是复盘教练（走错了再想）。三者本质是「思考时机」与「是否用记忆」的取舍：思考越前置越抗干扰但越僵化；思考越靠后越灵活但需要重试。本实验证明：在同一组带陷阱工具的任务上，Reflexion（98%）> Plan-Execute（83%）> ReAct（60%），但代价是 token 翻 2x。没有银弹——实战几乎都用组合（Plan 骨架 + Reflexion 兜底 + ReAct 应对意外）。**

---

## ✍️ 练习（`01_paradigms.py`）

1. **改陷阱概率**：把 ReAct 的 $p_{\text{trap}}$ 从 0.3 调到 0.1，看成功率会涨到多少。再调到 0.5，看是否跌破 30%。**画出 $p_{\text{trap}}$ vs 成功率曲线。**
2. **加第 4 种范式**：实现 **LATS**（Language Agent Tree Search）——把 ReAct 走出的每步当成树节点，用 MCTS 风格的 UCB 选下一步。看它在陷阱任务上能否超过 Reflexion。
3. **接真 LLM**：把规则 planner 换成豆包/DeepSeek 的 Function Calling，看真 LLM 的 $p_{\text{trap}}$ 是多少（通常 < 5%，远好于规则模拟）。
4. **制造"反思错位"**：故意让 Reflexion 的 reflect 函数给出错误教训（"下次多用 _guess 工具"），看它是否会越改越糟。这是 Reflexion 的最大风险。

---

## 📌 下一步

下一篇 **02-工具调用工程** 把"工具"这件事彻底讲透：从 Function Calling 的 JSON Schema、到工具描述质量对选择正确率的影响、到 MCP（Model Context Protocol）这个 2024 起的新标准——它是 Anthropic 推动的"工具调用 USB-C"，正在统一各家 Agent 框架的工具协议。

---

## 🔗 外部精华

→ 三范式在 2024 后的融合形态：**AgentKit**（arXiv:2404.11483）把 ReAct/Plan-Execute/Reflexion 变成同一张动态 DAG 上的不同节点编排——范式不是互斥选项，是节点编排模式。详见 [PaperAgent精华合入-总入口 §三](../PaperAgent精华合入-总入口.md)。
