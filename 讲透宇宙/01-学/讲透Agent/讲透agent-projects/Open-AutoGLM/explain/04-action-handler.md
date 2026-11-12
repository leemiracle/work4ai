# 04 · 动作执行层（phone_agent/actions/handler.py）

> 对应 tour 第 6 步前半「动作执行」。模型输出的伪代码在这里变成真机操作。

## ① 角色定位

`handler.py` 承担三件事：**安全解析**（`parse_action` 用 `ast.parse` 而非 eval 还原模型输出的伪代码调用）、**分派执行**（`ActionHandler` 把动作字典路由到 14 个 `_handle_*` 并经 `DeviceFactory` 抵达设备）、**人机安全边界**（敏感操作确认 `confirmation_callback` 与人工接管 `takeover_callback` 双回调）。它是"不可信模型输出"与"真机副作用"之间唯一的一层防线，也是隐私政策（`resources/privacy_policy.txt` 六类高风险操作）在代码里的落点。

## ② 内部结构

**`ActionResult`**（`phone_agent/actions/handler.py:14-21`）：`success/should_finish/message/requires_confirmation` 四字段——注意 `requires_confirmation` 定义后无任何赋值点，是预留字段。

**`ActionHandler`**（`:24`）构造期只存 `device_id` 与两个回调，缺省回落到控制台版（`:42-43`）——`_default_confirmation` 走 `input()` Y/N（`:320-324`），`_default_takeover` 等人工回车（`:326-329`）。

**`execute`**（`:45`）的容错阶梯：`_metadata=="finish"` 直接成功收尾（`:61-64`）；非 `do` 的未知元类型 `should_finish=True`（`:66-71`）——协议级错误终止任务；动作名不在分派表 `should_finish=False`（`:76-81`）——单个动作不认识只是跳过继续；具体 handler 抛异常被兜住返回失败（`:83-88`）。

**分派表 `_get_handler`**（`:90-108`）：14 个键——`Launch/Tap/Type/Type_Name/Swipe/Back/Home/Double Tap/Long Press/Wait/Take_over/Note/Call_API/Interact`。`Type_Name` 与 `Type` 共用 `_handle_type`（`:95-96`）是语义别名；`Note/Call_API` 是**占位空实现**（`:241-251`，注释自述"依赖具体需求"），`Interact` 只回一条消息（`:253-256`）——提示词里这三个动作对模型可见但对手机无副作用。

各 handler 的共同姿势：取参数 → 相对坐标换算 → 工厂调用。`_convert_relative_to_absolute`（`:110-116`）把 0-1000 归一坐标乘上截图宽高。`_handle_tap` 在执行前检查 `action` 里有无 `message` 键——有则先过 `confirmation_callback`，用户拒绝即 `should_finish=True` 结束任务（`:139-145`）。`_handle_type` 是最重的动作，五拍节奏全靠 `TIMING_CONFIG.action` 的四个延时配置（`:158-171`）：切 ADB 键盘→sleep→清文本→sleep→输入→sleep→还原键盘→sleep。`_handle_wait` 解析 `"3 seconds"` 字符串，解析失败回落 1 秒（`:226-230`）。`_handle_takeover` 只调回调不碰设备（`:235-239`）。

**`parse_action`**（`:332-387`）三条路径：

1. **Type 特判**（`:348-353`）：响应以 `do(action="Type"` 或 `Type_Name` 开头时，直接 `split("text=",1)[1][1:-2]` 切片取正文——绕过语法解析，文本里含未转义引号/换行也不炸。
2. **AST 主路径**（`:354-376`）：先把裸 `\n\r\t` 替换成字面转义（`:358-360`），`ast.parse(mode="eval")`（`:362`）、校验根节点是 `ast.Call`（`:363-364`），再逐 keyword 用 `ast.literal_eval` 取**字面量值**（`:369-372`）——不 eval 任何表达式，`element=[100,200]` 还原成 list。
3. **finish 分支**（`:378-382`）：字符串手术 `replace("finish(message=","")[1:-2]` 剥引号与括号。

模块级 `do()/finish()` 帮助函数（`:390-399`）给编程构造动作字典用（如 `phone_agent/agent.py:195` 的解析兜底）。

