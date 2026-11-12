# Open-AutoGLM 文件详解（ONBOARDING-DETAILS）

> 本文档对 [`ONBOARDING.md`](ONBOARDING.md) 中提到的所有文件做深度 `/understand-explain`。
> 按架构层组织，每个文件覆盖：**角色 / 内部结构 / 外部连接 / 数据流 / 模式与坑**。
> 配套：知识图谱 `.understand-anything/knowledge-graph.json`。

---

## 入口与 CLI 层

### `main.py`（853 行，complex）— 统一 CLI 入口

**角色**：用户与 Agent 之间的唯一入口。注册 `phone-agent` console_script（`setup.py:44-48`），等价于 `python main.py`。

**内部结构**（6 个模块级函数）：
- `check_system_requirements(device_type, wda_url)` — 启动前自检（37-269 行）
  - 3 步检查：工具装好（adb/hdc/idevice）→ 设备连上 → 平台特异组件（ADB Keyboard / WDA）
- `check_model_api(base_url, model_name, api_key)` — 模型服务探活（272-352 行）
  - 用真实 chat completion 而非 `/models` 列表（更普适）
- `parse_args()` — argparse 配置（355-524 行）
  - 4 类参数：模型（base-url/model/apikey/max-steps）/ 设备（device-id/connect/list-devices/enable-tcpip）/ iOS 专用（wda-url/pair/wda-status）/ 其他（quiet/list-apps/lang/task）
- `handle_ios_device_commands(args)` — iOS 子命令（527-599 行）
- `handle_device_commands(args)` — adb/hdc 子命令（602-681 行）
  - **`--connect` 特殊**：成功后返回 `not success`（False），让主流程继续
- `main()` — 主流程（684-850 行）

**主流程数据流**：
```
parse_args → set_device_type 全局 → --list-apps 出口 → handle_device_commands 出口
→ check_system_requirements → check_model_api → 实例化 PhoneAgent/IOSPhoneAgent
→ 打印 header → if task: agent.run(task) else: 交互模式循环
```

**外部连接**：
- imports：`phone_agent/__init__.py`、`agent.py`、`agent_ios.py`、`device_factory.py`、`model/__init__.py`、`xctest/__init__.py`、3 个 apps 模块
- 调用：`PhoneAgent(model_config, agent_config).run(task)` 或 `IOSPhoneAgent(...)`

**关键模式**：
- **iOS 跳过 `set_device_type`**（main.py:697-698 `if device_type != DeviceType.IOS`）—— iOS 不走 DeviceFactory，架构不一致的历史遗留
- **HDC verbose 自动开**（main.py:701-704）
- **交互模式每任务后调 `agent.reset()`** 清空上下文

**坑**：与 `ios.py` 90% 重叠，新手容易混淆该用哪个（推荐永远用 `main.py`）。

---

### `ios.py`（550 行，moderate）— iOS 独立 CLI（历史遗留）

**角色**：早期 iOS 单独开发时的入口，现在 `main.py --device-type ios` 已能做所有事。

**与 main.py 的差异**：
| 维度 | main.py | ios.py |
|------|---------|--------|
| 平台 | 三平台 | 仅 iOS |
| 检查 | `check_system_requirements(DeviceType.IOS, wda_url)` | 独立的 `check_system_requirements(wda_url)`（无 device_type 参数） |
| 设备子命令 | 在 `handle_ios_device_commands` | 直接写在 main() 里 |

**外部连接**：imports `agent_ios.py`、`config/apps_ios.py`、`model/__init__.py`、`xctest/__init__.py`。

**坑**：`check_model_api` 函数定义存在但**被注释掉不调用**（ios.py 第 ~399 行 `# if not check_model_api(...)`），与 main.py 不一致。

**建议**：从仓库删除或加 deprecation warning。

---

### `examples/basic_usage.py`（190 行，simple）— Python API 用法示例

**角色**：演示 `phone_agent` 包的 5 种典型用法。

**5 个 example 函数**：
1. `example_basic_task(lang)` — 最小可运行：ModelConfig + AgentConfig + PhoneAgent.run
2. `example_with_callbacks(lang)` — 注入 confirmation_callback + takeover_callback
3. `example_step_by_step(lang)` — 用 step() 逐步调试，每步打印 thinking
4. `example_multiple_tasks(lang)` — 循环跑多任务，每任务后 `agent.reset()`
5. `example_remote_device(lang)` — 远程设备：ADBConnection.connect + device_id 指定

**外部连接**：imports `phone_agent/__init__.py`、`agent.py`、`config/__init__.py`、`model/__init__.py`。

**模式**：默认 `__main__` 只跑 example 1，其他注释掉（避免新手一次跑太多）。

---

### `examples/demo_thinking.py`（64 行，simple）— verbose 模式最小 demo

**角色**：演示 verbose=True 时 Agent 怎么打印 thinking + action。

**结构**：单 `main(lang)` 函数，配置 ModelConfig（temperature=0.1，注意与项目默认 0.0 不同）+ AgentConfig（max_steps=10, verbose=True），跑 `agent.run("打开小红书搜索美食攻略")`。

**外部连接**：同 basic_usage.py。

---

### `scripts/check_deployment_cn.py`（115 行，simple）+ `_en.py`（129 行）— 部署验证

**角色**：发非流式 chat completion 请求验证模型服务可达性。中英文版本结构相同，只是默认 messages 文件不同。

**关键流程**：
1. 解析 CLI（`--base-url` / `--model` / `--apikey` / `--messages-file` / `--max-tokens` / `--temperature` / `--top_p` / `--frequency_penalty`）
2. 加载 `sample_messages.json`（含完整 system prompt + 一张截图 base64 + 任务）
3. `OpenAI(base_url, api_key).chat.completions.create(..., stream=False)` — **非流式**（与 ModelClient 的 stream=True 不同）
4. 打印模型回复 + token 统计（prompt/completion/total）
5. 异常时打印错误类型 + 排查提示

**判定标准**：thinking 有多步规划逻辑 + action 是合法 `do(...)`/`finish(...)` 格式 = 部署成功。

