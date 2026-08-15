# 分册 A · Agent 框架与编排（11 仓深读）

> 深读材料：README（前 300 行）+ 关键源文件（≤350 行）+ 代码树指标。行号证据限于已读片段。

### langchain-ai/langchain
- **架构模式**：组件化 LCEL 流水线（Runnable 管道组合 + 可插拔集成层）
- **核心抽象**：`BaseSingleActionAgent`/`BaseMultiActionAgent`（agents/agent.py:L55、L221）；`AgentAction/AgentFinish` 协议（agent.py:L68-103）；`create_react_agent`（agents/react/agent.py:L16）
- **关键机制**：
  - Agent 即"planner"：`plan()/aplan()` 以 `intermediate_steps` 为入参返回下一步动作（agent.py:L67-103），同步/异步双轨
  - ReAct 用 LCEL 竖线组合：`assign(scratchpad) | prompt | llm.bind(stop) | output_parser`（react/agent.py:L143-149），把论文模式降维成一条 Runnable 链
  - 用 `stop=["\nObservation"]` 截断幻觉输出（react/agent.py:L137-141）
  - 超限兜底 `return_stopped_response("force")` 返回常量而非崩溃（agent.py:L129-136）
- **工程亮点**：Agent 可序列化为 YAML/JSON（`save()`，agent.py:L182-214）；统一 CallbackManager 贯穿 chain/tool 两级运行
- **教学映射**：讲透多Agent协作（ReAct 基线）、讲透RAG（retriever/vectorstore 标准接口）
- **一句话本质**：给 LLM 应用定一套"可互换零件"标准接口，让换模型/换向量库不动业务代码。

### langchain-ai/langgraph
- **架构模式**：Pregel 式 BSP 图执行引擎（受 Google Pregel/Apache Beam 启发，README:L80）
- **核心抽象**：`Pregel` 主类（pregel/main.py:L201）；`NodeBuilder`（main.py:L206-341）；`BaseChannel`/`Checkpoint`（main.py:L47-52、L110-111）
- **关键机制**：
  - 节点声明式订阅：`subscribe_to/subscribe_only/read_from/write_to` 链式 DSL（main.py:L242-341），通道更新触发节点
  - 超步算法：`prepare_next_tasks/apply_writes`（main.py:L122-128 import）实现消息驱动调度
  - 持久化执行：`BaseCheckpointSaver` + `Durability` 常量（main.py:L47-51、L72），失败可从精确点恢复
  - `Send`/`Command`/`Interrupt` 类型支撑 map-reduce 动态分发与 human-in-the-loop（main.py:L177-192）
- **工程亮点**：节点级 `RetryPolicy/CachePolicy/TimeoutPolicy` 三策略内建（main.py:L149-151、L349）；`langgraph.json` 声明 graphs+dependencies 一键起 API server（cli.py:L44-92）
- **教学映射**：讲透多Agent协作、透视Agent系统工程（durable execution 范本）、讲透上下文缓存（CachePolicy）
- **一句话本质**：把"长时运行、会崩溃、需人工介入的 Agent"变成带 checkpoint 的可恢复图计算。

### microsoft/autogen
- **架构模式**：消息传递 + 事件驱动的 Actor 型多 Agent 分层框架（Core→AgentChat→Extensions，README:L179-183）
- **核心抽象**：`AssistantAgent`（README:L53）；`AgentTool`——把整个 Agent 包装成工具（README:L106-127）；`McpWorkbench`（README:L75-87）
- **关键机制**：
  - Agent-as-Tool：math/chemistry 专家被包成 tool 挂给主 assistant，`max_tool_iterations=10` 控制循环（README:L117-151）
  - Core 层提供本地/分布式 runtime 与跨语言（.NET 497 个 .cs 文件佐证双栈，tree-metrics）
  - 基准工程化：`agbench` CLI 的 run/tabulate/lint/remove_missing 命令面（agbench/cli.py:L26-53）
  - `run_stream` + `Console` 流式 UI 贯穿执行（README:L95）
- **工程亮点**：AutoGen Studio 无代码原型 + 明确声明"非生产就绪"的安全边界（README:L158-164）；现已维护模式，迁移至 Microsoft Agent Framework——一个大厂框架完整生命周期的活标本
- **教学映射**：讲透群体智能（group chat 模式源头）、讲透多Agent协作、透视Agent系统工程（框架退役/迁移治理）
- **一句话本质**：证明"多个会对话的 Agent 能协作"的开山框架，其遗产是 AgentTool 与对话式编排范式。

