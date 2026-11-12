# Agent Security

[English](./README.md) | 简体中文

## 简介

**Agent Security** 是 openJiuwen 面向 Agent 场景的安全能力合集仓库，聚焦 Agent 行为检测、隔离运行、安全审计等方向，为 Agent 提供全链路的纵深安全防护。

当前仓库包含以下组件，后续将持续扩展更多安全能力：

- **Agent SSAS**：Agent 安全态势感知系统（Security Situation Awareness System）。通过事件采集与可插拔检测模块框架，实时感知 Agent 行为并产出 OCSF 格式威胁报告，支持进程内与独立 HTTP 服务两种运行模式，可无缝接入 JiuwenSwarm 等智能体运行时。详见 [agent_ssas/README.zh.md](./agent_ssas/README.zh.md)。
- **JiuwenBox Sandbox**：轻量 Agent 安全沙箱服务，为 Agent 工具调用与代码执行提供分层隔离。
- **agent-shield**：进程内动作决策与内容检测。详见 [docs/zh/2.开发指南/Agent Shield.md](./docs/zh/2.开发指南/Agent%20Shield.md)。

## 文档

中英文文档统一放在 [docs/](./docs/)：

- [docs/zh/SUMMARY.md](./docs/zh/SUMMARY.md)
- [docs/en/SUMMARY.md](./docs/en/SUMMARY.md)

## 参与贡献

我们欢迎所有形式的贡献，包括但不限于：

- 提交问题和功能建议
- 改进文档
- 提交代码
- 分享使用经验

## 开源许可证

本项目依据 [Apache-2.0](./LICENSE) 许可证授权。

本产品仅作为流程编排工具，不包含 AI 模型能力；用户在连接 AI 模型用于特定业务场景时，需自行承担欧盟 AI 法案等相关合规义务。