**外部连接**：依赖 `openai` SDK + sample_messages.json（不依赖 phone_agent 包本身）。

---

## Agent 核心层

### `phone_agent/__init__.py`（12 行，simple）— 包入口

**角色**：导出顶层 API。

```python
from phone_agent.agent import PhoneAgent
from phone_agent.agent_ios import IOSPhoneAgent
__version__ = "0.1.0"
__all__ = ["PhoneAgent", "IOSPhoneAgent"]
```

**外部连接**：imports `agent.py` + `agent_ios.py`。

---

### `phone_agent/agent.py`（253 行，complex）★ — PhoneAgent 主类

**角色**：项目心脏。编排感知-动作循环。

**内部结构**：
- `class AgentConfig`（dataclass，16-28 行）— max_steps/device_id/lang/system_prompt/verbose，`__post_init__` 默认调 `get_system_prompt(lang)`
- `class StepResult`（dataclass，31-39 行）— success/finished/action/thinking/message
- `class PhoneAgent`（42-252 行）— 主类
  - `__init__(model_config, agent_config, confirmation_callback, takeover_callback)` — 组合 ModelClient + ActionHandler
  - `run(task) -> str`（84-110 行）— 一次性跑完，自动重置 _context，循环到 finish 或 max_steps
  - `step(task?) -> StepResult`（112-129 行）— 单步调试，不循环
  - `reset()`（131-134 行）— 清空 _context + _step_count
  - `_execute_step(user_prompt, is_first) -> StepResult`（136-243 行）— **6 段心脏**
  - `@property context` / `@property step_count`（246-253 行）

**`_execute_step` 6 段数据流**：
```
段 1 (136-145): 截图 + 当前 app
  device_factory = get_device_factory()
  screenshot = device_factory.get_screenshot(device_id)
  current_app = device_factory.get_current_app(device_id)

段 2 (147-169): 组装消息
  if is_first: 注入 system + 带 task 的 user message
  else: 只带 screen info

段 3 (171-187): 调模型 + 实时打印 thinking
  print("💭 thinking:")  # 标头先打,ModelClient 流式打印内容
  response = model_client.request(context)
  异常 → finished=True 直接终止

段 4 (189-202): 解析动作
  action = parse_action(response.action)
  异常 → action = finish(message=response.action)  # 兜底

段 5 (204-217): 图片清理 + 动作执行
  ★ self._context[-1] = remove_images_from_message(self._context[-1])  # 省 token 关键
  result = action_handler.execute(action, screenshot.width, screenshot.height)
  异常 → result = execute(finish(message=str(e)), ...)  # 兜底

段 6 (219-243): 回填上下文 + 终止判断
  self._context.append(create_assistant_message(f"<think>{response.thinking}</think><answer>{response.action}</answer>"))
  finished = action._metadata == "finish" or result.should_finish
```

**外部连接**：
- imports：`ActionHandler`、`parse_action/do/finish`、`get_messages/get_system_prompt`、`get_device_factory`、`ModelClient/ModelConfig`、`MessageBuilder`
- calls：`ModelClient.request`、`ActionHandler.execute`、`DeviceFactory.get_screenshot/get_current_app`、`parse_action`

**关键模式**：
- **图片一次性消费**（205 行）—— 每步模型回复后立即剥掉历史截图，省 token 80%+
- **双层异常兜底**（模型异常段 3 + 执行异常段 5 都转成 finish）
- **assistant message XML 包裹**（即使模型输出裸 `do(...)` 也重新包成 `<think>...</think><answer>...</answer>`，保持上下文格式一致）

---

### `phone_agent/agent_ios.py`（277 行，complex）— IOSPhoneAgent

**角色**：iOS 版 PhoneAgent，与 agent.py 重复度约 90%。

**关键差异**（vs PhoneAgent）：
1. **构造时自动创建 WDA session**（83-90 行）：
   ```python
   if self.agent_config.session_id is None:
       success, session_id = self.wda_connection.start_wda_session()
   ```
2. **设备访问绕过 DeviceFactory**（161-168 行）：直接调 `xctest.get_screenshot(wda_url, session_id, device_id)` 和 `xctest.get_current_app(wda_url, session_id)`
3. **持 IOSActionHandler** 而非 ActionHandler
4. **重复打印 thinking bug**（219-222 行）：在 `print("💭 thinking:")` 头之后又 `print(response.thinking)`——但 ModelClient 流式过程已经实时打印过，会重复。修复：删 222 行

**外部连接**：
- imports：`IOSActionHandler`、`ActionHandler`、`do/finish/parse_action`、`get_messages/get_system_prompt`、`ModelClient/MessageBuilder`、`xctest/*`

---

### `phone_agent/device_factory.py`（167 行，simple）— DeviceFactory

**角色**：adb/hdc 的统一调度工厂 + 全局单例。

**内部结构**：
- `class DeviceType(Enum)`（7-12 行）— ADB/HDC/IOS 三值
- `class DeviceFactory`（15-144 行）
  - `__init__(device_type)` — 存类型，_module=None
  - `@property module`（33-46 行）— lazy-load adb 或 hdc，**iOS raise ValueError**（44-45 行）
  - 14 个纯转发方法：`get_screenshot/get_current_app/tap/double_tap/long_press/swipe/back/home/launch_app/type_text/clear_text/detect_and_set_adb_keyboard/restore_keyboard/list_devices/get_connection_class`
- `set_device_type(device_type)`（146-153 行）— 设全局单例
- `get_device_factory() -> DeviceFactory`（157-167 行）— 取全局单例，默认 ADB

**外部连接**：
- 被 main.py 调用 `set_device_type` 设全局
- 被 agent.py 调用 `get_device_factory().get_screenshot/get_current_app`
- 被 handler.py 调用所有 14 个转发方法

**架构债**：iOS 不走此工厂是历史遗留，详见 EXTENDING.md 的 Protocol 重构建议。

---

## 动作执行层

### `phone_agent/actions/__init__.py`（5 行，simple）

