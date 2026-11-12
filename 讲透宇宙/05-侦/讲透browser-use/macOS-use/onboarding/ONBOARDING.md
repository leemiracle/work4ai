# macOS-use 新人上手文档（ONBOARDING）

> 图谱 154 节点/14 层/16 步 tour + 源码核实；锚均为 `file:line` 实证。

## 1. 项目一句话定位

**browser-use 官方的 macOS 桌面 agent 移植项目：LLM 经 Accessibility API 感知并操控任意 Mac 应用。** 包名钉在 `pyproject.toml:2-7`：`mlx-use` v0.0.3——仓库名（macOS-use）≠ 包名（mlx_use），一切 `mlx_use.*` 指后者。

诚实定位：**browser-use 的 macOS 移植中间态，上游残留未清理**。骨架（Agent 循环/Controller/Registry/MessageManager/telemetry）拷自上游；`README.md:119` 宣称基于 MLX 本地推理，但依赖无 mlx 包、examples 默认 Gemini——mlx 只是愿景词；release 即发 PyPI 而仓内唯一"测试"收集即崩（`publish.yml:11-13`）。安全先读 `README.md:147-148`：agent 会用真实凭据，**不会在验证码处停下**。

## 2. 总体架构（14 层）

- **L01-L02 配置与门面**：`pyproject.toml:29-35` 依赖（langchain 全家桶+pyobjc 桥+posthog+gradio）；`__init__.py:1-19`（:3 日志副作用；re-export 六符号=全部 API 面）；`logging_config.py:64/:68`（RESULT 级；环境变量名仍是上游的）。
- **L03 mac/ 底座**（真正新写）：element/tree/actions。**L04-L07 上游骨架**：动作注册→数据模型与提示词→消息管理→主循环。**L08 遥测**：PostHog，硬编码上游 key（第 8 节）。**L10-L14 外围**：gradio_app、examples、文档模板（指向上游）。
- **L09 断裂件专层**：`mac/context.py`、`mac/views.py`、`message_manager/tests.py`、仓根 `-`（9.4MB PNG 误提交）。改造前必读第 8 节。

## 3. 核心链路

**感知**：`MacUITreeBuilder`（`mac/tree.py:45`）以 pid 为根递归遍历 AX 树，交互元素编 `highlight_index` 入 `_element_cache`（:48/:198）——**动作按 index 寻址的唯一通道**。

**决策**：`get_next_action`（`agent/service.py:310-328`）以 `with_structured_output` 解析；`AgentOutput` 由 registry 动态生成 ActionModel 经 `type_with_custom_actions`（`agent/views.py:51`）注入——**自定义 action 自动进 LLM 输出 schema**。

**执行**：`Controller._register_default_actions`（`controller/service.py:37`）用 `@self.registry.action(...)` **内联七个闭包**：done/input_text/click_element/right_click_element/scroll_element/open_app/run_apple_script（:43-:227）；`multi_act`(:275-288) 顺序执行、遇 done/error 提前 break（:285）。注册侧从函数签名动态生成参数模型（`registry/service.py:45`）——**新增动作=类型注解 async 函数+一行装饰器**。

**主循环**：`run(max_steps=100)`（`agent/service.py:401-442`）→ `step()`(:193-260)：build_tree → 渲染状态 → LLM → `multi_act`（首步引导 open_app，:202-203）；失败超 max_failures(5) 停（:444-449）；终态：done / 失败超限 / 步数耗尽。

## 4. 关键模块深读

**agent/service.py（491 行心脏）**：① `include_attributes` 默认（:69-80）是 HTML 属性表，AX 语义错位（第 6 节）；② `generate_gif=True`（:68/:99）死配置，全仓零消费；③ 硬编码版本 0.0.1（:149-154）与 pyproject 0.0.3 打架。

**mac 底座**：element（:7）`_element` 直存 AXUIElement 引用（:21），状态文本由 `get_clickable_elements_string`(:77-110) 产出（:97 格式、:84 白名单、:147-148 path 消歧）；actions `click` **双必需参数**（:43）、`type_into`(:62) 直写 AXValue、`scroll`(:119) 方向映射。

**registry 与 controller**：`registry/views.py` RegisteredAction(:6)/ActionModel(:32)/ActionRegistry(:64，:69 拼动作清单进 system prompt)；`controller/views.py` 七动作参数模型，底部留注释掉的上游浏览器动作。**telemetry**：`views.py:9` 抽象基类+四类事件；`service.py:31-33` 硬编码常量是最大勘误源。**gradio_app/src/models/app.py**：`MacOSUseGradioApp`(:23) God-class——Controller、agent 异步生命周期、automations(:31)、preferences.json(:32-33)、`set_key` 写 .env（:9）。

## 5. 数据流与制品

初始三消息：system prompt+任务（`message_manager/service.py:57-60`）+ **AgentOutput 示例 tool_call**（:82/:87）。每步：状态+上步结果 → `add_state_message`(:95) → LLM → `_remove_last_state_message`(:123) 换 `add_model_output`(:127)——**状态消息临时插入、模型输出永久保留**。`cut_messages`(:191-231) 超 128000 先剥图片再按比例截末条，超 99% 抛错（:217-221）。

**LLM 现实：走 Gemini 而非仓名暗示的 MLX**——`examples/try.py:35-43` 探测链 GEMINI 优先；`examples/basic_agent.py:17` 直连 gemini-2.0-flash-exp；MLX 全仓零代码，仅存 README 愿景（:136）。制品：每步对话 txt（`agent/service.py:353-359`）、`AgentHistory.json`（:464-468）。

## 6. 设计决策与取舍

