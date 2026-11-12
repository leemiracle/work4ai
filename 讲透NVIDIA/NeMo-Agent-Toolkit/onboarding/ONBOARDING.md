# NeMo Agent Toolkit（NAT）图谱导览 ONBOARDING

> 基于 understand-anything 知识图谱：8250 节点 / 17475 边 / 16 层 / 16 步导览，fingerprints 2507 文件 @c7e1162a。
> 仓库：/usr-data/data2/repos/agent-repos/NVIDIA/NeMo-Agent-Toolkit（只读镜像）。本文所有行号锚均经源码 grep 核实。

## 一、仓库定位与全景

NVIDIA NeMo Agent Toolkit（NAT，CLI 命令名 `nat`）是 NVIDIA 开源的多智能体编排框架：用户用一份 YAML 声「要什么」，NAT 从组件注册表把 LLM、工具、agent、中间件、前端装配成可运行、可服务化、可评测的 workflow。它不是又一个 agent 框架，而是**框架之上的装配层**——LangChain、Agno、LlamaIndex、AutoGen、CrewAI、Semantic Kernel、Strands、Google ADK 都是它的可选后端（见 `packages/` 下 34 个 `nvidia_nat_*` 包）。

单仓多包布局（uv workspace，根 `pyproject.toml` 管全局）：

| 区域 | 体量 | 内容 |
|---|---|---|
| `packages/nvidia_nat_core` | 629 文件 | 心脏：builder/registry/middleware/front_ends/cli/data_models |
| `packages/nvidia_nat_langchain` 等 33 包 | 929 文件 | 框架适配器+MCP/A2A/A365/evals/profiler/security 等域包 |
| `examples/` | 640 文件 | 每个示例都是可安装的独立 uv 包 |
| `skills/` + `docs/source` | 180 文件 | agent 技能手册（45）+人类文档（135） |
| `ci/`+`external/`+`test_data/`+`.cursor/`+`.github/`+根配置 | 157 文件 | 工程化外壳 |

图谱 16 层从工程门面（L01）→核心基座（L02-L08）→域包（L09-L13）→文档技能（L14）→示例（L15/L16），与本导览节次对应。

## 二、架构总览：注册表中心制

NAT 的一切组件共享一个注册表模型。最小示例 `examples/getting_started/simple_calculator/src/nat_simple_calculator/configs/config.yml` 就是全架构缩影：`function_groups:`（calculator）、`functions:`（current_datetime）、`llms:`（`_type: nim`，`model_name: nvidia/nemotron-3.5-lightning-30b-a3b` 在 config.yml:28）、`workflow:`（config.yml:34-35 `_type: react_agent`，`tool_names`+`llm_name` 引用上面两节）。

`_type` 是万能键：每个组件配置类都继承 pydantic 基类并携带注册名——`CalculatorToolConfig(FunctionGroupBaseConfig, name="calculator")`（simple_calculator/register.py:33）。核心把这些映射存进 `GlobalTypeRegistry`（`packages/nvidia_nat_core/src/nat/cli/type_registry.py:1423`），全进程唯一组件目录。

组件注册的标准姿势是装饰器：`register_function`（`packages/nvidia_nat_core/src/nat/cli/register_workflow.py:172`）与 `register_function_group`（register_workflow.py:266）。它们的入参 `config_type` 携带 `name=` 注册名，`framework_wrappers` 声明适配哪个 LLM 框架。

## 三、entry-points 仓外注册架构（专节）

这是 NAT 最具特色的设计：**core 不 import 任何外部框架，外部框架包也不进 core 仓库**。装配靠 Python 标准的 importlib entry-points：

