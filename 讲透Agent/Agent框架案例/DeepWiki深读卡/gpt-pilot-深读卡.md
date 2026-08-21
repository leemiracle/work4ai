# gpt-pilot 深读卡 —— AI 结对从零增量开发整个 App 的多 Agent 研发流水线

> **定位**：GPT Pilot 是 Pythagora 出品的研究型 CLI/VSCode 工具，用 10 个角色化 Agent（SpecWriter→Architect→TechLead→Developer→CodeMonkey→Troubleshooter/BugHunter…）模拟一支完整开发团队，从需求澄清到 QA 迭代 step-by-step 写出整应用，而非一次性吐代码库。核心理念"AI 写 95%、人类把关 5%"，human-in-the-loop 贯穿全程；官方明确定位区别于 Smol Developer / GPT Engineer，是 DevTI（开发工具智能）方向早期代表。
> **本地**：`repos/gpt-pilot`（Pythagora-io/gpt-pilot）｜**深读**：deepwiki 33 子页归档 `deepwiki/gpt-pilot/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| CLI/UI 层 | 入口与人机交互，多 UI 适配器 | `core/cli/main.py`、`UIBase`/`PlainConsoleUI`/`IPCClientUI`(VSCode 扩展)/`VirtualUI`(测试) |
| 编排层 | 状态机选 agent、并行执行、状态提交 | `Orchestrator`、`AgentResponse`/`ResponseType`(7 种) |
| Agent 层 | 10 个角色 agent + mixin 复用 | `BaseAgent`、SpecWriter/Architect/TechLead/Developer/CodeMonkey/Frontend/Troubleshooter/BugHunter/Wizard、`mixins.py`(RelevantFiles/ChatWithBreakdown/IterationPrompt/FileDiff/Git) |
| 状态层 | 两态事务 + 不可变快照链 | `StateManager`、Project→Branch→ProjectState（epics/tasks/steps/iterations + action 审计字段） |
| 文件层 | VFS 抽象、内容去重、diff | `save_file()`、`modified_files`、`restore_files()` |
| LLM 层 | 多 provider + 按 agent 配模型 | OpenAI/Anthropic/Azure/Groq/Relace client、`AgentConvo` |
| Prompt 层 | Jinja2 模板 + token 剪枝 | `core/prompts/*`、`partials/`、`trim_logs()` |
| 模板层 | 脚手架起步（前端先行） | `vite_react`/`vite_react_swagger`、`templates/registry.py` |

## 二、核心机制

1. **数据库驱动的状态机编排，而非消息传递**（来源：Agent System / Orchestrator and Control Flow）：`Orchestrator.create_agent()` 按 `current_state` 缺什么就选谁——无 epics→Wizard、无 spec→SpecWriter、无架构→Architect、无 tasks→TechLead、无 steps→Developer、有 step→CodeMonkey/Executor、有 iteration→Troubleshooter/BugHunter。agent 之间从不直接通信，只通过共享状态 + 7 种 `AgentResponse` 返回类型（DONE/INPUT_REQUIRED/EXTERNAL_DOCS_REQUIRED/DESCRIBE_FILES/UPDATE_SPECIFICATION/IMPORT/EXIT）路由。**区别于 AutoGen 式 agent 对话协作：这是把"流水线调度"外化到持久化状态机的做法**，天然可断点续传。
2. **两态事务 + 时间旅行**（来源：Project Lifecycle and Stages）：`current_state` 只读 / `next_state` 可写，agent 每完成一轮 `commit()` 生成新 `ProjectState`（step_index 递增的不可变快照链），`python main.py --project <id> --step 42` 可回滚到任意历史点重放；`action` 字段（SPEC_CREATE/FE_START/BH_START_BUG_HUNT…）留下人类可读审计轨迹。这是它敢做"长程任务"的底气。
3. **四级分解 + `<pythagoracode>` 代码协议 + 显式人工步骤**（来源：Implementation Agents / Development Workflow）：Spec→epic→task→step 逐层 LLM 分解；step 仅 4 类（command/save_file/human_intervention/utility_function），代码以 `<pythagoracode file="...">` 标签从 Developer 传给 CodeMonkey 落盘，多个 save_file 步可 `asyncio.gather` 并行；`human_intervention` 步把"95%/5% 理念"做成了**一等公民步骤类型**——AI 明确知道哪里需要人。
4. **人类测试闭环 + 循环检测兜底**（来源：Quality Assurance Agents / User Testing and Feedback Loop）：每个 task 完成后 Troubleshooter 用 LLM 生成测试说明让**真人**测 app，反馈三分类（bug/改动请求/循环）；同一问题迭代 3 次（`LOOP_THRESHOLD=3`）判定卡死，转 ProblemSolver 换备选方案；BugHunter 自带完整状态机（HUNTING_FOR_BUG→AWAITING_LOGGING→AWAITING_BUG_FIX→AWAITING_USER_TEST→START_PAIR_PROGRAMMING），最终兜底是人类结对调试（pair programming）。

## 三、与讲透系列的对位

| gpt-pilot 概念 | 讲透Agent / 讲透多Agent协作 / 讲透学习型Agent 对应概念 |
|---|---|
| `create_agent()` 状态机编排 | 多Agent协作·编排模式（中心化 Orchestrator vs P2P 对话） |
| `AgentResponse` 7 类返回路由 | 多Agent协作·控制流与消息路由 |
| current/next_state 两态事务 | 记忆机制·外部化持久记忆 + 检查点/恢复 |
| `RelevantFilesMixin` 文件相关性过滤 | 上下文工程·检索裁剪（大代码库只喂相关文件） |
| LOOP_THRESHOLD→换备选方案 | 学习型Agent·反思与失败恢复策略 |
| human_intervention 步 + BugHunter pair programming | human-in-the-loop 安全护栏 |

## 四、关键入口

```python
core/agents/orchestrator.py        # L36 Orchestrator；L463 create_agent() 状态机选 agent（全系统心脏）
core/agents/base.py                # L15 BaseAgent：current/next_state 双态 + ask_question()/get_llm()
core/agents/developer.py           # L32 StepType 四类步骤；task→steps 分解与 <pythagoracode> 计数校验
core/agents/code_monkey.py         # L63 正则解析 <pythagoracode file="..."> 提取代码并落盘
core/agents/troubleshooter.py      # L22 LOOP_THRESHOLD=3 循环检测；用户反馈三分类建 iteration
core/agents/bug_hunter.py          # bug 狩猎状态机 + start_pair_programming() 人类兜底
core/state/state_manager.py        # L433 commit() 两态交换；load_project(step_index) 时间旅行
core/prompts/tech-lead/plan.prompt # epic 分解 6 条规则（Rule#4：每个 epic 必须绑定 API endpoint）
```

## 五、深读子页地图（33 页精选 6）

1. **Agent System**（11，43KB）— 全部 agent 职责/方法/工作流一页看全，信息密度最高，首读
2. **Project Lifecycle and Stages**（23，33KB）— 10 阶段全生命周期 + 两态事务模型 + 断点续传/时间旅行
3. **Orchestrator and Control Flow**（9）— 编排状态机、并行 CodeMonkey 执行、commit 时序细节
4. **User Testing and Feedback Loop**（26）— 人类测试闭环设计，human-in-the-loop 的教科书实现
5. **Code Generation and File Management**（24）— pythagoracode 协议、VFS、内容去重、原子回滚
6. **Context Filtering and Relevance**（25）— 大项目上下文裁剪：relevant files 并行选择的上下文工程范本

## 六、与"我们"的关系（一句话）

学 Agent 的人在这里能看到"把软件公司组织结构直接映射为多 Agent 流水线"的最早完整实现之一——编排不靠消息而靠数据库状态机、长程任务靠不可变快照链续传，是人类确认式开发 Agent 的经典范本（也是 Pythagora/ 通义千元级"AI 程序员"商业路线的源头）。

---
生成：2026-08-21 · deepwiki 33 页全归档
