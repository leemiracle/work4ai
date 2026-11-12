# 11 · openhands/agenthub/：Agent 家族（CodeAct 核心、只读/定位继承、浏览旁支）

## 1. 角色定位

`openhands/agenthub/` 是 V0 的 **agent 实现动物园**：六个 agent 子包全部通过 `openhands/agenthub/__init__.py:5-12` 的 import 完成自我注册（`openhands/controller/agent.py:129` 的 `Agent.register` 注册表），上层用 `Agent.get_cls(name)` 按名取类。家族结构是一棵两层的树——`CodeActAgent` 是独根（CodeAct 论文思路：把所有动作统一为代码动作，`openhands/agenthub/codeact_agent/codeact_agent.py:65`），`ReadOnlyAgent`/`LocAgent` 继承它只换工具集与提示词，`BrowsingAgent` 则是从 `Agent` 抽象直接分叉的另一物种（BrowserGym 文本动作空间，无工具调用）；`DummyAgent`（测试桩）与 `VisualBrowsingAgent`（截图浏览）补全生态。全目录 Legacy-V0 头注（`openhands/agenthub/codeact_agent/codeact_agent.py:1-8` 还加了一句"V1 replacement lives in the Software Agent SDK"）。虽然整层将被外部 SDK 取代，但它承载了"如何用工具开关×提示词模板把一个 agent 派生成一个家族"的完整方法论。

## 2. 内部结构

**CodeActAgent**（`openhands/agenthub/codeact_agent/codeact_agent.py:57`，`VERSION = '2.2'`）：
- 构造（`:86-104`）：`pending_actions: deque` 双阶段执行队列（`:93`）；`ConversationMemory`（`:98`，事件→LLM 消息的 898 行转换器住在 `openhands/memory/conversation_memory.py`）；`Condenser.from_config`（`:100`）；`llm_registry.get_router`（`:104`，支持多模型路由）。
- 工具装配 `_get_tools`（`:116-161`）纯配置驱动：九个开关各自 append——`enable_cmd`→bash 工具（`:134-135`）、think（`:136-137`）、finish（`:138-139`）、condensation_request（`:140-141`）、browsing（`:142-146`，win32 直接警告跳过）、jupyter（`:147-148`）、**plan mode→task_tracker**（`:149-151`）、编辑器二选一（`:152-160`，`enable_llm_editor` 与 `enable_editor` 互斥）。对 gpt-4/o3/o1/o4 系模型自动切短工具描述（`:119-131`，规避 OpenAI 历史 1k 字符限制）。
- `step`（`:169-238`）四拍：pending 队列先出队（`:192-193`）；`/exit` 口令直接 Finish（`:196-198`）；condenser 输出 match——View 取压缩历史+遗忘集、Condensation 直接当动作返回（`:207-213`）；`llm.completion` 后 `response_to_actions` 可产多动作排队、返回队首（`:232-238`）。消息构造委托 `ConversationMemory.process_events`（`:300-306`），Anthropic 缓存在 `:308-309` 单独施加。
- 提示词资产 `prompts/`：`system_prompt.j2` 8906B 主模板、`system_prompt_interactive.j2`、`system_prompt_tech_philosophy.j2`、`in_context_learning_example.j2`、`security_risk_assessment.j2`、`microagent_info.j2`；**`user_prompt.j2` 是 0 字节空占位**；`openhands/agenthub/codeact_agent/prompts/system_prompt_long_horizon.j2:1` 以 `{% include "system_prompt.j2" %}` 开头，追加 `<TASK_MANAGEMENT>` 六条 task_tracker 使用军规（`openhands/agenthub/codeact_agent/prompts/system_prompt_long_horizon.j2:3-40`）与压缩后继续追踪任务的要求（`:42-46`）。

