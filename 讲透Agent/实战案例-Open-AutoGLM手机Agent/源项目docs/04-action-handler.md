# 04 · 动作执行器（Action Handler）

> 本文解析 `phone_agent/actions/handler.py`（Android/HarmonyOS，399 行）和 `handler_ios.py`（iOS，280 行）。
> 这一层是 **Agent 决策** 与 **设备执行** 之间的桥梁，定义了 AutoGLM 的动作协议。

## 文件地图

| 文件 | 行数 | 作用 |
|------|------|------|
| `phone_agent/actions/__init__.py` | 5 | 导出 `ActionHandler`, `ActionResult` |
| `phone_agent/actions/handler.py` | 399 | **ActionHandler** + `parse_action` + `do`/`finish` 辅助函数 |
| `phone_agent/actions/handler_ios.py` | 280 | IOSActionHandler（WDA 直连，不走 DeviceFactory）|

## AutoGLM 动作协议

模型输出的动作字符串遵循两种格式之一：

```
do(action="<ActionName>", <key>=<value>, ...)
finish(message="<终止说明>")
```

**例子**：

```
do(action="Tap", element=[500, 300])
do(action="Tap", element=[500, 300], message="确认下单")
do(action="Type", text="无线耳机")
do(action="Swipe", start=[500, 800], end=[500, 200])
do(action="Launch", app="小红书")
do(action="Back")
do(action="Wait", duration="2 seconds")
do(action="Take_over", message="需要输入验证码")
finish(message="已成功下单 3 件商品")
```

解析后变成 dict：

```python
{"_metadata": "do", "action": "Tap", "element": [500, 300]}
{"_metadata": "finish", "message": "已成功下单"}
```

`_metadata` 字段是类型标识（`"do"` 或 `"finish"`），由 parser 注入，模型不输出。

## `parse_action`：字符串 → dict

`handler.py:332-387`。**安全第一**：用 `ast` 解析而非 `eval`。

### 解析路径

```python
def parse_action(response: str) -> dict[str, Any]:
    print(f"Parsing action: {response}")   # ⚠ debug 残留,生产可删
    response = response.strip()

    # 路径 A: Type 动作特殊处理(因为 text 含特殊字符会破坏 AST)
    if response.startswith('do(action="Type"') or response.startswith('do(action="Type_Name"'):
        text = response.split("text=", 1)[1][1:-2]   # 简单字符串切分
        return {"_metadata": "do", "action": "Type", "text": text}

    # 路径 B: 其他 do(...) 用 AST 解析
    if response.startswith("do"):
        response = response.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        tree = ast.parse(response, mode="eval")
        if not isinstance(tree.body, ast.Call):
            raise ValueError("Expected a function call")
        call = tree.body
        action = {"_metadata": "do"}
        for keyword in call.keywords:
            action[keyword.arg] = ast.literal_eval(keyword.value)
        return action

    # 路径 C: finish(...)
    if response.startswith("finish"):
        return {
            "_metadata": "finish",
            "message": response.replace("finish(message=", "")[1:-2],
        }

    raise ValueError(f"Failed to parse action: {response}")
```

### 为什么 Type 要特殊路径？

Type 动作的 `text` 参数可能含**引号、换行、特殊字符**，例如：

```
do(action="Type", text="她说："你好"")
```

这种字符串无法直接 `ast.parse`。所以走简单字符串切分：`response.split("text=", 1)[1][1:-2]` —— 取 `text=` 之后的内容，去掉前后引号。

> **潜在 bug**：如果 Type 的 text 本身以 `"` 结尾（如 `text="hello""`），切分逻辑可能错。实际使用中 text 通常不带尾引号，所以问题不严重。

### 为什么用 AST 而非 eval？

`eval(response)` 能解析同样的字符串，但有**代码注入风险**：模型（或恶意构造的输出）可能输出：

```
do(action="Tap", element=__import__('os').system('rm -rf /'))
```

`ast.parse + ast.literal_eval` 只允许字面量（数字、字符串、列表、字典、元组、布尔、None），任何名字解析或调用都会抛 `ValueError`，被 Agent 捕获后转成 `finish`。

### 边界情况

| 输入 | 结果 |
|------|------|
| `do(action="Unknown")` | 解析成功，但 `_get_handler` 返回 None，execute 返回 `Unknown action` |
| `not_do_not_finish` | 抛 `ValueError` → Agent 把它当 `finish(message=...)` |
| `do()` | AST 解析成功但 `action` key 缺失，`_get_handler(None)` → Unknown |
| `do(action="Tap")` 缺 element | 解析成功，handler 检查到 `element is None` 返回错误 |
| 多行响应 | 路径 B 会转义换行再解析 |

## `ActionHandler.execute`：调度核心

`handler.py:45-88`：

