# browser-use 新人上手文档（ONBOARDING）

> 基于知识图谱（912 节点/1957 边/16 层/16 步 tour，commit `2cc71890`），结论均经源码核实。

## 1. 项目一句话定位

browser-use 是「LLM 自主控制浏览器」的事实标准框架（约 12 万 star，README.md:31）：LLM 循环读 DOM、决定动作，直到任务完成。技术路线为 **LLM + CDP 直控 Chromium**——底层只用 cdp-use 类型化 WebSocket 接口，不经 Playwright 封装（CLAUDE.md「CDP-Use」节）。

本仓（v0.13.14，pyproject.toml:5）是 browser-use 组织的**基座**：browser-harness（CLI 3.0 引擎，pyproject.toml:50）、jev-ultrafast、web-ui、workflow-use 等子仓都构建在其 Agent/BrowserSession API 上。产品三路径：Cloud 托管（闭源，见 CLOUD.md）、CLI、Python 库；CLI 四别名全指向 `browser_use.cli:main`（pyproject.toml:105-109）。

## 2. 总体架构：16 层分层叙事

图谱 16 层的纵贯线：**镜像链→llm→browser→actor→dom→tools→agent→watchdogs→cli/mcp→skills→观测→外围**。

- **L01-02 基座与入口**：Docker 三层镜像链（Dockerfile.fast 把构建 2 分钟→30 秒）；包门面懒加载 `_LAZY_IMPORTS`（browser_use/__init__.py:76）。
- **L03-04 LLM**：base.py 的 `BaseChatModel` Protocol + **16 家供应商适配**（llm/__init__.py 导出 17 个 Chat 类含基类）；openai/serializer.py 被四家网关复用。
- **L05-07 浏览器**：BrowserSession（browser/session.py，4197 行）持 cdp_use CDPClient；watchdogs/ **14 个看门狗**；actor/ 类 Playwright 三件套（Page→Element→Mouse）。
- **L08-11 感知动作与 Agent**：dom/ 把 DOMSnapshot 转带索引元素树；tools/registry 把任意函数规范化为 kwargs-only 动作；agent/service.py（4188 行）主循环；system_prompts/ 八版模板。
- **L12-16 外围**：CLI 3.0+MCP 双通道、skills 云客户端、tokens/telemetry、sandbox/integrations/beta、十条 Actions 工作流。

最重要的主线是**事件驱动**：BrowserSession 持 bubus `EventBus`（session.py:556），events.py 定义 45 个事件类，看门狗全挂总线按事件名分发。

## 3. 核心链路：Agent 主循环 × DOM 快照 × Controller

Agent 一步的生命周期：

1. **取感知**：DomService（dom/service.py:45）→ enhanced_snapshot.py 无状态解析（`_SENSITIVE_INPUT_TYPES`:48 识别敏感输入）→ DOMTreeSerializer（serializer/serializer.py，1406 行）产出索引元素树，入口 `get_serialized_dom_tree`（dom/service.py:1111）。
2. **渲染消息**：prompts.py 的 `AgentMessagePrompt` 渲染状态/文件系统/历史；MessageManager（message_manager/service.py:104）维护历史，`maybe_compact_messages`（:216）超长压缩。
3. **调 LLM**：`llm.ainvoke`（agent/service.py:1953），结构化输出解析为动作列表。
4. **执行**：`multi_act`（agent/service.py:1217）逐个走 `act()`（tools/service.py:2178）统一分发，动作经事件总线派到看门狗（default_action_watchdog 承担 33 个默认动作）。
5. **循环**：`take_step`（agent/service.py:2272）/`_execute_step`（:2456）驱动；预算 75% 注 BUDGET WARNING（:1555），末步强制只剩 done（:1569）。

配套：启动/重连后 `attach_all_watchdogs()`（session.py:814/:1706）挂全部看门狗；`_cdp_timeout.py` 治云浏览器假死（60s 上限）。

## 4. 关键模块深读

**agent/service.py（4188 行编排中枢）**：每步串「感知→渲染→LLM→执行→上报」，挂载 skills/judge 评审/variable_detector/gif/cloud_events；结果面 `AgentHistoryList`（views.py，33 方法），输出 schema 工厂支持任意 Pydantic 模型。

**browser/session.py+watchdog**：profile.py:585 `BrowserProfile` 多重继承四类 Playwright kwargs 基类聚合启动选项；watchdog_base 按 `on_EventName` 约定自动发现 handler，内建 CDP 断连熔断。

**prompts.py 五开关**（`_load_prompt_template`:72-84）：五个布尔开关组合出八版。**词序相反双模板**：`system_prompt_anthropic_flash.md`（247 行）给 Anthropic 4.5——prompt caching 要求前缀 ≥4096 token，长文反而省钱；`system_prompt_flash_anthropic.md`（31 行）给其余 Anthropic flash 模式。

**llm 适配**：anthropic 校验 thinking、失败从纯文本兜底恢复 JSON；google 修 Gemini schema；aws 转图片 base64；groq 从报错体抢救 JSON；browser_use 云端为零依赖自研客户端。

**beta/service.py（6810 行）**：`find_browser_use_terminal_binary`（:187）定位 Rust 版终端二进制（安装提示 :91）——Rust 终端 SDK 的 Python 桥。

**tools/registry/service.py**：`_get_special_param_types`（:57）按名注入 `browser_session`（:65）/`file_system`（:71），其余参数从类型注解生成 Pydantic 模型（规范化 :75）。tools/service.py 注册默认动作（navigate:507 等）——views.py 动作字段的 description 就是写给 LLM 的说明书。

