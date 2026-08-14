# Open-AutoGLM 文档集

> 本目录是 Open-AutoGLM 的**源码级技术文档**，面向想理解架构或二次开发的开发者。
> 如果只想安装使用，请看根目录的 [../README.md](../README.md)。

## 快速导航

### 按目标选文档

| 我想... | 看哪篇 |
|--------|-------|
| 理解整体架构 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 改 Agent 循环逻辑 | [02-agent-loop.md](02-agent-loop.md) |
| 调试设备控制 / 加新平台 | [03-device-layer.md](03-device-layer.md) |
| 加新动作 / 改协议 | [04-action-handler.md](04-action-handler.md) |
| 换模型 / 调流式 | [05-model-client.md](05-model-client.md) |
| 加 app / 改 prompt / 调时间 | [06-config-prompts.md](06-config-prompts.md) |
| **部署模型服务**（vLLM/SGLang/第三方）| [07-deployment.md](07-deployment.md) |
| **做开发/贡献代码**（pre-commit/测试/PR）| [08-development.md](08-development.md) |
| **远程设备 / 交互模式 / 自定义回调** | [09-remote-advanced.md](09-remote-advanced.md) |
| 理解 `python main.py` 全流程 | [01-entry-cli.md](01-entry-cli.md) |
| 二次开发（扩展） | [EXTENDING.md](EXTENDING.md) |
| iOS 安装 | [ios_setup/ios_setup.md](ios_setup/ios_setup.md) |

### 按角色选文档

| 角色 | 推荐阅读顺序 |
|------|------------|
| **新人入门** | ARCHITECTURE → 07（部署）→ 02（循环） |
| **想加新 app** | 06（"添加新 app 的步骤"小节）|
| **想做 Android/HarmonyOS 扩展** | ARCHITECTURE → 02 → 04 → 03 → EXTENDING |
| **想做 iOS 扩展** | ARCHITECTURE → 02 → 04 → 03（"iOS 特殊点"）→ EXTENDING |
| **想换模型** | 05（"换模型的注意事项"）→ 07 |
| **想本地部署模型** | 07（完整指南）|
| **想做远程/无人值守** | 09（远程设备 + 回调实战）|
| **想统一三平台抽象** | 03（"代码重复度评估"） → EXTENDING（"统一设备抽象建议"）|
| **想贡献代码 / 提 PR** | 08（含"已知问题"清单）|

## 文档清单

| # | 文件 | 行数 | 内容摘要 |
|---|------|------|---------|
| ★ | [ARCHITECTURE.md](ARCHITECTURE.md) | ~440 | 总体架构、6 层视图、数据流时序、模块依赖、设计决策、DeepWiki 勘误 |
| 1 | [01-entry-cli.md](01-entry-cli.md) | ~345 | `main.py` / `ios.py` 入口、CLI 参数、自检流程 |
| 2 | [02-agent-loop.md](02-agent-loop.md) | ~370 | PhoneAgent 核心、run/step/\_execute\_step、上下文管理、iOS 差异 |
| 3 | [03-device-layer.md](03-device-layer.md) | ~453 | DeviceFactory、adb/hdc/xctest 三套对照、连接类、截图、输入法 |
| 4 | [04-action-handler.md](04-action-handler.md) | ~410 | AutoGLM 协议、6 大动作分类、parse_action、14 种 handler、坐标转换 |
| 5 | [05-model-client.md](05-model-client.md) | ~402 | ModelClient 流式解析、性能指标、MessageBuilder、换模型指南 |
| 6 | [06-config-prompts.md](06-config-prompts.md) | ~371 | apps×3、prompts×3、i18n、timing、添加 app/语言步骤 |
| 7 | [07-deployment.md](07-deployment.md) | ~440 | 三种部署路径、vLLM/SGLang 完整参数、验证脚本、故障排查、性能调优 |
| 8 | [08-development.md](08-development.md) | ~430 | setup.py、pre-commit（Ruff/Typos/PyMarkdown）、测试、PR 流程、已知问题 |
| 9 | [09-remote-advanced.md](09-remote-advanced.md) | ~440 | 远程设备（WiFi 调试）、交互模式、4 种回调实战（Web/Slack/日志/超时）|
| ★ | [EXTENDING.md](EXTENDING.md) | ~552 | 加动作/平台/回调/prompt 语言/模型、架构改进建议 |

