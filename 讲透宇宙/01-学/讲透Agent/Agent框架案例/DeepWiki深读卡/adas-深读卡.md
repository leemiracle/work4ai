# ADAS 深读卡 —— 自动设计 Agent 系统（NeurIPS 2024，Meta Agent Search）

> **定位**：ShengranHu/ADAS，论文 "Automated Design of Agentic Systems"（NeurIPS 2024）官方实现——**用 LLM（Meta Agent）在代码空间里搜索/发明新 Agent 架构**，而不是人工设计。Agent 设计自动化（agent architecture search）方向的开山代码库之一。
> **本地**：`repos/adas`｜**深读**：deepwiki 14 子页归档 `deepwiki/adas/full.md`（2026-08-21，159KB）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Meta Agent | 设计新架构 | `LLMAgentBase` → Meta Agent 读历史档案+问题样本，**写出新 AgentSystem 类的代码** |
| 搜索循环 | 进化式搜索 | `search.py`（每域一个：`_arc/_drop/_gpqa/_mgsm/_mmlu`）迭代 archive |
| 被发现的 Agent | 动态执行 | `AgentSystem`（草稿→ critiques→答案等已涌现出的模式）+ `Info` 数据结构 |
| 评估 | 多基准 | ARC / DROP / GPQA / MGSM / MMLU 五套 solver+评测 |

## 二、核心机制

1. **代码即架构搜索空间**：候选 Agent 不是配置模板而是**可执行 Python 类**——Meta Agent 每轮以"档案（历史最优+代码）+任务描述"为上下文，生成新类定义，热加载进评估循环（Dynamic Code Evaluation 页：import 字符串→实例化→跑基准）。
2. **已涌现的典型发明**：Multi-Perspective Agent（多视角自辩论）、Draft-Critique 循环、leaf-wise 深化……论文核心发现：搜索发现的架构能击败手工 SOTA（如多视角讨论+逐步推理混合体）。
3. **工程细节**：OpenAI API 重试/限流封装、并行评估、置信度计算（answer extraction 跨 5 域复用）。

## 三、与讲透系列的对位

| ADAS 概念 | 讲透系列对应 |
|---|---|
| Meta Agent 搜索 Agent 空间 | 讲透学习型Agent/02 §自我改进形式化（此处=架构层自改进）|
| 代码空间 + 热执行 | 讲透Agent/01 §CodeAct（代码即动作的搜索版）|
| archive 进化 | 讲透学习型Agent/01 §进化四层（Layer 4 代表作）|

## 四、关键入口

```
_arc/search.py 等        # 每个基准的搜索主循环（11 个样板近乎同构）
agents/                   # LLMAgentBase / Meta Agent prompts
_methods/                 # 动态生成的 AgentSystem 代码落地处
```

## 五、深读子页地图（14 页精选 5）

2 Core Architecture（LLMAgentBase/Info/复用模式）｜3 Evolutionary Search（搜索算法主体）｜4 Dynamic Code Evaluation（热加载执行——安全上无沙盒，直接 exec）｜5 Problem Solvers（五域 solver 对照）｜9 Evaluation Systems。

## 六、与"我们"的关系（一句话）

讲透学习型Agent 的"Agent 发明 Agent"不是科幻——ADAS 就是可跑的起点实现，且 14 页 wiki 已归档；注意其**动态代码执行无沙盒**，复现时务必隔离环境（对照 cline 的 command-guard）。

---
生成：2026-08-21 · deepwiki 14 页全归档 · 论文：arXiv:2408.08435（NeurIPS 2024）
