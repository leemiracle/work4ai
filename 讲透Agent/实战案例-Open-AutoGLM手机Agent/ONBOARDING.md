# Open-AutoGLM 新成员 Onboarding 指南

> 本指南基于源码级知识图谱自动生成，目标是让新加入团队成员在 2-4 小时内对项目有完整的架构认知。
> 配套阅读：[`docs/`](.) 下的 11 篇技术文档（共约 4900 行，覆盖所有模块）。
> 知识图谱：`.understand-anything/knowledge-graph.json`（83 节点 / 127 边 / 12 层 / 12 步 tour）。

---

## 1. Project Overview（项目概览）

| 字段 | 值 |
|------|-----|
| **项目名** | Open-AutoGLM（PyPI 包名 `phone-agent`）|
| **定位** | 基于 AutoGLM-Phone-9B 视觉语言模型的手机 GUI Agent 框架 |
| **核心抽象** | 截图 → 视觉模型决策 → 设备执行 → 回填上下文 → 循环 |
| **支持平台** | Android（ADB）/ HarmonyOS（HDC）/ iOS（XCTest/WDA）|
| **主要语言** | Python 3.10+ |
| **其他语言** | Markdown（文档）、YAML（CI/pre-commit）、JSON（测试数据）、TXT（隐私政策）|
| **关键依赖** | openai SDK（HTTP API）、Pillow（图片）、requests（仅 iOS） |
| **可选推理引擎** | vLLM / SGLang（本地部署）、智谱 BigModel / ModelScope（云端）|
| **代码规模** | ~8300 行 Python / 41 个 .py 文件 |
| **当前 commit** | `86f5538` |

**项目特点**：
- 项目本身**不含模型**，通过 OpenAI 兼容 HTTP API 调用模型服务
- 三平台**平行实现**（adb/hdc/xctest 三套目录结构相同，重复度 70-80%，无共同基类）
- 内置**敏感操作确认**（confirmation_callback）与**人工接管**（takeover_callback）双回调机制
- 支持**远程 WiFi 调试**（adb connect / hdc tconn / WDA URL）

---

## 2. Architecture Layers（12 个架构层）

整个项目按职责分成 12 层。从上到下，越靠近用户越抽象，越靠近设备越具体。

### 2.1 入口与 CLI 层（`layer:entry-cli`，8 节点）

**职责**：用户交互入口。解析 CLI 参数、自检环境、路由到对应平台的 Agent。

| 文件 | 行数 | 角色 |
|------|------|------|
| `main.py` | 853 | **统一 CLI 入口**（Android/HarmonyOS/iOS 三平台）。注册 `phone-agent` 命令。 |
| `ios.py` | 550 | iOS 独立 CLI（历史遗留，与 `main.py --device-type ios` 重叠）。 |
| `setup.py` | 49 | 包定义。注册 `phone-agent` console_script。 |
| `requirements.txt` | 20 | 运行时依赖清单（Pillow + openai + iOS 的 requests）。 |
| `.pre-commit-config.yaml` | 23 | Git pre-commit hooks（ruff + typos + pymarkdown）。 |
| `README.md` | 991 | 中文主 README（含面向 AI 的自动化部署章节）。 |
| `README_en.md` | 933 | 英文 README。 |
| `README_coding_agent.md` | 430 | 面向 coding agent 的 README。 |

### 2.2 Agent 核心层（`layer:core-agent`，9 节点）

**职责**：PhoneAgent / IOSPhoneAgent 主类。编排感知-动作循环。

| 文件 / 类 | 行数 | 角色 |
|----------|------|------|
| `phone_agent/agent.py` | 253 | **PhoneAgent 主类**（Android/HarmonyOS）。 |
| `phone_agent/agent_ios.py` | 277 | IOSPhoneAgent（与 agent.py 重复度 ~90%）。 |
| `phone_agent/__init__.py` | 12 | 包导出 PhoneAgent + IOSPhoneAgent。 |
| `class PhoneAgent` | — | 提供 run/step/_execute_step 三层 API。 |
| `class AgentConfig` | — | dataclass：max_steps/device_id/lang/system_prompt/verbose。 |
| `class StepResult` | — | dataclass：success/finished/action/thinking/message。 |
| `class IOSPhoneAgent` | — | iOS 版，自动创建 WDA session。 |
| `concept: perception-action-loop` | — | 截图→决策→执行→回填→循环的核心抽象。 |
| `concept: image-once-consumption` | — | 每步只保留最新截图，历史截图即时移除（省 token 80%+）。 |

