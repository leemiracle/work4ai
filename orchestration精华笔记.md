# orchestration 精华笔记（蒸馏细节）

> 本文是 [orchestration精华合入-总入口](./orchestration精华合入-总入口.md) 的资料附录：各仓库的核心思想原文级蒸馏，供人工研读与后续迭代 skill 用。

## 一、humanlayer/12-factor-agents（25.3k★）

**核心立场**：好的 agent 是 "mostly software"——确定性代码为主体，LLM 只在决策点介入；别把控制流交给框架黑盒。

12 条原则：

| # | 原则 | 精炼表述 |
|---|---|---|
| 1 | Natural Language → Tool Calls | LLM 的价值是把自然语言变成结构化工具调用，这是 agent 的原子操作 |
| 2 | Own Your Prompts | prompt 是核心资产，版本化、可调试，不藏在框架里 |
| 3 | Own Your Context Window | 上下文是稀缺资源，须主动裁剪/压缩/总结，只放有用信息 |
| 4 | Tools = Structured Outputs | 工具调用本质是结构化输出，可用代码解析校验，不必绑死 provider |
| 5 | Unify Execution & Business State | 执行中间态与业务状态合并进一个可序列化对象 |
| 6 | Launch/Pause/Resume | agent 是可中断续跑的进程，用简单 API 管理 |
| 7 | Contact Humans via Tool Calls | 人工介入也建模为工具（ask_human） |
| 8 | Own Your Control Flow | 控制流写在普通代码里，LLM 只做实时决策 |
| 9 | Errors as Text | 错误压缩成文本回灌上下文让模型自愈，而非崩溃重试 |
| 10 | Small, Focused Agents | 多个小而专的 agent 优于巨型全能 agent，交接时只传精简上下文 |
| 11 | Trigger from Anywhere | 触发源不限聊天框（webhook/cron），在用户所在处交付 |
| 12 | Stateless Reducer | agent 是纯函数 (状态,事件)→新状态，可重放可恢复 |

Top 3 设计决策：① 上下文窗口主动管理（裁剪优先于堆砌）；② 无状态 reducer + 统一状态（可恢复/可测试）；③ 控制流自持 + 错误即文本（把 LLM 限制在决策点）。

## 二、deepset-ai/haystack 3.0（26.2k★）

- 架构：`Pipeline`（支持循环/分支/条件的计算图）由 `Component`（类型化输入输出的独立单元）经显式 `Connection` 组成；同步/异步一体、token 级流式；组件可替换、厂商无关。
- Context engineering：信息进入模型前的 retrieve→rank→filter→combine→structure→route 全部显式建模、透明可追踪；agent 有 lifecycle hooks（`before_llm`/`before_tool`/`on_exit`）注入 guardrail；内建 step_count/token_usage 计量。
- 借鉴：① 类型化组件+显式连接（可单测）；② 渐进式技能发现（SkillToolset：工具描述按需注入，不塞满 system prompt）；③ 生命周期钩子+原生计量。

## 三、工作流引擎六家内核（airflow 46.5k / kestra 27.8k / prefect 23.6k / dagster 16k / dolphinscheduler 14.4k / trigger.dev 16k）

- **DAG**：统一以有向无环图表示（任务图/资产图/拓扑视图）；拓扑排序分层调度，上游成功才放行下游；图即代码（可版本化可测试）。
- **幂等**：Airflow 明言任务应幂等——重跑结果一致、不产生重复数据。手法：确定性 key（flow 名+参数+时间窗）、内容寻址（输出 hash 未变则跳过）、任务间只传元数据引用（XCom）。
- **重试**：只对瞬态错误（网络/限流/资源）重试；指数退避+最大次数封顶；参数校验类确定性失败直接进错误分支。
- **回填 backfill**：按时间区间/参数集重放历史；配合幂等+缓存只重算受影响节点。
- **传感器/触发器**：Airflow sensor 轮询、Kestra/Trigger.dev 事件触发（文件到达/队列/webhook）；"条件满足"成为一等公民。
- **资产/血缘**（Dagster 范式）：以产物为中心而非任务为中心，声明函数产出什么资产，引擎自动推导依赖与血缘，支撑增量更新。
- **Durable execution**（Trigger.dev）：每步 checkpoint 持久化，崩溃后从检查点恢复；幂等 key、并发队列控制、human-in-the-loop 暂停。
- **事件驱动**（Kestra）：上游/外部完成即触发下游，调度与事件统一在 trigger 定义下。

