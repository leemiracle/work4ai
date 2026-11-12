# Agent Gateway Documentation

This documentation covers installation, usage, reference, and design for Agent Gateway. Chinese is the authoritative source; the English structure mirrors it.

## Coverage

- **Tutorial**: step-by-step first run for new users.
- **How-to**: task-oriented guides such as local validation, channel configuration, and multiple instances.
- **Reference**: CLI options, environment variables, configuration keys, and protocol fields.
- **Explanation**: the gateway's role, data flow, modules, and design decisions.

## Tutorial

| Document | Description |
| --- | --- |
| [01-quick-start](en/tutorial/01-quick-start.md) | Run the gateway locally with a mock AgentServer and complete a `chat.send` round trip |

## How-to

| Document | Description |
| --- | --- |
| [local-validation](en/how-to/local-validation.md) | Full local validation steps, expected output, and troubleshooting |
| [configure-channels](en/how-to/configure-channels.md) | Configure Feishu, DingTalk, WeCom, Telegram, Discord, Slack, and other IM channels |
| [run-multiple-instances](en/how-to/run-multiple-instances.md) | Run multiple isolated Gateway + AgentServer instances on one host |

## Reference

| Document | Description |
| --- | --- |
| [cli-and-environment](en/reference/cli-and-environment.md) | CLI options, environment variables, config file, runtime directories, and exit behavior |
| [e2a-protocol](en/reference/e2a-protocol.md) | E2A request/response protocol between the gateway and AgentServer |

## Explanation

| Document | Description |
| --- | --- |
| [architecture](en/explanation/architecture.md) | Gateway role, data flow, modules, startup sequence, and key design decisions |

## Chinese documentation

- [中文文档](README.md)
- [快速开始](zh/tutorial/01-quick-start.md)
- [本地功能验证](zh/how-to/local-validation.md)
- [配置渠道](zh/how-to/configure-channels.md)
- [单机多实例](zh/how-to/run-multiple-instances.md)
- [命令行与环境变量](zh/reference/cli-and-environment.md)
- [E2A 协议](zh/reference/e2a-protocol.md)
- [架构说明](zh/explanation/architecture.md)

## Other resources

- Runnable examples: [examples/](../examples/)
- Open-source notice: [OPEN_SOURCE_SOFTWARE_NOTICE.md](../OPEN_SOURCE_SOFTWARE_NOTICE.md)
- Release notes: [GitCode Releases](https://gitcode.com/openJiuwen/agent-gateway/releases)

## Navigation

- [Project home](../README.md)
