# 06 · ADB 设备栈（phone_agent/adb/ 四件套）

> 对应 tour 第 7 步「Android ADB 通道」。三套设备栈中最常用、也是 hdc/xctest 的同构模板。

## ① 角色定位

`phone_agent/adb/` 把"控制一台 Android"拆成四个职责单一的模块：`connection.py` 管 adb 连接与设备枚举、`device.py` 管手势与前台应用识别、`input.py` 管文本注入、`screenshot.py` 管截图与兜底。`__init__.py` 把 15 个函数汇聚导出（`phone_agent/adb/__init__.py:28-51`），对上满足 DeviceFactory 的鸭子契约（见 05 篇）。全栈的实现手段是 `subprocess.run` 调宿主 `adb` 命令行——本仓不依赖 uiautomator/appium 等重框架，唯一设备侧依赖是中文输入所需的 ADB Keyboard APK。

## ② 内部结构

**connection.py**（353 行）：`ConnectionType` 枚举 USB/WIFI/REMOTE（`:12-17`，**WIFI 从未被赋值**——`list_devices` 只区分 "host:port"→REMOTE、其余→USB，模拟器也归 USB，`:146-151`）；`DeviceInfo` dataclass（`:20-27`）；`ADBConnection` 类——`connect` 补默认端口 `:5555`（`:72-73`）、以 stdout 含 "connected"/"already connected" 判成功（`:85-88`）；`list_devices` 解析 `adb devices -l`，从 `model:` 段取机型（`:154-158`）；`is_connected` 要求 status=="device"（`:215`）；`enable_tcpip` 开无线调试并按 `TIMING_CONFIG.connection.adb_restart_delay` 等待（`:219-250`）；`get_device_ip` 先 `ip route` 找 src 再回退 `ip addr show wlan0`（`:257-299`）；`restart_server` kill+start（`:305-328`）。模块尾的 `quick_connect/list_devices` 便捷函数（`:331-353`）。

**device.py**（252 行）：`get_current_app` 跑 `dumpsys window`（`:24-26`），扫 `mCurrentFocus/mFocusedApp` 行（`:33`）拿包名去 `APP_PACKAGES`（`config/apps.py` 中文名→包名映射，如 "微信"→`com.tencent.mm`，`phone_agent/config/apps.py:4-6`）反查应用名，查不到回落 `"System Home"`（`:38`）。手势全家族：`tap`=`input tap`+默认延时（`:58-61`）；`double_tap`=两次 tap 夹 `double_tap_interval` 0.1s（`:81-88`）；`long_press`=同点 `input swipe` 拖 duration（`:113-117`）；`swipe` 时长自适应——按距离平方/1000 算再 clamp 到 1000-2000ms（`:147-151`）；`back`=`keyevent 4`（`:184`）；`home`=`KEYCODE_HOME`（`:203`）；`launch_app` 先查 APP_PACKAGES 否则 False（`:225-226`），用 `monkey -p <pkg> -c android.intent.category.LAUNCHER 1` 拉起（`:231-243`）。

**input.py**（109 行）：中文输入的完整答案——`type_text` 把文本 base64 编码后 `am broadcast -a ADB_INPUT_B64 --es msg <b64>` 广播给 ADB Keyboard（`:21-37`），绕开 `input text` 不支持中文/空格转义的地雷；`clear_text` 广播 `ADB_CLEAR_TEXT`（`:49-53`）；`detect_and_set_adb_keyboard` 读 `settings get secure default_input_method`（`:69-74`），不是 `com.android.adbkeyboard/.AdbIME` 就 `ime set` 切换（`:77-82`），再 `type_text("")` 热身（`:85`），返回原 IME 供还原；`restore_keyboard` 用 `ime set` 复原（`:100-102`）。

**screenshot.py**（109 行）：`Screenshot` dataclass 四字段，`is_sensitive` 标记敏感页（`:15-22`）。流程：`screencap -p /sdcard/tmp.png`（`:45-50`）→ 输出含 `Status: -1`/`Failed` 判为**敏感页拦截**返回黑图（`:53-55`）→ `adb pull` 到本地临时文件（`:58-63`）→ 文件不存在返回非敏感黑图（`:65-66`）→ PIL 打开取宽高、重存 PNG、base64（`:69-74`）→ 清理临时文件（`:77`）；任何异常也回落黑图（`:83-85`）。`_create_fallback_screenshot` 生成 1080×2400 纯黑 PNG（`:95-109`）。

## ③ 外部连接

