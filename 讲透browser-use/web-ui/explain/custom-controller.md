# custom_controller.py 精讲——CustomController：动作分发与 MCP 工具的并轨点

> 源码：`/usr-data/data2/repos/browser-use/web-ui/src/controller/custom_controller.py`（182 行）
> 图谱层位：L04 浏览览器与动作控制器

## ① 角色定位

`CustomController` 继承上游 `browser_use` 的 `Controller`（custom_controller.py:39），是 agent"手"的本地定制层。上游 Controller 已经注册了二十来个标准浏览器动作（click、input_text、goto、scroll、switch_tab、done……），本类只做三件增量的事：

1. **新增两个自定义动作**——`ask_for_assistant`（向人类求援，custom_controller.py:54-71）和 `upload_file`（带白名单的文件上传，custom_controller.py:73-107）；
2. **改写动作执行入口 `act()`**（custom_controller.py:109-152）——在标准分发表里劈出一个"MCP 旁路"，让 LLM 生成的 `mcp.xxx.yyy` 动作名不走 `registry.execute_action`，而是直接调用 LangChain 工具的 `ainvoke`；
3. **管理 MCP 客户端生命周期**（custom_controller.py:154-182）——连接 MCP 服务器、把远端工具登记进本地动作注册表、退出时手工关闭。

它是全仓"浏览器原生动作"与"MCP 外部工具"两条能力线的**汇合点**，也是理解 web-ui 如何扩展 browser-use 动作面的最短路径。

## ② 内部结构

**构造（custom_controller.py:40-49）**：`__init__` 接三个参数——`exclude_actions`（排除上游动作，默认空）、`output_model`（结构化输出模型）、`ask_assistant_callback`（人类应答回调，同步或异步皆可）。随后立即 `self._register_custom_actions()`（custom_controller.py:46）注册自定义动作，并把 `self.mcp_client`、`self.mcp_server_config` 初始化为 `None`（custom_controller.py:48-49）——MCP 是可选晚绑定的，这一点决定了同一份 controller 可以在无 MCP 配置下正常工作。

**动作注册 `_register_custom_actions`（custom_controller.py:51-107）**：用 `@self.registry.action(描述文本)` 装饰器把内嵌函数登记进注册表，参数签名（含类型注解）会被上游自动转成 param_model 供 LLM 参考。

- `ask_for_assistant`（custom_controller.py:60-71）：动作描述写得很讲究（custom_controller.py:55-59）——要求 agent 优先自主完成，只在"缺凭据、需主观判断、需物理操作、复杂验证码"等确定性阻碍时才求助。回调统一在这里做同步/异步双态分发（`inspect.iscoroutinefunction`，custom_controller.py:62-65）；若 UI 没接回调，返回固定话术 "Human cannot help you. Please try another way."（custom_controller.py:70-71），逼模型换路径而不是死等。
- `upload_file`（custom_controller.py:76-107）：双闸门——路径必须在 `available_file_paths` 白名单内（custom_controller.py:77-78）且真实存在（custom_controller.py:80-81）；然后按 index 取 DOM 元素 → 判定是文件上传控件（custom_controller.py:85-87）→ 定位 Playwright 句柄 → `set_input_files`（custom_controller.py:100）。白名单来自 UI 的文件选择，是防 LLM 幻觉路径的关键设计。

**动作分发 `act`（custom_controller.py:109-152）**：核心逻辑压在 L124-140。`action.model_dump(exclude_unset=True)` 把 LLM 本步输出的动作模型展开成 `{action_name: params}`（custom_controller.py:124），随后逐项判断：

```python
if action_name.startswith("mcp"):                 # custom_controller.py:126
    mcp_tool = self.registry.registry.actions.get(action_name).function
    result = await mcp_tool.ainvoke(params)        # custom_controller.py:130
else:
    result = await self.registry.execute_action(   # custom_controller.py:132-140
        action_name, params, browser=browser_context, ...)
```

