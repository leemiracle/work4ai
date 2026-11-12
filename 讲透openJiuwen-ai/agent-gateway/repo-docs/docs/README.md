# Agent Gateway 文档

本文档汇总 Agent Gateway 的安装、使用、参考与设计说明。中文为权威源，英文版本结构与内容对称。

## 文档覆盖范围

- **Tutorial（教程）**：面向首次使用者，按步骤完成一次可运行的验证。
- **How-to（操作指南）**：解决具体任务，如本地验证、配置渠道、运行多实例。
- **Reference（参考）**：查询命令行参数、环境变量、配置项与协议字段。
- **Explanation（解释）**：理解 Gateway 的定位、数据流、模块划分与设计决策。

## Tutorial

| 文档 | 说明 |
| --- | --- |
| [01-quick-start](zh/tutorial/01-quick-start.md) | 用 Mock AgentServer 在本地跑通 Gateway，并完成一次 `chat.send` 往返 |

## How-to

| 文档 | 说明 |
| --- | --- |
| [local-validation](zh/how-to/local-validation.md) | 完整的本地功能验证步骤、期望输出与排错 |
| [configure-channels](zh/how-to/configure-channels.md) | 配置飞书、钉钉、企业微信、Telegram、Discord、Slack 等 IM 渠道 |
| [run-multiple-instances](zh/how-to/run-multiple-instances.md) | 在同一台机器上隔离运行多个 Gateway + AgentServer 实例 |

## Reference

| 文档 | 说明 |
| --- | --- |
| [cli-and-environment](zh/reference/cli-and-environment.md) | 命令行参数、环境变量、配置文件、运行时目录与退出行为 |
| [e2a-protocol](zh/reference/e2a-protocol.md) | Gateway 与 AgentServer 之间的 E2A 请求/响应协议 |

## Explanation

| 文档 | 说明 |
| --- | --- |
| [architecture](zh/explanation/architecture.md) | Gateway 的定位、数据流、模块划分、启动顺序与关键设计决策 |

## 英文文档

- [English documentation](README_EN.md)
- [Quick Start (EN)](en/tutorial/01-quick-start.md)
- [Local validation (EN)](en/how-to/local-validation.md)
- [Configure channels (EN)](en/how-to/configure-channels.md)
- [Run multiple instances (EN)](en/how-to/run-multiple-instances.md)
- [CLI and environment (EN)](en/reference/cli-and-environment.md)
- [E2A protocol (EN)](en/reference/e2a-protocol.md)
- [Architecture (EN)](en/explanation/architecture.md)

## 其他资料

- 可运行示例：[examples/](../examples/)
- 开源软件声明：[OPEN_SOURCE_SOFTWARE_NOTICE.md](../OPEN_SOURCE_SOFTWARE_NOTICE.md)
- 变更记录：[GitCode Releases](https://gitcode.com/openJiuwen/agent-gateway/releases)

## 返回导航

- [项目首页](../README.zh.md)
