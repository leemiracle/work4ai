# mlx_use/controller/registry/service.py 精讲——动作注册表：装饰器到 LLM 工具契约的编译器

## 一、角色定位

`mlx_use/controller/registry/service.py`（142 行，配套数据模型 `registry/views.py` 71 行）实现了一个微型"工具编译器"：`Registry` 类把 Python 函数登记进动作表，并向三个方向转换——向 LLM 编译（函数签名→Pydantic 参数模型→汇总为可校验的 `ActionModel`）、向 prompt 编译（动作清单→自然语言说明）、向运行时分派（`execute_action` 查表调用）。它是 Controller 插件化动作体系的发动机：`controller/service.py` 的默认动作（done/input_text/click_element 等）全部经 `@action` 装饰器注册。

图谱 fanIn 1 / fanOut 10：唯一上游是 `Controller`（controller/service.py L5 导入）。

## 二、内部结构

**Registry.__init__（L23-28）**：三样家当——`ActionRegistry()` 空容器（views.py L64-71）、`ProductTelemetry()` 遥测单例、`exclude_actions` 排除清单。L28 的 `arguments_to_ignore = ['browser', 'mac_tree_builder', 'builder']` 是本文件最有味道的一行：三个"隐身"注入参数名里，`browser` 是上游残留（本仓没有 browser 对象），`mac_tree_builder` 是 macOS 移植新增的替代者，`builder` 是孤儿——三个名字叠在一起就是 fork 改名未净的地层剖面。

**_create_param_model（L30-43）**：无现成 `param_model` 时用 `inspect.signature` 自动生成参数模型：遍历形参，跳过 `arguments_to_ignore`，注解做类型、默认值做默认，`create_model(f'{函数名}_parameters', __base__=ActionModel, **params)` 合成。L38 留着上游的 `# TODO: make the types here work`——注解若为字符串形式会失败，本仓未触发。

**action 装饰器（L45-85）**：注册主流程四步——① 名字在 `exclude_actions` 里就原样返回不注册（L55-56）；② 取 `param_model` 或现场生成（L59）；③ **同步函数自动包装成异步**（L62-71）：`asyncio.to_thread(func, ...)` 扔进线程池，再把 `__signature__`（L68）、`__name__`、`__annotations__` 拷到包装上——不拷 signature，别处再解析签名只会看到 `*args, **kwargs`；④ 打包成 `RegisteredAction`（views.py L6-15 五字段）入表（L82）。装饰器**返回原函数而非包装**（L83）——被装饰函数在别处的直接调用保持同步语义。

**execute_action（L87-117）**：运行时分派。未注册名 `ValueError`（L89-90）；`param_model(**params)` 先校验（L95）；再判断第一个形参是否 Pydantic 模型（L98-100），决定两种调用形态——模型实例整体传入（L109/113）或 `model_dump()` 展开成关键字（L110/114）。`requires_mac_builder=True` 的动作要求调用方传 `mac_tree_builder`（L103-110），缺失时 L106 报 "Action X **requires browser** but none provided"——browser-use 原文残留：场景明明是 mac_builder 缺失，文案还念念不忘 browser。执行异常统一包成 `RuntimeError` 重抛（L116-117），由 Controller 转成 `ActionResult(error=...)`。

**create_action_model（L119-138）**：把注册表编译成单个 `ActionModel` 子类——每个动作一个 `Optional[param_model]` 字段，Field 描述即注册时的 `description`（L121-127）；调用顺带触发遥测上报（L129-136）。**get_prompt_description（L140-142）**：委托 views.py L69-71，逐动作拼 `{动作名: {参数schema}}` 串进 system prompt。

配套 views.py 三件套：`RegisteredAction.prompt_description()`（L17-29）渲染时剥掉 schema 的 `title` 键（L19）省 token；`ActionModel`（L32-61）是动态动作模型基类，`get_index`/`set_index`（L41-61）从"单字段动作"读写 `index`——给"高亮元素索引重编号"留的后门；`ActionRegistry`（L64-71）是字典薄壳。

## 三、外部连接

