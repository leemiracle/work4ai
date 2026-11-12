# controller/service.py —— Controller：装饰器闭包注册的七个默认动作

## 一、角色定位

`mlx_use/controller/service.py`（316 行）是"LLM 意图 → 系统副作用"的翻译官。`Controller` 类持有动作注册中心 `Registry`，在构造时用装饰器把**七个默认动作**注册成闭包；`multi_act`/`act` 两个执行器把 `AgentOutput.action` 列表逐个派发。它同时是扩展点——用户子类化 Controller 再 `@controller.action('描述')` 装饰自己的函数，新动作就自动进入结构化输出 schema（Registry 的 `create_action_model` 动态造模型，agent/service.py:168 调用）。

七个默认动作（controller/service.py:37-265）：`done`（携带总结文本结束任务）、`input_text`、`click_element`、`right_click_element`、`scroll_element`、`open_app`（启动 App 并回 pid）、`run_apple_script`（osascript 逃生通道）。前五个带 `requires_mac_builder=True`——声明执行期需要 Agent 传下来的树构建器做 index 寻址。

## 二、内部结构

**注册期 `_register_default_actions`（controller/service.py:37-265）**：每个动作一个 `@self.registry.action(description, param_model=..., requires_mac_builder=...)` 装饰的 async 闭包。param_model 全部来自 controller/views.py 的 Pydantic 小模型（`ClickElementAction{index,action}`、`InputTextAction{index,text,submit}`、`ScrollElementAction{index,direction: Literal}` 等）。四个 UI 动作闭包同构四拍：查 `_element_cache` 有无 index（controller/service.py:54,83,119,148）→ 查 `element.enabled` → 调 mac/actions.py 原子函数 → 把 bool 折算成 `ActionResult`（失败时 extracted_content 与 error 双写，让模型下轮看到）。

**`open_app`（controller/service.py:169-221）**：三级 pid 解析链——`NSWorkspace.launchApplication_`（:176）失败再试小写名（:181-184）；启动后睡 1 秒（:189），按 bundle id 前缀匹配 runningApplications 找 pid（:191-196）；仍找不到就 `pgrep -i` 子进程兜底（:199-213）。成功返回 `ActionResult(current_app_pid=pid)`（:221）——这个 pid 就是 agent 端 `get_last_pid`（agent/service.py:183-190）的数据源。

**`run_apple_script`（controller/service.py:223-265）**：把脚本包进 AppleScript 的 try/on error 壳（:231-238），`osascript -e` 子进程执行（:241-245），按输出协议解析："OK"→Success、"ERROR:..."→错误、其他输出原样返回（:247-256）。

**执行器 `multi_act`/`act`（controller/service.py:274-309）**：`multi_act` 顺序执行动作列表，**遇 done/error/最后一个即熔断**（:285）——一步失败后续动作全部跳过（此时 index 大概率已失效，继续执行只会错上加错）。`act` 把单个 ActionModel `model_dump(exclude_unset=True)` 展开（:294）——pydantic 联合动作模型一次只有一个字段被赋值——取出 `(action_name, params)` 调 `registry.execute_action`（:296），按返回类型分派成 ActionResult（:297-304）。

## 三、外部连接

- **Registry（controller/registry/service.py）**：真正持有动作表。`arguments_to_ignore = ['browser','mac_tree_builder','builder']`（registry/service.py）在生成参数模型时剥掉依赖注入参数；`execute_action` 里 `requires_mac_builder` 分支校验 builder 并以 kwargs 注入（注意其错误文案"requires browser but none provided"——browser-use 残留，见坑 6）。
- **agent/service.py**：`multi_act` 的两个调用点——每步动作（agent/service.py:233）与初始动作（:409-411，`check_for_new_elements=False`）。
- **mac/actions.py 与 tree.py**：闭包体消费的四原子函数与 `_element_cache` 地址簿。
- **views.py（controller）**：六个动作参数模型 + 大段被注释的 browser 动作化石（SearchGoogleAction/GoToUrlAction 等）。

## 四、数据流

