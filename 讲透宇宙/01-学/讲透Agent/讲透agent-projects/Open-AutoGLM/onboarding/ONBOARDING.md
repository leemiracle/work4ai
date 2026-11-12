# Open-AutoGLM 新人上手指南（ONBOARDING）

> 基于仓库知识图谱（191 节点/449 边/14 层/15 步 tour）生成，行号锚均经源码核实。

## 1. 项目定位

**一句话**：Open-AutoGLM 是智谱 AutoGLM 手机 GUI Agent 的开源实现——用视觉语言模型（VLM）看手机截图、思考下一步、输出伪代码动作，经 ADB/HDC/WebDriverAgent 三条通道在 Android、鸿蒙、iOS 真机执行自然语言任务。

关键形态：**本体不含模型**，只是"薄编排层 + 三套设备驱动"，默认模型 `autoglm-phone-9b`（`phone_agent/model/client.py:14`），OpenAI 兼容端点（BigModel/ModelScope/SGLang/vLLM）均可接。主文档 `README.md`（约 991 行）是第一入口。

## 2. 技术栈与运行形态

- **依赖极薄**：Python ≥3.10（`setup.py`），运行时仅 Pillow/openai/requests（`requirements.txt`）。
- **模型侧**：OpenAI 兼容流式接口；`ModelClient`（`phone_agent/model/client.py:41`）剥 `<think>` 段流式拉全量，`in_action_phase`（:100-102）只停终端打印**并未断流**（循环无 break，action 标记为 `finish(message=`/`do(action=` :84），记录 TTFT 等指标；`scripts/check_deployment_cn.py` 可携样例直探自部署服务。
- **设备侧**：依赖宿主工具——Android 走 `adb`（中文输入需 ADB Keyboard）、鸿蒙走 `hdc`、iOS 走 WebDriverAgent + go-ios。
- **双形态**：CLI（`main.py` 全平台；`ios.py` iOS 入口）与 Python API（`phone_agent/__init__.py` 只暴露 PhoneAgent/IOSPhoneAgent）。

## 3. 仓库目录速览

```
Open-AutoGLM/
├── main.py / ios.py        # 全平台 CLI / iOS 专用入口
├── phone_agent/            # 核心包（下述文件均在其中）
│   ├── agent.py            # 主编排器（253 行）
│   ├── agent_ios.py        # iOS 对等实现
│   ├── device_factory.py   # 设备抽象工厂（167 行）
│   ├── actions/            # 动作执行 handler*.py
│   ├── model/client.py     # VLM 客户端 + MessageBuilder
│   ├── config/             # 提示词/应用清单/i18n/timing
│   ├── adb/ | hdc/ | xctest/   # 三设备栈（同构，见 §4）
├── examples/  scripts/     # 用例示例；部署验证脚本
└── docs/  resources/       # iOS 指南；隐私政策（中英）
```

## 4. 核心架构（14 层图谱的主线）

**A. Agent 编排核心（L11）**：`PhoneAgent`（`phone_agent/agent.py:42`）实现"截图感知→组装上下文→请求 VLM→解析动作→执行回填"循环：`run()`（agent.py:84）全自动驱动至 finish 或 max_steps，`step()`（agent.py:112）单步控制，`AgentConfig`（agent.py:17）按语言注入默认提示词。iOS 侧 `IOSPhoneAgent`（`phone_agent/agent_ios.py:44`）对等实现。

**B. 动作执行层（L10）**：`ActionHandler`（`phone_agent/actions/handler.py:24`）把伪代码动作（Launch/Tap/Type/Swipe/Wait/Takeover 等）分派到 13 个 `_handle_*`；`parse_action`（handler.py:332）用 **ast.parse 而非 eval** 安全解析；敏感操作前 `confirmation_callback` 确认，`Takeover` 转交 `takeover_callback`；`ActionResult`（handler.py:15）四字段回报。

