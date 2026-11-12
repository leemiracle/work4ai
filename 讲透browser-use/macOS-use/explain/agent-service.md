# agent/service.py —— Agent 主循环：感知、决策、执行的三拍子

## 一、角色定位

`mlx_use/agent/service.py`（490 行）是 macOS-use 的心脏：把 macOS Accessibility 树喂给 LLM、拿回结构化动作序列、再驱动 Controller 执行的自主循环。它不感知像素——全仓库没有截图输入链路——而是把 UI 抽象成 `[index][:]<AXButton actions="AXPress"> [interactive]` 文本序列（element.py 生成），让模型在纯文本世界里"看-想-做"。

血统一眼可辨：这是 browser-use 的 `AgentService` 移植版。参数名（`browser` 换 `mac_tree_builder`）、提示词三件套（evaluation_previous_goal / memory / next_goal）、telemetry 事件族全部同构。心智模型：**browser-use 的 DOM 感知层被整层换成 macOS AX API，决策与执行骨架原样保留**。

## 二、内部结构

文件只有一个 `Agent` 类，分五块：

**初始化（`__init__`，service.py:55-147）**：核心参数是 `task`/`llm`/`controller`/`max_actions_per_step`。service.py:101 自建 `MacUITreeBuilder` 作感知探针；service.py:112 调 `_setup_action_models()`（service.py:165-170）从 Registry 动态生成 `ActionModel`/`AgentOutput` 两个 Pydantic 模型；service.py:120-129 组装 `MessageManager`。`_paused`/`_stopped` 旗标在 service.py:146-147。

**单步 `step()`（service.py:192-260）**：全仓库最重要的 70 行。睡 1 秒等 UI 稳定（service.py:194）→ 无 pid 时预置开场白（service.py:202-203）→ `build_tree` 建树取可点击元素串（service.py:205-207）→ 注入状态消息（service.py:217）→ 调 LLM（service.py:221）→ 成功后 `_remove_last_state_message` 再 `add_model_output`（service.py:227-228）→ `multi_act` 执行（service.py:233）。异常统一落 `_handle_step_error`（service.py:241-243），`finally` 无条件发 telemetry（service.py:246-255）。

**错误处理（service.py:262-288）**：`ValidationError/ValueError` 细分"Max token limit reached"（削 500 token 并 `cut_messages`，service.py:270-274）与"Could not parse response"（追加 JSON 提示，service.py:275-277）；`RateLimitError` 睡 `retry_delay`；其余计一次连续失败。返回 `ActionResult(error=..., include_in_memory=True)`（service.py:288）让错误以独立 HumanMessage 入记忆。

**LLM 调用 `get_next_action`（service.py:309-328）**：`with_structured_output(self.AgentOutput, include_raw=True)` 拿原始响应；`parsed` 为 None 抛 `ValueError('Could not parse response.')`（service.py:319-321）——这个字符串是上游错误分档的匹配依据，改文案会静默破坏自愈。动作超量截断在 service.py:324，`n_steps += 1` 在 service.py:326（**只有 LLM 调用成功才计步**，失败步不占预算）。

**外层 `run`（service.py:401-442）**：`@observe(name='agent.run')` 挂 Laminar 追踪（service.py:401）。初始动作先执行（service.py:408-412），循环内依次查失败上限（service.py:415）、暂停/停止旗标（service.py:419）、执行 step、查 `history.is_done()`（service.py:424-428）。for-else（service.py:429-430）区分"步数耗尽"与"任务完成"两种终态。

## 三、外部连接

- **MessageManager**（service.py:27）：消息历史唯一权威，token 裁剪全在其内。Agent 每步只做"加状态→取消息→删状态→加模型输出"。
- **Controller/Registry**（service.py:38）：动作执行全权委托，Agent 只消费 `ActionResult`。
- **MacUITreeBuilder**（service.py:39,101）：builder 属于 Agent 而非 Controller，每步 `multi_act` 时作参数传下去（service.py:233），动作靠 `requires_mac_builder=True` 声明依赖。
- **ProductTelemetry**（service.py:40-45,109）：PostHog 匿名遥测，`ANONYMIZED_TELEMETRY=False` 可关。
- **AgentHistoryList**（views.py:89）：`_make_history_item`（service.py:290-307）存 model_output/state/result，供 `is_done()`/`save_history` 消费。

