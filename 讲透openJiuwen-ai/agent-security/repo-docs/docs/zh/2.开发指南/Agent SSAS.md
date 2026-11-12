# Agent SSAS

Agent SSAS（包名 `agent-ssas`，导入名 `agent_ssas`）采集智能体运行时事件，做威胁检测，并把结果落成 OCSF 日志。它不绑定某一个智能体框架。当前通过安全 Rail 接入 JiuwenSwarm。

组件自己的文档中心在 [agent_ssas/docs/README.md](../../../agent_ssas/docs/README.md)，里面有教程、操作指南、配置参考和架构说明。本文只说明它在本仓库中的位置。

---

## 1. 两个子系统

| 子系统 | 包路径 | 职责 |
| --- | --- | --- |
| AgentSSASCore | `agent_ssas.core` | 检测引擎：预处理、分析流水线、检测模块、存储、OCSF 呈现 |
| AgentSSASClient | `agent_ssas.backend_client` | 采集事件并上报。openjiuwen 客户端的核心类是 `AgentSSASSecurityRail` |

检测引擎可以单独嵌进任意 Python 进程。只有接入 JiuwenSwarm 的那一层客户端依赖智能体运行时。

## 2. 运行方式

| 模式 | 行为 |
| --- | --- |
| `inprocess` | 默认。检测跑在同一进程里 |
| `http` | 独立的 FastAPI 服务，多个智能体共用一台分析引擎 |

决策策略有两种：`observe_only` 只记录，全部放行；`active_protection` 在 critical 时阻断，其余告警。检测引擎自身出错时不拦住调用方。

内置检测模块包括 `agent_moss` 和 `security_rail_detection`。`test_detection` 默认关闭。新模块用 `module.yaml` 声明，不改框架代码。

## 3. 从这里继续

| 想做的事 | 文档 |
| --- | --- |
| 认识概念 | `agent_ssas/docs/zh/tutorial/01-introduction.md` |
| 在本进程跑通 | `agent_ssas/docs/zh/tutorial/02-quickstart.md` |
| 接入 JiuwenSwarm | `agent_ssas/docs/zh/tutorial/03-integrate-jiuwenswarm.md` |
| 配置字段 | `agent_ssas/docs/zh/reference/configuration.md` |

示例在 `agent_ssas/examples/`。JiuwenSwarm 的接入补丁在 `agent_ssas/patches/`。