**C. 设备抽象工厂（L9）**：`DeviceFactory`（`phone_agent/device_factory.py:15`）按 `DeviceType`（ADB/HDC/IOS，:7）延迟加载子包，统一签名转发 15 个设备操作——上层零平台分支；`get_device_factory()`（:157）/`set_device_type()`（:146）模块级单例。

**D. 三设备栈（L6/L7/L8）**：`phone_agent/adb/`、`phone_agent/hdc/`、`phone_agent/xctest/` 严格同构，各含同名四模块（connection/device/input/screenshot），以 adb 为例：`phone_agent/adb/connection.py` 连接与设备枚举、`phone_agent/adb/device.py` 手势与前台应用、`phone_agent/adb/input.py` 文本输入、`phone_agent/adb/screenshot.py` 截图+兜底。共享配置：包名清单（`phone_agent/config/apps.py` 168 条、`apps_harmonyos.py` 100+、`apps_ios.py` Bundle ID）、`phone_agent/config/i18n.py` 双语与 `timing.py` 时序单例。

```
run() → [截图(黑图兜底) → MessageBuilder(剥图) → ModelClient(流式全量)
         → parse_action(ast) → ActionHandler(回调) → DeviceFactory] 循环至 finish
```

## 5. 关键数据流：一条指令的完整旅程

以「打开小红书搜索美食攻略」（`examples/demo_thinking.py`）为例，五步一轮：

1. **入口**：`main.py:main` 解析参数→`set_device_type` 注册→体检→组装 AgentConfig。
2. **感知**：`_execute_step`（`phone_agent/agent.py:136`）取截图——adb 栈 `screencap -p`+`adb pull` 后 PIL 转 base64（`phone_agent/adb/screenshot.py:46`）；敏感页返回黑图标 `is_sensitive=True`（:55），**循环不因截图失败中断**；`get_current_app` 解析 `dumpsys window` 识别前台应用（`phone_agent/adb/device.py`）。
3. **决策**：`MessageBuilder`（`phone_agent/model/client.py:219`）拼系统消息+首帧截图+任务指令（历史剥图）；`ModelClient.request()`（client.py:53）流式拉取到自然结束（**无提前断流**，`</answer>` 仅在 `_parse_response` :209 解析降级用），多级降级解析。
4. **解析与执行**：`parse_action` 解析 `do(action="Tap", element=[x,y])` 伪代码；`ActionHandler.execute()`（`phone_agent/actions/handler.py:45`）分派，相对坐标换算像素，经 DeviceFactory 执行 `input tap` / `uitest uiInput click` / WDA POST。
5. **回填**：动作与结果追加回历史，循环至 finish 或 max_steps。

iOS 线差异：**复用** Android 的 `parse_action`（`phone_agent/agent_ios.py:8` 导入、:210 调用），`IOSActionHandler`（`phone_agent/actions/handler_ios.py:53`）消费同一动作字典做 WDA 调用。

## 6. 新人上手路径（15 步 tour 压缩为 8 个里程碑）

1. **全景**：读 `README.md` 与 `requirements.txt`；AI 助手场景读 `README_coding_agent.md`。
2. **跑通 CLI**：`main.py` 体检→交互循环（run/reset/quit）；iOS 走 `ios.py`。
3. **精读主循环**：`phone_agent/agent.py` 是心脏；配 `phone_agent/config/__init__.py` barrel 建地图。
4. **行为契约**：`phone_agent/config/prompts_zh.py`（及 `prompts_en.py`）定义 `<think>/<answer>` 格式与执行规则（滑动失效反向重试、防死循环）。**勘误**：同目录 `prompts.py` 是无引用死代码——barrel（`phone_agent/config/__init__.py:6-7`）只导出 prompts_en/prompts_zh 两件。
5. **模型客户端**：`phone_agent/model/client.py` 流式与 TTFT；`phone_agent/config/i18n.py` 双语。
6. **动作与工厂**：`phone_agent/actions/handler.py` + `phone_agent/device_factory.py`——ast 解析、双回调、延迟加载。
7. **三栈对照**：`phone_agent/adb/`（最常用）→ `phone_agent/hdc/`（同构）→ `phone_agent/xctest/` + `phone_agent/agent_ios.py` + `docs/ios_setup/ios_setup.md`。
8. **配置收尾**：`phone_agent/config/apps.py`、`phone_agent/config/timing.py`、`scripts/check_deployment_cn.py`；产品化前读 `resources/privacy_policy.txt`。

