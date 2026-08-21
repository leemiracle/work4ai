# maestro-framework 深读卡 —— Doriandarko 轻量三层编排：orchestrator→subtask→execution 的多 provider 分解器

> **定位**：Doriandarko（claude-engineer/aeon 同作者生态）的 Maestro LLM 编排框架——把复杂任务分解为子任务交 LLM 执行：**三层编排模型**（orchestrator 规划→subtask 分解→execution 执行），多 provider（Claude/GPT/Gemini/Groq/Ollama/LM Studio 本地）。
> **本地**：`repos/maestro-framework`（Doriandarko/maestro）｜**深读**：deepwiki 18 子页归档 `deepwiki/maestro-framework/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 目标接收入口 | run_maestro() |
| 规划层 | orchestrator | opus_orchestrator()（或等价） |
| 分解层 | 子任务生成 | task decomposition |
| 执行层 | LLM 执行 | 多 provider（云+本地） |
| Web | 界面 | Web Interface |

## 二、核心机制

1. **三层编排极简**：orchestrator 只做分解，execution 只做执行——与 gpt-pilot 十角色对照的"最少角色数"设计（3 层 vs 10 agent）。
2. **本地模型一等公民**：Ollama/LM Studio 直连——离线编排全流程可跑。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 三层分解 | 讲透多Agent协作/01 §层级编排（极简端） |
| 本地 provider | 讲透LLM §本地推理 |

## 四、关键入口

```
run_maestro()        # 主入口（wiki Core Architecture 图）
```

## 五、深读子页地图（18 页精选 4）

Overview（三层架构 mermaid）｜Usage Guide｜Implementations｜Web Interface。

## 六、与"我们"的关系（一句话）

"分解-执行"范式的最小完整 Python 实现——教学时先跑它，再对比 gpt-pilot（重）/bernstein（分布式）看同一范式的三个量级。

---
生成：2026-08-21 · deepwiki 18 页全归档