对编码 agent 的 5 点借鉴：① 子任务幂等+确定性输出 key（批量分析按"任务名+输入hash"落盘）；② 检查点而非单次长执行；③ 显式 DAG+失败分层（只重试该节点及下游）；④ 以产物为中心组织血缘；⑤ 触发式衔接代替阻塞等待。

## 四、statelyai/xstate（30k★）

- 核心概念：state（有限状态集）/ event / transition（显式定义，非法事件默认忽略——不可能出现未定义状态组合）/ guard（转移上的条件谓词，不满足则拒绝）/ final state（完成态+output）；扩展：context、层级嵌套、并行状态、history。
- Actor 模型：机器运行实例即 actor，内部状态封装、仅异步消息（mailbox 逐条串行）通信、不共享内存；父机器可 invoke/spawn 子 actor；快照可订阅、可持久化恢复。
- 借鉴：① plan→execute→review 建成显式状态机，未到 review 态 "approve" 事件被忽略——机制防跳步；② guard 做准入（execute→review 需 tests_passed==true）——防假完成；③ actor 隔离+快照——失败局部化+断点续跑。

## 五、rowboatlabs/rowboat（17.3k★）

- 记忆：不做按需 RAG，而是把邮件/会议/对话持续索引成 Obsidian 式双向链接"活知识图谱"（Brain）；本地纯 Markdown（可检视、可手编、零私有格式）；上下文随时间累积、记忆复利。
- 协作：编排者持有全量上下文，按需驱动外部编码 agent 并行执行（code mode）；background agent 由事件（新邮件）或日程触发，可调 MCP 工具/浏览器/搜索；各表面共享同一记忆底座。
- 借鉴：① 记忆=本地 Markdown 双向链接图谱（决策/踩坑持久累积）；② 事件驱动后台 agent；③ 编排层与执行层分离、上下文按需注入。

## 六、langgenius/dify（152k★）

- 节点类型：User Input/Trigger、LLM、Knowledge Retrieval、If/Else、Question Classifier、Code、Template(Jinja2)、HTTP Request、Tool、Parameter Extractor、Variable Aggregator、Iteration/Loop、Agent、Answer/Output。
- 条件分支：互斥路径只走一支；变量聚合：收敛互斥分支为单一输出变量（同类型，取有值者）。
- 迭代节点：数组逐元素子工作流，内置 items/index；串行或并行（≤10 并发）；错误三策略（terminate / continue 置 null / skip 剔除）；输出结果数组。
- Agent 节点：Function Calling 或 ReAct；设最大迭代数防死循环；TokenBufferMemory 控记忆窗口；输出含 final answer、tool outputs、reasoning trace、iteration count、success status。
- 变量传递：下游按 `节点.变量名` 显式引用上游输出；并行分支互不可见，汇合后可读全部；LLM 节点经 Context 字段接入检索结果。
- RAG：多知识库并行检索→合并；两层过滤（库级候选池+节点级 rerank）+ Top-K+分数阈值；元数据过滤；输出 chunk 含内容/元数据/标题，引用可溯源。
- 借鉴：① 显式变量引用协议（节点输出即数据契约）；② 迭代错误分级+并发上限；③ Agent 输出结构化（可审计可回放）。

## 七、cft0808/edict（16.4k★）

- 架构（12 agent）：用户(皇上)→太子分拣（闲聊直答/正事建任务）→中书省规划拆解→门下省审议把关（可封驳打回）→尚书省派发协调汇总→执行六部：户部数据报表、礼部文档规范、兵部代码开发审查、刑部安全合规、工部 CI/CD 部署、吏部 agent 注册权限、早朝官定时情报。
- 权限矩阵限定谁能给谁发消息；9 态状态机强制合法流转；非法跳转被拒绝并记录。
- 审计：audit.py 记录所有状态变更；奏折系统五阶段归档（圣旨→中书→门下→六部→回奏）。
- 借鉴：① 制度性审核关卡（规划须经独立审查者准奏/封驳，强制返工循环）；② 权限矩阵+状态机校验（通信拓扑与流转白纸黑字）；③ 规划/调度/执行三权分立。

---
生成：2026-08-15 · 4 个并行研究 agent 抓取 GitHub 文档后蒸馏