**① namespace package+sys.path hack**：gradio_app 全树 0 个 `__init__.py`；`src/models/app.py:18-19` `sys.path.append` 仓库根才能导入 mlx_use；requirements.txt 末行 `-e ..` 兜底。`gradio_app/app.py:10` 绝对导入，**须 `python -m gradio_app.app` 从根跑**。

**② GIF 未移植**：`generate_gif` 存而不用（`agent/service.py:68`），README 演示 GIF 无生成链路。

**③ include_attributes 双重失效**：语义错位（HTML 属性表 :69-80）之上，参数存进 `prompts.py:155` 后 **`get_user_message`(:158-175) 从未读取**（经 `message_manager/service.py:47/:117` 传入）——真正生效的是 element.py:84 白名单，改此参数零效果。

**④ find-replace 级移植痕迹**：`BROWSER_USE_LOGGING_LEVEL`（`logging_config.py:68`）、telemetry 缓存 `~/.cache/browser_use/`（`telemetry/service.py:31`）、docstring 仍写 "default browser actions"（`controller/service.py:38`）；目录学约定（service.py 超 500 行拆分）见 `mlx_use/README.md:13-26`。

## 7. 上手路径（tour 16 步+地雷图）

- **地基（tour1-4）**：README → .env.example 配 key → `__init__.py` 六符号 → `mlx_use/README.md` 目录学。
- **核心（tour5-11）**：element（看见）→ tree（遍历）→ actions（触摸，记住 :43 click 双参数）→ registry → controller → agent/views+prompts（`prompts.py:58` 元素格式与 :86-87 AppleScript 兜底是域知识最密处）→ message_manager → agent/service 主循环。入口 `python examples/try.py`（`README.md:64`）。
- **地雷图（tour13，改造前必读）——四断链件不可 import**：`mac/context.py`（:26 引用不存在类即崩；全仓无人导入）；`mac/views.py`（:6-7 `mlx_use.dom.*` 死导入即崩，内容仍是浏览器模型）；`message_manager/tests.py`（:9-10 同类死导入，收集即崩）；仓根 `-`。**`__init__.py` 导入链不经过任何断链件，包本体可正常 import**。
- **外围（tour12/14-16）**：examples 九入口全走 set_llm+Controller+Agent 脚手架；gradio_app 三 Tab。内地雷：`basic_agent.py:206` click 漏参；`calculate.py:30-31` set_llm 后者覆盖前者。

## 8. 常见坑与勘误（甄别清单）

1. **telemetry 硬编码上游 PostHog key，事件仍上报 browser-use 官方**：`telemetry/service.py:32` `phc_F8JMNjW1i2KbGUTaW1unnDdLSPCoyc52SGRU0JecaUh` 与上游仓逐字节相同（跨仓实证），HOST=eu.i.posthog.com（:33）。`.env.example:8` 虽默认 false，**装包即默认开**（:39 getenv 缺省 'true'）。
2. **click 三处 TypeError 级 bug**：签名双必需（`mac/actions.py:43`），但 `actions.py:117`、`context.py:158`、`basic_agent.py:206` 三处只传 element；主链路 `controller/service.py:91` 传参正确——核心循环不炸，炸的是边缘路径（right_click 回退/示例）。
3. **tests 全量不可运行**：`pytest.ini:7` testpaths 指向不存在的 tests/；唯一测试收集即 ModuleNotFoundError；CI 只 publish 不跑测试。
4. **mac/views.py 与 mac/context.py 纯上游残留**：前者仍是 BrowserState/TabInfo 浏览器模型；后者四重死引用（:26 不存在类、:29 引不存在的 manager.py、:100/:136 NSWorkspace 未导入、:185 空 `get_state` 覆盖 :121）。
5. **get_llm 无 alibaba 分支选必抛 ValueError**：`llm_models.py:12` 注册表有 `"alibaba"`，`get_llm`(:15-27) 只有三分支，选 alibaba 落 :25 抛错——UI 里看得到用不了。
6. **issue 模板指向上游**：`bug_report.yml:2`"Report a bug in browser-use"、`:44` 让跑 `uv pip show browser-use`；`config.yml:4/7/10` 引流上游文档与 Discord。
7. **仓根 `-` 是 9.4MB PNG 误提交**（git blob 8c1dc95）；`.gitattributes` 只管 static/*.gif。
8. **版本三处打架**：pyproject 0.0.3 vs 遥测硬编码 0.0.1（`agent/service.py:150`）vs README 安装命令（:28）。
9. **tree.py 拼接残留**：:1-4 内嵌 mac_use 旧包名文件的拼接头，两组 import 与两个 logger 并存——mac_use 是比 mlx_use 更早的包名。
10. **google_form.py 外发用户 prompt**：`google_form.py:8` 硬编码 Google Form 端点，prompt+终端输出 POST 出去（:18）。

### 勘误（图谱 vs 源码复核）

1. 图谱称 click 漏参为"TypeError 级 bug"，复核确认，但主链路 `controller/service.py:91` 传参正确，bug 仅影响边缘路径，影响面小于图谱表述。
2. 图谱称 tests.py "import 目标目录不存在"，精确死因是 :9-10 导入 `mlx_use.browser.*`/`mlx_use.dom.*` 两个不存在的模块。
3. 图谱对 include_attributes 仅记"语义错位"；复核发现 `get_user_message` 完全未消费该参数（`prompts.py:158-175`），双重死参数。
4. 图谱称仓根 `-` 为 9.4MB PNG——git blob 实测 9,445,300 字节确证；该文件在工作区未物化，仅存于 git 对象库。
