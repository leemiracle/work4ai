# agentk 深读卡 —— 一个会自己"造 Agent、造 Tool"的 LangGraph 自进化微内核

> **定位**：AgentK 是 mikekelly 的 self-evolving AGI 实验：仅内置 4-5 个内核 Agent（Hermes 编排 + AgentSmith 造 Agent + ToolMaker 造 Tool + WebResearcher 取知识 + SoftwareEngineer 管代码），其余能力全部由系统在完成任务过程中自我生成。哲学是"K = kernel"——最小内核 + 引导自举，Agent 与 Tool 都是 `agents/`、`tools/` 目录下的普通 Python 文件，git 可追踪、随用随长。
> **本地**：`repos/agentk`（mikekelly/AgentK）｜**深读**：deepwiki 20 子页归档 `deepwiki/agentk/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 框架层 | ReAct 状态机底座 | LangGraph `StateGraph(MessagesState)`、`ToolNode`、LangChain |
| 编排层（内核） | 人机交互、目标规划、调度其他 Agent | `agents/hermes.py`（唯一常驻用户入口，带 checkpointing） |
| 自进化层 | 动态扩产能力 | `agents/agent_smith.py`（造 Agent）、`agents/tool_maker.py`（造 Tool） |
| 知识/代码层 | 联网检索、代码管理 | `agents/web_researcher.py`、`agents/software_engineer.py` |
| 任务执行层 | AgentSmith 现场生成的领域 Agent | `agents/new_agent.py`（运行时产出，文件名=函数名） |
| 工具层 | 文件系统 / Web / Agent 交互 / 自定义 | `tools/write_to_file.py`、`run_shell_command.py`、`duck_duck_go_web_search.py`、`assign_agent_to_task.py`、`list_available_agents.py`… |
| 基础设施 | 注册发现、质量门、隔离部署 | `utils.all_agents()`（Agent Registry）、`tests/agents/` smoke test、Docker + `./agentk` 脚本 |

## 二、核心机制

1. **全员同一 ReAct 状态机**（来源：Overview、2.2 LangGraph Implementation）：每个 Agent 都是 `reasoning 节点 → check_for_tool_calls 条件边 → ToolNode → 回 reasoning` 的循环，无 tool call 即 `END`；状态就是一个 `{"messages": [...]}` 字典。唯一特例 Hermes：入口是 `feedback_and_wait_on_human_input`、出口是用户敲 "exit"，并启用 checkpointing 持久化——差异全部体现在系统提示词 + 图的出入口，节点代码零差异。
2. **自进化闭环**（来源：Overview）：接到新任务 → 能力评估 → 缺 Agent 找 AgentSmith、缺 Tool 找 ToolMaker → 新组件集成入系统 → 执行任务 → 反馈回流供下次复用。系统不是预装所有能力，而是"长出自己的心智"。
3. **Agent 即文件 + 强制质量门**（来源：3.2 AgentSmith）：AgentSmith 用 `write_to_file` 生成 `agents/new_agent.py` 与 `tests/agents/test_new_agent.py`，跑 smoke test，不过就改到过为止；硬性规约：文件名=函数名、`from tools.tool_name import tool_name`、必须用 LangGraph、必须有测试。完成后经 `utils.all_agents()` 注册，Hermes 立即可调度。
4. **防"代理化"设计**（来源：3.2 AgentSmith）：系统提示明确禁止创建" merely proxy to functions "的过度特化 Agent，倾向可复用能力——这是微内核不膨胀的关键自律条款。

## 三、与讲透系列的对位

| AgentK 概念 | 讲透系列对应主题 | 备注 |
|---|---|---|
| ReAct 循环（reasoning↔ToolNode） | 讲透 Agent / 规划推理（ReAct、CoT、ToT） | 三层宪法的"代码层"现成样板：~100 行一个 Agent |
| `StateGraph` + 条件边 | agent-development / LangGraph 模块 | `check_for_tool_calls` 是条件边的最小教学案例 |
| `write_to_file` 造 Agent/Tool | 工具调用与 MCP 协议（元编程：Agent 造 Agent） | 自进化=多智能体协作 × 代码生成闭环 |
| Hermes ↔ AgentSmith ↔ ToolMaker 分工 | 多智能体协作（orchestrator-worker 模式） | 编排者/工厂者角色分离的极简实现 |
| smoke test 质量门 + Docker 隔离 | 工程铁律（可跑通验证、环境隔离） | "生成了必须测过" 与我们 bash 跑通宪法同构 |

## 四、关键入口

```bash
cd repos/agentk
cp .env.template .env    # 填 LLM API key（Configuration → Language Model Setup）
./agentk                 # Docker 隔离启动，进入 Hermes 对话循环（exit 退出）
```

```text
agents/hermes.py          # 编排器：人机入口 + 任务规划 + assign_agent_to_task
agents/agent_smith.py     # Agent 工厂：设计→(缺工具找ToolMaker)→写文件→smoke test→注册
agents/tool_maker.py      # Tool 工厂：同 ReAct 模式，强调工具验证
tools/write_to_file.py    # 自进化的"笔"——所有新 Agent/Tool 由此落盘
tests/agents/             # 质量门：每个新 Agent 必须带 smoke test
```

## 五、深读子页地图（20 页精选 5）

| 子页 | 一句话要点 |
|---|---|
| 1 Overview | 全景：微内核哲学 + 4 内核 Agent + 自进化流程图（已读） |
| 2.2 LangGraph Implementation | ReAct 状态机逐行拆解：StateGraph/条件边/出入口变体（已深读） |
| 3.2 AgentSmith: Agent Creator | Agent 诞生全流程：计划→造工具→写码→测试→注册（已深读） |
| 3.3 ToolMaker: Tool Creator | 与 AgentSmith 对偶的 Tool 工厂，工具验证环节更重 |
| 7.1 Creating New Agents | 开发者视角手动加 Agent 的规约（AgentSmith 的"人肉版"） |

## 六、与"我们"的关系（一句话）

AgentK 是"讲透 Agent"系列最理想的赠品级参考实现——用约 100 行 × 5 个文件演示了 ReAct、LangGraph、多 Agent 编排与 Agent 自造 Agent 的完整闭环，可直接作为"直觉→公式→代码"三层宪法里代码层的解剖标本。

---
生成：2026-08-21 · deepwiki 20 页全归档
