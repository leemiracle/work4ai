# maestro-orchestrate 深读卡 —— 39 个专业 Agent 的开发编排：src-first 一次编写→四运行时适配生成

> **定位**：josstei 的多 Agent 开发编排平台——"TechLead"人设协调 **39 个专业 AI Agent** 走结构化 SDLC：任务分类→方案设计→实现规划→委派执行。核心架构 **src-first, generated-runtime**：所有逻辑/方法论/协议在 canonical `src/` 写一次，生成器产出四个 LLM 运行时适配器——**Gemini CLI/Claude Code/Codex/Qwen Code**。
> **本地**：`repos/maestro-orchestrate`（josstei/maestro-orchestrate）｜**深读**：deepwiki 30 子页归档 `deepwiki/maestro-orchestrate/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 源核 | 一次编写 | canonical src/（逻辑+方法论+协议） |
| 生成层 | 四运行时适配 | adapters: Gemini CLI/Claude Code/Codex/Qwen Code |
| 编排层 | TechLead | 任务分类/方案设计/实现规划/委派执行 |
| Agent 池 | 39 专业角色 | specialized agents |
| 状态 | 持久会话 | persistent session state |

## 二、核心机制

1. **src-first 生成运行时**：编排逻辑与具体 CLI agent 解耦——写一次协议，生成四家适配器——多 coding agent 生态碎片化的"编译器式"应对（对照 bernstein 40+ adapter 手写：这里是生成路线）。
2. **39 角色全 SDLC**：分类→设计→规划→执行的角色矩阵——gpt-pilot 10 角色的四倍展开。
3. **TechLead 人设中枢**：以单一"技术负责人"视角统筹——编排人格化。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| src-first 适配生成 | 讲透代码生成 §多目标生成 |
| 39 角色 SDLC | 讲透多Agent协作/01 §角色分工（重型端） |

## 四、关键入口

```
src/                # canonical 源（逻辑/方法论/协议）
（生成器产出四 runtime adapter；docs/architecture.md）
```

## 五、深读子页地图（30 页精选 5）

Overview｜Architecture（src-first 模型）｜Agent 方法论｜编排协议｜四运行时适配。

## 六、与"我们"的关系（一句话）

"多 coding agent 适配"问题的生成器答案——与 bernstein（手写 adapter 群）/praisonai（框架适配注册表）三路线对照讲"异构 agent 编排的前置工程"。

---
生成：2026-08-21 · deepwiki 30 页全归档
