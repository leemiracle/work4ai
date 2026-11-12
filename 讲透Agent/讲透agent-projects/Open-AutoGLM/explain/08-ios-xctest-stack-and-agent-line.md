# 08 · xctest 子包与 iOS Agent 线：WebDriverAgent 全链

## ① 角色定位

iOS 是三平台中唯一不走"宿主命令行"的通道：`phone_agent/xctest/` 以 **HTTP REST** 驱动设备上常驻的 WebDriverAgent（WDA），辅以 libimobiledevice 工具链（idevice_id/ideviceinfo/idevicepair/idevicescreenshot）做设备发现与配对。在栈之上，`phone_agent/agent_ios.py` 与 `phone_agent/actions/handler_ios.py` 复刻 Android 版主循环、复用同一套动作解析，构成从截图到 WDA 调用的独立完整线。**勘误（源码实证）**：知识图谱与 DeepWiki 称本栈管理"go-ios/xctrace 子进程"，全仓 grep 零引用——实际工具链只有 libimobiledevice + WDA，环境文档 `docs/ios_setup/ios_setup.md:113` 也只出现 `iproxy 8100 8100`。

## ② 内部结构

- **connection.py**：`XCTestConnection`（`phone_agent/xctest/connection.py:28`）持 `wda_url`（默认 `http://localhost:8100`，:47）；`list_devices()` 跑 `idevice_id -ln`（:70-75），UDID 含 `-` 且长度>40 判 NETWORK 连接（:84-88）；`is_wda_ready()` GET `/status`（:209-212）；`start_wda_session()` POST `/session`，sessionId 兼容顶层与 `value` 内两处（:238-243）；`pair_device()` 走 `idevicepair`（:284-290）。`restart_wda`（:331-348）只检测不重启——WDA 必须由 Xcode 手动拉起。
- **device.py**：`SCALE_FACTOR = 3`（:9，Retina 3x）贯穿所有坐标——W3C Actions 的 `pointerMove` 坐标要 `x/SCALE_FACTOR`（:105）；swipe 用私有端点 `wda/dragfromtoforduration`（:263-274）；back 无系统返回键，模拟左缘右滑手势 (0,640)→(400,640)（:307-313）；home 走 `wda/homescreen`（:341）。
- **input.py**：`type_text`（:26）POST `wda/keys`，`value` 是逐字符列表（`list(text)`，:52）；`clear_text`（:64）先 `element/active`→clear（:83-95），失败回退连发 100 个退格控制符 `\u0008`（:106-134）；`set_pasteboard`（:241）写剪贴板备长文本粘贴。
- **screenshot.py**：三级降级（:46-57）——WDA `GET /screenshot` 直接返回 base64（:77-96）→`idevicescreenshot` 子进程落盘再编码（:106-147）→1179×2556 黑图（iPhone 14 Pro 尺寸，:170）。
- **agent_ios.py / handler_ios.py**：`IOSPhoneAgent`（agent_ios.py:44）构造时若无 session_id 自动建 WDA 会话（:83-90）；`IOSActionHandler`（handler_ios.py:53）维护 14 个动作分发表（:100-115）。

## ③ 外部连接

向上：`IOSPhoneAgent` 由 `ios.py` 与 `main.py --device-type ios` 两条入口创建（main.py:765-768）；`phone_agent/__init__.py` 把它与 PhoneAgent 并列为仅有的两个门面。横向复用：`agent_ios.py:8` 直接导入 Android 线的 `parse_action`/`finish`（提示词动作协议全平台共享），消息构建同样借 `MessageBuilder`（:172-192）。向下：device.py 依赖 `phone_agent/config/apps_ios.py` 的 Bundle ID 清单（:7）；handler 的 `_convert_relative_to_absolute`（handler_ios.py:118-124）把模型 0-1000 相对坐标转逻辑像素，栈内再除 3——**两层换算勿混**。

## ④ 数据流

`_execute_step`（agent_ios.py:154-267）单步：get_screenshot（:161-165）→get_current_app（WDA `wda/activeAppInfo`→bundleId→清单反查，phone_agent/xctest/device.py:31-72）→首步拼 system+任务+截图、后续步拼 `** Screen Info **`+新截图（:171-192）→`ModelClient.request`（:196）→`parse_action(response.action)`（:210），解析失败降级为 finish 并把原文当 message（:211-214）→立即剥掉上一条消息里的图省 token（:229）→`action_handler.execute(action, screenshot.width, screenshot.height)`（:233-235），执行异常也转 finish 收尾（:236-241）→assistant 消息以 `<think>…</think><answer>…</answer>` 原文回填（:244-248）→`_metadata=="finish" or result.should_finish` 判终（:251）。Type 动作在 handler 内是 clear→sleep 0.5→type→sleep 0.5→hide_keyboard→sleep 0.5 的三段式（handler_ios.py:166-174）。

## ⑤ 设计决策与陷阱

1. **REST 而非命令行**：与 adb/hdc 栈"同构"的只是函数签名；实现从 subprocess 换成 requests，`requests` 因此进 requirements.txt（iOS 注释，requirements.txt:3-4）。所有 WDA 调用 `verify=False`（如 device.py:114）。
2. **坐标双陷阱**：handler 层已转成"逻辑像素"，栈内又除 `SCALE_FACTOR=3`（device.py:105,154,212,267-270）——非 3x 设备（旧机型/部分 iPad）需改 :9 这一个常量。
3. **pause 时长单位混乱**：tap 的 pause 写 `0.1`（device.py:107），double_tap 写 `100`（:156-161）——W3C pause duration 名义单位是毫秒，0.1 实为立即；复用 double_tap 时留意节奏。
4. **未知动作直接终止任务**：`execute` 收到未知 `_metadata` 返回 `should_finish=True`（handler_ios.py:74-79），与 Android 侧行为不同，模型输出走样时 iOS 线会提前收摊。
5. **Note/Call_API/Interact 是空壳**（handler_ios.py:254-269），提示词却已声明这些动作——模型真用了只会得到静默成功。
6. **`is_keyboard_shown`/`press_button` 等 7 个函数无消费者**（phone_agent/xctest/input.py:184-238、device.py:431-458 等），属预留 API。
7. **WDA 会话可选**：session_id 为 None 时所有端点走无 session 形式（connection.py 与 device.py 的 `_get_wda_session_url` 双实现，phone_agent/xctest/device.py:11-28）。

## ⑥ 新人提示

环境搭建照 `docs/ios_setup/ios_setup.md` 走：Xcode 部署 WDA（GUI 或 `xcodebuild test` 命令行，:88-101）→USB 场景另开终端 `iproxy 8100 8100`→浏览器开 `http://localhost:8100/status` 验活。先跑 `python ios.py --list-devices` 与 `--wda-status`（ios.py:380-443）再谈自动化。读代码顺序：connection.py 的 WDA 会话三件套 → device.py 的 SCALE_FACTOR → handler_ios.py 分发表 → agent_ios.py 主循环对照 agent.py 找差异。iOS 线源自社区 PR141 与 Gekowa 分支（ios_setup.md:126-130），代码风格与主线略有出入。
