# 03 · 设备抽象层（Device Layer）

> 本文解析 `phone_agent/` 下的三套平行设备实现：`adb/`（Android）、`hdc/`（HarmonyOS）、`xctest/`（iOS），
> 以及统一调度它们的 `device_factory.py`。这是项目代码量最大、重复度最高的一层。

## 文件地图

| 目录/文件 | 总行数 | 角色 |
|----------|-------|------|
| `device_factory.py` | 167 | **工厂调度**（只支持 adb/hdc，不支持 ios）|
| `adb/` | 874 | Android（subprocess: `adb shell`）|
| `hdc/` | 1018 | HarmonyOS（subprocess: `hdc shell uitest`）|
| `xctest/` | 1416 | iOS（HTTP: WebDriverAgent + subprocess: `idevice*`）|

每套目录结构完全相同：

```
<backend>/
├── __init__.py      统一接口导出（约 50 行）
├── connection.py    Connection 类 + 设备列举 + 远程连接（约 350-380 行）
├── device.py        tap/swipe/launch_app/get_current_app 等控制（约 250-460 行）
├── input.py         文本输入相关（约 110-300 行）
└── screenshot.py    截图（约 110-230 行）
```

## `device_factory.py`：不完整的统一抽象

`DeviceFactory` 类（`device_factory.py:15-139`）包装 adb 或 hdc 模块，提供统一方法签名。

### 工作原理

```python
class DeviceFactory:
    def __init__(self, device_type: DeviceType = DeviceType.ADB):
        self.device_type = device_type
        self._module = None

    @property
    def module(self):
        if self._module is None:
            if self.device_type == DeviceType.ADB:
                from phone_agent import adb
                self._module = adb
            elif self.device_type == DeviceType.HDC:
                from phone_agent import hdc
                self._module = hdc
            else:
                raise ValueError(f"Unknown device type: {self.device_type}")  # ★ iOS 走不到这里
        return self._module

    def tap(self, x, y, device_id=None, delay=None):
        return self.module.tap(x, y, device_id, delay)
    # ...其他方法都是简单转发...
```

**关键设计**：
- **延迟导入**：`module` 属性第一次访问时才 import adb/hdc，避免启动时加载所有平台。
- **纯转发**：每个方法（`tap`/`swipe`/`launch_app`/...）都是 `return self.module.xxx(...)`，没有额外逻辑。

### 全局单例

```python
_device_factory: DeviceFactory | None = None

def set_device_type(device_type: DeviceType):
    global _device_factory
    _device_factory = DeviceFactory(device_type)

def get_device_factory() -> DeviceFactory:
    global _device_factory
    if _device_factory is None:
        _device_factory = DeviceFactory(DeviceType.ADB)   # 默认 ADB
    return _device_factory
```

`main.py` 启动时调 `set_device_type(DeviceType.HDC)` 切换全局。之后所有 `get_device_factory().tap(...)` 都路由到 hdc。

### iOS 不走 Factory！

`device_factory.py:44-45`：

```python
else:  # IOS
    raise ValueError(f"Unknown device type: {self.device_type}")
```

**`DeviceFactory` 完全不支持 iOS**。`main.py:697-698`：

```python
if device_type != DeviceType.IOS:
    set_device_type(device_type)
```

iOS 设备跳过 factory 设置，走独立的 `IOSPhoneAgent` → `IOSActionHandler` → 直接调 `xctest` 模块函数。

**为什么不统一？** 推测原因：
1. iOS 用 HTTP API（WDA），签名与 adb/hdc 的 subprocess 模式差异大
2. iOS 需要 WDA session 管理（有状态），adb/hdc 无状态
3. iOS 坐标需要 SCALE_FACTOR 缩放
4. 历史演进：先有 Android，再加 HarmonyOS（同构），最后加 iOS（异构）