## 5. 数据流与制品

**消息历史**：MessageManager 分 `system`/`state` 两槽（`_set_message_with_type`:556），每步重建 state 消息保证新鲜；`_filter_sensitive_data`（:577）送 LLM 前脱敏。**AgentHistoryList**（agent/views.py，33 方法）：final_result/errors/urls/extracted_content 聚合，也是 judge 输入。**计费三源**（tokens/service.py）：LiteLLM 价格表（:54，缓存 1 天）+ custom_pricing.py + OpenRouter 实时价（:22）；llm/views.py 统一 8 家 token 口径。**遥测**：telemetry 匿名上报（config.py:58 默认开）；observability 接 Laminar。**文件系统**：filesystem/file_system.py 是持久记忆——长任务用 todo.md 追踪、results.md 累积、PDF 自动下载供 read_file。

## 6. 设计决策与取舍

- **懒加载门面防导入开销**：`_LAZY_IMPORTS`+PEP 562 `__getattr__`+TYPE_CHECKING 块（__init__.py:76/118）——Chat 类全家桶不拖累 CLI 冷启动。
- **Controller=tools.service 别名 shim**：controller/__init__.py 全文仅一行 `from browser_use.tools.service import Controller`——动作体系迁入 tools/ 后的兼容层。
- **词序双模板的成本工程**：对 Anthropic 4.5 用长文命中 4096 token 缓存门槛（省缓存费），其余模型用精简版（省 token 费）。
- **延迟 import 防循环依赖**：EventBus 把 session/watchdog/agent 连成环，cli.py:42/160/186 等函数内 import 破环。
- **无状态快照换一致性**：每步重解析 DOMSnapshot（不维护易漂移的可变树），`*[` 标记「新元素」还增量给 LLM。
- **MCP 工具一视同仁**：mcp/client.py 把外部 MCP 工具注册为普通动作，主循环不感知来源。

## 7. 上手路径：按 tour 16 步的首日路线

1. **鸟瞰（Step 1-3）**：README → pyproject 四入口 → `__init__.py` 懒加载门面 → service.py/views.py 组织纪律 → config.py 双轨配置。
2. **LLM（Step 4-5）**：base.py → messages.py（cache 字段服务 Anthropic 缓存）→ schema.py 的 SchemaOptimizer（$defs 展开、全字段 required）→ openai/ 基准 → anthropic、google 看差异。
3. **浏览器（Step 6-8）**：events.py 当字典查 → session.py（启动/attach_all_watchdogs:1706/事件分发）→ 精读 dom/security/default_action 三看门狗。
4. **感知与动作（Step 9-11）**：actor/README.md（251 行契约）→ enhanced_snapshot → serializer → registry → act():2178。
5. **Agent（Step 12-13）**：主循环锚点（1953/1217/2272/2456）→ message_manager → system_prompts/ 对比读（基版 270 行 vs 微调版 18 行）。
6. **外围（Step 14-16）**：cli.py `_dispatch`:357 与 `_LEGACY_HINTS`:206 → mcp/server.py（16 个 browser_* 工具，实测）→ skills/ → tokens/sandbox。

环境：`uv venv --python 3.11 && uv sync`；测试 `uv run pytest -vxs tests/ci`。仓规：tab 缩进、pydantic v2、不 mock（LLM 除外）。

## 8. 常见坑与勘误

五条均源码实证（前四条纠正仓库自带文档）：

1. **CLAUDE.md 提示词路径写错**：CLAUDE.md「File Organization」节写 `browser_use/agent/system_prompt*.md`，实际是复数目录 `browser_use/agent/system_prompts/`（八个 md），单数 glob 匹配不到。
2. **skills/service.py 非本地技能消费端**：是 **Browser Use 云 API 市场客户端**——`SkillService`（skills/service.py:19）经 `browser_use_sdk.AsyncBrowserUse` 拉取/执行云端技能，构造强制 `BROWSER_USE_API_KEY`（:30-33）。本地给 AI 看的技能文档在仓库根 `skills/` 目录，两回事。
3. **subagent.md 是 CLI 2.x 命令面，与 3.0 代差**：skills/cloud/references/guides/subagent.md:50-60 教 `browser-use cloud login` / `browser-use cloud v2`，但 3.0 里 `cloud` 已进 `_LEGACY_HINTS`（cli.py:218），新答案 `browser-use auth login`+`start_remote_daemon()`；`browser-use --mcp` 仍有效。
4. **OldConfig 的「配置项」是 @property 非 pydantic 字段**：config.py:47 的 `BROWSER_USE_LOGGING_LEVEL`（:53-55）等全是 @property 读 env；用 pydantic `Field` 的是 `FlatEnvConfig`（config.py:201-205）。用户拿到的 `CONFIG`（config.py:366）是 `__getattr__` 动态代理，每次访问重读 env——当普通 pydantic 对象做 `model_dump()` 会失败。
5. **sandbox 的 import 是「假」的**：sandbox/sandbox.py 用 `inspect.getsource` 剥装饰器取源码（:50），ast 只挑函数体引用的顶层 import（:65），以**文本形式**拼进自包含代码字符串（:295-297），连同 cloudpickle 上下文经 SSE 投云端执行——生成代码里的 import 只是文本头，静态分析工具不可见。

另：图谱称 events.py 有 46 个事件类，实测 45（BaseEvent 来自 bubus，events.py:7）。
