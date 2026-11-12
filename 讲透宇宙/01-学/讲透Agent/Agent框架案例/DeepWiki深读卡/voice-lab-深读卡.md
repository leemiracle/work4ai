# voice-lab 深读卡 —— 语音 Agent 评测迭代框架：LLM 对话/网页聊天/语音分析/实时语音四模态测试

> **定位**：saharmor 的 Voice Lab——**评测与迭代 LLM 语音 Agent** 的 Python 测试框架：四模态（LLM 对话测试/Web chatbot 评估/语音分析/实时语音交互），自动化测试+性能指标+成本优化，数据驱动选型（不同 LM/配置对比）。虽为语音优化，任何 LLM Agent 评测皆可用。
> **本地**：`repos/voice-lab`（saharmor/voice-lab）｜**深读**：deepwiki 18 子页归档 `deepwiki/voice-lab/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 测试系统 | 四模态 | LLM conversation/Web chatbot/Speech analysis/Real-time voice |
| 配置 | 测试管理 | Test Configuration |
| 指标 | 性能/成本 | 自动化 metrics |

## 二、核心机制

1. **四模态评测矩阵**：文本对话→网页聊天→语音分析→实时语音全链覆盖——语音 Agent 各研发阶段各有对应测试面。
2. **成本优化对比**：跨模型/配置的成本-质量权衡数据化——评测驱动选型（对照 phoenix 的 evals：voice-lab 专注语音时延/质量维度）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 多模态评测 | ml-experiment §评测（语音维度） |
| 数据驱动迭代 | 与 pipecat（框架）配对的评测件 |

## 四、关键入口

```
（Python 框架：testing systems+config；详见 wiki Testing Systems）
```

## 五、深读子页地图（18 页精选 4）

Voice Lab Overview｜Testing Systems｜Test Configuration｜指标/成本页。

## 六、与"我们"的关系（一句话）

语音 Agent 生态的"评测补位"——与 pipecat（框架）/joinly（会议）拼图时，评测环节就靠它，讲透语音 Agent 专题三件套之一。

---
生成：2026-08-21 · deepwiki 18 页全归档
