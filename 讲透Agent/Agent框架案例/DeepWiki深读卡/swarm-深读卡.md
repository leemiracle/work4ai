# swarm 深读卡 —— 把多 Agent 编排压进一个 while 循环的教育标本：Agent = 提示词 + 工具包，Handoff = 函数返回值

> **定位**：OpenAI 官方实验性、教育性多 Agent 编排框架——run loop 约 100 行、整个 `swarm/` 包仅 4 个文件（core/types/util/repl，<500 行），完全骑在无状态 Chat Completions API 上。用两个原语（`Agent` + **handoff**）表达 agent 网络，无路由器、无调度器、无服务端状态。README 顶部已声明被 production-ready 的 OpenAI Agents SDK（openai-agents-python）取代，其真正价值是定义了后者 Agent/Handoff/Context 的概念原型。

> **本地**：`repos/swarm`（openai/swarm）｜**深读**：deepwiki 22 子页归档 `deepwiki/swarm/full.md`（2026-08-21，3294 行/137.5KB，含 skeleton.md + structure.txt）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 类型层 `swarm/types.py` | Pydantic 数据模型，全部状态的定义 | `Agent`（name/model/instructions/functions/tool_choice/parallel_tool_calls）、`Response`（messages+agent+context_variables）、`Result`、`AgentFunction` |
| 编排层 `swarm/core.py` | 无状态 run loop：补全→工具→切换 Agent | `Swarm.run()` / `run_and_stream()`、`get_chat_completion`、`handle_tool_calls`、`handle_function_result` |
| 工具层 `swarm/util.py` | Python 函数 ↔ OpenAI tools JSON schema 双向桥 | `function_to_json`（inspect.signature + type_map）、`merge_chunk`（流式增量合并）、`debug_print` |
| 交互层 `swarm/repl/` | 命令行演示循环 | `run_demo_loop`（展示"把 Response 喂回下一次 run"的续聊范式） |
| 示例层 `examples/` | 编排模式样本；streaming 示例自成体系 | triage（路由）、airline（多级 handoff+policy）、customer_service_streaming（`AssistantsEngine`/`LocalEngine` 双引擎 + Pydantic 严格工具 schema `tool.py`） |

## 二、核心机制

1. **Handoff = 返回 `Agent` 的普通函数**（来源：Overview「Core Primitives」+ 2.1 Swarm Class「Agent Switching」）：工具函数直接 `return agent_b`，`handle_function_result` 用 match/case 把它规范化为 `Result(value=json.dumps({"assistant": agent.name}), agent=agent)`（core.py:71-87），run loop 检测到 `result.agent` 就地换 active_agent——控制流完全数据化，没有图、没有队列。
2. **Run Loop 五步循环 + 三元组状态**（来源：Overview「The Run Loop」步骤表 + 2.1「Execution Flow」）：①`get_chat_completion` ②`handle_tool_calls` ③执行 Python 函数 ④处理 Handoff ⑤更新 `context_variables`，循环至无 tool_calls 或触 `max_turns`；整个框架的持久状态只有 `(messages, active_agent, context_variables)` 三元组，随 `Response` 返还调用方，服务端零存储（与 Assistants API 的本质区别）。
3. **`context_variables` 签名注入 + 对模型隐身**（来源：3 Tool System「Context Variables Injection」+ 2.1）：函数签名里声明 `context_variables` 参数即被自动注入（core.py:120 用 `func.__code__.co_varnames` 探测），同时该参数从发给 LLM 的 tools schema 中剔除（core.py:51-56）——模型看不见、函数拿得到；函数经 `Result` 回写即实现跨轮共享状态。
4. **零装饰器工具系统**（来源：3 Tool System「Core Logic: function_to_json」）：`inspect.signature` + type_map（str→string、int→integer…缺省 fallback string）把裸函数转 JSON schema，docstring 即 description；返回值多态三分支——`str`（工具输出）/ `Agent`（handoff）/ `Result`（value+agent+context_variables 三合一）。

## 三、与讲透系列的对位

| swarm 原语 | 讲透系列主题 | 对位要点 |
|---|---|---|
| `Agent`（instructions+functions） | 讲透 Agent / LLM 调用 | Agent 无非 system prompt + tools 的打包，Pydantic 6 字段说尽 |
| handoff（返回值即切换） | 讲透多 Agent 协作 / 路由 | 相比 LangGraph/CrewAI 的图与角色编排，这是"函数返回值即边"的最简形态 |
| `Swarm.run()` while 循环 | ReAct / Agent Loop | 补全→工具→更新 的裸 executor，手写 agent loop 的标准模板 |
| `function_to_json` | 工具调用 / function calling / MCP | 无 `@tool` 装饰器的手写 schema 生成器，看清 tool 协议本质 |
| `context_variables` | 记忆机制 / 状态管理 | 状态显式外置、随 Response 往返——"无记忆框架"的记忆方案 |
| triage/airline 示例 | 多 Agent 实战模式 | triage 路由、policy 注入 instructions、多级 handoff 的最小参考实现 |

## 四、关键入口

```python
from swarm import Swarm, Agent          # __init__.py 仅导出 3 个名字

client = Swarm()                        # 内部就是 OpenAI() 客户端，无它物

def transfer_to_agent_b():              # handoff：返回 Agent 即切换
    return agent_b

agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful agent.",   # 也可为 callable(context_variables)->str
    functions=[transfer_to_agent_b],
)
agent_b = Agent(name="Agent B", instructions="Only speak in Haikus.")

response = client.run(                  # ≈ chat.completions.create 的多轮版
    agent=agent_a,
    messages=[{"role": "user", "content": "I want to talk to agent B."}],
    context_variables={},               # 可选：max_turns / model_override / stream / execute_tools / debug
)
print(response.messages[-1]["content"])
# Response = (messages, agent=最后活跃Agent, context_variables) —— 续聊就把它再喂回 run()
```

## 五、深读子页地图（22 页精选 6）

| full.md 行 | 页面 | 为什么值得读 |
|---|---|---|
| L6 | Overview | 全景入口：双原语、Run Loop 五步表、Code↔NL 双空间 3 张 mermaid |
| L365 | Swarm Class (core.py) | 核心 292 行逐方法拆解，handoff/context 的行级代码引用最全 |
| L582 | Types and Data Models | Agent/Response/Result 字段表 + 五步类型流转表，一页看懂数据模型 |
| L1035 | Tool System | function_to_json 类型映射表、context 注入时序图、工具属性总结表 |
| L1435 | Airline Customer Service Example | 多级 handoff + policy 注入的参考实现，含 evals |
| L3175 | Glossary | Turn / Run Loop / Routine / Triage Agent 等术语的代码指针定义 |

（其余：L167 Core Implementation、L729 Utility Functions、L891 REPL、L1193-2247 Examples 六页、L2248-2586 Testing 三页、L2587-3174 Developer Guide 四页）

## 六、与"我们"的关系（一句话）

讲透 Agent 循环/多 Agent 协作的最佳"最小标本"——LangChain/LangGraph 用千行讲的工具、路由、状态、循环四件事，这里各用一个原语压到百行级，是讲透系列"直觉→公式→代码→手写复刻"链条里理想的对照阅读与从零手写起点（其精神继承者 OpenAI Agents SDK 则是生产化对照面）。

---
生成：2026-08-21 · deepwiki 22 页全归档