## 四、数据流

1. **pid 流**：`open_app` 返回 `ActionResult(current_app_pid=...)`（controller/service.py:221）存入 `_last_result`；下步 `get_last_pid()`（service.py:183-190）倒序扫描取最新 pid 喂 `build_tree`。"Agent 记得自己开的是哪个 App"的全部机制就是一个 Optional[int] 接力棒。
2. **状态流**：AX 树 → 可点击元素字符串 → 状态 HumanMessage → LLM → `AgentOutput{current_state, action[]}` → AIMessage+ToolMessage 永久入史 → 状态消息删除。**状态消息阅后即焚**（service.py:217/227）：历史里永远只有动作与结果，没有两步前的整棵树，以此控制上下文膨胀。
3. **错误流**：异常 → 格式化错误串 → `include_in_memory=True` 的 ActionResult → 下步被提升为独立 HumanMessage，同时 telemetry 带 `consecutive_failures`。

## 五、设计决策与取舍

- **文本树而非截图**：`use_vision` 参数（service.py:60）存在但全文件无消费点。纯 AX 文本感知是刻意选择：token 可控、元素可直接索引、无需多模态；代价是空间布局仅剩 position/size 属性。
- **每步 sleep(1)**（service.py:194）：给 AX 树一点动画沉淀时间，避免读到过渡态。这是 observer 被 stub 掉（见 tree 篇）背景下的务实补丁。
- **失败步不计步**：`n_steps` 只在 service.py:326 递增，宽限解析抖动；`consecutive_failures` 独立计数兜底（service.py:444-449），双闸门。
- **动态模型生成**：动作集合运行期从 Registry 造出（service.py:168-170），注册自定义动作后自动进结构化输出 schema，LLM 侧零改动——browser-use 系框架最优雅的一手。

## 六、新人提示（坑与勘误）

1. **可变默认参数 `controller: Controller = Controller()`**（service.py:59）：两个 Agent 不显式传 controller 会共享同一 Registry，自定义动作互相可见。
2. **`set_tool_calling_method` 吞显式值**（service.py:172-181）：只有 `== 'auto'` 分支无 else，你显式传 `'function_calling'` 返回的是 None——静默降级。
3. **`generate_gif` 死参数**（service.py:68）：收下后零消费；service.py:24 的 PIL 导入同样为死——GIF 逻辑移植时删了，参数忘删。
4. **`include_attributes` HTML 语义错位**（service.py:69-80）：`tabindex`/`aria-label`/`placeholder`/`alt`/`aria-expanded` 是 DOM 属性，AX 世界不存在；且 element.py 的序列化用硬编码 `['title','value','description','enabled']`，整个 mac 链路没人消费它——纯装饰参数。
5. **`_make_history_item` 死变量**（service.py:300-303）：`interacted_element`/`len_result`/`interacted_elements` 赋值后从未使用，是 browser-use 定位逻辑残骸。
6. **`_save_conversation` 陷阱**（service.py:351）：路径为纯文件名时 `os.path.dirname()` 得空串，`os.makedirs('')` 直接 FileNotFoundError。
7. **版本漂移**：service.py:150 硬编码 `'0.0.1'`，pyproject.toml 是 0.0.3，遥测版本失真。
8. **MLX 是愿景不是现实**：依赖里没有 mlx-lm，examples 全用 `ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')`（examples/calculate.py:28）；README.md:136 明言 mlx 本地推理是未勾选的 roadmap。"LLM 实走 Gemini/OpenAI 云端"是读这个仓库前必须校准的预期。

（行号锚：service.py:24,55,59,60,68,69-80,101,109,112,120-129,146-147,150,165-170,172-181,183-190,192-260,262-288,290-307,309-328,401-442,444-449；views.py:89；controller/service.py:221；examples/calculate.py:28；README.md:136）