1. **声明侧**：每个适配器包在自己的 `pyproject.toml` 声明入口。如 `packages/nvidia_nat_langchain/pyproject.toml:109-111`：`[project.entry-points.'nat.components']` 下注册 `nat_langchain = "nat.plugins.langchain.register"`。
2. **发现侧**：`packages/nvidia_nat_core/src/nat/runtime/loader.py:128` 的 `discover_entrypoints()` 用 `importlib.metadata.entry_points()`（loader.py:133）按组名收集，组名共六个：`nat.plugins`/`nat.components`（组件，loader.py:139-140）、`nat.front_ends`（loader.py:141-142）、`nat.registry_handlers`、`nat.evaluators`、`nat.authentication_providers`（loader.py:143-148）。
3. **装载侧**：`discover_and_register_plugins()`（loader.py:175）逐个 `entry_point.load()`，并在 `pause_registration_changed_hooks()` 上下文里批量写入 GlobalTypeRegistry（loader.py:187）以优化大量插件加载性能；单插件加载超过 150-300ms 会记录慢加载告警（loader.py:204-209）。

细节彩蛋：loader.py:138 注释明言 aiq 入口组**有意保留以向后兼容**——NAT 前身是 NVIDIA Agent Intelligence Kit（AIQ），仓内大量 `aiq_` 前缀类名是同一血脉的活化石。

效果：`pip install nvidia-nat-langchain` 之后，config.yml 里就能写 `_type: react_agent`，无需改 core 一行代码。34 个包彼此可选、按需安装，core 保持零框架依赖。同样机制支撑三类扩展人：写适配器包（框架厂商）、写组件（用户 register.py）、写前端（`nat.front_ends` 组）。

组件还能跨仓流通：`packages/nvidia_nat_core/src/nat/registry_handlers/` 提供三种注册处理器——`AbstractRegistryHandler`（registry_handler_base.py:35）定义 `publish/pull/search/remove` 四协议（registry_handler_base.py:47/63/78/93），`LocalRegistryHandler`（local/local_handler.py:38）管本地 entry-points，pypi/rest 处理器可把组件发布到 PyPI 或远程组件仓（schemas/ 下全套请求响应模型），CLI 对应 `nat registry publish/pull/search`。

## 四、核心运行时：Builder → Workflow → Session

构建链三段式：

1. **Builder 抽象**（`packages/nvidia_nat_core/src/nat/builder/builder.py:75`，`Builder(ABC)`）：定义全套供给装配方法——`add_function`（builder.py:102）、`get_tools`（builder.py:230）、`add_llm`（builder.py:258）、`add_auth_provider`（builder.py:314）、`add_object_store`（builder.py:355）、`add_embedder`（builder.py:398）、`add_memory_client`（builder.py:450）、`add_retriever`（builder.py:489）、`add_trainer`（builder.py:558）、`add_middleware`（builder.py:747）。Builder 也是 context manager，`current()`（builder.py:78）给注册函数提供当前构建上下文。
2. **WorkflowBuilder 实现**（`packages/nvidia_nat_core/src/nat/builder/workflow_builder.py:319`）：从 config 解析引用、按 `ConfiguredFunction/ConfiguredLLM/ConfiguredMiddleware` 等 dataclass（workflow_builder.py:115-195）暂存组件意图，`_build_function_impl`（workflow_builder.py:226）真正实例化；`detect_llm_frameworks_in_build_fn`（workflow_builder.py:98）在构建期探测组件适配的框架并包裹 build 函数实现一组件多框架。`sync_builder`（workflow_builder.py:447）暴露同步门面。
3. **Workflow**（`packages/nvidia_nat_core/src/nat/builder/workflow.py:39`）：用户侧执行单元，`run()`（workflow.py:100）+ `result_with_steps()`（workflow.py:116）+ `from_entry_fn()`（workflow.py:133）把普通函数升级为 workflow。

运行期由 `SessionManager`（`packages/nvidia_nat_core/src/nat/runtime/session.py:176`）托管：`load_config` 后 `WorkflowBuilder.from_config`（loader.py:115）构建，`SessionManager.create`（loader.py:117）建会话池。它支持 per-user 隔离——`PerUserBuilderInfo`（session.py:58）、`identity_header`（session.py:213-214）、`_per_user_builders` 字典+锁（session.py:241-242），为多租户服务化铺路。