### 2.3 动作执行层（`layer:action-processing`，7 节点）

**职责**：Agent 决策与设备执行之间的桥梁。

| 文件 / 类 / 函数 | 行数 | 角色 |
|----------------|------|------|
| `phone_agent/actions/handler.py` | 399 | **ActionHandler** + parse_action + do/finish 辅助。 |
| `phone_agent/actions/handler_ios.py` | 280 | IOSActionHandler（WDA 直连）。 |
| `phone_agent/actions/__init__.py` | 5 | 导出 ActionHandler + ActionResult。 |
| `class ActionHandler` | — | 调度 14 个 handler，含坐标转换 + 双回调注入。 |
| `function parse_action` | — | 模型响应字符串 → dict（ast 安全解析）。 |
| `class ActionResult` | — | dataclass：success/should_finish/message。 |
| `concept: autoglm-action-protocol` | — | do(action="Tap", element=[500,300]) 函数调用风格协议。 |

### 2.4 AI 模型客户端层（`layer:ai-model`，6 节点）

**职责**：与 OpenAI 兼容 VLM 服务通信。

| 文件 / 类 | 行数 | 角色 |
|----------|------|------|
| `phone_agent/model/client.py` | 290 | **ModelClient** 流式 + MessageBuilder。 |
| `phone_agent/model/__init__.py` | 5 | 只导出 ModelClient + ModelConfig。 |
| `class ModelClient` | — | 流式请求 + 实时分离 thinking/action（marker 检测器）。 |
| `class ModelConfig` | — | base_url/api_key/model_name=autoglm-phone-9b/max_tokens=3000/temperature=0.0 等。 |
| `class ModelResponse` | — | thinking/action/raw_content + 3 项性能指标。 |
| `class MessageBuilder` | — | 构造 OpenAI 多模态消息（图前文后）+ remove_images_from_message。 |

### 2.5 设备抽象层（`layer:device-abstraction`，3 节点）

**职责**：DeviceFactory 工厂 + 全局单例。**注意**：iOS 不走此工厂（架构债）。

| 文件 / 类 | 行数 | 角色 |
|----------|------|------|
| `phone_agent/device_factory.py` | 167 | **DeviceFactory** + 全局单例 set/get_device_factory。 |
| `class DeviceFactory` | — | lazy-load adb/hdc 模块，纯转发方法。 |
| `class DeviceType` | — | 枚举：ADB/HDC/IOS。 |

### 2.6 Android 平台层 ADB（`layer:platform-android`，5 节点）

**职责**：Android 设备的 subprocess 命令实现。

| 文件 | 行数 | 角色 |
|------|------|------|
| `phone_agent/adb/__init__.py` | 51 | 统一接口导出。 |
| `phone_agent/adb/connection.py` | 353 | ADBConnection + 设备列举/远程连接。 |
| `phone_agent/adb/device.py` | 252 | tap/swipe/launch_app（adb shell input + monkey）。 |
| `phone_agent/adb/input.py` | 109 | ADB Keyboard 文本输入（base64 + am broadcast）。 |
| `phone_agent/adb/screenshot.py` | 109 | 两步截图（screencap + adb pull）。 |

### 2.7 HarmonyOS 平台层 HDC（`layer:platform-harmonyos`，5 节点）

**职责**：HarmonyOS 设备的 subprocess 命令实现。结构与 ADB 平行。

| 文件 | 行数 | 角色 |
|------|------|------|
| `phone_agent/hdc/__init__.py` | 53 | 统一接口导出。 |
| `phone_agent/hdc/connection.py` | 381 | HDCConnection（与 ADBConnection 几乎相同）。 |
| `phone_agent/hdc/device.py` | 310 | uitest uiInput click/swipe/keyEvent。 |
| `phone_agent/hdc/input.py` | 149 | 原生 uitest uiInput text（支持中文，无需 ADB Keyboard）。 |
| `phone_agent/hdc/screenshot.py` | 125 | snapshot_display + hdc file recv。 |

