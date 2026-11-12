# xagent 深读卡 —— OpenBMB 自主任务求解 Agent：外循环计划树 × 内循环 ReAct 的工程化范本

> **定位**：OpenBMB（清华系）开源的 LLM 自主任务求解 Agent，用 outer-inner 双循环把复杂任务拆成计划树再逐节点 ReAct 执行。差异化在于：计划是运行时可精炼的"活树"、工具全部跑在 Docker 沙盒 ToolServer 中，并配套 XAgentGen 让开源模型做 function calling。开源社区高热度项目（无正式论文，工程实践型）。
> **本地**：`repos/xagent`（OpenBMB/XAgent）｜**深读**：deepwiki 29 子页归档 `deepwiki/xagent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 接口层 | 人机交互入口 | XAgentWeb（Vue3）、CLI（`run.py`） |
| 服务层 | 对外暴露任务、会话与持久化 | XAgentServer（FastAPI+WebSocket）、MySQL/Redis/MongoDB |
| 认知层 | 规划-执行-反思 | Dispatcher、PlanGenAgent/PlanRefineAgent、ToolAgent、ReflectAgent |
| 流程层 | 双循环驱动 | TaskHandler（`outer_loop`/`inner_loop`）、ReACTChainSearch |
| 数据层 | 计划与记忆 | Plan 树（`data_structure/{tree,plan,node}.py`）、working_memory、vector_db（缓存） |
| 工具层 | 沙盒执行 | ToolServerManager/Monitor/Node（Docker），FileEditor/Notebook/Browser/Shell/RapidAPI |
| 模型层 | LLM 接入 | OpenAI/Azure 请求封装（`ai_functions/request/openai.py`）、XAgentGen 约束解码 |
| 留痕层 | 全量记录与回放 | RunningRecorder、recorder.py、RecordDir |

## 二、核心机制

1. **Outer-Inner 双循环，计划是"活树"**（来源：Task Planning System）：`outer_loop` 对 Plan 树做中序遍历逐个取子任务，`inner_loop` 为每个子任务起一条 ReACT 链；子任务失败时 PlanRefineAgent 用 SPLIT/ADD/DELETE/EXIT 四算子改树再继续。创新点：计划不是一次性 TODO，而是运行时可增/删/拆的数据结构，且树宽/深/精炼链长全部有界（默认 4/3/4）防失控——区别于 AutoGPT 式线性任务队列。
2. **"计划即工具"的函数调用调度**（来源：Task Planning System + Tool System）：计划生成与精炼本身通过 `ai_functions`（如 `task_manage_functions.yml`）以 function call 让 LLM 输出结构化 JSON（subtask name / goal / criticism / milestones），Pydantic schema 校验、失败自动重试修复。创新点：把"管理计划树"也建模成与执行工具同一套 schema 校验管道的 LLM 工具调用。
3. **Docker 级工具沙盒**（来源：Architecture + ToolServer Architecture）：工具不嵌入 Agent 进程，ToolServerManager 动态创建 ToolServerNode 容器，NodeChecker 心跳健康检查、用完即回收。创新点：安全隔离做到部署层（容器编排），而非库层 try/except，Shell 等高危操作不威胁宿主机。
4. **反思回写 + 开源模型约束解码**（来源：Task Planning System + Model Generation）：每子任务完成后 ReflectAgent 提取 Summary/Plan Reflection/Tool Reflection 三类后验知识注入后续规划；XAgentGen 用 Pydantic→正则→constrained logits 链路让 XAgentLlama 等自训开模型稳定输出复杂 JSON function call。创新点：轻量"经验回写"记忆 + 不绑死 OpenAI 的自定义模型兜底。

## 三、与讲透系列的对位

| XAgent 概念 | 讲透系列对应概念 |
|---|---|
| outer_loop 计划树遍历 + Refine 四算子 | 讲透多Agent协作：编排模式（planner-executor 分层 / replan） |
| inner_loop ReACTChainSearch | 讲透Agent：ReAct 循环（思考-行动-观察） |
| ai_functions 函数调用 + Pydantic 校验重试 | 讲透Agent：工具调用 / 结构化输出（上下文工程） |
| ToolServer Docker 容器隔离 | 讲透Agent：安全沙盒 |
| ReflectAgent 后验知识回写 | 讲透学习型Agent：记忆机制 / 自进化 |

## 四、关键入口

```python
XAgent/workflow/task_handler.py              # outer_loop()/inner_loop()：双循环主控，子任务调度与失败重试
XAgent/workflow/plan_exec.py                 # Plan 树数据结构 + PlanAgent（initial_plan_generation / refine_plan）
XAgent/agent/plan_refine_agent/prompt.py     # SPLIT/ADD/DELETE/EXIT 四算子的提示词定义
XAgent/inner_loop_search_algorithms/ReACT.py # ReACTChainSearch.run()：内循环思考-行动链搜索
XAgent/agent/dispatcher.py                   # 按任务动态实例化各 Agent 的工厂/分发器
XAgent/toolserver_interface.py               # 与 ToolServer 的 HTTP 接口（工具清单获取 + 调用）
XAgent/running_recorder.py                   # 全量留痕：LLM/工具/计划变更五类记录，可回放
XAgentGen/xgen/text/generate/regex.py        # Pydantic→正则约束解码，开源模型 function calling
```

## 五、深读子页地图（29 页精选 6）

1. **Task Planning System**（p5）：双循环 + 四精炼算子 + 计划树 API，全书认知核心
2. **ToolServer Architecture**（p11）：Manager/Monitor/Node 三件套与容器生命周期、健康检查
3. **Tool Types and Capabilities**（p12）：FileEditor/Notebook/Browser/Shell/RapidAPI 五类工具逐一拆解
4. **Task Recording**（p9）：RunningRecorder 五类留痕与 CLI/Server 双模式记录回放
5. **Model Generation**（p25）：Pydantic→regex→logits 约束解码全链路
6. **XAgent Core**（p4）：Dispatcher/Planner/Actor/Recorder 职责切分总览

## 六、与"我们"的关系（一句话）

想看"计划可运行时重构 + 工具进沙盒"在真实工程里如何落地，这是比 AutoGPT 更干净的双循环参考实现，是学任务分解与编排模式的最佳解剖标本之一。

---
生成：2026-08-21 · deepwiki 29 页全归档（注：编排为 Dispatcher→TaskHandler 双循环，非 AWEL——AWEL 属 DB-GPT）