中间件是横切机制：`Middleware(ABC)`（`packages/nvidia_nat_core/src/nat/middleware/middleware.py:118`）以 `pre_invoke`（middleware.py:163）/`post_invoke`（middleware.py:192）钩住函数调用，`middleware_invoke`（middleware.py:237）/`middleware_stream`（middleware.py:273）实现洋葱圈。内置 cache/circuit_breaker/dynamic/logging/timeout 五族走「实现+config+register」三件套并由 `middleware/register.py:18-22` 统一挂接（cache 是全库唯一默认 `is_final=True` 的中间件，cache_middleware.py:93，命中即终结整链）；第六族 hitl **无 register.py**——HITLMiddleware 是供继承的抽象层不进 YAML 注册体系，examples/HITL 的实际路线是把审批做成普通函数（`hitl_approval_tool.py:32`，由 por_to_jiratickets 示例包提供）在 agent 循环里调用。security 包的 defense/guardrails/red_teaming 三道防线同为中间件形态。

前端是出口：`front_ends/fastapi/`（main.py 起，routes/ 提供 `/v1/chat_completions` 等 OpenAI 兼容路由）、console 终端前端、simple_base 自定义基类、cron 定时。MCP 也是前端家族一员：`MCPFrontEndConfig(FrontEndBaseConfig, name="mcp")`（`packages/nvidia_nat_mcp/src/nat/plugins/mcp/server/front_end_config.py:29`），config-server.yml:22-24 的 `general.front_end._type: mcp` 一行即把 workflow 发布成 MCP server（`nat mcp serve`）。反向集成由 client/ + `tool_converter.py` 把外部 MCP 工具转成 NAT function。

## 五、供给与横切层速查

- **LLM**：core `llm/` 内置 nim/openai/litellm/aws_bedrock/azure_openai/dynamo/huggingface/oci 等十余家客户端，`utils/hooks.py` 与 `utils/thinking.py` 处理推理钩子与思考链标签剥离。
- **工具**：core `tool/` 提供 retriever、document_search、code_execution 沙箱、datetime、github、memory_tools、server_tools 内置工具。
- **四类供给抽象**：retriever/embedder/memory/object_store——外部包（mem0ai/rag/redis/s3/mysql）在各自 register.py 里按契约注册实现。
- **agent 家族**：`nvidia_nat_langchain` 的 react_agent（`ReActAgentWorkflowConfig(AgentBaseConfig, OptimizableMixin, name="react_agent")`，react_agent/register.py:61；`@register_function(framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])`，register.py:114）、rewoo_agent（rewoo_agent/register.py:38）、tool_calling_agent（tool_calling_agent/register.py:78）、reasoning/responses_api/auto_memory_wrapper/prompt_optimizer 等；路由 agent 也存在但住在 control_flow/ 目录（`control_flow/router_agent/register.py:30` `RouterAgentWorkflowConfig(name="router_agent")`）——NAT 用目录边界区分「agent=可复用求解函数」与「control flow=编排节点」。
- **可观测**：core `observability/` 自研 exporter（file/raw/span/processing）+ processor（batching/redaction 脱敏/span_tagging）管线，`nvidia_nat_opentelemetry` 打通 OTEL；`nvidia_nat_profiler` 做 token 计费（callbacks/calc）与容量预测（forecasting）。
- **评测**：`nvidia_nat_atif` 定义 ATIF（Agent Trajectory Interchange Format，注意全称是 Trajectory 交互格式，trajectory.py:16 docstring 三处一致）轨迹模型（trajectory/step/tool_call/observation）+ ATOF（Agentic Trajectory Observability Format）事件抽取，`nvidia_nat_eval` 提供 atif_evaluator 等评测器与 `nat eval` CLI，`nvidia_nat_data_flywheel` 从生产 OTEL span 走独立线（Span→TraceContainer→TraceAdapterRegistry）回流微调数据。

## 六、外围生态一览

