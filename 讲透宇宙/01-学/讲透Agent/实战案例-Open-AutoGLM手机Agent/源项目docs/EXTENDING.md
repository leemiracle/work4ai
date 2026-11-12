# 二次开发指南（EXTENDING）

> 本文档面向想**扩展 Open-AutoGLM** 的开发者。每节给出最小可工作的修改清单 + 代码骨架。
> 阅读前建议先看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解整体架构。

## 目录

- [加新动作](#加新动作)
- [加新设备平台](#加新设备平台)
- [加新 app](#加新-app)
- [加自定义回调](#加自定义回调)
- [加新 prompt 语言](#加新-prompt-语言)
- [换模型](#换模型)
- [加 step hook（如截图保存）](#加-step-hook)
- [统一设备抽象建议（架构改进）](#统一设备抽象建议)
- [为什么 iOS 不走 DeviceFactory](#为什么-ios-不走-devicefactory)

---

## 加新动作

**场景**：让 Agent 支持 `do(action="Scroll_To_End")` 这种新动作。

### 步骤 1：在 handler 注册新 handler 方法

`phone_agent/actions/handler.py` 的 `_get_handler` 字典加映射：

```python
def _get_handler(self, action_name: str) -> Callable | None:
    handlers = {
        # ...existing entries...
        "Scroll_To_End": self._handle_scroll_to_end,   # ★ 新增
    }
    return handlers.get(action_name)
```

### 步骤 2：实现 handler 方法

在 `ActionHandler` 类里加：

```python
def _handle_scroll_to_end(self, action: dict, width: int, height: int) -> ActionResult:
    """Scroll to the end of the current page (multiple swipes)."""
    device_factory = get_device_factory()

    # 反复下滑直到屏幕不再变化
    prev_screenshot = device_factory.get_screenshot(self.device_id).base64_data
    for _ in range(10):   # 最多 10 次
        device_factory.swipe(
            width // 2, int(height * 0.8),
            width // 2, int(height * 0.2),
            device_id=self.device_id
        )
        time.sleep(0.5)
        curr = device_factory.get_screenshot(self.device_id).base64_data
        if curr == prev_screenshot:
            return ActionResult(True, False, "Reached end of page")
        prev_screenshot = curr

    return ActionResult(True, False, "Max scroll iterations reached")
```

### 步骤 3：更新 prompt

`phone_agent/config/prompts_zh.py` 加描述：

```python
- do(action="Scroll_To_End")  
    滑动到页面底部。适用于需要加载更多内容的列表页。
```

`prompts_en.py` 对应加英文描述。

### 步骤 4（可选）：加 iOS 支持

如果 iOS 也要支持，在 `phone_agent/actions/handler_ios.py` 的 `IOSActionHandler` 加同样逻辑（用 `xctest.swipe` 替代 `device_factory.swipe`）。

### 步骤 5：测试

```python
from phone_agent.actions.handler import parse_action, ActionHandler

# 测试解析
action = parse_action('do(action="Scroll_To_End")')
assert action == {"_metadata": "do", "action": "Scroll_To_End"}

# 测试执行(需真机)
handler = ActionHandler(device_id="emulator-5554")
result = handler.execute(action, 1080, 2400)
print(result)
```

**完整例子**：完整 diff 见 git history 中添加 `Wait` 动作的 commit。

---

## 加新设备平台

**场景**：支持 Linux Desktop（用 `xdotool` / `gnome-screenshot`）。

### 设计决策：走 DeviceFactory 还是独立路径？

| 走 Factory（adb/hdc 模式） | 独立路径（iOS 模式） |
|--------------------------|-------------------|
| 适合：subprocess + 无状态命令 | 适合：HTTP API / 有状态协议 |
| 改动：`device_factory.py` 加分支 + 新建 `linux/` 目录 | 改动：新建 `LinuxAgent` + `LinuxActionHandler` |

Linux Desktop 走 subprocess（`xdotool`），适合**走 Factory 模式**。

### 步骤 1：新建 `phone_agent/linux/` 目录

参考 `phone_agent/adb/` 结构：

```
phone_agent/linux/
├── __init__.py      导出统一接口函数
├── connection.py    LinuxConnection 类（实际上没有"连接"概念,可简化）
├── device.py        tap/swipe/launch_app/get_current_app（用 xdotool）
├── input.py         type_text（用 xdotool type）
└── screenshot.py    get_screenshot（用 gnome-screenshot / scrot / import）
```

### 步骤 2：实现 `__init__.py` 导出

参照 `adb/__init__.py`，导出同样签名的函数：

```python
# phone_agent/linux/__init__.py
from phone_agent.linux.screenshot import get_screenshot, Screenshot
from phone_agent.linux.device import (
    tap, double_tap, long_press, swipe,
    back, home, launch_app, get_current_app,
)
from phone_agent.linux.input import type_text, clear_text
# detect_and_set_adb_keyboard / restore_keyboard 占位 noop
from phone_agent.linux.connection import LinuxConnection, DeviceInfo, ConnectionType, list_devices

def detect_and_set_adb_keyboard(device_id=None): return "noop"
def restore_keyboard(ime, device_id=None): pass
```

### 步骤 3：实现 device.py（用 xdotool）

```python
# phone_agent/linux/device.py
import subprocess

def tap(x: int, y: int, device_id=None, delay=None):
    subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], check=True)

def swipe(sx, sy, ex, ey, duration_ms=None, device_id=None, delay=None):
    duration_s = (duration_ms or 300) / 1000
    subprocess.run([
        "xdotool", "mousemove", str(sx), str(sy),
        "mousedown", "1",
        "mousemove", str(ex), str(ey),  # xdotool 不直接支持 duration,需要 sleep
        "mouseup", "1"
    ])

def get_current_app(device_id=None) -> str:
    result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"],
                            capture_output=True, text=True)
    return result.stdout.strip()

def launch_app(app_name, device_id=None, delay=None) -> bool:
    result = subprocess.run(["gtk-launch", app_name], capture_output=True)
    return result.returncode == 0

# ... double_tap / long_press / back / home ...
```

### 步骤 4：在 DeviceType 加新值

`phone_agent/device_factory.py`：

```python
class DeviceType(Enum):
    ADB = "adb"
    HDC = "hdc"
    IOS = "ios"
    LINUX = "linux"   # ★ 新增
```

更新 `DeviceFactory.module` 属性：

```python
@property
def module(self):
    if self._module is None:
        if self.device_type == DeviceType.ADB:
            from phone_agent import adb
            self._module = adb
        elif self.device_type == DeviceType.HDC:
            from phone_agent import hdc
            self._module = hdc
        elif self.device_type == DeviceType.LINUX:    # ★ 新增
            from phone_agent import linux
            self._module = linux
        else:
            raise ValueError(f"Unknown device type: {self.device_type}")
    return self._module
```

### 步骤 5：加 CLI 选项

`main.py:510-515` 的 `--device-type` choices 加 `linux`：

```python
parser.add_argument(
    "--device-type", type=str,
    choices=["adb", "hdc", "ios", "linux"],   # ★ 加 linux
    default=os.getenv("PHONE_AGENT_DEVICE_TYPE", "adb"),
)
```

`main()` 里加 `elif args.device_type == "linux": device_type = DeviceType.LINUX`。

### 步骤 6：配置 app 映射

新建 `phone_agent/config/apps_linux.py`：

```python
APP_PACKAGES = {
    "Chrome": "google-chrome",
    "Firefox": "firefox",
    "VSCode": "code",
    "Terminal": "gnome-terminal",
    # ...
}

def list_supported_apps():
    return sorted(APP_PACKAGES.keys())
```

在 `main.py` 的 `--list-apps` 分支加 `elif device_type == DeviceType.LINUX:` 处理。

### 步骤 7：测试

```bash
python main.py --device-type linux --list-apps
python main.py --device-type linux --base-url http://localhost:8000/v1 "打开 Chrome 浏览器"
```

---

## 加新 app

**最简单的扩展**，详见 [06-config-prompts.md](06-config-prompts.md#添加新-app-的步骤)。

简而言之：

```python
# phone_agent/config/apps.py（Android）
APP_PACKAGES["抖音极速版"] = "com.ss.android.aweme.lite"

# phone_agent/config/apps_harmonyos.py（HarmonyOS）
APP_PACKAGES["抖音极速版"] = "com.ss.hm.aweme.lite"
# 若 ability != "EntryAbility":
APP_ABILITIES["com.ss.hm.aweme.lite"] = "MainAbility"

# phone_agent/config/apps_ios.py（iOS）
APP_PACKAGES_IOS["抖音极速版"] = "com.ss.iphone.ugc.aweme.lite"
```

无需改 `__init__.py` / prompts / timing。

---

## 加自定义回调

**场景**：用 Web 界面替代终端 `input()` 确认敏感操作。

### 默认实现

```python
# actions/handler.py:321-329
@staticmethod
def _default_confirmation(message: str) -> bool:
    response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
    return response.upper() == "Y"

@staticmethod
def _default_takeover(message: str) -> None:
    input(f"{message}\nPress Enter after completing manual operation...")
```

### 注入自定义实现

```python
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig

# 用 FastAPI/Flask 提供 HTTP 确认端点
def web_confirmation(message: str) -> bool:
    """通过 Web 界面让用户确认,阻塞等待结果。"""
    import requests
    # 发请求到前端,前端弹窗
    requests.post("http://localhost:3000/notify", json={"message": message})
    # 长轮询等用户点击
    while True:
        r = requests.get("http://localhost:3000/pending_confirmation")
        if r.json().get("resolved"):
            return r.json()["approved"]
        time.sleep(0.5)

def slack_takeover(message: str) -> None:
    """通过 Slack 通知用户,等用户在 Slack 里回复 done。"""
    send_slack_message(f"需要人工接管: {message}")
    wait_for_slack_reaction()   # 阻塞

agent = PhoneAgent(
    model_config=ModelConfig(...),
    agent_config=AgentConfig(...),
    confirmation_callback=web_confirmation,
    takeover_callback=slack_takeover,
)
```

**关键约束**：回调必须**阻塞**直到用户响应。Agent 主循环在调用 callback 期间是停住的。

---

## 加新 prompt 语言

**场景**：支持日语 prompt。

详见 [06-config-prompts.md](06-config-prompts.md#添加新语言如日语)。简而言之：

1. 新建 `phone_agent/config/prompts_ja.py`（翻译 `prompts_zh.py`）
2. `config/__init__.py` 加 `SYSTEM_PROMPT_JA` 和 `get_system_prompt` 分支
3. `config/i18n.py` 加 `MESSAGES_JA` 字典和 `get_messages` 分支
4. `main.py` 的 `--lang` choices 加 `"ja"`

---

## 换模型

**场景**：用 Qwen-VL 或其他 VLM 替换 AutoGLM-Phone-9B。

详见 [05-model-client.md](05-model-client.md#换模型的注意事项)。关键障碍：

1. **输出格式**：必须输出 `do(action=...)` 或 `finish(message=...)`，否则要改 `parse_action` + `_parse_response`
2. **多模态消息格式**：图片顺序（图前文后 vs 文前图后）可能要调
3. **流式支持**：必须支持 SSE

**最小改动方案**：

```python
# 1. 改 ModelConfig
model_config = ModelConfig(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_name="qwen-vl-max",
)

# 2. 如果 Qwen 输出 JSON 而非 do(...),改 parse_action
# actions/handler.py
def parse_action(response: str) -> dict:
    response = response.strip()
    if response.startswith("{"):
        # JSON 格式
        import json
        d = json.loads(response)
        d["_metadata"] = "do" if d.get("action") != "finish" else "finish"
        return d
    # 原 AST 逻辑作为 fallback
    ...
```

---

## 加 step hook

**场景**：每步保存截图、记录日志、调用外部 API。

### 方案 A：用 step() 手动驱动

```python
agent = PhoneAgent(model_config=ModelConfig(...), agent_config=AgentConfig(verbose=False))

result = agent.step(task)
step_num = 1
save_screenshot(agent, step_num)   # 自定义 hook

while not result.finished and agent.step_count < 50:
    result = agent.step()
    step_num += 1
    save_screenshot(agent, step_num)
    log_step(result, step_num)

def save_screenshot(agent, step_num):
    """在 step 后立刻截图保存。"""
    # 注意:step 内部已经截过图了,这里再截一次拿到最新状态
    from phone_agent.device_factory import get_device_factory
    shot = get_device_factory().get_screenshot()
    with open(f"logs/step_{step_num:03d}.png", "wb") as f:
        import base64
        f.write(base64.b64decode(shot.base64_data))
```

### 方案 B：monkey-patch _execute_step

```python
original_execute_step = PhoneAgent._execute_step

def logged_execute_step(self, *args, **kwargs):
    result = original_execute_step(self, *args, **kwargs)
    print(f"[HOOK] Step {self._step_count}: action={result.action}")
    return result

PhoneAgent._execute_step = logged_execute_step
```

### 方案 C：继承 PhoneAgent（推荐）

```python
class LoggedPhoneAgent(PhoneAgent):
    def _execute_step(self, *args, **kwargs):
        result = super()._execute_step(*args, **kwargs)
        self._log_step(result)
        return result

    def _log_step(self, result):
        import json
        with open("agent.log", "a") as f:
            f.write(json.dumps({
                "step": self.step_count,
                "action": result.action,
                "thinking": result.thinking[:200],
            }, ensure_ascii=False) + "\n")
```

---

## 统一设备抽象建议

**当前问题**：三套设备实现（adb/hdc/xctest）完全平行，重复度 70-80%，iOS 不走 DeviceFactory，导致 `PhoneAgent` 和 `IOSPhoneAgent` 分裂。

### 建议架构

```python
# phone_agent/device/base.py
from typing import Protocol

class DeviceControl(Protocol):
    """统一设备控制接口。"""
    def tap(self, x: int, y: int): ...
    def swipe(self, sx: int, sy: int, ex: int, ey: int, duration_ms: int): ...
    def back(self): ...
    def home(self): ...
    def launch_app(self, app_name: str) -> bool: ...
    def get_current_app(self) -> str: ...
    def type_text(self, text: str): ...
    def clear_text(self): ...

class ScreenshotProvider(Protocol):
    def get_screenshot(self) -> Screenshot: ...

class DeviceConnection(Protocol):
    def list_devices(self) -> list[DeviceInfo]: ...
    def is_connected(self, device_id) -> bool: ...

# phone_agent/device/adb.py
class ADBDevice(DeviceControl, ScreenshotProvider):
    """ADB 实现,封装 device_id。"""
    def __init__(self, device_id: str | None = None): ...
    def tap(self, x, y):
        subprocess.run(["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)])
    # ...

# phone_agent/device/xctest.py
class XCTestDevice(DeviceControl, ScreenshotProvider):
    """iOS 实现,封装 wda_url + session_id。"""
    def __init__(self, wda_url: str, session_id: str): ...
    def tap(self, x, y):
        # WDA Actions + SCALE_FACTOR 缩放
        ...
```

### 统一后的 Agent

```python
class PhoneAgent:
    def __init__(self, model_config, device: DeviceControl & ScreenshotProvider, ...):
        self.device = device   # 策略注入,平台无关
        self.action_handler = ActionHandler(device=device)   # 也注入

    def _execute_step(self, ...):
        screenshot = self.device.get_screenshot()    # 统一接口
        current_app = self.device.get_current_app()
        # ...
        self.action_handler.execute(action, screenshot.width, screenshot.height)
```

### 收益

- `PhoneAgent` 和 `IOSPhoneAgent` 合并为一个类
- `DeviceFactory` 支持所有平台
- 加新平台只需实现 Protocol，不改 Agent 代码
- 三套重复代码可大量消除（`Screenshot` dataclass 等统一一份）

### 迁移成本

中等。建议：
1. 先建 `phone_agent/device/base.py` 定义 Protocol
2. 让现有 adb/hdc/xctest 模块**适配** Protocol（不改原有代码，加 wrapper）
3. 新 Agent 用 Protocol，老 Agent 保留作为兼容路径
4. 逐步迁移调用方

---

## 为什么 iOS 不走 DeviceFactory

历史原因 + 接口差异叠加：

| 因素 | 说明 |
|------|------|
| 接口签名差异 | adb/hdc 用 `device_id`，xctest 用 `wda_url + session_id` |
| 状态管理 | adb/hdc 无状态，xctest 需要先 `start_wda_session` |
| 坐标缩放 | xctest 多一层 SCALE_FACTOR |
| 错误模式 | subprocess 退出码 vs HTTP 状态码 |
| 演进时序 | Android 先有 → HarmonyOS（同构）→ iOS（异构）后加 |

当时的 DeviceFactory 抽象只针对 subprocess 模式设计，iOS 加进来时强行套用会破坏现有抽象，所以走了独立路径。

如果做架构重构（见上文），可以让 DeviceFactory 支持所有平台，但需要把"连接上下文"（device_id 或 wda_url+session_id）抽象成一个对象，而不是散落在每个方法签名里。

---

## 贡献回上游

如果你想给 [zai-org/Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 提 PR：

1. 看 `.github/PULL_REQUEST_TEMPLATE.md` 了解 PR 格式
2. 跑 `.pre-commit-config.yaml` 配置的 hook（black、flake8 等）
3. 测试：
   ```bash
   pip install -e ".[dev]"
   pytest tests/
   ```
4. CHANGELOG 更新（如果项目有的话）

**目前仓库没有 `tests/` 目录**（虽然 README 提到），所以测试主要靠手动跑 `examples/` 和真机验证。

---

## 下一步

- 想理解动作协议 → [04-action-handler.md](04-action-handler.md)
- 想理解模型流式 → [05-model-client.md](05-model-client.md)
- 想改 prompt → [06-config-prompts.md](06-config-prompts.md)
- 想看完整架构 → [ARCHITECTURE.md](ARCHITECTURE.md)

---
