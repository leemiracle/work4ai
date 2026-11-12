# praisonai 深读卡 —— 一份 agents.yaml 声明式定义，可切换 AutoGen/CrewAI/原生三种执行后端

> **定位**：低代码多 Agent 平台：UI+代码双模式，wrapper 层通过 FrameworkAdapterRegistry 把 AutoGen/CrewAI 当可插拔执行引擎。曾获 Elon Musk 推特引用、Trendshift 徽章，无论文背书（工程驱动型项目）。注意：声明式定义文件是 `agents.yaml`（不是 agents.md）；根目录 `AGENTS.md` 是 monorepo 架构约束文件，勿混淆。
> **本地**：`repos/praisonai`（MervinPraison/PraisonAI）｜**深读**：deepwiki 97 子页归档 `deepwiki/praisonai/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 用户界面 | CLI / TUI / Chainlit Web UI / Claw Dashboard / Telegram·Slack·Discord bot | `praisonai` CLI、`TUIApp`、`WebSocketGateway` |
| 编排适配 | agents.yaml 解析、框架路由、NL 自动生成 | `PraisonAI`、`AgentsGenerator`、`FrameworkAdapterRegistry` |
| 框架后端 | 原生 / AutoGen(v0.2/v0.4/AG2) / CrewAI 执行引擎 | `PraisonAIAdapter`、`AutoGenAdapter`、`CrewAIAdapter` |
| 核心 Agent | Agent 生命周期 / 任务 / 工作流 / 记忆 | `Agent`（mixin 分解）、`Agents`、`Task`、`Workflow` |
| 能力协议 | 工具 / MCP / A2A / RAG 知识库 | `ToolRegistry`、`MCP`、`A2A`、`Knowledge`（ChromaDB/Mem0/Mongo） |
| 安全控制 | guardrails / 人工审批 / 策略引擎 / doom-loop 检测 | `Guardrail`、`ApprovalRegistry`、`PermissionsManager`、`DoomLoopDetector` |
| 基础设施 | 沙盒 / 云部署 / 微调训练 / 24/7 调度 | `SandboxManager`、`Deploy`、`LLMTrainer`、`AgentScheduler` |

## 二、核心机制

1. **框架无关的声明式定义**（来源：praisonai Package、Architecture Overview）——`agents.yaml` 一份配置描述 role/goal/instructions/tools，`framework:` 字段（或环境变量）经 `FrameworkAdapterRegistry` 运行时路由到三个后端；`BaseFrameworkAdapter` 用能力标志（`SUPPORTS_SESSION_CONTINUITY/ASYNC/WORKFLOW`）做能力门控，AutoGen 适配器还能按 `AUTOGEN_VERSION` 在 v0.2/v0.4/AG2 间动态切换。**创新点本质**：同类框架都绑定自家 runtime，PraisonAI 把竞品框架降格为可插拔执行引擎，用一份 YAML 对冲框架选型风险。
2. **NL→YAML→执行团队的两级自动生成**（来源：praison Package、Overview）——`auto.py` 用 LLM 把一句话 topic 直接生成完整 agents.yaml（支持与已有文件 merge）；`AgentsGenerator` 再把 YAML 归一化（`_normalize_yaml_config`）、重名检测（`_list_to_dict`）、工具超时强制（`ToolTimeoutError`+线程池）后实例化为 Agent 团队。**创新点本质**：低代码的落点不是拖拽 UI，而是"配置生成本身也自动化"。
3. **九包 monorepo 分层 + 懒加载**（来源：Overview、Architecture Overview）——`praisonaiagents` 纯净核心 + 7 个专用包（code/bot/train/browser/mcp/sandbox/deploy）+ wrapper 层，靠 `_wrapper_bridge` 等桥接模块维持单向依赖；`__getattr__` 懒加载使启动 ~20ms、Agent 实例化 3.77μs；依赖方向由 `AGENTS.md` + CI import 门禁（甚至 AI reviewer）强制执法。**创新点本质**：把"架构约束"写成机器可执法的宪法，而非口头约定。
4. **双层 doom-loop 检测 + 分层安全栈**（来源：Loop Detection and Safety Escalation、Guardrails）——确定性 `LoopDetectionPlugin`（插件钩子）+ 启发式 `DoomLoopDetector`（escalation 目录）两层检测卡死循环，触发安全升级管道；外加函数/LLM 双型 guardrails、人工审批注册表、策略引擎、shell 命令分解与工作区边界，构成纵深防御。

## 三、与讲透系列的对位

| PraisonAI 概念 | 讲透系列对应概念 |
|---|---|
| agents.yaml 声明式定义 + AgentsGenerator | 讲透Agent：配置驱动的 Agent 定义 / 低代码编排模式 |
| FrameworkAdapterRegistry 三后端切换 | 讲透多Agent协作：框架选型对比 + 编排模式（同一抽象映射不同 runtime） |
| Five-Layer Stack（Prompt/Context/Harness/Loop/Graph） | 上下文工程（Context 层）+ ReAct 循环（Loop 层）+ 编排模式（Graph 层） |
| reflection 三档自反思 / planning TodoTools | ReAct 循环的反思与规划增强 |
| 双层 doom-loop + guardrails + approval | 安全沙盒与自主性边界 |
| Skills 自改进循环 + praisonai-train 训练闭环 | 自进化 / 学习型Agent |

## 四、关键入口

```python
src/praisonai/praisonai/cli/main.py            # PraisonAI 编排器：读 agents.yaml、framework 路由总入口
src/praisonai/praisonai/agents_generator.py    # agents.yaml → Agent 团队（YAML 归一化/重名检测/工具超时）
src/praisonai/praisonai/framework_adapters/    # base+registry + praisonai/crewai/autogen 三适配器（双框架支持核心）
src/praisonai/praisonai/auto.py                # 一句话 topic → 自动生成 agents.yaml（可 merge 既有配置）
src/praisonai-agents/praisonaiagents/agent/agent.py   # 核心 Agent 类（chat/execution/tool/durable mixin 分解）
src/praisonai-agents/praisonaiagents/agents/agents.py # Agents/AgentTeam 多 agent 编排（sequential/parallel/hierarchical/workflow）
src/praisonai-agents/praisonaiagents/mcp/mcp.py       # MCP client+server 双模式（Agent 可反向暴露为 MCP 服务）
AGENTS.md                                      # monorepo 架构宪法：CI import 门禁 + AI reviewer 执法依赖方向
```

## 五、深读子页地图（97 页精选 6）

1. **Architecture Overview** — 五层栈→代码实体映射 + 九包依赖图，最快建立全局心智模型
2. **praisonai Package** — 双框架适配器 + AgentsGenerator + auto 生成 + 调度器，wrapper 层主线全在这
3. **Multi-Agent Orchestration** — AgentTeam 四种 process 策略与层级委派（Manager Schema）
4. **Loop Detection and Safety Escalation** — 双层 doom-loop 检测与协作取消，自主 Agent 安全设计范本
5. **MCP Protocol** — 既是 MCP client（消费工具）也是 server（`praisonai-mcp` 把 Agent 暴露成工具）
6. **LLM Fine-Tuning and Agent Training** — 微调 + AgentTrainer 训练闭环，看"运行时 Agent→数据集→更强模型"的自进化路径

## 六、与"我们"的关系（一句话）

对学 Agent 的人，这个仓库的最大价值是给出"框架适配器模式"的生产级实现——一份 YAML 同时对比 AutoGen/CrewAI/原生三套执行引擎的差异，等于一次读懂三个框架的公共抽象与分歧点。

---
生成：2026-08-21 · deepwiki 97 页全归档