34 包按职能分四类：**框架适配器**（langchain/agno/llama_index/adk/autogen/crewai/semantic_kernel/strands + 记忆类 mem0ai/memmachine/zep_cloud）；**协议出口**（mcp/fastmcp/a2a——Agent2Agent 协议带 OAuth 中间件、a365）；**工程域**（security/profiler/opentelemetry/eval/atif/ragas/data_flywheel/config_optimizer/nemo_customizer/redis/s3/mysql/phoenix/weave/openpipe_art/rag/test）；**产品组装**（nat_app——compiler/executors/graph/constraints 组成的应用编排引擎）。`external/dynamo/` 是 TensorRT-LLM Dynamo 后端的参考组件（kv_indexer 等），与 `dynamo_llm.py` 和 examples/dynamo_integration/ 对齐。

## 七、agent-first 设计（专节）

NAT 是罕见的「AI 编码代理一等公民」仓库。入口 `AGENTS.md:18` 自我定位为 "AI Agent Entry Point"，规定：技能住 `skills/` 扁平布局（AGENTS.md:20）；五条强制仓库规则（AGENTS.md:22-29）——保护用户未提交改动（先 `git status`）、优先现有模式而非新抽象、不随意加依赖、产品命名规范（首用全名 "NVIDIA NeMo Agent Toolkit"，`nat` 仅作技术标识符，AGENTS.md:27）、含糊任务先澄清；AGENTS.md:45-65 给出 14 行 Task Routing 表把任务路由到 11 个 skill；AGENTS.md:67-71 设立 **skill-evolution 预编辑门**——改任何 skill 前必须先读 `skills/skill-evolution/SKILL.md`，用户纠偏/命令报错/发现 gotcha 后回头评估技能是否该沉淀。

11 个 skill（nat-user-rules 总规范、nat-installation、nat-workflow-creation、nat-agent-configuration、nat-tools-and-functions、nat-evaluation、nat-optimization、nat-telemetry、nat-mcp-and-serving、nat-path-checks、skill-evolution）每个是 SKILL.md+references/ 深参考结构，如 nat-agent-configuration 带 agents.md/subagents.md/subagent-patterns.md/additional-agent-types.md 四篇参考。与 `docs/source/`（人类文档）构成双轨制：代理查 skills，人查 docs。Quick Commands 固化在 AGENTS.md:77-81（`uv run nat --help`、`uv run pytest packages/nvidia_nat_core`、`NAT_DISABLE_API_BUILD=1 make -C docs html`）。

## 八、上手路线与坑

**五步上手**：① 读 `examples/getting_started/simple_calculator/`——一个 pyproject+config.yml+register.py 三件套就是完整 NAT 包；② `uv run nat workflow create` 用脚手架生成新包（模板在 `packages/nvidia_nat_core/src/nat/cli/commands/workflow/templates/`：workflow.py.j2/config.yml.j2/register.py.j2/pyproject.toml.j2）；③ 装适配器包改 `_type` 换 agent 风格；④ 加中间件/前端（`_type: fastapi` 或 `mcp`）服务化；⑤ 用 `nat eval` + ATIF 评测。

**坑位图**：① `_type` 拼错报「找不到组件」时，先确认对应适配器包已安装（entry-points 没注册=组件不存在），`nat info list-components` 可盘点；② 大量 `aiq_` 前缀类名是前身 Agent Intelligence Kit 的兼容层，读代码别当新特性；③ per-user workflow 需要 front_end 配 `identity_header`（session.py:214），否则全部请求共享单例；④ MCP server 受保护示例（examples/MCP/simple_calculator_mcp_protected/）含 OAuth2 introspection 完整配置，别从裸 server 示例直接上生产；⑤ 3L 以上数据文件多为 Git LFS 指针（图谱甄别已录），本地不含真实内容；⑥ 测试跑单包即可（`uv run pytest packages/nvidia_nat_core`），全仓测试极重。

**图谱层导览**：16 步 tour 从 S01 门面→S03/S04 builder/注册表心脏→S05 数据模型→S06/S07 前端中间件→S08 供给→S09 安全→S10 CLI→S11 可观测→S12 评测→S13 适配器→S14 协议出口→S15 技能→S16 示例，建议按序读 explain 系列配合源码。