## 7. 设计决策与陷阱（源码锚实证）

1. **ast.parse 而非 eval**（`phone_agent/actions/handler.py:362`，`ast.literal_eval` :371）：模型输出是伪代码字符串，只取字面量，不可信代码不得直接执行。
2. **流式拉全量 + 历史剥图**（`phone_agent/model/client.py:88-140`、MessageBuilder :219）：**勘误**——流式循环无 break（`</answer>` 提前断流省 token 的说法与源码不符，`in_action_phase` :100-102 只停打印），每步新截图、旧图全剥。
3. **同构四件套 + 工厂延迟加载**（`phone_agent/device_factory.py:15`）：代价是 iOS 另有 `phone_agent/agent_ios.py` 平行实现，改动作协议要同步两处。
4. **中文输入三套方案**：Android 依赖 ADB Keyboard，base64 广播注入（`phone_agent/adb/input.py:30`）；鸿蒙 `uitest uiInput text` 多行拆分+keyEvent 2054+转义（`phone_agent/hdc/input.py:36,45`）；iOS WDA value 逐字分帧，长文本走剪贴板 `set_pasteboard`（`phone_agent/xctest/input.py:241`）。
5. **截图多级兜底**：adb 敏感页黑图（`phone_agent/adb/screenshot.py:55`）；hdc 回退 `snapshot_display`（`phone_agent/hdc/screenshot.py:62`）；iOS 三级降级——截图失败绝不打断循环。
6. **坐标多层换算勿混淆**：模型 0-1000 相对坐标→handler 层转逻辑像素（`phone_agent/actions/handler_ios.py:118-123`）；iOS 栈内再乘 `SCALE_FACTOR=3`（`phone_agent/xctest/device.py:9`）。
7. **时序集中配置**：`TIMING_CONFIG` 单例（`phone_agent/config/timing.py`，DeviceTimingConfig :38）控制动作后 sleep，`PHONE_AGENT_*` 环境变量可覆盖。
8. **陷阱**：① 鸿蒙 `detect_and_set_adb_keyboard` 是 placeholder 只读不切换；② `scripts/sample_messages.json` 的 system 消息是提示词**静态快照**（日期硬编码），改 prompts 后漂移；③ `get_current_app` 未识别包名返回 "System Home"（`phone_agent/adb/device.py`）。
9. **安全隐私是产品边界**：`resources/privacy_policy.txt` 定义 6+1 类高风险操作强制确认与五类禁止行为，正对应 handler 双回调——二次开发必须保留。

## 8. 延伸阅读

**DeepWiki（43 页全量归档于 `../deepwiki/`）**：`1-overview.md`、`3.3-agent-execution-loop.md`、`3.4-ai-model-integration.md`（主循环）；`4.1-android-adb.md` / `4.2-harmonyos-hdc.md` / `4.3-ios-webdriveragent.md`（三栈）；`8.2-self-hosting-models.md`、`8.3-deployment-verification.md`（自部署）。

**源码按序精读**：`phone_agent/agent.py`（253 行）→ `phone_agent/actions/handler.py`（399 行）→ `phone_agent/device_factory.py`（167 行）→ `phone_agent/model/client.py`（290 行）→ 三设备栈 → `main.py`（853 行）与 `ios.py` → `examples/basic_usage.py`。

**背景**：AutoGLM 论文引用见 `README.md` 尾部；iOS 通道源自 PR141 与 Gekowa 社区分支。