- **被谁用**：`DeviceFactory.module` 懒加载后全量转发（`phone_agent/device_factory.py:37-39`）；`adb/__init__.py` 是唯一聚合点（`:3-26` 四个 import 源）。
- **imports**：`device.py` 依赖 `config/apps.APP_PACKAGES` 与 `TIMING_CONFIG`（`phone_agent/adb/device.py:8-9`）；`connection.py` 依赖 `TIMING_CONFIG.connection`（`:9`）；`screenshot.py` 依赖 PIL（`:12`）。`input.py` 零仓内依赖。
- **外部世界**：宿主 `adb` 二进制、设备端 ADB Keyboard（`phone_agent/adb/input.py:17-18` 文档注明的 AdbKeyboard 项目）、`/sdcard/tmp.png` 固定中转路径。

## ④ 数据流

```
Agent 每步:
 get_screenshot: screencap→pull→PIL→base64 ─┐
 get_current_app: dumpsys window→APP_PACKAGES ├→ MessageBuilder→VLM
 动作执行:
 Tap(x,y)   → input tap x y → sleep(默认1s, TIMING_CONFIG.device)
 Type(text) → detect IME→切AdbIME→clear广播→b64广播→还原IME（四段 sleep）
 Launch(名) → APP_PACKAGES 查包名→monkey -p 启动
失败路径: 截图任何一步异常 → 1080×2400 黑图 → 循环继续
```

与 04 篇衔接：handler 传入的像素坐标由 0-1000 相对坐标乘**截图宽高**得来——黑图兜底时宽高是假的 1080×2400，若真机分辨率不同，后续 tap 换算基准失真。

## ⑤ 设计决策与陷阱

1. **黑图兜底：活命优先于精确**（`phone_agent/adb/screenshot.py:95-109`）：支付页等敏感屏 Android 直接拒截（`Status: -1`），栈的选择是返回黑图让 agent "看见黑屏"自行判断，绝不抛异常打断循环。`is_sensitive=True` 字段已就绪但 agent 侧未消费——二次开发可据此做提示（如"当前页面截图被系统拦截"）。
2. **中文输入三保险**：base64 广播（避开 shell 转义）+ IME 临时切换 + 用后还原（`phone_agent/adb/input.py:56-102`）。陷阱：若 ADB Keyboard 未装，`ime set` 会失败但代码不检查返回值——表现为"输入动作成功但屏幕没字"，排障第一步查 `adb shell ime list`。
3. **`launch_app` 的白名单制**：应用名必须命中 `APP_PACKAGES`（`phone_agent/adb/device.py:225-226`），模型说"打开抖音"而清单没有就 False——扩 App 支持改 `config/apps.py`（168 条），不是设备栈。
4. **monkey 启动而非 `am start`**（`:231-243`）：monkey 不需要知道 Activity 名，只要包名即可拉 LAUNCHER intent，代价是 monkey 自身的日志噪声与个别 ROM 兼容差异。
5. **每个动作后固定 sleep ~1s**（TIMING_CONFIG 默认，`timing.py` DeviceTimingConfig）：为截图稳定服务，代价是步频上限；`PHONE_AGENT_TAP_DELAY` 等环境变量全局可调。
6. **`/sdcard/tmp.png` 固定路径**（`phone_agent/adb/screenshot.py:46`）：多 agent 并发控同一台设备会互踩文件；device_id 不同设备则无冲突（pull 用各自 prefix）。
7. **`dumpsys window` 的兜底语义**：前台应用识别不到一律 "System Home"（`phone_agent/adb/device.py:38`）——模型可能因此误判"已回桌面"，实际只是清单没收录该 app。
8. **ConnectionType.WIFI 是死枚举值**（`:17` 定义后无赋值点），别据它推断连接形态。

## ⑥ 新人提示

- 环境自检三条命令：`adb devices -l`（连接）、`adb shell ime list | grep adbkeyboard`（输入依赖）、手动跑 `screencap -p /sdcard/tmp.png && adb pull`（截图链路）——对应四件套的三大故障域。
- 读 hdc/xctest 前先把 adb 栈读熟：三栈同构，`hdc/device.py` 的 `uitest uiInput click` 与本文 `input tap` 逐方法对得上，对照读最快理解"平台差异被怎样关在设备层"。
- 调坐标类 bug 时打印 `screenshot.width/height` 与换算后像素（`phone_agent/actions/handler.py:136`），确认不是黑图假分辨率。
- 加新手势（如双指缩放）：`device.py` 加函数 → `__init__.py` 导出 → hdc 同步 → 工厂接口本就转发无需改（除非带新参数签名）。
- `connection.py` 的 `enable_tcpip+get_device_ip+connect` 三连是 USB 转 WiFi 控机的标准路径（`:219-303`），适合机器人/机柜场景。