- **controller/service.py**：`Controller.__init__`（L29-35，L34 创建 `Registry`）并 `_register_default_actions()`（L40 起第一个注册）——done 用显式 `param_model=DoneAction`（L40-44），input_text/click_element 等标 `requires_mac_builder=True`（L49/L78），函数体直接使用注入的 `mac_tree_builder._element_cache` 查元素。Controller 只是 Registry 门面：`Controller.action`（L267）代理注册，`multi_act`（L275）循环 `act`（L291）→ `execute_action`。
- **agent/service.py L170**：`type_with_custom_actions(self.ActionModel)` 的 `ActionModel` 正是 `create_action_model()` 产物——注册表经此进入 LLM 输出校验闭环。
- **agent/prompts.py**：system prompt 嵌入 `get_prompt_description()` 输出。
- **telemetry/service.py**：接收 L129-136 的 `ControllerRegisteredFunctionsTelemetryEvent`（含每个动作完整 JSON schema）。
- **上游对照**：三元组与 browser-use 的 `controller/registry/` 同构，`browser` 参数名、`requires browser` 文案、L38 TODO 原样平移；本仓改造点只有 `mac_tree_builder` 注入线。

## 四、数据流

一次"新增自定义动作"的完整旅程：

1. 用户写 `@controller.action('描述', param_model=MyParams, requires_mac_builder=True)` 装饰的异步函数；
2. 装饰器采用/生成参数模型，包装函数，`RegisteredAction` 入表；
3. Agent 初始化时 `create_action_model()` 编译动态 `ActionModel` 并上报遥测；`get_prompt_description()` 把动作说明写进 system prompt；
4. LLM 每步输出 JSON，经动态模型校验得 `action: list[ActionModel]`——每个元素只有一个字段被 set（动作名即字段名）；
5. `multi_act` 逐个 `execute_action`：查表 → 参数校验 → 判 is_pydantic → 实例/展开传参（requires_mac_builder 时注入 builder）→ 返回值包装为 `ActionResult` 回写历史。

反向流（索引重编号）：`get_index/set_index` 在动态模型实例上读写 index，无需知道具体动作类型。

## 五、设计决策与取舍

- **签名即契约**：参数文档、校验、prompt 描述全部从同一函数签名派生，消灭"文档与实现漂移"。代价是签名之外的表达力受限（参数间约束要靠显式 param_model 补）。
- **同步自动异步化**：`asyncio.to_thread` 包装同步动作（L64-65），用户可用同步代码写自动化（pyobjc 调用多为阻塞）而不卡事件循环。拷贝 `__signature__`（L68）是透明包装最易漏的一步，这里做对了。
- **is_pydantic 双形态调用（L98-114）**：兼容面向对象式（收模型实例）与过程式（收展开参数）两种动作风格。判断依据"第一个形参注解是否 BaseModel 子类"简单有效但脆弱：注解为字符串时 `issubclass` 报错（本仓未触发）。
- **exclude_actions 裁剪**：`Controller(exclude_actions=['open_app'])` 即可摘除危险动作，配合装饰器内静默跳过（L55-56），零侵入。
- **注册即遥测**：`create_action_model` 每次调用上报全部函数 schema（L129-136），维护者可统计社区动作分布——也意味着你的动作参数结构默认外发，详见 telemetry-service.md。

## 六、新人提示（坑与勘误）

1. **两处 browser 残留**：L28 `arguments_to_ignore` 里的 `'browser'` 与 L106 报错文案 "requires browser"。读代码时别被误导去找 browser 对象。
2. **`create_action_model` 有副作用**：调用即发遥测（L129-136）。测试里反复构造 Agent 会反复上报；关闭用 `ANONYMIZED_TELEMETRY=false`。
3. **装饰器返回原函数**（L83）：同步调用方拿到的仍是同步函数，异步包装只在表内——`registry.actions['x'].function` 与原函数不是同一对象属正常。
4. **动态字段都是 Optional**（L123）：LLM 输出"全空动作"能通过校验，报错挡在分派层 L89 而非校验层。
5. **`get_index` 只看第一个非 None 字段**（views.py L44-50）：多字段 set 时取字典序靠前的一个，依赖 `model_dump(exclude_unset=True)` 键序，勿在多参数动作上依赖其语义。
6. **异常包装吞类型**（L116-117）：所有错误变 `RuntimeError`，区分参数错/执行错只能解析消息字符串。
7. **自动推导路径零使用**：controller/service.py 默认动作全传显式 `param_model`，`_create_param_model` 是留给第三方的便利，测试覆盖最薄。