### 2.8 iOS 平台层 XCTest/WDA（`layer:platform-ios`，5 节点）

**职责**：iOS 设备的 HTTP API 实现。**差异最大**：有状态 WDA session、坐标缩放、双 fallback 截图。

| 文件 | 行数 | 角色 |
|------|------|------|
| `phone_agent/xctest/__init__.py` | 47 | 统一接口导出（签名多 wda_url/session_id）。 |
| `phone_agent/xctest/connection.py` | 382 | XCTestConnection + WDA session + pair + libimobiledevice。 |
| `phone_agent/xctest/device.py` | 458 | **最大单文件**。WDA Actions API + SCALE_FACTOR=3 缩放。 |
| `phone_agent/xctest/input.py` | 299 | WDA /wda/keys + 剪贴板 + 键盘检测（6 个未导出函数）。 |
| `phone_agent/xctest/screenshot.py` | 230 | 双 fallback：WDA → idevicescreenshot → 黑图。 |

### 2.9 配置层（`layer:configuration`，9 节点）

**职责**：横切关注点（apps / prompts / i18n / timing）。

| 文件 | 行数 | 角色 |
|------|------|------|
| `phone_agent/config/__init__.py` | 53 | 包导出 + get_system_prompt(lang) 路由。 |
| `phone_agent/config/apps.py` | 226 | **Android 168 个 app** 中文名 → package name。 |
| `phone_agent/config/apps_harmonyos.py` | 266 | **HarmonyOS 154 个 app** + APP_ABILITIES（39 项）。 |
| `phone_agent/config/apps_ios.py` | 339 | **iOS 182 个 app** + iTunes Lookup API（3 个独有函数）。 |
| `phone_agent/config/prompts_zh.py` | 77 | 中文 system prompt（15 动作 + 18 条规则，~1200 token）。 |
| `phone_agent/config/prompts_en.py` | 79 | 英文 system prompt（7 动作 + 3 条规则，~650 token）。 |
| `phone_agent/config/prompts.py` | 75 | ⚠ **遗留废弃**（与 prompts_zh.py 95% 相同，无人 import）。 |
| `phone_agent/config/i18n.py` | 81 | 22 个 key × 中/英（UI 终端消息，不影响模型行为）。 |
| `phone_agent/config/timing.py` | 167 | 14 个时间常量 + 环境变量覆盖。 |

### 2.10 脚本与 CI 层（`layer:scripts-deployment`，7 节点）

**职责**：部署验证脚本 + GitHub Issue/PR 模板。

| 文件 | 行数 | 角色 |
|------|------|------|
| `scripts/check_deployment_cn.py` | 115 | 中文部署验证脚本。 |
| `scripts/check_deployment_en.py` | 129 | 英文部署验证脚本。 |
| `scripts/sample_messages.json` | 20 | 中文测试消息（含截图 + 比价任务）。 |
| `scripts/sample_messages_en.json` | 20 | 英文测试消息。 |
| `.github/ISSUE_TEMPLATE/bug_report.yaml` | 72 | bug 报告模板。 |
| `.github/ISSUE_TEMPLATE/feature-request.yaml` | 34 | 功能请求模板。 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 40 | PR 模板。 |

### 2.11 示例层（`layer:examples`，2 节点）

**职责**：Python API 用法示例。

| 文件 | 行数 | 角色 |
|------|------|------|
| `examples/basic_usage.py` | 190 | 5 种用法：基础/回调/单步/批量/远程。 |
| `examples/demo_thinking.py` | 64 | verbose 模式最小 demo。 |

### 2.12 文档层（`layer:documentation`，17 节点）

**职责**：11 篇源码级技术文档集（共约 4900 行）+ iOS 配置 + 法律文档。

