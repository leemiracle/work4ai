# open-multi-agent 深读卡 —— 生产级多 Agent 团队编排：目标→DAG 任务分解→按能力依赖执行（Node.js）

> **定位**：JackChen-me 的生产级编排框架——构建管理**协作 Agent 团队**：模型无关（Claude+GPT 等混编一个 Node.js 进程），自动化多 Agent 协作生命周期：**目标→规划分解→DAG 任务图→按依赖与 Agent 能力执行**。
> **本地**：`repos/open-multi-agent`（JackChen-me/open-multi-agent）｜**深读**：deepwiki 26 子页归档 `deepwiki/open-multi-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 目标→DAG | planning（goal 分解为 DAG of tasks） |
| 执行层 | 依赖调度 | 按 dependencies+agent capabilities 分派 |
| 模型层 | 混编 | 多 provider 单进程协作 |
| 工具层 | 能力 | tool execution |
| LLM 通信 | 统一 | provider 抽象 |

## 二、核心机制

1. **DAG 任务分解**：目标先分解成有向无环任务图，依赖关系显式——执行顺序由图拓扑+Agent 能力双约束（对照 xagent 的计划树：DAG 允许并行分支）。
2. **能力匹配调度**：任务分派看 Agent 能力声明——异构模型各司其职。
3. **单进程轻编排**：不引消息总线/分布式，单 Node 进程跑多 agent——"够用的编排"务实派。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 目标→DAG | 讲透多Agent协作/03 §图编排 |
| 能力匹配 | xagent abilities 对照 |

## 四、关键入口

```
（Node.js 包；package.json L36-49 依赖契约）
```

## 五、深读子页地图（26 页精选 4）

Overview（组件关系图）｜Planning/DAG 分解｜执行调度｜工具/LLM 层。

## 六、与"我们"的关系（一句话）

"DAG 分解"范式的 Node.js 教材版——代码量小，讲多 Agent 编排章可当"学生实现"对照 LangGraph/bernstein 工业版。

---
生成：2026-08-21 · deepwiki 26 页全归档
