# 04 · dataflow_agent 框架核心：BaseAgent、执行策略与供应商层

## 角色定位

`dataflow_agent/` 是整个平台的心脏——一个多 agent 编排框架，上游血统是 OpenDCAI 的 DataFlow-Agent（README:844 仍引用 `/DataFlow-Agent/script/...` 路径）。它定义"agent 是什么"（BaseAgent 抽象基类）、"agent 怎么跑"（7 种执行策略）、"agent 用什么模型"（llm_callers + 12+ 供应商 ABC）、"agent 怎么组装成图"（GenericGraphBuilder）。业务层的 41 个领域角色（paper2any_agents 40 + common 1）全部继承自这里的 BaseAgent；06 篇的 wf_* 工作流全部建立在本篇的骨架上。03 篇的 FastAPI 只是它的 HTTP 壳。

## 内部结构

**BaseAgent（agentroles/cores/base_agent.py 1538 行，L95 `class BaseAgent(ABC)`）**：全框架最重的单类。`__init__`（L172-235+）参数即能力开关：`tool_manager`（工具集）、`temperature/max_tokens`、`tool_mode`、`react_mode + react_max_retries`（ReAct 循环）、`parser_type/parser_config`（输出解析器）、`use_vlm + vlm_config`（视觉模型通道）、`ignore_history/message_history`（记忆策略）、`chat_api_url`、`execution_config`。LLM 调用器按 `use_vlm` 二选一（L501-512 注释自述：返回 VisionLLMCaller 或 TextLLMCaller）。

**__init_subclass__ 双通道自动注册**是框架第一诀窍（base_agent.py:150-171）：任何 BaseAgent 子类在**类定义完成那一刻**触发钩子——创建临时实例 `cls(tool_manager=None)` 读取其 `role_name` 属性，随即以 `role_name.lower()` 为键注册进 AgentRegistry；构造失败的子类（抽象中间层）静默跳过。第二通道是显式 `@register("name")` 装饰器（cores/registry.py:31-39），同样落 AgentRegistry，且重复注册同名异类会抛 ValueError（registry.py:15-20）。registry 本体仅 39 行：`register/get/all` 三个类方法 + 模块级 dict（registry.py:7），`get` 未命中时报错并附全部可选名单（registry.py:22-26）——双通道意味着"写完子类即全局可用"，代价见批判节。

**7 策略执行家族（cores/strategies.py 794 行）**：`ExecutionStrategy`（L13，ABC）之下七个具体策略——SimpleStrategy（L26 单发）、ReactStrategy（L36 工具循环重试）、GraphStrategy（L61 子图编排）、VLMStrategy（L77 图文多模态）、ParallelStrategy（L107 并发扇出）、PlanSolveStrategy（L126 先规划后求解）、PlanExecuteStrategy（L361 带审批中断的分步执行，794 行里独占 400+ 行，是复杂度之王）。`StrategyFactory`（L771）以 mode 字符串路由七者，且开放 `register` 注册自定义策略（strategies.py:792-794）。BaseAgent 的 `execution_config` 最终决定实例化哪个策略。

**41 个领域角色（agentroles/paper2any_agents/ 40 文件 + common_agents/ 1）**：role_name 全量实测 41 个，按产品线分族——PPT 线 outline_agent/long_paper_outline_agent/outline_refine_agent/content_expander/topic_writer；图表线 diagram_planner/diagram_editor/diagram_vlm_validator/drawio_xml_generator/chart_code_generator/chart_type_recommender/figure_desc_generator/diagram_segment_hint_agent；技术路线线 tech_route_reference_analyzer/technical_route_desc_generator/technical_route_bw_svg_generator/technical_route_colorize_svg_agent/svg_bg_cleaner_agent；检索线 websearch_initial_analyzer/planner/researcher/curator 四件套；视频线 p2v_* 七件套（beamer 生成/调试/升级、extract_pdf、pdf2ppt、subtitle_and_cursor、refine_subtitle_and_cursor）；KB 线 kb_outline_agent/kb_prompt_agent/kb_image_insert_agent；以及 icon 三件、table 两件、qa_agent、deep_research_agent、paper_idea_extractor、ImageTextBBoxAgent。每个角色 = 一个 py 文件 = role_name 属性 + prompt 模板引用 + 输出解析。