**`_send_keyevent`**（`:258-318`）：handler 里唯一带平台分支的方法——HDC 设备把 ENTER 映射到鸿蒙 keyEvent 2054（`:271-276`），ADB 走标准 `input keyevent`（`:313-318`）。这是抽象泄漏的孤例（应下沉设备栈），也说明工厂只覆盖了"高频原语"。

## ③ 外部连接

- **imports**：`config.timing.TIMING_CONFIG`（`:10`）与 `device_factory.get_device_factory`（`:11`）——所有设备操作都通过工厂，本文件零 adb/hdc 字样（`_send_keyevent` 例外）。
- **被谁用**：`actions/__init__.py` 只导出 `ActionHandler/ActionResult`；`agent.py:8-9` 同时导入它和 `parse_action/do/finish`；iOS 线 `agent_ios.py` 复用 `parse_action` 但用独立的 `handler_ios.py` 执行——**解析协议共享、执行栈分叉**。
- **提示词耦合**：分派表 14 键与 `prompts_zh.py` 指令表一一对应（`phone_agent/config/prompts_zh.py:24-53`），见 02 篇三角契约。

## ④ 数据流

```
ModelClient → response.action 字符串（如 'do(action="Tap", element=[500,300])'）
 → parse_action: 转义→ast.parse→literal_eval
   = {"_metadata":"do", "action":"Tap", "element":[500,300]}
 → ActionHandler.execute(action, screen_w, screen_h)
   → 分派表命中 _handle_tap
   → (500/1000*w, 300/1000*h) 像素坐标
   → [message 键? → confirmation_callback 人审]
   → DeviceFactory.tap(x,y) → adb input tap
 → ActionResult{success, should_finish, message} → agent 回填历史/判终
```

`_metadata` 是贯穿的协议键：`execute` 用它区分 do/finish（`:59-66`），agent 用它判终（`phone_agent/agent.py:227`），`do()/finish()` 帮助函数注入它（`:392,398`）。

## ⑤ 设计决策与陷阱

1. **ast 而非 eval 是安全底线**（`:362,371`）：模型输出永远当不可信输入；`literal_eval` 只认字面量，`__import__` 之类在词法层就被拒。
2. **错误分级**：协议错（非 do/finish）终止任务，动作错（未知动作名/执行异常）跳过继续（`:66-88`）——与提示词规则 14/15"跳过并在 finish message 说明"呼应，但也意味着**未知动作静默成功**（返回 `success=False` 但循环继续），日志里容易漏看。
3. **敏感确认的取消=终止**（`:141-145`）：用户拒绝即 `should_finish=True`，不是"跳过该动作"。要"取消但继续"语义需改这里。
4. **Type 特判切片的边界**（`:351`）：`[1:-2]` 假设收尾必是 `")`，模型若输出尾随空格（`" )`）会把残括号带进文本。
5. **四段 sleep 串行**（`:159-171`）：一次 Type 固定 ~4 秒基线（timing.py 默认全 1.0s），任务里大量输入时显著拖慢；`PHONE_AGENT_*` 环境变量可调（`phone_agent/config/timing.py:22-33`）。
6. **`_send_keyevent` 的 HDC 特判**（`:266-310`）是本层唯一平台 if——新增平台此处必漏，重构方向是把 keyevent 纳入工厂接口。

## ⑥ 新人提示

- 加新动作：`_get_handler` 加键（`:92`）→ 写 `_handle_*` → 提示词指令表补样例（中英双份）——三步缺一模型学不会。
- 单测友好：`parse_action` 是纯函数，直接 `assert parse_action('do(action="Back")') == {"_metadata":"do","action":"Back"}` 式测试；`execute` 可用假工厂打桩。
- 调"点了没反应"问题链：先看分派是否命中（`:74-81`），再看坐标换算（`:136`），最后才怀疑设备层。
- 敏感操作联调：给 `PhoneAgent` 传自定义 `confirmation_callback`（`phone_agent/agent.py:68`）比用默认 input() 适合自动化测试。
- iOS 改动作协议记得 `handler_ios.py` 平行改——分派表在这层是两份。
