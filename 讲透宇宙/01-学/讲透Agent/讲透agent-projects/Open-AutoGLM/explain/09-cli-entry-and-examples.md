# 09 · CLI 入口与使用示例：main.py、ios.py 与 examples/

## ① 角色定位

仓库提供两条 CLI 入口：`main.py`（853 行）是全平台统一入口，按 `--device-type adb|hdc|ios` 分流环境体检、设备命令与 Agent 构造；`ios.py`（550 行）是 iOS 独立精简入口，早于 main.py 的 iOS 支持而存在，两者保留大量重复代码。`examples/` 两个文件则是 Python API 侧的教学样张——不看 CLI 的话，从这里五分钟能理解 PhoneAgent 的全部驱动方式。三个文件共同构成"人类使用这个项目"的全部界面。

## ② 内部结构

**main.py** 四段式：`check_system_requirements`（:37-269）按平台三查——工具安装（adb/hdc/idevice_id，:62-98）、设备在线（:125-186）、第三查平台特化（ADB 查 ADB Keyboard `com.android.adbkeyboard/.AdbIME`，:195-228；HDC 明确跳过，:229-232；iOS 查 WDA，:233-260）；`check_model_api`（:272-352）用一次 `chat.completions.create(model, "Hi", max_tokens=5)` 探活并分类报错；`handle_device_commands`（:602-681）处理 `--list-devices/--connect/--disconnect/--enable-tcpip` 四个即退命令，iOS 命令另有 `handle_ios_device_commands`（:527-599）；`main()`（:684-849）串起：set_device_type 全局注册（:697-698，iOS 除外）→HDC 开 verbose（:701-704）→`--list-apps` 三平台分流（:707-728）→体检→模型检查（:735-745）→按平台建 `PhoneAgent` 或 `IOSPhoneAgent`（:755-781）→单任务执行或进入交互循环（:821-849）。

**ios.py** 结构同构但只服务 iOS：三查（libimobiledevice/设备/WDA，:31-159）、`check_model_api`（:162-247，与 main.py 不同的是走 `models.list()` 而非 chat）、设备命令（:371-443）、main（:446-546）。**examples/basic_usage.py** 五个函数：基本任务（:15-41）、回调注入（:44-70）、step 单步（:73-90）、多任务复用（:93-115）、远程设备（:118-149）；`__main__` 只激活第一个，其余注释（:170-190）。**examples/demo_thinking.py** 是 verbose 模式的最小演示（:30-44）。

## ③ 外部连接

main.py 是全仓唯一同时 import 两套 Agent 与三平台清单的地方（:25-34），也是 `set_device_type`（device_factory 模块级单例）的唯一生产调用方。ios.py 只 import iOS 线。examples 演示的是 `phone_agent` 包的公开 API：`PhoneAgent`/`AgentConfig`/`ModelConfig`/`get_messages`（basic_usage.py:9-12），远程设备示例直接用 `phone_agent.adb.ADBConnection`（:120）。环境变量面：`PHONE_AGENT_BASE_URL/MODEL/API_KEY/MAX_STEPS/DEVICE_ID/LANG/DEVICE_TYPE/WDA_URL` 全部在 argparse default 兜底（main.py:405-522）。

## ④ 数据流

典型一次 `python main.py "打开微信发消息"`：parse_args→`set_device_type(DeviceType.ADB)`→体检三查全绿→check_model_api 发 5 token 探活→`ModelConfig`+`AgentConfig` 组装→`PhoneAgent(model_config, agent_config)`→`agent.run(task)` 打印结果（:821-824）。无位置参数时进入交互循环：`input` 收任务→`agent.run`→**`agent.reset()` 清上下文**（:829-843）——多任务不复用历史。`--connect 192.168.1.100:5555` 流（:641-648）：连接成功后把地址写回 `args.device_id` 作为本次默认设备，返回 `not success` 决定是否继续主流程。examples 的 step 模式（basic_usage.py:81-90）展示手动驱动：首步 `agent.step(task)`，之后 `agent.step()` 裸调至 `result.finished` 或计数上限。

## ⑤ 设计决策与陷阱

1. **两个入口、两套模型检查、两种判定**：main.py:743-745 的 `check_model_api` 是**启用**的（chat 探活），ios.py:471-473 的同名调用被**注释停用**——iOS 入口对模型端点不做任何预检，坏 URL 要到首个任务才炸。
2. **探活用 chat 而非 /models**：main.py:299-306 注释明言"chat API 比 /models 通用"；ios.py:192 恰恰用 models.list——后提交的 main.py 版本更稳。
3. **重复代码未合并**：ios.py 的三查/设备命令与 main.py 的 iOS 分支约 300 行近似复制（对照 ios.py:117-150 与 main.py:233-260），改 WDA 提示文案要改两处。
4. **交互循环 quit 语义**：`quit/exit/q` 三别名（main.py:833），Ctrl-C 也优雅退出（:845-847）；但任务中途 Ctrl-C 会穿透到循环层，不会只停单个任务。
5. **examples 是文档不是测试**：`__main__` 默认只跑 example 1（basic_usage.py:170-190），回调/单步/批量/远程四段全注释；取消注释前先确认模型端点与设备就绪，否则连环报错。
6. **`--enable-tcpip` 的地址提示**（main.py:662-679）依赖 `get_device_ip` 解析 `ifconfig`，部分 ROM 输出格式不同会拿不到 IP（提示"Check device WiFi settings"，:678）。
7. **help 即教程**：parse_args 的 epilog 收录 15 条示例命令（main.py:360-401），比 README 更快上手。

## ⑥ 新人提示

第一条命令跑 `python main.py --list-apps`（免体检）看应用清单，再 `python main.py --list-devices`、然后裸 `python main.py` 进交互模式。做产品集成请绕开 CLI，直接抄 examples/basic_usage.py 的 API 用法：回调注入（:44-70）演示了敏感操作确认与人工接管的挂接点，step 单步（:73-90）是调试提示词行为的最佳姿势——配合 demo_thinking.py 的 verbose 输出能看到每步 think/action。iOS 用户从 ios.py 起步即可，但要记得它不检查模型端点。
