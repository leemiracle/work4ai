# gobii-platform 深读卡 —— Django 多 Agent 编排平台：持久 Agent × 浏览器自动化 × 积分计费多渠道

> **定位**：gobii-ai 的 Django 多 Agent 编排系统——用户创建**持久 AI Agent**（跨会话存在），具备浏览器自动化/工具集成（MCP）/多渠道通信；平台级配套**积分消费与计费系统**；支持个人与团队双模式。Python/Django 全栈路线的企业 Agent 平台。
> **本地**：`repos/gobii-platform`（gobii-ai/gobii-platform）｜**深读**：deepwiki 36 子页归档 `deepwiki/gobii-platform/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 管理 | 生命周期/配置 | Agent Management 子系统 |
| 计费 | 积分消费 | Credit & Billing System |
| 工具 | MCP 集成 | Tool Integration |
| 渠道 | 多渠道通信 | Communication Systems |
| 框架 | Web 全栈 | Django |

## 二、核心机制

1. **持久 Agent**：Agent 作为一等实体跨会话存活（记忆/配置/状态持续）——区别于会话即抛的多数框架。
2. **积分计费内建**：Credit 消耗模型平台级实现——商业化四件（计费/渠道/持久化/工具）齐于一旦。
3. **Django 全栈**：用成熟 Web 框架而非自研——企业 Django 团队做 Agent 平台的参考路径。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 持久 Agent | 讲透Agent/04 §跨会话状态 |
| 积分计费 | ai-deployment §商业化 |

## 四、关键入口

```
（Django apps：agents/billing/tools/channels）
```

## 五、深读子页地图（36 页精选 5）

Platform Overview｜Agent Management｜Credit & Billing｜Tool Integration (MCP)｜Communication Systems。

## 六、与"我们"的关系（一句话）

"Python 企业派" Agent 平台样本——与 dust（TS 企业派）/superagi（2023 化石）对照技术栈选择对平台架构的影响。

---
生成：2026-08-21 · deepwiki 36 页全归档
