# deep_research_agent.py 精讲——DeepResearchAgent：LangGraph 编排的浏览器研究流水线

> 源码：`/usr-data/data2/repos/browser-use/web-ui/src/agent/deep_research/deep_research_agent.py`（1261 行，本系列最大文件）
> 图谱层位：L05 Agent 引擎层

## ① 角色定位

`DeepResearchAgent` 是 web-ui 内置的"深度研究"引擎——用户给一个主题，它产出一份带结构的 Markdown 报告，全程用真实浏览器搜集资料。它与 Run Agent 页的 `BrowserUseAgent` 是**两种不同层级的 agent**：

- `BrowserUseAgent`：单任务步进循环（感知→决策→动作）；
- `DeepResearchAgent`（本文件）：**agent 的 agent**——用 LangGraph 状态机做编排层，把主题拆成类别/任务两层计划（deep_research_agent.py:304-315），再为每个任务现场生成一个 `BrowserUseAgent` 子实例去执行搜索（deep_research_agent.py:133-141）。

文件骨架四段：浏览器子任务执行器（:50-298）、LangGraph 状态与节点（:301-976）、编排类 `DeepResearchAgent`（:982-1261）。图结构只有四个节点：`plan_research → execute_research ⇄（自环）→ synthesize_report → end_run`（:1055-1080），复杂度全在节点内部而非图拓扑。

## ② 内部结构

**子任务执行 `run_single_browser_task`（deep_research_agent.py:50-194）**：每次调用现场造一套完整栈——`CustomBrowser`（含 BrowserConfig：headless/窗口尺寸/wss/cdp，:95-107）→ 强制新建的 context（`force_new_context=True`，:109-115）→ 裸 `CustomController()`（:118，不带 MCP）→ `BrowserUseAgent`（:133-141，任务 prompt 要求返回"摘要+标题+URL"三件套，:122-131，并内置 PDF 处理指令"先下载再用 read_file"，:130）。实例以 `{task_id}_{uuid4()}` 为键登记进模块级 `_BROWSER_AGENT_INSTANCES`（:144-145）供 stop 使用；finally 里关 context、关 browser、清登记（:176-193）。

**搜索工具工厂（deep_research_agent.py:196-298）**：`parallel_browser_search` 是给编排 LLM 用的唯一浏览器工具。`BrowserSearchInput` 只有一个 `queries: List[str]` 字段（:196-199）；`_run_browser_search_tool` 先**硬截断** `queries[:max_parallel_browsers]`（:216，防 LLM 无视说明）、`Semaphore` 限并发（:222）、`asyncio.gather(return_exceptions=True)` 汇总（:242）、三态归一（cancelled/failed/dict，:244-263）。依赖注入用 `functools.partial` 把 task_id/llm/browser_config/stop_event 绑进函数（:282-289），再 `StructuredTool.from_function(coroutine=...)` 成工具（:291-298）——**工具描述里动态写明并发上限**（:294-296），让 LLM 知道该给几条 query。

**LangGraph 状态（deep_research_agent.py:318-332）**：`DeepResearchState` 是 TypedDict，值得注意它把 `llm`、`tools`、`browser_config` 这类**大对象直接塞进图状态**——LangGraph 状态本应可序列化（checkpoint 场景），这里为了省事全部走内存引用，代价是这条图永远不能用持久化 checkpointer。

**三个节点**：

