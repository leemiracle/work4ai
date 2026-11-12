# web-ui 新人上手文档（ONBOARDING）

> 基于图谱（117 节点/12 层/15 步 tour，commit 61962296）撰写，关键结论经源码核实，锚 `file:line`。

## 1. 项目一句话定位

web-ui 是 browser-use 官方 **Gradio 网页控制台**：把 browser-use 框架（requirements.txt:1 锁 `browser-use==0.1.48`）的浏览器 agent 能力包装成网页应用——网页里配置 LLM 与浏览器、下发任务、观看回放。三大特性：多 LLM 支持（README.md:14）、自有浏览器免重登录（README.md:18）、跨任务持久会话（README.md:20）。与主框架是**纯消费关系**：28 个 py 文件不含任何 DOM 提取/推理实现，全部继承 browser-use 类（`CustomBrowser(Browser)`、`BrowserUseAgent(Agent)`），只做封装配置、注册扩展动作、搭界面；另附 DeepResearchAgent 研究产品线（src/agent/deep_research/deep_research_agent.py:982）。

## 2. 总体架构（12 层压缩为五段）

- **配置基座（L01）**：requirements.txt、.env.example（42 个环境变量，grep 实测，覆盖 14 家 LLM 密钥+浏览器/VNC）、.dockerignore:1-5（排除 data/tmp/results/.env，防密钥入镜像）。
- **包骨架与共享服务（L02-03）**：7 个空 `__init__.py` 划出五子包；utils 四模块为共享层——config.py:15 静态 `model_names`、llm_provider.py 唯一 LLM 工厂、mcp_client.py 做 Schema→pydantic 重建、utils.py:12,20 图片编码与产物发现。
- **执行与智能（L04-05）**：src/browser+src/controller 是 agent 的眼和手；src/agent 下双引擎——BrowserUseAgent 与 DeepResearchAgent。
- **界面（L06-08）**：WebuiManager 状态中枢（src/webui/webui_manager.py:22）→ 五 Tab 组件 → interface.py:22-95 `create_ui` 总装 → webui.py:9-11 启动（默认 7788）。
- **部署与外围（L09-12）**：Docker 三件套、CI 多架构发布、tests 手动冒烟、README/SECURITY。

## 3. 核心链路：webui.py 到可视化回放

1. **启动**：webui.py:1-2 `load_dotenv()`；:14-15 `create_ui().queue().launch()`。
2. **总装**：interface.py:60 `gr.Blocks` 装五 Tab，theme_map 八主题（:10-18）。
3. **下发**：`run_button.click(submit_wrapper, inputs=all_managed_components)`（browser_use_agent_tab.py:1070）——**全部注册组件**作入参，即设置值被运行时读取的机制。
4. **组装**：`run_agent_task`（browser_use_agent_tab.py:275）取值后实例化 LLM+CustomBrowser+CustomController+BrowserUseAgent，`asyncio.create_task` 后台执行（:559）并流式推送输出/截图/GIF。
5. **主循环**：BrowserUseAgent.run（browser_use_agent.py:48）逐步 `self.step`，检查暂停/停止/连续失败（:78-95），结束落 Playwright 脚本（:144-157）与 GIF（:164-169）。
6. **分发**：CustomController.act（custom_controller.py:110）——`mcp` 前缀动作直接 `ainvoke`（:126-130），其余走父类 registry。
7. **求助回路**：`ask_for_assistant`（custom_controller.py:60-71）→ `bu_response_event`（browser_use_agent_tab.py:242,635）→ 等用户作答后继续。

## 4. 关键模块深读

- **browser_use 封装**：`_set_tool_calling_method`（browser_use_agent.py:31-45）按模型库选协议——无工具支持模型走 `raw`、ChatOpenAI/Azure 走 `function_calling`、Gemini 走 None；run 用 SignalHandler 实现 Ctrl+C 暂停/恢复（:57-66）。重试与脱敏在 browser-use 包内，本仓重写点是信号处理与产物落盘。
- **deep_research**：1261 行自包含。StateGraph 三节点 `plan_research/execute_research/synthesize_report`（deep_research_agent.py:1055-1057）；`asyncio.Semaphore` 限流并行开多浏览器（:222）；`_load_previous_state`（:339）+恢复 plan（:1153-1155）支持断点续跑；`_stop_lingering_browsers`（:1226）清残留实例。
- **mcp_client 工具层**：`setup_mcp_client_and_tools`（mcp_client.py:17-43）兼容顶层 `mcpServers` 包裹（:35-36）；`create_tool_param_model`（:46-131）把工具 JSON Schema 递归转 pydantic 模型，`resolve_type`（:134-254）覆盖 enum/嵌套对象/联合类型；无 schema 按 `_run` 签名兜底（:101-125）。
- **llm_provider 抽象**：`get_llm_model`（llm_provider.py:152）先校验 `{PROVIDER}_API_KEY`（ollama/bedrock 豁免，:159-167），再按 14 个显式分支构造 LangChain Chat 实例（:168-338）；DeepSeek-R1 双子类——OpenAI 版绕过 LangChain 直连提取 reasoning_content（:55-114）、Ollama 版切 `<think>`（:117-149）。
- **五 Tab**：agent_settings_tab（双 LLM 参数组+MCP 上载，:213-237 注册 22 组件）、browser_settings_tab（14 控件，:134-151）、browser_use_agent_tab（:1025-1040）、deep_research_agent_tab（:406-420）、load_save_config_tab。