★ = 核心必读

## 文档约定

- **语言**：中文叙述，代码、API、技术术语保留英文
- **图**：架构与时序用 [mermaid](https://mermaid.js.org/) 语法，GitHub/VS Code 原生渲染
- **行号引用**：`文件名:行号` 格式（如 `agent.py:84`），方便对照源码
- **代码片段**：每段不超过 30 行，关键逻辑配注释
- **配套源码版本**：本文档基于 commit `86f553`（2026-08-11 检出，与 [DeepWiki](https://deepwiki.com/zai-org/Open-AutoGLM) 同步）

## 核心概念速查

| 术语 | 含义 | 出现于 |
|------|------|-------|
| **AutoGLM 协议** | 模型输出 `do(action=..., ...)` / `finish(message=...)` 字符串 | 04 |
| **_metadata** | parser 注入的字段，标识 `"do"` 或 `"finish"` | 04 |
| **相对坐标** | 模型输出 `[0-1000, 0-1000]`，handler 转像素 | 04 |
| **SCALE_FACTOR** | iOS 坐标除以 3（物理像素 → 逻辑像素）| 03 |
| **图片一次性消费** | 历史截图即时移除，只保留最新一张 | 02 |
| **WDA** | WebDriverAgent，iOS 自动化 HTTP 服务 | 03 |
| **ADB Keyboard** | Android 命令行输入中文用的第三方输入法 | 03, 06 |
| **DeviceFactory** | 全局单例，路由 adb/hdc（不支持 iOS） | 03 |
| **confirmation_callback** | 敏感操作确认回调 | 04, 09 |
| **takeover_callback** | 人工接管回调（登录/验证码） | 04, 09 |
| **phone-agent** | `pip install` 后注册的命令（等同 `python main.py`）| 08 |
| **TIMING_CONFIG** | 14 个时间常量，环境变量可覆盖 | 06 |
| **MAX_PIXELS=5000000** | vLLM/SGLang 部署的关键参数，容纳高分辨率截图 | 07 |

## 一图看完

整个项目的核心循环（来自 ARCHITECTURE.md）：

```
截图 → 模型决策 → 解析动作 → 执行动作 → 回填上下文 → 循环
```

具体见 [ARCHITECTURE.md](ARCHITECTURE.md#一次-agent-step-的数据流核心) 的完整时序图。

## 与 DeepWiki 的关系

[DeepWiki](https://deepwiki.com/zai-org/Open-AutoGLM) 提供了项目自动生成的 wiki（10 章 30+ 子页面），覆盖范围广但有若干错误。本文档集：

- **以源码为唯一真相**，DeepWiki 内容仅作参考与补充
- **修正了 DeepWiki 的 10 处错误**（见 [ARCHITECTURE.md 附录](ARCHITECTURE.md#附录与-deepwiki-的差异勘误)）
- **吸收了 DeepWiki 的好组织**（6 层架构、动作 6 大分类、平台对照矩阵）
- **补全了 DeepWiki 没覆盖的实战内容**（部署、开发、远程、回调）

## 维护

- **发现错误**：欢迎提 issue 或 PR 到 [zai-org/Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)
- **源码变更后**：检查文档行号引用是否失效（用 `grep -n "agent.py:" docs/` 等核对）
- **加新文档**：放在本目录，文件名用 `NN-主题.md` 格式（NN 是序号），并更新本 README 的表格

## 文档树

```
docs/
├── README.md                ← 你在这里(索引页)
├── ARCHITECTURE.md          ★ 总体架构(含 DeepWiki 勘误)
├── 01-entry-cli.md          入口与 CLI
├── 02-agent-loop.md         核心循环
├── 03-device-layer.md       设备抽象
├── 04-action-handler.md     动作执行器
├── 05-model-client.md       模型客户端
├── 06-config-prompts.md     配置与 Prompt
├── 07-deployment.md         模型部署完整指南 ★
├── 08-development.md        开发指南(pre-commit/tests/PR) ★
├── 09-remote-advanced.md    远程设备 + 交互模式 + 回调实战 ★
├── EXTENDING.md             二次开发
└── ios_setup/               iOS 安装指南(项目原有)
    └── ios_setup.md
```

★ = 本次更新新增

---