```python
from phone_agent.actions.handler import ActionHandler, ActionResult
__all__ = ["ActionHandler", "ActionResult"]
```

---

### `phone_agent/actions/handler.py`（399 行，complex）★ — ActionHandler + parse_action

**角色**：Agent 决策 → 设备执行的桥梁。

**内部结构**：
- `@dataclass ActionResult`（14-21 行）— success/should_finish/message/requires_confirmation
- `class ActionHandler`（24-329 行）
  - `__init__(device_id, confirmation_callback, takeover_callback)` — callbacks 默认是 input()
  - `execute(action, screen_width, screen_height) -> ActionResult`（45-88 行）— 三层调度：finish/do/unknown
  - `_get_handler(action_name) -> Callable`（90-108 行）— **14 项 handler 字典**
  - `_convert_relative_to_absolute(element, w, h) -> (x, y)`（110-116 行）— `[0-1000]` 相对值 → pixels
  - 14 个 `_handle_*` 方法（118-257 行）：
    - `_handle_launch`（118）/`_handle_tap`（130，**含敏感操作 confirmation 检查**）/`_handle_type`（151，**4 个 delay**）/`_handle_swipe`（175）/`_handle_back`（190）/`_handle_home`（196）/`_handle_double_tap`（202）/`_handle_long_press`（213）/`_handle_wait`（224）/`_handle_takeover`（235）/`_handle_note`（241，**noop 占位**）/`_handle_call_api`（247，**noop 占位**）/`_handle_interact`（253，**noop 占位**）
  - `_send_keyevent(keycode)`（258-318 行）— **死代码**！HDC keycode 映射，但无人调用
  - `_default_confirmation/@staticmethod`（321-325 行）— `input("Y/N")`
  - `_default_takeover/@staticmethod`（327-329 行）— `input("Enter to continue")`
- `def parse_action(response: str) -> dict`（332-388 行）★ — **模块级函数**，三路径解析
- `def do(**kwargs)` / `def finish(**kwargs)`（390-399 行）— 辅助构造函数

**`parse_action` 三路径**（332-388 行）：
```
路径 A (Type 特殊): if startswith('do(action="Type"'):
  text = response.split("text=", 1)[1][1:-2]   # 字符串切分,处理特殊字符
路径 B (其他 do): if startswith("do"):
  response.replace('\n', '\\n')...  # 转义换行
  tree = ast.parse(response, mode="eval")  # AST 解析
  for keyword in call.keywords:
    action[keyword.arg] = ast.literal_eval(keyword.value)
路径 C (finish): if startswith("finish"):
  message = response.replace("finish(message=", "")[1:-2]
```

**外部连接**：
- imports：`TIMING_CONFIG`、`get_device_factory`
- 被 agent.py 调用 `parse_action(response.action)` + `action_handler.execute(...)`
- calls `device_factory.tap/swipe/launch_app/...`

**坑**：
- **`handler.py:345` 有 debug print 残留**：`print(f"Parsing action: {response}")`，生产建议删
- Type 路径的 `split("text=", 1)[1][1:-2]` 假设 text 双引号包裹，模型用单引号会错
- 只有 Tap 检测 `message` 字段触发 confirmation，Swipe/Long Press 不会

---

### `phone_agent/actions/handler_ios.py`（280 行，moderate）— IOSActionHandler

**角色**：iOS 版 ActionHandler，直接调 xctest 模块（绕过 DeviceFactory）。

**关键差异**（vs ActionHandler）：
- `__init__(wda_url, session_id, device_id, confirmation_callback, takeover_callback)` — 多 wda_url + session_id
- 不调 `device_factory.tap(...)`，改调 `xctest.tap(x, y, wda_url, session_id, ...)`
- **硬编码 time.sleep(0.5)**，不受 TIMING_CONFIG 控制（架构债）
- 长按 duration 硬编码 `3.0` 秒
- back 用 WDA 左边缘手势滑动（无按键）
- type 流程简化：clear → type → hide_keyboard（无 IME 切换）
- **无 `_send_keyevent` 死代码**

**外部连接**：imports `xctest/__init__.py` + `xctest/input.py`。

---

## AI 模型客户端层

### `phone_agent/model/__init__.py`（5 行，simple）

```python
from phone_agent.model.client import ModelClient, ModelConfig
__all__ = ["ModelClient", "ModelConfig"]
```

注意：**未导出 ModelResponse 和 MessageBuilder**，被 agent.py 从 `model.client` 子模块直接 import。

---

### `phone_agent/model/client.py`（290 行，complex）★ — ModelClient 流式 + MessageBuilder

**角色**：与 OpenAI 兼容 VLM 服务通信，流式接收 + 实时分离 thinking/action。

**内部结构**：
- `@dataclass ModelConfig`（13-25 行）— base_url/api_key/model_name=autoglm-phone-9b/max_tokens=3000/temperature=0.0/top_p=0.85/frequency_penalty=0.2/extra_body/lang
- `@dataclass ModelResponse`（28-38 行）— thinking/action/raw_content + 3 项性能指标（time_to_first_token/time_to_thinking_end/total_time）
- `class ModelClient`（41-217 行）
  - `__init__(config)` — 创建 `OpenAI(base_url, api_key)` 客户端
  - `request(messages) -> ModelResponse`（53-174 行）★ — **4 段流式**
  - `_parse_response(content) -> (thinking, action)`（176-217 行）— **4 条规则**
- `class MessageBuilder`（219-289 行）— 5 个 staticmethod
  - `create_system_message(content)` — `{"role":"system","content":...}`
  - `create_user_message(text, image_base64=None)` — **图前文后**（VLM 偏好）
  - `create_assistant_message(content)` — `{"role":"assistant","content":...}`
  - `remove_images_from_message(message)` — 剥掉 image_url，只留 text（**图片一次性消费关键**）
  - `build_screen_info(current_app, **extra_info)` — JSON 字符串 `{"current_app":"..."}`