- `planning_node`（:461-606）：few-shot JSON prompt（含 4 个示例类别，:487-517，明确"3-10 类别、2-6 任务"，:519）→ 剥 ```json 围栏（:531-534）→ `json.loads` → 容错三种 LLM 输出形态（纯字符串任务 :548、`{"task_description": ...}` :558、常见的 `{"task": ...}` :567）→ 存 `research_plan.md`（:592）。若已有计划且游标>0 则直接跳过规划（:472-477，断点续跑入口）。
- `research_execution_node`（:609-808）：单任务执行。`llm.bind_tools(tools)`（:664）→ 组任务 prompt（:667-673）→ `ainvoke`（:687）→ 逐 tool_call 执行（:706-750，每次执行前查 stop_event :722-728）→ 成败判定（:753-768）→ 存盘（:770-772）→ 游标推进（:774-779）→ 消息累积（:781）。
- `synthesis_node`（:811-932）：把 `search_info.json` 里的结果格式化为 Markdown 素材（三分支：浏览器搜索结果 :846-852 / 其他工具 :853-856 / 失败项 :857-862），连同计划完成度摘要（:865-870）一起喂给 LLM 写报告（:872-912），存 `report.md`（:927）。

**路由 `should_continue`（deep_research_agent.py:938-976）**：三出口——stop 或严重错误（错误信息含 `"Core Execution Error"` 子串匹配，:943-945）→ end_run；计划还有待办 → execute_research；全部完成 → synthesize_report。

**编排类（deep_research_agent.py:982-1261）**：`__init__` 即编译图（:1003）；`run`（:1085-1224）防重入（:1102-1111）、路径防护（normpath + startswith 把 save_dir 圈进 `./tmp/deep_research`，:1114-1119）、注册 stop_event 进模块级 `_AGENT_STOP_FLAGS`（:1127-1128）、组装初始状态（:1132-1147）、可选恢复（:1149-1165）、`asyncio.create_task(graph.ainvoke(...))`（:1173）、四态收尾判定 stopped/error/completed/finished_incomplete（:1177-1194）。`stop`（:1249-1258）置位 event 并逐个 `.stop()` 残留浏览器 agent（:1226-1247）。

## ③ 外部连接

**向下复用三件套**：`BrowserUseAgent`（:34）、`CustomBrowser`（:35）、`CustomController`（:36）——深研究链是 web-ui 内部架构的完整复检：每次子任务都走一遍与 Run Agent 页同款的浏览器栈。**MCP**：`setup_mcp_client_and_tools`（:37）在 `_setup_tools` 里按需连接（:1029-1032），MCP 工具作为 LangChain 工具直接给编排 LLM（与 controller 链的注册表路径不同，见 mcp-client 篇）。**文件工具**：langchain-community 的 Read/Write/ListDirectory（:11-15）也是编排 LLM 的工具，配合任务 prompt 里的"PDF 先下载再 read_file"指令形成资料采集闭环。

**向上**：UI 消费方是 `deep_research_agent_tab.py`——`get_llm_model` 造 LLM（:27）、`DeepResearchAgent(...)` 构造（:151）、结果目录约定 `./tmp/deep_research/{task_id}/`。**持久化三文件**既是产物也是断点载体：`research_plan.md`（checkbox 进度）、`search_info.json`（结果集）、`report.md`（终稿）——`_load_previous_state`（:338-418）逐行解析 md 的 `## ` 类别行（:357）与 `- [ ]/- [x]/- [-]` 三态任务行（:365-371），推算续跑游标（:378-383）。

## ④ 数据流

```
用户主题（UI）
  → DeepResearchAgent.run(topic)                     :1085
  → planning_node：LLM few-shot → 类别×任务 两层计划   :481-521
  → 存 research_plan.md（全部 - [ ]）                 :592
  ┌─ execute_research 循环（每任务一轮）────────────┐
  │ 编排 LLM（bind_tools）产出 queries                :664-687
  │ → parallel_browser_search 工具                   :731
  │    → run_single_browser_task × N（Semaphore）    :232
  │        → 新 CustomBrowser+Controller+BrowserUseAgent :95-141
  │        → 子 agent 跑完 → final_result（摘要文本） :159-162
  │ → 结果并入 search_info.json（覆写全量）            :772
  │ → 计划 checkbox 打勾 → 存 research_plan.md        :770-771
  │ → 游标+1 → should_continue 判定下一步              :774-779 / :938
  └──────────────────────────────────────────────┘
  → synthesize_node：素材格式化+计划摘要 → LLM 成文     :836-912
  → report.md 落盘 → 返回四态 status                   :927 / :1177-1194
```

两条横切通道独立于主数据流：**停止信号**（UI 停止按钮 → `stop()` :1249 → `threading.Event` 置位 → 节点入口/工具执行前/子任务前多处轮询 :611/722/151）与**实例登记表**（`_BROWSER_AGENT_INSTANCES` :47，stop 时兜底强停滞留的子 agent :1226-1247）。

## ⑤ 设计决策与取舍

**为什么用 Markdown checkbox 而不是 JSON 存计划？** `research_plan.md`（:421-435）人类可读、可手改、可在 UI 里直接看进度——代价是解析器（:347-386）要处理行级状态机（类别标题行/任务行/游标回推）。这是"产物即状态"的取舍：宁要 40 行解析代码，也要让用户能打开文件看懂研究进行到哪。`search_info.json` 则相反选了机器格式（全量覆写，:438-447），两类状态各取所需。

