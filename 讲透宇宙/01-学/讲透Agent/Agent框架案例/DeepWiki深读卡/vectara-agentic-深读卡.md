# vectara-agentic 深读卡 —— Vectara 平台之上的 Agentic RAG 框架：LLM 当"经理"调度检索工具

> **定位**：Vectara 官方 Python 库——基于 Vectara RAG 平台构建 Agentic RAG 应用：LLM 作为 "manager" 推理复杂查询、调工具（Vectara 检索为核心） gathering 信息、生成有据回答。针对传统 RAG "单轮检索" 局限引入 agent 循环——多步检索/推理/组合的检索 Agent 化路线。
> **本地**：`repos/vectara-agentic`（vectara/py-vectara-agentic）｜**深读**：deepwiki 26 子页归档 `deepwiki/vectara-agentic/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 层 | 推理调度 | LLM manager + 工具循环 |
| 工具层 | 检索能力 | Vectara 检索工具（query/excerpt 等） |
| 数据层 | 语料库 | Vectara corpora |
| 接口 | 简化 API | Python 库 |

## 二、核心机制

1. **RAG 的 Agent 化**：单轮 retrieve→generate 升级为 agent 决定"查什么→查几次→怎么组合"——Agentic RAG 命名的代表实现之一（对照 gpt-researcher 的全栈自研：vectara-agentic 是平台绑定轻封装）。
2. **grounded 回答**：回答强制挂Vectara 引用——企业 RAG 的可溯源底线。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| Agentic RAG | 讲透NLP §RAG 进化（单轮→多轮 agent） |
| 引用接地 | data-to-paper grounded 对照 |

## 四、关键入口

```
vectara_agentic/     # 核心包
```

## 五、深读子页地图（26 页精选 4）

Overview｜Architecture｜Installation｜工具/检索章节。

## 六、与"我们"的关系（一句话）

"Agentic RAG"术语级样本——讲 RAG 演进史时：localgpt（静态 RAG）→vectara-agentic（检索 Agent 化）→gpt-researcher（全栈研究 Agent）三级跳的中间站。

---
生成：2026-08-21 · deepwiki 26 页全归档
