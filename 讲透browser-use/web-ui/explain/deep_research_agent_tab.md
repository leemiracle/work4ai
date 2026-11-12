# deep_research_agent_tab.py 精讲——Deep Research 页：文件轮询驱动的异步任务控制台

> 源码：`/usr-data/data2/repos/browser-use/web-ui/src/webui/components/deep_research_agent_tab.py`（457 行）
> 图谱层位：L07 Gradio Tab 组件层（嵌于 Agent Marketplace 内）

## ① 角色定位

本文件是 Deep Research 功能的**UI 壳 + 任务驾驶舱**：它把用户输入（研究主题、并行度、保存目录、断点任务 ID）装配成 `DeepResearchAgent.run()` 的调用，并在 agent 跑长任务期间用**文件系统轮询**把中间产物（research_plan.md / report.md）搬回界面。与它相对，deep_research_agent.py 是纯引擎（LangGraph 状态机），对 Gradio 一无所知——两者只通过 `webui_manager.dr_*` 属性和磁盘文件通信。文件四个模块级成员：`_initialize_llm`（deep_research_agent_tab.py:18-40）、`_read_file_safe`（deep_research_agent_tab.py:43-52）、核心 `run_deep_research`（deep_research_agent_tab.py:57-290）、`stop_deep_research`（deep_research_agent_tab.py:293-355），尾部是 `create_deep_research_agent_tab`（deep_research_agent_tab.py:376-457）。

## ② 内部结构

界面仅 10 个控件（deep_research_agent_tab.py:406-419）：MCP 上载两件套、研究主题输入（默认值是一段瑞士旅行计划，deep_research_agent_tab.py:389-391）、resume_task_id、parallel_num、保存目录、Stop/Run 双按钮、Markdown 报告展示与下载。

`run_deep_research` 主体带 1-8 编号的段落注释，是全仓最清晰的异步生命周期范本：①收割设置并做**路径安全护栏**（deep_research_agent_tab.py:78-83）——`os.path.commonpath` 校验保存目录必须落在 `./tmp/deep_research` 之下，否则强制回退默认目录，防目录穿越；②锁 UI（Run 变 "⏳ Running..."，deep_research_agent_tab.py:97-106）；③跨 tab 读 agent_settings/browser_settings 并初始化 LLM（deep_research_agent_tab.py:116-147）；④懒加载单例 agent（deep_research_agent_tab.py:150-156）；⑤`asyncio.create_task` 起 agent 并记录 task id（deep_research_agent_tab.py:159-185）；⑥**监控循环**（deep_research_agent_tab.py:197-229）每秒查 plan 文件 mtime、变化才重读重推；⑦收尾读 report（deep_research_agent_tab.py:231-267）；⑧finally 恢复 UI（deep_research_agent_tab.py:275-290）。

## ③ 外部连接

- **DeepResearchAgent**（deep_research_agent_tab.py:12、151-155）：构造期传入 llm、browser_config 字典、mcp_config；`run(topic, task_id, save_dir, max_parallel_browsers)`（deep_research_agent_tab.py:159-164）不再收 MCP 参数——MCP 配置只在构造时注入一次。
- **跨 tab 配置**：`get_setting` 闭包按 `"{tab}.{key}"` 反查注册表（deep_research_agent_tab.py:118-120），LLM 取自 agent_settings，浏览器六项取自 browser_settings（deep_research_agent_tab.py:139-147）——注意传的是**配置字典而非 Browser 对象**，DR agent 自己起浏览器。
- **温度下限**：`max(temperature, 0.5)`（deep_research_agent_tab.py:125）——DR 页不允许低温，研究者要发散。
- **停止协议**：`stop_deep_research` 调 `agent.stop()`（deep_research_agent_tab.py:314），监控循环靠 `getattr(webui_manager.dr_agent, 'stopped', False)` 轮询退出（deep_research_agent_tab.py:200-203），停后等 1.5 秒再试着读最终报告（deep_research_agent_tab.py:322）。

## ④ 数据流

用户视角的数据闭环：输入主题 → Run → plan 文件在 `<save_dir>/<task_id>/research_plan.md` 被引擎写出（deep_research_agent_tab.py:189-191）→ 轮询发现 mtime 变化 → 内容推入 markdown_display（deep_research_agent_tab.py:206-216）→ 任务完成读同目录 report.md，同时把文件挂到下载控件（deep_research_agent_tab.py:245-252）→ finally 清 `dr_current_task`/`dr_task_id` 并解锁按钮。断点续跑反向流动：用户填 resume_task_id → 作为 `task_id` 传给 run（deep_research_agent_tab.py:75、161）→ 引擎复用该目录续写；界面还会把实际运行的 task id 回填进输入框（deep_research_agent_tab.py:199），方便用户抄下来。

## ⑤ 设计决策与取舍

- **文件系统当 UI 总线**：不侵入引擎加回调，而是监控引擎本来就要落盘的产物。代价是 1 秒轮询的延迟与 mtime 竞态（写入一半被读到），代码用"内容与上次不同才推"缓解（deep_research_agent_tab.py:212-216）。
- **agent 单例复用**：`if not webui_manager.dr_agent` 才构造（deep_research_agent_tab.py:150），浏览器/LLM 连接不重建；但见⑥的 MCP 代价。
- **生成器式 UI 更新**：`run_deep_research` 是 async generator，`start_wrapper` 逐段透传（deep_research_agent_tab.py:438-440），让"锁界面→流式刷新→解锁"在一个处理器里完成，Gradio 天然支持。
- **stop 的双段式**：Stop 处理器只发信号 + 展示"Stopping..."（deep_research_agent_tab.py:306-341），最终 UI 复位交给 run 侧的 finally——避免两个处理器同时改一批控件。

## ⑥ 新人提示（坑/勘误）

1. **组件 ID 错位**：保存目录控件注册名是 `max_query`（deep_research_agent_tab.py:398、410），取用时只能按 `deep_research_agent.max_query` 反查并注释自嘲 "component ID seems misnamed"（deep_research_agent_tab.py:65-66）——重命名会同时断掉 save_config 存档的兼容性。
2. **幽灵 ID 必崩分支**：无任务时点 Stop 走 else 分支，会反查 `deep_research_agent.max_iteration`（deep_research_agent_tab.py:351）——该控件从未注册，`get_component_by_id` 直接 KeyError。
3. **MCP 换文件不生效**：`update_mcp_server` 的 DR 版只 close 客户端不置 `dr_agent=None`（deep_research_agent_tab.py:362-364），复用路径下新 JSON 永远到不了构造参数（对比 agent_settings_tab.py:34 会置 None 强制重建）。
4. **dr_task_id 未初始化**：`init_deep_research_agent` 只声明 4 个属性（webui_manager.py:44-51），`dr_task_id` 是运行期动态属性（deep_research_agent_tab.py:185）——首次运行前点 Stop，deep_research_agent_tab.py:298 读它必 AttributeError（与坑 2 相同触发条件，先崩谁看属性访问顺序）。
5. **docstring 残留**：deep_research_agent_tab.py:424 又见 "Wrapper for handle_pause_resume."。
6. **1 秒轮询**是硬编码（deep_research_agent_tab.py:229），大报告场景 plan 展示最多滞后一轮。
