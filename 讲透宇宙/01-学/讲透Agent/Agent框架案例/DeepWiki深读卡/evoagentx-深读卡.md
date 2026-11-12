# evoagentx 深读卡 —— 工作流全生命周期进化引擎：自动构建→评估→演化优化的多 Agent 框架

> **定位**：EvoAgentX——构建/评估/**演化** LLM 多 Agent 工作流的开源生态（EvoAgent 论文系列工程化）：自然语言目标 → `WorkFlowGenerator` 单提示自动构建多 Agent 工作流 → 内置评估器打分 → **进化引擎**（textual gradients 文本梯度/变异/引导搜索三类优化策略）迭代优化——像持续测试改进软件一样持续进化 agentic workflow。
> **本地**：`repos/evoagentx`（EvoAgentX/EvoAgentX）｜**深读**：deepwiki 76 子页归档 `deepwiki/evoagentx/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 工作流构建 | 目标→结构化多 Agent 工作流 | `WorkFlowGenerator`（workflow_generator.py:7） |
| 评估 | agent 行为自动打分 | 内置 evaluators（任务特定准则） |
| 进化引擎 | 优化工作流 | textual gradients / mutation / guided search |
| HITL | 人类审阅纠偏 | `HITLManager` |
| 运行时 | 执行工作流 | 多 agent 执行层 |

## 二、核心机制

1. **Workflow Autoconstruction**：一句 prompt 经 `WorkFlowGenerator` 生成结构化多 Agent 工作流（角色/工具/拓扑）——"从模糊想法到可用系统"的工程自动化（对照 ADAS：那里搜索单 Agent 架构，这里构建多 Agent 工作流）。
2. **Textual Gradients 进化**：借鉴 DSPy 的文本梯度思想但作用在**整个工作流**（提示词+结构+工具配置一起变异）——优化对象从 prompt 升维到 workflow。
3. **评估在环**：进化不盲变——每代工作流先过内置评估器，分数驱动搜索方向（进化算法+评估函数的标准组合，罕见地用在 agent 工作流上）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| workflow 自动构建 | 讲透学习型Agent/05 §结构自进化 |
| textual gradients | dspy 同思想对照（prompt→workflow 升维） |
| 评估驱动进化 | ml-experiment §评估在环 |

## 四、关键入口

```
evoagentx/workflow/workflow_generator.py   # 工作流自动生成
evoagentx/hitl/                            # 人在环管理
evoagentx/（进化引擎模块）                   # 三类优化策略
```

## 五、深读子页地图（76 页精选 5）

Overview｜Key Concepts｜WorkflowGenerator｜Evolution Engine（文本梯度/变异）｜HITLManager。

## 六、与"我们"的关系（一句话）

"workflow 也进化"思潮的代表实现——与 dspy（prompt 进化）/ACE（技能进化）/aden-hive（改图）合成"进化对象四层"完整教具：prompt→skill→workflow→architecture。

---
生成：2026-08-21 · deepwiki 76 页全归档