**每任务现起浏览器 vs 长驻一个浏览器**。`run_single_browser_task` 的 finally（:176-193）保证每子任务零残留——隔离性强、一条任务崩溃不污染下一条；代价是每任务冷启动浏览器（秒级开销）且无法复用登录态。对研究报告场景（多站点、浅交互）这个取舍合理；若做"需要登录的纵深研究"就得改成会话复用。

**编排层信任策略：工具输出直写状态**。`parallel_browser_search` 的返回直接 extend 进 `search_results`（:735），不再让 LLM 转述——避免了摘要链上的信息损耗，但也意味着报告质量上限锁死在子 agent `final_result()` 的文本质量（synthesis 的 prompt 里也承认这一点，:851 注释）。综合时 LLM 只做重组不做核实，"浏览器 agent 说什么就是什么"。

**游标推进集中化**：任务完成后无论成败都推进游标（成功 :774-779、异常 :797-801）——研究任务失败不重试、不阻塞全局，这是"广度优先、尽力而为"的策略，与 Run Agent 页的连续失败止损（browser_use_agent.py:83）形成对照。

**字符串嗅探当协议用**：失败判定靠 `"Error:" in str(tr.content)`（:753）、严重错误路由靠 `"Core Execution Error" in error_message`（:943）——脆弱但零依赖。若工具输出正文恰好含 "Error:" 会被误判失败，这是已知风险。

## ⑥ 新人提示（坑与勘误）

1. **真 bug：无工具调用分支丢失游标（deep_research_agent.py:694-703）**。LLM 没调工具时，代码把 `current_category_index`/`current_task_index_in_category` 塞进 **task dict**（:700-701）然后 `return current_task`——LangGraph 拿到的 partial state 里没有任何合法状态键，游标不推进、任务仍标 pending（:698），下一轮又执行同一任务。若 LLM 持续不调工具（比如模型不兼容 bind_tools），图会在同一点无限自环烧 token。修复应返回包含游标的合法 state dict。
2. **真 bug：死分支（:1038-1041）**。`elif self.mcp_server_config:` 紧跟同条件的 `if self.mcp_server_config:`（:1026），永假；原意大概是判"配置存在但导入失败"，现在那条 warning 永远打不出来。
3. **引用列表永不生成**：`references = {}`（:837）之后无任何写入，`if references:`（:916）恒 False——报告不会有 References 段。根因在 :843-851 注释自陈：子 agent 只返回字符串摘要，标题/URL 没有结构化回传，与任务 prompt 要求的三件套（:125-128）断了契约。**任务描述要 URL、执行拿不到 URL、综合不列 URL**，这条断链是全文件最值得重构的三个点之一。
4. **`if not BrowserUseAgent:`（:62）恒 False 死检查**——模块级导入成功即非空，这段防御性代码永远不会走到。
5. **子 agent `run()` 不传 max_steps（:159）**：吃到 browser-use 默认 100 步——单个子搜索最多烧 100 步 LLM 调用，深研究一次跑几十个任务时成本惊人，接手加预算控制先改这行。
6. **`search_info.json` 全量覆写（:443）**：断点续跑靠它 + 计划 md 双文件，只删其中一个会造成"计划说做完了、结果却缺失"的错位；手工清理时两个一起动。
7. **消息无限累积（:781）**：`updated_messages = state["messages"] + ...` 每任务追加不裁剪，长研究后上下文膨胀，LLM 成本与延迟随之上升（browser-use 主链有消息裁剪，这条链没有）。
8. **`tools_map` 同名覆盖（:1042-1043）**：`{tool.name: tool}` 让 MCP 工具与内置工具同名时后者被覆盖——同名静默失配，排查"工具调不动"时先查命名冲突。
9. **测试入口**：`tests/` 四文件是手动 smoke 脚本（`import pdb` 开头、需真实 key、直接 python 运行），不覆盖本文件的 LangGraph 逻辑；验证改动请用 `./tmp/deep_research/` 的三文件做断点续跑手工回归。

一句话总结：这是一条"LLM 规划 → 浏览器 agent 并行采集 → LLM 成文"的三段流水线，工程亮点在 Markdown 进度即持久化、Semaphore+partial 的工具依赖注入与三文件断点续跑；三处真 bug（:700 游标丢失自环、:1038 死分支、:916 永空的引用段）都集中在"编排层与子 agent 的契约"上——改这个文件，先守住游标推进与结果契约这两条命脉。