### crewAIInc/crewAI
- **架构模式**：角色化 Crew（自主协作）+ 事件驱动 Flow（确定性控制）双轨编排
- **核心抽象**：`Crew`（角色/目标/背景故事团队，README:L61、L169-175）；`Flow`（事件驱动状态机，README:L176-180）；CLI 的 `crew/flow/tool/skill/template` 五类产物（cli.py:L139-276）
- **关键机制**：
  - CLI 延迟导入：`__new__` 壳类把重依赖推迟到命令实例化（cli.py:L57-88），冷启动优化
  - 训练闭环：`crewai train --n-iterations` 迭代打磨并把数据存 `trained_agents_data.pkl`（cli.py:L304-338）
  - `crewai replay --task-id` 从任一任务回放后续链路（cli.py:L341-351）
  - `crewai uv` 包装器注入全部工具凭证到子进程环境（cli.py:L108-136）
- **工程亮点**：新旧参数双写+`warn_deprecated` 平滑迁移（cli.py:L154-160、L334-336）；docs 目录 24k+ mdx 文件、cookbook 式文档即护城河（tree-metrics）
- **教学映射**：讲透多Agent协作（角色分工教科书）、讲透学习型Agent（train 迭代）、软件即熵治理（参数废弃管理）
- **一句话本质**：用"雇一支团队"的心智模型（角色+任务+流程）把多 Agent 编排降到产品经理可用。

### agno-agi/agno
- **架构模式**：SDK + AgentOS 运行时 + 管理 UI 三层"Agent 平台"单体
- **核心抽象**：`AgentOS`（cookbook/00_quickstart/run.py:L58-77）——一次注册 agents/teams/workflows 即成服务；`ContextProvider`（01_demo/run.py:L36-48）；cookbook 示例矩阵（tools/memory/knowledge/learning/guardrails…run.py:L60-71）
- **关键机制**：
  - `agent_os.get_app()` 生成 FastAPI app，`serve()` 直启并挂 tracing（run.py:L77-83）
  - lifespan 钩子在 shutdown 时统一 `aclose()` 各 MCP ContextProvider 会话（01_demo/run.py:L36-48）
  - 环境门控的可选 Agent：git/notion wiki 凭证存在才注册（01_demo/run.py:L51-57）
  - scheduler、JWT RBAC、多租户隔离为运行时内建能力（README:L50-59）
- **工程亮点**：cookbook 2954 个可运行示例 = 可执行文档（tree-metrics）；"20 行代码起步 → 平台化落地"的无断层梯度
- **教学映射**：透视Agent系统工程（agent-as-a-service 全景）、讲透记忆（session/memory/knowledge 分层存储）
- **一句话本质**：把"写一个 Agent"升级为"拥有一个可运营的 Agent 平台"，数据和记忆留在自己数据库里。

### langgenius/dify
- **架构模式**：可视化工作流画布 + BaaS 的 LLMOps 平台（Flask REST 控制面 + 前端 7681 文件的重 UI）
- **核心抽象**：`App/AppMode`（AGENT_CHAT/WORKFLOW/ADVANCED_CHAT 多形态，agent.py:L52、L344）；`AgentDriveService`（Agent 文件盘，agent.py:L43-49）；`SkillStandardizeService`（技能包标准化，agent.py:L36-42）
- **关键机制**：
  - 技能包上传→标准化→工具推断流水线：`.zip/.skill` 解包后 `SkillToolInferenceService.infer()` 自动推导工具签名（agent.py:L186-211、L316-328）
  - Agent Drive 以 key（如 `files/sample.pdf`、`{slug}/SKILL.md`）做文件/技能的 commit/delete 事务（agent.py:L232-260、L288-313）
  - 执行可观测：`AgentLogResponse` 返回逐轮 iterations、tool_calls、tokens、elapsed_time（agent.py:L94-128）
  - RBAC 装饰器栈：`rbac_permission_required`+`with_session`+`get_app_model` 权限即注解（agent.py:L339-345）
- **工程亮点**：workflow 节点也能挂 agent（`node_id` 解析分支，agent.py:L174-179）；租户级上传校验防越权（agent.py:L222-229）
- **教学映射**：讲透RAG（pipeline 内建）、透视Agent系统工程（多租户 SaaS 化）、软件即熵治理（schema 演进与驱动 key 规范）
- **一句话本质**：让不写代码的团队也能拼出带 RAG、Agent、观测的 LLM 应用并一键 API 化。