```python
def execute(self, action: dict, screen_width: int, screen_height: int) -> ActionResult:
    action_type = action.get("_metadata")

    if action_type == "finish":
        return ActionResult(success=True, should_finish=True, message=action.get("message"))

    if action_type != "do":
        return ActionResult(success=False, should_finish=True,
                            message=f"Unknown action type: {action_type}")

    action_name = action.get("action")
    handler_method = self._get_handler(action_name)

    if handler_method is None:
        return ActionResult(success=False, should_finish=False,
                            message=f"Unknown action: {action_name}")

    try:
        return handler_method(action, screen_width, screen_height)
    except Exception as e:
        return ActionResult(success=False, should_finish=False,
                            message=f"Action failed: {e}")
```

**三层异常处理**：
1. 未知 `_metadata` 类型 → `should_finish=True`（致命，终止）
2. 未知 action 名 → `should_finish=False`（让 Agent 继续尝试别的）
3. handler 抛异常 → `should_finish=False`，把异常塞进 message

> **注意**：Agent 拿到 `should_finish=False` 的失败结果后，并不会主动重试同一个动作——它会把这次失败结果作为上下文，让模型在下一步决策。模型可能自己决定重试（换个坐标点），也可能换路径。

## 14 种动作 handler

### 6 大动作分类（DeepWiki 视角）

DeepWiki 把 15+ 动作归为 6 大功能类别，对理解动作语义有帮助：

| 类别 | 动作 | 用途 |
|------|------|------|
| **App Control** | `Launch`、`Back`、`Home` | 应用导航与生命周期 |
| **Touch Gestures** | `Tap`、`Double Tap`、`Long Press`、`Swipe` | 直接屏幕触控 |
| **Text Input** | `Type`、`Type_Name` | 键盘输入 |
| **Flow Control** | `Wait`、`finish` | 执行节奏与任务完成 |
| **User Interaction** | `Take_over`、`Interact` | 人工介入与用户选择 |
| **Content Operations** | `Note`、`Call_API` | 内容记录与总结（占位） |

典型任务流程：`Launch` → 导航（`Tap`/`Swipe`/`Back`）→ `Type` 输入 → 高级交互（`Long Press`/`Double Tap`）→ `Wait` 加载 → `Take_over` 认证 → `finish`。

> **动作计数说明**：不同视角会得到不同数字，本文档统一约定：
> - **14 个 handler**：`_get_handler` 字典注册的映射数（`Type` 和 `Type_Name` 共用 `_handle_type`，详见下表）
> - **15 种动作**：中文 prompt 描述的 `do(...)` 动作种类（把 `Tap` 和 `Tap+message` 算两种）
> - **7 种动作**：英文 prompt 的精简版
> - **+1 个 finish**：终止动作（`_metadata: "finish"`，不走 handler 调度）

### 完整 handler 映射

`_get_handler` 返回的 handler 字典（`handler.py:90-108`）：

| Action 名 | Handler | 用途 | 走 DeviceFactory? |
|----------|---------|------|------------------|
| `Launch` | `_handle_launch` | 启动 app | ✅ `launch_app` |
| `Tap` | `_handle_tap` | 点击 | ✅ `tap` |
| `Type` / `Type_Name` | `_handle_type` | 输入文本 | ✅ `type_text` + 键盘管理 |
| `Swipe` | `_handle_swipe` | 滑动 | ✅ `swipe` |
| `Back` | `_handle_back` | 返回键 | ✅ `back` |
| `Home` | `_handle_home` | Home 键 | ✅ `home` |
| `Double Tap` | `_handle_double_tap` | 双击 | ✅ `double_tap` |
| `Long Press` | `_handle_long_press` | 长按 | ✅ `long_press` |
| `Wait` | `_handle_wait` | 等待 | ❌ `time.sleep` |
| `Take_over` | `_handle_takeover` | 人工接管 | ❌ 调 `takeover_callback` |
| `Note` | `_handle_note` | 记录页面内容 | ❌ 占位（无操作）|
| `Call_API` | `_handle_call_api` | 总结/评论 | ❌ 占位（无操作）|
| `Interact` | `_handle_interact` | 用户交互 | ❌ 仅返回 message |

**注意**：`Note` / `Call_API` / `Interact` 是**占位实现**——返回成功但不做任何事。prompt 里告诉模型可以用它们记录内容或请求总结，但当前实现是 noop。这是预留给二次开发的扩展点。

## 关键 handler 详解

### `_handle_tap`：点击（含敏感操作确认）

`handler.py:130-149`：

```python
def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
    element = action.get("element")
    if not element:
        return ActionResult(False, False, "No element coordinates")

    x, y = self._convert_relative_to_absolute(element, width, height)

    # 敏感操作检测:带 message 字段的 Tap
    if "message" in action:
        if not self.confirmation_callback(action["message"]):
            return ActionResult(success=False, should_finish=True,
                                message="User cancelled sensitive operation")

    device_factory = get_device_factory()
    device_factory.tap(x, y, self.device_id)
    return ActionResult(True, False)
```