**llm_callers 三件**：`BaseLLMCaller`（llm_callers/base.py:14，ABC）、`TextLLMCaller`（text.py:10，40 行薄封装）、`VisionLLMCaller`（image.py:22，227 行，多模态消息组装）。

**providers 供应商层（toolkits/multimodaltool/providers.py 1706 行）**：`AIProviderStrategy` ABC（L15）统一定义"文生图/TTS/多模态理解"的供应商接口，之下 13 个具体 provider（实测计数，任务书"12 供应商"按源码勘误为 13）：ApiYiGeminiProvider（L134）、IkunCodeGeminiProvider（L320）、Local123GeminiProvider（L515）、ApiYiSeeDreamProvider（L671）、ApiYiGPTImageAllProvider（L711）、ApiYiGPTImageProvider（L746）、OpenAIDalleProvider（L875）、CosyVoiceProvider（L927）、OpenAITTSProvider（L1000）、OpenAICompatGeminiProvider（L1056）、GoogleNativeProvider（L1157）、ComflyProvider（L1183）。文件尾部还有两个非供应商枢纽：`TokenUsageTracker`（L1417，用量记账）与 `LLMClient`（L1486，统一门面，03 篇 rebuttal_service.py:12 直接引用）。

**GenericGraphBuilder（graphbuilder/graph_builder.py 148 行）**：链式建图器，核心是 role 维度的工具拦截——`@pre_tool(name, role)`（L39-46）在指定角色的指定工具调用前插钩子、`@post_tool(role)`（L48-54）在后插钩子，注册表按 role 分桶（L26-27）；`build` 时把钩子经 ToolManager 的 register_pre_tool/register_post_tool 注入（L95-115）。这让"同一个工具在不同 agent 手里行为不同"无需改 agent 代码。

**脚手架与状态**：`dfa create` CLI（cli.py:187 行）用 templates/ 7 个 jinja（agent/workflow/state/test/gradio_page/prompt_repo/agent_as_tool）一键生成新 agent+工作流+测试骨架。state.py（788 行）以 `@dataclass` 定义 29 个状态类——MainRequest/MainState 基类（L14/L41）派生 DF、Paper2Video、Planning（含 PlanStep）、Paper2Figure、IntelligentQA、KBPodcast、KBMindMap 等成对 Request/State，是 LangGraph 图的共享状态契约（router 直接 import，见 kb.py:18）。

## 外部连接

- **上游血统**：包名 `dataflow_agent` 与 pyproject `include = ["dataflow_agent*"]`（pyproject.toml:59）是 DataFlow-Agent 的移植保留；`dfa` 入口（pyproject.toml:63）、templates 脚手架、docs 里 `/DataFlow-Agent/` 路径引用全部继承。
- **fastapi_app**：services 经 `run_workflow` 驱动 wf_* 图；state.py dataclass 被 router 层直接使用。
- **toolkits**（05 篇）：BaseAgent 的 tool_manager 装载 tool_manager.py（118 行）注册的角色化工具；providers.py 物理上住在 toolkits/multimodaltool/ 内，本篇与 05 篇各讲一半。
- **paper2any_agents**：41 角色的 prompt 全部来自 promptstemplates（prompts_repo.py 2460 行总仓，见 06 篇）。
- **LangGraph**：strategies 的 Graph/PlanExecute 与 wf_* 图构建都压在 langgraph 之上。

## 数据流

定义期：开发者继承 BaseAgent → `__init_subclass__` 自动注册（或 @register 显式）→ AgentRegistry 全局可查。装配期：wf_* 图经 GenericGraphBuilder 声明节点（name→(func, role) 二元组，graph_builder.py:21）→ pre/post_tool 钩子挂到 ToolManager → 图构建完成。执行期：HTTP 请求 → service 构造 Request dataclass → `run_workflow` 起 LangGraph → 节点内 `agent.execute(state)` → BaseAgent 按参数选 Text/Vision caller → StrategyFactory 按 execution_config 实例化策略 → 策略驱动 LLM 调用（可循环调工具，工具再落 providers 的某个供应商）→ TokenUsageTracker 记账 → 解析器产出结构化结果写回 State → 下一个节点。