### n8n-io/n8n
- **架构模式**：节点图工作流引擎 + 内嵌 Agent SDK 运行时（TS monorepo，19283 个 .ts）
- **核心抽象**：`Agent` SDK（packages/@n8n/agents/src/index.ts:L172）；`EpisodicMemory`（index.ts:L43-70）；`DelegateSubAgentTool`（index.ts:L285-313）
- **关键机制**：
  - 子 Agent 委托：任务路径树 `createChildSubAgentTaskPath` + `DEFAULT_SUB_AGENT_MAX_CHILDREN` 限深防递归失控（index.ts:L276-297）
  - 情景记忆管线：extract→reflect→index→`createRecallMemoryTool` 召回，含内容哈希去重与任务锁（index.ts:L330-351、L64）
  - 审批即暂停/恢复：`APPROVAL_SUSPEND/RESUME_SCHEMA + wrapToolForApproval`（index.ts:L129-136）
  - Guardrail 内建 PII 流式脱敏（`StreamingRedactor`、Luhn 校验，index.ts:L147-156）
- **工程亮点**：流式防卡死（`ModelStreamStallError` + 首 token/空闲超时，index.ts:L124-128）；Skills 以 Markdown 目录为载体动态加载（index.ts:L174-216）
- **教学映射**：讲透记忆（episodic memory 最完整实现）、讲透多Agent协作（委托+限深）、软件即熵治理（1500 集成的版本治理）
- **一句话本质**：把 Agent 塞进已有 8 年的自动化节点图里，让 AI 成为连接 1500+ 系统的工作流中的一个节点族。

### Significant-Gravitas/AutoGPT
- **架构模式**：Block-DAG 可视化执行图 + 事件总线（block 即节点，Agent 亦为 block）
- **核心抽象**：`Block/BlockSchema`（blocks/agent.py:L4-12）；`AgentExecutorBlock`（agent.py:L24）；async execution event bus（agent.py:L150-160）
- **关键机制**：
  - Agent-in-Agent：`AgentExecutorBlock.run()` 调 `add_graph_execution` 启动子图并挂 `parent_execution_id`（agent.py:L93-105），递归组合
  - 父块监听子图事件流，只透传 OUTPUT 类型块、按 `node_exec_id` 去重（agent.py:L156-219）
  - 子图成本上卷：`reconciled_cost_delta` 汇总子图花费到父级 graph_stats（agent.py:L179-187）
  - 协调块显式豁免叶节点级 wall-clock 上限，避免长子 Agent 误杀（agent.py:L25-28）
- **工程亮点**：`_stop` 带 3600s 等待超时与 `func_retry`（agent.py:L221-241）；classic（MIT）与 platform（Polyform Shield）双许可分层（README:L190-196）
- **教学映射**：讲透多Agent协作（图嵌图）、透视Agent系统工程（事件总线+成本核算）、软件即熵治理（许可证演化）
- **一句话本质**：从"自主 Agent 玄学鼻祖"转型为"用可视化 Block 图精确编排 Agent 的低代码平台"。

### bytedance/deer-flow
- **架构模式**：LangGraph 之上的"超级 Agent 悬挂架"（harness）——中间件栈组装 + FastAPI Gateway 网关
- **核心抽象**：Lead Agent 工厂（agents/lead_agent/agent.py:L1）；`AgentMiddleware` 中间件族（agent.py:L36-50）；`AuthzDecision/AuthzRequest` 授权三元组（agent.py:L52-55）
- **关键机制**：
  - 15+ 中间件叠层：LoopDetection/SubagentLimit/Summarization/TokenUsage/Todo/Clarification…每项横切能力一个类（agent.py:L37-50）
  - 模型级授权 `model:use`：拒绝时优雅降级到首个可用模型而非报错，fail_closed/fail_open 可选（agent.py:L143-235）
  - tracing 回调只挂图根 + 全链 `attach_tracing=False` 的不变量写进模块 docstring（agent.py:L1-23）——防重复 span 的契约式设计
  - Gateway 23 个 router（runs/threads/skills/mcp/channels/webhooks…gateway/app.py:L15-39）+ 无认证→有认证的孤儿 thread 分页迁移（app.py:L68-137、L140-157）
- **工程亮点**：不可信 webhook 渠道冻结 admin 工具的注入防护（agent.py:L76-82）；checkpoint 通道模式"冻结语义"显式文档化（README:L264-267）
- **教学映射**：讲透多Agent协作（sub-agent 编排）、讲透记忆（长期记忆+手动上下文压缩）、软件即熵治理（升级路径/迁移/不变量治理的最佳标本）
- **一句话本质**：演示"如何在 LangGraph 裸引擎上工程化地长出一个 Claude Code 级通用 Agent"的参考实现。

