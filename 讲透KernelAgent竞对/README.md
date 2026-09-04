# 讲透 KernelAgent 竞对四仓 · 深度知识库

> 基于 DeepWiki 关联快照 + understand-anything 中文知识图谱 + 新人指南 + 核心文件深解 + 数据集审计的四仓知识库。
> 生成于 2026-09-03，对应各仓 git 快照（见各 knowledge-graph/GRAPH-SUMMARY.md 的 commit 钉版）。

## 这是什么

hpc-agent 论文线（TRANSFER-LAWS）的四个竞对/关联项目的系统性知识库，同时服务两类场景：

| 场景 | 用哪部分 | 怎么用 |
|---|---|---|
| 快速看懂某竞对 | `<仓>/ONBOARDING.md` | 20 分钟全局观（架构分层/关键概念/学习路径） |
| 深挖某模块 | `<仓>/explain/`（共 22 篇） | 每篇一个核心文件的角色/结构/数据流/设计决策 |
| 交互探索代码 | `<仓>/knowledge-graph/`（共 532 节点/1067 边） | 先读 GRAPH-SUMMARY，再去本体仓跑 /understand-chat |
| 对照 KernelBench 生态 | `shared-deepwiki/kernelbench/`（36 页全量快照） | 四仓共同的上游评测基座，交叉引用表在各仓 DEEPWIKI-CROSSREF.md |
| 数据资产盘点 | `evokernel/DATASET-AUDIT.md` | 567 kernel 五集合统计/schema/复用建议 |

## 四仓定位对比

| | KernelBlaster (NVlabs) | KernelMem | EvoKernel | ReGraphT |
|---|---|---|---|---|
| **一句话** | MAIC-RL：NCU profiling+持久优化知识库+RL 探索 | 长短期记忆 kernel 自进化循环 | 值驱动记忆的数据资产（框架未开源） | 大模型推理轨迹→推理图→迁移小模型 |
| **arXiv** | 2602.14293 | — | 2603.10846 | ICLR2026 投稿 |
| **记忆形态** | optimization_database.json（出厂 3 策展状态组）+ replay buffer | memorybank yaml+gate 表（长期）×轮次回灌（短期） | 导出 kernel 集+value 标签（MHC） | reasoning graph（构图+检索） |
| **图谱规模** | 269n/589e/10 层/15 步 | 129n/258e/6 层/12 步 | 86n/136e/5 层/9 步（采样式） | 48n/84e/6 层/9 步 |
| **关键情报** | KB 无实测对、状态匹配待跨机检验 | gate 表=人工策展先验 | MHC 6/15 超 baseline=价值标注样本；正确率有存活者偏差 | reasoner 三空文件=早期占位，完成度低 |

## 目录结构

```
讲透KernelAgent竞对/
├── README.md                    # 本文件
├── FINAL-REPORT.md              # 生成过程报告（方法/统计/坑/覆盖检查）
├── shared-deepwiki/kernelbench/ # KernelBench DeepWiki 36 页全量快照（四仓共用，1MB）
├── kernelblaster/  {ONBOARDING.md, DEEPWIKI-CROSSREF.md, knowledge-graph/(摘要+图谱), explain/(8篇)}
├── kernelmem/      {同构, explain/(6篇)}
├── evokernel/      {同构 + DATASET-AUDIT.md, explain/(4篇)}
└── regrapht/       {同构, explain/(4篇)}
```

本体仓路径（图谱交互用）：`/data/usershare/ai/{KernelBlaster,KernelMem,EvoKernel,ReGraphT}`——各仓 `.understand-anything/knowledge-graph.json` 支持 understand 增量更新（fingerprints 基线已建）。

## 推荐阅读路径

```
竞对格局速览（本 README 对比表）
   ↓ 按需进仓
ONBOARDING.md（20min/仓）
   ↓ 想吃透某个模块
explain/ 对应篇（15-25min/篇）
   ↓ 需要 KernelBench 评测语境
shared-deepwiki/kernelbench/ 对应章（2.1/2.5/7.1 高频）
   ↓ 交互查依赖
本体仓 /understand-chat
```
