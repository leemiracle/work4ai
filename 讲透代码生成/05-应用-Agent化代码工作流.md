---
card_id: CG-05
title: "第 5 幕 · 应用：Agent 化代码工作流"
universe: 讲透代码生成
arc_position: 第 5 幕（应用/新平衡）
status: draft
next_card: null
---

# 🚀 第 5 幕 · 应用：Agent 化代码工作流

## 当前最可靠的用法：AI 写 + 人审

不要信「全自动工程师」营销。**2024-2026 的主流是「AI 写+人审」**：
- AI 生成草稿（70% 时间省下）
- 人审关键路径（30% 时间花在 review/test/debug）
- AI 在人反馈下迭代（Agentic 闭环）

## 工具链选型

| 工具 | 定位 | 适合 |
|---|---|---|
| **Cursor 1.x** | AI-native IDE | 日常 coding |
| **Claude Code / OpenCode** | CLI agent | 复杂任务/CI 集成 |
| **Aider** | 终端 pair programming | git 友好 |
| **GitHub Copilot Workspace** | 从 issue 到 PR | 团队协作 |
| **Devin / Factory** | 「全自动」(能力有限) | 受控 demo 场景 |

## 设计模式：让 Agentic 可靠

### 1. AGENTS.md / Cursor rules
把项目约定写成机器可读文件，让 agent 遵守。**这是「项目级 prompt」**。

### 2. Skills（本 work4ai 项目的实践）
把重复工作流封装成 skill，agent 按场景调用。**复用 = 熵减**。

### 3. MCP（Model Context Protocol）
标准化接工具/数据源。code agent 的「USB-C」。

### 4. 并行多 agent + file ownership
并行实现时，**每个 agent 负责互斥的文件集**，避免冲突。见 `讲透多Agent协作/`。

### 5. 人审断点（human-in-loop）
关键节点暂停等人审。LangGraph 的 interrupt、OpenCode 的确认机制。

### 6. Sandbox 执行
agent 跑代码在 sandbox 里，防 `rm -rf` 灾难。

## 生产化清单

- [ ] 有 AGENTS.md / rules 约束 agent
- [ ] 命令白名单（禁危险操作）
- [ ] 测试套件 agent 可跑（验证闭环）
- [ ] prompt caching 降本
- [ ] 预算上限（防成本爆炸）
- [ ] 全链路 trace（可调试）
- [ ] 人审断点（关键节点）

## 五条经验法则

1. **把 benchmark 分数打 5-7 折估真实能力**。
2. **测试通过 ≠ 正确**——加 code review。
3. **指令与数据分离**——防注入。
4. **小模型粗筛 + 大模型精修**——降本。
5. **「AI 写+人审」>「AI 独立交付」**——当前阶段。

## 与已有资产

- **`Karpathy经典代码精读/`**：理解别人代码（生成的逆问题）
- **`故事化学习法/`**：code agent 的 story = 故事卡

---

## 🎬 五幕收束

> 代码生成的可靠路径 = **Agentic 闭环（耗散结构）+ 工程约束（AGENTS.md/MCP/测试）+ 人审断点**。SWE-bench 70% 不是终点，是「半自动」的起点。**真正的全自动，需要先解决「测试通过≠正确」和「成本可控」两个根本难题**。

📌 **该宇宙五幕完成** → 回 `README.md`
