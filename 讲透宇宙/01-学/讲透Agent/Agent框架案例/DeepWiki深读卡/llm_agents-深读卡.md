# llm_agents 深读卡 —— 莱比锡大学教学级 Agent 库：Thought-Action-Observation 循环的最小纯净实现

> **定位**：mpaepper（Leipzig 大学 NLP 组 Marc Pålsson）出品的极简教学型 LLM Agent 库——刻意做"langchain 的简化版"：Agent = Pydantic BaseModel + 一个 Thought-Action-Observation 循环 + ToolInterface 协议，全库仅 4 个源文件。价值不在功能而在**清晰度**：每层抽象都薄到一眼看穿，是讲 ReAct 教学时"先看最小实现再看工业框架"的最佳第一站。
> **本地**：`repos/llm_agents`（mpaepper/llm_agents）｜**深读**：deepwiki 32 子页归档 `deepwiki/llm_agents/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 层 | 中央编排：迭代推理循环/响应解析/工具调度 | `Agent`（agent.py:36-95，Pydantic BaseModel；llm/tools/prompt_template/max_loops/stop_pattern 五属性） |
| LLM 层 | 推理步生成 | `ChatLLM`（openai 兼容，含本地模型） |
| 循环层 | TAO 推理范式 | Thought-Action-Observation Loop（wiki 专页 16KB 详解） |
| 工具层 | 能力扩展协议+实现 | `ToolInterface` 协议 + SerpAPI/GoogleSearch/Searx/HackerNews/PythonREPL 五工具（各一专页） |
| 入口 | 配置与运行 | `run_agent.py`、`.env` 管理 |

## 二、核心机制

1. **Agent=编排器三件套**（The Agent 页）：`Agent` 连接 ChatLLM（生成推理步）+ Tool Registry（执行能力）+ Prompt Management（历史上下文），职责单一：发 prompt→解析出 action+action_input→调工具→observation 回灌 prompt，循环至 final answer 或 max_loops——教科书级 ReAct 骨架，无任何多余抽象。
2. **Thought-Action-Observation 显式循环**（TAO Loop 页 16KB）：与 LangChain 把 ReAct 藏在 AgentExecutor 内部不同，这里 TAO 循环是文档级一等公民——wiki 用整页拆每步的 prompt 构造、stop_pattern 截断、解析失败处理，教学可拆性极强。
3. **ToolInterface 最小协议**（Tool System 页）：工具=实现接口的对象（name/description/use），PythonREPLTool（17KB 专页）演示代码执行工具的完整安全考量；自定义工具指南（Creating Custom Tools 页）三步走。
4. **Pydantic 全程**：Agent 本身是 Pydantic BaseModel——配置即验证，与 lagent 的"Agent 即层"哲学同为 Pythonic 极简路线。

## 三、与讲透系列的对位

| llm_agents 概念 | 讲透系列对应概念 |
|---|---|
| TAO 循环 | 讲透Agent/01 §ReAct（**最小实现标本**，先读它再看 smolagents/swarm） |
| ToolInterface | 讲透Agent/02 §工具调用（协议最小化对照 MCP） |
| stop_pattern/max_loops | 循环终止条件设计 |
| Pydantic Agent | 声明式配置验证 |

## 四、关键入口

```
llm_agents/agent.py        # Agent 类 L36-95：循环编排核心（102 行文件）
llm_agents/__init__.py     # 导出与组装
llm_agents/tools/searx.py  # 自托管搜索工具样例
run_agent.py               # CLI 入口（.env 配 key）
```

## 五、深读子页地图（32 页精选 5）

4 Core Architecture｜5 The Agent（类结构全解）｜**7 Thought-Action-Observation Loop（灵魂页）**｜8-9 Tool System + ToolInterface｜15 PythonREPLTool（代码工具安全）。

## 六、与"我们"的关系（一句话）

讲透Agent 的"手写 ReAct 三十行"教学章可以直接以它为对照答案——比 swarm 更薄（无多 Agent 概念），比 LangChain 清晰三个数量级，是"从零理解 Agent 循环"的纯净起点。

---
生成：2026-08-21 · deepwiki 32 页全归档