**`request` 4 段算法**（核心难点）：
```
段 1 (53-80): 发起流式请求
  stream = client.chat.completions.create(..., stream=True)

段 2 (82-140): ★ 带缓冲的 marker 检测器（最绕的部分）
  action_markers = ["finish(message=", "do(action="]
  buffer = ""
  in_action_phase = False

  for chunk in stream:
    content = chunk.choices[0].delta.content
    raw_content += content
    if in_action_phase: continue   # 已进 action 阶段,只累积不打印

    buffer += content
    # 检测完整 marker
    for marker in action_markers:
      if marker in buffer:
        print(buffer.split(marker)[0])  # 打印 thinking 部分
        in_action_phase = True
        break

    # 检测 marker 前缀（如 buffer 末尾是 "do(ac"）
    is_potential_marker = ...
    if not is_potential_marker:
      print(buffer)  # 安全打印
      buffer = ""

段 3 (142-146): 解析
  thinking, action = self._parse_response(raw_content)

段 4 (148-174): 打印性能指标 + 返回 ModelResponse
```

**`_parse_response` 4 条规则**（176-217 行）：
```
规则 1 (优先): if "finish(message=" in content → 按 finish 切分
规则 2: if "do(action=" in content → 按 do 切分
规则 3 (fallback): if "<answer>" in content → XML 标签切分（legacy）
规则 4: 全部当 action，thinking=""
```

**协议演进洞察**：prompt（`prompts_zh.py`）要求 `<think>/<answer>` XML，但 parser 优先匹配裸 `do(...)/finish(...)`。**模型已演化为直接输出函数调用，prompt 描述滞后**。

**外部连接**：
- imports：`openai.OpenAI`、`get_message`（i18n）
- 被 agent.py / agent_ios.py 调用 `request(context)`
- calls `OpenAI.chat.completions.create`

**坑**：
- `base_url` 必须以 `/v1` 结尾（少了 404）
- `model_name` 必须与服务端 `--served-model-name` 完全一致（区分大小写）
- 性能指标打印**无法关闭**（不受 verbose 控制），如需静默要改 client.py:148-165

---

## 设备抽象层

### `phone_agent/device_factory.py`（见上文 Agent 核心层）

---

## Android 平台层（adb/）

5 个文件，全部用 subprocess 调 `adb shell`，**无状态**。

### `phone_agent/adb/__init__.py`（51 行，simple）— 统一接口导出

导出 4 类共 17 个名字：
- 截图：`get_screenshot`
- 输入：`type_text/clear_text/detect_and_set_adb_keyboard/restore_keyboard`
- 设备控制：`get_current_app/tap/swipe/back/home/double_tap/long_press/launch_app`
- 连接管理：`ADBConnection/DeviceInfo/ConnectionType/quick_connect/list_devices`

---

### `phone_agent/adb/connection.py`（353 行，moderate）— ADBConnection

**内部结构**：
- `class ConnectionType(Enum)` — USB/WIFI/REMOTE
- `@dataclass DeviceInfo` — device_id/status/connection_type/model/android_version
- `class ADBConnection`：
  - `connect(address)` — `adb connect ip:port`
  - `disconnect(address|None)` — `adb disconnect [addr]`
  - `list_devices()` — `adb devices -l` 解析
  - `is_connected(device_id)` / `get_device_info(device_id)`
  - `enable_tcpip(port, device_id)` — `adb tcpip 5555`（USB→WiFi 转换）
  - `get_device_ip(device_id)` — `adb shell ip route` / `ip addr show wlan0` 解析
  - `restart_server()` — `adb kill-server` + `adb start-server`
- 模块级 `quick_connect(address)` / `list_devices()` 辅助

**外部连接**：imports `TIMING_CONFIG`（用 `adb_restart_delay` + `server_restart_delay`）。

---

### `phone_agent/adb/device.py`（252 行，moderate）— Android 设备控制

**关键命令对照**：
| 操作 | adb 命令 |
|------|---------|
| 点击 | `adb shell input tap x y` |
| 双击 | 两次 `input tap` + `double_tap_interval` 间隔 |
| 长按 | `input swipe x y x y duration_ms`（同点 swipe 模拟） |
| 滑动 | `input swipe sx sy ex ey duration_ms` |
| 返回 | `input keyevent 4` |
| Home | `input keyevent KEYCODE_HOME` |
| 启动 app | `monkey -p package -c android.intent.category.LAUNCHER 1` |
| 当前 app | `dumpsys window` 解析 mCurrentFocus |

**关键模式**：每个动作后 `time.sleep(delay)`，delay 默认从 `TIMING_CONFIG.device.default_*_delay` 取。

**外部连接**：imports `APP_PACKAGES`（查 package name）+ `TIMING_CONFIG`。

---

### `phone_agent/adb/input.py`（109 行，moderate）— ADB Keyboard 文本输入

**Android 中文输入最复杂**：需第三方 [ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard) APK。

**核心机制**：
```python
# type_text
encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
subprocess.run(["adb", "shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", encoded])

# clear_text
subprocess.run(["adb", "shell", "am", "broadcast", "-a", "ADB_CLEAR_TEXT"])

# detect_and_set_adb_keyboard
# 1. settings get secure default_input_method  读当前 IME
# 2. if 不是 ADB Keyboard: ime set com.android.adbkeyboard/.AdbIME
# 3. type_text("") 热身键盘
# 4. return 原 IME 供恢复

# restore_keyboard(ime)
# ime set <ime>
```

---

### `phone_agent/adb/screenshot.py`（109 行，simple）— Android 截图

**两步截图**：
```python
# 1. 截屏到设备
subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/tmp.png"])
# 2. pull 到本地
subprocess.run(["adb", "pull", "/sdcard/tmp.png", temp_path])
```

**敏感页面检测**：检查 `"Status: -1" in output or "Failed" in output`，返回黑图 + `is_sensitive=True` 触发 takeover。

**fallback 分辨率**：1080×2400。

**外部连接**：imports `PIL.Image` 转 PNG。

---

## HarmonyOS 平台层（hdc/）

5 个文件，结构与 adb/ 完全平行（重复度 80%+），用 subprocess 调 `hdc shell uitest uiInput`。**原生支持中文输入，无需 ADB Keyboard**。