| 文档 | 行数 | 内容 |
|------|------|------|
| `docs/README.md` | 128 | 文档集索引页。 |
| `docs/ARCHITECTURE.md` | 413 | ★ 总体架构 + 6 层视图 + mermaid 时序图 + 10 条 DeepWiki 勘误。 |
| `docs/EXTENDING.md` | 552 | ★ 二次开发指南 + 统一设备抽象建议。 |
| `docs/01-entry-cli.md` | 345 | main.py 全流程 + 所有 CLI 参数。 |
| `docs/02-agent-loop.md` | 372 | PhoneAgent 核心 + _execute_step 六段拆解。 |
| `docs/03-device-layer.md` | 453 | DeviceFactory + adb/hdc/xctest 三套对照。 |
| `docs/04-action-handler.md` | 408 | AutoGLM 协议 + parse_action + 14 种 handler。 |
| `docs/05-model-client.md` | 402 | ModelClient 流式解析 + 换模型指南。 |
| `docs/06-config-prompts.md` | 371 | apps×3 + prompts×3 + i18n + timing。 |
| `docs/07-deployment.md` | 432 | 三种部署路径 + vLLM/SGLang 完整参数。 |
| `docs/08-development.md` | 473 | setup.py + pre-commit + PR + 10 项已知问题。 |
| `docs/09-remote-advanced.md` | 547 | 远程设备 + 交互模式 + 4 种回调实战。 |
| `docs/ios_setup/ios_setup.md` | 134 | iOS 环境配置（WebDriverAgent 部署）。 |
| `resources/WECHAT.md` | 6 | 微信社区资源。 |
| `resources/privacy_policy.txt` | 131 | 中文隐私政策。 |
| `resources/privacy_policy_en.txt` | 133 | 英文隐私政策。 |
| `concept: three-platform-parallels` | — | 三平台平行实现抽象。 |

---

## 3. Key Concepts（关键概念）

### 3.1 感知-动作循环（perception-action-loop）

```
截图 → 组消息 → 模型决策 → 解析动作 → 执行动作 → 回填上下文 → 循环
```

整个项目的核心抽象。终止条件：模型主动 `finish(...)` 或步数耗尽（默认 max_steps=100）。

**实现位置**：`PhoneAgent._execute_step`（`agent.py:136-243`）

### 3.2 AutoGLM 动作协议（autoglm-action-protocol）

模型输出**非 JSON、非 tool_call**，而是 Python 函数调用风格字符串：

```
do(action="Tap", element=[500, 300])
do(action="Tap", element=[500, 300], message="确认支付 ¥99.00")  # 敏感操作
do(action="Type", text="无线耳机")
do(action="Swipe", start=[500, 800], end=[500, 200])
finish(message="已成功下单")
```

- **坐标系**：`[0-1000, 0-1000]` 相对值（跨设备复用），handler 转 pixels
- **iOS 多一层缩放**：WDA 用逻辑 points，截图是物理 pixels，`SCALE_FACTOR = 3`
- **带 message 的 Tap** 触发 sensitive 操作确认

**实现位置**：`parse_action`（`handler.py:332`）

### 3.3 图片一次性消费（image-once-consumption）

VLM 推理贵在图片 token。Agent 采取「每步只保留最新截图，历史截图即时移除」策略：

```python
# agent.py:205
self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])
```

**效果**：上下文中永远只有最新一步的截图。token 节省 80%+。

### 3.4 三平台平行实现（three-platform-parallels）

`adb/` / `hdc/` / `xctest/` 三套目录结构完全相同（connection/device/input/screenshot），代码重复度 70-80%，**无共同基类**。

| 平台 | 后端 | 接入方式 | 走 DeviceFactory? |
|------|------|---------|------------------|
| Android | adb/ | subprocess `adb shell` | ✅ |
| HarmonyOS | hdc/ | subprocess `hdc shell uitest` | ✅ |
| iOS | xctest/ | HTTP WebDriverAgent + `idevice*` | ❌（独立路径） |

**架构债**：iOS 不走 DeviceFactory 是历史遗留。改进方向：用 Protocol 抽象统一三平台（详见 `docs/EXTENDING.md` 的"统一设备抽象建议"）。

---

## 4. Guided Tour（12 步学习路径）

按推荐顺序阅读，每步 15-30 分钟，全程约 4-6 小时。

