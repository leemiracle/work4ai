# llama-cpp-agent 深读卡 —— 本地 LLM Agent 全家桶：引导采样让非微调模型稳定 function calling/JSON

> **定位**：Maximilian-Winter 的 llama-cpp-python 之上 Agent 框架——为**本地 GGUF 模型**补齐 chat/function calling/结构化输出/RAG 全能力。核心差异化：**引导采样（guided sampling）**——用语法约束（GBNF）让未经 function-calling 微调的模型也能稳定产出合法 JSON/工具调用——"本地模型也能当 Agent 用"的基建。
> **本地**：`repos/llama-cpp-agent`（Maximilian-Winter/llama-cpp-agent）｜**深读**：deepwiki 25 子页归档 `deepwiki/llama-cpp-agent/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 核心框架 | 统一接口 | chat/function calling/结构化输出/RAG |
| Provider 系统 | 多后端 | provider 层（llama.cpp 本地+API） |
| 记忆系统 | 会话/长期 | memory 子系统 |
| 工具层 | 函数调用 | tools & function calling |
| 引导采样 | 语法约束 | GBNF grammar constrained decoding |

## 二、核心机制

1. **引导采样**：不是 prompt 求模型输出 JSON，而是**解码层强制语法**（GBNF 文法约束 token 采样）——输出必然合法（对照 XAgentGen 的 regex→logits 约束解码：同族技术，XAgent 面向训练、llama-cpp-agent 面向推理）。
2. **本地优先全能力**：结构化输出/工具调用/RAG 全在 GGUF 模型上闭环——零 API 依赖的完整 Agent。
3. **多 provider 抽象**：本地 llama.cpp 与远程 API 统一接口——混合部署可迁移。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| GBNF 约束解码 | 讲透LLM §结构化输出（解码层约束 vs prompt 层约束） |
| 本地 Agent 全家桶 | llocalsearch 对照（它做检索、这个做通用） |

## 四、关键入口

```
llama_cpp_agent/    # 核心包（provider/memory/tools）
```

## 五、深读子页地图（25 页精选 5）

Overview｜Core Framework｜Provider System｜Memory System｜Tools and Function Calling（引导采样详解）。

## 六、与"我们"的关系（一句话）

"本地模型 Agent 化"技术核心标本——结构化输出教学从此有了"prompt 约束 vs 解码约束"的最佳对比组（与 deepanalyze 的训练层约束三分天下：prompt/解码/权重）。

---
生成：2026-08-21 · deepwiki 25 页全归档