### `phone_agent/hdc/__init__.py`（53 行，simple）— 统一接口导出

结构与 `adb/__init__.py` 相同，多导出 `set_hdc_verbose`。

---

### `phone_agent/hdc/connection.py`（381 行，moderate）— HDCConnection

**与 ADBConnection 几乎相同**，差异：
- 命令前缀：`adb` → `hdc`，`-s` → `-t`
- `connect` → `tconn`，`disconnect` → `tdisconn`
- `enable_tcpip` → `tmode port`
- `list_devices` → `hdc list targets`
- `_run_hdc_command` 辅助函数（含 verbose 模式）
- DeviceInfo 字段：`harmony_version`（vs adb 的 `android_version`）

**外部连接**：imports `TIMING_CONFIG`。

---

### `phone_agent/hdc/device.py`（310 行，moderate）— HarmonyOS 设备控制

**关键命令对照**（与 Android 差异）：
| 操作 | hdc 命令 |
|------|---------|
| 点击 | `uitest uiInput click x y` |
| 双击 | `uitest uiInput doubleClick x y` |
| 长按 | `uitest uiInput longClick x y`（注意：可能不支持 duration） |
| 滑动 | `uitest uiInput swipe sx sy ex ey duration` |
| 返回 | `uitest uiInput keyEvent Back` ★ **非 KEYCODE_BACK** |
| Home | `uitest uiInput keyEvent Home` |
| 启动 app | `aa start -b bundle -a ability` ★ **需 ability 双重查找** |
| 当前 app | `aa dump -l` 解析 `state #FOREGROUND` + `app name [bundle]` |

**ability 双重查找**（281-282 行）：
```python
ability = APP_ABILITIES.get(bundle, "EntryAbility")  # 默认 EntryAbility
```

**外部连接**：imports `APP_PACKAGES` + `APP_ABILITIES` + `TIMING_CONFIG` + `_run_hdc_command`。

---

### `phone_agent/hdc/input.py`（149 行，simple）— HarmonyOS 文本输入

**原生支持中文**，无需 ADB Keyboard。

**核心命令**：
```python
# type_text（单行）
subprocess.run(["hdc", "shell", "uitest", "uiInput", "text", escaped_text])

# type_text（多行）★ ADB 不支持多行
for line in text.split('\n'):
    uitest uiInput text line
    if not last: uitest uiInput keyEvent 2054  # ENTER

# clear_text
uitest uiInput keyEvent 2072 2017  # Ctrl+A
uitest uiInput keyEvent 2055        # Delete

# detect_and_set_adb_keyboard  ★ noop 占位（HarmonyOS 不需要切换 IME）
# 只读当前 IME 返回,不切换
```

**特殊字符转义**：`"` → `\"`，`$` → `\$`。

---

### `phone_agent/hdc/screenshot.py`（125 行，simple）— HarmonyOS 截图

**双方法尝试**（HDC 版本差异）：
```python
# 方法 1: snapshot_display -f /tmp.jpeg（或 screenshot）
hdc shell snapshot_display -f /data/local/tmp/tmp_screenshot.jpeg
# 方法 2: screenshot 命令
hdc shell screenshot /data/local/tmp/tmp_screenshot.jpeg

# pull 到本地（hdc file recv）
hdc file recv /data/local/tmp/tmp_screenshot.jpeg temp_path

# PIL 转 JPEG→PNG
img = Image.open(temp_path)
img.save(buffered, format="PNG")
```

**敏感检测**：`"fail"/"error"/"not found" in output`。

**fallback 分辨率**：1080×2400。

**外部连接**：imports `PIL.Image` + `_run_hdc_command`。

---

## iOS 平台层（xctest/）

5 个文件，**差异最大**：用 HTTP 调 WebDriverAgent（WDA）+ subprocess 调 `idevice*` 工具。**有状态**（WDA session）。

### `phone_agent/xctest/__init__.py`（47 行，simple）— 统一接口导出

**关键差异**：所有函数签名多 `wda_url` + `session_id` 参数。导出 `XCTestConnection`（vs ADBConnection/HDCConnection）。

---

### `phone_agent/xctest/connection.py`（382 行，complex）★ — XCTestConnection

**iOS 独有功能**：
- `is_wda_ready(timeout)` — `GET /status` 探活
- `start_wda_session() -> (success, session_id)` — `POST /session` 创建会话（**有状态**！）
- `get_wda_status() -> dict` — `GET /status` 详细信息（含 sessionId/build time/currentApp）
- `pair_device(device_id) -> (success, msg)` — `idevicepair pair`
- `restart_wda() -> (success, msg)` ★ **名字误导**：实际只检查状态，提示用户在 Xcode 手动重启
- `get_device_name(device_id)` — `ideviceinfo -k DeviceName`

**未实现的**（adb/hdc 有但 iOS 无）：connect/disconnect/enable_tcpip（HTTP 无连接概念）。

**外部连接**：imports `requests`（HTTP）+ subprocess 调 `idevice_id/ideviceinfo/idevicepair`。

---

### `phone_agent/xctest/device.py`（458 行，complex）★ **最大单文件**

**WDA Actions API**（多步 pointer 事件）：
```python
# tap 的实际实现（约 100 行）
actions = {
    "type": "pointerMove", "duration": 0, "x": x / SCALE_FACTOR, "y": y / SCALE_FACTOR
}, {
    "type": "pointerDown", "buttonIndex": 0
}, {
    "type": "pause", "duration": 0.5
}, {
    "type": "pointerUp", "buttonIndex": 0
}
POST /session/{id}/actions {"actions": [...]}
```

**SCALE_FACTOR 缩放**（line 9）：
```python
SCALE_FACTOR = 3  # 物理像素 → 逻辑 points
```

**使用点**：105, 154, 212（pointerMove）+ 267-270（swipe 的 fromX/Y toX/Y）。

**已知 bug**：硬编码 3，对 1x（老 iPhone）/2x（iPhone SE/8、iPad mini）设备会算错坐标。正确做法是从 `GET /session/{id}/window/size` 动态计算。

