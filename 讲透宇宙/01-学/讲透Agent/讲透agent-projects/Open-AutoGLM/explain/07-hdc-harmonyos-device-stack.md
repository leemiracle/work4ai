# 07 · hdc 子包：鸿蒙设备栈（HarmonyOS Device Connector）

## ① 角色定位

`phone_agent/hdc/` 是 Open-AutoGLM 三套同构设备栈中的鸿蒙实现，把 `hdc`（HarmonyOS Device Connector，鸿蒙版 adb）的命令行能力包装成与 `phone_agent/adb/` 完全同签名的四个模块：connection（连接管理）、device（手势与前台应用）、input（文本注入）、screenshot（截图）。上层 `DeviceFactory`（`phone_agent/device_factory.py`）按 `DeviceType.HDC` 延迟加载本包，Agent 主循环对"底下是 Android 还是鸿蒙"毫无感知。与 adb 栈最大的差异在三个点：手势走 `uitest uiInput`、文本输入是原生能力（无需装第三方输入法）、应用启动需要 bundle+ability 二元组。

## ② 内部结构

- **connection.py**：`HDCConnection`（`phone_agent/hdc/connection.py:66`）管理连接生命周期——`connect()` 走 `hdc tconn`（:110-111），地址无端口时自动补 `:5555`（:106-107）；`list_devices()` 解析 `hdc list targets`（:173-174），device_id 含 `:` 判 REMOTE、否则 USB（:190-193）；`enable_tcpip()` 走 `hdc tmode port`（:279）开启无线调试；`restart_server()` 是 kill→sleep→`start -r` 三步（:342-351）。模块级 `_run_hdc_command`（:17）是所有子进程调用的唯一出口，`HDC_VERBOSE` 环境变量开关命令回显（:14）。
- **device.py**：8 个手势函数（tap/double_tap/long_press/swipe/back/home/launch_app/get_current_app）全部拼 `uitest uiInput` 子命令——点击是 `uiInput click`（:98-99），返回/桌面是 `keyEvent Back/Home`（:228/:249）。`get_current_app`（:13）解析 `aa dump -l` 的 mission 列表。
- **input.py**：`type_text`（:10）走 `uitest uiInput text`；`clear_text`（:66）用组合键；`detect_and_set_adb_keyboard`（:92）是 placeholder。
- **screenshot.py**：`get_screenshot`（:26）双方法回退 + 黑图兜底，返回 `Screenshot` dataclass（:16-23，含 is_sensitive 标志）。
- **__init__.py**：barrel 导出 19 个名字（:29-53），与 adb/xctest 栈的 `__all__` 逐项对齐。

## ③ 外部连接

- 被消费：`DeviceFactory` 按 type 转发；`phone_agent/hdc/device.py:8-9` 直接导入 `APP_ABILITIES`/`APP_PACKAGES`（`phone_agent/config/apps_harmonyos.py`）与 `TIMING_CONFIG`（`phone_agent/config/timing.py`）。
- 依赖宿主：`hdc` 可执行文件（来自 DevEco Studio / HarmonyOS SDK）；`main.py:701-704` 在 `--device-type hdc` 时自动 `set_hdc_verbose(True)`。
- shell 侧协议：`uitest`（系统预置测试框架）、`aa`（Ability Assistant，应用管理）、`settings`/`ime`（部分命令在鸿蒙上未必存在，见下）。

## ④ 数据流

一次 `launch_app("抖音")`（`phone_agent/hdc/device.py:255`）：查 `APP_PACKAGES` 得 bundle `com.ss.hm.ugc.aweme`，未命中则打印可用前 10 个应用并返回 False（:272-275）；再以 `APP_ABILITIES.get(bundle, "EntryAbility")` 取 ability（:282），拼 `hdc shell aa start -b {bundle} -a {ability}`（:286-298），末尾 `time.sleep(TIMING_CONFIG.device.default_launch_delay)`（:299）。截图流（screenshot.py:44-97）：shell `screenshot` 写远端 JPEG→失败换 `snapshot_display -f`（:60-66）→`hdc file recv` 拉到本地临时文件（:73-74）→PIL 读出尺寸、转 PNG、base64 编码（:85-90）→返回；两级都失败时按失败输出是否含 fail/error 判敏感页，返回 1080×2400 黑图（:59,111-125）。注意黑图有**两种语义**：双方法都报错标 `is_sensitive=True`（真敏感页），而 `file recv` 拉回失败或异常路径的黑图标 `is_sensitive=False`（screenshot.py:81,:101）——排查日志时同是黑图含义不同。

## ⑤ 设计决策与陷阱

1. **同构换壳**：四模块与 adb 栈一一对应，学习成本趋零；但 `connection.py:286` 复用的是 `TIMING_CONFIG.connection.adb_restart_delay`——字段名还叫 adb，是直接从 adb 栈移植的痕迹，改时序配置时别被名字骗了。
2. **多行文本拆行注入**：`uitest uiInput text` 不认 `\n`，`input.py:28-50` 逐行发送并在行间插 `keyEvent 2054`（鸿蒙 ENTER 键码）；行内 `"` 和 `$` 手工转义（:33）。**空行会被跳过**（:31 `if line`），需要保留空行的文本会失真。
3. **clear_text 是组合键硬清**：`input.py:80-89` 发 `2072 2017`（Ctrl+A）再发 `2055`（Delete），对超长文本比逐键退格高效，但依赖焦点仍在输入框。
4. **placeholder 陷阱**：`detect_and_set_adb_keyboard`（`input.py:92-121`）文档自认是 placeholder——只读取当前 IME 并原样返回，不切换；而 `restore_keyboard`（:124-142）却会真调 `hdc shell ime set`，两个函数不对称，鸿蒙上 `ime` 命令未必可用（异常被裸 except 吞掉）。
5. **`list_devices` 的状态是猜的**：HDC 不输出设备状态，connection.py:196-204 给所有出现的设备硬编码 `status="device"`，离线设备无法识别。
6. **swipe 时长自动合龙**：距离平方/1000 再 clamp 到 500-1000ms（`device.py:187-191`）；`long_press` 的 `duration_ms` 形参在鸿蒙 `longClick` 上可能不生效（:143-153 注释自认）。
7. **JPEG only**：HDC 截图只支持 JPEG（screenshot.py:46-47），落盘扩展名与真实格式靠 PIL 自动嗅探兜住。

## ⑥ 新人提示

先跑 `python main.py --device-type hdc --list-devices` 验证 hdc 工具链，再读 `hdc/device.py` 的 `get_current_app`（:26-77）理解 `aa dump -l` 的 mission 状态机解析（app name 行与 state #FOREGROUND 行的配对逻辑，:51-66）。给新鸿蒙应用加支持只需在 `apps_harmonyos.py` 的两个字典各加一条；ability 名不确定时先默认 `EntryAbility` 试跑。调时序用环境变量（如 `PHONE_AGENT_TAP_DELAY=2`）覆盖，不要改源码。