## 5. 数据流与制品

产物全落 `./tmp/`，无数据库：

- **UI 设置**：save_config 把非 Button/File 组件写为时间戳 JSON 落 `./tmp/webui_settings`（webui_manager.py:80-95）。
- **browser-use 四类产物**：录屏 `.webm`/trace/历史/下载默认落 `./tmp/` 子目录（browser_settings_tab.py:107-133）；GIF 固定名（browser_use_agent.py:165）；utils.py:20 找最新 `.webm/.zip` 供回放。
- **deep research 三件**：任务子目录下 `research_plan.md`+`search_info.json`（deep_research_agent.py:43-44）+报告（:450-455）；UI 每秒轮询 plan 增量刷报告（deep_research_agent_tab.py:190）。
- **生命周期**：tmp/data/results 均在 .dockerignore:1-3，容器重启即失；密钥只在 .env 与环境变量。

## 6. 设计决策与取舍

- **pydantic v1/v2 同名覆盖**（mcp_client.py:11-12）：`from pydantic import BaseModel, Field, create_model` 后紧跟 `from pydantic.v1 import BaseModel, Field` 覆盖前两者。动机：browser-use 0.1.48 的 ActionModel 是 v1 系（:8），`create_model(__base__=ActionModel)` 与 Field（:92）必须配 v1 才能注册进动作表，create_model 两版同名侥幸复用。**误"清理"此导入会把 v1 悄悄变 v2 致注册失败**。
- **startswith("mcp") 分发**（custom_controller.py:126）：注册名统一 `mcp.{server_name}.{tool.name}`（:167），分发仅凭前缀字符串判断——简单但自定义动作以 mcp 开头会被误路由。
- **update_mcp_server 双 Tab 重复**：agent_settings_tab.py:27（关 bu_controller）与 deep_research_agent_tab.py:358（关 dr_agent）两份近似实现，仅差异关哪个连接；复制而非抽象，隔离两条产品线。
- **namespace package**：src/agent/browser_use 与 src/agent/deep_research **无** `__init__.py`（ls 实证），靠 Python 3 隐式命名空间包；仓根启动可 import，setuptools find_packages 抓不到。
- **组件全量入参**：run 按钮 inputs 传全部组件（browser_use_agent_tab.py:1070），省去依赖表维护，代价是 Tab 改动波及取值链路。

## 7. 上手路径（tour 15 步首日路线）

1. **门面**（step-01）：README 三特性+安装路径；webui.py 19 行。
2. **配置**（02）：.env.example 42 变量对照 config.py:15。
3. **骨架**（03）：五子包地图，agent 下两目录是 namespace package。
4. **工厂**（04）：llm_provider.py:152 全分支。
5. **浏览器**（05）：custom_browser.py:66-76 参数组装、:78-82 端口冲突检测。
6. **控制器**（06）：custom_controller.py:54-107 自定义动作+Schema 重建，tests/test_controller.py 验回路。
7. **双引擎**（07/08）：browser_use_agent.py:48 主循环；deep_research_agent.py:1050-1080 图编译。
8. **中枢与 Tab**（09-11）：webui_manager.py:30-51 双实例池；browser_settings_tab.py:158-161 开关变更即关浏览器；browser_use_agent_tab.py:275 全生命周期。
9. **总装**（12）：interface.py:22-95，新增 Tab 从此接入。
10. **容器**（13）：Dockerfile:1 基镜像、:4 TARGETPLATFORM、:70-71 装依赖、:87 四端口；supervisord.conf priority 100→400。
11. **CI/验证**（14/15）：build.yml 两阶段 build/merge；tests/test_llm_api.py 冒烟。
12. **动手**：改 agent_settings 默认值→save/load 往返验证最小闭环。

## 8. 常见坑与勘误

**坑**：
- `from distutils.util import strtobool`（browser_settings_tab.py:2，用于 :55,61）——PEP 632 已废弃，Python 3.12+ ImportError。
- 死代码：custom_controller.py:1 与 custom_browser.py:2 各有未用的 `import pdb`；custom_browser.py:13-14 与 :24 重复导入。
- **源码自曝的组件 ID 错位**：deep_research_agent_tab.py:66 注释 `# Note: component ID seems misnamed in original code`，实例在 :398——变量 `max_query` 的 label 实为 "Research Save Dir"，按 ID 语义查代码必被误导。
- **stop 死引用**：deep_research_agent_tab.py:351 引用 `deep_research_agent.max_iteration`，但 :406-417 注册字典无此 ID，无任务时点 Stop 抛 KeyError。
- tests/ 四文件 0 个 assert（grep 实证），是冒烟脚本非自动化测试。

**勘误（图谱 summary 与源码不符，以源码为准）**：
1. 图谱称 custom_browser "探测代理连通性决定移除 --no-sandbox"——实际 :78-82 是探测 **CDP 调试端口**占用并移除 `--remote-debugging-port`；Docker 参数由 `IN_DOCKER` 经 CHROME_DOCKER_ARGS 决定（:69），无代理探测。
2. 图谱/任务书称动作分发在 custom_controller.py **L127**——`startswith("mcp")` 实际在 **L126**，L127 是注释行。
3. 图谱称 agent_settings_tab 注册 20 控件——实际 :213-233 注册 22 个。
4. 图谱称 config.py 为 "15 家供应商"清单——llm_provider.py:168-338 实测 14 个显式分支，以代码为准。
