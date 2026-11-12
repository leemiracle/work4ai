# 05 · 设备抽象工厂（phone_agent/device_factory.py）

> 对应 tour 第 6 步后半。167 行的文件，是整个多平台架构的支点，也是 iOS 线的"缺席者"。

## ① 角色定位

`device_factory.py` 用"模块级鸭子类型"实现平台抽象：`DeviceFactory` 不 import 任何具体设备类，而是在首次使用时**延迟加载** `phone_agent.adb` 或 `phone_agent.hdc` 子包，把它们的模块对象当后端，15 个转发方法统一签名。上层（agent 主循环、ActionHandler）因此一行平台分支都没有——要支持新平台（如 scrcpy、playwright-android），只需提供一个四件套同构的子包再挂进 `module` property。

它是全仓唯一持有"当前平台"全局状态的模块：`set_device_type()`/`get_device_factory()` 模块级单例（`phone_agent/device_factory.py:143-167`）。

## ② 内部结构

**`DeviceType` 枚举**（`:7-12`）：`ADB/HDC/IOS` 三值。

**`DeviceFactory`**（`:15`）：

- 构造只存 `device_type` 与 `_module=None`（`:22-30`）。
- **`module` property**（`:32-46`）：懒加载核心——`_module` 为空时按类型 `from phone_agent import adb`（`:37`）或 `hdc`（`:41`）导入子包并缓存；**其他类型（含 IOS）直接 `ValueError`**（`:44-45`）。能这样写是因为 adb/hdc 两个子包的 `__init__.py` 暴露同名函数集（`phone_agent/adb/__init__.py:28-51` 的 `__all__` 15 项），工厂对"模块对象"做属性转发，鸭子契约即接口文档。
- **15 个转发方法**（`:48-126`）：`get_screenshot`（带 timeout 参数 `:48-50`）、`get_current_app`、`tap/double_tap/long_press/swipe/back/home`、`launch_app`（返回 bool `:102-106`）、`type_text/clear_text`、`detect_and_set_adb_keyboard/restore_keyboard`、`list_devices`——签名与 adb 子包逐一对齐，`device_id` 一律第一可选参。
- **`get_connection_class`**（`:128-139`）：返回 `ADBConnection` 或 `HDCConnection` 类对象（供 `main.py` 体检连接用），IOS 同样 `ValueError`（`:138-139`）。

**单例区**（`:142-167`）：`_device_factory` 模块级变量；`set_device_type(type)` 重建实例（`:146-154`）；`get_device_factory()` 空则默认 `DeviceType.ADB`（`:157-167`，默认值 `:166`）。

**iOS 在哪？** `main.py` 显式绕过：解析 `--device-type` 后 `if device_type != DeviceType.IOS: set_device_type(...)`（`main.py:700-701`）——iOS 从不注册工厂，走独立的 `agent_ios.py + handler_ios.py + xctest/` 全套。所以 `DeviceType.IOS` 枚举值只在 main.py 的参数分流处消费，工厂内部无人处理。

## ③ 外部连接

- **上游（被谁用）**：`agent.py` 每步取截图/前台应用（`phone_agent/agent.py:143-145`）；`actions/handler.py` 全部设备原语经 `get_device_factory()`（`phone_agent/actions/handler.py:11`）；`main.py` 启动期 `set_device_type`（main.py:698）+ 体检。全仓 grep `get_device_factory` 恰好四个文件（agent/device_factory/main/handler），收敛点极干净。
- **下游（管谁）**：`phone_agent/adb` 与 `phone_agent/hdc` 两个子包——工厂要求它们提供同构 15 函数；两个 `__init__.py` 的 `__all__` 就是契约清单（`phone_agent/adb/__init__.py:28-51`）。
- **不连接**：`xctest/` 子包、`handler_ios.py`、`agent_ios.py`——iOS 全线旁路。

## ④ 数据流

```
进程启动: main.py 解析 --device-type
  ├─ adb/hdc → set_device_type(DeviceType.X) → 重建全局工厂（懒加载待命）
  └─ ios → 不注册工厂，选 IOSPhoneAgent 全套
运行期: get_device_factory()（首次触发 from phone_agent import adb/hdc）
  → factory.tap(x,y,id) → self.module.tap(x,y,id) → 子包函数 → subprocess adb/hdc
切换平台: 再调 set_device_type 即换后端（_module 缓存随之丢弃）
```

延迟导入的双收益：① 未装 iOS 依赖的 Android 用户不会触发跨平台 import 链；② 单元测试可 monkeypatch `factory._module` 为假模块，全部上层逻辑脱离真机可测。

## ⑤ 设计决策与陷阱

1. **转发模块而非接口类**：没有 `DeviceInterface` 抽象基类，契约靠两个子包 `__all__` 对齐维持。加第 16 个方法时若只改了 adb 忘改 hdc，**运行到该方法才 AttributeError**，没有静态检查兜底——扩接口必须双栈同改（改完 grep 两个 `__init__.py`）。
2. **全局单例=隐式全局状态**：`device_id` 又是每调用传参，平台是全局、设备是参数——多平台混跑（同时控 Android+鸿蒙）做不到，单例只支持一活平台。测试间须记得 `set_device_type` 复位，否则用例互相污染。
3. **IOS 枚举是"占位谎言"**（`:44-45,138-139`）：枚举里有 IOS、工厂里必炸。读代码的人容易误以为 iOS 也走工厂——实际靠 main.py:701 的 if 挡在门外。这是理解本仓 iOS 架构的最重要事实。
4. **同构双线的维护税**：iOS 旁路意味着动作协议（`parse_action` 共享）之外的一切（执行、截图、输入）都是两份平行实现；改 `Type` 语义要同步 `handler.py._handle_type` 与 `handler_ios.py` 对应逻辑。
5. **`get_device_factory()` 默认 ADB 的宽容**（`:166`）：忘调 `set_device_type` 不报错而是静默用 adb——在纯 HDC 环境会以"设备不存在"的表象失败，排障时先查有没有注册。
6. **方法签名与子包不完全同构**：工厂 `get_screenshot(device_id, timeout)`（`:48`）带 timeout，hdc 子包同名函数签名若漂移，同样运行期才暴露。

## ⑥ 新人提示

- 读此文件时对照 `phone_agent/adb/__init__.py` 的 `__all__` 逐项过一遍，10 分钟即可建立"工厂接口=子包导出集"的肌肉记忆。
- 想看平台差异如何被隔离：并排读 `adb/device.py:tap`（`input tap`）与 `phone_agent/hdc/device.py:tap`（`uitest uiInput click`），签名一致、实现全异——这就是工厂存在的意义。
- 单测技巧：`factory = DeviceFactory(DeviceType.ADB); factory._module = fake_module` 直接注入假后端，`agent.py`/`handler.py` 全链路即可离线跑。
- 加新平台四件套模板：connection/device/input/screenshot + `__init__.py` 暴露 15 函数 + `DeviceType` 加枚举 + `module` property 加分支——照 hdc 子包抄最快。
- 排查"Unknown device type"类 ValueError（`:45`）先看 main.py 有没有把 ios 也送进了 `set_device_type`（当前代码已挡，`:701`；老版本分支可能没有）。