### Skyvern-AI/skyvern
- **架构模式**：视觉 LLM + Playwright 的"感知-行动"浏览器 Agent（agent swarm 理解页面并规划动作，README:L39-44）
- **核心抽象**：`page.act/extract/validate/prompt` 四原语（README:L146-151）；AI-augmented Playwright action（`prompt=` 参数，README:L162-183）；workflow 执行器 `page.agent.run_workflow`（README:L153-160）
- **关键机制**：
  - 三模式交互：纯 selector→纯自然语言→selector 优先 AI 兜底（README:L174-183），工程确定性与泛化性可混合
  - 视觉映射替代 XPath：抗页面改版、零代码适配陌生网站（README:L46-51）
  - 凭证代理解析：Bitwarden/1Password 集成做 AI 登录（README:L158）
  - 本地 SQLite 默认 + 可切 Postgres 的渐进部署（README:L68-91）
- **工程亮点**：pip 依赖冲突的 troubleshooting 直接写在 README（L113-129），发行质量意识；WebVoyager 85.8% 的评测背书（README:L51）
- **教学映射**：讲透世界模型（视觉状态感知→动作映射的典型）、讲透代码生成（浏览器操作即代码生成域）
- **一句话本质**：让 Agent 用"眼睛+推理"代替脆弱的选择器脚本去操作任何网站。

### e2b-dev/E2B
- **架构模式**：微 VM 沙箱即服务（SDK 控制平面 + Firecracker 云基础设施，模板从 Dockerfile 派生）
- **核心抽象**：`Sandbox`（README:L47-62，create/commands.run 上下文管理器）；Code Interpreter `runCode()`（README:L73-79）；sandbox template（cli commands/index.ts:L9-16）
- **关键机制**：
  - 模板工作流：`e2b template create` 把 Dockerfile 变成可批量实例化的沙箱镜像（index.ts:L10-12）
  - 双语 SDK 同构 API：JS `Sandbox.create()` 与 Python `Sandbox.create()` 一致（README:L47-62）
  - 自托管走 Terraform，AWS/GCP 已验证、Azure 在路上（README:L87-95）
  - packages/ 761 文件 monorepo（py 449 + ts 250）承载 SDK 矩阵（tree-metrics）
- **工程亮点**：把"执行不可信 AI 代码"从各框架自建 subprocess 方案中抽离成独立基础设施层；隔离边界清晰（无 Agent 逻辑，纯执行原语）
- **教学映射**：讲透代码生成（执行环境半边）、透视Agent系统工程（安全沙箱层）、软件即熵治理（不可信代码的熵隔离）
- **一句话本质**：给"AI 写的代码"一个即开即用、用完即焚的安全体育馆。

---

## 组内横向对比

**谱系一：图/流编排引擎**——LangGraph（BSP 图 + checkpoint）、n8n（节点 DAG + 事件流）、AutoGPT Platform（Block-DAG + 事件总线）、Dify（可视化画布）四家同构，差异在"谁定义图"：代码（LangGraph）、拖拽（n8n/AutoGPT/Dify）。AutoGPT 的 `AgentExecutorBlock` 与 n8n 的 `DelegateSubAgentTool` 几乎是同一机制（Agent 作为节点/工具递归组合 + 限深），是"图嵌图"收敛的证据。

**谱系二：对话式多 Agent 协作**——AutoGen（消息传递/Actor）与 CrewAI（角色化 Crew）同源异构：前者以通信协议为中心，后者以社会角色为中心；两者都正被"Flow/确定性控制"回潮收编（CrewAI Flows、AutoGen→MAF），说明纯自主群体智能在生产端让位于混合编排。

**谱系三：harness/平台层**——DeerFlow 是"站在 LangGraph 上的参考 harness"（中间件栈+网关），Agno 是"SDK→运行时→平台"的纵向整合，两者都吸收了 Claude Code 的中间件/todo/子代理模式；LangChain 则退守为组件标准层。

**独特者**：Skyvern（视觉世界模型驱动浏览器）与 E2B（纯沙箱基础设施）不在编排轴上——前者解决感知-行动映射，后者解决执行隔离，恰好是编排框架身下的两块地基。

**演化方向**：① Agent-as-Tool/图嵌图成为多 Agent 通用形态；② 记忆从"挂个向量库"进化为 episodic memory 提取-反思-召回管线（n8n 最完整）；③ 中间件化横切（限深/循环检测/压缩/审批）取代 monolithic agent loop；④ 平台化与治理（RBAC、成本核算、许可证分层、迁移路径）成为竞争主战场——框架创新期结束，系统工程期开始。