详见 [EXTENDING.md](EXTENDING.md#为什么-ios-不走-devicefactory) 的统一化建议。

## 三套统一接口对照（__init__.py 导出）

每套 `__init__.py` 都导出类似的函数集，但签名有差异：

| 函数 | ADB 签名 | HDC 签名 | XCTest 签名 |
|------|---------|---------|------------|
| `get_screenshot` | `(device_id=None, timeout=10)` | `(device_id=None, timeout=10)` | `(wda_url, session_id=None, device_id=None, timeout=10)` |
| `tap` | `(x, y, device_id=None, delay=None)` | `(x, y, device_id=None, delay=None)` | `(x, y, wda_url, session_id=None, delay=1.0)` |
| `swipe` | `(sx, sy, ex, ey, duration_ms=None, device_id=None, delay=None)` | 同 ADB | `(sx, sy, ex, ey, duration=None, wda_url, session_id=None, delay=1.0)` |
| `type_text` | `(text, device_id=None)` | `(text, device_id=None)` | `(text, wda_url, session_id=None, frequency=60)` |
| `launch_app` | `(app_name, device_id=None, delay=None) → bool` | 同 ADB | `(app_name, wda_url, session_id=None, delay=1.0) → bool` |
| `back/home/double_tap/long_press` | `(device_id=None, delay=None)` | 同 ADB | `(wda_url, session_id=None, delay=1.0)` |
| `clear_text` | `(device_id=None)` | `(device_id=None)` | `(wda_url, session_id=None)` |
| `get_current_app` | `(device_id=None) → str` | 同 ADB | `(wda_url, session_id=None) → str` |
| `list_devices` | `() → list[DeviceInfo]` | `() → list[DeviceInfo]` | `() → list[DeviceInfo]` |

**核心签名差异**：
- ADB/HDC 用 `device_id`（字符串）定位设备
- XCTest 用 `wda_url` + `session_id`（HTTP 服务地址 + 会话 ID）
- ADB/HDC 的 swipe 用 `duration_ms`（毫秒），XCTest 用 `duration`（秒）

### XCTest 独有的未导出函数

`xctest/input.py` 有 6 个**未在 `__init__.py` 导出**的函数：

| 函数 | 行号 | 作用 |
|------|------|------|
| `send_keys(keys: list[str])` | `xctest/input.py:137` | 逐字符发送 |
| `press_enter()` | `xctest/input.py:167` | 发送 `\n` |
| `hide_keyboard()` | `xctest/input.py:184` | `POST /wda/keyboard/dismiss` |
| `is_keyboard_shown() → bool` | `xctest/input.py:208` | `GET /wda/keyboard/shown` |
| `set_pasteboard(text)` | `xctest/input.py:241` | 写剪贴板 |
| `get_pasteboard() → str` | `xctest/input.py:271` | 读剪贴板 |

这些被 `IOSActionHandler` 直接从子模块 import 使用。

## 平台能力对照表

| 能力 | ADB (Android) | HDC (HarmonyOS) | XCTest (iOS) |
|------|--------------|-----------------|--------------|
| **点击** | `input tap x y` | `uitest uiInput click x y` | WDA Actions pointerDown/Up |
| **双击** | 两次 `input tap` + 间隔 | `uitest uiInput doubleClick x y` | WDA Actions 两次 pointerDown/Up |
| **长按** | `input swipe x y x y ms` | `uitest uiInput longClick x y` | WDA Actions pointerDown + pause(ms) |
| **滑动** | `input swipe sx sy ex ey ms` | `uitest uiInput swipe sx sy ex ey ms` | WDA `/wda/dragfromtoforduration` |
| **返回** | `input keyevent 4` | `uitest uiInput keyEvent Back` | 左边缘手势滑动 |
| **Home** | `input keyevent KEYCODE_HOME` | `uitest uiInput keyEvent Home` | `POST /wda/homescreen` |
| **输入文本** | `ADB_INPUT_B64` 广播（需 ADB Keyboard） | `uitest uiInput text` 原生 | WDA `/wda/keys` |
| **清空文本** | `ADB_CLEAR_TEXT` 广播 | Ctrl+A (2054,2017) + Delete (2055) | WDA `element/active` → `clear` |
| **截图** | `screencap` + `adb pull` | `screenshot` + `hdc file recv` | WDA `/screenshot` + `idevicescreenshot` fallback |
| **启动App** | `monkey -p pkg -c LAUNCHER 1` | `aa start -b bundle -a ability` | `POST /wda/apps/launch` |
| **当前App** | `dumpsys window` 解析 mCurrentFocus | `aa dump -l` 解析 FOREGROUND bundle | `GET /wda/activeAppInfo` |
| **列出设备** | `adb devices -l` | `hdc list targets` | `idevice_id -ln` |
| **远程连接** | `adb connect ip:port` | `hdc tconn ip:port` | WiFi 网络 + WDA URL |
| **输入法切换** | 需要（ADB Keyboard） | 不需要（原生 uitest） | 不需要（WDA） |
| **回车键** | `input keyevent 66` | `uitest uiInput keyEvent 2054` | `press_enter()` 发 `\n` |

## 连接类对照

三套都有 `Connection` 类管理设备连接：

### ADBConnection（`adb/connection.py:31`）

```python
class ADBConnection:
    def __init__(self, adb_path: str = "adb"): ...

    def connect(self, address: str) -> tuple[bool, str]      # adb connect ip:port
    def disconnect(self, address: str | None) -> tuple[bool, str]  # adb disconnect [addr]
    def list_devices(self) -> list[DeviceInfo]               # adb devices -l
    def is_connected(self, device_id) -> bool
    def enable_tcpip(self, port=5555, device_id=None)        # adb tcpip port
    def get_device_ip(self, device_id=None) -> str | None    # adb shell ip route
    def restart_server(self)                                  # adb kill-server + start-server
```

### HDCConnection（`hdc/connection.py:66`）

签名几乎与 ADBConnection 完全相同，只是底层命令换成 `hdc tconn` / `hdc tdisconn` / `hdc list targets` / `hdc tmode port` / `hdc shell ifconfig`。

### XCTestConnection（`xctest/connection.py:28`）

签名**差异最大**：

```python
class XCTestConnection:
    def __init__(self, wda_url: str = "http://localhost:8100"): ...

    def list_devices(self) -> list[DeviceInfo]               # idevice_id -ln + ideviceinfo
    def is_connected(self, device_id) -> bool
    def is_wda_ready(self, timeout=2) -> bool                # GET /status ★ iOS 独有
    def start_wda_session(self) -> tuple[bool, str]          # POST /session ★ iOS 独有
    def get_wda_status(self) -> dict | None                  # GET /status ★ iOS 独有
    def pair_device(self, device_id) -> tuple[bool, str]     # idevicepair pair ★ iOS 独有
    def restart_wda(self) -> bool                            # 只检查状态,提示手动重启
    def get_device_name(self, device_id) -> str | None       # ideviceinfo -k DeviceName
    # 没有 connect/disconnect/enable_tcpip (HTTP 无连接概念)
```

### DeviceInfo 数据类

三套都有 `DeviceInfo`，字段略有不同：

```python
# adb/connection.py:20-28
device_id: str
status: str
connection_type: ConnectionType   # USB/WIFI/REMOTE
model: str | None
android_version: str | None       # ★ Android 独有

# hdc/connection.py:55-63
device_id: str
status: str
connection_type: ConnectionType
model: str | None
harmony_version: str | None       # ★ HarmonyOS 独有

# xctest/connection.py:16-25
device_id: str                    # UDID
status: str
connection_type: ConnectionType   # USB/NETWORK
model: str | None
ios_version: str | None           # ★ iOS 独有
device_name: str | None           # ★ iOS 独有
```

理想情况下应该有一个基类 `BaseDeviceInfo` + 平台特化字段。当前是三份独立定义。

## 截图实现详解

三套都返回**相同的 `Screenshot` 数据类**：

```python
@dataclass
class Screenshot:
    base64_data: str
    width: int
    height: int
    is_sensitive: bool
```

但获取方式差异巨大：

| 维度 | ADB | HDC | XCTest |
|------|-----|-----|--------|
| **截屏命令** | `screencap -p /sdcard/tmp.png` | `snapshot_display -f /tmp.jpeg` 或 `screenshot` | WDA `GET /screenshot` |
| **取回方式** | `adb pull` 到 temp 文件 | `hdc file recv` 到 temp 文件 | HTTP response JSON 直接 base64 |
| **格式转换** | PNG 原生 | JPEG → PIL → PNG | PNG base64 → 解码 → PIL |
| **分辨率获取** | `PIL.Image.open().size` | 同 ADB | 同 ADB |
| **fallback 分辨率** | 1080×2400 | 1080×2400 | 1179×2556（iPhone 14 Pro）|
| **敏感页面检测** | `"Status: -1" in output` | `"fail"/"error" in output` | 无 |
| **fallback 机制** | 黑图 | 黑图 | **双路径**: WDA → `idevicescreenshot` CLI → 黑图 |

**敏感页面检测**：Android/HDC 截图失败时（如支付页面 DRM 保护），返回黑图并设 `is_sensitive=True`，Agent 据此触发 takeover。

**iOS 双 fallback**：WDA HTTP 失败 → 用 `idevicescreenshot` CLI 工具（libimobiledevice 提供）→ 还失败 → 黑图。这是最健壮的实现。

## 输入法处理

### ADB：ADB Keyboard 广播机制（最复杂）

Android 系统输入法是 GUI 组件，命令行直接 `input text` 对中文不友好。Open-AutoGLM 用第三方 [ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard) APK，它监听一个 broadcast：

```python
# adb/input.py:21, 27-34
encoded_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
subprocess.run(adb_prefix + [
    "shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", encoded_text
], ...)
```

**完整输入流程**（`ActionHandler._handle_type` → adb/input.py）：

1. `settings get secure default_input_method` 读当前 IME
2. 若不是 ADB Keyboard → `ime set com.android.adbkeyboard/.AdbIME` 切换
3. 发空字符串 "热身"键盘
4. `ADB_CLEAR_TEXT` 广播清空
5. `ADB_INPUT_B64` 广播输入文本（base64 编码避免特殊字符）
6. `ime set <原IME>` 恢复

**为什么要切换+恢复？** 因为切到 ADB Keyboard 后用户看不到正常键盘，必须用完恢复。

### HDC：原生 uitest（无需特殊输入法）

HarmonyOS 的 `uitest uiInput text` 命令原生支持中文输入，不需要安装 APK：

```python
# hdc/input.py:36, 60
_run_hdc_command(hdc_prefix + ["shell", "uitest", "uiInput", "text", escaped_text], ...)
```

**多行文本处理**（ADB 不支持）：按 `\n` 分割，每行发完用 `keyEvent 2054`（回车）。特殊字符转义：`"` → `\"`，`$` → `\$`。

`detect_and_set_adb_keyboard` 在 HDC 是**占位函数**——只返回当前 IME 不切换。

### XCTest：WDA HTTP 输入

```python
# xctest/input.py:48-53
url = _get_wda_session_url(wda_url, session_id, "wda/keys")
response = requests.post(url, json={"value": list(text), "frequency": frequency}, ...)
```

WDA 的 `/wda/keys` 端点接收字符列表，逐字符模拟键盘输入。`frequency=60` 是每秒字符数（默认 60）。

## iOS 特殊点

### WDA Session 管理

WebDriverAgent 是**有状态**服务，操作前必须创建 session：

```python
# agent_ios.py:83-90 启动时自动创建
if self.agent_config.session_id is None:
    success, session_id = self.wda_connection.start_wda_session()
    if success and session_id != "session_started":
        self.agent_config.session_id = session_id
```

`start_wda_session`（`xctest/connection.py:221-253`）发 `POST /session` 带 capabilities，解析返回的 sessionId。后续所有 WDA 调用都带这个 sessionId。

### iOS 坐标缩放

`xctest/device.py:9`：

```python
SCALE_FACTOR = 3  # 3 for most modern iPhone
```

**所有坐标在发给 WDA 前都除以 3**：

```python
# xctest/device.py:105, 154, 212, 267-270
x, y = x // SCALE_FACTOR, y // SCALE_FACTOR
```

**原因**：
- 截图是**物理像素**（如 iPhone 14 Pro: 1179×2556）
- WDA Actions API 用**逻辑像素 points**（如 393×852）
- 比例 1179/393 = 3（Retina 3x）

**潜在 bug**：硬编码 3，对 1x（老 iPhone）/2x（iPhone SE/8、iPad mini）设备会算错。正确做法是从 `GET /session/{id}/window/size` 动态计算 SCALE_FACTOR。

### iOS 设备列举

```python
# xctest/connection.py:71
result = subprocess.run(["idevice_id", "-ln"], ...)
```

`idevice_id -ln` 列出所有连接的 iOS 设备 UDID。连接类型通过 UDID 格式判断：
- 含 `-` 且长度 > 40 → NETWORK（WiFi）
- 否则 → USB

设备详情（型号、iOS 版本、设备名）通过 `ideviceinfo -u UDID` 获取，解析 ProductType / ProductVersion / DeviceName 字段。

### `restart_wda` 实际不重启

`xctest/connection.py:331-348`：方法名叫 `restart_wda`，但实际**只检查 WDA 状态**，提示用户手动在 Xcode 里重启。因为 WebDriverAgent 跑在 iOS 设备上，主机无法直接重启它。

## 代码重复度评估

三套实现是**完全平行的，没有共同基类**。重复度约 70-80%。

### 重复模式

| 重复模式 | 出现次数 | 说明 |
|---------|---------|------|
| `_get_*_prefix(device_id)` 函数 | 6 处 | `["adb", "-s", id]` vs `["hdc", "-t", id]` 模式 |
| `_get_wda_session_url()` 函数 | 2 处 | xctest/device.py 和 xctest/input.py 各一份 |
| `Screenshot` dataclass | 3 处 | 三套 screenshot.py 各一份完全相同的定义 |
| `_create_fallback_screenshot()` | 3 处 | 三套各一份，仅默认分辨率不同 |
| `DeviceInfo` dataclass | 3 处 | 三套 connection.py 各一份，OS 版本字段不同 |
| `ConnectionType` Enum | 3 处 | ADB/HDC 相同，XCTest 略不同 |
| delay 初始化模式 | ~24 处 | `if delay is None: delay = TIMING_CONFIG.device.default_*` |

### 理想抽象（当前缺口）

```python
# 建议的抽象基类（当前不存在）
class BaseDeviceControl(Protocol):
    def tap(self, x: int, y: int, ...): ...
    def swipe(self, sx, sy, ex, ey, ...): ...
    def launch_app(self, app_name: str, ...) -> bool: ...
    def get_current_app(self, ...) -> str: ...
    # ...

class BaseConnection(Protocol):
    def list_devices(self) -> list[DeviceInfo]: ...
    def is_connected(self, device_id) -> bool: ...

class ScreenshotProvider(Protocol):
    def get_screenshot(self, ...) -> Screenshot: ...
```

如果做了这个抽象：
- `DeviceFactory` 可以支持 iOS（消除当前不一致）
- `PhoneAgent` 和 `IOSPhoneAgent` 可以合并为一个类 + 策略注入
- 添加新平台（如 Linux Desktop、Web）只需实现 Protocol

详见 [EXTENDING.md](EXTENDING.md#统一设备抽象建议)。

## 调试技巧

### 1. 验证 ADB 命令

```bash
# 手动跑 handler 会调的命令
adb shell input tap 540 1200          # 点击屏幕中心
adb shell input swipe 540 2000 540 400 300   # 上滑
adb shell dumpsys window | grep mCurrentFocus   # 看当前 app
```

### 2. 验证 HDC 命令

```bash
hdc shell uitest uiInput click 540 1200
hdc shell uitest uiInput swipe 540 2000 540 400 300
hdc shell aa dump -l | head
```

### 3. 验证 WDA 端点

```bash
# WDA 状态
curl http://localhost:8100/status

# 截图
curl http://localhost:8100/screenshot

# 当前 app
curl http://localhost:8100/wda/activeAppInfo
```

### 4. 启用 HDC verbose

`main.py:701-704` 启动时会自动开 HDC verbose：

```python
if device_type == DeviceType.HDC:
    from phone_agent.hdc import set_hdc_verbose
    set_hdc_verbose(True)
```

## 下一步

- 想了解动作怎么调度到这些函数 → [04-action-handler.md](04-action-handler.md)
- 想加新平台 → [EXTENDING.md](EXTENDING.md#加新设备平台)
- 想统一三套抽象 → [EXTENDING.md](EXTENDING.md#统一设备抽象建议)
- iOS 安装 → [ios_setup/ios_setup.md](ios_setup/ios_setup.md)

---