**ReadOnlyAgent**（`openhands/agenthub/readonly_agent/readonly_agent.py:30`，`VERSION='1.0'`）是"安全探索代码库"特化：覆写 `prompt_manager` 指向自己的 prompts 目录（`:63-70`）、覆写 `_get_tools` 只留五件套（`:72-75`）、`set_mcp_tools` 直接警告忽略 MCP 工具（`:77-85`）。工具三客 `GrepTool`/`GlobTool`/`ViewTool`（`readonly_agent/tools/` 的 grep.py/glob.py/view.py）**与 Claude Code 的 Glob/Grep/View 命名同源**——但实现是编译到 ripgrep 的 shell 命令：`grep_to_cmdrun` 拼 `rg -li {pattern} --sortr=modified ... | head -n 100`（`openhands/agenthub/readonly_agent/function_calling.py:51-83`，shlex.quote 全程转义 `:68-69`），`glob_to_cmdrun` 用 `rg --files {path} -g {pattern}`（`:86-114`，注释自认"最接近 NodeJS glob 实现"）；`response_to_actions` 里 Grep/Glob 都落成 `CmdRunAction`（`:176-202`），ViewTool 落成 `impl_source=OH_ACI` 的 `FileReadAction` 带 `view_range`（`:156-165`）。

**LocAgent**（`openhands/agenthub/loc_agent/loc_agent.py:21`）最薄：继承 CodeActAgent，构造里整体替换 `self.tools = locagent_function_calling.get_tools()`（`:38`），工具为 `tools/explore_structure.py` 与 `tools/search_content.py` 两件定位特化件；`response_to_actions` 同样换解析器（`:43-47`）。

**BrowsingAgent**（`openhands/agenthub/browsing_agent/browsing_agent.py:101`）不走工具调用：动作空间来自 BrowserGym 的 `HighLevelActionSet`（`:126-130`，subsets=['chat','bid']+'nav'）。三个环境变量在 **import 期**求值成进程级开关（`:33-43`：`USE_NAV`/`USE_CONCISE_ANSWER`/`EVAL_MODE`，专供 webarena/miniwob 基准）。`step`（`:140-230`）是手写状态机：扫 `state.view` 收集 prev_actions/url/axtree（`:166-174`），agent 已发消息即 Finish（`:170-172`）；BrowserGym 的 `send_msg_to_user` 转成 OpenHands 的 MessageAction（`:182-186`）；错误累积超 5 次判失败（`:188-194`）；可达树用 `flatten_axtree_to_str` 压平（`:199-204`）；LLM 输出由 `BrowsingResponseParser`（`openhands/agenthub/browsing_agent/response_parser.py:19`）解析——补全 ```)``` 尾巴的自动修复（`:42-48`）、无代码块当消息（`:59-76`）、`ast.parse` 抠 `send_msg_to_user` 参数+正则兜底（`:113-127`）。

**注册面**：各子包 `__init__.py` 尾部一行 `Agent.register('XxxAgent', XxxAgent)`（如 `codeact_agent/__init__.py`、`browsing_agent/__init__.py` 末行）；`openhands/agenthub/__init__.py:3` 还有个副作用 `load_dotenv()`（import agenthub 就加载 .env——层级相当诡异的隐式行为）。

## 3. 外部连接

家族向上被 `AgentSession`/`run_controller` 按 `config.default_agent` 名字实例化；注册机制靠 import 副作——`openhands/server/app.py` 与 `openhands/core/setup.py` 都"纯为触发注册"而 `import openhands.agenthub`（批 9/11 阶段实证）。CodeActAgent 的依赖扇出最大：`openhands/controller/agent.py:33` 的 Agent 基类（`register`/`get_cls`/`step` 抽象 `:113`）、`memory/conversation_memory.py`、`memory/condenser`（`:46-47`）、`runtime/plugins` 的 `AgentSkillsRequirement+JupyterRequirement`（`:49-53`，注释强调 skills 必须先于 Jupyter 初始化 `:79-83`）、`utils/prompt.py` 的 PromptManager（`:107-114` 惰性加载 prompts 目录）。工具定义住在 `codeact_agent/tools/` 十二件（bash/browser/finish/ipython/str_replace_editor/task_tracker/think 等，多为模块级 `ChatCompletionToolParam` 常量）。BrowsingAgent 依赖外部包 browsergym（`openhands/agenthub/browsing_agent/browsing_agent.py:10-11`）。计划模式联动 `openhands/core/config/agent_config.py`：`system_prompt_filename` 默认 `system_prompt.j2`（`openhands/core/config/agent_config.py:29`）、`enable_plan_mode` 默认 True（`:59`）、`resolved_system_prompt_filename` 在两者同时默认时自动切 `system_prompt_long_horizon.j2`（`:80-88`）——**这就是长视野提示词的自动切换机关**。

## 4. 数据流

