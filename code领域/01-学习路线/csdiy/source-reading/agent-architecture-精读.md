# Agent 架构精读：从 ReAct 到多智能体

> 参照：ReAct (Yao 2022) / LangGraph / AutoGPT / CrewAI / OpenAI Assistants API
>
> csdiy 对应：agent-development skill + tinyrag + prompt-engineering + tinyllm

---

## 一、Agent = LLM + 工具 + 记忆 + 规划

```
传统 LLM: 输入文本 → 输出文本（无状态）
Agent:   输入目标 → 自主规划 → 调用工具 → 观察 → 迭代 → 完成目标

Agent 的 4 个组件：
  ① LLM（大脑）: 推理 + 决策
  ② Tools（手脚）: 搜索/计算/API/代码执行
  ③ Memory（记忆）: 短期（对话历史）+ 长期（向量库）
  ④ Planning（规划）: 任务分解 + 反思 + 重试
```

---

## 二、ReAct：最基础的 Agent 模式

```
循环：
  Thought: "我需要搜索最新天气"
  Action: search("北京 天气")
  Observation: "北京今天 25°C 晴"
  Thought: "25°C 适合户外活动"
  Action: respond("北京 25°C，适合外出")
  Done.
```

### 实现（参照 prompt-engineering-deep精读）

```python
react_prompt = f"""
You have access to these tools: {tools_schema}

Use this format:
Thought: <reasoning>
Action: <tool_name>(<args>)
Observation: <tool_result>
... (repeat)
Thought: I now know the answer
Action: respond(<answer>)

Goal: {user_goal}
"""
```

---

## 三、Agent 框架对比

### LangChain（最流行）

```python
from langchain.agents import create_react_agent

agent = create_react_agent(llm, tools, prompt)
result = agent.invoke({"input": "预订明天北京的机票"})
```

**特点**：生态丰富，链式组合（Chain），但复杂度高。

### LangGraph（新一代）

```python
from langgraph.graph import StateGraph

graph = StateGraph(AgentState)
graph.add_node("plan", plan_node)
graph.add_node("execute", execute_node)
graph.add_node("reflect", reflect_node)
graph.add_edge("plan", "execute")
graph.add_conditional_edges("execute", should_reflect)
```

**特点**：图结构（DAG），状态管理，循环+分支。

### CrewAI（多智能体协作）

```python
from crewai import Agent, Task, Crew

researcher = Agent(role="Researcher", goal="收集信息", llm=llm)
writer = Agent(role="Writer", goal="写报告", llm=llm)

crew = Crew(agents=[researcher, writer],
            tasks=[research_task, write_task])
result = crew.kickoff()
```

**特点**：角色分工，顺序/并行任务。

### OpenAI Assistants API

```python
assistant = openai.beta.assistants.create(
    model="gpt-4",
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
)
thread = openai.beta.threads.create()
openai.beta.threads.messages.create(thread.id, role="user", content="分析数据")
```

**特点**：托管服务，内置代码执行 + RAG + Function Calling。

---

## 四、Function Calling（工具调用）

### 模式

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "北京天气如何？"}],
    tools=tools,
)

# 模型返回 tool_call
# → 执行 get_weather("北京")
# → 把结果返回给模型
# → 模型生成最终回答
```

### 和 ReAct 的区别

```
ReAct: 文本格式（Thought/Action/Observation）→ 需要解析
Function Calling: 结构化 JSON → 原生支持

→ Function Calling 更可靠（但需要 API 支持）
→ 开源模型也支持（如 Qwen/LLaMA-3 的 tool_use）
```

---

## 五、记忆机制

### 短期记忆（工作记忆）

```
对话历史 → LLM context window
  "用户问了什么，我回答了什么"

问题: context window 有限（4K-200K）
→ 超出后需要摘要/截断
```

### 长期记忆（向量存储）

```
把历史交互存入向量数据库 → 需要时检索

用户: "上次你帮我分析的 Python 项目叫什么？"
Agent:
  ① 向量检索: search("Python 项目分析")
  ② 找到历史对话片段
  ③ 回答: "上次分析的是 tinytorch 框架"
```

### 记忆管理

```
① 摘要: 定期把旧对话摘要压缩
② 实体提取: "用户喜欢 Python" → 存入知识图谱
③ 情感追踪: "用户越来越不耐烦" → 调整回复风格
④ 反思: "上次这个方法失败了 → 这次换方法"
```

---

## 六、规划策略

### Plan-and-Execute（先规划再执行）

```
Plan:
  1. 搜索 API 文档
  2. 阅读认证部分
  3. 编写代码示例
  4. 测试代码

Execute:
  Step 1: search("REST API authentication") → ...
  Step 2: read(result) → ...
  ...
```

### Reflexion（自我反思）

```
Attempt 1: 生成代码 → 测试失败
Reflect: "错误是缺少 import，下次注意"
Attempt 2: 生成代码（带 import）→ 测试通过
```

### Tree of Thoughts（树搜索规划）

```
对于复杂任务，生成多个候选计划 → 评估 → 选最优 → 执行
```

---

## 七、多智能体协作

### 模式

```
① 层级式（Hierarchical）:
   Manager Agent → 分配任务 → Worker Agents → 汇报

② 对话式（Conversational）:
   Agent A ↔ Agent B → 讨论 → 共同决策

③ 流水线式（Pipeline）:
   Agent A(搜索) → Agent B(分析) → Agent C(写作)

④ 竞争式（Adversarial）:
   Generator Agent vs Critic Agent → 对抗优化
```

### 典型应用

```
AutoGPT: 自主完成复杂目标（写代码/调试/部署）
Devin: 自主软件工程师（端到端开发）
MetaGPT: 多角色软件开发（PM/架构师/工程师/测试）
ChatDev: 对话式软件开发
```

---

## 八、Agent 的挑战

| 挑战 | 描述 | 当前解法 |
|------|------|---------|
| 幻觉 | Agent 编造不存在的工具/API | 严格 tool schema 验证 |
| 循环 | Agent 陷入无限循环（重复调用） | 最大步数限制 + 检测 |
| 成本 | 每步调用 LLM → token 消耗大 | 缓存 + 小模型路由 |
| 可靠性 | Function Calling 格式错误 | 重试 + 结构化输出 |
| 安全 | Agent 执行危险操作 | 人工确认 + 沙箱 |

---

## 九、一句话总结

> Agent = LLM + 工具 + 记忆 + 规划 → 自主完成目标。
>
> ReAct（Thought-Action-Observation）= 最基础模式。
> LangGraph = 图结构编排（当前最灵活）。
> Function Calling = 结构化工具调用（比 ReAct 更可靠）。
>
> **Agent 是 LLM 从"聊天机器人"进化到"数字员工"的关键。**

---

*配套：[prompt-engineering-deep精读](prompt-engineering-deep-精读.md) | [tinyrag/pipeline.py](../projects/tinyrag/pipeline.py) | [tinyllm/serve.py](../projects/tinyllm/serve.py)*