钉版勘误：`startswith("mcp")` 的判定在 **custom_controller.py:126**（不是某些资料写的 L127）。MCP 分支绕过了 `execute_action` 的整套注入机制（browser/page_extraction_llm/sensitive_data/context 都不传，custom_controller.py:130 的 `ainvoke` 只收 params），因为 LangChain 工具不认识 browser-use 的依赖注入协议——`register_mcp_tools` 在登记时用 `functools` 级闭包（`setup_mcp_client_and_tools` 返回的 client）已把依赖封在工具内部。结果归一化在 custom_controller.py:142-149：str → `extracted_content`；`ActionResult` 原样透传；None → 空结果；其他类型直接抛 `ValueError`。

**MCP 生命周期（custom_controller.py:154-182）**：`setup_mcp_client` 存配置 → 建客户端 → `register_mcp_tools`（custom_controller.py:154-158）。`register_mcp_tools` 遍历 `server_name_to_tools`，把每个工具命名为 `mcp.{server_name}.{tool.name}`（custom_controller.py:167），然后**直接写进 `self.registry.registry.actions` 字典**（custom_controller.py:168-173）——不走 `registry.action()` 装饰器，因此没有 domain 过滤器、没有自动 param_model 推断，`param_model` 由 `create_tool_param_model(tool)` 现场从工具 schema 合成。`close_mcp_client` 手工调 `__aexit__(None, None, None)`（custom_controller.py:182），因为这个 MCP client 从不走 `async with` 上下文。

## ③ 外部连接

**上游**：`Controller/Registry/RegisteredAction` 与十来个标准动作视图类从 `browser_use.controller.*` 导入（custom_controller.py:8-22）。`act()` 的签名（browser_context、page_extraction_llm、sensitive_data、available_file_paths、context 五个注入位，custom_controller.py:110-120）必须与上游 Agent 调用约定逐字对齐——基类 `Agent.step()` 每步都按这套关键字调它。

**MCP 侧**：从 `src.utils.mcp_client` 导入 `create_tool_param_model` 和 `setup_mcp_client_and_tools`（custom_controller.py:30）——前者把 LangChain 工具的 JSON schema 转成 pydantic 动作参数模型，后者初始化 `MultiServerMCPClient` 并连服务器。

**UI 侧消费者**：`browser_use_agent_tab.py:430-432`——`CustomController(ask_assistant_callback=ask_callback_wrapper)` 之后立刻 `await setup_mcp_client(mcp_server_config)`，其中 mcp_server_config 来自 Agent Settings 的 MCP json 文件/文本框（`update_mcp_server`，agent_settings_tab.py:27 一带）。controller 实例缓存在 `webui_manager.bu_controller`，跨任务复用，只有进程重启才重建。

**Deep Research 链**：deep_research_agent.py:118 构造 `CustomController()` 时不传 MCP 配置也不传回调——深研究的子任务没有 MCP 工具、求助动作会返回"人类帮不了你"。

## ④ 数据流

一步动作的完整数据流：

```
Agent.step()（上游基类）
  → LLM 输出动作 JSON → 解析为 ActionModel
  → controller.act(action, browser_context=..., sensitive_data=..., ...)
                                          custom_controller.py:109
  → model_dump(exclude_unset=True)        :124
  → 动作名分流
     ├─ "mcp.srv.tool" 前缀命中            :126
     │    → registry.actions[name].function（LangChain 工具）
     │    → await tool.ainvoke(params)     :130 → MCP 服务器执行
     └─ 标准动作                           :132-140
          → registry.execute_action（注入 browser/敏感数据映射/白名单）
  → 结果归一化 ActionResult                :142-149
  → 回到 Agent：写入 step history / 消息管理器
```

MCP 工具的登记流（反向）：UI 上传 MCP json → `setup_mcp_client(config)`（custom_controller.py:154）→ `MultiServerMCPClient` 连接并拉取工具清单 → `register_mcp_tools`（custom_controller.py:160）→ 每个工具以 `mcp.{server}.{tool}` 之名连同 `create_tool_param_model` 合成的参数模型进注册表（custom_controller.py:168-173）→ 下一轮 Agent 构造 prompt 时这些动作连同参数描述一并暴露给 LLM。

## ⑤ 设计决策与取舍

