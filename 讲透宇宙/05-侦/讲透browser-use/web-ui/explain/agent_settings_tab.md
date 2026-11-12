# agent_settings_tab.py 精讲——Agent Settings 页：22 控件与"全量快照"配置协议

> 源码：`/usr-data/data2/repos/browser-use/web-ui/src/webui/components/agent_settings_tab.py`（269 行）
> 图谱层位：L07 Gradio Tab 组件层

## ① 角色定位

`agent_settings_tab.py` 是五个标签页中**第一个被装配**的配置页（interface.py:72-73），负责收齐"用哪个模型、怎么调、允许跑多久"这三类决策。它本身不含任何业务逻辑——控件值只是被注册进 `WebuiManager`，等 Run Agent 或 Deep Research 页的运行处理器来收割。文件由三块构成：两个模块级回调函数 `update_model_dropdown`（agent_settings_tab.py:15-24）与 `update_mcp_server`（agent_settings_tab.py:27-43），以及主体 `create_agent_settings_tab`（agent_settings_tab.py:46-269）。注意图谱 hub 摘要写"20 个控件"是漏数——`tab_components` 字典（agent_settings_tab.py:213-236）实际注册 **22 个控件**。

## ② 内部结构

界面按 `gr.Group` 分五段：

- **提示词组**（agent_settings_tab.py:53-56）：`override_system_prompt` / `extend_system_prompt` 两个多行文本框，对应 BrowserUseAgent 构造时的 `override_system_message` / `extend_system_message` 两个互斥入口。
- **MCP 组**（agent_settings_tab.py:58-60）：`mcp_json_file` 文件上载 + 默认隐藏的 `mcp_server_config` 文本框（上传后展开显示 JSON 全文，可手工再编辑）。
- **主 LLM 组**（agent_settings_tab.py:62-119）：provider 与 model 双下拉、temperature 滑条、use_vision 开关、仅 ollama 可见的 num_ctx 滑条（agent_settings_tab.py:97-106，初始 `visible=False`）、base_url 与 api_key（password 型）。
- **Planner LLM 组**（agent_settings_tab.py:121-176）：与主 LLM 完全同构的七件套，全部前缀 `planner_`，默认不选 provider 即整组不生效。
- **预算组**（agent_settings_tab.py:178-212）：`max_steps`（1-1000，默认 100）、`max_actions`（每步动作数上限，默认 10）、`max_input_tokens`（默认 128000）、`tool_calling_method` 下拉（六选项 + `allow_custom_value`，agent_settings_tab.py:205-212）。

事件绑定集中在函数尾部：两个 provider 的 `change` 各绑两次——一次切换 ollama 滑条可见性（agent_settings_tab.py:239-243、249-253），一次刷新模型下拉（agent_settings_tab.py:244-248、254-258）；MCP 文件上载走 `update_wrapper`（agent_settings_tab.py:260-263）。

## ③ 外部连接

- **config.model_names** 是下拉框的唯一数据源（agent_settings_tab.py:20-21、65、73-74）：provider 列表 = 字典键集合；`DEFAULT_LLM` 环境变量决定初始选中项，缺省 "openai"。
- **WebuiManager**：`add_components("agent_settings", ...)`（agent_settings_tab.py:237）把这 22 个控件挂进全局注册表，此后它们能被任何 tab 的处理器以 `agent_settings.<key>` 反查。
- **消费方**：Run Agent 页的 `get_setting("agent_settings.xxx")`（browser_use_agent_tab.py:327-345）与 Deep Research 页的 `get_setting`（deep_research_agent_tab.py:118-133）都按这个前缀取值。
- **update_mcp_server 与 deep_research_agent_tab.py:358-373 近乎逐字重复**（见⑥），是两个 tab 各自持份的拷贝。

## ④ 数据流

配置的流动是**拉式快照**而非推式绑定：用户改控件时 Gradio 只更新前端状态；点 Run 后，处理器把 `all_managed_components` 全量组件值打包成 `{组件对象: 值}` 字典传入，再按 ID 反查取值。MCP 数据流是唯一例外——它在本页就有即时处理：上传 JSON 文件 → `update_mcp_server` 校验存在性与 `.json` 后缀（agent_settings_tab.py:36-38）→ 读文件、`json.dumps(indent=2)` 回填到可见文本框（agent_settings_tab.py:40-43）。真正生效要等到 Run 时：browser_use_agent_tab.py:350-355 对文本框内容 `json.loads`，交给 `CustomController.setup_mcp_client`（browser_use_agent_tab.py:429-433）。

## ⑤ 设计决策与取舍

- **全量快照 vs 逐控件绑定**：inputs 传所有组件而非显式列举，新增控件零接线成本；代价是处理器必须依赖 ID 注册纪律，拼错前缀只会拿到默认值而不报错。
- **模型下拉双态**：已知 provider 给固定 choices 且首项为默认值；未知 provider 给空 choices + `allow_custom_value=True`（agent_settings_tab.py:24），保住了对 config 没收录的新模型的可输入性。
- **ollama 特例内联**：num_ctx 只对 ollama 有意义，用 visible 联动而非单独 tab，避免界面分裂；run 侧同样只在 provider=="ollama" 时传 num_ctx（browser_use_agent_tab.py:420）。
- **API key 留空走 .env**：password 控件默认空串（agent_settings_tab.py:114-119），工厂层会用环境变量兜底——UI 不做密钥持久化，配合 save_config 时非交互控件被过滤的机制双重防泄漏。

## ⑥ 新人提示（坑/勘误）

1. **docstring 错位**：`update_wrapper` 的注释写着 "Wrapper for handle_pause_resume."（agent_settings_tab.py:261）——纯复制粘贴残留，实际包装的是 MCP 更新。同一残留也出现在 deep_research_agent_tab.py:424 与 browser_settings_tab.py:155。
2. **同一组件双输出**：`outputs=[mcp_server_config, mcp_server_config]`（agent_settings_tab.py:268）不是笔误——回调返回 `(json字符串, gr.update(visible=True))` 二元组，第一个槽设值、第二个槽设可见性。
3. **重复定义的不对称语义**：本页 `update_mcp_server` 换文件时会把 `bu_controller` 置 None（agent_settings_tab.py:31-34）强制下次重建；deep_research 版只 close 不置 None（deep_research_agent_tab.py:362-364），导致新 MCP 配置对已存在的 DR agent 不生效。
4. **DEFAULT_LLM 合法性无人校验**：若设成 config.model_names 没有的键，agent_settings_tab.py:73 直接 KeyError，页面构建崩溃。
5. **控件计数**：字典 22 项（含 2 个 MCP 控件），别被 hub 摘要的"20"误导。