| Step | 主题 | 关键文件 | 时长 |
|------|------|---------|------|
| 1 | **从 README 开始** | `README.md` + `docs/ARCHITECTURE.md` | 30min |
| 2 | **入口：python main.py 全流程** | `main.py` + `docs/01-entry-cli.md` | 30min |
| 3 | **PhoneAgent：感知-动作循环** | `agent.py` + PhoneAgent/AgentConfig/StepResult + `docs/02-agent-loop.md` | 45min |
| 4 | **AutoGLM 动作协议** | 两个 concept | 15min |
| 5 | **parse_action：字符串→dict 安全解析** | `handler.py` + parse_action/ActionHandler + `docs/04-action-handler.md` | 30min |
| 6 | **14 种 handler 与双回调** | ActionHandler + `handler_ios.py` + `docs/09-remote-advanced.md` | 30min |
| 7 | **ModelClient：流式响应实时分离** | `client.py` + ModelClient/Config/Response/MessageBuilder + `docs/05-model-client.md` | 45min |
| 8 | **DeviceFactory：不完整的统一抽象** | `device_factory.py` + `docs/03-device-layer.md` + `docs/EXTENDING.md` | 30min |
| 9 | **三平台平行实现对照** | adb/hdc/xctest 各自的 connection + input | 60min |
| 10 | **配置层** | `config/*` 8 个文件 + `docs/06-config-prompts.md` | 30min |
| 11 | **部署模型服务** | `scripts/check_deployment_*` + sample_messages + `docs/07-deployment.md` | 30min |
| 12 | **二次开发与贡献** | `docs/EXTENDING.md` + `docs/08-development.md` + setup.py + pre-commit | 30min |

---

## 5. File Map（按层组织的文件清单）

完整文件清单参见上面 §2 的 12 层表格。**所有 ONBOARDING 涉及的文件**（去重后）：

### 核心源码（必读，按重要性排序）

1. `main.py` — CLI 入口
2. `phone_agent/agent.py` — PhoneAgent 主类（complex）
3. `phone_agent/agent_ios.py` — iOS Agent（complex）
4. `phone_agent/actions/handler.py` — ActionHandler + parse_action（complex）
5. `phone_agent/actions/handler_ios.py` — iOS ActionHandler
6. `phone_agent/model/client.py` — ModelClient 流式（complex）
7. `phone_agent/device_factory.py` — DeviceFactory
8. `phone_agent/adb/{connection,device,input,screenshot}.py` — Android 4 文件
9. `phone_agent/hdc/{connection,device,input,screenshot}.py` — HarmonyOS 4 文件
10. `phone_agent/xctest/{connection,device,input,screenshot}.py` — iOS 4 文件（device.py 最大 458 行，complex）
11. `phone_agent/config/{__init__,apps,apps_harmonyos,apps_ios,prompts_zh,prompts_en,prompts,i18n,timing}.py` — 配置 9 文件
12. `ios.py` — iOS 独立入口
13. `examples/{basic_usage,demo_thinking}.py` — 示例 2 文件
14. `scripts/{check_deployment_cn,check_deployment_en}.py` — 验证脚本 2 文件
15. 各 `__init__.py`（5 个 phone_agent 子包 + 1 个顶层）

### 配置文件

- `setup.py`, `requirements.txt`, `.pre-commit-config.yaml`
- `scripts/sample_messages.json`, `scripts/sample_messages_en.json`
- `.github/ISSUE_TEMPLATE/{bug_report,feature-request}.yaml`, `.github/PULL_REQUEST_TEMPLATE.md`

### 文档

- `README.md`, `README_en.md`, `README_coding_agent.md`
- `docs/` 下 13 个 md 文件（含 README + ARCHITECTURE + EXTENDING + 9 编号 + iOS setup）
- `resources/{WECHAT.md,privacy_policy.txt,privacy_policy_en.txt}`

**总计：约 50 个独立文件**（41 .py + 6 .yaml/.json + 17 .md/.txt + 配置）。

---

## 6. Complexity Hotspots（复杂度热点）

新成员应**特别小心**以下 complex 节点（建议在导师陪同下阅读）：