**其他命令**：
- `tap(x, y, wda_url, session_id, delay)` — Actions API
- `swipe(sx, sy, ex, ey, duration, wda_url, session_id, delay)` — `/wda/dragfromtoforduration`
- `back(wda_url, session_id, delay)` — **左边缘手势滑动**（无按键）
- `home(wda_url, session_id, delay)` — `POST /wda/homescreen`
- `launch_app(app_name, wda_url, session_id, delay)` — `POST /wda/apps/launch {"bundleId": ...}`
- `get_current_app(wda_url, session_id)` — `GET /wda/activeAppInfo`

**外部连接**：imports `APP_PACKAGES_IOS as APP_PACKAGES`（line 7 别名）。

---

### `phone_agent/xctest/input.py`（299 行，moderate）— iOS 文本输入

**核心**：`POST /wda/keys` 逐字符发送。

```python
# type_text（line 26-62）
url = f"{wda_url}/session/{session_id}/wda/keys"
requests.post(url, json={"value": list(text), "frequency": frequency})
# frequency=60 默认（每秒 60 字符）

# clear_text（line 64-104）
# 找到 active element → clear
POST /session/{id}/element/active → element_id
POST /session/{id}/element/{eid}/clear
```

**6 个未导出函数**（被 IOSActionHandler 直接 import）：
| 函数 | 行号 | 作用 |
|------|------|------|
| `send_keys(keys: list[str])` | 137 | 逐字符发送 |
| `press_enter()` | 167 | 发 `\n` |
| `hide_keyboard()` | 184 | `POST /wda/keyboard/dismiss` |
| `is_keyboard_shown() -> bool` | 208 | `GET /wda/keyboard/shown` |
| `set_pasteboard(text)` | 241 | 写剪贴板 |
| `get_pasteboard() -> str` | 271 | 读剪贴板 |

**外部连接**：imports `requests`。

---

### `phone_agent/xctest/screenshot.py`（230 行，moderate）— iOS 截图

**双 fallback（最健壮）**：
```python
def get_screenshot(wda_url, session_id, device_id, timeout):
    # 1. 尝试 WDA HTTP
    screenshot = _get_screenshot_wda(wda_url, session_id, timeout)
    if screenshot: return screenshot

    # 2. fallback 到 idevicescreenshot CLI（libimobiledevice）
    screenshot = _get_screenshot_idevice(device_id, timeout)
    if screenshot: return screenshot

    # 3. 都失败 → 黑图
    return _create_fallback_screenshot(is_sensitive=False)
```

**WDA 路径**：`GET /screenshot` → JSON `{"value": "<base64>"}`

**idevicescreenshot 路径**：`subprocess.run(["idevicescreenshot", "-u", device_id, temp_path])` → PIL 读

**fallback 分辨率**：1179×2556（iPhone 14 Pro，比 adb/hdc 的 1080×2400 大）。

---

## 配置层（config/）

### `phone_agent/config/__init__.py`（53 行，simple）— 包导出 + 路由

**导出 15 个名字**（`__all__`，37-53 行）：
- 应用映射：`APP_PACKAGES`（Android）、`APP_PACKAGES_IOS`（iOS）
- Prompt：`SYSTEM_PROMPT`、`SYSTEM_PROMPT_ZH`、`SYSTEM_PROMPT_EN`、`get_system_prompt(lang)`
- i18n：`get_messages(lang)`、`get_message(key, lang)`
- Timing：`TIMING_CONFIG`、`TimingConfig`、`ActionTimingConfig`、`DeviceTimingConfig`、`ConnectionTimingConfig`、`get_timing_config()`、`update_timing_config()`

**`get_system_prompt(lang)` 路由**（line 19-31）：
```python
if lang == "en": return SYSTEM_PROMPT_EN
return SYSTEM_PROMPT_ZH  # 默认中文（向后兼容）
```

**导出缺口**：`apps_harmonyos.py` 的 `APP_PACKAGES` 和 `APP_ABILITIES` **未在 __init__.py 导出**——hdc 层直接从子模块 import。三平台地位不平等。

---

### `phone_agent/config/apps.py`（226 行，simple）— Android 应用映射

**168 个 app**：中文名 → Android package name。

**样本**：
```python
APP_PACKAGES = {
    "微信": "com.tencent.mm",
    "小红书": "com.xingin.xhs",
    "淘宝": "com.taobao.taobao",
    "Chrome": "com.android.chrome",
    "chrome": "com.android.chrome",          # ★ 容错变体
    "Google Chrome": "com.android.chrome",   # ★ 容错变体
    "google chrome": "com.android.chrome",   # ★ 容错变体
    # ... 168 项
}
```

**容错设计**：大量大小写/空格/连字符变体指向同一包名（处理模型输出的不同写法）。

**查询函数**：`get_package_name(app_name)`、`get_app_name(package)`、`list_supported_apps()`。

---

### `phone_agent/config/apps_harmonyos.py`（266 行，simple）— HarmonyOS 应用映射

**154 个 app + APP_ABILITIES 39 项**。

**两字典**：
```python
APP_PACKAGES = { "微信": "com.tencent.wechat", ... }  # 154 项
APP_ABILITIES = { "cn.wps.mobileoffice.hap": "DocumentAbility", ... }  # 39 项
```

**HarmonyOS 启动 app 需双重查找**：bundle name + ability name（默认 EntryAbility）。

**22 条注释掉的条目**：从 apps.py 复制后验证失败的遗留（应清理）。

---

### `phone_agent/config/apps_ios.py`（339 行，moderate）— iOS 应用映射

**182 个 app** + 3 个独有 iTunes API 函数。

**3 个独有函数**（line 243-339）：
- `check_app_installed(app_name, wda_url)` — iTunes Lookup API 检查 app 是否存在
- `get_app_info_from_itunes(bundle_id)` — 用 bundle ID 查 iTunes
- `get_app_info_by_id(app_store_id)` — 用 App Store 数字 ID 查

调 `https://itunes.apple.com/lookup`，依赖 `requests`（延迟 import）。

