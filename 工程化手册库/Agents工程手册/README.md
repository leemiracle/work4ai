# Agents 工程手册

> **建立**：2026-08-13
> **是什么**：AI Agent = LLM + 工具 + 多轮规划 + 记忆。让 LLM 从"只会说"变成"会做事"。
> **为什么重要**：2024+ Agent 是 LLM 应用层最热方向（Devin / Cursor / Claude Computer Use / Operator）。

---

## 1. 是什么 + 为什么

**Agent 的本质**：让 LLM **自主决策 + 调用工具 + 多轮迭代**，完成复杂任务。

**vs 普通聊天**：
- 聊天：用户问 → LLM 答（1 轮）
- Agent：用户给目标 → LLM 规划 → 调工具 → 看结果 → 再规划 → ... → 完成（N 轮）

**2026 现状**：
- Devin（Cognition）：AI 软件工程师
- Claude Computer Use：直接操作电脑
- Cursor Agent：编程 Agent
- OpenAI Operator：浏览器 Agent
- 多 Agent 系统（CrewAI / AutoGen）

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个 Agent 系统（tools / planning / memory / safety）|
| **说** | 用 Agent 圈行话（ReAct / function calling / tool schema / trajectory）|
| **读** | 读 Agent 论文（ReAct / Reflexion / Toolformer / Voyager）|
| **写** | 搭建一个生产级 Agent |

---

## 3. TPRMS 解析框架

```
T - Tools（工具）：Agent 能调什么
P - Planning（规划）：怎么分解任务
R - Reasoning（推理）：怎么决定下一步
M - Memory（记忆）：怎么记住历史
S - Safety（安全）：怎么防止失控
```

### T · Tools（工具）
| 类型 | 例子 |
|------|------|
| 搜索 | web_search / wiki_search |
| 代码 | python_exec / sql_query |
| 文件 | read_file / write_file |
| API | send_email / create_issue |
| 浏览器 | click / type / screenshot |
| 模型 | vision_check / summarize |

**关键**：tool schema（JSON）描述清楚 + 错误处理。

### P · Planning（规划）
| 策略 | 何时用 |
|------|--------|
| Zero-shot（直接做）| 简单任务 |
| Plan-and-Execute（先规划再执行）| 复杂任务 |
| ReAct（想一步做一步）| 不确定任务 |
| Tree-of-Thoughts（探索多条路径）| 推理任务 |
| Reflexion（失败后反思）| 可验证任务 |

### R · Reasoning
- **CoT**（Chain of Thought）：逐步推理
- **Function Calling**：结构化输出 tool call
- **Extended Thinking**（o1 / Claude thinking）：模型自己想

### M · Memory
| 类型 | 实现 |
|------|------|
| 短期（对话历史）| context window |
| 长期（跨会话）| 向量库 / 知识图谱 |
| 工作记忆（当前任务）| scratchpad |

**工具**：mem0 / Letta / Zep / LangGraph state

### S · Safety
- **最大步数限制**（防止无限循环）
- **危险操作确认**（删文件 / 发邮件）
- **沙箱执行**（代码在容器跑）
- **人类审批**（关键步骤暂停等人确认）

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | 任务完成率（黄金任务集）|
| **2. 可靠性** | 同样任务多次跑一致吗 |
| **3. 效率** | 平均步数 / token 消耗 / 成本 |
| **4. 可控性** | 失败时可中断 / 可回溯 |
| **5. 安全性** | 无危险操作 / 无信息泄漏 |
| **6. 成本** | $/task（含 LLM 调用 + 工具执行）|

### Benchmark
- **AgentBench**：多任务 Agent 评测
- **SWE-bench**：软件工程 Agent
- **WebArena**：浏览器 Agent
- **GAIA**：通用 Assistant

---

## 5. 工具栈（2026-08）

### 框架
| 框架 | 特点 | 适用 |
|------|------|------|
| **LangGraph** | 状态机 + 图，最灵活 | 复杂 Agent |
| **AutoGen**（Microsoft）| 多 Agent 对话 | 多 Agent 协作 |
| **CrewAI** | 角色化 Agent | 团队模拟 |
| **OpenAI Assistants API** | 托管 | 简单部署 |
| **Anthropic Computer Use** | 操作电脑 | 桌面自动化 |
| **LlamaIndex Agents** | RAG + Agent | 知识密集 |

### Agent 产品（参考）
| 产品 | 类型 |
|------|------|
| **Devin**（Cognition）| 软件工程 |
| **Cursor Agent** | 编程 |
| **Claude Computer Use** | 桌面 |
| **OpenAI Operator** | 浏览器 |
| **Manus** | 通用 |

### 记忆系统
- **mem0**：记忆提取与管理
- **Letta**（原 MemGPT）：长期记忆
- **Zep**：时序记忆

---

## 6. 跨平台差异

| 维度 | LangGraph | AutoGen | CrewAI | OpenAI Assistants |
|------|---|---|---|---|
| 架构 | 状态图 | 多 Agent 对话 | 角色 + 任务 | 单 Agent 托管 |
| 灵活性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | 陡 | 中 | 平 | 极平 |
| 生产就绪 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 多 Agent | ✅ | ✅✅ | ✅ | ❌ |
| 成本 | 自托管 | 自托管 | 自托管 | 按量付费 |

---

## 7. 实战案例

### 案例 1：ReAct Agent（LangGraph）

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # 实际实现
    return f"Results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    return str(eval(expression))  # ⚠️ 生产用 ast.literal_eval

model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = [search_web, calculate]

agent = create_react_agent(model, tools)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the population of Tokyo times 2?"}]
})
print(result["messages"][-1].content)
```

### 案例 2：多 Agent 协作（CrewAI）

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find latest AI papers",
    backstory="Expert at finding academic papers",
    tools=[search_web],
    llm="claude-3-5-sonnet"
)

writer = Agent(
    role="Writer",
    goal="Write a blog post",
    backstory="Expert tech writer",
    llm="claude-3-5-sonnet"
)

research_task = Task(
    description="Find 3 recent interp papers",
    agent=researcher,
    expected_output="List of 3 papers with summaries"
)

write_task = Task(
    description="Write a blog post about the papers",
    agent=writer,
    expected_output="1000-word blog post",
    context=[research_task]  # 依赖研究结果
)

crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
result = crew.kickoff()
```

---

## 8. 反模式 10 条

1. **无最大步数**（Agent 无限循环烧钱）
2. **工具 schema 模糊**（模型不知道何时调）
3. **无错误处理**（工具失败 → Agent 崩）
4. **不沙箱执行代码**（任意代码 = 安全灾难）
5. **危险操作无确认**（删文件 / 发邮件）
6. **记忆无上限**（context 爆炸）
7. **不评估就上线**（Agent 不可靠 → 用户流失）
8. **单 Agent 干所有事**（应该多 Agent 分工）
9. **不记录 trajectory**（无法 debug）
10. **忽视成本**（Agent 10 步 = 10x LLM 调用）

---

## 9. 下一步

- 读 ReAct 论文（arXiv 2210.03629）
- 读 Reflexion 论文（arXiv 2303.11366）
- 用 LangGraph 搭一个 ReAct Agent
- 用 CrewAI 搭一个多 Agent 系统
- 跑 SWE-bench / AgentBench 评估

---

**版本**：v1.0（2026-08-13）
**核心理念**：**Agent = LLM + 工具 + 规划 + 记忆 + 安全。让 AI 从"会说"变成"会做"。**