## 设计决策（含批判）

1. **__init_subclass__ 临时实例注册是"魔法换便利"**：写子类即注册，零样板；但三个坑真实存在——①临时实例要求 `cls(tool_manager=None)` 可构造，任何在 `__init__` 里做重活的子类会在**类定义时**就执行一次重活；②`except Exception: pass` 静默吞掉注册失败（base_agent.py:169-170），一个 role_name 拼写错误不会报错，只会让该 agent "查无此人"到运行期；③双通道（隐式 + @register）注册同一类时若 role_name 大小写不一致会产生两个键。
2. **1538 行 BaseAgent 同样是上帝类苗头**：身份（role_name/prompt）、执行（react/vlm/parallel 开关）、记忆（history）、解析（parser）四域合一；不过它用策略模式把执行语义外包给 strategies.py，比 03 篇巨类健康得多。
3. **PlanExecuteStrategy 独占近半文件**：带 interrupt 审批的规划执行是框架最复杂路径，也是测试最薄弱处（tests/ 无 strategies 直接单测）；改它必须跑全量回归。
4. **providers 13 具体类挤一个 1706 行文件**：每家一个 class 本身是干净的 ABC 多态，但 Gemini 系四家（ApiYi/IkunCode/Local123/OpenAICompat）高度相似，存在可合并的模板方法空间；新增供应商照抄一个类是最快路径，债务可控制在常数级。
5. **移植残留实证**：`toolkits/dockertool/Makefile` 的 build target 执行 `python -m dataflow.dataflowagent.toolkits.dockertool.build_docker`（Makefile:6）——模块路径还是上游的 `dataflow.dataflowagent.*` 三层嵌套，本仓实际包是 `dataflow_agent`，**`make build` 必 ModuleNotFoundError**；run-thirdparty/run-stdlib 目标的 `--file dataflow/dataflowagent/...` 相对路径同样指向不存在的目录。这是"包名改了、深处引用没改"的典型移植疤痕，也是识别 fork 世系的化石。
6. **41 角色 vs 图谱摘要"22-agent"**：L08 图层摘要写 22-agent，实测 role_name 全量为 41——知识图谱摘要的计数口径（可能只数框架文件数）与源码事实有差，以源码为准。
7. **dfa 脚手架是好设计**：7 个 jinja 模板 + cli 生成全套 agent/workflow/test/prompt_repo，把"新增一条产品线"的样板成本压到最低，也保证了 41 角色的文件形态高度一致——这正是新人上手最快的路径。

## 新人提示

- 写新 agent 的最短路径：`dfa create`（cli.py:31-119）生成骨架，改 role_name 与 prompt 引用，继承链与注册全自动；千万别忘了 role_name 必须可读——它是注册键。
- 查"agent 为什么没注册上"：先确认子类 `cls(tool_manager=None)` 能否无参构造（__init_subclass__ 的隐含契约），再看 role_name 拼写；静默失败意味着没有报错可查。
- 执行模式七选一参考 strategies.py:774-781 的 mode 表：simple 单发、react 带工具循环、graph 子图、vlm 多模态、parallel 并发、plan_solve/plan_execute 规划族。
- 改供应商行为去 providers.py 找对应 class（按 L 行号索引）；改"工具在某个 agent 手里的行为"去 wf_* 图的 @pre_tool/@post_tool 钩子，不要改 agent 本体。
- 跑 dockertool 前先改 Makefile：把 `dataflow.dataflowagent` 全局替换为 `dataflow_agent`，否则 build/run 三个 target 全炸。
- state.py 加新工作流状态：继承 MainRequest/MainState 成对添加，dataclass 字段即 LangGraph 的 state schema，router 层可直接复用。
