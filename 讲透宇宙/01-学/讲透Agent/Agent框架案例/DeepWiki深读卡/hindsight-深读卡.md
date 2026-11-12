# hindsight 深读卡 —— vectorize-io 仿生 Agent 记忆：世界事实/经历事实/模式观察三库 + TEMPR 多策略检索

> **定位**：Hindsight™（vectorize-io）的 Agent 记忆系统——让 Agent "随时间学习"的 biomimetic 长期记忆：超越平铺向量库的 naive RAG，把信息组织为**世界事实（客观知识）/经历事实（个人体验）/巩固观察（习得模式）**三类记忆单元，配实体消解（"CEO"="Satya Nadella"）、因果时间感知、自主反思进化。检索走 **TEMPR 多策略**：语义/BM25 关键词/图/时序四路并行。
> **本地**：`repos/hindsight`（vectorize-io/hindsight）｜**深读**：deepwiki 74 子页归档 `deepwiki/hindsight/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 记忆引擎 | 提取/组织/反思 | memory_engine.py（74-76 事实提取）、三库结构 |
| 实体层 | 跨会话身份 | Canonical entity tracking（http.py:61-63） |
| 检索层 | TEMPR 四路 | 语义+BM25+图+时序并行（memory_engine.py:4-10） |
| API | 服务化 | hindsight-api-slim（HTTP 接口） |
| 反思 | 自主进化 | autonomous reflection（模式合成） |

## 二、核心机制

1. **三库仿生组织**：world facts（客观）/experience facts（主观）/consolidated observations（学习所得）分离存储——明确指出 naive RAG 三缺失（无因果时间/无实体归一/无学习机制）并逐一对应解决。
2. **TEMPR 四路检索**：temporal+semantic+keyword+graph 并行召回再融合——时间与关系是记忆检索一维度，非仅相似度。
3. **实体消解**：同一实体跨会话/跨表述归一到 canonical id——"关于 Satya 的所有事"可完整召回。
4. **反思巩固**：从原始交互中自主合成新模式（观察库增长）——离线巩固（对照 mateclaw 的 Dreaming）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 三库仿生记忆 | 讲透Agent/04 §记忆（情景/语义/程序记忆映射） |
| TEMPR 时序检索 | 时间感知 RAG |
| 反思巩固 | 讲透学习型Agent §离线学习 |

## 四、关键入口

```
hindsight-api-slim/hindsight_api/engine/memory_engine.py  # 引擎核心
hindsight-api-slim/hindsight_api/api/http.py               # API+实体消解
```

## 五、深读子页地图（74 页精选 5）

Overview（三库+TEMPR）｜Biomimetic Memory Architecture｜Entity Resolution｜TEMPR 检索实现｜Reflection 巩固。

## 六、与"我们"的关系（一句话）

记忆系统"仿生分类派"的论文级实现——与 cortex-mem（分层）/ACE（技能化）三对照，讲透Agent 记忆章的 2026 前沿三样本。

---
生成：2026-08-21 · deepwiki 74 页全归档