---

### `phone_agent/config/prompts_zh.py`（77 行，simple）— 中文 system prompt

**~1200 token**。结构：
- 5-8 行：日期注入（动态今天 + 星期几）
- 14 行：角色定义"你是一个智能体分析专家"
- 15-21 行：输出格式 `<think>{think}</think><answer>{action}</answer>`
- 23-55 行：**15 种动作**（Launch/Tap/Tap+message/Type/Type_Name/Interact/Swipe/Note/Call_API/Long Press/Double Tap/Take_over/Back/Home/Wait + finish）
- 57-75 行：**18 条硬性规则**（导航/等待/搜索/购物车/外卖/游戏/死循环防护等领域知识）

**协议演进脱节**：要求 XML 包裹，但 `client.py:_parse_response` 优先匹配裸 `do(...)`。

---

### `phone_agent/config/prompts_en.py`（79 行，simple）— 英文 system prompt

**~650 token**。是 prompts_zh 的精简版：
- **7 种动作**（Tap/Type/Swipe/Long Press/Launch/Back/Finish）
- **3 条通用规则**

缺少中文版的领域特定策略（购物车、外卖等）。

---

### `phone_agent/config/prompts.py`（75 行，simple）⚠ **遗留废弃**

与 prompts_zh.py 95% 相同，唯一区别：日期格式无星期（line 6 `today.strftime("%Y年%m月%d日")`）。

**无人 import**（grep 确认零引用），应删除。

---

### `phone_agent/config/i18n.py`（81 行，simple）— UI 消息国际化

**22 个 key × 中/英**。

**关键 key**：`thinking`、`action`、`task_completed`、`done`、`step`、`task`、`result`、`performance_metrics`、`time_to_first_token`、`time_to_thinking_end`、`total_inference_time`、`confirmation_required`、`manual_operation_required` 等。

**两个函数**：
```python
def get_messages(lang="cn") -> dict:
    return MESSAGES_EN if lang == "en" else MESSAGES_ZH

def get_message(key, lang="cn") -> str:
    return get_messages(lang).get(key, key)  # fallback 返回 key 本身
```

**用途定位**：**给 UI 终端显示，不影响模型行为**。
- 消费者：`agent.py:173`（thinking/action 标签）、`client.py:152-163`（性能指标标签）

---

### `phone_agent/config/timing.py`（167 行，moderate）— 时间常量配置

**4 个 dataclass 共 14 个常量**：

```
TimingConfig (组合根, 100-111)
├── action: ActionTimingConfig (4 个)
│   - keyboard_switch_delay (1.0s)
│   - text_clear_delay (1.0s)
│   - text_input_delay (1.0s)
│   - keyboard_restore_delay (1.0s)
├── device: DeviceTimingConfig (8 个)
│   - default_tap_delay (1.0s)
│   - default_double_tap_delay (1.0s)
│   - double_tap_interval (0.1s)
│   - default_long_press_delay (1.0s)
│   - default_swipe_delay (1.0s)
│   - default_back_delay (1.0s)
│   - default_home_delay (1.0s)
│   - default_launch_delay (1.0s)
└── connection: ConnectionTimingConfig (2 个)
    - adb_restart_delay (2.0s)
    - server_restart_delay (1.0s)
```

**双层配置**：每个 dataclass 的 `__post_init__` 从环境变量读 `PHONE_AGENT_*_DELAY`（如 `PHONE_AGENT_KEYBOARD_SWITCH_DELAY`）覆盖默认值。

**热更新**：`update_timing_config(action=None, device=None, connection=None)` 函数（129-156 行）。

**架构债**：iOS 版 `handler_ios.py` 硬编码 `time.sleep(0.5)`，**不消费 TIMING_CONFIG**，调时间常量对 iOS 无效。

---

## 配置文件

### `setup.py`（49 行，simple）— 包定义

```python
setup(
    name="phone-agent",
    version="0.1.0",
    author="Zhipu AI",
    description="AI-powered phone automation framework",
    url="https://github.com/yourusername/phone-agent",  # ⚠ 占位符未改
    python_requires=">=3.10",
    install_requires=["Pillow>=12.0.0", "openai>=2.9.0"],  # ⚠ 漏 requests
    extras_require={"dev": ["pytest", "black", "mypy", "ruff"]},  # ⚠ black+ruff 冲突
    entry_points={"console_scripts": ["phone-agent=main:main"]},
    license=Apache 2.0,
)
```

**已知 bug**：
1. `url` 占位符 `yourusername/phone-agent`（应改 `zai-org/Open-AutoGLM`）
2. `install_requires` 漏 `requests`（iOS 用户 `pip install phone-agent` 会 ImportError）
3. `extras_require["dev"]` 同时含 `black` 和 `ruff`（formatter 冲突，pre-commit 用 ruff-format）

---

### `requirements.txt`（20 行，simple）

```
Pillow>=12.0.0          # 截图处理
openai>=2.9.0           # OpenAI 兼容 API

# For iOS Support
requests>=2.31.0        # 调 WDA HTTP

# For Model Deployment (注释掉,按需启用)
# sglang>=0.5.6.post1
# vllm>=0.12.0
# transformers>=5.0.0rc0  # ★ 超前版本要求,与 vLLM/SGLang 协同需要

# Optional: for development (注释掉)
# pytest>=7.0.0 / pre-commit>=4.5.0 / black / mypy
```

**transformers 依赖冲突可忽略**（README 明示）。

---

### `.pre-commit-config.yaml`（23 行，simple）

**3 工具**：
- `ruff`（v0.11.7）— lint + import 排序（`--select I`）+ format
- `typos`（v1.32.0）— 拼写检查
- `pymarkdown`（v0.9.29）— Markdown 格式

**已知 YAML bug**（4-5 行）：
```yaml
exclude: '^phone_agent/config/apps\.py$'   # 第一个 exclude
exclude: '^README_en\.md$'                 # 第二个 exclude,覆盖前者
```
YAML 规范：相同 key 后者覆盖前者。**实际只排除 README_en.md，apps.py 仍被检查**。