CodeAct 一步：controller 调 `agent.step(state)` → pending 队列检查 → condenser 产 View → `ConversationMemory.process_events` 把事件流转成 Message 列表（带遗忘集与视觉能力参数）→ `check_tools` 过滤（`:226`）→ `llm.completion`（附 `state.to_llm_metadata` 的会话元数据 `:227-231`）→ `codeact_function_calling.response_to_actions` 把工具调用翻成 Action 列表（`:313-317`，含 MCP 名单注入 `:316`）→ 全部入 pending 队列返回队首 → controller 确认闸门→事件流→runtime 执行。Browsing 一步则无队列：直接从 view 重建 prompt（url+axtree+prev_actions 三段）→ completion（stop 序列 `[')```', ')\n```']` 防跑飞，`:226-229`）→ response_parser 产 `BrowseInteractiveAction`。

## 5. 设计决策

Legacy-V0→V1 语境下四个决策：其一，**继承换工具集**（ReadOnly/Loc 覆写 `_get_tools`/`prompt_manager`/`response_to_actions` 三点）而非组合——V1 SDK 把这个模式反转成"工具集配置化"，但 V0 的三覆写点足够小，继承税可控。其二，**提示词模板目录+惰性 PromptManager**（`openhands/agenthub/codeact_agent/codeact_agent.py:106-114`）：系统提示文件名可配置，子类只换 `prompt_dir` 就有完整人格；`user_prompt.j2` 留 0 字节占位是"目录契约"的一部分（PromptManager 要求文件存在但不要求有内容）。其三，**plan mode 是提示词层功能而非控制流功能**：`enable_plan_mode` 只影响工具清单（`openhands/agenthub/codeact_agent/codeact_agent.py:149-151`）与系统提示选择（`openhands/core/config/agent_config.py:80-88`），loop/控制器完全无感——最小侵入的多模态开关设计。其四，**BrowsingAgent 拒绝工具调用范式**：文本动作空间+stop 序列+字符串解析（`openhands/agenthub/browsing_agent/browsing_agent.py:226-230`）是 2023 年范式的活化石，代价是解析器要不断打补丁（response_parser 的三种兜底 `:42-127`），V1 线已将其淘汰。

## 6. 新人提示

- **死代码**：`openhands/agenthub/browsing_agent/utils.py`（182 行）全仓零消费者——`yaml_parser`（`:15`）、`compress_string`/`_compress_chunks`（`:32`/`:56`）、`parse_html_tags`（`:129`）无一被 import（grep 实证），是旧版 BrowsingAgent 的解析残留，别在新代码里引用。
- **勘误**：不存在 `openhands/agenthub/agents/__init__.py` 这个注册文件——注册动作在各子包自己的 `__init__.py` 尾行，总注册面是 `openhands/agenthub/__init__.py:5-12`。
- 双份维护陷阱：ICL 示例在 `prompts/in_context_learning_example.j2`（5576B）与 `openhands/llm/fn_call_converter.py:394` 的 `IN_CONTEXT_LEARNING_EXAMPLE_PREFIX = get_example_for_tools` 硬编码**逐字双份**（fn_call_converter 在 `:519` 为首条用户消息注入）——改示例必须两处同改。
- `openhands/agenthub/__init__.py:3` 的 `load_dotenv()` 是 import 副作用：任何 import agenthub 的进程都会被工作目录下的 `.env` 污染环境变量，调试诡异配置时先查这里。
- BrowsingAgent 的三个开关在 import 期冻结（`openhands/agenthub/browsing_agent/browsing_agent.py:33-43`）——运行中改环境变量无效，测试必须用子进程隔离。
- `openhands/agenthub/readonly_agent/function_calling.py:54-56` 与 `:87-89` 两处 TODO 自曝依赖：Grep/Glob 都依赖 ripgrep（`rg`）装在 runtime 里，CLIRuntime/LocalRuntime 可能没有——工具会以"命令找不到"的形式失败。
- ReadOnlyAgent 明确拒绝 MCP（`openhands/agenthub/readonly_agent/readonly_agent.py:77-85`）："只读"承诺靠工具白名单而非沙箱——底层仍是 `CmdRunAction`（`openhands/agenthub/readonly_agent/function_calling.py:187`/`:202`），沙箱逃逸时白名单即失效。
- `openhands/core/config/agent_config.py:59` `enable_plan_mode` **默认 True**：开箱即用的 CodeActAgent 用的其实是 `system_prompt_long_horizon.j2`（含 task_tracker 军规），不是 `system_prompt.j2`——读默认提示词别读错文件。
