# metagpt 深读卡 —— 用 `Code = SOP(Team)` 把软件公司流水线编译成多 Agent 协议的开山框架

> **定位**：MetaGPT 把人类软件公司的标准作业流程（SOP）"物化"为多 Agent 协作协议：一行需求进来，ProductManager→Architect→ProjectManager→Engineer→QaEngineer 按瀑布式 SDLC 接力产出 PRD→系统设计→任务分解→可执行代码仓（论文 arXiv:2308.00352，ICLR 2024 oral）。其本质是"装配线而非聊天室"——每个 Role 消费上游的**结构化产物**而非自由对话，这是它降幻觉、提一致性的核心。新版已自我革命为 RoleZero/MGX 的"动态智能"路线（无固化 SOP 的自主 Agent）。
> **本地**：`repos/metagpt`（geekan/MetaGPT）｜**深读**：deepwiki 34 子页归档 `deepwiki/metagpt/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | hire 角色、investment 预算控制、按 `n_round` 驱动循环 | `Team`、`Environment`/`MGXEnv`、`CostManager`（超支抛 `NoMoneyException`） |
| 角色层 | observe→think→act 循环、消息订阅 | `Role`、`RoleContext`、`RoleReactMode`（REACT / BY_ORDER / PLAN_AND_ACT） |
| 行动层 | 一次 LLM 调用产出结构化文档/代码 | `Action`、`ActionNode`/`ActionOutput`（`WritePRD`/`WriteDesign`/`WriteTasks`/`WriteCode`…） |
| 通信层 | 广播+订阅路由，`cause_by` 即路由键 | `Message`（id/content/instruct_content/cause_by/sent_from/send_to）、`MessageQueue`(asyncio.Queue)、`<all>/<self>/<none>` 常量 |
| 记忆层 | 按 `cause_by` 索引历史消息 | `Memory.get_by_actions`、`RoleZeroLongTermMemory`（memory_k=200 + Chroma RAG 转存） |
| LLM 层 | 多厂商适配与成本追踪 | `BaseLLM`、`config2.yaml`、`Context`（Config+LLM+CostManager 的服务定位器） |
| 动态智能（DI） | 无固定 SOP 的自主规划+工具调用 | `RoleZero`、`TeamLeader`(Mike)、`Engineer2`(Alex)、`DataAnalyst`(David)、`tool_execution_map` |
| 增强层 | 检索增强与工具扩展 | `SimpleEngine`(RAG)、`ToolRegistry` |

## 二、核心机制

1. **SOP 物化 = watch 订阅拓扑**（来源：Software Company Metaphor / Role System 页）。流水线没有中央调度器硬编码顺序：每个 Role 在初始化时声明 `watch`（一组 Action 类名集合），上游 Action 的产物以 `Message(cause_by=ActionX)` 广播进环境，命中订阅的 Role 才把它拉进私有 `msg_buffer`。瀑布接力即订阅图——PM watch `UserRequirement`，Architect watch `WritePRD`，Engineer watch `WriteTasks`。
2. **observe→think→act 三段循环**（来源：Role System / Message Passing System 页）。`_observe()` 从 `msg_buffer.pop_all()` 并按 watch 过滤后写入 memory；`_think()` 依 `RoleReactMode` 选出 `todo` Action（多 Action 时用 `STATE_TEMPLATE` 让 LLM 输出状态编号选择）；`_act()` 执行 Action 并 `publish_message` 回环境。`MESSAGE_ROUTE_TO_SELF`（`<self>`）让 QaEngineer 自己触发 WriteTest→RunCode→DebugError 的调试迭代。
3. **结构化产物即角色间合同**（来源：Overview / Software Company Metaphor 页）。每个 Action 通过 `ActionNode` 输出 Pydantic 约束的结构化中间表示（`instruct_content: BaseModel`），下游消费"装配好的零件"而非原始文本——这正是论文中 assembly line 范式的代码落地。
4. **RoleZero：从固化 SOP 到动态智能**（来源：RoleZero 页）。新版把"角色=SOP"翻转为"角色=规划器+工具箱"：`_quick_think` 将输入分流为 QUICK（直答）/TASK（走 Planner）/SEARCH（RAG 问答）；复杂任务通过 `tool_execution_map` 把字符串命令绑定到函数（`Plan.append_task`、`ask_human`、`Editor.write`、`Browser.goto`…）；`MGXEnv` 把所有消息接管给 TeamLeader 再显式路由（数据任务→DataAnalyst，软件任务→PM/Architect/Engineer 流水线）；记忆超 memory_k=200 后旧消息转存 Chroma 长期库，`experience_retriever` 把成功轨迹注入当前 prompt。

## 三、与讲透系列的对位

| MetaGPT 概念 | 讲透系列落点 |
|---|---|
| observe→think→act、RoleReactMode | Agent 规划推理（ReAct vs Plan-and-Act 的现成双模式对照实验） |
| Message/cause_by 订阅路由 | 多智能体协作（"通信协议=数据结构"的教科书案例，可画订阅图） |
| ActionNode 结构化输出 | Prompt 工程/结构化输出（Pydantic 约束生成的工业级用法） |
| Memory + RoleZeroLongTermMemory | 记忆机制（短期截断 + RAG 长期转存的完整工程闭环） |
| SOP 物化 vs RoleZero 动态化 | agent-development 框架选型（与 LangGraph 图编排/CrewAI 顺序编排对比的一等素材） |

## 四、关键入口

```python
# repos/metagpt（均已本地核实存在）
metagpt/software_company.py    # generate_repo()：hire 一条标准软件公司流水线
metagpt/team.py                # Team.run()：run_project 发布 idea → n_round 循环 → archive
metagpt/roles/role.py          # Role 基类：_observe/_think/_act + watch/publish_message
metagpt/schema.py              # Message（cause_by 路由键）+ MessageQueue
metagpt/roles/di/role_zero.py  # RoleZero：动态智能，tool_execution_map + Planner
metagpt/config2.py             # config2.yaml → 按 api_type 实例化 LLM Provider
```

## 五、深读子页地图（34 页精选 6）

| 子页 | full.md 行号 | 为什么值得读 |
|---|---|---|
| Overview | L6 | 一页看懂 `Code=SOP(Team)` 与组件关系图（Role/Team/Message/Action/DI/RAG） |
| Software Company Metaphor | L382 | Team/hire/investment 与 SDLC 接力表（PM→Architect→PM→Engineer→QA），读架构必看 |
| Role System | L740 | Role/RoleContext/RoleReactMode 类图+生命周期时序，全框架心脏 |
| Message Passing System | L958 | cause_by/watch 路由协议与 `<all>/<self>/<none>` 语义，理解"瀑布=订阅"的关键 |
| RoleZero | L3209 | 新版动态智能路线，看 MetaGPT 如何推翻自己的固化 SOP |
| Glossary | L6217 | 术语表，快速校准 DI/MGX/RoleZero 等新概念 |

## 六、与"我们"的关系（一句话）

讲透 Agent 规划推理与多智能体协作时，MetaGPT 是"SOP 即架构"的最正宗一手标本——watch 订阅路由、结构化产物合同、RoleZero 自主演进恰好各对应我们 agent-development 教程的一个核心章节。

---
生成：2026-08-21 · deepwiki 34 页全归档