`AgentOutput.action: list[ActionModel]` → `multi_act` 循环 → `act` 展开 `(name, params)` → `Registry.execute_action(name, params, mac_tree_builder=...)` → param_model 校验 → 判断函数首参是否 Pydantic 模型（registry 的 `is_pydantic` 探测，本项目闭包首参是 int 所以走 `**validated_params.model_dump()` 展开）+ builder 以 kwargs 注入 → 闭包执行 → ActionResult 逐层回传。index 在这条链上被两次消费：闭包里查 cache 拿节点，element 内部再持有原始 AXUIElement 引用直通 AX API。`done` 动作的 `is_done=True` 沿 result 上浮到 agent 端 `history.is_done()`（views.py:152-156）终止循环。

## 五、设计决策与取舍

- **闭包注册而非方法分发**：动作不是类方法而是 `_register_default_actions` 里的局部闭包——好处是 `exclude_actions` 逻辑集中在 Registry、每个动作的描述/参数模型/依赖声明全在装饰器一处可读；代价是子类无法覆写单个默认动作（只能整个重建 Controller 或 exclude 后重注册同名）。browser-use 上游同款设计。
- **依赖注入走函数签名**：`mac_tree_builder` 出现在参数列表但被 Registry 从 LLM schema 中隐藏、执行期自动注入——LLM 永远看不见这个参数，函数体却拿得到。这套"签名即契约"的魔法是理解整个注册体系的关键。
- **error 即熔断**（:285）：把"动作序列的原子性"交给模型自己判断——prompt（prompts.py:43-44）教了"稳定 UI 批量、动态 UI 单步"，运行期再用熔断兜底。
- **AppleScript 逃生通道**：UI 自动化覆盖不了的（窗口级操作、深层脚本接口），让模型写 AppleScript 直接兜——代价是模型获得了近乎完整的系统权限（README.md:147 的警告即源于此），且 f-string 内插无任何注入防护（:231-238）。

## 六、新人提示（坑与勘误）

1. **`from playwright.async_api import Page`（controller/service.py:8）是死导入**：全文件零使用，是 browser-use 血统的残留。playwright 甚至不在 mac 链路的运行路径上（pyproject 仍列为依赖）。
2. **`@time_execution_sync` 装饰了 async 函数（controller/service.py:290）**：utils.py 的 sync 包装器不 await，只是创建 coroutine 就返回——功能上侥幸正确（multi_act 在 :282 `await self.act(...)` 把这个 coroutine await 掉了），但计时完全失真（只测了 coroutine 创建），且这是异步装饰器误用的活标本。
3. **`open_app` 的 pid 匹配是子串匹配**（:192）：`app_name.lower() in app.bundleIdentifier().lower()`——开 "Notes" 可能匹配到任何 bundle id 含 notes 的 App（如某些第三方笔记应用）；pgrep -i 兜底（:201-208）同样宽松且取第一个 pid。
4. **`NoParamsAction`（controller/service.py:311-315）在本文件无人使用**：它是给外部注册者准备的基类便利，但没有任何示例消费——接近死代码。
5. **动作闭包的 `logging.error` 与模块 `logger.error` 混用**（:72,88,100 vs :107,108）：两处用了 root logger（`logging.error`），与 :25 的模块 logger 不一致，日志级别配置对前者无效。
6. **Registry 错误文案残留**（registry/service.py execute_action）："Action ... requires browser but none provided"——macOS 项目里说 browser，误导排障方向；同文件 `arguments_to_ignore` 列表里的 `'browser'` 同样是上游参数名残留。
7. **初始动作路径不查新元素**（agent/service.py:410 `check_for_new_elements=False`）：但 `multi_act` 签名里这个参数（:276）实际上无人消费——又一个签名与实现脱节的化石参数。

（行号锚：controller/service.py:8,25,37-265,54,83-84,91,119,148,169-221,191-196,199-213,221,223-265,274-309,282,285,290-309,294,296-304,311-315；agent/service.py:168,183-190,233,409-411；views.py:152-156；README.md:147；prompts.py:43-44）
