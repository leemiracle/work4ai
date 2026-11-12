# 08 examples 生态：可安装的活文档与脚手架

## 一、角色定位

examples/ 是 NAT 的"可执行文档"：692 个文件、30 余个顶层主题，每个示例不是教程片段而是带 pyproject、可 `uv pip install -e` 的独立包。三职合一：入门教程（getting_started）、框架适配样例（frameworks）、生产级参考（advanced_agents）。`README.md:88-90` 列出 Beginner 三入口，notebooks 从 Hello World（`README.md:74`）递进到 Multi-Agent（L79）。

## 二、内部结构

### 标准解剖：simple_calculator 五件套

- **pyproject.toml**：包名 `nat_simple_calculator`（`pyproject.toml:28`）；依赖是 `"nvidia-nat[langchain,test] == {version}"`（`pyproject.toml:37`），构建时注入框架当前版本；`[tool.uv.sources]` 指回仓库根 editable（`pyproject.toml:41`）；entry-point 声明插件入口（`pyproject.toml:43`）。
- **configs/config.yml**：四段式——function_groups（`config.yml:17`）、functions（`config.yml:21`）、llms（`config.yml:25`）、workflow `_type: react_agent`（`config.yml:34`）；同目录另有变体 config-reasoning.yml。
- **register.py**：`CalculatorToolConfig(FunctionGroupBaseConfig, name="calculator")`（`register.py:26`）声明配置类型，`@register_function_group`（`register.py:31`）挂注册表，五个异步工具经 `group.add_function` 注册（`register.py:86`）后 `yield group`（`register.py:92`）。
- **tests/**：`locate_example_config` 定位配置（`test_simple_calculator_workflow.py:32`）、`load_workflow`（L33）、`workflow.run()` + `runner.result(to_type=str)`（L37-38）、`@pytest.mark.integration` + `nvidia_api_key`（L44-45）。
- **README.md**：安装说明。

### 脚手架：nat workflow create 的模板

create_command（`workflow_commands.py:209`）从 templates 目录（`workflow_commands.py:237`）用 Jinja2（L260）渲染五个模板——workflow.py.j2/config.yml.j2/register.py.j2/pyproject.toml.j2/__init__.py.j2（任务书只列四个，实为五个），可选 `uv pip install -e`（L264）。模板与手写示例同构：`workflow.py.j2:14` 生成 `XxxConfig(FunctionBaseConfig, name=...)`、`workflow.py.j2:21` 生成 `@register_function(..., framework_wrappers=[...])`、`workflow.py.j2:50` 生成 `yield FunctionInfo.from_fn(...)`；`config.yml.j2:16` 同款 react_agent 骨架；`pyproject.toml.j2:24` 同款 entry-point；`register.py.j2:4` 导入即触发注册；连字符转下划线见 `workflow_commands.py:270`。

### 家族地图

getting_started：simple_calculator（算术 ReAct）、simple_web_query（`config.yml:18` 的 webpage_query 配 react_agent `config.yml:40`）、scaffolding（`scaffolding/README.md:22`）。frameworks：adk_demo、agno_personal_finance、nat_autogen_demo、semantic_kernel_demo、strands_demo、haystack_deep_research_agent、auto_wrapper 及单仓混框架的 multi_frameworks——其 register.py 导入三个框架子模块（`multi_frameworks/register.py:28-30`），主类 `MultiFrameworksWorkflowConfig`（L43），以 `builder.get_tool(..., wrapper_type=LLMFrameworkEnum.LANGCHAIN)` 统一取用异构组件（L76）。advanced_agents：alert_triage_agent 带 live/offline 五套 config。专题：HITL、evaluation_and_profiling（simple_calculator_eval 八个 eval config，如 `config-trajectory-eval.yml:26` 的 phoenix）、control_flow、MCP、deploy、dynamo_integration、safety_and_security。

## 三、外部连接

- **entry-points 插件机制**：示例装好后，运行时 `loader.py:140` 的 discover_entrypoints 收集 `nat.plugins`/`nat.components` 入口并 import 各 register 模块，装饰器 `register_function`（`register_workflow.py:172`）登记进 GlobalTypeRegistry——示例与核心组件走同一发现路径。
- **示例互相依赖**：simple_calculator_hitl 依赖 `nat_simple_calculator` 与 `nat_por_to_jiratickets`（`simple_calculator_hitl/pyproject.toml:38-39`），uv.sources 指向两个兄弟目录（L44-45）；其 config 引用的 `hitl_approval_tool`（`config-hitl.yml:23`，挂于 L45）由 por_to_jiratickets 提供（`hitl_approval_tool.py:32`），README 明言 "reusable plugin"（`simple_calculator_hitl/README.md:67`）。
- **中间件消费**：retail_agent 的顶层 middleware 节（`config-with-defenses.yml:50`）即中间件体系的 YAML 入口。
- **文档互引**：示例 README 反链 docs 安装指南，与 skills 文档互为索引。

## 四、一个示例包从零到跑通的生命周期

1. **生成**：`nat workflow create my-agent` 渲染五模板生成 src/my_agent/，`--install` 即装。
2. **安装注册**：安装只做一件事——把 `my_agent.register` 写进 nat.components entry-point（模板 `pyproject.toml.j2:24` 与手写包 `pyproject.toml:43` 同构）。
3. **发现**：`nat` 命令启动时 loader 扫 entry-points（`loader.py:140`）并 import register 模块；`register.py.j2:4` 的导入随即触发 `@register_function`（`register_workflow.py:172`），配置类型进注册表。
4. **装配**：`load_workflow("configs/config.yml")` 解析四段式，每个 `_type` 查表实例化；workflow 段（`config.yml:34`）把 llm 与工具装配成 react_agent，函数被 builder 包装（含中间件链）。
5. **运行**：`workflow.run(input)`（`test_simple_calculator_workflow.py:37`）返回 runner，`runner.result(to_type=str)` 拿输出（L38）；集成测试以 nvidia_api_key fixture 断言（L44-45）。
6. **演化**：复制 config 变体、叠 eval、或被下游示例当插件依赖（HITL 链）。

## 五、设计决策

1. **示例即包**：editable + entry-points，示例是装完即可被框架发现的真组件——学习路径与扩展机制二合一，代价是维护 pyproject 与版本耦合。
2. **`{version}` 动态依赖**（`pyproject.toml:37`）：示例版本随框架走，防 API 漂移；版本取自 git 描述（`pyproject.toml:20`）。
3. **脚手架保结构一致**：五模板强制新包与手写示例同构（对照 `workflow.py.j2:14` 与 `register.py:26`），结构正确从约定变成机制。
4. **示例间依赖显式化**：hitl_approval_tool 复用走 pyproject 依赖而非复制代码，插件化在示例层即被示范。
5. **wrapper 统一化**：异构组件经 wrapper_type 统一取用（`multi_frameworks/register.py:76`）。
6. **eval 与示例共生**：同一工具包叠八个 eval config（`config-trajectory-eval.yml:26` 换 phoenix 后端），先可评测再优化。
7. **分级即导航**：README 以 Beginner/Intermediate/Advanced 标注（`README.md:105`）。

## 六、新人提示

- 跑通顺序：`nat workflow create` 生成并安装 → 改 config.yml 工具与 llm → 跑 integration 测试；勿手抄结构，模板已保一致。
- 改 `_type` 前确认组件已装（`_type` 是注册表键）；示例缺工具先看其 pyproject 依赖了哪些兄弟示例（HITL 链最常见）。- multi_frameworks 是理解框架中立的最佳入口：三框架子模块被一个 LangChain 工作流统一编排（`multi_frameworks/register.py:28` 与 L76 对照读）。
- 写 eval 从 config-trajectory-eval.yml 复制起步（`config-trajectory-eval.yml:26`）。
- 示例 uv.sources 指向仓库根（`pyproject.toml:41`），仓外复用需改此路径。