**敏感操作协议**：prompt 告诉模型，点击涉及**财产/支付/隐私**的按钮时要带 `message` 参数：

```
do(action="Tap", element=[500, 300], message="确认支付 ¥99.00")
```

handler 检测到 `message` 字段就调 `confirmation_callback`，让用户确认。回调返回 False → 任务终止。

### `_handle_type`：输入文本（含键盘切换）

`handler.py:151-173`：

```python
def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
    text = action.get("text", "")
    device_factory = get_device_factory()

    # 1. 切换到 ADB Keyboard(返回原 IME 供恢复)
    original_ime = device_factory.detect_and_set_adb_keyboard(self.device_id)
    time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)

    # 2. 清空当前输入框
    device_factory.clear_text(self.device_id)
    time.sleep(TIMING_CONFIG.action.text_clear_delay)

    # 3. 输入新文本
    device_factory.type_text(text, self.device_id)
    time.sleep(TIMING_CONFIG.action.text_input_delay)

    # 4. 恢复原输入法
    device_factory.restore_keyboard(original_ime, self.device_id)
    time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

    return ActionResult(True, False)
```

**4 个 delay 都来自 `TIMING_CONFIG`**（见 [06-config-prompts.md](06-config-prompts.md#timing-时间常量)）。这些等待是必要的——切换 IME、清空、输入都需要时间，立即截图会捕捉到中间状态。

**iOS 版简化**（`handler_ios.py:161-176`）：WDA 不需要键盘切换，直接 `clear_text` → `type_text` → `hide_keyboard`。

### `_handle_launch`：启动 app

```python
def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
    app_name = action.get("app")
    if not app_name:
        return ActionResult(False, False, "No app name specified")

    device_factory = get_device_factory()
    success = device_factory.launch_app(app_name, self.device_id)
    if success:
        return ActionResult(True, False)
    return ActionResult(False, False, f"App not found: {app_name}")
```

`launch_app` 内部做的事（见 [03-device-layer.md](03-device-layer.md)）：
- Android: `adb shell monkey -p <package> -c android.intent.category.LAUNCHER 1`
- HarmonyOS: `hdc shell aa start -b <bundle> -a <ability>`
- iOS: `POST /wda/apps/launch {"bundleId": "..."}`

`app_name`（中文名如"小红书"）→ 包名（如 `com.xingin.xhs`）的映射在 `config/apps*.py`，详见 [06-config-prompts.md](06-config-prompts.md)。

### `_handle_takeover`：人工接管

```python
def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
    message = action.get("message", "User intervention required")
    self.takeover_callback(message)
    return ActionResult(True, False)
```

**关键**：`takeover_callback` 是**阻塞调用**——它在等待用户手动完成操作（输入密码、过验证码、扫码登录）后才返回。默认实现是 `input("Press Enter after completing...")`。

返回 `should_finish=False`，所以接管完成后 Agent 继续下一步——通常会重新截图看到登录后的状态。

## 坐标系：相对 → 绝对

`handler.py:110-116`：

```python
def _convert_relative_to_absolute(self, element: list[int], screen_width: int, screen_height: int):
    x = int(element[0] / 1000 * screen_width)
    y = int(element[1] / 1000 * screen_height)
    return x, y
```

模型输出 `[0-1000, 0-1000]`（实际 prompt 写的是 0-999，但代码按 1000 算），handler 转成屏幕像素：

| 模型坐标 | 1080×2400 屏幕 | 含义 |
|---------|---------------|------|
| `[0, 0]` | `(0, 0)` | 左上角 |
| `[500, 500]` | `(540, 1200)` | 中心 |
| `[999, 999]` | `(1078, 2397)` | 右下角附近 |
| `[1000, 1000]` | `(1080, 2400)` | 右下角(理论) |

**iOS 多一层缩放**：WDA Actions API 用逻辑像素（points），而截图是物理像素，所以 `xctest/device.py` 在调 WDA 前会把坐标再除以 `SCALE_FACTOR = 3`（Retina 3x 设备）。

> **潜在 bug**：`SCALE_FACTOR = 3` 是硬编码，对 1x/2x 设备（老 iPhone、iPad mini）会算错坐标。详见 [03-device-layer.md](03-device-layer.md#ios-坐标缩放)。

## iOS 版差异（IOSActionHandler）

`handler_ios.py` 与 `handler.py` 结构几乎完全相同（同样 14 个 handler），差异：

| 维度 | ActionHandler (Android) | IOSActionHandler (iOS) |
|------|------------------------|----------------------|
| 设备访问 | 通过 `get_device_factory()` | 直接调 `xctest.tap(wda_url, session_id, ...)` |
| 时间常量 | `TIMING_CONFIG`（可配置） | 硬编码 `time.sleep(0.5)` |
| 长按 duration | 来自 action dict | 硬编码 `duration=3.0`（秒） |
| `_send_keyevent` | 有（处理 HDC keycode 映射） | 无 |
| back 实现 | 设备按键 | WDA 左边缘手势滑动 |
| type 流程 | 切 IME → clear → type → 恢复 IME | clear → type → hide_keyboard |

**`_send_keyevent` 是死代码**：`handler.py:258-318` 定义了它，但**没有任何 handler 调用它**。它处理 HDC 的 keycode 映射（如 Android KEYCODE_ENTER=66 → HarmonyOS 2054），看起来是预留给"按回车确认搜索"等隐式需求的，但当前 prompt 和 handler 都没用到。

## 完整动作清单（与 prompt 对照）

下表是 prompt 里告诉模型的动作 vs handler 实际支持的：

| Prompt 描述（prompts_zh.py） | 实际 handler 支持 | 状态 |
|----------------------------|-----------------|------|
| `do(action="Launch", app="xxx")` | ✅ `_handle_launch` | 完整 |
| `do(action="Tap", element=[x,y])` | ✅ `_handle_tap` | 完整 |
| `do(action="Tap", element=[x,y], message="重要操作")` | ✅ `_handle_tap`（敏感路径） | 完整 |
| `do(action="Type", text="xxx")` | ✅ `_handle_type` | 完整 |
| `do(action="Type_Name", text="xxx")` | ✅ `_handle_type`（别名） | 完整 |
| `do(action="Interact")` | ⚠️ `_handle_interact` | **占位**（只返回 message，无实际交互） |
| `do(action="Swipe", start=[x1,y1], end=[x2,y2])` | ✅ `_handle_swipe` | 完整 |
| `do(action="Note", message="True")` | ⚠️ `_handle_note` | **占位**（noop） |
| `do(action="Call_API", instruction="xxx")` | ⚠️ `_handle_call_api` | **占位**（noop） |
| `do(action="Long Press", element=[x,y])` | ✅ `_handle_long_press` | 完整 |
| `do(action="Double Tap", element=[x,y])` | ✅ `_handle_double_tap` | 完整 |
| `do(action="Take_over", message="xxx")` | ✅ `_handle_takeover` | 完整 |
| `do(action="Back")` | ✅ `_handle_back` | 完整 |
| `do(action="Home")` | ✅ `_handle_home` | 完整 |
| `do(action="Wait", duration="x seconds")` | ✅ `_handle_wait` | 完整 |
| `finish(message="xxx")` | ✅ `execute` 直接处理 | 完整 |

3 个占位 handler 是二次开发的天然扩展点。

## 辅助函数：do / finish

`handler.py:390-399`：

```python
def do(**kwargs) -> dict[str, Any]:
    kwargs["_metadata"] = "do"
    return kwargs

def finish(**kwargs) -> dict[str, Any]:
    kwargs["_metadata"] = "finish"
    return kwargs
```

这两个 helper 用于**代码内构造动作 dict**（不走模型解析），主要用于错误兜底：

```python
# agent.py 拿到无法解析的模型回复时
action = finish(message=response.action)

# handler 执行抛异常时
result = self.action_handler.execute(finish(message=str(e)), ...)
```

## 常见陷阱

### 1. `print(f"Parsing action: {response}")` 是 debug 残留

`handler.py:345` 有一行 print，每次解析都打印原始响应。生产环境建议删掉或改成 `if verbose`。

### 2. Type 路径的字符串切分不健壮

`response.split("text=", 1)[1][1:-2]` 假设 text 一定是双引号包裹的。如果模型输出 `text='xxx'`（单引号）会切错。实践中模型总是用双引号，但值得注意。

### 3. 敏感操作只检测 Tap

只有 `Tap` 检测 `message` 字段触发 confirmation。如果模型输出 `do(action="Swipe", ..., message="删除")`，message 会被**忽略**。如果需要敏感 Swipe/Long Press，要在对应 handler 加同样的检查。

### 4. iOS 硬编码时间

`handler_ios.py` 的 `time.sleep(0.5)` 不受 `TIMING_CONFIG` 控制，调时间常量无效。如果要统一，需要把 iOS 版改成读 `TIMING_CONFIG`。

## 下一步

- 想加新动作 → [EXTENDING.md](EXTENDING.md#加新动作)
- 想改协议格式（如改用 JSON） → 改 `parse_action` + `_get_handler` + prompt
- 想了解设备底层命令 → [03-device-layer.md](03-device-layer.md)
- 想了解模型如何生成这些动作 → [05-model-client.md](05-model-client.md)

---
