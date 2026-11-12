# 01 · lead-agent 装配：create_agent 函数式总装车间

## 角色定位

`backend/packages/harness/deerflow/agents/lead_agent/agent.py` 是整个 DeerFlow "超级 agent" 的总装配车间。它不是 LangGraph 的 planner/researcher/reporter 多智能体图，而是 langchain 1.x 的函数式 `create_agent`（agent.py:3）加一条 `AgentMiddleware` 栈——所有能力（沙箱、记忆、子代理、MCP、澄清）都以中间件与工具的形式挂进单 agent 循环。入口 `make_lead_agent(config)`（agent.py:257）由 `backend/langgraph.json` 以 module:symbol 反射路径注册，LangGraph Server（2024 端口）每次运行时调用它现装一个 agent。同仓的嵌入式客户端 `DeerFlowClient` 与子代理执行器都复用同一套装配函数，所以这里是全仓行为一致性的锚点。

## 内部结构

文件自上而下五段：

1. **模型解析** `_resolve_model_name`（agent.py:25）：无任何模型配置直接抛 ValueError（agent.py:30）；请求模型不在 config 时告警并回退默认模型（agent.py:35-37）。最终解析链是三级：请求覆盖 `requested_model_name` → 自定义 agent 配置 `agent_config.model`（agent.py:275）→ 全局默认，见 agent.py:278。
2. **SummarizationMiddleware 工厂** `_create_summarization_middleware`（agent.py:40）：这是唯一装配在 agent.py 而非 middlewares/ 目录的环——langchain 内置类直接 import（agent.py:4）。未配置专用模型时用 `create_chat_model(thinking_enabled=False)` 走轻量模型省钱（agent.py:64）。
3. **TodoMiddleware 工厂** `_create_todo_list_middleware`（agent.py:82）：约 100 行 DeerFlow 风格的 system_prompt 与 tool_description 全部内嵌在 agent.py:95-192，只在 plan 模式返回实例。
4. **中间件栈装配** `_build_middlewares`（agent.py:207）：先取共享基座 `build_lead_runtime_middlewares(lazy_init=True)`（agent.py:217，5 个基础环），再按序追加 Summarization（可选，agent.py:220-222）→ Todo（可选，agent.py:225-228）→ Title（agent.py:231）→ Memory（agent.py:234）→ ViewImage（仅 `supports_vision` 模型，agent.py:238-241）→ SubagentLimit（可选，agent.py:244-247）→ LoopDetection（agent.py:250）→ Clarification 恒最后（agent.py:253）。
5. **总装** `make_lead_agent`（agent.py:257）：读 `config.configurable` 的 8 个运行时开关（agent.py:264-271），注入 LangSmith 追踪 metadata（agent.py:304-313），最终 `create_agent(model, tools, middleware, system_prompt, state_schema=ThreadState)`（agent.py:328-334）。bootstrap 分支（agent.py:315-325）用最小 prompt 加 `setup_agent` 工具走自定义 agent 创建流程。

**环计数漂移真相（钉版）**：三份口径互相矛盾——backend/README 写 9、CLAUDE.md 写 "10 middleware components / 链 11 项"、middlewares/ 目录实际 11 个 .py 文件。以源码为准的真实答案是**动态 9~13 环**：必选 9 环 = 基座 5（ThreadData/Uploads/Sandbox/Dangling/ToolError，见 tool_error_handling_middleware.py:78-93）+ Title + Memory + LoopDetection + Clarification；可选 4 环 = Summarization/Todo/ViewImage/SubagentLimit 按运行时配置登场。CLAUDE.md 的 11 项链漏掉了 LoopDetection（agent.py:249-250 实际必选），SandboxMiddleware 住在 `sandbox/middleware.py:21` 而非 middlewares/ 目录、SummarizationMiddleware 来自 langchain 包——目录文件数 ≠ 链环数，这就是三个数字各说各话的根源。

## 外部连接

- **tools 延迟装配**：`from deerflow.tools import get_available_tools` 与 `setup_agent` 都在 make_lead_agent 函数体内延迟 import（agent.py:259-260），注释明示规避循环依赖——tools 包反过来要引用 prompt 与 thread_state。
- **子代理共享基座**：`build_subagent_runtime_middlewares`（tool_error_handling_middleware.py:106）被 `subagents/executor.py:169` 在 `_create_agent` 内延迟 import，主/子 agent 共用 ThreadData+Sandbox+ToolError 三环。
- **私有 API 被脚本消费**：`scripts/tool-error-degradation-detection.sh:38` 直接 `from deerflow.agents.lead_agent.agent import _build_middlewares`——下划线私有函数成为工具故障降级检测的契约；该脚本对子链还准备了回退最小链（脚本 151-159 行，ThreadDataMiddleware+SandboxMiddleware）。
- **prompt 侧**：`apply_prompt_template`（agent.py:332 调用）负责技能/记忆/子代理章节注入；`state_schema=ThreadState`（agent.py:333）把 sandbox/thread_data/title/artifacts 等七个字段焊进状态契约（thread_state.py:48-55）。

## 数据流

一次请求的装配数据流：`RunnableConfig.configurable`（model_name/is_plan_mode/subagent_enabled/agent_name 等，agent.py:262-271）→ 模型三级解析（agent.py:278）→ `supports_thinking` 不匹配时降级关闭 thinking（agent.py:285-287）→ metadata 更新（agent.py:304）→ `_build_middlewares` 现算中间件实例列表 → `get_available_tools(groups=agent_config.tool_groups)`（agent.py:330）按自定义 agent 的工具组过滤 → create_agent 返回可 invoke/astream 的 Runnable。注意 agent 是每请求新建的（无缓存），但中间件内部有单例（如 MemoryUpdateQueue、沙箱 provider），"装配廉价、资源常驻"是本仓的显式取舍。

## 设计决策

1. **函数式注册而非图编排**：单 agent + 中间件栈放弃了 LangGraph 多节点图的显式控制流，换来的是每个中间件可独立插拔（agent.py:197-206 的十行注释块就是顺序语义的唯一权威文档：Clarification 必须 last、ThreadData 必须在 Sandbox 前）。
2. **lazy_init 默认 True**：基座以 `lazy_init=True` 装配（agent.py:217），目录创建与沙箱获取都推迟到首次工具调用，纯聊天轮零 IO 开销。
3. **运行时开关驱动条件装配**：可选环在装配期决定而非运行期分支——ViewImage 依赖解析后的真实 model_name（agent.py:237 注释明示避免 stale config）。
4. **bootstrap 特例**：is_bootstrap 走精简 prompt + `available_skills={"bootstrap"}`（agent.py:317），让"创建自定义 agent"这件事本身也是一次 agent 运行。

## 新人提示

- 改中间件顺序前先读 agent.py:197-206 注释块，顺序错误会破坏 thread_id 可用性与澄清拦截时序。
- 文档口径以 backend/CLAUDE.md 为准但链清单漏 LoopDetection；README/CONTRIBUTING 残留 backend/src/ 旧布局，一律以 agent.py 源码为准。
- 新增中间件要同步改三处：middlewares/ 目录、`_build_middlewares`（agent.py:207）、CLAUDE.md 链清单，否则计数漂移继续恶化。
- `_build_middlewares` 虽是私有命名，已被检测脚本与嵌入式客户端消费（client.py `_ensure_agent`），改签名等于破坏两处隐式契约，动手前先 grep 消费方。