**为什么用字符串前缀而不是类型标签区分 MCP？** `act()` 只有 `action_name` 一个可靠信号——ActionModel 是上游动态拼装的联合模型，动作注册表本身不区分来源（custom_controller.py:168 直接把 MCP 工具塞进同一个 dict）。于是"名字以 mcp 开头"成了唯一低成本的判别式。代价有两个：①理论上若有人注册一个本机动作且名字以 mcp 开头会被误路由，命名约定 `mcp.` 前缀（带点）是软保障；②MCP 分支拿不到 browser 注入，MCP 工具永远无法操作当前浏览器会话——这是能力边界而非 bug。

**`registry.actions` 直写 vs 装饰器注册**。标准做法是 `registry.action(...)`；直写字典（custom_controller.py:168）省去了装饰器对函数签名的解析（LangChain BaseTool 不是裸函数，装饰器无法推断参数模型），代价是绕过了 domain 过滤机制——所有 MCP 工具在所有页面可用。对通用 MCP 工具（查天气、查数据库）这无所谓，但若挂上文件系统类 MCP server，等于给 LLM 全量文件能力，部署时要心里有数。

**`ask_for_assistant` 的描述即护栏**。这个动作的行为约束几乎完全写在 description 文本里（custom_controller.py:55-59），代码只做转发。这是 prompt-as-spec 的典型：约束不硬编码，靠 LLM 遵守描述。好处是灵活，坏处是模型不读描述时可能滥用求助。

**L151-152 的 `except Exception as e: raise e` 是无操作透传**——捕获后原样抛出，既没恢复也没 enrich。实际等于没有 try/except。上游基类版本（0.1.48 service 同名方法）会包装错误信息，本类这样做等于把异常处理权完全上交 `Agent.step()` 的失败计数器（browser_use_agent.py:83 的 `consecutive_failures`）。

## ⑥ 新人提示（坑与勘误）

1. **`startswith("mcp")` 在 custom_controller.py:126**（钉版勘误：不是 L127）。引用这处分流逻辑时以 126 为准；同一判定块内 `ainvoke` 在 L130、`execute_action` 在 L132。
2. **一批死导入**：`pyperclip`（custom_controller.py:3）、`MainContentExtractor`（custom_controller.py:10）、以及 `browser_use.controller.views` 里整整十个动作类（`ClickElementAction/DoneAction/ExtractPageContentAction/GoToUrlAction/InputTextAction/OpenTabAction/ScrollAction/SearchGoogleAction/SendKeysAction/SwitchTabAction`，custom_controller.py:11-22）在本文件体内**零使用**——它们是早期版本 controller 自己实现这些动作时的残留，现在全由上游 Controller 提供。`DoneAction` 还在 L8 与 L14 **重复导入两次**。读代码时别在这些导入上找功能。
3. **`import pdb`（custom_controller.py:1）是调试遗留**，不要模仿；同类遗留还有 llm_provider.py:2。
4. **MCP 动作没有浏览器上下文**：给 MCP server 写"操作当前页面"类工具是死路，`ainvoke(params)`（custom_controller.py:130）不传 browser；需要浏览器能力的动作必须注册成本地动作。
5. **controller 跨任务长存**（`webui_manager.bu_controller` 缓存）：改了 MCP json 后 UI 会重新 `setup_mcp_client`，但旧工具不会从注册表摘除（`register_mcp_tools` 只增不删，custom_controller.py:160-178），换 server 名可以并存，同 server 改工具清单则以新条目覆盖同名键——排查"改了配置没生效"时重启进程最干净。
6. **`close_mcp_client` 手工 `__aexit__`（custom_controller.py:182）**：这个 client 是 `setup_mcp_client_and_tools` 里 `await client.__aenter__()`（mcp_client.py:38）手工拉起的，不走 async with，所以收尾也必须手工——忘了调就会泄漏 MCP 连接进程。

一句话总结：`CustomController` 的全部存在感浓缩在 custom_controller.py:126 那一行前缀判断——它把上游动作注册表改造成"本地动作 + MCP 工具"的双轨分发面；读它时盯住 act() 分流与 register_mcp_tools 直写注册表这两处，其余（含十来个死导入）都是历史沉积。
