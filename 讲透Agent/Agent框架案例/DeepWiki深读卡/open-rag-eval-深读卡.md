# open-rag-eval 深读卡 —— Vectara 开源 RAG 评测工具箱：TREC-RAG 基准指标的模块化评估框架

> **定位**：Vectara 开源的 RAG 管线评测工具箱——模块化可扩展的 Python 框架，测/析 RAG 系统质量：**TREC-RAG 基准的标准指标**、灵活架构（既评已有 RAG 输出也评在线系统）、报告与可视化。RAG 评测标准化方向的官方补位（与公司 RAG 产品形成"造+评"闭环）。
> **本地**：`repos/open-rag-eval`（vectara/open-rag-eval）｜**深读**：deepwiki 18 子页归档 `deepwiki/open-rag-eval/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 指标层 | 标准评测 | TREC-RAG 基准指标集 |
| 评估层 | 双模式 | 评已有输出 / 在线 RAG 系统 |
| 报告层 | 可视化分析 | reporting & visualization |
| 集成层 | 灵活接入 | 不同 RAG 实现适配 |

## 二、核心机制

1. **TREC-RAG 指标内建**：信息检索界权威基准（TREC）的 RAG 指标搬进工具箱——检索质量评测的学术标准工程化。
2. **双模评测**：离线（评已有输出文件）与在线（接活系统）——CI 回归与研发调试两用。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| RAG 评测标准化 | ml-experiment §评测（与 phoenix evals/voice-lab 组成评测三件套） |

## 四、关键入口

```
（Python 工具箱；metrics+eval+report 三模块）
```

## 五、深读子页地图（18 页精选 4）

Overview｜Getting Started｜Core Components（指标详解）｜集成模式。

## 六、与"我们"的关系（一句话）

RAG 生态"评测标准件"——与 vectara-agentic（造）配对即"造+评"完整闭环，讲 RAG 章收尾必备。

---
生成：2026-08-21 · deepwiki 18 页全归档