| 节点 | 类型 | 行数 | 为什么复杂 |
|------|------|------|-----------|
| `phone_agent/xctest/device.py` | file | **458** | 最大单文件。WDA Actions API 多步 pointer 事件 + SCALE_FACTOR 缩放，最容易写错坐标。 |
| `phone_agent/actions/handler.py` | file | 399 | AST 解析有 3 条分支（Type 特殊路径 + do AST + finish 切分），出错难调试。 |
| `phone_agent/xctest/connection.py` | file | 382 | iOS 独有 WDA session 管理 + libimobiledevice 多工具配合。 |
| `main.py` | file | 853 | CLI 入口，分支多（3 平台 × 多个子命令）。 |
| `ios.py` | file | 550 | 与 main.py 重叠的历史遗留，容易混淆。 |
| `phone_agent/model/client.py` | file | 290 | 流式 marker 检测算法（带缓冲 + 前缀检测）很绕。 |
| `phone_agent/agent.py` | file | 253 | _execute_step 6 段逻辑，context 管理微妙。 |
| `phone_agent/agent_ios.py` | file | 277 | 与 agent.py 90% 重复，但有 WDA session 创建等差异。 |
| `class PhoneAgent` | class | — | Agent 核心，组合 ModelClient + ActionHandler + DeviceFactory。 |
| `class IOSPhoneAgent` | class | — | iOS 版，启动自动创建 WDA session，agent_ios.py:222 有重复打印 thinking bug。 |
| `class ActionHandler` | class | — | 14 handler 调度 + 坐标转换 + 双回调。 |
| `class ModelClient` | class | — | 流式 + marker 检测 + 性能指标采集。 |

**已知的代码质量问题**（贡献机会）：
- `agent_ios.py:222` 重复打印 thinking（流式已打 + 这里又打）
- `handler.py:345` debug print 残留
- `handler.py:258-318` `_send_keyevent` 死代码
- `xctest/device.py:9` `SCALE_FACTOR = 3` 硬编码（1x/2x 设备会算错）
- `setup.py:17` url 还是 `yourusername/phone-agent` 占位符
- `setup.py:32-35` install_requires 漏 `requests`（iOS 用户会 ImportError）
- `setup.py:36-43` extras_require[dev] 同时含 black + ruff（formatter 冲突）
- `.pre-commit-config.yaml:4-5` 两个 `exclude:` key，后者覆盖前者
- `phone_agent/config/prompts.py` 遗留废弃文件（应删）
- `.github/PULL_REQUEST_TEMPLATE.md:31-39` 引用不存在的 `glmv-reward/` 目录
- 没有 `tests/` 目录（虽然 README 提到）

---

## 7. 快速开始（5 分钟跑通）

### 7.1 环境准备

```bash
# 1. 克隆 + 进入
git clone https://github.com/zai-org/Open-AutoGLM.git
cd Open-AutoGLM

# 2. 虚拟环境
python -m venv venv && source venv/bin/activate

# 3. 安装
pip install -r requirements.txt && pip install -e .

# 4. 验证 ADB（Android）/ HDC（HarmonyOS）/ idevice（iOS）已装且设备连上
adb devices  # 或 hdc list targets  或 idevice_id -ln
```

### 7.2 模型服务（三选一）

| 方案 | 命令 |
|------|------|
| **智谱 BigModel**（推荐新手） | `python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model autoglm-phone --apikey sk-xxx "..."` |
| **ModelScope** | `python main.py --base-url https://api-inference.modelscope.cn/v1 --model ZhipuAI/AutoGLM-Phone-9B --apikey sk-xxx "..."` |
| **本地 vLLM** | 见 `docs/07-deployment.md` 的完整参数（需 24GB+ VRAM） |

### 7.3 跑第一个任务

```bash
# 交互模式
python main.py --base-url http://your-model-server/v1

# 单任务
python main.py "打开微信发消息给文件传输助手：部署成功"

# 列支持的应用
python main.py --list-apps
```

---

## 8. 下一步

- **想加深理解**：按 §4 Guided Tour 顺序读 12 步
- **想做贡献**：先看 §6 的「已知代码质量问题」清单（10 项易上手的贡献机会），再读 `docs/08-development.md` 的 PR 流程
- **想做二次开发**：读 `docs/EXTENDING.md` 的扩展指南（加动作/平台/app/回调）
- **想可视化架构**：运行 `/understand-dashboard` 启动交互式仪表盘查看知识图谱

---

## 9. 维护

- 本文档基于知识图谱 `.understand-anything/knowledge-graph.json` 自动生成
- 知识图谱基于 commit `86f5538`（2026-08-11）
- 项目代码变更后重跑 `/understand` 更新图谱，再重跑 `/understand-onboard` 重新生成本文档
- 如发现错误：欢迎提 issue 或 PR 到 [zai-org/Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)