修复：用正则 `|` 合并：`exclude: '^(phone_agent/config/apps\.py|README_en\.md)$'`

---

### `scripts/sample_messages.json` + `sample_messages_en.json`（各 20 行，simple）

OpenAI 格式消息数组，含：
- system message：完整 system prompt
- user message：text + **一张手机截图（base64）** + 任务指令（"小红书洗发水比价"）

被 `check_deployment_cn.py` / `_en.py` 加载，发非流式 chat completion 测模型服务。

---

### `.github/ISSUE_TEMPLATE/bug_report.yaml`（72 行）+ `feature-request.yaml`（34 行）

GitHub Issue 表单模板。bug_report 字段：System Info / Who can help / Information / Reproduction / Expected behavior。

---

### `.github/PULL_REQUEST_TEMPLATE.md`（40 行）

PR 模板。**小 bug**：第 31-39 行引用不存在的 `glmv-reward/` 目录（复制粘贴遗留，提 PR 时可忽略）。

---

## 文档层

### `README.md`（991 行）★ 主 README（中文）

含完整安装/部署/使用指南 + 面向 AI 的自动化部署章节。引用 AutoGLM（arXiv:2411.00820）+ MobileRL（arXiv:2509.18119）论文。

### `README_en.md`（933 行）— 英文 README

### `README_coding_agent.md`（430 行）— 面向 coding agent 的 README，指引 Claude Code/Cursor 通过 GLM Coding Plan 部署。

### `docs/README.md`（128 行）— 文档集索引页

含按目标/角色选文档的导航表、文档清单（含行数）、核心概念速查表、与 DeepWiki 的关系。

### `docs/ARCHITECTURE.md`（413 行）★ 总体架构

6 层架构视图 + mermaid 时序图 + 模块依赖图 + 5 个核心设计决策 + 与 DeepWiki 的 10 条勘误（全以源码为准）。

### `docs/EXTENDING.md`（552 行）★ 二次开发指南

加动作/平台/app/回调/prompt 语言/模型/step hook 的最小修改清单 + 统一设备抽象 Protocol 重构建议 + iOS 不走 DeviceFactory 的历史原因。

### `docs/01-entry-cli.md`（345 行）— 入口与 CLI

main.py 全流程 + 所有 CLI 参数 + 自检流程 + ios.py 历史遗留。

### `docs/02-agent-loop.md`（372 行）— PhoneAgent 核心

三层 API + _execute_step 六段拆解 + 上下文演化表 + iOS 差异 + 常见陷阱（5 个）。

### `docs/03-device-layer.md`（453 行）— 设备抽象层

DeviceFactory + adb/hdc/xctest 三套对照 + 平台能力矩阵 + 截图实现 + 输入法 + iOS 坐标缩放 + 代码重复度评估。

### `docs/04-action-handler.md`（408 行）— 动作执行器

AutoGLM 协议 + parse_action 三路径 + 14 种 handler + 坐标系 + iOS 版差异 + 与 prompt 对照表。

### `docs/05-model-client.md`（402 行）— 模型客户端

流式 marker 检测算法（带缓冲 + 前缀检测）+ _parse_response 四条规则 + 配置参数详解 + 换模型注意事项。

### `docs/06-config-prompts.md`（371 行）— 配置层

apps×3（共 504 app）+ prompts×3 + i18n（22 key）+ timing（14 常量）+ 添加 app/语言步骤。

### `docs/07-deployment.md`（432 行）— 模型部署完整指南

三种部署路径（API/vLLM/SGLang）+ 完整启动参数 + 验证脚本 + 故障排查 + 性能调优。

### `docs/08-development.md`（473 行）— 开发指南

setup.py 详解 + pre-commit + 测试现状 + PR 流程 + **10 项已知问题清单（贡献机会）**。

### `docs/09-remote-advanced.md`（547 行）— 远程与高级用法

三平台 WiFi 调试 + 交互模式 + **4 种回调实战**（Web UI / Slack / 日志 / 超时）+ 远程协助老人综合案例。

### `docs/ios_setup/ios_setup.md`（134 行）— iOS 环境配置

WebDriverAgent 部署 + 签名 + 设备信任 + iproxy 端口映射 + xcodebuild 命令行模式。

### `resources/WECHAT.md`（6 行）— 微信社区二维码资源

### `resources/privacy_policy.txt`（131 行）+ `privacy_policy_en.txt`（133 行）— 中英文隐私政策

---

## 完整性核查

本详解覆盖 ONBOARDING.md 中提到的所有文件：

| 类型 | 数量 | 覆盖 |
|------|------|------|
| Python 源码 | 41 | ✅ 全部 |
| 配置（.yaml/.json/.txt）| 7 | ✅ 全部 |
| 文档（.md）| 16 | ✅ 全部（含 docs/ 13 个 + 顶层 3 个 README）|
| 法律文档（.txt）| 2 | ✅ privacy_policy 中英文 |
| **总计** | **66** | **✅ 全覆盖** |

**对照 ONBOARDING.md 的 12 层架构**：
- ✅ 入口与 CLI 层（8 文件）
- ✅ Agent 核心层（3 .py + 4 class/concept，class/concept 在 .py 文件内解释）
- ✅ 动作执行层（3 .py + 4 class/concept）
- ✅ AI 模型客户端层（2 .py + 4 class）
- ✅ 设备抽象层（1 .py + 2 class，归入 Agent 核心层一起讲）
- ✅ Android 平台层（5 .py）
- ✅ HarmonyOS 平台层（5 .py）
- ✅ iOS 平台层（5 .py）
- ✅ 配置层（9 .py）
- ✅ 脚本与 CI 层（2 .py + 4 配置 + 1 .md）
- ✅ 示例层（2 .py）
- ✅ 文档层（13 .md + 3 .md/.txt）

**对照 ONBOARDING.md 的 Tour 12 步**：每步涉及的文件全部解释。

**对照 ONBOARDING.md 的 Complexity Hotspots**：6 个 complex 文件 + 5 个 complex class 全部带详细解释（标注 ★）。
