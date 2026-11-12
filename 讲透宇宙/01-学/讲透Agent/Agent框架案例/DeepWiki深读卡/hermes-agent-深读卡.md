# hermes-agent 深读卡 —— Nous Research 自我改进 Agent 框架：技能创建/进化 + 多宿主部署 + ACP 编辑器集成

> **定位**：Nous Research 官方 self-improving AI agent 框架（Hermes 模型生态的参考 harness）——对话循环带工具调用/持久记忆管理/**技能创建与改进**（self-improving 的落点），部署覆盖 CLI/消息平台（Telegram/Discord/WhatsApp）/编辑器（**ACP Agent Client Protocol**）。任意 OpenAI 兼容 LLM provider；执行环境可选本地主机/容器/云端。核心 agent 管对话编排+工具执行+状态持久。
> **本地**：`repos/hermes-agent`（nousresearch/hermes-agent）｜**深读**：deepwiki 68 子页归档 `deepwiki/hermes-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心 agent | 对话编排+工具+状态 | run_agent.py 主循环 |
| CLI | 终端入口 | cli.py |
| 消息平台 | 多渠道 | Telegram/Discord/WhatsApp 等 |
| 编辑器 | ACP 集成 | Agent Client Protocol |
| 技能系统 | 自我改进 | skill creation & improvement |
| 记忆 | 持久化 | persistent memory management |
| 执行环境 | 三选一 | 本地/容器/云端 |
| 模型层 | 任意 provider | OpenAI 兼容统一 |

## 二、核心机制

1. **技能自我改进**：agent 运行中可创建新技能并改进既有技能——self-improving 是产品主张而非论文口号（与 agentk/ACE 同族，Nous 版本更重多宿主部署）。
2. **ACP 编辑器集成**：经 Agent Client Protocol 接入编辑器（Zed 等）——Agent 标准协议三件套（MCP 工具/A2A agent 间/ACP 客户端-编辑器）中 ACP 的代表实现之一。
3. **三档执行环境**：本地主机/容器/云——从开发到生产的沙盒梯度内建。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 技能创建+改进 | 讲透学习型Agent/05 §自改进 |
| ACP | 讲透Agent/02 §协议栈（MCP/A2A/ACP 三层） |
| 三档执行环境 | 沙盒梯度（本地→容器→云） |

## 四、关键入口

```
run_agent.py      # 主循环（L1-21）
cli.py            # CLI 入口
```

## 五、深读子页地图（68 页精选 5）

Overview｜Architecture Overview（三层设计）｜技能系统章节｜消息平台集成｜ACP。

## 六、与"我们"的关系（一句话）

开源模型厂商官方 agent harness 的标本（Nous 系）——与 Claude Code（Anthropic 闭源标杆）/openclaw（社区）对照"模型厂×agent 框架"的三种绑定方式。

---
生成：2026-08-21 · deepwiki 68 页全归档
